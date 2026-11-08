// Cross-report invariants over the corpus (plan THIEN-BAN-33 G-INV): counts violations per invariant on the whole report as the reader gets
// it (proseAllChapters + checkedOnly).
//   node tools/interpret/eval_invariants.ts [--n 300] [--show 20] [--inv INV-1]
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import type { ChartInput, Knowledge } from '../../src/interpret/types.ts';
import { proseAllChapters } from '../../src/interpret/route.ts';
import { checkedOnly } from '../../src/interpret/prose/checked.ts';
import { checkInvariants, sentencesOf, type Violation } from '../../src/interpret/invariants.ts';

const arg = (k: string, d: string) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const FX = 'src/interpret/test/fixtures';
const K: Knowledge = JSON.parse(readFileSync('src/interpret/generated/knowledge.json', 'utf8'));
const refs: Array<[string, ChartInput]> = [['owner_2002', JSON.parse(readFileSync(join(FX, 'owner_2002_kl_2026-11.json'), 'utf8'))],
  ['site_1990', JSON.parse(readFileSync(join(FX, 'site_sample_1990.json'), 'utf8'))]];
const corpus = (JSON.parse(gunzipSync(readFileSync(join(FX, 'corpus1000.json.gz'))).toString()) as Array<{ facts: ChartInput }>).slice(0, Number(arg('--n', '300')));
const only = arg('--inv', ''), show = Number(arg('--show', '15'));
const all: Array<Violation & { label: string }> = [];
let n = 0;
const t0 = Date.now();
for (const [label, f] of [...refs, ...corpus.map((c, i) => [`corpus#${i}`, c.facts] as [string, ChartInput])]) {
  const chs = proseAllChapters(f, K, { allowDraft: true, deep: true, luan: true }).map(c => checkedOnly(c as never, f, K)) as never;
  n += sentencesOf(chs).length;
  for (const v of checkInvariants(f, chs)) if (!only || v.inv === only) all.push({ ...v, label });
}
const by = new Map<string, number>();
for (const v of all) by.set(v.inv, (by.get(v.inv) ?? 0) + 1);
console.log(`${refs.length + corpus.length} charts, ${n} sentences, ${((Date.now() - t0) / 1000).toFixed(0)} s`);
for (const [k, c] of [...by].sort()) console.log(`${k}: ${c}`);
for (const v of all.slice(0, show)) console.log(`✖ ${v.inv} ${v.label}/${v.chapter}: ${v.why} | ${v.text.slice(0, 160)}`);
if (!all.length) console.log('ok');
