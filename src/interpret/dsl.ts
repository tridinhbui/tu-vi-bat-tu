// Rule-condition evaluator: a faithful port of engine/tvbt/knowledge/dsl.py (three-valued logic; a missing fact is UNKNOWN, never false).
// Parity with the Python engine is enforced by test/engine.test.ts over the regression fixtures.
import type { Expr, Facts, Tri } from './types.ts';

const ROLES = new Set(['self', 'opp', 'trine1', 'trine2', 'flank_prev', 'flank_next', 'nhi_hop']);
export type World = (palace: string) => Facts | null;

function eq(a: unknown, b: unknown): boolean {
  if (Array.isArray(a) && Array.isArray(b)) return a.length === b.length && a.every((x, i) => eq(x, b[i]));
  return a === b;
}
function has(container: unknown, item: unknown): boolean | null {
  if (typeof container === 'string') return typeof item === 'string' ? container.includes(item) : null;   // Python: substring
  if (Array.isArray(container)) return container.some(x => eq(x, item));
  if (container && typeof container === 'object') return typeof item === 'string' ? item in (container as object) : null;
  return null;                                                                                              // TypeError -> unknown
}
function num(v: unknown): number | null {
  return typeof v === 'number' ? v : typeof v === 'boolean' ? (v ? 1 : 0) : null;
}

export function compare(got: unknown, op: string, want: unknown): Tri {
  switch (op) {
    case 'eq': return eq(got, want);
    case 'ne': return !eq(got, want);
    case 'in': return has(want, got);
    case 'not_in': { const h = has(want, got); return h === null ? null : !h; }
    case 'gte': case 'lte': {
      const a = num(got), b = num(want);
      if (a === null || b === null) return null;
      return op === 'gte' ? a >= b : a <= b;
    }
    case 'contains': return has(got, want);
    case 'not_contains': { const h = has(got, want); return h === null ? null : !h; }
    case 'contains_any': { if (!Array.isArray(want)) return null; const r = want.map(w => has(got, w)); return r.includes(null) && !r.includes(true) ? null : r.includes(true); }
    case 'contains_all': { if (!Array.isArray(want)) return null; const r = want.map(w => has(got, w)); return r.includes(false) ? false : r.includes(null) ? null : true; }
  }
  throw new Error(`unknown operator ${op}`);
}

export function resolvePalace(target: string, facts: Facts): string | null {
  if (ROLES.has(target)) {
    const names = facts['palace.rel_names'];
    return names && typeof names === 'object' ? ((names as Record<string, string>)[target] ?? null) : null;
  }
  return target;
}

export function evaluate(expr: Expr, facts: Facts, world?: World): Tri {
  if ('all' in expr) { const v = expr.all.map(e => evaluate(e, facts, world)); return v.includes(false) ? false : v.includes(null) ? null : true; }
  if ('any' in expr) { const v = expr.any.map(e => evaluate(e, facts, world)); return v.includes(true) ? true : v.includes(null) ? null : false; }
  if ('not' in expr) { const v = evaluate(expr.not, facts, world); return v === null ? null : !v; }
  if ('count' in expr) {
    const v = expr.count.map(e => evaluate(e, facts, world));
    const yes = v.filter(x => x === true).length, unk = v.filter(x => x === null).length, op = expr.operator ?? 'eq';
    const answers = new Set<Tri>();
    for (let n = yes; n <= yes + unk; n++) answers.add(compare(n, op, expr.value));
    return answers.size === 1 ? [...answers][0] : null;
  }
  if ('ref' in expr) {
    if (!world) return null;
    const name = resolvePalace(expr.ref.palace, facts);
    const other = name ? world(name) : null;
    if (!other || !(expr.ref.fact in other)) return null;
    return compare(other[expr.ref.fact], expr.operator ?? 'eq', expr.value);
  }
  if (!(expr.fact in facts)) return null;
  return compare(facts[expr.fact], expr.operator ?? 'eq', expr.value);
}

/** Leaves of a condition that are TRUE on these facts (refs and negations are not expanded): what the chart actually satisfied. */
export function trueLeaves(expr: Expr, facts: Facts): Array<{ fact: string; operator: string; value: unknown }> {
  if ('fact' in expr) return evaluate(expr, facts) === true ? [{ fact: expr.fact, operator: expr.operator ?? 'eq', value: expr.value }] : [];
  if ('ref' in expr || 'not' in expr) return [];
  const sub = 'all' in expr ? expr.all : 'any' in expr ? expr.any : 'count' in expr ? expr.count : [];
  return sub.flatMap(e => trueLeaves(e, facts));
}

/** Leaves under a satisfied `not` (the inner condition is false on the chart): what the rule requires to be ABSENT, for the rendered
 *  condition ("Tử Vi tại Mệnh, không có Tả Phụ và Hữu Bật hội chiếu"). Only `not` nodes on a satisfied path are followed. */
export function absentLeaves(expr: Expr, facts: Facts): Array<{ fact: string; operator: string; value: unknown }> {
  if ('fact' in expr || 'ref' in expr) return [];
  if ('not' in expr) return evaluate(expr.not, facts) === false ? leaves(expr.not).filter(l => !l.fact.startsWith('not:') && !l.fact.startsWith('ref:')) : [];
  const sub = 'all' in expr ? expr.all : 'any' in expr ? expr.any.filter(e => evaluate(e, facts) === true) : 'count' in expr ? expr.count : [];
  return sub.flatMap(e => absentLeaves(e, facts));
}

/** All leaves of a condition (fact, operator, value), for provenance and independence keys. */
export function leaves(expr: Expr): Array<{ fact: string; operator: string; value: unknown }> {
  if ('fact' in expr) return [{ fact: expr.fact, operator: expr.operator ?? 'eq', value: expr.value }];
  if ('ref' in expr) return [{ fact: `ref:${expr.ref.palace}:${expr.ref.fact}`, operator: expr.operator ?? 'eq', value: expr.value }];
  if ('not' in expr) return leaves(expr.not).map(l => ({ ...l, fact: 'not:' + l.fact }));
  const sub = 'all' in expr ? expr.all : 'any' in expr ? expr.any : 'count' in expr ? expr.count : [];
  return sub.flatMap(leaves);
}
