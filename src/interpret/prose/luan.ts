// Luận cung (prose-style plan S2–S4): each palace read the way the reference reading the owner admires is built, from the palace's own
// ReadingPlan (reason/plan.ts reasonPalace), so every claim is still a fired rule placed on its seat:
//   frame       the palace and its branch, its chính tinh with the checked brightness, the brightest chính tinh of its tam phương tứ chính and
//               the palace it shines from, the Khảo Luận star group the two share (KL pp.166-167), its companions and Tuần/Triệt;
//               at Mệnh also the centre of the reading and the draft cách cục states;
//   topics      the theses grouped by what they speak of, each group a paragraph with a bold lead-in ("Về tính cách và cách giao tiếp"); inside
//               a paragraph the thesis is argued as in the reasoned chapter (claim → behaviour → the book's reducers / the other side → the
//               rescuer's limit → tam phương), then its tail: what the paragraph's limit asks of the person (the card's `mature`) and, when a
//               strength and a limit came from one seat, the two-edged image that ties them to it (both he_thong, nothing new is claimed);
//   Mệnh only   the cung giáp pairs, nhị hợp and lục hại (positions, no meaning: no book in the repository reads them natally), Thân cư with
//               the Thân palace's own strongest thesis (the palace chapter then leaves it out), the later đại hạn by Khảo Luận's tam hợp
//               rule (KL pp.230-233), and a closing that walks from youth (Mệnh = tuổi thơ, KL pp.233-236) to maturity (Thân) and late life;
//   other       a short closing over the strength and the limit the chapter said.
// A palace whose plan has no thesis and no modifier keeps the older chapter (chapter.ts), so no chapter is emptier than before.
import type { ChartInput, Concept, Knowledge, Palace } from '../types.ts';
import { run } from '../engine.ts';
import { lift, type Labelled } from '../kg/lift.ts';
import { applyQualifiers, resolve, type Resolved } from '../kg/resolve.ts';
import { reasonPalace, type ReadingPlan, type Thesis } from '../reason/plan.ts';
import type { Reading } from '../reason/adjudicate.ts';
import { Micro } from './micro.ts';
import { Writer, argueThesis, lowerSafe, structureSentences, type ArgueCtx, type ReasoningFrames } from './narrative.ts';
import { configClause, dignityOf, hoaOn, joinVi, named, palaceConfig } from './named.ts';
import { bookStarsOf, readPalace } from './deep.ts';
import type { ProseParagraph, ProseSentence, SentenceTrace } from './realize.ts';
import { validateProse } from './validate.ts';
import { PROSE_ORDER, PROSE_SPECS, PROSE_VERSION, proseReport, seedOf, type ProseChapter, type ProseChapterId } from './chapter.ts';

export type Topic = 'tinh_cach' | 'su_nghiep' | 'tai_loc' | 'quy_nhan' | 'quan_he' | 'duong_doi' | 'the_trang' | 'vi_tri' | 'than' | 'than_same' | 'than_style'
  | 'hau_van' | 'tong_ket' | 'tom_lai' | 'pho_thong';
export interface LuanLib {
  status: string;
  lead: Record<Topic, string[]>; lead_palace: Record<string, Partial<Record<Topic, string[]>>>;
  /** one lead-in for two short neighbouring topics told as one paragraph ("su_nghiep|duong_doi") */
  lead_pair: Record<string, string[]>;
  frame: Record<'open' | 'open_pair' | 'open_vcd' | 'open_empty' | 'tp_contrast' | 'tp_add' | 'opp_contrast' | 'opp_add' | 'with' | 'tt' | 'tt_alone' | 'group' | 'group_self', string[]>;
  tail: Record<'synth' | 'advice' | 'edge', string[]>;
  than: Record<'pos' | 'meaning' | 'same' | 'rule' | 'borrow', string[]>;
  pos: Record<'giap' | 'nhi_hop' | 'luc_hai', string[]>;
  late: Record<'neg' | 'pos' | 'calm' | 'course', string[]>;
  summary: Record<'arc' | 'mature' | 'mature_same' | 'late' | 'late_calm' | 'turn' | 'close' | 'close_pos' | 'close_neg', string[]>;
  health_note: string[];
}
/** A luận cung chapter: the shape of the older chapter (report.js reads either), plus a title and the plan it was argued from. */
export interface LuanChapter extends ProseChapter { title: string; luan: true; theses: string[] }

export const LUAN_VERSION = 'luan-0.1.0';
const fill = (t: string, v: Record<string, string>) => t.replace(/\{([A-Za-z_]+)\}/g, (_, key) => { if (v[key] === undefined) throw new Error(`slot {${key}} unfilled in: ${t}`); return v[key]; });
const RANK: Record<string, number> = { 'miếu': 6, 'vượng': 5, 'đắc': 4, 'lợi': 3, 'bình': 2, 'hãm': 1 };
/** pairs that flank a palace from its two neighbours (cung giáp), named as the books name them; Hóa pairs from the natal Tứ Hóa */
const GIAP: Array<[string, string]> = [['Tả Phụ', 'Hữu Bật'], ['Văn Xương', 'Văn Khúc'], ['Thiên Khôi', 'Thiên Việt'], ['Thái Dương', 'Thái Âm'], ['Tử Vi', 'Thiên Phủ'],
  ['Hóa Khoa', 'Hóa Lộc'], ['Hóa Quyền', 'Hóa Lộc'], ['Hóa Khoa', 'Hóa Quyền'], ['Kình Dương', 'Đà La'], ['Địa Không', 'Địa Kiếp'], ['Hỏa Tinh', 'Linh Tinh']];
const KL_NEG = new Set(['tuổi sinh xuất cho đại vận', 'đại vận khắc tuổi']), KL_POS = new Set(['tuổi khắc đại vận', 'đại vận sinh nhập cho tuổi']);
/** where hậu vận starts, in years of age: a convention of this system (he_thong), not a page */
const LATE_FROM = 43;
const TOPIC_ORDER: Topic[] = ['tinh_cach', 'su_nghiep', 'tai_loc', 'quy_nhan', 'quan_he', 'the_trang', 'duong_doi'];
const CONNECTIVE_OPEN = /^(Cũng vậy|Ngoài ra|Đồng thời|Thêm vào đó|Bên cạnh đó|Mặt khác|Hơn nữa|Lại nữa|Cũng thế|Về đường đời|Trên đường đời|Về nhịp chung),\s*/u;
/** a paragraph holds at most this many sentences before the topic goes on in the next one (the reference's paragraphs run 5–8) */
const PARA_MAX = 8;
/** facets whose concepts are traits: only these are set side by side in a tail or named in the closing (a course concept such as
 *  "phần bất lợi được giảm nhẹ" is not a side of anyone's character) */
