// Domain ledger (plan quirky-tinkering-rabin step 3, S1): one verdict per life domain for the whole report, so that no two chapters conclude
// opposite things about the same matter. Each domain (engine/data/kg/domains.json, a labelled system convention) gathers the verified
// readings of its palaces on its facets and the structural elements of its core palace (reason/evidence.ts), and is adjudicated ONCE, in the
// order of reason/adjudicate.ts — never by summing scores:
//   (a) the book's own link: a timing reading (rel.timing, career.late, life.late_bloom …) ties the two sides to different times, or the
//       resolver applied a book relation between them → có điều kiện, the link told;
//   (b) specificity: a side whose evidence contains the other's and more is the narrower one and is the base;
//   (c) tier: the side resting on the more fundamental seat (reason/tiers.ts) is the base, the other its condition;
//   (d) otherwise hai chiều: both sides are told, neither is the conclusion.
// With one side only: a limiting element of the core palace (Hóa Kỵ, a sát tinh, Tuần/Triệt, a hãm chính tinh) or a lone minor star makes
// the verdict conditional; nothing in the way makes it thuận (or trở ngại for a limit). Every step goes into the evidence chain
// (fact → reading → link → verdict) with its rule, page and basis.
import type { ChartInput, Concept, Knowledge } from '../types.ts';
import type { Resolved } from '../kg/resolve.ts';
import { nesting } from '../kg/atoms.ts';
import { Geo, rarity, seatOf, type SeatRef } from './tiers.ts';
import { guardHolds } from './positions.ts';
import { palaceEvidence, TIMING_FACET, type Element, type PalaceEvidence } from './evidence.ts';

export const LEDGER_VERSION = 'ledger-1.0.0';
export type Verdict = 'thuan' | 'co_dieu_kien' | 'hai_chieu' | 'tro_ngai' | 'chua_du';
export type Side = '+' | '-' | 'timing' | 'mixed';
export interface LedgerItem { ruleId: string; palace: string; concept: string; side: Side; seat: SeatRef; rarity: number; cites: string[];
  /** the stars and Hóa the reading stands on */
  stars: string[];
  /** the star carrying Hóa Kỵ this strength rests on (the item is then 'mixed', never a plain positive) */
  kyCarrier?: string }
export interface LedgerStep { type: 'fact' | 'reading' | 'link' | 'precedence' | 'verdict'; palace?: string; element?: string; ruleId?: string; cite?: string;
  basis: 'sach' | 'he_thong' | 'tinh_toan'; note: string }
export interface Link { kind: 'timing' | 'book' | 'specific' | 'tier' | 'structure' | 'single'; ruleId?: string; elements?: string[];
  /** book link: the side the book's own relation reduces ('-': a limit made lighter, '+': a strength narrowed) */
  reduces?: '+' | '-';
  /** book link: the reading the book's relation qualifies (the one it makes lighter or narrower) */
  target?: string }
export interface DomainVerdict {
  id: string; part?: string; label: string; verdict: Verdict; base: '+' | '-' | null;
  pos: LedgerItem[]; neg: LedgerItem[]; timing: LedgerItem[]; mixed: LedgerItem[];
  /** limiting / helping elements of the core palace(s), each with its palace */
  limits: Array<Element & { palace: string }>; supports: Array<Element & { palace: string }>;
  link?: Link; chain: LedgerStep[]; chapters: string[];
  /** the chapter that tells the domain in full when no earlier chapter voiced its readings */
  home?: string;
  /** the facets in the domain's order of importance (the first is its subject proper) */
  facets: string[];
}
export interface Ledger { version: string; domains: DomainVerdict[]; byChapter: Record<string, DomainVerdict[]> }

interface DomainDef { label: string; home?: string; palaces?: Record<string, string>; facets?: string[]; elements?: string[]; than?: boolean; cite?: string; chapters: string[];
  parts?: Record<string, { label: string; palaces: Record<string, string>; facets: string[]; elements?: string[] }> }
export interface DomainsFile { version: string; domains: Record<string, DomainDef> }

