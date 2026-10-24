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
import type { run } from '../engine.ts';
import type { Labelled } from '../kg/lift.ts';
import type { Resolved } from '../kg/resolve.ts';
import { reasonPalace, type ReadingPlan, type Thesis } from '../reason/plan.ts';
import { courseSentences, COURSE_PALACES } from './course.ts';
import { SAT } from '../kg/atoms.ts';
import { buildLedger, verdictKey, type DomainVerdict, type Ledger, type LedgerItem } from '../reason/ledger.ts';
import type { Element } from '../reason/evidence.ts';
import type { Reading } from '../reason/adjudicate.ts';
import { Micro, finish } from './micro.ts';
import { Writer, addNote, argueThesis, foldAsides, lowerSafe, structureSentences, type ArgueCtx, type ReasoningFrames } from './narrative.ts';
import { configClause, dignityOf, hoaOn, joinVi, named, palaceConfig } from './named.ts';
import type { ProseParagraph, ProseSentence, SentenceTrace } from './realize.ts';
import { validateProse } from './validate.ts';
import { deepParagraphs } from './luan_deep.ts';
import { borrowedReadings, type Borrowed } from '../reason/borrow.ts';
import { PROSE_ORDER, PROSE_SPECS, PROSE_VERSION, infer, proseReport, seedOf, type Inference, type ProseChapter, type ProseChapterId } from './chapter.ts';

export type Topic = 'tinh_cach' | 'su_nghiep' | 'tai_loc' | 'quy_nhan' | 'quan_he' | 'duong_doi' | 'the_trang' | 'vi_tri' | 'than' | 'than_same' | 'than_style'
  | 'hau_van' | 'tong_ket' | 'tom_lai' | 'pho_thong' | 'ket_luan' | 'tai_kiem' | 'tai_giu' | 'tai_tich' | 'chan_dung' | 'dien_bien';
export interface LuanLib {
  status: string;
  lead: Record<Topic, string[]>; lead_palace: Record<string, Partial<Record<Topic, string[]>>>;
  /** one lead-in for two short neighbouring topics told as one paragraph ("su_nghiep|duong_doi") */
  lead_pair: Record<string, string[]>;
  frame: Record<'open' | 'open_pair' | 'open_vcd' | 'open_empty' | 'tp_contrast' | 'tp_add' | 'opp_contrast' | 'opp_add' | 'with' | 'tt' | 'tt_alone' | 'group' | 'group_self', string[]>;
  tail: Record<'synth' | 'advice' | 'edge', string[]>;
  than: Record<'pos' | 'meaning' | 'same' | 'rule' | 'borrow', string[]>;
  pos: Record<'giap' | 'nhi_hop' | 'luc_hai', string[]>;
  late: Record<'list' | 'pos' | 'item' | 'calm' | 'course', string[]>;
  summary: Record<'arc' | 'mature' | 'mature_same' | 'late' | 'late_calm' | 'turn' | 'close' | 'close_pos' | 'close_neg', string[]>;
  health_note: string[];
  /** Tật Ách: the cứu giải stars against the sát tinh and Hóa Kỵ of the palace (owner decision 2026-10-23: a balance, no diagnosis) */
  health_balance?: { both: string[]; lean: Record<'shield' | 'press' | 'even', string>; shield_only: string[]; press_only: string[]; tail: string[] };
  /** the course of a domain across the đại hạn (prose/course.ts) */
  course?: import('./course.ts').CourseLib;
  /** the Mệnh portrait (review 2026-10-23, point 1): strengths and weaknesses gathered, the inner conflict, the shared root */
  portrait?: Record<'both' | 'pos' | 'neg' | 'conflict' | 'conflict_same' | 'root', string[]>;
  /** the domain ledger's conclusion (reason/ledger.ts): verdict words and the sentence frames by case */
  ledger: Record<string, string[]> & { verdict: Record<string, string[]> };
  /** a limiting element of the palace no reading of the chapter faced: the structural conditional sentence, by element kind */
  confront: Record<string, string[]>;
  /** the same, for an older chapter with no reading of its own to qualify ({el}: the element) */
  confront_alone?: string[];
  /** a big conclusion resting on one minor star */
  single: string[];
  /** a verified timing reading of the palace */
  timing: string[];
}
/** A luận cung chapter: the shape of the older chapter (report.js reads either), plus a title and the plan it was argued from. */
export interface LuanChapter extends ProseChapter { title: string; luan: true; theses: string[] }

export const LUAN_VERSION = 'luan-0.2.0';
const fill = (t: string, v: Record<string, string>) => t.replace(/\{([A-Za-z_]+)\}/g, (_, key) => { if (v[key] === undefined) throw new Error(`slot {${key}} unfilled in: ${t}`); return v[key]; });
const RANK: Record<string, number> = { 'miếu': 6, 'vượng': 5, 'đắc': 4, 'lợi': 3, 'bình': 2, 'hãm': 1 };
/** pairs that flank a palace from its two neighbours (cung giáp), named as the books name them; Hóa pairs from the natal Tứ Hóa */
const GIAP: Array<[string, string]> = [['Tả Phụ', 'Hữu Bật'], ['Văn Xương', 'Văn Khúc'], ['Thiên Khôi', 'Thiên Việt'], ['Thái Dương', 'Thái Âm'], ['Tử Vi', 'Thiên Phủ'],
  ['Hóa Khoa', 'Hóa Lộc'], ['Hóa Quyền', 'Hóa Lộc'], ['Hóa Khoa', 'Hóa Quyền'], ['Kình Dương', 'Đà La'], ['Địa Không', 'Địa Kiếp'], ['Hỏa Tinh', 'Linh Tinh']];
