// Reader prose by chapter (prose plan P3 for Mệnh, P5 for the other palaces): chart facts -> rules -> concepts -> resolution (relations,
// page-checked qualifiers) -> selection -> schema -> sentences. No language model; deterministic for a given chart, knowledge version and
// prose-library version. Cards that are not 'approved' are used only with allowDraft (TVBT_PROSE_DRAFT on the Worker); without any
// usable card a chapter is empty, never padded.
// A report is a chain (PROSE_ORDER): chapters share the variant memory and the concepts already said, so no idea and no phrasing is
// told twice; a single chapter is computed by running the chain up to it.
import { run } from '../engine.ts';
import { lift } from '../kg/lift.ts';
import { applyQualifiers, resolve, type KgRelation, type Resolved, type Tension } from '../kg/resolve.ts';
import type { ChartInput, Concept, Knowledge } from '../types.ts';
import { chooseSchema, presentMoves } from './discourse.ts';
import { Micro, fnv, lowerFirst } from './micro.ts';
import { Realizer, type ProseParagraph, type ProseSentence } from './realize.ts';
import { IDENTITY, select, type Selection } from './select.ts';
import { validateProse, type ProseIssue, type ProseMetrics } from './validate.ts';
import type { Move } from './types.ts';
import { bookStarsOf, para, readPalace } from './deep.ts';

export const PROSE_VERSION = 'prose-0.4.0';
export type ProseChapterId = 'menh' | 'cong_danh' | 'tai_bach' | 'thien_di' | 'phu_the' | 'phuc_duc' | 'dien_trach' | 'no_boc'
  | 'tu_tuc' | 'huynh_de' | 'phu_mau' | 'tat_ach';
interface ProseSpec { palace: string; pool: (c?: Concept) => boolean; borrowFrom: string[];
  /** what may be taken from the borrowFrom palaces (default: pool) — Phu Thê must not take the person's own traits as the partner's */
  borrowPool?: (c?: Concept) => boolean; chart: boolean; extra: string[]; degree: boolean;
  /** Phu Thê, Nô Bộc: readings not about the bond describe the other people (frames.other[palace]) */
  bond?: (c?: Concept) => boolean }
const facet = (...pre: string[]) => (c?: Concept) => !!c && pre.some(p => c.facet === p || c.facet.startsWith(p + '.'));
export const PROSE_SPECS: Record<ProseChapterId, ProseSpec> = {
  menh: { palace: 'Mệnh', pool: IDENTITY, borrowFrom: [], chart: true, extra: ['life.transient', 'life.mobility', 'life.late_bloom'], degree: true },
  cong_danh: { palace: 'Quan Lộc', pool: facet('career'), borrowFrom: ['Mệnh'], chart: false, extra: [], degree: false },
  tai_bach: { palace: 'Tài Bạch', pool: facet('finance'), borrowFrom: ['Mệnh'], chart: false, extra: [], degree: false },
  // Thiên Di: everything that happens away from home — luck, money, conflict, temper and state of mind abroad
  thien_di: { palace: 'Thiên Di', pool: facet('life', 'finance', 'identity', 'inner', 'career'), borrowPool: facet('life.mobility', 'life.outside'),
    borrowFrom: ['Mệnh'], chart: false, extra: [], degree: false },
  // Phu Thê: the bond (relationships.*) is the person's; any other trait describes the partner
  phu_the: { palace: 'Phu Thê', pool: facet('relationships.marriage', 'relationships.partner', 'relationships.timing', 'identity', 'career', 'finance', 'wellbeing', 'life.course'),
    borrowPool: facet('relationships.marriage', 'relationships.partner', 'relationships.timing'), borrowFrom: ['Mệnh'], chart: false, extra: [], degree: false,
    bond: facet('relationships', 'life.course') },
  phuc_duc: { palace: 'Phúc Đức', pool: facet('inner', 'life', 'wellbeing', 'relationships.family', 'finance', 'career.support', 'identity'),
    borrowPool: facet('inner', 'life.spirituality'), borrowFrom: ['Mệnh'], chart: false, extra: [], degree: false },
  dien_trach: { palace: 'Điền Trạch', pool: facet('finance', 'life', 'relationships.family'), borrowPool: facet('finance.property'), borrowFrom: ['Mệnh', 'Tài Bạch'],
    chart: false, extra: [], degree: false },
  // Nô Bộc: allies, help and what they cost are the person's; character traits describe the friends and subordinates
  no_boc: { palace: 'Nô Bộc', pool: facet('relationships.allies', 'career', 'identity', 'finance', 'life.course'), borrowPool: facet('relationships.allies', 'career.support'),
    borrowFrom: ['Mệnh'], chart: false, extra: [], degree: false, bond: facet('relationships.allies', 'career', 'finance', 'life.course') },
  // Tử Tức, Huynh Đệ, Phụ Mẫu: the family bond (kin.*, family) is the person's; status, wealth, character describe the children,
  // the siblings, the parents (frames.other[palace])
  tu_tuc: { palace: 'Tử Tức', pool: facet('relationships.kin', 'relationships.family', 'relationships.allies', 'career', 'finance', 'identity'), borrowFrom: [],
    chart: false, extra: [], degree: false, bond: facet('relationships') },
  huynh_de: { palace: 'Huynh Đệ', pool: facet('relationships.kin', 'relationships.family', 'career', 'finance', 'identity'), borrowFrom: [],
    chart: false, extra: [], degree: false, bond: facet('relationships') },
  phu_mau: { palace: 'Phụ Mẫu', pool: facet('relationships', 'career', 'finance', 'identity', 'inner', 'life.course'), borrowPool: facet('relationships.family'),
    borrowFrom: ['Mệnh'], chart: false, extra: [], degree: false, bond: facet('relationships') },
  tat_ach: { palace: 'Tật Ách', pool: facet('wellbeing', 'life', 'inner'), borrowPool: facet('wellbeing'), borrowFrom: ['Mệnh'], chart: false, extra: [], degree: false },
};
export interface Advice { strengths: string[]; actions: string[]; basis: 'loi_khuyen' }
/** What a chapter's voiced concepts suggest doing: the card's `value` for a positive trait, its `mature` clause for a limiting one. Only concepts
 *  the text actually said (basis sach) are used, so the advice adds no claim; it is labelled as the system's suggestion, not the book's word. */
