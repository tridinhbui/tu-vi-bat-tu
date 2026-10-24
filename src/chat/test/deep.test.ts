// The deep reading: coins only (or the chart's Cao cấp package), paid once, kept, refunded when it does not finish, saved even if the browser leaves.
import { test, before, after, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { getPlatformProxy } from "wrangler";
import knowledge from "../../interpret/generated/knowledge.json" with { type: "json" };
import { handleDeep, handleDeepStatus, DEEP_INSTRUCTIONS, type DeepDeps } from "../deep.ts";
import { buyPlan } from "../../billing/paywall.ts";
import { getWallet, grant } from "../../billing/wallet.ts";
import { COSTS, FREE_MESSAGES_PER_DAY } from "../../billing/config.ts";
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
  uid = `d${++n}`;
  await db.prepare("INSERT INTO users (id, google_sub, email, created_at) VALUES (?, ?, ?, 1)").bind(uid, `s${n}`, `d${n}@x.test`).run();
});

const birth = { year: 1990, month: 5, day: 17, hour: 10, minute: 30, gender: "male" };
const post = (body: unknown, headers: Record<string, string> = { "x-tvbt": "1" }) =>
  new Request("https://x.test/api/me/deep", { method: "POST", headers, body: JSON.stringify(body) });
const TEXT = "Cung Mệnh có Vũ Khúc và Thiên Phủ, nghiêng về quản lý và tích lũy. ".repeat(6);
const good: LlmEvent[] = [{ text: TEXT.slice(0, 100) }, { text: TEXT.slice(100) }, { stop: "end_turn" }];
const llmOf = (events: LlmEvent[], then?: Error): Llm => async function* () { for (const e of events) yield e; if (then) throw then; };

function make(llm: Llm | null) {
  const spy = { llmCalls: 0, sent: null as any, jobs: [] as Promise<unknown>[], deps: null as any as DeepDeps };
  spy.deps = {
    db, user: { id: uid, email: "", name: "", picture: "" }, knowledge: knowledge as any,
    llm: llm && (async function* (req) { spy.llmCalls++; spy.sent = req; yield* llm(req); }),
    facts: async () => new Response(JSON.stringify(chart.facts)),
    defer: p => { spy.jobs.push(p); },
  };
  return spy;
}
const events = async (res: Response) => (await res.text()).split("\n\n").filter(l => l.startsWith("data: ")).map(l => JSON.parse(l.slice(6)));
const coins = async () => (await getWallet(db, uid)).coins;
const saved = (chapter = "cong_danh") => db.prepare("SELECT text FROM deep_readings WHERE user_id = ? AND chapter = ?").bind(uid, chapter).first<{ text: string }>();
const ask = (chapter = "cong_danh") => ({ birth, chapter });

test("bad requests cost nothing", async () => {
  const s = make(llmOf(good));
  assert.equal((await handleDeep(post(ask(), {}), s.deps)).status, 403);
  assert.equal((await handleDeep(new Request("https://x.test/api/me/deep"), s.deps)).status, 405);
  assert.equal((await handleDeep(post({ birth, chapter: "nope" }), s.deps)).status, 400);
  assert.equal((await handleDeep(post({ chapter: "menh" }), s.deps)).status, 400);
  assert.equal((await handleDeep(post(ask()), make(null).deps)).status, 503);
  assert.equal(s.llmCalls, 0);
});

test("never uses the free chats: no coins means locked even with free chats left", async () => {
  const s = make(llmOf(good));
  const res = await handleDeep(post(ask()), s.deps);
  assert.equal(res.status, 402);
  const b = await res.json() as any; assert.equal(b.need, COSTS.deep); assert.equal(b.wallet.free.remaining, FREE_MESSAGES_PER_DAY);
  assert.equal(s.llmCalls, 0);
  await grant(db, uid, COSTS.deep - 1, "short");
  assert.equal((await handleDeep(post(ask()), s.deps)).status, 402);                 // one coin short
  assert.equal(await coins(), COSTS.deep - 1);
});

