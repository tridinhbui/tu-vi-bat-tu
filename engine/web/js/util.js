// Shared helpers + domain vocabulary (names only; no calculation lives in the UI).
export const $ = (s, r = document) => r.querySelector(s);
export const $$ = (s, r = document) => [...r.querySelectorAll(s)];
export const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

export const STEMS = [
  ['Giáp', '甲', 'Mộc'], ['Ất', '乙', 'Mộc'], ['Bính', '丙', 'Hỏa'], ['Đinh', '丁', 'Hỏa'], ['Mậu', '戊', 'Thổ'],
  ['Kỷ', '己', 'Thổ'], ['Canh', '庚', 'Kim'], ['Tân', '辛', 'Kim'], ['Nhâm', '壬', 'Thủy'], ['Quý', '癸', 'Thủy'],
].map(([n, h, e]) => ({ n, h, e }));
export const BRANCHES = [
  ['Tý', '子', 'Thủy'], ['Sửu', '丑', 'Thổ'], ['Dần', '寅', 'Mộc'], ['Mão', '卯', 'Mộc'], ['Thìn', '辰', 'Thổ'], ['Tỵ', '巳', 'Hỏa'],
  ['Ngọ', '午', 'Hỏa'], ['Mùi', '未', 'Thổ'], ['Thân', '申', 'Kim'], ['Dậu', '酉', 'Kim'], ['Tuất', '戌', 'Thổ'], ['Hợi', '亥', 'Thủy'],
].map(([n, h, e]) => ({ n, h, e }));

// Order = sinh cycle (Mộc sinh Hỏa sinh Thổ sinh Kim sinh Thủy sinh Mộc)
export const ELEMENTS = ['Mộc', 'Hỏa', 'Thổ', 'Kim', 'Thủy'];
export const EL = {
  'Mộc': { h: '木', slug: 'moc', dir: 'Đông', season: 'Xuân', color: 'xanh lục', sinh: 'Hỏa', khac: 'Thổ', duocSinh: 'Thủy', biKhac: 'Kim' },
  'Hỏa': { h: '火', slug: 'hoa', dir: 'Nam', season: 'Hạ', color: 'đỏ', sinh: 'Thổ', khac: 'Kim', duocSinh: 'Mộc', biKhac: 'Thủy' },
  'Thổ': { h: '土', slug: 'tho', dir: 'Trung ương', season: 'Giao mùa', color: 'vàng', sinh: 'Kim', khac: 'Thủy', duocSinh: 'Hỏa', biKhac: 'Mộc' },
  'Kim': { h: '金', slug: 'kim', dir: 'Tây', season: 'Thu', color: 'trắng', sinh: 'Thủy', khac: 'Mộc', duocSinh: 'Thổ', biKhac: 'Hỏa' },
  'Thủy': { h: '水', slug: 'thuy', dir: 'Bắc', season: 'Đông', color: 'đen / xanh thẫm', sinh: 'Mộc', khac: 'Hỏa', duocSinh: 'Kim', biKhac: 'Thổ' },
};
export const elStems = e => STEMS.filter(s => s.e === e).map(s => s.n).join(', ');
export const elBranches = e => BRANCHES.filter(s => s.e === e).map(s => s.n).join(', ');

// Colour is never the only cue: every element also gets a glyph and a distinct shape.
export function elIcon(e, size = 12) {
  const s = size, c = s / 2;
  const shape = {
    'Mộc': `<rect x="${c - s * .17}" y="${s * .08}" width="${s * .34}" height="${s * .84}" rx="${s * .12}"/>`,
    'Hỏa': `<path d="M${c} ${s * .06}L${s * .94} ${s * .92}H${s * .06}Z"/>`,
    'Thổ': `<rect x="${s * .12}" y="${s * .12}" width="${s * .76}" height="${s * .76}" rx="${s * .06}"/>`,
    'Kim': `<circle cx="${c}" cy="${c}" r="${s * .42}"/>`,
    'Thủy': `<path d="M${s * .04} ${s * .62}Q${s * .27} ${s * .22} ${c} ${s * .62}T${s * .96} ${s * .62}" fill="none" stroke="currentColor" stroke-width="${s * .2}" stroke-linecap="round"/>`,
  }[e] || '';
  return `<svg class="el-ico" width="${s}" height="${s}" viewBox="0 0 ${s} ${s}" fill="currentColor" aria-hidden="true">${shape}</svg>`;
}
export const elChip = (e, extra = '') => e && EL[e]
  ? `<span class="el el-${EL[e].slug}" data-el="${e}">${elIcon(e)}<span class="el-h" lang="zh">${EL[e].h}</span>${esc(e)}${extra}</span>` : '';

// ----- star vocabulary (classification is presentation only) -----
const POS = new Set(['Tả Phụ', 'Hữu Bật', 'Văn Xương', 'Văn Khúc', 'Thiên Khôi', 'Thiên Việt', 'Lộc Tồn', 'Thiên Quan', 'Thiên Phúc', 'Thiên Đức', 'Nguyệt Đức', 'Long Trì', 'Phượng Các', 'Tam Thai', 'Bát Tọa', 'Bát Tòa', 'Ân Quang', 'Thiên Quý', 'Giải Thần', 'Thiên Giải', 'Địa Giải', 'Thiên Y', 'Hồng Loan', 'Thiên Hỷ', 'Thanh Long', 'Hoa Cái', 'Quốc Ấn', 'Đường Phù', 'Phúc Đức', 'Thiên Tài', 'Thiên Thọ', 'Phong Cáo', 'Thai Phụ', 'Văn Tinh', 'Thiên Trù']);
const NEG = new Set(['Kình Dương', 'Đà La', 'Hỏa Tinh', 'Linh Tinh', 'Địa Không', 'Địa Kiếp', 'Thiên Hình', 'Thiên Riêu', 'Đại Hao', 'Tiểu Hao', 'Kiếp Sát', 'Thiên Không', 'Cô Thần', 'Quả Tú', 'Bệnh Phù', 'Tang Môn', 'Bạch Hổ', 'Điếu Khách', 'Thiên Khốc', 'Thiên Hư', 'Phi Liêm', 'Quan Phù', 'Tử Phù', 'Phục Binh', 'Quan Phủ', 'Thiên Thương', 'Thiên Sứ', 'Lưu Hà', 'Thiên La', 'Địa Võng', 'Phá Toái']);
export const starKind = s => POS.has(s) ? 'pos' : NEG.has(s) ? 'neg' : 'neu';

