// /chiem-tinh/ page controller: form → POST /api/west/chart → wheel, detail panel, tables, reading, vận hạn. Holds the page state;
// every figure on screen is read from the engine's responses.
import { $, $$, esc } from '../util.js';
import { westPost } from './api.js';
import { createWheel } from './wheel.js';
import { detailHtml, detailEmpty } from './detail.js';
import { positionsTable, outerTable, cuspsTable, aspectsList, aspectsGrid, dignityTable, structureHtml, srRelation } from './tables.js';
import { initBirthForm, placeBox, latLonTxt } from './form.js';
import { initForecast } from './timeline.js';
import { loadReading, redrawReading } from './reading.js';
import { initGlossary, loadGlossary, autoLink } from '../glossary.js';
import { initPaywall } from '../paywall.js';
import { initSynastry } from './synastry.js';
import * as store from './store.js';
import { WARN, ASPECT, bodyName, bodyGlyph, aspName, aspGlyph, signLabel, num, fmtDate, zonedMs, zonedParts, isoDay, hhmm, HOUSE_SYS } from './vocab.js';

const S = { gender: null, inp: null, natal: null, mode: 'natal', whenMs: Date.now(), srYear: new Date().getFullYear(), srPlace: null, view: null, sel: null, deep: false, sort: 'orb', tab: 'pos', reqSeq: 0 };
const res = $('#ket-qua');
const notice = (title, text, kind = 'info', extra = '') => `<div class="notice ${kind}" role="note"><svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><circle cx="9" cy="9" r="7.5" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M9 8v4.5M9 5.4v.1" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg><div><b>${title}</b>${text ? `<p>${text}</p>` : ''}${extra}</div></div>`;

// ----- wheel + detail -----
const detail = $('#detail');
const wheel = createWheel($('#wheel'), { onSelect: s => { S.sel = s; showDetail(); } });
const showDetail = () => {
  const v = S.view; if (!v) return;
  detail.innerHTML = (S.sel && detailHtml({ chart: v.chart, outer: v.outer, tz: S.inp.birth.tz }, S.sel)) || detailEmpty(!!v.chart.angles);
};
$('#z-in').onclick = () => wheel.zoom(1.35);
$('#z-out').onclick = () => wheel.zoom(1 / 1.35);
$('#z-reset').onclick = () => wheel.reset();
$('#wheel').addEventListener('wt-zoom', e => { $('#z-reset').disabled = e.detail <= 1.01; $('#z-level').textContent = `${Math.round(e.detail * 100)}%`; });

function select(s, { scroll = true } = {}) {
  S.sel = s; wheel.select(s); showDetail();
  if (scroll) {
    const r = $('.wt-stage').getBoundingClientRect();
    if (r.top < 60 || r.top > innerHeight * .5) $('.wt-stage').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  }
}
// any [data-pick] button on the page (tables, detail panel, profections) selects that thing on the wheel
document.addEventListener('click', e => {
  const b = e.target.closest('[data-pick]');
  if (b && res.contains(b)) {
    const [k, x] = b.dataset.pick.split(':');
    const s = k === 'house' ? { kind: 'house', n: +x } : k === 'aspect' || k === 'link' ? { kind: k, i: +x } : { kind: k, id: x };
    if ((k === 'aspect' || k === 'planet' || k === 'house') && S.mode !== 'natal' && S.mode !== 'sr' && b.closest('#bang, #van-han')) { setMode('natal').then(() => select(s, { scroll: !detail.contains(b) })); return; }
    select(s, { scroll: !detail.contains(b) });
    return;
  }
  const ev = e.target.closest('[data-ev]');
  if (ev && res.contains(ev)) { if (S.mode !== 'natal') setMode('natal').then(() => select(JSON.parse(ev.dataset.ev))); else select(JSON.parse(ev.dataset.ev)); }
});

