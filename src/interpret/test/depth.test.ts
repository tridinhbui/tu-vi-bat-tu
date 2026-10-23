// The deep reading of Quan Lộc, Tài Bạch and Phu Thê (plan DEEP-TUVI, reason/depth.ts + prose/luan_deep.ts) and the minh họa policy
// (owner, 2026-10-22): every deep sentence stands on a reading, a page of Khảo Luận or a chart fact; a minh họa line is tied to exactly one
// sourced claim of its paragraph and goes with it; Phu Thê's deep reading carries no timing or event; the owner's 2002 chart gets the
// mechanisms the plan names.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { ChartInput, Knowledge } from '../types.ts';
import { luanReport } from '../prose/luan.ts';
import { checkedOnly, checkedParagraphs } from '../prose/checked.ts';
import { infer } from '../prose/chapter.ts';
import { buildLedger } from '../reason/ledger.ts';
import { domainDepth } from '../reason/depth.ts';
import type { ProseParagraph } from '../prose/realize.ts';
/** the method words of readable.test.ts (not imported: importing a test file runs its tests) */
const METHOD = /nguồn(?! (?:thu|lợi|tiền)\b)|quy tắc|đối chiếu|phạm vi|hệ thống|trọng số|cách hiểu|chưa có lời/iu;

const FX = join(import.meta.dirname, 'fixtures');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const REF: ChartInput = JSON.parse(readFileSync(join(FX, 'ref_2002_01_09_kl.json'), 'utf8'));
const REFS = JSON.parse(readFileSync(join(FX, 'deep_reference_charts.json'), 'utf8')) as Record<string, ChartInput>;
const bench = JSON.parse(readFileSync(join(FX, 'benchmark20.json'), 'utf8')) as Array<{ label: string; facts: ChartInput }>;
const charts: Array<[string, ChartInput]> = [['2002', REF], ['1911', REFS['1911-01-01_1230_nam']], ['1971', REFS['1971-05-24_1030_nam']], ...bench.map(b => [b.label, b.facts] as [string, ChartInput])];
type Ch = { chapter: string; paragraphs: ProseParagraph[] };
const read = (f: ChartInput) => luanReport(f, K, { allowDraft: true, deep: true }).map(c => checkedOnly(c as never) as unknown as Ch);
const all = charts.map(([label, f]) => ({ label, f, chs: read(f) }));
const deepOf = (chs: Ch[], id: string) => chs.find(c => c.chapter === id)?.paragraphs.filter(p => p.deep) ?? [];

test('every deep sentence has a step and stands on a reading, a page or a chart fact', () => {
  const bad: string[] = [];
  for (const { label, chs } of all) for (const c of chs) for (const p of c.paragraphs.filter(x => x.deep)) {
    assert.ok(p.title, `${label}/${c.chapter}: deep paragraph without title`);
    for (const s of p.sentences) {
      const t = s.trace;
      if (!t.step) bad.push(`${label}/${c.chapter} no step: ${s.text}`);
      if (t.basis === 'sach' && !t.rules.length && !t.cites.some(x => /^KL p/.test(x))) bad.push(`${label}/${c.chapter} sach without rule or page: ${s.text}`);
      if (t.basis === 'pho_thong') bad.push(`${label}/${c.chapter} phổ thông in deep: ${s.text}`);
      if (METHOD.test(s.text)) bad.push(`${label}/${c.chapter} method word: ${s.text}`);
    }
  }
  assert.deepEqual(bad.slice(0, 5), [], `${bad.length}`);
});

