// Profile, share links and account deletion against a real local D1 (wrangler's platform proxy). The engine is a stub that echoes
// what it was asked, so the tests see exactly which birth data reaches it and what a viewer gets back.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { getPlatformProxy } from "wrangler";
import { handleAccount, CONFIRM } from "../route.ts";
import { cleanProfile } from "../profile.ts";
import { scrub } from "../shares.ts";
import { createSession } from "../../auth/session.ts";
import { syncCharts } from "../../auth/charts.ts";

let proxy: Awaited<ReturnType<typeof getPlatformProxy>>, db: D1Database;
const BASE = "https://example.test";
const calls: { path: string; body: Record<string, unknown> }[] = [];
const engine = async (path: string, body: Record<string, unknown>) => {
  calls.push({ path, body });
  return new Response(JSON.stringify({ tuvi: { lunar: { day: 23, month: 4, year: 1990, leap: false }, trace: { steps: [{ inputs: { naive: "1990-05-17T10:30" } }] } },
    normalization_trace: { steps: [{ id: "tz.resolve" }] }, input: body, echo: body.to_year ?? null }), { headers: { "content-type": "application/json" } });
};
let alice = "", bob = "";

before(async () => {
  proxy = await getPlatformProxy({ configPath: "wrangler.jsonc", persist: false });
  db = (proxy.env as any).DB as D1Database;
  // the older migrations only: profiles and shares must appear on first use, as on a deploy where 0008 was not applied yet
  for (const f of readdirSync("migrations/app").sort().filter(f => f < "0008")) {
    const sql = readFileSync(`migrations/app/${f}`, "utf8").replace(/--.*$/gm, "");
    for (const stmt of sql.split(";").map(s => s.trim()).filter(Boolean)) await db.prepare(stmt).run();
  }
  for (const [id, sub] of [["ua", "sa"], ["ub", "sb"]]) await db.prepare("INSERT INTO users (id, google_sub, email, name, created_at) VALUES (?, ?, ?, ?, 1)").bind(id, sub, `${id}@x.vn`, id).run();
  alice = (await createSession(db, new Request(BASE), "ua")).split(";")[0];
  bob = (await createSession(db, new Request(BASE), "ub")).split(";")[0];
  await syncCharts(db, "ua", [{ id: "me1", label: "Minh", rel: "Tôi", req: { year: 1990, month: 5, day: 17, hour: 10, minute: 30, gender: "male", tz: "Asia/Ho_Chi_Minh" } },
    { id: "mom", label: "Mẹ", rel: "Người thân", req: { year: 1965, month: 2, day: 3, hour: 6, minute: 0, gender: "female" } }]);
  await syncCharts(db, "ub", [{ id: "bob1", label: "Bob", rel: "Tôi", req: { year: 1992, month: 1, day: 1, hour: 1, minute: 0, gender: "male" } }]);
});
after(async () => { await proxy.dispose(); });

const call = (path: string, init: RequestInit & { cookie?: string } = {}) => {
  const h: Record<string, string> = { "content-type": "application/json", ...(init.headers as Record<string, string>) };
  if (init.cookie) h.cookie = init.cookie;
  if (init.method && init.method !== "GET" && !("x-tvbt" in h)) h["x-tvbt"] = "1";
  return handleAccount(new Request(BASE + path, { ...init, headers: h }), db, engine);
};
const j = async (r: Response | Promise<Response>) => (await r).json() as Promise<any>;
const PROFILE = { name: "Nguyễn Minh", gender: "male", cal: "solar", year: 1990, month: 5, day: 17, hour: 10, minute: 30, place: "TP. Hồ Chí Minh", tz: "Asia/Ho_Chi_Minh", career: "tim_viec", relationship: "ket_hon" };

test("every /api/me route needs a session, and writes need the x-tvbt header", async () => {
  for (const [p, m] of [["/api/me/profile", "GET"], ["/api/me/shares", "GET"], ["/api/me/profile", "PUT"], ["/api/me/charts/me1/share", "POST"], ["/api/me/data", "POST"], ["/api/me/account", "POST"]])
    assert.equal((await call(p, { method: m, body: m === "GET" ? undefined : "{}" })).status, 401, `${m} ${p}`);
  assert.equal((await call("/api/me/profile", { method: "PUT", cookie: alice, headers: { "x-tvbt": "" }, body: JSON.stringify(PROFILE) })).status, 403);
  assert.equal((await call("/api/me/account", { method: "POST", cookie: alice, headers: { "x-tvbt": "" }, body: JSON.stringify({ confirm: CONFIRM }) })).status, 403);
  assert.equal((await handleAccount(new Request(BASE + "/api/me/profile"), undefined, engine)).status, 404);
});

