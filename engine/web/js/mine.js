// "Của bạn" layer: this-year cards and charts saved on this device only (localStorage; nothing is sent to the server).
import { $, $$, esc, post, PILLAR_LABEL } from './util.js';
import { terms } from './glossary.js';

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

/** Home list of saved charts; onOpen(req) generates the chart again from the stored birth data. */
export function renderSaved(host, onOpen) {
  const list = readSaved(), sec = host.closest('section') || host;
  sec.hidden = !list.length;
  host.innerHTML = list.map(x => `<li><button type="button" class="sv-open" data-id="${esc(x.id)}"><span class="sv-rel">${esc(x.rel)}</span><b>${esc(x.label)}</b><small>${esc(fmt(x.req))}</small></button><button type="button" class="sv-del" data-id="${esc(x.id)}" aria-label="Xóa lá số ${esc(x.label)} khỏi máy này">Xóa</button></li>`).join('');
  $$('.sv-open', host).forEach(b => b.onclick = () => onOpen(list.find(x => x.id === b.dataset.id).req));
  $$('.sv-del', host).forEach(b => b.onclick = () => { writeSaved(readSaved().filter(x => x.id !== b.dataset.id)); renderSaved(host, onOpen); });
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

// ---- "Năm nay của bạn" ----
const KIND = { can_hợp: 'Thiên can hợp', can_xung: 'Thiên can xung', 'chi_lục hợp': 'Địa chi lục hợp', chi_phá: 'Địa chi phá', chi_hại: 'Địa chi hại', chi_xung: 'Địa chi xung', 'chi_tam hợp': 'Địa chi tam hợp' };
const kindText = k => KIND[k] || k.replace('_', ' ');
const godPlain = (T, g) => T['god:' + g]?.plain || '';
const rel = (arr, who) => arr.map(r => `${who} ${kindText(r.kind).toLowerCase()} trụ ${PILLAR_LABEL[r.with] || r.with}`);

export async function renderYear(req, T = terms()) {
  const y = new Date().getFullYear();
  let d; try { d = await post('/api/year', { ...req, to_year: y }); } catch { return null; }
  const b = d.bazi, t = d.tuvi, tuHoa = t.luu_tu_hoa_reading || [];
  const inter = rel(b.annual_vs_natal, 'năm nay').concat(rel(b.luck_vs_natal, 'đại vận'));
  const bazi = `<section class="bs yr" aria-labelledby="yr-bt-h"><p class="eyebrow">Năm nay của bạn · ${y}</p><h2 id="yr-bt-h">Năm ${esc(b.annual_pillar)}, bạn khoảng ${b.age} tuổi</h2>
    <p class="sec-sub">Mỗi năm có một cặp Can Chi riêng, được so với tám chữ gốc của bạn. Đây là bối cảnh để suy ngẫm, không phải lời tiên đoán.</p>
    <div class="bs-grid">
      <div class="bs-c"><span class="k">Năm ${y}</span><b>${esc(b.annual_pillar)}</b><p>Đối với Nhật Chủ của bạn, can của năm mang tính chất <b>${esc(b.annual_stem_ten_god)}</b>. ${esc(godPlain(T, b.annual_stem_ten_god))}</p></div>
      <div class="bs-c"><span class="k">Chặng 10 năm đang đi</span><b>Đại vận ${esc(b.luck_pillar)}</b><p>Can của đại vận là <b>${esc(b.luck_stem_ten_god)}</b>. ${esc(godPlain(T, b.luck_stem_ten_god))}</p></div>
      <div class="bs-c"><span class="k">Gặp tám chữ gốc</span><b>${inter.length} điểm tương tác</b><p>${inter.length ? esc(inter.slice(0, 4).join('; ')) + (inter.length > 4 ? `; và ${inter.length - 4} điểm khác.` : '.') + ' “Hợp” là gắn kết, “xung” là va chạm; chỉ cho biết có chạm nhau, chưa nói tốt hay xấu.' : 'Năm này không chạm trực tiếp vào tám chữ gốc.'}</p></div>
    </div></section>`;
  const tuvi = `<section class="bs yr" aria-labelledby="yr-tv-h"><p class="eyebrow">Năm nay của bạn · ${y}</p><h2 id="yr-tv-h">Năm ${esc(t.annual_pillar)}: ánh đèn rọi vào đâu?</h2>
    <p class="sec-sub">Tử Vi đặt thêm một lớp “của năm” lên lá số gốc. Chỗ nào được rọi sáng là lĩnh vực bạn có thể để ý hơn trong năm; không phải điều chắc chắn xảy ra.</p>
    <div class="bs-grid">
      <div class="bs-c"><span class="k">Tiểu hạn năm nay</span><b>Cung ${esc(t.tieu_han_palace)}</b><p>${esc(T['palace:' + t.tieu_han_palace]?.plain || '')}</p></div>
      <div class="bs-c"><span class="k">Lưu Thái Tuế</span><b>Cung ${esc(t.luu_thai_tue_palace)}</b><p>Nơi “ngôi sao của năm” đóng, thường gắn với những việc nổi bật trong năm. ${esc(T['palace:' + t.luu_thai_tue_palace]?.plain || '')}</p></div>
    </div>
    ${tuHoa.length ? `<h3>Tứ Hóa của năm ${y}</h3><ul class="bs-lim">${tuHoa.map(h => `<li><b>${esc(h.hoa)} · ${esc(h.star)}</b> rơi vào cung <b>${esc(h.palace)}</b>: ${esc(h.advice)}.</li>`).join('')}</ul>` : ''}
    <p class="muted small">Thông tin theo năm là dữ kiện cấu trúc từ sách, không phải dự đoán sự kiện.</p></section>`;
  return { bazi, tuvi };
}
