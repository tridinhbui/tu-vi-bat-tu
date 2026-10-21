// Public side of the feedback bubble (/api/feedback) and visit counting (/api/hit). Anyone may write, signed in or not.
// A thread is owned by whoever holds its random key (kept in the visitor's browser); the admin side is src/admin/route.ts.
import { randomToken, sha256, type User } from "../auth/session.ts";
import { bump, vnDay } from "../stats/stats.ts";

export const MAX_BODY = 2000;
const THREADS_PER_HOUR = 5;          // new threads per network address
const MESSAGES_PER_10MIN = 20;       // visitor messages per thread

export interface Message { id: number; author: "visitor" | "admin"; body: string; at: number }

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

// Same statements as migrations/app/0006_feedback_traffic.sql, run once per isolate so a deploy works before the migration is applied.
const SCHEMA = [
  "CREATE TABLE IF NOT EXISTS feedback_threads (id TEXT PRIMARY KEY, key_hash TEXT NOT NULL UNIQUE, user_id TEXT, name TEXT NOT NULL DEFAULT '', email TEXT NOT NULL DEFAULT '', page TEXT NOT NULL DEFAULT '', ip_hash TEXT NOT NULL DEFAULT '', created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL, admin_seen INTEGER NOT NULL DEFAULT 0)",
  "CREATE INDEX IF NOT EXISTS feedback_threads_updated ON feedback_threads(updated_at)",
  "CREATE INDEX IF NOT EXISTS feedback_threads_ip ON feedback_threads(ip_hash, created_at)",
  "CREATE TABLE IF NOT EXISTS feedback_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, thread_id TEXT NOT NULL REFERENCES feedback_threads(id) ON DELETE CASCADE, author TEXT NOT NULL CHECK (author IN ('visitor', 'admin')), body TEXT NOT NULL, created_at INTEGER NOT NULL)",
  "CREATE INDEX IF NOT EXISTS feedback_messages_thread ON feedback_messages(thread_id, id)",
  "CREATE TABLE IF NOT EXISTS visitor_days (day TEXT NOT NULL, vid TEXT NOT NULL, PRIMARY KEY (day, vid))",
];
const ready = new WeakMap<D1Database, Promise<unknown>>();
export function ensureSchema(db: D1Database): Promise<unknown> {
  let p = ready.get(db);
  if (!p) { p = db.batch(SCHEMA.map(s => db.prepare(s))).catch(e => { ready.delete(db); throw e; }); ready.set(db, p); }
  return p;
}

/** Trimmed, length-checked message text, or null. */
export function cleanBody(v: unknown): string | null {
  if (typeof v !== "string") return null;
  const s = v.replace(/\r\n?/g, "\n").replace(/[\u0000-\u0008\u000B-\u001F\u007F]/g, "").trim();
  return s && s.length <= MAX_BODY ? s : null;
}

export async function listMessages(db: D1Database, threadId: string, after = 0): Promise<Message[]> {
  const { results } = await db.prepare("SELECT id, author, body, created_at AS at FROM feedback_messages WHERE thread_id = ? AND id > ? ORDER BY id LIMIT 200")
    .bind(threadId, after).all<Message>();
  return results;
}

export async function addMessage(db: D1Database, threadId: string, author: Message["author"], body: string, now = Date.now()): Promise<void> {
  await db.batch([
    db.prepare("INSERT INTO feedback_messages (thread_id, author, body, created_at) VALUES (?, ?, ?, ?)").bind(threadId, author, body, now),
    db.prepare("UPDATE feedback_threads SET updated_at = ? WHERE id = ?").bind(now, threadId),
  ]);
}

const ipHash = (request: Request) => sha256("tvbt-feedback:" + (request.headers.get("cf-connecting-ip") ?? "")).then(h => h.slice(0, 32));
const BOT = /bot|crawl|spider|slurp|preview|monitor|headless|lighthouse/i;

export const isFeedbackPath = (p: string) => p === "/api/feedback" || p === "/api/hit";

