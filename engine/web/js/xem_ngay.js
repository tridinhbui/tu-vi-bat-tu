// Xem ngày: month grid from /api/calendar (all numbers are computed by the engine; this file only draws them).
import { $, esc } from './util.js';
import { readSaved } from './mine.js';

const BR = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'];
const WD = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'];
const KEY = 'tvbt-xn-birth';
const store = { get: () => { try { return localStorage.getItem(KEY); } catch { return null; } }, set: v => { try { v ? localStorage.setItem(KEY, v) : localStorage.removeItem(KEY); } catch { /* private mode */ } } };
// the engine container can drop a request while it wakes up: retry 5xx / network errors a few times
const getJSON = async u => { for (let i = 0; i < 4; i++) { try { const r = await fetch(u); if (r.ok) return r.json(); if (r.status < 500) throw new Error(String(r.status)); } catch (e) { if (i === 3) throw e; } await new Promise(r => setTimeout(r, 600 * (i + 1))); } };

const now = new Date(), todayIso = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
const q = new URLSearchParams(location.search);
let Y = +q.get('y') || now.getFullYear(), M = +q.get('m') || now.getMonth() + 1, sel = null, data = null;
const birthYear = () => { const v = +$('#cal-birth').value; return v >= 1901 && v <= 2099 ? v : null; };
const branchOf = y => ((y - 4) % 12 + 12) % 12;          // lunar year number -> earthly branch (4 CE = Giáp Tý)

const mSel = $('#cal-m');
mSel.innerHTML = Array.from({ length: 12 }, (_, i) => `<option value="${i + 1}">Tháng ${i + 1}</option>`).join('');

function lunarText(l) { return `${l.day}/${l.month}${l.leap ? ' nhuận' : ''}`; }

function detail(d) {
  const cc = d.can_chi, tuoi = data.birth_branch;
  const terms = d.terms.map(t => `${esc(t.name)} (${t.kind}) lúc ${t.time}${t.bazi_month_after ? `: từ giờ này trụ tháng Bát Tự là ${esc(t.bazi_month_after)}` : ''}${t.bazi_year_after ? `, trụ năm ${esc(t.bazi_year_after)}` : ''}`).join('<br>');
  $('#cal-detail').innerHTML = `<h2>${esc(d.weekday)}, ${d.day}/${data.month}/${data.year}</h2><dl>
    <dt>Âm lịch</dt><dd>Ngày ${d.lunar.day} tháng ${d.lunar.month}${d.lunar.leap ? ' (nhuận)' : ''} năm ${esc(cc.year.name)} (${d.lunar.year})</dd>
    <dt>Ngày</dt><dd>${esc(cc.day.name)}</dd>
    <dt>Tháng âm</dt><dd>${cc.month ? esc(cc.month.name) : 'tháng nhuận, không gán can chi (chưa có nguồn cho quy ước này)'}</dd>
    <dt>Năm âm</dt><dd>${esc(cc.year.name)}</dd>
    <dt>Bát Tự (đầu ngày)</dt><dd>trụ năm ${esc(d.bazi.year.name)}, trụ tháng ${esc(d.bazi.month.name)}</dd>
    ${terms ? `<dt>Tiết khí</dt><dd>${terms}</dd>` : ''}
    ${tuoi ? `<dt>Với tuổi ${esc(tuoi.name)}</dt><dd>${d.clash ? `Ngày ${esc(BR[cc.day.branch])} xung với tuổi ${esc(tuoi.name)} (lục xung).` : 'Không xung.'}</dd>` : ''}
  </dl>`;
}

