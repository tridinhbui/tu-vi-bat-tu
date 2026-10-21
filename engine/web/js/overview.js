// "Tổng quan lá số" (docs/PRODUCT-PLAN.md 1.5): the reasoner's frame and theses for Mệnh and four charts of SYSTEM INDICES from
// POST /api/overview (src/interpret/overview.ts, indices.ts). Plain SVG, drawn at the host's real width (re-drawn on resize) so text keeps its
// size on phones. Every chart says in words that an index is a weighted count of book rules, not a probability; clicking a mark lists the
// rules behind it. No calculation lives here: the numbers come from the server as they are.
import { esc } from './util.js';

const SIDE = { support: 'Mức thuận lợi', limit: 'Mức thử thách' };
const LAYER = { ban_menh: 'Bản mệnh (cung và tam phương)', van: 'Câu sách về cung vận', luu_thai_tue: 'Lưu Thái Tuế', luu_tu_hoa: 'Lưu Tứ Hóa (thông lệ)' };
const BASIS = { sach: 'sách', sach_dien_giai: 'sách, diễn ý', thong_le: 'thông lệ' };
const SCOPE = { self: 'chính cung', opp: 'xung chiếu', trine: 'tam hợp' };
const VERDICT = { affirmed: '', qualified: 'có giới hạn', contested: 'hai chiều' };
const CHAPTERS = [['ban-menh', 'Bản Mệnh'], ['tinh-cach', 'Tính cách'], ['cong-danh', 'Công danh'], ['tai-bach', 'Tài Bạch'], ['quan-he', 'Quan hệ'],
  ['dai-han', 'Đại hạn & lưu niên'], ['cach-cuc', 'Cách cục'], ['muoi-hai-cung', 'Mười hai cung']];
const NS = 'http://www.w3.org/2000/svg';
const fmt = x => (Math.round(x * 100) / 100).toLocaleString('vi-VN', { maximumFractionDigits: 2 });
const niceMax = v => { const s = [0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 15, 20]; return s.find(x => x >= v) ?? Math.ceil(v); };

export function overviewHtml(o) {
  return `<div class="ov">
    <p class="ov-disc" role="note"><b>Chỉ số tổng hợp từ quy tắc sách, không phải xác suất hay dự báo.</b> Mỗi cột, mỗi điểm là tổng có trọng số của các câu sách đã đối chiếu bắn vào một cung; bấm vào để xem từng quy tắc và trang sách.</p>
    ${frameHtml(o)}
    <div class="ov-grid">
      ${card('dv', 'Xu hướng đại vận', 'Mười chặng đại vận. Mỗi chặng: chỉ số bản mệnh của cung đại vận (so với mức thường gặp) cộng các câu sách về cung vận.')}
      ${card('tv', 'Tiểu vận từng năm', `Mười năm trước và sau năm ${o.indices.year}: cung tiểu hạn, nửa trọng số cung lưu Thái Tuế, và lưu Tứ Hóa (thông lệ, trọng số thấp).`)}
      ${card('rd', 'Mười hai cung', 'Mỗi cung cùng tam phương của nó, so với mức trung bình của chính cung đó trên 1.000 lá số mẫu. Vòng tròn đậm là mức thường gặp (1).')}
      ${o.indices.months ? card('nv', `Nguyệt vận năm ${o.indices.months.year}`, 'Cung của từng tháng theo nguyệt hạn (Thực Hành tr.115); mức của tháng là chỉ số bản mệnh của cung đó. Không có “nhật vận”.') : ''}
    </div>
    <details class="ov-method"><summary>Cách tính chỉ số</summary><ul>${Object.entries(o.indices.method).map(([k, v]) => `<li><b>${esc(LAYER[k] || (k === 'nguyet' ? 'Nguyệt vận' : k))}:</b> ${esc(v)}.</li>`).join('')}
      ${o.indices.norms ? `<li>Mức thường gặp: ${o.indices.norms.charts} lá số mẫu (${esc(o.indices.norms.corpus)}, bộ mẫu phân tầng, không phải dân số thật).</li>` : ''}
      <li>Phiên bản ${esc(o.indices.version)}, tri thức ${esc(o.kbVersion)}. Cùng ngày giờ sinh luôn cho cùng con số.</li></ul></details>
    <nav class="ov-ch" aria-label="Đọc từng chương"><p class="eyebrow">Đọc tiếp từng chương</p>${CHAPTERS.map(([id, t]) => `<button type="button" class="ov-chip" data-ov-ch="${id}">${t}</button>`).join('')}</nav>
  </div>`;
}

