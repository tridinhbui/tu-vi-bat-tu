// Bát Tự depth gate (Track C): sentences per chapter as the reader gets them (after checkedOnly), the share of đại vận lines with ≥2
// sentences of basis sach / tinh_toan, and the count of pho_thong sentences. Charts: benchmark20 + user_1990_nam + the owner's chart.
//   node tools/interpret/bazi_depth.ts [--print <fixture.json>]
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { proseBazi } from '../../src/interpret/prose/bazi.ts';
import { checkedOnly } from '../../src/interpret/prose/checked.ts';
import { seedOf, PROSE_VERSION } from '../../src/interpret/prose/chapter.ts';
import type { ChartInput, Knowledge } from '../../src/interpret/types.ts';
import type { ProseParagraph } from '../../src/interpret/prose/realize.ts';

const ROOT = join(import.meta.dirname, '..', '..');
const FX = join(ROOT, 'src', 'interpret', 'test', 'fixtures');
const K: Knowledge = JSON.parse(readFileSync(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'), 'utf8'));

export function baziReader(c: ChartInput, k: Knowledge = K) {
  return checkedOnly(proseBazi(c, k, seedOf(c), PROSE_VERSION, true) as Parameters<typeof checkedOnly>[0]) as ReturnType<typeof proseBazi>;
}
/** a đại vận paragraph: one that tells one luck pillar (its trace step starts "luck:") */
const isLuck = (p: ProseParagraph) => p.sentences.some(s => (s.trace.step ?? '').startsWith('luck:'))
  || /^(Đại vận \S+ \S+ bắt đầu|Từ \d+ tuổi \(khoảng năm \d+\), đại vận)/.test(p.sentences[0]?.text ?? '');   // the paragraphs before Track C

export function stats(c: ChartInput, k: Knowledge = K) {
  const o = baziReader(c, k);
  const per: Record<string, number> = {};
  for (const [id, ps] of Object.entries(o.chapters ?? {})) per[id] = (ps as ProseParagraph[]).reduce((a, p) => a + p.sentences.length, 0);
  // per luck pillar (REVIEW-19 W6): its short paragraph and its Đọc sâu together, keyed by the trace step "luck:<n>" (the short paragraph joins
  // the pillar's head to its verdict, and the gods and growth stage moved to Đọc sâu)
  const lp = Object.values(o.chapters ?? {}).flat().filter(isLuck) as ProseParagraph[];
  const key = (p: ProseParagraph) => p.sentences.map(s => s.trace.step ?? '').find(x => x.startsWith('luck:')) ?? p.sentences[0]?.text ?? '';
  const byLuck = new Map<string, ProseParagraph[]>();
  for (const p of lp) (byLuck.get(key(p)) ?? byLuck.set(key(p), []).get(key(p))!).push(p);
  const luck = [...byLuck.values()];
  const luckSourced = luck.filter(ps => ps.flatMap(p => p.sentences).filter(s => s.trace.basis === 'sach' || s.trace.basis === 'tinh_toan').length >= 2).length;
  const all = Object.values(o.chapters ?? {}).flat().flatMap(p => (p as ProseParagraph).sentences);
  return { per, total: all.length, luck: luck.length, luckSourced, phoThong: all.filter(s => s.trace.basis === 'pho_thong').length };
}

if (import.meta.main) {
  const i = process.argv.indexOf('--print');
  if (i > 0) {
    const c: ChartInput = JSON.parse(readFileSync(process.argv[i + 1], 'utf8'));
    const o = baziReader(c);
    for (const [id, ps] of Object.entries(o.chapters ?? {})) {
      console.log(`\n## ${id}`);
      for (const p of ps as ProseParagraph[]) console.log((p.lead ? `**${p.lead}** · ` : '') + p.sentences.map(s => `${s.text} [${s.trace.basis}]`).join(' ') + '\n');
    }
  } else {
    const bench = JSON.parse(readFileSync(join(FX, 'benchmark20.json'), 'utf8')) as Array<{ facts?: ChartInput } & ChartInput>;
    const charts: Array<[string, ChartInput]> = [['user_1990_nam', JSON.parse(readFileSync(join(FX, 'user_1990_nam.json'), 'utf8'))],
      ['ref_2002_01_09', JSON.parse(readFileSync(join(FX, 'ref_2002_01_09_kl.json'), 'utf8'))], ...bench.map((b, j) => [`bench${j}`, b.facts ?? b] as [string, ChartInput])];
    let L = 0, LS = 0, PT = 0;
    const sum: Record<string, number> = {};
    for (const [lab, c] of charts) {
      const s = stats(c); L += s.luck; LS += s.luckSourced; PT += s.phoThong;
      for (const [k2, v] of Object.entries(s.per)) sum[k2] = (sum[k2] ?? 0) + v;
      if (!lab.startsWith('bench')) console.log(lab, JSON.stringify(s));
    }
    const n = charts.length - 2;
    console.log('benchmark20 mean sentences/chapter', Object.fromEntries(Object.entries(sum).map(([k2, v]) => [k2, +(v / charts.length).toFixed(1)])));
    console.log(`đại vận paragraphs with ≥2 sách/tính toán sentences: ${LS}/${L} (${L ? Math.round(100 * LS / L) : 0}%); pho_thong sentences: ${PT}; charts ${n}+2`);
  }
}
