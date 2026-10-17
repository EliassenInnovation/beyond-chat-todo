"""The app: your todo list, with a chat with the agent (the assistant) beside it.

    .venv/bin/python -m streamlit run todo/app.py

Both work on the same TodoList object: tick a box and the agent sees it the next time it
reads the list; ask the agent and the list updates. Deleting differs on purpose: you delete
with one click, the agent can only ask, and its request waits here for you.
The list is a component (todo_view.py) that reports what you did; this page carries it out
with the same registered actions the agent's tools run (capabilities.execute).
Tracing is off unless turned on (LANGFUSE_TRACING_ENABLED=true), which also shows the persona player: the
player needs no Langfuse (a persona reports in code), so it shows whether or not the server is
reachable, and links to a trace when there is one. Even traced, a chat of your own is never sent,
and a production chat has no way out. A persona played here is traced, each thing it says one trace,
its whole chat one session, and so is anything you type into its chat to test it, or into the
Exploratory tester's (picked like a persona: you type, on a scratch list): the screen then says
"Recording to Langfuse".
"""

# macOS: the OpenAI library asks platform for the processor, which runs `uname -p` in a child process,
# the first time a client sends a request. In this app that happens in a thread, after the network code
# has looked up proxies, and on 2026-10-06 the child crashed before it ran (a "Python quit unexpectedly"
# report each time a persona started; the app itself carried on). Asking once here, before any of that
# is loaded, fills platform's cache, so no child is started later.
import os
import platform
# Streamlit runs this file in a thread, so even asking here runs `uname -p` from a thread (crash 2026-10-13).
# Python 3.13 caches the processor on platform.uname()'s result; fill it from os.uname(), with no child process.
platform.uname().__dict__.setdefault('processor', os.uname().machine)
# platform.architecture() runs the `file` command for the same OpenAI headers; answer from Python itself instead.
platform._syscmd_file = lambda target, default='': default

import base64
from datetime import date
import html
import uuid
from pathlib import Path

import streamlit as st
from langfuse import propagate_attributes
from streamlit.components.v2 import component

import evaluations.personas as personas
import todo.todo_view as todo_view
from todo.agent import Agent
from todo.langfuse_setup import RECORDED_SESSIONS, connect, synthetic_only, setting
from todo.capabilities import ActionError
from todo.todos import TodoList
from todo.view import View

DATA = Path(os.environ.get('EVALBASICS_DATA', Path(__file__).resolve().parents[1] / 'todos.json'))

st.set_page_config(page_title='Todos', layout='wide')

# An unconfigured checkout opens a useful replay without constructing a model client.
# Presence of a key means configured, not that a provider has been contacted or verified.
from todo.model_provider import model_for, provider_for
from todo.recorded_demo import replay_html

agent_provider = provider_for('agent', model_for('agent'))
model_configured = bool(setting('ANTHROPIC_API_KEY' if agent_provider == 'anthropic' else 'OPENAI_API_KEY', '').strip())
show_demo = st.sidebar.checkbox('Show recorded demo', value=not model_configured)
if show_demo:
    st.iframe(replay_html(), height=1150, alt="Recorded persona session with playback controls")
    st.stop()



@st.cache_resource
def langfuse_connection():
    # Off unless turned on (LANGFUSE_TRACING_ENABLED=true), and even then only a persona's conversation leaves the
    # process: a trace is a copy of what was said, and a real person's words stay here.
    # asked_for is read before connect(), which clears the variable when Langfuse is unreachable;
    # cached, so it survives the reruns that re-execute this module.
    asked_for = setting('LANGFUSE_TRACING_ENABLED', '').lower() == 'true'
    show_player = setting('EVALBASICS_PERSONA_PLAYER', '').lower() == 'true' or asked_for
    client, live = connect(should_export_span=synthetic_only, opt_in=True)  # once per process, before anything is traced
    return client, live, show_player


langfuse, live, player_on = langfuse_connection()  # player_on is independent of whether tracing is available

state = st.session_state
NO_PERSONA = 'None'  # you, on your own list
EXPLORATORY = 'Exploratory tester'  # you type, on a scratch list, and the chat is recorded
# Each persona has a colour from the palette, so its messages are told apart at a glance: a box of
# that colour with the persona's initial in white. Anyone not listed gets the ink colour.
PERSONA_COLORS = {'dana': '#d87a76', 'sam': '#33438f', 'priya': '#99beb4', 'leo': '#dfb77c', 'grace': '#7391a5'}
INK = '#1b1e32'


