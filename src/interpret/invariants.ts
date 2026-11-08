// Cross-report invariants (plan docs/plans/THIEN-BAN-33-REVIEW-PLAN.md, G-INV): checks that run on the WHOLE report as the reader gets it
// (proseAllChapters + checkedOnly), against the chart facts, not on one module. Shared by test/invariants.test.ts and
// tools/interpret/eval_invariants.ts. Each violation names its invariant, chapter and sentence.
//   INV-1  position: a star said to stand "ở / tại / đóng ở / đứng ở" a palace stands there (Hóa: its carrier does); a cách whose stars
//          stand elsewhere is not said to stand in the palace it reaches
//   INV-2  cause: a Tổng luận sentence that names a ground ("do / gốc là / dựa trên / nền ở X") carries trace.cause, each cause's stars stand
//          where it says, and its rule is one of the sentence's rules
//   INV-4  Tổng luận against the twelve-palace chart: a strength explained as "lower than usual on the chart" is not called the chart's support
//   INV-6  severity: no grave book sentence (claim_severity.json) in a main paragraph; every neutral line has its page and the caution line
//   INV-11 no absolute words in the system's own sentences (book quotes are the book's words)
//   INV-12 level ceiling: a domain the Tổng luận ranks first or last rests on evidence of level 3 or more (tam phương / Tứ Hóa,
//          reason/analysis.ts), never on one palace's own star alone
import type { ChartInput } from './types.ts';
import type { ProseParagraph, ProseSentence } from './prose/realize.ts';
import { graveRuleOf } from './prose/severity.ts';
import { ABSOLUTE } from './prose/lint.ts';
import type { Analysis } from './reason/analysis.ts';

export interface Violation { inv: string; chapter: string; text: string; why: string }
type Ch = { chapter: string; paragraphs: ProseParagraph[] };

const PALACES = ['Mệnh', 'Phụ Mẫu', 'Phúc Đức', 'Điền Trạch', 'Quan Lộc', 'Nô Bộc', 'Thiên Di', 'Tật Ách', 'Tài Bạch', 'Tử Tức', 'Phu Thê', 'Huynh Đệ'];
const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const ABS = [...ABSOLUTE, 'cả đời'];

