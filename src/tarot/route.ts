// Tarot API, behind TVBT_TAROT ("1" turns it on; off, every path answers 404 as if it did not exist).
//   POST /api/tarot/draw {spread: 1|3, reversals?: boolean}            a new shuffle: {id, fan: 78}. The order stays here (only the seed is stored).
//   POST /api/tarot/draw {id, picks: [positions], question?: string}   the cards under the picked fan positions, once; asked again, the same cards.
//                                                                       The question is read for the notice and then dropped, never stored here.
//   GET  /api/tarot/x/<id>                                              a saved draw, for a share link; its question only if the owner chose to show it.
//   GET/POST/DELETE /api/me/tarot                                       the signed-in reader's saved draws (save = keep the draw, and the question if given).
// Free: 3 shuffles a day (Vietnam date) per account, per address for guests. Writes carry the x-tvbt header, as the account routes do.
import { randomToken, sha256, type User } from "../auth/session.ts";
import { DECK_SIZE, publicCard } from "./deck.ts";
import { isSpread, newSeed, reveal, SPREADS, validPicks, type SpreadSize } from "./draw.ts";
import { cleanQuestion, noticesFor, TAROT_HEADER } from "./guard.ts";
import { readingFor, SOURCE } from "./reading.ts";

export const DAILY_FREE = 3;
export const MAX_SAVED = 200;
const PENDING_MS = 3600_000;                 // a shuffle must be revealed within an hour
const KEEP_UNSAVED_MS = 2 * 86400_000;
export const DRAW_ID = /^[A-Za-z0-9_-]{22}$/;

// Same statements as migrations/app/0011_tarot.sql, run once per isolate (as account/route.ts does) so the route works before the migration.
export const SCHEMA = [
  "CREATE TABLE IF NOT EXISTS tarot_draws (id TEXT PRIMARY KEY, seed TEXT NOT NULL, spread INTEGER NOT NULL, reversals INTEGER NOT NULL DEFAULT 1, picks_json TEXT, user_id TEXT REFERENCES users(id) ON DELETE CASCADE, saved INTEGER NOT NULL DEFAULT 0, question TEXT, show_question INTEGER NOT NULL DEFAULT 0, created_at INTEGER NOT NULL, revealed_at INTEGER, saved_at INTEGER)",
  "CREATE INDEX IF NOT EXISTS tarot_draws_user ON tarot_draws(user_id, saved, saved_at)",
  "CREATE INDEX IF NOT EXISTS tarot_draws_unsaved ON tarot_draws(saved, created_at)",
  "CREATE TABLE IF NOT EXISTS tarot_daily (key TEXT NOT NULL, day TEXT NOT NULL, n INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (key, day))",
];
const ready = new WeakMap<D1Database, Promise<unknown>>();
function ensureSchema(db: D1Database): Promise<unknown> {
  let p = ready.get(db);
  if (!p) { p = db.batch(SCHEMA.map(s => db.prepare(s))).catch(e => { ready.delete(db); throw e; }); ready.set(db, p); }
  return p;
}

export const isTarotPath = (p: string) => p.startsWith("/api/tarot/") || p === "/api/me/tarot";

export interface TarotDeps { db?: D1Database; enabled: boolean; user: User | null; now?: () => number }

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "private, no-store", "x-robots-tag": "noindex" } });
const NOT_FOUND = () => json({ detail: "not found" }, 404);

interface Row { id: string; seed: string; spread: number; reversals: number; picks_json: string | null; user_id: string | null; saved: number;
  question: string | null; show_question: number; created_at: number; revealed_at: number | null; saved_at: number | null }

/** The Vietnam calendar date (UTC+7) of a moment: the day the free draws are counted in. */
export const vnDay = (ms: number) => new Date(ms + 7 * 3600_000).toISOString().slice(0, 10);

