// Phase 2 money rules against a real local D1: the paywall cuts paid chapters on the server, unlocking spends coins once, gift and
// discount codes, Stripe orders with a discount, the wallet history, and the admin code routes.
import { test, before, after, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { getPlatformProxy } from "wrangler";
import { buyPlan, gateOutput, gateResponse, needs, preview, unlockedChapters } from "../paywall.ts";
import { createCode, redeemGift, checkDiscount, setActive } from "../codes.ts";
import { completeOrder, createOrder, getOrder, walletHistory, receiptEmail } from "../orders.ts";
import { handleEvent } from "../stripe.ts";
import { handleBilling, plansView } from "../route.ts";
import { getWallet, grant } from "../wallet.ts";
import { PACKS, PAID_CHAPTERS, PALACE_CHAPTERS, PLANS, PRICES_ARE_PLACEHOLDERS, discounted, planById } from "../config.ts";
import { handleAdmin } from "../../admin/route.ts";

let proxy: Awaited<ReturnType<typeof getPlatformProxy>>, db: D1Database, n = 0, uid = "", user: any;
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
  uid = `c${++n}`; user = { id: uid, email: `c${n}@x.test`, name: "", picture: "" };
  await db.prepare("INSERT INTO users (id, google_sub, email, created_at) VALUES (?, ?, ?, 1)").bind(uid, `cs${n}`, user.email).run();
});

const T = Date.UTC(2026, 9, 21, 5, 0);
const coins = async (u = uid) => (await getWallet(db, u, T)).coins;
const BIRTH = { year: 1990, month: 5, day: 17, hour: 10, minute: 30, gender: "male" }, FP = "1990-5-17-10-30-male";
const me = (path: string, body?: unknown, u: any = user, method = body === undefined ? "GET" : "POST") =>
  handleBilling(new Request(`https://tu-vi.test${path}`, { method, headers: { "x-tvbt": "1" }, body: body === undefined ? undefined : JSON.stringify(body) }), { DB: db, STRIPE_SECRET_KEY: "sk_test" } as any, u,
    (async () => new Response(JSON.stringify({ url: "https://checkout.stripe.com/c/pay/cs_x", id: `cs_${Math.random().toString(36).slice(2)}` }))) as any, T);

// a prose chapter as /api/interpret mode "prose" serves it: paragraphs of traced sentences, evidence, advice
const sent = (t: string, rules: string[] = []) => ({ text: t, trace: { move: "ANCHOR", basis: "sach", rules, concepts: [`k_${t}`], cites: [] } });
const para = (i: number) => ({ role: "core", sentences: [sent(`P${i}a.`, [`R${i}`]), sent(`P${i}b.`)], text: `P${i}a. P${i}b.` });
const chapter = (id: string, nPara = 5) => ({
  engine: "e", kbVersion: "k", chapter: id, palace: "X", schema: "S", order: [], draft: true, pass: true,
  paragraphs: Array.from({ length: nPara }, (_, i) => para(i)), text: "all the text", issues: [{ level: "warn", code: "x", msg: "secret detail" }], metrics: { secret: 1 },
  advice: { strengths: ["a"], actions: ["b"] },
  evidence: { resolved: [1], tensions: [1], unused: ["R9"], rules: Object.fromEntries(Array.from({ length: nPara }, (_, i) => [`R${i}`, { reading: `reading ${i}`, cites: [] }])), concepts: { "k_P0a.": "c0", "k_P4a.": "c4" }, divergences: [{ note: "n", rules: [] }], limits: ["l"] },
});

test("config: one source of prices, all marked as placeholders; plans open only paid chapters; discount rounding has a floor", () => {
  assert.equal(PRICES_ARE_PLACEHOLDERS, true);
  const v = plansView({} as any);
  assert.equal(v.placeholder, true); assert.match(v.placeholderLabel, /GIÁ TẠM/);
  assert.deepEqual(v.providers, { stripe: false, vnpay: false }); assert.equal(v.paywall, false);
  assert.equal(plansView({ TVBT_PAYWALL: "1" } as any).paywall, true);
  for (const p of PLANS) if (p.chapters !== "one") for (const c of p.chapters) assert.ok((PAID_CHAPTERS as readonly string[]).includes(c), `${p.id}: ${c}`);
  assert.ok(!(PAID_CHAPTERS as readonly string[]).includes("menh"));
  assert.equal(discounted(49000, 0), 49000); assert.equal(discounted(129000, 10), 116000); assert.equal(discounted(49000, 90), 10000); assert.equal(discounted(8000, 50), 8000);
  assert.deepEqual(needs("gia_dao"), ["phu_mau", "huynh_de", "tu_tuc"]); assert.deepEqual(needs("menh"), []); assert.deepEqual(needs("van_han"), ["van_han"]);
});

