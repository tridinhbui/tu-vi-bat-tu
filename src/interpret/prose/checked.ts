// Only what is checked reaches the reader (owner's decision, 2026-10-21): a sentence of basis 'pho_thong' — a common meaning the system drafted
// and no page confirms (deep.ts cards, the Toàn Thư hạn verses still waiting for their page check, the Bát Tự cards, phù ức and cách names) —
// is removed from every prose output. A paragraph left with nothing but the system's own words (he_thong) goes too, since those words
// restated what was removed; a lead-in whose sentence went moves to the next sentence.
import type { ProseParagraph } from './realize.ts';
import { withLead } from './luan.ts';

const UNCHECKED = new Set(['pho_thong']);

/** A system sentence that stands on its own ground rather than restating a removed one: a domain conclusion of the ledger, a hạn's level
 *  on the indices, a hạn's Hóa or natal link (reason/ledger.ts, prose/vanhan.ts). */
const OWN = (s: ProseParagraph['sentences'][number]) => !!s.trace.ledger || /^(level|hoa|natal):/.test(s.trace.step ?? '');

/** An illustration (basis minh_hoa, owner policy 2026-10-22) stays only next to the one sourced sentence it makes concrete: its trace.attach
 *  names that sentence's step, and that sentence must be kept and be a book sentence or a computed one. */
const attachedOk = (s: ProseParagraph['sentences'][number], kept: ProseParagraph['sentences']) =>
  s.trace.basis !== 'minh_hoa' || (!!s.trace.attach && kept.some(k => k !== s && k.trace.step === s.trace.attach && (k.trace.basis === 'sach' || k.trace.basis === 'tinh_toan')));

export function checkedParagraphs(ps: ProseParagraph[]): ProseParagraph[] {
  return ps.flatMap(p => {
    const kept0 = p.sentences.filter(s => !UNCHECKED.has(s.trace.basis));
    const kept = kept0.filter(s => attachedOk(s, kept0));
    if (!kept.length || (kept.length < p.sentences.length && kept.every(s => s.trace.basis === 'he_thong' && !OWN(s)))) return [];
    if (kept.length === p.sentences.length) return [p];
    let sentences = kept;
    if (p.lead && !kept[0].text.startsWith(p.lead)) sentences = [{ ...kept[0], text: withLead(p.lead, kept[0].text) }, ...kept.slice(1)];
    return [{ ...p, sentences, text: sentences.map(s => s.text).join(' ') }];
  });
}

/** A prose chapter (or the Bát Tự reading with its per-section `chapters`, or the overview with its `card`) with the unchecked parts removed. */
export function checkedOnly<T extends { paragraphs: ProseParagraph[]; text: string; chapters?: unknown; card?: unknown; advice?: unknown }>(ch: T): T {
  const paragraphs = checkedParagraphs(ch.paragraphs);
  const out: T = { ...ch, paragraphs, text: paragraphs.map(p => p.text).join('\n\n') };
  if (ch.chapters && typeof ch.chapters === 'object' && !Array.isArray(ch.chapters))
    (out as { chapters: Record<string, ProseParagraph[]> }).chapters = Object.fromEntries(Object.entries(ch.chapters as Record<string, ProseParagraph[]>)
      .map(([id, ps]) => [id, checkedParagraphs(ps)] as const).filter(([, ps]) => ps.length));
  if (Array.isArray(ch.card)) (out as { card: Array<{ basis: string }> }).card = (ch.card as Array<{ basis: string }>).filter(f => !UNCHECKED.has(f.basis));
  return out;
}
