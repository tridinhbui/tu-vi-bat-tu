// Admin "Bán hàng" tab: make discount and gift codes, switch them off, and see recent orders. All checks are on the server
// (src/billing/codes.ts); this page only collects the fields and shows the answer.
const $ = (s, r = document) => r.querySelector(s);
const api = (path, opts = {}) => fetch(path, { credentials: 'same-origin', cache: 'no-store', ...opts, headers: { 'x-tvbt': '1', 'content-type': 'application/json', ...(opts.headers || {}) } });
const fmt = n => Number(n || 0).toLocaleString('vi-VN');
const when = t => t ? new Date(t).toLocaleString('vi-VN', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit', year: 'numeric' }) : '—';
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
const STATUS = { pending: 'Đang chờ', paid: 'Đã thanh toán', failed: 'Không thành công' };
const PROVIDER = { stripe: 'Stripe', vnpay: 'VNPAY' };

function table(head, rows) {
  const t = el('table', 'adm-table'), tr = el('tr');
  for (const h of head) tr.append(el('th', '', h));
  const th = el('thead'); th.append(tr); t.append(th);
  const tb = el('tbody'); for (const r of rows) { const x = el('tr'); for (const c of r) { const td = el('td'); c instanceof Node ? td.append(c) : (td.textContent = c); x.append(td); } tb.append(x); }
  t.append(tb); return t;
}

async function loadCodes() {
  const host = $('#code-list');
  let codes; try { const r = await api('/api/admin/codes'); if (!r.ok) throw 0; codes = (await r.json()).codes; } catch { host.textContent = 'Chưa tải được danh sách mã.'; return; }
  if (!codes.length) { host.replaceChildren(el('p', 'muted', 'Chưa có mã nào.')); return; }
  host.replaceChildren(table(['Mã', 'Loại', 'Giá trị', 'Đã dùng', 'Hết hạn', 'Ghi chú', ''], codes.map(c => {
    const b = el('button', 'btn btn-sm btn-ghost', c.active ? 'Tắt' : 'Bật'); b.type = 'button';
    b.onclick = async () => { b.disabled = true; await api('/api/admin/codes/' + encodeURIComponent(c.code), { method: 'POST', body: JSON.stringify({ active: !c.active }) }).catch(() => {}); loadCodes(); };
    const code = el('code', c.active ? '' : 'muted', c.code);
    return [code, c.kind === 'gift' ? 'Quà tặng' : 'Giảm giá', c.kind === 'gift' ? `${fmt(c.coins)} xu` : `−${c.percent}%`, `${fmt(c.used)} / ${fmt(c.max_uses)}`,
      c.expires_at ? when(c.expires_at) : 'không', c.note || '', b];
  })));
}

async function loadOrders() {
  const host = $('#order-list');
  let orders; try { const r = await api('/api/admin/orders'); if (!r.ok) throw 0; orders = (await r.json()).orders; } catch { host.textContent = 'Chưa tải được đơn hàng.'; return; }
  if (!orders.length) { host.replaceChildren(el('p', 'muted', 'Chưa có đơn hàng nào.')); return; }
  host.replaceChildren(table(['Thời gian', 'Tài khoản', 'Cổng', 'Xu', 'Số tiền', 'Mã giảm', 'Trạng thái', 'Mã đơn'], orders.map(o => [
    when(o.createdAt), o.email || '—', PROVIDER[o.provider] || o.provider, fmt(o.coins), `${fmt(o.amount)}đ${o.amount !== o.listAmount ? ` (gốc ${fmt(o.listAmount)}đ)` : ''}`,
    o.discountCode || '', STATUS[o.status] || o.status, el('code', 'small', o.id)])));
}

let bound = false;
export function loadSales() {
  if (!bound) {
    bound = true;
    const f = $('#code-form'), msg = $('.sl-msg', f);
    const kind = () => f.kind.value;
    f.kind.onchange = () => { $('.sl-gift', f).hidden = kind() !== 'gift'; $('.sl-disc', f).hidden = kind() !== 'discount'; };
    f.onsubmit = async e => {
      e.preventDefault(); msg.textContent = ''; msg.className = 'sl-msg small';
      const body = { kind: kind(), code: f.code.value.trim() || undefined, max_uses: Number(f.max_uses.value), expires: f.expires.value || undefined, note: f.note.value.trim() };
      if (kind() === 'gift') body.coins = Number(f.coins.value); else body.percent = Number(f.percent.value);
      const btn = $('button[type=submit]', f); btn.disabled = true;
      try {
        const r = await api('/api/admin/codes', { method: 'POST', body: JSON.stringify(body) }), j = await r.json();
        if (!r.ok) throw new Error(j.detail || 'lỗi');
        msg.textContent = `Đã tạo mã ${j.code.code}.`; msg.classList.add('ok'); f.code.value = ''; f.note.value = '';
        loadCodes();
      } catch (x) { msg.textContent = 'Chưa tạo được mã: ' + x.message; msg.classList.add('err'); }
      finally { btn.disabled = false; }
    };
    $('#sl-refresh').onclick = () => { loadCodes(); loadOrders(); };
  }
  loadCodes(); loadOrders();
}
