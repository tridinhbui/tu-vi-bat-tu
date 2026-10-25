// Horary chart wheel (SVG, no library). Ascendant on the left, zodiac counter-clockwise, unequal house cusps as computed.
// Planets and aspect lines are keyboard-focusable buttons; selecting one calls onSelect({kind, ...}).
export const GLYPH = { sun: '☉', moon: '☽', mercury: '☿', venus: '♀', mars: '♂', jupiter: '♃', saturn: '♄', uranus: '♅', neptune: '♆', pluto: '♇' };
export const SIGN_GLYPH = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓'];
export const PLANET_VI = { sun: 'Mặt Trời', moon: 'Mặt Trăng', mercury: 'Thủy tinh', venus: 'Kim tinh', mars: 'Hỏa tinh', jupiter: 'Mộc tinh', saturn: 'Thổ tinh', uranus: 'Thiên Vương', neptune: 'Hải Vương', pluto: 'Diêm Vương' };
export const SIGN_VI = ['Bạch Dương', 'Kim Ngưu', 'Song Tử', 'Cự Giải', 'Sư Tử', 'Xử Nữ', 'Thiên Bình', 'Bọ Cạp', 'Nhân Mã', 'Ma Kết', 'Bảo Bình', 'Song Ngư'];
export const ASPECT_VI = { 0: 'hội hợp', 60: 'lục hợp', 90: 'vuông góc', 120: 'tam hợp', 180: 'xung chiếu' };
const T = '︎';            // text presentation: never draw the glyphs as emoji
const NS = 'http://www.w3.org/2000/svg';
const C = 300, R_OUT = 292, R_SIGN = 254, R_PL = 214, R_HOUSE_IN = 138, R_ASP = 132;

export const fmtDeg = lon => { const d = ((lon % 30) + 30) % 30; const m = Math.floor((d % 1) * 60); return `${Math.floor(d)}°${String(m).padStart(2, '0')}′`; };
export const fmtPos = lon => `${fmtDeg(lon)} ${SIGN_VI[Math.floor(((lon % 360) + 360) % 360 / 30)]}`;

function el(tag, attrs = {}, text) {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (text != null) e.textContent = text;
  return e;
}

