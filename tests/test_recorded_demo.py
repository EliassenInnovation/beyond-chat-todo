import json
from todo.recorded_demo import ASSETS, replay_html


def test_replay_is_self_contained_and_has_no_model_access():
    page = replay_html()
    assert "fetch(" not in page
    assert 'src="persona-replay.js"' not in page
    assert 'id="play"' in page and 'id="next"' in page
    assert 'OPENAI_API_KEY' not in page


def test_recording_contains_complete_approval_lifecycle():
    record = json.loads((ASSETS / 'sam-recording.json').read_text())
    assert record['turns'][-1]['end']
    approval_turn = next(t for t in record['turns'] if t['clicked_ids'])
    pending = approval_turn['before_click']['waiting_for_approval']
    assert {p['id'] for p in pending} == set(approval_turn['clicked_ids'])
    assert not approval_turn['before']['waiting_for_approval']
    deleted = {p['todo_id'] for p in pending}
    assert not deleted.intersection(t['id'] for t in approval_turn['before']['todos'])
    assert record['final'] == record['turns'][-1]['after']


def test_unconfigured_app_opens_replay_without_agent(monkeypatch):
    from streamlit.testing.v1 import AppTest
    from unittest.mock import patch
    monkeypatch.setenv('EVALBASICS_PROVIDER', 'openai')
    monkeypatch.setenv('EVALBASICS_AGENT_PROVIDER', 'openai')
    monkeypatch.setenv('OPENAI_API_KEY', '')
    with patch('todo.agent.Agent', side_effect=AssertionError('Replay constructed Agent')):
        app = AppTest.from_file(str(ASSETS.parents[1] / 'todo' / 'app.py')).run(timeout=15)
    assert not app.exception
    assert app.selectbox[0].options == ['-- Prerecorded Run --']
