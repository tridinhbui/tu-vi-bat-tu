// Admin area (/api/admin/*, page /admin): the feedback inbox and site statistics.
// An admin is a signed-in Google account whose email is listed in ADMIN_EMAILS (comma-separated; a Worker secret or var).
// Without ADMIN_EMAILS, or for anyone else, every route here answers 404, as if it did not exist.
// /api/admin/grant (bearer ADMIN_TOKEN, for scripts) stays in src/auth/route.ts.
import type { User } from "../auth/session.ts";
import { addMessage, cleanBody, ensureSchema, listMessages } from "../feedback/route.ts";
import { getStats, vnDay } from "../stats/stats.ts";

export interface AdminEnv { DB?: D1Database; ADMIN_EMAILS?: string }

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

export function isAdmin(env: AdminEnv, user: User | null): boolean {
  if (!user || !env.ADMIN_EMAILS) return false;
  const want = user.email.trim().toLowerCase();
  return env.ADMIN_EMAILS.split(",").some(e => e.trim().toLowerCase() === want && want !== "");
}

export const isAdminPath = (p: string) => p.startsWith("/api/admin/") && p !== "/api/admin/grant";

export async function handleAdmin(request: Request, env: AdminEnv, user: User | null): Promise<Response> {
  const db = env.DB, path = new URL(request.url).pathname;
  if (!db || !isAdmin(env, user)) return json({ detail: "not found" }, 404);
  if (request.method !== "GET" && request.headers.get("x-tvbt") !== "1") return json({ detail: "missing x-tvbt header" }, 403);
  try { await ensureSchema(db); } catch { /* stats still answer what they can */ }

  if (path === "/api/admin/me") return json({ admin: true, email: user!.email });
  if (path === "/api/admin/stats" && request.method === "GET") return json(await siteStats(db));

  if (path === "/api/admin/feedback" && request.method === "GET") {
    const { results } = await db.prepare(
      `SELECT t.id, t.name, t.email, t.page, t.created_at AS createdAt, t.updated_at AS updatedAt,
              (SELECT COUNT(*) FROM feedback_messages m WHERE m.thread_id = t.id AND m.author = 'visitor' AND m.id > t.admin_seen) AS unread,
              (SELECT COUNT(*) FROM feedback_messages m WHERE m.thread_id = t.id) AS total,
              (SELECT body FROM feedback_messages m WHERE m.thread_id = t.id ORDER BY m.id DESC LIMIT 1) AS last,
              (SELECT author FROM feedback_messages m WHERE m.thread_id = t.id ORDER BY m.id DESC LIMIT 1) AS lastAuthor
       FROM feedback_threads t ORDER BY t.updated_at DESC LIMIT 200`).all();
    return json({ threads: results.map(t => ({ ...t, last: String(t.last ?? "").slice(0, 160) })) });
  }

  const m = path.match(/^\/api\/admin\/feedback\/([A-Za-z0-9_-]{6,20})$/);
  if (m) {
    const t = await db.prepare("SELECT id, name, email, page, created_at AS createdAt FROM feedback_threads WHERE id = ?").bind(m[1]).first();
    if (!t) return json({ detail: "no such conversation" }, 404);
    if (request.method === "POST") {
      const b = await request.json().catch(() => null) as { body?: unknown } | null;
      const body = cleanBody(b?.body);
      if (!body) return json({ detail: "reply must be 1..2000 characters" }, 400);
      await addMessage(db, m[1], "admin", body);
    } else if (request.method !== "GET") return json({ detail: "GET or POST" }, 405);
    const messages = await listMessages(db, m[1]);
    const lastId = messages.length ? messages[messages.length - 1].id : 0;
    await db.prepare("UPDATE feedback_threads SET admin_seen = ? WHERE id = ? AND admin_seen < ?").bind(lastId, m[1], lastId).run();
    return json({ thread: t, messages });
  }
  return json({ detail: "not found" }, 404);
}

type Range = { today: number; d7: number; d30: number; all: number };
const DAYS = 30;

