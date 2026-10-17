// "Của bạn" layer: charts saved on this device only (localStorage; nothing is sent to the server).
import { $, $$, esc, post } from './util.js';
import { terms, autoLink } from './glossary.js';

const KEY = 'tvbt-saved-v1', MAX = 12;
const FIELDS = ['year', 'month', 'day', 'hour', 'minute', 'gender', 'tz', 'calendar', 'zi_rule', 'level', 'use_true_solar_time', 'longitude'];
const RELS = ['Tôi', 'Người thân', 'Bạn bè'];

export const readSaved = () => { try { const a = JSON.parse(localStorage.getItem(KEY)); return Array.isArray(a) ? a : []; } catch { return []; } };
const writeSaved = a => { try { localStorage.setItem(KEY, JSON.stringify(a)); return true; } catch { return false; } };
const same = (a, b) => ['year', 'month', 'day', 'hour', 'minute', 'gender'].every(k => a[k] === b[k]);
const pick = req => Object.fromEntries(FIELDS.filter(k => req[k] !== undefined).map(k => [k, req[k]]));
const fmt = r => `${String(r.day).padStart(2, '0')}/${String(r.month).padStart(2, '0')}/${r.year} · ${String(r.hour).padStart(2, '0')}:${String(r.minute).padStart(2, '0')} · ${r.gender === 'male' ? 'Nam' : 'Nữ'}`;

export function saveChart(req, label, rel) {
  const list = readSaved(), r = pick(req), name = (label || '').trim().slice(0, 30) || rel;
  const i = list.findIndex(x => same(x.req, r));
  const item = { id: i >= 0 ? list[i].id : Date.now().toString(36), label: name, rel, req: r };
  if (i >= 0) list[i] = item; else list.unshift(item);
  return writeSaved(list.slice(0, MAX)) ? item : null;
}
export const isSaved = req => readSaved().find(x => same(x.req, pick(req)));

const picked = new Set();

/** Home list of saved charts; onOpen(req) generates the chart again from the stored birth data. With 2+ charts, any two can be compared. */
export function renderSaved(host, onOpen) {
  const list = readSaved(), sec = host.closest('section') || host, out = $('#compare-out', sec);
  sec.hidden = !list.length;
  [...picked].forEach(id => { if (!list.some(x => x.id === id)) picked.delete(id); });
  host.innerHTML = list.map(x => `<li>${list.length > 1 ? `<label class="sv-cmp"><input type="checkbox" data-id="${esc(x.id)}"${picked.has(x.id) ? ' checked' : ''} aria-label="Chọn ${esc(x.label)} để so sánh"></label>` : ''}<button type="button" class="sv-open" data-id="${esc(x.id)}"><span class="sv-rel">${esc(x.rel)}</span><b>${esc(x.label)}</b><small>${esc(fmt(x.req))}</small></button><button type="button" class="sv-del" data-id="${esc(x.id)}" aria-label="Xóa lá số ${esc(x.label)} khỏi máy này">Xóa</button></li>`).join('');
  $$('.sv-open', host).forEach(b => b.onclick = () => onOpen(list.find(x => x.id === b.dataset.id).req));
  $$('.sv-del', host).forEach(b => b.onclick = () => { writeSaved(readSaved().filter(x => x.id !== b.dataset.id)); renderSaved(host, onOpen); });
  const hint = $('#compare-hint', sec), go = () => {
    const two = list.filter(x => picked.has(x.id));
    hint.textContent = list.length < 2 ? 'Lưu thêm một lá số nữa để so sánh hai người.' : two.length === 2 ? '' : 'Tích chọn hai lá số để so sánh.';
    if (two.length === 2) renderCompare(out, two[0], two[1]); else out.innerHTML = '';
  };
  $$('.sv-cmp input', host).forEach(i => i.onchange = () => {
    if (i.checked) { if (picked.size >= 2) { i.checked = false; return; } picked.add(i.dataset.id); } else picked.delete(i.dataset.id);
    $$('.sv-cmp input', host).forEach(o => o.disabled = !o.checked && picked.size >= 2);
    go();
  });
  $$('.sv-cmp input', host).forEach(o => o.disabled = !o.checked && picked.size >= 2);
  go();
}

