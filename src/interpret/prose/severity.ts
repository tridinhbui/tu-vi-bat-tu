// Claim severity (plan docs/plans/THIEN-BAN-33-REVIEW-PLAN.md G1, owner decision Q2 2026-11-07). Severity is its own axis, independent of
// confidence: a book sentence whose conditions hold exactly may still be too heavy to stand as a conclusion about the person.
//   grave classes (suc_khoe, tho_yeu, sinh_san, hon_nhan_vo, vat_chat_nang, tat_xau, phap_ly): the book sentence never reaches a main
//     paragraph, a chapter close or the Tổng luận. It is replaced, in the chapter's Đọc sâu, by a neutral line: which combination the tradition
//     reads into which matter and in which direction, labelled as a traditional idea not checked by experience. The quote and page stay in
//     the sentence trace (the evidence panel shows them).
//   moc_tuoi (a fixed age): the sentence stays, said as the book's own mark.
// The classes come from engine/data/kg/claim_severity.json (tools/interpret/build_claim_severity.py, hand-reviewed).
import SEV from '../../../engine/data/kg/claim_severity.json' with { type: 'json' };
import type { ProseParagraph, ProseSentence } from './realize.ts';
import type { ChartInput } from '../types.ts';

export interface SeverityEntry { class: string; pol: '+' | '-' | '~'; palace: string; cond: string; cite: string; claim: string }
const RULES = (SEV as { rules: Record<string, SeverityEntry> }).rules;
const GRAVE = new Set((SEV as { grave: string[] }).grave);
const CLS = (SEV as { classes: Record<string, { topic: string; re: string }> }).classes;
const TOPIC = Object.fromEntries(Object.entries(CLS).map(([c, v]) => [c, v.topic]));
const WORDS = Object.fromEntries(Object.entries(CLS).map(([c, v]) => [c, new RegExp(v.re, 'iu')]));
/** a book sentence is grave when the rule it voices is: the first rule, or any listed rule whose class words the sentence itself says (a
 *  corroboration lists the other rules of the same reading; their outcome is the sentence's only when its words say it) */
export function graveRuleOf(s: ProseSentence): string | undefined {
  const rs = s.trace.rules;
  if (!rs.length || s.trace.ledger) return undefined;
  if (isGrave(rs[0])) return rs[0];
  return rs.find(id => isGrave(id) && WORDS[RULES[id].class]?.test(s.text));
}

export const severityOf = (ruleId: string): SeverityEntry | undefined => RULES[ruleId];
export const isGrave = (ruleId: string) => { const s = RULES[ruleId]; return !!s && GRAVE.has(s.class); };

/** a sentence that only leans on the one before it (a corroboration, an "also"): it goes with that sentence */
const LEANS = /^(Điều này|Điều ấy|Ý này|Ý ấy|Câu ấy|Thêm một căn cứ|Cũng trong|Cũng theo|Cùng chiều ấy|Nhìn sang)/;
const cap = (s: string) => s.charAt(0).toLocaleUpperCase('vi') + s.slice(1);
const joinVi = (xs: string[]) => xs.length <= 1 ? xs.join('') : `${xs.slice(0, -1).join(', ')} và ${xs.at(-1)}`;

/** the stars of the book conditions that stand on this chart, said where they stand (a book condition is often a list of alternatives,
 *  "Bệnh hoặc Bệnh Phù": only the ones present are named, INV-1); without the chart, the palace alone */
function standing(chart: ChartInput | undefined, es: SeverityEntry[]): string {
  const P = es.find(e => e.palace)?.palace ?? '';
  if (!chart) return P ? `một số sao ở cung ${P}` : 'một số sao của lá số';
  const home = chart.palaces.find(p => p.name === P);
  const near = home ? [0, 4, 8, 6].map(d => chart.palaces.find(p => p.branch_index === (home.branch_index + d) % 12)!) : chart.palaces;
  const names = [...new Set(chart.palaces.flatMap(p => [...p.stars, ...p.major_stars]))].sort((a, b) => b.length - a.length);
  const by = new Map<string, string[]>();
  const put = (name: string, pal: string) => { const xs = by.get(pal) ?? by.set(pal, []).get(pal)!; if (!xs.includes(name)) xs.push(name); };
  for (const e of es) {
    let rest = e.cond;
    for (const n of names) {
      if (!rest.includes(n)) continue;
      rest = rest.split(n).join(' ');
      const q = near.find(p => p.stars.includes(n) || p.major_stars.includes(n));
      if (q) put(n, q.name);
    }
    for (const t of ['Tuần', 'Triệt'] as const) if (e.cond.includes(t)) { const q = near.find(p => (t === 'Tuần' ? p.tuan : p.triet)); if (q) put(t, q.name); }
  }
  if (!by.size) return P ? `một số sao ở cung ${P}` : 'một số sao của lá số';
  const parts = [...by].sort(([a], [b]) => Number(b === P) - Number(a === P)).map(([pal, xs]) => `${joinVi(xs)} ở cung ${pal}`);
  return joinVi(parts) + (P && !by.has(P) ? ` (chiếu về cung ${P})` : '');
}

