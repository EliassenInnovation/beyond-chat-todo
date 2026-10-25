/* Browser-only handoff builder. Text is inserted with textContent, never interpreted as HTML. */
(function () {
  'use strict';
  const labels = {undecided: 'Undecided', include: 'Include', adapt: 'Adapt', na: 'Not applicable'};
  function decisions(data) {
    return Object.fromEntries(data.checks.map(c => [c.id, {status: 'undecided', note: ''}]));
  }
  function preset(data, state, name) {
    // Add suggestions only to undecided items; retain every explicit decision and note.
    data.checks.forEach(c => {
      if (state[c.id].status === 'undecided' && (name === 'all' || c.presets.includes(name)))
        state[c.id].status = 'include';
    });
  }
  function errors(data, state) {
    return data.checks.filter(c => ['adapt', 'na'].includes(state[c.id].status) && !state[c.id].note.trim())
      .map(c => `Check ${c.id}: add ${state[c.id].status === 'adapt' ? 'an adaptation note' : 'a reason for setting it aside'}.`);
  }
  const cell = value => value.replace(/\|/g, '\\|').replace(/[\r\n]+/g, ' ');
  function outputs(data, state, scope, chapters) {
    const unresolved = data.checks.filter(c => state[c.id].status === 'undecided');
    const selected = data.checks.filter(c => ['include', 'adapt'].includes(state[c.id].status));
    const version = `Guide: ${data.guideUrl}\nSource commit: ${data.commit}${data.dirty ? ' (working-tree edits included)' : ''}\nContent revision: ${data.revision}\n${data.revisionNote}`;
    const status = unresolved.length ? `Draft: ${unresolved.length} checks remain undecided. Resolve them with the team before treating this as the agreed scope.` : 'All applicability decisions recorded. Acceptance still requires implementation and test evidence.';
    const persistent = `# Application-agent working instructions\n\n${status}\n\n## Agreed task\n\n${scope.trim() || 'Task scope remains to be agreed. Assess first; agree implementation work with the team.'}\n\n${version}\n\n## Who owns what\n\n${data.ownership}\n\n## Working rules\n\n${data.rules}\n\n## Adopted checks\n\n${selected.map(c => c.id + (state[c.id].status === 'adapt' ? ' (adapted)' : '')).join(', ') || 'None selected yet.'}\n\nRead [agent-checks.md](agent-checks.md) for the full checks, adaptations, exclusions, and unresolved decisions. These applicability choices are not test results. Merge this section with existing project instructions.\n`;
    let detailed = `# Application-agent checks and decisions\n\n${status}\n\n## Agreed task\n\n${scope.trim() || 'To be agreed.'}\n\n${version}\n\n${data.security}\n\n## Decisions\n\n| Check | Decision | Note or reason |\n| --- | --- | --- |\n`;
    data.checks.forEach(c => {const d=state[c.id]; detailed += `| [${c.id} — ${cell(c.title)}](${c.url}) | ${labels[d.status]} | ${cell(d.note)} |\n`;});
    detailed += '\n## Selected checks\n\n';
    selected.forEach(c => {detailed += `### Check ${c.id} — ${c.title}\n\n${c.text}\n\nSource: ${c.url}\n\n`; if(state[c.id].status==='adapt') detailed += `Team adaptation: ${state[c.id].note}\n\n`;});
    detailed += `## Reporting evidence\n\n${data.report}\n\n## Guide chapters\n\n`;
    data.chapters.forEach(c => { detailed += `- [${c.title}](${c.url})\n`; });
    data.chapters.filter(c => chapters.includes(c.id)).forEach(c => { detailed += `\n---\n\n${c.text}\n`; });
    const snapshot = {format: 1, revision: data.revision, scope, chapters, decisions: state};
    detailed += '\n## Resume this handoff\n\nLoad this file in the checklist builder to restore its saved choices. Edit choices in the builder and download again.\n\n```handoff-state\n' + JSON.stringify(snapshot, null, 2) + '\n```\n';
    return {persistent, detailed};
  }
  function restore(data, markdown) {
    const saved = markdown.match(/^```handoff-state\n([\s\S]*?)\n```/m);
    let imported;
    if (saved) {
      imported = JSON.parse(saved[1]);
      if (imported.format !== 1 || typeof imported.scope !== 'string' || !Array.isArray(imported.chapters))
        throw Error('Unsupported handoff format.');
    } else {
      // Older downloads have only the visible decision table.
      const table = markdown.match(/^## Decisions\n([\s\S]*?)(?=^## |$(?![\s\S]))/m);
      if (!table) throw Error('Choose an agent-checks.md download.');
      const rows = Object.create(null);
      for (const line of table[1].split('\n')) {
        const match = line.match(/^\| \[(\d+\.\d+) — .*?\]\(.*?\) \| (Undecided|Include|Adapt|Not applicable) \| (.*) \|$/);
        if (match) {
          if (rows[match[1]]) throw Error('Duplicate check in the imported table.');
          rows[match[1]] = {status:Object.keys(labels).find(k=>labels[k]===match[2]), note:match[3].replace(/\\\|/g,'|')};
        }
      }
      imported = {format:1, decisions:rows, chapters:[], scope:(markdown.match(/^## Agreed task\n\n([\s\S]*?)\n\nGuide:/m)||[])[1]||'', revision:(markdown.match(/^Content revision: (.+)$/m)||[])[1]};
    }
    if (!imported.decisions || typeof imported.decisions !== 'object' || Array.isArray(imported.decisions)) throw Error('Missing decisions.');
    const state=decisions(data), unknown=[];
    for (const [id, value] of Object.entries(imported.decisions)) {
      if (!value || !Object.hasOwn(labels,value.status) || typeof value.note !== 'string') throw Error(`Invalid decision for ${id}.`);
      if (!Object.hasOwn(state,id)) {unknown.push(id);continue;}
      state[id]={status:value.status,note:value.note};
    }
    if (!Object.keys(imported.decisions).some(id=>Object.hasOwn(state,id))) throw Error('No matching checks found.');
    const changed = imported.revision !== data.revision;
    return {state, scope:imported.scope, chapters:imported.chapters.filter(id=>data.chapters.some(c=>c.id===id)),
      message:'Draft loaded. ' + (changed?'The guide revision differs; review the restored decisions against the current checks. ':'') +
        (unknown.length?`Checks absent from this guide were not imported: ${unknown.join(', ')}. Keep the original file. `:'') +
        'Checks missing from the draft remain undecided.'};
  }
  function selectGroup(state, ids, checked) {
    ids.forEach(id => {
      if (checked && state[id].status !== 'adapt') state[id].status = 'include';
      if (!checked && ['include', 'adapt'].includes(state[id].status)) state[id].status = 'undecided';
    });
  }
  const api = {decisions, preset, errors, outputs, selectGroup, restore};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (typeof document === 'undefined') return;
  const root = document.getElementById('checklist-builder');
  if (!root) return;
  function el(tag, text, parent, attrs={}) {
    const node=document.createElement(tag); if(text) node.textContent=text;
    Object.entries(attrs).forEach(([k,v])=>node.setAttribute(k,v)); if(parent) parent.append(node); return node;
  }
  fetch(root.dataset.source).then(r => {if(!r.ok) throw Error('Unable to load checks'); return r.json();}).then(data => {
    root.replaceChildren(); const state=decisions(data); preset(data,state,'embedded');
    el('p', `${data.checks.length} checks · Content revision ${data.revision}${data.dirty ? ' · includes unpublished edits' : ''}`,root);
    el('p','Choose Everything or a group on the left, then review its checks on the right. A dash means partly selected. Unchecking returns checks to Undecided; use Not applicable with a reason to set a check aside. Existing notes are retained.',root);
    el('label','Resume from an agent-checks.md download',root,{for:'builder-import'});
    const importFile=el('input','',root,{id:'builder-import',type:'file',accept:'.md,text/markdown,text/plain'});
    el('p','Loading a draft replaces the choices on this page. Download your current work first if you want to keep it.',root);
    const importStatus=el('p','',root,{role:'status'});
    const scopeLabel=el('label','Describe the job, interfaces, and changes you authorize',root,{for:'builder-scope'});
    const scope=el('textarea','',root,{id:'builder-scope',rows:'3',placeholder:'For example: assess rescheduling through the screen and embedded agent; report gaps before changing code.'});
    const summary=el('p','',root,{role:'status','aria-live':'polite'});
    const tree=el('div','',root,{class:'builder-tree'});
    const buttons=el('div','',tree,{class:'builder-presets'});
    el('h3','Choose scope',buttons);
    const sections=el('div','',tree,{class:'builder-branches'}); const controls={};
    const groupControls=[];
    function groupBox(parent, label, ids) {
      const row=el('label','',parent,{class:'builder-group-choice'});
      const input=el('input','',row,{type:'checkbox'});
      const text=el('span',label,row); const count=el('small','',row);
      groupControls.push({input,count,ids});
      input.addEventListener('change',()=>{selectGroup(state,ids,input.checked);refresh();});
    }
    [...new Set(data.checks.map(c=>c.section))].forEach(section=>{
      const group=el('section','',sections,{class:'builder-branch'});
      groupBox(group,section,data.checks.filter(c=>c.section===section).map(c=>c.id));
      data.checks.filter(c=>c.section===section).forEach(c=>{
        const item=el('div','',group,{class:'builder-check'});
        const row=el('div','',item,{class:'builder-check-row'});
        const tick=el('input','',row,{type:'checkbox','aria-label':`Include Check ${c.id}: ${c.title}`});
        const detail=el('details','',row);
        el('summary',`${c.id} — ${c.title}`,detail);
        const badge=el('small','',item,{class:'builder-decision'});
        el('a','Read in the guide',detail,{href:c.url,target:'_blank',rel:'noopener'});
        tick.addEventListener('change',()=>{selectGroup(state,[c.id],tick.checked);refresh();});
        el('p',c.text,detail,{class:'builder-explanation'});
        el('label',`Decision for Check ${c.id}`,detail,{for:`decision-${c.id}`});
        const select=el('select','',detail,{id:`decision-${c.id}`});
        Object.entries(labels).forEach(([value,label])=>el('option',label,select,{value})); select.value=state[c.id].status;
        el('label',`Adaptation, reason, or optional note for Check ${c.id}`,detail,{for:`note-${c.id}`});
        const note=el('textarea','',detail,{id:`note-${c.id}`,rows:'2'});
        controls[c.id]={select,note,tick,badge};
        select.addEventListener('change',()=>{state[c.id].status=select.value; refresh();});
        note.addEventListener('input',()=>{state[c.id].note=note.value; refresh();});
      });
    });
    const chapterGroup=el('details','',root);el('summary','Include chapter text (optional)',chapterGroup);
    el('p','Both downloads link to the guide. Select chapters here when the coding agent also needs their full text in agent-checks.md.',chapterGroup);
    const chapterControls=data.chapters.map((c,i)=>{const label=el('label','',chapterGroup,{class:'builder-chapter'}); const input=el('input','',label,{type:'checkbox',value:c.id}); label.append(document.createTextNode(' '+c.title));input.addEventListener('change',refresh);return input;});
    el('h2','Preview and download',root);
    el('label','Persistent instructions filename',root,{for:'builder-filename'});
    const filename=el('select','',root,{id:'builder-filename'});['AGENTS.md','CLAUDE.md'].forEach(x=>el('option',x,filename,{value:x}));
    el('p','Merge the persistent section into your existing instructions; keep agent-checks.md beside it. If both tools are used, keep one maintained instruction file and point the other at it.',root);
    const messages=el('p','',root,{role:'status'});const actions=el('div','',root,{class:'builder-actions'});
    const previews={};['persistent','detailed'].forEach((key,i)=>{const d=el('details','',root);el('summary',i?'Preview checks and decisions':'Preview persistent instructions',d);previews[key]=el('pre','',d);});
    function result(){return outputs(data,state,scope.value,chapterControls.filter(x=>x.checked).map(x=>x.value));}
    function refresh(){
      const counts={};Object.keys(labels).forEach(k=>counts[k]=data.checks.filter(c=>state[c.id].status===k).length);
      summary.textContent=Object.keys(labels).map(k=>`${counts[k]} ${labels[k].toLowerCase()}`).join(' · ');
      const issues=errors(data,state);messages.textContent=issues.length?issues.join(' '):counts.undecided?'Download a draft, or resolve the remaining checks for a completed handoff.':'Ready to download your decisions.';
      Object.keys(controls).forEach(id=>{const {select,note,tick,badge}=controls[id];select.value=state[id].status;tick.checked=['include','adapt'].includes(state[id].status);badge.textContent=labels[state[id].status];note.required=['adapt','na'].includes(state[id].status);note.setAttribute('aria-invalid',String(note.required&&!note.value.trim()));});
      groupControls.forEach(({input,count,ids})=>{const n=ids.filter(id=>['include','adapt'].includes(state[id].status)).length;input.checked=n===ids.length;input.indeterminate=n>0&&n<ids.length;count.textContent=`${n} / ${ids.length}`;});
      actions.querySelectorAll('button').forEach(b=>b.disabled=issues.length>0);
      const out=result();Object.keys(previews).forEach(k=>previews[k].textContent=out[k]);
    }
    [['all','Everything'],['embedded','Embedded agent, first capability'],['mcp','External agents (MCP)'],['evaluation','Evaluation']].forEach(([name,label])=>{
      groupBox(buttons,label,data.checks.filter(c=>name==='all'||c.presets.includes(name)).map(c=>c.id));
    });
    el('p','Groups can overlap. Selecting a group includes its checks; adaptations remain adapted. Review individual decisions below.',buttons);
    [['persistent','Download instructions'],['detailed','Download checks']].forEach(([key,label])=>{const b=el('button',label,actions,{type:'button'});b.onclick=()=>{if(errors(data,state).length)return;const url=URL.createObjectURL(new Blob([result()[key]],{type:'text/markdown;charset=utf-8'}));const a=el('a','',null,{href:url,download:key==='persistent'?filename.value:'agent-checks.md'});a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};});
    importFile.addEventListener('change',async()=>{
      const file=importFile.files[0];if(!file)return;
      try {
        if(file.size>5000000)throw Error('Choose a handoff smaller than 5 MB.');
        const loaded=restore(data,await file.text());
        Object.keys(state).forEach(id=>{state[id]=loaded.state[id];controls[id].note.value=state[id].note;});
        scope.value=loaded.scope;chapterControls.forEach(c=>c.checked=loaded.chapters.includes(c.value));
        refresh();importStatus.textContent=loaded.message;
      } catch(error) {importStatus.textContent='Draft was not loaded. '+error.message;}
      importFile.value='';
    });
    scope.addEventListener('input',refresh);refresh();
  }).catch(()=>{root.textContent='The checklist could not load. Reload the page, or use the acceptance checks and full download linked below.';});
})();
