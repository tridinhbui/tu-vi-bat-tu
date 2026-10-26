// Pricing page (/bang-gia): packages and coin packs from GET /api/plans (src/billing/config.ts is the one source of prices), buying
// coins (Stripe or VNPAY), discount and gift codes, and the wallet history. Prices are decided on the server; this page only shows them.
import { COIN_SVG } from './account.js';
import { esc } from './util.js';

const $ = s => document.querySelector(s);
const api = (path, opts = {}) => fetch(path, { credentials: 'same-origin', cache: 'no-store', ...opts, headers: { 'x-tvbt': '1', 'content-type': 'application/json', ...(opts.headers || {}) } });
const vnd = n => `${Number(n).toLocaleString('vi-VN')}đ`;
const xu = n => `${COIN_SVG}<b>${Number(n).toLocaleString('vi-VN')}</b> xu`;
const when = t => new Date(t).toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh', hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit', year: 'numeric' });
const say = (el, text, cls = '') => { el.textContent = text; el.className = 'cm-msg' + (cls ? ' ' + cls : ''); };

let plans = null, me = null, discount = null;

async function boot() {
  try { plans = await (await fetch('/api/plans', { cache: 'no-store' })).json(); } catch { $('#cm-plans').textContent = 'Chưa tải được bảng giá.'; return; }
  try { me = await (await fetch('/api/auth/me', { credentials: 'same-origin' })).json(); } catch { me = null; }
  // who is signed in, and the sign-in button, are in the site header (js/nav.js)
  // the page never describes a lock the server does not apply: with the paywall off (TVBT_PAYWALL), every chapter is open and it says so
  const notes = [plans.placeholder && `<b>${esc(plans.placeholderLabel)}.</b> Các mức giá trên trang này đang là giá tạm để thử hệ thống, chưa phải giá bán chính thức.`,
    !plans.paywall && 'Mọi chương luận giải đối chiếu sách, kể cả phần Đọc sâu, đều miễn phí cho mọi người; xu chỉ dùng cho Luận riêng và các câu hỏi Bát Bát thêm.'].filter(Boolean);
  if (notes.length) { const b = $('#cm-placeholder'); b.innerHTML = notes.join(' '); b.hidden = false; }
  $('#cmp-chat-free').textContent = `${plans.freeMessagesPerDay ?? 2} câu mỗi ngày`;
  $('#cmp-chat-pro').textContent = `sau mỗi lần nạp hoặc gói Cao cấp: ${plans.topupChat?.days ?? 30} ngày chat (tới ${plans.topupChat?.perDay ?? 30} câu/ngày); thêm câu: ${plans.costs.chat} xu`;
  $('#cmp-ai').textContent = `${plans.costs.deep} xu một chương`;
  paintPlans(); paintPacks(); paintHistory();
  if (new URLSearchParams(location.search).get('paid') === '0') say($('#cm-pay-msg'), 'Bạn đã dừng thanh toán; chưa có khoản nào bị trừ.');
}

// what each package holds, beside its blurb (config.ts): the three Tử Vi / Bát Tự ones are nested, so each card names what it adds;
// Chiêm tinh stands apart (a Western birth has a place, so it is bought for that chart)
const PLAN_POINTS = {
  van_nam: ['Đại hạn, tiểu hạn, lưu niên Tử Vi', 'Đại vận, Lưu niên Bát Tự', 'Trọn luận chính và Đọc sâu (theo sách)'],
  tron_bo: ['Mười hai cung, Tổng luận, mọi mục Bát Tự', 'Gồm cả gói Vận năm', 'Trọn luận chính và Đọc sâu, kèm trang sách'],
  cao_cap: ['Luận riêng mọi chương của lá số', 'Suy luận sâu trên cả lá số, khoảng 500–800 từ mỗi chương', '30 ngày chat với Bát Bát (tới 30 câu/ngày)'],
  chiem_tinh: ['Bản đồ sao phương Tây (trang Chiêm tinh), riêng cho một ngày giờ và nơi sinh', 'Đọc sâu bảy chương đời sống', 'Trọn Tổng hợp và Thời vận'],
};
function paintPlans() {
  const tag = plans.placeholder ? `<small class="muted"> · ${esc(plans.placeholderLabel)}</small>` : '';
  $('#cm-plans').innerHTML = plans.plans.map(p => `<article class="cm-card cm-plan${p.id === 'tron_bo' ? ' cm-pick' : ''}">${p.id === 'tron_bo' ? '<p class="cm-badge">Gợi ý</p>' : ''}<h3>${esc(p.name)}</h3><p class="cm-price">${xu(p.coins)}${tag}</p>`
    + (PLAN_POINTS[p.id] ? `<ul class="cm-points" title="${esc(p.blurb)}">${PLAN_POINTS[p.id].map(x => `<li>${esc(x)}</li>`).join('')}</ul>` : `<p>${esc(p.blurb)}</p>`) + '</article>').join('')
    + `<article class="cm-card cm-plan"><h3>Luận riêng lẻ</h3><p class="cm-price">${xu(plans.costs.deep)}${tag}</p><p>Một chương viết bằng suy luận sâu: đọc cả lá số cùng lúc và đi sâu hơn phần đối chiếu sách, khoảng 500–800 từ, chỉ từ dữ kiện và luận giải đã có; bấm ở thẻ “Luận riêng” dưới chương. Khác với phần Đọc sâu (theo sách). Viết hỏng thì xu được hoàn lại.</p></article>`;
}

