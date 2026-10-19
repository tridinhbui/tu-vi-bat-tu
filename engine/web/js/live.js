// Live counters on the landing page. The numbers come from /api/stats and are re-read while the page is open and visible;
// when one grows it counts up and flashes. Nothing here invents a number: if the server has not reported a change, nothing moves.
const fmt = n => n.toLocaleString('vi-VN');
const POLL_MS = 12000;
const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;

function tween(el, from, to) {
  if (calm || from === to) { el.textContent = fmt(to); return; }
  const t0 = performance.now(), dur = Math.min(900, 300 + (to - from) * 60);
  const step = t => {
    const k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3);
    el.textContent = fmt(Math.round(from + (to - from) * e));
    if (k < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

export function initLive(host) {
  if (!host) return;
  const els = Object.fromEntries([...host.querySelectorAll('[data-stat]')].map(e => [e.dataset.stat, e]));
  let shown = null, timer = 0;

  function show(s) {
    if (!shown) {                                        // first reading: count up from zero once, no flash
      shown = { charts: 0, users: 0 };
      host.hidden = false;
    }
    for (const k of ['charts', 'users']) {
      if (s[k] === shown[k]) continue;
      const grew = shown[k] > 0 && s[k] > shown[k];
      tween(els[k], shown[k], s[k]);
      if (grew && !calm) { const item = els[k].parentElement; item.classList.remove('bump'); void item.offsetWidth; item.classList.add('bump'); }
      shown[k] = s[k];
    }
  }
  async function poll() {
    clearTimeout(timer);
    if (!document.hidden) {
      try { const r = await fetch('/api/stats', { cache: 'no-store' }); if (r.ok) show(await r.json()); } catch { /* offline: keep what is shown */ }
    }
    timer = setTimeout(poll, POLL_MS);
  }
  document.addEventListener('visibilitychange', () => { if (!document.hidden) poll(); });
  poll();
}
