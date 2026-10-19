// Prose library lint (prose plan P2): structural checks a card must pass before review. It does not judge style; it guarantees the
// generator can use a card without producing a meta-sentence, an unsupported absolute, a broken slot or a repeated phrasing.
import type { Concept } from '../types.ts';
import type { ConceptCard, ProseLibrary } from './types.ts';

export interface LintIssue { level: 'error' | 'warning'; where: string; msg: string }

/** Words that would turn reader prose back into an evidence report, or claim certainty the books do not give. */
export const META = ['sách ', 'căn cứ', 'quy tắc', 'theo thực hành', 'theo khảo luận', 'theo toàn thư', 'nhận định', 'trang ', 'tr.', 'luận đoán'];
export const ABSOLUTE = ['chắc chắn', 'nhất định', 'suốt đời', 'trọn đời', 'không bao giờ', 'luôn luôn', 'tuyệt đối', 'định mệnh'];
const SLOT = /\{\??([a-zA-Z0-9_.]+)(\|[^{}]*)?\}/g;

const MIN: Record<'+' | '-' | '~', Partial<Record<keyof ConceptCard, number>>> = {
  '+': { pred: 3, behave: 2, soft: 2, value: 2 },
  '-': { turn: 3, soft: 2, mature: 2 },
  '~': { pred: 3, behave: 2 },
};
const FRAGMENTS: Array<keyof ConceptCard> = ['pred', 'turn', 'soft', 'mature', 'value'];

export function lintLibrary(lib: ProseLibrary, concepts: Concept[], required: string[], slots: Record<string, string[]>): LintIssue[] {
  const out: LintIssue[] = [];
  const cmap = new Map(concepts.map(c => [c.id, c]));
  const cards = new Map<string, ConceptCard>();
  const err = (where: string, msg: string) => out.push({ level: 'error', where, msg });
  const warn = (where: string, msg: string) => out.push({ level: 'warning', where, msg });
  const textCheck = (where: string, t: string, allowed: string[]) => {
    const low = ' ' + t.toLowerCase();
    for (const w of META) if (low.includes(' ' + w)) err(where, `meta-language "${w.trim()}": ${t}`);
    for (const w of ABSOLUTE) if (low.includes(w)) err(where, `absolute "${w}": ${t}`);
    for (const m of t.matchAll(SLOT)) if (!allowed.includes(m[1])) err(where, `unknown slot {${m[1]}}: ${t}`);
    if (/\s{2,}|\s[,.;]/.test(t)) err(where, `spacing: ${t}`);
  };

  for (const c of lib.concepts) {
    if (cards.has(c.id)) err(c.id, 'duplicate card');
    cards.set(c.id, c);
    const con = cmap.get(c.id);
    if (!con) { err(c.id, 'card for an unknown concept'); continue; }
    if (!c.np || !c.pron) err(c.id, 'np and pron are required');
    for (const [field, n] of Object.entries(MIN[con.pol])) {
      const have = (c[field as keyof ConceptCard] as string[] | undefined)?.length ?? 0;
      if (have < n!) err(c.id, `${field}: ${have} variant(s), need ${n}`);
    }
    if (c.shadow && !cmap.has(c.shadow)) err(c.id, `shadow ${c.shadow} is not a concept`);
    const seen = new Set<string>();
    for (const f of [...FRAGMENTS, 'behave'] as Array<keyof ConceptCard>) {
      for (const t of (c[f] as string[] | undefined) ?? []) {
        const where = `${c.id}.${f}`;
        if (seen.has(t)) err(where, `repeated variant: ${t}`);
        seen.add(t);
        textCheck(where, t, f === 'behave' ? slots.behave : slots.fragment);
        if (f === 'behave') { if (!/^(\{S\}|\p{Lu})/u.test(t) || !/[.!?]$/.test(t)) err(where, `sentence must start with {S} or a capital and end with a period: ${t}`); }
        else if (/[.!?]$/.test(t) || /^\p{Lu}/u.test(t.replace(/^\{[^}]+\}/, ''))) err(where, `fragment must be lower-case and unpunctuated: ${t}`);
        // the realizer supplies the verb: a pred must not start with 'thường/hay/luôn', a turn not with 'dễ'
        if (f === 'pred' && /^(thường|hay|luôn|dễ) /.test(t)) err(where, `pred follows 'thường': it must not start with its own 'thường/hay/luôn/dễ': ${t}`);
        if (f === 'turn' && /^(dễ|khó) /.test(t)) err(where, `turn after 'dễ' must not start with 'dễ' or 'khó' ('dễ khó giàu'): ${t}`);
        const words = t.split(/\s+/).length;
        if (words > 32) warn(where, `long (${words} words): ${t}`);
      }
    }
  }
  // the closing line must not repeat the card's own predicate word for word ('giữ được những quan hệ bền lâu … là những quan hệ bền lâu')
  for (const c of lib.concepts) for (const v of c.value ?? []) for (const t of [...(c.pred ?? []), ...(c.behave ?? [])])
    if (v.split(/\s+/).length >= 3 && t.toLowerCase().includes(v.toLowerCase())) err(`${c.id}.value`, `value repeats a predicate: "${v}" in "${t}"`);
  for (const id of required) if (!cards.has(id)) err(id, 'no card for a concept that Mệnh rules assert');

  const moves = new Set(['ANCHOR', 'ELABORATE', 'TURN', 'RESCUE', 'TENSION', 'TIMING', 'SATELLITE', 'VALUE', 'TRANSFORM', 'BORROW']);
  for (const s of lib.schemas) for (const m of [...s.order.map(x => x.replace('?', '')), ...s.needs, ...(s.forbid ?? [])]) if (!moves.has(m)) err(s.id, `unknown move ${m}`);
  if (new Set(lib.schemas.map(s => s.id)).size !== lib.schemas.length) err('schemas', 'duplicate schema id');
  for (const m of lib.modifiers) {
    if (m.variants.length < 2) err(m.id, `${m.variants.length} variant(s), need 2`);
    for (const v of m.variants) textCheck(m.id, v, slots.modifier);
  }
  const conn = new Set<string>();
  for (const c of lib.connectives) {
    if (conn.has(c.id)) err(c.id, 'duplicate connective id');
    conn.add(c.id);
    textCheck(c.id, c.text, []);
  }
  for (const [k, vs] of Object.entries(lib.frames.anchor)) for (const v of vs) textCheck(`frames.anchor.${k}`, v, slots.frame);
  for (const [k, vs] of Object.entries(lib.frames.anchor_palace ?? {})) for (const v of vs) textCheck(`frames.anchor_palace.${k}`, v, slots.frame);
  for (const v of lib.frames.via ?? []) textCheck('frames.via', v, ['from', 'S']);
  return out;
}
