// "Hỏi Bát Bát": the AI chat on every page, a floating button bottom right (the feedback bubble owns bottom left).
// Self-contained like feedback.js: a page only needs <script type="module" src="/js/ask.js">; the stylesheet is loaded here.
// What it talks about: the chart on screen (home page; app.js registers it through initAsk), else one of the member's saved charts (a
// compact picker, "Tôi" first, then the most recent), else general questions. Anyone can open it; sending needs sign-in, and the server
// charges per message (free ones first). Everything the model says is shown as text, never as HTML.
import { avatar } from './guides.js';

const FIELDS = ['year', 'month', 'day', 'hour', 'minute', 'gender', 'tz', 'calendar', 'zi_rule', 'level', 'use_true_solar_time', 'longitude'];
const pick = r => Object.fromEntries(FIELDS.filter(k => r[k] !== undefined).map(k => [k, r[k]]));
const key = r => ['year', 'month', 'day', 'hour', 'minute', 'gender'].map(k => r[k]).join('-');
const two = n => String(n).padStart(2, '0');
const born = r => `${two(r.day)}/${two(r.month)}/${r.year}`;
const CHAPTERS = [['menh', 'Mệnh, Thân và tính cách'], ['cong_danh', 'Công danh'], ['tai_bach', 'Tài Bạch'], ['dien_trach', 'Điền Trạch'], ['phu_the', 'Phu Thê'], ['phuc_duc', 'Phúc Đức'],
  ['gia_dao', 'Phụ Mẫu, Huynh Đệ và Tử Tức'], ['di_no_tat', 'Thiên Di, Nô Bộc và Tật Ách'], ['van_han', 'Đại hạn và tiểu hạn'], ['bat_tu', 'Bát Tự: tứ trụ và nhật chủ']];
// 503: the server has no model key; nothing was charged
const OFF = 'Bát Bát chưa được bật trên máy chủ. Lượt này không bị tính.';
const LOST = 'Không kết nối được. Bạn thử lại nhé.';
const chip = w => `${w.free.remaining} câu miễn phí hôm nay · ${Number(w.coins).toLocaleString('vi-VN')} xu`;
const G_ICON = '<svg viewBox="0 0 18 18" width="16" height="16" aria-hidden="true"><path fill="#4285F4" d="M17.6 9.2c0-.6-.1-1.2-.2-1.7H9v3.3h4.8a4.1 4.1 0 0 1-1.8 2.7v2.2h2.9c1.7-1.6 2.7-3.9 2.7-6.5z"/><path fill="#34A853" d="M9 18c2.4 0 4.5-.8 6-2.2l-2.9-2.2c-.8.5-1.8.9-3.1.9-2.4 0-4.4-1.6-5.1-3.8H.9v2.3A9 9 0 0 0 9 18z"/><path fill="#FBBC05" d="M3.9 10.7a5.4 5.4 0 0 1 0-3.4V5H.9a9 9 0 0 0 0 8z"/><path fill="#EA4335" d="M9 3.6c1.3 0 2.5.5 3.4 1.3l2.6-2.6A9 9 0 0 0 .9 5l3 2.3C4.6 5.2 6.6 3.6 9 3.6z"/></svg>';

let getChart = () => null, ui = null;

/** The home page registers the chart on screen (null while none, or for a shared chart that is not the viewer's). */
export function initAsk(getReq) { getChart = getReq; mount(); ui.sync(); }

function el(tag, cls, text) { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; }

