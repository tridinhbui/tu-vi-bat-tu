// Interpretation Reasoner for the Mệnh chapter (plan quirky-tinkering-rabin R3). It finishes the reading BEFORE any sentence is written:
//   1. frame     the Mệnh configuration and the cách cục it forms; which seat carries the most weight (is the chính tinh the centre?)
//   2. seats     every live reading is placed on the structural element it rests on (tiers.ts) and each seat is scored by tier × scope ×
//                the rarity of its rules — a seat whose readings most charts also get weighs little
//   3. axes      each concept/opposite pair is adjudicated (adjudicate.ts): book word → specificity → tier → contested
//   4. claims    each axis belongs to the seat of its strongest reading; a claim is kept only if it tells this chart apart (a concept most
//                charts get, carried only by common rules, is left out)
//   5. theses    the two or three seats with the strongest claims become the theses, each with its steps (book qualifiers, precedence,
//                rescues and the caveat on the rescuer itself, corroboration or counter-evidence from Tài Bạch / Quan Lộc / Thiên Di)
// The result is a ReadingPlan: plain data, testable without any prose. The narrative layer (prose/narrative.ts) may say only what is in it.
import type { ChartInput, Concept, Knowledge, Rule } from '../types.ts';
import { run } from '../engine.ts';
import { lift, type Labelled } from '../kg/lift.ts';
import { applyQualifiers, resolve, type Resolved } from '../kg/resolve.ts';
import { triggerAtoms } from '../kg/atoms.ts';
import type { World } from '../dsl.ts';
import { axes, best, readingsOf, type Axis, type Reading, type Step } from './adjudicate.ts';
import { Geo, SCOPE_WEIGHT, TIER_WEIGHT, conceptRate, rarity, ruleRate, seatOf, type SeatRef } from './tiers.ts';
import { guardHolds } from './positions.ts';
import { detectStructures, evaluateFormations, type FormationState as FState, type Structure, type Verification } from './structures.ts';
import { palaceEvidence, readsElement, TIMING_FACET, type Element, type PalaceEvidence } from './evidence.ts';

export const REASONER_VERSION = 'reasoner-0.4.0';

export interface Formation { ruleId: string; name: string; condition: string; rate: number; rarity: number; seat: string; kind: 'formation' | 'classification'; pol?: '+' | '-'; cites: string[] }
/** A draft cách cục (engine/data/experimental/formations_experimental.json) evaluated on the chart: thành / thành thượng / bị phá / phá được cứu. */
export interface CachState { id: string; name: string; state: FState; stateVi: string; seat: string; boosters: string[]; breakers: string[]; rescuers: string[]; uncovered: string[];
  verification: string; experimental: boolean }
/** A special structure at Mệnh (structures.ts detectStructures, port of synthesis/structures.py). `position`: no book sentence for it
 *  (chua_du_nguon), so it is told only as where things stand — no limiter, rescuer, reading or caveat is carried. `thesis`: the thesis whose
 *  seat it concerns and whose steps carry it; absent when no thesis stands on those seats. */
export interface StructureNote { id: string; name: string; verification: Verification; position: boolean; seats: string[]; thesis?: string;
  limiters: string[]; rescuers: string[]; caveat: string; cites: string[]; matrixIds: string[] }
/** An assertion the R1 position guard rejected: its rule fired, but an atom does not stand where the book's wording puts it. */
export interface Guarded { ruleId: string; concept: string; reason: string; cite: string }
export interface Seat { ref: SeatRef; readings: Reading[]; formations: Formation[]; states: CachState[]; score: number }
export interface Claim { axis: Axis; concept: string; soft: boolean; score: number; conceptRate: number; rarest: number;
  /** a big conclusion (career, money, marriage, health) resting on one minor star or one rule of minor stars: unless the chapter tells
   *  another palace saying the same (a corroboration), it is told as what that star alone suggests, never as the palace's conclusion */
  single?: string[];
  /** the claim is a strength, but a star it rests on carries Hóa Kỵ in this palace: it is never told as a plain positive */
  kyCarrier?: string;
}
/** A limiting element standing in the palace (Hóa Kỵ, a sát tinh not checked đắc, a hãm chính tinh, Tuần / Triệt, a star carrying Kỵ) and
 *  the verified readings that stand on it: the chapter must face it — by one of these readings, or by a structural conditional sentence. */
