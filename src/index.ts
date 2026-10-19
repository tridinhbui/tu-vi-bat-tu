import { Container, getContainer } from "@cloudflare/containers";
import knowledge from "./interpret/generated/knowledge.json" with { type: "json" };
import { handleAuth, isAuthPath, type AuthEnv } from "./auth/route.ts";
import { currentUser } from "./auth/session.ts";
import { handleChat } from "./chat/route.ts";
import { handleDeep } from "./chat/deep.ts";
import { anthropicLlm, CHAT_OPTIONS, DEEP_OPTIONS } from "./chat/llm.ts";
import { interpret, CHAPTERS, ENGINE_VERSION, type Chapter } from "./interpret/pipeline.ts";
import { BundledStore, D1Store, LayeredCache, cacheKey, type D1Like, type R2Like } from "./interpret/store.ts";
import type { ChartInput, Knowledge } from "./interpret/types.ts";

// The Python (FastAPI) engine runs inside the container; this Worker routes requests to it, and hosts the deterministic TypeScript
// interpretation pipeline (/api/interpret), which asks the container for chart facts only.
export class TvbtContainer extends Container {
  defaultPort = 8000;
  sleepAfter = "10m";
}

interface Env extends AuthEnv {
  ANTHROPIC_API_KEY?: string;       // secret; without it /api/me/chat answers 503
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
  // the Bát Tự chapter reads facts.bazi (pillars, luck), the others the Tử Vi facts; both go into the key so no chapter can hit a stale entry
  const key = await cacheKey([facts.base, facts.decades, facts.year, facts.bazi ?? null, chapter, ENGINE_VERSION, k.version]);
  const hit = await cache.get(key);
  if (hit) return new Response(hit, { headers: { "content-type": "application/json; charset=utf-8", "x-interpret-cache": "hit" } });
  const out = interpret(facts, chapter, k);
  const text = JSON.stringify(out);
  ctx.waitUntil(cache.put(key, chapter, text, { engine: ENGINE_VERSION, kb: k.version, pass: out.quality.pass }));
  return new Response(text, { headers: { "content-type": "application/json; charset=utf-8", "x-interpret-cache": "miss" } });
}

async function chatRoute(request: Request, env: Env, ctx: ExecutionContext, deep: boolean): Promise<Response> {
  const user = env.DB ? await currentUser(env.DB, request) : null;
  if (!env.DB || !user) return new Response(JSON.stringify({ detail: "sign in required" }), { status: 401, headers: { "content-type": "application/json" } });
  const deps = {
    db: env.DB, user, knowledge: knowledge as unknown as Knowledge,
    llm: env.ANTHROPIC_API_KEY ? anthropicLlm(env.ANTHROPIC_API_KEY, deep ? DEEP_OPTIONS : CHAT_OPTIONS) : null,
    facts: (birth: Record<string, unknown>) => getContainer(env.TVBT, "main").fetch(new Request(new URL("/api/facts", request.url), {
      method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(birth) })),
  };
  return deep ? handleDeep(request, { ...deps, defer: p => ctx.waitUntil(p) }) : handleChat(request, deps);
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const path = new URL(request.url).pathname;
    if (path === "/api/me/chat") return chatRoute(request, env, ctx, false);
    if (path === "/api/me/deep") return chatRoute(request, env, ctx, true);
    if (isAuthPath(path)) return handleAuth(request, env);
    if (path === "/api/interpret") return interpretRoute(request, env, ctx);
    // The container API is stateless and stores nothing (accounts live in the Worker, above), so one shared instance is enough.
    return getContainer(env.TVBT, "main").fetch(request);
  },
};