function paintPacks() {
  const host = $('#cm-packs'), signed = !!me?.user, pv = plans.providers;
  const buy = (id, provider, label) => `<button type="button" class="btn btn-sm${provider === 'vnpay' ? '' : ' btn-ghost'}" data-buy="${esc(id)}" data-provider="${provider}">${label}</button>`;
  host.innerHTML = plans.packs.map(k => {
    const price = discount ? discount.price(k) : k.amount;
    const pay = !signed ? '<a class="btn btn-sm" href="/api/auth/google">Đăng nhập để nạp</a>'
      : !pv.stripe && !pv.vnpay ? '<span class="muted small">Thanh toán chưa được bật.</span>'
      : (pv.vnpay ? buy(k.id, 'vnpay', 'VNPAY (QR, thẻ ATM)') : '') + (pv.stripe ? buy(k.id, 'stripe', 'Thẻ quốc tế') : '');
    return `<article class="cm-card cm-plan"><h3>${xu(k.coins)}</h3><p class="cm-price">${vnd(price)}${price !== k.amount ? `<span class="cm-was">${vnd(k.amount)}</span>` : ''}${plans.placeholder ? `<small class="muted"> · giá tạm</small>` : ''}</p><div class="cm-pay">${pay}</div></article>`;
  }).join('');
  host.querySelectorAll('[data-buy]').forEach(b => b.onclick = () => checkout(b));
}

async function checkout(b) {
  const msg = $('#cm-pay-msg');
  document.querySelectorAll('[data-buy]').forEach(x => { x.disabled = true; });
  say(msg, 'Đang mở trang thanh toán…');
  try {
    const r = await api('/api/me/checkout', { method: 'POST', body: JSON.stringify({ pack: b.dataset.buy, provider: b.dataset.provider, code: discount?.code }) });
    const j = await r.json().catch(() => ({}));
    if (!r.ok || !j.url) throw new Error(j.detail || String(r.status));
    location.href = j.url;
  } catch (x) { say(msg, 'Chưa mở được trang thanh toán: ' + x.message, 'err'); document.querySelectorAll('[data-buy]').forEach(x => { x.disabled = false; }); }
}

// a discount code: the server checks it and prices every pack; it checks it again at checkout
$('#cm-code-btn').onclick = async () => {
  const msg = $('#cm-code-msg'), code = $('#cm-code').value.trim();
  if (!code) { discount = null; say(msg, ''); paintPacks(); return; }
  if (!me?.user) { say(msg, 'Đăng nhập để dùng mã giảm giá.', 'err'); return; }
  try {
    const r = await api('/api/me/quote', { method: 'POST', body: JSON.stringify({ code }) }), j = await r.json();
    if (!r.ok) throw new Error(j.detail || String(r.status));
    const pct = j.discount.percent;
    discount = { code: j.discount.code, price: k => j.prices[k.id] ?? k.amount };
    say(msg, `Mã ${j.discount.code}: giảm ${pct}%. Giá mới đã hiện ở từng gói.`, 'ok');
  } catch (x) { discount = null; say(msg, x.message, 'err'); }
  paintPacks();
};

