// Corpus evaluation of the interpretation pipeline over the regression charts: per chapter and chart, length, evidence, quality checks,
// CPU time, and how much content is shared between charts (a template that fires identically everywhere is filler).
//   node tools/interpret/evaluate.ts                 summary table on stdout
//   node tools/interpret/evaluate.ts --md out.md     also writes the markdown report
//   node tools/interpret/evaluate.ts --chart 3 menh  prints one chapter (text + warnings), for reading
import { readFileSync, writeFileSync } from 'node:fs';
import { interpret, prepare, CHAPTERS, type Chapter, type ChapterOutput } from '../../src/interpret/pipeline.ts';
import type { Knowledge } from '../../src/interpret/types.ts';

const K: Knowledge = JSON.parse(readFileSync('src/interpret/generated/knowledge.json', 'utf8'));
const charts = JSON.parse(readFileSync('src/interpret/test/fixtures/charts.json', 'utf8'));
const args = process.argv.slice(2);

if (args[0] === '--chart') {
  const c = charts[Number(args[1])], only = args[2];
  for (const ch of CHAPTERS) {
    if (only && ch !== only) continue;
    const o = interpret(c.facts, ch, K);
    console.log(`\n=========== ${o.title} (${o.quality.metrics.words} words, pass=${o.quality.pass}) — ${c.label} ===========`);
    for (const p of o.paragraphs) console.log(`\n### ${p.title}\n${p.text}`);
    if (o.quality.errors.length) console.log('ERRORS', JSON.stringify(o.quality.errors));
    if (o.quality.warnings.length) console.log('WARN', o.quality.warnings.map(w => `${w.check}: ${w.detail}`).join('\n'));
  }
  process.exit(0);
}

interface Row { chart: number; label: string; chapter: Chapter; words: number; grounds: number; pass: boolean; warnings: string[]; errors: string[]; ms: number; content: Set<string> }
const rows: Row[] = [], prepMs: number[] = [];
for (const [i, c] of charts.entries()) {
  // rule inference + evidence + chart graph, shared by all chapters of a chart: timed on its own
  const p0 = performance.now(); prepare(c.facts, K); prepMs.push(performance.now() - p0);
  for (const ch of CHAPTERS) {
    const t0 = performance.now();
    const o: ChapterOutput = interpret(c.facts, ch, K);
    const ms = performance.now() - t0;
    rows.push({ chart: i, label: c.label, chapter: ch, words: o.quality.metrics.words, grounds: o.quality.metrics.independentGrounds ?? 0, pass: o.quality.pass,
      warnings: o.quality.warnings.map(w => w.check), errors: o.quality.errors.map(e => e.check), ms,
      content: new Set(o.paragraphs.flatMap(p => p.sentences.filter(s => ['claim', 'contrast', 'interaction'].includes(s.kind)).map(s => s.text))) });
  }
}

const lines: string[] = [];
const out = (s = '') => { lines.push(s); console.log(s); };
out(`# Đánh giá trên ${charts.length} lá số × ${CHAPTERS.length} chương (${K.version})`);
out();
out('| chương | số chữ (min / trung vị / max) | căn cứ độc lập (trung vị) | đạt | cảnh báo | câu sách trùng nguyên văn giữa hai lá số (trung vị / max) | CPU ms (trung vị / max) |');
out('|---|---|---|---|---|---|---|');
const med = (xs: number[]) => { const s = [...xs].sort((a, b) => a - b); return s.length ? s[Math.floor(s.length / 2)] : 0; };
for (const ch of CHAPTERS) {
  const rs = rows.filter(r => r.chapter === ch);
  const w = rs.map(r => r.words), g = rs.map(r => r.grounds), ms = rs.map(r => r.ms);
  const warn = new Map<string, number>();
  for (const r of rs) for (const x of r.warnings) warn.set(x, (warn.get(x) ?? 0) + 1);
  // share of one chart's book sentences (claim / contrast with a quote) found word for word in another chart's chapter; pairs where the
  // first chapter has fewer than 5 such sentences are skipped (one common reading would read as 100%)
  const shares: number[] = [];
  for (let a = 0; a < rs.length; a++) for (let b = 0; b < rs.length; b++) {
    const A = rs[a].content, B = rs[b].content; if (a === b || A.size < 5) continue;
    shares.push([...A].filter(x => B.has(x)).length / A.size);
  }
  const maxShare = shares.length ? Math.max(...shares) : 0, medShare = med(shares);
  out(`| ${ch} | ${Math.min(...w)} / ${med(w)} / ${Math.max(...w)} | ${med(g)} | ${rs.filter(r => r.pass).length}/${rs.length} | ${[...warn].map(([k, v]) => `${k}×${v}`).join(', ') || '—'} | ${(medShare * 100).toFixed(0)}% / ${(maxShare * 100).toFixed(0)}% | ${med(ms).toFixed(1)} / ${Math.max(...ms).toFixed(1)} |`);
}
out();
out(`Suy luận dùng chung cho mọi chương của một lá số (luật + bằng chứng + đồ thị): trung vị ${med(prepMs).toFixed(1)} ms, max ${Math.max(...prepMs).toFixed(1)} ms; cột CPU ở trên là phần riêng của từng chương (Node ${process.version}, máy phát triển; số đo trên Worker sẽ khác).`);
out();
const bad = rows.filter(r => r.errors.length || r.warnings.length);
if (bad.length) {
  out('## Chương có cảnh báo hoặc lỗi');
  out();
  for (const r of bad) out(`- lá số ${r.chart} (${r.label}), ${r.chapter}: ${[...r.errors.map(e => `LỖI ${e}`), ...r.warnings].join(', ')} — ${r.words} chữ, ${r.grounds} căn cứ`);
}
const mi = args.indexOf('--md');
if (mi >= 0) writeFileSync(args[mi + 1], lines.join('\n') + '\n');
