// Regression and quality invariants of the deterministic interpretation pipeline (Công danh chapter).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { DatabaseSync } from 'node:sqlite';
import { interpret } from '../pipeline.ts';
import { run } from '../engine.ts';
import { D1Store, LayeredCache, cacheKey, type D1Like } from '../store.ts';
import type { Knowledge } from '../types.ts';

const K: Knowledge = JSON.parse(readFileSync(new URL('../generated/knowledge.json', import.meta.url), 'utf8'));
const charts = JSON.parse(readFileSync(new URL('./fixtures/charts.json', import.meta.url), 'utf8'));
const REF = charts[0];                                   // 17/05/1990 10:30 nam — the regression case
const words = (t: string) => t.split(/\s+/).filter(w => /[\p{L}\p{N}]/u.test(w)).length;

test('17/05/1990: the Công danh chapter passes the quality checks and stays within the word budget', () => {
  const o = interpret(REF.facts, 'cong_danh', K);
  assert.equal(o.quality.pass, true, JSON.stringify(o.quality.errors));
  assert.deepEqual(o.quality.warnings, []);
  const wc = words(o.text);
  assert.ok(wc >= 800 && wc <= 1500, `words ${wc}`);
  assert.ok(o.quality.metrics.repeated4gramRate < 0.08);
  assert.ok(o.quality.metrics.personalization >= 0.6);
  assert.equal(o.quality.editorial.allApproved, false);   // modules are drafts until an expert approves them; the output says so
});

test('17/05/1990: central configuration, grounds, dominance, cross-palace links and timing are the ones the chart supports', () => {
  const o = interpret(REF.facts, 'cong_danh', K), t = o.text;
  // central configuration (facts)
  assert.match(t, /Quan Lộc, an tại Canh Thìn/);
  assert.match(t, /Tử Vi \(vượng\) và Thiên Tướng \(vượng\)/);
  assert.match(t, /Địa Kiếp/);
  // two Toàn Thư sentences on the same pairing are ONE ground
  assert.match(t, /“quyền quý” và “trong ngoài đều có quyền quý”[^.]*một căn cứ/);
  // the sát-star readings are one factor seen from several sides, and the Toàn Thư 'gặp sát tinh' reading names the sát stars
  assert.match(t, /Địa Kiếp trong khung đọc của Quan Lộc/);
  assert.match(t, /sát tinh Địa Kiếp và Linh Tinh \(từ Phu Thê\) hội về Quan Lộc/);
  // dominance: explicit criteria, verdict and the same-book note
  assert.match(t, /năm tiêu chí (cố định|công khai)/);
  assert.match(t, /điều chỉnh mức độ chứ không phải lời phủ định/);
  assert.match(t, /Toàn Thư tự đặt hai câu này trong cùng mục bàn về Tử Vi ở cung Quan Lộc/);
  // cross-palace links come from the knowledge graph (a Mệnh reading that needs Tử Vi in Quan Lộc; Lộc Mã from Tài Bạch)
  assert.match(t, /“tạo được uy quyền hiển hách”.{0,160}Tử Vi nằm ở cung Quan Lộc/);
  assert.match(t, /Lộc Tồn và Thiên Mã nằm ở cung Tài Bạch/);
  // timing: late vs early readings kept apart, decade through Quan Lộc, vận readings that disagree are not resolved
  assert.match(t, /46–55 tuổi mụ/);
  assert.match(t, /không kết luận chặng ấy đi lên hay đi xuống/);
  assert.match(t, /giữ cả hai thay vì chọn một/);
  // what is deliberately not used
  assert.match(t, /không được áp sang Quan Lộc|không chuyển chúng sang Quan Lộc/);
  assert.match(t, /chưa được đối chiếu đủ|chưa đối chiếu đủ/);
  // rule-integrity regressions found on this chart are not in the text
  assert.doesNotMatch(t, /Nhật Nguyệt giáp/);
  assert.doesNotMatch(t, /ở cung Mệnh” \(Thực Hành tr\.72\)/);
});

