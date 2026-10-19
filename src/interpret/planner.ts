// Narrative planner: turns validated evidence into an ARGUMENT GRAPH for one section of a chapter before any sentence exists.
// A section is read from one focus palace (Quan Lộc for Công danh, Tài Bạch for Tài Bạch, ...), its tam phương tứ chính and the person
// (Mệnh / Thân), following the chapter specification (chapters.ts).
//   roles      base (readings on the focus palace's chính tinh) · support (its phụ tinh) · qualifier (limiting readings / sát tinh) ·
//              cross (Mệnh, Thân, chart or tam-phương readings whose subject is this section's facets) · environment (the opposite palace) ·
//              timing (readings about WHEN) · work_style (Công danh only: the person's discipline / ambition)
//   grounds    evidence standing on the same normalised chart facts is ONE ground, whatever the number of books
//   dominance  each opposed (base, qualifier) pair gets a verdict from five public criteria; the verdict states what the books say and what
//              the system's precedence convention is, never more
//   themes     claims are clustered into argued themes: a lead reading, readings that reinforce it, and counter-readings with the relation
//              that ties them (dominance verdict, lexicon relation, refinement or "both hold"); prose is written per theme, not per rule
//   exclusions drafts, readings the books give for another palace, and what the rule set cannot decide
import { ChartGraph, SAT, CAT } from './graph.ts';
import { citeVi, classify, KB, type School } from './dignity.ts';
import { joinVi, rootStars, type Evidence, type Lexicon } from './semantic.ts';
import type { ChapterSpec, SectionSpec } from './chapters.ts';
import type { ChartInput, Finding, Knowledge, Rule } from './types.ts';

export type Role = 'base' | 'support' | 'qualifier' | 'cross' | 'environment' | 'timing' | 'work_style';

export interface Ground { root: string[]; evidence: Evidence[]; books: string[]; cites: string[]; independent: boolean }
export interface Claim {
  id: string; concept: string; facet: string; polarity: '+' | '-' | '~'; palace: string; role: Role;
  grounds: Ground[]; rules: string[]; quotes: string[];
}
export interface Dominance {
  base: Claim; qualifier: Claim; sharedStars: string[]; sameBook: boolean; specificity: 'qualifier' | 'base' | 'none';
  directness: string; verdict: 'qualified_base' | 'both_hold'; criteria: string[];
}
export interface CrossLink { claim: Claim; deps: Array<{ star: string; palace: string }> }
export interface Tension { pos: Claim; neg: Claim; kind: 'refinement' | 'both_hold' }
export interface Counter { claim: Claim; kind: 'qualified' | 'both_hold' | 'refinement' | 'relation'; synth?: string; dominance?: Dominance }
export interface Theme {
  id: string; facet: string; facetName: string; lead: Claim; support: Claim[]; counters: Counter[];
  polarity: '+' | '-' | '~'; salience: number; stars: string[]; palaces: string[];
  /** stars in OTHER palaces that the lead reading stands on (cross-palace dependency, from the chart graph) */
  deps: Array<{ star: string; palace: string }>;
}
export interface ArgumentGraph {
  chapter: string; section: SectionSpec; focus: string; triad: string[]; opposite: string; than: string;
  /** the focus palace's stars and their brightness (Thực Hành table), for the narrative's modifiers */
  focusStars: string[]; focusDignity: Record<string, string>;
  claims: Claim[]; dominance: Dominance[]; cross: CrossLink[]; tensions: Tension[]; timingConflict: { early: Claim[]; late: Claim[] };
  themes: Theme[]; envThemes: Theme[]; restThemes: Theme[];
  slots: Record<string, string>; lists: Record<string, Claim[]>; excluded: { drafts: Array<{ rule: string; text: string }>; scopeNotes: Array<{ rule: string; text: string; palace: string }> };
  evidenceCount: number;
}

const WORK_STYLE = new Set(['identity.ambition', 'identity.discipline']);
const BOOK_PAGE = (c: string) => c.replace(/^TH /, 'Thực Hành tr.').replace(/^KL /, 'Khảo Luận tr.').replace(/^TT /, 'Toàn Thư tr.').replace(/p+\.\s?/, '').replace(/-/g, '–');
const TIMING = (f: string) => f.endsWith('.timing');
const MAX_THEMES = 5;
const EARLY = new Set(['career.early']), LATE = new Set(['career.late', 'life.late_bloom']);

