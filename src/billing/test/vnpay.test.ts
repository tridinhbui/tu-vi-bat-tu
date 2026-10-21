// VNPAY against its 2.1.0 spec with a fake gateway: the signed string, the HMAC-SHA512, the payment URL, and the IPN crediting exactly once.
import { test, before, after, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import { readFileSync, readdirSync } from "node:fs";
import { getPlatformProxy } from "wrangler";
import { createPaymentUrl, handleIpn, phpEncode, signData, verifyVnpay, vnpayConfig, vnpTime, VNPAY_SANDBOX_URL, IPN } from "../vnpay.ts";
import { createOrder, getOrder } from "../orders.ts";
import { handleBilling } from "../route.ts";
import { getWallet } from "../wallet.ts";
import { PACKS } from "../config.ts";

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
  uid = `v${++n}`;
  await db.prepare("INSERT INTO users (id, google_sub, email, created_at) VALUES (?, ?, ?, 1)").bind(uid, `vs${n}`, `v${n}@x.test`).run();
});

const SECRET = "SANDBOXSECRETKEY0123456789ABCDEF", TMN = "TBTEST01", NOW = Date.UTC(2026, 9, 21, 3, 4, 5);
const cfg = { tmnCode: TMN, hashSecret: SECRET, url: VNPAY_SANDBOX_URL };
const hmac = (s: string, secret = SECRET) => createHmac("sha512", secret).update(Buffer.from(s, "utf8")).digest("hex");
const coins = async () => (await getWallet(db, uid)).coins;

/** What VNPAY's server sends to the IPN for an order: its fields signed the way VNPAY signs them. */
function ipnParams(o: { id: string; amount: number }, over: Record<string, string> = {}, secret = SECRET) {
  const p: Record<string, string> = {
    vnp_Amount: String(o.amount * 100), vnp_BankCode: "NCB", vnp_BankTranNo: "VNP14422574", vnp_CardType: "ATM", vnp_OrderInfo: `Nap xu Thien Ban, don ${o.id}`,
    vnp_PayDate: "20261021100815", vnp_ResponseCode: "00", vnp_TmnCode: TMN, vnp_TransactionNo: "14422574", vnp_TransactionStatus: "00", vnp_TxnRef: o.id, ...over,
  };
  const data = Object.keys(p).sort().map(k => `${k}=${encodeURIComponent(p[k]).replace(/%20/g, "+")}`).join("&");
  return new URLSearchParams({ ...p, vnp_SecureHashType: "HmacSHA512", vnp_SecureHash: hmac(data, secret) });
}

test("encoding and the signed string follow VNPAY's PHP sample: sorted keys, urlencode with + for spaces, hash fields left out", () => {
  assert.equal(phpEncode("a b/c:d?e=f&g"), "a+b%2Fc%3Ad%3Fe%3Df%26g");
  assert.equal(phpEncode("it's (ok)*!"), "it%27s+%28ok%29%2A%21");                 // PHP urlencode encodes these, encodeURIComponent does not
  assert.equal(phpEncode("Nạp"), "N%E1%BA%A1p");
  const s = signData({ vnp_TxnRef: "abc", vnp_Amount: "4900000", vnp_SecureHash: "x", vnp_SecureHashType: "y", vnp_OrderInfo: "Nap 50 xu", other: "z", vnp_Empty: "" });
  assert.equal(s, "vnp_Amount=4900000&vnp_OrderInfo=Nap+50+xu&vnp_TxnRef=abc");
  assert.equal(signData({ vnp_B: "", vnp_A: "1" }, { keepEmpty: true }), "vnp_A=1&vnp_B=");
});

test("vnp_CreateDate is Vietnam time, yyyyMMddHHmmss", () => {
  assert.equal(vnpTime(NOW), "20261021100405");
  assert.equal(vnpTime(Date.UTC(2026, 11, 31, 17, 0, 0)), "20270101000000");        // midnight in Hà Nội is 17:00 UTC
});

