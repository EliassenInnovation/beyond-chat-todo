"""The application: a todo list saved to a JSON file. No AI and no Langfuse here.

Two callers use it: the person, through app.py, and the agent, through agent.py.
Both run the actions declared at the bottom of this file, through capabilities.execute.
They share every operation, and each action says who may call it. A person deletes
directly; from the agent, the same delete is only a *request*, which waits here until a
person approves or denies it. That rule lives in this code, so no prompt or model can get
around it.
"""

import json
import os
import tempfile
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

from todo.capabilities import REGISTRY, ActionError, Guard

# Storage belongs to this application; the reusable registry knows no todo fields.
REGISTRY.transaction = lambda ctx: ctx.todos.transaction()


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False
    due: str | None = None  # YYYY-MM-DD


@dataclass
class PendingDelete:
    id: int
    todo_id: int
    title: str


class TodoError(ActionError):
    """A request the list cannot carry out. The message says what would work instead."""


def _due(value):
    if value in (None, ''):
        return None
    try:
        return date.fromisoformat(value).isoformat()
    except (TypeError, ValueError):
        raise TodoError(f'Due dates are YYYY-MM-DD; got {value!r}.') from None


class TodoList:
    """One list, one copy in memory. The agent's freshness check (agent.py) compares against
    this object, so every caller must share it; two copies of the same file would not see
    each other's changes."""

    def __init__(self, path):
        self.path = Path(path)
        saved = json.loads(self.path.read_text()) if self.path.exists() else {}
        self.todos = [Todo(**t) for t in saved.get('todos', [])]
        self.pending = [PendingDelete(**p) for p in saved.get('pending', [])]
        # Ids are never reused, so "todo 2" in an old chat or trace always means the same todo.
        self.next_ids = saved.get('next_ids', {'todo': 1, 'pending': 1})
        # One undo stack for everyone (Bob, 2026-10-07): each entry is one click in the app or one
        # request to the agent, however many changes it made, with the list as it was before it.
        self.undo_stack = saved.get('undo', [])
        self.redo_stack = saved.get('redo', [])
        self.approval_targets = saved.get('approval_targets', {})
        self._transaction_depth = 0
        self.undo_stopped_by = saved.get('undo_stopped_by')  # the todo whose delete emptied the stack

    @contextmanager
    def transaction(self):
        """Commit a registered action once; restore memory if validation or saving fails.

        This is single-process demo storage, not concurrent database isolation. Nested
        actions share the outer transaction. No intermediate batch state reaches disk.
        """
        if self._transaction_depth:
            yield
            return
        before = deepcopy(self.__dict__)
        self._transaction_depth = 1
        try:
            yield
            self._transaction_depth = 0
            if self.__dict__ != before:
                self.save()
        except BaseException:
            self.__dict__.clear()
            self.__dict__.update(before)
            raise

    def save(self):
        if self._transaction_depth:
            return
        data = json.dumps({'todos': [asdict(t) for t in self.todos],
                           'pending': [asdict(p) for p in self.pending],
                           'next_ids': self.next_ids, 'approval_targets': self.approval_targets,
                           'undo': self.undo_stack, 'redo': self.redo_stack,
                           'undo_stopped_by': self.undo_stopped_by}, indent=2)
        # Replace only after a complete file has been written. A failed write or replace
        # leaves the last saved file intact. The temp file is on the same filesystem.
        name = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                             dir=self.path.parent, delete=False) as out:
                name = out.name
                out.write(data)
                out.flush()
                os.fsync(out.fileno())
            os.replace(name, self.path)
        finally:
            if name and os.path.exists(name):
                os.unlink(name)

    # --- Undo: one stack, the person's clicks and the agent's requests -------

    def state(self):
        """The list and its delete requests, as a value an undo can put back."""
        return {'todos': [asdict(t) for t in self.todos], 'pending': [asdict(p) for p in self.pending],
                'approval_targets': deepcopy(self.approval_targets)}

    def checkpoint(self, by, before):
        """Put what one click or one request changed on the undo stack, given the list before it.
        A deleted todo cannot come back, so a change that deleted one clears the stack: undoing
        anything older would bring back a list that no longer exists."""
        if before == self.state():
            return
        gone = [t['title'] for t in before['todos'] if t['id'] not in {t.id for t in self.todos}]
        if gone:
            self.undo_stack, self.undo_stopped_by = [], gone[0]
        else:
            self.undo_stack.append({'by': by, 'before': before})
        self.redo_stack = []
        self.save()

    def undo(self):
        """Put back the list as it was before the last entry; returns what that changed, in words."""
        # Said, not left to puzzle over: after a delete the Undo button is gone and undo finds nothing.
        stopped = (f' since “{self.undo_stopped_by}” was deleted: a deleted todo cannot come back'
                   if self.undo_stopped_by else '')
        return self._step(self.undo_stack, self.redo_stack, f'Nothing to undo{stopped}.')

    def redo(self):
        return self._step(self.redo_stack, self.undo_stack, 'Nothing to redo.')

    def _step(self, take, give, empty):
        if not take:
            raise TodoError(empty)
        entry = take.pop()
        was = self.snapshot()
        give.append({'by': entry['by'], 'before': self.state()})
        self.todos = [Todo(**t) for t in entry['before']['todos']]
        self.pending = [PendingDelete(**p) for p in entry['before']['pending']]
        self.approval_targets = deepcopy(entry['before'].get('approval_targets', {}))
        self.save()
        return entry['by'], undo_receipt(was, self.snapshot())

    def _new_id(self, kind):
        self.next_ids[kind] += 1
        return self.next_ids[kind] - 1

    def snapshot(self):
        """{id: (title, done, due, waiting for approval, position)}: enough to tell whether anything changed."""
        waiting = {p.todo_id for p in self.pending}
        return {t.id: (t.title, t.done, t.due, t.id in waiting, n + 1) for n, t in enumerate(self.todos)}

    def get(self, todo_id):
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        raise TodoError(f'No todo with id {todo_id}. Existing ids: {[t.id for t in self.todos]}.')

    # --- Shared by the person and the agent --------------------------------

    def add(self, title, due=None):
        if not title or not title.strip():
            raise TodoError('A todo needs a title.')
        todo = Todo(id=self._new_id('todo'), title=title.strip(), due=_due(due))
        self.todos.append(todo)
        self.save()
        return todo

    def complete(self, todo_id):
        todo = self.get(todo_id)
        todo.done = True
        self.save()
        return todo

    def set_due(self, todo_id, due):
        todo = self.get(todo_id)
        todo.due = _due(due)
        self.save()
        return todo

    def move(self, todo_id, after_id=None, before_id=None):
        """Put a todo directly after one todo, or directly before one; neither puts it first.
        The list reads top to bottom, so before is above and after is below."""
        todo = self.get(todo_id)
        if todo_id in (after_id, before_id):
            raise TodoError('A todo cannot move next to itself.')
        after = self.get(after_id) if after_id is not None else None
        before = self.get(before_id) if before_id is not None else None
        rest = [t for t in self.todos if t is not todo]
        if after and before and rest.index(before) != rest.index(after) + 1:
            # Both is fine when they name one spot ("between the cake and the invitations").
            raise TodoError(f'{after.title!r} and {before.title!r} are not next to each other; give one of them.')
        self.todos.remove(todo)
        at = self.todos.index(after) + 1 if after else self.todos.index(before) if before else 0
        self.todos.insert(at, todo)
        self.save()
        return todo

    def reopen(self, todo_id):
        todo = self.get(todo_id)
        todo.done = False
        self.save()
        return todo

    def rename(self, todo_id, title):
        """Change a todo's text. A pending delete keeps the original proposal for approval."""
        if not title or not title.strip():
            raise TodoError('A todo needs a title.')
        todo = self.get(todo_id)
        todo.title = title.strip()
        self.save()
        return todo

    # --- The agent's side of deleting: ask, and wait -----------------------

    def request_delete(self, todo_id):
        todo = self.get(todo_id)
        for pending in self.pending:
            if pending.todo_id == todo_id:
                return pending
        pending = PendingDelete(id=self._new_id('pending'), todo_id=todo.id, title=todo.title)
        self.pending.append(pending)
        self.approval_targets[str(pending.id)] = asdict(todo)
        self.save()
        return pending

    # --- The person's side: only the app calls these -----------------------

    def delete(self, todo_id):
        todo = self.get(todo_id)
        self.todos.remove(todo)
        removed = [p for p in self.pending if p.todo_id == todo_id]
        self.pending = [p for p in self.pending if p.todo_id != todo_id]
        for pending in removed:
            self.approval_targets.pop(str(pending.id), None)
        self.save()
        return todo

    def approve(self, pending_id):
        pending = self._pending(pending_id)
        if self.approval_targets.get(str(pending.id)) != asdict(self.get(pending.todo_id)):
            raise TodoError('This todo changed since the delete was requested, or the request has no saved '
                            'approval details. Deny this request and ask for a new one before approving.')
        return self.delete(pending.todo_id)

    def deny(self, pending_id):
        pending = self._pending(pending_id)
        self.pending.remove(pending)
        self.approval_targets.pop(str(pending.id), None)
        self.save()
        return pending

    def _pending(self, pending_id):
        for pending in self.pending:
            if pending.id == pending_id:
                return pending
        raise TodoError(f'No pending delete {pending_id}.')


