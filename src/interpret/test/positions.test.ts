// Positional relations and position guards (plan quirky-tinkering-rabin R1): relationOf on hand cases, the Hóa carrier on the worked-example
// chart (Tân Mùi: Hóa Lộc on Cự Môn at Mệnh Tuất), guard pass/fail, every guard names a real pack rule, and over the corpus a guard never
// blocks what the rule's own condition already guarantees.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { relationOf, isNhiHop, hoaCarrier, guardHolds, type PositionGuard } from '../reason/positions.ts';
import { triggerAtoms, type Atom } from '../kg/atoms.ts';
import { evaluate } from '../dsl.ts';
import type { Expr, Facts } from '../types.ts';
import guardsFile from '../../../engine/data/kg/position_guards.json' with { type: 'json' };

const GUARDS = (guardsFile as unknown as { guards: PositionGuard[] }).guards;
const DATA = new URL('../../../engine/data/', import.meta.url);
const PACK_RULES = readdirSync(DATA).filter(f => /^pack_.*\.json$/.test(f))
  .flatMap(f => (JSON.parse(readFileSync(new URL(f, DATA), 'utf8')).rules ?? []) as Array<{ id: string; system: string; conditions: Expr }>);
const RULE = new Map(PACK_RULES.map(r => [r.id, r]));
const ex = JSON.parse(readFileSync(new URL('./fixtures/menh_cu_tuat.json', import.meta.url), 'utf8'));
const P = ex.facts.palaces as Array<{ name: string; branch_index: number }>;
const factsAt = (base: Record<string, Facts>, palace: string): Facts => ({ ...(base.chart ?? {}), ...base[`palace:${palace}`] });
const world = (base: Record<string, Facts>) => (n: string) => base[`palace:${n}`] ?? null;
const star = (name: string, palace: string | null): Atom => ({ kind: 'star', name, palace });
const hoa = (name: string, palace: string | null): Atom => ({ kind: 'hoa', name, palace });
const guard = (id: string) => GUARDS.find(g => g.ruleId === id)!;

test('relationOf: seats relative to Mệnh Tuất from branch indices', () => {
  // the worked example: Mệnh Tuất(10), Thiên Di Thìn(4), Tài Bạch Ngọ(6), Quan Lộc Dần(2), Phụ Mẫu Hợi(11), Huynh Đệ Dậu(9), Phúc Đức Tý(0)
  assert.equal(relationOf('Mệnh', 'Mệnh', P), 'self');
  assert.equal(relationOf('Thiên Di', 'Mệnh', P), 'opp');
  assert.equal(relationOf('Tài Bạch', 'Mệnh', P), 'trine');
  assert.equal(relationOf('Quan Lộc', 'Mệnh', P), 'trine');
  assert.equal(relationOf('Phụ Mẫu', 'Mệnh', P), 'flank');
  assert.equal(relationOf('Huynh Đệ', 'Mệnh', P), 'flank');
  assert.equal(relationOf('Phúc Đức', 'Mệnh', P), 'elsewhere');
  assert.equal(relationOf('Nô Bộc', 'Mệnh', P), 'elsewhere');
  // relative to another palace, and wrap-around at Tý
  assert.equal(relationOf('Mệnh', 'Thiên Di', P), 'opp');
  assert.equal(relationOf('Phúc Đức', 'Phụ Mẫu', P), 'flank');
  assert.equal(relationOf('Điền Trạch', 'Tử Tức', P), 'opp');
  assert.equal(relationOf(null, 'Mệnh', P), null);
  assert.equal(relationOf('Mệnh', 'Thân', P), null);
  // nhị hợp: Mão–Tuất (Nô Bộc with Mệnh here), not Mệnh with itself or with its neighbour
  assert.equal(isNhiHop('Nô Bộc', 'Mệnh', P), true);
  assert.equal(isNhiHop('Phụ Mẫu', 'Mệnh', P), false);
  assert.equal(isNhiHop('Mệnh', 'Mệnh', P), false);
});

