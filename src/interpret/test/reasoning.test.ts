// Unit tests of the reasoning primitives the audit corrected: counterfactual necessity of cross-palace links, condition rendering,
// citation merging, the 'narrower case' relation, and the timing lean.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { run } from '../engine.ts';
import { ChartGraph } from '../graph.ts';
import { Lexicon, annotate, condText, splitReading, type CondParts } from '../semantic.ts';
import { mergeCites } from '../planner.ts';
import { interpret, CHAPTERS } from '../pipeline.ts';
import { loadCorpus } from '../../../tools/interpret/sweep.ts';
import type { Knowledge } from '../types.ts';

const K: Knowledge = JSON.parse(readFileSync(new URL('../generated/knowledge.json', import.meta.url), 'utf8'));
const REF = JSON.parse(readFileSync(new URL('./fixtures/charts.json', import.meta.url), 'utf8'))[0];

test('cross-palace dependencies are tested counterfactually, not read off the condition', () => {
  const res = run(K.rules, K.sources, REF.facts.base);
  const ev = annotate(res.findings, K, new Lexicon(K), REF.facts.base);
  const g = new ChartGraph(REF.facts, ev);
  const deps = (rule: string) => g.crossDependencies(ev.find(e => e.rule.id === rule)!.finding.id);
  // 'Hóa Quyền gặp Tử, Phủ' at Mệnh: Thiên Phủ is in Mệnh itself, so Tử Vi in Quan Lộc is a second satisfying branch, not a need
  assert.deepEqual(deps('TV_TH_AUX_MENH_HQ_TU_PHU').map(d => [d.star, d.palace, d.necessary]), [['Tử Vi', 'Quan Lộc', false]]);
  // 'Vũ Khúc được Lộc, Mã hợp chiếu': both Lộc Tồn and Thiên Mã are in Tài Bạch and each is needed
  assert.deepEqual(deps('TV_KL_PHU_VU_LOC_MA').map(d => [d.star, d.palace, d.necessary]).sort(), [['Lộc Tồn', 'Tài Bạch', true], ['Thiên Mã', 'Tài Bạch', true]]);
});

test('conditions render relative to the palace a paragraph already names; brightness branch lists read as brightness', () => {
  const c: CondParts = { palace: 'Quan Lộc', own: ['Thiên Tướng', 'Địa Kiếp'], hoa: [], opp: [], tp: [], nb: [], dig: {}, branch: null, tt: [], extra: [] };
  assert.equal(condText(c), 'Thiên Tướng và Địa Kiếp tại Quan Lộc');
  assert.equal(condText(c, 'Quan Lộc'), 'có Thiên Tướng và Địa Kiếp trong cung');
  const ham: CondParts = { ...c, own: ['Địa Kiếp'], branch: { branch: 'Thìn', kind: 'ham' } };
  assert.equal(condText(ham, 'Quan Lộc'), 'có Địa Kiếp hãm địa ở Thìn');
  assert.equal(condText({ ...c, own: ['Tử Vi'], tp: ['Lộc Tồn'] }, 'Quan Lộc'), 'có Tử Vi trong cung, Lộc Tồn hội chiếu về');
  // one order for the same stars, so equal conditions read equal and can be merged
  assert.equal(condText({ ...c, own: ['Thiên Mã', 'Lộc Tồn'] }), condText({ ...c, own: ['Lộc Tồn', 'Thiên Mã'] }));
});

test('editorial notes after ";" never reach a quoted reading', () => {
  assert.equal(splitReading('nói khéo, hát hay, thích ca múa; hai sao sau chưa có trong hệ thống (Thiếu Âm ở Mệnh) [TH p.60]').core, 'nói khéo, hát hay, thích ca múa');
  assert.equal(splitReading("Đào Hồng đối mặt: công danh sớm ; sách nói xác suất 'khá tốt', không phải chắc chắn [KL pp.225-227]").core, 'công danh sớm');
});

test('citations of one book are merged', () => {
  assert.equal(mergeCites(['Thực Hành tr.29–30', 'Thực Hành tr.44', 'Toàn Thư tr.78–80']), 'Thực Hành tr.29–30, 44; Toàn Thư tr.78–80');
});

test('a timing lean exists only when a side stands on this chart\'s stars; "nghiêng về" never appears without it', () => {
  let leans = 0, genericOnly = 0;
  for (const c of loadCorpus()) for (const ch of CHAPTERS) {
    const o = interpret(c.facts, ch, K);
    if (o.argument.timing.lean) leans++;
    if (o.argument.timing.leanReason === 'generic_only') { genericOnly++; assert.equal(o.argument.timing.lean, null); }
    if (/nghiêng về/.test(o.text)) assert.ok(o.argument.timing.lean, `${c.label} ${ch}`);
  }
  assert.ok(leans > 0 && genericOnly > 0, `leans ${leans}, generic-only ${genericOnly}`);   // both branches are exercised by the corpus
});

test('a narrower limiting condition that differs only by sát stars is a degree adjustment; a narrower case (branch) is read first', () => {
  const corpus = loadCorpus();
  const rels = corpus.flatMap((c: any) => interpret(c.facts, 'cong_danh', K).argument.dominance.map(d => d.relation));
  assert.ok(rels.includes('sat_qualifier') && rels.includes('specific_qualifier'), rels.join(','));
  // Nhật Nguyệt đồng cung: 'đường công danh không thông' (at Sửu/Mùi) is the narrower case of 'giàu sang như đã có sẵn'
  const nn = corpus.find((c: any) => c.label.includes('ql_major:Thái Dương,ql_major:Thái Âm'));
  const d = interpret(nn.facts, 'cong_danh', K).argument.dominance.find(x => x.qualifier === 'đường công danh không thông');
  assert.equal(d?.relation, 'specific_qualifier');
});
