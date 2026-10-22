// "Thông tin cá nhân" (account page): name, gender, birth date (dương or âm lịch), birth hour, place, career and relationship status,
// stored in the signed-in account (/api/me/profile). It prefills the chart form and orders the reading's chapters (focus.js); it never
// adds a claim. Signed out, nothing here is shown or stored.
import { $, $$, esc, post, placeTz } from './util.js';
import { api, session } from './account.js';
import { CAREER, RELATIONSHIP, focusOf } from './focus.js';

export const profileState = { profile: null, loaded: false };
const OWN = ['year', 'month', 'day', 'gender'];

/** True when this birth request is the user's own (profile birth, as dương lịch, plus the hour when the profile knows it). */
export function isOwnChart(req) {
  const p = profileState.profile;
  if (!p?.solar || !req || !p.gender) return false;
  const mine = { ...p.solar, gender: p.gender };
  if (!OWN.every(k => req[k] === mine[k])) return false;
  return p.hour === null || (req.hour === p.hour && req.minute === p.minute);
}
/** Focus for the reading of this chart: only the user's own chart is reordered. */
export const focusFor = req => isOwnChart(req) ? focusOf(profileState.profile) : [];

const opt = (v, t, sel) => `<option value="${esc(v)}"${sel ? ' selected' : ''}>${esc(t)}</option>`;
const pad = n => String(n).padStart(2, '0');

