// Orders: one per purchase attempt, made before the visitor leaves for the payment page, and completed (coins credited) exactly once by
// the provider's signed callback. Also the wallet history and the receipt.
import { CURRENCY, discounted, periodOf, type Pack } from "./config.ts";
import { grantPass } from "./wallet.ts";

export type Provider = "stripe" | "vnpay";
export interface Order {
  id: string; user_id: string; provider: Provider; provider_ref: string; pack: string; coins: number; list_amount: number; amount: number;
  currency: string; discount_code: string; discount_pct: number; status: "pending" | "paid" | "failed"; detail: string; created_at: number; paid_at: number;
}

/** 20 hex characters: unguessable, and VNPAY's vnp_TxnRef accepts it (letters and digits only). */
export const newOrderId = () => [...crypto.getRandomValues(new Uint8Array(10))].map(x => x.toString(16).padStart(2, "0")).join("");
export const isOrderId = (s: unknown): s is string => typeof s === "string" && /^[0-9a-f]{20}$/.test(s);

export async function createOrder(db: D1Database, o: { userId: string; provider: Provider; pack: Pack; discount?: { code: string; percent: number } | null }, now = Date.now()): Promise<Order> {
  const id = newOrderId(), pct = o.discount?.percent ?? 0, amount = discounted(o.pack.amount, pct);
  await db.prepare("INSERT INTO orders (id, user_id, provider, pack, coins, list_amount, amount, currency, discount_code, discount_pct, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)")
    .bind(id, o.userId, o.provider, o.pack.id, o.pack.coins, o.pack.amount, amount, CURRENCY, o.discount?.code ?? "", pct, now).run();
  return (await getOrder(db, id))!;
}
export const getOrder = (db: D1Database, id: string) => db.prepare("SELECT * FROM orders WHERE id = ?").bind(id).first<Order>();
export const setProviderRef = (db: D1Database, id: string, ref: string) => db.prepare("UPDATE orders SET provider_ref = ? WHERE id = ? AND status = 'pending'").bind(ref, id).run();

/** The ledger ref that credits an order: what makes a repeated callback harmless. Stripe keeps its old form (session id). */
export const ledgerRefOf = (o: Pick<Order, "provider" | "provider_ref" | "id">) => o.provider === "stripe" ? `stripe:${o.provider_ref}` : `vnpay:${o.id}`;

export type CompleteResult = "credited" | "duplicate";

/** Credits a paid order, once. One D1 batch: the ledger row (unique ref), the coins (only if the row was new), the discount use (only if
 *  the coins went in), the order marked paid, and the `payments` record the admin page counts. The caller has already checked the
 *  provider's signature and that the amount paid equals `order.amount`. */
export async function completeOrder(db: D1Database, order: Order, providerRef: string, detail: string, now = Date.now()): Promise<CompleteResult> {
  const o = { ...order, provider_ref: order.provider_ref || providerRef }, ref = ledgerRefOf(o);
  await db.prepare("INSERT OR IGNORE INTO wallets (user_id) VALUES (?)").bind(o.user_id).run();
  const [led, upd] = await db.batch([
    db.prepare("INSERT OR IGNORE INTO ledger (user_id, kind, usage, delta, period, ref, created_at) VALUES (?, 'grant', ?, ?, ?, ?, ?)")
      .bind(o.user_id, `pack:${o.pack}`, o.coins, periodOf(now), ref, now),
    db.prepare("UPDATE wallets SET coins = coins + ?1, updated_at = ?2 WHERE user_id = ?3 AND changes() > 0").bind(o.coins, now, o.user_id),
    db.prepare("UPDATE promo_codes SET used = used + 1 WHERE code = ? AND changes() > 0").bind(o.discount_code),
    db.prepare("UPDATE orders SET status = 'paid', paid_at = ?, provider_ref = ?, detail = ? WHERE id = ? AND status <> 'paid'").bind(now, o.provider_ref, detail.slice(0, 200), o.id),
    db.prepare("INSERT OR IGNORE INTO payments (session_id, user_id, pack, coins, amount, currency, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)")
      .bind(o.provider === "stripe" ? o.provider_ref : `vnpay:${o.id}`, o.user_id, o.pack, o.coins, o.amount, o.currency, now),
  ]);
  const result: CompleteResult = (led.meta?.changes ?? 0) > 0 && (upd.meta?.changes ?? 0) > 0 ? "credited" : "duplicate";
  // every top-up opens (or extends) the 30-day chat pass; once per order, and a retried callback heals a pass that failed to land
  await grantPass(db, o.user_id, ref, now);
  return result;
}

