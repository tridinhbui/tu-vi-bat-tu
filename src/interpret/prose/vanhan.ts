// Vận hạn prose (prose plan P6): one paragraph per đại hạn, in order of age. Every sentence is one of:
//   - where the ten years sit: ages, palace, branch and its chính tinh, exactly as chart.decades has them (computed, TH p.27);
//   - Thiên Lương's tam hợp reading of the year branch against the vận palace (Tử Vi Nghiệm Lý 1974): đắc thời / sinh xuất / khắc nhập /
//     khắc xuất; sinh nhập is never voiced, the book says nothing about it for a vận;
//   - a Khảo Luận / Thực Hành vận reading that fired for this palace (chart.decades[].readings, by rule id), paraphrased in van_han.json;
//     when readings that say "đi lên" and "đi xuống" both fired, neither is voiced and one both-ways sentence stands in their place;
//   - where the vận stem's Hóa Lộc and Hóa Kỵ land (Tứ Hóa by the hạn's stem is a convention, he_thong) with Khảo Luận's meaning of a Hóa in a
//     palace (KL pp.195-197: Lộc brings ease, Kỵ "gây điều không êm ở cung đó"), tied to the natal domain ledger where they land;
//   - the hạn palace related to the natal reading: the domain whose palace it is, and that domain's verdict in the report-wide ledger
//     (reason/ledger.ts), so a hạn never reads a palace as if the natal chapters had not concluded on it;
//   - for the current hạn, the year's lưu stars that land in it (positions, KL pp.41-42);
//   - the closing: the hạn's level on the system indices (indices.ts, a labelled convention), so the prose and the period chart agree. The
//     older closing that counted good and bad sentences is gone.
import type { ChartInput, Decade, Knowledge } from '../types.ts';
import { Micro, finish, lowerFirst } from './micro.ts';
import type { ProseParagraph, ProseSentence } from './realize.ts';
import { validateProse } from './validate.ts';
import { readPalace, type StructureLib } from './deep.ts';
import norms from '../../../engine/data/kg/index_norms.json' with { type: 'json' };
import { computeIndices, luuStars, type IndexNorms } from '../indices.ts';
import { buildLedger, verdictKey, type DomainVerdict, type Ledger } from '../reason/ledger.ts';
import { infer } from './chapter.ts';
import { khaoLuanLines, toanThuLines, trungPhung } from './vanhan_books.ts';

export interface VanHanLibrary {
  status: 'draft' | 'approved';
  rules: Record<string, { reading: string; cites: string[] }>;
  frame: string[]; stars_major: string[]; stars_none: string[];
  tam_hop: Record<'DONG' | 'SINH_XUAT' | 'KHAC_NHAP' | 'KHAC_XUAT', string[]>;
  readings: Record<string, { dir: 'up' | 'down' | 'mixed'; v: string[] }>;
  both: string[]; hoa: string[];
  /** Khảo Luận pp.230-233 (decades[].kl), Toàn Thư nhập hạn ca (decades[].tt), the hạn's Hóa Quyền/Khoa, the closing, the current year */
  kl_rel: Record<string, string[]>; kl_rel_tone: Record<string, '' | 'pos' | 'neg'>; kl_xung: string[]; kl_nhi_hop: string[]; kl_event: string[];
  tt_lead: string[]; hoa_qk: string[]; kl_stage?: string[]; sum: Record<'good' | 'mixed' | 'hard', string[]>;
  year: { frame: string[]; luu_thai_tue: string[]; luu_hoa: string[] };
  /** the hạn's Hóa Lộc / Hóa Kỵ with KL's meaning of a Hóa in a palace, and the natal link where they land */
  hoa_loc: string[]; hoa_ky: string[]; natal_link: Record<'same' | 'domain', string[]> & Partial<Record<'again' | 'same_decade', string[]>>;
  /** the hạn against the one before it on the system indices (review 2026-10-23: the decades told as one course), and what it touches most */
  trend?: Record<'up' | 'down' | 'flat' | 'turn_up' | 'turn_down', string[]>; focus?: string[];
  /** a Khảo Luận p.233 line or the Quyền/Khoa meanings told again in a later hạn: the same sense named with this hạn's stars, shorter */
  kl_again?: Record<string, string[]>; hoa_qk_again?: string[];
  /** the hạn palace's domain and its verdict in the natal ledger */
  ledger_palace: string[]; ledger_limits: string[];
  /** the year's lưu stars landing in the current hạn palace */
  luu: string[];
  /** the closing by the hạn's level on the system indices (0 … 4); when the level runs against the hạn's book sentences, the frame that says so */
  level: Record<string, string[]>; level_against: Record<'low' | 'high', string[]>; level_thin?: string[]; level_word: Record<string, string>;
}
interface KlFacts { src: string; relation: string; verdict: string; xung_controlled: boolean; opp_majors: string[];
  nhi_hop: { branch: string; palace: string; counts: boolean; majors: string[] }; thai_tue_triad: boolean; event: string | null }
