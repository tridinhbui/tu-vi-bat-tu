// Structures for the reasoner (plan quirky-tinkering-rabin R2): the TS port of formation_eval.py and synthesis/structures.py must agree with
// Python on every chart of the 1,000-chart corpus (fixture: tools/interpret/make_structure_parity.py), plus hand checks on the worked example
// (02/03/1991 08:30 nam, Cự Môn hãm hóa Lộc + Kình Dương + Tuần at Mệnh Tuất).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { run } from '../engine.ts';
import { detectStructures, evaluateFormations, labelledFindings, type Formation } from '../reason/structures.ts';
import type { ChartInput, Knowledge } from '../types.ts';

const FORMATIONS: Formation[] = JSON.parse(readFileSync(new URL('../../../engine/data/experimental/formations_experimental.json', import.meta.url), 'utf8')).formations;
const corpus: Array<{ facts: ChartInput }> = JSON.parse(gunzipSync(readFileSync(new URL('./fixtures/corpus1000.json.gz', import.meta.url))).toString('utf8'));
const parity = JSON.parse(gunzipSync(readFileSync(new URL('./fixtures/structures_parity.json.gz', import.meta.url))).toString('utf8'));
const ex: { facts: ChartInput } = JSON.parse(readFileSync(new URL('./fixtures/menh_cu_tuat.json', import.meta.url), 'utf8'));
const K: Knowledge = JSON.parse(readFileSync(new URL('../generated/knowledge.json', import.meta.url), 'utf8'));

const tsFormations = (c: ChartInput) => evaluateFormations(FORMATIONS, c.base).map(r => ({ ...r.verdict, text: r.text }));

test('the fixture covers the whole corpus', () => {
  assert.equal(parity.charts.length, corpus.length);
  assert.equal(corpus.length, 1000);
});

test('formations: TS verdict and Vietnamese text == Python on all 1,000 corpus charts', () => {
  const bad: string[] = [];
  corpus.forEach((c, i) => {
    try { assert.deepEqual(tsFormations(c.facts), parity.charts[i].formations); } catch (e) { bad.push(`chart ${i}: ${(e as Error).message.slice(0, 400)}`); }
  });
  assert.deepEqual(bad.slice(0, 3), []);
});

test('structures: TS detectors == Python on all 1,000 corpus charts', () => {
  const bad: string[] = [];
  corpus.forEach((c, i) => {
    try { assert.deepEqual(detectStructures(c.facts.palaces, c.facts.tu_hoa), parity.charts[i].structures); } catch (e) { bad.push(`chart ${i}: ${(e as Error).message.slice(0, 400)}`); }
  });
  assert.deepEqual(bad.slice(0, 3), []);
});

test('the corpus reaches every state the formations can take on it, and no formation is ever verified', () => {
  const states = new Map<string, Set<string>>();
  for (const c of corpus) for (const r of evaluateFormations(FORMATIONS, c.facts.base)) {
    if (!states.has(r.id)) states.set(r.id, new Set());
    states.get(r.id)!.add(r.state);
    assert.notEqual(r.verification, 'verified');
    assert.equal(r.experimental, true);
  }
  assert.equal(states.size, 10);
  for (const [id, s] of states) assert.ok(s.has('khong_hien') && s.has('bi_pha') && s.size >= 3, `${id}: ${[...s]}`);
  // matched evidence carries its label; bị phá always names the uncovered breaker
  const r = corpus.flatMap(c => evaluateFormations(FORMATIONS, c.facts.base)).find(x => x.state === 'bi_pha')!;
  assert.ok(r.uncovered.length && r.uncovered.every(e => e.label.length > 0) && r.effect === 'limit');
});

test('worked example: TS == Python on formations and structures', () => {
  assert.deepEqual(tsFormations(ex.facts), parity.example.formations);
  assert.deepEqual(detectStructures(ex.facts.palaces, ex.facts.tu_hoa), parity.example.structures);
});

test('worked example: Cự Môn hãm + Hóa Lộc at Tuất gives CU_MON_HOA_LOC with the Tứ Mộ limiter (KL tr.66 / TH tr.52)', () => {
  const ss = detectStructures(ex.facts.palaces, ex.facts.tu_hoa);
  const cu = ss.find(s => s.id === 'CU_MON_HOA_LOC')!;
  assert.equal(cu.present, true);
  assert.equal(cu.name, 'Cự Môn hãm gặp Hóa Lộc');
  assert.deepEqual(cu.palaces, ['Mệnh']);
  assert.deepEqual(cu.premises.map(p => p.ok), [true, true, true]);
  assert.equal(cu.premises[0].text, 'Cự Môn tại Tuất (Mệnh), độ sáng: hãm');
  assert.ok(cu.limiters.includes('Hóa Lộc đóng ở Tứ Mộ: tài lộc giảm nhiều (KL tr.66; TH tr.52 nói giảm quá nửa, trừ khi gặp Tham/Vũ)'));
  assert.ok(cu.limiters.some(l => l.startsWith('Sát tinh trong tam phương tứ chính: ') && l.includes('Kình Dương')));
  assert.ok(cu.rescuers.some(r => r.startsWith('Cung có Tuần')) && cu.matrix_ids.includes('R07'));
  assert.ok(cu.cites.includes('KL tr.66') && cu.cites.includes('TH tr.52'));
  assert.equal(cu.verification, 'mot_phan');                        // the combination itself has no book sentence
  assert.ok(cu.reading.startsWith('Điều kiện tiên quyết ‘Cự Môn hãm’ đúng.'));
  // Kình Dương sits at Tuất too: the Tứ Mộ Kình structure is reported for Mệnh
  assert.ok(ss.some(s => s.id === 'KINH_DUONG_TU_MO' && s.palaces[0] === 'Mệnh' && s.verification === 'mot_phan'));
  // Cự Môn at Tuất is not Tý/Ngọ: Thạch trung ẩn ngọc does not appear
  assert.equal(evaluateFormations(FORMATIONS, ex.facts.base).find(r => r.id === 'CACH_X_THACH_TRUNG_AN_NGOC')!.state, 'khong_hien');
});

test('labelled findings: exactly the formation/classification entries lift() returns, with claim and reading attached', () => {
  const res = run(K.rules, K.sources, ex.facts.base);
  for (const draft of [false, true]) {
    const out = labelledFindings(res.findings, K, ex.facts.base, { includeDraftRules: draft });
    const links = K.kg?.ruleConcepts ?? {};
    const want = res.findings.filter(f => (draft || f.basis === 'verified') && ['formation', 'classification'].includes(links[f.ruleId]?.kind ?? ''));
    assert.deepEqual(out.map(l => [l.ruleId, l.subject, l.claim]), want.map(f => [f.ruleId, f.subject, f.claim]));
    assert.ok(out.some(l => l.ruleId === 'TV_TH_CACH_MENH_KINH_NHAP_MIEU' && l.kind === 'formation'));
    for (const l of out) assert.ok(l.kind === 'formation' || l.kind === 'classification');
  }
});
