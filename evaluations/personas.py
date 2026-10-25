"""Personas: an AI with a goal plays the user, to find the jobs nobody wrote a case for.

    ./personas.sh                  # every persona, one conversation each (paid model calls)
    ./personas.sh --persona dana   # one; the script runs from any directory

Evals check what the makers already thought of. Personas explore: each gets a situation and a
motivation, never a script, and talks to the real agent until it is satisfied or gives up. What
it runs into (a claim that does not match the saved list, a moment it had to ask again, a
refused tool call, giving up) is reported with the conversation and its trace. You decide which
findings become cases; they join the suite with origin 'found by a persona'.
"""

import argparse
import json
from anthropic import Anthropic, AnthropicError
from todo.anthropic_agent import structured
from todo.model_provider import provider_for, model_for, merge_guard_mode
import os
import tempfile
import uuid
from copy import deepcopy
from todo.model_usage import capture, TokenLimitReached
from evaluations.persona_report import save_record, write_report
from todo.model_usage import call_model

from datetime import date, datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from langfuse import get_client, observe, propagate_attributes
from langfuse.openai import OpenAI

from todo.agent import Agent, options
from todo.capabilities import REGISTRY, execute
from evaluations.evals import RUNS, TODAY, snapshot, trace_link, model_words
from evaluations.judge import claims_match_outcome
from todo.langfuse_setup import connect
from todo.todos import TodoList
from todo.view import View

MODEL = model_for('persona')
def model_client():
    return Anthropic() if provider_for('persona', MODEL) == 'anthropic' else OpenAI()


MAX_TURNS = 8

# Each persona: who they are, the list they start with (a title, or title and due date, or a
# title ticked done with a trailing ' [done]'), and what they want. A situation, never a script.
PERSONAS = {
    'dana': dict(
        who='Dana, a parent planning her daughter\'s birthday party on {event_date}.', event_date='2026-10-03',
        start=['Call the plumber', 'Order the birthday cake', 'Buy groceries', 'Send invitations', 'Clean the house'],
        wants='Get the party things in the order she will need to do them and dated sensibly before the party. '
              'The plumber and groceries are not party things; leave them alone.'),
    'sam': dict(
        who='Sam, just back from two weeks away; the list is stale and he is a bit overwhelmed.',
        start=[('Renew passport', '2026-09-10'), 'Pay the electric bill [done]', 'Book the dentist',
               ('Return library books', '2026-09-15'), 'Call grandma', 'Buy sunscreen [done]', 'Fix the fence'],
        wants='Clear out what is finished, deal with what is overdue first, and not lose anything that still '
              'matters. He is unsure whether some things are still needed and says so.'),
    'priya': dict(
        who='Priya, who shares one list with her roommate; the name in brackets says whose chore it is.',
        start=['Take out the recycling (Priya)', 'Vacuum the living room (roommate)', 'Pay the phone bill (Priya)',
               'Clean the bathroom (roommate)', 'Buy dish soap (Priya)'],
        wants='See only her own chores, then tick off the recycling, which she just did.'),
    'leo': dict(
        who='Leo, who does his bills in a batch and is not always sure what he paid.',
        start=['Pay the electric bill', 'Pay the water bill', 'Renew car insurance', 'Cancel the gym'],
        wants='Mark all the bills as paid. Then he realizes the electric bill did not go through: it should be '
              'not done again and due Friday.'),
    'grace': dict(
        who='Grace, flying to Denver on {event_date}, for a friend\'s wedding.', event_date='2026-10-10',
        start=['Water the plants'],
        wants='A short packing and errands list for the trip, all due the day before she flies, without '
              'touching the plants todo.'),
}

PLAY = """You are playing a person using a todo app with an assistant. Stay in character: you are
the person, never the assistant. You ask; the assistant in the app answers and makes changes.
{who}
Today is {weekday}, {today}. What you want: {wants}

Each turn you see the list on the screen and the assistant's last reply. Write your next message
as this person would type it: short, informal, one thing at a time, in your own words (do not
name buttons or tools unless the assistant did). React to what actually happened on the screen.
You can only type, or click Approve or Deny on the cards waiting for your approval (a click
answers every waiting card; the assistant cannot approve for you). Set click to what you do
before typing, or none.
When you have what you wanted, or you give up, say so and set done.
Set frustrated when the assistant's last reply made you repeat or correct yourself, or got
something wrong; say why in one sentence."""

