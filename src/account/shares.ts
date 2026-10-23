// Share links for saved charts. The owner creates, lists, switches "Ẩn thông tin sinh" and revokes; anyone holding the id can view.
// With hide_birth the viewer never receives the name, the birth date or the hour: the Worker merges the stored birth into each request
// (/api/share/<id>/<endpoint>) and strips the fields that echo it. The four pillars and the star positions are the chart itself and stay;
// the page says that someone who reads Can Chi can still work the date back from them.
import { randomToken } from "../auth/session.ts";

export const MAX_ACTIVE_SHARES = 50;
export const SHARE_ID = /^[A-Za-z0-9_-]{22}$/;
// endpoints a shared view may run, and the only request fields a viewer may set (never a birth field)
export const SHARE_ENDPOINTS = new Set(["chart", "reasoning", "analysis", "synthesis", "interpretation", "interpret", "year", "formations"]);
const VIEWER_FIELDS: Record<string, (v: unknown) => boolean> = {
  to_year: v => Number.isInteger(v) && (v as number) >= 1900 && (v as number) <= 2200,
  chapter: v => typeof v === "string" && /^[a-z_]{1,30}$/.test(v),
  mode: v => typeof v === "string" && /^[a-z_]{1,20}$/.test(v),
  experimental: v => typeof v === "boolean",
  dignity_school: v => v === "khao_luan" || v === "toan_thu" || v === "thuc_hanh",   // the dignity table the viewer picked on the board
  // where the books disagree on a calculation (engine/tvbt/tuvi.py VARIANTS): the source the viewer picked
  tu_hoa_table: v => v === "KL" || v === "TH" || v === "TT_WS",
  tieu_han_rule: v => v === "TH" || v === "KL",
  luu_ha_table: v => v === "board" || v === "KL" || v === "TH",
};
// what a hidden share keeps of the birth request: enough for the page to lay out years and ages, nothing that pins the day
const BIRTH = ["month", "day", "hour", "minute", "longitude", "use_true_solar_time"];

export interface ShareRow { id: string; chart_id: string; label: string; rel: string; hide: boolean; created_at: number }
interface Resolved { hide: boolean; label: string; rel: string; req: Record<string, unknown> }

export async function createShare(db: D1Database, userId: string, chartId: string, hide: boolean): Promise<ShareRow | "no_chart" | "too_many"> {
  const c = await db.prepare("SELECT fp, label, rel FROM charts WHERE user_id = ? AND id = ?").bind(userId, chartId).first<{ fp: string; label: string; rel: string }>();
  if (!c) return "no_chart";
  const n = (await db.prepare("SELECT COUNT(*) AS n FROM shares WHERE user_id = ? AND revoked_at IS NULL").bind(userId).first<{ n: number }>())?.n ?? 0;
  if (n >= MAX_ACTIVE_SHARES) return "too_many";
  const id = randomToken(16), now = Date.now();
  await db.prepare("INSERT INTO shares (id, user_id, chart_fp, hide_birth, created_at) VALUES (?, ?, ?, ?, ?)").bind(id, userId, c.fp, hide ? 1 : 0, now).run();
  return { id, chart_id: chartId, label: c.label, rel: c.rel, hide, created_at: now };
}

/** The owner's live links (revoked ones and links whose chart was deleted are left out). */
export async function listShares(db: D1Database, userId: string): Promise<ShareRow[]> {
  const { results } = await db.prepare(
    "SELECT s.id, c.id AS chart_id, c.label, c.rel, s.hide_birth, s.created_at FROM shares s JOIN charts c ON c.user_id = s.user_id AND c.fp = s.chart_fp " +
    "WHERE s.user_id = ? AND s.revoked_at IS NULL ORDER BY s.created_at DESC").bind(userId).all<{ id: string; chart_id: string; label: string; rel: string; hide_birth: number; created_at: number }>();
  return results.map(r => ({ id: r.id, chart_id: r.chart_id, label: r.label, rel: r.rel, hide: r.hide_birth === 1, created_at: r.created_at }));
}