const TRAIT = /^(identity|inner|career|finance|relationships)\./;
/** a sentence that opens with a name keeps its capital after the lead-in: stars, palaces, branches, Hóa, Tuần/Triệt */
const NAME_OPEN = new RegExp('^(?:' + ['Tử Vi', 'Thiên Cơ', 'Thái Dương', 'Vũ Khúc', 'Thiên Đồng', 'Liêm Trinh', 'Thiên Phủ', 'Thái Âm', 'Tham Lang', 'Cự Môn', 'Thiên Tướng',
  'Thiên Lương', 'Thất Sát', 'Phá Quân', 'Kình Dương', 'Đà La', 'Hỏa Tinh', 'Linh Tinh', 'Địa Không', 'Địa Kiếp', 'Tả Phụ', 'Hữu Bật', 'Văn Xương', 'Văn Khúc', 'Thiên Khôi',
  'Thiên Việt', 'Lộc Tồn', 'Thiên Mã', 'Hóa', 'Tuần', 'Triệt', 'Mệnh', 'Thân', 'Tài Bạch', 'Quan Lộc', 'Thiên Di', 'Phu Thê', 'Phúc Đức', 'Điền Trạch', 'Nô Bộc', 'Tử Tức',
  'Huynh Đệ', 'Phụ Mẫu', 'Tật Ách', 'Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Dậu', 'Tuất', 'Hợi'].join('|') + ')(?![\\p{L}])', 'u');
/** "Về tính cách, …": the lead-in, then the sentence with its opening connective dropped and its first letter lowered unless it opens with a
 *  name (the fixed list, or any star of the chart: "Tiểu Hao", "Thanh Long") */
export function withLead(lead: string, text: string, names: Set<string> = new Set()): string {
  const body = text.replace(CONNECTIVE_OPEN, '');
  const named = NAME_OPEN.test(body) || [...names].some(n => body.startsWith(n) && !/\p{L}/u.test(body.charAt(n.length)));
  return `${lead}, ${named ? body : body.charAt(0).toLocaleLowerCase('vi') + body.slice(1)}`;
}
/** a book sentence voicing a reading (concept@palace) the report already voiced is dropped: no reading is told twice */
function dedupe(xs: ProseSentence[], keys: Set<string>): ProseSentence[] {
  return xs.filter(s => {
    if (s.trace.basis !== 'sach' || s.trace.move === 'ELABORATE' || !s.trace.keys?.length) return true;
    if (s.trace.keys.some(x => keys.has(x))) return false;
    s.trace.keys.forEach(x => keys.add(x));
    return true;
  });
}

/** What a reading speaks of, by its concept's facet; a reading resting on the cung giáp is about the people around. At Mệnh money and career
 *  are one topic, as in the reference ("năng lực và sự nghiệp"); a palace of money keeps them apart. */
function topicOf(c: Concept | undefined, palace: string, flank = false): Topic {
  const f = c?.facet ?? '';
  if (flank || f === 'career.support' || (f === 'relationships.allies' && palace === 'Mệnh')) return 'quy_nhan';
  if (f.startsWith('identity.') || f.startsWith('inner.')) return 'tinh_cach';
  if (f.startsWith('career.')) return 'su_nghiep';
  if (f.startsWith('finance.')) return palace === 'Mệnh' ? 'su_nghiep' : 'tai_loc';
  if (f.startsWith('relationships.')) return 'quan_he';
  if (f.startsWith('wellbeing.')) return 'the_trang';
  return 'duong_doi';
}

/** Everything the chapters of one report share: one rule run, one resolution, one variant memory, the rules told so far (none is told
 *  twice), the theses another chapter already told (Thân cư tells the Thân palace's strongest thesis). */
export interface LuanShared { findings: ReturnType<typeof run>['findings']; resolved: Resolved[]; labelled: Labelled[]; micro: Micro; voiced: Set<string>;
  /** readings (concept@palace) told so far in the report */
  keys: Set<string>; told: Set<string>; seed: string; allowDraft: boolean;
  /** palace|star whose common (phổ thông) reading was already told (Thân cư borrows it) */
  colourTold: Set<string> }

export function luanShared(chart: ChartInput, k: Knowledge, allowDraft: boolean): LuanShared {
  const findings = run(k.rules, k.sources, chart.base).findings;
  const lifted = lift(findings, k, chart.base);
  const resolved = resolve(lifted.assertions, k).resolved;
  applyQualifiers(resolved, k, chart.base);
  const seed = seedOf(chart);
  return { findings, resolved, labelled: lifted.labelled, micro: new Micro(`${seed}|luan`, k.prose!.connectives, k.prose!.frames), voiced: new Set(), keys: new Set(), told: new Set(), seed, allowDraft, colourTold: new Set() };
}

/** The twelve palace chapters: the luận cung chapter where the palace's plan has something to argue, the older chapter otherwise. */
export function luanReport(chart: ChartInput, k: Knowledge, opts: { allowDraft?: boolean; deep?: boolean } = {}): ProseChapter[] {
  const allowDraft = !!opts.allowDraft;
  if (!k.prose?.luan || !(allowDraft || k.prose.luan.status === 'approved')) return proseReport(chart, k, opts);
  const old = proseReport(chart, k, opts);
  const sh = luanShared(chart, k, allowDraft);
  return PROSE_ORDER.map((id, i) => luanChapter(chart, k, id, sh) ?? old[i]);
}

