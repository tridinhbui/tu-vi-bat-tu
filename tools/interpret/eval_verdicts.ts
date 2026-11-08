// Domain verdict distribution over the corpus (plan THIEN-BAN-33 G4): how often a domain ends "chưa phân xử", and the weighing reasons.
//   node tools/interpret/eval_verdicts.ts [--n 300]
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import type { ChartInput, Knowledge } from '../../src/interpret/types.ts';
import { infer } from '../../src/interpret/prose/chapter.ts';
import { buildLedger } from '../../src/interpret/reason/ledger.ts';
const arg = (k: string, d: string) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const K: Knowledge = JSON.parse(readFileSync('src/interpret/generated/knowledge.json', 'utf8'));
const corpus = (JSON.parse(gunzipSync(readFileSync('src/interpret/test/fixtures/corpus1000.json.gz')).toString()) as Array<{ facts: ChartInput }>).slice(0, Number(arg('--n', '300')));
const by = new Map<string, number>(), why = new Map<string, number>();
let n = 0, twoSided = 0;
for (const c of corpus) for (const v of buildLedger(c.facts, K, infer(c.facts, K).resolved).domains) {
  if (v.verdict === 'khong_ket_luan') continue;
  n++; by.set(v.verdict, (by.get(v.verdict) ?? 0) + 1);
  if (v.pos.length && v.neg.length) twoSided++;
  for (const w of v.weigh?.why ?? []) why.set(w.kind, (why.get(w.kind) ?? 0) + 1);
  if (v.link?.kind === 'weigh' && (v.weigh?.why ?? []).every(w => w.kind === 'count')) why.set('count_only', (why.get('count_only') ?? 0) + 1);
}
console.log(`${corpus.length} charts, ${n} domain verdicts (health excluded), two-sided ${twoSided}`);
for (const [k, c] of [...by].sort((a, b) => b[1] - a[1])) console.log(`${k.padEnd(14)} ${c} (${(100 * c / n).toFixed(1)}%)`);
console.log('weigh reasons', Object.fromEntries(why));