function mount() {
  if (ui) return;
  const root = el('div', 'ask'); root.id = 'ask';
  // hidden until its stylesheet is in, so the button never flashes unstyled
  if (!document.querySelector('link[href="/css/ask.css"]')) {
    const css = el('link'); css.rel = 'stylesheet'; css.href = '/css/ask.css'; root.hidden = true;
    css.onload = css.onerror = () => { root.hidden = false; }; document.head.append(css);
  }
  root.innerHTML = `<button type="button" class="ask-fab" aria-expanded="false" aria-controls="ask-panel" aria-label="Hỏi Bát Bát">${avatar('bat', 34, true)}<span class="ask-fab-t">Hỏi Bát Bát</span></button>
    <section class="ask-panel" id="ask-panel" role="dialog" aria-labelledby="ask-title" hidden>
      <header class="ask-h">${avatar('bat', 38, true)}<div class="ask-ht"><b id="ask-title">Hỏi Bát Bát</b><span class="ask-left"></span></div><a class="ask-buy" href="/bang-gia#nap-xu" hidden>Nạp xu</a><button type="button" class="ask-x" aria-label="Đóng">×</button></header>
      <div class="ask-ctx" hidden><label for="ask-pick">Hỏi về</label><select id="ask-pick"></select></div>
      <div class="ask-deep" hidden><select aria-label="Chương muốn viết Luận riêng">${CHAPTERS.map(([id, t]) => `<option value="${id}">${t}</option>`).join('')}</select><button type="button" class="btn btn-sm btn-ghost">Luận riêng · 20 xu</button></div>
      <div class="ask-log" aria-live="polite"></div>
      <div class="ask-note" hidden></div>
      <form class="ask-form"><label class="ask-sr" for="ask-ta">Câu hỏi</label><textarea id="ask-ta" rows="1" maxlength="1500" placeholder="Hỏi Bát Bát…"></textarea><button class="btn btn-sm" type="submit">Gửi</button></form>
      <p class="ask-fine"></p>
    </section>`;
  document.body.append(root);
  const $ = s => root.querySelector(s);
  const fab = $('.ask-fab'), panel = $('.ask-panel'), log = $('.ask-log'), note = $('.ask-note'), form = $('.ask-form'), ta = $('textarea'), send = $('.ask-form .btn'),
    leftEl = $('.ask-left'), buy = $('.ask-buy'), ctx = $('.ask-ctx'), picker = $('#ask-pick'), deepRow = $('.ask-deep'), deepBtn = $('.ask-deep .btn'), deepSel = $('.ask-deep select'), fine = $('.ask-fine');

  let me = null, wallet = null, saved = null, busy = false, loaded = false, history = [], sel = 'general', chosen = false, convKey = '', screenKey = null;

  // ---------- what the chat is about ----------
  const onScreen = () => document.body.dataset.view === 'chart' ? getChart() : null;
  /** Saved charts: "Tôi" first, then the most recent (the server lists newest first). */
  const sortedSaved = () => (saved || []).map((c, i) => [c, i]).sort((a, b) => (b[0].rel === 'Tôi') - (a[0].rel === 'Tôi') || a[1] - b[1]).map(x => x[0]);
  function targets() {
    const out = [], r = onScreen();
    if (r) out.push({ v: 'screen', t: 'Lá số đang xem', req: r });
    for (const c of sortedSaved()) out.push({ v: 'id:' + c.id, t: `${c.label} · ${born(c.req)}`, label: c.label, id: c.id, req: c.req });
    out.push({ v: 'general', t: 'Câu hỏi chung' });
    return out;
  }
  const current = () => targets().find(t => t.v === sel) || { v: 'general' };

  function greet() {
    const t = current(), p = botSay('');
    if (t.v === 'screen') p.textContent = 'Bạn muốn hỏi gì về lá số này?';
    else if (t.id) p.textContent = `Bạn muốn hỏi gì về lá số “${t.label}”?`;
    else {
      p.textContent = 'Chào bạn, mình là Bát Bát. Bạn hỏi gì về Tử Vi, Bát Tự cũng được.';
      if (me?.user && saved && !saved.length) {
        const a = el('a', '', 'Lập lá số'); a.href = '/#lap-la-so';
        p.append(' ', a, ' và lưu lại để hỏi về chính lá số của bạn.');
      }
    }
  }
  /** Rebuilds the picker. Until the reader picks, the subject is the default: the chart on screen, else the first saved chart, else general.
   *  A new chart on screen (or leaving it) brings the default back. Starts a new conversation when the subject changed. */
  function sync() {
    const list = targets(), r = onScreen(), k = r ? key(r) : '';
    if (k !== screenKey) { chosen = false; screenKey = k; }
    if (!chosen || !list.some(t => t.v === sel)) sel = list[0].v;
    picker.replaceChildren(...list.map(t => { const o = el('option', '', t.t); o.value = t.v; return o; }));
    picker.value = sel;
    ctx.hidden = list.length < 2;
    const t = current(), conv = t.v === 'screen' ? 'screen:' + k : t.v;
    deepRow.hidden = !t.req;
    fine.textContent = t.req ? 'Trả lời dựa trên lá số của bạn.' : 'Bát Bát trả lời.';
    if (conv !== convKey) { convKey = conv; history = []; log.replaceChildren(); greet(); }
  }
  picker.onchange = () => { sel = picker.value; chosen = true; sync(); if (!ta.disabled) ta.focus(); };

  // ---------- messages ----------
  function botSay(text, cls = '') {
    const row = el('div', 'ask-row' + (cls ? ' ' + cls : '')); row.innerHTML = avatar('bat', 28, true);
    const p = el('p', 'ask-m ask-bot', text); row.append(p); log.append(row); log.scrollTop = log.scrollHeight; return p;
  }
  const meSay = text => { const p = el('p', 'ask-m ask-me', text); log.append(p); log.scrollTop = log.scrollHeight; return p; };
  const errSay = text => { const p = el('p', 'ask-m ask-err', text); log.append(p); log.scrollTop = log.scrollHeight; return p; };
  const drop = p => (p.closest('.ask-row') || p).remove();
  const setNote = (...parts) => { note.replaceChildren(...parts); note.hidden = !parts.length; };

  const locked = () => wallet && wallet.free.remaining <= 0 && wallet.coins < wallet.costs.chat;
  function paint() {
    const guest = loaded && !me?.user;
    ta.disabled = send.disabled = busy || !me?.user;
    deepBtn.disabled = deepSel.disabled = busy || !me?.user;
    leftEl.textContent = me?.user && wallet ? chip(wallet) : '';
    if (wallet) deepBtn.textContent = `Luận riêng · ${wallet.costs.deep} xu`;
    buy.hidden = !me?.user;
    if (guest) {
      const a = el('a', 'btn btn-sm ask-google'); a.href = '/api/auth/google'; a.innerHTML = G_ICON; a.append('Đăng nhập với Google');
      setNote(el('span', '', 'Đăng nhập để hỏi Bát Bát.'), a);
    } else if (locked()) {
      const a = el('a', '', 'Nạp xu'), line = el('span', '', 'Hết câu miễn phí hôm nay. '); a.href = '/bang-gia#nap-xu';
      line.append(a, ` để hỏi tiếp: mỗi lần nạp có ${wallet.pass?.days ?? 30} ngày chat, tới ${wallet.pass?.perDay ?? 30} câu mỗi ngày.`);
      setNote(line);
      ta.disabled = send.disabled = true;
    } else setNote();
  }
  const setWallet = w => { wallet = { ...(wallet || {}), ...w }; dispatchEvent(new CustomEvent('tvbt:wallet', { detail: wallet })); };

  async function load() {
    try { me = await (await fetch('/api/auth/me', { credentials: 'same-origin' })).json(); } catch { me = null; }
    loaded = true;
    if (me?.user) {
      const get = p => fetch(p, { credentials: 'same-origin' }).then(r => r.ok ? r.json() : null).catch(() => null);
      const [w, c] = await Promise.all([get('/api/me/wallet'), get('/api/me/charts')]);
      wallet = w; saved = c?.charts ?? saved ?? [];
    }
    sync(); paint();
  }

  // ---------- open and close ----------
  const open = async () => {
    panel.hidden = false; fab.setAttribute('aria-expanded', 'true'); document.documentElement.classList.add('ask-open');
    if (loaded) { sync(); paint(); }
    await load();
    (ta.disabled ? $('.ask-x') : ta).focus();
  };
  const close = () => { panel.hidden = true; fab.setAttribute('aria-expanded', 'false'); document.documentElement.classList.remove('ask-open'); };
  fab.onclick = () => panel.hidden ? open() : close();
  $('.ask-x').onclick = () => { close(); fab.focus(); };
  addEventListener('keydown', e => { if (e.key === 'Escape' && !panel.hidden) { close(); fab.focus(); } });
  ta.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); } });
  ta.addEventListener('input', () => { ta.style.height = 'auto'; ta.style.height = Math.min(ta.scrollHeight, 120) + 'px'; });
  // the home page switches views (form, chart, account) without reloading: keep the subject in step
  new MutationObserver(() => { if (!panel.hidden) sync(); }).observe(document.body, { attributes: true, attributeFilter: ['data-view'] });

  /** Reads the server-sent events of one answer into `out`; shows an error line when the server reports one. */
  async function readStream(res, out) {
    let got = '', failed = false, buf = '';
    const rd = res.body.getReader(), dec = new TextDecoder();
    for (;;) {
      const { value, done } = await rd.read(); if (done) break;
      buf += dec.decode(value, { stream: true });
      let i; while ((i = buf.indexOf('\n\n')) >= 0) {
        const line = buf.slice(0, i); buf = buf.slice(i + 2);
        if (!line.startsWith('data: ')) continue;
        const ev = JSON.parse(line.slice(6));
        if (ev.type === 'delta') { got += ev.text; out.textContent = got; log.scrollTop = log.scrollHeight; }
        else if (ev.type === 'error') { failed = true; if (!got) drop(out); errSay(ev.message + (ev.refunded ? ' Lượt này không bị tính.' : '')); }
        else if (ev.type === 'done' && ev.truncated) out.textContent = got + ' …';
        else if (ev.type === 'wallet') setWallet(ev.wallet);
      }
    }
    return { got, failed };
  }
  const subject = t => t.v === 'screen' ? { birth: pick(t.req) } : t.id ? { chart_id: t.id } : {};

  form.onsubmit = async e => {
    e.preventDefault();
    const text = ta.value.trim(), t = current();
    if (!text || busy || !me?.user) return;
    busy = true; paint(); ta.value = ''; ta.style.height = '';
    meSay(text); const out = botSay('…');
    const messages = [...history, { role: 'user', content: text }].slice(-19);
    let r = { got: '', failed: false };
    try {
      const res = await fetch('/api/me/chat', { method: 'POST', credentials: 'same-origin', headers: { 'content-type': 'application/json', 'x-tvbt': '1' }, body: JSON.stringify({ ...subject(t), messages }) });
      if (res.status === 402) { const b = await res.json(); drop(out); setWallet(b.wallet); }
      else if (res.status === 401) { me = null; drop(out); }
      else if (res.status === 404) { r.failed = true; drop(out); errSay('Không tìm thấy lá số này trong tài khoản. Bạn chọn lá số khác nhé.'); saved = null; load(); }
      else if (res.status === 503) { r.failed = true; drop(out); errSay(OFF); }
      else if (!res.ok || !res.body) throw new Error(String(res.status));
      else r = await readStream(res, out);
    } catch { r.failed = true; if (!r.got) drop(out); errSay(LOST); }
    if (r.got) history.push({ role: 'user', content: text }, { role: 'assistant', content: r.got });
    else if (!r.failed && out.isConnected) drop(out);
    busy = false; paint();
    if (!ta.disabled) ta.focus();
  };

  // "Luận riêng" (suy luận sâu; not to be confused with the book-based "Đọc sâu (theo sách)"): one chapter written in full by the model; coins once, then kept
  deepBtn.onclick = async () => {
    const t = current(); if (!t.req || busy || !me?.user) return;
    const title = deepSel.selectedOptions[0].textContent;
    busy = true; paint();
    meSay(`Luận riêng: ${title}`); const out = botSay('Đang suy luận trên cả lá số rồi viết, có thể mất một đến hai phút…');
    try {
      const res = await fetch('/api/me/deep', { method: 'POST', credentials: 'same-origin', headers: { 'content-type': 'application/json', 'x-tvbt': '1' }, body: JSON.stringify({ birth: pick(t.req), chapter: deepSel.value }) });
      if (res.status === 402) { const b = await res.json(); setWallet(b.wallet); drop(out); errSay(`Cần ${b.need} xu, bạn đang có ${b.wallet.coins} xu.`); }
      else if (res.status === 401) { me = null; drop(out); }
      else if (res.status === 503) { drop(out); errSay(OFF); }
      else if (!res.ok || !res.body) throw new Error(String(res.status));
      else { out.textContent = ''; const r = await readStream(res, out); if (!r.got && !r.failed && out.isConnected) drop(out); }
    } catch { if (out.isConnected) drop(out); errSay(LOST); }
    busy = false; paint();
  };

  ui = { sync: () => { if (!panel.hidden) sync(); } };

  // back from the older Stripe flow (/?paid=1): the webhook may land a few seconds after the redirect, so look at the wallet a few times
  const paid = new URLSearchParams(location.search).get('paid');
  if (paid !== null) {
    window.history.replaceState(null, '', location.pathname + location.hash);
    if (paid === '1') (async () => {
      await open(); const before = wallet?.coins ?? 0;
      botSay('Cảm ơn bạn! Đang cộng xu vào tài khoản…');
      for (let i = 0; i < 8; i++) {
        await new Promise(r => setTimeout(r, 2500)); await load();
        if ((wallet?.coins ?? 0) > before) { botSay(`Đã cộng xu. Bạn có ${wallet.coins} xu.`); setWallet(wallet); return; }
      }
      botSay('Thanh toán đã ghi nhận nhưng xu chưa hiện. Bạn tải lại trang sau ít phút nhé.');
    })();
  }
}

mount();