const KL_NEG = new Set(['tuổi sinh xuất cho đại vận', 'đại vận khắc tuổi']), KL_POS = new Set(['tuổi khắc đại vận', 'đại vận sinh nhập cho tuổi']);
/** where hậu vận starts, in years of age: a convention of this system (he_thong), not a page */
const LATE_FROM = 43;
/** the last đại hạn told there starts at this age (a hạn from 83 on is left to the đại hạn chapter) */
const LATE_TO = 73;
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
  let dropped = false;
  return xs.flatMap(s => {
    // what follows a claim the report already told (its behaviour line, its one-star or Kỵ caveat) goes with it: a card line never stands alone
    if (dropped && /^(behave|single|kyc):/.test(s.trace.step ?? '')) return [];
    if (s.trace.move === 'ELABORATE') return [s];
    if (s.trace.basis !== 'sach' || !s.trace.keys?.length) { dropped = false; return [s]; }
    if (s.trace.keys.some(x => keys.has(x))) { dropped = true; return []; }
    s.trace.keys.forEach(x => keys.add(x));
    // an anaphoric claim whose antecedent was just dropped says its ground in full
    const out = dropped && s.trace.alt ? { ...s, text: s.trace.alt } : s;
    dropped = false;
    return [out];
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
  /** the report-wide domain ledger: one verdict per domain, which every chapter tells the same way */
  ledger: Ledger;
  /** domain id → the chapter that first told its conclusion (later chapters say it agrees, in brief) */
  domainsTold: Map<string, string>;
  /** the deep reading (prose/luan_deep.ts): star-nature / relation ids and minh họa concepts the report already told (each once) */
  natureSaid: Set<string>; minhSaid: Set<string>;
  /** every sentence the luận chapters told so far (the deep reading recalls, never repeats) */
  saidAll: ProseSentence[];
  /** how many times each domain's verdict was recalled after its full telling (review 2026-10-23: at most ECHO_MAX in a report) */
  echo: Map<string, number>;
  /** chapter id → verified readings of its palace the chapter does not tell, with the reason (evidence `untold`) */
  untold: Map<string, Array<{ ruleId: string; reason: string }>>;
  /** readings of the chính tinh each vô chính diệu palace borrows from its opposite palace (reason/borrow.ts): deep reading only */
  borrowed: Borrowed[];
}

export function luanShared(chart: ChartInput, k: Knowledge, allowDraft: boolean, pre?: Inference): LuanShared {
  const { findings, resolved, labelled } = pre ?? infer(chart, k);
  const seed = seedOf(chart);
  // variant choice is seeded by what the reading stands on (the chính tinh of every palace, the Tứ Hóa, the year), not by every minor star,
  // so a change the reasoning ignores does not reword the text (the reasoned chapter seeds by its plan for the same reason)
  const vseed = [chart.year_gz, chart.gender, ...chart.palaces.map(p => p.major_stars.join('+')), ...Object.entries(chart.tu_hoa).map(([h, v]) => `${h}:${v.star}`)].join('|');
  return { findings, resolved, labelled, micro: new Micro(`${vseed}|luan`, k.prose!.connectives, k.prose!.frames), voiced: new Set(), keys: new Set(), told: new Set(), seed, allowDraft,
    ledger: buildLedger(chart, k, resolved), domainsTold: new Map(), natureSaid: new Set(), minhSaid: new Set(), saidAll: [], echo: new Map(), untold: new Map(), borrowed: borrowedReadings(chart, k, resolved) };
}

/** The twelve palace chapters: the luận cung chapter where the palace's plan has something to argue, the older chapter otherwise. */
export function luanReport(chart: ChartInput, k: Knowledge, opts: { allowDraft?: boolean; deep?: boolean } = {}): ProseChapter[] {
  const allowDraft = !!opts.allowDraft;
  if (!k.prose?.luan || !(allowDraft || k.prose.luan.status === 'approved')) return proseReport(chart, k, opts);
  const pre = infer(chart, k);
  const old = proseReport(chart, k, { ...opts, pre });
  const sh = luanShared(chart, k, allowDraft, pre);
  const chs = PROSE_ORDER.map((id, i) => luanChapter(chart, k, id, sh) ?? withConfront(chart, k, id, withoutTold(old[i], sh.keys), sh));
  return echoLedger(k, chs, sh);
}

/** A domain's verdict, once told in full, is recalled at most twice in the report (review 2026-10-23: the same "còn hai mặt chưa phân xử
 *  được" in five chapters is repetition, not synthesis). True when one more recall is allowed, and counts it. */
const ECHO_MAX = 2;
const COURSE_LABEL: Record<string, string> = { 'Quan Lộc': 'đường công danh', 'Tài Bạch': 'chuyện tiền bạc', 'Phu Thê': 'đời sống hôn nhân', 'Điền Trạch': 'việc tạo dựng nhà cửa, tài sản' };
export function echoOk(sh: Pick<LuanShared, 'echo'>, domain: string): boolean {
  const n = sh.echo.get(domain) ?? 0;
  if (n >= ECHO_MAX) return false;
  sh.echo.set(domain, n + 1);
  return true;
}

/** Two chapters voicing opposite sides of a domain (one a reading the ledger counted for it, the other one against) both cite the domain's one
 *  conditional verdict: the domain's own chapter tells it in full, the other chapter says in brief that it agrees. Only conditional verdicts
 *  (có điều kiện, hai chiều, trở ngại) — a thuận domain has no contradiction to tie — and only chapters on a side the report also contradicts. */
function echoLedger(k: Knowledge, chs: ProseChapter[], sh: LuanShared): ProseChapter[] {
  const G = k.prose!.luan!.ledger;
  const said = new Set(chs.flatMap(c => c.paragraphs.flatMap(p => p.sentences.map(s => s.text))));
  const add = new Map<number, ProseSentence[]>();
  for (const v of sh.ledger.domains) {
    if (!['co_dieu_kien', 'hai_chieu', 'tro_ngai', 'chua_phan_xu', 'hai_mat', 'giam_nhe', 'nghieng_ve'].includes(v.verdict) || !sh.domainsTold.has(v.id)) continue;
    const pos = new Set(v.pos.map(x => x.ruleId)), neg = new Set(v.neg.map(x => x.ruleId));
    const sideOf = (c: ProseChapter) => {
      const rs = c.paragraphs.flatMap(p => p.sentences).filter(s => s.trace.basis === 'sach').flatMap(s => s.trace.rules);
      return { pos: rs.some(r => pos.has(r)), neg: rs.some(r => neg.has(r)), cites: c.paragraphs.some(p => p.sentences.some(s => s.trace.ledger?.domain === v.id)) };
    };
    const sides = chs.map(sideOf);
    sides.forEach((sd, i) => {
      if (sd.cites || !(sd.pos || sd.neg)) return;
      const opposed = sides.some((o, j) => j !== i && ((sd.pos && o.neg) || (sd.neg && o.pos)));
      if (!opposed || !echoOk(sh, v.id)) return;
      const vkey = verdictKey(v);
      if (!G.verdict[vkey]?.length || !G.again?.length) return;
      const P = PROSE_SPECS[chs[i].chapter as ProseChapterId]?.palace ?? chs[i].chapter;
      let text = '';
      for (let n = 0; n < G.again.length * 2 && (!text || said.has(text)); n++)
        text = finish(fill(sh.micro.pick(`lecho|${v.id}|${P}|${n}`, G.again), { domain: v.label, verdict: sh.micro.pick(`lv|${v.id}|${n}`, G.verdict[vkey]) }));
      if (said.has(text)) return;
      said.add(text); sh.micro.said(text);
      const items = [...v.pos, ...v.neg, ...v.timing, ...v.mixed];
      (add.get(i) ?? add.set(i, []).get(i)!).push({ text, trace: { move: 'VALUE', step: `ledger:${v.id}:again`, basis: 'he_thong', concepts: [],
        rules: [...new Set(items.map(x => x.ruleId))].sort(), cites: [...new Set(items.flatMap(x => x.cites))].sort(),
        ledger: { domain: v.id, verdict: v.verdict, base: v.base }, part: 5 } as SentenceTrace });
    });
  }
  return chs.map((ch, i) => {
    const xs = add.get(i);
    if (!xs) return ch;
    const paragraphs = [...ch.paragraphs, { role: 'course', sentences: xs, text: xs.map(s => s.text).join(' '), part: 5 } as ProseParagraph];
    return { ...ch, paragraphs, text: paragraphs.map(p => p.text).join('\n\n') };
  });
}

/** An older chapter (a palace with nothing to argue) still faces the limiting elements of its palace that none of its readings stands on:
 *  one structural conditional sentence each, in a paragraph of their own (frame part 4). */
function withConfront(chart: ChartInput, k: Knowledge, id: ProseChapterId, ch: ProseChapter, sh: LuanShared): ProseChapter {
  const T = k.prose!.luan!.confront_alone, P = PROSE_SPECS[id].palace;
  if (!T?.length) return ch;
  const plan = reasonPalace(chart, k, P, { resolved: sh.resolved, labelled: sh.labelled }, { draftFormations: sh.allowDraft });
  const said = new Set(ch.paragraphs.flatMap(p => p.sentences.flatMap(s => s.trace.rules)));
  const open = plan.confront.filter(c => !c.readings.some(x => said.has(x.r.ruleId)));
  if (!open.length) return ch;
  const W = new Writer(chart, k, plan, sh.allowDraft, { micro: sh.micro });
  const TB = (k.prose!.luan as LuanLib & { confront_alone_borrowed?: string[] }).confront_alone_borrowed;
  const xs = open.map(c => W.sentence(fill(W.pick(`cfa|${P}|${c.element.id}`, c.element.borrowed && TB?.length ? TB : T),
    { el: c.element.borrowed ? `${c.element.star} hãm` : elName(c.element), pal: P, from: oppName(chart, P) }),
    { move: 'TURN', step: `confront:${c.element.id}`, basis: 'he_thong', confront: [c.element.id, ...(c.element.kind === 'ky_carrier' ? ['hoa:Hóa Kỵ'] : [])], part: 4 }));
  const para: ProseParagraph = { role: 'support', sentences: xs, text: xs.map(s => s.text).join(' '), part: 4 };
  const paragraphs = [...ch.paragraphs, para];
  return { ...ch, paragraphs, text: paragraphs.map(p => p.text).join('\n\n') };
}

/** One palace in the luận cung form, or null when its plan gives nothing to argue (the caller keeps the older chapter). */
export function luanChapter(chart: ChartInput, k: Knowledge, id: ProseChapterId, sh: LuanShared): LuanChapter | null {
  const L = k.prose!.luan!, F = k.prose!.reasoning!, spec = PROSE_SPECS[id], P = spec.palace, isMenh = P === 'Mệnh';
  const pal = chart.palaces.find(p => p.name === P)!;
  const full = reasonPalace(chart, k, P, { resolved: sh.resolved, labelled: sh.labelled }, { draftFormations: sh.allowDraft });
  const plan: ReadingPlan = { ...full, theses: full.theses.filter(t => !sh.told.has(`${P}|${t.id}`)) };
  // a palace with nothing to argue in the main reading still gets its frame, its limits and its deep reading (the older chapter is kept only
  // when the deep reading has nothing either, plan 2026-10-23 P0)
  const other = spec.bond ? k.prose!.frames.other?.[P] : undefined;
  const W = new Writer(chart, k, plan, sh.allowDraft, { micro: sh.micro, other, bond: spec.bond });
  const ctx: ArgueCtx = { voiced: sh.voiced, allConcepts: new Set(), structAt: [], lockRescue: true };
  const lead = (topic: Topic, v: Record<string, string> = {}) => fill(W.pick(`lead|${P}|${topic}`, L.lead_palace[P]?.[topic] ?? L.lead[topic]), v);
  const S = (text: string, trace: Partial<SentenceTrace> & { move: SentenceTrace['move']; step: string }) => W.sentence(text, trace);

  // ---- frame ----
  const frame = frameSentences(W, L, F, chart, pal, plan);

  // ---- theses, in the reasoned chapter's order (a thesis whose rescuer is reduced elsewhere is followed by the rescuer's thesis) ----
  // a rescued thesis is argued before its rescuer's (rescue lock): the rescuer's limit is told with the rescue, not later on its own
  const ranked = [...plan.theses];
  for (const t of plan.theses.filter(t => t.rescuerCaveat)) {
    const ri = ranked.findIndex(u => u.seat.id === t.rescuerCaveat!.seat.id), ti = ranked.indexOf(t);
    if (ri >= 0 && ri < ti) { ranked.splice(ti, 1); ranked.splice(ri, 0, t); }
  }
  const order: Thesis[] = [], pending = [...ranked];
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
    caveats(W, L, t, xs, P, sh.keys);
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
      const thanRule = !isMenh && JSON.stringify(W.rule(x.r.ruleId)?.conditions ?? {}).includes('"palace.is_than"');
      const s = S(thanRule ? fill(W.pick(`than|rule|${x.r.ruleId}`, L.than.rule), { pal: P, claim: r.claim })
        : fill(W.pick(late ? 'late|course' : 'course', late ? L.late.course : F.course), { ground: W.ground(x), claim: r.claim }),
        { move: 'EXTRA', step: `course:${plan.course.axis.key}`, concepts: [x.r.concept], rules: [x.r.ruleId], cites: x.r.cites, keys: [`${x.r.concept}@${P}`] });
      // the next sentence of the same book entry, on the same reading (TH p.75: "… muộn công danh. Nếu có Cát tinh hội cũng phải ngoài 40
      // tuổi …"): told right after it, in the book's own words, rather than dropped as a second rule of the same concept
      const more = late ? undefined : plan.course.axis.base.filter(y => y.r.ruleId !== x.r.ruleId && y.r.concept === x.r.concept && y.r.subject === x.r.subject
        && y.r.cites[0] === x.r.cites[0] && !sh.voiced.has(y.r.ruleId) && W.rule(y.r.ruleId)?.reviewStatus === 'verified')
        .map(y => ({ y, claim: W.read(y.r.ruleId).claim })).find(o => o.claim && o.claim !== r.claim);
      const xs = [s];
      if (more) {
        sh.voiced.add(more.y.r.ruleId);
        xs.push(S(more.claim!.charAt(0).toLocaleUpperCase('vi') + more.claim!.slice(1),
          { move: 'ELABORATE', step: `course:${plan.course.axis.key}:more`, concepts: [more.y.r.concept], rules: [more.y.r.ruleId], cites: more.y.r.cites, keys: [`${more.y.r.concept}@${P}|${more.y.r.ruleId}`] }));
      }
      if (late) lateCourse = s; else units.push({ topic: 'duong_doi', xs, own: new Set() });
    }
  }
  // ---- the palace's verified timing readings (rel.timing, career.late, …): told, never left as a mere course line ----
  for (const x of plan.timings) {
    // one sentence per timing concept: a second rule saying the same thing ("thời trẻ nhiều vất vả" twice) is not told again
    if (sh.voiced.has(x.r.ruleId) || ctx.allConcepts.has(x.r.concept) || units.filter(u => u.xs.some(s => s.trace.step?.startsWith('timing:'))).length >= 2) continue;
    const r = W.read(x.r.ruleId);
    if (!r.claim) continue;
    sh.voiced.add(x.r.ruleId); ctx.allConcepts.add(x.r.concept);
    const isThan = JSON.stringify(W.rule(x.r.ruleId)?.conditions ?? {}).includes('"palace.is_than"');
    const text = isThan ? fill(W.pick(`than|rule|${x.r.ruleId}`, L.than.rule), { pal: P, claim: r.claim }) : fill(W.pick(`timing|${x.r.ruleId}`, L.timing), { ground: plainGround(W, x, P), claim: r.claim });
    units.push({ topic: topicOf(W.concept(x.r.concept), P), own: new Set([x.r.concept]), xs: [S(text,
      { move: 'TIMING', step: `timing:${x.r.ruleId}`, concepts: [x.r.concept], rules: [x.r.ruleId], cites: x.r.cites, keys: [`${x.r.concept}@${P}|${x.r.ruleId}`], part: 2 })] });
  }
  // ---- every limiting element of the palace is faced: by a reading the chapter tells, else by a verified reading standing on it, else by a
  // structural conditional sentence (the element's position, and that the good readings of the palace hold only on condition) ----
  const mainTopic = units[0]?.topic ?? (plan.theses[0] ? thesisTopic(W, plan.theses[0], P) : 'duong_doi');
  for (const c of plan.confront) {
    const ids = new Set(c.readings.map(x => x.r.ruleId));
    const faced = (xs: ProseSentence[]) => xs.some(s => s.trace.rules.some(r => ids.has(r)) || (s.trace.confront ?? []).includes(c.element.id));
    if (faced(units.flatMap(u => u.xs))) continue;
    const x = c.readings.find(y => !sh.voiced.has(y.r.ruleId) && W.read(y.r.ruleId).claim && W.pol(y.r.concept) !== '+');
    if (x) {
      const r = W.read(x.r.ruleId);
      sh.voiced.add(x.r.ruleId); ctx.allConcepts.add(x.r.concept);
      units.push({ topic: topicOf(W.concept(x.r.concept), P), own: new Set([x.r.concept]), xs: [S(fill(W.pick(`mod|${x.r.ruleId}`, F.modifier), { conn: W.limitConn(`cf|${x.r.ruleId}`), ground: plainGround(W, x, P), claim: r.claim! }),
        { move: 'TURN', step: `confront:${c.element.id}`, concepts: [x.r.concept], rules: [x.r.ruleId], cites: x.r.cites, keys: [`${x.r.concept}@${P}|${x.r.ruleId}`], confront: [c.element.id], part: 4 })] });
      continue;
    }
    const tpl = confrontTpl(L, c.element);
    if (!tpl?.length) continue;
    units.push({ topic: mainTopic, own: new Set(), xs: [S(fill(W.pick(`cf|${P}|${c.element.id}`, tpl), { star: c.element.star ?? '', pal: P, from: oppName(chart, P) }),
      { move: 'TURN', step: `confront:${c.element.id}`, basis: 'he_thong', confront: [c.element.id, ...(c.element.kind === 'ky_carrier' ? ['hoa:Hóa Kỵ'] : [])], part: 4 })] });
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
    // a method sentence (a caveat, a structure with no reading) is the note of the reading next to it, not a sentence of the text
    let xs = foldAsides(dedupe(xs0, sh.keys), paras.at(-1)?.sentences.at(-1));
    // a paragraph of the system's words alone stands only as the closing
    if (!xs.length || (!xs.some(s => s.trace.basis !== 'he_thong') && topic !== 'tong_ket' && topic !== 'tom_lai' && !xs.some(s => s.trace.ledger))) return null;
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
  let thanNp: string | null = null, thanPal: Palace | null = null, lateAge: string | null = null, lateCalm = false, thanAlone: ProseSentence[] = [];
  if (isMenh) {
    // cung giáp, nhị hợp, lục hại are positions the books in the repository give no natal reading: notes on the frame, not a paragraph
    const vt = positionSentences(W, L, chart, pal), frameEnd = paras[0]?.sentences.at(-1);
    if (vt.length && frameEnd) addNote(frameEnd, withLead(lead('vi_tri'), vt.map(s => s.text).join(' ')));
    const than = chart.palaces.find(p => p.is_than) ?? pal;
    thanPal = than;
    if (than === pal) thanAlone = [S(W.pick('than|same', L.than.same), { move: 'ANCHOR', step: 'than:same', basis: 'tinh_toan' })];
    else {
      const r = thanSentences(W, L, F, chart, k, than, sh, new Set(paras.flatMap(p => p.sentences.flatMap(s => s.trace.concepts))));
      thanNp = r.np;
      // where Thân stands is not a paragraph of its own that ends on a position: it opens the paragraph of what the Thân palace brings
      // (its strongest thesis), or, with nothing read there, the hậu vận paragraph
      if (r.style.length) {
        const st = [{ ...r.style[0], text: withLead(lead('than_style'), r.style[0].text, names) }, ...r.style.slice(1)];
        para('support', 'than', [...r.position, ...st], lead('than', { pal: than.name }), ys => tail(r.W, L, ys, r.units, `than|${than.name}`));
      } else if (r.position.length > 1) para('support', 'than', r.position, lead('than', { pal: than.name }));
      else thanAlone = r.position;
    }
    const late = lateSentences(W, L, chart);
    lateAge = late.age; lateCalm = late.calm;
    const lx = [...late.xs, ...(lateCourse ? [lateCourse] : [])];
    // Thân an tại Mệnh, or a Thân palace with nothing read there: one sentence, said at the head of the hậu vận paragraph
    const thanLead = than === pal ? lead('than_same') : lead('than', { pal: than.name }), thanTopic = than === pal ? 'than_same' : 'than';
    if (thanAlone.length && lx.length) {
      lx[0] = { ...lx[0], text: withLead(lead('hau_van'), lx[0].text, names) };
      para('course', thanTopic, [...thanAlone, ...lx], thanLead);
    } else {
      if (thanAlone.length) para('support', thanTopic, thanAlone, thanLead);
      if (lx.length) para('course', 'hau_van', lx, lead('hau_van'));
    }
  } else if (lateCourse) para('course', 'duong_doi', [lateCourse], lead('duong_doi'));

  // a limit whose facing sentence the report had already told elsewhere (dropped above as a repeat) is faced here by its structural sentence
  for (const c of plan.confront) {
    const ids = new Set(c.readings.map(x => x.r.ruleId)), all = paras.flatMap(p => p.sentences);
    if (all.some(s => s.trace.rules.some(r => ids.has(r)) || (s.trace.confront ?? []).includes(c.element.id))) continue;
    const tpl = confrontTpl(L, c.element);
    if (!tpl?.length) continue;
    // with no reading paragraph left, the limits get a paragraph of their own (it then stands before the conclusion)
    let host = [...paras].reverse().find(p => p.role !== 'structure');
    if (!host) { host = { role: 'support', sentences: [], text: '', topic: mainTopic }; paras.push(host); }
    host.sentences.push(S(fill(W.pick(`cf2|${P}|${c.element.id}`, tpl), { star: c.element.star ?? '', pal: P, from: oppName(chart, P) }),
      { move: 'TURN', step: `confront:${c.element.id}`, basis: 'he_thong', confront: [c.element.id, ...(c.element.kind === 'ky_carrier' ? ['hoa:Hóa Kỵ'] : [])], part: 4 }));
  }

  // ---- the conditional conclusion: the domain ledger's verdict for the domains this chapter reads (Tài Bạch in three parts) ----
  // Mệnh concludes on career, read through Mệnh–Tài–Quan–Di; money is concluded, in its three parts, in the Tài Bạch chapter (a second full
  // money conclusion at Mệnh would only repeat it)
  const verdicts = (sh.ledger.byChapter[id] ?? []).filter(v => !isMenh || !v.part);
  let concluded = false;
  if (verdicts.length) {
    const parts = verdicts.filter(v => v.part);
    if (parts.length && !isMenh) for (const v of parts) {
      const xs = ledgerSentences(W, L, v, P, sh, id, paras.flatMap(p => p.sentences));
      if (xs.length) { para('course', `tai_${v.part === 'kiem' ? 'kiem' : v.part === 'giu' ? 'giu' : 'tich'}` as Topic, xs, lead(`tai_${v.part === 'kiem' ? 'kiem' : v.part === 'giu' ? 'giu' : 'tich'}` as Topic)); concluded = true; }
    }
    const xs = verdicts.filter(v => !v.part || isMenh).flatMap(v => ledgerSentences(W, L, v, P, sh, id, paras.flatMap(p => p.sentences)));
    if (xs.length) { para('course', 'ket_luan', xs, lead('ket_luan')); concluded = true; }
  }
  // Tật Ách: the stars the books call cứu giải for health (star_nature.json, health.shielded: KL pp.109, 120, 122, 140, 186) against the sát
  // tinh and Hóa Kỵ standing in the palace; which side has more is the system's count, said as such, and no health verdict follows
  if (P === 'Tật Ách' && L.health_balance) {
    const H = L.health_balance, here = new Set([...pal.stars, ...pal.major_stars, ...(pal.tuan ? ['Tuần'] : []), ...(pal.triet ? ['Triệt'] : []),
      ...Object.entries(chart.tu_hoa).filter(([, v]) => v.branch === pal.branch_index).map(([h]) => h)]);
    const shieldBy = new Map<string, string[]>();
    for (const e of k.kg?.starNature?.entries ?? []) if (e.explains?.includes('health.shielded')) for (const st of [e.star, ...(e.also ?? [])]) if (here.has(st)) (shieldBy.get(st) ?? shieldBy.set(st, []).get(st)!).push(`KL p.${e.page}`);
    const kyHere = Object.entries(chart.tu_hoa).some(([h, v]) => h === 'Hóa Kỵ' && v.branch === pal.branch_index);
    const shield = [...shieldBy.keys()];
    // a hãm chính tinh that is not itself a cứu giải star weighs on the palace too (evidence.ts: major_ham is a limit)
    const hamMajors = pal.major_stars.filter(st => pal.major_dignity?.[st] === 'hãm' && !shieldBy.has(st)).map(st => `${st} hãm`);
    const press = [...SAT.filter(st => here.has(st)), ...hamMajors, ...(kyHere ? ['Hóa Kỵ'] : [])];
    const cites = [...new Set([...shieldBy.values()].flat())].sort();
    const tr = (step: string) => ({ move: 'VALUE' as const, step, basis: 'he_thong' as const, concepts: [], cites, part: 5 as const,
      note: 'Sao cứu giải theo Khảo Luận (các trang ghi trong căn cứ); việc đếm hai phía là quy ước của hệ thống, không phải chẩn đoán.' });
    const xs: ProseSentence[] = [];
    if (shield.length && press.length) {
      const lean = H.lean[shield.length > press.length ? 'shield' : shield.length < press.length ? 'press' : 'even'];
      xs.push(S(fill(W.pick('hb|both', H.both), { shield: joinVi(shield), press: joinVi(press), lean }), tr('health:balance')));
    } else if (shield.length) xs.push(S(fill(W.pick('hb|s', H.shield_only), { shield: joinVi(shield) }), tr('health:balance')));
    else if (press.length) xs.push(S(fill(W.pick('hb|p', H.press_only), { press: joinVi(press) }), tr('health:balance')));
    if (xs.length) { xs.push(S(W.pick('hb|t', H.tail), tr('health:balance_tail')));
      const host = paras.find(p => p.topic === 'ket_luan') ?? [...paras].reverse().find(p => p.role !== 'structure');
      if (host) host.sentences.push(...xs); else para('course', 'ket_luan', xs, lead('ket_luan')); }
  }
  // the domain across the đại hạn: which hạn touch the palace, at what level (review 2026-10-23: career turning points, the course of a
  // marriage told as phases, how property is built over time)
  if (COURSE_PALACES[P]) {
    const xs = courseSentences(W, chart, k, P, COURSE_LABEL[P]);
    if (xs.length) para('course', 'dien_bien', xs, lead('dien_bien'));
  }

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
  } else if (!concluded && paras.filter(p => p.lead).length >= 2) {
    const tpl = pos.length && neg.length ? L.summary.close : pos.length ? L.summary.close_pos : neg.length ? L.summary.close_neg : [];
    if (tpl.length) closing.push(S(fill(W.pick(`sum|close|${P}`, tpl), { a: pos.length ? W.np(pos[0]) : '', b: neg.length ? W.np(neg[0]) : '' }), { move: 'VALUE', step: 'closing', basis: 'he_thong' }));
    if (closing.length) para('course', 'tom_lai', closing, lead('tom_lai'));
  }
  // no phổ thông (common, unchecked) reading is told: a palace the books say little about stays short (owner's decision, 2026-10-21)
  if (P === 'Tật Ách' && paras.some(p => p.topic === 'the_trang')) paras.at(-1)!.sentences.push(S(W.pick('health', L.health_note), { move: 'VALUE', step: 'health_note', basis: 'he_thong' }));
  for (const p of paras) { p.text = p.sentences.map(s => s.text).join(' '); for (const x of p.sentences) x.trace.part ??= partOf(x);
    p.part = /^(ket_luan|tai_|tong_ket|tom_lai)/.test(p.topic ?? '') ? 5 : p.sentences[0]?.trace.part; }

  const resolvedHere = sh.resolved.filter(r => r.subject === `palace:${P}` || (isMenh && r.subject === 'chart'));
  const { issues, metrics } = validateProse(paras, resolvedHere);
  paras.forEach((p, pi) => p.sentences.forEach((s, si) => { if (!s.trace.step) issues.push({ level: 'error', code: 'no_plan_step', where: `p${pi + 1}s${si + 1}`, msg: s.text }); }));
  // ---- the deep reading ("Đọc sâu", plan DEEP-TUVI): after the short reading, never inside it; its own checks are in luan_deep.ts ----
  const mainBook = paras.flatMap(p => p.sentences).filter(s => s.trace.basis === 'sach').length;
  const deep = deepParagraphs(chart, k, id, sh, W, [...paras.flatMap(p => p.sentences), ...sh.saidAll]);
  // a main reading with no book reading of its own: the first deep sections that carry one are the main reading (the caps of the main reading
  // left nothing there; what they left goes on in the deep part)
  if (!mainBook && !concluded) {
    const lead = deep.filter(p => p.sentences.some(s => s.trace.basis === 'sach' && s.trace.rules.length)).slice(0, 2);
    for (const p of lead) { p.deep = false; p.promoted = true; }
  }
  paras.push(...deep);
  // the Mệnh portrait (review 2026-10-23): every trait the chapter told, main and deep, gathered into strengths, weaknesses, the inner conflict
  // and the star most of them come from — the system's tổng hợp of what was said, after it was said
  if (isMenh && L.portrait) {
    const xs = portrait(W, L, sh, paras.flatMap(p => p.sentences));
    // with a deep part the portrait closes it (it gathers the deep traits too); without one it closes the main reading under its lead-in
    if (xs.length) { const ld = lead('chan_dung');
      if (!deep.length) xs[0] = { ...xs[0], text: withLead(ld, xs[0].text, names) };
      paras.push({ role: 'balance', sentences: xs, text: xs.map(x => x.text).join(' '), topic: 'chan_dung', part: 5, ...(deep.length ? { deep: true, title: ld } : { lead: ld }) }); }
  }
  sh.saidAll.push(...paras.flatMap(p => p.sentences));
  const rmap = new Map(k.rules.map(r => [r.id, r]));
  const reading = (rid: string) => { const r = rmap.get(rid)!; return (r.reading ?? k.claims[r.consequences[0]?.claim ?? ''] ?? '').replace(/^(khuynh hướng|hạn chế:)\s*/, ''); };
  const ruleIds = [...new Set(paras.flatMap(p => p.sentences.flatMap(s => [...s.trace.rules, ...(s.trace.also ?? [])])))].filter(r => rmap.has(r)).sort();
  const book = paras.flatMap(p => p.sentences).filter(s => s.trace.basis === 'sach').length;
  // a chapter whose readings the report already told still gives its domain conclusion (frame and conclusion only)
  if (!book && !concluded) return null;
  return {
    engine: `${PROSE_VERSION}/${LUAN_VERSION}`, kbVersion: k.version, chapter: id, palace: P, title: `Luận cung ${P}`, luan: true, schema: 'luan', order: [],
    theses: plan.theses.map(t => t.id),
    draft: sh.allowDraft && (L.status !== 'approved' || F.status !== 'approved' || k.prose!.concepts.some(c => c.status !== 'approved')),
    paragraphs: paras, text: paras.map(p => p.text).join('\n\n'), issues, metrics, pass: !issues.some(i => i.level === 'error'),
    advice: { strengths: [], actions: [], basis: 'loi_khuyen' },
    evidence: {
      resolved: resolvedHere.map(r => ({ ruleId: r.ruleId, concept: r.concept, stance: r.stance, status: r.status, by: r.by, cites: r.cites })), tensions: [], unused: [],
      rules: Object.fromEntries(ruleIds.map(rid => [rid, { reading: reading(rid), cites: rmap.get(rid)!.cites, verified: rmap.get(rid)!.reviewStatus === 'verified' }])),
      concepts: Object.fromEntries([...new Set(paras.flatMap(p => p.sentences.flatMap(s => s.trace.concepts)))].map(c => [c, k.concepts.concepts.find(x => x.id === c)?.short ?? c])),
      divergences: [],
      // verified readings of the palace this chapter does not tell, each with its reason (plan 2026-10-23 P0: none is dropped silently)
      untold: sh.untold.get(id) ?? [],
      // the domain verdicts this chapter concludes on, with their evidence chains (part 6: shown in the chapter's Căn cứ fold)
      ledger: verdicts.map(v => ({ id: v.id, label: v.label, verdict: v.verdict, base: v.base, link: v.link ?? null, chain: v.chain,
        limits: v.limits.map(l => ({ id: l.id, palace: l.palace })) })),
    },
  };
}

