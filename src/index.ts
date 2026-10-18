import { Container, getContainer } from "@cloudflare/containers";
import knowledge from "./interpret/generated/knowledge.json" with { type: "json" };
import { interpret, CHAPTERS, ENGINE_VERSION, type Chapter } from "./interpret/pipeline.ts";
import { BundledStore, D1Store, LayeredCache, cacheKey, type D1Like, type R2Like } from "./interpret/store.ts";
import type { ChartInput, Knowledge } from "./interpret/types.ts";

// The Python (FastAPI) engine runs inside the container; this Worker routes requests to it, and hosts the deterministic TypeScript
// interpretation pipeline (/api/interpret), which asks the container for chart facts only.
export class TvbtContainer extends Container {
  defaultPort = 8000;
  sleepAfter = "10m";
}

interface Env {
  TVBT: DurableObjectNamespace<TvbtContainer>;
  TVBT_INTERPRET?: string;          // "1" enables /api/interpret (default off: the route answers 404)
  INTERPRET_DB?: D1Like;            // optional D1 knowledge base + output cache (migrations/interpret)
  INTERPRET_CACHE?: R2Like;         // optional R2 bucket for cached outputs
}

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8" } });

async function interpretRoute(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
  if (env.TVBT_INTERPRET !== "1") return json({ detail: "interpretation pipeline is disabled" }, 404);
  if (request.method !== "POST") return json({ detail: "POST a birth record" }, 405);
  const body = await request.json().catch(() => null) as Record<string, unknown> | null;
  if (!body) return json({ detail: "invalid JSON" }, 400);
  const chapter = (body.chapter ?? "cong_danh") as Chapter;
  if (!CHAPTERS.includes(chapter)) return json({ detail: `chapter must be one of ${CHAPTERS.join(", ")}` }, 422);
  const { chapter: _c, ...birth } = body;
  const factsRes = await getContainer(env.TVBT, "main").fetch(new Request(new URL("/api/facts", request.url), {
    method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(birth) }));
  if (!factsRes.ok) return new Response(factsRes.body, { status: factsRes.status, headers: factsRes.headers });
  const facts = await factsRes.json() as ChartInput;
  const store = env.INTERPRET_DB ? new D1Store(env.INTERPRET_DB, knowledge as unknown as Knowledge) : new BundledStore(knowledge as unknown as Knowledge);
  const k = await store.load();
  const cache = new LayeredCache({ db: env.INTERPRET_DB, r2: env.INTERPRET_CACHE, edge: (globalThis as any).caches?.default });
  const key = await cacheKey([facts.base, facts.decades, facts.year, chapter, ENGINE_VERSION, k.version]);
  const hit = await cache.get(key);
  if (hit) return new Response(hit, { headers: { "content-type": "application/json; charset=utf-8", "x-interpret-cache": "hit" } });
  const out = interpret(facts, chapter, k);
  const text = JSON.stringify(out);
  ctx.waitUntil(cache.put(key, chapter, text, { engine: ENGINE_VERSION, kb: k.version, pass: out.quality.pass }));
  return new Response(text, { headers: { "content-type": "application/json; charset=utf-8", "x-interpret-cache": "miss" } });
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    if (new URL(request.url).pathname === "/api/interpret") return interpretRoute(request, env, ctx);
    // The rest of the API is stateless and nothing is stored, so one shared instance is enough.
    return getContainer(env.TVBT, "main").fetch(request);
  },
};
