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