# --- The actions: what callers may do with the list, and who may ---------
# Each declaration sits on its handler. `description` is what a model reads when it chooses a
# tool, so every word of it was measured by the evals. A result says what is now true.
# The model is offered these tools in registration order; the order is measured too (agent.py).
# Every action here touches todos the caller names, and every write but delete can be taken back by another
# action (undone_by). So delete is the one the agent must ask for; the bulk actions are the person's.

ID = {'id': {'type': 'integer'}}
# A list lets one call change several todos, and the model then read words that fit two todos as both
# (which-to-delete 3/5, which-to-tick 4/5). The list's own description says whom it is for.
# Found in use: asked "how do I merge two items?" and then "can you do it for me?", the agent merged
# the bouncy castles, which the user never named. Merging is a job people ask for again and again, so
# it is a tool of its own (merge_todos, below), with a guard of its own (Bob, 2026-10-07): before a
# merge, a second model answers one question from the conversation's words alone. It never sees the
# list, so two todos that look alike cannot tempt it into a guess. The question names the problem,
# not its absence (see capabilities.Guard), and quotes no example request, so it cannot echo a case.
# Measured on 12 labelled merge conversations: 11/12, the same on a second pass. Wordings that said
# "only refers to merging", or "the user's own words", refused "merge the bouncy castles for me" after
# a how-to answer (0.68-1.00); "only refers to an action" does not (0.22). Its miss: "merge the castle
# one with something" names one todo and passes (0.16).
MERGE_UNNAMED = REGISTRY.guard(Guard(
    'todos.merge_unnamed',
    question=('Is the user asking the assistant to merge todos into one without saying which todos to merge? '
              'Answer yes when the request only refers to an action, such as asking the assistant to carry out what it '
              'just explained, and names no todos, or only one; a todo the assistant mentioned only as an example '
              'does not count as named. Answer no when the user names the todos; describes them by what they have '
              'in common; refers back to todos already being discussed; agrees to todos the assistant proposed; or '
              'is not asking to merge.'),
    refusal=('Not merged: the user has not said which todos to merge. Change nothing; ask which, and you may suggest '
             'the ones that look alike.')))

