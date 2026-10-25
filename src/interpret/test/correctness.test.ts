// Regression tests of the owner's review of 09/01/2002 04:30 nam (2026-10-22, docs/audit/DEEP-TUVI.md §Correctness). Each fix is at the root
// (facts, positions, plan, ledger); these hold it there:
//   2  a reducer never turns a domain into a strength; health gets no good / bad verdict at all
//   3  "cha mẹ hiền không đủ sức chống …" (TL p.127): the Phụ Mẫu stars are never the ground of the Tật Ách reading
//   4  a palace of other people never corroborates or counters another palace (Phụ Mẫu "cha mẹ khá giả" is not the children's wealth)
//   5  a timing reading never reconciles two qualities: with both sides and no book relation, the verdict is chưa phân xử (or hai mặt when
//      the sides speak of different facets), and the text names both
//   9  advice is labelled lời khuyên chung; illustration lines are minh họa tied to one claim
// (1, the borrowed star written as seated, is in positions_text.test.ts; 6–8 are Python-side, engine/tests/test_audit_correctness.py.)
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import type { ChartInput, Knowledge } from '../types.ts';
import { luanReport } from '../prose/luan.ts';
import { proseVanHan } from '../prose/vanhan.ts';
import { checkedOnly } from '../prose/checked.ts';
import { infer, PROSE_VERSION, seedOf } from '../prose/chapter.ts';
import { buildLedger } from '../reason/ledger.ts';
import { reasonPalace } from '../reason/plan.ts';

const FX = join(import.meta.dirname, 'fixtures');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const REF: ChartInput = JSON.parse(readFileSync(join(FX, 'ref_2002_01_09_kl.json'), 'utf8'));
const corpus = JSON.parse(gunzipSync(readFileSync(join(FX, 'corpus1000.json.gz'))).toString()) as Array<{ facts: ChartInput }>;
const sample = corpus.slice(0, 200).map(c => c.facts);
type S = { text: string; trace: { step?: string; basis: string; rules: string[]; ledger?: { domain: string; verdict: string }; tied?: string; move: string } };
const text = (f: ChartInput) => luanReport(f, K, { allowDraft: true, deep: true }).map(c => checkedOnly(c as never) as unknown as { chapter: string; paragraphs: Array<{ sentences: S[] }> });

test('2: health has no verdict word; a reducer is never a strength of its own', () => {
  const { resolved } = infer(REF, K);
  const L = buildLedger(REF, K, resolved);
  const h = L.domains.find(v => v.id === 'suc_khoe')!;
  assert.equal(h.verdict, 'khong_ket_luan');
  for (const f of [REF, ...sample]) {
    const led = buildLedger(f, K, infer(f, K).resolved);
    for (const v of led.domains) {
      assert.ok(!(v.id === 'suc_khoe' && v.verdict !== 'khong_ket_luan'), 'health gets no verdict');
      // a domain whose only strength is a book reducer of its limit is never thuận / có điều kiện (+)
      if (!v.pos.length && v.mitig.length) assert.ok(v.base !== '+' && v.verdict !== 'thuan', `${v.id}: ${v.verdict}`);
    }
    const sents = [...text(f).flatMap(c => c.paragraphs.flatMap(p => p.sentences)), ...proseVanHan(f, K, seedOf(f), PROSE_VERSION, true).paragraphs.flatMap(p => p.sentences as unknown as S[])];
    for (const s of sents) assert.ok(!/sức khỏe[^.;]{0,30}(thuận|vướng|trở ngại|gắng sức)/.test(s.text), s.text);
  }
});

test('3: TL p.127 stands on the bad stars at Tật Ách, never on the Phụ Mẫu stars that cannot hold them off', () => {
  const { resolved } = infer(REF, K);
  for (const r of resolved.filter(x => x.ruleId === 'TV_TL_TAT_ACH_NANG')) assert.ok(r.atoms.every(a => a.palace !== 'Phụ Mẫu'), JSON.stringify(r.atoms));
  const tat = text(REF).find(c => c.chapter === 'tat_ach')!.paragraphs.flatMap(p => p.sentences.map(s => s.text)).join(' ');
  assert.ok(!/Phụ Mẫu[^.]{0,40}(tai ách|bạo bệnh)/.test(tat), tat);
});

