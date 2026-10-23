// Bát Tự: tiền bạc, nghề, quan hệ and the years by the 八字真宗 direct judgements (DEEP-BAZI-2, 2026-10-23). The facts and the fired rules come
// from engine/tvbt/bazi_deep/kin.py (facts.bazi.deep.kin, and per year deep.years[].kin); the rules are data/bazi_deep/pack_zz_kin.json with the
// printed words in quotes_zz_kin.json. Basis per sentence:
//   - sach: a fired rule (BT_ZZK_*), its chart condition named with the characters of this chart, its effect as the manual words it;
//   - tinh_toan: a position the manual defines and the chart has (where Tài, Quan, Ấn stand; the spouse, parent, sibling, child stars of
//     pp.55, 57, 60, 63; the three places next to the day master, p.50; the pillar left of the Quan pillar, p.52; thai nguyên / mệnh / thân cung).
// The manual's own conditions decide between its judgements: on Tài, p.50 断语条件 1-3 ("财星旺，但未流入日，则财运平常") cap every positional
// "tài vận tốt" when Tài is strong and does not reach the day master; on work, p.51 #3-5 by the same 流入日主. Nothing here names a book or a page
// in the text: the page is in each sentence's note.
import type { ChartInput } from '../types.ts';
import { Micro, finish, lowerFirst } from './micro.ts';
import type { ProseParagraph, ProseSentence, SentenceTrace } from './realize.ts';

export interface KinFinding { rule_id: string; topic: string; tone: 'pos' | 'neg' | 'neutral'; effect: string; cause: string; page: string; note?: string }
export interface KinDetail {
  tmm: Array<{ key: 'thai' | 'menh' | 'than'; stem: string; branch: string; god_stem: string; god_branch: string }>;
  tai_flow: string[]; quan_flow: string[]; near_dm: Array<{ at: string; god: string }>; quan_trans: string[];
  work: { from: string | null; from_name: string; basis: string; left: string | null; left_name: string; stem_god: string | null; candidates: string[] };
  tai: { trans: string[]; hidden: string[]; share: number | null };
  parents: { father: string | null; father_at: string[]; mother: string | null; mother_at: string[] };
  tai_an_war: string[]; triple: string[];
  spouse: { group: string | null; at: string[]; hidden_only: boolean };
  siblings: { star: string | null; at: string[] };
  children: { stars: string[]; at: string[]; hour: boolean };
  layout: Record<'year' | 'month' | 'day' | 'hour', { stem: string | null; branch: string }>;
  day_combine: Array<{ pillar: string; stem: string; god: string }>;
  share: Record<string, number | null>; vuong: string[]; nhuoc: string[]; absent: string[];
}
export interface BaziKin { detail: KinDetail; findings: KinFinding[] }
export interface KinYear { gods: string[]; fill_void: boolean; natal_void_gods: string[]; findings: KinFinding[] }
export interface KinFrames {
  rule: string[]; rule_next: string[]; lead: Record<string, string[]>;
  tai_flat: string[]; tai_flow: string[]; tai_flow_tmm: string[]; dm_wait: string[]; why_noflow: string[]; why_noflow_an: string[]; why_flow: string[]; capped: string[]; capped_dm: string[];
  layout: string[]; work_field: string[]; work_field_day: string[]; work_place: string[]; work_none: string[];
  spouse: string[]; spouse_none: string[]; day_combine: string[]; parents: string[]; siblings: string[]; siblings_an: string[]; children: string[]; children_hour: string[];
  tmm: string[];
  year_link: string[]; year_link_none: string[]; year_rule: string[]; year_rule_good: string[]; year_void: string[];
  domain: Record<string, string>;
}

