// Narrative planner for the Công danh chapter: turns validated evidence into an ARGUMENT GRAPH before any sentence exists.
//   central configuration  -> the career palace (Quan Lộc), its stars, Tứ Hóa, Tuần/Triệt and its tam phương tứ chính
//   roles                  -> base (readings on the palace's chính tinh), support (cát / phụ tinh), qualifier (sát tinh or limiting
//                             readings), cross (readings of Mệnh/Thân that depend on stars of the career triad), environment
//                             (Thiên Di), timing (readings about when, decades through Quan Lộc)
//   grounds                -> evidence standing on the same normalised chart facts is ONE ground, whatever the number of books
//   dominance              -> each opposed (base, qualifier) pair gets a verdict from five explicit criteria; the verdict says what
//                             the books state and what is the system's precedence policy, never more
//   exclusions             -> drafts, readings the books give for another palace, and what the rule set cannot decide
import { ChartGraph, SAT, CAT } from './graph.ts';
import { joinVi, rootStars, type Evidence, type Lexicon } from './semantic.ts';
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
export interface ArgumentGraph {
  chapter: 'cong_danh'; career: string; triad: string[]; opposite: string;
  claims: Claim[]; dominance: Dominance[]; cross: CrossLink[]; tensions: Tension[]; timingConflict: { early: Claim[]; late: Claim[] };
  slots: Record<string, string>; lists: Record<string, Claim[]>; excluded: { drafts: Array<{ rule: string; text: string }>; scopeNotes: Array<{ rule: string; text: string; palace: string }> };
  evidenceCount: number;
}

const CAREER_FACETS = new Set(['career.authority', 'career.trajectory', 'career.expertise', 'career.path', 'career.support', 'career.timing']);
const WORK_STYLE = new Set(['identity.ambition', 'identity.discipline']);
const ENV_FACETS = new Set(['career.support', 'career.trajectory', 'life.mobility', 'life.course', 'career.timing']);
const BOOK_PAGE = (c: string) => c.replace(/^TH /, 'Thực Hành tr.').replace(/^KL /, 'Khảo Luận tr.').replace(/^TT /, 'Toàn Thư tr.').replace(/p+\.\s?/, '').replace(/-/g, '–');

