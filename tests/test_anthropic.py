"""Provider isolation and tool-protocol/recovery tests; no network or credentials."""
import json
from types import SimpleNamespace as NS

import pytest
from anthropic import AnthropicError
from anthropic.types import Message

from todo import agent as agents, anthropic_agent as adapter, guard_check
from todo.capabilities import ActionError
from todo.model_usage import capture
from todo.todos import TodoList, MERGE_UNNAMED
from evaluations import judge, personas


def response(content, stop='end_turn'):
    return Message.model_validate(dict(id='msg-test', type='message', role='assistant',
        model='claude-haiku-5-5', stop_reason=stop, content=content,
        usage=dict(input_tokens=100, output_tokens=20, cache_read_input_tokens=10,
                   cache_creation_input_tokens=5)))


def text(value):
    return {'type': 'text', 'text': value}


def tool(name, args, id='tool-1'):
    return dict(type='tool_use', id=id, name=name, input=args)


def client(*responses):
    replies = iter(responses)
    calls = []
    def create(**kwargs):
        calls.append(kwargs)
        reply = next(replies)
        if isinstance(reply, Exception):
            raise reply
        return reply
    return NS(messages=NS(create=create)), calls


@pytest.fixture
def only_anthropic(monkeypatch):
    for role in ('AGENT', 'JUDGE', 'PERSONA', 'ACTION_GUARD'):
        monkeypatch.setenv(f'EVALBASICS_{role}_PROVIDER', 'anthropic')
    monkeypatch.setenv('EVALBASICS_MERGE_GUARD_MODE', 'boolean')
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    def forbidden(*args, **kwargs):
        pytest.fail('Anthropic-only configuration attempted an OpenAI call')
    for module in (agents, judge, personas, guard_check):
        monkeypatch.setattr(module, 'OpenAI', forbidden)
    monkeypatch.setattr(agents.openai, 'OpenAI', forbidden)


def test_multiple_tools_native_history_context_and_usage(tmp_path, only_anthropic, monkeypatch):
    native = [dict(type='thinking', thinking='Consider the request.', signature='sig'),
              text('Adding both.'), tool('add_todo', {'todos': [{'title': 'One', 'due': None}]}),
              tool('add_todo', {'todos': [{'title': 'Two', 'due': None}]}, 'tool-2')]
    fake, requests = client(response(native, 'tool_use'), response([text('Added both.')]), response([text('Two tasks.')]))
    monkeypatch.setattr(adapter, 'Anthropic', lambda: fake)
    a = agents.Agent(TodoList(tmp_path/'todos.json'), model='claude-haiku-5-5')
    with capture() as usage:
        assert a.ask('Add One and Two') == 'Added “One.”\n\nAdded “Two.”\n\nAdded both.'
        assert a.last_model_reply == 'Added both.'
    assert [t.title for t in a.todos.todos] == ['One', 'Two']
    assert usage.total == 270  # Anthropic cache tokens are additional to input_tokens.
    assert requests[1]['messages'][-2]['content'] == native
    results = requests[1]['messages'][-1]['content']
    assert [r['tool_use_id'] for r in results] == ['tool-1', 'tool-2']
    assert all(not r['is_error'] for r in results)
    assert 'name' not in requests[0] and 'reasoning_effort' not in requests[0]
    a.ask('How many?')
    assert sum('The todo list right now' in b.get('text', '') for m in requests[2]['messages'] for b in m['content']) == 1


@pytest.mark.parametrize('failure', [AnthropicError('offline'), response([tool('add_todo', {'todos': [{'title':'Never', 'due':None}]})], 'max_tokens')])
def test_failure_after_save_preserves_receipt_and_undo(tmp_path, only_anthropic, monkeypatch, failure):
    fake, requests = client(response([tool('add_todo', {'todos': [{'title':'Saved', 'due':None}]})], 'tool_use'), failure)
    monkeypatch.setattr(adapter, 'Anthropic', lambda: fake)
    a = agents.Agent(TodoList(tmp_path/'todos.json'), model='claude-haiku-5-5')
    reply = a.ask('Add Saved')
    assert 'could not finish' in reply and 'Saved' in reply
    assert [t.title for t in a.todos.todos] == ['Saved']
    assert len(a.todos.undo_stack) == 1


