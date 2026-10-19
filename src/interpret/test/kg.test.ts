// Knowledge-graph layer (prose plan P0): trigger atoms, evidence nesting and the page-checked qualifiers, on the worked-example chart
// (02/03/1991 08:30 nam, Cự Môn hãm hóa Lộc + Kình Dương + Tuần at Mệnh Tuất) and over the 1,000-chart corpus.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { run } from '../engine.ts';
import { triggerAtoms, signature, nesting } from '../kg/atoms.ts';
import { evaluateQualifiers, type Qualifier } from '../kg/qualifiers.ts';
import type { Facts, Knowledge } from '../types.ts';

const K: Knowledge = JSON.parse(readFileSync(new URL('../generated/knowledge.json', import.meta.url), 'utf8'));
const ex = JSON.parse(readFileSync(new URL('./fixtures/menh_cu_tuat.json', import.meta.url), 'utf8'));
const corpusUrl = new URL('./fixtures/corpus1000.json.gz', import.meta.url);
const rule = (id: string) => K.rules.find(r => r.id === id)!;
const QS = K.kg!.qualifiers as Qualifier[];
const factsAt = (base: Record<string, Facts>, palace: string): Facts => ({ ...(base.chart ?? {}), ...base[`palace:${palace}`] });
const world = (base: Record<string, Facts>) => (n: string) => base[`palace:${n}`] ?? null;

test('worked example: the TS engine fires exactly what Python fires', () => {
  const res = run(K.rules, K.sources, ex.facts.base);
  const ts = new Set(res.findings.map(f => [f.ruleId, f.subject, f.claim, f.effect, f.basis].join('|')));
  const py = new Set<string>(ex.python_fired.map((x: string[]) => x.join('|')));
  assert.deepEqual([...ts].filter(x => !py.has(x)), []);
  assert.deepEqual([...py].filter(x => !ts.has(x)), []);
});

test('trigger atoms name the chart facts a reading stood on, located in their palace', () => {
  const b = ex.facts.base, f = factsAt(b, 'Mệnh');
  const loc = triggerAtoms(rule('TV_TH_MV_MENH_CU_THIN_TUAT_LOC').conditions, f, world(b), 'Mệnh');
  assert.deepEqual(loc.map(a => `${a.kind}:${a.name}@${a.palace}${a.value !== undefined ? '=' + a.value : ''}`).sort(),
    ['branch:vị trí@Mệnh=Tuất', 'hoa:Hóa Lộc@Mệnh', 'star:Cự Môn@Mệnh']);
  const ham = triggerAtoms(rule('TV_TH_CU_HAM_GIAN_XAO_DA_NGHI').conditions, f, world(b), 'Mệnh');
  assert.ok(ham.some(a => a.kind === 'dignity' && a.name === 'Cự Môn' && a.value === 'hãm'));
  // the sát count resolves to the actual sát stars and where they sit, not to a number
  const sat = triggerAtoms(rule('TV_TH_STAR_CU_MON_NAM_HAM_SAT').conditions, f, world(b), 'Mệnh');
  assert.ok(sat.some(a => a.kind === 'star' && a.name === 'Kình Dương' && a.palace === 'Mệnh'));
  // a condition that is false on the chart contributes nothing
  assert.deepEqual(triggerAtoms(rule('TV_KL_PHU_CU_TY_NGO_TAM_HOA').conditions, f, world(b), 'Mệnh'), []);
});

test('nesting: the Tân hóa Lộc reading is narrower than the plain hãm reading (same star, more conditions)', () => {
  const b = ex.facts.base, f = factsAt(b, 'Mệnh');
  const sig = (id: string) => signature(triggerAtoms(rule(id).conditions, f, world(b), 'Mệnh'));
  assert.equal(nesting(sig('TV_TH_MV_MENH_CU_THIN_TUAT_LOC'), sig('TV_KL_CT_CU_THU_MENH')), 'narrower');
  assert.equal(nesting(sig('TV_KL_CT_CU_THU_MENH'), sig('TV_TH_CU_HAM_GIAN_XAO_DA_NGHI')), 'same');   // dignity folds into its star
  assert.equal(nesting(sig('TV_TH_AUX_MENH_TA_HUU_NHAN_HAU'), sig('TV_KL_CT_CU_THU_MENH')), 'disjoint');
});

