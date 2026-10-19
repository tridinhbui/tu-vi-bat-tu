// Per-chart knowledge graph. Nodes: palaces, star placements, Tứ Hóa, findings, rules, sources, concepts. Edges carry the geometry
// (tam hợp / xung chiếu / giáp), what each finding was fired by, which book it cites, which concept it expresses, and — the basis of
// cross-palace reasoning — which star placements in WHICH palaces a finding depends on (a Mệnh reading that 'gặp Tử Vi' depends on the
// palace where Tử Vi actually sits).
import { classify, KB, type School } from './dignity.ts';
import { evaluate } from './dsl.ts';
import type { Evidence } from './semantic.ts';
import type { ChartInput, Facts, Palace } from './types.ts';

export type NodeKind = 'palace' | 'star' | 'hoa' | 'finding' | 'rule' | 'source' | 'concept';
export interface GNode { id: string; kind: NodeKind; label: string; data?: Record<string, unknown> }
export interface GEdge { src: string; dst: string; kind: string; data?: Record<string, unknown> }

export const SAT = ['Kình Dương', 'Đà La', 'Hỏa Tinh', 'Linh Tinh', 'Địa Không', 'Địa Kiếp'];
export const CAT = ['Tả Phụ', 'Hữu Bật', 'Văn Xương', 'Văn Khúc', 'Thiên Khôi', 'Thiên Việt', 'Lộc Tồn', 'Thiên Mã'];

export class ChartGraph {
  nodes = new Map<string, GNode>(); edges: GEdge[] = [];
  palaces: Map<string, Palace>; byBranch: Map<number, Palace>; starAt = new Map<string, string>(); chart: ChartInput;
  constructor(chart: ChartInput, evidence: Evidence[]) {
    this.chart = chart;
    this.palaces = new Map(chart.palaces.map(p => [p.name, p]));
    this.byBranch = new Map(chart.palaces.map(p => [p.branch_index, p]));
    const school = ((chart as { dignity_school?: School }).dignity_school ?? KB.default_school) as School;
    for (const p of chart.palaces) {
      this.node({ id: `palace:${p.name}`, kind: 'palace', label: p.name, data: { branch: p.branch, stem: p.stem, tuan: p.tuan, triet: p.triet, than: p.is_than } });
      for (const s of p.stars) {
        this.starAt.set(s, p.name);
        // brightness from the shared knowledge base (engine/data/dignity_kb.json), the same one the Python chart used
        const r = classify(s, p.branch, school);
        const dig = r.status === 'VERIFIED' ? r.value : null;
        this.node({ id: `star:${s}`, kind: 'star', label: s, data: {
          major: p.major_stars.includes(s), dignity: dig, dignityStatus: r.status,
          ...(r.status === 'VERIFIED' ? { dignityTerm: r.term, dignitySchool: r.school, dignityLocator: r.locator } : {}),
          ...(r.status === 'CONFLICT' ? { dignityAlternatives: r.alternatives } : {}),
          ...('variants' in r && r.variants ? { dignityVariants: r.variants } : {}) } });
        this.edge(`palace:${p.name}`, `star:${s}`, 'contains', { dignity: dig, dignityStatus: r.status });
        if (r.status === 'VERIFIED' || r.status === 'CONFLICT') {
          const src = KB.schools[r.school].source;
          this.node({ id: `source:${src}`, kind: 'source', label: src });
          const pages = r.status === 'VERIFIED' ? [r.locator] : r.alternatives.map(a => a.locator);
          this.edge(`star:${s}`, `source:${src}`, 'dignity_from', { branch: p.branch, status: r.status, pages });
        }
      }
      for (const [d, kind] of [[4, 'tam_hop'], [8, 'tam_hop'], [6, 'xung_chieu'], [1, 'giap'], [11, 'giap']] as Array<[number, string]>) {
        this.edge(`palace:${p.name}`, `palace:${this.byBranch.get((p.branch_index + d) % 12)!.name}`, kind);
      }
    }
    for (const [h, v] of Object.entries(chart.tu_hoa)) {
      this.node({ id: `hoa:${h}`, kind: 'hoa', label: h });
      this.edge(`hoa:${h}`, `star:${v.star}`, 'attached_to');
      this.starAt.set(h, this.byBranch.get(v.branch)!.name);
    }
    for (const e of evidence) {
      const fid = e.finding.id;
      this.node({ id: fid, kind: 'finding', label: e.core, data: { polarity: e.polarity } });
      this.node({ id: `rule:${e.rule.id}`, kind: 'rule', label: e.rule.id });
      this.edge(fid, `rule:${e.rule.id}`, 'fired_by');
      if (e.palace) this.edge(fid, `palace:${e.palace}`, 'about');
      for (const s of e.rule.sourceIds) { this.node({ id: `source:${s}`, kind: 'source', label: s }); this.edge(`rule:${e.rule.id}`, `source:${s}`, 'cites', { pages: e.cites }); }
      for (const c of e.concepts) { this.node({ id: `concept:${c.id}`, kind: 'concept', label: c.id }); this.edge(fid, `concept:${c.id}`, 'expresses'); }
      for (const s of e.presentStars) {
        const at = this.starAt.get(s);
        if (at) this.edge(fid, `star:${s}`, 'depends_on', { palace: at, cross: at !== e.palace, necessary: at !== e.palace ? this.necessary(e, s) : true });
      }
    }
  }
  /** Counterfactual test: would the rule still hold if star `s` were absent from the palaces that chiếu into the finding's palace?
   *  true = the reading needs that palace; false = another true branch already satisfies it ('Tử hoặc Phủ' with Phủ in the palace itself);
   *  null = the condition cannot be re-evaluated from base facts (derived facts), so necessity is not claimed. */
  private necessary(e: Evidence, s: string): boolean | null {
    if (!e.palace) return null;
    const facts: Facts = { ...(this.chart.base.chart ?? {}), ...(this.chart.base[`palace:${e.palace}`] ?? {}) };
    if (evaluate(e.rule.conditions, facts) !== true) return null;
    const own = /^palace\.(own_|rel\.self_|tu_hoa$)/;
    const cf: Facts = {};
    for (const [k, v] of Object.entries(facts)) cf[k] = Array.isArray(v) && !own.test(k) ? v.filter(x => x !== s) : v;
    if (SAT.includes(s) && typeof cf['palace.khi.sat_tp'] === 'number') cf['palace.khi.sat_tp'] = (cf['palace.khi.sat_tp'] as number) - 1;
    if (CAT.includes(s) && typeof cf['palace.khi.cat_tp'] === 'number') cf['palace.khi.cat_tp'] = (cf['palace.khi.cat_tp'] as number) - 1;
    return evaluate(e.rule.conditions, cf) !== true;
  }
  private node(n: GNode) { if (!this.nodes.has(n.id)) this.nodes.set(n.id, n); }
  private edge(src: string, dst: string, kind: string, data?: Record<string, unknown>) { this.edges.push({ src, dst, kind, data }); }

