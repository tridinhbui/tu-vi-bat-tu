// Receipt page (/bien-nhan?order=<id>): the order as the server recorded it. A payment is "paid" only once the provider's signed callback
// (Stripe webhook, VNPAY IPN) reached the server, so a page opened right after paying waits for it, re-reading for up to two minutes.
import { esc } from './util.js';

const $ = s => document.querySelector(s);
const q = new URLSearchParams(location.search), id = q.get('order') || '', vnp = q.get('vnp');
const vnd = n => `${Number(n).toLocaleString('vi-VN')}đ`;
const when = t => new Date(t).toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh', hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit', year: 'numeric' });
const STATUS = { pending: ['Đang chờ xác nhận', 'rc-pending'], paid: ['Đã thanh toán', 'rc-paid'], failed: ['Không thành công', 'rc-failed'] };
// VNPAY codes a visitor may come back with (src/billing/vnpay.ts RESPONSE_VI holds the same list for the server)
const VNP = { '24': 'Bạn đã hủy giao dịch.', '11': 'Hết thời gian chờ thanh toán.', '51': 'Tài khoản không đủ số dư.', '65': 'Tài khoản đã vượt hạn mức giao dịch trong ngày.', '75': 'Ngân hàng thanh toán đang bảo trì.', '07': 'Giao dịch đang chờ ngân hàng xác minh.' };

let tries = 0;
async function load() {
  const body = $('#rc-body');
  if (!/^[0-9a-f]{20}$/.test(id)) { body.innerHTML = '<p>Không tìm thấy đơn hàng.</p>'; return; }
  const r = await fetch('/api/me/orders/' + id, { credentials: 'same-origin', cache: 'no-store' }).catch(() => null);
  if (!r || r.status === 401) { body.innerHTML = '<p>Đăng nhập bằng tài khoản đã thanh toán để xem biên nhận.</p><p><a class="btn btn-sm" href="/api/auth/google">Đăng nhập với Google</a></p>'; return; }
  if (!r.ok) { body.innerHTML = '<p>Không tìm thấy đơn hàng này trong tài khoản của bạn.</p>'; return; }
  const { order: o, wallet } = await r.json(), [st, cls] = STATUS[o.status] || [o.status, ''];
  const note = o.status === 'paid' ? `Đã cộng ${o.coins} xu vào ví. Ví hiện có ${wallet.coins} xu.`
    : o.status === 'failed' ? 'Giao dịch không thành công; không có khoản nào được ghi nhận cho đơn này.'
    : vnp && vnp !== '00' ? (vnp === 'bad' ? 'Không xác thực được kết quả trả về từ cổng thanh toán.' : VNP[vnp] || `Cổng thanh toán báo mã ${esc(vnp)}.`)
    : 'Đang chờ cổng thanh toán xác nhận. Trang tự cập nhật; thường chỉ mất vài giây.';
  $('#rc-h').textContent = o.status === 'paid' ? 'Cảm ơn bạn, thanh toán đã xong' : 'Đơn nạp xu';
  body.innerHTML = `<p><span class="rc-status ${cls}">${st}</span></p><p>${note}</p><div class="cm-card"><dl>
    <dt>Mã đơn</dt><dd><code>${esc(o.id)}</code></dd><dt>Tạo lúc</dt><dd>${when(o.createdAt)}</dd>${o.paidAt ? `<dt>Thanh toán lúc</dt><dd>${when(o.paidAt)}</dd>` : ''}
    <dt>Gói</dt><dd>${o.coins} xu</dd><dt>Giá niêm yết</dt><dd>${vnd(o.listAmount)}</dd>${o.discountPct ? `<dt>Mã giảm giá</dt><dd>${esc(o.discountCode)} (−${o.discountPct}%)</dd>` : ''}
    <dt>Số tiền</dt><dd>${vnd(o.amount)}</dd><dt>Cổng thanh toán</dt><dd>${o.provider === 'vnpay' ? 'VNPAY' : 'Thẻ quốc tế (Stripe)'}</dd>${o.providerRef ? `<dt>Mã giao dịch</dt><dd><code>${esc(o.providerRef)}</code></dd>` : ''}</dl></div>`;
  $('#rc-print').hidden = o.status !== 'paid';
  if (o.status === 'pending' && !(vnp && vnp !== '00') && ++tries < 40) setTimeout(load, 3000);
}
$('#rc-print').onclick = () => print();
load();
