// Source-cited qualifiers (engine/data/kg/qualifiers.json, page-checked): conditions under which a reading that fired is voided,
// weakened, modified, strengthened or made durable. A qualifier never makes a rule fire or stop firing; it is evaluated next to the
// reading it concerns and reported with its status on the chart. Port of evaluate_qualifiers in the evidence engine.
import { evaluate, type World } from '../dsl.ts';
import type { Expr, Facts } from '../types.ts';
import { triggerAtoms, type Atom } from './atoms.ts';

export type QualifierEffect = 'voids' | 'weakens' | 'modifies' | 'requires_for_durability' | 'strengthens';
export interface Qualifier {
  id: string; effect: QualifierEffect; when: Expr; text_vi: string; source: string; review?: string; scope_vi?: string; open_question_vi?: string;
  target: { palace?: string; palace_in?: string[]; stars_any?: string[]; stars_all?: string[]; aspect?: string; polarity?: string; any_reading?: boolean; skip_if_atom?: string };
}
export interface QualifierHit {
  id: string; effect: QualifierEffect; status: 'met' | 'not_met' | 'unknown'; text: string; onChart: Atom[]; source: string; review: string; question: string | null;
}

/** Whether a qualifier concerns a reading in `palace` resting on `atoms`. Only trigger stars standing IN that palace select it:
 *  a star seen by chiếu is the other palace's business. */
export function applies(q: Qualifier, palace: string | null, atoms: Atom[], aspect = '', polarity = ''): boolean {
  const t = q.target;
  if (palace === null) return false;
  if (t.palace && t.palace !== palace) return false;
  if (t.palace_in && !t.palace_in.includes(palace)) return false;
  if (t.aspect && t.aspect !== aspect) return false;
  if (t.polarity && t.polarity !== polarity) return false;
  if (t.skip_if_atom && atoms.some(a => a.kind === t.skip_if_atom)) return false;
  if (t.any_reading) return true;
  const stars = new Set(atoms.filter(a => (a.kind === 'star' || a.kind === 'dignity') && a.palace === palace).map(a => a.name));
  const all = t.stars_all ?? [], any = t.stars_any ?? [];
  if (!all.length && !any.length) return true;
  return all.every(s => stars.has(s)) && (!any.length || any.some(s => stars.has(s)));
}

export function evaluateQualifiers(qs: Qualifier[], palace: string | null, atoms: Atom[], base: Record<string, Facts>, aspect = '', polarity = ''): QualifierHit[] {
  if (palace === null) return [];
  const fx = base[`palace:${palace}`];
  if (!fx) return [];
  const world: World = n => base[`palace:${n}`] ?? null;
  const out: QualifierHit[] = [];
  for (const q of qs) {
    if (!applies(q, palace, atoms, aspect, polarity)) continue;
    const v = evaluate(q.when, fx, world);
    const status = v === true ? 'met' : v === false ? 'not_met' : 'unknown';
    out.push({ id: q.id, effect: q.effect, status, text: q.text_vi, onChart: v === true ? triggerAtoms(q.when, fx, world, palace) : [],
      source: q.source, review: q.review ?? 'verified', question: status !== 'not_met' ? (q.open_question_vi ?? null) : null });
  }
  return out;
}