/** One palace in the luận cung form, or null when its plan gives nothing to argue (the caller keeps the older chapter). */
export function luanChapter(chart: ChartInput, k: Knowledge, id: ProseChapterId, sh: LuanShared): LuanChapter | null {
  const L = k.prose!.luan!, F = k.prose!.reasoning!, spec = PROSE_SPECS[id], P = spec.palace, isMenh = P === 'Mệnh';
  const pal = chart.palaces.find(p => p.name === P)!;
  const full = reasonPalace(chart, k, P, { resolved: sh.resolved, labelled: sh.labelled }, { draftFormations: sh.allowDraft });
  const plan: ReadingPlan = { ...full, theses: full.theses.filter(t => !sh.told.has(`${P}|${t.id}`)) };
  if (!plan.theses.length && !plan.modifiers.length) return null;
  const other = spec.bond ? k.prose!.frames.other?.[P] : undefined;
  const W = new Writer(chart, k, plan, sh.allowDraft, { micro: sh.micro, other, bond: spec.bond });
  const ctx: ArgueCtx = { voiced: sh.voiced, allConcepts: new Set(), structAt: [] };
  const lead = (topic: Topic, v: Record<string, string> = {}) => fill(W.pick(`lead|${P}|${topic}`, L.lead_palace[P]?.[topic] ?? L.lead[topic]), v);
  const S = (text: string, trace: Partial<SentenceTrace> & { move: SentenceTrace['move']; step: string }) => W.sentence(text, trace);

  // ---- frame ----
  const frame = frameSentences(W, L, F, chart, pal, plan);

  // ---- theses, in the reasoned chapter's order (a thesis whose rescuer is reduced elsewhere is followed by the rescuer's thesis) ----
  const order: Thesis[] = [], pending = [...plan.theses];
  while (pending.length) {
    const t = pending.shift()!;
    order.push(t);
    const cav = t.rescuerCaveat && pending.findIndex(u => u.seat.id === t.rescuerCaveat!.seat.id);
    if (cav !== undefined && cav >= 0) order.push(...pending.splice(cav, 1));
  }
  // a UNIT is one thesis argued (with the thesis bridged to it, which must follow it), or one modifier sentence; units of a topic make its
  // paragraphs. `own` are the concepts the unit's own seat asserts: only these may be called two sides of that seat.
  type Unit = { topic: Topic; xs: ProseSentence[]; seat?: Thesis['seat']; own: Set<string>; after?: Unit };
  const units: Unit[] = [];
  const ownConcepts = (t: Thesis) => new Set(t.claims.flatMap(c => [...c.axis.base, ...c.axis.against].filter(x => x.seat.id === t.seat.id).map(x => x.r.concept)));
  order.forEach((t, ti) => {
    const xs: ProseSentence[] = [];
    argueThesis(W, F, t, order[ti - 1], order, xs, ctx);
    if (!xs.length && !t.steps.some(st => st.structure)) return;
    // a thesis bridged from the one before it ("Cũng chính Hóa Lộc vừa nói …") keeps that bridge only if it is told right after it
    const prev = order[ti - 1], bridged = !!prev?.rescuerCaveat && prev.rescuerCaveat.seat.id === t.seat.id;
    units.push({ topic: thesisTopic(W, t, P), xs, seat: t.seat, own: ownConcepts(t), ...(bridged && units.length ? { after: units[units.length - 1] } : {}) });
  });
  // ---- modifiers: one grounded sentence each, in the paragraph of what it speaks of ----
  for (const md of plan.modifiers) {
    const x = md.reading;
    if (sh.voiced.has(x.r.ruleId)) continue;
    const r = W.read(x.r.ruleId), ground = W.ground(x);
    const conn = W.pol(x.r.concept) === '-' ? W.conn('contrast', `mod|${x.r.ruleId}`) : W.conn('addition', `mod|${x.r.ruleId}`);
    const p = r.claim ? null : W.pred(x.r.concept, x.r.status !== 'holds', `mod|${x.r.ruleId}`);
    const text = r.claim ? fill(W.pick(`mod|${x.r.ruleId}`, F.modifier), { conn, ground, claim: r.claim })
      : p ? fill(W.pick(`modc|${x.r.ruleId}`, F.modifier_card), { conn, ground, S: W.S(x.r.concept), pred: p }) : '';
    if (!text) continue;
    sh.voiced.add(x.r.ruleId); ctx.allConcepts.add(x.r.concept);
    units.push({ topic: topicOf(W.concept(x.r.concept), P, md.seat.scope === 'flank'), seat: md.seat, own: new Set([x.r.concept]),
      xs: [S(text, { move: 'TENSION', step: `modifier:${md.seat.id}`, concepts: [x.r.concept], rules: [x.r.ruleId], cites: x.r.cites, keys: [`${x.r.concept}@${P}|${x.r.ruleId}`] })] });
  }
  // ---- the course line ----
  let lateCourse: ProseSentence | null = null;
  if (plan.course) {
    const x = rarestOf(plan.course.axis.base), r = W.read(x.r.ruleId);
    if (r.claim && !sh.voiced.has(x.r.ruleId)) {
      sh.voiced.add(x.r.ruleId); ctx.allConcepts.add(x.r.concept);
      const late = isMenh && x.r.concept === 'life.late_bloom';
      const s = S(fill(W.pick(late ? 'late|course' : 'course', late ? L.late.course : F.course), { ground: W.ground(x), claim: r.claim }),
        { move: 'EXTRA', step: `course:${plan.course.axis.key}`, concepts: [x.r.concept], rules: [x.r.ruleId], cites: x.r.cites, keys: [`${x.r.concept}@${P}`] });
      if (late) lateCourse = s; else units.push({ topic: 'duong_doi', xs: [s], own: new Set() });
    }
  }
  // ---- special structures, on the units of the theses that carry them (written last, so the text before them does not move) ----
  for (const { t, xs, at } of ctx.structAt) xs.splice(at, 0, ...structureSentences(W, F.structure, plan, t, [...frame, ...units.flatMap(u => u.xs)]));

  // ---- topic paragraphs: units of one topic together (Mệnh in the reference's order, another palace led by its strongest thesis' topic),
  // a paragraph of at most PARA_MAX sentences, the lead-in on the first paragraph of each topic, each closed by its tail ----
  const topics = [...new Set(units.map(u => u.topic))];
  if (isMenh) topics.sort((x, y) => TOPIC_ORDER.indexOf(x) - TOPIC_ORDER.indexOf(y));
  const paras: ProseParagraph[] = [];
  const names = new Set(chart.palaces.flatMap(p => [...p.stars, ...p.major_stars]));
  /** a paragraph: its sentences less any reading the report already told, then its tail (computed on what is left), then its lead-in */
  const para = (role: ProseParagraph['role'], topic: Topic | null, xs0: ProseSentence[], leadText?: string, tailOf?: (xs: ProseSentence[]) => ProseSentence[]): ProseParagraph | null => {
    let xs = dedupe(xs0, sh.keys);
    // a paragraph of the system's words alone stands only as the closing
    if (!xs.length || (!xs.some(s => s.trace.basis !== 'he_thong') && topic !== 'tong_ket' && topic !== 'tom_lai')) return null;
    if (tailOf) xs = [...xs, ...tailOf(xs)];
    if (leadText) xs[0] = { ...xs[0], text: withLead(leadText, xs[0].text, names) };
    const p: ProseParagraph = { role, sentences: xs, text: xs.map(s => s.text).join(' '), ...(leadText ? { lead: leadText } : {}), ...(topic ? { topic } : {}) };
    paras.push(p);
    return p;
  };
  para('structure', null, frame);
  const placed = topics.flatMap(topic => units.filter(u => u.topic === topic));
  placed.forEach((u, i) => { if (u.after && placed[i - 1] !== u.after) u.xs = u.xs.filter(s => !(s.trace.step ?? '').startsWith('bridge:')); });
  // paragraphs: a topic's units up to PARA_MAX sentences; two neighbouring topics of at most two sentences each are told as one, under a
  // lead-in naming both when the library has one
  const groups: Array<{ topics: Topic[]; us: Unit[] }> = [];
  for (const topic of topics) for (const u of units.filter(x => x.topic === topic)) {
    const g = groups[groups.length - 1], n = g ? g.us.reduce((a, x) => a + x.xs.length, 0) : 0;
    if (g && g.topics.at(-1) === topic && n + u.xs.length <= PARA_MAX) { g.us.push(u); continue; }
    const pairKey = g && `${g.topics[0]}|${topic}`;
    if (g && g.topics.length === 1 && g.topics[0] !== topic && n <= 2 && u.xs.length <= 2 && L.lead_pair[pairKey!]) { g.topics.push(topic); g.us.push(u); continue; }
    // a lone sentence on a topic of its own does not get a paragraph: it closes the paragraph before it
    if (g && u.xs.length === 1 && n + 1 <= PARA_MAX && units.filter(x => x.topic === topic).length === 1) { g.us.push(u); continue; }
    groups.push({ topics: [topic], us: [u] });
  }
  groups.forEach((g, gi) => {
    const xs = g.us.flatMap(u => u.xs);
    if (!xs.length) return;
    const first = groups.findIndex(h => h.topics[0] === g.topics[0]) === gi;
    const leadText = g.topics.length > 1 ? W.pick(`lead2|${P}|${g.topics.join('|')}`, L.lead_pair[g.topics.join('|')]) : first ? lead(g.topics[0]) : undefined;
    para(gi === 0 ? 'core' : 'support', g.topics[0], xs, leadText, ys => tail(W, L, ys, g.us, `${P}|${g.topics.join('|')}|${gi}`));
  });

  // ---- Mệnh only: cung giáp / nhị hợp / lục hại, Thân cư, hậu vận, the closing arc ----
  let thanNp: string | null = null, thanPal: Palace | null = null, lateAge: string | null = null, lateCalm = false;
  if (isMenh) {
    const vt = positionSentences(W, L, chart, pal);
    if (vt.length) para('support', 'vi_tri', vt, lead('vi_tri'));
    const than = chart.palaces.find(p => p.is_than) ?? pal;
    thanPal = than;
    if (than === pal) para('support', 'than_same', [S(W.pick('than|same', L.than.same), { move: 'ANCHOR', step: 'than:same', basis: 'pho_thong' })], lead('than_same'));
    else {
      const r = thanSentences(W, L, F, chart, k, than, sh, new Set(paras.flatMap(p => p.sentences.flatMap(s => s.trace.concepts))));
      thanNp = r.np;
      para('support', 'than', r.position, lead('than', { pal: than.name }));
      if (r.style.length) para('support', 'than_style', r.style, lead('than_style'), ys => tail(r.W, L, ys, r.units, `than|${than.name}`));
    }
    const late = lateSentences(W, L, chart);
    lateAge = late.age; lateCalm = late.calm;
    const lx = [...late.xs, ...(lateCourse ? [lateCourse] : [])];
    if (lx.length) para('course', 'hau_van', lx, lead('hau_van'));
  } else if (lateCourse) para('course', 'duong_doi', [lateCourse], lead('duong_doi'));

  // ---- closing ----
  const said = paras.flatMap(p => p.sentences).filter(s => s.trace.basis === 'sach');
  const conceptsSaid = [...new Set(said.flatMap(s => s.trace.concepts))].filter(c => W.card(c) && TRAIT.test(W.concept(c)?.facet ?? ''));
  const pos = conceptsSaid.filter(c => W.pol(c) === '+'), neg = conceptsSaid.filter(c => W.pol(c) === '-');
  const closing: ProseSentence[] = [];
  if (isMenh) {
    // the youth: the first strength and the first limit the Mệnh paragraphs told (or the first two traits), strength first
    const young = (pos.length && neg.length ? [pos[0], neg[0]] : conceptsSaid.slice(0, 2)).map(c => W.np(c));
    if (young.length) {
      const mature = thanPal && thanPal !== pal && thanNp ? fill(W.pick('sum|mature', L.summary.mature), { pal: thanPal.name, np: thanNp })
        : thanPal === pal ? W.pick('sum|mature_same', L.summary.mature_same) : '';
      const lateTxt = lateAge ? fill(W.pick('sum|late', L.summary.late), { age: lateAge }) : lateCalm ? W.pick('sum|late_calm', L.summary.late_calm) : '';
      closing.push(S(fill(W.pick('sum|arc', L.summary.arc), { S: W.S(), young: joinVi(young), mature, late: lateTxt }), { move: 'VALUE', step: 'closing:arc', basis: 'he_thong' }));
      if (pos.length && neg.length) closing.push(S(fill(W.pick('sum|turn', L.summary.turn), { S: W.S(), pos: W.np(pos[0]), neg: W.np(neg[0]) }), { move: 'VALUE', step: 'closing:turn', basis: 'he_thong' }));
    }
    if (closing.length) para('course', 'tong_ket', closing, lead('tong_ket'));
  } else if (paras.filter(p => p.lead).length >= 2) {
    const tpl = pos.length && neg.length ? L.summary.close : pos.length ? L.summary.close_pos : neg.length ? L.summary.close_neg : [];
    if (tpl.length) closing.push(S(fill(W.pick(`sum|close|${P}`, tpl), { a: pos.length ? W.np(pos[0]) : '', b: neg.length ? W.np(neg[0]) : '' }), { move: 'VALUE', step: 'closing', basis: 'he_thong' }));
    if (closing.length) para('course', 'tom_lai', closing, lead('tom_lai'));
  }
  // a palace the books say little about: the common reading of its chính tinh and notable phụ tinh, labelled phổ thông (deep.ts), for the
  // stars no book sentence of the chapter already speaks of
  if (!isMenh && paras.flatMap(p => p.sentences).filter(s => s.trace.basis === 'sach').length < 4) {
    const opp = chart.palaces.find(p => p.branch_index === (pal.branch_index + 6) % 12);
    // a star a book sentence of the chapter (or Thân cư, for this palace) already speaks of is not read again from the common cards
    const ruleIds = new Set(paras.flatMap(p => p.sentences.flatMap(s => s.trace.rules)));
    const inBook = new Set([...names].filter(n => k.rules.some(r => ruleIds.has(r.id) && JSON.stringify(r.conditions).includes(`"${n}"`))));
    const bookStars = new Set([...bookStarsOf(paras, k, pal, opp), ...[...sh.colourTold].filter(x => x.startsWith(`${P}|`)).map(x => x.slice(P.length + 1))]);
    const colour = readPalace(chart, k, P, sh.micro, { key: 'luan', bookStars, lead: false }).colour
      .filter(s => ![...inBook].some(n => s.text.startsWith(`${n} ở cung`)));
    const at = paras.findIndex(p => p.topic === 'tom_lai');
    const before = at < 0 ? paras.length : at;
    const n = paras.length;
    para('colour', 'pho_thong', colour, lead('pho_thong' as Topic));
    if (paras.length > n && before < n) paras.splice(before, 0, paras.pop()!);
  }
  if (P === 'Tật Ách' && paras.some(p => p.topic === 'the_trang')) paras.at(-1)!.sentences.push(S(W.pick('health', L.health_note), { move: 'VALUE', step: 'health_note', basis: 'he_thong' }));
  for (const p of paras) p.text = p.sentences.map(s => s.text).join(' ');

  const resolvedHere = sh.resolved.filter(r => r.subject === `palace:${P}` || (isMenh && r.subject === 'chart'));
  const { issues, metrics } = validateProse(paras, resolvedHere);
  paras.forEach((p, pi) => p.sentences.forEach((s, si) => { if (!s.trace.step) issues.push({ level: 'error', code: 'no_plan_step', where: `p${pi + 1}s${si + 1}`, msg: s.text }); }));
  const rmap = new Map(k.rules.map(r => [r.id, r]));
  const reading = (rid: string) => { const r = rmap.get(rid)!; return (r.reading ?? k.claims[r.consequences[0]?.claim ?? ''] ?? '').replace(/^(khuynh hướng|hạn chế:)\s*/, ''); };
  const ruleIds = [...new Set(paras.flatMap(p => p.sentences.flatMap(s => s.trace.rules)))].filter(r => rmap.has(r)).sort();
  const book = paras.flatMap(p => p.sentences).filter(s => s.trace.basis === 'sach').length;
  if (!book) return null;
  return {
    engine: PROSE_VERSION, kbVersion: k.version, chapter: id, palace: P, title: `Luận cung ${P}`, luan: true, schema: 'luan', order: [],
    theses: plan.theses.map(t => t.id),
    draft: sh.allowDraft && (L.status !== 'approved' || F.status !== 'approved' || k.prose!.concepts.some(c => c.status !== 'approved')),
    paragraphs: paras, text: paras.map(p => p.text).join('\n\n'), issues, metrics, pass: !issues.some(i => i.level === 'error'),
    advice: { strengths: [], actions: [], basis: 'he_thong' },
    evidence: {
      resolved: resolvedHere.map(r => ({ ruleId: r.ruleId, concept: r.concept, stance: r.stance, status: r.status, by: r.by, cites: r.cites })), tensions: [], unused: [],
      rules: Object.fromEntries(ruleIds.map(rid => [rid, { reading: reading(rid), cites: rmap.get(rid)!.cites, verified: rmap.get(rid)!.reviewStatus === 'verified' }])),
      concepts: Object.fromEntries([...new Set(paras.flatMap(p => p.sentences.flatMap(s => s.trace.concepts)))].map(c => [c, k.concepts.concepts.find(x => x.id === c)?.short ?? c])),
      divergences: [],
    },
  };
}

