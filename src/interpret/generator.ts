// Deterministic narrative generator: argument graph + editorial modules -> Vietnamese chapter.
// Slots are filled only from the argument graph (chart facts, fired verified rules and their pages); a passage whose slot is empty or
// unknown is skipped, never padded. Variant choice is a hash of (chart, module, passage) that skips variants whose opening words were
// used in the last sentences, so the same chart always reads the same and different charts do not read like one template.
//
// Prose is organised by THEME (planner.ts): each theme paragraph states what the configuration is about (system frame), gives the lead
// book reading with the chart condition that fires it, the readings that reinforce it, the facts that modify it (brightness, Tứ Hóa), the
// reading that pulls against it and how the two relate. The code below only assembles atomic fragments (a quote, its condition, its page);
// every connective sentence lives in the editorial modules (content/*.json) where an expert can review it.
import { joinVi } from './semantic.ts';
import { opposedPair, relIndexOf, type ArgumentGraph, type Claim, type Theme } from './planner.ts';
import type { Basis, ContentModule, Knowledge, ModuleCond, Passage } from './types.ts';

export interface Sentence { text: string; basis: Basis; kind: string; module: string; passage: string; rules: string[]; cites: string[] }
export interface Paragraph { module: string; role: string; title: string; sentences: Sentence[]; text: string; section?: string }
export type Slot = { text: string; rules: string[] };
export type Item = Record<string, Slot>;

