// Realize (prose plan §4.6): moves -> Vietnamese sentences, each with its trace (which rules, pages and resolver decisions it voices).
// Paragraph 1 follows the chosen schema; moves the schema leaves out, further satellites and the remaining limit go to paragraph 2;
// paragraph 3 carries the additive độ số balance and the course-of-life traits. Factual sentences carry basis 'sach' and the rules
// behind them; VALUE and TRANSFORM sentences are 'he_thong' and may only re-voice concepts said earlier in the same paragraph.
import type { Concept, Knowledge } from '../types.ts';
import type { Resolved } from '../kg/resolve.ts';
import type { ConceptCard, ModifierCard, Move } from './types.ts';
import type { ConceptPick, Selection } from './select.ts';
import { Micro, finish, lead, lowerFirst } from './micro.ts';

export interface SentenceTrace {
  move: Move | 'DEGREE' | 'EXTRA' | 'VIA' | import('./deep.ts').DeepMove; concepts: string[]; rules: string[]; cites: string[];
  /** sach: a verified book rule; he_thong: the system's closing words over what was said; tinh_toan: a computed fact or a page-cited
   *  table (deep.ts); pho_thong: a draft card of common meanings (deep.ts), labelled as such to the reader */
  basis: 'sach' | 'he_thong' | 'tinh_toan' | 'pho_thong' | 'minh_hoa' | 'loi_khuyen';
  /** narrative.ts: the claim was told in its card's soft form (a weakened reading): it is never set side by side with another as a plain strength */
  soft?: boolean;
  /** minh_hoa (owner policy 2026-10-22): the step of the ONE sourced sentence this illustration makes concrete — `tied` (Tử Vi,
   *  prose/luan_deep.ts, narrative.ts) or `attach` (Bát Tự, bazi_deep.ts); prose/checked.ts drops the line when that sentence goes */
  tied?: string;
  attach?: string;
  /** Bát Tự (bazi_deep.ts): the sentence says why (a mechanism), not only what */
  mech?: boolean;
  /** Bát Tự (bazi_deep.ts): the condition a verdict stands on, e.g. 'cach_partial' = true only if the cách is established (owner review 2026-10-22) */
  conditional?: string;
  /** deep.ts: a difficulty ('neg'), something good ('pos'), or what answers a difficulty ('answer') */
  tone?: 'neg' | 'pos' | 'answer';
  resolution?: { relation: string; byRule: string; cite?: string }; schema?: string; woven?: Array<SentenceTrace['move']>;
  /** narrative.ts: the full form of an anaphoric claim ("Cùng thế ấy, …"), used when the sentence it leans on is not told */
  alt?: string;
  /** concept@palace of every reading voiced: the report never voices the same reading twice */
  keys?: string[];
  /** reasoned chapter (narrative.ts): the ReadingPlan step this sentence voices */
  step?: string;
  /** how the reading was reached or what the books leave open (a caveat, a position with no reading of its own, the centre of the
   *  reading): never told in the text, shown when the reader opens this sentence (report.js proseWhy) */
  note?: string;
  /** a method sentence (narrative.ts foldAsides): it becomes the note of the reading next to it and is not told */
  aside?: boolean;
  /** luận cung (prose/luan.ts): which part of the chapter frame the sentence belongs to — 1 structure, 2 support / limit, 3 interaction,
   *  4 a contradiction and how it is explained, 5 the conditional conclusion from the domain ledger (6, the sources, is the Căn cứ fold) */
  part?: 1 | 2 | 3 | 4 | 5;
  /** the domain verdict a conclusion sentence voices (reason/ledger.ts): every chapter says the same verdict for the same domain */
  ledger?: { domain: string; verdict: string; base: '+' | '-' | null };
  /** the limiting elements of the palace (reason/evidence.ts ids) the sentence faces */
  confront?: string[];
}
/** Who a chapter's sentences are about: in Phu Thê and Nô Bộc a reading that is not about the bond itself describes the other people. */
export interface Voice { other?: { first: string[]; next: string[] }; bond?: (c?: Concept) => boolean }
export interface ProseSentence { text: string; trace: SentenceTrace }
export interface ProseParagraph { role: 'core' | 'support' | 'course' | 'structure' | 'colour' | 'balance'; sentences: ProseSentence[]; text: string;
  /** luận cung (prose/luan.ts): the bold lead-in the paragraph opens with ("Về tính cách và cách giao tiếp"); the first sentence's text starts
   *  with it, so a plain-text reader sees it too. `topic` is its key (tinh_cach, su_nghiep, than, hau_van, tong_ket, …). */
  lead?: string; topic?: string;
  /** the frame part the paragraph serves: luận cung numbers it 1 … 5 (trace.part); the Bát Tự cách cục chapter names it (bazi_deep.ts FramePart) */
  part?: number | string;
  /** the deep reading (prose/luan_deep.ts): folded under "Đọc sâu" on the page, with its subsection title */
  deep?: boolean; title?: string;
  /** Bát Tự (bazi_deep.ts): 'sau' = the paragraph belongs to the "Đọc sâu" fold under the short reading; `depthTitle` names what it deepens */
  depth?: 'sau'; depthTitle?: string }

