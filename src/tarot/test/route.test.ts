// The Tarot API against a real local D1 (wrangler's platform proxy, persist off; nothing remote is touched): the switch, the daily
// allowance, the two-step draw that never sends the deck order or the seed, the question kept only when saved, and share links.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { getPlatformProxy } from "wrangler";
import { handleTarot, isTarotPath, SCHEMA, DAILY_FREE, vnDay, type TarotDeps } from "../route.ts";
import { TAROT_HEADER } from "../guard.ts";
import { PENDING_TEXT } from "../reading.ts";
import type { User } from "../../auth/session.ts";

let proxy: Awaited<ReturnType<typeof getPlatformProxy>>, db: D1Database;
const BASE = "https://example.test";
const alice: User = { id: "ua", email: "ua@x.vn", name: "A", picture: "" };
const bob: User = { id: "ub", email: "ub@x.vn", name: "B", picture: "" };
let clock = Date.UTC(2026, 9, 25, 3, 0, 0);

before(async () => {
  proxy = await getPlatformProxy({ configPath: "wrangler.jsonc", persist: false });
  db = (proxy.env as any).DB as D1Database;
  for (const f of readdirSync("migrations/app").sort()) {
    const sql = readFileSync(`migrations/app/${f}`, "utf8").replace(/--.*$/gm, "");
    for (const stmt of sql.split(";").map(s => s.trim()).filter(Boolean)) await db.prepare(stmt).run();
  }
  for (const u of [alice, bob]) await db.prepare("INSERT INTO users (id, google_sub, email, name, created_at) VALUES (?, ?, ?, ?, 1)").bind(u.id, "s" + u.id, u.email, u.name).run();
});
after(async () => { await proxy.dispose(); });

const call = (path: string, init: RequestInit & { user?: User | null; ip?: string; enabled?: boolean } = {}) => {
  const h: Record<string, string> = { "content-type": "application/json", "cf-connecting-ip": init.ip ?? "203.0.113.1", ...(init.headers as Record<string, string>) };
  if (init.method && init.method !== "GET" && !("x-tvbt" in h)) h["x-tvbt"] = "1";
  const deps: TarotDeps = { db, enabled: init.enabled ?? true, user: init.user ?? null, now: () => clock };
  return handleTarot(new Request(BASE + path, { ...init, headers: h }), deps);
};
const j = async (r: Response | Promise<Response>) => { const x = await r; return { status: x.status, body: await x.json() as any }; };
const post = (path: string, body: unknown, o: { user?: User | null; ip?: string } = {}) => j(call(path, { method: "POST", body: JSON.stringify(body), ...o }));

test("the migration and the route's own schema are the same statements", () => {
  const norm = (s: string) => s.replace(/\s+/g, " ").replace(/\( /g, "(").replace(/ \)/g, ")").trim();
  const sql = readFileSync("migrations/app/0011_tarot.sql", "utf8").replace(/--.*$/gm, "").split(";").map(norm).filter(Boolean);
  assert.deepEqual(sql, SCHEMA.map(norm));
});

test("with TVBT_TAROT off every Tarot path answers 404, and the paths are recognised", async () => {
  for (const [p, m] of [["/api/tarot/draw", "POST"], ["/api/tarot/x/" + "A".repeat(22), "GET"], ["/api/me/tarot", "GET"], ["/api/me/tarot", "POST"], ["/api/me/tarot?id=x", "DELETE"]] as const) {
    const r = await call(p, { method: m, enabled: false, user: alice, body: m === "GET" ? undefined : "{}" });
    assert.equal(r.status, 404, `${m} ${p}`);
  }
  assert.ok(isTarotPath("/api/tarot/draw") && isTarotPath("/api/me/tarot") && !isTarotPath("/api/me/profile"));
  assert.equal((await call("/api/tarot/draw", { method: "POST", body: "{}", headers: { "x-tvbt": "" } })).status, 403);
  assert.equal((await handleTarot(new Request(BASE + "/api/tarot/draw", { method: "POST" }), { enabled: true, user: null })).status, 503);
});

