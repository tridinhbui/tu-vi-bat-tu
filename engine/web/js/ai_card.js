// "Luận riêng" (told to readers as "suy luận sâu"): the readings written by the model (POST /api/me/deep, src/chat/deep.ts), not to be
// confused with the book-based "Đọc sâu (theo sách)". Three levels (owner, 2026-10-26): under a report chapter, mức 1 Luận riêng and mức 2
// Luận sâu of that chapter; at the top of the Tử Vi report, mức 3 Luận chuyên sâu of the whole chart. The model's chapters are fewer than
// the report's (src/interpret/chapters.ts groups Phụ Mẫu, Huynh Đệ, Tử Tức and Thiên Di, Nô Bộc, Tật Ách), so a grouped card sits under the
// last palace of its group. A written reading is replayed free; the chart's Cao cấp package writes every mức 1 chapter without xu
// (POST /api/me/deep/status says which are written, which are being written, and the price of each level).
import { esc } from './util.js';
import { COIN_SVG } from './account.js';

const AI_OF = {
  menh: 'menh', cong_danh: 'cong_danh', tai_bach: 'tai_bach', phu_the: 'phu_the', phuc_duc: 'phuc_duc', dien_trach: 'dien_trach',
  phu_mau: 'gia_dao', tat_ach: 'di_no_tat', van_han: 'van_han', 'bat_tu:nhat-chu': 'bat_tu',
};
const AI_TITLE = {
  menh: 'Mệnh, Thân và tính cách', cong_danh: 'Công danh', tai_bach: 'Tài Bạch', phu_the: 'Phu Thê', phuc_duc: 'Phúc Đức', dien_trach: 'Điền Trạch',
  gia_dao: 'Phụ Mẫu, Huynh Đệ và Tử Tức', di_no_tat: 'Thiên Di, Nô Bộc và Tật Ách', van_han: 'Đại hạn và tiểu hạn', bat_tu: 'Bát Tự',
};
const WHOLE = 'toan_bo';
const LEVEL = {
  1: { name: 'Luận riêng', what: 'đọc cả lá số cùng lúc và đi sâu hơn phần đối chiếu sách ở trên, khoảng 500–800 từ' },
  2: { name: 'Luận sâu', what: 'mô hình mạnh nhất lần theo mọi cung, Tứ Hóa và Bát Tự liên quan, đối chiếu hai hệ và đi qua từng đại hạn; khoảng 1.500–2.000 từ' },
  3: { name: 'Luận chuyên sâu', what: 'cả lá số qua nhiều bước: lập dàn ý trục và các chỗ giằng co, viết từng phần, tự kiểm từng câu với dữ kiện rồi bỏ câu không có căn cứ, sau cùng là phần mở đầu và mười năm tới; khoảng 8.000–12.000 từ' },
};
const keyOf = (level, id) => level === 1 ? id : `${level === 3 ? WHOLE : id}#${level}`;

/** The empty card for a report chapter ('' when the chapter has no reading of its own); initAiCards fills it. */
export function aiSlot(chapter) {
  const id = AI_OF[chapter];
  return id ? `<div class="ai-card" data-ai="${id}"><p class="eyebrow">Luận riêng · ${esc(AI_TITLE[id])}</p><div class="ai-body"></div></div>` : '';
}
/** The card for mức 3, the whole chart (top of the Tử Vi report). */
export const wholeSlot = () => `<div class="ai-card ai-whole" data-ai="${WHOLE}"><p class="eyebrow">Luận chuyên sâu · toàn lá số</p><div class="ai-body"></div></div>`;

const post = (path, body) => fetch(path, { method: 'POST', credentials: 'same-origin', headers: { 'content-type': 'application/json', 'x-tvbt': '1' }, body: JSON.stringify(body) });
const FIELDS = ['year', 'month', 'day', 'hour', 'minute', 'gender', 'tz', 'calendar', 'zi_rule', 'level', 'use_true_solar_time', 'longitude'];
const pick = r => Object.fromEntries(FIELDS.filter(k => r[k] !== undefined).map(k => [k, r[k]]));

