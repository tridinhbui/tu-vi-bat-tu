// Vận hạn prose (prose plan P6): golden text for the worked example, ages always the chart's, every sentence traced, Thiên Lương's tam hợp
// reading, and the 1,000-chart run. Regenerate the golden after an intended change:  UPDATE_GOLDEN=1 node --test src/interpret/test/vanhan.test.ts
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { proseVanHan, tamHop, VAN_HAN_LAST_START } from '../prose/vanhan.ts';
import { seedOf } from '../prose/chapter.ts';
import type { ChartInput, Knowledge } from '../types.ts';

const K: Knowledge = JSON.parse(readFileSync(new URL('../generated/knowledge.json', import.meta.url), 'utf8'));
const ex = JSON.parse(readFileSync(new URL('./fixtures/menh_cu_tuat.json', import.meta.url), 'utf8'));
const goldenUrl = new URL('./fixtures/menh_cu_tuat.van_han.prose.txt', import.meta.url);
const corpusUrl = new URL('./fixtures/corpus1000.json.gz', import.meta.url);
const run = (f: ChartInput, draft = true) => proseVanHan(f, K, seedOf(f), 'test', draft);

test('tam hợp (Tử Vi Nghiệm Lý 1974): same group, sinh xuất, khắc nhập, khắc xuất; sinh nhập is not voiced', () => {
  assert.equal(tamHop('Ngọ', 'Tuất')?.kind, 'DONG');
  assert.equal(tamHop('Mùi', 'Ngọ')?.kind, 'SINH_XUAT');            // Mộc sinh Hỏa (NL p.58: Quý Mùi at a Hỏa vận)
  assert.equal(tamHop('Ngọ', 'Tý')?.kind, 'KHAC_NHAP');             // Thủy khắc Hỏa (NL p.66: Dần Ngọ Tuất at Tí)
  assert.equal(tamHop('Tuất', 'Sửu')?.kind, 'KHAC_XUAT');           // Hỏa khắc Kim (NL p.38, p.66: sa lầy)
  assert.equal(tamHop('Sửu', 'Thìn')?.kind, 'SINH_XUAT');           // Kim sinh Thủy (NL p.67)
  assert.equal(tamHop('Ngọ', 'Mão'), null, 'Mộc sinh Hỏa into the person: sinh nhập, nothing said');
});

test('worked example: golden text, ages straight from chart.decades, every sentence traced', () => {
  const o = run(ex.facts);
  if (process.env.UPDATE_GOLDEN === '1' || !existsSync(goldenUrl)) writeFileSync(goldenUrl, o.text + '\n');
  assert.equal(o.text + '\n', readFileSync(goldenUrl, 'utf8'));
  assert.ok(o.pass, JSON.stringify(o.issues));
  const want = (ex.facts as ChartInput).decades.filter(d => d.age_from <= VAN_HAN_LAST_START);
  assert.deepEqual(o.decades.map(d => [d.age_from, d.age_to, d.palace]), want.map(d => [d.age_from, d.age_to, d.palace]));
  // a book sentence names its rules and pages; a computed or common-meaning sentence (deep layers) says which it is
  for (const s of o.paragraphs.flatMap(p => p.sentences)) {
    if (s.trace.basis === 'sach') assert.ok(s.trace.rules.length && s.trace.cites.length, s.text);
    // the system's own sentences (S1): a hạn's Hóa under the convention of the hạn stem, its natal link, its level on the indices, its trend
    // against the previous hạn and what it touches most (review 2026-10-23); each says why
    else if (s.trace.basis === 'he_thong') assert.ok(/^(hoa|natal|level|trend):|^focus$/.test(s.trace.step ?? ''), s.text);
    else assert.ok(['tinh_toan', 'pho_thong'].includes(s.trace.basis), s.text);
    for (const id of s.trace.rules) assert.ok(o.evidence.rules[id]?.cites.length, id);
  }
  assert.equal(run(JSON.parse(JSON.stringify(ex.facts))).text, o.text, 'deterministic');
  assert.equal(run(ex.facts, false).paragraphs.length, 0, 'draft library: nothing without allowDraft');
});

test('1,000 charts: no blocking error, ages always the chart\'s, Thiên Lương never voiced on sinh nhập, up/down conflicts never voiced one-sided',
  { skip: !existsSync(corpusUrl) && 'corpus not built' }, () => {
  const corpus = JSON.parse(gunzipSync(readFileSync(corpusUrl)).toString('utf8'));
  let paras = 0, conflicts = 0;
  for (const c of corpus) {
    const f = c.facts as ChartInput, o = run(f);
    assert.ok(o.pass, `${c.label}: ${JSON.stringify(o.issues)}`);
    const want = f.decades.filter(d => d.age_from <= VAN_HAN_LAST_START);
    assert.equal(o.starts.length, want.length);
    o.starts.forEach((pi, i) => {
      // a decade's sentences: its first paragraph and, when present, the one after it up to the next decade
      const end = o.starts[i + 1] ?? o.paragraphs.findIndex((q, j) => j > pi && /^Năm \d{4}/.test(q.sentences[0].text));
      const ps = o.paragraphs.slice(pi, end < 0 ? undefined : end), p = { sentences: ps.flatMap(q => q.sentences) };
      paras++;
      assert.match(p.sentences[0].text, new RegExp(`${want[i].age_from}\\D+${want[i].age_to} tuổi`));
      const ids = p.sentences.flatMap(s => s.trace.rules);
      const rd = (want[i].readings as Array<{ rule_id?: string | null }>).map(r => r.rule_id);
      if (rd.some(r => r === 'VH_TPVT_CNDL') && rd.some(r => r === 'VH_TPVT_SAT' || r === 'VH_VCD_SPT')) {
        conflicts++;
        assert.ok(p.sentences.some(s => s.trace.rules.includes('VH_TPVT_CNDL') && s.trace.rules.length > 1), 'both-ways sentence');
      }
      for (const id of ids) assert.ok(!/SINH_NHAP/.test(id));
    });
  }
  assert.ok(paras > 7000, String(paras));
  console.log(`van_han: ${paras} paragraphs, ${conflicts} up/down conflicts`);
});