export type RelIndex = Map<string, { type: string; synth?: string }>;
const relCache = new WeakMap<Knowledge, RelIndex>();
export function relIndexOf(k: Knowledge): RelIndex {
  let m = relCache.get(k);
  if (!m) { m = new Map(); for (const r of k.relations.relations) m.set([r.a, r.b].sort().join('|'), { type: r.type, synth: r.synth }); relCache.set(k, m); }
  return m;
}
/** Two narrated readings that pull in opposite directions and must be put side by side: a lexicon 'contradicts' pair (in one palace, or
 *  one of them about the person: Mệnh, Thân, the chart), or the same facet of the same palace with opposite signs. Two readings that go
 *  the same way are never opposed, whatever their concepts. Shared by the planner, the realizer and the validator. */
export function opposedPair(c1: Claim, c2: Claim, rel: RelIndex, person: (palace: string) => boolean): boolean {
  if (c1.polarity === c2.polarity) return false;
  const r = rel.get([c1.concept, c2.concept].sort().join('|'));
  if (r?.type === 'contradicts' && (c1.palace === c2.palace || person(c1.palace) || person(c2.palace))) return true;
  return c1.palace === c2.palace && c1.facet === c2.facet && c1.polarity !== '~' && c2.polarity !== '~';
}

export function plan(chart: ChartInput, ev: Evidence[], g: ChartGraph, lex: Lexicon, k: Knowledge, drafts: Array<{ rule: Rule; claim: string }>,
  fired: Finding[], spec: ChapterSpec, sec: SectionSpec): ArgumentGraph {
  const focus = sec.palace === 'Thân' ? chart.palaces.find(p => p.is_than)!.name : sec.palace;
  const q = g.palace(focus);
  const triad = g.related(focus, 'tam_hop').map(p => p.name);
  const opposite = g.related(focus, 'xung_chieu')[0].name;
  const envPal = sec.envPalace ?? opposite;
  const linked = new Set((sec.linked ?? []).filter(p => p !== focus));
  const than = chart.palaces.find(p => p.is_than)!.name;
  const facetOf = (id: string) => lex.concepts.get(id)!.facet;
  const facets = new Set(sec.facets), envFacets = new Set(sec.envFacets ?? []);
  const isMenhChapter = focus === 'Mệnh';

  // ---------- scope and roles: one primary concept per evidence, so each book sentence is narrated once
  const claimsMap = new Map<string, Claim>();
  const add = (e: Evidence, concept: string, role: Role) => {
    const key = `${role}|${concept}|${e.palace}`;
    let c = claimsMap.get(key);
    if (!c) { c = { id: key, concept, facet: facetOf(concept), polarity: e.polarity, palace: e.palace ?? 'chart', role, grounds: [], rules: [], quotes: [] }; claimsMap.set(key, c); }
    c.rules.push(e.rule.id);
    let gr = c.grounds.find(x => x.root.join('|') === e.root.join('|'));
    if (!gr) { gr = { root: e.root, evidence: [], books: [], cites: [], independent: true }; c.grounds.push(gr); }
    gr.evidence.push(e); gr.books = [...new Set([...gr.books, ...e.books])].sort(); gr.cites = [...new Set([...gr.cites, ...e.cites])];
  };
  const majors = new Set(q.major_stars);
  const frame = new Set([focus, ...triad, opposite]);
  for (const e of ev) {
    if (!e.concepts.length) continue;
    // the primary concept comes from the domain the reading talks about most ("yên phận, tích cóp phòng xa, khá giả nhờ cần kiệm" is about
    // money: two finance concepts against one of temperament), preferring, inside that domain, a facet of this section; a reading of the
    // focus palace keeps its own domain even when the section has no facet there
    const domOf = (id: string) => facetOf(id).split('.')[0];
    const counts = new Map<string, number>();
    for (const c of e.concepts) counts.set(domOf(c.id), (counts.get(domOf(c.id)) ?? 0) + 1);
    const top = Math.max(...counts.values()), dom = e.concepts.map(c => domOf(c.id)).find(d => counts.get(d) === top)!;
    const inDom = e.concepts.filter(c => domOf(c.id) === dom), inSec = (c: { id: string }) => facets.has(facetOf(c.id));
    const primary = e.palace === focus ? (inDom.find(inSec) ?? (top > 1 ? inDom[0] : e.concepts.find(inSec) ?? inDom[0]))
      : (inDom.find(inSec) ?? e.concepts.find(inSec) ?? inDom[0]);
    const pf = facetOf(primary.id);
    // (audit) 'tự tin, dễ bị ganh ghét' at Mệnh is about temperament; its secondary cue 'ganh ghét' (career.support) must not pull a person
    // reading into a palace chapter: when the dominant domain is not the section's, a lone career.support cue does not count
    const secOnly = e.concepts.filter(inSec);
    const incidental = e.palace !== focus && !isMenhChapter && !inDom.some(inSec) && secOnly.length > 0 && secOnly.every(c => facetOf(c.id) === 'career.support');
    const inFacets = !incidental && (facets.has(pf) || e.concepts.some(c => facets.has(facetOf(c.id))));
    if (e.palace === focus) {
      if (TIMING(pf)) { add(e, primary.id, 'timing'); continue; }
      const onSat = e.presentStars.some(s => SAT.includes(s)) || /sát tinh/.test(e.chartCondition);
      const onMajor = e.presentStars.some(s => majors.has(s));
      add(e, primary.id, e.polarity === '-' || onSat ? 'qualifier' : onMajor ? 'base' : 'support');
    } else if (!isMenhChapter && (e.palace === 'Mệnh' || e.palace === than || e.palace === null)) {
      const deps = g.crossDependencies(e.finding.id).filter(d => frame.has(d.palace));
      if (TIMING(pf) && facets.has(pf)) add(e, primary.id, 'timing');
      else if (inFacets) add(e, primary.id, deps.length || e.polarity !== '-' ? 'cross' : 'qualifier');
      else if (spec.id === 'cong_danh' && WORK_STYLE.has(pf)) add(e, primary.id, 'work_style');
    } else if (isMenhChapter && (e.palace === than || e.palace === null || linked.has(e.palace ?? '')) && inFacets) {
      add(e, primary.id, TIMING(pf) ? 'timing' : 'cross');
    } else if (linked.has(e.palace ?? '') && inFacets) {
      add(e, primary.id, TIMING(pf) ? 'timing' : 'cross');
    } else if (e.palace === envPal && !isMenhChapter) {
      if (TIMING(pf) && facets.has(pf)) add(e, primary.id, 'timing');
      else if (envFacets.has(pf) || e.concepts.some(c => envFacets.has(facetOf(c.id)))) add(e, primary.id, 'environment');
    } else if (triad.includes(e.palace ?? '') && inFacets && !isMenhChapter) {
      add(e, primary.id, TIMING(pf) ? 'timing' : 'cross');
    }
  }
  const claims = [...claimsMap.values()];
  // a reading conditioned on 'sát tinh hội' stands on the sát stars actually in the tam phương: name them, and count them in its root
  const satTpStars = g.tamPhuong(focus).flatMap(p => p.stars.filter(st => SAT.includes(st)).map(st => ({ st, p: p.name })));
  // (evidence is shared by every chapter of the chart, so it is copied here, never edited in place)
  for (const c of claims) for (const gr of c.grounds) gr.evidence = gr.evidence.map(e => {
    if (!(e.palace === focus && /sát tinh hội về/.test(e.chartCondition) && satTpStars.length)) return e;
    gr.root = [...new Set([...gr.root, ...satTpStars.map(x => `tp:${x.st}`)])].sort();
    return { ...e, chartCondition: e.chartCondition.replace(/sát tinh hội về ([^,]+)/, `sát tinh ${joinVi(satTpStars.map(x => x.p === focus ? x.st : `${x.st} (từ ${x.p})`))} hội về $1`),
      presentStars: [...new Set([...e.presentStars, ...satTpStars.map(x => x.st)])] };
  });
  for (const c of claims) {
    c.grounds.sort((a, b) => a.root.length - b.root.length || a.root.join().localeCompare(b.root.join()));
    c.grounds.forEach((gr, i) => { gr.independent = !c.grounds.slice(0, i).some(o => [...rootStars(o.root)].some(st => rootStars(gr.root).has(st))); });
    c.polarity = c.grounds.flatMap(x => x.evidence).some(e => e.polarity === '-') && c.role === 'qualifier' ? '-' : c.polarity;
    c.quotes = [...new Set(c.grounds.flatMap(x => x.evidence.map(e => e.core)))];
  }

  // ---------- dominance between the focus palace's base readings and its qualifiers
  const dominance: Dominance[] = [];
  const bases = claims.filter(c => c.role === 'base' && c.polarity !== '-');
  for (const qual of claims.filter(c => c.role === 'qualifier' && c.palace === focus)) {
    const qe = qual.grounds.flatMap(x => x.evidence);
    const best = bases.map(b => {
      const be = b.grounds.flatMap(x => x.evidence);
      const shared = [...new Set(qe.flatMap(e => e.presentStars).filter(s => be.some(x => x.presentStars.includes(s)) && majors.has(s)))];
      const sameBook = qe.some(e => be.some(x => x.books.some(bk => e.books.includes(bk))));
      const related = shared.length > 0 || b.facet === qual.facet || relIndexOf(k).has([b.concept, qual.concept].sort().join('|'));
      return { b, shared, sameBook, related, score: shared.length * 2 + (sameBook ? 1 : 0) + (b.facet === qual.facet ? 3 : 0) };
    })
      // a qualifier is weighed only against a reading it can limit: one on the same major star, of the same facet, or related in the
      // lexicon ("học nhiều nhưng khó đạt thành tựu" does not limit "uy quyền hiển hách" just because both sit in Mệnh)
      .filter(x => x.related)
      .sort((a, b) => b.score - a.score || a.b.id.localeCompare(b.b.id))[0];
    if (!best) continue;
    const qr = new Set(qe[0].root), br = new Set(best.b.grounds[0].root);
    const specificity = [...br].every(a => qr.has(a)) && qr.size > br.size ? 'qualifier' : [...qr].every(a => br.has(a)) && br.size > qr.size ? 'base' : 'none';
    const qualOnSat = qe.some(e => e.presentStars.some(s => SAT.includes(s)) || /sát tinh/.test(e.chartCondition));
    const criteria = [
      best.shared.length ? `cùng nói về ${joinVi(best.shared)}` : 'không cùng một chính tinh',
      best.sameBook ? 'cùng một sách' : 'hai sách khác nhau',
      specificity === 'qualifier' ? 'câu hạn chế có điều kiện cụ thể hơn' : specificity === 'base' ? 'câu nền có điều kiện cụ thể hơn' : 'không câu nào bao trùm điều kiện của câu kia',
      qualOnSat ? 'câu hạn chế đứng trên sát tinh, câu nền đứng trên chính tinh' : 'cả hai đứng trên chính tinh',
      `${best.b.grounds.filter(x => x.independent).length} căn cứ độc lập cho câu nền, ${qual.grounds.filter(x => x.independent).length} cho câu hạn chế`,
    ];
    dominance.push({ base: best.b, qualifier: qual, sharedStars: best.shared, sameBook: best.sameBook, specificity,
      directness: `cả hai đọc ngay tại cung ${focus}`, verdict: qualOnSat || specificity === 'qualifier' ? 'qualified_base' : 'both_hold', criteria });
  }

  // ---------- tensions: opposed readings outside the base/qualifier pairs, classified by their facts
  const relIndex = relIndexOf(k);
  const covered = new Set(dominance.flatMap(d => [d.base.id + '|' + d.qualifier.id, d.qualifier.id + '|' + d.base.id]));
  const tensions: Tension[] = [];
  for (const c1 of claims) for (const c2 of claims) {
    if (c1.id >= c2.id || covered.has(c1.id + '|' + c2.id) || c1.role === 'timing' || c2.role === 'timing') continue;
    const person = (p: string) => p === 'Mệnh' || p === than || p === 'chart';
    if (!opposedPair(c1, c2, relIndex, person) || c1.polarity === '~' || c2.polarity === '~') continue;
    const [pos, neg] = c1.polarity === '-' ? [c2, c1] : [c1, c2];
    const rp = new Set(pos.grounds[0].root), rn = new Set(neg.grounds[0].root);
    tensions.push({ pos, neg, kind: [...rp].every(x => rn.has(x)) && rn.size > rp.size ? 'refinement' : 'both_hold' });
  }
  const timingClaims = claims.filter(c => c.role === 'timing');
  const early = timingClaims.filter(c => EARLY.has(c.concept)), late = timingClaims.filter(c => LATE.has(c.concept));

  // ---------- cross-palace links read from the graph
  const cross: CrossLink[] = claims.filter(c => c.role === 'cross').sort((x, y) => y.grounds.length - x.grounds.length || x.id.localeCompare(y.id)).map(c => ({ claim: c,
    deps: c.grounds.flatMap(x => x.evidence).flatMap(e => g.crossDependencies(e.finding.id)).filter(d => d.necessary === true).filter((d, i, a) => a.findIndex(o => o.star === d.star) === i) }));

  // ---------- themes
  const sal = (c: Claim) => c.grounds.filter(x => x.independent).length * 10 + ({ base: 6, qualifier: 5, cross: 4, support: 3, work_style: 2, environment: 3, timing: 1 }[c.role]) +
    new Set(c.grounds.flatMap(x => x.books)).size;
  const themesOf = (pool: Claim[], tag: string): Theme[] => {
    const used = new Set<string>(), out: Theme[] = [];
    // (audit) two claims that quote the same sentence (two rules, or one reading read from two palaces) are one narrated reading: the weaker
    // is folded into the stronger as further grounds, so a quote is never narrated in two themes
    const sorted: Claim[] = [];
    for (const c of [...pool].sort((a, b) => sal(b) - sal(a) || a.id.localeCompare(b.id))) {
      const twin = sorted.find(o => o.polarity === c.polarity && c.quotes.every(q => o.quotes.includes(q)));
      if (twin) { twin.grounds.push(...c.grounds.filter(gr => !twin.grounds.includes(gr))); twin.rules.push(...c.rules); } else sorted.push(c);
    }
    const relOf = (a: Claim, b: Claim) => relIndex.get([a.concept, b.concept].sort().join('|'));
    const counterOf = (lead: Claim, members: Claim[], c: Claim): Counter | null => {
      const d = dominance.find(x => x.qualifier.id === c.id && [lead, ...members].some(m => m.id === x.base.id));
      if (d) return { claim: c, kind: d.verdict === 'qualified_base' ? 'qualified' : 'both_hold', dominance: d };
      if (![lead, ...members].some(m => m.palace === c.palace)) return null;
      const r = [lead, ...members].map(m => relOf(m, c)).find(x => x && ['qualifies', 'contradicts', 'tempers', 'conditions'].includes(x.type));
      if (r) return { claim: c, kind: 'relation', synth: r.synth };
      if (![lead, ...members].some(m => m.facet === c.facet)) return null;
      const t = tensions.find(x => x.neg.id === c.id && [lead, ...members].some(m => m.id === x.pos.id));
      return { claim: c, kind: t?.kind === 'refinement' ? 'refinement' : 'both_hold' };
    };
    const starsOf = (cs: Claim[]) => [...new Set(cs.flatMap(c => c.grounds.flatMap(gr => gr.evidence.flatMap(e => e.presentStars))))];
    const mk = (lead: Claim, support: Claim[], counters: Counter[], polarity: Theme['polarity']): Theme => ({
      id: `${tag}:${lead.id}`, facet: lead.facet, facetName: k.ontology?.facets?.[lead.facet]?.name ?? lead.facet, lead, support, counters, polarity,
      salience: [lead, ...support].reduce((n, c) => n + sal(c), 0), stars: starsOf([lead, ...support]), palaces: [...new Set([lead, ...support].map(c => c.palace))],
      deps: lead.grounds[0].evidence.flatMap(e => g.crossDependencies(e.finding.id)).filter(d => d.necessary === true).filter((d, i, a) => a.findIndex(o => o.star === d.star) === i) });
    // 1. positive / neutral themes: a lead and up to three readings of the same facet that go the same way; a reading whose words are the
    //    same as one already in the theme (two rules giving the same sentence) is folded into it as a further ground, not narrated twice
    for (const lead of sorted) {
      if (used.has(lead.id) || lead.polarity === '-') continue;
      used.add(lead.id);
      const support: Claim[] = [];
      for (const c of sorted) {
        if (used.has(c.id) || c.facet !== lead.facet || !(c.polarity === lead.polarity || (lead.polarity === '+' && c.polarity === '~'))) continue;
        // a mixed reading whose concept the lexicon opposes to the lead's (or a member's) is not "the same way"
        if ([lead, ...support].some(m => opposedPair(m, c, relIndex, p => p === 'Mệnh' || p === than || p === 'chart'))) continue;
        if (c.quotes.every(q => [lead, ...support].some(m => m.quotes.includes(q)))) { lead.grounds.push(...c.grounds); lead.rules.push(...c.rules); used.add(c.id); continue; }
        if (support.length < 3) { support.push(c); used.add(c.id); }
      }
      out.push(mk(lead, support, [], '+'));
    }
    // 2. each limiting reading goes to the theme it argues with most directly — a dominance pair, then the same facet (same palace first),
    //    then a lexicon relation — assigned best link first over all pairs; a theme takes at most three; the rest become themes of their own
    const links: Array<{ c: Claim; t: Theme; score: number; ct: Counter }> = [];
    for (const c of sorted) {
      if (used.has(c.id) || c.polarity !== '-') continue;
      for (const t of out) {
        const ct = counterOf(t.lead, t.support, c);
        if (!ct) continue;
        const members = [t.lead, ...t.support];
        // same facet weighs most (the reader must see the two sides of one question together), then same palace, a dominance pair, a relation
        const score = (members.some(m => m.facet === c.facet) ? 3 : 0) + (members.some(m => m.palace === c.palace) ? 1 : 0) + (ct.dominance ? 2 : 0) + (ct.kind === 'relation' ? 1 : 0);
        links.push({ c, t, score, ct });
      }
    }
    links.sort((x, y) => y.score - x.score || sal(y.c) - sal(x.c) || x.c.id.localeCompare(y.c.id) || x.t.id.localeCompare(y.t.id));
    for (const l of links) {
      if (used.has(l.c.id) || l.t.counters.length >= 4) continue;
      l.t.counters.push(l.ct); used.add(l.c.id);
    }
    for (const lead of sorted) {
      if (used.has(lead.id)) continue;
      used.add(lead.id);
      const support = sorted.filter(c => !used.has(c.id) && c.facet === lead.facet && c.polarity === lead.polarity).slice(0, 2);
      support.forEach(c => used.add(c.id));
      out.push(mk(lead, support, [], lead.polarity));
    }
    const pos = out.filter(t => t.polarity !== '-').sort((a, b) => b.salience - a.salience || a.id.localeCompare(b.id));
    const neg = out.filter(t => t.polarity === '-').sort((a, b) => b.salience - a.salience || a.id.localeCompare(b.id));
    return [...pos, ...neg];
  };
  // one pool, so a limiting reading in Mệnh can stand next to the environment reading it pulls against (and vice versa)
  const allThemes = themesOf(claims.filter(c => ['base', 'support', 'qualifier', 'cross', 'work_style', 'environment'].includes(c.role)), 'core');
  const coreThemes = allThemes.filter(t => t.lead.role !== 'environment');
  const themes = coreThemes.slice(0, MAX_THEMES), restThemes = coreThemes.slice(MAX_THEMES);
  const envThemes = allThemes.filter(t => t.lead.role === 'environment').slice(0, 3);

  // ---------- exclusions
  const inScope = (pal: string | null) => pal === focus || pal === 'Mệnh' || pal === than || pal === opposite || triad.includes(pal ?? '');
  const draftsOut = drafts.filter(d => inScope(d.rule.subject === 'palace' ? draftPalace(d.rule) : null) && inSectionFacets(d.rule, lex, facetOf, facets, focus, draftPalace(d.rule)))
    .map(d => ({ rule: d.rule.id, text: (d.rule.reading ?? k.claims[d.claim] ?? d.claim).replace(/\s*\[[^\]]*\]/g, '') }));
  const scopeNotes = isMenhChapter ? [] : scopeNotesFor(q.major_stars, q.branch, k).map(r => ({ rule: r.id, text: (r.reading ?? '').replace(/\s*\[[^\]]*\]/g, ''), palace: 'Mệnh' }))
    .filter(n => n.text.trim());

  // ---------- slots (chart facts for the templates; empty string = the passage needing it is skipped)
  const dig = (p: typeof q, s: string) => { const d = p.major_dignity[s] ?? p.minor_dignity[s]; return d ? `${s} (${d})` : s; };
  const majorsDig = (name: string) => { const p = g.palace(name); return p.major_stars.length ? joinVi(p.major_stars.map(s => dig(p, s))) : ''; };
  const notable = (name: string) => g.palace(name).stars.filter(s => SAT.includes(s) || CAT.includes(s));
  const tt = (name: string) => { const p = g.palace(name); return [p.tuan && 'Tuần', p.triet && 'Triệt'].filter(Boolean).join(' và '); };
  const satTp = g.tamPhuong(focus).flatMap(p => p.stars.filter(s => SAT.includes(s)).map(s => `${s} ở ${p.name === focus ? 'ngay cung ' + focus : 'cung ' + p.name}`));
  // decades that start after 85 tuổi mụ are computed but not narrated: nothing useful can be said about them
  const dFocus = chart.decades.find(d => d.palace === focus && d.age_from <= 85);
  const dNow = chart.year.dai_han;
  const hoaInto = chart.decades.filter(d => d.age_to >= chart.year.age_tuoi_mu && d.age_from <= 85)
    .flatMap(d => Object.entries(d.hoa).filter(([, v]) => v.palace === focus).map(([h, v]) => `đại hạn ${d.age_from}–${d.age_to} (can ${d.stem}) đưa ${h} vào ${v.star}`)).slice(0, 3);
  const profiles = q.major_stars.map(s => ({ s, p: k.starProfiles.stars[s] })).filter(x => x.p);
  const ref = k.reference;
  const role = ref?.palaceRoles.roles[focus] ?? '';
  const hoaHere = Object.entries(chart.tu_hoa).filter(([, v]) => g.byBranch.get(v.branch)!.name === focus);
  const hoaNotes = hoaHere.map(([h, v]) => {
    const spec = ref?.tuHoa.byPalace?.[h]?.[focus];
    return spec ? `${h} (${v.star}) ở ${focus} thì ${spec}` : '';
  }).filter(Boolean);
  const stage = (ref && dFocus) ? (chart.dai_han_direction === 'thuận' ? ref.lifeStages.thuan : ref.lifeStages.nghich)[focus] ?? '' : '';
  const nowStage = (ref && dNow) ? (chart.dai_han_direction === 'thuận' ? ref.lifeStages.thuan : ref.lifeStages.nghich)[dNow.palace] ?? '' : '';
  // the page of the book the level actually came from (Toàn Thư under that school), from the shared dignity knowledge base
  const school = ((chart as { dignity_school?: School }).dignity_school ?? KB.default_school) as School;
  const digLoc = (s: string) => { const r = classify(s, q.branch, school); return r.status === 'VERIFIED' ? citeVi(r.locator) : ''; };
  const digFacts = q.major_stars.filter(s => q.major_dignity[s]).map(s => `${s} ở ${q.branch} được xếp ${q.major_dignity[s]}${digLoc(s) ? ` (${digLoc(s)})` : ''}`);
  const slots: Record<string, string> = {
    'chapter.title': spec.title, 'chapter.scope': spec.scope, 'topic': sec.topic,
    'f.name': focus, 'f.where': `${q.stem} ${q.branch}`, 'f.branch': q.branch, 'f.majors': joinVi(q.major_stars), 'f.majors_dig': majorsDig(focus),
    'f.no_major': q.major_stars.length ? '' : '1', 'f.sat': joinVi(notable(focus).filter(s => SAT.includes(s))), 'f.cat': joinVi(notable(focus).filter(s => CAT.includes(s))),
    'f.minor': joinVi([...notable(focus).filter(s => CAT.includes(s)), ...notable(focus).filter(s => SAT.includes(s))]),
    'f.hoa': joinVi(g.hoaIn(focus)), 'f.tt': tt(focus), 'f.sat_tp': joinVi(satTp), 'f.pair': q.major_stars.length === 2 ? '1' : '',
    'f.role': role, 'f.role_cite': role ? 'Khảo Luận tr.214–220' : '', 'f.is_menh': isMenhChapter ? '1' : '',
    'f.dignity': joinVi(digFacts), 'f.hoa_notes': hoaNotes.join('; '),
    'f.opp_borrow': q.major_stars.length ? '' : majorsDig(opposite),
    'menh.majors_dig': majorsDig('Mệnh') || 'không có chính tinh', 'menh.hoa': joinVi(g.hoaIn('Mệnh')),
    'triad.a': triad[0], 'triad.b': triad[1], 'triad.a_majors': majorsDig(triad[0]) || 'vô chính diệu', 'triad.b_majors': majorsDig(triad[1]) || 'vô chính diệu',
    'triad.a_notable': joinVi(notable(triad[0])), 'triad.b_notable': joinVi(notable(triad[1])),
    'env.name': envPal, 'env.is_opp': envPal === opposite ? '1' : '', 'env.majors_dig': majorsDig(envPal) || 'không có chính tinh',
    'opp.name': opposite, 'opp.majors_dig': majorsDig(opposite) || 'không có chính tinh', 'opp.notable': joinVi([...notable(opposite), ...(tt(opposite) ? [tt(opposite)] : [])]),
    'than.palace': than, 'than.is_focus': than === focus ? '1' : '', 'than.is_opp': than === opposite ? '1' : '', 'than.in_triad': triad.includes(than) ? '1' : '',
    'than.majors_dig': majorsDig(than) || 'không có chính tinh',
    'profiles': profiles.map(({ s, p }) => `${s} ${p!.dau ? 'là ' + p!.dau.toLowerCase() : ''}${p!.domain ? ', chủ về ' + p!.domain : ''}`).join('; '),
    'profiles.cite': mergePages([...new Set(profiles.map(x => x.p!.locator).filter(Boolean))].map(c => BOOK_PAGE(String(c)))),
    'dh.focus': dFocus ? `${dFocus.age_from}–${dFocus.age_to}` : '', 'dh.focus_stem': dFocus?.stem ?? '', 'dh.focus_stage': stage,
    'dh.focus_readings': dFocus ? dFocus.readings.filter(r => !r.text.startsWith('Hai điều kiện trái chiều')).map(r => `“${r.text.replace(/\.$/, '').replace(/\btheo sách (đây |là )?/g, '')}” (${r.src.replace(/pp?\.\s?/, 'tr.').replace(/-/g, '–')})`).join('; ') : '',
    'dh.focus_conflict': dFocus && dFocus.readings.some(r => r.text.startsWith('Hai điều kiện trái chiều')) ? '1' : '',
    'dh.now': dNow ? `cung ${dNow.palace} (${dNow.age_from}–${dNow.age_to} tuổi mụ)` : '', 'dh.now_stage': nowStage, 'dh.now_is_focus': dNow?.palace === focus ? '1' : '',
    'dh.passed': dFocus && chart.year.age_tuoi_mu > dFocus.age_to ? '1' : '', 'dh.before': dFocus && chart.year.age_tuoi_mu < dFocus.age_from ? '1' : '',
    'year': String(chart.year.year), 'age': String(chart.year.age_tuoi_mu), 'hoa_into': joinVi(hoaInto),
  };
  const groups = Object.entries(ref?.groupNotes.members ?? {}).filter(([, ms]) => q.major_stars.some(s => ms.includes(s)));
  slots['f.group'] = joinVi(groups.map(([gname]) => `${gname} (${ref!.groupNotes.notes[gname] ?? ''})`.replace(' ()', '')));
  slots['f.group_stars'] = joinVi(q.major_stars.filter(s => groups.some(([, ms]) => ms.includes(s))));
  slots['menh.cuc'] = chart.cuc?.name ?? ''; slots['menh.nap_am'] = chart.menh_nap_am ?? ''; slots['menh.cuc_rel'] = chart.menh_cuc_relation ?? '';
  slots['menh.branch'] = g.palace('Mệnh').branch; slots['than.differs'] = than !== 'Mệnh' ? '1' : '';
  const TPVT = ['Tử Vi', 'Thiên Phủ', 'Vũ Khúc', 'Thiên Tướng'];
  const groupRule = fired.find(f => f.claim === 'menh_nhom_tu_phu_vu_tuong' && f.basis === 'verified');
  slots['group.same'] = spec.id === 'cong_danh' && groupRule && q.major_stars.length && q.major_stars.every(s => TPVT.includes(s)) ? '1' : '';
  slots['group.rule'] = groupRule?.ruleId ?? '';
  const lists: Record<string, Claim[]> = {};
  for (const r of ['base', 'support', 'qualifier', 'cross', 'environment', 'timing', 'work_style'] as Role[])
    lists[r] = claims.filter(c => c.role === r).sort((x, y) => sal(y) - sal(x) || x.id.localeCompare(y.id));
  const focusDignity: Record<string, string> = {};
  for (const [st, d] of Object.entries({ ...q.minor_dignity, ...q.major_dignity })) if (d && d !== 'unspecified') focusDignity[st] = d;
  return { chapter: spec.id, section: sec, focus, triad, opposite, than, focusStars: q.stars, focusDignity, claims, dominance, cross, tensions, timingConflict: { early, late },
    themes, envThemes, restThemes, slots, lists, excluded: { drafts: draftsOut, scopeNotes }, evidenceCount: ev.length };
}

