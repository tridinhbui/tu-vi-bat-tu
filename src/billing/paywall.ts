// The reading tiers (config.ts): guests read the first half of each chapter's main reading; members read Tổng quan and Mệnh whole and the
// first half of every other chapter; a package bought for the chart opens its chapters whole, main reading and "Đọc sâu (theo sách)". The
// Worker computes (or reads from cache) the WHOLE reading — the viewer is never part of a cache key — and this file cuts it per request,
// after the cache, BEFORE it leaves the server. The browser is told what was held back and how to get it; it is never trusted to hide
// anything itself. Every filtered response is `private, no-store`.
import { cleanReq } from "../auth/charts.ts";
import { currentUser } from "../auth/session.ts";
import { BAZI_TAB_TITLES, CHAPTER_TITLES, DEEP_CHAPTERS, MEMBER_FREE, PLANS, guestShown, periodOf, planById, planChapters, plansFor, type Tier } from "./config.ts";
import { grantPass } from "./wallet.ts";
import { gateWest, westBody, westFp } from "./west.ts";

export async function unlockedChapters(db: D1Database, userId: string, fp: string): Promise<Set<string>> {
  const { results } = await db.prepare("SELECT chapter FROM unlocks WHERE user_id = ? AND fp = ?").bind(userId, fp).all<{ chapter: string }>();
  return new Set(results.map(r => r.chapter));
}

/** The xu this user already spent on packages for this chart: what a bigger package is discounted by. */
export async function spentOn(db: D1Database, userId: string, fp: string): Promise<number> {
  const pre = `unlock:${fp}:`;
  const r = await db.prepare("SELECT COALESCE(SUM(-delta), 0) AS n FROM ledger WHERE user_id = ? AND kind = 'coin_spend' AND substr(ref, 1, ?) = ?").bind(userId, pre.length, pre).first<{ n: number }>();
  return Math.max(0, r?.n ?? 0);
}

export type UnlockResult =
  | { ok: true; charged: number; chapters: string[]; already: boolean }
  | { ok: false; reason: "bad_plan" | "insufficient"; need?: number };

/** Opens a plan's chapters for one chart. One D1 batch (a transaction): the ledger row is written only when the wallet holds enough, the
 *  wallet is charged only when that row was written, and the chapters are opened only when the charge applied. The ledger ref is the
 *  same for the same purchase, so a double click charges once. A plan whose chapters are all open already charges nothing; otherwise it
 *  costs its price less what was spent on packages for this chart before (an upgrade pays the difference). Cao cấp also opens the chat
 *  pass, once per purchase (wallet.ts grantPass). `_chapter` is accepted for old clients and ignored. */
export async function buyPlan(db: D1Database, userId: string, fp: string, planId: unknown, _chapter?: unknown, now = Date.now()): Promise<UnlockResult> {
  const plan = planById(planId);
  if (!plan || !fp) return { ok: false, reason: "bad_plan" };
  const chapters = planChapters(plan);
  const have = await unlockedChapters(db, userId, fp), missing = chapters.filter(c => !have.has(c) && !have.has(c.split(":")[0]));   // a tab is open with its chapter
  if (!missing.length) return { ok: true, charged: 0, chapters, already: true };
  await db.prepare("INSERT OR IGNORE INTO wallets (user_id) VALUES (?)").bind(userId).run();
  const base = `unlock:${fp}:${plan.id}`;
  // a purchase bought before and later taken back (rows removed by an admin) can be bought again under a new ref
  const prior = (await db.prepare("SELECT COUNT(*) AS n FROM ledger WHERE user_id = ? AND (ref = ? OR ref LIKE ?)").bind(userId, base, `${base}#%`).first<{ n: number }>())?.n ?? 0;
  const ref = prior ? `${base}#${prior + 1}` : base, cost = Math.max(0, plan.coins - await spentOn(db, userId, fp));
  const [led, upd] = await db.batch([
    db.prepare("INSERT OR IGNORE INTO ledger (user_id, kind, usage, delta, period, ref, created_at) SELECT ?1, 'coin_spend', ?2, ?3, ?4, ?5, ?6 " +
      "WHERE (SELECT coins FROM wallets WHERE user_id = ?1) >= ?7").bind(userId, `unlock:${plan.id}`, -cost, periodOf(now), ref, now, cost),
    db.prepare("UPDATE wallets SET coins = coins - ?1, updated_at = ?2 WHERE user_id = ?3 AND coins >= ?1 AND changes() > 0").bind(cost, now, userId),
    db.prepare("INSERT OR IGNORE INTO unlocks (user_id, fp, chapter, plan, ledger_ref, created_at) SELECT ?1, ?2, value, ?3, ?4, ?5 FROM json_each(?6) WHERE changes() > 0")
      .bind(userId, fp, plan.id, ref, now, JSON.stringify(missing)),
  ]);
  if ((led.meta?.changes ?? 0) > 0 && (upd.meta?.changes ?? 0) > 0) {
    if (plan.pass) await grantPass(db, userId, ref, now);
    return { ok: true, charged: cost, chapters, already: false };
  }
  // the same purchase landed a moment ago (double click): nothing more was charged
  if (await db.prepare("SELECT 1 AS x FROM ledger WHERE user_id = ? AND ref = ?").bind(userId, ref).first()) return { ok: true, charged: 0, chapters, already: true };
  return { ok: false, reason: "insufficient", need: cost };
}

