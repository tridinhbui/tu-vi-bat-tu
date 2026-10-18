// Semantic layer (port of the parts of engine/tvbt/synthesis/semantics.py the narrative needs): a rule's own book sentence, its
// condition as the book states it, the condition leaves TRUE on this chart in Vietnamese, the concepts the sentence names
// (longest-cue matching with negation), polarity and modality, and the normalised chart facts it stands on (independence key).
import { leaves, trueLeaves } from './dsl.ts';
import type { Concept, Facts, Finding, Knowledge, Rule } from './types.ts';

export interface Evidence {
  finding: Finding; rule: Rule; palace: string | null;
  reading: string; core: string; bookCondition: string; chartCondition: string;
  presentStars: string[]; concepts: Array<{ id: string; clause: string; group: number }>;
  polarity: '+' | '-' | '~'; modality: 'tendency' | 'potential' | 'condition' | 'limitation';
  root: string[]; books: string[]; cites: string[];
  cond: CondParts;            // the satisfied condition, structured (rendered relative to a home palace by condText)
  specificity: number;        // chart-specific atoms in the root (stars, dignity, branch): 0 = applies to a whole class of people
  generic: boolean;           // true when the rule stands on year branch / gender / polarity only (same reading for every such person)
}
export interface CondParts {
  palace: string | null; own: string[]; hoa: string[]; opp: string[]; tp: string[]; nb: string[]; dig: Record<string, string>;
  branch: { branch: string; kind: 'ham' | 'sang' | 'plain' } | null; tt: string[]; extra: string[];
}

const MAJORS = new Set(['Tử Vi', 'Thiên Cơ', 'Thái Dương', 'Vũ Khúc', 'Thiên Đồng', 'Liêm Trinh', 'Thiên Phủ', 'Thái Âm', 'Tham Lang', 'Cự Môn', 'Thiên Tướng', 'Thiên Lương', 'Thất Sát', 'Phá Quân']);
const SCHOOL: Record<string, string> = { SRC_THUC_HANH: 'Thực Hành', SRC_KHAO_LUAN: 'Khảo Luận', SRC_TOAN_THU: 'Toàn Thư', SRC_TVDS_TAN_BIEN: 'Tân Biên' };
const EDITORIAL = ["'", '‘', '“', 'sách ', 'đây là', 'câu ', 'độ sáng', 'cùng nhận định', 'chưa ', 'đọc là', 'nhưng sách', 'bảng ', 'tức ', 'gọi là', 'ngưỡng', 'hệ thống', 'lưu ý', 'xem ', 'không phân'];
const CONTRAST = [' nhưng ', ' mà ', ' song ', ' tuy '];
const NORM: Record<string, string> = {
  'palace.own_major_stars': 'own', 'palace.own_stars': 'own', 'palace.tam_phuong_stars': 'tp', 'palace.tam_phuong_majors': 'tp',
  'palace.tam_phuong_tu_hoa': 'tp', 'palace.rel.tp_hoa': 'tp', 'palace.tu_hoa': 'own', 'palace.rel.opp_stars': 'opp', 'palace.rel.opp_majors': 'opp',
  'palace.neighbor_stars': 'nb', 'palace.neighbor_majors': 'nb', 'palace.rel.flank_prev_stars': 'nb', 'palace.rel.flank_next_stars': 'nb',
  'palace.rel.flank_prev_majors': 'nb', 'palace.rel.flank_next_majors': 'nb', 'palace.rel.flank_stars': 'nb',
  'palace.rel.tp_stars': 'tp', 'palace.rel.tp_majors': 'tp', 'palace.rel.trine_stars': 'tp', 'palace.rel.trine_majors': 'tp', 'palace.rel.trine_hoa': 'tp',
  'palace.rel.trine1_stars': 'tp', 'palace.rel.trine1_majors': 'tp', 'palace.rel.trine1_hoa': 'tp', 'palace.rel.trine2_stars': 'tp', 'palace.rel.trine2_majors': 'tp',
  'palace.rel.trine2_hoa': 'tp', 'palace.rel.self_stars': 'own', 'palace.rel.self_majors': 'own', 'palace.rel.self_hoa': 'own', 'palace.rel.opp_hoa': 'opp',
};

export class Lexicon {
  concepts: Map<string, Concept>; cues: Array<[string, string]>; negators: string[];
  constructor(k: Knowledge) {
    this.concepts = new Map(k.concepts.concepts.map(c => [c.id, c]));
    this.cues = k.concepts.concepts.flatMap(c => c.cues.map(q => [q, c.id] as [string, string])).sort((a, b) => b[0].length - a[0].length || (a[0] < b[0] ? -1 : 1));
    this.negators = k.concepts.negators;
  }

