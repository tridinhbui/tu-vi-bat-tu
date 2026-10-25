// Chart wheel: hand-written SVG. Standard orientation: the Ascendant at 9 o'clock, the zodiac running counter-clockwise.
// Positions, cusps and aspects are drawn exactly as /api/west returns them; the only geometry done here is screen layout
// (where a glyph sits when its neighbours are too close, how far the view is zoomed).
import { esc } from '../util.js';
import { SIGNS, BODY, ASPECT, bodyName, bodyGlyph, signName, aspName } from './vocab.js';

const C = 300, PAD = 30, NS = 'http://www.w3.org/2000/svg';
const rad = d => d * Math.PI / 180;
const norm = d => ((d % 360) + 360) % 360;

/** Ring radii and type sizes. `compact` (a phone-width wheel) drops the minutes line and enlarges every label so it stays readable
 *  when the whole 660-unit drawing is shrunk to ~340 px; `bi` makes room for a second set of glyphs outside the natal ones. */
function metrics(compact, bi) {
  if (!bi) return compact
    ? { R0: 296, Rz: 252, g: { r: 222, f: 28, d: 194, df: 18, m: null, rr: 176, rf: 14 }, Rh: 164, hR: 150, hF: 17, Ra: 134 }
    : { R0: 296, Rz: 256, g: { r: 231, f: 19, d: 210, df: 10.5, m: 199, mf: 8.5, rr: 188, rf: 8.5 }, Rh: 177, hR: 164, hF: 10.5, Ra: 151 };
  return compact
    ? { R0: 296, Rz: 254, o: { r: 232, f: 23, d: 211, df: 14, m: null, rr: 198, rf: 12 }, Rb: 189, g: { r: 170, f: 22, d: 150, df: 14, m: null, rr: 136, rf: 12 }, Rh: 126, hR: 114, hF: 13, Ra: 101 }
    : { R0: 296, Rz: 256, o: { r: 238, f: 16, d: 221, df: 9.5, m: null, rr: 211, rf: 8 }, Rb: 202, g: { r: 186, f: 16, d: 169, df: 9.5, m: 159, mf: 7.5, rr: 149, rf: 7.5 }, Rh: 140, hR: 129, hF: 9.5, Ra: 117 };
}

/** Spread glyphs that would overlap. Items keep their order around the circle; any run closer than `sep` degrees is laid out at
 *  exactly `sep` apart, centred on the mean of its true longitudes, and runs that then touch are merged and re-centred. Starts after the
 *  widest empty arc so a run never straddles the seam. Returns id → drawn longitude. */
export function spread(items, sep) {
  const n = items.length, out = new Map();
  if (!n) return out;
  sep = Math.min(sep, 360 / n * 0.96);
  const s = [...items].sort((a, b) => a.lon - b.lon);
  let gi = 0, gmax = -1;
  for (let i = 0; i < n; i++) { const g = n === 1 ? 360 : norm(s[(i + 1) % n].lon - s[i].lon); if (g > gmax) { gmax = g; gi = i; } }
  const seq = Array.from({ length: n }, (_, k) => s[(gi + 1 + k) % n]);
  const x = []; seq.forEach((it, i) => { let v = it.lon; if (i) while (v < x[i - 1]) v += 360; x.push(v); });
  let cl = x.map((v, i) => ({ i, n: 1, sum: v }));
  const first = c => c.sum / c.n - (c.n - 1) * sep / 2, last = c => c.sum / c.n + (c.n - 1) * sep / 2;
  for (let guard = 0, merged = true; merged && guard < 200; guard++) {
    merged = false;
    for (let k = 0; k < cl.length - 1; k++) {
      if (last(cl[k]) + sep > first(cl[k + 1]) + 1e-9) { cl[k] = { i: cl[k].i, n: cl[k].n + cl[k + 1].n, sum: cl[k].sum + cl[k + 1].sum }; cl.splice(k + 1, 1); merged = true; break; }
    }
    if (!merged && cl.length > 1 && last(cl[cl.length - 1]) + sep > first(cl[0]) + 360) { // collision across the seam
      const a = cl.pop(), b = cl.shift();
      cl.unshift({ i: a.i, n: a.n + b.n, sum: a.sum - 360 * a.n + b.sum }); merged = true;
      // indices of the moved run now precede the first: rotate seq/x accordingly
      const moved = seq.splice(a.i), mx = x.splice(a.i).map(v => v - 360);
      seq.unshift(...moved); x.unshift(...mx);
      let i0 = 0; cl = cl.map(c => { const r = { ...c, i: i0 }; i0 += c.n; return r; });
    }
  }
  for (const c of cl) for (let j = 0; j < c.n; j++) out.set(seq[c.i + j].id, norm(first(c) + j * sep));
  return out;
}