/** A thesis' topic: that of its first claim with a topic of its own; a thesis of course concepts only reads as the course of life. */
function thesisTopic(W: Writer, t: Thesis, P: string): Topic {
  const flank = t.seat.scope === 'flank';
  return t.claims.map(c => topicOf(W.concept(c.concept), P, flank)).find(x => x !== 'duong_doi') ?? 'duong_doi';
}
const rarestOf = (xs: Reading[]) => [...xs].sort((a, b) => Number(b.r.status === 'holds') - Number(a.r.status === 'holds') || b.rarity - a.rarity || (a.r.ruleId < b.r.ruleId ? -1 : 1))[0];

/** The palace's opening: where it stands, its chính tinh, the brightest chính tinh around it and the group they share, its companions;
 *  at Mệnh the centre of the reading and the draft cách cục states (as in the reasoned chapter). */
function frameSentences(W: Writer, L: LuanLib, F: ReasoningFrames, chart: ChartInput, pal: Palace, plan: ReadingPlan): ProseSentence[] {
  const out: ProseSentence[] = [], P = pal.name, cfg = palaceConfig(chart, pal), byIdx = new Map(chart.palaces.map(p => [p.branch_index, p]));
  const opp = byIdx.get((pal.branch_index + 6) % 12)!;
  const cites = new Set(cfg.cites);
  const own = pal.major_stars;
  let open: string;
  if (own.length) open = fill(W.pick(`frame|open|${P}`, own.length > 1 ? L.frame.open_pair : L.frame.open), { pal: P, branch: pal.branch, majors: joinVi(cfg.majors) });
  else if (opp.major_stars.length) {
    open = fill(W.pick(`frame|vcd|${P}`, L.frame.open_vcd), { pal: P, branch: pal.branch, majors: joinVi(opp.major_stars.map(s => named(opp, s))) });
    opp.major_stars.forEach(s => { const d = dignityOf(opp, s); if (d?.cite) cites.add(d.cite); });
  } else open = fill(W.pick(`frame|empty|${P}`, L.frame.open_empty), { pal: P, branch: pal.branch });
  // the brightest chính tinh of the tam phương tứ chính (checked cells only); the opposite palace is not counted again when it was borrowed
  const tp = [4, 8, 6].map(d => byIdx.get((pal.branch_index + d) % 12)!).filter(q => q && !(q === opp && !own.length));
  const cand = tp.flatMap(q => q.major_stars.map(s => ({ q, s, d: dignityOf(q, s) }))).filter(x => x.d && (RANK[x.d.value] ?? 0) >= RANK['đắc'])
    .sort((a, b) => RANK[b.d!.value] - RANK[a.d!.value] || Number(b.q === opp) - Number(a.q === opp) || (a.s < b.s ? -1 : 1));
  const ownDim = own.length > 0 && own.every(s => dignityOf(pal, s)?.value === 'hãm');
  let tpStar: string | null = null;
  if (cand.length) {
    const c = cand[0], isOpp = c.q === opp;
    if (c.d!.cite) cites.add(c.d!.cite);
    tpStar = c.s;
    const tpl = isOpp ? (ownDim ? L.frame.opp_contrast : L.frame.opp_add) : (ownDim ? L.frame.tp_contrast : L.frame.tp_add);
    open += ', ' + fill(W.pick(`frame|tp|${P}`, tpl), { star: [named(c.q, c.s), ...hoaOn(chart, c.q, c.s)].join(' '), from: `cung ${c.q.name} (${c.q.branch})` });
  }
  out.push(W.sentence(open, { move: 'ANCHOR', step: `frame:${P}`, basis: 'tinh_toan', cites: [...cites].sort() }));
  // the Khảo Luận group the palace's star and the brightest star around it share (KL pp.166-167)
  const gn = (W.k.reference as { groupNotes?: { members: Record<string, string[]>; notes: Record<string, string> } } | undefined)?.groupNotes;
  const a = own[0] ?? opp.major_stars[0];
  const grp = gn && a ? Object.entries(gn.members).find(([, ms]) => ms.includes(a)) : undefined;
  if (grp && tpStar && grp[1].includes(tpStar) && tpStar !== a)
    out.push(W.sentence(fill(W.pick(`frame|group|${P}`, L.frame.group), { a, b: tpStar, group: grp[0], note: gn!.notes[grp[0]] }), { move: 'ANCHOR', step: `frame:group:${grp[0]}`, basis: 'tinh_toan', cites: ['KL pp.166-167'] }));
  else if (grp && P === 'Mệnh')
    out.push(W.sentence(fill(W.pick(`frame|group1|${P}`, L.frame.group_self), { a, group: grp[0], note: gn!.notes[grp[0]] }), { move: 'ANCHOR', step: `frame:group:${grp[0]}`, basis: 'tinh_toan', cites: ['KL pp.166-167'] }));
  // companions and Tuần / Triệt
  const comp = [...cfg.sat, ...cfg.cat, ...cfg.other].slice(0, 4);
  const tt = cfg.tuanTriet.length ? fill(W.pick(`frame|tt|${P}`, L.frame.tt), { tt: joinVi(cfg.tuanTriet) }) : '';
  if (comp.length) out.push(W.sentence(fill(W.pick(`frame|with|${P}`, L.frame.with), { stars: joinVi(comp) }) + (tt ? `; ${tt}` : ''), { move: 'ANCHOR', step: `frame:with:${P}`, basis: 'tinh_toan', cites: cfg.cites }));
  else if (tt) out.push(W.sentence(fill(W.pick(`frame|tt1|${P}`, L.frame.tt_alone), { tt: joinVi(cfg.tuanTriet), pal: P }), { move: 'ANCHOR', step: `frame:tt:${P}`, basis: 'tinh_toan' }));
  if (P !== 'Mệnh') return out;
  // the centre of the reading, then the draft cách cục states
  const fr = plan.frame, centre = fr.centre.seat;
  const star = (fr.centre.why === 'major' && centre.star) || fr.majors[0]?.star || fr.borrowed[0] || '';
  const centreName = fr.vcd ? `${joinVi(fr.borrowed)} ở cung xung chiếu` : centre.kind === 'major' ? (centre.star ?? star) : centre.star ?? W.seatGround(centre);
  if (star || fr.vcd) {
    const formName = fr.formations.find(f => f.seat === centre.id && f.kind === 'formation')?.name ?? centreName;
    // "Cự Môn là chính tinh, nhưng điều làm lá số này khác đi lại nằm ở Cự Môn" says nothing: a centre that is the star itself reads as a major
    const why = fr.centre.why !== 'major' && fr.centre.why !== 'vcd' && (formName === star || centreName === star) ? 'major' : fr.centre.why;
    out.push(W.sentence(fill(W.pick(`centre|${why}`, F.centre[why]), { star: star || centreName, name: formName, seat: centreName }), { move: 'ANCHOR', step: `centre:${centre.id}`, basis: 'he_thong' }));
  }
  const norm = (x: string) => x.toLowerCase().replace(/^cách\s+/, '').trim();
  const verifiedNames = new Set(fr.formations.map(f => norm(f.name)));
  for (const st of fr.states.slice(0, 2)) {
    if ([...verifiedNames].some(v => v.includes(norm(st.name)) || norm(st.name).includes(v))) continue;
    const list = (xs: string[]) => joinVi(xs.slice(0, 2).map(x => lowerSafe(x.replace(/\s*\([^()]*\)/g, ''))));
    const v = { name: st.name, boosters: list(st.boosters), breakers: list(st.uncovered.length ? st.uncovered : st.breakers), rescuers: list(st.rescuers) };
    const tpl = (F.formation_state as Record<string, string[]>)[st.state + (st.state === 'thanh' && !st.boosters.length ? '_plain' : '')] ?? [];
    if (tpl.length) out.push(W.sentence(fill(W.pick(`fstate|${st.id}`, tpl), v), { move: 'ANCHOR', step: `cach:${st.id}:${st.state}`, basis: 'he_thong', concepts: [`cach:${st.id}:${st.state}`] }));
  }
  return out;
}

