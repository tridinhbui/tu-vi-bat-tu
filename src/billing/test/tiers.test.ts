// The reading tiers (owner decisions 2026-10-23, 2026-10-24) on real readings and a real local D1: a guest gets the first half of each
// chapter's main reading and nothing else in the JSON; a member Tổng quan and Mệnh whole (no Đọc sâu) and the first half of the rest; a
// package opens its chapters whole; Bát Tự cut per tab (Vận năm opens two tabs); /api/overview, /api/synthesis and /api/interpretation cut
// the same way; a share link reads as a guest; the cache holds one full copy.
import { test, before, after, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { join } from "node:path";
import { getPlatformProxy } from "wrangler";
import { GUEST, SHARED, accessFor, buyPlan, gateOutput, gateOverview, gateResponse, gateSynthesis, gated, isDeep, type Access } from "../paywall.ts";
import { MEMBER_FREE, guestShown, planById } from "../config.ts";
import { grant } from "../wallet.ts";
import { createSession } from "../../auth/session.ts";
import { handleShare } from "../../account/shares.ts";
import { handleInterpret, proseAllChapters } from "../../interpret/route.ts";
import { checkedOnly } from "../../interpret/prose/checked.ts";
import { proseBazi } from "../../interpret/prose/bazi.ts";
import { seedOf } from "../../interpret/prose/chapter.ts";
import { overview } from "../../interpret/overview.ts";
import { BundledStore, type OutputCache } from "../../interpret/store.ts";
import type { ChartInput, Knowledge } from "../../interpret/types.ts";

const FX = join(import.meta.dirname, "..", "..", "interpret", "test", "fixtures");
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, "..", "..", "interpret", "generated", "knowledge.json"), "utf8"));
const ex: ChartInput = JSON.parse(readFileSync(join(FX, "menh_cu_tuat.json"), "utf8")).facts;
const corpus = JSON.parse(gunzipSync(readFileSync(join(FX, "corpus1000.json.gz"))).toString());
const BIRTH = { year: 1990, month: 5, day: 17, hour: 10, minute: 30, gender: "male" }, FP = "1990-5-17-10-30-male";

// the whole report as /api/interpret mode "prose" chapter "all" serves it (and caches it)
const clone = <T>(x: T): T => JSON.parse(JSON.stringify(x));
// as it comes out of the cache: JSON
const FULL = clone({ engine: "e", kbVersion: K.version, chapters: proseAllChapters(ex, K, { allowDraft: true, deep: true, luan: true }).map(c => checkedOnly(c as any)), pass: true }) as any;
const full = (id: string) => FULL.chapters.find((c: any) => c.chapter === id);
const member = (...open: string[]): Access => ({ tier: "member", open: new Set(open) });
const mainOf = (ps: any[]) => ps.filter(p => !isDeep(p)), deepOf = (ps: any[]) => ps.filter(isDeep);
/** the paragraphs a reader must not receive: in the full chapter, not among those sent */
const heldBack = (all: any[], sent: any[]) => { const keep = new Set(sent.map(p => p.text)); return all.filter(p => !keep.has(p.text)); };
/** no sentence of the held-back paragraphs is anywhere in the JSON, unless the same sentence was sent in a kept paragraph */
const assertAbsent = (json: string, ps: any[], what: string, sent: any[] = [], readings: string[] = []) => {
  // a sentence that IS the reading of a rule behind a sentence sent was sent anyway, as that rule's evidence
  const ok = new Set([...sent.flatMap(p => p.sentences.map((s: any) => s.text)), ...readings]);
  for (const p of ps) for (const s of p.sentences) if (!ok.has(s.text)) assert.ok(!json.includes(JSON.stringify(s.text).slice(1, -1)), `${what}: ${s.text.slice(0, 60)}`);
};

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
  uid = `t${++n}`;
  await db.prepare("INSERT INTO users (id, google_sub, email, created_at) VALUES (?, ?, ?, 1)").bind(uid, `ts${n}`, `t${n}@x.test`).run();
});
const cookieFor = async (id: string) => (await createSession(db, new Request("https://tu-vi.test/"), id)).split(";")[0];

