// Luận cung chapters (prose/luan.ts, prose-style plan S2–S4): golden text for the worked example; the reference's shape (frame naming the
// palace's stars with checked brightness and the brightest star around it, bold topic lead-ins, Thân cư, cung giáp / nhị hợp / lục hại as
// positions, closing); and, over the corpus, no blocking error, every book sentence a fired verified rule, the system's tail sentences
// claiming nothing the paragraph did not say, no reading told twice in the report.
// Regenerate the golden:  UPDATE_GOLDEN=1 node --test src/interpret/test/luan.test.ts
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import type { Knowledge } from '../types.ts';
import { run } from '../engine.ts';
import { luanReport, luanChapter, luanShared, withLead, type LuanChapter } from '../prose/luan.ts';
import { reasonedChapter } from '../prose/narrative.ts';
import { ABSOLUTE, META } from '../prose/lint.ts';

const FX = join(import.meta.dirname, 'fixtures');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const ex = JSON.parse(readFileSync(join(FX, 'menh_cu_tuat.json'), 'utf8')).facts;
const corpusFile = join(FX, 'corpus1000.json.gz');
const rmap = new Map(K.rules.map(r => [r.id, r]));
const isLuan = (c: { luan?: boolean }): c is LuanChapter => !!c.luan;

test('luan.json: no frame uses meta-language or an absolute, every slot is one the writer fills', () => {
  const SLOTS = new Set(['pal', 'branch', 'majors', 'star', 'from', 'stars', 'tt', 'a', 'b', 'group', 'note', 'S', 'mature', 'seat', 'config', 'domain', 'claim', 'text',
    'pair', 'left', 'right', 'other', 'opal', 'neg', 'pos', 'list', 'age', 'young', 'np', 'late']);
  const walk = (x: unknown, at: string): void => {
    if (typeof x === 'string') {
      const low = ' ' + x.toLowerCase();
      for (const w of META) assert.ok(!low.includes(' ' + w), `${at}: meta "${w}" in ${x}`);
      for (const w of ABSOLUTE) assert.ok(!low.includes(w), `${at}: absolute "${w}" in ${x}`);
      for (const m of x.matchAll(/\{([A-Za-z_]+)\}/g)) assert.ok(SLOTS.has(m[1]), `${at}: slot {${m[1]}}`);
    } else if (Array.isArray(x)) x.forEach((y, i) => walk(y, `${at}[${i}]`));
    else if (x && typeof x === 'object') for (const [k2, v] of Object.entries(x)) walk(v, `${at}.${k2}`);
  };
  const { status: _s, ...lib } = K.prose!.luan!;
  walk(lib, 'luan');
});

test('withLead: the lead-in, then the sentence lowered unless it opens with a name, its opening connective dropped', () => {
  assert.equal(withLead('Về tính cách', 'Ngoài ra, Cự Môn hãm …'), 'Về tính cách, Cự Môn hãm …');
  assert.equal(withLead('Về tính cách', 'Với Thái Dương tọa …'), 'Về tính cách, với Thái Dương tọa …');
  assert.equal(withLead('Về tiền bạc', 'Tiểu Hao ở vào thế hãm', new Set(['Tiểu Hao'])), 'Về tiền bạc, Tiểu Hao ở vào thế hãm');
});