def test_forbidden_tool_returns_error_without_approval(tmp_path, only_anthropic, monkeypatch):
    todos = TodoList(tmp_path/'todos.json'); todos.add('Keep')
    pending = todos.request_delete(1)
    fake, requests = client(response([tool('approve', {'id':pending.id})], 'tool_use'), response([text('Cannot approve.')]))
    monkeypatch.setattr(adapter, 'Anthropic', lambda: fake)
    a = agents.Agent(todos, model='claude-haiku-5-5'); a.ask('Approve it')
    assert len(todos.todos) == 1 and todos.pending
    assert requests[1]['messages'][-1]['content'][0]['is_error']


@pytest.mark.parametrize('answer,refused', [(True, True), (False, False)])
def test_boolean_merge_guard_has_no_probability(tmp_path, only_anthropic, monkeypatch, answer, refused):
    fake, requests = client(response([text(json.dumps({'todos.merge_unnamed':answer}))]))
    monkeypatch.setattr(guard_check, 'Anthropic', lambda **kw: fake)
    a=agents.Agent(TodoList(tmp_path/'todos.json'), model='claude-haiku-5-5')
    a.todos.add('One'); a.todos.add('Two'); a.seen=a.todos.snapshot()
    a.messages.append({'role':'user','content':'Merge One and Two'})
    result=a.run_tool('merge_todos', json.dumps({'ids':[1,2], 'title':'Both'}))
    assert ('error' in result) == refused
    record=a.tool_log[-1]['guard_checks'][0]
    assert record['answer'] is answer and 'probability' not in record
    assert MERGE_UNNAMED.provider == 'decisions'  # do not mutate shared declarations


@pytest.mark.parametrize('stop,payload', [('max_tokens','{}'), ('refusal','{}'), ('end_turn','{"todos.merge_unnamed":0.9}')])
def test_guard_missing_or_invalid_answer_fails_closed(only_anthropic, monkeypatch, stop, payload):
    from dataclasses import replace
    fake,_=client(response([text(payload)],stop))
    monkeypatch.setattr(guard_check,'Anthropic',lambda **kw:fake)
    with pytest.raises(ActionError):
        guard_check.ask_chat([replace(MERGE_UNNAMED,provider='chat')], {'words':'Merge them'})


def test_native_judge_and_persona_use_only_anthropic(only_anthropic, monkeypatch):
    import anthropic
    fake,requests=client(response([text('{"ok":true}')]))
    monkeypatch.setattr(anthropic,'Anthropic',lambda:fake)
    schema={'json_schema':{'schema':{'type':'object','properties':{'ok':{'type':'boolean'}},'required':['ok'],'additionalProperties':False}}}
    assert json.loads(judge.answer('Judge', 'Evidence', schema, 'test')) == {'ok':True}
    result=dict(click='none',message='Show overdue tasks',done=False,satisfied=False,frustrated=False,why='')
    fake,requests=client(response([text(json.dumps(result))]))
    monkeypatch.setattr(personas,'Anthropic',lambda:fake)
    history=[]
    assert personas.persona_says(personas.model_client(),'sam',personas.PERSONAS['sam'],history,'Empty',None)==result
    assert history[-1]['content']=='Show overdue tasks'


def test_provider_override_keeps_gateway_claude_on_openai(monkeypatch):
    from todo.model_provider import provider_for
    monkeypatch.setenv('EVALBASICS_AGENT_PROVIDER','openai')
    assert provider_for('agent','claude-gateway-alias')=='openai'
    monkeypatch.setenv('EVALBASICS_AGENT_PROVIDER','typo')
    with pytest.raises(ValueError): provider_for('agent','claude-test')


