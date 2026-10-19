// Select (prose plan §4.3): from the resolved assertions of a chapter's palace, choose what each move of the paragraph will voice.
//   NUCLEUS   the chapter's own kind of concept (identity for Mệnh, career for Quan Lộc, finance for Tài Bạch) standing most directly on the
//             palace's chính tinh (salience: anchoring, independent rules, specificity);
//   TURN      up to two limiting concepts of that kind, preferring the nucleus's own shadow and those resting on a hãm chính tinh;
//   RESCUE    a softened/weakened assertion whose relation is a book-stated 'rescues', with the rescuing rule;
//   TENSION   a concept brought by a sát tinh standing in the palace (its +/− pair from the same rule) or by Hóa Quyền/Kỵ/Khoa there;
//   TIMING    a hard start / late bloom / early or late success, flagged when Tuần or Triệt sits on the palace;
//   SATELLITE further concepts of the chapter's kind; VIA the same kind read at another palace (Mệnh hands career and money on);
//   DEGREE    the additive độ số balance (Mệnh only).
// A reading (concept at a palace) is voiced at most once in a report (spec.exclude carries what earlier chapters said). Voided assertions are never selected.
import type { Concept, Knowledge, Palace } from '../types.ts';
import type { Resolved } from '../kg/resolve.ts';
import { SAT } from '../kg/atoms.ts';

export interface ConceptPick { concept: string; assertions: Resolved[]; score: number; soft: boolean }
export interface SelectSpec {
  palace: Palace; opp?: Palace; pool: (c?: Concept) => boolean; borrowPool?: (c?: Concept) => boolean; borrowFrom: string[]; chart: boolean; exclude: Set<string>; extra: string[]; degree: boolean;
}
export interface Selection {
  /** the first turn is the nucleus's own shadow (then 'sự sắc sảo ấy dễ …' reads true) */
  turnIsShadow?: boolean;
  palace: Palace; majors: string[]; vcd: boolean; oppMajors: string[];
  via: Array<{ pick: ConceptPick; from: string }>;
  nucleus?: ConceptPick; elaborate: boolean;
  turn: ConceptPick[]; turnCause?: { star: string; dignity: string };
  rescue?: { target: ConceptPick; byRule: string; relation: string; via: 'hoa' | 'tuan_triet' | 'cat' | 'generic'; star?: string; hoa?: string; tt?: string; mitigated?: ConceptPick };
  tension?: { pos?: ConceptPick; neg?: ConceptPick; star: string; kind: 'sat' | 'hoa'; dignityOk: boolean; dignity?: string; hoa?: string };
  timing?: { pick: ConceptPick; tt?: string };
  satellites: ConceptPick[]; satelliteNeg?: ConceptPick;
  degree: { up: Resolved[]; down: Resolved[] };
  extra: ConceptPick[];
  unused: string[];
}

export const IDENTITY = (c?: Concept) => !!c && (c.facet.startsWith('identity.') || c.facet === 'inner.contentment' || c.facet === 'life.spirituality');
const TIMING = new Set(['life.early_hardship', 'life.late_bloom', 'career.late', 'career.early']);
const OK_DIGNITY = new Set(['miếu', 'vượng', 'đắc', 'lợi']);

