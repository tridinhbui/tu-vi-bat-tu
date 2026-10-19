// Reader prose for the Mệnh chapter (prose plan P3): chart facts -> rules -> concepts -> resolution -> selection -> schema -> sentences.
// No language model; deterministic for a given chart, knowledge version and prose-library version. Cards that are not 'approved' are
// used only with allowDraft (TVBT_PROSE_DRAFT on the Worker); without any usable card the chapter is empty, never padded.
import { run } from '../engine.ts';
import { lift } from '../kg/lift.ts';
import { resolve, type Resolved, type Tension } from '../kg/resolve.ts';
import type { ChartInput, Knowledge } from '../types.ts';
import { chooseSchema, presentMoves } from './discourse.ts';
import { Micro, fnv, lowerFirst } from './micro.ts';
import { Realizer, type ProseParagraph, type ProseSentence } from './realize.ts';
import { select, type Selection } from './select.ts';
import { validateProse, type ProseIssue, type ProseMetrics } from './validate.ts';
import type { Move } from './types.ts';

export const PROSE_VERSION = 'prose-0.1.0';
export interface ProseChapter {
  engine: string; kbVersion: string; chapter: 'menh'; schema: string; order: Move[];
  /** draft cards were allowed and the library still holds drafts: the reader must be told the wording is unreviewed */
  draft: boolean;
  paragraphs: ProseParagraph[]; text: string; issues: ProseIssue[]; metrics: ProseMetrics; pass: boolean;
  evidence: { resolved: Array<Pick<Resolved, 'ruleId' | 'concept' | 'stance' | 'status' | 'by' | 'cites'>>; tensions: Tension[]; unused: string[];
    /** every rule a sentence traces to, with its book paraphrase and pages, for the evidence panel */
    rules: Record<string, { reading: string; cites: string[]; verified: boolean }>; concepts: Record<string, string> };
}

/** Starts with a proper name (a star, Tuần/Triệt, a Hóa): its capital stays when the sentence is woven into the previous one. */
const properStart = (t: string) => /^(\p{Lu}\p{Ll}*\s\p{Lu})|^(Tuần|Triệt)\b/u.test(t);
const words = (t: string) => t.split(/\s+/).length;
/** A sentence may join the one before it with a semicolon: an elaboration after the anchor, a timing or course remark, or the turn
 *  right after the anchor; both factual (editorial sentences are never woven), and the result at most 48 words. */
const canWeave = (prev: ProseSentence, s: ProseSentence) =>
  ((s.trace.move === 'ELABORATE' && (prev.trace.move === 'ANCHOR' || prev.trace.move === 'BORROW')) || s.trace.move === 'TIMING' || s.trace.move === 'EXTRA'
    || (s.trace.move === 'TURN' && prev.trace.move === 'ANCHOR')) && !prev.trace.woven && prev.trace.basis === 'sach' && s.trace.basis === 'sach' && words(prev.text) + words(s.text) <= 48;
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
  const ps = paras.map(([role, xs]) => {
    const out: ProseSentence[] = [];
    for (const s of xs) { const prev = out[out.length - 1]; if (prev && canWeave(prev, s) && fnv(`${seed}|weave|${role}|${out.length}`) % 3 !== 0) out[out.length - 1] = join2(prev, s); else out.push(s); }
    return [role, out] as [ProseParagraph['role'], ProseSentence[]];
  });
  const lens = () => ps.flatMap(([, xs]) => xs.map(s => words(s.text)));
  for (let guard = 0; guard < 6 && spread(lens()) < 6; guard++) {
    let best = null as [number, number, number] | null;
    ps.forEach(([, xs], pi) => xs.forEach((s, i) => {
      if (!i || !canWeave(xs[i - 1], s)) return;
      const trial = lens(), off = ps.slice(0, pi).reduce((a, [, ys]) => a + ys.length, 0) + i;
      trial.splice(off - 1, 2, trial[off - 1] + trial[off]);
      const sd = spread(trial);
      if (!best || sd > best[2]) best = [pi, i, sd];
    }));
    const pick = best as [number, number, number] | null;
    if (!pick || pick[2] <= spread(lens())) break;
    const [pi, i] = pick, xs = ps[pi][1];
    xs.splice(i - 1, 2, join2(xs[i - 1], xs[i]));
  }
  return ps;
}

