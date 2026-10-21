// Seats and tiers (plan quirky-tinkering-rabin R2b/R3). A SEAT is the structural element of the chart a reading stands on — the Mệnh chính tinh,
// a Hóa, a sát or cát tinh in Mệnh, Tuần/Triệt, the tam phương, or the chart's độ số — so that readings are weighed by what they rest on
// instead of all being equal. Each assertion's seat is its most fundamental trigger atom; the other atoms it needed are LINKS to other seats
// (the evidence that two elements interact, e.g. "Cự Môn hãm … nhưng hóa Lộc").
//
// The tier order is a system convention (basis he_thong), the usual reading order of Tử Vi practice, not a page of any book:
//   T1 chính tinh of Mệnh and its dignity (for Mệnh vô chính diệu: the chính tinh of the opposite palace, read as borrowed)
//   T2 a named cách cục the chart forms (a rule of kind 'formation' fired)
//   T3 the birth-year Tứ Hóa, bound to the star that carries it
//   T4 the six sát and six cát tinh, Lộc Tồn and Thiên Mã standing in Mệnh
//   T5 Tuần/Triệt on Mệnh, stars of the tam phương, độ số (season, hour, cục, can chi)
//   T6 any other minor star in Mệnh
// Rarity (how few corpus charts fire a rule, engine/data/kg/base_rates.json) is the second axis: a reading most charts get says little.
import type { ChartInput, Knowledge, Palace } from '../types.ts';
import type { Atom } from '../kg/atoms.ts';
import { CAT, SAT } from '../kg/atoms.ts';
import type { Resolved } from '../kg/resolve.ts';

export type Tier = 1 | 2 | 3 | 4 | 5 | 6;
export type Scope = 'self' | 'opp' | 'trine' | 'flank' | 'elsewhere' | 'chart';
export type SeatKind = 'major' | 'formation' | 'hoa' | 'star' | 'tuan_triet' | 'tam_phuong' | 'degree';
export const TIER_WEIGHT: Record<Tier, number> = { 1: 1, 2: 0.95, 3: 0.85, 4: 0.75, 5: 0.55, 6: 0.4 };
export const SCOPE_WEIGHT: Record<Scope, number> = { self: 1, opp: 0.85, trine: 0.7, flank: 0.6, elsewhere: 0.4, chart: 0.8 };
const STRONG_MINOR = new Set([...SAT, ...CAT, 'Lộc Tồn', 'Thiên Mã']);
export const TU_MO = new Set(['Thìn', 'Tuất', 'Sửu', 'Mùi']);

/** Positions relative to the Mệnh palace, from branch indices (Mệnh, opposite, the two tam hợp, the two neighbours). `centre` reads another
 *  palace the same way (its own chính tinh, opposite, tam hợp): the system indices (indices.ts) weigh a finding on its own palace with it. */
export class Geo {
  readonly menh: Palace; readonly byName: Map<string, Palace>; readonly majors: string[]; readonly vcd: boolean; readonly opp: Palace;
  readonly hoaCarrier: Record<string, { star: string; palace: string | undefined }>;
  constructor(chart: ChartInput, centre = 'Mệnh') {
    this.byName = new Map(chart.palaces.map(p => [p.name, p]));
    this.menh = this.byName.get(centre)!;
    const byIdx = new Map(chart.palaces.map(p => [p.branch_index, p]));
    this.opp = byIdx.get((this.menh.branch_index + 6) % 12)!;
    this.majors = this.menh.major_stars;
    this.vcd = !this.majors.length;
    this.hoaCarrier = Object.fromEntries(Object.entries(chart.tu_hoa).map(([h, v]) => [h, { star: v.star, palace: byIdx.get(v.branch)?.name }]));
  }
  scope(palace: string | null): Scope {
    if (!palace) return 'chart';
    const p = this.byName.get(palace);
    if (!p) return 'elsewhere';
    const d = (p.branch_index - this.menh.branch_index + 12) % 12;
    return d === 0 ? 'self' : d === 6 ? 'opp' : d === 4 || d === 8 ? 'trine' : d === 1 || d === 11 ? 'flank' : 'elsewhere';
  }
  dignity(star: string, palace: string): string | undefined {
    const p = this.byName.get(palace);
    return (p?.major_dignity?.[star] ?? p?.minor_dignity?.[star]) || undefined;
  }
}