def recorded():
    """True when this chat goes to Langfuse: tracing is live and the session is a persona's, the same
    test synthetic_only applies at export. Anything typed into it goes too, so the screen says so."""
    return bool(live and state.session_id.startswith(RECORDED_SESSIONS))


def session_link():
    """This persona chat in Langfuse, or None. A link is a convenience: without Langfuse, no link."""
    if not (live and (state.persona or state.tester) and state.agent.last_trace_id):
        return None
    try:
        trace_url = langfuse.get_trace_url(trace_id=state.agent.last_trace_id)
    except Exception:
        return None
    return f'{trace_url.rsplit("/traces/", 1)[0]}/sessions/{state.session_id}'


def badge(name, size=64):
    """The persona's avatar: its colour, its initial in white (SVG, which the chat accepts as an image)."""
    color = PERSONA_COLORS.get(name.lower(), INK)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 64 64">'
            f'<rect width="64" height="64" rx="12" fill="{color}"/><text x="32" y="44" text-anchor="middle" '
            f'font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="34" font-weight="600" '
            f'fill="#ffffff">{name[:1].upper()}</text></svg>')


def start(todos, persona=None, tester=False):
    """A fresh chat on this list: a new agent, a new Langfuse session, and the persona playing, if any.
    tester: an exploratory tester, a person typing on a scratch list, recorded; no persona plays."""
    state.todos = todos
    state.view = View()  # what the screen shows; the filter buttons and the agent both set it
    state.agent = Agent(state.todos, view=state.view)  # the real date; persona and tester lists are moved to it
    state.chat = []
    state.session_id = f'{"persona-" + persona if persona else "tester" if tester else "chat"}-{uuid.uuid4().hex[:8]}'
    state.persona, state.tester, state.persona_history, state.persona_said = persona, tester, [], None
    state.pending = None  # the step to take after this redraw: ('persona', None) or ('assistant', text)
    state.playing = False  # Play: the persona keeps taking turns until it is done, frustrated, or paused


if 'tester' not in state:  # a new session (or one from before the persona player or the tester)
    start(TodoList(DATA))
todos, view, agent = state.todos, state.view, state.agent

# The list and the assistant side by side in a centered 1300px band; Streamlit stacks the columns
# on narrow screens. The assistant gets a title in the same type as "todos", so the two cards
# start at the same height. Streamlit gives each keyed element the class st-key-<key>; this is
# presentation only.
# In the tour's frame (?tour=1; Streamlit keeps ?embed to itself), the page drops its top margin:
# the frame is scaled to fit, so empty space costs size.
TOP = 0.5 if st.query_params.get('tour') == '1' else 2.75
st.html('''<style>
.block-container, [data-testid="stMainBlockContainer"] {max-width: 1300px; padding-top: TOPrem}
.title {margin: 0 0 8px; padding: 0; text-align: center; font-family: "Helvetica Neue", Helvetica,
  Arial, sans-serif; font-size: 56px; font-weight: 200; line-height: 1.1; color: #b83f45}
.st-key-assistant {margin-top: -1rem; background: #ffffff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2), 0 25px 50px rgba(0,0,0,0.1)}
.st-key-assistant [data-testid="stChatMessage"] {padding: 0.4rem 0.6rem; gap: 0.6rem}
.st-key-assistant [data-testid="stChatMessage"] p {font-size: 0.9rem; line-height: 1.45}
.st-key-assistant [data-testid^="stChatMessageAvatar"],
.st-key-assistant [data-testid="stChatMessage"] > img {width: 1.6rem; height: 1.6rem}  /* a persona's avatar is an img */
/* Room under the newest exchange, so it can sit at the top of the chat box (chat_scroll.js). */
.chat-spacer {height: 220px}
.recorded {display: flex; align-items: center; gap: 6px; font-size: 0.8rem; font-weight: 600; color: #b83f45; margin: 2px 0 4px 8px}  /* in line with the chat's avatars */
.recorded .dot {width: 8px; height: 8px; border-radius: 50%; background: #b83f45}
.recorded a {color: #33438f; font-weight: 600; text-decoration: none}
.persona-card {display: flex; gap: 10px; align-items: flex-start; font-size: 0.85rem; line-height: 1.5; color: #4f6599}
.persona-card b {color: #1b1e32; font-weight: 600}
.persona-card a {display: block; margin-top: 2px; color: #33438f; font-weight: 600; text-decoration: none}
.persona-card img {flex-shrink: 0; width: 1.6rem; height: 1.6rem; margin-top: 1px}
</style>'''.replace('TOP', str(TOP)))