function card(id, title, sub) {
  return `<section class="ov-card" data-chart="${id}" aria-labelledby="ov-${id}-h"><header><h3 id="ov-${id}-h">${title}</h3><p>${sub}</p></header>
    ${legend(id)}<div class="ov-plot" data-plot="${id}"></div>
    <p class="ov-cap">Chỉ số tổng hợp từ quy tắc sách, không phải xác suất hay dự báo.</p>
    <div class="ov-why" data-why="${id}" aria-live="polite"><p class="ov-hint">Bấm vào ${id === 'rd' ? 'tên một cung' : id === 'tv' ? 'một năm' : 'một cột'} để xem các quy tắc phía sau.</p></div>
    <details class="ov-tbl"><summary>Xem bảng số</summary><div data-table="${id}"></div></details></section>`;
}
const legend = id => `<p class="ov-leg"><span><i class="sw sw-s${id === 'tv' || id === 'rd' ? ' sw-line' : ''}"></i>${SIDE.support}</span><span><i class="sw sw-l${id === 'tv' || id === 'rd' ? ' sw-line sw-dash' : ''}"></i>${SIDE.limit}</span></p>`;

function frameHtml(o) {
  const f = o.frame;
  if (!f) return '';
  const majors = f.vcd ? `Vô chính diệu${f.borrowed.length ? `, mượn ${esc(f.borrowed.join(', '))} của cung xung chiếu` : ''}`
    : f.majors.map(m => `${esc(m.star)}${m.dignity ? ` <small>(${esc(m.dignity)})</small>` : ''}${m.hoa.length ? ` <small>hóa ${esc(m.hoa.map(h => h.replace('Hóa ', '')).join(', '))}</small>` : ''}`).join(', ');
  const marks = [f.than && 'Thân cư Mệnh', f.tuan && 'Tuần', f.triet && 'Triệt'].filter(Boolean).join(' · ');
  const theses = o.theses.map((t, i) => `<li class="ov-th"><p class="ov-th-h"><span class="ov-no">${i + 1}</span>${esc(t.label)}</p>
    <ul>${t.claims.map(c => `<li>${esc(cap(c.text))}${VERDICT[c.verdict] ? ` <span class="ov-tag">${VERDICT[c.verdict]}</span>` : ''}</li>`).join('')}</ul>
    <details><summary>Căn cứ</summary><ul class="ov-rules">${[...new Map(t.claims.flatMap(c => c.rules).map(r => [r.id, r])).values()]
      .map(r => `<li><code>${esc(r.id)}</code> ${esc(r.cite)}${r.role !== 'base' ? ` <span class="ov-tag">${r.role === 'reducer' ? 'giảm nhẹ' : 'chiều ngược'}</span>` : ''}</li>`).join('')}
      ${t.formations.map(x => `<li>${esc(x.name)} · ${esc(x.cites.join('; '))}</li>`).join('')}</ul></details></li>`).join('');
  return `<section class="ov-frame" aria-labelledby="ov-fr-h"><div class="ov-fr-main"><p class="eyebrow">Khung lá số</p>
    <h3 id="ov-fr-h">Mệnh ở ${esc(f.branch)}: ${majors}</h3>
    ${marks ? `<p class="ov-marks">${marks}</p>` : ''}
    <p class="ov-centre">Trọng tâm khi đọc: <b>${esc(f.centre)}</b></p>
    ${f.formations.length ? `<p class="ov-forms">Cách cục theo sách: ${f.formations.map(x => `<span class="ov-form">${esc(x.name)} <small>${esc(x.cites.join('; '))}</small></span>`).join(' ')}</p>` : ''}</div>
    ${theses ? `<div class="ov-fr-th"><p class="eyebrow">Luận điểm chính về Mệnh</p><ol class="ov-ths">${theses}</ol>
      <p class="ov-note">Do bộ suy luận chọn theo tầng và độ hiếm của quy tắc; chỉ dùng quy tắc đã đối chiếu sách.</p></div>` : ''}</section>`;
}
const cap = s => s ? s[0].toUpperCase() + s.slice(1) : s;