export interface Confront { element: Element; readings: Reading[] }
export interface Cross { type: 'corroborated' | 'countered'; palace: string; ruleId: string; concept: string; cite?: string }
export interface Thesis {
  id: string; seat: SeatRef; formations: Formation[]; states: CachState[]; claims: Claim[]; steps: Step[]; cross: Cross[]; score: number;
  /** the seat that rescues this thesis' limit, when that seat's own reading is reduced elsewhere on the chart (told together) */
  rescuerCaveat?: { seat: SeatRef; axis: Axis };
}
export interface ReadingPlan {
  /** the palace read: Mệnh (reasonMenh) or any other (reasonPalace); every field below is relative to it */
  version: string; palace: string;
  frame: { branch: string; majors: Array<{ star: string; dignity?: string; hoa: string[] }>; vcd: boolean; borrowed: string[]; tuan: boolean; triet: boolean;
    than: boolean; formations: Formation[]; states: CachState[]; centre: { seat: SeatRef; why: 'major' | 'formation' | 'outweighs_major' | 'vcd' } };
  theses: Thesis[];
  /** elements standing in Mệnh that change the picture though they are not theses (a Hóa, a sát or cát tinh, Tuần/Triệt): one reading each,
   *  chosen by structure, not by rarity — the answer to "how much does this Kình Dương change the conclusion?" */
  modifiers: Array<{ seat: SeatRef; reading: Reading }>;
  course?: { axis: Axis; rarest: number };
  degree: { up: string[]; down: string[]; lean: 'up' | 'down' | 'mixed' };
  contested: Axis[];
  residue: Array<{ seat: string; concepts: string[] }>;
  distinct: { rules: Array<{ id: string; rate: number }>; meanConceptRate: number };
  seats: Array<{ id: string; tier: number; score: number; rules: number }>;
  guarded: Guarded[];
  structures: StructureNote[];
  /** every structural element of the palace (reason/evidence.ts), whether or not a rule read it */
  evidence: PalaceEvidence;
  /** the limiting elements of the palace, each with the verified readings standing on it (limits first) */
  confront: Confront[];
  /** verified timing readings of the palace (rel.timing, career.late, …): told, never dropped as a mere course line */
  timings: Reading[];
}
/** facets of the big conclusions that may not rest on one minor star */
export const BIG = /^(career|finance|wellbeing)\.|^relationships\.(marriage|partner|romance)$/;
/** States of a cách cục worth telling: one that only has the shape (hình thức), is absent or lacks data says nothing about the chart. */
const TOLD: Set<FState> = new Set(['thanh', 'thanh_thuong', 'bi_pha', 'pha_duoc_cuu'] as FState[]);
const STATE_BONUS: Partial<Record<FState, number>> = { thanh_thuong: 1.2, thanh: 1, pha_duoc_cuu: 0.8, bi_pha: 0.8 };

/** Concepts the Mệnh chapter may make a thesis of; life.timing / life.mobility go to the course line. */
const CLAIMABLE = (c?: Concept) => !!c && (c.facet.startsWith('identity.') || c.facet.startsWith('inner.') || c.facet === 'life.course' || c.facet === 'life.legal'
  || c.facet === 'life.spirituality' || c.facet === 'finance.flow' || c.facet === 'career.trajectory' || c.facet === 'career.authority');
const COURSE = (c?: Concept) => !!c && (c.facet === 'life.timing' || c.facet === 'life.mobility');
const CROSS: Array<[RegExp, string[]]> = [[/^finance\./, ['Tài Bạch']], [/^career\./, ['Quan Lộc']], [/^(identity|inner)\./, ['Thiên Di']], [/^life\.course/, ['Quan Lộc', 'Tài Bạch']]];
const facetIn = (...pre: string[]) => (c?: Concept) => !!c && pre.some(p => c.facet === p || c.facet.startsWith(p + '.'));
/** What each other palace may make a thesis of (the topics of chapter.ts PROSE_SPECS, the same split): the palace's own subject and what
 *  the books say of the people it stands for. Timing concepts go to the course line, as at Mệnh. */
