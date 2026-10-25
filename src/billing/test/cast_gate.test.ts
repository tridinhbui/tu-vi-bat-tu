// Kinh Dịch / Mai Hoa readings: Đọc sâu only for a member holding a paid package (owner decision 2026-10-25).
import { test } from "node:test";
import assert from "node:assert/strict";
import { CAST_PATHS, FILTERS, GUEST, gateCast, type Access } from "../paywall.ts";

const reading = () => ({
  cast: { ban: { number: 7 } },
  reading: { sections: [
    { id: "tinh_the", paragraphs: [{ depth: "nhanh", sentences: [{ text: "a." }] }] },
    { id: "cau_truc", paragraphs: [{ depth: "sau", sentences: [{ text: "b." }] }] },
    { id: "mixed", paragraphs: [{ depth: "nhanh", sentences: [{ text: "c." }] }, { depth: "sau", sentences: [{ text: "d." }] }] },
  ] },
});
const member = (paid: boolean): Access => ({ tier: "member", open: new Set(), paid });

test("both reading paths are gated by gateCast", () => {
  for (const p of CAST_PATHS) assert.equal(FILTERS[p], gateCast);
});

test("a guest and an unpaid member keep the main reading and lose Đọc sâu", () => {
  for (const [a, need] of [[GUEST, "sign_in"], [member(false), "package"]] as const) {
    const out = gateCast(reading(), a);
    assert.deepEqual(out.reading.sections.map((s: any) => s.id), ["tinh_the", "mixed"]);
    assert.equal(out.reading.sections[1].paragraphs.length, 1);
    assert.deepEqual(out.reading.locked, { tier: a.tier, deep: 2, need });
  }
});

test("a member holding a paid package gets everything", () => {
  const r = reading();
  assert.deepEqual(gateCast(r, member(true)), r);
});

test("a reading without Đọc sâu is left alone", () => {
  const r = { reading: { sections: [{ id: "x", paragraphs: [{ depth: "nhanh", sentences: [] }] }] } };
  assert.deepEqual(gateCast(r, GUEST), r);
});
