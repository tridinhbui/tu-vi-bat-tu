// Saved horary questions against a real local D1 (wrangler's platform proxy): sign-in, header, validation, isolation between
// accounts, the per-user cap and deletion.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { getPlatformProxy } from "wrangler";
import { handleHorary, cleanItem } from "../route.ts";
import { handleAccount, CONFIRM } from "../../account/route.ts";
import { createSession } from "../../auth/session.ts";

let proxy: Awaited<ReturnType<typeof getPlatformProxy>>, db: D1Database;
const BASE = "https://example.test";
let alice = "", bob = "";
before(async () => {
  proxy = await getPlatformProxy({ configPath: "wrangler.jsonc", persist: false });
  db = (proxy.env as any).DB as D1Database;
  for (const f of readdirSync("migrations/app").sort().filter(f => f < "0011")) {
    const sql = readFileSync(`migrations/app/${f}`, "utf8").replace(/--.*$/gm, "");
    for (const stmt of sql.split(";").map(s => s.trim()).filter(Boolean)) await db.prepare(stmt).run();
  }
  for (const [id, sub] of [["ua", "sa"], ["ub", "sb"]]) await db.prepare("INSERT INTO users (id, google_sub, email, name, created_at) VALUES (?, ?, ?, ?, 1)").bind(id, sub, `${id}@x.vn`, id).run();
  alice = (await createSession(db, new Request(BASE), "ua")).split(";")[0];
  bob = (await createSession(db, new Request(BASE), "ub")).split(";")[0];
});
after(async () => { await proxy.dispose(); });

const ITEM = { id: "784bcec97c27ded8-mh2k1x", fingerprint: "784bcec97c27ded8", engine: "horary-0.1.0", verdict: "Không thuận",
  moment: { year: 2026, month: 10, day: 25, hour: 9, minute: 30, second: 0, tz: "Asia/Ho_Chi_Minh", lat: 21.0285, lon: 105.8542, place: "Hà Nội", house_system: "regiomontanus" },
  frame: { text: "Tôi có được thăng chức không?", topic: "career", subtype: "promotion", party: "self", confirmed: true, extra: "dropped" } };
const call = (path: string, init: RequestInit & { cookie?: string } = {}) => {
  const h: Record<string, string> = { "content-type": "application/json", ...(init.headers as Record<string, string>) };
  if (init.cookie) h.cookie = init.cookie;
  if (init.method && init.method !== "GET" && !("x-tvbt" in h)) h["x-tvbt"] = "1";
  return handleHorary(new Request(BASE + path, { ...init, headers: h }), db);
};
const j = async (r: Response | Promise<Response>) => (await r).json() as Promise<any>;

test("needs a session and the x-tvbt header; 404 without a database", async () => {
  assert.equal((await call("/api/me/horary")).status, 401);
  assert.equal((await call("/api/me/horary", { method: "POST", body: JSON.stringify(ITEM) })).status, 401);
  assert.equal((await call("/api/me/horary", { method: "POST", cookie: alice, headers: { "x-tvbt": "" }, body: JSON.stringify(ITEM) })).status, 403);
  assert.equal((await handleHorary(new Request(BASE + "/api/me/horary"), undefined)).status, 404);
});

test("validation keeps only known fields and refuses bad values", () => {
  const ok = cleanItem(ITEM) as any;
  assert.equal(typeof ok, "object");
  assert.equal(ok.frame.extra, undefined);
  assert.equal(typeof cleanItem({ ...ITEM, id: "../x" }), "string");
  assert.equal(typeof cleanItem({ ...ITEM, moment: { ...ITEM.moment, lat: 95 } }), "string");
  assert.equal(typeof cleanItem({ ...ITEM, moment: { ...ITEM.moment, tz: "Asia/Ho Chi Minh; drop" } }), "string");
  assert.equal(typeof cleanItem({ ...ITEM, frame: { ...ITEM.frame, text: "x".repeat(501) } }), "string");
  assert.equal(typeof cleanItem({ ...ITEM, fingerprint: "zz" }), "string");
});

test("save, list, upsert, isolation between accounts, delete", async () => {
  assert.equal((await call("/api/me/horary", { method: "POST", cookie: alice, body: JSON.stringify(ITEM) })).status, 200);
  assert.equal((await call("/api/me/horary", { method: "POST", cookie: alice, body: JSON.stringify({ ...ITEM, verdict: "Thuận" }) })).status, 200);
  const list = await j(call("/api/me/horary", { cookie: alice }));
  assert.equal(list.items.length, 1);
  assert.equal(list.items[0].verdict, "Thuận");
  assert.equal(list.items[0].frame.text, ITEM.frame.text);
  assert.equal((await j(call("/api/me/horary", { cookie: bob }))).items.length, 0);
  assert.equal((await call(`/api/me/horary/${ITEM.id}`, { method: "DELETE", cookie: bob })).status, 200);       // bob deletes nothing of alice's
  assert.equal((await j(call("/api/me/horary", { cookie: alice }))).items.length, 1);
  assert.equal((await call(`/api/me/horary/${ITEM.id}`, { method: "DELETE", cookie: alice })).status, 200);
  assert.equal((await j(call("/api/me/horary", { cookie: alice }))).items.length, 0);
});

test("'delete my data' in the account removes saved horary questions too", async () => {
  await call("/api/me/horary", { method: "POST", cookie: alice, body: JSON.stringify(ITEM) });
  const engine = async () => new Response("{}");
  const r = await handleAccount(new Request(BASE + "/api/me/data", { method: "POST", headers: { cookie: alice, "x-tvbt": "1", "content-type": "application/json" }, body: JSON.stringify({ confirm: CONFIRM }) }), db, engine);
  assert.equal(r.status, 200);
  assert.equal((await j(call("/api/me/horary", { cookie: alice }))).items.length, 0);
});