const POOL: Record<string, (c?: Concept) => boolean> = {
  'Quan Lộc': facetIn('career', 'finance.flow', 'life.course', 'life.legal'),
  'Tài Bạch': facetIn('finance', 'life.course'),
  'Thiên Di': facetIn('life', 'finance', 'identity', 'inner', 'career'),
  'Phu Thê': facetIn('relationships.marriage', 'relationships.partner', 'relationships.romance', 'identity', 'career', 'finance', 'wellbeing', 'life.course'),
  'Phúc Đức': facetIn('inner', 'life', 'wellbeing', 'relationships.family', 'finance', 'career.support', 'identity'),
  'Điền Trạch': facetIn('finance', 'life', 'relationships.family'),
  'Nô Bộc': facetIn('relationships.allies', 'career', 'identity', 'finance', 'life.course'),
  'Tử Tức': facetIn('relationships.kin', 'relationships.family', 'relationships.allies', 'career', 'finance', 'identity'),
  'Huynh Đệ': facetIn('relationships.kin', 'relationships.family', 'career', 'finance', 'identity'),
  'Phụ Mẫu': facetIn('relationships', 'career', 'finance', 'identity', 'inner', 'life.course'),
  'Tật Ách': facetIn('wellbeing', 'life', 'inner'),
};
const TIMING = (c?: Concept) => !!c && (c.facet.endsWith('.timing') || c.facet === 'life.mobility');
/** the palaces of a palace's tam phương tứ chính (its opposite and its two tam hợp), by branch */
const tamPhuong = (g: Geo) => [...g.byName.values()].filter(p => { const d = (p.branch_index - g.menh.branch_index + 12) % 12; return d === 4 || d === 6 || d === 8; }).map(p => p.name);
/** A concept at least this common (≥ 60 % of the corpus), carried only by rules firing on more than ~7 % of it, does not tell the chart apart. */
const BARNUM_RATE = 0.6, BARNUM_RARITY = 0.5;

export interface ReasonInput { chart: ChartInput; k: Knowledge; resolvedAll?: Resolved[]; labelled?: Labelled[] }

export interface ReasonOptions {
  /** evaluate the draft cách cục (thành / phá / cứu) and let them weigh on the seats; the narrative passes allowDraft (default true) */
  draftFormations?: boolean;
  /** also apply the guards' needs-reading tightenings ('book?') */
  strictGuards?: boolean;
}

export function reasonMenh(chart: ChartInput, k: Knowledge, pre?: { resolved: Resolved[]; labelled: Labelled[] }, opts: ReasonOptions = {}): ReadingPlan {
  return reasonPalace(chart, k, 'Mệnh', pre, opts);
}

/** The same reasoning for any palace (prose-style plan S4): its own readings on seats relative to it, the corpus rates of that palace, its
 *  topic pool, corroboration from its tam phương tứ chính. Mệnh keeps its own pool, chart-level readings and cross-palace map. */
