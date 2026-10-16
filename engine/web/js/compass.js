// CelestialCompass — the product's signature figure and logo source.
import { BRANCHES, STEMS, ELEMENTS, EL } from './util.js';

const pt = (r, deg) => { const a = (deg - 90) * Math.PI / 180; return [300 + r * Math.cos(a), 300 + r * Math.sin(a)]; };
const f = n => n.toFixed(2);

export function compass({ label = 'La bàn thiên văn: mười hai địa chi và ngũ hành', animate = true, detail = 'full' } = {}) {
  const ticks = [];
  for (let i = 0; i < 120; i++) {
    const long = i % 10 === 0, mid = i % 5 === 0;
    const [x1, y1] = pt(292, i * 3), [x2, y2] = pt(long ? 278 : mid ? 282 : 286, i * 3);
    ticks.push(`<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" class="cp-line${long ? ' cp-strong' : ''}"/>`);
  }
  const branches = BRANCHES.map((b, i) => {
    const [hx, hy] = pt(244, i * 30), [nx, ny] = pt(214, i * 30);
    return `<text x="${f(hx)}" y="${f(hy)}" class="cp-han" lang="zh" text-anchor="middle" dominant-baseline="central">${b.h}</text>
      <text x="${f(nx)}" y="${f(ny)}" class="cp-vn" text-anchor="middle" dominant-baseline="central">${b.n.toUpperCase()}</text>`;
  }).join('');
  const seps = Array.from({ length: 12 }, (_, i) => { const [x1, y1] = pt(262, i * 30 + 15), [x2, y2] = pt(200, i * 30 + 15); return `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" class="cp-line"/>`; }).join('');
  const stems = STEMS.map((s, i) => { const [x, y] = pt(176, i * 36 + 18); return `<text x="${f(x)}" y="${f(y)}" class="cp-han cp-stem" lang="zh" text-anchor="middle" dominant-baseline="central">${s.h}</text>`; }).join('');
  const vert = ELEMENTS.map((e, i) => ({ e, p: pt(112, i * 72) }));
  const pent = vert.map(v => v.p.map(f).join(',')).join(' ');
  const star = [0, 2, 4, 1, 3].map(i => vert[i].p.map(f).join(',')).join(' ');
  const nodes = vert.map(({ e, p }) => `<g class="cp-node el-${EL[e].slug}"><circle cx="${f(p[0])}" cy="${f(p[1])}" r="19"/><text x="${f(p[0])}" y="${f(p[1])}" lang="zh" text-anchor="middle" dominant-baseline="central">${EL[e].h}</text></g>`).join('');
  const orbit = (rx, ry, rot, cls, dur, planet) => `<g class="cp-orbit ${animate ? 'spin' : ''}" style="--dur:${dur}s;transform-origin:300px 300px;transform:rotate(${rot}deg)">
      <ellipse cx="300" cy="300" rx="${rx}" ry="${ry}" class="cp-line cp-orb"/>${planet ? `<circle cx="${300 + rx}" cy="300" r="${planet[0]}" class="${planet[1]}"/>` : ''}</g>`;
  return `<svg class="compass" viewBox="0 0 600 600" role="img" aria-label="${label}" xmlns="http://www.w3.org/2000/svg">
  <circle cx="300" cy="300" r="296" class="cp-disc"/>
  <circle cx="300" cy="300" r="292" class="cp-line cp-strong" fill="none"/>
  ${ticks.join('')}
  <circle cx="300" cy="300" r="270" class="cp-line" fill="none"/>
  <circle cx="300" cy="300" r="262" class="cp-line" fill="none"/>
  <g class="${animate ? 'cp-ring' : ''}">${seps}${branches}</g>
  <circle cx="300" cy="300" r="200" class="cp-line cp-strong" fill="none"/>
  <circle cx="300" cy="300" r="190" class="cp-line" fill="none" stroke-dasharray="2 5"/>
  ${stems}
  <circle cx="300" cy="300" r="156" class="cp-line cp-strong" fill="none"/>
  ${detail === 'full' ? orbit(228, 92, -28, 'a', 46, [5, 'cp-planet a']) + orbit(228, 120, 52, 'b', 64, [4, 'cp-planet b']) + orbit(228, 70, 118, 'c', 38, [3.5, 'cp-planet c']) : ''}
  <circle cx="300" cy="300" r="132" class="cp-line" fill="none"/>
  <polygon points="${pent}" class="cp-line cp-strong" fill="none"/>
  <polygon points="${star}" class="cp-line cp-star" fill="none"/>
  ${nodes}
  <circle cx="300" cy="300" r="40" class="cp-line cp-strong" fill="var(--cp-fill, transparent)"/>
  <g class="cp-needle"><path d="M300 262L309 300L300 338L291 300Z" class="cp-cinnabar"/><path d="M300 262L309 300L291 300Z" class="cp-needle-hi"/></g>
  <circle cx="300" cy="300" r="4" class="cp-pin"/>
</svg>`;
}

// Brand mark: a simplified compass — outer ring with 12 ticks, an offset celestial orbit and a cinnabar needle.
export function brandMark(size = 34) {
  const ticks = Array.from({ length: 12 }, (_, i) => { const [x1, y1] = pt(290, i * 30), [x2, y2] = pt(i % 3 === 0 ? 236 : 260, i * 30); return `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}"/>`; }).join('');
  return `<svg class="brand-mark" width="${size}" height="${size}" viewBox="0 0 600 600" aria-hidden="true">
    <circle cx="300" cy="300" r="288" fill="none" stroke="currentColor" stroke-width="22"/>
    <g stroke="currentColor" stroke-width="16" stroke-linecap="round">${ticks}</g>
    <ellipse cx="300" cy="300" rx="196" ry="86" transform="rotate(-32 300 300)" fill="none" stroke="currentColor" stroke-width="14" opacity=".55"/>
    <path d="M300 150L336 300L300 450L264 300Z" fill="var(--cinnabar)"/>
    <circle cx="300" cy="300" r="16" fill="var(--ivory)"/>
  </svg>`;
}
