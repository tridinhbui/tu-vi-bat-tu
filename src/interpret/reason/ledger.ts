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

export const LEDGER_VERSION = 'ledger-1.1.0';
/** thuan / tro_ngai: one side, nothing in the way; co_dieu_kien: one side with a concrete, sourced or structural condition, or a book relation
 *  narrowing a strength; giam_nhe: a limit that a book relation makes lighter (never turned into a strength); chua_phan_xu: both sides stand
 *  and no book sentence adjudicates them (named, not merged); khong_ket_luan: a domain the report never judges good or bad (health: only the
 *  book readings are told); chua_du: nothing to conclude. hai_chieu is kept for older payloads only. */
export type Verdict = 'thuan' | 'co_dieu_kien' | 'hai_chieu' | 'tro_ngai' | 'chua_du' | 'giam_nhe' | 'chua_phan_xu' | 'hai_mat' | 'khong_ket_luan' | 'nghieng_ve';
/** the key a verdict's words are listed under (content/prose/luan.json ledger.verdict): a verdict with a base names its side */
export const verdictKey = (v: { verdict: Verdict; base: '+' | '-' | null }) => v.verdict === 'co_dieu_kien' || v.verdict === 'nghieng_ve' ? `${v.verdict}${v.base ?? ''}` : v.verdict;
export type Side = '+' | '-' | 'timing' | 'mixed';
export interface LedgerItem { ruleId: string; palace: string; concept: string; side: Side; seat: SeatRef; rarity: number; cites: string[];
  /** the stars and Hóa the reading stands on */
  stars: string[];
  /** the same, each with the palace it stands in (a sentence naming them says where each one is) */
  at: Array<{ name: string; palace: string }>;
  /** the star carrying Hóa Kỵ this strength rests on (the item is then 'mixed', never a plain positive) */
  kyCarrier?: string }
export interface LedgerStep { type: 'fact' | 'reading' | 'link' | 'precedence' | 'verdict'; palace?: string; element?: string; ruleId?: string; cite?: string;
  basis: 'sach' | 'he_thong' | 'tinh_toan'; note: string }
export interface Link { kind: 'timing' | 'book' | 'specific' | 'tier' | 'structure' | 'single' | 'mitigation' | 'unresolved' | 'weigh'; ruleId?: string; elements?: string[];
  /** book link: the side the book's own relation reduces ('-': a limit made lighter, '+': a strength narrowed) */
  reduces?: '+' | '-';
  /** book link: the reading the book's relation qualifies (the one it makes lighter or narrower) */
  target?: string }
export interface DomainVerdict {
  id: string; part?: string; label: string; verdict: Verdict; base: '+' | '-' | null;
  pos: LedgerItem[]; neg: LedgerItem[]; timing: LedgerItem[]; mixed: LedgerItem[];
  /** readings that only make a limit lighter (a book reducer of a negative item): never a side of their own */
  mitig: LedgerItem[];
  /** limiting / helping elements of the core palace(s), each with its palace */
  limits: Array<Element & { palace: string }>; supports: Array<Element & { palace: string }>;
  link?: Link; chain: LedgerStep[]; chapters: string[];
  /** the chapter that tells the domain in full when no earlier chapter voiced its readings */
  home?: string;
  /** the facets in the domain's order of importance (the first is its subject proper) */
  facets: string[];
  /** nghieng_ve: the weighing of the two sides (domains.json `weigh`, a labelled system convention) and why the heavier side weighs more */
  weigh?: Weighing;
}
/** why one side of a two-sided domain weighs more: its reading rests on a chính tinh against a minor star, on a bright star against a hãm
 *  one, on more independent stars, or stands in the domain's own palace against a palace of its tam phương */
export interface WeighReason { kind: 'tier' | 'dignity' | 'count' | 'core' | 'tuan_triet'; star?: string; other?: string; dignity?: string; palace?: string; n?: number }
export interface Weighing { pos: number; neg: number; heavy: LedgerItem; light: LedgerItem; why: WeighReason[] }
export interface Ledger { version: string; domains: DomainVerdict[]; byChapter: Record<string, DomainVerdict[]> }

