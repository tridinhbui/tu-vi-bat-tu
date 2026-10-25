// Synthesis layer (plan quirky-tinkering-rabin steps 3–5, S1): palace evidence, the guards on the palace plans, the report-wide domain ledger,
// the luận chapters' frame and the vận hạn link to the natal reading.
//   - the owner's regression chart (09/01/2002 04:30 nam, Khảo Luận dignity), checked against the tuvi.vn board first: Phu Thê names Cơ–Âm
//     vượng, Văn Xương hóa Kỵ, Đà La and Tuần and concludes conditionally; Quan Lộc (vô chính diệu, Thân cư) reads the borrowed Cơ–Âm, Thân
//     and its tam hợp and concludes from no single star; Mệnh and Quan Lộc agree on career; Tài Bạch has three parts;
//   - metamorphic: adding or removing Hóa Kỵ, Đà La or Tuần in Phu Thê changes the conclusion;
//   - report-wide: one domain never gets two conclusions, and opposite readings of a domain always come with an explaining conclusion;
//   - every limiting element of a palace is faced; no unsupported, duplicated or empty chapter; the đại hạn closing agrees with the index level.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import type { ChartInput, Knowledge } from '../types.ts';
import { luanReport, type LuanChapter } from '../prose/luan.ts';
import { infer, type ProseChapter } from '../prose/chapter.ts';
import { proseVanHan } from '../prose/vanhan.ts';
import { proseAllChapters } from '../route.ts';
import { checkedOnly } from '../prose/checked.ts';
import { palaceEvidence, readsElement } from '../reason/evidence.ts';
import { buildLedger } from '../reason/ledger.ts';
import { reasonPalace } from '../reason/plan.ts';
import { computeIndices, type IndexNorms } from '../indices.ts';
import norms from '../../../engine/data/kg/index_norms.json' with { type: 'json' };
import type { ProseParagraph, ProseSentence } from '../prose/realize.ts';

const FX = join(import.meta.dirname, 'fixtures');
const ROOT = join(import.meta.dirname, '..', '..', '..');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const REF: ChartInput = JSON.parse(readFileSync(join(FX, 'ref_2002_01_09_kl.json'), 'utf8'));
const BOARD = JSON.parse(readFileSync(join(ROOT, 'engine', 'tests', 'reference_charts', '2002-01-09_0430_nam.json'), 'utf8'));
const bench = JSON.parse(readFileSync(join(FX, 'benchmark20.json'), 'utf8')) as Array<{ label: string; facts: ChartInput }>;
const META = JSON.parse(readFileSync(join(FX, 'phu_the_metamorphic.json'), 'utf8')) as Array<{ name: string; element: string | null; change: string | null; facts: ChartInput }>;
const corpus = JSON.parse(gunzipSync(readFileSync(join(FX, 'corpus1000.json.gz'))).toString()) as Array<{ facts: ChartInput }>;
const cmap = new Map(K.concepts.concepts.map(c => [c.id, c]));

const report = (f: ChartInput) => luanReport(f, K, { allowDraft: true, deep: true });
const sentences = (c: { paragraphs: ProseParagraph[] }) => c.paragraphs.flatMap(p => p.sentences);
const R2002 = report(REF);
const ch = (id: string) => R2002.find(c => c.chapter === id)! as LuanChapter;
const conclusions = (c: ProseChapter, domain: string) => sentences(c).filter(s => s.trace.ledger?.domain === domain);

