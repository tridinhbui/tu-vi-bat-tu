// Discourse (prose plan §4.4): the moves the selection supports, and the paragraph shape. Schemas are tried in library order; among
// the first four that fit, the chart's seed decides, so charts with the same argument do not all read alike. A move the chosen schema
// does not place is not lost: the realizer moves it to the supporting paragraph.
import type { Move, ParagraphSchema } from './types.ts';
import type { Selection } from './select.ts';
import { fnv } from './micro.ts';

export function presentMoves(s: Selection): Set<Move> {
  const m = new Set<Move>();
  if (s.vcd && s.nucleus) m.add('BORROW');
  else if (s.nucleus) m.add('ANCHOR');
  if (s.nucleus && s.elaborate) m.add('ELABORATE');
  if (s.turn.length) m.add('TURN');
  if (s.rescue) m.add('RESCUE');
  if (s.tension && (s.tension.pos || s.tension.neg)) m.add('TENSION');
  if (s.timing) m.add('TIMING');
  if (s.satellites.length) m.add('SATELLITE');
  if (s.nucleus) m.add('VALUE');
  if (s.turn.length || s.tension?.neg) m.add('TRANSFORM');
  return m;
}

export function chooseSchema(schemas: ParagraphSchema[], present: Set<Move>, seed: string): { schema: ParagraphSchema; order: Move[] } {
  const all = schemas.filter(s => s.needs.every(n => present.has(n)) && !(s.forbid ?? []).some(f => present.has(f)));
  const fits = all.length > 1 ? all.filter(s => s.needs.length) : all;          // the fallback only when nothing else fits
  const pool = fits.slice(0, Math.min(4, fits.length));
  const schema = pool[fnv(`${seed}|schema`) % pool.length];
  const order = schema.order.map(o => o.replace('?', '') as Move).filter(m => present.has(m))
    .filter(m => !(m === 'ANCHOR' && present.has('BORROW')));            // vô chính diệu: the borrow frame is the anchor
  return { schema, order };
}