test("the payment URL carries the order, amount x100, and an HMAC-SHA512 over exactly its own query string", async () => {
  const url = await createPaymentUrl(cfg, { order: { id: "0123456789abcdef0123", amount: 49000, coins: 50 }, returnUrl: "https://tu-vi.test/api/vnpay/return", ip: "203.0.113.9", now: NOW });
  const [base, qs] = url.split("?");
  assert.equal(base, VNPAY_SANDBOX_URL);
  const q = new URLSearchParams(qs);
  assert.equal(q.get("vnp_Version"), "2.1.0"); assert.equal(q.get("vnp_Command"), "pay"); assert.equal(q.get("vnp_TmnCode"), TMN);
  assert.equal(q.get("vnp_Amount"), "4900000"); assert.equal(q.get("vnp_CurrCode"), "VND"); assert.equal(q.get("vnp_TxnRef"), "0123456789abcdef0123");
  assert.equal(q.get("vnp_ReturnUrl"), "https://tu-vi.test/api/vnpay/return"); assert.equal(q.get("vnp_IpAddr"), "203.0.113.9");
  assert.equal(q.get("vnp_CreateDate"), "20261021100405"); assert.equal(q.get("vnp_ExpireDate"), "20261021101905");
  assert.match(q.get("vnp_OrderInfo")!, /^[\x20-\x7e]+$/);                         // plain ASCII, as VNPAY asks
  // independent check: the signature is node's HMAC-SHA512 of everything before "&vnp_SecureHash="
  const signed = qs.slice(0, qs.indexOf("&vnp_SecureHash="));
  assert.equal(q.get("vnp_SecureHash"), hmac(signed));
  assert.ok(signed.includes("vnp_ReturnUrl=https%3A%2F%2Ftu-vi.test%2Fapi%2Fvnpay%2Freturn"));
  assert.deepEqual(signed.split("&").map(x => x.split("=")[0]), [...signed.split("&").map(x => x.split("=")[0])].sort());
});

test("callback signatures: VNPAY's own passes; tampered fields, another secret, missing or malformed hash fail", async () => {
  const p = ipnParams({ id: "0123456789abcdef0123", amount: 49000 });
  assert.equal(await verifyVnpay(p, SECRET), true);
  assert.equal(await verifyVnpay(new URLSearchParams({ ...Object.fromEntries(p), vnp_SecureHash: p.get("vnp_SecureHash")!.toUpperCase() }), SECRET), true);
  for (const [k, v] of [["vnp_Amount", "100"], ["vnp_ResponseCode", "24"], ["vnp_TxnRef", "ffffffffffffffffffff"]]) {
    const t = new URLSearchParams(p); t.set(k, v); assert.equal(await verifyVnpay(t, SECRET), false, k);
  }
  assert.equal(await verifyVnpay(p, "another-secret"), false);
  const none = new URLSearchParams(p); none.delete("vnp_SecureHash"); assert.equal(await verifyVnpay(none, SECRET), false);
  const bad = new URLSearchParams(p); bad.set("vnp_SecureHash", "zz"); assert.equal(await verifyVnpay(bad, SECRET), false);
  // a field sent empty: accepted whether VNPAY signed it (PHP/Node samples) or left it out (Java/.NET samples)
  const withEmpty = ipnParams({ id: "0123456789abcdef0123", amount: 49000 }, { vnp_BankTranNo: "" });
  assert.equal(await verifyVnpay(withEmpty, SECRET), true);
  const raw = Object.fromEntries(withEmpty); delete raw.vnp_SecureHash; delete raw.vnp_SecureHashType;
  const withEmptySigned = { ...raw, vnp_SecureHash: hmac(Object.keys(raw).sort().map(k => `${k}=${encodeURIComponent(raw[k]).replace(/%20/g, "+")}`).join("&")) };
  assert.equal(await verifyVnpay(withEmptySigned, SECRET), true);
});

test("IPN credits a paid order once; a repeated IPN answers 02 and adds nothing", async () => {
  const order = await createOrder(db, { userId: uid, provider: "vnpay", pack: PACKS[1] });
  const p = ipnParams(order);
  const first = await handleIpn(db, cfg, p);
  assert.deepEqual(first, { answer: IPN.ok, result: "credited" });
  assert.equal(await coins(), PACKS[1].coins);
  const o = await getOrder(db, order.id);
  assert.equal(o!.status, "paid"); assert.equal(o!.provider_ref, "14422574");
  for (let i = 0; i < 3; i++) assert.deepEqual(await handleIpn(db, cfg, p), { answer: IPN.already });
  assert.equal(await coins(), PACKS[1].coins);
  // even if the order row were somehow still pending, the ledger ref "vnpay:<order>" stops a second credit
  await db.prepare("UPDATE orders SET status = 'pending' WHERE id = ?").bind(order.id).run();
  assert.deepEqual(await handleIpn(db, cfg, p), { answer: IPN.ok, result: "duplicate" });
  assert.equal(await coins(), PACKS[1].coins);
  const pay = await db.prepare("SELECT COUNT(*) AS n FROM payments WHERE session_id = ?").bind(`vnpay:${order.id}`).first<{ n: number }>();
  assert.equal(pay!.n, 1);
});

