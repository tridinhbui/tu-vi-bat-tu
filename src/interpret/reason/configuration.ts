// Configurations (plan docs/plans/THIEN-BAN-33-REVIEW-PLAN.md G9, owner review 2026-11-07: "luận tổ hợp thay vì luận từng sao"). The unit of
// reading is no longer one rule but one palace's whole structure: its core (own or borrowed chính tinh), the members that stand with it
// (in the palace, xung chiếu, tam hợp, giáp), each with a ROLE, and the relations between them (Hóa carried, chế hóa from kg/che_hoa.json,
// borrowing). The roles act in a fixed order, each step a trace line; nothing is decided by counting stars or edges.
//   nen        the core: the palace's chính tinh (a vô chính diệu palace borrows the opposite palace's, KL pp.218/222, TT p.18)
//   bien_tinh  changes the character of the whole: a Hóa Lộc / Quyền / Khoa carried by a member (KL pp.195-197 meanings), Hóa Kỵ on a member
//   tro_luc    adds strength: cát tinh (Tả Hữu, Xương Khúc, Khôi Việt), Lộc Tồn, a bright chính tinh of the tam phương
//   tru        lessens, on the facet the book names: a sát tinh not bright, a hãm chính tinh of the tam phương, Hóa Kỵ in the tam phương
//   pha        breaks the whole: only where a book says so (a page-checked cách evaluated bị phá)
// Tuần / Triệt on the palace act on both sides (KL p.203: "giảm cái tốt cũng như giảm cái xấu"). The roles and the order are a system
// convention (he_thong); every member, relation and answer carries its evidence id (fact, rule, chế hóa relation, page).
import type { ChartInput, Knowledge, Palace } from '../types.ts';
import type { Resolved } from '../kg/resolve.ts';
import { palaceEvidence, tamPhuongOf, type PalaceEvidence, type Where } from './evidence.ts';
import { cheHoaUnits, natureOf } from './depth.ts';
import { evaluateFormations } from './structures.ts';

export const CONFIG_VERSION = 'config-0.1.0';
/** the matter each palace's star natures speak of (star_nature.json `use`) */
const USE: Record<string, string> = { 'Quan Lộc': 'career', 'Tài Bạch': 'money', 'Điền Trạch': 'property', 'Phu Thê': 'marriage', 'Thiên Di': 'travel', 'Phúc Đức': 'fortune', 'Tật Ách': 'health', 'Mệnh': 'self', 'Nô Bộc': 'allies', 'Tử Tức': 'children', 'Huynh Đệ': 'siblings', 'Phụ Mẫu': 'parents' };
export type MemberRole = 'nen' | 'bien_tinh' | 'tro_luc' | 'tru' | 'pha';
export type ConfigState = 'thanh' | 'co_dieu_kien' | 'bi_pha' | 'duoc_cuu' | 'chua_du';
/** levels of a reading (plan G9.4): 1 one star, 2 the palace's own stars, 3 tam phương and Tứ Hóa, 4 cách cục, 5 Mệnh–Tài–Quan–Phúc–Di, 6 periods */
export type Level = 1 | 2 | 3 | 4 | 5 | 6;
export interface Member { id: string; name: string; palace: string; where: Where | 'giap'; role: MemberRole; dignity?: string; hoa?: string; borrowed?: boolean;
  /** what the member does to the whole, in the system's words (he_thong) or the book's (with cite) */
  does: string; cite?: string; level: Level }
export interface Relation { kind: 'muon' | 'hoa' | 'che' | 'xung' | 'tam_hop' | 'giap' | 'dong_cung'; from: string; to: string; note: string; cite?: string }
export interface Step { role: MemberRole | 'tuan_triet' | 'state'; note: string; strength: number; members: string[] }
export interface Answer { q: string; a: string; evidence: string[]; known: boolean }
export interface Activation { age_from: number; age_to: number; palace: string; what: string; members: string[] }
export interface Configuration {
  id: string; palace: string; branch: string; version: string; level: Level;
  core: Member[]; members: Member[]; relations: Relation[];
  /** fired verified readings of the palace (the book's words on this configuration or a part of it) */
  rules: Array<{ ruleId: string; concept: string; pol: string; cites: string[]; stars: string[] }>;
  state: ConfigState;
  /** 0 … 4 after the ordered steps (a system convention: 1 nhẹ, 2 vừa, 3 rõ, 4 mạnh); `steps` says why */
  strength: number; steps: Step[];
  questions: Answer[]; activation: Activation[];
  basis: 'he_thong';
}