test("preview: two paragraphs of a long chapter, one of a short one, first sentences of a one-paragraph chapter, never all of it", () => {
  assert.equal(preview(chapter("x", 5).paragraphs).length, 2);
  assert.equal(preview(chapter("x", 3).paragraphs).length, 1);
  const one = preview(chapter("x", 1).paragraphs);
  assert.equal(one.length, 1); assert.equal(one[0].sentences.length, 1); assert.equal(one[0].text, "P0a.");
  assert.deepEqual(preview([{ sentences: [sent("only")] }]), []);
  assert.deepEqual(preview([]), []);
});

test("paywall: a locked chapter leaves only its preview and the rules behind it; advice, issues, other evidence and the full text are gone", () => {
  const out = gateOutput({ engine: "e", chapters: [chapter("menh"), chapter("cong_danh"), chapter("van_han", 12), { ...chapter("bat_tu"), chapters: { "nhat-chu": [para(0)], "su-nghiep": [para(3)] } }], pass: true }, { signedIn: false, open: new Set() });
  const [menh, cd, vh, bt] = out.chapters;
  assert.equal(menh.paragraphs.length, 5); assert.ok(menh.advice); assert.equal(menh.locked, undefined);          // free chapter untouched
  assert.equal(cd.paragraphs.length, 2); assert.equal(cd.text, "P0a. P0b.\n\nP1a. P1b.");
  assert.equal(cd.advice, undefined); assert.deepEqual(cd.issues, []); assert.equal(cd.metrics, undefined);
  assert.deepEqual(Object.keys(cd.evidence.rules).sort(), ["R0", "R1"]); assert.deepEqual(cd.evidence.concepts, { "k_P0a.": "c0" });
  assert.deepEqual(cd.evidence.divergences, []); assert.deepEqual(cd.evidence.unused, []);
  assert.ok(!JSON.stringify(cd).includes("P4a") && !JSON.stringify(cd).includes("reading 4") && !JSON.stringify(cd).includes("all the text"));
  assert.deepEqual(cd.locked.plans.map((p: any) => p.id), ["chuong", "van_han", "cung12", "tron_bo"].filter(id => planById(id)!.chapters === "one" || (planById(id)!.chapters as readonly string[]).includes("cong_danh")));
  assert.equal(cd.locked.plans.find((p: any) => p.id === "chuong").chapter, "cong_danh");
  assert.equal(cd.locked.signedIn, false); assert.deepEqual([cd.locked.shown, cd.locked.total], [2, 5]);
  assert.equal(vh.paragraphs.length, 2); assert.ok(vh.locked.plans.some((p: any) => p.id === "van_han"));
  assert.deepEqual(Object.keys(bt.chapters), ["nhat-chu"]); assert.equal(bt.chapters["nhat-chu"].length, 2);    // other Bát Tự chapters are not sent
  // opened: whole again, marked
  const open = gateOutput(chapter("cong_danh"), { signedIn: true, open: new Set(["cong_danh"]) });
  assert.equal(open.paragraphs.length, 5); assert.equal(open.unlocked, true); assert.ok(open.advice);
  // a group chapter (evidence mode) needs all of its palaces
  assert.ok(gateOutput(chapter("gia_dao"), { signedIn: true, open: new Set(["phu_mau", "huynh_de"]) }).locked);
  assert.equal(gateOutput(chapter("gia_dao"), { signedIn: true, open: new Set(["phu_mau", "huynh_de", "tu_tuc"]) }).locked, undefined);
});

