// Deterministic interpretation pipeline: chart facts -> rule inference -> semantic evidence -> knowledge graph -> argument graph(s) ->
// narrative -> quality report. No model inference anywhere; the marginal cost per chart is a few milliseconds of CPU.
// Rule inference, evidence and the chart graph are computed once per chart and shared by every chapter (prepare()).
import { run, type EngineResult } from './engine.ts';
import { ChartGraph } from './graph.ts';
import { plan, type ArgumentGraph } from './planner.ts';
import { Realizer, newState, type Paragraph } from './generator.ts';
import { Lexicon, annotate, type Evidence } from './semantic.ts';
import { validate, type QualityReport } from './validate.ts';
import { SPECS, CHAPTER_IDS, type ChapterId } from './chapters.ts';
import { timeline } from './timeline.ts';
import { baziChapter } from './bazi.ts';
import type { ChartInput, ContentModule, Knowledge, Rule } from './types.ts';

export const ENGINE_VERSION = 'interpret-2.0.0';
export const CHAPTERS = CHAPTER_IDS;
export type Chapter = ChapterId;

export interface SectionSummary {
  palace: string; themes: Array<{ facet: string; lead: string; polarity: string; counters: Array<{ quote: string; kind: string }>; supports: number }>;
  claims: Array<{ id: string; role: string; concept: string; palace: string; polarity: string; quotes: string[]; rules: string[]; grounds: number; independentGrounds: number }>;
  dominance: Array<{ base: string; qualifier: string; verdict: string; criteria: string[] }>; cross: Array<{ quote: string; deps: Array<{ star: string; palace: string }> }>;
  tensions: Array<{ pos: string; neg: string; kind: string }>; slots: Record<string, string>; excluded: ArgumentGraph['excluded']; evidenceCount: number;
}
export interface ChapterOutput {
  engine: string; kbVersion: string; chapter: Chapter; title: string;
  paragraphs: Paragraph[]; text: string; quality: QualityReport;
  argument: { chapter: Chapter; sections: SectionSummary[] };
  trace: { fired: number; verified: number; evidence: number; graph: { nodes: number; edges: number } };
}

interface Prepared { res: EngineResult; ev: Evidence[]; g: ChartGraph; lex: Lexicon; drafts: Array<{ rule: Rule; claim: string }>; verified: Set<string>; seed: string }
const lexCache = new WeakMap<Knowledge, Lexicon>();
const prepCache = new WeakMap<ChartInput, WeakMap<Knowledge, Prepared>>();

/** Rule inference + semantic evidence + chart graph, once per (chart object, knowledge). Chapters only read it. */
export function prepare(chart: ChartInput, k: Knowledge): Prepared {
  const hit = prepCache.get(chart)?.get(k);
  if (hit) return hit;
  const res = run(k.rules, k.sources, chart.base);
  const lex = lexCache.get(k) ?? new Lexicon(k); lexCache.set(k, lex);
  const ev = annotate(res.findings, k, lex, chart.base);
  const g = new ChartGraph(chart, ev);
  const rmap = new Map(k.rules.map(r => [r.id, r]));
  const drafts = res.findings.filter(f => f.basis !== 'verified').map(f => ({ rule: rmap.get(f.ruleId)!, claim: f.claim }));
  const verified = new Set(res.findings.filter(f => f.basis === 'verified').map(f => f.ruleId));
  const seed = `${chart.birth_year}|${chart.year_gz}|${chart.palaces.map(p => p.stars.join(',')).join('/')}`;
  const p: Prepared = { res, ev, g, lex, drafts, verified, seed };
  if (!prepCache.has(chart)) prepCache.set(chart, new WeakMap());
  prepCache.get(chart)!.set(k, p);
  return p;
}

const modulesFor = (k: Knowledge, chapter: string): ContentModule[] =>
  k.modules.filter(m => m.chapter === chapter || (m.chapter === '*' && !(m.exceptChapters ?? []).includes(chapter)));

