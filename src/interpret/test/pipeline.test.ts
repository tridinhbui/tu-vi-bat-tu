// Regression and quality invariants of the deterministic interpretation pipeline, every chapter, over the regression charts
// (fixtures/charts.json: 3 reviewed charts, random dates, two edge dates, and one chart for each rare configuration in make_fixtures.py).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { DatabaseSync } from 'node:sqlite';
import { interpret, CHAPTERS, type ChapterOutput } from '../pipeline.ts';
import { run } from '../engine.ts';
import { shortCond, citeVi } from '../generator.ts';
import { SPECS } from '../chapters.ts';
import { D1Store, LayeredCache, cacheKey, type D1Like } from '../store.ts';
import type { Knowledge } from '../types.ts';

const K: Knowledge = JSON.parse(readFileSync(new URL('../generated/knowledge.json', import.meta.url), 'utf8'));
const charts = JSON.parse(readFileSync(new URL('./fixtures/charts.json', import.meta.url), 'utf8'));
const REF = charts[0];                                   // 17/05/1990 10:30 nam — the regression case
const byLabel = (l: string) => { const c = charts.find((x: any) => x.label === l); assert.ok(c, `fixture ${l}`); return c; };
const words = (t: string) => t.split(/\s+/).filter(w => /[\p{L}\p{N}]/u.test(w)).length;
// one interpretation per (chart, chapter), shared by the tests below
const memo = new Map<string, ChapterOutput>();
const out = (i: number, ch: (typeof CHAPTERS)[number]) => { const key = `${i}|${ch}`; if (!memo.has(key)) memo.set(key, interpret(charts[i].facts, ch, K)); return memo.get(key)!; };

test('regression set: at least 30 charts, including every rare configuration', () => {
  assert.ok(charts.length >= 30, `${charts.length} charts`);
  for (const l of ['Mệnh vô chính diệu', 'Quan Lộc vô chính diệu', 'Tuần Triệt cùng ở Quan Lộc', 'Hóa Kỵ tại Mệnh', 'Thân cư Quan Lộc', 'Không Kiếp cùng tại Mệnh'])
    byLabel(l);
});

test('17/05/1990: the Công danh chapter passes every quality check and stays within the word budget', () => {
  const o = out(0, 'cong_danh');
  assert.equal(o.quality.pass, true, JSON.stringify(o.quality.errors));
  assert.deepEqual(o.quality.warnings, []);
  const wc = words(o.text);
  assert.ok(wc >= 800 && wc <= 1500, `words ${wc}`);
  assert.ok(o.quality.metrics.repeated4gramRate < 0.08);
  assert.ok(o.quality.metrics.personalization >= 0.6);
  assert.equal(o.quality.editorial.allApproved, false);   // modules are drafts until an expert approves them; the output says so
});

