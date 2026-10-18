// Narrative planner: turns validated evidence into an ARGUMENT GRAPH before any sentence exists. One planner serves every chapter
// (chapters.ts says which palace, which facets, where the environment is read).
//   central configuration  -> the focus palace, its stars (brightness, Tứ Hóa), Tuần/Triệt and its tam phương tứ chính
//   roles                  -> base (readings on the palace's chính tinh), support (phụ tinh), qualifier (limiting readings or readings
//                             standing on sát tinh), cross (readings of a linked palace that NEED a star of the focus frame — tested
//                             counterfactually), link (in-scope readings of a linked palace that stand on that palace alone),
//                             environment, timing, work_style
//   grounds                -> evidence standing on the same normalised chart facts is ONE ground, whatever the number of books
//   dominance              -> each limiting reading of the focus palace is set against the favourable readings it opposes; the relation
//                             (narrower condition, added sát tinh, both hold) is computed from the satisfied conditions, and the text
//                             says that the precedence is the system's stated convention, never the books'
//   tensions               -> other opposed readings, grouped by their limiting side, with which side is the narrower case
//   timing                 -> early vs late readings; a lean is stated only when one side is absent or rests on a generic condition
//                             (year branch / gender) while the other rests on stars of this chart
//   exclusions             -> drafts, readings the books give for another palace, and what the rule set cannot decide
import { ChartGraph, SAT, CAT } from './graph.ts';
import { joinVi, rootStars, splitReading, condText, type Evidence, type Lexicon } from './semantic.ts';
import { SPECS, inFacets, type ChapterId, type ChapterSpec } from './chapters.ts';
import type { ChartInput, Finding, Knowledge, Palace, Rule } from './types.ts';

export type Role = 'base' | 'support' | 'qualifier' | 'cross' | 'link' | 'environment' | 'timing' | 'work_style' | 'generic';

export interface Ground { root: string[]; evidence: Evidence[]; books: string[]; cites: string[]; independent: boolean }
export interface Claim {
  id: string; concept: string; facet: string; polarity: '+' | '-' | '~'; palace: string; role: Role;
  grounds: Ground[]; rules: string[]; quotes: string[];
}
export type DomRelation = 'specific_qualifier' | 'sat_qualifier' | 'specific_base' | 'both_hold';
export interface Dominance {
  qualifier: Claim; bases: Claim[]; base: Claim; sharedStars: string[]; sameBook: boolean; sameSection: boolean; books: string[]; cites: string[];
  relation: DomRelation; qualEvidence: Evidence; baseEvidence: Evidence; criteria: string[]; addedSat: string[];
  /** compatibility with the first output contract */ verdict: 'qualified_base' | 'both_hold';
}
export interface Dep { star: string; palace: string; necessary: boolean | null }
export interface CrossLink { claim: Claim; evidence: Evidence; deps: Dep[]; support: Dep[] }
export interface Tension { pos: Claim[]; posAll: Claim[]; neg: Claim; negs: Claim[]; kind: 'neg_refines' | 'pos_refines' | 'both_hold' }
export interface TimingView { early: Claim[]; late: Claim[]; lean: 'early' | 'late' | null; leanReason: 'one_side' | 'specific' | 'generic_only' | null }
export interface ArgumentGraph {
  chapter: ChapterId; spec: ChapterSpec; career: string; focus: string; triad: string[]; opposite: string;
  claims: Claim[]; dominance: Dominance[]; cross: CrossLink[]; links: CrossLink[]; tensions: Tension[]; timing: TimingView;
  timingConflict: { early: Claim[]; late: Claim[] };
  slots: Record<string, string>; lists: Record<string, Claim[]>;
  excluded: { drafts: Array<{ rule: string; text: string; neg?: boolean }>; scopeNotes: Array<{ rule: string; text: string; palace: string }> };
  evidenceCount: number;
}

