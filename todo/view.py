"""What the screen shows: presentation, not data.

The person's All / Active / Completed buttons and the agent's show_todos tool set the same
View, the way both change todos through the same TodoList. Nothing here changes a todo, so a
view change needs no approval and no fresh read. It is an action only an agent that shares
the person's screen should have (an external client could not see its effect).
"""

from todo.capabilities import REGISTRY
from todo.todos import TodoError

FILTERS = ('all', 'active', 'completed', 'only')  # 'only': a chosen set of todos (only_ids)

# The screen's language: every control, what it is called there, where it is, what it does.
# The agent is given this so it can tell the user how to do something, or point at it; the
# component (todo_view.js) maps each id to the element it highlights.
SCREEN = {
    'new-todo': ('"What needs to be done?"', 'the box at the top of the list', 'type a todo and press Enter; the date box beside it sets a due date'),
    'toggle-all': ('the down-arrow', 'left of the "What needs to be done?" box', 'marks every todo done, or all not done'),
    'checkbox': ('the round checkbox', 'left of each todo', 'ticks a todo done, or un-ticks it'),
    'todo-text': ("a todo's text", 'each row', 'click it to change the wording'),
    'due-date': ('the date', 'right side of each todo ("add date" when it has none)', 'click it to set, change or clear the due date'),
    'grip': ('the grip (six dots)', 'right side of each todo, on hover', 'drag it to reorder; or focus it and use the Up and Down keys'),
    'delete': ('the ×', 'far right of each todo, on hover', 'deletes that todo'),
    'filter-all': ('All', 'the buttons under the list', 'shows every todo'),
    'filter-active': ('Active', 'the buttons under the list', 'shows only the todos not done'),
    'filter-completed': ('Completed', 'the buttons under the list', 'shows only the done todos'),
    'show-all': ('Show all', 'the note above the list, when only some todos are shown', 'shows every todo again'),
    'clear-completed': ('Clear completed', 'under the list, on the right', 'deletes every done todo'),
    'undo': ('Undo / Redo', 'under the list, on the right, after a change', 'Undo takes back the last change, a click or a whole request to the assistant; click again to go further back'),
    'approve-card': ('Approve / Deny', 'the card under the list, when the assistant asks to delete', 'approves or refuses that delete'),
}
ON_EACH_TODO = ('checkbox', 'todo-text', 'due-date', 'grip', 'delete')  # one per row
FILTER_BUTTONS = ('filter-all', 'filter-active', 'filter-completed')


def not_on_screen(ctx, control, todo_id=None):
    """Why the page is not drawing this control now, or None when it is. This is the one place
    that decides it: the page draws each control from this answer (todo_view.screen_data), and
    point_at asks it during the agent's turn, before the page has drawn."""
    todos, view = ctx.todos, ctx.view
    if control in ON_EACH_TODO:
        visible = view.visible(todos)
        if todo_id is not None and all(t.id != todo_id for t in visible):
            return 'that todo is hidden by what the screen is showing'
        return None if visible else 'no todo is on the screen'
    if control in FILTER_BUTTONS and not todos.todos:
        return 'the filter buttons appear once the list has a todo'
    if control == 'clear-completed' and not any(t.done for t in todos.todos):
        return 'it appears when at least one todo is done'
    if control == 'show-all' and view.showing != 'only':
        return 'it appears when the screen shows only some chosen todos'
    if control == 'approve-card' and not todos.pending:
        return 'it appears when a delete request is waiting'
    if control == 'undo':
        request = getattr(ctx, 'request', None)  # this request's own changes get their Undo when it ends
        changed = request is not None and request['before'] != todos.state()
        if not (todos.undo_stack or todos.redo_stack or changed):
            return 'it appears after a change to the list'
    return None