// ---------- who is reading ----------
/** `open`: what this member opened for the chart in the request (chapters, Bát Tự tabs, "ai"). `credit`: xu already spent on packages for
 *  it (the lock card prices an upgrade with it). `shared`: the reader came through a share link. */
export interface Access { tier: Tier; open: Set<string>; credit?: number; shared?: boolean; paid?: boolean }
export const GUEST: Access = Object.freeze({ tier: "guest", open: new Set<string>() }) as Access;
/** A share link's viewer reads at the guest tier, whoever they are: the link opens someone else's chart. */
export const SHARED: Access = Object.freeze({ tier: "guest", open: new Set<string>(), shared: true }) as Access;

/** The tier for one request. Signed out: guest. Signed in: member, with what was opened for the chart in the body (a body that is not a
 *  birth record, or a failing lookup, opens nothing: fail closed). */
export async function accessFor(db: D1Database | undefined, user: { id: string } | null, body: unknown, fpOf: (b: unknown) => string | null = b => cleanReq(b)?.fp ?? null): Promise<Access> {
  if (!user) return GUEST;
  const fp = fpOf(body);
  if (!fp || !db) return { tier: "member", open: new Set<string>(), credit: 0 };
  const [open, credit] = await Promise.all([unlockedChapters(db, user.id, fp).catch(() => new Set<string>()), spentOn(db, user.id, fp).catch(() => 0)]);
  return { tier: "member", open, credit };
}

/** The main reading of a chapter (or of one of its Bát Tự tabs) comes whole: a member on a free chapter, or one the chart's package opened. */
const mainWhole = (a: Access, id: string, tab?: string) => a.tier === "member" && (MEMBER_FREE.includes(id) || a.open.has(id) || (!!tab && a.open.has(`${id}:${tab}`)));
/** The Đọc sâu part comes too: only what a package opened. */
const deepOpen = (a: Access, id: string, tab?: string) => a.tier === "member" && (a.open.has(id) || (!!tab && a.open.has(`${id}:${tab}`)));
/** Every chapter of the chart is open (Trọn bộ, Cao cấp): the whole-report layers (synthesis, evidence engine) are this reader's too. */
export const fullAccess = (a: Access) => a.tier === "member" && DEEP_CHAPTERS.every(c => a.open.has(c));

// ---------- the filter ----------
type Json = Record<string, any>;
/** A paragraph of the Đọc sâu part: Tử Vi luận cung `deep`, Bát Tự depth 'sau'. */
export const isDeep = (p: Json) => p?.deep === true || p?.depth === "sau";

interface Cut { kept: Json[]; main: number; mainShown: number; deep: number; deepShown: number }
/** The paragraphs this reader gets of one run, in their order: the first half of the main ones unless `whole`; the Đọc sâu ones only
 *  when `deep`. */
function cutParagraphs(ps: Json[], whole: boolean, deep: boolean): Cut {
  const main = ps.filter(p => !isDeep(p)), sau = ps.filter(isDeep);
  const keepMain = new Set(whole ? main : main.slice(0, guestShown(main.length)));
  const kept = ps.filter(p => keepMain.has(p) || (deep && isDeep(p)));
  return { kept, main: main.length, mainShown: keepMain.size, deep: sau.length, deepShown: deep ? sau.length : 0 };
}
/** The packages offered on a lock: those that open the chapter, or for a chapter no package names (a synthesis section), those that open all. */
const offerFor = (chapter: string) => { const named = plansFor(chapter); return named.length ? named : PLANS.filter(p => p.chapters === DEEP_CHAPTERS); };
const hidden = (c: Cut) => c.main - c.mainShown + c.deep - c.deepShown;

