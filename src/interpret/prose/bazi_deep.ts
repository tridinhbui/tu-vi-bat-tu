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
}
export interface BaziDeep {
  strength: { dm_strong: boolean | null; own_share: number | null; threshold: number | null; season_state: string | null; tvh_totals?: Record<string, number> };
  climate: { label: string | null; han_noan: string | null };
  dieu_hau: { cell: string | null; need: string[]; avoid: string[]; satisfied: boolean | null; verified: boolean;
    stems: Array<{ stem: string; ten_god: string; rank: string; visible: boolean; hidden: boolean }> };
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
  season: string[]; season_state: Record<string, string>; strength_border: string[]; strength_side: string[]; climate: string[]; climate_presence: string[];
  need: string[]; luck_role: Record<string, string>; luck_branch_role: Record<string, string>; verified_text: Record<string, string>;
  // Track C
  frame2: string[]; frame2_no_need: string[]; season_name: Record<string, string>; stages: string[]; stage_turn: string[]; totals: string[];
  cach_first: string[]; tb_next: string[]; tb_turn: string[]; table: string[]; table_no_van: string[]; table_special: string[]; dh_turn: string[]; advice: string[];
  shensha: string[]; shensha_hung: string[]; shensha_plain: string[];
  luck_head: string[]; luck_head_short: string[]; luck_now: string; tvh_both: string[]; tvh_same: string[]; tvh_split: string[]; tvh_one: string[]; tvh_none: string[]; verdict: Record<string, string>;
  ev_open: string[]; ev_none: string[]; ev_kind: Record<string, string>; spouse_first: string; spouse_next: string; marriage: string;
  year_head: string[]; year_luck: Record<string, string>; year_advice: string[];
  tk_open: string[]; tk_phase: string[]; tk_phase_name: string[]; tk_verdict: Record<string, string>; tk_verdict_dh: Record<string, string>; tk_advice: string[];
  premise: Record<string, 'strong' | 'weak'>;
}
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
  const sh = D.strength.own_share, th = D.strength.threshold, border = fired.has('BT_TVH_BIEN');
  const strong = border ? null : D.strength.dm_strong;
  const levelVi = border ? 'ở sát ngưỡng vượng nhược' : strong == null ? 'ở mức cân bằng' : strong ? 'vượng' : 'nhược';
  const CT = D.cach_tvh, dh = D.dieu_hau;
  const tableOk = CT?.status === 'ap_dung' && !!CT.cach;
  const tvhPage = CT?.page ? `TVH pp.${CT.page.replace(/\s/g, '')}` : 'TVH pp.378-386';

  // ---- frame (second sentence): season, TVH verdict, điều hậu need ----
  const frame: ProseSentence[] = [];
  if (D.strength.season_state && sh != null && F.frame2) {
    const need = dh.verified && dh.need.length ? join(dh.need) : '';
    say(frame, fill(m.pick('bd|frame2', need ? F.frame2 : F.frame2_no_need), { mb, season: F.season_name[mb] ?? '', el, dm, state: F.season_state[D.strength.season_state]?.split(',')[0] ?? D.strength.season_state,
      need }), 'tinh_toan', ['ZZ (ngũ hành vượng tướng hưu tù tử)', ...(need ? ['TVH pp.389-396'] : [])], [], { step: 'frame:bat_tu:2' });
  }
  if (frame.length) para('nhat-chu', frame, 'structure');

  // ---- nhật chủ: season, strength by TVH's score, growth stages, the turn ----
  const st: ProseSentence[] = [];
  if (D.strength.season_state && !frame.length) say(st, fill(m.pick('bd|season', F.season), { dm, el, mb, state: F.season_state[D.strength.season_state] ?? D.strength.season_state }), 'tinh_toan', ['ZZ (ngũ hành vượng tướng hưu tù tử)']);
  if (sh != null && th != null) {
    const pct = String(Math.round(sh * 100)), thp = String(Math.round(th * 100));
    if (border) say(st, fill(m.pick('bd|border', F.strength_border), { pct, th: thp }), 'sach', ['TVH pp.331-355'], [cite('BT_TVH_BIEN', fired.get('BT_TVH_BIEN')!.text, ['TVH pp.331-355'])]);
    else {
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

  // ---- cách cục và dụng thần: the cách, TVH's thành bại sentences, his dụng thần table, điều hậu, the TTT rules, what to do ----
  const cc: ProseSentence[] = [];
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
    say(cc, fill(m.pick(`bd|tb${i}`, frames), { mb, cach: cachName ?? '', cond: lowerFirst(cond), verdict: lowerFirst(verdict) }), 'sach', ['TVH pp.367-369'],
      [cite(v.rule_id, v.text, ['TVH pp.367-369'])], { tone: xau ? 'neg' : 'pos' });
  });
  if (tableOk && CT!.yong.length) {
    const vars = { cach: CT!.cach!, dm: CT!.dm ?? levelVi, dom: CT!.dominant ?? '', yong: join(CT!.yong), tot: join(CT!.van_tot), xau: join(CT!.van_xau) };
    say(cc, fill(m.pick('bd|table', CT!.van_tot.length || CT!.van_xau.length ? F.table : F.table_no_van), vars), 'tinh_toan', [tvhPage]);
  } else if (CT?.special && F.table_special && (CT.special_tot.length || CT.special_xau.length)) {
    say(cc, fill(m.pick('bd|tsp', F.table_special), { name: CT.special.replace(/\s*\(TVH\)$/, ''), tot: join(CT.special_tot), xau: join(CT.special_xau) || 'không có hành nào' }), 'tinh_toan', ['TVH pp.385-386']);
  }
  if (dh.verified && dh.stems.length) {
    const main = dh.stems.filter(s => s.rank.startsWith('chính')).map(s => `${s.stem} (${s.ten_god})`), others = dh.stems.filter(s => !s.rank.startsWith('chính')).map(s => `${s.stem} (${s.ten_god})`);
    const mainTxt = join(main.length ? main : others.slice(0, 1));
    // the two tables of the same book name different useful gods: the điều hậu one comes as the turn
    const mainGroups = dh.stems.filter(s => s.rank.startsWith('chính')).map(s => s.ten_god);
    const differs = tableOk && CT!.yong.length && mainGroups.length && !mainGroups.some(g => CT!.yong.some(y => GROUP_OF[g] === y));
    if (differs && F.dh_turn) say(cc, fill(m.pick('bd|dhturn', F.dh_turn), { mb, dm, climate: D.climate.label ?? '', main: mainTxt, yong: join(CT!.yong) }), 'tinh_toan', ['TVH pp.389-396']);
    else say(cc, fill(m.pick('bd|cl', F.climate), { mb, dm, climate: D.climate.label ?? '', main: mainTxt, others: join(main.length ? others : others.slice(1)) || 'không có can nào khác' }),
      'tinh_toan', ['TVH pp.389-396']);
    const present = dh.stems.filter(s => s.visible || s.hidden).map(s => s.stem), absent = dh.stems.filter(s => !s.visible && !s.hidden).map(s => s.stem);
    if (present.length && absent.length) say(cc, fill(m.pick('bd|pr', F.climate_presence), { present: join(present), absent: join(absent) }), 'tinh_toan', ['TVH pp.389-396']);
    if (dh.need.length) say(cc, fill(m.pick('bd|need', F.need), { need: join(dh.need), avoid: join(dh.avoid) || 'không có hành nào cần tránh rõ' }), 'tinh_toan', ['TVH pp.389-396']);
  }
  // the Trích Thiên Tủy rules that fired, in the order hàn noãn, nguyên lưu, Quan Sát hỗn tạp, Thương Quan, tòng / hóa; a rule whose premise
  // names the day master's strength is said only when the TVH verdict agrees with it
  const TTT_ORDER = ['BT_TTT_HANNOAN', 'BT_TTT_NGUYENLUU', 'BT_TTT_HONTAP', 'BT_TTT_TQ', 'BT_TTT_TONG', 'BT_TTT_HOA', 'BT_TVH_CV', 'BT_TVH_TONG', 'BT_TVH_HOA'];
  for (const pre of TTT_ORDER) for (const [id, v] of fired) {
    if (!id.startsWith(pre) || !F.verified_text[id]) continue;
    const need = F.premise[id];
    if (need && (strong == null || (need === 'strong') !== strong)) continue;
    const src = id.startsWith('BT_TVH') ? 'TVH pp.369-376' : 'TTT';
    say(cc, F.verified_text[id], 'sach', [src], [cite(id, v.text, [src])], /_KY$|CO_BENH/.test(id) ? { tone: 'neg' } : {});
  }
  // what to do: the useful group by TVH's table and the element by the điều hậu table, the luck groups to lean on and to take with care
  if (cc.length && F.advice && (tableOk || dh.need.length)) {
    const lean = tableOk && CT!.yong.length ? `nhóm ${join(CT!.yong)}` : '', needTxt = dh.verified && dh.need.length ? `hành ${join(dh.need)}` : '';
    say(cc, fill(m.pick('bd|adv', F.advice), { lean: join([lean, needTxt].filter(Boolean)), tot: tableOk && CT!.van_tot.length ? join(CT!.van_tot) : '', xau: tableOk && CT!.van_xau.length ? join(CT!.van_xau) : '' })
      .replace(/; những chặng gặp  thuận hơn những chặng gặp /, '').replace(/ thuận hơn những chặng gặp \./, '.'), 'he_thong', [], [], { tone: 'answer' });
  }
  para('cach-cuc', cc);

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
  const events = (t: BaziTemporal, key: string, subject: { stem: string; branch: string; who: string }): { text: string; cites: string[] } | null => {
    if (!t.events) return null;                         // facts from before Track C carry no relations: nothing is claimed either way
    const ev = t.events.filter(e => e.targets.every(x => x in pil));
    if (!ev.length) return F.ev_none.length ? { text: m.pick(`bd|evn|${key}`, F.ev_none), cites: ['ZZ pp.19-20'] } : null;
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
    return { text: fill(m.pick(`bd|ev|${key}`, F.ev_open), { list: parts.length > 1 ? `${parts.slice(0, -1).join('; ')}; còn ${parts.at(-1)}` : parts[0] }).replace(/\.$/, '') + note, cites: ['ZZ pp.19-20', ...(note ? ['ZZ p.57'] : [])] };
  };
  /** the TVH table's verdict on the stem and the branch, and the điều hậu table's role, turned when they disagree */
  const roles = (xs: ProseSentence[], t: BaziTemporal & { dieu_hau: { stem: Role; branch: Role } }, key: string, who: { stem: string; branch: string }, year = false): boolean => {
    const v = t.tvh ?? { stem: null, branch: null };
    let tvhBad = false, tvhGood = false;
    if (tableOk || CT?.special) {
      const cach = CT!.special ? CT!.special.replace(/\s*\(TVH\)$/, '') : CT!.cach!;
      const vs = { cach, stem: who.stem, branch: who.branch, sg: t.stem_group ?? '', bg: t.branch_group ?? '', v: F.verdict[v.stem ?? ''] ?? '', v2: F.verdict[v.branch ?? ''] ?? '' };
      let text = '';
      if (v.stem && v.branch && v.stem === v.branch) text = m.pick(`bd|tb|${key}`, vs.sg === vs.bg ? F.tvh_same : F.tvh_both);
      else if (v.stem && v.branch) text = m.pick(`bd|ts|${key}`, F.tvh_split);
      else if (v.stem || v.branch) text = fill(m.pick(`bd|t1|${key}`, F.tvh_one), { Part: v.stem ? 'Can' : 'Chi', who: v.stem ? who.stem : who.branch, g: v.stem ? vs.sg : vs.bg, v: F.verdict[(v.stem ?? v.branch)!] });
      else text = m.pick(`bd|tn|${key}`, F.tvh_none);
      say(xs, fill(text, vs), 'tinh_toan', [CT!.special ? 'TVH pp.385-386' : tvhPage], [], { tone: (v.stem ?? v.branch) === 'xau' ? 'neg' : (v.stem ?? v.branch) === 'tot' ? 'pos' : undefined });
      tvhBad = v.stem === 'xau' || (!v.stem && v.branch === 'xau'); tvhGood = v.stem === 'tot' || (!v.stem && v.branch === 'tot');
    }
    const dr = t.dieu_hau.stem, br = t.dieu_hau.branch;
    const dGood = dr === 'yong' || dr === 'xi' || (!dr && (br === 'yong' || br === 'xi')), dBad = dr === 'ji' || (!dr && br === 'ji');
    const dText0 = dr && F.luck_role[dr] ? F.luck_role[dr] : br && F.luck_branch_role[br] ? F.luck_branch_role[br] : '';
    if (!dText0) return false;
    const dText = year ? dText0.replace(/vận này/g, 'năm này').replace(/cho vận\b/g, 'cho năm').replace(/cả vận/g, 'cả năm').replace(/nửa sau vận/g, 'nửa sau năm') : dText0;
    const turn = (tvhBad && dGood) || (tvhGood && dBad);
    const c = turn ? m.conn('contrast', `bd|turn|${key}`) || 'Tuy nhiên,' : '';
    say(xs, c ? `${c} ${lowerFirst(dText.replace(/^Can vận/, `xét điều hậu, can ${who.stem}`).replace(/^Chi vận/, `xét điều hậu, chi ${who.branch}`))}` : dText.replace(/^Can vận/, `Xét điều hậu, can ${who.stem}`).replace(/^Chi vận/, `Xét điều hậu, chi ${who.branch}`),
      'tinh_toan', ['TVH pp.389-396'], [], { tone: dBad ? 'neg' : 'pos' });
    return dGood;
  };
  const told: Array<{ name: string; age: number; verdict: Verdict; good: boolean; bad: boolean }> = [];
  for (const l of D.luck) {
    const meta = b.luck[l.index - 1] ?? b.luck.find(x => x.name === l.pillar);
    if (!meta || meta.start_year == null || meta.start_age > 80) continue;
    const xs: ProseSentence[] = [];
    const [stem, branch] = l.stem && l.branch ? [l.stem, l.branch] : l.pillar.split(' ');
    const cur = meta.start_year <= yr && yr < meta.start_year + 10;
    const step = `luck:${l.index}`;
    say(xs, fill(m.pick(`bd|lk${l.index}`, l.branch_god && l.stage ? F.luck_head : F.luck_head_short), { age: String(Math.round(meta.start_age)), from: String(meta.start_year), to: String(meta.start_year + 9), pillar: l.pillar,
      cur: cur ? fill(F.luck_now, { year: String(yr) }) : '', stem, branch, god: l.ten_god ?? '—', bgod: l.branch_god ?? '—', stage: l.stage ?? '' }),
    'tinh_toan', ['ZZ p.20', 'ZZ pp.24-25'], [], { step });
    roles(xs, l, `l${l.index}`, { stem, branch });
    const ev = events(l, `l${l.index}`, { stem, branch, who: 'cả trụ vận' });
    if (ev) say(xs, ev.text, 'tinh_toan', ev.cites, [], { step });
    for (const f of l.findings) if (F.verified_text[f.rule_id]) say(xs, F.verified_text[f.rule_id], 'sach', ['TTT'], [cite(f.rule_id, f.text, ['TTT'])], { tone: 'neg', step });
    for (const s of xs) s.trace.step ??= step;
    if (meta.start_year <= yr + 60) {
      para('dai-van', xs);
      const v = l.tvh?.stem ?? l.tvh?.branch ?? null;
      told.push({ name: `${l.pillar} (từ ${Math.round(meta.start_age)} tuổi)`, age: meta.start_age, verdict: v,
        good: v === 'tot' || (!v && ['yong', 'xi'].includes(l.dieu_hau.stem ?? '')), bad: v === 'xau' || (!v && l.dieu_hau.stem === 'ji') });
    }
  }

  // ---- lưu niên: the requested year and the two after it ----
  for (const y of D.years ?? []) {
    const xs: ProseSentence[] = [], key = `y${y.year}`, step = `year:${y.year}`;
    const stem = y.stem ?? y.pillar.split(' ')[0], branch = y.branch ?? y.pillar.split(' ')[1];
    say(xs, fill(m.pick(`bd|yh|${key}`, F.year_head), { year: String(y.year), pillar: y.pillar, luck: y.luck ?? '', stem, branch, god: y.ten_god, bgod: y.branch_god ?? '—', stage: y.stage ?? '' })
      .replace(/, đi trong đại vận ?:/, ':'), 'tinh_toan', ['ZZ p.20'], [], { step });
    const helped = roles(xs, y, key, { stem, branch }, true);
    const ev = events(y, key, { stem, branch, who: 'cả trụ năm' });
    if (ev) say(xs, ev.text, 'tinh_toan', ev.cites, [], { step });
    const withLuck = (y.events ?? []).filter(e => e.targets[0] === 'luck' && F.year_luck[e.kind]).map(e => fill(F.year_luck[e.kind], { luck: y.luck ?? '' }));
    if (withLuck.length) say(xs, withLuck.join(' '), 'tinh_toan', ['TTT'], [], { step });
    let neg = false;
    for (const f of y.findings) if (F.verified_text[f.rule_id]) { neg ||= f.rule_id.endsWith('NHUOC'); say(xs, F.verified_text[f.rule_id], 'sach', ['TTT'], [cite(f.rule_id, f.text, ['TTT'])], { tone: f.rule_id.endsWith('NHUOC') ? 'neg' : 'pos', step }); }
    const bad = y.tvh?.stem === 'xau' && y.tvh?.branch !== 'tot';
    if ((neg || (bad && !helped)) && F.year_advice.length) say(xs, m.pick(`bd|ya|${key}`, F.year_advice), 'he_thong', [], [], { tone: 'answer', step });
    para('luu-nien', xs);
  }

  // ---- tổng kết: along the timeline, by the TVH table (or the điều hậu table when the TVH one gives no row) ----
  if (told.length && F.tk_open.length) {
    const xs: ProseSentence[] = [];
    say(xs, fill(m.pick('bd|tk', F.tk_open), { dm, level: levelVi, mb, need: dh.verified && dh.need.length ? join(dh.need) : '' }).replace(/, lá số cần \./, '.').replace(/; hành cần bổ là \./, '.'), 'he_thong', [], [], { step: 'closing:bat_tu' });
    const cuts = [0, 30, 60, 200];
    F.tk_phase_name.forEach((ph, i) => {
      const xsP = told.filter(x => x.age >= cuts[i] - 0.5 && x.age < cuts[i + 1] - 0.5);
      if (!xsP.length) return;
      const g = xsP.filter(x => x.good).length, bd = xsP.filter(x => x.bad).length;
      const v = g && !bd ? 'tot' : bd && !g ? 'xau' : g || bd ? 'mix' : 'none';
      say(xs, fill(m.pick(`bd|tkp${i}`, F.tk_phase), { phase: ph, list: join(xsP.map(x => x.name)), verdict: (tableOk || CT?.special ? F.tk_verdict : F.tk_verdict_dh)[v] }), 'he_thong', [], [], { step: 'closing:bat_tu', tone: v === 'xau' ? 'neg' : v === 'tot' ? 'pos' : undefined });
    });
    const good = tableOk ? CT!.van_tot : [], badG = tableOk ? CT!.van_xau : [];
    if (F.tk_advice.length && (good.length || dh.need.length)) say(xs, fill(m.pick('bd|tka', F.tk_advice), { good: join(good.length ? good.map(x => `nhóm ${x}`) : dh.need.map(x => `hành ${x}`)),
      bad: badG.length ? join(badG.map(x => `nhóm ${x}`)) : dh.avoid.length ? join(dh.avoid.map(x => `hành ${x}`)) : '' }).replace(/, và giữ sức ở những chặng mang \./, '.'), 'he_thong', [], [], { step: 'closing:bat_tu', tone: 'answer' });
    para('tong-ket', xs, 'course');
  }
  return out;
}

const GROUP_OF: Record<string, string> = { 'Tỉ Kiên': 'Tỉ Kiếp', 'Kiếp Tài': 'Tỉ Kiếp', 'Thực Thần': 'Thực Thương', 'Thương Quan': 'Thực Thương', 'Chính Tài': 'Tài', 'Thiên Tài': 'Tài',
  'Chính Quan': 'Quan Sát', 'Thất Sát': 'Quan Sát', 'Chính Ấn': 'Ấn', 'Thiên Ấn': 'Ấn' };