/** domains.json `weigh`: the system's scale for two sides no book sentence adjudicates (owner decision 2026-10-23, labelled tổng hợp) */
interface WeighDef { tier: Record<string, number>; role: Record<string, number>; bright: number; ham: number; tuan_triet: number; per_extra: number; max_extra: number; margin: number }
interface DomainDef { label: string; home?: string;
  /** false: the domain gets no good / bad verdict at all (health, audit 2026-10-22); only its book readings are told */
  verdict?: boolean; palaces?: Record<string, string>; facets?: string[]; elements?: string[]; than?: boolean; cite?: string; chapters: string[];
  parts?: Record<string, { label: string; palaces: Record<string, string>; facets: string[]; elements?: string[] }> }
export interface DomainsFile { version: string; domains: Record<string, DomainDef>; weigh?: WeighDef }

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
    for (const part of parts) out.push({ ...decide(chart, k, cmap, live, evOf, id, part.pid, part.label, part.palaces, part.facets, part.elements, d.chapters, d.than && thanPal && part.palaces[thanPal] ? thanPal : undefined, d.verdict === false, file.weigh),
      ...(d.home ? { home: d.home } : {}), facets: part.facets });
  }
  const byChapter: Record<string, DomainVerdict[]> = {};
  for (const v of out) for (const c of v.chapters) (byChapter[c] ??= []).push(v);
  return { version: LEDGER_VERSION, domains: out, byChapter };
}

