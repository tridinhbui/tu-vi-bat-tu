// Chart tables: positions, house cusps, aspects (list + grid), essential dignities and the chart's structure (sect, lots,
// dispositors, receptions, patterns, stelliums, element/modality counts). Formatting only.
import { esc } from '../util.js';
import { bodyName, bodyLabel, bodyGlyph, bodyShort, signLabel, aspName, aspGlyph, posFull, num, dm, PLANETS10, CLASSICAL,
  HOUSE_SYS, DIGNITY, SOLAR, ASPECT, PATTERN, RECEPTION, ELEMENT, MODALITY, HEMI, MOON_PHASE, fmtDate } from './vocab.js';
import { speedText, stationText } from './detail.js';

const pickBtn = (sel, html) => `<button type="button" class="wt-rowbtn" data-pick="${sel}">${html}</button>`;
const tbl = (head, rows, cls = '') => `<div class="tbl-wrap"><table class="tbl wt-tbl ${cls}"><thead><tr>${head.map(h => `<th scope="col">${h}</th>`).join('')}</tr></thead><tbody>${rows.join('')}</tbody></table></div>`;

export function positionsTable(ch, title = '') {
  const known = !!ch.angles, sys = ch.houses?.system;
  const ids = [...PLANETS10, 'chiron'];
  const rows = ids.filter(id => ch.bodies?.[id]).map(id => {
    const p = ch.bodies[id], c = ch.conditions?.[id];
    return `<tr><th scope="row">${pickBtn('planet:' + id, bodyLabel(id))}</th><td>${posFull(p)}</td>${known ? `<td>${p.house ?? '—'}</td><td>${p.house_ws ?? '—'}</td>` : ''}`
      + `<td>${num(p.speed, 3)}°${c?.station_days != null ? `<small>${stationText(c.station_days)}</small>` : ''}</td><td>${p.retrograde ? '<b class="wt-rx">R</b> <span class="sr-only">nghịch hành</span>' : ''}</td>`
      + `<td>${num(p.lat, 2)}°</td><td>${num(p.dec, 2)}°</td></tr>`;
  });
  const extra = [];
  for (const id of ['north_node', 'south_node']) if (ch.points?.[id]) extra.push([id, ch.points[id]]);
  if (ch.lots) for (const id of ['fortune', 'spirit']) extra.push([id, ch.lots[id]]);
  if (ch.angles) for (const id of ['asc', 'mc', 'dsc', 'ic']) extra.push([id, ch.angles[id]]);
  extra.forEach(([id, p]) => rows.push(`<tr class="wt-pt"><th scope="row">${pickBtn('planet:' + id, bodyLabel(id))}</th><td>${posFull(p)}</td>${known ? `<td>${p.house ?? '—'}</td><td>${p.house_ws ?? '—'}</td>` : ''}<td>${p.speed != null ? num(p.speed, 3) + '°' : ''}</td><td>${p.retrograde ? '<b class="wt-rx">R</b>' : ''}</td><td></td><td></td></tr>`));
  return (title ? `<h3 class="wt-th">${title}</h3>` : '')
    + tbl(['Thiên thể', 'Vị trí', ...(known ? [`Nhà <small>${esc(HOUSE_SYS[sys] || '')}</small>`, 'Nhà <small>Whole Sign</small>'] : []), 'Tốc độ /ngày', 'R', 'Hoàng vĩ', 'Xích vĩ'], rows)
    + (ch.bodies?.moon && ch.moon_day_range ? `<p class="hint">Mặt Trăng trong ngày sinh đi từ ${posFull(ch.moon_day_range.start)} đến ${posFull(ch.moon_day_range.end)}${ch.moon_day_range.changes_sign ? ', <b>có đổi cung</b>' : ''}; vị trí trong bảng chỉ là một điểm trong khoảng đó.</p>` : '');
}

