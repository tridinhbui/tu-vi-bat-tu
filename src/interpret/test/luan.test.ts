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
import { SAT } from '../kg/atoms.ts';
import type { ProseSentence } from '../prose/realize.ts';

const FX = join(import.meta.dirname, 'fixtures');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const ex = JSON.parse(readFileSync(join(FX, 'menh_cu_tuat.json'), 'utf8')).facts;
const corpusFile = join(FX, 'corpus1000.json.gz');
const rmap = new Map(K.rules.map(r => [r.id, r]));
const isLuan = (c: { luan?: boolean }): c is LuanChapter => !!c.luan;

test('luan.json: no frame uses meta-language or an absolute, every slot is one the writer fills', () => {
  const SLOTS = new Set(['pal', 'branch', 'majors', 'star', 'from', 'stars', 'tt', 'a', 'b', 'group', 'note', 'S', 'mature', 'seat', 'config', 'domain', 'claim', 'text',
    'pair', 'left', 'right', 'other', 'opal', 'neg', 'pos', 'list', 'age', 'young', 'np', 'late',
    // the ledger conclusion, the confronted limits, the one-star caveat (S1)
    'domain', 'verdict', 'link', 'ground', 'limits', 'palace', 'supports', 'mitig', 'el',
    // the two sides of an unresolved or two-faceted domain (owner review 2026-10-22): what each stands on, what each is about
    'gpos', 'gneg', 'fpos', 'fneg']);
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
  // cung giáp / nhị hợp / lục hại carry no reading: a note on the frame, not a paragraph of the text
  assert.ok(!rest.some(p => p.topic === 'vi_tri'), 'no paragraph of bare positions');
  const pos = frame.sentences.at(-1)!.trace.note ?? '';
  assert.match(pos, /nhị hợp/); assert.match(pos, /Mão/);
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
          // a system sentence claims nothing of its own; a domain conclusion (trace.ledger) lists the verified readings it gathers
          if (s.trace.basis === 'he_thong' && !s.trace.ledger) assert.equal(s.trace.rules.length, 0, s.text);
          if (s.trace.ledger) for (const id of s.trace.rules) assert.equal(rmap.get(id)?.reviewStatus, 'verified', `${id}: ${s.text}`);
          assert.notEqual(s.trace.basis, 'pho_thong', `a phổ thông sentence in a luận cung chapter: ${s.text}`);
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

// ---- the owner's own chart (09/01/2002 04:30 nam, Khảo Luận table, facts as /api/facts gave them on 2026-10-21): three reasoning defects ----
const mine = JSON.parse(readFileSync(join(FX, 'ref_2002_01_09_kl.json'), 'utf8'));
const polOf = new Map(K.concepts.concepts.map(c => [c.id, c.pol]));
/** names of the limiting atoms (sát tinh, Hóa Kỵ, Tuần/Triệt, a chính tinh in hãm) a book sentence's own rules rest on */
function limitingAtoms(s: ProseSentence, sh: ReturnType<typeof luanShared>, chart: typeof mine): string[] {
  const rs = sh.resolved.filter(r => s.trace.rules.includes(r.ruleId) && s.trace.concepts.includes(r.concept));
  // the trace lists every rule on the claim's axis; the sentence voices one of them: when one of them rests on no limiting atom at all,
  // the sentence may be voicing that one
  const lim = (r: typeof rs[number]) => r.atoms.some(a => (a.kind === 'star' && SAT.includes(a.name)) || (a.kind === 'hoa' && a.name === 'Hóa Kỵ') || a.kind === 'tuan_triet'
    || (a.kind === 'dignity' && a.value === 'hãm') || (a.kind === 'star' && chart.palaces.find((p: any) => p.name === a.palace)?.major_dignity?.[a.name] === 'hãm'));
  if (rs.some(r => !lim(r))) return [];
  const ham = (star: string, palace: string | null) => chart.palaces.find((p: any) => p.name === palace)?.major_dignity?.[star] === 'hãm';
  return [...new Set(rs.flatMap(r => r.atoms.filter(a => (a.kind === 'star' && (SAT.includes(a.name) || ham(a.name, a.palace))) || (a.kind === 'hoa' && a.name === 'Hóa Kỵ')
    || a.kind === 'tuan_triet' || (a.kind === 'dignity' && a.value === 'hãm')).map(a => a.name)))];
}
/** the book's short forms of the limiting stars ("Kình", "Không Kiếp", "Kỵ") count as naming them */
const SHORT: Record<string, string> = { 'Kình Dương': 'Kình', 'Đà La': 'Đà', 'Địa Không': 'Không', 'Địa Kiếp': 'Kiếp', 'Hỏa Tinh': 'Hỏa', 'Linh Tinh': 'Linh', 'Hóa Kỵ': 'Kỵ' };
/** a limiting claim names at least one limiting atom of its own rule, when the rule has one */
function negativeClaimsNameTheirCause(ch: LuanChapter, sh: ReturnType<typeof luanShared>, chart: typeof mine): string[] {
  const bad: string[] = [];
  for (const p of ch.paragraphs) p.sentences.forEach((s, i) => {
    if (s.trace.basis !== 'sach' || !(s.trace.step ?? '').startsWith('claim:')) return;
    if (!s.trace.concepts.some(c => polOf.get(c) === '-')) return;
    // the cause may have been named just before ("Cùng thế ấy, …", "Hệ quả là …"): this sentence or an earlier one of the paragraph
    const said = p.sentences.slice(0, i + 1).map(x => x.text).join(' ');
    const atoms = limitingAtoms(s, sh, chart);
    if (atoms.length && !atoms.some(a => said.includes(a) || (SHORT[a] && new RegExp(`(^|[^\\p{L}])${SHORT[a]}(?![\\p{L}])`, 'u').test(said)))) bad.push(`${atoms.join('/')} not named: ${s.text}`);
  });
  return bad;
}

test('own chart (1): a limiting claim names the limiting atom of its rule, not only the helping stars', () => {
  const sh = luanShared(mine, K, true), ch = luanChapter(mine, K, 'menh', sh)!;
  assert.deepEqual(negativeClaimsNameTheirCause(ch, sh, mine), []);
  const s = ch.paragraphs.flatMap(p => p.sentences).find(x => x.text.includes('đường công danh mờ mịt'))!;
  assert.ok(s && s.text.includes('Kình Dương'), s?.text);
});

test('own chart (2): within a paragraph a cause clause is not said twice', () => {
  const ch = luanChapter(mine, K, 'menh', luanShared(mine, K, true))!;
  for (const p of ch.paragraphs) {
    const claims = p.sentences.filter(s => (s.trace.step ?? '').startsWith('claim:')).map(s => s.text.toLowerCase().replace(/[.,;:]/g, '').split(/\s+/));
    const seen = new Map<string, number>();
    claims.forEach((w, i) => { for (let j = 0; j + 5 <= w.length; j++) { const g = w.slice(j, j + 5).join(' '); if (seen.has(g) && seen.get(g) !== i) assert.fail(`"${g}" repeated in: ${p.text}`); seen.set(g, i); } });
  }
  assert.ok(!/Hóa Khoa trên Văn Khúc[^.]*\.[^.]*Hóa Khoa trên Văn Khúc/.test(ch.text));
});

test('own chart (3): the Hóa Lộc rescue of Cự Môn hãm is told soft, with the Tứ Mộ reduction right after it, once', () => {
  const ch = luanChapter(mine, K, 'menh', luanShared(mine, K, true))!;
  const p = ch.paragraphs.find(q => q.sentences.some(s => s.trace.step === 'claim:T:major:Cự Môn:life.mitigated'))!;
  const i = p.sentences.findIndex(s => s.trace.step === 'claim:T:major:Cự Môn:life.mitigated');
  assert.equal(p.sentences[i + 1]?.trace.step, 'caveat:T:major:Cự Môn', p.text);
  assert.match(p.sentences[i + 1].text, /Tứ Mộ/);
  assert.ok(!ch.paragraphs.some(q => q.sentences.some(s => s.trace.step?.startsWith('behave:') && s.trace.concepts.includes('life.mitigated'))), 'no behaviour line amplifies the rescue');
  assert.ok(!/vẫn giữ được thế khá|cơ chế tự cân bằng|hết hãm/.test(ch.text.replace(/không có nghĩa là Cự Môn hết hãm/, '')), ch.text);
  assert.equal((ch.text.match(/đóng ở Tứ Mộ/g) ?? []).length, 1, 'the Tứ Mộ reduction is told once');
});

test('own chart: Tả Phụ at Dần is hãm in Khảo Luận (KL p.121 "Tả Hữu đắc địa tứ mộ, còn hãm địa tất cả các cung khác"), shown with its page', () => {
  const ch = luanChapter(mine, K, 'menh', luanShared(mine, K, true))!;
  const s = ch.paragraphs.flatMap(p => p.sentences).find(x => x.text.includes('Tả Phụ (Hãm Địa)'))!;
  assert.ok(s && s.trace.cites.includes('KL p.121'), s?.text);
});

test('corpus: every limiting claim names a limiting atom of its rule', { skip: !existsSync(corpusFile) && 'corpus not built' }, () => {
  const corpus = JSON.parse(gunzipSync(readFileSync(corpusFile)).toString('utf8'));
  const bad: string[] = [];
  for (const c of corpus.slice(0, 200)) {
    const sh = luanShared(c.facts, K, true);
    for (const id of ['menh', 'cong_danh', 'tai_bach'] as const) { const ch = luanChapter(c.facts, K, id, sh); if (ch) bad.push(...negativeClaimsNameTheirCause(ch, sh, c.facts)); }
  }
  assert.deepEqual(bad.slice(0, 5), [], `${bad.length} limiting claims without their cause`);
});