/** The tail of an argued paragraph: when it said a limit, what that limit asks of the person (the card's `mature`); when a strength and a
 *  limit came from the same seat, the two-edged image naming that seat; two strengths and no limit, the line that sets them side by side.
 *  Nothing new is claimed: the noun phrases are those of concepts the paragraph's book sentences voiced. */
function tail(W: Writer, L: LuanLib, xs: ProseSentence[], units: Array<{ seat?: Thesis['seat']; own: Set<string> }>, key: string): ProseSentence[] {
  const out: ProseSentence[] = [];
  const book = xs.filter(s => s.trace.basis === 'sach');
  const concepts = [...new Set(book.flatMap(s => s.trace.concepts))].filter(c => W.card(c) && TRAIT.test(W.concept(c)?.facet ?? ''));
  const pos = concepts.filter(c => W.pol(c) === '+'), neg = concepts.filter(c => W.pol(c) === '-');
  // a limit the book put on a strength (a reducer) counts as the strength's limit: its card's mature clause answers it
  const reduced = book.filter(s => s.trace.move === 'TURN').flatMap(s => s.trace.concepts).filter(c => W.pol(c) !== '-' && W.card(c)?.mature?.length);
  const answer = [...neg, ...reduced].find(c => W.card(c)?.mature?.length);
  if (answer) {
    const m = W.pick(`tail|mature|${answer}`, W.card(answer)!.mature!);
    out.push(W.sentence(fill(W.pick(`tail|advice|${key}`, L.tail.advice), { S: W.S(answer), mature: m }), { move: 'TRANSFORM', step: `advice:${answer}`, basis: 'he_thong', concepts: [answer] }));
  }
  // the two-edged image only for a strength and a limit the same star asserts (its own seat), named by that star
  const edge = units.map(u => ({ u, p: pos.find(c => u.own.has(c)), n: neg.find(c => u.own.has(c)) })).find(x => x.p && x.n && x.u.seat?.star && x.u.seat.kind !== 'hoa');
  if (edge)
    out.push(W.sentence(fill(W.pick(`tail|edge|${key}`, L.tail.edge), { a: W.np(edge.p!), b: W.np(edge.n!), seat: edge.u.seat!.star! }), { move: 'VALUE', step: `edge:${edge.p}|${edge.n}`, basis: 'he_thong', concepts: [edge.p!, edge.n!] }));
  else if (!neg.length && !answer && pos.length >= 2)
    out.push(W.sentence(fill(W.pick(`tail|synth|${key}`, L.tail.synth), { a: W.np(pos[0]), b: W.np(pos[1]) }), { move: 'VALUE', step: `synth:${pos[0]}|${pos[1]}`, basis: 'he_thong', concepts: [pos[0], pos[1]] }));
  return out;
}