// ---------- the "why" panel ----------
function whyHtml(title, s) {
  const items = side => s.items.filter(i => i.side === side).sort((a, b) => b.w - a.w);
  const list = side => { const xs = items(side); return xs.length ? `<ul>${xs.map(i => `<li><p>${esc(i.text)}</p><p class="ov-src"><code>${esc(i.id)}</code> · ${esc(i.cite)} · ${LAYER[i.layer]}${i.layer === 'ban_menh' ? `, ${esc(i.palace)} (${SCOPE[i.scope]})` : ''} · <span class="ov-tag ov-b-${i.basis}">${BASIS[i.basis]}</span> · trọng số ${fmt(i.w)}</p></li>`).join('')}</ul>` : '<p class="ov-none">Không có quy tắc nào.</p>'; };
  return `<h4>${title}</h4><p class="ov-vals"><span class="v-s">${SIDE.support}: <b>${fmt(s.support)}</b></span><span class="v-l">${SIDE.limit}: <b>${fmt(s.limit)}</b></span></p>
    <ul class="ov-parts">${s.parts.map(p => `<li><b>${LAYER[p.layer]}</b>: +${fmt(p.support)} / +${fmt(p.limit)} <small>(${esc(p.note)})</small></li>`).join('')}</ul>
    <div class="ov-sides"><div><h5>Phía thuận lợi</h5>${list('support')}</div><div><h5>Phía thử thách</h5>${list('limit')}</div></div>
    <p class="ov-cap">Chỉ số tổng hợp từ quy tắc sách, không phải xác suất hay dự báo.</p>`;
}

// ---------- SVG helpers ----------
const el = (tag, attrs = {}, kids = []) => { const e = document.createElementNS(NS, tag); for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v); kids.forEach(k => e.append(k)); return e; };
const txt = (x, y, s, attrs = {}) => { const t = el('text', { x, y, ...attrs }); t.textContent = s; return t; };
const colPath = (x, y0, w, h) => { const r = Math.min(4, w / 2, h); return h <= 0 ? '' : `M${x} ${y0}V${y0 - h + r}Q${x} ${y0 - h} ${x + r} ${y0 - h}H${x + w - r}Q${x + w} ${y0 - h} ${x + w} ${y0 - h + r}V${y0}Z`; };
function svgFor(w, h, label) { return el('svg', { width: w, height: h, viewBox: `0 0 ${w} ${h}`, role: 'img', 'aria-label': label, class: 'ov-svg' }); }
function yAxis(svg, x0, x1, y0, plotH, max) {
  for (let i = 0; i <= 4; i++) {
    const v = max * i / 4, y = y0 - plotH * i / 4;
    svg.append(el('line', { x1: x0, x2: x1, y1: y, y2: y, class: i ? 'ov-grid' : 'ov-base' }), txt(x0 - 6, y + 4, fmt(v), { class: 'ov-tick', 'text-anchor': 'end' }));
  }
}

/** Grouped columns (two per group): đại vận and nguyệt vận. */
function columns(host, groups, { label, sub, title, current, onPick, xCaption }) {
  const W = Math.max(300, host.clientWidth), small = W < 560, H = small ? 250 : 280;
  const m = { l: 34, r: 8, t: 18, b: small ? 46 : 42 }, pw = W - m.l - m.r, ph = H - m.t - m.b, y0 = m.t + ph;
  const max = niceMax(Math.max(1, ...groups.flatMap(g => [g.support, g.limit])));
  const svg = svgFor(W, H, label);
  yAxis(svg, m.l, W - m.r, y0, ph, max);
  const band = pw / groups.length, bw = Math.min(24, (band - 10) / 2);
  groups.forEach((g, i) => {
    const gx = m.l + band * i, cx = gx + band / 2;
    const grp = el('g', { class: `ov-grp${current?.(g) ? ' is-cur' : ''}`, tabindex: 0, role: 'button', 'aria-label': `${title(g)}: ${SIDE.support} ${fmt(g.support)}, ${SIDE.limit} ${fmt(g.limit)}` });
    if (current?.(g)) grp.append(el('rect', { x: gx + 1, y: m.t - 14, width: band - 2, height: ph + 14, class: 'ov-curband', rx: 6 }), txt(cx, m.t - 3, small ? 'Nay' : 'Hiện tại', { class: 'ov-curlbl', 'text-anchor': 'middle' }));
    grp.append(el('rect', { x: gx, y: m.t, width: band, height: ph + m.b, class: 'ov-hit' }));
    grp.append(el('path', { d: colPath(cx - bw - 1, y0, bw, ph * g.support / max), class: 'ov-col-s' }));
    grp.append(el('path', { d: colPath(cx + 1, y0, bw, ph * g.limit / max), class: 'ov-col-l' }));
    const [l1, l2] = sub(g, small);
    grp.append(txt(cx, y0 + 16, l1, { class: 'ov-xl', 'text-anchor': 'middle' }));
    if (l2) grp.append(txt(cx, y0 + 30, l2, { class: 'ov-xl2', 'text-anchor': 'middle' }));
    grp.addEventListener('click', () => onPick(g, grp));
    grp.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onPick(g, grp); } });
    tip(grp, () => `<b>${esc(title(g))}</b><br>${SIDE.support}: ${fmt(g.support)}<br>${SIDE.limit}: ${fmt(g.limit)}`);
    svg.append(grp);
  });
  if (small && xCaption) svg.append(txt(m.l + pw / 2, H - 6, xCaption, { class: 'ov-xl2', 'text-anchor': 'middle' }));
  host.replaceChildren(svg);
}

