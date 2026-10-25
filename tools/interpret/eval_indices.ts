// Agreement of the period charts with the books and with the reading (indices-3.0.0, owner's plan of 2026-10-24), over corpus1000:
//   direction   a period's level side (above / below "Trung bình") against the side of its book items — never forced to 0: a year may follow
//               its đại vận against its own palaces, and the words then say so;
//   triad       decades in the Thái Tuế – Quan Phù – Bạch Hổ triad (KL p.233) drawn below "Trung bình", and whether their words explain it;
//   evidence    the share of periods with no book evidence ("chưa đủ căn cứ") and of months with no level of their own;
//   year/decade years on the other side of "Trung bình" from their decade, and whether their words say why;
//   months      distinct levels per year, months equal to the year's level;
//   radar       the radar side of Quan Lộc, Tài Bạch, Điền Trạch, Phu Thê against the ledger verdict of its domain.
//   node tools/interpret/eval_indices.ts [charts]      (the years and months walked with the default tiểu hạn school, KL pp.39-40)
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import { computeIndices, TRIAD_RULES, type IndexNorms, type Item } from '../../src/interpret/indices.ts';
import { buildLedger } from '../../src/interpret/reason/ledger.ts';
import { infer } from '../../src/interpret/prose/chapter.ts';
import type { Knowledge } from '../../src/interpret/types.ts';

const ROOT = join(import.meta.dirname, '..', '..');
const K: Knowledge = JSON.parse(readFileSync(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'), 'utf8'));
const N: IndexNorms = JSON.parse(readFileSync(join(ROOT, 'engine', 'data', 'kg', 'index_norms.json'), 'utf8'));
const corpus = JSON.parse(gunzipSync(readFileSync(join(ROOT, 'src', 'interpret', 'test', 'fixtures', 'corpus1000.json.gz'))).toString('utf8'));
const LIMIT = Number(process.argv[2] ?? corpus.length);
const r3 = (x: number) => Math.round(x * 1000) / 1000;
const SRC = (i: Item) => i.basis === 'sach' || i.basis === 'sach_dien_giai';
const bookSide = (xs: Item[]) => Math.sign(r3(xs.filter(SRC).reduce((a, i) => a + (i.side === 'support' ? i.w : -i.w), 0)));
const side = (level: number) => Math.sign(level - 2);
const RADAR: Record<string, string> = { cong_danh: 'Quan Lộc', 'tai_loc.kiem': 'Tài Bạch', 'tai_loc.tich_luy': 'Điền Trạch', hon_nhan: 'Phu Thê' };
const ledgerSide = (v: { verdict: string; base: '+' | '-' | null }) => v.verdict === 'thuan' ? 1 : v.verdict === 'tro_ngai' ? -1
  : v.base === '+' ? 1 : v.base === '-' ? -1 : v.verdict === 'hai_mat' || v.verdict === 'chua_phan_xu' ? 0 : null;

const c: Record<string, number> = {};
const inc = (k: string, n = 1) => { c[k] = (c[k] ?? 0) + n; };
const levels = { decade: [0, 0, 0, 0, 0], year: [0, 0, 0, 0, 0], month: [0, 0, 0, 0, 0] };
for (const ch of corpus.slice(0, LIMIT)) {
  const I = computeIndices(ch.facts, K, N, 10, { tieuHanRule: 'KL' });
  for (const d of I.decades) {
    inc('dec');
    if (d.insufficient) { inc('dec.insufficient'); if (d.level !== 2) inc('dec.insufficient_not_middle'); continue; }
    levels.decade[d.level]++;
    const b = bookSide(d.items);
    if (b && side(d.level) === -b) { inc('dec.against_book'); if (/nghiêng về|tam hợp Thái Tuế/.test(d.text.at(-1)!)) inc('dec.against_book_explained'); }
    if (b && side(d.level) === 0) inc('dec.book_sided_middle');
    if (d.items.some(i => TRIAD_RULES.has(i.id))) {
      inc('dec.triad');
      if (d.level <= 1) { inc('dec.triad_low'); if (d.text.at(-1)!.includes('tam hợp Thái Tuế')) inc('dec.triad_low_explained'); }
    }
  }
  for (const y of I.years) {
    inc('yr');
    if (y.insufficient) { inc('yr.insufficient'); continue; }
    levels.year[y.level]++;
    const own = bookSide(y.items);
    if (own && side(y.level) === -own) inc('yr.against_own_palaces');
    const dec = y.decade === null ? null : I.decades[y.decade];
    if (dec && !dec.insufficient && side(dec.level) * side(y.level) < 0) { inc('yr.other_side_of_decade'); if (y.text.at(-1)!.includes('khác chiều với chặng')) inc('yr.other_side_explained'); }
    if (dec && dec.palace === y.palace) inc('yr.same_palace');
  }
  if (I.months) {
    const yv = I.years.find(y => y.current)!;
    inc('mo.years'); inc('mo.n', 12);
    const ls = I.months.months.filter(m => m.level !== null).map(m => m.level!);
    inc('mo.undetermined', 12 - ls.length); inc('mo.same_as_year', ls.filter(l => l === yv.level).length); inc('mo.distinct', new Set(ls).size);
    for (const l of ls) levels.month[l]++;
  }
  if ((c.charts = (c.charts ?? 0) + 1) <= 300) {
    // the radar against the ledger (the first 300 charts: the ledger runs the whole reasoner)
    const L = buildLedger(ch.facts, K, infer(ch.facts, K).resolved);
    for (const v of L.domains) {
      const pal = RADAR[v.id], want = ledgerSide(v);
      if (!pal || want === null) continue;
      const p = I.palaces.find(x => x.palace === pal)!, d = p.support - p.limit, got = d > 0.15 ? 1 : d < -0.15 ? -1 : 0;
      inc('radar.n'); if (got === want) inc('radar.same'); else if (got * want < 0) inc('radar.opposite');
    }
  }
}
const pct = (a: string, b: string) => `${c[a] ?? 0} / ${c[b] ?? 0} (${r3(100 * (c[a] ?? 0) / (c[b] || 1))} %)`;
const share = (h: number[]) => { const n = h.reduce((a, x) => a + x, 0) || 1; return h.map(x => `${r3(100 * x / n)} %`).join(' / '); };
console.log(JSON.stringify({
  charts: c.charts,
  decade: { insufficient: pct('dec.insufficient', 'dec'), insufficient_not_middle: c['dec.insufficient_not_middle'] ?? 0, against_book: pct('dec.against_book', 'dec'), against_book_explained: pct('dec.against_book_explained', 'dec.against_book'),
    book_sided_but_middle: pct('dec.book_sided_middle', 'dec'), triad_low: pct('dec.triad_low', 'dec.triad'), triad_low_explained: pct('dec.triad_low_explained', 'dec.triad_low'), levels: share(levels.decade) },
  year: { insufficient: pct('yr.insufficient', 'yr'), against_own_palaces: pct('yr.against_own_palaces', 'yr'), other_side_of_decade: pct('yr.other_side_of_decade', 'yr'),
    other_side_explained: pct('yr.other_side_explained', 'yr.other_side_of_decade'), levels: share(levels.year) },
  month: { undetermined: pct('mo.undetermined', 'mo.n'), same_as_year: pct('mo.same_as_year', 'mo.n'), distinct_per_year: r3((c['mo.distinct'] ?? 0) / (c['mo.years'] || 1)), levels: share(levels.month) },
  radar: { same: pct('radar.same', 'radar.n'), opposite: pct('radar.opposite', 'radar.n') },
}, null, 1));
