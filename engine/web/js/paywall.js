// Lock card under a paid chapter the reader has not opened. The server already cut the chapter to its preview (src/billing/paywall.ts);
// this card only offers the ways to open it. Opening spends xu on the server (POST /api/me/unlock), then the report is drawn again.
import { esc } from './util.js';
import { COIN_SVG } from './account.js';

const post = (path, body) => fetch(path, { method: 'POST', credentials: 'same-origin', headers: { 'content-type': 'application/json', 'x-tvbt': '1' }, body: JSON.stringify(body) });

export function lockHtml(p) {
  const L = p?.locked;
  if (!L) return '';
  const left = Math.max(0, L.total - L.shown);
  const plans = L.signedIn
    ? `<div class="pw-plans">${L.plans.map(x => `<button type="button" class="btn btn-sm${x.id === 'chuong' ? '' : ' btn-ghost'}" data-plan="${esc(x.id)}"${x.chapter ? ` data-chapter="${esc(x.chapter)}"` : ''}>${esc(x.name)} · ${COIN_SVG}<b>${Number(x.coins)}</b> xu</button>`).join('')}</div>`
    : `<p><a class="btn btn-sm" href="/api/auth/google">Đăng nhập với Google để mở khóa</a></p>`;
  return `<div class="pw-lock" data-locked="${esc(L.chapter)}"><p class="eyebrow">Phần chuyên sâu</p>
    <p>Bạn đang đọc phần đầu của <b>${esc(L.title)}</b>${left ? `; còn ${left} đoạn nữa` : ''}. Mở trọn chương để đọc hết, kèm căn cứ từng câu và gợi ý hành động.</p>
    ${plans}<p class="small muted">Mở một lần cho lá số này, đọc lại không tốn thêm. <a href="/bang-gia">Xem bảng giá và nạp xu</a></p><p class="pw-msg small" role="status" aria-live="polite"></p></div>`;
}

/** Click handling for every lock card on the page. getReq(): the birth record of the chart on screen. */
export function initPaywall(getReq) {
  document.addEventListener('click', async e => {
    const b = e.target.closest('.pw-lock button[data-plan]'); if (!b) return;
    const card = b.closest('.pw-lock'), msg = card.querySelector('.pw-msg'), req = getReq();
    if (!req) return;
    card.querySelectorAll('button').forEach(x => { x.disabled = true; });
    msg.textContent = 'Đang mở khóa…'; msg.className = 'pw-msg small';
    try {
      const r = await post('/api/me/unlock', { birth: req, plan: b.dataset.plan, chapter: b.dataset.chapter });
      const j = await r.json().catch(() => ({}));
      if (j.wallet) dispatchEvent(new CustomEvent('tvbt:wallet', { detail: j.wallet }));
      if (r.status === 402) { msg.innerHTML = `Ví còn ${Number(j.wallet?.coins ?? 0)} xu, gói này cần ${Number(j.need)} xu. <a href="/bang-gia#nap-xu">Nạp xu</a>`; msg.classList.add('err'); return; }
      if (!r.ok) throw new Error(j.detail || String(r.status));
      msg.textContent = j.charged ? `Đã mở khóa, trừ ${j.charged} xu. Đang tải lại luận giải…` : 'Chương này đã mở sẵn. Đang tải lại…';
      dispatchEvent(new CustomEvent('tvbt:unlocked', { detail: { open: j.open, chapter: card.dataset.locked } }));
    } catch (x) { msg.textContent = 'Chưa mở khóa được: ' + x.message; msg.classList.add('err'); }
    finally { card.querySelectorAll('button').forEach(x => { x.disabled = false; }); }
  });
}
