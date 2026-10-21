import { Container, getContainer } from "@cloudflare/containers";
import knowledge from "./interpret/generated/knowledge.json" with { type: "json" };
import { handleAuth, isAuthPath, type AuthEnv } from "./auth/route.ts";
import { currentUser } from "./auth/session.ts";
import { bump, handleStats } from "./stats/stats.ts";
import { handleChat } from "./chat/route.ts";
import { handleFeedback, isFeedbackPath } from "./feedback/route.ts";
import { handleAdmin, isAdminPath, type AdminEnv } from "./admin/route.ts";
import { handleDeep } from "./chat/deep.ts";
import { handleBilling, isBillingPath, paywallOn, type BillingEnv } from "./billing/route.ts";
import { gateResponse } from "./billing/paywall.ts";
import { anthropicLlm, CHAT_OPTIONS, DEEP_OPTIONS } from "./chat/llm.ts";
import { handleInterpret } from "./interpret/route.ts";
import { BundledStore, D1Store, LayeredCache, type D1Like, type R2Like } from "./interpret/store.ts";
import type { Knowledge } from "./interpret/types.ts";

// The Python (FastAPI) engine runs inside the container; this Worker routes requests to it, and hosts the deterministic TypeScript
// interpretation pipeline (/api/interpret), which asks the container for chart facts only.
export class TvbtContainer extends Container {
  defaultPort = 8000;
  sleepAfter = "10m";
}

interface Env extends AuthEnv, BillingEnv, AdminEnv {
  ANTHROPIC_API_KEY?: string;       // secret; without it /api/me/chat answers 503
  TVBT: DurableObjectNamespace<TvbtContainer>;
  TVBT_INTERPRET?: string;          // "1" enables /api/interpret (default off: the route answers 404)
  TVBT_PROSE_DRAFT?: string;        // "1" lets mode "prose" use prose cards that are still drafts (default: approved cards only)
  INTERPRET_DB?: D1Like;            // optional D1 knowledge base + output cache (migrations/interpret)
  INTERPRET_CACHE?: R2Like;         // optional R2 bucket for cached outputs
}

async function interpretRoute(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
  // TVBT_PAYWALL=1: paid chapters the reader has not opened leave the Worker as a short preview (src/billing/paywall.ts)
  const gate = paywallOn(env) && request.method === "POST";
  const body = gate ? await request.clone().json().catch(() => null) : null;
  const res = await handleInterpret(request, {
    enabled: env.TVBT_INTERPRET === "1", proseDraft: env.TVBT_PROSE_DRAFT === "1",
    facts: birth => getContainer(env.TVBT, "main").fetch(new Request(new URL("/api/facts", request.url), {
      method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(birth) })),
    store: env.INTERPRET_DB ? new D1Store(env.INTERPRET_DB, knowledge as unknown as Knowledge) : new BundledStore(knowledge as unknown as Knowledge),
    cache: new LayeredCache({ db: env.INTERPRET_DB, r2: env.INTERPRET_CACHE, edge: (globalThis as any).caches?.default }),
    defer: p => ctx.waitUntil(p),
  });
  return gate ? gateResponse(res, body, env.DB, env.DB ? await currentUser(env.DB, request) : null) : res;
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
    if (path === "/api/stats") return handleStats(env.DB);
    if (isBillingPath(path)) return handleBilling(request, env, env.DB ? await currentUser(env.DB, request) : null);
    if (path === "/api/me/chat") return chatRoute(request, env, ctx, false);
    if (path === "/api/me/deep") return chatRoute(request, env, ctx, true);
    if (isFeedbackPath(path)) return handleFeedback(request, env.DB, env.DB ? await currentUser(env.DB, request) : null);
    if (isAdminPath(path)) return handleAdmin(request, env, env.DB ? await currentUser(env.DB, request) : null);
    if (isAuthPath(path)) return handleAuth(request, env);
    if (path === "/api/interpret") return interpretRoute(request, env, ctx);
    // The container API is stateless and stores nothing (accounts live in the Worker, above), so one shared instance is enough.
    const res = await getContainer(env.TVBT, "main").fetch(request);
    // one more chart scan, counted only when the engine really produced the chart
    if (request.method === "POST" && path === "/api/chart" && res.ok && env.DB) ctx.waitUntil(bump(env.DB, "scans"));
    return res;
  },
};
