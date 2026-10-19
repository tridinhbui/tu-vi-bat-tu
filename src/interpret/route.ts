// POST /api/interpret, shared by the Worker (src/index.ts, facts from the Python container) and the local dev server
// (tools/interpret/dev_server.ts, facts from a local uvicorn), so a local check exercises the same code the Worker runs.
import { interpret, CHAPTERS, ENGINE_VERSION, type Chapter } from './pipeline.ts';
import { proseChapter, proseReport, PROSE_ORDER, PROSE_VERSION, type ProseChapterId } from './prose/chapter.ts';
import { cacheKey, type KnowledgeStore, type OutputCache } from './store.ts';
import type { ChartInput } from './types.ts';

export interface InterpretDeps {
  enabled: boolean;                                         // TVBT_INTERPRET === "1"
  proseDraft: boolean;                                      // TVBT_PROSE_DRAFT === "1": mode "prose" may use draft cards
  facts: (birth: Record<string, unknown>) => Promise<Response>;
  store: KnowledgeStore; cache: OutputCache; defer: (p: Promise<unknown>) => void;
}

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json; charset=utf-8' } });

export async function handleInterpret(request: Request, d: InterpretDeps): Promise<Response> {
  if (!d.enabled) return json({ detail: 'interpretation pipeline is disabled' }, 404);
  if (request.method !== 'POST') return json({ detail: 'POST a birth record' }, 405);
  const body = await request.json().catch(() => null) as Record<string, unknown> | null;
  if (!body) return json({ detail: 'invalid JSON' }, 400);
  const chapter = (body.chapter ?? 'cong_danh') as Chapter;
  // mode "prose": reader prose (src/interpret/prose) for the chapters it covers so far; default "evidence" keeps the v2 evidence report
  const mode = body.mode === 'prose' ? 'prose' : 'evidence';
  if (mode === 'evidence' && !CHAPTERS.includes(chapter)) return json({ detail: `chapter must be one of ${CHAPTERS.join(', ')}` }, 422);
  // chapter "all" in prose mode returns the whole chained report in one response (the report page asks for it this way)
  if (mode === 'prose' && chapter !== ('all' as Chapter) && !PROSE_ORDER.includes(chapter as ProseChapterId)) return json({ detail: `mode "prose" is available for chapters ${PROSE_ORDER.join(', ')} or "all"` }, 422);
  const { chapter: _c, mode: _m, ...birth } = body;
  const factsRes = await d.facts(birth);
  if (!factsRes.ok) return new Response(factsRes.body, { status: factsRes.status, headers: factsRes.headers });
  const facts = await factsRes.json() as ChartInput;
  const k = await d.store.load();
  // the Bát Tự chapter reads facts.bazi (pillars, luck), the others the Tử Vi facts; both go into the key so no chapter can hit a stale entry
  const key = await cacheKey([facts.base, facts.decades, facts.year, facts.bazi ?? null, chapter, ENGINE_VERSION, k.version, mode, mode === 'prose' ? [PROSE_VERSION, d.proseDraft] : null]);
  const hit = await d.cache.get(key);
  if (hit) return new Response(hit, { headers: { 'content-type': 'application/json; charset=utf-8', 'x-interpret-cache': 'hit' } });
  const out = mode !== 'prose' ? interpret(facts, chapter, k)
    : chapter === ('all' as Chapter) ? (cs => ({ engine: PROSE_VERSION, kbVersion: k.version, chapters: cs, pass: cs.every(c => c.pass) }))(proseReport(facts, k, { allowDraft: d.proseDraft }))
    : proseChapter(facts, k, chapter as ProseChapterId, { allowDraft: d.proseDraft });
  const text = JSON.stringify(out);
  const pass = 'quality' in out ? out.quality.pass : out.pass;
  d.defer(d.cache.put(key, chapter, text, { engine: mode === 'prose' ? PROSE_VERSION : ENGINE_VERSION, kb: k.version, pass }));
  return new Response(text, { headers: { 'content-type': 'application/json; charset=utf-8', 'x-interpret-cache': 'miss' } });
}
