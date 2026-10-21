// Landing-page counters: chart scans and sign-ins. The page shows a fixed starting figure plus what was recorded here
// (one row per counter in `stats`, each event adds one atomically). Only totals are stored, nothing about a person or a birth.
export interface Stats { scans: number; signins: number; live: boolean; at: number }
type Key = "scans" | "signins";

/** What the site had already counted before these counters existed; real events add on top. */
export const BASE: Record<Key, number> = { scans: 102, signins: 75 };

const CREATE = "CREATE TABLE IF NOT EXISTS stats (key TEXT PRIMARY KEY, value INTEGER NOT NULL DEFAULT 0 CHECK (value >= 0), updated_at INTEGER NOT NULL DEFAULT 0)";

/** Base + recorded. Without a database or table the base figures are shown (live: false) rather than nothing. */
export async function getStats(db: D1Database | undefined, now = Date.now()): Promise<Stats> {
  const rec: Record<Key, number> = { scans: 0, signins: 0 };
  let live = false;
  if (db) try {
    const { results } = await db.prepare("SELECT key, value FROM stats WHERE key IN ('scans', 'signins')").all<{ key: Key; value: number }>();
    for (const r of results) rec[r.key] = r.value;
    live = true;
  } catch { /* table not created yet: base figures only */ }
  return { scans: BASE.scans + rec.scans, signins: BASE.signins + rec.signins, live, at: now };
}

/** Adds one to a counter, creating the table on first use. Never throws: a counter must not break the request it rides on. */
export async function bump(db: D1Database, key: Key, now = Date.now()): Promise<void> {
  const add = () => db.prepare("INSERT INTO stats (key, value, updated_at) VALUES (?1, 1, ?2) ON CONFLICT(key) DO UPDATE SET value = value + 1, updated_at = ?2").bind(key, now).run();
  try { await add(); } catch (e) {
    if (!/no such table/i.test(String(e))) return;
    try { await db.prepare(CREATE).run(); await add(); } catch { /* ignore */ }
  }
}

export async function handleStats(db: D1Database | undefined): Promise<Response> {
  // a few seconds at the edge: a crowd of open landing pages shares one database read
  return new Response(JSON.stringify(await getStats(db)), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "public, max-age=3, s-maxage=5" } });
}
