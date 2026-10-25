"""The persona explorer, with no model calls: a scripted persona, a fake agent, a fake judge."""

import json
from types import SimpleNamespace

import evaluations.personas as personas
from todo.view import View


def persona_model(*turns):
    """A stand-in for the persona's model: replies with each turn in order."""
    replies = iter(turns)

    def create(**kwargs):
        turn = next(replies)
        if turn is None:  # the model's empty reply: a refusal
            return SimpleNamespace(choices=[SimpleNamespace(
                finish_reason='stop', message=SimpleNamespace(content=None, refusal="I can't help with that."))])
        turn = dict(click='none', message='', done=False, satisfied=False, frustrated=False, why='') | turn
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(turn)))])
    return lambda: SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))


class FakeAgent:
    """Adds whatever it is told to add; a message starting 'crash' raises; 'refuse' logs a refused call."""

    def __init__(self, todos, view=None, today=None):
        self.todos, self.tool_log, self.last_trace_id = todos, [], None

    def ask(self, text):
        self.tool_log = [{'tool': 'list_todos', 'args': '', 'given': True}]
        if text.startswith('crash'):
            raise RuntimeError('provider timed out')
        if text.startswith('refuse'):
            self.tool_log.append({'tool': 'complete_todo', 'args': '{"id": 99}', 'error': 'No todo 99.'})
            return 'Done!'
        self.todos.add(text.removeprefix('add '))
        return f'Added {text}.'


def play(monkeypatch, *turns, truthful=True):
    monkeypatch.setattr(personas, 'OpenAI', persona_model(*turns))
    monkeypatch.setattr(personas, 'Agent', FakeAgent)
    monkeypatch.setattr(personas, 'claims_match_outcome', lambda *a: (truthful, '' if truthful else 'Done!'))
    return personas.run('grace', max_turns=3)


def test_every_persona_starts_from_its_own_situation():
    for name, persona in personas.PERSONAS.items():
        assert persona['who'] and persona['wants'] and persona['start'], name
    sam = personas.start_list(personas.PERSONAS['sam'])
    assert [t.title for t in sam.todos if t.done] == ['Pay the electric bill', 'Buy sunscreen']
    assert next(t.due for t in sam.todos if t.title == 'Renew passport') == '2026-09-10'


def test_the_persona_sees_the_screen_not_the_data():
    todos = personas.start_list(personas.PERSONAS['sam'])
    shown = personas.screen(todos, View('active'))
    assert '[ ] Renew passport (due 2026-09-10)' in shown
    assert 'sunscreen' not in shown and shown.endswith('(2 hidden by the current view)')


def test_a_satisfied_conversation_has_no_findings(monkeypatch):
    run = play(monkeypatch, {'message': 'add Pack the suit'}, {'message': 'thanks!', 'done': True, 'satisfied': True})
    assert [t['user'] for t in run['turns']] == ['add Pack the suit', 'thanks!']
    assert run['turns'][0]['after']['visible'] == ['Water the plants', 'Pack the suit']
    assert run['findings'] == [] and run['session'].startswith('persona-grace-')


def test_trouble_is_reported_with_the_words_that_caused_it(monkeypatch):
    run = play(monkeypatch, {'message': 'refuse this'},
               {'message': 'forget it', 'done': True, 'frustrated': True, 'why': 'it never ticked it'}, truthful=False)
    kinds = [(f['turn'], f['kind']) for f in run['findings']]
    assert kinds == [(1, 'claimed a change that did not happen'), (1, 'note: a tool call was refused'),
                     (1, 'the persona was frustrated'), (2, 'gave up')]
    assert run['findings'][1]['detail'] == 'complete_todo: No todo 99.'
    # frustration belongs to the reply it reacts to, with the reaction beside it
    assert run['findings'][2].items() >= {'assistant': 'Done!', 'reaction': 'forget it', 'user': 'refuse this'}.items()


def test_the_persona_sees_waiting_deletes_and_can_click_approve(tmp_path):
    from todo.todos import TodoList
    todos = TodoList(tmp_path / 'todos.json')
    for title in ('Cake', 'Balloons', 'Hats'):
        todos.add(title)
    todos.request_delete(1), todos.request_delete(2)
    assert 'Waiting for your approval: delete "Cake" (a delete cannot be undone)  [Approve] [Deny]' in personas.screen(todos, View())
    personas.click(todos, 'none')
    assert len(todos.pending) == 2
    personas.click(todos, 'approve')
    assert [t.title for t in todos.todos] == ['Hats'] and todos.pending == []


def test_a_crash_keeps_its_turn_and_ends_the_conversation(monkeypatch):
    run = play(monkeypatch, {'message': 'crash now'}, {'message': 'hello?'})
    assert len(run['turns']) == 1 and run['turns'][0]['error'] == 'RuntimeError: provider timed out'
    assert [f['kind'] for f in run['findings']] == ['the agent crashed']


def test_a_persona_that_never_finishes_runs_out_of_turns(monkeypatch):
    run = play(monkeypatch, *({'message': f'add item {n}'} for n in range(3)))
    assert [f['kind'] for f in run['findings']] == ['ran out of turns']


def test_done_on_the_first_turn_still_asks_the_agent(monkeypatch):
    run = play(monkeypatch, {'message': 'add Pack the suit', 'done': True, 'satisfied': True},
               {'message': 'great', 'done': True, 'satisfied': True})
    assert run['turns'][0]['assistant'] == 'Added add Pack the suit.' and run['turns'][1].get('end')


def test_an_empty_persona_reply_is_retried_once(monkeypatch):
    run = play(monkeypatch, None, {'message': 'add Pack the suit'}, {'message': 'thanks', 'done': True, 'satisfied': True})
    assert run['turns'][0]['user'] == 'add Pack the suit' and run['findings'] == []


def test_a_persona_that_stays_silent_ends_the_conversation_as_a_harness_note(monkeypatch):
    run = play(monkeypatch, {'message': 'add Pack the suit'}, None, None)
    assert run['turns'][-1] == {'n': 2, 'user': None, 'persona_stopped': "I can't help with that."}
    assert [f['kind'] for f in run['findings']] == ['note: the persona stopped (the harness, not the agent)']


def test_current_openai_persona_uses_supported_parameters_and_preserves_user_role(monkeypatch):
    """A reasoning model must not receive the legacy persona temperature setting."""
    monkeypatch.setattr(personas, 'MODEL', 'gpt-6-luna')
    monkeypatch.setattr(personas, 'provider_for', lambda *args: 'openai')
    result = dict(click='none', message='Can you show just my chores?', done=False,
                  satisfied=False, frustrated=False, why='')
    requests = []

    def create(**kwargs):
        requests.append(kwargs)
        assert kwargs['model'] == 'gpt-6-luna'
        assert kwargs['reasoning_effort'] == 'none'
        assert 'temperature' not in kwargs
        assert kwargs['response_format']['json_schema']['strict'] is True
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(result)))])

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    history = []
    actual = personas.persona_says(client, 'priya', personas.PERSONAS['priya'], history,
                                  '[ ] Take out the recycling (Priya)', None)
    assert actual == result
    assert 'You are playing a person' in requests[0]['messages'][0]['content']
    assert history[-1] == {'role': 'assistant', 'content': result['message']}
