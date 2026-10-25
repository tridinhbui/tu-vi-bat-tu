// Western astrology vocabulary: names, glyphs and number formatting only. No calculation lives here: every longitude, house,
// orb and date shown on the page comes from /api/west/*. Names mirror engine/data/western/kb/core.json and aspects.json.
import { esc } from '../util.js';

/** U+FE0E keeps the zodiac and planet symbols as text glyphs (iOS would otherwise draw several of them as colour emoji). */
const T = s => s + '︎';

export const BODY = {
  sun: { vi: 'Mặt Trời', g: T('☉') }, moon: { vi: 'Mặt Trăng', g: T('☽') }, mercury: { vi: 'Sao Thủy', g: T('☿') },
  venus: { vi: 'Sao Kim', g: T('♀') }, mars: { vi: 'Sao Hỏa', g: T('♂') }, jupiter: { vi: 'Sao Mộc', g: T('♃') },
  saturn: { vi: 'Sao Thổ', g: T('♄') }, uranus: { vi: 'Sao Thiên Vương', g: T('♅') }, neptune: { vi: 'Sao Hải Vương', g: T('♆') },
  pluto: { vi: 'Sao Diêm Vương', g: T('♇') }, chiron: { vi: 'Chiron', g: T('⚷') },
  north_node: { vi: 'La Hầu (Nút Bắc)', g: T('☊') }, south_node: { vi: 'Kế Đô (Nút Nam)', g: T('☋') },
  fortune: { vi: 'Điểm May Mắn (Lot of Fortune)', g: T('⊗') }, spirit: { vi: 'Điểm Tinh Thần (Lot of Spirit)', g: T('◇') },
  asc: { vi: 'Điểm Mọc (ASC)', g: 'ASC' }, mc: { vi: 'Thiên Đỉnh (MC)', g: 'MC' }, dsc: { vi: 'Điểm Lặn (DSC)', g: 'DSC' }, ic: { vi: 'Thiên Để (IC)', g: 'IC' },
};
export const PLANETS10 = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto'];
export const CLASSICAL = PLANETS10.slice(0, 7);
/** Bodies drawn on the natal wheel, in table order. The lots and angles are drawn when the birth time is known. */
export const WHEEL_BODIES = [...PLANETS10, 'chiron', 'north_node', 'south_node'];
export const bodyName = id => BODY[id]?.vi || id;
export const bodyGlyph = id => BODY[id]?.g || id;
/** A body as "☉ Mặt Trời" with the glyph hidden from screen readers. */
export const bodyLabel = id => `<span class="wt-g" aria-hidden="true">${bodyGlyph(id)}</span> ${esc(bodyName(id))}`;
/** Short Vietnamese name without the parenthesised English (for tight cells). */
export const bodyShort = id => bodyName(id).replace(/\s*\(.*\)$/, '');

export const SIGNS = [
  ['aries', 'Bạch Dương', '♈'], ['taurus', 'Kim Ngưu', '♉'], ['gemini', 'Song Tử', '♊'], ['cancer', 'Cự Giải', '♋'],
  ['leo', 'Sư Tử', '♌'], ['virgo', 'Xử Nữ', '♍'], ['libra', 'Thiên Bình', '♎'], ['scorpio', 'Bọ Cạp', '♏'],
  ['sagittarius', 'Nhân Mã', '♐'], ['capricorn', 'Ma Kết', '♑'], ['aquarius', 'Bảo Bình', '♒'], ['pisces', 'Song Ngư', '♓'],
].map(([id, vi, g], i) => ({ id, vi, g: T(g), i, el: ['fire', 'earth', 'air', 'water'][i % 4] }));
export const SIGN = Object.fromEntries(SIGNS.map(s => [s.id, s]));
export const signName = id => SIGN[id]?.vi || id;
export const signLabel = id => SIGN[id] ? `<span class="wt-g" aria-hidden="true">${SIGN[id].g}</span> ${esc(SIGN[id].vi)}` : esc(id);
export const ELEMENT = { fire: 'Lửa', earth: 'Đất', air: 'Khí', water: 'Nước' };
export const MODALITY = { cardinal: 'Khởi đầu (cardinal)', fixed: 'Kiên định (fixed)', mutable: 'Biến đổi (mutable)' };
export const HEMI = { above: 'Trên đường chân trời', below: 'Dưới đường chân trời', east: 'Nửa phía Đông', west: 'Nửa phía Tây' };

