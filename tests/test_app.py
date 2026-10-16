"""The app's screen, driven headlessly with Streamlit's AppTest. No model calls.

AppTest cannot click inside the list component, so the page test checks what the component
is given, and the actions it reports are tested through todo_view.apply, the function the
page calls with them.
"""

import json
from pathlib import Path
from datetime import date

import pytest
from streamlit.testing.v1 import AppTest

import todo.langfuse_setup as langfuse_setup
import todo.todo_view as todo_view
from todo.capabilities import ActionError
from todo.todos import TodoError, TodoList
from todo.view import View


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv('EVALBASICS_DATA', str(tmp_path / 'todos.json'))
    # No tracing and no real keys: nothing from .env reaches the test process.
    monkeypatch.setattr(langfuse_setup, 'load_env', lambda *args, **kwargs: None)
    for key in ('LANGFUSE_PUBLIC_KEY', 'LANGFUSE_SECRET_KEY', 'LANGFUSE_TRACING_ENABLED'):
        monkeypatch.setenv(key, 'off' if key != 'LANGFUSE_TRACING_ENABLED' else 'false')
    monkeypatch.setenv('LANGFUSE_BASE_URL', 'http://127.0.0.1:9')
    monkeypatch.setenv('OPENAI_API_KEY', 'test')
    monkeypatch.setenv('EVALBASICS_PERSONA_PLAYER', 'false')
    import streamlit as st
    st.cache_resource.clear()  # the app connects once per process; each test decides afresh
    return AppTest.from_file(Path(__file__).resolve().parents[1] / 'todo/app.py', default_timeout=10), tmp_path / 'todos.json'


@pytest.fixture
def traced_app(app, monkeypatch):
    """The app as if run with ./run.sh --trace: it believes tracing is on, but its client sends nothing."""
    monkeypatch.setenv('LANGFUSE_TRACING_ENABLED', 'true')  # what --trace sets; the persona player reads it
    connect = langfuse_setup.connect
    monkeypatch.setattr(langfuse_setup, 'connect', lambda **kwargs: (connect(**kwargs)[0], True))
    return app


@pytest.fixture
def untraceable_app(app, monkeypatch):
    """./run.sh --trace with no Langfuse to reach: the real state of a machine without the server."""
    monkeypatch.setenv('LANGFUSE_TRACING_ENABLED', 'true')  # LANGFUSE_BASE_URL already points at a dead port
    return app


def test_without_tracing_there_is_no_persona_player(app):
    at, _ = app
    at.run()
    assert not at.exception
    assert not [s for s in at.selectbox if s.key == 'persona-picker']
    assert not [b for b in at.button if b.key == 'persona-next']


def test_the_persona_player_shows_with_trace_even_when_langfuse_is_unreachable(untraceable_app):
    """A persona reports in code, so the player is worth having untraced: --trace is what shows it."""
    at, _ = untraceable_app
    at.run()
    assert not at.exception
    assert [s for s in at.selectbox if s.key == 'persona-picker']


def test_the_page_shows_the_list_and_the_assistant(app):
    at, _ = app
    at.run()
    assert not at.exception
    at.session_state.todos.add('Call the plumber', due='2026-09-28')
    at.session_state.todos.request_delete(1)  # what the agent's request_delete does
    at.run()
    shown = json.loads(at.get('bidi_component')[0].proto.json)
    assert [(t['title'], t['due']) for t in shown['todos']] == [('Call the plumber', '2026-09-28')]
    assert [p['title'] for p in shown['pending']] == ['Call the plumber']
    assert len(at.chat_input) == 1


def recorded_marker(at):
    return [h for h in at.get('html') if 'Recording to Langfuse' in h.proto.body]


def test_the_screen_says_when_a_chat_is_recorded(traced_app):
    """A persona's chat goes to Langfuse, and so does anything typed into it: the screen says so."""
    at, _ = traced_app
    at.run()
    assert not recorded_marker(at)  # your own chat: never sent, so nothing to say
    at.selectbox(key='persona-picker').select('sam').run()
    assert recorded_marker(at)


def test_the_exploratory_tester_types_on_a_scratch_list_and_is_recorded(traced_app):
    """Chosen from the picker: no persona plays, a person types on a scratch list, and the chat is recorded."""
    import evaluations.personas as personas
    at, real = traced_app
    at.run()
    at.session_state.todos.add('My own todo')
    at.selectbox(key='persona-picker').select('Exploratory tester').run()
    titles = [t.title for t in at.session_state.todos.todos]
    assert len(titles) == len(personas.TESTER['start']) and 'Call the plumber' in titles
    assert [t.title for t in TodoList(real).todos] == ['My own todo']  # your list is untouched
    assert at.session_state.session_id.startswith('tester-') and at.session_state.persona is None
    assert not [b for b in at.button if b.key == 'persona-next']  # nobody to play: you type
    assert recorded_marker(at)


def test_no_recorded_marker_when_nothing_is_sent(untraceable_app):
    at, _ = untraceable_app
    at.run()
    at.selectbox(key='persona-picker').select('sam').run()
    assert not recorded_marker(at)  # --trace asked for, but Langfuse is not there: nothing leaves