export function plan(chart: ChartInput, ev: Evidence[], g: ChartGraph, lex: Lexicon, k: Knowledge, drafts: Array<{ rule: Rule; claim: string }>, fired: Finding[] = []): ArgumentGraph {
  const career = 'Quan Lộc';
  const q = g.palace(career);
  const triad = g.related(career, 'tam_hop').map(p => p.name);
  const opposite = g.related(career, 'xung_chieu')[0].name;
  const than = chart.palaces.find(p => p.is_than)!.name;
  const facetOf = (id: string) => lex.concepts.get(id)!.facet;

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
  for (const e of ev) {
    if (!e.concepts.length) continue;
    const primary = e.concepts.find(c => CAREER_FACETS.has(facetOf(c.id))) ?? e.concepts[0];
    const pf = facetOf(primary.id);
    if (e.palace === career && pf === 'career.timing') {
      add(e, primary.id, 'timing');
    } else if (e.palace === career) {
      const onSat = e.presentStars.some(s => SAT.includes(s)) || /sát tinh/.test(e.chartCondition);
      const onMajor = e.presentStars.some(s => majors.has(s));
      const role: Role = e.polarity === '-' || onSat ? 'qualifier' : onMajor ? 'base' : 'support';
      add(e, primary.id, role);
    } else if (e.palace === 'Mệnh' || e.palace === than || e.palace === null) {
      if (pf === 'career.timing') { add(e, primary.id, 'timing'); continue; }
      const deps = g.crossDependencies(e.finding.id).filter(d => d.palace === career || triad.includes(d.palace) || d.palace === opposite);
      if (deps.length && (CAREER_FACETS.has(pf) || e.concepts.some(c => facetOf(c.id).startsWith('career.') || c.id === 'fin.abundance' || c.id === 'life.mobility'))) add(e, primary.id, 'cross');
      else if (pf === 'career.timing') add(e, primary.id, 'timing');
      else if (CAREER_FACETS.has(pf)) add(e, primary.id, e.polarity === '-' ? 'qualifier' : 'cross');
      else if (WORK_STYLE.has(pf)) add(e, primary.id, 'work_style');
    } else if (e.palace === 'Thiên Di') {
      if (pf === 'career.timing') add(e, primary.id, 'timing');
      else if (ENV_FACETS.has(pf) || e.concepts.some(c => ENV_FACETS.has(facetOf(c.id)))) add(e, primary.id, 'environment');
    } else if ((triad.includes(e.palace ?? '') || e.palace === opposite) && CAREER_FACETS.has(pf)) {
      add(e, primary.id, pf === 'career.timing' ? 'timing' : 'cross');
    }
  }
  const claims = [...claimsMap.values()];
  // a reading conditioned on 'sát tinh hội' stands on the sát stars actually in the tam phương: name them, and count them in its root
  const satTpStars = g.tamPhuong(career).flatMap(p => p.stars.filter(st => SAT.includes(st)).map(st => ({ st, p: p.name })));
  for (const c of claims) for (const gr of c.grounds) for (const e of gr.evidence) {
    if (e.palace === career && /sát tinh hội về/.test(e.chartCondition) && satTpStars.length) {
      e.chartCondition = e.chartCondition.replace(/sát tinh hội về ([^,]+)/, `sát tinh ${joinVi(satTpStars.map(x => x.p === career ? x.st : `${x.st} (từ ${x.p})`))} hội về $1`);
      e.presentStars = [...new Set([...e.presentStars, ...satTpStars.map(x => x.st)])];
      gr.root = [...new Set([...gr.root, ...satTpStars.map(x => `tp:${x.st}`)])].sort();
    }
  }
  for (const c of claims) {
    c.grounds.sort((a, b) => a.root.length - b.root.length || a.root.join().localeCompare(b.root.join()));
    c.grounds.forEach((gr, i) => { gr.independent = !c.grounds.slice(0, i).some(o => [...rootStars(o.root)].some(st => rootStars(gr.root).has(st))); });
    c.polarity = c.grounds.flatMap(x => x.evidence).some(e => e.polarity === '-') && c.role === 'qualifier' ? '-' : c.polarity;
    c.quotes = [...new Set(c.grounds.flatMap(x => x.evidence.map(e => e.core)))];
  }

  // ---------- dominance between the palace's base readings and its qualifiers
  const dominance: Dominance[] = [];
  const bases = claims.filter(c => c.role === 'base' && c.polarity !== '-');
  for (const qual of claims.filter(c => c.role === 'qualifier' && c.palace === career)) {
    const qe = qual.grounds.flatMap(x => x.evidence);
    const best = bases.map(b => {
      const be = b.grounds.flatMap(x => x.evidence);
      const shared = [...new Set(qe.flatMap(e => e.presentStars).filter(s => be.some(x => x.presentStars.includes(s)) && majors.has(s)))];
      const sameBook = qe.some(e => be.some(x => x.books.some(bk => e.books.includes(bk))));
      return { b, shared, sameBook, score: shared.length * 2 + (sameBook ? 1 : 0) };
    }).sort((a, b) => b.score - a.score)[0];
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
      directness: 'cả hai đọc ngay tại cung Quan Lộc', verdict: qualOnSat || specificity === 'qualifier' ? 'qualified_base' : 'both_hold', criteria });
  }

  // ---------- tensions: opposed career readings outside the base/qualifier pairs (e.g. two Mệnh readings), classified by their facts
  const contra = new Set(k.relations.relations.filter(r => r.type === 'contradicts').map(r => [r.a, r.b].sort().join('|')));
  const covered = new Set(dominance.flatMap(d => [d.base.id + '|' + d.qualifier.id, d.qualifier.id + '|' + d.base.id]));
  const tensions: Tension[] = [];
  for (const c1 of claims) for (const c2 of claims) {
    if (c1.id >= c2.id || covered.has(c1.id + '|' + c2.id) || c1.role === 'timing' || c2.role === 'timing') continue;
    const opposed = contra.has([c1.concept, c2.concept].sort().join('|')) ||
      (c1.palace === c2.palace && c1.polarity !== c2.polarity && c1.polarity !== '~' && c2.polarity !== '~' && facetOf(c1.concept) === facetOf(c2.concept) && c1.palace !== career);
    if (!opposed) continue;
    const [pos, neg] = c1.polarity === '-' ? [c2, c1] : [c1, c2];
    const rp = new Set(pos.grounds[0].root), rn = new Set(neg.grounds[0].root);
    const kind = [...rp].every(x => rn.has(x)) && rn.size > rp.size ? 'refinement' : 'both_hold';
    tensions.push({ pos, neg, kind });
  }
  const timingClaims = claims.filter(c => c.role === 'timing');
  const early = timingClaims.filter(c => c.concept === 'career.early'), late = timingClaims.filter(c => c.concept === 'career.late');

  // ---------- cross-palace links read from the graph
  const cross: CrossLink[] = claims.filter(c => c.role === 'cross').sort((x, y) => y.grounds.length - x.grounds.length || x.id.localeCompare(y.id)).map(c => ({ claim: c,
    deps: c.grounds.flatMap(x => x.evidence).flatMap(e => g.crossDependencies(e.finding.id)).filter((d, i, a) => a.findIndex(o => o.star === d.star) === i) }));

  // ---------- exclusions
  const inScope = (pal: string | null) => pal === career || pal === 'Mệnh' || pal === than || pal === 'Thiên Di' || triad.includes(pal ?? '');
  const draftsOut = drafts.filter(d => inScope(d.rule.subject === 'palace' ? draftPalace(d.rule) : null) && careerish(d.rule, k, lex, facetOf))
    .map(d => ({ rule: d.rule.id, text: (d.rule.reading ?? k.claims[d.claim] ?? d.claim).replace(/\s*\[[^\]]*\]/g, '') }));
  const scopeNotes = scopeNotesFor(q.major_stars, q.branch, k).map(r => ({ rule: r.id, text: (r.reading ?? '').replace(/\s*\[[^\]]*\]/g, ''), palace: 'Mệnh' }));

  // ---------- slots (chart facts for the templates; empty string = the passage needing it is skipped)
  const dig = (p: typeof q, s: string) => { const d = p.major_dignity[s] ?? p.minor_dignity[s]; return d ? `${s} (${d})` : s; };
  const majorsDig = (name: string) => { const p = g.palace(name); return p.major_stars.length ? joinVi(p.major_stars.map(s => dig(p, s))) : ''; };
  const notable = (name: string) => g.palace(name).stars.filter(s => SAT.includes(s) || CAT.includes(s));
  const tt = (name: string) => { const p = g.palace(name); return [p.tuan && 'Tuần', p.triet && 'Triệt'].filter(Boolean).join(' và '); };
  const satTp = g.tamPhuong(career).flatMap(p => p.stars.filter(s => SAT.includes(s)).map(s => `${s} ở ${p.name === career ? 'ngay cung Quan Lộc' : 'cung ' + p.name}`));
  const dQuan = chart.decades.find(d => d.palace === career);
  const dNow = chart.year.dai_han;
  const hoaIntoQuan = chart.decades.flatMap(d => Object.entries(d.hoa).filter(([, v]) => v.palace === career).map(([h, v]) => `đại hạn ${d.age_from}–${d.age_to} (can ${d.stem}) đưa ${h} vào ${v.star}`));
  const profiles = q.major_stars.map(s => ({ s, p: k.starProfiles.stars[s] })).filter(x => x.p);
  const slots: Record<string, string> = {
    'quan.where': `${q.stem} ${q.branch}`, 'quan.branch': q.branch, 'quan.majors': joinVi(q.major_stars), 'quan.majors_dig': majorsDig(career),
    'quan.no_major': q.major_stars.length ? '' : '1', 'quan.sat': joinVi(notable(career).filter(s => SAT.includes(s))), 'quan.cat': joinVi(notable(career).filter(s => CAT.includes(s))),
    'quan.hoa': joinVi(g.hoaIn(career)), 'quan.tt': tt(career), 'quan.sat_tp': joinVi(satTp), 'quan.pair': q.major_stars.length === 2 ? '1' : '',
    'menh.majors_dig': majorsDig('Mệnh') || 'không có chính tinh', 'menh.hoa': joinVi(g.hoaIn('Mệnh')),
    'triad.a': triad[0], 'triad.b': triad[1], 'triad.a_majors': majorsDig(triad[0]) || 'vô chính diệu', 'triad.b_majors': majorsDig(triad[1]) || 'vô chính diệu',
    'triad.a_notable': joinVi(notable(triad[0])), 'triad.b_notable': joinVi(notable(triad[1])),
    'opp.name': opposite, 'opp.majors_dig': majorsDig(opposite) || 'không có chính tinh', 'opp.notable': joinVi([...notable(opposite), ...(tt(opposite) ? [tt(opposite)] : [])]),
    'than.palace': than, 'than.is_career': than === career ? '1' : '',
    'profiles': profiles.map(({ s, p }) => `${s} ${p!.dau ? 'là ' + p!.dau.toLowerCase() : ''}${p!.domain ? ', chủ về ' + p!.domain : ''}`).join('; '),
    'profiles.cite': [...new Set(profiles.map(x => x.p!.locator).filter(Boolean))].map(c => BOOK_PAGE(String(c))).join(', '),
    'dh.quan': dQuan ? `${dQuan.age_from}–${dQuan.age_to}` : '', 'dh.quan_stem': dQuan?.stem ?? '',
    'dh.quan_readings': dQuan ? dQuan.readings.filter(r => !r.text.startsWith('Hai điều kiện trái chiều')).map(r => `“${r.text.replace(/\.$/, '')}” (${r.src.replace(/pp?\.\s?/, 'tr.').replace(/-/g, '–')})`).join('; ') : '',
    'dh.quan_conflict': dQuan && dQuan.readings.some(r => r.text.startsWith('Hai điều kiện trái chiều')) ? '1' : '',
    'dh.now': dNow ? `cung ${dNow.palace} (${dNow.age_from}–${dNow.age_to} tuổi mụ)` : '', 'dh.now_is_quan': dNow?.palace === career ? '1' : '',
    'dh.passed_quan': dQuan && chart.year.age_tuoi_mu > dQuan.age_to ? '1' : '', 'dh.before_quan': dQuan && chart.year.age_tuoi_mu < dQuan.age_from ? '1' : '',
    'year': String(chart.year.year), 'age': String(chart.year.age_tuoi_mu), 'hoa_into_quan': joinVi(hoaIntoQuan),
  };
  const TPVT = ['Tử Vi', 'Thiên Phủ', 'Vũ Khúc', 'Thiên Tướng'];
  const groupRule = fired.find(f => f.claim === 'menh_nhom_tu_phu_vu_tuong' && f.basis === 'verified');
  slots['group.same'] = groupRule && q.major_stars.length && q.major_stars.every(s => TPVT.includes(s)) ? '1' : '';
  slots['group.rule'] = groupRule?.ruleId ?? '';
  const lists: Record<string, Claim[]> = {};
  const sal = (c: Claim) => c.grounds.filter(x => x.independent).length * 10 + new Set(c.grounds.flatMap(x => x.books)).size;
  for (const r of ['base', 'support', 'qualifier', 'cross', 'environment', 'timing', 'work_style'] as Role[])
    lists[r] = claims.filter(c => c.role === r).sort((x, y) => sal(y) - sal(x) || x.id.localeCompare(y.id));
  return { chapter: 'cong_danh', career, triad, opposite, claims, dominance, cross, tensions, timingConflict: { early, late }, slots, lists, excluded: { drafts: draftsOut, scopeNotes }, evidenceCount: ev.length };
}

function draftPalace(r: Rule): string | null {
  const walk = (e: any): string | null => e?.fact === 'palace.name' ? String(e.value) : (e?.all ?? e?.any ?? []).map(walk).find(Boolean) ?? null;
  return walk(r.conditions);
}
function careerish(r: Rule, k: Knowledge, lex: Lexicon, facetOf: (id: string) => string): boolean {
  const text = r.reading ?? '';
  return lex.match(text).some(c => facetOf(c.id).startsWith('career.'));
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