/** Cung giáp (a named pair standing in the two neighbours), the nhị hợp palace and the lục hại palace: positions computed from the
 *  branches, said without a meaning — the books in the repository read nhị hợp only for a đại hạn (KL pp.230-233), lục hại not at all. */
function positionSentences(W: Writer, L: LuanLib, chart: ChartInput, pal: Palace): ProseSentence[] {
  const out: ProseSentence[] = [], byIdx = new Map(chart.palaces.map(p => [p.branch_index, p]));
  const left = byIdx.get((pal.branch_index + 11) % 12)!, right = byIdx.get((pal.branch_index + 1) % 12)!;
  const has = (p: Palace, s: string) => s.startsWith('Hóa ') ? chart.tu_hoa[s]?.branch === p.branch_index : p.stars.includes(s) || p.major_stars.includes(s);
  const pairs = GIAP.filter(([a, b]) => (has(left, a) && has(right, b)) || (has(left, b) && has(right, a))).map(([a, b]) => `${a} và ${b}`);
  if (pairs.length) out.push(W.sentence(fill(W.pick(`pos|giap|${pal.name}`, L.pos.giap), { pal: pal.name, pair: pairs.slice(0, 2).join(', '), left: left.name, right: right.name }),
    { move: 'ANCHOR', step: 'position:giap', basis: 'tinh_toan' }));
  const brief = (p: Palace) => {
    const c = palaceConfig(chart, p);
    const xs = [...c.majors, ...c.sat.slice(0, 1), ...c.cat.slice(0, 1)];
    return xs.length ? `, có ${joinVi(xs)}` : ', vô chính diệu';
  };
  const nh = byIdx.get((13 - pal.branch_index) % 12)!, lh = byIdx.get((19 - pal.branch_index) % 12)!;
  out.push(W.sentence(fill(W.pick(`pos|nh|${pal.name}`, L.pos.nhi_hop), { pal: pal.name, branch: pal.branch, other: nh.branch, opal: nh.name, stars: brief(nh) }), { move: 'ANCHOR', step: 'position:nhi_hop', basis: 'tinh_toan' }));
  if (lh !== nh) out.push(W.sentence(fill(W.pick(`pos|lh|${pal.name}`, L.pos.luc_hai), { branch: pal.branch, other: lh.branch, opal: lh.name, stars: brief(lh) }), { move: 'ANCHOR', step: 'position:luc_hai', basis: 'tinh_toan' }));
  return out;
}

