"""Unattended exploration must preserve evidence and never replay side effects."""
import json
from types import SimpleNamespace

import pytest
import todo.model_usage as model_usage
import evaluations.personas as personas
import evaluations.persona_report as persona_report
from test_personas import FakeAgent, persona_model


def setup_player(monkeypatch, *turns):
    monkeypatch.setattr(personas, 'OpenAI', persona_model(*turns))
    monkeypatch.setattr(personas, 'Agent', FakeAgent)
    monkeypatch.setattr(personas, 'claims_match_outcome', lambda *a: (True, ''))


def test_judge_failure_keeps_paid_conversation_and_allows_review(monkeypatch):
    setup_player(monkeypatch, {'message': 'add Hat'}, {'message': 'thanks', 'done': True, 'satisfied': True})
    def broken(*args):
        raise RuntimeError('judge unavailable')
    monkeypatch.setattr(personas, 'claims_match_outcome', broken)
    checkpoints = []
    result = personas.run('grace', max_turns=2, on_update=checkpoints.append)
    assert result['status'] == 'satisfied'
    assert result['turns'][0]['after']['visible'] == ['Water the plants', 'Hat']
    assert result['turns'][0]['truthful'] is None
    assert any('assistant' in r['turns'][0] and 'judge_error' not in r['turns'][0]
               for r in checkpoints if r['turns'])
    assert any(f['kind'] == 'note: judgment unavailable' for f in result['findings'])
    assert checkpoints[0]['turns'] == []  # callbacks are detached snapshots


def test_interrupt_preserves_state_and_is_not_an_agent_failure(monkeypatch):
    setup_player(monkeypatch, {'message': 'add Hat'})
    class Interrupted(FakeAgent):
        def ask(self, text):
            self.todos.add('Hat')
            raise KeyboardInterrupt()
    monkeypatch.setattr(personas, 'Agent', Interrupted)
    checkpoints = []
    result = personas.run('grace', on_update=checkpoints.append)
    assert result['status'] == 'interrupted'
    assert result['turns'][0]['after']['visible'] == ['Water the plants', 'Hat']
    assert result == checkpoints[-1]
    assert not any(f['kind'] == 'the agent crashed' for f in result['findings'])


def test_terminal_persona_click_is_recorded_with_before_and_after(monkeypatch):
    setup_player(monkeypatch, {'message': 'delete plants'},
                 {'message': 'thanks', 'click': 'approve', 'done': True, 'satisfied': True})
    class Deleting(FakeAgent):
        def ask(self, text):
            self.todos.request_delete(1)
            return 'Waiting for approval.'
    monkeypatch.setattr(personas, 'Agent', Deleting)
    result = personas.run('grace')
    ending = result['turns'][-1]
    assert ending['clicked_ids'] == [1]
    assert ending['before_click']['todos'][0]['title'] == 'Water the plants'
    assert ending['after']['todos'] == []
    assert result['final']['todos'] == []


def response(tokens):
    return SimpleNamespace(model='actual-model', usage=SimpleNamespace(model_dump=lambda: {'total_tokens': tokens}))


def test_budget_covers_calls_and_blocks_next_call_without_changing_response():
    calls = []
    def provider(**kwargs):
        calls.append(kwargs)
        return response(7)
    with model_usage.capture(10) as usage:
        for purpose in ('persona', 'agent'):
            assert model_usage.call_model(provider, purpose=purpose, model='requested').model == 'actual-model'
        with pytest.raises(model_usage.TokenLimitReached):
            model_usage.call_model(provider, purpose='judge', model='requested')
    assert len(calls) == 2 and usage.total == 14
    assert usage.summary()['complete']
    assert [c['purpose'] for c in usage.calls] == ['persona', 'agent']
    assert model_usage.call_model(provider, purpose='agent', model='requested').model == 'actual-model'


def test_unknown_usage_stops_further_spend():
    with model_usage.capture(100) as usage:
        model_usage.call_model(lambda: object(), purpose='persona')
        assert not usage.summary()['complete']
        with pytest.raises(model_usage.TokenLimitReached, match='unavailable'):
            model_usage.call_model(lambda: pytest.fail('must not call'), purpose='agent')


def test_budget_stop_is_saved_as_harness_limit(monkeypatch):
    setup_player(monkeypatch, {'message': 'add Hat'})
    def limited(*args, **kwargs):
        raise model_usage.TokenLimitReached('allowance reached')
    monkeypatch.setattr(personas, 'persona_says', limited)
    result = personas.run('grace')
    assert result['status'] == 'token_limit' and result['turns'] == []
    assert result['findings'] == []


def test_replay_is_offline_and_escapes_model_text(monkeypatch, tmp_path):
    path = tmp_path / 'run.json'
    persona_report.save_record(path, [{'persona': '<script>bad()</script>', 'turns': [], 'final': {}}])
    monkeypatch.setattr(personas, 'connect', lambda **kwargs: pytest.fail('replay must be offline'))
    personas.main(['--replay', str(path)])
    page = path.with_suffix('.html').read_text()
    assert '<script>bad()</script>' not in page
    assert '&lt;script&gt;bad()&lt;/script&gt;' in page
    assert 'Recorded conversation' in page


def test_failed_atomic_replace_preserves_previous_checkpoint(monkeypatch, tmp_path):
    path = tmp_path / 'run.json'
    persona_report.save_record(path, {'old': True})
    def broken(*args):
        raise OSError('disk error')
    monkeypatch.setattr(persona_report.os, 'replace', broken)
    with pytest.raises(OSError):
        persona_report.save_record(path, {'new': True})
    assert json.loads(path.read_text()) == {'old': True}
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize('option', ['--turns', '--max-tokens'])
def test_nonpositive_limits_rejected_before_connect(monkeypatch, option):
    monkeypatch.setattr(personas, 'connect', lambda **kwargs: pytest.fail('must not connect'))
    with pytest.raises(SystemExit):
        personas.main([option, '0'])


def test_visible_persona_event_dates_move_with_the_list():
    from datetime import timedelta
    dana=personas.PERSONAS['dana']
    assert personas.persona_who(dana)=="Dana, a parent planning her daughter's birthday party on Saturday, October 3."
    assert 'Thursday, October 8' in personas.persona_who(dana, personas.TODAY+timedelta(days=5))
    grace=personas.PERSONAS['grace']
    assert 'Saturday, October 10' in personas.persona_who(grace)
    assert 'Thursday, October 15' in personas.persona_who(grace, personas.TODAY+timedelta(days=5))
