// Mệnh reader-prose evaluation over the 1,000-chart corpus (prose plan §6). Writes docs/examples/prose-eval-1000.md:
//   node tools/interpret/eval_prose.ts [--n 1000]
// Automatic measures only (correctness by construction + surface statistics); blind human rating and the expert gold set are separate.
import { readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import { proseChapter, type ProseChapter, type ProseChapterId } from '../../src/interpret/prose/chapter.ts';
import type { Knowledge } from '../../src/interpret/types.ts';

const ROOT = join(import.meta.dirname, '..', '..');
const K: Knowledge = JSON.parse(readFileSync(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'), 'utf8'));
const corpus = JSON.parse(gunzipSync(readFileSync(join(ROOT, 'src', 'interpret', 'test', 'fixtures', 'corpus1000.json.gz'))).toString('utf8'));
const n = Number(process.argv[process.argv.indexOf('--n') + 1]) || corpus.length;
const CH = (process.argv.includes('--chapter') ? process.argv[process.argv.indexOf('--chapter') + 1] : 'menh') as ProseChapterId;

export interface ProseEval {
  charts: number; errors: Record<string, number>; empty: number; pass: number;
  sentLenOk: number; rep4Max: number; rep4Mean: number; topOpener: [string, number]; topFirstOpener: [string, number];
  jaccardMedian: number; schemaEntropy: number; schemaMax: number; schemas: Record<string, number>; variantOveruse: Array<[string, number]>;
  msMean: number; msP95: number; samples: Array<{ birth: unknown; text: string; schema: string }>;
}

const grams = (t: string) => { const w = t.toLowerCase().replace(/[.,;:!?]/g, '').split(/\s+/).filter(Boolean); const s = new Set<string>(); for (let i = 0; i + 4 <= w.length; i++) s.add(w.slice(i, i + 4).join(' ')); return s; };
const jac = (a: Set<string>, b: Set<string>) => { let i = 0; for (const x of a) if (b.has(x)) i++; return i / Math.max(1, a.size + b.size - i); };

export function evaluate(charts: any[], chapter: ProseChapterId = 'menh'): ProseEval {
  const outs: Array<{ c: any; o: ProseChapter; ms: number }> = [];
  for (const c of charts) { const t0 = performance.now(); const o = proseChapter(c.facts, K, chapter, { allowDraft: true }); outs.push({ c, o, ms: performance.now() - t0 }); }
  const errors: Record<string, number> = {};
  for (const { o } of outs) for (const i of o.issues) if (i.level === 'error') errors[i.code] = (errors[i.code] ?? 0) + 1;
  const sentLenOk = outs.filter(({ o }) => o.metrics.meanSentenceWords >= 18 && o.metrics.meanSentenceWords <= 35 && o.metrics.sdSentenceWords >= 6).length;
  const reps = outs.map(({ o }) => o.metrics.repeated4gramRate);
  const count = (xs: string[]) => { const m = new Map<string, number>(); xs.forEach(x => m.set(x, (m.get(x) ?? 0) + 1)); return [...m.entries()].sort((a, b) => b[1] - a[1]); };
  const allOpen = count(outs.flatMap(({ o }) => o.metrics.openers.map(x => x.toLowerCase())));
  const firstOpen = count(outs.map(({ o }) => (o.metrics.openers[0] ?? '').toLowerCase()));
  // diversity: charts sharing the same nucleus concept and the same Mệnh stars should still read differently
  const groups = new Map<string, Array<Set<string>>>();
  for (const { c, o } of outs) {
    const nuc = o.paragraphs[0]?.sentences.find(s => s.trace.move === 'ANCHOR' || s.trace.move === 'BORROW')?.trace.concepts[0] ?? '-';
    const key = `${nuc}|${c.facts.palaces.find((p: any) => p.name === o.palace).major_stars.join('+')}`;
    (groups.get(key) ?? groups.set(key, []).get(key)!).push(grams(o.paragraphs[0]?.text ?? ''));
  }
  const js: number[] = [];
  for (const g of groups.values()) for (let i = 0; i < g.length && i < 12; i++) for (let j = i + 1; j < g.length && j < 12; j++) js.push(jac(g[i], g[j]));
  js.sort((a, b) => a - b);
  const sch = count(outs.map(({ o }) => o.schema));
  const tot = outs.length, H = -sch.reduce((a, [, k]) => a + (k / tot) * Math.log(k / tot), 0);
  // a variant (whole fragment) used in more than 15 % of the chapters where it could appear
  const vcount = count(outs.flatMap(({ o }) => o.paragraphs.flatMap(p => p.sentences.map(s => s.text.replace(/^[^,]{0,25},\s*/, '').slice(0, 60)))));
  const ms = outs.map(x => x.ms).sort((a, b) => a - b);
  return {
    charts: tot, errors, empty: outs.filter(({ o }) => !o.paragraphs.length).length, pass: outs.filter(({ o }) => o.pass).length,
    sentLenOk, rep4Max: Math.max(...reps), rep4Mean: +(reps.reduce((a, b) => a + b, 0) / tot).toFixed(3),
    topOpener: [allOpen[0][0], +(allOpen[0][1] / allOpen.reduce((a, [, k]) => a + k, 0)).toFixed(3)],
    topFirstOpener: [firstOpen[0][0], +(firstOpen[0][1] / tot).toFixed(3)],
    jaccardMedian: +(js[Math.floor(js.length / 2)] ?? 0).toFixed(3), schemaEntropy: +H.toFixed(3), schemaMax: +Math.log(sch.length).toFixed(3),
    schemas: Object.fromEntries(sch), variantOveruse: vcount.filter(([, k]) => k / tot > 0.15).slice(0, 10).map(([v, k]) => [v, +(k / tot).toFixed(2)]),
    msMean: +(ms.reduce((a, b) => a + b, 0) / tot).toFixed(2), msP95: +ms[Math.floor(tot * 0.95)].toFixed(2),
    samples: outs.filter((_, i) => i % Math.max(1, Math.floor(tot / 12)) === 0).slice(0, 12).map(({ c, o }) => ({ birth: c.birth, text: o.text, schema: o.schema })),
  };
}

if (import.meta.main) {
  const e = evaluate(corpus.slice(0, n), CH);
  const md = [`# Đánh giá văn đọc chương ${CH} trên ${e.charts} lá số`, '', `Sinh bởi \`tools/interpret/eval_prose.ts --chapter ${CH}\` (prose ${'prose-0.2.0'}, knowledge \`${K.version}\`). Toàn bộ thẻ văn đang là bản nháp (allowDraft); các chỉ số là kiểm tra tự động, chưa phải chấm của người đọc hay chuyên gia.`, '',
    '| Chỉ số | Giá trị | Ngưỡng (plan §6) |', '|---|---|---|',
    `| Chương không lỗi chặn | ${e.pass}/${e.charts} | 100% |`, `| Lỗi chặn theo loại | ${JSON.stringify(e.errors)} | 0 |`, `| Chương rỗng | ${e.empty} | 0 |`,
    `| Độ dài câu TB 18–35 chữ và độ lệch ≥ 6 | ${(100 * e.sentLenOk / e.charts).toFixed(1)}% | ≥ 95% |`,
    `| 4-gram lặp trong một chương (TB / max) | ${e.rep4Mean} / ${e.rep4Max} | < 0.05 |`,
    `| Opener phổ biến nhất (mọi câu) | “${e.topOpener[0]}” ${(100 * e.topOpener[1]).toFixed(1)}% | ≤ 8% |`,
    `| Opener phổ biến nhất (câu đầu chương) | “${e.topFirstOpener[0]}” ${(100 * e.topFirstOpener[1]).toFixed(1)}% | (theo dõi) |`,
    `| Jaccard 4-gram đoạn 1, cùng nucleus và cùng chính tinh (trung vị) | ${e.jaccardMedian} | ≤ 0.35 |`,
    `| Entropy phân bố schema | ${e.schemaEntropy} / log(${Object.keys(e.schemas).length}) = ${e.schemaMax} | ≥ 0.7 × log(số schema dùng được) |`,
    `| Câu/đoạn mở dùng > 15% số chương | ${e.variantOveruse.length} | 0 |`,
    `| Thời gian sinh một chương (TB / p95, Node) | ${e.msMean} ms / ${e.msP95} ms | p95 < 30 ms |`, '',
    `Schema: ${Object.entries(e.schemas).map(([k, v]) => `${k} ${v}`).join(', ')}`, '',
    e.variantOveruse.length ? `Câu dùng quá nhiều: ${e.variantOveruse.map(([v, k]) => `“${v}…” ${k}`).join('; ')}` : '', '', '## Mẫu', '',
    ...e.samples.flatMap(s => [`### ${JSON.stringify(s.birth)} · ${s.schema}`, '', s.text, ''])].join('\n');
  writeFileSync(join(ROOT, 'docs', 'examples', CH === 'menh' ? 'prose-eval-1000.md' : `prose-eval-1000-${CH}.md`), md);
  console.log(JSON.stringify({ ...e, samples: undefined }, null, 1));
}