/** Thân cư: where the Thân palace stands, what the common reading takes it to mean with the palace's domain (KL pp.233-236), the book
 *  readings that name Thân in that palace, and — as the maturity paragraph — the Thân palace's own strongest thesis, argued with the same
 *  steps (the palace's chapter then leaves that thesis out). With no thesis there and no chính tinh, the borrowed star's common reading. */
function thanSentences(W: Writer, L: LuanLib, F: ReasoningFrames, chart: ChartInput, k: Knowledge, than: Palace, sh: LuanShared, saidConcepts: Set<string>) {
  const position: ProseSentence[] = [], style: ProseSentence[] = [];
  const cfg = configClause(chart, than);
  position.push(W.sentence(fill(W.pick('than|pos', L.than.pos), { branch: than.branch, config: cfg.text }), { move: 'ANCHOR', step: `than:${than.name}`, basis: 'tinh_toan', cites: cfg.cites }));
  const domain = (k.reference as { lifeStages?: { domain: Record<string, string> } } | undefined)?.lifeStages?.domain?.[than.name];
  if (domain) position.push(W.sentence(fill(W.pick('than|meaning', L.than.meaning), { domain }), { move: 'TIMING', step: 'than:meaning', basis: 'pho_thong', cites: ['KL pp.233-236'] }));
  const rmap = new Map(k.rules.map(r => [r.id, r]));
  const thanRules = [...new Set(sh.findings.filter(f => f.subject === `palace:${than.name}` && rmap.get(f.ruleId)?.reviewStatus === 'verified'
    && JSON.stringify(rmap.get(f.ruleId)!.conditions).includes('"palace.is_than"')).map(f => f.ruleId))].sort();
  for (const id of thanRules.slice(0, 2)) {
    const r = W.read(id);
    if (!r.claim || sh.voiced.has(id)) continue;
    sh.voiced.add(id);
    const concepts = [...new Set(sh.resolved.filter(x => x.ruleId === id).map(x => x.concept))];
    position.push(W.sentence(fill(W.pick(`than|rule|${id}`, L.than.rule), { pal: than.name, claim: r.claim }), { move: 'ELABORATE', step: `than:rule:${id}`, rules: [id], cites: rmap.get(id)!.cites, concepts }));
  }
  // the maturity paragraph: the Thân palace's strongest thesis
  const plan = reasonPalace(chart, k, than.name, { resolved: sh.resolved, labelled: sh.labelled }, { draftFormations: sh.allowDraft });
  const spec = Object.values(PROSE_SPECS).find(s => s.palace === than.name);
  const W2 = new Writer(chart, k, plan, sh.allowDraft, { micro: sh.micro, other: spec?.bond ? k.prose!.frames.other?.[than.name] : undefined, bond: spec?.bond });
  // the strongest thesis whose first claim the Mệnh chapter has not already made
  const t0 = plan.theses.find(t => t.claims[0] && !saidConcepts.has(t.claims[0].concept));
  let np: string | null = null;
  const units: Array<{ seat?: Thesis['seat']; own: Set<string> }> = [];
  if (t0) {
    const ctx: ArgueCtx = { voiced: sh.voiced, allConcepts: new Set(), structAt: [] };
    argueThesis(W2, F, t0, undefined, [t0], style, ctx);
    for (const { t, xs, at } of ctx.structAt) xs.splice(at, 0, ...structureSentences(W2, F.structure, plan, t, style));
    if (style.length) {
      sh.told.add(`${than.name}|${t0.id}`);
      units.push({ seat: t0.seat, own: new Set(t0.claims.flatMap(c => [...c.axis.base, ...c.axis.against].filter(x => x.seat.id === t0.seat.id).map(x => x.r.concept))) });
      const c = t0.claims[0]?.concept; if (c && W2.card(c)) np = W2.np(c);
    }
  }
  if (!style.length && !than.major_stars.length) {
    const opp = chart.palaces.find(p => p.branch_index === (than.branch_index + 6) % 12)!;
    const card = (k.prose?.phoThong as { chinh?: Record<string, Record<string, { core: string }>> } | undefined)?.chinh?.[opp.major_stars[0] ?? '']?.[than.name];
    if (card) sh.colourTold.add(`${than.name}|${opp.major_stars[0]}`);
    if (card) style.push(W.sentence(fill(W.pick('than|borrow', L.than.borrow), { text: lowerSafe(card.core).replace(/\{S\}/g, () => W.S()) }), { move: 'BORROW', step: `than:borrow:${opp.major_stars[0]}`, basis: 'pho_thong' }));
  }
  return { position, style, np, units, W: W2 };
}

