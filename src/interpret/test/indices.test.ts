// Overview indices (docs/PRODUCT-PLAN.md phase 1; indices-3.0.0, owner's plan of 2026-10-24): the radar is natal only; a period (đại vận,
// year, month) is a weighted sum of layers scaled to their corpus size, not centred (a layer with nothing adds 0), placed on five levels
// anchored at 0. Checked here: every score is the sum of its listed parts; natal findings are never a period's reasons; a period with no
// book item is "Trung bình, chưa đủ căn cứ", a month with nothing to read has no level; KL p.233 (đắc / hãm, the Thái Tuế triad), TH p.115
// (Nam / Bắc đẩu), TH pp.117-118 (lưu đại hạn), the tiểu hạn school (KL pp.39-40 default); counterfactuals; lưu stars and tiểu hạn agree
// with the Python engine; the words carry no rule ids or weights; the Bát Tự strip never enters the Tử Vi score.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import type { ChartInput, Knowledge } from '../types.ts';
import { computeIndices, natalRawAll, luuStars, gistOf, tieuHanBranch, tieuHanRule, luuDaiHanBranch, DISCLAIMER, INDICES_VERSION, KL_RELATION, LEVELS, NORM_SMOOTH,
  TT_SENTENCES, VAN_RULES, VAN_NO_SIDE, TRIAD_RULES, DAU_TINH, TRUNG_TINH, HUNG_TINH, W_DECADE, W_YEAR, W_MONTH, CONVENTION, CONV_K, CONV_FLOOR, LEVEL_DEFAULT, TAT_ACH_NOTE,
  type IndexNorms, type Period } from '../indices.ts';
import { overview, handleOverview } from '../overview.ts';
import { BundledStore } from '../store.ts';
import { TIER_WEIGHT, rarity } from '../reason/tiers.ts';
import norms from '../../../engine/data/kg/index_norms.json' with { type: 'json' };

const FX = join(import.meta.dirname, 'fixtures');
const ROOT = join(import.meta.dirname, '..', '..', '..');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const bench = JSON.parse(readFileSync(join(FX, 'benchmark20.json'), 'utf8'));
const ref = bench.find((b: any) => b.label === 'ref_cu_tuat');
const N = norms as IndexNorms;
const r3 = (x: number) => Math.round(x * 1000) / 1000;
const X = computeIndices(ref.facts, K, N);
const periods = (x: typeof X): Array<Omit<Period, 'level'> & { level: number | null }> => [...x.decades, ...x.years, ...(x.months?.months ?? [])];
const REF = JSON.parse(readFileSync(join(FX, 'ref_2002_01_09_kl.json'), 'utf8')) as ChartInput;

test('norms: current version, a size for every period layer, ordered cut points for each kind of period', () => {
  assert.equal(N.version, INDICES_VERSION);
  assert.equal(N.charts, 1000);
  for (const k of ['hoa_van', 'van', 'vung', 'dai_van', 'tieu_han', 'luu_dai_han', 'dau_tinh', 'luu_sao', 'luu_sao_tl', 'luu_tu_hoa', 'nguyet']) assert.ok(N.layers?.[k] && N.layers[k].rms > 0, `layer ${k}`);
  for (const k of ['decade', 'year', 'month'] as const) {
    const c = N.cuts![k];
    assert.equal(c.length, 4);
    assert.deepEqual([...c].sort((a, b) => a - b), c, `${k} cut points ascend`);
  }
});