  /** Greedy longest-first cue matching over the whole reading; a negator right before a cue flips it to the concept's `opp`. */
  match(core: string): Array<{ id: string; clause: string; group: number }> {
    const low = core.toLowerCase(), taken = new Array(low.length).fill(false), hits: Array<[number, string]> = [];
    const isAlnum = (ch: string | undefined) => !!ch && /[\p{L}\p{N}]/u.test(ch);
    for (const [cue, cid0] of this.cues) {
      let start = 0;
      for (;;) {
        const i = low.indexOf(cue, start);
        if (i < 0) break;
        const j = i + cue.length;
        if (!isAlnum(low[i - 1]) && !isAlnum(low[j]) && !taken.slice(i, j).some(Boolean)) {
          for (let k = i; k < j; k++) taken[k] = true;
          const before = low.slice(Math.max(0, i - 10), i), c = this.concepts.get(cid0)!;
          const neg = this.negators.some(n => before.endsWith(n));
          if (neg && c.opp) hits.push([i, c.opp]);
          else if (!(neg && c.pol !== '~')) hits.push([i, cid0]);
        }
        start = j;
      }
    }
    hits.sort((a, b) => a[0] - b[0]);
    const cuts = CONTRAST.map(w => low.indexOf(w)).filter(x => x >= 0), cut = cuts.length ? Math.min(...cuts) : low.length;
    const bounds = [0, ...[...core.matchAll(/[,;]| và | nhưng | mà | song | tuy /g)].map(m => (m.index ?? 0) + m[0].length), core.length + 1];
    const seen = new Set<string>(), out: Array<{ id: string; clause: string; group: number }> = [];
    for (const [i, id] of hits) {
      if (seen.has(id)) continue;
      seen.add(id);
      const lo = Math.max(...bounds.filter(b => b <= i)), hi = Math.min(...bounds.filter(b => b > i), core.length);
      const clause = core.slice(lo, hi).replace(/^[\s,;]+|[\s,;]+$/g, '').replace(/\s*(và|nhưng|mà|song|tuy)$/, '').trim();
      if (/^(nên|cần|phải biết) /i.test(clause) && id !== 'rel.timing') continue;
      out.push({ id, clause, group: i > cut ? 1 : 0 });
    }
    return out;
  }
}

/** (core, condition) of a book sentence: the condition is the LAST top-level parenthetical; editorial notes after ';' are dropped. */
export function splitReading(text0: string): { core: string; condition: string } {
  let text = text0.replace(/\s*\[[^\]]*\]/g, '').trim().replace(/\.$/, '');
  for (const pre of ['khuynh hướng ', 'hạn chế: ']) if (text.startsWith(pre)) text = text.slice(pre.length);
  const segs = text.split(';').map(s => s.trim());
  text = [segs[0], ...segs.slice(1).filter(s => s && !EDITORIAL.some(e => s.toLowerCase().startsWith(e)) && !/hệ thống|chưa có trong|đọc là|bản luận|sách (nói|ghi|xem|không)/i.test(s))].join('; ');
  let condition = '', depth = 0, start = -1, last: [number, number] | null = null;
  for (let i = 0; i < text.length; i++) {
    if (text[i] === '(') { if (depth === 0) start = i; depth++; }
    else if (text[i] === ')' && depth) { depth--; if (depth === 0) last = [start, i]; }
  }
  if (last) { condition = text.slice(last[0] + 1, last[1]); text = (text.slice(0, last[0]).trimEnd() + ' ' + text.slice(last[1] + 1).trimStart()).trim(); }
  let core = text.replace(/^[\s;,.]+|[\s;,.]+$/g, '');
  if (!condition && core.includes(': ') && core.split(': ')[0].length <= 45) { const [a, ...b] = core.split(': '); condition = a; core = b.join(': '); }
  return { core: core.trim(), condition: condition.replace(/^theo /, '').trim() };
}

const join = (xs: string[]) => xs.length <= 1 ? (xs[0] ?? '') : xs.slice(0, -1).join(', ') + ' và ' + xs[xs.length - 1];