test('17/05/1990 Công danh: configuration, grounds, counters, cross-palace links and timing are the ones the chart supports', () => {
  const t = out(0, 'cong_danh').text;
  // central configuration (facts) and the frame: Quan Lộc in its tam phương, the environment read from Thiên Di (opposite Mệnh)
  assert.match(t, /Quan Lộc an tại Canh Thìn với Tử Vi \(vượng\) và Thiên Tướng \(vượng\), có thêm sát tinh Địa Kiếp/);
  assert.match(t, /hai cung tam hợp là Mệnh .* và Tài Bạch .*, còn cung xung chiếu là Phu Thê/);
  assert.match(t, /Bối cảnh bên ngoài được đọc ở Thiên Di/);
  // the Tử–Phủ–Vũ–Tướng group of KL pp.166-167 links Mệnh and Quan Lộc
  assert.match(t, /Tử – Phủ – Vũ – Tướng.*Khảo Luận tr\.166–167/);
  // two Toàn Thư sentences on the same pairing are ONE ground
  assert.match(t, /“quyền quý” và “trong ngoài đều có quyền quý”[\s\S]{0,200}một căn cứ/);
  // brightness modifies the lead (Thực Hành locator + Khảo Luận p.233 principle), said once
  assert.match(t, /Tử Vi ở Thìn được xếp vượng \(Thực Hành tr\.29\)/);
  assert.equal((t.match(/chính tinh đắc địa thì tốt/g) ?? []).length, 1);
  // the limiting readings sit next to the lead: the same-book one first, with its sát-star condition, then the other books
  assert.match(t, /Toàn Thư[^“]{0,60}“công danh tầm thường”[^.]{0,30}Tử Vi tại Quan Lộc, sát tinh Địa Kiếp và Linh Tinh \(từ Phu Thê\) hội về Quan Lộc/);
  assert.match(t, /Thực Hành cũng ghi “khó đạt công danh”/);
  // the limiting readings add sát stars (a degree adjustment) — with TH p.110 firing too since rules read their own book's table (audit
  // 2026-10-23), the text frames it as potential vs present conditions
  assert.match(t, /câu thuận vẫn đứng như mô tả tiềm năng[^.]*phần điều chỉnh mức độ|phía thuận nói tiềm năng của tổ hợp sao, còn phía hạn chế nói điều kiện đang có mặt/);   // the limiting reading only adds sát stars: a degree adjustment
  // cross-palace necessity is tested counterfactually: 'Hóa Quyền gặp Tử hoặc Phủ' holds through Thiên Phủ in Mệnh itself, so the text must NOT
  // claim it stands on Tử Vi in Quan Lộc (audit finding); Lộc Mã from Tài Bạch IS necessary for 'lập nghiệp nơi xa'
  assert.doesNotMatch(t, /“tạo được uy quyền hiển hách”.{0,200}(đứng được|chỉ đứng|nhờ Tử Vi|Tử Vi nằm ở cung Quan Lộc)/s);
  assert.match(t, /“lập nghiệp nơi xa, giàu sang lớn”/);
  assert.match(t, /Lộc Tồn và Thiên Mã nằm ở cung Tài Bạch/);
  // audit regressions: the system's voice never sits inside a quote; a Mệnh personality reading is not a counter-reading of the environment;
  // a brightness branch list reads as brightness; no generic reflection filler
  assert.doesNotMatch(t, /theo sách (đây|là)/);
  assert.doesNotMatch(t, /Thiên Di[^]{0,400}“tự tin \('ta đây'\)/);
  assert.match(t, /Quan Lộc ở Thìn \(thế hãm\)/);
  assert.doesNotMatch(t, /Khi con đường không thẳng/);
  // timing: decade through Quan Lộc, vận readings that disagree are not resolved, early vs late readings kept apart
  assert.match(t, /46–55 tuổi mụ/);
  assert.match(t, /không kết luận chặng ấy đi lên hay đi xuống/);
  assert.match(t, /“công danh sớm, yêu sớm, về sau nhiều ngậm ngùi”.*“danh vọng đến muộn, khi tuổi đã cao”.*cả hai được giữ/);
  // what is deliberately not used
  assert.match(t, /không được áp sang Quan Lộc/);
  assert.match(t, /chưa được đối chiếu đủ/);
  // rule-integrity regressions found on this chart are not in the text
  assert.doesNotMatch(t, /Nhật Nguyệt giáp/);
  assert.doesNotMatch(t, /ở cung Mệnh” \(Thực Hành tr\.72\)/);
});

test('every chapter of every regression chart: no errors, book sentences rest on fired verified rules, no banned wording, budget, deterministic', () => {
  for (const [i, c] of charts.entries()) {
    const verifiedOf = (base: any, system: string) => new Set(run(K.rules, K.sources, base, system).findings.filter(f => f.basis === 'verified').map(f => f.ruleId));
    const tv = verifiedOf(c.facts.base, 'tu_vi'), bz = verifiedOf(c.facts.bazi.base, 'bat_tu');
    for (const ch of CHAPTERS) {
      const verified = ch === 'bat_tu' ? bz : tv;
      const o = out(i, ch), where = `${c.label} / ${ch}`;
      assert.equal(o.quality.errors.length, 0, `${where}: ${JSON.stringify(o.quality.errors)}`);
      for (const s of o.paragraphs.flatMap(p => p.sentences)) {
        if (s.basis === 'sach') assert.ok(s.rules.length || s.cites.length, `${where}: ${s.text}`);
        // a book sentence names only verified rules that fired, or the engine's time readings (VH:<palace>, VH_*, lưu Tứ Hóa)
        if (s.basis === 'sach') for (const r of s.rules) if (!/^(VH[:_]|LUU_TU_HOA$)/.test(r)) assert.ok(verified.has(r), `${where}: ${r} in ${s.text}`);
        assert.doesNotMatch(s.text.replace(/“[^”]*”/g, ''), /chắc chắn|định mệnh|tai họa|sẽ bị|tuyệt đối/i, where);
      }
      assert.ok(words(o.text) <= 1550, `${where}: ${words(o.text)} words`);
      assert.equal(interpret(c.facts, ch, K).text, o.text, `${where}: not deterministic`);
    }
  }
});

test('opposed readings are always narrated together, and sensitive chapters always carry their notice', () => {
  for (const [i] of charts.entries()) for (const ch of CHAPTERS) {
    const o = out(i, ch);
    assert.deepEqual(o.quality.warnings.filter(w => w.check === 'contradiction_not_explained'), [], `${charts[i].label} / ${ch}`);
    if (SPECS[ch].sensitive) assert.ok(o.paragraphs.some(p => p.sentences.some(s => s.kind === 'notice')), `${charts[i].label} / ${ch}: notice`);
  }
});