export function renderWheel(host, chart, judgment, onSelect) {
  const asc = chart.asc;
  const ang = lon => (180 + (lon - asc)) * Math.PI / 180;
  const xy = (lon, r) => [C + r * Math.cos(ang(lon)), C - r * Math.sin(ang(lon))];
  const sig = judgment?.significators || {};
  const roles = {};
  if (sig.querent) roles[sig.querent.planet] = 'q1';
  if (sig.quesited) roles[sig.quesited.planet] = roles[sig.quesited.planet] ? 'both' : 'q2';
  roles.moon = roles.moon || 'moon';

  const svg = el('svg', { viewBox: '-24 -24 648 648', class: 'hz-wheel', role: 'group', 'aria-label': 'Bản đồ sao vấn sự: điểm Mọc bên trái, các cung hoàng đạo ngược chiều kim đồng hồ' });
  svg.append(el('circle', { cx: C, cy: C, r: R_OUT, class: 'w-ring' }), el('circle', { cx: C, cy: C, r: R_SIGN, class: 'w-ring' }),
    el('circle', { cx: C, cy: C, r: R_HOUSE_IN, class: 'w-ring w-inner' }));
  // signs
  for (let s = 0; s < 12; s++) {
    const [x1, y1] = xy(s * 30, R_SIGN), [x2, y2] = xy(s * 30, R_OUT);
    svg.append(el('line', { x1, y1, x2, y2, class: 'w-sign-div' }));
    const [tx, ty] = xy(s * 30 + 15, (R_SIGN + R_OUT) / 2);
    svg.append(el('text', { x: tx, y: ty, class: `w-sign w-el-${s % 4}`, 'text-anchor': 'middle', 'dominant-baseline': 'central', 'aria-hidden': 'true' }, SIGN_GLYPH[s] + T));
    for (let d = 5; d < 30; d += 5) {
      const [a1, b1] = xy(s * 30 + d, R_SIGN), [a2, b2] = xy(s * 30 + d, R_SIGN + (d % 10 ? 4 : 7));
      svg.append(el('line', { x1: a1, y1: b1, x2: a2, y2: b2, class: 'w-tick' }));
    }
  }
  // houses
  chart.cusps.forEach((c, i) => {
    const angle = i === 0 || i === 3 || i === 6 || i === 9;
    const [x1, y1] = xy(c, R_HOUSE_IN), [x2, y2] = xy(c, R_SIGN);
    svg.append(el('line', { x1, y1, x2, y2, class: angle ? 'w-axis' : 'w-cusp' }));
    const next = chart.cusps[(i + 1) % 12];
    const mid = c + (((next - c) % 360) + 360) % 360 / 2;
    const [hx, hy] = xy(mid, R_HOUSE_IN + 12);
    const qh = judgment?.frame?.quesited_house;
    svg.append(el('text', { x: hx, y: hy, class: 'w-hnum' + (i + 1 === 1 || i + 1 === qh ? ' w-hnum-on' : ''), 'text-anchor': 'middle', 'dominant-baseline': 'central' }, String(i + 1)));
  });
  for (const [lon, lab] of [[chart.asc, 'ASC'], [chart.mc, 'MC']]) {
    const [x, y] = xy(lon, R_OUT + 1);
    svg.append(el('text', { x, y, class: 'w-anglab', 'text-anchor': lab === 'ASC' ? 'end' : 'middle', 'dominant-baseline': lab === 'ASC' ? 'central' : 'auto', dy: lab === 'MC' ? -4 : 0 }, lab));
  }
  // aspect lines among traditional planets within orb
  const pairs = judgment?.pairs || {};
  const aspG = el('g', { class: 'w-asps' });
  for (const [key, p] of Object.entries(pairs)) {
    if (!p.within_orb || p.angle === 0) continue;
    const [a, b] = key.split('-');
    const [x1, y1] = xy(chart.bodies[a].lon, R_ASP), [x2, y2] = xy(chart.bodies[b].lon, R_ASP);
    const main = (roles[a] && roles[b] && (roles[a] !== 'moon' || roles[b] !== 'moon')) && ((roles[a] === 'q1' || roles[a] === 'q2' || roles[a] === 'both') && (roles[b] === 'q1' || roles[b] === 'q2' || roles[b] === 'both'));
    const kind = p.angle === 60 || p.angle === 120 ? 'soft' : 'hard';
    const g = el('g', { class: `w-asp w-asp-${kind}${p.motion === 'applying' ? ' w-app' : ' w-sep'}${main ? ' w-asp-main' : ''}`, tabindex: 0, role: 'button',
      'aria-label': `${PLANET_VI[a]} ${ASPECT_VI[p.angle]} ${PLANET_VI[b]}, lệch ${p.orb.toFixed(2)} độ, ${p.motion === 'applying' ? 'đang tiến tới' : 'đang tách ra'}` });
    g.append(el('line', { x1, y1, x2, y2, class: 'w-asp-hit' }), el('line', { x1, y1, x2, y2, class: 'w-asp-line' }));
    const pick = () => onSelect?.({ kind: 'aspect', key, pair: p });
    g.addEventListener('click', pick); g.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(); } });
    aspG.append(g);
  }
  svg.append(aspG);
  // planets with collision spreading (minimum 8 degrees between glyphs on the ring)
  const ids = Object.keys(chart.bodies).sort((a, b) => chart.bodies[a].lon - chart.bodies[b].lon);
  const pos = ids.map(id => ({ id, lon: chart.bodies[id].lon, at: chart.bodies[id].lon }));
  for (let pass = 0; pass < 40; pass++) {
    let moved = false;
    for (let i = 0; i < pos.length; i++) {
      const a = pos[i], b = pos[(i + 1) % pos.length];
      const gap = (((b.at - a.at) % 360) + 360) % 360;
      if (pos.length > 1 && gap < 8) { a.at -= (8 - gap) / 2; b.at += (8 - gap) / 2; moved = true; }
    }
    if (!moved) break;
  }
  const plG = el('g', { class: 'w-planets' });
  for (const p of pos) {
    const b = chart.bodies[p.id];
    const role = roles[p.id] || (b.traditional ? 'trad' : 'outer');
    const [x0, y0] = xy(p.lon, R_SIGN), [x1, y1] = xy(p.lon, R_SIGN - 9);
    plG.append(el('line', { x1: x0, y1: y0, x2: x1, y2: y1, class: 'w-pl-tick' }));
    const [gx, gy] = xy(p.at, R_PL);
    const g = el('g', { class: `w-pl w-role-${role}`, tabindex: 0, role: 'button',
      'aria-label': `${PLANET_VI[p.id]} ${fmtPos(b.lon)}, nhà ${b.house}${b.retrograde ? ', nghịch hành' : ''}${role === 'q1' ? ', đại diện người hỏi' : role === 'q2' ? ', đại diện việc được hỏi' : role === 'both' ? ', đại diện cả hai bên' : ''}` });
    if (['q1', 'q2', 'both', 'moon'].includes(role)) g.append(el('circle', { cx: gx, cy: gy, r: 16, class: 'w-pl-halo' }));
    g.append(el('text', { x: gx, y: gy, class: 'w-pl-g', 'text-anchor': 'middle', 'dominant-baseline': 'central' }, GLYPH[p.id] + T));
    const [dx, dy] = xy(p.at, R_PL - 27);
    g.append(el('text', { x: dx, y: dy, class: 'w-pl-d', 'text-anchor': 'middle', 'dominant-baseline': 'central' }, `${Math.floor(b.lon % 30)}°${b.retrograde ? '℞' : ''}`));
    const pick = () => onSelect?.({ kind: 'planet', id: p.id });
    g.addEventListener('click', pick); g.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(); } });
    plG.append(g);
  }
  svg.append(plG);
  host.replaceChildren(svg);
  return svg;
}