function summary(a: ArgumentGraph): SectionSummary {
  return { palace: a.focus,
    themes: a.themes.map(t => ({ facet: t.facet, lead: t.lead.quotes[0], polarity: t.polarity, supports: t.support.length, counters: t.counters.map(c => ({ quote: c.claim.quotes[0], kind: c.kind })) })),
    claims: a.claims.map(c => ({ id: c.id, role: c.role, concept: c.concept, palace: c.palace, polarity: c.polarity, quotes: c.quotes, rules: c.rules, grounds: c.grounds.length, independentGrounds: c.grounds.filter(x => x.independent).length })),
    dominance: a.dominance.map(d => ({ base: d.base.quotes[0], qualifier: d.qualifier.quotes[0], verdict: d.verdict, criteria: d.criteria })),
    cross: a.cross.map(x => ({ quote: x.claim.quotes[0], deps: x.deps })),
    tensions: a.tensions.map(t => ({ pos: t.pos.quotes[0], neg: t.neg.quotes[0], kind: t.kind })), slots: a.slots, excluded: a.excluded, evidenceCount: a.evidenceCount };
}

export function interpret(chart: ChartInput, chapter: Chapter, k: Knowledge): ChapterOutput {
  const spec = SPECS[chapter];
  if (!spec) throw new Error(`unknown chapter ${chapter}`);
  const P = prepare(chart, k);
  const modules = modulesFor(k, chapter);
  let paras: Paragraph[] = [], graphs: ArgumentGraph[] = [], verified = P.verified;
  if (chapter === 'bat_tu') {
    const b = baziChapter(chart, k, modules, P.seed);
    paras = b.paragraphs; verified = b.verified;
  } else if (chapter === 'van_han') {
    const t = timeline(chart, P, k, modules);
    paras = t.paragraphs; graphs = t.graphs;
  } else {
    graphs = spec.sections.map(sec => plan(chart, P.ev, P.g, P.lex, k, P.drafts, P.res.findings, spec, sec));
    const multi = spec.sections.length > 1;
    const conceptShort = (id: string) => k.concepts.concepts.find(c => c.id === id)?.short ?? '';
    const summaryText = graphs.map(a => a.themes[0] ? `ở ${a.focus} là ${conceptShort(a.themes[0].lead.concept) || a.themes[0].facetName}` : '').filter(Boolean);
    // a section is empty only when no verified reading at all was attached to it (a timing reading counts)
    const emptySections = graphs.filter(a => !a.claims.length).map(a => a.focus);
    const render = (scale: number) => {
      const recent: string[] = [], out: Paragraph[] = [], state = newState();
      graphs.forEach((a, i) => {
        const extra: Record<string, string> = { 'section.multi': multi ? '1' : '', 'section.first': i === 0 ? '1' : '', 'section.last': i === graphs.length - 1 ? '1' : '',
          'chapter.sensitive': spec.sensitive ?? '', [`sensitive.${spec.sensitive ?? 'none'}`]: '1',
          'chapter.summary': summaryText.length ? summaryText.join('; ') : '', 'chapter.empty': emptySections.join(', ') };
        const r = new Realizer(a, k, `${P.seed}|${chapter}|${i}`, scale, extra, state);
        for (const p of r.render(modules, recent)) {
          // in a combined chapter the section frame is titled by its palace, its themes "Palace — theme"; notice / limits / synthesis stay chapter-wide
          const title = !multi || ['synthesis', 'limits'].includes(p.role) || p.module === 'S.05.NOTICE' ? p.title : p.module === 'S.10.FRAME' ? a.focus : `${a.focus} — ${p.title}`;
          out.push({ ...p, section: multi ? a.focus : undefined, title });
        }
      });
      return out;
    };
    // word budget: a major chapter aims at 800–1,500 words when evidence allows; over budget, the lists are shortened (salience order),
    // never the reasoning paragraphs, and what was left out stays in the detailed evidence list. Text is never padded.
    paras = render(1);
    for (const scale of [0.75, 0.5]) {
      if (paras.map(p => p.text).join(' ').split(/\s+/).length <= 1500) break;
      paras = render(scale);
    }
  }
  const quality = validate(paras, graphs, chart, k, verified, spec.sensitive);
  return {
    engine: ENGINE_VERSION, kbVersion: k.version, chapter, title: spec.title, paragraphs: paras, text: paras.map(p => p.text).join('\n\n'), quality,
    argument: { chapter, sections: graphs.map(summary) },
    trace: { fired: P.res.findings.length, verified: P.verified.size, evidence: P.ev.length, graph: { nodes: P.g.nodes.size, edges: P.g.edges.length } },
  };
}

/** Every chapter of one chart (inference shared). */
export function interpretAll(chart: ChartInput, k: Knowledge): ChapterOutput[] {
  return CHAPTERS.map(c => interpret(chart, c, k));
}
