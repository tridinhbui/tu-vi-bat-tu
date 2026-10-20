// Interpretation Reasoner + reasoned Mệnh prose (plan quirky-tinkering-rabin R3–R5). Gates are the plan's: the reading must change where a key
// element changes and stay put where nothing that matters changed; every sentence voices a plan step; the worked example argues what the
// books say about it (Hóa Lộc ở Tứ Mộ reduces the money the same Lộc brings). Golden: UPDATE_GOLDEN=1 regenerates benchmark20.reasoned.txt.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import type { Knowledge } from '../types.ts';
import { reasonMenh } from '../reason/plan.ts';
import { reasonedChapter, reasonedSaid } from '../prose/narrative.ts';
import { counterfactual, distinct, oldEngine } from '../../../tools/interpret/eval_distinct.ts';

const FX = join(import.meta.dirname, 'fixtures');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const bench = JSON.parse(readFileSync(join(FX, 'benchmark20.json'), 'utf8'));
const variants = JSON.parse(gunzipSync(readFileSync(join(FX, 'counterfactual100.json.gz'))).toString('utf8'));
const rates = { concept: K.kg!.baseRates!.concept, rule: K.kg!.baseRates!.rule };
const ref = bench.find((b: any) => b.label === 'ref_cu_tuat');

test('worked example: Cự Môn hãm hóa Lộc at Tuất — the rescue and the Tứ Mộ limit of the same Lộc are argued together', () => {
  const p = reasonMenh(ref.facts, K);
  assert.equal(p.frame.centre.seat.id, 'major:Cự Môn');
  assert.ok(p.frame.formations.some(f => f.ruleId === 'TV_TH_CACH_MENH_KINH_NHAP_MIEU'), 'cách Kình Dương nhập miếu is in the frame');
  const cu = p.theses.find(t => t.seat.id === 'major:Cự Môn')!;
  assert.ok(cu.claims.some(c => c.concept === 'life.mitigated'), 'Cự hãm hóa Lộc: vẫn khá (TH)');
  assert.equal(cu.rescuerCaveat?.seat.id, 'hoa:Hóa Lộc');
  const loc = p.theses.find(t => t.seat.id === 'hoa:Hóa Lộc')!;
  const fin = loc.claims.find(c => c.concept === 'fin.abundance')!;
  assert.equal(fin.axis.verdict, 'qualified');
  assert.deepEqual(fin.axis.reducers.map(x => x.r.ruleId).sort(), ['TV_KL_PHU2_HOA_LOC_TU_MO', 'TV_TH_AUX_MENH_HL_TU_MO']);
  assert.ok(fin.axis.against.some(x => x.r.ruleId === 'TV_KL_PHU2_BA_KHONG'), 'Ba Không is kept as the limit, below the Hóa on tier');
  const o = reasonedChapter(ref.facts, K, { allowDraft: true });
  assert.ok(o.pass, o.issues.map(i => i.code + ' ' + i.msg).join('\n'));
  assert.match(o.text, /Tứ Mộ/);
  assert.match(o.text, /Kình Dương nhập miếu/);
});

test('position guards: a rule whose stars do not stand where the book says is not used (Tả Hữu "ở Tài Bạch, Quan Lộc", here Hữu Bật in Mệnh)', () => {
  const p = reasonMenh(ref.facts, K);
  assert.ok(p.guarded.some(g => g.ruleId === 'TV_TT_MENH_TA_HUU_TAI_QUAN'));
  const fin = p.theses.flatMap(t => t.claims).find(c => c.concept === 'fin.abundance')!;
  assert.ok(!fin.axis.base.some(x => x.r.ruleId === 'TV_TT_MENH_TA_HUU_TAI_QUAN'));
});

test('draft cách cục states reach the frame and the text only when draft prose is allowed', () => {
  const b = bench.find((x: any) => x.label === 'tu_phu_vu_tuong');
  const p = reasonMenh(b.facts, K);
  assert.ok(p.frame.states.some(s => s.id === 'CACH_X_TU_PHU_VU_TUONG' && s.state === 'bi_pha'));
  assert.match(reasonedChapter(b.facts, K, { allowDraft: true }).text, /cách Tử Phủ Vũ Tướng, nhưng cách bị phá/);
  assert.equal(reasonMenh(b.facts, K, undefined, { draftFormations: false }).frame.states.length, 0);
});

test('every benchmark chapter passes validation, voices only plan steps and is not empty', () => {
  for (const b of bench) {
    const o = reasonedChapter(b.facts, K, { allowDraft: true });
    assert.ok(o.pass, `${b.label}: ${o.issues.filter(i => i.level === 'error').map(i => i.code + ' ' + i.msg).join('\n')}`);
    assert.ok(o.paragraphs.length >= 2, `${b.label}: at least the frame and one thesis`);
    for (const p of o.paragraphs) for (const s of p.sentences) assert.ok(s.trace.step, `${b.label}: sentence without plan step: ${s.text}`);
  }
});

test('one-factor counterfactuals: critical changes move the reading at the right place, inert ones change nothing', () => {
  const c = counterfactual(reasonedSaid, K, bench, variants);
  assert.ok(c.criticalLocal >= 0.9, `critical changes voiced at the changed element: ${c.criticalLocal}`);
  assert.equal(c.inertSame, 1, 'a control variant leaves the content unchanged');
  assert.equal(c.inertTextSim, 1, 'and the text identical (variant choice is seeded by the plan, not the star list)');
});

test('content distinctiveness is better than the old selection on the benchmark', () => {
  const now = distinct(reasonedSaid, K, bench, rates), old = distinct(oldEngine, K, bench, rates);
  assert.ok(now.barnum < old.barnum - 0.05, `barnum ${now.barnum} vs old ${old.barnum}`);
  assert.ok(now.commonShare < old.commonShare, `common share ${now.commonShare} vs old ${old.commonShare}`);
  assert.ok(now.contentJ < old.contentJ, `content Jaccard ${now.contentJ} vs old ${old.contentJ}`);
});

test('golden: the reasoned chapter of the 20 benchmark charts', () => {
  const text = bench.map((b: any) => `### ${b.label}\n${reasonedChapter(b.facts, K, { allowDraft: true }).text}\n`).join('\n');
  const f = join(FX, 'benchmark20.reasoned.txt');
  if (process.env.UPDATE_GOLDEN || !existsSync(f)) writeFileSync(f, text);
  assert.equal(text, readFileSync(f, 'utf8'));
});
