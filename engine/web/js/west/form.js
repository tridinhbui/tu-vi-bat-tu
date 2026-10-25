// Birth form of the Western chart: date, time (or "không rõ giờ"), birthplace search over the GeoNames gazetteer, advanced options.
// The form only collects and checks input; the engine resolves the civil time (DST, historical offsets) and computes everything.
import { $, esc } from '../util.js';
import { searchPlaces } from './api.js';
import { num } from './vocab.js';

export const latLonTxt = (lat, lon) => `${num(Math.abs(lat), 4)}° ${lat >= 0 ? 'B' : 'N'} · ${num(Math.abs(lon), 4)}° ${lon >= 0 ? 'Đ' : 'T'}`;

/** Accessible combobox over /api/west/places. `onPick(place)` gets one result row ({name, admin1, country, lat, lon, tz}). */
export function placeBox(input, list, { onPick, onType } = {}) {
  let ctl = null, timer = 0, items = [], active = -1, seq = 0;
  input.setAttribute('role', 'combobox'); input.setAttribute('aria-autocomplete', 'list');
  input.setAttribute('aria-expanded', 'false'); input.setAttribute('aria-controls', list.id);
  list.setAttribute('role', 'listbox');
  const close = () => { list.hidden = true; input.setAttribute('aria-expanded', 'false'); input.removeAttribute('aria-activedescendant'); active = -1; };
  const mark = () => {
    [...list.children].forEach((li, i) => li.setAttribute('aria-selected', String(i === active)));
    if (active >= 0) { input.setAttribute('aria-activedescendant', list.children[active].id); list.children[active].scrollIntoView({ block: 'nearest' }); }
  };
  const show = (res, msg = '') => {
    items = res || [];
    list.innerHTML = items.length ? items.map((p, i) => `<li id="${list.id}-${i}" role="option" aria-selected="false" data-i="${i}"><b>${esc(p.name)}</b>`
      + `<span>${esc([p.admin1 && p.admin1 !== p.name ? p.admin1 : '', p.country].filter(Boolean).join(', '))}</span><small>${latLonTxt(p.lat, p.lon)} · ${esc(p.tz)}</small></li>`).join('')
      : `<li class="wt-pl-empty" role="option" aria-disabled="true">${esc(msg || 'Không tìm thấy nơi nào. Thử tên không dấu hoặc tên tiếng Anh, hoặc nhập tọa độ trong phần nâng cao.')}</li>`;
    list.hidden = false; input.setAttribute('aria-expanded', 'true'); active = -1;
  };
  const choose = i => { const p = items[i]; if (!p) return; input.value = p.name + (p.country ? ', ' + p.country : ''); close(); onPick?.(p); };
  input.addEventListener('input', () => {
    onType?.();
    clearTimeout(timer); ctl?.abort();
    const q = input.value.trim();
    if (q.length < 2) { close(); return; }
    timer = setTimeout(async () => {
      ctl = new AbortController(); const my = ++seq;
      const r = await searchPlaces(q, ctl.signal);
      if (my !== seq || document.activeElement !== input) return;
      if (r) show(r.results);
    }, 260);
  });
  input.addEventListener('keydown', e => {
    if (list.hidden) { if (e.key === 'ArrowDown' && items.length) { show(items); active = 0; mark(); e.preventDefault(); } return; }
    if (e.key === 'ArrowDown') { active = Math.min(items.length - 1, active + 1); mark(); e.preventDefault(); }
    else if (e.key === 'ArrowUp') { active = Math.max(0, active - 1); mark(); e.preventDefault(); }
    else if (e.key === 'Enter') { if (active >= 0 || items.length === 1) { choose(Math.max(0, active)); e.preventDefault(); } }
    else if (e.key === 'Escape') { close(); e.preventDefault(); }
  });
  list.addEventListener('mousedown', e => e.preventDefault()); // keep focus in the input while choosing
  list.addEventListener('click', e => { const li = e.target.closest('li[data-i]'); if (li) choose(+li.dataset.i); });
  input.addEventListener('blur', () => setTimeout(close, 120));
  return { close };
}

const DAYS_IN = (y, m) => new Date(Date.UTC(y, m, 0)).getUTCDate();