def test_native_costs_include_cache_and_unknown_models_keep_counts():
    from evaluations.eval_costs import estimate
    call=dict(purpose='agent', served_model='claude-haiku-5-5',
              usage=dict(input_tokens=1000,output_tokens=100,cache_read_input_tokens=200,
                         cache_creation_input_tokens=100,cache_creation={'ephemeral_1h_input_tokens':40}))
    cost=estimate([call])
    assert cost['complete'] and cost['input_tokens']==1300
    assert cost['usd']==pytest.approx(0.0001675)
    cost=estimate([dict(call,served_model='unknown-claude')])
    assert not cost['complete'] and cost['usd'] is None and cost['input_tokens']==1300


def test_missing_anthropic_key_keeps_manual_list_available(tmp_path, only_anthropic, monkeypatch):
    monkeypatch.delenv('ANTHROPIC_API_KEY',raising=False)
    a=agents.Agent(TodoList(tmp_path/'todos.json'),model='claude-haiku-5-5')
    assert a.client is None
    assert 'could not finish' in a.ask('Hello')


def test_one_provider_switch_selects_all_roles_and_merge_mode(monkeypatch):
    from todo import model_provider as config
    values={'EVALBASICS_PROVIDER':'anthropic'}
    monkeypatch.setattr(config,'setting',lambda name,default:values.get(name,default))
    for role in ('agent','judge','persona','action_guard'):
        assert config.model_for(role)=='claude-haiku-5-5'
        assert config.provider_for(role,config.model_for(role))=='anthropic'
    assert config.merge_guard_mode()=='boolean'
    values['EVALBASICS_PROVIDER']='openai'
    assert config.model_for('agent')=='gpt-6-luna'
    assert config.model_for('persona')=='gpt-4.1-mini'
    assert config.merge_guard_mode()=='decisions'
    values.update(EVALBASICS_JUDGE_PROVIDER='anthropic',EVALBASICS_JUDGE_MODEL='claude-custom')
    assert config.provider_for('judge',config.model_for('judge'))=='anthropic'
    assert config.model_for('judge')=='claude-custom'


@pytest.mark.parametrize('explanation', ['', 'I deleted everything.'])
def test_direct_confirmation_survives_empty_or_incorrect_model_reply(tmp_path, only_anthropic, monkeypatch, explanation):
    fake, _ = client(response([tool('add_todo', {'todos': [{'title': 'Saved', 'due': None}]})], 'tool_use'),
                     response([text(explanation or ' ') ]))
    monkeypatch.setattr(adapter, 'Anthropic', lambda: fake)
    a = agents.Agent(TodoList(tmp_path/'todos.json'), model='claude-haiku-5-5')
    delivered = a.ask('Add Saved')
    assert delivered.startswith('Added “Saved.”')
    assert a.last_model_reply.strip() == explanation
    assert a.messages[-1]['content'] == delivered
    assert [t.title for t in a.todos.todos] == ['Saved']
    assert len(a.todos.undo_stack) == 1


def test_empty_end_turn_is_not_reported_as_service_outage(tmp_path, only_anthropic, monkeypatch):
    fake, _ = client(response([tool('add_todo', {'todos': [{'title': 'Saved', 'due': None}]})], 'tool_use'),
                     response([]), response([]))
    monkeypatch.setattr(adapter, 'Anthropic', lambda: fake)
    a = agents.Agent(TodoList(tmp_path/'todos.json'), model='claude-haiku-5-5')
    assert a.ask('Add Saved') == 'Added “Saved.”'
    assert a.last_model_reply == ''
    assert a.messages[-1]['content'] == 'Added “Saved.”'
    assert a.ask('What is overdue?') == 'The model returned no answer.'
    assert a.last_model_reply == ''
    assert len(a.todos.todos) == 1
