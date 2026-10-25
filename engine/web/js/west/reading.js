// Reading renderer for POST /api/west/reading. Shows only what the engine sends: chapters → paragraphs with their evidence tier,
// school, evidence chips (each one lights up its planet, house, sign or aspect on the wheel) and, in "Đọc sâu", the steps, the quote
// and the sources. Until the endpoint exists the section says so; no reading text is ever written on the client.
import { esc } from '../util.js';
import { EV, evMark } from '../atlas.js';
import { SCHOOL } from './vocab.js';
import { westPost } from './api.js';
import { lockHtml } from '../paywall.js';

/** Parse an evidence item into a wheel selection (null = nothing to light up, e.g. a rule). Aspect ids are matched loosely
 *  ("sun-moon-trine", "sun|moon|trine", "aspect:sun:moon:trine") against the chart's own aspect list. */
export function evidenceSel(ev, chart) {
  const id = String(ev.id || '').replace(/^(planet|house|aspect|sign|point):/, '');
  if (ev.kind === 'planet' || ev.kind === 'point') return { kind: 'planet', id };
  if (ev.kind === 'house') { const n = parseInt(id.replace(/\D+/g, ''), 10); return n >= 1 && n <= 12 ? { kind: 'house', n } : null; }
  if (ev.kind === 'sign') return { kind: 'sign', id };
  if (ev.kind === 'aspect') {
    const parts = id.split(/[|:,\s-]+/).filter(Boolean);
    const i = (chart.aspects || []).findIndex(a => parts.includes(a.a) && parts.includes(a.b) && (parts.length < 3 || parts.includes(a.type)));
    if (i >= 0) return { kind: 'aspect', i };
    // not among the natal aspects (a sign-based contact, or a transit in Thời vận): light up the two natal points instead
    const pts = parts.filter(x => chart.bodies?.[x] || chart.points?.[x] || chart.angles?.[x] || chart.lots?.[x]);
    const type = parts.find(x => !pts.includes(x)) || '';
    return pts.length === 2 ? { kind: 'pair', a: pts[0], b: pts[1], type } : pts.length === 1 ? { kind: 'planet', id: pts[0] } : null;
  }
  return null;
}

const para = (p, deep, chart) => {
  const tier = EV[p.tier] ? `<span class="wt-tier" title="${esc(EV[p.tier].hint)}">${evMark(p.tier)}${esc(EV[p.tier].label)}</span>` : '';
  const school = p.school ? `<span class="badge wt-school s-${esc(p.school)}">${esc(SCHOOL[p.school] || p.school)}</span>` : '';
  const chips = (p.evidence || []).map(e => {
    const s = evidenceSel(e, chart);
    return s ? `<button type="button" class="wt-evc" data-ev="${esc(JSON.stringify(s))}" title="Xem trên bánh xe">${esc(e.label || e.id)}</button>` : `<span class="wt-evc off">${esc(e.label || e.id)}</span>`;
  }).join('');
  let more = '';
  if (deep) {
    if (p.method) more += `<p class="wt-dsub">Phương pháp của nguồn</p><p class="wt-method">${esc(p.method)}</p>`;
    if (p.steps?.length) more += `<p class="wt-dsub">Các bước suy luận</p><ol class="wt-steps">${p.steps.map(s => `<li>${esc(s)}</li>`).join('')}</ol>`;
    if (p.quote?.text) more += `<blockquote class="wt-quote"><p>${esc(p.quote.text)}</p>${p.quote.source_label ? `<cite>${esc(p.quote.source_label)}</cite>` : ''}</blockquote>`;
  }
  return `<article class="wt-para tier-${esc(p.tier || '')}${p.level === 'deep' ? ' deep' : ''}${p.paid ? ' pw-paid' : ''}" id="wt-p-${esc(p.id)}">`
    + (p.heading ? `<h4>${esc(p.heading)}</h4>` : '') + `<div class="wt-pmeta">${tier}${school}</div><p>${esc(p.text)}</p>`
    + (chips ? `<div class="wt-evs" aria-label="Dữ kiện làm căn cứ">${chips}</div>` : '')
    + (p.sources?.length ? `<div class="wt-srcs" aria-label="Nguồn">${p.sources.map(x => `<span class="wt-src" title="${esc([x.id, x.loc].filter(Boolean).join(' · '))}"><svg width="11" height="11" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 1.5h6.5a1 1 0 011 1v8H3a1 1 0 01-1-1z" fill="none" stroke="currentColor" stroke-width="1"/></svg>${esc(x.label || x.id)}${x.loc && !x.label ? ` <em>${esc(x.loc)}</em>` : ''}</span>`).join('')}</div>` : '')
    + more + '</article>';
};

export function renderReading(host, data, { deep, chart }) {
  const chs = (data.chapters || []).map(c => {
    const ps = (c.paragraphs || []).filter(p => deep || p.level !== 'deep');
    // the server held part of the chapter back (src/billing/west.ts): its lock card; a held-back Đọc sâu shows only in Đọc sâu mode
    const lock = c.locked && (c.locked.total > c.locked.shown || (deep && c.locked.deep)) ? lockHtml({ chapter: c.locked.chapter, locked: c.locked }) : '';
    if (!ps.length && !c.lead && !lock) return '';
    return `<section class="wt-chap" id="wt-c-${esc(c.id)}">${c.title ? `<h3>${esc(c.title)}</h3>` : ''}${c.lead ? `<p class="lead">${esc(c.lead)}</p>` : ''}${ps.map(p => para(p, deep, chart)).join('')}${lock}</section>`;
  }).join('');
  const legend = `<ul class="ev-legend wt-evleg" aria-label="Chú giải ba lớp thông tin">${['calc', 'src', 'hyp'].map(k => `<li title="${esc(EV[k].hint)}">${evMark(k)}${EV[k].label}</li>`).join('')}</ul>`;
  host.innerHTML = legend + (chs || '<p class="note">Máy chủ chưa trả về đoạn luận giải nào cho bản đồ này.</p>') + (data.disclaimer ? `<p class="cnote">${esc(data.disclaimer)}</p>` : '');
}

/** Fetch and render. 404/405 (endpoint not deployed yet) → the placeholder note, nothing else. */
let seq = 0;
export async function loadReading(host, inp, chart, { deep, gender = null }) {
  const my = ++seq;
  host.innerHTML = '<p class="note">Đang soạn luận giải (vài giây)…</p>';
  try {
    const body = { birth: inp.birth, options: inp.options, mode: deep ? 'deep' : 'overview' };
    if (gender) body.gender = gender;
    const data = await westPost('reading', body, { retries: 1 });
    if (my !== seq) return null;
    renderReading(host, data, { deep, chart });
    return data;
  } catch (e) {
    if (my !== seq) return null;
    host.innerHTML = e.status === 404 || e.status === 405
      ? '<div class="cnote"><b>Phần luận giải đang được hoàn thiện.</b> Các bảng số liệu và bánh xe ở trên đã đầy đủ; phần diễn giải sẽ hiện ở đây khi được đối chiếu xong với sách nguồn.</div>'
      : `<p class="note">Chưa tải được luận giải: ${esc(e.message)}</p>`;
    return null;
  }
}