/** A thesis' topic: that of its first claim with a topic of its own; a thesis of course concepts only reads as the course of life. */
function thesisTopic(W: Writer, t: Thesis, P: string): Topic {
  const flank = t.seat.scope === 'flank';
  return t.claims.map(c => topicOf(W.concept(c.concept), P, flank)).find(x => x !== 'duong_doi') ?? 'duong_doi';
}
/** An older chapter kept for a palace with nothing to argue, less the book sentences voicing a reading the luận cung chapters already told. */
function withoutTold(ch: ProseChapter, keys: Set<string>): ProseChapter {
  const paragraphs = ch.paragraphs.map(p => ({ ...p, sentences: p.sentences.filter(s => s.trace.basis !== 'sach' || !(s.trace.keys ?? []).some(x => keys.has(x))) }))
    .filter(p => p.sentences.some(s => s.trace.basis === 'sach' || s.trace.basis === 'pho_thong' || s.trace.basis === 'tinh_toan'))
    .map(p => ({ ...p, text: p.sentences.map(s => s.text).join(' ') }));
  return { ...ch, paragraphs, text: paragraphs.map(p => p.text).join('\n\n') };
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
    // which seat the reading is centred on is how it was reached: a note on the frame, not a sentence ("Cự Môn là trục của cả lá số")
    out.push(W.sentence(fill(W.pick(`centre|${why}`, F.centre[why]), { star: star || centreName, name: formName, seat: centreName }), { move: 'ANCHOR', step: `centre:${centre.id}`, basis: 'he_thong', aside: true }));
  }
  // the draft cách cục states (formations_experimental.json) are not checked against a page: not told here (the reasoned chapter keeps them)
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
  const softened = new Set(book.filter(s => s.trace.soft || s.trace.move === 'TURN').flatMap(s => s.trace.concepts));
  const strong = pos.filter(c => !softened.has(c));
  const answer = [...neg, ...reduced].find(c => W.card(c)?.mature?.length);
  if (answer) {
    const m = W.pick(`tail|mature|${answer}`, W.card(answer)!.mature!);
    // a suggestion, labelled as one ('lời khuyên chung'), naming the reading it answers: the system's advice, not something the chart says
    out.push(W.sentence(fill(W.pick(`tail|advice|${key}|${answer}`, L.tail.advice), { S: W.S(answer), mature: m, np: W.np(answer) }), { move: 'TRANSFORM', step: `advice:${answer}`, basis: 'loi_khuyen', concepts: [answer],
      note: 'Gợi ý của hệ thống rút từ nhận định vừa nêu, không phải lời phán đoán của lá số.' }));
  }
  // the two-edged image only for a strength and a limit the same star asserts (its own seat), named by that star
  const edge = units.map(u => ({ u, p: pos.find(c => u.own.has(c)), n: neg.find(c => u.own.has(c)) })).find(x => x.p && x.n && x.u.seat?.star && x.u.seat.kind !== 'hoa');
  if (edge)
    out.push(W.sentence(fill(W.pick(`tail|edge|${key}`, L.tail.edge), { a: W.np(edge.p!), b: W.np(edge.n!), seat: edge.u.seat!.star! }), { move: 'VALUE', step: `edge:${edge.p}|${edge.n}`, basis: 'he_thong', concepts: [edge.p!, edge.n!] }));
  // two strengths set side by side only when both were told plainly: a softened claim means the two do not simply 'go one way'
  else if (!neg.length && !answer && strong.length >= 2)
    out.push(W.sentence(fill(W.pick(`tail|synth|${key}`, L.tail.synth), { a: W.np(strong[0]), b: W.np(strong[1]) }), { move: 'VALUE', step: `synth:${strong[0]}|${strong[1]}`, basis: 'he_thong', concepts: [strong[0], strong[1]] }));
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
  // a partner palace is named only when it holds something that weighs (a natal Hóa, Lộc Tồn, a sát tinh): the selection is this system's
  const SAT6 = ['Kình Dương', 'Đà La', 'Địa Không', 'Địa Kiếp', 'Hỏa Tinh', 'Linh Tinh'];
  const weighs = (p: Palace) => Object.values(chart.tu_hoa).some(h => h.branch === p.branch_index) || p.stars.some(x => x === 'Lộc Tồn' || SAT6.includes(x));
  if (weighs(nh)) out.push(W.sentence(fill(W.pick(`pos|nh|${pal.name}`, L.pos.nhi_hop), { pal: pal.name, branch: pal.branch, other: nh.branch, opal: nh.name, stars: brief(nh) }), { move: 'ANCHOR', step: 'position:nhi_hop', basis: 'tinh_toan' }));
  if (lh !== nh && weighs(lh)) out.push(W.sentence(fill(W.pick(`pos|lh|${pal.name}`, L.pos.luc_hai), { pal: pal.name, branch: pal.branch, other: lh.branch, opal: lh.name, stars: brief(lh) }), { move: 'ANCHOR', step: 'position:luc_hai', basis: 'tinh_toan' }));
  return out;
}