test('fixture ref_2002_01_09_kl matches the tuvi.vn board on every cell the readings below use', () => {
  const byBranch = new Map(REF.palaces.map(p => [p.branch, p]));
  for (const br of ['Thân', 'Dần', 'Tuất', 'Ngọ', 'Tỵ']) {
    const b = BOARD.palaces[br], p = byBranch.get(br)!;
    assert.equal(p.name, b.name, br);
    assert.deepEqual([...p.major_stars].sort(), Object.keys(b.majors).sort(), `${br} chính tinh`);
    for (const s of b.stars) assert.ok(p.stars.includes(BOARD.aliases[s] ?? s), `${br}: ${s}`);
    assert.equal(!!p.tuan, !!b.tuan, `${br} Tuần`); assert.equal(!!p.triet, !!b.triet, `${br} Triệt`);
  }
  const L = { M: 'miếu', V: 'vượng', 'Đ': 'đắc', H: 'hãm' } as Record<string, string>;
  for (const [s, d] of Object.entries(BOARD.palaces['Thân'].majors as Record<string, string>)) assert.equal(byBranch.get('Thân')!.major_dignity[s], L[d], `Phu Thê ${s}`);
  assert.equal(byBranch.get('Tuất')!.major_dignity['Cự Môn'], 'hãm');
  assert.ok(byBranch.get('Dần')!.is_than && BOARD.palaces['Dần'].than, 'Thân cư Quan Lộc');
  for (const [h, star] of Object.entries(BOARD.hoa.natal as Record<string, string>)) {
    assert.equal(REF.tu_hoa[h].star, star, h);
    assert.equal(REF.palaces.find(p => p.branch_index === REF.tu_hoa[h].branch)!.branch, BOARD.hoa.natal_branch[h], `${h} branch`);
  }
});

test('evidence: every palace; a VCD palace borrows the opposite chính tinh, labelled; Tứ Hóa bound to its star; limits by role', () => {
  const { resolved } = infer(REF, K);
  const ev = Object.fromEntries(REF.palaces.map(p => [p.name, palaceEvidence(REF, K, p.name, { resolved })]));
  assert.equal(Object.keys(ev).length, 12);
  const ql = ev['Quan Lộc'];
  assert.ok(ql.vcd && ql.than && ql.majors.every(m => m.borrowed && m.palace === 'Phu Thê'), 'Quan Lộc borrows Cơ–Âm');
  assert.deepEqual(ql.majors.map(m => `${m.star}:${m.dignity}`).sort(), ['Thiên Cơ:vượng', 'Thái Âm:vượng']);
  assert.ok(ql.tamPhuong.some(m => m.star === 'Thái Dương' && m.hoa.includes('Hóa Quyền')), 'tam hợp Thái Dương hóa Quyền');
  const pt = ev['Phu Thê'];
  assert.deepEqual(pt.limit.map(e => e.id).sort(), ['hoa:Hóa Kỵ', 'sat:Đà La', 'tt:Tuần']);
  assert.ok(pt.mixed.some(e => e.kind === 'ky_carrier' && e.star === 'Văn Xương'), 'Văn Xương carries Kỵ: mixed, never support');
  assert.ok(!pt.support.some(e => e.star === 'Văn Xương'));
  assert.ok(pt.hoa.some(h => h.hoa === 'Hóa Kỵ' && h.star === 'Văn Xương' && h.where === 'self'));
  assert.ok(pt.rules.some(r => r.ruleId === 'TV_KL_CUNG_PHU_THE_TT' && r.timing), 'rel.timing facet kept');
  assert.ok(ev['Mệnh'].majors.some(m => m.star === 'Cự Môn' && m.role === 'mixed'), 'Cự Môn hãm hóa Lộc is mixed');
});