# These checks run by default. The input check never sees
# the proposed action. Output checks share one request; both requests run concurrently.
TARGET_IDENTIFIED = REGISTRY.guard(Guard(
    'todos.target_identified', 'Is it clear which task or group of tasks the user means?',
    'This action was not applied: ask which task or tasks the user means before trying again.',
    inputs=('conversation', 'state', 'current_date'), reason='Resolve references against the current list without a proposed selection.',
    provider='chat', require_yes=True))
OUTPUT_GUARDS = tuple(REGISTRY.guard(Guard(
    name, question, refusal,
    inputs=('conversation', 'state', 'current_date', 'action', 'calendar', 'tool_meanings'),
    reason='Compare the proposed operation and arguments with the request and current tasks.', provider='chat', require_yes=(name == 'todos.operation_matches'))).name
    for name, question, refusal in (
        ('todos.extra_tasks', 'Does the proposed action include any tasks outside the user’s intended selection?',
         'This action was not applied: this action includes tasks the user did not ask to change. Correct the selection.'),
        ('todos.omitted_tasks', 'Does the user ask for this same operation on any tasks missing from the proposed action?',
         'This action was not applied: this action omits requested tasks. Include all tasks requested for this operation.'),
        ('todos.operation_matches', 'Is this operation one of the task changes the user intends?',
         'This action was not applied: this operation does not match the request. Choose the requested operation.'),
        ('todos.wrong_values', 'Does the proposed change use any values that conflict with what the user requested?',
         'This action was not applied: the proposed values conflict with the request. Correct the arguments.')))
TARGET_GUARDS = (TARGET_IDENTIFIED.name, *OUTPUT_GUARDS)
# Only due-date changes carry new values; completion/deletion select tasks, not dates.
TASK_GUARDS = tuple(g for g in TARGET_GUARDS if g != 'todos.wrong_values')


PICKED = ("the todos the user's words pick out: one, or several when they name several. Words that could "
          'mean any one of several todos pick out none of them: ask which one instead.')
