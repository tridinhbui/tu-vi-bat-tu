// Referral rules against a real local D1 (wrangler's platform proxy), same set-up as the wallet tests. Coins move, so every rule has a test.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { getPlatformProxy } from "wrangler";
import { getWallet } from "../../billing/wallet.ts";
import { claim, codeOf, CODE_RE, handleReferral, REFERRAL, summary } from "../route.ts";

let proxy: Awaited<ReturnType<typeof getPlatformProxy>>, db: D1Database, n = 0;
const T = Date.UTC(2026, 9, 21, 5, 0);
before(async () => {
  proxy = await getPlatformProxy({ configPath: "wrangler.jsonc", persist: false });
  db = (proxy.env as any).DB as D1Database;
  for (const f of readdirSync("migrations/app").sort()) {
    const sql = readFileSync(`migrations/app/${f}`, "utf8").replace(/--.*$/gm, "");
    for (const stmt of sql.split(";").map(s => s.trim()).filter(Boolean)) await db.prepare(stmt).run();
  }
});
after(async () => { await proxy.dispose(); });

/** A user whose account was created `ageDays` before T. */
async function user(ageDays = 0) {
  const id = `r${++n}`;
  await db.prepare("INSERT INTO users (id, google_sub, email, created_at) VALUES (?, ?, ?, ?)")
    .bind(id, `rs${n}`, `r${n}@x.test`, Math.floor((T - ageDays * 86400_000) / 1000)).run();
  return { id, email: `r${n}@x.test`, name: "", picture: "" };
}
const coins = async (id: string) => (await getWallet(db, id, T)).coins;

test("a code is made once per user and stays the same", async () => {
  const a = await user();
  const c = await codeOf(db, a.id, T);
  assert.match(c, CODE_RE);
  assert.equal(await codeOf(db, a.id, T), c);
});

test("a new account claims a friend's code: both get coins, once", async () => {
  const a = await user(30), b = await user(0);
  const code = await codeOf(db, a.id, T);
  assert.deepEqual(await claim(db, b.id, code.toLowerCase(), T), { ok: true, inviterCoins: REFERRAL.inviterCoins, inviteeCoins: REFERRAL.inviteeCoins });
  assert.equal(await coins(a.id), REFERRAL.inviterCoins);
  assert.equal(await coins(b.id), REFERRAL.inviteeCoins);
  // a retry (double click, network retry) pays nothing more
  assert.equal((await claim(db, b.id, code, T)).ok, true);
  assert.equal(await coins(a.id), REFERRAL.inviterCoins);
  assert.equal(await coins(b.id), REFERRAL.inviteeCoins);
  const s = await summary(db, a, "https://x.test", T);
  assert.deepEqual([s.invited, s.coinsEarned, s.url], [1, REFERRAL.inviterCoins, `https://x.test/?ref=${code}`]);
  assert.equal((await summary(db, b, "https://x.test", T)).joinedByReferral, true);
});

test("refused: own code, unknown code, an old account, a second code", async () => {
  const a = await user(), b = await user(), old = await user(REFERRAL.windowDays + 1), c = await user();
  const ca = await codeOf(db, a.id, T), cb = await codeOf(db, b.id, T);
  assert.deepEqual(await claim(db, a.id, ca, T), { ok: false, reason: "own_code" });
  assert.deepEqual(await claim(db, c.id, "ZZZZZZZZ", T), { ok: false, reason: "bad_code" });
  assert.deepEqual(await claim(db, c.id, "not a code", T), { ok: false, reason: "bad_code" });
  assert.deepEqual(await claim(db, old.id, ca, T), { ok: false, reason: "too_old" });
  assert.equal((await summary(db, old, "https://x.test", T)).canClaim, false);
  assert.equal((await claim(db, c.id, ca, T)).ok, true);
  assert.deepEqual(await claim(db, c.id, cb, T), { ok: false, reason: "already_claimed" });
  assert.equal(await coins(b.id), 0);
  assert.equal(await coins(old.id), 0);
});

test("an inviter is rewarded for at most maxPerInviter accounts", async () => {
  const a = await user(), code = await codeOf(db, a.id, T);
  for (let i = 0; i < REFERRAL.maxPerInviter; i++) assert.equal((await claim(db, (await user()).id, code, T)).ok, true);
  const late = await user();
  assert.deepEqual(await claim(db, late.id, code, T), { ok: false, reason: "inviter_full" });
  assert.equal(await coins(a.id), REFERRAL.maxPerInviter * REFERRAL.inviterCoins);
  assert.equal(await coins(late.id), 0);
});

test("HTTP: sign-in required, writes need the x-tvbt header, status codes", async () => {
  const a = await user(), b = await user();
  const code = await codeOf(db, a.id, T);
  const req = (path: string, init: RequestInit = {}) => new Request("https://x.test" + path, init);
  assert.equal((await handleReferral(req("/api/me/referral"), db, null, T)).status, 401);
  assert.equal((await handleReferral(req("/api/me/referral"), undefined, a, T)).status, 503);
  const g = await (await handleReferral(req("/api/me/referral"), db, a, T)).json() as any;
  assert.equal(g.code, code);
  const post = (body: unknown, h: Record<string, string> = { "x-tvbt": "1" }) =>
    handleReferral(req("/api/me/referral/claim", { method: "POST", headers: { "content-type": "application/json", ...h }, body: JSON.stringify(body) }), db, b, T);
  assert.equal((await post({ code }, {})).status, 403);
  assert.equal((await post({})).status, 400);
  assert.equal((await post({ code: "ZZZZZZZZ" })).status, 404);
  assert.equal((await post({ code })).status, 200);
  assert.equal((await handleReferral(req("/api/me/referral/claim", { method: "POST", headers: { "x-tvbt": "1" }, body: JSON.stringify({ code }) }), db, a, T)).status, 409);
});
