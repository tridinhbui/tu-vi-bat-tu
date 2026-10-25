// Cung hoàng đạo (Western sun sign): a short card at the top of the Tử Vi pane, a chip in the result highlights, and the card on the
// /cung-hoang-dao/ lookup page. Everything shown is computed by the engine (tvbt/hoang_dao.py: the Sun's ingress = the trung khí
// instants); this file only draws it. Readings come from the engine with book and printed page (engine/data/hoang_dao/pack.json:
// Alan Leo for character, Lilly and Ptolemy for element / modality / ruler); a sign without any gets the engine's neutral line.
import { esc } from './util.js';

// One SVG path per sign (24x24, stroke only), the same strings as tvbt/hoang_dao.py GLYPHS (engine/tests/test_hoang_dao.py checks them).
export const GLYPHS = {
  "bach-duong": "M12 21V10M12 10C12 6 10.5 3.5 7.5 3.5S3 5.5 3 8s2 3.5 3.5 3.5M12 10c0-4 1.5-6.5 4.5-6.5S21 5.5 21 8s-2 3.5-3.5 3.5",
  "kim-nguu": "M3 3.5c1.2 4 4.5 6 9 6s7.8-2 9-6M12 9.5a5.5 5.5 0 1 0 0 11a5.5 5.5 0 1 0 0-11",
  "song-tu": "M4.5 3.5c4.5 1.6 10.5 1.6 15 0M4.5 20.5c4.5-1.6 10.5-1.6 15 0M9 4.6v14.8M15 4.6v14.8",
  "cu-giai": "M4 9a3 3 0 1 0 6 0a3 3 0 1 0-6 0M7 6c4.2-2.6 10-2 13.5 1.8M14 15a3 3 0 1 0 6 0a3 3 0 1 0-6 0M17 18c-4.2 2.6-10 2-13.5-1.8",
  "su-tu": "M9.5 16a3 3 0 1 1-6 0a3 3 0 1 1 6 0C9.5 11.5 7.5 9.5 7.5 7a4.5 4.5 0 0 1 9 0c0 4-3 6-3 10c0 2.4 1.4 3.5 3.2 3.5c1.8 0 3.3-1.2 3.3-3",
  "xu-nu": "M3 5.5c1.3 0 2 .8 2 2.2V18M5 8.5c0-1.9 1.2-3 2.8-3s2.7 1.1 2.7 3V18M10.5 8.5c0-1.9 1.2-3 2.8-3s2.7 1.1 2.7 3v6.5c0 3 1.5 5 4.5 6M16 13c1.8-1.6 5-1.2 5 1.2c0 2.6-3 4.6-6.5 5.8",
  "thien-binh": "M3 20h18M3 16h5.2a4.5 4.5 0 1 1 7.6 0H21",
  "bo-cap": "M3 5.5c1.3 0 2 .8 2 2.2V18M5 8.5c0-1.9 1.2-3 2.8-3s2.7 1.1 2.7 3V18M10.5 8.5c0-1.9 1.2-3 2.8-3s2.7 1.1 2.7 3V17c0 1.8 1.1 3 2.8 3H21M18.8 17.8l2.2 2.2-2.2 2.2",
  "nhan-ma": "M4 20L20 4M12.5 4H20v7.5M6.5 11.5l6 6",
  "ma-ket": "M3 5c1.4 0 2.5 1 2.5 3v10.5M5.5 8c0-2.2 1.5-3.5 3.5-3.5s3.5 1.3 3.5 3.5v8.5c0 2.7 1.9 4.5 4.3 4.5a3.4 3.4 0 0 0 0-6.8c-2 0-3.5 1.3-4.3 3",
  "bao-binh": "M3 10l3-3 3 3 3-3 3 3 3-3 3 3M3 17l3-3 3 3 3-3 3 3 3-3 3 3",
  "song-ngu": "M5.5 3c4 4.5 4 13.5 0 18M18.5 3c-4 4.5-4 13.5 0 18M4.5 12h15",
};

export const glyph = (slug, cls = 'hd-glyph') => GLYPHS[slug]
  ? `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="${GLYPHS[slug]}"/></svg>` : '';