IDS = {'ids': {'type': 'array', 'items': {'type': 'integer'}, 'description': PICKED}}
DATE = {'type': 'string', 'description': 'YYYY-MM-DD'}
OPTIONAL_DATE = {'type': ['string', 'null'], 'description': 'YYYY-MM-DD, or null for no due date'}
# Facts are written once, on the actions they are about: the agent reads them in the tool
# descriptions, and the evals' checks rest on the same truths.
DATE_FACTS = ('A due date shows next to the todo on the list, and nothing more: the app cannot contact the user in '
              'any way (no reminders, messages or alerts), and nothing happens on the date. When a request depends '
              'on hearing from the app later, set the date and say plainly that the app will not contact them.',)
PERSON_ONLY = dict(surfaces=('ui',), policy={'person': 'allow', 'agent': 'forbidden'})


@REGISTRY.action('todos.list', tool='list_todos', effects=('read',), params={},
                 description='List every todo with its id, title, done flag, and due date, plus any deletes '
                             'waiting for the user to approve. The list also comes with each message; use this '
                             'to read it again during a turn.')
def list_todos(ctx):
    return {'todos': [vars(t) for t in ctx.todos.todos],
            'waiting_for_approval': [vars(p) for p in ctx.todos.pending],
            'screen_shows': ctx.view.showing,
            'visible_todo_ids': [t.id for t in ctx.view.visible(ctx.todos)]}


# Adding takes one todo or several ("add eggs, bread and butter"), like ticking: one request, one
# sentence about all of it in the app's words, and all of it or none.
NEW_TODO = {'type': 'object', 'properties': {'title': {'type': 'string'}, 'due': OPTIONAL_DATE},
            'required': ['title', 'due'], 'additionalProperties': False}


@REGISTRY.action('todos.add', tool='add_todo', effects=('write',), undone_by='todos.delete',
                 facts=DATE_FACTS,
                 params={'todos': {'type': 'array', 'items': NEW_TODO, 'description': 'one new todo, or several'}},
                 description='Add new todos, each optionally with a due date: one, or several in one call. Write each '
                             'title as it should read on the list, starting with a capital letter.')
def add_todo(ctx, todos):
    if not todos:
        raise TodoError('Name at least one todo to add.')
    for new in todos:  # every one is checked before any is added
        if not new['title'].strip():
            raise TodoError('A todo needs a title.')
        _due(new['due'])
    added = [ctx.todos.add(new['title'], new['due']) for new in todos]
    return {'todos': [vars(t) for t in added], 'receipt': add_receipt(added), 'note': SAY_RECEIPT}


def spoken_date(due):
    """2026-09-28 -> Monday, September 28: the weekday comes from the date, never from a model."""
    day = date.fromisoformat(due)
    return f'{day:%A}, {day:%B} {day.day}'


def add_receipt(added):
    """The sentence the assistant says about what it added, written by the app (see move_receipt)."""
    dues = {t.due for t in added}
    if len(dues) == 1:  # all on one date, or none dated: "Added “Eggs,” “Bread” and “Butter.”"
        due = dues.pop()
        return finish(f'Added {titles([t.title for t in added])}' + (f' due {spoken_date(due)}' if due else ''))
    # Dates have commas of their own, so every part ends with one: “Pay rent” due Friday, October 9, and ...
    parts = [f'“{t.title}”' + (f' due {spoken_date(t.due)}' if t.due else '') for t in added]
    comma = lambda part: part[:-1] + ',”' if part.endswith('”') else part + ','
    listed = [comma(p) if len(parts) > 2 or t.due else p for p, t in zip(parts[:-1], added)]
    return finish('Added ' + ' '.join(listed) + ' and ' + parts[-1])


def finish(sentence):
    """End a sentence, with the period inside a closing quote: “Buy bread.”"""
    return sentence[:-1] + '.”' if sentence.endswith('”') else sentence + '.'


# Changes to an existing todo need an up-to-date read first. The prompt asks for that too,
# but a prompt can only ask: when the person changed the list in the app, the model trusted
# its memory of the list anyway (read-fresh failed 3/3). Code requires it instead: an agent's
# call to an action with needs_current_read is refused, with what changed, until it has read.
# Ticking takes one todo or several ("I did all the grocery shopping"), so the reply can carry one
# sentence about all of them in the app's words. Its impact is still 'one': the agent names every
# todo it ticks, as it would in one call per todo, and each tick can be taken back. The 'many' rule
# is for actions that reach todos nobody named (tick all, clear completed): those stay the person's.
@REGISTRY.action('todos.complete', tool='complete_todo', effects=('write',), params=IDS, needs_current_read=True,
                 undone_by='todos.reopen', guards=TASK_GUARDS,
                 guard_description='Mark tasks completed. Keep them in the list.',
                 description='Mark todos done: one, or several in one call. Use it when the user says they did the '
                             'thing, e.g. "I swept the chimney".')