test("buying a plan: refused without coins (nothing charged, nothing opened), charged once, double clicks and repeats are free", async () => {
  const r0 = await buyPlan(db, uid, FP, "cung12", undefined, T);
  assert.deepEqual(r0, { ok: false, reason: "insufficient", need: planById("cung12")!.coins });
  assert.equal((await unlockedChapters(db, uid, FP)).size, 0);
  assert.equal((await db.prepare("SELECT COUNT(*) AS n FROM ledger WHERE user_id = ?").bind(uid).first<{ n: number }>())!.n, 0);
  await grant(db, uid, 200, "t", T);
  const [a, b] = await Promise.all([buyPlan(db, uid, FP, "cung12", undefined, T), buyPlan(db, uid, FP, "cung12", undefined, T)]);
  assert.equal([a, b].filter(r => r.ok && r.charged > 0).length, 1);                 // two parallel clicks: one charge
  assert.equal(await coins(), 200 - planById("cung12")!.coins);
  assert.deepEqual([...await unlockedChapters(db, uid, FP)].sort(), [...PALACE_CHAPTERS].sort());
  assert.deepEqual(await buyPlan(db, uid, FP, "cung12", undefined, T), { ok: true, charged: 0, chapters: [...PALACE_CHAPTERS], already: true });
  // one chapter of another chart; a chapter must be named for "chuong", and must be a paid one
  assert.deepEqual(await buyPlan(db, uid, "other-fp", "chuong", undefined, T), { ok: false, reason: "bad_plan" });
  assert.deepEqual(await buyPlan(db, uid, "other-fp", "chuong", "menh", T), { ok: false, reason: "bad_plan" });
  assert.deepEqual(await buyPlan(db, uid, "other-fp", "nope", undefined, T), { ok: false, reason: "bad_plan" });
  const one = await buyPlan(db, uid, "other-fp", "chuong", "van_han", T);
  assert.ok(one.ok && one.charged === planById("chuong")!.coins);
  assert.deepEqual([...await unlockedChapters(db, uid, "other-fp")], ["van_han"]);
  assert.equal((await unlockedChapters(db, uid, FP)).has("van_han"), false);        // per chart
  // opened by someone else's purchase? never: unlocks belong to the buyer
  const other = `c${n}x`; await db.prepare("INSERT INTO users (id, google_sub, email, created_at) VALUES (?, ?, ?, 1)").bind(other, `${other}s`, `${other}@x.test`).run();
  assert.equal((await unlockedChapters(db, other, FP)).size, 0);
});

test("unlock route and gated response: the server decides, per signed-in account and chart", async () => {
  assert.equal((await me("/api/me/unlock", { birth: BIRTH, plan: "van_han" }, null)).status, 401);
  assert.equal((await me("/api/me/unlock", { birth: { year: "x" }, plan: "van_han" })).status, 400);
  const poor = await me("/api/me/unlock", { birth: BIRTH, plan: "van_han" });
  assert.equal(poor.status, 402); assert.equal(((await poor.json()) as any).need, planById("van_han")!.coins);
  const served = () => new Response(JSON.stringify({ chapters: [chapter("menh"), chapter("van_han"), chapter("tai_bach")] }), { headers: { "content-type": "application/json" } });
  const gated = async (body: unknown, u: any) => (await (await gateResponse(served(), body, db, u)).json() as any).chapters;
  let [, vh, tb] = await gated({ ...BIRTH, chapter: "all", mode: "prose" }, user);
  assert.ok(vh.locked && tb.locked); assert.equal(vh.locked.signedIn, true);
  await grant(db, uid, 100, "t2", T);
  const ok = await me("/api/me/unlock", { birth: { ...BIRTH, to_year: 2026, chapter: "all" }, plan: "van_han" });
  const j = await ok.json() as any;
  assert.equal(ok.status, 200); assert.equal(j.charged, planById("van_han")!.coins); assert.deepEqual(j.open, ["van_han"]); assert.equal(j.wallet.coins, 100 - planById("van_han")!.coins);
  [, vh, tb] = await gated({ ...BIRTH, chapter: "all", mode: "prose", to_year: 2026 }, user);
  assert.equal(vh.paragraphs.length, 5); assert.ok(tb.locked);
  // signed out, another account, another chart, or a body that is not a birth record: still locked
  assert.ok((await gated({ ...BIRTH }, null))[1].locked);
  assert.ok((await gated({ ...BIRTH, day: 18 }, user))[1].locked);
  assert.ok((await gated({ nonsense: true }, user))[1].locked);
  const res = await gateResponse(served(), BIRTH, db, user);
  assert.equal(res.headers.get("cache-control"), "private, no-store");
  // an error from the engine passes through untouched
  const err = new Response("{}", { status: 502 });
  assert.equal(await gateResponse(err, BIRTH, db, user), err);
});