/** Thân cư: where the Thân palace stands, what the common reading takes it to mean with the palace's domain (KL pp.233-236), the book
 *  readings that name Thân in that palace, and — as the maturity paragraph — the Thân palace's own strongest thesis, argued with the same
 *  steps (the palace's chapter then leaves that thesis out). With no thesis there and no chính tinh, the borrowed star's common reading. */
function thanSentences(W: Writer, L: LuanLib, F: ReasoningFrames, chart: ChartInput, k: Knowledge, than: Palace, sh: LuanShared, saidConcepts: Set<string>) {
  const position: ProseSentence[] = [], style: ProseSentence[] = [];
  const cfg = configClause(chart, than);
  position.push(W.sentence(fill(W.pick('than|pos', L.than.pos), { branch: than.branch, config: cfg.text }), { move: 'ANCHOR', step: `than:${than.name}`, basis: 'tinh_toan', cites: cfg.cites }));
  const rmap = new Map(k.rules.map(r => [r.id, r]));
  const thanRules = [...new Set(sh.findings.filter(f => f.subject === `palace:${than.name}` && rmap.get(f.ruleId)?.reviewStatus === 'verified'
    && JSON.stringify(rmap.get(f.ruleId)!.conditions).includes('"palace.is_than"')).map(f => f.ruleId))].sort();
  for (const id of thanRules.slice(0, 2)) {
    const r = W.read(id);
    if (!r.claim || sh.voiced.has(id)) continue;
    // a timing reading of the Thân palace ("công danh đến muộn") is told in that palace's own chapter, with its domain's conclusion
    if (sh.resolved.some(x => x.ruleId === id && /\.timing$/.test(W.concept(x.concept)?.facet ?? ''))) continue;
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
    const ctx: ArgueCtx = { voiced: sh.voiced, allConcepts: new Set(), structAt: [], lockRescue: true };
    argueThesis(W2, F, t0, undefined, [t0], style, ctx);
    for (const { t, xs, at } of ctx.structAt) xs.splice(at, 0, ...structureSentences(W2, F.structure, plan, t, style));
    if (style.length) {
      sh.told.add(`${than.name}|${t0.id}`);
      units.push({ seat: t0.seat, own: new Set(t0.claims.flatMap(c => [...c.axis.base, ...c.axis.against].filter(x => x.seat.id === t0.seat.id).map(x => x.r.concept))) });
      const c = t0.claims[0]?.concept; if (c && W2.card(c)) np = W2.np(c);
    }
  }
  return { position, style, np, units, W: W2 };
}