def complete_todo(ctx, ids):
    return tick(ctx, ids, done=True)


@REGISTRY.action('todos.reopen', tool='reopen_todo', effects=('write',), params=IDS, needs_current_read=True,
                 undone_by='todos.complete',
                 description='Mark done todos as not done again: one, or several in one call. Use it when the user '
                             'says something they ticked off is not finished after all, e.g. "turns out I never sent '
                             'that form".')
def reopen_todo(ctx, ids):
    return tick(ctx, ids, done=False)


def tick(ctx, ids, done):
    """Tick or untick every todo named, or none: an id that is not on the list refuses the whole call."""
    ids = list(dict.fromkeys(ids))  # once each, in the order given
    if not ids:
        raise TodoError('Name at least one todo.')
    todos = [ctx.todos.get(i) for i in ids]
    already = [t.title for t in todos if t.done == done]
    changed = [t.title for t in todos if t.done != done]
    for i in ids:
        (ctx.todos.complete if done else ctx.todos.reopen)(i)
    return {'todos': [vars(ctx.todos.get(i)) for i in ids],
            'receipt': tick_receipt(changed, already, done), 'note': SAY_RECEIPT}


def titles(names):
    """“Buy milk,” “Buy eggs” and “Buy bread”: a list of titles in quotes, for a sentence."""
    quoted = [f'“{n},”' if i < len(names) - 2 else f'“{n}”' for i, n in enumerate(names)]
    return ' and '.join([' '.join(quoted[:-1]), quoted[-1]]) if len(quoted) > 1 else quoted[0]


def tick_receipt(changed, already, done):
    """The sentence the assistant says about ticks or unticks, written by the app in the assistant's
    voice (see move_receipt), so the reply cannot say "marked as not done" after ticking, or name a
    todo it did not tick."""
    state = 'done' if done else 'not done'
    said = [f'Marked {titles(changed)} {state}'] if changed else []
    if already:
        said.append(f'{titles(already)} {"was" if len(already) == 1 else "were"} already {state}')
    return '; '.join(said) + '.'


DATED = {'type': 'object', 'properties': {**ID, 'due': OPTIONAL_DATE}, 'required': ['id', 'due'],
         'additionalProperties': False}


@REGISTRY.action('todos.set_due', tool='set_due_date', effects=('write',),
                 params={'todos': {'type': 'array', 'items': DATED, 'description': PICKED}},
                 needs_current_read=True, undone_by='todos.set_due', guards=TARGET_GUARDS,
                 guard_description='Set, change or clear the due date of tasks. A null due value removes the date.',
                 facts=DATE_FACTS,
                 description="Set, change or clear due dates (null clears one): one todo, or several in one call. If "
                             "the user's words fit more than one todo, ask which one instead of calling this.")
def set_due_date(ctx, todos):
    if not todos:
        raise TodoError('Name at least one todo.')
    for change in todos:  # every one is checked before any changes
        ctx.todos.get(change['id'])
        _due(change['due'])
    before = {c['id']: ctx.todos.get(c['id']).due for c in todos}
    changed = [ctx.todos.set_due(c['id'], c['due']) for c in todos]
    return {'todos': [vars(t) for t in changed],
            'receipt': due_receipt([(t, before[t.id] == t.due) for t in changed]), 'note': SAY_RECEIPT}


def due_receipt(changes):
    """The sentence the assistant says about due dates, written by the app (see move_receipt). Todos given
    the same date share a clause: "“Pay rent” and “Call mom” are now due Friday, October 9."""
    groups = {}  # (due, already) -> titles, in the order given
    for todo, already in changes:
        groups.setdefault((todo.due, already), []).append(todo.title)
    said = []
    for (due, already), names in groups.items():
        one = len(names) == 1
        if due is None:
            said.append(f'{titles(names)} {"had" if already else "has" if one else "have"} no due date'
                        + ('' if already else ' now'))
        else:
            verb = ('was' if one else 'were') + ' already' if already else ('is' if one else 'are') + ' now'
            said.append(f'{titles(names)} {verb} due {spoken_date(due)}')
    return '; '.join(said) + '.'