test("gift codes: credited once per account, capped by max uses, refused when expired or switched off", async () => {
  const made = await createCode(db, { kind: "gift", code: "tet-2027", coins: 25, max_uses: 2, note: "Tết" }, "admin@x.test", T);
  assert.ok(made.ok); assert.equal(made.ok && made.code.code, "TET-2027");
  assert.deepEqual(await createCode(db, { kind: "gift", code: "TET-2027", coins: 5 }, "a", T), { ok: false, detail: "this code already exists" });
  assert.equal((await redeemGift(db, uid, " tet-2027 ", T)).ok, true);
  assert.equal(await coins(), 25);
  assert.deepEqual(await redeemGift(db, uid, "TET-2027", T), { ok: false, reason: "already" });
  assert.equal(await coins(), 25);
  // two more accounts race for the one use left: exactly one wins
  const others = [`${uid}a`, `${uid}b`];
  for (const o of others) await db.prepare("INSERT INTO users (id, google_sub, email, created_at) VALUES (?, ?, ?, 1)").bind(o, `${o}s`, `${o}@x.test`).run();
  const rs = await Promise.all(others.map(o => redeemGift(db, o, "TET-2027", T)));
  assert.equal(rs.filter(r => r.ok).length, 1); assert.deepEqual(rs.find(r => !r.ok), { ok: false, reason: "used_up" });
  assert.equal((await coins(others[0])) + (await coins(others[1])), 25);
  assert.equal((await db.prepare("SELECT used FROM promo_codes WHERE code = 'TET-2027'").first<{ used: number }>())!.used, 2);
  // expired, inactive, unknown, discount code used as a gift, malformed
  await createCode(db, { kind: "gift", code: "OLD-1", coins: 5, expires: "2026-10-20" }, "a", Date.UTC(2026, 9, 1));
  assert.deepEqual(await redeemGift(db, uid, "OLD-1", T), { ok: false, reason: "expired" });
  await createCode(db, { kind: "gift", code: "OFF-1", coins: 5 }, "a", T); await setActive(db, "OFF-1", false);
  assert.deepEqual(await redeemGift(db, uid, "OFF-1", T), { ok: false, reason: "invalid" });
  await createCode(db, { kind: "discount", code: "DISC-1", percent: 10 }, "a", T);
  assert.deepEqual(await redeemGift(db, uid, "DISC-1", T), { ok: false, reason: "invalid" });
  assert.deepEqual(await redeemGift(db, uid, "NOPE-NOPE", T), { ok: false, reason: "invalid" });
  assert.deepEqual(await redeemGift(db, uid, "x'; DROP", T), { ok: false, reason: "invalid" });
  assert.equal(await coins(), 25);
  // through the route: Vietnamese message on failure, wallet on success
  await createCode(db, { kind: "gift", code: "ROUTE-1", coins: 7 }, "a", T);
  const ok = await me("/api/me/redeem", { code: "route-1" }); assert.equal(ok.status, 200); assert.equal(((await ok.json()) as any).wallet.coins, 32);
  const again = await me("/api/me/redeem", { code: "route-1" }); assert.equal(again.status, 400); assert.match(((await again.json()) as any).detail, /đã dùng/);
  assert.equal((await me("/api/me/redeem", { code: "ROUTE-1" }, null)).status, 401);
});

test("code validation on create", async () => {
  const bad = async (b: any) => { const r = await createCode(db, b, "a", T); assert.equal(r.ok, false, JSON.stringify(b)); };
  await bad(null); await bad({ kind: "free" }); await bad({ kind: "discount", percent: 0 }); await bad({ kind: "discount", percent: 95 });
  await bad({ kind: "gift", coins: 0 }); await bad({ kind: "gift", coins: 1.5 }); await bad({ kind: "gift", coins: 5, max_uses: 0 });
  await bad({ kind: "gift", coins: 5, expires: "tomorrow" }); await bad({ kind: "gift", coins: 5, expires: "2020-01-01" }); await bad({ kind: "gift", coins: 5, code: "a b" });
  const auto = await createCode(db, { kind: "gift", coins: 5 }, "a", T);
  assert.ok(auto.ok && /^QUA-[A-HJ-NP-Z2-9]{10}$/.test(auto.code.code));
});