test('length follows evidence: chapters without fired readings stay short; longer chapters have the evidence for their length', () => {
  for (const [i] of charts.entries()) for (const ch of CHAPTERS) {
    if (ch === 'van_han') continue;
    // Bát Tự has no palace argument graph: a fixed frame (pillars, luck, limits) plus a handful of readings
    if (ch === 'bat_tu') { assert.ok(words(out(i, ch).text) <= 800, `${charts[i].label} / bat_tu`); continue; }
    const o = out(i, ch), g = o.quality.metrics.independentGrounds, wc = words(o.text);
    if (g === 0) assert.ok(wc <= 450, `${charts[i].label} / ${ch}: ${wc} words with no ground`);
    // the validator's inflation check (words per evidence unit) may only fire on short, frame-dominated chapters
    if (o.quality.warnings.some(w => w.check === 'possible_inflation')) assert.ok(wc <= 450, `${charts[i].label} / ${ch}: ${wc} words, inflated`);
  }
});

test('personalization: different charts share almost no book sentences word for word', () => {
  for (const ch of ['menh', 'cong_danh', 'tai_bach'] as const) {
    const sets = charts.map((_: unknown, i: number) => new Set(out(i, ch).paragraphs.flatMap(p => p.sentences.filter(s => ['claim', 'contrast'].includes(s.kind) && s.text.includes('“')).map(s => s.text))));
    const shares: number[] = [];
    for (let a = 0; a < sets.length; a++) for (let b = 0; b < sets.length; b++) if (a !== b && sets[a].size >= 5) shares.push([...sets[a]].filter(x => sets[b].has(x)).length / sets[a].size);
    shares.sort((x, y) => x - y);
    assert.ok(shares[Math.floor(shares.length / 2)] <= 0.05, `${ch}: median share ${shares[Math.floor(shares.length / 2)]}`);
    assert.ok(shares[shares.length - 1] <= 0.5, `${ch}: max share ${shares[shares.length - 1]}`);
  }
});

test('rare configurations are narrated from what is actually there', () => {
  const idx = (l: string) => charts.indexOf(byLabel(l));
  // a palace without major star: said, and the opposite palace's stars are read (the borrowing convention), not invented
  assert.match(out(idx('Mệnh vô chính diệu'), 'menh').text, /Mệnh an tại \S+ \S+ và không có chính tinh.*đọc thêm chính tinh của cung đối diện là Thiên Di/);
  assert.match(out(idx('Quan Lộc vô chính diệu'), 'cong_danh').text, /Quan Lộc an tại \S+ \S+ và không có chính tinh.*cung đối diện là Phu Thê/);
  // Tuần and Triệt together on Quan Lộc are both named
  assert.match(out(idx('Tuần Triệt cùng ở Quan Lộc'), 'cong_danh').text, /gặp Tuần và Triệt/);
  // Hóa Kỵ in Mệnh is named with the star it attaches to
  assert.match(out(idx('Hóa Kỵ tại Mệnh'), 'menh').text, /mang Hóa Kỵ \(Văn Xương\)/);
  // Thân in Quan Lộc: the Công danh chapter says the palace is also the Thân palace
  assert.match(out(idx('Thân cư Quan Lộc'), 'cong_danh').text, /Thân cư ngay tại Quan Lộc/);
  // a 96-year-old: no decade beyond the current one is narrated; a 3-year-old: the current decade is the first one
  const old = out(idx('sinh 1931, giờ Tý muộn'), 'van_han').text;
  assert.match(old, /96 tuổi mụ/);
  assert.doesNotMatch(old, /103–112|113–122/);
  assert.match(out(idx('sinh cuối 2024, giờ Tý sớm'), 'van_han').text, /Chặng đang đi qua: 2–11 tuổi, cung Mệnh|Từ 2–11 tuổi mụ, vận ở cung Mệnh/);
});

test('combined chapters: each section has its own frame, the chapter shares one notice and one synthesis', () => {
  for (const ch of ['gia_dao', 'di_no_tat'] as const) {
    const o = out(0, ch);
    for (const sec of SPECS[ch].sections) assert.ok(o.paragraphs.some(p => p.title === sec.palace), `${ch}: frame of ${sec.palace}`);
    assert.equal(o.paragraphs.filter(p => p.module === 'S.05.NOTICE').length, 1, `${ch}: one notice`);
    assert.equal(o.paragraphs.filter(p => p.role === 'synthesis').length, 1, `${ch}: one synthesis`);
  }
});

