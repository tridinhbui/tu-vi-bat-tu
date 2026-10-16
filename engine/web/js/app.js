// App shell: navigation, home interactions, BirthChartForm, results orchestration.
import { $, $$, esc, post, hourBranch, STEMS, BRANCHES, loadMeta } from './util.js';
import { compass, brandMark } from './compass.js';
import { fiveElements } from './elements.js';
import { renderBazi } from './bazi.js';
import { renderTuvi } from './tuvi.js';
import { renderBaziReport, renderTuviReport } from './report.js';
import { notice } from './ui.js';

const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const metaReady = loadMeta();
let state = null; // { req, chart, reason, tv }

// ---------- brand + hero art ----------
$$('[data-brand]').forEach(e => e.innerHTML = brandMark(e.dataset.brand === 'lg' ? 44 : 32));
$('#hero-compass').innerHTML = compass({ animate: !reduce });
$('#load-compass').innerHTML = compass({ animate: false, detail: 'min' });
$('#foot-compass').innerHTML = compass({ animate: false, detail: 'min' });

// ---------- navigation ----------
const view = v => { document.body.dataset.view = v; scrollTo({ top: 0 }); };
function setTab(tab, scroll = true) {
  $('#chart-view').dataset.tab = tab;
  $$('.res-tabs button').forEach(b => { const on = b.id === 'tab-' + tab; b.setAttribute('aria-selected', on); b.tabIndex = on ? 0 : -1; });
  if (scroll) scrollTo({ top: 0 });
}
function go(id) {
  const tabs = { 'bat-tu': 'bazi', 'tu-vi': 'tuvi' };
  if (tabs[id] && state) { if (document.body.dataset.view !== 'chart') view('chart'); setTab(tabs[id]); history.replaceState({ v: 'chart' }, '', '#la-so/' + id); closeMenu(); return; }
  const target = { 'bat-tu': 'hai-he-thong', 'tu-vi': 'hai-he-thong' }[id] || id;
  if (document.body.dataset.view !== 'home') view('home');
  requestAnimationFrame(() => $('#' + target)?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' }));
  history.replaceState(null, '', '#' + id);
  closeMenu();
}
document.addEventListener('click', e => {
  const a = e.target.closest('[data-go]'); if (!a) return;
  e.preventDefault(); go(a.dataset.go);
});
const menuBtn = $('#menu-btn');
const closeMenu = () => { document.body.classList.remove('menu-open'); menuBtn.setAttribute('aria-expanded', 'false'); };
menuBtn.onclick = () => { const o = document.body.classList.toggle('menu-open'); menuBtn.setAttribute('aria-expanded', o); };
$('#nav-scrim').onclick = closeMenu;
addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });
addEventListener('popstate', () => { if (document.body.dataset.view === 'chart') view('home'); });
let lastY = 0;
addEventListener('scroll', () => { const y = scrollY; $('#site-header').classList.toggle('stuck', y > 8); lastY = y; }, { passive: true });

// ---------- home: Five Elements, library, form ----------
fiveElements($('#home-fe'), { onSelect: () => {} });

const LIB = {
  'can-chi': ['Can Chi', 'Mười Thiên can (Giáp, Ất, Bính, Đinh, Mậu, Kỷ, Canh, Tân, Nhâm, Quý) ghép với mười hai Địa chi (Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi) tạo thành chu kỳ sáu mươi năm, gọi là Lục thập hoa giáp. Can mang tính dương hoặc âm xen kẽ và thuộc một trong năm hành; Chi cũng vậy, kèm theo gắn với tháng và giờ trong ngày.'],
  'ngu-hanh': ['Ngũ Hành', 'Mộc, Hỏa, Thổ, Kim, Thủy là năm phạm trù biểu tượng dùng để mô tả sự vận động và quan hệ giữa các yếu tố. Tương sinh: Mộc sinh Hỏa, Hỏa sinh Thổ, Thổ sinh Kim, Kim sinh Thủy, Thủy sinh Mộc. Tương khắc: Mộc khắc Thổ, Thổ khắc Thủy, Thủy khắc Hỏa, Hỏa khắc Kim, Kim khắc Mộc. Sinh hay khắc chỉ là quan hệ nền; lợi hay hại còn tùy thế của toàn cục.'],
  'tam-phuong': ['Tam phương tứ chính', 'Khi xem một cung trên lá số Tử Vi, người ta không chỉ nhìn riêng cung đó mà còn xét cung đối diện (xung chiếu) cùng hai cung tam hợp ở các vị trí cách nhau bốn cung. Bốn cung này hợp thành “tứ chính”, và cùng với cung gốc tạo nên “tam phương tứ chính”. Trên lá số của site, chọn một cung sẽ vẽ các đường nối này.'],
  'tuan-triet': ['Tuần và Triệt', 'Tuần (Tuần không) và Triệt (Triệt lộ không vong) là hai dấu hiệu đặc biệt đặt lên một cặp cung. Trong truyền thống, chúng được xem như yếu tố làm giảm hoặc thay đổi tác động của sao ở cung bị che. Cách tính và cách luận khác nhau giữa các trường phái, vì vậy site hiển thị chúng như dữ kiện vị trí.'],
  'gio-ty': ['Giờ Tý và ngày mới', 'Giờ Tý kéo dài từ 23h đến 1h sáng hôm sau. Có hai quy ước: tính từ 23h là đã sang ngày mới (“Tý sớm”), hoặc chỉ sang ngày mới sau 24h (“Tý muộn”). Hai quy ước này có thể cho ra trụ Ngày và Giờ khác nhau, nên được đặt trong phần cài đặt nâng cao.'],
  'tiet-khi': ['Tiết khí và tháng Bát Tự', 'Bát Tự lấy tháng theo 12 “tiết” trong 24 tiết khí, tức theo vị trí của Mặt Trời trên hoàng đạo, chứ không theo mùng một âm lịch. Vì vậy một người sinh vào đầu tháng âm lịch vẫn có thể thuộc tháng Bát Tự của tháng trước, nếu tiết chưa đổi.'],
};
const dlg = $('#lib-dlg');
$$('[data-lib]').forEach(b => b.onclick = () => { const [t, body] = LIB[b.dataset.lib]; $('#lib-t').textContent = t; $('#lib-b').textContent = body; dlg.showModal(); });
dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });

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
  if (!other) { form.tz.value = 'Asia/Ho_Chi_Minh'; form.longitude.value = PLACES[form.place.value]; }
};
form.place.onchange = syncPlace; syncPlace();
const hint = () => { const [h] = (form.time.value || '00:00').split(':').map(Number); $('#hour-hint').textContent = `Giờ ${hourBranch(h)}`; };
form.time.oninput = hint; hint();
$('#solar').onchange = e => { $('#lon-wrap').hidden = !e.target.checked; };