export const TU_HOA_SHORT = { 'Hóa Lộc': 'Lộc', 'Hóa Quyền': 'Quyền', 'Hóa Khoa': 'Khoa', 'Hóa Kỵ': 'Kỵ' };

export function tenGodGroup(n = '') {
  if (/Tỉ|Tỷ|Kiếp/.test(n)) return 'Tỉ Kiếp';
  if (/Thực|Thương/.test(n)) return 'Thực Thương';
  if (/Tài/.test(n)) return 'Tài';
  if (/Ấn/.test(n)) return 'Ấn';
  if (/Quan|Sát/.test(n)) return 'Quan Sát';
  return '';
}
export const TEN_GOD_GROUPS = ['Tỉ Kiếp', 'Thực Thương', 'Tài', 'Quan Sát', 'Ấn'];

export const PILLAR_LABEL = { year: 'Năm', month: 'Tháng', day: 'Ngày', hour: 'Giờ' };
export const SIX_HOUR = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'];
export const hourBranch = h => SIX_HOUR[Math.floor(((h + 1) % 24) / 2)];

export const CLAIMS = {};
export const SOURCES = { SRC_TVDS_TAN_BIEN: 'Tử Vi Đẩu Số Tân Biên', SRC_ZIPING_ZHENQUAN: 'Tử Bình Chân Thuyên (子平真詮)' };
export const SRC_OK = {};
const cap = t => t ? t[0].toUpperCase() + t.slice(1) : t;
/** Vietnamese phrase for a claim id; falls back to a neutral prettified id (never invented prose). */
export const claimPhrase = (c, effect) => (effect === 'limit' && CLAIMS['limit:' + c]) || CLAIMS[c] || String(c).replace(/_/g, ' ');
export const claimLabel = c => cap(claimPhrase(c));
export const claimKnown = c => !!CLAIMS[c];
/** Loads Vietnamese claim phrases and source names; retries because a cold container may answer 5xx once. */
export async function loadMeta() {
  for (let i = 0; i < 4; i++) {
    try {
      const get = async u => { const x = await fetch(u); if (!x.ok) throw new Error(String(x.status)); return x.json(); };
      const [c, r] = await Promise.all([get('/api/claims'), get('/api/rules')]);
      Object.assign(CLAIMS, c);
      (r.sources || []).forEach(s => { SOURCES[s.id] = s.title; SRC_OK[s.id] = !!s.verified; });
      return;
    } catch { await new Promise(r => setTimeout(r, 500 * (i + 1))); }
  } // still failing: readings without a known phrase are hidden in 'Dễ hiểu' instead of showing raw ids
}
export const palaceOfSubject = s => /^palace:/.test(s) ? s.slice(7) : null;

const sleepMs = ms => new Promise(r => setTimeout(r, ms));
/** POST JSON. Retries network errors and 5xx (the engine container can drop a request under load); never retries 4xx. */
/** Birth data on screen, wrapped so the "Ẩn thông tin sinh" export option can hide it (body.hide-birth). has = false: the page never
 *  received the value (a share link with the birth hidden), so only the stand-in shows ("ẩn", or alt, e.g. "··/··/" before a year). */
export const bd = (v, has = v !== undefined && v !== null, alt = 'ẩn') => has ? `<span class="bd">${v}</span><span class="bd-x">${alt}</span>` : `<span class="bd-x bd-on">${alt}</span>`;
export const DM = '··/··/';

/** Set while a share link is open (share.js): engine calls then go through /api/share/<id>/<endpoint>, which adds the stored birth. */
export const shareMode = { id: null };
const SHARED = /^\/api\/(chart|reasoning|analysis|synthesis|interpretation|interpret|year|formations)$/;
const VIEWER = ['to_year', 'chapter', 'mode', 'experimental', 'dignity_school', 'tu_hoa_table', 'tieu_han_rule', 'luu_ha_table'];

export async function post(u, b, { retries = 3 } = {}) {
  if (shareMode.id && SHARED.test(u)) { b = Object.fromEntries(VIEWER.filter(k => b?.[k] !== undefined).map(k => [k, b[k]])); u = `/api/share/${shareMode.id}/${u.slice(5)}`; }
  let last;
  for (let i = 0; i <= retries; i++) {
    try {
      const r = await fetch(u, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(b) });
      let j = {};
      try { j = await r.json(); } catch { /* non-JSON error body */ }
      if (r.ok) return j;
      if (r.status < 500) throw Object.assign(new Error(typeof j.detail === 'string' ? j.detail : (r.status === 422 ? 'Dữ liệu ngày giờ sinh chưa hợp lệ.' : 'Yêu cầu chưa hợp lệ.')), { final: true });
      last = new Error('Máy chủ chưa phản hồi. Vui lòng thử lại.');
    } catch (e) { if (e.final) throw e; last = new Error('Máy chủ chưa phản hồi. Vui lòng thử lại.'); }
    if (i < retries) await sleepMs(500 * (i + 1));
  }
  throw last;
}