export function seedOf(chart: ChartInput): string {
  return `${chart.birth_year}|${chart.year_gz}|${chart.palaces.map(p => p.stars.join(',')).join('/')}`;
}

export function proseMenh(chart: ChartInput, k: Knowledge, opts: { allowDraft?: boolean } = {}): ProseChapter {
  const findings = run(k.rules, k.sources, chart.base).findings.filter(f => f.subject === 'palace:Mệnh' || f.subject === 'chart');
  const { assertions } = lift(findings, k, chart.base);
  const { resolved, tensions } = resolve(assertions, k);
  const menh = chart.palaces.find(p => p.name === 'Mệnh')!, opp = chart.palaces.find(p => p.name === 'Thiên Di');
  const sel: Selection = select(resolved, k, menh, opp);
  const seed = seedOf(chart);
  const micro = new Micro(seed, k.prose!.connectives, k.prose!.frames);
  const R = new Realizer(k, sel, micro, !!opts.allowDraft);

  // paragraph 1: the schema's moves
  const present = presentMoves(sel);
  const { schema, order } = chooseSchema(k.prose!.schemas, present, seed);
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
  const sats = placed.has('SATELLITE') ? sel.satellites.slice(2) : sel.satellites;
  push(R.satellite(sats, 'sat2', sel.satelliteNeg));
  if (present.has('TIMING') && !placed.has('TIMING')) push(R.timing());

  // paragraph 3: the độ số balance and the course of life
  const p3: ProseSentence[] = [];
  const d = R.degree();
  if (d) p3.push(d);
  sel.extra.forEach((x, i) => { const s = R.course(x, i); if (s) p3.push(s); });

  const paragraphs: ProseParagraph[] = rhythm(([['core', p1], ['support', p2], ['course', p3]] as Array<[ProseParagraph['role'], ProseSentence[]]>).filter(([, xs]) => xs.length), seed)
    .map(([role, xs]) => ({ role, sentences: xs, text: xs.map(s => s.text).join(' ') }));
  const { issues, metrics } = validateProse(paragraphs, resolved);
  const rmap = new Map(k.rules.map(r => [r.id, r]));
  return {
    engine: PROSE_VERSION, kbVersion: k.version, chapter: 'menh', schema: schema.id, order,
    draft: !!opts.allowDraft && [...k.prose!.concepts, ...k.prose!.modifiers].some(c => c.status !== 'approved'),
    paragraphs, text: paragraphs.map(p => p.text).join('\n\n'), issues, metrics, pass: !issues.some(i => i.level === 'error'),
    evidence: { resolved: resolved.map(r => ({ ruleId: r.ruleId, concept: r.concept, stance: r.stance, status: r.status, by: r.by, cites: r.cites })), tensions, unused: sel.unused,
      rules: Object.fromEntries([...new Set(paragraphs.flatMap(p => p.sentences.flatMap(s => s.trace.rules)))].sort().map(id => {
        const r = rmap.get(id)!; return [id, { reading: (r.reading ?? k.claims[r.consequences[0]?.claim ?? ''] ?? '').replace(/^(khuynh hướng|hạn chế:)\s*/, ''), cites: r.cites, verified: r.reviewStatus === 'verified' }];
      })),
      concepts: Object.fromEntries([...new Set(paragraphs.flatMap(p => p.sentences.flatMap(s => s.trace.concepts)))].map(c => [c, k.concepts.concepts.find(x => x.id === c)?.short ?? c])) },
  };
}