test("the worked example has what the tiers act on: chapters with Đọc sâu paragraphs, and chapters of several main paragraphs", () => {
  assert.ok(FULL.chapters.filter((c: any) => deepOf(c.paragraphs).length).length >= 3);
  assert.ok(FULL.chapters.some((c: any) => mainOf(c.paragraphs).length >= 4));
  assert.equal(guestShown(0), 0); assert.equal(guestShown(1), 1); assert.equal(guestShown(2), 1); assert.equal(guestShown(3), 2); assert.equal(guestShown(4), 2); assert.equal(guestShown(18), 9);
});

test("guest: the first half of every chapter's main reading, no Đọc sâu, and no held-back word anywhere in the JSON", () => {
  const out = gateOutput(clone(FULL), GUEST);
  assert.equal(out.chapters.length, FULL.chapters.length);
  for (const g of out.chapters) {
    const f = full(g.chapter), json = JSON.stringify(g);
    if (g.chapter === "bat_tu") continue;                                                   // per tab: next test
    const main = mainOf(f.paragraphs), k = guestShown(main.length);
    assert.deepEqual(g.paragraphs, main.slice(0, k), g.chapter);
    assert.ok(!g.paragraphs.some(isDeep), g.chapter);
    const held = heldBack(f.paragraphs, g.paragraphs);
    assertAbsent(json, held, g.chapter, g.paragraphs, Object.values(g.evidence?.rules ?? {}).map((r: any) => r.reading));
    if (!held.length) { assert.equal(g.locked, undefined, g.chapter); continue; }
    assert.ok(!json.includes(JSON.stringify(f.text).slice(1, -1)), `${g.chapter}: the full text`);
    for (const k2 of ["advice", "theses", "metrics", "quality", "argument"]) assert.equal(g[k2], undefined, `${g.chapter}.${k2}`);
    assert.equal(g.evidence.ledger, undefined); assert.deepEqual(g.evidence.divergences, []);
    const used = new Set(g.paragraphs.flatMap((p: any) => p.sentences.flatMap((s: any) => s.trace.rules)));
    for (const r of Object.keys(g.evidence.rules)) assert.ok(used.has(r), `${g.chapter}: rule ${r} not behind a sentence sent`);
    assert.deepEqual([g.locked.tier, g.locked.shown, g.locked.total, g.locked.deep], ["guest", k, main.length, deepOf(f.paragraphs).length]);
    assert.equal(g.locked.plans, undefined); assert.equal(g.locked.shared, undefined);
  }
  // van_han: the decade starts point into the paragraphs sent
  const vh = out.chapters.find((c: any) => c.chapter === "van_han");
  assert.ok(vh.starts.every((i: number) => i < vh.paragraphs.length));
});

test("member: Tổng quan and Mệnh main reading whole, every other chapter's first half with the packages that open it; no Đọc sâu", () => {
  const out = gateOutput(clone(FULL), member());
  for (const g of out.chapters) {
    const f = full(g.chapter);
    if (g.chapter === "bat_tu") continue;
    const main = mainOf(f.paragraphs), deep = deepOf(f.paragraphs), free = MEMBER_FREE.includes(g.chapter);
    assert.deepEqual(g.paragraphs, free ? main : main.slice(0, guestShown(main.length)), g.chapter);
    if (heldBack(f.paragraphs, g.paragraphs).length === 0) { assert.deepEqual(g, f, `${g.chapter}: nothing held back, nothing changed`); continue; }
    assertAbsent(JSON.stringify(g), heldBack(f.paragraphs, g.paragraphs), g.chapter, g.paragraphs, Object.values(g.evidence?.rules ?? {}).map((r: any) => r.reading));
    assert.equal(g.locked.tier, "member"); assert.equal(g.locked.deep, deep.length);
    if (free) {
      assert.ok(g.advice || !f.advice, `${g.chapter}: advice goes with the whole main reading`);
      assert.deepEqual(g.evidence.ledger, f.evidence.ledger);
      assert.equal(g.locked.shown, g.locked.total);
    } else {
      for (const k of ["advice", "theses"]) assert.equal(g[k], undefined, `${g.chapter}.${k}: restates the whole main reading`);
      assert.equal(g.evidence.ledger, undefined); assert.deepEqual(g.evidence.divergences, []);
    }
    assert.deepEqual(g.locked.plans.map((p: any) => p.id), g.chapter === "van_han" ? ["van_nam", "tron_bo", "cao_cap"] : ["tron_bo", "cao_cap"], g.chapter);
    assert.ok(g.locked.plans.every((p: any) => p.price === p.coins), "nothing spent yet: full price");
  }
  // xu already spent on the chart lower the price shown
  const up = gateOutput(clone(FULL), { tier: "member", open: new Set(["van_han", "bat_tu:dai-van", "bat_tu:luu-nien"]), credit: 49 });
  const cd = up.chapters.find((c: any) => c.chapter === "cong_danh");
  assert.deepEqual(cd.locked.plans.map((p: any) => p.price), [100, 250]);
});