test('every period score is the sum of its parts, and each layer part is weight × z of its raw value against the corpus', () => {
  for (const s of periods(X)) {
    assert.ok(Math.abs(s.score - s.parts.reduce((a, p) => a + p.value, 0)) < 0.01, 'score = Σ parts');
    assert.equal(s.level_vi, LEVELS[s.level]);
    for (const p of s.parts) {
      if (p.layer === 'nam' || p.layer === 'thong_le_cap') continue;
      const n = N.layers![p.layer];
      assert.ok(Math.abs(p.z - p.raw / n.rms) < 0.01, `${p.layer}: raw in its corpus size, not centred`);
      assert.ok(Math.abs(p.value - p.weight * p.z) < 0.01, `${p.layer}: value = weight × z`);
      if (p.raw === 0) assert.equal(p.value, 0, `${p.layer}: a layer with nothing adds nothing`);
    }
    for (const i of s.items) { assert.ok(i.id && i.cite && i.text, `item ${i.id} has an id, a cite and a text`); assert.ok(i.w > 0); }
  }
});

test('natal findings are never a period\'s reasons; no natal background or robustness modifier in a score', () => {
  for (const s of periods(X)) assert.ok(s.items.every(i => i.layer !== 'ban_menh'), 'no natal rule listed for a period');
  for (const s of periods(X)) assert.ok(s.parts.every(p => !['nen', 'vung', 'luu_thai_tue'].includes(p.layer)), 'the radar never enters a period score (3.0.0)');
  // the experimental cách cục (all draft) never enter a live score
  assert.ok(periods(X).every(s => s.items.every(i => i.basis !== 'nhap')));
  // the reported bug: TV_KL_CUNG_PHU_THE_THAI_AM (a natal reading of Phu Thê) was listed for decade 23–32 and again for 2026
  assert.ok(!periods(X).some(s => s.items.some(i => i.id.startsWith('TV_'))));
});

test('book before convention: convention weights stay below the book layers, and no convention flips the books\' direction', () => {
  const sum = (o: Record<string, number>, conv: boolean) => Object.entries(o).filter(([k]) => CONVENTION.has(k as any) === conv).reduce((a, [, v]) => a + v, 0);
  assert.ok(sum(W_DECADE, true) < sum(W_DECADE, false) / 2);
  assert.ok(sum(W_YEAR, true) < sum(W_YEAR, false) / 2);
  let capped = 0;
  for (const b of bench) for (const s of [...computeIndices(b.facts, K, N).decades, ...computeIndices(b.facts, K, N).years]) {
    const S = s.parts.filter(p => !CONVENTION.has(p.layer) && p.layer !== 'thong_le_cap').reduce((a, p) => a + p.value, 0);
    const C = s.parts.filter(p => CONVENTION.has(p.layer) || p.layer === 'thong_le_cap').reduce((a, p) => a + p.value, 0);
    assert.ok(Math.abs(C) <= CONV_K * Math.abs(S) + CONV_FLOOR + 0.002, `${b.label}: convention ${C} within the cap of book ${S}`);
    if (Math.abs(S) > 0.01 && Math.sign(C) !== Math.sign(S)) assert.equal(Math.sign(S + C), Math.sign(S), `${b.label}: the books' direction stands`);
    if (s.parts.some(p => p.layer === 'thong_le_cap')) capped++;
  }
  assert.ok(capped > 0, 'the cap is exercised on the benchmark');
});

test('radar: natal ratio to the corpus mean of the same palace, rarity read on the palace the finding stands on', () => {
  const raw = natalRawAll(ref.facts, K);
  for (const p of X.palaces) {
    const n = N.palace[p.palace];
    assert.equal(p.support, r3((raw[p.palace].support + NORM_SMOOTH) / (n.support + NORM_SMOOTH)));
    assert.equal(p.limit, r3((raw[p.palace].limit + NORM_SMOOTH) / (n.limit + NORM_SMOOTH)));
    for (const i of p.items.filter(i => i.scope === 'self')) {
      const t = i.w / (0.5 + rarity(K, i.id, i.palace));
      assert.ok(Object.values(TIER_WEIGHT).some(x => Math.abs(x - t) < 0.01), `${i.id} on ${i.palace}: tier × (0.5 + rarity on its own palace)`);
    }
  }
  assert.equal(X.palaces[0].palace, 'Mệnh', 'the radar starts at Mệnh and goes round the board');
  // before the fix every finding outside Mệnh weighed 0.63 (rarity read on Mệnh, where those rules never fire)
  const outside = X.palaces.flatMap(p => p.items.filter(i => i.scope === 'self' && i.palace !== 'Mệnh'));
  assert.ok(new Set(outside.map(i => i.w)).size > 3);
});

