// Payments with a fake Stripe: signatures, crediting exactly once, and everything that must NOT credit.
import { test, before, after, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import { readFileSync, readdirSync } from "node:fs";
import { getPlatformProxy } from "wrangler";
import { verifyWebhook, handleEvent, createCheckout } from "../stripe.ts";
import { handleBilling } from "../route.ts";
import { getWallet } from "../wallet.ts";
import { PACKS } from "../config.ts";
import { handleAuth } from "../../auth/route.ts";
import { createSession } from "../../auth/session.ts";

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
  uid = `p${++n}`;
  await db.prepare("INSERT INTO users (id, google_sub, email, created_at) VALUES (?, ?, ?, 1)").bind(uid, `s${n}`, `p${n}@x.test`).run();
});

const SECRET = "whsec_test", NOW = 1_800_000_000_000;
const sign = (body: string, t = NOW / 1000, secret = SECRET) => `t=${t},v1=${createHmac("sha256", secret).update(`${t}.${body}`).digest("hex")}`;
const paid = (over: Record<string, unknown> = {}, pack = PACKS[0]) => ({ type: "checkout.session.completed", data: { object: {
  id: `cs_${Math.random().toString(36).slice(2)}`, payment_status: "paid", amount_total: pack.amount, currency: "vnd", client_reference_id: uid, metadata: { pack: pack.id }, ...over } } });
const coins = async () => (await getWallet(db, uid)).coins;

test("webhook signature: valid passes; wrong secret, tampered body, stale or missing header fail", async () => {
  const body = '{"a":1}';
  assert.equal(await verifyWebhook(body, sign(body), SECRET, NOW), true);
  assert.equal(await verifyWebhook(body, sign(body, NOW / 1000, "whsec_other"), SECRET, NOW), false);
  assert.equal(await verifyWebhook('{"a":2}', sign(body), SECRET, NOW), false);
  assert.equal(await verifyWebhook(body, sign(body, NOW / 1000 - 600), SECRET, NOW), false);       // ten minutes old
  assert.equal(await verifyWebhook(body, null, SECRET, NOW), false);
  assert.equal(await verifyWebhook(body, "garbage", SECRET, NOW), false);
  // Stripe may send several v1 signatures while a secret is being rotated; any one matching is enough
  assert.equal(await verifyWebhook(body, `t=${NOW / 1000},v1=${"0".repeat(64)},${sign(body).split(",")[1]}`, SECRET, NOW), true);
});

test("a paid session credits the pack's coins once, and a replayed webhook credits nothing more", async () => {
  const ev = paid({}, PACKS[1]);
  assert.equal(await handleEvent(db, ev), "credited");
  assert.equal(await coins(), PACKS[1].coins);
  assert.equal(await handleEvent(db, ev), "duplicate");
  assert.equal(await handleEvent(db, ev), "duplicate");
  assert.equal(await coins(), PACKS[1].coins);
  const rows = await db.prepare("SELECT COUNT(*) AS n FROM payments WHERE user_id = ?").bind(uid).first<{ n: number }>();
  assert.equal(rows!.n, 1);
  // a different session is a different purchase
  assert.equal(await handleEvent(db, paid({}, PACKS[0])), "credited");
  assert.equal(await coins(), PACKS[1].coins + PACKS[0].coins);
});

test("nothing is credited for unpaid sessions, other events, wrong amounts, unknown packs or users", async () => {
  assert.equal(await handleEvent(db, paid({ payment_status: "unpaid" })), "ignored");
  assert.equal(await handleEvent(db, { ...paid(), type: "payment_intent.created" }), "ignored");
  assert.equal(await handleEvent(db, paid({ amount_total: 1000 })), "rejected");                 // paid less than the pack costs
  assert.equal(await handleEvent(db, paid({ currency: "usd" })), "rejected");
  assert.equal(await handleEvent(db, paid({ metadata: { pack: "p9999", coins: "999999" } })), "rejected");
  assert.equal(await handleEvent(db, paid({ client_reference_id: "nobody" })), "rejected");
  assert.equal(await handleEvent(db, paid({ client_reference_id: null })), "rejected");
  assert.equal(await handleEvent(db, { type: "checkout.session.completed" } as any), "ignored");
  assert.equal(await coins(), 0);
});

test("a delayed payment method credits when it finally succeeds, not before", async () => {
  const id = "cs_delayed";
  assert.equal(await handleEvent(db, paid({ id, payment_status: "unpaid" })), "ignored");
  assert.equal(await coins(), 0);
  assert.equal(await handleEvent(db, { ...paid({ id }), type: "checkout.session.async_payment_succeeded" }), "credited");
  assert.equal(await coins(), PACKS[0].coins);
});