const LIVE = (r: Resolved) => r.status !== 'voided' && r.status !== 'divergent';
const facetIn = (facet: string, fs: string[]) => fs.some(f => facet === f || facet.startsWith(f + '.'));
const ELEMENT_NAME: Record<string, string> = { tuan: 'Tuần', triet: 'Triệt', hoa_ky: 'Hóa Kỵ' };
/** the name an element is listed under in domains.json `elements` */
export const elementName = (e: Element) => ELEMENT_NAME[e.kind] ?? e.star ?? e.hoa ?? e.id;

/** The verified readings the ledger may use: live, past the position guards of their own palace. */
function placed(chart: ChartInput, k: Knowledge, resolved: Resolved[]): Resolved[] {
  const guards = new Map((k.kg?.positionGuards ?? []).map(x => [x.ruleId, x]));
  const rmap = new Map(k.rules.map(r => [r.id, r]));
  return resolved.filter(r => LIVE(r) && rmap.get(r.ruleId)?.reviewStatus === 'verified' && !r.additive).filter(r => {
    const gd = guards.get(r.ruleId);
    return !gd || guardHolds(gd, r.atoms, chart.palaces, { here: r.palace ?? 'Mệnh', tuHoa: chart.tu_hoa });
  });
}

export function buildLedger(chart: ChartInput, k: Knowledge, resolved: Resolved[]): Ledger {
  const file = k.kg?.domains as DomainsFile | undefined;
  const out: DomainVerdict[] = [];
  if (!file) return { version: LEDGER_VERSION, domains: [], byChapter: {} };
  const cmap = new Map<string, Concept>(k.concepts.concepts.map(c => [c.id, c]));
  const live = placed(chart, k, resolved);
  const ev = new Map<string, PalaceEvidence>();
  const evOf = (P: string) => ev.get(P) ?? ev.set(P, palaceEvidence(chart, k, P, { resolved: live })).get(P)!;
  const thanPal = chart.palaces.find(p => p.is_than)?.name;
  for (const [id, d] of Object.entries(file.domains)) {
    const parts = d.parts ? Object.entries(d.parts).map(([pid, p]) => ({ pid, ...p })) : [{ pid: undefined as string | undefined, label: d.label, palaces: d.palaces!, facets: d.facets!, elements: d.elements }];
    for (const part of parts) out.push({ ...decide(chart, k, cmap, live, evOf, id, part.pid, part.label, part.palaces, part.facets, part.elements, d.chapters, d.than && thanPal && part.palaces[thanPal] ? thanPal : undefined),
      ...(d.home ? { home: d.home } : {}), facets: part.facets });
  }
  const byChapter: Record<string, DomainVerdict[]> = {};
  for (const v of out) for (const c of v.chapters) (byChapter[c] ??= []).push(v);
  return { version: LEDGER_VERSION, domains: out, byChapter };
}

