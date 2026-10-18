// Writes the example chapters of a corpus chart as Markdown (output exactly as the pipeline produces it, with provenance and the
// automated quality report):  node tools/interpret/example.ts [chart-index] [outdir]
import { writeFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { interpret, CHAPTERS, ENGINE_VERSION } from '../../src/interpret/pipeline.ts';
import { loadCorpus } from './sweep.ts';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const idx = Number(process.argv[2] ?? 0), out = process.argv[3] ?? join(ROOT, 'docs', 'examples');
const k = JSON.parse(readFileSync(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'), 'utf8'));
const c = loadCorpus()[idx], b = c.birth;
const slug = `${String(b.day).padStart(2, '0')}-${String(b.month).padStart(2, '0')}-${b.year}`;
const FILE: Record<string, string> = { cong_danh: 'cong-danh', tai_bach: 'tai-bach', menh: 'menh' };
mkdirSync(out, { recursive: true });
for (const ch of CHAPTERS) {
  const o = interpret(c.facts, ch, k), m = o.quality.metrics;
  const rows = o.paragraphs.flatMap(p => p.sentences.map(s => `| ${p.module}/${s.passage} | ${s.basis} | ${s.rules.join(', ') || '—'} |`));
  const md = [
    `# ${o.title} — lá số ${b.day}/${b.month}/${b.year} ${b.hour}:${String(b.minute).padStart(2, '0')} (${b.gender === 'male' ? 'nam' : 'nữ'})`, '',
    `Đầu ra nguyên văn của pipeline (\`${ENGINE_VERSION}\`, knowledge \`${o.kbVersion}\`), tạo bằng \`node tools/interpret/example.ts ${idx}\`. Không có mô hình ngôn ngữ nào tham gia; chạy lại cho đúng từng chữ.`, '',
    `> **Trạng thái biên tập:** ${o.quality.editorial.notice} Các con số dưới đây là **kiểm tra tự động**, không phải thẩm định chuyên gia.`, '', '---', '',
    ...o.paragraphs.flatMap(p => [`### ${p.title}`, '', p.text, '']), '---', '',
    '## Kiểm tra tự động', '',
    '| Chỉ số | Giá trị |', '|---|---|',
    `| Kết quả | ${o.quality.pass ? 'đạt' : 'không đạt'} — ${o.quality.errors.length} lỗi, ${o.quality.warnings.length} cảnh báo${o.quality.warnings.length ? ' (' + o.quality.warnings.map(w => w.check).join(', ') + ')' : ''} |`,
    `| Số chữ | ${m.words} |`, `| Câu / đoạn | ${m.sentences} / ${m.paragraphs} |`, `| Căn cứ độc lập | ${m.independentGrounds} (≈ ${m.wordsPerGround} chữ / căn cứ) |`,
    `| Câu theo nguồn | ${Object.entries(m.bySource).map(([s, n]) => `${s} ${n}`).join(' · ')} |`, `| Tỉ lệ 4-gram lặp | ${m.repeated4gramRate} |`,
    `| Tỉ lệ câu gắn với dữ kiện riêng | ${m.personalization} |`,
    `| Truy vết | ${o.trace.fired} quy tắc kích hoạt (${o.trace.verified} đã đối chiếu), ${o.trace.evidence} bằng chứng, đồ thị ${o.trace.graph.nodes} nút / ${o.trace.graph.edges} cạnh |`, '',
    '## Truy vết từng câu', '', '| Module / passage | Loại | Quy tắc |', '|---|---|---|', ...rows, '',
  ].join('\n');
  writeFileSync(join(out, `${FILE[ch]}-${slug}.md`), md);
  console.log(join(out, `${FILE[ch]}-${slug}.md`), m.words, 'words', o.quality.pass ? 'pass' : 'FAIL');
}