test("the webhook route needs a valid signature; a good one credits and answers 200", async () => {
  const env: any = { DB: db, STRIPE_WEBHOOK_SECRET: SECRET };
  const body = JSON.stringify(paid());
  const post = (headers: Record<string, string>, b = body, e = env) => handleBilling(new Request("https://x.test/api/stripe/webhook", { method: "POST", headers, body: b }), e, null);
  assert.equal((await post({})).status, 400);
  assert.equal((await post({ "stripe-signature": sign(body, Math.floor(Date.now() / 1000), "wrong") })).status, 400);
  assert.equal(await coins(), 0);
  const ok = await post({ "stripe-signature": sign(body, Math.floor(Date.now() / 1000)) });
  assert.equal(ok.status, 200); assert.equal(((await ok.json()) as any).result, "credited");
  assert.equal(await coins(), PACKS[0].coins);
  assert.equal((await post({ "stripe-signature": "x" }, body, { DB: db })).status, 503);          // no secret configured
  assert.equal((await handleBilling(new Request("https://x.test/api/stripe/webhook"), env, null)).status, 405);
});

test("checkout: needs sign-in, header and key; only known packs; return URLs use our own origin; the price comes from our table", async () => {
  const sent: { url: string; body: URLSearchParams; auth: string }[] = [];
  const fakeStripe = async (url: string, init?: RequestInit) => { sent.push({ url, body: new URLSearchParams(String(init!.body)), auth: String((init!.headers as any).authorization) }); return new Response(JSON.stringify({ url: "https://checkout.stripe.com/c/pay/cs_1" })); };
  const user = { id: uid, email: `p${n}@x.test`, name: "", picture: "" };
  const env: any = { DB: db, STRIPE_SECRET_KEY: "sk_test_x" };
  const call = (body: unknown, u: any = user, headers: Record<string, string> = { "x-tvbt": "1", origin: "https://evil.test" }, e = env) =>
    handleBilling(new Request("https://tu-vi.test/api/me/checkout", { method: "POST", headers, body: JSON.stringify(body) }), e, u, fakeStripe as any);

  assert.equal((await call({ pack: "p50" }, null)).status, 401);
  assert.equal((await call({ pack: "p50" }, user, {})).status, 403);
  assert.equal((await call({ pack: "p50" }, user, { "x-tvbt": "1" }, { DB: db })).status, 503);
  assert.equal((await call({ pack: "free" })).status, 400);
  assert.equal((await call({ pack: "p50", amount: 1 })).status, 200);
  assert.equal(sent.length, 1);
  const b = sent[0].body;
  assert.equal(sent[0].url, "https://api.stripe.com/v1/checkout/sessions"); assert.equal(sent[0].auth, "Bearer sk_test_x");
  assert.equal(b.get("line_items[0][price_data][unit_amount]"), String(PACKS[0].amount));         // the browser's "amount" was ignored
  assert.equal(b.get("line_items[0][price_data][currency]"), "vnd");
  assert.equal(b.get("client_reference_id"), uid); assert.equal(b.get("metadata[pack]"), "p50");
  // our origin, not the Origin header's; the visitor comes back to the receipt of the order made for this purchase
  assert.match(b.get("success_url")!, /^https:\/\/tu-vi\.test\/bien-nhan\?order=[0-9a-f]{20}$/);
  assert.equal(b.get("success_url")!.split("=")[1], b.get("metadata[order]"));
  const r = await call({ pack: "p400" }); assert.equal(((await r.json()) as any).url, "https://checkout.stripe.com/c/pay/cs_1");
  const failing = async () => new Response("{}", { status: 500 });
  assert.equal((await handleBilling(new Request("https://x.test/api/me/checkout", { method: "POST", headers: { "x-tvbt": "1" }, body: JSON.stringify({ pack: "p50" }) }), env, user, failing as any)).status, 502);
});

test("the wallet endpoint lists the packs and whether buying is possible", async () => {
  const cookie = (await createSession(db, new Request("https://x.test"), uid)).split(";")[0];
  const get = (e: any) => handleAuth(new Request("https://x.test/api/me/wallet", { headers: { cookie } }), { DB: db, GOOGLE_CLIENT_ID: "c", GOOGLE_CLIENT_SECRET: "s", ...e });
  const a = await (await get({})).json() as any; assert.equal(a.canBuy, false); assert.equal(a.packs.length, PACKS.length);
  const b = await (await get({ STRIPE_SECRET_KEY: "sk" })).json() as any; assert.equal(b.canBuy, true);
});
