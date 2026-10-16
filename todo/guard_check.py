"""Evidence-scoped semantic checks. The app supplies facts; models supply judgments."""
from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context
import json
import math

import openai
from langfuse import get_client, observe
from langfuse.openai import OpenAI

from todo.capabilities import ActionError
from todo.langfuse_setup import setting
from todo.model_usage import call_model

MODEL = setting('EVALBASICS_ACTION_GUARD_MODEL', 'gpt-6-luna')
SETTINGS = {'reasoning_effort': 'low'} if MODEL.startswith(('gpt-5', 'gpt-6')) else {}


@observe(as_type='guardrail', capture_input=False, capture_output=False)
def ask_chat(guards, evidence):
    """One batch of binary judgments; these are answers, not calibrated probabilities."""
    questions = {g.name: g.question for g in guards}
    shape = {'type': 'object', 'properties': {name: {'type': 'boolean'} for name in questions},
             'required': list(questions), 'additionalProperties': False}
    get_client().update_current_span(name='semantic-guards', input={'evidence': evidence, 'questions': questions})
    try:
        reply = call_model(OpenAI(max_retries=0, timeout=45).chat.completions.create,
                           purpose='guard-chat', model=MODEL, **SETTINGS, max_completion_tokens=1500,
                           response_format={'type': 'json_schema', 'json_schema': {
                               'name': 'decisions', 'strict': True, 'schema': shape}},
                           messages=[{'role': 'system', 'content': 'Answer each yes/no question using the supplied evidence.'},
                                     {'role': 'user', 'content': json.dumps({'questions': questions, 'evidence': evidence}, sort_keys=True)}])
        answers = json.loads(reply.choices[0].message.content)
    except (openai.OpenAIError, ValueError, TypeError, IndexError, AttributeError) as exc:
        raise ActionError('This action was not applied: a guard could not answer. Try again later.') from exc
    if not isinstance(answers, dict) or set(answers) != set(questions) or any(type(v) is not bool for v in answers.values()):
        raise ActionError('This action was not applied: a guard returned an invalid answer.')
    get_client().update_current_span(output=answers)
    return answers


def check_guards(guards, available, cache, ask_decisions, report=None):
    """Batch matching evidence, run independent groups concurrently, enforce declared order.

    Changed arguments or task state require fresh checks. Only valid answers are cached.
    """
    groups, keys = {}, {}
    by_name = {g.name: g for g in guards}
    for guard in guards:
        evidence = {name: available[name] for name in guard.inputs}
        encoded = json.dumps(evidence, sort_keys=True)
        key = (guard.name, encoded)
        keys[guard.name] = key
        if key not in cache:
            groups.setdefault((guard.provider, encoded), []).append(guard)

    def ask(group, members):
        provider, encoded = group
        if provider == 'chat':
            return ask_chat(members, json.loads(encoded))
        return {g.name: ask_decisions(g, json.loads(encoded)) for g in members}

    if groups:
        with ThreadPoolExecutor(max_workers=min(4, len(groups))) as pool:
            jobs = [pool.submit(copy_context().run, ask, group, members) for group, members in groups.items()]
            for future in jobs:
                for name, answer in future.result().items():
                    valid = (type(answer) is bool if by_name[name].provider == 'chat' else
                             type(answer) in (float, int) and math.isfinite(answer) and 0 <= answer <= 1)
                    if not valid:
                        raise ActionError('This action was not applied: a guard returned an invalid answer.')
                    cache[keys[name]] = answer
    if report is not None:
        report([{'guard': g.name, 'refused': g.refuses(cache[keys[g.name]]),
                 **({'answer': cache[keys[g.name]]} if g.provider == 'chat' else
                    {'probability': cache[keys[g.name]]})} for g in guards])
    for guard in guards:
        if guard.refuses(cache[keys[guard.name]]):
            raise ActionError(guard.refusal)