/** Simple positions of an outer set (transit chart, progressed, solar return relation). */
export function outerTable(label, bodies, { natalHouse = false } = {}) {
  const rows = Object.entries(bodies).map(([id, p]) => `<tr><th scope="row">${pickBtn('outer:' + id, bodyLabel(id))}</th><td>${posFull(p)}</td>${natalHouse ? `<td>${p.natal_house ?? '—'}</td>` : ''}<td>${p.speed != null ? num(p.speed, 3) + '°' : ''}</td><td>${p.retrograde ? '<b class="wt-rx">R</b>' : ''}</td></tr>`);
  return `<h3 class="wt-th">${esc(label)}</h3>` + tbl(['Thiên thể', 'Vị trí', ...(natalHouse ? ['Nhà gốc'] : []), 'Tốc độ /ngày', 'R'], rows);
}

export function cuspsTable(ch) {
  if (!ch.houses) return '<p class="note">Không có giờ sinh nên không có đỉnh nhà.</p>';
  const sys = ch.houses.system, sets = ch.houses.cusps;
  const opts = Object.keys(HOUSE_SYS).map(k => `<option value="${k}"${k === sys ? ' selected' : ''}${sets[k] ? '' : ' disabled'}>${esc(HOUSE_SYS[k])}${sets[k] ? '' : ' (không xác định ở vĩ độ này)'}</option>`).join('');
  const rows = (sets[sys] || []).map((c, i) => {
    const r = (ch.house_rulers || []).find(h => h.house === i + 1);
    return `<tr><th scope="row">${pickBtn('house:' + (i + 1), `Nhà ${i + 1}`)}</th><td>${posFull(c)}</td><td>${r ? `${bodyLabel(r.ruler)}${r.modern_ruler && r.modern_ruler !== r.ruler ? ` <small>(hiện đại: ${esc(bodyShort(r.modern_ruler))})</small>` : ''}` : ''}</td><td>${r ? `${signLabel(r.ruler_sign)} · Nhà ${r.ruler_house}` : ''}</td></tr>`;
  });
  return `<div class="wt-tctl"><label class="fld"><span>Hệ nhà</span><div class="sel"><select id="wt-cusp-sys">${opts}</select></div></label>`
    + `<p class="hint">Đổi hệ nhà sẽ lập lại bản đồ (vị trí nhà của mọi thiên thể đổi theo).${ch.houses.requested !== sys ? ` Bạn chọn ${esc(HOUSE_SYS[ch.houses.requested])}, nhưng hệ này không xác định ở vĩ độ nơi sinh nên đang dùng ${esc(HOUSE_SYS[sys])}.` : ''}</p></div>`
    + tbl(['Nhà', 'Đỉnh nhà', 'Chủ nhà', 'Chủ nhà đang ở'], rows);
}

const ASP_SORT = { orb: (a, b) => a.orb - b.orb, body: (a, b) => a.ka - b.ka || a.orb - b.orb, type: (a, b) => a.kt - b.kt || a.orb - b.orb };
const ORDER = [...PLANETS10, 'chiron', 'north_node', 'asc', 'mc', 'fortune'];
const TYPES = Object.keys(ASPECT);
export function aspectsList(ch, sort = 'orb') {
  const items = (ch.aspects || []).map((a, i) => ({ ...a, i, ka: ORDER.indexOf(a.a) * 100 + ORDER.indexOf(a.b), kt: TYPES.indexOf(a.type) })).sort(ASP_SORT[sort] || ASP_SORT.orb);
  const th = (k, t) => `<button type="button" class="wt-sort" data-sort="${k}" aria-pressed="${sort === k}">${t}</button>`;
  const rows = items.map(a => `<tr class="tone-${ASPECT[a.type]?.tone || 'soft'}${ASPECT[a.type]?.major ? '' : ' minor'}"><th scope="row">${pickBtn('aspect:' + a.i, `${bodyLabel(a.a)} <span class="wt-ag" aria-hidden="true">${aspGlyph(a.type)}</span> ${bodyLabel(a.b)}`)}</th>`
    + `<td>${esc(aspName(a.type))} <small>${a.angle}°</small></td><td>${dm(a.orb)}<small> / ${dm(a.max_orb)}</small></td><td>${a.applying === true ? 'tiến lại' : a.applying === false ? 'tách ra' : '—'}</td></tr>`);
  return `<div class="wt-sorts" role="group" aria-label="Sắp xếp góc hợp">Sắp xếp: ${th('orb', 'theo orb')}${th('body', 'theo thiên thể')}${th('type', 'theo loại góc')}</div>`
    + (rows.length ? tbl(['Cặp', 'Góc hợp', 'Orb', 'Chiều'], rows, 'wt-asp-tbl') : '<p class="note">Không có góc hợp nào trong orb đang dùng.</p>');
}