test("IPN credits nothing for a bad signature, another merchant, an unknown order, a wrong amount, or a failed payment", async () => {
  const order = await createOrder(db, { userId: uid, provider: "vnpay", pack: PACKS[0] });
  assert.deepEqual(await handleIpn(db, cfg, ipnParams(order, {}, "wrong")), { answer: IPN.badSignature });
  assert.deepEqual(await handleIpn(db, cfg, ipnParams(order, { vnp_TmnCode: "OTHER" })), { answer: IPN.badSignature });
  assert.deepEqual(await handleIpn(db, cfg, ipnParams({ id: "ffffffffffffffffffff", amount: order.amount })), { answer: IPN.notFound });
  assert.deepEqual(await handleIpn(db, cfg, ipnParams({ id: "not-an-order", amount: order.amount })), { answer: IPN.notFound });
  assert.deepEqual(await handleIpn(db, cfg, ipnParams({ id: order.id, amount: 1000 })), { answer: IPN.badAmount });
  const stripeOrder = await createOrder(db, { userId: uid, provider: "stripe", pack: PACKS[0] });
  assert.deepEqual(await handleIpn(db, cfg, ipnParams(stripeOrder)), { answer: IPN.notFound });
  assert.equal(await coins(), 0);
  // the visitor cancelled (24): recorded as failed, acknowledged with 00, nothing credited; a later "success" for it is refused
  assert.deepEqual(await handleIpn(db, cfg, ipnParams(order, { vnp_ResponseCode: "24", vnp_TransactionStatus: "02" })), { answer: IPN.ok, result: "failed" });
  assert.equal((await getOrder(db, order.id))!.status, "failed");
  assert.deepEqual(await handleIpn(db, cfg, ipnParams(order)), { answer: IPN.already });
  assert.equal(await coins(), 0);
});

test("routes: VNPAY is off until VNPAY_ENABLED=1 and both keys are set; checkout signs with our order; return redirects without crediting", async () => {
  assert.equal(vnpayConfig({ VNPAY_TMN_CODE: TMN, VNPAY_HASH_SECRET: SECRET }), null);
  assert.equal(vnpayConfig({ VNPAY_ENABLED: "1", VNPAY_TMN_CODE: TMN }), null);
  assert.equal(vnpayConfig({ VNPAY_ENABLED: "1", VNPAY_TMN_CODE: TMN, VNPAY_HASH_SECRET: SECRET })!.url, VNPAY_SANDBOX_URL);
  const user = { id: uid, email: `v${n}@x.test`, name: "", picture: "" };
  const off: any = { DB: db }, on: any = { DB: db, VNPAY_ENABLED: "1", VNPAY_TMN_CODE: TMN, VNPAY_HASH_SECRET: SECRET };
  const buy = (e: any) => handleBilling(new Request("https://tu-vi.test/api/me/checkout", { method: "POST", headers: { "x-tvbt": "1", "cf-connecting-ip": "198.51.100.7" }, body: JSON.stringify({ pack: "p150", provider: "vnpay", amount: 1 }) }), e, user);
  assert.equal((await buy(off)).status, 503);
  assert.equal((await handleBilling(new Request("https://tu-vi.test/api/vnpay/ipn?x=1"), off, null)).status, 404);
  const r = await buy(on), j = await r.json() as any;
  assert.equal(r.status, 200);
  const q = new URL(j.url).searchParams, order = (await getOrder(db, j.order))!;
  assert.equal(order.amount, PACKS[1].amount); assert.equal(order.user_id, uid); assert.equal(order.status, "pending");
  assert.equal(q.get("vnp_TxnRef"), order.id); assert.equal(q.get("vnp_Amount"), String(PACKS[1].amount * 100)); assert.equal(q.get("vnp_IpAddr"), "198.51.100.7");
  assert.equal(q.get("vnp_ReturnUrl"), "https://tu-vi.test/api/vnpay/return");
  assert.equal(await verifyVnpay(q, SECRET), true);
  // the visitor's browser comes back: a receipt redirect, no coins (only the IPN credits)
  const back = await handleBilling(new Request(`https://tu-vi.test/api/vnpay/return?${ipnParams(order)}`), on, null);
  assert.equal(back.status, 302); assert.equal(back.headers.get("location"), `/bien-nhan?order=${order.id}&vnp=00`);
  const forged = await handleBilling(new Request(`https://tu-vi.test/api/vnpay/return?${ipnParams(order, {}, "wrong")}`), on, null);
  assert.equal(forged.headers.get("location"), `/bien-nhan?order=${order.id}&vnp=bad`);
  assert.equal(await coins(), 0);
  // the IPN route answers VNPAY's JSON, and credits
  const ipn = await handleBilling(new Request(`https://tu-vi.test/api/vnpay/ipn?${ipnParams(order)}`), on, null);
  assert.equal(ipn.status, 200); assert.deepEqual(await ipn.json(), IPN.ok);
  assert.equal(await coins(), PACKS[1].coins);
  assert.deepEqual(await (await handleBilling(new Request(`https://tu-vi.test/api/vnpay/ipn?${ipnParams(order)}`), on, null)).json(), IPN.already);
});
