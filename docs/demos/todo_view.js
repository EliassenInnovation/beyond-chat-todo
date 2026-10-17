// The todo list, drawn in the page by todo_view.py (a Streamlit v2 component).
// It only reports what the person did, as one `action` trigger; Python calls
// TodoList for it and redraws. No todo logic lives here.

const SKELETON = `
<section class="todoapp">
  <h1>todos</h1>
  <div class="card">
    <header class="new">
      <button class="toggle-all" type="button" aria-label="Mark all as complete">
        <svg width="18" height="12" viewBox="0 0 22 14" fill="none" aria-hidden="true"><path d="M2 2l9 9 9-9" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </button>
      <label class="sr" for="new-todo">New todo</label>
      <input id="new-todo" class="new-todo" placeholder="What needs to be done?" autocomplete="off">
      <label class="sr" for="new-due">Due date (optional)</label>
      <input id="new-due" class="new-due" type="date" title="Due date (optional)">
    </header>
    <div class="custom-note" hidden></div>
    <ul class="list"></ul>
    <p class="empty">Nothing yet. Add one here or ask the assistant.</p>
    <footer class="footer">
      <span class="count"></span>
      <nav class="filters" aria-label="Filter todos">
        <button type="button" data-filter="all">All</button>
        <button type="button" data-filter="active">Active</button>
        <button type="button" data-filter="completed">Completed</button>
      </nav>
      <span class="clear-wrap"><button type="button" class="clear">Clear completed</button></span>
    </footer>
    <div class="history"><button type="button" class="undo">Undo</button><button type="button" class="redo">Redo</button></div>
  </div>
  <div class="pending"></div>
  <p class="hint">Click a todo or its date to change it · drag to reorder</p>
</section>`;

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function el(tag, attrs, children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === 'text') node.textContent = v;
    else if (k.startsWith('on')) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  for (const child of children || []) node.append(child);
  return node;
}

// The screen reports the todo a moved one lands below (null: the top); the app moves it after that one.
function belowFor(order, id, targetId, after) {
  const rest = order.filter((x) => x !== id);
  if (after) return targetId;
  const i = rest.indexOf(targetId);
  return i > 0 ? rest[i - 1] : null;
}

function build(root) {
  const holder = el('div', { class: 'todo-root' });
  holder.innerHTML = SKELETON;
  root.append(holder);
  const q = (s) => holder.querySelector(s);
  const ui = {
    filter: 'all', dragId: null, focusGrip: null, editing: null,
    title: q('.new-todo'), due: q('.new-due'), list: q('.list'), empty: q('.empty'),
    footer: q('.footer'), count: q('.count'), clear: q('.clear'), undo: q('.undo'), redo: q('.redo'), history: q('.history'), pending: q('.pending'),
    toggleAll: q('.toggle-all'), filters: [...holder.querySelectorAll('[data-filter]')],
  };
  holder.ui = ui;
  ui.root = holder;
  ui.title.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter' || !ui.title.value.trim()) return;
    ui.send({ op: 'add', title: ui.title.value.trim(), due: ui.due.value || null });
    ui.title.value = '';
    ui.due.value = '';
  });
  ui.toggleAll.addEventListener('click', () => ui.send({ op: 'toggle_all' }));
  ui.clear.addEventListener('click', () => ui.send({ op: 'clear_completed' }));
  ui.undo.addEventListener('click', () => ui.send({ op: 'undo' }));
  ui.redo.addEventListener('click', () => ui.send({ op: 'redo' }));
  for (const b of ui.filters) {
    // Shown at once, then reported: the app owns the filter, so the agent can change it too.
    b.addEventListener('click', () => { ui.filter = b.dataset.filter; render(ui); ui.send({ op: 'filter', filter: ui.filter }); });
  }
  return ui;
}

function startEdit(ui, id, field) {
  ui.editing = { id, field };
  render(ui);
}

// Click a title or a date to change it: Enter or leaving the field saves, Escape cancels.
// A title goes to the rename action, a date to set_due (empty clears it).
function editor(ui, todo, field) {
  const isTitle = field === 'title';
  const input = el('input', {
    class: isTitle ? 'edit-title' : 'edit-due', type: isTitle ? 'text' : 'date',
    'aria-label': isTitle ? `New text for ${todo.title}` : `Due date for ${todo.title} (empty for none)`,
  });
  input.value = isTitle ? todo.title : (todo.due || '');
  let done = false;
  const finish = (save) => {
    if (done) return;
    done = true;
    ui.editing = null;
    const value = input.value.trim();
    if (save && isTitle && value && value !== todo.title) ui.send({ op: 'rename', id: todo.id, title: value });
    else if (save && !isTitle && (value || null) !== (todo.due || null)) ui.send({ op: 'set_due', id: todo.id, due: value || null });
    else render(ui);
  };
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') finish(true);
    if (e.key === 'Escape') finish(false);
  });
  // Leaving the field saves; a field that disappeared because the list was redrawn does not.
  input.addEventListener('blur', () => setTimeout(() => { if (input.isConnected) finish(true); }, 0));
  ui.focusEdit = input;
  return input;
}

