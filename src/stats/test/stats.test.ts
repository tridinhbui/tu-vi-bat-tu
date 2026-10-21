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

test("with nothing recorded yet the page shows the starting figures, 102 scans and 75 sign-ins", async () => {
  const s = await getStats(db);
  assert.deepEqual([s.scans, s.signins, s.live], [102, 75, true]);
});

test("each event adds exactly one, even in parallel, and the other counter is untouched", async () => {
  await Promise.all(Array.from({ length: 25 }, () => bump(db, "scans")));
  await bump(db, "signins");
  const s = await getStats(db);
  assert.deepEqual([s.scans, s.signins], [102 + 25, 75 + 1]);
});

test("re-running the migrations does not reset the counters", async () => {
  const sql = readFileSync("migrations/app/0004_stats.sql", "utf8").replace(/--.*$/gm, "");
  for (const stmt of sql.split(";").map(s => s.trim()).filter(Boolean)) await db.prepare(stmt).run();
  assert.equal((await getStats(db)).scans, 102 + 25);
});

test("the endpoint answers with the totals and a short cache; without a database it still shows the starting figures", async () => {
  const ok = await handleStats(db);
  assert.equal(ok.status, 200); assert.match(ok.headers.get("cache-control")!, /max-age=3/);
  const b = await ok.json() as any; assert.equal(b.scans, 127); assert.equal(b.signins, 76); assert.equal(b.live, true); assert.equal(typeof b.at, "number");
  const none = await handleStats(undefined);
  assert.equal(none.status, 200); assert.deepEqual(Object.values(await none.json() as any).slice(0, 3), [102, 75, false]);
});

test("a missing table is not an error: base figures are shown, and the first event creates the table", async () => {
  await db.prepare("ALTER TABLE stats RENAME TO stats_off").run();
  try {
    assert.deepEqual(Object.values(await getStats(db)).slice(0, 3), [102, 75, false]);
    await bump(db, "scans");                                  // must not throw; creates the table
    const s = await getStats(db);
    assert.deepEqual([s.scans, s.signins, s.live], [103, 75, true]);
  } finally { await db.prepare("DROP TABLE IF EXISTS stats").run(); await db.prepare("ALTER TABLE stats_off RENAME TO stats").run(); }
});
