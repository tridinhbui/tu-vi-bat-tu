// Detail panel beside the wheel: what was tapped (a planet, a house sector, an aspect line, a sign) and the chart facts behind it.
// Only reads the chart JSON; every degree, orb and lord is the engine's.
import { esc } from '../util.js';
import { bodyName, bodyLabel, bodyGlyph, signLabel, signName, aspName, aspGlyph, posFull, num, dm, fmtDate,
  DIGNITY, SOLAR, HOUSE_SYS, ASPECT, TONE, SIGN, ELEMENT, MODALITY } from './vocab.js';

const row = (k, v) => v == null || v === '' ? '' : `<div class="wt-kv"><dt>${k}</dt><dd>${v}</dd></div>`;
const dl = rows => `<dl class="wt-dl">${rows.join('')}</dl>`;
const ptOf = (ch, id) => ch.bodies?.[id] || ch.points?.[id] || ch.angles?.[id] || ch.lots?.[id];

/** A button that selects an aspect on the wheel (event delegation in main.js through data-pick). */
export const aspBtn = (ch, a, i, self = null) => {
  const other = self ? (a.a === self ? a.b : a.a) : null;
  const who = other ? bodyLabel(other) : `${bodyLabel(a.a)} – ${bodyLabel(a.b)}`;
  return `<button type="button" class="wt-ab tone-${ASPECT[a.type]?.tone || 'soft'}" data-pick="aspect:${i}"><span class="wt-g" aria-hidden="true">${aspGlyph(a.type)}</span> ${esc(aspName(a.type))} ${who}<small>orb ${dm(a.orb)}</small></button>`;
};

export function speedText(p, cond) {
  if (p?.speed == null) return '';
  let t = `${num(p.speed, 3)}°/ngày`;
  if (cond?.speed_ratio != null) t += ` · ${cond.speed_ratio >= 1 ? 'nhanh hơn' : 'chậm hơn'} mức trung bình của chính nó (×${num(cond.speed_ratio, 2)})`;
  return t;
}
export function stationText(d) {
  if (d == null) return '';
  return d < 0 ? `đổi chiều (station) cách đây ${num(-d, 1)} ngày` : `sẽ đổi chiều (station) sau ${num(d, 1)} ngày`;
}
export function solarText(s) {
  if (!s) return '';
  const ph = s.phase ? SOLAR[s.phase] || s.phase : 'Không trong vùng tia Mặt Trời';
  return `${ph} · cách Mặt Trời ${dm(s.distance)} · ${s.oriental ? 'phương Đông (mọc trước Mặt Trời)' : 'phương Tây (lặn sau Mặt Trời)'}`;
}
export function lordsText(e) {
  if (!e?.lords) return '';
  const L = e.lords, n = id => id ? esc(bodyName(id)) : '—';
  return dl([
    row(DIGNITY.domicile, n(L.domicile)), row(DIGNITY.exaltation, n(L.exaltation)),
    row(DIGNITY.triplicity, (L.triplicity || []).map(n).join(', ') + (L.triplicity_ruler ? ` <small>(đang nắm: ${n(L.triplicity_ruler)})</small>` : '')),
    row(DIGNITY.term, n(L.term)), row(DIGNITY.face, n(L.face)),
  ]);
}