test('hoaCarrier: Tân Mùi puts Hóa Lộc on Cự Môn at Mệnh, Hóa Kỵ on Văn Xương at Tài Bạch', () => {
  assert.equal(ex.facts.year_gz, 'Tân Mùi');
  assert.deepEqual(hoaCarrier(ex.facts, 'Hóa Lộc'), { star: 'Cự Môn', palace: 'Mệnh' });
  assert.deepEqual(hoaCarrier(ex.facts, 'Hóa Quyền'), { star: 'Thái Dương', palace: 'Tài Bạch' });
  assert.deepEqual(hoaCarrier(ex.facts, 'Hóa Kỵ'), { star: 'Văn Xương', palace: 'Tài Bạch' });
  assert.deepEqual(hoaCarrier(ex.facts, 'Hóa Khoa'), { star: 'Văn Khúc', palace: 'Phu Thê' });
  assert.equal(hoaCarrier(ex.facts, 'Hóa Nhạc'), null);
  // the per-palace facts only list the Hóa name: the carrier comes from the table
  assert.deepEqual(ex.facts.base['palace:Mệnh']['palace.tu_hoa'], ['Hóa Lộc']);
});

test('guards: a seat wider than the book fails, the book seat passes', () => {
  // TH p.55 "Đào, Hồng chỉ xung chiếu Mệnh (không đóng ở Mệnh)": the condition takes the whole tam phương, the book only the opposite palace
  const g = guard('TV_TH_AUX_MENH_DH_CHIEU');
  assert.equal(g.certainty, 'certain');
  assert.equal(guardHolds(g, [star('Đào Hoa', 'Thiên Di')], P), true);
  assert.equal(guardHolds(g, [star('Đào Hoa', 'Tài Bạch')], P), false);
  assert.equal(guardHolds(g, [star('Hồng Loan', 'Thiên Di'), star('Đào Hoa', 'Quan Lộc')], P), false);
  // an atom with no palace cannot be checked: fail closed; an atom the guard does not name is ignored; no named atom present: vacuous
  assert.equal(guardHolds(g, [star('Đào Hoa', null)], P), false);
  assert.equal(guardHolds(g, [star('Thiên Hỷ', 'Mệnh')], P), true);
  assert.equal(guardHolds(g, [], P), true);
  // TH p.52 "Lộc Tồn ở Mệnh có Phá Quân chính chiếu": Phá Quân in Mệnh itself does not count
  const lp = guard('TV_TH_AUX_MENH_LOC_PHA');
  assert.equal(guardHolds(lp, [star('Lộc Tồn', 'Mệnh'), star('Phá Quân', 'Thiên Di')], P), true);
  assert.equal(guardHolds(lp, [star('Lộc Tồn', 'Mệnh'), star('Phá Quân', 'Mệnh')], P), false);
  // KL p.66 "Khoa Quyền Lộc hội mà Hóa Kỵ hoặc Kình đồng cung": mixed scopes; Kình must be in Mệnh, the three Hóa anywhere in the tam phương
  const kk = guard('TV_KL_STAR_MENH_TAM_KY_KY_KINH');
  assert.ok(kk.kinds!.includes('mixed'));
  assert.equal(guardHolds(kk, [hoa('Hóa Lộc', 'Tài Bạch'), star('Kình Dương', 'Mệnh')], P), true);
  assert.equal(guardHolds(kk, [hoa('Hóa Lộc', 'Tài Bạch'), star('Kình Dương', 'Thiên Di')], P), false);
  assert.equal(guardHolds(kk, [hoa('Hóa Lộc', 'Phụ Mẫu')], P), false);
});

test('guards: a Hóa the book binds to a star must ride that star', () => {
  // TH p.88 "Cự Môn hãm ở Thìn/Tuất nhưng hóa Lộc (tuổi Tân)": on the worked example the rule fires and the Lộc does ride Cự Môn
  const g = guard('TV_TH_MV_MENH_CU_THIN_TUAT_LOC');
  const r = g.requires.find(x => x.atom === 'Hóa Lộc')!;
  assert.equal(r.carrier, 'Cự Môn');
  const b = ex.facts.base, f = factsAt(b, 'Mệnh');
  const atoms = triggerAtoms(RULE.get(g.ruleId)!.conditions, f, world(b), 'Mệnh');
  assert.ok(atoms.some(a => a.kind === 'hoa' && a.name === 'Hóa Lộc' && a.palace === 'Mệnh'));
  assert.equal(guardHolds(g, atoms, P, { tuHoa: ex.facts.tu_hoa }), true);
  // same palace, but the Lộc rides another star (e.g. a Mệnh Cự Môn + Thái Dương of a Canh-like table): blocked
  assert.equal(guardHolds(g, atoms, P, { tuHoa: { ...ex.facts.tu_hoa, 'Hóa Lộc': { star: 'Thái Dương', branch: 10 } } }), false);
  // without the table the carrier cannot be checked
  assert.equal(guardHolds(g, atoms, P), false);
  // KL p.246 "Thái Âm hãm hóa Quyền ở Mệnh"
  const q = guard('TV_KL_CASE_MENH_AM_HAM_QUYEN');
  const qa = [star('Thái Âm', 'Mệnh'), hoa('Hóa Quyền', 'Mệnh')];
  assert.equal(guardHolds(q, qa, P, { tuHoa: { 'Hóa Quyền': { star: 'Thái Âm', branch: 10 } } }), true);
  assert.equal(guardHolds(q, qa, P, { tuHoa: { 'Hóa Quyền': { star: 'Thiên Đồng', branch: 10 } } }), false);
});