const join = (xs: string[]) => xs.length <= 1 ? (xs[0] ?? '') : xs.slice(0, -1).join(', ') + ' và ' + xs[xs.length - 1];
function fill(t: string, vars: Record<string, string | undefined>): string {
  return t.replace(/\{([a-zA-Z0-9_.]+)\}/g, (_, k) => { const v = vars[k]; if (v === undefined) throw new Error(`slot {${k}} unfilled in: ${t}`); return v; });
}

export class Realizer {
  private cards: Map<string, ConceptCard>; private mods: Map<string, ModifierCard>; private frameUsed = false; private said = new Set<string>();
  private cmap: Map<string, Concept>; private k: Knowledge; private s: Selection; private m: Micro; private voice: Voice;
  constructor(k: Knowledge, s: Selection, m: Micro, allowDraft: boolean, voice: Voice = {}) {
    this.k = k; this.s = s; this.m = m; this.voice = voice;
    const ok = (st: string) => st === 'approved' || (allowDraft && st !== 'retired');
    this.cards = new Map(k.prose!.concepts.filter(c => ok(c.status)).map(c => [c.id, c]));
    this.mods = new Map(k.prose!.modifiers.filter(c => ok(c.status)).map(c => [c.id, c]));
    this.cmap = new Map(k.concepts.concepts.map(c => [c.id, c]));
  }
  has(p?: ConceptPick) { return !!p && this.cards.has(p.concept); }
  saidConcepts() { return this.said; }

