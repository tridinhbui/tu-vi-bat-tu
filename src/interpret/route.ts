// POST /api/interpret, shared by the Worker (src/index.ts, facts from the Python container) and the local dev server
// (tools/interpret/dev_server.ts, facts from a local uvicorn), so a local check exercises the same code the Worker runs.
import { interpret, CHAPTERS, ENGINE_VERSION, type Chapter } from './pipeline.ts';
import { proseChapter, proseReport, seedOf, PROSE_ORDER, PROSE_VERSION, type ProseChapterId } from './prose/chapter.ts';
import { proseVanHan } from './prose/vanhan.ts';
import { proseBazi } from './prose/bazi.ts';
import { proseThemes } from './prose/themes.ts';
import { luanReport, LUAN_VERSION } from './prose/luan.ts';
import { checkedOnly } from './prose/checked.ts';
import { reasonedChapter, NARRATIVE_VERSION } from './prose/narrative.ts';
import { planView } from './reason/plan.ts';
import { cacheKey, type KnowledgeStore, type OutputCache } from './store.ts';
import type { ChartInput } from './types.ts';

export interface InterpretDeps {
  enabled: boolean;                                         // TVBT_INTERPRET === "1"
  proseDraft: boolean;                                      // TVBT_PROSE_DRAFT === "1": mode "prose" may use draft cards
  reasoner?: boolean;                                       // TVBT_REASONER === "1": mode "reasoned" (Mệnh only, plan quirky-tinkering-rabin); off unless set
  /** prose mode: the structure, common-meaning and balance layers around the book readings (prose/deep.ts); on unless set false */
  deep?: boolean;
  /** prose mode: the palace chapters in the luận cung form (prose/luan.ts), the older chapter where a palace has nothing to argue; on unless false */
  luan?: boolean;
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
  const mode = body.mode === 'prose' ? 'prose' : body.mode === 'reasoned' ? 'reasoned' : 'evidence';
  // mode "reasoned": the Interpretation Reasoner's plan and the prose argued from it, for the Mệnh chapter only, behind its own flag
  if (mode === 'reasoned' && !d.reasoner) return json({ detail: 'reasoned mode is disabled' }, 404);
  if (mode === 'reasoned' && chapter !== ('menh' as Chapter)) return json({ detail: 'mode "reasoned" is available for chapter menh only' }, 422);
  if (mode === 'evidence' && !CHAPTERS.includes(chapter)) return json({ detail: `chapter must be one of ${CHAPTERS.join(', ')}` }, 422);
  // chapter "all" in prose mode returns the whole chained report in one response (the report page asks for it this way)
  if (mode === 'prose' && chapter !== ('all' as Chapter) && chapter !== ('van_han' as Chapter) && chapter !== ('bat_tu' as Chapter) && !PROSE_ORDER.includes(chapter as ProseChapterId)) return json({ detail: `mode "prose" is available for chapters ${PROSE_ORDER.join(', ')}, van_han, bat_tu or "all"` }, 422);
  const { chapter: _c, mode: _m, ...birth } = body;
  const factsRes = await d.facts(birth);
  if (!factsRes.ok) return new Response(factsRes.body, { status: factsRes.status, headers: factsRes.headers });
  const facts = await factsRes.json() as ChartInput;
  const k = await d.store.load();
  // the Bát Tự chapter reads facts.bazi (pillars, luck), the others the Tử Vi facts; both go into the key so no chapter can hit a stale entry
  const key = await cacheKey([facts.base, facts.decades, facts.year, facts.bazi ?? null, chapter, ENGINE_VERSION, k.version, mode, mode === 'prose' ? [PROSE_VERSION, d.proseDraft, d.deep !== false, d.luan !== false ? LUAN_VERSION : null, 'checked'] : mode === 'reasoned' ? [NARRATIVE_VERSION, d.proseDraft] : null]);
  const hit = await d.cache.get(key);
  if (hit) return new Response(hit, { headers: { 'content-type': 'application/json; charset=utf-8', 'x-interpret-cache': 'hit' } });
  const luan = d.luan !== false;
  const palaces = (o: { allowDraft: boolean; deep: boolean }) => luan ? luanReport(facts, k, o) : proseReport(facts, k, o);
  const out0 = mode === 'reasoned' ? (o => ({ ...o, plan: planView(o.plan) }))(reasonedChapter(facts, k, { allowDraft: d.proseDraft }))
    : mode !== 'prose' ? interpret(facts, chapter, k)
    : chapter === ('all' as Chapter) ? (cs => ({ engine: PROSE_VERSION, kbVersion: k.version, chapters: cs, pass: cs.every(c => c.pass) }))(
        [...proseThemes(facts, k, PROSE_VERSION, { allowDraft: d.proseDraft, luan }), ...palaces({ allowDraft: d.proseDraft, deep: d.deep !== false }), proseVanHan(facts, k, seedOf(facts), PROSE_VERSION, d.proseDraft), proseBazi(facts, k, seedOf(facts), PROSE_VERSION, d.proseDraft)])
    : chapter === ('van_han' as Chapter) ? proseVanHan(facts, k, seedOf(facts), PROSE_VERSION, d.proseDraft)
    : chapter === ('bat_tu' as Chapter) ? proseBazi(facts, k, seedOf(facts), PROSE_VERSION, d.proseDraft)
    : luan ? palaces({ allowDraft: d.proseDraft, deep: d.deep !== false }).find(c => c.chapter === chapter)!
    : proseChapter(facts, k, chapter as ProseChapterId, { allowDraft: d.proseDraft, deep: d.deep !== false });
  // only checked readings reach the reader: the phổ thông sentences are removed from every prose output (prose/checked.ts)
  type Checkable = Parameters<typeof checkedOnly>[0];
  const out = (mode !== 'prose' ? out0 : 'chapters' in out0 && Array.isArray(out0.chapters)
    ? { ...out0, chapters: out0.chapters.map(c => checkedOnly(c as Checkable)) } : checkedOnly(out0 as Checkable)) as typeof out0;
  const text = JSON.stringify(out);
  const pass = 'quality' in out ? out.quality.pass : out.pass;
  d.defer(d.cache.put(key, chapter, text, { engine: mode === 'prose' ? PROSE_VERSION : mode === 'reasoned' ? NARRATIVE_VERSION : ENGINE_VERSION, kb: k.version, pass }));
  return new Response(text, { headers: { 'content-type': 'application/json; charset=utf-8', 'x-interpret-cache': 'miss' } });
}