test('deterministic: same facts → identical output', () => {
  assert.deepEqual(computeIndices(ref.facts, K, N), computeIndices(structuredClone(ref.facts), K, N));
});

test('đại vận of the worked example: ten decades, the current one marked, book sentences and the decade stem\'s Tứ Hóa on their side', () => {
  assert.equal(X.decades.length, 10);
  assert.deepEqual(X.decades.filter(d => d.current).map(d => d.palace), [ref.facts.year.dai_han.palace]);
  const huynh = X.decades.find(d => d.palace === 'Huynh Đệ')!;
  assert.ok(huynh.items.some(i => i.id === 'VH_POS_6' && i.side === 'limit'), 'Tham Lang ở Dậu: hao tài (KL pp.233-236) is a limit');
  assert.ok(huynh.items.some(i => i.id === 'KL_DV_VAN_KHAC_TUOI' && i.side === 'limit' && i.cite.includes('230-233')));
  const phu = X.decades.find(d => d.palace === 'Phu Thê')!;
  assert.ok(phu.items.some(i => i.id === 'TH_DAO_HONG_KHOA_QUYEN' && i.side === 'support'));
  // can Bính: Hóa Quyền on Thiên Cơ in Phu Thê itself — a convention, labelled
  assert.ok(phu.items.some(i => i.id === 'DV_HOA_QUYEN' && i.scope === 'self' && i.basis === 'thong_le'));
  assert.ok(phu.items.filter(i => i.id.startsWith('TT_')).every(i => i.basis === 'sach_dien_giai'), 'Toàn Thư paraphrase is labelled');
  // KL p.233 mục 4: every star read by its brightness is a chính, trung or hung tinh with a page-checked level in its own palace
  for (const d of X.decades) for (const i of d.items.filter(i => i.id.startsWith('KL233_'))) {
    const p = ref.facts.palaces.find((q: any) => q.name === i.palace);
    const st = p.dignity_status[i.star!];
    assert.equal(st.status, 'VERIFIED', `${i.star} in ${i.palace}`);
    assert.equal(st.value, i.dignity);
    assert.ok(p.major_stars.includes(i.star) || TRUNG_TINH.includes(i.star!) || HUNG_TINH.includes(i.star!));
    assert.ok(i.cite.includes('KL tr.233') && i.cite.includes(st.locator), i.cite);
    assert.equal(i.side, i.id === 'KL233_HAM' ? 'limit' : 'support');
  }
});

test('counterfactual: the decade stem\'s Tứ Hóa moves the decade; a natal rule, near or far, does not', () => {
  const i = X.decades.findIndex(d => d.palace === 'Phu Thê');
  // give the Phu Thê decade the Tứ Hóa of the Tài Bạch decade's stem (Giáp: Kỵ on Thái Dương)
  const f = structuredClone(ref.facts) as ChartInput;
  const other = f.decades.find(d => d.palace === 'Tài Bạch')!;
  f.decades.find(d => d.palace === 'Phu Thê')!.hoa = other.hoa;
  const y = computeIndices(f, K, N);
  assert.ok(Math.abs(y.decades[i].score - X.decades[i].score) > 0.3, 'another stem\'s Tứ Hóa changes the decade');
  for (const [j, d] of X.decades.entries()) if (j !== i) assert.equal(y.decades[j].score, d.score, 'the other decades stay');
  // natal rules are never in a period score (3.0.0): dropping one, near or far, leaves every decade as it was
  const it = X.palaces.flatMap(p => p.items.filter(i => i.scope === 'self')).sort((a, b) => b.w - a.w)[0];
  const K2 = { ...K, rules: K.rules.filter(r => r.id !== it.id) };
  assert.deepEqual(computeIndices(ref.facts, K2, N).decades.map(d => d.score), X.decades.map(d => d.score), `${it.id} on ${it.palace}`);
});

