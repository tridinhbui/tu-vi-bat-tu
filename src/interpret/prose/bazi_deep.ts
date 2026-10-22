// Bát Tự structure prose (plan async-inventing-fairy C, deepened by plan quirky-tinkering-rabin Track C): what the structure analysis
// (engine/tvbt/bazi_deep, facts.bazi.deep) computes, told chapter by chapter. Only books and calculation (owner's decision 2026-10-21: no
// common meanings). Basis per sentence:
//   - sach: a verified rule that fired, with its id (BT_TVH_* on strength and on the cách's thành bại, TVH pp.367-369; the Trích Thiên Tủy
//     rules on hàn noãn, nguyên lưu, Quan Sát hỗn tạp, Thương Quan, tòng / hóa; the TTT 歲運 rules on luck pillars and years);
//   - tinh_toan: a computed fact or a page-cited table (TVH score pp.331-355, TVH dụng thần and vận hỷ kỵ table pp.378-386, the TVH điều hậu
//     table pp.389-396, the 八字真宗 tables: hợp xung hình hại phá pp.19-20, nạp âm pp.20-21, thần sát pp.21-22, trường sinh pp.24-25, the
//     marriage and spouse palaces p.57);
//   - he_thong: the closing words that re-say what the paragraph already told (advice, the summary over the timeline).
// The relations between a luck pillar or a year and the natal pillars are told as positions: 八字真宗 pp.19-20 prints the tables only, no
// meanings, so no meaning is given to them; the day branch is named the spouse palace, and the month branch the marriage palace, by p.57.
// Balanced on purpose: a luck pillar the table calls bad is turned with what the other table says, or with what to do, never left as a verdict.
// Method reconciliation (plan quirky-tinkering-rabin step 3, S2): every luck pillar and year gets ONE verdict from the cách table (TVH
// pp.378-386: the day master's balance against the largest group) and the điều hậu table (pp.389-396: the season's cold or heat), by stem
// name, never by ten-god group (`reconcile`, mirrored from bazi_deep.pipeline.reconcile for facts older than it). Where the two agree the
// verdict is firm; where they differ the text says where and how far each table goes, and the verdict is conditional; the đại vận chapter,
// the lưu niên and the closing all read the same verdicts. The cold/heat element ("cần Hỏa") is voiced only through the Trích Thiên Tủy
// hàn noãn rule that names it, never as the điều hậu table's (its cell names stems). Phù ức is a draft method and nothing here reasons by it.
import type { ChartInput, Knowledge } from '../types.ts';
import { Micro, finish, lowerFirst } from './micro.ts';
import type { ProseParagraph, ProseSentence, SentenceTrace } from './realize.ts';

type Role = 'yong' | 'xi' | 'ji' | null;
type Verdict = 'tot' | 'xau' | null;
export interface BaziEvent { kind: string; targets: string[]; part: 'stem' | 'branch' | 'pillar'; opens_kho?: boolean; element?: string | null }
/** a temporal pillar (luck or year) as computed facts: ten gods, hidden stems, growth stage of the day master, the TVH table's verdicts */
export interface BaziTemporal {
  stem?: string; branch?: string; branch_god?: string; hidden?: Array<{ stem: string; ten_god: string }>; stage?: string;
  stem_group?: string; branch_group?: string; stem_element?: string; branch_element?: string; tvh?: { stem: Verdict; branch: Verdict };
  can_chi_detail?: { relation: string; mitigated: boolean; aggravated: boolean } | null; events?: BaziEvent[];
  /** the combined verdict (bazi_deep.pipeline.reconcile); absent in facts older than it, then computed here the same way */
  reconcile?: Reconcile;
  /** the luck pillar's years whose stem the cách table calls good or the điều hậu cell names (absent in older facts) */
  good_years?: Array<{ year: number; pillar: string; group: string; why: string[] }>; first_year?: number;
}
export interface Reconcile {
  cach: 'tot' | 'xau' | 'tron' | null; climate: 'thuan' | null; warm: boolean; agree: 'cung' | 'khac' | 'tron' | 'mot_phia' | 'khong';
  verdict: 'thuan' | 'kha_thuan' | 'co_dieu_kien' | 'nang' | 'trung';
  support?: Array<{ stem: string; ten_god: string; group: string; why: string[] }>;
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
}
/** the part of the chapter frame a paragraph holds (plan step 4); the sources, part 6, are each sentence's trace */
export type FramePart = 'cau_truc' | 'ho_tro' | 'tuong_tac' | 'mau_thuan' | 'ket_luan';
export type BaziDeepChapter = 'nhat-chu' | 'ngu-hanh' | 'su-nghiep' | 'quan-he' | 'dai-van' | 'cach-cuc' | 'luu-nien' | 'tong-ket';

