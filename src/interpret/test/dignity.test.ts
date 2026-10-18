// Auxiliary-star brightness is computed only in Python (engine/tvbt/dignity.py); the TS side must carry it through unchanged:
// the fact base the TS rule engine reads, the chart graph and the source tags must all agree with the chart facts, on every
// regression and sweep chart (all 12 palaces of each), and an unknown level must stay unknown (never filled in).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { ChartGraph } from '../graph.ts';

const reg = JSON.parse(readFileSync(new URL('./fixtures/charts.json', import.meta.url), 'utf8'));
const sweep = JSON.parse(gunzipSync(readFileSync(new URL('./fixtures/sweep.json.gz', import.meta.url))).toString('utf8'));
const charts = [...reg, ...(Array.isArray(sweep) ? sweep : sweep.charts)];
const LEVELS = new Set(['miếu', 'vượng', 'đắc', 'lợi', 'bình', 'hãm']);

test('aux dignity: facts, graph and source tags agree on every palace of every fixture chart', () => {
  let cells = 0, known = 0;
  for (const c of charts) {
    const g = new ChartGraph(c.facts, []);
    assert.equal(c.facts.palaces.length, 12);
    for (const p of c.facts.palaces) {
      const base = c.facts.base[`palace:${p.name}`];
      for (const [s, lv] of Object.entries(p.minor_dignity as Record<string, string | null>)) {
        cells++;
        assert.ok(p.stars.includes(s), `${s} has a level but is not in ${p.name}`);
        assert.equal(base[`palace.dignity.${s}`], lv ?? 'unspecified', `fact base ${p.name}/${s}`);
        assert.equal(g.nodes.get(`star:${s}`)!.data!.dignity, lv, `graph ${s}`);
        const src = p.minor_dignity_src?.[s];
        if (lv === null) { assert.equal(src, undefined, `unknown ${s} must carry no source`); continue; }
        known++;
        assert.ok(LEVELS.has(lv), `level ${lv}`);
        assert.ok(src && /^(TH|TT|KL) pp?\.\d/.test(src.locator), `source of ${s} in ${p.name}`);
        if (src.term === 'lợi') assert.ok(lv === 'lợi' || (s === 'Văn Xương' && lv === 'đắc'), `lợi is only read as đắc for Văn Xương (${s})`);
      }
    }
  }
  assert.ok(cells > 500 && known > 200, `coverage ${known}/${cells}`);
});
