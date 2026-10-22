// "Tổng quan lá số" (docs/PRODUCT-PLAN.md 1.5): the reasoner's frame and theses for Mệnh, and four charts from POST /api/overview
// (src/interpret/overview.ts, indices.ts). The period charts (đại vận, years, months) show one of five levels per period — how the period
// activates the whole chart, against 1,000 sample charts — with two to four plain sentences; rule ids, weights and formulas stay in the
// "Căn cứ" fold. The radar shows the natal quality of each palace only. Plain SVG, drawn at the host's real width (re-drawn on resize) so
// text keeps its size on phones. No calculation lives here: levels, sentences and numbers come from the server as they are.
import { esc } from './util.js';

const SIDE = { support: 'Mức thuận lợi', limit: 'Mức thử thách' };
const LAYER = { ban_menh: 'Bản mệnh (cung và tam phương)', hoa_van: 'Tứ Hóa theo can đại vận', van: 'Câu sách về cung vận', nen: 'Nền bẩm sinh của cung',
  vung: 'Độ vững của cả lá số', dai_van: 'Đại vận đang đi', tieu_han: 'Câu sách về cung tiểu hạn', luu_thai_tue: 'Cung lưu Thái Tuế',
  luu_sao: 'Lưu Khốc, Hư ở tiểu hạn (TH tr.114)', luu_sao_tl: 'Sao lưu khác (thông lệ)', luu_tu_hoa: 'Lưu Tứ Hóa', thong_le_cap: 'Giới hạn phần thông lệ', nam: 'Mức của năm', nguyet: 'Cung nguyệt hạn' };
const METHOD = { thang: 'Thang năm mức', sach_truoc: 'Sách trước, thông lệ sau', dai_van: 'Đại vận', nam: 'Từng năm', thang_am: 'Từng tháng', ban_menh: 'Mười hai cung', bat_tu: 'Dải Bát Tự' };
const BASIS = { sach: 'sách', sach_dien_giai: 'sách, diễn ý', thong_le: 'thông lệ', nhap: 'thử nghiệm', tinh_toan: 'tính toán' };
const SCOPE = { self: 'chính cung', opp: 'xung chiếu', trine: 'tam hợp', menh: 'Mệnh' };
/** a claim's verdict said in words after its sentence, not as a badge */
const VERDICT = { affirmed: '', qualified: 'Điều này có giới hạn.', contested: 'Lá số cũng có chiều ngược lại ở điểm này.' };
const LEVELS = ['Rất thử thách', 'Nhiều thử thách', 'Trung bình', 'Thuận', 'Rất thuận'];
const CHAPTERS = [['ban-menh', 'Bản Mệnh'], ['tinh-cach', 'Tính cách'], ['cong-danh', 'Công danh'], ['tai-bach', 'Tài Bạch'], ['quan-he', 'Quan hệ'],
  ['dai-han', 'Đại hạn & lưu niên'], ['cach-cuc', 'Cách cục'], ['muoi-hai-cung', 'Mười hai cung']];
const NS = 'http://www.w3.org/2000/svg';
const fmt = x => (Math.round(x * 100) / 100).toLocaleString('vi-VN', { maximumFractionDigits: 2 });
const niceMax = v => { const s = [0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 15, 20]; return s.find(x => x >= v) ?? Math.ceil(v); };