/** One more draw for this reader today, if the free allowance has room: the count and the check are one statement. */
async function takeDraw(db: D1Database, key: string, day: string): Promise<number | null> {
  const r = await db.prepare("INSERT INTO tarot_daily (key, day, n) VALUES (?, ?, 1) ON CONFLICT (key, day) DO UPDATE SET n = n + 1 WHERE n < ?")
    .bind(key, day, DAILY_FREE).run();
  if (!(r.meta.changes ?? 0)) return null;
  const n = (await db.prepare("SELECT n FROM tarot_daily WHERE key = ? AND day = ?").bind(key, day).first<{ n: number }>())?.n ?? DAILY_FREE;
  return Math.max(0, DAILY_FREE - n);
}

const readerKey = async (request: Request, user: User | null) =>
  user ? "u:" + user.id : "ip:" + (await sha256("tvbt-tarot:" + (request.headers.get("cf-connecting-ip") ?? ""))).slice(0, 32);

/** The cards of a revealed draw, each with its reading from the sourced pack (or the neutral line). */
async function cardsOf(row: Row) {
  const picks = JSON.parse(row.picks_json ?? "[]") as number[];
  return (await reveal(row.seed, row.reversals === 1, picks)).map(d => ({
    slot: d.slot, pick: d.pick, reversed: d.reversed, card: publicCard(d.card), reading: readingFor(d.card, d.reversed),
  }));
}

async function drawView(row: Row, opts: { question?: string | null } = {}) {
  const question = opts.question ?? null;
  return {
    id: row.id, spread: row.spread, reversals: row.reversals === 1, header: TAROT_HEADER, source: SOURCE.cite,
    layout_note: row.spread === 3 ? "Ba vị trí chỉ là cách bày bài, không mang nghĩa riêng: sách nguồn không định nghĩa quá khứ, hiện tại, tương lai." : null,
    cards: await cardsOf(row), notices: noticesFor(question), created_at: row.created_at, saved: row.saved === 1,
  };
}

const getRow = (db: D1Database, id: string) => db.prepare("SELECT * FROM tarot_draws WHERE id = ?").bind(id).first<Row>();

