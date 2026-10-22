// Bát Tự "Energy Architecture": pillar plate + relation arcs, seasonal dial, Five Elements, Đại vận timeline and one contextual reading panel.
// Presentation only: every value is read from the chart / year responses. Report pieces (`parts`) are unchanged.
import { $, $$, esc, bd, DM, STEMS, BRANCHES, EL, ELEMENTS, elChip, elIcon, PILLAR_LABEL, tenGodGroup, TEN_GOD_GROUPS } from './util.js';
import { fiveElements } from './elements.js';
import { timeline, findingList } from './ui.js';
import { easyReadings } from './beginner.js';
import { terms, autoLink } from './glossary.js';
import { collapseWhenDash } from './dash.js';
import { tier, evLegend, yearData, periodYears, luckFirstYear, luckIndexOn, centerIn, onPick } from './atlas.js';

const ORDER = ['year', 'month', 'day', 'hour'];
// the 30 nạp âm in cycle order, the same table as engine/tvbt/ganzhi.py NAP_AM_NAMES (index = cycle index // 2)
const NAP_AM = ['Hải Trung Kim', 'Lư Trung Hỏa', 'Đại Lâm Mộc', 'Lộ Bàng Thổ', 'Kiếm Phong Kim', 'Sơn Đầu Hỏa', 'Giản Hạ Thủy', 'Thành Đầu Thổ', 'Bạch Lạp Kim',
  'Dương Liễu Mộc', 'Tuyền Trung Thủy', 'Ốc Thượng Thổ', 'Tích Lịch Hỏa', 'Tùng Bách Mộc', 'Trường Lưu Thủy', 'Sa Trung Kim', 'Sơn Hạ Hỏa', 'Bình Địa Mộc',
  'Bích Thượng Thổ', 'Kim Bạch Kim', 'Phú Đăng Hỏa', 'Thiên Hà Thủy', 'Đại Dịch Thổ', 'Thoa Xuyến Kim', 'Tang Đố Mộc', 'Đại Khê Thủy', 'Sa Trung Thổ',
  'Thiên Thượng Hỏa', 'Thạch Lựu Mộc', 'Đại Hải Thủy'];
const napAm = (st, br) => NAP_AM[Math.floor((((6 * st - 5 * br) % 60) + 60) % 60 / 2)];
const GOD_SHORT = { 'Tỉ Kiên': 'Tỉ', 'Kiếp Tài': 'Kiếp', 'Thực Thần': 'Thực', 'Thương Quan': 'Thương', 'Chính Tài': 'Tài', 'Thiên Tài': 'T.Tài', 'Chính Quan': 'Quan',
  'Thất Sát': 'Sát', 'Chính Ấn': 'Ấn', 'Thiên Ấn': 'Kiêu' };
const HK = { 'Kim': 'kim', 'Mộc': 'moc', 'Thủy': 'thuy', 'Hỏa': 'hoa', 'Thổ': 'tho' };
/** "Mệnh bàn tứ trụ": the classic table of the four pillars (dates, ten gods, the eight characters coloured by hành, nạp âm, hidden stems,
 *  their ten gods, the twelve stages), then ten đại vận and ten lưu niên with the current ones marked, then Mệnh cung, Thai nguyên and the
 *  two Không vong. Every value comes from the chart response; no thần sát row, the page is not sent them. */