$('#cm-gift-btn').onclick = async () => {
  const msg = $('#cm-gift-msg'), code = $('#cm-gift').value.trim();
  if (!code) return;
  if (!me?.user) { say(msg, 'Đăng nhập để đổi mã quà tặng.', 'err'); return; }
  const b = $('#cm-gift-btn'); b.disabled = true;
  try {
    const r = await api('/api/me/redeem', { method: 'POST', body: JSON.stringify({ code }) }), j = await r.json();
    if (!r.ok) throw new Error(j.detail || String(r.status));
    say(msg, `Đã cộng ${j.coins} xu. Ví hiện có ${j.wallet.coins} xu.`, 'ok'); $('#cm-gift').value = '';
    paintHistory();
  } catch (x) { say(msg, x.message, 'err'); } finally { b.disabled = false; }
};

const PLAN_NAME = () => ({ ...(plans?.retiredPlans || {}), ...Object.fromEntries((plans?.plans || []).map(p => [p.id, p.name])) });
function label(h) {
  const ref = h.ref || '';
  if (h.kind === 'grant' && (ref.startsWith('stripe:') || ref.startsWith('vnpay:'))) return `Nạp xu${h.amount ? ` · ${vnd(h.amount)}` : ''}${h.order ? ` · <a href="/bien-nhan?order=${esc(h.order)}">biên nhận</a>` : ''}`;
  if (h.kind === 'grant' && ref.startsWith('admin:')) return 'Quản trị viên tặng xu';
  if (h.kind === 'grant' && ref.startsWith('referral:')) return ref === 'referral:joined' ? 'Thưởng khi tham gia qua lời mời' : 'Thưởng mời bạn';
  if (h.kind === 'grant') return 'Cộng xu';
  if (h.kind === 'gift') return `Mã quà tặng <code>${esc(ref.slice(5))}</code>`;
  if (h.kind === 'refund_coin') return 'Hoàn xu';
  if (h.usage === 'chat') return 'Hỏi đáp về lá số';
  if (h.usage === 'deep') return 'Luận riêng';
  if (h.usage.startsWith('unlock:')) return `Mở gói: ${esc(PLAN_NAME()[h.usage.slice(7)] || h.usage.slice(7))}`;
  return esc(h.kind);
}
const STATUS = { pending: ['Đang chờ', 'rc-pending'], paid: ['Đã thanh toán', 'rc-paid'], failed: ['Không thành công', 'rc-failed'] };

async function paintHistory() {
  const host = $('#cm-history');
  if (!me?.user) return;
  let j; try { const r = await api('/api/me/wallet/history'); if (!r.ok) throw 0; j = await r.json(); } catch { host.innerHTML = '<p class="muted">Chưa tải được lịch sử ví.</p>'; return; }
  dispatchEvent(new CustomEvent('tvbt:wallet', { detail: j.wallet }));
  const rows = j.history.map(h => `<tr><td>${when(h.at)}</td><td>${label(h)}</td><td class="${h.delta > 0 ? 'plus' : 'minus'}">${h.delta > 0 ? '+' : ''}${h.delta}</td></tr>`).join('');
  const orders = j.orders.filter(o => o.status !== 'paid').slice(0, 10).map(o => `<tr><td>${when(o.createdAt)}</td><td>${o.coins} xu · ${vnd(o.amount)} · ${o.provider === 'vnpay' ? 'VNPAY' : 'Stripe'}</td><td><span class="rc-status ${STATUS[o.status][1]}">${STATUS[o.status][0]}</span> <a href="/bien-nhan?order=${esc(o.id)}">chi tiết</a></td></tr>`).join('');
  host.innerHTML = `<p>Ví hiện có ${xu(j.wallet.coins)} · ${j.wallet.free.remaining}/${j.wallet.free.limit} câu chat miễn phí hôm nay${j.wallet.pass?.active ? ` · gói chat tới ${new Date(j.wallet.pass.until).toLocaleDateString('vi-VN')}` : ''}.</p>`
    + (rows ? `<div class="cm-scroll"><table class="cm-table"><thead><tr><th>Thời gian</th><th>Nội dung</th><th>Xu</th></tr></thead><tbody>${rows}</tbody></table></div>` : '<p class="muted">Chưa có giao dịch xu nào.</p>')
    + (orders ? `<h3 class="small muted" style="margin-top:var(--s4)">Lần thanh toán chưa hoàn tất</h3><div class="cm-scroll"><table class="cm-table"><tbody>${orders}</tbody></table></div>` : '');
}

boot();