test('year: the current đại vận carried, lưu stars and lưu Tứ Hóa labelled, 2026 of the worked example', () => {
  const y26 = X.years.find(y => y.year === 2026)!;
  assert.equal(y26.palace, 'Phúc Đức');
  const dv = y26.parts.find(p => p.layer === 'dai_van')!, cur = X.decades.find(d => d.current)!;
  assert.equal(dv.raw, cur.score);
  assert.equal(dv.weight, W_YEAR.dai_van);
  // 2026 Bính: Lộc Thiên Đồng (Thiên Di), Quyền Thiên Cơ (Phu Thê), Khoa Văn Xương (Tài Bạch) all in the tam phương of tiểu hạn Phúc Đức
  assert.deepEqual(y26.items.filter(i => i.layer === 'luu_tu_hoa').map(i => i.id).sort(), ['LUU_HOA_KHOA', 'LUU_HOA_LOC', 'LUU_HOA_QUYEN']);
  assert.ok(X.years.flatMap(y => y.items.filter(i => i.layer === 'luu_tu_hoa')).every(i => i.basis === 'thong_le'));
  // TH tr.114: lưu Khốc, Hư at the tiểu hạn are bad (book); elsewhere their side is a convention
  const luu = X.years.flatMap(y => y.items.filter(i => i.layer === 'luu_sao' || i.layer === 'luu_sao_tl'));
  assert.ok(luu.length > 0);
  for (const i of luu) {
    const book = (i.id === 'LUU_KHOC' || i.id === 'LUU_HU') && i.scope === 'self' || i.id === 'TH_LUU_KHOC_HU_HUNG';
    assert.equal(i.basis, book ? 'sach' : 'thong_le', i.id);
    assert.equal(i.layer, book ? 'luu_sao' : 'luu_sao_tl', `${i.id}: book and convention lưu stars in separate layers`);
  }
  assert.ok(y26.items.some(i => (i.id === 'LUU_KHOC' || i.id === 'LUU_HU') && i.scope === 'self' && i.cite.includes('TH tr.114')));
});

test('lưu stars: the nine of KL tr.41-42 agree with the Python engine on every corpus chart', () => {
  const corpus = JSON.parse(gunzipSync(readFileSync(join(FX, 'corpus1000.json.gz'))).toString('utf8'));
  let n = 0;
  for (const c of corpus) {
    const py = Object.fromEntries((c.facts.year.luu_stars as Array<{ name: string; palace: string; basis: string }>).filter(s => s.basis === 'KL tr.41-42').map(s => [s.name, s.palace]));
    assert.deepEqual(luuStars(c.facts, c.facts.year.year), py, c.birth && JSON.stringify(c.birth));
    n++;
  }
  assert.equal(n, 1000);
});

test('tiểu hạn: the viewed year reads facts.year.tieu_han_tt / tieu_han_kl, the same sentences as the decade entry of that palace', () => {
  for (const b of bench) {
    const x = computeIndices(b.facts, K, N), y = x.years.find(y => y.current)!;
    const f = structuredClone(b.facts);
    delete f.year.tieu_han_tt; delete f.year.tieu_han_kl;
    const y2 = computeIndices(f, K, N).years.find(y => y.current)!;
    assert.deepEqual(y.items, y2.items, b.label);
  }
});

test('tiểu vận: ±10 years, tiểu hạn and lưu Thái Tuế palaces agree with the Python engine for every benchmark chart', () => {
  const py = JSON.parse(readFileSync(join(FX, 'tieu_han_years.json'), 'utf8'));
  let n = 0;
  for (const b of bench) {
    const x = computeIndices(b.facts, K, N);
    assert.equal(x.years.filter(y => y.current).length, 1);
    for (const y of x.years) {
      const e = py[b.label][y.year];
      if (!e) continue;
      assert.deepEqual([y.palace, y.thai_tue], e, `${b.label} ${y.year}`);
      n++;
    }
  }
  assert.ok(n > 300);
});