/** Hậu vận: the đại hạn from LATE_FROM years of age on, by Khảo Luận's tam hợp rule (tuổi against the hạn's tam hợp, KL pp.230-233), in one
 *  sentence: the hạn that run against the age (sinh xuất, bị khắc) and those that run with it (khắc được, được sinh); or that none runs
 *  against it. Each hạn is told in full in the đại hạn chapter (vanhan.ts), with the verdict's words. */
function lateSentences(W: Writer, L: LuanLib, chart: ChartInput): { xs: ProseSentence[]; age: string | null; calm: boolean } {
  type Kl = { relation: string; verdict: string };
  const ds = (chart.decades ?? []).map(d => ({ d, kl: (d as unknown as { kl?: Kl }).kl })).filter(x => x.kl && x.d.age_from >= LATE_FROM && x.d.age_from <= LATE_TO);
  if (!ds.length) return { xs: [], age: null, calm: false };
  const age = (d: { age_from: number; age_to: number }) => `${d.age_from}–${d.age_to}`;
  const item = (x: typeof ds[number], i: number) => fill(W.pick(`late|item|${i}`, L.late.item), { age: age(x.d), pal: x.d.palace });
  const neg = ds.filter(x => KL_NEG.has(x.kl!.relation)).slice(0, 3), pos = ds.filter(x => KL_POS.has(x.kl!.relation)).slice(0, 2);
  const cite = ['KL pp.230-233'];
  const text = neg.length
    ? fill(W.pick('late|list', L.late.list), { neg: joinVi(neg.map(item)), pos: pos.length ? fill(W.pick('late|pos', L.late.pos), { list: joinVi(pos.map((x, i) => item(x, i + 5))) }) : '' })
    : fill(W.pick('late|calm', L.late.calm), { age: String(LATE_FROM) });
  return { xs: [W.sentence(text, { move: 'TIMING', step: 'late:tam_hop', basis: 'tinh_toan', cites: cite })], age: neg.length ? age(neg[0].d) : null, calm: !neg.length };
}