  palace(name: string): Palace { return this.palaces.get(name)!; }
  related(name: string, kind: 'tam_hop' | 'xung_chieu' | 'giap'): Palace[] {
    return this.edges.filter(e => e.src === `palace:${name}` && e.kind === kind).map(e => this.palace(e.dst.slice(7)));
  }
  /** The four palaces of the tam phương tứ chính of `name`: itself, its two tam hợp and its xung chiếu. */
  tamPhuong(name: string): Palace[] { return [this.palace(name), ...this.related(name, 'tam_hop'), ...this.related(name, 'xung_chieu')]; }
  hoaIn(name: string): string[] { return Object.entries(this.chart.tu_hoa).filter(([, v]) => this.byBranch.get(v.branch)!.name === name).map(([h, v]) => `${h} (${v.star})`); }
  /** Palaces (other than the finding's own) whose stars a finding depends on. */
  crossDependencies(findingId: string): Array<{ star: string; palace: string; necessary: boolean | null }> {
    return this.edges.filter(e => e.src === findingId && e.kind === 'depends_on' && e.data?.cross)
      .map(e => ({ star: e.dst.slice(5), palace: String(e.data!.palace), necessary: e.data!.necessary as boolean | null }));
  }
  satIn(names: string[]): string[] { return names.flatMap(n => this.palace(n).stars.filter(s => SAT.includes(s))); }
  catIn(names: string[]): string[] { return names.flatMap(n => this.palace(n).stars.filter(s => CAT.includes(s))); }
}