function menhBan(b, ctx) {
  const P = b.pillars, req = ctx.req, lunar = ctx.chartRaw?.tuvi?.lunar, now = new Date().getFullYear();
  const col = f => ORDER.map(k => `<td>${f(P[k], k)}</td>`).join('');
  const ch = (txt, el, big = false) => `<span class="mb-c h-${HK[el] || 'none'}${big ? ' mb-big' : ''}">${esc(txt)}</span>`;
  const lp = b.luck_pillars.slice(0, 10), birthY = req.year;
  const cur = luckIndexOn(lp);                // by the exact start date, not the birth year + age (audit BZ-5)
  const yrs = Array.from({ length: 10 }, (_, i) => now - 3 + i);
  const gzY = y => `${STEMS[((y - 4) % 10 + 10) % 10].n} ${BRANCHES[((y - 4) % 12 + 12) % 12].n}`;
  const ex = b.extras || {};
  const two = s => { const [a, c] = String(s).split(' '); return `${esc(a)}<br>${esc(c || '')}`; };
  return `<div class="mb" role="table" aria-label="Mệnh bàn tứ trụ">
    <div class="mb-head"><h3 class="mb-t">Mệnh bàn tứ trụ</h3><dl class="mb-meta">
      <div><dt>Dương lịch</dt><dd>${bd(`${req.day}/${req.month}/`, req.day != null, DM)}${req.year}${bd(` - ${req.hour}:${String(req.minute || 0).padStart(2, '0')}`, req.hour != null, ' - giờ ẩn')}</dd></div>
      ${lunar ? `<div><dt>Âm lịch</dt><dd>${bd(`${lunar.day}/${lunar.month}${lunar.leap ? ' nhuận' : ''}/`, lunar.day != null, DM)}${lunar.year}</dd></div>` : ''}
      <div><dt>Khởi vận</dt><dd>${esc(b.luck_start.start_date.split('-').reverse().join('/'))} · sau ${b.luck_start.years} năm ${b.luck_start.months} tháng</dd></div>
    </dl></div>
    <table class="mb-tab"><tbody>
      <tr class="mb-dates"><th>Năm sinh<br>dương</th><td>${req.year}</td><td>${bd(req.month)}</td><td>${bd(req.day)}</td><td>${bd(`${req.hour}:${String(req.minute || 0).padStart(2, '0')}`, req.hour != null)}</td></tr>
      <tr><th>Thập thần</th>${col((p, k) => k === 'day' ? '<b>NHẬT CHỦ</b>' : esc(GOD_SHORT[p.stem_ten_god] || p.stem_ten_god || ''))}</tr>
      <tr class="mb-bt"><th>Bát tự</th>${col(p => ch(STEMS[p.stem].n.toLocaleUpperCase('vi'), STEMS[p.stem].e, true) + '<br>' + ch(BRANCHES[p.branch].n.toLocaleUpperCase('vi'), BRANCHES[p.branch].e, true))}</tr>
      <tr><th>Nạp âm<br>ngũ hành</th>${col(p => esc(napAm(p.stem, p.branch)))}</tr>
      <tr><th>Can chi<br>tàng ẩn</th>${col(p => p.hidden.map(h => ch(h.name, h.element)).join(' '))}</tr>
      <tr><th>Phó tinh</th>${col(p => p.hidden.map(h => esc(GOD_SHORT[h.ten_god] || h.ten_god)).join(' '))}</tr>
      <tr><th>Thập nhị<br>thần</th>${col(p => esc(p.stage_vs_day_master || ''))}</tr>
    </tbody></table>
    <table class="mb-tab mb-luck"><tbody>
      <tr><th>Đại vận</th>${lp.map((l, i) => `<td class="${i === cur ? 'mb-now' : ''}">${two(l.name)}</td>`).join('')}</tr>
      <tr class="mb-red"><th>Năm</th>${lp.map((l, i) => { const a = Math.round(l.start_age) + 1; return `<td class="${i === cur ? 'mb-now' : ''}">${a}-${a + 9}t<br>${luckFirstYear(l.start_year_exact)}</td>`; }).join('')}</tr>
      <tr><th>Lưu niên</th>${yrs.map(y => `<td class="${y === now ? 'mb-now' : ''}">${two(gzY(y))}</td>`).join('')}</tr>
      <tr><th>Năm</th>${yrs.map(y => `<td class="${y === now ? 'mb-now' : ''}">${y}<br><span class="mb-red">${y - birthY + 1}t</span></td>`).join('')}</tr>
    </tbody></table>
    <table class="mb-tab mb-menh"><tbody>
      <tr class="mb-sub"><th rowspan="2">Mệnh</th><td>Mệnh cung</td><td>Thai nguyên</td><td>Niên không</td><td>Nhật không</td></tr>
      <tr><td>${esc(ex.ming_gong || '—')}</td><td>${esc(ex.thai_yuan || '—')}</td><td>${esc((ex.kong_wang_year_pillar_view || []).join(' - ') || '—')}</td><td>${esc((ex.kong_wang_day || []).join(' - ') || '—')}</td></tr>
    </tbody></table>
  </div>`;
}
const PL = { year: 'Năm', month: 'Tháng', day: 'Ngày', hour: 'Giờ' };
const PH = { year: '年', month: '月', day: '日', hour: '時' };
const plPair = s => String(s).split('-').map(x => PL[x] || x).join(' – ');
const REL_TITLE = {
  stem_combine: 'Thiên can hợp', stem_clash: 'Thiên can xung', branch_six_combine: 'Địa chi lục hợp', branch_clash: 'Địa chi lục xung',
  branch_harm: 'Địa chi lục hại', branch_destroy: 'Địa chi phá', branch_triad_complete: 'Tam hợp', branch_meeting_complete: 'Tam hội', branch_semi_triad: 'Bán hợp',
  branch_penalty: 'Hình', branch_self_penalty: 'Tự hình',
};
// Han marks for the relation badges (vocabulary only) and which lane (stems / branches) a relation belongs to.
const REL_META = {
  stem_combine: ['合', 'can'], stem_clash: ['沖', 'can'], branch_six_combine: ['合', 'chi'], branch_clash: ['沖', 'chi'], branch_harm: ['害', 'chi'],
  branch_destroy: ['破', 'chi'], branch_triad_complete: ['三合', 'chi'], branch_meeting_complete: ['三會', 'chi'], branch_semi_triad: ['半合', 'chi'], branch_penalty: ['刑', 'chi'], branch_self_penalty: ['自刑', 'chi'],
};
const YEAR_REL = { can_hợp: 'Thiên can hợp', can_xung: 'Thiên can xung', 'chi_lục hợp': 'Địa chi lục hợp', chi_xung: 'Địa chi xung', chi_hại: 'Địa chi hại', chi_phá: 'Địa chi phá', chi_hình: 'Địa chi hình', chi_tam_hợp: 'Địa chi tam hợp', chi_tam_hội: 'Địa chi tam hội' };
const WITH = { year: 'trụ Năm', month: 'trụ Tháng', day: 'trụ Ngày', hour: 'trụ Giờ' };
const first = s => (s || '').split(/(?<=\.)\s/)[0];

function relText(k, it) {
  const chars = (it.stems ? it.stems.map(i => STEMS[i]?.n) : it.branches ? it.branches.map(i => BRANCHES[i]?.n) : it.branch != null ? [BRANCHES[it.branch]?.n] : []).filter(Boolean).join(' · ');
  const extra = it.potential_element ? ` — tiềm năng hóa ${it.potential_element}${it.transforms ? ' (đã hóa)' : ' (chưa xét hóa)'}` : '';
  return `<li><span class="rel-p">${esc(plPair(it.pillars || ''))}</span><b>${esc(chars)}</b>${extra ? `<span class="muted">${esc(extra)}</span>` : ''}</li>`;
}
const relChars = it => (it.stems ? it.stems.map(i => STEMS[i]?.n) : it.branches ? it.branches.map(i => BRANCHES[i]?.n) : it.branch != null ? [BRANCHES[it.branch]?.n] : []).filter(Boolean).join(' · ');

/** Which selectable thing a finding belongs to, from its claim id (routing for display only; unmatched findings stay in the report). */
function targetOf(f) {
  const c = f.claim;
  if (/^bt_ri_gan|^bt_nap_am|^bt_zz_hn_nhat_chi/.test(c)) return 'p:day';
  if (/^bt_zz_hn_nguyet/.test(c)) return 'p:month';
  if (/^bt_zz_nghe_(tru_gio|can_gio)/.test(c)) return 'p:hour';
  const m = c.match(/^bt_thieu_hanh_(.+)$/);
  const e = m && ELEMENTS.find(x => x.toLowerCase() === m[1]);
  return e ? 'e:' + e : 'chart';
}

