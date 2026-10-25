// App shell: navigation, home interactions, BirthChartForm, results orchestration.
import { $, $$, esc, bd, DM, post, hourBranch, placeTz, STEMS, BRANCHES, loadMeta, shareMode, beginLoad, endLoad, cancelLoad, isCancel } from './util.js';
import { compass, brandMark } from './compass.js';
import { renderBazi } from './bazi.js';
import { renderTuvi } from './tuvi.js';
import { renderBaziReport, renderTuviReport } from './report.js';
import { notice } from './ui.js';
import { renderHourSweep } from './hours.js';
import { initGlossary, loadGlossary, setChart, autoLink, terms } from './glossary.js';
import { summaryBazi, summaryTuvi, yearCard } from './beginner.js';
import { initCompare } from './compare.js';
import { initPrint, printNow } from './print.js';
import { initChat, initChapterBubbles, dialogueBazi, dialogueTuvi } from './mascots.js';
import { renderSaved, initSave, isSaved, autoSave } from './mine.js';
import { initAccount, session } from './account.js';
import { initAccountPage } from './acctpage.js';
import { focusFor, isOwnChart } from './profile.js';
import { openShareDialog, loadShare, shareBanner, SHARE_HASH } from './share.js';
import { exportBoardPng } from './png.js';
import { initAsk } from './ask.js';
import { initPaywall, takeResume } from './paywall.js';
import { initAiCards } from './ai_card.js';
import { initLive } from './live.js';
import { initGrowth } from './growth.js';
import { renderOverview } from './overview.js';
import { renderHoangDao, hoangdaoChip } from './hoangdao.js';
import { cacheKey, cachedChart, cacheChart, rememberCurrent, forgetCurrent, currentChart } from './chartcache.js';

const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const metaReady = Promise.all([loadMeta(), loadGlossary()]);
// Hidden experimental mode: open the site with ?thu-nghiem (turn off with ?thu-nghiem=off). Kept per tab, never shown to normal visitors.
const EXP_KEY = 'tvbt_exp';
try { const u = new URL(location.href); if (u.searchParams.has('thu-nghiem')) { sessionStorage.setItem(EXP_KEY, u.searchParams.get('thu-nghiem') === 'off' ? '' : '1'); u.searchParams.delete('thu-nghiem'); history.replaceState(null, '', u); } } catch { /* storage unavailable */ }
const expOn = () => { try { return sessionStorage.getItem(EXP_KEY) === '1'; } catch { return false; } };
const expBadge = document.getElementById('exp-badge');
if (expOn()) { expBadge.hidden = false; expBadge.onclick = () => { try { sessionStorage.setItem(EXP_KEY, ''); } catch { /* ignore */ } location.reload(); }; }
initGlossary();
let state = null; // { req, chart, reason, tv }
let sampling = false;  // the sample chart is being opened: it is never kept in Lá số của tôi

// ---------- brand + hero art ----------
$$('[data-brand]').forEach(e => e.innerHTML = brandMark(e.dataset.brand === 'lg' ? 44 : 32));
$('#hero-compass').innerHTML = compass({ animate: !reduce });
$('#load-compass').innerHTML = compass({ animate: false, detail: 'min' });
$('#foot-compass').innerHTML = compass({ animate: false, detail: 'min' });

