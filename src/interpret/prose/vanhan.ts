// Vận hạn prose (prose plan P6): one paragraph per đại hạn, in order of age. Every sentence is one of:
//   - where the ten years sit: ages, palace, branch and its chính tinh, exactly as chart.decades has them (computed, TH p.27);
//   - Thiên Lương's tam hợp reading of the year branch against the vận palace (Tử Vi Nghiệm Lý 1974): đắc thời / sinh xuất / khắc nhập /
//     khắc xuất; sinh nhập is never voiced, the book says nothing about it for a vận;
//   - a Khảo Luận / Thực Hành vận reading that fired for this palace (chart.decades[].readings, by rule id), paraphrased in van_han.json;
//     when readings that say "đi lên" and "đi xuống" both fired, neither is voiced and one both-ways sentence stands in their place;
//   - where the vận stem's Hóa Lộc and Hóa Kỵ land (computed). Nothing about what will happen in a given year.
import type { ChartInput, Decade, Knowledge } from '../types.ts';
import { Micro, finish, lowerFirst } from './micro.ts';
import type { ProseParagraph, ProseSentence } from './realize.ts';
import { validateProse } from './validate.ts';

export interface VanHanLibrary {
  status: 'draft' | 'approved';
  rules: Record<string, { reading: string; cites: string[] }>;
  frame: string[]; stars_major: string[]; stars_none: string[];
  tam_hop: Record<'DONG' | 'SINH_XUAT' | 'KHAC_NHAP' | 'KHAC_XUAT', string[]>;
  readings: Record<string, { dir: 'up' | 'down' | 'mixed'; v: string[] }>;
  both: string[]; hoa: string[];
}

/** đại hạn shown: those starting by this age */
export const VAN_HAN_LAST_START = 75;
const GROUPS: Array<{ name: string; branches: string[]; el: string }> = [
  { name: 'Thân Tý Thìn', branches: ['Thân', 'Tý', 'Thìn'], el: 'Thủy' }, { name: 'Dần Ngọ Tuất', branches: ['Dần', 'Ngọ', 'Tuất'], el: 'Hỏa' },
  { name: 'Tỵ Dậu Sửu', branches: ['Tỵ', 'Dậu', 'Sửu'], el: 'Kim' }, { name: 'Hợi Mão Mùi', branches: ['Hợi', 'Mão', 'Mùi'], el: 'Mộc' },
];
const GEN: Record<string, string> = { 'Thủy': 'Mộc', 'Mộc': 'Hỏa', 'Hỏa': 'Thổ', 'Thổ': 'Kim', 'Kim': 'Thủy' };
const CTRL: Record<string, string> = { 'Thủy': 'Hỏa', 'Hỏa': 'Kim', 'Kim': 'Mộc', 'Mộc': 'Thổ', 'Thổ': 'Thủy' };
const groupOf = (b: string) => GROUPS.find(g => g.branches.includes(b))!;

/** Thiên Lương's reading of the year branch's tam hợp against the vận palace's; null for sinh nhập (not voiced). */
export function tamHop(yearBranch: string, vanBranch: string): { kind: keyof VanHanLibrary['tam_hop']; g1: string; g2: string } | null {
  const a = groupOf(yearBranch), b = groupOf(vanBranch);
  const kind = a === b ? 'DONG' : GEN[a.el] === b.el ? 'SINH_XUAT' : CTRL[b.el] === a.el ? 'KHAC_NHAP' : CTRL[a.el] === b.el ? 'KHAC_XUAT' : null;
  return kind ? { kind, g1: a.name, g2: b.name } : null;
}

const fill = (t: string, v: Record<string, string>) => t.replace(/\{([A-Za-z0-9_]+)\}/g, (m, k) => v[k] ?? m);
const joinNames = (xs: string[]) => xs.length < 2 ? xs.join('') : `${xs.slice(0, -1).join(', ')} và ${xs.at(-1)}`;
const toCite = (src: string) => src.replace(/^Khảo Luận\s*/, 'KL ').replace(/^Thực Hành\s*/, 'TH ').replace(/^Toàn Thư\s*/, 'TT ');

export interface VanHanChapter {
  engine: string; kbVersion: string; chapter: 'van_han'; palace: string; schema: string; order: string[]; draft: boolean;
  paragraphs: ProseParagraph[]; text: string; issues: ReturnType<typeof validateProse>['issues']; metrics: ReturnType<typeof validateProse>['metrics']; pass: boolean;
  /** the ages each paragraph speaks of, straight from chart.decades */
  decades: Array<{ age_from: number; age_to: number; palace: string; branch: string }>;
  evidence: { resolved: []; tensions: []; unused: string[]; rules: Record<string, { reading: string; cites: string[]; verified: boolean }>; concepts: Record<string, string>; divergences: [] };
}

