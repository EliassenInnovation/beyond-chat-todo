"""The evals page: a run report turned into one page an engineer and a product person can read together.

    .venv/bin/python -m evaluations.evals_page                 # the latest run -> runs/evals.html
    .venv/bin/python -m evaluations.evals_page runs/X.json     # a particular run

Three levels, each answering a different question, and nothing open until it is clicked:
  1. the case     what it asks, in plain words, and how many attempts passed
  2. the attempt  a triangle, green or amber, and the reasons it failed; opening it shows
                  what happened, turn by turn: what was said, what the agent read and changed,
                  what it replied, each grader's verdict
  3. the trace    the user's sentence is the link to that attempt's Langfuse trace

The look is Advisor's evals page (~/bin/investments/tools/coach/langfuse_integration/
evals_page.py), adapted to local evidence completeness, cost estimates and comparable history.
Generated from the run report (evals.py writes it), never edited by hand. Static HTML, no
script: rows open in place with <details>.
"""

import evaluations.eval_monitor as eval_monitor
from evaluations.eval_costs import estimate

import json
import math
import sys
from json import JSONDecodeError
from html import escape
from pathlib import Path

import todo.view as view  # noqa: F401  registers the view's actions, and through its import, todos.py's
from todo.capabilities import REGISTRY

RUNS = Path(__file__).resolve().parents[1] / 'runs'

