// Regression and quality invariants of the deterministic interpretation pipeline. 17/05/1990 is the first regression case; every
// assertion below encodes either a fact of that chart or a defect found in the audit (docs/INTERPRETATION-AUDIT.md) that must not return.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { DatabaseSync } from 'node:sqlite';
import { interpret, CHAPTERS } from '../pipeline.ts';
import { run } from '../engine.ts';
import { D1Store, LayeredCache, cacheKey, type D1Like } from '../store.ts';
import type { Knowledge } from '../types.ts';

const K: Knowledge = JSON.parse(readFileSync(new URL('../generated/knowledge.json', import.meta.url), 'utf8'));
const charts = JSON.parse(readFileSync(new URL('./fixtures/charts.json', import.meta.url), 'utf8'));
const REF = charts[0];                                   // 17/05/1990 10:30 nam — the regression case
const words = (t: string) => t.split(/\s+/).filter(w => /[\p{L}\p{N}]/u.test(w)).length;

test('17/05/1990 Công danh: passes the quality checks within the word budget; drafts are reported as drafts', () => {
  const o = interpret(REF.facts, 'cong_danh', K);
  assert.equal(o.quality.pass, true, JSON.stringify(o.quality.errors));
  assert.deepEqual(o.quality.warnings, []);
  const wc = words(o.text);
  assert.ok(wc >= 800 && wc <= 1500, `words ${wc}`);
  assert.ok(o.quality.metrics.repeated4gramRate < 0.06);
  assert.ok(o.quality.metrics.personalization >= 0.6);
  assert.equal(o.quality.editorial.allApproved, false);   // modules are drafts until an expert approves them; the output says so
});

