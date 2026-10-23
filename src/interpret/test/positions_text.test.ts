// Every sentence that puts a star in a palace says what the chart has (audit 2026-10-22, owner review of 09/01/2002: "Với Tham Lang hãm ở cung
// Nô Bộc" while Tham Lang sits in Huynh Đệ). Over the reader's Tử Vi text (luận chapters, overview, vận hạn) of benchmark20, the reference
// charts and part of the corpus: "<star …> ở cung X" and "<star> tọa X" must name a star standing in X — a star the palace only borrows,
// or that reaches it by chiếu / hội / giáp, must be written as such ("mượn … từ cung đối", "chiếu", "hội", "giáp").
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import type { ChartInput, Knowledge } from '../types.ts';
import { luanReport } from '../prose/luan.ts';
import { proseThemes } from '../prose/themes.ts';
import { proseVanHan } from '../prose/vanhan.ts';
import { checkedOnly } from '../prose/checked.ts';
import { PROSE_VERSION, seedOf } from '../prose/chapter.ts';

const FX = join(import.meta.dirname, 'fixtures');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const REFS = JSON.parse(readFileSync(join(FX, 'deep_reference_charts.json'), 'utf8')) as Record<string, ChartInput>;
const bench = JSON.parse(readFileSync(join(FX, 'benchmark20.json'), 'utf8')) as Array<{ label: string; facts: ChartInput }>;
const corpus = JSON.parse(gunzipSync(readFileSync(join(FX, 'corpus1000.json.gz'))).toString()) as Array<{ facts: ChartInput }>;
const N = Number(process.env.POSITIONS_N ?? 150);
const charts: Array<[string, ChartInput]> = [['2002', JSON.parse(readFileSync(join(FX, 'ref_2002_01_09_kl.json'), 'utf8'))],
  ...Object.entries(REFS), ...bench.map(b => [b.label, b.facts] as [string, ChartInput]), ...corpus.slice(0, N).map((c, i) => [`corpus#${i}`, c.facts] as [string, ChartInput])];

const STARS = ['Tử Vi', 'Thiên Cơ', 'Thái Dương', 'Vũ Khúc', 'Thiên Đồng', 'Liêm Trinh', 'Thiên Phủ', 'Thái Âm', 'Tham Lang', 'Cự Môn', 'Thiên Tướng', 'Thiên Lương', 'Thất Sát',
  'Phá Quân', 'Kình Dương', 'Đà La', 'Hỏa Tinh', 'Linh Tinh', 'Địa Không', 'Địa Kiếp', 'Tả Phụ', 'Hữu Bật', 'Văn Xương', 'Văn Khúc', 'Thiên Khôi', 'Thiên Việt', 'Lộc Tồn',
  'Thiên Mã', 'Đại Hao', 'Tiểu Hao'];
const PALACES = ['Mệnh', 'Phụ Mẫu', 'Phúc Đức', 'Điền Trạch', 'Quan Lộc', 'Nô Bộc', 'Thiên Di', 'Tật Ách', 'Tài Bạch', 'Tử Tức', 'Phu Thê', 'Huynh Đệ'];
const ST = `(?:${STARS.join('|')})(?: hóa (?:Lộc|Quyền|Khoa|Kỵ))?(?: \\([^)]*\\))?`;
// a list of stars, then (optionally) a brightness, then "ở cung X"
const AT = new RegExp(`(?<![Ll]ưu )(${ST}(?:(?:, | và | cùng )${ST})*)(?: (?:ở thế |ở vào thế |rơi vào |đắc địa|hãm địa|hãm|đắc|miếu|vượng|bình hòa)[^,.;:]{0,12}?)? ở cung (${PALACES.join('|')})(?![\\p{L}])`, 'gu');
const SEAT = new RegExp(`(${STARS.join('|')}) tọa (${PALACES.join('|')})(?![\\p{L}])`, 'gu');
const NAMES = new RegExp(STARS.join('|'), 'g');

export function misplaced(f: ChartInput, text: string): string[] {
  const bad: string[] = [];
  const pal = (name: string) => f.palaces.find(p => p.name === name)!;
  const has = (p: ReturnType<typeof pal>, s: string) => p.stars.includes(s) || p.major_stars.includes(s);
  for (const m of text.matchAll(AT)) {
    const span = m[0], p = pal(m[2]);
    // the 40 characters before the list: "mượn …", "chiếu …", "hội …" write the relation, not a seat
    const before = text.slice(Math.max(0, m.index! - 40), m.index!);
    if (/mượn|chiếu|hội|giáp|xung/.test(span) || /mượn\s*$|mượn [^.]{0,30}$/.test(before)) continue;
    for (const s of span.match(NAMES) ?? []) if (!has(p, s)) bad.push(`${s} not in ${m[2]}: “${span}”`);
  }
  for (const m of text.matchAll(SEAT)) if (!pal(m[2]).major_stars.includes(m[1])) bad.push(`${m[1]} not seated in ${m[2]}: “${m[0]}”`);
  return bad;
}

test('a star said to stand in a palace stands there (borrowed, chiếu, hội and giáp are written as such)', () => {
  const bad: string[] = [];
  for (const [label, f] of charts) {
    const chs = [...luanReport(f, K, { allowDraft: true, deep: true }), ...proseThemes(f, K, PROSE_VERSION, { allowDraft: true, luan: true }),
      proseVanHan(f, K, seedOf(f), PROSE_VERSION, true)].map(c => checkedOnly(c as never) as { chapter: string; paragraphs: Array<{ sentences: Array<{ text: string }> }> });
    for (const c of chs) for (const p of c.paragraphs) for (const s of p.sentences) for (const b of misplaced(f, s.text)) bad.push(`${label}/${c.chapter}: ${b} — ${s.text}`);
  }
  assert.deepEqual(bad.slice(0, 8), [], `${bad.length} sentences`);
});

test('the owner chart: Nô Bộc (Mão, vô chính diệu) names Tham Lang as borrowed from Huynh Đệ, never as standing in Nô Bộc', () => {
  const f = charts[0][1];
  const nb = luanReport(f, K, { allowDraft: true, deep: true }).find(c => c.chapter === 'no_boc')!;
  const text = nb.paragraphs.flatMap(p => p.sentences.map(s => s.text)).join(' ');
  assert.ok(!/Tham Lang[^.]{0,20} ở cung Nô Bộc/.test(text), text);
  assert.ok(/mượn Tham Lang|Tham Lang mượn/.test(text), text);
});
