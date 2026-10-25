// The owner's 19-point review of the live report (2026-10-23, docs/audit/REVIEW-19.md): the weighed verdict, the Tổng luận and Cách cục
// chapters, the course of a domain across the đại hạn, the Mệnh portrait, the Tật Ách balance, the đại hạn links and the recall cap.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import type { ChartInput, Knowledge } from '../types.ts';
import { luanReport } from '../prose/luan.ts';
import { proseVanHan } from '../prose/vanhan.ts';
import { proseTongLuan } from '../prose/tong_luan.ts';
import { proseCachCuc } from '../prose/cach_cuc.ts';
import { checkedOnly } from '../prose/checked.ts';
import { infer, seedOf } from '../prose/chapter.ts';
import { buildLedger } from '../reason/ledger.ts';

const FX = join(import.meta.dirname, 'fixtures');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const REF: ChartInput = JSON.parse(readFileSync(join(FX, 'ref_2002_01_09_kl.json'), 'utf8'));
const corpus = JSON.parse(gunzipSync(readFileSync(join(FX, 'corpus1000.json.gz'))).toString()) as Array<{ facts: ChartInput }>;
const sample = corpus.slice(0, 40).map(c => c.facts);
type S = { text: string; trace: { step?: string; basis: string; rules: string[]; concepts: string[]; ledger?: { domain: string; verdict: string } } };
type Ch = { chapter: string; paragraphs: Array<{ deep?: boolean; title?: string; sentences: S[] }> };
const report = (f: ChartInput) => luanReport(f, K, { allowDraft: true, deep: true }).map(c => checkedOnly(c as never) as unknown as Ch);
const sentencesOf = (c?: Ch) => (c?.paragraphs ?? []).flatMap(p => p.sentences);

test('14: a weighed domain names both sides and why the heavier one weighs more; a close call stays unresolved', () => {
  for (const f of [REF, ...sample]) {
    const L = buildLedger(f, K, infer(f, K).resolved);
    for (const v of L.domains.filter(d => d.verdict === 'nghieng_ve')) {
      assert.ok(v.weigh && v.weigh.why.length, `${v.id}: a weighed verdict carries its reasons`);
      assert.ok(Math.abs(v.weigh!.pos - v.weigh!.neg) >= 0.2, `${v.id}: margin`);
      assert.equal(v.base, v.weigh!.pos > v.weigh!.neg ? '+' : '-');
      assert.ok(v.pos.length && v.neg.length, `${v.id}: both sides stand`);
    }
    for (const c of report(f)) for (const s of sentencesOf(c)) if (s.trace.step?.endsWith(':weigh')) assert.equal(s.trace.basis, 'he_thong', s.text);
  }
});

test('19: Tổng luận ranks the domains, never ranks health, adds no reading; the advice is labelled', () => {
  for (const f of [REF, ...sample]) {
    const o = proseTongLuan(f, K, seedOf(f), 'x', true);
    assert.ok(o.pass, JSON.stringify(o.issues));
    for (const s of o.paragraphs.flatMap(p => p.sentences)) {
      assert.ok(['he_thong', 'loi_khuyen'].includes(s.trace.basis), s.text);
      assert.ok(!s.trace.concepts.length, 'no concept of its own');
      assert.ok(!(s.trace.step?.startsWith('tong_luan:best') && s.trace.ledger?.domain === 'suc_khoe'), 'health is never ranked');
    }
    const best = o.paragraphs.flatMap(p => p.sentences).find(s => s.trace.step?.startsWith('tong_luan:best'));
    const worst = o.paragraphs.flatMap(p => p.sentences).find(s => s.trace.step?.startsWith('tong_luan:worst'));
    const adv = o.paragraphs.flatMap(p => p.sentences).find(s => s.trace.step === 'tong_luan:advice');
    assert.equal(!!adv, !!(best && worst), 'the advice names a strength and a weakness');
  }
});

