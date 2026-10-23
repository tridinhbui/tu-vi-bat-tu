// Trigger atoms: the chart facts a rule's condition actually USED on this chart (port of trigger_atoms in the evidence engine,
// engine/tvbt/reasoning/conclusions.py on branch feat/interp-engine-audit). Two readings are "the same evidence" when their atoms
// coincide; one is "more specific" when its atoms strictly contain the other's. Absences (`not`) contribute nothing: an absence is a
// condition, not a fact of the chart; for `any`, only the satisfied branches count.
import { evaluate, resolvePalace, type World } from '../dsl.ts';
import type { Expr, Facts } from '../types.ts';

export type AtomKind = 'star' | 'hoa' | 'dignity' | 'tuan_triet' | 'branch' | 'vcd' | 'than' | 'chart' | 'derived' | 'count';
export interface Atom { kind: AtomKind; name: string; palace: string | null; value?: unknown }

export const CAT = ['Tả Phụ', 'Hữu Bật', 'Văn Xương', 'Văn Khúc', 'Thiên Khôi', 'Thiên Việt'];
export const SAT = ['Kình Dương', 'Đà La', 'Hỏa Tinh', 'Linh Tinh', 'Địa Không', 'Địa Kiếp'];
/** Facts fixed by the birth year and sex alone: every chart of that year and sex has them. */
export const GENERIC = new Set(['chart.year_branch', 'chart.year_stem', 'chart.can_chi_relation', 'chart.year_polarity', 'chart.gender', 'chart.am_duong_ly']);

const ROLES = ['self', 'opp', 'trine1', 'trine2', 'flank_prev', 'flank_next', 'nhi_hop'];
const TP = ['self', 'trine1', 'trine2', 'opp'];
const STAR_ROLES: Record<string, string[]> = {
  'palace.own_stars': ['self'], 'palace.own_major_stars': ['self'],
  'palace.tam_phuong_stars': TP, 'palace.tam_phuong_majors': TP, 'palace.rel.tp_stars': TP, 'palace.rel.tp_majors': TP,
  'palace.neighbor_stars': ['flank_prev', 'flank_next'], 'palace.neighbor_majors': ['flank_prev', 'flank_next'], 'palace.rel.flank_stars': ['flank_prev', 'flank_next'],
  'palace.rel.trine_stars': ['trine1', 'trine2'], 'palace.rel.trine_majors': ['trine1', 'trine2'],
};
const HOA_ROLES: Record<string, string[]> = { 'palace.tu_hoa': ['self'], 'palace.tam_phuong_tu_hoa': TP, 'palace.rel.tp_hoa': TP, 'palace.rel.trine_hoa': ['trine1', 'trine2'] };
for (const r of ROLES) { STAR_ROLES[`palace.rel.${r}_stars`] = [r]; STAR_ROLES[`palace.rel.${r}_majors`] = [r]; HOA_ROLES[`palace.rel.${r}_hoa`] = [r]; }

const relNames = (f: Facts) => (f['palace.rel_names'] ?? {}) as Record<string, string>;
const listHas = (v: unknown, x: unknown) => Array.isArray(v) && v.includes(x);
function palacesOf(item: string, roles: string[], f: Facts, suffix: 'stars' | 'hoa'): string[] {
  const out: string[] = [];
  for (const r of roles) { const n = relNames(f)[r]; if (n && listHas(f[`palace.rel.${r}_${suffix}`], item) && !out.includes(n)) out.push(n); }
  return out;
}