/** The satisfied leaves, structured, with the chart's own values ('Kình hoặc Đà' becomes the star actually there). */
export function chartCondition(rule: Rule, facts: Facts, palace: string | null): { text: string; stars: string[]; parts: CondParts } {
  const parts: CondParts = { palace, own: [], hoa: [], opp: [], tp: [], nb: [], dig: {}, branch: null, tt: [], extra: [] };
  const book = (rule.reading ?? '').toLowerCase();
  for (const lf of trueLeaves(rule.conditions, facts)) {
    if (lf.fact === 'palace.name') continue;
    const got = facts[lf.fact], want = Array.isArray(lf.value) ? lf.value : [lf.value];
    const vals = Array.isArray(got) ? want.filter(w => (got as unknown[]).includes(w)) : want;
    const add = (arr: string[]) => vals.forEach(v => typeof v === 'string' && !arr.includes(v) && arr.push(v));
    if (lf.fact.startsWith('palace.dignity.')) { if (typeof got === 'string' && got !== 'unspecified') parts.dig[lf.fact.slice(15)] = got; if (!parts.own.includes(lf.fact.slice(15))) parts.own.push(lf.fact.slice(15)); }
    else if (lf.fact === 'palace.tu_hoa') add(parts.hoa);
    else if (NORM[lf.fact] === 'own') add(parts.own);
    else if (NORM[lf.fact] === 'tp') add(parts.tp);
    else if (NORM[lf.fact] === 'opp') add(parts.opp);
    else if (NORM[lf.fact] === 'nb') add(parts.nb);
    else if (lf.fact === 'palace.branch') {
      // a branch list in a rule is almost always a brightness table ('Kiếp/Không hãm', 'Nhật Nguyệt Sửu Mùi'): say which, never 'an tại X' alone
      const kind = /hãm/.test(book) && lf.operator === 'not_in' ? 'ham' : /hãm/.test(book) && lf.operator === 'in' ? 'ham' : /(miếu|vượng|đắc|sáng)/.test(book) ? 'sang' : 'plain';
      parts.branch = { branch: String(got), kind };
    }
    else if ((lf.fact === 'palace.tuan' || lf.fact === 'palace.triet') && got) parts.tt.push(lf.fact.endsWith('tuan') ? 'Tuần' : 'Triệt');
    else if (lf.fact === 'chart.gender') parts.extra.push(`${got} mệnh`);
    else if (lf.fact === 'chart.year_polarity') parts.extra.push(`tuổi ${got}`);
    else if (lf.fact === 'palace.khi.sat_tp') parts.extra.push('sát tinh hội về');
    else if (lf.fact === 'chart.year_branch') {
      const label = rule.reading?.match(/^([^:]{3,45}):/)?.[1];
      parts.extra.push(label ? `${label} — thế chung của mọi lá số tuổi ${got}` : `tuổi ${got} (áp chung cho mọi người tuổi ${got})`);
    }
  }
  const inPalace = Array.isArray(facts['palace.own_stars']) ? facts['palace.own_stars'] as string[] : [];
  for (const s of [...parts.tp]) if (inPalace.includes(s) && !parts.own.includes(s)) { parts.own.push(s); parts.tp.splice(parts.tp.indexOf(s), 1); }
  if (parts.extra.length === 2 && parts.extra[0].endsWith(' mệnh') && parts.extra[1].startsWith('tuổi ')) parts.extra = [`${parts.extra[0]} ${parts.extra[1]}`];
  const stars = [...new Set([...parts.own, ...parts.hoa, ...parts.opp, ...parts.tp.filter(x => !parts.own.includes(x)), ...parts.nb])];
  return { text: condText(parts), stars, parts };
}

/** Renders a condition. With `home` equal to the condition's palace (the paragraph already names it), the palace is not repeated:
 *  'có Thiên Tướng và Địa Kiếp trong cung' instead of a dangling 'Thiên Tướng và Địa Kiếp'. */
