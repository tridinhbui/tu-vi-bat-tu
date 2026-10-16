// FiveElementsDiagram — interactive, used both as an educational piece (home) and as a chart companion (results).
import { ELEMENTS, EL, esc, elIcon, elStems, elBranches, $$ } from './util.js';

const pos = (i, r = 112) => { const a = (-90 + i * 72) * Math.PI / 180; return [150 + r * Math.cos(a), 150 + r * Math.sin(a) + 6]; };

export function fiveElements(host, { counts = null, onSelect = () => {}, hint = true } = {}) {
  let mode = 'both', sel = null;
  const max = counts ? Math.max(1, ...Object.values(counts)) : 1;
  const P = ELEMENTS.map((_, i) => pos(i));
  const arc = (i, j) => { const [a, b] = [P[i], P[j]]; return `M${a[0].toFixed(1)} ${a[1].toFixed(1)}A112 112 0 0 1 ${b[0].toFixed(1)} ${b[1].toFixed(1)}`; };
  // shorten khắc lines so arrow heads clear the node circles
  const line = (i, j) => { const [a, b] = [P[i], P[j]], d = Math.hypot(b[0] - a[0], b[1] - a[1]), k = 30 / d; return `M${(a[0] + (b[0] - a[0]) * k).toFixed(1)} ${(a[1] + (b[1] - a[1]) * k).toFixed(1)}L${(b[0] - (b[0] - a[0]) * k).toFixed(1)} ${(b[1] - (b[1] - a[1]) * k).toFixed(1)}`; };
  host.innerHTML = `<div class="fe">
    <svg viewBox="0 0 300 312" class="fe-svg" role="group" aria-label="Sơ đồ ngũ hành tương sinh, tương khắc">
      <defs><marker id="fe-a" viewBox="0 0 8 8" refX="6" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8Z" fill="currentColor"/></marker></defs>
      <g class="fe-sinh" color="var(--jade)">${ELEMENTS.map((_, i) => `<path d="${arc(i, (i + 1) % 5)}" fill="none" stroke="currentColor" stroke-width="1.6" marker-end="url(#fe-a)" data-from="${i}" data-to="${(i + 1) % 5}"/>`).join('')}</g>
      <g class="fe-khac" color="var(--cinnabar)">${ELEMENTS.map((_, i) => `<path d="${line(i, (i + 2) % 5)}" stroke="currentColor" stroke-width="1.3" stroke-dasharray="4 4" marker-end="url(#fe-a)" data-from="${i}" data-to="${(i + 2) % 5}"/>`).join('')}</g>
      ${ELEMENTS.map((e, i) => { const [x, y] = P[i], c = counts ? counts[e] : null, r = 24 + (c != null ? (c / max) * 8 : 4);
        return `<g class="fe-node el-${EL[e].slug}" data-el="${e}" tabindex="0" role="button" aria-pressed="false" aria-label="${e}${c != null ? ', ' + c + ' vị trí' : ''}">
          <circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r}" class="fe-disc"/><circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r + 5}" class="fe-ring"/>
          <text x="${x.toFixed(1)}" y="${(y - 3).toFixed(1)}" class="fe-han" lang="zh" text-anchor="middle" dominant-baseline="central">${EL[e].h}</text>
          <text x="${x.toFixed(1)}" y="${(y + 15).toFixed(1)}" class="fe-name" text-anchor="middle">${e}${c != null ? ' · ' + c : ''}</text></g>`; }).join('')}
      <text x="150" y="156" class="fe-center" text-anchor="middle">NGŨ HÀNH</text>
    </svg>
    <div class="fe-side">
      <div class="seg" role="group" aria-label="Kiểu quan hệ">
        <button type="button" data-m="both" aria-pressed="true">Cả hai</button><button type="button" data-m="sinh" aria-pressed="false">Tương sinh</button><button type="button" data-m="khac" aria-pressed="false">Tương khắc</button></div>
      <div class="fe-legend"><span><i class="ln sinh"></i>Sinh (liền nét)</span><span><i class="ln khac"></i>Khắc (nét đứt)</span></div>
      <div class="fe-detail" aria-live="polite"></div>
    </div></div>`;
  const detail = host.querySelector('.fe-detail');
  const setMode = m => { mode = m; host.querySelector('.fe-sinh').style.opacity = m === 'khac' ? .08 : 1; host.querySelector('.fe-khac').style.opacity = m === 'sinh' ? .08 : 1;
    $$('.seg button', host).forEach(b => b.setAttribute('aria-pressed', b.dataset.m === m)); };
  const show = e => {
    sel = sel === e ? null : e;
    $$('.fe-node', host).forEach(n => { const on = n.dataset.el === sel; n.classList.toggle('on', on); n.setAttribute('aria-pressed', on); });
    if (!sel) { detail.innerHTML = hint ? '<p class="fe-hint">Chọn một hành để xem quan hệ sinh khắc' + (counts ? ' và các vị trí trong lá số.' : '.') + '</p>' : ''; onSelect(null); return; }
    const d = EL[sel];
    detail.innerHTML = `<h4 class="el-${d.slug}">${elIcon(sel, 16)}<span lang="zh">${d.h}</span> ${sel}</h4>
      <dl><div><dt>Sinh</dt><dd>${sel} sinh ${d.sinh}</dd></div><div><dt>Khắc</dt><dd>${sel} khắc ${d.khac}</dd></div><div><dt>Được sinh bởi</dt><dd>${d.duocSinh}</dd></div><div><dt>Bị khắc bởi</dt><dd>${d.biKhac}</dd></div>
      <div><dt>Phương · mùa</dt><dd>${d.dir} · ${d.season}</dd></div><div><dt>Thiên can</dt><dd>${elStems(sel)}</dd></div><div><dt>Địa chi</dt><dd>${elBranches(sel)}</dd></div></dl>
      ${counts ? `<p class="fe-count">Trong 8 chữ của lá số: <b>${counts[sel]}</b>. Các chữ này được đánh dấu ở bốn trụ.</p>` : ''}`;
    // emphasise the relations of this element
    const i = ELEMENTS.indexOf(sel);
    $$('.fe-sinh path,.fe-khac path', host).forEach(p => { const rel = +p.dataset.from === i || +p.dataset.to === i; p.style.opacity = rel ? 1 : .14; });
    onSelect(sel);
    if (!sel) setMode(mode);
  };
  host.querySelectorAll('.fe-node').forEach(n => { n.onclick = () => show(n.dataset.el); n.onkeydown = ev => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); show(n.dataset.el); } }; });
  host.querySelectorAll('.seg button').forEach(b => b.onclick = () => { setMode(b.dataset.m); if (sel) { const s = sel; sel = null; show(s); } });
  detail.innerHTML = hint ? '<p class="fe-hint">Chọn một hành để xem quan hệ sinh khắc' + (counts ? ' và các vị trí trong lá số.' : '.') + '</p>' : '';
  return { select: show, clear: () => { if (sel) show(sel); } };
}
