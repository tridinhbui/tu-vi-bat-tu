// Readability gate (plan quirky-tinkering-rabin, Track B): the Tử Vi reading speaks of the person, not of the method. Over benchmark20 and the
// two reference charts (menh_cu_tuat, the owner's 09/01/2002), the text the reader sees (chapter "all", checked readings only, Bát Tự aside)
//   - names no method word: how a reading was reached, what the books leave open, which table was used live in the sentence's note
//     (trace.note, shown when the sentence is opened), never in the text;
//   - ends every reading paragraph on a consequence or a piece of advice, not on a bare position;
//   - keeps sentences short (the mean is reported);
// and the Mệnh chapter's content measures (tools/interpret/eval_distinct.ts) are no worse than the luận cung baseline (docs/LUAN-EVAL.md).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { Knowledge } from '../types.ts';
import { proseAllChapters } from '../route.ts';
import { checkedOnly } from '../prose/checked.ts';
import { luanSaid } from '../prose/luan.ts';
import { distinct } from '../../../tools/interpret/eval_distinct.ts';
import type { ProseParagraph } from '../prose/realize.ts';

const FX = join(import.meta.dirname, 'fixtures');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const bench = JSON.parse(readFileSync(join(FX, 'benchmark20.json'), 'utf8')) as Array<{ label: string; facts: any }>;
const refs: Array<[string, any]> = [['menh_cu_tuat', JSON.parse(readFileSync(join(FX, 'menh_cu_tuat.json'), 'utf8')).facts], ['ref_2002_01_09', JSON.parse(readFileSync(join(FX, 'ref_2002_01_09_kl.json'), 'utf8'))]];
const charts: Array<[string, any]> = [...bench.map(b => [b.label, b.facts] as [string, any]), ...refs];

/** method words; "nguồn thu / nguồn lợi / nguồn tiền" are the reader's own words for income, not a source */
export const METHOD = /nguồn(?! (?:thu|lợi|tiền)\b)|quy tắc|đối chiếu|phạm vi|hệ thống|trọng số|cách hiểu|chưa có lời/iu;
/** steps that state where things stand without what follows from it: a reading paragraph does not end on one */
const BARE = /^(frame|position|centre|domain|majors|group|hoa)(:|$)|^structure:[^:]+:(head|position|caveat)$|^than:[^:]+$/;

type Ch = { chapter: string; luan?: boolean; paragraphs: ProseParagraph[] };
const reading = (facts: any): Ch[] => proseAllChapters(facts, K, { allowDraft: true, deep: true, luan: true })
  .map(c => checkedOnly(c as Parameters<typeof checkedOnly>[0]) as unknown as Ch).filter(c => !String(c.chapter).startsWith('bat_tu'));
const all = charts.map(([label, f]) => ({ label, chs: reading(f), kl: (f.decades ?? []).some((d: any) => d.kl) }));

test('the text names no method word; what the method says is in a note', () => {
  const bad: string[] = [];
  for (const { label, chs } of all) for (const c of chs) for (const p of c.paragraphs) for (const s of p.sentences) {
    if (METHOD.test(s.text)) bad.push(`${label}/${c.chapter}: ${s.text}`);
    if (s.trace.aside) bad.push(`${label}/${c.chapter}: aside left in the text: ${s.text}`);
  }
  assert.deepEqual(bad.slice(0, 5), [], `${bad.length} sentences`);
});

test('every reading paragraph ends on a consequence or advice, not on a bare position', () => {
  const bad: string[] = [];
  for (const { label, chs, kl } of all) for (const c of chs) for (const p of c.paragraphs) {
    if (p.role === 'structure') continue;                     // the chapter's opening: where the palace stands
    const last = p.sentences.at(-1)!, step = last.trace.step ?? '';
    // a đại hạn told by its palace alone: only in facts older than the Khảo Luận hạn reading (decades[].kl, menh_cu_tuat), which /api/facts
    // always sends now
    const vanFrame = kl && c.chapter === 'van_han' && last.trace.rules.length === 1 && last.trace.rules[0] === 'VH_CALC_DAI_HAN';
    if (BARE.test(step) || vanFrame) bad.push(`${label}/${c.chapter} [${step || last.trace.move}]: ${p.sentences.map(s => s.text).join(' ')}`);
  }
  assert.deepEqual(bad.slice(0, 5), [], `${bad.length} paragraphs`);
});

test('sentences stay short (the mean is reported)', () => {
  const lens = all.flatMap(({ chs }) => chs.flatMap(c => c.paragraphs.flatMap(p => p.sentences.map(s => s.text.split(/\s+/).length))));
  const mean = lens.reduce((a, b) => a + b, 0) / lens.length, long = lens.filter(n => n > 35).length / lens.length;
  console.log(`# readability: ${lens.length} sentences, mean ${mean.toFixed(1)} words, ${(100 * long).toFixed(1)}% over 35 words`);
  assert.ok(mean <= 23, `mean ${mean.toFixed(1)} words`);
  assert.ok(long <= 0.05, `${(100 * long).toFixed(1)}% of sentences over 35 words`);
});

test('owner chart: the Cự Môn caveat and the centre are notes, the text never says hãm turned good', () => {
  const menh = all.find(x => x.label === 'ref_2002_01_09')!.chs.find(c => c.chapter === 'menh')!;
  const ss = menh.paragraphs.flatMap(p => p.sentences), text = ss.map(s => s.text).join(' ');
  assert.ok(!/hết hãm|là trục của cả lá số|chưa có nguồn|chữ ‘hội’/.test(text), text);
  assert.ok(ss.some(s => /Cự Môn hết hãm/.test(s.trace.note ?? '')), 'the caveat is a note');
  assert.ok(ss.some(s => /Cự Môn/.test(s.trace.note ?? '') && /trục|bắt đầu từ|xoay quanh/.test(s.trace.note ?? '')), 'the centre is a note');
});

test('Mệnh content measures no worse than the luận cung baseline (docs/LUAN-EVAL.md, benchmark20: Barnum 40.5%, strip 0.065)', () => {
  const rates = JSON.parse(readFileSync(join(import.meta.dirname, '..', '..', '..', 'engine', 'data', 'kg', 'base_rates.json'), 'utf8'));
  const d = distinct(luanSaid, K, bench, rates);
  console.log(`# benchmark20 luận cung Mệnh: Barnum ${(100 * d.barnum).toFixed(1)}%, strip ${d.stripSim}`);
  assert.ok(d.barnum <= 0.4055, `Barnum ${d.barnum}`);
  assert.ok(d.stripSim <= 0.0655, `strip ${d.stripSim}`);
});