/** The chip for the result highlights (#res-hl). Empty when there is nothing to show (shared link with the birth hidden). */
export function hoangdaoChip(w) {
  if (!w?.sun_sign) return '';
  const s = w.sun_sign;
  return `<button type="button" class="hl-chip hl-hd" data-act="hoangdao" title="Cung hoàng đạo (chiêm tinh phương Tây) theo vị trí Mặt Trời lúc sinh">${glyph(s.slug, 'hd-glyph hd-glyph-sm')}${esc(s.label)} <small>Cung hoàng đạo</small></button>`;
}

export const cite = c => `[${c.short || c.book}, tr. ${c.page}]`;
const CARD_READS = 5;   // the card shows the first few character readings; the sign's page has them all

/** Element / modality / ruler, each with the pages that state it. */
export function factsHtml(f) {
  const keys = ['element', 'modality', 'ruler'].filter(k => f?.[k]);
  if (!keys.length) return '';
  return `<dl class="hd-facts">${keys.map(k => `<div><dt>${esc(f[k].name)}</dt><dd>${esc(f[k].label)} <cite>${f[k].cites.map(c => esc(cite(c))).join(' ')}</cite></dd></div>`).join('')}</dl>`;
}

/** The character readings (not the classification ones) as a list; limit = how many (0 = all). */
export function readsHtml(rs, limit = 0) {
  const list = (rs || []).filter(r => r.topic !== 'classification');
  const shown = limit ? list.slice(0, limit) : list;
  return shown.length ? `<ul class="hd-reads">${shown.map(r => `<li>${esc(r.reading)} <cite>${esc(cite(r))}</cite></li>`).join('')}</ul>` : '';
}

/** The card's HTML. opts.link: link to the sign's article page (default true). */
export function hoangdaoCard(w, { link = true, heading = 'h3' } = {}) {
  if (!w?.sun_sign) return '';
  const s = w.sun_sign, a = w.ingress, b = w.next_ingress, H = heading;
  const n = (w.readings || []).filter(r => r.topic !== 'classification').length;
  const reads = n
    ? `${factsHtml(w.facts)}<p class="hd-sub">Theo sách</p>${readsHtml(w.readings, CARD_READS)}`
    : `${factsHtml(w.facts)}<p class="hd-wait">${esc(w.reading_status || '')}</p>`;
  const label = n > CARD_READS ? `Đọc đủ ${n} ý về cung hoàng đạo ${s.name}` : `Về cung hoàng đạo ${s.name}`;
  return `<section class="hd-card" id="hd-card" aria-labelledby="hd-h">
  <div class="hd-mark">${glyph(s.slug)}</div>
  <div class="hd-body">
    <p class="hd-k">Cung hoàng đạo · chiêm tinh phương Tây</p>
    <${H} id="hd-h" class="hd-name">${esc(s.label)} <small>${esc(s.latin)}</small></${H}>
    <p class="hd-span">Mặt Trời ở cung hoàng đạo này từ <b>${esc(a.text)}</b> đến <b>${esc(b.text)}</b> (giờ nơi sinh, ${esc(a.utc_offset)}). Ngày dương lịch thường gặp: ${esc(s.approx_dates)} (${esc(s.approx_dates_note)}, mốc thật xê dịch theo năm).</p>
    ${w.note ? `<p class="hd-cusp" role="note">${esc(w.note)}</p>` : ''}
    ${reads}
    <p class="hd-foot">Cung hoàng đạo tính theo vị trí Mặt Trời trên hoàng đạo lúc sinh; đây là cách chia của chiêm tinh phương Tây, khác với mười hai cung của lá số Tử Vi.${n ? ' Mỗi ý là lời diễn lại ngắn kèm tên sách và trang: khuynh hướng theo sách, không phải lời đoán cho riêng ai.' : ''}${link ? ` <a class="link" href="/bai-viet/hoang-dao/${esc(s.slug)}/">${esc(label)}</a>` : ''}</p>
  </div>
</section>`;
}

/** Draws the card into host; w = chart.western, or null to clear it (shared link whose birth day is hidden). */
export function renderHoangDao(host, w) {
  if (!host) return;
  host.innerHTML = w ? hoangdaoCard(w) : '';
  host.hidden = !w;
}