test("discount codes: Stripe charges the discounted price, the webhook checks it against the order, the use counts only once paid", async () => {
  await createCode(db, { kind: "discount", code: "GIAM20", percent: 20, max_uses: 5 }, "a", T);
  const q = await me("/api/me/quote", { code: "giam20" }), qj = await q.json() as any;
  assert.equal(q.status, 200); assert.deepEqual(qj.prices, Object.fromEntries(PACKS.map(p => [p.id, discounted(p.amount, 20)])));
  assert.equal((await me("/api/me/quote", { code: "NOPE-1" })).status, 400);
  const r = await me("/api/me/checkout", { pack: "p150", code: "GIAM20" }), j = await r.json() as any;
  assert.equal(r.status, 200);
  const order = (await getOrder(db, j.order))!;
  assert.deepEqual([order.amount, order.list_amount, order.discount_code, order.discount_pct, order.status], [discounted(PACKS[1].amount, 20), PACKS[1].amount, "GIAM20", 20, "pending"]);
  assert.ok(order.provider_ref.startsWith("cs_"));
  assert.equal((await db.prepare("SELECT used FROM promo_codes WHERE code = 'GIAM20'").first<{ used: number }>())!.used, 0);   // not paid yet
  const ev = (over: Record<string, unknown> = {}) => ({ type: "checkout.session.completed", data: { object: {
    id: order.provider_ref, payment_status: "paid", amount_total: order.amount, currency: "vnd", client_reference_id: uid, metadata: { pack: "p150", order: order.id }, ...over } } });
  assert.equal(await handleEvent(db, ev({ amount_total: PACKS[1].amount + 1 }) as any, T), "rejected");          // not what the order says
  assert.equal(await handleEvent(db, ev({ client_reference_id: "someone-else" }) as any, T), "rejected");
  assert.equal(await handleEvent(db, ev({ metadata: { pack: "p150", order: "ffffffffffffffffffff" } }) as any, T), "rejected");
  assert.equal(await coins(), 0);
  assert.equal(await handleEvent(db, ev() as any, T), "credited");
  assert.equal(await handleEvent(db, ev() as any, T), "duplicate");
  assert.equal(await coins(), PACKS[1].coins);
  assert.equal((await getOrder(db, order.id))!.status, "paid");
  assert.equal((await db.prepare("SELECT used FROM promo_codes WHERE code = 'GIAM20'").first<{ used: number }>())!.used, 1);
  // once per account: after a paid order the same code is refused for this account
  assert.deepEqual(await checkDiscount(db, uid, "GIAM20", T), { ok: false, reason: "already" });
  assert.equal((await me("/api/me/checkout", { pack: "p50", code: "GIAM20" })).status, 400);
  // the receipt belongs to its account only
  const rc = await me(`/api/me/orders/${order.id}`), rj = await rc.json() as any;
  assert.equal(rc.status, 200); assert.equal(rj.order.amount, order.amount); assert.equal(rj.order.discountCode, "GIAM20");
  assert.equal((await me(`/api/me/orders/${order.id}`, undefined, { ...user, id: "intruder" })).status, 404);
  assert.equal((await me(`/api/me/orders/not-an-id`)).status, 404);
});

test("wallet history: top-ups with their VND amount and receipt, gifts, unlocks; free chats left out", async () => {
  const order = await createOrder(db, { userId: uid, provider: "vnpay", pack: PACKS[0] }, T);
  assert.equal(await completeOrder(db, order, "TXN1", "vnp 00/00", T), "credited");
  await createCode(db, { kind: "gift", code: "HIST-1", coins: 10 }, "a", T); await redeemGift(db, uid, "HIST-1", T);
  await buyPlan(db, uid, FP, "van_han", undefined, T + 1);
  await db.prepare("INSERT INTO ledger (user_id, kind, usage, delta, period, created_at) VALUES (?, 'free_spend', 'chat', 0, '2026-10', ?)").bind(uid, T).run();
  const h = await walletHistory(db, uid);
  assert.deepEqual(h.map(x => [x.kind, x.delta]), [["coin_spend", -planById("van_han")!.coins], ["gift", 10], ["grant", PACKS[0].coins]]);
  assert.equal(h[2].order, order.id); assert.equal(h[2].amount, order.amount); assert.equal(h[2].provider, "vnpay");
  assert.equal(h[0].usage, "unlock:van_han");
  const r = await me("/api/me/wallet/history"), j = await r.json() as any;
  assert.equal(r.status, 200); assert.equal(j.history.length, 3); assert.equal(j.orders[0].status, "paid"); assert.equal(j.wallet.coins, PACKS[0].coins + 10 - planById("van_han")!.coins);
  // the receipt e-mail says what was paid and leaves the seller lines for the owner
  const mail = receiptEmail((await getOrder(db, order.id))!, "https://tu-vi.test", { email: user.email });
  assert.match(mail.subject, new RegExp(order.id)); assert.match(mail.text, /49\.000đ/); assert.match(mail.text, /chủ site điền/); assert.match(mail.html, /bien-nhan\?order=/);
});