test("buyer: Vận năm opens the đại hạn chapter whole and nothing else; Trọn bộ (for the difference) opens every chapter", async () => {
  await grant(db, uid, 500, "t", 1);
  assert.ok((await buyPlan(db, uid, FP, "van_nam")).ok);
  let a = await accessFor(db, { id: uid }, { ...BIRTH, chapter: "all", mode: "prose", to_year: 2026 });
  assert.equal(a.tier, "member"); assert.equal(a.credit, planById("van_nam")!.coins);
  let out = gateOutput(clone(FULL), a);
  const got = (id: string) => out.chapters.find((c: any) => c.chapter === id);
  assert.deepEqual(got("van_han"), { ...full("van_han"), unlocked: true });
  assert.ok(got("cong_danh").locked && got("cong_danh").paragraphs.length < mainOf(full("cong_danh").paragraphs).length);
  // another chart, another account, a body that is not a birth record: nothing opened
  assert.equal((await accessFor(db, { id: uid }, { ...BIRTH, day: 18 })).open.size, 0);
  assert.equal((await accessFor(db, { id: "nobody" }, BIRTH)).open.size, 0);
  assert.equal((await accessFor(db, { id: uid }, { nonsense: 1 })).open.size, 0);
  assert.equal(await accessFor(db, null, BIRTH), GUEST);
  const t = await buyPlan(db, uid, FP, "tron_bo");
  assert.ok(t.ok && t.charged === planById("tron_bo")!.coins - planById("van_nam")!.coins);
  a = await accessFor(db, { id: uid }, BIRTH);
  out = gateOutput(clone(FULL), a);
  for (const c of FULL.chapters) if (!MEMBER_FREE.includes(c.chapter) && c.chapter !== "bat_tu") assert.deepEqual(got(c.chapter), { ...full(c.chapter), unlocked: true }, c.chapter);
});

