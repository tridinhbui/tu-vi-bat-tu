// The layers around the book readings (prose/deep.ts, prose/bazi_deep.ts, vanhan.ts; plan async-inventing-fairy): no empty chapter, the
// book wins over a common-meaning card, every difficulty is answered, Tuần/Triệt only where they are, labels never claim the book.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { proseReport, seedOf, PROSE_VERSION } from '../prose/chapter.ts';
import { proseVanHan } from '../prose/vanhan.ts';
import { proseBazi } from '../prose/bazi.ts';
import type { PhoThongLib } from '../prose/deep.ts';
import { META, ABSOLUTE } from '../prose/lint.ts';
import type { ChartInput, Knowledge } from '../types.ts';

const K: Knowledge = JSON.parse(readFileSync(new URL('../generated/knowledge.json', import.meta.url), 'utf8'));
const user: ChartInput = JSON.parse(readFileSync(new URL('./fixtures/user_1990_nam.json', import.meta.url), 'utf8'));
const corpusUrl = new URL('./fixtures/corpus1000.json.gz', import.meta.url);
const corpus = (n: number): ChartInput[] => existsSync(corpusUrl) ? JSON.parse(gunzipSync(readFileSync(corpusUrl)).toString('utf8')).slice(0, n).map((c: { facts: ChartInput }) => c.facts) : [];
const P = K.prose!.phoThong as PhoThongLib;

test('the cards cover every chính tinh in every palace, and no card text claims the book or certainty', () => {
  const majors = ['Tử Vi', 'Thiên Cơ', 'Thái Dương', 'Vũ Khúc', 'Thiên Đồng', 'Liêm Trinh', 'Thiên Phủ', 'Thái Âm', 'Tham Lang', 'Cự Môn', 'Thiên Tướng', 'Thiên Lương', 'Thất Sát', 'Phá Quân'];
  const palaces = ['Mệnh', 'Phụ Mẫu', 'Phúc Đức', 'Điền Trạch', 'Quan Lộc', 'Nô Bộc', 'Thiên Di', 'Tật Ách', 'Tài Bạch', 'Tử Tức', 'Phu Thê', 'Huynh Đệ'];
  for (const s of majors) for (const p of palaces) for (const f of ['core', 'bright', 'dim', 'advice'] as const) assert.ok(P.chinh[s]?.[p]?.[f], `${s} ${p} ${f}`);
  const texts = [...Object.values(P.chinh).flatMap(x => Object.values(x).flatMap(c => Object.values(c))), ...Object.values(P.phu).flatMap(c => [c.line, c.advice])];
  for (const t of texts) {
    const low = ' ' + t.toLowerCase();
    for (const w of [...META, ...ABSOLUTE]) assert.ok(!low.includes(w.startsWith(' ') ? w : (META.includes(w) ? ' ' + w : w)), `"${w}" in: ${t}`);
    assert.ok(!t.startsWith('{S}'), t);
  }
});

test('300 charts: every palace chapter says something, passes validation, answers each difficulty, and Tuần/Triệt only where they are',
  { skip: !existsSync(corpusUrl) && 'corpus not built' }, () => {
  const rmap = new Map(K.rules.map(r => [r.id, JSON.stringify(r.conditions)]));
  for (const c of corpus(300)) {
    for (const ch of proseReport(c, K, { allowDraft: true, deep: true })) {
      assert.ok(ch.paragraphs.length, `${ch.chapter} empty`);
      assert.ok(ch.pass, `${ch.chapter}: ${JSON.stringify(ch.issues.filter(i => i.level === 'error'))}`);
      const ss = ch.paragraphs.flatMap(p => p.sentences);
      if (ss.some(s => s.trace.tone === 'neg')) assert.ok(ss.some(s => s.trace.tone === 'answer'), `${ch.chapter}: a difficulty with nothing answering it`);
      for (const s of ss) assert.ok(s.trace.basis !== 'sach' || s.trace.rules.length, s.text);
      const pal = c.palaces.find(p => p.name === ch.palace)!;
      const struct = ss.filter(s => s.trace.move === 'STRUCT');
      if (!pal.tuan) assert.ok(!struct.some(s => s.trace.step === 'tuan'), `${ch.palace}: Tuần said without Tuần`);
      if (!pal.triet) assert.ok(!struct.some(s => s.trace.step === 'triet'), `${ch.palace}: Triệt said without Triệt`);
      // the book wins: a star a voiced book rule speaks of has no card core in this chapter
      const book = ss.filter(s => s.trace.basis === 'sach').flatMap(s => s.trace.rules).map(id => rmap.get(id) ?? '');
      for (const s of ss.filter(x => x.trace.step === 'colour')) {
        const star = pal.major_stars.find(m => s.text.includes(m) && book.some(b => b.includes(`"${m}"`)));
        assert.ok(!star || !P.chinh[star]?.[ch.palace] || !s.text.includes(P.chinh[star][ch.palace].core.slice(0, 30)), `${ch.palace}: card read for ${star} after the book spoke of it`);
      }
    }
  }
});

test('the user\'s chart: đại hạn read with Khảo Luận and the nhập hạn ca, the current year told, Bát Tự strength by Thiệu Vĩ Hoa', () => {
  const v = proseVanHan(user, K, seedOf(user), PROSE_VERSION, true);
  assert.ok(v.pass, JSON.stringify(v.issues));
  assert.equal(v.starts.length, Math.min(10, user.decades.length));
  const ss = v.paragraphs.flatMap(p => p.sentences);
  assert.ok(ss.some(s => s.trace.cites.includes('KL pp.230-233')), 'Khảo Luận pp.230-233 voiced');
  assert.ok(ss.filter(s => s.trace.cites.includes('TT pp.97-105')).every(s => s.trace.basis === 'pho_thong'), 'nhập hạn ca not yet page-checked: never said as the book');
  assert.ok(v.paragraphs.some(p => p.sentences[0].text.startsWith(`Năm ${user.year.year}`)), 'the year paragraph');
  // the Tử Vi verse's exception replaces its general reading
  assert.ok(!ss.some(s => /thăng tiến/.test(s.text) && ss.some(t => t !== s && /dễ bị giáng/.test(t.text) && v.paragraphs.find(p => p.sentences.includes(s))?.sentences.includes(t))));
  const b = proseBazi(user, K, seedOf(user), PROSE_VERSION, true);
  assert.ok(b.pass, JSON.stringify(b.issues));
  for (const id of ['nhat-chu', 'cach-cuc', 'ngu-hanh', 'su-nghiep', 'quan-he', 'dai-van'] as const) assert.ok(b.chapters[id]?.length, id);
  // own share 38 % against 40 %: the book's rule decides (TVH p.355 calls 39.6 % "hơi nhược"); the system's ±3 % band is only the note (S2, BZ-9/10)
  const near = b.chapters['nhat-chu']!.flatMap(p => p.sentences).find(s => /hơi nhược/.test(s.text));
  assert.ok(near && /không phải của sách/.test(near.trace.note ?? ''), 'near the line: "hơi nhược", with the band as a note');
  assert.ok(b.chapters['dai-van']!.length >= 6, 'one paragraph per luck pillar');
});
