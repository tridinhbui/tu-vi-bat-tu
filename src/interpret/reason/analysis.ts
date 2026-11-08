// The structured analysis of each life domain (plan docs/plans/THIEN-BAN-33-REVIEW-PLAN.md G9.5): the one input a narrative layer may
// voice (G10). It joins the domain ledger (reason/ledger.ts: the book readings and their verdict) with the configuration of the domain's
// core palace (reason/configuration.ts: the structure those readings stand in). Every item carries an evidence id: `rule:<id>` for a fired
// verified rule, `member:<id>` / `rel:<n>` for a configuration member or relation (chart facts and page-cited relations).
// The level ceiling (G9.4): a conclusion's scope is the highest level its evidence reaches; a reading of one star never concludes a
// whole domain (INV-12 checks the Tổng luận against it).
import type { ChartInput, Knowledge } from '../types.ts';
import type { Resolved } from '../kg/resolve.ts';
import { buildLedger, type DomainVerdict, type LedgerItem, type Verdict } from './ledger.ts';
import { configurationOf, type Configuration, type Level, type Member } from './configuration.ts';
import { isGrave } from '../prose/severity.ts';

export const ANALYSIS_VERSION = 'analysis-0.1.0';
export interface Ev { id: string; text: string; level: Level; cite?: string }
export interface Analysis {
  topic: string; domain: string; label: string; level: Level;
  dominant_configuration: string | null;
  supporting_evidence: Ev[]; limiting_evidence: Ev[]; interactions: Ev[]; rescues: Ev[];
  unresolved_conditions: string[];
  activation: Configuration['activation'];
  conclusion: { type: Verdict; base: '+' | '-' | null; scope: 'mot_sao' | 'cung' | 'tam_phuong' | 'cach_cuc' | 'menh_tai_quan'; confidence: 'ro' | 'vua' | 'tam'; severity: 'none' | 'grave' };
  evidence_ids: string[];
}
const SCOPE: Record<Level, Analysis['conclusion']['scope']> = { 1: 'mot_sao', 2: 'cung', 3: 'tam_phuong', 4: 'cach_cuc', 5: 'menh_tai_quan', 6: 'menh_tai_quan' };
const TRIAD = new Set(['Mệnh', 'Tài Bạch', 'Quan Lộc', 'Thiên Di']);

/** a ledger reading's level: a lone minor star 1, the palace's own stars 2, stars of other palaces (tam phương, Hóa) 3 */
function itemLevel(x: LedgerItem): Level {
  const far = x.at.some(a => a.palace !== x.palace);
  if (far) return 3;
  return x.seat.tier >= 5 && x.stars.length <= 1 ? 1 : 2;
}
const ev = (x: LedgerItem, cmap: Map<string, string>): Ev => ({ id: `rule:${x.ruleId}`, text: `${cmap.get(x.concept) ?? x.concept} (${x.stars.join(', ') || x.palace}, cung ${x.palace})`, level: itemLevel(x), cite: x.cites[0] });
const mev = (m: Member): Ev => ({ id: `member:${m.id}`, text: `${m.name} (${m.palace}): ${m.does}`, level: m.level, ...(m.cite ? { cite: m.cite } : {}) });

