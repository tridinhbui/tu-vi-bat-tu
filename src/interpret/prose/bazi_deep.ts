// Bát Tự structure prose (plan async-inventing-fairy C, deepened by plan quirky-tinkering-rabin Track C and by the 2026-10-22 depth pass): what
// the structure analysis (engine/tvbt/bazi_deep, facts.bazi.deep) computes, told chapter by chapter. Only books and calculation (owner's
// decision 2026-10-21: no common meanings). Basis per sentence:
//   - sach: a verified rule that fired, with its id (BT_TVH_* on strength and on the cách's thành bại, TVH pp.367-369; the Trích Thiên Tủy
//     rules on hàn noãn, nguyên lưu, Quan Sát hỗn tạp, Thương Quan, tòng / hóa; the TTT 歲運 rules on luck pillars and years; the printed note
//     of the điều hậu cell, TVH pp.391-397);
//   - tinh_toan: a computed fact or a page-cited table or mechanism (TVH score pp.331-355 taken apart: degrees, the month's ±1/5, roots, ngũ
//     hợp hóa or not; TVH dụng thần and vận hỷ kỵ table pp.378-386 with the book's reasons pp.377-383; hỉ / kị thần by relation and the luck
//     halves, p.382; the TVH điều hậu table pp.389-396; the 八字真宗 tables: ten gods p.17, hợp xung hình hại phá pp.19-20, nạp âm pp.20-21,
//     thần sát pp.21-22, trường sinh pp.24-25, the marriage and spouse palaces p.57);
//   - minh_hoa: a pre-written illustration attached to exactly one sourced sentence (trace.attach), making it concrete; no new claim, no event
//     or time, no health (owner policy 2026-10-22);
//   - he_thong: the closing words that re-say what the paragraph already told (advice, the summary over the timeline).
// Readability (2026-10-22): the text names no book, page, table or method (they are in each sentence's note and the Căn cứ fold); every chapter
// gives a short reading first and puts the mechanism in paragraphs marked depth 'sau', which the report folds under "Đọc sâu".
// The relations between a luck pillar or a year and the natal pillars are told as positions: 八字真宗 pp.19-20 prints the tables only, no
// meanings; what they do to the useful god is told by TVH p.382 (what khắc, xung or hợp the useful god is kị thần).
// Method reconciliation (plan quirky-tinkering-rabin step 3, S2): every luck pillar and year gets ONE verdict from the cách table (TVH
// pp.378-386) and the điều hậu table (pp.389-396), by stem name (`reconcile`, mirrored from bazi_deep.pipeline.reconcile for older facts).
// Phù ức is a draft method and nothing here reasons by it.
import type { ChartInput, Knowledge } from '../types.ts';
import { Micro, finish, lowerFirst } from './micro.ts';
import type { ProseParagraph, ProseSentence, SentenceTrace } from './realize.ts';

type Role = 'yong' | 'xi' | 'ji' | null;
type Verdict = 'tot' | 'xau' | null;
export interface BaziEvent { kind: string; targets: string[]; part: 'stem' | 'branch' | 'pillar'; opens_kho?: boolean; element?: string | null }
export interface BaziTouch { kind: string; part: 'stem' | 'branch'; who: string; stem?: string; target?: string; target_stem?: string; target_branch?: string; targets?: string[]; target_stems?: string[] }
export interface BaziWhy { key: string; text: string; page: string }
/** a temporal pillar (luck or year) as computed facts: ten gods, hidden stems, growth stage of the day master, the TVH table's verdicts */
export interface BaziTemporal {
  stem?: string; branch?: string; branch_god?: string; hidden?: Array<{ stem: string; ten_god: string }>; stage?: string;
  stem_group?: string; branch_group?: string; stem_element?: string; branch_element?: string; tvh?: { stem: Verdict; branch: Verdict };
  can_chi_detail?: { relation: string; mitigated: boolean; aggravated: boolean } | null; events?: BaziEvent[];
  /** the combined verdict (bazi_deep.pipeline.reconcile); absent in facts older than it, then computed here the same way */
  reconcile?: Reconcile;
  /** the luck pillar's years whose stem the cách table calls good or the điều hậu cell names (absent in older facts) */
  good_years?: Array<{ year: number; pillar: string; group: string; why: string[]; verdict?: string }>; first_year?: number;
  /** depth (2026-10-22): what it does to the useful god (TVH p.382), why the table calls its stem / branch good or bad (pp.377-382) */
  touch?: BaziTouch[]; why?: { stem: BaziWhy[] | null; branch: BaziWhy[] | null };
  halves?: { stem: [number, number]; branch: [number, number] } | null;
  luck_half?: { part: 'stem' | 'branch'; index: number; verdict: Verdict } | null;
}
export interface Reconcile {
  cach: 'tot' | 'xau' | 'tron' | null; climate: 'thuan' | null; warm: boolean; agree: 'cung' | 'khac' | 'tron' | 'mot_phia' | 'khong';
  verdict: 'thuan' | 'kha_thuan' | 'co_dieu_kien' | 'nang' | 'trung';
  support?: Array<{ stem: string; ten_god: string; group: string; why: string[] }>;
}
/** bazi_deep.depth: the why behind the verdicts (absent in facts older than 2026-10-22) */
export interface BaziDepth {
  score: { own_elements: string[]; own: number; total: number; need: number; gap: number; gap_stems: number; lenh: string; lenh_minus: string | null;
    share_without_lenh: number; lenh_decides: boolean; heaven_own: number; earth_own: number;
    elements: Array<{ el: string; group: string; heaven: number; earth: number; lenh: '+' | '-' | null; total: number }> };
  stems: { stems: Array<{ pillar: string; stem: string; ten_god: string; element: string; deg: number; rooted: boolean;
    hop?: { with: string; with_stem: string; el: string; outcome: 'hoa' | 'khong_hoa' | 'tranh_hop' | 'hu_phu'; why: string | null; victim: boolean | null };
    khac?: { by: string[]; by_stem: string[]; loss: number; kep: boolean }; tru?: { kind: string; loss: number; branch: string } }>;
    dm_roots: Array<{ pillar: string; branch: string; stem?: string; same?: boolean; main?: boolean; via?: string }>; dm_rooted: boolean; dm_root_main?: boolean; hua_day: string | null };
  units: Array<{ kind: string; kind_vi: string; el: string; pillars: string[]; branches: string[]; hoa: boolean }>;
  flow: { groups: Array<{ group: string; el: string; deg: number; share: number }>; there: Record<string, Array<{ pillar: string; part: 'stem' | 'branch'; stem: string }>>;
    links: Array<{ from: string; to: string; visible: boolean }> };
  yong: { kind: 'cach' | 'special'; group: string; el: string; first: string; fallback: boolean; why: { text: string; page: string } | null; dm: string | null; dominant: string | null;
    alternatives: Array<{ group: string; el: string; present: boolean; visible: boolean | unknown[]; hidden: Array<{ pillar: string; branch: string; stem: string; main: boolean }> }>;
    hy: { group: string; el: string }; ky: { group: string; el: string };
    natal: Array<{ kind: string; part: string; pillar: string; who: string; with?: string; with_stem?: string; with_branch?: string }>;
    table_vs_relation?: { hy_in_tot: boolean; hy_in_xau: boolean; ky_in_xau: boolean; ky_in_tot: boolean } } | null;
  dh_note: { cell: string; say: string; page: string; cuc: Array<{ el: string; formed: boolean }>; id: string; text?: string } | null;
}
export interface BaziDeep {
  strength: { dm_strong: boolean | null; own_share: number | null; threshold: number | null; season_state: string | null; tvh_totals?: Record<string, number>; near_threshold?: boolean };
  climate: { label: string | null; han_noan: string | null };
  dieu_hau: { cell: string | null; need: string[]; avoid: string[]; satisfied: boolean | null; verified: boolean;
    stems: Array<{ stem: string; ten_god: string; rank: string; visible: boolean; hidden: boolean }>;
    /** the stems the cell names, chính first; need/avoid above are the system's cold/heat index (need_src he_thong) */
    table?: string[]; need_src?: string; need_rule?: string | null; need_rule_element?: string | null };
  phu_uc: Array<{ level: string; yong: string[]; xi: string[]; ji: string[] }>;
  geju: { inner: Array<{ name: string; state: string | null }>; outer: Array<{ name: string; quality: string | null }> };
  cach_tvh?: { status: string | null; cach: string | null; dm: string | null; dominant: string | null; yong: string[]; van_tot: string[]; van_xau: string[]; page: string | null;
    special: string | null; special_tot: string[]; special_xau: string[] };
  pillars?: Record<'year' | 'month' | 'day' | 'hour', { nap_am: string; stage: string }>;
  shensha?: Array<{ vi: string; kind: 'cat' | 'trung' | 'hung'; pillar: string; at: string; gloss: string | null }>;
  verified: Array<{ rule_id: string; claim: string; text: string; verdict?: 'tot' | 'xau' }>;
  luck: Array<BaziTemporal & { index: number; pillar: string; ten_god: string | null; level: string | null; effect: string | null; can_chi: string[];
    dieu_hau: { stem: Role; branch: Role }; findings: Array<{ rule_id: string; text: string }> }>;
  years?: Array<BaziTemporal & { year: number; pillar: string; luck: string | null; ten_god: string; dieu_hau: { stem: Role; branch: Role }; findings: Array<{ rule_id: string; text: string }> }>;
  depth?: BaziDepth | null;
}
/** the depth frames (content deep.d) and the minh họa library (deep.mh) */
export interface DepthFrames {
  str_deg: string[]; str_deg_near: string[]; side: Record<string, string>; other: string[]; own_big: string[]; lenh: string[]; lenh_plus_own: string; lenh_minus_own: string;
  lenh_same?: string[]; lenh_flip: string[]; gap_weak: string[]; gap_strong: string[]; gap_lt1: string; gap_n: string; where: string[]; where_vi: Record<string, string>;
  roots: string[]; roots_no_main: string; roots_none: string[]; hop_dm_khong: string[]; hop_victim_dm: string; hop_victim_other: string; hop_other_khong: string[];
  hop_dm_hoa: string[]; hop_other_hoa: string[]; hop_why: Record<string, string>; tranh: string[]; hu_phu: string[]; khac: string[]; khac_how: Record<string, string>;
  unit_hoa: string[]; unit_khong: string[]; groups: string[]; hv: string[]; chain: string[]; an_vis: string[]; an_hid: string[]; an_none: string[];
  out_vis: string[]; out_hid: string[]; qs_hit: string[]; yong_why: string; fallback: string[]; natal_khac: string; natal_sinh: string; natal_sinh_first?: string; natal_no_sinh: string; ky_in_tot?: string[]; ky_in_tot_plain?: string[]; hy_in_xau?: string[];
  natal_open: string[]; natal_none: string[]; natal_hop: string; natal_xung: string; hyky: string[]; hy_unlisted: string[]; dh_note: string[]; dh_cuc: Record<'yes' | 'no', string>;
  why: Record<string, string[]>; why_one: string[]; why_two: string[]; why_both?: string[]; group_def?: Record<string, string>; why_and: string; halves: string[]; halves_tail: Record<'first' | 'second', string>;
  touch: string[]; touch_year?: string[]; touch_kind: Record<string, string>; year_half: string[]; year_half_tail: string; tk_diag: string[]; tk_diag_heat: string; tk_diag_special: string[];
  tk_turn: string[]; tk_turn_what: Record<string, string>; special_yong?: string[]; special_pick?: string[]; dom_skip?: string[];
  cach_status?: string[]; cach_cond?: string[]; cach_cond_year: string; tk_cond?: string[]; vs_luck?: string[]; vs_luck_none?: string[]; vs_luck_kind?: Record<string, string>;
  tai_layers?: Record<'pos' | 'dm' | 'method' | 'method_no_tb' | 'decide', string[]>;
}
export interface BaziDeepFrames {
  season: string[]; season_state: Record<string, string>; strength_near: string[]; strength_side: string[]; climate: string[]; climate_presence: string[];
  verified_text: Record<string, string>;
  // Track C
  frame2: string[]; frame2_no_need: string[]; season_name: Record<string, string>; stages: string[]; stage_turn: string[]; totals: string[];
  ev_open_year?: string[]; cach_first: string[]; tb_next: string[]; tb_turn: string[]; table: string[]; table_no_van: string[]; table_special: string[]; dh_turn: string[]; advice: string[];
  shensha: string[]; shensha_hung: string[]; shensha_plain: string[];
  luck_head: string[]; luck_head_short: string[]; luck_now: string; tvh_both: string[]; tvh_same: string[]; tvh_split: string[]; tvh_one: string[]; tvh_none: string[]; verdict: Record<string, string>;
  ev_open: string[]; ev_none: string[]; ev_kind: Record<string, string>; spouse_first: string; spouse_next: string; marriage: string;
  year_head: string[]; year_luck: Record<string, string>; year_advice: string[];
  tk_open: string[]; tk_phase: string[]; tk_phase_name: string[]; tk_class: Record<string, string>; tk_class_many: Record<string, string>; tk_advice: string[];
  premise: Record<string, 'strong' | 'weak'>;
  // S2 reconciliation
  dh_role: Record<string, string>; yong_where: Record<string, string>; reliability: string[]; conclusion_split: string[];
  rc_khac: string[]; rc_support: string[]; rc: Record<string, string[]>; rc_years: string; rc_note: string;
  // 2026-10-22 depth
  d?: DepthFrames; mh?: Record<string, string[]>;
}
/** the part of the chapter frame a paragraph holds (plan step 4); the sources, part 6, are each sentence's trace */
export type FramePart = 'cau_truc' | 'ho_tro' | 'tuong_tac' | 'mau_thuan' | 'ket_luan';
export type BaziDeepChapter = 'nhat-chu' | 'ngu-hanh' | 'su-nghiep' | 'quan-he' | 'dai-van' | 'cach-cuc' | 'luu-nien' | 'tong-ket';

