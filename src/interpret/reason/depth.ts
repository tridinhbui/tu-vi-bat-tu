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

export const DEPTH_VERSION = 'depth-1.0.0';
export type Use = 'career' | 'money' | 'marriage' | 'property';
export interface StarNature { id: string; star: string; also?: string[]; page: number; quote: string; text: string; use: Use[]; palace?: string;
  /** '+' (default) a strength, '-' a limit, '±' a nature with both edges: told after a reading only of a matching side */
  pol?: '+' | '-' | '±';
  tames?: string[]; link?: string[] }
export interface PalaceRelation { id: string; palace: string; page: number; quote: string; text: string; when?: string; with?: string[] }
export interface StarNatureFile { version: string; basis: string; entries: StarNature[]; relations: PalaceRelation[] }

export type DepthDomain = 'cong_danh' | 'tai_bach' | 'phu_the';
export const DEPTH_PALACE: Record<DepthDomain, string> = { cong_danh: 'Quan Lộc', tai_bach: 'Tài Bạch', phu_the: 'Phu Thê' };
const USE: Record<DepthDomain, Use> = { cong_danh: 'career', tai_bach: 'money', phu_the: 'marriage' };
/** the palaces whose readings a domain's deep reading gathers (domains.json, a labelled system convention) and their place in it */
const PALACES: Record<DepthDomain, string[]> = { cong_danh: ['Quan Lộc', 'Mệnh', 'Tài Bạch', 'Thiên Di'], tai_bach: ['Tài Bạch', 'Mệnh', 'Quan Lộc', 'Phúc Đức', 'Điền Trạch'],
  phu_the: ['Phu Thê', 'Phúc Đức', 'Mệnh'] };
/** the sections of each domain, in reading order */
export const SECTIONS: Record<DepthDomain, string[]> = {
  cong_danh: ['huong', 'the_manh', 'moi_truong', 'quyen', 'nhip', 'tro_ngai', 'tien_bac'],
  tai_bach: ['kiem', 'tich_luy', 'ben', 'chi_tieu', 'rui_ro', 'lien_cung'],
  phu_the: ['dong_luc', 'hop', 'giao_tiep', 'cang_thang', 'giu', 'dieu_kien'],
};
/** which section a reading of a concept belongs to, by domain (concept id first, then facet prefix) */
function sectionOf(d: DepthDomain, c: Concept, palace: string): string | null {
  const f = c.facet, id = c.id;
  if (d === 'cong_danh') {
    if (palace !== 'Quan Lộc' && !f.startsWith('career.')) return null;
    if (f.startsWith('career.path') || f.startsWith('career.expertise') || id === 'adapt.unsteady') return c.pol === '-' ? 'tro_ngai' : 'huong';
    if (id === 'career.authority' || id === 'career.status') return 'quyen';
    if (id === 'career.success' || id === 'career.fame') return 'the_manh';
    if (f === 'career.support') return c.pol === '-' ? 'tro_ngai' : 'moi_truong';
    if (f === 'career.timing') return 'nhip';
    if (f.startsWith('career.')) return c.pol === '-' ? 'tro_ngai' : 'the_manh';
    if (f.startsWith('finance.') && palace === 'Quan Lộc') return 'tien_bac';
    return null;
  }
  if (d === 'tai_bach') {
    if (!f.startsWith('finance.')) return null;
    if (f === 'finance.property') return 'tich_luy';
    if (f === 'finance.source') return 'kiem';
    if (f === 'finance.style') return 'chi_tieu';
    if (f === 'finance.retention') return c.pol === '-' ? 'rui_ro' : 'ben';
    if (f === 'finance.flow') return c.pol === '-' ? 'rui_ro' : 'kiem';
    return null;
  }
  // Phu Thê: the bond; never a timing or event concept
  if (f.endsWith('.timing') || f === 'life.mobility') return null;
  if (palace !== 'Phu Thê' && !f.startsWith('relationships.marriage')) return null;
  if (id === 'rel.harmony') return 'giu';
  if (id === 'rel.strain' || id === 'rel.jealous') return 'cang_thang';
  if (id === 'rel.partner' || f.startsWith('identity.') || f.startsWith('values.') || f.startsWith('career.') || f.startsWith('finance.')) return 'hop';
  if (f.startsWith('cognition') || id.startsWith('cog.') || id.startsWith('comm.') || id.startsWith('temper.')) return 'giao_tiep';
  if (f.startsWith('relationships.marriage')) return c.pol === '-' ? 'cang_thang' : 'giu';
  return palace === 'Phu Thê' ? 'dong_luc' : null;
}