export function renderBazi(host, b, ctx) {
  const counts = Object.fromEntries(ELEMENTS.map(e => [e, 0]));
  ORDER.forEach(k => { counts[STEMS[b.pillars[k].stem].e]++; counts[BRANCHES[b.pillars[k].branch].e]++; });
  const dmP = b.pillars.day, dmS = STEMS[dmP.stem], month = b.pillars.month, mb = BRANCHES[month.branch];
  const gods = Object.fromEntries(TEN_GOD_GROUPS.map(g => [g, 0]));
  ORDER.filter(k => k !== 'day').forEach(k => { const g = tenGodGroup(b.pillars[k].stem_ten_god); if (g) gods[g]++; });
  const godChips = TEN_GOD_GROUPS.filter(g => gods[g]).map(g => `<span class="chip">${g}<b>×${gods[g]}</b></span>`).join('') || '<span class="muted">—</span>';
  const now = new Date().getFullYear(), nowFrac = now + (new Date() - new Date(now, 0, 1)) / (365.25 * 864e5);
  const lp = b.luck_pillars;
  const curIdx = luckIndexOn(lp);
  const tl = timeline(lp.map((l, i) => ({
    title: `<span class="tl-han">${esc(l.name)}</span>`, sub: `${esc(l.ten_god)}`, meta: `${Math.round(l.start_age)} tuổi · ${luckFirstYear(l.start_year_exact)}`,
    el: EL[STEMS[l.stem].e].slug, current: i === curIdx,
  })), { label: 'Các đại vận Bát Tự' });

  // ---- report pieces (unchanged content) ----
  const rels = Object.entries(b.relations).filter(([, v]) => v.length);
  const relBody = rels.length
    ? rels.map(([k, v]) => `<div class="rel-g"><h5>${REL_TITLE[k] || k}</h5><ul class="rel">${v.map(it => relText(k, it)).join('')}</ul></div>`).join('') + '<p class="muted small">Chỉ là dữ kiện về quan hệ giữa các chữ; việc “hóa” hay “hợp mà không hóa” chưa được xét.</p>'
    : '<p class="muted">Không phát hiện quan hệ hợp, xung, hại, phá, hình nào giữa các trụ.</p>';

  const nguyetLenh = `<p>Nguyệt lệnh là địa chi của tháng sinh (<b>${esc(mb.n)}</b>, hành ${mb.e}). Nhật Chủ ${esc(dmS.n)} ở trạng thái <b>${esc(month.stage_vs_day_master)}</b> tại tháng này.</p><p class="muted">Tháng Bát Tự đổi theo <i>tiết</i> trong 24 tiết khí chứ không theo mùng một âm lịch. Tiết gần nhất trước giờ sinh: <b>${new Date(b.jie_used.prev_jie_utc).toLocaleDateString('vi-VN', { timeZone: ctx.req.tz === 'Asia/Hanoi' ? 'Asia/Bangkok' : ctx.req.tz || 'Asia/Ho_Chi_Minh', day: 'numeric', month: 'numeric', year: 'numeric' })}</b>.</p>`;
  const thapThan = `<div class="tg-rows">${ORDER.map(k => { const p = b.pillars[k]; return `<div><span class="k">${PL[k]}</span><b>${k === 'day' ? 'Nhật Chủ' : esc(p.stem_ten_god)}</b><span class="muted">can ${esc(STEMS[p.stem].n)}</span></div>`; }).join('')}</div>`;
  const tangCan = `<div class="tc-rows">${ORDER.map(k => { const p = b.pillars[k]; return `<div><h5>${PL[k]} · ${esc(BRANCHES[p.branch].n)}</h5>${p.hidden.map(h => `<div class="tc">${elChip(h.element)} <b>${esc(h.name)}</b> <span class="muted">${esc(h.ten_god)}</span></div>`).join('')}</div>`; }).join('')}</div>`;
  // Thấu can / thông căn: purely positional facts (is a visible stem's own character hidden in some branch, and vice versa).
  const hiddenOf = k => b.pillars[k].hidden.map(h => h.stem);
  const rootRows = ORDER.map(k => {
    const p = b.pillars[k], st = STEMS[p.stem], sameEl = ORDER.filter(j => b.pillars[j].hidden.some(h => h.element === st.e)).map(j => PL[j]);
    const exact = ORDER.filter(j => hiddenOf(j).includes(p.stem)).map(j => PL[j]);
    return `<tr><th scope="row">${PL[k]} · ${esc(st.n)} <small>${st.e}</small></th><td>${exact.length ? esc(exact.join(', ')) : '<span class="muted">không</span>'}</td><td>${sameEl.length ? esc(sameEl.join(', ')) : '<span class="muted">không</span>'}</td></tr>`;
  }).join('');
  const thongCan = `<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Thiên can</th><th>Cùng chữ trong tàng can của trụ</th><th>Cùng hành trong tàng can của trụ</th></tr></thead><tbody>${rootRows}</tbody></table></div><p class="muted small">Đây là dữ kiện vị trí. Việc một can “có căn” mạnh hay yếu còn tùy nhiều điều kiện (mùa, hợp, xung...) mà hệ thống chưa xét.</p>`;

  // ---- relations normalised to pillar indices (for the arcs) ----
  const relItems = [];
  Object.entries(b.relations).forEach(([kind, arr]) => arr.forEach(it => {
    const meta = REL_META[kind]; if (!meta) return;
    let idx = it.pillars ? String(it.pillars).split('-').map(k => ORDER.indexOf(k)).filter(i => i >= 0) : [];
    if (!idx.length && it.branches) idx = ORDER.map((k, i) => it.branches.includes(b.pillars[k].branch) ? i : -1).filter(i => i >= 0);
    idx = [...new Set(idx)].sort((x, y) => x - y);
    if (idx.length < 2) return;
    relItems.push({ id: relItems.length, kind, han: meta[0], lane: meta[1], idx, it, title: REL_TITLE[kind] || kind });
  }));

  // ---- findings routed to what they describe ----
  const allF = (ctx.reason.systems.bat_tu?.findings || []).map(f => ({ ...f, sys: 'bat_tu' }));
  const fFor = key => allF.filter(f => targetOf(f) === key);
  const none = '<p class="muted">Chưa có quy tắc nào đã đối chiếu sách khớp với mục này. Điều đó không có nghĩa mục này “không có gì”, chỉ là bộ quy tắc hiện hành chưa phủ tới.</p>';
  const readingTiers = fs => {
    const ver = fs.filter(f => f.basis === 'verified'), dr = fs.filter(f => f.basis !== 'verified');
    return tier('src', `<div class="pro-only">${ver.length ? findingList(ver) : none}</div><div class="easy-only">${easyReadings(fs, { empty: none })}</div><p class="muted small">Diễn giải theo hệ biểu tượng truyền thống, không phải dự báo.</p>`, { count: ver.length })
      + (dr.length ? tier('hyp', findingList(dr), { pro: true, count: dr.length }) : '');
  };

  // ---- plate markup ----
  const stemCell = (k, p) => { const s = STEMS[p.stem]; return `<div class="bz-g el-${EL[s.e].slug}" data-el="${s.e}"><span class="g-han" lang="zh">${s.h}</span><span class="g-vn">${esc(s.n)}</span><span class="g-el">${elIcon(s.e, 11)}${s.e}</span>${k === 'day' ? '<span class="seal" title="Thiên can của trụ Ngày là Nhật Chủ"><i lang="zh">日主</i>Nhật Chủ</span>' : ''}</div>`; };
  const branchCell = (k, p) => { const s = BRANCHES[p.branch]; return `<div class="bz-g el-${EL[s.e].slug}" data-el="${s.e}"><span class="g-han" lang="zh">${s.h}</span><span class="g-vn">${esc(s.n)}</span><span class="g-el">${elIcon(s.e, 11)}${s.e}</span></div>`; };
  const row = (cls, label, cell) => `<div class="bz-row ${cls}"><span class="bz-rl">${label}</span>${ORDER.map(k => `<div class="bz-c" data-pillar="${k}">${cell(k, b.pillars[k])}</div>`).join('')}</div>`;
  const lane = (key, label) => `<div class="bz-lane" data-lane="${key}"><span class="bz-rl">${label}</span><div class="bz-lane-s"><svg role="group" aria-label="${label}"></svg><p class="bz-lane-n"></p></div></div>`;

  host.innerHTML = `
    <div class="bz-stage">
      <div class="bz-plate" id="bz-plate">
        ${menhBan(b, ctx)}
        <details class="bz-more"><summary>Quan hệ can chi và chi tiết từng trụ <span>chạm vào một trụ để mở lớp đọc</span></summary>
        <header class="plate-h"><h3 id="bz-h2"><i lang="zh">八字</i>Bốn trụ · tám chữ</h3><span class="plate-k">Chạm vào một trụ, một cung nối hoặc một vận</span></header>
        <div class="bz-arcs">${lane('can', 'Quan hệ Thiên can')}${lane('chi', 'Quan hệ Địa chi')}</div>
        <div class="bz-grid" role="group" aria-labelledby="bz-h2">
          <div class="bz-row bz-head"><span class="bz-rl"></span>${ORDER.map(k => `<div class="bz-c" data-pillar="${k}"><button type="button" class="bz-ch" data-pillar="${k}" aria-pressed="false"><i lang="zh">${PH[k]}</i>Trụ ${PILLAR_LABEL[k]}</button></div>`).join('')}</div>
          ${row('bz-stems', 'Thiên can', stemCell)}
          <div class="bz-row bz-join" aria-hidden="true"><span class="bz-rl"></span>${ORDER.map(k => `<div class="bz-c" data-pillar="${k}"><i></i></div>`).join('')}</div>
          ${row('bz-branches', 'Địa chi', branchCell)}
          ${row('bz-hids', 'Tàng can', (k, p) => `<div class="bz-hid">${p.hidden.map((h, i) => `<span class="hid el-${EL[h.element].slug}" data-el="${h.element}"><i>${i === 0 ? 'Chính' : i === 1 ? 'Trung' : 'Dư'}</i><b>${esc(h.name)}</b>${elIcon(h.element, 10)}<em>${esc(h.ten_god)}</em></span>`).join('')}</div>`)}
          ${row('bz-gods', 'Thập thần', (k, p) => `<b class="${k === 'day' ? 'is-dm' : ''}">${k === 'day' ? 'Nhật Chủ' : esc(p.stem_ten_god)}</b>`)}
          ${row('bz-life', 'Trường sinh', (k, p) => `<span>${esc(p.stage_vs_day_master)}</span>`)}
        </div></details>
      </div>
      <aside class="bz-panel" id="bz-panel" aria-live="polite" aria-label="Lớp đọc theo lựa chọn"></aside>
    <div class="bz-instr">
      <section class="bz-fe" aria-labelledby="bz-fe-t"><header class="plate-h"><h3 id="bz-fe-t"><i lang="zh">五行</i>Ngũ Hành trong lá số</h3><span class="plate-k">Đếm 8 chữ trên bốn trụ</span></header><div id="bz-fe"></div></section>
      <section class="bz-dial" aria-labelledby="bz-dial-t"><header class="plate-h"><h3 id="bz-dial-t"><i lang="zh">月令</i>Khí tháng</h3><span class="plate-k">Nguyệt lệnh và vị trí các địa chi</span></header><div id="bz-dial"></div></section>
    </div>
    <section class="bz-time" aria-labelledby="bz-tm-t">
      <header class="plate-h"><h3 id="bz-tm-t"><i lang="zh">大運</i>Đại vận</h3><span class="plate-k">${esc(b.luck_direction)} · khởi vận sau ${b.luck_start.years} năm ${b.luck_start.months} tháng · chọn một vận để mở mười năm</span></header>
      <div class="tm-scroll" id="tm-scroll"><ol class="tm-track" id="tm-track" style="--n:${lp.length}">${lp.map((l, i) => {
        const st = STEMS[l.stem], br = BRANCHES[l.branch], yrs = periodYears(l.start_year_exact, lp[i + 1]?.start_year_exact);
        return `<li><button type="button" class="tm-tab el-${EL[st.e].slug}${i === curIdx ? ' now' : ''}" data-i="${i}" aria-pressed="false"${i === curIdx ? ' aria-current="true"' : ''}>
          <span class="tm-age">${Math.round(l.start_age)} tuổi</span><span class="tm-han" lang="zh">${st.h}${br.h}</span><span class="tm-vn">${esc(l.name)}</span><span class="tm-god">${esc(l.ten_god)}</span><span class="tm-yr">${yrs[0]}–${yrs[yrs.length - 1]}</span>${i === curIdx ? '<span class="tm-now">Hiện tại</span>' : ''}</button></li>`; }).join('')}
        ${(() => { const i = curIdx; if (i < 0) return ''; const l = lp[i], nx = lp[i + 1], span = (nx ? nx.start_year_exact : l.start_year_exact + 10) - l.start_year_exact, f = Math.min(Math.max((nowFrac - l.start_year_exact) / span, 0), 1); return `<span class="tm-needle" style="left:${((i + f) / lp.length * 100).toFixed(2)}%" title="Hôm nay"><i>Nay ${now}</i></span>`; })()}
      </ol></div>
      <div class="tm-years" id="tm-years" aria-live="polite"></div>
    </section>
    </div>`;

  // ---- seasonal dial ----
  const dial = (() => {
    const cx = 160, cy = 160, R0 = 98, R1 = 140, pt = (r, deg) => { const a = (deg - 90) * Math.PI / 180; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; };
    const f = n => n.toFixed(1), sector = (i) => { const a0 = i * 30 - 15, a1 = i * 30 + 15, p = [pt(R1, a0), pt(R1, a1), pt(R0, a1), pt(R0, a0)]; return `M${f(p[0][0])} ${f(p[0][1])}A${R1} ${R1} 0 0 1 ${f(p[1][0])} ${f(p[1][1])}L${f(p[2][0])} ${f(p[2][1])}A${R0} ${R0} 0 0 0 ${f(p[3][0])} ${f(p[3][1])}Z`; };
    const seg = BRANCHES.map((br, i) => { const [hx, hy] = pt(122, i * 30), [nx, ny] = pt(107, i * 30);
      return `<g class="dl-seg el-${EL[br.e].slug}${i === month.branch ? ' is-month' : ''}"><path d="${sector(i)}"><title>${br.n} · hành ${br.e} · mùa ${EL[br.e].season}</title></path><text x="${f(hx)}" y="${f(hy)}" class="dl-han" lang="zh" text-anchor="middle" dominant-baseline="central">${br.h}</text><text x="${f(nx)}" y="${f(ny)}" class="dl-vn" text-anchor="middle" dominant-baseline="central">${br.n}</text></g>`; }).join('');
    const used = {}, OFF = [0, 16, -16, 32];
    const marks = ORDER.map(k => { const bi = b.pillars[k].branch, n = used[bi] = (used[bi] || 0) + 1, ang = bi * 30 + OFF[n - 1], [x, y] = pt(80, ang), [x0, y0] = pt(R0, ang);
      return `<g class="dl-mk${k === 'day' ? ' is-day' : ''}" data-pillar="${k}"><line x1="${f(x0)}" y1="${f(y0)}" x2="${f(x)}" y2="${f(y)}"/><circle cx="${f(x)}" cy="${f(y)}" r="11"/><text x="${f(x)}" y="${f(y)}" lang="zh" text-anchor="middle" dominant-baseline="central">${PH[k]}</text><title>Trụ ${PL[k]}: ${esc(BRANCHES[bi].n)}</title></g>`; }).join('');
    const mAng = month.branch * 30, tip = pt(R1 + 2, mAng), pl = pt(R1 + 13, mAng - 5), pr = pt(R1 + 13, mAng + 5);
    return `<div class="dl"><svg viewBox="0 0 320 320" role="img" aria-label="Vòng mười hai địa chi: tháng sinh ${esc(mb.n)} (${mb.e}); Nhật Chủ ${esc(dmS.n)} ở trạng thái ${esc(month.stage_vs_day_master)} tại tháng này">
      <circle cx="160" cy="160" r="150" class="dl-o"/>${seg}<circle cx="160" cy="160" r="${R0}" class="dl-i"/>
      <path class="dl-pt" d="M${f(tip[0])} ${f(tip[1])}L${f(pl[0])} ${f(pl[1])}L${f(pr[0])} ${f(pr[1])}Z"><title>Nguyệt lệnh</title></path>${marks}
      <text x="160" y="126" class="dl-k" text-anchor="middle">NHẬT CHỦ</text><text x="160" y="160" class="dl-dm el-${EL[dmS.e].slug}" lang="zh" text-anchor="middle" dominant-baseline="central">${dmS.h}</text>
      <text x="160" y="190" class="dl-nm" text-anchor="middle">${esc(dmS.n)} · ${dmS.e}</text></svg>
      <dl class="dl-facts"><div><dt>Tháng sinh (Nguyệt lệnh)</dt><dd>${esc(mb.n)} · hành ${mb.e} · ${EL[mb.e].season.toLowerCase() === 'giao mùa' ? 'giao mùa' : 'mùa ' + EL[mb.e].season.toLowerCase()}</dd></div><div><dt>${esc(dmS.n)} tại tháng này</dt><dd>${esc(month.stage_vs_day_master)} <small>trường sinh</small></dd></div><div><dt>Địa chi trên bốn trụ</dt><dd>${ORDER.map(k => `${PL[k]} ${esc(BRANCHES[b.pillars[k].branch].n)}`).join(' · ')}</dd></div></dl></div>`;
  })();
  $('#bz-dial', host).innerHTML = dial;

  // ---- elements ----
  const plate = $('#bz-plate', host), panel = $('#bz-panel', host), chips = $$('.bz-ch', host);
  // the detail panel lives in the right-hand column next to the chat (css/dash.css)
  collapseWhenDash(document.getElementById('bazi-report'));
  const bzSide = document.getElementById('bazi-side');
  if (bzSide) { bzSide.querySelector('#bz-panel')?.remove(); bzSide.prepend(panel); }
  const cells = $$('[data-pillar]', plate), cols = $$('.bz-c', plate);
  const glyphs = $$('.bz-g,.hid', plate);
  const apply = el => glyphs.forEach(c => { const hit = el && c.dataset.el === el; c.classList.toggle('hit', !!hit); c.classList.toggle('dim', !!el && !hit); });
  let S = { kind: null };
  const fe = fiveElements($('#bz-fe', host), { counts, onSelect: el => { apply(el); if (el) setSel({ kind: 'element', el }, { fromFe: true }); else if (S.kind === 'element') setSel({ kind: null }, { fromFe: true }); } });

  // ---- relation arcs (drawn at the real pixel width so badges stay round) ----
  const lanes = Object.fromEntries($$('.bz-lane', host).map(l => [l.dataset.lane, l]));
  function drawArcs() {
    Object.entries(lanes).forEach(([key, el]) => {
      const svg = $('svg', el), W = svg.parentElement.clientWidth, items = relItems.filter(r => r.lane === key);
      const note = $('.bz-lane-n', el);
      if (!items.length) { svg.setAttribute('height', 0); svg.innerHTML = ''; note.textContent = 'Không có quan hệ'; el.classList.add('empty'); return; }
      el.classList.remove('empty'); note.textContent = '';
      const span = Math.max(...items.map(r => r.idx[r.idx.length - 1] - r.idx[0])), H = 26 + span * 11;
      svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.setAttribute('height', H); svg.setAttribute('width', W);
      const X = i => (i + .5) / 4 * W, base = H - 5;
      svg.innerHTML = items.map(r => {
        const a = r.idx[0], z = r.idx[r.idx.length - 1], h = 10 + (z - a) * 11, x1 = X(a), x2 = X(z), xm = (x1 + x2) / 2;
        return `<g class="rl-a rl-${/合|會/.test(r.han) ? 'join' : 'break'}" data-rel="${r.id}" role="button" tabindex="0" aria-label="${esc(r.title)}: ${esc(r.idx.map(i => PL[ORDER[i]]).join(' – '))}">
          <path d="M${x1} ${base}C${x1} ${base - h * 1.3} ${x2} ${base - h * 1.3} ${x2} ${base}" class="rl-p"/>
          ${r.idx.map(i => `<circle cx="${X(i)}" cy="${base}" r="3" class="rl-d"/>`).join('')}
          <circle cx="${xm}" cy="${base - h * .98}" r="${r.han.length > 1 ? 15 : 12}" class="rl-b"/><text x="${xm}" y="${base - h * .98}" lang="zh" class="rl-t" text-anchor="middle" dominant-baseline="central">${r.han}</text><title>${esc(r.title)}</title></g>`;
      }).join('');
      $$('.rl-a', svg).forEach(g => onPick(g, () => setSel(S.kind === 'rel' && S.id === +g.dataset.rel ? { kind: null } : { kind: 'rel', id: +g.dataset.rel })));
    });
    paintArcs();
  }
  function paintArcs() {
    const sel = S.kind === 'pillar' ? S.i : null;
    $$('.rl-a', host).forEach(g => {
      const r = relItems[+g.dataset.rel], on = (S.kind === 'rel' && S.id === r.id) || (sel != null && r.idx.includes(sel));
      g.classList.toggle('on', on); g.classList.toggle('off', (S.kind === 'rel' || sel != null) && !on);
    });
  }
  if ('ResizeObserver' in window) new ResizeObserver(() => drawArcs()).observe($('.bz-arcs', host)); else addEventListener('resize', drawArcs);

  // ---- panel ----
  const row2 = (k, v) => `<div><dt>${k}</dt><dd>${v}</dd></div>`;
  const hidList = p => `<ul class="rd-hid">${p.hidden.map((h, i) => `<li class="el-${EL[h.element].slug}"><i>${i === 0 ? 'Chính' : i === 1 ? 'Trung' : 'Dư'}</i><b class="gl" role="button" tabindex="0" data-gl="can:${esc(h.name)}">${esc(h.name)}</b>${elChip(h.element)}<span class="muted">${esc(h.ten_god)}</span></li>`).join('')}</ul>`;
  const relLi = r => `<li class="rel-i"><span class="rel-han" lang="zh">${r.han}</span><span><b>${esc(r.title)}</b> · ${esc(relChars(r.it))}<br><span class="muted small">${esc(plPair(r.idx.map(i => ORDER[i]).join('-')))}${r.it.potential_element ? ` — tiềm năng hóa ${esc(r.it.potential_element)} (${r.it.transforms ? 'đã hóa' : 'chưa xét hóa'})` : ''}</span></span></li>`;
  const head = (eye, title, sub = '') => `<header class="rd-h"><div><p class="rd-eye">${eye}</p><h3>${title}</h3>${sub ? `<p class="rd-sub">${sub}</p>` : ''}</div>${S.kind ? '<button type="button" class="rd-x" aria-label="Bỏ lựa chọn">×</button>' : ''}</header>`;

  function panelDefault() {
    return `${head('Nhật Chủ · bạn trong lá số', `<span class="rd-glyph el-${EL[dmS.e].slug}"><span lang="zh">${dmS.h}</span>${esc(dmS.n)}</span>`, `${elChip(dmS.e)}`)}
      <dl class="rd-dl">${row2('Nguyệt lệnh', `${esc(mb.n)} · hành ${mb.e}`)}${row2('Trường sinh tại tháng', esc(month.stage_vs_day_master))}${row2('Đại vận', `${esc(b.luck_direction)}, khởi vận ${b.luck_start.years} năm ${b.luck_start.months} tháng`)}</dl>
      <div class="rd-chips"><span class="rd-k">Thập thần trên thiên can</span><span class="chips">${godChips}</span></div>
      <p class="rd-hint">Bảng này chỉ hiện điều bạn chọn. Chạm vào một trụ, một hành trên sơ đồ Ngũ Hành, một cung nối phía trên các trụ, hoặc một đại vận bên dưới.</p>
      ${evLegend()}`;
  }
  function panelPillar(i) {
    const k = ORDER[i], p = b.pillars[k], st = STEMS[p.stem], br = BRANCHES[p.branch], isDay = k === 'day';
    const rl = relItems.filter(r => r.idx.includes(i));
    const calc = `<dl class="rd-dl">${row2('Thiên can', `<span class="gl" role="button" tabindex="0" data-gl="can:${esc(st.n)}">${esc(st.n)}</span> <span lang="zh">${st.h}</span> ${elChip(st.e)}`)}${row2('Địa chi', `<span class="gl" role="button" tabindex="0" data-gl="chi:${esc(br.n)}">${esc(br.n)}</span> <span lang="zh">${br.h}</span> ${elChip(br.e)}`)}${row2('Thập thần của can', isDay ? 'Nhật Chủ' : `<span class="gl" role="button" tabindex="0" data-gl="god:${esc(p.stem_ten_god)}">${esc(p.stem_ten_god)}</span>`)}${row2('Trường sinh', esc(p.stage_vs_day_master))}</dl>
      <h5>Tàng can</h5>${hidList(p)}
      <h5>Quan hệ với các trụ khác</h5>${rl.length ? `<ul class="rel-l">${rl.map(relLi).join('')}</ul><p class="muted small">Chỉ là dữ kiện vị trí; chưa xét việc “hóa”.</p>` : '<p class="muted">Trụ này không có hợp, xung, hại, phá, hình với trụ nào khác.</p>'}`;
    return `${head(`Trụ ${PL[k]}`, `<span class="rd-glyph"><span lang="zh">${st.h}${br.h}</span>${esc(p.name)}</span>`, isDay ? 'Trụ Ngày: thiên can là Nhật Chủ' : '')}${tier('calc', calc)}${readingTiers(fFor('p:' + k))}`;
  }
  function panelElement(e) {
    const where = [];
    ORDER.forEach(k => { const p = b.pillars[k];
      if (STEMS[p.stem].e === e) where.push(`thiên can ${esc(STEMS[p.stem].n)} · trụ ${PL[k]}`);
      if (BRANCHES[p.branch].e === e) where.push(`địa chi ${esc(BRANCHES[p.branch].n)} · trụ ${PL[k]}`);
      p.hidden.filter(h => h.element === e).forEach(h => where.push(`tàng can ${esc(h.name)} · trụ ${PL[k]}`)); });
    const calc = `<dl class="rd-dl">${row2('Trên tám chữ', `<b>${counts[e]}</b> / 8`)}${row2('Là hành của Nhật Chủ', e === dmS.e ? 'Có' : 'Không')}</dl><h5>Xuất hiện ở</h5>${where.length ? `<ul class="plain">${where.map(w => `<li>${w}</li>`).join('')}</ul>` : '<p class="muted">Không xuất hiện trên tám chữ hay trong tàng can.</p>'}<p class="muted small">Quan hệ sinh khắc của hành này hiện ở sơ đồ bên cạnh.</p>`;
    return `${head('Ngũ Hành', `<span class="rd-glyph el-${EL[e].slug}"><span lang="zh">${EL[e].h}</span>${e}</span>`, `${EL[e].dir} · ${EL[e].season}`)}${tier('calc', calc)}${readingTiers(fFor('e:' + e))}`;
  }
  function panelRel(id) {
    const r = relItems[id];
    const calc = `<ul class="rel-l">${relLi(r)}</ul><p class="muted small">${r.lane === 'can' ? 'Quan hệ giữa các Thiên can.' : 'Quan hệ giữa các Địa chi.'} Việc “hợp rồi có hóa hay không” cần điều kiện mà hệ thống chưa xét, nên chỉ ghi là tiềm năng.</p>`;
    return `${head('Quan hệ Can Chi', `<span class="rd-glyph"><span lang="zh">${r.han}</span>${esc(r.title)}</span>`, esc(r.idx.map(i => 'Trụ ' + PL[ORDER[i]]).join(' – ')))}${tier('calc', calc)}${tier('src', '<p class="muted">Hệ thống không gắn luận giải đã đối chiếu sách riêng cho từng cặp hợp, xung. Các tính chất chung nằm ở chương <b>Quan hệ Can Chi & hôn nhân</b> bên dưới.</p>')}`;
  }
  const jump = (id, text) => `<p><button type="button" class="link" data-jump-ch="${id}">${text}</button></p>`;
  function panelPeriod() {
    const l = lp[S.li], st = STEMS[l.stem], br = BRANCHES[l.branch], yrs = periodYears(l.start_year_exact, lp[S.li + 1]?.start_year_exact);
    const god = terms()['god:' + l.ten_god]?.plain;
    const calc = `<dl class="rd-dl">${row2('Đại vận', `${esc(l.name)} <span lang="zh">${st.h}${br.h}</span>`)}${row2('Thập thần của can', `<span class="gl" role="button" tabindex="0" data-gl="god:${esc(l.ten_god)}">${esc(l.ten_god)}</span>`)}${row2('Hành của can', elChip(st.e))}${row2('Bắt đầu', `${Math.round(l.start_age)} tuổi · ${esc(l.start_date)}`)}${row2('Các năm', `${yrs[0]}–${yrs[yrs.length - 1]}`)}</dl>${god ? `<p class="easy-only muted small">${esc(first(god))}</p>` : ''}<div id="rd-luckrel"><p class="muted small">Đang tải quan hệ với nguyên cục…</p></div>`;
    return `${head('Đại vận', `<span class="rd-glyph el-${EL[st.e].slug}"><span lang="zh">${st.h}${br.h}</span>${esc(l.name)}</span>`, `${Math.round(l.start_age)}–${Math.round(l.start_age) + 9} tuổi`)}${tier('calc', calc)}${tier('src', `<p class="muted">Từng đại vận chỉ có dữ kiện; chưa có quy tắc đã đối chiếu sách cho từng chặng. Phân tích chung về đại vận nằm ở chương dưới.</p>${jump('dai-van', 'Mở chương Đại vận & lưu niên ↓')}`)}`;
  }
  function panelYear() {
    const l = lp[S.li], y = S.year;
    return `${head(`Lưu niên ${y}`, `<span class="rd-glyph" id="rd-ypil">…</span>`, `trong đại vận ${esc(l.name)}`)}<div id="rd-year"><p class="muted small">Đang tải…</p></div>`;
  }
  async function fillPeriod(mine) {
    const l = lp[S.li], y0 = periodYears(l.start_year_exact, lp[S.li + 1]?.start_year_exact)[0];
    try {
      const d = await yearData(ctx.req, y0); if (mine !== seq) return;
      const rel = d.bazi.luck_vs_natal, box = $('#rd-luckrel', panel); if (!box) return;
      box.innerHTML = rel.length ? `<h5>Đại vận đối với nguyên cục</h5><ul class="yx-list">${rel.map(x => `<li><b>${esc(x.from)}</b> ${esc(YEAR_REL[x.kind] || x.kind.replace(/_/g, ' '))} với ${esc(WITH[x.with] || x.with)}</li>`).join('')}</ul>` : '<p class="muted small">Đại vận này không có tương tác đáng kể với nguyên cục.</p>';
    } catch { const box = $('#rd-luckrel', panel); if (box) box.innerHTML = '<p class="muted small">Chưa tải được quan hệ của đại vận này.</p>'; }
  }
  async function fillYear(mine) {
    try {
      const d = await yearData(ctx.req, S.year); if (mine !== seq) return;
      const bz = d.bazi, inter = [...bz.annual_vs_natal, ...bz.luck_vs_natal], li = x => `<li><b>${esc(x.from)}</b> ${esc(YEAR_REL[x.kind] || x.kind.replace(/_/g, ' '))} với ${esc(WITH[x.with] || x.with)}</li>`;
      const hy = $('#rd-ypil', panel), out = $('#rd-year', panel); if (!out) return;
      const [a, c] = bz.annual_pillar.split(' ');
      hy.innerHTML = `<span lang="zh">${[STEMS.find(s => s.n === a)?.h, BRANCHES.find(s => s.n === c)?.h].filter(Boolean).join('')}</span>${esc(bz.annual_pillar)}`;
      const calc = `<dl class="rd-dl">${row2('Lưu niên', `${esc(bz.annual_pillar)} · ${esc(bz.annual_stem_ten_god)}`)}${row2('Đại vận đang hành', `${esc(bz.luck_pillar || 'chưa khởi')}${bz.luck_stem_ten_god ? ` · ${esc(bz.luck_stem_ten_god)}` : ''}`)}</dl>
        <h5>Tương tác với nguyên cục</h5>${inter.length ? `<ul class="yx-list">${inter.map(li).join('')}</ul>` : '<p class="muted small">Không có tương tác đáng kể.</p>'}
        <h5>Lưu nguyệt <span class="muted small">· tháng tính theo tiết, từ Lập Xuân</span></h5><ol class="yx-mo">${(bz.months || []).map(m => `<li><span class="mo-j">${esc(m.jie)}</span><b>${esc(m.pillar)}</b><em>${esc(m.ten_god)}</em>${m.vs_natal.length ? `<span class="mo-n" title="${esc(m.vs_natal.map(x => (YEAR_REL[x.kind] || x.kind.replace(/_/g, ' ')) + ' ' + (WITH[x.with] || x.with)).join('; '))}">${m.vs_natal.length} tương tác</span>` : '<span class="mo-n muted">—</span>'}</li>`).join('')}</ol>
        <p class="muted small">Dữ kiện cấu trúc theo thời gian, không phải dự đoán sự kiện.</p>`;
      out.innerHTML = tier('calc', calc) + tier('src', `<p class="muted">Lưu niên và lưu nguyệt chỉ có dữ kiện; chưa có quy tắc đã đối chiếu sách cho từng năm.</p>${jump('dai-van', 'Mở chương Đại vận & lưu niên ↓')}`);
      autoLink(out, 'bt');
    } catch (e) { const out = $('#rd-year', panel); if (out) out.innerHTML = `<p class="muted small">Chưa tải được dữ liệu năm này.</p>`; }
  }

  // ---- years strip under the timeline ----
  const yearsBox = $('#tm-years', host);
  let stripSeq = 0;
  async function paintYears() {
    const mine = ++stripSeq;
    if (S.kind !== 'period' && S.kind !== 'year') { yearsBox.innerHTML = ''; yearsBox.dataset.li = ''; yearsBox.classList.remove('open'); return; }
    yearsBox.dataset.li = S.li;
    const l = lp[S.li], yrs = periodYears(l.start_year_exact, lp[S.li + 1]?.start_year_exact);
    yearsBox.classList.add('open');
    yearsBox.innerHTML = `<p class="tm-ytitle">Các năm của đại vận <b>${esc(l.name)}</b> <span class="muted">· chọn một năm để xem lưu niên</span></p><ol class="yr-strip">${yrs.map(y => `<li><button type="button" class="yr${y === S.year ? ' is-sel' : ''}${y === now ? ' now' : ''}" data-y="${y}" aria-pressed="${y === S.year}"><span class="yr-n">${y}</span><span class="yr-p">…</span><span class="yr-g"></span></button></li>`).join('')}</ol>`;
    $$('.yr', yearsBox).forEach(btn => btn.onclick = () => setSel(S.kind === 'year' && S.year === +btn.dataset.y ? { kind: 'period', li: S.li } : { kind: 'year', li: S.li, year: +btn.dataset.y }));
    yrs.forEach(async y => {
      try { const d = await yearData(ctx.req, y); if (mine !== stripSeq) return; const btn = $(`.yr[data-y="${y}"]`, yearsBox); if (!btn) return;
        const [a, c] = d.bazi.annual_pillar.split(' ');
        $('.yr-p', btn).innerHTML = `<span lang="zh">${[STEMS.find(s => s.n === a)?.h, BRANCHES.find(s => s.n === c)?.h].filter(Boolean).join('')}</span> ${esc(d.bazi.annual_pillar)}`; $('.yr-g', btn).textContent = d.bazi.annual_stem_ten_god; }
      catch { /* the strip still works without the pillar names */ }
    });
  }

  // ---- selection ----
  let seq = 0;
  function setSel(next, { fromFe = false } = {}) {
    S = next; const mine = ++seq;
    if (!fromFe) { if (S.kind !== 'element' && fe) fe.clear?.(); }
    cells.forEach(c => c.classList.toggle('is-sel', S.kind === 'pillar' && ORDER[S.i] === c.dataset.pillar));
    chips.forEach(c => c.setAttribute('aria-pressed', S.kind === 'pillar' && ORDER[S.i] === c.dataset.pillar));
    $$('.tm-tab', host).forEach(t => t.setAttribute('aria-pressed', (S.kind === 'period' || S.kind === 'year') && +t.dataset.i === S.li));
    paintArcs();
    panel.closest('.dash-side')?.scrollTo(0, 0);
    panel.innerHTML = `<div class="rd-in">${S.kind === 'pillar' ? panelPillar(S.i) : S.kind === 'element' ? panelElement(S.el) : S.kind === 'rel' ? panelRel(S.id) : S.kind === 'period' ? panelPeriod() : S.kind === 'year' ? panelYear() : panelDefault()}</div>`;
    panel.dataset.kind = S.kind || 'idle';
    $('.rd-x', panel)?.addEventListener('click', () => { if (S.kind === 'element') fe.clear(); else setSel({ kind: null }); });
    $$('[data-jump-ch]', panel).forEach(bt => bt.onclick = () => document.getElementById('bt-' + bt.dataset.jumpCh)?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
    autoLink(panel, 'bt');
    if (S.kind === 'period') fillPeriod(mine); if (S.kind === 'year') fillYear(mine);
    if (S.kind === 'period' || S.kind === 'year') { if (yearsBox.dataset.li !== String(S.li)) paintYears(); else paintYearSel(); } else paintYears();
    if (S.kind && matchMedia('(max-width:999px)').matches) { const r = panel.getBoundingClientRect(); if (r.top > innerHeight * .8 || r.bottom < 0) panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
  }
  function paintYearSel() { $$('.yr', yearsBox).forEach(b => { const on = S.kind === 'year' && +b.dataset.y === S.year; b.classList.toggle('is-sel', on); b.setAttribute('aria-pressed', on); }); }

  cols.forEach(c => { c.addEventListener('click', e => { if (e.target.closest('button')) return; const i = ORDER.indexOf(c.dataset.pillar); setSel(S.kind === 'pillar' && S.i === i ? { kind: null } : { kind: 'pillar', i }); }); });
  chips.forEach(c => c.addEventListener('click', () => { const i = ORDER.indexOf(c.dataset.pillar); setSel(S.kind === 'pillar' && S.i === i ? { kind: null } : { kind: 'pillar', i }); }));
  $$('.tm-tab', host).forEach(t => t.addEventListener('click', () => { const i = +t.dataset.i; if (S.li === i && (S.kind === 'period' || S.kind === 'year')) setSel({ kind: null }); else setSel({ kind: 'period', li: i }); centerIn($('#tm-scroll', host), t); }));
  $$('.dl-mk', host).forEach(g => g.addEventListener('click', () => setSel({ kind: 'pillar', i: ORDER.indexOf(g.dataset.pillar) })));
  drawArcs(); setSel({ kind: null });
  requestAnimationFrame(() => { const t = $('.tm-tab.now', host); if (t) centerIn($('#tm-scroll', host), t); });

  return { counts, select: setSel, parts: { luck: tl, nguyetLenh, thapThan, tangCan, thongCan, relations: relBody, relCount: rels.reduce((n, [, v]) => n + v.length, 0) } };
}
