// Bát Tự report-wide checks (audit 2026-10-22, S2 steps 3-5). Over benchmark20, the owner's chart (09/01/2002), the 1990 chart and the
// 1,000-chart corpus, the Bát Tự reading as the reader gets it (checked readings only):
//   - one verdict per đại vận: the same luck pillar is never told with two verdicts (đại vận paragraph vs the closing), and a paragraph that
//     holds both a good and a bad finding ends on the verdict that reconciles them (no bare "vận xấu");
//   - no duplicate sentence, no unsupported claim (a book sentence names a verified rule; a computed one names its table), no empty chapter,
//     no phổ thông sentence, no method word, no seven-level strength label, no misattributed điều hậu need;
//   - the cách chapter follows the frame (cấu trúc → hỗ trợ/hạn chế → tương tác → mâu thuẫn → kết luận; sources in the trace);
//   - the TypeScript fallback (`reconcileTs`, for facts older than the Python layer) gives the Python verdict wherever both exist.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { proseBazi } from '../prose/bazi.ts';
import { checkedOnly } from '../prose/checked.ts';
import { seedOf } from '../prose/chapter.ts';
import { classOf, dhRoleOf, reconcileTs, goodYearsTs, type BaziDeep, type Reconcile } from '../prose/bazi_deep.ts';
import type { ProseParagraph } from '../prose/realize.ts';
import type { ChartInput, Knowledge } from '../types.ts';

// the readability gate's method words (readable.test.ts METHOD; copied, importing that file would run its tests here)
const METHOD = /nguồn(?! (?:thu|lợi|tiền)\b)|quy tắc|đối chiếu|phạm vi|hệ thống|trọng số|cách hiểu|chưa có lời/iu;
const FX = new URL('./fixtures/', import.meta.url);
const K: Knowledge = JSON.parse(readFileSync(new URL('../generated/knowledge.json', import.meta.url), 'utf8'));
const read = (f: string) => JSON.parse(readFileSync(new URL(f, FX), 'utf8'));
const bench = (read('benchmark20.json') as Array<{ label: string; facts: ChartInput }>).map(b => [b.label, b.facts] as const);
const owner: ChartInput = read('ref_2002_01_09_kl.json'), user1990: ChartInput = read('user_1990_nam.json');
const charts: Array<readonly [string, ChartInput]> = [['ref_2002', owner], ['user_1990', user1990], ...bench];
const corpusUrl = new URL('corpus1000.json.gz', FX);
const corpus = (): Array<readonly [string, ChartInput]> => existsSync(corpusUrl)
  ? (JSON.parse(gunzipSync(readFileSync(corpusUrl)).toString('utf8')) as Array<{ label: string; facts: ChartInput }>).map(c => [c.label, c.facts] as const) : [];

type Ch = Partial<Record<string, ProseParagraph[]>>;
const reader = (f: ChartInput) => checkedOnly(proseBazi(f, K, seedOf(f), 'test', true) as Parameters<typeof checkedOnly>[0]) as ReturnType<typeof proseBazi>;
const sentences = (ch: Ch) => Object.values(ch).flat().flatMap(p => p!.sentences);
type V = { verdict?: string; verdicts?: Array<[string, string]> };