function planet(ch, id) {
  const p = ptOf(ch, id); if (!p) return '';
  const c = ch.conditions?.[id], e = c?.essential, sys = ch.houses?.system;
  const asp = (ch.aspects || []).map((a, i) => [a, i]).filter(([a]) => a.a === id || a.b === id);
  const rules = (ch.house_rulers || []).filter(h => h.ruler === id).map(h => h.house);
  const has = e ? [...(e.has || []).map(k => DIGNITY[k] || k), ...(e.debilities || []).map(k => DIGNITY[k] || k), e.peregrine ? DIGNITY.peregrine : null].filter(Boolean) : [];
  return `<h3 class="wt-dh"><span class="wt-g big" aria-hidden="true">${bodyGlyph(id)}</span>${esc(bodyName(id))}</h3>`
    + dl([
      row('Vị trí', posFull(p)),
      row('Nhà', p.house ? `Nhà ${p.house} <small>(${esc(HOUSE_SYS[sys] || sys)})</small>${p.house_ws && p.house_ws !== p.house ? ` · Nhà ${p.house_ws} theo Whole Sign` : ''}` : ''),
      row('Chuyển động', [speedText(p, c), c?.retrograde || p.retrograde ? '<b>Nghịch hành (R)</b>' : '', stationText(c?.station_days)].filter(Boolean).join('<br>')),
      row('Pha với Mặt Trời', solarText(c?.solar)),
      row('Tước vị', e ? `${has.length ? esc(has.join(', ')) : 'Không có tước vị riêng ở độ này'} ${c?.lilly ? ` · điểm Lilly ${num(c.lilly.score, 0)} <small>(tính trên bảng của Lilly)</small>` : ''}` : ''),
      row('Cai quản', rules.length ? rules.map(n => `<button type="button" class="link" data-pick="house:${n}">Nhà ${n}</button>`).join(', ') : ''),
      row('Hoàng vĩ · xích vĩ', p.lat != null ? `${num(p.lat, 2)}° · ${num(p.dec, 2)}°` : ''),
      row('Công thức', p.formula ? esc(p.formula) : ''),
    ])
    + (e?.lords ? `<h4 class="wt-dsub">Chủ các tước vị ở độ này</h4>${lordsText(e)}` : '')
    + `<h4 class="wt-dsub">Góc hợp (${asp.length})</h4>`
    + (asp.length ? `<div class="wt-abs">${asp.sort((x, y) => x[0].orb - y[0].orb).map(([a, i]) => aspBtn(ch, a, i, id)).join('')}</div>` : '<p class="hint">Không có góc hợp nào trong orb đang dùng.</p>');
}

function house(ch, n) {
  const sys = ch.houses?.system, c = ch.houses?.cusps?.[sys]?.[n - 1]; if (!c) return '';
  const r = (ch.house_rulers || []).find(h => h.house === n);
  const inside = Object.entries({ ...ch.bodies, ...ch.points, ...(ch.lots ? { fortune: ch.lots.fortune, spirit: ch.lots.spirit } : {}) })
    .filter(([, p]) => p?.house === n).map(([id]) => `<button type="button" class="link" data-pick="planet:${id}">${bodyLabel(id)}</button>`);
  return `<h3 class="wt-dh"><span class="wt-hnum" aria-hidden="true">${n}</span>Nhà ${n}</h3>`
    + dl([
      row('Đỉnh nhà', `${posFull(c)} <small>(${esc(HOUSE_SYS[sys] || sys)})</small>`),
      row('Chủ nhà', r ? `<button type="button" class="link" data-pick="planet:${r.ruler}">${bodyLabel(r.ruler)}</button>${r.modern_ruler && r.modern_ruler !== r.ruler ? ` <small>(hiện đại: ${esc(bodyName(r.modern_ruler))})</small>` : ''}` : ''),
      row('Chủ nhà đang ở', r ? `${signLabel(r.ruler_sign)}, Nhà ${r.ruler_house}` : ''),
      row('Whole Sign', r ? `${signLabel(r.ws_sign)} · chủ ${esc(bodyName(r.ws_ruler))}` : ''),
      row('Trong nhà', inside.length ? inside.join(', ') : 'Không có thiên thể nào'),
    ]);
}

