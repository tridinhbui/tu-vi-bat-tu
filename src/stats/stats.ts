// Landing-page counters: charts made and people who joined. One row each in `stats`; an event adds one atomically.
export interface Stats { charts: number; users: number; at: number }
type Key = "charts" | "users";

export async function getStats(db: D1Database, now = Date.now()): Promise<Stats | null> {
  try {
    const { results } = await db.prepare("SELECT key, value FROM stats WHERE key IN ('charts', 'users')").all<{ key: Key; value: number }>();
    const v = Object.fromEntries(results.map(r => [r.key, r.value]));
    return typeof v.charts === "number" && typeof v.users === "number" ? { charts: v.charts, users: v.users, at: now } : null;
  } catch { return null; }                                       // table not created yet: the page just hides the counters
}

/** Adds one to a counter. Never throws: a counter must not break the request it rides on. */
export async function bump(db: D1Database, key: Key, now = Date.now()): Promise<void> {
  try { await db.prepare("UPDATE stats SET value = value + 1, updated_at = ?2 WHERE key = ?1").bind(key, now).run(); } catch { /* ignore */ }
}

export async function handleStats(db: D1Database | undefined): Promise<Response> {
  const s = db ? await getStats(db) : null;
  if (!s) return new Response(JSON.stringify({ detail: "stats unavailable" }), { status: 503, headers: { "content-type": "application/json" } });
  // a few seconds at the edge: a crowd of open landing pages shares one database read
  return new Response(JSON.stringify(s), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "public, max-age=3, s-maxage=5" } });
}
