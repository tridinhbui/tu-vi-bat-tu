// The chat route with a fake model and the stored fixture chart: modes (chart on screen, saved chart, general), sign-in, charging, the
// daily allowance and the top-up pass, locking, refunds and the stream shape.
import { test, before, after, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { getPlatformProxy } from "wrangler";
import knowledge from "../../interpret/generated/knowledge.json" with { type: "json" };
import { handleChat, cleanMessages, type ChatDeps } from "../route.ts";
import { buildContext } from "../context.ts";
import { getWallet, grant, grantPass } from "../../billing/wallet.ts";
import { FREE_MESSAGES_PER_DAY, TOPUP_CHAT } from "../../billing/config.ts";
import type { Llm, LlmEvent } from "../llm.ts";

const chart = JSON.parse(readFileSync("src/interpret/test/fixtures/charts.json", "utf8"))[0];
let proxy: Awaited<ReturnType<typeof getPlatformProxy>>, db: D1Database, n = 0, uid = "";
before(async () => {
  proxy = await getPlatformProxy({ configPath: "wrangler.jsonc", persist: false });
  db = (proxy.env as any).DB as D1Database;
  for (const f of readdirSync("migrations/app").sort()) {
    const sql = readFileSync(`migrations/app/${f}`, "utf8").replace(/--.*$/gm, "");
    for (const stmt of sql.split(";").map(s => s.trim()).filter(Boolean)) await db.prepare(stmt).run();
  }
});
after(async () => { await proxy.dispose(); });
beforeEach(async () => {
  uid = `c${++n}`;
  await db.prepare("INSERT INTO users (id, google_sub, email, created_at) VALUES (?, ?, ?, 1)").bind(uid, `s${n}`, `c${n}@x.test`).run();
});

const birth = { year: 1990, month: 5, day: 17, hour: 10, minute: 30, gender: "male", evil: "dropped" };
const post = (body: unknown, headers: Record<string, string> = { "x-tvbt": "1" }) =>
  new Request("https://x.test/api/me/chat", { method: "POST", headers, body: JSON.stringify(body) });
const ask = (text = "Mệnh của tôi nói gì về công việc?") => ({ birth, messages: [{ role: "user", content: text }] });
const llmOf = (events: LlmEvent[], then?: Error): Llm => async function* () { for (const e of events) yield e; if (then) throw then; };

interface Spy { llmCalls: number; factsCalls: number; sent?: any; deps: ChatDeps }
function make(llm: Llm | null, factsOk = true): Spy {
  const spy: Spy = { llmCalls: 0, factsCalls: 0, deps: null as any };
  spy.deps = {
    db, user: { id: uid, email: "", name: "", picture: "" }, knowledge: knowledge as any,
    llm: llm && (async function* (req) { spy.llmCalls++; spy.sent = req; yield* llm(req); }),
    facts: async b => { spy.factsCalls++; return factsOk ? new Response(JSON.stringify(chart.facts)) : new Response("x", { status: 500 }); },
  };
  return spy;
}
async function events(res: Response): Promise<any[]> {
  const text = await res.text();
  return text.split("\n\n").filter(l => l.startsWith("data: ")).map(l => JSON.parse(l.slice(6)));
}
const free = async () => (await getWallet(db, uid)).free.used;

test("the context carries the facts and every chapter's reading", () => {
  const ctx = buildContext(chart.facts, knowledge as any);
  console.log(`      context: ${ctx.length} chars`);
  for (const must of ["DỮ KIỆN LÁ SỐ", "Hỏa lục cục", "MƯỜI HAI CUNG", "TỨ tứ HÓA".replace("tứ ", ""), "BÁT TỰ", "BÀI LUẬN GIẢI"]) assert.ok(ctx.includes(must), must);
  assert.ok(ctx.length > 5000, "has the readings, not just the facts");
});

test("messages are validated", () => {
  assert.equal(cleanMessages([]), null);
  assert.equal(cleanMessages([{ role: "assistant", content: "hi" }]), null);                       // must start with the user
  assert.equal(cleanMessages([{ role: "user", content: "a" }, { role: "assistant", content: "b" }]), null); // must end with the user
  assert.equal(cleanMessages([{ role: "user", content: "x".repeat(1501) }]), null);
  assert.equal(cleanMessages([{ role: "system", content: "x" }]), null);
  assert.equal(cleanMessages(Array.from({ length: 21 }, (_, i) => ({ role: i % 2 ? "assistant" : "user", content: "x" }))), null);
  assert.equal(cleanMessages([{ role: "user", content: " hi " }])![0].content, "hi");
});

test("rejects bad requests without charging or calling the model", async () => {
  const s = make(llmOf([{ text: "x" }]));
  assert.equal((await handleChat(post(ask(), {}), s.deps)).status, 403);
  assert.equal((await handleChat(new Request("https://x.test/api/me/chat"), s.deps)).status, 405);
  assert.equal((await handleChat(post({ birth: { year: 1 }, messages: [] }), s.deps)).status, 400);
  assert.equal((await handleChat(post(ask()), make(null).deps)).status, 503);
  assert.equal(s.llmCalls + s.factsCalls, 0); assert.equal(await free(), 0);
});

test("a normal answer streams, charges one free chat, and sends the context to the model", async () => {
  const s = make(llmOf([{ text: "Mệnh " }, { text: "có Vũ Khúc." }, { stop: "end_turn" }]));
  const res = await handleChat(post(ask()), s.deps);
  assert.equal(res.status, 200); assert.match(res.headers.get("content-type")!, /text\/event-stream/);
  const ev = await events(res);
  assert.deepEqual(ev.map(e => e.type), ["meta", "delta", "delta", "done", "wallet"]);
  assert.equal(ev[0].source, "free");
  assert.equal(ev.filter(e => e.type === "delta").map(e => e.text).join(""), "Mệnh có Vũ Khúc.");
  assert.equal(ev[4].wallet.free.used, 1);
  assert.ok(s.sent.context.includes("BÀI LUẬN GIẢI")); assert.equal(s.sent.messages[0].content, "Mệnh của tôi nói gì về công việc?");
  assert.equal(JSON.stringify(s.sent).includes("dropped"), false);                                   // unknown birth fields never reach anything
});

test("after the day's free chats the next one is locked (402) and costs nothing", async () => {
  for (let i = 0; i < FREE_MESSAGES_PER_DAY; i++) await events(await handleChat(post(ask()), make(llmOf([{ text: "ok" }])).deps));
  assert.equal(await free(), FREE_MESSAGES_PER_DAY);
  const s = make(llmOf([{ text: "never" }]));
  const res = await handleChat(post(ask()), s.deps);
  assert.equal(res.status, 402);
  const b = await res.json() as any; assert.equal(b.detail, "locked"); assert.equal(b.wallet.free.remaining, 0);
  assert.equal(s.llmCalls, 0); assert.equal(s.factsCalls, 0);
});

test("with coins the chat keeps working after the free allowance, one coin each", async () => {
  for (let i = 0; i < FREE_MESSAGES_PER_DAY; i++) await events(await handleChat(post(ask()), make(llmOf([{ text: "ok" }])).deps));
  await grant(db, uid, 2, "g");
  const ev = await events(await handleChat(post(ask()), make(llmOf([{ text: "ok" }])).deps));
  assert.equal(ev[0].source, "coin"); assert.equal(ev.at(-1).wallet.coins, 1);
});

test("a model failure before any text refunds the chat", async () => {
  const ev = await events(await handleChat(post(ask()), make(llmOf([], new Error("overloaded"))).deps));
  const err = ev.find(e => e.type === "error");
  assert.equal(err.refunded, true); assert.equal(await free(), 0);
});

test("a refusal or an empty answer refunds the chat", async () => {
  const ev = await events(await handleChat(post(ask()), make(llmOf([{ stop: "refusal" }])).deps));
  assert.equal(ev.find(e => e.type === "error").refunded, true); assert.equal(await free(), 0);
  const ev2 = await events(await handleChat(post(ask()), make(llmOf([{ stop: "end_turn" }])).deps));
  assert.equal(ev2.find(e => e.type === "error").refunded, true); assert.equal(await free(), 0);
});

test("a failure after text was delivered keeps the charge", async () => {
  const ev = await events(await handleChat(post(ask()), make(llmOf([{ text: "Mệnh " }], new Error("cut"))).deps));
  assert.equal(ev.find(e => e.type === "error").refunded, false); assert.equal(await free(), 1);
});

test("a guest can reach the route but not send: 401, nothing computed or charged", async () => {
  const s = make(llmOf([{ text: "x" }]));
  const res = await handleChat(post(ask()), { ...s.deps, user: null });
  assert.equal(res.status, 401); assert.equal(s.llmCalls + s.factsCalls, 0);
});

test("general mode: no chart in the body, no chart facts, the short general prompt, one free chat", async () => {
  const s = make(llmOf([{ text: "Hóa Lộc là " }, { text: "một trong Tứ Hóa." }, { stop: "end_turn" }]));
  const ev = await events(await handleChat(post({ messages: [{ role: "user", content: "Hóa Lộc là gì?" }] }), s.deps));
  assert.deepEqual(ev.map(e => e.type), ["meta", "delta", "delta", "done", "wallet"]);
  assert.equal(ev[0].mode, "general"); assert.equal(s.factsCalls, 0);
  assert.match(s.sent.instructions, /chế độ hỏi chung/); assert.ok(s.sent.instructions.length < 1200, "short prompt");
  assert.equal(s.sent.context.includes("DỮ KIỆN LÁ SỐ"), false); assert.equal(s.sent.context.includes("BÀI LUẬN GIẢI"), false);
  assert.equal(await free(), 1);
});

test("chat by saved-chart id: the stored birth is used; another user's chart id is not found (404) and costs nothing", async () => {
  await db.prepare("INSERT INTO charts (user_id, fp, id, label, rel, req_json, updated_at) VALUES (?, ?, ?, ?, ?, ?, 1)")
    .bind(uid, "1990-5-17-10-30-male", "mine1", "Tôi", "Tôi", JSON.stringify({ year: 1990, month: 5, day: 17, hour: 10, minute: 30, gender: "male" })).run();
  const s = make(llmOf([{ text: "ok" }]));
  let sentBirth: any = null; const facts = s.deps.facts; s.deps.facts = async b => { sentBirth = b; return facts(b); };
  const ev = await events(await handleChat(post({ chart_id: "mine1", messages: [{ role: "user", content: "Mệnh tôi?" }] }), s.deps));
  assert.equal(ev[0].mode, "chart"); assert.equal(sentBirth.year, 1990); assert.equal(sentBirth.day, 17);
  assert.ok(s.sent.context.includes("BÀI LUẬN GIẢI"));
  // someone else's chart id: the lookup is by (user, id), so it does not exist for this user
  const owner = uid; uid = `c${++n}`;
  await db.prepare("INSERT INTO users (id, google_sub, email, created_at) VALUES (?, ?, ?, 1)").bind(uid, `s${n}`, `c${n}@x.test`).run();
  const t = make(llmOf([{ text: "never" }]));
  const res = await handleChat(post({ chart_id: "mine1", messages: [{ role: "user", content: "Mệnh?" }] }), t.deps);
  assert.equal(res.status, 404); assert.equal(t.llmCalls + t.factsCalls, 0); assert.equal(await free(), 0);
  assert.notEqual(owner, uid);
  // malformed ids, or a birth and an id together, are refused
  assert.equal((await handleChat(post({ chart_id: "../x", messages: [{ role: "user", content: "a" }] }), t.deps)).status, 400);
  assert.equal((await handleChat(post({ chart_id: "mine1", birth, messages: [{ role: "user", content: "a" }] }), t.deps)).status, 400);
});

test("two free chats a day, then 1 xu each; the next day (Vietnam time) the free ones come back", async () => {
  const T = Date.UTC(2026, 9, 23, 5, 0), at = (now: number) => { const s = make(llmOf([{ text: "ok" }])); s.deps.now = () => now; return s.deps; };
  for (let i = 0; i < FREE_MESSAGES_PER_DAY; i++) assert.equal((await events(await handleChat(post(ask()), at(T))))[0].source, "free");
  assert.equal((await handleChat(post(ask()), at(T))).status, 402);
  await grant(db, uid, 1, "g1", T);
  const paid = await events(await handleChat(post(ask()), at(T)));
  assert.equal(paid[0].source, "coin"); assert.equal(paid.at(-1).wallet.coins, 0);
  const next = Date.UTC(2026, 9, 23, 17, 0);                                    // 00:00 on 24 Oct in Vietnam
  const ev = await events(await handleChat(post(ask()), at(next)));
  assert.equal(ev[0].source, "free"); assert.equal(ev.at(-1).wallet.free.remaining, FREE_MESSAGES_PER_DAY - 1);
});

test("after a top-up the chat is free up to 30 a day for 30 days, then 1 xu", async () => {
  const T = Date.UTC(2026, 9, 23, 5, 0), at = (now: number) => { const s = make(llmOf([{ text: "ok" }])); s.deps.now = () => now; return s.deps; };
  const gen = { messages: [{ role: "user", content: "Tứ Hóa là gì?" }] };            // general mode: same quota, no chart to build each time
  await grantPass(db, uid, "vnpay:t1", T);
  for (let i = 0; i < TOPUP_CHAT.perDay; i++) assert.equal((await events(await handleChat(post(gen), at(T))))[0].source, "free");
  assert.equal((await handleChat(post(gen), at(T))).status, 402);
  await grant(db, uid, 2, "g2", T);
  assert.equal((await events(await handleChat(post(gen), at(T))))[0].source, "coin");
  const after = T + (TOPUP_CHAT.days + 1) * 86400_000;                         // the pass is over: back to 2 a day
  const w = (await events(await handleChat(post(gen), at(after)))).at(-1).wallet;
  assert.equal(w.pass.active, false); assert.equal(w.free.limit, FREE_MESSAGES_PER_DAY);
});

test("if the chart cannot be computed the user is not charged", async () => {
  const res = await handleChat(post(ask()), make(llmOf([{ text: "x" }]), false).deps);
  assert.equal(res.status, 502); assert.equal(await free(), 0);
});