test('nguyệt vận: twelve months where TH p.115 / KL pp.40-41 put them, the year\'s level stepped by the stars of the month palace', () => {
  const yv = X.years.find(y => y.current)!;
  assert.deepEqual(X.months!.months.map(m => m.month), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);
  for (const m of X.months!.months) {
    assert.equal(ref.facts.year.nguyet_han[m.palace], m.month);
    assert.equal(m.parts[0].value, yv.score);
    assert.ok(Math.abs(m.score - yv.score - W_MONTH * m.parts[1].z) < 0.01);
    assert.ok(m.items.every(i => i.id.startsWith('KL233_')), 'a month reads the brightness of its stars only');
    assert.equal(m.level === null, m.items.length === 0, 'no level of its own when there is nothing to read');
    if (m.level === null) assert.match(m.text.at(-1)!, /chưa xác định/);
  }
  assert.match(X.months!.basis, /TH tr\.115/);
});

test('tiểu hạn school: KL pp.39-40 by default, TH p.27 for older facts made with it; months and lưu stars follow', () => {
  // the 2002 reference (âm nam) was made with TH p.27: 2026 at Thân (Phu Thê); KL pp.39-40 walks âm nam nghịch: Ngọ (Tài Bạch)
  assert.equal(tieuHanRule(REF), 'TH');
  const th = computeIndices(REF, K, N), kl = computeIndices({ ...REF, tieu_han_rule: 'KL' }, K, N);
  assert.equal(th.years.find(y => y.current)!.palace, 'Phu Thê');
  assert.equal(kl.years.find(y => y.current)!.palace, 'Tài Bạch');
  assert.equal(kl.tieu_han_rule.rule, 'KL');
  assert.match(kl.tieu_han_rule.label, /Khảo Luận tr\.39-40/);
  // the same count from the KL tiểu hạn: tháng Giêng at Tuất (Mệnh), as engine/tests/test_luu_nguyet.py
  assert.equal(kl.months!.months[0].palace, 'Mệnh');
  assert.equal(kl.months!.months[11].palace, 'Huynh Đệ');
  // dương nam (thuận) and dương nữ (nghịch): the two books walk the same way; âm nam and âm nữ go the other way in KL
  for (const b of bench.filter((b: any) => ['dương nam', 'dương nữ'].includes(b.facts.yin_yang_gender)))
    for (const age of [1, 7, 26, 40]) assert.equal(tieuHanBranch(b.facts, age, 'KL'), tieuHanBranch(b.facts, age, 'TH'));
});

test('lưu đại hạn: TH pp.117-118, the book\'s worked example, and the first year of each decade at the decade palace', () => {
  // decade at Tử (Hợi) from 32, nghịch: 33 Tỵ, 34 Ngọ, 35 Tỵ, 36 Thìn, 37 Mão, 38 Dần, 39 Sửu
  assert.deepEqual([0, 1, 2, 3, 4, 5, 6, 7].map(k => luuDaiHanBranch(11, -1, k)), [11, 5, 6, 5, 4, 3, 2, 1]);
  for (const y of X.years) {
    if (y.decade === null) { assert.equal(y.luu_dai_han, null); continue; }
    const d = X.decades[y.decade];
    if (y.age === d.age_from) assert.equal(y.luu_dai_han, d.palace);
    for (const i of y.items.filter(i => i.layer === 'luu_dai_han')) assert.match(i.cite, /TH tr\.117-118/);
  }
});