export interface DepthReading { ruleId: string; concept: string; palace: string; pol: '+' | '-' | '~'; status: Resolved['status']; cites: string[];
  /** the stars / Hóa / Tuần-Triệt the reading fired on, with the palace each stands in */
  atoms: Array<{ name: string; palace: string }>;
  /** the reading's main star (the first chính tinh, else the first star / Hóa it names in its own palace) */
  star?: string;
  /** a book relation that reduces it (its status is weakened / softened / narrowed) */
  reducedBy?: string }
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
export interface DepthPlan { version: string; domain: DepthDomain; palace: string; sections: Array<{ id: string; units: DepthUnit[] }> }

const LIVE = (r: Resolved) => r.status !== 'voided' && r.status !== 'divergent';
const SATS = ['Kình Dương', 'Đà La', 'Hỏa Tinh', 'Linh Tinh', 'Địa Không', 'Địa Kiếp'];
const HOA = ['Hóa Lộc', 'Hóa Quyền', 'Hóa Khoa', 'Hóa Kỵ'];
/** words of an event or a time in a marriage reading */
const EVENT = /lần|dang dở|ly dị|ly hôn|ly tán|bỏ nhau|góa|tái giá|tái hôn|muộn|sớm|xa cách|chia lìa|cưới|hai đời|tuổi|khóc/u;

export function natureOf(k: Knowledge, star: string, use: Use, said: Set<string>, opts: { palace?: string; pol?: '-' | '+' } = {}): StarNature | undefined {
  // a nature is told after a reading only on the reading's own side: a limit is never the "reason" of a strength, nor the reverse
  const fits = (e: StarNature) => !opts.pol || (e.pol ?? '+') === '±' || (e.pol ?? '+') === opts.pol;
  const xs = (k.kg?.starNature?.entries ?? []).filter(e => (e.star === star || (e.also ?? []).includes(star)) && e.use.includes(use) && !said.has(e.id) && !e.tames && fits(e)
    && (!e.palace || e.palace === opts.palace));
  // the entry naming the domain's palace first, then one of exactly the asked side, then the file's order
  return [...xs].sort((a, b) => Number(b.palace === opts.palace) - Number(a.palace === opts.palace)
    || Number((b.pol ?? '+') === opts.pol) - Number((a.pol ?? '+') === opts.pol))[0];
}