const join = (xs: string[]) => xs.length < 2 ? (xs[0] ?? '') : `${xs.slice(0, -1).join(', ')} và ${xs.at(-1)}`;
const fill = (t: string, v: Record<string, string>) => t.replace(/\{([A-Za-z0-9_]+)\}/g, (m, k) => v[k] ?? m);
const PIL_VI: Record<string, string> = { year: 'năm', month: 'tháng', day: 'ngày', hour: 'giờ', luck: 'đại vận', year_t: 'năm' };
const K = ['year', 'month', 'day', 'hour'] as const;
/** a TVH thành bại claim "theo Thiệu Vĩ Hoa (tr.367-369): <condition>: <verdict>" -> its condition and verdict */
export function tbParts(text: string): { cond: string; verdict: string } | null {
  const m = text.replace(/^theo Thiệu Vĩ Hoa \([^)]*\):\s*/, '').match(/^(.*):\s*([^:]+)$/);
  return m ? { cond: m[1].trim(), verdict: m[2].trim() } : null;
}

export function deepBazi(chart: ChartInput, k: Knowledge, m: Micro, F: BaziDeepFrames | undefined,
  rules: Record<string, { reading: string; cites: string[]; verified: boolean }>): Partial<Record<BaziDeepChapter, ProseParagraph[]>> {
  void k;
  const b = chart.bazi as (ChartInput['bazi'] & { deep?: BaziDeep | null }) | undefined, D = b?.deep;
  if (!b || !D || !F) return {};
  const say = (xs: ProseSentence[], text: string, basis: SentenceTrace['basis'], cites: string[] = [], ids: string[] = [], extra: Partial<SentenceTrace> = {}) => {
    const t = finish(text); m.said(t);
    xs.push({ text: t, trace: { move: 'ELABORATE', concepts: [], rules: ids, cites, basis, ...extra } });
  };
  const fired = new Map(D.verified.map(v => [v.rule_id, v]));
  const cite = (id: string, text: string, cites: string[]) => { rules[id] = { reading: text, cites, verified: true }; return id; };
  const pil = b.pillars, dm = b.day_master, el = b.day_master_element, mb = pil.month.branch;
  const out: Partial<Record<BaziDeepChapter, ProseParagraph[]>> = {};
  const para = (id: BaziDeepChapter, xs: ProseSentence[], role: ProseParagraph['role'] = 'support') => { if (xs.length) (out[id] ??= []).push({ role, sentences: xs, text: xs.map(s => s.text).join(' ') }); };
  // the 40% rule always decides (TVH p.355, which calls a 39.6% example "hơi nhược"); near the line the reading says "hơi" and the system's
  // ±3% band stays a note (audit BZ-9/10: the reading never gives a third level, nor the system's seven-level label)
  const sh = D.strength.own_share, th = D.strength.threshold, near = D.strength.near_threshold ?? fired.has('BT_TVH_BIEN');
  const strong = D.strength.dm_strong;
  const levelVi = strong == null ? 'ở mức cân bằng' : `${near ? 'hơi ' : ''}${strong ? 'vượng' : 'nhược'}`;
  const CT = D.cach_tvh, dh = D.dieu_hau;
  const tableOk = CT?.status === 'ap_dung' && !!CT.cach;
  // the stems the điều hậu cell names (chính first), and the element a fired hàn noãn rule asks for (TTT pp.113-114)
  const table = dh.verified ? (dh.table ?? dh.stems.map(s => s.stem)) : [];
  const needRule = fired.has('BT_TTT_HANNOAN_CAN_NOAN') ? 'BT_TTT_HANNOAN_CAN_NOAN' : fired.has('BT_TTT_HANNOAN_CAN_HAN') ? 'BT_TTT_HANNOAN_CAN_HAN' : '';
  const needEl = needRule === 'BT_TTT_HANNOAN_CAN_NOAN' ? 'Hỏa' : needRule ? 'Thủy' : '';
  const yongG = tableOk ? CT!.yong : [], totG = tableOk ? CT!.van_tot : [], xauG = tableOk ? CT!.van_xau : [];
  const rcOf = (t: BaziTemporal) => t.reconcile ?? reconcileTs(t, dm, table, needEl, yongG, xauG);
  const tvhPage = CT?.page ? `TVH pp.${CT.page.replace(/\s/g, '')}` : 'TVH pp.378-386';

  // ---- frame (second sentence): season, TVH verdict, điều hậu need ----
  const frame: ProseSentence[] = [];
  if (D.strength.season_state && sh != null && F.frame2) {
    // the điều hậu cell names stems; the element "cần Hỏa" is the system's cold/heat index and is not told here (it was, as the table's)
    const need = table.length ? join(table) : '';
    say(frame, fill(m.pick('bd|frame2', need ? F.frame2 : F.frame2_no_need), { mb, season: F.season_name[mb] ?? '', el, dm, state: F.season_state[D.strength.season_state]?.split(',')[0] ?? D.strength.season_state,
      need }), 'tinh_toan', ['ZZ (ngũ hành vượng tướng hưu tù tử)', ...(need ? ['TVH pp.389-396'] : [])], [], { step: 'frame:bat_tu:2' });
  }
  if (frame.length) para('nhat-chu', frame, 'structure');

  // ---- nhật chủ: season, strength by TVH's score, growth stages, the turn ----
  const st: ProseSentence[] = [];
  if (D.strength.season_state && !frame.length) say(st, fill(m.pick('bd|season', F.season), { dm, el, mb, state: F.season_state[D.strength.season_state] ?? D.strength.season_state }), 'tinh_toan', ['ZZ (ngũ hành vượng tướng hưu tù tử)']);
  if (sh != null && th != null) {
    const pct = String(Math.round(sh * 100)), thp = String(Math.round(th * 100));
    if (near && strong != null) say(st, fill(m.pick('bd|near', F.strength_near), { pct, th: thp, cmp: strong ? 'trên' : 'dưới', side: strong ? 'vượng' : 'nhược' }), 'tinh_toan', ['TVH pp.331-355'], [],
      { note: 'Thiệu Vĩ Hoa (tr.355) gọi một ví dụ 39,6% là "hơi nhược": sát ngưỡng vẫn là một kết luận. Dải ±3% quanh 40% là quy ước hiển thị của hệ thống, không phải của sách.' });
    else if (strong != null) {
      const id = strong ? 'BT_TVH_VUONG' : 'BT_TVH_NHUOC', v = fired.get(id);
      say(st, fill(m.pick('bd|side', F.strength_side), { pct, th: thp, cmp: strong ? 'vượt' : 'dưới', side: strong ? 'thuộc thế vượng' : 'thuộc thế nhược' }),
        v ? 'sach' : 'tinh_toan', ['TVH pp.331-355'], v ? [cite(id, v.text, ['TVH pp.331-355'])] : []);
    }
  }
  const ps = D.pillars;
  if (ps && F.stages) {
    say(st, fill(m.pick('bd|stages', F.stages), { dm, list: join(K.map(x => `chi ${PIL_VI[x]} ${pil[x].branch} ở ${ps[x].stage}`)) }), 'tinh_toan', ['ZZ pp.24-25']);
    // the turn: a weak day master that still stands at its peak somewhere, or a strong one that meets its grave or end
    const peak = K.filter(x => ['Trường Sinh', 'Lâm Quan', 'Đế Vượng'].includes(ps[x].stage)), low2 = K.filter(x => ['Tử', 'Mộ', 'Tuyệt'].includes(ps[x].stage));
    const turnAt = strong === false ? peak : strong === true ? low2 : [];
    if (turnAt.length && F.stage_turn) say(st, fill(m.pick('bd|stturn', F.stage_turn), { at: join(turnAt.map(x => `chi ${PIL_VI[x]} ${pil[x].branch}`)), stage: join([...new Set(turnAt.map(x => ps[x].stage))]),
      dir: strong ? 'chỗ khí nhật chủ lắng xuống' : 'chỗ nhật chủ còn khí mạnh' }), 'tinh_toan', ['ZZ pp.24-25'], [], { tone: strong ? 'neg' : 'pos' });
  }
  para('nhat-chu', st);

  // ---- ngũ hành: TVH's scored totals and the largest group ----
  const tot = D.strength.tvh_totals;
  if (tot && Object.keys(tot).length && F.totals) {
    const xs = Object.entries(tot).sort((x, y) => y[1] - x[1]), num = (v: number) => String(v).replace('.', ',');
    const nh: ProseSentence[] = [];
    say(nh, fill(m.pick('bd|totals', F.totals), { top: join(xs.slice(0, 2).map(([e, v]) => `${e} (${num(v)})`)), low: `${xs.at(-1)![0]} (${num(xs.at(-1)![1])})`,
      dom: CT?.dominant ?? '' }).replace(/; nhóm  chiếm[^.]*/, ''), 'tinh_toan', ['TVH pp.331-355']);
    para('ngu-hanh', nh);
  }

  // ---- cách cục và dụng thần, in the chapter frame (plan step 4): 1 cấu trúc (the cách and the table's dụng thần), 2 hỗ trợ / hạn chế
  // (TVH's thành bại sentences, where the dụng thần group stands in the chart), 3 tương tác (điều hậu, the Trích Thiên Tủy rules),
  // 4 mâu thuẫn (where the cách and điều hậu tables differ, and how far each goes), 5 kết luận có điều kiện; 6, the sources, stay in each
  // sentence's trace (the "Căn cứ" fold), never in the text ----
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
    say(i === 0 ? c1 : c2, fill(m.pick(`bd|tb${i}`, frames), { mb, cach: cachName ?? '', cond: lowerFirst(cond), verdict: lowerFirst(verdict) }), 'sach', ['TVH pp.367-369'],
      [cite(v.rule_id, v.text, ['TVH pp.367-369'])], { tone: xau ? 'neg' : 'pos' });
  });
  if (tableOk && CT!.yong.length) {
    const vars = { cach: CT!.cach!, dm: levelVi, dom: CT!.dominant ?? '', yong: join(CT!.yong), tot: join(CT!.van_tot), xau: join(CT!.van_xau) };
    say(c1, fill(m.pick('bd|table', CT!.van_tot.length || CT!.van_xau.length ? F.table : F.table_no_van), vars), 'tinh_toan', [tvhPage]);
    // where the dụng thần group stands in the four pillars (the day stem is the day master itself)
    const yg = new Set(CT!.yong), many = CT!.yong.length > 1;
    const vis = (['year', 'month', 'hour'] as const).filter(x => yg.has(GROUP_OF[pil[x].stem_ten_god ?? ''])).map(x => `can ${PIL_VI[x]} ${pil[x].stem}${many ? ` (${pil[x].stem_ten_god})` : ''}`);
    const hid = K.flatMap(x => pil[x].hidden.filter(h => yg.has(GROUP_OF[h.ten_god])).map(h => `chi ${PIL_VI[x]} ${pil[x].branch} (${h.stem})`));
    if (F.yong_where) say(c2, fill(F.yong_where[vis.length ? 'vis' : hid.length ? 'hid' : 'none'], { yong: join(CT!.yong), vis: join(vis), hid: join(hid), hid2: hid.length && vis.length ? fill(F.yong_where.and_hid, { hid: join(hid) }) : '' }),
      'tinh_toan', ['ZZ p.17'], [], { tone: vis.length ? 'pos' : 'neg' });
  } else if (CT?.special && F.table_special && (CT.special_tot.length || CT.special_xau.length)) {
    say(c1, fill(m.pick('bd|tsp', F.table_special), { name: CT.special.replace(/\s*\(TVH\)$/, ''), tot: join(CT.special_tot), xau: join(CT.special_xau) || 'không có hành nào' }), 'tinh_toan', ['TVH pp.385-386']);
  }
  // the two tables of the same book name different useful gods: said in part 4, with where they differ and how far each goes
  const mainGroups = dh.stems.filter(s => s.rank.startsWith('chính')).map(s => s.ten_god);
  const differs = !!(dh.verified && dh.stems.length && tableOk && CT!.yong.length && mainGroups.length && !mainGroups.some(g => CT!.yong.some(y => GROUP_OF[g] === y)));
  if (dh.verified && dh.stems.length) {
    const main = dh.stems.filter(s => s.rank.startsWith('chính')).map(s => `${s.stem} (${s.ten_god})`), others = dh.stems.filter(s => !s.rank.startsWith('chính')).map(s => `${s.stem} (${s.ten_god})`);
    const mainTxt = join(main.length ? main : others.slice(0, 1));
    if (differs && F.dh_turn) say(c4, fill(m.pick('bd|dhturn', F.dh_turn), { mb, dm, climate: D.climate.label ?? '', main: mainTxt, yong: join(CT!.yong) }), 'tinh_toan', ['TVH pp.389-396']);
    else say(c3, fill(m.pick('bd|cl', F.climate), { mb, dm, climate: D.climate.label ?? '', main: mainTxt, others: join(main.length ? others : others.slice(1)) || 'không có can nào khác' }),
      'tinh_toan', ['TVH pp.389-396']);
    const present = dh.stems.filter(s => s.visible || s.hidden).map(s => s.stem), absent = dh.stems.filter(s => !s.visible && !s.hidden).map(s => s.stem);
    if (present.length && absent.length) say(c3, fill(m.pick('bd|pr', F.climate_presence), { present: join(present), absent: join(absent) }), 'tinh_toan', ['TVH pp.389-396']);
  }
  // the Trích Thiên Tủy rules that fired, in the order hàn noãn, nguyên lưu, Quan Sát hỗn tạp, Thương Quan, tòng / hóa; a rule whose premise
  // names the day master's strength is said only when the TVH verdict agrees with it
  const TTT_ORDER = ['BT_TTT_HANNOAN', 'BT_TTT_NGUYENLUU', 'BT_TTT_HONTAP', 'BT_TTT_TQ', 'BT_TTT_TONG', 'BT_TTT_HOA', 'BT_TVH_CV', 'BT_TVH_TONG', 'BT_TVH_HOA'];
  for (const pre of TTT_ORDER) for (const [id, v] of fired) {
    if (!id.startsWith(pre) || !F.verified_text[id]) continue;
    const need = F.premise[id];
    if (need && (strong == null || (need === 'strong') !== strong)) continue;
    const src = id.startsWith('BT_TVH') ? 'TVH pp.369-376' : 'TTT';
    say(c3, F.verified_text[id], 'sach', [src], [cite(id, v.text, [src])], /_KY$|CO_BENH/.test(id) ? { tone: 'neg' } : {});
  }
  // part 4: where the two tables part ways (the balance of the day master against its largest group, the season's cold or heat) and how far
  // each goes (yongshen.METHOD_META: both transcribed as printed; the cách table comes with the scoring the strength verdict uses, the điều
  // hậu table is one Thiệu Vĩ Hoa says a reader sent him, origin unknown, p.388), so where they differ the verdict is conditional
  const luckRcs = D.luck.map(l => rcOf(l));
  const clash = differs || luckRcs.some(r => r.agree === 'khac');
  if (clash && tableOk && table.length && F.reliability?.length) {
    const note = 'Mức tin cậy (yongshen.METHOD_META): bảng dụng thần theo cách tr.378-386 chép khớp trang in, quy tắc 40% khớp tr.355; bảng điều hậu tr.389-396 chép khớp trang in, việc gán can chính là Dụng là quy ước của hệ thống, và Thiệu Vĩ Hoa ghi bảng do độc giả gửi, chưa rõ xuất xứ (tr.388). Chưa phép nào được kiểm nghiệm thực tế.';
    F.reliability.forEach((f, i) => say(c4, fill(f, { dm: levelVi, dom: CT!.dominant ?? '', climate: D.climate.label ?? '', mb }), 'tinh_toan', [tvhPage, 'TVH pp.388-396'], [], { step: `reconcile:cach:${i}`, ...(i ? { note } : {}) }));
  }
  // part 5: what to do, conditional where the tables differ: lean on the cách's dụng thần, take the điều hậu stems the cách table does not
  // call bad as a plus, and read the luck pillars where they differ by whether the dụng thần comes along
  if ((c1.length || c3.length) && F.advice && (tableOk || table.length)) {
    const dhOk = table.filter(x => { const g = dh.stems.find(s => s.stem === x)?.ten_god; return !g || !xauG.includes(GROUP_OF[g]); });
    const lean = tableOk && CT!.yong.length ? `nhóm ${join(CT!.yong)}` : '', dhTxt = dhOk.length ? `can ${join(dhOk)}` : '', heat = needEl ? `hành ${needEl}` : '';
    if (clash && lean && F.conclusion_split?.length) say(c5, fill(m.pick('bd|cs', F.conclusion_split), { lean, extra: join([dhTxt, heat].filter(Boolean)) || lean, yong: join(CT!.yong) })
      .replace(/, thêm  về khí hậu/, ''), 'he_thong', [tvhPage, 'TVH pp.389-396'], [], { tone: 'answer', step: 'conclusion:cach' });
    else say(c5, fill(m.pick('bd|adv', F.advice), { lean: join([lean, dhTxt, heat].filter(Boolean)), tot: totG.length ? join(totG) : '', xau: xauG.length ? join(xauG) : '' })
      .replace(/; những chặng gặp  thuận hơn những chặng gặp /, '').replace(/ thuận hơn những chặng gặp \./, '.'), 'he_thong', [], [], { tone: 'answer', step: 'conclusion:cach' });
  }
  const part = (xs: ProseSentence[], key: FramePart) => { if (xs.length) (out['cach-cuc'] ??= []).push({ role: 'support', sentences: xs, text: xs.map(s => s.text).join(' '), part: key } as ProseParagraph); };
  part(c1, 'cau_truc'); part(c2, 'ho_tro'); part(c3, 'tuong_tac'); part(c4, 'mau_thuan'); part(c5, 'ket_luan');

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

  // ---- đại vận: one paragraph per luck pillar, from the first that starts after birth ----
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
      for (const [p, ks] of by) { const key = join([...new Set(ks)]); (same.get(key) ?? same.set(key, []).get(key)!).push(p); }
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
  /** the cách side (support / limit): the TVH table's verdict on the stem and the branch */
  const cachSide = (xs: ProseSentence[], t: BaziTemporal, key: string, who: { stem: string; branch: string }, year?: number) => {
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
    say(xs, year ? `Xét năm ${year}, ${lowerFirst(t0)}` : t0, 'tinh_toan', [CT!.special ? 'TVH pp.385-386' : tvhPage], [], { tone: (v.stem ?? v.branch) === 'xau' ? 'neg' : (v.stem ?? v.branch) === 'tot' ? 'pos' : undefined });
  };
  /** the climate side: the stem (or the branch's main qi) the điều hậu cell names, or the element the hàn noãn rule asks for; turned with a
   *  contrast when the cách side called the pillar bad */
  const climateSide = (xs: ProseSentence[], t: BaziTemporal, rc: Reconcile, key: string, who: { stem: string; branch: string }, kind: string) => {
    const sr = dhRoleOf(who.stem, table), h = t.hidden?.[0]?.stem, br = sr ? null : dhRoleOf(h, table);
    const k = sr ?? (br ? `branch_${br}` : rc.warm ? (needEl === 'Hỏa' ? 'warm' : 'cool') : '');
    if (!k || !F.dh_role[k]) return;
    const text = fill(F.dh_role[k], { stem: who.stem, branch: who.branch, h: h ?? '', kind, el: needEl, pk: `${kind} ${who.stem} ${who.branch}` });
    const turn = rc.cach === 'xau' ? m.conn('contrast', `bd|turn|${key}`) || 'Tuy nhiên,' : '';
    say(xs, turn ? `${turn} ${lowerFirst(text)}` : text, rc.warm && !sr && !br ? 'sach' : 'tinh_toan', rc.warm && !sr && !br ? ['TTT'] : ['TVH pp.389-396'],
      rc.warm && !sr && !br && needRule && fired.get(needRule) ? [cite(needRule, fired.get(needRule)!.text, ['TTT'])] : [], { tone: 'pos' });
  };
  /** where the tables differ (part 4) and the one verdict with what to do (part 5); the same verdict feeds the closing */
  const verdictOf = (xs: ProseSentence[], t: BaziTemporal, rc: Reconcile, key: string, who: { stem: string; branch: string }, o: { year: boolean; years?: BaziTemporal['good_years'] }) => {
    const kind = o.year ? 'năm' : 'vận', step = `reconcile:${key}`, pk = `${kind} ${who.stem} ${who.branch}`;
    const yongTxt = yongG.length ? `nhóm ${join(yongG)}` : '';
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
    const split = rc.agree === 'tron' ? (t.tvh?.stem === 'tot' ? 'tron' : 'tron_rev') : '';
    const fr = F.rc[split || (rc.verdict === 'co_dieu_kien' && !yongTxt ? 'co_dieu_kien_no_yong' : rc.verdict === 'nang' && !list ? (o.year ? 'nang_year' : 'nang_no_years') : rc.verdict)];
    if (!fr?.length) return;
    // the conditional verdict leans on Thiệu Vĩ Hoa's own thành bại sentence when one fired that names the dụng thần group as protection
    const tbYong = tbOrder.find(v => v.verdict !== 'xau' && yongG.some(g => tbParts(v.text)!.cond.includes(g)));
    say(xs, fill(m.pick(`bd|rv|${key}`, fr), { kind, pk, Pk: pk.charAt(0).toLocaleUpperCase('vi') + pk.slice(1), yong: yongTxt, years: list, yearsTail: years, stem: who.stem, branch: who.branch }), 'he_thong',
      tbYong && (rc.verdict === 'co_dieu_kien' || rc.verdict === 'nang') ? ['TVH pp.367-369'] : [], tbYong && (rc.verdict === 'co_dieu_kien' || rc.verdict === 'nang') ? [cite(tbYong.rule_id, tbYong.text, ['TVH pp.367-369'])] : [],
      { tone: rc.verdict === 'thuan' || rc.verdict === 'kha_thuan' ? 'pos' : 'answer', step: `verdict:${key}`, verdict: classOf(rc) } as Partial<SentenceTrace>);
  };
  const told: Array<{ name: string; age: number; verdict: VerdictClass }> = [];
  for (const l of D.luck) {
    const meta = b.luck[l.index - 1] ?? b.luck.find(x => x.name === l.pillar);
    if (!meta || meta.start_year == null || meta.start_age > 80) continue;
    const xs: ProseSentence[] = [];
    const [stem, branch] = l.stem && l.branch ? [l.stem, l.branch] : l.pillar.split(' ');
    const cur = meta.start_year <= yr && yr < meta.start_year + 10;
    const step = `luck:${l.index}`, rc = rcOf(l), who = { stem, branch };
    say(xs, fill(m.pick(`bd|lk${l.index}`, l.branch_god && l.stage ? F.luck_head : F.luck_head_short), { age: String(Math.round(meta.start_age)), from: String(meta.start_year), to: String(meta.start_year + 9), pillar: l.pillar,
      cur: cur ? fill(F.luck_now, { year: String(yr) }) : '', stem, branch, god: l.ten_god ?? '—', bgod: l.branch_god ?? '—', stage: l.stage ?? '' }),
    'tinh_toan', ['ZZ p.20', 'ZZ pp.24-25'], [], { step });
    cachSide(xs, l, `l${l.index}`, who);
    climateSide(xs, l, rc, `l${l.index}`, who, 'vận');
    const ev = events(l, `l${l.index}`, { stem, branch, who: 'cả trụ vận' });
    if (ev) say(xs, ev.text, 'tinh_toan', ev.cites, [], { step });
    for (const f of l.findings) if (F.verified_text[f.rule_id]) say(xs, fill(F.verified_text[f.rule_id], { stem, branch }), 'sach', ['TTT'], [cite(f.rule_id, f.text, ['TTT'])], { tone: 'neg', step });
    verdictOf(xs, l, rc, `l${l.index}`, who, { year: false, years: l.good_years ?? goodYearsTs(meta.start_year, dm, table, totG, xauG) });
    for (const s of xs) s.trace.step ??= step;
    if (meta.start_year <= yr + 60) {
      para('dai-van', xs);
      told.push({ name: l.pillar, age: meta.start_age, verdict: classOf(rc) });
    }
  }

  // ---- lưu niên: the requested year and the two after it, judged the same way ----
  for (const y of D.years ?? []) {
    const xs: ProseSentence[] = [], key = `y${y.year}`, step = `year:${y.year}`;
    const stem = y.stem ?? y.pillar.split(' ')[0], branch = y.branch ?? y.pillar.split(' ')[1], rc = rcOf(y), who = { stem, branch };
    say(xs, fill(m.pick(`bd|yh|${key}`, F.year_head), { year: String(y.year), pillar: y.pillar, luck: y.luck ?? '', stem, branch, god: y.ten_god, bgod: y.branch_god ?? '—', stage: y.stage ?? '' })
      .replace(/, đi trong đại vận ?:/, ':'), 'tinh_toan', ['ZZ p.20'], [], { step });
    cachSide(xs, y, key, who, y.year);
    climateSide(xs, y, rc, key, who, 'năm');
    const ev = events(y, key, { stem, branch, who: 'cả trụ năm', year: y.year });
    if (ev) say(xs, ev.text, 'tinh_toan', ev.cites, [], { step });
    const withLuck = (y.events ?? []).filter(e => e.targets[0] === 'luck' && F.year_luck[e.kind]).map(e => fill(F.year_luck[e.kind], { luck: y.luck ?? '' }));
    if (withLuck.length) say(xs, withLuck.join(' '), 'tinh_toan', ['TTT'], [], { step });
    let neg = false;
    for (const f of y.findings) if (F.verified_text[f.rule_id]) { neg ||= f.rule_id.endsWith('NHUOC'); say(xs, fill(F.verified_text[f.rule_id], { year: String(y.year), stem, branch }), 'sach', ['TTT'], [cite(f.rule_id, f.text, ['TTT'])], { tone: f.rule_id.endsWith('NHUOC') ? 'neg' : 'pos', step }); }
    // a year the thiên khắc địa xung rule calls a great ill is told so, with what to do, whatever the tables say
    verdictOf(xs, y, neg && rc.verdict !== 'nang' ? { ...rc, verdict: 'nang', support: [] } : rc, key, who, { year: true });
    para('luu-nien', xs);
  }

  // ---- tổng kết: along the timeline, by the very verdicts the đại vận paragraphs gave ----
  if (told.length && F.tk_open.length) {
    const xs: ProseSentence[] = [];
    say(xs, fill(m.pick('bd|tk', F.tk_open), { dm, level: levelVi, mb, need: needEl }).replace(/, lá số cần \./, '.').replace(/; hành cần bổ là \./, '.'), 'he_thong', [], [], { step: 'closing:bat_tu' });
    const cuts = [0, 30, 60, 200], ORDER: VerdictClass[] = ['thuan', 'kha_thuan', 'co_dieu_kien', 'tron', 'nang', 'trung'];
    F.tk_phase_name.forEach((ph, i) => {
      const xsP = told.filter(x => x.age >= cuts[i] - 0.5 && x.age < cuts[i + 1] - 0.5);
      if (!xsP.length) return;
      const parts = ORDER.map(v => [v, xsP.filter(x => x.verdict === v)] as const).filter(([, g]) => g.length)
        .map(([v, g]) => fill((g.length > 1 ? F.tk_class_many : F.tk_class)[v], { list: join(g.map(x => `${x.name} (từ ${Math.round(x.age)} tuổi)`)), yong: yongG.length ? `nhóm ${join(yongG)}` : 'chỗ dựa' }));
      const list = parts.length > 1 ? `${parts.slice(0, -1).join('; ')}; còn ${parts.at(-1)}` : parts[0];
      const tone = xsP.every(x => x.verdict === 'nang') ? 'neg' : xsP.every(x => x.verdict === 'thuan' || x.verdict === 'kha_thuan') ? 'pos' : undefined;
      say(xs, fill(m.pick(`bd|tkp${i}`, F.tk_phase), { phase: ph, list }), 'he_thong', [], [], { step: 'closing:bat_tu', tone, verdicts: xsP.map(x => [x.name, x.verdict]) } as Partial<SentenceTrace>);
    });
    const dhOk = table.filter(x => { const g = dh.stems.find(s => s.stem === x)?.ten_god; return !g || !xauG.includes(GROUP_OF[g]); });
    const good = [...totG.map(x => `nhóm ${x}`), ...(dhOk.length ? [`can ${join(dhOk)}`] : [])];
    if (F.tk_advice.length && good.length) say(xs, fill(m.pick('bd|tka', F.tk_advice), { good: join(good), bad: xauG.length ? join(xauG.map(x => `nhóm ${x}`)) : '' })
      .replace(/, và giữ sức ở những chặng mang \./, '.').replace(/, còn khi gặp  thì nên giữ\./, '.'), 'he_thong', [], [], { step: 'closing:bat_tu', tone: 'answer' });
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
/** bazi_deep.pipeline.reconcile, for facts from before it (same inputs, same table) */
/** the verdict as the reader is told it: a conditional verdict from a stem / branch split ('tron') is "tốt xấu đan xen", one from the two
 *  tables disagreeing is "tùy lúc có dụng thần đi kèm"; the đại vận paragraphs, the lưu niên and the closing all use this one class */
export type VerdictClass = Reconcile['verdict'] | 'tron';
export const classOf = (rc: Reconcile): VerdictClass => rc.verdict === 'co_dieu_kien' && rc.agree === 'tron' ? 'tron' : rc.verdict;
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
export function goodYearsTs(first: number, dm: string, table: string[], totG: string[], xauG: string[]): NonNullable<BaziTemporal['good_years']> {
  const out: NonNullable<BaziTemporal['good_years']> = [];
  for (let y = first; y < first + 10; y++) {
    const s = STEMS_VI[(((y - 4) % 10) + 10) % 10], br = BRANCHES_VI[(((y - 4) % 12) + 12) % 12], g = groupOf(dm, s);
    const why = [...(totG.includes(g) ? ['cach'] : []), ...(table.includes(s) && !xauG.includes(g) ? ['dieu_hau'] : [])];
    if (why.length) out.push({ year: y, pillar: `${s} ${br}`, group: g, why });
  }
  return out;
}
