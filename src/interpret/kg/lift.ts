// Lift (prose plan §4.1): fired findings -> concept assertions, through the reviewed rule→concept links in knowledge.kg.ruleConcepts
// (engine/data/kg/rule_concepts.json). No text matching at runtime: a rule with no link asserts nothing. Each assertion carries the
// trigger atoms its rule stood on, so the resolver can compare evidence.
import type { World } from '../dsl.ts';
import type { Facts, Finding, Knowledge, Rule } from '../types.ts';
import { signature, triggerAtoms, type Atom } from './atoms.ts';

export type Stance = 'affirms' | 'weakens';
export type Strength = 'tendency' | 'potential' | 'condition';
export interface RuleConcept {
  asserts: Array<{ concept: string; stance: Stance; strength?: Strength }>;
  kind?: 'meaning' | 'formation' | 'classification'; pol?: '+' | '-'; src: 'auto' | 'manual'; review: 'draft' | 'approved';
  /** độ số modifiers (season, hour, đắc chính, gốc–ngọn): they add up, two additive assertions never oppose (system convention) */
  additive?: boolean;
}
export interface Assertion {
  key: string; ruleId: string; subject: string; palace: string | null; concept: string; stance: Stance; strength: Strength;
  effect: Finding['effect']; atoms: Atom[]; sig: Set<string>; cites: string[]; review: RuleConcept['review']; additive: boolean;
}
/** Rules that fired but name a cách or a grouping: no concept, kept for the evidence panel. */
export interface Labelled { ruleId: string; subject: string; palace: string | null; kind: 'formation' | 'classification'; pol?: '+' | '-'; cites: string[] }

export function lift(findings: Finding[], k: Knowledge, base: Record<string, Facts>, opts: { includeDraftRules?: boolean } = {}):
  { assertions: Assertion[]; labelled: Labelled[]; unlinked: string[] } {
  const links = k.kg?.ruleConcepts ?? {}, rules = new Map<string, Rule>(k.rules.map(r => [r.id, r]));
  const world: World = n => base[`palace:${n}`] ? { ...(base.chart ?? {}), ...base[`palace:${n}`] } : null;
  const out = { assertions: [] as Assertion[], labelled: [] as Labelled[], unlinked: [] as string[] };
  for (const f of findings) {
    if (f.basis !== 'verified' && !opts.includeDraftRules) continue;
    const rule = rules.get(f.ruleId)!, link = links[f.ruleId];
    if (!link) { out.unlinked.push(f.ruleId); continue; }
    if (link.kind === 'formation' || link.kind === 'classification') {
      out.labelled.push({ ruleId: f.ruleId, subject: f.subject, palace: f.palace, kind: link.kind, pol: link.pol, cites: rule.cites });
    }
    const facts = { ...(base.chart ?? {}), ...(base[f.subject] ?? {}) };
    const atoms = triggerAtoms(rule.conditions, facts, world, f.palace), sig = signature(atoms);
    for (const a of link.asserts) {
      out.assertions.push({ key: `${f.ruleId}|${f.subject}|${a.concept}`, ruleId: f.ruleId, subject: f.subject, palace: f.palace, concept: a.concept,
        stance: a.stance, strength: a.strength ?? 'tendency', effect: f.effect, atoms, sig, cites: rule.cites, review: link.review, additive: !!link.additive });
    }
  }
  return out;
}
