// Runs the auth handler against a real local D1 (wrangler's platform proxy); Google itself is not called.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { getPlatformProxy } from "wrangler";
import { handleAuth } from "../route.ts";
import { createSession, sha256 } from "../session.ts";

let proxy: Awaited<ReturnType<typeof getPlatformProxy>>, db: D1Database, env: any;
before(async () => {
  proxy = await getPlatformProxy({ configPath: "wrangler.jsonc", persist: false });
  db = proxy.env.DB as D1Database;
  const sql = (await import("node:fs")).readFileSync("migrations/app/0001_accounts.sql", "utf8");
  for (const stmt of sql.replace(/--.*$/gm, "").split(";").map(s => s.trim()).filter(Boolean)) await db.prepare(stmt).run();
  env = { DB: db, GOOGLE_CLIENT_ID: "cid", GOOGLE_CLIENT_SECRET: "sec" };
});
after(async () => { await proxy.dispose(); });

const BASE = "https://example.test";
const call = (path: string, init: RequestInit = {}, cookie = "") =>
  handleAuth(new Request(BASE + path, { ...init, headers: { ...(init.headers as object), ...(cookie ? { cookie } : {}) } }), env);
const chart = (day: number, label = "Minh") => ({ id: "a" + day, label, rel: "Tôi", req: { year: 1990, month: 5, day, hour: 10, minute: 30, gender: "male", evil: "dropped" } });

test("me is signed out without a cookie, and disabled without config", async () => {
  assert.deepEqual(await (await call("/api/auth/me")).json(), { enabled: true, user: null });
  const off = await handleAuth(new Request(BASE + "/api/auth/me"), {});
  assert.deepEqual(await off.json(), { enabled: false, user: null });
});

test("google start sets a state cookie and redirects to Google", async () => {
  const r = await call("/api/auth/google");
  assert.equal(r.status, 302);
  assert.match(r.headers.get("location")!, /^https:\/\/accounts\.google\.com\//);
  assert.match(r.headers.get("set-cookie")!, /tvbt_oauth=.+HttpOnly.+SameSite=Lax.+Secure/);
});

test("callback with a wrong state is rejected", async () => {
  const r = await call("/api/auth/google/callback?code=x&state=bad", {}, "tvbt_oauth=other");
  assert.equal(r.headers.get("location"), "/?login=failed");
});

test("chart sync merges by birth, caps fields, needs auth and the csrf header", async () => {
  await db.prepare("INSERT INTO users (id, google_sub, email, created_at) VALUES ('u1','s1','a@b.c',1)").run();
  const cookie = (await createSession(db, new Request(BASE), "u1")).split(";")[0];
  assert.equal((await call("/api/me/charts")).status, 401);
  const post = (charts: unknown[], h: object = { "x-tvbt": "1" }) =>
    call("/api/me/charts/sync", { method: "POST", headers: h, body: JSON.stringify({ charts }) }, cookie);
  assert.equal((await post([chart(17)], {})).status, 403);
  const a = await (await post([chart(17), chart(18), { id: "!!", label: "x", rel: "Tôi", req: {} }])).json() as any;
  assert.equal(a.charts.length, 2);
  assert.equal(a.charts[0].req.evil, undefined);
  // same birth from another device (different id) merges, keeps the stored id, takes the new name
  const b = await (await post([{ ...chart(17, "Mẹ"), id: "zzz" }])).json() as any;
  assert.equal(b.charts.length, 2);
  const merged = b.charts.find((c: any) => c.req.day === 17);
  assert.equal(merged.id, "a17"); assert.equal(merged.label, "Mẹ");
  const del = await call("/api/me/charts/a17", { method: "DELETE", headers: { "x-tvbt": "1" } }, cookie);
  assert.equal(del.status, 200);
  assert.equal(((await (await call("/api/me/charts", {}, cookie)).json()) as any).charts.length, 1);
  // logout kills the session
  await call("/api/auth/logout", { method: "POST", headers: { "x-tvbt": "1" } }, cookie);
  assert.equal((await call("/api/me/charts", {}, cookie)).status, 401);
  assert.equal(await db.prepare("SELECT 1 AS x FROM sessions WHERE token_hash=?").bind(await sha256("nope")).first(), null);
});