test('17/05/1990 Công danh: configuration, Tứ Hóa, Tuần/Triệt and conditions are stated as the chart has them', () => {
  const t = interpret(REF.facts, 'cong_danh', K).text;
  assert.match(t, /Quan Lộc, trên lá số này an tại Canh Thìn với Tử Vi \(vượng\) và Thiên Tướng \(vượng\), cùng Địa Kiếp/);
  assert.match(t, /Mệnh \(Vũ Khúc hóa Quyền và Thiên Phủ \(vượng\)\)/);           // Tứ Hóa of the frame is named
  assert.match(t, /Phu Thê có Tuần và Thiên Di có Triệt/);                          // Tuần/Triệt with no rule: recorded, not interpreted
  assert.match(t, /“khó đạt công danh” khi có Địa Kiếp hãm địa ở Thìn/);            // a brightness branch list is read as brightness
  assert.doesNotMatch(t, /an tại Thìn \(/);
  assert.match(t, /“gian truân” khi có Thiên Tướng và Địa Kiếp trong cung/);        // condition complete (was 'khi Thiên Tướng và Địa Kiếp')
  assert.match(t, /Linh Tinh \(từ Phu Thê, nơi có Tuần\)/);                         // a sát star counted from a palace under Tuần says so
  assert.match(t, /“quyền quý” và “trong ngoài đều có quyền quý”[^.]*một căn cứ/);  // two sentences of one ground count once
  assert.match(t, /Địa Kiếp trong khung đọc của Quan Lộc/);
  assert.match(t, /Thực Hành tr\.29–30, 44/);                                       // citations of one book are merged
});

test('17/05/1990 Công danh: dominance, cross-palace links and timing follow the computed relations, never more', () => {
  const o = interpret(REF.facts, 'cong_danh', K), t = o.text;
  // dominance: the Toàn Thư limiting sentence only ADDS sát stars to Tử Vi -> a degree adjustment, stated as the system's convention
  assert.equal(o.argument.dominance[0].relation, 'sat_qualifier');
  assert.match(t, /chỉ thêm sát tinh — Địa Kiếp và Linh Tinh/);
  assert.match(t, /quy ước công khai/);
  assert.match(t, /Địa Kiếp trong cung, yếu tố chung của các câu hạn chế, hạ mức độ của tiềm năng ấy chứ không xóa nó/);
  // cross-palace: necessity is tested counterfactually. Lộc Mã in Tài Bạch is NECESSARY for 'lập nghiệp nơi xa'; Tử Vi in Quan Lộc is
  // NOT necessary for 'tạo được uy quyền hiển hách' (Thiên Phủ in Mệnh already satisfies 'Tử hoặc Phủ') — the old text claimed it was
  assert.match(t, /“lập nghiệp nơi xa, giàu sang lớn”.{0,40}câu này chỉ thỏa vì Lộc Tồn và Thiên Mã ở cung Tài Bạch/);
  assert.match(t, /“tạo được uy quyền hiển hách”.{0,140}Tử Vi ở cung Quan Lộc cũng thỏa điều kiện ấy, nhưng câu này không phụ thuộc vào đó/);
  assert.doesNotMatch(t, /hiển hách”[^.]*chỉ đứng được vì Tử Vi/);
  const cx = o.argument.cross.find(x => x.rule === 'TV_KL_PHU_VU_LOC_MA');
  assert.deepEqual(cx?.needs.map(d => d.star).sort(), ['Lộc Tồn', 'Thiên Mã']);
  // timing: the early reading stands on the year branch alone (every Ngọ-year chart), the late one on Địa Không in Thiên Di
  assert.equal(o.argument.timing.lean, 'late');
  assert.equal(o.argument.timing.leanReason, 'specific');
  assert.match(t, /thế chung của mọi lá số tuổi Ngọ/);
  assert.match(t, /theo quy ước ưu tiên điều kiện cụ thể, bản luận nghiêng về nhịp muộn, nhưng vẫn ghi cả hai/);
  assert.match(t, /46–55 tuổi mụ/);
  assert.match(t, /không kết luận chặng ấy đi lên hay đi xuống/);
  assert.match(t, /Năm 2026 \(Bính Ngọ\), tiểu hạn rơi đúng cung Quan Lộc/);
  assert.match(t, /lưu Hóa Kỵ \(Liêm Trinh\) rơi vào cung Tài Bạch/);
  // limits
  assert.match(t, /không được áp sang Quan Lộc/);
  assert.match(t, /chưa đối chiếu đủ|chưa được đối chiếu đủ/);
});

test('17/05/1990 Công danh: defects found in the audit stay out', () => {
  const t = interpret(REF.facts, 'cong_danh', K).text;
  assert.doesNotMatch(t, /Nhật Nguyệt giáp/);                         // giáp rule fired with both stars on one side
  assert.doesNotMatch(t, /tự tin \('ta đây'\)/);                       // a Mệnh personality reading routed into career limits
  assert.doesNotMatch(t, /sách nghiêng về thành tựu đến muộn/);         // the old unsupported tilt (one early, one late reading)
  assert.doesNotMatch(t, /96–105|115–124/);                            // decades no reader can use
  assert.doesNotMatch(t, /Khi con đường không thẳng/);                 // generic reflection filler
  assert.doesNotMatch(t, /theo sách đây|theo sách là/);                // the system's voice inside a quoted reading
  assert.doesNotMatch(t, /hoa rơi giữa rừng gươm/);                    // a harsh unverified draft is counted, never quoted
  assert.doesNotMatch(t, /Thực Hành, Thực Hành/);
});

test('17/05/1990 Mệnh and Tài Bạch reuse the same pipeline: each passes, and stays within its own topic', () => {
  const m = interpret(REF.facts, 'menh', K), tb = interpret(REF.facts, 'tai_bach', K);
  for (const o of [m, tb]) { assert.equal(o.quality.pass, true, JSON.stringify(o.quality.errors)); assert.deepEqual(o.quality.warnings, []); }
  assert.equal(m.title, 'Mệnh'); assert.equal(tb.title, 'Tài bạch');
  // Mệnh: a harsh reading that only adds a sát star (from Thiên Di, under Triệt) is a degree adjustment, not the reading that wins
  assert.equal(m.argument.dominance[0].relation, 'sat_qualifier');
  assert.match(m.text, /Địa Không \(từ Thiên Di, nơi có Triệt\)/);
  assert.doesNotMatch(m.text, /độ số/);                                // technical classification readings stay out of prose
  assert.match(m.text, /không đứng trên sao mà trên năm sinh hoặc giới tính|chỉ dựa vào năm sinh hoặc giới tính/);
  // Tài Bạch: Lộc Tồn readings of one ground are counted once; Lộc Mã in Tài Bạch is what Mệnh's 'lập nghiệp nơi xa' needs
  assert.match(tb.text, /bốn câu Khảo Luận và Toàn Thư ghi cho cùng một dữ kiện \(Lộc Tồn tại Tài Bạch\)/);
  assert.match(tb.text, /Điền Trạch/);
  assert.doesNotMatch(tb.text, /họ hàng đông đúc/);                   // a Phúc Đức clan reading that merely mentions 'thịnh vượng'
});

test('every book sentence of every regression chart and chapter rests on fired, verified rules; no banned wording; deterministic', () => {
  for (const c of charts) for (const ch of CHAPTERS) {
    const o = interpret(c.facts, ch, K);
    const verified = new Set(run(K.rules, K.sources, c.facts.base).findings.filter(f => f.basis === 'verified').map(f => f.ruleId));
    for (const s of o.paragraphs.flatMap(p => p.sentences)) {
      if (s.basis === 'sach') assert.ok(s.rules.length || s.cites.length || /tr\.\d/.test(s.text), s.text);
      if (s.basis === 'sach') for (const r of s.rules) if (!r.startsWith('VH_')) assert.ok(verified.has(r), `${r} in ${s.text}`);
      assert.doesNotMatch(s.text, /chắc chắn|định mệnh|tai họa|sẽ bị|tuyệt đối/i);
    }
    assert.equal(o.quality.errors.length, 0, `${c.label} ${ch}: ${JSON.stringify(o.quality.errors)}`);
    assert.equal(interpret(c.facts, ch, K).text, o.text);
    assert.ok(words(o.text) <= 1500, `${c.label} ${ch} ${words(o.text)}`);
  }
});

test('sentence-level provenance: a synthesis sentence carries only the rules of the claims it names', () => {
  const o = interpret(REF.facts, 'cong_danh', K);
  const syn = o.paragraphs.find(p => p.role === 'synthesis')!.sentences;
  const timing = syn.find(s => /Về thời điểm|Còn về thời điểm/.test(s.text))!;
  assert.deepEqual([...timing.rules].sort(), ['TV_KL_DHK_06_NGO', 'TV_TH_VERSE_DI_KHONG_KIEP']);
  assert.deepEqual(syn.find(s => /tiên đoán|đoán định/.test(s.text))!.rules, []);
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

test('D1 schema + seed load into SQLite; the D1 store gives the same text as the bundle for every chapter; the cache round-trips', async () => {
  const db = new DatabaseSync(':memory:');
  db.exec(readFileSync(new URL('../../../migrations/interpret/0001_schema.sql', import.meta.url), 'utf8'));
  db.exec(readFileSync(new URL('../../../migrations/interpret/0002_seed.sql', import.meta.url), 'utf8'));
  db.exec(readFileSync(new URL('../../../migrations/interpret/0002_seed.sql', import.meta.url), 'utf8'));   // re-applying the seed is idempotent
  assert.equal((db.prepare('SELECT COUNT(*) AS n FROM module_reviews').get() as any).n, K.modules.reduce((n, m: any) => n + (m.reviews?.length ?? 0), 0));
  const k2 = await new D1Store(d1(db), K).load();
  assert.equal(k2.version, K.version);
  assert.equal(k2.rules.length, K.rules.length);
  assert.equal(k2.modules.length, K.modules.length);
  for (const c of charts.slice(0, 3)) for (const ch of CHAPTERS) assert.equal(interpret(c.facts, ch, k2).text, interpret(c.facts, ch, K).text, `${c.label} ${ch}`);
  const cache = new LayeredCache({ db: d1(db) });
  const key = await cacheKey([REF.facts.base, 'cong_danh', 'x']);
  assert.equal(await cache.get(key), null);
  await cache.put(key, 'cong_danh', '{"ok":1}', { engine: 'e', kb: 'k', pass: true });
  assert.equal(await cache.get(key), '{"ok":1}');
  // R2 layer first: an R2 hit is served without touching D1; a put writes the body to R2 and only the pointer to D1
  const objs = new Map<string, string>();
  const r2 = { get: async (k: string) => objs.has(k) ? { text: async () => objs.get(k)! } : null, put: async (k: string, v: string) => { objs.set(k, v); } };
  const c2 = new LayeredCache({ db: d1(db), r2 });
  await c2.put('k2', 'menh', '{"r2":1}', { engine: 'e', kb: 'k', pass: true });
  assert.equal(objs.get('interpretations/k2.json'), '{"r2":1}');
  assert.equal((db.prepare("SELECT output_json, r2_key FROM interpretations WHERE cache_key = 'k2'").get() as any).r2_key, 'interpretations/k2.json');
  assert.equal(await c2.get('k2'), '{"r2":1}');
});

test('cache key changes with the chapter, the engine version and the knowledge version', async () => {
  const base = [REF.facts.base, REF.facts.decades, REF.facts.year];
  const a = await cacheKey([...base, 'cong_danh', 'e1', 'k1']);
  assert.notEqual(a, await cacheKey([...base, 'menh', 'e1', 'k1']));
  assert.notEqual(a, await cacheKey([...base, 'cong_danh', 'e2', 'k1']));
  assert.notEqual(a, await cacheKey([...base, 'cong_danh', 'e1', 'k2']));
  assert.equal(a, await cacheKey([...base, 'cong_danh', 'e1', 'k1']));
});

test('loadKnowledge: one version row per request, the full D1 read once per isolate; an unseeded binding falls back to the bundle', async () => {
  const { loadKnowledge } = await import('../store.ts');
  const db = new DatabaseSync(':memory:');
  db.exec(readFileSync(new URL('../../../migrations/interpret/0001_schema.sql', import.meta.url), 'utf8'));
  assert.equal(await loadKnowledge(d1(db), K), K);                      // schema only, no seed
  db.exec(readFileSync(new URL('../../../migrations/interpret/0002_seed.sql', import.meta.url), 'utf8'));
  let reads = 0;
  const counting: D1Like = { prepare: (sql: string) => { reads++; return d1(db).prepare(sql); } } as D1Like;
  const a = await loadKnowledge(counting, K), n1 = reads;
  const b = await loadKnowledge(counting, K);
  assert.equal(a, b);
  assert.equal(reads - n1, 1);                                          // second request: only the version row
  assert.equal(await loadKnowledge(undefined, K), K);
});
