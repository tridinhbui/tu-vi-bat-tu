// Corpus means of the raw ban_menh sums per palace (src/interpret/indices.ts): the books write about Mệnh far more than about any other palace,
// so the overview charts tell each palace's natal layer as a ratio to what the corpus' typical chart has on the same palace.
//   node tools/interpret/index_norms.ts      → engine/data/kg/index_norms.json (re-run after the rules, guards or base rates change)
// The corpus is stratified (make_corpus.py): rare Mệnh configurations are over-represented, so the mean is a reference level, not a
// population average and never a probability.
import { readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import { natalRawAll, INDICES_VERSION, type IndexNorms } from '../../src/interpret/indices.ts';
import type { Knowledge } from '../../src/interpret/types.ts';

const ROOT = join(import.meta.dirname, '..', '..');

export function indexNorms(K: Knowledge, charts: any[]): IndexNorms {
  const acc = new Map<string, { support: number; limit: number }>();
  for (const c of charts) for (const [name, v] of Object.entries(natalRawAll(c.facts, K))) {
    const a = acc.get(name) ?? acc.set(name, { support: 0, limit: 0 }).get(name)!;
    a.support += v.support; a.limit += v.limit;
  }
  const n = charts.length, r3 = (x: number) => Math.round(x / n * 1000) / 1000;
  return { version: INDICES_VERSION, kbVersion: K.version, charts: n, corpus: 'corpus1000.json.gz',
    palace: Object.fromEntries([...acc.entries()].map(([k, v]) => [k, { support: r3(v.support), limit: r3(v.limit) }])) };
}

if (import.meta.main) {
  const K: Knowledge = JSON.parse(readFileSync(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'), 'utf8'));
  const corpus = JSON.parse(gunzipSync(readFileSync(join(ROOT, 'src', 'interpret', 'test', 'fixtures', 'corpus1000.json.gz'))).toString('utf8'));
  const t0 = Date.now();
  const out = indexNorms(K, corpus);
  writeFileSync(join(ROOT, 'engine', 'data', 'kg', 'index_norms.json'), JSON.stringify(out, null, 1) + '\n');
  console.log(`index_norms.json: ${out.charts} charts, ${((Date.now() - t0) / 1000).toFixed(1)} s`);
  console.log(out.palace);
}