export function adviceOf(paragraphs: ProseParagraph[], k: Knowledge, allowDraft: boolean, seed: string): Advice {
  const ok = (st: string) => st === 'approved' || (allowDraft && st !== 'retired');
  const cards = new Map(k.prose!.concepts.filter(c => ok(c.status)).map(c => [c.id, c]));
  const pol = new Map(k.concepts.concepts.map(c => [c.id, c.pol]));
  const said = [...new Set(paragraphs.flatMap(p => p.sentences.filter(s => s.trace.basis === 'sach').flatMap(s => s.trace.concepts)))];
  const pick = (xs: string[] | undefined, id: string) => xs?.length ? xs[fnv(`${seed}|adv|${id}`) % xs.length] : undefined;
  const strengths = said.filter(c => pol.get(c) === '+').map(c => pick(cards.get(c)?.value, c)).filter((x): x is string => !!x).slice(0, 3);
  const actions = said.filter(c => pol.get(c) === '-').map(c => pick(cards.get(c)?.mature, c)).filter((x): x is string => !!x).slice(0, 3);
  return { strengths: [...new Set(strengths)], actions: [...new Set(actions)], basis: 'loi_khuyen' };
}
export const PROSE_ORDER: ProseChapterId[] = ['menh', 'cong_danh', 'tai_bach', 'thien_di', 'phu_the', 'phuc_duc', 'dien_trach', 'no_boc', 'tu_tuc', 'huynh_de', 'phu_mau', 'tat_ach'];
export interface ProseChapter {
  engine: string; kbVersion: string; chapter: ProseChapterId; palace: string; schema: string; order: Move[];
  /** draft cards were allowed and the library still holds drafts: the reader must be told the wording is unreviewed */
  draft: boolean;
  paragraphs: ProseParagraph[]; text: string; issues: ProseIssue[]; metrics: ProseMetrics; pass: boolean;
  /** action suggestions drawn from the cards of the concepts this chapter voices (a strength to lean on, a habit to watch); system wording */
  advice: Advice;
  evidence: { resolved: Array<Pick<Resolved, 'ruleId' | 'concept' | 'stance' | 'status' | 'by' | 'cites'>>; tensions: Tension[]; unused: string[];
    /** every rule a sentence traces to, with its book paraphrase and pages, for the evidence panel */
    rules: Record<string, { reading: string; cites: string[]; verified: boolean }>; concepts: Record<string, string>;
    /** two schools disagree on this chart: neither reading is in the text, both are shown here with their pages */
    divergences: Array<{ relation: string; cite?: string; note?: string; rules: Array<{ id: string; reading: string; cites: string[] }> }>;
    /** luận cung: the domain verdicts of the report-wide ledger this chapter concludes on (reason/ledger.ts), with their evidence chains */
    ledger?: Array<{ id: string; label: string; verdict: string; base: '+' | '-' | null; link: unknown; chain: unknown[]; limits: Array<{ id: string; palace: string }> }>;
    /** verified readings of the palace the chapter does not tell, with the reason (prose/luan.ts) */
    untold?: Array<{ ruleId: string; reason: string }> };
}

