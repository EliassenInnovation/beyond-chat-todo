import renderTodos from './todo_view.js';
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
      frames.at(-1).exchangeComplete = true;
    }
  }
  add(record.final, 'End of the recorded session.', null, true);
  return frames;
}

// Next completes the current exchange, including preceding recorded approval actions.
export function nextExchange(frames, index) {
  for (let next = index + 1; next < frames.length; next++) {
    if (frames[next].exchangeComplete || frames[next].end) return next;
  }
  return frames.length - 1;
}

// Allow time to read each new message; Next bypasses the automatic wait.
export function frameDelay(frame) {
 if(frame.selection) return 2500;
 const words=(frame.messages.at(-1)?.text || '').split(/\s+/).length;
 return Math.max(4000, Math.min(45000, words * 300 + 1500));
}
const $=id=>document.getElementById(id);
const node=(tag,text,cls)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(cls)el.className=cls;return el;};
async function start(){
 const guideMode=document.body.dataset.guideMode==='true';
 const bar=document.querySelector('.guide-bar');
 bar.hidden=!guideMode;
 for(const link of bar.querySelectorAll('a'))if(!link.getAttribute('href')?.trim())link.hidden=true;
 if(guideMode){const font=document.createElement('link');font.rel='stylesheet';font.href='https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500&display=swap';document.head.append(font);}

 const response=await fetch('sam-recording.json');if(!response.ok)throw Error('Recording could not be loaded.');const record=await response.json();
 const styleResponse=await fetch('todo_view.css');if(!styleResponse.ok)throw Error('App styling could not be loaded.');const todoCss=await styleResponse.text();
 const root=$('todo-host').attachShadow({mode:'open'});const style=node('style',todoCss);root.append(style);const list=node('div');root.append(list);
 const frames=makeFrames(record);let index=0,timer=null,playing=false;
 function pause(){clearTimeout(timer);timer=null;playing=false;$('play').textContent=frames[index].end?'↻  Replay':'▷  Play';}
 function render(){const frame=frames[index],state=frame.state;
  renderTodos({parentElement:list,setTriggerValue:()=>{},data:{todos:state.todos,pending:state.waiting_for_approval,today:record.today,filter:state.screen_shows,only:state.todos.filter(t=>state.visible.includes(t.title)).map(t=>t.id),can_undo:index>1,can_redo:false}});
  list.inert=true; // Saved states cannot be edited or executed.
  if(frame.selection){const cards=list.querySelectorAll('.request');state.waiting_for_approval.forEach((request,i)=>{if(frame.selection.ids.includes(request.id))cards[i].querySelector('.'+frame.selection.action).classList.add('flash');});}
  $('chat').replaceChildren();
  for(const message of frame.messages){const box=node('div',undefined,'message '+message.role);const avatar=node('span',message.role==='sam'?'S':message.role==='assistant'?'':'✓','avatar');if(message.role==='assistant')avatar.innerHTML='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.8" aria-hidden="true"><rect x="5" y="6" width="14" height="14" rx="2"/><path d="M12 3v3M2 10v6M22 10v6M8 15h8"/><circle cx="9" cy="10" r="1"/><circle cx="15" cy="10" r="1"/></svg>';box.append(avatar);const body=node('div',undefined,'message-text');for(const paragraph of message.text.split(/\n\n/)){const p=node('p');for(const [i,part] of paragraph.split(/\*\*(.*?)\*\*/gs).entries())p.append(node(i%2?'b':'span',part));body.append(p);}box.append(body);$('chat').append(box);}
  const spacer=node('div');spacer.style.height='220px';spacer.setAttribute('aria-hidden','true');$('chat').append(spacer);
  // Start at the latest question, rather than the bottom of a long reply.
  const question=[...$('chat').querySelectorAll('.message.sam')].at(-1);
  if(question)$('chat').scrollTop=question.getBoundingClientRect().top-$('chat').getBoundingClientRect().top+$('chat').scrollTop;
  else $('chat').scrollTop=0;
  $('event').textContent=frame.end?'Session complete.':frame.selection?'Sam clicks Approve on the requests.':'';
  $('next').disabled=frame.end;$('play').disabled=false;if(frame.end)$('play').textContent='↻  Replay';
 }
 function advance(){if(index<frames.length-1){index++;render();}if(frames[index].end)pause();}
 function schedule(){timer=setTimeout(()=>{advance();if(playing)schedule();},frameDelay(frames[index]));}
 $('play').onclick=()=>{if(playing){pause();return;}if(frames[index].end){index=0;render();}playing=true;$('play').textContent='Ⅱ  Pause';schedule();};
 $('next').onclick=()=>{pause();index=nextExchange(frames,index);render();};
 document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
 $('persona').append(node('b',record.who),node('div','Wants: '+record.wants));render();
}
if(typeof document!=='undefined')start().catch(error=>{$('error').hidden=false;$('error').textContent=error.message;$('play').disabled=true;$('next').disabled=true;});
