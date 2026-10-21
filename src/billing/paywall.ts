// Paid report chapters: opening them with coins, and the paywall over /api/interpret. The Worker computes (or reads from cache) the whole
// reading, then cuts every paid chapter the signed-in reader has not opened down to a short preview BEFORE it leaves the server. The
// browser is told what is locked and how to open it; it is never trusted to hide anything itself.
import { cleanReq } from "../auth/charts.ts";
import { CHAPTER_TITLES, PREVIEW_PARAGRAPHS, PREVIEW_SENTENCES, isPaidChapter, periodOf, planById, planChapters, plansFor, type PaidChapter } from "./config.ts";

/** Evidence-mode chapters that cover several palaces need every one of them open. */
const GROUPS: Record<string, PaidChapter[]> = { gia_dao: ["phu_mau", "huynh_de", "tu_tuc"], di_no_tat: ["thien_di", "no_boc", "tat_ach"] };
/** The paid chapters a served chapter id needs; [] when it is free. */
export const needs = (id: unknown): PaidChapter[] => typeof id !== "string" ? [] : GROUPS[id] ?? (isPaidChapter(id) ? [id] : []);

export async function unlockedChapters(db: D1Database, userId: string, fp: string): Promise<Set<string>> {
  const { results } = await db.prepare("SELECT chapter FROM unlocks WHERE user_id = ? AND fp = ?").bind(userId, fp).all<{ chapter: string }>();
  return new Set(results.map(r => r.chapter));
}

export type UnlockResult =
  | { ok: true; charged: number; chapters: PaidChapter[]; already: boolean }
  | { ok: false; reason: "bad_plan" | "insufficient"; need?: number };

/** Opens a plan's chapters for one chart. One D1 batch (a transaction): the ledger row is written only when the wallet holds enough, the
 *  wallet is charged only when that row was written, and the chapters are opened only when the charge applied. The ledger ref is the
 *  same for the same purchase, so a double click charges once. Chapters already open cost nothing more; a plan whose chapters are all
 *  open already charges nothing. */
export async function buyPlan(db: D1Database, userId: string, fp: string, planId: unknown, chapter?: unknown, now = Date.now()): Promise<UnlockResult> {
  const plan = planById(planId), chapters = plan && planChapters(plan, chapter);
  if (!plan || !chapters || !fp) return { ok: false, reason: "bad_plan" };
  const have = await unlockedChapters(db, userId, fp), missing = chapters.filter(c => !have.has(c));
  if (!missing.length) return { ok: true, charged: 0, chapters, already: true };
  await db.prepare("INSERT OR IGNORE INTO wallets (user_id) VALUES (?)").bind(userId).run();
  const base = `unlock:${fp}:${plan.id}${plan.chapters === "one" ? `:${chapter}` : ""}`;
  // a purchase bought before and later taken back (rows removed by an admin) can be bought again under a new ref
  const prior = (await db.prepare("SELECT COUNT(*) AS n FROM ledger WHERE user_id = ? AND (ref = ? OR ref LIKE ?)").bind(userId, base, `${base}#%`).first<{ n: number }>())?.n ?? 0;
  const ref = prior ? `${base}#${prior + 1}` : base, cost = plan.coins;
  const [led, upd] = await db.batch([
    db.prepare("INSERT OR IGNORE INTO ledger (user_id, kind, usage, delta, period, ref, created_at) SELECT ?1, 'coin_spend', ?2, ?3, ?4, ?5, ?6 " +
      "WHERE (SELECT coins FROM wallets WHERE user_id = ?1) >= ?7").bind(userId, `unlock:${plan.id}`, -cost, periodOf(now), ref, now, cost),
    db.prepare("UPDATE wallets SET coins = coins - ?1, updated_at = ?2 WHERE user_id = ?3 AND coins >= ?1 AND changes() > 0").bind(cost, now, userId),
    db.prepare("INSERT OR IGNORE INTO unlocks (user_id, fp, chapter, plan, ledger_ref, created_at) SELECT ?1, ?2, value, ?3, ?4, ?5 FROM json_each(?6) WHERE changes() > 0")
      .bind(userId, fp, plan.id, ref, now, JSON.stringify(missing)),
  ]);
  if ((led.meta?.changes ?? 0) > 0 && (upd.meta?.changes ?? 0) > 0) return { ok: true, charged: cost, chapters, already: false };
  // the same purchase landed a moment ago (double click): nothing more was charged
  if (await db.prepare("SELECT 1 AS x FROM ledger WHERE user_id = ? AND ref = ?").bind(userId, ref).first()) return { ok: true, charged: 0, chapters, already: true };
  return { ok: false, reason: "insufficient", need: cost };
}

