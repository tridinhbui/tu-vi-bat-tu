// The TS rule engine must fire exactly the rules the validated Python engine fires, on every regression chart.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { run } from '../engine.ts';
import { compare, evaluate } from '../dsl.ts';
import type { Knowledge } from '../types.ts';

const K: Knowledge = JSON.parse(readFileSync(new URL('../generated/knowledge.json', import.meta.url), 'utf8'));
const charts = JSON.parse(readFileSync(new URL('./fixtures/charts.json', import.meta.url), 'utf8'));

test('dsl three-valued semantics match Python', () => {
  assert.equal(compare(['Tử Vi'], 'contains', 'Tử Vi'), true);
  assert.equal(compare('Thìn', 'in', ['Thìn', 'Tuất']), true);
  assert.equal(compare(null, 'gte', 1), null);                       // Python TypeError -> unknown
  assert.equal(evaluate({ fact: 'missing', value: 1 }, {}), null);
  assert.equal(evaluate({ all: [{ fact: 'a', value: 1 }, { fact: 'missing', value: 1 }] }, { a: 2 }), false);
  assert.equal(evaluate({ any: [{ fact: 'a', value: 1 }, { fact: 'missing', value: 1 }] }, { a: 2 }), null);
  assert.equal(evaluate({ count: [{ fact: 'a', value: 1 }, { fact: 'b', value: 1 }], operator: 'gte', value: 1 }, { a: 1 }), true);
});

for (const c of charts) {
  test(`parity with the Python engine: ${c.label} (${c.birth.year}-${c.birth.month}-${c.birth.day})`, () => {
    const res = run(K.rules, K.sources, c.facts.base);
    const ts = new Set(res.findings.map(f => [f.ruleId, f.subject, f.claim, f.effect, f.basis].join('|')));
    const py = new Set<string>(c.python_fired.map((x: string[]) => x.join('|')));
    assert.deepEqual([...ts].filter(x => !py.has(x)), [], 'fired in TS only');
    assert.deepEqual([...py].filter(x => !ts.has(x)), [], 'fired in Python only');
  });
}

for (const c of charts) {
  test(`Bát Tự parity with the Python engine: ${c.label} (${c.birth.year}-${c.birth.month}-${c.birth.day})`, () => {
    assert.ok(c.facts.bazi, 'fixture carries the bat_tu fact base');
    const res = run(K.rules, K.sources, c.facts.bazi.base, 'bat_tu');
    const ts = new Set(res.findings.map(f => [f.ruleId, f.subject, f.claim, f.effect, f.basis].join('|')));
    const py = new Set<string>(c.python_fired_bazi.map((x: string[]) => x.join('|')));
    assert.deepEqual([...ts].filter(x => !py.has(x)), [], 'fired in TS only');
    assert.deepEqual([...py].filter(x => !ts.has(x)), [], 'fired in Python only');
  });
}