function draw() {
  const g = $('#cal-grid'), lead = data.first_weekday;
  const cells = WD.map((w, i) => `<div class="wd${i === 6 ? ' sun' : ''}" aria-hidden="true">${w}</div>`);
  for (let i = 0; i < lead; i++) cells.push('<div class="cal-blank" aria-hidden="true"></div>');
  for (const d of data.days) {
    const wd = (lead + d.day - 1) % 7, cls = ['cal-day', wd === 6 && 'sun', d.date === todayIso && 'today', d.clash && 'clash', d.terms.length && 'tkd'].filter(Boolean).join(' ');
    const first = d.lunar.day === 1 || d.day === 1;
    const label = `${d.weekday} ${d.day}/${data.month}, âm lịch ${lunarText(d.lunar)}, ngày ${d.can_chi.day.name}${d.terms.length ? ', ' + d.terms.map(t => t.name).join(', ') : ''}${d.clash ? ', xung tuổi' : ''}`;
    cells.push(`<button type="button" class="${cls}" data-d="${d.day}" aria-pressed="${sel === d.day}" aria-label="${esc(label)}"><span class="sd">${d.day}</span>`
      + `<span class="ld${d.lunar.day === 1 ? ' m1' : ''}">${first ? lunarText(d.lunar) : d.lunar.day}</span><span class="gz">${esc(d.can_chi.day.name)}</span>`
      + (d.terms.length ? `<span class="tk">${esc(d.terms.map(t => t.name).join(', '))}</span>` : '') + '</button>');
  }
  g.innerHTML = cells.join('');
  g.setAttribute('role', 'group'); g.setAttribute('aria-label', `Lịch tháng ${data.month}/${data.year}`);
  const tuoi = data.birth_branch;
  $('#cal-tuoi').textContent = tuoi ? `Tuổi ${tuoi.name}: ngày ${tuoi.clashes_with} xung với tuổi (đánh dấu "xung"), ${data.days.filter(d => d.clash).length} ngày trong tháng này.` : 'Nhập năm sinh âm lịch để đánh dấu những ngày xung với tuổi.';
  const pick = data.days.find(d => d.day === sel) || data.days.find(d => d.date === todayIso);
  if (pick) { sel = pick.day; g.querySelector(`[data-d="${sel}"]`)?.setAttribute('aria-pressed', 'true'); detail(pick); } else $('#cal-detail').innerHTML = '';
}

async function load() {
  mSel.value = String(M); $('#cal-y').value = String(Y);
  const by = birthYear(), u = `/api/calendar?year=${Y}&month=${M}${by ? '&branch=' + branchOf(by) : ''}`;
  history.replaceState(null, '', `?y=${Y}&m=${M}`);
  try { data = await getJSON(u); draw(); }
  catch { $('#cal-grid').innerHTML = '<p class="note">Chưa tải được lịch. Vui lòng thử lại sau ít giây.</p>'; }
}
const go = (dy, dm) => { M += dm; Y += dy; if (M < 1) { M = 12; Y--; } if (M > 12) { M = 1; Y++; } Y = Math.min(2099, Math.max(1901, Y)); sel = null; load(); };

$('#cal-prev').onclick = () => go(0, -1);
$('#cal-next').onclick = () => go(0, 1);
$('#cal-today').onclick = () => { Y = now.getFullYear(); M = now.getMonth() + 1; sel = now.getDate(); load(); };
mSel.onchange = () => { M = +mSel.value; sel = null; load(); };
$('#cal-y').onchange = () => { const v = +$('#cal-y').value; if (v >= 1901 && v <= 2099) { Y = v; sel = null; load(); } };
$('#cal-birth').onchange = () => { store.set(birthYear() ? String(birthYear()) : ''); load(); };
$('#cal-grid').onclick = e => { const b = e.target.closest('.cal-day'); if (!b) return; sel = +b.dataset.d; draw(); };

// Birth year: what the visitor typed last time, else the lunar year of the first chart saved as "Tôi" on this device.
(async () => {
  const saved = store.get();
  if (saved) $('#cal-birth').value = saved;
  else {
    const me = readSaved().find(x => x.rel === 'Tôi');
    if (me?.req?.year) {
      try {
        const m = await getJSON(`/api/calendar?year=${me.req.year}&month=${me.req.month}`);
        const d = m.days.find(x => x.day === me.req.day);
        if (d) $('#cal-birth').value = String(d.lunar.year);
      } catch { /* optional */ }
    }
  }
  load();
})();