test("admin code routes: 404 for everyone but admins; admins create, list and switch codes off, and see orders", async () => {
  const env: any = { DB: db, ADMIN_EMAILS: "boss@x.test" };
  const boss = { id: uid, email: "boss@x.test", name: "", picture: "" };
  const call = (path: string, u: any, body?: unknown) => handleAdmin(new Request(`https://x.test${path}`, { method: body === undefined ? "GET" : "POST", headers: { "x-tvbt": "1" }, body: body === undefined ? undefined : JSON.stringify(body) }), env, u);
  assert.equal((await call("/api/admin/codes", user)).status, 404);
  assert.equal((await call("/api/admin/codes", null, { kind: "gift", coins: 5 })).status, 404);
  assert.equal((await call("/api/admin/orders", user)).status, 404);
  const made = await call("/api/admin/codes", boss, { kind: "discount", code: "ADM-10", percent: 10, max_uses: 3 });
  assert.equal(made.status, 200); assert.equal(((await made.json()) as any).code.created_by, "boss@x.test");
  assert.equal((await call("/api/admin/codes", boss, { kind: "discount", percent: 500 })).status, 400);
  const list = await (await call("/api/admin/codes", boss)).json() as any;
  assert.ok(list.codes.some((c: any) => c.code === "ADM-10"));
  assert.equal((await call("/api/admin/codes/adm-10", boss, { active: false })).status, 200);
  assert.deepEqual(await checkDiscount(db, uid, "ADM-10", T), { ok: false, reason: "invalid" });
  assert.equal((await call("/api/admin/codes/NOPE-9", boss, { active: true })).status, 404);
  assert.equal((await call("/api/admin/codes/ADM-10", boss, { active: "yes" })).status, 400);
  assert.equal((await call("/api/admin/orders", boss)).status, 200);
});

test("before migration 0007 (no orders table) Stripe checkout still works the old way, and VNPAY or a discount code cannot start", async () => {
  const noTable = { prepare: () => ({ bind: () => ({ run: async () => { throw new Error("D1_ERROR: no such table: orders"); }, first: async () => { throw new Error("D1_ERROR: no such table"); } }) }) } as any;
  const sent: URLSearchParams[] = [];
  const stripe = (async (_u: string, init?: RequestInit) => { sent.push(new URLSearchParams(String(init!.body))); return new Response(JSON.stringify({ url: "https://checkout.stripe.com/c/pay/cs_old", id: "cs_old" })); }) as any;
  const call = (body: unknown, env: any) => handleBilling(new Request("https://tu-vi.test/api/me/checkout", { method: "POST", headers: { "x-tvbt": "1" }, body: JSON.stringify(body) }), { DB: noTable, ...env }, user, stripe, T);
  const r = await call({ pack: "p50" }, { STRIPE_SECRET_KEY: "sk" });
  assert.equal(r.status, 200); assert.deepEqual(await r.json(), { url: "https://checkout.stripe.com/c/pay/cs_old" });
  assert.equal(sent[0].get("success_url"), "https://tu-vi.test/?paid=1"); assert.equal(sent[0].get("metadata[order]"), null);
  assert.equal(sent[0].get("line_items[0][price_data][unit_amount]"), String(PACKS[0].amount));
  assert.equal((await call({ pack: "p50", code: "GIAM20" }, { STRIPE_SECRET_KEY: "sk" })).status, 503);
  assert.equal(sent.length, 1);
});
