// Position audit of the Tử Vi rule packs (plan quirky-tinkering-rabin R1, "không suy diễn sai"). For every Tử Vi rule in engine/data/pack_*.json
// it compares what the description says about WHERE each star or Hóa stands (đồng cung / tọa / thủ / chiếu / xung / hội / tam hợp / giáp / gặp)
// with the fact scope the rule's `conditions` actually test, and flags:
//   wider        the condition accepts positions the book did not state (e.g. book "đồng cung", condition tam phương)
//   narrower     the book allows positions the condition does not test (e.g. book "hội", condition own palace only)
//   mismatch     both at once (e.g. book "giáp", condition tam phương)
//   mixed        one rule tests atoms in different scopes (own palace and tam phương …): prose must not voice them all as "đồng cung"
//   hoa_unbound  the rule tests a Hóa by name in a palace (facts list Hóa names per palace, not the carrying star) while the book binds the
//                Hóa to a star ("Thái Âm hãm hóa Quyền"), or a star that could carry it is tested in the same scope
//   dead         the condition tests a Hóa name in a star list, which never holds (facts keep Hóa out of star lists)
// Each flag is `certain` (an explicit position word governs the mention, or a system note fixes the reading) or `needs-reading` (the description
// is ambiguous: 'gặp', 'có', 'chiếu' without 'xung'/'tam hợp', an implied subject …). The packs are NOT edited (they feed the live Python
// /api/reasoning); the result is a draft guard file that the reasoner applies on top.
//   node tools/interpret/audit_positions.ts   → docs/audit/POSITION-AUDIT.md + engine/data/kg/position_guards.json
import { readFileSync, writeFileSync, readdirSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { gunzipSync } from 'node:zlib';
import { CAT, SAT, triggerAtoms } from '../../src/interpret/kg/atoms.ts';
import { evaluate } from '../../src/interpret/dsl.ts';
import { guardHolds } from '../../src/interpret/reason/positions.ts';

const ROOT = join(import.meta.dirname, '..', '..');
const DATA = join(ROOT, 'engine', 'data');

// ---- positions as sets over {self, opp, trine, flank, nhi_hop} ----
export type Pos = 'self' | 'opp' | 'trine' | 'flank' | 'nhi_hop';
const TP: Pos[] = ['self', 'opp', 'trine'];
type Scope = 'self' | 'opp' | 'trine' | 'tp' | 'flank' | 'nhi_hop';
const SCOPE_POS: Record<Scope, Pos[]> = { self: ['self'], opp: ['opp'], trine: ['trine'], tp: TP, flank: ['flank'], nhi_hop: ['nhi_hop'] };
const SCOPE_LABEL: Record<Scope, string> = { self: 'own palace', opp: 'xung chiếu', trine: 'tam hợp', tp: 'tam phương', flank: 'giáp', nhi_hop: 'nhị hợp' };

/** Scope a fact tests, or null for facts that are not star/Hóa membership. */
function factScope(fact: string): Scope | null {
  if (fact === 'palace.own_stars' || fact === 'palace.own_major_stars' || fact === 'palace.tu_hoa' || /^palace\.rel\.self_/.test(fact)) return 'self';
  if (/^palace\.rel\.opp_/.test(fact)) return 'opp';
  if (/^palace\.rel\.trine[12]?_/.test(fact)) return 'trine';
  if (/^palace\.(tam_phuong_|rel\.tp_)/.test(fact)) return 'tp';
  if (/^palace\.(rel\.flank|neighbor_)/.test(fact)) return 'flank';
  if (/^palace\.rel\.nhi_hop_/.test(fact)) return 'nhi_hop';
  return null;
}
const KHI_SCOPE: Record<string, Scope> = { self: 'self', tp: 'tp', flank: 'flank' };
const HOA = ['Hóa Lộc', 'Hóa Quyền', 'Hóa Khoa', 'Hóa Kỵ'];
const MAJORS = ['Tử Vi', 'Thiên Cơ', 'Thái Dương', 'Vũ Khúc', 'Thiên Đồng', 'Liêm Trinh', 'Thiên Phủ', 'Thái Âm', 'Tham Lang', 'Cự Môn', 'Thiên Tướng',
  'Thiên Lương', 'Thất Sát', 'Phá Quân'];

// ---- condition side ----
interface Leaf { name: string; kind: 'star' | 'hoa'; scope: Scope; fact: string; neg: boolean; group?: 'SAT' | 'CAT' }
interface RuleScan { leaves: Leaf[]; refs: string[]; of: string; yearStem: boolean; vcd: boolean; dead: string[]; branches: string[] }

function scanConditions(expr: any): RuleScan {
  const out: RuleScan = { leaves: [], refs: [], of: '@palace', yearStem: false, vcd: false, dead: [], branches: [] };
  const names: string[] = [];
  const walk = (e: any, neg: boolean) => {
    if (!e || typeof e !== 'object') return;
    for (const k of ['all', 'any', 'count']) if (Array.isArray(e[k])) e[k].forEach((x: any) => walk(x, neg));
    if (e.not) walk(e.not, !neg);
    if (e.ref) { out.refs.push(`ref:${e.ref.palace}.${String(e.ref.fact).replace('palace.', '')}`); return; }
    if (typeof e.fact !== 'string') return;
    const f: string = e.fact, op = e.operator ?? 'eq';
    if (f === 'palace.name' && !neg) { if (typeof e.value === 'string') names.push(e.value); return; }
    if (f === 'chart.year_stem') out.yearStem = true;
    if (f === 'palace.branch' && !neg && (op === 'in' || op === 'eq')) out.branches.push(...(Array.isArray(e.value) ? e.value : [e.value]));
    if (f === 'palace.has_no_major' && e.value === true && !neg) out.vcd = true;
    const khi = /^palace\.khi\.(sat|cat)_(self|tp|flank)$/.exec(f);
    if (khi) {
      // a count ≤ 0 is an absence; any positive count is presence of members of the group
      const isAbsence = (op === 'lte' && Number(e.value) <= 0) || (op === 'eq' && Number(e.value) === 0) || (op === 'lt' && Number(e.value) <= 1);
      const grp = khi[1] === 'sat' ? 'SAT' : 'CAT';
      for (const s of grp === 'SAT' ? SAT : CAT) out.leaves.push({ name: s, kind: 'star', scope: KHI_SCOPE[khi[2]], fact: f, neg: neg !== isAbsence, group: grp });
      return;
    }
    if (f === 'palace.sat_pha_tham_in_tam_phuong' && e.value === true) {
      for (const s of ['Thất Sát', 'Phá Quân', 'Tham Lang']) out.leaves.push({ name: s, kind: 'star', scope: 'tp', fact: f, neg });
      return;
    }
    const sc = factScope(f);
    if (!sc || !['contains', 'contains_any', 'contains_all'].includes(op)) return;
    const vals = (Array.isArray(e.value) ? e.value : [e.value]).filter((v: unknown) => typeof v === 'string') as string[];
    for (const v of vals) {
      const kind = HOA.includes(v) ? 'hoa' : 'star';
      if (kind === 'hoa' && /_(stars|majors)$/.test(f)) out.dead.push(`${f} contains ${v}`);
      out.leaves.push({ name: v, kind, scope: sc, fact: f, neg });
    }
  };
  walk(expr, false);
  if (names.length === 1) out.of = names[0];
  return out;
}

// ---- description side: a small tokenizer for the Vietnamese position phrases the packs use ----
type Strength = 3 | 2 | 1; // 3 explicit or documented, 2 weak ('gặp', 'có', 'thêm' …), 1 implied (an atom with no position word)
interface Kw { text: string; pos: Pos[]; strength: Strength; family: 'plain' | 'chieu' | 'gap' | 'loc' }
const KW: Kw[] = [
  { text: 'đồng cung', pos: ['self'], strength: 3, family: 'plain' }, { text: 'cùng đóng', pos: ['self'], strength: 3, family: 'plain' }, { text: 'đóng', pos: ['self'], strength: 3, family: 'plain' }, { text: 'cùng cung', pos: ['self'], strength: 3, family: 'plain' },
  { text: 'cùng thủ', pos: ['self'], strength: 3, family: 'plain' }, { text: 'tọa thủ', pos: ['self'], strength: 3, family: 'plain' },
  { text: 'tọa', pos: ['self'], strength: 3, family: 'plain' }, { text: 'thủ', pos: ['self'], strength: 3, family: 'plain' },
  { text: 'xung chiếu', pos: ['opp'], strength: 3, family: 'plain' }, { text: 'chính chiếu', pos: ['opp'], strength: 3, family: 'plain' },
  { text: 'đối chiếu', pos: ['opp'], strength: 3, family: 'plain' }, { text: 'xung', pos: ['opp'], strength: 3, family: 'plain' },
  // 'tam hợp' is loose in the books (KL p.83 "tam hợp Đào, Hồng, Hỷ": Hồng Loan and Thiên Hỷ always face each other), so it is never certain
  { text: 'tam hợp chiếu', pos: ['trine'], strength: 3, family: 'chieu' }, { text: 'tam hợp', pos: ['trine'], strength: 3, family: 'chieu' },
  { text: 'hội chiếu', pos: TP, strength: 3, family: 'plain' }, { text: 'hội họp', pos: TP, strength: 3, family: 'plain' },
  { text: 'hội tụ', pos: TP, strength: 3, family: 'plain' }, { text: 'tam phương tứ chính', pos: TP, strength: 3, family: 'plain' }, { text: 'tam phương', pos: TP, strength: 3, family: 'plain' },
  { text: 'hội', pos: TP, strength: 3, family: 'plain' },
  { text: 'hợp chiếu', pos: ['opp', 'trine'], strength: 3, family: 'chieu' }, { text: 'củng chiếu', pos: ['opp', 'trine'], strength: 3, family: 'chieu' },
  { text: 'chiếu', pos: ['opp', 'trine'], strength: 3, family: 'chieu' }, { text: 'chầu', pos: ['opp', 'trine'], strength: 3, family: 'chieu' },
  { text: 'giáp', pos: ['flank'], strength: 3, family: 'plain' }, { text: 'kẹp', pos: ['flank'], strength: 3, family: 'plain' },
  { text: 'nhị hợp', pos: ['nhi_hop'], strength: 3, family: 'plain' },
  { text: 'gặp', pos: TP, strength: 2, family: 'gap' }, { text: 'hợp với', pos: TP, strength: 2, family: 'gap' }, { text: 'hợp', pos: TP, strength: 2, family: 'gap' },
  { text: 'tụ vào', pos: TP, strength: 2, family: 'gap' }, { text: 'triều viên', pos: ['opp', 'trine'], strength: 3, family: 'chieu' }, { text: 'triều', pos: ['opp', 'trine'], strength: 3, family: 'chieu' },
  { text: 'đi kèm', pos: ['self'], strength: 2, family: 'plain' },
  { text: 'đi với', pos: ['self'], strength: 2, family: 'plain' }, { text: 'đi cùng', pos: ['self'], strength: 2, family: 'plain' },
  { text: 'thêm', pos: ['self'], strength: 2, family: 'plain' }, { text: 'có', pos: ['self'], strength: 2, family: 'plain' },
  { text: 'ở', pos: ['self'], strength: 2, family: 'loc' }, { text: 'tại', pos: ['self'], strength: 2, family: 'loc' }, { text: 'cư', pos: ['self'], strength: 2, family: 'loc' },
];
const PLACES = ['Mệnh', 'Thân', 'Huynh Đệ', 'Phu Thê', 'Tử Tức', 'Tài Bạch', 'Tật Ách', 'Thiên Di', 'Nô Bộc', 'Quan Lộc', 'Điền Trạch', 'Phúc Đức', 'Phụ Mẫu',
  'Bào', 'Tài', 'Quan', 'Phúc', 'Điền', 'Phu', 'Thê', 'Tật', 'Di', 'Nô', 'Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Dậu', 'Tuất', 'Hợi', 'Tứ Mộ',
  'Tứ Mã', 'Tứ Sinh', 'tứ mộ', 'Thủy nhị cục', 'Mộc tam cục', 'Kim tứ cục', 'Thổ ngũ cục', 'Hỏa lục cục'];
const BRANCHES = new Set(['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi', 'Tứ Mộ', 'Tứ Mã', 'Tứ Sinh', 'tứ mộ']);
const SHORT: Array<[string, string[]]> = [
  ['Tử', ['Tử Vi']], ['Phủ', ['Thiên Phủ']], ['Vũ', ['Vũ Khúc']], ['Tướng', ['Thiên Tướng']], ['Cơ', ['Thiên Cơ']], ['Nguyệt', ['Thái Âm']], ['Nhật', ['Thái Dương']],
  ['Đồng', ['Thiên Đồng']], ['Lương', ['Thiên Lương']], ['Cự', ['Cự Môn']], ['Sát', ['Thất Sát']], ['Phá', ['Phá Quân']], ['Liêm', ['Liêm Trinh']], ['Tham', ['Tham Lang']],
  ['Kình', ['Kình Dương']], ['Đà', ['Đà La']], ['Hỏa', ['Hỏa Tinh']], ['Linh', ['Linh Tinh']], ['Không', ['Địa Không', 'Thiên Không']], ['Kiếp', ['Địa Kiếp']],
  ['Xương', ['Văn Xương']], ['Khúc', ['Văn Khúc']], ['Tả', ['Tả Phụ']], ['Hữu', ['Hữu Bật']], ['Khôi', ['Thiên Khôi']], ['Việt', ['Thiên Việt']], ['Mã', ['Thiên Mã']],
  ['Hồng', ['Hồng Loan']], ['Đào', ['Đào Hoa']], ['Hình', ['Thiên Hình']], ['Riêu', ['Thiên Riêu']], ['Hỷ', ['Thiên Hỷ']], ['Khoa', ['Hóa Khoa']], ['Quyền', ['Hóa Quyền']], ['Kỵ', ['Hóa Kỵ']],
  ['Lộc', ['Hóa Lộc', 'Lộc Tồn']], ['Hao', ['Đại Hao', 'Tiểu Hao']],
  ['Tam Hóa', ['Hóa Lộc', 'Hóa Quyền', 'Hóa Khoa']], ['Khôi Việt', ['Thiên Khôi', 'Thiên Việt']],
];
const GROUPS: Array<[string, string[]]> = [
  ['sát tinh', SAT], ['lục sát', SAT], ['tứ sát', ['Kình Dương', 'Đà La', 'Hỏa Tinh', 'Linh Tinh']], ['hung tinh', SAT], ['sát diệu', SAT], ['hung sát', SAT], ['sát', SAT],
  ['cát tinh', CAT], ['lục cát', CAT], ['văn tinh', ['Văn Xương', 'Văn Khúc']],
];
// case-insensitive compounds that name stars, not groups
const COMPOUNDS: Array<[string, string[]]> = [['song hao', ['Đại Hao', 'Tiểu Hao']], ['song lộc', ['Hóa Lộc', 'Lộc Tồn']]];
const NEG_WORDS = ['không', 'tránh', 'chẳng', 'chưa', 'không bị', 'thiếu'];
const HARD = ['mà', 'nhưng', 'lại', 'nếu', 'còn', 'thì'];
// words that may sit between a position word and its object ("giáp hai bên", "có sao Tử Vi")
const FILLER = new Set(['cung', 'hai', 'bên', 'về', 'vào', 'đều', 'cả', 'các', 'những', 'sao', 'chỉ', 'cùng', 'thêm', 'nhiều', 'đủ']);

type Tok = { t: 'atom'; names: string[]; text: string; at: number; neg: boolean } | { t: 'kw'; kw: Kw; text: string; at: number }
  | { t: 'place'; text: string; branch: boolean; at: number } | { t: 'or'; at: number } | { t: 'comma'; at: number } | { t: 'hard'; at: number; neg: boolean }
  | { t: 'sym'; at: number } | { t: 'pass'; at: number } | { t: 'word'; text: string; at: number };

const isL = (c: string | undefined) => !!c && /[\p{L}\p{M}]/u.test(c);
function tokenize(text: string, fullNames: string[]): Tok[] {
  type Cand = { text: string; cs: boolean; make: (s: string, at: number) => Tok };
  const cands: Cand[] = [];
  for (const n of fullNames) cands.push({ text: n, cs: false, make: (s, at) => ({ t: 'atom', names: [n], text: s, at, neg: false }) });
  for (const [s, ns] of SHORT) cands.push({ text: s, cs: true, make: (x, at) => ({ t: 'atom', names: ns, text: x, at, neg: false }) });
  for (const [s, ns] of COMPOUNDS) cands.push({ text: s, cs: false, make: (x, at) => ({ t: 'atom', names: ns, text: x, at, neg: false }) });
  for (const [s, ns] of GROUPS) cands.push({ text: s, cs: false, make: (x, at) => ({ t: 'atom', names: ns, text: x, at, neg: false }) });
  for (const k of KW) cands.push({ text: k.text, cs: true, make: (x, at) => ({ t: 'kw', kw: k, text: x, at }) });
  for (const p of PLACES) cands.push({ text: p, cs: true, make: (x, at) => ({ t: 'place', text: x, branch: BRANCHES.has(p), at }) });
  for (const w of NEG_WORDS) cands.push({ text: w, cs: false, make: (_x, at) => ({ t: 'hard', at, neg: true }) });
  for (const w of HARD) cands.push({ text: w, cs: false, make: (_x, at) => ({ t: 'hard', at, neg: false }) });
  for (const w of ['hoặc', 'và', 'với', 'hay']) cands.push({ text: w, cs: false, make: (_x, at) => ({ t: 'or', at }) });
  for (const w of ['ngược lại', 'nhau', 'tương']) cands.push({ text: w, cs: false, make: (_x, at) => ({ t: 'sym', at }) });
  for (const w of ['được', 'bị']) cands.push({ text: w, cs: false, make: (_x, at) => ({ t: 'pass', at }) });
  cands.sort((a, b) => b.text.length - a.text.length);
  const lower = text.toLowerCase(), out: Tok[] = [];
  let i = 0;
  while (i < text.length) {
    const c = text[i];
    if (c === ',' || c === '/') { out.push({ t: 'comma', at: i }); i++; continue; }
    if ('();:.'.includes(c)) { out.push({ t: 'hard', at: i, neg: false }); i++; continue; }
    if (!isL(c)) { i++; continue; }
    if (isL(text[i - 1])) { i++; continue; }
    let hit: Tok | null = null, len = 0;
    for (const k of cands) {
      const seg = k.cs ? text.slice(i, i + k.text.length) : lower.slice(i, i + k.text.length);
      if (seg === (k.cs ? k.text : k.text.toLowerCase()) && !isL(text[i + k.text.length])) { hit = k.make(text.slice(i, i + k.text.length), i); len = k.text.length; break; }
    }
    if (hit) { out.push(hit); i += len; continue; }
    let j = i; while (j < text.length && isL(text[j])) j++;
    out.push({ t: 'word', text: text.slice(i, j), at: i });
    i = j;
  }
  return out;
}

export interface Mention { names: string[]; text: string; pos: Pos[]; strength: Strength; family: Kw['family'] | 'implied' | 'sym'; kw: string; neg: boolean; documented?: boolean; group?: boolean }
/** What the description is read against: the palace the rule is on and the branches it requires (to resolve "ở Tỵ", "ở Thiên Di"). */
export interface DescCtx { of: string; branches: string[] }

const PALACE_ORDER = ['Mệnh', 'Phụ Mẫu', 'Phúc Đức', 'Điền Trạch', 'Quan Lộc', 'Nô Bộc', 'Thiên Di', 'Tật Ách', 'Tài Bạch', 'Tử Tức', 'Phu Thê', 'Huynh Đệ'];
const SHORT_PALACE: Record<string, string> = { Tài: 'Tài Bạch', Quan: 'Quan Lộc', Phúc: 'Phúc Đức', Điền: 'Điền Trạch', Phu: 'Phu Thê', Thê: 'Phu Thê', Tật: 'Tật Ách', Di: 'Thiên Di', Nô: 'Nô Bộc', Bào: 'Huynh Đệ' };
const BRANCH_ORDER = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'];
const offsetPos = (d: number): Pos[] | null => { d = ((d % 12) + 12) % 12; return d === 0 ? ['self'] : d === 6 ? ['opp'] : d === 4 || d === 8 ? ['trine'] : d === 1 || d === 11 ? ['flank'] : null; };
/** Seat stated by "ở/tại <place>" relative to the rule's palace; null when it cannot be resolved (then: own palace, weak). */
function placePos(place: string, ctx: DescCtx): { pos: Pos[]; explicit: boolean } | null {
  const pal = SHORT_PALACE[place] ?? place;
  if (pal === 'Thân') return null;
  const a = PALACE_ORDER.indexOf(ctx.of), b = PALACE_ORDER.indexOf(pal);
  if (b >= 0) { if (a < 0) return null; const p = offsetPos(b - a); return p ? { pos: p, explicit: true } : null; }
  if (/^tứ (mộ|mã|sinh)$/i.test(place)) return { pos: ['self'], explicit: true };
  const bi = BRANCH_ORDER.indexOf(place);
  if (bi < 0) return null;
  if (!ctx.branches.length || ctx.branches.includes(place)) return { pos: ['self'], explicit: ctx.branches.length > 0 };
  const p = offsetPos(bi - BRANCH_ORDER.indexOf(ctx.branches[0]));
  return p ? { pos: p, explicit: ctx.branches.length === 1 } : null;
}

/** The book side: for each star mention of the description, the position its governing word states. */
export function parseDescription(desc: string, fullNames: string[], ctx: DescCtx = { of: '@palace', branches: [] }): { mentions: Mention[]; bindings: Array<{ star: string; hoa: string }>; notes: Record<string, Pos[]> } {
  const notes: Record<string, Pos[]> = {};
  for (const m of desc.matchAll(/'([^']+)'\s+(?:được\s+)?đọc là\s+([^;\[]+)/g)) {
    const r = m[2].toLowerCase();
    const pos: Pos[] | null = /đồng cung/.test(r) ? ['self'] : /xung chiếu/.test(r) ? ['opp'] : /hội|tam phương/.test(r) ? TP : /giáp/.test(r) ? ['flank'] : null;
    if (pos) notes[m[1].toLowerCase()] = pos;
  }
  // the book paraphrase: after the section header's colon, up to the citation or the first top-level ';' (system notes follow it)
  let body = desc.replace(/\[[^\]]*\]\s*$/, '');
  const colon = body.indexOf(': ');
  if (colon >= 0) body = body.slice(colon + 2);
  let depth = 0, cut = body.length;
  for (let i = 0; i < body.length; i++) { const c = body[i]; if (c === '(') depth++; else if (c === ')') depth--; else if (c === ';' && depth === 0) { cut = i; break; } }
  body = body.slice(0, cut);
  const toks = tokenize(body, fullNames);
  // Hóa bound to a star: "Thiên Cơ hóa Kỵ", "Thái Âm hãm hóa Quyền"
  const DIG = /^(miếu|vượng|đắc|bình|hãm|địa|lợi)$/i;
  const bindings: Array<{ star: string; hoa: string }> = [];
  for (let k = 0; k < toks.length; k++) {
    const a = toks[k];
    if (a.t !== 'atom' || !a.names.some(n => HOA.includes(n)) || !/^h[óo]a\s/i.test(a.text)) continue;
    let p = k - 1;
    if (a.text.startsWith('hóa')) while (p >= 0 && toks[p].t !== 'atom') p--; // the verb "hóa": "Cự Môn hãm ở Thìn/Tuất nhưng hóa Lộc"
    else while (p >= 0 && toks[p].t === 'word' && DIG.test((toks[p] as any).text)) p--;
    const s = toks[p];
    if (s && s.t === 'atom' && s.names.length === 1 && MAJORS.concat(['Văn Xương', 'Văn Khúc', 'Tả Phụ', 'Hữu Bật']).includes(s.names[0]))
      bindings.push({ star: s.names[0], hoa: a.names.find(n => HOA.includes(n))! });
  }
  // merge "kw hoặc kw" into one keyword with the union of positions
  const merged: Tok[] = [];
  for (const t of toks) {
    const prev = merged[merged.length - 1], prev2 = merged[merged.length - 2];
    if (t.t === 'kw' && prev?.t === 'or' && prev2?.t === 'kw') {
      merged.splice(merged.length - 2, 2);
      merged[merged.length - 1] = { ...prev2, kw: { ...prev2.kw, text: `${prev2.kw.text} hoặc ${t.kw.text}`, pos: [...new Set([...prev2.kw.pos, ...t.kw.pos])], strength: Math.min(prev2.kw.strength, t.kw.strength) as Strength, family: prev2.kw.family === 'plain' ? t.kw.family : prev2.kw.family } };
      continue;
    }
    merged.push(t);
  }
  // hard clauses → soft segments (commas)
  const clauses: Tok[][] = [[]];
  let neg = false;
  for (const t of merged) {
    if (t.t === 'hard') { clauses.push([]); neg = t.neg; continue; }
    if (t.t === 'atom') t.neg = neg;
    clauses[clauses.length - 1].push(t);
  }
  type Asg = { pos: Pos[]; strength: Strength; family: Mention['family']; kw: string; documented: boolean };
  const mentions: Mention[] = [];
  let subjectSeen = false;
  for (const cl of clauses) {
    const atoms = cl.map((t, i) => t.t === 'atom' ? i : -1).filter(i => i >= 0);
    if (!atoms.length) continue;
    const asg = new Map<number, Asg>();
    const put = (i: number, a: Asg, mode: 'max' | 'override' | 'union') => {
      const cur = asg.get(i);
      if (!cur || a.strength > cur.strength || (mode === 'override' && a.strength >= cur.strength)) asg.set(i, a);
      else if (mode === 'union' && a.strength === cur.strength) asg.set(i, { ...cur, pos: [...new Set([...cur.pos, ...a.pos])], kw: `${cur.kw} hoặc ${a.kw}`, family: cur.family === 'plain' ? a.family : cur.family });
    };
    const segOf = (i: number) => cl.slice(0, i).filter(t => t.t === 'comma').length;
    const segHasKw = (s: number) => cl.some((t, i) => t.t === 'kw' && t.kw.family !== 'loc' && segOf(i) === s);
    const govern = new Map<number, number[]>(); // kw index → atom indexes it assigned
    for (let i = 0; i < cl.length; i++) {
      const t = cl[i];
      if (t.t !== 'kw') continue;
      const note = notes[t.kw.text.toLowerCase()];
      const base: Asg = { pos: note ?? t.kw.pos, strength: note ? 3 : t.kw.strength, family: t.kw.family, kw: t.kw.text, documented: !!note };
      // pre (governs the atoms after it) or post (governs the atoms before it)?
      // pre (an atom follows, past filler words), post (nothing, a place or a comma follows), or a non-star object ("gặp Triệt"): governs nothing
      let j = i + 1; while (j < cl.length && (cl[j].t === 'pass' || (cl[j].t === 'word' && FILLER.has((cl[j] as any).text.toLowerCase())))) j++;
      const pre = j < cl.length && cl[j].t === 'atom';
      if (!pre && t.kw.strength === 2 && t.kw.family !== 'loc' && j < cl.length && cl[j].t === 'word') { govern.set(i, []); continue; }
      const got: number[] = [];
      if (pre) {
        for (let k = j; k < cl.length; k++) {
          const u = cl[k];
          if (u.t === 'kw' && u.kw.family !== 'loc') break;
          if (u.t === 'comma' && segHasKw(segOf(k) + 1)) break; // the next segment has its own position word
          if (u.t === 'atom') { put(k, base, 'max'); got.push(k); }
        }
      } else {
        let a = base;
        if (t.kw.family === 'loc') {
          // "X ở Ngọ", "Lộc Tồn ở Thiên Di": the place fixes the seat; without a place it is weak
          const pl = j < cl.length && cl[j].t === 'place' ? placePos((cl[j] as any).text, ctx) : null;
          a = pl ? { ...base, pos: pl.pos, strength: pl.explicit ? 3 : 2, kw: `${t.kw.text} ${(cl[j] as any).text}` } : { ...base, strength: 2 };
        }
        // "KW1 <place> hoặc KW2": KW2 is an alternative seat for what KW1 governed
        let q = i - 1; while (q >= 0 && (cl[q].t === 'place' || cl[q].t === 'word')) q--;
        const alt = q >= 0 && cl[q].t === 'or' && (() => { let r = q - 1; while (r >= 0 && (cl[r].t === 'place' || cl[r].t === 'word')) r--; return r >= 0 && cl[r].t === 'kw' ? r : -1; })();
        if (typeof alt === 'number' && alt >= 0 && govern.get(alt)?.length) {
          for (const k of govern.get(alt)!) { put(k, a, 'union'); got.push(k); }
        } else {
          const run: Array<{ k: number; crossed: boolean }> = [];
          let crossed = false;
          for (let k = i - 1; k >= 0; k--) {
            const u = cl[k];
            if (u.t === 'kw' || u.t === 'pass') break; // "X được/bị Y chiếu": the word governs Y, not X
            if (u.t === 'comma') { if (cl[k - 1]?.t !== 'atom') break; crossed = true; continue; } // only a list of stars runs on past a comma
            if (u.t === 'atom') run.push({ k, crossed });
          }
          // "Lộc Mã xung chiếu" with no object: the two may face each other (one in the palace) rather than both face it
          const startsClause = run.length > 0 && !cl.slice(0, Math.min(...run.map(r => r.k))).some(x => x.t === 'kw' || x.t === 'atom');
          if (run.length >= 2 && startsClause && a.pos.length === 1 && a.pos[0] === 'opp' && !(j < cl.length && cl[j].t === 'place'))
            a = { ...a, pos: ['self', 'opp'], family: 'sym', kw: `${a.kw} (lẫn nhau?)` };
          // past a comma the word only replaces a weaker reading ("có Không, Kiếp giáp": yes; "đồng cung Lộc Tồn, Tả Hữu hội chiếu": no)
          for (const { k, crossed: c } of run) { if (t.kw.family === 'loc' && asg.has(k)) continue; put(k, a, c ? 'max' : 'override'); got.push(k); }
        }
      }
      govern.set(i, got);
    }
    const sym = cl.some(t => t.t === 'sym');
    // an atom no word governs: the subject (own palace, implied) if it opens the first clause that states a relation; otherwise unstated
    const firstKw = cl.findIndex(t => t.t === 'kw');
    const subject = !subjectSeen && firstKw >= 0;
    subjectSeen = true;
    const ms: Mention[] = atoms.flatMap(i => {
      const a = cl[i] as Extract<Tok, { t: 'atom' }>, g = asg.get(i), group = GROUPS.some(([s]) => s === a.text.toLowerCase());
      if (g) return [{ names: a.names, text: a.text, pos: g.pos, strength: g.strength, family: g.family, kw: g.kw, neg: a.neg, documented: g.documented, group }];
      if (subject && i < firstKw) return [{ names: a.names, text: a.text, pos: ['self'] as Pos[], strength: 1 as Strength, family: 'implied' as const, kw: '(chủ thể)', neg: a.neg, group }];
      return [];
    });
    if (sym && ms.length) { // "chiếu nhau", "tương hội", "hoặc ngược lại": the relation is between the stars, one of them may be the palace's own
      const all = [...new Set<Pos>(['self', ...ms.flatMap(m => m.pos)])];
      for (const m of ms) { m.pos = all; m.family = 'sym'; m.kw += ' (đối xứng)'; }
    }
    mentions.push(...ms);
  }
  return { mentions, bindings, notes };
}