function aspect(ch, i) {
  const a = ch.aspects?.[i]; if (!a) return '';
  const k = ASPECT[a.type] || {};
  return `<h3 class="wt-dh"><span class="wt-g big" aria-hidden="true">${aspGlyph(a.type)}</span>${esc(aspName(a.type))}</h3>`
    + `<p class="wt-dpair"><button type="button" class="link" data-pick="planet:${a.a}">${bodyLabel(a.a)}</button> và <button type="button" class="link" data-pick="planet:${a.b}">${bodyLabel(a.b)}</button></p>`
    + dl([
      row('Góc chuẩn', `${a.angle}° · ${k.major ? 'góc hợp chính' : 'góc hợp phụ'} · nét vẽ kiểu ${TONE[k.tone] || ''}`),
      row('Orb', `${dm(a.orb)} <small>(giới hạn ${dm(a.max_orb)}; độ chính xác ${num(a.exactness * 100, 0)}%)</small>`),
      row('Chiều', a.applying === true ? 'Đang tiến lại gần (applying)' : a.applying === false ? 'Đang tách ra (separating)' : 'Không xét (có một điểm trục tham gia)'),
      row('Theo cung', a.whole_sign ? 'Cũng đúng số cung cách nhau (góc hợp theo cung)' : 'Không đúng số cung (góc hợp vượt ranh giới cung)'),
    ]);
}

function sign(ch, id) {
  const s = SIGN[id]; if (!s) return '';
  const inside = Object.entries({ ...ch.bodies, ...ch.points }).filter(([, p]) => p?.sign === id)
    .map(([b]) => `<button type="button" class="link" data-pick="planet:${b}">${bodyLabel(b)}</button>`);
  return `<h3 class="wt-dh"><span class="wt-g big" aria-hidden="true">${s.g}</span>${esc(s.vi)}</h3>`
    + dl([row('Nguyên tố', ELEMENT[s.el]), row('Tính chất', MODALITY[['cardinal', 'fixed', 'mutable'][s.i % 3]]), row('Độ hoàng đạo', `${s.i * 30}°–${s.i * 30 + 30}°`),
      row('Trong cung', inside.length ? inside.join(', ') : 'Không có thiên thể nào')]);
}

/** Outer ring of a bi-wheel: transit or progressed positions, plus the links to natal points. */
function outer(ctx, id) {
  const o = ctx.outer, p = o?.bodies?.[id]; if (!p) return '';
  const links = (o.links || []).map((l, i) => [l, i]).filter(([l]) => l.a === id);
  return `<h3 class="wt-dh"><span class="wt-g big" aria-hidden="true">${bodyGlyph(id)}</span>${esc(bodyName(id))} <small>${esc(o.label)}</small></h3>`
    + dl([row('Vị trí', posFull(p)), row(o.houseLabel || 'Nhà của bản đồ gốc', p.natal_house ? `Nhà ${p.natal_house}` : ''),
      row('Chuyển động', [p.speed != null ? `${num(p.speed, 3)}°/ngày` : '', p.retrograde ? '<b>Nghịch hành (R)</b>' : ''].filter(Boolean).join(' · '))])
    + (o.links ? `<h4 class="wt-dsub">${esc(o.linkTitle || 'Góc hợp với bản đồ gốc lúc này')} (${links.length})</h4>` + (links.length
      ? `<div class="wt-abs">${links.map(([l, i]) => `<button type="button" class="wt-ab tone-${ASPECT[l.type]?.tone}" data-pick="link:${i}"><span class="wt-g" aria-hidden="true">${aspGlyph(l.type)}</span> ${esc(aspName(l.type))} ${bodyLabel(l.b)} ${esc(o.innerTag ?? 'gốc')}</button>`).join('')}</div>`
      : `<p class="hint">${esc(o.noLinks || 'Không có góc hợp nào trong orb transit lúc này.')}</p>`) : '');
}