function decide(chart: ChartInput, k: Knowledge, cmap: Map<string, Concept>, live: Resolved[], evOf: (P: string) => PalaceEvidence, id: string, part: string | undefined,
  label: string, palaces: Record<string, string>, facets: string[], elements: string[] | undefined, chapters: string[], than?: string, noVerdict = false, W?: WeighDef): DomainVerdict {
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
        stars: [...new Set(r.atoms.filter(a => (a.kind === 'star' || a.kind === 'hoa') && a.palace !== null).map(a => a.name))],
        at: r.atoms.filter(a => (a.kind === 'star' || a.kind === 'hoa') && a.palace !== null).map(a => ({ name: a.name, palace: a.palace! })).filter((a, i, xs) => xs.findIndex(b => b.name === a.name && b.palace === a.palace) === i),
        ...(ky ? { kyCarrier: ky.name } : {}) });
    }
  }
  // one reading step per rule: a rule read at several palaces or for several concepts is listed once, with all of them
  for (const id of [...new Set(items.map(x => x.ruleId))]) {
    const xs = items.filter(x => x.ruleId === id);
    const ky = xs.find(x => x.kyCarrier)?.kyCarrier;
    chain.push({ type: 'reading', palace: [...new Set(xs.map(x => x.palace))].join(', '), ruleId: id, cite: xs[0].cites[0], basis: 'sach',
      note: `${[...new Set(xs.map(x => `${x.concept} (${x.side})`))].join('; ')}${ky ? `, ${ky} mang Hóa Kỵ` : ''}` });
  }
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

  const neg = items.filter(x => x.side === '-'), timing = items.filter(x => x.side === 'timing'), mixed = items.filter(x => x.side === 'mixed');
  // a strength that only exists as the book's reducer of a limit ("cường độ tật ách được giảm bớt") is a mitigation, not a side of its own:
  // it may make the limit lighter, never turn the domain into a strength (audit 2026-10-22)
  const reducerOf = (x: LedgerItem) => neg.find(n => live.some(r => r.ruleId === n.ruleId && r.by.some(b => b.basis === 'sach' && b.byRule === x.ruleId)));
  const mitig = items.filter(x => x.side === '+' && !!reducerOf(x));
  const pos = items.filter(x => x.side === '+' && !mitig.includes(x));
  const best = (xs: LedgerItem[]) => [...xs].sort((a, b) => a.seat.tier - b.seat.tier || b.rarity - a.rarity || (a.ruleId < b.ruleId ? -1 : 1))[0];
  const indep = (xs: LedgerItem[]) => new Set(xs.map(x => `${x.palace}|${x.seat.id}`)).size;
  const strong = (xs: LedgerItem[]) => xs.some(x => x.seat.tier <= 3) || indep(xs) >= 2;
  let verdict: Verdict, base: '+' | '-' | null = null, link: Link | undefined, weigh: Weighing | undefined;
  const slink = (): Link => ({ kind: 'structure', elements: limits.map(elementName) });
  // timing is its own dimension: it is told as such, never the condition of a quality verdict nor the link between two qualities
  if (noVerdict) {
    verdict = 'khong_ket_luan';
    if (pos.length && neg.length) link = { kind: 'unresolved' };
  } else if (!pos.length && !neg.length) {
    verdict = 'chua_du';
  } else if (!neg.length) {
    base = '+';
    if (limits.length || mixed.length) { verdict = 'co_dieu_kien'; link = slink(); }
    else if (!strong(pos)) { verdict = 'co_dieu_kien'; link = { kind: 'single', ruleId: best(pos).ruleId }; }
    else verdict = 'thuan';
  } else if (!pos.length) {
    base = '-';
    const m = mitig[0];
    if (m) { verdict = 'giam_nhe'; link = { kind: 'mitigation', ruleId: m.ruleId, reduces: '-', target: reducerOf(m)!.ruleId }; }
    else if (!strong(neg) && !limits.length) { verdict = 'co_dieu_kien'; link = { kind: 'single', ruleId: best(neg).ruleId }; }
    else verdict = 'tro_ngai';
  } else {
    const bp = best(pos), bn = best(neg);
    // only a book relation between the two sides adjudicates them: a strength the book narrows is the base, with that condition
    const bookRel = pos.flatMap(x => live.filter(r => r.ruleId === x.ruleId).flatMap(r => r.by.map(b => ({ b, x }))))
      .find(({ b }) => b.basis === 'sach' && neg.some(y => y.ruleId === b.byRule));
    if (bookRel) { verdict = 'co_dieu_kien'; base = '+'; link = { kind: 'book', ruleId: bookRel.b.byRule, reduces: '+', target: bookRel.x.ruleId }; }
    else {
      // two sides on different facets of the matter (money coming in vs money kept) both hold: 'hai_mat', said as such; two sides on the
      // same facet, or KG opposites, oppose head-on and stay 'chua_phan_xu' (owner review 2026-10-22: never merged into a conditional)
      const cp = cmap.get(bp.concept), cn = cmap.get(bn.concept);
      const oppose = !cp || !cn || cp.facet === cn.facet || cp.opp === cn.id || cn.opp === cp.id;
      verdict = oppose ? 'chua_phan_xu' : 'hai_mat';
      link = { kind: 'unresolved', ruleId: bp.ruleId, target: bn.ruleId };
      // two sides head-on: the system's scale (domains.json weigh) may find one clearly heavier; the verdict then says which and why, both
      // sides still named (owner decision 2026-10-23: a labelled tổng hợp, never a book adjudication). A close call stays chua_phan_xu.
      const w = oppose && W ? weighSides(chart, W, palaces, evOf, pos, neg) : undefined;
      if (w) { verdict = 'nghieng_ve'; base = w.pos > w.neg ? '+' : '-'; weigh = w; link = { kind: 'weigh', ruleId: w.heavy.ruleId, target: w.light.ruleId }; }
    }
  }
  if (link) chain.push({ type: link.kind === 'book' || link.kind === 'mitigation' ? 'link' : 'precedence', ruleId: link.ruleId, basis: link.kind === 'book' || link.kind === 'mitigation' ? 'sach' : 'he_thong',
    note: link.kind === 'structure' ? `yếu tố hạn chế: ${link.elements!.join(', ')}` : link.kind === 'weigh' ? `cân hai mặt: thuận ${weigh!.pos.toFixed(2)}, khó ${weigh!.neg.toFixed(2)} (${weigh!.why.map(x => x.kind).join(', ')})` : link.kind });
  chain.push({ type: 'verdict', basis: 'he_thong', note: `${verdict}${base ? ` (${base})` : ''}` });
  return { id: part ? `${id}.${part}` : id, ...(part ? { part } : {}), label, verdict, base, pos, neg, timing, mixed, mitig, limits, supports, ...(link ? { link } : {}), ...(weigh ? { weigh } : {}), chain, chapters, facets };
}