/** Visits, unique visitors, scans and sign-ins by day (Vietnam time) and over today / 7 / 30 days / all time; accounts and feedback.
 *  Each part fails on its own (zeros) so one missing table does not blank the page. */
export async function siteStats(db: D1Database, now = Date.now()) {
  const days = Array.from({ length: DAYS }, (_, i) => vnDay(now - (DAYS - 1 - i) * 86400_000));
  const today = days[DAYS - 1], d7 = days[DAYS - 7];
  const safe = async <T>(f: () => Promise<T>, fallback: T): Promise<T> => { try { return await f(); } catch { return fallback; } };

  const counters = await safe(async () => {
    const { results } = await db.prepare("SELECT key, value FROM stats WHERE key IN ('visits', 'scans', 'signins') OR key LIKE '%@____-__-__'").all<{ key: string; value: number }>();
    return new Map(results.map(r => [r.key, r.value]));
  }, new Map<string, number>());
  const series = (k: string) => days.map(d => counters.get(`${k}@${d}`) ?? 0);
  const sum = (a: number[], from: number) => a.slice(from).reduce((x, y) => x + y, 0);
  const range = (k: string, all: number): Range => { const s = series(k); return { today: s[DAYS - 1], d7: sum(s, DAYS - 7), d30: sum(s, 0), all }; };

  const pub = await getStats(db, now);
  const visitorsByDay = await safe(async () => {
    const { results } = await db.prepare("SELECT day, COUNT(*) AS n FROM visitor_days WHERE day >= ? GROUP BY day").bind(days[0]).all<{ day: string; n: number }>();
    const m = new Map(results.map(r => [r.day, r.n]));
    return days.map(d => m.get(d) ?? 0);
  }, days.map(() => 0));
  const distinct = (from?: string) => safe(async () => (await (from
    ? db.prepare("SELECT COUNT(DISTINCT vid) AS n FROM visitor_days WHERE day >= ?").bind(from)
    : db.prepare("SELECT COUNT(DISTINCT vid) AS n FROM visitor_days")).first<{ n: number }>())?.n ?? 0, 0);
  const [v7, v30, vAll] = await Promise.all([distinct(d7), distinct(days[0]), distinct()]);

  const sec = Math.floor(now / 1000), dayStart = Math.floor(Date.parse(today + "T00:00:00+07:00") / 1000);
  const count = (sql: string, ...args: unknown[]) => safe(async () => (await db.prepare(sql).bind(...args).first<{ n: number }>())?.n ?? 0, 0);
  const [uAll, uToday, u7, charts, fbThreads, fbUnread, pay, payCoins] = await Promise.all([
    count("SELECT COUNT(*) AS n FROM users"),
    count("SELECT COUNT(*) AS n FROM users WHERE created_at >= ?", dayStart),
    count("SELECT COUNT(*) AS n FROM users WHERE created_at >= ?", sec - 7 * 86400),
    count("SELECT COUNT(*) AS n FROM charts"),
    count("SELECT COUNT(*) AS n FROM feedback_threads"),
    count("SELECT COUNT(*) AS n FROM feedback_threads t WHERE EXISTS (SELECT 1 FROM feedback_messages m WHERE m.thread_id = t.id AND m.author = 'visitor' AND m.id > t.admin_seen)"),
    count("SELECT COUNT(*) AS n FROM payments"),
    count("SELECT COALESCE(SUM(coins), 0) AS n FROM payments"),
  ]);

  return {
    at: now, days, live: pub.live,
    visits: range("visits", counters.get("visits") ?? 0),
    visitors: { today: visitorsByDay[DAYS - 1], d7: v7, d30: v30, all: vAll } as Range,
    // "all" is what the landing page shows (starting figure + recorded); the daily rows begin when this page was added
    scans: range("scans", pub.scans),
    signins: range("signins", pub.signins),
    series: { visits: series("visits"), visitors: visitorsByDay, scans: series("scans"), signins: series("signins") },
    accounts: { total: uAll, today: uToday, d7: u7, savedCharts: charts },
    feedback: { threads: fbThreads, unread: fbUnread },
    payments: { count: pay, coins: payCoins },
  };
}