CHAT_HEIGHT = 260 if player_on else 380  # px; the chat scrolls inside this; the persona player, when shown, takes the rest

# The chat scrolls in whole exchanges, and a new one lands at the top of the box: chat_scroll.js.
CHAT_SCROLL = Path(__file__).parent / 'assets' / 'chat_scroll.js'

list_side, assistant_side = st.columns(2, gap='large')

with list_side:
    # The real date, for the list as for the agent: persona and tester lists are moved to it (start_list).
    action = todo_view.show(todos, view)
    if action:
        try:
            todo_view.apply(todos, view, action)
        except (ActionError, OSError) as error:
            st.toast(str(error))
        st.rerun()

with assistant_side:
    st.html('<h1 class="title">assistant</h1>')
    with st.container(key='assistant', border=True):
        # The box has its full height from the start, empty or not, so the page does not jump
        # at the first message. One keyed container per exchange (what you said, then the
        # reply): the unit the scroll snaps to. autoscroll keeps the newest in view.
        exchanges = [state.chat[n:n + 2] for n in range(0, len(state.chat), 2)]
        with st.container(key='chat', height=CHAT_HEIGHT, border=False):
            if not exchanges:
                st.caption('Ask it to add, date, finish or reorder todos.')
            for n, exchange in enumerate(exchanges):
                with st.container(key=f'exchange-{n}'):  # stable names; the script finds the newest by order
                    for role, text in exchange:
                        persona_avatar = badge(role) if role.lower() in personas.PERSONAS else None
                        st.chat_message(role, avatar=persona_avatar).write(text)
            if exchanges:  # a real block: Streamlit leaves out an empty container
                st.html('<div class="chat-spacer"></div>')
        # ready: no step is running, so the input box is enabled again and can take the focus back.
        component('chat_scroll', js=CHAT_SCROLL.read_text())(key='chat-scroll', data={'exchanges': len(exchanges),
                                                                                    'ready': not state.pending})
        # While a step runs, the input box says whose turn it is; nothing else on the page moves.
        waiting = {'persona': f'{(state.persona or "").title()} is typing…',
                   'assistant': 'The assistant is replying…'}.get(state.pending and state.pending[0])
        # Recording is never silent: when this chat goes to Langfuse, including anything you type into
        # a persona's chat to test it, the screen says so. A production chat has no path out at all.
        if recorded():
            link = session_link()
            st.html('<div class="recorded"><span class="dot"></span>Recording to Langfuse'
                    + (f' · <a href="{html.escape(link)}" target="_blank">open</a>' if link else '') + '</div>')
        if prompt := st.chat_input(waiting or 'Tell the assistant what to do', disabled=bool(waiting) or not model_configured, key='chat-input'):
            state.chat.append(('user', prompt))
            state.pending = ('assistant', prompt)
            st.rerun()

    # The persona player (personas.py): pick a person, and each Next has a second model write
    # what they would say next, sent to the assistant as if typed. A persona plays on its own
    # scratch list, so your list is never touched; pick None to go back to it.
    # It shows when tracing was asked for (LANGFUSE_TRACING_ENABLED=true), whether or not Langfuse is reachable:
    # a persona plays and reports in code, so it is worth watching untraced too. With Langfuse there,
    # each thing it says is a trace and the card links to it.
    if player_on and model_configured:
        # None and the exploratory tester are not personas: a dropdown cannot set them in italics, so
        # dashes mark them, first.
        choices = [NO_PERSONA, EXPLORATORY] + list(personas.PERSONAS)
        label = {NO_PERSONA: '-- None --', EXPLORATORY: '-- Exploratory Tester --'}
        current = state.persona or (EXPLORATORY if state.tester else NO_PERSONA)
        picker, play, step = st.columns([3, 1.3, 1.2], vertical_alignment='bottom')
        picked = picker.selectbox('Persona', choices, index=choices.index(current),
                                  format_func=lambda c: label.get(c, c.title()), key='persona-picker')
        if picked != current:
            if picked == NO_PERSONA:
                start(TodoList(DATA))
            elif picked == EXPLORATORY:
                start(personas.start_list(personas.TESTER, date.today()), tester=True)
            else:
                start(personas.start_list(personas.PERSONAS[picked], date.today()), picked)
            st.rerun()
        if state.tester:
            link = session_link()
            st.caption('**Exploratory tester:** you type, on a scratch list made for probing; your own list is '
                       'untouched. ' + ('This chat is recorded to Langfuse.' if recorded() else 'Trace export is off.') + (f'  \n[This chat in Langfuse]({link})' if link else ''))
        if state.persona:
            persona = personas.PERSONAS[state.persona]
            said = state.persona_said
            finished = bool(said and said['done'])
            # Play keeps the persona going on its own; Next takes one turn. Pause stays live while a turn
            # runs. Streamlit stops a page only at its next Streamlit call, so the step that is running
            # finishes whole (no half-made change); Pause then drops the persona's next turn if it is only
            # queued. A reply still owed to what the persona said is given.
            playing = state.get('playing', False)
            if play.button('Pause' if playing else 'Play', icon=':material/pause:' if playing else ':material/play_arrow:',
                           key='persona-play', disabled=finished, width='stretch'):
                state.playing = not playing
                if state.playing and not state.pending:
                    state.pending = ('persona', None)
                elif not state.playing and state.pending and state.pending[0] == 'persona':
                    state.pending = None
                st.rerun()
            if step.button('Next', icon=':material/skip_next:', key='persona-next',
                           disabled=finished or playing or bool(state.pending), width='stretch'):
                state.pending = ('persona', None)
                st.rerun()
            # The Langfuse link sits under the persona's line (only a persona's chat is sent to Langfuse).
            link = session_link()
            if finished:
                st.caption(f"**{state.persona.title()} is done, {'satisfied' if said['satisfied'] else 'not satisfied'}.** "
                           f"{said['message']} {said['why']}".strip() + (f'  \n[This chat in Langfuse]({link})' if link else ''))
            elif said and said['frustrated']:
                st.caption(f"**{state.persona.title()} is frustrated:** {said['why']}"
                           + (f'  \n[This chat in Langfuse]({link})' if link else ''))
            else:
                chip = base64.b64encode(badge(state.persona, 26).encode()).decode()  # st.html drops inline SVG
                st.html(f'<div class="persona-card"><img alt="" src="data:image/svg+xml;base64,{chip}"><div><b>{html.escape(personas.persona_who(persona, date.today()))}</b> '
                        f'Wants: {html.escape(persona["wants"])}'
                        + (f' <a href="{html.escape(link)}" target="_blank" rel="noopener">This chat in Langfuse</a>' if link else '')
                        + '</div></div>')