// ----- header of the result -----
function renderHead() {
  const n = S.natal, b = S.inp.birth, t = n.time;
  $('#res-title').textContent = b.name ? `Bản đồ sao của ${b.name}` : 'Bản đồ sao cá nhân';
  const date = `${String(b.day).padStart(2, '0')}/${String(b.month).padStart(2, '0')}/${b.year}`;
  const off = t.offset_hours != null ? `UTC${t.offset_hours >= 0 ? '+' : '−'}${num(Math.abs(t.offset_hours), 2)}` : '';
  $('#res-sub').innerHTML = [`<span>${esc(date)}${b.hour != null ? ` lúc ${esc(hhmm(b))}` : ' · không rõ giờ'}</span>`,
    b.hour != null ? `<span>${esc(off)}${t.dst ? ' · giờ mùa hè' : ''}${t.lmt ? ' · giờ địa phương trung bình' : ''}</span>` : '',
    `<span>${esc(b.place || 'Nơi sinh nhập tay')} · ${latLonTxt(b.lat, b.lon)}</span>`,
    b.hour != null ? `<span>UT ${esc(t.utc.slice(0, 16).replace('T', ' '))}</span>` : ''].filter(Boolean).join('');
  const big = [['sun', n.bodies.sun], ['moon', n.bodies.moon], ...(n.angles ? [['asc', n.angles.asc]] : [])];
  $('#res-big').innerHTML = big.map(([id, p]) => `<button type="button" class="wt-bigc" data-pick="planet:${id}"><small>${esc(bodyName(id).replace(/\s*\(.*\)$/, ''))}</small>${signLabel(p.sign)}</button>`).join('')
    + (n.sect ? `<span class="wt-bigc static"><small>Phe</small>${n.sect.is_day ? 'Ban ngày' : 'Ban đêm'}</span>` : '');
  // notes: warnings, the DST overlap choice, local mean time
  const notes = [];
  if (t.ambiguous) {
    const f = b.fold || 0;
    notes.push(notice('Giờ này xảy ra hai lần trong ngày', `Lúc ${esc(hhmm(b))} ngày ${esc(date)} đồng hồ ở ${esc(b.tz)} được vặn lùi, nên giờ này lặp lại. Chọn đúng lần theo giấy khai sinh:`, 'warn',
      `<div class="seg wt-fold" role="group" aria-label="Chọn lần xảy ra của giờ sinh"><button type="button" data-fold="0" aria-pressed="${f === 0}">Giờ mùa hè (lần thứ nhất)</button><button type="button" data-fold="1" aria-pressed="${f === 1}">Giờ chuẩn (lần thứ hai)</button></div>`));
  }
  for (const w of n.warnings || []) if (WARN[w]) notes.push(notice(w === 'no_time' ? 'Bản đồ không có giờ sinh' : 'Hệ nhà thay thế', esc(WARN[w]) + (w === 'no_time' && n.moon_day_range ? ` Trong ngày sinh, Mặt Trăng đi từ ${esc(n.moon_day_range.start.fmt)} ${signLabel(n.moon_day_range.start.sign)} đến ${esc(n.moon_day_range.end.fmt)} ${signLabel(n.moon_day_range.end.sign)} (cung đậm trên bánh xe).` : '') + (w === 'no_time' ? ' Không có cung Mọc nên bánh xe đặt 0° Bạch Dương ở vị trí 9 giờ.' : ''), 'info'));
  if (t.lmt) notes.push(notice('Giờ địa phương trung bình', 'Thời điểm sinh trước khi nơi này dùng múi giờ chuẩn, nên giờ được quy đổi theo kinh độ nơi sinh (LMT).'));
  $('#res-notes').innerHTML = notes.join('');
  $$('[data-fold]').forEach(x => x.onclick = () => { const inp = structuredClone(S.inp); inp.birth.fold = +x.dataset.fold; $('#birth-form').dataset.fold = inp.birth.fold; compute(inp); });
}