const join = (xs: string[]) => xs.length < 2 ? (xs[0] ?? '') : `${xs.slice(0, -1).join(', ')} và ${xs.at(-1)}`;
const fill = (t: string, v: Record<string, string>) => t.replace(/\{([A-Za-z0-9_]+)\}/g, (m, k) => v[k] ?? m);
const PIL_VI: Record<string, string> = { year: 'năm', month: 'tháng', day: 'ngày', hour: 'giờ', luck: 'đại vận', year_t: 'năm' };
const K = ['year', 'month', 'day', 'hour'] as const;
/** 69 -> "69", 57.6 -> "57,6" */
const num = (v: number) => String(Math.round(v * 10) / 10).replace('.', ',');
const cap = (s: string) => s.charAt(0).toLocaleUpperCase('vi') + s.slice(1);
/** a TVH thành bại claim "theo Thiệu Vĩ Hoa (tr.367-369): <condition>: <verdict>" -> its condition and verdict */
export function tbParts(text: string): { cond: string; verdict: string } | null {
  const m = text.replace(/^theo Thiệu Vĩ Hoa \([^)]*\):\s*/, '').match(/^(.*):\s*([^:]+)$/);
  return m ? { cond: m[1].trim(), verdict: m[2].trim() } : null;
}
// the book and pages behind a sentence, said in its note (shown when the sentence is opened), never in the text
const NOTE = {
  score: 'Phép chấm độ vượng suy của Thiệu Vĩ Hoa (Dự Đoán Theo Tứ Trụ, tr.331-355): can có chỗ dựa 36 độ, hư phù 9 độ; chi tháng nắm lệnh +1/5, hành bị nó khắc −1/5; nhật chủ vượng khi phe mình từ 40% tổng độ (tr.355).',
  stems: 'Thiệu Vĩ Hoa tr.332-336: chỗ dựa của thiên can (tr.333), ngũ hợp hóa khi hóa thần cùng hành chi tháng (tr.336), khắc gần −12, cách ngôi −6, kẹp −24 (tr.332).',
  units: 'Thiệu Vĩ Hoa tr.338-346: tam hội 72, tam hợp 60, bán tam hợp 40, lục hợp 36 độ khi hóa; không hóa thì chỉ giữ bản khí.',
  groups: 'Mười thần theo quan hệ ngũ hành với nhật chủ (Bát Tự Chân Tông tr.17); độ theo phép chấm của Thiệu Vĩ Hoa (tr.331-355). Tên các mạch sinh khắc (Tài sinh Quan Sát, Ấn sinh thân, Thực Thương xì hơi nhật chủ) là chữ của Thiệu Vĩ Hoa tr.367-369, 377-383.',
  yong: 'Dụng thần theo cách và lý do chọn: Thiệu Vĩ Hoa tr.377-383 (bệnh và thuốc tr.376-377); danh sách vận tốt xấu tr.382-386.',
  hyky: 'Thiệu Vĩ Hoa tr.382: can chi sinh trợ dụng thần hoặc khắc chế kị thần là hỉ thần; can chi khắc, xung, hợp dụng thần là kị thần; dụng thần không nên bị tổn thương.',
  halves: 'Thiệu Vĩ Hoa tr.382: một đại vận mười năm, thiên can quản năm năm đầu, địa chi quản năm năm sau.',
  dh: 'Bảng điều hậu và lời chú từng ô: Thiệu Vĩ Hoa tr.389-397 (tác giả ghi bảng do một độc giả gửi, chưa rõ xuất xứ, tr.388).',
  van: 'Lý do một nhóm là vận tốt hay xấu: theo định nghĩa hỉ thần, kị thần (Thiệu Vĩ Hoa tr.382) và lý bệnh, thuốc (tr.376-377).',
  tb: 'Đánh giá tốt xấu của chính cách: Thiệu Vĩ Hoa tr.367-369.',
  mh: 'Câu minh họa: chỉ làm cụ thể câu ngay trước, không thêm nhận định.',
};

