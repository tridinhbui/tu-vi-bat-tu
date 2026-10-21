// Tử Vi "Twelve Palaces": the real 12-palace plate, Tam Phương Tứ Chính on select/hover, one contextual panel, đại hạn → năm timeline.
// Presentation only: every value is read from the chart / year responses; no calculation lives here.
import { $, $$, esc, bd, starKind, BRANCHES, STEMS, palaceOfSubject } from './util.js';
import { compass } from './compass.js';
import { findingList, timeline } from './ui.js';
import { scopeText, scopePanelTuvi } from './scope.js';
import { terms, autoLink } from './glossary.js';
import { easyReadings, emptyReading } from './beginner.js';
import { palaceBubble } from './mascots.js';
import { tier, evLegend, yearData, centerIn } from './atlas.js';
import { HANH, MAJOR_SIGN, BOLD, TRANG_SINH, BRANCH_HANH, YANG_BRANCH, hk } from './stars_hanh.js';

// Traditional layout: branch index per grid cell (null = centre block). Tỵ top-left, clockwise.
const CELLS = [5, 6, 7, 8, 4, null, null, 9, 3, null, null, 10, 2, 1, 0, 11];
// Tứ Hóa seals: Han mark + css key (vocabulary only)
const HOA = { 'Hóa Lộc': { k: 'loc', h: '祿', gl: 'c:hoa-loc', s: 'Lộc' }, 'Hóa Quyền': { k: 'quyen', h: '權', gl: 'c:hoa-quyen', s: 'Quyền' }, 'Hóa Khoa': { k: 'khoa', h: '科', gl: 'c:hoa-khoa', s: 'Khoa' }, 'Hóa Kỵ': { k: 'ky', h: '忌', gl: 'c:hoa-ky', s: 'Kỵ' } };
const DG = { 'miếu': 'Miếu', 'vượng': 'Vượng', 'đắc': 'Đắc', 'bình': 'Bình', 'hãm': 'Hãm', 'lợi': 'Lợi', 'đắc cách': 'Đắc' };
// book a brightness came from (dignity_status.school), for the badge tooltip
const DG_BOOK = { thuc_hanh: 'Thực Hành', toan_thu: 'Toàn Thư', khao_luan: 'Khảo Luận' };

