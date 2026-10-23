// Stripe over plain fetch (nothing to install in the Worker): create a Checkout Session, verify a webhook, credit coins once.
import { CURRENCY, packById, type Pack } from "./config.ts";
import { completeOrder, getOrder, isOrderId, type Order } from "./orders.ts";
import { grant, grantPass } from "./wallet.ts";

export type Fetch = (input: string, init?: RequestInit) => Promise<Response>;

const enc = new TextEncoder();
const hex = (b: ArrayBuffer) => [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, "0")).join("");

async function hmac(secret: string, msg: string): Promise<string> {
  const key = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return hex(await crypto.subtle.sign("HMAC", key, enc.encode(msg)));
}
const sameHex = (a: string, b: string) => { if (a.length !== b.length) return false; let d = 0; for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i); return d === 0; };

/** Checks the Stripe-Signature header (`t=<unix>,v1=<hmac of "<t>.<raw body>">`) against the raw body. Five minutes of tolerance. */
export async function verifyWebhook(rawBody: string, header: string | null, secret: string, now = Date.now(), toleranceSec = 300): Promise<boolean> {
  if (!header) return false;
  const parts = header.split(",").map(p => p.trim().split("="));
  const t = parts.find(p => p[0] === "t")?.[1], sigs = parts.filter(p => p[0] === "v1").map(p => p[1] ?? "");
  if (!t || !/^\d+$/.test(t) || Math.abs(now / 1000 - Number(t)) > toleranceSec) return false;
  const want = await hmac(secret, `${t}.${rawBody}`);
  return sigs.some(s => sameHex(s, want));
}

/** Creates a one-off payment Checkout Session for a pack and returns its hosted-page URL (and the session id). The return URLs come from
 *  the Worker's own origin. With an order (orders.ts) the price is the order's (after any discount) and the webhook checks against it. */
export async function createCheckout(f: Fetch, secretKey: string, o: { userId: string; email: string; pack: Pack; origin: string; order?: Pick<Order, "id" | "amount"> }): Promise<string> {
  return (await createCheckoutSession(f, secretKey, o)).url;
}
export async function createCheckoutSession(f: Fetch, secretKey: string, o: { userId: string; email: string; pack: Pack; origin: string; order?: Pick<Order, "id" | "amount"> }): Promise<{ url: string; id: string }> {
  const body = new URLSearchParams({
    mode: "payment", "payment_method_types[0]": "card", client_reference_id: o.userId, customer_email: o.email,
    success_url: o.order ? `${o.origin}/bien-nhan?order=${o.order.id}` : `${o.origin}/?paid=1`, cancel_url: o.order ? `${o.origin}/bang-gia?paid=0` : `${o.origin}/?paid=0`,
    "line_items[0][quantity]": "1", "line_items[0][price_data][currency]": CURRENCY, "line_items[0][price_data][unit_amount]": String(o.order?.amount ?? o.pack.amount),
    "line_items[0][price_data][product_data][name]": `${o.pack.coins} xu Thiên Bàn`,
    "metadata[pack]": o.pack.id, "metadata[user]": o.userId, ...(o.order ? { "metadata[order]": o.order.id } : {}),
  });
  const res = await f("https://api.stripe.com/v1/checkout/sessions", { method: "POST", headers: { authorization: `Bearer ${secretKey}`, "content-type": "application/x-www-form-urlencoded" }, body });
  if (!res.ok) throw new Error(`stripe ${res.status}`);
  const { url, id } = await res.json() as { url?: string; id?: string };
  if (!url) throw new Error("stripe returned no url");
  return { url, id: id ?? "" };
}

interface Session { id: string; payment_status?: string; amount_total?: number; currency?: string; client_reference_id?: string | null; metadata?: Record<string, string> }
export type WebhookResult = "credited" | "duplicate" | "ignored" | "rejected";

/** A paid Checkout session becomes coins, exactly once. Anything that does not match our own pack table is rejected, not credited. */
export async function handleEvent(db: D1Database, event: { type?: string; data?: { object?: Session } }, now = Date.now()): Promise<WebhookResult> {
  if (event.type !== "checkout.session.completed" && event.type !== "checkout.session.async_payment_succeeded") return "ignored";
  const s = event.data?.object;
  if (!s || s.payment_status !== "paid") return "ignored";                       // a delayed method completes later with its own event
  // a session made from an order (every session since orders exist): the order decides the coins and the amount, discount included
  if (s.metadata?.order !== undefined) {
    const order = isOrderId(s.metadata.order) ? await getOrder(db, s.metadata.order) : null;
    if (!order || order.provider !== "stripe" || order.user_id !== s.client_reference_id || s.currency !== order.currency || s.amount_total !== order.amount) return "rejected";
    return completeOrder(db, { ...order, provider_ref: s.id }, s.id, `stripe ${s.payment_status}`, now);
  }
  const pack = packById(s.metadata?.pack), userId = s.client_reference_id;
  if (!pack || !userId || s.currency !== CURRENCY || s.amount_total !== pack.amount) return "rejected";
  const user = await db.prepare("SELECT id FROM users WHERE id = ?").bind(userId).first();
  if (!user) return "rejected";
  const applied = await grant(db, userId, pack.coins, `stripe:${s.id}`, now);
  await db.prepare("INSERT OR IGNORE INTO payments (session_id, user_id, pack, coins, amount, currency, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)")
    .bind(s.id, userId, pack.id, pack.coins, pack.amount, CURRENCY, now).run();
  await grantPass(db, userId, `stripe:${s.id}`, now);                         // a top-up: the 30-day chat pass, once per session
  return applied ? "credited" : "duplicate";
}
