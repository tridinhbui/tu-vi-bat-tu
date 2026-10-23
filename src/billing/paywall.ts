// The three reading tiers (config.ts): guests read the first third of each chapter's main reading, members read every main reading, and the
// "Đọc sâu (theo sách)" part of a chapter needs that chapter opened with xu. The Worker computes (or reads from cache) the WHOLE reading — the
// viewer is never part of a cache key — and this file cuts it per request, after the cache, BEFORE it leaves the server. The browser is told
// what was held back and how to get it; it is never trusted to hide anything itself. Every filtered response is `private, no-store`.
import { cleanReq } from "../auth/charts.ts";
import { currentUser } from "../auth/session.ts";
import { BAZI_TAB_TITLES, CHAPTER_TITLES, guestShown, isDeepChapter, periodOf, planById, planChapters, plansFor, type DeepChapter, type Tier } from "./config.ts";

export async function unlockedChapters(db: D1Database, userId: string, fp: string): Promise<Set<string>> {
  const { results } = await db.prepare("SELECT chapter FROM unlocks WHERE user_id = ? AND fp = ?").bind(userId, fp).all<{ chapter: string }>();
  return new Set(results.map(r => r.chapter));
}

export type UnlockResult =
  | { ok: true; charged: number; chapters: DeepChapter[]; already: boolean }
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

// ---------- who is reading ----------
/** `open`: the chapters whose Đọc sâu part this member opened for the chart in the request. `shared`: the reader came through a share link. */
export interface Access { tier: Tier; open: Set<string>; shared?: boolean }
export const GUEST: Access = Object.freeze({ tier: "guest", open: new Set<string>() }) as Access;
/** A share link's viewer reads at the guest tier, whoever they are: the link opens someone else's chart. */
export const SHARED: Access = Object.freeze({ tier: "guest", open: new Set<string>(), shared: true }) as Access;

/** The tier for one request. Signed out: guest. Signed in: member, with the chapters opened for the chart in the body (a body that is not a
 *  birth record, or a failing lookup, opens nothing: fail closed). */
export async function accessFor(db: D1Database | undefined, user: { id: string } | null, body: unknown): Promise<Access> {
  if (!user) return GUEST;
  const birth = cleanReq(body);
  const open = birth && db ? await unlockedChapters(db, user.id, birth.fp).catch(() => new Set<string>()) : new Set<string>();
  return { tier: "member", open };
}

// ---------- the filter ----------
type Json = Record<string, any>;
/** A paragraph of the Đọc sâu part: Tử Vi luận cung `deep`, Bát Tự depth 'sau'. */
export const isDeep = (p: Json) => p?.deep === true || p?.depth === "sau";

interface Cut { kept: Json[]; main: number; mainShown: number; deep: number; deepShown: number }
/** The paragraphs this reader gets of one run, in their order: a guest the first third of the main ones, a member all of them; the Đọc sâu
 *  ones only when `deepOpen`. */
function cutParagraphs(ps: Json[], tier: Tier, deepOpen: boolean): Cut {
  const main = ps.filter(p => !isDeep(p)), deep = ps.filter(isDeep);
  const keepMain = new Set(tier === "guest" ? main.slice(0, guestShown(main.length)) : main);
  const keepDeep = tier === "member" && deepOpen;
  const kept = ps.filter(p => keepMain.has(p) || (keepDeep && isDeep(p)));
  return { kept, main: main.length, mainShown: keepMain.size, deep: deep.length, deepShown: keepDeep ? deep.length : 0 };
}
const hidden = (c: Cut) => c.main - c.mainShown + c.deep - c.deepShown;

/** What the lock card shows: a guest is asked to sign in (or, on a share link, told why the reading is short); a member is offered the
 *  plans that open the chapter's Đọc sâu part. Counts only: no word of the held-back text. */
function lockInfo(chapter: string, title: string, a: Access, c: Cut): Json {
  const base = { chapter, title, tier: a.tier, shown: c.mainShown, total: c.main, deep: c.deep - c.deepShown };
  if (a.tier === "guest") return { ...base, ...(a.shared ? { shared: true } : {}) };
  const sold = isDeepChapter(chapter.split(":")[0]) ? chapter.split(":")[0] as DeepChapter : null;
  return { ...base, plans: sold ? plansFor(sold).map(p => ({ id: p.id, name: p.name, coins: p.coins, chapter: p.chapters === "one" ? sold : undefined })) : [] };
}

const TOP_KEEP = ["engine", "kbVersion", "chapter", "palace", "title", "schema", "order", "draft", "pass", "luan", "card"];
const MEMBER_KEEP = ["theses", "advice"];