export function deepBazi(chart: ChartInput, k: Knowledge, m: Micro, F: BaziDeepFrames | undefined,
  rules: Record<string, { reading: string; cites: string[]; verified: boolean }>): Partial<Record<BaziDeepChapter, ProseParagraph[]>> {
  void k;
  const b = chart.bazi as (ChartInput['bazi'] & { deep?: BaziDeep | null }) | undefined, D = b?.deep;
  if (!b || !D || !F) return {};
  const say = (xs: ProseSentence[], text: string, basis: SentenceTrace['basis'], cites: string[] = [], ids: string[] = [], extra: Partial<SentenceTrace> = {}) => {
    const t = finish(text); m.said(t);
    xs.push({ text: t, trace: { move: 'ELABORATE', concepts: [], rules: ids, cites, basis, ...extra } });
  };
  const MH = F.mh, Dd = F.d, P = D.depth ?? null;
  /** an illustration (minh họa) attached to the sourced sentence of step `attach`, which must be the last one said in `xs` */
  const mh = (xs: ProseSentence[], key: string, vars: Record<string, string>, attach: string) => {
    if (!MH?.[key]?.length || !xs.some(s => s.trace.step === attach)) return;
    say(xs, fill(m.pick(`bd|mh|${key}`, MH[key]), vars), 'minh_hoa', [], [], { attach, step: `mh:${attach}`, note: NOTE.mh });
  };
  const fired = new Map(D.verified.map(v => [v.rule_id, v]));
  const cite = (id: string, text: string, cites: string[]) => { rules[id] = { reading: text, cites, verified: true }; return id; };
  const pil = b.pillars, dm = b.day_master, el = b.day_master_element, mb = pil.month.branch;
  const out: Partial<Record<BaziDeepChapter, ProseParagraph[]>> = {};
  const para = (id: BaziDeepChapter, xs: ProseSentence[], role: ProseParagraph['role'] = 'support', extra: Partial<ProseParagraph> = {}) => {
    if (xs.length) (out[id] ??= []).push({ role, sentences: xs, text: xs.map(s => s.text).join(' '), ...extra });
  };
  const deep = (title?: string): Partial<ProseParagraph> => ({ depth: 'sau', ...(title ? { depthTitle: title } : {}) });
  // the 40% rule always decides (TVH p.355, which calls a 39.6% example "hơi nhược"); near the line the reading says "hơi" and the system's
  // ±3% band stays a note (audit BZ-9/10: the reading never gives a third level, nor the system's seven-level label)
  const sh = D.strength.own_share, th = D.strength.threshold, near = D.strength.near_threshold ?? fired.has('BT_TVH_BIEN');
  const strong = D.strength.dm_strong;
  const levelVi = strong == null ? 'ở mức cân bằng' : `${near ? 'hơi ' : ''}${strong ? 'vượng' : 'nhược'}`;
  const CT = D.cach_tvh, dh = D.dieu_hau;
  const tableOk = CT?.status === 'ap_dung' && !!CT.cach;
  // the cách's status (owner review 2026-10-22): 'partial' unless the facts say otherwise; older facts carry no status and read as partial
  const cachPartial = tableOk && (CT as { verification?: string }).verification !== 'verified';
  // the stems the điều hậu cell names (chính first), and the element a fired hàn noãn rule asks for (TTT pp.113-114)
  const table = dh.verified ? (dh.table ?? dh.stems.map(s => s.stem)) : [];
  const needRule = fired.has('BT_TTT_HANNOAN_CAN_NOAN') ? 'BT_TTT_HANNOAN_CAN_NOAN' : fired.has('BT_TTT_HANNOAN_CAN_HAN') ? 'BT_TTT_HANNOAN_CAN_HAN' : '';
  const needEl = needRule === 'BT_TTT_HANNOAN_CAN_NOAN' ? 'Hỏa' : needRule ? 'Thủy' : '';
  const yongG = tableOk ? CT!.yong : [], totG = tableOk ? CT!.van_tot : [], xauG = tableOk ? CT!.van_xau : [];
  const rcOf = (t: BaziTemporal) => t.reconcile ?? reconcileTs(t, dm, table, needEl, yongG, xauG);
  const tvhPage = CT?.page ? `TVH pp.${CT.page.replace(/\s/g, '')}` : 'TVH pp.378-386';
  const Y = P?.yong ?? null;
  // the useful god the reading leans on: the first of the book's order that the chart holds ("không có X thì lấy Y", TVH pp.378-381)
  const Y1 = Y ? Y.group : tableOk ? (CT!.yong[0] ?? '') : '';
  const hoaC = /Hóa/.test(CT?.special ?? '');

  // ---- frame (second sentence): season, điều hậu stems ----
  const frame: ProseSentence[] = [];
  if (D.strength.season_state && sh != null && F.frame2) {
    // the điều hậu cell names stems; the element "cần Hỏa" is the system's cold/heat index and is not told here (it was, as the table's)
    const need = table.length ? join(table) : '';
    say(frame, fill(m.pick('bd|frame2', need ? F.frame2 : F.frame2_no_need), { mb, season: F.season_name[mb] ?? '', el, dm, state: F.season_state[D.strength.season_state]?.split(',')[0] ?? D.strength.season_state,
      need }), 'tinh_toan', ['ZZ (ngũ hành vượng tướng hưu tù tử)', ...(need ? ['TVH pp.389-396'] : [])], [], { step: 'frame:bat_tu:2', ...(need ? { note: NOTE.dh } : {}) });
  }
  if (frame.length) para('nhat-chu', frame, 'structure');

  // ---- nhật chủ, short: the verdict in degrees, with one illustration ----
  const st: ProseSentence[] = [];
  if (D.strength.season_state && !frame.length) say(st, fill(m.pick('bd|season', F.season), { dm, el, mb, state: F.season_state[D.strength.season_state] ?? D.strength.season_state }), 'tinh_toan', ['ZZ (ngũ hành vượng tướng hưu tù tử)']);
  const S = P?.score;
  if (sh != null && th != null && strong != null) {
    const pct = String(Math.round(sh * 100)), thp = String(Math.round(th * 100));
    const id = strong ? 'BT_TVH_VUONG' : 'BT_TVH_NHUOC', v = fired.get(id);
    const src = { basis: (v ? 'sach' : 'tinh_toan') as SentenceTrace['basis'], ids: v ? [cite(id, v.text, ['TVH pp.331-355'])] : [] };
    if (S && Dd) {
      const hua = P?.stems?.hua_day;
      const vars = { el: hua ? `${S.own_elements[0]} mà nhật chủ ${dm} đã hóa thành` : S.own_elements[0], mel: S.own_elements[1], own: num(S.own), total: num(S.total), pct, need: num(S.need), gap: num(Math.abs(S.gap)),
        cmp: strong ? 'trên' : 'dưới', side: near ? (strong ? 'vượng' : 'nhược') : Dd.side[strong ? 'strong' : 'weak'] };
      say(st, fill(m.pick('bd|strdeg', near ? Dd.str_deg_near : Dd.str_deg), vars), src.basis, ['TVH pp.331-355'], src.ids, { step: 'strength', mech: true,
        note: near ? `${NOTE.score} Thiệu Vĩ Hoa (tr.355) gọi một ví dụ 39,6% là "hơi nhược": sát ngưỡng vẫn là một kết luận. Dải ±3% quanh 40% là quy ước hiển thị của hệ thống, không phải của sách.` : NOTE.score });
    } else if (near) say(st, fill(m.pick('bd|near', F.strength_near), { pct, th: thp, cmp: strong ? 'trên' : 'dưới', side: strong ? 'vượng' : 'nhược' }), 'tinh_toan', ['TVH pp.331-355'], [],
      { step: 'strength', note: 'Thiệu Vĩ Hoa (tr.355) gọi một ví dụ 39,6% là "hơi nhược": sát ngưỡng vẫn là một kết luận. Dải ±3% quanh 40% là quy ước hiển thị của hệ thống, không phải của sách.' });
    else say(st, fill(m.pick('bd|side', F.strength_side), { pct, th: thp, cmp: strong ? 'vượt' : 'dưới', side: strong ? 'thuộc thế vượng' : 'thuộc thế nhược' }), src.basis, ['TVH pp.331-355'], src.ids, { step: 'strength', note: NOTE.score });
    const x = num(Math.round(sh * 20) / 2);              // tenths of the whole, to the half
    mh(st, near ? 'strength_near' : strong ? 'strength_strong' : 'strength_weak', { x }, 'strength');
  }
  para('nhat-chu', st);

  // ---- nhật chủ, Đọc sâu 1: how the degrees add up (TVH pp.331-355) ----
  if (S && Dd) {
    const xs: ProseSentence[] = [];
    const cites = ['TVH pp.331-355'], ex = { note: NOTE.score, mech: true, step: 'strength:deg' };
    const els = [...S.elements].sort((a, c) => c.total - a.total);
    const other = els.filter(e => !S.own_elements.includes(e.el)).slice(0, 2), ownTop = els.filter(e => S.own_elements.includes(e.el));
    const item = (e: typeof els[number]) => `${e.el} (${e.group}) ${num(e.total)} độ`;
    if (strong && ownTop[0] === els[0]) say(xs, fill(m.pick('bd|ownbig', Dd.own_big), { list: join(ownTop.map(item)) }), 'tinh_toan', cites, [], ex);
    else if (other.length) say(xs, fill(m.pick('bd|other', Dd.other), { list: join(other.map(item)) }), 'tinh_toan', cites, [], ex);
    if (S.lenh_minus) {
      const own = S.own_elements.includes(S.lenh) ? Dd.lenh_plus_own : S.own_elements.includes(S.lenh_minus) ? Dd.lenh_minus_own : '';
      say(xs, fill(m.pick('bd|lenh', Dd.lenh), { mb, lenh: S.lenh, minus: S.lenh_minus, own }), 'tinh_toan', cites, [], ex);
      if (S.lenh_decides) say(xs, fill(m.pick('bd|lenh2', Dd.lenh_flip), { p0: String(Math.round(S.share_without_lenh * 100)), side: strong ? 'vượng' : 'nhược' }), 'tinh_toan', cites, [], ex);
    }
    if (!near && Math.abs(S.gap) >= 1) {
      const stemsTxt = S.gap_stems < 1 ? Dd.gap_lt1 : fill(Dd.gap_n, { n: num(Math.round(S.gap_stems * 2) / 2) });
      say(xs, fill(m.pick('bd|gap', strong ? Dd.gap_strong : Dd.gap_weak), { gap: num(Math.abs(S.gap)), stems: stemsTxt }), 'tinh_toan', cites, [], ex);
    }
    if (S.heaven_own + S.earth_own > 0) say(xs, fill(m.pick('bd|where', Dd.where), { where: Dd.where_vi[S.earth_own >= S.heaven_own ? 'earth' : 'heaven'], h: num(S.heaven_own), e: num(S.earth_own) }),
      'tinh_toan', cites, [], ex);
    para('nhat-chu', xs, 'support', deep('sức vượng nhược'));
  }
  // ---- nhật chủ, Đọc sâu 2: stems, roots, combinations, growth stages ----
  {
    const xs: ProseSentence[] = [];
    const T = P?.stems;
    if (T && Dd) {
      const ex = { note: NOTE.stems, mech: true, step: 'stems' }, cites = ['TVH pp.332-336'];
      const where = (r: { pillar: string; branch: string; stem?: string }) => `chi ${PIL_VI[r.pillar]} ${r.branch}`;
      if (T.dm_roots.length) {
        const byBranch = new Map<string, string[]>();
        for (const r of T.dm_roots) if (r.stem) (byBranch.get(where(r)) ?? byBranch.set(where(r), []).get(where(r))!).push(r.stem);
        const list = [...byBranch].map(([w, ss]) => `${join([...new Set(ss)])} trong ${w}`);
        if (list.length) say(xs, fill(m.pick('bd|roots', Dd.roots), { dm, list: join(list) }) + (T.dm_root_main === false ? Dd.roots_no_main : ''), 'tinh_toan', cites, [], ex);
      } else say(xs, fill(m.pick('bd|rootsn', Dd.roots_none), { dm }), 'tinh_toan', cites, [], ex);
      const dmS = T.stems.find(s => s.pillar === 'day')!;
      const hopSaid = new Set<string>();
      for (const s of T.stems) {
        if (!s.hop || hopSaid.has([s.pillar, s.hop.with].sort().join())) continue;
        hopSaid.add([s.pillar, s.hop.with].sort().join());
        const h = s.hop, isDm = s.pillar === 'day' || h.with === 'day';
        const o = isDm ? (s.pillar === 'day' ? { p: h.with, s: h.with_stem } : { p: s.pillar, s: s.stem }) : null;
        if (h.outcome === 'khong_hoa') {
          if (isDm) {
            const victimDm = s.pillar === 'day' ? h.victim : !h.victim;
            say(xs, fill(m.pick('bd|hopk', Dd.hop_dm_khong), { dm, p: PIL_VI[o!.p], s: o!.s, el: h.el, mb,
              victim: victimDm ? fill(Dd.hop_victim_dm, { dm, deg: num(dmS.deg) }) : fill(Dd.hop_victim_other, { s: o!.s }) }), 'tinh_toan', cites, [], { ...ex, step: 'stems:hop' });
            mh(xs, 'hop_khong_hoa', {}, 'stems:hop');
          } else say(xs, fill(m.pick('bd|hopko', Dd.hop_other_khong), { p1: PIL_VI[s.pillar], s1: s.stem, p2: PIL_VI[h.with], s2: h.with_stem, el: h.el, mb }), 'tinh_toan', cites, [], ex);
        } else if (h.outcome === 'hoa') {
          const why = fill(Dd.hop_why[h.why ?? 'lenh'] ?? Dd.hop_why.lenh, { el: h.el, mb });
          if (isDm) {
            say(xs, fill(m.pick('bd|hoph', Dd.hop_dm_hoa), { dm, p: PIL_VI[o!.p], s: o!.s, el: h.el, why }), 'tinh_toan', cites, [], { ...ex, step: 'stems:hop' });
            mh(xs, 'hop_hoa', { el: h.el }, 'stems:hop');
          } else say(xs, fill(m.pick('bd|hopho', Dd.hop_other_hoa), { p1: PIL_VI[s.pillar], s1: s.stem, p2: PIL_VI[h.with], s2: h.with_stem, el: h.el, why }), 'tinh_toan', cites, [], ex);
        } else if (h.outcome === 'tranh_hop') {
          const mid = T.stems.filter(x => x.hop?.outcome === 'tranh_hop').find(x => T.stems.filter(y => y.hop?.with === x.pillar).length > 1) ?? s;
          say(xs, fill(m.pick('bd|tranh', Dd.tranh), { s: `${mid.pillar === 'day' ? 'nhật chủ' : `can ${PIL_VI[mid.pillar]}`} ${mid.stem}` }), 'tinh_toan', cites, [], ex);
          for (const y of T.stems) if (y.hop?.outcome === 'tranh_hop') hopSaid.add([y.pillar, y.hop.with].sort().join());
        }
      }
      // the stems that matter here: the useful god's, the largest group's; hư phù and khắc
      const matters = (g: string) => !!Y && (g === Y.group || g === Y.dominant) || g === (CT?.dominant ?? '');
      const gOf = (s: { ten_god: string }) => GROUP_OF[s.ten_god] ?? s.ten_god;
      const huPhu = T.stems.filter(s => s.pillar !== 'day' && !s.rooted).slice(0, 2);
      for (const s of huPhu) say(xs, fill(m.pick('bd|hp', Dd.hu_phu), { p: PIL_VI[s.pillar], s: s.stem, god: s.ten_god, deg: num(s.deg) }), 'tinh_toan', cites, [], ex);
      const kh = T.stems.filter(s => s.khac && (s.pillar === 'day' || matters(gOf(s)))).slice(0, 2);
      for (const s of kh) say(xs, fill(m.pick('bd|kh', Dd.khac), { p: s.pillar === 'day' ? 'ngày' : PIL_VI[s.pillar], s: s.stem, god: s.pillar === 'day' ? 'nhật chủ' : s.ten_god,
        p2: PIL_VI[s.khac!.by[0]], s2: s.khac!.by_stem[0], how: s.khac!.kep ? Dd.khac_how.kep : Dd.khac_how[String(Math.abs(K.indexOf(s.pillar as typeof K[number]) - K.indexOf(s.khac!.by[0] as typeof K[number])))] ?? '',
        loss: num(s.khac!.loss) }).replace(/  +/g, ' '), 'tinh_toan', cites, [], ex);
      for (const u of (P?.units ?? []).slice(0, 2)) say(xs, fill(m.pick(`bd|u${u.hoa}`, u.hoa ? Dd.unit_hoa : Dd.unit_khong), { list: join(u.pillars.map((p, i) => `${PIL_VI[p]} ${u.branches[i]}`)), kind: u.kind_vi, el: u.el }),
        'tinh_toan', ['TVH pp.338-346'], [], { note: NOTE.units, mech: true, step: 'stems' });
    }
    const ps = D.pillars;
    if (ps && F.stages) {
      say(xs, fill(m.pick('bd|stages', F.stages), { dm, list: join(K.map(x => `chi ${PIL_VI[x]} ${pil[x].branch} ở ${ps[x].stage}`)) }), 'tinh_toan', ['ZZ pp.24-25']);
      // the turn: a weak day master that still stands at its peak somewhere, or a strong one that meets its grave or end
      const peak = K.filter(x => ['Trường Sinh', 'Lâm Quan', 'Đế Vượng'].includes(ps[x].stage)), low2 = K.filter(x => ['Tử', 'Mộ', 'Tuyệt'].includes(ps[x].stage));
      const turnAt = strong === false ? peak : strong === true ? low2 : [];
      if (turnAt.length && F.stage_turn) say(xs, fill(m.pick('bd|stturn', F.stage_turn), { at: join(turnAt.map(x => `chi ${PIL_VI[x]} ${pil[x].branch}`)), stage: join([...new Set(turnAt.map(x => ps[x].stage))]),
        dir: strong ? 'chỗ khí nhật chủ lắng xuống' : 'chỗ nhật chủ còn khí mạnh' }), 'tinh_toan', ['ZZ pp.24-25'], [], { tone: strong ? 'neg' : 'pos' });
    }
    // older facts (no depth): the stages are the strength paragraph's second half, as before
    if (P) para('nhat-chu', xs, 'support', deep('can chi và chỗ dựa'));
    else if (xs.length) { const last = out['nhat-chu']?.at(-1); if (last && last.role !== 'structure') { last.sentences.push(...xs); last.text = last.sentences.map(s => s.text).join(' '); } else para('nhat-chu', xs); }
  }

  // ---- ngũ hành: the scored totals (short), then the groups, heaven / earth and the sinh links (Đọc sâu) ----
  const tot = D.strength.tvh_totals;
  if (tot && Object.keys(tot).length && F.totals) {
    const xs = Object.entries(tot).sort((x, y) => y[1] - x[1]);
    const nh: ProseSentence[] = [];
    say(nh, fill(m.pick('bd|totals', F.totals), { top: join(xs.slice(0, 2).map(([e, v]) => `${e} (${num(v)})`)), low: `${xs.at(-1)![0]} (${num(xs.at(-1)![1])})`,
      dom: P?.flow?.groups?.[0]?.group ?? CT?.dominant ?? '' }).replace(/; (so với nhật chủ, )?nhóm  chiếm[^.]*/, '').replace(/; so với nhật chủ thì nhóm  nhiều nhất/, ''), 'tinh_toan', ['TVH pp.331-355'], [], { note: NOTE.score });
    para('ngu-hanh', nh);
  }
  if (P?.flow && S && Dd) {
    const xs: ProseSentence[] = [], ex = { note: NOTE.groups, mech: true, step: 'flow' }, cites = ['ZZ p.17', 'TVH pp.331-355'];
    // the terms explained where they matter: the largest group and the useful god's group carry what they are; the note holds all five
    const def = (g: string) => (g === P.flow.groups[0]?.group || g === Y1) && Dd.group_def?.[g] ? `, ${Dd.group_def[g]}` : '';
    say(xs, fill(m.pick('bd|groups', Dd.groups), { dm: P.stems?.hua_day ? `${dm} (đã hóa ${P.stems.hua_day})` : dm, list: join(P.flow.groups.map(g => `${g.group} (${g.el}${def(g.group)}) ${num(g.deg)} độ`)) }), 'tinh_toan', cites, [], { ...ex,
      note: `${NOTE.groups} Tỉ Kiếp: cùng hành với nhật chủ; Ấn: hành sinh ra nhật chủ; Thực Thương: hành nhật chủ sinh ra; Tài: hành nhật chủ khắc; Quan Sát: hành khắc nhật chủ.` });
    const hv = [...S.elements].sort((a, c) => c.heaven - a.heaven)[0], ev = [...S.elements].sort((a, c) => c.earth - a.earth)[0];
    if (hv.heaven > 0 && hv.el !== ev.el) say(xs, fill(m.pick('bd|hv', Dd.hv), { h: hv.el, hv: num(hv.heaven), e: ev.el, ev: num(ev.earth) }), 'tinh_toan', ['TVH pp.331-355'], [], ex);
    const th = P.flow.there, stemsOf = (g: string) => {
      const by = new Map<string, string[]>();
      for (const x of (th[g] ?? []).filter(x => x.part === 'stem')) (by.get(x.stem) ?? by.set(x.stem, []).get(x.stem)!).push(`can ${PIL_VI[x.pillar]}`);
      return join([...by].map(([s, ws]) => `${s} ở ${join(ws)}`));
    };
    const hidOf = (g: string) => join([...new Set((th[g] ?? []).filter(x => x.part === 'branch').map(x => `chi ${PIL_VI[x.pillar]} ${pil[x.pillar as typeof K[number]].branch}`))]);
    const vis = P.flow.links.filter(l => l.visible && l.to !== 'thân');
    if (vis.length) say(xs, fill(m.pick('bd|chain', Dd.chain), { chain: join(vis.map(l => `${l.from} (${stemsOf(l.from)}) sinh ${l.to} (${stemsOf(l.to)})`)) }), 'tinh_toan', cites, [], ex);
    // the link into the day master: Ấn sinh thân for a weak one (and Quan Sát khắc thân), Thực Thương xì hơi for a strong one
    if (strong === false) {
      const an = stemsOf('Ấn'), anH = hidOf('Ấn');
      say(xs, an ? fill(m.pick('bd|anv', Dd.an_vis), { where: an }) : anH ? fill(m.pick('bd|anh', Dd.an_hid), { where: anH }) : m.pick('bd|ann', Dd.an_none), 'tinh_toan', cites, [], ex);
      const qs = stemsOf('Quan Sát');
      if (qs) say(xs, fill(m.pick('bd|qs', Dd.qs_hit), { where: qs }), 'tinh_toan', cites, [], ex);
    } else if (strong === true) {
      const tt = stemsOf('Thực Thương'), ttH = hidOf('Thực Thương');
      if (tt || ttH) say(xs, tt ? fill(m.pick('bd|ttv', Dd.out_vis), { where: tt }) : fill(m.pick('bd|tth', Dd.out_hid), { where: ttH }), 'tinh_toan', cites, [], ex);
    }
    para('ngu-hanh', xs, 'support', deep('quan hệ giữa các hành'));
  }

  // ---- cách cục và dụng thần, in the chapter frame (plan step 4): 1 cấu trúc (the cách, the useful god and why), 2 hỗ trợ / hạn chế (the
  // thành bại sentences, where the useful god stands, what in the chart sinh or khắc it), 3 tương tác (điều hậu and its note, the Trích Thiên
  // Tủy rules), 4 mâu thuẫn (where the cách and điều hậu tables differ), 5 kết luận có điều kiện; 6, the sources, stay in each sentence's
  // trace (the "Căn cứ" fold). Parts 2-4 are the Đọc sâu of the chapter. ----
  const c1: ProseSentence[] = [], c2: ProseSentence[] = [], c3: ProseSentence[] = [], c4: ProseSentence[] = [], c5: ProseSentence[] = [];
  // a special cách of Thiệu Vĩ Hoa (pp.369-376) replaces the ordinary one: his thành bại sentences for the ordinary cách are then not told
  const tb = CT?.special ? [] : D.verified.filter(v => v.rule_id.startsWith('BT_TVH_TB_') && tbParts(v.text));
  const tbOrder = [...tb.filter(v => v.verdict !== 'xau'), ...tb.filter(v => v.verdict === 'xau')];
  const cachName = CT?.cach ?? D.geju.inner[0]?.name;
  let turned = false;
  tbOrder.forEach((v, i) => {
    const { cond, verdict } = tbParts(v.text)!;
    const xau = v.verdict === 'xau', turn = xau && !turned && i > 0;
    if (turn) turned = true;
    const frames = i === 0 ? F.cach_first : turn ? F.tb_turn : F.tb_next;
    const xs = i === 0 ? c1 : c2, step = `tb:${i}`;
    say(xs, fill(m.pick(`bd|tb${i}`, frames), { mb, cach: cachName ?? '', cond: lowerFirst(cond), verdict: lowerFirst(verdict) }), 'sach', ['TVH pp.367-369'],
      [cite(v.rule_id, v.text, ['TVH pp.367-369'])], { tone: xau ? 'neg' : 'pos', step, note: NOTE.tb });
    if (!xau && /hộ thân|sinh thân|giúp thân/.test(cond)) mh(xs, 'ho_than', {}, step);
  });
  const dmVi = levelVi;
  if (tableOk && CT!.yong.length) {
    const why = Y?.kind === 'cach' && Y.why && !Y.fallback && Dd ? fill(Dd.yong_why, { why: Y.why.text }) : '';
    const vars = { cach: CT!.cach!, dm: dmVi, dom: CT!.dominant ?? '', yong: join(CT!.yong.slice(0, 1)), tot: join(CT!.van_tot), xau: join(CT!.van_xau), why };
    // the cách's one status (owner review 2026-10-22): partial, so the dụng thần and every luck verdict drawn from it are conditional
    if (cachPartial && Dd?.cach_status?.length) say(c1, fill(m.pick('bd|cst', Dd.cach_status), { cach: CT!.cach! }), 'tinh_toan', ['TVH pp.356-366'], [],
      { step: 'cach:status', conditional: 'cach_partial', note: 'Trạng thái của cách: xác lập một phần (yongshen.METHOD_META cach_cuc_tvh). Bảng dụng thần và vận hỷ kỵ (Thiệu Vĩ Hoa tr.378-386) chép khớp trang in; phép định cách từ chi tháng mới được đối chiếu một phần với tr.356-366. Mọi lời xếp vận tốt xấu suy từ bảng ấy vì vậy có điều kiện là cách được xác lập.' } as Partial<SentenceTrace>);
    say(c1, fill(m.pick('bd|table', CT!.van_tot.length || CT!.van_xau.length ? F.table : F.table_no_van), vars), 'tinh_toan', [tvhPage, ...(Y?.why ? [`TVH pp.${Y.why.page.replace(/\s/g, '')}`] : [])], [],
      { step: 'yong', note: NOTE.yong, mech: !!why });
    mh(c1, 'benh_thuoc', { benh: `nhật chủ ${dmVi} mà nhóm ${CT!.dominant ?? ''} nhiều nhất`, yong: Y1 }, 'yong');
    const top = P?.flow?.groups?.[0]?.group;
    if (top && CT!.dominant && top !== CT!.dominant && Dd?.dom_skip?.length) say(c1, fill(m.pick('bd|dsk', Dd.dom_skip), { top, dom: CT!.dominant, cach: CT!.cach! }), 'tinh_toan', [tvhPage], [], { note: 'Bảng dụng thần theo cách (Thiệu Vĩ Hoa tr.378-386) chỉ có dòng cho một số nhóm nhiều nhất; khi nhóm lớn nhất không có dòng, bộ máy lấy nhóm lớn kế tiếp có dòng (yongshen.cach_cuc_tvh). Sách không nói cách xử lý trường hợp này.', step: 'yong:dom' });
    if (Y?.fallback && Dd) say(c1, fill(m.pick('bd|fb', Dd.fallback), { first: Y.first, use: Y.group }).replace(/\.\s*$/, Y.why ? fill(Dd.yong_why, { why: Y.why.text }) + '.' : '.'), 'tinh_toan', [tvhPage], [], { note: NOTE.yong, step: 'yong:fallback', mech: !!Y.why });
    // where the useful god stands in the four pillars (the day stem is the day master itself)
    const yg = new Set([Y1]), many = false;
    const vis = (['year', 'month', 'hour'] as const).filter(x => yg.has(GROUP_OF[pil[x].stem_ten_god ?? ''])).map(x => `can ${PIL_VI[x]} ${pil[x].stem}${many ? ` (${pil[x].stem_ten_god})` : ''}`);
    const hid = K.flatMap(x => pil[x].hidden.filter(h => yg.has(GROUP_OF[h.ten_god])).map(h => `chi ${PIL_VI[x]} ${pil[x].branch} (${h.stem})`));
    if (F.yong_where) say(c2, fill(F.yong_where[vis.length ? 'vis' : hid.length ? 'hid' : 'none'], { yong: Y1, vis: join(vis), hid: join(hid), hid2: hid.length && vis.length ? fill(F.yong_where.and_hid, { hid: join(hid) }) : '' }),
      'tinh_toan', ['ZZ p.17'], [], { tone: vis.length ? 'pos' : 'neg' });
  } else if (CT?.special && F.table_special && (CT.special_tot.length || CT.special_xau.length)) {
    say(c1, fill(m.pick('bd|tsp', F.table_special), { name: CT.special.replace(/\s*\(TVH\)$/, ''), tot: join(CT.special_tot), xau: join(CT.special_xau) || 'không có hành nào' }), 'tinh_toan', ['TVH pp.385-386'], [], { note: NOTE.yong });
    if (Y?.kind === 'special' && Dd?.special_yong?.length) say(c1, fill(m.pick('bd|spy', Dd.special_yong), { el: Y.el, grp: /Hóa/.test(CT.special) ? '' : `, tức nhóm ${Y.group}` }), 'tinh_toan', ['TVH p.381'], [], { note: NOTE.yong, step: 'yong' });
  }
  // the useful god inside the chart (TVH p.382): what khắc it, what sinh it, what binds or clashes it; hỉ and kị thần by relation
  if (Y && Dd) {
    const ex = { note: NOTE.hyky, mech: true, step: 'yong:natal' }, cites = ['TVH p.382'];
    const nat = Y.natal, by = (k2: string) => nat.filter(x => x.kind === k2);
    const name = (x: { pillar: string; who: string }) => `can ${PIL_VI[x.pillar]} ${x.who}`;
    const khac = by('khac_yong'), sinh = by('sinh_yong');
    const parts: string[] = [];
    if (khac.length) parts.push(fill(Dd.natal_khac, { list: join(khac.map(name)), el: Y.el }) + (sinh.length ? '' : `, còn ${Dd.natal_no_sinh}`));
    if (sinh.length) parts.push(fill(khac.length ? Dd.natal_sinh : Dd.natal_sinh_first ?? Dd.natal_sinh, { list: join(sinh.map(name)), el: Y.el }));
    for (const x of by('hop_yong')) parts.push(fill(Dd.natal_hop, { p: PIL_VI[x.pillar], s: x.who, p2: PIL_VI[x.with!], s2: x.with_stem! }));
    for (const x of by('xung_yong')) parts.push(fill(Dd.natal_xung, { p: PIL_VI[x.pillar], b: x.who, p2: PIL_VI[x.with!], b2: x.with_branch! }));
    if (parts.length) say(c2, fill(m.pick('bd|nat', Dd.natal_open), { list: parts.length > 1 ? `${parts.slice(0, -1).join('; ')}; ${parts.at(-1)}` : parts[0] }), 'tinh_toan', cites, [], { ...ex, tone: khac.length ? 'neg' : 'pos' });
    else say(c2, fill(m.pick('bd|natn', Dd.natal_none), { el: Y.el }), 'tinh_toan', cites, [], ex);
    say(c2, fill(m.pick('bd|hyky', Dd.hyky), hoaC ? { hy: `hành ${Y.hy.el}`, hyEl: '', ky: `hành ${Y.ky.el}`, kyEl: '' } : { hy: Y.hy.group, hyEl: `hành ${Y.hy.el}`, ky: Y.ky.group, kyEl: `hành ${Y.ky.el}` }).replace(/ \(\)/g, ''), 'tinh_toan', cites, [], { ...ex, step: 'yong:hyky' });
    const tv = Y.table_vs_relation;
    if (tv && !tv.hy_in_tot && !tv.hy_in_xau && Y.hy.group !== Y.group) say(c2, fill(m.pick('bd|hyu', Dd.hy_unlisted), { hy: Y.hy.group }), 'tinh_toan', cites, [], ex);
    const alts = Y.alternatives.map(a => a.group);
    if (tv?.ky_in_tot && Dd.ky_in_tot) say(c2, fill(m.pick('bd|kyt', alts.includes(Y.ky.group) ? Dd.ky_in_tot : Dd.ky_in_tot_plain ?? Dd.ky_in_tot), { ky: Y.ky.group, alts: join(alts), yong: Y.group }), 'tinh_toan', ['TVH p.382', tvhPage], [], { ...ex, step: 'yong:conflict', note: `${NOTE.hyky} Danh sách vận của cách: ${tvhPage.replace('TVH pp.', 'tr.')}.` });
    if (tv?.hy_in_xau && Dd.hy_in_xau) say(c2, fill(m.pick('bd|hyx', Dd.hy_in_xau), { hy: Y.hy.group }), 'tinh_toan', ['TVH p.382', tvhPage], [], { ...ex, step: 'yong:conflict' });
  }
  // the two tables of the same book name different useful gods: said in part 4, with where they differ and how far each goes
  const mainGroups = dh.stems.filter(s => s.rank.startsWith('chính')).map(s => s.ten_god);
  const differs = !!(dh.verified && dh.stems.length && tableOk && CT!.yong.length && mainGroups.length && !mainGroups.some(g => CT!.yong.some(y => GROUP_OF[g] === y)));
  if (dh.verified && dh.stems.length) {
    const main = dh.stems.filter(s => s.rank.startsWith('chính')).map(s => `${s.stem} (${s.ten_god})`), others = dh.stems.filter(s => !s.rank.startsWith('chính')).map(s => `${s.stem} (${s.ten_god})`);
    const mainTxt = join(main.length ? main : others.slice(0, 1));
    if (differs && F.dh_turn) say(c4, fill(m.pick('bd|dhturn', F.dh_turn), { mb, dm, climate: D.climate.label ?? '', main: mainTxt, yong: Y1 }), 'tinh_toan', ['TVH pp.389-396'], [], { note: NOTE.dh });
    else say(c3, fill(m.pick('bd|cl', F.climate), { mb, dm, climate: D.climate.label ?? '', main: mainTxt, others: join(main.length ? others : others.slice(1)) || 'không có can nào khác' }),
      'tinh_toan', ['TVH pp.389-396'], [], { note: NOTE.dh });
    const present = dh.stems.filter(s => s.visible || s.hidden).map(s => s.stem), absent = dh.stems.filter(s => !s.visible && !s.hidden).map(s => s.stem);
    if (present.length && absent.length) say(c3, fill(m.pick('bd|pr', F.climate_presence), { present: join(present), absent: join(absent) }), 'tinh_toan', ['TVH pp.389-396'], [], { note: NOTE.dh });
    // the printed note of the cell (TVH pp.391-397), and whether a cục it names is formed in the chart
    const N = P?.dh_note;
    if (N && Dd) {
      const id = cite(N.id, `Thiệu Vĩ Hoa, chú thích bảng dụng thần điều hậu (tr.${N.page}), ô ${N.cell}: ${N.text ?? N.say}`, [`TVH pp.${N.page}`]);
      // the printed note may hold two sentences: one sentence here, the second joined with a semicolon
      const one0 = N.say.replace(/\.\s+(\S+)/g, (_, w: string) => `; ${STEMS_VI.includes(w) || EL_ORDER.includes(w) ? w : lowerFirst(w)}`);
      const one = [...STEMS_VI, ...EL_ORDER, ...BRANCHES_VI, 'Tỉ Kiếp', 'Thương Quan'].some(s => one0.startsWith(s + ' ') || one0.startsWith(s + ',')) ? one0 : lowerFirst(one0);
      say(c3, fill(m.pick('bd|dhn', Dd.dh_note), { dm, mb, say: one }), 'sach', [`TVH pp.${N.page}`], [id], { note: NOTE.dh, step: 'dh:note' });
      for (const c of N.cuc) say(c3, fill(Dd.dh_cuc[c.formed ? 'yes' : 'no'], { el: c.el }), 'tinh_toan', ['TVH pp.338-346'], [], { note: NOTE.units });
    }
  }
  // the Trích Thiên Tủy rules that fired, in the order hàn noãn, nguyên lưu, Quan Sát hỗn tạp, Thương Quan, tòng / hóa; a rule whose premise
  // names the day master's strength is said only when the TVH verdict agrees with it
  const TTT_ORDER = ['BT_TTT_HANNOAN', 'BT_TTT_NGUYENLUU', 'BT_TTT_HONTAP', 'BT_TTT_TQ', 'BT_TTT_TONG', 'BT_TTT_HOA', 'BT_TVH_CV', 'BT_TVH_TONG', 'BT_TVH_HOA'];
  let mhTong = false;
  for (const pre of TTT_ORDER) for (const [id, v] of fired) {
    if (!id.startsWith(pre) || !F.verified_text[id]) continue;
    const need = F.premise[id];
    if (need && (strong == null || (need === 'strong') !== strong)) continue;
    const src = id.startsWith('BT_TVH') ? 'TVH pp.369-376' : 'TTT', step = `rule:${id}`;
    say(c3, F.verified_text[id], 'sach', [src], [cite(id, v.text, [src])], { ...(/_KY$|CO_BENH/.test(id) ? { tone: 'neg' } : {}), step,
      note: id.startsWith('BT_TVH') ? 'Cách đặc biệt: Thiệu Vĩ Hoa tr.369-376.' : 'Trích Thiên Tủy (Nhậm Thiết Tiều bình giảng).' });
    if (id === 'BT_TTT_HANNOAN_CAN_NOAN') mh(c3, 'cold', {}, step);
    if (id === 'BT_TTT_HANNOAN_CAN_HAN') mh(c3, 'hot', {}, step);
    if (!mhTong && /TONG_(TAI|SAT|NHI|THE)$/.test(id)) { mh(c3, 'tong', {}, step); mhTong = true; }
  }
  // two special cách of the same book fit at once: which one the reading follows (the first the engine checks: tvh_cach.special), said as such
  const tongs = [...fired.keys()].filter(id => /^BT_TVH_(TONG|CV|HOA)_/.test(id));
  if (tongs.length > 1 && CT?.special && Dd?.special_pick?.length)
    say(c3, fill(m.pick('bd|spk', Dd.special_pick), { list: join(tongs.map(id => F.verified_text[id]?.match(/cách ([^:(,]+?)(?::| \(|,|$)/)?.[1]?.trim() ?? id).filter(Boolean)), name: CT.special.replace(/\s*\(TVH\)$/, '') }), 'he_thong', [], [],
      { note: 'Khi lá số khớp nhiều cách đặc biệt, bộ máy lấy cách đầu tiên theo thứ tự xét của engine/tvbt/bazi_deep/tvh_cach.py (chuyên vượng, tòng tài, tòng sát, tòng nhi, hóa khí); sách không nói nên chọn cách nào.' });
  // part 4: where the two tables part ways and how far each goes (yongshen.METHOD_META), so where they differ the verdict is conditional
  const luckRcs = D.luck.map(l => rcOf(l));
  const clash = differs || luckRcs.some(r => r.agree === 'khac');
  if (clash && tableOk && table.length && F.reliability?.length) {
    const note = 'Mức tin cậy (yongshen.METHOD_META): bảng dụng thần theo cách tr.378-386 chép khớp trang in, quy tắc 40% khớp tr.355; bảng điều hậu tr.389-396 chép khớp trang in, việc gán can chính là Dụng là quy ước của hệ thống, và Thiệu Vĩ Hoa ghi bảng do độc giả gửi, chưa rõ xuất xứ (tr.388). Chưa phép nào được kiểm nghiệm thực tế.';
    F.reliability.forEach((f, i) => say(c4, fill(f, { dm: levelVi, dom: CT!.dominant ?? '', climate: D.climate.label ?? '', mb }), 'tinh_toan', [tvhPage, 'TVH pp.388-396'], [], { step: `reconcile:cach:${i}`, note: i ? note : F.rc_note }));
  }
  // part 5: what to do, conditional where the tables differ
  if ((c1.length || c3.length) && F.advice && (tableOk || table.length)) {
    const dhOk = table.filter(x => { const g = dh.stems.find(s => s.stem === x)?.ten_god; return !g || !xauG.includes(GROUP_OF[g]); });
    const lean = tableOk && CT!.yong.length ? `nhóm ${Y1}` : '', dhTxt = dhOk.length ? `can ${join(dhOk)}` : '', heat = needEl ? `hành ${needEl}` : '';
    if (clash && lean && F.conclusion_split?.length) say(c5, fill(m.pick('bd|cs', F.conclusion_split), { lean, extra: join([dhTxt, heat].filter(Boolean)) || lean, yong: Y1 })
      .replace(/, thêm  về khí hậu/, ''), 'he_thong', [tvhPage, 'TVH pp.389-396'], [], { tone: 'answer', step: 'conclusion:cach' });
    else say(c5, fill(m.pick('bd|adv', F.advice), { lean: join([lean, dhTxt, heat].filter(Boolean)), tot: totG.length ? join(totG) : '', xau: xauG.length ? join(xauG) : '' })
      .replace(/; những chặng gặp  thuận hơn những chặng gặp /, '').replace(/ thuận hơn những chặng gặp \./, '.').replace(/, tiến ở những chặng gặp  và giữ sức ở những chặng gặp /, ''), 'he_thong', [], [], { tone: 'answer', step: 'conclusion:cach' });
  }
  const part = (xs: ProseSentence[], key: FramePart, d?: boolean) => { if (xs.length) (out['cach-cuc'] ??= []).push({ role: 'support', sentences: xs, text: xs.map(s => s.text).join(' '), part: key, ...(d ? deep() : {}) } as ProseParagraph); };
  part(c1, 'cau_truc'); part(c2, 'ho_tro', !!P); part(c3, 'tuong_tac', !!P); part(c4, 'mau_thuan', !!P); part(c5, 'ket_luan');

  // ---- thần sát (八字真宗 pp.21-22): the stars whose printed gloss the data keeps, then the rest by position ----
  const ss = D.shensha ?? [];
  if (ss.length && F.shensha) {
    const xs: ProseSentence[] = [];
    const where = (x: { pillar: string; at: string }) => `trụ ${PIL_VI[x.pillar]} (${x.at})`;
    const byStar = (ys: typeof ss) => [...new Map(ys.map(x => [x.vi, ys.filter(y => y.vi === x.vi)])).values()];
    const good = byStar(ss.filter(x => x.gloss && x.kind !== 'hung'));
    if (good.length) say(xs, fill(m.pick('bd|ss', F.shensha), { list: good.map(g => `${g[0].vi} ở ${join(g.map(where))}, được ghi là ${g[0].gloss!.replace(/^sách ghi:\s*/, '')}`).join('; ') }), 'tinh_toan', ['ZZ pp.21-22'], [], { tone: 'pos' });
    const list = (gs: typeof good) => { const it = gs.map(g => `${g[0].vi} ở ${join(g.map(where))}`); return it.some(x => x.includes(' và ')) ? it.join('; ') : join(it); };
    const hung = byStar(ss.filter(x => x.kind === 'hung'));
    if (hung.length && F.shensha_hung) say(xs, fill(m.pick('bd|ssh', F.shensha_hung), { list: list(hung), them: hung.length > 1 || hung[0].length > 1 ? 'những sao' : 'sao' }), 'tinh_toan', ['ZZ pp.21-22']);
    const plain = byStar(ss.filter(x => !x.gloss && x.kind !== 'hung'));
    if (plain.length && F.shensha_plain) say(xs, fill(m.pick('bd|ssp', F.shensha_plain), { list: list(plain) }), 'tinh_toan', ['ZZ pp.21-22']);
    if (xs.length) (out['cach-cuc'] ??= []).push({ role: 'support', sentences: xs, text: xs.map(s => s.text).join(' '), topic: 'than_sat' });
  }

  // ---- sự nghiệp: Tài in three layers (owner review 2026-10-22). 八字真宗 p.50 reads "Tài thấu can và có gốc: tài vận tốt" from the Tài's
  // position alone; Thiệu Vĩ Hoa reads the same chart through the day master's strength and the cách. Where the day master is weak and the
  // cách table calls Tài a bad luck, the three layers are told apart, and the condition that decides is named; no page weighs the two.
  const TL = Dd?.tai_layers, zzW = Object.keys(rules).find(id => /^BT_ZZ_DIRECT_W_(CHINH|THIEN)_TAI_ROOT$/.test(id));
  if (TL && zzW && strong === false && tableOk && (xauG.includes('Tài') || CT!.dominant === 'Tài')) {
    const xs: ProseSentence[] = [], zz = rules[zzW].reading.replace(/\s*\(.*$/, '').trim();
    const visT = (['year', 'month', 'hour'] as const).filter(x => GROUP_OF[pil[x].stem_ten_god ?? ''] === 'Tài').map(x => `can ${PIL_VI[x]} ${pil[x].stem}`);
    const hidT = [...new Set(K.flatMap(x => pil[x].hidden.filter(h => GROUP_OF[h.ten_god] === 'Tài').map(() => `chi ${PIL_VI[x]} ${pil[x].branch}`)))];
    const where = `Tài lộ ở ${join(visT)}${hidT.length ? ` và có gốc trong ${join(hidT)}` : ''}`;
    say(xs, fill(m.pick('bd|tl1', TL.pos), { where, zz }), 'sach', ['ZZ p.50'], [zzW], { step: 'tai:pos', note: 'Bát Tự Chân Tông tr.50: lời về tài vận xét vị trí của Tài (thấu can, có gốc), không xét sức nhật chủ.' });
    say(xs, fill(m.pick('bd|tl2', TL.dm), { dm, level: levelVi }), 'tinh_toan', ['TVH pp.331-355'], [], { step: 'tai:dm', note: NOTE.score, mech: true });
    const tbT = tbOrder.find(v => /^BT_TVH_TB_TAI_/.test(v.rule_id));
    const tbTxt = tbT ? (() => { const p2 = tbParts(tbT.text)!; return `trường hợp ${lowerFirst(p2.cond)} được xếp là ${lowerFirst(p2.verdict)}`; })() : '';
    say(xs, fill(m.pick('bd|tl3', tbTxt ? TL.method : TL.method_no_tb), { cach: CT!.cach!, tb: tbTxt }), 'tinh_toan', ['TVH pp.367-369', tvhPage], [],
      { step: 'tai:method', conditional: cachPartial ? 'cach_partial' : undefined, note: `${NOTE.tb} ${NOTE.yong}` } as Partial<SentenceTrace>);
    say(xs, fill(m.pick('bd|tl4', TL.decide), { zz }), 'he_thong', [], [], { step: 'tai:decide', tone: 'answer',
      note: 'Phân xử của hệ thống: lời có điều kiện cụ thể hơn (nêu cả sức nhật chủ, Thiệu Vĩ Hoa tr.367-369) được lấy làm điều quyết định; lời chung về vị trí của Tài (Bát Tự Chân Tông tr.50) giữ nguyên nhưng chỉ trọn khi điều kiện ấy có. Không trang sách nào trong bộ đang dùng cân hai lời này với nhau: chỗ vênh còn mở.' });
    para('su-nghiep', xs);
  }

  // ---- đại vận: per luck pillar a short paragraph (what it is, the cách side with its reason, the climate side, the one verdict) and a
  // Đọc sâu paragraph (the halves, what it does to the useful god, the relations with the natal pillars) ----
  const yr = chart.year?.year ?? new Date().getFullYear();
  let spouseSaid = false;
  /** "Với nguyên cục, can Kỷ hợp can tháng Giáp, còn chi Hợi xung chi năm Tỵ, lục hợp và phá chi giờ Dần." */
  const events = (t: BaziTemporal, key: string, subject: { stem: string; branch: string; who: string; year?: number }): { text: string; cites: string[] } | null => {
    if (!t.events) return null;                         // facts from before Track C carry no relations: nothing is claimed either way
    const ev = t.events.filter(e => e.targets.every(x => x in pil));
    if (!ev.length) return F.ev_none.length ? { text: fill(m.pick(`bd|evn|${key}`, F.ev_none), { Who: `${subject.who === 'cả trụ năm' ? 'Năm' : 'Vận'} ${subject.stem} ${subject.branch}` }), cites: ['ZZ pp.19-20'] } : null;
    const name = (p: string, part: string) => `${part === 'stem' ? 'can' : 'chi'} ${PIL_VI[p]} ${part === 'stem' ? pil[p as typeof K[number]].stem : pil[p as typeof K[number]].branch}`;
    // relations grouped by target, then targets with the same relations together: "lục hợp và phá chi giờ Dần", "hại chi tháng Sửu và chi ngày Sửu"
    const group = (part: 'stem' | 'branch') => {
      const by = new Map<string, string[]>();
      for (const e of ev.filter(x => x.part === part && x.targets.length === 1)) {
        const kv = e.kind === 'branch_clash' && e.opens_kho ? F.ev_kind.branch_clash_kho : F.ev_kind[e.kind];
        if (kv) (by.get(e.targets[0]) ?? by.set(e.targets[0], []).get(e.targets[0])!).push(fill(kv, { el: e.element ?? '' }));
      }
      const same = new Map<string, string[]>();
      for (const [p, ks] of by) { const key2 = join([...new Set(ks)]); (same.get(key2) ?? same.set(key2, []).get(key2)!).push(p); }
      return [...same].map(([ks, ps2]) => `${ks} ${join(ps2.map(p => name(p, part)))}`);
    };
    const stems = group('stem'), branches = group('branch');
    for (const e of ev.filter(x => x.part === 'branch' && x.targets.length > 1)) {
      const kv = F.ev_kind[e.kind];
      if (kv) branches.push(fill(kv, { with: join(e.targets.map(p => `chi ${PIL_VI[p]} ${pil[p as typeof K[number]].branch}`)), el: e.element ?? '' }));
    }
    const pillars = ev.filter(x => x.part === 'pillar').map(e => F.ev_kind[e.kind] ? fill(F.ev_kind[e.kind], { with: `trụ ${PIL_VI[e.targets[0]]} ${pil[e.targets[0] as typeof K[number]].name}`, who: subject.who }) : '').filter(Boolean);
    const parts = [stems.length ? `can ${subject.stem} ${stems.join(', ')}` : '', branches.length ? `chi ${subject.branch} ${branches.join(', ')}` : '', ...pillars].filter(Boolean);
    if (!parts.length) return null;
    const hitsDay = ev.some(e => e.part !== 'stem' && e.targets.includes('day')), hitsMonth = ev.some(e => e.part === 'branch' && e.targets.includes('month'));
    let note = '';
    if (hitsDay) { note = spouseSaid ? F.spouse_next : F.spouse_first; spouseSaid = true; }
    else if (hitsMonth) note = F.marriage;
    return { text: fill(m.pick(`bd|ev|${key}`, subject.year && F.ev_open_year?.length ? F.ev_open_year : F.ev_open), { year: String(subject.year ?? ''), list: parts.length > 1 ? `${parts.slice(0, -1).join('; ')}; còn ${parts.at(-1)}` : parts[0] }).replace(/\.$/, '') + note, cites: ['ZZ pp.19-20', ...(note ? ['ZZ p.57'] : [])] };
  };
  /** the cách side (support / limit): the TVH table's verdict on the stem and the branch, then why (TVH pp.377-382) */
  const cachSide = (xs: ProseSentence[], t: BaziTemporal, key: string, who: { stem: string; branch: string }, step: string, year?: number) => {
    const v = t.tvh ?? { stem: null, branch: null };
    if (!tableOk && !CT?.special) return;
    const cach = CT!.special ? CT!.special.replace(/\s*\(TVH\)$/, '') : CT!.cach!;
    const vs = { cach, stem: who.stem, branch: who.branch, sg: t.stem_group ?? '', bg: t.branch_group ?? '', v: F.verdict[v.stem ?? ''] ?? '', v2: F.verdict[v.branch ?? ''] ?? '' };
    let text = '';
    if (v.stem && v.branch && v.stem === v.branch) text = m.pick(`bd|tb|${key}`, vs.sg === vs.bg ? F.tvh_same : F.tvh_both);
    else if (v.stem && v.branch) text = m.pick(`bd|ts|${key}`, F.tvh_split);
    else if (v.stem || v.branch) text = fill(m.pick(`bd|t1|${key}`, F.tvh_one), { Part: v.stem ? 'Can' : 'Chi', who: v.stem ? who.stem : who.branch, g: v.stem ? vs.sg : vs.bg, v: F.verdict[(v.stem ?? v.branch)!] });
    else text = m.pick(`bd|tn|${key}`, F.tvh_none);
    // a year says which year it is, so it never repeats the sentence of a luck pillar with the same stem
    const t0 = fill(text, vs);
    // conditional on the cách standing (owner review 2026-10-22), said in the sentence itself
    const condOn = cachPartial && !CT!.special && Dd?.cach_cond?.length;
    const head = year ? (condOn ? fill(Dd!.cach_cond_year, { year: String(year), cach, x: lowerFirst(t0) }) : `Xét năm ${year}, ${lowerFirst(t0)}`)
      : condOn ? fill(m.pick(`bd|cc|${key}`, Dd!.cach_cond ?? []), { cach, x: lowerFirst(t0) }) : t0, tone = (v.stem ?? v.branch) === 'xau' ? 'neg' as const : (v.stem ?? v.branch) === 'tot' ? 'pos' as const : undefined;
    const src = CT!.special ? 'TVH pp.385-386' : tvhPage;
    // why: the book's reasons for the groups (TVH pp.377-382), at most two per group
    const W = Dd?.why, ws = t.why;
    if (!W || !ws) { say(xs, head, 'tinh_toan', [src], [], { tone, step, note: NOTE.yong }); return; }
    const phrase = (r: BaziWhy) => { const vsW = W[r.key]; return vsW?.length ? fill(m.pick(`bd|why|${r.key}|${key}`, Array.isArray(vsW) ? vsW : [vsW]), { dom: CT?.dominant ?? '' }) : ''; };
    const keys = (rs: BaziWhy[] | null | undefined) => (rs ?? []).map(r => r.key).join(',');
    const ra = v.stem ? ws.stem ?? [] : [], rb = v.branch ? ws.branch ?? [] : [];
    const a = ra.map(phrase).filter(Boolean), c = keys(ra) === keys(rb) ? a : rb.map(phrase).filter(Boolean);
    const G1 = vs.sg, G2 = vs.bg, both = (r: string[]) => r[0] + (r[1] ? fill(Dd!.why_and, { b: r[1] }) : '');
    const pk = (xs2: string[] | string | undefined, k2: string) => m.pick(`bd|${k2}|${key}`, Array.isArray(xs2) ? xs2 : xs2 ? [xs2] : []);
    let why = '';
    if (a.length && c.length && G1 !== G2 && keys(ra) === keys(rb) && Dd!.why_both) why = fill(pk(Dd!.why_both, 'wb'), { G1, G2, a: both(a) });
    else if (a.length && c.length && G1 !== G2) why = fill(pk(Dd!.why_two, 'w2'), { G1, a1: both(a), G2, a2: both(c) });
    else if (a.length || c.length) { const r = a.length ? a : c; why = fill(pk(Dd!.why_one, 'w1'), { G: a.length ? G1 : G2, a: r[0], b: r[1] ? fill(Dd!.why_and, { b: r[1] }) : '' }); }
    // the verdict and its reason in one sentence: it names the stem and the branch, so the same reason never repeats word for word
    const reason = why.replace(/\.$/, '');
    say(xs, why ? `${head.replace(/\.$/, '')}: ${/^Vì /.test(reason) ? lowerFirst(reason) : reason}` : head, 'tinh_toan', [src, ...(why ? ['TVH pp.377-382'] : [])], [],
      { tone, step, note: why ? `${NOTE.yong} ${NOTE.van}` : NOTE.yong, ...(why ? { mech: true } : {}) });
  };
  /** the climate side: the stem (or the branch's main qi) the điều hậu cell names, or the element the hàn noãn rule asks for; turned with a
   *  contrast when the cách side called the pillar bad */
  const climateSide = (xs: ProseSentence[], t: BaziTemporal, rc: Reconcile, key: string, who: { stem: string; branch: string }, kind: string, step: string) => {
    const sr = dhRoleOf(who.stem, table), h = t.hidden?.[0]?.stem, br = sr ? null : dhRoleOf(h, table);
    const k2 = sr ?? (br ? `branch_${br}` : rc.warm ? (needEl === 'Hỏa' ? 'warm' : 'cool') : '');
    if (!k2 || !F.dh_role[k2]) return;
    const text = fill(F.dh_role[k2], { stem: who.stem, branch: who.branch, h: h ?? '', kind, el: needEl, pk: `${kind} ${who.stem} ${who.branch}` });
    const turn = rc.cach === 'xau' ? m.conn('contrast', `bd|turn|${key}`) || 'Tuy nhiên,' : '';
    const warmOnly = rc.warm && !sr && !br;
    say(xs, turn ? `${turn} ${lowerFirst(text)}` : text, warmOnly ? 'sach' : 'tinh_toan', warmOnly ? ['TTT'] : ['TVH pp.389-396'],
      warmOnly && needRule && fired.get(needRule) ? [cite(needRule, fired.get(needRule)!.text, ['TTT'])] : [], { tone: 'pos', step, note: warmOnly ? 'Trích Thiên Tủy, Hàn Thử (tr.113-114).' : NOTE.dh });
  };
  /** where the tables differ (part 4) and the one verdict with what to do (part 5); the same verdict feeds the closing */
  const verdictOf = (xs: ProseSentence[], t: BaziTemporal, rc: Reconcile, key: string, who: { stem: string; branch: string }, o: { year: boolean; years?: BaziTemporal['good_years'] }) => {
    const kind = o.year ? 'năm' : 'vận', step = `reconcile:${key}`, pk = `${kind} ${who.stem} ${who.branch}`;
    const yongTxt = Y1 ? `nhóm ${Y1}` : '';
    if (rc.agree === 'khac' && F.rc_khac.length && tableOk) {
      const g = t.tvh?.stem ? t.stem_group : t.branch_group, whoC = t.tvh?.stem ? `can ${who.stem}` : `chi ${who.branch}`;
      // the climate side names what brought it: the stem (named, or of the hàn noãn element), else the branch by its main qi
      const h = t.hidden?.[0]?.stem, whoH = dhRoleOf(who.stem, table) || rc.warm ? `can ${who.stem}` : `chi ${who.branch} (tàng ${h})`;
      say(xs, fill(m.pick(`bd|rk|${key}`, F.rc_khac), { kind, pk, g: g ?? '', dm: levelVi, dom: CT!.dominant ?? '', who: whoC, whoH }), 'tinh_toan', [tvhPage, 'TVH pp.389-396'], [], { step, note: F.rc_note });
    }
    const sup = (rc.support ?? []).map(x => `${x.stem} (${x.ten_god}), ${x.why.includes('cach') ? `thuộc nhóm dụng thần ${x.group}` : x.stem === table[0] ? 'can điều hậu đứng đầu' : 'một can điều hậu'}`);
    // what in the branch still answers the chart's need, said only where the cách table calls the pillar bad (a split pillar already says which half is good)
    if (sup.length && rc.cach === 'xau' && F.rc_support.length)
      say(xs, fill(m.pick(`bd|rs|${key}`, F.rc_support), { c: rc.verdict === 'nang' ? 'Dẫu vậy, c' : 'C', branch: who.branch, list: sup.join('; '), kind, pk }), 'tinh_toan', ['ZZ pp.7-8', 'ZZ p.17'], [], { step, tone: 'pos' });
    const ys = o.years ?? [];
    const list = ys.length && !o.year ? join(ys.map(y => `${y.year} (${y.pillar})`)) : '', years = list ? fill(F.rc_years, { list }) : '';
    // stem and branch split by the cách table: said as such (which half is which), never weighed one against the other
    // a luck pillar with its halves (TVH p.382) says which five years each half governs
    const hv = !o.year ? t.halves : null;
    const split = rc.agree === 'tron' ? `${t.tvh?.stem === 'tot' ? 'tron' : 'tron_rev'}${hv && F.rc.tron_h ? '_h' : ''}` : '';
    const fr = F.rc[split || (rc.verdict === 'co_dieu_kien' && !yongTxt ? 'co_dieu_kien_no_yong' : rc.verdict === 'nang' && !list ? (o.year ? 'nang_year' : 'nang_no_years') : rc.verdict)];
    if (!fr?.length) return;
    // the conditional verdict leans on Thiệu Vĩ Hoa's own thành bại sentence when one fired that names the dụng thần group as protection
    const tbYong = tbOrder.find(v => v.verdict !== 'xau' && yongG.some(g => tbParts(v.text)!.cond.includes(g)));
    say(xs, fill(m.pick(`bd|rv|${key}`, fr), { kind, pk, Pk: cap(pk), yong: yongTxt, years: list, yearsTail: years, stem: who.stem, branch: who.branch,
      ha: hv ? `${hv.stem[0]}–${hv.stem[1]}` : '', hb: hv ? `${hv.branch[0]}–${hv.branch[1]}` : '' }), 'he_thong',
      tbYong && (rc.verdict === 'co_dieu_kien' || rc.verdict === 'nang') ? ['TVH pp.367-369'] : [], tbYong && (rc.verdict === 'co_dieu_kien' || rc.verdict === 'nang') ? [cite(tbYong.rule_id, tbYong.text, ['TVH pp.367-369'])] : [],
      { tone: rc.verdict === 'thuan' || rc.verdict === 'kha_thuan' ? 'pos' : 'answer', step: `verdict:${key}`, verdict: classOf(rc), ...(split.endsWith('_h') ? { note: NOTE.halves } : {}), ...(cachPartial ? { conditional: 'cach_partial' } : {}) } as Partial<SentenceTrace>);
  };
  /** what a luck pillar or a year does to the useful god (TVH p.382) */
  const touchSay = (xs: ProseSentence[], t: BaziTemporal, step: string, year?: number) => {
    if (!Dd || !Y || !t.touch?.length) return;
    const T2 = Dd.touch_kind;
    // a useful-god stem bound by natal stems is told once, with every stem that binds it, in place of "mang đúng hành dụng thần"
    const bound = new Map<string, string[]>();
    for (const x of t.touch) if (x.kind === 'yong_bi_hop') (bound.get(x.who) ?? bound.set(x.who, []).get(x.who)!).push(`can ${PIL_VI[x.target ?? '']} ${x.target_stem ?? ''}`);
    const touch: Array<BaziTouch & { _ts?: string }> = [...t.touch.filter(x => x.kind !== 'yong_bi_hop' && !(x.kind === 'mang_yong' && x.part === 'stem' && bound.has(x.who))),
      ...[...bound].map(([who, ts]): BaziTouch & { _ts?: string } => ({ kind: 'yong_bi_hop', part: 'stem', who, _ts: join(ts) }))];
    const it = touch.map(x => {
      const k2 = T2[`${x.kind}_${x.part}`] ? `${x.kind}_${x.part}` : x.kind;
      return T2[k2] ? fill(T2[k2], { who: x.who, stem: x.stem ?? '', p: PIL_VI[x.target ?? ''] ?? '', t: x.target_stem ?? x.target_branch ?? '',
        ts: (x as { _ts?: string })._ts ?? join((x.targets ?? []).map((p, i) => `can ${PIL_VI[p]} ${x.target_stems?.[i] ?? ''}`)) }) : '';
    }).filter(Boolean);
    if (!it.length) return;
    const bad = t.touch.some(x => /khac_yong|hop_yong|yong_bi_hop|xung_yong/.test(x.kind)), good = t.touch.some(x => /mang_yong|sinh_yong|khac_ky/.test(x.kind));
    // a year names itself, so it never repeats the sentence of its luck pillar with the same stem
    say(xs, fill(m.pick(`bd|touch|${step}`, year && Dd.touch_year?.length ? Dd.touch_year : Dd.touch), { year: String(year ?? ''), yong: hoaC ? `hành ${Y.el}` : `${Y.group} (${Y.el})`, list: it.length > 1 ? `${it.slice(0, -1).join('; ')}; còn ${it.at(-1)}` : it[0] }), 'tinh_toan', ['TVH p.382'], [],
      { step, note: NOTE.hyky, mech: true, ...(bad && !good ? { tone: 'neg' } : good && !bad ? { tone: 'pos' } : {}) });
  };
  const told: Array<{ name: string; age: number; verdict: VerdictClass; stemGroup?: string }> = [];
  for (const l of D.luck) {
    const meta = b.luck[l.index - 1] ?? b.luck.find(x => x.name === l.pillar);
    if (!meta || meta.start_year == null || meta.start_age > 80) continue;
    const xs: ProseSentence[] = [], ds: ProseSentence[] = [];
    const [stem, branch] = l.stem && l.branch ? [l.stem, l.branch] : l.pillar.split(' ');
    const cur = meta.start_year <= yr && yr < meta.start_year + 10;
    const step = `luck:${l.index}`, rc = rcOf(l), who = { stem, branch };
    say(xs, fill(m.pick(`bd|lk${l.index}`, l.branch_god && l.stage ? F.luck_head : F.luck_head_short), { age: String(Math.round(meta.start_age)), from: String(meta.start_year), to: String(meta.start_year + 9), pillar: l.pillar,
      cur: cur ? fill(F.luck_now, { year: String(yr) }) : '', stem, branch, god: l.ten_god ?? '—', bgod: l.branch_god ?? '—', stage: l.stage ?? '' }),
    'tinh_toan', ['ZZ p.20', 'ZZ pp.24-25'], [], { step });
    cachSide(xs, l, `l${l.index}`, who, step);
    climateSide(xs, l, rc, `l${l.index}`, who, 'vận', step);
    // Đọc sâu: the halves (TVH p.382) when they differ or for the current luck, what it does to the useful god, the relations
    const hv = l.halves, v = l.tvh;
    if (hv && Dd && cur && !(v?.stem && v?.branch && v.stem !== v.branch)) {
      const tail = v?.stem && v?.branch && v.stem !== v.branch ? Dd.halves_tail[v.stem === 'tot' ? 'first' : 'second'] : '';
      say(ds, fill(m.pick(`bd|hv|${l.index}`, Dd.halves), { stem, branch, a: String(hv.stem[0]), b: String(hv.stem[1]), c: String(hv.branch[0]), d: String(hv.branch[1]), tail }), 'tinh_toan', ['TVH p.382'], [],
        { step, note: NOTE.halves, mech: true });
    }
    touchSay(ds, l, step);
    const ev = events(l, `l${l.index}`, { stem, branch, who: 'cả trụ vận' });
    if (ev) say(P ? ds : xs, ev.text, 'tinh_toan', ev.cites, [], { step });
    for (const f of l.findings) if (F.verified_text[f.rule_id]) say(xs, fill(F.verified_text[f.rule_id], { stem, branch }), 'sach', ['TTT'], [cite(f.rule_id, f.text, ['TTT'])], { tone: 'neg', step, note: 'Trích Thiên Tủy, Tuế Vận (tr.229-233).' });
    verdictOf(xs, l, rc, `l${l.index}`, who, { year: false, years: l.good_years ?? goodYearsTs(meta.start_year, dm, table, totG, xauG, needEl, l.pillar) });
    for (const s of [...xs, ...ds]) s.trace.step ??= step;
    if (meta.start_year <= yr + 60) {
      para('dai-van', xs);
      para('dai-van', ds, 'support', deep(`vận ${l.pillar}`));
      told.push({ name: l.pillar, age: meta.start_age, verdict: classOf(rc), stemGroup: l.stem_group });
    }
  }

  // ---- lưu niên: the requested year and the two after it, judged the same way ----
  for (const y of D.years ?? []) {
    const xs: ProseSentence[] = [], ds: ProseSentence[] = [], key = `y${y.year}`, step = `year:${y.year}`;
    const stem = y.stem ?? y.pillar.split(' ')[0], branch = y.branch ?? y.pillar.split(' ')[1], rc = rcOf(y), who = { stem, branch };
    say(xs, fill(m.pick(`bd|yh|${key}`, F.year_head), { year: String(y.year), pillar: y.pillar, luck: y.luck ?? '', stem, branch, god: y.ten_god, bgod: y.branch_god ?? '—', stage: y.stage ?? '' })
      .replace(/, đi trong đại vận ?:/, ':'), 'tinh_toan', ['ZZ p.20'], [], { step });
    cachSide(xs, y, key, who, step, y.year);
    climateSide(xs, y, rc, key, who, 'năm', step);
    // Đọc sâu: which half of its luck pillar the year falls in (TVH p.382), what it does to the useful god, the relations
    const lh = y.luck_half;
    if (lh && Dd && y.luck) {
      const [ls, lb] = y.luck.split(' '), part = lh.part === 'stem' ? `can ${ls}` : `chi ${lb}`;
      say(ds, fill(m.pick(`bd|yhalf|${key}`, Dd.year_half), { year: String(y.year), i: String(lh.index), luck: y.luck, part, tail: lh.verdict ? fill(Dd.year_half_tail, { part, v: F.verdict[lh.verdict] ?? '' }) : '' }),
        'tinh_toan', ['TVH p.382'], [], { step, note: NOTE.halves, mech: true });
    }
    touchSay(ds, y, step, y.year);
    const ev = events(y, key, { stem, branch, who: 'cả trụ năm', year: y.year });
    if (ev) say(P ? ds : xs, ev.text, 'tinh_toan', ev.cites, [], { step });
    const withLuck = (y.events ?? []).filter(e => e.targets[0] === 'luck' && F.year_luck[e.kind]).map(e => fill(F.year_luck[e.kind], { luck: y.luck ?? '' }));
    if (withLuck.length) say(xs, withLuck.join(' '), 'tinh_toan', ['TTT'], [], { step });
    // the year against its own luck pillar (owner review 2026-10-22): positions by the 八字真宗 pp.19-20 tables; the head-on clash and the
    // repeat of the same pillar are said just above (year_luck), so they are not repeated here
    const vl = (y as BaziTemporal & { vs_luck?: Array<{ kind: string; part: string }> }).vs_luck;
    if (vl && y.luck && Dd?.vs_luck?.length) {
      const [ls, lb] = y.luck.split(' ');
      const ks = (part: string) => [...new Set(vl.filter(e => e.part === part).map(e => Dd.vs_luck_kind?.[e.kind]).filter(Boolean) as string[])];
      const parts = [ks('stem').length ? `can ${stem} ${join(ks('stem'))} can ${ls} của vận` : '', ks('branch').length ? `chi ${branch} ${join(ks('branch'))} chi ${lb} của vận` : ''].filter(Boolean);
      say(xs, parts.length ? fill(m.pick(`bd|vsl|${key}`, Dd.vs_luck), { luck: y.luck, year: String(y.year), list: join(parts) }) : fill(m.pick(`bd|vsl0|${key}`, Dd.vs_luck_none ?? []), { luck: y.luck, year: String(y.year) }),
        'tinh_toan', ['ZZ pp.19-20'], [], { step, note: 'Quan hệ giữa năm và chính đại vận của nó tra theo bảng hợp, xung, hình, hại, phá của Bát Tự Chân Tông (tr.19-20); trang này chỉ in bảng, không in ý nghĩa, nên văn chỉ nêu vị trí.' });
    }
    let neg = false;
    for (const f of y.findings) if (F.verified_text[f.rule_id]) { neg ||= f.rule_id.endsWith('NHUOC'); say(xs, fill(F.verified_text[f.rule_id], { year: String(y.year), stem, branch }), 'sach', ['TTT'], [cite(f.rule_id, f.text, ['TTT'])], { tone: f.rule_id.endsWith('NHUOC') ? 'neg' : 'pos', step, note: 'Trích Thiên Tủy, Tuế Vận (tr.229-233).' }); }
    // a year the thiên khắc địa xung rule calls a great ill is told so, with what to do, whatever the tables say
    verdictOf(xs, y, neg && rc.verdict !== 'nang' ? { ...rc, verdict: 'nang', support: [] } : rc, key, who, { year: true });
    para('luu-nien', xs);
    para('luu-nien', ds, 'support', deep(`năm ${y.year}`));
  }

  // ---- tổng kết: the diagnosis in one sentence, then the timeline by the very verdicts the đại vận paragraphs gave, the turning point ----
  if (told.length && F.tk_open.length) {
    const xs: ProseSentence[] = [];
    if (Dd && tableOk && CT!.dominant && CT!.yong.length) {
      const heat = needEl ? fill(Dd.tk_diag_heat, { climate: D.climate.label ?? '', mb, need: `hành ${needEl}` }) : '';
      say(xs, fill(m.pick('bd|tkd', Dd.tk_diag), { dm, level: levelVi, dom: CT!.dominant, yong: Y1, heat }), 'he_thong', [], [], { step: 'closing:bat_tu' });
    } else if (Dd && CT?.special && Y?.kind === 'special') say(xs, fill(m.pick('bd|tkds', Dd.tk_diag_special), { dm, name: CT.special.replace(/\s*\(TVH\)$/, ''), yong: `hành ${Y.el} (${Y.group})` }), 'he_thong', [], [], { step: 'closing:bat_tu' });
    else say(xs, fill(m.pick('bd|tk', F.tk_open), { dm, level: levelVi, mb, need: needEl }).replace(/, lá số cần \./, '.').replace(/; hành cần bổ là \./, '.'), 'he_thong', [], [], { step: 'closing:bat_tu' });
    const cuts = [0, 30, 60, 200], ORDER: VerdictClass[] = ['thuan', 'kha_thuan', 'co_dieu_kien', 'tron', 'nang', 'trung'];
    F.tk_phase_name.forEach((ph, i) => {
      const xsP = told.filter(x => x.age >= cuts[i] - 0.5 && x.age < cuts[i + 1] - 0.5);
      if (!xsP.length) return;
      const parts = ORDER.map(v => [v, xsP.filter(x => x.verdict === v)] as const).filter(([, g]) => g.length)
        .map(([v, g]) => fill((g.length > 1 ? F.tk_class_many : F.tk_class)[v], { list: join(g.map(x => `${x.name} (từ ${Math.round(x.age)} tuổi thực)`)), yong: Y1 ? `nhóm ${Y1}` : 'chỗ dựa' }));
      const list = parts.length > 1 ? `${parts.slice(0, -1).join('; ')}; còn ${parts.at(-1)}` : parts[0];
      const tone = xsP.every(x => x.verdict === 'nang') ? 'neg' : xsP.every(x => x.verdict === 'thuan' || x.verdict === 'kha_thuan') ? 'pos' : undefined;
      say(xs, fill(m.pick(`bd|tkp${i}`, F.tk_phase), { phase: ph, list }), 'he_thong', [], [], { step: 'closing:bat_tu', tone, verdicts: xsP.map(x => [x.name, x.verdict]) } as Partial<SentenceTrace>);
    });
    // the turning point: the first luck pillar whose stem brings the useful god after none did, else the first one called good after others
    if (Dd && told.length > 1) {
      const good = (v: VerdictClass) => v === 'thuan' || v === 'kha_thuan';
      const yi = Y1 ? told.findIndex(x => x.stemGroup === Y1) : -1;
      const gi = told.findIndex(x => good(x.verdict));
      const [i, what] = yi > 0 ? [yi, good(told[yi].verdict) && told[yi].verdict === 'thuan' ? 'both' : 'yong_stem'] : gi > 0 ? [gi, told[gi].verdict === 'thuan' ? 'both' : 'first_good'] : [-1, ''];
      if (i > 0) say(xs, fill(m.pick('bd|tkt', Dd.tk_turn), { pillar: told[i].name, age: String(Math.round(told[i].age)), what: Dd.tk_turn_what[what] }), 'he_thong', [], [], { step: 'closing:bat_tu' });
    }
    if (cachPartial && Dd?.tk_cond?.length) say(xs, fill(m.pick('bd|tkc', Dd.tk_cond), { cach: CT!.cach! }), 'he_thong', [], [], { step: 'closing:bat_tu', conditional: 'cach_partial' } as Partial<SentenceTrace>);
    const dhOk = table.filter(x => { const g = dh.stems.find(s => s.stem === x)?.ten_god; return !g || !xauG.includes(GROUP_OF[g]); });
    const good = [...totG.map(x => `nhóm ${x}`), ...(dhOk.length ? [`can ${join(dhOk)}`] : [])];
    if (F.tk_advice.length && good.length) say(xs, fill(m.pick('bd|tka', F.tk_advice), { good: join(good), bad: xauG.length ? join(xauG.map(x => `nhóm ${x}`)) : '' })
      .replace(/, còn  là những nhóm nên giữ sức/, '').replace(/, chỗ nên giữ sức là ;/, ';'), 'he_thong', [], [], { step: 'closing:bat_tu', tone: 'answer' });
    para('tong-ket', xs, 'course');
  }
  return out;
}

const GROUP_OF: Record<string, string> = { 'Tỉ Kiên': 'Tỉ Kiếp', 'Kiếp Tài': 'Tỉ Kiếp', 'Thực Thần': 'Thực Thương', 'Thương Quan': 'Thực Thương', 'Chính Tài': 'Tài', 'Thiên Tài': 'Tài',
  'Chính Quan': 'Quan Sát', 'Thất Sát': 'Quan Sát', 'Chính Ấn': 'Ấn', 'Thiên Ấn': 'Ấn' };

const STEMS_VI = ['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý'];
const BRANCHES_VI = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'];
const EL_ORDER = ['Mộc', 'Hỏa', 'Thổ', 'Kim', 'Thủy'];
const stemEl = (s: string) => EL_ORDER[Math.floor(STEMS_VI.indexOf(s) / 2)];
/** the ten-god group of a stem against the day master (八字真宗 p.17 by element: same, generated, controlled, controlling, generating) */
export function groupOf(dm: string, s: string): string {
  const d = EL_ORDER.indexOf(stemEl(dm)), o = EL_ORDER.indexOf(stemEl(s)), k = (o - d + 5) % 5;
  return ['Tỉ Kiếp', 'Thực Thương', 'Tài', 'Quan Sát', 'Ấn'][k];
}
/** the điều hậu role of a stem by name: the cell's chính stem, another stem it names, or none (bazi_deep.pipeline._dh_role) */
export function dhRoleOf(stem: string | undefined, table: string[]): 'yong' | 'xi' | null {
  return !stem || !table.length ? null : stem === table[0] ? 'yong' : table.includes(stem) ? 'xi' : null;
}
/** the verdict as the reader is told it: a conditional verdict from a stem / branch split ('tron') is "tốt xấu đan xen", one from the two
 *  tables disagreeing is "tùy lúc có dụng thần đi kèm"; the đại vận paragraphs, the lưu niên and the closing all use this one class */
export type VerdictClass = Reconcile['verdict'] | 'tron';
export const classOf = (rc: Reconcile): VerdictClass => rc.verdict === 'co_dieu_kien' && rc.agree === 'tron' ? 'tron' : rc.verdict;
/** bazi_deep.pipeline.reconcile, for facts from before it (same inputs, same table) */
export function reconcileTs(t: BaziTemporal, dm: string, table: string[], needEl: string, yongG: string[], xauG: string[]): Reconcile {
  const stem = t.stem ?? '', cs = t.tvh?.stem ?? null, cb = t.tvh?.branch ?? null;
  const cach: Reconcile['cach'] = cs && (cb == null || cb === cs) ? cs : !cs ? cb : 'tron';
  const warm = !!needEl && !!stem && stemEl(stem) === needEl;
  const climate = dhRoleOf(stem, table) || dhRoleOf(t.hidden?.[0]?.stem, table) || warm ? 'thuan' : null;
  const [agree, verdict]: [Reconcile['agree'], Reconcile['verdict']] = cach === 'tot' ? (climate ? ['cung', 'thuan'] : ['mot_phia', 'kha_thuan'])
    : cach === 'xau' ? (climate ? ['khac', 'co_dieu_kien'] : ['mot_phia', 'nang']) : cach === 'tron' ? ['tron', 'co_dieu_kien']
    : climate ? ['mot_phia', 'kha_thuan'] : ['khong', 'trung'];
  const rc: Reconcile = { cach, climate, warm, agree, verdict };
  if (cach === 'xau' || cach === 'tron') rc.support = (t.hidden ?? []).map(h => ({ stem: h.stem, ten_god: h.ten_god, group: groupOf(dm, h.stem),
    why: [...(yongG.includes(groupOf(dm, h.stem)) ? ['cach'] : []), ...(table.includes(h.stem) ? ['dieu_hau'] : [])] })).filter(x => x.why.length && !xauG.includes(x.group));
  return rc;
}
/** bazi_deep.pipeline good_years, for facts from before it: a luck pillar's years whose stem the cách table calls good or the điều hậu
 *  cell names (and the cách table does not call bad) */
export function goodYearsTs(first: number, dm: string, table: string[], totG: string[], xauG: string[], needEl = '', luck?: string): NonNullable<BaziTemporal['good_years']> {
  // mirrors bazi_deep.pipeline good_years (owner review 2026-10-22): a year is listed when ITS OWN verdict (stem and branch by the cách
  // table, the điều hậu cell) is thuận or khá thuận and it does not clash head-on with the luck pillar (thiên khắc địa xung)
  const out: NonNullable<BaziTemporal['good_years']> = [];
  const role = (g: string) => totG.includes(g) ? 'tot' as const : xauG.includes(g) ? 'xau' as const : null;
  const [ls, lb] = luck ? luck.split(' ') : [];
  for (let y = first; y < first + 10; y++) {
    const s = STEMS_VI[(((y - 4) % 10) + 10) % 10], br = BRANCHES_VI[(((y - 4) % 12) + 12) % 12], g = groupOf(dm, s), main = MAIN_QI[BRANCHES_VI.indexOf(br)];
    const rc = reconcileTs({ stem: s, tvh: { stem: role(g), branch: role(groupOf(dm, main)) }, hidden: [{ stem: main, ten_god: '' }] }, dm, table, needEl, [], xauG);
    const phan = !!ls && STEM_CLASH.has([s, ls].sort().join('|')) && (BRANCHES_VI.indexOf(br) - BRANCHES_VI.indexOf(lb) + 12) % 12 === 6;
    if ((rc.verdict === 'thuan' || rc.verdict === 'kha_thuan') && !phan)
      out.push({ year: y, pillar: `${s} ${br}`, group: g, verdict: rc.verdict, why: [...(rc.cach === 'tot' ? ['cach'] : []), ...(rc.climate === 'thuan' ? ['dieu_hau'] : [])] } as NonNullable<BaziTemporal['good_years']>[number]);
  }
  return out;
}
/** main qi of each branch (八字真宗 pp.7-8) and the ten stem clash / control pairs of 八字真宗 p.20 (bazi.STEM_CLASH_KIND) */
const MAIN_QI = ['Quý', 'Kỷ', 'Giáp', 'Ất', 'Mậu', 'Bính', 'Đinh', 'Kỷ', 'Canh', 'Tân', 'Mậu', 'Nhâm'];
const STEM_CLASH = new Set([['Canh', 'Giáp'], ['Tân', 'Ất'], ['Bính', 'Nhâm'], ['Quý', 'Đinh'], ['Giáp', 'Mậu'], ['Kỷ', 'Ất'], ['Bính', 'Canh'], ['Tân', 'Đinh'], ['Mậu', 'Nhâm'], ['Kỷ', 'Quý']].map(p => p.sort().join('|')));
