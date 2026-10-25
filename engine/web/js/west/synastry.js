// Synastry ("So sánh hai bản đồ sao"): person A is the chart on the page, person B comes from a saved profile or a second birth form.
// POST /api/west/synastry → bi-wheel (A inside, B outside, inter-aspect lines), inter-aspect table, house overlays both ways,
// Ptolemy's four places, and the engine's reading paragraphs. Every figure is the engine's.
import { $, $$, esc } from '../util.js';
import { westPost } from './api.js';
import { createWheel } from './wheel.js';
import { detailHtml, detailEmpty } from './detail.js';
import { initBirthForm, latLonTxt } from './form.js';
import { renderReading } from './reading.js';
import * as store from './store.js';
import { bodyLabel, bodyName, aspName, aspGlyph, dm, num, ASPECT, PLANETS10, hhmm } from './vocab.js';

const RELATION = { same: 'Cùng cung', sextile: 'Lục hợp', square: 'Vuông góc', trine: 'Tam hợp', opposition: 'Đối đỉnh', disjunct: 'Không nhìn thấy nhau (cách 1 hoặc 5 cung)' };
const PLACE = { sun: 'Mặt Trời', moon: 'Mặt Trăng', asc: 'Cung Mọc', lot: 'Lot of Fortune' };
const OUTER_IDS = [...PLANETS10, 'chiron', 'north_node'];
const who = b => b.name || `${String(b.day).padStart(2, '0')}/${String(b.month).padStart(2, '0')}/${b.year}`;
const when = b => `${String(b.day).padStart(2, '0')}/${String(b.month).padStart(2, '0')}/${b.year}${b.hour != null ? ' ' + hhmm(b) : ''}`;

