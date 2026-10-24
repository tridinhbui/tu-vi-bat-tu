// Domain depth (plan DEEP-TUVI, 2026-10-22): the analysis behind the "Đọc sâu" part of the Quan Lộc, Tài Bạch and Phu Thê chapters. The short
// reading (prose/luan.ts) says WHAT the books read on the chart; this layer works out, before any sentence is written, the structure of the
// domain — and every unit it keeps stands on something checked:
//   reading    a verified reading of the domain's palaces (live, past the position guards), with the elements it fired on (trigger atoms);
//   mechanism  what Khảo Luận says the star a reading or a fact stands on is (engine/data/kg/star_nature.json: "Thái Dương tượng trưng
//              cho uy quyền, quan lộc, danh vọng nên rất cần ở cung Quan", KL p.187) — the WHY of the reading, told right after it;
//   trigger    where a reading's elements stand when one of them is not in the palace itself (a Hóa Kỵ chiếu from the opposite palace):
//              the chart fact that makes the reading fire, computed from its trigger atoms;
//   link       a computed tie between the domain's palace and another one: the same star or Hóa reaching both (Thái Dương hóa Quyền in Tài
//              Bạch hội chiếu Quan Lộc), Thân cư with Khảo Luận's sentence on it (KL p.215), the palaces the book says weigh on Tài
//              (KL p.216), Kỵ on the opposite palace;
//   tame       a book statement that a star of the palace or its tam phương holds a limiting star of the same palace in check (Thất Sát
//              "thầy Kình Đà", KL p.190) — an interaction between two elements the chart actually has;
//   condition  the domain ledger's verdict (reason/ledger.ts) with the limiting elements it is conditional on.
// Sections are the domain's own questions (Quan Lộc: orientation, strengths, environment, authority, rhythm, obstacles, career→money;
// Tài Bạch: earning, accumulation, stability, spending, risk, Mệnh–Tài–Quan–Điền; Phu Thê: dynamics, compatibility, communication,
// tension, stabilisers, conditions). A section is kept only with a chart-specific anchor (a reading, a trigger, a link) — a star's nature
// alone is never a section. Phu Thê never carries a timing or event unit (owner's rule, 2026-10-22).
import type { ChartInput, Concept, Knowledge, Palace } from '../types.ts';
import type { Resolved } from '../kg/resolve.ts';
import { guardHolds } from './positions.ts';
import { palaceEvidence, tamPhuongOf, type Element, type PalaceEvidence, type Where } from './evidence.ts';
import type { DomainVerdict, Ledger } from './ledger.ts';
import type { Borrowed } from './borrow.ts';

export const DEPTH_VERSION = 'depth-2.0.0';
/** the matter a star-nature line speaks of (star_nature.json `use`) */
export type Use = string;
export interface StarNature { id: string; star: string; also?: string[]; page: number; quote: string; text: string; use: Use[]; palace?: string;
  /** '+' (default) a strength, '-' a limit, '±' a nature with both edges: told after a reading only of a matching side */
  pol?: '+' | '-' | '±';
  tames?: string[]; link?: string[];
  /** the readings (concept ids, or prefixes ending in '.') this nature may be the 'why' of */
  explains?: string[];
  /** the book (default KL) */
  book?: string }
export interface PalaceRelation { id: string; palace: string; page: number; quote: string; text: string; when?: string; with?: string[]; book?: string;
  /** the palaces whose chapters may tell it (default: `palace`) */
  chapters?: string[] }
export interface StarNatureFile { version: string; basis: string; entries: StarNature[]; relations: PalaceRelation[] }

