// Star dignity has ONE knowledge base (engine/data/dignity_kb.json). Python computes the chart from it; src/interpret/dignity.ts reads
// the same file. These tests prove the layers agree on every star of every palace of every regression and sweep chart: the chart's
// dignity_status (what the badges show), the level fields and fact base (what rules see), and the TS classifier / chart graph (what the
// planner and knowledge graph use). An unknown level must stay unknown everywhere.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { ChartGraph } from '../graph.ts';
import { citeVi, classify, KB, normalizeStar, starId, verifiedLevel, type School } from '../dignity.ts';

const reg = JSON.parse(readFileSync(new URL('./fixtures/charts.json', import.meta.url), 'utf8'));
const sweep = JSON.parse(gunzipSync(readFileSync(new URL('./fixtures/sweep.json.gz', import.meta.url))).toString('utf8'));
const charts = [...reg, ...(Array.isArray(sweep) ? sweep : sweep.charts)];
const LEVELS = new Set(KB.levels);
const SCHOOLS = Object.keys(KB.schools) as School[];

test('chart dignity_status (Python) == TS classify, and level fields / facts / graph agree, on all 12 palaces of every chart', () => {
  let stars = 0, verified = 0;
  for (const c of charts) {
    const school = (c.facts.dignity_school ?? 'thuc_hanh') as School;
    const g = new ChartGraph(c.facts, []);
    assert.equal(c.facts.palaces.length, 12);
    for (const p of c.facts.palaces) {
      const base = c.facts.base[`palace:${p.name}`];
      assert.deepEqual(Object.keys(p.dignity_status).sort(), [...p.stars].sort(), `${p.name}: every star classified`);
      for (const s of p.stars) {
        stars++;
        const py = p.dignity_status[s], ts = classify(s, p.branch, school);
        assert.equal(ts.status, py.status, `${s} @ ${p.branch}`);
        if (ts.status === 'VERIFIED') {
          verified++;
          assert.ok(LEVELS.has(ts.value));
          assert.deepEqual([ts.value, ts.term, ts.school, ts.locator], [py.value, py.term, py.school, py.locator], `${s} @ ${p.branch}`);
        }
        if (ts.status === 'CONFLICT') assert.deepEqual(ts.alternatives, py.alternatives);
        assert.deepEqual('variants' in ts ? ts.variants ?? null : null, py.variants ?? null, `variants ${s} @ ${p.branch}`);
        const lvl = verifiedLevel(s, p.branch, school);
        const node = g.nodes.get(`star:${s}`)!.data!;
        assert.equal(node.dignity, lvl, `graph ${s}`);
        assert.equal(node.dignityStatus, ts.status);
        if (s in p.major_dignity) assert.equal(p.major_dignity[s], lvl, `major_dignity ${s}`);
        if (s in p.minor_dignity) assert.equal(p.minor_dignity[s], lvl, `minor_dignity ${s}`);
        if (`palace.dignity.${s}` in base) assert.equal(base[`palace.dignity.${s}`], lvl ?? 'unspecified', `fact ${s}`);
        if (lvl === null) assert.equal(p.minor_dignity_src?.[s], undefined, `no source tag for unknown ${s}`);
      }
    }
  }
  assert.ok(stars > 5000 && verified > 1000, `coverage ${verified}/${stars}`);
});

test('the knowledge base: every star × 12 branches × 3 schools has exactly one status; only VERIFIED has a level', () => {
  for (const sc of SCHOOLS) for (const [star, row] of Object.entries(KB.resolved[sc])) {
    assert.deepEqual(Object.keys(row).sort(), [...KB.branches].sort(), `${sc}/${star}`);
    for (const r of Object.values(row)) {
      assert.ok(['VERIFIED', 'CONFLICT', 'UNVERIFIED', 'NOT_APPLICABLE'].includes(r.status));
      if (r.status === 'VERIFIED') assert.ok(LEVELS.has(r.value) && /^(TH|TT|KL) pp?\.\d/.test(r.locator) && citeVi(r.locator), `${star}`);
      else assert.equal((r as { value?: unknown }).value, undefined, `${star}: no level outside VERIFIED`);
      if (r.status === 'CONFLICT') assert.ok(r.alternatives.length >= 2);
    }
  }
  assert.equal(Object.keys(KB.stars).length, 102);
});

test('star identifiers: TS slug == Python slug, names / ids / aliases normalise, ambiguous ids refuse to guess', () => {
  for (const [n, m] of Object.entries(KB.stars)) {
    const k = starId(n);
    if (!KB.ambiguous.includes(k)) assert.equal(KB.aliases[k], m.id, n);
    assert.equal(normalizeStar(n), n);
    assert.equal(normalizeStar(m.id), n);
    assert.equal(normalizeStar(n.toUpperCase()), n);
    assert.equal(normalizeStar(n.normalize('NFD')), n);
  }
  assert.equal(normalizeStar('Thiên Diêu'), 'Thiên Riêu');
  assert.equal(normalizeStar('Hoả Tinh'), 'Hỏa Tinh');
  assert.equal(normalizeStar('kinh duong'), 'Kình Dương');
  assert.equal(normalizeStar('Quan Phu'), null);                 // Quan Phủ (Lộc Tồn ring) or Quan Phù (Thái Tuế ring)?
  assert.equal(normalizeStar('Sao Không Có'), null);
  assert.equal(classify('Sao Không Có', 'Tý').status, 'UNVERIFIED');
});

test('pinned cells across schools (page images)', () => {
  assert.deepEqual([classify('Thiên Cơ', 'Dần').status, verifiedLevel('Thiên Cơ', 'Dần')], ['VERIFIED', 'đắc']);   // TH p.30 'Địa Dần Thân'
  assert.equal(classify('Thiên Cơ', 'Thìn').status, 'UNVERIFIED');                                                  // printed 'Ích'
  assert.equal(verifiedLevel('Thiên Cơ', 'Thìn', 'khao_luan'), 'miếu');                                             // KL p.187
  assert.equal(classify('Thái Âm', 'Tý', 'toan_thu').status, 'CONFLICT');                                           // TT p.31 phú vs Hi Di
  assert.equal(classify('Tham Lang', 'Thìn', 'khao_luan').status, 'CONFLICT');                                      // KL p.189 vs p.101
  assert.equal(classify('Tử Vi', 'Ngọ', 'khao_luan').status, 'UNVERIFIED');                                         // KL has no table
  assert.equal(classify('Thiên Thương', 'Dậu').status, 'NOT_APPLICABLE');                                           // TT p.54
  assert.equal(classify('Thiên Khôi', 'Tý').status, 'UNVERIFIED');
  const loc = classify('Lộc Tồn', 'Ngọ');
  assert.ok(loc.status === 'VERIFIED' && loc.school === 'toan_thu' && citeVi(loc.locator) === 'Toàn Thư tr.47');    // fallback, named
  const d = classify('Thiên Đồng', 'Dần');
  assert.ok(d.status === 'VERIFIED' && d.term === 'lợi' && d.value === 'đắc' && d.legacy);                         // legacy, flagged
});
