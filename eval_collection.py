"""Offline collection review from a portable, deliberately selected evidence bundle.

    python eval_collection.py examples/evaluation-review/collection.json

No model calls, service connections, grade changes or automatic baseline acceptance.
"""
import argparse
import json
import math
from html import escape
from pathlib import Path

from run_evidence import digest


def validate(bundle):
    if bundle.get('version') != 1:
        raise ValueError('Unsupported collection version.')
    if bundle.get('bundle_digest') != digest({k: v for k, v in bundle.items() if k != 'bundle_digest'}):
        raise ValueError('Collection digest does not match; rebuild the bundle after intentional edits.')
    observations = bundle['observations']
    if not observations or len({o['run'] for o in observations}) != len(observations):
        raise ValueError('Collection needs distinct observations.')
    for o in observations:
        if o['passed'] + o['failed'] + o['inconclusive'] != o['expected']:
            raise ValueError('Observation counts do not reconcile.')
    if len({x['id'] for x in bundle['examples']}) != len(bundle['examples']):
        raise ValueError('Review example identifiers must be unique.')
    by_run = {o['run']: o for o in observations}
    for x in bundle['examples']:
        if x['run'] not in by_run or x['source_digest'] != by_run[x['run']]['source_digest']:
            raise ValueError('Review evidence must name its original run and digest.')


def validate_notes(bundle, notes):
    """Review notes describe judgments; they never rewrite source grades."""
    validate(bundle)
    if notes.get('version') != 1 or notes.get('bundle_digest') != bundle['bundle_digest']:
        raise ValueError('Review notes belong to a different evidence bundle.')
    expected = {x['id'] for x in bundle['examples']}
    reviews = notes.get('reviews', [])
    ids = [x.get('id') for x in reviews]
    if len(ids) != len(set(ids)) or set(ids) != expected:
        raise ValueError('Review notes must contain each example exactly once.')
    choices = {'unreviewed', 'grader_concern', 'application_concern', 'mixed', 'uncertain'}
    if any(x.get('assessment') not in choices or not isinstance(x.get('note'), str) for x in reviews):
        raise ValueError('Invalid review assessment or note.')
    return sum(x['assessment'] != 'unreviewed' for x in reviews)


STYLE = '''
:root{color-scheme:light;--ink:#17223a;--muted:#536174;--line:#d4dce5;--accent:#334da0}
*{box-sizing:border-box}body{font:17px/1.55 system-ui,sans-serif;color:var(--ink);background:#f6f8fb;margin:0;padding:28px 20px 60px}
main{max-width:1060px;margin:auto}h1{font-size:32px;line-height:1.2}h2{font-size:23px;margin-top:0}h3{font-size:18px}
p{margin:10px 0}a{color:var(--accent)}section,article{background:white;border:1px solid var(--line);border-radius:12px;padding:24px;margin:22px 0}
.notice{border-left:5px solid #aa7100;background:#fff8e8}.muted,small{color:var(--muted)}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.metric b{display:block;font-size:30px}.metric span{font-size:14px}
svg{display:block;width:100%;height:auto}table{border-collapse:collapse;width:100%;font-size:15px}th,td{text-align:left;padding:10px;border-bottom:1px solid var(--line)}.table{overflow-x:auto}details{margin:12px 0}summary{cursor:pointer;color:var(--accent)}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.5 ui-monospace,monospace;background:#f5f7fa;padding:12px;border-radius:6px}
.turn{border-left:3px solid var(--line);padding:0 0 0 14px;margin:18px 0}.speaker{font-weight:650;font-size:14px}label{display:block;margin:10px 0}select,textarea,input,button{font:inherit;max-width:100%}select,textarea,input{padding:10px;border:1px solid #8794a6;border-radius:5px;background:white;color:var(--ink)}textarea{width:100%;min-height:85px}button{background:var(--accent);color:white;border:0;border-radius:6px;padding:12px 18px;cursor:pointer}button:focus-visible,summary:focus-visible{outline:3px solid #df9b35;outline-offset:4px}.badge{font-size:14px;font-weight:600;color:#865800}.wrap{overflow-wrap:anywhere}
@media(max-width:600px){body{padding:16px 10px}section,article{padding:16px}.metrics{grid-template-columns:1fr}h1{font-size:26px}.metric b{font-size:26px}}
'''


def e(value):
    return escape(str(value), quote=True)