test("Bát Tự: each tab cut on its own (never collapsed into one), Đọc sâu held back per tab, opened with the bat_tu chapter", () => {
  const f = corpus[0].facts ?? corpus[0];
  const bt: any = clone(proseBazi(f, K, seedOf(f), "x", true));
  // the corpus facts predate the Đọc sâu layer: mark the last paragraph of each longer tab as one, as prose/bazi_deep.ts does
  for (const ps of Object.values(bt.chapters) as any[][]) if (ps.length >= 3) Object.assign(ps[ps.length - 1], { depth: "sau", depthTitle: "Cơ chế" });
  const tabs = Object.keys(bt.chapters);
  assert.ok(tabs.length >= 5);
  const g = gateOutput(clone(bt), GUEST);
  assert.deepEqual(Object.keys(g.chapters), tabs, "every tab is sent, each with its own first half");
  for (const t of tabs) {
    const main = mainOf(bt.chapters[t]);
    assert.deepEqual(g.chapters[t], main.slice(0, guestShown(main.length)), t);
    const held = heldBack(bt.chapters[t], g.chapters[t]);
    if (held.length) assert.deepEqual([g.locks[t].tier, g.locks[t].chapter, g.locks[t].shown, g.locks[t].total], ["guest", `bat_tu:${t}`, guestShown(main.length), main.length]);
    else assert.equal(g.locks[t], undefined, t);
  }
  const json = JSON.stringify(g);
  for (const t of tabs) assertAbsent(json, heldBack(bt.chapters[t], g.chapters[t]), t, g.paragraphs);
  assertAbsent(json, heldBack(bt.paragraphs, g.paragraphs), "flat", g.paragraphs);
  assert.deepEqual(g.paragraphs, tabs.flatMap(t => g.chapters[t]), "the flat reading is what the tabs kept");
  // member: the first half of each tab, as a guest, with the packages; Vận năm's two tabs open alone; buyer of bat_tu: whole
  const m = gateOutput(clone(bt), member());
  for (const t of tabs) assert.deepEqual(m.chapters[t], mainOf(bt.chapters[t]).slice(0, guestShown(mainOf(bt.chapters[t]).length)), t);
  for (const [t, l] of Object.entries(m.locks) as [string, any][]) {
    assert.equal(l.tier, "member");
    assert.deepEqual(l.plans.map((p: any) => p.id), t === "dai-van" || t === "luu-nien" ? ["van_nam", "tron_bo", "cao_cap"] : ["tron_bo", "cao_cap"], t);
  }
  assertAbsent(JSON.stringify(m), Object.values(bt.chapters).flat().filter(isDeep), "member");
  const vn = gateOutput(clone(bt), member("bat_tu:dai-van", "bat_tu:luu-nien"));
  for (const t of tabs) assert.deepEqual(vn.chapters[t], t === "dai-van" || t === "luu-nien" ? bt.chapters[t] : mainOf(bt.chapters[t]).slice(0, guestShown(mainOf(bt.chapters[t]).length)), t);
  assert.deepEqual(vn.unlockedTabs, tabs.filter(t => t === "dai-van" || t === "luu-nien"));
  assert.deepEqual(gateOutput(clone(bt), member("bat_tu")), { ...bt, unlocked: true });
});

