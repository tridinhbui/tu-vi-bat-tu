// Only what is checked reaches the reader (owner's decision, 2026-10-21): a sentence of basis 'pho_thong' — a common meaning the system drafted
// and no page confirms (deep.ts cards, the Toàn Thư hạn verses still waiting for their page check, the Bát Tự cards, phù ức and cách names) —
// is removed from every prose output. A paragraph left with nothing but the system's own words (he_thong) goes too, since those words
// restated what was removed; a lead-in whose sentence went moves to the next sentence.
import type { ProseParagraph } from './realize.ts';
import { withLead } from './luan.ts';
import { severityParagraphs } from './severity.ts';
import type { ChartInput, Knowledge } from '../types.ts';

const UNCHECKED = new Set(['pho_thong']);

/** A system sentence that stands on its own ground rather than restating a removed one: a domain conclusion of the ledger, a hạn's level
 *  on the indices, a hạn's Hóa or natal link (reason/ledger.ts, prose/vanhan.ts). */
const OWN = (s: ProseParagraph['sentences'][number]) => !!s.trace.ledger || /^(level|hoa|natal):/.test(s.trace.step ?? '');

/** A minh họa line (owner's policy 2026-10-22) passes only while the ONE sourced sentence it makes concrete is told in the same paragraph:
 *  Tử Vi ties it by `tied` to a book sentence with a rule; Bát Tự by `attach` to a book or computed sentence. A line with no tie, or whose
 *  sentence was removed, goes. */
function tiedOk(s: ProseParagraph['sentences'][number], kept: ProseParagraph['sentences']): boolean {
  if (s.trace.basis !== 'minh_hoa') return true;
  if (s.trace.tied) return kept.some(x => x !== s && x.trace.step === s.trace.tied && x.trace.basis === 'sach' && x.trace.rules.length > 0);
  return !!s.trace.attach && kept.some(k => k !== s && k.trace.step === s.trace.attach && (k.trace.basis === 'sach' || k.trace.basis === 'tinh_toan'));
}

/** Habitual additive openers (the owner's style brief, docs/plans/NARRATIVE-STYLE-PROMPT.md §3; plan G10.7): they add nothing a reader
 *  needs, so within one paragraph only the first one stays; a later one is dropped and the sentence starts on its own words. Connectors that
 *  carry a relation (Dẫu vậy, Vì vậy, Tuy nhiên …) are not touched. */
const HABIT_OPENER = /^(Bên cạnh đó|Ngoài ra|Thêm vào đó|Thêm nữa|Hơn nữa|Song song với điều ấy|Song song với những nét ấy|Cùng với đó),\s+/u;
/** the same causal joint said again and again in one paragraph ("…; vì vậy …" five times): from the second on, it turns to another causal
 *  joint of the same meaning */
const CAUSAL = [', nên ', ': ', '; do đó ', ', vì thế '];
export function connectorParagraphs(ps: ProseParagraph[]): ProseParagraph[] {
  return ps.map(p => {
    let seen = 0, vv = 0, changed = false;
    const sentences = p.sentences.map(s0 => {
      let s = s0;
      if (s.text.includes('; vì vậy ') && ++vv > 1) { s = { ...s, text: s.text.replace('; vì vậy ', CAUSAL[(vv - 2) % CAUSAL.length]) }; changed = true; }
      const m = s.text.match(HABIT_OPENER);
      if (!m) return s;
      if (++seen === 1) return s;
      changed = true;
      const rest = s.text.slice(m[0].length);
      return { ...s, text: rest.charAt(0).toLocaleUpperCase('vi') + rest.slice(1) };
    });
    return changed ? { ...p, sentences, text: sentences.map(s => s.text).join(' ') } : p;
  });
}

export function checkedParagraphs(ps: ProseParagraph[], chart?: ChartInput, k?: Knowledge): ProseParagraph[] {
  // grave book sentences (claim_severity.json, owner decision Q2 2026-11-07) leave the main text for a neutral Đọc sâu line first
  return connectorParagraphs(severityParagraphs(ps, chart, k)).flatMap(p => {
    const kept0 = p.sentences.filter(s => !UNCHECKED.has(s.trace.basis));
    const kept = kept0.filter(s => tiedOk(s, kept0));
    if (!kept.length || (kept.length < p.sentences.length && kept.every(s => (s.trace.basis === 'he_thong' || s.trace.basis === 'tong_hop' || s.trace.basis === 'minh_hoa' || s.trace.basis === 'loi_khuyen') && !OWN(s)))) return [];
    if (kept.length === p.sentences.length) return [p];
    let sentences = kept;
    if (p.lead && !kept[0].text.startsWith(p.lead)) sentences = [{ ...kept[0], text: withLead(p.lead, kept[0].text) }, ...kept.slice(1)];
    return [{ ...p, sentences, text: sentences.map(s => s.text).join(' ') }];
  });
}

/** A prose chapter (or the Bát Tự reading with its per-section `chapters`, or the overview with its `card`) with the unchecked parts removed. */
export function checkedOnly<T extends { paragraphs: ProseParagraph[]; text: string; chapters?: unknown; card?: unknown; advice?: unknown }>(ch: T, chart?: ChartInput, k?: Knowledge): T {
  const paragraphs = checkedParagraphs(ch.paragraphs, chart, k);
  const out: T = { ...ch, paragraphs, text: paragraphs.map(p => p.text).join('\n\n') };
  if (ch.chapters && typeof ch.chapters === 'object' && !Array.isArray(ch.chapters))
    (out as { chapters: Record<string, ProseParagraph[]> }).chapters = Object.fromEntries(Object.entries(ch.chapters as Record<string, ProseParagraph[]>)
      .map(([id, ps]) => [id, checkedParagraphs(ps, chart, k)] as const).filter(([, ps]) => ps.length));
  if (Array.isArray(ch.card)) (out as { card: Array<{ basis: string }> }).card = (ch.card as Array<{ basis: string }>).filter(f => !UNCHECKED.has(f.basis));
  return out;
}
