// Coverage sweep: 8 regression charts + 40 charts chosen to cover rare configurations (Quan Lộc / Mệnh vô chính diệu, Tuần or Triệt in
// the palace, each Tứ Hóa in Quan Lộc, Thân cư Quan Lộc, 0 or 4+ sát in the tam phương, Lộc Mã, children and the elderly...), for every
// chapter. These are AUTOMATED checks: they bound defects a reader would notice, they do not certify interpretive quality.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { CHAPTERS } from '../pipeline.ts';
import { sweep, loadCorpus } from '../../../tools/interpret/sweep.ts';
import type { Knowledge } from '../types.ts';

const K: Knowledge = JSON.parse(readFileSync(new URL('../generated/knowledge.json', import.meta.url), 'utf8'));

test('the corpus has at least 30 diverse charts', () => {
  const c = loadCorpus();
  assert.ok(c.length >= 30, `${c.length} charts`);
  const feats = new Set(c.flatMap((x: any) => x.features ?? []));
  for (const f of ['ql_vcd', 'menh_vcd', 'ql_tuan', 'ql_triet', 'than_ql', 'tp_sat_0', 'tp_sat_4+', 'tp_loc_ma', 'ql_Hóa Kỵ', 'now_in_ql_decade', 'child', 'old'])
    assert.ok(feats.has(f), `missing configuration ${f}`);
});

for (const ch of CHAPTERS) {
  test(`${ch}: every chart passes; warnings stay rare; no inflation; templates do not dominate; CPU stays in milliseconds`, () => {
    const r = sweep(ch, K);
    const errors = r.rows.flatMap(x => x.errors.map((e: string) => `${x.i}:${e}`));
    assert.deepEqual(errors, []);
    const warnings = r.rows.flatMap(x => x.warnings);
    assert.ok(warnings.length <= 3, `${warnings.length} warnings: ${warnings.join(', ')}`);
    for (const x of r.rows) assert.ok(x.words <= 1500, `${x.i} ${x.words} words`);
    const bp = r.rows.map(x => x.boilerplate).sort((a, b) => a - b);
    assert.ok(bp[bp.length >> 1] <= 0.08 && bp[bp.length - 1] <= 0.15, `boilerplate median ${bp[bp.length >> 1]} max ${bp[bp.length - 1]}`);
    // no CONTENT sentence skeleton (book reading / condition) recurs in more than half of the charts
    assert.deepEqual(r.recurring.filter(x => x.charts > r.n / 2 && !/^(Theo phép tam phương|Khung tam phương|Đại hạn đi qua|Theo vòng đại hạn)/.test(x.skeleton)).map(x => x.skeleton), []);
    const ms = r.rows.map(x => x.ms).sort((a, b) => a - b);
    assert.ok(ms[ms.length >> 1] < 250, `median ${ms[ms.length >> 1]} ms`);
  });
}