/** One served chapter for this reader. Nothing held back: the chapter as it was. Otherwise only listed fields survive, so nothing added to a
 *  chapter later can leak through a cut by accident; the evidence keeps only the rules and concepts behind the sentences sent (a member also
 *  keeps the verdict ledger and its rules: the reading's footing, not the Đọc sâu prose). */
export function gateChapter(ch: Json, a: Access): Json {
  if (!ch || typeof ch !== "object" || !Array.isArray(ch.paragraphs)) return ch;
  const id = String(ch.chapter ?? ""), deepOpen = a.tier === "member" && a.open.has(id);
  const tabs: Array<[string, Json[]]> = ch.chapters && typeof ch.chapters === "object" && !Array.isArray(ch.chapters)
    ? Object.entries(ch.chapters as Record<string, Json[]>).filter(([, ps]) => Array.isArray(ps)) : [];
  const flat = cutParagraphs(ch.paragraphs, a.tier, deepOpen);
  const tabCuts = tabs.map(([t, ps]) => [t, cutParagraphs(ps, a.tier, deepOpen)] as const);
  const anyDeep = flat.deep > 0 || tabCuts.some(([, c]) => c.deep > 0);
  if (!hidden(flat) && tabCuts.every(([, c]) => !hidden(c))) return deepOpen && anyDeep ? { ...ch, unlocked: true } : ch;

  const out: Json = {};
  for (const k of TOP_KEEP) if (k in ch) out[k] = ch[k];
  if (a.tier === "member") for (const k of MEMBER_KEEP) if (k in ch) out[k] = ch[k];
  // Bát Tự: each tab cut on its own (a guest reads the first third of every tab); the flat reading becomes what the tabs kept
  if (tabs.length) {
    out.chapters = Object.fromEntries(tabCuts.filter(([, c]) => c.kept.length).map(([t, c]) => [t, c.kept]));
    out.locks = Object.fromEntries(tabCuts.filter(([, c]) => hidden(c)).map(([t, c]) => [t, lockInfo(`${id}:${t}`, BAZI_TAB_TITLES[t] ?? t, a, c)]));
  }
  const kept: Json[] = tabs.length ? tabCuts.flatMap(([, c]) => c.kept) : flat.kept;
  out.paragraphs = kept;
  out.text = kept.map(p => p.text ?? "").join("\n\n");
  out.issues = [];
  const used = new Set<string>(), concepts = new Set<string>();
  for (const p of kept) for (const s of p.sentences ?? []) { for (const r of s.trace?.rules ?? []) used.add(r); for (const k of s.trace?.concepts ?? []) concepts.add(k); }
  const ev: Json = ch.evidence ?? {};
  const ledger: Json[] = a.tier === "member" && Array.isArray(ev.ledger) ? ev.ledger : [];
  for (const d of ledger) { if (d?.link?.ruleId) used.add(d.link.ruleId); for (const x of d?.chain ?? []) if (x?.ruleId) used.add(x.ruleId); }
  const pick = (o: Json | undefined, keys: Set<string>) => Object.fromEntries(Object.entries(o ?? {}).filter(([k]) => keys.has(k)));
  out.evidence = { resolved: [], tensions: [], unused: [], limits: Array.isArray(ev.limits) ? ev.limits : [], rules: pick(ev.rules, used), concepts: pick(ev.concepts, concepts),
    divergences: a.tier === "member" && Array.isArray(ev.divergences) ? ev.divergences : [], ...(a.tier === "member" && Array.isArray(ev.ledger) ? { ledger } : {}) };
  // van_han: the decade facts are on the board already; the paragraph index of each decade's start follows the paragraphs kept
  if (Array.isArray(ch.decades)) out.decades = ch.decades;
  if (Array.isArray(ch.starts)) {
    const at = new Map(ch.paragraphs.map((p: Json, i: number) => [p, i]));
    const newIdx = new Map(kept.map((p, j) => [at.get(p), j]));
    out.starts = ch.starts.filter((i: number) => newIdx.has(i)).map((i: number) => newIdx.get(i));
  }
  const whole = tabs.length
    ? tabCuts.reduce((s, [, c]) => ({ kept: [], main: s.main + c.main, mainShown: s.mainShown + c.mainShown, deep: s.deep + c.deep, deepShown: s.deepShown + c.deepShown }), { kept: [], main: 0, mainShown: 0, deep: 0, deepShown: 0 } as Cut)
    : flat;
  out.locked = lockInfo(id, CHAPTER_TITLES[id] ?? String(ch.title ?? id), a, whole);
  return out;
}