type Tt = Array<{ text: string; src: string }>;
/** a nhập hạn ca line that tells of a difficulty */
const HARD = /(hao|khó|trở ngại|rắc rối|hỏng|nợ|bất lợi|mất|tan|kém|tiết chế|giáng)/;

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
  /** index of each decade's first paragraph (a decade has one or two; the year's paragraphs follow the last decade) */
  starts: number[];
  evidence: { resolved: []; tensions: []; unused: string[]; rules: Record<string, { reading: string; cites: string[]; verified: boolean }>; concepts: Record<string, string>; divergences: [] };
}

/** the verdict words of a ledger domain, as the luận chapters say them (content/prose/luan.json ledger.verdict) */
function verdictWords(k: Knowledge, v: DomainVerdict, m: Micro, key: string): string {
  const V = (k.prose?.luan as { ledger?: { verdict?: Record<string, string[]> } } | undefined)?.ledger?.verdict ?? {};
  const xs = V[verdictKey(v)];
  return xs?.length ? m.pick(key, xs) : '';
}
const NORMS = norms as IndexNorms;

export function proseVanHan(chart: ChartInput, k: Knowledge, seed: string, engine: string, allowDraft: boolean, micro?: Micro, ledger?: Ledger): VanHanChapter {
  const L = k.prose?.vanhan as VanHanLibrary | undefined;
  const yb = chart.year_gz.split(' ')[1];
  const m = micro ?? new Micro(`${seed}|van_han`, k.prose!.connectives, k.prose!.frames);
  const usable = !!L && (allowDraft || L.status === 'approved');
  const decades = usable ? chart.decades.filter(d => d.age_from <= VAN_HAN_LAST_START) : [];
  const rules: VanHanChapter['evidence']['rules'] = {};
  const cite = (id: string, reading: string, cites: string[]) => { rules[id] = { reading, cites, verified: true }; return id; };
  const S = () => lowerFirst(m.subject());          // {S} never opens a sentence in van_han.json
  const sentence = (text: string, ids: string[], cites: string[], basis: ProseSentence['trace']['basis'] = 'sach', tone?: 'pos' | 'neg' | 'answer'): ProseSentence => {
    const t = finish(text.replace(/\{S\}/g, () => S())); m.said(t);
    return { text: t, trace: { move: 'TIMING', concepts: [], rules: ids, cites: [...new Set(cites)].sort(), basis, ...(tone ? { tone } : {}) } };
  };
  const ST = k.prose?.structure as StructureLib | undefined;
  const dom = (pal: string) => ST?.domain_short[pal] ?? pal;
  const paragraphs: ProseParagraph[] = [], starts: number[] = [];
  // the natal ledger (one verdict per domain, as the luận chapters tell it) and the hạn levels of the system indices
  const L0 = usable ? (ledger ?? buildLedger(chart, k, infer(chart, k).resolved)) : null;
  const domainAt = (pal: string) => (L0?.domains ?? []).filter(v => v.verdict !== 'chua_du' && v.verdict !== 'khong_ket_luan' && (v.limits[0]?.palace ?? v.supports[0]?.palace ?? null) === pal
    && (!v.part || v.part !== 'kiem' || pal === 'Tài Bạch'));
  const levels = usable && decades.length ? computeIndices(chart, k, NORMS).decades : [];
  const curYear = chart.year?.year, luu = usable && curYear ? luuStars(chart, curYear) : {};
  // a domain's natal verdict is told in full once in the chapter; a later hạn touching it names the domain only (review 2026-10-23: no
  // "nơi xem hôn nhân, vốn …" in every decade)
  const natalTold = new Set<string>(), klTold = new Set<string>();
  let qkTold = false;
  let prevLevel: { level: number; vi: string } | null = null;
  for (const d of decades) {
    const xs: ProseSentence[] = [], key = `vh|${d.index}`, decTold = new Set<string>();
    const pal = chart.palaces.find(p => p.branch === d.branch)!;
    const stars = pal.major_stars.length ? fill(m.pick(`${key}|stars`, L!.stars_major), { majors: joinNames(pal.major_stars) }) : m.pick(`${key}|none`, L!.stars_none);
    const c0 = L!.rules.VH_CALC_DAI_HAN;
    xs.push(sentence(fill(m.pick(`${key}|frame`, L!.frame), { a: String(d.age_from), b: String(d.age_to), pal: d.palace, br: d.branch, stars }),
      [cite('VH_CALC_DAI_HAN', c0.reading, c0.cites)], c0.cites));
    // the hạn palace read as a palace: brightness of its stars and what its tam phương tứ chính bring (deep.ts, no domain line: the frame said it)
    const pr = readPalace(chart, k, d.palace, m, { key: `vh${d.index}`, lead: false });
    xs.push(...pr.structure.filter(x => x.trace.step === 'gist' || x.trace.step === 'tp' || x.trace.step === 'tuan' || x.trace.step === 'triet'));
    // the hạn against the previous one (the same levels as the period chart): a change of two levels or more is a turning point
    // a decade without book evidence ("chưa đủ căn cứ") is not compared, nor is the one after it compared with it
    const lvNow = levels.find(x => x.age_from === d.age_from && !x.insufficient);
    if (lvNow && prevLevel && L!.trend) {
      const j = lvNow.level - prevLevel.level, k2 = j >= 2 ? 'turn_up' : j <= -2 ? 'turn_down' : j > 0 ? 'up' : j < 0 ? 'down' : 'flat';
      const st = sentence(fill(m.pick(`${key}|trend`, L!.trend[k2]), { from: prevLevel.vi, to: lvNow.level_vi }), [], [], 'he_thong', j > 0 ? 'pos' : j < 0 ? 'neg' : undefined);
      st.trace.step = `trend:${k2}`;
      st.trace.note = 'So sánh mức của hai đại hạn liền nhau theo chỉ số tổng hợp của hệ thống (cùng thang với biểu đồ giai đoạn), không phải lời sách.';
      xs.push(st);
    }
    prevLevel = lvNow ? { level: lvNow.level, vi: lvNow.level_vi } : null;
    // what the hạn touches most: the hạn palace's matter and where its Hóa Lộc and Hóa Kỵ land (Tứ Hóa by the hạn stem, he_thong)
    const touched = [...new Set([d.palace, d.hoa['Hóa Lộc']?.palace, d.hoa['Hóa Kỵ']?.palace].filter((x): x is string => !!x))].map(dom);
    if (L!.focus?.length && touched.length >= 2) {
      const st = sentence(fill(m.pick(`${key}|focus`, L!.focus), { list: ((xs: string[]) => xs.some(x => x.includes(',')) && xs.length > 1 ? `${xs.slice(0, -1).join('; ')}; và ${xs.at(-1)}` : joinNames(xs))([...new Set(touched)]) }), [], ['KL pp.195-197'], 'he_thong');
      st.trace.step = 'focus';
      st.trace.note = 'Gom cung hạn và hai cung nhận Hóa Lộc, Hóa Kỵ theo can hạn (thông lệ); không thêm nhận định.';
      xs.push(st);
    }
    // the natal reading of the hạn palace: the domain it is the palace of, and that domain's verdict in the ledger
    for (const v of domainAt(d.palace).slice(0, 1)) {
      natalTold.add(v.id); decTold.add(v.id);
      const vw = verdictWords(k, v, m, `${key}|lv|${v.id}`);
      if (!vw) continue;
      const lim = v.limits.length ? fill(m.pick(`${key}|llim`, L!.ledger_limits), { limits: joinNames([...new Set(v.limits.map(l => l.kind === 'tuan' ? 'Tuần' : l.kind === 'triet' ? 'Triệt' : l.kind === 'ky_carrier' ? `${l.star} hóa Kỵ` : l.kind === 'hoa_ky' ? 'Hóa Kỵ' : l.star ?? ''))].filter(Boolean)) }) : '';
      xs.push({ ...sentence(fill(m.pick(`${key}|ledger`, L!.ledger_palace), { domain: v.label, verdict: vw, limits: lim }), [], [], 'he_thong'), });
      xs.at(-1)!.trace.step = `natal:${v.id}`;
      xs.at(-1)!.trace.ledger = { domain: v.id, verdict: v.verdict, base: v.base };
    }
    // the year's tam hợp against the hạn's: Khảo Luận pp.230-233 reads all five cases; Thiên Lương (NL) is voiced where it adds a view —
    // the đắc thời of the same triad, and the khắc xuất case where it reads the opposite way to Khảo Luận
    const kl = (d as unknown as { kl?: KlFacts }).kl, th = tamHop(yb, d.branch);
    if (th?.kind === 'DONG') {
      const id = 'NL_VAN_TAM_HOP_DONG', r = L!.rules[id];
      xs.push(sentence(fill(m.pick(`${key}|th`, L!.tam_hop.DONG), { yb, g: th.g1 }), [cite(id, r.reading, r.cites)], [...r.cites, 'KL pp.230-233'], 'sach', 'pos'));
    } else if (kl && L!.kl_rel[kl.relation]) {
      xs.push(sentence(fill(m.pick(`${key}|kl`, L!.kl_rel[kl.relation]), { yb }), [], [kl.src.replace('Khảo Luận', 'KL')], 'tinh_toan', (L!.kl_rel_tone[kl.relation] || undefined) as 'pos' | 'neg' | undefined));
      if (th?.kind === 'KHAC_XUAT') {
        const id = 'NL_VAN_TAM_HOP_KHAC_XUAT', r = L!.rules[id];
        xs.push(sentence(fill(m.pick(`${key}|th`, L!.tam_hop.KHAC_XUAT), { yb }), [cite(id, r.reading, r.cites)], r.cites));
      }
    }
    if (kl?.xung_controlled) xs.push(sentence(fill(m.pick(`${key}|xung`, L!.kl_xung), { opp: chart.palaces.find(p => p.branch_index === (pal.branch_index + 6) % 12)!.name }), [], ['KL pp.230-233'], 'tinh_toan', 'pos'));
    if (kl?.nhi_hop.counts && kl.nhi_hop.majors.length) xs.push(sentence(fill(m.pick(`${key}|nh`, L!.kl_nhi_hop), { nh: `${kl.nhi_hop.palace} (${kl.nhi_hop.branch})`, majors: joinNames(kl.nhi_hop.majors) }), [], ['KL pp.230-233'], 'tinh_toan'));
    if (kl?.event) xs.push(sentence(fill(m.pick(`${key}|ev`, L!.kl_event), { pal: d.palace, event: kl.event }), [], ['KL pp.230-233'], 'tinh_toan'));
    // Khảo Luận pp.234-235: the stage of life this palace stands for in the chart's direction of the hạn
    const klb = khaoLuanLines(chart, d);
    if (klb.stage && L!.kl_stage?.length) { const b = klb.stage; xs.push(sentence(fill(m.pick(`${key}|stage`, L!.kl_stage), { pal: d.palace, stage: b.text }), [cite(b.id, b.text, [b.cite])], [b.cite], 'sach')); xs.at(-1)!.trace.step = 'stage'; }
    const mid = xs.length;                                 // paragraph 2 starts here: what happens in the hạn
    // Khảo Luận p.233: the hạn's chính tinh and hung tinh đắc / hãm, Tuần / Triệt that giải, a hung tinh with its quan thầy; pp.235-236: the
    // opening sentence of a Sát / Phá / Tham hạn
    for (const b0 of klb.lines) {
      // the same p.233 rule in a later hạn: the sense said with this hạn's stars (the rule and page are the same)
      const ak = b0.id.slice(7), alt = klTold.has(b0.id) ? L!.kl_again?.[ak] : undefined;
      const tt = [pal.tuan ? 'Tuần' : '', pal.triet ? 'Triệt' : ''].filter(Boolean);
      const b = alt?.length ? { ...b0, text: finish(fill(m.pick(`${key}|kla|${ak}`, alt), { majors: joinNames(pal.major_stars), tt: joinNames(tt) })) } : b0;
      klTold.add(b0.id);
      const st = sentence(b.text, [cite(b.id, b.text, [b.cite])], [b.cite], 'sach', (b.tone || undefined) as 'pos' | 'neg' | undefined); st.trace.step = b.id; xs.push(st); }
    // Toàn Thư nhập hạn ca (pp.96-106, page-checked): what the stars of the hạn palace bring, read with the hạn's own Tứ Hóa
    for (const b of toanThuLines(chart, d, 2)) {
      const st = sentence(fill(m.pick(`${key}|tt|${b.id}`, L!.tt_lead), { t: b.text, T: b.text.charAt(0).toLocaleUpperCase("vi") + b.text.slice(1) }), [cite(b.id, b.text, [b.cite])], [b.cite], 'sach', (b.tone || undefined) as 'pos' | 'neg' | undefined);
      st.trace.step = b.id; xs.push(st);
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
      xs.push(sentence(fill(m.pick(`${key}|${r.rule_id}`, c.v), { v_branch: d.branch, S: S() }), [cite(r.rule_id!, r.text, [toCite(r.src)])], [toCite(r.src)], 'sach', c.dir === 'up' ? 'pos' : c.dir === 'down' ? 'neg' : undefined));
    }
    // the hạn stem's Hóa Lộc and Hóa Kỵ: where they land (Tứ Hóa by the hạn's stem: a convention, he_thong), what a Hóa does to the palace
    // it lands in (KL pp.195-197), and the natal domain they touch; a Hóa landing in the hạn palace itself says so
    for (const [h, tpl] of [['Hóa Lộc', L!.hoa_loc], ['Hóa Kỵ', L!.hoa_ky]] as const) {
      const x = d.hoa[h];
      if (!x?.palace) continue;
      const v = domainAt(x.palace)[0], vw = v ? verdictWords(k, v, m, `${key}|hv|${h}`) : '';
      const again = v && decTold.has(v.id) ? L!.natal_link.same_decade : v && natalTold.has(v.id) ? L!.natal_link.again : undefined;
      const natal = x.palace === d.palace ? m.pick(`${key}|same|${h}`, L!.natal_link.same)
        : v && vw && again?.length ? fill(m.pick(`${key}|nla|${h}`, again), { domain: v.label })
        : v && vw ? fill(m.pick(`${key}|nl|${h}`, L!.natal_link.domain), { domain: v.label, verdict: vw }) : '';
      if (v) { natalTold.add(v.id); decTold.add(v.id); }
      const st = sentence(fill(m.pick(`${key}|${h}`, tpl), { stem: d.stem, star: x.star, pal: x.palace, dom: dom(x.palace) }), [], ['KL pp.195-197'], 'he_thong', h === 'Hóa Kỵ' ? 'neg' : 'pos');
      st.trace.step = `hoa:${h}`;
      st.trace.note = 'Tứ Hóa theo can của cung đại hạn là thông lệ; nghĩa của một Hóa đóng ở một cung theo Khảo Luận tr.195-197.';
      xs.push(st);
      // where the Hóa lands, in the natal reading: its own short sentence
      if (natal) { const nl = sentence(natal, [], [], 'he_thong'); nl.trace.step = `natal:${v && x.palace !== d.palace ? v.id : 'same'}`; if (v && x.palace !== d.palace) nl.trace.ledger = { domain: v.id, verdict: v.verdict, base: v.base }; xs.push(nl); }
    }
    // the hạn's Hóa Quyền and Hóa Khoa: where they land (KL pp.195-197 on what each Hóa is)
    const q = d.hoa['Hóa Quyền'], kh = d.hoa['Hóa Khoa'], M = k.reference?.tuHoa?.meaning ?? {};
    if (q?.palace && kh?.palace && L!.hoa_qk?.length && M['Hóa Quyền'] && M['Hóa Khoa']) {
      const short = (x: string) => x.replace(/\s*\(.*\)$/, '');
      // what Quyền and Khoa stand for is said once in the chapter; later hạn name where they land
      const qkT = qkTold && L!.hoa_qk_again?.length ? L!.hoa_qk_again : L!.hoa_qk;
      qkTold = true;
      const st = sentence(fill(m.pick(`${key}|qk`, qkT), { qstar: q.star, qpal: q.palace, qmean: short(M['Hóa Quyền']), cstar: kh.star, cpal: kh.palace, cmean: short(M['Hóa Khoa']) }), [], ['KL pp.195-197'], 'he_thong', 'pos');
      st.trace.step = 'hoa:qk';
      st.trace.note = 'Tứ Hóa theo can của cung đại hạn là thông lệ; nghĩa của mỗi Hóa theo Khảo Luận tr.195-197.';
      xs.push(st);
    }
    // the current hạn: the year's lưu stars that land in it (KL pp.41-42; positions only)
    if (chart.year?.dai_han?.age_from === d.age_from && curYear) {
      const here = Object.entries(luu).filter(([, p]) => p === d.palace).map(([s0]) => s0);
      if (here.length) { const st = sentence(fill(m.pick(`${key}|luu`, L!.luu), { year: String(curYear), stars: joinNames(here) }), [], ['KL pp.41-42'], 'tinh_toan'); st.trace.step = 'luu'; xs.push(st); }
    }
    // closing: the hạn's level on the system indices (the same level the period chart shows), then the hạn palace's advice line
    const lvx = levels.find(x => x.age_from === d.age_from), lv = lvx?.level;
    if (lvx?.insufficient && L!.level_thin?.length) {
      // no book evidence: the default middle is said as such, never as a real middle (owner's decision 2026-10-24)
      const st = sentence(m.pick(`${key}|thin`, L!.level_thin), [], [], 'he_thong', 'answer');
      st.trace.step = `level:${lv}`;
      st.trace.note = 'Chặng không có câu sách hay sao nào đã đối chiếu độ sáng để xét: biểu đồ để mức “Trung bình” mặc định, ghi “chưa đủ căn cứ”.';
      xs.push(st);
    } else if (lv !== undefined && L!.level?.[String(lv)]?.length) {
      // a level that runs against the book sentences of the hạn says so, and why (the other layers of the index weigh more)
      const book = xs.filter(x => x.trace.basis === 'sach' || x.trace.basis === 'tinh_toan'), up = book.filter(x => x.trace.tone === 'pos').length, down = book.filter(x => x.trace.tone === 'neg').length;
      // the indices' own book side counts too (KL p.233: a hạn in the Thái Tuế triad is "gặp thời" whatever its level; owner's plan 2026-10-24:
      // a level against the books is explained, never left bare)
      const S = (lvx?.items ?? []).filter(i => i.basis === 'sach' || i.basis === 'sach_dien_giai').reduce((a, i) => a + (i.side === 'support' ? i.w : -i.w), 0);
      const against = lv <= 1 && (up > down || S > 0) ? 'low' : lv >= 3 && (down > up || S < 0) ? 'high' : null;
      const text = against && L!.level_against?.[against]?.length ? fill(m.pick(`${key}|lva`, L!.level_against[against]), { w: L!.level_word[String(lv)] }) : m.pick(`${key}|level`, L!.level[String(lv)]);
      const st = sentence(text, [], [], 'he_thong', 'answer');
      st.trace.step = `level:${lv}`;
      st.trace.note = 'Mức của chặng theo chỉ số hệ thống (thông lệ, xếp theo phân vị của 1.000 lá số mẫu), cùng mức với biểu đồ ở phần Tổng quan.';
      xs.push(st);
    }
    xs.push(...pr.balance.filter(x => (lv ?? 2) < 3 || x.trace.step === 'advice'));
    // one paragraph for where the hạn sits and how it meets the year, one for what happens in it
    // a first paragraph that would only name the hạn palace is not a paragraph of its own: the hạn is told in one
    const cut = mid > 1 ? mid : 0;
    starts.push(paragraphs.length);
    for (const part of [xs.slice(0, cut), xs.slice(cut)]) if (part.length) paragraphs.push({ role: 'course', sentences: part, text: part.map(s => s.text).join(' ') });
  }
  if (usable) paragraphs.push(...yearParagraphs(chart, k, L!, m, S, sentence, dom));
  const { issues, metrics } = validateProse(paragraphs, []);
  // the ages in each paragraph are the chart's: a frame that names other ages is a blocking error
  starts.forEach((pi, i) => {
    const d = decades[i], p = paragraphs[pi];
    if (!p.sentences[0].text.includes(String(d.age_from)) || !p.sentences[0].text.includes(String(d.age_to)))
      issues.push({ level: 'error', code: 'age_mismatch', where: `p${pi + 1}s1`, msg: `${d.age_from}-${d.age_to}: ${p.sentences[0].text}` });
  });
  return {
    engine, kbVersion: k.version, chapter: 'van_han', palace: 'Đại hạn', schema: 'VAN_HAN', order: ['TIMING'], draft: usable && L!.status !== 'approved',
    paragraphs, text: paragraphs.map(p => p.text).join('\n\n'), issues, metrics, pass: !issues.some(i => i.level === 'error'),
    decades: decades.map(d => ({ age_from: d.age_from, age_to: d.age_to, palace: d.palace, branch: d.branch })),
    starts,
    evidence: { resolved: [], tensions: [], unused: [], rules, concepts: {}, divergences: [] },
  };
}

