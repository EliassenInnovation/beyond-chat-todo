"""Display a recorded persona session without constructing a model client."""
from pathlib import Path
import json

ASSETS = Path(__file__).resolve().parents[1] / 'docs' / 'demos'


def replay_html():
    """Bundle the same browser replay for Streamlit's isolated component iframe."""
    record = json.loads((ASSETS / 'sam-recording.json').read_text())
    script = (ASSETS / 'persona-replay.js').read_text()
    payload = json.dumps(record, ensure_ascii=False).replace('<', '\\u003c')
    script = script.replace("const response=await fetch('sam-recording.json');if(!response.ok)throw Error('Recording could not be loaded.');const record=await response.json();", f'const record={payload};')
    script = script.replace('export function makeFrames', 'function makeFrames')
    page = (ASSETS / 'persona-replay.html').read_text()
    page = page.replace('<script type="module" src="persona-replay.js"></script>', '<script type="module">' + script + '</script>')
    page = page.replace('<a href="../index.html#introduction">← Back to the guide</a>', '')
    page = page.replace('<a href="sam-recording.json">Download the recording</a>', '')
    return page
