// Narrative planner for the reasoned Mệnh chapter (plan quirky-tinkering-rabin R4). Input: the ReadingPlan (reason/plan.ts), already decided.
// Each thesis becomes one paragraph that argues: CLAIM (the chart's positions, then what the rarest rule standing on them says) → the
// reading the book gives for the same structure (behaviour, from the concept card) → BUT/UNLESS (the book's reducers, a limit from a lower
// seat, the two sides of a contested axis, the caveat on a rescuer) → corroboration or counter-evidence from Tài Bạch / Quan Lộc / Thiên Di.
// The frame (Mệnh configuration, cách cục, which seat is the centre) opens the chapter; the course line, the độ số balance and one closing
// sentence end it. Nothing is said that is not in the plan: every sentence carries the plan step it voices.
//
// Grounds are built from the trigger atoms (true chart positions), not from the rule's generic condition, so "Cự Môn ở vào thế hãm tại Tuất"
// rather than "Cự Môn hãm ở Thìn/Tuất". Claims are the rule's own reading ("claim (condition)" in 97 % of verified Tử Vi rules), cleaned;
// a reading that is not clean enough for a reader falls back to the concept card. Variant choice is seeded by the plan's content, so a change
// that does not change the reasoning does not change the text.
import type { ChartInput, Concept, Knowledge, Rule } from '../types.ts';
import { reasonMenh, type ReadingPlan, type Thesis } from '../reason/plan.ts';
import { Geo, type SeatRef } from '../reason/tiers.ts';
import type { Reading, Step } from '../reason/adjudicate.ts';
import { Micro, finish, lowerFirst } from './micro.ts';
import { ABSOLUTE, META } from './lint.ts';
import type { ProseParagraph, ProseSentence, SentenceTrace } from './realize.ts';
import { validateProse, type ProseIssue, type ProseMetrics } from './validate.ts';
import type { ConceptCard } from './types.ts';

export interface ReasoningFrames {
  status: string;
  frame: Record<'single' | 'pair' | 'vcd', string[]>; centre: Record<ReadingPlan['frame']['centre']['why'], string[]>;
  claim: string[]; claim_next: string[]; claim_card: string[]; formation: string[]; formation_plain: string[]; formation_then: Record<'+' | '-' | '~', string[]>;
  reducer: string[]; against: string[]; modifier: string[]; modifier_card: string[]; formation_state: Record<string, string[]>; contested: string[]; caveat: string[]; bridge: string[]; corroborated: string[]; countered: string[];
  behave: string[]; course: string[]; degree: Record<'up' | 'down', string[]>; closing: string[]; ground: Record<string, string[]>;
  /** counter-evidence that is better news than the claim it qualifies (a limit answered by a strength in the tam phương) */
  countered_up?: string[];
  /** special structures at Mệnh (plan.ts StructureNote): `lines` turns a verbatim structure line into reader words (regex + named groups) */
  structure: { head: Record<'sach' | 'he_thong', string[]>; limit: string[]; limit_named: string[]; rescue: string[]; rescue_named: string[]; position: string[];
    lines: Array<{ type: 'limit' | 'rescue' | 'caveat'; structure?: string; match: string; say: string[] }> };
}
export interface ReasonedChapter {
  engine: string; chapter: 'menh'; palace: 'Mệnh'; draft: boolean; plan: ReadingPlan;
  paragraphs: ProseParagraph[]; text: string; issues: ProseIssue[]; metrics: ProseMetrics; pass: boolean;
}
export const NARRATIVE_VERSION = 'narrative-0.1.0';

const fill = (t: string, v: Record<string, string>) => t.replace(/\{([A-Za-z_]+)\}/g, (_, k) => { if (v[k] === undefined) throw new Error(`slot {${k}} unfilled in: ${t}`); return v[k]; });
const PROPER = /^(Mệnh|Thân|Kình|Đà|Tuần|Triệt|Lộc|Kỵ|Khoa|Quyền|Cự|Tả|Hữu|Xương|Khúc|Khôi|Việt|Tý|Sửu|Dần|Mão|Thìn|Tỵ|Ngọ|Mùi|Dậu|Tuất|Hợi|Tứ)\b/u;
/** Lower-cases the first letter unless the clause opens with a name (a star, a palace, a branch: "Thiên Lương", "Hóa Kỵ", "Kình", "Mệnh"). */
export const lowerSafe = (s: string) => /^\p{Lu}\S*\s+\p{Lu}/u.test(s) || PROPER.test(s) ? s : lowerFirst(s);
const joinVi = (xs: string[]) => xs.length <= 1 ? (xs[0] ?? '') : xs.slice(0, -1).join(', ') + ' và ' + xs[xs.length - 1];
const fnvStr = (s: string) => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0).toString(36); };

