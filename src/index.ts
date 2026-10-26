import { Container, getContainer } from "@cloudflare/containers";
import knowledge from "./interpret/generated/knowledge.json" with { type: "json" };
import { handleAuth, isAuthPath, type AuthEnv } from "./auth/route.ts";
import { handleAccount, isAccountPath } from "./account/route.ts";
import { handleHorary, isHoraryPath } from "./horary/route.ts";
import { currentUser } from "./auth/session.ts";
import { bump, handleStats } from "./stats/stats.ts";
import { handleChat } from "./chat/route.ts";
import { handleFeedback, isFeedbackPath } from "./feedback/route.ts";
import { handleAdmin, isAdmin, isAdminPath, type AdminEnv } from "./admin/route.ts";
import { handleReferral, isReferralPath } from "./referral/route.ts";
import { handleTarot, isTarotPath } from "./tarot/route.ts";
import { handleDeep, handleDeepStatus } from "./chat/deep.ts";
import { handleBilling, isBillingPath, paywallOn, type BillingEnv } from "./billing/route.ts";
import { gated as gatedRoute } from "./billing/paywall.ts";
import { anthropicLlm, CHAT_OPTIONS, DEEP_OPTIONS, type LlmOptions } from "./chat/llm.ts";
import { handleInterpret } from "./interpret/route.ts";
import { handleOverview } from "./interpret/overview.ts";
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
  CF_VERSION_METADATA?: { id: string };   // deploy version id (wrangler version_metadata); keys the interpretation cache
  TVBT_INTERPRET?: string;          // "1" enables /api/interpret (default off: the route answers 404)
  TVBT_PROSE_DRAFT?: string;        // "1" lets mode "prose" use prose cards that are still drafts (default: approved cards only)
  TVBT_TAROT?: string;              // "1" turns on the Tarot API (src/tarot/route.ts); off (default), its paths answer 404
  TVBT_LUAN?: string;               // "0" turns off the luận cung chapters (prose/luan.ts) in the whole-report prose; on unless set to "0"
  INTERPRET_DB?: D1Like;            // optional D1 knowledge base + output cache (migrations/interpret)
  INTERPRET_CACHE?: R2Like;         // optional R2 bucket for cached outputs
}

/** TVBT_PAYWALL=1: every reading leaves the Worker cut to the reader's tier (src/billing/paywall.ts): guest, member, Đọc sâu opened. The cut
 *  runs on the finished response, after the cache, so the cache never holds a per-reader copy. A share link's viewer reads at the guest tier. */
const gated = (request: Request, env: Env, path: string, shared: boolean, run: (r: Request) => Promise<Response>) =>
  gatedRoute(request, { db: env.DB, paywall: paywallOn(env), path, shared, isAdmin: u => isAdmin(env, u) }, run);

async function interpretRoute(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
  return handleInterpret(request, {
    enabled: env.TVBT_INTERPRET === "1", proseDraft: env.TVBT_PROSE_DRAFT === "1", luan: env.TVBT_LUAN !== "0",
    facts: birth => getContainer(env.TVBT, "main").fetch(new Request(new URL("/api/facts", request.url), {
      method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(birth) })),
    store: env.INTERPRET_DB ? new D1Store(env.INTERPRET_DB, knowledge as unknown as Knowledge) : new BundledStore(knowledge as unknown as Knowledge),
    cache: new LayeredCache({ db: env.INTERPRET_DB, r2: env.INTERPRET_CACHE, edge: (globalThis as any).caches?.default }),
    defer: p => ctx.waitUntil(p), codeRev: env.CF_VERSION_METADATA?.id,
  });
}

// "Tổng quan lá số": reasoner frame + system indices for the charts (src/interpret/overview.ts), on the same switch as /api/interpret
async function overviewRoute(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
  return handleOverview(request, {
    enabled: env.TVBT_INTERPRET === "1",
    facts: birth => getContainer(env.TVBT, "main").fetch(new Request(new URL("/api/facts", request.url), {
      method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(birth) })),
    store: env.INTERPRET_DB ? new D1Store(env.INTERPRET_DB, knowledge as unknown as Knowledge) : new BundledStore(knowledge as unknown as Knowledge),
    cache: new LayeredCache({ db: env.INTERPRET_DB, r2: env.INTERPRET_CACHE, edge: (globalThis as any).caches?.default }),
    defer: p => ctx.waitUntil(p), codeRev: env.CF_VERSION_METADATA?.id,
  });
}