test('2002 Phu Thê: Cơ–Âm vượng, Văn Xương hóa Kỵ, Đà La and Tuần are named; harmony and strain are left unresolved, with the limits named', () => {
  const c = ch('phu_the');
  assert.ok(c.luan && c.pass, JSON.stringify(c.issues));
  const text = c.text;
  for (const x of ['Thiên Cơ (Vượng Địa)', 'Thái Âm (Vượng Địa)', 'Văn Xương', 'Đà La', 'Tuần']) assert.ok(text.includes(x), x);
  assert.match(text, /Văn Xương (hóa Kỵ|lại mang Hóa Kỵ|ở đây mang Hóa Kỵ)/);
  // the limits are faced by readings or caveats in the reading paragraphs, not only by the frame
  const body = c.paragraphs.slice(1).map(p => p.text).join(' ');
  for (const x of ['Đà La', 'Tuần', 'Hóa Kỵ']) assert.ok(body.includes(x), `${x} faced in the reading`);
  const end = conclusions(c, 'hon_nhan');
  // no book sentence decides between sự hòa hợp and sự trắc trở, and Tuần's timing reading no longer ties them (owner review 2026-10-22);
  // the system's scale weighs them (Thái Âm vượng, a chính tinh, against Đà La) and says so as its own tổng hợp (owner decision 2026-10-23)
  // since Tử Vi Hàm Số (2026-10-25 merge) the palace holds two more strain readings (Hóa Kỵ ở Phu Thê: hay cãi vã, HS p.169; Tuần: trắc trở,
  // HS p.227) and two more harmony ones (Quang Quý, HS p.147; Cơ Nguyệt ở Dần Thân, HS p.119): the scale no longer separates the sides, so
  // both are named and left unresolved
  assert.ok(end.length && end.every(s => ['nghieng_ve', 'chua_phan_xu'].includes(s.trace.ledger!.verdict)), end.map(s => s.text).join(' | '));
  assert.ok(end.some(s => /sự hòa hợp/.test(s.text) && /sự trắc trở/.test(s.text)), 'both sides named');
  if (end.some(s => s.trace.ledger!.verdict === 'nghieng_ve')) assert.ok(end.some(s => s.trace.step === 'ledger:hon_nhan:weigh'), 'the reason the heavier side weighs more');
  assert.ok(end.some(s => /Đà La/.test(s.text) && /Tuần/.test(s.text)), 'the limits of the palace are named with the conclusion');
  assert.ok(end.some(s => s.trace.part === 5));
  // Văn Xương carries Kỵ: every strength resting on it is followed by its caveat
  const ss = sentences(c);
  ss.forEach((s, i) => { if (s.trace.basis === 'sach' && s.text.includes('Văn Xương') && cmap.get(s.trace.concepts[0])?.pol === '+')
    assert.ok(ss.slice(0, i + 4).some(x => (x.trace.confront ?? []).includes('hoa:Hóa Kỵ')), s.text); });
});

test('2002 Quan Lộc: borrowed Cơ–Âm, Thân cư and tam hợp; no conclusion from one star; it agrees with Mệnh on career', () => {
  const c = ch('cong_danh');
  assert.ok(c.luan && c.pass, 'Quan Lộc is a luận chapter');
  assert.match(c.paragraphs[0].text, /vô chính diệu/);
  for (const x of ['Thiên Cơ (Vượng Địa)', 'Thái Âm (Vượng Địa)', 'Thái Dương']) assert.ok(c.paragraphs[0].text.includes(x), x);
  assert.match(c.text, /Thân cư Quan Lộc/);
  const plan = reasonPalace(REF, K, 'Quan Lộc', infer(REF, K));
  for (const t of plan.theses) for (const cl of t.claims.filter(x => x.single)) {
    const at = sentences(c).findIndex(s => s.trace.step === `claim:${t.id}:${cl.concept}`);
    // its caveat, or another palace saying the same on other stars (luan.ts caveats(): such a corroboration makes it more than one star's)
    if (at >= 0) assert.ok(sentences(c).slice(at, at + 4).some(s => s.trace.step?.startsWith('single:') || (s.trace.step?.startsWith('corroborated:') && s.trace.concepts.includes(cl.concept))),
      `one-star claim ${cl.concept} has its caveat`);
  }
  const L = buildLedger(REF, K, infer(REF, K).resolved).domains.find(d => d.id === 'cong_danh')!;
  assert.notEqual(L.verdict, 'thuan');
  assert.ok(L.pos.length + L.neg.length >= 2, 'career rests on more than one reading');
  const q = conclusions(c, 'cong_danh'), m = conclusions(ch('menh'), 'cong_danh');
  assert.ok(q.length && m.length, 'both chapters conclude on career');
  assert.deepEqual(new Set([...q, ...m].map(s => s.trace.ledger!.verdict)), new Set([L.verdict]));
});

