import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { getPlatformProxy } from "wrangler";
import { bump, getStats, handleStats } from "../stats.ts";

let proxy: Awaited<ReturnType<typeof getPlatformProxy>>, db: D1Database;
before(async () => {
  proxy = await getPlatformProxy({ configPath: "wrangler.jsonc", persist: false });
  db = (proxy.env as any).DB as D1Database;
  for (const f of readdirSync("migrations/app").sort()) {
    const sql = readFileSync(`migrations/app/${f}`, "utf8").replace(/--.*$/gm, "");
    for (const stmt of sql.split(";").map(s => s.trim()).filter(Boolean)) await db.prepare(stmt).run();
  }
});
after(async () => { await proxy.dispose(); });

test("the counters start at 37 charts and 15 people", async () => {
  const s = await getStats(db);
  assert.deepEqual([s!.charts, s!.users], [37, 15]);
});

test("each event adds exactly one, even in parallel, and the other counter is untouched", async () => {
  await Promise.all(Array.from({ length: 25 }, () => bump(db, "charts")));
  await bump(db, "users");
  const s = await getStats(db);
  assert.deepEqual([s!.charts, s!.users], [37 + 25, 15 + 1]);
});

test("re-running the migration does not reset the counters", async () => {
  const sql = readFileSync("migrations/app/0004_stats.sql", "utf8").replace(/--.*$/gm, "");
  for (const stmt of sql.split(";").map(s => s.trim()).filter(Boolean)) await db.prepare(stmt).run();
  assert.equal((await getStats(db))!.charts, 37 + 25);
});

test("the endpoint answers with the counts and a short cache, and 503 without a database", async () => {
  const ok = await handleStats(db);
  assert.equal(ok.status, 200); assert.match(ok.headers.get("cache-control")!, /max-age=3/);
  const b = await ok.json() as any; assert.equal(b.charts, 62); assert.equal(b.users, 16); assert.equal(typeof b.at, "number");
  assert.equal((await handleStats(undefined)).status, 503);
});

test("a missing table is not an error: stats are just unavailable", async () => {
  await db.prepare("ALTER TABLE stats RENAME TO stats_off").run();
  try {
    assert.equal(await getStats(db), null);
    await bump(db, "charts");                                 // must not throw
    assert.equal((await handleStats(db)).status, 503);
  } finally { await db.prepare("ALTER TABLE stats_off RENAME TO stats").run(); }
});
