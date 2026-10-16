"""Guard evidence boundaries, concurrency, caching, and refusal before mutation."""
import json
from datetime import date
from threading import Barrier
from types import SimpleNamespace

import pytest

import todo.agent as agent_module
import todo.guard_check as guard_check
from todo.capabilities import ActionError, Guard
from todo.model_usage import capture
from todo.todos import TARGET_GUARDS, TodoList


def agent(tmp_path):
    todos = TodoList(tmp_path / 'todos.json')
    todos.add('Call Morgan')
    todos.add('Call Priya')
    a = agent_module.Agent(todos, today=date(2026, 11, 2))
    a.guards = set(TARGET_GUARDS)
    a.seen = todos.snapshot()
    a.messages.append({'role': 'user', 'content': 'Move the call to Friday.'})
    return a


def answer(guards, evidence):
    return {g.name: g.require_yes for g in guards}


def test_separate_evidence_concurrent_groups_and_argument_cache(tmp_path, monkeypatch):
    a = agent(tmp_path)
    calls = []
    barrier = Barrier(2)
    def ask(gs, evidence):
        calls.append(evidence)
        if len(calls) <= 2:
            barrier.wait(timeout=3)  # sequential execution would fail
        return {g.name: False for g in gs}
    monkeypatch.setattr(guard_check, 'ask_chat', ask)
    args = json.dumps({'todos': [{'id': 1, 'due': '2026-11-06'}]})
    before = a.todos.path.read_bytes()
    assert 'ask which' in a.run_tool('set_due_date', args)['error']
    assert a.todos.path.read_bytes() == before
    assert len(a.tool_log[-1]['guard_checks']) == 5
    assert a.tool_log[-1]['guard_checks'][0]['refused']
    input_evidence = next(e for e in calls if 'action' not in e)
    assert set(input_evidence) == {'conversation', 'state', 'current_date'}
    output = next(e for e in calls if 'action' in e)
    assert output['calendar']['2026-11-06'].startswith('Friday')
    assert 'not marking them completed' in output['tool_meanings']['request_delete']
    a.run_tool('set_due_date', args)
    assert len(calls) == 2
    a.run_tool('set_due_date', json.dumps({'todos': [{'id': 2, 'due': '2026-11-06'}]}))
    assert len(calls) == 3  # same input evidence reused, changed action rechecked


def test_new_state_rechecks_and_late_person_edit_refuses(tmp_path, monkeypatch):
    a = agent(tmp_path)
    def ask(gs, evidence):
        if gs[0].require_yes:
            a.todos.rename(1, 'Changed by person')
        return answer(gs, evidence)
    monkeypatch.setattr(guard_check, 'ask_chat', ask)
    result = a.run_tool('complete_todo', '{"ids":[1]}')
    assert 'list changed' in result['error'].lower()
    assert not a.todos.get(1).done


def test_unavailable_and_invalid_guard_never_changes_tasks(tmp_path, monkeypatch):
    a = agent(tmp_path)
    def unavailable(*args):
        raise ActionError('Nothing changed: guard unavailable.')
    monkeypatch.setattr(guard_check, 'ask_chat', unavailable)
    assert 'unavailable' in a.run_tool('complete_todo', '{"ids":[1]}')['error']
    assert not a.todos.get(1).done
    # A refusal or absent answer cannot become an allow.
    monkeypatch.setattr(guard_check, 'ask_chat', lambda gs,e: {g.name: float('nan') for g in gs})
    assert 'invalid answer' in a.run_tool('complete_todo', '{"ids":[1]}')['error']
    assert not a.todos.get(1).done


def test_valid_action_and_approval_path_unchanged(tmp_path, monkeypatch):
    a = agent(tmp_path)
    monkeypatch.setattr(guard_check, 'ask_chat', answer)
    assert 'error' not in a.run_tool('complete_todo', '{"ids":[1]}')
    assert a.todos.get(1).done
    assert 'error' not in a.run_tool('request_delete', '{"ids":[2]}')
    assert a.todos.get(2).title == 'Call Priya'
    assert a.todos.pending[0].todo_id == 2


def test_malformed_arguments_do_not_call_guard(tmp_path, monkeypatch):
    a = agent(tmp_path)
    monkeypatch.setattr(guard_check, 'ask_chat', lambda *args: pytest.fail('Unexpected paid call'))
    assert 'error' in a.run_tool('complete_todo', '{"ids":"one"}')


def response(answers):
    return SimpleNamespace(model=guard_check.MODEL,
                           choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(answers)))],
                           usage=SimpleNamespace(model_dump=lambda: {'prompt_tokens':10,'completion_tokens':4,'total_tokens':14}))


def mock_client(monkeypatch, complete):
    monkeypatch.setattr(guard_check, 'OpenAI', lambda **kwargs: SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=complete))))


@pytest.mark.parametrize('answers', [{}, {'g': True, 'extra': False}, {'g': 1}, {'g': None}, {'g': 'yes'}])
def test_provider_answer_validation(monkeypatch, answers):
    mock_client(monkeypatch, lambda **kwargs: response(answers))
    with pytest.raises(ActionError):
        guard_check.ask_chat([Guard('g', 'Question?', 'Refused', provider='chat')], {'words': 'Hello'})


