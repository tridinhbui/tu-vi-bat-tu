// Discount codes (percent off a coin pack bought with money) and gift codes (free coins, once per account), made on /admin.
import { MAX_DISCOUNT_PCT, periodOf } from "./config.ts";
import { grantPass } from "./wallet.ts";

export interface PromoCode {
  code: string; kind: "discount" | "gift"; percent: number; coins: number; max_uses: number; used: number;
  expires_at: number; active: number; note: string; created_by: string; created_at: number;
}

export const cleanCode = (v: unknown): string | null => typeof v === "string" && /^[A-Za-z0-9-]{4,32}$/.test(v.trim()) ? v.trim().toUpperCase() : null;
// no 0/O, 1/I/L: a code read aloud or copied from a picture is typed right
const ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789";
export function newCode(prefix = "TB"): string {
  const b = crypto.getRandomValues(new Uint8Array(10));
  return `${prefix}-${[...b].map(x => ALPHABET[x % ALPHABET.length]).join("")}`;
}

const VN_OFFSET_MS = 7 * 3600 * 1000;
/** "YYYY-MM-DD" means "until the end of that day, Vietnam time". */
export const endOfVnDay = (d: string) => Date.parse(`${d}T00:00:00Z`) - VN_OFFSET_MS + 86400_000;

export type CreateResult = { ok: true; code: PromoCode } | { ok: false; detail: string };

/** Validates and stores a new code. Body: {kind, code?, percent | coins, max_uses?, expires? (YYYY-MM-DD), note?}. */
export async function createCode(db: D1Database, b: Record<string, unknown> | null, by: string, now = Date.now()): Promise<CreateResult> {
  if (!b || (b.kind !== "discount" && b.kind !== "gift")) return { ok: false, detail: "kind must be discount or gift" };
  const int = (v: unknown, lo: number, hi: number) => Number.isInteger(v) && (v as number) >= lo && (v as number) <= hi ? v as number : null;
  const percent = b.kind === "discount" ? int(b.percent, 1, MAX_DISCOUNT_PCT) : 0;
  const coins = b.kind === "gift" ? int(b.coins, 1, 100000) : 0;
  if (percent === null) return { ok: false, detail: `percent must be 1..${MAX_DISCOUNT_PCT}` };
  if (coins === null) return { ok: false, detail: "coins must be 1..100000" };
  const max = b.max_uses === undefined || b.max_uses === null || b.max_uses === "" ? 1 : int(b.max_uses, 1, 100000);
  if (max === null) return { ok: false, detail: "max_uses must be 1..100000" };
  let expires = 0;
  if (b.expires) {
    if (typeof b.expires !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(b.expires) || Number.isNaN(Date.parse(b.expires))) return { ok: false, detail: "expires must be YYYY-MM-DD" };
    expires = endOfVnDay(b.expires);
    if (expires <= now) return { ok: false, detail: "expires is in the past" };
  }
  const code = b.code ? cleanCode(b.code) : newCode(b.kind === "gift" ? "QUA" : "GIAM");
  if (!code) return { ok: false, detail: "code must be 4..32 letters, digits or dashes" };
  const note = typeof b.note === "string" ? b.note.trim().slice(0, 200) : "";
  const r = await db.prepare("INSERT OR IGNORE INTO promo_codes (code, kind, percent, coins, max_uses, used, expires_at, active, note, created_by, created_at) VALUES (?, ?, ?, ?, ?, 0, ?, 1, ?, ?, ?)")
    .bind(code, b.kind, percent, coins, max, expires, note, by, now).run();
  if (!(r.meta?.changes ?? 0)) return { ok: false, detail: "this code already exists" };
  return { ok: true, code: (await getCode(db, code))! };
}

export const getCode = (db: D1Database, code: string) => db.prepare("SELECT * FROM promo_codes WHERE code = ?").bind(code).first<PromoCode>();
export async function listCodes(db: D1Database): Promise<PromoCode[]> {
  return (await db.prepare("SELECT * FROM promo_codes ORDER BY created_at DESC LIMIT 500").all<PromoCode>()).results;
}
export async function setActive(db: D1Database, code: string, active: boolean): Promise<boolean> {
  const r = await db.prepare("UPDATE promo_codes SET active = ? WHERE code = ?").bind(active ? 1 : 0, code).run();
  return (r.meta?.changes ?? 0) > 0;
}