const lonOf = (ch, id) => (ch.bodies?.[id] || ch.points?.[id] || ch.angles?.[id] || ch.lots?.[id])?.lon;

export function createWheel(host, { onSelect, label = 'Bánh xe bản đồ sao' } = {}) {
  host.innerHTML = `<div class="wt-wheel-box"><svg class="wt-wheel" xmlns="${NS}" role="group" aria-label="${esc(label)}"></svg></div>`;
  const box = host.firstElementChild, svg = box.firstElementChild;
  const base = { x: -PAD, y: -PAD, w: 600 + 2 * PAD };
  let view = { s: 1, x: base.x, y: base.y }, data = null, sel = null, compact = null, dragged = false, geo = null;

  const applyView = () => {
    const w = base.w / view.s;
    view.x = Math.min(Math.max(view.x, base.x), base.x + base.w - w);
    view.y = Math.min(Math.max(view.y, base.y), base.y + base.w - w);
    svg.setAttribute('viewBox', `${view.x} ${view.y} ${w} ${w}`);
    svg.style.touchAction = view.s > 1.01 ? 'none' : 'pan-x pan-y';
    box.classList.toggle('zoomed', view.s > 1.01);
    host.dispatchEvent(new CustomEvent('wt-zoom', { detail: view.s }));
  };
  /** Zoom by `f` keeping the drawing point (px, py) under the same screen spot. */
  const zoomAt = (f, px = C, py = C) => {
    const s = Math.min(4, Math.max(1, view.s * f)), w0 = base.w / view.s, w1 = base.w / s;
    view.x = px - (px - view.x) * w1 / w0; view.y = py - (py - view.y) * w1 / w0; view.s = s; applyView();
  };
  const toSvg = (cx, cy) => { const m = svg.getScreenCTM(); if (!m) return { x: C, y: C }; const p = new DOMPoint(cx, cy).matrixTransform(m.inverse()); return { x: p.x, y: p.y }; };

  // ----- drawing -----
  function draw() {
    if (!data) return;
    const ch = data.chart, bi = !!data.outer, M = metrics(compact, bi);
    const rot = ch.angles?.asc?.lon ?? 0;
    const A = lon => rad(180 + lon - rot);
    const P = (r, lon) => [C + r * Math.cos(A(lon)), C - r * Math.sin(A(lon))];
    const pt = (r, lon) => P(r, lon).map(v => v.toFixed(2)).join(',');
    const arc = (r1, r2, a, b) => { // annular sector from lon a to lon b (counter-clockwise on screen)
      const span = norm(b - a), large = span > 180 ? 1 : 0;
      return `M${pt(r2, a)}A${r2},${r2} 0 ${large} 0 ${pt(r2, b)}L${pt(r1, b)}A${r1},${r1} 0 ${large} 1 ${pt(r1, a)}Z`;
    };
    const o = [];
    geo = { arc, Ra: M.Ra, Ro: bi ? M.Rb : M.Rz };
    // zodiac ring
    o.push(`<circle class="wt-ring" cx="${C}" cy="${C}" r="${M.R0}"/><circle class="wt-ring-in" cx="${C}" cy="${C}" r="${M.Rz}"/>`);
    for (const s of SIGNS) {
      const a = s.i * 30, [gx, gy] = P((M.R0 + M.Rz) / 2 + 3, a + 15);
      o.push(`<g class="wt-sign el-${s.el}" data-sel="sign:${s.id}"><path class="wt-sign-bg" d="${arc(M.Rz, M.R0, a, a + 30)}"/>`
        + `<text class="wt-sign-g" x="${gx.toFixed(1)}" y="${gy.toFixed(1)}" font-size="${compact ? 26 : 21}">${s.g}</text><title>${esc(s.vi)}</title></g>`);
      o.push(`<line class="wt-sign-sep" x1="${P(M.Rz, a)[0]}" y1="${P(M.Rz, a)[1]}" x2="${P(M.R0, a)[0]}" y2="${P(M.R0, a)[1]}"/>`);
    }
    let ticks = '';
    for (let d = 0; d < 360; d++) {
      const len = d % 10 === 0 ? 9 : d % 5 === 0 ? 6 : compact ? 0 : 2.5;
      if (!len || d % 30 === 0) continue;
      const [x1, y1] = P(M.Rz, d), [x2, y2] = P(M.Rz + len, d);
      ticks += `M${x1.toFixed(1)},${y1.toFixed(1)}L${x2.toFixed(1)},${y2.toFixed(1)}`;
    }
    o.push(`<path class="wt-tick" d="${ticks}"/>`);
    if (bi) o.push(`<circle class="wt-ring-bi" cx="${C}" cy="${C}" r="${M.Rb}"/>`);

    // houses
    const cusps = ch.houses?.cusps?.[ch.houses.system];
    o.push(`<circle class="wt-ring-h" cx="${C}" cy="${C}" r="${M.Rh}"/><circle class="wt-ring-a" cx="${C}" cy="${C}" r="${M.Ra}"/>`);
    if (cusps) {
      // house numbers sit mid-sector; very narrow houses (polar latitudes) push their numbers apart like glyphs
      const mids = cusps.map((c, i) => ({ id: String(i), lon: c.lon + norm(cusps[(i + 1) % 12].lon - c.lon) / 2 }));
      const hAt = spread(mids, M.hF * 1.25 / M.hR * 180 / Math.PI);
      cusps.forEach((c, i) => {
        const next = cusps[(i + 1) % 12].lon, [hx, hy] = P(M.hR, hAt.get(String(i)));
        o.push(`<g class="wt-hs" data-sel="house:${i + 1}" role="button" tabindex="0" aria-label="Nhà ${i + 1}, đỉnh ${esc(c.fmt)} ${esc(signName(c.sign))}">`
          + `<path class="wt-hs-bg" d="${arc(M.Ra, bi ? M.Rb : M.Rz, c.lon, next)}"/>`
          + `<text class="wt-hn" x="${hx.toFixed(1)}" y="${hy.toFixed(1)}" font-size="${M.hF}">${i + 1}</text></g>`);
      });
      cusps.forEach((c, i) => {
        const [x1, y1] = P(M.Ra, c.lon), [x2, y2] = P(M.Rz, c.lon);
        o.push(`<line class="wt-cusp${i % 3 === 0 ? ' ang' : ''}" x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}"/>`);
      });
    }
    // the four angles, drawn from chart.angles (in Whole Sign they are not the cusps)
    const aF = compact ? 18 : 11, aAt = ch.angles ? spread(['asc', 'mc', 'dsc', 'ic'].map(id => ({ id, lon: ch.angles[id].lon })), aF * 2.4 / (M.R0 + 17) * 180 / Math.PI) : null;
    if (ch.angles) for (const k of ['asc', 'mc', 'dsc', 'ic']) {
      const lon = ch.angles[k].lon, [x1, y1] = P(M.Ra, lon), [x2, y2] = P(M.R0 + 6, lon), [lx, ly] = P(M.R0 + 17, aAt.get(k));
      o.push(`<g class="wt-ang wt-p" data-sel="planet:${k}" role="button" tabindex="0" aria-label="${esc(bodyName(k))} ${esc(ch.angles[k].fmt)} ${esc(signName(ch.angles[k].sign))}">`
        + `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}"/>`
        + `<text x="${lx.toFixed(1)}" y="${ly.toFixed(1)}" font-size="${aF}">${k.toUpperCase()}</text></g>`);
    }
    // Moon's possible arc on a day without a birth time
    if (ch.moon_day_range) {
      const r = ch.moon_day_range, rr = (bi ? M.Rb : M.Rz) - 5;
      const span = norm(r.end.lon - r.start.lon);
      o.push(`<path class="wt-moonarc" d="M${pt(rr, r.start.lon)}A${rr},${rr} 0 ${span > 180 ? 1 : 0} 0 ${pt(rr, r.end.lon)}"><title>Mặt Trăng có thể ở bất kỳ đâu từ ${esc(r.start.fmt)} ${esc(signName(r.start.sign))} đến ${esc(r.end.fmt)} ${esc(signName(r.end.sign))} trong ngày sinh</title></path>`);
    }

    // aspect lines (natal), or the outer-to-natal links in a bi-wheel when there are any
    const lines = bi && data.outer.links?.length ? data.outer.links.map((l, i) => ({ ...l, i, link: true, la: (data.outer.bodies[l.a] || data.outer.points?.[l.a])?.lon, lb: lonOf(ch, l.b) }))
      : (ch.aspects || []).map((a, i) => ({ ...a, i, la: lonOf(ch, a.a), lb: lonOf(ch, a.b) }));
    for (const a of lines) {
      if (a.type === 'conjunction' || a.la == null || a.lb == null) continue;
      const k = ASPECT[a.type] || { tone: 'soft', major: false }, [x1, y1] = P(M.Ra, a.la), [x2, y2] = P(M.Ra, a.lb);
      const d = `M${x1.toFixed(1)},${y1.toFixed(1)}L${x2.toFixed(1)},${y2.toFixed(1)}`;
      o.push(`<g class="wt-asp tone-${k.tone} ${k.major ? 'maj' : 'min'}${a.link ? ' link' : ''}" data-sel="${a.link ? 'link' : 'aspect'}:${a.i}" data-a="${a.a}" data-b="${a.b}">`
        + `<path class="wt-asp-hit" d="${d}"/><path class="wt-asp-l" d="${d}"/><title>${esc(bodyName(a.a))} ${esc(aspName(a.type))} ${esc(bodyName(a.b))}</title></g>`);
    }

    // glyph sets: natal inside, the other set (transit / progressed) on the outer band
    const set = (pts, G, ring, edge) => {
      const ids = Object.keys(pts).filter(id => pts[id]?.lon != null);
      const ang = id => id === 'asc' || id === 'mc';   // progressed angles ride the outer ring as small "ASC"/"MC" labels
      const wpx = Math.max(G.f * .9, G.df * 1.7, ids.some(ang) ? G.f * 1.3 : 0), sepDeg = wpx / Math.min(G.rr, G.d) * 180 / Math.PI + .4;
      const at = spread(ids.map(id => ({ id, lon: pts[id].lon })), sepDeg);
      for (const id of ids) {
        const p = pts[id], dl = at.get(id), [gx, gy] = P(G.r, dl), [dx, dy] = P(G.d, dl);
        const [tx1, ty1] = P(edge, p.lon), [tx2, ty2] = P(edge - 6, p.lon), [lx, ly] = P(G.r + G.f * .62, dl);
        const fm = String(p.fmt || '').split('°'), deg = fm[0], min = (fm[1] || '').trim();
        const moved = Math.abs(((dl - p.lon + 540) % 360) - 180) > .3;
        const lab = `${bodyName(id)} ${p.fmt || ''} ${signName(p.sign)}${p.house ? ', nhà ' + p.house : ''}${p.retrograde ? ', nghịch hành' : ''}${ring === 'outer' ? ' (' + data.outer.label + ')' : ''}`;
        let g = `<g class="wt-p ${ring}${p.retrograde ? ' rx' : ''}${ang(id) ? ' ax' : ''}" data-sel="${ring === 'outer' ? 'outer' : 'planet'}:${id}" role="button" tabindex="0" aria-label="${esc(lab)}">`
          + `<path class="wt-lead" d="M${tx1.toFixed(1)},${ty1.toFixed(1)}L${tx2.toFixed(1)},${ty2.toFixed(1)}${moved ? `L${lx.toFixed(1)},${ly.toFixed(1)}` : ''}"/>`
          + `<circle class="wt-hit" cx="${gx.toFixed(1)}" cy="${gy.toFixed(1)}" r="${(G.f * .8).toFixed(1)}"/>`
          + `<text class="wt-pg" x="${gx.toFixed(1)}" y="${gy.toFixed(1)}" font-size="${ang(id) ? (G.f * .62).toFixed(1) : G.f}">${ang(id) ? id.toUpperCase() : bodyGlyph(id)}</text>`
          + `<text class="wt-pd" x="${dx.toFixed(1)}" y="${dy.toFixed(1)}" font-size="${G.df}">${esc(deg)}°</text>`;
        if (G.m && min) { const [mx, my] = P(G.m, dl); g += `<text class="wt-pm" x="${mx.toFixed(1)}" y="${my.toFixed(1)}" font-size="${G.mf}">${esc(min)}</text>`; }
        if (p.retrograde) { const [rx, ry] = P(G.rr, dl); g += `<text class="wt-pr" x="${rx.toFixed(1)}" y="${ry.toFixed(1)}" font-size="${G.rf}">R</text>`; }
        if (id === 'moon' && ch.moon_day_range && ring === 'inner') { const [qx, qy] = P(G.rr, dl); g += `<text class="wt-pr q" x="${qx.toFixed(1)}" y="${qy.toFixed(1)}" font-size="${G.rf}">≈</text>`; }
        o.push(g + '</g>');
      }
    };
    const natal = {};
    for (const id of ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto', 'chiron']) natal[id] = ch.bodies?.[id];
    if (ch.points) { natal.north_node = ch.points.north_node; natal.south_node = ch.points.south_node; }
    if (ch.lots?.fortune && !bi) natal.fortune = ch.lots.fortune;
    set(natal, M.g, 'inner', bi ? M.Rb : M.Rz);
    if (bi) set(data.outer.bodies, M.o, 'outer', M.Rz);

    svg.innerHTML = o.join('');
    paint();
  }

  // ----- selection -----
  function paint() {
    svg.classList.toggle('has-sel', !!sel);
    svg.querySelectorAll('.on').forEach(e => e.classList.remove('on'));
    svg.querySelector('.wt-span')?.remove();
    if (!sel) return;
    // a house of another system than the wheel's (Lilly's, whole sign, Ptolemy's places): drawn as its own band
    const span = sel.kind === 'span' ? sel : sel.span;
    if (span && geo) {
      const g = document.createElementNS(NS, 'g');
      g.setAttribute('class', 'wt-span on');
      g.innerHTML = `<path d="${geo.arc(geo.Ra, geo.Ro, span.from, span.to)}"/><title>${esc(span.label || '')}</title>`;
      svg.insertBefore(g, svg.querySelector('.wt-asp, .wt-p'));
    }
    const on = q => svg.querySelectorAll(q).forEach(e => e.classList.add('on'));
    if (sel.kind === 'planet' || sel.kind === 'outer') {
      on(`[data-sel="${sel.kind}:${sel.id}"]`);
      if (sel.kind === 'planet') on(`.wt-asp:not(.link)[data-a="${sel.id}"],.wt-asp:not(.link)[data-b="${sel.id}"],.wt-asp.link[data-b="${sel.id}"]`);
      else on(`.wt-asp.link[data-a="${sel.id}"]`);
    } else if (sel.kind === 'pair') on(`[data-sel="planet:${sel.a}"],[data-sel="planet:${sel.b}"]`);
    else if (sel.kind === 'house') on(`[data-sel="house:${sel.n}"]`);
    else if (sel.kind === 'sign') on(`[data-sel="sign:${sel.id}"]`);
    else if (sel.kind === 'aspect' || sel.kind === 'link') {
      const g = svg.querySelector(`[data-sel="${sel.kind}:${sel.i}"]`);
      if (g) { g.classList.add('on'); on(`[data-sel="${sel.kind === 'link' ? 'outer' : 'planet'}:${g.dataset.a}"],[data-sel="planet:${g.dataset.b}"]`); }
      else { // conjunctions have no line: light up the two bodies
        const a = data?.chart?.aspects?.[sel.i]; if (a && sel.kind === 'aspect') on(`[data-sel="planet:${a.a}"],[data-sel="planet:${a.b}"]`);
      }
    }
  }
  const parseSel = v => {
    const [k, x] = v.split(':');
    if (k === 'house') return { kind: 'house', n: +x };
    if (k === 'aspect' || k === 'link') return { kind: k, i: +x };
    return { kind: k, id: x };
  };
  const pick = el => { const t = el.closest('[data-sel]'); if (!t) return; const s = parseSel(t.dataset.sel); sel = s; paint(); onSelect?.(s); };
  svg.addEventListener('click', e => { if (dragged) { dragged = false; return; } pick(e.target); });
  svg.addEventListener('keydown', e => { if ((e.key === 'Enter' || e.key === ' ') && e.target.closest('[data-sel]')) { e.preventDefault(); pick(e.target); } });

  // ----- zoom: buttons, ctrl+wheel / trackpad pinch, two-finger pinch, drag to pan once zoomed -----
  svg.addEventListener('wheel', e => {
    if (!e.ctrlKey && view.s <= 1.01) return;
    e.preventDefault();
    const p = toSvg(e.clientX, e.clientY);
    if (e.ctrlKey) zoomAt(Math.exp(-e.deltaY * .01), p.x, p.y);
    else { const k = base.w / view.s / svg.clientWidth; view.x += e.deltaX * k; view.y += e.deltaY * k; applyView(); }
  }, { passive: false });
  const ptrs = new Map(); let pinch = null, pan = null;
  svg.addEventListener('pointerdown', e => {
    ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (ptrs.size === 2) {
      const [a, b] = [...ptrs.values()];
      pinch = { d: Math.hypot(a.x - b.x, a.y - b.y), s: view.s }; pan = null;
    } else if (ptrs.size === 1) { pan = { x: e.clientX, y: e.clientY, vx: view.x, vy: view.y, moved: false }; dragged = false; }
  });
  svg.addEventListener('pointermove', e => {
    if (!ptrs.has(e.pointerId)) return;
    ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pinch && ptrs.size === 2) {
      const [a, b] = [...ptrs.values()], d = Math.hypot(a.x - b.x, a.y - b.y), m = toSvg((a.x + b.x) / 2, (a.y + b.y) / 2);
      zoomAt(pinch.s * d / pinch.d / view.s, m.x, m.y); dragged = true;
    } else if (pan && view.s > 1.01) {
      const dx = e.clientX - pan.x, dy = e.clientY - pan.y;
      if (!pan.moved && Math.hypot(dx, dy) < 5) return;
      if (!pan.moved) { pan.moved = true; try { svg.setPointerCapture(e.pointerId); } catch { /* pointer already gone */ } }
      const k = base.w / view.s / svg.clientWidth;
      view.x = pan.vx - dx * k; view.y = pan.vy - dy * k; applyView(); dragged = true;
    }
  });
  const up = e => { ptrs.delete(e.pointerId); if (ptrs.size < 2) pinch = null; if (!ptrs.size) pan = null; };
  svg.addEventListener('pointerup', up); svg.addEventListener('pointercancel', up);

  const ro = new ResizeObserver(() => {
    const c = (box.clientWidth || 600) < 520;
    if (c !== compact) { compact = c; draw(); }
  });
  ro.observe(box);
  compact = (box.clientWidth || 600) < 520;
  applyView();

  return {
    svg,
    render(d) { data = d; sel = null; draw(); },
    select(s) { sel = s; paint(); },
    zoom(f) { zoomAt(f); },
    reset() { view = { s: 1, x: base.x, y: base.y }; applyView(); },
    get scale() { return view.s; },
  };
}