@REGISTRY.action('todos.move', tool='move_todo', effects=('write',), needs_current_read=True, undone_by='todos.move',
                 params={**ID, 'before_id': {'type': ['integer', 'null'], 'description': 'the todo it comes directly before'},
                         'after_id': {'type': ['integer', 'null'], 'description': 'the todo it comes directly after'}},
                 description='Move a todo so it comes directly before another one (before_id) or directly after another '
                             'one (after_id); give one of them, or neither to put it first.')
def move_todo(ctx, id, before_id, after_id):
    # Where it came from, in the result: asked to put it back, the agent reads its old place instead of
    # rebuilding it from memory ("back there, please" put it one place too high, 0/10).
    todos = ctx.todos.todos
    i = [t.id for t in todos].index(ctx.todos.get(id).id)
    above = todos[i - 1] if i > 0 else None
    below_of = todos[i + 1] if i + 1 < len(todos) else None
    # Above and below, the screen's words: "after" read both ways (the todo after it, or it after the todo).
    was = {'position': i + 1, 'directly_below': above.title if above else None,
           'directly_above': below_of.title if below_of else None}
    back = ({'id': id, 'after_id': above.id, 'before_id': None, 'meaning': f'directly below "{above.title}"'} if above
            else {'id': id, 'after_id': None, 'before_id': None, 'meaning': 'first on the list'})
    earlier = getattr(ctx.todos, 'place_before_move', {}).get(id, 'none')  # the todo above it before its last move
    moved = ctx.todos.move(id, after_id=after_id, before_id=before_id)
    now = ctx.todos.todos
    j = [t.id for t in now].index(id)
    place = (now[j - 1].id if j > 0 else None)
    ctx.todos.place_before_move = {**getattr(ctx.todos, 'place_before_move', {}), id: (above.id if above else None)}
    return {**vars(moved), 'order': [t.title for t in now], 'was': was, 'to_put_it_back': back,
            'receipt': move_receipt(moved.title, j, now, unchanged=(j == i), back=(earlier != 'none' and place == earlier), came_from=i),
            'note': SAY_RECEIPT}


SAY_RECEIPT = 'The application displays this receipt directly. Do not repeat it; add only useful explanation or unanswered parts of the request.'
ORDINALS = ('first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth')


def move_receipt(title, j, todos, unchanged=False, back=False, came_from=None):
    """The sentence the assistant says about a move, written by the app in the assistant's voice, so
    the reply cannot misstate where the todo went ("third" when it was second, "back" when it was not)."""
    if j == 0:
        where = 'the top'
    elif j == len(todos) - 1:
        where = f'the bottom, below “{todos[j - 1].title}.”'
    else:
        where = f'{ORDINALS[j] if j < len(ORDINALS) else f"number {j + 1}"}, below “{todos[j - 1].title}.”'
    if unchanged:  # "already at the top." / "already at the bottom, below ..." / "already third, below ..."
        return f'“{title}” is already {"at " if where.startswith("the ") else ""}{where}' + ('.' if j == 0 else '')
    origin = '' if came_from is None or back else f', from {"the top" if came_from == 0 else ORDINALS[came_from] if came_from < len(ORDINALS) else f"number {came_from + 1}"}'
    if j == 0:
        return f'Moved “{title}” {"back " if back else ""}to the top{origin}.'
    return f'Moved “{title}” {"back " if back else ""}{origin.lstrip(", ") + " " if origin else ""}to {where}'.replace('from ', 'from ', 1)


def request_delete(ctx, ids):
    """What a delete from the agent does instead: ask, and wait for the person."""
    ids = named(ctx, ids)
    asked_before = {p.todo_id for p in ctx.todos.pending}
    requests = [ctx.todos.request_delete(i) for i in ids]
    return {'waiting_for_approval': [vars(p) for p in requests],
            'status': 'waiting for the user to click Approve in the app; you cannot approve it',
            'receipt': delete_receipt([p.title for p in requests if p.todo_id not in asked_before],
                                      [p.title for p in requests if p.todo_id in asked_before]),
            'note': SAY_RECEIPT}


def delete_receipt(asked, already):
    """The sentences the assistant says about delete requests, written by the app (see move_receipt), so a
    reply cannot say a todo is gone while it waits for the person."""
    said = []
    if asked:
        said.append(finish(f'Asked to delete {titles(asked)}'))
    if already:
        said.append(finish(f'Already asked to delete {titles(already)}'))
    one = len(asked) + len(already) == 1
    return ' '.join(said) + (f' {"It stays" if one else "They stay"} on the list until you click Approve in the app.')