  // ---- helpers ----
  private otherSaid = false;
  private isOther(p?: ConceptPick) { return !!p && !!this.voice.other && !(this.voice.bond?.(this.cmap.get(p.concept)) ?? true); }
  /** The subject for a sentence about p: the other people, or the person (frame-initial form when it opens the chapter). */
  private who(p: ConceptPick | undefined, opening = false): string {
    // the other people are named in full the first time ('người bạn đời'), then by anaphor ('người ấy')
    if (this.isOther(p)) { const first = opening || !this.otherSaid; this.otherSaid = true; return first ? this.m.pick(`other|${this.s.palace.name}|${opening}`, this.voice.other!.first) : this.m.subject(this.voice.other!.next); }
    // where other people are spoken of, 'họ' would read as them: the person is then named without it
    const next = this.voice.other ? this.k.prose!.frames.subject.next.filter(x => x !== 'Họ') : undefined;
    return opening ? this.m.pick(`pfirst|${this.s.palace.name}`, this.k.prose!.frames.subject.palace_first) : this.m.subject(next);
  }
  private card(id: string) { return this.cards.get(id)!; }
  /** The predicate for a concept, with its verb: 'thường …' (+/~), 'dễ …' (−), or the soft form when the evidence was softened. */
  private pred(p: ConceptPick, key: string, verb = true): string {
    const c = this.card(p.concept), pol = this.cmap.get(p.concept)?.pol;
    if (p.soft && c.soft?.length) return this.m.pick(`${key}|soft|${p.concept}`, c.soft);
    if (pol === '-') return `${verb ? 'dễ ' : ''}${this.m.pick(`${key}|turn|${p.concept}`, c.turn ?? [])}`;
    return `${verb ? 'thường ' : ''}${this.m.pick(`${key}|pred|${p.concept}`, c.pred ?? [])}`;
  }
  private trace(move: SentenceTrace['move'], picks: Array<ConceptPick | undefined>, extra: Resolved[] = [], basis: 'sach' | 'he_thong' | 'loi_khuyen' = 'sach'): SentenceTrace {
    const ps = picks.filter((x): x is ConceptPick => !!x);
    ps.forEach(p => this.said.add(p.concept));
    const as = [...ps.flatMap(p => p.assertions), ...extra];
    return { move, keys: [...new Set(as.map(a => `${a.concept}@${a.palace ?? 'Mệnh'}`))], concepts: [...new Set(ps.map(p => p.concept))], rules: [...new Set(as.map(a => a.ruleId))].sort(), cites: [...new Set(as.flatMap(a => a.cites))].sort(), basis };
  }
  private mod(id: string, key: string, vars: Record<string, string | undefined>): string | null {
    const c = this.mods.get(id);
    return c ? fill(this.m.pick(`${key}|${id}`, c.variants), vars) : null;
  }
  private sentence(text: string, trace: SentenceTrace): ProseSentence {
    const t = finish(text);
    this.m.said(t);
    return { text: t, trace };
  }
  private frameVars() {
    return { stars: join(this.s.majors), branch: this.s.palace.branch, palace: this.s.palace.name, opp_stars: join(this.s.oppMajors) || 'các sao cung đối diện' };
  }
  /** The opening frame, naming what the first reading actually rests on. Mệnh has its own frames ('tọa Mệnh'); other palaces are named.
   *  An empty palace is read through the opposite one's stars only when the reading rests on them (vcd); a reading resting on a star
   *  standing in the empty palace names that star (vcd_own); otherwise the frame just says the palace has no chính tinh (vcd_plain). */
  private frame(p: ConceptPick): string {
    const P = this.s.palace.name, opp = this.s.oppMajors, atoms = p.assertions.flatMap(a => a.atoms);
    const own = [...new Set(atoms.filter(a => a.kind === 'star' && a.palace === P).map(a => a.name))];
    const kind = !this.s.vcd ? (this.s.majors.length === 2 ? 'pair' : 'single')
      : atoms.some(a => a.kind === 'star' && opp.includes(a.name)) ? 'vcd' : own.length ? 'vcd_own' : 'vcd_plain';
    const frames = P === 'Mệnh' ? this.k.prose!.frames.anchor : this.k.prose!.frames.anchor_palace;
    return fill(this.m.pick(`frame|${P}|${kind}`, frames[kind]), { ...this.frameVars(), own: join(own), S: P === 'Mệnh' ? undefined : this.who(p, true) });
  }
  private dignity(level: string | undefined, key: string): string {
    const lv = level === 'lợi' ? 'đắc' : level ?? '';
    return this.m.pick(`${key}|dig|${lv}`, this.k.prose!.frames.dignity[lv] ?? [lv]);
  }

  // ---- moves ----
  anchor(): ProseSentence | null {
    const n = this.s.nucleus;
    if (!this.has(n)) return null;
    if (this.frameUsed) return this.sentence(lead(this.m.conn('concession', 'anchor'), `${this.who(n)} vẫn ${this.pred(n!, 'anchor')}`), this.trace('ANCHOR', [n]));
    const frame = this.frame(n!);
    this.frameUsed = true;
    return this.sentence(`${frame} ${this.pred(n!, 'anchor')}`, this.trace(this.s.vcd ? 'BORROW' : 'ANCHOR', [n]));
  }

