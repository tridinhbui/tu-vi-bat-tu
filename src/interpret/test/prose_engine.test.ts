// Mệnh reader prose (prose plan P3): golden text for the worked example, its argument, metamorphic checks, and the 1,000-chart thresholds.
// Regenerate the golden after an intended library change:  UPDATE_GOLDEN=1 node --test src/interpret/test/prose_engine.test.ts
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { proseMenh } from '../prose/menh.ts';
import { evaluate } from '../../../tools/interpret/eval_prose.ts';
import type { ChartInput, Knowledge } from '../types.ts';

const K: Knowledge = JSON.parse(readFileSync(new URL('../generated/knowledge.json', import.meta.url), 'utf8'));
const ex = JSON.parse(readFileSync(new URL('./fixtures/menh_cu_tuat.json', import.meta.url), 'utf8'));
const goldenUrl = new URL('./fixtures/menh_cu_tuat.prose.txt', import.meta.url);
const corpusUrl = new URL('./fixtures/corpus1000.json.gz', import.meta.url);
const clone = <T>(x: T): T => JSON.parse(JSON.stringify(x));

test('worked example (02/03/1991 08:30 nam): golden text, byte for byte', () => {
  const o = proseMenh(ex.facts, K, { allowDraft: true });
  if (process.env.UPDATE_GOLDEN === '1' || !existsSync(goldenUrl)) writeFileSync(goldenUrl, o.text + '\n');
  assert.equal(o.text + '\n', readFileSync(goldenUrl, 'utf8'));
  assert.equal(proseMenh(clone(ex.facts), K, { allowDraft: true }).text, o.text, 'deterministic');
});

test('worked example: the argument behind the text', () => {
  const o = proseMenh(ex.facts, K, { allowDraft: true });
  assert.ok(o.pass, JSON.stringify(o.issues));
  const all = o.paragraphs.flatMap(p => p.sentences), by = (m: string) => all.find(s => s.trace.move === m || s.trace.woven?.includes(m as any));
  // the limit is Cự Môn hãm (TH p.43, TH p.88 verse), named with its cause
  assert.ok(by('TURN')!.trace.rules.includes('TV_TH_CU_HAM_GIAN_XAO_DA_NGHI'));
  assert.match(by('TURN')!.text, /Cự Môn .*hãm/);
  // the core is the sharp mind Cự Môn thủ Mệnh gives (KL p.223)
  assert.ok(by('ANCHOR')!.trace.concepts.includes('cog.sharp') && by('ANCHOR')!.trace.rules.includes('TV_KL_CT_CU_THU_MENH'));
  // the book's own rescue (TH p.88) is what turns it; 'suốt đời cùng khổ, cô đơn' (TH p.95) is never voiced as such
  assert.deepEqual(by('RESCUE')!.trace.resolution, { relation: 'REL_TH88_CU_TUAT_TAN_LOC', byRule: 'TV_TH_MV_MENH_CU_THIN_TUAT_LOC', cite: 'TH p.88' });
  assert.doesNotMatch(o.text, /cùng khổ|cô đơn|suốt đời/);
  // Kình Dương đắc địa reads as resolve, with its pride, not as a plain sát (TH p.62)
  assert.match(o.text, /Kình Dương[^.]*quả quyết/);
  assert.ok(by('TENSION')!.trace.rules.includes('TV_TH_AUX2_MENH_KINH_DAC'));
  // Tuần at Mệnh: a slow start (TH p.83, KL p.68)
  assert.match(by('TIMING')!.text, /Tuần/);
  // closing: editorial, and only about what the paragraph said
  const close = o.paragraphs[0].sentences.at(-1)!;
  assert.equal(close.trace.basis, 'he_thong');
  for (const s of all) if (s.trace.basis === 'sach') assert.ok(s.trace.rules.length && s.trace.cites.length, s.text);
});

test('draft cards stay off unless asked for: without allowDraft the chapter is empty, never padded', () => {
  const o = proseMenh(ex.facts, K);
  assert.equal(o.paragraphs.length, 0);
  assert.equal(o.text, '');
});

test('metamorphic: without Hóa Lộc at Mệnh there is no rescue; without Tuần there is no Tuần sentence', () => {
  const noLoc: ChartInput = clone(ex.facts);
  const m = noLoc.base['palace:Mệnh'];
  for (const k of ['palace.tu_hoa', 'palace.rel.self_hoa', 'palace.tam_phuong_tu_hoa', 'palace.rel.tp_hoa']) m[k] = (m[k] as string[] ?? []).filter(h => h !== 'Hóa Lộc');
  const a = proseMenh(noLoc, K, { allowDraft: true });
  assert.ok(!a.paragraphs.flatMap(p => p.sentences).some(s => s.trace.move === 'RESCUE'));
  const noTuan: ChartInput = clone(ex.facts);
  noTuan.base['palace:Mệnh']['palace.tuan'] = false;
  noTuan.palaces.find(p => p.name === 'Mệnh')!.tuan = false;
  const b = proseMenh(noTuan, K, { allowDraft: true });
  assert.doesNotMatch(b.text, /Tuần/);
});