/** Starts with a proper name (a star, Tuần/Triệt, a Hóa): its capital stays when the sentence is woven into the previous one. */
const properStart = (t: string) => /^(\p{Lu}\p{Ll}*\s\p{Lu})|^(Tuần|Triệt)\b/u.test(t);
const words = (t: string) => t.split(/\s+/).length;
/** A sentence may join the one before it with a semicolon: an elaboration after the anchor, a timing or course remark, or the turn
 *  right after the anchor; both factual (editorial sentences are never woven), and the result at most 48 words. */
const canWeave = (prev: ProseSentence, s: ProseSentence) =>
  ((s.trace.move === 'ELABORATE' && (prev.trace.move === 'ANCHOR' || prev.trace.move === 'BORROW')) || s.trace.move === 'TIMING' || s.trace.move === 'EXTRA'
    || (s.trace.move === 'TURN' && prev.trace.move === 'ANCHOR')) && !prev.trace.woven && prev.trace.basis === 'sach' && s.trace.basis === 'sach' && words(prev.text) + words(s.text) <= 48;
const LOOSE_SECOND = new Set(['ELABORATE', 'TENSION', 'TIMING', 'EXTRA', 'SATELLITE', 'VIA', 'DEGREE']);
/** a contrast already in the first half and another opening the second reads 'nhưng …; nhưng …': never woven loosely */
const CONTRAST = /(^|\s)(nhưng|song|tuy|dù|dẫu|có điều|ngược lại|chỉ có điều|thế nhưng)(\s|,)/i;
const canWeaveLoose = (prev: ProseSentence, s: ProseSentence) => canWeave(prev, s) || (LOOSE_SECOND.has(s.trace.move) && !prev.trace.woven
  && !(CONTRAST.test(prev.text) && CONTRAST.test(s.text.split(/\s+/).slice(0, 3).join(' ')))
  && prev.trace.basis === 'sach' && s.trace.basis === 'sach' && words(prev.text) + words(s.text) <= 48);
function join2(prev: ProseSentence, s: ProseSentence): ProseSentence {
  const second = properStart(s.text) ? s.text : lowerFirst(s.text);
  return { text: `${prev.text.replace(/\.$/, '')}; ${second}`, trace: { ...prev.trace, concepts: [...new Set([...prev.trace.concepts, ...s.trace.concepts])],
    rules: [...new Set([...prev.trace.rules, ...s.trace.rules])].sort(), cites: [...new Set([...prev.trace.cites, ...s.trace.cites])].sort(), woven: [...(prev.trace.woven ?? []), s.trace.move] } };
}
const spread = (xs: number[]) => { const m = xs.reduce((a, b) => a + b, 0) / xs.length; return Math.sqrt(xs.reduce((a, b) => a + (b - m) ** 2, 0) / xs.length); };
/** Rhythm (prose plan §6: edited prose varies sentence length — the reference paragraph has sd 7.1 words). First a seeded pass weaves
 *  about two in three eligible pairs; then, across the whole chapter, while the spread of sentence lengths is under 6 words, the
 *  eligible pair whose weaving raises it most is woven. Deterministic: same chart, same text. */