function link(ctx, i) {
  const l = ctx.outer?.links?.[i]; if (!l) return '';
  if (!l.event) { // synastry: point of B (outer) to point of A (inner)
    const o = ctx.outer;
    return `<h3 class="wt-dh"><span class="wt-g big" aria-hidden="true">${aspGlyph(l.type)}</span>${esc(aspName(l.type))}</h3>`
      + dl([row(esc(o.innerName || 'Bản đồ trong'), `<button type="button" class="link" data-pick="planet:${l.b}">${bodyLabel(l.b)}</button> ${posFull(ptOf(ctx.chart, l.b))}`),
        row(esc(o.outerName || 'Bản đồ ngoài'), `<button type="button" class="link" data-pick="outer:${l.a}">${bodyLabel(l.a)}</button> ${posFull(o.bodies[l.a] || o.points?.[l.a])}`),
        row('Orb', `${dm(l.orb)} <small>(giới hạn ${dm(l.max_orb)})</small>`)]);
  }
  const tz = ctx.tz, e = l.event;
  return `<h3 class="wt-dh"><span class="wt-g big" aria-hidden="true">${aspGlyph(l.type)}</span>${esc(bodyName(l.a))} ${esc(aspName(l.type))} ${esc(bodyName(l.b))} gốc</h3>`
    + dl([
      row('Vào orb', e.start ? fmtDate(e.start, tz, { time: true }) : `trước ${fmtDate(e.win?.[0], tz)}`),
      row('Chính xác', e.exact.map((x, k) => fmtDate(x, tz, { time: true }) + (e.retro_at_exact[k] ? ' <small>(lúc nghịch hành)</small>' : '')).join('<br>') || `không có trong khoảng ${fmtDate(e.win?.[0], tz)} – ${fmtDate(e.win?.[1], tz)}`),
      row('Ra khỏi orb', e.end ? fmtDate(e.end, tz, { time: true }) : `sau ${fmtDate(e.win?.[1], tz)}`),
      row('Orb transit', `${dm(e.orb)} <small>(quy ước Thiên Bàn)</small>`),
    ]) + `<p class="hint">Giờ theo múi ${esc(tz)}.</p>`;
}

/** Two natal points named together by a reading paragraph whose aspect is not in the natal list (orb, sign-based, or a transit). */
function pair(ch, a, b, type) {
  const pa = ptOf(ch, a), pb = ptOf(ch, b); if (!pa || !pb) return '';
  return `<h3 class="wt-dh">${ASPECT[type] ? `<span class="wt-g big" aria-hidden="true">${aspGlyph(type)}</span>${esc(aspName(type))}` : 'Hai điểm'}</h3>`
    + dl([row(`<button type="button" class="link" data-pick="planet:${a}">${bodyLabel(a)}</button>`, posFull(pa)), row(`<button type="button" class="link" data-pick="planet:${b}">${bodyLabel(b)}</button>`, posFull(pb))])
    + '<p class="hint">Góc hợp này không có trong danh sách góc hợp của bản đồ gốc với orb đang dùng: đoạn luận giải tính nó theo cung, hoặc đó là một transit. Hai điểm được tô trên bánh xe là vị trí gốc.</p>';
}

/** HTML for the panel. ctx = {chart, outer, tz}. */
export function detailHtml(ctx, s) {
  const ch = ctx.chart;
  if (!s) return '';
  if (s.kind === 'planet') return planet(ch, s.id);
  if (s.kind === 'house') return house(ch, s.n);
  if (s.kind === 'pair') return pair(ch, s.a, s.b, s.type);
  if (s.kind === 'aspect') return aspect(ch, s.i);
  if (s.kind === 'sign') return sign(ch, s.id);
  if (s.kind === 'outer') return outer(ctx, s.id);
  if (s.kind === 'link') return link(ctx, s.i);
  return '';
}
export const detailEmpty = timeKnown => `<p class="wt-dempty">Chạm vào một hành tinh${timeKnown ? ', một nhà' : ''} hoặc một đường góc hợp trên bánh xe để xem chi tiết. Dùng phím Tab để đi qua từng hành tinh${timeKnown ? ' và từng nhà' : ''}.</p>`;
export { signName };
