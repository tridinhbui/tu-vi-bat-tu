// Borrowed chính tinh for a palace with none (owner's decision 2026-10-23, Toàn Thư p.18: "bản phương không có chính tinh tức không có chủ
// thì phải mượn sao ở cung xung chiếu làm chủ"). Every vô chính diệu palace whose opposite palace holds chính tinh is read a second time with
// those stars as its own: the palace's facts take the opposite palace's chính tinh, their brightness and that palace's branch (a borrowed star
// keeps the brightness of where it stands). A rule that fires only in this borrowed reading, and stands on a borrowed star, is a BORROWED
// reading: lower confidence than a seated star, always told as "mượn … từ cung …" (prose/luan_deep.ts), never in the ledger, the synthesis or
// the main argument. Its atoms of the borrowed stars are put back where the stars stand (the opposite palace), so no sentence can seat them.
import type { ChartInput, Facts, Knowledge } from '../types.ts';
import { run } from '../engine.ts';
import { lift } from '../kg/lift.ts';
import { resolve, type Resolved } from '../kg/resolve.ts';

export const BORROW_CITE = 'TT p.18';
export interface Borrowed extends Resolved { borrowed: { from: string; stars: string[] } }

/** The vô chính diệu palaces of the chart and the palace each borrows from. */
export function vcdBorrows(chart: ChartInput): Array<{ palace: string; from: string; stars: string[] }> {
  const byIdx = new Map(chart.palaces.map(p => [p.branch_index, p]));
  return chart.palaces.filter(p => !p.major_stars.length).map(p => ({ p, o: byIdx.get((p.branch_index + 6) % 12)! }))
    .filter(x => x.o && x.o.major_stars.length).map(x => ({ palace: x.p.name, from: x.o.name, stars: [...x.o.major_stars] }));
}

export function borrowedReadings(chart: ChartInput, k: Knowledge, natural: Resolved[]): Borrowed[] {
  const vcd = vcdBorrows(chart);
  if (!vcd.length) return [];
  const base: Record<string, Facts> = { ...chart.base };
  for (const v of vcd) {
    const own = chart.base[`palace:${v.palace}`] ?? {}, opp = chart.base[`palace:${v.from}`] ?? {};
    const f: Facts = { ...own, 'palace.own_major_stars': [...v.stars], 'palace.has_no_major': false, 'palace.rel.self_majors': [...v.stars],
      'palace.rel.self_stars': [...((own['palace.rel.self_stars'] as string[] | undefined) ?? []), ...v.stars], 'palace.branch': opp['palace.branch'] };
    for (const s of v.stars) for (const key of [`palace.dignity.${s}`, `palace.dignity_rank.${s}`]) if (key in opp) f[key] = opp[key];
    base[`palace:${v.palace}`] = f;
  }
  const subjects = new Map(vcd.map(v => [`palace:${v.palace}`, v]));
  const findings = run(k.rules, k.sources, base).findings.filter(f => subjects.has(f.subject));
  const fired = new Set(natural.map(r => `${r.ruleId}|${r.subject}`));
  const fresh = findings.filter(f => !fired.has(`${f.ruleId}|${f.subject}`));
  const { assertions } = lift(fresh, k, base);
  const kept = assertions.filter(a => {
    const v = subjects.get(a.subject)!;
    // it must stand on a borrowed star of its own palace, and on no borrowed star of another vô chính diệu palace
    return a.atoms.some(x => x.kind === 'star' && x.palace === v.palace && v.stars.includes(x.name))
      && !a.atoms.some(x => (x.kind === 'star' || x.kind === 'dignity') && x.palace !== v.palace && vcd.some(w => w.palace === x.palace && w.stars.includes(x.name)));
  });
  const { resolved } = resolve(kept, k);
  return resolved.map(r => {
    const v = subjects.get(r.subject)!;
    const atoms = r.atoms.map(x => (x.kind === 'star' || x.kind === 'dignity') && x.palace === v.palace && v.stars.includes(x.name) ? { ...x, palace: v.from } : x);
    return { ...r, atoms, cites: [...r.cites, BORROW_CITE], borrowed: { from: v.from, stars: v.stars } };
  });
}
