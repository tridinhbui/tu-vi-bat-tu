// Phase 3 account routes: /api/me/profile, /api/me/shares*, /api/me/charts/<id>/share, /api/me/data, /api/me/account (signed in),
// and the public /api/share/<id>* (src/account/shares.ts). Same rules as src/auth/route.ts: cookie session, and every write carries x-tvbt.
import { COOKIE, currentUser, setCookie } from "../auth/session.ts";
import { cleanProfile, getProfile, putProfile } from "./profile.ts";
import { createShare, handleShare, listShares, revokeShare, setShareHide, SHARE_ID, type Forward } from "./shares.ts";

// Same statements as migrations/app/0008_profile_shares.sql, run once per isolate so a deploy works before the migration is applied.
const SCHEMA = [
  "CREATE TABLE IF NOT EXISTS profiles (user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE, data_json TEXT NOT NULL, updated_at INTEGER NOT NULL)",
  "CREATE TABLE IF NOT EXISTS shares (id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, chart_fp TEXT NOT NULL, hide_birth INTEGER NOT NULL DEFAULT 1, created_at INTEGER NOT NULL, revoked_at INTEGER)",
  "CREATE INDEX IF NOT EXISTS shares_user ON shares(user_id, created_at)",
];
const ready = new WeakMap<D1Database, Promise<unknown>>();
export function ensureAccountSchema(db: D1Database): Promise<unknown> {
  let p = ready.get(db);
  if (!p) { p = db.batch(SCHEMA.map(s => db.prepare(s))).catch(e => { ready.delete(db); throw e; }); ready.set(db, p); }
  return p;
}

const json = (body: unknown, status = 200, headers: HeadersInit = {}) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...headers } });

const SHARE_OF_CHART = /^\/api\/me\/charts\/([a-z0-9]{1,20})\/share$/;
export const isAccountPath = (p: string) =>
  p === "/api/me/profile" || p === "/api/me/data" || p === "/api/me/account" || p === "/api/me/shares" || p.startsWith("/api/me/shares/") ||
  SHARE_OF_CHART.test(p) || p.startsWith("/api/share/");

// Typed by the user in the confirmation box; the server checks it too, so a stray request cannot wipe an account.
export const CONFIRM = "XOA";

/** Everything this account stored except the account itself and its wallet (coins already paid for stay). */
async function deleteData(db: D1Database, userId: string): Promise<void> {
  await db.batch([
    db.prepare("DELETE FROM shares WHERE user_id = ?").bind(userId),
    db.prepare("DELETE FROM profiles WHERE user_id = ?").bind(userId),
    db.prepare("DELETE FROM deep_readings WHERE user_id = ?").bind(userId),
    db.prepare("DELETE FROM charts WHERE user_id = ?").bind(userId),
  ]);
  // feedback threads carry the name and e-mail of a signed-in writer; the table appears on first use (src/feedback/route.ts)
  try { await db.prepare("DELETE FROM feedback_threads WHERE user_id = ?").bind(userId).run(); } catch { /* no feedback table yet */ }
  try { await db.prepare("DELETE FROM horary_questions WHERE user_id = ?").bind(userId).run(); } catch { /* no horary table yet */ }
  // saved Tarot draws (and their questions); the table appears with migrations/app/0011_tarot.sql or the first draw
  try { await db.prepare("DELETE FROM tarot_draws WHERE user_id = ?").bind(userId).run(); } catch { /* no tarot table yet */ }
}

export async function handleAccount(request: Request, db: D1Database | undefined, forward: Forward): Promise<Response> {
  const path = new URL(request.url).pathname;
  if (!db) return json({ detail: "accounts are not configured" }, 404);
  await ensureAccountSchema(db);
  if (path.startsWith("/api/share/")) return handleShare(request, db, forward);

  const user = await currentUser(db, request);
  if (!user) return json({ detail: "sign in required" }, 401);
  if (request.method !== "GET" && request.headers.get("x-tvbt") !== "1") return json({ detail: "missing x-tvbt header" }, 403);
  const body = () => request.json().catch(() => null) as Promise<Record<string, unknown> | null>;

  if (path === "/api/me/profile") {
    if (request.method === "GET") return json({ profile: await getProfile(db, user.id) });
    if (request.method !== "PUT") return json({ detail: "GET or PUT" }, 405);
    const p = cleanProfile(await body());
    if (typeof p === "string") return json({ detail: p }, 400);
    await putProfile(db, user.id, p);
    return json({ profile: p });
  }

  if (path === "/api/me/shares" && request.method === "GET") return json({ shares: await listShares(db, user.id) });
  const sc = path.match(SHARE_OF_CHART);
  if (sc) {
    if (request.method !== "POST") return json({ detail: "POST only" }, 405);
    const b = await body();
    const r = await createShare(db, user.id, sc[1], b?.hide !== false);          // hidden unless the owner says otherwise
    if (r === "no_chart") return json({ detail: "no such saved chart" }, 404);
    if (r === "too_many") return json({ detail: "too many active share links; revoke one first" }, 409);
    return json({ share: r });
  }
  const one = path.match(/^\/api\/me\/shares\/([^/]+)$/);
  if (one) {
    if (!SHARE_ID.test(one[1])) return json({ detail: "not found" }, 404);
    if (request.method === "PATCH") {
      const b = await body();
      if (!b || typeof b.hide !== "boolean") return json({ detail: "body must be {hide: boolean}" }, 400);
      return (await setShareHide(db, user.id, one[1], b.hide)) ? json({ ok: true, hide: b.hide }) : json({ detail: "not found" }, 404);
    }
    if (request.method === "DELETE") return (await revokeShare(db, user.id, one[1])) ? json({ ok: true }) : json({ detail: "not found" }, 404);
    return json({ detail: "PATCH or DELETE" }, 405);
  }

  if ((path === "/api/me/data" || path === "/api/me/account") && request.method === "POST") {
    const b = await body();
    if (b?.confirm !== CONFIRM) return json({ detail: `body must be {confirm: "${CONFIRM}"}` }, 400);
    await deleteData(db, user.id);
    if (path === "/api/me/data") return json({ ok: true });
    // wallet, ledger and payments go with the user row (ON DELETE CASCADE); sessions are removed explicitly as well
    await db.batch([db.prepare("DELETE FROM sessions WHERE user_id = ?").bind(user.id), db.prepare("DELETE FROM users WHERE id = ?").bind(user.id)]);
    return json({ ok: true }, 200, { "set-cookie": setCookie(request, COOKIE, "", 0) });
  }
  return json({ detail: "not found" }, 404);
}
