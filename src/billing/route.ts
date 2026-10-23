// Billing routes.
//   GET  /api/plans                public: the reading tiers, packages, coin packs, which payment methods are on
//   POST /api/me/checkout          start a purchase {pack, provider?: "stripe" | "vnpay", code?}: makes an order, answers {url, order}
//   POST /api/me/quote             every pack's price with a discount code {code}
//   POST /api/me/redeem            redeem a gift code {code}
//   POST /api/me/unlock            open the Đọc sâu part of report chapters with coins {birth, plan, chapter?}
//   GET  /api/me/wallet/history    coin movements and orders
//   GET  /api/me/orders/<id>       one order of the signed-in account (the receipt page)
//   POST /api/stripe/webhook       Stripe says a Checkout session was paid
//   GET  /api/vnpay/ipn            VNPAY's server reports a payment result (the only VNPAY path that credits coins)
//   GET  /api/vnpay/return         the visitor's browser comes back from VNPAY; redirected to the receipt page
import type { User } from "../auth/session.ts";
import { cleanReq } from "../auth/charts.ts";
import { CHAPTER_TITLES, COSTS, DEEP_CHAPTERS, FREE_MESSAGES_PER_DAY, PACKS, PLACEHOLDER_LABEL, PLANS, PRICES_ARE_PLACEHOLDERS, RETIRED_PLAN_NAMES, TOPUP_CHAT, discounted, packById } from "./config.ts";
import { CODE_PROBLEM_VI, checkDiscount, redeemGift } from "./codes.ts";
import { createOrder, getOrder, isOrderId, listOrders, receiptOf, setProviderRef, walletHistory } from "./orders.ts";
import { buyPlan, unlockedChapters } from "./paywall.ts";
import { createCheckoutSession, handleEvent, verifyWebhook, type Fetch } from "./stripe.ts";
import { createPaymentUrl, handleIpn, verifyVnpay, vnpayConfig, IPN, type VnpayEnv } from "./vnpay.ts";
import { getWallet } from "./wallet.ts";

export interface BillingEnv extends VnpayEnv { DB?: D1Database; STRIPE_SECRET_KEY?: string; STRIPE_WEBHOOK_SECRET?: string; TVBT_PAYWALL?: string }
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
const redirect = (to: string) => new Response(null, { status: 302, headers: { location: to, "cache-control": "no-store" } });

const ME = new Set(["/api/me/checkout", "/api/me/quote", "/api/me/redeem", "/api/me/unlock", "/api/me/wallet/history"]);
export const isBillingPath = (p: string) => p === "/api/plans" || ME.has(p) || p.startsWith("/api/me/orders/")
  || p === "/api/stripe/webhook" || p === "/api/vnpay/ipn" || p === "/api/vnpay/return";

export const paywallOn = (env: BillingEnv) => env.TVBT_PAYWALL === "1";

/** What the pricing page and the lock cards show. Everything here comes from config.ts. */
export function plansView(env: BillingEnv) {
  return {
    placeholder: PRICES_ARE_PLACEHOLDERS, placeholderLabel: PLACEHOLDER_LABEL, paywall: paywallOn(env),
    plans: PLANS.map(p => ({ id: p.id, name: p.name, coins: p.coins, blurb: p.blurb, chapters: p.chapters === "one" ? "one" : [...p.chapters] })),
    retiredPlans: RETIRED_PLAN_NAMES, packs: PACKS, costs: COSTS, freeMessagesPerDay: FREE_MESSAGES_PER_DAY, topupChat: TOPUP_CHAT,
    // guests read the first third of each chapter's main reading, members all of it; the Đọc sâu part of these chapters is opened with xu
    tiers: { guestShare: "1/3", deepChapters: [...DEEP_CHAPTERS], titles: CHAPTER_TITLES },
    providers: { stripe: !!env.STRIPE_SECRET_KEY, vnpay: !!vnpayConfig(env) },
  };
}