/** Two lines over the years, with the "Năm nay" marker: tiểu vận. */
function lines(host, ys, { onPick }) {
  const W = Math.max(300, host.clientWidth), small = W < 560, H = small ? 240 : 270;
  const m = { l: 34, r: 12, t: 22, b: 40 }, pw = W - m.l - m.r, ph = H - m.t - m.b, y0 = m.t + ph;
  const max = niceMax(Math.max(1, ...ys.flatMap(g => [g.support, g.limit])));
  const svg = svgFor(W, H, 'Tiểu vận từng năm: mức thuận lợi và mức thử thách');
  yAxis(svg, m.l, W - m.r, y0, ph, max);
  const step = pw / Math.max(1, ys.length - 1), X = i => m.l + step * i, Y = v => y0 - ph * v / max;
  const cur = ys.findIndex(y => y.current);
  if (cur >= 0) svg.append(el('line', { x1: X(cur), x2: X(cur), y1: m.t - 6, y2: y0, class: 'ov-now' }), txt(X(cur), m.t - 10, 'Năm nay', { class: 'ov-curlbl', 'text-anchor': cur > ys.length - 3 ? 'end' : 'middle' }));
  for (const [side, cls] of [['support', 'ov-ln-s'], ['limit', 'ov-ln-l']]) {
    svg.append(el('path', { d: ys.map((y, i) => `${i ? 'L' : 'M'}${X(i).toFixed(1)} ${Y(y[side]).toFixed(1)}`).join(''), class: cls }));
  }
  const every = small ? 5 : 2;
  ys.forEach((y, i) => {
    const g = el('g', { class: 'ov-grp ov-pt', tabindex: 0, role: 'button', 'aria-label': `Năm ${y.year}, cung ${y.palace}: ${SIDE.support} ${fmt(y.support)}, ${SIDE.limit} ${fmt(y.limit)}` });
    g.append(el('rect', { x: X(i) - step / 2, y: m.t, width: step, height: ph + m.b, class: 'ov-hit' }));
    g.append(el('circle', { cx: X(i), cy: Y(y.support), r: i === cur ? 5 : 4, class: 'ov-dot-s' }), el('circle', { cx: X(i), cy: Y(y.limit), r: i === cur ? 5 : 4, class: 'ov-dot-l' }));
    if (i % every === 0 || i === cur) g.append(txt(X(i), y0 + 16, String(y.year), { class: `ov-xl${i === cur ? ' is-cur' : ''}`, 'text-anchor': 'middle' }));
    g.addEventListener('click', () => onPick(y, g));
    g.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onPick(y, g); } });
    tip(g, () => `<b>${y.year} (${esc(y.can_chi)}), ${y.age} tuổi</b><br>Tiểu hạn: ${esc(y.palace)} · Thái Tuế: ${esc(y.thai_tue)}<br>${SIDE.support}: ${fmt(y.support)}<br>${SIDE.limit}: ${fmt(y.limit)}`);
    svg.append(g);
  });
  host.replaceChildren(svg);
}