const LINK = { 'cùng hành': 'Hai hành giống nhau thường được mô tả là “cùng nhịp”, nhưng đây chỉ là mô tả, không phải đánh giá.', sinh: 'Một hành nuôi dưỡng hành kia theo vòng tương sinh.', khắc: 'Một hành kiềm chế hành kia theo vòng tương khắc. “Khắc” là quan hệ giữa hai hành, không tự nó là điều xấu.' };

async function renderCompare(host, A, B) {
  host.innerHTML = '<p class="muted">Đang so sánh…</p>';
  let r; try { r = await post('/api/compare-charts', { a: A.req, b: B.req }); } catch (e) { host.innerHTML = `<p class="muted">Chưa so sánh được: ${esc(e.message)}</p>`; return; }
  const T = terms(), plain = g => esc(T['god:' + g]?.plain || '');
  const col = (n, s) => `<div class="cmp-c"><span class="k">${esc(n.rel === n.label ? n.label : n.rel + ' · ' + n.label)}</span><b>${esc(s.day_master)} ${esc(s.element)}</b><p>Trụ Ngày ${esc(s.day_pillar)} · ${esc(s.polarity)} · ngày chi ${esc(s.day_branch)}</p></div>`;
  host.innerHTML = `<div class="cmp"><p class="eyebrow">So sánh dữ kiện</p><h3>${esc(A.label)} và ${esc(B.label)}</h3>
    <div class="cmp-cols">${col(A, r.a)}${col(B, r.b)}</div>
    <ul class="cmp-list">
      <li><b>Nhật Chủ nhìn nhau.</b> Với ${esc(A.label)}, Nhật Chủ của ${esc(B.label)} mang tính <b>${esc(r.ten_god_of_b_for_a)}</b>; ngược lại, với ${esc(B.label)}, Nhật Chủ của ${esc(A.label)} mang tính <b>${esc(r.ten_god_of_a_for_b)}</b>. ${plain(r.ten_god_of_b_for_a)} ${r.ten_god_of_a_for_b !== r.ten_god_of_b_for_a ? plain(r.ten_god_of_a_for_b) : ''}</li>
      <li><b>Ngũ Hành của hai Nhật Chủ.</b> ${esc(r.element_link.text.replace('người A', A.label).replace('người B', B.label))} ${esc(LINK[r.element_link.kind] || '')}</li>
      <li><b>Hai Thiên can Nhật Chủ.</b> ${esc(r.day_master_stems.text)}</li>
      <li><b>Hai ngày chi.</b> ${r.day_branches.map(x => esc(x.text)).join(' ')}</li>
    </ul>
    <p class="muted small">${esc(r.note)} Tám chữ còn lại, sao Tử Vi và vận hạn chưa được đưa vào so sánh này.</p></div>`;
  autoLink(host, 'bt');
}

/** Save control on the result page: one button that expands to name + relation. */
export function initSave(host, getReq, onChange) {
  host.innerHTML = `<button type="button" class="btn btn-ghost btn-sm" id="sv-btn" aria-expanded="false"></button>
    <form class="sv-form" id="sv-form" hidden><label>Tên gọi<input name="label" maxlength="30" placeholder="Ví dụ: Mẹ, Minh…" autocomplete="off"></label>
    <label>Mối quan hệ<select name="rel">${RELS.map(r => `<option>${r}</option>`).join('')}</select></label>
    <button class="btn btn-sm" type="submit">Lưu trên máy này</button><p class="muted small">Chỉ lưu trong trình duyệt của bạn; máy chủ không nhận được gì. Xóa được bất cứ lúc nào ở trang chủ.</p></form>`;
  const btn = $('#sv-btn', host), form = $('#sv-form', host);
  const paint = () => { const s = getReq() && isSaved(getReq()); btn.textContent = s ? `Đã lưu: ${s.label} · sửa tên` : 'Lưu lá số này'; };
  btn.onclick = () => { const o = form.hidden; form.hidden = !o; btn.setAttribute('aria-expanded', o); const s = isSaved(getReq()); if (s) { form.label.value = s.label; form.rel.value = s.rel; } };
  form.onsubmit = e => {
    e.preventDefault();
    const ok = saveChart(getReq(), form.label.value, form.rel.value);
    if (!ok) { $('.muted', form).textContent = 'Trình duyệt không cho phép lưu (chế độ riêng tư hoặc đã chặn lưu trữ).'; return; }
    form.hidden = true; btn.setAttribute('aria-expanded', 'false'); paint(); onChange();
  };
  paint();
  return { paint };
}