export interface SeatRef { id: string; kind: SeatKind; tier: Tier; scope: Scope; star?: string; palace?: string | null; hoa?: string }

/** The seat of one assertion (its most fundamental atom) and the other seats its rule needed (links). */
export function seatOf(r: Pick<Resolved, 'atoms' | 'subject'>, g: Geo): { seat: SeatRef; links: SeatRef[] } {
  const refs = r.atoms.map(a => atomSeat(a, g)).filter((x): x is SeatRef => !!x);
  if (!refs.length) refs.push({ id: 'degree', kind: 'degree', tier: 5, scope: 'chart' });
  // độ số (chart-level facts, the branch of Mệnh) is the seat only when nothing else is: it qualifies a star reading, it does not own it
  const rank = (s: SeatRef) => (s.kind === 'degree' ? 100 : s.tier * 10) + (s.scope === 'self' ? 0 : s.scope === 'opp' ? 1 : s.scope === 'chart' ? 2 : 3);
  const sorted = [...new Map(refs.map(s => [s.id, s])).values()].sort((a, b) => rank(a) - rank(b) || (a.id < b.id ? -1 : 1));
  return { seat: sorted[0], links: sorted.slice(1) };
}

export function atomSeat(a: Atom, g: Geo): SeatRef | null {
  const scope = g.scope(a.palace);
  if (a.kind === 'star' || a.kind === 'dignity') {
    if (scope === 'self' && g.majors.includes(a.name)) return { id: `major:${a.name}`, kind: 'major', tier: 1, scope, star: a.name, palace: a.palace };
    if (g.vcd && scope === 'opp' && g.opp.major_stars.includes(a.name)) return { id: `major:${a.name}`, kind: 'major', tier: 1, scope, star: a.name, palace: a.palace };
    if (scope === 'self') return { id: `star:${a.name}`, kind: 'star', tier: STRONG_MINOR.has(a.name) ? 4 : 6, scope, star: a.name, palace: a.palace };
    if (scope === 'opp' || scope === 'trine') return { id: `tp:${a.palace}`, kind: 'tam_phuong', tier: 5, scope, palace: a.palace };
    return { id: `tp:${a.palace}`, kind: 'tam_phuong', tier: 6, scope, palace: a.palace };
  }
  if (a.kind === 'hoa') return { id: `hoa:${a.name}`, kind: 'hoa', tier: 3, scope, hoa: a.name, palace: a.palace, star: g.hoaCarrier[a.name]?.star };
  if (a.kind === 'tuan_triet') return scope === 'self' ? { id: `tt:${a.name}`, kind: 'tuan_triet', tier: 5, scope, palace: a.palace } : null;
  if (a.kind === 'vcd') return { id: 'major:vcd', kind: 'major', tier: 1, scope: 'self', palace: 'Mệnh' };
  if (a.kind === 'count') return null;
  return { id: 'degree', kind: 'degree', tier: 5, scope: 'chart' };
}

/** 0 … 1: how rare a rule's firing is on Mệnh across the corpus (rate 0.5 → 0.13, 0.1 → 0.43, 0.02 → 0.74, ≤ 0.005 → 1). */
export function rarity(k: Knowledge, ruleId: string): number {
  const rate = k.kg?.baseRates?.rule?.[ruleId] ?? 0.5;
  return Math.max(0, Math.min(1, Math.log2(1 / Math.max(rate, 0.005)) / Math.log2(200)));
}
/** How common a concept is at Mệnh across the corpus (0 … 1). */
export function conceptRate(k: Knowledge, concept: string): number {
  return k.kg?.baseRates?.concept?.[concept] ?? 0.5;
}