// ---------- the filter ----------
export interface Access { signedIn: boolean; open: Set<string> }
type Json = Record<string, any>;

const lockInfo = (id: string, need: PaidChapter[], a: Access, shown: number, total: number) => {
  // a group chapter (evidence mode) is offered through the plans that open its first palace
  const first = need[0];
  return { chapter: id, title: CHAPTER_TITLES[id] ?? id, signedIn: a.signedIn, shown, total, missing: need.filter(c => !a.open.has(c)),
    plans: plansFor(first).map(p => ({ id: p.id, name: p.name, coins: p.coins, chapter: p.chapters === "one" ? first : undefined })) };
};

/** The first paragraphs of a chapter, never most of it: PREVIEW_PARAGRAPHS of a long chapter, one of a short one, and of a one-paragraph
 *  chapter its first sentences (never all of them). */
export function preview(ps: Json[]): Json[] {
  if (ps.length >= 2 * PREVIEW_PARAGRAPHS) return ps.slice(0, PREVIEW_PARAGRAPHS);
  if (ps.length >= 2) return ps.slice(0, 1);
  const ss: Json[] = Array.isArray(ps[0]?.sentences) ? ps[0].sentences : [];
  const n = Math.min(PREVIEW_SENTENCES, ss.length - 1);
  if (n < 1) return [];
  const s = ss.slice(0, n);
  return [{ ...ps[0], sentences: s, text: s.map(x => x.text).join(" ") }];
}

/** One served chapter, cut to its preview when it is paid and not open. Only listed fields survive, so nothing new added to a chapter
 *  later can leak through a lock by accident. */
export function gateChapter(c: Json, a: Access): Json {
  const need = needs(c?.chapter);
  if (!need.length) return c;
  if (need.every(x => a.open.has(x))) return { ...c, unlocked: true };
  const all: Json[] = Array.isArray(c.paragraphs) ? c.paragraphs : [], kept = preview(all);
  const used = new Set<string>(), concepts = new Set<string>();
  for (const p of kept) for (const s of p.sentences ?? []) { for (const r of s.trace?.rules ?? []) used.add(r); for (const k of s.trace?.concepts ?? []) concepts.add(k); }
  const pick = (o: Json | undefined, keys: Set<string>) => Object.fromEntries(Object.entries(o ?? {}).filter(([k]) => keys.has(k)));
  const out: Json = {};
  for (const k of ["engine", "kbVersion", "chapter", "palace", "title", "schema", "order", "draft", "pass"]) if (k in c) out[k] = c[k];
  out.paragraphs = kept;
  out.text = kept.map(p => p.text ?? "").join("\n\n");
  out.issues = [];
  out.evidence = { resolved: [], tensions: [], unused: [], divergences: [], limits: [], rules: pick(c.evidence?.rules, used), concepts: pick(c.evidence?.concepts, concepts) };
  if (Array.isArray(c.decades)) out.decades = c.decades;                               // ages and palaces: facts already on the board
  if (Array.isArray(c.starts)) out.starts = c.starts.filter((i: number) => i < kept.length);
  if (c.chapters && typeof c.chapters === "object") out.chapters = { "nhat-chu": kept };   // Bát Tự: the preview heads its first chapter
  out.locked = lockInfo(String(c.chapter), need, a, kept.length, all.length);
  return out;
}

/** A whole /api/interpret answer: one chapter, or {chapters: [...]} for chapter "all". */
export function gateOutput(out: Json, a: Access): Json {
  if (Array.isArray(out?.chapters) && !("paragraphs" in out)) return { ...out, chapters: out.chapters.map((c: Json) => gateChapter(c, a)) };
  return gateChapter(out, a);
}

/** The paywall over a finished /api/interpret response: the reader's open chapters for the chart in the request body, then gateOutput.
 *  Signed out, or with a body that is not a birth record, nothing paid is open. A failing lookup also opens nothing (fail closed). */
export async function gateResponse(res: Response, body: unknown, db: D1Database | undefined, user: { id: string } | null): Promise<Response> {
  if (!res.ok) return res;
  const birth = cleanReq(body);
  const open = user && birth && db ? await unlockedChapters(db, user.id, birth.fp).catch(() => new Set<string>()) : new Set<string>();
  const out = await res.json() as Json;
  const headers = new Headers(res.headers);
  headers.set("cache-control", "private, no-store");
  headers.delete("content-length");
  return new Response(JSON.stringify(gateOutput(out, { signedIn: !!user, open })), { status: res.status, headers });
}