export function initBirthForm(form, { onSubmit, ids = {} }) {
  const I = { place: 'f-place', list: 'f-place-list', info: 'f-place-info', err: 'form-err', ...ids };
  const f = n => form.elements[n];
  f('day').innerHTML = Array.from({ length: 31 }, (_, i) => `<option value="${i + 1}">${i + 1}</option>`).join('');
  f('month').innerHTML = Array.from({ length: 12 }, (_, i) => `<option value="${i + 1}">Tháng ${i + 1}</option>`).join('');
  let picked = null;
  const info = $('#' + I.info, form);
  const showInfo = () => {
    const lat = parseFloat(f('lat').value), lon = parseFloat(f('lon').value), tz = f('tz').value.trim();
    info.innerHTML = Number.isFinite(lat) && Number.isFinite(lon) && tz ? `<span class="wt-pin" aria-hidden="true"></span>${latLonTxt(lat, lon)} · múi giờ ${esc(tz)}${picked ? '' : ' <small>(nhập tay)</small>'}` : '';
  };
  placeBox($('#' + I.place, form), $('#' + I.list, form), {
    onPick: p => { picked = p; f('lat').value = p.lat; f('lon').value = p.lon; f('tz').value = p.tz; showInfo(); },
    onType: () => { picked = null; },
  });
  ['lat', 'lon', 'tz'].forEach(n => f(n).addEventListener('input', () => { picked = null; showInfo(); }));
  const noTime = f('notime'), time = f('time');
  noTime.addEventListener('change', () => { time.disabled = noTime.checked; form.classList.toggle('wt-notime', noTime.checked); });

  const err = $('#' + I.err, form);
  const fail = msg => { err.innerHTML = `<div class="notice warn" role="note"><svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><circle cx="9" cy="9" r="7.5" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M9 8v4.5M9 5.4v.1" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg><div><b>Chưa lập được bản đồ</b><p>${esc(msg)}</p></div></div>`; err.hidden = false; };

  /** {birth, options} from the fields, or throws a Vietnamese message. */
  function read() {
    const y = parseInt(f('year').value, 10), m = +f('month').value, d = +f('day').value;
    if (!(y >= 1900 && y <= 2100)) throw new Error('Năm sinh cần nằm trong khoảng 1900 đến 2100.');
    if (d > DAYS_IN(y, m)) throw new Error(`Tháng ${m}/${y} chỉ có ${DAYS_IN(y, m)} ngày.`);
    let hour = null, minute = null;
    if (!noTime.checked) {
      const t = /^(\d{1,2}):(\d{2})/.exec(time.value || '');
      if (!t) throw new Error('Hãy nhập giờ sinh, hoặc đánh dấu "Không rõ giờ sinh".');
      hour = +t[1]; minute = +t[2];
    }
    const lat = parseFloat(f('lat').value), lon = parseFloat(f('lon').value), tz = f('tz').value.trim();
    if (!Number.isFinite(lat) || !Number.isFinite(lon) || !tz) throw new Error('Hãy chọn nơi sinh trong danh sách gợi ý, hoặc nhập vĩ độ, kinh độ và múi giờ IANA trong phần nâng cao.');
    if (Math.abs(lat) > 90 || Math.abs(lon) > 180) throw new Error('Vĩ độ phải trong khoảng −90 đến 90, kinh độ trong khoảng −180 đến 180.');
    const off = f('offset').value.trim();
    const birth = { year: y, month: m, day: d, hour, minute, lat, lon, tz, place: (picked?.name || f('place').value.split(',')[0] || '').trim().slice(0, 120),
      name: f('name').value.trim().slice(0, 80), fold: +(form.dataset.fold || 0) };
    if (off !== '') {
      const o = parseFloat(off.replace(',', '.'));
      if (!Number.isFinite(o) || Math.abs(o) > 14) throw new Error('Độ lệch UTC phải là số giờ trong khoảng −14 đến +14, ví dụ 7 hoặc −4,5.');
      birth.utc_offset_hours = o;
    }
    if (!f('house')) return { birth, options: null, gender: form.querySelector('[name=gender]:checked')?.value || null };
    const options = { house_system: f('house').value, node: f('node').value, rulers: f('rulers').value, terms: f('terms').value,
      triplicity: f('trip').value, orbs: f('orbs').value, lot_rule: f('lotrule').value, minor_aspects: f('minor').checked };
    return { birth, options, gender: form.querySelector('[name=gender]:checked')?.value || null };
  }
  /** Fill the fields from saved or shared data. */
  function fill({ birth: b, options: o = {}, gender = null }) {
    const g = form.querySelector(`[name=gender][value="${gender === 'male' || gender === 'female' ? gender : ''}"]`); if (g) g.checked = true;
    f('name').value = b.name || ''; f('year').value = b.year; f('month').value = b.month; f('day').value = b.day;
    noTime.checked = b.hour == null; time.disabled = noTime.checked; form.classList.toggle('wt-notime', noTime.checked);
    if (b.hour != null) time.value = `${String(b.hour).padStart(2, '0')}:${String(b.minute || 0).padStart(2, '0')}`;
    f('lat').value = b.lat; f('lon').value = b.lon; f('tz').value = b.tz; f('place').value = b.place || '';
    picked = b.place ? { name: b.place } : null;
    f('offset').value = b.utc_offset_hours ?? '';
    form.dataset.fold = b.fold || 0;
    const set = (n, v) => { if (v != null && f(n)) f(n).value = v; };
    set('house', o.house_system); set('node', o.node); set('rulers', o.rulers); set('terms', o.terms); set('trip', o.triplicity); set('orbs', o.orbs); set('lotrule', o.lot_rule);
    if (o.minor_aspects != null && f('minor')) f('minor').checked = o.minor_aspects;
    showInfo();
  }
  form.addEventListener('submit', async e => {
    e.preventDefault(); err.hidden = true;
    let inp; try { inp = read(); } catch (x) { fail(x.message); return; }
    const btn = $('[type=submit]', form); btn.classList.add('busy'); btn.disabled = true;
    try { await onSubmit(inp); } catch (x) { fail(x.message); } finally { btn.classList.remove('busy'); btn.disabled = false; }
  });
  // a fresh change of date/time/place forgets an earlier DST-overlap choice
  ['year', 'month', 'day', 'time', 'tz'].forEach(n => f(n).addEventListener('change', () => { form.dataset.fold = 0; }));
  return { read, fill, fail, setHouse(v) { if (f('house')) f('house').value = v; } };
}
