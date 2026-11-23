// Star dignity (Miếu / Vượng / Đắc / Lợi / Bình / Hãm) for the TS side. It reads the SAME knowledge base as the Python engine
// (engine/data/dignity_kb.json, built by tools/build_dignity_kb.py) and only looks results up: there is no second calculation
// pipeline, so the chart badges (Python), the rule facts (Python) and the knowledge graph / planner here cannot disagree.
// Only VERIFIED carries a level. CONFLICT, UNVERIFIED and NOT_APPLICABLE never become a level, a badge or a confident sentence.
import kbJson from '../../engine/data/dignity_kb.json' with { type: 'json' };

export type DignityLevel = 'miếu' | 'vượng' | 'đắc' | 'lợi' | 'bình' | 'hãm';
export type School = 'thuc_hanh' | 'toan_thu' | 'khao_luan';
export interface Variant { school: School; value: DignityLevel; term: string; locator: string; reported?: string }
export type DignityResult =
  | { status: 'VERIFIED'; value: DignityLevel; term: string; school: School; locator: string; legacy?: boolean; variants?: Variant[] }
  | { status: 'CONFLICT'; school: School; alternatives: Array<{ value: DignityLevel | null; term: string; locator: string }>; variants?: Variant[] }
  | { status: 'UNVERIFIED'; school?: School; reason?: string; variants?: Variant[] }
  | { status: 'NOT_APPLICABLE'; reason: string };

interface KB {
  version: string; levels: DignityLevel[]; branches: string[]; default_school: School;
  schools: Record<School, { book: string; source: string; title: string }>;
  stars: Record<string, { id: string; kind: 'chinh_tinh' | 'phu_tinh' | 'tu_hoa'; group: string }>;
  aliases: Record<string, string>; ambiguous: string[];
  resolved: Record<School, Record<string, Record<string, DignityResult>>>;
}
export const KB = kbJson as unknown as KB;
const BY_ID = new Map(Object.entries(KB.stars).map(([n, m]) => [m.id, n]));

/** Mark-stripped id, identical to tools/build_dignity_kb.py slug() (NFD, marks removed, đ->d, lower, spaces->_). */
export function starId(name: string): string {
  return name.replace(/Đ/g, 'D').replace(/đ/g, 'd').normalize('NFD').replace(/\p{Mn}/gu, '').toLowerCase().trim().replace(/ /g, '_');
}

/** Canonical star name for a name, id or alias; null when unknown or ambiguous (e.g. 'Quan Phu' without tone marks). */
export function normalizeStar(star: string): string | null {
  const nfc = star.trim().normalize('NFC');
  if (nfc in KB.stars) return nfc;
  const lower = nfc.toLocaleLowerCase('vi');
  for (const n of Object.keys(KB.stars)) if (n.toLocaleLowerCase('vi') === lower) return n;
  const key = BY_ID.has(nfc) ? nfc : starId(nfc);
  if (BY_ID.has(key)) return BY_ID.get(key)!;
  const id = KB.aliases[key];
  return id ? BY_ID.get(id) ?? null : null;
}

/** Classification of `star` in `branch` under `school` (default: the engine's default, Thực Hành). */
export function classify(star: string, branch: string, school: School = KB.default_school): DignityResult & { star?: string } {
  if (!(school in KB.resolved)) throw new Error(`unknown school ${school}`);
  if (!KB.branches.includes(branch)) throw new Error(`unknown branch ${branch}`);
  const name = normalizeStar(star);
  if (!name) return { status: 'UNVERIFIED', reason: `unknown star ${star}` };
  return { star: name, ...KB.resolved[school][name][branch] };
}

/** The level when VERIFIED, else null: the only form rules, sentences and badges may use. */
export function verifiedLevel(star: string, branch: string, school?: School): DignityLevel | null {
  const r = classify(star, branch, school);
  return r.status === 'VERIFIED' ? r.value : null;
}

/** 'Thực Hành tr.30' / 'Toàn Thư tr.37–38' / 'Khảo Luận tr.187' for a locator such as 'TH p.30', 'TT pp.37-38'. */
export function citeVi(locator: string): string {
  const m = locator.match(/^(TH|TT|KL) pp?\.(\d+(?:-\d+)?)/);
  if (!m) return '';
  return `${{ TH: 'Thực Hành', TT: 'Toàn Thư', KL: 'Khảo Luận' }[m[1] as 'TH' | 'TT' | 'KL']} tr.${m[2].replace(/-/g, '–')}`;
}

const BRIGHT_CLASS = new Set<DignityLevel>(['miếu', 'vượng', 'đắc']);
const ORDER: DignityLevel[] = ['miếu', 'vượng', 'đắc', 'lợi', 'bình', 'hãm'];
type DigCell = { status: string; value?: string; alternatives?: Array<{ value: string | null }>; variants?: Array<{ value: string }> };

/** The level a chính tinh may be read at when its cell has no single checked level but every book that gives one agrees on the class
 *  (audit 2026-11-22, C5): Tham Lang at Tuất is CONFLICT in Khảo Luận (vượng p.189, miếu p.101) and miếu in Thực Hành and Toàn Thư, yet
 *  the prose said "không có chính tinh sáng". A CONFLICT cell whose alternatives (and the other schools' readings) are all bright reads
 *  at the weakest of them; an UNVERIFIED cell does the same when at least two other schools give it and all agree. Any value outside
 *  the class (a hãm beside a vượng), or a single reading, keeps it unknown: school disagreement is never decided here. */
export function agreedLevel(cell: DigCell | undefined): DignityLevel | null {
  if (!cell || (cell.status !== 'CONFLICT' && cell.status !== 'UNVERIFIED')) return null;
  const alts = (cell.alternatives ?? []).map(a => a.value), vars = (cell.variants ?? []).map(v => v.value);
  if (alts.some(v => v == null)) return null;
  const vals = [...alts, ...vars] as DignityLevel[];
  if (cell.status === 'UNVERIFIED' ? vars.length < 2 : !alts.length) return null;
  const cls = (v: DignityLevel) => BRIGHT_CLASS.has(v) ? 'bright' : v === 'hãm' ? 'ham' : 'mid';
  if (!vals.length || vals.some(v => !ORDER.includes(v)) || new Set(vals.map(cls)).size !== 1 || cls(vals[0]) === 'mid') return null;
  return vals.reduce((a, b) => ORDER.indexOf(b) > ORDER.indexOf(a) ? b : a);
}

/** The chart with each chính tinh's agreed level filled in where `major_dignity` has none (see agreedLevel), marked in
 *  `dignity_agreed` so a sentence can tell a page-checked level from an agreed one. Applied once where the facts enter (route.ts). */
export function withAgreedDignity<T extends { palaces: Array<{ major_stars: string[]; major_dignity: Record<string, string | null>; dignity_status?: Record<string, unknown> }> }>(chart: T): T {
  return { ...chart, palaces: chart.palaces.map(p => {
    const add: Record<string, DignityLevel> = {};
    for (const s of p.major_stars) if (!p.major_dignity?.[s]) { const v = agreedLevel(p.dignity_status?.[s] as DigCell | undefined); if (v) add[s] = v; }
    return Object.keys(add).length ? { ...p, major_dignity: { ...p.major_dignity, ...add }, dignity_agreed: Object.fromEntries(Object.keys(add).map(s => [s, true])) } : p;
  }) };
}
