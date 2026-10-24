// REVIEW-19 W6 measure: how much of the Bát Tự short reading (the paragraphs outside the Đọc sâu / Số liệu folds) is calculation, over a corpus
// of facts, and how often the combinations, the money weighing and the group lines reach the text.
//   node tools/interpret/bazi_main_share.ts [corpus.json.gz] [--json out.json]
// tinh_toan share = sentences of basis tinh_toan / all sentences of the short reading (sach, tinh_toan, he_thong, tong_hop, minh_hoa).
import { readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import { reader } from './bazi_deep_audit.ts';
import type { ChartInput } from '../../src/interpret/types.ts';
import type { ProseParagraph } from '../../src/interpret/prose/realize.ts';

const ROOT = join(import.meta.dirname, '..', '..');
const arg = process.argv[2] && !process.argv[2].startsWith('--') ? process.argv[2] : join(ROOT, 'src', 'interpret', 'test', 'fixtures', 'corpus1000.json.gz');
const raw = readFileSync(arg);
const corpus = JSON.parse((arg.endsWith('.gz') ? gunzipSync(raw) : raw).toString('utf8')) as Array<{ label: string; facts: ChartInput }>;
const per: Record<string, { n: number; t: number }> = {};
let N = 0, T = 0, combo = 0, comboCharts = 0, weigh = 0, groups = 0, perChart: number[] = [];
for (const c of corpus) {
  const ch = reader(c.facts);
  let n = 0, t = 0, hasCombo = false;
  for (const [id, ps] of Object.entries(ch)) for (const p of (ps ?? []) as ProseParagraph[]) {
    for (const s of p.sentences) {
      if (/^kin:pt:/.test(s.trace.step ?? '')) { combo++; hasCombo = true; }
      if (s.trace.step === 'kin:tai_weigh') weigh++;
      if (/^BT_TVHK_G\d+$/.test(s.trace.rules[0] ?? '')) groups++;
    }
    if (p.depth === 'sau') continue;
    const e = (per[id] ??= { n: 0, t: 0 });
    for (const s of p.sentences) { e.n++; n++; if (s.trace.basis === 'tinh_toan') { e.t++; t++; } }
  }
  N += n; T += t; perChart.push(n ? t / n : 0); if (hasCombo) comboCharts++;
}
perChart.sort((a, b) => a - b);
const pc = (a: number, b: number) => b ? +(100 * a / b).toFixed(1) : 0;
const res = { charts: corpus.length, main_sentences_per_chart: +(N / corpus.length).toFixed(1), tinh_toan_share: pc(T, N),
  median_chart_share: +(100 * perChart[Math.floor(perChart.length / 2)]).toFixed(1), p90_chart_share: +(100 * perChart[Math.floor(perChart.length * 0.9)]).toFixed(1),
  per_chapter: Object.fromEntries(Object.entries(per).map(([k, v]) => [k, { sentences: +(v.n / corpus.length).toFixed(1), tinh_toan_share: pc(v.t, v.n) }])),
  charts_with_a_combination: comboCharts, combination_sentences: combo, money_weighing_sentences: weigh, group_line_sentences: groups };
console.log(JSON.stringify(res, null, 1));
const j = process.argv.indexOf('--json');
if (j > 0) writeFileSync(process.argv[j + 1], JSON.stringify(res, null, 1) + '\n');
