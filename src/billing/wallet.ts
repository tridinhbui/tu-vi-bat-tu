// Atomic spending. Every state change is one conditional UPDATE (so two parallel requests can never overspend) batched with its
// ledger row via changes(), which is 0 when the UPDATE did not apply. D1 runs a batch as a single transaction.
import { COSTS, FREE_MESSAGES_PER_DAY, FREE_USES, TOPUP_CHAT, dayOf, nextResetAt, periodOf, type Usage } from "./config.ts";

export type SpendResult =
  | { ok: true; source: "free" | "coin"; ref: number }
  | { ok: false; reason: "insufficient" };

export interface WalletView {
  coins: number;
  /** Today's free chats: 2 a day, or up to 30 a day while a top-up's chat pass runs. `period` is the day (YYYY-MM-DD, Vietnam time). */
  free: { limit: number; used: number; remaining: number; period: string; resetsAt: number };
  /** The chat pass from top-ups; `until` is 0 when there never was one. */
  pass: { active: boolean; until: number; days: number; perDay: number };
  costs: typeof COSTS;
}

const changed = (r: D1Result) => (r.meta?.changes ?? 0) > 0;
const ensure = (db: D1Database, userId: string) =>
  db.prepare("INSERT OR IGNORE INTO wallets (user_id) VALUES (?)").bind(userId).run();

// ---------- chat pass (migration 0010; created here on first use while the migration has not run yet) ----------
const CREATE_PASSES = "CREATE TABLE IF NOT EXISTS chat_passes (user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE, until INTEGER NOT NULL DEFAULT 0, updated_at INTEGER NOT NULL DEFAULT 0)";
const noTable = (e: unknown) => /no such table/i.test(String(e));

/** When this user's chat pass ends (0: none). Before the table exists nobody has a pass. */
export async function passUntil(db: D1Database, userId: string): Promise<number> {
  try { return (await db.prepare("SELECT until FROM chat_passes WHERE user_id = ?").bind(userId).first<{ until: number }>())?.until ?? 0; }
  catch (e) { if (noTable(e)) return 0; throw e; }
}

/** A top-up was credited under ledger ref `creditRef` (a paid order, a gift code): the chat pass now runs TOPUP_CHAT.days from the later of
 *  now and its current end. Idempotent per credit: a "pass:<creditRef>" ledger row is written in the same transaction, so a repeated
 *  payment callback never extends twice, and a callback retried after a failure here still extends once. Returns true when it extended. */
export async function grantPass(db: D1Database, userId: string, creditRef: string, now = Date.now()): Promise<boolean> {
  const span = TOPUP_CHAT.days * 86400_000;
  const run = () => db.batch([
    db.prepare("INSERT OR IGNORE INTO ledger (user_id, kind, usage, delta, period, ref, created_at) VALUES (?, 'pass', 'chat', 0, ?, ?, ?)")
      .bind(userId, periodOf(now), `pass:${creditRef}`, now),
    db.prepare("INSERT INTO chat_passes (user_id, until, updated_at) SELECT ?1, ?2 + ?3, ?2 WHERE changes() > 0 " +
      "ON CONFLICT(user_id) DO UPDATE SET until = MAX(until, ?2) + ?3, updated_at = ?2").bind(userId, now, span),
  ]);
  let led: D1Result;
  try { [led] = await run(); } catch (e) { if (!noTable(e)) throw e; await db.prepare(CREATE_PASSES).run(); [led] = await run(); }
  return changed(led);
}

/** Today's free chat limit: the pass's daily cap while it runs, else the plain daily allowance. */
const freeLimit = (until: number, now: number) => until > now ? TOPUP_CHAT.perDay : FREE_MESSAGES_PER_DAY;

export async function getWallet(db: D1Database, userId: string, now = Date.now()): Promise<WalletView> {
  await ensure(db, userId);
  const w = await db.prepare("SELECT coins, free_period, free_used FROM wallets WHERE user_id = ?").bind(userId).first<{ coins: number; free_period: string; free_used: number }>();
  const until = await passUntil(db, userId), limit = freeLimit(until, now);
  const period = dayOf(now), used = w && w.free_period === period ? w.free_used : 0;
  return {
    coins: w?.coins ?? 0, free: { limit, used, remaining: Math.max(0, limit - used), period, resetsAt: nextResetAt(now) },
    pass: { active: until > now, until, days: TOPUP_CHAT.days, perDay: TOPUP_CHAT.perDay }, costs: COSTS,
  };
}

/** Spends one use: today's free allowance first (for uses that have one), then coins. Nothing is charged on "insufficient". */
export async function spend(db: D1Database, userId: string, usage: Usage, now = Date.now()): Promise<SpendResult> {
  await ensure(db, userId);
  const period = periodOf(now);
  if (FREE_USES.includes(usage)) {
    const day = dayOf(now), limit = freeLimit(await passUntil(db, userId), now);
    const [upd, led] = await db.batch([
      db.prepare(
        "UPDATE wallets SET free_used = CASE WHEN free_period = ?1 THEN free_used + 1 ELSE 1 END, free_period = ?1, updated_at = ?2 " +
        "WHERE user_id = ?3 AND (free_period <> ?1 OR free_used < ?4)").bind(day, now, userId, limit),
      // filed under its day, so a refund gives the use back only to that same day's counter
      db.prepare("INSERT INTO ledger (user_id, kind, usage, delta, period, created_at) SELECT ?, 'free_spend', ?, 0, ?, ? WHERE changes() > 0")
        .bind(userId, usage, day, now),
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
      // a free use only comes back on the day it was spent, while the counter still belongs to that day
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
