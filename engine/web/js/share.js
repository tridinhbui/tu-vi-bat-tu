// Share links for saved charts. Owner side: a dialog to create a link (birth hidden by default), switch "Ẩn thông tin sinh", copy and
// revoke. Viewer side: /#chia-se/<id> opens the chart read-only; with the birth hidden the page never receives the name, day, month or
// hour, because every engine call goes through /api/share/<id>/... (util.js shareMode) and the Worker adds the stored birth.
import { $, $$, esc, shareMode } from './util.js';
import { api, session, syncItem } from './account.js';

export const HIDE_NOTE = 'Người xem không nhận được tên và ngày, tháng, giờ sinh; máy chủ tự tính lá số cho họ. Năm sinh vẫn hiện vì năm Can Chi và tuổi trên lá số đã cho biết năm. Người thạo lịch Can Chi vẫn có thể suy ngược gần đúng ngày giờ sinh từ bốn trụ.';
export const shareUrl = id => `${location.origin}/#chia-se/${id}`;
export const SHARE_HASH = /^#chia-se\/([A-Za-z0-9_-]{22})$/;

let dlg = null;
function dialog() {
  if (dlg) return dlg;
  dlg = document.createElement('dialog');
  dlg.className = 'dlg sh-dlg'; dlg.setAttribute('aria-labelledby', 'sh-t');
  dlg.innerHTML = `<div class="sh-b"><div class="sh-h"><div><p class="eyebrow">Chia sẻ</p><h3 id="sh-t"></h3></div><button type="button" class="cpx-x" data-close aria-label="Đóng">×</button></div><div class="sh-body" aria-live="polite"></div></div>`;
  document.body.append(dlg);
  dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });
  $('[data-close]', dlg).onclick = () => dlg.close();
  return dlg;
}

const linkRow = s => `<li class="sh-link" data-sid="${esc(s.id)}"><div class="sh-url"><input readonly value="${esc(shareUrl(s.id))}" aria-label="Liên kết chia sẻ"><button type="button" class="btn btn-sm" data-copy>Sao chép</button></div>
  <div class="sh-row"><label class="chk chk-sm"><input type="checkbox" data-hide${s.hide ? ' checked' : ''}><span>Ẩn thông tin sinh</span></label><span class="muted small">Tạo ngày ${new Date(s.created_at).toLocaleDateString('vi-VN')}</span><button type="button" class="link" data-revoke>Thu hồi</button></div></li>`;

/** Wires copy / hide / revoke on rendered link rows; after() repaints whoever lists the links. */
export function bindLinks(root, after) {
  $$('.sh-link', root).forEach(li => {
    const id = li.dataset.sid;
    $('[data-copy]', li).onclick = async e => { const inp = $('input', li); inp.select(); try { await navigator.clipboard.writeText(inp.value); e.target.textContent = 'Đã chép'; } catch { document.execCommand?.('copy'); } };
    $('[data-hide]', li).onchange = async e => {
      const r = await api(`/api/me/shares/${id}`, { method: 'PATCH', body: JSON.stringify({ hide: e.target.checked }) }).catch(() => null);
      if (!r?.ok) { e.target.checked = !e.target.checked; alert('Chưa đổi được, vui lòng thử lại.'); }
    };
    $('[data-revoke]', li).onclick = async e => {
      if (e.target.dataset.sure !== '1') { e.target.dataset.sure = '1'; e.target.textContent = 'Bấm lần nữa để thu hồi'; return; }
      const r = await api(`/api/me/shares/${id}`, { method: 'DELETE' }).catch(() => null);
      if (r?.ok || r?.status === 404) after(); else alert('Chưa thu hồi được, vui lòng thử lại.');
    };
  });
}

export async function listShares() {
  const r = await api('/api/me/shares'); if (!r.ok) throw new Error(String(r.status));
  return (await r.json()).shares;
}

/** Opens the share dialog for one saved chart ({id, label, rel, req}); onChange() after any change (mycharts.js repaints). */
export async function openShareDialog(item, onChange = () => {}) {
  const d = dialog(), body = $('.sh-body', d);
  $('#sh-t', d).textContent = `Lá số “${item.label}”`;
  if (!d.open) d.showModal();
  if (!session.user) { body.innerHTML = `<p>Đăng nhập để tạo liên kết chia sẻ. Lá số được lưu vào tài khoản; liên kết trỏ tới bản lưu đó và bạn thu hồi được bất cứ lúc nào.</p><a class="btn" href="/api/auth/google">Đăng nhập với Google</a>`; return; }
  body.innerHTML = '<p class="muted">Đang tải…</p>';
  let chart;
  try { chart = await syncItem(item); } catch { chart = null; }
  if (!chart) { body.innerHTML = '<p class="muted">Chưa lưu được lá số lên tài khoản, nên chưa tạo được liên kết. Vui lòng thử lại.</p>'; return; }
  const paint = async () => {
    let mine = [];
    try { mine = (await listShares()).filter(s => s.chart_id === chart.id); } catch { body.innerHTML = '<p class="muted">Chưa tải được danh sách liên kết.</p>'; return; }
    body.innerHTML = `<p class="small">Ai có liên kết đều xem được lá số này (chỉ xem, không sửa). Liên kết ngừng hoạt động khi bạn thu hồi nó hoặc xóa lá số.</p>
      ${mine.length ? `<h4>Liên kết đang hoạt động</h4><ul class="sh-links">${mine.map(linkRow).join('')}</ul>` : ''}
      <form class="sh-new"><h4>${mine.length ? 'Tạo thêm liên kết' : 'Tạo liên kết'}</h4><label class="chk"><input type="checkbox" name="hide" checked><span>Ẩn thông tin sinh<small>${esc(HIDE_NOTE)}</small></span></label><button class="btn btn-sm" type="submit">Tạo liên kết</button><p class="muted small sh-err" role="alert"></p></form>`;
    bindLinks(body, () => { paint(); onChange(); });
    $('.sh-new', body).onsubmit = async e => {
      e.preventDefault();
      const r = await api(`/api/me/charts/${encodeURIComponent(chart.id)}/share`, { method: 'POST', body: JSON.stringify({ hide: e.target.hide.checked }) }).catch(() => null);
      if (!r?.ok) { $('.sh-err', body).textContent = r?.status === 409 ? 'Bạn đã có 50 liên kết đang hoạt động; hãy thu hồi bớt.' : 'Chưa tạo được liên kết, vui lòng thử lại.'; return; }
      await paint(); onChange();
      $('.sh-link input', body)?.select();
    };
  };
  await paint();
}

/** Viewer side. Returns { hide, label, rel, req } for a live link, or null (unknown or revoked). */
export async function loadShare(id) {
  const r = await fetch(`/api/share/${encodeURIComponent(id)}`).catch(() => null);
  if (!r?.ok) return null;
  const s = await r.json();
  shareMode.id = id;
  return s;
}

/** The banner on top of a shared chart. */
export function shareBanner(s) {
  return `<div class="wrap sh-ban-in"><p><b>Bạn đang xem một lá số được chia sẻ${s.label ? `: ${esc(s.label)}` : ''}.</b> ${s.hide ? 'Chủ lá số đã ẩn tên và ngày, tháng, giờ sinh. Năm sinh vẫn hiện vì năm Can Chi và tuổi trên lá số đã cho biết năm.' : 'Chủ lá số cho phép hiện thông tin sinh.'}</p><a class="btn btn-sm" href="/#lap-la-so">Lập lá số của bạn</a></div>`;
}