export function reasonPalace(chart: ChartInput, k: Knowledge, P: string, pre?: { resolved: Resolved[]; labelled: Labelled[] }, opts: ReasonOptions = {}): ReadingPlan {
  const isMenh = P === 'Mệnh';
  const claimable = isMenh ? CLAIMABLE : (c?: Concept) => !!POOL[P]?.(c) && !TIMING(c);
  const course = isMenh ? COURSE : (c?: Concept) => !!POOL[P]?.(c) && TIMING(c);
  let resolvedAll: Resolved[], labelled: Labelled[];
  if (pre) ({ resolved: resolvedAll, labelled } = pre);
  else {
    const findings = run(k.rules, k.sources, chart.base).findings;
    const lifted = lift(findings, k, chart.base);
    resolvedAll = resolve(lifted.assertions, k).resolved;
    applyQualifiers(resolvedAll, k, chart.base);
    labelled = lifted.labelled;
  }
  const g = new Geo(chart, P);
  const cmap = new Map(k.concepts.concepts.map(c => [c.id, c]));
  const rmap = new Map<string, Rule>(k.rules.map(r => [r.id, r]));
  const here = (r: { subject: string }) => r.subject === `palace:${P}` || (isMenh && r.subject === 'chart');
  // position guards (R1): a fired rule whose atoms do not stand where the book's wording puts them is not used, and is listed as guarded
  const guards = new Map((k.kg?.positionGuards ?? []).map(x => [x.ruleId, x]));
  const guarded: Guarded[] = [];
  const placed = (r: { ruleId: string; atoms: Resolved['atoms']; palace: string | null; concept?: string }) => {
    const gd = guards.get(r.ruleId);
    if (!gd || guardHolds(gd, r.atoms, chart.palaces, { here: r.palace ?? P, tuHoa: chart.tu_hoa, strict: !!opts.strictGuards })) return true;
    if (!guarded.some(x => x.ruleId === r.ruleId && x.concept === (r.concept ?? ''))) guarded.push({ ruleId: r.ruleId, concept: r.concept ?? '', reason: gd.reason, cite: gd.cite });
    return false;
  };
  resolvedAll = resolvedAll.filter(placed);
  const readings = readingsOf(resolvedAll.filter(here), g, k);

  // ---- seats and the formations that sit on them ----
  const seats = new Map<string, Seat>();
  const seatFor = (ref: SeatRef) => seats.get(ref.id) ?? seats.set(ref.id, { ref, readings: [], formations: [], states: [], score: 0 }).get(ref.id)!;
  readings.forEach(x => seatFor(x.seat).readings.push(x));
  const world: World = n => chart.base[`palace:${n}`] ? { ...(chart.base.chart ?? {}), ...chart.base[`palace:${n}`] } : null;
  const formations: Formation[] = [];
  for (const l of labelled.filter(here)) {
    if (formations.some(f => f.ruleId === l.ruleId)) continue;
    const rule = rmap.get(l.ruleId)!;
    const atoms = triggerAtoms(rule.conditions, { ...(chart.base.chart ?? {}), ...(chart.base[l.subject] ?? {}) }, world, l.palace);
    if (!placed({ ruleId: l.ruleId, atoms, palace: l.palace })) continue;
    const { seat } = seatOf({ atoms, subject: l.subject }, g);
    const text = (rule.reading ?? k.claims[rule.consequences[0]?.claim ?? ''] ?? '').trim();
    const m = text.match(/^(.*?)\s*\((.*)\)\s*$/);
    const rate = ruleRate(k, l.ruleId, P);
    const f: Formation = { ruleId: l.ruleId, name: (m?.[1] ?? text).replace(/^nhóm\s+/, 'nhóm '), condition: m?.[2] ?? '', rate, rarity: rarity(k, l.ruleId, P), seat: seat.id,
      kind: l.kind, pol: l.pol, cites: l.cites };
    formations.push(f);
    seatFor(seat).formations.push(f);
  }
  // draft cách cục at Mệnh (R2a port of the Python evaluator): the state sits on the seat of its core stars and weighs on it
  const states: CachState[] = [];
  if (opts.draftFormations ?? true) {
    const menhFacts = { ...(chart.base.chart ?? {}), ...(chart.base[`palace:${P}`] ?? {}) };
    const defs = new Map((k.kg?.formations ?? []).map(f => [f.id, f]));
    for (const f of evaluateFormations(k.kg?.formations ?? [], chart.base)) {
      if (f.anchor !== P || !TOLD.has(f.state)) continue;
      const { seat } = seatOf({ atoms: triggerAtoms(defs.get(f.id)!.core, menhFacts, world, P), subject: `palace:${P}` }, g);
      const st: CachState = { id: f.id, name: f.name, state: f.state, stateVi: f.stateVi, seat: seat.id, boosters: f.boosters.map(x => x.label), breakers: f.breakers.map(x => x.label),
        rescuers: f.rescuers.map(x => x.label), uncovered: f.uncovered.map(x => x.label), verification: f.verification, experimental: f.experimental };
      states.push(st);
      seatFor(seat).states.push(st);
    }
  }
  for (const s of seats.values()) {
    const rules = [...new Map(s.readings.map(x => [x.r.ruleId, x.rarity])).values()].sort((a, b) => b - a).slice(0, 3);
    const formBonus = s.formations.filter(f => f.kind === 'formation').reduce((a, f) => a + 1.5 * f.rarity, 0) + s.states.reduce((a, x) => a + (STATE_BONUS[x.state] ?? 0), 0);
    const tier = s.formations.some(f => f.kind === 'formation') || s.states.length ? Math.min(s.ref.tier, 2) as SeatRef['tier'] : s.ref.tier;
    s.score = +(TIER_WEIGHT[tier] * SCOPE_WEIGHT[s.ref.scope] * (0.5 + rules.reduce((a, b) => a + b, 0) + formBonus)).toFixed(3);
  }

  // ---- axes and claims ----
  const all = axes(readings, k);
  const owner = (ax: Axis) => best(ax.base.length ? ax.base : [...ax.against, ...ax.reducers])?.seat.id;
  const claimOf = (ax: Axis): Claim | null => {
    const c = cmap.get(ax.concept);
    if (!claimable(c) || !ax.base.length && ax.verdict !== 'contested') return null;
    const rarest = Math.max(...[...ax.base, ...ax.reducers, ...ax.against].map(x => x.rarity));
    const cr = conceptRate(k, ax.concept, P);
    if (cr >= BARNUM_RATE && rarest < BARNUM_RARITY) return null;
    const info = Math.max(0, Math.min(1, Math.log2(1 / Math.max(cr, 0.02)) / Math.log2(20)));
    const soft = ax.verdict !== 'affirmed' && (ax.reducers.length > 0 || ax.base.every(x => x.r.status !== 'holds' && x.r.status !== 'narrowed'));
    return { axis: ax, concept: ax.concept, soft, score: +(rarest + 0.5 * info).toFixed(3), conceptRate: cr, rarest: +rarest.toFixed(3) };
  };
  const bySeat = new Map<string, Claim[]>();
  for (const ax of all) {
    const cl = claimOf(ax), o = owner(ax);
    if (cl && o) (bySeat.get(o) ?? bySeat.set(o, []).get(o)!).push(cl);
  }

  // ---- theses ----
  const resolvedOther = (palaces: string[]) => resolvedAll.filter(r => palaces.some(p => r.subject === `palace:${p}`) && r.status !== 'voided' && r.status !== 'divergent');
  const cand: Thesis[] = [];
  for (const [sid, cls] of bySeat) {
    const s = seats.get(sid)!;
    // a thesis leads with a conclusion: a contested axis is never its first claim, and at most one of its claims
    cls.sort((a, b) => Number(a.axis.verdict === 'contested') - Number(b.axis.verdict === 'contested') || b.score - a.score || (a.concept < b.concept ? -1 : 1));
    const claims = cls.filter((c, i) => i === 0 || c.axis.verdict !== 'contested' || !cls.slice(0, i).some(d => d.axis.verdict === 'contested')).slice(0, 2);
    const steps: Step[] = claims.flatMap(c => c.axis.steps);
    for (const f of s.formations) steps.unshift({ type: 'formation', ruleId: f.ruleId, cite: f.cites[0], basis: 'sach' });
    for (const c of claims) for (const x of c.axis.base) for (const l of x.links) steps.push({ type: 'interaction', ruleId: x.r.ruleId, seat: l.id, cite: x.r.cites[0], basis: 'sach' });
    const cross: Cross[] = [];
    for (const c of claims) {
      const facet = cmap.get(c.concept)!.facet, opp = cmap.get(c.concept)?.opp;
      const pals = isMenh ? CROSS.find(([re]) => re.test(facet))?.[1] ?? [] : tamPhuong(g);
      for (const r of resolvedOther(pals)) {
        if (r.concept === c.concept && r.stance === 'affirms') cross.push({ type: 'corroborated', palace: r.palace!, ruleId: r.ruleId, concept: r.concept, cite: r.cites[0] });
        else if ((r.concept === opp && r.stance === 'affirms') || (r.concept === c.concept && r.stance === 'weakens')) cross.push({ type: 'countered', palace: r.palace!, ruleId: r.ruleId, concept: r.concept, cite: r.cites[0] });
      }
    }
    const top = Math.max(...claims.map(c => c.score));
    cand.push({ id: `T:${sid}`, seat: s.ref, formations: s.formations, states: s.states, claims, steps, cross: dedupeCross(cross), score: +(s.score * (0.6 + top)).toFixed(3) });
  }
  cand.sort((a, b) => b.score - a.score || (a.id < b.id ? -1 : 1));
  const theses = cand.filter((t, i) => i < 2 || (i === 2 && t.score >= 0.4 * cand[0].score));
  // a thesis whose claim rests on a link to another seat (a rescue, an interaction) carries that seat's own reduction, when it has one
  const RESCUE = new Set(['life.mitigated', 'life.blessed']);
  for (const t of theses) for (const c of t.claims.filter(c => RESCUE.has(c.concept) || c.axis.steps.some(st => st.type === 'rescue'))) for (const x of c.axis.base) for (const l of x.links) {
    const red = all.find(ax => owner(ax) === l.id && ax.reducers.length);
    if (red && !t.rescuerCaveat) t.rescuerCaveat = { seat: l, axis: red };
  }

  // ---- special structures at Mệnh: their limiters, rescuers and caveat become steps of the thesis standing on their seats ----
  const structures = structuresAtMenh(detectStructures(chart.palaces, chart.tu_hoa), g.vcd ? g.opp.major_stars : g.majors, g.vcd, P);
  for (const st of structures) {
    const t = theses.find(t => st.note.seats.includes(t.seat.id));
    if (!t) continue;
    st.note.thesis = t.id;
    t.steps.push(...st.steps);
  }

  // ---- modifiers: Hóa, sát/cát tinh and Tuần/Triệt in Mệnh that no thesis carries ----
  const thesisRules = new Set(theses.flatMap(t => t.claims.flatMap(c => [...c.axis.base, ...c.axis.against, ...c.axis.reducers].map(x => x.r.ruleId))));
  const isMod = (s: Seat) => s.ref.scope === 'self' && (s.ref.kind === 'hoa' || s.ref.kind === 'tuan_triet' || (s.ref.kind === 'star' && s.ref.tier === 4));
  const modifiers = [...seats.values()].filter(s => isMod(s) && !theses.some(t => t.seat.id === s.ref.id))
    .map(s => ({ seat: s.ref, reading: [...s.readings].filter(x => !thesisRules.has(x.r.ruleId) && !x.r.additive && (claimable(cmap.get(x.r.concept)) || course(cmap.get(x.r.concept))))
      .sort((a, b) => Number(b.r.status === 'holds') - Number(a.r.status === 'holds') || b.rarity - a.rarity || (a.r.ruleId < b.r.ruleId ? -1 : 1))[0], score: s.score }))
    .filter(m => m.reading).sort((a, b) => b.score - a.score || (a.seat.id < b.seat.id ? -1 : 1)).slice(0, 4).map(({ seat, reading }) => ({ seat, reading }));

  // ---- course line, độ số, residue ----
  const courseAx = all.filter(ax => course(cmap.get(ax.concept)) && ax.base.length)
    .map(ax => ({ axis: ax, rarest: Math.max(...ax.base.map(x => x.rarity)) })).sort((a, b) => b.rarest - a.rarest)[0];
  const deg = readings.filter(x => x.r.additive && x.r.concept === 'life.degree');
  const up = [...new Set(deg.filter(x => x.r.stance === 'affirms').map(x => x.r.ruleId))].sort(), down = [...new Set(deg.filter(x => x.r.stance === 'weakens').map(x => x.r.ruleId))].sort();
  const usedSeats = new Set(theses.map(t => t.seat.id));
  const residue = [...bySeat.entries()].filter(([s]) => !usedSeats.has(s)).map(([seat, cls]) => ({ seat, concepts: cls.map(c => c.concept) }));
  const centreSeat = [...seats.values()].sort((a, b) => b.score - a.score || (a.ref.id < b.ref.id ? -1 : 1))[0];
  const majorSeat = [...seats.values()].filter(s => s.ref.kind === 'major').sort((a, b) => b.score - a.score)[0];
  const why: ReadingPlan['frame']['centre']['why'] = g.vcd ? 'vcd' : centreSeat?.ref.kind === 'major' ? 'major'
    : centreSeat?.formations.some(f => f.kind === 'formation') || centreSeat?.states.length ? 'formation' : 'outweighs_major';
  const usedRules = [...new Set(theses.flatMap(t => [...t.claims.flatMap(c => [...c.axis.base, ...c.axis.reducers].map(x => x.r.ruleId)), ...t.formations.map(f => f.ruleId)]))];

  // ---- evidence, guards on big conclusions, the limits to face, the timing readings ----
  const evidence = palaceEvidence(chart, k, P, { resolved: resolvedAll });
  const kyStars = new Set(evidence.mixed.filter(e => e.kind === 'ky_carrier').map(e => e.star!));
  for (const t of theses) for (const c of t.claims) {
    const con = cmap.get(c.concept);
    // a strength resting on a star that carries Hóa Kỵ here is never a plain positive
    if (con?.pol !== '-') {
      const ky = c.axis.base.flatMap(x => x.r.atoms).find(a => a.kind === 'star' && a.palace === P && kyStars.has(a.name));
      if (ky) c.kyCarrier = ky.name;
    }
    // one minor star (or one rule of minor stars) is not enough for a big conclusion
    if (con && BIG.test(con.facet) && c.axis.verdict !== 'contested' && c.axis.base.length && c.axis.base.every(x => x.seat.tier >= 4)
      && new Set(c.axis.base.map(x => x.r.ruleId)).size <= 1)
      c.single = [...new Set(c.axis.base.flatMap(x => x.r.atoms).filter(a => (a.kind === 'star' || a.kind === 'hoa') && a.palace !== null).map(a => a.name))];
  }
  const live = readings.filter(x => rmap.get(x.r.ruleId)?.reviewStatus === 'verified');
  const confront: Confront[] = [...evidence.limit, ...evidence.mixed.filter(e => e.kind === 'ky_carrier')].map(e => ({
    element: e,
    readings: live.filter(x => readsElement(x.r, e, P) && !x.r.additive)
      .sort((a, b) => Number(isLimit(b)) - Number(isLimit(a)) || b.rarity - a.rarity || (a.r.ruleId < b.r.ruleId ? -1 : 1)),
  }));
  function isLimit(x: Reading) { return cmap.get(x.r.concept)?.pol === '-' || x.r.stance === 'weakens' || TIMING_FACET(cmap.get(x.r.concept)?.facet ?? ''); }
  // a timing reading stands on a star, a Hóa or Tuần/Triệt of the palace (the độ số timings of the chart are the overview's)
  const timings = live.filter(x => x.r.subject === `palace:${P}` && x.r.atoms.some(a => a.kind === 'star' || a.kind === 'hoa' || a.kind === 'tuan_triet') && TIMING_FACET(cmap.get(x.r.concept)?.facet ?? '') && (isMenh || POOL[P]?.(cmap.get(x.r.concept)) || x.r.concept.startsWith('rel.') || x.r.concept.startsWith('career.')))
    // at Mệnh (whose course line already tells the rarest timing) only a timing that tells the chart apart: a concept under half the corpus,
    // a rule as rare as the course line's (rarity ≥ 0.3)
    .filter(x => !isMenh || (conceptRate(k, x.r.concept, P) < 0.5 && x.rarity >= 0.3))
    .sort((a, b) => b.rarity - a.rarity || (a.r.ruleId < b.r.ruleId ? -1 : 1));
  return {
    version: REASONER_VERSION, palace: P,
    frame: {
      branch: g.menh.branch, vcd: g.vcd, borrowed: g.vcd ? g.opp.major_stars : [], tuan: !!g.menh.tuan, triet: !!g.menh.triet, than: !!g.menh.is_than,
      majors: g.majors.map(s => ({ star: s, dignity: g.dignity(s, P), hoa: Object.entries(g.hoaCarrier).filter(([, v]) => v.star === s && v.palace === P).map(([h]) => h) })),
      formations: formations.filter(f => f.kind === 'formation' || f.rarity >= 0.3).sort((a, b) => b.rarity - a.rarity),
      states: [...states].sort((a, b) => (STATE_BONUS[b.state] ?? 0) - (STATE_BONUS[a.state] ?? 0) || (a.id < b.id ? -1 : 1)),
      centre: { seat: (why === 'major' || why === 'vcd') && majorSeat ? majorSeat.ref : centreSeat?.ref ?? { id: 'degree', kind: 'degree', tier: 5, scope: 'chart' }, why },
    },
    theses,
    modifiers,
    course: courseAx && courseAx.rarest >= 0.3 ? courseAx : undefined,
    degree: { up, down, lean: up.length - down.length >= 2 ? 'up' : down.length - up.length >= 2 ? 'down' : 'mixed' },
    contested: all.filter(ax => ax.verdict === 'contested'),
    residue,
    distinct: { rules: usedRules.map(id => ({ id, rate: ruleRate(k, id, P) })).sort((a, b) => a.rate - b.rate),
      meanConceptRate: +(theses.flatMap(t => t.claims).reduce((a, c, _, xs) => a + c.conceptRate / xs.length, 0)).toFixed(3) },
    seats: [...seats.values()].sort((a, b) => b.score - a.score).map(s => ({ id: s.ref.id, tier: s.ref.tier, score: s.score, rules: new Set(s.readings.map(x => x.r.ruleId)).size })),
    guarded,
    structures: structures.map(x => x.note),
    evidence, confront, timings,
  };
}