/** Radar of the twelve palaces (support and limit polygons) with the ring at 1 = the corpus' typical chart. */
function radar(host, ps, { onPick }) {
  const W = Math.max(300, host.clientWidth), S = Math.min(W, 460), small = S < 400;
  const cx = W / 2, cy = S / 2, R = S / 2 - (small ? 66 : 62);   // room for the longest side label ("Điền Trạch")
  const max = niceMax(Math.max(1.5, ...ps.flatMap(p => [p.support, p.limit])));
  const svg = svgFor(W, S, 'Mười hai cung: mức thuận lợi và mức thử thách so với mức thường gặp');
  const ang = i => -Math.PI / 2 + 2 * Math.PI * i / ps.length, pt = (i, v) => [cx + Math.cos(ang(i)) * R * v / max, cy + Math.sin(ang(i)) * R * v / max];
  for (let k = 1; k <= 4; k++) svg.append(el('circle', { cx, cy, r: R * k / 4, class: 'ov-grid ov-ring' }));
  const ta = -Math.PI / 2 + Math.PI / 12, tr = R / max;   // the label sits between the Mệnh and Phụ Mẫu axes, just outside the ring
  svg.append(el('circle', { cx, cy, r: tr, class: 'ov-typ' }), txt(cx + Math.cos(ta) * (tr + 4), cy + Math.sin(ta) * (tr + 4), 'mức thường gặp', { class: 'ov-tick ov-typl' }));
  ps.forEach((_, i) => { const [x, y] = pt(i, max); svg.append(el('line', { x1: cx, y1: cy, x2: x, y2: y, class: 'ov-grid' })); });
  for (const [side, cls] of [['support', 'ov-poly-s'], ['limit', 'ov-poly-l']]) svg.append(el('polygon', { points: ps.map((p, i) => pt(i, p[side]).map(n => n.toFixed(1)).join(',')).join(' '), class: cls }));
  ps.forEach((p, i) => {
    const [lx, ly] = pt(i, max * (1 + (small ? 0.2 : 0.17))), a = Math.cos(ang(i));
    const g = el('g', { class: 'ov-grp', tabindex: 0, role: 'button', 'aria-label': `Cung ${p.palace}: ${SIDE.support} ${fmt(p.support)}, ${SIDE.limit} ${fmt(p.limit)}` });
    for (const side of ['support', 'limit']) { const [x, y] = pt(i, p[side]); g.append(el('circle', { cx: x, cy: y, r: 4, class: side === 'support' ? 'ov-dot-s' : 'ov-dot-l' })); }
    g.append(el('rect', { x: lx - 40, y: ly - 14, width: 80, height: 22, class: 'ov-hit' }));
    g.append(txt(lx, ly + 4, p.palace, { class: 'ov-axl', 'text-anchor': Math.abs(a) < 0.3 ? 'middle' : a > 0 ? 'start' : 'end' }));
    g.addEventListener('click', () => onPick(p, g));
    g.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onPick(p, g); } });
    tip(g, () => `<b>Cung ${esc(p.palace)} (${esc(p.branch)})</b><br>${SIDE.support}: ${fmt(p.support)}<br>${SIDE.limit}: ${fmt(p.limit)}`);
    svg.append(g);
  });
  host.replaceChildren(svg);
}

// ---------- tooltip (one floating box for all charts) ----------
let tipEl = null;
function tip(node, html) {
  const show = e => {
    tipEl ??= Object.assign(document.body.appendChild(document.createElement('div')), { className: 'ov-tip', role: 'tooltip' });
    tipEl.innerHTML = html(); tipEl.hidden = false;
    const r = (e.touches?.[0] ?? e), x = r.clientX ?? node.getBoundingClientRect().left, y = r.clientY ?? node.getBoundingClientRect().top;
    const w = tipEl.offsetWidth; tipEl.style.left = `${Math.max(8, Math.min(innerWidth - w - 8, x + 14))}px`; tipEl.style.top = `${y + 16}px`;
  };
  node.addEventListener('pointermove', show); node.addEventListener('focus', e => show({ clientX: node.getBoundingClientRect().right, clientY: node.getBoundingClientRect().top }));
  const hide = () => { if (tipEl) tipEl.hidden = true; };
  node.addEventListener('pointerleave', hide); node.addEventListener('blur', hide);
}

