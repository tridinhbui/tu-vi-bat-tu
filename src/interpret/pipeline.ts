// Deterministic interpretation pipeline: chart facts -> rule inference -> semantic evidence -> knowledge graph -> argument graph ->
// narrative -> quality report. No model inference anywhere; the marginal cost per chart is a few milliseconds of CPU.
import { run } from './engine.ts';
import { ChartGraph } from './graph.ts';
import { plan, type ArgumentGraph } from './planner.ts';
import { Realizer, type Paragraph } from './generator.ts';
import { Lexicon, annotate } from './semantic.ts';
import { validate, type QualityReport } from './validate.ts';
import type { ChartInput, Knowledge } from './types.ts';

export const ENGINE_VERSION = 'interpret-1.0.0';
export const CHAPTERS = ['cong_danh'] as const;
export type Chapter = typeof CHAPTERS[number];

export interface ChapterOutput {
  engine: string; kbVersion: string; chapter: Chapter; title: string;
  paragraphs: Paragraph[]; text: string; quality: QualityReport;
  argument: Omit<ArgumentGraph, 'claims' | 'cross' | 'dominance' | 'lists' | 'tensions' | 'timingConflict'> & {
    tensions: Array<{ pos: string; neg: string; kind: string }>;
    claims: Array<{ id: string; role: string; concept: string; palace: string; polarity: string; quotes: string[]; rules: string[]; grounds: number; independentGrounds: number }>;
    dominance: Array<{ base: string; qualifier: string; verdict: string; criteria: string[] }>; cross: Array<{ quote: string; deps: Array<{ star: string; palace: string }> }>;
  };
  trace: { fired: number; verified: number; evidence: number; graph: { nodes: number; edges: number } };
}

const lexCache = new WeakMap<Knowledge, Lexicon>();

export function interpret(chart: ChartInput, chapter: Chapter, k: Knowledge): ChapterOutput {
  const res = run(k.rules, k.sources, chart.base);
  const lex = lexCache.get(k) ?? new Lexicon(k); lexCache.set(k, lex);
  const ev = annotate(res.findings, k, lex, chart.base);
  const g = new ChartGraph(chart, ev);
  const rmap = new Map(k.rules.map(r => [r.id, r]));
  const drafts = res.findings.filter(f => f.basis !== 'verified').map(f => ({ rule: rmap.get(f.ruleId)!, claim: f.claim }));
  const a = plan(chart, ev, g, lex, k, drafts, res.findings);
  const seed = `${chart.birth_year}|${chart.year_gz}|${chart.palaces.map(p => p.stars.join(',')).join('/')}`;
  const modules = k.modules.filter(m => m.chapter === chapter);
  // word budget: a major chapter aims at 800–1,500 words when evidence allows; over budget, the lists are shortened (salience order),
  // never the reasoning paragraphs, and what was left out stays in the detailed evidence list
  let paras = new Realizer(a, k, seed).render(modules);
  for (const scale of [0.75, 0.5]) {
    if (paras.map(p => p.text).join(' ').split(/\s+/).length <= 1500) break;
    paras = new Realizer(a, k, seed, scale).render(modules);
  }
  const verified = new Set(res.findings.filter(f => f.basis === 'verified').map(f => f.ruleId));
  const quality = validate(paras, a, chart, k, verified);
  return {
    engine: ENGINE_VERSION, kbVersion: k.version, chapter, title: 'Công danh', paragraphs: paras, text: paras.map(p => p.text).join('\n\n'), quality,
    argument: { chapter: a.chapter, career: a.career, triad: a.triad, opposite: a.opposite, slots: a.slots, excluded: a.excluded, evidenceCount: a.evidenceCount,
      claims: a.claims.map(c => ({ id: c.id, role: c.role, concept: c.concept, palace: c.palace, polarity: c.polarity, quotes: c.quotes, rules: c.rules, grounds: c.grounds.length, independentGrounds: c.grounds.filter(x => x.independent).length })),
      dominance: a.dominance.map(d => ({ base: d.base.quotes[0], qualifier: d.qualifier.quotes[0], verdict: d.verdict, criteria: d.criteria })),
      cross: a.cross.map(x => ({ quote: x.claim.quotes[0], deps: x.deps })),
      tensions: a.tensions.map(t => ({ pos: t.pos.quotes[0], neg: t.neg.quotes[0], kind: t.kind })) },
    trace: { fired: res.findings.length, verified: verified.size, evidence: ev.length, graph: { nodes: g.nodes.size, edges: g.edges.length } },
  };
}
