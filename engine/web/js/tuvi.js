// TuViChartGrid + TuViPalace + ChartIdentityPanel + palace detail drawer.
import { $, $$, esc, starKind, TU_HOA_SHORT, claimLabel, BRANCHES, STEMS, palaceOfSubject } from './util.js';
import { compass } from './compass.js';
import { acc, notice, timeline, reasoningPanel, findingCard } from './ui.js';
import { scopeText, scopePanelTuvi } from './scope.js';

// Traditional layout: branch index per grid cell (null = centre block). Tỵ top-left, clockwise.
const CELLS = [5, 6, 7, 8, 4, null, null, 9, 3, null, null, 10, 2, 1, 0, 11];

export function renderTuvi(host, t, ctx) {
  const by = Object.fromEntries(t.palaces.map(p => [p.branch_index, p]));
  const byBranch = Object.fromEntries(t.palaces.map(p => [p.branch, p]));
  const byName = Object.fromEntries(t.palaces.map(p => [p.name, p]));
  const dh = Object.fromEntries(t.dai_han.map(d => [d.branch, d]));
  const th = {}; Object.entries(t.tu_hoa).forEach(([k, v]) => { th[v.star] = k; });
  const unv = new Set(t.stars.filter(x => /chưa đối chiếu/.test(x.group)).map(x => x.name));
  const than = t.palaces.find(p => p.is_than), menh = t.palaces.find(p => p.name === 'Mệnh');
  const findings = (ctx.reason?.systems?.tu_vi?.findings || []);
  const fOf = name => findings.filter(f => palaceOfSubject(f.subject) === name);
  const DG = { 'miếu': 'Miếu', 'vượng': 'Vượng', 'đắc': 'Đắc', 'bình': 'Bình', 'hãm': 'Hãm' };
  const starHtml = (s, major, dg) => { const k = starKind(s), h = th[s]; return `<span class="st st-${k}${major ? ' major' : ''}${unv.has(s) ? ' unv' : ''}"${unv.has(s) ? ' title="Sao an theo công thức phổ biến, chưa đối chiếu sách"' : ''}>${esc(s)}${dg ? `<sup class="dg dg-${dg}" title="Độ sáng: ${esc(dg)}">${DG[dg] || esc(dg)}</sup>` : ''}${h ? `<sup class="th th-${h === 'Hóa Kỵ' ? 'ky' : 'ok'}" title="${esc(h)}">${TU_HOA_SHORT[h]}</sup>` : ''}</span>`; };

  const cell = i => {
    const p = by[i], minors = p.stars.filter(s => !p.major_stars.includes(s));
    const order = { pos: 0, neu: 1, neg: 2 }; minors.sort((a, b) => order[starKind(a)] - order[starKind(b)]);
    const d = dh[p.branch];
    return `<button type="button" class="pal" data-i="${i}" aria-pressed="false" aria-label="Cung ${esc(p.name)}, ${esc(p.stem)} ${esc(p.branch)}. Chính tinh: ${esc(p.major_stars.join(', ') || 'vô chính diệu')}">
      <span class="pal-h"><span class="pal-name">${esc(p.name)}</span><span class="pal-gz"><i lang="zh">${BRANCHES[i].h}</i>${esc(p.stem)} ${esc(p.branch)}</span></span>
      ${p.is_than || p.tuan || p.triet ? `<span class="pal-tags">${p.is_than ? '<span class="tag tag-than">Thân</span>' : ''}${p.tuan ? '<span class="tag">Tuần</span>' : ''}${p.triet ? '<span class="tag">Triệt</span>' : ''}</span>` : ''}
      <span class="pal-maj">${p.major_stars.length ? p.major_stars.map(s => starHtml(s, true, p.major_dignity?.[s])).join('') : '<span class="vcd">vô chính diệu</span>'}</span>
      <span class="pal-min">${minors.map(s => starHtml(s, false)).join('')}</span>
      ${d ? `<span class="pal-dh" title="Đại hạn">${d.age_from}<small>–${d.age_to}</small></span>` : ''}
    </button>`;
  };

  const center = `<div class="ident" aria-labelledby="id-t">
      <div class="ident-art" aria-hidden="true">${compass({ animate: false, detail: 'min' })}</div>
      <div class="ident-in">
        <p class="eyebrow">Lá số Tử Vi Đẩu Số</p>
        <h3 id="id-t" class="ident-gz">${esc(t.year_gz)}</h3>
        <p class="ident-line">${esc(t.yin_yang_gender)} · Âm lịch ${t.lunar.day}/${t.lunar.month}/${t.lunar.year}${t.lunar.leap ? ' nhuận' : ''}</p>
        <dl class="ident-dl">
          <div><dt>Mệnh cung</dt><dd>${esc(menh.stem)} ${esc(menh.branch)}</dd></div>
          <div><dt>Thân cư</dt><dd>${esc(than.name)}</dd></div>
          <div><dt>Cục</dt><dd>${esc(t.cuc.name)}</dd></div>
          <div><dt>Bản mệnh</dt><dd>${esc(t.menh_nap_am)}</dd></div>
          ${t.extras?.menh_chu ? `<div><dt>Mệnh chủ</dt><dd>${esc(t.extras.menh_chu.star)}</dd></div><div><dt>Thân chủ</dt><dd>${esc(t.extras.than_chu.star)}</dd></div>` : ''}
        </dl>
        <p class="ident-sum">${esc(t.menh_cuc_relation)} · đại hạn ${esc(t.dai_han_direction)}${menh.major_stars.length ? ` · Mệnh có ${esc(menh.major_stars.join(', '))}` : ' · Mệnh vô chính diệu'}</p>
        <button type="button" class="link" data-scope>Phạm vi tính toán</button>
      </div></div>`;

  host.innerHTML = scopePanelTuvi(t) + `
    <div class="tv-layout">
      <div class="tv-main">
        <div class="seg tv-toggle" role="group" aria-label="Chế độ xem lá số"><button type="button" data-v="ov" aria-pressed="true">Tổng quan</button><button type="button" data-v="full" aria-pressed="false">Toàn lá số</button></div>
        <ol class="tv-ov" aria-label="Tổng quan mười hai cung">${t.palaces.slice().sort((a, b) => (a.branch_index - menh.branch_index + 12) % 12 - (b.branch_index - menh.branch_index + 12) % 12).map(p => `<li><button type="button" data-i="${p.branch_index}"><span class="ov-n">${esc(p.name)}</span><span class="ov-gz">${esc(p.stem)} ${esc(p.branch)}</span><span class="ov-s">${esc(p.major_stars.join(' · ') || 'vô chính diệu')}</span></button></li>`).join('')}</ol>
        <div class="tv-scroll" tabindex="0" role="region" aria-label="Lá số Tử Vi, có thể cuộn ngang"><div class="tv-board" id="tv-board">
          <svg class="tv-links" aria-hidden="true"></svg>
          <div id="grid">${CELLS.map((i, k) => i === null ? (k === 5 ? `<div class="center">${center}</div>` : '') : cell(i)).join('')}</div></div></div>
        <div class="legend"><span><i class="st-neu major">Aa</i>Chính tinh</span><span class="l-pos">Cát tinh</span><span class="l-neg">Sát / hung tinh</span><span class="l-neu">Phụ tinh</span><span><sup class="th th-ok">Lộc</sup>Tứ Hóa</span><span><sup class="dg dg-vượng">Vượng</sup>Độ sáng</span><span><b class="legend-dh">6–15</b>Đại hạn</span></div>
        <p class="muted small tv-school">Trường phái: ${esc(t.school.schoolId)} · bộ quy tắc ở trạng thái <b>${t.school.review_status === 'partially_verified' ? 'đã xác minh một phần' : esc(t.school.review_status)}</b>.</p>
      </div>
      <aside class="drawer" id="tv-drawer" aria-label="Chi tiết cung" aria-live="polite"></aside>
    </div>
    <dialog id="scope-dlg" class="dlg"><form method="dialog"><h3>Phạm vi tính toán hiện tại</h3><p class="muted">Những phần dưới đây chưa được tính hoặc chưa hiển thị để bảo đảm lá số không chứa dữ kiện thiếu căn cứ.</p><ul>${t.unsupported.map(u => `<li>${esc(scopeText(u))}</li>`).join('')}</ul>${t.warnings.length ? `<h4>Cảnh báo</h4><ul>${t.warnings.map(w => `<li>${esc(w)}</li>`).join('')}</ul>` : ''}<button class="btn btn-ghost">Đã hiểu</button></form></dialog>`;

  const board = $('#tv-board', host), svg = $('.tv-links', host), drawer = $('#tv-drawer', host);
  let cur = null;

  const emptyDrawer = () => `<div class="drawer-empty"><div class="ident-art sm" aria-hidden="true">${compass({ animate: false, detail: 'min' })}</div><h3>Chọn một cung</h3><p class="muted">Nhấn vào một cung để xem sao, tam phương tứ chính và các nhận định liên quan. Các đường nối sẽ cho thấy quan hệ giữa các cung.</p></div>`;
  drawer.innerHTML = emptyDrawer();

  function links(i) {
    svg.innerHTML = '';
    if (i == null) return;
    const s = t.structure[by[i].branch];
    const rect = board.getBoundingClientRect();
    const c = b => { const el = $(`.pal[data-i="${BRANCHES.findIndex(x => x.n === b)}"]`, host), r = el.getBoundingClientRect(); return [r.left - rect.left + r.width / 2, r.top - rect.top + 20]; };
    svg.setAttribute('viewBox', `0 0 ${rect.width} ${rect.height}`);
    const me = c(by[i].branch), op = c(s.opposite), t1 = c(s.tam_hop[0]), t2 = c(s.tam_hop[1]);
    const ln = (a, b, cls) => `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" class="${cls}"/>`;
    svg.innerHTML = ln(t1, t2, 'lk lk-tri') + ln(me, op, 'lk lk-op') + ln(me, t1, 'lk lk-th') + ln(me, t2, 'lk lk-th') +
      [me, op, t1, t2].map((p, k) => `<circle cx="${p[0]}" cy="${p[1]}" r="${k === 0 ? 5 : 3.5}" class="lk-dot${k === 0 ? ' me' : ''}"/>`).join('');
  }

  function detail(i) {
    const p = by[i], s = t.structure[p.branch], d = dh[p.branch], fs = fOf(p.name);
    const minors = p.stars.filter(x => !p.major_stars.includes(x));
    const grp = k => minors.filter(x => starKind(x) === k);
    const rel = (label, branch) => { const q = byBranch[branch]; return `<button type="button" class="relp" data-i="${q.branch_index}"><span class="k">${label}</span><b>${esc(q.name)}</b><span class="muted">${esc(q.branch)} · ${esc(q.major_stars.join(', ') || 'vô chính diệu')}</span></button>`; };
    const ths = Object.entries(t.tu_hoa).filter(([, v]) => v.branch === p.branch_index || v.branch === i).map(([k, v]) => `<span class="chip">${esc(k)} · ${esc(v.star)}</span>`).join('');
    drawer.innerHTML = `<div class="dr-in">
      <button class="dr-x" type="button" aria-label="Đóng chi tiết cung">×</button>
      <p class="eyebrow">Cung ${esc(p.stem)} ${esc(p.branch)}${p.is_than ? ' · Thân cư' : ''}</p>
      <h3 class="dr-t">${esc(p.name)}</h3>
      <div class="dr-tags">${p.tuan ? '<span class="tag">Tuần</span>' : ''}${p.triet ? '<span class="tag">Triệt</span>' : ''}${d ? `<span class="tag tag-dh">Đại hạn ${d.age_from}–${d.age_to} tuổi</span>` : ''}</div>
      <section><h4>Chính tinh</h4><div class="dr-stars">${p.major_stars.length ? p.major_stars.map(x => starHtml(x, true, p.major_dignity?.[x])).join('') : '<span class="vcd">Vô chính diệu — cung không có chính tinh.</span>'}</div></section>
      <section><h4>Phụ tinh</h4>
        ${[['pos', 'Cát tinh'], ['neu', 'Trung tính'], ['neg', 'Sát / hung tinh']].map(([k, l]) => grp(k).length ? `<div class="dr-grp"><span class="k">${l}</span><div class="dr-stars sm">${grp(k).map(x => starHtml(x, false)).join('')}</div></div>` : '').join('') || '<p class="muted">Không có.</p>'}
        ${ths ? `<div class="dr-grp"><span class="k">Tứ Hóa tại cung</span><div class="chips">${ths}</div></div>` : ''}</section>
      <section><h4>Tam phương tứ chính</h4><div class="relps">${rel('Xung chiếu', s.opposite)}${rel('Tam hợp', s.tam_hop[0])}${rel('Tam hợp', s.tam_hop[1])}</div>
        <p class="muted small">Cung giáp: ${s.giap.map(b => `${esc(byBranch[b].name)} (${esc(b)})`).join(' · ')}</p></section>
      <section><h4>Nhận định liên quan</h4>${fs.length ? fs.map(f => findingCard(f)).join('') + '<p class="muted small">Diễn giải theo hệ biểu tượng truyền thống, không phải dự báo.</p>' : '<p class="muted">Chưa có quy tắc nào được kích hoạt cho cung này. Điều đó không có nghĩa cung “không có gì”, chỉ là bộ quy tắc hiện hành chưa phủ tới.</p>'}</section>
    </div>`;
    $('.dr-x', drawer).onclick = () => select(null);
    $$('.relp', drawer).forEach(b => b.onclick = () => select(+b.dataset.i));
  }

  function select(i, { scroll = true } = {}) {
    cur = i === cur ? cur : i;
    if (i == null) cur = null;
    const rel = cur == null ? [] : (() => { const s = t.structure[by[cur].branch]; return [s.opposite, ...s.tam_hop].map(b => byBranch[b].branch_index); })();
    $$('.pal', host).forEach(e => { const n = +e.dataset.i; e.classList.toggle('hl', n === cur); e.classList.toggle('rel', rel.includes(n)); e.setAttribute('aria-pressed', n === cur); });
    $$('.tv-ov button', host).forEach(e => e.classList.toggle('hl', +e.dataset.i === cur));
    host.classList.toggle('has-sel', cur != null);
    if (cur == null) { drawer.classList.remove('open'); drawer.innerHTML = emptyDrawer(); document.body.classList.remove('sheet-open'); links(null); return; }
    detail(cur); drawer.classList.add('open'); drawer.scrollTop = 0;
    document.body.classList.toggle('sheet-open', matchMedia('(max-width:1179px)').matches);
    requestAnimationFrame(() => links(cur));
  }
  $$('.pal', host).forEach(e => e.onclick = () => select(+e.dataset.i === cur ? null : +e.dataset.i));
  $$('.tv-ov button', host).forEach(e => e.onclick = () => select(+e.dataset.i));
  $$('.tv-toggle button', host).forEach(b => b.onclick = () => { host.dataset.view = b.dataset.v; $$('.tv-toggle button', host).forEach(x => x.setAttribute('aria-pressed', x === b)); requestAnimationFrame(() => links(cur)); });
  host.dataset.view = 'ov';
  $('[data-scope]', host).onclick = () => $('#scope-dlg', host).showModal();
  addEventListener('resize', () => links(cur));
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && cur != null && !document.querySelector('dialog[open]')) select(null); });

  // Đại hạn timeline for the report
  const timelineHtml = timeline(t.dai_han.map(d => ({ title: `<span class="tl-han">${esc(d.palace)}</span>`, sub: `${esc(d.stem)} ${esc(d.branch)}`, meta: `${d.age_from}–${d.age_to} tuổi`, current: false })), { label: 'Đại hạn Tử Vi' });
  return { select: name => { const p = byName[name]; if (p) { select(p.branch_index); $('#tv-board', host).scrollIntoView({ behavior: 'smooth', block: 'center' }); } }, byName, menh, than, timelineHtml };
}