const BOOK_PAGE = (c: string) => c.replace(/^TH /, 'Thực Hành tr.').replace(/^KL /, 'Khảo Luận tr.').replace(/^TT /, 'Toàn Thư tr.').replace(/p+\.\s?/, '').replace(/-/g, '–');
/** Effective condition of a piece of evidence: the stars, brightness and branch the chart actually satisfied (used for 'narrower case'). */
export const effRoot = (e: Evidence) => new Set([...e.presentStars.map(s => 's:' + s), ...(e.cond.branch ? ['b:' + e.cond.branch.branch] : []),
  ...Object.keys(e.cond.dig).map(d => 'd:' + d), ...e.cond.tt.map(t => 't:' + t), ...e.cond.extra.map(x => 'x:' + x)]);
const superset = (a: Set<string>, b: Set<string>) => a.size > b.size && [...b].every(x => a.has(x));

export function plan(chart: ChartInput, ev: Evidence[], g: ChartGraph, lex: Lexicon, k: Knowledge, drafts: Array<{ rule: Rule; claim: string }>,
  fired: Finding[] = [], chapter: ChapterId = 'cong_danh'): ArgumentGraph {
  const spec = SPECS[chapter], focus = spec.focus;
  const q = g.palace(focus);
  const triad = g.related(focus, 'tam_hop').map(p => p.name);
  const opposite = g.related(focus, 'xung_chieu')[0].name;
  const frame = [focus, ...triad, opposite];
  const than = chart.palaces.find(p => p.is_than)!.name;
  const links = [...new Set(spec.links.map(l => l === 'Thân' ? than : l))].filter(p => p !== focus);
  const facetOf = (id: string) => lex.concepts.get(id)!.facet;
  const tt = (name: string) => { const p = g.palace(name); return [p.tuan && 'Tuần', p.triet && 'Triệt'].filter(Boolean).join(' và '); };
  const inScope = (id: string) => inFacets(facetOf(id), spec.facets);

  // ---------- roles: one primary concept per evidence, so each book sentence is narrated once
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
  const depsOf = (e: Evidence) => g.crossDependencies(e.finding.id).filter(d => frame.includes(d.palace));
  const delegated: Evidence[] = [];
  for (const e of ev) {
    if (!e.concepts.length || /độ số/.test(e.core)) continue;
    const scoped = e.concepts.filter(c => inScope(c.id));
    const isTiming = (id: string) => inFacets(facetOf(id), spec.timing.facets) || spec.timing.early.includes(id) || spec.timing.late.includes(id);
    if (e.palace === focus) {
      if (spec.focusFacets && !e.concepts.some(c => inFacets(facetOf(c.id), spec.focusFacets!))) { delegated.push(e); continue; }
      const primary = (spec.focusFacets ? e.concepts.find(c => inFacets(facetOf(c.id), spec.focusFacets!)) : undefined) ?? scoped[0] ?? e.concepts[0];
      if (isTiming(primary.id)) { add(e, primary.id, 'timing'); continue; }
      if (e.generic) { add(e, primary.id, 'generic'); continue; }
      const onSat = e.presentStars.some(s => SAT.includes(s)) || e.cond.extra.includes('sát tinh hội về');
      const onMajor = e.presentStars.some(s => majors.has(s));
      add(e, primary.id, e.polarity === '-' || (onSat && e.polarity === '~') ? 'qualifier' : onMajor && !onSat ? 'base' : 'support');
    } else if (links.includes(e.palace ?? '') || e.palace === null) {
      const timing = e.concepts.find(c => isTiming(c.id));
      if (timing) { add(e, timing.id, 'timing'); continue; }
      if (e.palace === null) { const ws = e.concepts.find(c => inFacets(facetOf(c.id), spec.workStyle)); if (ws) add(e, ws.id, 'work_style'); continue; }
      if (!scoped.length) { const ws = e.concepts.find(c => inFacets(facetOf(c.id), spec.workStyle)); if (ws) add(e, ws.id, 'work_style'); continue; }
      const deps = depsOf(e);
      add(e, scoped[0].id, deps.some(d => d.necessary === true) ? 'cross' : e.polarity === '-' ? 'qualifier' : 'link');
    } else if (spec.env && e.palace === spec.env.palace) {
      const timing = e.concepts.find(c => isTiming(c.id));
      const envc = e.concepts.find(c => inFacets(facetOf(c.id), spec.env!.facets));
      if (timing) add(e, timing.id, 'timing'); else if (envc) add(e, envc.id, 'environment');
    } else if (spec.frameLinks && frame.includes(e.palace ?? '') && scoped.length && scoped[0] === e.concepts[0]) {   // the reading must be ABOUT the topic, not mention it
      add(e, scoped[0].id, isTiming(scoped[0].id) ? 'timing' : 'link');
    }
  }
  const claims = [...claimsMap.values()];
  // a reading conditioned on 'sát tinh hội' stands on the sát stars actually in the tam phương: name them, and count them in its root
  const satTpStars = g.tamPhuong(focus).flatMap(p => p.stars.filter(st => SAT.includes(st)).map(st => ({ st, p: p.name })));
  for (const c of claims) for (const gr of c.grounds) for (const e of gr.evidence) {
    const i = e.cond.extra.indexOf('sát tinh hội về');
    if (e.palace === focus && i >= 0 && satTpStars.length) {
      e.cond.extra[i] = `sát tinh ${joinVi(satTpStars.map(x => x.p === focus ? x.st : `${x.st} (từ ${x.p}${tt(x.p) ? ', nơi có ' + tt(x.p) : ''})`))} hội về`;
      e.chartCondition = condText(e.cond);
      e.presentStars = [...new Set([...e.presentStars, ...satTpStars.map(x => x.st)])];
      gr.root = [...new Set([...gr.root, ...satTpStars.map(x => `tp:${x.st}`)])].sort();
    }
  }
  for (const c of claims) for (const e of evOf0(c)) {
    for (const key of ['tp', 'opp'] as const) e.cond[key] = e.cond[key].map(st => {
      const at = g.starAt.get(st);
      return at && at !== e.palace && tt(at) && !/\(từ /.test(st) ? `${st} (từ ${at}, nơi có ${tt(at)})` : st;
    });
    e.chartCondition = condText(e.cond);
  }
  for (const c of claims) {
    c.grounds.sort((a, b) => a.root.length - b.root.length || a.root.join().localeCompare(b.root.join()));
    c.grounds.forEach((gr, i) => { gr.independent = !c.grounds.slice(0, i).some(o => [...rootStars(o.root)].some(st => rootStars(gr.root).has(st))); });
    c.polarity = c.grounds.flatMap(x => x.evidence).some(e => e.polarity === '-') && c.role === 'qualifier' ? '-' : c.polarity;
    c.quotes = [...new Set(c.grounds.flatMap(x => x.evidence.map(e => e.core)))];
  }

  // ---------- dominance: each limiting reading of the focus palace against the favourable readings it opposes
  const dominance: Dominance[] = [];
  const contraRel = new Set(k.relations.relations.filter(r => r.type === 'contradicts').map(r => [r.a, r.b].sort().join('|')));
  const OUTCOME = ['career', 'finance', 'life'];
  const comparable = (a: Claim, b: Claim) => a.facet === b.facet || contraRel.has([a.concept, b.concept].sort().join('|')) ||
    (OUTCOME.includes(a.facet.split('.')[0]) && OUTCOME.includes(b.facet.split('.')[0]));
  const bases = claims.filter(c => c.role === 'base' && c.polarity !== '-');
  const evOf = (c: Claim) => c.grounds.flatMap(x => x.evidence);
  for (const qual of claims.filter(c => c.role === 'qualifier' && c.palace === focus)) {
    const qe = evOf(qual);
    const sharing = bases.filter(b => comparable(b, qual)).map(b => ({ b, shared: [...new Set(qe.flatMap(e => e.presentStars).filter(s => majors.has(s) && evOf(b).some(x => x.presentStars.includes(s))))] }));
    const opposed = sharing.filter(x => x.shared.length);
    if (!opposed.length) continue;
    // the evidence pair that decides the relation: a narrower qualifier first, then a sát-based one, then a narrower base
    let rel: DomRelation = 'both_hold', pair: [Evidence, Evidence] = [evOf(opposed[0].b)[0], qe[0]];
    const pairs = opposed.flatMap(o => evOf(o.b).flatMap(be => qe.map(x => [be, x] as [Evidence, Evidence])));
    const extraOnlySat = (be: Evidence, x: Evidence) => { const b = effRoot(be); return [...effRoot(x)].filter(a => !b.has(a)).every(a => a.startsWith('s:') && SAT.includes(a.slice(2))); };
    const pq = pairs.find(([be, x]) => superset(effRoot(x), effRoot(be)) && !extraOnlySat(be, x));
    const ps = pairs.find(([be, x]) => x.presentStars.some(s => SAT.includes(s) && !be.presentStars.includes(s)) && x.presentStars.some(s => be.presentStars.includes(s)));
    const pb = pairs.find(([be, x]) => superset(effRoot(be), effRoot(x)));
    if (pq) { rel = 'specific_qualifier'; pair = pq; } else if (ps) { rel = 'sat_qualifier'; pair = ps; } else if (pb) { rel = 'specific_base'; pair = pb; }
    const [be, xe] = pair;
    const shared = [...new Set(opposed.flatMap(o => o.shared))];
    const sameBook = be.books.some(b => xe.books.includes(b));
    const basesSorted = opposed.map(o => o.b).sort((a, b) => (evOf(a).includes(be) ? -1 : 0) - (evOf(b).includes(be) ? -1 : 0) || a.id.localeCompare(b.id)).slice(0, 3);
    const criteria = [
      shared.length ? `cùng nói về ${joinVi(shared)}` : 'không cùng một chính tinh',
      sameBook ? `cùng một sách (${be.books.join(', ')})` : 'hai sách khác nhau',
      rel === 'specific_qualifier' ? 'điều kiện của câu hạn chế bao trùm điều kiện của câu thuận và thêm dữ kiện' :
        rel === 'specific_base' ? 'điều kiện của câu thuận bao trùm điều kiện của câu hạn chế' :
        rel === 'sat_qualifier' ? 'câu hạn chế thêm sát tinh vào cùng chính tinh' : 'hai điều kiện không bao trùm nhau',
      `${basesSorted[0].grounds.filter(x => x.independent).length} căn cứ độc lập cho câu thuận, ${qual.grounds.filter(x => x.independent).length} cho câu hạn chế`,
    ];
    dominance.push({ qualifier: qual, bases: basesSorted, base: basesSorted[0], sharedStars: shared, sameBook, sameSection: false, books: [...new Set([...be.books, ...xe.books])],
      cites: [...new Set([...be.cites, ...xe.cites])], relation: rel, qualEvidence: xe, baseEvidence: be, criteria,
      addedSat: xe.presentStars.filter(s => SAT.includes(s) && !be.presentStars.includes(s)).map(s => { const at = g.starAt.get(s); return at && at !== focus ? `${s} (từ ${at}${tt(at) ? ', nơi có ' + tt(at) : ''})` : s; }),
      verdict: rel === 'both_hold' || rel === 'specific_base' ? 'both_hold' : 'qualified_base' });
  }

  for (const d of dominance) {
    // 'cùng một mục' only when EVERY listed base shares a page reference with the limiting reading; 'cùng một sách' when every one shares the book
    const qc = new Set(d.qualEvidence.cites), qb = new Set(d.qualEvidence.books);
    d.sameSection = d.bases.every(b => evOf(b).some(e => e.cites.some(c => qc.has(c))));
    d.sameBook = d.bases.every(b => evOf(b).some(e => e.books.some(x => qb.has(x))));
    d.cites = [...new Set([...d.bases.flatMap(b => evOf(b).flatMap(e => e.cites)), ...d.qualEvidence.cites])];
    d.books = [...new Set([...d.bases.flatMap(b => evOf(b).flatMap(e => e.books)), ...d.qualEvidence.books])];
  }
  for (let i = 1; i < dominance.length; i++) {
    const used = new Set(dominance.slice(0, i).flatMap(d => d.bases));
    const rest = dominance[i].bases.filter(b => !used.has(b));
    if (rest.length) { dominance[i].bases = rest; dominance[i].base = rest[0]; }
  }
  // ---------- tensions: other opposed readings (an explicit 'contradicts' relation, or the same facet with opposite polarity in one palace)
  const contra = new Set(k.relations.relations.filter(r => r.type === 'contradicts').map(r => [r.a, r.b].sort().join('|')));
  const covered = (a: Claim, b: Claim) => dominance.some(d => [d.qualifier, ...d.bases].includes(a) && [d.qualifier, ...d.bases].includes(b));
  const absorbed = (a: Claim, b: Claim) => dominance.some(d => (d.qualifier === a && b.palace === focus && b.role === 'base') || (d.qualifier === b && a.palace === focus && a.role === 'base'));
  const pairsT: Array<{ pos: Claim; neg: Claim }> = [];
  for (const c1 of claims) for (const c2 of claims) {
    if (c1.id >= c2.id || c1.role === 'timing' || c2.role === 'timing' || c1.role === 'generic' || c2.role === 'generic' || covered(c1, c2)) continue;
    if (c1.palace !== c2.palace) continue;
    const opposed = contra.has([c1.concept, c2.concept].sort().join('|')) || (c1.polarity !== c2.polarity && c1.polarity !== '~' && c2.polarity !== '~' && c1.facet === c2.facet);
    if (!opposed || c1.polarity === c2.polarity) continue;
    const [pos, neg] = c1.polarity === '-' ? [c2, c1] : [c1, c2];
    if (absorbed(pos, neg)) { const d = dominance.find(x => x.qualifier === neg); if (d && !d.bases.includes(pos) && d.bases.length < 3 && !dominance.slice(0, dominance.indexOf(d)).some(o => o.bases.includes(pos))) d.bases.push(pos); continue; }
    pairsT.push({ pos, neg });
  }
  const tensions: Tension[] = [];
  for (const neg of [...new Set(pairsT.map(p => p.neg))]) {
    const posAll = pairsT.filter(p => p.neg === neg).map(p => p.pos), pos = posAll.slice(0, 2);
    const ne = evOf(neg)[0], pe = evOf(pos[0])[0];
    const kind = superset(effRoot(ne), effRoot(pe)) ? 'neg_refines' : superset(effRoot(pe), effRoot(ne)) ? 'pos_refines' : 'both_hold';
    const same = tensions.find(t => t.kind === kind && t.pos.map(c => c.id).join('|') === pos.map(c => c.id).join('|'));
    if (same) { if (!same.negs.includes(neg)) same.negs.push(neg); } else tensions.push({ pos, posAll, neg, negs: [neg], kind });
  }

  // ---------- timing
  const timingClaims = claims.filter(c => c.role === 'timing');
  const early = timingClaims.filter(c => spec.timing.early.includes(c.concept)), late = timingClaims.filter(c => spec.timing.late.includes(c.concept));
  const spec0 = (cs: Claim[]) => Math.max(0, ...cs.flatMap(evOf).map(e => e.specificity));
  let lean: TimingView['lean'] = null, leanReason: TimingView['leanReason'] = null;
  if (late.length && !early.length) { if (spec0(late) > 0) { lean = 'late'; leanReason = 'one_side'; } else leanReason = 'generic_only'; }
  else if (early.length && !late.length) { if (spec0(early) > 0) { lean = 'early'; leanReason = 'one_side'; } else leanReason = 'generic_only'; }
  else if (early.length && late.length) {
    if (spec0(early) === 0 && spec0(late) > 0) { lean = 'late'; leanReason = 'specific'; }
    else if (spec0(late) === 0 && spec0(early) > 0) { lean = 'early'; leanReason = 'specific'; }
  }

  // ---------- cross-palace links, per piece of evidence (a quote is paired only with ITS OWN dependencies)
  const focusQuotes = new Set(claims.filter(c => c.palace === focus).flatMap(c => c.quotes));
  const linkItems = (role: Role) => claims.filter(c => c.role === role).flatMap(c => evOf(c).filter(e => !focusQuotes.has(e.core)).map(e => ({ claim: c, evidence: e, all: depsOf(e) })))
    .map(x => ({ claim: x.claim, evidence: x.evidence, deps: uniqDeps(x.all.filter(d => d.necessary === true)), support: uniqDeps(x.all.filter(d => d.necessary !== true)) }));
  const cross = linkItems('cross').filter(x => x.deps.length).sort((a, b) => b.claim.grounds.length - a.claim.grounds.length || a.evidence.rule.id.localeCompare(b.evidence.rule.id));
  const linkL = linkItems('link').sort((a, b) => a.evidence.rule.id.localeCompare(b.evidence.rule.id));

  // ---------- exclusions
  const scopePal = (pal: string | null) => pal !== null && (frame.includes(pal) || links.includes(pal) || pal === spec.env?.palace);
  const draftsOut = drafts.filter(d => { const pal = d.rule.subject === 'palace' ? draftPalace(d.rule) : null; return scopePal(pal) && (pal === focus || lex.match(d.rule.reading ?? '').some(c => inScope(c.id))); })
    // a limiting draft is counted, never quoted: an unverified harsh sentence should not reach the reader even as an exclusion
    .map(d => ({ rule: d.rule.id, text: cleanDraft(d.rule.reading ?? k.claims[d.claim] ?? d.claim), neg: d.rule.consequences.some(c => c.effect === 'limit') || lex.match(cleanDraft(d.rule.reading ?? '')).some(c => lex.concepts.get(c.id)!.pol === '-') }))
    .filter((d, i, a) => a.findIndex(o => o.text === d.text) === i);
  const scopeNotes = spec.scopeNotes ? scopeNotesFor(q.major_stars, q.branch, k).map(r => ({ rule: r.id, text: cleanDraft(r.reading ?? ''), palace: 'Mệnh' })).filter(n => n.text) : [];

  // ---------- slots (chart facts for the templates; empty string = the passage needing it is skipped)
  const hoaOf = (p: Palace, s: string) => Object.entries(chart.tu_hoa).filter(([, v]) => v.star === s && g.byBranch.get(v.branch)?.name === p.name).map(([h]) => h.replace('Hóa ', 'hóa '));
  const label = (p: Palace, s: string) => { const d = p.major_dignity[s] ?? p.minor_dignity[s]; const h = hoaOf(p, s); return `${s}${d ? ` (${d})` : ''}${h.length ? ' ' + h.join(', ') : ''}`; };
  const majorsDig = (name: string) => { const p = g.palace(name); return p.major_stars.length ? joinVi(p.major_stars.map(s => label(p, s))) : ''; };
  const notable = (name: string) => { const p = g.palace(name); return [...p.stars.filter(s => (SAT.includes(s) || CAT.includes(s) || hoaOf(p, s).length) && !p.major_stars.includes(s)).map(s => label(p, s)), ...(tt(name) ? [tt(name)] : [])]; };
  const satTp = g.tamPhuong(focus).flatMap(p => p.stars.filter(s => SAT.includes(s)).map(s => `${s} ở ${p.name === focus ? 'ngay cung ' + focus : 'cung ' + p.name}`));
  const dF = chart.decades.find(d => d.palace === focus);
  const dNow = chart.year.dai_han, age = chart.year.age_tuoi_mu;
  const vanReadings = (rs: Array<{ text: string; src: string }> | undefined) => (rs ?? []).filter(r => !r.text.startsWith('Hai điều kiện trái chiều'))
    .map(r => `“${r.text.replace(/\.$/, '').replace(/\btheo sách (đây |là )?/g, '').replace(/\s{2,}/g, ' ')}” (${r.src.replace(/pp?\.\s?/, 'tr.').replace(/-/g, '–')})`);
  // Tứ Hóa of the decade stems that land in the focus palace: only decades a reader can still use (current, the focus decade, the next
  // two), grouped by decade
  const hoaDecades = chart.decades.filter(d => d.age_to >= age && (d.age_from <= age + 20 || d === dF) && d.age_from <= 85)
    .map(d => ({ d, h: Object.entries(d.hoa).filter(([, v]) => v.palace === focus).map(([h, v]) => `${h} vào ${v.star}`) })).filter(x => x.h.length)
    .map(x => `đại hạn ${x.d.age_from}–${x.d.age_to} (can ${x.d.stem}) đưa ${joinVi(x.h)}`);
  const profiles = q.major_stars.map(s => ({ s, p: k.starProfiles.stars[s] })).filter(x => x.p);
  const y: any = chart.year;
  const thReadings = vanReadings(y.tieu_han_reading), dhReadings = vanReadings(dF?.readings);
  const luu = ((y.luu_tu_hoa_reading ?? []) as Array<{ hoa: string; star: string; palace: string; advice: string; position_note: string; src: string }>)
    .filter(r => r.palace === focus || (r.hoa === 'Hóa Kỵ' && frame.includes(r.palace))).slice(0, 2)
    .map(r => `lưu ${r.hoa} (${r.star}) rơi vào ${r.palace === focus ? 'chính cung ' + focus : 'cung ' + r.palace}; với ${r.hoa} của ${r.star}, sách ghi “${r.advice}” (${r.src.replace(/pp?\.\s?/, 'tr.').replace(/-/g, '–')})`);
  // Tuần / Triệt in the palaces whose readings the chapter quotes, where no fired verified rule of that palace tests them
  const ttTested = new Set(claims.flatMap(evOf).filter(e => /palace\.(tuan|triet)/.test(JSON.stringify(e.rule.conditions))).map(e => e.palace));
  const ttNote = [focus, opposite, ...(spec.env ? [spec.env.palace] : [])].filter((p, i, a) => a.indexOf(p) === i && tt(p) && !ttTested.has(p)).map(p => `${p} có ${tt(p)}`);
  const slots: Record<string, string> = {
    topic: spec.topic, Topic: spec.topic[0].toUpperCase() + spec.topic.slice(1), 'f.name': focus, 'f.where': `${q.stem} ${q.branch}`, 'f.branch': q.branch, 'f.majors': joinVi(q.major_stars), 'f.majors_dig': majorsDig(focus),
    'f.no_major': q.major_stars.length ? '' : '1', 'f.notable': joinVi(notable(focus)), 'f.sat_tp': joinVi(satTp), 'f.pair': q.major_stars.length === 2 ? '1' : '',
    'f.is_menh': focus === 'Mệnh' ? '1' : '',
    'menh.majors_dig': majorsDig('Mệnh') || 'không có chính tinh',
    'tri.a': triad[0], 'tri.b': triad[1], 'tri.a_majors': majorsDig(triad[0]) || 'vô chính diệu', 'tri.b_majors': majorsDig(triad[1]) || 'vô chính diệu',
    'tri.a_notable': joinVi(notable(triad[0])), 'tri.b_notable': joinVi(notable(triad[1])),
    'opp.name': opposite, 'opp.majors_dig': majorsDig(opposite) || 'vô chính diệu', 'opp.majors': joinVi(g.palace(opposite).major_stars), 'opp.notable': joinVi(notable(opposite)),
    'than.palace': than, 'than.is_focus': than === focus ? '1' : '', 'than.is_opp': than === opposite ? '1' : '', 'than.in_triad': triad.includes(than) ? '1' : '',
    'env.name': spec.env?.palace ?? '', 'env.label': spec.env?.label ?? '',
    'profiles': profiles.map(({ s, p }) => `${s} ${p!.dau ? 'là ' + p!.dau.toLowerCase() : ''}${p!.domain ? ', chủ về ' + p!.domain : ''}`).join('; '),
    'profiles.cite': mergeCites([...new Set(profiles.map(x => x.p!.locator).filter(Boolean))].map(c => BOOK_PAGE(String(c)))),
    'dh.f': dF && dF.age_from <= 75 ? `${dF.age_from}–${dF.age_to}` : '', 'dh.f_stem': dF?.stem ?? '',
    'dh.f_readings': dhReadings.join('; '),
    'dh.f_conflict': dF && dF.readings.some(r => r.text.startsWith('Hai điều kiện trái chiều')) ? '1' : '',
    'dh.now': dNow ? `cung ${dNow.palace} (${dNow.age_from}–${dNow.age_to} tuổi mụ)` : '', 'dh.now_is_f': dNow?.palace === focus ? '1' : '',
    'dh.passed_f': dF && age > dF.age_to ? '1' : '', 'dh.before_f': dF && age < dF.age_from ? '1' : '',
    'year': String(chart.year.year), 'age': String(age), 'hoa_into_f': hoaDecades.join('; '),
    'yr.pillar': y.annual_pillar ?? '', 'yr.th_palace': y.tieu_han_palace ?? '', 'yr.th_is_f': y.tieu_han_palace === focus ? '1' : '',
    'yr.th_readings': y.tieu_han_palace === focus && thReadings.join('|') !== dhReadings.join('|') ? thReadings.join('; ') : '',
    'yr.th_same_as_dh': y.tieu_han_palace === focus && thReadings.length && thReadings.join('|') === dhReadings.join('|') ? '1' : '',
    'yr.luu': luu.join('; '), 'yr.luu_cite': luu.length ? 'KL pp.195-197' : '',
    'f.delegated': delegated.length ? String(new Set(delegated.map(e => e.core)).size) : '',
    'tt.note': joinVi(ttNote), 'tt.note_n': ttNote.length === 1 ? 'một' : String(ttNote.length),
  };
  const TPVT = ['Tử Vi', 'Thiên Phủ', 'Vũ Khúc', 'Thiên Tướng'];
  const groupRule = fired.find(f => f.claim === 'menh_nhom_tu_phu_vu_tuong' && f.basis === 'verified');
  slots['group.same'] = chapter === 'cong_danh' && groupRule && q.major_stars.length && q.major_stars.every(s => TPVT.includes(s)) ? '1' : '';
  slots['group.rule'] = groupRule?.ruleId ?? '';
  const lists: Record<string, Claim[]> = {};
  const sal = (c: Claim) => c.grounds.filter(x => x.independent).length * 10 + new Set(c.grounds.flatMap(x => x.books)).size;
  for (const r of ['base', 'support', 'qualifier', 'cross', 'link', 'environment', 'timing', 'work_style', 'generic'] as Role[])
    lists[r] = claims.filter(c => c.role === r).sort((x, z) => sal(z) - sal(x) || x.id.localeCompare(z.id));
  const timing: TimingView = { early, late, lean, leanReason };
  return { chapter, spec, career: focus, focus, triad, opposite, claims, dominance, cross, links: linkL, tensions, timing, timingConflict: { early, late },
    slots, lists, excluded: { drafts: draftsOut, scopeNotes }, evidenceCount: ev.length };
}

const evOf0 = (c: Claim) => c.grounds.flatMap(x => x.evidence);
const uniqDeps = (ds: Dep[]) => ds.filter((d, i, a) => a.findIndex(o => o.star === d.star) === i);
/** Book text of a draft or scope rule without its condition parenthetical and editorial notes ('; sách nói…', 'hệ thống…'). */
function cleanDraft(t: string): string { return splitReading(t).core.replace(/\btheo sách (đây |là )?/g, '').trim(); }
/** 'Thực Hành tr.29–30', 'Thực Hành tr.44' -> 'Thực Hành tr.29–30, 44' */
export function mergeCites(cs: string[]): string {
  const by = new Map<string, string[]>();
  for (const c of cs) { const m = c.match(/^(.*?) tr\.(.+)$/); const [b, p] = m ? [m[1], m[2]] : [c, '']; by.set(b, [...(by.get(b) ?? []), ...(p ? [p] : [])]); }
  return [...by].map(([b, ps]) => ps.length ? `${b} tr.${[...new Set(ps)].join(', ')}` : b).join('; ');
}
function draftPalace(r: Rule): string | null {
  const walk = (e: any): string | null => e?.fact === 'palace.name' ? String(e.value) : (e?.all ?? e?.any ?? []).map(walk).find(Boolean) ?? null;
  return walk(r.conditions);
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