  elaborate(): ProseSentence | null {
    const n = this.s.nucleus;
    if (!this.has(n) || n!.soft || !this.card(n!.concept).behave?.length) return null;      // a weakened core is not elaborated
    const v = this.m.pick(`elab|${n!.concept}`, this.card(n!.concept).behave!), subj = this.who(n);
    const t = v.replace('{S}', v.startsWith('{S}') ? subj : lowerFirst(subj));
    return this.sentence(t, this.trace('ELABORATE', [n]));
  }

  turn(): ProseSentence | null {
    const ts = this.s.turn.filter(p => this.has(p));
    if (!ts.length) return null;
    const [t1, t2] = ts, c = this.s.turnCause, n = this.s.nucleus;
    const second = t2 ? `, và cũng ${this.pred(t2, 'turn2')}` : '';
    let text: string;
    if (c && this.frameUsed && n && this.said.has(n.concept)) {
      const who = this.s.turnIsShadow ? this.card(n.concept).pron : lowerFirst(this.who(t1));
      text = lead(this.m.conn('contrast', 'turn'), `ở ${this.s.palace.branch}, ${c.star} ${this.dignity(c.dignity, 'turn')}, nên ${who} ${this.pred(t1, 'turn1')}${second}`);
    } else if (c && !this.frameUsed) {
      this.frameUsed = true;
      const here = this.s.palace.name === 'Mệnh' ? `người có ${c.star} tọa Mệnh tại đây` : `người có ${c.star} ở cung ${this.s.palace.name}`;
      text = `Ở ${this.s.palace.branch}, ${c.star} ${this.dignity(c.dignity, 'turn')}, nên ${here} ${this.pred(t1, 'turn1')}${second}`;
    } else if (!this.frameUsed) {
      // the limit opens the chapter: name the chart first, never a contrast with nothing before it
      this.frameUsed = true;
      text = `${this.frame(t1)} ${this.pred(t1, 'turn1')}${second}`;
    } else {
      text = lead(this.m.conn('contrast', 'turn'), `${this.who(t1)} cũng ${this.pred(t1, 'turn1')}${second}`);
    }
    return this.sentence(text, this.trace('TURN', ts));
  }

  rescue(): ProseSentence | null {
    const r = this.s.rescue;
    if (!r || !this.has(r.target)) return null;
    const tc = this.card(r.target.concept);
    const id = r.via === 'hoa' && r.hoa === 'Hóa Lộc' ? 'MOD_RESCUE_HOA_LOC' : r.via === 'tuan_triet' ? 'MOD_RESCUE_TUAN_TRIET' : r.via === 'cat' ? 'MOD_RESCUE_CAT' : 'MOD_RESCUE_GENERIC';
    const text = this.mod(id, 'rescue', { star: r.star ?? this.s.majors[0] ?? 'chính tinh', tt: r.tt, 'target.pron': this.said.has(r.target.concept) ? tc.pron : tc.np, 'target.np': tc.np })
      ?? this.mod('MOD_RESCUE_GENERIC', 'rescue', { 'target.pron': tc.np, 'target.np': tc.np });
    if (!text) return null;
    const tr = this.trace('RESCUE', [r.target, r.mitigated]);
    const by = r.target.assertions.flatMap(a => a.by).find(b => b.relation === r.relation);
    tr.resolution = { relation: r.relation, byRule: r.byRule, cite: by?.cite };
    if (!tr.rules.includes(r.byRule)) tr.rules.push(r.byRule);
    return this.sentence(text, tr);
  }