test('metamorphic over the corpus: removing Tuần/Triệt from Mệnh removes every Tuần/Triệt sentence', { skip: !existsSync(corpusUrl) && 'corpus not built' }, () => {
  const corpus = JSON.parse(gunzipSync(readFileSync(corpusUrl)).toString('utf8'));
  let pairs = 0;
  const bad: string[] = [];
  for (const c of corpus) {
    const pal = c.facts.palaces.find((p: any) => p.name === 'Mệnh');
    if (!pal.tuan && !pal.triet) continue;
    const before = proseMenh(c.facts, K, { allowDraft: true });
    if (!/\b(Tuần|Triệt)\b/.test(before.text)) continue;
    const f: ChartInput = clone(c.facts);
    for (const k of ['palace.tuan', 'palace.triet']) f.base['palace:Mệnh'][k] = false;
    Object.assign(f.palaces.find(p => p.name === 'Mệnh')!, { tuan: false, triet: false });
    const after = proseMenh(f, K, { allowDraft: true });
    pairs++;
    if (/\b(Tuần|Triệt)\b/.test(after.text)) bad.push(JSON.stringify(c.birth));
  }
  assert.ok(pairs >= 100, `${pairs} pairs`);
  assert.deepEqual(bad, []);
});

test('1,000 charts: no blocking error, no empty chapter, repetition, diversity and schema spread within the plan thresholds',
  { skip: !existsSync(corpusUrl) && 'corpus not built' }, () => {
  const corpus = JSON.parse(gunzipSync(readFileSync(corpusUrl)).toString('utf8'));
  const e = evaluate(corpus);
  assert.deepEqual(e.errors, {});
  assert.equal(e.pass, 1000);
  assert.equal(e.empty, 0);
  assert.ok(e.rep4Max < 0.05, `repeated 4-grams ${e.rep4Max}`);
  assert.ok(e.jaccardMedian <= 0.35, `jaccard ${e.jaccardMedian}`);
  assert.ok(e.topOpener[1] <= 0.08, `opener ${e.topOpener}`);
  assert.ok(e.schemaEntropy >= 0.7 * e.schemaMax, `entropy ${e.schemaEntropy}`);
  assert.deepEqual(e.variantOveruse, []);
  // sentence rhythm: the plan's target is 95 % of chapters (the reference paragraph itself: mean 30.9, sd 7.1). Reached since the
  // repair pass weaves toward the band and caps woven length when a chapter runs long (97 % on the first 300 charts).
  assert.ok(e.sentLenOk >= 950, `sentence rhythm ${e.sentLenOk}/1000`);
});

// ---- the shared /api/interpret handler (src/interpret/route.ts): what the Worker and tools/interpret/dev_server.ts both run ----
import { handleInterpret } from '../route.ts';
import { BundledStore, LayeredCache } from '../store.ts';
const deps = (over: Partial<Parameters<typeof handleInterpret>[1]> = {}) => ({
  enabled: true, proseDraft: true, deep: false, store: new BundledStore(K), cache: new LayeredCache({}), defer: () => {},
  facts: async () => new Response(JSON.stringify(ex.facts), { headers: { 'content-type': 'application/json' } }), ...over });
const call = (body: unknown, over = {}) => handleInterpret(new Request('http://x/api/interpret', { method: 'POST', body: JSON.stringify(body) }), deps(over));

