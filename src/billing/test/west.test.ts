// The Western reading tiers (owner decision 2026-10-25, src/billing/west.ts) on a reading shaped like engine/western/reading's: a guest gets
// the first 3/5 of each chapter's main part; a member every natal chapter's main part and Đọc sâu of the four chart chapters; the Chiêm tinh
// package opens the rest; the fingerprint keeps the place; a Western package is never sold for a Tử Vi birth, nor the other way round.
import { test } from "node:test";
import assert from "node:assert/strict";
import { gateWest, westFp } from "../west.ts";
import { GUEST, type Access } from "../paywall.ts";
import { PLANS, WEST_DEEP_FREE, WEST_MAIN_FREE, WEST_PAID, guestShown, isWestPlan, planById } from "../config.ts";
import { safeNext } from "../../auth/route.ts";

const IDS = ["tong_quan", "hanh_tinh", "goc_hop", "tinh_cach", "tu_duy", "cam_xuc", "su_nghiep", "tai_chinh", "quan_he", "gia_dinh", "dinh_huong", "tong_hop", "thoi_van"];
const para = (ch: string, i: number, level: string) => ({ id: `${ch}.${i}`, heading: "", text: `${ch} ${level} ${i}`, school: "traditional", sources: [], evidence: [], level, tier: "src", steps: [] });
const READING = {
  version: "w", mode: "deep", audit: { ok: true, issues: [] }, disclaimer: "d", operational: {},
  chapters: IDS.map(id => ({ id, title: id, paragraphs: [para(id, 1, "overview"), para(id, 2, "deep"), para(id, 3, "overview"), para(id, 4, "overview"), para(id, 5, "deep")] })),
};
const MEMBER: Access = { tier: "member", open: new Set(), credit: 0 };
const main = (ps: any[]) => ps.filter(p => p.level !== "deep"), deep = (ps: any[]) => ps.filter(p => p.level === "deep");

test("every chapter of the reading has a tier, and the package opens exactly the paid ones", () => {
  for (const id of IDS) assert.ok(WEST_MAIN_FREE.includes(id) || WEST_PAID.includes(id), id);
  for (const id of WEST_DEEP_FREE) assert.ok(WEST_MAIN_FREE.includes(id) && !WEST_PAID.includes(id), id);
  const p = planById("chiem_tinh")!;
  assert.ok(isWestPlan(p));
  assert.deepEqual([...p.chapters], WEST_PAID.map(c => `west:${c}`));
  assert.deepEqual(PLANS.filter(isWestPlan).map(x => x.id), ["chiem_tinh"]);
});

test("a guest reads the first 3/5 of each chapter's main part, never Đọc sâu", () => {
  const out = gateWest(structuredClone(READING), GUEST);
  for (const [i, c] of out.chapters.entries()) {
    const full = READING.chapters[i].paragraphs, k = guestShown(main(full).length);
    assert.deepEqual(c.paragraphs, main(full).slice(0, k), c.id);
    assert.deepEqual([c.locked.tier, c.locked.shown, c.locked.total, c.locked.deep, c.locked.chapter], ["guest", k, 3, 2, `west:${c.id}`]);
    assert.equal(c.locked.plans, undefined);
    assert.equal(c.locked.next, "/chiem-tinh/");
  }
  assert.deepEqual(out.audit, READING.audit);
});

test("a member reads the natal main parts whole and Đọc sâu of the chart chapters; the package is offered for the rest", () => {
  const out = gateWest(structuredClone(READING), MEMBER);
  for (const [i, c] of out.chapters.entries()) {
    const full = READING.chapters[i].paragraphs;
    if (WEST_DEEP_FREE.includes(c.id)) { assert.deepEqual(c, READING.chapters[i], c.id); continue; }
    const wantMain = WEST_MAIN_FREE.includes(c.id) ? main(full) : main(full).slice(0, guestShown(3));
    assert.deepEqual(c.paragraphs, wantMain, c.id);
    assert.equal(c.locked.deep, deep(full).length);
    assert.deepEqual(c.locked.plans.map((p: any) => p.id), ["chiem_tinh"], c.id);
  }
});

test("the Chiêm tinh package opens its chapters whole", () => {
  const a: Access = { tier: "member", open: new Set(WEST_PAID.map(c => `west:${c}`)), credit: 0 };
  const out = gateWest(structuredClone(READING), a);
  for (const [i, c] of out.chapters.entries()) {
    assert.deepEqual(c.paragraphs, READING.chapters[i].paragraphs, c.id);
    assert.equal(c.locked, undefined, c.id);
  }
});

test("Tử Vi unlocks open nothing of the Western reading", () => {
  const a: Access = { tier: "member", open: new Set(["su_nghiep", "tong_hop", "van_han", "ai"]), credit: 0 };
  const out = gateWest(structuredClone(READING), a);
  assert.ok(out.chapters.find((c: any) => c.id === "thoi_van").locked);
});

test("the Western fingerprint keeps date, time and place, and ignores the name", () => {
  const b = { year: 1990, month: 5, day: 17, hour: 10, minute: 30, lat: 10.8231, lon: 106.6297, tz: "Asia/Ho_Chi_Minh", name: "A", place: "HCM" };
  assert.equal(westFp(b), "w:1990:5:17:10:30:10.823:106.630:Asia/Ho_Chi_Minh");
  assert.equal(westFp({ ...b, name: "B" }), westFp(b));
  assert.notEqual(westFp({ ...b, lat: 21.03 }), westFp(b));
  assert.equal(westFp({ ...b, hour: null, minute: null }), "w:1990:5:17:x:x:10.823:106.630:Asia/Ho_Chi_Minh");
  assert.equal(westFp({ year: 1990, month: 5, day: 17, hour: 10, minute: 30, gender: "male" }), null);
  assert.equal(westFp(null), null);
});

test("sign-in comes back only to one of the site's own pages", () => {
  assert.equal(safeNext("/chiem-tinh/"), "/chiem-tinh/");
  for (const bad of ["//evil.example", "https://evil.example/", "/a/../b", "/x?y=1", "", null, "/chiem-tinh/#x"]) assert.equal(safeNext(bad), "/", String(bad));
});
