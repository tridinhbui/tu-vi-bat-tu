// Writes every chapter of one corpus chart as a Markdown report (output exactly as the pipeline produces it, with the automated checks):
//   node tools/interpret/report.ts <chart-index> <out.md> [--sweep]
import { readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { interpret, CHAPTERS, ENGINE_VERSION } from '../../src/interpret/pipeline.ts';
const [idx, out] = [Number(process.argv[2] ?? 0), process.argv[3] ?? 'report.md'];
const K = JSON.parse(readFileSync('src/interpret/generated/knowledge.json', 'utf8'));
const charts = JSON.parse(readFileSync('src/interpret/test/fixtures/charts.json', 'utf8'));
if (process.argv.includes('--sweep')) charts.push(...JSON.parse(gunzipSync(readFileSync('src/interpret/test/fixtures/sweep.json.gz')).toString('utf8')));
const c = charts[idx], b = c.birth ?? {};
const lines = [`# Báo cáo mẫu — ${c.label}${b.year ? ` (${b.day}/${b.month}/${b.year} ${b.hour}:${String(b.minute ?? 0).padStart(2, '0')}, ${b.gender === 'male' ? 'nam' : 'nữ'})` : ''}`, '',
  `Đầu ra nguyên văn của pipeline (\`${ENGINE_VERSION}\`, knowledge \`${K.version}\`), không có mô hình ngôn ngữ nào tham gia; chạy lại cho đúng từng chữ.`,
  '> **Trạng thái biên tập:** mọi module nội dung đang ở trạng thái nháp, chưa có chuyên gia duyệt. Các chỉ số dưới đây là kiểm tra tự động, không phải thẩm định chuyên gia.', ''];
for (const ch of CHAPTERS) {
  const o = interpret(c.facts, ch, K), m = o.quality.metrics;
  lines.push(`## ${o.title}`, '', `*${m.words} chữ · ${o.quality.pass ? 'đạt' : 'KHÔNG đạt'} kiểm tra tự động · cảnh báo: ${o.quality.warnings.map(w => w.check).join(', ') || 'không'} · căn cứ độc lập: ${m.independentGrounds ?? 0}*`, '');
  for (const p of o.paragraphs) lines.push(`### ${p.title}`, '', p.text, '');
}
writeFileSync(out, lines.join('\n'));
console.log(out, lines.length, 'lines');
