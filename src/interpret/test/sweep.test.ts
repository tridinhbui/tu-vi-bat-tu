// Coverage sweep: the 30 regression charts + 40 charts chosen by tools/interpret/make_sweep.py to cover rare configurations (vô chính diệu,
// Tuần/Triệt, each Tứ Hóa in Quan Lộc, Thân cư Quan Lộc, 0 / 4+ sát tinh, Lộc Mã, children, the elderly...), every chapter. These are AUTOMATED
// checks: they bound defects a reader would notice; they do not certify interpretive quality (no practitioner has reviewed the content).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { interpret, CHAPTERS } from '../pipeline.ts';
import type { Knowledge } from '../types.ts';

const K: Knowledge = JSON.parse(readFileSync(new URL('../generated/knowledge.json', import.meta.url), 'utf8'));
const reg = JSON.parse(readFileSync(new URL('./fixtures/charts.json', import.meta.url), 'utf8'));
const sweep = JSON.parse(gunzipSync(readFileSync(new URL('./fixtures/sweep.json.gz', import.meta.url))).toString('utf8'));
const corpus: Array<{ label: string; facts: any; features?: string[] }> = [...reg, ...sweep];

test('the coverage corpus has 70 charts and every rare configuration', () => {
  assert.ok(corpus.length >= 70);
  const f = new Set(sweep.flatMap((x: any) => x.features));
  for (const x of ['ql_vcd', 'menh_vcd', 'ql_tuan', 'ql_triet', 'than_ql', 'tp_sat_0', 'tp_sat_4+', 'tp_loc_ma', 'ql_Hóa Kỵ', 'now_in_ql_decade', 'child', 'old']) assert.ok(f.has(x), `missing ${x}`);
});

test('every chapter of every corpus chart: no errors, warnings stay rare, budget respected, deterministic', () => {
  const warn = new Map<string, number>();
  for (const c of corpus) for (const ch of CHAPTERS) {
    const o = interpret(c.facts, ch, K);
    assert.deepEqual(o.quality.errors, [], `${c.label} ${ch}`);
    for (const w of o.quality.warnings) warn.set(w.check, (warn.get(w.check) ?? 0) + 1);
    if (ch !== 'bat_tu') assert.ok(o.quality.metrics.words <= 1500, `${c.label} ${ch} ${o.quality.metrics.words}`);
  }
  const total = [...warn.values()].reduce((a, b) => a + b, 0);
  assert.ok(total <= 20, `${total} warnings over ${corpus.length * CHAPTERS.length} chapters: ${[...warn].join(' ')}`);   // 700 chapters; 13 today
  for (const c of [corpus[0], corpus[33], corpus[55]]) for (const ch of CHAPTERS) assert.equal(interpret(c.facts, ch, K).text, interpret(c.facts, ch, K).text);
});
