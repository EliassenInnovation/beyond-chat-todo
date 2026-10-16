"""Regression evidence for the reference-app review. No keys, network or model calls."""
import json
from types import SimpleNamespace as NS

import pytest

import todo.agent as agent_module
import evaluations.evals as evals
import evaluations.evals_page as evals_page
import todo.todo_view as todo_view
from todo.capabilities import REGISTRY, Action, ActionError, Registry, execute
from todo.todos import TodoList
from todo.view import View


def context(tmp_path):
    return NS(todos=TodoList(tmp_path / 'todos.json'), view=View())


@pytest.mark.parametrize('actor', ['person', 'agent'])
def test_failed_batch_save_restores_memory_and_file(tmp_path, monkeypatch, actor):
    ctx = context(tmp_path)
    ctx.todos.add('Existing task')
    before = ctx.todos.path.read_bytes()
    def fail(*args):
        raise OSError('disk unavailable')
    monkeypatch.setattr('todo.todos.os.replace', fail)
    with pytest.raises(OSError, match='disk unavailable'):
        execute(REGISTRY, 'todos.add', {'todos': [{'title': 'One', 'due': None},
                                                {'title': 'Two', 'due': None}]}, actor=actor, ctx=ctx)
    assert ctx.todos.path.read_bytes() == before
    assert [t.title for t in ctx.todos.todos] == ['Existing task']
    assert ctx.todos.next_ids['todo'] == 2
    assert list(tmp_path.iterdir()) == [ctx.todos.path]


def test_batch_commits_once_and_click_includes_undo(tmp_path, monkeypatch):
    ctx = context(tmp_path)
    import todo.todos as todos
    original, writes = todos.os.replace, []
    def write(src, dst):
        writes.append(json.loads(open(src).read()))
        original(src, dst)
    monkeypatch.setattr(todos.os, 'replace', write)
    todo_view.apply(ctx.todos, ctx.view, {'op': 'add', 'title': 'Read the guide'})
    assert len(writes) == 1 and len(writes[0]['undo']) == 1
    execute(REGISTRY, 'todos.add', {'todos': [{'title': 'One', 'due': None},
                                            {'title': 'Two', 'due': None}]}, actor='agent', ctx=ctx)
    assert len(writes) == 2 and len(writes[-1]['todos']) == 3


def test_tool_evidence_does_not_change_after_later_writes(tmp_path):
    ctx = context(tmp_path)
    ctx.todos.add('Original')
    earlier = execute(REGISTRY, 'todos.list', {}, actor='agent', ctx=ctx)
    execute(REGISTRY, 'todos.rename', {'todos': [{'id': 1, 'title': 'Changed'}]}, actor='person', ctx=ctx)
    assert earlier['todos'][0]['title'] == 'Original'


@pytest.mark.parametrize('change', ['rename', 'complete', 'set_due'])
def test_approval_is_bound_to_requested_details_after_reload(tmp_path, change):
    ctx = context(tmp_path)
    ctx.todos.add('Original')
    request = ctx.todos.request_delete(1)
    if change == 'rename':
        ctx.todos.rename(1, 'Changed')
    elif change == 'complete':
        ctx.todos.complete(1)
    else:
        ctx.todos.set_due(1, '2026-11-01')
    ctx.todos = TodoList(ctx.todos.path)
    with pytest.raises(ActionError, match='changed since'):
        execute(REGISTRY, 'todos.approve', {'id': request.id}, actor='person', ctx=ctx)
    assert len(ctx.todos.todos) == 1
    ctx.todos.deny(request.id)
    new = ctx.todos.request_delete(1)
    assert new.id != request.id
    ctx.todos.approve(new.id)
    assert not ctx.todos.todos


def test_legacy_approval_without_snapshot_requires_new_request(tmp_path):
    ctx = context(tmp_path)
    ctx.todos.add('Original')
    pending = ctx.todos.request_delete(1)
    ctx.todos.approval_targets = {}
    with pytest.raises(ActionError, match='no saved approval details'):
        ctx.todos.approve(pending.id)