// ---- comparison ----
export type FlagKind = 'wider' | 'narrower' | 'mismatch' | 'mixed' | 'hoa_unbound' | 'dead';
export interface Flag { kind: FlagKind; certain: boolean; atom?: string; book?: string; cond?: string; note?: string }
/** from: 'condition' = the seat the rule's condition already guarantees (holds whenever the rule fires; recorded so prose knows the seat);
 *  'book' = tightened to the book's wording by a certain flag; 'book?' = tightened by a needs-reading flag (applied only in strict mode). */
export interface Require { atom: string; relation: 'self' | 'opp' | 'trine' | 'tam_phuong' | 'flank' | 'nhi_hop' | Pos[]; of: string;
  carrier?: string; carrierCandidates?: string[]; from: 'condition' | 'book' | 'book?' }
export interface Guard { ruleId: string; requires: Require[]; reason: string; cite: string; review: 'draft'; certainty: 'certain' | 'needs-reading'; kinds: FlagKind[] }

const set = (xs: Pos[]) => [...new Set(xs)].sort();
const sub = (a: Pos[], b: Pos[]) => a.every(x => b.includes(x));
const posLabel = (p: Pos[]) => { const s = set(p).join('+'); return ({ self: 'self', opp: 'opp', trine: 'trine', 'opp+self+trine': 'tam_phuong', flank: 'flank', nhi_hop: 'nhi_hop' } as Record<string, string>)[s] ?? s; };
function relationOf(p: Pos[]): Require['relation'] {
  const s = set(p).join('+');
  if (s === 'self' || s === 'opp' || s === 'trine' || s === 'flank' || s === 'nhi_hop') return s;
  if (s === 'opp+self+trine') return 'tam_phuong';
  return set(p);
}