function rhythm(paras: Array<[ProseParagraph['role'], ProseSentence[]]>, seed: string): Array<[ProseParagraph['role'], ProseSentence[]]> {
  // the seeded pass, with a lower cap on a woven sentence's length when the chapter would otherwise average over 35 words a sentence
  const pass = (cap: number) => paras.map(([role, xs]) => {
    const out: ProseSentence[] = [];
    for (const s of xs) { const prev = out[out.length - 1]; if (prev && canWeave(prev, s) && words(prev.text) + words(s.text) <= cap && fnv(`${seed}|weave|${role}|${out.length}`) % 3 !== 0) out[out.length - 1] = join2(prev, s); else out.push(s); }
    return [role, out] as [ProseParagraph['role'], ProseSentence[]];
  });
  const avg = (q: Array<[ProseParagraph['role'], ProseSentence[]]>) => { const l = q.flatMap(([, xs]) => xs.map(s => words(s.text))); return l.reduce((a, b) => a + b, 0) / l.length; };
  let ps = pass(48);
  for (const cap of [40, 34]) if (avg(ps) > 35) ps = pass(cap);
  const lens = () => ps.flatMap(([, xs]) => xs.map(s => words(s.text)));
  // repair: while the chapter misses the rhythm band (mean 18-35 words, spread >= 6), weave the pair of adjacent factual sentences that
  // brings it closest; the first rounds use the narrow rule above, then any two factual sentences of one paragraph (never a rescue,
  // a closing or an anchor as the second half), so short chapters get one long sentence among short ones
  const miss = (xs: number[]) => { const m = xs.reduce((a, b) => a + b, 0) / xs.length, sd = spread(xs); return Math.max(0, 18 - m) + Math.max(0, m - 35) + Math.max(0, 6 - sd); };
  for (const rule of [canWeave, canWeaveLoose]) for (let guard = 0; guard < 6 && miss(lens()) > 0; guard++) {
    let best = null as [number, number, number] | null;
    ps.forEach(([, xs], pi) => xs.forEach((s, i) => {
      if (!i || !rule(xs[i - 1], s)) return;
      const trial = lens(), off = ps.slice(0, pi).reduce((a, [, ys]) => a + ys.length, 0) + i;
      trial.splice(off - 1, 2, trial[off - 1] + trial[off]);
      const v = miss(trial);
      if (!best || v < best[2]) best = [pi, i, v];
    }));
    const pick = best as [number, number, number] | null;
    if (!pick || pick[2] >= miss(lens())) break;
    const [pi, i] = pick, xs = ps[pi][1];
    xs.splice(i - 1, 2, join2(xs[i - 1], xs[i]));
  }
  return ps;
}

export function seedOf(chart: ChartInput): string {
  return `${chart.birth_year}|${chart.year_gz}|${chart.palaces.map(p => p.stars.join(',')).join('/')}`;
}

/** Every chapter of the chain up to `until` (inclusive), sharing rule inference, the variant memory and the concepts already said. */
/** `deep`: add the structure, common-meaning and balance layers around the book readings (prose/deep.ts; draft library, so with allowDraft
 *  only). The route turns it on; the book-layer tests leave it off so their goldens and thresholds measure the book readings alone. */
/** One rule run, lifted and resolved with the page-checked qualifiers applied: what every chapter of a report reads (proseReport and the
 *  luận cung chain share it, so a report infers once). */
export interface Inference { findings: ReturnType<typeof run>['findings']; labelled: ReturnType<typeof lift>['labelled']; resolved: Resolved[]; tensions: Tension[] }
export function infer(chart: ChartInput, k: Knowledge): Inference {
  const findings = run(k.rules, k.sources, chart.base).findings;
  const { assertions, labelled } = lift(findings, k, chart.base);
  const { resolved, tensions } = resolve(assertions, k);
  applyQualifiers(resolved, k, chart.base);
  return { findings, labelled, resolved, tensions };
}
export function proseReport(chart: ChartInput, k: Knowledge, opts: { allowDraft?: boolean; until?: ProseChapterId; deep?: boolean; pre?: Inference } = {}): ProseChapter[] {
  const { findings, resolved, tensions } = opts.pre ?? infer(chart, k);
  const fired = new Set(findings.map(f => `${f.ruleId}|${f.subject}`));
  const seed = seedOf(chart);
  const micro = new Micro(seed, k.prose!.connectives, k.prose!.frames);
  const said = new Set<string>(), out: ProseChapter[] = [];
  for (const id of PROSE_ORDER) {
    const ch = chapterOf(chart, k, id, resolved, tensions, micro, said, !!opts.allowDraft, seed, fired);
    ch.paragraphs.forEach(p => p.sentences.forEach(s => (s.trace.keys ?? []).forEach(c => said.add(c))));
    out.push(opts.allowDraft && opts.deep ? deepen(ch, chart, k, micro, resolved) : ch);
    if (id === (opts.until ?? PROSE_ORDER[PROSE_ORDER.length - 1])) break;
  }
  return out;
}
/** The chapter with its structure paragraph first, then the book readings, then the common meanings and the balance (prose/deep.ts).
 *  Draft library only: the structure frames and the cards are unreviewed. */