test('TH p.115 IX: Nam / Bắc đẩu chính tinh of the hạn by âm dương, Bắc đẩu in the first five years of the đại hạn, Nam đẩu in the last five', () => {
  for (const b of bench.slice(0, 8)) {
    const x = computeIndices(b.facts, K, N), g = ['dương nam', 'âm nữ'].includes(b.facts.yin_yang_gender) ? 'nam' : 'bac';
    for (const d of x.decades) for (const i of d.items.filter(i => i.id.startsWith('TH115_'))) {
      assert.equal(i.id, g === 'nam' ? 'TH115_NAM_DAU' : 'TH115_BAC_DAU');
      assert.equal(i.side, 'support');
    }
    for (const y of x.years) for (const i of y.items.filter(i => i.layer === 'dau_tinh')) {
      const d = x.decades[y.decade!], first = y.age - d.age_from < 5, grp = DAU_TINH[i.star!].group;
      assert.ok(grp === 'ca_hai' || grp === (first ? 'bac' : 'nam'), `${b.label} ${y.year}: ${i.star}`);
      assert.equal(i.palace, d.palace);
    }
  }
});

test('KL p.233: the Thái Tuế triad weighs as one full sentence; xung chiếu refused and nhị hợp counted as the book says', () => {
  for (const id of TRIAD_RULES) assert.equal(VAN_RULES[id].w, 1);
  const huynh = computeIndices(REF, K, N).decades.find(d => d.palace === 'Huynh Đệ')!;
  assert.ok(huynh.items.some(i => i.id === 'VH_QUAN_PHU' && i.w === 1 && /bất kể Mệnh/.test(i.cite)));
  for (const b of bench) {
    const x = computeIndices(b.facts, K, N);
    x.decades.forEach((d, j) => {
      const kl = (b.facts.decades[j] as any).kl;
      if (kl?.xung_controlled) assert.ok(!d.items.some(i => i.id === 'KL233_HAM' && i.scope === 'opp'), 'the opposite\'s hãm stars are refused');
      if (!kl?.nhi_hop?.counts) assert.ok(!d.items.some(i => i.scope === 'nhi_hop'), 'nhị hợp only when it generates the vận');
      // a triad decade drawn low says why
      if (!d.insufficient && d.level <= 1 && d.items.some(i => TRIAD_RULES.has(i.id))) assert.match(d.text.at(-1)!, /tam hợp Thái Tuế/);
    });
  }
});

test('no book evidence: "Trung bình" flagged "chưa đủ căn cứ", never a real middle; a month with nothing to read has no level', () => {
  const f = structuredClone(REF) as any;
  for (const p of f.palaces) { p.dignity_status = {}; p.major_stars = []; }
  for (const d of f.decades) { d.readings = []; d.tt = []; d.kl = null; }
  f.year.tieu_han_tt = []; f.year.tieu_han_kl = null;
  const x = computeIndices(f, K, N);
  for (const d of x.decades) {
    assert.ok(d.insufficient);
    assert.equal(d.level, LEVEL_DEFAULT);
    assert.match(d.text.at(-1)!, /chưa đủ căn cứ/);
    assert.ok(d.notes.some(n => /chưa đủ căn cứ/.test(n.text)));
  }
  for (const y of x.years.filter(y => !y.items.some(i => i.basis === 'sach'))) assert.ok(y.insufficient && y.level === LEVEL_DEFAULT);
  for (const m of x.months!.months) { assert.equal(m.level, null); assert.equal(m.level_vi, 'Chưa xác định'); }
});

test('lưu Tứ Hóa is not counted again when the year stem is the đại hạn stem; the radar says what Tật Ách is not', () => {
  let n = 0;
  for (const b of bench) {
    const x = computeIndices(b.facts, K, N);
    for (const y of x.years) {
      if (y.decade === null || x.decades[y.decade].stem !== y.can_chi.split(' ')[0]) continue;
      assert.ok(!y.items.some(i => i.layer === 'luu_tu_hoa'), `${b.label} ${y.year}`);
      n++;
    }
  }
  assert.ok(n > 0);
  assert.equal(X.radar_note, TAT_ACH_NOTE);
  assert.match(TAT_ACH_NOTE, /không phải dự đoán sức khỏe hay chẩn đoán y khoa/);
});