// ----- "Hiểu bản đồ sao trong 3 phút": the page explained with this chart's own Sun, Moon and Ascendant -----
function render3min() {
  const n = S.natal, b = n.bodies, asc = n.angles?.asc, sys = HOUSE_SYS[n.houses?.system] || 'Placidus';
  const li = (h, t) => `<li><b>${h}.</b> ${t}</li>`;
  const host = $('#wt-3min-body');
  host.innerHTML = `<ol class="wt-3min-l">`
    + li('Bánh xe là bầu trời lúc bạn sinh', 'Vòng ngoài là mười hai cung hoàng đạo; các ký hiệu bên trong là vị trí các hành tinh nhìn từ nơi sinh; các đường kẻ ở giữa là góc hợp giữa hai hành tinh (đường đỏ: kiểu căng, đường xanh: kiểu hài hòa).')
    + li('Ba điểm quan trọng nhất', `Mặt Trời của bạn ở ${signLabel(b.sun.sign)}: phần lõi bền của tính cách. Mặt Trăng ở ${signLabel(b.moon.sign)}: đời sống cảm xúc. `
      + (asc ? `Cung Mọc ở ${signLabel(asc.sign)}: cách bạn hiện ra với người khác; cung Mọc đổi khoảng mỗi hai giờ nên cần giờ sinh đúng.` : 'Không có giờ sinh nên chưa biết cung Mọc, điểm cho biết cách bạn hiện ra với người khác.'))
    + li('Mười hai nhà là mười hai mảng đời', `Nhà 1 là bản thân, Nhà 2 tiền bạc, Nhà 7 hôn nhân, Nhà 10 nghề nghiệp... Bánh xe chia nhà theo ${esc(sys)}; Lilly và Valens chia khác, nên một hành tinh có thể mang số nhà khác ở từng trường phái, và bài luận luôn ghi rõ đang dùng cách nào.`)
    + li('Hành tinh mạnh hay yếu', 'Mỗi hành tinh mạnh lên hay yếu đi tùy cung nó đứng, gọi là phẩm vị (bảng "Phẩm vị"). Hành tinh đứng gần các trục chính (nhà góc) tác động rõ hơn.')
    + li('Ba trường phái đặt cạnh nhau', 'Hy Lạp cổ đại (Ptolemy, Valens), truyền thống (Lilly, thế kỷ XVII) và hiện đại (Alan Leo, đầu thế kỷ XX). Mỗi đoạn luận ghi nó theo trường phái nào; khi hai trường phái cho kết quả khác nhau, bài luận nói rõ thay vì trộn lại.')
    + li('Cách đọc trang này', '“Đọc nhanh” cho phần tóm tắt dễ hiểu của từng chương; “Đọc sâu” thêm lập luận, chứng thuận và nghịch, nguồn sách. Bấm vào một dữ kiện (ví dụ “Sao Kim 17°05′ Ma Kết”) để thấy nó trên bánh xe; bấm vào chữ gạch chấm để xem giải thích thuật ngữ.')
    + li('Giới hạn', 'Chiêm tinh là một truyền thống đọc biểu tượng, không phải phép dự báo đã được khoa học kiểm chứng. Bài luận nói về khuynh hướng và thời điểm chủ đề được nhắc tới, không phải lời đoán chắc chắn.')
    + '</ol>';
  loadGlossary().then(() => autoLink(host, 'west'));
}