/** host: the profile section of the account page; placeOptions: the chart form's place list (HTML); onPrefill(profile): fill the form. */
export function initProfile(host, { placeOptions, onPrefill, onRun }) {
  let lunar = false;
  host.innerHTML = `<form class="pf-form bform" id="pf-form" novalidate>
      <label class="fld"><span>Họ tên</span><input name="name" maxlength="60" autocomplete="name" placeholder="Tên bạn muốn hiện trên lá số"></label>
      <fieldset class="fld fld-radio"><legend>Giới tính</legend><div class="seg" role="radiogroup"><label><input type="radio" name="gender" value="male"><span>Nam</span></label><label><input type="radio" name="gender" value="female"><span>Nữ</span></label></div></fieldset>
      <fieldset class="f-set"><legend>Ngày sinh</legend>
        <div class="seg seg-wide" role="group" aria-label="Loại lịch"><button type="button" data-cal="solar" aria-pressed="true">Dương lịch</button><button type="button" data-cal="lunar" aria-pressed="false">Âm lịch</button></div>
        <div class="f-row f-3"><label class="fld"><span>Ngày</span><div class="sel"><select name="day"></select></div></label><label class="fld"><span>Tháng</span><div class="sel"><select name="month">${Array.from({ length: 12 }, (_, i) => opt(i + 1, 'Tháng ' + (i + 1))).join('')}</select></div></label><label class="fld"><span>Năm</span><input name="year" type="number" inputmode="numeric" min="1900" max="2049"></label></div>
        <label class="chk" data-leap hidden><input type="checkbox" name="leap"><span>Tháng nhuận</span></label></fieldset>
      <div class="f-row f-2"><div class="fld"><label class="lbl" for="pf-time">Giờ sinh</label><input id="pf-time" name="time" type="time" value="12:00"><label class="chk chk-sm"><input type="checkbox" name="nohour"><span>Tôi không rõ giờ sinh</span></label></div>
        <label class="fld"><span>Nơi sinh</span><div class="sel"><select name="place">${placeOptions}</select></div></label></div>
      <div class="f-row f-2"><label class="fld"><span>Công việc hiện nay</span><div class="sel"><select name="career">${opt('', 'Không muốn nói')}${Object.entries(CAREER).map(([k, v]) => opt(k, v)).join('')}</select></div></label>
        <label class="fld"><span>Tình trạng quan hệ</span><div class="sel"><select name="relationship">${opt('', 'Không muốn nói')}${Object.entries(RELATIONSHIP).map(([k, v]) => opt(k, v)).join('')}</select></div></label></div>
      <p class="help">Công việc và tình trạng quan hệ chỉ dùng để đưa các chương bạn quan tâm (Công danh, Tài Bạch, Quan hệ) lên trước khi bạn xem lá số của chính mình. Hệ thống không suy thêm nhận định nào từ hai ô này.</p>
      <div id="pf-err" role="alert" hidden></div>
      <div class="pf-act"><button class="btn" type="submit">Lưu thông tin</button><button class="btn btn-ghost" type="button" data-run hidden>Lập lá số của tôi</button><span class="muted small pf-ok" role="status"></span></div>
    </form>`;
  const f = $('#pf-form', host), err = $('#pf-err', host), ok = $('.pf-ok', host);
  const days = () => { const cur = +f.day.value || 1; f.day.innerHTML = Array.from({ length: lunar ? 30 : 31 }, (_, i) => opt(i + 1, i + 1, i + 1 === Math.min(cur, lunar ? 30 : 31))).join(''); };
  const setCal = l => { lunar = l; $$('[data-cal]', f).forEach(b => b.setAttribute('aria-pressed', String((b.dataset.cal === 'lunar') === l))); $('[data-leap]', f).hidden = !l; days(); };
  $$('[data-cal]', f).forEach(b => b.onclick = () => setCal(b.dataset.cal === 'lunar'));
  f.nohour.onchange = () => { f.time.disabled = f.nohour.checked; };
  setCal(false);

  const fill = p => {
    f.name.value = p?.name || ''; setCal(p?.cal === 'lunar');
    f.year.value = p?.year || ''; f.month.value = p?.month || 1; days(); f.day.value = p?.day || 1; f.leap.checked = !!p?.leap;
    f.nohour.checked = p ? p.hour === null : false; f.time.value = p && p.hour !== null ? `${pad(p.hour)}:${pad(p.minute)}` : '12:00'; f.nohour.onchange();
    $$('[name=gender]', f).forEach(r => { r.checked = r.value === p?.gender; });
    if (p?.place && [...f.place.options].some(o => o.value === p.place)) f.place.value = p.place;
    f.career.value = p?.career || ''; f.relationship.value = p?.relationship || '';
    $('[data-run]', f).hidden = !p;
  };
  const read = () => {
    const [h, m] = (f.time.value || '12:00').split(':').map(Number);
    return { name: f.name.value, gender: f.gender.value || '', cal: lunar ? 'lunar' : 'solar', year: +f.year.value, month: +f.month.value, day: +f.day.value, leap: lunar && f.leap.checked,
      hour: f.nohour.checked ? null : h, minute: f.nohour.checked ? 0 : m, place: f.place.value, tz: f.place.value === '__other' ? '' : placeTz(f.place.value),
      career: f.career.value, relationship: f.relationship.value };
  };

  f.onsubmit = async e => {
    e.preventDefault(); err.hidden = true; ok.textContent = '';
    const p = read();
    if (!(p.year >= 1900 && p.year <= 2049)) { err.textContent = 'Năm sinh cần trong khoảng 1900 đến 2049.'; err.hidden = false; return; }
    try {
      if (p.cal === 'lunar') { const c = await post('/api/lunar-to-solar', { day: p.day, month: p.month, year: p.year, leap: p.leap, calendar: 'vn' }); p.solar = { year: c.solar.year, month: c.solar.month, day: c.solar.day }; }
      const r = await api('/api/me/profile', { method: 'PUT', body: JSON.stringify(p) });
      const j = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(r.status === 400 ? 'Thông tin chưa hợp lệ (kiểm tra lại ngày sinh).' : 'Chưa lưu được, vui lòng thử lại.');
      profileState.profile = j.profile; fill(j.profile); ok.textContent = 'Đã lưu.';
      dispatchEvent(new CustomEvent('tvbt:profile', { detail: j.profile }));
    } catch (x) { err.textContent = x.message; err.hidden = false; }
  };
  $('[data-run]', f).onclick = () => profileState.profile && onRun(profileState.profile);

  async function load() {
    if (!session.user) return;
    try {
      const r = await api('/api/me/profile'); if (!r.ok) return;
      profileState.profile = (await r.json()).profile; profileState.loaded = true;
      fill(profileState.profile);
      if (profileState.profile) { onPrefill(profileState.profile); dispatchEvent(new CustomEvent('tvbt:profile', { detail: profileState.profile })); }
    } catch { /* the profile is optional: the form keeps its sample values */ }
  }
  if (session.ready) load(); else addEventListener('tvbt:account', load, { once: true });
  return { reset: () => { profileState.profile = null; fill(null); } };
}