// the model writes plain text with a few "## " headings, "- " lists and **bold**: escaped first, then only these marks become tags
function textHtml(t) {
  const inline = s => esc(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
  return t.split(/\n{2,}/).map(b => b.trim()).filter(Boolean).map(b => {
    const h = b.match(/^#{1,4}\s+(.*)$/);
    if (h && !b.includes('\n')) return `<h5>${inline(h[1])}</h5>`;
    const lines = b.split('\n');
    if (lines.every(l => /^\s*[-*•]\s+/.test(l))) return `<ul>${lines.map(l => `<li>${inline(l.replace(/^\s*[-*•]\s+/, ''))}</li>`).join('')}</ul>`;
    return `<p>${lines.map(inline).join('<br>')}</p>`;
  }).join('');
}

/** getReq(): the birth record of the chart on screen (null on a share link: no card is filled). */
export function initAiCards(getReq) {
  let me = null, key = '', status = null;
  const busy = new Set();
  const meReady = fetch('/api/auth/me', { credentials: 'same-origin' }).then(r => r.ok ? r.json() : null).then(j => { me = j; }).catch(() => { me = null; });
  const statusFor = async req => {
    const k = JSON.stringify(pick(req));
    if (k !== key || !status) {
      key = k;
      status = post('/api/me/deep/status', { birth: pick(req) }).then(r => r.ok ? r.json() : null).catch(() => null);
    }
    return status;
  };

  function button(st, id, level) {
    const k = keyOf(level, id), cost = Number(st.costs?.[level] ?? st.cost), L = LEVEL[level];
    const label = st.written.includes(k) ? `Đọc ${L.name} đã viết`
      : (st.writing || []).includes(k) ? `${L.name} đang được viết · bấm để xem`
      : st.admin ? `Mức ${level} · ${L.name} · admin (khách trả ${cost} xu)`
      : level === 1 && st.plan ? `Mức 1 · ${L.name} (đã gồm trong gói Cao cấp)`
      : `Mức ${level} · ${L.name} · ${COIN_SVG}<b>${cost}</b> xu`;
    return `<button type="button" class="btn btn-sm${st.written.includes(k) ? ' btn-ghost' : ''}" data-ai-go data-level="${level}">${label}</button>`;
  }

  async function fill(card) {
    card.dataset.ready = '1';
    const body = card.querySelector('.ai-body'), id = card.dataset.ai, req = getReq(), whole = id === WHOLE;
    if (!req) { card.hidden = true; return; }
    await meReady;
    const levels = whole ? [3] : [1, 2];
    const about = levels.map(l => `<b>Mức ${l} · ${LEVEL[l].name}</b>: ${LEVEL[l].what}.`).join(' ');
    if (!me?.user) {
      body.innerHTML = `<p class="small">Phần luận giải ở trên là đối chiếu sách, miễn phí. Luận riêng dùng suy luận sâu và tính xu. ${about}</p>
        <p><a class="btn btn-sm btn-ghost" href="/api/auth/google" data-pw-signin>Đăng nhập để dùng Luận riêng</a></p>`;
      return;
    }
    const st = await statusFor(req);
    if (!st) { card.hidden = true; return; }                                       // not available on this server
    const allWritten = levels.every(l => st.written.includes(keyOf(l, id)));
    body.innerHTML = `${allWritten ? '' : `<p class="small">${about} Chỉ dùng dữ kiện và luận giải đã có, không thêm sao hay nhận định mới. Viết một lần, đọc lại không tốn thêm; viết hỏng thì không bị tính.${whole ? ' Mất khoảng 5–8 phút: hãy giữ trang này mở. Nếu bị ngắt giữa chừng, xu được hoàn tự động sau khoảng 20 phút.' : ''}${!whole && !st.plan ? ' <a href="/bang-gia">Gói Cao cấp</a> gồm mức 1 mọi chương.' : ''}</p>`}
      <p class="ai-go">${levels.map(l => button(st, id, l)).join(' ')}</p><div class="ai-out"></div><p class="ai-msg small" role="status" aria-live="polite"></p>`;
  }

  async function write(card, level) {
    const req = getReq(), id = card.dataset.ai, k = `${id}#${level}`;
    if (!req || busy.has(k)) return;
    const btn = card.querySelector(`[data-ai-go][data-level="${level}"]`), msg = card.querySelector('.ai-msg'), outs = card.querySelector('.ai-out');
    let out = outs.querySelector(`.ai-text[data-level="${level}"]`);
    if (!out) { outs.insertAdjacentHTML('beforeend', `<div class="ai-text" data-level="${level}"><p class="eyebrow">Mức ${level} · ${LEVEL[level].name}</p><div class="ai-t"></div></div>`); out = outs.querySelector(`.ai-text[data-level="${level}"]`); }
    const t = out.querySelector('.ai-t');
    busy.add(k); btn.disabled = true; msg.className = 'ai-msg small';
    msg.textContent = level === 3 ? 'Đang bắt đầu, giữ trang này mở…' : 'Đang suy luận trên cả lá số rồi viết, có thể mất một đến ba phút…';
    let got = '', failed = false;
    try {
      const res = await post('/api/me/deep', { birth: pick(req), ...(level === 3 ? {} : { chapter: id }), level });
      if (res.status === 402) { const j = await res.json(); if (j.wallet) dispatchEvent(new CustomEvent('tvbt:wallet', { detail: j.wallet })); msg.innerHTML = `Cần ${Number(j.need)} xu, ví đang có ${Number(j.wallet?.coins ?? 0)} xu. <a href="/bang-gia#nap-xu">Nạp xu</a>`; msg.classList.add('err'); return; }
      if (res.status === 401) { msg.innerHTML = 'Phiên đăng nhập đã hết. <a href="/api/auth/google" data-pw-signin>Đăng nhập lại</a>'; msg.classList.add('err'); return; }
      if (res.status === 409) { msg.textContent = 'Bài này đang được viết (có thể ở một thẻ khác). Bấm lại sau ít phút để đọc, không bị tính thêm.'; return; }
      if (res.status === 503) { msg.textContent = 'Luận riêng đang tạm dừng. Bạn thử lại sau nhé.'; msg.classList.add('err'); return; }
      if (!res.ok || !res.body) throw new Error(String(res.status));
      const rd = res.body.getReader(), dec = new TextDecoder(); let buf = '';
      for (;;) {
        const { value, done } = await rd.read(); if (done) break;
        buf += dec.decode(value, { stream: true });
        let i; while ((i = buf.indexOf('\n\n')) >= 0) {
          const line = buf.slice(0, i); buf = buf.slice(i + 2);
          if (!line.startsWith('data: ')) continue;
          const ev = JSON.parse(line.slice(6));
          if (ev.type === 'delta') { got += ev.text; t.innerHTML = textHtml(got); msg.textContent = ''; }
          else if (ev.type === 'step') msg.textContent = ev.label + '…';
          else if (ev.type === 'error') { failed = true; msg.textContent = ev.message + (ev.refunded ? ' Lượt này không bị tính.' : ''); msg.classList.add('err'); }
          else if (ev.type === 'wallet') dispatchEvent(new CustomEvent('tvbt:wallet', { detail: ev.wallet }));
        }
      }
      if (got && !failed) { btn.remove(); if (!card.querySelector('[data-ai-go]')) card.querySelector('.ai-body > p.small:not(.ai-msg)')?.remove(); status = null; }
    } catch { msg.textContent = 'Mất kết nối khi đang viết. Bài vẫn được viết tiếp và lưu khi xong: bấm lại sau ít phút để đọc, không bị tính thêm.'; msg.classList.add('err'); }
    finally { busy.delete(k); if (btn.isConnected) btn.disabled = false; }
  }

  document.addEventListener('click', e => { const b = e.target.closest('.ai-card [data-ai-go]'); if (b) write(b.closest('.ai-card'), Number(b.dataset.level) || 1); });
  // a package bought on this page may now cover mức 1
  addEventListener('tvbt:unlocked', () => { status = null; });
  const scan = () => document.querySelectorAll('.ai-card:not([data-ready])').forEach(fill);
  new MutationObserver(scan).observe(document.body, { childList: true, subtree: true });
  scan();
}