STYLE = """
:root { color-scheme: dark; --bg: #1c1c1e; --panel: #232326; --open: #202023; --text: #ececec; --muted: #a3a3a3;
        --faint: #8b8b8b; --rule: #353538; --pass: #5cb85f; --some: #e0aa4a; --broke: #e5735e; --link: #8ab4f8; }
* { box-sizing: border-box; }
body { margin: 0; padding-block: 36px 64px; padding-inline: 24px; background: var(--bg); color: var(--text);
       font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
       font-size: 18px; line-height: 1.5; text-align: left; }
header, main, footer { max-width: 1040px; margin: 0 auto; }
h1 { font-size: 30px; font-weight: 500; margin: 0 0 6px; letter-spacing: 0.01em; }
p { margin: 0; }
.num { font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, monospace; font-variant-numeric: tabular-nums; }
.pass { color: var(--pass); } .some { color: var(--some); } .broke { color: var(--broke); }
.muted { color: var(--muted); } .faint { color: var(--faint); }
.label { font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }
a { color: var(--link); text-decoration: none; border-bottom: 1px solid #2f4a70; }
header { display: flex; justify-content: space-between; align-items: flex-start; gap: 24px; flex-wrap: wrap; }
header .intro { max-width: 64ch; color: var(--muted); font-size: 16px; }
header .when { text-align: right; color: var(--muted); font-size: 15px; white-space: nowrap; }
header .when .num { display: block; font-size: 14px; color: var(--faint); margin-top: 2px; }
.band { margin-top: 28px; background: var(--panel); border-radius: 10px; padding: 22px 24px; }
.band .cells { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.band .big { font-size: 40px; line-height: 1.1; margin-top: 4px; }
.band .big small { font-size: 20px; color: var(--muted); }
.band { overflow-wrap: anywhere; }
.band h2 { font-size: 20px; margin: 6px 0 10px; }
.band p { font-size: 15px; margin: 8px 0; }
.band svg { width: 100%; height: auto; }
.band table { width: 100%; border-collapse: collapse; font-size: 14px; }
.band th, .band td { padding: 8px; border-bottom: 1px solid var(--rule); overflow-wrap: anywhere; }
.band .under { font-size: 15px; color: var(--muted); margin-top: 4px; }
.cols, details.row > summary { display: grid; grid-template-columns: 1fr 150px 190px 110px; gap: 16px; align-items: start; }
.cols { padding: 8px 12px; border-bottom: 1px solid var(--rule); margin-top: 36px; }
details.row { border-bottom: 1px solid var(--rule); }
details.row > summary { padding: 14px 12px; cursor: pointer; list-style: none; }
details.row > summary::-webkit-details-marker { display: none; }
details.row > summary:hover { background: #202023; }
.case .question { font-size: 18px; font-weight: 500; line-height: 1.4; }
.case .id { font-size: 13px; color: var(--faint); margin-top: 3px; }
.origin { display: inline-block; font-size: 11px; text-transform: uppercase; letter-spacing: .06em;
          border-radius: 4px; padding: 0 5px; margin-left: 8px; border: 1px solid var(--rule); color: var(--faint); }
.origin.found { color: var(--some); border-color: var(--some); } .origin.held { color: var(--link); border-color: #2f4a70; }
.judged { font-size: 15px; color: var(--muted); padding-top: 3px; }
.result .verdict { font-size: 18px; font-weight: 500; }
.result .detail { font-size: 14px; color: var(--muted); margin-top: 2px; }
.toggle { color: var(--link); font-size: 15px; padding-top: 3px; text-align: right; white-space: nowrap; }
.toggle::after { content: ' \\25B8'; color: var(--faint); }
details[open].row > summary .toggle::after { content: ' \\25BE'; }
.panel { background: var(--open); border-radius: 8px; margin: 0 12px 14px; padding: 14px 16px 12px; }
.panel .label { display: block; margin-bottom: 6px; }
.panel .label.amber { color: var(--some); } .panel .label.green { color: var(--pass); }
.panel .rule { border-top: 1px solid var(--rule); margin: 10px 0 12px; }
details.conv > summary { display: grid; grid-template-columns: 14px 1fr auto; gap: 0 12px; align-items: start;
  padding: 6px 0; cursor: pointer; list-style: none; }
details.conv > summary::-webkit-details-marker { display: none; }
details.conv > summary:focus-visible { outline: 1px solid var(--some); outline-offset: 2px; }
.conv .tri { font-size: 15px; line-height: 1; margin-top: 4px; transition: transform .12s; }
.conv .tri::before { content: '\\25B6'; }
.conv .tri.passed { color: var(--pass); } .conv .tri.failed { color: var(--some); } .conv .tri.broke { color: var(--broke); }
details.conv[open] > summary .tri { transform: rotate(90deg); }
@media (prefers-reduced-motion: reduce) { .conv .tri { transition: none; } }
.conv .ask { font-size: 15px; line-height: 1.45; }
/* The user's own sentence is the link to the trace: the target is the row the eye is on. */
.conv .ask a { color: inherit; border-bottom: 1px dotted var(--faint); }
.conv .ask a::after { content: ' \\2197'; color: var(--faint); font-size: 13px; }
.conv .ask a:hover { border-bottom-color: var(--text); }
.conv .ask .none { color: var(--faint); font-size: 13px; margin-left: 6px; }
.conv .reasons { font-size: 14px; color: var(--some); margin-top: 2px; line-height: 1.4; }
.conv .reasons.broke { color: var(--broke); }
.conv .id { font-size: 12px; color: var(--faint); padding-top: 5px; }
.outline { margin: 0 0 8px 26px; font-size: 14px; }
.outline .turn { margin: 8px 0 0 4px; padding-left: 12px; border-left: 2px solid var(--rule); }
.outline .turn.bad { border-left-color: var(--some); }
.outline .said { color: var(--text); }
.outline ul { list-style: none; margin: 4px 0 0; padding: 0; }
.outline li { margin: 2px 0; color: var(--muted); line-height: 1.45; }
.outline li.bad { color: var(--some); } .outline li.answer { color: var(--text); }
.outline .k { display: inline-block; min-width: 64px; font-size: 12px; text-transform: uppercase;
              letter-spacing: 0.05em; color: var(--faint); }
.outline .grade { margin: 10px 0 0 4px; }
/* Each step opens in place to show what it sent and what came back. */
.outline details.step > summary { cursor: pointer; list-style: none; }
.outline details.step > summary::-webkit-details-marker { display: none; }
.outline details.step > summary::after { content: ' \\25B8'; color: var(--faint); font-size: 11px; }
.outline details.step[open] > summary::after { content: ' \\25BE'; }
.outline .more { margin: 4px 0 6px 68px; }
.outline .more .lbl { font-size: 11px; text-transform: uppercase; letter-spacing: .06em; color: var(--faint);
  margin-top: 4px; }
.outline .more pre { margin: 2px 0 0; padding: 8px 10px; background: var(--panel); border-radius: 6px;
  font-size: 12px; line-height: 1.4; color: var(--muted); white-space: pre-wrap; word-break: break-word;
  max-height: 320px; overflow: auto; }
footer { border-top: 1px solid var(--rule); margin-top: 48px; padding-top: 14px; color: var(--faint); font-size: 13px; }
@media (max-width: 820px) {
  body { padding-inline: 16px; font-size: 17px; }
  .band .cells { grid-template-columns: 1fr; }
  .cols { display: none; }
  details.row > summary { grid-template-columns: 1fr; gap: 6px; }
  .toggle { text-align: left; }
}
"""


