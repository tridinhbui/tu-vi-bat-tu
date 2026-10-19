// "Hỏi về lá số": a chat panel for the chart on screen. Needs sign-in; the server charges one free chat (or one coin) per message and
// streams the answer. Everything the model says is shown as text, never as HTML.
import { $ } from './util.js';

const post = (body) => fetch('/api/me/chat', { method: 'POST', credentials: 'same-origin', headers: { 'content-type': 'application/json', 'x-tvbt': '1' }, body: JSON.stringify(body) });
const pick = r => Object.fromEntries(['year', 'month', 'day', 'hour', 'minute', 'gender', 'tz', 'calendar', 'zi_rule', 'level', 'use_true_solar_time', 'longitude'].filter(k => r[k] !== undefined).map(k => [k, r[k]]));
const key = r => ['year', 'month', 'day', 'hour', 'minute', 'gender'].map(k => r[k]).join('-');
const CHAPTERS = [['menh', 'Mệnh, Thân và tính cách'], ['cong_danh', 'Công danh'], ['tai_bach', 'Tài Bạch'], ['dien_trach', 'Điền Trạch'], ['phu_the', 'Phu Thê'], ['phuc_duc', 'Phúc Đức'],
  ['gia_dao', 'Phụ Mẫu, Huynh Đệ và Tử Tức'], ['di_no_tat', 'Thiên Di, Nô Bộc và Tật Ách'], ['van_han', 'Đại hạn và tiểu hạn'], ['bat_tu', 'Bát Tự: tứ trụ và nhật chủ']];
const left = w => `${w.free.remaining} lượt miễn phí · ${w.coins} xu`;

