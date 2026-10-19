// POST /api/me/checkout (start a purchase) and POST /api/stripe/webhook (Stripe tells us it was paid).
import type { User } from "../auth/session.ts";
import { packById } from "./config.ts";
import { createCheckout, handleEvent, verifyWebhook, type Fetch } from "./stripe.ts";

export interface BillingEnv { DB?: D1Database; STRIPE_SECRET_KEY?: string; STRIPE_WEBHOOK_SECRET?: string }
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

export const isBillingPath = (p: string) => p === "/api/me/checkout" || p === "/api/stripe/webhook";

export async function handleBilling(request: Request, env: BillingEnv, user: User | null, f: Fetch = fetch): Promise<Response> {
  const path = new URL(request.url).pathname;
  if (!env.DB) return json({ detail: "not available" }, 503);

  if (path === "/api/stripe/webhook") {
    if (request.method !== "POST") return json({ detail: "POST only" }, 405);
    if (!env.STRIPE_WEBHOOK_SECRET) return json({ detail: "not configured" }, 503);
    const raw = await request.text();                                              // the signature covers the exact bytes
    if (!(await verifyWebhook(raw, request.headers.get("stripe-signature"), env.STRIPE_WEBHOOK_SECRET))) return json({ detail: "bad signature" }, 400);
    let event; try { event = JSON.parse(raw); } catch { return json({ detail: "bad json" }, 400); }
    const result = await handleEvent(env.DB, event);
    // "rejected" answers 200 on purpose: Stripe would retry a payment we will never accept; the mismatch is for a human to look at
    return json({ received: true, result });
  }

  // /api/me/checkout
  if (request.method !== "POST") return json({ detail: "POST only" }, 405);
  if (!user) return json({ detail: "sign in required" }, 401);
  if (request.headers.get("x-tvbt") !== "1") return json({ detail: "missing x-tvbt header" }, 403);
  if (!env.STRIPE_SECRET_KEY) return json({ detail: "payments are not configured" }, 503);
  const body = await request.json().catch(() => null) as { pack?: unknown } | null;
  const pack = packById(body?.pack);
  if (!pack) return json({ detail: "unknown pack" }, 400);
  try {
    const url = await createCheckout(f, env.STRIPE_SECRET_KEY, { userId: user.id, email: user.email, pack, origin: new URL(request.url).origin });
    return json({ url });
  } catch { return json({ detail: "could not start the payment" }, 502); }
}