export async function handleTarot(request: Request, deps: TarotDeps): Promise<Response> {
  if (!deps.enabled) return NOT_FOUND();
  const { db, user } = deps;
  if (!db) return json({ detail: "tarot is not configured" }, 503);
  await ensureSchema(db);
  const now = (deps.now ?? Date.now)();
  const path = new URL(request.url).pathname;
  if (request.method !== "GET" && request.headers.get("x-tvbt") !== "1") return json({ detail: "missing x-tvbt header" }, 403);
  const body = async () => { const b = await request.json().catch(() => null); return b && typeof b === "object" && !Array.isArray(b) ? b as Record<string, unknown> : null; };

  if (path === "/api/tarot/draw") {
    if (request.method !== "POST") return json({ detail: "POST only" }, 405);
    const b = await body();
    if (!b) return json({ detail: "body must be a JSON object" }, 400);

    if (b.id === undefined) {                                             // a new shuffle
      const spread = b.spread === undefined ? 1 : b.spread;
      if (!isSpread(spread)) return json({ detail: "spread must be 1 or 3" }, 400);
      if (b.reversals !== undefined && typeof b.reversals !== "boolean") return json({ detail: "reversals must be true or false" }, 400);
      const remaining = await takeDraw(db, await readerKey(request, user), vnDay(now));
      if (remaining === null) return json({ detail: `Bạn đã rút đủ ${DAILY_FREE} lượt miễn phí hôm nay. Mời bạn quay lại ngày mai.`, limit: DAILY_FREE, remaining: 0 }, 429);
      const id = randomToken(16);
      await db.batch([
        db.prepare("INSERT INTO tarot_draws (id, seed, spread, reversals, user_id, created_at) VALUES (?, ?, ?, ?, ?, ?)")
          .bind(id, newSeed(), spread, b.reversals === false ? 0 : 1, user?.id ?? null, now),
        db.prepare("DELETE FROM tarot_draws WHERE saved = 0 AND created_at < ?").bind(now - KEEP_UNSAVED_MS),
        db.prepare("DELETE FROM tarot_daily WHERE day < ?").bind(vnDay(now - 2 * 86400_000)),
      ]);
      return json({ id, spread, reversals: b.reversals !== false, fan: DECK_SIZE, pick: SPREADS[spread as SpreadSize].cards, remaining, limit: DAILY_FREE, header: TAROT_HEADER });
    }

    if (typeof b.id !== "string" || !DRAW_ID.test(b.id)) return NOT_FOUND();      // a reveal
    let row = await getRow(db, b.id);
    if (!row) return NOT_FOUND();
    const question = cleanQuestion(b.question);
    if (row.picks_json === null) {
      if (now - row.created_at > PENDING_MS) return json({ detail: "Lượt xáo bài này đã quá hạn; mời bạn xáo lại." }, 410);
      if (!validPicks(b.picks, row.spread as SpreadSize)) return json({ detail: `picks must be ${row.spread} distinct positions from 0 to ${DECK_SIZE - 1}` }, 400);
      await db.prepare("UPDATE tarot_draws SET picks_json = ?, revealed_at = ? WHERE id = ? AND picks_json IS NULL").bind(JSON.stringify(b.picks), now, row.id).run();
      row = (await getRow(db, row.id))!;                                 // a concurrent reveal may have won: its picks stand
    }
    return json(await drawView(row, { question }));
  }

  const x = path.match(/^\/api\/tarot\/x\/([^/]+)$/);
  if (x) {
    if (request.method !== "GET") return json({ detail: "GET only" }, 405);
    const row = DRAW_ID.test(x[1]) ? await getRow(db, x[1]) : null;
    if (!row || row.saved !== 1 || row.picks_json === null) return json({ detail: "Liên kết không tồn tại hoặc chủ lượt rút đã xóa." }, 404);
    const shown = row.show_question === 1 ? row.question : null;
    return json({ ...(await drawView(row, { question: shown })), question: shown, question_hidden: !!row.question && !shown, saved: undefined });
  }

  if (path === "/api/me/tarot") {
    if (!user) return json({ detail: "sign in required" }, 401);
    if (request.method === "GET") {
      const { results } = await db.prepare("SELECT * FROM tarot_draws WHERE user_id = ? AND saved = 1 ORDER BY saved_at DESC LIMIT 100").bind(user.id).all<Row>();
      return json({ draws: await Promise.all(results.map(async r => ({ ...(await drawView(r, { question: r.question })), question: r.question, show_question: r.show_question === 1, saved_at: r.saved_at }))) });
    }
    if (request.method === "POST") {
      const b = await body();
      if (!b || typeof b.id !== "string" || !DRAW_ID.test(b.id)) return NOT_FOUND();
      if (b.show_question !== undefined && typeof b.show_question !== "boolean") return json({ detail: "show_question must be true or false" }, 400);
      const row = await getRow(db, b.id);
      if (!row || (row.user_id && row.user_id !== user.id)) return NOT_FOUND();
      if (row.picks_json === null) return json({ detail: "draw not revealed yet" }, 409);
      if (row.saved !== 1) {
        const n = (await db.prepare("SELECT COUNT(*) AS n FROM tarot_draws WHERE user_id = ? AND saved = 1").bind(user.id).first<{ n: number }>())?.n ?? 0;
        if (n >= MAX_SAVED) return json({ detail: `Bạn đã lưu ${MAX_SAVED} lượt rút; hãy xóa bớt trước khi lưu thêm.` }, 409);
      }
      const question = cleanQuestion(b.question);
      await db.prepare("UPDATE tarot_draws SET user_id = ?, saved = 1, question = ?, show_question = ?, saved_at = ? WHERE id = ?")
        .bind(user.id, question, question && b.show_question === true ? 1 : 0, row.saved_at ?? now, row.id).run();
      const saved = (await getRow(db, row.id))!;
      return json({ ...(await drawView(saved, { question })), question, show_question: saved.show_question === 1, share_path: `/tarot/?x=${saved.id}` });
    }
    if (request.method === "DELETE") {
      const id = new URL(request.url).searchParams.get("id") ?? "";
      if (!DRAW_ID.test(id)) return NOT_FOUND();
      const r = await db.prepare("DELETE FROM tarot_draws WHERE id = ? AND user_id = ?").bind(id, user.id).run();
      return (r.meta.changes ?? 0) > 0 ? json({ ok: true }) : NOT_FOUND();
    }
    return json({ detail: "GET, POST or DELETE" }, 405);
  }
  return NOT_FOUND();
}
