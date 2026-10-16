// The assistant chat scrolls in whole exchanges (what you said and the reply).
//
// One wheel step or trackpad flick moves to the next or previous exchange's top. An exchange
// taller than the box is paged through, a box-height at a time, so a long answer stays readable.
// When a new exchange arrives, it is placed at the top of the box (the spacer under it makes
// room). CSS scroll-snap could not do both: with long answers, a small wheel step snapped back.

const STEP_MS = 350;      // one gesture = one step; events inside this window are the same gesture
const OVERLAP = 40;       // px kept in view when paging through a tall exchange

function exchanges(box) {
  const top = (x) => x.getBoundingClientRect().top - box.getBoundingClientRect().top + box.scrollTop;
  return [...box.querySelectorAll('[class*="st-key-exchange-"]')].map((x) => ({ top: top(x), bottom: top(x) + x.offsetHeight }));
}

function target(box, down) {
  const ex = exchanges(box), cur = box.scrollTop, h = box.clientHeight;
  const max = box.scrollHeight - h;
  if (!ex.length) return cur;
  const i = Math.max(0, ex.findLastIndex((e) => e.top <= cur + 1));  // the exchange at the top of the box
  let t;
  if (down) {
    const tall = ex[i].bottom > cur + h + 1;  // part of this exchange is still below the box
    const next = ex[i + 1] ? ex[i + 1].top : null;
    if (tall) t = Math.min(cur + h - OVERLAP, next ?? ex[i].bottom - h + OVERLAP);
    else t = next ?? cur;                     // the newest, fully shown: nowhere further to go
  } else {
    const start = cur - ex[i].top > 1 ? ex[i].top : (ex[i - 1] ? ex[i - 1].top : 0);
    t = cur - start > h ? Math.max(start, cur - (h - OVERLAP)) : start;
  }
  return Math.max(0, Math.min(max, t));
}

function wire(box) {
  if (box.__unitScroll) return;
  box.__unitScroll = true;
  let busyUntil = 0;
  box.addEventListener('wheel', (e) => {
    e.preventDefault();
    box.__userScrolled = true;
    if (Date.now() < busyUntil || Math.abs(e.deltaY) < 4) return;
    busyUntil = Date.now() + STEP_MS;
    box.scrollTo({ top: target(box, e.deltaY > 0), behavior: 'smooth' });
  }, { passive: false });
}

// The input box is disabled while a reply is written, and a disabled box loses the focus; nothing
// gave it back, so every message meant a click on the box first. When a reply has arrived and the box
// is enabled again, the focus returns to it, unless the person is working elsewhere (a todo being
// edited, say): only from the page itself, or from the box.
function refocus(want) {
  if (window.__focusedFor === want) return true;
  const input = document.querySelector('[data-testid="stChatInputTextArea"]');
  if (!input || input.disabled) return false;          // not back yet: try again next frame
  const active = document.activeElement;
  if (!active || active === document.body || active === input) input.focus();
  window.__focusedFor = want;
  return true;
}

export default function ({ data }) {
  const want = data.exchanges;
  const started = Date.now();
  let box = null;
  let refocused = false;
  const pinNewest = !!want && window.__pinnedExchanges !== want;
  if (pinNewest) window.__pinnedExchanges = want;
  // Keep the newest at the top while the page settles (long answers above it finish laying out a
  // moment later), for 1.5 s or until the person scrolls. Any other rerun leaves the chat alone.
  const tick = () => {
    box = box || document.querySelector('.st-key-chat');
    if (box) {
      wire(box);
      if (pinNewest && !box.__userScrolled) {
        const all = box.querySelectorAll('[class*="st-key-exchange-"]');
        const newest = all.length === want ? all[want - 1] : null;  // by order: names can lag a rerun
        if (newest) {
          box.scrollTop = newest.getBoundingClientRect().top - box.getBoundingClientRect().top + box.scrollTop;
        }
      }
    }
    if (data.ready && want) refocused = refocused || refocus(want);
    if (Date.now() - started < 1500) requestAnimationFrame(tick);
    else if (box) box.__userScrolled = false;
  };
  if (pinNewest && document.querySelector('.st-key-chat')) document.querySelector('.st-key-chat').__userScrolled = false;
  requestAnimationFrame(tick);
}