/** A page named in a structure line ("… (KL tr.66; TH tr.52 …)"): the line is then a book sentence, the juxtaposition is still the system's. */
const PAGE = /\b(?:KL|TH|TT) tr\.\d+(?:–\d+)?/;
/** The seats a structure concerns, by its kind (seat ids of tiers.ts): Cự Môn and the Lộc it carries; the Kình Dương in Mệnh; the Sát/Phá/Tham
 *  that stand in Mệnh; the three Hóa and Mệnh's own chính tinh. For Mệnh vô chính diệu `majors` are the borrowed stars of the opposite palace
 *  (their seat ids are `major:<star>` too) and the vô chính diệu seat counts as Mệnh's own. */
function structureSeats(s: Structure, majors: string[], vcd: boolean): string[] {
  const own = (xs: string[]) => [...(vcd ? ['major:vcd'] : []), ...xs.filter(x => majors.includes(x)).map(x => `major:${x}`)];
  switch (s.id) {
    case 'CU_MON_HOA_LOC': return ['major:Cự Môn', 'hoa:Hóa Lộc'];
    case 'KINH_DUONG_TU_MO': return ['star:Kình Dương'];
    case 'SAT_PHA_THAM': return own(['Thất Sát', 'Phá Quân', 'Tham Lang']);
    case 'TAM_HOA_HOI_MENH': return ['hoa:Hóa Lộc', 'hoa:Hóa Quyền', 'hoa:Hóa Khoa', ...own(majors)];
    default: return [];
  }
}

