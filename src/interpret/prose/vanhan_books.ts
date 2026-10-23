// The book readings of a đại hạn and of the year (plan 2026-10-23 Đại hạn), from engine/data/kg/van_han_books.json (tools/build_van_han_books.py,
// page-checked): Toàn Thư's nhập hạn verses pp.96-106 on the hạn palace, read with the Tứ Hóa of the hạn's OWN stem (TT p.105 Hóa Lộc / Quyền /
// Khoa); Khảo Luận pp.233-236 — the hạn's chính tinh and hung tinh đắc / hãm, Tuần / Triệt that giải a hãm chính tinh, a hung tinh meeting its
// 'quan thầy', the opening sentence of a Thất Sát / Phá Quân / Tham Lang hạn, the stage of life the palace stands for in the chart's direction;
// Thực Hành p.119 — đại and tiểu hạn on one palace. Data only in, matches out: vanhan.ts voices them.
import type { ChartInput, Decade, Palace } from '../types.ts';
import books from '../../../engine/data/kg/van_han_books.json' with { type: 'json' };

export interface BookLine { id: string; text: string; tone: '' | 'pos' | 'neg'; cite: string; quote: string }
interface Cond { major?: string; star?: string; dig?: string[]; not_dig?: string[]; with_any?: string[]; tp_any?: string[]; tp_any2?: string[]; tp_all?: string[];
  tp_sat?: boolean; tp_sat2?: boolean; tp_cat?: boolean; no_cat?: boolean; no_sat_tp?: boolean; hoa?: string[]; hoa_any?: string[]; hoa3?: boolean; hoa_star_dig?: string[];
  opp_major?: string[]; branch?: string[]; tuoi?: string[]; tp_major_dig?: Record<string, string[]> }
interface Entry { id: string; kind: string; cond: Cond; text: string; tone: '' | 'pos' | 'neg'; book: string; page: number; quote: string }
interface KlLine { text: string; tone: '' | 'pos' | 'neg'; book: string; page: number; quote: string }
const B = books as unknown as { entries: Entry[]; kl: Record<string, KlLine>; quan_thay: Record<string, string> };
const SAT = ['Kình Dương', 'Đà La', 'Địa Không', 'Địa Kiếp', 'Hỏa Tinh', 'Linh Tinh'];
const CAT = ['Tả Phụ', 'Hữu Bật', 'Văn Xương', 'Văn Khúc', 'Thiên Khôi', 'Thiên Việt'];
const GOOD = new Set(['miếu', 'vượng', 'đắc']);
const cite = (x: { book: string; page: number }) => `${x.book} p.${x.page}`;
const joinVi = (xs: string[]) => xs.length <= 1 ? (xs[0] ?? '') : xs.slice(0, -1).join(', ') + ' và ' + xs[xs.length - 1];

function dignityOf(p: Palace, star: string): string | undefined {
  return (p.major_dignity as Record<string, string> | undefined)?.[star] ?? ((p as unknown as { minor_dignity?: Record<string, string> }).minor_dignity ?? {})[star];
}

/** The verses of Toàn Thư that the hạn palace meets, in the data's order; at most `max`, the conditional ones first. */
export function toanThuLines(chart: ChartInput, d: Decade, max = 2): BookLine[] {
  const p = chart.palaces.find(x => x.branch === d.branch)!;
  const byIdx = new Map(chart.palaces.map(x => [x.branch_index, x]));
  const tp = [0, 4, 8, 6].map(o => byIdx.get((p.branch_index + o) % 12)!);
  const opp = byIdx.get((p.branch_index + 6) % 12)!;
  const has = (s: string) => p.stars.includes(s) || p.major_stars.includes(s);
  const tpHas = (s: string) => tp.some(q => q.stars.includes(s) || q.major_stars.includes(s));
  const hoaHere = (h: string) => (d.hoa as Record<string, { star: string; palace: string } | undefined>)[h]?.palace === p.name;
  const tpNames = new Set(tp.map(q => q.name));
  const hoaTp = (h: string) => tpNames.has((d.hoa as Record<string, { palace: string } | undefined>)[h]?.palace ?? '');
  const yb = chart.year_gz.split(' ')[1];
  const ok = (c: Cond) => {
    const s = c.major ?? c.star;
    if (c.major && !p.major_stars.includes(c.major)) return false;
    if (c.star && !p.stars.includes(c.star) && !p.major_stars.includes(c.star)) return false;
    const dg = s ? dignityOf(p, s) : undefined;
    if (c.dig && !(dg && c.dig.includes(dg))) return false;
    if (c.not_dig && dg && c.not_dig.includes(dg)) return false;
    if (c.with_any && !c.with_any.some(has)) return false;
    if (c.tp_any && !c.tp_any.some(tpHas)) return false;
    if (c.tp_any2 && !c.tp_any2.some(tpHas)) return false;
    if (c.tp_all && !c.tp_all.every(tpHas)) return false;
    if (c.tp_sat && !SAT.some(tpHas)) return false;
    if (c.tp_sat2 && SAT.filter(tpHas).length < 2) return false;
    if (c.no_sat_tp && SAT.some(tpHas)) return false;
    if (c.tp_cat && !CAT.some(tpHas)) return false;
    if (c.no_cat && CAT.some(tpHas)) return false;
    if (c.hoa && !c.hoa.every(hoaHere)) return false;
    if (c.hoa_any && !c.hoa_any.some(hoaHere)) return false;
    if (c.hoa3 && !['Hóa Lộc', 'Hóa Quyền', 'Hóa Khoa'].every(hoaTp)) return false;
    if (c.hoa_star_dig) { const st = (d.hoa as Record<string, { star: string } | undefined>)['Hóa Kỵ']?.star; const dd = st ? dignityOf(p, st) : undefined; if (!(dd && c.hoa_star_dig.includes(dd))) return false; }
    if (c.opp_major && !c.opp_major.some(s0 => opp.major_stars.includes(s0))) return false;
    if (c.branch && !c.branch.includes(p.branch)) return false;
    if (c.tuoi && !c.tuoi.includes(yb)) return false;
    if (c.tp_major_dig) for (const [st, lv] of Object.entries(c.tp_major_dig)) { const q = tp.find(x => x.major_stars.includes(st)); if (!q || !lv.includes(dignityOf(q, st) ?? '')) return false; }
    return true;
  };
  const hits = B.entries.filter(e => e.kind === 'tt' && ok(e.cond));
  // a verse whose star another, narrower verse of the same star already reads is left to that one
  const spec = (e: Entry) => Object.keys(e.cond).length;
  const byStar = new Map<string, Entry>();
  for (const e of [...hits].sort((a, b) => spec(b) - spec(a))) { const k = e.cond.major ?? e.cond.star ?? e.cond.hoa?.join('|') ?? e.id; if (!byStar.has(k)) byStar.set(k, e); }
  return [...byStar.values()].sort((a, b) => spec(b) - spec(a)).slice(0, max).map(e => ({ id: `TT_HAN:${e.id}`, text: e.text, tone: e.tone, cite: cite(e), quote: e.quote }));
}