// ---------- navigation ----------
const TITLE = document.title;
const view = v => { document.body.dataset.view = v; if (v !== 'chart') document.body.classList.remove('sheet-open'); document.title = TITLE; scrollTo({ top: 0 }); };
function setTab(tab, scroll = true) {
  $('#chart-view').dataset.tab = tab;
  document.body.classList.remove('sheet-open');      // a palace sheet left open on the other system must not keep the page dimmed
  $$('.res-tabs button').forEach(b => { const on = b.id === 'tab-' + tab; b.setAttribute('aria-selected', on); b.tabIndex = on ? 0 : -1; });
  if (scroll) scrollTo({ top: 0 });
  requestAnimationFrame(() => dispatchEvent(new Event('resize')));
}
function go(id) {
  // Trang chủ: the whole landing page, also for a signed-in member (app.css hides its welcome sections otherwise)
  document.body.classList.toggle('landing', id === 'hero' || id === 'trang-chu');
  if (id === 'trang-chu') id = 'hero';
  if (id === 'tai-khoan') { if (shareMode.id) { leaveShare('#tai-khoan'); return; } view('account'); acctPage.paint(); history.replaceState(null, '', '#tai-khoan'); return; }
  const tabs = { 'tong-quan': 'overview', 'bat-tu': 'bazi', 'tu-vi': 'tuvi', 'truong-thanh': 'growth' };
  if (tabs[id] && state?.chart) { if (document.body.dataset.view !== 'chart') view('chart'); setTab(tabs[id]); history.replaceState({ v: 'chart' }, '', '#la-so/' + id); return; }
  if (shareMode.id) { leaveShare('#' + id); return; }   // a shared view is read-only: going anywhere else starts the site afresh
  const target = $('#' + id) ? id : 'lap-la-so'; // retired anchors from older links land on the form
  if (document.body.dataset.view !== 'home') view('home');
  requestAnimationFrame(() => $('#' + target)?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' }));
  history.replaceState(null, '', '#' + target);
}
document.addEventListener('click', e => {
  const a = e.target.closest('[data-go]'); if (!a) return;
  e.preventDefault(); go(a.dataset.go);
});
addEventListener('popstate', () => { if (document.body.dataset.view !== 'home') view('home'); });
// next-step buttons inside the result page (summary and end of each report)
document.addEventListener('click', e => {
  const a = e.target.closest('[data-act]'); if (!a) return;
  const act = a.dataset.act;
  if (act === 'sample') { e.preventDefault(); loadSample().then(() => setTab(a.dataset.tab || 'tuvi')); }
  else if (act === 'print') { e.preventDefault(); printNow(); }
  else if (act === 'print-full') { e.preventDefault(); printNow(true); }
  else if (act === 'again') { e.preventDefault(); again(); }
  else if (act === 'save') { e.preventDefault(); $('#save-host button')?.click(); $('.atl-mast').scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' }); }
  else if (act === 'hoangdao') { e.preventDefault(); setTab('tuvi', false); history.replaceState({ v: 'chart' }, '', '#la-so/tu-vi'); requestAnimationFrame(() => $('#hd-card')?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' })); }
  else if (act === 'scroll') { e.preventDefault(); $(a.dataset.target)?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' }); }
});
if (/^#(hoc|kham-pha|tu-vi|bat-tu|gioi-thieu)/.test(location.hash)) history.replaceState(null, '', location.pathname);

// ---------- depth: the reading is always shown in full ('Chuyên sâu': rules, book pages, every tier); the 'Dễ hiểu' mode was removed.
// The data-depth attribute stays so the existing .pro-only / .easy-only markup keeps working.
document.body.dataset.depth = 'pro';
try { localStorage.removeItem('tvbt-depth'); } catch { /* storage unavailable */ }

// ---------- home: Five Elements, library, form ----------


// ----- BirthChartForm -----
const PLACES = { 'Hà Nội': 105.85, 'TP. Hồ Chí Minh': 106.66, 'Đà Nẵng': 108.22, 'Huế': 107.59, 'Hải Phòng': 106.68, 'Cần Thơ': 105.78, 'Nha Trang': 109.19, 'Đà Lạt': 108.44, 'Vinh': 105.68 };
const form = $('#birth-form');
const opt = (v, t, sel) => `<option value="${v}"${sel ? ' selected' : ''}>${t}</option>`;
form.day.innerHTML = Array.from({ length: 31 }, (_, i) => opt(i + 1, i + 1, i + 1 === 17)).join('');
form.month.innerHTML = Array.from({ length: 12 }, (_, i) => opt(i + 1, 'Tháng ' + (i + 1), i + 1 === 5)).join('');
form.place.innerHTML = Object.keys(PLACES).map((p, i) => opt(p, p, i === 1)).join('') + opt('__other', 'Nơi khác / ngoài Việt Nam');
const syncPlace = () => {
  const other = form.place.value === '__other';
  $('#tz-other').hidden = !other;
  if (!other) { form.tz.value = placeTz(form.place.value); form.longitude.value = PLACES[form.place.value]; }
};
form.place.onchange = syncPlace; syncPlace();
const CHI = ['Tý (23h–1h)', 'Sửu (1h–3h)', 'Dần (3h–5h)', 'Mão (5h–7h)', 'Thìn (7h–9h)', 'Tỵ (9h–11h)', 'Ngọ (11h–13h)', 'Mùi (13h–15h)', 'Thân (15h–17h)', 'Dậu (17h–19h)', 'Tuất (19h–21h)', 'Hợi (21h–23h)'];
$('#hour-chi').insertAdjacentHTML('beforeend', CHI.map((c, i) => `<option value="${String(i === 0 ? 0 : 2 * i).padStart(2, '0')}:00">Giờ ${c}</option>`).join(''));
$('#hour-chi').onchange = e => { if (e.target.value) { form.time.value = e.target.value; hint(); } };
let lunarModeOn = false;
const setCal = l => {
  lunarModeOn = l; $('#cal-solar').setAttribute('aria-pressed', !l); $('#cal-lunar').setAttribute('aria-pressed', l);
  $('#leap-wrap').hidden = !l; $('#cal-help').textContent = l ? 'Bạn nhập ngày âm lịch. Hệ thống tự quy đổi sang dương lịch rồi lập lá số.' : 'Bạn nhập ngày dương lịch. Hệ thống tự quy đổi sang âm lịch.';
  form.day.options[0]; form.querySelector('[name=month]').innerHTML = Array.from({ length: 12 }, (_, i) => opt(i + 1, (l ? 'Tháng ' : 'Tháng ') + (i + 1), i + 1 === +form.month.value || (!form.month.value && i + 1 === 5))).join('');
  form.day.innerHTML = Array.from({ length: l ? 30 : 31 }, (_, i) => opt(i + 1, i + 1, i + 1 === Math.min(+form.day.value || 17, l ? 30 : 31))).join('');
};
$('#cal-solar').onclick = () => setCal(false); $('#cal-lunar').onclick = () => setCal(true);
$('#no-hour').onchange = e => { form.time.disabled = e.target.checked; $('#hour-chi').disabled = e.target.checked; $('#time-box').classList.toggle('off', e.target.checked); };
const hint = () => { const [h] = (form.time.value || '00:00').split(':').map(Number);
  if (Number.isNaN(h)) return; $('#hour-hint').textContent = `Giờ ${hourBranch(h)}`; };
form.time.oninput = hint; hint();
$('#solar').onchange = e => { $('#lon-wrap').hidden = !e.target.checked; };

// "Thông tin cá nhân" fills the form once it has loaded, unless the visitor already started typing
let formTouched = false;
form.addEventListener('input', () => { formTouched = true; }, { once: true });
function prefill(p, force = false) {
  if (!p || (formTouched && !force)) return;
  setCal(p.cal === 'lunar');
  form.year.value = p.year; form.month.value = p.month; setCal(p.cal === 'lunar'); form.day.value = p.day; $('#leap').checked = !!p.leap;
  const unknown = p.hour === null; $('#no-hour').checked = unknown; $('#no-hour').onchange({ target: { checked: unknown } });
  if (!unknown) form.time.value = `${String(p.hour).padStart(2, '0')}:${String(p.minute).padStart(2, '0')}`;
  if (p.gender) form.gender.value = p.gender;
  if (p.place && [...form.place.options].some(o => o.value === p.place)) form.place.value = p.place;
  syncPlace(); hint();
  const note = $('.form-sample-note'); if (note) note.innerHTML = 'Các ô đang điền sẵn từ <a class="link" href="#tai-khoan" data-go="tai-khoan">Thông tin cá nhân</a> của bạn.';
}

function readForm() {
  const unknown = $('#no-hour').checked, [h, m] = unknown ? [12, 0] : form.time.value.split(':').map(Number);
  const o = { year: +form.year.value, month: +form.month.value, day: +form.day.value, hour: h, minute: m, gender: form.gender.value, tz: form.tz.value.trim() || 'Asia/Ho_Chi_Minh', calendar: form.calsys.value, zi_rule: form.zi_rule.value, level: +form.level.value };
  if ($('#solar').checked) { o.use_true_solar_time = true; o.longitude = +form.longitude.value; }
  // dignity table chosen on the board (tuvi.js): the whole chart, board and readings, is computed with the same one
  try { const dg = localStorage.getItem('tvbt.dignity'); if (dg === 'khao_luan' || dg === 'toan_thu' || dg === 'thuc_hanh') o.dignity_school = dg; } catch {}
  Object.assign(o, storedVariants());
  return o;
}
const fmtDate = r => `${String(r.day).padStart(2, '0')}/${String(r.month).padStart(2, '0')}/${r.year}`;

// calculation items where the books disagree (tiểu hạn, Tứ Hóa table, Lưu Hà): the viewer's pick, kept per browser
const VARIANT_OK = { tu_hoa_table: ['KL', 'TH', 'TT_WS'], tieu_han_rule: ['TH', 'KL'], luu_ha_table: ['board', 'KL', 'TH'] };
function storedVariants() {
  let v = {}; try { v = JSON.parse(localStorage.getItem('tvbt.variants') || '{}') || {}; } catch { v = {}; }
  return Object.fromEntries(Object.entries(v).filter(([k, x]) => VARIANT_OK[k]?.includes(x)));
}
addEventListener('tvbt:variant', e => {
  const { key, value } = e.detail || {}; if (!VARIANT_OK[key]?.includes(value)) return;
  try { localStorage.setItem('tvbt.variants', JSON.stringify({ ...storedVariants(), [key]: value })); } catch {}
  if (state?.req) (shareMode.id ? compute : generate.bind(null, null))({ ...state.req, [key]: value });
});
addEventListener('tvbt:dignity', e => { if (state?.req) (shareMode.id ? compute : generate.bind(null, null))({ ...state.req, dignity_school: e.detail }); });
// a chapter's Đọc sâu part was opened with xu (js/paywall.js): draw the report again, the server now sends it, and open its fold
addEventListener('tvbt:unlocked', async e => {
  if (!state?.req) return;
  const id = e.detail?.chapter, sys = $('.res-tabs button[aria-selected=true]')?.id?.replace('tab-', '');
  await generate(null, { ...state.req }, { fresh: true });   // the server now sends the bought part: never the copy kept on this device
  if (sys) setTab(sys, false);
  if (id) requestAnimationFrame(() => {
    const sec = document.querySelector(`.prose[data-chapter="${CSS.escape(id)}"]:not([data-lifted])`);
    // the bought Đọc sâu stays folded; the reader opens it from its dropdown
    sec?.scrollIntoView({ block: 'start' });
  });
});
async function generate(ev, saved = null, { fresh = false, lunarIn: keptLunar = null } = {}) {
  ev?.preventDefault();
  const err = $('#form-err'), btn = $('#submit-btn'); err.hidden = true;
  const req = saved ? { ...saved } : readForm(), unknownHour = saved ? false : $('#no-hour').checked, lunarMode = saved ? false : lunarModeOn;
  const d = new Date(req.year, req.month - 1, req.day);
  if ((!lunarMode && d.getMonth() !== req.month - 1) || !req.year || req.year < 1900 || req.year > 2049 || Number.isNaN(req.hour)) {
    err.innerHTML = notice('Ngày giờ sinh chưa hợp lệ', req.year < 1900 || req.year > 2049 ? 'Hệ thống hiện hỗ trợ các năm từ 1900 đến 2049.' : 'Ngày này không tồn tại trong tháng đã chọn. Vui lòng kiểm tra lại.', 'warn'); err.hidden = false; return;
  }
  btn.disabled = true; btn.classList.add('busy'); $('#loading').hidden = false; beginLoad();
  try {
    let lunarIn = keptLunar;
    if (lunarMode) {
      lunarIn = { day: req.day, month: req.month, year: req.year, leap: $('#leap').checked };
      const conv = await post('/api/lunar-to-solar', { ...lunarIn, calendar: req.calendar });
      Object.assign(req, conv.solar);
    }
    if (unknownHour) {
      const sweep = await post('/api/hour-sweep', req);
      state = { req, lunarIn, sweep };
      showHourSweep();
      return;
    }
    await compute(req, lunarIn, fresh);
    // a member's chart from the form goes straight into Lá số của tôi (not the sample, not one reopened from the list)
    if (!saved && !sampling && autoSave(req, isOwnChart(req))) { renderSaved(savedList, openSaved); saver.paint(); }
  } catch (x) {
    // the reader pressed Hủy: back to the form as it was, no error shown
    if (isCancel(x)) { view('home'); $('#lap-la-so')?.scrollIntoView({ block: 'center' }); return; }
    err.innerHTML = notice('Chưa lập được lá số', esc(x.message), 'warn'); err.hidden = false;
    $('#lap-la-so').scrollIntoView({ block: 'center' });
  } finally { endLoad(); btn.disabled = false; btn.classList.remove('busy'); $('#loading').hidden = true; }
}
/** Every engine call for one chart, then the result page. A shared view passes its masked request; util.js post() reroutes the calls. */
async function compute(req, lunarIn = null, fresh = false) {
  // the same chart built earlier on this device (chartcache.js): drawn at once, no engine calls; a shared view is always live
  const key = shareMode.id ? null : cacheKey(req, `${session.user?.email || ''}|${expOn() ? 'x' : ''}`);
  const kept = key && !fresh && await cachedChart(key);
  if (kept) { state = { ...kept, req, lunarIn }; showResults(); return; }
  // /api/synthesis is an optional layer (server flag): a 404 or failure just leaves the chapters without the composed section
  const synthReq = post('/api/synthesis', { ...req, to_year: Math.max(new Date().getFullYear(), req.year) }, { retries: 0 }).catch(() => null);
  // /api/interpret mode "prose" (TS engine on the Worker, or tools/interpret/dev_server.ts locally) is optional too: 404 leaves Bản Mệnh as it was
  const proseReq = post('/api/interpret', { ...req, chapter: 'all', mode: 'prose', to_year: Math.max(new Date().getFullYear(), req.year) }, { retries: 0 })
    .then(r => Object.fromEntries((r.chapters || []).map(x => [x.chapter, x]))).catch(() => null);
  const interpReq = post('/api/interpretation', { ...req, to_year: Math.max(new Date().getFullYear(), req.year) }, { retries: 0 }).catch(() => null);   // optional, same flag
  // "Tổng quan lá số" (/api/overview, TS on the Worker): optional too; without it the result opens on Tử Vi as before
  const overviewReq = post('/api/overview', { ...req, to_year: Math.max(new Date().getFullYear(), req.year) }, { retries: 0 }).catch(() => null);
  const [chart, reason, analysis, formations, , synth, interp, prose, overview] = await Promise.all([post('/api/chart', req), post('/api/reasoning', req), post('/api/analysis', req), expOn() ? post('/api/formations', req).catch(() => null) : null, metaReady, synthReq, interpReq, proseReq, overviewReq]);
  // Only readings checked against the books are shown; draft rules stay in the engine and on the rule-library page.
  Object.values(reason.systems).forEach(sys => { sys.findings = sys.findings.filter(f => f.basis === 'verified'); sys.pending = []; });
  state = { req, chart, reason, analysis, lunarIn, formations, synth, interp, prose, overview };
  if (key) cacheChart(key, { chart, reason, analysis, formations, synth, interp, prose, overview });
  showResults();
}
form.onsubmit = generate;
const savedList = $('#saved-list'), openSaved = r => generate(null, r);
renderSaved(savedList, openSaved);
const compare = initCompare($('#cmp-host'));
initPrint($('#print-btn'), $('#print-full-btn'));
const saver = initSave($('#save-host'), () => state?.req, () => { renderSaved(savedList, openSaved); paintShareBtn(); });
const acctPage = initAccountPage($('#account-view'), {
  placeOptions: form.place.innerHTML, onPrefill: p => prefill(p), compare,
  onRun: p => { prefill(p, true); generate(); }, onOpen: req => generate(null, req), onChange: () => renderSaved(savedList, openSaved),
});
initAccount(() => { renderSaved(savedList, openSaved); acctPage.paint(); }, saver);
initAsk(() => shareMode.id ? null : state?.req);                // "Hỏi Bát Bát": the chart on screen, never a shared one
initPaywall(() => shareMode.id ? null : state?.req);
initAiCards(() => shareMode.id ? null : state?.req);   // "Luận AI" under each chapter, never on a shared chart
initLive($('#live-stats'));
async function loadSample() {
  sampling = true;
  setCal(false); $('#no-hour').checked = false; $('#no-hour').onchange({ target: { checked: false } });
  form.year.value = 1990; form.month.value = 5; form.day.value = 17; form.time.value = '10:30'; form.gender.value = 'male'; form.place.value = 'TP. Hồ Chí Minh'; syncPlace(); hint();
  try { await generate(); } finally { sampling = false; }
}
$('#sample-btn').onclick = loadSample;
$$('[data-sample]').forEach(b => b.onclick = () => loadSample());

function showHourSweep() {
  const { req, lunarIn, sweep } = state;
  $('#res-sub').innerHTML = `<span><b>${fmtDate(req)}</b> · giờ sinh chưa rõ</span><span>${req.gender === 'male' ? 'Nam' : 'Nữ'}</span>${lunarIn ? `<span>Nhập âm lịch ${lunarIn.day}/${lunarIn.month}/${lunarIn.year}${lunarIn.leap ? ' nhuận' : ''}</span>` : ''}`;
  $('#res-hl').innerHTML = '';
  renderHourSweep($('#hour-host'), sweep, h => { $('#no-hour').checked = false; $('#no-hour').onchange({ target: { checked: false } }); form.time.value = h.hour_branch === 'Tý' ? '00:00' : `${String(2 * ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'].indexOf(h.hour_branch)).padStart(2, '0')}:00`; hint(); generate(); });
  document.body.classList.add('hour-mode'); setTab('hour', false); view('chart');
  history.pushState({ v: 'chart' }, '', '#la-so/gio-sinh');
}

function initYearCards() {
  const T = terms(), y0 = state.req.year, now = new Date().getFullYear();
  $$('.bs-year').forEach(host => {
    let y = Math.min(Math.max(now, y0), y0 + 100), seq = 0;
    const sys = host.dataset.sys;
    async function load() {
      const mine = ++seq;
      try {
        const d = await post('/api/year', { ...state.req, to_year: y });
        if (mine !== seq) return;
        host.innerHTML = yearCard(d, T, sys, { atStart: y <= y0, atEnd: y >= y0 + 100 });
        autoLink(host, sys);
        $$('[data-yd]', host).forEach(b => b.onclick = () => { y += +b.dataset.yd; load(); });
      } catch { host.innerHTML = ''; } // the card is a bonus: the rest of the summary stands without it
    }
    load();
  });
}

function showResults() {
  document.body.classList.remove('hour-mode');
  const { req, chart, reason, analysis } = state;
  const ctx = { req, focus: shareMode.id ? [] : focusFor(req), reason, formations: state.formations, synth: state.synth, interp: state.interp, prose: state.prose, highlight: (items, label) => state.tv.highlight(items, label), analysis: analysis.chapters, chartRaw: chart, openPalace: name => { setTab('tuvi', false); setTimeout(() => { $('#tuvi-host').scrollIntoView({ behavior: 'smooth', block: 'start' }); state.tv.select(name); }, 120); } };
  setChart(chart);
  const tv = renderTuvi($('#tuvi-host'), chart.tuvi, ctx);
  state.tv = tv; ctx.tv = tv;
  const bz = renderBazi($('#bazi-host'), chart.bazi, ctx);
  renderBaziReport($('#bazi-report'), chart, ctx, bz.parts);
  renderTuviReport($('#tuvi-report'), chart, ctx);
  const T = terms();
  $('#bazi-summary').innerHTML = summaryBazi(chart, ctx, T); $('#tuvi-summary').innerHTML = summaryTuvi(chart, ctx, T);
  initYearCards();
  if (!shareMode.id) initGrowth($('#growth-host'), $('#tab-growth'), req); // optional layer: the tab stays hidden when the server has it switched off
  // the guides (scripted from the chart's facts, no AI): a conversation at the top of each system, one bubble per chapter, one per palace
  initChat($('#bazi-mascot'), 'bt', dialogueBazi(chart, ctx, T)); initChat($('#tuvi-mascot'), 'tv', dialogueTuvi(chart, ctx, T));
  initChapterBubbles($('#bazi-report'), 'bt'); initChapterBubbles($('#tuvi-report'), 'tv');
  autoLink($('#bazi-host'), 'bt'); autoLink($('#bazi-summary'), 'bt'); autoLink($('#tuvi-host'), 'tv'); autoLink($('#tuvi-summary'), 'tv');
  const t = chart.tuvi, b = chart.bazi;
  const lu = state.lunarIn ? `<span>Nhập âm lịch ${state.lunarIn.day}/${state.lunarIn.month}/${state.lunarIn.year}${state.lunarIn.leap ? ' nhuận' : ''}</span>` : '';
  const has = req.day != null;   // false on a share link with the birth hidden: the page never received the day, month or hour
  $('#res-sub').innerHTML = (has && lu ? bd(lu) : '') + `<span><b>${bd(`${String(req.day).padStart(2, '0')}/${String(req.month).padStart(2, '0')}/`, has, DM)}${req.year}</b>${bd(` · ${String(req.hour).padStart(2, '0')}:${String(req.minute).padStart(2, '0')} · giờ ${esc(hourBranch(req.hour))}`, has, ' · giờ sinh ẩn')}</span><span>${req.gender === 'male' ? 'Nam' : 'Nữ'}</span><span>Âm lịch ${bd(`${t.lunar.day}/${t.lunar.month}/`, t.lunar.day != null, DM)}${t.lunar.year}${t.lunar.leap ? ' nhuận' : ''}</span><span>Năm ${esc(t.year_gz)}</span>`;
  $('#res-hl').innerHTML = `<button type="button" class="hl-chip gl" data-gl="c:nhat-chu">${esc(STEMS[b.pillars.day.stem].n)} ${STEMS[b.pillars.day.stem].e} <small>Nhật Chủ</small></button><button type="button" class="hl-chip gl" data-gl="c:cuc">${esc(t.cuc.name)}</button><button type="button" class="hl-chip gl" data-gl="c:nap-am">Mệnh ${esc(t.menh_nap_am)}</button>` + (has ? hoangdaoChip(chart.western) : '');
  // cung hoàng đạo card at the top of the Tử Vi pane; a share link with the birth day hidden never shows it (the Worker also drops the block)
  renderHoangDao($('#hoangdao-host'), has ? chart.western : null);
  saver.paint(); paintShareBtn();
  if (!shareMode.id) rememberCurrent(req, state.lunarIn);     // a reload of #la-so/... comes back to this chart
  // the overview tab opens first when the server sent it; its chapter buttons open the matching Tử Vi chapter
  const ov = !!state.overview?.indices;
  $('#tab-overview').hidden = !ov;
  if (ov) renderOverview($('#overview-host'), state.overview, { prose: state.prose, onChapter: id => { setTab('tuvi', false); history.replaceState({ v: 'chart' }, '', '#la-so/tu-vi'); setTimeout(() => $('#tv-' + id)?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' }), 60); } });
  else $('#overview-host').innerHTML = '';
  setTab(ov ? 'overview' : 'tuvi', false); view('chart');
  if (!shareMode.id) history.pushState({ v: 'chart' }, '', ov ? '#la-so/tong-quan' : '#la-so/tu-vi');
}

// ---------- share link, PNG, "Ẩn thông tin sinh" on exports ----------
function paintShareBtn() { $('#share-btn').hidden = !session.user || !!shareMode.id || !state?.req; }
addEventListener('tvbt:account', paintShareBtn);
$('#share-btn').onclick = () => {
  const item = state?.req && isSaved(state.req);
  if (item) { openShareDialog(item, () => renderSaved(savedList, openSaved)); return; }
  resMsg('Lưu lá số này trước, rồi chia sẻ.'); $('#save-host button')?.click();
};
const resMsg = t => { const m = $('#res-msg'); m.textContent = t; m.hidden = !t; };
$('#hide-birth').onchange = e => document.body.classList.toggle('hide-birth', e.target.checked);
$('#png-btn').onclick = async e => {
  const b = e.currentTarget; b.disabled = true; resMsg('Đang dựng ảnh…');
  try { await exportBoardPng(); resMsg(''); } catch (x) { resMsg(x.message); } finally { b.disabled = false; }
};
function leaveShare(hash) { location.replace('/' + hash); location.reload(); }
document.addEventListener('click', e => { if (shareMode.id && e.target.closest('[data-leave-share]')) { e.preventDefault(); leaveShare('#lap-la-so'); } });
async function openShare(id) {
  $('#loading').hidden = false; beginLoad();
  try {
    const s = await loadShare(id);
    if (!s) { $('#form-err').innerHTML = notice('Không mở được lá số được chia sẻ', 'Liên kết không tồn tại hoặc đã bị chủ lá số thu hồi.', 'warn'); $('#form-err').hidden = false; history.replaceState(null, '', '#lap-la-so'); go('lap-la-so'); return; }
    document.body.classList.add('shared');
    if (s.hide) document.body.classList.add('hide-birth');
    $('#share-banner').innerHTML = shareBanner(s); $('#share-banner').hidden = false;
    $('#atl-h').innerHTML = s.label ? `Lá số của <span class="res-name">${esc(s.label)}</span>` : 'Lá số được chia sẻ';
    $('.atl-id .eyebrow').textContent = 'Lá số được chia sẻ · chỉ xem';
    let dg = null; try { dg = localStorage.getItem('tvbt.dignity'); } catch { /* storage unavailable */ }
    await compute(dg === 'khao_luan' || dg === 'toan_thu' ? { ...s.req, dignity_school: dg } : s.req);
  } catch (x) {
    if (!isCancel(x)) { $('#form-err').innerHTML = notice('Chưa mở được lá số được chia sẻ', esc(x.message), 'warn'); $('#form-err').hidden = false; }
    view('home');
  } finally { endLoad(); $('#loading').hidden = true; }
}
// a pasted share link or the account page, on load and when only the hash changes (same document)
const route = () => { const m = location.hash.match(SHARE_HASH); if (m) { if (shareMode.id && shareMode.id !== m[1]) location.reload(); else if (!shareMode.id) openShare(m[1]); } else if (location.hash === '#tai-khoan') go('tai-khoan'); else if (location.hash === '#trang-chu') go('trang-chu'); else if (location.hash === '#la-so-mau') { history.replaceState(null, '', location.pathname); loadSample().then(() => setTab('tuvi')); } };
route(); addEventListener('hashchange', route);
// back from "Đăng nhập để đọc tiếp" on a guest lock card (js/paywall.js): the chart that was on screen, now read at the member tier
{ const resume = takeResume(); if (resume && !SHARE_HASH.test(location.hash)) generate(null, resume); else restoreCurrent(); }
// a reload on #la-so/<tab>: the chart that was on screen in this tab, on the same tab (from the device copy when there is one)
async function restoreCurrent() {
  const m = location.hash.match(/^#la-so\/(tong-quan|tu-vi|bat-tu|truong-thanh)$/), cur = m && currentChart();
  if (!cur?.req) return;
  // the account decides what the server sends, so wait (briefly) for it before looking up the kept copy
  if (!session.ready) await new Promise(r => { addEventListener('tvbt:account', r, { once: true }); setTimeout(r, 3000); });
  await generate(null, cur.req, { lunarIn: cur.lunarIn });
  if (state?.chart) go(m[1]);
}
function again() { forgetCurrent(); view('home'); history.replaceState(null, '', '#lap-la-so'); requestAnimationFrame(() => $('#lap-la-so').scrollIntoView({ behavior: 'smooth', block: 'start' })); }
$('#again').onclick = again;
// the header's "Tải PDF" appears once the result masthead (with its own buttons) has scrolled away
if ('IntersectionObserver' in window) new IntersectionObserver(([e]) => document.body.classList.toggle('mast-off', !e.isIntersecting)).observe($('.res-act'));

// reveal on scroll
if (!reduce && 'IntersectionObserver' in window) {
  const rv = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); rv.unobserve(e.target); } }), { threshold: .12 });
  $$('.reveal').forEach(el => rv.observe(el));
} else $$('.reveal').forEach(el => el.classList.add('in'));
// Hủy on the loading screen: abort the chart being built (util.js cancelLoad); Esc does the same while the screen is up
$('#load-cancel')?.addEventListener('click', cancelLoad);
document.addEventListener('keydown', e => { if (e.key === 'Escape' && !$('#loading').hidden) cancelLoad(); });