const join = (xs: string[]) => xs.length < 2 ? (xs[0] ?? '') : `${xs.slice(0, -1).join(', ')} và ${xs.at(-1)}`;
const fill = (t: string, v: Record<string, string>) => t.replace(/\{([A-Za-z0-9_]+)\}/g, (m, k) => v[k] ?? m);
const cap = (s: string) => s.charAt(0).toLocaleUpperCase('vi') + s.slice(1);
const PIL_VI: Record<string, string> = { year: 'năm', month: 'tháng', day: 'ngày', hour: 'giờ' };
const GROUP: Record<string, string> = { 'Tỉ Kiên': 'Tỉ Kiếp', 'Kiếp Tài': 'Tỉ Kiếp', 'Thực Thần': 'Thực Thương', 'Thương Quan': 'Thực Thương', 'Chính Tài': 'Tài', 'Thiên Tài': 'Tài',
  'Chính Quan': 'Quan Sát', 'Thất Sát': 'Quan Sát', 'Chính Ấn': 'Ấn', 'Thiên Ấn': 'Ấn' };
const TEN = new Set(Object.keys(GROUP).concat(Object.values(GROUP), ['Quan']));
/** lower the first letter unless the text opens with a ten god's name (they keep their capitals inside a sentence) */
const low = (t: string) => [...TEN].some(g => t.startsWith(g)) ? t : lowerFirst(t);
const ZZ = (page: string) => `ZZ ${page}`;
const FLOW_NOTE = 'Bát Tự Chân Tông tr.50, điều kiện cuối bảng tài vận: "Tài sinh Quan, Quan sinh Ấn, Ấn đứng ở chi ngày, can tháng hoặc can giờ" mới là "chảy vào nhật chủ"; '
  + 'hai chữ "đứng sát" là cùng một trụ (can với chi) hoặc cùng hàng ở hai trụ liền nhau (ví dụ 2 tr.58: can không sinh chi của trụ khác).';
const SHARE_NOTE = 'Tài "vượng": phần độ của nhóm Tài trên tổng độ (phép chấm Thiệu Vĩ Hoa tr.331-355) từ 25% — ngưỡng của hệ thống, sách không cho thước đo.';
const DOM_SHORT: Record<string, string> = { 'Tài': 'tiền bạc', 'Quan Sát': 'công việc', 'Ấn': 'học hành', 'Tỉ Kiếp': 'anh chị em' };
const WAR = new Set(['BT_ZZK_W24', 'BT_ZZK_W25', 'BT_ZZK_W26']);
const WORK_VERDICT = /^BT_ZZK_O0[345][AB]$/;

export interface KinContext { gender: string | null; dm: string; strong: boolean | null; taiDm?: boolean }