async function chatRoute(request: Request, env: Env, ctx: ExecutionContext, deep: boolean): Promise<Response> {
  const user = env.DB ? await currentUser(env.DB, request) : null;
  if (!env.DB || (!user && deep)) return new Response(JSON.stringify({ detail: "sign in required" }), { status: 401, headers: { "content-type": "application/json" } });
  const deps = {
    db: env.DB, knowledge: knowledge as unknown as Knowledge, unlimited: isAdmin(env, user),
    llm: env.ANTHROPIC_API_KEY ? anthropicLlm(env.ANTHROPIC_API_KEY, deep ? DEEP_OPTIONS : CHAT_OPTIONS) : null,
    facts: (birth: Record<string, unknown>) => getContainer(env.TVBT, "main").fetch(new Request(new URL("/api/facts", request.url), {
      method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(birth) })),
  };
  // a guest reaches handleChat, which answers 401 itself (the panel opens for anyone; sending needs sign-in)
  const key = env.ANTHROPIC_API_KEY, llmFor = key ? (o: LlmOptions) => anthropicLlm(key, o) : undefined;   // one client per Luận riêng level and step
  return deep && user ? handleDeep(request, { ...deps, user, llmFor, defer: p => ctx.waitUntil(p) }) : handleChat(request, { ...deps, user });
}

// A shared chart is computed from the birth stored with it: the engine call is built here, never from the viewer's body alone. Its readings
// are cut at the guest tier, labelled as a share (the viewer may be signed in, but the chart is not theirs).
const shareForward = (request: Request, env: Env, ctx: ExecutionContext) => (path: string, body: Record<string, unknown>) => {
  const req = new Request(new URL(path, request.url), { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
  return gated(req, env, path, true, r => path === "/api/interpret" ? interpretRoute(r, env, ctx) : getContainer(env.TVBT, "main").fetch(r));
};

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const path = new URL(request.url).pathname;
    if (path === "/api/stats") return handleStats(env.DB);
    if (isBillingPath(path)) return handleBilling(request, env, env.DB ? await currentUser(env.DB, request) : null);
    // Tarot (/api/tarot/*, /api/me/tarot): before the /api/me/* account routes and the container forward
    if (isTarotPath(path)) {
      const on = env.TVBT_TAROT === "1";
      return handleTarot(request, { db: env.DB, enabled: on, user: on && env.DB ? await currentUser(env.DB, request) : null });
    }
    if (path === "/api/me/chat") return chatRoute(request, env, ctx, false);
    if (path === "/api/me/deep") return chatRoute(request, env, ctx, true);
    if (path === "/api/me/deep/status") {
      const user = env.DB ? await currentUser(env.DB, request) : null;
      return env.DB && user ? handleDeepStatus(request, { db: env.DB, user, admin: isAdmin(env, user) }) : new Response(JSON.stringify({ detail: "sign in required" }), { status: 401, headers: { "content-type": "application/json" } });
    }
    if (isFeedbackPath(path)) return handleFeedback(request, env.DB, env.DB ? await currentUser(env.DB, request) : null);
    if (isReferralPath(path)) return handleReferral(request, env.DB, env.DB ? await currentUser(env.DB, request) : null);
    if (isAdminPath(path)) return handleAdmin(request, env, env.DB ? await currentUser(env.DB, request) : null);
    if (isHoraryPath(path)) return handleHorary(request, env.DB);
    if (isAccountPath(path)) return handleAccount(request, env.DB, shareForward(request, env, ctx));
    if (isAuthPath(path)) return handleAuth(request, env);
    if (path === "/api/interpret") return gated(request, env, path, false, r => interpretRoute(r, env, ctx));
    if (path === "/api/overview") return gated(request, env, path, false, r => overviewRoute(r, env, ctx));
    // the engine's own reading layers (behind TVBT_DEEP_INTERPRETATION in the container): cut like the rest
    if (path === "/api/synthesis" || path === "/api/interpretation") return gated(request, env, path, false, r => getContainer(env.TVBT, "main").fetch(r));
    // Kinh Dịch / Mai Hoa readings: the main reading for everyone, Đọc sâu for a member who holds a paid package (paywall.ts gateCast)
    if (path === "/api/kinh-dich/reading" || path === "/api/mai-hoa/reading") return gated(request, env, path, false, r => getContainer(env.TVBT, "main").fetch(r));
    // the Western reading: part of it is paid (src/billing/west.ts); the chart and forecast data are not cut
    if (path === "/api/west/reading") return gated(request, env, path, false, r => getContainer(env.TVBT, "main").fetch(r));
    // The container API is stateless and stores nothing (accounts live in the Worker, above), so one shared instance is enough.
    const res = await getContainer(env.TVBT, "main").fetch(request);
    // one more chart scan, counted only when the engine really produced the chart
    if (request.method === "POST" && path === "/api/chart" && res.ok && env.DB) ctx.waitUntil(bump(env.DB, "scans"));
    return res;
  },
};