test('words: two to four plain sentences per decade and year; no rule ids, weights or decimals outside "Căn cứ"', () => {
  for (const b of bench) {
    const x = computeIndices(b.facts, K, N);
    for (const s of [...x.decades, ...x.years]) {
      assert.ok(s.text.length >= 2 && s.text.length <= 4, `${b.label}: ${s.text.length} sentences`);
      assert.doesNotMatch(s.text.join(' '), /undefined|null|NaN/);
      for (const t of s.text) {
        assert.doesNotMatch(t, /\b[A-Z]{2,}_[A-Z0-9_]+\b/, `rule id in "${t}"`);
        assert.doesNotMatch(t, /trọng số|điểm chuẩn|\d,\d/, `method words or decimals in "${t}"`);
        assert.match(t, /[.!?]$/);
      }
      assert.ok(s.text.at(-1)!.includes(`“${s.level_vi}”`), 'the last sentence names the level');
    }
  }
  assert.equal(gistOf('Vận có Tham Lang ở Dậu: theo sách hao tài, phóng túng.'), 'vận có Tham Lang ở Dậu thì hao tài, phóng túng');
  assert.equal(gistOf('Mệnh có Tử Phủ Vũ Tướng mà cung vận có Kình Dương: theo sách đây lại là dịp đi lên.'), 'Mệnh có Tử Phủ Vũ Tướng mà cung vận có Kình Dương, đây lại là dịp đi lên');
});

test('the levels spread over the benchmark charts (not all in one level)', () => {
  const h = [0, 0, 0, 0, 0];
  for (const b of bench) for (const d of computeIndices(b.facts, K, N).decades) h[d.level]++;
  assert.ok(h.filter(c => c > 0).length === 5, `decade levels ${h}`);
  assert.ok(Math.max(...h) / h.reduce((a, c) => a + c, 0) < 0.5, `decade levels ${h}`);
});

test('Bát Tự strip: luck pillars tagged by the điều hậu table, beside the decades and never in the Tử Vi score', () => {
  const s = X.bazi!;
  assert.ok(s && s.pillars.length >= 8);
  assert.match(s.basis, /389-396/);
  assert.ok(s.pillars.every(p => ['dung', 'hy', 'khong'].includes(p.tag)));
  assert.equal(s.pillars.filter(p => p.current).length, 1);
  const f = structuredClone(ref.facts);
  delete f.bazi;
  const y = computeIndices(f, K, N);
  assert.equal(y.bazi, null);
  assert.deepEqual(y.decades.map(d => d.score), X.decades.map(d => d.score));
  assert.deepEqual(y.years.map(d => d.score), X.years.map(d => d.score));
});