/** One chapter's deep reading, as engine/data/kg/domains.json `depth` configures it (a system convention, he_thong). */
export interface DepthConfig {
  palace: string; use: Use; prefix: string[]; sections: string[];
  /** which section a reading of a concept goes to: first match wins; `fallback` takes any other reading of the palace */
  map: Array<{ match: string[]; to?: string; pos?: string; neg?: string }>; fallback?: { to?: string; pos?: string; neg?: string };
  orient: string; obst: string; quyen: string; link: string; cond: string | null; verdicts: string[];
  noTiming?: boolean; noEvents?: boolean; noVerdict?: boolean; thanSection?: string; relations?: string[]; hoaLink?: boolean;
}
export type DepthDomain = string;
export const depthConfig = (k: Knowledge, d: DepthDomain): DepthConfig | undefined => (k.kg?.domains as { depth?: Record<string, DepthConfig> } | undefined)?.depth?.[d];
/** the sections of a domain, in reading order */
export const sectionsOf = (k: Knowledge, d: DepthDomain) => depthConfig(k, d)?.sections ?? [];
const matches = (m: string, c: Concept) => m.startsWith('#') ? (m.endsWith('.') ? c.id.startsWith(m.slice(1)) : c.id === m.slice(1))
  : m.endsWith('.') ? c.facet.startsWith(m) : c.facet === m || c.facet.startsWith(m + '.');
/** which section a reading of a concept belongs to (by the concept's own polarity) */
function sectionOf(cfg: DepthConfig, c: Concept): string | null {
  const pick = (e: { to?: string; pos?: string; neg?: string }) => e.to ?? (c.pol === '-' ? e.neg : e.pos) ?? null;
  const e = cfg.map.find(x => x.match.some(m => matches(m, c)));
  return e ? pick(e) : cfg.fallback ? pick(cfg.fallback) : null;
}
/** why a verified reading of the palace was not told in the deep reading (kept in the trace, chapter evidence `untold`) */
export type UntoldReason = 'timing_main' | 'event' | 'no_section' | 'no_text' | 'same_reading' | 'guarded' | 'sensitive' | 'domain_unexplained';

export interface DepthReading { ruleId: string; concept: string; palace: string; pol: '+' | '-' | '~'; status: Resolved['status']; cites: string[];
  /** the stars / Hóa / Tuần-Triệt the reading fired on, with the palace each stands in */
  atoms: Array<{ name: string; palace: string }>;
  /** the reading's main star (the first chính tinh, else the first star / Hóa it names in its own palace) */
  star?: string;
  /** a book relation that reduces it (its status is weakened / softened / narrowed) */
  reducedBy?: string;
  /** a reading of the chính tinh this vô chính diệu palace borrows from the opposite palace (reason/borrow.ts, TT p.18) */
  borrowed?: { from: string; stars: string[] } }
export interface DepthUnit {
  kind: 'reading' | 'mechanism' | 'trigger' | 'link' | 'tame' | 'condition';
  section: string;
  reading?: DepthReading;
  nature?: StarNature; relation?: PalaceRelation;
  /** mechanism: the star whose nature is told, the palace it stands in, how it reaches the domain palace */
  star?: string; palace?: string; where?: Where | 'elsewhere';
  /** trigger / link: the elements (name@palace) */
  elements?: Array<{ name: string; palace: string; where: Where | 'elsewhere' }>;
  /** link kind */
  link?: 'shared_star' | 'hoa' | 'than' | 'relation' | 'ky_opp' | 'verdicts';
  /** tame: the star held in check */
  tamed?: string;
  verdicts?: DomainVerdict[];
}
export interface DepthPlan { version: string; domain: DepthDomain; palace: string; sections: Array<{ id: string; units: DepthUnit[] }>;
  /** verified readings of the palace the deep reading does not tell, and why */
  untold: Array<{ ruleId: string; reason: UntoldReason }> }

const LIVE = (r: Resolved) => r.status !== 'voided' && r.status !== 'divergent';
const SATS = ['Kình Dương', 'Đà La', 'Hỏa Tinh', 'Linh Tinh', 'Địa Không', 'Địa Kiếp'];
const HOA = ['Hóa Lộc', 'Hóa Quyền', 'Hóa Khoa', 'Hóa Kỵ'];
/** words of an event or a time in a marriage reading */
const EVENT = /lần|dang dở|ly dị|ly hôn|ly tán|bỏ nhau|góa|tái giá|tái hôn|muộn|sớm|xa cách|chia lìa|cưới|hai đời|tuổi|khóc/u;