function row(ui, todo, order) {
  const today = ui.data.today;
  const overdue = todo.due && !todo.done && todo.due < today;
  const [, m, d] = (todo.due || '--').split('-');
  const grip = el('button', {
    type: 'button', class: 'grip', 'data-id': todo.id,
    'aria-label': `Move ${todo.title} (drag, or Up and Down arrow keys)`,
    onkeydown: (e) => {
      const i = order.indexOf(todo.id);
      let below;
      if (e.key === 'ArrowUp' && i > 0) below = i >= 2 ? order[i - 2] : null;
      else if (e.key === 'ArrowDown' && i < order.length - 1) below = order[i + 1];
      else return;
      e.preventDefault();
      ui.focusGrip = todo.id;
      ui.send({ op: 'move', id: todo.id, below });
    },
  });
  grip.innerHTML = '<svg width="9" height="14" viewBox="0 0 10 16" fill="currentColor" aria-hidden="true"><circle cx="2" cy="2" r="1.5"/><circle cx="8" cy="2" r="1.5"/><circle cx="2" cy="8" r="1.5"/><circle cx="8" cy="8" r="1.5"/><circle cx="2" cy="14" r="1.5"/><circle cx="8" cy="14" r="1.5"/></svg>';

  const toggle = el('button', {
    type: 'button', class: 'toggle', 'aria-pressed': String(todo.done),
    'aria-label': todo.done ? `Mark ${todo.title} as not done` : `Mark ${todo.title} as done`,
    onclick: () => ui.send({ op: todo.done ? 'reopen' : 'complete', id: todo.id }),
  });
  toggle.innerHTML = '<span class="ring"><svg width="13" height="10" viewBox="0 0 16 12" fill="none" aria-hidden="true"><path d="M1.5 6.5l4 4 9-9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>';

  const editing = ui.editing && ui.editing.id === todo.id ? ui.editing.field : null;
  const label = todo.due ? `${MONTHS[Number(m) - 1]} ${Number(d)}` : '';
  const text = editing === 'title'
    ? editor(ui, todo, 'title')
    : el('button', {
      type: 'button', class: 'title', text: todo.title, 'aria-label': `Change ${todo.title}`,
      onclick: () => startEdit(ui, todo.id, 'title'),
    });
  const due = editing === 'due'
    ? editor(ui, todo, 'due')
    : el('button', {
      type: 'button', class: `due${todo.due ? '' : ' none'}${overdue ? ' overdue' : ''}`,
      text: label || 'add date',
      'aria-label': todo.due ? `Due ${label}; change the date of ${todo.title}` : `Add a due date to ${todo.title}`,
      onclick: () => startEdit(ui, todo.id, 'due'),
    });
  const destroy = el('button', {
    type: 'button', class: 'destroy', 'aria-label': `Delete ${todo.title}`,
    onclick: () => ui.send({ op: 'delete', id: todo.id }),
  });
  destroy.innerHTML = '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true"><path d="M1 1l10 10M11 1L1 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>';

  const li = el('li', { class: todo.done ? 'todo done' : 'todo', 'data-id': todo.id, draggable: editing ? 'false' : 'true' },
    [toggle, el('div', { class: 'text' }, [text]), due, grip, destroy]);
  const after = (e) => e.clientY > li.getBoundingClientRect().top + li.offsetHeight / 2;
  li.addEventListener('dragstart', (e) => {
    ui.dragId = todo.id;
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', String(todo.id));
    li.classList.add('dragging');
  });
  li.addEventListener('dragover', (e) => {
    if (ui.dragId == null || ui.dragId === todo.id) return;
    e.preventDefault();
    li.classList.toggle('drop-after', after(e));
    li.classList.toggle('drop-before', !after(e));
  });
  li.addEventListener('dragleave', () => li.classList.remove('drop-before', 'drop-after'));
  li.addEventListener('drop', (e) => {
    e.preventDefault();
    li.classList.remove('drop-before', 'drop-after');
    const id = ui.dragId;
    ui.dragId = null;
    if (id == null || id === todo.id) return;
    const below = belowFor(order, id, todo.id, after(e));
    const current = order.indexOf(id) > 0 ? order[order.indexOf(id) - 1] : null;
    if (below !== current) ui.send({ op: 'move', id, below });
  });
  li.addEventListener('dragend', () => { ui.dragId = null; li.classList.remove('dragging'); });
  return li;
}