/** Present structures that stand at Mệnh, each with the steps it adds. A chua_du_nguon structure adds one position step and nothing else. */
export function structuresAtMenh(all: Structure[], majors: string[], vcd = false, palace = 'Mệnh'): Array<{ note: StructureNote; steps: Step[] }> {
  return all.filter(s => s.present && s.palaces.includes(palace)).map(s => {
    const position = s.verification === 'chua_du_nguon';
    const note: StructureNote = { id: s.id, name: s.name, verification: s.verification, position, seats: structureSeats(s, majors, vcd),
      limiters: position ? [] : s.limiters, rescuers: position ? [] : s.rescuers, caveat: position ? '' : s.caveat, cites: s.cites, matrixIds: s.matrix_ids };
    if (position) return { note, steps: [{ type: 'structure_position', structure: s.id, note: s.name, basis: 'he_thong' }] };
    const line = (type: Step['type'], text: string): Step => {
      const cite = text.match(PAGE)?.[0];
      return { type, structure: s.id, note: text, basis: cite ? 'sach' : 'he_thong', ...(cite ? { cite } : {}) };
    };
    // the structure itself is a book reading only when every component is (da_doi_chieu); otherwise the system juxtaposes, with no page of its own
    const head: Step = s.verification === 'da_doi_chieu' ? { type: 'structure', structure: s.id, note: s.name, cite: s.cites[0], basis: 'sach' }
      : { type: 'structure', structure: s.id, note: s.name, basis: 'he_thong' };
    const steps: Step[] = [head,
      ...s.limiters.map(x => line('structure_limit', x)), ...s.rescuers.map(x => line('structure_rescue', x))];
    if (s.caveat) steps.push({ type: 'structure_caveat', structure: s.id, note: s.caveat, basis: 'he_thong' });
    return { note, steps };
  });
}

