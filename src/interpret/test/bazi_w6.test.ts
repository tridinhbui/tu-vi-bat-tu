// REVIEW-19 W6 (2026-10-23): the Bát Tự reading less computational and more practical. Over the 1,000-chart corpus (facts refreshed with
// tools/interpret/refresh_bazi_deep.py --corpus) and the owner's chart, as the reader gets it (checked readings only):
//   - the short reading (outside the Đọc sâu / Số liệu folds) is under 35 % calculation sentences, and holds no degree or percent figure;
//   - every Ten-God combination told (kin._patterns) is followed by what a verified, page-checked judgement says of it; the combinations without
//     a page (Thương Quan phối Ấn, Chế Sát quá mức) never reach the text as a combination;
//   - two-sided money and rank are weighed: no "không lời nào xếp bên nào nặng hơn" left, every weighing names its reason, basis tong_hop;
//   - the cách condition is said once per chapter, not at every luck pillar and year;
//   - the closing goes by priority: the pillar being walked and the year, money, work, then the timeline.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { proseBazi } from '../prose/bazi.ts';
import { checkedOnly } from '../prose/checked.ts';
import { seedOf } from '../prose/chapter.ts';
import type { ProseParagraph, ProseSentence } from '../prose/realize.ts';
import type { ChartInput, Knowledge } from '../types.ts';

const FX = new URL('./fixtures/', import.meta.url);
const K: Knowledge = JSON.parse(readFileSync(new URL('../generated/knowledge.json', import.meta.url), 'utf8'));
const corpusUrl = new URL('corpus1000.json.gz', FX);
const reader = (f: ChartInput) => checkedOnly(proseBazi(f, K, seedOf(f), 'test', true) as Parameters<typeof checkedOnly>[0]) as ReturnType<typeof proseBazi>;
type Ch = Partial<Record<string, ProseParagraph[]>>;
const NUMBER = /\d+(,\d+)? độ|\d+(,\d+)?%/;
const UNWEIGHED = /không lời nào (xếp|cân)|không mặt nào được xếp|không được cân với nhau/;

function problems(label: string, f: ChartInput): { bad: string[]; n: number; t: number } {
  const o = reader(f), ch = o.chapters as Ch, bad: string[] = [];
  let n = 0, t = 0;
  for (const [id, ps] of Object.entries(ch)) for (const p of ps ?? []) {
    const ss = p.sentences;
    if (p.depth !== 'sau') for (const s of ss) {
      n++; if (s.trace.basis === 'tinh_toan') t++;
      if (NUMBER.test(s.text)) bad.push(`${label}: ${id}: a number in the short reading: ${s.text}`);
    }
    ss.forEach((s: ProseSentence, i) => {
      if (UNWEIGHED.test(s.text)) bad.push(`${label}: unweighed: ${s.text}`);
      const step = s.trace.step ?? '';
      if (step.startsWith('kin:pt:')) {
        if (/thuong_phoi_an|che_sat_qua_muc/.test(step)) bad.push(`${label}: a combination without a page: ${s.text}`);
        const next = ss.slice(i + 1).find(x => (x.trace.step ?? '').startsWith('kin:'));
        if (!next || next.trace.basis !== 'sach' || !next.trace.rules.every(r => o.evidence.rules[r]?.verified)) bad.push(`${label}: combination with no book line after it: ${s.text}`);
      }
      if (step === 'kin:tai_weigh' || step === 'kin:rank_weigh') {
        if (s.trace.basis !== 'tong_hop' || !/ vì /.test(s.text) || !s.trace.note) bad.push(`${label}: weighing without its reason or label: ${s.text}`);
      }
    });
  }
  // the cách condition once per chapter
  for (const id of ['dai-van', 'luu-nien']) {
    const k = (ch[id] ?? []).filter(p => p.depth !== 'sau').flatMap(p => p.sentences).filter(s => s.trace.basis === 'tinh_toan' && /đứng được/.test(s.text)).length;
    if (k > 1) bad.push(`${label}: ${id}: the cách condition said ${k} times`);
  }
  // the closing by priority
  const tk = (ch['tong-ket'] ?? []).flatMap(p => p.sentences).map(s => s.trace.step ?? '');
  const at = (x: string) => tk.indexOf(x), ph = tk.findIndex((x, i) => x === 'closing:bat_tu' && i > 0 && ((ch['tong-ket'] ?? []).flatMap(p => p.sentences)[i].trace as { verdicts?: unknown }).verdicts);
  for (const [a, b] of [['closing:now', 'closing:money'], ['closing:money', 'closing:work']] as const)
    if (at(a) >= 0 && at(b) >= 0 && at(a) > at(b)) bad.push(`${label}: closing out of order: ${a} after ${b}`);
  if (at('closing:now') >= 0 && ph >= 0 && at('closing:now') > ph) bad.push(`${label}: the pillar being walked told after the timeline`);
  return { bad, n, t };
}