export function initSynastry(root, { getA }) {
  const out = $('#syn-out', root), formEl = $('#syn-form', root), sel = $('#syn-prof', root);
  const S = { res: null, deep: false, sort: 'orb', wheel: null, view: null };
  const form = initBirthForm(formEl, { ids: { place: 'syn-place', list: 'syn-place-list', info: 'syn-place-info', err: 'syn-err' }, onSubmit: run });

  function refresh() {
    const A = getA(); if (!A) return;
    $('#syn-a-txt', root).innerHTML = (A.inp.birth.name ? `<b>${esc(A.inp.birth.name)}</b> · ` : '') + `${esc(when(A.inp.birth))} · ${esc(A.inp.birth.place || latLonTxt(A.inp.birth.lat, A.inp.birth.lon))} <small>(bản đồ đang mở ở trên)</small>`;
    const g = $(`[name=syn-ga][value="${A.gender || ''}"]`, root); if (g) g.checked = true;
    const pr = store.profiles(), rc = store.recent();
    sel.innerHTML = '<option value="">Chọn một hồ sơ…</option>'
      + (pr.length ? `<optgroup label="Hồ sơ đã lưu">${pr.map((p, i) => `<option value="p${i}">${esc(p.label || who(p.birth))} · ${esc(when(p.birth))}</option>`).join('')}</optgroup>` : '')
      + (rc.length ? `<optgroup label="Mở gần đây">${rc.map((p, i) => `<option value="r${i}">${esc(who(p.birth))} · ${esc(when(p.birth))}</option>`).join('')}</optgroup>` : '');
  }
  sel.onchange = () => {
    const v = sel.value; if (!v) return;
    const x = (v[0] === 'p' ? store.profiles() : store.recent())[+v.slice(1)];
    if (x) form.fill({ birth: x.birth, options: {}, gender: x.gender || null });
  };

  async function run(inpB) {
    const A = getA(); if (!A) throw new Error('Hãy lập bản đồ của người A trước.');
    const ga = $('[name=syn-ga]:checked', root)?.value || null;
    const body = { a: A.inp.birth, b: inpB.birth, options: A.inp.options };
    if (ga) body.gender_a = ga;
    if (inpB.gender) body.gender_b = inpB.gender;
    const res = await westPost('synastry', body);
    S.res = res; S.names = [who(A.inp.birth), who(inpB.birth)];
    render();
  }

  // ----- rendering -----
  function render() {
    const { a, b, synastry: sy, reading } = S.res, [na, nb] = S.names;
    const bodies = {};
    for (const id of OUTER_IDS) { const p = b.bodies?.[id] || b.points?.[id]; if (p) bodies[id] = { ...p, natal_house: sy.overlays?.b_in_a?.[id] ?? null }; }
    const links = (sy.aspects || []).map(x => ({ a: x.b, b: x.a, type: x.type, orb: x.orb, max_orb: x.max_orb }));
    S.view = { chart: a, outer: { label: `B · ${nb}`, bodies, points: b.angles ? { asc: b.angles.asc, mc: b.angles.mc } : {}, links,
      houseLabel: `Rơi vào nhà của ${na}`, linkTitle: `Góc hợp với ${na}`, innerTag: `của ${na}`, noLinks: `Không có góc hợp nào với ${na} trong orb đang dùng.`, innerName: `A · ${na}`, outerName: `B · ${nb}` } };
    out.hidden = false;
    out.innerHTML = `<div class="wt-syn-head"><p><b class="wt-syn-tag">A</b> ${esc(na)} ở vòng trong · <b class="wt-syn-tag b">B</b> ${esc(nb)} ở vòng ngoài</p></div>`
      + `<div class="wt-stage" id="syn-stage"><div class="wt-wheel-col"><div class="wt-zoom no-print" role="group" aria-label="Thu phóng bánh xe so sánh"><button type="button" data-z="out" aria-label="Thu nhỏ">−</button><button type="button" data-z="in" aria-label="Phóng to">+</button><button type="button" data-z="reset">Vừa khung</button></div><div id="syn-wheel"></div>`
      + `<p class="hint">Các đường ở giữa là góc hợp giữa một điểm của ${esc(na)} và một điểm của ${esc(nb)}; nét vẽ theo cùng quy ước với bánh xe ở trên.</p></div>`
      + `<aside class="wt-detail" id="syn-detail" aria-live="polite" aria-label="Chi tiết so sánh"></aside></div>`
      + `<div class="wt-syn-tables"><section><h3 class="wt-th">Góc hợp giữa hai người (${links.length})</h3>${aspTable(sy, na, nb)}</section>`
      + `<div class="wt-two"><section><h3 class="wt-th">Hành tinh của ${esc(na)} trong nhà của ${esc(nb)}</h3>${overlay(sy.overlays?.a_in_b, nb)}</section>`
      + `<section><h3 class="wt-th">Hành tinh của ${esc(nb)} trong nhà của ${esc(na)}</h3>${overlay(sy.overlays?.b_in_a, na)}</section></div>`
      + `<section><h3 class="wt-th">Bốn nơi theo Ptolemy (Tetrabiblos IV.7)</h3>${ptolemy(sy.ptolemy, na, nb)}</section></div>`
      + `<section class="wt-syn-read"><div class="wt-sech"><h3 class="wt-th">Luận giải so sánh</h3><div class="seg no-print" role="group" aria-label="Độ sâu luận giải so sánh"><button type="button" data-sdeep="0" aria-pressed="${!S.deep}">Tổng quan</button><button type="button" data-sdeep="1" aria-pressed="${S.deep}">Đọc sâu</button></div></div><div id="syn-reading"></div></section>`;
    S.wheel = createWheel($('#syn-wheel', out), { label: `Bánh xe so sánh: ${na} ở trong, ${nb} ở ngoài`, onSelect: s => { S.sel = s; showDetail(); } });
    S.wheel.render(S.view); S.sel = null; showDetail();
    $$('[data-z]', out).forEach(x => x.onclick = () => { const z = x.dataset.z; z === 'in' ? S.wheel.zoom(1.35) : z === 'out' ? S.wheel.zoom(1 / 1.35) : S.wheel.reset(); });
    drawReading();
    $$('[data-sdeep]', out).forEach(x => x.onclick = () => { S.deep = x.dataset.sdeep === '1'; $$('[data-sdeep]', out).forEach(y => y.setAttribute('aria-pressed', String(y === x))); drawReading(); });
    out.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    function drawReading() { renderReading($('#syn-reading', out), { chapters: [{ id: 'syn', title: '', paragraphs: reading || [] }] }, { deep: S.deep, chart: a }); }
  }
  const showDetail = () => { $('#syn-detail', out).innerHTML = (S.sel && detailHtml({ chart: S.view.chart, outer: S.view.outer, tz: 'UTC' }, S.sel)) || detailEmpty(!!S.view.chart.angles); };

  function aspTable(sy, na, nb) {
    const xs = (sy.aspects || []).map((x, i) => ({ ...x, i })).sort((p, q) => p.orb - q.orb);
    if (!xs.length) return '<p class="note">Không có góc hợp nào trong orb đang dùng.</p>';
    return `<div class="tbl-wrap"><table class="tbl wt-tbl wt-asp-tbl"><thead><tr><th scope="col">${esc(na)}</th><th scope="col">Góc hợp</th><th scope="col">${esc(nb)}</th><th scope="col">Orb</th></tr></thead><tbody>`
      + xs.map(x => `<tr class="tone-${ASPECT[x.type]?.tone || 'soft'}${ASPECT[x.type]?.major ? '' : ' minor'}"><th scope="row"><button type="button" class="wt-rowbtn" data-pick="link:${x.i}">${bodyLabel(x.a)}</button></th>`
        + `<td><span class="wt-ag" aria-hidden="true">${aspGlyph(x.type)}</span> ${esc(aspName(x.type))}</td><td>${bodyLabel(x.b)}</td><td>${dm(x.orb)}<small> / ${dm(x.max_orb)}</small></td></tr>`).join('')
      + '</tbody></table></div>';
  }
  const overlay = (m, host) => m
    ? `<div class="tbl-wrap"><table class="tbl wt-tbl"><thead><tr><th scope="col">Hành tinh</th><th scope="col">Nhà của ${esc(host)}</th></tr></thead><tbody>${Object.entries(m).map(([id, h]) => `<tr><th scope="row">${bodyLabel(id)}</th><td>Nhà ${h}</td></tr>`).join('')}</tbody></table></div>`
    : `<p class="note">Cần giờ sinh của ${esc(host)} để có các nhà.</p>`;
  function ptolemy(pt, na, nb) {
    if (!pt) return '';
    const rows = Object.entries(PLACE).map(([k, v]) => { const x = pt.places?.[k]; return `<tr><th scope="row">${v}</th><td>${x ? esc(RELATION[x.relation] || x.relation) : '<span class="muted">Cần giờ sinh của cả hai</span>'}</td><td>${x ? num(x.degrees, 1) + '°' : ''}</td></tr>`; }).join('');
    const lum = Object.entries(pt.luminaries || {}).map(([k, v]) => {
      const [p, q] = k.split('-'), nm = t => `${t.startsWith('sun') ? 'Mặt Trời' : 'Mặt Trăng'} của ${t.endsWith('_a') ? na : nb}`;
      return `<li>${esc(nm(p))} và ${esc(nm(q))}: ${esc(RELATION[v] || v)}</li>`;
    }).join('');
    const ex = (pt.exchanges || []).map(([x, y]) => `<li>${esc(bodyName(x))} và ${esc(bodyName(y))}</li>`).join('');
    return `<div class="tbl-wrap"><table class="tbl wt-tbl"><thead><tr><th scope="col">Nơi</th><th scope="col">Quan hệ theo cung</th><th scope="col">Cách nhau</th></tr></thead><tbody>${rows}</tbody></table></div>`
      + (lum ? `<h4 class="wt-dsub">Hai sao sáng</h4><ul class="plain wt-syn-list">${lum}</ul>` : '')
      + `<h4 class="wt-dsub">Trao đổi vị trí</h4>${ex ? `<ul class="plain wt-syn-list">${ex}</ul>` : '<p class="hint">Không có cặp nào đổi chỗ cho nhau giữa hai bản đồ.</p>'}`
      + '<p class="hint">Ptolemy so theo cung, không theo độ: cách 1 hoặc 5 cung là “không nhìn thấy nhau”.</p>';
  }

  // buttons inside the synastry section select on its own wheel
  root.addEventListener('click', e => {
    const b = e.target.closest('[data-pick]'); if (!b || !S.wheel) return;
    const [k, x] = b.dataset.pick.split(':');
    const s = k === 'house' ? { kind: 'house', n: +x } : k === 'link' || k === 'aspect' ? { kind: k, i: +x } : { kind: k, id: x };
    S.sel = s; S.wheel.select(s); showDetail();
    if (!$('#syn-detail', out).contains(b)) $('#syn-stage', out).scrollIntoView({ block: 'start', behavior: 'smooth' });
  });
  return { refresh };
}