export function analysisOf(v: DomainVerdict, cfg: Configuration | undefined, cmap: Map<string, string>, thisAge?: number): Analysis {
  const pos = [...v.pos, ...v.mixed].map(x => ev(x, cmap)), neg = v.neg.map(x => ev(x, cmap));
  const sup = cfg ? cfg.members.filter(m => m.role === 'nen' || m.role === 'bien_tinh' || m.role === 'tro_luc').map(mev) : [];
  const lim = cfg ? cfg.members.filter(m => m.role === 'tru' || m.role === 'pha').map(mev) : [];
  const rels = cfg ? cfg.relations.map((r, i) => ({ id: `rel:${cfg.palace}:${i}`, text: r.note, level: 3 as Level, ...(r.cite ? { cite: r.cite } : {}) })) : [];
  const rescues = rels.filter(r => /cứu giải|giải được|giảm bớt|kìm/u.test(r.text));
  const interactions = rels.filter(r => !rescues.includes(r));
  // the level ceiling: the highest level of the evidence the verdict rests on; Mệnh–Tài–Quan (5) only when readings of two of them stand
  const items = [...v.pos, ...v.neg, ...v.mixed];
  let level: Level = Math.max(1, ...items.map(itemLevel)) as Level;
  if (cfg && items.length) level = Math.max(level, Math.min(cfg.level, 3)) as Level;
  if (new Set(items.map(x => x.palace).filter(p => TRIAD.has(p))).size >= 2) level = 5;
  const unresolved: string[] = [];
  if (v.verdict === 'chua_phan_xu' || v.verdict === 'hai_mat' || v.verdict === 'chua_du') {
    const next = (cfg?.activation ?? []).filter(a => (thisAge === undefined || a.age_to >= thisAge) && a.age_from < 80 && a.members.length).slice(0, 2);
    unresolved.push(next.length ? `điều có thể làm cán cân nghiêng: ${next.map(a => `đại hạn ${a.age_from}–${a.age_to} (${a.what})`).join('; ')}` : 'chưa có đại hạn nào trước 80 tuổi chạm vào thành viên của tổ hợp');
  }
  for (const q of cfg?.questions ?? []) if (!q.known) unresolved.push(`${q.q} ${q.a}`);
  const confidence: Analysis['conclusion']['confidence'] = v.verdict === 'thuan' || v.verdict === 'tro_ngai' ? 'ro'
    : v.verdict === 'co_dieu_kien' || v.verdict === 'nghieng_ve' || v.verdict === 'giam_nhe' ? 'vua' : 'tam';
  const supporting = [...pos, ...sup], limiting = [...neg, ...lim];
  return {
    topic: v.label, domain: v.id, label: v.label, level, dominant_configuration: cfg && cfg.state !== 'chua_du' ? cfg.id : null,
    supporting_evidence: supporting, limiting_evidence: limiting, interactions, rescues, unresolved_conditions: unresolved, activation: cfg?.activation ?? [],
    conclusion: { type: v.verdict, base: v.base, scope: SCOPE[level], confidence, severity: items.some(x => isGrave(x.ruleId)) ? 'grave' : 'none' },
    evidence_ids: [...new Set([...supporting, ...limiting, ...interactions, ...rescues].map(e => e.id))],
  };
}

/** The core palace of a domain (or of a domain part), from kg/domains.json. */
function corePalace(k: Knowledge, id: string): string | undefined {
  const D = (k.kg?.domains as { domains?: Record<string, { palaces?: Record<string, string>; parts?: Record<string, { palaces: Record<string, string> }> }> } | undefined)?.domains ?? {};
  const [d, part] = id.split('.'), def = D[d];
  const ps = (part ? def?.parts?.[part]?.palaces : def?.palaces) ?? {};
  return Object.keys(ps).find(p => ps[p] === 'core');
}

/** Every domain's analysis for one chart, with the configurations they rest on. */
export function analyses(chart: ChartInput, k: Knowledge, resolved: Resolved[], thisAge?: number): { version: string; domains: Analysis[]; configurations: Configuration[] } {
  const led = buildLedger(chart, k, resolved);
  const cmap = new Map(k.concepts.concepts.map(c => [c.id, (c as { np?: string }).np ?? c.id]));
  const cfgs = new Map<string, Configuration>();
  const cfgOf = (P: string) => cfgs.get(P) ?? cfgs.set(P, configurationOf(chart, k, P, resolved)).get(P)!;
  const domains = led.domains.map(v => { const P = corePalace(k, v.id); return analysisOf(v, P ? cfgOf(P) : undefined, cmap, thisAge); });
  return { version: ANALYSIS_VERSION, domains, configurations: [...cfgs.values()] };
}