/** the natal part: su-nghiep (Tài, the work, the rank) and quan-he (spouse, marriage, parents, siblings, children) */
export function kinBazi(chart: ChartInput, m: Micro, F: KinFrames | undefined, rules: Record<string, { reading: string; cites: string[]; verified: boolean }>,
  ctx: KinContext): { 'su-nghiep': ProseParagraph[]; 'quan-he': ProseParagraph[] } {
  const out = { 'su-nghiep': [] as ProseParagraph[], 'quan-he': [] as ProseParagraph[] };
  const K = (chart.bazi as { deep?: { kin?: BaziKin } } | undefined)?.deep?.kin;
  if (!F || !K) return out;
  const D = K.detail, fs = K.findings, by = new Map(fs.map(f => [f.rule_id, f]));
  const say = (xs: ProseSentence[], text: string, basis: SentenceTrace['basis'], cites: string[], ids: string[], extra: Partial<SentenceTrace> = {}) => {
    const t = finish(text); m.said(t); xs.push({ text: t, trace: { move: 'ELABORATE', concepts: [], rules: ids, cites, basis, ...extra } });
  };
  const reg = (f: KinFinding) => { rules[f.rule_id] = { reading: `${f.effect} (${f.cause})`, cites: [ZZ(f.page)], verified: true }; return f.rule_id; };
  const tone = (f: KinFinding): Partial<SentenceTrace> => f.tone === 'pos' ? { tone: 'pos' } : f.tone === 'neg' ? { tone: 'neg' } : {};
  /** one fired rule as a sentence: its condition (with this chart's characters where given), then its effect */
  const rule = (xs: ProseSentence[], f: KinFinding, key: string, i: number, cause = f.cause, extra: Partial<SentenceTrace> = {}) =>
    say(xs, fill(m.pick(`kin|${key}|${i ? 'n' : 'f'}`, i ? F.rule_next : F.rule), { Cause: cap(cause), cause: low(cause), effect: low(f.effect) }), 'sach', [ZZ(f.page)], [reg(f)],
      { ...tone(f), step: `kin:${f.rule_id}`, ...(f.note ? { note: f.note } : {}), ...extra });
  const P = (id: 'su-nghiep' | 'quan-he', xs: ProseSentence[], extra: Partial<ProseParagraph> = {}) => {
    if (xs.length) out[id].push({ role: 'support', sentences: xs, text: xs.map(s => s.text).join(' '), ...extra });
  };
  const deep = (title: string): Partial<ProseParagraph> => ({ depth: 'sau', depthTitle: title });
  const lead = (key: string, xs: ProseSentence[]) => {
    const l = F.lead[key]?.length ? m.pick(`kin|lead|${key}`, F.lead[key]) : '';
    if (l && xs.length) xs[0] = { ...xs[0], text: `${l}, ${low(xs[0].text)}` };
    return l;
  };
  const pct = D.share['Tài'] != null ? String(Math.round(D.share['Tài']! * 100)) : '';

  // ---------------- tiền bạc: the manual's own condition first, then each character
  const head: ProseSentence[] = [], tdeep: ProseSentence[] = [];
  const w = [...WAR].map(id => by.get(id)).find(Boolean);
  if (w) {
    const key = w.rule_id === 'BT_ZZK_W24' ? 'tai_flat' : w.rule_id === 'BT_ZZK_W25' ? 'tai_flow' : 'tai_flow_tmm';
    const tmmHit = D.tmm.map(t => `${t.key === 'thai' ? 'thai nguyên' : t.key === 'menh' ? 'mệnh cung' : 'thân cung'} ${t.stem} ${t.branch}`);
    // the weak day master with Tài a bad luck (the Tài layers below): even the flowing "tài vận tốt" waits on the day master's strength
    const dmWait = key === 'tai_flow' && ctx.taiDm;
    const t0 = fill(m.pick(`kin|${key}`, F[key]), { pct, chain: join(D.tai_flow), tmm: join(tmmHit) });
    say(head, dmWait ? `${t0.replace(/\.$/, '')}${F.dm_wait[0] ?? ''}` : t0, 'sach', [ZZ(w.page)], [reg(w)],
      { step: 'kin:tai', tone: w.tone === 'pos' ? 'pos' : undefined, mech: true, note: `${FLOW_NOTE} ${SHARE_NOTE}`, ...(dmWait ? { conditional: 'tai_position_only' } : {}) });
  }
  // why it does (not) flow: the three places next to the day master (computed)
  if (w || by.has('BT_ZZK_O03B') || by.has('BT_ZZK_O04B') || by.has('BT_ZZK_O05B') || by.has('BT_ZZK_R05')) {
    const near = D.near_dm.map(x => `${x.at} (${x.god})`);
    const an = D.near_dm.filter(x => GROUP[x.god] === 'Ấn');
    if (D.tai_flow.length || D.quan_flow.length) say(tdeep, fill(m.pick('kin|whyf', F.why_flow), { chain: join(D.tai_flow.length ? D.tai_flow : D.quan_flow) }), 'tinh_toan', ['ZZ p.50'], [], { step: 'kin:flow', mech: true, note: FLOW_NOTE });
    else say(tdeep, fill(m.pick(an.length ? 'kin|whyna' : 'kin|whyn', an.length ? F.why_noflow_an : F.why_noflow), { near: join(near), an: join(an.map(x => x.at)) }), 'tinh_toan', ['ZZ p.50'], [],
      { step: 'kin:flow', mech: true, note: FLOW_NOTE });
  }
  // each Tài judgement by position; a "tài vận tốt" is capped by the manual's own condition when Tài is strong and does not flow
  const capped = by.has('BT_ZZK_W24') || by.has('BT_ZZK_W26');
  fs.filter(f => f.topic === 'wealth' && !WAR.has(f.rule_id)).forEach((f, i) => {
    const where = '';
    if (capped && f.tone === 'pos' && w) {
      say(tdeep, fill(m.pick(`kin|cap|${i}`, F.capped), { Cause: cap(f.cause + where), effect: low(f.effect) }), 'sach', [ZZ(f.page), ZZ(w.page)], [reg(f), w.rule_id],
        { step: `kin:${f.rule_id}`, conditional: 'tai_flow', note: `${f.note ? f.note + ' ' : ''}${FLOW_NOTE}` });
    } else if (ctx.taiDm && f.tone === 'pos' && !w) {
      // the weak day master with Tài a bad luck (the Tài layers below): a positional "tài vận tốt" waits on the day master's strength
      say(tdeep, fill(m.pick(`kin|capdm|${i}`, F.capped_dm), { Cause: cap(f.cause + where), effect: low(f.effect) }), 'sach', [ZZ(f.page)], [reg(f)],
        { step: `kin:${f.rule_id}`, conditional: 'tai_position_only', note: `${f.note ? f.note + ' ' : ''}Bát Tự Chân Tông tr.50: lời về tài vận xét vị trí của Tài, không xét sức nhật chủ.` });
    } else rule(tdeep, f, 'w', i, f.cause + where);
  });
  // ---------------- công việc: the verdict by 流入日主, the field and the size by the pillar left of the Quan pillar
  const work: ProseSentence[] = [], wdeep: ProseSentence[] = [];
  const wv = fs.find(f => WORK_VERDICT.test(f.rule_id));
  if (wv) rule(work, wv, 'wv', 0, wv.cause, { mech: true, note: `${wv.note ? wv.note + ' ' : ''}${FLOW_NOTE}` });
  const og = fs.find(f => f.rule_id.startsWith('BT_ZZK_OG_')), os = fs.find(f => f.rule_id.startsWith('BT_ZZK_OS_')), op = fs.find(f => /^BT_ZZK_O06[AB]$/.test(f.rule_id));
  const Wk = D.work;
  if ((og || os) && Wk.left) {
    const basis = Wk.basis === 'tai' ? 'Tài (lá số không có Quan Sát)' : 'Quan';
    const vars = { basis, from: `trụ ${PIL_VI[Wk.from!]} ${Wk.from_name}`, left: `trụ ${PIL_VI[Wk.left]} ${Wk.left_name}`, stem: Wk.left_name.split(' ')[0], god: Wk.stem_god ?? '',
      field: og ? low(og.effect.replace(/^nghề hợp thiên về /, '')) : '', list: os ? os.effect.replace(/^nghề có thể thuộc nhóm /, '') : '' };
    const ids = [og, os].filter(Boolean).map(f => reg(f!));
    say(work, fill(m.pick('kin|field', Wk.left === 'day' || !og ? F.work_field_day : F.work_field), vars).replace(/, cụ thể có thể là \./, '.'), 'sach', ['ZZ p.52', 'ZZ p.53'], ids,
      { step: 'kin:work_field', mech: true, note: (og ?? os)!.note });
  } else if (Wk.candidates.length > 1 && F.work_none.length) {
    say(wdeep, fill(m.pick('kin|wnone', F.work_none), { list: join(Wk.candidates.map(p => `trụ ${PIL_VI[p]}`)) }), 'tinh_toan', ['ZZ p.52'], [],
      { step: 'kin:work_none', note: 'Bát Tự Chân Tông tr.52 mục 6-7 đọc nghề theo trụ bên trái trụ có Quan; khi Quan ở nhiều trụ mà không có một Quan thấu can duy nhất, không xác định được trụ ấy.' });
  }
  if (op && Wk.left) say(wdeep, fill(m.pick('kin|place', F.work_place), { left: `trụ ${PIL_VI[Wk.left]} ${Wk.left_name}`, stem: Wk.left_name.split(' ')[0], effect: low(op.effect),
    sits: op.rule_id.endsWith('A') ? 'ngồi trên gốc của nó' : 'không có gốc ngay dưới' }), 'sach', [ZZ(op.page)], [reg(op)], { ...tone(op), step: `kin:${op.rule_id}`, note: op.note });
  fs.filter(f => f.topic === 'rank').forEach((f, i) => rule(i ? wdeep : work, f, 'rank', i ? 1 : 0, f.cause, { step: `kin:${f.rule_id}` }));
  // ---------------- the layout of the ten-god groups by pillar (computed; owner plan P2): Tài, Quan Sát, Ấn, Thực Thương, Tỉ Kiếp
  const where: Record<string, string[]> = {};
  for (const p of ['year', 'month', 'day', 'hour'] as const) {
    const L = D.layout[p];
    if (L.stem) (where[GROUP[L.stem]] ??= []).push(`can ${PIL_VI[p]}`);
    (where[GROUP[L.branch]] ??= []).push(`chi ${PIL_VI[p]}`);
  }
  const lay = ['Tài', 'Quan Sát', 'Ấn', 'Thực Thương', 'Tỉ Kiếp'].filter(g => where[g]).map(g => `${g} ở ${join(where[g])}`);
  const none = ['Tài', 'Quan Sát', 'Ấn', 'Thực Thương'].filter(g => !where[g]);
  const layout: ProseSentence[] = [];
  if (lay.length) say(layout, fill(m.pick('kin|layout', F.layout), { list: join(lay), none: none.length ? `; ${join(none)} chỉ ẩn trong tàng can hoặc không có` : '' }), 'tinh_toan', ['ZZ p.17'], [],
    { step: 'kin:layout', note: 'Thập thần của từng can và chính khí từng chi so với nhật chủ (Bát Tự Chân Tông tr.17); chi tính theo chính khí.' });

  const sn = [...layout, ...head, ...work];
  const lw = lead('work', sn);
  P('su-nghiep', sn, { lead: lw || undefined, topic: 'kin_work' });
  P('su-nghiep', tdeep, deep('tiền bạc, từng chữ Tài'));
  P('su-nghiep', wdeep, deep('nghề và chức vụ'));

  // ---------------- quan hệ: the spouse star by sex, marriage, parents, siblings, children
  const qh: ProseSentence[] = [], qdeep: ProseSentence[] = [], kdeep: ProseSentence[] = [];
  const sp = D.spouse;
  if (sp.group && F.spouse.length) {
    const who = ctx.gender === 'nam' ? 'vợ' : 'chồng';
    say(qh, fill(m.pick('kin|sp', sp.at.length ? F.spouse : F.spouse_none), { gender: ctx.gender ?? '', who, group: sp.group, at: join(sp.at) }), 'tinh_toan', ['ZZ p.57'], [],
      { step: 'kin:spouse', note: 'Bát Tự Chân Tông tr.57: sao phu thê của nam là Tài, của nữ là Quan; xét cung hôn nhân (chi tháng), cung phối ngẫu (chi ngày) trước, sao phu thê sau.' });
    const dc = D.day_combine.filter(x => GROUP[x.god] === sp.group);
    if (dc.length && F.day_combine.length) say(qh, fill(m.pick('kin|dc', F.day_combine), { list: join(dc.map(x => `can ${PIL_VI[x.pillar]} ${x.stem} (${x.god})`)), dm: ctx.dm, who }), 'tinh_toan',
      ['ZZ p.57', 'ZZ pp.19-20'], [], { step: 'kin:day_combine', note: 'Can hợp theo bảng ngũ hợp (Bát Tự Chân Tông tr.19-20). Các lời của tr.57 về sao phu thê tranh hợp nhật can nói chuyện ngoại tình: không đưa vào văn.' });
  }
  const mar = fs.filter(f => f.topic === 'marriage');
  mar.forEach((f, i) => rule(i < 2 ? qh : qdeep, f, 'm', i < 2 ? i : 1));
  const kin2: ProseSentence[] = [];
  const sib = D.siblings;
  if (sib.star && F.siblings.length) say(kin2, fill(m.pick('kin|sib', sib.star === 'Ấn' ? F.siblings_an : F.siblings), { at: join(sib.at) }), 'tinh_toan', ['ZZ p.63'], [],
    { step: 'kin:siblings', note: 'Bát Tự Chân Tông tr.63: anh chị em xét theo Tỉ Kiếp; không có Tỉ Kiếp thì lấy Ấn. Phép đếm số anh chị em của trang này không đưa vào văn.' });
  fs.filter(f => f.topic === 'siblings').forEach((f, i) => rule(i < 2 ? kin2 : kdeep, f, 's', i < 2 ? i : 1));
  const par = D.parents;
  if ((par.father || par.mother) && F.parents.length) say(kdeep, fill(m.pick('kin|par', F.parents), {
    father: par.father ? `${par.father}, ở ${join(par.father_at)}` : 'không có trong tứ trụ', mother: par.mother === 'Quan' ? `Quan Sát (vì không có Ấn), ở ${join(par.mother_at)}` : par.mother ? `${par.mother}, ở ${join(par.mother_at)}` : 'không có trong tứ trụ' }),
  'tinh_toan', ['ZZ p.54', 'ZZ p.55'], [], { step: 'kin:parents', note: 'Bát Tự Chân Tông tr.54-55: xét cha theo Thiên Tài (không có thì Thực Thần), mẹ theo Ấn (không có thì Quan). Các mục về tuổi thọ cha mẹ không đưa vào văn.' });
  fs.filter(f => f.topic === 'parents').forEach((f, i) => rule(kdeep, f, 'p', i));
  const ch = D.children;
  if (ch.stars.length && F.children.length) say(kdeep, fill(m.pick('kin|kid', F.children), { stars: join(ch.stars), at: ch.at.length ? `ở ${join(ch.at)}` : 'chỉ ẩn trong tàng can' }), 'tinh_toan', ['ZZ p.60'], [],
    { step: 'kin:children', note: 'Bát Tự Chân Tông tr.60: sao con cái theo giới tính và theo lá số có Tài (nam) hay có Thực Thương (nữ). Lời đoán con trai, con gái và các mục về sinh nở không đưa vào văn.' });
  else if (ch.hour && F.children_hour.length) say(kdeep, fill(m.pick('kin|kidh', F.children_hour), { hour: `${(chart.bazi as { pillars: { hour: { name: string } } }).pillars.hour.name}` }), 'tinh_toan', ['ZZ p.60'], [],
    { step: 'kin:children', note: 'Bát Tự Chân Tông tr.60: không có sao con cái thì xem can và chi trụ giờ.' });
  // thai nguyên, mệnh cung, thân cung are named inside the judgements that read them (W19, W26, M23, Y21)
  const lq = lead('marriage', qh);
  P('quan-he', qh, { lead: lq || undefined, topic: 'kin_marriage' });
  const lk = lead('family', kin2);
  P('quan-he', kin2, { lead: lk || undefined, topic: 'kin_family' });
  P('quan-he', qdeep, deep('hôn nhân'));
  P('quan-he', kdeep, deep('cha mẹ, anh em, con cái'));
  return out;
}

