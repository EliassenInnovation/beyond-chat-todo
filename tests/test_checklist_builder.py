"""The generated handoff must preserve source checks and explicit applicability decisions."""
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('checklist_data', ROOT / '.github/checklist_data.py')
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)


def test_builder_tracks_source_and_preserves_nested_requirements():
    source = (ROOT / 'docs/principles/implementation.md').read_text()
    checks = parser.parse_checks(source)
    assert [c['id'] for c in checks] == re.findall(r'^- Check (\d+\.\d+) —', source, re.M)
    view = next(c for c in checks if c['id'] == '1.14')
    assert 'Only the client that announces support receives the view.' in view['text']
    assert 'Also make the view fail to display' in view['text']
    for ident in ('3.3', '3.4', '3.6'):
        assert 'embedded' in next(c for c in checks if c['id'] == ident)['presets']
    with pytest.raises(ValueError):
        parser.parse_checks(source.replace('<!-- builder:', '<!-- omitted:', 1))


def test_browser_exports_preserve_notes_and_unresolved_decisions(tmp_path):
    if not shutil.which('node'):
        pytest.skip('Node is needed to test the browser export functions')
    data = parser.build_data(ROOT, 'https://example.org/guide/', [], 'https://github.com/example/project')
    fixture = tmp_path / 'data.json'
    fixture.write_text(json.dumps(data))
    script = r'''
const assert = require('node:assert/strict');
const fs = require('node:fs');
const api = require(process.argv[1]);
const data = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const state = api.decisions(data);
api.preset(data,state,'embedded');
assert.equal(state['3.3'].status,'include');
assert.equal(state['6.9'].status,'undecided');
state['3.3']={status:'na',note:''};
assert(api.errors(data,state).some(x=>x.includes('3.3')));
state['3.3'].note='Read-only review | revisit before writes';
state['1.1']={status:'adapt',note:'Only the screen and embedded agent'};
api.preset(data,state,'all');
assert.equal(state['3.3'].status,'na');
assert.equal(state['1.1'].status,'adapt');
assert.equal(api.errors(data,state).length,0);
state['6.9'].status='undecided';
const out=api.outputs(data,state,'Assess before implementation',[]);
assert(out.persistent.includes('Draft: 1 checks remain undecided'));
assert(out.persistent.includes('1.1 (adapted)'));
assert(out.detailed.includes('Team adaptation: Only the screen and embedded agent'));
assert(out.detailed.includes('Read-only review \\| revisit before writes'));
assert(!out.detailed.includes('### Check 3.3'));
assert(!out.detailed.includes('### Check 6.9'));
assert(out.detailed.includes('### Check 1.14'));
assert(out.detailed.includes('Also make the view fail to display'));
assert(out.detailed.includes(data.commit));
assert(out.detailed.includes(data.revision));
api.selectGroup(state,data.checks.map(c=>c.id),true);
assert(data.checks.every(c=>['include','adapt'].includes(state[c.id].status)));
assert.equal(state['1.1'].status,'adapt');
api.selectGroup(state,['3.3'],false);
assert.equal(state['3.3'].status,'undecided');
assert.equal(state['3.3'].note,'Read-only review | revisit before writes');
state['1.1'].note='First line\nSecond | line';
const saved=api.outputs(data,state,'A scoped task',[]).detailed;
const restored=api.restore(data,saved);
assert.deepEqual(restored.state,state);
assert.equal(restored.scope,'A scoped task');
assert.throws(()=>api.restore(data,'unrelated file'));
assert.throws(()=>api.restore(data,'```handoff-state\n{}\n```'));
const legacy=saved.split('## Resume this handoff')[0];
assert.equal(api.restore(data,legacy).state['1.1'].status,'adapt');
assert.equal(api.restore(data,legacy).state['3.3'].note,state['3.3'].note);
const newer=structuredClone(data);newer.revision='next';newer.checks.push({id:'9.1'});
const migrated=api.restore(newer,saved);
assert(migrated.message.includes('revision differs'));
assert.equal(migrated.state['9.1'].status,'undecided');

'''
    subprocess.run(['node', '-e', script, str(ROOT / 'docs/javascripts/checklist-builder.js'), str(fixture)], check=True)


def test_repository_links_follow_configuration():
    result = parser.portable('[code](../../todo/todos.py)', 'guide/start.md', ROOT,
                             'https://example.org/guide/', 'https://github.com/new-owner/new-repo')
    assert result == '[code](https://github.com/new-owner/new-repo/blob/main/todo/todos.py)'
