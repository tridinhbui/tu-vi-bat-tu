// Reading renderer for POST /api/west/reading. Shows only what the engine sends: chapters → paragraphs with their evidence tier,
// school, evidence chips (each one lights up its planet, house, sign or aspect on the wheel) and, in "Đọc sâu", the steps, the quote
// and the sources. Until the endpoint exists the section says so; no reading text is ever written on the client.
import { esc } from '../util.js';
import { EV, evMark } from '../atlas.js';
import { SCHOOL } from './vocab.js';
import { westPost } from './api.js';
import { lockHtml } from '../paywall.js';
import { loadGlossary, autoLink } from '../glossary.js';

const SYS_VI = { lilly: 'cách chia của Lilly', whole_sign: 'trọn cung', ptolemy: 'chỗ 30° của Ptolemy' };
/** The band of house `n` in `system` (null when it is the wheel's own system, which the wheel draws already). */
export function houseSpan(n, system, chart) {
  if (!n || !system || system === chart.houses?.system) return null;
  const cs = chart.houses?.cusps || {}, asc = chart.angles?.asc?.lon;
  if (system === 'whole_sign' && cs.whole_sign) return { kind: 'span', from: cs.whole_sign[n - 1].lon, to: cs.whole_sign[n - 1].lon + 30 };
  if (system === 'lilly' && cs.regiomontanus) return { kind: 'span', from: cs.regiomontanus[n - 1].lon - 5, to: cs.regiomontanus[n % 12].lon - 5 };
  if (system === 'ptolemy' && asc != null) return { kind: 'span', from: asc - 5 + 30 * (n - 1), to: asc - 5 + 30 * n };
  if (cs[system]) return { kind: 'span', from: cs[system][n - 1].lon, to: cs[system][n % 12].lon };
  return null;
}

/** Parse an evidence item into a wheel selection (null = nothing to light up). A planet or house read in another house system than
 *  the wheel's carries that system's band; a transit lights the natal point it touches (its aspect is not a natal aspect). */
export function evidenceSel(ev, chart) {
  const id = String(ev.id || '').replace(/^(planet|house|aspect|sign|point):/, '');
  if (ev.kind === 'planet' || ev.kind === 'point') {
    const sp = ev.house ? houseSpan(ev.house, ev.system, chart) : null;
    return { kind: 'planet', id, ...(sp ? { span: { ...sp, label: `Nhà ${ev.house} theo ${SYS_VI[ev.system] || ev.system}` } } : {}) };
  }
  if (ev.kind === 'house') {
    const n = parseInt(id.replace(/\D+/g, ''), 10);
    if (!(n >= 1 && n <= 12)) return null;
    const sp = houseSpan(n, ev.system, chart);
    return sp ? { ...sp, label: `Nhà ${n} theo ${SYS_VI[ev.system] || ev.system}` } : { kind: 'house', n };
  }
  if (ev.kind === 'sign') return { kind: 'sign', id };
  if (ev.kind === 'star') { const st = chart.fixed_stars?.[id]; return st ? { kind: 'span', from: st.lon - 1, to: st.lon + 1, label: st.name } : null; }
  if (ev.kind === 'transit') return ev.natal ? { kind: 'planet', id: ev.natal } : null;
  if (ev.kind === 'aspect') {
    const parts = id.split(/[|:,\s-]+/).filter(Boolean);
    const i = (chart.aspects || []).findIndex(a => parts.includes(a.a) && parts.includes(a.b) && (parts.length < 3 || parts.includes(a.type)));
    if (i >= 0) return { kind: 'aspect', i };
    // not among the natal aspects (a sign-based contact): light up the two natal points instead
    const pts = parts.filter(x => chart.bodies?.[x] || chart.points?.[x] || chart.angles?.[x] || chart.lots?.[x]);
    const type = parts.find(x => !pts.includes(x)) || '';
    return pts.length === 2 ? { kind: 'pair', a: pts[0], b: pts[1], type } : pts.length === 1 ? { kind: 'planet', id: pts[0] } : null;
  }
  return null;
}

