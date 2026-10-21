// System indices and the overview (docs/PRODUCT-PLAN.md phase 1): deterministic, traceable (every value is the sum of listed items, each
// with a rule id and a page), every vận sentence the Python engine can produce has a side, the tiểu hạn years agree with Python, and the
// response says in words that an index is not a probability.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { Knowledge } from '../types.ts';
import { computeIndices, natalRawAll, DISCLAIMER, KL_RELATION, NORM_SMOOTH, TT_SENTENCES, VAN_RULES, type IndexNorms, type Score } from '../indices.ts';
import { overview, handleOverview } from '../overview.ts';
import { BundledStore } from '../store.ts';
import norms from '../../../engine/data/kg/index_norms.json' with { type: 'json' };

const FX = join(import.meta.dirname, 'fixtures');
const ROOT = join(import.meta.dirname, '..', '..', '..');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const bench = JSON.parse(readFileSync(join(FX, 'benchmark20.json'), 'utf8'));
const ref = bench.find((b: any) => b.label === 'ref_cu_tuat');
const N = norms as IndexNorms;
const r3 = (x: number) => Math.round(x * 1000) / 1000;

test('every value is the sum of its parts, and every part of its items (traceable)', () => {
  const x = computeIndices(ref.facts, K, N);
  const all: Score[] = [...x.palaces, ...x.decades, ...x.years, ...(x.months?.months ?? [])];
  for (const s of all) {
    assert.ok(Math.abs(s.support - s.parts.reduce((a, p) => a + p.support, 0)) < 0.01, 'support = Σ parts');
    assert.ok(Math.abs(s.limit - s.parts.reduce((a, p) => a + p.limit, 0)) < 0.01, 'limit = Σ parts');
    for (const p of s.parts.filter(p => p.layer !== 'ban_menh')) {
      const its = s.items.filter(i => i.layer === p.layer);
      assert.ok(Math.abs(p.support - its.filter(i => i.side === 'support').reduce((a, i) => a + i.w, 0)) < 0.01, `${p.layer} support = Σ items`);
      assert.ok(Math.abs(p.limit - its.filter(i => i.side === 'limit').reduce((a, i) => a + i.w, 0)) < 0.01, `${p.layer} limit = Σ items`);
    }
    for (const i of s.items) { assert.ok(i.id && i.cite && i.text, `item ${i.id} has an id, a cite and a text`); assert.ok(i.w > 0); }
  }
});

test('ban_menh is the ratio to the corpus mean of the same palace: (sum + 1) / (mean + 1)', () => {
  const x = computeIndices(ref.facts, K, N), raw = natalRawAll(ref.facts, K);
  for (const p of x.palaces) {
    const n = N.palace[p.palace];
    assert.equal(p.support, r3((raw[p.palace].support + NORM_SMOOTH) / (n.support + NORM_SMOOTH)));
    assert.equal(p.limit, r3((raw[p.palace].limit + NORM_SMOOTH) / (n.limit + NORM_SMOOTH)));
    assert.ok(p.items.every(i => i.basis === 'sach' && i.layer === 'ban_menh'), 'natal items are verified book findings');
  }
  assert.equal(x.palaces[0].palace, 'Mệnh', 'the radar starts at Mệnh and goes round the board');
  assert.equal(x.palaces.length, 12);
});

test('deterministic: same facts → identical output', () => {
  assert.deepEqual(computeIndices(ref.facts, K, N), computeIndices(structuredClone(ref.facts), K, N));
});

test('đại vận: ten decades, the current one marked, vận readings of the worked example on their side', () => {
  const x = computeIndices(ref.facts, K, N);
  assert.equal(x.decades.length, 10);
  assert.deepEqual(x.decades.filter(d => d.current).map(d => d.palace), [ref.facts.year.dai_han.palace]);
  const huynh = x.decades.find(d => d.palace === 'Huynh Đệ')!;
  assert.ok(huynh.items.some(i => i.id === 'VH_POS_6' && i.side === 'limit'), 'Tham Lang ở Dậu: hao tài (KL pp.233-236) is a limit');
  assert.ok(huynh.items.some(i => i.id === 'KL_DV_VAN_KHAC_TUOI' && i.side === 'limit' && i.cite.includes('230-233')));
  const phu = x.decades.find(d => d.palace === 'Phu Thê')!;
  assert.ok(phu.items.some(i => i.id === 'TH_DAO_HONG_KHOA_QUYEN' && i.side === 'support'));
  assert.ok(phu.items.filter(i => i.id.startsWith('TT_')).every(i => i.basis === 'sach_dien_giai'), 'Toàn Thư paraphrase is labelled');
  assert.ok(phu.support > huynh.support && huynh.limit > phu.limit);
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

test('lưu Tứ Hóa is a low-weight convention, never a book reading', () => {
  const x = computeIndices(ref.facts, K, N);
  const luu = x.years.flatMap(y => y.items.filter(i => i.layer === 'luu_tu_hoa' || i.layer === 'luu_thai_tue'));
  assert.ok(luu.length > 0);
  assert.ok(luu.every(i => i.basis === 'thong_le'));
  assert.ok(luu.filter(i => i.layer === 'luu_tu_hoa').every(i => i.w <= 0.3));
  // 2026 Bính: Lộc Thiên Đồng (Thiên Di), Quyền Thiên Cơ (Phu Thê), Khoa Văn Xương (Tài Bạch) all in the tam phương of tiểu hạn Phúc Đức
  const y26 = x.years.find(y => y.year === 2026)!;
  assert.equal(y26.palace, 'Phúc Đức');
  assert.deepEqual(y26.items.filter(i => i.layer === 'luu_tu_hoa').map(i => i.id).sort(), ['LUU_HOA_KHOA', 'LUU_HOA_LOC', 'LUU_HOA_QUYEN']);
});

test('nguyệt vận: twelve months, each the palace TH p.115 puts it in', () => {
  const x = computeIndices(ref.facts, K, N);
  assert.deepEqual(x.months!.months.map(m => m.month), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);
  for (const m of x.months!.months) assert.equal(ref.facts.year.nguyet_han[m.palace], m.month);
  assert.match(x.months!.basis, /TH tr\.115/);
});

test('every vận sentence the Python engine can write has a side', () => {
  const rules = JSON.parse(readFileSync(join(ROOT, 'engine', 'data', 'van_han_rules.json'), 'utf8')).rules as Array<{ id: string }>;
  assert.deepEqual(rules.map(r => r.id).filter(id => !VAN_RULES[id]), [], 'van_han_rules.json ids without a side');
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
  assert.equal(o.frame?.centre, 'Cự Môn (hãm) ở Mệnh');
  assert.ok(o.frame!.formations.some(f => f.ruleId === 'TV_TH_CACH_MENH_KINH_NHAP_MIEU'));
  assert.ok(o.theses.length >= 2 && o.theses.length <= 3);
  for (const t of o.theses) for (const c of t.claims) assert.ok(c.text && c.rules.length && c.rules.every(r => r.id && r.cite));
  assert.equal(o.theses[0].label, 'Cự Môn (hãm) ở Mệnh');
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
