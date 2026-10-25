// Corpus norms of the overview indices (src/interpret/indices.ts):
//   palace  mean raw natal sums per palace (the radar is a ratio to them: the books write about Mệnh far more than about any other palace);
//   layers  mean, spread and root mean square of every period layer's raw net value; the rms is the unit (raw / rms, not centred, so a
//           layer with nothing adds 0) and all layers share it;
//   cuts    the 12 / 33 / 67 / 88 % quantiles of the decade, year and month scores of the periods with book evidence: the five levels
//           (a scale anchored at 0 was tried: the book material leans favourable, 99.6 % of decades came out Thuận or above).
//   node tools/interpret/index_norms.ts      → engine/data/kg/index_norms.json (re-run after the rules, guards, base rates or weights change)
// The corpus is stratified (make_corpus.py): rare Mệnh configurations are over-represented, so the levels are a reference, not a
// population share and never a probability. The run also prints the check numbers of docs/INDICES-EVAL.md.
import { readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import { natalRawAll, periodInputs, periodScores, scoreDecade, LEVEL_Q, levelOf, INDICES_VERSION, type IndexNorms, type LayerNorm, type PeriodInputs, type ScoredPeriod } from '../../src/interpret/indices.ts';
import type { Knowledge } from '../../src/interpret/types.ts';

const ROOT = join(import.meta.dirname, '..', '..');
const r3 = (x: number) => Math.round(x * 1000) / 1000;
const stats = (xs: number[]): LayerNorm => {
  const n = xs.length || 1, m = xs.reduce((a, x) => a + x, 0) / n;
  return { mean: r3(m), sd: r3(Math.sqrt(xs.reduce((a, x) => a + (x - m) ** 2, 0) / n)) || 1, rms: r3(Math.sqrt(xs.reduce((a, x) => a + x * x, 0) / n)) || 1 };
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
  // pass 2: every period layer's raw value. The corpus facts were made before KL pp.39-40 became the tiểu hạn default (2026-10-24): the years
  // and months are walked with the default school here, so the norms describe what the live charts draw.
  const inputs: PeriodInputs[] = charts.map(c => periodInputs(c.facts, K, norms, 10, { tieuHanRule: 'KL' }));
  const raw: Record<string, number[]> = {};
  const push = (k: string, x: number) => (raw[k] ??= []).push(x);
  for (const p of inputs) {
    push('vung', p.natalNet['Mệnh'] ?? 0);
    if (p.than) push('vung', p.natalNet[p.than] ?? 0);
    for (const d of p.decades) for (const l of d.layers) push(l.layer, l.raw);
    for (const y of p.years) for (const l of y.layers) push(l.layer, l.raw);
    for (const m of p.months ?? []) push('nguyet', m.layer.raw);
  }
  norms.layers = Object.fromEntries(Object.entries(raw).map(([k, xs]) => [k, stats(xs)]));
  // the decade score is itself the year's first layer: its size, with the layers above
  const dScores = inputs.flatMap(p => p.decades.map(d => scoreDecade(norms, d.layers).score));
  norms.layers.dai_van = stats(dScores);
  // pass 3: the cut points of each kind of period, on the periods with book evidence (a period without is told "chưa đủ căn cứ", not placed)
  const all = inputs.map(p => periodScores(p, norms));
  const kinds = { decade: all.flatMap(s => s.decades), year: all.flatMap(s => s.years), month: all.flatMap(s => s.months) };
  const booked = (xs: ScoredPeriod[]) => xs.filter(x => x.book).map(x => x.score);
  norms.cuts = { decade: LEVEL_Q.map(q => quantile(booked(kinds.decade), q)), year: LEVEL_Q.map(q => quantile(booked(kinds.year), q)), month: LEVEL_Q.map(q => quantile(booked(kinds.month), q)) };
  // check numbers: how far the decade score still follows the natal quality of its palace, and the spread of the levels
  const natalOf = inputs.flatMap(p => p.decades.map(d => p.natalNet[d.d.palace] ?? 0));
  const spread = (xs: number[], cuts: number[]) => { const h = [0, 0, 0, 0, 0]; for (const x of xs) h[levelOf(x, cuts)]++; return h.map(c => r3(c / (xs.length || 1))); };
  const check = {
    corr_decade_natal: corr(kinds.decade.map(x => x.score), natalOf),
    corr_year_decade: corr(all.flatMap((s, i) => inputs[i].years.map((y, j) => y.decade === null ? NaN : s.years[j].score)).filter(x => !Number.isNaN(x)),
      all.flatMap((s, i) => inputs[i].years.filter(y => y.decade !== null).map(y => s.decades[y.decade!].score))),
    levels: { decade: spread(booked(kinds.decade), norms.cuts.decade), year: spread(booked(kinds.year), norms.cuts.year), month: spread(booked(kinds.month), norms.cuts.month) },
    insufficient: { decade: r3(1 - booked(kinds.decade).length / kinds.decade.length), year: r3(1 - booked(kinds.year).length / kinds.year.length),
      month: r3(1 - booked(kinds.month).length / (kinds.month.length || 1)) },
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