test("/api/overview, /api/synthesis, /api/interpretation: a guest gets the first half or nothing; a member the free chapters; a full buyer the whole", async () => {
  const ov: any = clone(overview(ex, K));
  assert.ok(ov.theses.length >= 2);
  const g = gateOverview(clone(ov), GUEST), k = guestShown(ov.theses.length);
  assert.deepEqual(g.theses, ov.theses.slice(0, k)); assert.deepEqual(g.indices, ov.indices); assert.deepEqual(g.frame, ov.frame);
  assert.deepEqual([g.locked.tier, g.locked.shown, g.locked.total], ["guest", k, ov.theses.length]);
  for (const t of ov.theses.slice(k)) assert.ok(!JSON.stringify(g).includes(JSON.stringify(t)));
  assert.deepEqual(gateOverview(clone(ov), member()), ov);
  // the engine's synthesis layer: chapters of paragraphs, and the Semantic IR at level 5
  const syn = { engine: "s", note: "n", coverage: {}, semantic_ir: { secret: "whole reading" },
    chapters: [{ id: "tong_quan", title: "T", paragraphs: [{ text: "S0" }, { text: "S1" }, { text: "S2" }, { text: "S3" }] }, { id: "menh", title: "M", paragraphs: [{ text: "M0" }] },
      { id: "tai_bach", title: "TB", paragraphs: [{ text: "B0" }, { text: "B1" }, { text: "B2" }] }] };
  const gs = gateSynthesis(clone(syn), GUEST);
  assert.equal(gs.semantic_ir, undefined); assert.deepEqual(gs.chapters[0].paragraphs.map((p: any) => p.text), ["S0", "S1"]);
  assert.deepEqual(gs.chapters[1], syn.chapters[1]); assert.ok(!/S2|S3|B2|whole reading/.test(JSON.stringify(gs)));
  const ms = gateSynthesis(clone(syn), member());
  assert.deepEqual(ms.chapters.slice(0, 2), syn.chapters.slice(0, 2)); assert.deepEqual(ms.chapters[2].paragraphs.map((p: any) => p.text), ["B0", "B1"]);
  assert.deepEqual(ms.chapters[2].locked.plans.map((p: any) => p.id), ["tron_bo", "cao_cap"]); assert.equal(ms.semantic_ir, undefined);
  const all = member("menh", "cong_danh", "tai_bach", "thien_di", "phu_the", "phuc_duc", "dien_trach", "no_boc", "tu_tuc", "huynh_de", "phu_mau", "tat_ach", "van_han", "bat_tu", "tong_luan");
  assert.deepEqual(gateSynthesis(clone(syn), all), syn);
  // through the route: the evidence engine is for members only; with the paywall off nothing is touched
  const engine = (body: unknown) => async () => new Response(JSON.stringify(body), { headers: { "content-type": "application/json", "cache-control": "public, max-age=60" } });
  const req = (cookie?: string) => new Request("https://tu-vi.test/api/interpretation", { method: "POST", headers: cookie ? { cookie } : {}, body: JSON.stringify(BIRTH) });
  const ev = { report: { chapters: [{ id: "menh", sections: { nhan_dinh_tong_quan: "EVIDENCE TEXT" } }] } };
  const r1 = await gated(req(), { db, paywall: true, path: "/api/interpretation", shared: false }, engine(ev));
  assert.equal(r1.status, 401); assert.ok(!(await r1.text()).includes("EVIDENCE")); assert.equal(r1.headers.get("cache-control"), "private, no-store");
  const r2 = await gated(req(await cookieFor(uid)), { db, paywall: true, path: "/api/interpretation", shared: false }, engine(ev));
  assert.equal(r2.status, 402); assert.ok(!(await r2.text()).includes("EVIDENCE"));
  await grant(db, uid, 500, "t", 1); await buyPlan(db, uid, FP, "tron_bo");
  const r2b = await gated(req(await cookieFor(uid)), { db, paywall: true, path: "/api/interpretation", shared: false }, engine(ev));
  assert.equal(r2b.status, 200); assert.deepEqual(await r2b.json(), ev); assert.equal(r2b.headers.get("cache-control"), "private, no-store");
  const r3 = await gated(req(), { db, paywall: false, path: "/api/interpretation", shared: false }, engine(ev));
  assert.equal(r3.headers.get("cache-control"), "public, max-age=60");
  // an engine error passes through untouched
  const bad = new Response("{}", { status: 502 });
  assert.equal(await gateResponse(bad, GUEST), bad);
});