  tension(): ProseSentence | null {
    const t = this.s.tension;
    if (!t) return null;
    const pos = this.has(t.pos) ? t.pos : undefined, neg = this.has(t.neg) ? t.neg : undefined;
    if (!pos && !neg) return null;
    let text: string | null;
    if (t.kind === 'sat' && t.dignityOk && pos) {
      text = this.mod('MOD_TENSION_SAT_DAC', 'tension', { star: t.star, dignity: this.dignity(t.dignity, 'tension'), 'concept.np': this.card(pos.concept).np });
      if (text && neg) text += `, ${this.m.conn('concession', 'tension', 'medial') || 'dù'} cũng kèm ${this.card(neg.concept).np}`;
    } else if (t.kind === 'sat') {
      const p = neg ?? pos!;
      text = this.mod('MOD_TENSION_SAT_HAM', 'tension', { star: t.star, 'concept.say': `${lowerFirst(this.who(p))} ${this.pred(p, 'tension')}` });
    } else {
      const id = t.hoa === 'Hóa Quyền' ? 'MOD_TENSION_HOA_QUYEN' : t.hoa === 'Hóa Kỵ' ? 'MOD_TENSION_HOA_KY' : 'MOD_TENSION_HOA_KHOA';
      const p = pos ?? neg!;
      text = this.mod(id, 'tension', { star: t.star, 'concept.np': this.card(p.concept).np, 'concept.say': `${lowerFirst(this.who(p))} ${this.pred(p, 'tension')}` });
    }
    return text ? this.sentence(text, this.trace('TENSION', [pos, neg])) : null;
  }

  timing(): ProseSentence | null {
    const t = this.s.timing;
    if (!t || !this.has(t.pick)) return null;
    const say = `${lowerFirst(this.who(t.pick))} ${this.pred(t.pick, 'timing')}`;
    const text = t.tt ? this.mod('MOD_TIMING_TUAN_TRIET', 'timing', { tt: t.tt, palace: this.s.palace.name, 'concept.say': say }) : this.mod('MOD_TIMING_GENERIC', 'timing', { 'concept.say': say });
    return text ? this.sentence(text, this.trace('TIMING', [t.pick])) : null;
  }

  /** Further traits; a limit (aside) joins the same sentence with a medial contrast, or follows as its own sentence. */
  satellite(picks: ConceptPick[], key: string, aside?: ConceptPick): ProseSentence | null {
    const all = picks.filter(p => this.has(p)), ps = all.filter(p => this.isOther(p) === this.isOther(all[0])).slice(0, 2);
    const neg = this.has(aside) && (!ps.length || this.isOther(aside) === this.isOther(ps[0])) ? aside : undefined;
    if (!ps.length) return neg ? this.limitAside(neg) : null;
    let body = ps.length === 2 ? `${this.pred(ps[0], key)}, lại ${this.pred(ps[1], key + '2', false)}` : this.pred(ps[0], key);
    if (neg) body += `, ${this.m.conn('contrast', key + 'm', 'medial') || 'nhưng'} cũng ${this.pred(neg, key + 'neg')}`;
    return this.sentence(lead(this.m.conn('addition', key), `${this.who(ps[0])} ${body}`), this.trace('SATELLITE', [...ps, neg]));
  }

  /** A concept of this chapter's kind that only another palace carries (Mệnh hands career and money on): said with where it is read. */
  via(items: Selection['via']): ProseSentence | null {
    const xs = items.filter(x => this.has(x.pick));
    if (!xs.length) return null;
    const from = xs[0].from, body = xs.length === 2 && xs[1].from === from ? `${this.pred(xs[0].pick, 'via')}, lại ${this.pred(xs[1].pick, 'via2', false)}` : this.pred(xs[0].pick, 'via');
    const frame = fill(this.m.pick('via', this.k.prose!.frames.via), { from, S: lowerFirst(this.m.subject()) });
    const t = this.trace('VIA', xs[0].from === from && xs.length === 2 ? xs.map(x => x.pick) : [xs[0].pick]);
    return this.sentence(`${frame} ${body}`, t);
  }