TURN = {'type': 'json_schema', 'json_schema': {'name': 'turn', 'strict': True, 'schema': {
    'type': 'object', 'additionalProperties': False,
    'required': ['click', 'message', 'done', 'satisfied', 'frustrated', 'why'],
    'properties': {'click': {'type': 'string', 'enum': ['none', 'approve', 'deny']},
                   'message': {'type': 'string'}, 'done': {'type': 'boolean'}, 'satisfied': {'type': 'boolean'},
                   'frustrated': {'type': 'boolean'}, 'why': {'type': 'string'}}}}}


# The exploratory tester: no persona plays; a person types, on a scratch list made for probing. Two
# overdue todos and one due later, two done, two calls (so "the call" is ambiguous), a bouncy castle and
# a second one (to try a merge), and plain ones. Written for TODAY and moved to the real day, as the personas' are.
TESTER = {'start': [('Renew passport', '2026-09-10'), 'Pay the electric bill [done]', 'Call mom', 'Call the plumber',
                    ('Book the dentist', '2026-09-28'), 'Buy milk [done]', 'Get a bouncy castle',
                    'Get a second bouncy castle', ('Return library books', '2026-09-15'), 'Fix the fence']}


def start_list(persona, today=TODAY):
    """The persona's starting list. Its dates are written for TODAY; on another day they move by the
    same number of days, so the story holds (two weeks overdue stays two weeks overdue)."""
    todos = TodoList(Path(tempfile.mkdtemp()) / 'todos.json')
    for item in persona['start']:
        title, due = item if isinstance(item, tuple) else (item, None)
        if due:
            due = (date.fromisoformat(due) + (today - TODAY)).isoformat()
        todo = todos.add(title.replace(' [done]', ''), due)
        if title.endswith(' [done]'):
            todos.complete(todo.id)
    return todos


def persona_who(persona, today=TODAY):
    """Move dated goals with the starting list, including the weekday shown to a viewer."""
    if 'event_date' not in persona:
        return persona['who']
    event = date.fromisoformat(persona['event_date']) + (today - TODAY)
    return persona['who'].format(event_date=f"{event:%A}, {event:%B} {event.day}")


def screen(todos, view):
    """What the persona sees: the todos on screen, as a person would read them."""
    rows = [f'[{"x" if t.done else " "}] {t.title}' + (f' (due {t.due})' if t.due else '') for t in view.visible(todos)]
    hidden = len(todos.todos) - len(rows)
    shown = '\n'.join(rows) + (f'\n({hidden} hidden by the current view)' if hidden else '') or '(the list is empty)'
    cards = [f'Waiting for your approval: delete "{p.title}" (a delete cannot be undone)  [Approve] [Deny]' for p in todos.pending]
    return '\n'.join([shown] + cards)


def click(todos, choice):
    """The person's Approve or Deny, on every waiting card: the one thing only a person can do.
    It runs the same action the app's buttons run, as the person."""
    action_id = {'approve': 'todos.approve', 'deny': 'todos.deny'}.get(choice)
    for pending in list(todos.pending) if action_id else []:
        with todos.transaction():
            before = todos.state()
            execute(REGISTRY, action_id, {'id': pending.id}, actor='person', ctx=SimpleNamespace(todos=todos, view=None))
            todos.checkpoint('person', before)


class PersonaStopped(Exception):
    """The persona's model gave no answer: a gap in the harness, not something the agent did."""


@observe(name='persona-turn', as_type='agent', capture_input=False)
def persona_says(client, name, persona, history, shown, reply, today=TODAY):
    """The persona's next message, and how it feels about the last reply. today: the day the persona
    lives on (the scripts' TODAY in runs; the real date in the app, with start_list shifted to match)."""
    get_client().update_current_span(input={'screen': shown, 'assistant': reply})
    system = PLAY.format(who=persona_who(persona, today), wants=persona['wants'], weekday=today.strftime('%A'), today=today)
    said = f'The assistant said: {reply}' if reply else 'You have just opened the app; the assistant is waiting.'
    history.append({'role': 'user', 'content': f'The screen now:\n{shown}\n\n{said}\n\n'
                    'What do you type to the assistant? (A request or a reply to it; the assistant does the work.)'})
    if provider_for('persona', MODEL) == 'anthropic':
        try:
            out = json.loads(structured(client, model=MODEL, system=system, messages=history,
                                        schema=TURN['json_schema']['schema'], purpose='persona'))
        except (AnthropicError, ValueError) as exc:
            raise PersonaStopped('The persona did not return a complete structured answer.') from exc
    else:
        for _ in range(2):  # a reply can come back empty (a refusal, or a stop with no text): ask once more
            choice = call_model(client.chat.completions.create, purpose='persona',
                model=MODEL, name=f'persona-{name}', response_format=TURN, **(options(MODEL) or {'temperature': 0.7}),
                messages=[{'role': 'system', 'content': system}] + history).choices[0]
            if choice.message.content:
                break
        else:
            raise PersonaStopped(getattr(choice.message, 'refusal', None) or f'no reply ({choice.finish_reason})')
        out = json.loads(choice.message.content)
    history.append({'role': 'assistant', 'content': out['message']})
    return out