/** "Thực Hành tr.29–30; tr.44": one book name, its pages in order of appearance */
function mergePages(cs: string[]): string {
  const by = new Map<string, string[]>();
  for (const c of cs) { const m = c.match(/^(.+?) (tr\..+)$/); const b = m ? m[1] : c; by.set(b, [...(by.get(b) ?? []), ...(m ? [m[2]] : [])]); }
  return [...by].map(([b, ps]) => ps.length ? `${b} ${ps.join('; ')}` : b).join('; ');
}

function draftPalace(r: Rule): string | null {
  const walk = (e: any): string | null => e?.fact === 'palace.name' ? String(e.value) : (e?.all ?? e?.any ?? []).map(walk).find(Boolean) ?? null;
  return walk(r.conditions);
}
function inSectionFacets(r: Rule, lex: Lexicon, facetOf: (id: string) => string, facets: Set<string>, focus: string, pal: string | null): boolean {
  if (pal === focus) return true;
  return lex.match(r.reading ?? '').some(c => facets.has(facetOf(c.id)));
}
/** Verified rules the books give for the SAME chính tinh combination in the Mệnh palace: shown as "not applied here" notes. */
function scopeNotesFor(majors: string[], branch: string, k: Knowledge): Rule[] {
  if (!majors.length) return [];
  const positive = (e: any, out: { palace?: string; stars: Set<string>; branches?: string[] }) => {
    if (!e || typeof e !== 'object' || e.not) return out;
    if (e.fact === 'palace.name') out.palace = String(e.value);
    if ((e.fact === 'palace.own_major_stars' || e.fact === 'palace.own_stars') && (e.operator ?? 'eq') === 'contains') out.stars.add(String(e.value));
    if (e.fact === 'palace.branch' && e.operator === 'in') out.branches = e.value;
    (e.all ?? []).forEach((x: any) => positive(x, out));
    return out;
  };
  return k.rules.filter(r => {
    if (r.system !== 'tu_vi' || r.reviewStatus !== 'verified') return false;
    const f = positive(r.conditions, { stars: new Set() });
    return f.palace === 'Mệnh' && majors.every(m => f.stars.has(m)) && f.stars.size === majors.length && (!f.branches || f.branches.includes(branch));
  }).sort((a, b) => a.id < b.id ? -1 : 1).slice(0, 3);          // order by id: identical whichever store (bundle or D1) loaded the rules
}