test("profile: validated field by field, stored per user, invisible to another account", async () => {
  assert.equal(typeof cleanProfile({ ...PROFILE, month: 2, day: 30 }), "string");          // no 30 February in dương lịch
  assert.equal(typeof cleanProfile({ ...PROFILE, cal: "lunar", month: 2, day: 30 }), "object");   // âm lịch months have 30 days
  assert.equal(typeof cleanProfile({ ...PROFILE, career: "ceo" }), "string");
  assert.equal(typeof cleanProfile({ ...PROFILE, tz: "../etc" }), "string");
  const unknownHour = cleanProfile({ ...PROFILE, hour: null, minute: 45 }) as any;
  assert.equal(unknownHour.hour, null); assert.equal(unknownHour.minute, 0);
  assert.equal((cleanProfile({ ...PROFILE, name: "x".repeat(99) }) as any).name.length, 60);
  assert.deepEqual(await j(call("/api/me/profile", { cookie: alice })), { profile: null });
  assert.equal((await call("/api/me/profile", { method: "PUT", cookie: alice, body: JSON.stringify({ ...PROFILE, year: 1800 }) })).status, 400);
  const put = await j(call("/api/me/profile", { method: "PUT", cookie: alice, body: JSON.stringify({ ...PROFILE, evil: 1 }) }));
  assert.equal(put.profile.evil, undefined);
  assert.deepEqual(put.profile.solar, { year: 1990, month: 5, day: 17 });
  const lunar = await j(call("/api/me/profile", { method: "PUT", cookie: alice, body: JSON.stringify({ ...PROFILE, cal: "lunar", month: 4, day: 23, leap: false, solar: { year: 1990, month: 5, day: 17 } }) }));
  assert.equal(lunar.profile.cal, "lunar"); assert.deepEqual(lunar.profile.solar, { year: 1990, month: 5, day: 17 });
  assert.equal((await j(call("/api/me/profile", { cookie: alice }))).profile.career, "tim_viec");
  assert.deepEqual(await j(call("/api/me/profile", { cookie: bob })), { profile: null });
});

test("share links: only the owner of a chart can create, change or revoke one; a hidden link never gives out the birth", async () => {
  assert.equal((await call("/api/me/charts/nope/share", { method: "POST", cookie: alice, body: "{}" })).status, 404);
  assert.equal((await call("/api/me/charts/bob1/share", { method: "POST", cookie: alice, body: "{}" })).status, 404);   // Bob's chart
  const { share } = await j(call("/api/me/charts/me1/share", { method: "POST", cookie: alice, body: "{}" }));
  assert.match(share.id, /^[A-Za-z0-9_-]{22}$/);
  assert.equal(share.hide, true);                                     // hidden unless the owner says otherwise
  // the viewer's side: no name, no day / month / hour
  const pub = await j(call(`/api/share/${share.id}`));
  assert.equal(pub.label, null); assert.equal(pub.hide, true);
  assert.deepEqual(Object.keys(pub.req).sort(), ["gender", "tz", "year"]);
  // the engine gets the stored birth; a viewer cannot replace it, only pick allowed options such as the year to look at
  calls.length = 0;
  const out = await j(call(`/api/share/${share.id}/chart`, { method: "POST", body: JSON.stringify({ day: 1, month: 1, hour: 0, to_year: 2030, chapter: "../x" }) }));
  assert.deepEqual(calls[0], { path: "/api/chart", body: { year: 1990, month: 5, day: 17, hour: 10, minute: 30, gender: "male", tz: "Asia/Ho_Chi_Minh", to_year: 2030 } });
  assert.equal(out.input, undefined); assert.equal(out.echo, 2030);
  assert.deepEqual(out.normalization_trace, { steps: [] }); assert.deepEqual(out.tuvi.trace, { steps: [] });
  assert.deepEqual(out.tuvi.lunar, { year: 1990, month: null, day: null, leap: false, hidden: true });
  assert.equal(JSON.stringify(out).includes("05-17"), false);
  assert.equal((await call(`/api/share/${share.id}/rules`, { method: "POST", body: "{}" })).status, 404);    // not an endpoint a viewer may run
  assert.equal((await call(`/api/share/${share.id}`, { method: "POST", body: "{}" })).status, 405);
  // Bob can neither switch the toggle nor revoke Alice's link, and does not see it in his list
  assert.equal((await call(`/api/me/shares/${share.id}`, { method: "PATCH", cookie: bob, body: JSON.stringify({ hide: false }) })).status, 404);
  assert.equal((await call(`/api/me/shares/${share.id}`, { method: "DELETE", cookie: bob })).status, 404);
  assert.deepEqual((await j(call("/api/me/shares", { cookie: bob }))).shares, []);
  // the owner shows the birth: the viewer now gets the name and the request, and the engine answer is passed through as it is
  assert.equal((await call(`/api/me/shares/${share.id}`, { method: "PATCH", cookie: alice, body: JSON.stringify({ hide: "no" }) })).status, 400);
  assert.equal((await call(`/api/me/shares/${share.id}`, { method: "PATCH", cookie: alice, body: JSON.stringify({ hide: false }) })).status, 200);
  const open = await j(call(`/api/share/${share.id}`));
  assert.equal(open.label, "Minh"); assert.equal(open.req.day, 17);
  assert.equal((await j(call(`/api/share/${share.id}/chart`, { method: "POST", body: "{}" }))).tuvi.lunar.day, 23);
  const list = (await j(call("/api/me/shares", { cookie: alice }))).shares;
  assert.deepEqual(list.map((s: any) => [s.id, s.chart_id, s.label, s.hide]), [[share.id, "me1", "Minh", false]]);
  // revoked: gone for viewers, for the engine proxy and from the owner's list; revoking twice is not found
  assert.equal((await call(`/api/me/shares/${share.id}`, { method: "DELETE", cookie: alice })).status, 200);
  assert.equal((await call(`/api/share/${share.id}`)).status, 404);
  calls.length = 0;
  assert.equal((await call(`/api/share/${share.id}/chart`, { method: "POST", body: "{}" })).status, 404);
  assert.equal(calls.length, 0);
  assert.deepEqual((await j(call("/api/me/shares", { cookie: alice }))).shares, []);
  assert.equal((await call(`/api/me/shares/${share.id}`, { method: "DELETE", cookie: alice })).status, 404);
  assert.equal((await call(`/api/me/shares/${share.id}`, { method: "PATCH", cookie: alice, body: JSON.stringify({ hide: true }) })).status, 404);
  assert.equal((await call("/api/share/not-a-share-id")).status, 404);
});

