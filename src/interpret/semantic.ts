// Semantic layer (port of the parts of engine/tvbt/synthesis/semantics.py the narrative needs): a rule's own book sentence, its
// condition as the book states it, the condition leaves TRUE on this chart in Vietnamese, the concepts the sentence names
// (longest-cue matching with negation), polarity and modality, and the normalised chart facts it stands on (independence key).
import { absentLeaves, leaves, trueLeaves } from './dsl.ts';
import type { Concept, Facts, Finding, Knowledge, Rule } from './types.ts';

export interface Evidence {
  finding: Finding; rule: Rule; palace: string | null;
  reading: string; core: string; bookCondition: string; chartCondition: string;
  presentStars: string[]; concepts: Array<{ id: string; clause: string; group: number }>;
  polarity: '+' | '-' | '~'; modality: 'tendency' | 'potential' | 'condition' | 'limitation';
  root: string[]; books: string[]; cites: string[];
}

const SCHOOL: Record<string, string> = { SRC_THUC_HANH: 'Thực Hành', SRC_KHAO_LUAN: 'Khảo Luận', SRC_TOAN_THU: 'Toàn Thư', SRC_TVDS_TAN_BIEN: 'Tân Biên' };
const EDITORIAL = ["'", '‘', '“', 'sách ', 'đây là', 'câu ', 'độ sáng', 'cùng nhận định', 'chưa ', 'đọc là', 'nhưng sách', 'bảng ', 'tức ', 'gọi là', 'mùa lấy theo', 'ngưỡng ', 'hệ thống '];
const CONTRAST = [' nhưng ', ' mà ', ' song ', ' tuy '];
const NORM: Record<string, string> = {
  'palace.own_major_stars': 'own', 'palace.own_stars': 'own', 'palace.tam_phuong_stars': 'tp', 'palace.tam_phuong_majors': 'tp',
  'palace.tam_phuong_tu_hoa': 'tp', 'palace.rel.tp_hoa': 'tp', 'palace.tu_hoa': 'own', 'palace.rel.opp_stars': 'opp', 'palace.rel.opp_majors': 'opp',
  'palace.neighbor_stars': 'nb', 'palace.neighbor_majors': 'nb', 'palace.rel.flank_prev_stars': 'nb', 'palace.rel.flank_next_stars': 'nb',
  'palace.rel.flank_prev_majors': 'nb', 'palace.rel.flank_next_majors': 'nb',
  // the tam phương as positions.py computes it (self + opposite + two trines), and the trines alone: both read "hội chiếu về"
  'palace.rel.tp_stars': 'tp', 'palace.rel.tp_majors': 'tp', 'palace.rel.trine_stars': 'tp', 'palace.rel.trine_majors': 'tp',
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
  text = [segs[0], ...segs.slice(1).filter(s => s && !EDITORIAL.some(e => s.toLowerCase().startsWith(e)))].join('; ');
  let condition = '', depth = 0, start = -1, last: [number, number] | null = null;
  for (let i = 0; i < text.length; i++) {
    if (text[i] === '(') { if (depth === 0) start = i; depth++; }
    else if (text[i] === ')' && depth) { depth--; if (depth === 0) last = [start, i]; }
  }
  if (last) { condition = text.slice(last[0] + 1, last[1]); text = (text.slice(0, last[0]).trimEnd() + ' ' + text.slice(last[1] + 1).trimStart()).trim(); }
  let core = text.replace(/\btheo sách (đây |là )?/g, '').replace(/\s{2,}/g, ' ').replace(/^[\s;,.]+|[\s;,.]+$/g, '');
  if (!condition && core.includes(': ') && core.split(': ')[0].length <= 45) { const [a, ...b] = core.split(': '); condition = a; core = b.join(': '); }
  return { core: core.trim(), condition: condition.replace(/^theo /, '').trim() };
}

const join = (xs: string[]) => xs.length <= 1 ? (xs[0] ?? '') : xs.slice(0, -1).join(', ') + ' và ' + xs[xs.length - 1];