function leafAtoms(fact: string, op: string, value: unknown, f: Facts, here: string | null): Atom[] {
  if (fact === 'palace.name') return [];
  const vals = Array.isArray(value) ? value : [value], got = f[fact];
  const isContains = op === 'contains' || op === 'contains_any' || op === 'contains_all';
  if (STAR_ROLES[fact] && isContains) {
    return vals.filter(v => listHas(got, v)).flatMap(s => { const ps = palacesOf(s as string, STAR_ROLES[fact], f, 'stars'); return (ps.length ? ps : [null]).map(p => ({ kind: 'star' as const, name: s as string, palace: p })); });
  }
  if (HOA_ROLES[fact] && isContains) {
    return vals.filter(v => listHas(got, v)).flatMap(h => { const ps = palacesOf(h as string, HOA_ROLES[fact], f, 'hoa'); return (ps.length ? ps : [null]).map(p => ({ kind: 'hoa' as const, name: h as string, palace: p })); });
  }
  if (fact.startsWith('palace.dignity@')) fact = `palace.dignity.${fact.slice(fact.indexOf('.', 15) + 1)}`;
  if (fact.startsWith('palace.dignity.') || fact.startsWith('palace.dignity_rank.')) {
    const star = fact.split('.').slice(2).join('.');
    return [{ kind: 'dignity', name: star, palace: here, value: f[`palace.dignity.${star}`] ?? got }];
  }
  if (fact.startsWith('palace.tp_rank.')) {
    const star = fact.split('.').slice(2).join('.');
    return [{ kind: 'dignity', name: star, palace: palacesOf(star, TP, f, 'stars')[0] ?? here, value: got }];
  }
  if ((fact === 'palace.tuan' || fact === 'palace.triet') && got) return [{ kind: 'tuan_triet', name: fact.endsWith('tuan') ? 'Tuần' : 'Triệt', palace: here }];
  if ((fact === 'palace.rel.opp_tuan' || fact === 'palace.rel.opp_triet') && got) return [{ kind: 'tuan_triet', name: fact.endsWith('tuan') ? 'Tuần' : 'Triệt', palace: relNames(f).opp ?? null }];
  if (fact === 'palace.branch') return [{ kind: 'branch', name: 'vị trí', palace: here, value: got }];
  if (fact === 'palace.has_no_major' && got) return [{ kind: 'vcd', name: 'vô chính diệu', palace: here }];
  if (fact === 'palace.is_than' && got) return [{ kind: 'than', name: 'Thân', palace: here }];
  if (fact.startsWith('chart.') || fact.startsWith('bazi.')) return [{ kind: 'chart', name: fact, palace: null, value: got }];
  if (fact.startsWith('derived.')) return [{ kind: 'derived', name: fact, palace: here, value: got }];
  if (fact.startsWith('palace.khi.') && typeof got === 'number') {
    const grp = fact.includes('.sat_') ? SAT : CAT;
    const roles = ({ self: ['self'], tp: TP, flank: ['flank_prev', 'flank_next'] } as Record<string, string[]>)[fact.slice(fact.lastIndexOf('_') + 1)] ?? ['self'];
    const found = grp.flatMap(s => palacesOf(s, roles, f, 'stars').map(p => ({ kind: 'star' as const, name: s, palace: p })));
    return found.length ? found : [{ kind: 'count', name: fact, palace: here, value: got }];
  }
  return [{ kind: 'count', name: fact, palace: here, value: got }];
}

export function triggerAtoms(expr: Expr, f: Facts, world?: World, here: string | null = null): Atom[] {
  if (evaluate(expr, f, world) !== true) return [];
  if ('all' in expr) return expr.all.flatMap(e => triggerAtoms(e, f, world, here));
  if ('any' in expr) return expr.any.filter(e => evaluate(e, f, world) === true).flatMap(e => triggerAtoms(e, f, world, here));
  if ('count' in expr) return expr.count.filter(e => evaluate(e, f, world) === true).flatMap(e => triggerAtoms(e, f, world, here));
  if ('not' in expr) return [];
  if ('ref' in expr) {
    const name = resolvePalace(expr.ref.palace, f), other = world && name ? world(name) : null;
    return other ? leafAtoms(expr.ref.fact, expr.operator ?? 'eq', expr.value, other, name) : [];
  }
  return leafAtoms(expr.fact, expr.operator ?? 'eq', expr.value, f, here);
}

/** Identity of an atom for comparing evidence: a dignity folds into its star (the star's presence is the fact; brightness is its quality). */
export function atomKey(a: Atom): string {
  return a.kind === 'dignity' ? `star|${a.name}|${a.palace}` : `${a.kind}|${a.name}|${a.palace}`;
}
/** The non-generic atom keys of a reading: two readings with equal signatures rest on the same chart facts. */
export function signature(atoms: Atom[]): Set<string> {
  return new Set(atoms.filter(a => !(a.kind === 'chart' && GENERIC.has(a.name))).map(atomKey));
}
export type Nesting = 'same' | 'narrower' | 'broader' | 'disjoint' | 'overlap';
/** How reading A's evidence relates to B's: 'narrower' means A needs everything B needs and more (A is the more specific reading). */
export function nesting(a: Set<string>, b: Set<string>): Nesting {
  const aInB = [...a].every(x => b.has(x)), bInA = [...b].every(x => a.has(x));
  if (aInB && bInA) return 'same';
  if (bInA) return 'narrower';
  if (aInB) return 'broader';
  return [...a].some(x => b.has(x)) ? 'overlap' : 'disjoint';
}