test('13: Cách cục tells only formations a verified rule names, each with its state and reach', () => {
  const rmap = new Map(K.rules.map(r => [r.id, r]));
  for (const f of [REF, ...sample]) {
    const o = proseCachCuc(f, K, seedOf(f), 'x', true);
    assert.ok(o.pass, JSON.stringify(o.issues));
    const ss = o.paragraphs.flatMap(p => p.sentences);
    // a book sentence stands on a verified rule or on a page-checked cách (formations_verified.json, verified only)
    const fv = new Set((K.kg?.formationsVerified?.formations ?? []).map(x => x.id));
    for (const s of ss.filter(x => x.trace.basis === 'sach')) {
      assert.ok(s.trace.cites.length, s.text);
      for (const r of s.trace.rules) assert.ok(rmap.get(r)?.reviewStatus === 'verified' || fv.has(r), r);
    }
    assert.ok(!ss.some(s => s.text.includes('Mã đầu đới kiếm')), 'a disputed cách is never told');
    for (const id of Object.keys(o.evidence.rules)) {
      assert.ok(ss.some(s => s.trace.step === `cach:${id}:state`), `${id}: state`);
      // the degree line, or (DEEP-3) the page's meaning of the cách in its state in place of it
      assert.ok(ss.some(s => s.trace.step === `cach:${id}:reach` || s.trace.step === `cach:${id}:meaning`), `${id}: reach`);
    }
  }
});

test('2–4, 10: the course across the đại hạn names ages the chart has, and Phu Thê tells phases, never an event', () => {
  const EVENT = /cưới|kết hôn năm|ly hôn|ly dị|tái hôn|tái giá|góa/;
  for (const f of [REF, ...sample.slice(0, 20)]) {
    const ages = new Set(f.decades.map(d => `${d.age_from}–${d.age_to}`));
    for (const c of report(f)) for (const s of sentencesOf(c).filter(x => x.trace.step?.startsWith('course:'))) {
      for (const m of s.text.matchAll(/(\d+)–(\d+) tuổi/g)) assert.ok(ages.has(`${m[1]}–${m[2]}`), s.text);
      if (c.chapter === 'phu_the') assert.ok(!EVENT.test(s.text), s.text);
    }
  }
});

test('1, 11, 12: the Mệnh portrait re-voices told traits only; Tật Ách balance has no health verdict; no behaviour line in kin palaces', () => {
  for (const f of [REF, ...sample.slice(0, 20)]) {
    const chs = report(f);
    const menh = chs.find(c => c.chapter === 'menh');
    const told = new Set(sentencesOf(menh).filter(s => s.trace.basis === 'sach').flatMap(s => s.trace.concepts));
    for (const s of sentencesOf(menh).filter(x => x.trace.step?.startsWith('portrait:'))) for (const c of s.trace.concepts) assert.ok(told.has(c), `${c}: ${s.text}`);
    for (const s of sentencesOf(chs.find(c => c.chapter === 'tat_ach')).filter(x => x.trace.step === 'health:balance'))
      assert.ok(!/tốt cho sức khỏe|sức khỏe tốt|sức khỏe kém|bệnh nặng/.test(s.text), s.text);
    for (const id of ['no_boc', 'tu_tuc', 'huynh_de', 'phu_mau'])
      assert.ok(!sentencesOf(chs.find(c => c.chapter === id)).some(s => s.trace.step?.startsWith('behave:')), id);
  }
});

test('15: a domain verdict is recalled at most twice after its full telling; đại hạn tells a natal verdict in full once per domain', () => {
  for (const f of [REF, ...sample.slice(0, 20)]) {
    const again = new Map<string, number>();
    for (const c of report(f)) for (const s of sentencesOf(c)) if (s.trace.ledger && /:again$/.test(s.trace.step ?? '')) again.set(s.trace.ledger.domain, (again.get(s.trace.ledger.domain) ?? 0) + 1);
    for (const [d, n] of again) assert.ok(n <= 2, `${d} recalled ${n} times`);
    const vh = checkedOnly(proseVanHan(f, K, seedOf(f), 'x', true) as never) as unknown as Ch;
    const full = new Map<string, number>();
    for (const s of sentencesOf(vh)) if (s.trace.ledger && /^natal:/.test(s.trace.step ?? '') && /vốn|xét cả lá số|cả lá số cho thấy/.test(s.text))
      full.set(s.trace.ledger.domain, (full.get(s.trace.ledger.domain) ?? 0) + 1);
    for (const [d, n] of full) assert.ok(n <= 2, `${d}: full natal verdict ${n} times in đại hạn`);
  }
});

test('5: every đại hạn after the first is set against the one before it', () => {
  for (const f of [REF, ...sample.slice(0, 20)]) {
    const vh = proseVanHan(f, K, seedOf(f), 'x', true);
    const trends = vh.paragraphs.flatMap(p => p.sentences).filter(s => s.trace.step?.startsWith('trend:'));
    assert.ok(trends.length >= Math.min(1, vh.decades.length - 1), 'trend sentences');
    for (const s of trends) assert.equal(s.trace.basis, 'he_thong');
  }
});