/** a year: its two ten gods told as what they stand for in the manual (Tài money and the man's spouse star, Quan work and the woman's, Ấn
 *  learning, Tỉ Kiếp siblings), and the pp.64-65 judgements that fire, each with its condition; a bad one in a year the reading calls good is said
 *  as one side of it */
export function kinYear(y: { year: number; kin?: KinYear }, m: Micro, F: KinFrames | undefined, rules: Record<string, { reading: string; cites: string[]; verified: boolean }>,
  ctx: KinContext & { good: boolean; stem: string; branch: string; childStars: string[]; years?: Array<{ year: number; kin?: KinYear }> }): { short: ProseSentence[]; deep: ProseSentence[] } {
  const res = { short: [] as ProseSentence[], deep: [] as ProseSentence[] };
  const Y = y.kin;
  if (!F || !Y) return res;
  const step = `year:${y.year}`;
  const say = (xs: ProseSentence[], text: string, basis: SentenceTrace['basis'], cites: string[], ids: string[], extra: Partial<SentenceTrace> = {}) => {
    const t = finish(text); m.said(t); xs.push({ text: t, trace: { move: 'ELABORATE', concepts: [], rules: ids, cites, basis, step, ...extra } });
  };
  const dom = (god: string): { text: string; cite: string } | null => {
    const g = GROUP[god];
    if (g === 'Tài') return { text: ctx.gender === 'nam' ? F.domain.tai_nam : F.domain.tai, cite: ctx.gender === 'nam' ? 'ZZ p.50, p.57' : 'ZZ p.50' };
    if (g === 'Quan Sát') return { text: ctx.gender === 'nữ' ? F.domain.quan_nu : F.domain.quan, cite: ctx.gender === 'nữ' ? 'ZZ pp.51-53, p.57' : 'ZZ pp.51-53' };
    if (g === 'Ấn') return { text: F.domain.an, cite: 'ZZ p.56' };
    if (g === 'Tỉ Kiếp') return { text: F.domain.ti, cite: 'ZZ p.63' };
    if (ctx.childStars.includes(god)) return { text: F.domain.con, cite: 'ZZ p.60' };
    return null;
  };
  const [sg, bg] = Y.gods;
  const ds = [...new Map([[GROUP[sg], sg], [GROUP[bg], bg]].map(([g, x]) => [g, x])).values()];
  const parts = ds.map(g => [g, dom(g)] as const).filter(([, d]) => d).map(([g, d]) => ({ text: `${d!.text === F.domain.con ? g : GROUP[g]} ứng với ${d!.text}`, cite: d!.cite }));
  if (parts.length) say(res.short, fill(m.pick(`kin|yl|${y.year}`, F.year_link), { year: String(y.year), sg, bg, list: join(parts.map(p => p.text)) }), 'tinh_toan',
    [...new Set(parts.flatMap(p => p.cite.split(', ').map(c => c.startsWith('ZZ') ? c : `ZZ ${c}`)))], [],
    { note: 'Nhóm thập thần ứng với việc gì theo Bát Tự Chân Tông: Tài với tiền bạc (tr.50), Quan với công việc, chức vụ (tr.51-53), Ấn với học hành (tr.56), Tỉ Kiếp với anh chị em (tr.63); sao phu thê nam là Tài, nữ là Quan (tr.57); sao con cái theo tr.60.' });
  else if (F.year_link_none.length) say(res.short, fill(m.pick(`kin|yl0|${y.year}`, F.year_link_none), { year: String(y.year), sg, bg }), 'tinh_toan', ['ZZ p.17'], []);
  const same = (f: KinFinding) => (ctx.years ?? []).filter(o => o.kin?.findings.some(g => g.rule_id === f.rule_id && g.cause === f.cause)).map(o => o.year);
  // Y31 and Y32 in one year (the same premise, the year brings both Tài and Thực Thương): one sentence
  const fs0 = Y.findings, y31 = fs0.find(f => f.rule_id === 'BT_ZZK_Y31'), y32 = fs0.find(f => f.rule_id === 'BT_ZZK_Y32');
  const merged = y31 && y32 ? { ...y31, cause: `${y31.cause} và ${y32.cause.replace(/^.*năm lại mang /, '')}`, also: 'BT_ZZK_Y32' } : null;
  const list: Array<KinFinding & { also?: string }> = merged ? [...fs0.filter(f => f !== y31 && f !== y32), merged] : fs0;
  list.forEach((f, i) => {
    const ys = same(f);
    if (ys.length && ys[0] < y.year) return;                 // said at the first year that has it
    const also = f.also;
    rules[f.rule_id] = { reading: `${f.effect} (${f.cause})`, cites: [ZZ(f.page)], verified: true };
    if (also && y32) rules[also] = { reading: `${y32.effect} (${y32.cause})`, cites: [ZZ(y32.page)], verified: true };
    let cause = f.cause, effect = f.effect;
    if (f.rule_id === 'BT_ZZK_Y14') { const d = DOM_SHORT[GROUP[bg]]; effect = d ? `chuyện ${d} dễ trắc trở` : effect; cause = `${cause}, mà chi ${ctx.branch} mang ${bg}`; }
    const yl = ys.length > 1 ? join(ys.map(String)) : String(y.year);
    const frame = ctx.good && f.tone === 'neg' && ys.length <= 1 ? F.year_rule_good : F.year_rule;
    say(res.deep, fill(m.pick(`kin|yr|${y.year}|${i}`, frame), { year: yl, Cause: cap(cause), cause: low(cause), effect: low(effect) }), 'sach', [ZZ(f.page)], also ? [f.rule_id, also] : [f.rule_id],
      { ...(f.tone === 'neg' ? { tone: 'neg' } : f.tone === 'pos' ? { tone: 'pos' } : {}), ...(f.note ? { note: f.note } : {}) });
  });
  return res;
}