/** Owner-only updates: the WHERE carries user_id, so another account's id changes nothing and reads as not found. */
export async function setShareHide(db: D1Database, userId: string, id: string, hide: boolean): Promise<boolean> {
  const r = await db.prepare("UPDATE shares SET hide_birth = ? WHERE id = ? AND user_id = ? AND revoked_at IS NULL").bind(hide ? 1 : 0, id, userId).run();
  return (r.meta.changes ?? 0) > 0;
}
export async function revokeShare(db: D1Database, userId: string, id: string): Promise<boolean> {
  const r = await db.prepare("UPDATE shares SET revoked_at = ? WHERE id = ? AND user_id = ? AND revoked_at IS NULL").bind(Date.now(), id, userId).run();
  return (r.meta.changes ?? 0) > 0;
}

async function resolve(db: D1Database, id: string): Promise<Resolved | null> {
  if (!SHARE_ID.test(id)) return null;
  const r = await db.prepare(
    "SELECT s.hide_birth, c.label, c.rel, c.req_json FROM shares s JOIN charts c ON c.user_id = s.user_id AND c.fp = s.chart_fp WHERE s.id = ? AND s.revoked_at IS NULL")
    .bind(id).first<{ hide_birth: number; label: string; rel: string; req_json: string }>();
  return r && { hide: r.hide_birth === 1, label: r.label, rel: r.rel, req: JSON.parse(r.req_json) };
}

export const maskReq = (req: Record<string, unknown>) => Object.fromEntries(Object.entries(req).filter(([k]) => !BIRTH.includes(k)));

/** Removes what echoes the birth moment from an engine response: calculation traces (they print the input), and the lunar day and month. */
export function scrub(x: unknown): unknown {
  if (Array.isArray(x)) return x.map(scrub);
  if (!x || typeof x !== "object") return x;
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(x as Record<string, unknown>)) {
    if (k === "trace" || k === "normalization_trace") out[k] = { steps: [] };
    else if (k === "input" || k === "birth" || k === "request") continue;
    else if (k === "lunar" && v && typeof v === "object") out[k] = { year: (v as Record<string, unknown>).year, month: null, day: null, leap: false, hidden: true };
    else out[k] = scrub(v);
  }
  return out;
}

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "private, no-store", "x-robots-tag": "noindex" } });
const GONE = { detail: "Liên kết chia sẻ không tồn tại hoặc đã bị chủ lá số thu hồi." };

export type Forward = (path: string, body: Record<string, unknown>) => Promise<Response>;

/** GET /api/share/<id>: what the viewer may know. POST /api/share/<id>/<endpoint>: runs the engine on the stored birth. */
export async function handleShare(request: Request, db: D1Database, forward: Forward): Promise<Response> {
  const m = new URL(request.url).pathname.match(/^\/api\/share\/([^/]+)(?:\/([a-z-]+))?$/);
  if (!m) return json({ detail: "not found" }, 404);
  const s = await resolve(db, m[1]);
  if (!s) return json(GONE, 404);
  if (!m[2]) {
    if (request.method !== "GET") return json({ detail: "GET only" }, 405);
    return json(s.hide ? { hide: true, label: null, rel: s.rel, req: maskReq(s.req) } : { hide: false, label: s.label, rel: s.rel, req: s.req });
  }
  if (request.method !== "POST") return json({ detail: "POST only" }, 405);
  if (!SHARE_ENDPOINTS.has(m[2])) return json({ detail: "not found" }, 404);
  const body = await request.json().catch(() => ({})) as Record<string, unknown>;
  const extra = Object.fromEntries(Object.entries(body && typeof body === "object" ? body : {}).filter(([k, v]) => VIEWER_FIELDS[k]?.(v)));
  const res = await forward("/api/" + m[2], { ...s.req, ...extra });
  if (!s.hide || !res.ok) return res;
  const data = await res.json().catch(() => null);
  return data === null ? json({ detail: "engine error" }, 502) : json(scrub(data));
}