const para = (p, deep, chart) => {
  const tier = EV[p.tier] ? `<span class="wt-tier" title="${esc(EV[p.tier].hint)}">${evMark(p.tier)}${esc(EV[p.tier].label)}</span>` : '';
  const summary = p.layer === 'summary';
  const school = summary ? '<span class="badge wt-school s-sum" title="Thiên Bàn gom kết quả các phép của chương này, mỗi chứng ghi rõ của tác giả nào">Tổng hợp của Thiên Bàn</span>'
    : p.school ? `<span class="badge wt-school s-${esc(p.school)}">${esc(SCHOOL[p.school] || p.school)}</span>` : '';
  const chips = (p.evidence || []).map(e => {
    const s = evidenceSel(e, chart);
    return s ? `<button type="button" class="wt-evc" data-ev="${esc(JSON.stringify(s))}" title="Xem trên bánh xe">${esc(e.label || e.id)}</button>` : `<span class="wt-evc off">${esc(e.label || e.id)}</span>`;
  }).join('');
  let more = '';
  if (deep && (p.method || p.steps?.length || p.quote?.text)) {
    more = `<details class="wt-why"><summary>${summary ? 'Cách gom các chứng' : 'Phương pháp và các bước'}</summary>`
      + (p.method ? `<p class="wt-method">${esc(p.method)}</p>` : '')
      + (p.steps?.length ? `<ol class="wt-steps">${p.steps.map(x => `<li>${esc(x)}</li>`).join('')}</ol>` : '')
      + (p.quote?.text ? `<blockquote class="wt-quote"><p>${esc(p.quote.text)}</p>${p.quote.source_label ? `<cite>${esc(p.quote.source_label)}</cite>` : ''}</blockquote>` : '')
      + '</details>';
  }
  return `<article class="wt-para tier-${esc(p.tier || '')}${p.level === 'deep' ? ' deep' : ''}${summary ? ' wt-sum' : ''}${p.paid ? ' pw-paid' : ''}" id="wt-p-${esc(p.id)}">`
    + (p.heading ? `<h4>${esc(p.heading)}</h4>` : '') + `<div class="wt-pmeta">${tier}${school}</div><p class="wt-txt">${esc(p.text)}</p>`
    + (chips ? `<div class="wt-evs" aria-label="Dữ kiện làm căn cứ (bấm để xem trên bánh xe)">${chips}</div>` : '')
    + (p.sources?.length ? `<div class="wt-srcs" aria-label="Nguồn">${p.sources.map(x => `<span class="wt-src" title="${esc([x.id, x.loc].filter(Boolean).join(' · '))}"><svg width="11" height="11" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 1.5h6.5a1 1 0 011 1v8H3a1 1 0 01-1-1z" fill="none" stroke="currentColor" stroke-width="1"/></svg>${esc(x.label || x.id)}${x.loc && !x.label ? ` <em>${esc(x.loc)}</em>` : ''}</span>`).join('')}</div>` : '')
    + more + '</article>';
};

/** Đọc nhanh: each chapter's plain-language summary (or, for the chapters that describe the chart itself, its main paragraphs).
 *  Đọc sâu: the summary, the school paragraphs of the main part, then the deeper ones folded in "Đọc sâu". One response serves both. */
export function renderReading(host, data, { deep, chart }) {
  const chs = (data.chapters || []).map(c => {
    const all = c.paragraphs || [];
    const sum = all.filter(p => p.layer === 'summary'), main = all.filter(p => p.layer !== 'summary' && p.level !== 'deep'), low = all.filter(p => p.level === 'deep');
    const quick = sum.length ? sum : main;
    // the server held part of the chapter back (src/billing/west.ts): its lock card; a held-back Đọc sâu shows only in Đọc sâu mode
    const lock = c.locked && (c.locked.total > c.locked.shown || (deep && c.locked.deep)) ? lockHtml({ chapter: c.locked.chapter, locked: c.locked }) : '';
    let body;
    if (!deep) {
      if (!quick.length && !lock) return '';
      const rest = all.length - quick.length;
      body = quick.map(p => para(p, false, chart)).join('')
        + (rest > 0 ? `<button type="button" class="link wt-more" data-deepen="${esc(c.id)}">Xem phân tích chi tiết (${rest} đoạn) →</button>` : '');
    } else {
      if (!all.length && !lock) return '';
      body = sum.map(p => para(p, true, chart)).join('') + main.map(p => para(p, true, chart)).join('')
        + (low.length ? `<details class="pr-deep wt-deep"><summary><span class="cb-t">Đọc sâu</span><span class="muted small">${esc(low.map(p => p.heading).filter(Boolean).slice(0, 5).join(' · '))}${low.length > 5 ? ' …' : ''}</span></summary>${low.map(p => para(p, true, chart)).join('')}</details>` : '');
    }
    return `<section class="wt-chap" id="wt-c-${esc(c.id)}">${c.title ? `<h3>${esc(c.title)}</h3>` : ''}${c.lead ? `<p class="lead">${esc(c.lead)}</p>` : ''}${body}${lock}</section>`;
  }).join('');
  const legend = `<ul class="ev-legend wt-evleg" aria-label="Chú giải ba lớp thông tin">${['calc', 'src', 'hyp'].map(k => `<li title="${esc(EV[k].hint)}">${evMark(k)}${EV[k].label}</li>`).join('')}</ul>`;
  host.innerHTML = legend + (chs || '<p class="note">Máy chủ chưa trả về đoạn luận giải nào cho bản đồ này.</p>') + (data.disclaimer ? `<p class="cnote">${esc(data.disclaimer)}</p>` : '');
  loadGlossary().then(() => host.querySelectorAll('.wt-txt').forEach(el => autoLink(el, 'west')));
}

/** Fetch (always the whole reading: Đọc nhanh and Đọc sâu are two views of it) and render. 404/405 → the placeholder note. */
let seq = 0, last = null, want = false, pending = null;
export function loadReading(host, inp, chart, { deep, gender = null }) {
  return (pending = loadReading_(host, inp, chart, { deep, gender }));
}
async function loadReading_(host, inp, chart, { deep, gender }) {
  const my = ++seq;
  last = null; want = deep;          // a toggle while this loads must not redraw the previous chart's reading
  host.innerHTML = '<p class="note">Đang soạn luận giải (vài giây)…</p>';
  try {
    const body = { birth: inp.birth, options: inp.options, mode: 'deep' };
    if (gender) body.gender = gender;
    const data = await westPost('reading', body, { retries: 1 });
    if (my !== seq) return null;
    last = { host, data, chart };
    renderReading(host, data, { deep: want, chart });
    return data;
  } catch (e) {
    if (my !== seq) return null;
    host.innerHTML = e.status === 404 || e.status === 405
      ? '<div class="cnote"><b>Phần luận giải đang được hoàn thiện.</b> Các bảng số liệu và bánh xe ở trên đã đầy đủ; phần diễn giải sẽ hiện ở đây khi được đối chiếu xong với sách nguồn.</div>'
      : `<p class="note">Chưa tải được luận giải: ${esc(e.message)}</p>`;
    return null;
  }
}

/** The reading request in flight (or done), so the PDF button can wait for it. */
export const readingDone = () => pending || Promise.resolve(null);

/** Switch Đọc nhanh / Đọc sâu on the reading already loaded (no new request); false when there is none and none is loading. */
export function redrawReading(deep) {
  want = deep;
  if (!last) return !!pending;      // still loading: the response is drawn in the mode chosen last
  renderReading(last.host, last.data, { deep, chart: last.chart });
  return true;
}