/** Hậu vận: the đại hạn from LATE_FROM years of age on, read by Khảo Luận's tam hợp rule (tuổi against the hạn's tam hợp, KL pp.230-233):
 *  the first two that run against the age, one that runs with it, or that none runs against it. */
function lateSentences(W: Writer, L: LuanLib, chart: ChartInput): { xs: ProseSentence[]; age: string | null; calm: boolean } {
  type Kl = { relation: string; verdict: string };
  const ds = (chart.decades ?? []).map(d => ({ d, kl: (d as unknown as { kl?: Kl }).kl })).filter(x => x.kl && x.d.age_from >= LATE_FROM && x.d.age_from <= 83);
  const xs: ProseSentence[] = [];
  if (!ds.length) return { xs, age: null, calm: false };
  const age = (d: { age_from: number; age_to: number }) => `${d.age_from}–${d.age_to}`;
  const neg = ds.filter(x => KL_NEG.has(x.kl!.relation)).slice(0, 2), pos = ds.filter(x => KL_POS.has(x.kl!.relation)).slice(0, 1);
  const verdict = (kl: Kl) => kl.verdict.replace(/:\s*/g, ', ');
  const cite = ['KL pp.230-233'];
  neg.forEach((x, i) => xs.push(W.sentence(fill(W.pick(`late|neg|${i}`, L.late.neg), { age: age(x.d), pal: x.d.palace, rel: x.kl!.relation, verdict: verdict(x.kl!) }), { move: 'TIMING', step: `late:neg:${x.d.index}`, basis: 'tinh_toan', cites: cite })));
  if (neg.length && pos.length) xs.push(W.sentence(fill(W.pick('late|pos', L.late.pos), { age: age(pos[0].d), pal: pos[0].d.palace, rel: pos[0].kl!.relation, verdict: verdict(pos[0].kl!) }), { move: 'TIMING', step: `late:pos:${pos[0].d.index}`, basis: 'tinh_toan', cites: cite }));
  if (!neg.length) xs.push(W.sentence(fill(W.pick('late|calm', L.late.calm), { age: String(LATE_FROM) }), { move: 'TIMING', step: 'late:calm', basis: 'tinh_toan', cites: cite }));
  return { xs, age: neg.length ? age(neg[0].d) : null, calm: !neg.length };
}

/** Adapter for tools/interpret/eval_distinct.ts: the luận cung Mệnh chapter of one chart. */
export const luanSaid = (facts: any, k: Knowledge) => {
  const sh = luanShared(facts, k, true);
  const o = luanChapter(facts, k, 'menh', sh);
  return { text: o?.text ?? '', sentences: (o?.paragraphs ?? []).flatMap(p => p.sentences.map(s => ({ text: s.text, concepts: s.trace.concepts, rules: s.trace.rules }))) };
};
