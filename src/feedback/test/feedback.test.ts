// Feedback bubble, visit counting and the admin area, against a real local D1 (wrangler's platform proxy).
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { getPlatformProxy } from "wrangler";
import { handleFeedback } from "../route.ts";
import { handleAdmin, isAdmin, siteStats } from "../../admin/route.ts";
import { bump, vnDay } from "../../stats/stats.ts";
import type { User } from "../../auth/session.ts";

let proxy: Awaited<ReturnType<typeof getPlatformProxy>>, db: D1Database;
before(async () => {
  proxy = await getPlatformProxy({ configPath: "wrangler.jsonc", persist: false });
  db = (proxy.env as any).DB as D1Database;
  // only the older migrations: the feedback tables must appear on first use, as on a deploy where 0006 was not applied yet
  for (const f of readdirSync("migrations/app").sort().filter(f => f < "0006")) {
    const sql = readFileSync(`migrations/app/${f}`, "utf8").replace(/--.*$/gm, "");
    for (const stmt of sql.split(";").map(s => s.trim()).filter(Boolean)) await db.prepare(stmt).run();
  }
});
after(async () => { await proxy.dispose(); });

const BASE = "https://example.test";
const admin: User = { id: "u-admin", email: "Boss@Example.com", name: "Boss", picture: "" };
const visitor: User = { id: "u-v", email: "v@example.com", name: "Vi", picture: "" };
const env = { DB: undefined as unknown as D1Database, ADMIN_EMAILS: " other@x.com, boss@example.com " };
const fb = (init: RequestInit & { key?: string; path?: string; ip?: string } = {}, user: User | null = null) =>
  handleFeedback(new Request(BASE + (init.path ?? "/api/feedback"), { ...init, headers: {
    "x-tvbt": "1", "content-type": "application/json", "cf-connecting-ip": init.ip ?? "1.2.3.4", ...(init.key ? { "x-feedback-key": init.key } : {}), ...(init.headers as object) } }), db, user);
const adm = (path: string, init: RequestInit = {}, user: User | null = admin) =>
  handleAdmin(new Request(BASE + path, { ...init, headers: { "x-tvbt": "1", "content-type": "application/json", ...(init.headers as object) } }), { ...env, DB: db }, user);

test("admins are the signed-in accounts listed in ADMIN_EMAILS, case and spaces ignored; nobody without the list", () => {
  assert.equal(isAdmin(env, admin), true);
  assert.equal(isAdmin(env, visitor), false);
  assert.equal(isAdmin(env, null), false);
  assert.equal(isAdmin({}, admin), false);
  assert.equal(isAdmin({ ADMIN_EMAILS: "" }, { ...admin, email: "" }), false);
});

test("a visitor starts a thread without signing in, gets a key, and only that key reads it", async () => {
  const r = await fb({ method: "POST", body: JSON.stringify({ body: "  Trang bị lỗi ở phần Bát Tự  ", page: "/#chart" }) });
  assert.equal(r.status, 200);
  const j = await r.json() as any;
  assert.match(j.key, /^[A-Za-z0-9_-]{30,}$/);
  assert.deepEqual(j.messages.map((m: any) => [m.author, m.body]), [["visitor", "Trang bị lỗi ở phần Bát Tự"]]);
  const own = await (await fb({ key: j.key })).json() as any;
  assert.equal(own.messages.length, 1);
  assert.deepEqual(await (await fb({ key: "x".repeat(32) })).json(), { messages: [] });
  assert.deepEqual(await (await fb({})).json(), { messages: [] });
});

test("writes need the x-tvbt header, and the message must be 1..2000 characters", async () => {
  const r = await handleFeedback(new Request(BASE + "/api/feedback", { method: "POST", body: JSON.stringify({ body: "hi" }) }), db, null);
  assert.equal(r.status, 403);
  assert.equal((await fb({ method: "POST", body: JSON.stringify({ body: "   " }) })).status, 400);
  assert.equal((await fb({ method: "POST", body: JSON.stringify({ body: "a".repeat(2001) }) })).status, 400);
  assert.equal((await handleFeedback(new Request(BASE + "/api/feedback"), undefined, null)).status, 503);
});

