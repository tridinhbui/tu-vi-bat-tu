// Repetition inside one report (review of the live report 2026-10-23, point 15: "lặp ý, lặp sao, lặp cấu trúc câu"), over the corpus:
//   node tools/interpret/eval_repeat.ts [--n 200] [--json out.json]
//   sentences   exact sentences told twice or more in one report (Tử Vi chapters, đại hạn, Tổng luận; after checkedOnly)
//   ngrams      6-word runs (lowercased, names kept) found in two or more sentences of one report, per 100 sentences: a frame reused
//   ledger      sentences naming a domain's verdict ("trace.ledger"), per domain per report: the verdict is told once in full, echoes count
//   unresolved  sentences that say two sides stay unadjudicated ("chưa phân xử"), per report
// The cross-chart measure (eval_distinct.ts) is a different question: whether two charts read alike.
import { readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import type { ChartInput, Knowledge } from '../../src/interpret/types.ts';
import { proseAllChapters } from '../../src/interpret/route.ts';
import { checkedOnly } from '../../src/interpret/prose/checked.ts';

const ROOT = join(import.meta.dirname, '..', '..');
const arg = (k: string, d: string) => process.argv.includes(k) ? process.argv[process.argv.indexOf(k) + 1] : d;
const K: Knowledge = JSON.parse(readFileSync(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'), 'utf8'));
const corpus = JSON.parse(gunzipSync(readFileSync(join(ROOT, 'src', 'interpret', 'test', 'fixtures', 'corpus1000.json.gz'))).toString()) as Array<{ facts: ChartInput }>;
const N = Number(arg('--n', '200'));
type S = { text: string; trace: { ledger?: { domain: string } } };
const m = { charts: 0, sentences: 0, repeatedSentences: 0, ngramHits: 0, ledgerMentions: 0, ledgerDomains: 0, maxLedger: 0, unresolved: 0 };
const top = new Map<string, number>();
for (const c of corpus.slice(0, N)) {
  const chs = proseAllChapters(c.facts, K, { allowDraft: true, deep: true, luan: true }).filter(x => x.chapter !== 'bat_tu').map(x => checkedOnly(x as never) as unknown as { paragraphs: Array<{ sentences: S[] }> });
  const ss = chs.flatMap(x => x.paragraphs.flatMap(p => p.sentences));
  m.charts++; m.sentences += ss.length;
  const seen = new Map<string, number>();
  for (const s of ss) seen.set(s.text, (seen.get(s.text) ?? 0) + 1);
  m.repeatedSentences += [...seen.values()].filter(n => n > 1).reduce((a, n) => a + n - 1, 0);
  const gram = new Map<string, Set<number>>();
  ss.forEach((s, i) => { const w = s.text.toLowerCase().replace(/[.,;:()“”"]/g, ' ').split(/\s+/).filter(Boolean);
    for (let j = 0; j + 6 <= w.length; j++) { const g = w.slice(j, j + 6).join(' '); (gram.get(g) ?? gram.set(g, new Set()).get(g)!).add(i); } });
  for (const [g, xs] of gram) if (xs.size > 1) { m.ngramHits += xs.size - 1; top.set(g, (top.get(g) ?? 0) + xs.size - 1); }
  const led = new Map<string, number>();
  for (const s of ss) if (s.trace.ledger) led.set(s.trace.ledger.domain, (led.get(s.trace.ledger.domain) ?? 0) + 1);
  m.ledgerMentions += [...led.values()].reduce((a, n) => a + n, 0); m.ledgerDomains += led.size; m.maxLedger = Math.max(m.maxLedger, ...led.values(), 0);
  m.unresolved += ss.filter(s => /chưa phân xử|chưa có phân xử|chưa xếp được/.test(s.text)).length;
}
const out = { ...m, repeatedPerReport: +(m.repeatedSentences / m.charts).toFixed(2), ngramPer100: +(100 * m.ngramHits / m.sentences).toFixed(1),
  ledgerPerDomain: +(m.ledgerMentions / Math.max(1, m.ledgerDomains)).toFixed(2), unresolvedPerReport: +(m.unresolved / m.charts).toFixed(2),
  topNgrams: [...top].sort((a, b) => b[1] - a[1]).slice(0, 25) };
console.log(JSON.stringify(out, null, 1));
if (process.argv.includes('--json')) writeFileSync(arg('--json', 'eval_repeat.json'), JSON.stringify(out, null, 1));