const BRIGHT = new Set(['miếu', 'vượng', 'đắc']);
/** The system's scale for two sides (domains.json `weigh`): each reading weighs by its seat's tier, its palace's role in the domain, the
 *  brightness of the star it rests on (a bright star's strength and a hãm star's limit count more) and Tuần/Triệt over a strength's palace; a
 *  side weighs as its heaviest reading plus a little for each further independent seat. Returns the weighing only when one side is heavier by
 *  the margin, with the reasons that make the difference (the first reason is the one the sentence names). */
function weighSides(chart: ChartInput, W: WeighDef, palaces: Record<string, string>, evOf: (P: string) => PalaceEvidence, pos: LedgerItem[], neg: LedgerItem[]): Weighing | undefined {
  const geo = new Map<string, Geo>();
  const dig = (x: LedgerItem) => { const st = x.seat.star, P = x.seat.palace ?? x.palace; if (!st || !P || (x.seat.kind !== 'major' && x.seat.kind !== 'hoa')) return undefined;
    const g = geo.get(P) ?? geo.set(P, new Geo(chart, P)).get(P)!; return g.dignity(st, P); };
  const tt = (x: LedgerItem) => evOf(x.palace).limit.some(l => l.kind === 'tuan' || l.kind === 'triet');
  const one = (x: LedgerItem, side: '+' | '-') => {
    let w = (W.tier[String(x.seat.tier)] ?? 0.4) * (W.role[palaces[x.palace]] ?? 0.7);
    const d = dig(x);
    if (d && BRIGHT.has(d)) w += side === '+' ? W.bright : -W.bright;
    // a hãm star carrying Hóa Lộc / Quyền / Khoa is helped out of part of its fall (the role evidence.ts gives it is 'mixed'): no hãm weight
    const helped = !!x.seat.star && Object.entries(chart.tu_hoa).some(([h, v]) => v.star === x.seat.star && h !== 'Hóa Kỵ');
    if (d === 'hãm' && !helped) w += side === '-' ? W.ham : -W.ham;
    if (side === '+' && tt(x)) w -= W.tuan_triet;
    return w;
  };
  const side = (xs: LedgerItem[], s: '+' | '-') => {
    const ws = xs.map(x => ({ x, w: one(x, s) })).sort((a, b) => b.w - a.w || (a.x.ruleId < b.x.ruleId ? -1 : 1));
    const n = new Set(xs.map(x => `${x.palace}|${x.seat.id}`)).size;
    return { top: ws[0], n, w: ws[0].w + Math.min(W.max_extra, W.per_extra * (n - 1)) };
  };
  const P = side(pos, '+'), N = side(neg, '-');
  if (Math.abs(P.w - N.w) < W.margin) return undefined;
  const [H, Lt, hs] = P.w > N.w ? [P, N, '+'] as const : [N, P, '-'] as const;
  const h = H.top.x, l = Lt.top.x, why: WeighReason[] = [];
  const dh = dig(h), dl = dig(l);
  if (h.seat.tier < l.seat.tier && h.seat.kind === 'major' && l.seat.kind !== 'major') why.push({ kind: 'tier', star: h.seat.star, other: l.seat.star ?? l.stars[0] });
  const helpedH = !!h.seat.star && Object.entries(chart.tu_hoa).some(([k, v]) => v.star === h.seat.star && k !== 'Hóa Kỵ');
  if (dh && (hs === '+' ? BRIGHT.has(dh) : dh === 'hãm' && !helpedH) && dh !== dl) why.push({ kind: 'dignity', star: h.seat.star, dignity: dh, palace: h.seat.palace ?? h.palace });
  if (palaces[h.palace] === 'core' && palaces[l.palace] !== 'core') why.push({ kind: 'core', palace: h.palace, other: l.palace });
  if (hs === '-' && tt(l)) why.push({ kind: 'tuan_triet', palace: l.palace });
  if (H.n > Lt.n) why.push({ kind: 'count', n: H.n });
  // a difference with no reason the reader can be told is not told as one
  if (!why.length) return undefined;
  return { pos: +P.w.toFixed(3), neg: +N.w.toFixed(3), heavy: h, light: l, why };
}

/** The ledger as plain JSON for the API and the evidence panel. */
export const ledgerView = (l: Ledger) => ({ version: l.version, domains: l.domains });