/** Aspect names (kb/aspects.json) and the visual family used by the wheel. `tone` is a drawing convention, not a reading:
 *  the conjunction has no line, trine/sextile-type angles are drawn as the "harmonious" style, square/opposition-type as "tense". */
export const ASPECT = {
  conjunction: { vi: 'Trùng tụ', g: '☌', tone: 'conj', major: true },
  opposition: { vi: 'Đối đỉnh', g: '☍', tone: 'hard', major: true },
  trine: { vi: 'Tam hợp', g: '△', tone: 'soft', major: true },
  square: { vi: 'Vuông góc', g: '□', tone: 'hard', major: true },
  sextile: { vi: 'Lục hợp', g: '⚹', tone: 'soft', major: true },
  quincunx: { vi: 'Lệch 150° (quincunx)', g: '⚻', tone: 'hard', major: false },
  semisextile: { vi: 'Bán lục hợp', g: '⚺', tone: 'soft', major: false },
  semisquare: { vi: 'Bán vuông', g: '∠', tone: 'hard', major: false },
  sesquiquadrate: { vi: 'Vuông rưỡi', g: '⚼', tone: 'hard', major: false },
  quintile: { vi: 'Ngũ phân', g: 'Q', tone: 'soft', major: false },
  biquintile: { vi: 'Song ngũ phân', g: 'bQ', tone: 'soft', major: false },
};
export const aspName = t => ASPECT[t]?.vi || t;
export const aspGlyph = t => ASPECT[t]?.g ? T(ASPECT[t].g) : t;
export const TONE = { soft: 'hài hòa', hard: 'căng', conj: 'trùng tụ' };

export const PATTERN = {
  grand_trine: 'Đại tam hợp', t_square: 'Chữ T (T-square)', grand_cross: 'Đại thập tự', yod: 'Yod (ngón tay định mệnh)',
  kite: 'Con diều', mystic_rectangle: 'Chữ nhật huyền bí', stellium: 'Tụ hội (stellium)',
};
export const HOUSE_SYS = {
  placidus: 'Placidus', whole_sign: 'Whole Sign (trọn cung)', equal: 'Equal House (nhà đều)', porphyry: 'Porphyry', regiomontanus: 'Regiomontanus',
};
export const DIGNITY = {
  domicile: 'Chủ quản (domicile)', exaltation: 'Vượng (exaltation)', triplicity: 'Chủ tam phương (triplicity)',
  term: 'Giới (term)', face: 'Diện (face)', detriment: 'Bất lợi (detriment)', fall: 'Suy (fall)', peregrine: 'Lưu lạc (peregrine)',
};
export const SOLAR = { cazimi: 'Cazimi (giữa lòng Mặt Trời)', combust: 'Bị đốt (combust)', under_beams: 'Dưới tia Mặt Trời (under the beams)' };
export const MOON_PHASE = {
  new: 'Trăng non', waxing_crescent: 'Lưỡi liềm đầu tháng', first_quarter: 'Thượng huyền', waxing_gibbous: 'Trăng gần tròn (đang tăng)',
  full: 'Trăng tròn', waning_gibbous: 'Trăng khuyết dần', last_quarter: 'Hạ huyền', waning_crescent: 'Lưỡi liềm cuối tháng',
};
export const RECEPTION = { domicile: 'theo chủ quản', exaltation: 'theo vượng', mixed: 'hỗn hợp (chủ quản và vượng)' };
export const SCHOOL = { calc: 'Dữ kiện', hellenistic: 'Hy Lạp cổ đại', traditional: 'Truyền thống – Lilly', modern: 'Hiện đại – Alan Leo', compare: 'Đối chiếu' };
export const WARN = {
  no_time: 'Không có giờ sinh: không tính được cung Mọc, Thiên Đỉnh, các nhà và các Điểm (lot). Mặt Trăng có thể ở bất kỳ đâu trong khoảng nó đi qua trong ngày.',
  placidus_polar_fallback_porphyry: 'Ở vĩ độ trong vòng cực, hệ Placidus không xác định được mọi đỉnh nhà, nên các nhà được chia theo Porphyry (chia đều từng góc phần tư giữa các trục).',
};