export function overviewHtml(o, prose = null) {
  const I = o.indices, lv = I.levels || LEVELS;
  return `<div class="ov">
    <p class="ov-disc" role="note"><b>Mỗi chặng, mỗi năm được xếp vào một trong năm mức</b> (${lv.slice().reverse().map(esc).join(' · ')}), so với 1.000 lá số mẫu. Đây là mức tổng hợp từ câu sách và thông lệ có ghi nhãn, không phải xác suất hay dự báo; bấm một cột để đọc vì sao.</p>
    ${frameHtml(o, prose?.menh)}
    <div class="ov-grid">
      ${card('dv', 'Xu hướng đại vận', 'Mười chặng, mỗi chặng mười năm: chặng ấy đánh thức lá số ra sao — Tứ Hóa theo can của chặng, lời sách về cung vận, trên nền cung vận và độ vững của cả lá số. Đường ngang giữa là mức thường gặp; cột lên là thuận hơn, cột xuống là nhiều thử thách hơn.', lv)}
      ${card('tv', 'Tiểu vận từng năm', `Mười năm trước và sau năm ${I.year}: đại vận đang đi, cung tiểu hạn, sao lưu và lưu Tứ Hóa (thông lệ).`, lv)}
      ${card('rd', 'Mười hai cung (bẩm sinh)', 'Chất lượng bẩm sinh của từng cung cùng tam phương, so với mức thường gặp (vòng tròn đậm). Không đổi theo thời gian.')}
      ${I.months ? card('nv', `Nguyệt vận năm ${I.months.year}`, 'Mức của năm, nhích nhẹ theo cung của từng tháng (vị trí theo Thực Hành tr.115). Không có “nhật vận”.', lv) : ''}
    </div>
    <details class="ov-method"><summary>Cách tính</summary><ul>${Object.entries(I.method).map(([k, v]) => `<li><b>${esc(METHOD[k] || LAYER[k] || k)}:</b> ${esc(v)}.</li>`).join('')}
      ${I.norms ? `<li>Mức thường gặp: ${I.norms.charts} lá số mẫu (${esc(I.norms.corpus)}, bộ mẫu phân tầng, không phải dân số thật).</li>` : ''}
      <li>Phiên bản ${esc(I.version)}, tri thức ${esc(o.kbVersion)}. Cùng ngày giờ sinh luôn cho cùng kết quả.</li></ul></details>
    <nav class="ov-ch" aria-label="Đọc từng chương"><p class="eyebrow">Đọc tiếp từng chương</p>${CHAPTERS.map(([id, t]) => `<button type="button" class="ov-chip" data-ov-ch="${id}">${t}</button>`).join('')}</nav>
  </div>`;
}

function card(id, title, sub, levels) {
  return `<section class="ov-card" data-chart="${id}" aria-labelledby="ov-${id}-h"><header><h3 id="ov-${id}-h">${title}</h3><p>${sub}</p></header>
    ${levels ? levelLegend(levels) : legend()}<div class="ov-plot" data-plot="${id}"></div>
    ${id === 'dv' ? '<div class="ov-bz" data-bz></div>' : ''}
    <div class="ov-why" data-why="${id}" aria-live="polite"><p class="ov-hint">Bấm vào ${id === 'rd' ? 'tên một cung' : id === 'tv' ? 'một năm' : id === 'nv' ? 'một tháng' : 'một chặng'} để đọc vì sao.</p></div>
    <details class="ov-tbl"><summary>Xem bảng</summary><div data-table="${id}"></div></details></section>`;
}
const legend = () => `<p class="ov-leg"><span><i class="sw sw-s sw-line"></i>${SIDE.support}</span><span><i class="sw sw-l sw-line sw-dash"></i>${SIDE.limit}</span></p>`;
const levelLegend = lv => `<p class="ov-leg ov-leg-lv">${lv.map((t, i) => `<span><i class="sw ov-lv-bg-${i}"></i>${esc(t)}</span>`).slice().reverse().join('')}</p>`;

/** The reading's own words for a thesis claim: the sentence the Mệnh chapter (prose.menh, luận cung) argued it with — its full form when it
 *  leans on the sentence before ("Cùng thế ấy, …"), without the paragraph's lead-in or an opening connective; null when the chapter has none. */
