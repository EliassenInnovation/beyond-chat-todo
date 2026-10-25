"""Offline review of recorded sessions. Rendering never runs the application or models."""
import html
import json
import os
from pathlib import Path
import tempfile

from evaluations.eval_costs import estimate, rates_note


def save_record(path, record):
    """Replace atomically so an interrupted write cannot destroy the previous checkpoint."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as out:
            temporary = Path(out.name)
            json.dump(record, out, indent=2)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, path)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


def esc(value):
    return html.escape(str(value))


def state(value):
    if value is None:
        return '<p>State was not recorded.</p>'
    raw = '<pre>' + esc(json.dumps(value, indent=2, ensure_ascii=False)) + '</pre>'
    if not isinstance(value, dict) or 'todos' not in value:
        return raw
    rows = []
    for todo in value['todos']:
        label = 'Done' if todo.get('done') else 'Open'
        due = f" · due {esc(todo['due'])}" if todo.get('due') else ''
        rows.append(f"<li><b>{label}</b>: {esc(todo['title'])}{due}</li>")
    body = '<ol>' + ''.join(rows) + '</ol>' if rows else '<p>The list is empty.</p>'
    for pending in value.get('waiting_for_approval', []):
        body += f"<p>Waiting for approval: delete {esc(pending['title'])}.</p>"
    if 'visible' in value:
        body += '<p><b>Visible on screen:</b> ' + esc(', '.join(value['visible']) or 'No tasks') + '.</p>'
    return body + '<details><summary>Recorded state details</summary>' + raw + '</details>'


def render(record):
    # Older CLI records were a list of sessions; retain offline access to those too.
    sessions = record if isinstance(record, list) else record.get('sessions', [])
    usage = {} if isinstance(record, list) else record.get('usage', {})
    pieces = []
    for session in sessions:
        title = esc(session.get('persona', 'Incomplete session'))
        pieces.append(f'<section class="frame"><h2>{title}: starting point</h2>'
                      f'<p>{esc(session.get("who", ""))}</p><p>Goal: {esc(session.get("wants", ""))}</p>'
                      f'<p>Recorded outcome: {esc(session.get("status", "not recorded"))}. '
                      'Satisfaction is the persona’s assessment, not a verified pass.</p>'
                      + (f'<p>{esc(session["stop_reason"])}</p>' if session.get('stop_reason') else '')
                      + state(session.get('initial')) + '</section>')
        for turn in session.get('turns', []):
            persona = turn.get('persona', {})
            pieces.append(f'<section class="frame"><h2>{title}: turn {esc(turn["n"])}</h2>')
            if turn.get('clicked_ids'):
                pieces.append(f'<p><b>Person action:</b> {esc(persona.get("click"))} '
                              f'on pending IDs {esc(turn["clicked_ids"])}.</p>')
            pieces.append(f'<h3>Persona</h3><p class="words">{esc(turn.get("user") or "No message recorded.")}</p>')
            pieces.append(f'<h3>Assistant</h3><p class="words">{esc(turn.get("assistant") or "No assistant reply recorded.")}</p>')
            for key in ('error', 'persona_stopped', 'judge_error'):
                if turn.get(key):
                    pieces.append(f'<p><b>{esc(key)}:</b> {esc(turn[key])}</p>')
            pieces.append('<div class="states"><div><h3>Before person action</h3>'
                          + state(turn.get('before_click', turn.get('before')))
                          + '</div><div><h3>After turn</h3>' + state(turn.get('after')) + '</div></div>')
            pieces.append('<details><summary>Tool calls and judgment evidence</summary>' + state(turn) + '</details></section>')
        pieces.append(f'<section class="frame"><h2>{title}: candidate findings</h2>'
                      '<p>Review these against the conversation. They are not fixed-suite eval scores.</p>'
                      + state(session.get('findings', [])) + '<h3>Final recorded state</h3>'
                      + state(session.get('final')) + '</section>')
    body = ''.join(pieces) or '<p>No session was recorded.</p>'
    tokens = esc(usage.get('reported_tokens', 'not recorded'))
    cost = estimate(usage.get('calls'))
    cost_text = f"${cost['usd']:.4f}" if cost['usd'] is not None else 'unknown'
    complete = {True: 'yes', False: 'no'}.get(usage.get('complete'), 'not recorded')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Persona session review</title><style>
body{font:16px/1.5 system-ui,sans-serif;color:#182b3b;background:#f4f6f8;margin:0;padding:24px}
main{max-width:1100px;margin:auto}h1,h2,h3{line-height:1.2}section{background:white;padding:24px;border-radius:12px;margin:16px 0}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.5 monospace;background:#eef2f5;padding:14px;border-radius:6px}
.words{white-space:pre-wrap;overflow-wrap:anywhere}.states{display:grid;grid-template-columns:1fr 1fr;gap:20px}.states>div{min-width:0}
nav{position:sticky;top:0;background:#f4f6f8;padding:12px 0;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
button{padding:8px 16px;font:inherit;cursor:pointer}button:disabled{cursor:default}details{margin-top:16px}
@media(max-width:650px){body{padding:12px}section{padding:16px}.states{grid-template-columns:1fr}}
[hidden]{display:none!important}</style><main><h1>Persona session review</h1>
<p>Recorded conversation and application state. Reviewing this file makes no model calls and changes no tasks.
This is a transcript review, not a visual UI test or a new simulation.</p>
''' + f'<p>Reported tokens: {tokens}. Usage complete: {complete}. Estimated API cost: {cost_text}. {esc(rates_note())} Token allowances are checked between calls; they are not dollar billing caps.</p>' + '''
<nav aria-label="Review steps" hidden><button id="previous">Previous</button><span id="position" aria-live="polite"></span><button id="next">Next</button><button id="all">Show all</button></nav>
''' + body + '''</main><script>
const frames=[...document.querySelectorAll('.frame')];let index=0,all=false;
const previous=document.getElementById('previous'),next=document.getElementById('next'),toggle=document.getElementById('all');
function show(){frames.forEach((f,i)=>f.hidden=!all&&i!==index);previous.disabled=all||index===0;next.disabled=all||index===frames.length-1;
document.getElementById('position').textContent=all?`${frames.length} steps`:`Step ${index+1} of ${frames.length}`;toggle.textContent=all?'Step through':'Show all';}
previous.onclick=()=>{index--;show()};next.onclick=()=>{index++;show()};toggle.onclick=()=>{all=!all;show()};
if(frames.length){document.querySelector('nav').hidden=false;show()}
</script></html>'''


def write_report(path):
    path = Path(path)
    destination = path.with_suffix('.html')
    destination.write_text(render(json.loads(path.read_text())), encoding='utf-8')
    return destination
