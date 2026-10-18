// Knowledge and output storage. The same pipeline runs against:
//   - BundledStore: knowledge.json shipped inside the Worker (no binding needed; what runs today)
//   - D1Store:      the relational knowledge base (migrations/interpret), when an INTERPRET_DB binding exists
// Outputs are cached by a content hash of (chart facts, chapter, engine version, knowledge version): in D1 `interpretations`, in R2 under
// interpretations/<key>.json when an INTERPRET_CACHE bucket is bound, otherwise in the Workers Cache API.
import type { ContentModule, Knowledge, Rule } from './types.ts';

/** Minimal D1 surface (structurally compatible with Cloudflare's D1Database and with the node:sqlite adapter used in tests). */
export interface D1Like {
  prepare(sql: string): { bind(...v: unknown[]): { all<T = Record<string, unknown>>(): Promise<{ results: T[] }>; first<T = Record<string, unknown>>(): Promise<T | null>; run(): Promise<unknown> };
    all<T = Record<string, unknown>>(): Promise<{ results: T[] }> };
}
export interface R2Like { get(key: string): Promise<{ text(): Promise<string> } | null>; put(key: string, value: string, opts?: unknown): Promise<unknown> }

export interface KnowledgeStore { load(): Promise<Knowledge> }

export class BundledStore implements KnowledgeStore {
  private k: Knowledge;
  constructor(k: Knowledge) { this.k = k; }
  async load() { return this.k; }
}

const J = <T>(s: unknown, d: T): T => (typeof s === 'string' && s ? JSON.parse(s) : d);

/** Reads the knowledge base from D1. Static parts that are not relational (ontology, star profiles, frames) come from the bundle. */
export class D1Store implements KnowledgeStore {
  private db: D1Like; private bundle: Knowledge; private cache: Knowledge | null = null;
  constructor(db: D1Like, bundle: Knowledge) { this.db = db; this.bundle = bundle; }
  async load(): Promise<Knowledge> {
    if (this.cache) return this.cache;
    const q = async <T>(sql: string) => (await this.db.prepare(sql).all<T>()).results;
    const version = (await q<{ value: string }>("SELECT value FROM kb_meta WHERE key = 'version'"))[0]?.value ?? 'd1';
    const sources = (await q<any>('SELECT * FROM sources')).map(s => ({ id: s.id, title: s.title, author: s.author, locator: s.locator, verified: !!s.verified }));
    const rules: Rule[] = (await q<any>('SELECT * FROM rules ORDER BY id')).map(r => ({
      id: r.id, system: r.system, school: r.school, category: r.category, subject: r.subject, priority: r.priority,
      conditions: J(r.conditions_json, {} as any), consequences: J(r.consequences_json, []), exceptions: J(r.exceptions_json, []),
      sourceIds: J(r.source_ids_json, []), reviewStatus: r.review_status, cites: J(r.cites_json, []), reading: r.reading }));
    const claims = Object.fromEntries((await q<any>('SELECT id, label FROM claims')).map(c => [c.id, c.label]));
    const concepts = (await q<any>('SELECT * FROM concepts')).map(c => ({ id: c.id, facet: c.facet, pol: c.pol, kind: c.kind, opp: c.opp ?? undefined, cues: J(c.cues_json, []), np: c.np, short: c.short ?? undefined }));
    const relations = (await q<any>('SELECT * FROM concept_relations')).map(r => ({ a: r.a, b: r.b, type: r.type, frame: r.frame ?? undefined, synth: r.synth ?? undefined }));
    const passages = await q<any>('SELECT * FROM module_passages ORDER BY module_id, ord');
    const modules: ContentModule[] = (await q<any>("SELECT * FROM content_modules WHERE status != 'retired'")).map(m => {
      const b = this.bundle.modules.find(x => x.id === m.id);
      return { id: m.id, chapter: m.chapter, role: m.role, version: m.version, status: m.status, title: m.title, order: b?.order ?? 50,
        when: J(m.when_json, undefined), evidence: J(m.evidence_json, undefined), author: m.author ?? undefined,
        passages: passages.filter(p => p.module_id === m.id).map(p => ({ id: p.passage_id, when: J(p.when_json, undefined), basis: p.basis, kind: p.kind,
          variants: J(p.variants_json, []), cites: J(p.cites_json, []), each: b?.passages.find(x => x.id === p.passage_id)?.each,
          followups: b?.passages.find(x => x.id === p.passage_id)?.followups })) };
    });
    this.cache = { ...this.bundle, version, sources, rules, claims, concepts: { ...this.bundle.concepts, concepts }, relations: { ...this.bundle.relations, relations }, modules };
    return this.cache;
  }
}

export async function cacheKey(parts: unknown[]): Promise<string> {
  const data = new TextEncoder().encode(JSON.stringify(parts));
  const digest = await crypto.subtle.digest('SHA-256', data);
  return [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('').slice(0, 40);
}

export interface OutputCache { get(key: string): Promise<string | null>; put(key: string, chapter: string, body: string, meta: { engine: string; kb: string; pass: boolean }): Promise<void> }

export class LayeredCache implements OutputCache {
  private db?: D1Like; private r2?: R2Like; private edge?: Cache;
  constructor(opts: { db?: D1Like; r2?: R2Like; edge?: Cache }) { this.db = opts.db; this.r2 = opts.r2; this.edge = opts.edge; }
  async get(key: string): Promise<string | null> {
    if (this.r2) { const o = await this.r2.get(`interpretations/${key}.json`); if (o) return o.text(); }
    if (this.db) { const row = await this.db.prepare('SELECT output_json FROM interpretations WHERE cache_key = ?').bind(key).first<{ output_json: string | null }>(); if (row?.output_json) return row.output_json; }
    if (this.edge) { const r = await this.edge.match(new Request(`https://interpret.cache/${key}`)); if (r) return r.text(); }
    return null;
  }
  async put(key: string, chapter: string, body: string, meta: { engine: string; kb: string; pass: boolean }) {
    if (this.r2) await this.r2.put(`interpretations/${key}.json`, body, { httpMetadata: { contentType: 'application/json' } });
    if (this.db) await this.db.prepare('INSERT OR REPLACE INTO interpretations (cache_key, chapter, engine_version, kb_version, output_json, r2_key, quality_pass) VALUES (?, ?, ?, ?, ?, ?, ?)')
      .bind(key, chapter, meta.engine, meta.kb, this.r2 ? null : body, this.r2 ? `interpretations/${key}.json` : null, meta.pass ? 1 : 0).run();
    if (this.edge) await this.edge.put(new Request(`https://interpret.cache/${key}`), new Response(body, { headers: { 'content-type': 'application/json', 'cache-control': 'max-age=2592000' } }));
  }
}
