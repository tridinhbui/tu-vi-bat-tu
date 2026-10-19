import { Container, getContainer } from "@cloudflare/containers";
import knowledge from "./interpret/generated/knowledge.json" with { type: "json" };
import { handleInterpret } from "./interpret/route.ts";
import { BundledStore, D1Store, LayeredCache, type D1Like, type R2Like } from "./interpret/store.ts";
import type { Knowledge } from "./interpret/types.ts";

// The Python (FastAPI) engine runs inside the container; this Worker routes requests to it, and hosts the deterministic TypeScript
// interpretation pipeline (/api/interpret), which asks the container for chart facts only.
export class TvbtContainer extends Container {
  defaultPort = 8000;
  sleepAfter = "10m";
}

interface Env {
  TVBT: DurableObjectNamespace<TvbtContainer>;
  TVBT_INTERPRET?: string;          // "1" enables /api/interpret (default off: the route answers 404)
  TVBT_PROSE_DRAFT?: string;        // "1" lets mode "prose" use prose cards that are still drafts (default: approved cards only)
  INTERPRET_DB?: D1Like;            // optional D1 knowledge base + output cache (migrations/interpret)
  INTERPRET_CACHE?: R2Like;         // optional R2 bucket for cached outputs
}

async function interpretRoute(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
  return handleInterpret(request, {
    enabled: env.TVBT_INTERPRET === "1", proseDraft: env.TVBT_PROSE_DRAFT === "1",
    facts: birth => getContainer(env.TVBT, "main").fetch(new Request(new URL("/api/facts", request.url), {
      method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(birth) })),
    store: env.INTERPRET_DB ? new D1Store(env.INTERPRET_DB, knowledge as unknown as Knowledge) : new BundledStore(knowledge as unknown as Knowledge),
    cache: new LayeredCache({ db: env.INTERPRET_DB, r2: env.INTERPRET_CACHE, edge: (globalThis as any).caches?.default }),
    defer: p => ctx.waitUntil(p),
  });
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    if (new URL(request.url).pathname === "/api/interpret") return interpretRoute(request, env, ctx);
    // The rest of the API is stateless and nothing is stored, so one shared instance is enough.
    return getContainer(env.TVBT, "main").fetch(request);
  },
};
