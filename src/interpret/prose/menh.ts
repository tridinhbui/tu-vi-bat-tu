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
/** Weave short factual sentences: an elaboration or a timing remark joins the sentence before it with a semicolon (seeded, about two
 *  times in three), so rhythm varies the way edited prose does. Editorial (he_thong) sentences are never woven. */
function weave(xs: ProseSentence[], seed: string, tag: string): ProseSentence[] {
  const out: ProseSentence[] = [];
  for (const s of xs) {
    const prev = out[out.length - 1];
    if (prev && ((s.trace.move === 'ELABORATE' && (prev.trace.move === 'ANCHOR' || prev.trace.move === 'BORROW')) || s.trace.move === 'TIMING' || s.trace.move === 'EXTRA' || (s.trace.move === 'TURN' && prev.trace.move === 'ANCHOR')) && prev.trace.basis === 'sach' && s.trace.basis === 'sach'
        && words(prev.text) + words(s.text) <= 48 && fnv(`${seed}|weave|${tag}|${out.length}`) % 3 !== 0) {
      const second = properStart(s.text) ? s.text : lowerFirst(s.text);
      out[out.length - 1] = { text: `${prev.text.replace(/\.$/, '')}; ${second}`, trace: { ...prev.trace, concepts: [...new Set([...prev.trace.concepts, ...s.trace.concepts])],
        rules: [...new Set([...prev.trace.rules, ...s.trace.rules])].sort(), cites: [...new Set([...prev.trace.cites, ...s.trace.cites])].sort(), woven: [...(prev.trace.woven ?? []), s.trace.move] } };
    } else out.push(s);
  }
  return out;
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

  const paragraphs: ProseParagraph[] = ([['core', p1], ['support', p2], ['course', p3]] as const)
    .filter(([, xs]) => xs.length).map(([role, xs]) => { const w = weave(xs, seed, role); return { role, sentences: w, text: w.map(s => s.text).join(' ') }; });
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