export function condText(c: CondParts, home?: string): string {
  const where = c.palace ?? 'lá số', atHome = !!home && home === c.palace, parts: string[] = [];
  const star = (s: string) => c.dig[s] ? `${s} (${c.dig[s]})` : s;
  // one order, so equal conditions read equal: chính tinh first (as the books write them), then the rest
  const vi = (a: string, b: string) => (MAJORS.has(a) ? 0 : 1) - (MAJORS.has(b) ? 0 : 1) || a.localeCompare(b, 'vi');
  const ownL = [...[...c.own].sort(vi).map(star), ...c.hoa];
  if (ownL.length) {
    const hamNote = c.branch?.kind === 'ham' ? ` hãm địa ở ${c.branch.branch}` : c.branch?.kind === 'sang' ? ` đắc địa ở ${c.branch.branch}` : '';
    parts.push(atHome ? `có ${join(ownL)}${hamNote}${hamNote ? '' : ' trong cung'}` : `${join(ownL)}${hamNote ? hamNote + ',' : ''} tại ${where}`);
  } else if (c.branch) parts.push(`${atHome ? 'cung' : where} ở ${c.branch.branch}`);
  if (c.branch && ownL.length && c.branch.kind === 'plain') parts.push(`${atHome ? 'cung' : where} ở ${c.branch.branch}`);
  if (c.opp.length) parts.push(`${join(c.opp)} xung chiếu${atHome ? '' : ' ' + where}`);
  const tp2 = c.tp.filter(x => !c.own.includes(x) && !c.hoa.includes(x));
  if (tp2.length) parts.push(`${join(tp2)} hội chiếu về${atHome ? '' : ' ' + where}`);
  if (c.nb.length) parts.push(`${join(c.nb)} giáp${atHome ? ' cung' : ' ' + where}`);
  if (c.tt.length) parts.push(`${atHome ? 'cung' : where} có ${join(c.tt)}`);
  for (const x of c.extra) parts.push(x === 'sát tinh hội về' ? `sát tinh hội về${atHome ? '' : ' ' + where}` : x);
  return parts.join(', ');
}

export function rootOf(rule: Rule): string[] {
  const atoms = new Set<string>();
  for (const l of leaves(rule.conditions)) {
    if (l.fact === 'palace.name') continue;
    const vals = Array.isArray(l.value) ? l.value : [l.value];
    if (NORM[l.fact]) vals.forEach(v => atoms.add(`${NORM[l.fact]}:${v}`));
    else if (l.fact.startsWith('palace.dignity.')) atoms.add(`dig:${l.fact.slice(15)}:${vals.join(',')}`);
    else atoms.add(`${l.fact}:${vals.join(',')}`);
  }
  return [...atoms].sort();
}
export function rootStars(root: string[]): Set<string> {
  return new Set(root.flatMap(a => { const [k, v] = a.split(/:(.*)/s); return ['own', 'tp', 'opp', 'nb'].includes(k) ? [v] : k === 'dig' ? [v.split(':')[0]] : []; }));
}

export function readingOf(rule: Rule, claims: Record<string, string>, claim: string, effect: string): string {
  if (rule.reading) return rule.reading;
  return (effect === 'limit' && claims['limit:' + claim]) || claims[claim] || claim.replace(/_/g, ' ');
}

export function annotate(findings: Finding[], k: Knowledge, lex: Lexicon, base: Record<string, Facts>): Evidence[] {
  const rmap = new Map(k.rules.map(r => [r.id, r]));
  const out: Evidence[] = [];
  for (const f of findings) {
    const rule = rmap.get(f.ruleId)!;
    if (f.basis !== 'verified' || /^(menh_nhom_|cach_sat_pha|cau_truc_)/.test(f.claim)) continue;   // drafts and classification labels stay out of prose
    const reading = readingOf(rule, k.claims, f.claim, f.effect);
    const sr = splitReading(reading), condition = sr.condition;
    const core = sr.core.replace(/\btheo sách (đây |là )?/g, '').replace(/\s{2,}/g, ' ').trim();
    const facts = { ...(base.chart ?? {}), ...(base[f.subject] ?? {}) };
    const cc = chartCondition(rule, facts, f.palace);
    const concepts = lex.match(core);
    const pols = new Set(concepts.map(c => lex.concepts.get(c.id)!.pol));
    let polarity: '+' | '-' | '~' = f.effect === 'limit' ? '-' : pols.has('+') && pols.has('-') ? '~' : pols.has('-') ? '-' : pols.has('+') ? '+' : '~';
    const low = core.toLowerCase();
    const modality = f.effect === 'limit' ? 'limitation' : /có thể/.test(low) ? 'potential' : /\b(nếu|khi|cần|mới|thì)\b/.test(low) ? 'condition' : 'tendency';
    const root = rootOf(rule), specificity = root.filter(a => /^(own|tp|opp|nb|dig|palace\.branch|palace\.tu_hoa|palace\.tuan|palace\.triet|palace\.khi)/.test(a)).length;
    out.push({ finding: f, rule, palace: f.palace, reading, core, bookCondition: condition, chartCondition: cc.text || condition, presentStars: cc.stars,
      concepts, polarity, modality, root, books: [...new Set(rule.sourceIds.map(s => SCHOOL[s] ?? s))].sort(), cites: rule.cites,
      cond: cc.parts, specificity, generic: specificity === 0 });
  }
  return out;
}

export { join as joinVi };