const OPEN = /^(Cũng vậy|Ngoài ra|Đồng thời|Thêm vào đó|Bên cạnh đó|Mặt khác|Hơn nữa|Lại nữa|Cũng thế|Song|Tuy vậy|Tuy nhiên|Dẫu vậy),\s*/u;
function claimSentence(menh, tid, concept) {
  for (const p of menh?.paragraphs || []) {
    const s = p.sentences.find(x => x.trace?.step === `claim:${tid}:${concept}`);
    if (!s) continue;
    const t = s.trace.alt || (p.lead && s.text.startsWith(p.lead + ', ') ? s.text.slice(p.lead.length + 2) : s.text);
    return cap(t.replace(OPEN, ''));
  }
  return null;
}
function frameHtml(o, menh) {
  const f = o.frame;
  if (!f) return '';
  const majors = f.vcd ? `Vô chính diệu${f.borrowed.length ? `, mượn ${esc(f.borrowed.join(', '))} của cung xung chiếu` : ''}`
    : f.majors.map(m => `${esc(m.star)}${m.dignity ? ` <small>(${esc(m.dignity)})</small>` : ''}${m.hoa.length ? ` <small>hóa ${esc(m.hoa.map(h => h.replace('Hóa ', '')).join(', '))}</small>` : ''}`).join(', ');
  const marks = [f.than && 'Thân cư Mệnh', f.tuan && 'Tuần', f.triet && 'Triệt'].filter(Boolean).join(' · ');
  const theses = o.theses.map((t, i) => `<li class="ov-th"><p class="ov-th-h"><span class="ov-no">${i + 1}</span>${esc(t.label)}</p>
    <ul>${t.claims.map(c => `<li>${esc(claimSentence(menh, t.id, c.concept) || cap(c.text))}${VERDICT[c.verdict] ? ` <span class="ov-vw">${VERDICT[c.verdict]}</span>` : ''}</li>`).join('')}</ul>
    <details><summary>Căn cứ</summary><ul class="ov-rules">${[...new Map(t.claims.flatMap(c => c.rules).map(r => [r.id, r])).values()]
      .map(r => `<li><code>${esc(r.id)}</code> ${esc(r.cite)}${r.role !== 'base' ? ` <span class="ov-tag">${r.role === 'reducer' ? 'giảm nhẹ' : 'chiều ngược'}</span>` : ''}</li>`).join('')}
      ${t.formations.map(x => `<li>${esc(x.name)} · ${esc(x.cites.join('; '))}</li>`).join('')}</ul></details></li>`).join('');
  return `<section class="ov-frame" aria-labelledby="ov-fr-h"><div class="ov-fr-main"><p class="eyebrow">Khung lá số</p>
    <h3 id="ov-fr-h">Mệnh ở ${esc(f.branch)}: ${majors}</h3>
    ${marks ? `<p class="ov-marks">${marks}</p>` : ''}
    <p class="ov-centre">Trọng tâm khi đọc: <b>${esc(f.centre)}</b></p>
    ${f.formations.length ? `<p class="ov-forms">Cách cục theo sách: ${f.formations.map(x => `<span class="ov-form">${esc(x.name)} <small>${esc(x.cites.join('; '))}</small></span>`).join(' ')}</p>` : ''}</div>
    ${theses ? `<div class="ov-fr-th"><p class="eyebrow">Luận điểm chính về Mệnh</p><ol class="ov-ths">${theses}</ol></div>` : ''}</section>`;
}
const cap = s => s ? s[0].toUpperCase() + s.slice(1) : s;

// ---------- the "why" panels ----------
const basisTag = b => `<span class="ov-tag ov-b-${b}">${BASIS[b] || b}</span>`;
function itemsList(items) {
  return items.length ? `<ul class="ov-items">${items.slice().sort((a, b) => b.w - a.w).map(i => `<li><p>${esc(i.text)}</p><p class="ov-src"><code>${esc(i.id)}</code> · ${esc(i.cite)} · ${SCOPE[i.scope] || ''} · ${basisTag(i.basis)} · trọng số ${fmt(i.w)}${i.side === 'limit' ? ' · bên bất lợi' : ' · bên thuận'}</p></li>`).join('')}</ul>` : '';
}
/** A period (decade, year, month): its level, its sentences, and everything else folded into "Căn cứ". */
function periodWhy(title, s) {
  return `<h4>${esc(title)}</h4><p class="ov-level"><span class="ov-lvchip ov-lv-bg-${s.level}">${esc(s.level_vi)}</span></p>
    <div class="ov-text">${s.text.map(t => `<p>${esc(t)}</p>`).join('')}</div>
    <details class="ov-basis"><summary>Căn cứ</summary>
      <table class="ov-table ov-parts"><thead><tr><th>Lớp</th><th>Thô</th><th>Điểm chuẩn</th><th>Trọng số</th><th>Góp vào</th></tr></thead><tbody>
      ${s.parts.map(p => `<tr><td>${esc(LAYER[p.layer] || p.layer)} ${basisTag(p.basis)}<br><small>${esc(p.note)}</small></td><td>${fmt(p.raw)}</td><td>${fmt(p.z)}</td><td>${fmt(p.weight)}</td><td>${fmt(p.value)}</td></tr>`).join('')}
      <tr class="is-cur"><td>Tổng</td><td></td><td></td><td></td><td>${fmt(s.score)}</td></tr></tbody></table>
      ${itemsList(s.items)}</details>`;
}
/** A palace on the radar: natal readings in words; ids, pages and weights folded. */
function palaceWhy(title, s) {
  const side = k => s.items.filter(i => i.side === k).sort((a, b) => b.w - a.w);
  const list = k => { const xs = side(k); return xs.length ? `<ul>${xs.slice(0, 6).map(i => `<li>${esc(i.text)}${i.scope !== 'self' ? ` <small>(${esc(i.palace)}, ${SCOPE[i.scope]})</small>` : ''}</li>`).join('')}</ul>${xs.length > 6 ? `<p class="ov-none">và ${xs.length - 6} câu khác trong phần căn cứ.</p>` : ''}` : '<p class="ov-none">Không có câu sách nào.</p>'; };
  return `<h4>${esc(title)}</h4>
    <div class="ov-sides"><div><h5>Phía thuận lợi</h5>${list('support')}</div><div><h5>Phía thử thách</h5>${list('limit')}</div></div>
    <details class="ov-basis"><summary>Căn cứ</summary><p class="ov-src">${esc(s.note)}; ${SIDE.support.toLowerCase()} ${fmt(s.support)}, ${SIDE.limit.toLowerCase()} ${fmt(s.limit)} (1 là mức thường gặp).</p>${itemsList(s.items)}</details>`;
}