test("a finished reading costs coins once, is saved, and opens again for free", async () => {
  await grant(db, uid, COSTS.deep + 5, "buy");
  const s = make(llmOf(good));
  const ev = await events(await handleDeep(post(ask()), s.deps));
  await Promise.all(s.jobs);
  assert.deepEqual(ev.map(e => e.type), ["meta", "delta", "delta", "done", "wallet"]);
  assert.equal(ev[0].source, "coin"); assert.equal(ev.filter(e => e.type === "delta").map(e => e.text).join(""), TEXT);
  assert.equal(await coins(), 5);
  assert.equal((await saved())!.text, TEXT);
  assert.equal(s.sent.instructions, DEEP_INSTRUCTIONS); assert.match(s.sent.messages[0].content, /Công danh/);
  assert.ok(s.sent.context.includes("BÀI LUẬN GIẢI"));

  // again, with fewer coins than the price and no model: it replays from storage and charges nothing
  const again = make(null);
  const ev2 = await events(await handleDeep(post(ask()), again.deps));
  assert.deepEqual(ev2.map(e => e.type), ["meta", "delta", "done", "wallet"]);
  assert.equal(ev2[0].source, "saved"); assert.equal(ev2[1].text, TEXT);
  assert.equal(await coins(), 5);
});

test("another chapter is a separate purchase", async () => {
  await grant(db, uid, COSTS.deep * 2, "two");
  for (const ch of ["cong_danh", "tai_bach"]) { const s = make(llmOf(good)); await events(await handleDeep(post(ask(ch)), s.deps)); await Promise.all(s.jobs); }
  assert.equal(await coins(), 0);
  assert.ok(await saved("cong_danh")); assert.ok(await saved("tai_bach"));
});

test("a reading that does not finish is refunded and not saved", async () => {
  await grant(db, uid, COSTS.deep, "buy");
  for (const [label, llm] of [["cut off", llmOf([{ text: TEXT }, { stop: "max_tokens" }])], ["error", llmOf([{ text: "Mệnh " }], new Error("x"))], ["refusal", llmOf([{ stop: "refusal" }])], ["too short", llmOf([{ text: "ok" }, { stop: "end_turn" }])]] as const) {
    const s = make(llm); const ev = await events(await handleDeep(post(ask()), s.deps)); await Promise.all(s.jobs);
    assert.equal(ev.find(e => e.type === "error").refunded, true, label);
    assert.equal(await coins(), COSTS.deep, label); assert.equal(await saved(), null, label);
  }
});

test("if the browser leaves mid-way the reading is still finished, saved and charged once", async () => {
  await grant(db, uid, COSTS.deep, "buy");
  let release!: () => void; const gate = new Promise<void>(r => (release = r));
  const slow: Llm = async function* () { yield { text: TEXT.slice(0, 50) }; await gate; yield { text: TEXT.slice(50) }; yield { stop: "end_turn" }; };
  const s = make(slow);
  const res = await handleDeep(post(ask()), s.deps);
  await res.body!.cancel();                                  // the reader walks away
  release();
  await Promise.all(s.jobs);
  assert.equal((await saved())!.text, TEXT); assert.equal(await coins(), 0);
  const ev = await events(await handleDeep(post(ask()), make(null).deps));
  assert.equal(ev[0].source, "saved");                       // coming back finds it, no second charge
});

test("Cao cấp: every Luận AI chapter of that chart is written without xu; another chart still costs; status says what is written", async () => {
  const FP = "1990-5-17-10-30-male";
  await grant(db, uid, 400, "t");
  assert.ok((await buyPlan(db, uid, FP, "cao_cap")).ok);
  const left = await coins(), s = make(llmOf(good));
  const ev = await events(await handleDeep(post(ask("tai_bach")), s.deps));
  await Promise.all(s.jobs);
  assert.deepEqual(ev[0], { type: "meta", source: "plan", cost: 0 });
  assert.equal(await coins(), left, "no xu taken");
  assert.equal((await saved("tai_bach"))?.text, TEXT);
  const st = (b: unknown) => handleDeepStatus(post(b), { db, user: s.deps.user });
  assert.deepEqual(await (await st({ birth })).json(), { written: ["tai_bach"], plan: true, cost: COSTS.deep });
  assert.deepEqual(await (await st({ birth: { ...birth, day: 18 } })).json(), { written: [], plan: false, cost: COSTS.deep });
  assert.equal((await st({ nope: 1 })).status, 400);
  // a failure on the package refunds nothing because nothing was charged, and says so
  const f = make(llmOf([{ text: "ngắn" }, { stop: "max_tokens" }]));
  const fe = await events(await handleDeep(post(ask("phu_the")), f.deps)); await Promise.all(f.jobs);
  assert.equal(fe.find(e => e.type === "error")?.refunded, true); assert.equal(await coins(), left);
  // another chart pays
  const o = make(llmOf(good));
  await events(await handleDeep(post({ birth: { ...birth, day: 18 }, chapter: "menh" }), o.deps)); await Promise.all(o.jobs);
  assert.equal(await coins(), left - COSTS.deep);
});