/** the problems the report-wide rules find in one reading */
export function baziProblems(label: string, f: ChartInput): string[] {
  const o = reader(f), ch = o.chapters as Ch, bad: string[] = [];
  const D = (f.bazi as { deep?: BaziDeep | null } | undefined)?.deep;
  // 1. one verdict per luck pillar across the report
  const byLuck = new Map<string, Set<string>>();
  for (const p of ch['dai-van'] ?? []) {
    const name = p.sentences[0].text.match(/đại vận (\S+ \S+)/)?.[1];
    const v = p.sentences.map(s => (s.trace as V).verdict).find(Boolean);
    if (name && v) (byLuck.get(name) ?? byLuck.set(name, new Set()).get(name)!).add(v);
    // a paragraph holding a good and a bad finding ends on its verdict
    const tones = new Set(p.sentences.map(s => s.trace.tone));
    if (name && tones.has('neg') && tones.has('pos') && !(p.sentences.at(-1)!.trace.step ?? '').startsWith('verdict:'))
      bad.push(`${label}: ${name}: good and bad findings with no verdict after them`);
    // no bare bad verdict: a paragraph whose cách side is bad ends on an answer (a turn, what to do) or a conditional verdict
    if (name && v === 'nang' && p.sentences.at(-1)!.trace.tone !== 'answer') bad.push(`${label}: ${name}: bare bad verdict`);
  }
  for (const s of sentences({ 'tong-ket': ch['tong-ket'] })) for (const [name, v] of (s.trace as V).verdicts ?? [])
    (byLuck.get(name) ?? byLuck.set(name, new Set()).get(name)!).add(v);
  for (const [name, vs] of byLuck) if (vs.size > 1) bad.push(`${label}: ${name} told as ${[...vs].join(' and ')}`);
  // the closing's own words follow the same classes: a luck in the "vận nặng" list is not called good anywhere
  // 2. text-level rules
  const all = sentences(ch), seen = new Set<string>();
  for (const s of all) {
    if (seen.has(s.text)) bad.push(`${label}: duplicate: ${s.text}`);
    seen.add(s.text);
    if (s.trace.basis === 'pho_thong') bad.push(`${label}: phổ thông: ${s.text}`);
    if (s.trace.basis === 'sach' && !s.trace.rules.some(id => o.evidence.rules[id]?.verified)) bad.push(`${label}: book sentence without a verified rule: ${s.text}`);
    if (s.trace.basis === 'tinh_toan' && !s.trace.cites.length && !s.trace.rules.length) bad.push(`${label}: computed sentence without its table: ${s.text}`);
    if (METHOD.test(s.text)) bad.push(`${label}: method word: ${s.text}`);
    if (/cực nhược|cực vượng|thiên nhược|thiên vượng|trung hòa|sát ngưỡng vượng nhược/.test(s.text)) bad.push(`${label}: seven-level label: ${s.text}`);
    if (/bảng điều hậu[^.]*cần (Hỏa|Thủy|Mộc|Kim|Thổ)|theo bảng điều hậu, lá số cần/.test(s.text)) bad.push(`${label}: điều hậu table named as the source of an element: ${s.text}`);
    if (/phù ức|sinh phù cho thân|thân nhược nên cần/.test(s.text)) bad.push(`${label}: phù ức reasoning in the text: ${s.text}`);
  }
  // 3. a stem the điều hậu cell does not name is never called the one the chart needs
  if (D?.dieu_hau?.verified) {
    const table = D.dieu_hau.table ?? D.dieu_hau.stems.map(x => x.stem);
    for (const s of all) {
      const m = s.text.match(/can (\S+) (chính là|là một) can điều hậu/);
      if (m && !table.includes(m[1])) bad.push(`${label}: ${m[1]} called a điều hậu stem, the cell names ${table.join(', ')}`);
    }
  }
  // 4. no empty chapter; the structure chapters exist when the analysis does
  for (const [id, ps] of Object.entries(ch)) if (!ps?.length || ps.some(p => !p.sentences.length)) bad.push(`${label}: empty ${id}`);
  if (D?.luck?.length) for (const id of ['nhat-chu', 'dai-van', 'cach-cuc', 'tong-ket']) if (!ch[id]?.length) bad.push(`${label}: missing ${id}`);
  // 5. the cách chapter's frame order
  const order = ['cau_truc', 'ho_tro', 'tuong_tac', 'mau_thuan', 'ket_luan'];
  const parts = (ch['cach-cuc'] ?? []).map(p => (p as ProseParagraph & { part?: string }).part).filter(Boolean) as string[];
  if (parts.some((x, i) => i && order.indexOf(x) < order.indexOf(parts[i - 1]))) bad.push(`${label}: cách parts out of order: ${parts}`);
  return bad;
}