export function natureOf(k: Knowledge, star: string, use: Use, said: Set<string>, opts: { palace?: string; pol?: '-' | '+'; concept?: string; prefix?: string[] } = {}): StarNature | undefined {
  const prefix = opts.prefix ?? [];
  // a nature is told after a reading only on the reading's own side: a limit is never the "reason" of a strength, nor the reverse
  const fits = (e: StarNature) => (!opts.pol || (e.pol ?? '+') === '±' || (e.pol ?? '+') === opts.pol)
    // after a reading, only a nature that speaks of that reading's matter (explains), never a generic trait of the star
    && (!opts.concept || (e.explains ?? []).some(x => x === opts.concept || (x.endsWith('.') && opts.concept!.startsWith(x))))
    // as the palace's own structure (no reading to explain), a nature is told only when it speaks of the domain: it names the palace, or it
    // explains readings of the domain's matter (Thiên Cơ's "tài tổ chức" says nothing about a marriage)
    && (!!opts.concept || e.palace === opts.palace || e.star.startsWith('Hóa ') || (e.explains ?? []).some(x => prefix.some(d => x.startsWith(d))));
  const xs = (k.kg?.starNature?.entries ?? []).filter(e => (e.star === star || (e.also ?? []).includes(star)) && e.use.includes(use) && !said.has(e.id) && !e.tames && fits(e)
    && (!e.palace || e.palace === opts.palace));
  // the entry naming the domain's palace first, then one of exactly the asked side, then the file's order
  return [...xs].sort((a, b) => Number(b.palace === opts.palace) - Number(a.palace === opts.palace)
    || Number((b.pol ?? '+') === opts.pol) - Number((a.pol ?? '+') === opts.pol))[0];
}