def chart(observations, candidate):
    rates = [o['failed'] / o['expected'] for o in observations if o['complete']]
    maximum = max(.1, math.ceil((max(rates + [candidate['upper']] if candidate else rates) + .01) * 10) / 10)
    y = lambda value: 215 - value / maximum * 170
    parts = [f'<svg viewBox="0 0 800 270" role="img" aria-label="Recorded failure rates by run; exact counts are in the table below"><text x="8" y="45">{maximum:.0%}</text><text x="20" y="220">0%</text><line x1="65" x2="760" y1="215" y2="215" stroke="#8794a6"/>']
    if candidate:
        for label, value in [('Candidate average', candidate['center']), ('Candidate upper limit', candidate['upper']), ('Candidate lower limit', candidate['lower'])]:
            if 0 <= value <= maximum:
                parts.append(f'<line x1="65" x2="760" y1="{y(value):.2f}" y2="{y(value):.2f}" stroke="#aa7100" stroke-dasharray="6 5"><title>{label}: {value:.2%}</title></line>')
    for i, o in enumerate(observations):
        x = 65 + i * 695 / max(1, len(observations)-1)
        if o['complete']:
            rate = o['failed']/o['expected']
            parts.append(f'<circle cx="{x:.2f}" cy="{y(rate):.2f}" r="5" fill="#334da0"><title>Observation {i+1}: {rate:.2%} recorded failures</title></circle>')
        parts.append(f'<text x="{x:.2f}" y="245" text-anchor="middle" font-size="12">{i+1}</text>')
    return ''.join(parts)+'</svg>'


def example(item):
    attempt = item['attempt']
    turns = []
    for turn in attempt['conversation']:
        if 'app' in turn:
            turns.append(f'<div class="turn"><div class="speaker">Person used the app</div><pre>{e(json.dumps(turn["app"], ensure_ascii=False))}</pre></div>')
        if 'user' in turn:
            turns.append(f'<div class="turn"><div class="speaker">Person</div><p>{e(turn["user"])}</p><div class="speaker">Assistant</div><p style="white-space:pre-wrap">{e(turn.get("assistant", ""))}</p>')
            evidence = {k:turn[k] for k in ('tools','list_after') if k in turn}
            turns.append(f'<details><summary>Actions and resulting state</summary><pre>{e(json.dumps(evidence,indent=2,ensure_ascii=False))}</pre></details></div>')
    checks = {k:v for k,v in attempt.get('checks', {}).items() if v.get('passed') is False}
    return f'''<article class="review-item" data-id="{e(item['id'])}"><h3>{e(item['title'])}</h3>
<p>{e(item['question'])}</p><p class="muted">{e(item['run_label'])} · {e(attempt['case'])} · attempt {attempt['attempt']}</p>
<details><summary>Conversation and application evidence</summary><p>Case expectation: {e(item['expectation'])}</p>
<details><summary>Initial state</summary><pre>{e(json.dumps(attempt['before'],indent=2,ensure_ascii=False))}</pre></details>{''.join(turns)}</details>
<label>Your assessment <select class="assessment"><option value="unreviewed">Not reviewed</option><option value="grader_concern">Grader concern: response appears adequate</option><option value="application_concern">Application concern: response or action is wrong</option><option value="mixed">Both application and grading concerns</option><option value="uncertain">Needs discussion / insufficient evidence</option></select></label>
<label>Why? <textarea class="note" placeholder="Describe the outcome that matters, rather than preferred wording."></textarea></label>
<details><summary>Original flags and assistant review note</summary><pre>{e(json.dumps(checks,indent=2,ensure_ascii=False))}</pre><p>{e(item['assistant_note'])}</p><p class="muted">This note is a proposed interpretation, not a human label.</p></details></article>'''


def render(bundle):
    validate(bundle)
    observations = bundle['observations']
    total = sum(o['expected'] for o in observations)
    passed = sum(o['passed'] for o in observations)
    complete = sum(o['complete'] for o in observations)
    cost = sum(o['cost_usd'] or 0 for o in observations)
    candidate = bundle.get('candidate_limits')
    rows = ''.join(f'<tr><td>{i+1}</td><td>{e(o["run_label"])}</td><td>{o["passed"]}/{o["expected"]}</td><td>{o["failed"]}</td><td>{"Complete" if o["complete"] else "Incomplete"}</td></tr>' for i,o in enumerate(observations))
    limits = (f'Average {candidate["center"]:.2%}; lower limit {candidate["lower"]:.2%}; upper limit {candidate["upper"]:.2%}. The negative lower limit is listed, not drawn.' if candidate else 'No candidate limits are available.')
    # Only a small identity payload enters script; user-controlled text stays escaped HTML.
    payload = json.dumps({'bundle_digest':bundle['bundle_digest'],'title':bundle['title']}).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(bundle['title'])}</title><style>{STYLE}</style></head><body><main>
