// Synthesis-layer metrics of the Tử Vi luận chapters (plan quirky-tinkering-rabin step 5, S1), over the corpus:
//   node tools/interpret/eval_synthesis.ts [--n 1000] [--json out.json]
//   unfaced      palaces whose chapter leaves a limiting element of the palace unfaced: Hóa Kỵ, a sát tinh not checked đắc, a hãm chính tinh,
//                Tuần / Triệt, a star carrying Kỵ (reason/evidence.ts). Faced = a sentence (not the frame) tells a verified reading standing on
//                it, or names it as a limit (trace.confront)
//   one-star     claim sentences on a big domain (career, money, marriage, health) whose readings rest on one rule of minor stars only (tier
//                ≥ 4), with no "one star" caveat after them
//   contradict   pairs of chapters of one report voicing opposite sides of the same domain (a + and a − book sentence on its facets) with no
//                conclusion sentence of that domain in the report that explains them (verdict có điều kiện / hai chiều / trở ngại). A reading
//                about other people (the wealth of the parents, children, siblings or partner: a concept outside the bond of a Phụ Mẫu / Tử
//                Tức / Huynh Đệ / Phu Thê reading, prose/chapter.ts PROSE_SPECS.bond) is not a side of the person's own domain
//   verdicts     conclusion sentences of one domain in one report that disagree with each other (must be 0)
// Runs on any checkout that has src/interpret/reason/evidence.ts (copy it in to measure an older tree).
import { readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import type { ChartInput, Knowledge } from '../../src/interpret/types.ts';
import { luanReport } from '../../src/interpret/prose/luan.ts';
import { infer, PROSE_SPECS } from '../../src/interpret/prose/chapter.ts';
import { palaceEvidence, readsElement } from '../../src/interpret/reason/evidence.ts';
import { Geo, seatOf } from '../../src/interpret/reason/tiers.ts';

const ROOT = join(import.meta.dirname, '..', '..');
const arg = (k: string, d: string) => process.argv.includes(k) ? process.argv[process.argv.indexOf(k) + 1] : d;
const K: Knowledge = JSON.parse(readFileSync(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'), 'utf8'));
const corpus = JSON.parse(gunzipSync(readFileSync(join(ROOT, 'src', 'interpret', 'test', 'fixtures', 'corpus1000.json.gz'))).toString()) as Array<{ facts: ChartInput }>;
const N = Number(arg('--n', '1000'));
const cmap = new Map(K.concepts.concepts.map(c => [c.id, c]));
const BIG = /^(career|finance|wellbeing)\.|^relationships\.(marriage|partner|romance)$/;
const DOMAIN = (facet: string) => facet.startsWith('career.') && !facet.endsWith('.timing') ? 'cong_danh' : facet.startsWith('finance.') ? 'tai_loc'
  : facet === 'relationships.marriage' ? 'hon_nhan' : facet.startsWith('wellbeing.') ? 'suc_khoe' : null;
// a conclusion that names both sides explains them: conditional, two-ways, adverse, and (owner review 2026-10-22) unresolved, two facets, mitigated, health named without verdict
const EXPLAINS = new Set(['co_dieu_kien', 'hai_chieu', 'tro_ngai', 'chua_phan_xu', 'hai_mat', 'giam_nhe', 'khong_ket_luan']);
const BOND = new Map(Object.values(PROSE_SPECS).filter(sp => sp.bond).map(sp => [sp.palace, sp.bond!]));

type S = { text: string; trace: { step?: string; rules: string[]; concepts: string[]; basis: string; confront?: string[]; ledger?: { domain: string; verdict: string } } };
const m = { charts: 0, palaces: 0, withLimit: 0, unfaced: 0, elements: 0, elementsUnfaced: 0, claims: 0, oneStar: 0, contradict: 0, verdictClash: 0, errors: 0 };
const examples: Record<string, string[]> = { unfaced: [], oneStar: [], contradict: [] };
for (const [idx, c] of corpus.slice(0, N).entries()) {
  const f = c.facts;
  const { resolved } = infer(f, K);
  const chs = luanReport(f, K, { allowDraft: true, deep: true }) as unknown as Array<{ chapter: string; palace: string; luan?: boolean; pass?: boolean; issues?: Array<{ level: string }>;
    paragraphs: Array<{ sentences: S[] }> }>;
  m.charts++;
  const sides = new Map<string, Map<string, Set<string>>>();
  const verdicts = new Map<string, Set<string>>();
  for (const ch of chs) {
    if (ch.issues?.some(i => i.level === 'error')) m.errors++;
    const P = ch.palace, ss = ch.paragraphs.flatMap(p => p.sentences);
    m.palaces++;
    const ev = palaceEvidence(f, K, P, { resolved });
    const els = [...ev.limit, ...ev.mixed.filter(e => e.kind === 'ky_carrier')];
    if (els.length) m.withLimit++;
    let miss = 0;
    for (const e of els) {
      m.elements++;
      const faced = ss.some(s => !(s.trace.step ?? '').startsWith('frame') && ((s.trace.confront ?? []).includes(e.id)
        || s.trace.rules.some(r => resolved.some(x => x.ruleId === r && x.subject === `palace:${P}` && readsElement(x, e, P)))));
      if (!faced) { m.elementsUnfaced++; miss++; }
    }
    if (miss) { m.unfaced++; if (examples.unfaced.length < 8) examples.unfaced.push(`${f.year_gz} ${P}: ${els.map(e => e.id).join(', ')}`); }
    // one-star big claims
    const g = new Geo(f, P);
    ss.forEach((s, i) => {
      const st = s.trace.step ?? '';
      if (!st.startsWith('claim:') || !s.trace.concepts.some(c0 => BIG.test(cmap.get(c0)?.facet ?? ''))) return;
      m.claims++;
      // the claim's readings: those of this palace and the chart-level ones (độ số, tuổi) the reasoner counts in the same claim (plan.ts)
      const rs = resolved.filter(x => s.trace.rules.includes(x.ruleId) && (x.subject === `palace:${P}` || !x.subject.startsWith('palace:')));
      if (!rs.length || new Set(rs.map(x => x.ruleId)).size > 1 || !rs.every(x => seatOf(x, g).seat.tier >= 4)) return;
      // a caveat after it, or another palace saying the same (corroboration from the tam phương): not a one-star conclusion
      const caveat = ss.slice(i + 1, i + 5).some(x => /^(single|corroborated):/.test(x.trace.step ?? ''));
      if (!caveat) { m.oneStar++; if (examples.oneStar.length < 20) examples.oneStar.push(`#${idx} ${f.year_gz} ${P}: ${s.text}`); }
    });
    // sides voiced per domain, and the domain conclusions
    for (const s of ss) {
      if (s.trace.ledger) (verdicts.get(s.trace.ledger.domain.split('.')[0]) ?? verdicts.set(s.trace.ledger.domain.split('.')[0], new Set()).get(s.trace.ledger.domain.split('.')[0])!).add(`${s.trace.ledger.domain}:${s.trace.ledger.verdict}`);
      if (s.trace.basis !== 'sach') continue;
      for (const c0 of s.trace.concepts) {
        const con = cmap.get(c0), d = con && DOMAIN(con.facet);
        if (!d || con.pol === '~') continue;
        // the palaces the sentence's readings of this concept stand on: all of them about other people → not the person's domain
        const at = resolved.filter(x => x.concept === c0 && s.trace.rules.includes(x.ruleId)).map(x => x.subject.replace(/^palace:/, ''));
        if (at.length && at.every(p => BOND.get(p) && !BOND.get(p)!(con))) continue;
        const bySide = sides.get(d) ?? sides.set(d, new Map()).get(d)!;
        (bySide.get(con.pol) ?? bySide.set(con.pol, new Set()).get(con.pol)!).add(ch.chapter);
      }
    }
  }
  for (const [d, bySide] of sides) {
    const plus = bySide.get('+') ?? new Set(), minus = bySide.get('-') ?? new Set();
    const pairs = [...plus].flatMap(a => [...minus].filter(b => b !== a).map(b => `${a}/${b}`));
    if (!pairs.length) continue;
    const explained = [...(verdicts.get(d) ?? [])].some(x => EXPLAINS.has(x.split(':')[1]));
    if (!explained) { m.contradict += pairs.length; if (examples.contradict.length < 8) examples.contradict.push(`#${idx} ${f.year_gz} ${d}: ${pairs.join(', ')}`); }
  }
  for (const [, vs] of verdicts) {
    const byPart = new Map<string, Set<string>>();
    for (const x of vs) { const [id, v] = x.split(':'); (byPart.get(id) ?? byPart.set(id, new Set()).get(id)!).add(v); }
    for (const [, s] of byPart) if (s.size > 1) m.verdictClash++;
  }
}
const out = { ...m, unfacedRate: +(m.unfaced / Math.max(1, m.withLimit)).toFixed(3), elementUnfacedRate: +(m.elementsUnfaced / Math.max(1, m.elements)).toFixed(3), examples };
console.log(JSON.stringify(out, null, 1));
if (process.argv.includes('--json')) writeFileSync(arg('--json', 'synthesis_eval.json'), JSON.stringify(out, null, 1));
