// The card where the server held part of a chapter back (src/billing/paywall.ts). Two states:
//   guest  (not signed in, or reading through a share link): a blurred stand-in for the rest of the chapter and "Đăng nhập để đọc tiếp";
//   member: the chapter's "Đọc sâu (theo sách)" part, opened with xu (POST /api/me/unlock), then the report is drawn again.
// The held-back text never reached the browser: the blurred block is filler, not the reading. Prices and plan names come from the server
// (the lock's own plans, refreshed from GET /api/plans, the one source config.ts feeds).
import { esc } from './util.js';
import { COIN_SVG } from './account.js';

const post = (path, body) => fetch(path, { method: 'POST', credentials: 'same-origin', headers: { 'content-type': 'application/json', 'x-tvbt': '1' }, body: JSON.stringify(body) });
const RESUME = 'tvbt.resume';

let plans = null;
fetch('/api/plans', { cache: 'no-store' }).then(r => r.ok ? r.json() : null).then(j => { plans = j; }).catch(() => { /* the lock's own plans are enough */ });

// filler under the blur: the shape of a reading, none of its words
const FILLER = 'Phần tiếp theo của chương này được luận theo từng sao, từng cung và trang sách, câu nào cũng ghi căn cứ để bạn tự kiểm chứng khi đọc.';
const blur = n => `<div class="pw-blur" aria-hidden="true">${Array.from({ length: Math.min(3, Math.max(1, n)) }, () => `<p>${FILLER} ${FILLER}</p>`).join('')}</div>`;

/** The lock of a served chapter; a Bát Tự tab (chapter "bat_tu:<tab>") reads its own lock from `locks`. '' when nothing was held back. */
export function lockHtml(p) {
  const id = String(p?.chapter || ''), tab = id.startsWith('bat_tu:') && p.locks ? id.slice(7) : null;
  const L = tab ? p.locks[tab] : p?.locked;
  if (!L) return '';
  return L.tier === 'guest' ? guestCard(L) : memberCard(L);
}

function guestCard(L) {
  const left = Math.max(0, (L.total || 0) - (L.shown || 0));
  const what = left ? `còn ${left} đoạn luận chính${L.deep ? ` và phần Đọc sâu (theo sách)` : ''}` : L.deep ? 'còn phần Đọc sâu (theo sách)' : 'còn phần tiếp theo';
  const head = L.shared
    ? `<p>Đây là lá số được chia sẻ: người xem qua liên kết đọc phần đầu mỗi chương. <b>${esc(L.title)}</b> ${what}.</p>`
    : `<p>Bạn đang đọc phần đầu của <b>${esc(L.title)}</b>; ${what}.</p>`;
  const cta = L.shared
    ? `<a class="btn btn-sm" href="/api/auth/google">Đăng nhập để lập và đọc trọn lá số của bạn</a>`
    : `<a class="btn btn-sm" href="/api/auth/google" data-pw-signin>Đăng nhập để đọc tiếp</a>`;
  return `<div class="pw-lock pw-guest" data-tier="guest" data-locked="${esc(L.chapter)}">${blur(left || 1)}
    <div class="pw-over"><p class="eyebrow">Đọc tiếp</p>${head}<p>${cta}</p>
    <p class="small muted">Đăng nhập bằng Google, miễn phí: đọc trọn phần luận chính của mọi chương.${L.deep ? ' Phần Đọc sâu (theo sách) mở thêm bằng xu.' : ''} <a href="/#quyen-loi">Quyền lợi thành viên</a></p></div></div>`;
}

function memberCard(L) {
  const byId = Object.fromEntries((plans?.plans || []).map(x => [x.id, x]));
  const tag = plans?.placeholder ? ` <span class="pw-tag">${esc(plans.placeholderLabel || 'giá tạm')}</span>` : '';
  const buttons = (L.plans || []).map(x => {
    const P = byId[x.id] || x;
    return `<button type="button" class="btn btn-sm${x.id === 'chuong' ? '' : ' btn-ghost'}" data-plan="${esc(x.id)}"${x.chapter ? ` data-chapter="${esc(x.chapter)}"` : ''} title="${esc(P.blurb || '')}">${esc(P.name || x.name)} · ${COIN_SVG}<b>${Number(P.coins ?? x.coins)}</b> xu</button>`;
  }).join('');
  return `<div class="pw-lock pw-deep" data-tier="member" data-locked="${esc(L.chapter)}"><p class="eyebrow">Đọc sâu (theo sách)</p>
    <p><b>${esc(L.title)}</b> còn ${Number(L.deep) || ''} đoạn Đọc sâu: vì sao có kết luận, tổ hợp sao hỗ trợ, yếu tố làm mạnh hay yếu, kèm trang sách. Phần này viết theo luật từ sách, không phải AI.</p>
    ${buttons ? `<div class="pw-plans">${buttons}</div>` : ''}<p class="small muted">Mở một lần cho lá số này, đọc lại không tốn thêm.${tag} <a href="/bang-gia">Xem bảng giá và nạp xu</a></p><p class="pw-msg small" role="status" aria-live="polite"></p></div>`;
}

/** Click handling for every lock card on the page. getReq(): the birth record of the chart on screen (null on a share link). */
export function initPaywall(getReq) {
  document.addEventListener('click', async e => {
    // signing in from a guest card: the chart on screen is drawn again when the reader comes back (app.js reads RESUME)
    const s = e.target.closest('a[data-pw-signin]');
    if (s) { const req = getReq(); if (req) try { sessionStorage.setItem(RESUME, JSON.stringify(req)); } catch { /* storage unavailable */ } return; }
    const b = e.target.closest('.pw-lock button[data-plan]'); if (!b) return;
    const card = b.closest('.pw-lock'), msg = card.querySelector('.pw-msg'), req = getReq();
    if (!req) return;
    card.querySelectorAll('button').forEach(x => { x.disabled = true; });
    msg.textContent = 'Đang mở phần Đọc sâu…'; msg.className = 'pw-msg small';
    try {
      const r = await post('/api/me/unlock', { birth: req, plan: b.dataset.plan, chapter: b.dataset.chapter });
      const j = await r.json().catch(() => ({}));
      if (j.wallet) dispatchEvent(new CustomEvent('tvbt:wallet', { detail: j.wallet }));
      if (r.status === 402) { msg.innerHTML = `Ví còn ${Number(j.wallet?.coins ?? 0)} xu, gói này cần ${Number(j.need)} xu. <a href="/bang-gia#nap-xu">Nạp xu</a>`; msg.classList.add('err'); return; }
      if (r.status === 401) { msg.innerHTML = 'Phiên đăng nhập đã hết. <a href="/api/auth/google" data-pw-signin>Đăng nhập lại</a>'; msg.classList.add('err'); return; }
      if (!r.ok) throw new Error(j.detail || String(r.status));
      msg.textContent = j.charged ? `Đã mở, trừ ${j.charged} xu. Đang tải lại luận giải…` : 'Phần này đã mở sẵn. Đang tải lại…';
      dispatchEvent(new CustomEvent('tvbt:unlocked', { detail: { open: j.open, chapter: card.dataset.locked } }));
    } catch (x) { msg.textContent = 'Chưa mở được: ' + x.message; msg.classList.add('err'); }
    finally { card.querySelectorAll('button').forEach(x => { x.disabled = false; }); }
  });
}

/** The chart a guest was reading before signing in, once: app.js draws it again on load. */
export function takeResume() {
  try { const v = sessionStorage.getItem(RESUME); sessionStorage.removeItem(RESUME); return v ? JSON.parse(v) : null; } catch { return null; }
}