<h1>{e(bundle['title'])}</h1><p>A real, fixed-configuration collection from the todo starter. No server, account, or model calls are needed to read this page.</p>
<section class="notice"><h2>Evidence complete; quality baseline not accepted</h2><p>{e(bundle['conclusion'])}</p><p>The scores below are the original recorded results. Human review notes do not change them.</p></section>
<section><div class="metrics"><div class="metric"><b>{complete}/{len(observations)}</b><span>Runs with complete evidence</span></div><div class="metric"><b>{passed:,}/{total:,}</b><span>Recorded passes ({passed/total:.2%})</span></div><div class="metric"><b>${cost:.2f}</b><span>Estimated reported cost; excludes separate preflight</span></div></div></section>
<section><h2>Observed variation</h2><p class="badge">Illustrative candidate limits—not an accepted baseline</p>{chart(observations,candidate)}<p>{e(limits)}</p>
<p>{e(bundle['chart_note'])}</p><details><summary>All observations in start-time order</summary><div class="table"><table><thead><tr><th>Order</th><th>Run</th><th>Passes</th><th>Failures</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div></details>
<p>A stable rate can still contain unacceptable outcomes or grader errors. New important failures need review even when the overall rate remains within limits.</p></section>
<section><h2>How to use this example</h2><p>Read a conversation and its actions, then decide whether the issue is in the application, the grader, or both. The original flag and assistant note are collapsed so you can form your own view first. These selected examples are a discussion queue, not a representative accuracy sample.</p>
<p>For ordinary changes: offline tests → focused evals → a full regression run when model behavior can change. Twenty full runs establish variation; they are not required after every edit. A new prompt, model, tool or grader starts a reviewed comparison period, not automatically new control limits.</p>
<p><a href="../../docs/evaluation-signals.md">Evaluation workflow and chart limits</a> · <a href="../../docs/guarded-baseline-2026-10-15.md">Collection review</a> · <a href="collection.json">Portable evidence bundle</a></p></section>
<section><h2>Human review queue</h2><p>Notes stay in this tab until you download them. Nothing is sent to a service or saved automatically. Download before closing or refreshing.</p><label>Reviewer (optional) <input id="reviewer" autocomplete="off"></label><noscript><p>JavaScript is disabled. The evidence is readable, but downloading structured notes requires JavaScript.</p></noscript></section>
{''.join(example(x) for x in bundle['examples'])}
<section><button id="download" type="button">Download review notes</button><p id="download-status" role="status" aria-live="polite"></p><p>Download creates a separate JSON file tied to this evidence bundle. It does not relabel attempts, update charts, or approve a baseline.</p></section>
<details><summary>Provenance and limitations</summary><p>{e(bundle['provenance'])}</p><p class="wrap">Bundle digest: {e(bundle['bundle_digest'])}</p><p>Digests detect accidental changes; they do not establish authorship. The JSON includes source-record digests and selected evidence, not every conversation or the full source snapshots. This is a review export, not a replacement run record.</p></details>
</main><script>
const identity={payload};
document.getElementById('download').addEventListener('click',()=>{{
 const reviews=Array.from(document.querySelectorAll('.review-item')).map(el=>({{id:el.dataset.id,assessment:el.querySelector('.assessment').value,note:el.querySelector('.note').value}}));
 const record={{version:1,...identity,reviewer:document.getElementById('reviewer').value,created:new Date().toISOString(),reviews}};
 const url=URL.createObjectURL(new Blob([JSON.stringify(record,null,2)+'\\n'],{{type:'application/json'}}));
 const link=document.createElement('a');link.href=url;link.download='todo-evaluation-review.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 document.getElementById('download-status').textContent='Downloaded notes for '+reviews.filter(x=>x.assessment!=='unreviewed').length+' reviewed examples. Original scores are unchanged.';
}});
</script></body></html>'''


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--notes',type=Path,help='validate downloaded notes without changing grades')
    args=parser.parse_args(argv)
    bundle=json.loads(args.bundle.read_text())
    if args.notes:
        count=validate_notes(bundle,json.loads(args.notes.read_text()))
        print(f'Valid notes: {count}/{len(bundle["examples"])} examples reviewed; scores unchanged.')
        return
    out=args.output or args.bundle.with_name('index.html')
    out.write_text(render(bundle))
    print(out)


if __name__=='__main__':
    main()