function render(ui) {
  const { todos, pending } = ui.data;
  const order = todos.map((t) => t.id);
  const left = todos.filter((t) => !t.done).length;
  const only = ui.data.only || [];
  const shown = todos.filter((t) => ui.filter === 'all' || (ui.filter === 'only' ? only.includes(t.id)
    : ui.filter === 'active' ? !t.done : t.done));
  const note = ui.root.querySelector('.custom-note');  // a chosen set: say so, and offer the way back
  note.hidden = ui.filter !== 'only';
  if (ui.filter === 'only') {
    note.replaceChildren(`Showing ${shown.length} of ${todos.length} ·`, el('button', { type: 'button', class: 'show-all',
      text: 'Show all', onclick: () => { ui.filter = 'all'; render(ui); ui.send({ op: 'filter', filter: 'all' }); } }));
  }

  ui.list.replaceChildren(...shown.map((t) => row(ui, t, order)));
  ui.empty.hidden = todos.length > 0;
  ui.footer.hidden = todos.length === 0;
  ui.toggleAll.classList.toggle('all-done', todos.length > 0 && left === 0);
  ui.toggleAll.setAttribute('aria-label', left === 0 ? 'Mark all as not done' : 'Mark all as done');
  ui.count.replaceChildren(el('strong', { text: String(left) }), ` ${left === 1 ? 'item' : 'items'} left`);
  ui.clear.hidden = !todos.some((t) => t.done);
  ui.undo.hidden = !ui.data.can_undo;
  ui.redo.hidden = !ui.data.can_redo;
  ui.history.hidden = !ui.data.can_undo && !ui.data.can_redo;
  for (const b of ui.filters) {
    b.classList.toggle('selected', b.dataset.filter === ui.filter);
    b.setAttribute('aria-pressed', String(b.dataset.filter === ui.filter));
  }

  ui.pending.replaceChildren(...pending.map((p) => el('div', { class: 'request', role: 'group', 'aria-label': 'Delete request' }, [
    el('span', {}, ['The assistant asks to delete ', el('strong', { text: p.title }), '. A delete can\u2019t be undone.']),
    el('button', { type: 'button', class: 'deny', text: 'Deny', onclick: () => ui.send({ op: 'deny', id: p.id }) }),
    el('button', { type: 'button', class: 'approve', text: 'Approve', onclick: () => ui.send({ op: 'approve', id: p.id }) }),
  ])));

  if (ui.focusEdit && ui.focusEdit.isConnected) {
    ui.focusEdit.focus();
    if (ui.focusEdit.type === 'text') ui.focusEdit.select();
  }
  ui.focusEdit = null;
  if (ui.focusGrip != null) {
    const grip = ui.list.querySelector(`.grip[data-id="${ui.focusGrip}"]`);
    if (grip) { grip.focus(); ui.focusGrip = null; }
  }
}

// The assistant points at a control: flash it for a few seconds. The ids are view.py's SCREEN.
const CONTROLS = {
  'new-todo': '.new-todo', 'toggle-all': '.toggle-all', checkbox: '.list .toggle', 'todo-text': '.list .title',
  'due-date': '.list .due', grip: '.list .grip', delete: '.list .destroy', 'filter-all': '[data-filter="all"]',
  'filter-active': '[data-filter="active"]', 'filter-completed': '[data-filter="completed"]', 'show-all': '.show-all',
  'clear-completed': '.clear', undo: '.history', 'approve-card': '.pending .request',
};
function flash(ui, root) {
  const { highlight, highlight_n: n, highlight_todo: id } = ui.data;
  if (!highlight || ui.flashed === n) return;
  ui.flashed = n;
  const selector = CONTROLS[highlight] || '_none_';  // one todo's: its row, then the control in it
  const found = [...root.querySelectorAll(id != null && selector.startsWith('.list ')
    ? `.list .todo[data-id="${id}"] ${selector.slice(6)}` : selector)];
  found.forEach((node) => node.classList.add('flash'));
  setTimeout(() => found.forEach((node) => node.classList.remove('flash')), 4000);
}

export default function (component) {
  const { data, parentElement, setTriggerValue } = component;
  // The screen's state lives on its own DOM node, not in this module: Streamlit may load this
  // module again for the same element, and a second build would draw the list twice.
  const existing = parentElement.querySelector('.todo-root');
  const ui = existing && existing.ui ? existing.ui : build(parentElement);
  ui.send = (action) => setTriggerValue('action', action);
  ui.data = data || { todos: [], pending: [], today: '', filter: 'all' };
  ui.filter = ui.data.filter || 'all';
  render(ui);
  flash(ui, parentElement);
}