/** Adapter for tools/interpret/eval_distinct.ts: the luận cung Mệnh chapter of one chart. */
export const luanSaid = (facts: any, k: Knowledge) => {
  const sh = luanShared(facts, k, true);
  const o = luanChapter(facts, k, 'menh', sh);
  // the main reading only: the deep reading holds, by design, the common readings the main reading's Barnum filter demoted (plan 2026-10-23)
  const ps = (o?.paragraphs ?? []).filter(p => !p.deep);
  return { text: ps.map(p => p.text).join('\n\n'), sentences: ps.flatMap(p => p.sentences.map(s => ({ text: s.text, concepts: s.trace.concepts, rules: s.trace.rules }))) };
};

/** The frame part of a sentence by what it does: the palace's structure (1), a reading for or against (2), how elements act on each other —
 *  tam phương, structures, Thân (3), a limit faced or a contradiction explained (4), the conclusion and the closing (5). */
function partOf(x: ProseSentence): 1 | 2 | 3 | 4 | 5 {
  const st = x.trace.step ?? '', m = x.trace.move;
  if (x.trace.ledger || /^(closing|sum|advice|edge|synth|health_note)/.test(st) || m === 'VALUE' || m === 'TRANSFORM') return 5;
  if (/^(frame|centre|position|than:same)/.test(st)) return 1;
  if (/^(confront|kyc|single|contested|against|reducer|caveat)/.test(st) || m === 'TURN' || m === 'TENSION') return 4;
  if (/^(structure|corroborated|countered|bridge|than|late|formation)/.test(st) || m === 'VIA') return 3;
  return 2;
}

/** After a thesis is argued: a big conclusion resting on one minor star is said to be only that star's suggestion, and a strength resting on a
 *  star that carries Hóa Kỵ is never left as a plain positive (plan.ts Claim.single / kyCarrier). */
const kySaid = new WeakMap<Writer, Set<string>>();
function caveats(W: Writer, L: LuanLib, t: Thesis, xs: ProseSentence[], P: string, told: Set<string>): void {
  const said = kySaid.get(W) ?? kySaid.set(W, new Set()).get(W)!;
  for (const c of t.claims) {
    // the claim sentence of this concept: its own, or the sentence of a sibling concept whose rule words already said it (narrative.ts)
    const at = xs.findIndex(s => s.trace.step === `claim:${t.id}:${c.concept}` || ((s.trace.step ?? "").startsWith(`claim:${t.id}:`) && s.trace.concepts.includes(c.concept)));
    if (at < 0) continue;
    const add: ProseSentence[] = [];
    if (c.kyCarrier && !said.has(c.kyCarrier) && said.add(c.kyCarrier)) add.push(W.sentence(fill(W.pick(`kyc|${P}|${c.kyCarrier}`, L.confront.ky_carrier), { star: c.kyCarrier, pal: P }),
      { move: 'TURN', step: `kyc:${t.id}:${c.concept}`, basis: 'he_thong', confront: [`cat:${c.kyCarrier}`, `major:${c.kyCarrier}`, 'hoa:Hóa Kỵ'], part: 4 }));
    // one minor star: unless the thesis goes on to tell another palace saying the same thing
    // (a corroboration an earlier chapter already told is dropped from this one by dedupe, so it does not count)
    if (c.single?.length && !(xs[at + 1]?.trace.step ?? "").startsWith("single:") && !(xs[at + 2]?.trace.step ?? "").startsWith("single:") && !xs.some(s => s.trace.step?.startsWith('corroborated:') && s.trace.concepts.includes(c.concept) && !(s.trace.keys ?? []).some(x => told.has(x)))) add.push(W.sentence(fill(W.pick(`single|${P}|${t.id}`, L.single), { stars: joinVi(c.single) }),
      { move: 'TURN', step: `single:${t.id}:${c.concept}`, basis: 'he_thong', part: 4 }));
    // after the claim and its behaviour line
    const after = xs[at + 1]?.trace.step?.startsWith('behave:') ? at + 2 : at + 1;
    xs.splice(after, 0, ...add);
  }
}

/** the palace a borrowed chính tinh stands in (the opposite palace) */
const oppName = (chart: ChartInput, P: string) => { const p = chart.palaces.find(x => x.name === P)!; return chart.palaces.find(x => x.branch_index === (p.branch_index + 6) % 12)!.name; };
/** the confront frames of an element: a hãm chính tinh the palace only borrows has its own frames, which say where it stands */
const confrontTpl = (L: LuanLib, e: Element) => e.borrowed && e.kind === 'major_ham' && L.confront.major_ham_borrowed?.length ? L.confront.major_ham_borrowed : L.confront[e.kind];
const elName = (e: Element) => e.kind === 'tuan' ? 'Tuần' : e.kind === 'triet' ? 'Triệt' : e.kind === 'ky_carrier' ? `${e.star} hóa Kỵ${e.borrowed ? ' (mượn từ cung đối)' : ''}`
  : e.kind === 'hoa_ky' ? `Hóa Kỵ` : e.kind === 'major_ham' ? `${e.star} hãm${e.borrowed ? ' (mượn từ cung đối)' : ''}` : e.star ?? e.id;