/** Khảo Luận pp.233-236 on the hạn palace: the brightness of its chính tinh (and Tuần / Triệt giải), its hung tinh with their quan thầy, the
 *  opening sentence of a Sát / Phá / Tham hạn, the stage of life of the palace. */
export function khaoLuanLines(chart: ChartInput, d: Decade): { stage?: BookLine; lines: BookLine[] } {
  const p = chart.palaces.find(x => x.branch === d.branch)!;
  const byIdx = new Map(chart.palaces.map(x => [x.branch_index, x]));
  const tp = [0, 4, 8, 6].map(o => byIdx.get((p.branch_index + o) % 12)!);
  const L = (key: string, v: Record<string, string> = {}): BookLine => { const x = B.kl[key]; return { id: `KL_HAN:${key}`, text: x.text.replace(/\{(\w+)\}/g, (_, k) => v[k] ?? ''), tone: x.tone, cite: cite(x), quote: x.quote }; };
  const lines: BookLine[] = [];
  const digs = p.major_stars.map(s => dignityOf(p, s)).filter((x): x is string => !!x);
  if (digs.length && digs.every(x => GOOD.has(x))) lines.push(L('kl233_chinh_tinh_dac'));
  else if (digs.includes('hãm')) {
    const tt = [p.tuan ? 'Tuần' : '', p.triet ? 'Triệt' : ''].filter(Boolean);
    lines.push(tt.length ? L('kl233_chinh_tinh_ham_giai', { tt: joinVi(tt) }) : L('kl233_chinh_tinh_ham'));
  }
  const sats = SAT.filter(s => p.stars.includes(s));
  const good = sats.filter(s => GOOD.has(dignityOf(p, s) ?? '')), bad = sats.filter(s => dignityOf(p, s) === 'hãm');
  const withMaster = good.filter(s => tp.some(q => q.major_stars.includes(B.quan_thay[s])));
  if (withMaster.length) lines.push(L('kl233_quan_thay', { stars: joinVi(withMaster), master: joinVi([...new Set(withMaster.map(s => B.quan_thay[s]))]) }));
  else if (good.length) lines.push(L('kl233_hung_tinh_dac', { stars: joinVi(good) }));
  if (bad.length) lines.push(L('kl233_hung_tinh_ham', { stars: joinVi(bad) }));
  for (const [star, key] of [['Thất Sát', 'kl235_that_sat_open'], ['Phá Quân', 'kl236_pha_quan_open'], ['Tham Lang', 'kl236_tham_lang_open']] as const)
    if (p.major_stars.includes(star)) { lines.push(L(key)); break; }
  const dir = /nghịch/.test(chart.dai_han_direction ?? '') ? 'nghich' : 'thuan';
  const sk = `stage:${dir}:${p.name}`;
  return { lines, ...(B.kl[sk] ? { stage: L(sk) } : {}) };
}

/** Thực Hành p.119: the tiểu hạn of the year falls on the đại hạn's palace. */
export function trungPhung(tieuHanPalace: string | undefined, daiHanPalace: string | undefined): BookLine | null {
  if (!tieuHanPalace || tieuHanPalace !== daiHanPalace) return null;
  const x = B.kl.th119_trung_phung;
  return { id: 'TH_HAN:trung_phung', text: x.text, tone: '', cite: cite(x), quote: x.quote };
}