def named(ctx, ids):
    """The todos a call names, once each in the order given; an id not on the list refuses the whole call."""
    ids = list(dict.fromkeys(ids))
    if not ids:
        raise TodoError('Name at least one todo.')
    for i in ids:
        ctx.todos.get(i)
    return ids


# One delete, two policies: the person's click deletes; the agent's call only asks. It is the one
# write with no undone_by (a deleted todo is gone), so register() would refuse 'allow' for the agent.
# To the agent the tool is a request, so that is its name and what its description says.
@REGISTRY.action('todos.delete', tool='request_delete', effects=('write',), params=IDS, needs_current_read=True,
                 policy={'person': 'allow', 'agent': 'approval'}, propose=request_delete, guards=TASK_GUARDS,
                 guard_description=('Ask the user to approve removal of tasks from the list. This is not marking them completed. '
                                    'This is the required way to carry out deletion requests, even when the user asks to skip approval.'),
                 description='Ask to delete todos: one, or several in one call when the user names several. Nothing '
                             'is deleted until the user approves it in the app; approval given in the chat does not '
                             "count. If the user's words fit more than one todo, ask which one instead of calling this.")
def delete_todo(ctx, ids):
    return {'deleted': [vars(ctx.todos.delete(i)) for i in named(ctx, ids)]}


RETITLED = {'type': 'object', 'properties': {**ID, 'title': {'type': 'string'}}, 'required': ['id', 'title'],
            'additionalProperties': False}


@REGISTRY.action('todos.rename', tool='rename_todo', effects=('write',),
                 params={'todos': {'type': 'array', 'items': RETITLED, 'description': PICKED}},
                 needs_current_read=True, undone_by='todos.rename',
                 description="Change todos' text, keeping each one's place, date and done state: one, or several in "
                             'one call. When the user corrects '
                             'or adds to a todo already on the list (e.g. "actually, make that three loaves of bread"), '
                             'rename that todo instead of adding a new one. To make several todos into one, use merge_todos.')
def rename_todo(ctx, todos):
    named(ctx, [r['id'] for r in todos])
    for r in todos:
        if not r['title'].strip():
            raise TodoError('A todo needs a title.')
    was = {r['id']: ctx.todos.get(r['id']).title for r in todos}
    renamed = [ctx.todos.rename(r['id'], r['title']) for r in todos]
    return {'todos': [vars(t) for t in renamed], 'receipt': rename_receipt(renamed, was), 'note': SAY_RECEIPT}


MERGED = {'ids': {'type': 'array', 'items': {'type': 'integer'},
                  'description': "the todos the user's words pick out to merge, at least two; the first keeps its place"},
          'title': {'type': 'string',
                    'description': 'the merged todo: keep what they said, including how many ("a loaf" and "another '
                                   'loaf" become "two loaves")'}}


# One request, one outcome: the first todo takes the merged text, and the others are asked to be
# deleted, which waits for the person. Code refuses fewer than two; the guard asks whether the user
# said which. The one-request undo takes all of it back.
@REGISTRY.action('todos.merge', tool='merge_todos', effects=('write',), params=MERGED, needs_current_read=True,
                 undone_by='todos.undo', guards=('todos.merge_unnamed',),
                 description='Merge todos into one: the first keeps its place, date and done state and gets the merged '
                             'text; the others are asked to be deleted, which waits for the user to approve in the app. '
                             'Only todos the user has named, at least two; if they have not said which, ask.')
def merge_todos(ctx, ids, title):
    ids = named(ctx, ids)
    if len(ids) < 2:
        raise TodoError('A merge needs at least two todos. Ask the user which todos to merge.')
    if not title.strip():
        raise TodoError('A todo needs a title.')
    was = [ctx.todos.get(i).title for i in ids]
    kept = ctx.todos.rename(ids[0], title)
    asked_before = {p.todo_id for p in ctx.todos.pending}
    requests = [ctx.todos.request_delete(i) for i in ids[1:]]
    receipt = finish(f'Merged {titles(was)} into “{kept.title}”') + ' ' + delete_receipt(
        [p.title for p in requests if p.todo_id not in asked_before], [p.title for p in requests if p.todo_id in asked_before])
    return {'merged': vars(kept), 'waiting_for_approval': [vars(p) for p in requests], 'receipt': receipt,
            'note': SAY_RECEIPT}