/** The satisfied leaves in Vietnamese, with the chart's own values ('Kình hoặc Đà' becomes the star actually there). */
export function chartCondition(rule: Rule, facts: Facts, palace: string | null): { text: string; stars: string[] } {
  const own: string[] = [], tp: string[] = [], opp: string[] = [], nb: string[] = [], hoa: string[] = [], extra: string[] = [], dig: Record<string, unknown> = {};
  for (const lf of trueLeaves(rule.conditions, facts)) {
    if (lf.fact === 'palace.name') continue;
    const got = facts[lf.fact], want = Array.isArray(lf.value) ? lf.value : [lf.value];
    const vals = Array.isArray(got) ? want.filter(w => (got as unknown[]).includes(w)) : want;
    const add = (arr: string[]) => vals.forEach(v => typeof v === 'string' && !arr.includes(v) && arr.push(v));
    if (lf.fact.startsWith('palace.dignity.')) dig[lf.fact.slice(15)] = got;
    else if (lf.fact === 'palace.tu_hoa') add(hoa);
    else if (NORM[lf.fact] === 'own') add(own);
    else if (NORM[lf.fact] === 'tp') add(tp);
    else if (NORM[lf.fact] === 'opp') add(opp);
    else if (NORM[lf.fact] === 'nb') add(nb);
    else if (lf.fact === 'palace.branch') {
      // a branch list in a rule is a brightness table: say which, not just where
      const b = (rule.reading ?? '').toLowerCase();
      extra.push(`${palace ?? 'cung'} ở ${got}${/hãm/.test(b) ? ' (thế hãm)' : /(miếu|vượng|đắc|thế sáng)/.test(b) ? ' (thế sáng)' : ''}`);
    }
    else if ((lf.fact === 'palace.tuan' || lf.fact === 'palace.triet') && got) extra.push(`${palace ?? 'cung'} có ${lf.fact.endsWith('tuan') ? 'Tuần' : 'Triệt'}`);
    else if (lf.fact === 'chart.gender') extra.push(`${got} mệnh`);
    else if (lf.fact === 'palace.khi.sat_tp') extra.push(`sát tinh hội về ${palace ?? 'cung'}`);
    else if (lf.fact === 'palace.khi.cat_tp') extra.push(`cát tinh hội về ${palace ?? 'cung'}`);
    else if (lf.fact === 'palace.has_no_major' && got) extra.push(`${palace ?? 'cung'} vô chính diệu`);
    else if (lf.fact === 'palace.is_than' && got) extra.push(`Thân cư ${palace ?? 'cung'}`);
    else if (lf.fact === 'chart.year_branch') extra.push(`${rule.reading?.match(/^([^:]{3,45}):/)?.[1] ?? 'thế Đào – Hồng – Thiên Không'} theo tuổi ${got}`);
  }
  for (const s of Object.keys(dig)) if (!own.includes(s) && !tp.includes(s)) own.push(s);
  const star = (s: string) => dig[s] && dig[s] !== 'unspecified' ? `${s} (${dig[s]})` : s;
  const where = palace ?? 'lá số', parts: string[] = [];
  if (own.length || hoa.length) parts.push(`${join([...own.map(star), ...hoa])} tại ${where}`);
  if (opp.length) parts.push(`${join(opp)} xung chiếu ${where}`);
  const tp2 = tp.filter(x => !own.includes(x) && !hoa.includes(x));
  if (tp2.length) parts.push(`${join(tp2)} hội chiếu về ${where}`);
  if (nb.length) parts.push(`${join(nb)} giáp ${where}`);
  // what the rule requires to be absent (a satisfied `not`): said, or the reading looks unconditional ("cô quân" needs no Tả Hữu)
  const noOwn: string[] = [], noTp: string[] = [];
  for (const lf of absentLeaves(rule.conditions, facts)) {
    const vs = (Array.isArray(lf.value) ? lf.value : [lf.value]).filter((v): v is string => typeof v === 'string');
    if (NORM[lf.fact] === 'own') vs.forEach(v => !noOwn.includes(v) && noOwn.push(v));
    else if (NORM[lf.fact] === 'tp') vs.forEach(v => !noTp.includes(v) && noTp.push(v));
  }
  if (noOwn.length) parts.push(`${where} không có ${join(noOwn)}`);
  if (noTp.length) parts.push(`không có ${join(noTp)} hội chiếu`);
  return { text: [...parts, ...extra].join(', '), stars: [...new Set([...own, ...hoa, ...opp, ...tp2, ...nb])] };
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
    const { core, condition } = splitReading(reading);
    const facts = { ...(base.chart ?? {}), ...(base[f.subject] ?? {}) };
    const cc = chartCondition(rule, facts, f.palace);
    const concepts = lex.match(core);
    const pols = new Set(concepts.map(c => lex.concepts.get(c.id)!.pol));
    let polarity: '+' | '-' | '~' = f.effect === 'limit' ? '-' : pols.has('+') && pols.has('-') ? '~' : pols.has('-') ? '-' : pols.has('+') ? '+' : '~';
    const low = core.toLowerCase();
    const modality = f.effect === 'limit' ? 'limitation' : /có thể/.test(low) ? 'potential' : /\b(nếu|khi|cần|mới|thì)\b/.test(low) ? 'condition' : 'tendency';
    out.push({ finding: f, rule, palace: f.palace, reading, core, bookCondition: condition, chartCondition: cc.text || condition, presentStars: cc.stars,
      concepts, polarity, modality, root: rootOf(rule), books: [...new Set(rule.sourceIds.map(s => SCHOOL[s] ?? s))].sort(), cites: rule.cites });
  }
  return out;
}

export { join as joinVi };
