// A corroboration ("Nhìn sang Tài Bạch, … cũng cùng chiều ấy") points at the sentence before it, so (owner review 2026-11-06, the site's
// sample chart 17/05/1990 10:30 nam, facts in fixtures/site_sample_1990.json):
//   - it follows the sentence of its own concept, never a turn toward the other side told in between;
//   - a reading said with its own limit ("kiếm được tiền, song không dư dả") is not "confirmed" by an unlimited one ("vàng ngọc đầy nhà"):
//     that one is told as the better side.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import type { Knowledge } from '../types.ts';
import { proseAllChapters } from '../route.ts';
import type { ProseParagraph } from '../prose/realize.ts';

const FX = join(import.meta.dirname, 'fixtures');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const sample = JSON.parse(readFileSync(join(FX, 'site_sample_1990.json'), 'utf8'));
const corpus = (JSON.parse(gunzipSync(readFileSync(join(FX, 'corpus1000.json.gz'))).toString()) as Array<{ facts: any }>).slice(0, 30);
type Ch = { chapter: string; paragraphs: ProseParagraph[] };
const read = (f: any) => proseAllChapters(f, K, { allowDraft: true, deep: true, luan: true }) as unknown as Ch[];
const AGREE = /cùng chiều ấy|xác nhận thêm|cũng nói như vậy|cho cùng một chiều|có chỗ dựa|Thêm một chứng/u;

test('the site sample: Công danh confirms "gian truân" before the turn, Mệnh tells "vàng ngọc đầy nhà" as the better side', () => {
  const chs = read(sample), sent = (c: string) => chs.find(x => x.chapter === c)!.paragraphs.flatMap(p => p.sentences);
  const cd = sent('cong_danh'), at = (re: RegExp) => cd.findIndex(s => re.test(s.text));
  assert.ok(at(/cùng khổ/) >= 0 && at(/gặp thời vận tốt/) >= 0);
  assert.ok(at(/cùng khổ/) < at(/gặp thời vận tốt/), 'the corroboration of gian truân comes before the turn');
  const rich = sent('menh').find(s => /vàng ngọc đầy nhà/.test(s.text))!;
  assert.ok(rich && !AGREE.test(rich.text), rich?.text);
});

test('no corroboration follows a turn of another concept (30 corpus charts)', () => {
  const bad: string[] = [];
  for (const [i, c] of corpus.entries()) for (const ch of read(c.facts)) for (const p of ch.paragraphs) p.sentences.forEach((s, j) => {
    if (!(s.trace.step ?? '').startsWith('corroborated:') || !AGREE.test(s.text) || j === 0) return;
    const prev = p.sentences[j - 1];
    if (prev.trace.move === 'TURN' && !prev.trace.concepts.some(x => s.trace.concepts.includes(x))) bad.push(`#${i}/${ch.chapter}: ${prev.text} | ${s.text}`);
  });
  assert.deepEqual(bad, []);
});
