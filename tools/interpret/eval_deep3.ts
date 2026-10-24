// DEEP-3 depth / repetition / grounding measure (docs/audit/DEEP-3.md), per chapter, over the corpus, on what the reader gets (checkedOnly):
//   node tools/interpret/eval_deep3.ts [--n 1000] [--chapters tu_tuc,phu_mau,…] [--json out.json]
//   sentences     sentences per chart (median), share of charts with ≤3 sentences
//   frame_sys     share of sentences that are frame lines (trace.step frame:*) or system lines (basis he_thong / tong_hop)
//   grounded      share of sentences with basis sach and at least one cite (a book claim, not a restated fact)
//   dup5          share of sentences whose exact text appears in ≥5% of the charts (template lines)
//   skel5         the same with star / palace / branch / stem / number names masked (frame reuse)
//   cond          share of charts where the chapter states a condition ("nếu", "khi", "trừ khi", "miễn là", "với điều kiện")
//   inter         sentences naming two or more stars, per chart (stars read together, not one by one)
//   personal      share of sentences that name something of this chart (a star, palace, branch, stem, age, element)
// Bát Tự chapters are read through tools/interpret/bazi_deep_audit.ts reader(), with keys prefixed "bt:".
import { readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import type { ChartInput, Knowledge } from '../../src/interpret/types.ts';
import { proseAllChapters } from '../../src/interpret/route.ts';
import { checkedOnly } from '../../src/interpret/prose/checked.ts';
import { reader } from './bazi_deep_audit.ts';

const ROOT = join(import.meta.dirname, '..', '..');
const arg = (k: string, d: string) => process.argv.includes(k) ? process.argv[process.argv.indexOf(k) + 1] : d;
const K: Knowledge = JSON.parse(readFileSync(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'), 'utf8'));
const corpus = JSON.parse(gunzipSync(readFileSync(join(ROOT, 'src', 'interpret', 'test', 'fixtures', 'corpus1000.json.gz'))).toString()) as Array<{ facts: ChartInput }>;
const N = Number(arg('--n', '1000'));
const WANT = arg('--chapters', 'tu_tuc,phu_mau,no_boc,tai_bach,cach_cuc,bt:cach-cuc').split(',');

const STARS = ['Tử Vi', 'Thiên Cơ', 'Thái Dương', 'Vũ Khúc', 'Thiên Đồng', 'Liêm Trinh', 'Thiên Phủ', 'Thái Âm', 'Tham Lang', 'Cự Môn', 'Thiên Tướng', 'Thiên Lương',
  'Thất Sát', 'Phá Quân', 'Tả Phụ', 'Hữu Bật', 'Văn Xương', 'Văn Khúc', 'Thiên Khôi', 'Thiên Việt', 'Lộc Tồn', 'Thiên Mã', 'Kình Dương', 'Đà La', 'Hỏa Tinh', 'Linh Tinh',
  'Địa Không', 'Địa Kiếp', 'Hóa Lộc', 'Hóa Quyền', 'Hóa Khoa', 'Hóa Kỵ', 'Tuần', 'Triệt', 'Long Trì', 'Phượng Các', 'Hồng Loan', 'Đào Hoa', 'Thiên Hỷ', 'Thanh Long',
  'Thiên Hình', 'Thiên Riêu', 'Cô Thần', 'Quả Tú', 'Đại Hao', 'Tiểu Hao', 'Tang Môn', 'Bạch Hổ', 'Thiên Khốc', 'Thiên Hư', 'Ân Quang', 'Thiên Quý', 'Tam Thai', 'Bát Tọa'];
const OTHER = ['Mệnh', 'Phụ Mẫu', 'Phúc Đức', 'Điền Trạch', 'Quan Lộc', 'Nô Bộc', 'Thiên Di', 'Tật Ách', 'Tài Bạch', 'Tử Tức', 'Phu Thê', 'Huynh Đệ',
  'Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi', 'Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý',
  'Mộc', 'Hỏa', 'Thổ', 'Kim', 'Thủy', 'Tỉ Kiên', 'Kiếp Tài', 'Thực Thần', 'Thương Quan', 'Chính Tài', 'Thiên Tài', 'Chính Quan', 'Chính Ấn', 'Thiên Ấn', 'Tỉ Kiếp', 'Thực Thương', 'Quan Sát', 'Ấn'];
const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const NAMES = new RegExp([...STARS, ...OTHER].sort((a, b) => b.length - a.length).map(esc).join('|') + '|\\d+', 'gu');
const STAR_RE = STARS.map(s => new RegExp(`(^|[^\\p{L}])${esc(s)}([^\\p{L}]|$)`, 'u'));
const COND = /(^|[\s,(])(nếu|khi|trừ khi|miễn là|với điều kiện|chỉ khi|hễ)(\s)/iu;

type Sent = { text: string; trace: { basis?: string; step?: string; cites?: string[] } };
const sentsOf = (paras: Array<{ sentences: Sent[] }> | undefined) => (paras ?? []).flatMap(p => p.sentences);
const acc: Record<string, { charts: number; counts: number[]; frame: number; grounded: number; inter: number; personal: number; cond: number; texts: Map<string, number>; skel: Map<string, number>; all: string[][] }> = {};
for (const c of corpus.slice(0, N)) {
  const tv = proseAllChapters(c.facts, K, { allowDraft: true, deep: true, luan: true }).map(x => checkedOnly(x as never) as unknown as { chapter: string; paragraphs: Array<{ sentences: Sent[] }> });
  const bt = WANT.some(w => w.startsWith('bt:')) ? reader(c.facts) as Record<string, Array<{ sentences: Sent[] }>> : {};
  for (const w of WANT) {
    const ss = w.startsWith('bt:') ? sentsOf(bt[w.slice(3)]) : sentsOf(tv.find(x => x.chapter === w)?.paragraphs);
    const a = acc[w] ??= { charts: 0, counts: [], frame: 0, grounded: 0, inter: 0, personal: 0, cond: 0, texts: new Map(), skel: new Map(), all: [] };
    a.charts++; a.counts.push(ss.length);
    a.frame += ss.filter(s => /^frame/.test(s.trace.step ?? '') || s.trace.basis === 'he_thong' || s.trace.basis === 'tong_hop').length;
    a.grounded += ss.filter(s => s.trace.basis === 'sach' && (s.trace.cites?.length ?? 0) > 0).length;
    a.inter += ss.filter(s => STAR_RE.filter(r => r.test(s.text)).length >= 2).length;
    a.personal += ss.filter(s => { NAMES.lastIndex = 0; return NAMES.test(s.text); }).length;
    if (ss.some(s => COND.test(s.text))) a.cond++;
    const texts = [...new Set(ss.map(s => s.text))], skels = [...new Set(ss.map(s => s.text.replace(NAMES, '_')))];
    for (const t of texts) a.texts.set(t, (a.texts.get(t) ?? 0) + 1);
    for (const t of skels) a.skel.set(t, (a.skel.get(t) ?? 0) + 1);
    a.all.push(ss.map(s => s.text));
  }
}
const pct = (x: number) => +(100 * x).toFixed(1);
const median = (xs: number[]) => { const s = [...xs].sort((a, b) => a - b); return s[Math.floor(s.length / 2)] ?? 0; };
const out: Record<string, unknown> = {};
for (const [w, a] of Object.entries(acc)) {
  const total = a.counts.reduce((x, y) => x + y, 0) || 1, cut = Math.max(2, Math.ceil(0.05 * a.charts));
  const dupT = new Set([...a.texts].filter(([, n]) => n >= cut).map(([t]) => t)), dupS = new Set([...a.skel].filter(([, n]) => n >= cut).map(([t]) => t));
  let d5 = 0, s5 = 0;
  for (const xs of a.all) for (const t of xs) { if (dupT.has(t)) d5++; if (dupS.has(t.replace(NAMES, '_'))) s5++; }
  out[w] = { charts: a.charts, sentences_mean: +(total / a.charts).toFixed(1), sentences_median: median(a.counts), le3: pct(a.counts.filter(n => n <= 3).length / a.charts),
    frame_sys: pct(a.frame / total), grounded: pct(a.grounded / total), dup5: pct(d5 / total), skel5: pct(s5 / total), cond: pct(a.cond / a.charts),
    inter_per_chart: +(a.inter / a.charts).toFixed(2), personal: pct(a.personal / total),
    top: [...a.texts].sort((x, y) => y[1] - x[1]).slice(0, 5).map(([t, n]) => `${n}× ${t.slice(0, 110)}`) };
}
console.log(JSON.stringify(out, null, 1));
if (process.argv.includes('--json')) writeFileSync(arg('--json', 'deep3.json'), JSON.stringify(out, null, 1));
