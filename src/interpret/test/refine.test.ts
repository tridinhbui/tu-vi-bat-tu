// The model refinement layer (plan THIEN-BAN-33 G10.7 cách 2, owner decisions 2026-11-08: a few small places only, as few tokens as
// possible): which paragraphs are picked, the request is small, and the verifier keeps the draft whenever the model adds or loses anything.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { ChartInput, Knowledge } from '../types.ts';
import { proseAllChapters } from '../route.ts';
import { checkedOnly } from '../prose/checked.ts';
import { refineReport, reportRequest, selectParagraphs, parseAnswer, SYSTEM } from '../refine/refine.ts';
import { verifyParagraph } from '../refine/verify.ts';
import type { ProseParagraph, ProseSentence } from '../prose/realize.ts';

const FX = join(import.meta.dirname, 'fixtures');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const owner: ChartInput = JSON.parse(readFileSync(join(FX, 'owner_2002_kl_2026-11.json'), 'utf8'));
type Ch = { chapter: string; paragraphs: ProseParagraph[]; text?: string };
const report = proseAllChapters(owner, K, { allowDraft: true, deep: true, luan: true }).map(c => checkedOnly(c as never, owner)) as unknown as Ch[];
const S = (text: string, basis: ProseSentence['trace']['basis'] = 'sach'): ProseSentence => ({ text, trace: { move: 'VALUE', concepts: [], rules: ['R'], cites: [], basis } });

test('a few paragraphs only, in one small request', () => {
  const picks = selectParagraphs(report);
  assert.ok(picks.length >= 1 && picks.length <= 6, `${picks.length}`);
  for (const { c, p } of picks) assert.ok(!report[c].paragraphs[p].deep && report[c].paragraphs[p].sentences.length >= 3);
  const chars = SYSTEM.length + reportRequest(report, picks).length;
  console.log(`# ${picks.length} paragraphs, request ${chars} chars`);
  assert.ok(chars < 9000, `request ${chars} chars`);
});

test('the verifier: a faithful rewrite passes; an added star, a lost limit, a dropped sentence or a new absolute keeps the draft', () => {
  const d = [S('Với Thân cư Quan Lộc, công danh đến muộn.'), S('Tả Phụ ở Quan Lộc cho thấy được người trên tin cậy, song chỉ phần nào.')];
  assert.deepEqual(verifyParagraph(d, [{ src: [0, 1], text: 'Thân cư Quan Lộc khiến công danh đến muộn, dù Tả Phụ ở Quan Lộc vẫn cho được người trên tin cậy, song chỉ phần nào.' }]).reasons, []);
  assert.ok(!verifyParagraph(d, [{ src: [0, 1], text: 'Thân cư Quan Lộc cùng Thái Dương khiến công danh đến muộn, Tả Phụ ở Quan Lộc cho được người trên tin cậy phần nào.' }]).ok, 'added star');
  assert.ok(!verifyParagraph(d, [{ src: [0], text: 'Với Thân cư Quan Lộc, công danh đến muộn.' }]).ok, 'dropped sentence');
  assert.ok(!verifyParagraph(d, [{ src: [0, 1], text: 'Thân cư Quan Lộc làm công danh đến muộn; Tả Phụ ở Quan Lộc cho được người trên tin cậy.' }]).ok, 'lost limit');
  assert.ok(!verifyParagraph(d, [{ src: [0, 1], text: 'Thân cư Quan Lộc chắc chắn làm công danh đến muộn, song Tả Phụ ở Quan Lộc cho được người trên tin cậy phần nào.' }]).ok, 'absolute');
});

test('refineReport with a stub model: the answer is parsed, a good paragraph is replaced, a bad one keeps its draft', async () => {
  const picks = selectParagraphs(report, 2);
  const [a, b] = picks;
  const echo = (c: number, p: number, mangle = false) => [`#${c}.${p}`, ...report[c].paragraphs[p].sentences.map((s, j) => `${j}| ${mangle && j === 0 ? s.text + ' Tử Vi cũng vậy.' : s.text}`)].join('\n');
  const r = await refineReport(report, async () => ({ text: `${echo(a.c, a.p)}\n\n${b ? echo(b.c, b.p, true) : ''}`, usage: { input: 1, output: 1 } }), { max: 2 });
  const ra = r.results.find(x => x.chapter === report[a.c].chapter && x.index === a.p)!;
  assert.ok(ra.ok, ra.reasons.join('; '));
  assert.ok((r.chapters[a.c].paragraphs[a.p] as ProseParagraph & { refined?: boolean }).refined);
  if (b) { const rb = r.results.find(x => x.chapter === report[b.c].chapter && x.index === b.p)!; assert.ok(!rb.ok); assert.equal(r.chapters[b.c].paragraphs[b.p], report[b.c].paragraphs[b.p]); }
  assert.equal(parseAnswer('#1.2\n0,1| câu\nlinh tinh').get('1.2')!.at(-1)!.src.length, 0, 'a malformed line has no source');
});