def rename_receipt(renamed, was):
    """The sentence the assistant says about a rename, written by the app (see move_receipt). One rename
    leaves the old text out: with "Renamed “Get a bouncy castle” to ..." in the conversation, the agent
    later renamed it back to "Get a bouncy castle" (one-todo-for-both 7/10; without the old text, 10/10).
    Several in one call name each old text, so the reply says which became which."""
    said = []
    for t in renamed:
        if was[t.id] == t.title:
            said.append(finish(f'“{t.title}” already says that'))
        else:
            said.append(finish(f'Renamed it to “{t.title}”' if len(renamed) == 1 else f'Renamed “{was[t.id]}” to “{t.title}”'))
    return ' '.join(said)


# Only a person can do these: approving the agent's request is the approval, so the agent
# is not offered them, and execute refuses them if it asks anyway.
@REGISTRY.action('todos.approve', effects=('write',), params=ID, **PERSON_ONLY,
                 description='Approve a delete the assistant asked for: the todo is deleted.')
def approve_delete(ctx, id):
    return vars(ctx.todos.approve(id))


@REGISTRY.action('todos.deny', effects=('write',), params=ID, **PERSON_ONLY,
                 description='Refuse a delete the assistant asked for: the todo stays.')
def deny_delete(ctx, id):
    return vars(ctx.todos.deny(id))


def undo_receipt(was, now):
    """What an undo or redo changed, written by the app (see rename_receipt), todo by todo."""
    said, reordered = [], False
    for i in sorted(set(was) | set(now)):
        if i not in now:
            said.append(f'removed “{was[i][0]}”')
            continue
        if i not in was:
            said.append(f'put “{now[i][0]}” back')
            continue
        (title, done, due, waiting, place), (title2, done2, due2, waiting2, place2) = was[i], now[i]
        if title2 != title:
            said.append(f'“{title}” says “{title2}” again')
        if done2 != done:
            said.append(f'“{title2}” is {"done" if done2 else "not done"} again')
        if due2 != due:
            said.append(f'“{title2}” is due {due2} again' if due2 else f'“{title2}” has no due date again')
        if waiting2 != waiting:
            said.append(f'withdrew the request to delete “{title2}”' if waiting else f'asked again to delete “{title2}”')
        reordered |= place2 != place
    if reordered:
        said.append('the order is as it was')
    return '; '.join(said)


# Undo takes back the last entry on the one stack, whoever made it, one step each time, from the
# button or the chat alike: least surprise (Bob, 2026-10-07). One step per request; saying it again
# goes further back. Redo takes an undo back, so each is the other's recovery.
@REGISTRY.action('todos.undo', tool='undo', effects=('write',), params={}, undone_by='todos.redo',
                 description="Undo the last change to the list, whoever made it: everything one request to you "
                             'changed, delete requests included, or one click in the app. One step per request; '
                             'asked again, it goes one step further back. A deleted todo cannot come back, so '
                             'nothing from before a delete can be undone.')
def undo(ctx):
    if getattr(ctx, 'undid', False):
        raise TodoError('One undo per request: the user can ask again, or click Undo under the list.')
    by, changed = ctx.todos.undo()
    ctx.undid = True
    return {'undid': by, 'receipt': finish(f'Undid that: {changed}' if by == 'agent' else
                                           f'Undid your last change in the app: {changed}'), 'note': SAY_RECEIPT}


@REGISTRY.action('todos.redo', tool='redo', effects=('write',), params={}, undone_by='todos.undo',
                 description='Put back the change the last undo took back ("put it back", "redo"). One step per '
                             'request. Only right after an undo: any new change ends what can be redone.')
def redo(ctx):
    if getattr(ctx, 'redid', False):
        raise TodoError('One redo per request: the user can ask again, or click Redo under the list.')
    by, changed = ctx.todos.redo()
    ctx.redid = True
    return {'redid': by, 'receipt': finish(f'Put it back: {changed}'), 'note': SAY_RECEIPT}


@REGISTRY.action('todos.toggle_all', effects=('write',), params={}, impact='many', undone_by='todos.toggle_all',
                 **PERSON_ONLY,
                 description='Mark every todo done, or every todo not done when all are done already.')
def toggle_all(ctx):
    # Like TodoMVC: finish everything, or reopen everything when all are done.
    todos = ctx.todos
    if any(not t.done for t in todos.todos):
        for t in [t for t in todos.todos if not t.done]:
            todos.complete(t.id)
    else:
        for t in list(todos.todos):
            todos.reopen(t.id)
    return {'todos': [vars(t) for t in todos.todos]}


@REGISTRY.action('todos.clear_completed', effects=('write',), params={}, impact='many', **PERSON_ONLY,
                 description='Delete every done todo.')
def clear_completed(ctx):
    return {'deleted': [vars(ctx.todos.delete(t.id)) for t in [t for t in ctx.todos.todos if t.done]]}