function dedupeCross(xs: Cross[]): Cross[] {
  return [...new Map(xs.map(x => [`${x.type}|${x.palace}|${x.concept}`, x])).values()];
}

/** The plan as plain JSON for the API and the evidence panel: each reading reduced to its rule, concept, status, seat and corpus rate. */
export function planView(p: ReadingPlan) {
  const rd = (x: Reading) => ({ ruleId: x.r.ruleId, concept: x.r.concept, stance: x.r.stance, status: x.r.status, seat: x.seat.id, links: x.links.map(l => l.id), rarity: +x.rarity.toFixed(3), cites: x.r.cites });
  const ax = (a: Axis) => ({ key: a.key, concept: a.concept, opp: a.opp, verdict: a.verdict, base: a.base.map(rd), against: a.against.map(rd), reducers: a.reducers.map(rd), steps: a.steps });
  return {
    ...p,
    theses: p.theses.map(t => ({ ...t, claims: t.claims.map(c => ({ ...c, axis: ax(c.axis) })), rescuerCaveat: t.rescuerCaveat && { seat: t.rescuerCaveat.seat, axis: ax(t.rescuerCaveat.axis) } })),
    modifiers: p.modifiers.map(m => ({ seat: m.seat, reading: rd(m.reading) })),
    course: p.course && { axis: ax(p.course.axis), rarest: p.course.rarest },
    contested: p.contested.map(ax),
    confront: p.confront.map(c => ({ element: c.element, readings: c.readings.map(rd) })),
    timings: p.timings.map(rd),
  };
}