function carriersByHoa(): Record<string, Set<string>> {
  const tv = JSON.parse(readFileSync(join(DATA, 'tu_hoa_vi.json'), 'utf8'));
  const out: Record<string, Set<string>> = Object.fromEntries(HOA.map(h => [h, new Set<string>()]));
  for (const list of Object.values(tv.by_stem) as Array<Array<{ star: string }>>) list.forEach((x, i) => out[HOA[i]].add(x.star));
  return out;
}

export interface Audited { id: string; pack: string; cite: string; description: string; of: string; flags: Flag[]; guard: Guard | null; bookScope: string; condScope: string; positional: boolean }

export function auditRule(r: any, pack: string, fullNames: string[], carriers: Record<string, Set<string>>): Audited {
  const scan = scanConditions(r.conditions);
  const desc: string = r.description ?? '';
  const cite = (/\[([^\]]+)\]\s*$/.exec(desc) ?? [, ''])[1]!;
  const { mentions, bindings } = parseDescription(desc, fullNames, { of: scan.of, branches: scan.branches });
  const pos = scan.leaves.filter(l => !l.neg);
  // condition positions per atom (union over the leaves that test it; for a vô chính diệu palace a chính tinh cannot be in it)
  const cond = new Map<string, { pos: Pos[]; scopes: Set<Scope>; kind: 'star' | 'hoa'; group?: string }>();
  for (const l of pos) {
    const c = cond.get(l.name) ?? { pos: [], scopes: new Set<Scope>(), kind: l.kind, group: l.group };
    let p = SCOPE_POS[l.scope];
    if (scan.vcd && MAJORS.includes(l.name) && l.scope !== 'self') p = p.filter(x => x !== 'self');
    c.pos = set([...c.pos, ...p]); c.scopes.add(l.scope); cond.set(l.name, c);
  }
  // "… nhưng không đóng ở Mệnh": an absence in the own palace removes that seat from a tam-phương test
  for (const l of scan.leaves) if (l.neg && l.scope === 'self' && !l.group) { const c = cond.get(l.name); if (c && c.pos.length > 1) c.pos = c.pos.filter(x => x !== 'self'); }
  const flags: Flag[] = [];
  const book = new Map<string, Mention>();
  for (const [name, c] of cond) {
    const named = mentions.filter(m => !m.neg && m.names.includes(name));
    // a star named by itself speaks over a group word ("Không hoặc Kiếp …, hội sát tinh khác")
    const ms = named.some(m => !m.group) ? named.filter(m => !m.group) : named;
    if (!ms.length) continue;
    // several mentions: the strongest position word speaks; equal strength → union
    const top = Math.max(...ms.map(m => m.strength)) as Strength, best = ms.filter(m => m.strength === top);
    const fam = (['sym', 'chieu', 'gap', 'implied'] as const).find(f => best.some(x => x.family === f)) ?? best[0].family;
    const m: Mention = { ...best[0], family: fam, pos: set(best.flatMap(x => x.pos)), kw: [...new Set(best.map(x => x.kw))].join(' / '), documented: best.some(x => x.documented) };
    book.set(name, m);
    const S = m.pos, C = c.pos;
    const wider = !sub(C, S), narrower = !sub(S, C);
    if (!wider && !narrower) continue;
    if (m.family === 'sym') { // a mutual phrase states the relation between the stars, not each star's seat: only a seat outside all of them is flagged
      if (wider) flags.push({ kind: 'wider', certain: false, atom: name, book: `'${m.kw}' (${posLabel(S)})`, cond: [...c.scopes].map(s => SCOPE_LABEL[s]).join('|') });
      continue;
    }
    if (m.family === 'gap' && !m.documented && !wider) {
      // 'gặp' is read as hội by the system; the condition testing only the own palace narrows it
      if (C.length === 1 && C[0] === 'self') flags.push({ kind: 'narrower', certain: false, atom: name, book: `'${m.kw}' (${posLabel(S)}, mơ hồ)`, cond: [...c.scopes].map(s => SCOPE_LABEL[s]).join('|') });
      continue;
    }
    const certain = m.strength === 3 && m.family !== 'chieu';
    const kind: FlagKind = wider && narrower ? 'mismatch' : wider ? 'wider' : 'narrower';
    flags.push({ kind, certain, atom: name, book: `'${m.kw}' (${posLabel(S)})`, cond: [...c.scopes].map(s => SCOPE_LABEL[s]).join('|') });
  }
  // mixed scopes among the positive atoms
  const scopes = new Set([...cond.values()].flatMap(c => [...c.scopes]));
  if (scopes.size >= 2) flags.push({ kind: 'mixed', certain: true, note: [...scopes].map(s => SCOPE_LABEL[s]).join(' + ') });
  // Hóa tested by name without its carrying star
  const carrierOf = new Map<string, { star: string; certain: boolean }>();
  if (!scan.yearStem) {
    for (const [h, c] of cond) {
      if (c.kind !== 'hoa') continue;
      const b = bindings.find(x => x.hoa === h && cond.has(x.star));
      if (b) { carrierOf.set(h, { star: b.star, certain: true }); flags.push({ kind: 'hoa_unbound', certain: true, atom: h, book: `${b.star} hóa ${h.slice(4)}`, cond: `${[...c.scopes].map(s => SCOPE_LABEL[s]).join('|')} lists ${h}, carrier untested` }); continue; }
      // only the own palace: there a co-tested star reads as the carrier ("Cự Môn … Hóa Kỵ" → "Cự Môn hóa Kỵ") though another star may carry it
      const co = c.scopes.has('self') ? [...cond.entries()].filter(([s, sc]) => sc.kind === 'star' && carriers[h]?.has(s) && sc.scopes.has('self')) : [];
      if (co.length) carrierOf.set(h, { star: co.map(([s]) => s).join('|'), certain: false });
      if (co.length) flags.push({ kind: 'hoa_unbound', certain: false, atom: h, book: `${h} beside ${co.map(([s]) => s).join(', ')}`, cond: `${[...c.scopes].map(s => SCOPE_LABEL[s]).join('|')} lists ${h}; a co-tested star could carry it` });
    }
  }
  for (const d of scan.dead) flags.push({ kind: 'dead', certain: true, cond: d, note: 'Hóa names never appear in star lists' });

  const bookScope = [...book.entries()].map(([n, m]) => `${n}: '${m.kw}' → ${posLabel(m.pos)}${m.documented ? ' (ghi chú hệ thống)' : ''}`).join('; ');
  const condScope = [...cond.entries()].map(([n, c]) => `${n}: ${[...c.scopes].map(s => SCOPE_LABEL[s]).join('|')}`).join('; ') + (scan.refs.length ? `; ${[...new Set(scan.refs)].join(', ')}` : '');
  let guard: Guard | null = null;
  if (flags.length) {
    const flagged = new Map(flags.filter(f => f.atom && f.kind !== 'hoa_unbound').map(f => [f.atom!, f]));
    const requires: Require[] = [];
    for (const [n, c] of cond) {
      const f = flagged.get(n), m = book.get(n);
      // a flagged wider/mismatch atom takes the book's seat (∩ what the condition can see); everything else keeps the condition's seat
      let p = c.pos, from: Require['from'] = 'condition';
      if (f && (f.kind === 'wider' || f.kind === 'mismatch') && m) { const inter = c.pos.filter(x => m.pos.includes(x)); p = inter.length ? inter : m.pos; from = f.certain ? 'book' : 'book?'; }
      const req: Require = { atom: n, relation: relationOf(p), of: scan.of, from };
      const car = carrierOf.get(n);
      if (car?.certain) { req.carrier = car.star; req.from = 'book'; }
      else if (car) { req.carrierCandidates = car.star.split('|'); if (req.from === 'condition') req.from = 'book?'; }
      requires.push(req);
    }
    const reason = flags.map(f => f.kind === 'mixed' ? `mixed scopes (${f.note})` : f.kind === 'dead' ? `dead condition: ${f.cond}` : `${f.kind} ${f.atom}: book ${f.book}, condition ${f.cond}`).join('; ');
    const certain = flags.filter(f => f.kind !== 'mixed').every(f => f.certain);
    guard = { ruleId: r.id, requires, reason, cite, review: 'draft', certainty: certain ? 'certain' : 'needs-reading', kinds: [...new Set(flags.map(f => f.kind))] };
  }
  return { id: r.id, pack, cite, description: desc, of: scan.of, flags, guard, bookScope, condScope, positional: cond.size > 0 };
}