/** The ledger's conclusion for one domain, as this chapter tells it: the contradiction and what ties it (part 4) when both sides stand, then
 *  the conditional verdict (part 5). A domain an earlier chapter concluded is said to agree, in brief. Basis he_thong: the words are the
 *  system's; the readings they gather are in the trace (rules, cites) and were told with their grounds in the chapters. */
function ledgerSentences(W: Writer, L: LuanLib, v: DomainVerdict, P: string, sh: LuanShared, chapter: string, said: ProseSentence[]): ProseSentence[] {
  const G = L.ledger;
  const vkey = verdictKey(v);
  const verdictWords = G.verdict[vkey] ? W.pick(`lv|${v.id}`, G.verdict[vkey]) : '';
  const rules = [...new Set([...v.pos, ...v.neg, ...v.timing, ...v.mixed].map(x => x.ruleId))].sort();
  const cites = [...new Set([...v.pos, ...v.neg, ...v.timing, ...v.mixed].flatMap(x => x.cites))].sort();
  const tr = (part: 4 | 5, step: string) => ({ move: 'VALUE' as const, step, basis: 'he_thong' as const, rules, cites, concepts: [], ledger: { domain: v.id, verdict: v.verdict, base: v.base }, part });
  if (v.verdict === 'chua_du' && !(v.limits.length && v.supports.length)) return [];
  // the full conclusion goes to the first chapter that voiced one of the domain's readings (it then explains what it said), or to the
  // domain's home chapter; every other chapter says, in brief, that it agrees
  const ids = new Set([...v.pos, ...v.neg, ...v.timing, ...v.mixed].map(x => x.ruleId));
  const voicedHere = said.some(s => s.trace.basis === 'sach' && s.trace.rules.some(r => ids.has(r)));
  const first = sh.domainsTold.get(v.id) ?? (voicedHere || v.home === chapter || !v.home ? undefined : 'later');
  if (first && first !== chapter) {
    if (!verdictWords || sh.domainsTold.get(`${v.id}|again`) === chapter || !echoOk(sh, v.id)) return [];
    if (first !== 'later') sh.domainsTold.set(`${v.id}|again`, chapter);
    return [W.sentence(fill(W.pick(`lagain|${v.id}|${P}`, G.again), { domain: v.label, verdict: verdictWords }), tr(5, `ledger:${v.id}:again`))];
  }
  sh.domainsTold.set(v.id, chapter);
  // the item that stands for a side: the domain's own subject first (its first facet), then the core palace, then the more fundamental seat
  const fi = (x: LedgerItem) => { const f = W.concept(x.concept)?.facet ?? ''; const i = v.facets.findIndex(y => f === y || f.startsWith(y + '.')); return i < 0 ? 99 : i; };
  const core = v.limits[0]?.palace ?? v.supports[0]?.palace;
  const best = (xs: LedgerItem[]) => [...xs].sort((a, b) => fi(a) - fi(b) || Number(b.palace === core) - Number(a.palace === core) || a.seat.tier - b.seat.tier || b.rarity - a.rarity || (a.ruleId < b.ruleId ? -1 : 1))[0];
  const np = (x?: LedgerItem) => x ? W.np(x.concept) : '';
  const bp = best(v.pos), bn = best(v.neg);
  const claimOf = (ruleId?: string) => ruleId ? W.read(ruleId).claim : null;
  const linkText = () => {
    if (v.link?.kind === 'timing') {
      const t = [...v.timing].sort((a, b) => Number(b.ruleId === v.link?.ruleId) - Number(a.ruleId === v.link?.ruleId) || Number(b.palace === core) - Number(a.palace === core) || a.seat.tier - b.seat.tier).find(x => claimOf(x.ruleId)) ?? v.timing[0];
      return claimOf(t?.ruleId) ?? np(t);
    }
    return claimOf(v.link?.ruleId) ?? '';
  };
  // a Hóa seat is named with its Hóa ("Cự Môn hóa Lộc ở cung Mệnh"): the star alone is not what the reading stands on
  const ground = (x?: LedgerItem) => x?.seat.star ? `${x.seat.star}${x.seat.kind === 'hoa' && x.seat.id.startsWith('hoa:Hóa ') ? ` hóa ${x.seat.id.slice(8)}` : ''}${x.seat.scope === 'opp' && x.seat.kind === 'major' ? ' mượn từ cung đối' : ''} ở cung ${x.palace}` : `cung ${x?.palace ?? P}`;
  // what a reading of an unresolved pair stands on: all its stars and Hóa (the rule's own condition), with the palace when they share one
  const starsGround = (x?: LedgerItem) => {
    if (!x?.at?.length) return ground(x);
    const by = new Map<string, string[]>();
    for (const a of x.at) (by.get(a.palace) ?? by.set(a.palace, []).get(a.palace)!).push(a.name);
    return joinVi([...by].sort((a, b) => Number(b[0] === x.palace) - Number(a[0] === x.palace)).map(([p, ns]) => `${joinVi(ns)} ở cung ${p}`));
  };
  const limits = joinVi([...new Set(v.limits.filter(l => !(l.kind === 'hoa_ky' && v.limits.some(m => m.kind === 'ky_carrier' && m.star === l.star))).map(elName))].slice(0, 3));
  const palace = v.limits[0]?.palace ?? P;
  const singleStars = (x?: LedgerItem) => joinVi(x?.stars.length ? x.stars : [x?.seat.star ?? `cung ${x?.palace}`]);
  const lk = v.link?.kind;
  let key: string | null = null;
  const vals: Record<string, string> = { domain: v.label, pos: np(bp), neg: np(bn), link: '', ground: '', limits, palace, stars: '', mitig: '', supports: joinVi(v.supports.map(elName)), S: W.S(), gpos: '', gneg: '', fpos: '', fneg: '' };
  const OPTIONAL = new Set(['mitig']);
  // health is never judged good or bad: with both sides, the two book readings are named and nothing is concluded (audit 2026-10-22)
  if (v.verdict === 'khong_ket_luan') { const bm = bp ?? best(v.mitig ?? []); if (!(bm && bn) || !G.health_both?.length) return []; key = 'health_both'; vals.pos = np(bm); }
  // both sides and no book sentence between them: named, with what each stands on, and left unresolved
  else if (v.verdict === 'chua_phan_xu') { key = 'chua_phan_xu'; vals.gpos = starsGround(bp); vals.gneg = starsGround(bn); }
  // both sides and the system's scale found one heavier (owner decision 2026-10-23): both named, then the heavier side and why
  else if (v.verdict === 'nghieng_ve' && v.weigh) { key = 'weighed'; vals.pos = np(v.base === '+' ? v.weigh.heavy : v.weigh.light);
    vals.neg = np(v.base === '+' ? v.weigh.light : v.weigh.heavy); vals.gpos = starsGround(v.base === '+' ? v.weigh.heavy : v.weigh.light);
    vals.gneg = starsGround(v.base === '+' ? v.weigh.light : v.weigh.heavy); }
  // two sides on different facets: both hold, each named with what it is about
  else if (v.verdict === 'hai_mat') { const fl = (L as LuanLib & { facet_label?: Record<string, string> }).facet_label ?? {}; key = 'coexist';
    vals.fpos = fl[W.concept(bp!.concept)?.facet ?? ''] ?? ''; vals.fneg = fl[W.concept(bn!.concept)?.facet ?? ''] ?? '';
    if (!vals.fpos || !vals.fneg || vals.fpos === vals.fneg) { key = 'chua_phan_xu'; vals.gpos = starsGround(bp); vals.gneg = starsGround(bn); } }
  // a limit a book relation makes lighter: still a limit, with its mitigating factor
  else if (v.verdict === 'giam_nhe') { key = 'neg_mitigated'; vals.link = claimOf(v.link?.ruleId) ?? np(v.mitig?.[0]); }
  else if (v.verdict === 'chua_du') key = 'struct_only';
  else if (v.verdict === 'hai_chieu') key = 'two_ways';
  else if (bp && bn) {
    if (lk === 'timing') { key = 'both_timing'; vals.link = linkText(); }
    else if (lk === 'book') { key = v.link?.reduces === '-' ? 'both_book_reduced' : 'both_book'; vals.link = linkText() || np(v.link?.reduces === '-' ? bp : bn);
      // the ground is the reading the book's relation narrows, not merely the strongest of its side
      vals.ground = ground(v.pos.find(x => x.ruleId === v.link?.target) ?? bp); }
    else if (v.base === '+') { key = 'both_pos'; vals.ground = ground(bp); }
    else { key = 'both_neg'; vals.ground = ground(bn); }
  } else if (bp) {
    if (lk === 'timing') { key = 'pos_timing'; vals.link = linkText(); }
    else if (lk === 'structure') key = 'pos_struct';
    else if (lk === 'single') { key = 'pos_single'; vals.stars = singleStars(bp); }
    else key = 'thuan';
  } else if (bn) {
    if (lk === 'single') { key = 'neg_single'; vals.stars = singleStars(bn); }
    else if (lk === 'timing') { key = 'neg_timing'; vals.link = linkText(); }
    else if (v.limits.some(l => !bn.stars.includes(l.star ?? ''))) { key = 'neg_struct'; vals.limits = joinVi([...new Set(v.limits.filter(l => !bn.stars.includes(l.star ?? '') && !(l.kind === 'hoa_ky' && v.limits.some(m => m.kind === 'ky_carrier' && m.star === l.star))).map(elName))]); }
    else key = 'neg';
  } else if (lk === 'timing') { key = 'timing_only'; vals.link = linkText(); }
  if (!key || !G[key]?.length || Object.entries(vals).some(([k2, x]) => !x && !OPTIONAL.has(k2) && G[key!].some(t => t.includes(`{${k2}}`)))) {
    return verdictWords ? [W.sentence(fill(W.pick(`lalone|${v.id}`, G.verdict_alone), { domain: v.label, verdict: verdictWords }), tr(5, `ledger:${v.id}`))] : [];
  }
  // a part of a domain (Tài Bạch's three parts) is told under its own lead-in ("Về đường kiếm tiền"): the main sentence names it by an
  // anaphor rather than repeating the label, and drops a second "về …" opener
  const mainVals = v.part && G.part_self?.length ? { ...vals, domain: W.pick(`lself|${v.id}`, G.part_self) } : vals;
  const mainText0 = fill(W.pick(`l|${v.id}|${key}`, G[key]), mainVals);
  const mainText = v.part ? mainText0.replace(new RegExp(`^về ${mainVals.domain},\\s*`), '') : mainText0;
  const main = W.sentence(mainText, tr(key.startsWith('both') || key === 'two_ways' || key === 'chua_phan_xu' || key === 'coexist' || key === 'health_both' || key === 'weighed' ? 4 : 5, `ledger:${v.id}:${key}`));
  const out = [main];
  if (key === 'weighed' && v.weigh && G.weigh_line?.length) {
    const why = weighWhy(W, G, v);
    if (why) out.push(W.sentence(fill(W.pick(`lw|${v.id}`, G.weigh_line), { heavy: np(v.weigh.heavy), light: np(v.weigh.light), why }),
      { ...tr(5, `ledger:${v.id}:weigh`), note: 'Lời tổng hợp: hai mặt đều có căn cứ, không câu sách nào xếp bên nào trên; bên nặng hơn là theo thang cân của hệ thống (chính tinh hơn phụ tinh, cung chính hơn cung tam phương, sao sáng/hãm, Tuần Triệt, số chỗ đứng).' }));
  }
  // an unresolved domain still names the limits standing in its own palace: they bound whatever the stronger side turns out to be
  if ((key === 'chua_phan_xu' || key === 'coexist' || (key === 'weighed' && v.base === '+')) && limits && (G as Record<string, string[]>).unresolved_limits?.length)
    out.push(W.sentence(fill(W.pick(`lul|${v.id}`, (G as Record<string, string[]>).unresolved_limits), { limits, palace }), tr(5, `ledger:${v.id}:limits`)));
  // the verdict, naming the limits of the core palace when the conclusion is conditional on them
  const withLimits = v.verdict === 'co_dieu_kien' && !!limits && key !== 'pos_struct' && key !== 'neg_struct';
  if ((key.startsWith('both') || key === 'two_ways' || withLimits) && verdictWords)
    out.push(W.sentence(fill(W.pick(`lverdict|${v.id}`, withLimits ? G.verdict_line_limits : G.verdict_line), { domain: v.label, verdict: verdictWords, limits, palace }), tr(5, `ledger:${v.id}`)));
  return out;
}