/** A whole /api/interpret answer: one chapter, or {chapters: [...]} for chapter "all". */
export function gateOutput(out: Json, a: Access): Json {
  if (Array.isArray(out?.chapters) && !("paragraphs" in out)) return { ...out, chapters: out.chapters.map((c: Json) => gateChapter(c, a)) };
  if (out && typeof out === "object" && "plan" in out && a.tier === "guest") { const { plan: _p, ...rest } = out; return gateChapter(rest, a); }   // mode "reasoned"
  return gateChapter(out, a);
}

/** POST /api/overview ("Tổng quan lá số"): the Mệnh theses are the Mệnh reading told as data, so a guest gets the first third of them; the
 *  frame (the palace's stars) and the charts are chart facts and stay. */
export function gateOverview(out: Json, a: Access): Json {
  if (a.tier !== "guest" || !Array.isArray(out?.theses)) return out;
  const n = out.theses.length, k = guestShown(n);
  if (k >= n) return out;
  return { ...out, theses: out.theses.slice(0, k), locked: { chapter: "overview", title: "Luận điểm chính về Mệnh", tier: "guest", shown: k, total: n, deep: 0, ...(a.shared ? { shared: true } : {}) } };
}

/** POST /api/synthesis (engine flag TVBT_DEEP_INTERPRETATION): a chapter list of paragraphs; a guest gets the first third of each. The
 *  Semantic IR (level 5) is the whole reading as data and never goes to a guest. */
export function gateSynthesis(out: Json, a: Access): Json {
  if (a.tier !== "guest" || !out || typeof out !== "object") return out;
  const { semantic_ir: _ir, ...rest } = out;
  if (!Array.isArray(rest.chapters)) return rest;
  return { ...rest, chapters: rest.chapters.map((c: Json) => {
    const ps: Json[] = Array.isArray(c?.paragraphs) ? c.paragraphs : [], k = guestShown(ps.length);
    if (k >= ps.length) return c;
    return { id: c.id, title: c.title, paragraphs: ps.slice(0, k), locked: { chapter: String(c.id), title: String(c.title ?? c.id), tier: "guest", shown: k, total: ps.length, deep: 0, ...(a.shared ? { shared: true } : {}) } };
  }) };
}

export type Filter = (out: Json, a: Access) => Json;
/** The filter for each gated path. /api/interpretation (the evidence engine: every conclusion of every palace, with its sources) has no
 *  first-third form: a guest is refused it (the report works without it). */
export const FILTERS: Record<string, Filter | "members"> = {
  "/api/interpret": gateOutput, "/api/overview": gateOverview, "/api/synthesis": gateSynthesis, "/api/interpretation": "members",
};

const PRIVATE = "private, no-store";
/** A finished engine response, cut for this reader. Errors pass through untouched; whatever is sent is never stored by a shared cache. */
export async function gateResponse(res: Response, a: Access, filter: Filter | "members" = gateOutput): Promise<Response> {
  if (!res.ok) return res;
  const headers = new Headers(res.headers);
  headers.set("cache-control", PRIVATE);
  headers.delete("content-length");
  headers.set("content-type", "application/json; charset=utf-8");
  if (filter === "members") {
    if (a.tier === "guest") return new Response(JSON.stringify({ detail: "Đăng nhập để xem phần này.", locked: { tier: "guest", ...(a.shared ? { shared: true } : {}) } }), { status: 401, headers });
    return new Response(res.body, { status: res.status, headers });
  }
  const out = await res.json() as Json;
  return new Response(JSON.stringify(filter(out, a)), { status: res.status, headers });
}

/** One gated route (src/index.ts): with the paywall on, a POST to a path in FILTERS runs, then leaves cut to the reader's tier. The cut runs on
 *  the finished response, after the cache, so the cache never holds a per-reader copy. `shared`: the request was built by a share link's
 *  forward, so the reader is a guest whoever is signed in. Only /api/interpret carries Đọc sâu: the chart in its body picks the member's
 *  opened chapters. */
export async function gated(request: Request, o: { db?: D1Database; paywall: boolean; path: string; shared: boolean }, run: (r: Request) => Promise<Response>): Promise<Response> {
  const filter = FILTERS[o.path];
  if (!o.paywall || request.method !== "POST" || !filter) return run(request);
  const body = o.path === "/api/interpret" && !o.shared ? await request.clone().json().catch(() => null) : null;
  const who = o.shared ? Promise.resolve(SHARED) : o.db ? currentUser(o.db, request).then(u => accessFor(o.db, u, body)).catch(() => GUEST) : Promise.resolve(GUEST);
  const [res, access] = await Promise.all([run(request), who]);
  return gateResponse(res, access, filter);
}
