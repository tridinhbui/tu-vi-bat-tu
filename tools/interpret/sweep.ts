// Sweep report over the regression charts (charts.json) and the coverage corpus (sweep.json.gz):
//   node tools/interpret/sweep.ts [chapter] [--json]
// Per chart: quality pass, warnings, words, independent grounds, CPU ms. Across charts: sentence SKELETONS (quotes, parentheticals,
// star / palace names, numbers removed) that recur — the template patterns a reader of several charts would notice — and the share
// of each chapter made of skeletons found in more than half of the charts.
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { interpret, CHAPTERS, type Chapter } from '../../src/interpret/pipeline.ts';
import type { Knowledge } from '../../src/interpret/types.ts';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const FX = join(ROOT, 'src', 'interpret', 'test', 'fixtures');
export function loadCorpus(): Array<{ label: string; facts: any }> {
  const reg = JSON.parse(readFileSync(join(FX, 'charts.json'), 'utf8'));
  const sweep = JSON.parse(gunzipSync(readFileSync(join(FX, 'sweep.json.gz'))).toString('utf8'));
  return [...reg, ...sweep];
}
const NAMES = /(Tử Vi|Thiên Cơ|Thái Dương|Vũ Khúc|Thiên Đồng|Liêm Trinh|Thiên Phủ|Thái Âm|Tham Lang|Cự Môn|Thiên Tướng|Thiên Lương|Thất Sát|Phá Quân|Kình Dương|Đà La|Hỏa Tinh|Linh Tinh|Địa Không|Địa Kiếp|Tả Phụ|Hữu Bật|Văn Xương|Văn Khúc|Thiên Khôi|Thiên Việt|Lộc Tồn|Thiên Mã|Hóa (Lộc|Quyền|Khoa|Kỵ)|Mệnh|Phụ Mẫu|Phúc Đức|Điền Trạch|Quan Lộc|Nô Bộc|Thiên Di|Tật Ách|Tài Bạch|Tử Tức|Phu Thê|Huynh Đệ|Tý|Sửu|Dần|Mão|Thìn|Tỵ|Ngọ|Mùi|Thân|Dậu|Tuất|Hợi|Giáp|Ất|Bính|Đinh|Mậu|Kỷ|Canh|Tân|Nhâm|Quý)/g;
export const skeleton = (s: string) => s.replace(/“[^”]*”/g, 'Q').replace(/\([^()]*(\([^()]*\)[^()]*)*\)/g, '').replace(NAMES, 'X')
  .replace(/\d+([–-]\d+)?/g, 'N').replace(/\b(X)( (và|,) X)+/g, 'X').replace(/\s+/g, ' ').trim();

export function sweep(chapter: Chapter, k: Knowledge) {
  const corpus = loadCorpus(), rows: any[] = [], skel = new Map<string, Set<number>>(), outs: any[] = [];
  corpus.forEach((c, i) => {
    const t0 = performance.now(); const o = interpret(c.facts, chapter, k); const ms = performance.now() - t0;
    outs.push(o);
    const sents = o.paragraphs.flatMap(p => p.sentences);
    for (const s of sents) { const key = skeleton(s.text); if (!skel.has(key)) skel.set(key, new Set()); skel.get(key)!.add(i); }
    rows.push({ i, label: c.label, pass: o.quality.pass, errors: o.quality.errors.map(e => e.check), warnings: o.quality.warnings.map(w => w.check),
      words: o.quality.metrics.words, grounds: o.quality.metrics.independentGrounds, ms: Math.round(ms) });
  });
  const n = corpus.length, common = new Set([...skel].filter(([, s]) => s.size > n / 2).map(([k]) => k));
  outs.forEach((o, i) => { const sents = o.paragraphs.flatMap((p: any) => p.sentences); rows[i].boilerplate = sents.length ? +(sents.filter((s: any) => common.has(skeleton(s.text))).length / sents.length).toFixed(2) : 0; });
  const recurring = [...skel].map(([k, s]) => ({ skeleton: k, charts: s.size })).filter(x => x.charts >= Math.max(3, n * 0.25)).sort((a, b) => b.charts - a.charts);
  return { n, rows, recurring, outs };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const chapter = (process.argv[2] && !process.argv[2].startsWith('--') ? process.argv[2] : 'cong_danh') as Chapter;
  if (!CHAPTERS.includes(chapter)) throw new Error(`chapter must be one of ${CHAPTERS.join(', ')}`);
  const k = JSON.parse(readFileSync(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'), 'utf8'));
  const r = sweep(chapter, k);
  if (process.argv.includes('--json')) { console.log(JSON.stringify({ ...r, outs: undefined }, null, 1)); process.exit(0); }
  const w = r.rows.map(x => x.words).sort((a, b) => a - b);
  console.log(`${chapter}: ${r.n} charts; pass ${r.rows.filter(x => x.pass).length}; errors ${r.rows.reduce((s, x) => s + x.errors.length, 0)}; ` +
    `warnings ${JSON.stringify(r.rows.flatMap(x => x.warnings).reduce((m: any, x: string) => (m[x] = (m[x] ?? 0) + 1, m), {}))}`);
  console.log(`words min ${w[0]} median ${w[w.length >> 1]} max ${w[w.length - 1]}; ms median ${r.rows.map(x => x.ms).sort((a, b) => a - b)[r.n >> 1]} max ${Math.max(...r.rows.map(x => x.ms))}`);
  console.log(`boilerplate share median ${r.rows.map(x => x.boilerplate).sort((a, b) => a - b)[r.n >> 1]} max ${Math.max(...r.rows.map(x => x.boilerplate))}`);
  console.log('recurring skeletons (≥25% of charts):');
  for (const x of r.recurring.slice(0, 40)) console.log(`  ${x.charts}/${r.n}  ${x.skeleton.slice(0, 170)}`);
  for (const x of r.rows.filter(x => !x.pass || x.warnings.length)) console.log('  chart', x.i, x.label, x.errors, x.warnings, x.words);
}