const table = (head, rows) => `<table class="ov-table"><thead><tr>${head.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>${rows.map(r => `<tr${r.cur ? ' class="is-cur"' : ''}>${r.cells.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table>`;

/** Draw the four charts into a host already holding overviewHtml(o). */
export function drawCharts(root, o) {
  const I = o.indices, q = s => root.querySelector(s);
  const pick = (id, title) => (s, node) => {
    root.querySelectorAll(`[data-chart="${id}"] .ov-grp.is-pick`).forEach(n => n.classList.remove('is-pick'));
    node.classList.add('is-pick');
    q(`[data-why="${id}"]`).innerHTML = whyHtml(title(s), s);
  };
  const dvTitle = d => `Đại vận ${d.age_from}–${d.age_to} tuổi (${d.year_from}–${d.year_to}) · cung ${d.palace} (${d.branch})`;
  const draw = () => {
    columns(q('[data-plot="dv"]'), I.decades, { label: 'Xu hướng đại vận: mức thuận lợi và mức thử thách', title: dvTitle, current: d => d.current, xCaption: 'tuổi bắt đầu mỗi chặng',
      sub: (d, small) => small ? [String(d.age_from), ''] : [`${d.age_from}–${d.age_to}`, String(d.year_from)], onPick: pick('dv', dvTitle) });
    lines(q('[data-plot="tv"]'), I.years, { onPick: pick('tv', y => `Năm ${y.year} (${y.can_chi}), ${y.age} tuổi · tiểu hạn ở ${y.palace}, lưu Thái Tuế ở ${y.thai_tue}`) });
    radar(q('[data-plot="rd"]'), I.palaces, { onPick: pick('rd', p => `Cung ${p.palace} (${p.branch}) và tam phương`) });
    if (I.months) columns(q('[data-plot="nv"]'), I.months.months, { label: `Nguyệt vận năm ${I.months.year}`, title: m => `Tháng ${m.month} âm lịch · cung ${m.palace}`,
      sub: (m, small) => [`T${m.month}`, small ? '' : m.palace.split(' ').map(w => w[0]).join('')], onPick: pick('nv', m => `Tháng ${m.month} âm lịch năm ${I.months.year} · nguyệt hạn ở cung ${m.palace}`) });
  };
  draw();
  q('[data-table="dv"]').innerHTML = table(['Chặng', 'Cung', SIDE.support, SIDE.limit], I.decades.map(d => ({ cur: d.current, cells: [`${d.age_from}–${d.age_to} tuổi (${d.year_from}–${d.year_to})`, esc(d.palace), fmt(d.support), fmt(d.limit)] })));
  q('[data-table="tv"]').innerHTML = table(['Năm', 'Tiểu hạn', 'Lưu Thái Tuế', SIDE.support, SIDE.limit], I.years.map(y => ({ cur: y.current, cells: [`${y.year} (${esc(y.can_chi)})`, esc(y.palace), esc(y.thai_tue), fmt(y.support), fmt(y.limit)] })));
  q('[data-table="rd"]').innerHTML = table(['Cung', SIDE.support, SIDE.limit], I.palaces.map(p => ({ cells: [esc(p.palace), fmt(p.support), fmt(p.limit)] })));
  if (I.months) q('[data-table="nv"]').innerHTML = table(['Tháng', 'Cung', SIDE.support, SIDE.limit], I.months.months.map(m => ({ cells: [String(m.month), esc(m.palace), fmt(m.support), fmt(m.limit)] })));
  // the current decade and year open with their rules listed: the page answers "why" before anyone asks
  const cd = I.decades.find(d => d.current), cy = I.years.find(y => y.current);
  if (cd) q('[data-why="dv"]').innerHTML = whyHtml(dvTitle(cd), cd);
  if (cy) q('[data-why="tv"]').innerHTML = whyHtml(`Năm ${cy.year} (${cy.can_chi}), ${cy.age} tuổi · tiểu hạn ở ${cy.palace}, lưu Thái Tuế ở ${cy.thai_tue}`, cy);
  return draw;
}

/** Render the overview into `host`; `onChapter(id)` opens a Tử Vi chapter. Returns nothing; redraws on resize while visible. */
export function renderOverview(host, o, { onChapter } = {}) {
  host.innerHTML = overviewHtml(o);
  const draw = drawCharts(host, o);
  host.querySelectorAll('[data-ov-ch]').forEach(b => b.onclick = () => onChapter?.(b.dataset.ovCh));
  // drawn while the tab may still be hidden (width 0): redraw once the plots have a real width, and whenever it changes
  const plot = host.querySelector('.ov-plot');
  let w = -1, t = 0;                                     // the observer's first call always redraws at the settled width
  const check = () => { const cw = plot.clientWidth; if (!cw || Math.abs(cw - w) < 8) return; w = cw; clearTimeout(t); t = setTimeout(draw, 40); };
  host._ovRo?.disconnect(); removeEventListener('resize', host._ovCheck ?? (() => {}));
  const ro = new ResizeObserver(check); ro.observe(plot);
  host._ovRo = ro; host._ovCheck = check; addEventListener('resize', check);
  setTimeout(check, 60);                                  // also without a rendering frame (observer callbacks wait for one)
}
