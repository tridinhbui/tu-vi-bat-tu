// Positional relations for the reasoner (plan quirky-tinkering-rabin R1, "không suy diễn sai"): where a trigger atom actually stands relative to
// a palace, which star carries each birth-year Hóa, and whether an assertion respects the position guard the audit wrote for its rule
// (engine/data/kg/position_guards.json, from tools/interpret/audit_positions.ts). The rule packs are not edited; a guard narrows a rule whose
// condition is wider than the book's wording (e.g. book "xung chiếu", condition tam phương) or binds a Hóa to the star the book names. Prose must
// not say "đồng cung / đi cùng" when relationOf says 'opp' or 'trine'. All functions are pure.
import type { ChartInput, Palace } from '../types.ts';
import type { Atom } from '../kg/atoms.ts';

export type Relation = 'self' | 'opp' | 'trine' | 'flank' | 'elsewhere';
export type GuardRelation = 'self' | 'opp' | 'trine' | 'tam_phuong' | 'flank' | 'nhi_hop';
export interface GuardRequire {
  atom: string; relation: GuardRelation | Array<'self' | 'opp' | 'trine' | 'flank' | 'nhi_hop'>; of: string;
  carrier?: string; carrierCandidates?: string[]; from?: 'condition' | 'book' | 'book?';
}
export interface PositionGuard { ruleId: string; requires: GuardRequire[]; reason: string; cite: string; review: string; certainty?: 'certain' | 'needs-reading'; kinds?: string[] }
type PalaceIdx = Pick<Palace, 'name' | 'branch_index'>;

/** Relation of the palace an atom stands in to a target palace, from branch indices: same palace, opposite (6 apart), tam hợp (4 or 8),
 *  giáp (adjacent) or elsewhere. null when either palace is not on the chart (an atom with no known palace cannot satisfy a guard). */
export function relationOf(atomPalace: string | null | undefined, targetPalace: string, palaces: PalaceIdx[]): Relation | null {
  const a = palaces.find(p => p.name === atomPalace), t = palaces.find(p => p.name === targetPalace);
  if (!a || !t) return null;
  const d = (((a.branch_index - t.branch_index) % 12) + 12) % 12;
  return d === 0 ? 'self' : d === 6 ? 'opp' : d === 4 || d === 8 ? 'trine' : d === 1 || d === 11 ? 'flank' : 'elsewhere';
}

/** Nhị hợp (lục hợp) pairs Tý–Sửu, Dần–Hợi, Mão–Tuất, Thìn–Dậu, Tỵ–Thân, Ngọ–Mùi: branch indices summing to 1 mod 12. */
export function isNhiHop(a: string | null | undefined, b: string, palaces: PalaceIdx[]): boolean {
  const x = palaces.find(p => p.name === a), y = palaces.find(p => p.name === b);
  return !!x && !!y && x !== y && (x.branch_index + y.branch_index) % 12 === 1;
}

/** The star carrying a birth-year Hóa and the palace it stands in, from the chart's tu_hoa table (facts list Hóa names per palace, not the
 *  carrier). null when the chart has no such Hóa. */
export function hoaCarrier(facts: Pick<ChartInput, 'tu_hoa' | 'palaces'>, hoaName: string): { star: string; palace: string | null } | null {
  const h = facts.tu_hoa?.[hoaName];
  if (!h) return null;
  return { star: h.star, palace: facts.palaces.find(p => p.branch_index === h.branch)?.name ?? null };
}

const ALLOWED: Record<GuardRelation, Relation[]> = { self: ['self'], opp: ['opp'], trine: ['trine'], tam_phuong: ['self', 'opp', 'trine'], flank: ['flank'], nhi_hop: [] };

export interface GuardOptions {
  /** the palace the rule fired on, for requirements whose `of` is '@palace' */
  here?: string;
  /** the chart's tu_hoa table, needed for carrier requirements (absent → a carrier requirement fails) */
  tuHoa?: ChartInput['tu_hoa'];
  /** also apply the 'book?' requirements (tightenings the audit marked needs-reading) */
  strict?: boolean;
}

/** True when every atom of the assertion that the guard names stands where the guard requires. A required atom absent from the assertion is
 *  skipped (an `any` branch not taken, or an absence); a present atom with no known palace, an unresolvable target palace, or a Hóa whose
 *  carrier cannot be checked fails: the guard is fail-closed. */
export function guardHolds(guard: Pick<PositionGuard, 'requires'>, assertionAtoms: Atom[], palaces: PalaceIdx[], opts: GuardOptions = {}): boolean {
  for (const r of guard.requires) {
    if (r.from === 'book?' && !opts.strict) continue;
    const present = assertionAtoms.filter(a => (a.kind === 'star' || a.kind === 'hoa' || a.kind === 'dignity') && a.name === r.atom);
    if (!present.length) continue;
    const target = r.of === '@palace' ? opts.here : r.of;
    if (!target) return false;
    for (const a of present) {
      if (!a.palace) return false;
      const want: string[] = Array.isArray(r.relation) ? r.relation : r.relation === 'nhi_hop' ? ['nhi_hop'] : ALLOWED[r.relation];
      const rel = relationOf(a.palace, target, palaces);
      if (!(rel && want.includes(rel)) && !(want.includes('nhi_hop') && isNhiHop(a.palace, target, palaces))) return false;
      if (a.kind === 'hoa' && (r.carrier || (r.carrierCandidates && opts.strict))) {
        const c = opts.tuHoa?.[r.atom]?.star;
        if (!c) return false;
        if (r.carrier && c !== r.carrier) return false;
        if (!r.carrier && r.carrierCandidates && opts.strict && !r.carrierCandidates.includes(c)) return false;
      }
    }
  }
  return true;
}
