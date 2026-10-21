// /api/auth/* (Google sign-in) and /api/me/* (the signed-in user's data).
import { authUrl, exchangeCode, newState, type GoogleConfig } from "./google.ts";
import { COOKIE, createSession, currentUser, destroySession, randomToken, readCookie, setCookie } from "./session.ts";
import { deleteChart, listCharts, syncCharts } from "./charts.ts";
import { getWallet, grant } from "../billing/wallet.ts";
import { PACKS } from "../billing/config.ts";
import { bump } from "../stats/stats.ts";
import { isAdmin } from "../admin/route.ts";

export interface AuthEnv { DB?: D1Database; GOOGLE_CLIENT_ID?: string; GOOGLE_CLIENT_SECRET?: string; ADMIN_TOKEN?: string; ADMIN_EMAILS?: string; STRIPE_SECRET_KEY?: string }

const json = (body: unknown, status = 200, headers: HeadersInit = {}) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...headers } });
const redirect = (to: string, cookies: string[] = []) => {
  const h = new Headers({ location: to, "cache-control": "no-store" });
  for (const c of cookies) h.append("set-cookie", c);
  return new Response(null, { status: 302, headers: h });
};
const OAUTH_COOKIE = "tvbt_oauth";

// Compares through SHA-256 so the comparison does not leak where two secrets first differ.
async function sameSecret(a: string, b: string): Promise<boolean> {
  const [x, y] = await Promise.all([a, b].map(async v => new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(v)))));
  let d = 0; for (let i = 0; i < x.length; i++) d |= x[i] ^ y[i];
  return d === 0;
}

export const isAuthPath = (p: string) => p.startsWith("/api/auth/") || p.startsWith("/api/me/") || p.startsWith("/api/admin/");

export async function handleAuth(request: Request, env: AuthEnv): Promise<Response> {
  const url = new URL(request.url), path = url.pathname, db = env.DB;
  const cfg: GoogleConfig | null = env.GOOGLE_CLIENT_ID && env.GOOGLE_CLIENT_SECRET ? { clientId: env.GOOGLE_CLIENT_ID, clientSecret: env.GOOGLE_CLIENT_SECRET } : null;

  // The page asks this first; "enabled: false" keeps the sign-in button hidden until the database and Google keys are configured.
  if (path === "/api/auth/me") {
    if (!db || !cfg) return json({ enabled: false, user: null });
    const user = await currentUser(db, request);
    return json({ enabled: true, user, ...(isAdmin(env, user) ? { admin: true } : {}) });      // admin: shows the header link to /admin
  }
  if (!db || !cfg) return json({ detail: "accounts are not configured" }, 404);

  if (path === "/api/auth/google") {
    const state = newState();
    return redirect(authUrl(cfg, request, state), [setCookie(request, OAUTH_COOKIE, state, 600)]);
  }

  if (path === "/api/auth/google/callback") {
    const state = url.searchParams.get("state"), code = url.searchParams.get("code");
    const expected = readCookie(request, OAUTH_COOKIE);
    const clear = setCookie(request, OAUTH_COOKIE, "", 0);
    if (!code || !state || !expected || state !== expected) return redirect("/?login=failed", [clear]);
    try {
      const p = await exchangeCode(cfg, request, code);
      let user = await db.prepare("SELECT id FROM users WHERE google_sub = ?").bind(p.sub).first<{ id: string }>();
      if (user) await db.prepare("UPDATE users SET email = ?, name = ?, picture = ? WHERE id = ?").bind(p.email, p.name, p.picture, user.id).run();
      else {
        user = { id: randomToken(16) };
        await db.prepare("INSERT INTO users (id, google_sub, email, name, picture, created_at) VALUES (?, ?, ?, ?, ?, ?)")
          .bind(user.id, p.sub, p.email, p.name, p.picture, Math.floor(Date.now() / 1000)).run();
      }
      await bump(db, "signins");                                 // every successful sign-in, new account or returning
      return redirect("/", [clear, await createSession(db, request, user.id)]);
    } catch {
      return redirect("/?login=failed", [clear]);
    }
  }

  // Admin grant, for testing before payments exist: needs ADMIN_TOKEN (a Worker secret); without it the route does not exist.
  if (path === "/api/admin/grant") {
    if (!env.ADMIN_TOKEN) return json({ detail: "not found" }, 404);
    if (request.method !== "POST") return json({ detail: "POST only" }, 405);
    if (!(await sameSecret(request.headers.get("authorization") ?? "", `Bearer ${env.ADMIN_TOKEN}`))) return json({ detail: "forbidden" }, 403);
    const b = await request.json().catch(() => null) as { email?: unknown; coins?: unknown; ref?: unknown } | null;
    if (!b || typeof b.email !== "string" || !Number.isInteger(b.coins) || (b.coins as number) <= 0 || (b.coins as number) > 100000 || typeof b.ref !== "string" || !b.ref)
      return json({ detail: "body must be {email, coins (1..100000), ref}" }, 400);
    const u = await db.prepare("SELECT id FROM users WHERE email = ?").bind(b.email).first<{ id: string }>();
    if (!u) return json({ detail: "no such user" }, 404);
    const applied = await grant(db, u.id, b.coins as number, `admin:${b.ref}`);
    return json({ applied, wallet: await getWallet(db, u.id) });
  }

  const user = await currentUser(db, request);

  if (path === "/api/auth/logout") {
    if (request.method !== "POST") return json({ detail: "POST only" }, 405);
    await destroySession(db, request);
    return json({ ok: true }, 200, { "set-cookie": setCookie(request, COOKIE, "", 0) });
  }

  if (!path.startsWith("/api/me/")) return json({ detail: "not found" }, 404);
  if (!user) return json({ detail: "sign in required" }, 401);
  // Cookie auth plus SameSite=Lax; writes also need a custom header, which a cross-site form or image cannot send.
  if (request.method !== "GET" && request.headers.get("x-tvbt") !== "1") return json({ detail: "missing x-tvbt header" }, 403);

  if (path === "/api/me/wallet" && request.method === "GET") return json({ ...(await getWallet(db, user.id)), packs: PACKS, canBuy: !!env.STRIPE_SECRET_KEY });
  if (path === "/api/me/charts" && request.method === "GET") return json({ charts: await listCharts(db, user.id) });
  if (path === "/api/me/charts/sync" && request.method === "POST") {
    const body = await request.json().catch(() => null) as { charts?: unknown } | null;
    if (!body || !Array.isArray(body.charts)) return json({ detail: "body must be {charts: [...]}" }, 400);
    return json({ charts: await syncCharts(db, user.id, body.charts) });
  }
  const del = path.match(/^\/api\/me\/charts\/([a-z0-9]{1,20})$/);
  if (del && request.method === "DELETE") { await deleteChart(db, user.id, del[1]); return json({ ok: true }); }
  return json({ detail: "not found" }, 404);
}