test("a draw: the shuffle answers with an id and the fan size only; the reveal gives the picked cards, once", async () => {
  const s = await post("/api/tarot/draw", { spread: 3, reversals: true }, { ip: "198.51.100.7" });
  assert.equal(s.status, 200);
  assert.match(s.body.id, /^[A-Za-z0-9_-]{22}$/);
  assert.equal(s.body.fan, 78); assert.equal(s.body.pick, 3); assert.equal(s.body.header, TAROT_HEADER);
  assert.equal(s.body.remaining, DAILY_FREE - 1);
  const seed = (await db.prepare("SELECT seed FROM tarot_draws WHERE id = ?").bind(s.body.id).first<{ seed: string }>())!.seed;
  assert.ok(!JSON.stringify(s.body).includes(seed));
  assert.equal((await post("/api/tarot/draw", { id: s.body.id, picks: [1, 2] })).status, 400);
  assert.equal((await post("/api/tarot/draw", { id: s.body.id, picks: [1, 1, 2] })).status, 400);
  const r = await post("/api/tarot/draw", { id: s.body.id, picks: [10, 3, 77], question: "Tôi nên nhìn công việc hiện tại thế nào?" });
  assert.equal(r.status, 200);
  assert.deepEqual(r.body.cards.map((c: any) => c.pick), [10, 3, 77]);
  assert.deepEqual(r.body.cards.map((c: any) => c.slot), [1, 2, 3]);
  // every card carries Waite's readings with their page (Two of Cups reversed: Waite gives none, said so)
  assert.ok(r.body.cards.every((c: any) => c.card.name_vi && c.card.name_en && (c.reading.status === "sourced"
    ? c.reading.items.length > 0 && c.reading.items.every((i: any) => /^PKT \(1916\) tr\. \d+$/.test(i.cite) && i.quote_en && i.text_vi)
    : c.reading.status === "no_reversed" && c.card.id === "C02" && c.reversed)), JSON.stringify(r.body.cards.map((c: any) => c.reading.status)));
  assert.ok(!JSON.stringify(r.body).includes(PENDING_TEXT));
  assert.equal(r.body.notices.length, 0);
  assert.match(r.body.layout_note, /không mang nghĩa riêng/);
  assert.ok(!JSON.stringify(r.body).includes(seed));
  // the question is read and dropped
  const row = await db.prepare("SELECT question, picks_json, saved FROM tarot_draws WHERE id = ?").bind(s.body.id).first<any>();
  assert.equal(row.question, null); assert.equal(row.saved, 0); assert.equal(row.picks_json, "[10,3,77]");
  // asked again (other picks), the same cards: no second look
  const again = await post("/api/tarot/draw", { id: s.body.id, picks: [0, 1, 2] });
  assert.deepEqual(again.body.cards, r.body.cards);
  // unknown or malformed ids
  assert.equal((await post("/api/tarot/draw", { id: "B".repeat(22), picks: [0] })).status, 404);
  assert.equal((await post("/api/tarot/draw", { id: "../x", picks: [0] })).status, 404);
  assert.equal((await post("/api/tarot/draw", { spread: 5 })).status, 400);
});

test("reversals off: every card upright; a sensitive question gets its notice", async () => {
  const s = await post("/api/tarot/draw", { spread: 3, reversals: false }, { ip: "198.51.100.8" });
  const r = await post("/api/tarot/draw", { id: s.body.id, picks: [0, 1, 2], question: "toi co nen dau tu co phieu khong, va benh vien nao tot" });
  assert.ok(r.body.cards.every((c: any) => c.reversed === false));
  assert.equal(r.body.reversals, false);
  assert.deepEqual(r.body.notices.map((n: any) => n.topic), ["health", "investment"]);
});

test("a shuffle left unrevealed for over an hour expires", async () => {
  const s = await post("/api/tarot/draw", { spread: 1 }, { ip: "198.51.100.9" });
  clock += 3601_000;
  assert.equal((await post("/api/tarot/draw", { id: s.body.id, picks: [5] })).status, 410);
});

