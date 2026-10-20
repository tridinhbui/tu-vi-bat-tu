// Depth of the reader prose (plan async-inventing-fairy, step 0): how much each chapter says, how often a chapter is empty, which basis
// the sentences stand on, and how many negative sentences go out with nothing that answers them. Corpus charts, plus one golden chart.
//   node tools/interpret/eval_depth.ts [--n 200] [--golden src/interpret/test/fixtures/user_1990_nam.json] [--out docs/examples/prose-depth.md]
import { readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import { proseReport, seedOf, PROSE_VERSION } from '../../src/interpret/prose/chapter.ts';
import { proseVanHan } from '../../src/interpret/prose/vanhan.ts';
import { proseBazi } from '../../src/interpret/prose/bazi.ts';
import type { ChartInput, Knowledge } from '../../src/interpret/types.ts';
import type { ProseParagraph, ProseSentence } from '../../src/interpret/prose/realize.ts';

const ROOT = join(import.meta.dirname, '..', '..');
const arg = (k: string) => process.argv.includes(k) ? process.argv[process.argv.indexOf(k) + 1] : undefined;
const K: Knowledge = JSON.parse(readFileSync(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'), 'utf8'));

export interface ChapterOut { chapter: string; paragraphs: ProseParagraph[] }
/** the whole report for one chart, the way the route's chapter "all" builds it */
export function report(c: ChartInput, k: Knowledge = K): ChapterOut[] {
  return [...proseReport(c, k, { allowDraft: true, deep: true }), proseVanHan(c, k, seedOf(c), PROSE_VERSION, true), proseBazi(c, k, seedOf(c), PROSE_VERSION, true)];
}

const words = (t: string) => t.split(/\s+/).filter(Boolean).length;
const sentences = (ch: ChapterOut) => ch.paragraphs.flatMap(p => p.sentences);
/** a sentence that tells of a difficulty: the move says so, or the trace marks it negative */
const isNeg = (s: ProseSentence) => s.trace.move === 'TURN' || s.trace.move === 'TENSION' || (s.trace as { tone?: string }).tone === 'neg';
/** what answers a difficulty: a rescue, a transform, or advice in the same paragraph */
const isAnswer = (s: ProseSentence) => ['RESCUE', 'TRANSFORM', 'VALUE'].includes(s.trace.move) || (s.trace as { tone?: string }).tone === 'answer';

export interface DepthStats {
  charts: number;
  chapters: Record<string, { meanWords: number; minWords: number; empty: number }>;
  basis: Record<string, number>; negatives: number; negativesUnanswered: number;
}

export function depth(charts: ChartInput[], k: Knowledge = K): DepthStats {
  const per = new Map<string, number[]>(), basis: Record<string, number> = {};
  let negatives = 0, negativesUnanswered = 0;
  for (const c of charts) for (const ch of report(c, k)) {
    const id = ch.chapter;
    (per.get(id) ?? per.set(id, []).get(id)!).push(words(ch.paragraphs.map(p => p.text).join(' ')));
    const answered = sentences(ch).some(isAnswer);       // the balance paragraph answers for the whole chapter
    for (const p of ch.paragraphs) {
      for (const s of p.sentences) {
        basis[s.trace.basis] = (basis[s.trace.basis] ?? 0) + 1;
        if (isNeg(s)) { negatives++; if (!answered) negativesUnanswered++; }
      }
    }
  }
  const chapters: DepthStats['chapters'] = {};
  for (const [id, ws] of per) chapters[id] = { meanWords: Math.round(ws.reduce((a, b) => a + b, 0) / ws.length), minWords: Math.min(...ws), empty: ws.filter(w => w === 0).length };
  return { charts: charts.length, chapters, basis, negatives, negativesUnanswered };
}

if (import.meta.main) {
  const corpus = JSON.parse(gunzipSync(readFileSync(join(ROOT, 'src', 'interpret', 'test', 'fixtures', 'corpus1000.json.gz'))).toString('utf8'));
  const n = Number(arg('--n')) || 200;
  const d = depth(corpus.slice(0, n).map((x: { facts: ChartInput }) => x.facts));
  const gPath = arg('--golden') ?? join(ROOT, 'src', 'interpret', 'test', 'fixtures', 'user_1990_nam.json');
  const g: ChartInput = JSON.parse(readFileSync(gPath, 'utf8'));
  const gr = report(g);
  const lines = [`# Prose depth (${PROSE_VERSION}, kb ${K.version})`, '', `Corpus: first ${d.charts} charts of corpus1000.`, '',
    '| chapter | mean words | min | empty |', '|---|---|---|---|',
    ...Object.entries(d.chapters).map(([id, s]) => `| ${id} | ${s.meanWords} | ${s.minWords} | ${s.empty} |`), '',
    `Sentences by basis: ${Object.entries(d.basis).map(([b, x]) => `${b} ${x}`).join(', ')}.`,
    `Negative sentences: ${d.negatives}, of which in a chapter with nothing answering them: ${d.negativesUnanswered}.`, '',
    `## Golden chart (${gPath.split('/').pop()})`, '',
    ...gr.map(ch => `### ${ch.chapter} (${words(sentences(ch).map(s => s.text).join(' '))} words)\n\n${ch.paragraphs.map(p => p.text).join('\n\n')}\n`)];
  const out = arg('--out') ?? join(ROOT, 'docs', 'examples', 'prose-depth.md');
  writeFileSync(out, lines.join('\n'));
  console.log(lines.slice(0, 8 + Object.keys(d.chapters).length + 3).join('\n'));
}