function readForm() {
  const [h, m] = form.time.value.split(':').map(Number);
  const o = { year: +form.year.value, month: +form.month.value, day: +form.day.value, hour: h, minute: m, gender: form.gender.value, tz: form.tz.value.trim() || 'Asia/Ho_Chi_Minh', calendar: form.calsys.value, zi_rule: form.zi_rule.value, level: +form.level.value };
  if ($('#solar').checked) { o.use_true_solar_time = true; o.longitude = +form.longitude.value; }
  return o;
}
const fmtDate = r => `${String(r.day).padStart(2, '0')}/${String(r.month).padStart(2, '0')}/${r.year}`;

async function generate(ev) {
  ev?.preventDefault();
  const err = $('#form-err'), btn = $('#submit-btn'); err.hidden = true;
  const req = readForm();
  const d = new Date(req.year, req.month - 1, req.day);
  if (d.getMonth() !== req.month - 1 || !req.year || req.year < 1900 || req.year > 2049 || Number.isNaN(req.hour)) {
    err.innerHTML = notice('Ngày giờ sinh chưa hợp lệ', req.year < 1900 || req.year > 2049 ? 'Hệ thống hiện hỗ trợ các năm từ 1900 đến 2049.' : 'Ngày này không tồn tại trong tháng đã chọn. Vui lòng kiểm tra lại.', 'warn'); err.hidden = false; return;
  }
  btn.disabled = true; btn.classList.add('busy'); $('#loading').hidden = false;
  try {
    const [chart, reason, analysis] = await Promise.all([post('/api/chart', req), post('/api/reasoning', req), post('/api/analysis', req), metaReady]);
    state = { req, chart, reason, analysis };
    showResults();
  } catch (x) {
    err.innerHTML = notice('Chưa lập được lá số', esc(x.message), 'warn'); err.hidden = false;
    $('#lap-la-so').scrollIntoView({ block: 'center' });
  } finally { btn.disabled = false; btn.classList.remove('busy'); $('#loading').hidden = true; }
}
form.onsubmit = generate;
$('#sample-btn').onclick = () => generate();

function showResults() {
  const { req, chart, reason, analysis } = state;
  const ctx = { req, reason, analysis: analysis.chapters, chartRaw: chart, openPalace: name => { setTab('tuvi', false); setTimeout(() => { $('#tuvi-host').scrollIntoView({ behavior: 'smooth', block: 'start' }); state.tv.select(name); }, 120); } };
  const tv = renderTuvi($('#tuvi-host'), chart.tuvi, ctx);
  state.tv = tv; ctx.tv = tv;
  const bz = renderBazi($('#bazi-host'), chart.bazi, ctx);
  renderBaziReport($('#bazi-report'), chart, ctx, bz.parts);
  renderTuviReport($('#tuvi-report'), chart, ctx);
  const t = chart.tuvi, b = chart.bazi;
  $('#res-sub').innerHTML = `<span><b>${fmtDate(req)}</b> · ${String(req.hour).padStart(2, '0')}:${String(req.minute).padStart(2, '0')} · giờ ${esc(hourBranch(req.hour))}</span><span>${req.gender === 'male' ? 'Nam' : 'Nữ'}</span><span>Âm lịch ${t.lunar.day}/${t.lunar.month}/${t.lunar.year}${t.lunar.leap ? ' nhuận' : ''}</span><span>Năm ${esc(t.year_gz)}</span>`;
  $('#res-hl').innerHTML = `<span>${esc(STEMS[b.pillars.day.stem].n)} ${STEMS[b.pillars.day.stem].e} <small>Nhật Chủ</small></span><span>${esc(t.cuc.name)}</span><span>Mệnh ${esc(t.menh_nap_am)}</span>`;
  setTab('bazi', false); view('chart');
  history.pushState({ v: 'chart' }, '', '#la-so/bat-tu');
}
$('#again').onclick = () => { view('home'); requestAnimationFrame(() => $('#lap-la-so').scrollIntoView({ behavior: 'smooth', block: 'start' })); };

// reveal on scroll
if (!reduce && 'IntersectionObserver' in window) {
  const rv = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); rv.unobserve(e.target); } }), { threshold: .12 });
  $$('.reveal').forEach(el => rv.observe(el));
} else $$('.reveal').forEach(el => el.classList.add('in'));
