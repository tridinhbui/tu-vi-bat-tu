// Shared pieces of the "Observatory" result pages: evidence tiers, per-chart year cache, timeline helpers.
// Presentation only. Every number and name comes from the engine responses passed in.
import { esc, post } from './util.js';

/** Three evidence tiers, one marker each (shape, not only colour). Same wording as the comparison dialog. */
export const EV = {
  calc: { cls: 'ev-calc', label: 'Dữ kiện tính toán', hint: 'Lập thẳng từ ngày giờ sinh, không qua diễn giải' },
  src: { cls: 'ev-src', label: 'Theo sách', hint: 'Quy tắc đã đối chiếu với một trang sách có trích dẫn' },
  hyp: { cls: 'ev-hyp', label: 'Giả thuyết · quy tắc nháp', hint: 'Quy tắc nháp, chưa xác minh nguồn' },
};
export const evMark = k => `<i class="ev ${EV[k].cls}" aria-hidden="true"></i>`;
/** One tier block. `pro` tiers disappear in the 'Dễ hiểu' mode, exactly like drafts do elsewhere. */
export const tier = (k, body, { pro = false, count = null, id = '' } = {}) =>
  `<section class="tier tier-${k}${pro ? ' pro-only' : ''}"${id ? ` id="${id}"` : ''}><h4 title="${esc(EV[k].hint)}">${evMark(k)}<span>${EV[k].label}</span>${count ? `<em>${count}</em>` : ''}</h4><div class="tier-b">${body}</div></section>`;
export const evLegend = () =>
  `<ul class="ev-legend" aria-label="Chú giải ba lớp thông tin">${['calc', 'src', 'hyp'].map(k => `<li${k === 'hyp' ? ' class="pro-only"' : ''} title="${esc(EV[k].hint)}">${evMark(k)}${EV[k].label}</li>`).join('')}</ul>`;

/** /api/year memoised per request object, so both pages and every timeline share one fetch per year. */
const yearCache = new WeakMap();
export function yearData(req, y) {
  let m = yearCache.get(req); if (!m) yearCache.set(req, m = new Map());
  if (!m.has(y)) m.set(y, post('/api/year', { ...req, to_year: y }).catch(e => { m.delete(y); throw e; }));
  return m.get(y);
}

/** Gregorian years covered by one 10-year period, from the engine's exact start instants (fractional years). */
/** The first Bát Tự year a luck pillar holds for most of it: the year whose middle (Lập Xuân ≈ Y + 0.09, plus half a year) falls on or
 *  after its exact start. Same rule as tvbt.bazi.luck_first_year and temporal.bazi_year (audit BZ-5/6), so the strip, the year labels and
 *  the report never disagree. */
export const luckFirstYear = startExact => Math.ceil(Math.round((startExact - 0.59) * 1e6) / 1e6);
/** The luck pillar in force on a day (ISO date, default today): the last one whose exact start_date is on or before it; -1 before the first. */
export const luckIndexOn = (lp, iso = new Date().toISOString().slice(0, 10)) => lp.reduce((a, l, i) => l.start_date && l.start_date <= iso ? i : a, -1);
export const periodYears = (startExact, nextStartExact) => {
  const a = luckFirstYear(startExact), b = nextStartExact != null ? luckFirstYear(nextStartExact) - 1 : a + 9;
  return Array.from({ length: Math.max(1, b - a + 1) }, (_, i) => a + i);
};

/** Wheel-free horizontal scroll helper: keep the chosen tab in view without jumping the page. */
export const centerIn = (scroller, el) => {
  if (!scroller || !el) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  scroller.scrollTo({ left: el.offsetLeft - scroller.clientWidth / 2 + el.offsetWidth / 2, behavior: reduce ? 'auto' : 'smooth' });
};

/** Pointer + keyboard activation for non-button targets. */
export const onPick = (el, fn) => {
  el.addEventListener('click', fn);
  el.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fn(e); } });
};