test('a minh họa line is tied to one book claim of its own paragraph, and goes when that claim goes', () => {
  let n = 0;
  for (const { chs } of all) for (const c of chs) for (const p of c.paragraphs) for (const s of p.sentences.filter(x => x.trace.basis === 'minh_hoa')) {
    n++;
    const claim = p.sentences.filter(x => x.trace.step === s.trace.tied);
    assert.equal(claim.length, 1, s.text);
    assert.equal(claim[0].trace.basis, 'sach');
    assert.ok(claim[0].trace.rules.length);
    assert.ok(!/\b(19|20)\d\d\b|\btuổi\b|năm nay|sắp tới|bệnh|từ sớm|về già/.test(s.text), `timing or health in a minh họa: ${s.text}`);
  }
  assert.ok(n > 0, 'some minh họa lines are told');
  // without its claim, the line is removed
  const claim = { text: 'A.', trace: { move: 'ANCHOR', step: 'deep:reading:X', basis: 'pho_thong', concepts: [], rules: ['X'], cites: [] } };
  const mh = { text: 'B.', trace: { move: 'ELABORATE', step: 'minh_hoa:x', basis: 'minh_hoa', tied: 'deep:reading:X', concepts: [], rules: [], cites: [] } };
  const fact = { text: 'C.', trace: { move: 'ANCHOR', step: 'frame:x', basis: 'tinh_toan', concepts: [], rules: [], cites: [] } };
  const out = checkedParagraphs([{ role: 'core', sentences: [claim, mh, fact], text: '' } as unknown as ProseParagraph]);
  assert.deepEqual(out.flatMap(p => p.sentences.map(s => s.text)), ['C.']);
});

test('Phu Thê deep reading: no timing, no event', () => {
  const cmap = new Map(K.concepts.concepts.map(c => [c.id, c]));
  for (const { label, chs } of all) for (const p of deepOf(chs, 'phu_the')) for (const s of p.sentences) {
    assert.ok(!s.trace.concepts.some(c => /timing$/.test(cmap.get(c)?.facet ?? '')), `${label}: ${s.text}`);
    assert.ok(!/\btuổi\b|lấy (vợ|chồng) (sớm|muộn)|ly dị|tái hôn|góa/.test(s.text), `${label}: ${s.text}`);
  }
});

test('owner chart 2002: the career deep reading names Thái Dương as the quan lộc star reaching a VCD Quan Lộc, the Kỵ behind công danh muộn, the Tứ Hóa of Mệnh–Tài–Quan', () => {
  const chs = all.find(x => x.label === '2002')!.chs;
  const cd = deepOf(chs, 'cong_danh').flatMap(p => p.sentences);
  assert.ok(cd.some(s => s.trace.step === 'mechanism:thai_duong.quan' && /Thái Dương/.test(s.text)), cd.map(s => s.text).join(' | '));
  assert.ok(cd.some(s => /^trigger:TV_TH_CACH_QUAN_LOC_THAN_TT$/.test(s.trace.step ?? '') && /Văn Xương hóa Kỵ ở cung Phu Thê/.test(s.text)));
  assert.ok(cd.some(s => s.trace.step === 'link:tu_hoa'));
  const tb = deepOf(chs, 'tai_bach').flatMap(p => p.sentences);
  assert.ok(tb.some(s => s.trace.step === 'mechanism:thai_duong.danh_tien'), 'the Tài Bạch reading says why Thái Dương brings money');
  assert.ok(tb.some(s => s.trace.step === 'link:tai.che_tai'));
  assert.ok(deepOf(chs, 'phu_the').length > 0);
});

test('the depth plan of a palace with a Hóa Kỵ in the opposite palace names it, and a star-nature line is told once per report', () => {
  const { resolved } = infer(REF, K);
  const ledger = buildLedger(REF, K, resolved);
  const said = new Set<string>();
  const plan = domainDepth(REF, K, 'cong_danh', { resolved, ledger, said });
  const units = plan.sections.flatMap(s => s.units);
  assert.ok(units.some(u => u.kind === 'trigger' && u.elements!.some(e => e.name === 'Hóa Kỵ' && e.palace === 'Phu Thê')));
  const ids = [...said];
  domainDepth(REF, K, 'tai_bach', { resolved, ledger, said });
  const after = [...said].slice(ids.length);
  assert.ok(!after.some(x => ids.includes(x)));
  // every deep paragraph's sentences are new to the report
  for (const { label, chs } of all) {
    const short = new Set(chs.flatMap(c => c.paragraphs.filter(p => !p.deep).flatMap(p => p.sentences.map(s => s.text))));
    for (const c of chs) for (const p of c.paragraphs.filter(x => x.deep)) for (const s of p.sentences) assert.ok(!short.has(s.text), `${label}/${c.chapter}: ${s.text}`);
  }
});