export async function handleBilling(request: Request, env: BillingEnv, user: User | null, f: Fetch = fetch, now = Date.now()): Promise<Response> {
  const url = new URL(request.url), path = url.pathname;
  if (path === "/api/plans") return json(plansView(env));
  if (!env.DB) return json({ detail: "not available" }, 503);
  const db = env.DB;

  if (path === "/api/stripe/webhook") {
    if (request.method !== "POST") return json({ detail: "POST only" }, 405);
    if (!env.STRIPE_WEBHOOK_SECRET) return json({ detail: "not configured" }, 503);
    const raw = await request.text();                                              // the signature covers the exact bytes
    if (!(await verifyWebhook(raw, request.headers.get("stripe-signature"), env.STRIPE_WEBHOOK_SECRET))) return json({ detail: "bad signature" }, 400);
    let event; try { event = JSON.parse(raw); } catch { return json({ detail: "bad json" }, 400); }
    const result = await handleEvent(db, event);
    // "rejected" answers 200 on purpose: Stripe would retry a payment we will never accept; the mismatch is for a human to look at
    return json({ received: true, result });
  }

  if (path === "/api/vnpay/ipn") {
    const cfg = vnpayConfig(env);
    if (!cfg) return json({ detail: "not found" }, 404);
    try { return json((await handleIpn(db, cfg, url.searchParams, now)).answer); } catch { return json(IPN.error); }
  }
  if (path === "/api/vnpay/return") {
    const cfg = vnpayConfig(env), id = url.searchParams.get("vnp_TxnRef") ?? "";
    if (!cfg || !isOrderId(id)) return redirect("/bang-gia");
    const ok = await verifyVnpay(url.searchParams, cfg.hashSecret);
    // the receipt page reads the order itself (paid only once the IPN arrived); these two only pick the message while it waits
    return redirect(`/bien-nhan?order=${id}&vnp=${ok ? encodeURIComponent(url.searchParams.get("vnp_ResponseCode") ?? "") : "bad"}`);
  }

  // ---------- the signed-in account ----------
  if (!user) return json({ detail: "sign in required" }, 401);
  if (request.method !== "GET" && request.headers.get("x-tvbt") !== "1") return json({ detail: "missing x-tvbt header" }, 403);

  if (path === "/api/me/wallet/history") {
    if (request.method !== "GET") return json({ detail: "GET only" }, 405);
    const [wallet, history, orders] = await Promise.all([getWallet(db, user.id, now), walletHistory(db, user.id), listOrders(db, user.id)]);
    return json({ wallet, history, orders: orders.map(receiptOf) });
  }
  const om = path.match(/^\/api\/me\/orders\/([0-9a-f]{20})$/);
  if (om) {
    const o = await getOrder(db, om[1]);
    if (!o || o.user_id !== user.id) return json({ detail: "no such order" }, 404);
    return json({ order: receiptOf(o), wallet: await getWallet(db, user.id, now) });
  }
  if (path.startsWith("/api/me/orders/")) return json({ detail: "no such order" }, 404);
  if (request.method !== "POST") return json({ detail: "POST only" }, 405);
  const body = await request.json().catch(() => null) as Record<string, unknown> | null;

  if (path === "/api/me/redeem") {
    const r = await redeemGift(db, user.id, body?.code, now);
    if (!r.ok) return json({ detail: CODE_PROBLEM_VI[r.reason], reason: r.reason }, 400);
    return json({ ok: true, coins: r.coins, wallet: await getWallet(db, user.id, now) });
  }

  if (path === "/api/me/unlock") {
    const birth = cleanReq(body?.birth);
    if (!birth) return json({ detail: "body must be {birth, plan, chapter?}" }, 400);
    const r = await buyPlan(db, user.id, birth.fp, body?.plan, body?.chapter, now);
    const wallet = await getWallet(db, user.id, now);
    if (!r.ok) return r.reason === "insufficient" ? json({ detail: "not enough coins", need: r.need, wallet }, 402) : json({ detail: "unknown plan or chapter" }, 400);
    return json({ ...r, open: [...await unlockedChapters(db, user.id, birth.fp)], wallet });
  }

  let discount: { code: string; percent: number } | null = null;
  if (body?.code) {
    const d = await checkDiscount(db, user.id, body.code, now).catch(() => null);
    if (!d) return json({ detail: "discount codes are not available yet" }, 503);
    if (!d.ok) return json({ detail: CODE_PROBLEM_VI[d.reason], reason: d.reason }, 400);
    discount = { code: d.code, percent: d.percent };
  }
  // every pack's price with the code, as checkout would charge it
  if (path === "/api/me/quote") return json({ discount, prices: Object.fromEntries(PACKS.map(p => [p.id, discounted(p.amount, discount?.percent ?? 0)])) });
  const pack = packById(body?.pack);
  if (!pack) return json({ detail: "unknown pack" }, 400);

  // /api/me/checkout
  const provider = body?.provider === "vnpay" ? "vnpay" : "stripe", origin = url.origin;
  if (provider === "vnpay") {
    const cfg = vnpayConfig(env);
    if (!cfg) return json({ detail: "VNPAY is not enabled" }, 503);
    const order = await createOrder(db, { userId: user.id, provider, pack, discount }, now);
    const payUrl = await createPaymentUrl(cfg, { order, returnUrl: `${origin}/api/vnpay/return`, ip: request.headers.get("cf-connecting-ip") ?? "", now });
    return json({ url: payUrl, order: order.id });
  }
  if (!env.STRIPE_SECRET_KEY) return json({ detail: "payments are not configured" }, 503);
  // before migration 0007 there is no orders table: Stripe keeps working the old way (list price, webhook credits by pack)
  const order = await createOrder(db, { userId: user.id, provider, pack, discount }, now).catch(() => null);
  if (!order && discount) return json({ detail: "discount codes are not available yet" }, 503);    // never charge full price for a discounted quote
  try {
    const s = await createCheckoutSession(f, env.STRIPE_SECRET_KEY, { userId: user.id, email: user.email, pack, origin, order: order ?? undefined });
    if (order && s.id) await setProviderRef(db, order.id, s.id);
    return json({ url: s.url, ...(order ? { order: order.id } : {}) });
  } catch { return json({ detail: "could not start the payment" }, 502); }
}