test('2002 Tài Bạch: earning, managing and accumulating, each with its own conclusion', () => {
  const c = ch('tai_bach');
  const topics = c.paragraphs.map(p => p.topic);
  for (const t of ['tai_kiem', 'tai_giu', 'tai_tich']) assert.ok(topics.includes(t), `${t}: ${topics.join(',')}`);
  for (const part of ['kiem', 'giu', 'tich_luy']) assert.ok(conclusions(c, `tai_loc.${part}`).length, part);
});

test('metamorphic: adding or removing Hóa Kỵ, Đà La or Tuần in Phu Thê changes the conclusion', () => {
  const concl = (f: ChartInput) => {
    const c = report(f).find(x => x.chapter === 'phu_the')!;
    const L = buildLedger(f, K, infer(f, K).resolved).domains.find(d => d.id === 'hon_nhan')!;
    return { text: conclusions(c, 'hon_nhan').map(s => s.text).join(' '), limits: L.limits.map(l => l.id).sort(), L };
  };
  const by = Object.fromEntries(META.map(v => [v.name, concl(v.facts)]));
  assert.deepEqual(by.base.limits, ['cat:Văn Xương', 'hoa:Hóa Kỵ', 'sat:Đà La', 'tt:Tuần']);
  const ID: Record<string, string> = { 'Hóa Kỵ': 'hoa:Hóa Kỵ', 'Đà La': 'sat:Đà La', 'Tuần': 'tt:Tuần' };
  for (const v of META.filter(x => x.element)) {
    const ref = v.change === 'remove' ? by.base : by.clean, got = by[v.name];
    assert.notEqual(got.text, ref.text, `${v.name}: the conclusion must change`);
    assert.equal(got.limits.includes(ID[v.element!]), v.change === 'add', `${v.name}: ${got.limits}`);
  }
  assert.ok(by.clean.limits.length === 0 && by.base.L.neg.length > 0 && by.clean.L.neg.length === 0, 'with no limit, no strain reading');
});

/** The report-wide contradiction check: a domain concluded twice with different verdicts, or opposite book readings of a domain voiced in two
 *  chapters with no conclusion that explains them (có điều kiện / hai chiều / trở ngại). */
const DOMAIN = (facet: string) => facet.startsWith('career.') && !facet.endsWith('.timing') ? 'cong_danh' : facet.startsWith('finance.') ? 'tai_loc'
  : facet === 'relationships.marriage' ? 'hon_nhan' : facet.startsWith('wellbeing.') ? 'suc_khoe' : null;
export function contradictions(chs: Array<{ chapter: string; paragraphs: ProseParagraph[] }>): string[] {
  const out: string[] = [], verdict = new Map<string, string>(), explained = new Set<string>(), sides = new Map<string, Map<string, Set<string>>>();
  for (const c of chs) for (const s of sentences(c)) {
    const l = s.trace.ledger;
    if (l) {
      const was = verdict.get(l.domain);
      if (was && was !== l.verdict) out.push(`${l.domain}: ${was} vs ${l.verdict} (${c.chapter})`);
      verdict.set(l.domain, l.verdict);
      if (l.verdict !== 'thuan') explained.add(l.domain.split('.')[0]);
    }
    if (s.trace.basis !== 'sach') continue;
    for (const x of s.trace.concepts) {
      const con = cmap.get(x), d = con && DOMAIN(con.facet);
      if (!d || con.pol === '~') continue;
      const m = sides.get(d) ?? sides.set(d, new Map()).get(d)!;
      (m.get(con.pol) ?? m.set(con.pol, new Set()).get(con.pol)!).add(c.chapter);
    }
  }
  for (const [d, m] of sides) {
    const plus = [...(m.get('+') ?? [])], minus = [...(m.get('-') ?? [])];
    if (plus.some(a => minus.some(b => b !== a)) && !explained.has(d)) out.push(`${d}: + in ${plus.join(',')} / − in ${minus.join(',')}, no explaining conclusion`);
  }
  return out;
}

