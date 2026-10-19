// Resolve (prose plan §2, fixed order): apply declared rule relations to the lifted assertions.
//   1. a relation with basis 'sach' (rescues / qualifies / overrides) applies when both of its rules fired on the same subject;
//   2. otherwise a relation with basis 'he_thong' (narrows: the more specific evidence wins) applies — a system convention, labelled;
//   3. opposed assertions with no relation stay 'holds' on both sides and are reported as open tensions (both_hold / unresolved);
//   4. a relation never makes a rule fire or stop firing; it only changes how the assertion may be voiced.
// Every status change records which relation, rule, basis and page caused it, for the evidence panel.
import type { Concept, Knowledge } from '../types.ts';
import type { Assertion } from './lift.ts';

export type RelationType = 'rescues' | 'qualifies' | 'overrides' | 'narrows' | 'both_hold' | 'unresolved';
export interface KgRelation {
  id: string; type: RelationType; from: string; to: string[]; effect: 'soften' | 'weaken' | 'cancel' | 'none';
  basis: 'sach' | 'he_thong'; cite?: string; note?: string; review: 'draft' | 'approved'; charts?: number;
}
export type Status = 'holds' | 'softened' | 'weakened' | 'voided' | 'narrowed';
export interface Resolution { relation: string; type: RelationType; byRule: string; basis: KgRelation['basis']; cite?: string }
export interface Resolved extends Assertion { status: Status; by: Resolution[] }
export interface Tension { a: string; b: string; concept: string; kind: 'both_hold' | 'unresolved'; relation?: string }

const STATUS_OF: Record<KgRelation['effect'], Status> = { soften: 'softened', weaken: 'weakened', cancel: 'voided', none: 'holds' };
const RANK: Record<Status, number> = { holds: 0, narrowed: 1, softened: 2, weakened: 2, voided: 3 };

/** Two assertions oppose when they speak of the same concept in opposite stances, or affirm a concept and its opposite. */
export function opposed(a: Assertion, b: Assertion, concepts: Map<string, Concept>): boolean {
  if (a.additive && b.additive) return false;                                       // độ số modifiers add up
  if (a.concept === b.concept) return a.stance !== b.stance;
  if (a.stance !== 'affirms' || b.stance !== 'affirms') return false;
  return concepts.get(a.concept)?.opp === b.concept || concepts.get(b.concept)?.opp === a.concept;
}

export function resolve(asserts: Assertion[], k: Knowledge): { resolved: Resolved[]; tensions: Tension[] } {
  const rels = (k.kg?.relations ?? []) as KgRelation[];
  const concepts = new Map(k.concepts.concepts.map(c => [c.id, c]));
  const fired = new Set(asserts.map(a => `${a.ruleId}|${a.subject}`));
  const resolved: Resolved[] = asserts.map(a => ({ ...a, status: 'holds', by: [] }));
  const apply = (target: Resolved, rel: KgRelation, status: Status) => {
    target.by.push({ relation: rel.id, type: rel.type, byRule: rel.from, basis: rel.basis, cite: rel.cite });
    if (RANK[status] > RANK[target.status]) target.status = status;
  };
  for (const basis of ['sach', 'he_thong'] as const) {
    for (const rel of rels) {
      if (rel.basis !== basis || rel.type === 'both_hold' || rel.type === 'unresolved') continue;
      for (const t of resolved) {
        if (!rel.to.includes(t.ruleId) || !fired.has(`${rel.from}|${t.subject}`)) continue;
        if (basis === 'he_thong' && t.by.some(b => b.basis === 'sach')) continue;      // the book's own word already decided it
        // narrows: only the broader reading's assertions that the narrower one contradicts are touched
        if (rel.type === 'narrows') {
          const narrow = resolved.filter(x => x.ruleId === rel.from && x.subject === t.subject);
          if (!narrow.some(n => opposed(n, t, concepts))) continue;
          apply(t, rel, 'narrowed');
        } else apply(t, rel, STATUS_OF[rel.effect]);
      }
    }
  }
  const tensions: Tension[] = [];
  const decl = new Map<string, KgRelation>();
  for (const r of rels) for (const t of r.to) { decl.set(`${r.from}|${t}`, r); decl.set(`${t}|${r.from}`, r); }
  for (let i = 0; i < resolved.length; i++) for (let j = i + 1; j < resolved.length; j++) {
    const a = resolved[i], b = resolved[j];
    if (a.subject !== b.subject || a.ruleId === b.ruleId || a.status === 'voided' || b.status === 'voided' || !opposed(a, b, concepts)) continue;
    const r = decl.get(`${a.ruleId}|${b.ruleId}`);
    if (r && r.type !== 'both_hold' && r.type !== 'unresolved' && (a.by.length || b.by.length)) continue;   // decided above
    tensions.push({ a: a.key, b: b.key, concept: a.concept, kind: r?.type === 'unresolved' ? 'unresolved' : 'both_hold', relation: r?.id });
  }
  return { resolved, tensions };
}
