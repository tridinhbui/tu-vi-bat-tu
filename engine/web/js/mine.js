// "Của bạn" layer: charts saved on this device only (localStorage; nothing is sent to the server).
import { $, $$, esc } from './util.js';

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

/** Home list of saved charts; onOpen(req) generates the chart again from the stored birth data. Comparing two charts lives in compare.js. */
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