test('owner chart (09/01/2002): Thực Thần sinh Tài told with its page line, money weighed by the day master against Tài, numbers in Số liệu', () => {
  const f: ChartInput = JSON.parse(readFileSync(new URL('ref_2002_01_09_kl.json', FX), 'utf8'));
  const { bad, n, t } = problems('ref_2002', f);
  assert.deepEqual(bad, []);
  assert.ok(t / n < 0.35, `${t}/${n}`);
  const ch = reader(f).chapters as Ch, sn = (ch['su-nghiep'] ?? []).filter(p => p.depth !== 'sau');
  const combo = sn.find(p => p.topic === 'kin_combo');
  assert.ok(combo && /Thực Thần sinh Tài/.test(combo.text) && combo.sentences.some(s => s.trace.rules.includes('BT_TVHK_PT_TSS2')), combo?.text);
  const w = sn.flatMap(p => p.sentences).find(s => s.trace.step === 'kin:tai_weigh');
  assert.ok(w && /mặt nghịch/.test(w.text) && /nhật chủ Đinh nhược mà Tài nhiều/.test(w.text), w?.text);
  // the degrees are told in the Số liệu fold of the strength
  const nc = ch['nhat-chu'] ?? [];
  assert.ok(nc.some(p => p.depth === 'sau' && p.depthTitle === 'Số liệu · sức vượng nhược' && /60 trên 234,6 độ|60 độ trong tổng số 234,6|cộng lại 60/.test(p.text)), nc.map(p => p.depthTitle).join(' | '));
  // the closing names the pillar being walked first, then money
  assert.match((ch['tong-ket'] ?? []).map(p => p.text).join(' '), /Mậu Tuất[^.]*nặng[^.]*; năm 2026 \(Bính Ngọ\) thuận[^]*tiền bạc/);
});

test('1,000 charts: short reading under 35 % calculation, combinations with their page lines, money weighed, the condition said once, closing by priority',
  { skip: !existsSync(corpusUrl) && 'corpus not built' }, () => {
  const cs = (JSON.parse(gunzipSync(readFileSync(corpusUrl)).toString('utf8')) as Array<{ label: string; facts: ChartInput }>);
  let N = 0, T = 0, combos = 0;
  const bad: string[] = [];
  for (const c of cs) {
    const r = problems(c.label, c.facts);
    bad.push(...r.bad); N += r.n; T += r.t;
    combos += Object.values(reader(c.facts).chapters as Ch).flat().flatMap(p => p!.sentences).filter(s => (s.trace.step ?? '').startsWith('kin:pt:')).length;
  }
  console.log(`# corpus1000: short reading ${N} sentences, tinh_toan ${(100 * T / N).toFixed(1)} %, ${combos} combinations told`);
  assert.deepEqual(bad.slice(0, 8), [], `${bad.length} problems`);
  assert.ok(T / N < 0.35, `${T}/${N}`);
  assert.ok(combos > 500, String(combos));
});
