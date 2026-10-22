// Palace evidence (plan quirky-tinkering-rabin step 3, S1): every structural element of a palace, whether or not a rule fired on it, so that
// the reasoner cannot pass over a Hóa Kỵ, a sát tinh or a Tuần just because no verified rule happened to read it. Nothing here is a reading:
// each element is a chart fact (basis tinh_toan) with a role — support / limit / mixed / neutral — taken from the star's kind and its
// checked brightness. The role is a system convention (he_thong), the usual reading order of Tử Vi practice:
//   support  a chính tinh miếu / vượng / đắc, a cát tinh (Tả Hữu, Xương Khúc, Khôi Việt), Lộc Tồn, Hóa Lộc / Quyền / Khoa;
//   limit    Hóa Kỵ, a sát tinh (Kình Đà, Hỏa Linh, Không Kiếp) not checked đắc or better, a chính tinh hãm, Tuần or Triệt;
//   mixed    a helping star that carries Hóa Kỵ (never a plain positive), a good Hóa on a hãm star, a sát tinh checked đắc or better.
// A palace with no chính tinh (vô chính diệu) borrows the chính tinh of the opposite palace: they are listed as its majors, marked
// `borrowed` (KL and TH read a VCD palace through its xung chiếu; which stars are borrowed is computed, not a reading).
import type { ChartInput, Concept, Knowledge, Palace } from '../types.ts';
import type { Resolved } from '../kg/resolve.ts';
import { CAT, SAT } from '../kg/atoms.ts';
import { Geo } from './tiers.ts';
import { detectStructures } from './structures.ts';
import { evaluateFormations } from './structures.ts';

export type Role = 'support' | 'limit' | 'mixed' | 'neutral';
export type Where = 'self' | 'opp' | 'trine';
export type Group = 'major' | 'cat' | 'sat' | 'loc' | 'ma' | 'hao' | 'other';
export interface StarEl { star: string; palace: string; where: Where; dignity?: string; group: Group; borrowed: boolean; hoa: string[]; role: Role }
export interface HoaEl { hoa: string; star: string; palace: string; where: Where; starDignity?: string; role: Role }
/** An element standing in the palace itself that the reading must face (limit / mixed) or may lean on (support). */
export interface Element { id: string; kind: 'hoa_ky' | 'sat' | 'major_ham' | 'tuan' | 'triet' | 'ky_carrier' | 'major_bright' | 'cat' | 'loc' | 'hoa_good' | 'sat_bright';
  star?: string; hoa?: string; dignity?: string; borrowed?: boolean; role: Role }
export interface RuleEl { ruleId: string; concept: string; facet: string; pol: '+' | '-' | '~'; stance: Resolved['stance']; status: Resolved['status']; timing: boolean;
  stars: string[]; cites: string[] }
export interface PalaceEvidence {
  palace: string; branch: string; vcd: boolean; than: boolean; tuan: boolean; triet: boolean;
  /** the palace's chính tinh, or for a VCD palace those of the opposite palace (borrowed) */
  majors: StarEl[];
  /** chính tinh of the tam phương tứ chính (the opposite palace's only when not already borrowed) */
  tamPhuong: StarEl[];
  /** cát / sát tinh, Lộc Tồn, Thiên Mã and the two Hao in the palace and its tam phương */
  stars: StarEl[];
  /** the birth-year Tứ Hóa standing in the palace or its tam phương, bound to the star that carries it */
  hoa: HoaEl[];
  /** named pairs in the two neighbouring palaces (cung giáp) */
  giap: Array<{ pair: [string, string]; left: string; right: string }>;
  /** draft cách cục evaluated at the palace (never told: listed so a reader of the plan sees them) and special structures present here */
  formations: Array<{ id: string; name: string; state: string; verification: string }>;
  structures: Array<{ id: string; name: string; verification: string }>;
  /** fired verified readings of the palace (live, past the position guards), timing facets included */
  rules: RuleEl[];
  /** elements standing in the palace itself, by role */
  support: Element[]; limit: Element[]; mixed: Element[];
  basis: 'tinh_toan';
}

const GOOD = new Set(['miếu', 'vượng', 'đắc']);
const GIAP: Array<[string, string]> = [['Tả Phụ', 'Hữu Bật'], ['Văn Xương', 'Văn Khúc'], ['Thiên Khôi', 'Thiên Việt'], ['Thái Dương', 'Thái Âm'], ['Tử Vi', 'Thiên Phủ'],
  ['Hóa Khoa', 'Hóa Lộc'], ['Hóa Quyền', 'Hóa Lộc'], ['Hóa Khoa', 'Hóa Quyền'], ['Kình Dương', 'Đà La'], ['Địa Không', 'Địa Kiếp'], ['Hỏa Tinh', 'Linh Tinh']];