const BRIGHT = new Set(['miếu', 'vượng', 'đắc']);
const SATS = new Set(['Kình Dương', 'Đà La', 'Hỏa Tinh', 'Linh Tinh', 'Địa Không', 'Địa Kiếp']);
const HOA_SHORT: Record<string, string> = { 'Hóa Lộc': 'Lộc', 'Hóa Quyền': 'Quyền', 'Hóa Khoa': 'Khoa', 'Hóa Kỵ': 'Kỵ' };
const joinVi = (xs: string[]) => xs.length <= 1 ? xs.join('') : `${xs.slice(0, -1).join(', ')} và ${xs.at(-1)}`;
const STRENGTH = ['rất nhẹ', 'nhẹ', 'vừa', 'rõ', 'mạnh'];
export const strengthWord = (n: number) => STRENGTH[Math.max(0, Math.min(4, Math.round(n)))];

/** The configuration of one palace. `resolved` is the report's resolution (fired verified readings, after the position guards). */
export function configurationOf(chart: ChartInput, k: Knowledge, P: string, resolved: Resolved[] = []): Configuration {
  const e: PalaceEvidence = palaceEvidence(chart, k, P, { resolved });
  const pal = chart.palaces.find(p => p.name === P)!;
  const tp = tamPhuongOf(chart, P);
  const opp = tp.find(x => x.where === 'opp')!.p;
  const meaning = (k.reference as { tuHoa?: { meaning?: Record<string, string>; cite?: string } } | undefined)?.tuHoa;
  const hoaCite = meaning?.cite ?? 'KL pp.195-197';
  const members: Member[] = [], relations: Relation[] = [], steps: Step[] = [];
  const id = (kind: string, name: string, palace: string) => `${kind}:${name}@${palace}`;
  const add = (m: Member) => { if (!members.some(x => x.id === m.id)) members.push(m); return m; };

  // 1. nen: the core chính tinh, own or borrowed
  const core = e.majors.map(m => add({ id: id('star', m.star, m.palace), name: m.star, palace: m.palace, where: m.borrowed ? 'opp' : 'self', role: 'nen', dignity: m.dignity, borrowed: m.borrowed,
    ...(m.hoa[0] ? { hoa: m.hoa[0] } : {}), level: 2,
    does: m.borrowed ? `cung ${P} vô chính diệu nên mượn ${m.star} từ cung ${m.palace} làm sao chủ` : `${m.star} là sao chủ của cung` }));
  for (const m of core.filter(x => x.borrowed)) relations.push({ kind: 'muon', from: m.id, to: `palace:${P}`, note: `${P} mượn ${m.name} của ${m.palace}`, cite: 'KL pp.218, 222' });
  let strength = 0;
  if (!core.length) steps.push({ role: 'nen', note: `cung ${P} và cung đối đều vô chính diệu: không có sao chủ`, strength, members: [] });
  else {
    const bright = core.filter(m => m.dignity && BRIGHT.has(m.dignity)), ham = core.filter(m => m.dignity === 'hãm');
    strength = bright.length ? 2 : ham.length ? 1 : 1.5;
    if (core.some(m => m.borrowed)) strength -= 0.5;
    steps.push({ role: 'nen', strength, members: core.map(m => m.id),
      note: `${joinVi(core.map(m => `${m.name}${m.dignity ? ` (${m.dignity})` : ''}`))}${core.some(m => m.borrowed) ? ' mượn từ cung đối, bớt nửa bậc' : ''}` });
  }

  // 2. bien_tinh: Tứ Hóa on a member of the palace or its tam phương (the birth-year Hóa)
  const bt: Member[] = [];
  for (const h of e.hoa) {
    const good = h.hoa !== 'Hóa Kỵ';
    const m = add({ id: id('hoa', `${h.star} ${h.hoa}`, h.palace), name: `${h.star} hóa ${HOA_SHORT[h.hoa]}`, palace: h.palace, where: h.where, role: good ? 'bien_tinh' : 'tru', hoa: h.hoa,
      ...(h.starDignity ? { dignity: h.starDignity } : {}), level: 3, cite: hoaCite,
      does: good ? `${HOA_SHORT[h.hoa]} là ${(meaning?.meaning?.[h.hoa] ?? '').replace(/\s*\(.*\)$/, '') || h.hoa}` : `Hóa Kỵ ${h.where === 'self' ? 'ngay trong cung' : `từ cung ${h.palace}`} làm vướng phần nó chạm tới` });
    relations.push({ kind: 'hoa', from: m.id, to: id('star', h.star, h.palace), note: `${h.hoa} đóng trên ${h.star}`, cite: hoaCite });
    if (good) bt.push(m);
  }
  if (bt.length) {
    // a good Hóa on the core or standing in the palace itself changes the whole by a step; from the tam phương, by half a step
    // a good Hóa on a hãm star only lifts part of its fall (evidence.ts role 'mixed'): a quarter step
    const d = bt.reduce((a, m) => a + (m.dignity === 'hãm' ? 0.25 : m.where === 'self' || core.some(c => m.name.startsWith(c.name)) ? 1 : 0.5), 0);
    strength += Math.min(1.5, d);
    steps.push({ role: 'bien_tinh', strength, members: bt.map(m => m.id), note: `${joinVi(bt.map(m => `${m.name} ở ${m.palace}`))} đổi tính chất tổ hợp (trong cung hay trên sao chủ một bậc, từ tam phương nửa bậc, trên sao hãm một phần tư; tối đa một bậc rưỡi)` });
  }

  // 3. tro_luc: cát tinh, Lộc Tồn, bright chính tinh of the tam phương
  const tl: Member[] = [];
  // a cát tinh carrying a good Hóa is already counted as bien_tinh: not counted twice
  for (const s of e.stars.filter(x => (x.group === 'cat' || x.group === 'loc') && x.role !== 'mixed' && !x.hoa.some(h => h !== 'Hóa Kỵ')))
    tl.push(add({ id: id('star', s.star, s.palace), name: s.star, palace: s.palace, where: s.where, role: 'tro_luc', ...(s.dignity ? { dignity: s.dignity } : {}), level: s.where === 'self' ? 2 : 3,
      does: `${s.star} ${s.where === 'self' ? 'trong cung' : `từ cung ${s.palace}`} thêm trợ lực` }));
  for (const s of e.tamPhuong.filter(x => x.dignity && BRIGHT.has(x.dignity) && !x.hoa.length))
    tl.push(add({ id: id('star', s.star, s.palace), name: s.star, palace: s.palace, where: s.where, role: 'tro_luc', dignity: s.dignity, level: 3, does: `${s.star} sáng ở cung ${s.palace} hội về` }));
  if (tl.length) {
    const indep = new Set(tl.map(m => m.palace)).size;
    const d = Math.min(1, 0.5 * indep);
    strength += d;
    steps.push({ role: 'tro_luc', strength, members: tl.map(m => m.id), note: `${tl.length} trợ lực ở ${indep} cung: thêm ${d} bậc (nửa bậc mỗi cung, tối đa một bậc); trợ lực không tự đổi tính chất` });
  }

  // 4. tru: sát tinh not bright, hãm chính tinh of the tam phương, Hóa Kỵ in the tam phương (added in step 2), on the facet a chế hóa names
  const tr: Member[] = members.filter(m => m.role === 'tru');
  for (const s of e.stars.filter(x => x.group === 'sat' || x.group === 'hao'))
    if (s.role === 'limit') tr.push(add({ id: id('star', s.star, s.palace), name: s.star, palace: s.palace, where: s.where, role: 'tru', ...(s.dignity ? { dignity: s.dignity } : {}), level: s.where === 'self' ? 2 : 3,
      does: `${s.star} ${s.where === 'self' ? 'trong cung' : `từ cung ${s.palace}`} làm giảm sức` }));
  for (const s of e.tamPhuong.filter(x => x.dignity === 'hãm' && !x.hoa.some(h => h !== 'Hóa Kỵ')))
    tr.push(add({ id: id('star', s.star, s.palace), name: s.star, palace: s.palace, where: s.where, role: 'tru', dignity: s.dignity, level: 3, does: `${s.star} hãm ở cung ${s.palace} hội về` }));
  // chế hóa the books state between the members (kg/che_hoa.json, conditions read on the chart): who lessens whom
  for (const u of cheHoaUnits(chart, P, k, new Set())) {
    const b = u.book!;
    relations.push({ kind: 'che', from: `${u.star}@${u.palace}`, to: u.tamed ? `${u.tamed}@${P}` : `*@${P}`, note: b.text, cite: `${b.book} p.${b.page}` });
    // a sát tinh the book names against a member of the palace lessens that member, bright or not (e.g. KL p.145 "Khôi Việt sợ … Kình Đà")
    if (u.tamed) for (const n of u.star!.split(', ').filter(n => SATS.has(n))) {
      const at = chart.palaces.find(q => q.name === u.palace)!;
      tr.push(add({ id: id('star', n, at.name), name: n, palace: at.name, where: u.where === 'elsewhere' ? 'trine' : u.where as Where, role: 'tru', level: 3, cite: `${b.book} p.${b.page}`,
        does: `${n} ở cung ${at.name} chế ${u.tamed.split('|').join(', ')}: ${b.text}` }));
    }
  }
  if (tr.length) {
    const uniq = [...new Map(tr.map(m => [m.id, m])).values()];
    const self = uniq.filter(m => m.where === 'self').length, far = uniq.length - self;
    // three quarters of a step for each in the palace, a quarter for each from the tam phương, at most two steps
    const d = Math.min(2, self * 0.75 + far * 0.25);
    strength -= d;
    steps.push({ role: 'tru', strength, members: tr.map(m => m.id),
      note: `${self} yếu tố trừ trong cung, ${far} từ tam phương: bớt ${d} bậc; trừ làm giảm sức, không tự phá tổ hợp` });
  }
  // Tuần / Triệt on the palace: both sides lessened (KL p.203)
  if (pal.tuan || pal.triet) {
    const name = pal.tuan && pal.triet ? 'Tuần và Triệt' : pal.tuan ? 'Tuần' : 'Triệt';
    strength = strength > 2 ? strength - 0.5 : strength < 2 ? strength + 0.5 : strength;
    add({ id: id('tt', name, P), name, palace: P, where: 'self', role: 'tru', level: 2, cite: 'KL p.203', does: `${name} án ngữ: giảm cả cái tốt lẫn cái xấu` });
    steps.push({ role: 'tuan_triet', strength, members: [id('tt', name, P)], note: `${name} kéo tổ hợp về phía giữa nửa bậc (KL p.203)` });
  }

  // 5. pha: a page-checked cách anchored here and evaluated broken; rescued when the evaluation found a rescuer
  let state: ConfigState = !core.length && !e.hoa.length ? 'chua_du' : tr.length ? 'co_dieu_kien' : 'thanh';
  const FV = (k.kg as { formationsVerified?: { formations: Parameters<typeof evaluateFormations>[0] } } | undefined)?.formationsVerified;
  for (const f of FV ? evaluateFormations(FV.formations, chart.base).filter(f => f.anchor === P) : []) {
    if (f.state === 'bi_pha' || f.state === 'pha_duoc_cuu') {
      const breakers = [...f.breakers, ...f.uncovered].flatMap(b => b.present ?? []);
      add({ id: id('cach', f.name, P), name: `cách ${f.name}`, palace: P, where: 'self', role: 'pha', level: 4, does: `cách ${f.name} bị phá${breakers.length ? ` bởi ${joinVi([...new Set(breakers)])}` : ''}` });
      state = f.state === 'pha_duoc_cuu' ? 'duoc_cuu' : 'bi_pha';
      steps.push({ role: 'pha', strength, members: [id('cach', f.name, P)], note: `cách ${f.name}: ${f.state === 'pha_duoc_cuu' ? 'bị phá nhưng được cứu' : 'bị phá'}` });
    }
  }
  strength = Math.max(0, Math.min(4, strength));
  steps.push({ role: 'state', strength, members: [], note: `trạng thái ${state}, sức ${strengthWord(strength)}` });

  // what the books read on this palace (the configuration's own words)
  const rules = e.rules.filter(r => !r.timing).map(r => ({ ruleId: r.ruleId, concept: r.concept, pol: r.pol, cites: r.cites, stars: r.stars }));
  // activation: đại hạn whose palace is a member's palace, or whose Hóa lands on a member (plan G9.2 activation, read by G6)
  const pals = new Set(members.map(m => m.palace));
  const activation: Activation[] = (chart.decades ?? []).flatMap(d => {
    const touched: string[] = [], what: string[] = [];
    if (d.palace === P) what.push('hạn vào chính cung');
    else if (pals.has(d.palace)) what.push(`hạn vào cung ${d.palace} của tổ hợp`);
    for (const [h, v] of Object.entries(d.hoa ?? {})) {
      const m = members.find(x => x.palace === v.palace && (x.name === v.star || x.name.startsWith(`${v.star} `)));
      if (m) { touched.push(m.id); what.push(`${h} của hạn vào ${v.star}`); }
    }
    return what.length ? [{ age_from: d.age_from, age_to: d.age_to, palace: d.palace, what: what.join(', '), members: touched }] : [];
  });

  // the questions a configuration must answer (plan G9.2); an answer with no ground says so
  const ids = (ms: Member[]) => ms.map(m => m.id);
  // what the core stars are, in the book's words for this palace's matter (KL, star_nature.json: page-checked quotes)
  // the domain prefixes of the palace's depth section (domains.json depth): a nature must speak of the palace's own matter
  const dcfg = Object.values(((k.kg?.domains as { depth?: Record<string, { palace: string; use: string; prefix: string[] }> } | undefined)?.depth) ?? {}).find(x => x.palace === P);
  const use = dcfg?.use ?? USE[P];
  const natures = core.flatMap(m => { const n = use ? natureOf(k, m.name, use as never, new Set(), { palace: P, prefix: dcfg?.prefix ?? [] }) : undefined; return n ? [{ m, n }] : []; });
  const questions: Answer[] = [
    { q: 'Sao chủ mang tính chất gì?', known: natures.length > 0, evidence: natures.map(x => x.m.id),
      a: natures.length ? natures.map(x => `${x.m.name} ${x.n.text} (KL p.${x.n.page})`).join('; ') : 'chưa có lời nào về tính chất sao chủ cho việc của cung này' },
    { q: 'Cung mượn sức từ đâu?', known: core.length > 0, evidence: ids(core),
      a: !core.length ? `cung ${P} và cung đối đều không có chính tinh` : core.some(m => m.borrowed) ? `mượn ${joinVi(core.map(m => m.name))} từ cung ${opp.name}` : `tự có ${joinVi(core.map(m => m.name))}` },
    { q: 'Yếu tố nào đổi tính chất tổ hợp?', known: bt.length > 0, evidence: ids(bt), a: bt.length ? joinVi(bt.map(m => `${m.name} ở ${m.palace} (${m.does})`)) : 'không có Hóa Lộc, Quyền, Khoa nào trong tam phương' },
    { q: 'Trợ lực ở mức nào?', known: true, evidence: ids(tl), a: tl.length ? `${joinVi(tl.map(m => m.name))}; trợ lực thêm sức chứ không tự bảo đảm` : 'không có cát tinh hội về' },
    { q: 'Yếu tố nào làm giảm, có phá cả tổ hợp không?', known: true, evidence: [...ids(tr), ...ids(members.filter(m => m.role === 'pha'))],
      a: `${tr.length ? `giảm: ${joinVi(tr.map(m => `${m.name}${m.palace !== P ? ` (${m.palace})` : ''}`))}` : 'không có yếu tố trừ'}; ${state === 'bi_pha' ? 'có cách bị phá' : state === 'duoc_cuu' ? 'có cách bị phá nhưng được cứu' : 'chưa có lời nào nói tổ hợp bị phá'}` },
    { q: 'Chặng nào kích hoạt tổ hợp?', known: activation.length > 0, evidence: activation.flatMap(a => a.members),
      a: activation.length ? activation.slice(0, 4).map(a => `${a.age_from}–${a.age_to} (${a.what})`).join('; ') : 'không đại hạn nào chạm vào các thành viên' },
  ];
  const level: Level = members.some(m => m.level === 4) ? 4 : members.some(m => m.level === 3) ? 3 : 2;
  return { id: `cfg:${P}`, palace: P, branch: pal.branch, version: CONFIG_VERSION, level, core, members, relations, rules, state, strength, steps, questions, activation, basis: 'he_thong' };
}

/** The configurations of the palaces a report reads as domains (Mệnh and the domain palaces). */
export const CONFIG_PALACES = ['Mệnh', 'Quan Lộc', 'Tài Bạch', 'Điền Trạch', 'Phu Thê', 'Phúc Đức', 'Thiên Di', 'Tật Ách'];
export const configurations = (chart: ChartInput, k: Knowledge, resolved: Resolved[]) => CONFIG_PALACES.map(P => configurationOf(chart, k, P, resolved));
export type { Palace };