test('worked example (Cự Môn hãm hóa Lộc tại Tuất): the reference shape, golden text', () => {
  const chs = luanReport(ex, K, { allowDraft: true, deep: true });
  const menh = chs.find(c => c.chapter === 'menh')!;
  assert.ok(isLuan(menh), 'Mệnh is a luận cung chapter');
  assert.ok(menh.pass, JSON.stringify(menh.issues.filter(i => i.level === 'error')));
  const [frame, ...rest] = menh.paragraphs;
  // the palace, its branch, the chính tinh with checked brightness and its Hóa, the brightest star of the tam phương and where it shines from
  for (const x of ['Mệnh', 'Tuất', 'Cự Môn (Hãm Địa) hóa Lộc', 'Thái Dương (Vượng Địa) hóa Quyền', 'cung Tài Bạch (Ngọ)']) assert.ok(frame.sentences[0].text.includes(x), `${x}: ${frame.sentences[0].text}`);
  assert.equal(frame.sentences[0].trace.basis, 'tinh_toan');
  assert.match(frame.text, /nhóm Cự – Nhật – Nguyệt/);
  assert.ok(rest.filter(p => p.lead).length >= 4, 'topic paragraphs open with a lead-in');
  for (const p of rest.filter(p => p.lead)) assert.ok(p.sentences[0].text.startsWith(p.lead + ', '), p.text);
  assert.ok(rest.some(p => p.topic === 'than' && p.lead?.includes('Tài Bạch')), 'Thân cư Tài Bạch');
  assert.ok(rest.some(p => p.topic === 'tong_ket'), 'closing');
  const pos = rest.find(p => p.topic === 'vi_tri')!;
  assert.ok(pos.sentences.every(s => s.trace.basis === 'tinh_toan' && !s.trace.rules.length), 'positions carry no reading');
  assert.match(pos.text, /nhị hợp với Mão/);
  // the reasoned Mệnh chapter (mode reasoned) is not changed by the luận cung form
  assert.ok(reasonedChapter(ex, K, { allowDraft: true }).pass);
  const golden = join(FX, 'menh_cu_tuat.luan.txt');
  const text = chs.map(c => `== ${c.chapter}${isLuan(c) ? '' : ' (older chapter)'}\n${c.paragraphs.map(p => (p.lead ? `[${p.topic}] ` : '') + p.text).join('\n\n')}`).join('\n\n') + '\n';
  if (process.env.UPDATE_GOLDEN || !existsSync(golden)) writeFileSync(golden, text);
  assert.equal(text, readFileSync(golden, 'utf8'));
});

test('without draft prose the luận cung form is off (the library is a draft)', () => {
  const sh = luanShared(ex, K, false);
  assert.equal(K.prose!.luan!.status, 'draft');
  const chs = luanReport(ex, K, { allowDraft: false });
  assert.ok(chs.every(c => !isLuan(c)));
  void sh; void luanChapter;
});

test('corpus: every luận cung chapter passes; book sentences fire and are verified; tails claim nothing new; no reading twice',
  { skip: !existsSync(corpusFile) && 'corpus not built' }, () => {
  const corpus = JSON.parse(gunzipSync(readFileSync(corpusFile)).toString('utf8'));
  let luan = 0, total = 0;
  for (const c of corpus.slice(0, 250)) {
    const facts = c.facts;
    const fired = new Set(run(K.rules, K.sources, facts.base).findings.map(f => f.ruleId));
    const keys = new Map<string, string>();
    for (const ch of luanReport(facts, K, { allowDraft: true, deep: true })) {
      total++;
      if (!isLuan(ch)) continue;
      luan++;
      assert.ok(ch.pass, `${c.id ?? ''} ${ch.chapter}: ${JSON.stringify(ch.issues.filter(i => i.level === 'error'))}`);
      for (const p of ch.paragraphs) {
        if (p.lead) assert.ok(p.sentences[0].text.startsWith(p.lead + ', '), p.text);
        for (const s of p.sentences) {
          assert.ok(s.trace.step, `no step: ${s.text}`);
          if (s.trace.basis === 'sach') for (const id of s.trace.rules) {
            assert.ok(fired.has(id), `${id} did not fire: ${s.text}`);
            assert.equal(rmap.get(id)?.reviewStatus, 'verified', `${id}: ${s.text}`);
          }
          if (s.trace.basis === 'he_thong') assert.equal(s.trace.rules.length, 0, s.text);
          if (s.trace.basis === 'sach' && s.trace.move !== 'ELABORATE') for (const k of s.trace.keys ?? []) {
            assert.ok(!keys.has(k), `${k} told twice: ${keys.get(k)} / ${s.text}`);
            keys.set(k, s.text);
          }
        }
      }
      if (ch.palace === 'Tật Ách' && ch.paragraphs.some(p => p.topic === 'the_trang')) assert.match(ch.text, /thầy thuốc/);
    }
  }
  assert.ok(luan / total > 0.6, `luận cung chapters ${luan}/${total}`);
});
