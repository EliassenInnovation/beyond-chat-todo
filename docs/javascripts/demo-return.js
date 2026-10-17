// Keep the guide's reading position in this tab, not in a shared browser profile.
(() => {
  const key = 'todo-guide-return';
  const read = () => { try { return JSON.parse(sessionStorage.getItem(key)); } catch { return null; } };
  const save = value => { try { sessionStorage.setItem(key, JSON.stringify(value)); return true; } catch { return false; } };
  document.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const target = new URL(link.href, location.href);
    if (target.origin === location.origin && target.pathname.endsWith('/demos/persona-replay.html')) {
      save({url: location.href, x: scrollX, y: scrollY, restore: false});
    } else if (link.matches('.guide-back')) {
      const saved = read();
      if (!saved) return;
      const origin = new URL(saved.url, location.href);
      if (origin.origin !== location.origin || origin.pathname.endsWith('/demos/persona-replay.html')) return;
      if (save({...saved, restore: true})) { event.preventDefault(); location.assign(saved.url); }
    }
  });
  async function restore() {
    const saved = read();
    if (!saved?.restore || saved.url !== location.href) return;
    // Wait for page layout before restoring, including the guide's local fonts and images.
    if (document.readyState !== 'complete') await new Promise(resolve => window.addEventListener('load', resolve, {once:true}));
    if (document.fonts) await document.fonts.ready;
    requestAnimationFrame(() => requestAnimationFrame(() => {
      scrollTo(saved.x, saved.y);
      save({...saved, restore:false});
    }));
  }
  window.addEventListener('pageshow', restore);
  restore();
})();