test('qualifiers: Tuần at Mệnh modifies every reading there except the Tuần readings themselves', () => {
  const b = ex.facts.base, f = factsAt(b, 'Mệnh');
  const atoms = triggerAtoms(rule('TV_KL_CT_CU_THU_MENH').conditions, f, world(b), 'Mệnh');
  const hits = evaluateQualifiers(QS, 'Mệnh', atoms, b);
  assert.deepEqual(hits.map(h => [h.id, h.status]), [['Q_KL141_TUAN_TRIET', 'met']]);
  assert.equal(hits[0].onChart[0].name, 'Tuần');
  const tt = triggerAtoms(rule('TV_KL_PHU2_TUAN_TRIET').conditions, f, world(b), 'Mệnh');
  assert.deepEqual(evaluateQualifiers(QS, 'Mệnh', tt, b), []);
});

test('qualifiers data: nine page-cited entries, every effect known, every condition parseable', () => {
  assert.equal(QS.length, 9);
  for (const q of QS) {
    assert.ok(['voids', 'weakens', 'modifies', 'requires_for_durability', 'strengthens'].includes(q.effect), q.id);
    assert.match(q.source, /tr\.\d+/, q.id);
  }
});

test('qualifiers over the corpus: each one is met on some chart and not met on another', { skip: !existsSync(corpusUrl) && 'corpus1000.json.gz not built' }, () => {
  const corpus = JSON.parse(gunzipSync(readFileSync(corpusUrl)).toString('utf8'));
  const seen: Record<string, Set<string>> = Object.fromEntries(QS.map(q => [q.id, new Set<string>()]));
  for (const c of corpus) {
    const b = c.facts.base;
    for (const [pal, stars] of [['Mệnh', ['Lộc Tồn', 'Thiên Mã', 'Tử Vi', 'Thiên Khôi', 'Thiên Việt']], ['Tài Bạch', ['Lộc Tồn', 'Thiên Mã']], ['Quan Lộc', ['Tử Vi']]] as const) {
      const f = b[`palace:${pal}`];
      const atoms = (f['palace.rel.self_stars'] as string[]).filter(s => (stars as readonly string[]).includes(s)).map(s => ({ kind: 'star' as const, name: s, palace: pal }));
      for (const h of evaluateQualifiers(QS, pal, atoms, b, 'tai', 'support')) seen[h.id].add(h.status);
    }
  }
  const lacking = Object.entries(seen).filter(([, s]) => !s.has('met') || !s.has('not_met')).map(([id, s]) => `${id}:${[...s].join('/')}`);
  assert.deepEqual(lacking, []);
});

// ---- P1: lift (rule → concept) and resolve (declared relations) ----
import { lift } from '../kg/lift.ts';
import { resolve } from '../kg/resolve.ts';

