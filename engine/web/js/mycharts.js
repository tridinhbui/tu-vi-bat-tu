// "Lá số của tôi" (account page): every saved chart (yourself, family, friends) with open / rename / share / delete, and a quick compare
// of the two ticked charts through the compare dialog (compare.js). The list is the same one the home page shows (mine.js).
import { $, $$, esc } from './util.js';
import { readSaved, saveChart, removeSaved, fmtBirth, RELS } from './mine.js';
import { session } from './account.js';
import { openShareDialog, listShares, bindLinks, shareUrl } from './share.js';

/** host: the section body; deps: { onOpen(req), compare: compare.js handle, onChange() after any edit (repaints the home list) } */
export function initMyCharts(host, { onOpen, compare, onChange }) {
  let picked = [], shares = [];
  const paint = async () => {
    const list = readSaved();
    picked = picked.filter(id => list.some(x => x.id === id));
    if (session.user) { try { shares = await listShares(); } catch { shares = []; } }
    const count = id => shares.filter(s => s.chart_id === id).length;
    const groups = RELS.map(r => [r, list.filter(x => x.rel === r)]).filter(([, xs]) => xs.length);
    host.innerHTML = !list.length ? `<p class="muted">Chưa có lá số nào được lưu. Lập một lá số rồi bấm “Lưu lá số này”; bạn lưu được lá số của mình, người thân và bạn bè.</p><a class="btn btn-sm" href="#lap-la-so" data-go="lap-la-so">Lập lá số</a>`
      : `<div class="mc-bar"><button type="button" class="btn btn-sm" data-cmp disabled>So sánh hai lá số đã chọn</button><span class="muted small" data-cmp-n>Chọn hai lá số để so sánh.</span></div>
      ${groups.map(([r, xs]) => `<h4 class="mc-g">${esc(r)} <small>(${xs.length})</small></h4><ul class="mc-list">${xs.map(x => `<li data-id="${esc(x.id)}">
        <label class="mc-pick"><input type="checkbox" data-pick${picked.includes(x.id) ? ' checked' : ''} aria-label="Chọn ${esc(x.label)} để so sánh"></label>
        <div class="mc-main"><b>${esc(x.label)}</b><small>${esc(fmtBirth(x.req))}</small>${count(x.id) ? `<span class="mc-sh">Đang chia sẻ · ${count(x.id)} liên kết</span>` : ''}</div>
        <div class="mc-act"><button type="button" class="btn btn-sm" data-open>Mở</button><button type="button" class="btn btn-ghost btn-sm" data-ren aria-expanded="false">Đổi tên</button><button type="button" class="btn btn-ghost btn-sm" data-share>Chia sẻ</button><button type="button" class="btn btn-ghost btn-sm mc-del" data-del>Xóa</button></div>
        <form class="mc-ren" hidden><label>Tên gọi<input name="label" maxlength="30" value="${esc(x.label)}"></label><label>Mối quan hệ<select name="rel">${RELS.map(o => `<option${o === x.rel ? ' selected' : ''}>${o}</option>`).join('')}</select></label><button class="btn btn-sm">Lưu</button><button type="button" class="btn btn-ghost btn-sm" data-cancel>Hủy</button></form></li>`).join('')}</ul>`).join('')}
      ${shares.length ? `<h4 class="mc-g">Liên kết đang chia sẻ <small>(${shares.length})</small></h4><ul class="sh-links mc-links">${shares.map(s => `<li class="sh-link" data-sid="${esc(s.id)}"><p class="small"><b>${esc(s.label)}</b> · ${s.hide ? 'đã ẩn thông tin sinh' : 'hiện thông tin sinh'}</p><div class="sh-url"><input readonly value="${esc(shareUrl(s.id))}" aria-label="Liên kết chia sẻ ${esc(s.label)}"><button type="button" class="btn btn-sm" data-copy>Sao chép</button></div><div class="sh-row"><label class="chk chk-sm"><input type="checkbox" data-hide${s.hide ? ' checked' : ''}><span>Ẩn thông tin sinh</span></label><button type="button" class="link" data-revoke>Thu hồi</button></div></li>`).join('')}</ul>` : ''}
      ${session.user ? '' : '<p class="muted small">Lá số đang nằm trên máy này. Đăng nhập để đồng bộ giữa các thiết bị và tạo liên kết chia sẻ.</p>'}`;
    const item = li => readSaved().find(x => x.id === li.dataset.id);
    const cmpBtn = $('[data-cmp]', host), cmpN = $('[data-cmp-n]', host);
    const syncPick = () => { if (!cmpBtn) return; cmpBtn.disabled = picked.length !== 2; cmpN.textContent = picked.length === 2 ? '' : picked.length > 2 ? 'Chỉ chọn hai lá số.' : `Đã chọn ${picked.length}/2.`; };
    syncPick();
    if (cmpBtn) cmpBtn.onclick = () => picked.length === 2 && compare.open(picked[0], picked[1]);
    $$('.mc-list > li', host).forEach(li => {
      const x = item(li); if (!x) return;
      $('[data-pick]', li).onchange = e => { picked = e.target.checked ? [...picked, x.id] : picked.filter(i => i !== x.id); syncPick(); };
      $('[data-open]', li).onclick = () => onOpen(x.req);
      const form = $('.mc-ren', li), ren = $('[data-ren]', li);
      ren.onclick = () => { form.hidden = !form.hidden; ren.setAttribute('aria-expanded', String(!form.hidden)); if (!form.hidden) form.label.focus(); };
      $('[data-cancel]', form).onclick = () => { form.hidden = true; ren.setAttribute('aria-expanded', 'false'); };
      // same birth -> same entry: saveChart updates the name and relation in place and pushes the change to the account
      form.onsubmit = e => { e.preventDefault(); saveChart(x.req, form.label.value, form.rel.value); onChange(); paint(); };
      $('[data-share]', li).onclick = () => openShareDialog(x, paint);
      $('[data-del]', li).onclick = e => {
        if (e.target.dataset.sure !== '1') { e.target.dataset.sure = '1'; e.target.textContent = count(x.id) ? 'Xóa cả liên kết chia sẻ?' : 'Bấm lần nữa để xóa'; return; }
        removeSaved(x.id); onChange(); setTimeout(paint, 300);     // the server deletes the chart, which also ends its share links
      };
    });
    bindLinks($('.mc-links', host) || host.ownerDocument.createElement('div'), paint);
  };
  addEventListener('tvbt:account', paint);
  return { paint };
}