def e(text):
    return escape(str(text))


def wilson(passed, n, z=1.96):
    """The 95% Wilson interval for a pass rate, as (low, high) fractions. With few attempts it is wide:
    5 of 5 is consistent with a true rate near 57%, 10 of 10 with one near 72%, so one case's before
    and after is a direction, not proof."""
    if not n:
        return 0.0, 1.0
    p = passed / n
    centre, half = p + z * z / (2 * n), z * (p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5
    return (centre - half) / (1 + z * z / n), (centre + half) / (1 + z * z / n)


def interval(passed, n):
    """'57–100%': the 95% range of the true pass rate, for showing beside a count."""
    low, high = wilson(passed, n)
    return f'{round(low * 100)}–{round(high * 100)}%'


def outcome(attempt):
    return eval_monitor.attempt_outcome(attempt)


def good(attempt):
    return outcome(attempt) == 'passed'


def reasons(attempt, expects):
    """Why an attempt failed, in plain words; empty when it passed."""
    out = []
    if attempt['error']:
        out.append(f'crashed: {attempt["error"]}')
    elif attempt['passed'] is None:
        out.append('not graded: a judge it rests on could not answer')
    elif not attempt['passed']:
        out.append(attempt.get('clarification_reason') if attempt.get('clarification_passed') is False and attempt.get('clarification_reason')
                   else f'outcome not as expected; expected {expects}')
    if attempt['truthful'] is None or attempt.get('answered') is None:
        out.append('inconclusive: required judgments unavailable')
    if attempt['truthful'] is False:
        quote = f': “{attempt["judge_quote"]}”' if attempt['judge_quote'] else ''
        out.append(f'a truthfulness or receipt check failed{quote}')
    if attempt.get('answered') is False:
        quote = f': “{attempt["answered_quote"]}”' if attempt.get('answered_quote') else ''
        out.append(f'a part of a message got no response{quote}')
    return out


def pretty(value):
    """JSON shown readably: one line per todo, not one line per field. Arguments arrive as a
    string, results as data."""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except JSONDecodeError:
            return value
    one = lambda v: json.dumps(v, ensure_ascii=False)
    if isinstance(value, dict) and any(isinstance(v, list) for v in value.values()):
        lines = []
        for key, v in value.items():
            if isinstance(v, list):
                lines.append(f'{key}:' + ('' if v else ' none'))
                lines += [f'  {one(item)}' for item in v]
            else:
                lines.append(f'{key}: {one(v)}')
        return '\n'.join(lines)
    return one(value)


def opens(summary, blocks, cls=''):
    """A step that opens in place to its blocks; a plain line when there is nothing to show."""
    blocks = [(label, text) for label, text in blocks if text not in (None, '', '{}')]
    if not blocks:
        return f'<li class="{cls}">{summary}</li>'
    more = ''.join(f'<div class="lbl">{e(label)}</div><pre>{e(text)}</pre>' for label, text in blocks)
    return f'<li class="{cls}"><details class="step"><summary>{summary}</summary><div class="more">{more}</div></details></li>'


def kind(tool):
    """What a call did, from what its action declares. A tool no longer registered (request_delete,
    in runs from before the registry) was a change."""
    action = REGISTRY.by_tool(tool)
    effects = action.effects if action else ('write',)
    return 'change' if 'write' in effects else 'view' if 'presentation' in effects else 'read'


def step(call):
    if call.get('given'):
        return opens('<span class="k">given</span> the current list, with the message',
                     [('the list', pretty(call['result']) if 'result' in call else None)])
    sent = pretty(call['args']) if call['args'] not in ('{}', '', None) else None
    checks = [('guard checks', pretty(call['guard_checks']))] if call.get('guard_checks') else []
    if 'error' in call:
        return opens(f'<span class="k">refused</span> {e(call["tool"])}: {e(call["error"])}',
                     [('sent', sent), ('came back', call['error'])] + checks, 'bad')
    return opens(f'<span class="k">{kind(call["tool"])}</span> {e(call["tool"])}',
                 [('sent', sent), ('came back', pretty(call['result']) if 'result' in call else None)] + checks)


def outline(attempt, expects):
    """What happened, turn by turn, then the saved list and both graders."""
    rows, number = [], 0
    for turn in attempt['conversation']:
        if 'app' in turn:
            rows.append(f'<div class="turn"><div class="said faint">In the app · {e(turn["app"])}</div></div>')
            continue
        number += 1
        calls = turn.get('tools', [])
        steps = ''.join(step(c) for c in calls) or '<li class="faint"><span class="k">tools</span> none</li>'
        answer = turn.get('assistant', '(no reply: the turn crashed)')
        bad = any('error' in c for c in calls) or 'assistant' not in turn
        rows.append(f'<div class="turn{" bad" if bad else ""}"><div class="said">Turn {number} · “{e(turn["user"])}”</div>'
                    f'<ul>{steps}<li class="answer"><span class="k">answer</span> {e(answer)}</li></ul></div>')
    after = attempt['after'] or {}
    waiting = {p['todo_id'] for p in after.get('waiting_for_approval', [])}
    saved = ''.join(f'<li>{"&#9745;" if t["done"] else "&#9744;"} {e(t["title"])}'
                    f'{" (due " + e(t["due"]) + ")" if t["due"] else ""}'
                    f'{" · waiting for your approval to delete" if t["id"] in waiting else ""}</li>'
                    for t in after.get('todos', [])) or '<li>(empty)</li>'
    if after.get('screen_shows', 'all') != 'all':
        saved += f'<li class="faint">the screen shows only {e(after["screen_shows"])} todos</li>'
    if attempt['truthful'] is None:
        judge = '<li class="faint"><span class="k">judge</span> unavailable</li>'
    else:
        verdict = 'truthfulness and receipt checks passed' if attempt['truthful'] else 'a truthfulness or receipt check failed'
        judge = opens(f'<span class="k">judge</span> {verdict}',
                      [('asked', 'Does any reply say a change happened that the saved list does not show?'),
                       ('answered', 'no' if attempt['truthful'] else 'yes'), ('quoted', attempt['judge_quote'])],
                      '' if attempt['truthful'] else 'bad')
    if attempt.get('answered') is not None:  # runs before this judge existed have no answer
        judge += opens(f'<span class="k">judge</span> {"every part of each message got a response" if attempt["answered"] else "a part of a message got no response"}',
                       [('asked', 'Does a reply leave any request or question in the message without a response?'),
                        ('answered', 'no' if attempt['answered'] else 'yes'), ('quoted', attempt.get('answered_quote'))],
                       '' if attempt['answered'] else 'bad')
    code = opens(f'<span class="k">code</span> outcome {"as expected" if attempt["passed"] else "not as expected"}',
                 [('expected', expects), ('saved', pretty(after))], '' if attempt['passed'] else 'bad')
    rows.append(f'<div class="turn{"" if attempt["passed"] else " bad"}"><div class="said">Saved list afterwards</div>'
                f'<ul>{saved}</ul></div><ul class="grade">{code}{judge}</ul>')
    if attempt.get('checks'):
        checks = ''.join(f'<li>{e(name)}: {"passed" if check["passed"] else "failed"}'
                         f'{": " + e(check["reason"]) if check.get("reason") else ""}</li>'
                         for name, check in attempt['checks'].items())
        missing = ''.join(f'<li>{e(name)}: unavailable</li>' for name in attempt.get('ungraded', []))
        rows.append(f'<details><summary>Individual checks and reasons</summary><ul>{checks}{missing}</ul></details>')
    return f'<div class="outline">{"".join(rows)}</div>'


def conversation(attempt, expects):
    dot = 'broke' if attempt['error'] else 'passed' if good(attempt) else 'failed'
    first = next((t['user'] for t in attempt['conversation'] if 'user' in t), '')
    # The first sentence opens the trace, so the click lands on the row the eye is on.
    ask = (f'<a href="{e(attempt["trace_url"])}" target="_blank" rel="noopener">{e(first)}</a>' if attempt['trace_url']
           else f'{e(first)}<span class="none">no trace</span>')
    why = reasons(attempt, expects)
    if attempt.get('harness_stop'):
        why.append('Measurement stopped: ' + attempt['harness_stop'])
    why_html = f'<div class="reasons{" broke" if attempt["error"] else ""}">{e(" · ".join(why))}</div>' if why else ''
    cost = attempt.get('_cost_estimate', {})
    cost_text = f"${cost['usd']:.4f}" if cost.get('usd') is not None else 'unknown'
    seconds = attempt.get('duration_seconds')
    timing = f'{seconds:.2f} seconds' if isinstance(seconds, (float, int)) else 'not recorded'
    measurement = f'<p class="detail">Estimated model cost, including judges: {cost_text}. Application execution: {e(timing)} (excludes grading).</p>'
    return (f'<details class="conv"><summary><span class="tri {dot}" aria-hidden="true"></span>'
            f'<div><div class="ask">{ask}</div>{why_html}</div>'
            f'<span class="id num">attempt {attempt["attempt"]}</span></summary>{measurement}{outline(attempt, expects)}</details>\n')


def origin_tag(case):
    """Where the case came from: the makers' intent, a user's intent the makers missed, or held out."""
    origin = case.get('origin')
    if origin in ('found in use', 'found by a persona'):
        return f'<span class="origin found">{e(origin)}</span>'
    if origin == 'held out':
        return f'<span class="origin held">held out · of {e(case.get("held_out_of") or "")}</span>'
    return '<span class="origin">makers\' intent</span>' if origin else ''


def row(case, attempts, repeat):
    ok = [a for a in attempts if good(a)]
    tone = 'pass' if len(ok) == repeat else 'broke' if any(outcome(a) == 'failed' for a in attempts) else 'some'
    flagged = sum(a['truthful'] is False or a.get('answered') is False for a in attempts)
    detail = ', '.join(x for x in [f'{flagged} repl{"y" if flagged == 1 else "ies"} flagged' if flagged else '',
                                   f'{sum(outcome(a) == "inconclusive" for a in attempts)} inconclusive' if any(outcome(a) == 'inconclusive' for a in attempts) else '',
                                   f'{repeat - len(attempts)} missing' if len(attempts) < repeat else ''] if x)
    panel = ['<div class="panel">', f'<p><strong>Expected outcome:</strong> {e(case["expects"])}</p>']
    for status, label, color in [('failed', 'Failed', 'amber'),
                                  ('inconclusive', 'Inconclusive', 'amber'),
                                  ('passed', 'Passed', 'green')]:
        group = [a for a in attempts if outcome(a) == status]
        if group:
            panel.append(f'<div class="rule"></div><span class="label {color}">{label} &middot; {len(group)}</span>')
            panel += [conversation(a, case['expects']) for a in group]
    missing = repeat - len(attempts)
    if missing:
        panel.append(f'<p class="some">{missing} planned attempts have no result. Investigate the runner.</p>')
    panel.append('</div>')
    turns = sum('user' in t for t in (attempts[0]['conversation'] if attempts else []))
    return (f'<details class="row"><summary>'
            f'<div class="case"><div class="question">{e(case["asks"])}</div>'
            f'<div class="id num">{e(case["name"])}{origin_tag(case)}</div></div>'
            f'<div class="judged">code + judge<br><span class="faint">{turns} turn{"s" if turns != 1 else ""}</span></div>'
            f'<div class="result"><div class="verdict {tone}">{len(ok)} of {repeat} passed</div>'
            f'<div class="detail faint">Confirmed passes / planned attempts</div>'
            + (f'<div class="detail">{e(detail)}</div>' if detail else '') +
            f'</div><div class="toggle">{repeat} attempts</div></summary>\n{"".join(panel)}</details>\n')


def monitor_panel(record, history, baseline, policy):
    counts = eval_monitor.counts(record)
    stability = eval_monitor.stability(record, baseline, history)
    if record.get('rejudged'):
        stability = {'status': 'not_comparable', 'message': 'Rejudged replies are not new application runs. Original control limits do not apply.'}
    acceptance = eval_monitor.acceptance(record, policy)
    cost = estimate(record.get('generations'))
    dollars = f"${cost['usd']:.4f}" if cost['usd'] is not None else 'Unknown'
    complete = 'Complete' if counts['complete'] else 'Incomplete'
    usage_text = (f"{cost['input_tokens']:,} reported input tokens; {cost['output_tokens']:,} output tokens."
                  if record.get('generations') else 'Token usage was not recorded.')
    key = eval_monitor.comparison_key(record)
    comparison_notice = ('Rejudged record: excluded from comparisons.' if record.get('rejudged') else
                         'Comparison metadata is missing or inconsistent.' if not key else '')
    comparable = [r for r in history if r['started'] <= record['started'] and key is not None
                  and eval_monitor.comparison_key(r) == key]
    if key is not None and not any(r['run'] == record['run'] for r in comparable):
        comparable.append(record)
    comparable.sort(key=lambda r: r['started'])
    history_rows = ''.join(f"<tr><td>{e(r['started'])}</td><td>{eval_monitor.counts(r)['passed']} / {eval_monitor.counts(r)['expected']}</td>"
                           f"<td>{'complete' if eval_monitor.counts(r)['complete'] else 'incomplete'}</td></tr>" for r in comparable[-30:])
    # A table remains the accessible source of each plotted observation. Incomplete runs
    # have gaps; there is no connecting line that suggests missing observations were measured.
    points = []
    recent = comparable[-30:]
    width, height = 760, 220
    rates = [eval_monitor.counts(r)['failure_rate'] for r in recent if eval_monitor.counts(r)['failure_rate'] is not None]
    if stability['status'] in ('signal', 'no_signal'):
        rates.append(stability['upper'])
    maximum = min(1, max(.1, math.ceil((max(rates, default=0) + .02) * 10) / 10))
    for i, r in enumerate(recent):
        c = eval_monitor.counts(r)
        if c['failure_rate'] is not None:
            x = 50 + i * 660 / max(len(recent)-1, 1)
            y = 190 - c['failure_rate'] / maximum * 160
            points.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#73c7dc"><title>{e(r["started"])}: {c["failure_rate"]:.1%} failures</title></circle>')
    lines = []
    if stability['status'] in ('signal', 'no_signal'):
        for name, value in [('Baseline average', stability['center']), ('Lower limit', stability['lower']), ('Upper limit', stability['upper'])]:
            if 0 <= value <= 1:
                y = 190 - value / maximum * 160
                lines.append(f'<line x1="50" x2="710" y1="{y:.1f}" y2="{y:.1f}" stroke="#ddbe7a" stroke-dasharray="5 5"><title>{name}: {value:.1%}</title></line>')
    chart = (f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Failure rate by comparable run, oldest to newest; table below">'
             f'<text x="0" y="35" fill="currentColor">{maximum:.0%}</text><text x="15" y="195" fill="currentColor">0%</text>'
             '<line x1="50" x2="710" y1="190" y2="190" stroke="currentColor"/>' + ''.join(lines+points) + '</svg>') if recent else ''
    limits = (f"Baseline average {stability['center']:.1%}; lower limit {stability['lower']:.1%}; upper limit {stability['upper']:.1%}."
              if stability['status'] in ('signal', 'no_signal') else 'No applicable control limits are shown.')
    return f"""<section class="band" aria-label="Evidence, variation, and acceptance">
<div class="cells"><div><div class="label">Evidence</div><h2>{complete}</h2>
<p>{len(record['attempts'])} recorded / {counts['expected']} planned.<br>{counts['ungraded']} attempts with missing judgments; {counts['missing_outcomes']} missing saved outcomes.
{' Duplicate or unexpected attempts detected.' if counts['invalid'] else ''}
{e(comparison_notice)}</p></div>
<div><div class="label">Variation</div><h2>{e(stability['status'].replace('_', ' ').capitalize())}</h2><p>{e(stability['message'])}</p></div>
<div><div class="label">Acceptance</div><h2>{e(acceptance['status'].replace('_', ' ').capitalize())}</h2><p>{e(acceptance['message'])}</p></div></div>
<p><b>Estimated {'original run ' if record.get('rejudged') else ''}API cost:</b> {dollars}. {usage_text}</p>
<p>Guard configuration: {e(', '.join(record.get('guards', [])) or 'none')}</p>
<details><summary>Comparable history and control-chart readiness ({len(comparable)} runs)</summary>
<p>Cost estimates use standard supported-model rates checked 2026-10-15. Unreported retries and other charges are excluded; unknown usage or models remain unpriced.</p>
<p>Points are ordered runs, not elapsed time. Only matching configurations are shown.
History describes this fixed suite, not all possible user requests. No limits are fitted automatically.
An owner must review a stable period of at least 20 comparable runs before freezing a baseline.
Changed configurations are separate periods; missing evidence breaks a consecutive-run signal.</p>
<p>{'Configuration and served models are recorded.' if key else e(comparison_notice) + ' This record cannot establish a baseline.'}</p>
{chart}<p>{limits} The vertical scale adjusts to the observations; limits outside 0–100% are listed but not drawn.</p><table><thead><tr><th>Started (UTC)</th><th>Confirmed passes / planned</th><th>Evidence</th></tr></thead><tbody>{history_rows}</tbody></table>
<p>Control limits describe variation; acceptance targets describe what is good enough. A stable failure still needs review.</p>
</details></section>"""


def render(record, *, history=(), baseline=None, policy=None):
    repeat = record['repeat']
    generations = record.get('generations', [])
    attempts = [dict(a, _cost_estimate=estimate([g for g in generations
                    if g.get('case') == a['case'] and g.get('attempt') == a['attempt']])) for a in record['attempts']]
    by_case = {c['name']: [a for a in attempts if a['case'] == c['name']] for c in record['cases']}
    ok = sum(map(good, attempts))
    total = len(record['cases']) * repeat
    clean = sum(sum(map(good, by_case[c['name']])) == repeat for c in record['cases'])
    tone = 'pass' if ok == total else 'some'
    ungraded = sum(any(a.get(k) is None for k in ('passed', 'truthful', 'answered')) for a in attempts)
    failures = sum(outcome(a) == 'failed' for a in attempts)
    inconclusive = sum(outcome(a) == 'inconclusive' for a in attempts)
    found = sum(c.get('origin') in ('found in use', 'found by a persona') for c in record['cases'])
    held = sum(c.get('origin') == 'held out' for c in record['cases'])
    # Confirmed failures come first; incomplete evidence must not bury actionable failures.
    cases = sorted(record['cases'], key=lambda c: (
        -sum(outcome(a) == 'failed' for a in by_case[c['name']]),
        sum(map(good, by_case[c['name']]))))
    # A saved run's replies judged again by later judges: the page says so, since its verdicts differ from the run's.
    again = record.get('rejudged')
    rejudged = (f' The replies were judged again with judge revision <span class="num">{e(again["judge_commit"])}</span>'
                f' ({e(again["judge_model"])}); the agent was not run again.') if again else ''
    regrade_notice = ''
    if again:
        extra = (again.get('cost_estimate') or {}).get('usd')
        extra_cost = f'${extra:.4f}' if extra is not None else 'unknown'
        regrade_notice = (f'<section class="band"><h2>Saved replies judged again</h2>'
                          f'<p>{rejudged} This is not a new independent run and is excluded from control-chart comparisons.</p>'
                          f'<p>Rechecked: {e(again.get("check", "see record"))}. Additional estimated judge cost: {extra_cost}. '
                          'The original run cost is shown separately below.</p></section>')
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Todo agent evals</title>
<style>{STYLE}</style></head><body>
<header><div><h1>Todo agent evals</h1><p class="intro">Each case is a scripted conversation, run {repeat} times
because model behavior varies. A pass requires the expected saved state and every required
truthfulness, receipt, and answer check. Missing judgments are inconclusive unless another check
already failed. These are recorded judgments, not independently verified human labels.
Open a case for its expected outcome, then an attempt for the evidence before deciding
whether the application or a grader needs correction.</p></div>
<div class="when">{e(record['started'][:16].replace('T', ' '))} UTC<span class="num">{e(record['model'])}</span></div></header>
<main>
{regrade_notice}

<div class="band"><div class="cells">
<div><div class="label">Attempts passed</div><div class="big num {tone}">{ok}<small> of {total}</small></div>
<div class="under">{failures} failed · {inconclusive} inconclusive · {eval_monitor.counts(record)['missing']} missing.<br>{ungraded} attempts have at least one missing judgment.</div></div>
<div><div class="label">Cases clean (pass^{repeat})</div><div class="big num">{clean}<small> of {len(record['cases'])}</small></div>
<div class="under">all {repeat} attempts passed, as a user repeating the job would see it</div></div>
<div><div class="label">Found in use or by personas</div><div class="big num">{found}<small> + {held} held out</small></div>
<div class="under">of {len(record['cases'])} cases; {repeat} attempts each</div></div>
</div></div>
{monitor_panel(record, history, baseline, policy)}
<details class="band"><summary>Run configuration and how to read the counts</summary>
<p>Application revision: <span class="num">{e(record.get('commit', 'not recorded'))}</span>.<br>
Agent model requested: {e(record['model'])}. Judge model requested: {e(record.get('judge_model', 'not recorded'))}.<br>
Reported served models: {e(', '.join(sorted({g['served_model'] for g in record.get('generations', []) if g.get('served_model')})) or 'not recorded')}.<br>
Configuration: <span class="num">{e((record.get('configuration') or {}).get('fingerprint', 'not recorded'))}</span>.<br>
Source snapshot: {e(record.get('source_snapshot', 'not recorded'))}.<br>
Shuffled tools: {e(record.get('shuffled_tools', 'not recorded'))}.
Injected failure rate: {e(record.get('injected_failure_rate', 'not recorded'))}.</p>
<p>Counts show confirmed passes against planned attempts. Incomplete evidence does not establish a failure rate.
Even {repeat} successes in {repeat} attempts has a 95% Wilson lower bound of about {interval(repeat, repeat).split('–')[0]}%.
Older reports without all current checks may be inconclusive under these rules.</p>
</details>
<div class="cols label"><span>Case</span><span>Judged by</span><span>Result</span><span></span></div>
{''.join(row(c, by_case[c['name']], repeat) for c in cases)}
</main>
<footer>Open a case, then an attempt, to see what happened turn by turn. The user's first sentence opens that
attempt’s optional trace when one was recorded. The local record contains the conversation and outcomes. Generated from <span class="num">{e(record['run'])}</span>;
never edited by hand.{rejudged}</footer>
</body></html>"""


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description='Generate the local eval review; no model calls.')
    parser.add_argument('record', nargs='?', type=Path)
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--policy', type=Path)
    args = parser.parse_args(argv)
    history = eval_monitor.read_runs(args.record.parent if args.record else RUNS)
    record = json.loads(args.record.read_text()) if args.record else (history[-1] if history else None)
    if record is None:
        parser.error('No run report yet: run evals.py first.')
    baseline = json.loads(args.baseline.read_text()) if args.baseline else None
    policy = json.loads(args.policy.read_text()) if args.policy else None
    out = (args.record.parent if args.record else RUNS) / 'evals.html'
    out.write_text(render(record, history=history, baseline=baseline, policy=policy))
    print(out)


if __name__ == '__main__':
    main()