/** the parts of a sentence the system itself asserts: quoted book words and conditional clauses ("khi / nếu / với điều kiện …") are left out */
const asserted = (t: string) => t.replace(/[“"][^”"]*[”"]/g, ' ').split(/[;:]/).filter(c => !/\b(khi|nếu|với điều kiện|hễ|mượn|phải mượn|giả như)\b/u.test(c)).join(' ; ');

export function checkInvariants(chart: ChartInput, chapters: Ch[], analysis?: Analysis[]): Violation[] {
  const out: Violation[] = [];
  const stars = [...new Set(chart.palaces.flatMap(p => [...p.stars, ...p.major_stars]))].sort((a, b) => b.length - a.length);
  const at = (name: string) => chart.palaces.filter(p => p.stars.includes(name) || p.major_stars.includes(name) || (name === 'Tuần' && p.tuan) || (name === 'Triệt' && p.triet)).map(p => p.name);
  const hoaAt = (h: string) => { const t = chart.tu_hoa[h]; return t ? chart.palaces.find(p => p.branch_index === t.branch)?.name : undefined; };
  const STAR = stars.map(esc).join('|'), PAL = PALACES.map(esc).join('|');
  // "<Star> [(dignity)] [hóa X] [(dignity)] ở|tại|đóng ở|đứng ở|nằm ở [ngay] [cung] <Palace>", the palace not followed by "hoặc" (a book's list)
  const POS = new RegExp(`(?<![\\p{L}])(${STAR}|Hóa (?:Lộc|Quyền|Khoa|Kỵ))(?: \\([^)]*\\))?( hóa (?:Lộc|Quyền|Khoa|Kỵ))?(?: \\([^)]*\\))? (?:ở|tại|đóng ở|đứng ở|nằm ở|đóng tại)(?: ngay)?(?: trong)?(?: chính)? (?:cung )?(${PAL})(?![\\p{L}])(?! hoặc| hay)`, 'gu');
  for (const ch of chapters) for (const p of ch.paragraphs) for (const s of p.sentences) {
    const said = (inv: string, why: string) => out.push({ inv, chapter: ch.chapter, text: s.text, why });
    // INV-1
    for (const m of asserted(s.text).matchAll(POS)) {
      const [, name, hoa, pal] = m;
      if (name.startsWith('Hóa ')) { const h = hoaAt(name); if (h && h !== pal) said('INV-1', `${name} ở cung ${h}, không ở ${pal}`); continue; }
      const where = at(name);
      if (where.length && !where.includes(pal)) said('INV-1', `${name} ở ${where.join(', ')}, không ở ${pal}`);
      if (hoa) { const h = `Hóa ${hoa.trim().replace(/^hóa /, '')}`; if (chart.tu_hoa[h] && chart.tu_hoa[h].star !== name) said('INV-1', `${h} thuộc ${chart.tu_hoa[h].star}, không thuộc ${name}`); }
    }
    // INV-6
    if (!p.deep && s.trace.basis === 'sach' && !s.trace.severity && graveRuleOf(s)) said('INV-6', `câu nặng ở đoạn chính (${graveRuleOf(s)})`);
    if (s.trace.severity && s.trace.severity !== 'moc_tuoi' && !s.trace.cites.length) said('INV-6', 'dòng trung tính thiếu trang');
    // INV-11
    if (s.trace.basis !== 'sach') { const low = ` ${s.text.toLowerCase()}`; for (const w of ABS) if (low.includes(` ${w}`)) said('INV-11', `từ tuyệt đối "${w}"`); }
    // INV-2
    if (ch.chapter === 'tong_luan' && /\b(do|gốc là|gốc ở|dựa trên|nền ở|có nền ở)\s/u.test(s.text) && /^tong_luan:(best|worst)/.test(s.trace.step ?? '')) {
      const cs = s.trace.cause ?? [];
      if (!cs.length) said('INV-2', 'câu nêu nguyên nhân mà không có trace.cause');
      for (const c of cs) {
        if (c.ruleId && !s.trace.rules.includes(c.ruleId)) said('INV-2', `luật ${c.ruleId} không thuộc câu`);
        for (const x of c.stars) if (x.name && !at(x.name).includes(x.palace) && hoaAt(x.name) !== x.palace) said('INV-2', `${x.name} không ở cung ${x.palace}`);
      }
    }
  }
  for (const ch of chapters) {
    // INV-1b: a cách told as reaching its palace from elsewhere is not also said to stand in it
    if (ch.chapter === 'cach_cuc') for (const p of ch.paragraphs) {
      const w = p.sentences.find(s => /:where$/.test(s.trace.step ?? ''));
      if (!w) continue;
      const anchor = w.text.match(/không đứng ở cung (\S+(?: \S+)?) mà/u)?.[1];
      for (const s of p.sentences) if (s !== w && anchor && new RegExp(`(Đứng ở|Cách ở|Vì ở|Đặt ở) cung ${esc(anchor)}`, 'u').test(s.text))
        out.push({ inv: 'INV-1', chapter: ch.chapter, text: s.text, why: `cách chiếu về ${anchor}, không đứng ở đó` });
    }
    // INV-12: the ranked domains of the Tổng luận rest on tam phương level evidence
    if (ch.chapter === 'tong_luan' && analysis) for (const p of ch.paragraphs) for (const s of p.sentences) {
      if (!/^tong_luan:(best|worst):/.test(s.trace.step ?? '')) continue;
      for (const c of s.trace.cause ?? []) {
        const a = analysis.find(x => x.domain === c.domain);
        if (a && a.level < 3) out.push({ inv: 'INV-12', chapter: ch.chapter, text: s.text, why: `${c.domain} xếp hạng trên chứng cứ cấp ${a.level}` });
      }
    }
    // INV-4: a best domain explained by the radar line is not told with the strong openers
    if (ch.chapter === 'tong_luan') for (const p of ch.paragraphs) {
      const radar = p.sentences.find(s => /^tong_luan:radar:/.test(s.trace.step ?? '') && /thấp hơn mức|dưới mức/u.test(s.text));
      const best = p.sentences.find(s => /^tong_luan:best:/.test(s.trace.step ?? ''));
      if (radar && best && /^(Điểm tựa vững nhất|Mặt mạnh nhất|Chỗ dựa đứng đầu)/u.test(best.text)) out.push({ inv: 'INV-4', chapter: ch.chapter, text: best.text, why: 'gọi là chỗ dựa mạnh nhất trong khi biểu đồ cung thấp hơn mức thường' });
    }
  }
  return out;
}

/** the sentences of the report, for counting */
export const sentencesOf = (chs: Ch[]): ProseSentence[] => chs.flatMap(c => c.paragraphs.flatMap(p => p.sentences));