  limitAside(p: ConceptPick | undefined): ProseSentence | null {
    if (!this.has(p)) return null;
    return this.sentence(lead(this.m.conn('contrast', 'aside'), `${this.who(p)} cũng ${this.pred(p!, 'aside')}`), this.trace('SATELLITE', [p]));
  }

  /** VALUE (+ TRANSFORM when both are due): re-voices only concepts already said in this paragraph. */
  close(withValue: boolean, withTransform: boolean, saidHere: Set<string>): ProseSentence | null {
    const n = this.s.nucleus;
    const value = withValue && this.has(n) && !n!.soft && saidHere.has(n!.concept) ? this.m.pick('value1', this.card(n!.concept).value ?? []) : '';
    const second = [this.s.tension?.pos, ...this.s.satellites].find(p => p && !p.soft && this.has(p) && saidHere.has(p.concept) && this.card(p.concept).value?.length && this.isOther(p) === this.isOther(n));
    const value2 = value && second ? this.m.pick('value2', this.card(second.concept).value!) : '';
    let mature = '', matureFrom: ConceptPick | undefined;
    if (withTransform) {
      const nc = n && this.has(n) ? this.card(n.concept) : undefined;
      if (nc?.mature?.length && !this.isOther(n) && this.s.turn.some(t => t.concept === nc.shadow) && saidHere.has(n!.concept)) { mature = this.m.pick('mature', nc.mature); matureFrom = n; }
      else for (const p of [...this.s.turn, this.s.tension?.neg]) if (p && this.has(p) && !this.isOther(p) && saidHere.has(p.concept) && this.card(p.concept).mature?.length) { mature = this.m.pick('mature', this.card(p.concept).mature!); matureFrom = p; break; }
    }
    // a trait of the other people is valued as theirs ('điều đáng quý ở người bạn đời …'), never as the person's own
    const v = !value ? null : this.isOther(n) ? this.mod('MOD_VALUE_OTHER', 'value', { value: value2 ? `${value} và ${value2}` : value, other: this.m.pick(`other|${this.s.palace.name}|v`, this.voice.other!.first) })
      : this.mod(value2 ? 'MOD_VALUE_PAIR' : 'MOD_VALUE_ONE', 'value', { value, value2 });
    const tr = mature ? this.mod('MOD_TRANSFORM', 'transform', { mature }) : null;
    if (!v && !tr) return null;
    const text = v && tr ? `${v}; ${tr}` : (v ?? tr!);
    // a sentence carrying a 'mature' clause is advice: labelled 'lời khuyên chung', never the chart's word (audit 2026-10-22)
    const t = this.trace(v && tr ? 'VALUE' : v ? 'VALUE' : 'TRANSFORM', [value ? n : undefined, value2 ? second : undefined, matureFrom], [], tr ? 'loi_khuyen' : 'he_thong');
    return this.sentence(text, t);
  }

  degree(): ProseSentence | null {
    const { up, down } = this.s.degree;
    if (!up.length && !down.length) return null;
    const kind = up.length && down.length ? 'MIXED' : up.length ? 'UP' : 'DOWN';
    const text = this.mod(`MOD_DEGREE_${kind}`, 'degree', {});
    if (!text) return null;
    const as = [...up, ...down];
    return this.sentence(text, { move: 'DEGREE', concepts: ['life.degree'], rules: [...new Set(as.map(a => a.ruleId))].sort(), cites: [...new Set(as.flatMap(a => a.cites))].sort(), basis: 'sach' });
  }

  course(p: ConceptPick, i: number): ProseSentence | null {
    if (!this.has(p)) return null;
    return this.sentence(lead(this.m.conn('addition', `course${i}`), `${this.who(p)} ${this.pred(p, `course${i}`)}`), this.trace('EXTRA', [p]));
  }
}