test('guards: needs-reading tightenings apply only in strict mode; @palace resolves to the firing palace', () => {
  const soft = GUARDS.find(g => g.requires.some(r => r.from === 'book?' && !r.carrierCandidates && r.relation === 'self'))!;
  assert.ok(soft, 'some guard has a needs-reading own-palace tightening');
  const r = soft.requires.find(x => x.from === 'book?' && x.relation === 'self')!;
  const target = r.of === '@palace' ? 'Mệnh' : r.of;
  const far = P.find(p => relationOf(p.name, target, P) === 'trine')!.name;
  assert.equal(guardHolds(soft, [star(r.atom, far)], P, { here: 'Mệnh' }), true);
  assert.equal(guardHolds(soft, [star(r.atom, far)], P, { here: 'Mệnh', strict: true }), false);
  const anywhere: PositionGuard = { ruleId: 'x', requires: [{ atom: 'Thiên Mã', relation: 'opp', of: '@palace' }], reason: '', cite: '', review: 'draft' };
  assert.equal(guardHolds(anywhere, [star('Thiên Mã', 'Mệnh')], P, { here: 'Thiên Di' }), true);
  assert.equal(guardHolds(anywhere, [star('Thiên Mã', 'Mệnh')], P), false);
});

test('every guard names a Tử Vi rule of a pack, and only atoms that rule tests', () => {
  assert.ok(GUARDS.length > 0);
  assert.equal(new Set(GUARDS.map(g => g.ruleId)).size, GUARDS.length, 'one entry per rule');
  for (const g of GUARDS) {
    const r = RULE.get(g.ruleId);
    assert.ok(r, `${g.ruleId} is in a pack`);
    assert.equal(r!.system, 'tu_vi', g.ruleId);
    assert.equal(g.review, 'draft');
    const cond = JSON.stringify(r!.conditions);
    for (const q of g.requires) {
      assert.ok(cond.includes(`"${q.atom}"`) || /khi\.|sat_pha_tham/.test(cond), `${g.ruleId}: ${q.atom} is tested by the rule`);
      assert.ok(q.of === '@palace' || cond.includes(`"${q.of}"`), `${g.ruleId}: of ${q.of}`);
    }
  }
});

test('over the corpus, a guard never blocks what its rule\'s own condition guarantees', () => {
  const corpus = JSON.parse(gunzipSync(readFileSync(new URL('./fixtures/corpus1000.json.gz', import.meta.url))).toString('utf8')) as Array<{ facts: any }>;
  const charts = [ex.facts, ...corpus.slice(0, 250).map(c => c.facts)];
  let fired = 0, blocked = 0;
  for (const facts of charts) {
    const b = facts.base as Record<string, Facts>;
    for (const g of GUARDS) {
      const rule = RULE.get(g.ruleId)!;
      for (const p of facts.palaces as Array<{ name: string }>) {
        const f = factsAt(b, p.name);
        if (evaluate(rule.conditions, f, world(b)) !== true) continue;
        fired++;
        const atoms = triggerAtoms(rule.conditions, f, world(b), p.name);
        const own = { ...g, requires: g.requires.filter(r => r.from === 'condition') };
        assert.equal(guardHolds(own, atoms, facts.palaces, { here: p.name, tuHoa: facts.tu_hoa }), true, `${g.ruleId} at ${p.name}`);
        if (!guardHolds(g, atoms, facts.palaces, { here: p.name, tuHoa: facts.tu_hoa })) blocked++;
      }
    }
  }
  assert.ok(fired > 100, `guarded rules fired ${fired} times`);
  assert.ok(blocked > 0 && blocked < fired, `certain guards block some firings (${blocked} of ${fired})`);
});