const BOOK: Record<string, string> = { TH: 'Thực Hành', KL: 'Khảo Luận', TT: 'Toàn Thư', TL: 'Nghiệm Lý (Thiên Lương)', NL: 'Nghiệm Lý 1974 (Thiên Lương)', ZZ: 'Bát Tự Chân Tông, PDF' };
// "KL p.51 Cơ #4" (item 4 of the Thiên Cơ list on p.51) -> "Khảo Luận tr.51, mục “Cơ” ý 4" (the label is the book list's own heading)
export const citeVi = (c: string) => {
  // 紫微斗數全書 (zh.wikisource snapshot, engine/data/sources_web): cited by quyển and mục, it has no page ("TTH 2 八奴仆")
  const w = c.match(/^TTH\s+(\d+)\s+(.+)$/);
  if (w) return `Toàn Thư Hán văn, quyển ${w[1]}, mục ${w[2]}`;
  const m = c.match(/^(TH|KL|TT|TL|NL|ZZ)\s+(?:pp?\.)?\s*([\d]+(?:[-–][\d]+)?)(?:\s+(.+?)\s+#(\d+))?(.*)$/);
  if (!m) return c;
  return `${BOOK[m[1]]} tr.${m[2].replace(/-/g, '–')}${m[3] ? `, mục “${m[3]}” ý ${m[4]}` : ''}${m[5]}`;
};
const cap = (s: string) => s ? s[0].toUpperCase() + s.slice(1) : s;
const ORD = ['', 'thứ nhất', 'thứ hai', 'thứ ba', 'thứ tư', 'thứ năm', 'thứ sáu'];
const NUM = ['', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu'];

function hash(s: string): number { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
const opener = (t: string) => t.replace(/[^\p{L}\p{N} ]/gu, ' ').trim().split(/\s+/).slice(0, 2).join(' ').toLowerCase();

function citesOf(c: Claim): string[] { return [...new Set(c.grounds.flatMap(g => g.cites))].map(citeVi); }
function quoteList(c: Claim): string { return joinVi(c.quotes.map(q => `“${q}”`)); }
function claimItem(c: Claim, withCond: boolean): string {
  if (!withCond) { const cites = citesOf(c); return `${quoteList(c)}${cites.length ? ` (${cites.join('; ')})` : ''}`; }
  return c.grounds.map(g => {
    const qs = joinVi([...new Set(g.evidence.map(e => `“${e.core}”`))]), cites = [...new Set(g.cites)].map(citeVi);
    const cond = g.evidence[0].chartCondition;
    return `${qs}${cond ? ` khi ${cond}` : ''}${cites.length ? ` (${cites.join('; ')})` : ''}`;
  }).join('; ');
}
const lead0 = (c: Claim) => c.grounds[0].evidence[0];
/** the theme's concept says the same as the chapter topic ("nhà cửa, cơ nghiệp" in the Điền Trạch chapter): the opener must not repeat it */
function npIsTopic(np: string, short: string, topic: string): boolean {
  const t = topic.toLowerCase(); if (!t) return false;
  return [np, short].some(x => { const l = x.toLowerCase(); return l && (l.includes(t) || t.includes(l)); });
}
/** "Thực Hành tr.29–30; tr.44" instead of repeating the book name for every page */
export function mergeCites(cs: string[]): string {
  const by = new Map<string, string[]>(), order: string[] = [];
  for (const c of cs.map(citeVi)) {
    const m = c.match(/^(.+?) (tr\..+)$/);
    const book = m ? m[1] : c, page = m ? m[2] : '';
    if (!by.has(book)) { by.set(book, []); order.push(book); }
    if (page && !by.get(book)!.includes(page)) by.get(book)!.push(page);
  }
  return order.map(b => by.get(b)!.length ? `${b} ${by.get(b)!.join('; ')}` : b).join('; ');
}
const booksOf = (c: Claim) => joinVi([...new Set(c.grounds.flatMap(g => g.books))]);
/** "Toàn Thư ghi “quyền quý” khi Tử Vi và Thiên Tướng tại Quan Lộc (Toàn Thư tr.78–80)": one atomic, fully cited fragment. */
function fragment(c: Claim, verb = 'ghi', sc: (x: string) => string = x => x): string {
  const g = c.grounds[0], qs = joinVi([...new Set(g.evidence.map(e => `“${e.core}”`))]), cond = sc(g.evidence[0].chartCondition), cites = [...new Set(g.cites)].map(citeVi);
  return `${joinVi(g.books)} ${verb} ${qs}${cond ? ` khi ${cond}` : ''}${cites.length ? ` (${mergeCites(g.cites)})` : ''}`;
}

/** Template engine shared by every chapter: slots, lists and items -> sentences with basis, rules and cites. */
export class Renderer {
  slots = new Map<string, Slot>(); lists = new Map<string, Claim[]>(); items = new Map<string, Item[]>();
  k: Knowledge; seed: string; capScale: number;
  constructor(k: Knowledge, seed: string, capScale = 1) { this.k = k; this.seed = seed; this.capScale = capScale; }
  set(key: string, text: string, rules: string[] = []) { this.slots.set(key, { text, rules }); }
  setItems(name: string, items: Item[]) { this.items.set(name, items); }

  protected listText(name: string): Slot {
    const all = this.lists.get(name) ?? [], capN = Math.max(1, Math.round((CAPS[name] ?? 4) * this.capScale)), cs = all.slice(0, capN);
    const withCond = !['base', 'support'].includes(name);
    const items = cs.map(c => claimItem(c, withCond || c.grounds.length > 1));
    const more = all.length - cs.length;
    return { text: items.join('; ') + (more > 0 ? `; cùng ${more} câu khác cùng chiều, xem trong danh sách chi tiết` : ''), rules: cs.flatMap(c => c.rules) };
  }
  /** Fill {slot}, {list:name} and optional {?slot|text} segments; returns null when a required slot is missing or empty. */
  fill(tpl: string, item?: Item, inner = false): { text: string; rules: string[] } | null {
    const rules: string[] = [];
    const get = (key: string): Slot | undefined => item?.[key] ?? (key.startsWith('list:') ? this.listText(key.slice(5)) : this.slots.get(key));
    let t = tpl.replace(/\{\?([\w.:]+)\|((?:[^{}]|\{[^{}]*\})*)\}/g, (_, key: string, body: string) => {
      const s = get(key); if (!s || !s.text) return '';
      const part = this.fill(body, item, true); if (!part) return '';
      rules.push(...s.rules, ...part.rules); return part.text;
    });
    let missing = false;
    t = t.replace(/\{([\w.:]+)\}/g, (_, key: string) => { const s = get(key); if (!s || !s.text) { missing = true; return ''; } rules.push(...s.rules); return s.text; });
    if (missing) return null;
    return { text: inner ? t : cap(t.replace(/\s+([,.;:])/g, '$1').replace(/\s{2,}/g, ' ').replace(/\.\./g, '.').trim()), rules };
  }

  cond(c: ModuleCond | undefined, item?: Item): boolean {
    if (!c) return true;
    if ('all' in c) return c.all.every(x => this.cond(x, item));
    if ('any' in c) return c.any.some(x => this.cond(x, item));
    if ('not' in c) return !this.cond(c.not, item);
    if ('list' in c) return (this.lists.get(c.list)?.length ?? this.items.get(c.list)?.length ?? 0) >= (c.min ?? 1);
    if ('slot' in c) { const v = item?.[c.slot]?.text ?? this.slots.get(c.slot)?.text ?? ''; return c.truthy === false ? !v : c.eq !== undefined ? v === c.eq : !!v; }
    return false;
  }

  /** variant indices already used per passage in this chapter: a passage rendered again prefers a variant it has not used */
  used = new Map<string, Set<number>>();
  render(modules: ContentModule[], recent: string[] = []): Paragraph[] {
    const out: Paragraph[] = [];
    for (const m of [...modules].sort((x, y) => x.order - y.order || (x.id < y.id ? -1 : 1))) {
      if (m.status === 'retired' || !this.cond(m.when)) continue;
      const groups: Array<Item | undefined> = m.each ? (this.items.get(m.each) ?? []) : [undefined];
      let merged: Sentence[] = [];
      groups.forEach((group, gi) => {
        const sentences: Sentence[] = m.merge ? merged : [];
        for (const p of m.passages) {
          if (!this.cond(p.when, group)) continue;
          const items = p.each ? (this.items.get(p.each) ?? []) : [group];
          items.forEach((item, idx) => {
            const filled = this.pick(m, p, m.merge ? gi : gi * 10 + idx, item, recent);
            if (!filled) return;
            const cites = (p.cites ?? []).map(c => this.fill(c, item)?.text ?? c).filter(Boolean).map(citeVi);
            for (const text of splitSentences(filled.text)) {
              sentences.push({ text, basis: p.basis, kind: p.kind ?? 'claim', module: m.id, passage: p.id, rules: [...new Set(filled.rules)], cites });
              recent.push(opener(text));
            }
          });
        }
        if (m.merge) return;
        const title = group?.['t.title']?.text ?? m.title;
        if (sentences.length) out.push({ module: m.id, role: m.role, title, sentences, text: sentences.map(s => s.text).join(' ') });
      });
      if (m.merge && merged.length) out.push({ module: m.id, role: m.role, title: this.fill(m.title)?.text ?? m.title, sentences: merged, text: merged.map(s => s.text).join(' ') });
      merged = [];
    }
    return out;
  }

  private pick(m: ContentModule, p: Passage, idx: number, item: Item | undefined, recent: string[]) {
    const useFollow = idx > 0 && !!p.followups?.length;
    const pool = useFollow ? p.followups! : p.variants;
    const key = `${m.id}/${p.id}/${useFollow ? 'f' : 'v'}`, used = this.used.get(key) ?? new Set<number>();
    const n = pool.length, start = hash(`${this.seed}|${m.id}|${p.id}|${idx}`) % n;
    const cands: Array<{ i: number; f: NonNullable<ReturnType<Renderer['fill']>> }> = [];
    for (let j = 0; j < n; j++) { const i = (start + j) % n, f = this.fill(pool[i], item); if (f) cands.push({ i, f }); }
    if (!cands.length) return null;
    const fresh = (c: { f: { text: string } }) => !recent.slice(-4).includes(opener(c.f.text));
    const best = cands.find(c => !used.has(c.i) && fresh(c)) ?? cands.find(c => fresh(c)) ?? cands.find(c => !used.has(c.i)) ?? cands[0];
    used.add(best.i); this.used.set(key, used);
    return best.f;
  }
}

/** What one chapter has already said, shared by the realizers of its sections (a combined chapter must not repeat itself). */
export interface NarrativeState { digSaid: Set<string>; principleSaid: { strong: boolean; weak: boolean }; used: Map<string, Set<number>>; condSaid: Set<string>; whereSaid: Set<string> }
export const newState = (): NarrativeState => ({ digSaid: new Set(), principleSaid: { strong: false, weak: false }, used: new Map(), condSaid: new Set(), whereSaid: new Set() });
/** A rule's chart condition, minus what the reader was already told: a trailing context clause ("Mệnh ở Tỵ", "Phu Thê có Tuần") is
 *  said once, and a star group written out once is then called by its conventional name. A gender condition is substantive and always
 *  kept; a star list is never split; the condition is never emptied. */
const CONTEXT = /^\p{Lu}\p{L}*(?: \p{Lu}\p{L}*)? (?:ở \p{Lu}\p{L}*|có (?:Tuần|Triệt))$/u;
// conventional short names of star pairs and groups (the books use them: "Lộc Mã", "Xương Khúc", "Cơ Nguyệt Đồng Lương"...), used for a
// star list the reader has already seen written out in full in this chapter
const GROUP_NAMES: Array<[RegExp, string]> = [
  [/Thiên Cơ, Thái Âm, Thiên Đồng và Thiên Lương/, 'Cơ Nguyệt Đồng Lương'],
  [/Lộc Tồn và Thiên Mã/, 'Lộc Mã'], [/Văn Xương và Văn Khúc/, 'Xương Khúc'], [/Tả Phụ và Hữu Bật/, 'Tả Hữu'], [/Thiên Khôi và Thiên Việt/, 'Khôi Việt'],
  [/Địa Không và Địa Kiếp/, 'Không Kiếp'], [/Kình Dương và Đà La/, 'Kình Đà'], [/Hỏa Tinh và Linh Tinh/, 'Hỏa Linh'],
];
export function shortCond(cond: string, said: Set<string>): string {
  if (!cond) return cond;
  const atoms = cond.split(/, /);
  const ctx = atoms.length > 1 && CONTEXT.test(atoms[atoms.length - 1]);
  let out = atoms.filter((x, i) => !(ctx && i > 0 && CONTEXT.test(x) && said.has(x))).join(', ');
  for (const x of atoms) if (CONTEXT.test(x)) said.add(x);
  for (const [re, name] of GROUP_NAMES) {
    if (!re.test(out)) continue;
    if (said.has(`grp:${name}`)) out = out.replace(re, name);
    said.add(`grp:${name}`);
  }
  return out;
}

/** The chapter realizer: a Renderer whose slots and items come from a section's argument graph. */
export class Realizer extends Renderer {
  a: ArgumentGraph; dropped: Theme[] = []; restKept: Theme[] = []; extra: Record<string, string> = {}; digSaid: Set<string>; principleSaid: { strong: boolean; weak: boolean }; condSaid: Set<string>; whereSaid: Set<string>;
  private sc = (x: string) => shortCond(x, this.condSaid);
  constructor(a: ArgumentGraph, k: Knowledge, seed: string, capScale = 1, extra: Record<string, string> = {}, state: NarrativeState = newState()) {
    super(k, seed, capScale); this.a = a; this.digSaid = state.digSaid; this.principleSaid = state.principleSaid; this.used = state.used; this.condSaid = state.condSaid; this.whereSaid = state.whereSaid;
    this.extra = extra;
    this.prepare();
    for (const [key, v] of Object.entries(extra)) this.set(key, v);
  }
  private concept(id: string) { return this.k.concepts.concepts.find(x => x.id === id); }

  /** where a theme's lead reading comes from: its stars (with brightness) and palace */
  private whereOf(c: Claim): string {
    const e = lead0(c), a = this.a;
    const p = a.slots['f.name'];
    if (c.palace === p) {
      const own = e.presentStars.filter(s => this.palaceStars(p).includes(s));
      if (!own.length) return `cung ${p}`;
      // brightness is given the first time a star is named as a source; "ngay trong cung X" only the first time the palace is
      const first = !this.whereSaid.has(`@${p}`); this.whereSaid.add(`@${p}`);
      const names = joinVi(own.map(s => { const said = this.whereSaid.has(s); this.whereSaid.add(s); return said ? s : this.dig(p, s); }));
      return first ? `${names} ngay trong cung ${p}` : `${names} (cung ${p})`;
    }
    if (c.palace === 'chart') return e.chartCondition || 'tuổi sinh';
    return `cung ${c.palace}`;
  }
  private palaceStars(name: string): string[] { return name === this.a.focus ? this.a.focusStars : []; }
  private dig(_p: string, s: string): string { const d = this.a.focusDignity[s]; return d ? `${s} (${d})` : s; }

  private themeItem(t: Theme, i: number, n: number): Item {
    const lead = t.lead, e = lead0(lead), c = this.concept(lead.concept);
    const neg = t.polarity === '-';
    const item: Item = {
      // a theme led from another palace says so in its title (two themes of one facet then never share a heading)
      't.title': { text: cap(`${neg ? `${t.facetName}: mặt cần cân nhắc` : t.facetName}${lead.palace !== this.a.focus && lead.palace !== 'chart' ? ` (qua cung ${lead.palace})` : ''}`), rules: [] },
      't.np': { text: c?.np ?? t.facetName, rules: [] }, 't.short': { text: c?.short ?? c?.np ?? t.facetName, rules: [] },
      't.facet': { text: t.facetName, rules: [] }, 't.where': { text: this.whereOf(lead), rules: [] },
      't.first': { text: i === 0 && !neg ? '1' : '', rules: [] }, 't.next': { text: i > 0 && !neg ? '1' : '', rules: [] }, 't.neg': { text: neg ? '1' : '', rules: [] },
      't.ord': { text: ORD[i + 1] ?? '', rules: [] }, 't.last': { text: i === n - 1 ? '1' : '', rules: [] },
      't.lead_books': { text: joinVi(lead.grounds[0].books), rules: [] }, 't.lead_quote': { text: joinVi([...new Set(lead.grounds[0].evidence.map(x => `“${x.core}”`))]), rules: lead.rules },
      't.lead_cond': { text: this.sc(e.chartCondition), rules: [] }, 't.lead_cite': { text: mergeCites(lead.grounds[0].cites), rules: [] },
      't.dep': { text: t.deps.length ? joinVi([...new Map(t.deps.map(d => [d.palace, t.deps.filter(x => x.palace === d.palace).map(x => x.star)])).entries()].map(([p, st]) => `${joinVi(st)} nằm ở cung ${p}`)) : '', rules: [] },
      't.dep_from': { text: lead.palace === 'chart' ? 'tuổi sinh' : `cung ${lead.palace}`, rules: [] },
      't.lead_shared': { text: lead.grounds[0].evidence.length >= 2 ? NUM[lead.grounds[0].evidence.length] ?? String(lead.grounds[0].evidence.length) : '', rules: [] },
      't.lead_more_grounds': { text: lead.grounds.length > 1 ? (() => {
        // grounds that restate a quote the lead already told are said in ONE clause (books and pages merged, conditions listed);
        // grounds with another quote get their own clause
        const more = lead.grounds.slice(1, 6), sameG = more.filter(g => lead.quotes.includes(g.evidence[0].core)), other = more.filter(g => !lead.quotes.includes(g.evidence[0].core)).slice(0, 2);
        const parts: string[] = [];
        if (sameG.length) {
          const conds = [...new Set(sameG.map(g => this.sc(g.evidence[0].chartCondition)))].slice(0, 3);
          parts.push(`${joinVi([...new Set(sameG.flatMap(g => g.books))])}${sameG.some(g => g.cites.length) ? ` (${mergeCites(sameG.flatMap(g => g.cites))})` : ''} ghi cùng ý ấy cho ${conds.length > 1 ? 'các trường hợp' : 'trường hợp'} ${conds.join('; ')}`);
        }
        for (const g of other) { const x = g.evidence[0]; parts.push(`${joinVi(g.books)} ghi “${x.core}” khi ${this.sc(x.chartCondition)}${g.cites.length ? ` (${mergeCites(g.cites)})` : ''}`); }
        return parts.join('; ');
      })() : '', rules: lead.rules },
      't.np_is_topic': { text: npIsTopic(c?.np ?? '', c?.short ?? '', this.slots.get('topic')?.text ?? '') ? '1' : '', rules: [] },
      't.dep_palaces': { text: joinVi([...new Set(t.deps.map(d => `cung ${d.palace}`))]), rules: [] },
      // a supporting reading of another palace names its palace: the book said it of that palace, not of this one
      // a supporting reading whose words are the lead's own quote (two books or two palaces, same sentence) is not told again
      't.more': { text: [...t.support].sort((x, y) => Number(x.palace !== lead.palace) - Number(y.palace !== lead.palace))
        .map(s => `${s.palace !== lead.palace ? (s.palace === 'chart' ? 'theo tuổi sinh, ' : `ở cung ${s.palace}, `) : ''}${fragment(s, 'cũng ghi', this.sc)}`)
        .filter(x => !lead.quotes.some(q => q && x.includes(q))).join('; '), rules: t.support.flatMap(s => s.rules) },
      't.more_n': { text: t.support.length ? NUM[t.support.length] ?? String(t.support.length) : '', rules: [] },
    };
    // a cross-palace dependency already explained for an earlier theme is only recalled, not explained again
    const depKey = `dep:${item['t.dep'].text}`;
    if (item['t.dep'].text && this.whereSaid.has(depKey)) { item['t.dep_again'] = item['t.dep']; item['t.dep'] = { text: '', rules: [] }; }
    else { if (item['t.dep'].text) this.whereSaid.add(depKey); item['t.dep_again'] = { text: '', rules: [] }; }
    // modifiers: brightness and Tứ Hóa notes for the lead's stars when the lead sits in the focus palace
    if (lead.palace === this.a.slots['f.name']) {
      const stars = e.presentStars;
      const digs = (this.a.slots['f.dignity'] || '').split('; ').filter(Boolean).flatMap(x => x.split(/, | và /))
        .filter(x => stars.some(s => x.startsWith(s + ' ') && !this.digSaid.has(s)));
      for (const s0 of stars) if (digs.some(x => x.startsWith(s0 + ' '))) this.digSaid.add(s0);
      item['t.mod_dignity'] = { text: joinVi(digs), rules: [] };
      const majorsLv = stars.filter(s => digs.some(d => d.startsWith(s + ' '))).map(s => this.a.focusDignity[s]);
      const strong = majorsLv.length > 0 && majorsLv.every(l => ['miếu', 'vượng', 'đắc'].includes(l)), weak = majorsLv.some(l => l === 'hãm');
      const sayStrong = strong && !neg && !this.principleSaid.strong, sayWeak = weak && !this.principleSaid.weak;
      if (sayStrong) this.principleSaid.strong = true;
      if (sayWeak) this.principleSaid.weak = true;
      item['t.mod_strong'] = { text: sayStrong ? '1' : '', rules: [] };
      item['t.mod_weak'] = { text: sayWeak ? '1' : '', rules: [] };
      item['t.mod_mid'] = { text: majorsLv.length && majorsLv.every(l => l === 'bình') ? '1' : '', rules: [] };
      item['t.mod_fact'] = { text: majorsLv.length && !sayStrong && !sayWeak && !majorsLv.every(l => l === 'bình') ? '1' : '', rules: [] };
    } else for (const key of ['t.mod_dignity', 't.mod_strong', 't.mod_weak', 't.mod_mid', 't.mod_fact']) item[key] = { text: '', rules: [] };
    const c1 = t.counters[0], c2 = t.counters[1];
    if (c1) {
      // the counter's grounds, the one from the lead's own book first (the book weighing its two sentences is the strongest contrast);
      // every ground is narrated: a limiting reading said by two books is said with both
      const leadBooks = lead.grounds[0].books;
      const gs = [...c1.claim.grounds].sort((x, y) => Number(y.books.some(b => leadBooks.includes(b))) - Number(x.books.some(b => leadBooks.includes(b))));
      const cl: Claim = { ...c1.claim, grounds: gs };
      const ce = gs[0].evidence[0], cc = this.sc(ce.chartCondition);
      item['t.counter'] = { text: fragment(cl, 'ghi', () => cc), rules: c1.claim.rules };
      item['t.counter_quote'] = { text: joinVi([...new Set(gs[0].evidence.map(x => `“${x.core}”`))]), rules: c1.claim.rules };
      item['t.counter_books'] = { text: booksOf(c1.claim), rules: [] };
      item['t.counter_cond'] = { text: cc, rules: [] };
      item['t.counter_cite'] = { text: mergeCites(gs[0].cites), rules: [] };
      item['t.counter_more'] = { text: gs.slice(1, 3).filter(g => !g.evidence.every(e => gs[0].evidence.some(x => x.core === e.core)))
        .map(g => fragment({ ...cl, grounds: [g] }, 'cũng ghi', this.sc)).join('; '), rules: c1.claim.rules };
      item['t.counter_short'] = { text: this.concept(c1.claim.concept)?.short ?? '', rules: [] };
      item['t.same_book'] = { text: joinVi(gs[0].books.filter(b => lead.grounds[0].books.includes(b))), rules: [] };
      item['t.k_qualified'] = { text: c1.kind === 'qualified' ? '1' : '', rules: [] };
      item['t.k_relation'] = { text: c1.kind === 'relation' && c1.synth ? c1.synth : '', rules: [] };
      item['t.k_both'] = { text: c1.kind === 'both_hold' || (c1.kind === 'relation' && !c1.synth) ? '1' : '', rules: [] };
      item['t.k_refine'] = { text: c1.kind === 'refinement' ? '1' : '', rules: [] };
      item['t.shared_stars'] = { text: joinVi(c1.dominance?.sharedStars ?? []), rules: [] };
      item['t.criteria'] = { text: c1.dominance ? c1.dominance.criteria.slice(0, 4).join('; ') : '', rules: [] };
      item['t.counter2'] = { text: c2 ? fragment(c2.claim, 'ghi', this.sc) : '', rules: c2?.claim.rules ?? [] };
      const crest = t.counters.slice(2);
      item['t.counter_rest'] = { text: crest.map(x => fragment(x.claim, 'ghi', this.sc)).join('; '), rules: crest.flatMap(x => x.claim.rules) };
    } else for (const key of ['t.counter_more', 't.counter', 't.counter_quote', 't.counter_books', 't.counter_cond', 't.counter_cite', 't.counter_short', 't.same_book', 't.k_qualified', 't.k_relation', 't.k_both', 't.k_refine', 't.shared_stars', 't.criteria', 't.counter2', 't.counter_rest'])
      item[key] = { text: '', rules: [] };
    return item;
  }

  private backRefs(order: Theme[]): Map<string, Item> {
    const rel = relIndexOf(this.k), than = this.a.than;
    const person = (p: string) => p === 'Mệnh' || p === 'chart' || p === than;
    const members = (t: Theme) => [t.lead, ...t.support, ...t.counters.map(c => c.claim)];
    const out = new Map<string, Item>();
    order.forEach((t, j) => {
      const empty: Item = { 't.back_self': { text: '', rules: [] }, 't.back_other': { text: '', rules: [] }, 't.back_where': { text: '', rules: [] }, 't.back_conds': { text: '', rules: [] } };
      out.set(t.id, empty);
      for (const x of members(t)) for (const u of order.slice(0, j)) for (const y of members(u)) {
        if (out.get(t.id)!['t.back_self'].text || !opposedPair(x, y, rel, person)) continue;
        if (order.some(w => members(w).includes(x) && members(w).includes(y))) continue;
        const cx = lead0(x).chartCondition, cy = lead0(y).chartCondition;
        out.set(t.id, { 't.back_self': { text: x.quotes[0], rules: x.rules }, 't.back_other': { text: y.quotes[0], rules: y.rules },
          't.back_where': { text: `mục “${cap(u.polarity === '-' ? `${u.facetName}: mặt cần cân nhắc` : u.facetName)}”`, rules: [] },
          't.back_conds': { text: cx && cy && cx !== cy ? `${cx}, và ${cy}` : '', rules: [] } });
      }
    });
    return out;
  }

  private prepare() {
    const a = this.a;
    for (const [k, v] of Object.entries(a.slots)) this.set(k, v);
    if (a.slots['dh.focus_readings']) this.set('dh.focus_readings', a.slots['dh.focus_readings'], [`VH:${a.focus}`]);
    const L = (name: string, cs: Claim[]) => this.lists.set(name, cs);
    L('base', a.lists.base); L('support', a.lists.support); L('cross', a.lists.cross); L('work_style', a.lists.work_style);
    L('qualifier_focus', a.lists.qualifier.filter(c => c.palace === a.focus));
    L('qualifier_other', a.lists.qualifier.filter(c => c.palace !== a.focus));
    L('environment', a.lists.environment); L('timing', a.lists.timing);
    L('dominance', a.dominance.map(d => d.qualifier));

    const nThemes = Math.max(2, Math.round(a.themes.length * this.capScale));
    // working copies: counters may be added below, and the argument graph is rendered more than once (word budget)
    const copy = (t: Theme): Theme => ({ ...t, counters: [...t.counters] });
    // in a combined chapter (three palaces), a theme that is a single sentence — no reading with it, none against it — beyond the first two
    // is listed among the minor points instead of getting a paragraph of its own: ten one-line paragraphs read as a list, not an argument
    const multi = !!this.extra['section.multi'];
    const keep = (t: Theme, i: number) => i < nThemes && (!multi || i < 2 || t.support.length > 0 || t.counters.length > 0);
    const shown = a.themes.filter(keep).map(copy), env = a.envThemes.map(copy);
    this.dropped = a.themes.filter((t, i) => !keep(t, i));
    // a minor reading (only listed among "những điểm phụ") that pulls against a narrated theme is narrated inside that theme instead,
    // so the two sides are read together
    const rel = relIndexOf(this.k), person = (p: string) => p === 'Mệnh' || p === 'chart' || p === a.than;
    const members = (t: Theme) => [t.lead, ...t.support, ...t.counters.map(c => c.claim)];
    const fold = (c: Claim) => {
      const host = [...shown, ...env].find(t => t.counters.length < 5 && members(t).some(m => opposedPair(m, c, rel, person)));
      if (host) host.counters.push({ claim: c, kind: 'both_hold' });
      return !!host;
    };
    this.restKept = [...this.dropped, ...a.restThemes].filter(r => !fold(r.lead));
    // two minor readings that pull against each other are said to do so in the same sentence list
    const rk = this.restKept.slice(0, 4), pair = rk.flatMap((x, i) => rk.slice(i + 1).map(y => [x.lead, y.lead])).find(([x, y]) => opposedPair(x, y, rel, person));
    this.set('rest.pair_a', pair ? pair[0].quotes[0] : '', pair?.[0].rules ?? []); this.set('rest.pair_b', pair ? pair[1].quotes[0] : '', pair?.[1].rules ?? []);
    const inThemes = new Set([...a.themes, ...a.restThemes, ...a.envThemes].flatMap(t => [t.lead, ...t.support, ...t.counters.map(c => c.claim)].map(c => c.id)));
    const crossKept = a.cross.filter(x => !inThemes.has(x.claim.id) && !fold(x.claim));
    // readings of two different themes that pull against each other: the later theme says so, quoting both (render order: themes, env)
    const backs = this.backRefs([...shown, ...env]);
    this.items.set('themes', shown.map((t, i) => ({ ...this.themeItem(t, i, shown.length), ...backs.get(t.id) })));
    this.items.set('env_themes', env.map((t, i) => ({ ...this.themeItem(t, i, env.length), ...backs.get(t.id),
      't.title': { text: `Bối cảnh từ cung ${a.slots['env.name']}: ${t.facetName}`, rules: [] } })));
    this.set('themes.n', a.themes.length ? NUM[a.themes.length] ?? String(a.themes.length) : '');
    const rest = this.restKept;
    this.set('rest', rest.length ? joinVi(rest.slice(0, 4).map(t => `${this.concept(t.lead.concept)?.short ?? t.facetName} (${joinVi(t.lead.quotes.slice(0, 1).map(q => `“${q}”`))}${citesOf(t.lead).length ? `, ${citesOf(t.lead)[0]}` : ''})`)) : '',
      rest.slice(0, 4).flatMap(t => t.lead.rules));

    // cross-palace items
    this.items.set('cross', crossKept.slice(0, 3).map(x => {
        const e = lead0(x.claim);
        const byPal = new Map<string, string[]>();
        for (const d of x.deps) byPal.set(d.palace, [...(byPal.get(d.palace) ?? []), d.star]);
        const deps = byPal.size ? joinVi([...byPal].map(([p, st]) => `${joinVi(st)} nằm ở cung ${p}`)) : '';
        return { 'x.from': { text: x.claim.palace === 'chart' ? 'tuổi sinh' : `cung ${x.claim.palace}`, rules: [] }, 'x.books': { text: joinVi(e.books), rules: [] },
          'x.quote': { text: e.core, rules: x.claim.rules }, 'x.cite': { text: mergeCites(x.claim.grounds.flatMap(g => g.cites)), rules: [] }, 'x.deps': { text: deps, rules: [] },
          'x.cond': { text: this.sc(e.chartCondition), rules: [] },
          'x.dep_palaces': { text: joinVi([...new Set(x.deps.map(d => `cung ${d.palace}`))]), rules: [] } };
      }));

    this.set('group.same', a.slots['group.same'] ?? '', a.slots['group.rule'] ? [a.slots['group.rule']] : []);

    // timing
    const early = a.timingConflict.early, late = a.timingConflict.late;
    this.set('t.late', late.length ? '1' : '');
    this.set('timing.list', a.lists.timing.length ? a.lists.timing.slice(0, Math.max(1, Math.round(3 * this.capScale))).map(c => fragment(c)).join('; ') : '', a.lists.timing.flatMap(c => c.rules));
    this.set('dh.focus_conflict_text', a.slots['dh.focus_conflict'] ? '1' : '');
    this.set('timing.conflict', early.length && late.length ? '1' : '', [...early, ...late].flatMap(c => c.rules));
    this.set('timing.early', early.length ? `“${early[0].quotes[0]}”` : ''); this.set('timing.late', late.length ? `“${late[0].quotes[0]}”` : '');
    this.set('timing.early_cond', early.length ? lead0(early[0]).chartCondition : ''); this.set('timing.late_cond', late.length ? lead0(late[0]).chartCondition : '');

    // limits
    const dr = a.excluded.drafts;
    this.set('lim.drafts', joinVi(dr.slice(0, 3).map(d => `“${d.text.split(' (')[0].split('; ')[0]}”`)) + (dr.length > 3 ? ` cùng ${dr.length - 3} câu khác` : ''), dr.slice(0, 3).map(d => d.rule));
    this.set('lim.drafts_n', NUM[a.excluded.drafts.length] ?? String(a.excluded.drafts.length));
    this.set('lim.drafts_pron', a.excluded.drafts.length === 1 ? 'nó' : 'chúng');
    this.set('lim.scope', joinVi(a.excluded.scopeNotes.map(n => `“${n.text.split(' (')[0]}”`)), a.excluded.scopeNotes.map(n => n.rule));
    const dom = a.dominance[0];
    this.set('lim.criteria', a.dominance.length ? '1' : '');
    this.set('lim.dom_n', a.dominance.length ? NUM[a.dominance.length] ?? String(a.dominance.length) : '');
    void dom;

    // synthesis: names only (concept shorts), never re-quotes a book sentence
    // a concept name that only repeats the chapter topic ("nhà cửa, cơ nghiệp xoay quanh cơ nghiệp") is replaced by the reading itself
    const topic = this.slots.get('topic')?.text ?? '';
    const shortOf = (c: Claim) => { const co = this.concept(c.concept); return co?.short && !npIsTopic(co.np ?? '', co.short, topic) ? co.short : `câu “${c.quotes[0]}”`; };
    const t0 = a.themes.find(t => t.polarity !== '-'), t1 = a.themes.filter(t => t.polarity !== '-' && t !== t0 && t.lead.polarity === '+')[0];
    const counters = a.themes.flatMap(t => t.counters.map(c => c.claim)).concat(a.themes.filter(t => t.polarity === '-').map(t => t.lead));
    this.set('syn.lead', t0 ? shortOf(t0.lead) : '', t0?.lead.rules ?? []);
    this.set('syn.lead_where', t0 ? this.whereOf(t0.lead) : '');
    this.set('syn.second', t1 ? shortOf(t1.lead) : '', t1?.lead.rules ?? []);
    const leadShort = t0 ? shortOf(t0.lead) : '';
    const cname = (c: Claim) => shortOf(c) === leadShort ? `câu “${c.quotes[0]}”` : shortOf(c);
    const said = new Set([leadShort, t1 ? shortOf(t1.lead) : '']);
    const cnames = [...new Set(counters.map(cname))].filter(x => !said.has(x)).slice(0, 2);
    this.set('syn.counter', cnames.length ? joinVi(cnames) : '', counters.flatMap(c => c.rules));
    const leadStars = new Set(t0 ? t0.stars : []);
    this.set('syn.counter_where', counters.length ? joinVi([...new Set(counters.flatMap(c => lead0(c).presentStars))].filter(st => !leadStars.has(st)).slice(0, 3)) : '');
    this.set('syn.qualified', a.themes.some(t => t.counters.some(c => c.kind === 'qualified')) ? '1' : '');
    const crossPals = [...new Set(a.cross.filter(x => x.claim.palace !== 'chart').map(x => x.claim.palace))];
    const crossChart = a.cross.some(x => x.claim.palace === 'chart');
    this.set('syn.cross', a.cross.length ? joinVi([...(crossPals.length ? [`cung ${joinVi(crossPals)}`] : []), ...(crossChart ? ['các câu theo tuổi sinh'] : [])]) : '', a.cross.flatMap(x => x.claim.rules));
    this.set('syn.env', a.envThemes.length ? shortOf(a.envThemes[0].lead) : '', a.envThemes[0]?.lead.rules ?? []);
    this.set('syn.timing', late.length && !early.length ? 'sách nghiêng về nhịp đến muộn' : early.length && !late.length ? 'sách nghiêng về nhịp đến sớm' : early.length && late.length ? 'hai câu về nhịp đi ngược chiều nhau' : '',
      [...early, ...late].flatMap(c => c.rules));
    const facet = t0?.facet ?? a.themes[0]?.facet;
    const refl = facet ? this.k.ontology?.facets?.[facet]?.reflection : '';
    this.set('syn.reflect', '');   // the ontology's generic reflection is filler (identical on every chart of a facet); the audit removed it
    void refl;
    this.set('evidence.thin', a.themes.length <= 1 && a.envThemes.length === 0 ? '1' : '');
    this.set('evidence.none', a.themes.length === 0 ? '1' : '');
  }

}

const CAPS: Record<string, number> = { base: 4, support: 3, qualifier_focus: 4, qualifier_other: 2, environment: 3, timing: 3, work_style: 2 };

/** Sentence split that never cuts inside quotes or parentheses. */
export function splitSentences(text: string): string[] {
  const out: string[] = []; let depth = 0, q = false, cur = '';
  for (let i = 0; i < text.length; i++) {
    const ch = text[i]; cur += ch;
    if (ch === '(') depth++; else if (ch === ')') depth = Math.max(0, depth - 1);
    else if (ch === '“') q = true; else if (ch === '”') q = false;
    else if ((ch === '.' || ch === '?') && !depth && !q && (text[i + 1] === ' ' || i === text.length - 1)) { out.push(cur.trim()); cur = ''; }
  }
  if (cur.trim()) out.push(cur.trim());
  return out.filter(Boolean);
}