// ----- chart switcher -----
const MODES = { natal: 'Bản đồ gốc', transit: 'Transit', progressed: 'Tiến trình', sr: 'Solar Return' };
$$('#modes [role=tab]').forEach(b => b.addEventListener('click', () => setMode(b.dataset.mode)));
$('#modes').addEventListener('keydown', e => {
  const tabs = $$('#modes [role=tab]'), i = tabs.indexOf(document.activeElement);
  if (i < 0 || !['ArrowLeft', 'ArrowRight'].includes(e.key)) return;
  const j = (i + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length; tabs[j].focus(); setMode(tabs[j].dataset.mode);
});

function modeControls() {
  const ctl = $('#mode-ctl'), tz = S.inp.birth.tz;
  if (S.mode === 'transit' || S.mode === 'progressed') {
    const p = zonedParts(tz, S.whenMs);
    ctl.innerHTML = `<div class="wt-mctl"><label class="fld"><span>Ngày</span><input type="date" id="m-date" value="${isoDay(p)}" min="1900-01-01" max="2100-12-31"></label>`
      + (S.mode === 'transit' ? `<label class="fld"><span>Giờ <small>(${esc(tz)})</small></span><input type="time" id="m-time" value="${hhmm(p)}"></label>` : '')
      + `<div class="wt-quick" role="group" aria-label="Chọn nhanh ngày"><button type="button" class="btn btn-ghost btn-sm" data-q="now">Hôm nay</button>`
      + [['d', -1, '−1 ngày'], ['d', 1, '+1 ngày'], ['m', -1, '−1 tháng'], ['m', 1, '+1 tháng'], ['y', -1, '−1 năm'], ['y', 1, '+1 năm']].map(([u, k, l]) => `<button type="button" class="btn btn-ghost btn-sm" data-q="${u}${k}">${l}</button>`).join('')
      + `</div></div><p class="hint">${S.mode === 'transit' ? 'Vòng ngoài: vị trí các hành tinh trên bầu trời lúc này, nhìn từ nơi sinh; các đường ở giữa là góc hợp transit đang nằm trong orb với điểm gốc.' : 'Vòng ngoài: bản đồ tiến trình thứ cấp (một ngày sau sinh = một năm tuổi) cho ngày đã chọn; các trục tiến theo cung Mặt Trời.'}</p>`;
    const apply = () => {
      const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec($('#m-date').value); if (!m) return;
      const t = /^(\d{2}):(\d{2})/.exec($('#m-time')?.value || '12:00');
      S.whenMs = zonedMs(tz, +m[1], +m[2], +m[3], t ? +t[1] : 12, t ? +t[2] : 0); loadMode();
    };
    $('#m-date').onchange = apply; if ($('#m-time')) $('#m-time').onchange = apply;
    $$('[data-q]', ctl).forEach(b => b.onclick = () => {
      const q = b.dataset.q;
      if (q === 'now') S.whenMs = Date.now();
      else {
        const u = q[0], k = +q.slice(1), p0 = zonedParts(tz, S.whenMs);
        S.whenMs = zonedMs(tz, p0.year + (u === 'y' ? k : 0), p0.month + (u === 'm' ? k : 0), p0.day + (u === 'd' ? k : 0), p0.hour, p0.minute);
      }
      modeControls(); loadMode();
    });
  } else if (S.mode === 'sr') {
    const pl = S.srPlace;
    ctl.innerHTML = `<div class="wt-mctl"><label class="fld"><span>Năm</span><input type="number" id="sr-year" inputmode="numeric" min="1900" max="2100" value="${S.srYear}"></label>`
      + `<div class="fld wt-plfld"><label for="sr-place">Nơi đón sinh nhật</label><div class="wt-plbox"><input id="sr-place" autocomplete="off" placeholder="Mặc định: nơi sinh" value="${esc(pl ? pl.name : '')}"><ul id="sr-place-list" class="wt-pl" hidden></ul></div></div>`
      + `<button type="button" class="btn btn-ghost btn-sm" id="sr-home"${pl ? '' : ' disabled'}>Dùng nơi sinh</button></div>`
      + `<p class="hint">Solar Return là bản đồ của khoảnh khắc Mặt Trời trở về đúng độ gốc trong năm đã chọn, lập tại nơi bạn ở lúc đó. ${pl ? `Đang dùng ${esc(pl.name)} (${latLonTxt(pl.lat, pl.lon)}, ${esc(pl.tz)}).` : 'Đang dùng nơi sinh.'}</p>`;
    $('#sr-year').onchange = () => { const y = parseInt($('#sr-year').value, 10); if (y >= 1900 && y <= 2100) { S.srYear = y; loadMode(); } };
    placeBox($('#sr-place'), $('#sr-place-list'), { onPick: p => { S.srPlace = p; modeControls(); loadMode(); } });
    $('#sr-home').onclick = () => { S.srPlace = null; modeControls(); loadMode(); };
  } else ctl.innerHTML = '';
}

async function setMode(m) {
  S.mode = m;
  $$('#modes [role=tab]').forEach(b => { const on = b.dataset.mode === m; b.setAttribute('aria-selected', String(on)); b.tabIndex = on ? 0 : -1; });
  modeControls();
  await loadMode();
}

async function loadMode() {
  const seq = ++S.reqSeq, n = S.natal, inp = S.inp, b = inp.birth, extra = $('#mode-extra');
  const done = view => { if (seq !== S.reqSeq) return false; S.view = view; S.sel = null; wheel.render(view); showDetail(); renderTables(); return true; };
  $('#stage-err').hidden = true;
  try {
    if (S.mode === 'natal') { done({ chart: n }); extra.innerHTML = ''; return; }
    $('.wt-stage').classList.add('busy');
    if (S.mode === 'transit') {
      const p = zonedParts(b.tz, S.whenMs), when = S.whenMs;
      // one ±120-day search for every body (the Moon included), so a live contact shows when it entered and leaves the orb
      const span = d => ({ ...inp, start: new Date(when - d * 864e5).toISOString(), end: new Date(when + d * 864e5).toISOString(), transiting: ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto', 'chiron'] });
      const [tc, tr] = await Promise.all([
        westPost('chart', { birth: { ...p, lat: b.lat, lon: b.lon, tz: b.tz, place: b.place, name: '' }, options: inp.options }),
        westPost('transits', span(120)),
      ]);
      const tag = t => t.events.map(e => ({ ...e, win: [t.start, t.end] }));
      const live = tag(tr).filter(e => (!e.start || Date.parse(e.start) <= when) && (!e.end || Date.parse(e.end) >= when));
      const bodies = {}; for (const id of ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto', 'chiron']) bodies[id] = tc.bodies[id];
      const label = `Transit ${fmtDate(new Date(when).toISOString(), b.tz, { time: true })}`;
      if (!done({ chart: n, outer: { label, bodies, links: live.map(e => ({ a: e.transiting, b: e.natal, type: e.aspect, event: e })) } })) return;
      extra.innerHTML = `<div class="wt-two">${outerTable(label, bodies)}<div><h3 class="wt-th">Góc hợp transit đang trong orb (${live.length})</h3>${live.length ? `<ul class="wt-abs">${live.map((e, i) => `<li><button type="button" class="wt-ab tone-${ASPECT[e.aspect]?.tone || 'soft'}" data-pick="link:${i}"><span class="wt-g" aria-hidden="true">${bodyGlyph(e.transiting)} ${aspGlyph(e.aspect)} ${bodyGlyph(e.natal)}</span> ${esc(bodyName(e.transiting))} ${esc(aspName(e.aspect).toLowerCase())} ${esc(bodyName(e.natal))} gốc<small>${e.exact.length ? 'chính xác ' + esc(fmtDate(e.exact[0], b.tz)) : ''}</small></button></li>`).join('')}</ul>` : '<p class="note">Không có góc hợp transit nào trong orb vào lúc này.</p>'}<p class="hint">Đây là các góc đang trong orb đúng lúc đã chọn. Cả năm, với bộ lọc “Chỉ mốc nổi bật”, nằm ở phần <a href="#van-han">Vận hạn</a> bên dưới.</p></div></div>`;
    } else if (S.mode === 'progressed') {
      const d = await westPost('progressions', { ...inp, when: new Date(S.whenMs).toISOString(), span_years: 2 });
      const bodies = { ...d.progressed.bodies };
      for (const k of ['asc', 'mc']) if (d.progressed.angles?.[k]) bodies[k] = d.progressed.angles[k];
      const label = `Tiến trình ${fmtDate(new Date(S.whenMs).toISOString(), b.tz)} (tuổi ${num(d.progressed.age_years, 1)})`;
      if (!done({ chart: n, outer: { label, bodies } })) return;
      const ang = d.progressed.angles;
      extra.innerHTML = outerTable(label, d.progressed.bodies, { natalHouse: true }) + (ang ? `<p class="hint">Trục tiến trình (vẽ ở vòng ngoài): ASC ${esc(ang.asc.fmt)} ${signLabel(ang.asc.sign)} · MC ${esc(ang.mc.fmt)} ${signLabel(ang.mc.sign)}.</p>` : '');
    } else if (S.mode === 'sr') {
      const body = { ...inp, year: S.srYear };
      if (S.srPlace) Object.assign(body, { lat: S.srPlace.lat, lon: S.srPlace.lon, tz: S.srPlace.tz, place: S.srPlace.name });
      const sr = await westPost('solar-return', body);
      if (!done({ chart: sr.chart, sr })) return;
      extra.innerHTML = `<h3 class="wt-th">Solar Return ${S.srYear}</h3>` + srRelation(sr);
    }
  } catch (e) {
    if (seq !== S.reqSeq) return;
    $('#stage-err').innerHTML = notice('Chưa lập được bản đồ này', esc(e.message), 'warn'); $('#stage-err').hidden = false;
  } finally { if (seq === S.reqSeq) $('.wt-stage').classList.remove('busy'); }
}

// ----- tables -----
const TABS = { pos: 'Vị trí', houses: 'Nhà', aspects: 'Góc hợp', dign: 'Phẩm vị', struct: 'Cấu trúc' };
$$('#tbl-tabs [role=tab]').forEach(b => b.addEventListener('click', () => { S.tab = b.dataset.tab; renderTables(); }));
$('#tbl-tabs').addEventListener('keydown', e => {
  const tabs = $$('#tbl-tabs [role=tab]'), i = tabs.indexOf(document.activeElement);
  if (i < 0 || !['ArrowLeft', 'ArrowRight'].includes(e.key)) return;
  const j = (i + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length; tabs[j].focus(); S.tab = tabs[j].dataset.tab; renderTables();
});
function renderTables() {
  const ch = S.view?.chart || S.natal; if (!ch) return;
  $('#tbl-for').textContent = S.view?.sr ? `của Solar Return ${S.srYear}` : 'của bản đồ gốc';
  $$('#tbl-tabs [role=tab]').forEach(b => { const on = b.dataset.tab === S.tab; b.setAttribute('aria-selected', String(on)); b.tabIndex = on ? 0 : -1; });
  const P = id => $('#tp-' + id);
  P('pos').innerHTML = positionsTable(ch);
  P('houses').innerHTML = cuspsTable(ch);
  P('aspects').innerHTML = `<div class="wt-two wt-asp2"><div><h3 class="wt-th">Danh sách</h3>${aspectsList(ch, S.sort)}</div><div><h3 class="wt-th">Lưới góc hợp</h3>${aspectsGrid(ch)}</div></div>`;
  P('dign').innerHTML = dignityTable(ch);
  P('struct').innerHTML = structureHtml(ch);
  Object.keys(TABS).forEach(k => { P(k).hidden = k !== S.tab; });
  $$('[data-sort]', P('aspects')).forEach(b => b.onclick = () => { S.sort = b.dataset.sort; renderTables(); $(`[data-sort="${S.sort}"]`)?.focus(); });
  const sys = $('#wt-cusp-sys');
  if (sys) sys.onchange = () => { const inp = structuredClone(S.inp); inp.options.house_system = sys.value; form.setHouse(sys.value); compute(inp, { keepMode: true, scroll: false }); };
}

// ----- reading -----
const setDeep = deep => {
  S.deep = deep;
  $$('#read-mode button').forEach(x => x.setAttribute('aria-pressed', String((x.dataset.deep === '1') === deep)));
  if (!redrawReading(deep)) loadReading($('#reading'), S.inp, S.natal, { deep, gender: S.gender });
};
$$('#read-mode button').forEach(b => b.onclick = () => setDeep(b.dataset.deep === '1'));
// "Xem phân tích chi tiết" under a chapter's summary: Đọc sâu, back at that chapter
$('#reading').addEventListener('click', e => {
  const b = e.target.closest('[data-deepen]'); if (!b) return;
  setDeep(true); document.getElementById('wt-c-' + b.dataset.deepen)?.scrollIntoView({ block: 'start' });
});

// ----- the paid part of the reading (src/billing/west.ts): lock cards open a package for this birth, then the reading is drawn again -----
initPaywall(() => S.inp?.birth || null);
initGlossary();
addEventListener('tvbt:unlocked', () => { if (S.inp) loadReading($('#reading'), S.inp, S.natal, { deep: S.deep, gender: S.gender }); });
// signing in from a lock card comes back to this page (?next=); the chart on screen is opened again once
const RESUME = 'tvbt.west.resume';
document.addEventListener('click', e => {
  if (!e.target.closest('a[data-pw-next]') || !S.inp) return;
  try { sessionStorage.setItem(RESUME, JSON.stringify({ ...S.inp, gender: S.gender })); } catch { /* storage unavailable */ }
});
const takeResume = () => { try { const v = sessionStorage.getItem(RESUME); sessionStorage.removeItem(RESUME); return v ? JSON.parse(v) : null; } catch { return null; } };

// ----- vận hạn -----
const forecast = initForecast($('#forecast'), { getCtx: () => S.inp && { inp: S.inp, natal: S.natal } });

// ----- synastry: person A is the chart on the page -----
const syn = initSynastry($('#syn'), { getA: () => S.inp && { inp: S.inp, gender: S.gender, natal: S.natal } });

// ----- compute -----
let forecastIO = null;
async function compute(inp0, { keepMode = false, scroll = true } = {}) {
  // gender goes to /reading only; every other call gets {birth, options}
  const gender = inp0.gender === undefined ? S.gender : inp0.gender, inp = { birth: inp0.birth, options: inp0.options };
  const natal = await westPost('chart', inp);
  S.inp = inp; S.natal = natal; S.gender = gender || null;
  store.remember({ ...inp, gender: S.gender }); renderLists(); syn.refresh();
  res.hidden = false; $('#syn').hidden = false;
  renderHead(); render3min();
  $('#act-save').textContent = store.isSaved(inp) ? 'Đã lưu hồ sơ' : 'Lưu hồ sơ';
  $('#share-box').hidden = true;
  if (!keepMode) { S.mode = 'natal'; S.whenMs = Date.now(); S.srYear = new Date().getFullYear(); S.srPlace = null; }
  await setMode(S.mode);
  const reading = loadReading($('#reading'), inp, natal, { deep: S.deep, gender: S.gender });
  // the three forecast panels load once the reading is done and only when the "Vận hạn" section comes near the screen
  // (a plain scroll check: it also works where IntersectionObserver is throttled)
  const fc = $('#forecast'), near = () => fc.getBoundingClientRect().top < innerHeight + 800;
  if (forecastIO) removeEventListener('scroll', forecastIO);
  forecastIO = null;
  forecast.reset();
  reading.finally(() => {
    if (near()) { forecast.load(); return; }
    forecastIO = () => { if (near()) { removeEventListener('scroll', forecastIO); forecastIO = null; forecast.load(); } };
    addEventListener('scroll', forecastIO, { passive: true });
  });
  if (scroll) res.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  $('#res-title').focus({ preventScroll: true });
}
const form = initBirthForm($('#birth-form'), { onSubmit: inp => compute(inp) });

// ----- profiles, history, share, print -----
const when = b => `${String(b.day).padStart(2, '0')}/${String(b.month).padStart(2, '0')}/${b.year}${b.hour != null ? ' ' + hhmm(b) : ''}`;
function renderLists() {
  const pr = store.profiles(), rc = store.recent();
  $('#prof-list').innerHTML = pr.length ? pr.map(p => `<li><button type="button" class="wt-li-open" data-open-prof="${esc(p.id)}"><b>${esc(p.label || p.birth.name || 'Không tên')}</b><small>${esc(when(p.birth))} · ${esc(p.birth.place || '')}</small></button><button type="button" class="wt-li-del" data-del-prof="${esc(p.id)}" aria-label="Xóa hồ sơ ${esc(p.label || p.birth.name || when(p.birth))}">Xóa</button></li>`).join('')
    : '<li class="hint">Chưa có hồ sơ nào. Lập bản đồ rồi bấm “Lưu hồ sơ”.</li>';
  $('#recent-list').innerHTML = rc.length ? rc.map((p, i) => `<li><button type="button" class="wt-li-open" data-open-recent="${i}"><b>${esc(p.birth.name || 'Không tên')}</b><small>${esc(when(p.birth))} · ${esc(p.birth.place || '')}</small></button></li>`).join('')
    : '<li class="hint">Các bản đồ bạn mở sẽ hiện ở đây.</li>';
  $('#recent-clear').hidden = !rc.length;
  if (S.inp) syn.refresh();
}
const openSaved = async x => { form.fill(x); try { await compute({ birth: x.birth, options: { ...x.options }, gender: x.gender || null }); } catch (e) { form.fail(e.message); $('#lap-ban-do').scrollIntoView(); } };
$('#profiles').addEventListener('click', e => {
  const o = e.target.closest('[data-open-prof]'), d = e.target.closest('[data-del-prof]'), r = e.target.closest('[data-open-recent]');
  if (o) { const p = store.profiles().find(x => x.id === o.dataset.openProf); if (p) openSaved(p); }
  if (r) { const p = store.recent()[+r.dataset.openRecent]; if (p) openSaved(p); }
  if (d) { const p = store.profiles().find(x => x.id === d.dataset.delProf); if (p && confirm(`Xóa hồ sơ “${p.label || p.birth.name || when(p.birth)}” khỏi trình duyệt này?`)) { store.deleteProfile(p.id); renderLists(); if (S.inp) $('#act-save').textContent = store.isSaved(S.inp) ? 'Đã lưu hồ sơ' : 'Lưu hồ sơ'; } }
});
$('#recent-clear').onclick = () => { store.clearRecent(); renderLists(); };
$('#act-save').onclick = () => {
  const ok = store.saveProfile({ ...S.inp, gender: S.gender }, S.inp.birth.name);
  $('#act-save').textContent = ok ? 'Đã lưu hồ sơ' : 'Không lưu được';
  $('#act-msg').textContent = ok ? 'Đã lưu vào trình duyệt này. Hồ sơ không được gửi lên máy chủ.' : 'Trình duyệt đang chặn bộ nhớ cục bộ (chế độ riêng tư?), nên chưa lưu được.';
  renderLists();
};
$('#act-share').onclick = () => {
  const box = $('#share-box'); box.hidden = false;
  $('#share-url').value = store.shareUrl({ ...S.inp, gender: S.gender }); $('#share-url').select();
};
$('#share-copy').onclick = async () => {
  try { await navigator.clipboard.writeText($('#share-url').value); $('#share-msg').textContent = 'Đã sao chép liên kết.'; }
  catch { $('#share-url').select(); $('#share-msg').textContent = 'Hãy sao chép thủ công (Ctrl/Cmd + C).'; }
};
$('#share-close').onclick = () => { $('#share-box').hidden = true; $('#act-share').focus(); };
$('#act-pdf').onclick = async () => {
  // the printout carries the whole reading and the forecast panels, whatever is open on screen
  const btn = $('#act-pdf'), deep0 = S.deep;
  btn.disabled = true; btn.textContent = 'Đang chuẩn bị…';
  try {
    if (forecastIO) { removeEventListener('scroll', forecastIO); forecastIO = null; }
    await forecast.load({ keepRef: true });
    if (!deep0) setDeep(true);
  } finally { btn.disabled = false; btn.textContent = 'Tải PDF'; }
  window.print();
  if (!deep0) setDeep(false);
};
$('#act-edit').onclick = () => { $('#lap-ban-do').scrollIntoView({ block: 'start' }); $('#birth-form [name=day]').focus({ preventScroll: true }); };
addEventListener('beforeprint', () => { $$('#ket-qua details:not([open])').forEach(d => { d.open = true; d.dataset.printOpened = '1'; }); });
addEventListener('afterprint', () => { $$('[data-print-opened]').forEach(d => { d.open = false; delete d.dataset.printOpened; }); });

renderLists();
// a share link opens straight into its chart
const shared = store.readShare();
const resumed = shared ? null : takeResume();
if (shared || resumed) { const c = shared || resumed; form.fill(c); compute(c).catch(e => { form.fail(e.message); }); }
addEventListener('hashchange', () => { const s = store.readShare(); if (s) { form.fill(s); compute(s).catch(e => form.fail(e.message)); } });
export { S, HOUSE_SYS };