def test_guard_usage_follows_concurrent_context(monkeypatch):
    def request(**kwargs):
        questions=json.loads(kwargs['messages'][-1]['content'])['questions']
        return response({name:False for name in questions})
    mock_client(monkeypatch, request)
    gs = [Guard('a', 'A?', 'No', provider='chat'),
          Guard('b', 'B?', 'No', inputs=('words', 'state'), reason='Needs state', provider='chat')]
    with capture() as usage:
        guard_check.check_guards(gs, {'words':'Hello','state':{}}, {}, lambda *args: None)
    assert len(usage.calls) == 2 and usage.total == 28
    from evaluations.eval_costs import estimate
    assert estimate(usage.calls)['complete']


def test_no_action_reuse_after_state_changes(tmp_path, monkeypatch):
    a=agent(tmp_path);calls=[]
    def ask(gs,e):
        calls.append(e)
        return answer(gs,e)
    monkeypatch.setattr(guard_check,'ask_chat',ask)
    a.run_tool('complete_todo','{"ids":[1]}')
    a.run_tool('complete_todo','{"ids":[2]}')
    assert len(calls)==4


def test_missing_key_blocks_without_network(monkeypatch):
    def missing(**kwargs):
        raise guard_check.openai.OpenAIError('Key missing')
    monkeypatch.setattr(guard_check, 'OpenAI', missing)
    with pytest.raises(ActionError, match='could not answer'):
        guard_check.ask_chat([Guard('g','Question?','No',provider='chat')], {'words':'Hello'})


def test_guard_declarations_require_reasons_and_check_both_polarities():
    from todo.capabilities import Registry
    r=Registry('test')
    with pytest.raises(ValueError, match='reason'):
        r.guard(Guard('g','Question?','Refuse',inputs=('words','state')))
    assert Guard('g','Question?','Refuse').refuses(.5)
    assert Guard('g','Question?','Refuse',require_yes=True).refuses(.5)
    assert not Guard('g','Question?','Refuse',require_yes=True).refuses(.8)


def test_guard_tools_and_calendar_use_declared_semantics(tmp_path):
    from todo.capabilities import REGISTRY
    a=agent(tmp_path)
    evidence=a.guard_evidence('set_due_date',{'todos':[{'id':1,'due':None}]})
    assert set(evidence['calendar'])=={'2026-11-02'}
    assert 'null' in evidence['tool_meanings']['set_due_date']
    guarded={x.tool for x in REGISTRY.actions if 'todos.target_identified' in x.guards}
    assert guarded=={'complete_todo','set_due_date','request_delete'}


def test_guard_model_is_part_of_eval_configuration(monkeypatch):
    from pathlib import Path
    from evaluations.run_evidence import configuration
    args=dict(cases=['example'],repeat=1,model='agent',judge_model='judge',
              guards=['todos.target_identified'],inject=0,shuffled=False)
    before=configuration(Path(__file__).resolve().parents[1],**args)
    monkeypatch.setattr(guard_check,'MODEL','another-model')
    after=configuration(Path(__file__).resolve().parents[1],**args)
    assert before['fingerprint'] != after['fingerprint']
    assert after['settings']['action_guard_model']=='another-model'


def test_pending_model_narration_is_not_user_intent_evidence(tmp_path):
    a=agent(tmp_path)
    a.messages.append({'role':'assistant','content':'I will delete both calls now.', 'tool_calls':[]})
    evidence=a.guard_evidence('request_delete', {'ids':[1,2]})
    assert 'delete both' not in evidence['conversation']
    assert 'Move the call to Friday' in evidence['conversation']
    from todo.capabilities import REGISTRY
    for name in TARGET_GUARDS:
        assert 'conversation' in REGISTRY.guard_named(name).inputs
        assert 'words' not in REGISTRY.guard_named(name).inputs
    assert REGISTRY.guard_named('todos.merge_unnamed').inputs==('words',)


@pytest.mark.parametrize('configured, expected', [
    (None, {'todos.merge_unnamed', *TARGET_GUARDS}),
    ('', set()),
    ('todos.target_identified', {'todos.target_identified'}),
])
def test_default_guard_selection_and_explicit_overrides(configured, expected):
    # Isolate module initialization from this machine's .env and imported test modules.
    import subprocess
    import sys
    script = """
import json
import todo.langfuse_setup as langfuse_setup
original = langfuse_setup.setting
configured = json.loads(__import__('sys').argv[1])
langfuse_setup.setting = lambda name, default: (
    default if configured is None else configured
) if name == 'EVALBASICS_GUARDS' else original(name, default)
import todo.agent as agent
print(json.dumps(sorted(agent.GUARDS)))
"""
    result = subprocess.run([sys.executable, '-c', script, json.dumps(configured)],
                            check=True, capture_output=True, text=True)
    assert set(json.loads(result.stdout)) == expected
