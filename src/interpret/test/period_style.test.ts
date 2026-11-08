// Plan THIEN-BAN-33 G6 (periods read against the natal structure, three views, the two systems side by side, the age mark beside the
// đại hạn) and G10.7 (no habitual opener repeated in a paragraph, the same causal joint varied, terms explained once) on the owner's chart.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { ChartInput, Knowledge } from '../types.ts';
import { proseAllChapters } from '../route.ts';
import { checkedOnly } from '../prose/checked.ts';
import { glossReport } from '../prose/glossary.ts';
import type { ProseParagraph } from '../prose/realize.ts';

const FX = join(import.meta.dirname, 'fixtures');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const owner: ChartInput = JSON.parse(readFileSync(join(FX, 'owner_2002_kl_2026-11.json'), 'utf8'));
type Ch = { chapter: string; paragraphs: ProseParagraph[]; text: string };
const report = glossReport(proseAllChapters(owner, K, { allowDraft: true, deep: true, luan: true }).map(c => checkedOnly(c as never, owner, K)) as unknown as Ch[]);
const text = (c: string) => report.find(x => x.chapter === c)!.paragraphs.map(p => p.text).join(' ');

test('G6: each đại hạn names the natal configurations it touches; the Tổng luận has the next decades and the two systems side by side', () => {
  assert.ok(report.find(x => x.chapter === 'van_han')!.paragraphs.flatMap(p => p.sentences).some(s => s.trace.step === 'config:touch'));
  const t = text('tong_luan');
  assert.match(t, /Hai chặng kế tiếp|Nhìn hai mươi năm tới/);
  assert.match(t, /chặng 23–32 tuổi \(2023–2032\)[^;]*Mậu Tuất, nặng; hai hệ vênh nhau/);
  assert.doesNotMatch(t, /\{[a-z]+\}/, 'every slot filled');
});

test('G6.4: the old text\'s age mark is set beside the chart\'s own đại hạn', () => {
  assert.match(text('cong_danh'), /Đặt cạnh lá số này, các đại hạn từ mốc ấy là 43–52 tuổi mức [^,]+, 53–62 tuổi/);
});

test('G10.7: no paragraph repeats a habitual opener or "; vì vậy"; each glossary term explained once, outside names', () => {
  for (const c of report) for (const p of c.paragraphs) {
    assert.ok(p.sentences.filter(s => /^(Bên cạnh đó|Ngoài ra|Thêm vào đó|Thêm nữa|Hơn nữa),/u.test(s.text)).length <= 1, `${c.chapter}: ${p.text.slice(0, 120)}`);
    assert.ok(p.sentences.filter(s => s.text.includes('; vì vậy ')).length <= 1, `${c.chapter}: ${p.text.slice(0, 120)}`);
  }
  const all = report.map(c => c.text).join(' ');
  assert.equal((all.match(/\(can của ngày sinh, đại diện cho bản thân\)/g) ?? []).length, 1);
  assert.doesNotMatch(all, /nhật chủ \(can của ngày sinh[^)]*\) Đinh/, 'not inside a name');
});
