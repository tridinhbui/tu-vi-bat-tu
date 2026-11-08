// Cross-report invariants (plan docs/plans/THIEN-BAN-33-REVIEW-PLAN.md G-INV) on the report as the reader gets it: the owner's chart
// (09/01/2002 04:30 nam, Khảo Luận table, facts from /api/facts on 2026-11-07), the site's sample chart and benchmark20. Corpus counts:
// tools/interpret/eval_invariants.ts --n 300.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { ChartInput, Knowledge } from '../types.ts';
import { proseAllChapters } from '../route.ts';
import { checkedOnly } from '../prose/checked.ts';
import { checkInvariants } from '../invariants.ts';
import type { ProseParagraph } from '../prose/realize.ts';

const FX = join(import.meta.dirname, 'fixtures');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const owner: ChartInput = JSON.parse(readFileSync(join(FX, 'owner_2002_kl_2026-11.json'), 'utf8'));
const sample: ChartInput = JSON.parse(readFileSync(join(FX, 'site_sample_1990.json'), 'utf8'));
const bench = (JSON.parse(readFileSync(join(FX, 'benchmark20.json'), 'utf8')) as Array<{ label: string; facts: ChartInput }>);
type Ch = { chapter: string; paragraphs: ProseParagraph[] };
const read = (f: ChartInput) => proseAllChapters(f, K, { allowDraft: true, deep: true, luan: true }).map(c => checkedOnly(c as never, f)) as unknown as Ch[];
const ownerReport = read(owner);
const text = (c: string) => ownerReport.find(x => x.chapter === c)!.paragraphs.flatMap(p => p.sentences).map(s => s.text).join(' ');

test('no invariant is broken on the owner chart, the site sample and benchmark20', () => {
  const bad = [['owner', owner, ownerReport] as const, ['sample', sample, read(sample)] as const, ...bench.map(b => [b.label, b.facts, read(b.facts)] as const)]
    .flatMap(([label, f, chs]) => checkInvariants(f, chs).map(v => `${label} ${v.inv} ${v.chapter}: ${v.why} | ${v.text.slice(0, 120)}`));
  assert.deepEqual(bad, []);
});

test('owner chart, Cách cục: Đào hoa Thiên không is told from Tài Bạch with the stars that ease it, never as standing in Mệnh', () => {
  const t = text('cach_cuc');
  assert.match(t, /Thiên Không và Đào Hoa không đứng ở cung Mệnh mà ở cung Tài Bạch/);
  assert.match(t, /Thái Dương hóa Quyền, Văn Khúc hóa Khoa/);
  assert.doesNotMatch(t, /Đứng ở cung Mệnh, cách xấu|không có chỗ đỡ|cả đời/);
  assert.doesNotMatch(t, /có sức nặng nhất/, 'a first place is told only with its reason');
});

test('owner chart, Tổng luận: each domain of a shared place has its own ground; no decade from 80 on is ranked', () => {
  const t = text('tong_luan');
  assert.match(t, /cách giữ và quản lý tiền \([^)]*gốc là Văn Khúc ở cung Tài Bạch\) và phần tích lũy, nhà cửa \([^)]*gốc là Liêm Trinh ở cung Điền Trạch\)/);
  assert.doesNotMatch(t, /93–102|103–112|113–122/);
  assert.doesNotMatch(t, /^Chỗ dựa đứng đầu/m);
});

test('owner chart, grave book sentences leave the main text for one neutral Đọc sâu line each', () => {
  const all = ownerReport.flatMap(c => c.paragraphs.filter(p => !p.deep).flatMap(p => p.sentences)).map(s => s.text).join(' ');
  for (const re of [/thích cờ bạc/, /chiếm đoạt, phá sản/, /hiếm con/, /bạo bệnh/, /cha mẹ thọ/]) assert.doesNotMatch(all, re);
  const neutral = ownerReport.flatMap(c => c.paragraphs.filter(p => p.severity).flatMap(p => p.sentences));
  assert.ok(neutral.some(s => /Văn Khúc ở cung Tài Bạch được đọc vào chuyện thói ham vui/.test(s.text)), 'the neutral line names the star where it stands');
  assert.ok(neutral.filter(s => s.trace.severity).every(s => s.trace.cites.length > 0), 'each neutral line keeps its page');
  assert.ok(neutral.some(s => /chưa được kiểm chứng bằng thực nghiệm/.test(s.text)));
});

test('owner chart, Quan Lộc: the Thân cư reading names the Hóa Kỵ it needs, the 40-year mark is the old text\'s own', () => {
  const t = text('cong_danh');
  assert.match(t, /Thân cư Quan Lộc lại gặp Văn Xương hóa Kỵ ở cung Phu Thê, nên công danh đến muộn/);
  assert.match(t, /Lời cổ còn đặt một mốc tuổi: dù có cát tinh hội, cũng phải ngoài 40 tuổi/);
  assert.doesNotMatch(t, /nổi lên ở các chặng/);
});