test('route: mode "prose" returns the golden text; other chapters refuse prose; the flags gate the route and the drafts', async () => {
  const birth = { year: 1991, month: 3, day: 2, hour: 8, minute: 30, gender: 'male' };
  // with the luận cung form off (TVBT_LUAN=0) the older chapter, byte for byte
  const r = await call({ ...birth, chapter: 'menh', mode: 'prose' }, { luan: false });
  assert.equal(r.status, 200);
  const o = await r.json() as any;
  assert.equal(o.text + '\n', readFileSync(goldenUrl, 'utf8'));
  assert.ok(o.draft && o.evidence.rules.TV_TH_MV_MENH_CU_THIN_TUAT_LOC.cites.includes('TH p.88'));
  // by default the luận cung chapter (prose/luan.ts; its own golden in luan.test.ts)
  const l = await (await call({ ...birth, chapter: 'menh', mode: 'prose' })).json() as any;
  assert.ok(l.luan && l.title === 'Luận cung Mệnh' && l.paragraphs.some((p: any) => p.lead), 'luận cung Mệnh with lead-ins');
  // only checked readings reach the reader: no phổ thông sentence in any chapter of the whole report, Bát Tự sections included
  const full = await (await call({ ...birth, chapter: 'all', mode: 'prose' })).json() as any;
  const sents = full.chapters.flatMap((c: any) => [...c.paragraphs, ...Object.values(c.chapters ?? {}).flat()].flatMap((p: any) => p.sentences));
  assert.ok(sents.length > 50 && sents.every((s: any) => s.trace.basis !== 'pho_thong'), 'no phổ thông sentence');
  assert.ok(full.chapters.find((c: any) => c.chapter === 'tong_quan').card.every((f: any) => f.basis !== 'pho_thong'));
  assert.equal((await call({ ...birth, chapter: 'tong_quan', mode: 'prose' })).status, 422);
  assert.equal((await call({ ...birth, chapter: 'van_han', mode: 'prose' })).status, 200);
  assert.equal((await call({ ...birth, chapter: 'bat_tu', mode: 'prose' })).status, 200);
  const all = await (await call({ ...birth, chapter: 'all', mode: 'prose' }, { luan: false })).json() as any;
  assert.deepEqual(all.chapters.map((c: any) => c.chapter), ['tong_quan', 'menh', 'cong_danh', 'tai_bach', 'thien_di', 'phu_the', 'phuc_duc', 'dien_trach', 'no_boc', 'tu_tuc', 'huynh_de', 'phu_mau', 'tat_ach', 'van_han', 'bat_tu']);
  assert.equal(all.chapters[1].text + '\n', readFileSync(goldenUrl, 'utf8'));
  assert.equal((await call({ ...birth, chapter: 'cong_danh', mode: 'prose' })).status, 200);
  assert.equal((await call({ ...birth, chapter: 'menh', mode: 'prose' }, { enabled: false })).status, 404);
  const strict = await (await call({ ...birth, chapter: 'menh', mode: 'prose' }, { proseDraft: false })).json() as any;
  assert.equal(strict.paragraphs.length, 0);
  const ev = await (await call({ ...birth, chapter: 'menh' })).json() as any;
  assert.equal(ev.engine, 'interpret-2.1.0');
});

// ---- P5: Công danh (Quan Lộc) and Tài Bạch, chained after Mệnh ----
import { proseChapter, proseReport } from '../prose/chapter.ts';
for (const ch of ['cong_danh', 'tai_bach', 'thien_di', 'phu_the', 'phuc_duc', 'dien_trach', 'no_boc', 'tu_tuc', 'huynh_de', 'phu_mau', 'tat_ach'] as const) {
  const url = new URL(`./fixtures/menh_cu_tuat.${ch}.prose.txt`, import.meta.url);
  test(`worked example, ${ch}: golden text, byte for byte, no blocking issue`, () => {
    const o = proseChapter(ex.facts, K, ch, { allowDraft: true });
    if (process.env.UPDATE_GOLDEN === '1' || !existsSync(url)) writeFileSync(url, o.text + '\n');
    assert.equal(o.text + '\n', readFileSync(url, 'utf8'));
    assert.ok(o.pass, JSON.stringify(o.issues));
  });
}

test('worked example, Tài Bạch: a qualifier-weakened tài lộc is told in its weakened form, never elaborated or praised', () => {
  const o = proseChapter(ex.facts, K, 'tai_bach', { allowDraft: true });
  const anchor = o.paragraphs[0].sentences[0];
  assert.ok(anchor.trace.concepts.includes('fin.abundance'));
  assert.ok(o.evidence.resolved.some(r => r.concept === 'fin.abundance' && r.by.some(b => b.relation === 'Q_KL197_SONG_LOC')), 'KL p.197 song lộc qualifier applied');
  assert.ok(!o.paragraphs.flatMap(p => p.sentences).some(s => s.trace.move === 'VALUE' && s.trace.concepts.includes('fin.abundance')));
});