/** The deep reading of one domain: data only, no prose. `said` are the star-nature ids the report already told (each is told once). */
export function domainDepth(chart: ChartInput, k: Knowledge, domain: DepthDomain, inp: { resolved: Resolved[]; ledger: Ledger; said?: Set<string> }): DepthPlan {
  const P = DEPTH_PALACE[domain], use = USE[domain];
  const cmap = new Map<string, Concept>(k.concepts.concepts.map(c => [c.id, c]));
  const rmap = new Map(k.rules.map(r => [r.id, r]));
  const guards = new Map((k.kg?.positionGuards ?? []).map(x => [x.ruleId, x]));
  const byName = new Map(chart.palaces.map(p => [p.name, p]));
  const pal = byName.get(P)!;
  const tp = tamPhuongOf(chart, P);
  const whereOf = (palace: string): Where | 'elsewhere' => tp.find(x => x.p.name === palace)?.where ?? 'elsewhere';
  const said = inp.said ?? new Set<string>();
  const sections = new Map<string, DepthUnit[]>(SECTIONS[domain].map(s => [s, []]));
  const push = (u: DepthUnit) => sections.get(u.section)?.push(u);
  const ev: PalaceEvidence = palaceEvidence(chart, k, P, { resolved: inp.resolved });

  // ---- readings of the domain's palaces, by section ----
  const placed = inp.resolved.filter(r => LIVE(r) && rmap.get(r.ruleId)?.reviewStatus === 'verified' && !r.additive).filter(r => {
    const gd = guards.get(r.ruleId);
    return !gd || guardHolds(gd, r.atoms, chart.palaces, { here: r.palace ?? 'Mệnh', tuHoa: chart.tu_hoa });
  });
  const seen = new Set<string>();
  const readings: DepthReading[] = [];
  // the domain's own palace: the readings of Mệnh, Tài Bạch, Thiên Di… are their chapters' (a Mệnh reading the Mệnh plan left out stays out)
  for (const palace of PALACES[domain].slice(0, 1)) for (const r of placed) {
    if (r.subject !== `palace:${palace}`) continue;
    const c = cmap.get(r.concept);
    if (!c) continue;
    const sec = sectionOf(domain, c, palace);
    // Phu Thê: a reading whose words tell an event or a time (dang dở, nhiều lần, xa cách, sớm / muộn …) is not told in the deep reading
    if (domain === 'phu_the' && EVENT.test(rmap.get(r.ruleId)?.reading ?? k.claims[rmap.get(r.ruleId)?.consequences[0]?.claim ?? ''] ?? '')) continue;
    if (!sec || seen.has(`${r.ruleId}|${r.concept}`)) continue;
    seen.add(`${r.ruleId}|${r.concept}`);
    const atoms = r.atoms.filter(a => (a.kind === 'star' || a.kind === 'hoa' || a.kind === 'tuan_triet' || a.kind === 'dignity') && a.palace)
      .map(a => ({ name: a.kind === 'tuan_triet' ? a.name : a.name, palace: a.palace! }));
    const own = byName.get(palace)!;
    const star = atoms.find(a => a.palace === palace && own.major_stars.includes(a.name))?.name ?? atoms.find(a => a.palace === palace)?.name ?? atoms[0]?.name;
    const pol = (c.pol === '~' ? '~' : (c.pol === '+') === (r.stance === 'affirms') ? '+' : '-') as DepthReading['pol'];
    const x: DepthReading = { ruleId: r.ruleId, concept: r.concept, palace, pol, status: r.status, cites: r.cites, atoms: dedupeAtoms(atoms), ...(star ? { star } : {}),
      ...(r.status !== 'holds' && r.by[0] ? { reducedBy: r.by[0].byRule } : {}) };
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
      const n = natureOf(k, x.star, use, said, { palace: P, pol: x.pol === '-' ? '-' : '+' });
      if (n) { toldStar.add(x.star); said.add(n.id); us.push({ kind: 'mechanism', section: sec, reading: x, nature: n, star: x.star, palace: x.palace, where: whereOf(x.palace) }); }
    }
  }

  // ---- the domain palace's own structure where no reading stood on it ----
  const majorsHere = ev.majors.map(m => m.star);
  const orient = domain === 'cong_danh' ? 'huong' : domain === 'tai_bach' ? 'kiem' : 'dong_luc';
  for (const m of ev.majors) {
    if (toldStar.has(m.star) || m.borrowed) continue;
    const n = natureOf(k, m.star, use, said, { palace: P });
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
      const n = natureOf(k, m.star, use, said, { palace: P });
      if (!n) continue;
      toldStar.add(m.star); said.add(n.id);
      push({ kind: 'mechanism', section: orient, nature: n, star: m.star, palace: m.palace, where: 'trine' });
    }
  }
  // the Hóa standing in the palace (KL pp.195-197 on what each Hóa is)
  for (const h of ev.hoa.filter(x => x.where === 'self')) {
    const n = natureOf(k, h.hoa, use, said, { palace: P });
    if (!n) continue;
    said.add(n.id); toldStar.add(h.hoa);
    const sec = h.hoa === 'Hóa Kỵ' ? (domain === 'cong_danh' ? 'tro_ngai' : domain === 'tai_bach' ? 'rui_ro' : 'cang_thang')
      : h.hoa === 'Hóa Quyền' ? (domain === 'cong_danh' ? 'quyen' : domain === 'tai_bach' ? 'kiem' : 'hop') : orient;
    push({ kind: 'mechanism', section: sec, nature: n, star: h.hoa, palace: P, where: 'self', elements: [{ name: `${h.star}|${h.hoa}`, palace: P, where: 'self' }] });
  }
  // limiting elements of the palace: the sát / Hao / Kỵ nature, in the obstacle section
  const obst = domain === 'cong_danh' ? 'tro_ngai' : domain === 'tai_bach' ? 'rui_ro' : 'cang_thang';
  for (const e of [...ev.limit, ...ev.mixed.filter(x => x.kind === 'ky_carrier')]) {
    const name = e.kind === 'hoa_ky' ? 'Hóa Kỵ' : e.star;
    if (!name || toldStar.has(name) || e.kind === 'major_ham' || e.kind === 'tuan' || e.kind === 'triet') continue;
    const n = natureOf(k, name, use, said, { palace: P, pol: '-' });
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
  const linkSec = domain === 'cong_danh' ? 'tien_bac' : domain === 'tai_bach' ? 'lien_cung' : 'dieu_kien';
  // Thân cư: Khảo Luận's sentence on what the Thân palace means (KL p.215)
  const thanRel = (k.kg?.starNature?.relations ?? []).find(r => r.when === 'than' && r.palace === P);
  if (pal.is_than && thanRel && !said.has(thanRel.id)) { said.add(thanRel.id); push({ kind: 'link', section: domain === 'phu_the' ? 'dong_luc' : linkSec, link: 'than', relation: thanRel, palace: P }); }
  // the natal Tứ Hóa across the domain's tam phương (career / money: Mệnh–Tài–Quan; marriage: the Kỵ reaching Phu Thê)
  if (domain !== 'phu_the') {
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
  // Tài Bạch: the palaces Khảo Luận says hold its balance (KL p.216), and Điền Trạch (KL p.219)
  if (domain === 'tai_bach') {
    for (const id of ['tai.che_tai', 'dien.ben']) {
      const r = (k.kg?.starNature?.relations ?? []).find(x => x.id === id);
      if (r && !said.has(r.id)) { said.add(r.id); push({ kind: 'link', section: linkSec, link: 'relation', relation: r, palace: r.palace }); }
    }
  }
  // a Hóa Kỵ in the opposite palace reaches the domain palace (Quan Lộc ↔ Phu Thê, Tài Bạch ↔ Phúc Đức)
  const kyAt = chart.palaces.find(p => p.branch_index === chart.tu_hoa['Hóa Kỵ']?.branch);
  if (kyAt && whereOf(kyAt.name) === 'opp' && !readings.some(x => x.palace === P && x.atoms.some(a => a.name === 'Hóa Kỵ')))
    push({ kind: 'link', section: obst, link: 'ky_opp', elements: [{ name: `${chart.tu_hoa['Hóa Kỵ'].star}|Hóa Kỵ`, palace: kyAt.name, where: 'opp' }] });

  // ---- the conditional conclusion: the domain verdicts with their limits ----
  const ids = domain === 'cong_danh' ? ['cong_danh', 'tai_loc.kiem'] : domain === 'tai_bach' ? ['tai_loc.kiem', 'tai_loc.giu', 'tai_loc.tich_luy'] : ['hon_nhan'];
  const verdicts = ids.map(id => inp.ledger.domains.find(v => v.id === id)).filter((v): v is DomainVerdict => !!v && v.verdict !== 'chua_du');
  if (verdicts.length) push({ kind: 'condition', section: domain === 'cong_danh' ? 'tien_bac' : domain === 'tai_bach' ? 'lien_cung' : 'dieu_kien', verdicts });

  // a section stands only on a chart-specific anchor: a reading, a trigger, a link, a tame or a mechanism of a star the palace holds
  const out = SECTIONS[domain].map(id => ({ id, units: sections.get(id)! })).filter(s => s.units.some(u => u.kind !== 'mechanism' || u.palace === P || u.where === 'trine'));
  return { version: DEPTH_VERSION, domain, palace: P, sections: out };
}

function dedupeAtoms(xs: Array<{ name: string; palace: string }>) {
  const seen = new Set<string>();
  return xs.filter(x => !seen.has(`${x.name}@${x.palace}`) && seen.add(`${x.name}@${x.palace}`));
}
export const _test = { sectionOf };
export type { Element, Palace };
