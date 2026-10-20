// Wallet rules against a real local D1 (wrangler's platform proxy). Money-like code: every rule has a test.
import { test, before, after, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { getPlatformProxy } from "wrangler";
import { getWallet, grant, refund, spend } from "../wallet.ts";
import { handleAuth } from "../../auth/route.ts";
import { createSession } from "../../auth/session.ts";
import { FREE_MESSAGES_PER_MONTH, nextResetAt, periodOf } from "../config.ts";

let proxy: Awaited<ReturnType<typeof getPlatformProxy>>, db: D1Database, n = 0, uid = "";
before(async () => {
  proxy = await getPlatformProxy({ configPath: "wrangler.jsonc", persist: false });
  db = (proxy.env as any).DB as D1Database;
  for (const f of readdirSync("migrations/app").sort()) {
    const sql = readFileSync(`migrations/app/${f}`, "utf8").replace(/--.*$/gm, "");
    for (const stmt of sql.split(";").map(s => s.trim()).filter(Boolean)) await db.prepare(stmt).run();
  }
});
after(async () => { await proxy.dispose(); });
beforeEach(async () => {
  uid = `u${++n}`;
  await db.prepare("INSERT INTO users (id, google_sub, email, created_at) VALUES (?, ?, ?, 1)").bind(uid, `s${n}`, `u${n}@x.test`).run();
});

const T = Date.UTC(2026, 9, 19, 5, 0);           // 19 Oct 2026, 12:00 Vietnam time
const coins = async () => (await getWallet(db, uid, T)).coins;

test("months and resets follow Vietnam time", () => {
  assert.equal(periodOf(Date.UTC(2026, 9, 31, 16, 59)), "2026-10");      // 23:59 on 31 Oct in Vietnam
  assert.equal(periodOf(Date.UTC(2026, 9, 31, 17, 0)), "2026-11");       // 00:00 on 1 Nov in Vietnam
  assert.equal(nextResetAt(T), Date.UTC(2026, 9, 31, 17, 0));
});

test("a new wallet has the full free allowance and no coins", async () => {
  const w = await getWallet(db, uid, T);
  assert.deepEqual([w.coins, w.free.used, w.free.remaining, w.free.limit], [0, 0, FREE_MESSAGES_PER_MONTH, FREE_MESSAGES_PER_MONTH]);
});

test("10 free chats, then locked without coins, and a refused spend charges nothing", async () => {
  for (let i = 0; i < FREE_MESSAGES_PER_MONTH; i++) { const r = await spend(db, uid, "chat", T); assert.ok(r.ok && r.source === "free"); }
  assert.deepEqual(await spend(db, uid, "chat", T), { ok: false, reason: "insufficient" });
  const w = await getWallet(db, uid, T);
  assert.equal(w.free.used, FREE_MESSAGES_PER_MONTH); assert.equal(w.coins, 0);
  const rows = await db.prepare("SELECT COUNT(*) AS n FROM ledger WHERE user_id = ?").bind(uid).first<{ n: number }>();
  assert.equal(rows!.n, FREE_MESSAGES_PER_MONTH);
});

test("after the free allowance, chats cost coins; deep reading never uses the free allowance", async () => {
  await grant(db, uid, 3, "t1", T);
  const d = await spend(db, uid, "deep", T);                       // 20 coins, only has 3
  assert.equal(d.ok, false);
  assert.equal((await getWallet(db, uid, T)).free.used, 0);        // free allowance untouched by a deep attempt
  for (let i = 0; i < FREE_MESSAGES_PER_MONTH; i++) await spend(db, uid, "chat", T);
  const c = await spend(db, uid, "chat", T); assert.ok(c.ok && c.source === "coin");
  assert.equal(await coins(), 2);
});

test("the free allowance renews in a new month", async () => {
  for (let i = 0; i < FREE_MESSAGES_PER_MONTH; i++) await spend(db, uid, "chat", T);
  assert.equal((await spend(db, uid, "chat", T)).ok, false);
  const next = nextResetAt(T) + 1000;
  assert.equal((await getWallet(db, uid, next)).free.remaining, FREE_MESSAGES_PER_MONTH);
  const r = await spend(db, uid, "chat", next); assert.ok(r.ok && r.source === "free");
  assert.equal((await getWallet(db, uid, next)).free.used, 1);
});

test("parallel requests can never overspend (10 free + 5 coins, 40 attempts)", async () => {
  await grant(db, uid, 5, "t2", T);
  const res = await Promise.all(Array.from({ length: 40 }, () => spend(db, uid, "chat", T)));
  const ok = res.filter(r => r.ok) as Extract<typeof res[number], { ok: true }>[];
  assert.equal(ok.length, FREE_MESSAGES_PER_MONTH + 5);
  assert.equal(ok.filter(r => r.source === "free").length, FREE_MESSAGES_PER_MONTH);
  assert.equal(new Set(ok.map(r => r.ref)).size, ok.length);       // every spend has its own ledger row
  assert.equal(await coins(), 0);
  const w = await getWallet(db, uid, T); assert.equal(w.free.used, FREE_MESSAGES_PER_MONTH);
});

test("refund returns a free use or coins exactly once", async () => {
  await grant(db, uid, 1, "t3", T);
  const free = await spend(db, uid, "chat", T); assert.ok(free.ok);
  assert.equal(await refund(db, uid, (free as any).ref, T), true);
  assert.equal(await refund(db, uid, (free as any).ref, T), false);          // second call is a no-op
  assert.equal((await getWallet(db, uid, T)).free.used, 0);
  for (let i = 0; i < FREE_MESSAGES_PER_MONTH; i++) await spend(db, uid, "chat", T);
  const paid = await spend(db, uid, "chat", T); assert.ok(paid.ok && paid.source === "coin");
  assert.equal(await coins(), 0);
  assert.equal(await refund(db, uid, (paid as any).ref, T), true);
  assert.equal(await refund(db, uid, (paid as any).ref, T), false);
  assert.equal(await coins(), 1);
});

test("refund cannot touch another user's spend", async () => {
  const mine = await spend(db, uid, "chat", T); assert.ok(mine.ok);
  const other = uid; uid = `v${++n}`;
  await db.prepare("INSERT INTO users (id, google_sub, email, created_at) VALUES (?, ?, ?, 1)").bind(uid, `s${n}`, `v${n}@x.test`).run();
  assert.equal(await refund(db, uid, (mine as any).ref, T), false);
  assert.equal((await getWallet(db, other, T)).free.used, 1);
});

test("a free refund after the month rolled over does not touch the new month", async () => {
  const s = await spend(db, uid, "chat", T); assert.ok(s.ok);
  const next = nextResetAt(T) + 1000;
  await spend(db, uid, "chat", next);                              // new month: counter now 1 for the new period
  assert.equal(await refund(db, uid, (s as any).ref, next), false);
  assert.equal((await getWallet(db, uid, next)).free.used, 1);
});

test("grant is idempotent per ref and validates the amount", async () => {
  assert.equal(await grant(db, uid, 50, "pay_1", T), true);
  assert.equal(await grant(db, uid, 50, "pay_1", T), false);
  assert.equal(await coins(), 50);
  await assert.rejects(() => grant(db, uid, 0, "x", T));
  await assert.rejects(() => grant(db, uid, 1.5, "y", T));
});

test("HTTP: wallet needs sign-in; admin grant needs the token and is hidden without one", async () => {
  const env: any = { DB: db, GOOGLE_CLIENT_ID: "c", GOOGLE_CLIENT_SECRET: "s" };
  const call = (path: string, init: RequestInit = {}, e = env) => handleAuth(new Request("https://x.test" + path, init), e);
  assert.equal((await call("/api/me/wallet")).status, 401);
  const cookie = (await createSession(db, new Request("https://x.test"), uid)).split(";")[0];
  const w = await (await call("/api/me/wallet", { headers: { cookie } })).json() as any;
  assert.equal(w.free.limit, FREE_MESSAGES_PER_MONTH);

  const body = JSON.stringify({ email: `u${n}@x.test`, coins: 7, ref: "r1" });
  const post = (h: Record<string, string>, e = env) => call("/api/admin/grant", { method: "POST", headers: h, body }, e);
  assert.equal((await post({ authorization: "Bearer k" })).status, 404);                      // no ADMIN_TOKEN: route does not exist
  const withTok = { ...env, ADMIN_TOKEN: "k" };
  assert.equal((await post({ authorization: "Bearer wrong" }, withTok)).status, 403);
  assert.equal((await post({}, withTok)).status, 403);
  const ok = await (await post({ authorization: "Bearer k" }, withTok)).json() as any;
  assert.equal(ok.applied, true); assert.equal(ok.wallet.coins, 7);
  const again = await (await post({ authorization: "Bearer k" }, withTok)).json() as any;
  assert.equal(again.applied, false); assert.equal(again.wallet.coins, 7);
});