export function loadTuViRules(): Array<{ rule: any; pack: string }> {
  const out: Array<{ rule: any; pack: string }> = [];
  for (const f of readdirSync(DATA).filter(f => /^pack_.*\.json$/.test(f)).sort()) {
    const d = JSON.parse(readFileSync(join(DATA, f), 'utf8'));
    for (const r of d.rules ?? []) if (r.system === 'tu_vi') out.push({ rule: r, pack: f });
  }
  return out;
}

function main() {
  const rules = loadTuViRules();
  const names = new Set<string>([...MAJORS, ...HOA, ...SAT, ...CAT]);
  for (const { rule } of rules) for (const l of scanConditions(rule.conditions).leaves) names.add(l.name);
  const fullNames = [...names].filter(n => n.includes(' '));
  const carriers = carriersByHoa();
  const res = rules.map(({ rule, pack }) => auditRule(rule, pack, fullNames, carriers));
  const flagged = res.filter(r => r.flags.length);
  const guards = flagged.map(r => r.guard!).filter(Boolean);

  const kinds: FlagKind[] = ['wider', 'narrower', 'mismatch', 'hoa_unbound', 'dead', 'mixed'];
  const count = (k: FlagKind, c?: boolean) => flagged.filter(r => r.flags.some(f => f.kind === k && (c === undefined || f.certain === c))).length;
  const esc = (s: string) => s.replace(/\|/g, '\\|');
  const md: string[] = [];
  md.push('# Position audit of the Tử Vi rule packs', '',
    'Generated by `node tools/interpret/audit_positions.ts` (plan quirky-tinkering-rabin R1). Compares what each rule\'s description says about where a star or Hóa',
    'stands with the fact scope its `conditions` test. Packs are not edited; the draft guards are in `engine/data/kg/position_guards.json` and are applied by',
    '`src/interpret/reason/positions.ts` (`guardHolds`).', '',
    '## Method', '',
    '- **Condition scope** per atom: `palace.own_stars` / `own_major_stars` / `palace.tu_hoa` / `rel.self_*` = own palace; `rel.opp_*` = xung chiếu; `rel.trine*_*` = tam hợp;',
    '  `palace.tam_phuong_*` / `rel.tp_*` / `khi.*_tp` = tam phương (own palace + xung + tam hợp, cannot tell which); `rel.flank_*` / `neighbor_*` = giáp; `rel.nhi_hop_*` = nhị hợp;',
    '  `ref:{palace}` = another named palace (listed, not compared). Absences (`not`, `khi.* ≤ 0`) are not compared.',
    '- **Book scope** per mention, from the paraphrase after the section colon (system notes after `;` are only used when they fix a reading, e.g. "\'gặp\' đọc là hội"):',
    '  `đồng cung` / `cùng cung` / `thủ` / `tọa` → own; `xung (chiếu)` → opp; `tam hợp (chiếu)` → trine; `hội` / `hội chiếu` / `tam phương` → tam phương; `chiếu` / `hợp chiếu` /',
    '  `củng chiếu` / `chầu` / `triều` → opp or trine (not own); `giáp` / `kẹp` → flank; `nhị hợp`; `ở/tại + chi or palace` → that seat relative to the rule\'s',
    '  palace (e.g. "Lộc Tồn ở Thiên Di" on Mệnh → opp). Weak words: `gặp` / `hợp (với)` / `tụ vào` (read as hội), `có`, `thêm`, `đi với`, `đi kèm`.',
    '  `X được/bị Y chiếu`: the word governs Y; a comma list ("đồng cung Tả Phụ, Hữu Bật") shares its word.',
    '  The stars opening the first clause that states a relation are its implied subject (own palace); other stars no word governs are unstated (not',
    '  compared). "chiếu nhau" / "tương hội" / "ngược lại" / a bare "X Y xung chiếu" state a relation between the stars: only a seat outside all of them is flagged.',
    '- **certain**: an explicit position word (or a system note) governs the mention and the condition contradicts it. **needs-reading**: weak or implied',
    '  wording, any `chiếu` without `xung` and any `tam hợp` (see the notes), or a Hóa merely co-tested in the own palace with a star',
    '  that could carry it. `mixed` is a structural fact (certain), not by itself a defect: it tells the prose layer that not every atom is "đồng cung".', '',
    '## Counts', '',
    `- Tử Vi rules scanned: **${res.length}**; with star/Hóa position conditions: **${res.filter(r => r.positional).length}**; flagged: **${flagged.length}**` +
    ` (of which ${flagged.filter(r => r.flags.some(f => f.kind !== 'mixed')).length} with a flag other than \`mixed\`).`, '',
    '| kind | rules | certain | needs-reading |', '|---|---:|---:|---:|',
    ...kinds.map(k => `| ${k} | ${count(k)} | ${count(k, true)} | ${count(k, false)} |`), '',
    'A rule can carry several kinds; each row counts rules with at least one flag of that kind.', '');
  const byPack = new Map<string, number>();
  for (const r of flagged.filter(r => r.flags.some(f => f.kind !== 'mixed'))) byPack.set(r.pack, (byPack.get(r.pack) ?? 0) + 1);
  md.push('Rules with a non-`mixed` flag, by pack: ' + [...byPack.entries()].map(([p, n]) => `\`${p}\` ${n}`).join(', ') + '.', '');
  const row = (r: Audited, fl: Flag[]) => `| \`${r.id}\` | ${esc(r.cite)} | ${fl.map(f => `${f.kind}${f.certain ? '' : '?'}`).join(', ')} | ${esc(fl.filter(f => f.book).map(f => `${f.atom}: ${f.book}`).join('; ') || r.bookScope)} | ${esc(fl.filter(f => f.cond).map(f => `${f.atom ? f.atom + ': ' : ''}${f.cond}`).join('; ') || r.condScope)} |`;
  const main = flagged.filter(r => r.flags.some(f => f.kind !== 'mixed'));
  const sortK = (a: Audited, b: Audited) => Number(b.guard?.certainty === 'certain') - Number(a.guard?.certainty === 'certain') || (a.of === 'Mệnh' ? 0 : 1) - (b.of === 'Mệnh' ? 0 : 1) || a.id.localeCompare(b.id);
  md.push('## Flagged rules (wider / narrower / mismatch / hoa_unbound / dead)', '',
    '`?` = needs-reading. Certain rules first, Mệnh rules first within each group.', '',
    '| rule | cite | flags | description scope | condition scope |', '|---|---|---|---|---|',
    ...main.sort(sortK).map(r => row(r, r.flags.filter(f => f.kind !== 'mixed'))), '');
  const mixedOnly = flagged.filter(r => r.flags.every(f => f.kind === 'mixed'));
  md.push(`## Mixed-scope rules with no other flag (${mixedOnly.length})`, '',
    'The condition matches the book, but the atoms sit in different scopes; the guard records each atom\'s seat so prose cannot voice a tam-phương atom as "đồng cung".', '',
    '| rule | cite | scopes | description scope | condition scope |', '|---|---|---|---|---|',
    ...mixedOnly.sort(sortK).map(r => `| \`${r.id}\` | ${esc(r.cite)} | ${esc(r.flags[0].note ?? '')} | ${esc(r.bookScope || '—')} | ${esc(r.condScope)} |`), '');
  // effect on the 1,000-chart corpus: how often each guarded rule fires and how often its guard blocks the firing
  const corpus = JSON.parse(gunzipSync(readFileSync(join(ROOT, 'src', 'interpret', 'test', 'fixtures', 'corpus1000.json.gz'))).toString('utf8')) as Array<{ facts: any }>;
  const byId = new Map(rules.map(x => [x.rule.id, x.rule]));
  const eff = new Map<string, [number, number, number]>();
  for (const { facts } of corpus) {
    const b = facts.base, w = (n: string) => b[`palace:${n}`] ?? null;
    for (const g of guards) {
      if (g.kinds.every(k => k === 'mixed')) continue;
      const r = byId.get(g.ruleId);
      for (const p of facts.palaces) {
        const f = { ...b.chart, ...b[`palace:${p.name}`] };
        if (evaluate(r.conditions, f, w) !== true) continue;
        const atoms = triggerAtoms(r.conditions, f, w, p.name), o = { here: p.name, tuHoa: facts.tu_hoa };
        const e = eff.get(g.ruleId) ?? [0, 0, 0];
        e[0]++; if (!guardHolds(g, atoms, facts.palaces, o)) e[1]++; if (!guardHolds(g, atoms, facts.palaces, { ...o, strict: true })) e[2]++;
        eff.set(g.ruleId, e);
      }
    }
  }
  const tot = [...eff.values()].reduce((a, x) => [a[0] + x[0], a[1] + x[1], a[2] + x[2]], [0, 0, 0]);
  md.push('## Effect on the 1,000-chart corpus', '',
    `Guarded rules (other than mixed-only) fired **${tot[0]}** times over the corpus (all palaces). The default guards (\`condition\` + \`book\` requirements) block **${tot[1]}**`,
    `of them; strict mode (also \`book?\`) blocks ${tot[2]}. Rules whose default guard blocks at least one firing:`, '',
    '| rule | fired | blocked | blocked (strict) |', '|---|---:|---:|---:|',
    ...[...eff.entries()].filter(([, x]) => x[1]).sort((a, b) => b[1][1] - a[1][1]).map(([k, x]) => `| \`${k}\` | ${x[0]} | ${x[1]} | ${x[2]} |`), '',
    '## Reviewer notes (hand-checked while building the audit)', '',
    '- `TV_KL_STAR_MENH_KHOA_LOC_GIAP` (KL p.66, Khoa Lộc giáp Mệnh) tests `rel.flank_*_stars contains Hóa …`; star lists never hold Hóa names (0 of 12,000 palace',
    '  fact sets in the corpus), so the rule never fires. The description already says the facts lack Tứ Hóa ở giáp; it needs `rel.flank_*_hoa` facts.',
    '- `TV_TH_MV_MENH_PHU_TUAT_HOA_CUC` (TH p.88): the "hợp cát tinh" list is `rel.tp_stars` ANY of Tử Vi, **Thiên Phủ**, Khôi, Việt, Tả, Hữu while',
    '  Thiên Phủ is required in the own palace, so the cát-tinh clause is always true (tp includes the own palace). Flagged as wider on Thiên Phủ.',
    '- `TV_TH_VERSE_MENH_CU_HOA_KY` (TH p.83, "Cự Môn hóa Kỵ"): Hóa Kỵ in Mệnh beside Cự Môn is carried by another star in half the corpus firings',
    '  (Cự Cơ, Cự Nhật, Xương/Khúc). Same for `TV_KL_CASE_MENH_AM_HAM_QUYEN` (Thái Âm hãm hóa Quyền) and `TV_TH_MV_MENH_CU_THIN_TUAT_LOC` (never blocked:',
    '  at Thìn/Tuất Cự Môn has no chính-tinh partner, so a Hóa Lộc there is its own or a phụ tinh\'s).',
    '- `TV_TH_AUX_MENH_DH_CHIEU` and `TV_TT_MENH_TA_HUU_TAI_QUAN` are the largest: the book names one seat (xung chiếu; Tài/Quan), the condition takes the whole',
    '  tam phương minus Mệnh. `TV_TH_AUX_MENH_LOC_PHA` ("Phá Quân chính chiếu") also fires with Phá Quân in Mệnh itself.',
    '- "tam hợp" is not used strictly: `TV_KL_STAR_MENH_NHAT_TAM_MINH` (KL p.83, "tam hợp Đào, Hồng, Hỷ") cannot hold literally because Hồng Loan and',
    '  Thiên Hỷ always stand opposite each other; every corpus firing has one of them in Mệnh or Thiên Di. All "tam hợp" readings are therefore needs-reading.',
    '- `narrower` rules (book "hội", condition own palace: `TV_TT_MENH_LUONG_MA`, `TV_TT_MENH_TU_VI_XUONG_KHUC`, `TV_TH_CACH_MENH_BT_KK_SAT` …) are safe for',
    '  prose (the atom really is in the palace) but miss charts the book covers; a guard cannot widen a rule, so these need a pack change upstream.',
    '- `TV_TH_AUX_MENH_LOC_HOA_LOC` ("Lộc Tồn gặp Hóa Lộc", TH p.51) is narrower? (the condition wants Hóa Lộc in Mệnh, "gặp" is read as hội elsewhere in TH).',
    '  `TV_KL_STAR_MENH_TAM_KY_KY_KINH` is consistent with its book line (Khoa Quyền Lộc hội, Kỵ/Kình đồng cung): mixed only.',
    '- Needs-reading flags come from wording the parser cannot settle (\'gặp\', \'có\', a bare \'chiếu\', an implied subject, "chiếu nhau"/"ngược lại");',
    '  their tightenings are `book?` and are not applied unless strict.', '');
  mkdirSync(join(ROOT, 'docs', 'audit'), { recursive: true });
  writeFileSync(join(ROOT, 'docs', 'audit', 'POSITION-AUDIT.md'), md.join('\n'));
  const head = {
    generated: 'node tools/interpret/audit_positions.ts', plan: 'quirky-tinkering-rabin R1', report: 'docs/audit/POSITION-AUDIT.md',
    note: 'Draft guards over the Tử Vi packs (not edited). An assertion of ruleId may be used only if each listed atom present in its trigger atoms stands in `relation` to palace `of` (\'@palace\' = the palace the rule fired on) and, when `carrier` is set, the Hóa rides that star (`carrierCandidates`: one of them). relation: self|opp|trine|tam_phuong|flank|nhi_hop or a list (any of). from: condition (already guaranteed by the rule), book (certain tightening), book? (needs reading; strict mode only). Applied by src/interpret/reason/positions.ts guardHolds.',
  };
  writeFileSync(join(DATA, 'kg', 'position_guards.json'),
    JSON.stringify(head, null, 1).replace(/\n}$/, ',\n "guards": [\n') + guards.map(g => '  ' + JSON.stringify(g)).join(',\n') + '\n ]\n}\n');
  const summary = Object.fromEntries(kinds.map(k => [k, { rules: count(k), certain: count(k, true), needsReading: count(k, false) }]));
  console.log(JSON.stringify({ scanned: res.length, flagged: flagged.length, nonMixed: main.length, guards: guards.length, summary }, null, 1));
}

if (import.meta.url === `file://${process.argv[1]}`) main();
