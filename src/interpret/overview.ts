// POST /api/overview: the "Tổng quan lá số" page (docs/PRODUCT-PLAN.md 1.5) in one light response — the reasoner's frame and theses for Mệnh
// (reason/plan.ts, told as data: star, concept, verdict, rules and pages; no prose), the natal radar and the period levels (indices.ts). Shared by the
// Worker (src/index.ts) and tools/interpret/dev_server.ts. Book cách cục only: the draft formations stay out (draftFormations: false).
import norms from '../../engine/data/kg/index_norms.json' with { type: 'json' };
import { computeIndices, INDICES_VERSION, type IndexNorms, type Indices } from './indices.ts';
import { reasonMenh, REASONER_VERSION, type ReadingPlan } from './reason/plan.ts';
import type { Reading } from './reason/adjudicate.ts';
import type { SeatRef } from './reason/tiers.ts';
import { cacheKey, type KnowledgeStore, type OutputCache } from './store.ts';
import type { ChartInput, Knowledge } from './types.ts';

export const OVERVIEW_VERSION = 'overview-2.0.0';
const NORMS = norms as IndexNorms;

export interface OverviewThesis {
  id: string; seat: string; label: string; score: number;
  claims: Array<{ concept: string; text: string; verdict: 'affirmed' | 'qualified' | 'contested'; soft: boolean;
    rules: Array<{ id: string; cite: string; role: 'base' | 'reducer' | 'against' }> }>;
  formations: Array<{ ruleId: string; name: string; cites: string[] }>;
}
export interface Overview {
  engine: string; reasoner: string; kbVersion: string; disclaimer: string;
  frame: { branch: string; vcd: boolean; borrowed: string[]; tuan: boolean; triet: boolean; than: boolean; centre: string;
    majors: Array<{ star: string; dignity?: string; hoa: string[] }>; formations: Array<{ ruleId: string; name: string; condition: string; cites: string[]; pol?: '+' | '-' }> } | null;
  theses: OverviewThesis[];
  indices: Indices;
}

/** A seat in words: "Cự Môn (hãm) ở Mệnh", "Hóa Lộc (trên Cự Môn)", "tam phương: Quan Lộc" … */
export function seatLabel(s: SeatRef, p: ReadingPlan): string {
  if (s.id === 'major:vcd') return 'Mệnh vô chính diệu';
  if (s.kind === 'major') {
    const d = p.frame.majors.find(m => m.star === s.star)?.dignity;
    return s.scope === 'opp' ? `${s.star} ở cung xung chiếu (Mệnh vô chính diệu mượn sao)` : `${s.star}${d ? ` (${d})` : ''} ở Mệnh`;
  }
  if (s.kind === 'hoa') return `${s.hoa}${s.star ? ` (trên ${s.star})` : ''}${s.palace && s.palace !== 'Mệnh' ? ` ở ${s.palace}` : ''}`;
  if (s.kind === 'star') return `${s.star} ở Mệnh`;
  if (s.kind === 'tuan_triet') return `${s.id.slice(3)} ở Mệnh`;
  if (s.kind === 'tam_phuong') return `tam phương: cung ${s.palace}`;
  return 'độ số của lá số (mùa, giờ, cục, can chi)';
}

export function overviewPlan(chart: ChartInput, k: Knowledge): Pick<Overview, 'frame' | 'theses'> {
  const p = reasonMenh(chart, k, undefined, { draftFormations: false });
  const cmap = new Map(k.concepts.concepts.map(c => [c.id, c]));
  const rules = (xs: Reading[], role: 'base' | 'reducer' | 'against') => xs.map(x => ({ id: x.r.ruleId, cite: x.r.cites.join('; '), role }));
  return {
    frame: { branch: p.frame.branch, vcd: p.frame.vcd, borrowed: p.frame.borrowed, tuan: p.frame.tuan, triet: p.frame.triet, than: p.frame.than,
      centre: seatLabel(p.frame.centre.seat, p), majors: p.frame.majors,
      formations: p.frame.formations.filter(f => f.kind === 'formation').map(f => ({ ruleId: f.ruleId, name: f.name, condition: f.condition, cites: f.cites, pol: f.pol })) },
    theses: p.theses.map(t => ({
      id: t.id, seat: t.seat.id, label: seatLabel(t.seat, p), score: t.score,
      claims: t.claims.map(c => ({ concept: c.concept, text: cmap.get(c.concept)?.np ?? c.concept, verdict: c.axis.verdict, soft: c.soft,
        rules: [...rules(c.axis.base, 'base'), ...rules(c.axis.reducers, 'reducer'), ...rules(c.axis.against, 'against')] })),
      formations: t.formations.filter(f => f.kind === 'formation').map(f => ({ ruleId: f.ruleId, name: f.name, cites: f.cites })),
    })),
  };
}

/** The whole overview for one chart. The reasoner reads Mệnh only; if it cannot (malformed facts), the charts still come back. */
export function overview(chart: ChartInput, k: Knowledge, n: IndexNorms | null = NORMS): Overview {
  let plan: Pick<Overview, 'frame' | 'theses'> = { frame: null, theses: [] };
  try { plan = overviewPlan(chart, k); } catch { /* the indices stand on their own */ }
  const indices = computeIndices(chart, k, n);
  return { engine: OVERVIEW_VERSION, reasoner: REASONER_VERSION, kbVersion: k.version, disclaimer: indices.disclaimer, ...plan, indices };
}

export interface OverviewDeps {
  enabled: boolean;                                         // TVBT_INTERPRET === "1" (the same switch as /api/interpret)
  facts: (birth: Record<string, unknown>) => Promise<Response>;
  store: KnowledgeStore; cache?: OutputCache; defer?: (p: Promise<unknown>) => void;
}
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json; charset=utf-8' } });

export async function handleOverview(request: Request, d: OverviewDeps): Promise<Response> {
  if (!d.enabled) return json({ detail: 'overview is disabled' }, 404);
  if (request.method !== 'POST') return json({ detail: 'POST a birth record' }, 405);
  const birth = await request.json().catch(() => null) as Record<string, unknown> | null;
  if (!birth) return json({ detail: 'invalid JSON' }, 400);
  const factsRes = await d.facts(birth);
  if (!factsRes.ok) return new Response(factsRes.body, { status: factsRes.status, headers: factsRes.headers });
  const facts = await factsRes.json() as ChartInput;
  const k = await d.store.load();
  const key = await cacheKey([facts.base, facts.decades, facts.year, 'overview', OVERVIEW_VERSION, INDICES_VERSION, REASONER_VERSION, k.version, NORMS.kbVersion, NORMS.version]);
  const hit = await d.cache?.get(key);
  if (hit) return new Response(hit, { headers: { 'content-type': 'application/json; charset=utf-8', 'x-overview-cache': 'hit' } });
  const text = JSON.stringify(overview(facts, k));
  if (d.cache && d.defer) d.defer(d.cache.put(key, 'overview', text, { engine: OVERVIEW_VERSION, kb: k.version, pass: true }));
  return new Response(text, { headers: { 'content-type': 'application/json; charset=utf-8', 'x-overview-cache': 'miss' } });
}