test("deleting a saved chart ends its share links", async () => {
  const { share } = await j(call("/api/me/charts/mom/share", { method: "POST", cookie: alice, body: JSON.stringify({ hide: false }) }));
  assert.equal(share.hide, false);
  assert.equal((await call(`/api/share/${share.id}`)).status, 200);
  await db.prepare("DELETE FROM charts WHERE user_id = 'ua' AND id = 'mom'").run();
  assert.equal((await call(`/api/share/${share.id}`)).status, 404);
  await syncCharts(db, "ua", [{ id: "mom", label: "Mẹ", rel: "Người thân", req: { year: 1965, month: 2, day: 3, hour: 6, minute: 0, gender: "female" } }]);
});

test("scrub keeps the chart and drops what prints the birth", () => {
  assert.deepEqual(scrub({ a: [{ trace: { steps: [1] }, lunar: { year: 2000, day: 1, month: 2 } }], birth: { day: 1 }, keep: 1 }),
    { a: [{ trace: { steps: [] }, lunar: { year: 2000, month: null, day: null, leap: false, hidden: true } }], keep: 1 });
});

test("delete my data clears charts, profile, shares and paid readings but keeps the account and its coins", async () => {
  await call("/api/me/profile", { method: "PUT", cookie: alice, body: JSON.stringify(PROFILE) });
  const { share } = await j(call("/api/me/charts/me1/share", { method: "POST", cookie: alice, body: "{}" }));
  await db.prepare("INSERT INTO deep_readings (user_id, fp, chapter, text, created_at) VALUES ('ua', 'f', 'menh', 't', 1)").run();
  await db.prepare("INSERT INTO wallets (user_id, coins) VALUES ('ua', 7)").run();
  assert.equal((await call("/api/me/data", { method: "POST", cookie: alice, body: JSON.stringify({ confirm: "yes" }) })).status, 400);
  assert.equal((await call("/api/me/data", { method: "POST", cookie: alice, body: JSON.stringify({ confirm: CONFIRM }) })).status, 200);
  const n = async (t: string) => (await db.prepare(`SELECT COUNT(*) AS n FROM ${t} WHERE user_id = 'ua'`).first<{ n: number }>())!.n;
  assert.deepEqual([await n("charts"), await n("profiles"), await n("shares"), await n("deep_readings")], [0, 0, 0, 0]);
  assert.equal((await call(`/api/share/${share.id}`)).status, 404);
  assert.equal(await n("wallets"), 1);
  assert.equal((await call("/api/me/profile", { cookie: alice })).status, 200);       // still signed in
  assert.equal(await n("charts") + (await db.prepare("SELECT COUNT(*) AS n FROM charts WHERE user_id = 'ub'").first<{ n: number }>())!.n, 1);   // Bob untouched
});

test("delete my account removes the user, its sessions and coins, and clears the cookie; other accounts stay", async () => {
  assert.equal((await call("/api/me/account", { method: "POST", cookie: alice, body: "{}" })).status, 400);
  const r = await call("/api/me/account", { method: "POST", cookie: alice, body: JSON.stringify({ confirm: CONFIRM }) });
  assert.equal(r.status, 200);
  assert.match(r.headers.get("set-cookie")!, /tvbt_session=;.*Max-Age=0/);
  assert.equal((await call("/api/me/profile", { cookie: alice })).status, 401);
  for (const t of ["users WHERE id", "sessions WHERE user_id", "wallets WHERE user_id"])
    assert.equal((await db.prepare(`SELECT COUNT(*) AS n FROM ${t} = 'ua'`).first<{ n: number }>())!.n, 0, t);
  assert.equal((await call("/api/me/profile", { cookie: bob })).status, 200);
});