test("share link: the viewer reads at the guest tier, labelled, signed in or not, birth hidden or not", async () => {
  const fp = FP;
  await db.prepare("INSERT INTO charts (user_id, fp, id, label, rel, req_json, updated_at) VALUES (?, ?, ?, ?, ?, ?, 1)").bind(uid, fp, `${uid}c`, "A", "self", JSON.stringify(BIRTH)).run();
  await grant(db, uid, 500, "t", 1); await buyPlan(db, uid, fp, "tron_bo");            // the owner bought everything: the viewer still reads as a guest
  const viewerCookie = await cookieFor(uid);
  for (const hide of [0, 1]) {
    const id = `share${hide}${uid}`.padEnd(22, "x").slice(0, 22);
    await db.prepare("INSERT INTO shares (id, user_id, chart_fp, hide_birth, created_at) VALUES (?, ?, ?, ?, 1)").bind(id, uid, fp, hide).run();
    // the forward src/index.ts builds: a fresh request (no cookie) run through the gate with shared = true
    const forward = (path: string, body: Record<string, unknown>) => gated(new Request(`https://tu-vi.test${path}`, { method: "POST", body: JSON.stringify(body) }),
      { db, paywall: true, path, shared: true }, async () => new Response(JSON.stringify(FULL)));
    const res = await handleShare(new Request(`https://tu-vi.test/api/share/${id}/interpret`, { method: "POST", headers: { cookie: viewerCookie }, body: JSON.stringify({ chapter: "all", mode: "prose" }) }), db, forward);
    assert.equal(res.status, 200); assert.equal(res.headers.get("cache-control"), "private, no-store");
    const out = await res.json() as any;
    const cd = out.chapters.find((c: any) => c.chapter === "cong_danh");
    assert.equal(cd.paragraphs.length, guestShown(mainOf(full("cong_danh").paragraphs).length), `hide=${hide}`);
    assert.equal(cd.locked.tier, "guest"); assert.equal(cd.locked.shared, true);
    assertAbsent(JSON.stringify(out), heldBack(full("cong_danh").paragraphs, cd.paragraphs), `share hide=${hide}`, out.chapters.flatMap((c: any) => c.paragraphs));
  }
  // the same signed-in reader outside the share link is a member
  const own = await gated(new Request("https://tu-vi.test/api/interpret", { method: "POST", headers: { cookie: viewerCookie }, body: JSON.stringify({ ...BIRTH, chapter: "all", mode: "prose" }) }),
    { db, paywall: true, path: "/api/interpret", shared: false }, async () => new Response(JSON.stringify(FULL)));
  assert.deepEqual((await own.json() as any).chapters.find((c: any) => c.chapter === "cong_danh"), { ...full("cong_danh"), unlocked: true });
  assert.equal(SHARED.tier, "guest"); assert.equal(SHARED.shared, true);
});

test("cache: one full copy per chart, never keyed by the reader; every tier is cut from it after the cache", async () => {
  const store = new Map<string, string>();
  const cache: OutputCache = { get: async k => store.get(k) ?? null, put: async (k, _c, body) => { store.set(k, body); } };
  const deferred: Promise<unknown>[] = [];
  const run = (r: Request) => handleInterpret(r, { enabled: true, proseDraft: true, luan: true, facts: async () => new Response(JSON.stringify(ex)),
    store: new BundledStore(K), cache, defer: p => { deferred.push(p); } });
  const ask = async (cookie?: string) => {
    const r = await gated(new Request("https://tu-vi.test/api/interpret", { method: "POST", headers: cookie ? { cookie } : {}, body: JSON.stringify({ ...BIRTH, chapter: "all", mode: "prose" }) }),
      { db, paywall: true, path: "/api/interpret", shared: false }, run);
    await Promise.all(deferred);
    return { hit: r.headers.get("x-interpret-cache"), cc: r.headers.get("cache-control"), out: await r.json() as any };
  };
  const cookie = await cookieFor(uid);
  const g1 = await ask(), m1 = await ask(cookie), g2 = await ask();
  await grant(db, uid, 500, "t", 1); await buyPlan(db, uid, FP, "tron_bo");
  const b1 = await ask(cookie);
  assert.deepEqual([g1.hit, m1.hit, g2.hit, b1.hit], ["miss", "hit", "hit", "hit"]);
  assert.equal(store.size, 1, "one entry, whoever asked");
  assert.ok([g1, m1, g2, b1].every(x => x.cc === "private, no-store"));
  const cached = JSON.parse([...store.values()][0]);
  const cdFull = cached.chapters.find((c: any) => c.chapter === "cong_danh");
  assert.ok(deepOf(cdFull.paragraphs).length > 0, "the cache holds the Đọc sâu part");
  assert.ok(!cdFull.locked && !cdFull.unlocked, "nothing reader-specific is cached");
  const cd = (x: any) => x.out.chapters.find((c: any) => c.chapter === "cong_danh");
  assert.deepEqual(g1.out, g2.out, "a guest after a member gets the guest cut");
  assert.equal(cd(g1).paragraphs.length, guestShown(mainOf(cdFull.paragraphs).length));
  assert.deepEqual(cd(m1).paragraphs, mainOf(cdFull.paragraphs).slice(0, guestShown(mainOf(cdFull.paragraphs).length)));
  assert.deepEqual(cd(b1).paragraphs, cdFull.paragraphs);
});