/** What the lock card shows: a guest is asked to sign in (or, on a share link, told why the reading is short); a member is offered the
 *  packages that open the chapter, each with its price for this reader (`price`: less what was spent on this chart already). Counts only:
 *  no word of the held-back text. */
function lockInfo(chapter: string, title: string, a: Access, c: Cut): Json {
  const base = { chapter, title, tier: a.tier, shown: c.mainShown, total: c.main, deep: c.deep - c.deepShown };
  if (a.tier === "guest") return { ...base, ...(a.shared ? { shared: true } : {}) };
  const credit = a.credit ?? 0;
  return { ...base, plans: offerFor(chapter).map(p => ({ id: p.id, name: p.name, coins: p.coins, price: Math.max(0, p.coins - credit) })) };
}

const TOP_KEEP = ["engine", "kbVersion", "chapter", "palace", "title", "schema", "order", "draft", "pass", "luan", "card"];
const MEMBER_KEEP = ["theses", "advice"];

/** One served chapter for this reader. Nothing held back: the chapter as it was. Otherwise only listed fields survive, so nothing added to a
 *  chapter later can leak through a cut by accident; the evidence keeps only the rules and concepts behind the sentences sent. The advice,
 *  theses and verdict ledger restate the whole main reading, so they go only with a whole main reading. */
export function gateChapter(ch: Json, a: Access): Json {
  if (!ch || typeof ch !== "object" || !Array.isArray(ch.paragraphs)) return ch;
  const id = String(ch.chapter ?? "");
  const tabs: Array<[string, Json[]]> = ch.chapters && typeof ch.chapters === "object" && !Array.isArray(ch.chapters)
    ? Object.entries(ch.chapters as Record<string, Json[]>).filter(([, ps]) => Array.isArray(ps)) : [];
  const flat = cutParagraphs(ch.paragraphs, mainWhole(a, id), deepOpen(a, id));
  const tabCuts = tabs.map(([t, ps]) => [t, cutParagraphs(ps, mainWhole(a, id, t), deepOpen(a, id, t))] as const);
  const bought = deepOpen(a, id) || tabs.some(([t]) => deepOpen(a, id, t));
  if (!hidden(flat) && tabCuts.every(([, c]) => !hidden(c))) return bought ? { ...ch, unlocked: true } : ch;

  const whole = tabs.length ? tabCuts.every(([, c]) => c.mainShown === c.main) : flat.mainShown === flat.main;
  const footing = a.tier === "member" && whole;
  const out: Json = {};
  for (const k of TOP_KEEP) if (k in ch) out[k] = ch[k];
  if (footing) for (const k of MEMBER_KEEP) if (k in ch) out[k] = ch[k];
  // Bát Tự: each tab cut on its own (a guest reads the first half of every tab); the flat reading becomes what the tabs kept
  if (tabs.length) {
    out.chapters = Object.fromEntries(tabCuts.filter(([, c]) => c.kept.length).map(([t, c]) => [t, c.kept]));
    out.locks = Object.fromEntries(tabCuts.filter(([, c]) => hidden(c)).map(([t, c]) => [t, lockInfo(`${id}:${t}`, BAZI_TAB_TITLES[t] ?? t, a, c)]));
    const open = tabCuts.filter(([t]) => deepOpen(a, id, t)).map(([t]) => t);
    if (open.length) out.unlockedTabs = open;
  }
  const kept: Json[] = tabs.length ? tabCuts.flatMap(([, c]) => c.kept) : flat.kept;
  out.paragraphs = kept;
  out.text = kept.map(p => p.text ?? "").join("\n\n");
  out.issues = [];
  const used = new Set<string>(), concepts = new Set<string>();
  for (const p of kept) for (const s of p.sentences ?? []) { for (const r of s.trace?.rules ?? []) used.add(r); for (const k of s.trace?.concepts ?? []) concepts.add(k); }
  const ev: Json = ch.evidence ?? {};
  const ledger: Json[] = footing && Array.isArray(ev.ledger) ? ev.ledger : [];
  for (const d of ledger) { if (d?.link?.ruleId) used.add(d.link.ruleId); for (const x of d?.chain ?? []) if (x?.ruleId) used.add(x.ruleId); }
  const pick = (o: Json | undefined, keys: Set<string>) => Object.fromEntries(Object.entries(o ?? {}).filter(([k]) => keys.has(k)));
  out.evidence = { resolved: [], tensions: [], unused: [], limits: Array.isArray(ev.limits) ? ev.limits : [], rules: pick(ev.rules, used), concepts: pick(ev.concepts, concepts),
    divergences: footing && Array.isArray(ev.divergences) ? ev.divergences : [], ...(footing && Array.isArray(ev.ledger) ? { ledger } : {}) };
  // van_han: the decade facts are on the board already; the paragraph index of each decade's start follows the paragraphs kept
  if (Array.isArray(ch.decades)) out.decades = ch.decades;
  if (Array.isArray(ch.starts)) {
    const at = new Map(ch.paragraphs.map((p: Json, i: number) => [p, i]));
    const newIdx = new Map(kept.map((p, j) => [at.get(p), j]));
    out.starts = ch.starts.filter((i: number) => newIdx.has(i)).map((i: number) => newIdx.get(i));
  }
  const sum = tabs.length
    ? tabCuts.reduce((s, [, c]) => ({ kept: [], main: s.main + c.main, mainShown: s.mainShown + c.mainShown, deep: s.deep + c.deep, deepShown: s.deepShown + c.deepShown }), { kept: [], main: 0, mainShown: 0, deep: 0, deepShown: 0 } as Cut)
    : flat;
  out.locked = lockInfo(id, CHAPTER_TITLES[id] ?? String(ch.title ?? id), a, sum);
  if (bought) out.unlocked = true;
  return out;
}