// ---------- SVG helpers ----------
const el = (tag, attrs = {}, kids = []) => { const e = document.createElementNS(NS, tag); for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v); kids.forEach(k => e.append(k)); return e; };
const txt = (x, y, s, attrs = {}) => { const t = el('text', { x, y, ...attrs }); t.textContent = s; return t; };
function svgFor(w, h, label) { return el('svg', { width: w, height: h, viewBox: `0 0 ${w} ${h}`, role: 'img', 'aria-label': label, class: 'ov-svg' }); }
/** A column from the zero line up (or down) to v, its far end rounded. */
const barPath = (x, y0, w, y1) => {
  const h = Math.abs(y1 - y0), r = Math.min(4, w / 2, h), up = y1 < y0;
  if (h < 0.5) return `M${x} ${y0 - 1}H${x + w}V${y0 + 1}H${x}Z`;
  return up ? `M${x} ${y0}V${y1 + r}Q${x} ${y1} ${x + r} ${y1}H${x + w - r}Q${x + w} ${y1} ${x + w} ${y1 + r}V${y0}Z`
    : `M${x} ${y0}V${y1 - r}Q${x} ${y1} ${x + r} ${y1}H${x + w - r}Q${x + w} ${y1} ${x + w} ${y1 - r}V${y0}Z`;
};

/** Diverging columns of period levels (đại vận, years, months): one column per period from the "thường gặp" line, coloured by level,
 *  over faint bands of the five levels (the corpus cut points). An optional Bát Tự strip runs under the đại vận on the same year axis. */
function levelBars(host, groups, { label, sub, title, current, onPick, xCaption, cuts, strip }) {
  const W = Math.max(300, host.clientWidth), small = W < 560, stripH = strip ? 46 : 0, H = (small ? 236 : 262) + stripH;
  const m = { l: 8, r: small ? 8 : 92, t: 18, b: (small ? 40 : 38) + stripH }, pw = W - m.l - m.r, ph = H - m.t - m.b;   // wide: a right gutter names the bands
  const c = cuts && cuts.length === 4 ? cuts : [-1.2816, -0.5244, 0.5244, 1.2816];
  const lim = Math.max(...groups.map(g => Math.abs(g.score)), Math.abs(c[0]), Math.abs(c[3])) * 1.18;
  const Y = v => m.t + ph / 2 - (ph / 2) * v / lim, y0 = Y(0);
  const svg = svgFor(W, H, label);
  const edges = [lim, c[3], c[2], c[1], c[0], -lim];
  for (let i = 0; i < 5; i++) {
    const a = Math.min(lim, Math.max(-lim, edges[i])), b = Math.min(lim, Math.max(-lim, edges[i + 1])), lv = 4 - i;
    const ya = Y(a), yb = Y(b);
    if (yb - ya < 1) continue;
    svg.append(el('rect', { x: m.l, y: ya, width: pw, height: yb - ya, class: `ov-band ov-band-${lv}` }));
    if (!small && yb - ya >= 12) svg.append(txt(W - m.r + 6, (ya + yb) / 2 + 3.5, LEVELS[lv], { class: 'ov-bandl' }));
  }
  svg.append(el('line', { x1: m.l, x2: W - m.r, y1: y0, y2: y0, class: 'ov-base' }));
  const band = pw / groups.length, bw = Math.max(5, Math.min(26, band - (small ? 4 : 10)));
  groups.forEach((g, i) => {
    const gx = m.l + band * i, cx = gx + band / 2, cur = current?.(g);
    const grp = el('g', { class: `ov-grp${cur ? ' is-cur' : ''}`, tabindex: 0, role: 'button', 'aria-label': `${title(g)}: ${g.level_vi}` });
    if (cur) grp.append(el('rect', { x: gx + 1, y: m.t - 14, width: band - 2, height: ph + 14, class: 'ov-curband', rx: 6 }), txt(cx, m.t - 3, small ? 'Nay' : 'Hiện tại', { class: 'ov-curlbl', 'text-anchor': 'middle' }));
    grp.append(el('rect', { x: gx, y: m.t, width: band, height: ph + m.b - stripH, class: 'ov-hit' }));
    grp.append(el('path', { d: barPath(cx - bw / 2, y0, bw, Y(g.score)), class: `ov-bar ov-lv-${g.level}` }));
    const [l1, l2] = sub(g, small);
    if (l1) grp.append(txt(cx, m.t + ph + 15, l1, { class: `ov-xl${cur ? ' is-cur' : ''}`, 'text-anchor': 'middle' }));
    if (l2) grp.append(txt(cx, m.t + ph + 28, l2, { class: 'ov-xl2', 'text-anchor': 'middle' }));
    grp.addEventListener('click', () => onPick(g, grp));
    grp.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onPick(g, grp); } });
    tip(grp, () => `<b>${esc(title(g))}</b><br>${esc(g.level_vi)}`);
    svg.append(grp);
  });
  if (strip) strip(svg, { x0: m.l, pw, y: H - stripH + 6, h: 22, small });
  else if (small && xCaption) svg.append(txt(m.l + pw / 2, H - 4, xCaption, { class: 'ov-xl2', 'text-anchor': 'middle' }));
  host.replaceChildren(svg);
}

