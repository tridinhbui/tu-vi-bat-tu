// Adjudication (plan quirky-tinkering-rabin R3.3): what the chart says on each AXIS (a concept and its opposite, e.g. cog.sharp ↔ cog.dull), decided
// in a fixed order and never by counting votes:
//   (a) the book's own word: a relation or page-checked qualifier the resolver applied (status weakened / softened / narrowed) — and a reading
//       whose rule says the concept is REDUCED (stance 'weakens', e.g. "Hóa Lộc ở Tứ Mộ: tài lộc giảm") qualifies its side, it does not oppose it;
//   (b) specificity: a reading whose evidence contains the other's and more is the narrower one and wins (system convention, he_thong);
//   (c) tier: a reading resting on a more fundamental seat is the base; the other side is kept as a limit on it (he_thong);
//   (d) otherwise the axis is CONTESTED: both readings are kept, told as two sides, and neither is made the conclusion.
// Each decision is a Step with the rule, page and basis that caused it, so the panel can show why the prose says what it says.
import type { Concept, Knowledge } from '../types.ts';
import { nesting } from '../kg/atoms.ts';
import type { Resolved } from '../kg/resolve.ts';
import { rarity, seatOf, type Geo, type SeatRef } from './tiers.ts';

export type StepType = 'reading' | 'book_qualifies' | 'narrower_wins' | 'tier_precedence' | 'contested' | 'rescue' | 'corroborated' | 'countered'
  | 'formation' | 'interaction';
export interface Step { type: StepType; ruleId?: string; against?: string; seat?: string; palace?: string; cite?: string; basis: 'sach' | 'he_thong'; note?: string }

/** One reading as the reasoner sees it: the resolved assertion plus its seat, links and rarity. */
export interface Reading { r: Resolved; seat: SeatRef; links: SeatRef[]; rarity: number }
export interface Axis {
  key: string; concept: string; opp?: string; verdict: 'affirmed' | 'qualified' | 'contested';
  /** base: affirm the winning concept; against: affirm its opposite (a limit when qualified, the other side when contested);
   *  reducers: say the winning concept is reduced; weakenedBase: base readings the book itself weakened */
  base: Reading[]; against: Reading[]; reducers: Reading[]; steps: Step[];
}

const LIVE = (r: Resolved) => r.status !== 'voided' && r.status !== 'divergent';
const STRONG = (x: Reading) => x.r.status === 'holds' || x.r.status === 'narrowed';
/** The evidence signature for specificity: the resolver's signature folds a dignity into its star, but "Cự Môn hãm" is narrower than "Cự Môn". */
const specSig = (x: Reading) => new Set([...x.r.sig, ...x.r.atoms.filter(a => a.kind === 'dignity').map(a => `dignity|${a.name}|${a.palace}|${a.value}`)]);

export function readingsOf(resolved: Resolved[], g: Geo, k: Knowledge): Reading[] {
  return resolved.filter(LIVE).map(r => ({ r, ...seatOf(r, g), rarity: rarity(k, r.ruleId) }));
}

/** The reading that stands for a side: the most fundamental seat, then the rarest rule. */
export const best = (ys: Reading[]) => [...ys].sort((p, q) => p.seat.tier - q.seat.tier || q.rarity - p.rarity || (p.r.ruleId < q.r.ruleId ? -1 : 1))[0];

export function axes(readings: Reading[], k: Knowledge): Axis[] {
  const cmap = new Map<string, Concept>(k.concepts.concepts.map(c => [c.id, c]));
  const axisOf = (c: string) => { const o = cmap.get(c)?.opp; return o && o < c ? `${o}|${c}` : o ? `${c}|${o}` : c; };
  const groups = new Map<string, Reading[]>();
  for (const x of readings) {
    if (x.r.additive) continue;                               // độ số modifiers add up; the degree line reads them, not an axis
    const key = axisOf(x.r.concept);
    (groups.get(key) ?? groups.set(key, []).get(key)!).push(x);
  }
  const out: Axis[] = [];
  for (const [key, xs] of groups) {
    const [a, b] = key.split('|');
    const aff = (c: string | undefined) => xs.filter(x => x.r.concept === c && x.r.stance === 'affirms');
    const red = (c: string | undefined) => xs.filter(x => x.r.concept === c && x.r.stance === 'weakens');
    const A = aff(a), B = aff(b);
    const bookSteps = (ys: Reading[]): Step[] => ys.flatMap(x => x.r.by.filter(y => y.basis === 'sach')
      .map(y => ({ type: y.type === 'rescues' ? 'rescue' : 'book_qualifies', ruleId: y.byRule, against: x.r.ruleId, cite: y.cite, basis: 'sach' } as Step)));
    const finish = (concept: string, opp: string | undefined, base: Reading[], against: Reading[], extra: Step[], contested = false) => {
      const reducers = red(concept);
      const steps = [...bookSteps(base), ...reducers.map(x => ({ type: 'book_qualifies', ruleId: x.r.ruleId, against: base[0]?.r.ruleId, cite: x.r.cites[0], basis: 'sach' } as Step)), ...extra];
      const qualified = against.length || reducers.length || base.every(x => !STRONG(x));
      out.push({ key, concept, opp, verdict: contested ? 'contested' : qualified ? 'qualified' : 'affirmed', base, against, reducers, steps });
    };
    if (!A.length && !B.length) continue;                     // only reducers: nothing affirmed to reduce
    if (!B.length) { finish(a, b, A, [], []); continue; }
    if (!A.length) { finish(b, a, B, [], []); continue; }
    // both sides affirmed. A reading the book weakened stays on its side, told in its reduced form: weakened is "less", not "defeated"
    // (only a voided reading drops out, and readingsOf already removed those)
    const pa = best(A.filter(STRONG).length ? A.filter(STRONG) : A), pb = best(B.filter(STRONG).length ? B.filter(STRONG) : B);
    // (b) specificity
    const n = nesting(specSig(pa), specSig(pb));
    if (n === 'narrower' || n === 'broader') {
      const [w, l, wc, lc, wr, lr] = n === 'narrower' ? [A, B, a, b, pa, pb] : [B, A, b, a, pb, pa];
      finish(wc, lc, w, l, [{ type: 'narrower_wins', ruleId: wr.r.ruleId, against: lr.r.ruleId, basis: 'he_thong' }]);
      continue;
    }
    // (c) tier
    if (pa.seat.tier !== pb.seat.tier) {
      const [w, l, wc, lc, wr, lr] = pa.seat.tier < pb.seat.tier ? [A, B, a, b, pa, pb] : [B, A, b, a, pb, pa];
      finish(wc, lc, w, l, [{ type: 'tier_precedence', ruleId: wr.r.ruleId, against: lr.r.ruleId, seat: wr.seat.id, basis: 'he_thong' }]);
      continue;
    }
    // (d) contested
    finish(a, b, A, B, [{ type: 'contested', ruleId: pa.r.ruleId, against: pb.r.ruleId, basis: 'he_thong' }], true);
  }
  return out;
}