def test_provider_failure_preserves_saved_work_undo_and_history(tmp_path, monkeypatch):
    ctx = context(tmp_path)
    calls = 0
    class Call:
        id = 'call-1'
        function = NS(name='add_todo', arguments='{"todos": [{"title": "Read the guide", "due": null}]}')
        def model_dump(self):
            return {'id': self.id, 'type': 'function', 'function': vars(self.function)}
    def create(**kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise agent_module.openai.OpenAIError('provider unavailable')
        return NS(model='test-model', choices=[NS(message=NS(tool_calls=[Call()], content=None))])
    monkeypatch.setattr(agent_module, 'OpenAI', lambda: NS(chat=NS(completions=NS(create=create))))
    agent = agent_module.Agent(ctx.todos)
    reply = agent.ask('Please add a task')
    assert 'could not finish' in reply and 'Read the guide' in reply
    assert agent.messages[-1] == {'role': 'assistant', 'content': reply}
    assert len(TodoList(ctx.todos.path).undo_stack) == 1
    todo_view.apply(ctx.todos, ctx.view, {'op': 'undo'})
    assert not ctx.todos.todos


def test_no_provider_key_needed_until_chat(tmp_path, monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    ctx = context(tmp_path)
    agent = agent_module.Agent(ctx.todos)
    assert agent.client is None
    assert 'could not finish' in agent.ask('Hello')
    assert not ctx.todos.todos


@pytest.mark.parametrize('missing', evals.TRUTH_CHECKS)
def test_each_required_judge_is_needed_for_a_pass(missing):
    names = [n for n in (*evals.TRUTH_CHECKS, 'passed', 'answers_every_part') if n != missing]
    item = NS(item={'input': {'case': 'add', 'attempt': 1}}, output={}, trace_id=None,
              evaluations=[NS(name=n, value=1.0, comment=None) for n in names])
    record = evals.run_record(NS(item_results=[item], name='test', run_name='test - 2026-10-15'), ['add'], 1)
    attempt = record['attempts'][0]
    assert attempt['truthful'] is None and missing in attempt['ungraded']
    assert not evals_page.good(attempt)
    assert 'inconclusive' in ' '.join(evals_page.reasons(attempt, 'add a task'))


def test_default_suite_excludes_held_out_cases():
    assert evals.default_cases()
    assert all(evals.CASES[n]['origin'] != 'held out' for n in evals.default_cases())


@pytest.mark.parametrize('policy', ['alow', 'approved', ''])
def test_unknown_policy_is_rejected_at_registration(policy):
    with pytest.raises(ValueError, match='unknown policy'):
        Registry('example').register(Action('a', 'a', 'test', {}, ('read',), lambda ctx: {},
                                            policy={'agent': policy}))


@pytest.mark.parametrize('state, expected', [
    ({'passed': True, 'truthful': True, 'answered': True}, 'passed'),
    ({'passed': True, 'truthful': None, 'answered': True}, 'inconclusive'),
    ({'passed': False, 'truthful': None, 'answered': True}, 'failed'),
    ({'passed': True, 'truthful': True}, 'inconclusive'),
])
def test_report_distinguishes_failed_and_ungraded(state, expected):
    assert evals_page.outcome({'error': None, **state}) == expected


def test_page_shows_expectation_and_incomplete_evidence_separately():
    attempt = dict(case='example', attempt=1, passed=True, truthful=None, answered=True,
                   error=None, judge_quote=None, trace_url=None, conversation=[],
                   before={'todos': []}, after={'todos': []}, checks={'passed': {'passed': True, 'reason': None}},
                   ungraded=['claims_real_abilities'])
    record = dict(run='layout fixture', started='2026-10-15', model='test model', repeat=2,
                  commit='test-revision', cases=[dict(name='example', asks='Does it leave the list alone?',
                                                   expects='No tasks change.')], attempts=[attempt])
    page = evals_page.render(record)
    assert 'Expected outcome:</strong> No tasks change.' in page
    assert 'Inconclusive &middot; 1' in page
    assert '1 planned attempts have no result' in page
    assert 'claims_real_abilities: unavailable' in page
    assert 'test-revision' in page


def test_unexpected_failure_keeps_undo_for_saved_work(tmp_path, monkeypatch):
    ctx = context(tmp_path)
    agent = agent_module.Agent(ctx.todos)
    def interrupted(text):
        agent.turn_before = ctx.todos.state()
        execute(REGISTRY, 'todos.add', {'todos': [{'title': 'Saved before interruption', 'due': None}]},
                actor='agent', ctx=agent)
        raise RuntimeError('interrupted')
    monkeypatch.setattr(agent, '_ask', interrupted)
    with pytest.raises(RuntimeError, match='interrupted'):
        agent.ask('Add a task')
    assert len(TodoList(ctx.todos.path).undo_stack) == 1
    todo_view.apply(ctx.todos, ctx.view, {'op': 'undo'})
    assert not ctx.todos.todos


def test_confirmed_failures_sort_before_inconclusive_cases():
    def attempt(case, passed):
        return dict(case=case, attempt=1, passed=passed, truthful=None, answered=None,
                    error=None, judge_quote=None, trace_url=None, conversation=[], after={'todos': []})
    record = dict(run='layout fixture', started='2026-10-15', model='test model', repeat=1,
                  cases=[dict(name=n, asks=n, expects='No change') for n in ('incomplete-case', 'failed-case')],
                  attempts=[attempt('incomplete-case', True), attempt('failed-case', False)])
    page = evals_page.render(record)
    assert page.index('failed-case') < page.index('incomplete-case')


@pytest.mark.parametrize('showing, ids, expected', [
    ('all', None, [1, 2, 3]),
    ('active', None, [1, 3]),
    ('completed', None, [2]),
    ('only', [3, 1], [1, 3]),
])
def test_current_read_reports_visible_task_ids_in_screen_order(tmp_path, showing, ids, expected):
    ctx = context(tmp_path)
    for title in ['Same title', 'Finished', 'Same title']:
        ctx.todos.add(title)
    ctx.todos.complete(2)
    execute(REGISTRY, 'view.show', {'showing': showing, 'ids': ids}, actor='agent', ctx=ctx)
    saved = ctx.todos.path.read_bytes()
    read = execute(REGISTRY, 'todos.list', {}, actor='agent', ctx=ctx)
    assert read['visible_todo_ids'] == expected
    assert [t['id'] for t in read['todos']] == [1, 2, 3]  # hidden tasks remain readable
    assert ctx.todos.path.read_bytes() == saved
    todo_view.apply(ctx.todos, ctx.view, {'op': 'filter', 'filter': 'all'})
    assert read['visible_todo_ids'] == expected  # earlier evidence remains detached


def test_each_agent_turn_observes_the_current_ui_filter(tmp_path):
    from copy import deepcopy
    ctx = context(tmp_path)
    ctx.todos.add('One')
    ctx.todos.add('Two')
    ctx.todos.complete(2)
    agent = agent_module.Agent(ctx.todos, view=ctx.view)
    requests = []
    def reply(**kwargs):
        requests.append(deepcopy(kwargs['messages']))
        return NS(model='test-model', choices=[NS(message=NS(content='Ready.', tool_calls=None))])
    agent.client = NS(chat=NS(completions=NS(create=reply)))
    agent.run_tool('show_todos', '{"showing":"only","ids":[1]}')
    agent.ask('What is visible?')
    assert agent.tool_log[0]['result']['visible_todo_ids'] == [1]
    todo_view.apply(ctx.todos, ctx.view, {'op':'filter', 'filter':'completed'})
    agent.ask('And now?')
    assert agent.tool_log[0]['result']['visible_todo_ids'] == [2]
    latest = [m['content'] for m in requests[-1] if m['role']=='system' and 'visible_todo_ids' in m['content']]
    assert len(latest) == 1 and '"visible_todo_ids": [2]' in latest[0]


def test_current_read_distinguishes_an_empty_view_from_an_empty_list(tmp_path):
    ctx = context(tmp_path)
    ctx.todos.add('Finished')
    ctx.todos.complete(1)
    todo_view.apply(ctx.todos, ctx.view, {'op': 'filter', 'filter': 'active'})
    read = execute(REGISTRY, 'todos.list', {}, actor='agent', ctx=ctx)
    assert read['visible_todo_ids'] == []
    assert [t['title'] for t in read['todos']] == ['Finished']


@pytest.mark.parametrize('probability', [float('nan'), float('inf'), -0.1, 1.1])
def test_restored_guard_rejects_invalid_probabilities(probability):
    from types import SimpleNamespace
    import todo.agent as agent
    from todo.todos import MERGE_UNNAMED
    client = SimpleNamespace(decisions=SimpleNamespace(create=lambda **kwargs:
        SimpleNamespace(answers=[SimpleNamespace(type='predicate', probability=probability)])))
    with pytest.raises(ActionError, match='invalid probability'):
        agent.ask_guard(client, MERGE_UNNAMED, [{'role': 'user', 'content': 'Merge them'}])


def test_restored_guard_refusal_changes_catalog_revision():
    from dataclasses import replace
    from todo.capabilities import Registry
    from todo.todos import MERGE_UNNAMED
    first, second = Registry('test'), Registry('test')
    first.guard(MERGE_UNNAMED)
    second.guard(replace(MERGE_UNNAMED, refusal='Ask which tasks.'))
    assert first.catalog()['catalog_revision'] != second.catalog()['catalog_revision']


def test_decisions_cost_is_input_only_and_does_not_use_chat_rates():
    from evaluations.eval_costs import estimate
    result = estimate([{'purpose': 'guard', 'served_model': 'gpt-6-luna',
                        'usage': {'input_tokens': 1000, 'output_tokens': 20,
                                  'input_tokens_details': {'cached_tokens': 500}}}])
    assert result['complete'] and result['usd'] == 0.0001
    assert result['input_tokens'] == 1000 and result['output_tokens'] == 20
    assert not estimate([{'purpose': 'guard', 'served_model': 'unknown',
                         'usage': {'input_tokens': 1000}}])['complete']
