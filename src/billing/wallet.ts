// Atomic spending. Every state change is one conditional UPDATE (so two parallel requests can never overspend) batched with its
// ledger row via changes(), which is 0 when the UPDATE did not apply. D1 runs a batch as a single transaction.
import { COSTS, FREE_MESSAGES_PER_MONTH, FREE_USES, nextResetAt, periodOf, type Usage } from "./config.ts";

export type SpendResult =
  | { ok: true; source: "free" | "coin"; ref: number }
  | { ok: false; reason: "insufficient" };

export interface WalletView {
  coins: number;
  free: { limit: number; used: number; remaining: number; period: string; resetsAt: number };
  costs: typeof COSTS;
}

const changed = (r: D1Result) => (r.meta?.changes ?? 0) > 0;
const ensure = (db: D1Database, userId: string) =>
  db.prepare("INSERT OR IGNORE INTO wallets (user_id) VALUES (?)").bind(userId).run();

export async function getWallet(db: D1Database, userId: string, now = Date.now()): Promise<WalletView> {
  await ensure(db, userId);
  const w = await db.prepare("SELECT coins, free_period, free_used FROM wallets WHERE user_id = ?").bind(userId).first<{ coins: number; free_period: string; free_used: number }>();
  const period = periodOf(now), used = w && w.free_period === period ? w.free_used : 0;
  return { coins: w?.coins ?? 0, free: { limit: FREE_MESSAGES_PER_MONTH, used, remaining: Math.max(0, FREE_MESSAGES_PER_MONTH - used), period, resetsAt: nextResetAt(now) }, costs: COSTS };
}

/** Spends one use: the monthly free allowance first (for uses that have one), then coins. Nothing is charged on "insufficient". */
export async function spend(db: D1Database, userId: string, usage: Usage, now = Date.now()): Promise<SpendResult> {
  await ensure(db, userId);
  const period = periodOf(now);
  if (FREE_USES.includes(usage)) {
    const [upd, led] = await db.batch([
      db.prepare(
        "UPDATE wallets SET free_used = CASE WHEN free_period = ?1 THEN free_used + 1 ELSE 1 END, free_period = ?1, updated_at = ?2 " +
        "WHERE user_id = ?3 AND (free_period <> ?1 OR free_used < ?4)").bind(period, now, userId, FREE_MESSAGES_PER_MONTH),
      db.prepare("INSERT INTO ledger (user_id, kind, usage, delta, period, created_at) SELECT ?, 'free_spend', ?, 0, ?, ? WHERE changes() > 0")
        .bind(userId, usage, period, now),
    ]);
    if (changed(upd)) return { ok: true, source: "free", ref: led.meta.last_row_id };
  }
  const cost = COSTS[usage];
  const [upd, led] = await db.batch([
    db.prepare("UPDATE wallets SET coins = coins - ?1, updated_at = ?2 WHERE user_id = ?3 AND coins >= ?1").bind(cost, now, userId),
    db.prepare("INSERT INTO ledger (user_id, kind, usage, delta, period, created_at) SELECT ?, 'coin_spend', ?, ?, ?, ? WHERE changes() > 0")
      .bind(userId, usage, -cost, period, now),
  ]);
  return changed(upd) ? { ok: true, source: "coin", ref: led.meta.last_row_id } : { ok: false, reason: "insufficient" };
}

/** Gives back a spend (for example when the model call failed). Safe to call twice: the second call does nothing. Returns true when it refunded. */
export async function refund(db: D1Database, userId: string, spendRef: number, now = Date.now()): Promise<boolean> {
  const s = await db.prepare("SELECT kind, usage, delta, period FROM ledger WHERE id = ? AND user_id = ?").bind(spendRef, userId)
    .first<{ kind: string; usage: string; delta: number; period: string }>();
  if (!s || (s.kind !== "free_spend" && s.kind !== "coin_spend")) return false;
  const free = s.kind === "free_spend", ref = `refund:${spendRef}`;
  const [led, upd] = await db.batch([
    db.prepare("INSERT OR IGNORE INTO ledger (user_id, kind, usage, delta, period, ref, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)")
      .bind(userId, free ? "refund_free" : "refund_coin", s.usage, free ? 0 : -s.delta, s.period, ref, now),
    free
      // a free use only comes back inside the month it was spent in, when the counter still belongs to that month
      ? db.prepare("UPDATE wallets SET free_used = free_used - 1, updated_at = ?1 WHERE user_id = ?2 AND free_period = ?3 AND free_used > 0 AND changes() > 0").bind(now, userId, s.period)
      : db.prepare("UPDATE wallets SET coins = coins + ?1, updated_at = ?2 WHERE user_id = ?3 AND changes() > 0").bind(-s.delta, now, userId),
  ]);
  return changed(led) && changed(upd);
}

/** Adds coins. `ref` makes it idempotent (the same payment or admin grant cannot be applied twice). Returns false when already applied. */
export async function grant(db: D1Database, userId: string, coins: number, ref: string, now = Date.now()): Promise<boolean> {
  if (!Number.isInteger(coins) || coins <= 0) throw new Error("coins must be a positive integer");
  await ensure(db, userId);
  const [led, upd] = await db.batch([
    db.prepare("INSERT OR IGNORE INTO ledger (user_id, kind, usage, delta, period, ref, created_at) VALUES (?, 'grant', '', ?, ?, ?, ?)")
      .bind(userId, coins, periodOf(now), ref, now),
    db.prepare("UPDATE wallets SET coins = coins + ?1, updated_at = ?2 WHERE user_id = ?3 AND changes() > 0").bind(coins, now, userId),
  ]);
  return changed(led) && changed(upd);
}