export function aspectsGrid(ch) {
  const ids = ORDER.filter(id => id !== 'fortune' && (ch.bodies?.[id] || ch.points?.[id] || ch.angles?.[id]));
  const find = (x, y) => (ch.aspects || []).findIndex(a => (a.a === x && a.b === y) || (a.a === y && a.b === x));
  let h = '<div class="tbl-wrap wt-grid-wrap"><table class="wt-grid" aria-label="Lưới góc hợp"><tbody>';
  ids.forEach((r, ri) => {
    h += `<tr><th scope="row" title="${esc(bodyName(r))}"><span class="wt-g" aria-hidden="true">${bodyGlyph(r)}</span><span class="sr-only">${esc(bodyName(r))}</span></th>`;
    for (let ci = 0; ci < ri; ci++) {
      const c = ids[ci], i = find(r, c), a = ch.aspects?.[i];
      h += a ? `<td class="tone-${ASPECT[a.type]?.tone}${ASPECT[a.type]?.major ? '' : ' minor'}"><button type="button" data-pick="aspect:${i}" aria-label="${esc(bodyName(r))} ${esc(aspName(a.type))} ${esc(bodyName(c))}, orb ${dm(a.orb)}"><span aria-hidden="true">${aspGlyph(a.type)}</span><small aria-hidden="true">${dm(a.orb)}</small></button></td>` : '<td></td>';
    }
    h += `<td class="wt-diag" title="${esc(bodyName(r))}" aria-hidden="true">${bodyGlyph(r)}</td></tr>`;
  });
  return h + '</tbody></table></div>';
}

export function dignityTable(ch) {
  const n = id => id ? `<span title="${esc(bodyName(id))}">${bodyGlyph(id)}</span>` : '—';
  const rows = CLASSICAL.map(id => {
    const e = ch.conditions?.[id]?.essential; if (!e) return '';
    const L = e.lords, s = ch.conditions[id].solar;
    const mark = k => (e.has || []).includes(k) ? ' class="wt-has"' : '';
    return `<tr><th scope="row">${pickBtn('planet:' + id, bodyLabel(id))}</th><td>${signLabel(ch.bodies[id].sign)}</td>`
      + `<td${mark('domicile')}>${n(L.domicile)}</td><td${mark('exaltation')}>${n(L.exaltation)}</td>`
      + `<td${mark('triplicity')}>${(L.triplicity || []).map(n).join(' ')}</td><td${mark('term')}>${n(L.term)}</td><td${mark('face')}>${n(L.face)}</td>`
      + `<td>${[...(e.has || []).map(k => DIGNITY[k]?.split(' (')[0] || k)].join(', ') || '—'}</td>`
      + `<td>${[...(e.debilities || []).map(k => DIGNITY[k]?.split(' (')[0] || k), e.peregrine ? 'Lưu lạc' : ''].filter(Boolean).join(', ') || '—'}</td>`
      + `<td class="num">${num(e.score, 0)}</td><td>${s?.phase ? esc(SOLAR[s.phase].split(' (')[0]) : ''}</td></tr>`;
  });
  const o = ch.options || {};
  return tbl(['Hành tinh', 'Cung', 'Chủ quản', 'Vượng', 'Tam phương', 'Giới', 'Diện', 'Có', 'Bất lợi', 'Điểm', 'Pha Mặt Trời'], rows, 'wt-dig')
    + `<p class="hint">Ký hiệu trong ô là chủ tước vị của độ mà hành tinh đứng; ô tô đậm là tước vị chính hành tinh đó đang có. Tam phương theo ${o.triplicity === 'ptolemaic' ? 'Ptolemy' : 'Dorotheus'}, giới theo bảng ${o.terms === 'ptolemaic' ? 'Ptolemy' : 'Ai Cập'}. Điểm cộng trừ theo thang của Lilly (Christian Astrology), do máy chủ tính.</p>`;
}