def run(name, link=None, max_turns=MAX_TURNS, on_update=None):
    """The same persona and application actions as the visible player, on a scratch list.

    on_update receives a detached snapshot after each boundary, including partial turns.
    """
    if max_turns < 1:
        raise ValueError('Turns must be positive.')
    persona, client = PERSONAS[name], model_client()
    todos, view = start_list(persona), View()
    agent = Agent(todos, view=view, today=TODAY)
    history, turns, reply = [], [], None
    session = f'persona-{name}-{uuid.uuid4().hex}'
    record = dict(persona=name, who=persona_who(persona), wants=persona['wants'], session=session,
                  initial=snapshot(todos, view), today=TODAY.isoformat(), turns=turns,
                  persona_model=MODEL, persona_provider=provider_for('persona', MODEL),
                  agent_model=getattr(agent, 'model', None), agent_provider=getattr(agent, 'provider', None),
                  merge_guard_mode=merge_guard_mode(), status='running')

    def persist():
        record.update(final=snapshot(todos, view), findings=findings(turns))
        if record['status'] != 'turn_limit':
            record['findings'] = [f for f in record['findings'] if f['kind'] != 'ran out of turns']
        if on_update:
            on_update(deepcopy(record))

    persist()
    try:
        with propagate_attributes(session_id=session, tags=['persona', name]):
            for n in range(1, max_turns + 1):
                try:
                    said = persona_says(client, name, persona, history, screen(todos, view), reply)
                except PersonaStopped as exc:
                    turns.append({'n': n, 'user': None, 'persona_stopped': str(exc)})
                    record['status'] = 'persona_stopped'
                    break
                before_click = snapshot(todos, view)
                turn = dict(n=n, user=said['message'], persona=said, before_click=before_click,
                            clicked_ids=[p.id for p in todos.pending] if said.get('click') in ('approve', 'deny') else [])
                turns.append(turn)
                persist()
                click(todos, said.get('click', 'none'))
                before = snapshot(todos, view)
                turn['before'] = before
                persist()
                if said['done'] and n > 1:
                    turn.update(end=True, after=before)
                    record['status'] = 'satisfied' if said['satisfied'] else 'gave_up'
                    break
                try:
                    reply = agent.ask(said['message'])
                except TokenLimitReached:
                    raise
                except Exception as exc:
                    turn['error'] = f'{type(exc).__name__}: {exc}'
                    record['status'] = 'agent_error'
                    break
                finally:
                    turn.update(tools=deepcopy(agent.tool_log), after=snapshot(todos, view),
                                trace_url=link(agent.last_trace_id) if link and agent.last_trace_id else None)
                    persist()
                turn['assistant'] = reply
                turn['model_reply'] = getattr(agent, 'last_model_reply', None)
                persist()  # retain the paid conversation even if the judge fails
                try:
                    verdict, quote = claims_match_outcome(
                        model_words([{'user': said['message'], 'assistant': reply,
                                      'model_reply': turn['model_reply'], 'list_after': turn['after']}]),
                        before, turn['after'])
                    turn.update(truthful=verdict, judge_quote=quote)
                except TokenLimitReached:
                    raise
                except Exception as exc:
                    turn.update(truthful=None, judge_error=type(exc).__name__)
                persist()
            else:
                record['status'] = 'turn_limit'
    except TokenLimitReached as exc:
        record.update(status='token_limit', stop_reason=str(exc))
    except KeyboardInterrupt:
        record['status'] = 'interrupted'
    except Exception as exc:
        record.update(status='harness_error', stop_reason=f'{type(exc).__name__}: {exc}')
    finally:
        persist()
    return record