def test_a_persona_lives_on_the_real_date_with_its_dates_moved_to_match(traced_app, monkeypatch):
    """The app and the list use the real date; a persona's dates, written for TODAY, move with it,
    so two weeks overdue stays two weeks overdue."""
    import evaluations.personas as personas
    from datetime import date as day
    at, _ = traced_app
    at.run()
    shown = lambda: json.loads(at.get('bidi_component')[0].proto.json)
    assert shown()['today'] == date.today().isoformat()  # you, on your own list: the real date
    at.selectbox(key='persona-picker').select('sam').run()
    assert shown()['today'] == date.today().isoformat()  # and a persona too
    passport = next(t for t in at.session_state.todos.todos if 'passport' in t.title.lower())
    written = next(d for item, d in [i for i in personas.PERSONAS['sam']['start'] if isinstance(i, tuple)] if 'passport' in item.lower())
    assert day.fromisoformat(passport.due) - date.today() == day.fromisoformat(written) - personas.TODAY


def test_screen_actions_use_the_list_operations(tmp_path):
    todos = TodoList(tmp_path / 'todos.json')
    view = View()
    for title in ('Call the plumber', 'Buy milk', 'Walk the dog'):
        todo_view.apply(todos, view, {'op': 'add', 'title': title, 'due': None})
    todo_view.apply(todos, view, {'op': 'complete', 'id': 1})
    todo_view.apply(todos, view, {'op': 'move', 'id': 3, 'below': None})  # dragged to the top
    assert [(t.title, t.done) for t in TodoList(todos.path).todos] == [
        ('Walk the dog', False), ('Call the plumber', True), ('Buy milk', False)]

    todo_view.apply(todos, view, {'op': 'toggle_all'})
    assert all(t.done for t in todos.todos)
    todo_view.apply(todos, view, {'op': 'toggle_all'})
    assert not any(t.done for t in todos.todos)

    todo_view.apply(todos, view, {'op': 'set_due', 'id': 2, 'due': '2026-10-02'})  # clicked the date
    assert todos.get(2).due == '2026-10-02'
    todo_view.apply(todos, view, {'op': 'set_due', 'id': 2, 'due': None})  # cleared it
    assert todos.get(2).due is None

    todos.request_delete(2)
    todo_view.apply(todos, view, {'op': 'rename', 'id': 2, 'title': 'Buy oat milk'})  # clicked the text
    assert todos.get(2).title == 'Buy oat milk' and todos.pending[0].title == 'Buy milk'
    with pytest.raises(TodoError):
        todo_view.apply(todos, view, {'op': 'rename', 'id': 2, 'title': ' '})
    with pytest.raises(TodoError, match='changed since'):
        todo_view.apply(todos, view, {'op': 'approve', 'id': 1})
    todo_view.apply(todos, view, {'op': 'deny', 'id': 1})
    fresh = todos.request_delete(2)
    todo_view.apply(todos, view, {'op': 'approve', 'id': fresh.id})
    assert [t.title for t in TodoList(todos.path).todos] == ['Walk the dog', 'Call the plumber']

    todo_view.apply(todos, view, {'op': 'complete', 'id': 1})
    todo_view.apply(todos, view, {'op': 'clear_completed'})
    assert [t.title for t in todos.todos] == ['Walk the dog']
    with pytest.raises(TodoError):
        todo_view.apply(todos, view, {'op': 'add', 'title': '  ', 'due': None})


def test_the_filter_belongs_to_the_app_so_the_agent_can_set_it_too(tmp_path):
    todos, view = TodoList(tmp_path / 'todos.json'), View()
    todo_view.apply(todos, view, {'op': 'filter', 'filter': 'completed'})  # the person clicks Completed
    assert view.showing == 'completed'
    with pytest.raises(ActionError, match='must be one of all, active'):  # refused at the shared boundary
        todo_view.apply(todos, view, {'op': 'filter', 'filter': 'overdue'})


def test_a_persona_plays_on_its_own_list_and_next_speaks_for_it(traced_app, monkeypatch):
    import todo.agent as agent_module
    import evaluations.personas as personas
    at, real = traced_app
    lines = iter([dict(click='none', message='Show me only my chores.', done=False, satisfied=False, frustrated=False, why=''),
                  dict(click='none', message='Thanks, that is it.', done=True, satisfied=True, frustrated=False, why='')])
    monkeypatch.setattr(personas, 'persona_says', lambda *args, **kwargs: next(lines))
    monkeypatch.setattr(agent_module.Agent, 'ask', lambda self, text: f'(reply to {text})')
    at.run()
    at.session_state.todos.add('My own todo')
    at.selectbox(key='persona-picker').select('priya').run()
    assert [t.title for t in at.session_state.todos.todos][:1] == ['Take out the recycling (Priya)']
    assert [t.title for t in TodoList(real).todos] == ['My own todo']  # your list is untouched

    at.button(key='persona-next').click().run()
    assert at.session_state.chat == [('Priya', 'Show me only my chores.'),
                                     ('assistant', '(reply to Show me only my chores.)')]
    at.button(key='persona-next').click().run()  # done: said below the chat, and Next turns off
    assert len(at.session_state.chat) == 2 and at.button(key='persona-next').disabled
    assert any('Priya is done, satisfied' in c.value for c in at.caption)

    at.selectbox(key='persona-picker').select('None').run()
    assert [t.title for t in at.session_state.todos.todos] == ['My own todo'] and at.session_state.chat == []