# The step asked for above runs after the page is drawn, so the input box already says who is
# typing; then the page is drawn again with the result. A persona's turn is two steps: its
# message, then the assistant's reply.
if state.pending:
    kind, text = state.pending
    tags = ['app', 'persona', state.persona] if state.persona else ['app', 'tester'] if state.tester else ['app']
    # Everything traced inside carries this session id; only a persona's session is exported.
    with propagate_attributes(session_id=state.session_id, tags=tags):
        if kind == 'persona':
            persona = personas.PERSONAS[state.persona]
            last_reply = next((t for role, t in reversed(state.chat) if role == 'assistant'), None)
            try:
                said = personas.persona_says(personas.model_client(), state.persona, persona, state.persona_history,
                                             personas.screen(todos, view), last_reply, today=date.today())
            except personas.PersonaStopped as stopped:
                said = dict(click='none', message='', done=True, satisfied=False, frustrated=False,
                            why=f'The persona stopped: {stopped}')
            clicked = bool(todos.pending) and said['click'] != 'none'
            personas.click(todos, said['click'])
            state.persona_said, state.pending = said, None
            if said['done']:
                state.playing = False
            if not (said['done'] and state.chat):  # done after a turn: the persona says so below the chat
                # A click is shown with the message, so a todo does not vanish unexplained;
                # the assistant is sent only what was typed.
                shown = f"*Clicked {said['click'].title()}.* " if clicked else ''
                state.chat.append((state.persona.title(), shown + said['message']))
                state.pending = ('assistant', said['message'])
        else:
            state.chat.append(('assistant', agent.ask(text)))
            state.pending = None
            said = state.persona_said if state.persona else None
            if state.get('playing') and said and not (said['done'] or said['frustrated']):
                state.pending = ('persona', None)  # playing: the persona's next turn
            else:
                state.playing = False  # done or frustrated: stop, so the card below says why
    st.rerun()