/** The grave book sentences of a chapter's paragraphs, moved out: each main or deep paragraph loses them (and a sentence that only leans on
 *  one of them); the chapter gains one Đọc sâu paragraph with the neutral lines. Returns the paragraphs unchanged when nothing is grave. */
export function severityParagraphs(ps: ProseParagraph[], chart?: ChartInput): ProseParagraph[] {
  const moved: Array<{ ruleId: string; e: SeverityEntry; s: ProseSentence }> = [];
  const out = ps.flatMap(p => {
    if ((p as ProseParagraph & { severity?: boolean }).severity) return [p];
    const kept: ProseSentence[] = [];
    let dropped = false, changed = false;
    for (const s of p.sentences) {
      // a book sentence on a grave rule moves; a system sentence that recalls or weighs it (not a domain verdict, which reason/ledger.ts
      // already keeps clear of grave readings standing alone) goes with it
      const g = s.trace.basis === 'sach' ? graveRuleOf(s) : s.trace.rules.length <= 3 && !s.trace.ledger ? s.trace.rules.find(isGrave) : undefined;
      if (g) { if (s.trace.basis === 'sach') moved.push({ ruleId: g, e: RULES[g], s }); dropped = changed = true; continue; }
      // a fixed age (moc_tuoi) stays, said as the old text's own mark, not as this chart's timing (G1; G6 sets it beside the đại hạn)
      const age = s.trace.basis === 'sach' ? s.trace.rules.find(id => RULES[id]?.class === 'moc_tuoi') : undefined;
      if (age && !s.trace.severity) {
        const body = s.text.replace(/[.!]\s*$/, ''), low = body.charAt(0).toLocaleLowerCase('vi') + body.slice(1);
        kept.push({ ...s, text: `Lời cổ còn đặt một mốc tuổi: ${low}; đó là mốc chung, chưa xét theo các đại hạn của riêng lá số này.`, trace: { ...s.trace, severity: 'moc_tuoi' } });
        dropped = false; changed = true;
        continue;
      }
      if (dropped && LEANS.test(s.text) && s.trace.basis !== 'he_thong') { changed = true; continue; }
      dropped = false;
      kept.push(s);
    }
    if (!changed) return [p];
    // a paragraph left with only the system's own words restated what was moved: it goes (as prose/checked.ts does for phổ thông)
    if (!kept.length || kept.every(s => s.trace.basis !== 'sach' && s.trace.basis !== 'tinh_toan' && !s.trace.ledger)) return [];
    const sentences = p.lead && !kept[0].text.startsWith(p.lead) ? [{ ...kept[0], text: `${p.lead} ${kept[0].text.charAt(0).toLocaleLowerCase('vi')}${kept[0].text.slice(1)}` }, ...kept.slice(1)] : kept;
    return [{ ...p, sentences, text: sentences.map(s => s.text).join(' ') }];
  });
  if (!moved.length) return out;
  // one line per class (no direction: the owner asked for a neutral description, Q2): the combinations the tradition reads into that matter, then the one caution line
  const groups = new Map<string, typeof moved>();
  for (const m of moved) { const key = m.e.class; if (!(groups.get(key) ?? groups.set(key, []).get(key)!).some(x => x.ruleId === m.ruleId)) groups.get(key)!.push(m); }
  const sentences: ProseSentence[] = [...groups.values()].map(ms => {
    const e = ms[0].e;
    const text = `Trong quan niệm truyền thống, ${standing(chart, ms.map(m => m.e))} được đọc vào chuyện ${TOPIC[e.class]}.`;
    return { text: cap(text), trace: { move: 'VALUE', concepts: [], rules: ms.map(m => m.ruleId), cites: [...new Set(ms.map(m => m.e.cite))].sort(), basis: 'sach', step: `severity:${e.class}`,
      severity: e.class, note: `Câu gốc: ${ms.map(m => `"${m.e.claim}" (${m.e.cite})`).join('; ')}. Lớp mức nặng ${e.class} (claim_severity.json): không đưa vào kết luận.` } } as ProseSentence;
  });
  sentences.push({ text: 'Đây là quan niệm cổ, chưa được kiểm chứng bằng thực nghiệm, nên phần luận này không dùng chúng để đoán về người có lá số.',
    trace: { move: 'VALUE', concepts: [], rules: [], cites: [], basis: 'he_thong', step: 'severity:caution' } } as ProseSentence);
  out.push({ role: 'support', sentences, text: sentences.map(s => s.text).join(' '), deep: true, title: 'Quan niệm cổ cần đọc thận trọng', severity: true } as ProseParagraph);
  return out;
}