test('4: no corroboration or counter-evidence from or to a palace of other people', () => {
  for (const f of [REF, ...sample.slice(0, 80)]) {
    const { resolved, labelled } = infer(f, K);
    for (const P of ['Tử Tức', 'Phụ Mẫu', 'Huynh Đệ', 'Nô Bộc', 'Phu Thê', 'Mệnh', 'Tài Bạch', 'Quan Lộc']) {
      const plan = reasonPalace(f, K, P, { resolved, labelled });
      for (const t of plan.theses) for (const x of t.cross) assert.ok(!['Tử Tức', 'Phụ Mẫu', 'Huynh Đệ', 'Nô Bộc', 'Phu Thê'].includes(x.palace) && !['Tử Tức', 'Phụ Mẫu', 'Huynh Đệ', 'Nô Bộc', 'Phu Thê'].includes(P), `${P} ← ${x.palace} ${x.ruleId}`);
    }
  }
  const tt = text(REF).find(c => c.chapter === 'tu_tuc')!.paragraphs.flatMap(p => p.sentences);
  assert.ok(!tt.some(s => /^corroborated:Phụ Mẫu/.test(s.trace.step ?? '')));
});

test('5: two sides with no book relation are named and left unresolved; a timing reading never ties them', () => {
  const { resolved } = infer(REF, K);
  const L = buildLedger(REF, K, resolved);
  assert.equal(L.domains.find(v => v.id === 'cong_danh')!.verdict, 'chua_phan_xu');
  // hôn nhân: Thái Âm vượng (chính tinh) against Đà La — the system's scale weighs the sides (owner decision 2026-10-23), naming why
  const hn = L.domains.find(v => v.id === 'hon_nhan')!;
  assert.ok(['chua_phan_xu', 'hai_mat', 'nghieng_ve'].includes(hn.verdict));
  if (hn.verdict === 'nghieng_ve') assert.ok(hn.weigh!.why.length && hn.weigh!.heavy && hn.weigh!.light, 'a weighed domain says why');
  for (const f of [REF, ...sample]) {
    const led = buildLedger(f, K, infer(f, K).resolved);
    for (const v of led.domains) assert.ok(v.link?.kind !== 'timing', `${v.id} tied by timing`);
    for (const c of text(f)) for (const p of c.paragraphs) for (const s of p.sentences)
      assert.ok(!/điều nối hai mặt|nối với nhau ở chỗ|hai mặt ấy gặp nhau ở chỗ/.test(s.text), s.text);
  }
  const menh = text(REF).find(c => c.chapter === 'menh')!.paragraphs.flatMap(p => p.sentences).find(s => s.trace.ledger?.domain === 'cong_danh' && s.trace.step?.endsWith(':chua_phan_xu'))!;
  // the positive side is named by its leading reading: since Tử Vi Hàm Số (Thiên Việt and Tả Phụ ở Quan Lộc, HS pp.178, 210) that is danh tiếng
  assert.ok(/thuận lợi trong công việc|danh tiếng/.test(menh.text) && /trở ngại trong công việc/.test(menh.text) && /chưa (có lời sách nào )?phân xử|chưa có phân xử|chưa phân xử được/.test(menh.text), menh.text);
});

test('9: advice is "lời khuyên chung"; every behaviour / illustration line is minh họa tied to one claim of its paragraph', () => {
  for (const f of [REF, ...sample.slice(0, 60)]) for (const c of luanReport(f, K, { allowDraft: true, deep: true }) as unknown as Array<{ paragraphs: Array<{ sentences: S[] }> }>) for (const p of c.paragraphs) for (const s of p.sentences) {
    if (/^advice:/.test(s.trace.step ?? '')) assert.equal(s.trace.basis, 'loi_khuyen', s.text);
    if (/^(behave|minh_hoa):/.test(s.trace.step ?? '')) {
      assert.equal(s.trace.basis, 'minh_hoa', s.text);
      assert.equal(p.sentences.filter(x => x.trace.step === s.trace.tied).length, 1, s.text);
    }
  }
});