/** The requested year (chart.year): where the year sits in the đại hạn, its tiểu hạn palace read like a hạn (Khảo Luận pp.230-233, Toàn
 *  Thư nhập hạn ca), the lưu Thái Tuế palace, and the year stem's lưu Tứ Hóa with Khảo Luận's per-star advice (pp.195-197). */
function yearParagraphs(chart: ChartInput, k: Knowledge, L: VanHanLibrary, m: Micro, S: () => string,
  sentence: (text: string, ids: string[], cites: string[], basis?: ProseSentence['trace']['basis'], tone?: 'pos' | 'neg' | 'answer') => ProseSentence,
  dom: (pal: string) => string): ProseParagraph[] {
  const y = chart.year as ChartInput['year'] & { tieu_han_kl?: KlFacts; tieu_han_tt?: Tt; luu_tu_hoa_reading?: Array<{ hoa: string; star: string; palace: string | null; advice?: string | null; position_note: string | null }> };
  if (!y?.tieu_han_palace || !y.dai_han) return [];
  const key = `ln|${y.year}`, xs: ProseSentence[] = [], ys: ProseSentence[] = [];
  const th = chart.palaces.find(p => p.name === y.tieu_han_palace)!;
  xs.push(sentence(fill(m.pick(`${key}|frame`, L.year.frame), { year: String(y.year), pillar: y.annual_pillar ?? '', S: S(), age: String(y.age_tuoi_mu), dh_from: String(y.dai_han.age_from),
    dh_to: String(y.dai_han.age_to), dh_pal: y.dai_han.palace, th_pal: th.name, th_br: th.branch, th_dom: dom(th.name) }), [], ['TH p.27'], 'tinh_toan'));
  const kl = y.tieu_han_kl;
  if (kl && L.kl_rel[kl.relation]) xs.push(sentence(fill(m.pick(`${key}|kl`, L.kl_rel[kl.relation]).replace(/mười năm này/g, 'năm này').replace(/[Cc]ung hạn/g, x => x[0] === 'C' ? 'Cung tiểu hạn' : 'cung tiểu hạn'), { yb: chart.year_gz.split(' ')[1] }),
    [], ['KL pp.230-233'], 'tinh_toan', (L.kl_rel_tone[kl.relation] || undefined) as 'pos' | 'neg' | undefined));
  // Thực Hành p.119: đại hạn and tiểu hạn on one palace
  const tp = trungPhung(y.tieu_han_palace, y.dai_han?.palace);
  if (tp) xs.push(sentence(tp.text, [tp.id], [tp.cite], 'sach'));
  if (y.luu_thai_tue_palace) xs.push(sentence(fill(m.pick(`${key}|ltt`, L.year.luu_thai_tue), { pal: y.luu_thai_tue_palace, dom: dom(y.luu_thai_tue_palace) }), [], [], 'pho_thong'));
  for (const r of y.luu_tu_hoa_reading ?? []) {
    if (!r.palace) continue;
    // what the Hóa brings to the palace it lands in (pho_thong card); Khảo Luận's own position note is generic or lists other palaces
    // what the Hóa does to the palace it lands in: Khảo Luận's own position note (pp.195-197), never a phổ thông card
    const note = r.position_note && r.hoa !== 'Hóa Quyền' ? `, ${r.position_note}` : '';
    ys.push(sentence(fill(m.pick(`${key}|${r.hoa}`, L.year.luu_hoa), { hoa: r.hoa, pillar: y.annual_pillar ?? '', star: r.star, pal: r.palace, note, advice: r.advice ? `; ${r.advice}` : '' }), [], ['KL pp.195-197'], 'tinh_toan',
      r.hoa === 'Hóa Kỵ' ? 'neg' : 'pos'));
  }
  // what holds the year up and what to do: the tiểu hạn palace's balance (deep.ts)
  ys.push(...readPalace(chart, k, th.name, m, { key: key, lead: false }).balance);
  return [xs, ys].filter(p => p.length).map(p => ({ role: 'course' as const, sentences: p, text: p.map(s => s.text).join(' ') }));
}

export type { Decade };