test('Bát Tự chapter: pillars are the engine\'s, readings only from verified bat_tu rules, never a Tử Vi rule, and no dụng thần claim', () => {
  for (const [i, c] of charts.entries()) {
    const o = out(i, 'bat_tu'), b = c.facts.bazi;
    assert.match(o.text, new RegExp(`ngày ${b.pillars.day.name}`));
    assert.match(o.text, new RegExp(`là ${b.day_master}, thuộc hành ${b.day_master_element}|thiên can ngày ${b.day_master} \\(hành ${b.day_master_element}\\)`));
    for (const s of o.paragraphs.flatMap(p => p.sentences)) {
      if (s.basis === 'sach') assert.ok(s.rules.length && s.rules.every(r => r.startsWith('BT_')), s.text);
      assert.doesNotMatch(s.text, /dụng thần (là|nên)|thân vượng|thân nhược/i, s.text);
    }
    assert.match(o.text, /chưa xét vượng suy của nhật chủ, dụng thần và cách cục/);
  }
});

test('time chapter: decades and the year are the engine\'s, readings only from vận rules', () => {
  const o = out(0, 'van_han'), c = REF.facts;
  const now = c.year.dai_han;
  assert.ok(o.paragraphs.some(p => p.title === `Chặng đang đi qua: ${now.age_from}–${now.age_to} tuổi, cung ${now.palace}`));
  assert.match(o.text, new RegExp(`${now.age_from}–${now.age_to} tuổi mụ, vận ở cung ${now.palace}`));
  assert.match(o.text, new RegExp(`tiểu hạn ở cung ${c.year.tieu_han_palace}`));
  for (const s of o.paragraphs.flatMap(p => p.sentences)) if (s.basis === 'sach') assert.ok(s.rules.every(r => /^(VH[:_]|LUU_TU_HOA$)/.test(r)), s.text);
});

test('condition shortening drops only repeated context clauses and never splits a star list', () => {
  const said = new Set<string>();
  assert.equal(shortCond('Văn Khúc và Vũ Khúc tại Mệnh, Mệnh ở Tỵ', said), 'Văn Khúc và Vũ Khúc tại Mệnh, Mệnh ở Tỵ');
  assert.equal(shortCond('Phá Quân tại Mệnh, Mệnh ở Tỵ', said), 'Phá Quân tại Mệnh');
  assert.equal(shortCond('Vũ Khúc (hãm) tại Mệnh, nữ mệnh', said), 'Vũ Khúc (hãm) tại Mệnh, nữ mệnh');       // gender is kept
  assert.equal(shortCond('Tham Lang tại Mệnh, Văn Khúc, Thiên Việt và Hóa Khoa hội chiếu về Mệnh', said), 'Tham Lang tại Mệnh, Văn Khúc, Thiên Việt và Hóa Khoa hội chiếu về Mệnh');
  assert.equal(shortCond('Lộc Tồn và Thiên Mã hội chiếu về Mệnh', said), 'Lộc Tồn và Thiên Mã hội chiếu về Mệnh');
  assert.equal(shortCond('Vũ Khúc tại Mệnh, Lộc Tồn và Thiên Mã hội chiếu về Mệnh', said), 'Vũ Khúc tại Mệnh, Lộc Mã hội chiếu về Mệnh');
  assert.equal(shortCond('Mệnh ở Tỵ', said), 'Mệnh ở Tỵ');                                                  // never emptied
  assert.equal(citeVi('KL p.51 Cơ #4'), 'Khảo Luận tr.51, mục “Cơ” ý 4');
  assert.equal(citeVi('TH pp.29-30'), 'Thực Hành tr.29–30');
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

test('D1 migrations + seed load into SQLite and the D1 store produces the same chapters as the bundled knowledge; output cache round-trips', async () => {
  const db = new DatabaseSync(':memory:');
  const dir = new URL('../../../migrations/interpret/', import.meta.url);
  for (const f of readdirSync(dir).filter(f => f.endsWith('.sql')).sort()) db.exec(readFileSync(new URL(f, dir), 'utf8'));
  const store = new D1Store(d1(db), K);
  const k2 = await store.load();
  assert.equal(k2.version, K.version);
  assert.equal(k2.rules.length, K.rules.length);
  assert.equal(k2.modules.length, K.modules.filter(m => m.status !== 'retired').length);   // retired modules are not loaded
  for (const ch of CHAPTERS) assert.equal(interpret(REF.facts, ch, k2).text, out(0, ch).text, `D1 vs bundle: ${ch}`);
  const cache = new LayeredCache({ db: d1(db) });
  const key = await cacheKey([REF.facts.base, 'cong_danh', 'x']);
  assert.equal(await cache.get(key), null);
  await cache.put(key, 'cong_danh', '{"ok":1}', { engine: 'e', kb: 'k', pass: true });
  assert.equal(await cache.get(key), '{"ok":1}');
});