test('the contradiction check fails on a report that concludes one domain both ways, or leaves opposite readings unexplained', () => {
  const s = (domain: string | null, verdict: string, concepts: string[] = []): ProseSentence => ({ text: 'x', trace: { move: 'VALUE', concepts, rules: [], cites: [],
    basis: domain ? 'he_thong' : 'sach', ...(domain ? { ledger: { domain, verdict, base: '+' } } : {}) } });
  const para = (...xs: ProseSentence[]): ProseParagraph => ({ role: 'core', sentences: xs, text: '' });
  assert.equal(contradictions([{ chapter: 'menh', paragraphs: [para(s('cong_danh', 'thuan'))] }, { chapter: 'cong_danh', paragraphs: [para(s('cong_danh', 'tro_ngai'))] }]).length, 1);
  assert.equal(contradictions([{ chapter: 'menh', paragraphs: [para(s(null, '', ['career.obstacle']))] }, { chapter: 'cong_danh', paragraphs: [para(s(null, '', ['career.success']))] }]).length, 1);
  assert.equal(contradictions([{ chapter: 'menh', paragraphs: [para(s(null, '', ['career.obstacle']))] }, { chapter: 'cong_danh', paragraphs: [para(s(null, '', ['career.success']), s('cong_danh', 'co_dieu_kien'))] }]).length, 0);
});

const sample = [...bench.map(b => b.facts), REF, ...corpus.slice(0, 60).map(c => c.facts)];
test('report-wide: no domain concluded two ways, no unexplained opposite readings (benchmark20, the 2002 chart, 60 corpus charts)', () => {
  const bad = sample.flatMap((f, i) => contradictions(report(f)).map(x => `chart ${i} (${f.year_gz}): ${x}`));
  assert.deepEqual(bad, []);
});

test('every limiting element of a palace is faced; every sentence has its step; no duplicate sentence; no empty chapter', () => {
  const bad: string[] = [];
  for (const [i, f] of sample.entries()) {
    const { resolved } = infer(f, K);
    const chs = report(f), seen = new Map<string, string>();
    for (const c of chs) {
      if (!c.paragraphs.length || !c.text.trim()) bad.push(`chart ${i} ${c.chapter}: empty`);
      if (!c.luan) continue;
      const ss = sentences(c);
      for (const s of ss) {
        if (!s.trace.step) bad.push(`chart ${i} ${c.chapter}: no step: ${s.text}`);
        if (s.trace.basis === 'sach' && !s.trace.rules.every(r => K.rules.find(x => x.id === r)?.reviewStatus === 'verified')) bad.push(`chart ${i}: unverified rule in ${s.text}`);
        if (s.trace.basis === 'sach' || s.trace.ledger) { const w = seen.get(s.text); if (w) bad.push(`chart ${i}: duplicate in ${c.chapter} and ${w}: ${s.text}`); else seen.set(s.text, c.chapter); }
      }
      const ev = palaceEvidence(f, K, c.palace, { resolved });
      for (const e of [...ev.limit, ...ev.mixed.filter(x => x.kind === 'ky_carrier')]) {
        const faced = ss.some(s => !(s.trace.step ?? '').startsWith('frame') && ((s.trace.confront ?? []).includes(e.id)
          || s.trace.rules.some(r => resolved.some(x => x.ruleId === r && x.subject === `palace:${c.palace}` && readsElement(x, e, c.palace)))));
        if (!faced) bad.push(`chart ${i} ${c.palace}: ${e.id} not faced`);
      }
    }
  }
  assert.deepEqual(bad.slice(0, 20), []);
});