test('a report never voices one reading (concept at a palace) in two chapters (300 charts)', { skip: !existsSync(corpusUrl) && 'corpus not built' }, () => {
  const corpus = JSON.parse(gunzipSync(readFileSync(corpusUrl)).toString('utf8')).slice(0, 300);
  const bad: string[] = [];
  for (const c of corpus) {
    const seen = new Map<string, string>();
    for (const o of proseReport(c.facts, K, { allowDraft: true }))
      for (const p of o.paragraphs) for (const s of p.sentences) {
        if (s.trace.basis === 'he_thong') continue;                          // closing lines re-voice what their paragraph said
        for (const x of s.trace.keys ?? []) { const prev = seen.get(x); if (prev && prev !== o.chapter) bad.push(`${JSON.stringify(c.birth)} ${x}: ${prev} and ${o.chapter}`); seen.set(x, o.chapter); }
      }
  }
  assert.deepEqual(bad.slice(0, 5), []);
});

test('Phu Thê speaks of the partner as the partner: a non-bond trait never has the person as subject (300 charts)', { skip: !existsSync(corpusUrl) && 'corpus not built' }, () => {
  const corpus = JSON.parse(gunzipSync(readFileSync(corpusUrl)).toString('utf8')).slice(0, 300);
  const person = /^(đương số|người mang lá số này|người này|người mang tổ hợp này|chủ nhân lá số)\b/i;
  const bad: string[] = [];
  for (const c of corpus) {
    const o = proseChapter(c.facts, K, 'phu_the', { allowDraft: true });
    for (const s of o.paragraphs.flatMap(p => p.sentences))
      if (s.trace.move === 'SATELLITE' && s.trace.concepts.every(x => /^(cog|temper|values|presence|career|fin|exp)\./.test(x)) && person.test(s.text.replace(/^[^,]*,\s*/, ''))) bad.push(s.text);
  }
  assert.deepEqual(bad.slice(0, 3), []);
});

for (const [ch, maxEmpty] of [['cong_danh', 10], ['tai_bach', 75]] as const) {
  test(`1,000 charts, ${ch}: no blocking error; repetition, openers, diversity and schema spread within the thresholds`, { skip: !existsSync(corpusUrl) && 'corpus not built' }, () => {
    const e = evaluate(JSON.parse(gunzipSync(readFileSync(corpusUrl)).toString('utf8')), ch);
    assert.deepEqual(e.errors, {});
    assert.equal(e.pass, 1000);
    // empty = no rule at all speaks of this palace's kind on the chart: the chapter stays empty rather than padded (rule-base gap)
    assert.ok(e.empty <= maxEmpty, `${e.empty} empty`);
    assert.ok(e.rep4Max < 0.05 && e.jaccardMedian <= 0.35 && e.topOpener[1] <= 0.08, JSON.stringify([e.rep4Max, e.jaccardMedian, e.topOpener]));
    assert.ok(e.schemaEntropy >= 0.7 * e.schemaMax);
    assert.deepEqual(e.variantOveruse, []);
  });
}

// the five P5 chapters on the first 400 charts (time): empty share = charts where no rule speaks of the palace's topic (rule-base gap)
// Tử Tức and Huynh Đệ are still often empty: the books say little about them, and nothing is padded. Thiên Lương's Bào/Nô, Phụ Mẫu
// and Tật Ách rules (TL pp.124-131) filled most of the gap in Huynh Đệ, Phụ Mẫu, Tật Ách, Nô Bộc and Phu Thê; the limits hold that gain.
// Tật Ách is 0.12 since the Khảo Luận p.218 rule 'về già sung túc' again carries the book's own exclusions (no Tham Lang, Hóa Kỵ, Không Kiếp;
// engine audit 0b0bd5c): fewer charts qualify, and an empty chapter is the honest result, not a gap to pad.
for (const [ch, maxEmpty] of [['thien_di', 0.01], ['phu_the', 0.08], ['phuc_duc', 0.06], ['dien_trach', 0.19], ['no_boc', 0.17],
  ['tu_tuc', 0.27], ['huynh_de', 0.28], ['phu_mau', 0.08], ['tat_ach', 0.12]] as const) {
  test(`400 charts, ${ch}: no blocking error; repetition, openers, diversity within the thresholds`, { skip: !existsSync(corpusUrl) && 'corpus not built' }, () => {
    const e = evaluate(JSON.parse(gunzipSync(readFileSync(corpusUrl)).toString('utf8')).slice(0, 400), ch);
    assert.deepEqual(e.errors, {});
    assert.equal(e.pass, 400);
    assert.ok(e.empty <= maxEmpty * 400, `${e.empty} empty`);
    assert.ok(e.rep4Max < 0.05 && e.jaccardMedian <= 0.35 && e.topOpener[1] <= 0.08, JSON.stringify([e.rep4Max, e.jaccardMedian, e.topOpener]));
    assert.deepEqual(e.variantOveruse, []);
  });
}
