// Base rates over the 1,000-chart corpus (plan quirky-tinkering-rabin R2b): how often each concept is asserted at Mệnh (or chart-level), and how
// often each Tử Vi rule fires on Mệnh. A reading that most charts would also get says little about THIS chart; the reasoner ranks theses by
// −log₂ of these rates and the distinctiveness evaluation (eval_distinct.ts) measures the voiced content against them.
//   node tools/interpret/base_rates.ts        → engine/data/kg/base_rates.json (then tools/interpret/build.ts compiles it into knowledge)
// Rates are over the stratified corpus (make_corpus.py), not the birth population: rare Mệnh configurations are over-represented there,
// so a rate is an upper bound on how common a reading is among real births, never a probability of anything.
import { readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import { run } from '../../src/interpret/engine.ts';
import { lift } from '../../src/interpret/kg/lift.ts';
import { applyQualifiers, resolve } from '../../src/interpret/kg/resolve.ts';
import type { Knowledge } from '../../src/interpret/types.ts';

const ROOT = join(import.meta.dirname, '..', '..');

export interface PalaceRates { concept: Record<string, number>; rule: Record<string, number> }
/** `concept` / `rule`: at Mệnh (or chart-level), as before; `palaces`: the same two rates for each other palace (the palace reasoner,
 *  reason/plan.ts reasonPalace, weighs a Quan Lộc reading against what most charts' Quan Lộc also get). */
export interface BaseRates { charts: number; corpus: string; concept: Record<string, number>; rule: Record<string, number>; palaces: Record<string, PalaceRates> }
const OTHER = ['Phụ Mẫu', 'Phúc Đức', 'Điền Trạch', 'Quan Lộc', 'Nô Bộc', 'Thiên Di', 'Tật Ách', 'Tài Bạch', 'Tử Tức', 'Phu Thê', 'Huynh Đệ'];

export function baseRates(K: Knowledge, charts: any[]): BaseRates {
  const cc = new Map<string, number>(), rc = new Map<string, number>();
  const pc = new Map(OTHER.map(p => [p, { c: new Map<string, number>(), r: new Map<string, number>() }]));
  const inc = (m: Map<string, number>, k: string) => m.set(k, (m.get(k) ?? 0) + 1);
  for (const c of charts) {
    const base = c.facts.base;
    const findings = run(K.rules, K.sources, base).findings;
    new Set(findings.filter(f => f.subject === 'palace:Mệnh' || f.subject === 'chart').map(f => f.ruleId)).forEach(id => inc(rc, id));
    const { assertions } = lift(findings, K, base);
    const { resolved } = resolve(assertions, K);
    applyQualifiers(resolved, K, base);
    new Set(resolved.filter(r => (r.subject === 'palace:Mệnh' || r.subject === 'chart') && r.status !== 'voided' && r.stance === 'affirms')
      .map(r => r.concept)).forEach(id => inc(cc, id));
    for (const [p, m] of pc) {
      new Set(findings.filter(f => f.subject === `palace:${p}`).map(f => f.ruleId)).forEach(id => inc(m.r, id));
      new Set(resolved.filter(r => r.subject === `palace:${p}` && r.status !== 'voided' && r.stance === 'affirms').map(r => r.concept)).forEach(id => inc(m.c, id));
    }
  }
  const n = charts.length, rate = (m: Map<string, number>) => Object.fromEntries([...m.entries()].sort((a, b) => b[1] - a[1]).map(([k, v]) => [k, +(v / n).toFixed(4)]));
  return { charts: n, corpus: 'corpus1000.json.gz', concept: rate(cc), rule: rate(rc),
    palaces: Object.fromEntries([...pc.entries()].map(([p, m]) => [p, { concept: rate(m.c), rule: rate(m.r) }])) };
}

if (import.meta.main) {
  const K: Knowledge = JSON.parse(readFileSync(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'), 'utf8'));
  const corpus = JSON.parse(gunzipSync(readFileSync(join(ROOT, 'src', 'interpret', 'test', 'fixtures', 'corpus1000.json.gz'))).toString('utf8'));
  const br = baseRates(K, corpus);
  writeFileSync(join(ROOT, 'engine', 'data', 'kg', 'base_rates.json'), JSON.stringify(br, null, 1) + '\n');
  const top = Object.entries(br.concept).slice(0, 12).map(([k, v]) => `${k} ${(100 * v).toFixed(0)}%`).join(', ');
  console.log(`${br.charts} charts, ${Object.keys(br.concept).length} concepts, ${Object.keys(br.rule).length} rules; most common: ${top}`);
}
