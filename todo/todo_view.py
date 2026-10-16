"""The todo list on screen: a Streamlit component with TodoMVC's look (todo_view.js, .css).

The component only reports what the person did, as an action like {'op': 'move', 'id': 3,
'below': 1}. `apply` turns that into the same registered action the agent's tool runs, through
the same `execute`, as the person; so the logic stays in todos.py and view.py. Approving a
delete is here because only the person can do it.
"""

from datetime import date
from pathlib import Path
from types import SimpleNamespace

from streamlit.components.v2 import component

from todo.capabilities import REGISTRY, execute
from todo.todos import TodoList
from todo.view import View

HERE = Path(__file__).parent / 'assets'

def show(todos: TodoList, view: View, key='todo-list', today=None):
    """Draw the list; return what the person just did (an action dict), or None.
    today: the date the list colors overdue against, the one the agent has (a persona's fixed day); default the real one."""
    data = {
        'today': (today or date.today()).isoformat(),
        'todos': [{'id': t.id, 'title': t.title, 'done': t.done, 'due': t.due}
                  for t in todos.todos],
        'pending': [{'id': p.id, 'title': p.title} for p in todos.pending],
        'filter': view.showing,  # the app owns the filter, so the agent can change it too
        'only': view.only_ids,
        'highlight': view.pointed_at,  # a control the agent pointed at: flashed once
        'highlight_n': view.pointed_n,
        'highlight_todo': view.pointed_todo,  # for a control on each todo: just this todo's, or every one
        'can_undo': bool(todos.undo_stack), 'can_redo': bool(todos.redo_stack),
    }
    # Registered on every run, as Streamlit's own examples do: the registry belongs to the
    # running app, and a registration made at import time is missed by a second app (AppTest).
    # The files are read each run too, so an edit to them shows on the next rerun.
    todo_list = component('todo_list', css=(HERE / 'todo_view.css').read_text(),
                          js=(HERE / 'todo_view.js').read_text())
    result = todo_list(key=key, data=data, on_action_change=lambda: None)
    return result.get('action') if result else None


def apply(todos: TodoList, view: View, action):
    """Carry out one action from the screen, as the person. Raises ActionError when it is refused."""
    op, todo_id = action.get('op'), action.get('id')
    title, due = action.get('title', ''), action.get('due')
    calls = {
        'add': ('todos.add', {'todos': [{'title': title, 'due': due}]}),
        'complete': ('todos.complete', {'ids': [todo_id]}),
        'reopen': ('todos.reopen', {'ids': [todo_id]}),
        'delete': ('todos.delete', {'ids': [todo_id]}),
        'rename': ('todos.rename', {'todos': [{'id': todo_id, 'title': title}]}),
        # The shared action takes a date string; the screen clears a date with an empty one.
        'set_due': ('todos.set_due', {'todos': [{'id': todo_id, 'due': due or None}]}),
        'move': ('todos.move', {'id': todo_id, 'before_id': None, 'after_id': action.get('below')}),  # dropped below = after
        'filter': ('view.show', {'showing': action.get('filter'), 'ids': None}),
        'approve': ('todos.approve', {'id': todo_id}),
        'deny': ('todos.deny', {'id': todo_id}),
        'toggle_all': ('todos.toggle_all', {}),
        'clear_completed': ('todos.clear_completed', {}),
        'undo': ('todos.undo', {}),
        'redo': ('todos.redo', {}),
    }
    if op not in calls:
        raise ValueError(f'Unknown action from the screen: {action!r}')
    action_id, args = calls[op]
    with todos.transaction():
        before = todos.state()
        result = execute(REGISTRY, action_id, args, actor='person', ctx=SimpleNamespace(todos=todos, view=view))
        if op not in ('undo', 'redo'):  # the change and its undo entry commit together
            todos.checkpoint('person', before)
        return result