export function select(resolved: Resolved[], k: Knowledge, spec: SelectSpec): Selection {
  const cmap = new Map(k.concepts.concepts.map(c => [c.id, c]));
  const pal = spec.palace, P = pal.name, majors = pal.major_stars, IDENTITY = (c?: Concept) => spec.pool(c);
  const borrowed = (r: Resolved) => !!r.palace && r.palace !== P && spec.borrowFrom.includes(r.palace);
  const live = resolved.filter(r => r.status !== 'voided' && !spec.exclude.has(`${r.concept}@${r.palace ?? 'Mệnh'}`)
    && (r.subject === `palace:${P}` || (spec.chart && r.subject === 'chart') || (borrowed(r) && (spec.borrowPool ?? spec.pool)(cmap.get(r.concept)))));
  const byConcept = new Map<string, Resolved[]>();
  for (const r of live) { if (r.additive) continue; (byConcept.get(r.concept) ?? byConcept.set(r.concept, []).get(r.concept)!).push(r); }

  const onMajor = (r: Resolved) => r.atoms.some(a => (a.kind === 'star' || a.kind === 'dignity') && a.palace === P && majors.includes(a.name));
  const onOwn = (r: Resolved) => r.atoms.some(a => a.palace === P && (a.kind === 'star' || a.kind === 'hoa' || a.kind === 'tuan_triet'));
  const pickOf = (id: string): ConceptPick => {
    const as = byConcept.get(id)!;
    const rules = new Set(as.map(a => a.ruleId));
    const score = (as.some(onMajor) ? 10 : 0) + (as.some(onOwn) ? 4 : 0) + Math.min(rules.size, 5) + Math.max(...as.map(a => a.sig.size)) * 0.1;
    const soft = as.every(a => a.status === 'softened' || a.status === 'weakened' || a.stance === 'weakens');
    return { concept: id, assertions: as, score, soft };
  };
  const ranked = [...byConcept.keys()].map(pickOf).sort((a, b) => b.score - a.score || (a.concept < b.concept ? -1 : 1));
  // a concept read only at a borrowed palace is told as such (VIA), never as this palace's own nucleus, turn or tension
  const borrowedOnly = (p: ConceptPick) => p.assertions.every(borrowed);
  const all = ranked.filter(p => !borrowedOnly(p));
  const used = new Set<string>();
  const take = (p?: ConceptPick) => { if (p) used.add(p.concept); return p; };
  const pol = (p: ConceptPick) => cmap.get(p.concept)?.pol;
  const free = (p: ConceptPick) => !used.has(p.concept);

  // RESCUE first: what the book itself turned decides how the turn is told
  let rescue: Selection['rescue'];
  for (const p of all) {
    const r = p.assertions.find(a => a.by.some(b => b.type === 'rescues' && b.basis === 'sach'));
    if (!r) continue;
    const b = r.by.find(x => x.type === 'rescues')!;
    const saver = live.filter(a => a.ruleId === b.byRule);
    const atoms = saver[0]?.atoms ?? [];
    const hoaAtom = atoms.find(a => a.kind === 'hoa'), tt = atoms.find(a => a.kind === 'tuan_triet');
    const via = hoaAtom ? 'hoa' : tt ? 'tuan_triet' : atoms.some(a => a.kind === 'star' && !majors.includes(a.name)) ? 'cat' : 'generic';
    const star = (via === 'hoa' ? majors.find(m => atoms.some(a => a.kind === 'star' && a.name === m)) : undefined) ?? majors.find(m => r.atoms.some(a => a.name === m)) ?? majors[0];
    const mit = saver.find(a => a.concept === 'life.mitigated' && byConcept.has(a.concept));
    rescue = { target: take(p)!, byRule: b.byRule, relation: b.relation, via, star, hoa: hoaAtom?.name, tt: tt?.name, mitigated: mit ? take(pickOf('life.mitigated')) : undefined };
    break;
  }

  // NUCLEUS: identity + / ~ trait, anchored on the Mệnh's chính tinh when one carries any
  const anchoredExists = all.some(p => IDENTITY(cmap.get(p.concept)) && pol(p) !== '-' && p.assertions.some(onMajor));
  const nucleusOf = (soft: boolean) => all.find(p => free(p) && IDENTITY(cmap.get(p.concept)) && pol(p) !== '-' && (soft || !p.soft) && (!anchoredExists || p.assertions.some(onMajor)));
  // when every candidate was weakened (a book qualifier, a narrower reading), the core is told in its weakened form rather than dropped
  const nucleus = take(nucleusOf(false) ?? nucleusOf(true));

  // TURN: limiting identity traits; the nucleus's shadow first, then traits on a hãm chính tinh, then salience
  const hamMajor = majors.find(m => pal.major_dignity?.[m] === 'hãm');
  const shadow = nucleus ? (k.prose?.concepts.find(c => c.id === nucleus.concept)?.shadow) : undefined;
  const onHam = (p: ConceptPick) => !!hamMajor && p.assertions.some(a => a.atoms.some(x => x.kind === 'dignity' && x.name === hamMajor && x.value === 'hãm'));
  const turnPool = all.filter(p => free(p) && pol(p) === '-' && IDENTITY(cmap.get(p.concept)) && !TIMING.has(p.concept))
    .sort((a, b) => Number(b.concept === shadow) - Number(a.concept === shadow) || Number(onHam(b)) - Number(onHam(a)) || b.score - a.score || (a.concept < b.concept ? -1 : 1));
  const turn: ConceptPick[] = [];
  for (const p of turnPool) {
    if (turn.length === 2) break;
    if (turn.length === 1 && !p.assertions.some(a => turn[0].assertions.some(b => b.ruleId === a.ruleId)) && !(onHam(p) && onHam(turn[0]))) continue;   // a second turn only when it shares the first's ground
    turn.push(take(p)!);
  }
  const turnCause = hamMajor && turn.length && onHam(turn[0]) ? { star: hamMajor, dignity: 'hãm' } : undefined;

  // TENSION: a sát tinh in Mệnh (its own dignity decides the tone), else Hóa Quyền / Kỵ / Khoa at Mệnh
  let tension: Selection['tension'];
  const satHere = SAT.filter(s => pal.stars.includes(s));
  for (const s of satHere) {
    // readings whose subject IS the sát star (no other star in their evidence), most specific first; rescued or weakened ones never
    const stars = (a: Resolved) => new Set(a.atoms.filter(x => x.kind === 'star' || x.kind === 'dignity').map(x => x.name)).size;
    const rs = live.filter(a => a.atoms.some(x => x.kind === 'star' && x.name === s && x.palace === P) && !a.additive && a.status === 'holds' && stars(a) === 1)
      .sort((a, b) => b.sig.size - a.sig.size || (a.ruleId < b.ruleId ? -1 : 1));
    if (!rs.length) continue;
    const top = rs[0].ruleId, same = rs.filter(a => a.ruleId === top);
    const posA = same.find(a => cmap.get(a.concept)?.pol === '+' && !used.has(a.concept)), negA = same.find(a => cmap.get(a.concept)?.pol === '-' && !used.has(a.concept));
    if (!posA && !negA) continue;
    const lv = pal.minor_dignity?.[s] ?? undefined;
    tension = { star: s, kind: 'sat', dignityOk: !!lv && OK_DIGNITY.has(lv), dignity: lv ?? undefined, pos: posA ? take(pickOf(posA.concept)) : undefined, neg: negA ? take(pickOf(negA.concept)) : undefined };
    break;
  }
  if (!tension) {
    for (const h of ['Hóa Quyền', 'Hóa Kỵ', 'Hóa Khoa']) {
      const rs = live.filter(a => a.atoms.some(x => x.kind === 'hoa' && x.name === h && x.palace === P) && !used.has(a.concept) && IDENTITY(cmap.get(a.concept)) && a.status === 'holds' && a.stance === 'affirms');
      if (!rs.length) continue;
      const a = rs[0], positive = cmap.get(a.concept)?.pol !== '-';
      tension = { star: majors[0] ?? '', kind: 'hoa', hoa: h, dignityOk: positive, pos: positive ? take(pickOf(a.concept)) : undefined, neg: positive ? undefined : take(pickOf(a.concept)) };
      break;
    }
  }

  // TIMING
  let timing: Selection['timing'];
  const tp = all.filter(p => free(p) && TIMING.has(p.concept)).sort((a, b) => b.score - a.score)[0];
  if (tp) {
    const tt = tp.assertions.flatMap(a => a.atoms).find(a => a.kind === 'tuan_triet' && a.palace === P);
    timing = { pick: take(tp)!, tt: tt?.name };
  }

  const satellites = all.filter(p => free(p) && IDENTITY(cmap.get(p.concept)) && pol(p) !== '-' && !p.soft).slice(0, 3);
  satellites.forEach(take);
  const satelliteNeg = take(all.find(p => free(p) && IDENTITY(cmap.get(p.concept)) && pol(p) === '-' && !p.soft));
  const extra = all.filter(p => free(p) && spec.extra.includes(p.concept)).slice(0, 2);
  extra.forEach(take);
  const via = ranked.filter(p => borrowedOnly(p) && free(p) && pol(p) !== '-' && !p.soft).slice(0, 2).map(p => ({ pick: take(p)!, from: p.assertions[0].palace! }));
  const deg = spec.degree ? live.filter(r => r.additive && r.concept === 'life.degree') : [];
  return {
    turnIsShadow: !!shadow && turn[0]?.concept === shadow,
    palace: pal, majors, vcd: majors.length === 0, oppMajors: spec.opp?.major_stars ?? [], via, nucleus, elaborate: !!nucleus, turn, turnCause, rescue, tension, timing, satellites, satelliteNeg,
    degree: { up: deg.filter(r => r.stance === 'affirms'), down: deg.filter(r => r.stance === 'weakens') }, extra,
    unused: ranked.filter(free).map(p => p.concept),
  };
}
