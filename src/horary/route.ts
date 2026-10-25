// Saved horary questions for signed-in users: GET/POST /api/me/horary, DELETE /api/me/horary/<id>. The engine is not called here:
// the page reopens a saved question by sending its stored moment and frame to /api/horary/judge with the stored fingerprint.
import { currentUser } from "../auth/session.ts";

const SCHEMA = [
  "CREATE TABLE IF NOT EXISTS horary_questions (user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, id TEXT NOT NULL, moment_json TEXT NOT NULL, frame_json TEXT NOT NULL, fingerprint TEXT NOT NULL, engine TEXT NOT NULL, verdict TEXT NOT NULL, saved_at INTEGER NOT NULL, PRIMARY KEY (user_id, id))",
  "CREATE INDEX IF NOT EXISTS horary_user_saved ON horary_questions(user_id, saved_at)",
];
const ready = new WeakMap<D1Database, Promise<unknown>>();
export function ensureHorarySchema(db: D1Database): Promise<unknown> {
  let p = ready.get(db);
  if (!p) { p = db.batch(SCHEMA.map(s => db.prepare(s))).catch(e => { ready.delete(db); throw e; }); ready.set(db, p); }
  return p;
}
export const MAX_SAVED = 200;
const ID = /^[a-z0-9-]{8,40}$/;
const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
export const isHoraryPath = (p: string) => p === "/api/me/horary" || p.startsWith("/api/me/horary/");

const int = (v: unknown, lo: number, hi: number) => typeof v === "number" && Number.isInteger(v) && v >= lo && v <= hi;
const num = (v: unknown, lo: number, hi: number) => typeof v === "number" && Number.isFinite(v) && v >= lo && v <= hi;
const str = (v: unknown, max: number, rx?: RegExp) => typeof v === "string" && v.length <= max && (!rx || rx.test(v));

/** The stored item, field by field (nothing else from the body is kept), or the reason it is refused. */
export function cleanItem(b: any): string | { id: string; moment: Record<string, unknown>; frame: Record<string, unknown>; fingerprint: string; engine: string; verdict: string } {
  if (!b || typeof b !== "object") return "body must be an object";
  if (!str(b.id, 40, ID)) return "bad id";
  const m = b.moment, f = b.frame;
  if (!m || !int(m.year, 1600, 2150) || !int(m.month, 1, 12) || !int(m.day, 1, 31) || !int(m.hour, 0, 23) || !int(m.minute, 0, 59)
      || !(m.second === undefined || int(m.second, 0, 59)) || !num(m.lat, -89.9, 89.9) || !num(m.lon, -180, 180)
      || !str(m.tz, 64, /^[A-Za-z_+\-/0-9]+$/) || !str(m.place ?? "", 120)
      || !(m.house_system === undefined || str(m.house_system, 20, /^(regiomontanus|alcabitius|whole_sign|placidus|equal|porphyry)$/))) return "bad moment";
  if (!f || !str(f.text, 500) || f.text.length < 3 || !str(f.topic, 20, /^[a-z_]+$/) || !str(f.subtype, 20, /^[a-z_]+$/)
      || !str(f.party ?? "self", 20, /^[a-z_]+$/)) return "bad frame";
  if (!str(b.fingerprint, 32, /^[0-9a-f]{16}$/) || !str(b.engine, 32, /^horary-[0-9.]+$/) || !str(b.verdict, 60)) return "bad chart reference";
  const moment = { year: m.year, month: m.month, day: m.day, hour: m.hour, minute: m.minute, second: m.second ?? 0, lat: m.lat, lon: m.lon,
    tz: m.tz, place: m.place ?? "", house_system: m.house_system ?? "regiomontanus", school: "lilly" };
  const frame = { text: f.text, topic: f.topic, subtype: f.subtype, party: f.party ?? "self", confirmed: true };
  return { id: b.id, moment, frame, fingerprint: b.fingerprint, engine: b.engine, verdict: b.verdict };
}

export async function handleHorary(request: Request, db: D1Database | undefined): Promise<Response> {
  if (!db) return json({ detail: "accounts are not configured" }, 404);
  await ensureHorarySchema(db);
  const user = await currentUser(db, request);
  if (!user) return json({ detail: "sign in required" }, 401);
  if (request.method !== "GET" && request.headers.get("x-tvbt") !== "1") return json({ detail: "missing x-tvbt header" }, 403);
  const path = new URL(request.url).pathname;
  if (path === "/api/me/horary") {
    if (request.method === "GET") {
      const r = await db.prepare("SELECT id, moment_json, frame_json, fingerprint, engine, verdict, saved_at FROM horary_questions WHERE user_id = ? ORDER BY saved_at DESC LIMIT ?")
        .bind(user.id, MAX_SAVED).all<any>();
      return json({ items: (r.results ?? []).map(x => ({ id: x.id, moment: JSON.parse(x.moment_json), frame: JSON.parse(x.frame_json),
        fingerprint: x.fingerprint, engine: x.engine, verdict: x.verdict, saved_at: x.saved_at })) });
    }
    if (request.method !== "POST") return json({ detail: "GET or POST" }, 405);
    const it = cleanItem(await request.json().catch(() => null));
    if (typeof it === "string") return json({ detail: it }, 400);
    const n = await db.prepare("SELECT COUNT(*) AS n FROM horary_questions WHERE user_id = ?").bind(user.id).first<{ n: number }>();
    const exists = await db.prepare("SELECT 1 AS x FROM horary_questions WHERE user_id = ? AND id = ?").bind(user.id, it.id).first();
    if (!exists && (n?.n ?? 0) >= MAX_SAVED) return json({ detail: `tối đa ${MAX_SAVED} câu hỏi đã lưu; hãy xóa bớt` }, 409);
    await db.prepare("INSERT INTO horary_questions (user_id, id, moment_json, frame_json, fingerprint, engine, verdict, saved_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
      + "ON CONFLICT(user_id, id) DO UPDATE SET moment_json = excluded.moment_json, frame_json = excluded.frame_json, fingerprint = excluded.fingerprint, engine = excluded.engine, verdict = excluded.verdict, saved_at = excluded.saved_at")
      .bind(user.id, it.id, JSON.stringify(it.moment), JSON.stringify(it.frame), it.fingerprint, it.engine, it.verdict, Date.now()).run();
    return json({ ok: true, id: it.id });
  }
  const id = decodeURIComponent(path.slice("/api/me/horary/".length));
  if (!ID.test(id)) return json({ detail: "bad id" }, 400);
  if (request.method !== "DELETE") return json({ detail: "DELETE" }, 405);
  await db.prepare("DELETE FROM horary_questions WHERE user_id = ? AND id = ?").bind(user.id, id).run();
  return json({ ok: true });
}