function deepen(ch: ProseChapter, chart: ChartInput, k: Knowledge, micro: Micro, resolved: Resolved[]): ProseChapter {
  const pal = chart.palaces.find(p => p.name === ch.palace)!;
  const oppName = (chart.base[`palace:${ch.palace}`]?.['palace.rel_names'] as Record<string, string> | undefined)?.opp;
  const r = readPalace(chart, k, ch.palace, micro, { key: 'natal', bookStars: bookStarsOf(ch.paragraphs, k, pal, chart.palaces.find(p => p.name === oppName)) });
  const paragraphs = [...para('structure', r.structure), ...ch.paragraphs, ...para('colour', r.colour), ...para('balance', r.balance)];
  const { issues, metrics } = validateProse(paragraphs, resolved.filter(x => ch.evidence.resolved.some(e => e.ruleId === x.ruleId)));
  return { ...ch, paragraphs, text: paragraphs.map(p => p.text).join('\n\n'), issues, metrics, pass: !issues.some(i => i.level === 'error') };
}
export function proseChapter(chart: ChartInput, k: Knowledge, id: ProseChapterId, opts: { allowDraft?: boolean; deep?: boolean } = {}): ProseChapter {
  return proseReport(chart, k, { ...opts, until: id }).at(-1)!;
}