def test_a_persona_click_shows_in_the_chat_but_only_its_words_reach_the_assistant(traced_app, monkeypatch):
    import todo.agent as agent_module
    import evaluations.personas as personas
    at, _ = traced_app
    monkeypatch.setattr(personas, 'persona_says', lambda *args, **kwargs: dict(
        click='approve', message='Go ahead.', done=False, satisfied=False, frustrated=False, why=''))
    monkeypatch.setattr(agent_module.Agent, 'ask', lambda self, text: f'(reply to {text})')
    at.run()
    at.selectbox(key='persona-picker').select('leo').run()
    at.session_state.todos.request_delete(4)  # 'Cancel the gym', waiting for approval
    at.button(key='persona-next').click().run()
    assert at.session_state.chat == [('Leo', '*Clicked Approve.* Go ahead.'), ('assistant', '(reply to Go ahead.)')]
    assert 'Cancel the gym' not in [t.title for t in at.session_state.todos.todos]


def test_play_keeps_the_persona_going_until_it_is_done(traced_app, monkeypatch):
    import todo.agent as agent_module
    import evaluations.personas as personas
    at, _ = traced_app
    lines = iter([dict(click='none', message='Show me only my chores.', done=False, satisfied=False, frustrated=False, why=''),
                  dict(click='none', message='Now the dated ones.', done=False, satisfied=False, frustrated=False, why=''),
                  dict(click='none', message='Thanks, that is it.', done=True, satisfied=True, frustrated=False, why='')])
    monkeypatch.setattr(personas, 'persona_says', lambda *args, **kwargs: next(lines))
    monkeypatch.setattr(agent_module.Agent, 'ask', lambda self, text: f'(reply to {text})')
    at.run()
    at.selectbox(key='persona-picker').select('priya').run()
    assert at.button(key='persona-play').label == 'Play'
    at.button(key='persona-play').click().run()
    assert [role for role, _ in at.session_state.chat] == ['Priya', 'assistant', 'Priya', 'assistant']
    assert not at.session_state.playing and at.button(key='persona-play').disabled  # done: nothing left to play
    assert any('Priya is done, satisfied' in c.value for c in at.caption)


def test_play_stops_when_the_persona_is_frustrated(traced_app, monkeypatch):
    import todo.agent as agent_module
    import evaluations.personas as personas
    at, _ = traced_app
    lines = iter([dict(click='none', message='Hide the done ones.', done=False, satisfied=False, frustrated=True,
                       why='It keeps showing everything.')])
    monkeypatch.setattr(personas, 'persona_says', lambda *args, **kwargs: next(lines))
    monkeypatch.setattr(agent_module.Agent, 'ask', lambda self, text: f'(reply to {text})')
    at.run()
    at.selectbox(key='persona-picker').select('priya').run()
    at.button(key='persona-play').click().run()
    assert len(at.session_state.chat) == 2 and not at.session_state.playing
    assert at.button(key='persona-play').label == 'Play' and not at.button(key='persona-next').disabled


def test_pause_drops_the_persona_turn_that_is_only_queued(traced_app, monkeypatch):
    import evaluations.personas as personas
    at, _ = traced_app
    monkeypatch.setattr(personas, 'persona_says', lambda *args, **kwargs: pytest.fail('paused: no persona turn'))
    at.run()
    at.selectbox(key='persona-picker').select('priya').run()
    at.session_state.playing = True  # as between turns while playing: the next one is queued
    at.session_state.pending = ('persona', None)
    at.button(key='persona-play').click().run()
    assert not at.session_state.playing and at.session_state.pending is None and at.session_state.chat == []
    assert at.button(key='persona-play').label == 'Play'


def test_app_can_open_without_a_model_key(app, monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    at, _ = app
    at.run()
    assert not at.exception


def test_visible_persona_player_does_not_require_trace_export(app, monkeypatch):
    monkeypatch.setenv('EVALBASICS_PERSONA_PLAYER', 'true')
    at, _ = app
    at.run()
    assert not at.exception
    assert [s for s in at.selectbox if s.key == 'persona-picker']
    assert not any('Recording to Langfuse' in item.value for item in at.caption)


def test_untraced_exploratory_tester_does_not_claim_export(app, monkeypatch):
    monkeypatch.setenv('EVALBASICS_PERSONA_PLAYER', 'true')
    at, _ = app
    at.run()
    picker=next(s for s in at.selectbox if s.key=='persona-picker')
    picker.select('Exploratory tester').run()
    assert not at.exception
    captions=' '.join(c.value for c in at.caption)
    assert 'Trace export is off.' in captions
    assert 'this chat is recorded to langfuse' not in captions.lower()