test('every book sentence of every regression chart rests on fired, verified rules; no banned wording; deterministic', () => {
  for (const c of charts) {
    const o = interpret(c.facts, 'cong_danh', K);
    const verified = new Set(run(K.rules, K.sources, c.facts.base).findings.filter(f => f.basis === 'verified').map(f => f.ruleId));
    for (const s of o.paragraphs.flatMap(p => p.sentences)) {
      if (s.basis === 'sach') assert.ok(s.rules.length || s.cites.length, s.text);
      if (s.basis === 'sach') for (const r of s.rules) if (!r.startsWith('VH_')) assert.ok(verified.has(r), `${r} in ${s.text}`);
      assert.doesNotMatch(s.text, /chắc chắn|định mệnh|tai họa|sẽ bị|tuyệt đối/i);
    }
    assert.equal(o.quality.errors.length, 0, `${c.label}: ${JSON.stringify(o.quality.errors)}`);
    const again = interpret(c.facts, 'cong_danh', K).text;
    if (again !== o.text) { const a = o.text.split('. '), b = again.split('. '); console.log('NONDET', c.label, a.find((x, i) => x !== b[i]), '||', b.find((x, i) => x !== a[i])); }
    assert.equal(again, o.text);
    assert.ok(words(o.text) <= 1700, `${c.label} ${words(o.text)}`);
  }
});

test('personalization: two different charts share almost no identical sentences, and thin evidence gives a short chapter', () => {
  const outs = charts.map((c: any) => interpret(c.facts, 'cong_danh', K));
  // content sentences (book readings, conditions, facts) must be chart-specific; method sentences (he_thong) may recur but not dominate
  const sets = outs.map((o: any) => new Set(o.paragraphs.flatMap((p: any) => p.sentences.filter((s: any) => s.basis !== 'he_thong').map((s: any) => s.text))));
  const all = outs.map((o: any) => new Set(o.paragraphs.flatMap((p: any) => p.sentences.map((s: any) => s.text))));
  for (let i = 1; i < sets.length; i++) {
    const shared = [...sets[0]].filter(x => sets[i].has(x));
    assert.ok(shared.length / sets[0].size < 0.15, `chart ${i} shares ${shared.length} content sentences: ${shared.join(' | ')}`);
    const sharedAll = [...all[0]].filter(x => all[i].has(x));
    assert.ok(sharedAll.length / all[0].size < 0.25, `chart ${i} shares ${sharedAll.length} sentences overall`);
  }
  for (const o of outs) assert.ok(words(o.text) / Math.max(1, o.quality.metrics.independentGrounds) <= 200);
});

/** node:sqlite adapter with the D1 surface the store uses. */
function d1(db: DatabaseSync): D1Like {
  const stmt = (sql: string, args: unknown[] = []) => ({
    all: async () => ({ results: db.prepare(sql).all(...(args as any[])) as any[] }),
    first: async () => (db.prepare(sql).get(...(args as any[])) as any) ?? null,
    run: async () => db.prepare(sql).run(...(args as any[])),
  });
  return { prepare: (sql: string) => ({ ...stmt(sql), bind: (...v: unknown[]) => stmt(sql, v) }) } as unknown as D1Like;
}

test('D1 schema + seed load into SQLite and the D1 store produces the same chapter as the bundled knowledge; output cache round-trips', async () => {
  const db = new DatabaseSync(':memory:');
  db.exec(readFileSync(new URL('../../../migrations/interpret/0001_schema.sql', import.meta.url), 'utf8'));
  db.exec(readFileSync(new URL('../../../migrations/interpret/0002_seed.sql', import.meta.url), 'utf8'));
  const store = new D1Store(d1(db), K);
  const k2 = await store.load();
  assert.equal(k2.version, K.version);
  assert.equal(k2.rules.length, K.rules.length);
  assert.equal(interpret(REF.facts, 'cong_danh', k2).text, interpret(REF.facts, 'cong_danh', K).text);
  const cache = new LayeredCache({ db: d1(db) });
  const key = await cacheKey([REF.facts.base, 'cong_danh', 'x']);
  assert.equal(await cache.get(key), null);
  await cache.put(key, 'cong_danh', '{"ok":1}', { engine: 'e', kb: 'k', pass: true });
  assert.equal(await cache.get(key), '{"ok":1}');
});