export function proseVanHan(chart: ChartInput, k: Knowledge, seed: string, engine: string, allowDraft: boolean, micro?: Micro): VanHanChapter {
  const L = k.prose?.vanhan as VanHanLibrary | undefined;
  const yb = chart.year_gz.split(' ')[1];
  const m = micro ?? new Micro(`${seed}|van_han`, k.prose!.connectives, k.prose!.frames);
  const usable = !!L && (allowDraft || L.status === 'approved');
  const decades = usable ? chart.decades.filter(d => d.age_from <= VAN_HAN_LAST_START) : [];
  const rules: VanHanChapter['evidence']['rules'] = {};
  const cite = (id: string, reading: string, cites: string[]) => { rules[id] = { reading, cites, verified: true }; return id; };
  const S = () => lowerFirst(m.subject());          // {S} never opens a sentence in van_han.json
  const sentence = (text: string, ids: string[], cites: string[]): ProseSentence => {
    const t = finish(text); m.said(t);
    return { text: t, trace: { move: 'TIMING', concepts: [], rules: ids, cites: [...new Set(cites)].sort(), basis: 'sach' } };
  };
  const paragraphs: ProseParagraph[] = [];
  for (const d of decades) {
    const xs: ProseSentence[] = [], key = `vh|${d.index}`;
    const pal = chart.palaces.find(p => p.branch === d.branch)!;
    const stars = pal.major_stars.length ? fill(m.pick(`${key}|stars`, L!.stars_major), { majors: joinNames(pal.major_stars) }) : m.pick(`${key}|none`, L!.stars_none);
    const c0 = L!.rules.VH_CALC_DAI_HAN;
    xs.push(sentence(fill(m.pick(`${key}|frame`, L!.frame), { a: String(d.age_from), b: String(d.age_to), pal: d.palace, br: d.branch, stars }),
      [cite('VH_CALC_DAI_HAN', c0.reading, c0.cites)], c0.cites));
    const th = tamHop(yb, d.branch);
    if (th) {
      const id = `NL_VAN_TAM_HOP_${th.kind}`, r = L!.rules[id];
      xs.push(sentence(fill(m.pick(`${key}|th`, L!.tam_hop[th.kind]), { yb, g: th.g1, g1: th.g1, g2: th.g2, S: S() }), [cite(id, r.reading, r.cites)], r.cites));
    }
    const rd = (d.readings as Array<{ text: string; src: string; rule_id?: string | null }>).filter(r => r.rule_id && L!.readings[r.rule_id]);
    const trend = (dir: string) => rd.filter(r => L!.readings[r.rule_id!].dir === dir && /^VH_(TPVT_SAT|TPVT_CNDL|VCD_SPT)$/.test(r.rule_id!));
    const conflict = trend('up').length > 0 && trend('down').length > 0;
    const voiced = conflict ? rd.filter(r => !trend('up').includes(r) && !trend('down').includes(r)) : rd;
    if (conflict) {
      const both = [...trend('up'), ...trend('down')];
      xs.push(sentence(m.pick(`${key}|both`, L!.both), both.map(r => cite(r.rule_id!, r.text, [toCite(r.src)])), both.map(r => toCite(r.src))));
    }
    for (const r of voiced.slice(0, 3)) {
      const c = L!.readings[r.rule_id!];
      xs.push(sentence(fill(m.pick(`${key}|${r.rule_id}`, c.v), { v_branch: d.branch, S: S() }), [cite(r.rule_id!, r.text, [toCite(r.src)])], [toCite(r.src)]));
    }
    const lo = d.hoa['Hóa Lộc'], ky = d.hoa['Hóa Kỵ'];
    if (lo?.palace && ky?.palace) {
      const c1 = L!.rules.VH_CALC_TU_HOA;
      xs.push(sentence(fill(m.pick(`${key}|hoa`, L!.hoa), { stem: d.stem, lstar: lo.star, lpal: lo.palace, kstar: ky.star, kpal: ky.palace }),
        [cite('VH_CALC_TU_HOA', c1.reading, c1.cites)], c1.cites));
    }
    paragraphs.push({ role: 'course', sentences: xs, text: xs.map(s => s.text).join(' ') });
  }
  const { issues, metrics } = validateProse(paragraphs, []);
  // the ages in each paragraph are the chart's: a frame that names other ages is a blocking error
  paragraphs.forEach((p, i) => {
    const d = decades[i];
    if (!p.sentences[0].text.includes(String(d.age_from)) || !p.sentences[0].text.includes(String(d.age_to)))
      issues.push({ level: 'error', code: 'age_mismatch', where: `p${i + 1}s1`, msg: `${d.age_from}-${d.age_to}: ${p.sentences[0].text}` });
  });
  return {
    engine, kbVersion: k.version, chapter: 'van_han', palace: 'Đại hạn', schema: 'VAN_HAN', order: ['TIMING'], draft: usable && L!.status !== 'approved',
    paragraphs, text: paragraphs.map(p => p.text).join('\n\n'), issues, metrics, pass: !issues.some(i => i.level === 'error'),
    decades: decades.map(d => ({ age_from: d.age_from, age_to: d.age_to, palace: d.palace, branch: d.branch })),
    evidence: { resolved: [], tensions: [], unused: [], rules, concepts: {}, divergences: [] },
  };
}

export type { Decade };