class View:
    def __init__(self, showing='all'):
        self.showing = showing
        self.only_ids = []  # the chosen set, when showing 'only'
        self.pointed_at = None  # a control the agent highlighted this turn; the app shows it once
        self.pointed_n = 0      # counts pointings, so the same control can be flashed twice
        self.pointed_todo = None  # for a control on each todo: the one todo whose control it is

    def point(self, control, todo_id=None):
        if control not in SCREEN:
            raise TodoError(f'Unknown control {control!r}. The screen has: {", ".join(SCREEN)}.')
        if todo_id is not None and control not in ON_EACH_TODO:
            raise TodoError(f'{control} is not on each todo; only {", ".join(ON_EACH_TODO)} take a todo.')
        self.pointed_at, self.pointed_todo = control, todo_id
        self.pointed_n += 1
        return self

    def show(self, showing, ids=None):
        if showing not in FILTERS:
            raise TodoError(f'The screen can show {", ".join(FILTERS)}; got {showing!r}.')
        if showing == 'only' and not ids:
            raise TodoError("To show only some todos, give their ids.")
        self.showing = showing
        self.only_ids = list(ids) if showing == 'only' else []
        return self

    def visible(self, todos):
        """The todos on screen now, in order."""
        keep = {'all': lambda t: True, 'active': lambda t: not t.done, 'completed': lambda t: t.done,
                'only': lambda t: t.id in self.only_ids}[self.showing]
        return [t for t in todos.todos if keep(t)]


# --- The actions. The order a model is offered them in is the agent adapter's choice (agent.py).

@REGISTRY.action('view.show', tool='show_todos', effects=('presentation',),
                 params={'showing': {'type': 'string', 'enum': list(FILTERS)},
                         'ids': {'type': ['array', 'null'], 'items': {'type': 'integer'},
                                 'description': 'for only: the todos to show'}},
                 description="Change which todos the screen shows: all; the open ones (active: exactly the todos not "
                             "done); the done ones (completed: exactly the done ones); or only the ones you choose (only, "
                             "with their ids), for anything else, including several conditions at once. Only the view "
                             "changes; no todo does. The result lists what is visible and what is hidden: say only what "
                             "it shows.")
def shown(ctx, showing, ids):
    """Change the view; report what is on screen now, so a claim about it can be true."""
    for todo_id in ids or []:
        ctx.todos.get(todo_id)  # an unknown id is refused, naming the ones that exist
    ctx.view.show(showing, ids)
    visible = ctx.view.visible(ctx.todos)
    return {'screen_shows': showing, 'visible': [t.title for t in visible],
            'hidden': [t.title for t in ctx.todos.todos if t not in visible]}


# Only the agent points: the person can see the screen already.
@REGISTRY.action('view.point_at', tool='point_at', effects=('presentation',), surfaces=('embedded_agent',),
                 params={'control': {'type': 'string', 'enum': list(SCREEN)},
                         'todo_id': {'type': ['integer', 'null'],
                                     'description': "to highlight it on one todo only, that todo's id; otherwise null"}},
                 description="Highlight a control on the user's screen for a few seconds, so they can see where it is. "
                             'Changes nothing. Use it when the user asks to be shown how or where. A control that '
                             'is not on the screen now is refused, with what makes it appear.')
def point_at(ctx, control, todo_id=None):
    # Said in the result, where the reply is drafted: it had highlighted a control and then offered
    # "I can highlight it for you if you want".
    todo = ctx.todos.get(todo_id) if todo_id is not None else None
    # The reply is written before the page draws, so the answer about the screen is decided here.
    # It had said "it is highlighted now" for Clear completed when no todo was done and nothing lit.
    if control in SCREEN and (todo_id is None or control in ON_EACH_TODO):
        missing = not_on_screen(ctx, control, todo_id)
        if missing:
            raise TodoError(f'{SCREEN[control][0]} is not on the screen now: {missing}. Nothing is highlighted.')
    result = {'highlighted': ctx.view.point(control, todo_id).pointed_at,
              'note': "It is highlighted on the user's screen now; say so, rather than offering to."}
    # A control on each todo lights on every todo. It once said "the grip on Book the dentist" is
    # highlighted while every grip was; the result says what is lit, where the reply is drafted.
    # (Pointing at one todo's control was tried twice, as a todo_id and as its own tool; each broke
    # an unrelated case, 5/5 to 0/5 and 10/10 to 1/10, so it waits.)
    if control in ON_EACH_TODO:
        result['lit_on'] = f'the todo "{todo.title}" only' if todo else 'every todo'
    return result