/** The deep reading of one domain: data only, no prose. `said` are the star-nature ids the report already told (each is told once). */
export function domainDepth(chart: ChartInput, k: Knowledge, domain: DepthDomain, inp: { resolved: Resolved[]; ledger: Ledger; said?: Set<string>; borrowed?: Borrowed[] }): DepthPlan {
  const cfg = depthConfig(k, domain);
  if (!cfg) return { version: DEPTH_VERSION, domain, palace: '', sections: [], untold: [] };
  const P = cfg.palace, use = cfg.use, prefix = cfg.prefix;
  const untold: DepthPlan['untold'] = [];
  const cmap = new Map<string, Concept>(k.concepts.concepts.map(c => [c.id, c]));
  const rmap = new Map(k.rules.map(r => [r.id, r]));
  const guards = new Map((k.kg?.positionGuards ?? []).map(x => [x.ruleId, x]));
  const byName = new Map(chart.palaces.map(p => [p.name, p]));
  const pal = byName.get(P)!;
  const tp = tamPhuongOf(chart, P);
  const whereOf = (palace: string): Where | 'elsewhere' => tp.find(x => x.p.name === palace)?.where ?? 'elsewhere';
  const said = inp.said ?? new Set<string>();
  const sections = new Map<string, DepthUnit[]>(cfg.sections.map(s => [s, []]));
  const push = (u: DepthUnit) => sections.get(u.section)?.push(u);
  const ev: PalaceEvidence = palaceEvidence(chart, k, P, { resolved: inp.resolved });

  // ---- readings of the domain's palaces, by section ----
  const placed = inp.resolved.filter(r => LIVE(r) && rmap.get(r.ruleId)?.reviewStatus === 'verified' && !r.additive).filter(r => {
    const gd = guards.get(r.ruleId);
    const ok = !gd || guardHolds(gd, r.atoms, chart.palaces, { here: r.palace ?? 'Mệnh', tuHoa: chart.tu_hoa });
    // a reading whose atoms do not stand where the book's wording puts them (position guard, R1) is not told, and says so
    if (!ok && r.subject === `palace:${P}`) untold.push({ ruleId: r.ruleId, reason: 'guarded' });
    return ok;
  });
  const seen = new Set<string>();
  const readings: DepthReading[] = [];
  // the domain's own palace: the readings of Mệnh, Tài Bạch, Thiên Di… are their chapters' (a Mệnh reading the Mệnh plan left out stays out)
  const palace = P;
  for (const r of placed) {
    if (r.subject !== `palace:${palace}`) continue;
    const c = cmap.get(r.concept);
    if (!c) continue;
    // Phu Thê: a timing reading stays with the main reading; a reading whose words tell an event or a time (dang dở, nhiều lần, xa cách, sớm /
    // muộn …) is not told in the deep reading
    if (cfg.noTiming && (c.facet.endsWith('.timing') || c.facet === 'life.mobility')) { untold.push({ ruleId: r.ruleId, reason: 'timing_main' }); continue; }
    if (cfg.noEvents && EVENT.test(rmap.get(r.ruleId)?.reading ?? k.claims[rmap.get(r.ruleId)?.consequences[0]?.claim ?? ''] ?? '')) { untold.push({ ruleId: r.ruleId, reason: 'event' }); continue; }
    const sec = sectionOf(cfg, c);
    if (!sec) { untold.push({ ruleId: r.ruleId, reason: 'no_section' }); continue; }
    if (seen.has(`${r.ruleId}|${r.concept}`)) continue;
    seen.add(`${r.ruleId}|${r.concept}`);
    const atoms = groundAtoms(r.atoms, chart);
    const own = byName.get(palace)!;
    const star = atoms.find(a => a.palace === palace && own.major_stars.includes(a.name))?.name ?? atoms.find(a => a.palace === palace)?.name ?? atoms[0]?.name;
    const pol = (c.pol === '~' ? '~' : (c.pol === '+') === (r.stance === 'affirms') ? '+' : '-') as DepthReading['pol'];
    const x: DepthReading = { ruleId: r.ruleId, concept: r.concept, palace, pol, status: r.status, cites: r.cites, atoms: dedupeAtoms(atoms), ...(star ? { star } : {}),
      ...(r.status !== 'holds' && r.by[0] ? { reducedBy: r.by[0].byRule } : {}) };
    readings.push(x);
    push({ kind: 'reading', section: sec, reading: x });
  }
  // ---- the chính tinh a vô chính diệu palace borrows (TT p.18): after its own readings, lower confidence; a rule whose wording the
  // position guards hold to a seated star is not read on a borrowed one ----
  for (const r of (inp.borrowed ?? []).filter(b => b.subject === `palace:${P}` && LIVE(b) && !b.additive && rmap.get(b.ruleId)?.reviewStatus === 'verified' && !guards.has(b.ruleId))) {
    const c = cmap.get(r.concept);
    if (!c || (cfg.noTiming && (c.facet.endsWith('.timing') || c.facet === 'life.mobility'))) continue;
    if (cfg.noEvents && EVENT.test(rmap.get(r.ruleId)?.reading ?? k.claims[rmap.get(r.ruleId)?.consequences[0]?.claim ?? ''] ?? '')) continue;
    const sec = sectionOf(cfg, c);
    if (!sec || seen.has(`${r.ruleId}|${r.concept}`)) continue;
    seen.add(`${r.ruleId}|${r.concept}`);
    const atoms = dedupeAtoms(groundAtoms(r.atoms, chart));
    const star = atoms.find(a => r.borrowed.stars.includes(a.name))?.name;
    const pol = (c.pol === '~' ? '~' : (c.pol === '+') === (r.stance === 'affirms') ? '+' : '-') as DepthReading['pol'];
    const x: DepthReading = { ruleId: r.ruleId, concept: r.concept, palace, pol, status: r.status, cites: r.cites, atoms, ...(star ? { star } : {}), borrowed: r.borrowed };
    readings.push(x);
    push({ kind: 'reading', section: sec, reading: x });
  }

  // ---- mechanism for each reading's main star (once per star in the chapter), trigger for its far elements ----
  const toldStar = new Set<string>();
  for (const [sec, us] of sections) for (const u of [...us]) {
    const x = u.reading!;
    const far = x.atoms.filter(a => a.palace !== x.palace && a.palace !== P);
    if (x.palace === P && far.length) us.push({ kind: 'trigger', section: sec, reading: x, elements: far.map(a => ({ ...a, where: whereOf(a.palace) })) });
    // a timing or neutral reading has no 'why' in a star's nature (công danh đến muộn is not explained by what Tả Phụ is)
    if (x.star && x.pol !== '~' && !toldStar.has(x.star)) {
      const n = natureOf(k, x.star, use, said, { palace: P, pol: x.pol === '-' ? '-' : '+', concept: x.concept, prefix });
      if (n) { toldStar.add(x.star); said.add(n.id); us.push({ kind: 'mechanism', section: sec, reading: x, nature: n, star: x.star, palace: x.palace, where: whereOf(x.palace) }); }
    }
  }

  // ---- the domain palace's own structure where no reading stood on it ----
  const majorsHere = ev.majors.map(m => m.star);
  const orient = cfg.orient;
  for (const m of ev.majors) {
    if (toldStar.has(m.star) || m.borrowed) continue;
    const n = natureOf(k, m.star, use, said, { palace: P, prefix });
    if (!n) continue;
    toldStar.add(m.star); said.add(n.id);
    push({ kind: 'mechanism', section: orient, nature: n, star: m.star, palace: P, where: 'self' });
  }
  // a VCD palace: the chính tinh that reach it from its tam phương carry its orientation (the books borrow the opposite palace's stars only for
  // Mệnh and Thiên Di, KL pp.218, 222: here the stars are named where they stand, never read as the palace's own)
  if (!majorsHere.length || ev.majors.every(m => m.borrowed)) {
    const near = ev.tamPhuong.filter(m => m.where === 'trine' && (m.dignity === 'miếu' || m.dignity === 'vượng' || m.dignity === 'đắc'));
    for (const m of near.slice(0, 2)) {
      if (toldStar.has(m.star)) continue;
      const n = natureOf(k, m.star, use, said, { palace: P, prefix });
      if (!n) continue;
      toldStar.add(m.star); said.add(n.id);
      push({ kind: 'mechanism', section: orient, nature: n, star: m.star, palace: m.palace, where: 'trine' });
    }
  }
  // the Hóa standing in the palace (KL pp.195-197 on what each Hóa is)
  for (const h of ev.hoa.filter(x => x.where === 'self')) {
    const n = natureOf(k, h.hoa, use, said, { palace: P, prefix });
    if (!n) continue;
    said.add(n.id); toldStar.add(h.hoa);
    const sec = h.hoa === 'Hóa Kỵ' ? cfg.obst : h.hoa === 'Hóa Quyền' ? cfg.quyen : orient;
    push({ kind: 'mechanism', section: sec, nature: n, star: h.hoa, palace: P, where: 'self', elements: [{ name: `${h.star}|${h.hoa}`, palace: P, where: 'self' }] });
  }
  // limiting elements of the palace: the sát / Hao / Kỵ nature, in the obstacle section
  const obst = cfg.obst;
  for (const e of [...ev.limit, ...ev.mixed.filter(x => x.kind === 'ky_carrier')]) {
    const name = e.kind === 'hoa_ky' ? 'Hóa Kỵ' : e.star;
    // a borrowed chính tinh does not stand in the palace: its nature is not told as the palace's own
    if (!name || toldStar.has(name) || e.borrowed || e.kind === 'major_ham' || e.kind === 'tuan' || e.kind === 'triet') continue;
    const n = natureOf(k, name, use, said, { palace: P, pol: '-', prefix });
    if (!n || n.pol !== '-') continue;
    toldStar.add(name); said.add(n.id);
    push({ kind: 'mechanism', section: obst, nature: n, star: name, palace: P, where: 'self' });
  }

  // ---- interactions the chart has: a star of the palace or its tam phương holding a limiting star of the palace in check ----
  const satHere = ev.stars.filter(s => s.where === 'self' && SATS.includes(s.star)).map(s => s.star);
  const tamers = (k.kg?.starNature?.entries ?? []).filter(e => e.tames?.length);
  for (const t of tamers) {
    const holders = [t.star, ...(t.also ?? [])];
    const at = [...ev.majors, ...ev.tamPhuong, ...ev.stars].find(s => holders.includes(s.star)) ?? ev.hoa.find(h => holders.includes(h.hoa)) as unknown as { star: string; palace: string; where: Where } | undefined;
    const tamed = satHere.filter(s => t.tames!.includes(s));
    if (!at || !tamed.length || said.has(t.id)) continue;
    said.add(t.id);
    const holder = holders.find(h => [...ev.majors, ...ev.tamPhuong, ...ev.stars].some(s => s.star === h) || ev.hoa.some(x => x.hoa === h))!;
    push({ kind: 'tame', section: obst, nature: t, star: holder, palace: (at as { palace: string }).palace, where: whereOf((at as { palace: string }).palace), tamed: tamed.join('|') });
  }

  // ---- links to the other palaces of the domain ----
  const linkSec = cfg.link;
  // Thân cư: Khảo Luận's sentence on what the Thân palace means (KL p.215)
  const thanRel = (k.kg?.starNature?.relations ?? []).find(r => r.when === 'than' && r.palace === P);
  if (pal.is_than && thanRel && !said.has(thanRel.id)) { said.add(thanRel.id); push({ kind: 'link', section: cfg.thanSection ?? linkSec, link: 'than', relation: thanRel, palace: P }); }
  // the natal Tứ Hóa across Mệnh–Tài–Quan: told once, in the career chapter (the money chapter would only repeat it)
  if (cfg.hoaLink) {
    const hs = Object.entries(chart.tu_hoa).map(([h, v]) => ({ h, star: v.star, palace: chart.palaces.find(p => p.branch_index === v.branch)!.name }))
      .filter(x => ['Mệnh', 'Tài Bạch', 'Quan Lộc'].includes(x.palace));
    if (hs.length >= 2) push({ kind: 'link', section: linkSec, link: 'hoa', elements: hs.map(x => ({ name: `${x.star}|${x.h}`, palace: x.palace, where: whereOf(x.palace) })) });
  }
  // a star the book ties to both palaces (Thái Dương: "hễ có danh thì dễ kiếm tiền", KL p.85) standing in either
  for (const e of (k.kg?.starNature?.entries ?? []).filter(x => x.link?.includes(P) && x.use.includes(use) && !said.has(x.id))) {
    const other = e.link!.find(q => q !== P)!;
    const at = [P, other].map(q => byName.get(q)!).find(q => q.major_stars.includes(e.star));
    if (!at) continue;
    said.add(e.id);
    push({ kind: 'link', section: linkSec, link: 'shared_star', nature: e, star: e.star, palace: at.name, where: whereOf(at.name) });
  }
  // Tài Bạch: the palaces Khảo Luận says hold its balance (KL p.216); Điền Trạch: nhà đất as the lasting form of wealth (KL p.219)
  {
    for (const id of cfg.relations ?? []) {
      const r = (k.kg?.starNature?.relations ?? []).find(x => x.id === id);
      // a relation the book states only for a woman's chart (TH p.96: Phu Thê with Phúc Đức) is told only there
      if (r?.when === 'nu' && chart.gender !== 'female') continue;
      // a relation whose sentence is a condition ("Mệnh, Thân gặp hung sát tinh mà Phúc có phúc tinh đắc địa …") is told only on a chart that
      // has it: a general line that does not apply would repeat from chart to chart
      if (r?.when && !relationHolds(chart, r.when, P)) continue;
      if (r && !said.has(r.id)) { said.add(r.id); push({ kind: 'link', section: linkSec, link: 'relation', relation: r, palace: r.palace }); }
    }
  }
  // a Hóa Kỵ in the opposite palace reaches the domain palace (Quan Lộc ↔ Phu Thê, Tài Bạch ↔ Phúc Đức)
  const kyAt = chart.palaces.find(p => p.branch_index === chart.tu_hoa['Hóa Kỵ']?.branch);
  if (kyAt && whereOf(kyAt.name) === 'opp' && !readings.some(x => x.palace === P && x.atoms.some(a => a.name === 'Hóa Kỵ')))
    push({ kind: 'link', section: obst, link: 'ky_opp', elements: [{ name: `${chart.tu_hoa['Hóa Kỵ'].star}|Hóa Kỵ`, palace: kyAt.name, where: 'opp' }] });

  // ---- the conditional conclusion: the domain verdicts with their limits ----
  // the money chapter already concludes its three parts in the short reading: its deep reading only adds the sides of the earning part
  const ids = cfg.verdicts;
  const verdicts = ids.map(id => inp.ledger.domains.find(v => v.id === id)).filter((v): v is DomainVerdict => !!v && v.verdict !== 'chua_du');
  if (verdicts.length && cfg.cond) push({ kind: 'condition', section: cfg.cond, verdicts });

  // a section stands only on a chart-specific anchor: a reading, a trigger, a link, a tame or a mechanism of a star the palace holds
  const out = cfg.sections.map(id => ({ id, units: sections.get(id)! })).filter(s => s.units.some(u => u.kind !== 'mechanism' || u.palace === P || u.where === 'trine'));
  return { version: DEPTH_VERSION, domain, palace: P, sections: out, untold };
}