test('lift + resolve on the worked example: the book\'s own rescue softens Cự hãm\'s outcome, not its temperament', () => {
  const b = ex.facts.base;
  const { assertions, unlinked } = lift(run(K.rules, K.sources, b).findings.filter(f => f.subject === 'palace:Mệnh' || f.subject === 'chart'), K, b);
  assert.deepEqual(unlinked, []);
  const { resolved } = resolve(assertions.filter(a => a.subject === 'palace:Mệnh' || a.subject === 'chart'), K);
  const st = (rule: string, concept: string) => resolved.find(r => r.ruleId === rule && r.concept === concept);
  assert.equal(st('TV_TH_STAR_CU_MON_NAM_HAM_SAT', 'life.hardship')?.status, 'softened');
  assert.deepEqual(st('TV_TH_STAR_CU_MON_NAM_HAM_SAT', 'life.hardship')?.by.map(x => [x.relation, x.basis, x.cite]), [['REL_TH88_CU_TUAT_TAN_LOC', 'sach', 'TH p.88']]);
  assert.equal(st('TV_TH_CU_HAM_GIAN_XAO_DA_NGHI', 'cog.suspicious')?.status, 'holds');
  assert.equal(st('TV_KL_PHU2_HOA_LOC', 'fin.abundance')?.status, 'weakened');
  assert.equal(st('TV_TH_AUX_MENH_HL_MENH', 'fin.abundance')?.status, 'weakened');
  assert.equal(st('TV_TH_MV_MENH_CU_THIN_TUAT_LOC', 'life.mitigated')?.status, 'holds');
  assert.ok(st('TV_TH_AUX2_MENH_KINH_DAC', 'temper.assertive'), 'Kình đắc địa lifts to quả quyết');
  assert.ok(st('TV_TH_VERSE_MENH_TRIET_TUAN', 'life.early_hardship'), 'Tuần at Mệnh lifts to a hard start, not a hard life');
});

test('KG coverage over the corpus: every verified Mệnh/chart finding is linked; additive độ số never forms a tension; book relations fire',
  { skip: !existsSync(corpusUrl) && 'corpus1000.json.gz not built' }, () => {
  const corpus = JSON.parse(gunzipSync(readFileSync(corpusUrl)).toString('utf8'));
  const unlinked = new Set<string>(), relFired = new Map<string, number>(), ruleFired = new Set<string>();
  let tensions = 0, additiveTension = 0, statuses: Record<string, number> = {};
  const byKey = (rs: ReturnType<typeof resolve>['resolved']) => new Map(rs.map(r => [r.key, r]));
  for (const c of corpus) {
    const b = c.facts.base, fs = run(K.rules, K.sources, b).findings.filter(f => f.subject === 'palace:Mệnh' || f.subject === 'chart');
    const { assertions, unlinked: u } = lift(fs, K, b);
    u.forEach(id => unlinked.add(id));
    fs.forEach(f => ruleFired.add(f.ruleId));
    const { resolved, tensions: ts } = resolve(assertions, K), m = byKey(resolved);
    for (const r of resolved) { statuses[r.status] = (statuses[r.status] ?? 0) + 1; for (const x of r.by) if (x.basis === 'sach') relFired.set(x.relation, (relFired.get(x.relation) ?? 0) + 1); }
    tensions += ts.length;
    additiveTension += ts.filter(t => m.get(t.a)!.additive && m.get(t.b)!.additive).length;
  }
  assert.deepEqual([...unlinked], [], 'verified Mệnh/chart rules without a concept link');
  assert.equal(additiveTension, 0);
  assert.ok(statuses.softened > 0 && statuses.weakened > 0 && statuses.holds > 0, JSON.stringify(statuses));
  // every Mệnh book relation names rules that fire at Mệnh somewhere on the corpus, except one rare configuration (Thái Dương hãm ở Hợi
  // with all three Hóa, male) that the 1,000 charts do not contain; most relations also co-fire. Relations between rules of another
  // palace (Thiên Lương's Tật Ách, TL p.128) are held to the same test in the prose chapter tests.
  const atMenh = (id: string) => !id.startsWith('TV_TL_TAT_ACH_');
  const sach = K.kg!.relations!.filter(r => r.basis === 'sach' && [r.from, ...r.to].every(atMenh));
  assert.deepEqual(sach.flatMap(r => [r.from, ...r.to].filter(id => !ruleFired.has(id)).map(id => `${r.id}:${id}`)),
    ['REL_TH93_NHAT_HAM_HOI_TAM_HOA:TV_TH_STAR_THAI_DUONG_NAM_HAM_HOI_TAM_HOA']);
  assert.ok(sach.filter(r => relFired.has(r.id)).length >= 8, [...relFired.keys()].join(','));
  assert.ok(tensions > 0, 'opposed readings without a relation remain visible as tensions');
});