/** A rule's reading split into its claim and its condition, cleaned for a reader; claim null when it is not fit to be voiced as is. */
export function splitReading(rule: Rule | undefined, k: Knowledge): { claim: string | null; cond: string | null } {
  if (!rule) return { claim: null, cond: null };
  const raw = (rule.reading ?? k.claims[rule.consequences[0]?.claim ?? ''] ?? '').trim();
  const m = raw.match(/^(.*?)\s*\(([^()]*)\)\s*(?:[;:].*)?$/);
  let claim = (m ? m[1] : raw).replace(/^(khuynh hướng|hạn chế:)\s*/i, '').replace(/;.*$/, '').trim();
  const cond = m ? m[2].trim() : null;
  const low = ' ' + claim.toLowerCase();
  if (!claim || claim.length > 110 || /[“”"/:()]|sách|nhận định/.test(claim) || META.some(w => low.includes(' ' + w)) || ABSOLUTE.some(w => low.includes(w))) claim = null as unknown as string;
  return { claim: claim ? lowerSafe(claim) : null, cond: cond && (cond.match(/,/g) ?? []).length < 3 && !META.some(w => (' ' + cond.toLowerCase()).includes(' ' + w)) && !/[/]/.test(cond) ? cond : null };
}

/** Options for a Writer that is not the reasoned Mệnh chapter's own: a shared variant memory (a report chain), the people a palace speaks of
 *  (Phu Thê, Nô Bộc, …: a trait not about the bond describes them, chapter.ts PROSE_SPECS.bond) and a seed key for the variant choice. */
export interface WriterOptions { micro?: Micro; other?: { first: string[]; next: string[] }; bond?: (c?: Concept) => boolean }

export class Writer {
  readonly m: Micro; readonly k: Knowledge; readonly g: Geo; readonly plan: ReadingPlan; readonly f: ReasoningFrames; private cards: Map<string, ConceptCard>;
  private cmap: Map<string, Concept>; private rmap: Map<string, Rule>; readonly chart: ChartInput; private firstS = true; private firstO = true;
  /** the palace read (plan.palace): ground frames written for Mệnh name it instead */
  readonly P: string; private o: WriterOptions;
  constructor(chart: ChartInput, k: Knowledge, plan: ReadingPlan, allowDraft: boolean, o: WriterOptions = {}) {
    this.chart = chart; this.k = k; this.plan = plan; this.P = plan.palace; this.g = new Geo(chart, plan.palace); this.f = k.prose!.reasoning!; this.o = o;
    const sig = [plan.frame.branch, ...plan.theses.map(t => t.id + ':' + t.claims.map(c => c.concept + c.axis.verdict).join(','))].join('|');
    this.m = o.micro ?? new Micro(fnvStr(sig), k.prose!.connectives, k.prose!.frames);
    const ok = (st: string) => st === 'approved' || (allowDraft && st !== 'retired');
    this.cards = new Map(k.prose!.concepts.filter(c => ok(c.status)).map(c => [c.id, c]));
    this.cmap = new Map(k.concepts.concepts.map(c => [c.id, c]));
    this.rmap = new Map(k.rules.map(r => [r.id, r]));
  }
  /** Ground frames name Mệnh; for another palace they name that palace ("Thái Dương tọa Quan Lộc ở Dần", "Tuần án ngữ cung Tài Bạch"). */
  T(xs: string[]) { return this.P === 'Mệnh' ? xs : xs.map(x => x.replace(/\bMệnh\b/g, this.P)); }
  pick(key: string, xs: string[]) { return this.m.pick(key, xs); }
  S(concept?: string): string {
    // a palace of other people (Phu Thê, Nô Bộc, …): a trait outside the bond is theirs
    if (concept && this.o.other && this.o.bond && !this.o.bond(this.cmap.get(concept))) {
      if (this.firstO) { this.firstO = false; return this.pick(`O|first|${this.P}`, this.o.other.first); }
      return this.m.subject(this.o.other.next);
    }
    if (this.firstS) { this.firstS = false; return lowerSafe(this.pick('S|first', this.k.prose!.frames.subject.first)); } return lowerSafe(this.m.subject());
  }
  concept(id: string) { return this.cmap.get(id); }
  conn(rel: Parameters<Micro['conn']>[0], key: string) { return this.m.conn(rel, key) || ''; }
  sentence(text: string, trace: Partial<SentenceTrace> & { move: SentenceTrace['move']; step: string }): ProseSentence {
    const t = finish(text.replace(/^\s*,\s*/, ''));
    this.m.said(t);
    return { text: t, trace: { concepts: [], rules: [], cites: [], basis: 'sach', ...trace } as SentenceTrace };
  }
  dig(d: string | undefined, key: string) { return d ? this.pick(`dig|${key}|${d}`, this.k.prose!.frames.dignity[d] ?? [d]) : ''; }
  rule(id: string) { return this.rmap.get(id); }
  read(id: string) { return splitReading(this.rule(id), this.k); }
  card(id: string) { return this.cards.get(id); }
  pol(id: string) { return this.cmap.get(id)?.pol ?? '~'; }
  /** A concept predicate from its card: 'dễ …' for a limit, the soft form when reduced, 'thường …' otherwise. */
  pred(concept: string, soft: boolean, key: string): string | null {
    const c = this.card(concept); if (!c) return null;
    if (soft && c.soft?.length) return this.pick(`${key}|soft|${concept}`, c.soft);
    if (this.pol(concept) === '-') return c.turn?.length ? 'dễ ' + this.pick(`${key}|turn|${concept}`, c.turn) : null;
    return c.pred?.length ? 'thường ' + this.pick(`${key}|pred|${concept}`, c.pred) : null;
  }
  np(concept: string) { return this.card(concept)?.np ?? this.cmap.get(concept)?.np ?? concept; }

  /** Chart positions a seat stands for, in words. */
  seatGround(s: SeatRef, x?: Reading): string {
    const G = this.f.ground, br = this.g.menh.branch, P = this.P, T = (xs: string[]) => this.T(xs);
    if (s.kind === 'major' && s.star) {
      if (s.scope === 'opp') return fill(this.pick(`g|borrow|${s.star}`, T(G.major_borrowed)), { star: s.star });
      const d = this.g.dignity(s.star, P);
      return d ? fill(this.pick(`g|major|${s.star}`, T(G.major)), { star: s.star, dignity: this.dig(d, s.star), branch: br })
        : fill(this.pick(`g|majorp|${s.star}`, T(G.major_plain)), { star: s.star, branch: br });
    }
    if (s.kind === 'major') return fill(this.pick('g|vcd', T(G.major_plain)), { star: `cung ${P} vô chính diệu`, branch: br }).replace(`tọa ${P} ở`, 'ở').replace(`đóng ${P} tại`, 'tại');
    if (s.kind === 'hoa' && s.hoa) {
      const c = this.g.hoaCarrier[s.hoa];
      return c?.palace === P ? fill(this.pick(`g|hoa|${s.hoa}`, T(G.hoa)), { hoa: s.hoa, star: c.star })
        : fill(this.pick(`g|hoafar|${s.hoa}`, T(G.hoa_far)), { hoa: s.hoa, star: c?.star ?? '', palace: c?.palace ?? '' });
    }
    if (s.kind === 'star' && s.star) {
      const d = this.g.dignity(s.star, P);
      return d ? fill(this.pick(`g|star|${s.star}`, T(G.star)), { star: s.star, dignity: this.dig(d, s.star) }) : fill(this.pick(`g|starp|${s.star}`, T(G.star_plain)), { star: s.star });
    }
    if (s.kind === 'tuan_triet') return fill(this.pick(`g|tt|${s.id}`, T(G.tuan_triet)), { name: s.id.slice(3) });
    if (s.kind === 'tam_phuong' && s.palace) {
      const stars = [...new Set((x?.r.atoms ?? []).filter(a => a.palace === s.palace && (a.kind === 'star' || a.kind === 'hoa')).map(a => a.name))];
      return fill(this.pick(`g|tp|${s.palace}`, T(G.tam_phuong)), { stars: joinVi(stars.length ? stars : ['các sao']), palace: s.palace });
    }
    const cond = x ? this.read(x.r.ruleId).cond : null;
    if (cond) return lowerSafe(cond);
    // a chart-level reading with no clean condition: name the chart fact it stood on
    const facts = new Set((x?.r.atoms ?? []).filter(a => a.kind === 'chart').map(a => a.name));
    const [stem, branch] = this.chart.year_gz.split(' ');
    if (facts.has('chart.year_branch')) return `tuổi ${branch}`;
    if (facts.has('chart.year_stem')) return `tuổi ${stem}`;
    if (facts.has('chart.menh_cuc_relation')) return `quan hệ giữa Cục và Mệnh (${this.chart.menh_cuc_relation})`;
    return 'thế của năm, tháng, giờ sinh';
  }
  /** The ground of one reading: its seat, plus the most fundamental other seat its rule needed. */
  ground(x: Reading): string {
    const base = this.seatGround(x.seat, x);
    const l = x.links.find(y => y.kind !== 'degree');
    if (!l) return base;
    if (x.seat.kind === 'major' && l.kind === 'hoa' && this.g.hoaCarrier[l.hoa!]?.star === x.seat.star) {
      const d = this.g.dignity(x.seat.star!, this.P);
      const tpl = this.T(d === 'hãm' ? this.f.ground.hoa_on_ham : d ? this.f.ground.hoa_on : this.f.ground.hoa_on_plain);
      return fill(this.pick(`g|hoaon|${l.id}`, tpl), { star: x.seat.star!, dignity: d ? this.dig(d, x.seat.star!) : '', branch: this.g.menh.branch, short: l.hoa!.replace(/^Hóa\s+/, '') });
    }
    // two chính tinh of Mệnh in one reading: they sit together
    if (x.seat.kind === 'major' && l.kind === 'major' && l.scope === 'self' && x.seat.scope === 'self')
      return fill(this.pick(`g|pair|${x.r.ruleId}`, this.T(this.f.ground.pair)), { a: x.seat.star!, b: l.star!, branch: this.g.menh.branch });
    // a linked star reads "… lại có Thái Tuế ở Mệnh", never "… lại có Mệnh có Thái Tuế"
    const has = `${this.P} có `, lg0 = this.seatGround(l, x), lg = lg0.startsWith(has) ? lg0.slice(has.length) + ` ở ${this.P}` : lg0;
    const contrast = x.seat.kind === 'major' && this.g.dignity(x.seat.star!, this.P) === 'hãm' && this.pol(x.r.concept) !== '-';
    return base + fill(this.pick(`g|link|${x.r.ruleId}`, contrast ? this.f.ground.link_but : this.f.ground.link_and), { link: lowerSafe(lg) });
  }
  /** Stars a reading of another palace stands on, in words ("Hóa Kỵ ở Tài Bạch"). */
  palaceGround(ruleId: string, palace: string, atoms: Reading['r']['atoms']): string {
    const stars = [...new Set(atoms.filter(a => a.palace === palace && (a.kind === 'star' || a.kind === 'hoa')).map(a => a.name))];
    return stars.length ? fill(this.pick(`g|pal|${ruleId}`, this.f.ground.palace), { stars: joinVi(stars), palace }) : `cung ${palace}`;
  }
}

/** The rarest reading of a list, preferring those the book did not weaken. */
const rarest = (xs: Reading[]) => [...xs].sort((a, b) => Number(b.r.status === 'holds') - Number(a.r.status === 'holds') || b.rarity - a.rarity || (a.r.ruleId < b.r.ruleId ? -1 : 1))[0];

export function reasonedChapter(chart: ChartInput, k: Knowledge, opts: { allowDraft?: boolean; plan?: ReadingPlan } = {}): ReasonedChapter {
  const plan = opts.plan ?? reasonMenh(chart, k, undefined, { draftFormations: !!opts.allowDraft });
  const W = new Writer(chart, k, plan, !!opts.allowDraft), F = k.prose!.reasoning!;
  const paras: Array<[ProseParagraph['role'], ProseSentence[]]> = [];
  const allConcepts = new Set<string>();
  /** rules whose own reading has been told: no reading is told twice (a rule asserting two concepts is voiced once) */
  const voiced = new Set<string>();
  const structAt: Array<{ t: Thesis; xs: ProseSentence[]; at: number }> = [];

  // ---- frame ----
  const fr = plan.frame, p1: ProseSentence[] = [];
  const majorsGround = fr.majors.map(m => `${m.star}${m.dignity ? ' ' + W.dig(m.dignity, `frame|${m.star}`) : ''}`);
  const hoaFrame = fr.majors.filter(m => m.hoa.length).map(m => `${fr.majors.length > 1 ? m.star + ' ' : ''}hóa ${m.hoa.map(h => h.replace(/^Hóa\s+/, '')).join(', ')}`);
  if (hoaFrame.length) majorsGround[majorsGround.length - 1] += fr.majors.length > 1 ? `; ${hoaFrame.join(', ')}` : `, lại ${hoaFrame[0]}`;
  const tt = [fr.tuan && 'Tuần', fr.triet && 'Triệt'].filter(Boolean) as string[];
  const frameText = fr.vcd ? fill(W.pick('frame|vcd', F.frame.vcd), { branch: fr.branch, borrowed: joinVi(fr.borrowed) || 'chính tinh' })
    : fill(W.pick(`frame|${fr.majors.length}`, fr.majors.length > 1 ? F.frame.pair : F.frame.single), { branch: fr.branch, ground: joinVi(majorsGround) })
      .replace(/\.$/, tt.length ? `; cung Mệnh có ${joinVi(tt)} án ngữ.` : '.');
  p1.push(W.sentence(frameText, { move: 'ANCHOR', step: 'frame', basis: 'he_thong' }));
  const centreSeat = fr.centre.seat;
  // the star named as the axis is the centre seat's when the centre is a chính tinh, so the opening and the closing name the same one
  const star = (fr.centre.why === 'major' && centreSeat.star) || fr.majors[0]?.star || fr.borrowed[0] || '';
  const centreName = fr.vcd ? `${joinVi(fr.borrowed)} ở cung xung chiếu` : centreSeat.kind === 'major' ? (centreSeat.star ?? star) : centreSeat.star ?? W.seatGround(centreSeat);
  const centreF = plan.theses[0]?.seat.id === centreSeat.id || fr.centre.why === 'major' || fr.centre.why === 'vcd';
  if (star || fr.vcd) {
    const formName = fr.formations.find(f => f.seat === centreSeat.id && f.kind === 'formation')?.name ?? centreName;
    p1.push(W.sentence(fill(W.pick(`centre|${fr.centre.why}`, F.centre[fr.centre.why]), { star: star || centreName, name: formName, seat: centreName }),
      { move: 'ANCHOR', step: `centre:${centreSeat.id}`, basis: 'he_thong' }));
  }
  void centreF;
  // draft cách cục states (thành / thượng / bị phá / phá được cứu): told after the centre, never twice under two names
  const norm = (x: string) => x.toLowerCase().replace(/^cách\s+/, '').trim();
  const verifiedNames = new Set(fr.formations.map(f => norm(f.name)));
  for (const st of fr.states.slice(0, 2)) {
    if ([...verifiedNames].some(v => v.includes(norm(st.name)) || norm(st.name).includes(v))) continue;
    const list = (xs: string[]) => joinVi(xs.slice(0, 2).map(x => lowerSafe(x.replace(/\s*\([^()]*\)/g, ''))));
    const v = { name: st.name, boosters: list(st.boosters), breakers: list(st.uncovered.length ? st.uncovered : st.breakers), rescuers: list(st.rescuers) };
    const tpl = (F.formation_state as Record<string, string[]>)[st.state + (st.state === 'thanh' && !st.boosters.length ? '_plain' : '')] ?? [];
    if (!tpl.length) continue;
    p1.push(W.sentence(fill(W.pick(`fstate|${st.id}`, tpl), v), { move: 'ANCHOR', step: `cach:${st.id}:${st.state}`, basis: 'he_thong', concepts: [`cach:${st.id}:${st.state}`] }));
    allConcepts.add(`cach:${st.id}:${st.state}`);
  }

  // ---- theses (a thesis whose rescuer is reduced elsewhere is followed by the thesis of that rescuer, bridged) ----
  const order: Thesis[] = [];
  const pending = [...plan.theses];
  while (pending.length) {
    const t = pending.shift()!;
    order.push(t);
    const cav = t.rescuerCaveat && pending.findIndex(u => u.seat.id === t.rescuerCaveat!.seat.id);
    if (cav !== undefined && cav >= 0) order.push(...pending.splice(cav, 1));
  }
  order.forEach((t, ti) => {
    const xs: ProseSentence[] = ti === 0 ? p1 : [];
    argueThesis(W, F, t, order[ti - 1], order, xs, { voiced, allConcepts, structAt });
    if (xs.length || t.steps.some(st => st.structure)) { if (ti === 0) paras.push(['core', xs]); else paras.push(['support', xs]); }
  });
  if (!order.length) paras.push(['core', p1]);

  // ---- modifiers: what each Hóa / sát / cát tinh / Tuần–Triệt in Mệnh adds, one grounded sentence each ----
  const mods: ProseSentence[] = [];
  for (const md of plan.modifiers) {
    const x = md.reading;
    if (voiced.has(x.r.ruleId)) continue;
    const r = W.read(x.r.ruleId), ground = W.ground(x);
    const conn = W.pol(x.r.concept) === '-' ? W.conn('contrast', `mod|${x.r.ruleId}`) : W.conn('addition', `mod|${x.r.ruleId}`);
    const p = r.claim ? null : W.pred(x.r.concept, x.r.status !== 'holds', `mod|${x.r.ruleId}`);
    const text = r.claim ? fill(W.pick(`mod|${x.r.ruleId}`, F.modifier), { conn, ground, claim: r.claim })
      : p ? fill(W.pick(`modc|${x.r.ruleId}`, F.modifier_card), { conn, ground, S: W.S(), pred: p }) : '';
    if (!text) continue;
    voiced.add(x.r.ruleId); allConcepts.add(x.r.concept);
    mods.push(W.sentence(text, { move: 'TENSION', step: `modifier:${md.seat.id}`, concepts: [x.r.concept], rules: [x.r.ruleId], cites: x.r.cites, keys: [`${x.r.concept}@Mệnh|${x.r.ruleId}`] }));
  }
  if (mods.length) paras.push(['support', mods]);

  // ---- course, độ số, closing ----
  const end: ProseSentence[] = [];
  if (plan.course) {
    const x = rarest(plan.course.axis.base), r = W.read(x.r.ruleId);
    if (r.claim && !voiced.has(x.r.ruleId)) { end.push(W.sentence(fill(W.pick('course', F.course), { ground: W.ground(x), claim: r.claim }), { move: 'EXTRA', step: `course:${plan.course.axis.key}`, concepts: [x.r.concept], rules: [x.r.ruleId], cites: x.r.cites, keys: [`${x.r.concept}@Mệnh`] })); allConcepts.add(x.r.concept); }
  }
  if (plan.degree.lean !== 'mixed') {
    const ids = plan.degree.lean === 'up' ? plan.degree.up : plan.degree.down;
    const conds = ids.map(id => W.read(id).cond).filter((c): c is string => !!c && !/ hoặc |:/.test(c)).slice(0, 3).map(lowerSafe);
    if (conds.length) end.push(W.sentence(fill(W.pick(`degree|${plan.degree.lean}`, F.degree[plan.degree.lean]), { conds: joinVi(conds) }), { move: 'DEGREE', step: `degree:${plan.degree.lean}`, concepts: ['life.degree'], rules: ids, cites: [] }));
  }
  const nps = plan.theses.flatMap(t => t.claims.slice(0, 1).map(c => W.np(c.concept)));
  if (nps.length >= 2) end.push(W.sentence(fill(W.pick('closing', F.closing), { nps: nps.some(x => x.includes(' và ')) ? nps.slice(0, -1).join(', ') + ' cùng ' + nps[nps.length - 1] : joinVi(nps), centre: centreName }), { move: 'VALUE', step: 'closing', basis: 'he_thong' }));
  if (end.length) paras.push(['course', end]);

  // ---- special structures, on the thesis paragraphs that carry them (written last, so the text before them does not move) ----
  for (const { t, xs, at } of structAt) xs.splice(at, 0, ...structureSentences(W, F.structure, plan, t, paras.flatMap(([, ys]) => ys)));

  const paragraphs: ProseParagraph[] = paras.filter(([, xs]) => xs.length).map(([role, xs]) => ({ role, sentences: xs, text: xs.map(s => s.text).join(' ') }));
  const resolved = plan.theses.flatMap(t => t.claims.flatMap(c => [...c.axis.base, ...c.axis.against, ...c.axis.reducers].map(x => x.r)));
  const { issues, metrics } = validateProse(paragraphs, resolved);
  // every sentence voices a step of the plan; concepts outside the plan may not appear
  const planConcepts = new Set([...allConcepts, 'life.degree', ...plan.theses.flatMap(t => [...t.claims.flatMap(c => [c.concept, c.axis.opp ?? '']), ...t.cross.map(x => x.concept), t.rescuerCaveat?.axis.concept ?? ''])]);
  // a structure whose caveat forbids reading 'hãm' as turned good (Cự Môn hãm gặp Hóa Lộc): no sentence but that caveat may say so
  const hamCaveat = plan.structures.some(s => /hãm biến thành tốt/.test(s.caveat));
  paragraphs.forEach((p, pi) => p.sentences.forEach((s, si) => {
    const where = `p${pi + 1}s${si + 1}`;
    if (hamCaveat && !(s.trace.step ?? '').endsWith(':caveat') && HAM_GOOD.test(s.text)) issues.push({ level: 'error', code: 'ham_turned_good', where, msg: s.text });
    if (!s.trace.step) issues.push({ level: 'error', code: 'no_plan_step', where, msg: s.text });
    for (const c of s.trace.concepts) if (!planConcepts.has(c)) issues.push({ level: 'error', code: 'outside_plan', where, msg: `${c}: ${s.text}` });
  }));
  return {
    engine: NARRATIVE_VERSION, chapter: 'menh', palace: 'Mệnh', plan,
    draft: !!opts.allowDraft && (F.status !== 'approved' || k.prose!.concepts.some(c => c.status !== 'approved')),
    paragraphs, text: paragraphs.map(p => p.text).join('\n\n'), issues, metrics, pass: !issues.some(i => i.level === 'error'),
  };
}

/** What the per-thesis argument shares with the chapter around it: the rules already voiced (none is told twice), the concepts said, and
 *  the theses whose special structures are told once the whole chapter is written (structureSentences). */
export interface ArgueCtx { voiced: Set<string>; allConcepts: Set<string>; structAt: Array<{ t: Thesis; xs: ProseSentence[]; at: number }> }
/** One thesis argued into `xs`: the bridge from the thesis before it, its cách cục, each claim (its ground and the rule's own reading, or the
 *  concept card), what it looks like in a life, the book's reducers, the other side of the axis, the rescuer's own limit, corroboration
 *  and counter-evidence from the tam phương. Every sentence voices a step of the plan. */
export function argueThesis(W: Writer, F: ReasoningFrames, t: Thesis, prev: Thesis | undefined, order: Thesis[], xs: ProseSentence[], ctx: ArgueCtx): void {
  const { voiced, allConcepts, structAt } = ctx, P = W.P;
  const bridged = !!prev?.rescuerCaveat && prev.rescuerCaveat.seat.id === t.seat.id;
  if (bridged && t.seat.hoa) xs.push(W.sentence(fill(W.pick(`bridge|${t.id}`, F.bridge), { hoa: t.seat.hoa, np: W.np(t.claims[0].concept) }), { move: 'VIA', step: `bridge:${prev.id}>${t.id}`, basis: 'he_thong' }));
  let usedFormation = false;
  for (const f of t.formations.filter(x => x.kind === 'formation')) {
    const g = W.seatGround(t.seat), name = /^(cách|nhóm)\s/i.test(f.name) ? f.name : `cách ${f.name}`;
    const txt = f.condition ? fill(W.pick(`form|${f.ruleId}`, F.formation), { ground: g, name, cond: lowerSafe(f.condition) }) : fill(W.pick(`formp|${f.ruleId}`, F.formation_plain), { ground: g, name });
    xs.push(W.sentence(txt, { move: 'ANCHOR', step: `formation:${f.ruleId}`, rules: [f.ruleId], cites: f.cites }));
    usedFormation = true;
  }
  t.claims.forEach((c, ci) => {
    const ax = c.axis;
    allConcepts.add(c.concept);
    const pool = ax.base.length ? ax.base : ax.against;
    const own = pool.filter(y => y.seat.id === t.seat.id && !voiced.has(y.r.ruleId));
    const x = rarest(own.length ? own : pool.filter(y => !voiced.has(y.r.ruleId)).length ? pool.filter(y => !voiced.has(y.r.ruleId)) : pool);
    if (!x) return;
    const rd = voiced.has(x.r.ruleId) ? { claim: null, cond: null } : W.read(x.r.ruleId);
    voiced.add(x.r.ruleId);
    const ground = W.ground(x);
    const rules = [...new Set(ax.base.map(y => y.r.ruleId))], cites = [...new Set(ax.base.flatMap(y => y.r.cites))];
    const tr = { concepts: [c.concept], rules, cites, keys: [`${c.concept}@${P}`] };
    if (ax.verdict === 'contested') {
      const b = rarest(ax.against);
      xs.push(W.sentence(fill(W.pick(`contest|${ax.key}`, F.contested), { ground_a: ground, np_a: W.np(ax.concept), ground_b: W.ground(b), np_b: W.np(ax.opp ?? b.r.concept) }),
        { move: 'TENSION', step: `contested:${ax.key}`, ...tr, concepts: [ax.concept, ax.opp ?? b.r.concept], rules: [x.r.ruleId, b.r.ruleId] }));
      return;
    }
    const claimText = rd.claim && !c.soft ? rd.claim : null;
    if (ci === 0 && usedFormation && claimText) {
      voiced.add(x.r.ruleId);
      xs.push(W.sentence(fill(W.pick(`fthen|${t.id}`, F.formation_then[W.pol(c.concept) as '+' | '-' | '~']), { claim: claimText }), { move: 'ELABORATE', step: `claim:${t.id}:${c.concept}`, ...tr }));
    } else if (claimText) {
      const tpl = ci === 0 ? F.claim : F.claim_next;
      xs.push(W.sentence(fill(W.pick(`claim|${t.id}|${ci}`, tpl), { ground, claim: claimText, conn: ci === 0 ? '' : W.conn('addition', `${t.id}|${ci}`) }), { move: ci === 0 ? 'ANCHOR' : 'SATELLITE', step: `claim:${t.id}:${c.concept}`, ...tr }));
    } else {
      const p = W.pred(c.concept, c.soft, `claim|${t.id}|${ci}`);
      if (!p) return;
      xs.push(W.sentence(fill(W.pick(`claimc|${t.id}|${ci}`, F.claim_card), { ground, S: W.S(c.concept), pred: p }), { move: ci === 0 ? 'ANCHOR' : 'SATELLITE', step: `claim:${t.id}:${c.concept}`, ...tr }));
    }
    // what the claim looks like in a life, from the card: once per thesis, after its first claim
    const card = W.card(c.concept);
    if (ci === 0 && !c.soft && card?.behave?.length) {
      const b = W.pick(`behave|${c.concept}`, card.behave);
      xs.push(W.sentence(b.replace('{S}', W.S(c.concept)), { move: 'ELABORATE', step: `behave:${t.id}:${c.concept}`, concepts: [c.concept], rules, cites, keys: [`${c.concept}@${P}`] }));
    }
    // the book's reducers of this claim
    const red = rarest(ax.reducers.filter(y => !voiced.has(y.r.ruleId)));
    if (red) {
      voiced.add(red.r.ruleId);
      const r = W.read(red.r.ruleId);
      if (r.claim && r.cond) xs.push(W.sentence(fill(W.pick(`red|${red.r.ruleId}`, F.reducer), { conn: W.conn('contrast', `red|${red.r.ruleId}`), cond: lowerSafe(r.cond), claim: r.claim }),
        { move: 'TURN', step: `reducer:${red.r.ruleId}`, concepts: [c.concept], rules: [...new Set(ax.reducers.map(y => y.r.ruleId))], cites: [...new Set(ax.reducers.flatMap(y => y.r.cites))], keys: [`${c.concept}@${P}|reduced`] }));
    }
    // a limit from the other side of the axis (a less fundamental seat)
    const ag = rarest(ax.against.filter(y => !voiced.has(y.r.ruleId)));
    if (ag) {
      voiced.add(ag.r.ruleId);
      const r = W.read(ag.r.ruleId), p = W.pred(ag.r.concept, false, `ag|${ag.r.ruleId}`);
      const text = r.claim ? `${W.conn('concession', `ag|${ag.r.ruleId}`)} ${W.ground(ag)} kéo theo chiều ngược lại: ${r.claim}`
        : p ? fill(W.pick(`ag|${ag.r.ruleId}`, F.against), { conn: W.conn('concession', `ag2|${ag.r.ruleId}`), ground: W.ground(ag), S: W.S(ag.r.concept), pred: p }) : '';
      if (text) { xs.push(W.sentence(text, { move: 'TURN', step: `against:${ax.key}`, concepts: [ag.r.concept], rules: [ag.r.ruleId], cites: ag.r.cites, keys: [`${ag.r.concept}@${P}`] })); allConcepts.add(ag.r.concept); }
    }
  });
  // the special structures this thesis carries are told here, once the whole chapter is written (a limit the book's reducers voice later
  // in the chapter, e.g. Hóa Lộc ở Tứ Mộ on the Hóa Lộc thesis, is not said twice)
  if (t.steps.some(st => st.structure)) structAt.push({ t, xs, at: xs.length });
  // the rescuer's own limit, when its thesis is not told next
  const cav = t.rescuerCaveat;
  if (cav && !order.some(u => u.seat.id === cav.seat.id)) {
    const red = rarest(cav.axis.reducers), r = red && W.read(red.r.ruleId);
    if (r?.claim && r.cond && cav.seat.hoa) xs.push(W.sentence(fill(W.pick(`cav|${t.id}`, F.caveat), { conn: W.conn('contrast', `cav|${t.id}`), hoa: cav.seat.hoa, cond: lowerSafe(r.cond), claim: r.claim }),
      { move: 'RESCUE', step: `caveat:${t.id}`, concepts: [cav.axis.concept], rules: [red.r.ruleId], cites: red.r.cites, keys: [`${cav.axis.concept}@${P}|caveat`] }));
  }
  // corroboration / counter-evidence from the tam phương
  for (const type of ['corroborated', 'countered'] as const) {
    const cr = t.cross.find(x => x.type === type && !voiced.has(x.ruleId));
    if (!cr) continue;
    voiced.add(cr.ruleId);
    const rr = W.read(cr.ruleId);
    if (!rr.claim) continue;
    const g = rr.cond ? lowerSafe(rr.cond) : `cung ${cr.palace}`;
    const tpl = type === 'countered' && W.pol(cr.concept) === '+' && F.countered_up?.length ? F.countered_up : F[type];
    xs.push(W.sentence(fill(W.pick(`${type}|${cr.ruleId}`, tpl), { conn: W.conn('contrast', `${type}|${cr.ruleId}`), palace: cr.palace, ground: g, claim: rr.claim }),
      { move: 'VIA', step: `${type}:${cr.palace}:${cr.ruleId}`, concepts: [cr.concept], rules: [cr.ruleId], cites: cr.cite ? [cr.cite] : [], keys: [`${cr.concept}@${cr.palace}`] }));
  }
}

/** A sentence saying a hãm star became good ("hết hãm", "hãm … biến thành tốt"). */
const HAM_GOOD = /(?:hết|không còn) hãm|hãm[^.;:]*?(?:biến|trở|chuyển|hóa)\s+(?:thành|nên)\s+(?:tốt|cát|đẹp)/iu;
/** Pages a structure line names ("KL tr.66; TH tr.52 …"), in the rules' cite form ("KL p.66"). */
const pagesOf = (s: string) => [...s.matchAll(/\b(KL|TH|TT) tr\.(\d+)/g)].map(m => `${m[1]} p.${m[2]}`);
/** A structure line in reader words: its `lines` entry (null when the entry keeps it silent); without one, the line itself once its pages and
 *  school codes are removed, if it then passes the reader lint. */
function structureLine(W: Writer, F: ReasoningFrames['structure'], type: 'limit' | 'rescue' | 'caveat', id: string, note: string, key: string): string | null {
  for (const e of F.lines) {
    if (e.type !== type || (e.structure && e.structure !== id)) continue;
    const m = note.match(new RegExp(e.match, 'u'));
    if (!m) continue;
    if (!e.say.length) return null;
    const v = Object.fromEntries(Object.entries(m.groups ?? {}).map(([k, x]) => [k, x === undefined ? '' : x.includes(', ') ? joinVi(x.split(', ')) : x]));
    return fill(W.pick(`sline|${key}`, e.say), v);
  }
  const t = note.replace(/\s*\([^()]*\b(?:KL|TH|TT) tr\.[^()]*\)/g, '').replace(/\s*\((?:R\d+|U_[A-Z_]+)\)/g, '').replace(/\s*—\s*R\d+.*$/, '').trim().replace(/\.$/, '');
  const low = ' ' + t.toLowerCase();
  if (!t || /[/()]/.test(t) || META.some(w => low.includes(' ' + w)) || ABSOLUTE.some(w => low.includes(w))) return null;
  return type === 'caveat' ? t : lowerSafe(t);
}
/** The sentences of the special structures a thesis carries (plan steps 'structure*'). A structure with no book sentence (structure_position)
 *  is told as a position fact and nothing else. A limit or rescue line whose pages are already cited by a limit sentence of the chapter (the
 *  KG reducers) is not said again. The structure's name opens the first line about it; it has a sentence of its own when it is a book reading
 *  (da_doi_chieu) or nothing else is said of it. Sentences are the system's (basis he_thong); the pages a line names stay in the trace. */
export function structureSentences(W: Writer, F: ReasoningFrames['structure'], plan: ReadingPlan, t: Thesis, said: ProseSentence[]): ProseSentence[] {
  const out: ProseSentence[] = [];
  const told = (note: string) => { const pg = pagesOf(note); return pg.length > 0 && [...said, ...out].some(s => ['TURN', 'RESCUE', 'TENSION'].includes(s.trace.move) && pg.every(p => s.trace.cites.includes(p))); };
  for (const id of [...new Set(t.steps.filter(st => st.structure).map(st => st.structure!))]) {
    const steps = t.steps.filter(st => st.structure === id), sn = plan.structures.find(x => x.id === id);
    const head = steps.find(st => st.type === 'structure');
    const name = (sn?.name ?? head?.note ?? steps[0].note ?? id).replace(/\s*—\s*cung Mệnh$/, '');
    const S = (text: string, part: string, move: SentenceTrace['move'], cites: string[] = []) =>
      out.push(W.sentence(text, { move, step: `structure:${id}:${part}`, basis: 'he_thong', cites: [...new Set(cites)], concepts: [] }));
    if (sn?.position || steps.some(st => st.type === 'structure_position')) { S(fill(W.pick(`spos|${id}`, F.position), { name }), 'position', 'ANCHOR'); continue; }
    const lines = (type: 'limit' | 'rescue', st: Step['type']) => steps.filter(x => x.type === st && x.note && !told(x.note))
      .map((x, i) => ({ text: structureLine(W, F, type, id, x.note!, `${id}|${type}|${i}`), cites: pagesOf(x.note!) })).filter((x): x is { text: string; cites: string[] } => !!x.text);
    const limits = lines('limit', 'structure_limit'), rescues = lines('rescue', 'structure_rescue');
    const alone = head?.basis === 'sach' || (!limits.length && !rescues.length);
    if (head && alone) S(fill(W.pick(`shead|${id}`, F.head[head.basis]), { name }), 'head', 'ANCHOR', head.cite ? [head.cite.replace(' tr.', ' p.')] : []);
    if (limits.length) S(fill(W.pick(`slim|${id}`, alone ? F.limit : F.limit_named), { name, lines: limits.map(x => x.text).join('; ') }),
      'limit', 'TURN', limits.flatMap(x => x.cites));
    if (rescues.length) S(fill(W.pick(`sres|${id}`, alone || limits.length ? F.rescue : F.rescue_named), { name, lines: rescues.map(x => x.text).join('; ') }),
      'rescue', 'RESCUE', rescues.flatMap(x => x.cites));
    const cav = steps.find(st => st.type === 'structure_caveat');
    const ct = cav?.note && structureLine(W, F, 'caveat', id, cav.note, `${id}|caveat`);
    if (ct) S(ct, 'caveat', 'TENSION');
  }
  return out;
}

/** Adapter for tools/interpret/eval_distinct.ts. */
export const reasonedSaid = (facts: any, k: Knowledge) => {
  const o = reasonedChapter(facts, k, { allowDraft: true });
  return { text: o.text, sentences: o.paragraphs.flatMap(p => p.sentences.map(s => ({ text: s.text, concepts: s.trace.concepts, rules: s.trace.rules }))) };
};