export const TIMING_FACET = (facet: string) => facet.endsWith('.timing') || facet === 'life.mobility';
const groupOf = (s: string, majors: string[]): Group => majors.includes(s) ? 'major' : CAT.includes(s) ? 'cat' : SAT.includes(s) ? 'sat'
  : s === 'Lộc Tồn' ? 'loc' : s === 'Thiên Mã' ? 'ma' : s === 'Đại Hao' || s === 'Tiểu Hao' ? 'hao' : 'other';
const dignityIn = (p: Palace, s: string) => (p.major_dignity?.[s] ?? p.minor_dignity?.[s]) || undefined;

/** The palaces of a palace's tam phương tứ chính, with where each stands. */
export function tamPhuongOf(chart: ChartInput, P: string): Array<{ p: Palace; where: Where }> {
  const g = new Geo(chart, P);
  return chart.palaces.map(p => ({ p, d: (p.branch_index - g.menh.branch_index + 12) % 12 }))
    .filter(x => x.d === 0 || x.d === 4 || x.d === 6 || x.d === 8).map(x => ({ p: x.p, where: (x.d === 0 ? 'self' : x.d === 6 ? 'opp' : 'trine') as Where }));
}

export function hoaOfStar(chart: ChartInput, star: string, p: Palace): string[] {
  return Object.entries(chart.tu_hoa).filter(([, v]) => v.star === star && v.branch === p.branch_index).map(([h]) => h);
}

function roleOf(group: Group, dignity: string | undefined, hoa: string[]): Role {
  const ky = hoa.includes('Hóa Kỵ'), goodHoa = hoa.some(h => h !== 'Hóa Kỵ');
  if (group === 'sat') return dignity && GOOD.has(dignity) ? 'mixed' : 'limit';
  if (group === 'major') {
    if (dignity === 'hãm') return goodHoa ? 'mixed' : 'limit';
    if (ky) return 'mixed';
    return dignity && GOOD.has(dignity) ? 'support' : goodHoa ? 'support' : 'neutral';
  }
  if (group === 'cat' || group === 'loc') return ky ? 'mixed' : 'support';
  if (group === 'hao') return 'limit';
  return ky ? 'limit' : goodHoa ? 'support' : 'neutral';
}

export interface EvidenceInput { resolved?: Resolved[] }