export function initAsk(host, getReq) {
  host.innerHTML = `<button type="button" class="ask-fab" aria-expanded="false" aria-controls="ask-panel" hidden>Hỏi về lá số</button>
    <section class="ask-panel" id="ask-panel" role="dialog" aria-label="Hỏi về lá số" hidden>
      <header class="ask-h"><b>Hỏi về lá số</b><span class="ask-left muted small"></span><button type="button" class="ask-x" aria-label="Đóng">×</button></header>
      <div class="ask-deep"><select aria-label="Chương muốn đọc sâu">${CHAPTERS.map(([id, t]) => `<option value="${id}">${t}</option>`).join('')}</select><button type="button" class="btn btn-sm btn-ghost">Luận giải sâu · 20 xu</button></div>
      <div class="ask-log" aria-live="polite"></div>
      <p class="ask-note" hidden></p>
      <form class="ask-form"><textarea rows="1" maxlength="1500" placeholder="Ví dụ: Công danh của tôi mạnh ở đâu?" aria-label="Câu hỏi"></textarea><button class="btn btn-sm" type="submit">Gửi</button></form>
      <p class="ask-fine muted small">Trợ lý chỉ dựa vào lá số và bài luận giải của bạn. Đây là hệ biểu tượng truyền thống, không phải dự báo. Để trả lời, nội dung lá số và câu hỏi của bạn được gửi tới Anthropic (Claude); nội dung chat không được lưu trên Thiên Bàn.</p>
    </section>`;
  const fab = $('.ask-fab', host), panel = $('.ask-panel', host), log = $('.ask-log', host), note = $('.ask-note', host), form = $('.ask-form', host), ta = $('textarea', host), send = $('.ask-form .btn', host), leftEl = $('.ask-left', host);
  let me = null, wallet = null, busy = false, forKey = '', history = [];

  const say = (cls, text) => { const p = document.createElement('p'); p.className = 'ask-m ' + cls; p.textContent = text; log.appendChild(p); log.scrollTop = log.scrollHeight; return p; };
  const setNote = (html, text) => { note.hidden = !text && !html; note.replaceChildren(); if (text) note.textContent = text; if (html) note.append(html); };
  const lock = () => {
    ta.disabled = send.disabled = true;
    const a = document.createElement('span'); a.textContent = 'Bạn đã dùng hết lượt miễn phí tháng này. Lượt miễn phí được làm mới vào đầu tháng sau. Gói xu để chat thêm sẽ có sớm.';
    setNote(a);
  };
  const paint = () => {
    const signedOut = !me?.user;
    ta.disabled = send.disabled = busy || signedOut; deepBtn.disabled = deepSel.disabled = busy || signedOut; leftEl.textContent = wallet ? left(wallet) : '';
    if (signedOut) {
      const a = document.createElement('a'); a.href = '/api/auth/google'; a.textContent = 'Đăng nhập với Google';
      setNote(a); note.prepend('Đăng nhập để hỏi trợ lý, mỗi tháng có 10 lượt miễn phí. ');
    } else if (wallet && wallet.free.remaining <= 0 && wallet.coins < wallet.costs.chat) lock();
    else setNote(null, '');
  };
  async function load() {
    try { me = await (await fetch('/api/auth/me', { credentials: 'same-origin' })).json(); } catch { me = null; }
    if (me?.user) { try { const r = await fetch('/api/me/wallet', { credentials: 'same-origin' }); wallet = r.ok ? await r.json() : null; } catch { wallet = null; } }
    paint();
  }
  function reset() {
    const r = getReq(); const k = r ? key(r) : '';
    if (k === forKey) return; forKey = k; history = []; log.replaceChildren();
    if (k) say('ask-bot', 'Bạn muốn hỏi gì về lá số này? Mình sẽ giải thích dựa trên chính bài luận giải của bạn.');
  }
  const open = async () => { reset(); panel.hidden = false; fab.setAttribute('aria-expanded', 'true'); await load(); ta.focus(); };
  const close = () => { panel.hidden = true; fab.setAttribute('aria-expanded', 'false'); };
  fab.onclick = () => panel.hidden ? open() : close();
  $('.ask-x', host).onclick = close;
  addEventListener('keydown', e => { if (e.key === 'Escape' && !panel.hidden) close(); });
  ta.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); } });

  // the button shows only while a chart is on screen
  const sync = () => { const on = document.body.dataset.view === 'chart'; fab.hidden = !on; if (!on) close(); };
  new MutationObserver(sync).observe(document.body, { attributes: true, attributeFilter: ['data-view'] }); sync();

  /** Reads the server-sent events of one answer into `out`; shows an error line when the server reports one. */
  async function readStream(res, out) {
    let got = '', failed = false;
    const rd = res.body.getReader(), dec = new TextDecoder(); let buf = '';
    for (;;) {
      const { value, done } = await rd.read(); if (done) break;
      buf += dec.decode(value, { stream: true });
      let i; while ((i = buf.indexOf('\n\n')) >= 0) {
        const line = buf.slice(0, i); buf = buf.slice(i + 2);
        if (!line.startsWith('data: ')) continue;
        const ev = JSON.parse(line.slice(6));
        if (ev.type === 'delta') { got += ev.text; out.textContent = got; log.scrollTop = log.scrollHeight; }
        else if (ev.type === 'error') { failed = true; if (!got) out.remove(); say('ask-err', ev.message + (ev.refunded ? ' Lượt này không bị tính.' : '')); }
        else if (ev.type === 'done' && ev.truncated) out.textContent = got + ' …';
        else if (ev.type === 'wallet') { wallet = ev.wallet; dispatchEvent(new CustomEvent('tvbt:wallet', { detail: wallet })); }
      }
    }
    return { got, failed };
  }

  // "Luận giải sâu": one chapter written out in full by the model; costs coins once, then it is kept
  const deepBtn = $('.ask-deep .btn', host), deepSel = $('.ask-deep select', host);
  deepBtn.onclick = async () => {
    const req = getReq(); if (!req || busy) return;
    if (!me?.user) { paint(); return; }
    const title = deepSel.selectedOptions[0].textContent;
    busy = true; paint(); deepBtn.disabled = deepSel.disabled = true;
    say('ask-me', `Luận giải sâu: ${title}`); const out = say('ask-bot', 'Đang viết, khoảng nửa phút…');
    try {
      const res = await fetch('/api/me/deep', { method: 'POST', credentials: 'same-origin', headers: { 'content-type': 'application/json', 'x-tvbt': '1' }, body: JSON.stringify({ birth: pick(req), chapter: deepSel.value }) });
      if (res.status === 402) { const b = await res.json(); wallet = b.wallet; out.remove(); say('ask-err', `Luận giải sâu cần ${b.need} xu, bạn đang có ${b.wallet.coins} xu. Gói xu sẽ có sớm.`); }
      else if (res.status === 401) { me = null; out.remove(); }
      else if (!res.ok || !res.body) throw new Error(String(res.status));
      else { out.textContent = ''; const r = await readStream(res, out); if (!r.got && !r.failed) out.remove(); }
    } catch { out.remove(); say('ask-err', 'Không kết nối được. Bạn thử lại nhé.'); }
    busy = false; deepBtn.disabled = deepSel.disabled = false; paint();
  };

  form.onsubmit = async e => {
    e.preventDefault();
    const text = ta.value.trim(), req = getReq();
    if (!text || busy || !req || !me?.user) return;
    busy = true; paint(); ta.value = '';
    say('ask-me', text); const out = say('ask-bot', '…');
    const messages = [...history, { role: 'user', content: text }].slice(-19);
    let r = { got: '', failed: false };
    try {
      const res = await post({ birth: pick(req), messages });
      if (res.status === 402) { const b = await res.json(); wallet = b.wallet; out.remove(); lock(); busy = false; leftEl.textContent = wallet ? left(wallet) : ''; return; }
      if (res.status === 401) { me = null; out.remove(); busy = false; paint(); return; }
      if (!res.ok || !res.body) throw new Error(String(res.status));
      r = await readStream(res, out);
    } catch { r.failed = true; if (!r.got) out.remove(); say('ask-err', 'Không kết nối được. Bạn thử lại nhé.'); }
    const { got, failed } = r;
    if (got) history.push({ role: 'user', content: text }, { role: 'assistant', content: got });
    else if (!failed) out.remove();
    busy = false; paint();
  };
}
