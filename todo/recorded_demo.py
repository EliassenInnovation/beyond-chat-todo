"""Display a recorded persona session without constructing a model client."""
from pathlib import Path
import json
import re

ASSETS = Path(__file__).resolve().parents[1] / 'docs' / 'demos'


def replay_html():
    """Bundle the same browser replay for Streamlit's isolated component iframe."""
    record = json.loads((ASSETS / 'sam-recording.json').read_text())
    script = (ASSETS / 'persona-replay.js').read_text()
    payload = json.dumps(record, ensure_ascii=False).replace('<', '\\u003c')
    script = script.replace("const response=await fetch('sam-recording.json');if(!response.ok)throw Error('Recording could not be loaded.');const record=await response.json();", f'const record={payload};')
    renderer = (ASSETS / 'todo_view.js').read_text().replace('export default function (component)', 'function renderTodos(component)')
    script = script.replace("import renderTodos from './todo_view.js';", renderer)
    css_payload = json.dumps((ASSETS / 'todo_view.css').read_text())
    script = script.replace("const styleResponse=await fetch('todo_view.css');if(!styleResponse.ok)throw Error('App styling could not be loaded.');const todoCss=await styleResponse.text();", f'const todoCss={css_payload};')
    script = script.replace('export function ', 'function ')
    page = (ASSETS / 'persona-replay.html').read_text().replace('data-guide-mode="true"', 'data-guide-mode="false"')
    page = re.sub(r'<script type="module" src="persona-replay\.js(?:\?[^"]*)?"></script>', lambda _: '<script type="module">' + script + '</script>', page)
    page = page.replace('<script src="../javascripts/demo-return.js?v=1"></script>', '')
    return page