/** A whole /api/interpret answer: one chapter, or {chapters: [...]} for chapter "all". */
export function gateOutput(out: Json, a: Access): Json {
  if (Array.isArray(out?.chapters) && !("paragraphs" in out)) return { ...out, chapters: out.chapters.map((c: Json) => gateChapter(c, a)) };
  if (out && typeof out === "object" && "plan" in out && a.tier === "guest") { const { plan: _p, ...rest } = out; return gateChapter(rest, a); }   // mode "reasoned"
  return gateChapter(out, a);
}

/** POST /api/overview ("Tổng quan lá số"): the Mệnh theses are the Mệnh reading told as data, so a guest gets the first half of them; the
 *  frame (the palace's stars) and the charts are chart facts and stay. */
export function gateOverview(out: Json, a: Access): Json {
  if (a.tier !== "guest" || !Array.isArray(out?.theses)) return out;
  const n = out.theses.length, k = guestShown(n);
  if (k >= n) return out;
  return { ...out, theses: out.theses.slice(0, k), locked: { chapter: "overview", title: "Luận điểm chính về Mệnh", tier: "guest", shown: k, total: n, deep: 0, ...(a.shared ? { shared: true } : {}) } };
}

/** POST /api/synthesis (engine flag TVBT_DEEP_INTERPRETATION): a chapter list of paragraphs, each cut like a report chapter: whole for a
 *  member on a free or opened chapter (or with every chapter open), else the first half. The Semantic IR (level 5) is the whole reading as
 *  data and goes only to a reader with every chapter open. */
export function gateSynthesis(out: Json, a: Access): Json {
  if (!out || typeof out !== "object" || fullAccess(a)) return out;
  const { semantic_ir: _ir, ...rest } = out;
  if (!Array.isArray(rest.chapters)) return rest;
  return { ...rest, chapters: rest.chapters.map((c: Json) => {
    const ps: Json[] = Array.isArray(c?.paragraphs) ? c.paragraphs : [], k = guestShown(ps.length), id = String(c?.id ?? "");
    if (k >= ps.length || mainWhole(a, id)) return c;
    const base = { chapter: id, title: String(c.title ?? c.id), tier: a.tier, shown: k, total: ps.length, deep: 0 };
    return { id: c.id, title: c.title, paragraphs: ps.slice(0, k), locked: a.tier === "guest" ? { ...base, ...(a.shared ? { shared: true } : {}) } : { ...base, plans: offerFor(id).map(p => ({ id: p.id, name: p.name, coins: p.coins, price: Math.max(0, p.coins - (a.credit ?? 0)) })) } };
  }) };
}

/** A Kinh Dịch / Mai Hoa cast has no chart to buy a package for: its Đọc sâu goes to any member who holds a paid package for some chart
 *  (owner decision 2026-10-25). Everyone else gets the main reading whole and is told what the Đọc sâu holds. */
