// Playback only: snapshots are displayed, never executed as application commands.
export function makeFrames(record) {
  const messages = [], frames = [];
  const add = (state, event, selection = null, end = false) => frames.push({state, event, selection, end, messages: [...messages]});
  add(record.initial, 'Starting list. Sam has just returned from two weeks away.');
  for (const turn of record.turns) {
    if (turn.clicked_ids?.length) {
      const selection = {ids: turn.clicked_ids, action: turn.persona.click};
      add(turn.before_click, `Sam selects ${selection.action === 'approve' ? 'Approve' : 'Deny'} on the pending requests.`, selection);
      messages.push({role:'person-action', text:`Sam clicked ${selection.action === 'approve' ? 'Approve' : 'Deny'} on ${selection.ids.length} request(s).`});
      add(turn.before, 'The application processes Sam’s decision and closes the approval cards.');
    }
    if (turn.user) messages.push({role:'sam', text:turn.user});
    add(turn.before, `Sam speaks — turn ${turn.n}.`);
    if (turn.assistant) {
      messages.push({role:'assistant', text:turn.assistant});
      add(turn.after, `Assistant reply and application state — turn ${turn.n}.`);
    }
  }
  add(record.final, 'End of the recorded session.', null, true);
  return frames;
}
const $ = id => document.getElementById(id);
const node = (tag, text, cls) => {const el=document.createElement(tag); if(text!==undefined)el.textContent=text;if(cls)el.className=cls;return el;};
async function start() {
 const response=await fetch('sam-recording.json');if(!response.ok)throw Error('Recording could not be loaded.');const record=await response.json();
 const frames=makeFrames(record);let index=0,timer=null;
 function pause(){clearTimeout(timer);timer=null;$('play').textContent='Play';}
 function render(){const frame=frames[index],state=frame.state;
  $('position').textContent=`Step ${index+1} of ${frames.length}`;$('event').textContent=frame.event;
  $('previous').disabled=index===0;$('next').disabled=index===frames.length-1;$('play').disabled=index===frames.length-1;
  $('todos').replaceChildren();const visible=state.todos.filter(t=>state.visible.includes(t.title));
  for(const todo of visible){const row=node('div',undefined,'todo'+(todo.done?' done':''));row.append(node('span',todo.done?'✓':'','circle'),node('span',todo.title,'title'));if(todo.due)row.append(node('span',todo.due,'due'));$('todos').append(row);}
  $('count').textContent=`${state.todos.filter(t=>!t.done).length} items left`;$('view').textContent=`View: ${state.screen_shows}`;
  $('filter').hidden=visible.length===state.todos.length;$('filter').textContent=`Showing ${visible.length} of ${state.todos.length} tasks`;
  $('approvals').replaceChildren();for(const request of state.waiting_for_approval){const card=node('div',undefined,'approval');card.append(node('p',`The assistant asks to delete ${request.title}.`));for(const action of ['deny','approve']){const button=node('button',action==='approve'?'Approve':'Deny',action);button.disabled=true;if(frame.selection?.ids.includes(request.id)&&frame.selection.action===action)button.classList.add('selected');card.append(button);}$('approvals').append(card);}
  $('chat').replaceChildren();for(const message of frame.messages){const box=node('div',undefined,`message ${message.role}`);if(message.role!=='person-action')box.append(node('strong',message.role==='sam'?'Sam':'Assistant'));for(const [i,part] of message.text.split(/\*\*(.*?)\*\*/gs).entries()){const text=node(i%2?'b':'span',part);box.append(text);}$('chat').append(box);}$('chat').scrollTop=$('chat').scrollHeight;
  $('ending').hidden=!frame.end;$('ending').textContent=`Session complete. Recorded outcome: ${record.status}.`;
 }
 function advance(){if(index<frames.length-1){index++;render();}if(index===frames.length-1)pause();}
 function play(){if(timer){pause();return;}$('play').textContent='Pause';const tick=()=>{advance();if(index<frames.length-1)timer=setTimeout(tick,Number($('speed').value));};timer=setTimeout(tick,Number($('speed').value));}
 $('next').onclick=()=>{pause();advance();};$('previous').onclick=()=>{pause();index=Math.max(0,index-1);render();};$('restart').onclick=()=>{pause();index=0;render();};$('play').onclick=play;
 document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
 $('persona').append(node('strong',record.who),node('p',`Wants: ${record.wants}`));
 $('provenance').textContent=`Recorded ${record.recorded}. Scenario date: ${record.today}. Agent: ${record.agent_model}; persona: ${record.persona_model}.`;
 render();
}
if(typeof document!=='undefined')start().catch(error=>{$('event').textContent=error.message;document.querySelectorAll('nav button').forEach(b=>b.disabled=true);});