test("non-admins get 404 everywhere under /api/admin; the admin sees the inbox, replies, and the visitor reads the reply", async () => {
  for (const u of [null, visitor]) for (const p of ["/api/admin/me", "/api/admin/stats", "/api/admin/feedback"]) assert.equal((await adm(p, {}, u)).status, 404);
  const start = await (await fb({ method: "POST", ip: "9.9.9.9", body: JSON.stringify({ body: "Cho mình hỏi về xu" }) }, visitor)).json() as any;
  const list = await (await adm("/api/admin/feedback")).json() as any;
  const t = list.threads.find((x: any) => x.email === "v@example.com");
  assert.equal(t.unread, 1); assert.equal(t.last, "Cho mình hỏi về xu");
  assert.equal((await adm(`/api/admin/feedback/${t.id}`, { method: "POST", body: JSON.stringify({ body: "Chào bạn, xu dùng cho chat." }), headers: { "x-tvbt": "" } })).status, 403);
  const rep = await (await adm(`/api/admin/feedback/${t.id}`, { method: "POST", body: JSON.stringify({ body: "Chào bạn, xu dùng cho chat." }) })).json() as any;
  assert.deepEqual(rep.messages.map((m: any) => m.author), ["visitor", "admin"]);
  const after = (await (await adm("/api/admin/feedback")).json() as any).threads.find((x: any) => x.id === t.id);
  assert.equal(after.unread, 0); assert.equal(after.lastAuthor, "admin");
  const seen = await (await fb({ key: start.key, path: `/api/feedback?after=${start.messages[0].id}` })).json() as any;
  assert.deepEqual(seen.messages.map((m: any) => m.body), ["Chào bạn, xu dùng cho chat."]);
});

test("new threads are limited per network address, and messages per thread", async () => {
  for (let i = 0; i < 5; i++) assert.equal((await fb({ method: "POST", ip: "5.5.5.5", body: JSON.stringify({ body: "m" + i }) })).status, 200);
  assert.equal((await fb({ method: "POST", ip: "5.5.5.5", body: JSON.stringify({ body: "one more" }) })).status, 429);
  const { key } = await (await fb({ method: "POST", ip: "6.6.6.6", body: JSON.stringify({ body: "0" }) })).json() as any;
  for (let i = 1; i < 20; i++) await fb({ method: "POST", key, body: JSON.stringify({ body: String(i) }) });
  assert.equal((await fb({ method: "POST", key, body: JSON.stringify({ body: "too many" }) })).status, 429);
});

test("visits count per call and unique visitors per browser per day; bots are ignored; stats add up by day", async () => {
  const hit = (vid: string, ua = "Mozilla/5.0") => fb({ path: "/api/hit", method: "POST", body: JSON.stringify({ vid }), headers: { "user-agent": ua } });
  await hit("browserAAAA1"); await hit("browserAAAA1"); await hit("browserBBBB2"); await hit("crawlerCCCC3", "Googlebot/2.1");
  assert.equal((await hit("bad id!")).status, 400);
  await bump(db, "scans"); await bump(db, "signins");
  const s = await siteStats(db);
  assert.equal(s.days[29], vnDay());
  assert.deepEqual([s.visits.today, s.visits.d7, s.visits.all], [3, 3, 3]);
  assert.deepEqual([s.visitors.today, s.visitors.d7, s.visitors.all], [2, 2, 2]);
  assert.equal(s.scans.today, 1); assert.equal(s.scans.all, 103);       // landing-page base 102 + one recorded
  assert.equal(s.signins.today, 1);
  assert.equal(s.series.visits[29], 3);
  assert.ok(s.feedback.threads >= 3); assert.equal(s.feedback.unread >= 1, true);
  const r = await adm("/api/admin/stats"); assert.equal(r.status, 200); assert.equal(r.headers.get("cache-control"), "no-store");
});