export async function handleFeedback(request: Request, db: D1Database | undefined, user: User | null): Promise<Response> {
  const path = new URL(request.url).pathname;
  if (!db) return json({ detail: "feedback is not configured" }, 503);
  // writes need a custom header, which a cross-site form or image cannot send
  if (request.method !== "GET" && request.headers.get("x-tvbt") !== "1") return json({ detail: "missing x-tvbt header" }, 403);
  try { await ensureSchema(db); } catch { return json({ detail: "feedback is not available" }, 503); }

  // One visit per browser session (the page sends it once per tab session), plus one row per browser per day for unique visitors.
  if (path === "/api/hit") {
    if (request.method !== "POST") return json({ detail: "POST only" }, 405);
    if (BOT.test(request.headers.get("user-agent") ?? "")) return json({ ok: true });
    const b = await request.json().catch(() => null) as { vid?: unknown } | null;
    const vid = typeof b?.vid === "string" && /^[A-Za-z0-9_-]{8,64}$/.test(b.vid) ? b.vid : null;
    if (!vid) return json({ detail: "body must be {vid}" }, 400);
    await Promise.all([bump(db, "visits"), db.prepare("INSERT OR IGNORE INTO visitor_days (day, vid) VALUES (?, ?)").bind(vnDay(), vid).run().catch(() => {})]);
    return json({ ok: true });
  }

  const key = request.headers.get("x-feedback-key") ?? "";
  const thread = /^[A-Za-z0-9_-]{20,64}$/.test(key)
    ? await db.prepare("SELECT id FROM feedback_threads WHERE key_hash = ?").bind(await sha256(key)).first<{ id: string }>()
    : null;

  if (request.method === "GET") {
    if (!thread) return json({ messages: [] });
    const after = Number(new URL(request.url).searchParams.get("after")) || 0;
    return json({ messages: await listMessages(db, thread.id, after) });
  }
  if (request.method !== "POST") return json({ detail: "GET or POST" }, 405);

  const b = await request.json().catch(() => null) as { body?: unknown; page?: unknown } | null;
  const body = cleanBody(b?.body);
  if (!body) return json({ detail: `message must be 1..${MAX_BODY} characters` }, 400);
  const now = Date.now();
  const page = typeof b?.page === "string" ? b.page.slice(0, 200) : "";

  if (thread) {
    const recent = await db.prepare("SELECT COUNT(*) AS n FROM feedback_messages WHERE thread_id = ? AND author = 'visitor' AND created_at > ?")
      .bind(thread.id, now - 600_000).first<{ n: number }>();
    if ((recent?.n ?? 0) >= MESSAGES_PER_10MIN) return json({ detail: "too many messages, try again in a few minutes" }, 429);
    // a visitor who signs in later is attached to the thread they already started
    if (user) await db.prepare("UPDATE feedback_threads SET user_id = ?, name = ?, email = ? WHERE id = ? AND user_id IS NULL").bind(user.id, user.name, user.email, thread.id).run();
    await addMessage(db, thread.id, "visitor", body, now);
    return json({ messages: await listMessages(db, thread.id) });
  }

  const ip = await ipHash(request);
  const made = await db.prepare("SELECT COUNT(*) AS n FROM feedback_threads WHERE ip_hash = ? AND created_at > ?").bind(ip, now - 3600_000).first<{ n: number }>();
  if ((made?.n ?? 0) >= THREADS_PER_HOUR) return json({ detail: "too many new conversations, try again later" }, 429);
  const id = randomToken(9), newKey = randomToken(24);
  await db.prepare("INSERT INTO feedback_threads (id, key_hash, user_id, name, email, page, ip_hash, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")
    .bind(id, await sha256(newKey), user?.id ?? null, user?.name ?? "", user?.email ?? "", page, ip, now, now).run();
  await addMessage(db, id, "visitor", body, now);
  return json({ key: newKey, messages: await listMessages(db, id) });
}
