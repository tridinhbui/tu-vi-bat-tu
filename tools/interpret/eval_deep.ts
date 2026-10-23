// Depth audit of the Tử Vi luận chapters (plan DEEP-TUVI, docs/audit/DEEP-TUVI.md): how much ANALYSIS a chapter carries, not how many
// words. Over the corpus, on the text the reader sees (luận chapters, checked readings only):
//   node tools/interpret/eval_deep.ts [--n 1000] [--json out.json] [--chapters cong_danh,tai_bach,phu_the]
// Per chapter and chart:
//   claims        distinct concepts voiced by book sentences (behaviour lines and illustrations not counted)
//   mechanisms    sentences that say WHY: a star's nature as the book states it (step mechanism:*), tied to a claim
//   supports      distinct positive concepts among the claims
//   counters      sentences that set a limit against a claim (frame part 4: a reducer, a limiting element faced, a Kỵ carrier, a one-star caveat)
//   interactions  sentences on how palaces or elements act on each other (part 3: tam phương corroboration / counter-evidence, structures,
//                 Thân, cross-palace links, step link:*)
//   conditions    conditional interpretations (step cond:*, or a ledger verdict có điều kiện / hai chiều / trở ngại)
//   units         claims + mechanisms + counters + interactions + conditions; words per unit = words / units (padding shows as a rise)
//   cross links   distinct OTHER palaces the chapter's sentences stand on (their rules' palaces) or name in a link sentence
//   unreasoned    conclusion sentences (trace.ledger) in a chapter where no book sentence voices any of the readings the conclusion gathers
//   overlooked    (a) verified readings that fire on the palace (live, past the position guards) and no chapter of the report voices;
//                 (b) a natal Hóa in the palace no sentence past the frame names; (c) a pair of chính tinh in the palace no sentence past the
//                 frame reads together; (d) the person's Thân in the palace, not named past the frame
//   repetition    median word-trigram Jaccard of the chapter between charts whose core palace has DIFFERENT chính tinh (names removed)
//   typical       units for charts whose core-palace configuration (its chính tinh, or VCD) is common (≥ 3 % of the corpus) vs rare (< 1 %)
import { readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import type { ChartInput, Knowledge } from '../../src/interpret/types.ts';
import { luanReport } from '../../src/interpret/prose/luan.ts';
import { checkedOnly } from '../../src/interpret/prose/checked.ts';
import { proseThemes } from '../../src/interpret/prose/themes.ts';
import { infer, PROSE_SPECS, type ProseChapterId } from '../../src/interpret/prose/chapter.ts';

const ROOT = join(import.meta.dirname, '..', '..');
const arg = (k: string, d: string) => process.argv.includes(k) ? process.argv[process.argv.indexOf(k) + 1] : d;
const K: Knowledge = JSON.parse(readFileSync(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'), 'utf8'));
const N = Number(arg('--n', '1000'));
const CHS = arg('--chapters', 'cong_danh,tai_bach,phu_the,menh,thien_di,phuc_duc,dien_trach').split(',') as ProseChapterId[];
const cmap = new Map(K.concepts.concepts.map(c => [c.id, c]));
const rmap = new Map(K.rules.map(r => [r.id, r]));
const PALACES = ['Mệnh', 'Phụ Mẫu', 'Phúc Đức', 'Điền Trạch', 'Quan Lộc', 'Nô Bộc', 'Thiên Di', 'Tật Ách', 'Tài Bạch', 'Tử Tức', 'Phu Thê', 'Huynh Đệ'];
const NAMES = new RegExp(['Tử Vi', 'Thiên Cơ', 'Thái Dương', 'Vũ Khúc', 'Thiên Đồng', 'Liêm Trinh', 'Thiên Phủ', 'Thái Âm', 'Tham Lang', 'Cự Môn', 'Thiên Tướng', 'Thiên Lương',
  'Thất Sát', 'Phá Quân', 'Kình Dương', 'Đà La', 'Hỏa Tinh', 'Linh Tinh', 'Địa Không', 'Địa Kiếp', 'Tả Phụ', 'Hữu Bật', 'Văn Xương', 'Văn Khúc', 'Thiên Khôi', 'Thiên Việt',
  'Lộc Tồn', 'Thiên Mã', 'Hóa Lộc', 'Hóa Quyền', 'Hóa Khoa', 'Hóa Kỵ', 'Tuần', 'Triệt', ...PALACES, 'Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu',
  'Tuất', 'Hợi', 'Miếu Địa', 'Vượng Địa', 'Đắc Địa', 'Lợi Địa', 'Bình Hòa', 'Hãm Địa', 'miếu', 'vượng', 'đắc', 'hãm', 'bình'].sort((a, b) => b.length - a.length).join('|'), 'g');
const words = (t: string) => t.toLowerCase().replace(/[.,;:!?()“”"]/g, ' ').split(/\s+/).filter(Boolean);
const grams = (t: string) => { const w = words(t.replace(NAMES, ' ')), s = new Set<string>(); for (let i = 0; i + 3 <= w.length; i++) s.add(w.slice(i, i + 3).join(' ')); return s; };
const jac = (a: Set<string>, b: Set<string>) => { if (!a.size && !b.size) return 1; let i = 0; for (const x of a) if (b.has(x)) i++; return i / (a.size + b.size - i); };
const median = (xs: number[]) => { const s = [...xs].sort((a, b) => a - b); return s.length ? s[Math.floor(s.length / 2)] : 0; };
const mean = (xs: number[]) => xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : 0;
const r2 = (x: number) => +x.toFixed(2);

type S = { text: string; trace: { step?: string; move: string; rules: string[]; concepts: string[]; basis: string; part?: number; ledger?: { domain: string; verdict: string } } };
type Ch = { chapter: string; palace: string; paragraphs: Array<{ sentences: S[]; deep?: boolean }> };
const LIVE = (r: { status: string }) => r.status !== 'voided' && r.status !== 'divergent';
const NOT_CLAIM = /^(behave|minh_hoa|frame|centre|position|mechanism|link|cond|trigger|tame|deep:back)/;
const COUNTER = /^(confront|kyc|single|contested|against|reducer|caveat|modifier)/;
const INTER = /^(corroborated|countered|structure|bridge|than|link|formation|trigger|tame)/;

export interface ChapterRow { chart: number; chapter: string; config: string; words: number; sentences: number; deepWords: number;
  claims: number; mechanisms: number; supports: number; counters: number; interactions: number; conditions: number; illustrations: number; units: number;
  cross: number; unreasoned: number; overlookedRules: string[]; overlookedHoa: string[]; overlookedPair: boolean; overlookedThan: boolean; text: string }

export function rowsOf(idx: number, f: ChartInput, k: Knowledge, chapters: string[]): ChapterRow[] {
  const { resolved } = infer(f, k);
  const all = luanReport(f, k, { allowDraft: true, deep: true }).map(c => checkedOnly(c as never) as unknown as Ch);
  const themes = proseThemes(f, k, 'eval', { allowDraft: true, luan: true }).map(c => checkedOnly(c as never) as unknown as Ch);
  const voicedRules = new Set([...all, ...themes].flatMap(c => c.paragraphs.flatMap(p => p.sentences.filter(s => s.trace.basis === 'sach').flatMap(s => s.trace.rules))));
  const out: ChapterRow[] = [];
  for (const ch of all) {
    if (!chapters.includes(ch.chapter)) continue;
    const P = ch.palace, pal = f.palaces.find(p => p.name === P)!;
    const ss = ch.paragraphs.flatMap(p => p.sentences), text = ss.map(s => s.text).join(' ');
    const deepWords = ch.paragraphs.filter(p => p.deep).flatMap(p => p.sentences).reduce((a, s) => a + words(s.text).length, 0);
    const book = ss.filter(s => s.trace.basis === 'sach');
    const claimC = new Set(book.filter(s => !NOT_CLAIM.test(s.trace.step ?? '') && s.trace.move !== 'ELABORATE').flatMap(s => s.trace.concepts));
    const mechanisms = ss.filter(s => (s.trace.step ?? '').startsWith('mechanism:')).length;
    const supports = [...claimC].filter(c => cmap.get(c)?.pol === '+').length;
    const counters = ss.filter(s => !s.trace.ledger && (s.trace.part === 4 || COUNTER.test(s.trace.step ?? ''))).length;
    const interactions = ss.filter(s => !s.trace.ledger && (s.trace.part === 3 || INTER.test(s.trace.step ?? ''))).length
      + ss.filter(s => s.trace.ledger && /:both_|:two_ways/.test(s.trace.step ?? '')).length;
    const conditions = ss.filter(s => (s.trace.step ?? '').startsWith('cond:') || (s.trace.ledger && ['co_dieu_kien', 'hai_chieu', 'tro_ngai', 'chua_phan_xu', 'hai_mat', 'giam_nhe'].includes(s.trace.ledger.verdict) && !/:again$/.test(s.trace.step ?? ''))).length;
    const illustrations = ss.filter(s => s.trace.basis === 'minh_hoa' || /^behave:/.test(s.trace.step ?? '')).length;
    // the other palaces the chapter stands on: the palaces of its sentences' readings, and palaces a link sentence names
    const cross = new Set<string>();
    for (const s of ss) {
      if (/^(frame|centre|position)/.test(s.trace.step ?? '')) continue;
      for (const r of resolved.filter(x => s.trace.rules.includes(x.ruleId))) { const q = r.subject.replace(/^palace:/, ''); if (q !== P && q !== 'chart') cross.add(q); }
      if (/^(link|cond|mechanism)/.test(s.trace.step ?? '')) for (const q of PALACES) if (q !== P && s.text.includes(q)) cross.add(q);
    }
    // conclusions with none of their readings voiced in this chapter
    const chRules = new Set(book.flatMap(s => s.trace.rules));
    const unreasoned = ss.filter(s => s.trace.ledger && s.trace.rules.length && !s.trace.rules.some(r => chRules.has(r))).length;
    // overlooked
    const live = resolved.filter(r => r.subject === `palace:${P}` && LIVE(r) && rmap.get(r.ruleId)?.reviewStatus === 'verified');
    const overlookedRules = [...new Set(live.map(r => r.ruleId))].filter(id => !voicedRules.has(id));
    const past = ss.filter(s => !/^(frame|centre|position)/.test(s.trace.step ?? ''));
    const pastText = past.map(s => s.text).join(' ');
    const hoaSelf = Object.entries(f.tu_hoa).filter(([, v]) => v.branch === pal.branch_index).map(([h, v]) => ({ h, star: v.star }));
    const overlookedHoa = hoaSelf.filter(x => !past.some(s => s.text.includes(x.h) || (s.text.includes(x.star) && /hóa (Lộc|Quyền|Khoa|Kỵ)/.test(s.text)))).map(x => `${x.h}:${x.star}`);
    const pair = pal.major_stars.length === 2 ? pal.major_stars : null;
    const overlookedPair = !!pair && !past.some(s => pair.every(m => s.text.includes(m)) || resolved.some(r => s.trace.rules.includes(r.ruleId) && pair.every(m => r.atoms.some(a => a.kind === 'star' && a.name === m))));
    const overlookedThan = !!pal.is_than && !/Thân/.test(pastText);
    const n = words(text).length;
    const units = claimC.size + mechanisms + counters + interactions + conditions;
    out.push({ chart: idx, chapter: ch.chapter, config: pal.major_stars.length ? [...pal.major_stars].sort().join('+') : 'VCD', words: n, sentences: ss.length, deepWords,
      claims: claimC.size, mechanisms, supports, counters, interactions, conditions, illustrations, units, cross: cross.size, unreasoned,
      overlookedRules, overlookedHoa, overlookedPair, overlookedThan, text });
  }
  return out;
}

export function summarize(rows: ChapterRow[]) {
  const by = new Map<string, ChapterRow[]>();
  for (const r of rows) (by.get(r.chapter) ?? by.set(r.chapter, []).get(r.chapter)!).push(r);
  const out: Record<string, unknown> = {};
  for (const [ch, rs] of by) {
    const freq = new Map<string, number>(); rs.forEach(r => freq.set(r.config, (freq.get(r.config) ?? 0) + 1));
    const common = rs.filter(r => freq.get(r.config)! / rs.length >= 0.03), rare = rs.filter(r => freq.get(r.config)! / rs.length < 0.01);
    // repetition: pairs of charts with different core configurations (deterministic sample)
    const sims: number[] = [];
    const gs = rs.map(r => grams(r.text));
    for (let i = 0; i < rs.length && sims.length < 4000; i++) for (let j = i + 1; j < rs.length && j < i + 9; j++) if (rs[i].config !== rs[j].config) sims.push(jac(gs[i], gs[j]));
    const ruleMiss = new Map<string, number>(); rs.forEach(r => r.overlookedRules.forEach(x => ruleMiss.set(x, (ruleMiss.get(x) ?? 0) + 1)));
    const units = rs.map(r => r.units);
    out[ch] = {
      charts: rs.length, words: r2(mean(rs.map(r => r.words))), deepWords: r2(mean(rs.map(r => r.deepWords))), sentences: r2(mean(rs.map(r => r.sentences))),
      units: r2(mean(units)), unitsMedian: median(units), claims: r2(mean(rs.map(r => r.claims))), mechanisms: r2(mean(rs.map(r => r.mechanisms))),
      supports: r2(mean(rs.map(r => r.supports))), counters: r2(mean(rs.map(r => r.counters))), interactions: r2(mean(rs.map(r => r.interactions))),
      conditions: r2(mean(rs.map(r => r.conditions))), illustrations: r2(mean(rs.map(r => r.illustrations))),
      wordsPerUnit: r2(mean(rs.filter(r => r.units).map(r => r.words / r.units))),
      mechanismCoverage: r2(rs.filter(r => r.mechanisms > 0).length / rs.length), crossLinks: r2(mean(rs.map(r => r.cross))),
      zeroUnits: rs.filter(r => !r.units).length, unreasoned: rs.reduce((a, r) => a + r.unreasoned, 0),
      overlookedRules: rs.reduce((a, r) => a + r.overlookedRules.length, 0), chartsWithOverlookedRule: rs.filter(r => r.overlookedRules.length).length,
      overlookedHoa: rs.reduce((a, r) => a + r.overlookedHoa.length, 0), overlookedPair: rs.filter(r => r.overlookedPair).length, overlookedThan: rs.filter(r => r.overlookedThan).length,
      repetition: r2(median(sims)),
      typical: { commonCharts: common.length, commonUnits: r2(mean(common.map(r => r.units))), rareCharts: rare.length, rareUnits: r2(mean(rare.map(r => r.units))) },
      topOverlooked: [...ruleMiss].sort((a, b) => b[1] - a[1]).slice(0, 12),
    };
  }
  return out;
}

/** The gate charts of the plan (2002 fixture, the 1911 / 1971 reference boards, three unusual configurations): `facts` by name. */
export function gateCharts(): Array<[string, ChartInput]> {
  const FX = join(ROOT, 'src', 'interpret', 'test', 'fixtures');
  const charts = JSON.parse(readFileSync(join(FX, 'charts.json'), 'utf8'));
  const refs = JSON.parse(readFileSync(join(FX, 'deep_reference_charts.json'), 'utf8'));
  return [['2002', JSON.parse(readFileSync(join(FX, 'ref_2002_01_09_kl.json'), 'utf8'))], ['1911', refs['1911-01-01_1230_nam']], ['1971', refs['1971-05-24_1030_nam']],
    ['tuan_triet_quan_loc', charts[21].facts], ['tai_bach_vcd', charts[13].facts], ['phu_the_vcd_nu', charts[23].facts]];
}

if (process.argv[1]?.endsWith('eval_deep.ts') && process.argv.includes('--gates')) {
  for (const [name, f] of gateCharts()) for (const r of rowsOf(0, f, K, ['cong_danh', 'tai_bach', 'phu_the']))
    console.log([name.padEnd(20), r.chapter.padEnd(9), `words ${r.words}`, `units ${r.units}`, `claims ${r.claims}`, `mech ${r.mechanisms}`, `counters ${r.counters}`, `inter ${r.interactions}`,
      `cond ${r.conditions}`, `cross ${r.cross}`, `w/u ${r.units ? (r.words / r.units).toFixed(1) : '-'}`, `overlooked ${r.overlookedRules.length}`].join(' | '));
} else if (process.argv[1]?.endsWith('eval_deep.ts')) {
  const corpus = JSON.parse(gunzipSync(readFileSync(join(ROOT, 'src', 'interpret', 'test', 'fixtures', 'corpus1000.json.gz'))).toString()) as Array<{ facts: ChartInput }>;
  const rows = corpus.slice(0, N).flatMap((c, i) => rowsOf(i, c.facts, K, CHS));
  const s = summarize(rows);
  console.log(JSON.stringify(s, null, 1));
  if (process.argv.includes('--json')) writeFileSync(arg('--json', 'deep_eval.json'), JSON.stringify(s, null, 1));
}
