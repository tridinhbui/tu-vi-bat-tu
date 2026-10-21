// Feedback bubble on every page (bottom left; the chart chat owns bottom right) and the visit ping for the admin statistics.
// Anyone can write, signed in or not. The thread key the server hands back stays in this browser; replies are polled.
// Self-contained: loads its own stylesheet, so a page only needs <script type="module" src="/js/feedback.js">.
const KEY = 'tvbt.fb.key', SEEN = 'tvbt.fb.seen', VID = 'tvbt.vid', HIT = 'tvbt.hit';
const store = {
  get: (k, s = localStorage) => { try { return s.getItem(k); } catch { return null; } },
  set: (k, v, s = localStorage) => { try { s.setItem(k, v); } catch { /* private mode: works for this page only */ } },
};
const api = (path, opts = {}) => fetch(path, { credentials: 'same-origin', cache: 'no-store', ...opts,
  headers: { 'x-tvbt': '1', 'content-type': 'application/json', ...(store.get(KEY) ? { 'x-feedback-key': store.get(KEY) } : {}), ...(opts.headers || {}) } });
const rid = () => [...crypto.getRandomValues(new Uint8Array(16))].map(b => b.toString(36).padStart(2, '0')).join('').slice(0, 24);

// One visit per tab session; the browser id only tells the server whether it has seen this browser today.
function ping() {
  if (store.get(HIT, sessionStorage)) return;
  let vid = store.get(VID); if (!vid) { vid = rid(); store.set(VID, vid); }
  store.set(HIT, '1', sessionStorage);
  api('/api/hit', { method: 'POST', body: JSON.stringify({ vid }), keepalive: true }).catch(() => {});
}

const ICON = '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5.5h16a1.5 1.5 0 0 1 1.5 1.5v9a1.5 1.5 0 0 1-1.5 1.5H10l-4.5 3.5V17.5H4A1.5 1.5 0 0 1 2.5 16V7A1.5 1.5 0 0 1 4 5.5z"/><path d="M7 10h10M7 13.5h6"/></svg>';
const fmtTime = t => new Date(t).toLocaleString('vi-VN', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' });

function mount() {
  const css = document.createElement('link'); css.rel = 'stylesheet'; css.href = '/css/feedback.css'; document.head.append(css);
  const host = document.createElement('div'); host.className = 'fb'; host.id = 'feedback';
  host.innerHTML = `<button type="button" class="fb-fab" aria-expanded="false" aria-controls="fb-panel" aria-label="Góp ý cho Thiên Bàn" title="Góp ý">${ICON}<span class="fb-fab-t">Góp ý</span><i class="fb-dot" hidden></i></button>
    <section class="fb-panel" id="fb-panel" role="dialog" aria-labelledby="fb-h" hidden>
      <header class="fb-h"><div><b id="fb-h">Góp ý cho Thiên Bàn</b><small>Chúng tôi đọc mọi tin nhắn và trả lời ngay tại đây.</small></div><button type="button" class="fb-x" aria-label="Đóng">×</button></header>
      <div class="fb-log" aria-live="polite"></div>
      <form class="fb-form"><label class="fb-sr" for="fb-ta">Tin nhắn góp ý</label><textarea id="fb-ta" rows="2" maxlength="2000" placeholder="Bạn thấy chỗ nào chưa ổn, hay muốn thêm gì?" required></textarea><button class="btn btn-sm fb-send" type="submit">Gửi</button></form>
      <p class="fb-fine">Không cần đăng nhập. Đừng gửi mật khẩu hay thông tin thẻ.</p>
    </section>`;
  document.body.append(host);
  const $ = s => host.querySelector(s);
  const fab = $('.fb-fab'), panel = $('.fb-panel'), log = $('.fb-log'), form = $('.fb-form'), ta = $('textarea'), send = $('.fb-send'), dot = $('.fb-dot');
  let msgs = [], timer = 0, busy = false;

  const lastId = () => msgs.length ? msgs[msgs.length - 1].id : 0;
  const lastAdminId = () => msgs.filter(m => m.author === 'admin').reduce((a, m) => Math.max(a, m.id), 0);
  function paint() {
    log.replaceChildren();
    if (!msgs.length) {
      const p = document.createElement('p'); p.className = 'fb-m fb-them';
      p.textContent = 'Xin chào! Bạn cứ nhắn góp ý, báo lỗi hay câu hỏi về Thiên Bàn. Câu trả lời sẽ hiện ở đây, kể cả khi bạn quay lại sau.';
      log.append(p);
    }
    for (const m of msgs) {
      const p = document.createElement('p'); p.className = 'fb-m ' + (m.author === 'admin' ? 'fb-them' : 'fb-me');
      p.textContent = m.body;
      const t = document.createElement('time'); t.textContent = (m.author === 'admin' ? 'Thiên Bàn · ' : '') + fmtTime(m.at); p.append(t);
      log.append(p);
    }
    log.scrollTop = log.scrollHeight;
    const unseen = lastAdminId() > Number(store.get(SEEN) || 0);
    if (!panel.hidden && unseen) store.set(SEEN, String(lastAdminId()));
    dot.hidden = panel.hidden ? !unseen : true;
  }
  function merge(list) { const have = new Set(msgs.map(m => m.id)); for (const m of list) if (!have.has(m.id)) msgs.push(m); msgs.sort((a, b) => a.id - b.id); }

  async function poll() {
    clearTimeout(timer);
    if (store.get(KEY) && !document.hidden) {
      try { const r = await api('/api/feedback?after=' + lastId()); if (r.ok) { const n = msgs.length; merge((await r.json()).messages); if (msgs.length !== n || !n) paint(); } } catch { /* offline */ }
    }
    if (store.get(KEY)) timer = setTimeout(poll, panel.hidden ? 60000 : 8000);
  }
  const open = () => { panel.hidden = false; fab.setAttribute('aria-expanded', 'true'); paint(); poll(); setTimeout(() => ta.focus(), 30); };
  const close = () => { panel.hidden = true; fab.setAttribute('aria-expanded', 'false'); paint(); poll(); };
  fab.onclick = () => panel.hidden ? open() : close();
  $('.fb-x').onclick = close;
  addEventListener('keydown', e => { if (e.key === 'Escape' && !panel.hidden) { close(); fab.focus(); } });
  document.addEventListener('visibilitychange', () => { if (!document.hidden) poll(); });
  ta.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); form.requestSubmit(); } });

  form.onsubmit = async e => {
    e.preventDefault();
    const body = ta.value.trim(); if (!body || busy) return;
    busy = true; send.disabled = true;
    try {
      const r = await api('/api/feedback', { method: 'POST', body: JSON.stringify({ body, page: location.pathname + location.hash }) });
      const j = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(r.status === 429 ? 'Bạn gửi hơi nhanh, đợi vài phút rồi gửi tiếp nhé.' : 'Chưa gửi được, bạn thử lại sau nhé.');
      if (j.key) store.set(KEY, j.key);
      msgs = []; merge(j.messages || []); ta.value = ''; paint(); poll();
    } catch (err) {
      const p = document.createElement('p'); p.className = 'fb-m fb-err'; p.textContent = err.message || 'Chưa gửi được, bạn thử lại sau nhé.'; log.append(p); log.scrollTop = log.scrollHeight;
    } finally { busy = false; send.disabled = false; }
  };
  poll();
}

ping();
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
