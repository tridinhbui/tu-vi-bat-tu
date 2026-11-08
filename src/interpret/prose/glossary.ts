// A term explained the first time a reader meets it (the owner's style brief, docs/plans/NARRATIVE-STYLE-PROMPT.md §4; plan G10.7): the
// whole report is walked in reading order and the first main-text sentence that uses a term gets a short gloss in brackets, only when the
// sentence stays within 35 words. Each gloss is a definition of the term as this report uses it (what is computed), not a reading.
import type { ProseParagraph } from './realize.ts';

export const GLOSSARY: Array<{ term: string; gloss: string }> = [
  { term: 'vô chính diệu', gloss: 'cung không có chính tinh' },
  { term: 'tam phương tứ chính', gloss: 'cung ấy, hai cung tam hợp và cung đối diện' },
  { term: 'xung chiếu', gloss: 'chiếu sang từ cung đối diện' },
  { term: 'nhật chủ', gloss: 'can của ngày sinh, đại diện cho bản thân' },
  { term: 'dụng thần', gloss: 'nhóm chữ lá số cần nhất để cân bằng' },
  { term: 'hỷ thần', gloss: 'nhóm chữ giúp cho dụng thần' },
  { term: 'kỵ thần', gloss: 'nhóm chữ khắc dụng thần' },
  { term: 'điều hậu', gloss: 'điều hòa khí nóng lạnh của tháng sinh' },
  { term: 'đại hạn', gloss: 'chặng mười năm của lá Tử Vi' },
  { term: 'đại vận', gloss: 'chặng mười năm của lá Bát Tự' },
];

type Ch = { chapter: string; paragraphs: ProseParagraph[]; text?: string };
const words = (t: string) => t.split(/\s+/).filter(Boolean).length;

/** The report's chapters with each glossary term explained at its first main-text use (chapters in reading order, Đọc sâu skipped). */
export function glossReport<T extends Ch>(chs: T[]): T[] {
  const done = new Set<string>();
  return chs.map(ch => {
    let changed = false;
    const paragraphs = ch.paragraphs.map(p => {
      if (p.deep || (p as ProseParagraph & { depth?: string }).depth === 'sau') return p;
      let pc = false;
      const sentences = p.sentences.map(s => {
        let text = s.text;
        for (const g of GLOSSARY) {
          if (done.has(g.term)) continue;
          // not inside a name ("nhật chủ Đinh", "đại hạn 23–32"): the gloss goes where the term ends a phrase
          const re = new RegExp(`(^|[^\\p{L}])(${g.term})(?![\\p{L}])(?!\\s*\\()(?!\\s+[\\p{Lu}\\d])`, 'iu');
          if (!re.test(text)) continue;
          const next = text.replace(re, `$1$2 (${g.gloss})`);
          // a sentence the gloss would make too long keeps the term for a later one
          if (words(next) <= 35) { text = next; pc = true; done.add(g.term); }
        }
        return text === s.text ? s : { ...s, text };
      });
      if (!pc) return p;
      changed = true;
      return { ...p, sentences, text: sentences.map(s => s.text).join(' ') };
    });
    return changed ? { ...ch, paragraphs, text: paragraphs.map(p => p.text).join('\n\n') } : ch;
  });
}