export async function holdsPackage(db: D1Database, userId: string): Promise<boolean> {
  return !!(await db.prepare("SELECT 1 AS x FROM unlocks WHERE user_id = ? LIMIT 1").bind(userId).first().catch(() => null));
}
export const CAST_PATHS = new Set(["/api/kinh-dich/reading", "/api/mai-hoa/reading"]);
export function gateCast(out: Json, a: Access): Json {
  const r = out?.reading;
  if (!r || !Array.isArray(r.sections) || a.paid) return out;
  let hidden = 0;
  const sections = r.sections.map((sec: Json) => {
    const ps: Json[] = Array.isArray(sec?.paragraphs) ? sec.paragraphs : [];
    const kept = ps.filter(p => !isDeep(p));
    hidden += ps.length - kept.length;
    return { ...sec, paragraphs: kept };
  }).filter((sec: Json) => sec.paragraphs.length);
  if (!hidden) return out;
  return { ...out, reading: { ...r, sections, locked: { tier: a.tier, deep: hidden, need: a.tier === "guest" ? "sign_in" : "package" } } };
}

export type Filter = (out: Json, a: Access) => Json;
/** The filter for each gated path. /api/interpretation (the evidence engine: every conclusion of every palace, with its sources) has no
 *  first-half form: it goes to a reader with every chapter of the chart open, a guest is asked to sign in, a member to open the chart
 *  (the report works without it). */
export const FILTERS: Record<string, Filter | "full"> = {
  "/api/interpret": gateOutput, "/api/overview": gateOverview, "/api/synthesis": gateSynthesis, "/api/interpretation": "full",
  "/api/kinh-dich/reading": gateCast, "/api/mai-hoa/reading": gateCast,
  "/api/west/reading": gateWest,
};
/** The fingerprint that picks what was opened for the chart of a request: the Western one for /api/west/*, the Tử Vi one otherwise. */
const fpFor = (path: string) => path.startsWith("/api/west/") ? (b: unknown) => westFp(westBody(b)) : undefined;

const PRIVATE = "private, no-store";
/** A finished engine response, cut for this reader. Errors pass through untouched; whatever is sent is never stored by a shared cache. */
export async function gateResponse(res: Response, a: Access, filter: Filter | "full" = gateOutput): Promise<Response> {
  if (!res.ok) return res;
  const headers = new Headers(res.headers);
  headers.set("cache-control", PRIVATE);
  headers.delete("content-length");
  headers.set("content-type", "application/json; charset=utf-8");
  if (filter === "full") {
    if (a.tier === "guest") return new Response(JSON.stringify({ detail: "Đăng nhập để xem phần này.", locked: { tier: "guest", ...(a.shared ? { shared: true } : {}) } }), { status: 401, headers });
    if (!fullAccess(a)) return new Response(JSON.stringify({ detail: "Phần này đi cùng gói Trọn bộ hoặc Cao cấp của lá số.", locked: { tier: "member" } }), { status: 402, headers });
    return new Response(res.body, { status: res.status, headers });
  }
  const out = await res.json() as Json;
  return new Response(JSON.stringify(filter(out, a)), { status: res.status, headers });
}

/** One gated route (src/index.ts): with the paywall on, a POST to a path in FILTERS runs, then leaves cut to the reader's tier. The cut runs on
 *  the finished response, after the cache, so the cache never holds a per-reader copy. `shared`: the request was built by a share link's
 *  forward, so the reader is a guest whoever is signed in. The chart in the body picks what the member opened for it. */
export async function gated(request: Request, o: { db?: D1Database; paywall: boolean; path: string; shared: boolean }, run: (r: Request) => Promise<Response>): Promise<Response> {
  const filter = FILTERS[o.path];
  if (!o.paywall || request.method !== "POST" || !filter) return run(request);
  const body = !o.shared ? await request.clone().json().catch(() => null) : null;
  const db = o.db;
  const who = o.shared ? Promise.resolve(SHARED)
    : !db ? Promise.resolve(GUEST)
    : CAST_PATHS.has(o.path) ? currentUser(db, request).then(async u => u ? { tier: "member" as Tier, open: new Set<string>(), paid: await holdsPackage(db, u.id) } : GUEST).catch(() => GUEST)
    : currentUser(db, request).then(u => accessFor(db, u, body, fpFor(o.path))).catch(() => GUEST);
  const [res, access] = await Promise.all([run(request), who]);
  return gateResponse(res, access, filter);
}