test('chapter frame: structure first, the conclusion from the ledger after the readings, readable (no method word)', () => {
  const METHOD = /nguồn(?! (?:thu|lợi|tiền)\b)|quy tắc|đối chiếu|phạm vi|hệ thống|trọng số|cách hiểu|chưa có lời/iu;
  for (const f of [REF, ...bench.slice(0, 8).map(b => b.facts)]) for (const c of report(f).filter(x => (x as LuanChapter).luan)) {
    const parts = c.paragraphs.map(p => p.part ?? 0);
    assert.equal(parts[0], 1, `${c.chapter}: the structure opens`);
    const five = parts.indexOf(5);
    if (five >= 0) assert.ok(parts.slice(1, five).some(x => x >= 2 && x <= 4) || five === 1, `${c.chapter}: readings before the conclusion`);
    for (const s of sentences(c)) assert.ok(!METHOD.test(s.text), `${c.chapter}: ${s.text}`);
  }
  // the 2002 chapters that conclude on a domain end their readings with part 5 and keep the sources in the evidence (Căn cứ fold)
  for (const id of ['phu_the', 'cong_danh', 'tai_bach', 'menh']) {
    const c = ch(id);
    assert.ok(c.paragraphs.some(p => p.part === 5), id);
    assert.ok((c.evidence as { ledger?: unknown[] }).ledger?.length, `${id}: ledger in the evidence`);
  }
});

test('vận hạn: no phổ thông meaning labelled as a book; each hạn tied to the natal ledger; the closing agrees with the index level', () => {
  for (const f of [REF, ...bench.slice(0, 6).map(b => b.facts)]) {
    const vh = proseVanHan(f, K, 'seed', 'test', true);
    const idx = computeIndices(f, K, norms as IndexNorms).decades;
    const ss = vh.paragraphs.flatMap(p => p.sentences);
    for (const s of ss) if (s.trace.basis === 'sach') assert.ok(s.trace.rules.length && !/^hoa:/.test(s.trace.step ?? ''), `sach without its rule: ${s.text}`);
    vh.starts.forEach((pi, i) => {
      const d = vh.decades[i], next = vh.starts[i + 1] ?? vh.paragraphs.length;
      const mine = vh.paragraphs.slice(pi, next).flatMap(p => p.sentences);
      const lv = mine.find(s => s.trace.step?.startsWith('level:'));
      const want = idx.find(x => x.age_from === d.age_from)!.level;
      assert.ok(lv, `${d.age_from}: a closing by level`);
      assert.equal(Number(lv!.trace.step!.slice(6)), want, `${d.age_from}: level`);
      if (want <= 1) assert.doesNotMatch(lv!.text, /chặng thuận|rất thuận|trung bình/);
      if (want >= 3) assert.doesNotMatch(lv!.text, /thử thách|trung bình/);
    });
    // the decade of the 2002 chart at Phu Thê speaks of the marriage verdict
    if (f === REF) assert.ok(ss.some(s => s.trace.step === 'natal:hon_nhan'), 'Phu Thê hạn tied to the marriage verdict');
  }
});

test('route output: the checked report keeps the conclusions and the hạn closings', () => {
  const chs = proseAllChapters(REF, K, { allowDraft: true, deep: true, luan: true }).map(c => checkedOnly(c as Parameters<typeof checkedOnly>[0]) as unknown as { chapter: string; paragraphs: ProseParagraph[] });
  assert.ok(chs.find(c => c.chapter === 'phu_the')!.paragraphs.some(p => p.sentences.some(s => s.trace.ledger)));
  const vh = chs.find(c => c.chapter === 'van_han')!;
  assert.ok(vh.paragraphs.flatMap(p => p.sentences).filter(s => s.trace.step?.startsWith('level:')).length >= 6);
  assert.ok(!vh.paragraphs.flatMap(p => p.sentences).some(s => s.trace.basis === 'pho_thong'));
});