export function renderTuvi(host, t, ctx) {
  const by = Object.fromEntries(t.palaces.map(p => [p.branch_index, p]));
  const byBranch = Object.fromEntries(t.palaces.map(p => [p.branch, p]));
  const byName = Object.fromEntries(t.palaces.map(p => [p.name, p]));
  const dhByBranch = Object.fromEntries(t.dai_han.map(d => [d.branch, d]));
  const th = {}; Object.entries(t.tu_hoa).forEach(([k, v]) => { th[v.star] = k; });
  const unv = new Set(t.stars.filter(x => /chưa đối chiếu/.test(x.group)).map(x => x.name));
  const than = t.palaces.find(p => p.is_than), menh = t.palaces.find(p => p.name === 'Mệnh');
  const findings = (ctx.reason?.systems?.tu_vi?.findings || []);
  const fOf = name => findings.filter(f => palaceOfSubject(f.subject) === name);
  const now = new Date().getFullYear(), age = now - ctx.req.year + 1;

  // Badge from the shared dignity knowledge base (palace.dignity_status, engine/data/dignity_kb.json): VERIFIED prints the book's own
  // term (Lợi, Đắc…); CONFLICT prints a muted '?' listing the readings; UNVERIFIED / NOT_APPLICABLE print nothing (never a guess).
  const page = loc => loc.replace(/^[A-Z]+ /, '').replace(/^pp?\./, 'tr.');
  const others = ds => (ds?.variants || []).map(v => `${DG_BOOK[v.school] || v.school}${v.reported ? ' (dẫn lại)' : ''}: ${v.term}`).join('; ');
  const badge = (ds, major) => {
    if (ds?.status === 'VERIFIED') {
      const dg = ds.value, term = ds.term || dg, o = others(ds);
      const tip = `Độ sáng: ${term}${term !== dg ? ` (xếp như ${dg})` : ''} · ${DG_BOOK[ds.school] || ds.school} ${page(ds.locator)}${ds.legacy ? ' · sách in “Lợi”, đọc như Đắc (đã xác nhận 19/10/2026)' : ''}${o ? ` · Sách khác: ${o}` : ''}`;
      return `<sup class="dg dg-${dg}${major ? '' : ' dg-aux'}" data-gl="dg:${esc(dg)}" title="${esc(tip)}">${DG[term] || DG[dg] || esc(term)}</sup>`;
    }
    if (ds?.status === 'CONFLICT') {
      const tip = `Sách ghi khác nhau, chưa xếp độ sáng: ${ds.alternatives.map(a => `${a.term} (${page(a.locator)})`).join(' / ')}`;
      return `<sup class="dg dg-conflict${major ? '' : ' dg-aux'}" data-gl="dg:conflict" title="${esc(tip)}">?</sup>`;
    }
    return '';
  };
  const starHtml = (s, major, ds, inCell = false) => {
    const k = starKind(s), h = th[s], hs = h && HOA[h], lbl = ds?.status === 'VERIFIED' ? `, ${ds.term || ds.value}` : ds?.status === 'CONFLICT' ? ', độ sáng chưa thống nhất' : '';
    return `<span class="st gl-s st-${k}${major ? ' major' : ''}${unv.has(s) ? ' unv' : ''}" role="button"${inCell ? '' : ' tabindex="0"'} data-gl="star:${esc(s)}" aria-label="${esc(s)}${esc(lbl)}: xem giải thích">${esc(s)}${badge(ds, major)}${hs ? `<span class="th th-${hs.k}" data-gl="${hs.gl}" title="${esc(h)}"><i lang="zh">${hs.h}</i></span>` : ''}</span>`;
  };

  // Traditional board cell (the Vietnamese lá số convention): can-chi and the palace's hành on the left, the palace name coloured by the hành of
  // its branch, the đại hạn age on the right; chính tinh in capitals with their dignity letter; phụ tinh in two columns (good left, bad right),
  // each coloured by its own hành (stars_hanh.js, display only); the foot carries ĐV.<role> / Tràng Sinh stage / LN.<role>.
  const LETTER = { 'miếu': 'M', 'vượng': 'V', 'đắc': 'Đ', 'bình': 'B', 'hãm': 'H', 'lợi': 'L' };
  const ROLE = ['MỆNH', 'PHỤ', 'PHÚC', 'ĐIỀN', 'QUAN', 'NÔ', 'DI', 'TẬT', 'TÀI', 'TỬ', 'PHỐI', 'HUYNH'];
  const dhNow = t.dai_han.find(d => age >= d.age_from && age <= d.age_to), dvRef = dhNow && byBranch[dhNow.branch];
  const lnRef = by[((now - 4) % 12 + 12) % 12];
  const roleOf = (p, ref) => ref ? ROLE[(p.branch_index - ref.branch_index + 12) % 12] : '';
  const dgLetter = ds => ds?.status === 'VERIFIED' ? LETTER[ds.value] : ds?.status === 'CONFLICT' ? '?' : '';
  const hoaOf = i => Object.entries(t.tu_hoa).filter(([, v]) => v.branch === i).map(([h]) => h);
  const tStar = (s, ds, major = false) => {
    const L = dgLetter(ds), h = HANH[s], tip = ds?.status === 'VERIFIED' ? `, ${ds.term || ds.value}` : '';
    const txt = major ? `${MAJOR_SIGN[s] || ''}${s.toLocaleUpperCase('vi')}` : s;
    return `<span class="st gl-s tb-s h-${hk(h)}${major ? ' tb-maj' : ''}${BOLD.has(s) ? ' tb-b' : ''}${unv.has(s) ? ' unv' : ''}" role="button" data-gl="star:${esc(s)}" aria-label="${esc(s)}${esc(tip)}">${esc(txt)}${L ? ` (${L})` : ''}</span>`;
  };
  const cell = i => {
    const p = by[i], d = dhByBranch[p.branch], isMenh = p.name === 'Mệnh', ph = BRANCH_HANH[p.branch];
    const stage = p.stars.find(s => TRANG_SINH.includes(s));
    const minors = p.stars.filter(s => !p.major_stars.includes(s) && !TRANG_SINH.includes(s));
    const hoas = hoaOf(i).map(h => ({ s: h, bad: h === 'Hóa Kỵ' }));
    const left = [...minors.filter(s => starKind(s) !== 'neg').map(s => tStar(s, p.dignity_status?.[s])), ...hoas.filter(x => !x.bad).map(x => tStar(x.s))];
    const right = [...minors.filter(s => starKind(s) === 'neg').map(s => tStar(s, p.dignity_status?.[s])), ...hoas.filter(x => x.bad).map(x => tStar(x.s))];
    const nm = `${p.name.toLocaleUpperCase('vi')}${p.is_than ? '<span class="tb-than">&lt;THÂN&gt;</span>' : ''}`;
    return `<button type="button" class="pal tb-pal${isMenh ? ' is-menh' : ''}${p.is_than ? ' is-than' : ''}" data-i="${i}" aria-pressed="false" aria-label="Cung ${esc(p.name)}, ${esc(p.stem)} ${esc(p.branch)}. Chính tinh: ${esc(p.major_stars.join(', ') || 'vô chính diệu')}">
      <span class="tb-h"><span class="tb-gz">${esc(p.stem[0])}.${esc(p.branch)}</span><span class="tb-name h-${hk(ph)}">${nm}</span><span class="tb-dh">${d ? d.age_from : ''}</span></span>
      <span class="tb-h2"><span class="tb-el">${YANG_BRANCH.has(p.branch) ? '+' : '−'}${esc(ph)}</span><span class="tb-majs">${p.major_stars.length ? p.major_stars.map(s => tStar(s, p.dignity_status?.[s], true)).join('') : '<span class="tb-vcd">vô chính diệu</span>'}</span><span class="tb-th"></span></span>
      <span class="tb-cols"><span class="tb-col">${left.join('')}</span><span class="tb-col">${right.join('')}</span></span>
      <span class="tb-foot"><span>${dvRef ? 'ĐV.' + roleOf(p, dvRef) : ''}</span><span class="tb-ts">${esc(stage || '')}</span><span>${lnRef ? 'LN.' + roleOf(p, lnRef) : ''}</span></span>
      <span class="pal-cy"></span>
    </button>`;
  };

  // centre of the board: the birth data as the traditional board lists it (no branding), the Mệnh–Cục relation, chủ mệnh / chủ thân
  const P = ctx.chartRaw?.bazi?.pillars || {}, gz = k => P[k]?.name || '';
  const yNow = `${STEMS[((now - 4) % 10 + 10) % 10].n} ${BRANCHES[((now - 4) % 12 + 12) % 12].n}`;
  const pad2 = n => String(n).padStart(2, '0');
  const row = (k, v, g = '') => `<div class="tb-r"><dt>${k}</dt><dd>${v}</dd><dd class="tb-g">${g}</dd></div>`;
  const center = `<div class="ident tb-centre" aria-labelledby="id-t">
      <h3 id="id-t" class="tb-title">Lá Số Tử Vi</h3>
      <dl class="tb-info">
        ${row('Năm:', `${ctx.req.year}`, esc(t.year_gz))}
        ${row('Tháng:', bd(`${ctx.req.month} (${t.lunar.month}${t.lunar.leap ? ' nhuận' : ''})`, ctx.req.month != null), esc(gz('month')))}
        ${row('Ngày:', bd(`${ctx.req.day} (${t.lunar.day})`, ctx.req.day != null), esc(gz('day')))}
        ${row('Giờ:', bd(`${ctx.req.hour} giờ ${pad2(ctx.req.minute || 0)} phút`, ctx.req.hour != null), esc(gz('hour')))}
        ${row('Năm xem:', `${yNow} (${now}), ${age} tuổi`)}
        ${row('Âm dương:', esc(t.yin_yang_gender))}
        ${row('Bản mệnh:', `${esc(t.menh_nap_am)} - ${esc(t.cuc.name)}`)}
        ${row('', `(${esc(t.menh_cuc_relation)})`)}
        ${t.extras?.menh_chu ? row('Chủ mệnh:', esc(t.extras.menh_chu.star)) + row('Chủ thân:', esc(t.extras.than_chu.star)) : ''}
        ${row('Thân cư:', esc(than.name))}
      </dl>
      <button type="button" class="link tb-scope" data-scope>Phạm vi tính toán</button>
    </div>`;

  const ovOrder = t.palaces.slice().sort((a, b) => (a.branch_index - menh.branch_index + 12) % 12 - (b.branch_index - menh.branch_index + 12) % 12);
  const yearsOf = d => Array.from({ length: d.age_to - d.age_from + 1 }, (_, k) => ctx.req.year + d.age_from - 1 + k);
  const curDh = t.dai_han.findIndex(d => age >= d.age_from && age <= d.age_to);
  const needle = (() => { if (curDh < 0) return ''; const d = t.dai_han[curDh], f = (age - d.age_from) / (d.age_to - d.age_from + 1); return `<span class="tm-needle" style="left:${((curDh + f) / t.dai_han.length * 100).toFixed(2)}%" title="Hôm nay"><i>Nay ${now}</i></span>`; })();

  host.innerHTML = `
    <div class="tv-stage" data-view="ov">
      <div class="tv-plate tv-main" id="tv-plate">
        <header class="plate-h"><h3 id="tv-h2"><i lang="zh">紫微</i>Mười hai cung</h3><span class="plate-k">Chạm một cung để mở · Tam Phương Tứ Chính sẽ sáng lên</span></header>
        <div class="seg tv-toggle" role="group" aria-label="Chế độ xem lá số"><button type="button" data-v="ov" aria-pressed="true">Sổ tay</button><button type="button" data-v="full" aria-pressed="false">Toàn lá số</button></div>
        <ol class="tv-ov" aria-label="Tổng quan mười hai cung, bắt đầu từ cung Mệnh">${ovOrder.map(p => `<li><button type="button" data-i="${p.branch_index}"><span class="ov-n">${esc(p.name)}${p.is_than ? ' <em>Thân</em>' : ''}</span><span class="ov-gz">${esc(p.stem)} ${esc(p.branch)}</span><span class="ov-s">${esc(p.major_stars.join(' · ') || 'vô chính diệu')}</span></button></li>`).join('')}</ol>
        <div class="tv-zoom" role="group" aria-label="Thu phóng lá số"><button type="button" data-z="out" aria-label="Thu nhỏ">−</button><span class="tv-zl" aria-live="polite">100%</span><button type="button" data-z="in" aria-label="Phóng to">+</button><button type="button" data-z="fit">Vừa khung</button><button type="button" data-z="one">100%</button><span class="tv-zh">Kéo để di chuyển · Ctrl + cuộn để thu phóng</span><label class="tv-dg">Bảng độ sáng <select data-dg><option value="khao_luan">Khảo Luận (mặc định, bảng phổ thông)</option><option value="thuc_hanh">Thực Hành</option><option value="toan_thu">Toàn Thư</option></select></label></div><div class="tv-scroll" tabindex="0" role="region" aria-label="Lá số Tử Vi: kéo để di chuyển, Ctrl + cuộn hoặc chụm hai ngón để thu phóng"><div class="tv-board" id="tv-board">
          <svg class="tv-links" aria-hidden="true"></svg>
          <div id="grid">${CELLS.map((i, k) => i === null ? (k === 5 ? `<div class="center">${center}</div>` : '') : cell(i)).join('')}</div><div class="tb-tt" aria-hidden="true"></div><div class="tb-legend"><span><b class="h-kim">M</b>:Miếu</span><span><b class="h-kim">V</b>:Vượng</span><span><b class="h-kim">Đ</b>:Đắc</span><span><b class="h-kim">B</b>:Bình hòa</span><span><b class="h-kim">H</b>:Hãm</span><span class="tb-lg-gap"></span><span><i class="sw h-kim"></i>Kim</span><span><i class="sw h-moc"></i>Mộc</span><span><i class="sw h-thuy"></i>Thủy</span><span><i class="sw h-hoa"></i>Hỏa</span><span><i class="sw h-tho"></i>Thổ</span></div></div></div>
        <div class="legend" aria-label="Cách đọc bảng">
          <span><i class="lg-seal lg-m" lang="zh">命</i>Cung Mệnh</span><span><i class="lg-seal lg-t" lang="zh">身</i>Thân cư</span>
          <span><i class="lg-maj">Aa</i>Chính tinh</span><span class="l-pos">Cát tinh</span><span class="l-neg">Sát / hung tinh</span><span class="l-neu">Phụ tinh</span>
          <span data-gl="c:tu-hoa" role="button" tabindex="0"><span class="th th-loc"><i lang="zh">祿</i></span><span class="th th-quyen"><i lang="zh">權</i></span><span class="th th-khoa"><i lang="zh">科</i></span><span class="th th-ky"><i lang="zh">忌</i></span>Tứ Hóa</span>
          <span data-gl="c:do-sang" role="button" tabindex="0"><sup class="dg dg-vượng">Vượng</sup>Độ sáng</span><span data-gl="c:dai-han" role="button" tabindex="0"><b class="legend-dh">6–15</b>Đại hạn</span>
        </div>
        <p class="muted small tv-hint">Khi một cung đang mở, chạm vào tên sao hoặc nhãn (Miếu, Hãm, Lộc…) để biết nó là gì.<span class="pro-only"> Bộ quy tắc Tử Vi đang dùng: bản Việt Nam.</span></p>
        ${scopePanelTuvi(t)}
      </div>
      <aside class="tv-panel drawer" id="tv-drawer" aria-label="Chi tiết cung" aria-live="polite"></aside>
      <section class="tv-time" aria-labelledby="tv-tm-t">
        <header class="plate-h"><h3 id="tv-tm-t"><i lang="zh">大限</i>Đại hạn</h3><span class="plate-k">Đại hạn chạy ${esc(t.dai_han_direction)} · chọn một chặng để đánh dấu cung · rồi chọn một năm</span></header>
        <div class="tm-scroll" id="tv-tm-scroll"><ol class="tm-track" id="tv-tm-track" style="--n:${t.dai_han.length}">${t.dai_han.map((d, i) => { const ys = yearsOf(d);
          return `<li><button type="button" class="tm-tab${i === curDh ? ' now' : ''}" data-i="${i}" aria-pressed="false"${i === curDh ? ' aria-current="true"' : ''}><span class="tm-age">${d.age_from}–${d.age_to} tuổi</span><span class="tm-pal">${esc(d.palace)}</span><span class="tm-vn">${esc(d.stem)} ${esc(d.branch)}</span><span class="tm-yr">${ys[0]}–${ys[ys.length - 1]}</span>${i === curDh ? '<span class="tm-now">Hiện tại</span>' : ''}</button></li>`; }).join('')}${needle}</ol></div>
        <div class="tm-years" id="tv-years"></div>
        <div class="tv-cy" id="tv-cy" aria-live="polite"></div>
      </section>
    </div>
    <dialog id="scope-dlg" class="dlg"><form method="dialog"><h3>Phạm vi tính toán hiện tại</h3><p class="muted">Những phần dưới đây chưa được tính hoặc chưa hiển thị để bảo đảm lá số không chứa dữ kiện thiếu căn cứ.</p><ul>${t.unsupported.map(u => `<li>${esc(scopeText(u))}</li>`).join('')}</ul>${t.warnings.length ? `<h4>Cảnh báo</h4><ul>${t.warnings.map(w => `<li>${esc(w)}</li>`).join('')}</ul>` : ''}<button class="btn btn-ghost">Đã hiểu</button></form></dialog>`;

  const stage = $('.tv-stage', host), board = $('#tv-board', host), svg = $('.tv-links', host), drawer = $('#tv-drawer', host);
  let cur = null, cycle = { dh: null, year: null }, yd = null;

  // The board keeps ONE design size (portrait, --bw × 4·--bh in css/atlas.css) and is never squeezed to the window: its frame (.tv-scroll)
  // shows it through a pan/zoom view. Drag moves it, Ctrl/⌘ + wheel or a trackpad pinch zooms at the pointer, two fingers pinch on touch,
  // plain wheel moves it while it has room and then lets the page scroll; − / + / "Vừa khung" / "100%" sit above the frame.
  const scroller = board.parentElement, zoomBar = $('.tv-zoom', host), zl = $('.tv-zl', host);
  const view = { k: 1, x: 0, y: 0, auto: true };
  const dims = () => [board.offsetWidth, board.offsetHeight];
  const apply = () => { board.style.transform = `translate(${view.x.toFixed(1)}px,${view.y.toFixed(1)}px) scale(${view.k.toFixed(4)})`; if (zl) zl.textContent = Math.round(view.k * 100) + '%'; };
  const clampPan = () => {
    const [W, H] = dims(), fw = scroller.clientWidth, fh = scroller.clientHeight, bw = W * view.k, bh = H * view.k;
    view.x = bw <= fw ? (fw - bw) / 2 : Math.min(0, Math.max(fw - bw, view.x));
    view.y = bh <= fh ? Math.max(0, Math.min((fh - bh) / 2, 12)) : Math.min(0, Math.max(fh - bh, view.y));
  };
  // default: the width of the frame, never above the design size (a wide frame shows the board at 100 %, a phone shows all of it small)
  const fitWidth = () => { const [W] = dims(), fw = scroller.clientWidth; if (!fw) return; view.k = Math.min(fw / W, 1); view.x = 0; view.y = 0; view.auto = true; clampPan(); apply(); };
  const fitAll = () => { const [W, H] = dims(), fw = scroller.clientWidth, fh = scroller.clientHeight; if (!fw || !fh) return; view.k = Math.min(fw / W, fh / H); view.auto = false; clampPan(); apply(); };
  const zoomAt = (f, cx, cy) => {
    const k = Math.min(2.5, Math.max(0.2, view.k * f)), r = k / view.k;
    view.x = cx - (cx - view.x) * r; view.y = cy - (cy - view.y) * r; view.k = k; view.auto = false; clampPan(); apply();
  };
  const centre = () => [scroller.clientWidth / 2, scroller.clientHeight / 2];
  new ResizeObserver(() => { if (view.auto) fitWidth(); else { clampPan(); apply(); } }).observe(scroller);
  fitWidth();
  const dgSel = $('[data-dg]', host);
  if (dgSel) { dgSel.value = t.school?.dignity_school || 'khao_luan'; dgSel.onchange = () => { try { localStorage.setItem('tvbt.dignity', dgSel.value); } catch {} dispatchEvent(new CustomEvent('tvbt:dignity', { detail: dgSel.value })); }; }
  const zh = $('.tv-zh', host); if (zh && matchMedia('(pointer:coarse)').matches) zh.textContent = 'Kéo để di chuyển · chụm hai ngón để thu phóng';
  // Tuần / Triệt: a black tag on the border shared by the two palaces each one covers (board coordinates, so the view does not move it)
  const ttTags = () => {
    const box = $('.tb-tt', host); if (!box) return;
    box.innerHTML = [['tuan', 'Tuần'], ['triet', 'Triệt']].map(([k, label]) => {
      const els = t.palaces.filter(p => p[k]).map(p => $(`.pal[data-i="${p.branch_index}"]`, host)).filter(Boolean);
      if (els.length !== 2) return '';
      const [a, b] = els.map(e => ({ x: e.offsetLeft, y: e.offsetTop, w: e.offsetWidth, h: e.offsetHeight }));
      const vertical = Math.abs(a.x - b.x) < 2;         // one above the other: the tag sits on the horizontal edge between them
      const x = vertical ? a.x + a.w / 2 : Math.max(a.x, b.x), y = vertical ? Math.max(a.y, b.y) : a.y + a.h;   // on the border itself, never over a row of text
      return `<span class="tb-tag" style="left:${x}px;top:${y}px">${label}</span>`;
    }).join('');
  };
  ttTags();
  // lưu stars of the current year ("L." prefix, /api/year luu_stars): appended to each palace's columns, bad ones on the right
  yearData(ctx.req, now).then(y => {
    for (const x of y.tuvi?.luu_stars || []) {
      const p = byName[x.palace], el = p && $(`.pal[data-i="${p.branch_index}"] .tb-col:${starKind(x.name) === 'neg' || x.name === 'Hóa Kỵ' ? 'last' : 'first'}-child`, host);
      if (el) el.insertAdjacentHTML('beforeend', `<span class="st tb-s tb-luu${x.basis === 'thông lệ' ? ' tb-conv' : ''} h-${hk(HANH[x.name])}${BOLD.has(x.name) ? ' tb-b' : ''}" title="Lưu ${esc(x.name)} năm ${now} · ${x.basis === 'thông lệ' ? 'theo thông lệ, chưa đối chiếu sách' : 'theo ' + esc(x.basis)}">L.${esc(x.name)}</span>`);
    }
    // nguyệt hạn of the year (TH p.115): "Th.N" at the right of the second row
    for (const [name, m] of Object.entries(y.tuvi?.nguyet_han || {})) { const p = byName[name], th = p && $(`.pal[data-i="${p.branch_index}"] .tb-th`, host); if (th) { th.textContent = `Th.${m}`; th.title = `Tháng ${m} âm lịch năm ${now} (nguyệt hạn, ${y.tuvi.nguyet_han_basis})`; } }
  }).catch(() => {});
  // built while hidden (the other system's tab, the Sổ tay view): fit the moment the frame becomes visible
  new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { if (view.auto || !board.style.transform) fitWidth(); ttTags(); if (cur == null) links(menh.branch_index); } }).observe(scroller);
  if (zoomBar) zoomBar.onclick = e => {
    const z = e.target.closest('[data-z]')?.dataset.z; if (!z) return;
    if (z === 'in') zoomAt(1.25, ...centre()); else if (z === 'out') zoomAt(0.8, ...centre());
    else if (z === 'fit') fitAll(); else if (z === 'one') zoomAt(1 / view.k, ...centre());
  };
  scroller.addEventListener('wheel', e => {
    if (e.ctrlKey || e.metaKey) { e.preventDefault(); const r = scroller.getBoundingClientRect(); zoomAt(Math.exp(-e.deltaY * 0.0025), e.clientX - r.left, e.clientY - r.top); return; }
    const x0 = view.x, y0 = view.y; view.x -= e.deltaX; view.y -= e.deltaY; clampPan();
    if (view.x !== x0 || view.y !== y0) { e.preventDefault(); view.auto = false; apply(); }
  }, { passive: false });
  // pointers: one drags, two pinch; a press that moved more than 4 px is a drag, and its click must not open a palace
  const pts = new Map(); let drag = null, pinch = null, moved = false;
  scroller.addEventListener('pointerdown', e => {
    pts.set(e.pointerId, [e.clientX, e.clientY]);
    if (pts.size === 1) { drag = { x: e.clientX, y: e.clientY, vx: view.x, vy: view.y, id: e.pointerId }; moved = false; }
    if (pts.size === 2) { const [a, b] = [...pts.values()]; pinch = { d: Math.hypot(a[0] - b[0], a[1] - b[1]) || 1, k: view.k }; }
  });
  scroller.addEventListener('pointermove', e => {
    if (!pts.has(e.pointerId)) return;
    pts.set(e.pointerId, [e.clientX, e.clientY]);
    const r = scroller.getBoundingClientRect();
    if (pinch && pts.size >= 2) {
      const [a, b] = [...pts.values()], d = Math.hypot(a[0] - b[0], a[1] - b[1]);
      zoomAt(pinch.k * d / pinch.d / view.k, (a[0] + b[0]) / 2 - r.left, (a[1] + b[1]) / 2 - r.top); moved = true; return;
    }
    if (!drag) return;
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (!moved && Math.hypot(dx, dy) < 4) return;
    if (!moved) { moved = true; scroller.setPointerCapture(e.pointerId); scroller.classList.add('dragging'); }
    view.x = drag.vx + dx; view.y = drag.vy + dy; view.auto = false; clampPan(); apply();
  });
  const up = e => { pts.delete(e.pointerId); if (pts.size < 2) pinch = null; if (!pts.size) { drag = null; scroller.classList.remove('dragging'); } };
  scroller.addEventListener('pointerup', up); scroller.addEventListener('pointercancel', up);
  scroller.addEventListener('click', e => { if (moved) { e.stopPropagation(); e.preventDefault(); moved = false; } }, true);

  const emptyDrawer = () => `<div class="drawer-empty"><div class="ident-art sm" aria-hidden="true">${compass({ animate: false, detail: 'min' })}</div><h3>Chọn một cung</h3><p class="muted">Nhấn vào một cung để xem sao, Tam Phương Tứ Chính và các nhận định liên quan. Các đường nối cho thấy cung nào đang tương tác với cung nào.</p>${evLegend()}</div>`;
  drawer.innerHTML = emptyDrawer();
  // the detail drawer, the legend, the reading hint and the scope note live in the right-hand column next to the chat (css/dash.css)
  const side = document.getElementById('tuvi-side');
  if (side) {
    side.querySelectorAll('#tv-drawer,.legend,.tv-hint,.sc').forEach(x => x.remove());
    side.prepend(drawer);
    for (const sel of ['.legend', '.tv-hint', '#scope-tv']) { const el = $(sel, host); if (el) side.append(el); }
  }

  function links(i) {
    svg.innerHTML = '';
    if (i == null) return;
    const s = t.structure[by[i].branch];
    // in board coordinates: the pan/zoom transform is undone, so the lines stay put whatever the view
    const rect = board.getBoundingClientRect(), k = view.k;
    const c = b => { const el = $(`.pal[data-i="${BRANCHES.findIndex(x => x.n === b)}"]`, host), r = el.getBoundingClientRect(); return [(r.left - rect.left) / k + r.width / k / 2, (r.top - rect.top) / k + 22]; };
    svg.setAttribute('viewBox', `0 0 ${board.offsetWidth} ${board.offsetHeight}`);
    const me = c(by[i].branch), op = c(s.opposite), t1 = c(s.tam_hop[0]), t2 = c(s.tam_hop[1]);
    const ln = (a, b, cls) => `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" class="${cls}"/>`;
    svg.innerHTML = ln(t1, t2, 'lk lk-tri') + ln(me, op, 'lk lk-op') + ln(me, t1, 'lk lk-th') + ln(me, t2, 'lk lk-th') +
      [me, op, t1, t2].map((p, k) => `<circle cx="${p[0]}" cy="${p[1]}" r="${k === 0 ? 5 : 3.5}" class="lk-dot${k === 0 ? ' me' : ''}"/>`).join('');
  }
  const relOf = i => { const s = t.structure[by[i].branch]; return [s.opposite, ...s.tam_hop].map(b => byBranch[b].branch_index); };

  function detail(i) {
    const p = by[i], s = t.structure[p.branch], d = dhByBranch[p.branch], fs = fOf(p.name);
    const minors = p.stars.filter(x => !p.major_stars.includes(x));
    const grp = k => minors.filter(x => starKind(x) === k);
    const rel = (label, branch) => { const q = byBranch[branch]; return `<button type="button" class="relp" data-i="${q.branch_index}"><span class="k">${label}</span><b>${esc(q.name)}</b><span class="muted">${esc(q.branch)} · ${esc(q.major_stars.join(', ') || 'vô chính diệu')}</span></button>`; };
    const ths = Object.entries(t.tu_hoa).filter(([, v]) => v.branch === i).map(([k, v]) => `<span class="chip chip-hoa"><span class="th th-${HOA[k].k}"><i lang="zh">${HOA[k].h}</i></span>${esc(k)} · ${esc(v.star)}</span>`).join('');
    const ver = fs.filter(f => f.basis === 'verified'), dr = fs.filter(f => f.basis !== 'verified');
    const none = '<p class="muted">Chưa có quy tắc nào đã đối chiếu sách khớp với cung này. Điều đó không có nghĩa cung “không có gì”, chỉ là bộ quy tắc hiện hành chưa phủ tới.</p>';
    const calc = `<div class="dr-tags">${p.tuan ? '<span class="tag">Tuần</span>' : ''}${p.triet ? '<span class="tag">Triệt</span>' : ''}${d ? `<span class="tag tag-dh">Đại hạn ${d.age_from}–${d.age_to} tuổi</span>` : ''}</div>
      <h5>Chính tinh</h5><div class="dr-stars">${p.major_stars.length ? p.major_stars.map(x => starHtml(x, true, p.dignity_status?.[x])).join('') : '<span class="vcd">Vô chính diệu — cung không có chính tinh.</span>'}</div>
      <h5>Phụ tinh</h5>${[['pos', 'Cát tinh'], ['neu', 'Trung tính'], ['neg', 'Sát / hung tinh']].map(([k, l]) => grp(k).length ? `<div class="dr-grp"><span class="k">${l}</span><div class="dr-stars sm">${grp(k).map(x => starHtml(x, false, p.dignity_status?.[x], false)).join('')}</div></div>` : '').join('') || '<p class="muted">Không có.</p>'}
      ${ths ? `<div class="dr-grp"><span class="k">Tứ Hóa tại cung</span><div class="chips">${ths}</div></div>` : ''}
      <h5>Tam Phương Tứ Chính</h5><div class="relps">${rel('Xung chiếu', s.opposite)}${rel('Tam hợp', s.tam_hop[0])}${rel('Tam hợp', s.tam_hop[1])}</div>
      <p class="muted small">Cung giáp: ${s.giap.map(b => `${esc(byBranch[b].name)} (${esc(b)})`).join(' · ')}</p>`;
    drawer.closest('.dash-side')?.scrollTo(0, 0);
    drawer.innerHTML = `<div class="dr-in">
      <button class="dr-x" type="button" aria-label="Đóng chi tiết cung">×</button>
      <p class="eyebrow">Cung ${esc(p.stem)} ${esc(p.branch)}${p.name === 'Mệnh' ? ' · Mệnh' : ''}${p.is_than ? ' · Thân cư' : ''}</p>
      <h3 class="dr-t">${esc(p.name)}</h3><span class="dr-han" aria-hidden="true" lang="zh">${BRANCHES[i].h}</span>
      ${palaceBubble(p, fs, terms())}<p class="dr-plain"><button type="button" class="link" data-gl="palace:${esc(p.name)}">Giải thích thêm về cung ${esc(p.name)}</button></p>
      ${tier('calc', calc)}
      ${tier('src', `<div class="pro-only">${ver.length ? findingList(ver) : none}</div><div class="easy-only">${easyReadings(fs, { empty: emptyReading('', terms(), { palace: p.name, brief: true }) })}</div><p class="muted small">Diễn giải theo hệ biểu tượng truyền thống, không phải dự báo.</p>`, { count: ver.length })}
      ${dr.length ? tier('hyp', findingList(dr), { pro: true, count: dr.length }) : ''}
    </div>`;
    autoLink(drawer, 'tv');
    $('.dr-x', drawer).onclick = () => select(null);
    $$('.relp', drawer).forEach(b => b.onclick = () => select(+b.dataset.i));
  }

  // focus = the palace whose Tam Phương Tứ Chính is lit; either the selected one or a hover/keyboard preview
  function paintFocus(i, preview = false) {
    const rel = i == null ? [] : relOf(i);
    $$('.pal', host).forEach(e => { const n = +e.dataset.i;
      e.classList.toggle('hl', !preview && n === cur); e.classList.toggle('rel', !preview && rel.includes(n));
      e.classList.toggle('pv', preview && n === i); e.classList.toggle('pv-rel', preview && rel.includes(n)); });
    board.classList.toggle('has-focus', i != null);
    links(i);
  }
  function select(i, { sheet = true, scroll = false } = {}) {
    cur = i;
    $$('.pal', host).forEach(e => e.setAttribute('aria-pressed', +e.dataset.i === cur));
    $$('.tv-ov button', host).forEach(e => e.classList.toggle('hl', +e.dataset.i === cur));
    host.classList.toggle('has-sel', cur != null);
    // the panel is a bottom sheet only where the CSS makes it one (fixed); in the desktop side column it is static and the page must not dim
    const narrow = getComputedStyle(drawer).position === 'fixed';
    if (cur == null) { drawer.classList.remove('open'); drawer.innerHTML = emptyDrawer(); document.body.classList.remove('sheet-open'); paintFocus(null); return; }
    detail(cur); drawer.classList.toggle('open', sheet || !narrow); drawer.scrollTop = 0;
    document.body.classList.toggle('sheet-open', narrow && sheet);
    requestAnimationFrame(() => paintFocus(cur));
    if (scroll) board.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
  $$('.pal', host).forEach(e => {
    e.onclick = () => select(+e.dataset.i === cur ? null : +e.dataset.i);
    e.addEventListener('pointerenter', () => { if (matchMedia('(hover:hover)').matches) paintFocus(+e.dataset.i, true); });
    e.addEventListener('focus', () => paintFocus(+e.dataset.i, true));
    e.addEventListener('blur', () => paintFocus(cur));
  });
  board.addEventListener('pointerleave', () => paintFocus(cur));
  $$('.tv-ov button', host).forEach(e => e.onclick = () => select(+e.dataset.i));
  $$('.tv-toggle button', host).forEach(b => b.onclick = () => { stage.dataset.view = b.dataset.v; $$('.tv-toggle button', host).forEach(x => x.setAttribute('aria-pressed', x === b)); requestAnimationFrame(() => links(cur)); });
  $('[data-scope]', host).onclick = () => $('#scope-dlg', host).showModal();
  addEventListener('resize', () => links(cur));
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && cur != null && !document.querySelector('dialog[open]')) select(null); });

  // ---- cycles: đại hạn → năm ----
  const yearsBox = $('#tv-years', host), cyBox = $('#tv-cy', host);
  const BADGE = { dh: 'Đại hạn', th: 'Tiểu hạn', tt: 'Lưu Thái Tuế' };
  function markCycle() {
    $$('.pal-cy', host).forEach(e => { e.innerHTML = ''; });
    $$('.pal', host).forEach(e => e.classList.remove('cy-on'));
    const add = (idx, key) => { const e = $(`.pal[data-i="${idx}"]`, host); if (!e) return; e.classList.add('cy-on'); $('.pal-cy', e).insertAdjacentHTML('beforeend', `<span class="cy cy-${key}">${BADGE[key]}</span>`); };
    if (cycle.dh != null) add(byBranch[t.dai_han[cycle.dh].branch].branch_index, 'dh');
    if (cycle.year != null && yd) { const a = byName[yd.tieu_han_palace], c = byName[yd.luu_thai_tue_palace]; if (a) add(a.branch_index, 'th'); if (c) add(c.branch_index, 'tt'); }
  }
  let yseq = 0;
  async function paintCycle() {
    const mine = ++yseq;
    $$('.tm-tab', host).forEach(b => b.setAttribute('aria-pressed', cycle.dh != null && +b.dataset.i === cycle.dh));
    if (cycle.dh == null) { yearsBox.classList.remove('open'); yearsBox.innerHTML = ''; cyBox.innerHTML = ''; yd = null; markCycle(); return; }
    const d = t.dai_han[cycle.dh], ys = yearsOf(d);
    if (yearsBox.dataset.dh !== String(cycle.dh)) {
      yearsBox.dataset.dh = cycle.dh; yearsBox.classList.add('open');
      yearsBox.innerHTML = `<p class="tm-ytitle">Các năm của đại hạn <b>cung ${esc(d.palace)}</b> <span class="muted">· mỗi ô ghi cung tiểu hạn của năm; chọn một năm để xem chi tiết</span></p><ol class="yr-strip">${ys.map(y => `<li><button type="button" class="yr${y === now ? ' now' : ''}" data-y="${y}" aria-pressed="false"><span class="yr-n">${y}</span><span class="yr-p">…</span><span class="yr-g"></span></button></li>`).join('')}</ol>`;
      $$('.yr', yearsBox).forEach(b => b.onclick = () => { cycle.year = cycle.year === +b.dataset.y ? null : +b.dataset.y; paintCycle(); });
      ys.forEach(async y => { try { const r = await yearData(ctx.req, y); if (mine !== yseq && yearsBox.dataset.dh !== String(cycle.dh)) return; const b = $(`.yr[data-y="${y}"]`, yearsBox); if (!b) return; $('.yr-p', b).textContent = r.tuvi.tieu_han_palace; $('.yr-g', b).textContent = r.tuvi.annual_pillar; } catch { /* strip still works without names */ } });
    }
    $$('.yr', yearsBox).forEach(b => { const on = cycle.year === +b.dataset.y; b.classList.toggle('is-sel', on); b.setAttribute('aria-pressed', on); });
    // decade facts (always available) + year facts (fetched)
    const hdr = `<dl class="rd-dl"><div><dt>Đại hạn</dt><dd>cung <b>${esc(d.palace)}</b> · ${esc(d.stem)} ${esc(d.branch)}</dd></div><div><dt>Tuổi mụ</dt><dd>${d.age_from}–${d.age_to}</dd></div><div><dt>Các năm</dt><dd>${ys[0]}–${ys[ys.length - 1]} <small class="muted">(tính theo tuổi mụ)</small></dd></div></dl>`;
    cyBox.innerHTML = tier('calc', hdr + (cycle.year == null ? '<p class="muted small">Chọn một năm ở trên để xem tiểu hạn, lưu Thái Tuế và lưu Tứ Hóa của năm đó.</p>' : '<p class="muted small">Đang tải…</p>'));
    select(byBranch[d.branch].branch_index, { sheet: false });
    if (cycle.year == null) { yd = null; markCycle(); return; }
    try {
      const r = await yearData(ctx.req, cycle.year); if (mine !== yseq) return; yd = r.tuvi;
      const T = terms(), x = r.tuvi;
      const rd = x.tieu_han_reading || [], easyRd = [rd.find(z => /trái chiều|không kết luận/.test(z.text))].filter(Boolean);
      const calc = `<dl class="rd-dl"><div><dt>Năm</dt><dd><b>${x.year}</b> · ${esc(x.annual_pillar)} · tuổi mụ ${x.age_tuoi_mu}</dd></div><div><dt>Đại hạn</dt><dd>${x.dai_han ? `cung ${esc(x.dai_han.palace)} (${x.dai_han.age_from}–${x.dai_han.age_to} tuổi)` : 'chưa vào'}</dd></div><div><dt>Tiểu hạn</dt><dd>cung <b>${esc(x.tieu_han_palace)}</b> · ${esc(x.tieu_han_branch)}${x.tieu_han_topic ? `<br><span class="muted small">${esc(x.tieu_han_topic)}</span>` : ''}</dd></div><div><dt>Lưu Thái Tuế</dt><dd>cung <b>${esc(x.luu_thai_tue_palace)}</b></dd></div></dl>
        <h5>Lưu Tứ Hóa</h5><ul class="yx-list">${Object.entries(x.luu_tu_hoa).map(([k, v]) => `<li><span class="th th-${HOA[k].k}"><i lang="zh">${HOA[k].h}</i></span><b>${esc(k)}</b> · ${esc(v.star)} <span class="muted">(cung ${esc(v.natal_palace)})</span></li>`).join('')}</ul>`;
      const src = `${rd.length ? `<h5>Mệnh gặp vận (tiểu hạn)</h5><ul class="yx-list pro-only">${rd.map(z => `<li>${esc(z.text)} <span class="src-chip">${esc(z.src)}</span></li>`).join('')}</ul><ul class="yx-list easy-only">${(easyRd.length ? easyRd : rd).map(z => `<li>${esc(z.text)}</li>`).join('')}</ul>${easyRd.length ? '<p class="muted small easy-only">Sách nêu hai điều kiện trái chiều cùng khớp, nên hệ thống không kết luận. Mở chế độ Chuyên sâu để xem từng điều kiện và trang sách.</p>' : ''}` : '<p class="muted small">Không có điều kiện nào trong sách khớp giữa Mệnh và cung tiểu hạn năm nay.</p>'}
        ${(x.luu_tu_hoa_reading || []).length ? `<p class="muted small">Lưu Tứ Hóa (vị trí ở phần dữ kiện): ${esc(x.luu_tu_hoa_reading[0].src || '')}.</p>` : ''}
        <p class="muted small">Dữ kiện cấu trúc theo thời gian, không phải dự đoán sự kiện. Lưu nguyệt Tử Vi chưa được hỗ trợ vì chưa có nguồn xác minh.</p>`;
      cyBox.innerHTML = tier('calc', calc) + tier('src', src);
      autoLink(cyBox, 'tv');
      markCycle();
    } catch { cyBox.innerHTML = tier('calc', hdr + '<p class="muted small">Chưa tải được dữ liệu năm này.</p>'); }
  }
  markCycle();
  $$('.tm-tab', host).forEach(b => b.onclick = () => {
    const i = +b.dataset.i; cycle = cycle.dh === i ? { dh: null, year: null } : { dh: i, year: null };
    if (cycle.dh == null) { yearsBox.dataset.dh = ''; select(null); } else centerIn($('#tv-tm-scroll', host), b);
    paintCycle();
  });
  requestAnimationFrame(() => { const b = $('.tm-tab.now', host); if (b) centerIn($('#tv-tm-scroll', host), b); });

  // Đại hạn timeline for the report
  const timelineHtml = timeline(t.dai_han.map(d => ({ title: `<span class="tl-han">${esc(d.palace)}</span>`, sub: `${esc(d.stem)} ${esc(d.branch)}`, meta: `${d.age_from}–${d.age_to} tuổi`, current: false })), { label: 'Đại hạn Tử Vi' });
  // Experimental cách-cục conditions: light up the stars and palaces that satisfy one condition.
  const bar = document.createElement('div'); bar.className = 'cx-bar'; bar.hidden = true;
  bar.innerHTML = '<span class="cx-t"></span><button type="button" class="link cx-x">Bỏ tô sáng</button>';
  $('#tv-plate .plate-h', host).after(bar);
  function clearHighlight() {
    $$('.cx-pal,.cx-star', host).forEach(e => e.classList.remove('cx-pal', 'cx-star'));
    bar.hidden = true;
  }
  function highlight(items, label = '') {
    clearHighlight();
    $('.tv-toggle button[data-v=full]', host)?.click();
    const pals = new Set();
    items.forEach(it => {
      const p = byName[it.palace]; if (!p) return;
      pals.add(p.branch_index);
      if (it.star) $$(`.pal[data-i="${p.branch_index}"] .st`, host).filter(e => e.dataset.gl === `star:${it.star}`).forEach(e => e.classList.add('cx-star'));
    });
    pals.forEach(i => $$(`.pal[data-i="${i}"],.tv-ov button[data-i="${i}"]`, host).forEach(e => e.classList.add('cx-pal')));
    $('.cx-t', bar).textContent = `Đang tô sáng: ${label || 'điều kiện đã chọn'}`; bar.hidden = false;
    $('#tv-plate', host).scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  $('.cx-x', bar).onclick = clearHighlight;
  return { highlight, clearHighlight, select: name => { const p = byName[name]; if (p) select(p.branch_index, { scroll: true }); }, byName, menh, than, timelineHtml };
}