const LOT_RULE = { ptolemy: 'Một công thức cho cả ngày lẫn đêm (Ptolemy, Tetrabiblos III.10).', sect: 'Công thức đảo cho bản đồ ban đêm (theo phe).', valens: 'Theo Valens: đảo khi sinh ban đêm và Mặt Trăng ở trên đường chân trời.' };
const list = ids => ids?.length ? ids.map(id => `<button type="button" class="link" data-pick="planet:${id}">${bodyLabel(id)}</button>`).join(', ') : '—';
export function structureHtml(ch) {
  const b = [];
  if (ch.sect) {
    const s = ch.sect;
    b.push(card('Phe (sect)', `<p>${s.is_day ? 'Bản đồ <b>ban ngày</b>' : 'Bản đồ <b>ban đêm</b>'}: Mặt Trời ở độ cao ${num(s.sun_altitude, 1)}°${s.borderline ? ' (sát đường chân trời, nên kiểm tra lại giờ sinh)' : ''}.</p>`
      + `<dl class="wt-dl">${kv('Thiên thể chủ phe', list([s.light]))}${kv('Cát tinh cùng phe', list([s.benefic_of_sect]))}${kv('Hung tinh cùng phe', list([s.malefic_of_sect]))}${kv('Cát tinh khác phe', list([s.benefic_contrary]))}${kv('Hung tinh khác phe', list([s.malefic_contrary]))}${kv('Sao Thủy', s.mercury_sect === 'diurnal' ? 'theo phe ngày' : 'theo phe đêm')}</dl>`));
  }
  if (ch.lots) {
    const l = ch.lots;
    b.push(card('Các Điểm (lot)', `<dl class="wt-dl">${['fortune', 'spirit'].map(k => kv(`<button type="button" class="link" data-pick="planet:${k}">${bodyLabel(k)}</button>`, `${posFull(l[k])} · Nhà ${l[k].house} <small>${esc(l[k].formula)}</small>`)).join('')}</dl>`
      + `<p class="hint">${LOT_RULE[l.rule] || ''}${l.moon_altitude != null ? ` Mặt Trăng ở độ cao ${num(l.moon_altitude, 1)}°.` : ''}</p>`));
  }
  const d = ch.dispositors;
  if (d) b.push(card('Chuỗi chủ quản (dispositor)', `<ul class="wt-chain">${Object.entries(d.chains).map(([k, c]) => `<li>${c.map(x => `<span title="${esc(bodyName(x))}">${bodyGlyph(x)}</span>`).join(' → ')}<span class="sr-only">${c.map(bodyName).join(' đến ')}</span></li>`).join('')}</ul>`
    + `<p>${d.final ? `Chủ quản cuối cùng: ${list([d.final])}.` : 'Không có một chủ quản cuối cùng duy nhất.'}${d.mutual_loops?.length ? ` Vòng tương hỗ: ${d.mutual_loops.map(p => p.map(bodyName).join(' ⇄ ')).join('; ')}.` : ''}</p>`
    + `<p class="hint">Theo chủ quản ${d.scheme === 'modern' ? 'hiện đại' : 'truyền thống (bảy hành tinh)'}.</p>`));
  b.push(card('Tiếp nhận tương hỗ (mutual reception)', ch.receptions?.length ? `<ul class="plain">${ch.receptions.map(r => `<li>${list([r.a])} và ${list([r.b])}: ${esc(RECEPTION[r.by] || r.by)}</li>`).join('')}</ul>` : '<p>Không có cặp tiếp nhận tương hỗ nào giữa bảy hành tinh cổ điển.</p>'));
  const pats = [...(ch.patterns || []).map(p => `<li><b>${esc(PATTERN[p.type] || p.type)}</b>: ${list(p.bodies)}${p.apex ? ` · đỉnh ${esc(bodyName(p.apex))}` : ''}</li>`),
    ...(ch.stelliums || []).map(s => `<li><b>${esc(PATTERN.stellium)}</b> ${s.by === 'sign' ? `ở ${signLabel(s.where)}` : `ở Nhà ${s.where}`}: ${list(s.bodies)}</li>`)];
  b.push(card('Hình thể và tụ hội', pats.length ? `<ul class="plain">${pats.join('')}</ul>` : '<p>Không có hình thể nhiều hành tinh nào trong orb đang dùng.</p>'));
  const bal = ch.balance;
  if (bal) {
    const grp = (o, names) => `<dl class="wt-dl wt-bal">${Object.entries(o).map(([k, v]) => kv(`${esc(names[k] || k)} <b class="wt-cnt">${v.length}</b>`, v.length ? v.map(x => `<span title="${esc(bodyName(x))}">${bodyGlyph(x)}</span>`).join(' ') : '—')).join('')}</dl>`;
    b.push(card('Nguyên tố, tính chất, bán cầu', `<h4 class="wt-dsub">Nguyên tố</h4>${grp(bal.element, ELEMENT)}<h4 class="wt-dsub">Tính chất</h4>${grp(bal.modality, MODALITY)}${bal.hemisphere ? `<h4 class="wt-dsub">Bán cầu</h4>${grp(bal.hemisphere, HEMI)}` : ''}<p class="hint">Đếm mười hành tinh, không gán trọng số.</p>`));
  }
  if (ch.moon_phase) b.push(card('Pha Mặt Trăng', `<p>${esc(MOON_PHASE[ch.moon_phase.phase] || ch.moon_phase.phase)} · ${ch.moon_phase.waxing ? 'trăng đang tròn dần' : 'trăng đang khuyết dần'} · độ sáng ${num(ch.moon_phase.illumination * 100, 1)}% · cách Mặt Trời ${num(ch.moon_phase.elongation, 1)}°</p>`));
  return `<div class="wt-cards">${b.join('')}</div>`;
}
const kv = (k, v) => `<div class="wt-kv"><dt>${k}</dt><dd>${v}</dd></div>`;
const card = (t, body) => `<section class="wt-card"><h3 class="wt-th">${t}</h3>${body}</section>`;

