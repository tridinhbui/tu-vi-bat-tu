// Saved-chart sync. The client sends its local list; the server merges it by birth fingerprint and returns the full list.
export const MAX_CHARTS = 200;
const RELS = new Set(["Tôi", "Người thân", "Bạn bè", "Đã lập"]);   // "Đã lập": kept automatically when a member generates a chart
const FIELDS = ["year", "month", "day", "hour", "minute", "gender", "tz", "calendar", "zi_rule", "level", "use_true_solar_time", "longitude"];

export interface ChartItem { id: string; label: string; rel: string; req: Record<string, unknown> }
interface Row { id: string; label: string; rel: string; req_json: string }

const prim = (v: unknown) => typeof v === "string" ? v.length <= 40 : typeof v === "number" ? Number.isFinite(v) : typeof v === "boolean";

/** Whitelists the birth request: known fields only, primitives only, integer date and a gender. Returns it with its fingerprint, or null. */
export function cleanReq(req: unknown): { req: Record<string, unknown>; fp: string } | null {
  if (!req || typeof req !== "object") return null;
  const r: Record<string, unknown> = {};
  for (const k of FIELDS) { const v = (req as Record<string, unknown>)[k]; if (v !== undefined) { if (!prim(v)) return null; r[k] = v; } }
  const nums = ["year", "month", "day", "hour", "minute"].map(k => r[k]);
  if (!nums.every(Number.isInteger) || (r.gender !== "male" && r.gender !== "female")) return null;
  return { req: r, fp: [...nums, r.gender].join("-") };
}

/** Returns a cleaned item and its fingerprint, or null when the item is malformed. Unknown request fields are dropped. */
export function clean(x: unknown): { item: ChartItem; fp: string } | null {
  if (!x || typeof x !== "object") return null;
  const { id, label, rel, req } = x as Record<string, unknown>;
  if (typeof id !== "string" || !/^[a-z0-9]{1,20}$/.test(id) || typeof label !== "string" || typeof rel !== "string" || !RELS.has(rel)) return null;
  const c = cleanReq(req);
  return c && { item: { id, label: label.trim().slice(0, 30) || rel, rel, req: c.req }, fp: c.fp };
}

export async function listCharts(db: D1Database, userId: string): Promise<ChartItem[]> {
  const { results } = await db.prepare("SELECT id, label, rel, req_json FROM charts WHERE user_id = ? ORDER BY updated_at DESC").bind(userId).all<Row>();
  return results.map(r => ({ id: r.id, label: r.label, rel: r.rel, req: JSON.parse(r.req_json) }));
}

/** Upserts the given items (the client's name and relation win per fingerprint) and returns the merged list. Items past the cap are ignored. */
export async function syncCharts(db: D1Database, userId: string, items: unknown[]): Promise<ChartItem[]> {
  const now = Date.now();
  const existing = (await db.prepare("SELECT COUNT(*) AS n FROM charts WHERE user_id = ?").bind(userId).first<{ n: number }>())?.n ?? 0;
  let room = MAX_CHARTS - existing;
  const stmts: D1PreparedStatement[] = [];
  const seen = new Set<string>();
  for (const raw of items.slice(0, MAX_CHARTS)) {
    const c = clean(raw);
    if (!c || seen.has(c.fp)) continue;
    seen.add(c.fp);
    const isNew = !(await db.prepare("SELECT 1 AS x FROM charts WHERE user_id = ? AND fp = ?").bind(userId, c.fp).first());
    if (isNew) { if (room <= 0) continue; room--; }
    // On a conflict keep the stored id (other devices already know it) but take the new name and relation.
    stmts.push(db.prepare(
      "INSERT INTO charts (user_id, fp, id, label, rel, req_json, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?) " +
      "ON CONFLICT (user_id, fp) DO UPDATE SET label = excluded.label, rel = excluded.rel, req_json = excluded.req_json, updated_at = excluded.updated_at")
      .bind(userId, c.fp, c.item.id, c.item.label, c.item.rel, JSON.stringify(c.item.req), now));
  }
  if (stmts.length) await db.batch(stmts);
  return listCharts(db, userId);
}

export async function deleteChart(db: D1Database, userId: string, id: string): Promise<void> {
  await db.prepare("DELETE FROM charts WHERE user_id = ? AND id = ?").bind(userId, id).run();
}