function decide(chart: ChartInput, k: Knowledge, cmap: Map<string, Concept>, live: Resolved[], evOf: (P: string) => PalaceEvidence, id: string, part: string | undefined,
  label: string, palaces: Record<string, string>, facets: string[], elements: string[] | undefined, chapters: string[], than?: string): DomainVerdict {
  const chain: LedgerStep[] = [];
  const items: LedgerItem[] = [];
  const core = Object.entries(palaces).filter(([, r]) => r === 'core').map(([p]) => p);
  for (const P of Object.keys(palaces)) {
    const g = new Geo(chart, P), e = evOf(P), kyStars = new Set(e.mixed.filter(x => x.kind === 'ky_carrier').map(x => x.star!));
    for (const r of live) {
      if (r.subject !== `palace:${P}`) continue;
      const c = cmap.get(r.concept);
      if (!c || !facetIn(c.facet, facets)) continue;
      const { seat } = seatOf(r, g);
      let side: Side = TIMING_FACET(c.facet) ? 'timing' : c.pol === '~' ? 'timing' : (c.pol === '+') === (r.stance === 'affirms') ? '+' : '-';
      if (c.pol === '~' && !TIMING_FACET(c.facet)) continue;           // a neutral concept (a path, a style) has no side
      const ky = side === '+' ? r.atoms.find(a => a.kind === 'star' && a.palace === P && kyStars.has(a.name)) : undefined;
      if (ky) side = 'mixed';
      if (items.some(x => x.ruleId === r.ruleId && x.palace === P && x.concept === r.concept)) continue;
      items.push({ ruleId: r.ruleId, palace: P, concept: r.concept, side, seat, rarity: rarity(k, r.ruleId, P), cites: r.cites,
        stars: [...new Set(r.atoms.filter(a => (a.kind === 'star' || a.kind === 'hoa') && a.palace !== null).map(a => a.name))], ...(ky ? { kyCarrier: ky.name } : {}) });
    }
  }
  for (const x of items) chain.push({ type: 'reading', palace: x.palace, ruleId: x.ruleId, cite: x.cites[0], basis: 'sach', note: `${x.concept} (${x.side})${x.kyCarrier ? `, ${x.kyCarrier} mang Hóa Kỵ` : ''}` });
  // the structural elements of the core palace(s): those the domain names (elements), or every limit / Kỵ-carrier / bright chính tinh
  const limits: DomainVerdict['limits'] = [], supports: DomainVerdict['supports'] = [];
  for (const P of core) {
    const e = evOf(P);
    // every limiting element of the core palace is gathered (a sát tinh, Hóa Kỵ, Tuần/Triệt, a hãm chính tinh, a star carrying Kỵ); `elements`
    // adds the part's own helping / limiting stars below
    for (const x of [...e.limit, ...e.mixed.filter(m => m.kind === 'ky_carrier')]) limits.push({ ...x, palace: P });
    for (const x of e.support.filter(s => s.kind === 'major_bright' || (elements ?? []).includes(elementName(s)))) supports.push({ ...x, palace: P });
    // the part's named elements may stand among the palace's helping stars (Lộc Tồn, Thiên Phủ for tích lũy)
    for (const x of e.majors.filter(m => (elements ?? []).includes(m.star) && !supports.some(s => s.star === m.star))) supports.push({ id: `major:${x.star}`, kind: 'major_bright', star: x.star, dignity: x.dignity, borrowed: x.borrowed, role: 'support', palace: P });
    for (const x of e.stars.filter(s => s.where === 'self' && (elements ?? []).includes(s.star) && s.role === 'limit' && !limits.some(l => l.star === s.star))) limits.push({ id: `${x.group}:${x.star}`, kind: 'sat', star: x.star, dignity: x.dignity, role: 'limit', palace: P });
  }
  for (const l of limits) chain.push({ type: 'fact', palace: l.palace, element: l.id, basis: 'tinh_toan', note: `${elementName(l)}${l.star && l.kind !== 'hoa_ky' && l.kind !== 'tuan' && l.kind !== 'triet' && l.dignity ? ` (${l.dignity})` : ''} ở ${l.palace}` });
  for (const s of supports) chain.push({ type: 'fact', palace: s.palace, element: s.id, basis: 'tinh_toan', note: `${elementName(s)}${s.dignity ? ` (${s.dignity})` : ''}${s.borrowed ? ' mượn' : ''} ở ${s.palace}` });
  if (than) chain.push({ type: 'fact', palace: than, basis: 'tinh_toan', note: `Thân cư ${than}` });

  const pos = items.filter(x => x.side === '+'), neg = items.filter(x => x.side === '-'), timing = items.filter(x => x.side === 'timing'), mixed = items.filter(x => x.side === 'mixed');
  const best = (xs: LedgerItem[]) => [...xs].sort((a, b) => a.seat.tier - b.seat.tier || b.rarity - a.rarity || (a.ruleId < b.ruleId ? -1 : 1))[0];
  const indep = (xs: LedgerItem[]) => new Set(xs.map(x => `${x.palace}|${x.seat.id}`)).size;
  const strong = (xs: LedgerItem[]) => xs.some(x => x.seat.tier <= 3) || indep(xs) >= 2;
  let verdict: Verdict, base: '+' | '-' | null = null, link: Link | undefined;
  const tlink = (): Link => ({ kind: 'timing', ruleId: best(timing).ruleId });
  const slink = (): Link => ({ kind: 'structure', elements: limits.map(elementName) });
  if (!pos.length && !neg.length) {
    if (timing.length) { verdict = 'co_dieu_kien'; link = tlink(); }
    else verdict = 'chua_du';
  } else if (!neg.length) {
    base = '+';
    if (timing.length) { verdict = 'co_dieu_kien'; link = tlink(); }
    else if (limits.length || mixed.length) { verdict = 'co_dieu_kien'; link = slink(); }
    else if (!strong(pos)) { verdict = 'co_dieu_kien'; link = { kind: 'single', ruleId: best(pos).ruleId }; }
    else verdict = 'thuan';
  } else if (!pos.length) {
    base = '-';
    if (!strong(neg) && !limits.length) { verdict = 'co_dieu_kien'; link = { kind: 'single', ruleId: best(neg).ruleId }; }
    else if (timing.length) { verdict = 'co_dieu_kien'; link = tlink(); }
    else verdict = 'tro_ngai';
  } else {
    const bp = best(pos), bn = best(neg);
    // a book relation between the two sides: the reading it qualifies is the reduced side
    const bookRel = [...pos.map(x => ['+', x] as const), ...neg.map(x => ['-', x] as const)].flatMap(([sd, x]) => live.filter(r => r.ruleId === x.ruleId).flatMap(r => r.by.map(b => ({ b, sd, x }))))
      .find(({ b }) => b.basis === 'sach' && [...pos, ...neg].some(y => y.ruleId === b.byRule));
    const sig = (x: LedgerItem) => new Set(live.filter(r => r.ruleId === x.ruleId && r.subject === `palace:${x.palace}`).flatMap(r => [...r.sig]));
    const n = nesting(sig(bp), sig(bn));
    if (timing.length) { verdict = 'co_dieu_kien'; link = tlink(); base = bp.seat.tier <= bn.seat.tier ? '+' : '-'; }
    else if (bookRel) { verdict = 'co_dieu_kien'; link = { kind: 'book', ruleId: bookRel.b.byRule, reduces: bookRel.sd, target: bookRel.x.ruleId }; base = bookRel.sd === '-' ? '+' : bp.seat.tier <= bn.seat.tier ? '+' : '-'; }
    else if (n === 'narrower' || n === 'broader') { base = n === 'narrower' ? '+' : '-'; verdict = base === '+' ? 'co_dieu_kien' : 'tro_ngai'; link = { kind: 'specific', ruleId: (base === '+' ? bp : bn).ruleId }; }
    else if (bp.seat.tier !== bn.seat.tier) { base = bp.seat.tier < bn.seat.tier ? '+' : '-'; verdict = base === '+' ? 'co_dieu_kien' : 'tro_ngai'; link = { kind: 'tier', ruleId: (base === '+' ? bp : bn).ruleId }; }
    else verdict = 'hai_chieu';
  }
  if (link) chain.push({ type: link.kind === 'timing' || link.kind === 'book' ? 'link' : 'precedence', ruleId: link.ruleId, basis: link.kind === 'timing' || link.kind === 'book' ? 'sach' : 'he_thong',
    note: link.kind === 'structure' ? `yếu tố hạn chế: ${link.elements!.join(', ')}` : link.kind });
  chain.push({ type: 'verdict', basis: 'he_thong', note: `${verdict}${base ? ` (${base})` : ''}` });
  return { id: part ? `${id}.${part}` : id, ...(part ? { part } : {}), label, verdict, base, pos, neg, timing, mixed, limits, supports, ...(link ? { link } : {}), chain, chapters, facets };
}

/** The ledger as plain JSON for the API and the evidence panel. */
export const ledgerView = (l: Ledger) => ({ version: l.version, domains: l.domains });