/** Solar Return relation facts. */
export function srRelation(sr) {
  const r = sr.relation || {}, ch = sr.chart;
  const houses = Object.entries(r.sr_planets_in_natal_houses || {}).map(([id, h]) => `<li>${bodyLabel(id)} → Nhà ${h} gốc</li>`).join('');
  return `<div class="wt-cards"><section class="wt-card"><h3 class="wt-th">Thời điểm trở về</h3><dl class="wt-dl">`
    + kv('Mặt Trời trở về đúng vị trí gốc', `${esc(fmtLocal(sr.exact_utc, sr.place?.tz))} <small>(${esc(sr.place?.tz || '')}; sai số ${num(sr.sun_error_arcsec, 3)}″)</small>`)
    + kv('Nơi lập', esc(sr.place?.name || `${num(sr.place?.lat, 3)}°, ${num(sr.place?.lon, 3)}°`))
    + (ch?.angles ? kv('Cung Mọc Solar Return', posFull(ch.angles.asc)) : '')
    + (r.sr_asc_in_natal_house ? kv('Cung Mọc SR rơi vào', `Nhà ${r.sr_asc_in_natal_house} gốc`) : '')
    + (r.natal_asc_in_sr_house ? kv('Cung Mọc gốc rơi vào', `Nhà ${r.natal_asc_in_sr_house} của SR`) : '')
    + `</dl></section><section class="wt-card"><h3 class="wt-th">Hành tinh SR trong các nhà gốc</h3><ul class="plain wt-cols">${houses}</ul></section>`
    + `<section class="wt-card"><h3 class="wt-th">Trục SR trùng hành tinh gốc</h3>${r.sr_angles_on_natal_planets?.length ? `<ul class="plain">${r.sr_angles_on_natal_planets.map(x => `<li>${esc(x.sr_angle.toUpperCase())} của SR trùng ${bodyLabel(x.natal)} gốc · orb ${dm(x.orb)}</li>`).join('')}</ul>` : '<p>Không có trục nào của SR nằm sát một hành tinh gốc.</p>'}</section></div>`;
}
const fmtLocal = (iso, tz) => fmtDate(iso, tz, { time: true });
export { speedText };
