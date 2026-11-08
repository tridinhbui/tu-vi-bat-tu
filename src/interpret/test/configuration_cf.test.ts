// Counterfactuals at the configuration level (plan THIEN-BAN-33 G10.6): one key fact of the owner's chart changed at a time, and the Quan
// Lộc configuration must react the way its roles say — a lost bien_tinh narrows it, a lost tru does not weaken it, a lost tro_luc leaves its
// state, a chính tinh in the palace ends the borrowing.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { ChartInput, Knowledge } from '../types.ts';
import { configurationOf } from '../reason/configuration.ts';

const FX = join(import.meta.dirname, 'fixtures');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const base: ChartInput = JSON.parse(readFileSync(join(FX, 'owner_2002_kl_2026-11.json'), 'utf8'));
const clone = (): ChartInput => JSON.parse(JSON.stringify(base));
const QL = (f: ChartInput) => configurationOf(f, K, 'Quan Lộc', []);
const pal = (f: ChartInput, n: string) => f.palaces.find(p => p.name === n)!;
const b0 = QL(base);

test('removing a bien_tinh (Thái Dương hóa Quyền) takes it out of the configuration and lowers its strength', () => {
  const f = clone(); delete (f.tu_hoa as Record<string, unknown>)['Hóa Quyền'];
  const c = QL(f);
  assert.ok(!c.members.some(m => m.name === 'Thái Dương hóa Quyền'));
  assert.ok(c.strength < b0.strength, `${c.strength} < ${b0.strength}`);
});

test('removing a tru (Kình Dương at Mệnh) never weakens the configuration', () => {
  const f = clone(); pal(f, 'Mệnh').stars = pal(f, 'Mệnh').stars.filter(s => s !== 'Kình Dương');
  const c = QL(f);
  assert.ok(!c.members.some(m => m.name === 'Kình Dương'));
  assert.ok(c.strength >= b0.strength);
});

test('removing a tro_luc (Thiên Khôi at Tài Bạch) keeps the state; the strength moves at most by its own step', () => {
  const f = clone(); pal(f, 'Tài Bạch').stars = pal(f, 'Tài Bạch').stars.filter(s => s !== 'Thiên Khôi');
  const c = QL(f);
  assert.equal(c.state, b0.state);
  assert.ok(b0.strength - c.strength <= 0.5);
});

test('a chính tinh in the palace ends the borrowing', () => {
  const f = clone(); const q = pal(f, 'Quan Lộc'); q.major_stars = ['Tử Vi']; q.stars = [...q.stars, 'Tử Vi'];
  const c = QL(f);
  assert.ok(c.core.length && c.core.every(m => !m.borrowed), JSON.stringify(c.core.map(m => m.name)));
  assert.ok(b0.core.every(m => m.borrowed));
});

test('an unrelated star elsewhere (Hồng Loan off Mệnh) changes nothing in the Quan Lộc configuration', () => {
  const f = clone(); pal(f, 'Mệnh').stars = pal(f, 'Mệnh').stars.filter(s => s !== 'Hồng Loan');
  const c = QL(f);
  assert.equal(c.strength, b0.strength);
  assert.deepEqual(c.members.map(m => m.id), b0.members.map(m => m.id));
});