test('every vận sentence the Python engine can write has a side', () => {
  const rules = JSON.parse(readFileSync(join(ROOT, 'engine', 'data', 'van_han_rules.json'), 'utf8')).rules as Array<{ id: string }>;
  assert.deepEqual(rules.map(r => r.id).filter(id => !VAN_RULES[id] && !VAN_NO_SIDE.has(id)), [], 'van_han_rules.json ids without a side');
  for (const id of VAN_NO_SIDE) assert.ok(!VAN_RULES[id] && rules.some(r => r.id === id), id);
  const py = readFileSync(join(ROOT, 'engine', 'tvbt', 'van_han_tt.py'), 'utf8');
  const sentences = [...py.matchAll(/add\("([^"]+)"/g)].map(m => m[1]);
  assert.ok(sentences.length >= 30);
  assert.deepEqual(sentences.filter(s => !TT_SENTENCES.some(t => s.startsWith(t.prefix))), [], 'Toàn Thư sentences without a side');
  const ids = TT_SENTENCES.map(t => t.id);
  assert.equal(new Set(ids).size, ids.length);
  const an = readFileSync(join(ROOT, 'engine', 'tvbt', 'analysis.py'), 'utf8');
  const rels = [...an.slice(an.indexOf('def age_vs_dai_van'), an.indexOf('def dai_van_facts')).matchAll(/return "([^"]+)"/g)].map(m => m[1]);
  assert.deepEqual(rels.filter(r => r !== 'cùng hành' && !KL_RELATION[r]), [], 'Khảo Luận relations without a side');
});

test('overview: the reasoner frame and theses of the worked example, the disclaimer in words', () => {
  const o = overview(ref.facts, K);
  assert.equal(o.disclaimer, DISCLAIMER);
  assert.match(o.disclaimer, /không phải xác suất hay dự báo/);
  assert.equal(o.frame?.branch, 'Tuất');
  // Cự Môn, or the Kình Dương formation seat now that Toàn Thư's 'Kình miếu' fires on its own table (owner review 2026-10-22 item 8)
  assert.ok(['Cự Môn (hãm) ở Mệnh', 'Kình Dương ở Mệnh'].includes(o.frame?.centre ?? ''), o.frame?.centre);
  assert.ok(o.frame!.formations.some(f => f.ruleId === 'TV_TH_CACH_MENH_KINH_NHAP_MIEU'));
  assert.ok(o.theses.length >= 2 && o.theses.length <= 3);
  for (const t of o.theses) for (const c of t.claims) assert.ok(c.text && c.rules.length && c.rules.every(r => r.id && r.cite));
  assert.equal(o.theses[0].label, 'Cự Môn (hãm) ở Mệnh');
  assert.deepEqual(o.indices.cuts, N.cuts);
});

test('handleOverview: off unless enabled, POST only, facts errors pass through, otherwise the overview', async () => {
  const store = new BundledStore(K);
  const facts = async () => new Response(JSON.stringify(ref.facts));
  const req = (m = 'POST') => new Request('http://x/api/overview', { method: m, body: m === 'POST' ? JSON.stringify(ref.birth) : undefined });
  assert.equal((await handleOverview(req(), { enabled: false, facts, store })).status, 404);
  assert.equal((await handleOverview(req('GET'), { enabled: true, facts, store })).status, 405);
  assert.equal((await handleOverview(req(), { enabled: true, facts: async () => new Response('{"detail":"bad"}', { status: 422 }), store })).status, 422);
  const r = await handleOverview(req(), { enabled: true, facts, store });
  assert.equal(r.status, 200);
  const o = await r.json() as ReturnType<typeof overview>;
  assert.equal(o.indices.decades.length, 10);
  assert.equal(o.indices.norms?.charts, 1000);
});

test('TH p.115 IX / p.117 6n vận sentences (3.1.0): each takes its book side; "không hề gì" is told but never scored', () => {
  const add = (rule_id: string) => {
    const f = structuredClone(ref.facts);
    f.decades[3].readings.push({ text: `câu ${rule_id}`, src: 'Thực Hành pp.115-117', rule_id });
    return computeIndices(f, K, N).decades.find(d => d.palace === f.decades[3].palace)!;
  };
  const base = X.decades.find(d => d.palace === ref.facts.decades[3].palace)!;
  for (const id of ['TH_IX6_GIAP_THUONG_SU', 'TH_IX6_CANH_THUONG_SU', 'TH_IX9_THAN_THUONG', 'TH_6N_SPT_TANG_HO']) {
    const d = add(id);
    assert.equal(d.items.find(i => i.id === id)?.side, 'limit', id);
    assert.ok(d.score < base.score, id);
  }
  const up = add('TH_IX10_TU_MO_KINH_DA_PHAT');
  assert.equal(up.items.find(i => i.id === 'TH_IX10_TU_MO_KINH_DA_PHAT')?.side, 'support');
  assert.ok(up.score > base.score);
  const none = add('TH_IX10_TU_MO_KINH_DA');
  assert.ok(!none.items.some(i => i.id === 'TH_IX10_TU_MO_KINH_DA'));
  assert.equal(none.score, base.score);
});