/** The Mệnh portrait: the traits the chapter's book sentences told, each with the stars at Mệnh its rule stands on. Strengths and weaknesses
 *  in the chapter's order; the inner conflict is a strength and a weakness of the same facet (or, failing that, the first of each), with
 *  where each comes from; the root is a Mệnh star three or more of the traits stand on. Nothing here is new: each concept was said above. */
function portrait(W: Writer, L: LuanLib, sh: LuanShared, said: ProseSentence[]): ProseSentence[] {
  const F = L.portrait!, out: ProseSentence[] = [];
  const book = said.filter(s => s.trace.basis === 'sach');
  const starsOf = new Map<string, string[]>();
  for (const s of book) for (const c of s.trace.concepts) {
    if (!W.card(c) || !/^(identity|inner)\./.test(W.concept(c)?.facet ?? '') || starsOf.has(c)) continue;
    const r = sh.resolved.find(x => s.trace.rules.includes(x.ruleId) && x.concept === c && x.subject === 'palace:Mệnh');
    starsOf.set(c, [...new Set((r?.atoms ?? []).filter(a => a.kind === 'star' && a.palace === 'Mệnh').map(a => a.name))]);
  }
  const cs = [...starsOf.keys()], pos = cs.filter(c => W.pol(c) === '+'), neg = cs.filter(c => W.pol(c) === '-');
  if (pos.length + neg.length < 2) return out;
  const tr = (step: string, concepts: string[]) => ({ move: 'VALUE' as const, step, basis: 'he_thong' as const, concepts, part: 5 as const,
    note: 'Lời tổng hợp: gom các nét tính cách đã nói ở trên, không thêm nét nào mới.' });
  const list = (xs: string[]) => joinVi(xs.slice(0, 4).map(c => W.np(c)));
  const key = pos.length && neg.length ? 'both' : pos.length ? 'pos' : 'neg';
  out.push(W.sentence(fill(W.pick(`por|${key}`, F[key]), { S: W.S(), pos: list(pos), neg: list(neg) }), tr('portrait:sides', [...pos.slice(0, 4), ...neg.slice(0, 4)])));
  const ground = (c: string) => starsOf.get(c)?.length ? `${joinVi(starsOf.get(c)!)} ở Mệnh` : '';
  const facet = (c: string) => W.concept(c)?.facet ?? '';
  const pair = pos.flatMap(p => neg.map(n => ({ p, n }))).sort((a, b) => Number(facet(b.p) === facet(b.n)) - Number(facet(a.p) === facet(a.n)))
    .find(x => ground(x.p) && ground(x.n));
  if (pair) {
    const same = ground(pair.p) === ground(pair.n);
    out.push(W.sentence(fill(W.pick(`por|cf`, same ? F.conflict_same : F.conflict), { p: W.np(pair.p), n: W.np(pair.n), gp: ground(pair.p), gn: ground(pair.n) }), tr('portrait:conflict', [pair.p, pair.n])));
  }
  const count = new Map<string, string[]>();
  for (const [c, ss] of starsOf) for (const st of ss) (count.get(st) ?? count.set(st, []).get(st)!).push(c);
  const root = [...count].filter(([, xs]) => xs.length >= 3).sort((a, b) => b[1].length - a[1].length || (a[0] < b[0] ? -1 : 1))[0];
  if (root) out.push(W.sentence(fill(W.pick('por|root', F.root), { star: root[0], list: joinVi(root[1].slice(0, 4).map(c => W.np(c))) }), tr('portrait:root', root[1].slice(0, 4))));
  return out;
}

/** Why the heavier side of a weighed domain weighs more, in at most two reasons (the scale's own order). */
function weighWhy(W: Writer, G: LuanLib['ledger'], v: DomainVerdict): string {
  const F = (G as unknown as { weigh_why?: Record<string, string[]> }).weigh_why ?? {};
  const xs = v.weigh!.why.slice(0, 2).map((r, i) => {
    const k = r.kind === 'dignity' ? (r.dignity === 'hãm' ? 'dignity_ham' : 'dignity_bright') : r.kind === 'tier' && !r.other ? 'tier_bare' : r.kind;
    return F[k]?.length ? fill(W.pick(`lww|${v.id}|${i}`, F[k]), { star: r.star ?? '', other: r.other ?? '', dignity: r.dignity ?? '', palace: r.palace ?? '', n: String(r.n ?? '') }) : '';
  }).filter(Boolean);
  return xs.length > 1 ? `${xs[0]}, thêm nữa ${xs[1]}` : xs[0] ?? '';
}

/** The ground of a reading named plainly: its stars in the palace, with the brightness only when the rule itself turned on it (a reading of
 *  "Vũ Khúc ở Tật Ách" is not grounded on "Vũ Khúc hãm"). */
function plainGround(W: Writer, x: Reading, P: string): string {
  if (x.r.atoms.some(a => a.kind === 'dignity') || x.seat.kind !== 'major') return W.ground(x);
  const stars = [...new Set(x.r.atoms.filter(a => a.kind === 'star' && a.palace === P).map(a => a.name))];
  return stars.length ? `${joinVi(stars)} ở cung ${P}` : W.ground(x);
}