test("free allowance: 3 shuffles a day per address for guests, per account when signed in; a new Vietnam day resets it", async () => {
  const ip = "192.0.2.50";
  for (let i = DAILY_FREE - 1; i >= 0; i--) assert.equal((await post("/api/tarot/draw", { spread: 1 }, { ip })).body.remaining, i);
  const over = await post("/api/tarot/draw", { spread: 1 }, { ip });
  assert.equal(over.status, 429); assert.match(over.body.detail, /3 lượt miễn phí/);
  assert.equal((await post("/api/tarot/draw", { spread: 1 }, { ip: "192.0.2.51" })).status, 200);          // another address
  for (let i = 0; i < DAILY_FREE; i++) assert.equal((await post("/api/tarot/draw", { spread: 1 }, { ip, user: bob })).status, 200);   // the account's own count
  assert.equal((await post("/api/tarot/draw", { spread: 1 }, { ip: "192.0.2.99", user: bob })).status, 429);   // a new address does not reset an account
  const day = vnDay(clock);
  clock += 86400_000;
  assert.notEqual(vnDay(clock), day);
  assert.equal((await post("/api/tarot/draw", { spread: 1 }, { ip })).status, 200);
  assert.equal(vnDay(Date.UTC(2026, 9, 24, 17, 30)), "2026-10-25");                                      // 00:30 in Hà Nội
});

test("saving: sign-in needed; the question only if sent; share links hide it unless the owner shows it; owner-only delete", async () => {
  const s = await post("/api/tarot/draw", { spread: 1 }, { ip: "203.0.113.20" });
  assert.equal((await post("/api/me/tarot", { id: s.body.id })).status, 401);
  assert.equal((await post("/api/me/tarot", { id: s.body.id }, { user: alice })).status, 409);           // not revealed yet
  await post("/api/tarot/draw", { id: s.body.id, picks: [42], question: "Điều gì đang chờ tôi?" });
  assert.equal((await j(call("/api/tarot/x/" + s.body.id))).status, 404);                                // not saved: no link
  const saved = await post("/api/me/tarot", { id: s.body.id }, { user: alice });
  assert.equal(saved.status, 200); assert.equal(saved.body.question, null); assert.equal(saved.body.share_path, `/tarot/?x=${s.body.id}`);
  let row = await db.prepare("SELECT question, user_id, saved FROM tarot_draws WHERE id = ?").bind(s.body.id).first<any>();
  assert.deepEqual(row, { question: null, user_id: "ua", saved: 1 });
  assert.equal((await post("/api/me/tarot", { id: s.body.id }, { user: bob })).status, 404);             // Alice's draw
  // with the question, hidden on the link by default
  await post("/api/me/tarot", { id: s.body.id, question: "Điều gì đang chờ tôi?" }, { user: alice });
  let shared = await j(call("/api/tarot/x/" + s.body.id));
  assert.equal(shared.status, 200); assert.equal(shared.body.question, null); assert.equal(shared.body.question_hidden, true);
  assert.ok(!JSON.stringify(shared.body).includes("chờ tôi"));
  assert.equal(shared.body.cards[0].pick, 42); assert.equal(shared.body.header, TAROT_HEADER);
  await post("/api/me/tarot", { id: s.body.id, question: "Điều gì đang chờ tôi?", show_question: true }, { user: alice });
  shared = await j(call("/api/tarot/x/" + s.body.id));
  assert.equal(shared.body.question, "Điều gì đang chờ tôi?");
  const mine = await j(call("/api/me/tarot", { user: alice }));
  assert.equal(mine.body.draws.length, 1); assert.equal(mine.body.draws[0].question, "Điều gì đang chờ tôi?");
  assert.equal((await j(call("/api/me/tarot", { user: bob }))).body.draws.length, 0);
  assert.equal((await call("/api/me/tarot?id=" + s.body.id, { method: "DELETE", user: bob })).status, 404);
  assert.equal((await call("/api/me/tarot?id=" + s.body.id, { method: "DELETE", user: alice })).status, 200);
  assert.equal((await j(call("/api/tarot/x/" + s.body.id))).status, 404);
  row = await db.prepare("SELECT COUNT(*) AS n FROM tarot_draws WHERE id = ?").bind(s.body.id).first<any>();
  assert.equal(row.n, 0);
});

test("unsaved draws older than two days are removed when a new shuffle is made", async () => {
  const s = await post("/api/tarot/draw", { spread: 1 }, { ip: "203.0.113.30" });
  clock += 3 * 86400_000;
  await post("/api/tarot/draw", { spread: 1 }, { ip: "203.0.113.31" });
  assert.equal((await db.prepare("SELECT COUNT(*) AS n FROM tarot_draws WHERE id = ?").bind(s.body.id).first<any>()).n, 0);
});