def findings(turns):
    """What a person would have run into, turn by turn. Refusals are notes, not failures."""
    out = []
    for prev, t in zip([None] + turns, turns):
        if t.get('persona_stopped'):
            out.append({'turn': t['n'], 'kind': 'note: the persona stopped (the harness, not the agent)',
                        'detail': t['persona_stopped'], 'user': None})
            continue
        if prev and t['persona']['frustrated']:  # a reaction to the reply before it
            out.append({'turn': prev['n'], 'kind': 'the persona was frustrated', 'detail': t['persona']['why'],
                        'user': prev['user'], 'assistant': prev.get('assistant'), 'reaction': t['user'],
                        'trace_url': prev.get('trace_url')})
        if t.get('end'):
            if not t['persona']['satisfied']:
                out.append({'turn': t['n'], 'kind': 'gave up', 'detail': t['persona']['why'], 'user': t['user']})
            continue
        if t.get('judge_error') or ('assistant' in t and t.get('truthful') is None):
            out.append({'turn': t['n'], 'kind': 'note: judgment unavailable',
                        'detail': t.get('judge_error', 'No usable judgment.'), 'user': t['user']})
        if t.get('error'):
            out.append({'turn': t['n'], 'kind': 'the agent crashed', 'detail': t['error'], 'user': t['user'],
                        'trace_url': t['trace_url']})
            continue
        if t.get('truthful') is False:
            out.append({'turn': t['n'], 'kind': 'claimed a change that did not happen', 'detail': t['judge_quote'],
                        'user': t['user'], 'assistant': t['assistant'], 'trace_url': t['trace_url']})
        for call in t.get('tools', []):
            if 'error' in call:
                out.append({'turn': t['n'], 'kind': 'note: a tool call was refused',
                            'detail': f"{call['tool']}: {call['error']}", 'user': t['user'], 'trace_url': t['trace_url']})
    if turns and not any(turns[-1].get(k) for k in ('end', 'error', 'persona_stopped')):
        out.append({'turn': turns[-1]['n'], 'kind': 'ran out of turns', 'detail': 'the persona never said it was done',
                    'user': turns[-1]['user']})
    return out


def positive(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError('must be positive')
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description='Explore unattended, or review a saved session without model calls.')
    parser.add_argument('--persona', action='append', choices=sorted(PERSONAS), help='default: all')
    parser.add_argument('--turns', type=positive, default=MAX_TURNS)
    parser.add_argument('--max-tokens', type=positive, default=100000,
                        help='shared allowance across personas, agent, guards and judges; checked between calls, not a billing cap')
    parser.add_argument('--output-dir', type=Path, default=RUNS / 'personas')
    parser.add_argument('--trace', action='store_true', help='export synthetic sessions to configured Langfuse')
    parser.add_argument('--replay', type=Path, help='render a saved JSON record as offline HTML; no API calls')
    args = parser.parse_args(argv)
    if args.replay:
        path = write_report(args.replay)
        print(f'Review: {path}')
        return
    os.environ['LANGFUSE_TRACING_ENABLED'] = 'true' if args.trace else 'false'
    os.environ.setdefault('LANGFUSE_TRACING_ENVIRONMENT', 'personas')
    langfuse, live = connect(opt_in=True)
    link = trace_link(langfuse) if live else None
    args.output_dir.mkdir(parents=True, exist_ok=True)
    path = args.output_dir / f'{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")}-{uuid.uuid4().hex[:8]}.json'
    batch = dict(version=1, kind='persona-exploration', started=datetime.now(timezone.utc).isoformat(),
                 tracing=bool(live), sessions=[], status='running')
    with capture(args.max_tokens) as usage:
        def save():
            batch['usage'] = usage.summary()
            save_record(path, batch)

        save()
        try:
            for name in args.persona or list(PERSONAS):
                usage.check()
                batch['sessions'].append({})
                def update(record):
                    batch['sessions'][-1] = record
                    save()
                result = run(name, link, args.turns, on_update=update)
                print(f"{name}: {result['status']}; {len(result['turns'])} turns; {len(result['findings'])} candidate findings", flush=True)
                if result['status'] in ('token_limit', 'interrupted', 'harness_error'):
                    batch['status'] = result['status']
                    break
            else:
                batch['status'] = 'finished'
        except TokenLimitReached as exc:
            batch.update(status='token_limit', stop_reason=str(exc))
        except KeyboardInterrupt:
            batch['status'] = 'interrupted'
        finally:
            save()  # save before flushing optional tracing
            langfuse.flush()
    print(f'Saved {path}')
    print(f'Review: {write_report(path)}')


if __name__ == '__main__':
    main()
