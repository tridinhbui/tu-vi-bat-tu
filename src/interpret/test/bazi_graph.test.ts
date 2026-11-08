// The Bát Tự side of the review plan (THIEN-BAN-33 G9.1, G2.3, G3.1, G2.4) on the owner's chart (Tân Tỵ · Tân Sửu · Đinh Sửu · Nhâm Dần):
// the element map agrees at Giáp and parts ways only at Canh, the Quan → Ấn chain is of middle grade through the Giáp hidden under Nhâm,
// the reading says so, and the Mậu Tuất pillar's chế hóa reaches its verdict.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { ChartInput, Knowledge } from '../types.ts';
import { baziGraph } from '../reason/bazi_graph.ts';
import { proseAllChapters } from '../route.ts';
import { checkedOnly } from '../prose/checked.ts';

const FX = join(import.meta.dirname, 'fixtures');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const owner: ChartInput = JSON.parse(readFileSync(join(FX, 'owner_2002_kl_2026-11.json'), 'utf8'));
const bazi = () => {
  const c = proseAllChapters(owner, K, { allowDraft: true, deep: true, luan: true }).find(x => x.chapter === 'bat_tu')!;
  return (checkedOnly(c as never, owner) as unknown as { text: string }).text;
};

test('graph: element map and the graded Quan → Ấn chain', () => {
  const g = baziGraph(owner)!;
  const row = (el: string) => g.elements.find(r => r.element === el)!;
  assert.equal(row('Mộc').group, 'Ấn'); assert.equal(row('Mộc').role, 'hy'); assert.equal(row('Mộc').agree, 'cung_chieu');
  assert.equal(row('Kim').agree, 'venh');
  const q = g.chains.find(c => c.from === 'Quan Sát')!;
  assert.equal(q.grade, 'vua', q.why);
  assert.deepEqual(q.path, ['hour.stem', 'hour.hidden.0', 'day.stem']);
  assert.ok(g.edges.some(e => e.kind === 'thong_can' && e.from.startsWith('year.hidden')), 'a root in Tỵ');
});

test('reading: agreement at Giáp, the one gap at Canh decided by named conditions, roots, the hidden chain, Mậu Tuất chế hóa', () => {
  const t = bazi();
  assert.doesNotMatch(t, /khác với dụng thần|không trùng với dụng thần/);
  assert.match(t, /Khí hậu và thế cân bằng gặp nhau ở Giáp|Ở điểm này hai phép cùng chiều/);
  assert.match(t, /(Chỗ vênh duy nhất là Canh|Hai phép chỉ vênh nhau ở Canh)/);
  assert.match(t, /Canh chỉ là can phụ của bảng điều hậu/);
  assert.match(t, /chi năm Tỵ \(Bính\) và chi giờ Dần \(Bính\)/);
  assert.match(t, /không đếm mỗi chữ như nhau|không tính bằng cách đếm chữ/);
  assert.match(t, /Giáp \(Chính Ấn\)[^.]*ngay dưới Nhâm \(Chính Quan\)|ngay dưới Nhâm \(Chính Quan\)/);
  assert.doesNotMatch(t, /chưa nối được tới nhật chủ/);
  assert.match(t, /[Cc]an Mậu của vận lại khắc can giờ Nhâm, chính chữ đang khắc dụng thần|can Mậu khắc can giờ Nhâm, chữ vốn đè lên dụng thần/);
});
