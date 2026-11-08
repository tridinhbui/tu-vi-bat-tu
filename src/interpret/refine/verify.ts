// The checks a model-refined paragraph must pass before it may replace the deterministic one (plan docs/plans/THIEN-BAN-33-REVIEW-PLAN.md
// G10.7, cách 2; owner decision Q5 2026-11-08: "Thử lớp LLM có kiểm"). Deterministic: the model may only re-say what the draft says.
//   map        every new sentence names the draft sentences it says (src), and every draft sentence is said by at least one new sentence
//   entities   every proper term of a new sentence (star, palace, branch, stem, Hóa, element, Thập thần, book, number) is in its source
//              sentences, and every proper term of a draft sentence is still in the new sentences that say it
//   content    a book or computed sentence keeps most of its words (the book's claim is not paraphrased away)
//   limits     a draft sentence with a limiting word (song, nhưng, chưa, dễ, có thể, phần nào, nếu …) is said with one
//   words      no method word, no absolute, no grave outcome word the draft did not have
//   length     the paragraph stays within the draft's length band
import type { ProseSentence } from '../prose/realize.ts';
import { META, ABSOLUTE } from '../prose/lint.ts';
import SEV from '../../../engine/data/kg/claim_severity.json' with { type: 'json' };

export interface RefinedSentence { text: string; src: number[] }
export interface Verdict { ok: boolean; reasons: string[] }

const MAJORS = ['Tử Vi', 'Thiên Cơ', 'Thái Dương', 'Vũ Khúc', 'Thiên Đồng', 'Liêm Trinh', 'Thiên Phủ', 'Thái Âm', 'Tham Lang', 'Cự Môn', 'Thiên Tướng', 'Thiên Lương', 'Thất Sát', 'Phá Quân'];
const MINORS = ['Tả Phụ', 'Hữu Bật', 'Văn Xương', 'Văn Khúc', 'Thiên Khôi', 'Thiên Việt', 'Lộc Tồn', 'Thiên Mã', 'Kình Dương', 'Đà La', 'Hỏa Tinh', 'Linh Tinh', 'Địa Không', 'Địa Kiếp',
  'Thiên Hình', 'Thiên Riêu', 'Thiên Khốc', 'Thiên Hư', 'Đại Hao', 'Tiểu Hao', 'Tang Môn', 'Bạch Hổ', 'Điếu Khách', 'Quan Phù', 'Phục Binh', 'Cô Thần', 'Quả Tú', 'Đẩu Quân', 'Thiên Không',
  'Phá Toái', 'Kiếp Sát', 'Đào Hoa', 'Hồng Loan', 'Thiên Hỷ', 'Bệnh Phù', 'Thiên Thọ', 'Thiên Y', 'Đế Vượng', 'Trường Sinh', 'Mộc Dục', 'Quan Đới', 'Lâm Quan', 'Thái Tuế', 'Long Trì', 'Phượng Các',
  'Ân Quang', 'Thiên Quý', 'Tam Thai', 'Bát Tọa', 'Thiên Giải', 'Địa Giải', 'Giải Thần', 'Thiên Quan', 'Thiên Phúc', 'Hoa Cái', 'Thiên Đức', 'Nguyệt Đức', 'Long Đức', 'Phúc Đức', 'Tấu Thư', 'Bác Sĩ',
  'Lực Sĩ', 'Thanh Long', 'Tướng Quân', 'Quốc Ấn', 'Đường Phù', 'Lưu Hà', 'Thiên Trù', 'Văn Tinh', 'Thiên La', 'Địa Võng', 'Tuần', 'Triệt', 'Quang Quý', 'Song Hao', 'Khôi Việt', 'Xương Khúc', 'Tả Hữu'];
const HOA = ['Hóa Lộc', 'Hóa Quyền', 'Hóa Khoa', 'Hóa Kỵ'];
const PALACES = ['Mệnh', 'Phụ Mẫu', 'Phúc Đức', 'Điền Trạch', 'Quan Lộc', 'Nô Bộc', 'Thiên Di', 'Tật Ách', 'Tài Bạch', 'Tử Tức', 'Phu Thê', 'Huynh Đệ', 'Thân'];
const BRANCHES = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'];
const STEMS = ['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý'];
const BAZI = ['Tỉ Kiên', 'Kiếp Tài', 'Thực Thần', 'Thương Quan', 'Thiên Tài', 'Chính Tài', 'Chính Quan', 'Thiên Ấn', 'Chính Ấn', 'Tỉ Kiếp', 'Thực Thương', 'Quan Sát', 'Kim', 'Mộc', 'Thủy', 'Hỏa', 'Thổ'];
const BOOKS = ['Khảo Luận', 'Thực Hành', 'Toàn Thư', 'Hàm Số', 'Thiệu Vĩ Hoa', 'Nghiệm Lý'];
/** longest first, so "Thiên Đồng" is one term and not "Thiên" + "Đồng"; a term is a whole word sequence (no letter on either side) */
const TERMS = [...new Set([...MAJORS, ...MINORS, ...HOA, ...PALACES, ...BRANCHES, ...STEMS, ...BAZI, ...BOOKS])].sort((a, b) => b.length - a.length);
const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const TERM_RE = new RegExp(`(?<![\\p{L}])(${TERMS.map(esc).join('|')})(?![\\p{L}])`, 'gu');
const NUM_RE = /\d+(?:[.,]\d+)?/g;