/** The Bát Tự luck pillars under the đại vận, on the same year axis (decade bands are ten years each). */
const baziStrip = (bz, decades) => (svg, { x0, pw, y, h, small }) => {
  const Y1 = decades[0].year_from, Y2 = decades.at(-1).year_to + 1, X = yr => x0 + pw * (yr - Y1) / (Y2 - Y1);
  svg.append(txt(x0, y - 1, small ? 'Bát Tự · điều hậu' : 'Bát Tự: đại vận mang thần điều hậu (Thiệu Vĩ Hoa)', { class: 'ov-xl2 ov-bzh' }));
  for (const p of bz.pillars) {
    if (p.year_from == null) continue;
    const a = Math.max(Y1, p.year_from), b = Math.min(Y2, (p.year_to ?? p.year_from + 9) + 1);
    if (b <= a) continue;
    const g = el('g', { class: `ov-bzseg ov-bz-${p.tag}${p.current ? ' is-cur' : ''}`, tabindex: 0, role: 'img', 'aria-label': `Vận ${p.pillar} (${p.year_from}–${p.year_to}): ${p.tag_vi}` });
    g.append(el('rect', { x: X(a) + 1, y: y + 4, width: Math.max(1, X(b) - X(a) - 2), height: h, rx: 4 }));
    if (X(b) - X(a) - 2 >= p.pillar.length * 6.2 + 8) g.append(txt((X(a) + X(b)) / 2, y + 4 + h / 2 + 4, p.pillar, { 'text-anchor': 'middle' }));
    tip(g, () => `<b>Vận ${esc(p.pillar)}</b> (${p.year_from}–${p.year_to})<br>${esc(p.tag_vi)}${p.reduced ? `<br><small>${esc(p.reduced)}</small>` : ''}`);
    svg.append(g);
  }
};

