// Configurations and the structured analysis (plan docs/plans/THIEN-BAN-33-REVIEW-PLAN.md G9): the owner's Quan Lộc read as one structure,
// every domain of benchmark20 resting on a configuration, and the level ceiling (INV-12) on the Tổng luận.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { ChartInput, Knowledge } from '../types.ts';
import { infer } from '../prose/chapter.ts';
import { configurationOf } from '../reason/configuration.ts';
import { analyses } from '../reason/analysis.ts';
import { proseAllChapters } from '../route.ts';
import { checkedOnly } from '../prose/checked.ts';
import { checkInvariants } from '../invariants.ts';

const FX = join(import.meta.dirname, 'fixtures');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const owner: ChartInput = JSON.parse(readFileSync(join(FX, 'owner_2002_kl_2026-11.json'), 'utf8'));
const bench = JSON.parse(readFileSync(join(FX, 'benchmark20.json'), 'utf8')) as Array<{ label: string; facts: ChartInput }>;

test('owner chart: Quan Lộc is one configuration (borrowed Cơ Âm, the three Hóa, Việt Phụ Khôi, Kình Dương and Hóa Kỵ lessening) answering its questions', () => {
  const c = configurationOf(owner, K, 'Quan Lộc', infer(owner, K).resolved);
  const role = (name: string) => c.members.find(m => m.name === name)?.role;
  assert.deepEqual(c.core.map(m => [m.name, m.palace, m.borrowed]), [['Thiên Cơ', 'Phu Thê', true], ['Thái Âm', 'Phu Thê', true]]);
  assert.equal(role('Thái Dương hóa Quyền'), 'bien_tinh');
  assert.equal(role('Văn Khúc hóa Khoa'), 'bien_tinh');
  for (const n of ['Tả Phụ', 'Thiên Việt', 'Thiên Khôi']) assert.equal(role(n), 'tro_luc', n);
  assert.equal(role('Văn Xương hóa Kỵ'), 'tru');
  assert.equal(role('Kình Dương'), 'tru', 'KL p.145: Khôi Việt sợ Kình Đà');
  assert.ok(!c.members.some(m => m.name === 'Văn Khúc' && m.role === 'tro_luc'), 'a star counted once');
  assert.equal(c.state, 'co_dieu_kien');
  assert.ok(c.relations.some(r => r.kind === 'che' && r.cite === 'KL p.145'));
  assert.equal(c.questions.length, 6);
  assert.ok(c.questions[0].known && /Thiên Cơ/.test(c.questions[0].a), c.questions[0].a);
  assert.ok(c.steps.map(s => s.role).join(',').startsWith('nen,bien_tinh,tro_luc,tru'), 'the roles act in their order');
});

test('benchmark20: every domain conclusion rests on a configuration; nothing the Tổng luận ranks is below the tam phương level', () => {
  let n = 0, withCfg = 0;
  const bad: string[] = [];
  for (const b of [{ label: 'owner', facts: owner }, ...bench]) {
    const a = analyses(b.facts, K, infer(b.facts, K).resolved);
    for (const d of a.domains) { n++; if (d.dominant_configuration) withCfg++; }
    const chs = proseAllChapters(b.facts, K, { allowDraft: true, deep: true, luan: true }).filter(c => c.chapter === 'tong_luan').map(c => checkedOnly(c as never, b.facts)) as never;
    bad.push(...checkInvariants(b.facts, chs, a.domains).filter(v => v.inv === 'INV-12').map(v => `${b.label}: ${v.why}`));
  }
  console.log(`# ${withCfg}/${n} domain conclusions with a dominant configuration`);
  assert.ok(withCfg / n >= 0.9, `${withCfg}/${n}`);
  assert.deepEqual(bad, []);
});