/** The evidence of one palace. `resolved` (one report's resolution, after the position guards) supplies the fired verified readings. */
export function palaceEvidence(chart: ChartInput, k: Knowledge, P: string, inp: EvidenceInput = {}): PalaceEvidence {
  const g = new Geo(chart, P), pal = g.menh;
  const tp = tamPhuongOf(chart, P);
  const opp = tp.find(x => x.where === 'opp')!.p;
  const vcd = !pal.major_stars.length;
  const star = (s: string, p: Palace, where: Where, borrowed = false): StarEl => {
    const allMajors = p.major_stars, group = groupOf(s, allMajors), dignity = dignityIn(p, s), hoa = hoaOfStar(chart, s, p);
    return { star: s, palace: p.name, where, ...(dignity ? { dignity } : {}), group, borrowed, hoa, role: roleOf(group, dignity, hoa) };
  };
  const majors = vcd ? opp.major_stars.map(s => star(s, opp, 'opp', true)) : pal.major_stars.map(s => star(s, pal, 'self'));
  const tamPhuong = tp.filter(x => x.where !== 'self' && !(vcd && x.where === 'opp')).flatMap(x => x.p.major_stars.map(s => star(s, x.p, x.where)));
  const stars = tp.flatMap(x => x.p.stars.filter(s => !x.p.major_stars.includes(s)).map(s => star(s, x.p, x.where)).filter(e => e.group !== 'other'));
  const hoa: HoaEl[] = [];
  for (const [h, v] of Object.entries(chart.tu_hoa)) {
    const at = tp.find(x => x.p.branch_index === v.branch);
    if (!at) continue;
    const d = dignityIn(at.p, v.star);
    hoa.push({ hoa: h, star: v.star, palace: at.p.name, where: at.where, ...(d ? { starDignity: d } : {}), role: h === 'Hóa Kỵ' ? 'limit' : d === 'hãm' ? 'mixed' : 'support' });
  }
  const byIdx = new Map(chart.palaces.map(p => [p.branch_index, p]));
  const left = byIdx.get((pal.branch_index + 11) % 12)!, right = byIdx.get((pal.branch_index + 1) % 12)!;
  const has = (p: Palace, s: string) => s.startsWith('Hóa ') ? chart.tu_hoa[s]?.branch === p.branch_index : p.stars.includes(s) || p.major_stars.includes(s);
  const giap = GIAP.filter(([a, b]) => (has(left, a) && has(right, b)) || (has(left, b) && has(right, a))).map(pair => ({ pair, left: left.name, right: right.name }));
  const defs = k.kg?.formations ?? [];
  const formations = defs.length ? evaluateFormations(defs, chart.base).filter(f => f.anchor === P && f.state !== 'vang' as never).map(f => ({ id: f.id, name: f.name, state: f.state, verification: f.verification })) : [];
  const structures = detectStructures(chart.palaces, chart.tu_hoa).filter(s => s.present && s.palaces.includes(P)).map(s => ({ id: s.id, name: s.name, verification: s.verification }));
  // fired verified readings of this palace
  const cmap = new Map<string, Concept>(k.concepts.concepts.map(c => [c.id, c]));
  const rmap = new Map(k.rules.map(r => [r.id, r]));
  const rules: RuleEl[] = [];
  for (const r of inp.resolved ?? []) {
    if (r.subject !== `palace:${P}` && !(P === 'Mệnh' && r.subject === 'chart')) continue;
    if (r.status === 'voided' || r.status === 'divergent' || rmap.get(r.ruleId)?.reviewStatus !== 'verified') continue;
    const c = cmap.get(r.concept);
    rules.push({ ruleId: r.ruleId, concept: r.concept, facet: c?.facet ?? '', pol: (c?.pol ?? '~') as RuleEl['pol'], stance: r.stance, status: r.status,
      timing: TIMING_FACET(c?.facet ?? ''), stars: [...new Set(r.atoms.filter(a => a.kind === 'star' || a.kind === 'hoa').map(a => a.name))], cites: r.cites });
  }
  // the elements standing in the palace itself (for a VCD palace the borrowed chính tinh count as its own, marked borrowed)
  const support: Element[] = [], limit: Element[] = [], mixed: Element[] = [];
  const put = (e: Element) => (e.role === 'support' ? support : e.role === 'limit' ? limit : e.role === 'mixed' ? mixed : []).push(e);
  for (const m of majors) {
    if (m.role === 'limit') put({ id: `major_ham:${m.star}`, kind: 'major_ham', star: m.star, dignity: m.dignity, borrowed: m.borrowed, role: 'limit' });
    else if (m.role === 'support') put({ id: `major:${m.star}`, kind: 'major_bright', star: m.star, dignity: m.dignity, borrowed: m.borrowed, role: 'support' });
    else if (m.role === 'mixed') put({ id: `major:${m.star}`, kind: m.hoa.includes('Hóa Kỵ') ? 'ky_carrier' : 'major_ham', star: m.star, dignity: m.dignity, borrowed: m.borrowed, hoa: m.hoa[0], role: 'mixed' });
  }
  for (const s of stars.filter(x => x.where === 'self')) {
    if (s.group === 'sat') put({ id: `sat:${s.star}`, kind: s.role === 'mixed' ? 'sat_bright' : 'sat', star: s.star, dignity: s.dignity, role: s.role });
    else if (s.group === 'cat' || s.group === 'loc') put({ id: `${s.group}:${s.star}`, kind: s.hoa.includes('Hóa Kỵ') ? 'ky_carrier' : s.group, star: s.star, hoa: s.hoa[0], dignity: s.dignity, role: s.role });
  }
  for (const h of hoa.filter(x => x.where === 'self')) {
    if (h.hoa === 'Hóa Kỵ') put({ id: 'hoa:Hóa Kỵ', kind: 'hoa_ky', hoa: h.hoa, star: h.star, role: 'limit' });
    else put({ id: `hoa:${h.hoa}`, kind: 'hoa_good', hoa: h.hoa, star: h.star, dignity: h.starDignity, role: h.role });
  }
  if (pal.tuan) put({ id: 'tt:Tuần', kind: 'tuan', role: 'limit' });
  if (pal.triet) put({ id: 'tt:Triệt', kind: 'triet', role: 'limit' });
  return { palace: P, branch: pal.branch, vcd, than: !!pal.is_than, tuan: !!pal.tuan, triet: !!pal.triet, majors, tamPhuong, stars, hoa, giap, formations, structures,
    rules, support, limit, mixed, basis: 'tinh_toan' };
}

/** Does a reading stand on an element (its trigger atoms name the element's star, Hóa or Tuần/Triệt in the palace)? */
export function readsElement(r: Pick<Resolved, 'atoms'>, e: Element, palace: string): boolean {
  return r.atoms.some(a => {
    if (e.kind === 'tuan' || e.kind === 'triet') return a.kind === 'tuan_triet' && a.palace === palace && a.name === (e.kind === 'tuan' ? 'Tuần' : 'Triệt');
    if (e.kind === 'hoa_ky' || e.kind === 'hoa_good') return a.kind === 'hoa' && a.name === e.hoa && (a.palace === palace || a.palace === null);
    // a borrowed chính tinh is read where it stands (the opposite palace) as well as in the palace that borrows it
    return (a.kind === 'star' || a.kind === 'dignity') && a.name === e.star && (a.palace === palace || !!e.borrowed);
  });
}

/** Evidence as plain JSON for the API's plan view (already plain). */
export const evidenceView = (e: PalaceEvidence) => e;