/** A payment the provider reports as not completed (cancelled, declined). A paid order never goes back. */
export const failOrder = (db: D1Database, id: string, detail: string) =>
  db.prepare("UPDATE orders SET status = 'failed', detail = ? WHERE id = ? AND status = 'pending'").bind(detail.slice(0, 200), id).run();

// ---------- what the user sees ----------
export interface HistoryRow { id: number; kind: string; usage: string; delta: number; ref: string | null; at: number; order: string | null; amount: number | null; provider: string | null }

/** Every coin movement of the account, newest first: top-ups (with the order and the VND paid), gift codes, admin grants, coin spends and
 *  refunds. Free chat uses and chat-pass rows move no coins and are left out. */
export async function walletHistory(db: D1Database, userId: string, limit = 200): Promise<HistoryRow[]> {
  const { results } = await db.prepare(
    `SELECT l.id, l.kind, l.usage, l.delta, l.ref, l.created_at AS at, o.id AS "order", o.amount, o.provider
     FROM ledger l LEFT JOIN orders o ON o.user_id = l.user_id AND l.ref = o.provider || ':' || (CASE o.provider WHEN 'stripe' THEN o.provider_ref ELSE o.id END)
     WHERE l.user_id = ? AND l.kind NOT IN ('free_spend', 'refund_free', 'pass') ORDER BY l.id DESC LIMIT ?`).bind(userId, limit).all<HistoryRow>();
  return results;
}
export async function listOrders(db: D1Database, userId: string, limit = 50): Promise<Order[]> {
  return (await db.prepare("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT ?").bind(userId, limit).all<Order>()).results;
}

/** The fields a receipt shows; the order belongs to the asking account or nothing is returned. */
export function receiptOf(o: Order) {
  return { id: o.id, provider: o.provider, providerRef: o.provider_ref, pack: o.pack, coins: o.coins, listAmount: o.list_amount, amount: o.amount, currency: o.currency,
    discountCode: o.discount_code, discountPct: o.discount_pct, status: o.status, createdAt: o.created_at, paidAt: o.paid_at };
}

const vnd = (n: number) => `${n.toLocaleString("vi-VN")}đ`;
const PROVIDER_VI: Record<string, string> = { stripe: "Thẻ quốc tế (Stripe)", vnpay: "VNPAY" };

/** A receipt e-mail for a paid order, plain text and HTML. Sending needs a mail sender the owner sets up (see docs/PAYMENTS.md); the
 *  receipt page /bien-nhan shows the same content. The seller lines are left for the owner to fill. */
export function receiptEmail(o: Order, origin: string, to: { name?: string; email: string }) {
  const when = new Date(o.paid_at || o.created_at).toLocaleString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh" });
  const lines: Array<[string, string]> = [
    ["Mã đơn", o.id], ["Thời gian", when], ["Gói", `${o.coins} xu`], ["Giá niêm yết", vnd(o.list_amount)],
    ...(o.discount_pct ? [["Mã giảm giá", `${o.discount_code} (−${o.discount_pct}%)`] as [string, string]] : []),
    ["Số tiền đã thanh toán", vnd(o.amount)], ["Cổng thanh toán", PROVIDER_VI[o.provider] ?? o.provider], ...(o.provider_ref ? [["Mã giao dịch", o.provider_ref] as [string, string]] : []),
  ];
  const link = `${origin}/bien-nhan?order=${o.id}`;
  const esc = (s: string) => s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]!));
  const subject = `Biên nhận Thiên Bàn — đơn ${o.id}`;
  const text = [`Chào ${to.name || to.email},`, "", "Thiên Bàn đã nhận thanh toán của bạn. Số xu đã được cộng vào ví.", "",
    ...lines.map(([k, v]) => `${k}: ${v}`), "", `Xem biên nhận: ${link}`, "Chính sách hoàn tiền: " + `${origin}/chinh-sach-hoan-tien`, "",
    "[Tên đơn vị bán, mã số thuế, địa chỉ — chủ site điền]"].join("\n");
  const html = `<p>Chào ${esc(to.name || to.email)},</p><p>Thiên Bàn đã nhận thanh toán của bạn. Số xu đã được cộng vào ví.</p><table cellpadding="6" style="border-collapse:collapse">${lines.map(([k, v]) => `<tr><td style="color:#666">${esc(k)}</td><td><b>${esc(v)}</b></td></tr>`).join("")}</table><p><a href="${esc(link)}">Xem biên nhận</a> · <a href="${esc(origin)}/chinh-sach-hoan-tien">Chính sách hoàn tiền</a></p><p style="color:#666">[Tên đơn vị bán, mã số thuế, địa chỉ — chủ site điền]</p>`;
  return { to: to.email, subject, text, html };
}
