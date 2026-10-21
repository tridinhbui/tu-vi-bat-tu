// Mời bạn: every signed-in user has a referral code; a NEW account opened from a ?ref= link claims it once, and both sides get coins
// through the wallet's own grant() (idempotent by ref, so a retried claim never pays twice). Payment code is not touched.
//   GET  /api/me/referral        -> my code, link, how many joined through it, coins earned, whether I can still claim one
//   POST /api/me/referral/claim  -> {code}: record that I joined through this code and pay both rewards
import type { User } from "../auth/session.ts";
import { grant } from "../billing/wallet.ts";

/** Rewards in coins and limits. The amounts are a product decision: change them here only. */
export const REFERRAL = {
  inviterCoins: 10,          // to the person who shared the link, per new account
  inviteeCoins: 5,           // to the new account
  windowDays: 7,             // only an account younger than this can claim (an old account cannot "join" again)
  maxPerInviter: 50,         // rewarded invitations per code
} as const;

const ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";   // no 0/O, 1/I: codes are read aloud and typed
export const CODE_RE = /^[A-HJ-NP-Z2-9]{8}$/;

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

// Same statements as migrations/app/0009_referrals.sql, run once per isolate so a deploy works before the migration is applied.
const SCHEMA = [
  "CREATE TABLE IF NOT EXISTS referral_codes (user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE, code TEXT NOT NULL UNIQUE, created_at INTEGER NOT NULL)",
  "CREATE TABLE IF NOT EXISTS referrals (invitee_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE, inviter_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, code TEXT NOT NULL, created_at INTEGER NOT NULL)",
  "CREATE INDEX IF NOT EXISTS referrals_inviter ON referrals(inviter_id)",
];
const ready = new WeakMap<D1Database, Promise<unknown>>();
function ensureSchema(db: D1Database): Promise<unknown> {
  let p = ready.get(db);
  if (!p) { p = db.batch(SCHEMA.map(s => db.prepare(s))).catch(e => { ready.delete(db); throw e; }); ready.set(db, p); }
  return p;
}

export const isReferralPath = (p: string) => p === "/api/me/referral" || p === "/api/me/referral/claim";

function newCode(): string {
  const b = crypto.getRandomValues(new Uint8Array(8));
  return Array.from(b, x => ALPHABET[x % ALPHABET.length]).join("");
}

/** The user's code, created on first use (a collision with another user's code just draws again). */
export async function codeOf(db: D1Database, userId: string, now = Date.now()): Promise<string> {
  await ensureSchema(db);
  for (let i = 0; i < 5; i++) {
    const row = await db.prepare("SELECT code FROM referral_codes WHERE user_id = ?").bind(userId).first<{ code: string }>();
    if (row) return row.code;
    await db.prepare("INSERT OR IGNORE INTO referral_codes (user_id, code, created_at) VALUES (?, ?, ?)").bind(userId, newCode(), now).run();
  }
  throw new Error("could not allocate a referral code");
}

export type ClaimResult =
  | { ok: true; inviterCoins: number; inviteeCoins: number }
  | { ok: false; reason: "bad_code" | "own_code" | "too_old" | "already_claimed" | "inviter_full" };

/** Joins `userId` to the owner of `code` and pays both rewards. Retrying after a partial failure finishes the payment, never doubles it. */
export async function claim(db: D1Database, userId: string, code: string, now = Date.now()): Promise<ClaimResult> {
  await ensureSchema(db);
  code = code.trim().toUpperCase();
  if (!CODE_RE.test(code)) return { ok: false, reason: "bad_code" };
  const owner = await db.prepare("SELECT user_id FROM referral_codes WHERE code = ?").bind(code).first<{ user_id: string }>();
  if (!owner) return { ok: false, reason: "bad_code" };
  if (owner.user_id === userId) return { ok: false, reason: "own_code" };
  const prior = await db.prepare("SELECT inviter_id FROM referrals WHERE invitee_id = ?").bind(userId).first<{ inviter_id: string }>();
  if (prior && prior.inviter_id !== owner.user_id) return { ok: false, reason: "already_claimed" };
  if (!prior) {
    const u = await db.prepare("SELECT created_at FROM users WHERE id = ?").bind(userId).first<{ created_at: number }>();
    if (!u || u.created_at * 1000 < now - REFERRAL.windowDays * 86400_000) return { ok: false, reason: "too_old" };
    // one statement, so the per-inviter cap holds even when two friends claim at the same moment
    const ins = await db.prepare(
      "INSERT OR IGNORE INTO referrals (invitee_id, inviter_id, code, created_at) SELECT ?1, ?2, ?3, ?4 " +
      "WHERE (SELECT COUNT(*) FROM referrals WHERE inviter_id = ?2) < ?5").bind(userId, owner.user_id, code, now, REFERRAL.maxPerInviter).run();
    if (!(ins.meta?.changes ?? 0)) {
      const again = await db.prepare("SELECT inviter_id FROM referrals WHERE invitee_id = ?").bind(userId).first<{ inviter_id: string }>();
      if (!again) return { ok: false, reason: "inviter_full" };
      if (again.inviter_id !== owner.user_id) return { ok: false, reason: "already_claimed" };
    }
  }
  // idempotent: the ledger refuses a second row with the same ref for the same user
  await grant(db, userId, REFERRAL.inviteeCoins, "referral:joined", now);
  await grant(db, owner.user_id, REFERRAL.inviterCoins, `referral:invited:${userId}`, now);
  return { ok: true, inviterCoins: REFERRAL.inviterCoins, inviteeCoins: REFERRAL.inviteeCoins };
}

export async function summary(db: D1Database, user: User, origin: string, now = Date.now()) {
  const code = await codeOf(db, user.id, now);
  const n = await db.prepare("SELECT COUNT(*) AS n FROM referrals WHERE inviter_id = ?").bind(user.id).first<{ n: number }>();
  const joined = await db.prepare("SELECT 1 AS x FROM referrals WHERE invitee_id = ?").bind(user.id).first();
  const u = await db.prepare("SELECT created_at FROM users WHERE id = ?").bind(user.id).first<{ created_at: number }>();
  const invited = n?.n ?? 0;
  return {
    code, url: `${origin}/?ref=${code}`, invited, coinsEarned: Math.min(invited, REFERRAL.maxPerInviter) * REFERRAL.inviterCoins,
    reward: { inviter: REFERRAL.inviterCoins, invitee: REFERRAL.inviteeCoins }, maxPerInviter: REFERRAL.maxPerInviter,
    joinedByReferral: !!joined, canClaim: !joined && !!u && u.created_at * 1000 >= now - REFERRAL.windowDays * 86400_000,
  };
}

export async function handleReferral(request: Request, db: D1Database | undefined, user: User | null, now = Date.now()): Promise<Response> {
  if (!db) return json({ detail: "not available" }, 503);
  if (!user) return json({ detail: "sign in required" }, 401);
  const url = new URL(request.url);
  if (url.pathname === "/api/me/referral") {
    if (request.method !== "GET") return json({ detail: "GET only" }, 405);
    return json(await summary(db, user, url.origin, now));
  }
  if (request.method !== "POST") return json({ detail: "POST only" }, 405);
  if (request.headers.get("x-tvbt") !== "1") return json({ detail: "missing x-tvbt header" }, 403);
  const body = await request.json().catch(() => null) as { code?: unknown } | null;
  if (!body || typeof body.code !== "string") return json({ detail: "body must be {code}" }, 400);
  const r = await claim(db, user.id, body.code, now);
  return json(r, r.ok ? 200 : r.reason === "bad_code" ? 404 : 409);
}
