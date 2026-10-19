// The TS rule engine must fire exactly the rules the validated Python engine fires, on every regression chart.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { run } from '../engine.ts';
import { ALT, compare, evaluate } from '../dsl.ts';
import { classify, type School } from '../dignity.ts';
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

// A CONFLICT dignity cell reaches the facts as alternatives (facts['alt:<name>']); the cases are shared with engine/tests/test_dsl_alternatives.py.
const ALTS = JSON.parse(readFileSync(new URL('./fixtures/dsl_alternatives.json', import.meta.url), 'utf8')).cases;
test('dsl: disagreeing alternatives are TRUE only if all agree, FALSE only if none, else UNKNOWN (same cases as Python)', () => {
  for (const c of ALTS) assert.equal(evaluate(c.expr, c.facts, c.world ? (n: string) => c.world[n] ?? null : undefined), c.want, c.why);
});

// Toàn Thư charts covering every Toàn Thư CONFLICT cell (tools/interpret/make_conflict_fixtures.py): the alternatives in the fact base are
// the classifier's, and the TS engine fires exactly what Python fired on them.
const conflicts = JSON.parse(readFileSync(new URL('./fixtures/conflicts.json', import.meta.url), 'utf8'));
for (const c of conflicts) {
  test(`CONFLICT-cell parity with the Python engine: ${c.label}`, () => {
    const school = c.facts.dignity_school as School;
    let alts = 0;
    for (const p of c.facts.palaces) for (const s of p.stars) {
      const r = classify(s, p.branch, school), got = c.facts.base[`palace:${p.name}`][`${ALT}palace.dignity.${s}`];
      if (r.status === 'CONFLICT') { alts++; assert.deepEqual(got, r.alternatives.map(a => a.value), `${s} @ ${p.branch}`); }
      else assert.equal(got, undefined, `${s} @ ${p.branch}`);
    }
    assert.ok(alts > 0);
    const res = run(K.rules, K.sources, c.facts.base);
    const ts = new Set(res.findings.map(f => [f.ruleId, f.subject, f.claim, f.effect, f.basis].join('|')));
    const py = new Set<string>(c.python_fired.map((x: string[]) => x.join('|')));
    assert.deepEqual([...ts].filter(x => !py.has(x)), [], 'fired in TS only');
    assert.deepEqual([...py].filter(x => !ts.has(x)), [], 'fired in Python only');
  });
}

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

// Prose plan P0: parity over the stratified 1,000-chart corpus (tools/interpret/make_corpus.py), Tử Vi and Bát Tự. One test, a list of
// mismatching charts on failure, so a regression names the charts and rules instead of drowning the report.
const corpusUrl = new URL('./fixtures/corpus1000.json.gz', import.meta.url);
test('parity with the Python engine over the 1,000-chart corpus', { skip: !existsSync(corpusUrl) && 'corpus1000.json.gz not built' }, () => {
  const corpus = JSON.parse(gunzipSync(readFileSync(corpusUrl)).toString('utf8'));
  assert.equal(corpus.length, 1000);
  const bad: string[] = [];
  for (const c of corpus) {
    for (const [system, base, want] of [['tu_vi', c.facts.base, c.python_fired], ['bat_tu', c.facts.bazi.base, c.python_fired_bazi]] as const) {
      const ts = new Set(run(K.rules, K.sources, base, system).findings.map(f => [f.ruleId, f.subject, f.claim, f.effect, f.basis].join('|')));
      const py = new Set<string>(want.map((x: string[]) => x.join('|')));
      const diff = [...[...ts].filter(x => !py.has(x)).map(x => 'TS+ ' + x), ...[...py].filter(x => !ts.has(x)).map(x => 'PY+ ' + x)];
      if (diff.length) bad.push(`${JSON.stringify(c.birth)} ${system}: ${diff.slice(0, 3).join('; ')}`);
    }
  }
  assert.deepEqual(bad, []);
});