/** Radar of the twelve palaces (support and limit polygons) with the ring at 1 = the corpus' typical chart. */
function radar(host, ps, { onPick }) {
  const W = Math.max(300, host.clientWidth), S = Math.min(W, 460), small = S < 400;
  const cx = W / 2, cy = S / 2, R = S / 2 - (small ? 66 : 62);   // room for the longest side label ("Điền Trạch")
  const max = niceMax(Math.max(1.5, ...ps.flatMap(p => [p.support, p.limit])));
  const svg = svgFor(W, S, 'Mười hai cung: mức thuận lợi và mức thử thách bẩm sinh so với mức thường gặp');
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
  const pick = (id, title, why) => (s, node) => {
    root.querySelectorAll(`[data-chart="${id}"] .ov-grp.is-pick`).forEach(n => n.classList.remove('is-pick'));
    node.classList.add('is-pick');
    q(`[data-why="${id}"]`).innerHTML = why(title(s), s);
  };
  const dvTitle = d => `Đại vận ${d.age_from}–${d.age_to} tuổi (${d.year_from}–${d.year_to}) · cung ${d.palace} (${d.stem} ${d.branch})`;
  const yTitle = y => `Năm ${y.year} (${y.can_chi}), ${y.age} tuổi · tiểu hạn ở ${y.palace}`;
  const mTitle = m => `Tháng ${m.month} âm lịch năm ${I.months.year} · nguyệt hạn ở cung ${m.palace}`;
  const draw = () => {
    levelBars(q('[data-plot="dv"]'), I.decades, { label: 'Xu hướng đại vận: mức của từng chặng', title: dvTitle, current: d => d.current, xCaption: 'tuổi bắt đầu mỗi chặng',
      sub: (d, small) => small ? [String(d.age_from), ''] : [`${d.age_from}–${d.age_to}`, String(d.year_from)], onPick: pick('dv', dvTitle, periodWhy),
      cuts: I.cuts?.decade, strip: I.bazi ? baziStrip(I.bazi, I.decades) : null });
    levelBars(q('[data-plot="tv"]'), I.years, { label: 'Tiểu vận từng năm: mức của từng năm', title: yTitle, current: y => y.current,
      sub: (y, small) => [(I.years.indexOf(y) % (small ? 5 : 2) === 0 || y.current) ? String(y.year) : '', ''], onPick: pick('tv', yTitle, periodWhy), cuts: I.cuts?.year });
    radar(q('[data-plot="rd"]'), I.palaces, { onPick: pick('rd', p => `Cung ${p.palace} (${p.branch}) và tam phương`, palaceWhy) });
    if (I.months) levelBars(q('[data-plot="nv"]'), I.months.months, { label: `Nguyệt vận năm ${I.months.year}`, title: mTitle,
      sub: (m, small) => [`T${m.month}`, small ? '' : m.palace.split(' ').map(w => w[0]).join('')], onPick: pick('nv', mTitle, periodWhy), cuts: I.cuts?.month });
  };
  draw();
  if (I.bazi) q('[data-bz]').innerHTML = `<p class="ov-cap">${esc(I.bazi.note)} <span class="ov-bzleg"><i class="ov-bz-dung"></i>dụng <i class="ov-bz-hy"></i>hỷ <i class="ov-bz-khong"></i>không mang</span></p>`;
  q('[data-table="dv"]').innerHTML = table(['Chặng', 'Cung', 'Mức'], I.decades.map(d => ({ cur: d.current, cells: [`${d.age_from}–${d.age_to} tuổi (${d.year_from}–${d.year_to})`, esc(d.palace), esc(d.level_vi)] })))
    + (I.bazi ? table(['Vận Bát Tự', 'Năm', 'Điều hậu'], I.bazi.pillars.map(p => ({ cur: p.current, cells: [esc(p.pillar), `${p.year_from ?? ''}–${p.year_to ?? ''}`, esc(p.tag_vi) + (p.reduced ? ' (giảm)' : '')] }))) : '');
  q('[data-table="tv"]').innerHTML = table(['Năm', 'Tiểu hạn', 'Mức'], I.years.map(y => ({ cur: y.current, cells: [`${y.year} (${esc(y.can_chi)})`, esc(y.palace), esc(y.level_vi)] })));
  q('[data-table="rd"]').innerHTML = table(['Cung', SIDE.support, SIDE.limit], I.palaces.map(p => ({ cells: [esc(p.palace), fmt(p.support), fmt(p.limit)] })));
  if (I.months) q('[data-table="nv"]').innerHTML = table(['Tháng', 'Cung', 'Mức'], I.months.months.map(m => ({ cells: [String(m.month), esc(m.palace), esc(m.level_vi)] })));
  // the current decade and year open with their reading: the page answers "why" before anyone asks
  const cd = I.decades.find(d => d.current), cy = I.years.find(y => y.current);
  if (cd) q('[data-why="dv"]').innerHTML = periodWhy(dvTitle(cd), cd);
  if (cy) q('[data-why="tv"]').innerHTML = periodWhy(yTitle(cy), cy);
  return draw;
}

/** Render the overview into `host`; `onChapter(id)` opens a Tử Vi chapter. Returns nothing; redraws on resize while visible. */
export function renderOverview(host, o, { onChapter, prose } = {}) {
  host.innerHTML = overviewHtml(o, prose);
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