/** The elements a reading stands on, by palace: stars, Hóa, Tuần/Triệt, a vô chính diệu palace; a brightness only for a star that stands
 *  there (a rule testing a star's brightness without its presence leaves a dignity atom of an absent star: never a ground) */
function groundAtoms(atoms: Resolved['atoms'], chart: ChartInput): Array<{ name: string; palace: string }> {
  const present = (name: string, palace: string) => !!chart.palaces.find(p => p.name === palace && (p.stars.includes(name) || p.major_stars.includes(name)));
  return atoms.filter(a => a.palace && (a.kind === 'star' || a.kind === 'hoa' || a.kind === 'tuan_triet' || a.kind === 'vcd' || (a.kind === 'dignity' && (atoms.some(b => b.kind === 'star' && b.name === a.name && b.palace === a.palace) || present(a.name, a.palace!)))))
    .map(a => ({ name: a.kind === 'vcd' ? 'vô chính diệu' : a.name, palace: a.palace! }));
}
/** The chart side a conditional palace relation needs (star_nature.json relations[].when). */
function relationHolds(chart: ChartInput, when: string, P: string): boolean {
  const pal = (n: string) => chart.palaces.find(p => p.name === n)!;
  const sat = (n: string) => pal(n).stars.some(s => SATS.includes(s));
  const dig = (n: string) => pal(n).major_stars.map(s => (pal(n).major_dignity as Record<string, string> | undefined)?.[s]);
  const bright = (n: string) => dig(n).some(x => x === 'miếu' || x === 'vượng' || x === 'đắc');
  if (when === 'nu' || when === 'than') return true;
  if (when === 'menh_hard_phuc_bright') return (sat('Mệnh') || dig('Mệnh').includes('hãm')) && bright('Phúc Đức');
  if (when === 'sat_here') return sat(P);
  // "quá đẹp" (KL p.220): every chính tinh bright, one at miếu / vượng, no sát tinh or Hóa Kỵ, and more than a lone star (a second chính
  // tinh or a cát tinh of the six): a single Thiên Tướng đắc is not "quá đẹp"
  if (when === 'bright_no_sat') {
    const p = pal(P), ky = chart.palaces.find(q => q.branch_index === chart.tu_hoa['Hóa Kỵ']?.branch)?.name === P;
    const CAT = ['Tả Phụ', 'Hữu Bật', 'Văn Xương', 'Văn Khúc', 'Thiên Khôi', 'Thiên Việt'];
    return dig(P).length > 0 && dig(P).every(x => x === 'miếu' || x === 'vượng' || x === 'đắc') && dig(P).some(x => x === 'miếu' || x === 'vượng')
      && !sat(P) && !ky && (p.major_stars.length >= 2 || p.stars.some(s => CAT.includes(s)));
  }
  return false;
}
function dedupeAtoms(xs: Array<{ name: string; palace: string }>) {
  const seen = new Set<string>();
  return xs.filter(x => !seen.has(`${x.name}@${x.palace}`) && seen.add(`${x.name}@${x.palace}`));
}
export const _test = { sectionOf, matches };
export type { Element, Palace };