/** the proper terms and numbers of a text, as a set ("Thiên Cơ", "Phu Thê", "40", …); a capitalised term only (Kim, Hỏa …) */
export function entities(text: string): Set<string> {
  const out = new Set<string>();
  for (const m of text.matchAll(TERM_RE)) out.add(m[1]);
  for (const m of text.matchAll(NUM_RE)) out.add(m[0].replace(',', '.'));
  return out;
}

// \b is ASCII-only in JS even with /u: letters with diacritics need explicit letter look-arounds
const LIMIT = /(?<![\p{L}])(song|nhưng|chưa|dễ|có thể|phần nào|nếu|tùy|có điều kiện|không|chỉ|kém|bớt|giảm|hạn chế|vướng|cản|ngại|tuy|dù|mặc dù|e rằng|khó)(?![\p{L}])/iu;
const STOP = new Set(['và', 'là', 'của', 'có', 'thì', 'nên', 'mà', 'với', 'cho', 'ở', 'tại', 'được', 'các', 'những', 'một', 'này', 'ấy', 'đó', 'cũng', 'lại', 'đã', 'đang', 'sẽ', 'để', 'trong', 'khi',
  'về', 'từ', 'như', 'thế', 'vì', 'do', 'nhờ', 'theo', 'người', 'lá', 'số', 'cung', 'sao', 'rằng', 'thường', 'vào', 'ra', 'lên', 'xuống']);
const words = (t: string) => t.toLocaleLowerCase('vi').replace(/[“”"(),.;:!?–-]/g, ' ').split(/\s+/).filter(w => w && !STOP.has(w));
const GRAVE = Object.entries((SEV as { classes: Record<string, { re: string }>; grave: string[] }).classes)
  .filter(([c]) => (SEV as { grave: string[] }).grave.includes(c)).map(([, v]) => new RegExp(v.re, 'iu'));

/** One paragraph: the draft sentences, the model's sentences. */
export function verifyParagraph(draft: ProseSentence[], out: RefinedSentence[], o: { maxGrow?: number; minShrink?: number } = {}): Verdict {
  const reasons: string[] = [];
  const n = draft.length;
  if (!out.length) return { ok: false, reasons: ['không có câu nào'] };
  // map
  for (const [j, s] of out.entries()) {
    if (!s.src.length || s.src.some(i => !Number.isInteger(i) || i < 0 || i >= n)) reasons.push(`câu ${j}: nguồn không hợp lệ (${s.src.join(',')})`);
  }
  if (reasons.length) return { ok: false, reasons };
  const covering = (i: number) => out.filter(s => s.src.includes(i));
  for (let i = 0; i < n; i++) if (!covering(i).length) reasons.push(`câu nháp ${i} không được nói lại`);
  // entities
  for (const [j, s] of out.entries()) {
    const src = s.src.map(i => draft[i].text).join(' ');
    const have = entities(src);
    const extra = [...entities(s.text)].filter(e => !have.has(e));
    if (extra.length) reasons.push(`câu ${j}: thêm ${extra.join(', ')}`);
  }
  for (let i = 0; i < n; i++) {
    const said = entities(covering(i).map(s => s.text).join(' '));
    const lost = [...entities(draft[i].text)].filter(e => !said.has(e));
    if (lost.length) reasons.push(`câu nháp ${i}: mất ${lost.join(', ')}`);
  }
  // content and limits
  for (let i = 0; i < n; i++) {
    const d = draft[i], said = covering(i).map(s => s.text).join(' ');
    const dw = new Set(words(d.text)), sw = new Set(words(said));
    const keep = dw.size ? [...dw].filter(w => sw.has(w)).length / dw.size : 1;
    const need = d.trace.basis === 'sach' || d.trace.basis === 'tinh_toan' ? 0.6 : 0.35;
    if (keep < need) reasons.push(`câu nháp ${i}: giữ ${(100 * keep).toFixed(0)}% chữ (cần ${100 * need}%)`);
    if (LIMIT.test(d.text) && !LIMIT.test(said)) reasons.push(`câu nháp ${i}: mất từ hạn định`);
  }
  // words
  const draftText = draft.map(s => s.text).join(' '), low = ` ${draftText.toLocaleLowerCase('vi')}`;
  for (const [j, s] of out.entries()) {
    const t = ` ${s.text.toLocaleLowerCase('vi')}`;
    for (const w of META) if (t.includes(` ${w}`) && !low.includes(` ${w}`)) reasons.push(`câu ${j}: từ phương pháp "${w.trim()}"`);
    for (const w of [...ABSOLUTE, 'cả đời']) if (t.includes(w) && !low.includes(w)) reasons.push(`câu ${j}: từ tuyệt đối "${w}"`);
    for (const re of GRAVE) if (re.test(s.text) && !re.test(draftText)) reasons.push(`câu ${j}: từ nặng (${re.source.slice(0, 20)}…)`);
    if (/không phải[^.]{0,60}mà là/iu.test(s.text)) reasons.push(`câu ${j}: lối "không phải… mà là…"`);
  }
  // length
  const dl = draftText.split(/\s+/).length, ol = out.map(s => s.text).join(' ').split(/\s+/).length;
  if (ol > dl * (o.maxGrow ?? 1.3)) reasons.push(`dài hơn nháp ${(100 * (ol / dl - 1)).toFixed(0)}%`);
  if (ol < dl * (o.minShrink ?? 0.6)) reasons.push(`ngắn hơn nháp ${(100 * (1 - ol / dl)).toFixed(0)}%`);
  return { ok: !reasons.length, reasons };
}
