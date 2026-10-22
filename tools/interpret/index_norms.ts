// Corpus norms of the overview indices (src/interpret/indices.ts):
//   palace  mean raw natal sums per palace (the radar is a ratio to them: the books write about Mệnh far more than about any other palace);
//   layers  mean and spread of every period layer's raw net value, so each layer becomes a z-score and all layers share one unit;
//   cuts    the 10 / 30 / 70 / 90 % quantiles of the decade, year and month scores: the five levels (Rất thử thách … Rất thuận).
//   node tools/interpret/index_norms.ts      → engine/data/kg/index_norms.json (re-run after the rules, guards, base rates or weights change)
// The corpus is stratified (make_corpus.py): rare Mệnh configurations are over-represented, so the levels are a reference, not a
// population share and never a probability. The run also prints the check numbers of docs/INDICES-EVAL.md.
import { readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import { natalRawAll, periodInputs, periodScores, scoreDecade, LEVEL_Q, levelOf, INDICES_VERSION, type IndexNorms, type LayerNorm, type PeriodInputs } from '../../src/interpret/indices.ts';
import type { Knowledge } from '../../src/interpret/types.ts';

const ROOT = join(import.meta.dirname, '..', '..');
const r3 = (x: number) => Math.round(x * 1000) / 1000;
const stats = (xs: number[]): LayerNorm => {
  const n = xs.length || 1, m = xs.reduce((a, x) => a + x, 0) / n;
  return { mean: r3(m), sd: r3(Math.sqrt(xs.reduce((a, x) => a + (x - m) ** 2, 0) / n)) || 1 };
};
const quantile = (xs: number[], q: number) => { const s = [...xs].sort((a, b) => a - b); return s.length ? r3(s[Math.min(s.length - 1, Math.floor(q * s.length))]) : 0; };
export const corr = (a: number[], b: number[]) => {
  const n = a.length, ma = a.reduce((s, x) => s + x, 0) / n, mb = b.reduce((s, x) => s + x, 0) / n;
  let sab = 0, saa = 0, sbb = 0;
  for (let i = 0; i < n; i++) { sab += (a[i] - ma) * (b[i] - mb); saa += (a[i] - ma) ** 2; sbb += (b[i] - mb) ** 2; }
  return r3(sab / Math.sqrt(saa * sbb || 1));
};

export function indexNorms(K: Knowledge, charts: any[], log = false): { norms: IndexNorms; check: Record<string, unknown> } {
  // pass 1: the radar means
  const acc = new Map<string, { support: number; limit: number }>();
  for (const c of charts) for (const [name, v] of Object.entries(natalRawAll(c.facts, K))) {
    const a = acc.get(name) ?? acc.set(name, { support: 0, limit: 0 }).get(name)!;
    a.support += v.support; a.limit += v.limit;
  }
  const n = charts.length;
  const norms: IndexNorms = { version: INDICES_VERSION, kbVersion: K.version, charts: n, corpus: 'corpus1000.json.gz',
    palace: Object.fromEntries([...acc.entries()].map(([k, v]) => [k, { support: r3(v.support / n), limit: r3(v.limit / n) }])) };
  if (log) console.log('pass 1 (radar means) done');
  // pass 2: every period layer's raw value
  const inputs: PeriodInputs[] = charts.map(c => periodInputs(c.facts, K, norms));
  const raw: Record<string, number[]> = {};
  const push = (k: string, x: number) => (raw[k] ??= []).push(x);
  for (const p of inputs) {
    push('vung', p.vung.raw);
    for (const d of p.decades) for (const l of d.layers) push(l.layer, l.raw);
    for (const y of p.years) for (const l of y.layers) if (l.layer !== 'nen' && l.layer !== 'luu_thai_tue') push(l.layer, l.raw);
  }
  norms.layers = Object.fromEntries(Object.entries(raw).map(([k, xs]) => [k, stats(xs)]));
  // the decade score is itself the year's first layer: its spread, with the layers above
  const dScores = inputs.flatMap(p => p.decades.map(d => scoreDecade(norms, d.layers, p.vung).score));
  norms.layers.dai_van = stats(dScores);
  // pass 3: the cut points of each kind of period
  const all = inputs.map(p => periodScores(p, norms));
  const kinds = { decade: all.flatMap(s => s.decades), year: all.flatMap(s => s.years), month: all.flatMap(s => s.months) };
  norms.cuts = { decade: LEVEL_Q.map(q => quantile(kinds.decade, q)), year: LEVEL_Q.map(q => quantile(kinds.year, q)), month: LEVEL_Q.map(q => quantile(kinds.month, q)) };
  // check numbers: how far the decade score still follows the natal quality of its palace, and the spread of the levels
  const natalOf = inputs.flatMap(p => p.decades.map(d => p.natalNet[d.d.palace] ?? 0));
  const spread = (xs: number[], cuts: number[]) => { const h = [0, 0, 0, 0, 0]; for (const x of xs) h[levelOf(x, cuts)]++; return h.map(c => r3(c / (xs.length || 1))); };
  const curDecade = inputs.flatMap((p, i) => p.decades.map((d, j) => ({ cur: charts[i].facts.year.dai_han?.age_from === d.d.age_from, s: all[i].decades[j] })));
  const check = {
    corr_decade_natal: corr(kinds.decade, natalOf),
    corr_decade_layers: Object.fromEntries(['hoa_van', 'van', 'nen'].map(l => [l, corr(kinds.decade, inputs.flatMap(p => p.decades.map(d => d.layers.find(x => x.layer === l)!.raw)))])),
    corr_year_decade: corr(all.flatMap((s, i) => inputs[i].years.map((y, j) => y.decade === null ? NaN : s.years[j])).filter(x => !Number.isNaN(x)),
      all.flatMap((s, i) => inputs[i].years.filter(y => y.decade !== null).map(y => s.decades[y.decade!]))),
    levels: { decade: spread(kinds.decade, norms.cuts.decade), year: spread(kinds.year, norms.cuts.year), month: spread(kinds.month, norms.cuts.month),
      current_decade: spread(curDecade.filter(x => x.cur).map(x => x.s), norms.cuts.decade) },
    n: { decades: kinds.decade.length, years: kinds.year.length, months: kinds.month.length },
  };
  return { norms, check };
}

if (import.meta.main) {
  const K: Knowledge = JSON.parse(readFileSync(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'), 'utf8'));
  const corpus = JSON.parse(gunzipSync(readFileSync(join(ROOT, 'src', 'interpret', 'test', 'fixtures', 'corpus1000.json.gz'))).toString('utf8'));
  const t0 = Date.now();
  const { norms, check } = indexNorms(K, corpus, true);
  writeFileSync(join(ROOT, 'engine', 'data', 'kg', 'index_norms.json'), JSON.stringify(norms, null, 1) + '\n');
  console.log(`index_norms.json: ${norms.charts} charts, ${((Date.now() - t0) / 1000).toFixed(1)} s`);
  console.log(JSON.stringify({ layers: norms.layers, cuts: norms.cuts, check }, null, 1));
}