test('report-wide rules hold on benchmark20, the owner chart and the 1990 chart', () => {
  const bad = charts.flatMap(([l, f]) => baziProblems(l, f));
  assert.deepEqual(bad.slice(0, 8), [], `${bad.length} problems`);
});

test('report-wide rules hold on the 1,000-chart corpus (facts from before the Python layer: the TS fallback decides)', { skip: !existsSync(corpusUrl) && 'corpus not built' }, () => {
  const cs = corpus();
  let luck = 0;
  const bad: string[] = [];
  for (const [l, f] of cs) {
    bad.push(...baziProblems(l, f));
    luck += (reader(f).chapters['dai-van'] ?? []).length;
  }
  console.log(`# corpus1000: ${cs.length} charts, ${luck} đại vận paragraphs, ${bad.length} problems`);
  assert.deepEqual(bad.slice(0, 8), [], `${bad.length} problems`);
});

test('owner chart (09/01/2002): the findings of the audit are gone', () => {
  const o = reader(owner), ch = o.chapters as Ch;
  const dv = (ch['dai-van'] ?? []).map(p => p.text), tk = (ch['tong-ket'] ?? []).map(p => p.text).join(' ');
  const luck = (name: string) => dv.find(t => t.toLowerCase().includes(`đại vận ${name.toLowerCase()}`) && /tuổi thực \(\d{4}–/.test(t)) ?? '';
  // Canh Tý: no longer "vận xấu" then "khá thuận" with nothing between: the two tables are said to differ, the verdict is conditional, and
  // the closing says the same
  assert.ok(/vênh nhau|không trùng nhau/.test(luck('Canh Tý')) && /thuận hay nặng tùy lúc có nhóm Tỉ Kiếp/.test(luck('Canh Tý')), luck('Canh Tý'));
  assert.ok(!/khá thuận/.test(luck('Canh Tý')));
  assert.match(tk, /Canh Tý \(từ 1 tuổi thực\) thuận hay nặng tùy lúc có nhóm Tỉ Kiếp/);
  // Mậu Tuất and Kỷ Hợi: the turn (what the branch still holds) and the years to lean on
  assert.match(luck('Mậu Tuất'), /chi Tuất còn tàng Đinh \(Tỉ Kiên\)[^.]*\. [^.]*những năm nên tiến là 2025 \(Ất Tỵ\) và 2026 \(Bính Ngọ\)/);
  assert.match(luck('Kỷ Hợi'), /chi Hợi còn tàng Giáp \(Chính Ấn\), can điều hậu đứng đầu/);
  assert.match(tk, /Kỷ Hợi \(từ 11 tuổi thực\) và Mậu Tuất \(từ 21 tuổi thực\) là những vận nặng/);
  // "theo bảng điều hậu lá số cần Hỏa": the frame names the table's stems; Hỏa is the Trích Thiên Tủy rule's
  const nc = (ch['nhat-chu'] ?? []).map(p => p.text).join(' ');
  assert.match(nc, /về điều hậu, can nên có là Giáp và Canh/);
  assert.ok(!/bảng điều hậu, lá số cần Hỏa/.test(nc));
  // luck_role.yong only for the stem the cell names: Ất is not "the element the chart needs"; Giáp is the cell's chính stem
  assert.ok(!/can Ất (chính là|là một) can điều hậu|Ất đúng là hành lá số cần/.test(dv.join(' ')));
  assert.match(luck('Giáp Ngọ'), /can Giáp chính là can điều hậu đứng đầu/);
  // the cái đầu rule no longer fires on Ất Mùi (its premise was the group-based role)
  assert.ok(!/thế cái đầu/.test(luck('Ất Mùi')), luck('Ất Mùi'));
  // the cách chapter explains the two tables and how far each goes, then concludes conditionally
  const cc = (ch['cach-cuc'] ?? []).map(p => p.text).join(' ');
  assert.match(cc, /Hai phía xét hai việc khác nhau/);
  // how far each table goes (the điều hậu table's origin, TVH p.388) is in the sentence note, not in the text (2026-10-22 readability)
  assert.ok((ch['cach-cuc'] ?? []).flatMap(p => p.sentences).some(s => /chưa rõ xuất xứ/.test(s.trace.note ?? '')));
  assert.ok(!/Thiệu Vĩ Hoa|Trích Thiên Tủy|Bát Tự Chân Tông/.test(cc));
  // 2026 (Bính Ngọ) is one of the years the đại vận names to lean on, and the lưu niên agrees
  assert.match((ch['luu-nien'] ?? [])[0]?.text ?? '', /Bính Ngọ[^]*cùng thuận|Bính Ngọ[^]*đều thuận/);
});

test('the TS fallback gives the Python verdict wherever the facts carry both', () => {
  let n = 0;
  for (const [l, f] of charts) {
    const D = (f.bazi as { deep?: BaziDeep | null } | undefined)?.deep;
    if (!D) continue;
    const fired = new Set(D.verified.map(v => v.rule_id));
    const needEl = fired.has('BT_TTT_HANNOAN_CAN_NOAN') ? 'Hỏa' : fired.has('BT_TTT_HANNOAN_CAN_HAN') ? 'Thủy' : '';
    const table = D.dieu_hau.verified ? (D.dieu_hau.table ?? D.dieu_hau.stems.map(x => x.stem)) : [];
    const ok = D.cach_tvh?.status === 'ap_dung' && !!D.cach_tvh.cach;
    const [yong, tot, xau] = ok ? [D.cach_tvh!.yong, D.cach_tvh!.van_tot, D.cach_tvh!.van_xau] : [[], [], []];
    for (const t of [...D.luck, ...(D.years ?? [])]) {
      if (!t.reconcile) continue;
      const ts = reconcileTs({ ...t, reconcile: undefined }, f.bazi!.day_master, table, needEl, yong, xau);
      const py: Reconcile = t.reconcile;
      assert.deepEqual({ ...ts, support: ts.support ?? [] }, { ...py, support: py.support ?? [] }, `${l} ${'pillar' in t ? t.pillar : ''}`);
      assert.equal(classOf(ts), classOf(py));
      n++;
    }
    for (const l2 of D.luck) if (ok && l2.good_years && l2.first_year != null)
      assert.deepEqual(goodYearsTs(l2.first_year, f.bazi!.day_master, table, tot, xau, needEl, l2.pillar), l2.good_years, `${l} ${l2.pillar}`);
    for (const t of D.luck) if (t.stem) assert.equal(dhRoleOf(t.stem, table), (t as { dieu_hau: { stem: string | null } }).dieu_hau.stem ?? null, `${l} ${t.pillar}`);
  }
  assert.ok(n > 100, `${n} pillars compared`);
});

// Owner review 2026-10-22, on the owner's chart (09/01/2002 04:30 nam): five correctness points, each at its root.
test('owner review 2026-10-22: one cách status, Tài in three layers, year × đại vận, every sentence with its basis, one age convention', () => {
  const o = reader(owner), ch = o.chapters as Ch, all = sentences(ch);
  const D = (owner.bazi as { deep?: BaziDeep | null }).deep!;
  // 1. the cách is "xác lập một phần" everywhere: said once in the cách chapter, and every luck / year verdict drawn from it is conditional
  assert.equal((D.cach_tvh as { verification?: string }).verification, 'partial');
  assert.ok((ch['cach-cuc'] ?? []).flatMap(p => p.sentences).some(s => s.trace.step === 'cach:status' && /xác lập (được )?một phần/.test(s.text)));
  const luckShort = (ch['dai-van'] ?? []).filter(p => p.depth !== 'sau' && p.sentences.some(s => (s.trace.step ?? '').startsWith('luck:')));
  for (const p of luckShort) {
    const cachSide = p.sentences.find(s => /vận (tốt|xấu)/.test(s.text) && s.trace.basis === 'tinh_toan');
    if (cachSide) assert.match(cachSide.text, /cách Thiên Tài[^.]*đứng được|đứng được[^.]*cách Thiên Tài/, cachSide.text);
    const v = p.sentences.find(s => (s.trace.step ?? '').startsWith('verdict:'));
    if (v) assert.equal(v.trace.conditional, 'cach_partial', v.text);
  }
  assert.ok((ch['tong-ket'] ?? []).flatMap(p => p.sentences).some(s => s.trace.conditional === 'cach_partial'));
  // 2. Tài (DEEP-BAZI-2): the manual's own condition decides first (八字真宗 p.50 断语条件 2: Tài strong but not flowing into the day master ->
  // tài vận bình thường), with why (the three places next to the day master hold no Ấn); then the day master's strength and the cách; and
  // the two books meet (no open tension left on this chart)
  const tai = (ch['su-nghiep'] ?? []).flatMap(p => p.sentences);
  for (const step of ['kin:tai', 'kin:flow', 'tai:dm', 'tai:method', 'tai:decide']) assert.ok(tai.some(s => s.trace.step === step), step);
  assert.match(tai.find(s => s.trace.step === 'kin:tai')!.text, /chưa (chảy|có đường chảy)[^.]*nhật chủ[^.]*bình thường/);
  assert.match(tai.find(s => s.trace.step === 'tai:decide')!.text, /gặp nhau/);
  // no unqualified "tài vận tốt" anywhere: every one carries its condition (trace.conditional) or is a quote
  for (const s of all) for (const m of s.text.matchAll(/tài vận tốt/g))
    assert.ok((s.text[m.index! - 1] === '“' && s.text[m.index! + m[0].length] === '”') || ['tai_flow', 'tai_position_only'].includes(s.trace.conditional ?? ''), s.text);
  const zz = tai.find(s => s.trace.rules[0] === 'BT_ZZK_W10R');
  assert.ok(zz && zz.trace.rules.includes('BT_ZZK_W24') && zz.trace.conditional === 'tai_flow', zz?.text);
  // the work field is read at the pillar left of the Quan pillar (p.52 #6-7, p.53 examples): the hour stem Nhâm is the Quan, so the day pillar
  assert.ok(tai.some(s => s.trace.step === 'kin:work_field' && /trụ ngày Đinh Sửu/.test(s.text)));
  // 3. 2027 (Đinh Mùi) is not among the Mậu Tuất years to press on: its own verdict is mixed and its branch meets the luck branch Tuất
  const mt = D.luck.find(l => l.pillar === 'Mậu Tuất')!;
  assert.ok(!(mt.good_years ?? []).some(g => g.year === 2027));
  for (const l of D.luck) for (const g of l.good_years ?? []) assert.ok(['thuan', 'kha_thuan'].includes(g.verdict ?? ''), `${l.pillar} ${g.year}`);
  const y27 = (ch['luu-nien'] ?? []).find(p => /Năm 2027|năm 2027/.test(p.sentences[0].text) && p.depth !== 'sau')!;
  assert.ok(y27.sentences.some(s => /đại vận Mậu Tuất, năm 2027 có[^.]*chi Mùi hình và phá chi Tuất của vận/.test(s.text)), y27.text);
  assert.ok(!/những năm nên tiến[^.]*2027/.test((ch['dai-van'] ?? []).map(p => p.text).join(' ')));
  // 4. every sentence carries its basis (the report's "Phạm vi kiểm chứng" lists them all, report.js btLedgerHtml)
  for (const s of all) assert.ok(['sach', 'tinh_toan', 'he_thong', 'minh_hoa'].includes(s.trace.basis), s.text);
  for (const s of all.filter(x => x.trace.basis === 'minh_hoa')) assert.ok(all.some(t => t.trace.step === s.trace.attach && t !== s), s.text);
  // 5. one age convention on the Bát Tự surface, named at every age: tuổi thực
  for (const s of all) assert.ok(!/\d+ tuổi(?! thực)/.test(s.text), s.text);
});