// ----- numbers (formatting only) -----
const nf = (d, min = 0) => new Intl.NumberFormat('vi-VN', { maximumFractionDigits: d, minimumFractionDigits: min });
export const num = (v, d = 2, min = 0) => v == null || Number.isNaN(+v) ? '—' : nf(d, min).format(v);
/** A small angle in degrees (orb) as 0°16′. */
export function dm(v) {
  if (v == null) return '—';
  const a = Math.abs(v); let d = Math.floor(a), m = Math.round((a - d) * 60);
  if (m === 60) { d += 1; m = 0; }
  return `${v < 0 ? '−' : ''}${d}°${String(m).padStart(2, '0')}′`;
}
/** "15°28′ ♒" from an API point ({sign, fmt}). */
export const posTxt = p => p ? `${p.fmt} ${SIGN[p.sign]?.g || ''}` : '—';
export const posFull = p => p ? `${esc(p.fmt)} ${signLabel(p.sign)}` : '—';

// ----- dates: shown in the birthplace's time zone, said once next to every list -----
/** The engine reads the full tz database, backzone included (Asia/Hanoi, the north's own history); browsers ship only canonical
 *  zones. For the dates this page formats (transits, returns, progressions: all after 1975) the canonical neighbour has the same clock. */
const TZ_ALIAS = { 'Asia/Hanoi': 'Asia/Ho_Chi_Minh', 'Asia/Saigon': 'Asia/Ho_Chi_Minh' };
const tzOk = new Map();
export function safeTz(tz) {
  if (!tz) return 'UTC';
  if (!tzOk.has(tz)) { let ok = true; try { new Intl.DateTimeFormat('en-US', { timeZone: tz }); } catch { ok = false; } tzOk.set(tz, ok); }
  return tzOk.get(tz) ? tz : TZ_ALIAS[tz] || 'UTC';
}
export function fmtDate(iso, tz, { time = false, short = false } = {}) {
  if (!iso) return '—';
  const o = short ? { day: '2-digit', month: '2-digit' } : { day: '2-digit', month: '2-digit', year: 'numeric' };
  if (time) Object.assign(o, { hour: '2-digit', minute: '2-digit', hourCycle: 'h23' });
  try { return new Intl.DateTimeFormat('vi-VN', { ...o, timeZone: safeTz(tz) }).format(new Date(iso)); } catch { return iso.slice(0, 16).replace('T', ' '); }
}
/** Offset (minutes east of UTC) of an IANA zone at an instant, read from Intl (the browser's own tz database). */
export function tzOffsetMin(tz, ms) {
  try {
    const p = Object.fromEntries(new Intl.DateTimeFormat('en-US', { timeZone: safeTz(tz), hourCycle: 'h23', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })
      .formatToParts(new Date(ms)).map(x => [x.type, x.value]));
    return Math.round((Date.UTC(+p.year, p.month - 1, +p.day, +p.hour % 24, +p.minute, +p.second) - ms) / 60000);
  } catch { return 0; }
}
/** UTC instant (ms) of a wall-clock time in a zone (two passes settle a DST edge). */
export function zonedMs(tz, y, mo, d, h = 0, mi = 0) {
  const guess = Date.UTC(y, mo - 1, d, h, mi);
  let t = guess - tzOffsetMin(tz, guess) * 60000;
  t = guess - tzOffsetMin(tz, t) * 60000;
  return t;
}
/** Wall-clock parts of an instant in a zone. */
export function zonedParts(tz, ms) {
  const off = tzOffsetMin(tz, ms), d = new Date(ms + off * 60000);
  return { year: d.getUTCFullYear(), month: d.getUTCMonth() + 1, day: d.getUTCDate(), hour: d.getUTCHours(), minute: d.getUTCMinutes() };
}
export const isoDay = p => `${p.year}-${String(p.month).padStart(2, '0')}-${String(p.day).padStart(2, '0')}`;
export const hhmm = p => `${String(p.hour).padStart(2, '0')}:${String(p.minute).padStart(2, '0')}`;