function chapterOf(chart: ChartInput, k: Knowledge, id: ProseChapterId, resolvedAll: Resolved[], tensionsAll: Tension[], micro: Micro, said: Set<string>,
  allowDraft: boolean, seed: string, fired: Set<string>): ProseChapter {
  const spec = PROSE_SPECS[id];
  const pal = chart.palaces.find(p => p.name === spec.palace)!;
  const oppName = (chart.base[`palace:${spec.palace}`]?.['palace.rel_names'] as Record<string, string> | undefined)?.opp;
  const opp = chart.palaces.find(p => p.name === oppName);
  const subjects = new Set([`palace:${spec.palace}`, ...(spec.chart ? ['chart'] : []), ...spec.borrowFrom.map(b => `palace:${b}`)]);
  const resolved = resolvedAll.filter(r => subjects.has(r.subject));
  const keys = new Set(resolved.map(r => r.key)), tensions = tensionsAll.filter(t => keys.has(t.a) && keys.has(t.b));
  const sel: Selection = select(resolved, k, { palace: pal, opp, pool: spec.pool, borrowPool: spec.borrowPool, borrowFrom: spec.borrowFrom, chart: spec.chart, exclude: said, extra: spec.extra, degree: spec.degree });
  const other = spec.bond ? k.prose!.frames.other?.[spec.palace] : undefined;
  const R = new Realizer(k, sel, micro, allowDraft, other ? { other, bond: spec.bond } : {});

  // paragraph 1: the schema's moves
  const present = presentMoves(sel);
  const cseed = id === 'menh' ? seed : `${seed}|${id}`;          // Mệnh keeps the seed it had before chapters were added
  const { schema, order } = chooseSchema(k.prose!.schemas, present, cseed);
  const p1: ProseSentence[] = [], placed = new Set<Move>();
  const saidIn = (xs: ProseSentence[]) => new Set(xs.flatMap(s => s.trace.concepts));
  for (let i = 0; i < order.length; i++) {
    const m = order[i];
    let s: ProseSentence | null = null;
    if (m === 'ANCHOR' || m === 'BORROW') s = R.anchor();
    else if (m === 'ELABORATE') s = R.elaborate();
    else if (m === 'TURN') s = R.turn();
    else if (m === 'RESCUE') s = R.rescue();
    else if (m === 'TENSION') s = R.tension();
    else if (m === 'TIMING') s = R.timing();
    else if (m === 'SATELLITE') s = R.satellite(sel.satellites, 'sat1');
    else if (m === 'VALUE' || m === 'TRANSFORM') {
      const both = m === 'VALUE' ? order.slice(i + 1).includes('TRANSFORM') : order.slice(i + 1).includes('VALUE');
      s = R.close(m === 'VALUE' || both, m === 'TRANSFORM' || both, saidIn(p1));
      if (both) { placed.add('VALUE'); placed.add('TRANSFORM'); i = order.length; }
    }
    if (s) { p1.push(s); s.trace.schema = schema.id; }
    placed.add(m);
  }

  // paragraph 2: what the schema did not place, more traits, the remaining limit
  const p2: ProseSentence[] = [];
  const push = (s: ProseSentence | null) => { if (s) p2.push(s); };
  if (present.has('TENSION') && !placed.has('TENSION')) push(R.tension());
  if (present.has('ELABORATE') && !placed.has('ELABORATE')) push(R.elaborate());
  const sats = sel.satellites.filter(p => !R.saidConcepts().has(p.concept));         // what paragraph 1 actually voiced, not its first two
  push(R.satellite(sats, 'sat2', sel.satelliteNeg));
  if (present.has('TIMING') && !placed.has('TIMING')) push(R.timing());
  push(R.via(sel.via));

  // paragraph 3: the độ số balance and the course of life
  const p3: ProseSentence[] = [];
  const d = R.degree();
  if (d) p3.push(d);
  sel.extra.forEach((x, i) => { const s = R.course(x, i); if (s) p3.push(s); });

  const paragraphs: ProseParagraph[] = rhythm(([['core', p1], ['support', p2], ['course', p3]] as Array<[ProseParagraph['role'], ProseSentence[]]>).filter(([, xs]) => xs.length), cseed)
    .map(([role, xs]) => ({ role, sentences: xs, text: xs.map(s => s.text).join(' ') }));
  const { issues, metrics } = validateProse(paragraphs, resolved);
  const rmap = new Map(k.rules.map(r => [r.id, r]));
  const reading = (id: string) => { const r = rmap.get(id)!; return (r.reading ?? k.claims[r.consequences[0]?.claim ?? ''] ?? '').replace(/^(khuynh hướng|hạn chế:)\s*/, ''); };
  const relById = new Map(((k.kg?.relations ?? []) as KgRelation[]).map(r => [r.id, r]));
  // from the fired findings, whatever their review status: a draft reading of one school is still worth showing beside the other's rebuttal
  const divergences = [...relById.values()].filter(r => r.type === 'school_divergence').flatMap(rel => {
    const subj = [...subjects].find(s => fired.has(`${rel.from}|${s}`) && rel.to.some(t => fired.has(`${t}|${s}`)));
    if (!subj) return [];
    const ids = [rel.from, ...rel.to.filter(t => fired.has(`${t}|${subj}`))].sort(), rid = rel.id;
    return [{ relation: rid, cite: rel.cite, note: rel.note, rules: ids.map(id => ({ id, reading: reading(id), cites: rmap.get(id)!.cites })) }];
  });
  return {
    engine: PROSE_VERSION, kbVersion: k.version, chapter: id, palace: spec.palace, schema: schema.id, order,
    draft: allowDraft && [...k.prose!.concepts, ...k.prose!.modifiers].some(c => c.status !== 'approved'),
    paragraphs, text: paragraphs.map(p => p.text).join('\n\n'), issues, metrics, pass: !issues.some(i => i.level === 'error'), advice: adviceOf(paragraphs, k, allowDraft, cseed),
    evidence: { resolved: resolved.map(r => ({ ruleId: r.ruleId, concept: r.concept, stance: r.stance, status: r.status, by: r.by, cites: r.cites })), tensions, unused: sel.unused,
      rules: Object.fromEntries([...new Set(paragraphs.flatMap(p => p.sentences.flatMap(s => s.trace.rules)))].sort().map(id => {
        const r = rmap.get(id)!; return [id, { reading: reading(id), cites: r.cites, verified: r.reviewStatus === 'verified' }];
      })),
      concepts: Object.fromEntries([...new Set(paragraphs.flatMap(p => p.sentences.flatMap(s => s.trace.concepts)))].map(c => [c, k.concepts.concepts.find(x => x.id === c)?.short ?? c])), divergences },
  };
}