export type CodeProblem = "invalid" | "expired" | "used_up" | "already";
export const CODE_PROBLEM_VI: Record<CodeProblem, string> = {
  invalid: "Mã không đúng hoặc đã ngừng dùng.", expired: "Mã đã hết hạn.", used_up: "Mã đã hết lượt dùng.", already: "Tài khoản này đã dùng mã này rồi.",
};
function problemOf(row: PromoCode | null, kind: PromoCode["kind"], now: number): CodeProblem | null {
  if (!row || row.kind !== kind || !row.active) return "invalid";
  if (row.expires_at && row.expires_at <= now) return "expired";
  if (row.used >= row.max_uses) return "used_up";
  return null;
}

export type RedeemResult = { ok: true; coins: number; code: string } | { ok: false; reason: CodeProblem };

/** Redeems a gift code: one D1 batch. The ledger row (ref "gift:<code>", unique per account) is written only while the code is valid and
 *  has uses left; the use is counted and the coins added only when that row was written. Two accounts racing for the last use cannot
 *  both win, and one account cannot redeem the same code twice. */
export async function redeemGift(db: D1Database, userId: string, raw: unknown, now = Date.now()): Promise<RedeemResult> {
  const code = cleanCode(raw);
  if (!code) return { ok: false, reason: "invalid" };
  await db.prepare("INSERT OR IGNORE INTO wallets (user_id) VALUES (?)").bind(userId).run();
  const [led, use, upd] = await db.batch([
    db.prepare("INSERT OR IGNORE INTO ledger (user_id, kind, usage, delta, period, ref, created_at) SELECT ?1, 'gift', '', p.coins, ?2, 'gift:' || p.code, ?3 " +
      "FROM promo_codes p WHERE p.code = ?4 AND p.kind = 'gift' AND p.active = 1 AND p.used < p.max_uses AND (p.expires_at = 0 OR p.expires_at > ?3)")
      .bind(userId, periodOf(now), now, code),
    db.prepare("UPDATE promo_codes SET used = used + 1 WHERE code = ? AND changes() > 0").bind(code),
    db.prepare("UPDATE wallets SET coins = coins + (SELECT coins FROM promo_codes WHERE code = ?1), updated_at = ?2 WHERE user_id = ?3 AND changes() > 0").bind(code, now, userId),
  ]);
  const row = await getCode(db, code);
  // a gift code counts as a top-up: it opens (or extends) the 30-day chat pass
  if ([led, use, upd].every(r => (r.meta?.changes ?? 0) > 0)) { await grantPass(db, userId, `gift:${code}`, now); return { ok: true, coins: row!.coins, code }; }
  if (await db.prepare("SELECT 1 AS x FROM ledger WHERE user_id = ? AND ref = ?").bind(userId, `gift:${code}`).first()) return { ok: false, reason: "already" };
  return { ok: false, reason: problemOf(row, "gift", now) ?? "invalid" };
}

export type DiscountCheck = { ok: true; code: string; percent: number } | { ok: false; reason: CodeProblem };

/** Whether a discount code can be used for a new order by this account (once per account: a paid order with the code blocks it). The use
 *  itself is counted when the payment succeeds (orders.ts completeOrder), so an abandoned payment page does not spend it. */
export async function checkDiscount(db: D1Database, userId: string, raw: unknown, now = Date.now()): Promise<DiscountCheck> {
  const code = cleanCode(raw);
  if (!code) return { ok: false, reason: "invalid" };
  const row = await getCode(db, code), p = problemOf(row, "discount", now);
  if (p) return { ok: false, reason: p };
  if (await db.prepare("SELECT 1 AS x FROM orders WHERE user_id = ? AND discount_code = ? AND status = 'paid'").bind(userId, code).first()) return { ok: false, reason: "already" };
  return { ok: true, code, percent: row!.percent };
}
