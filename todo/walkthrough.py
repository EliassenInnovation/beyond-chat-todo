"""Run the shared actions on disposable data. Python standard library only; no model calls."""
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace

from todo.capabilities import REGISTRY, ActionError, execute
from todo.todos import TodoList
from todo.view import View


def run():
    with tempfile.TemporaryDirectory(prefix='todo-walkthrough-') as folder:
        ctx = SimpleNamespace(todos=TodoList(Path(folder) / 'todos.json'), view=View())
        def call(action, args, actor='agent'):
            before = ctx.todos.state()
            with ctx.todos.transaction():
                result = execute(REGISTRY, action, args, actor=actor, ctx=ctx)
                if action not in ('todos.undo', 'todos.redo'):
                    ctx.todos.checkpoint(actor, before)
            return result

        print('1. Shared action and a saved result')
        added = call('todos.add', {'todos': [{'title': 'Read the guide', 'due': None},
                                            {'title': 'Try the sample', 'due': None}]})
        print(added['receipt'])
        assert len(TodoList(ctx.todos.path).todos) == 2

        print('\n2. A screen change does not change saved tasks')
        before = ctx.todos.path.read_bytes()
        print(call('view.show', {'showing': 'only', 'ids': [1]}))
        assert ctx.todos.path.read_bytes() == before

        print('\n3. A requested deletion waits for the person')
        print(call('todos.delete', {'ids': [2]})['receipt'])
        pending_id = ctx.todos.pending[0].id
        try:
            call('todos.approve', {'id': pending_id})
        except ActionError as error:
            print('Agent refused:', error)
        else:
            raise AssertionError('The agent approved its own deletion')
        assert len(ctx.todos.todos) == 2
        call('todos.deny', {'id': pending_id}, actor='person')

        print('\n4. Invalid batch input changes nothing')
        before = ctx.todos.path.read_bytes()
        try:
            call('todos.complete', {'ids': [1, 999]})
        except ActionError as error:
            print('Batch refused:', error)
        else:
            raise AssertionError('Unknown task accepted')
        assert ctx.todos.path.read_bytes() == before

        print('\n5. Both callers share recovery')
        print(call('todos.complete', {'ids': [1]})['receipt'])
        print(call('todos.undo', {}, actor='person')['receipt'])
        assert not ctx.todos.get(1).done
        print('\nSaved state:', json.dumps(ctx.todos.state(), indent=2))
        print('\nAll walkthrough checks passed. Temporary data is removed on exit.')


if __name__ == '__main__':
    run()
