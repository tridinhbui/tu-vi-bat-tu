// The shuffle: same seed ⇒ same draw, every card about equally likely in every place, reversals switch off without moving any card.
import { test } from "node:test";
import assert from "node:assert/strict";
import { DECK, DECK_SIZE, BY_ID, publicCard } from "../deck.ts";
import { newSeed, reveal, shuffle, Stream, validPicks, SEED_RE } from "../draw.ts";

const seedOf = (i: number) => i.toString(16).padStart(32, "0");

test("the deck: 78 cards, 22 Major and 14 of each suit, unique ids and slugs, names only", () => {
  assert.equal(DECK_SIZE, 78);
  assert.equal(DECK.filter(c => c.arcana === "major").length, 22);
  for (const s of ["wands", "cups", "swords", "pentacles"]) assert.equal(DECK.filter(c => c.suit === s).length, 14, s);
  assert.equal(new Set(DECK.map(c => c.id)).size, 78);
  assert.equal(new Set(DECK.map(c => c.slug)).size, 78);
  assert.ok(DECK.every(c => /^[a-z0-9-]+$/.test(c.slug) && c.name_en && c.name_vi));
  assert.equal(BY_ID.get("M08")!.name_en, "Strength");          // the 1909 deck: Strength VIII, Justice XI
  assert.equal(BY_ID.get("M11")!.name_en, "Justice");
  assert.equal(publicCard(BY_ID.get("M08")!).numeral, "VIII");
  assert.deepEqual(Object.keys(DECK[0]).sort(), ["arcana", "id", "name_en", "name_vi", "number", "slug", "suit"]);
});

test("a new seed is 128 bits from the system's random source", () => {
  const a = newSeed(), b = newSeed();
  assert.match(a, SEED_RE); assert.notEqual(a, b);
  assert.throws(() => new Stream("xyz"));
});

test("same seed, same order and same reversals; another seed, another order", async () => {
  const s = "0123456789abcdef0123456789abcdef";
  const a = await shuffle(s), b = await shuffle(s);
  assert.deepEqual(a, b);
  assert.deepEqual([...a.order].sort((x, y) => x - y), Array.from({ length: 78 }, (_, i) => i));   // a permutation
  assert.notDeepEqual((await shuffle(seedOf(1))).order, a.order);
  const r1 = await reveal(s, true, [5, 40, 77]), r2 = await reveal(s, true, [5, 40, 77]);
  assert.deepEqual(r1, r2);
  assert.deepEqual(r1.map(d => d.slot), [1, 2, 3]);
  assert.equal(r1[1].card, DECK[a.order[40]]);
});

test("switching reversals off keeps every card in place and turns them all upright", async () => {
  let anyReversed = 0;
  for (let i = 0; i < 20; i++) {
    const on = await shuffle(seedOf(i), true), off = await shuffle(seedOf(i), false);
    assert.deepEqual(on.order, off.order);
    assert.ok(off.reversed.every(r => r === false));
    anyReversed += on.reversed.filter(Boolean).length;
  }
  assert.ok(anyReversed > 20 * 78 * 0.4 && anyReversed < 20 * 78 * 0.6, `reversed share ${anyReversed / (20 * 78)}`);
});

test("roughly uniform: each card lands in the first place about 1/78 of the time", async () => {
  const N = 78 * 40, counts = new Array(78).fill(0), last = new Array(78).fill(0);
  for (let i = 0; i < N; i++) {
    const { order } = await shuffle(seedOf(1000 + i), false);
    counts[order[0]]++; last[order[77]]++;
  }
  const chi = (c: number[]) => c.reduce((s, x) => s + (x - 40) ** 2 / 40, 0);
  // 77 degrees of freedom: the 99.9th percentile is about 122
  assert.ok(chi(counts) < 122, `chi-square first place ${chi(counts)}`);
  assert.ok(chi(last) < 122, `chi-square last place ${chi(last)}`);
  assert.ok(Math.min(...counts) > 12 && Math.max(...counts) < 80, String(counts));
});

test("the stream is SHA-256(seed ‖ counter, 4 bytes big-endian), read as big-endian 32-bit words", async () => {
  const { createHash } = await import("node:crypto");
  const seed = "00112233445566778899aabbccddeeff", s = new Stream(seed);
  const want: number[] = [];
  for (let k = 0; k < 10; k++) {
    const h = createHash("sha256").update(Buffer.concat([Buffer.from(seed, "hex"), Buffer.from([0, 0, 0, k])])).digest();
    for (let w = 0; w < 8; w++) want.push(h.readUInt32BE(4 * w));
  }
  const got: number[] = [];
  for (let i = 0; i < 80; i++) got.push(await s.next());
  assert.deepEqual(got, want);
});

test("rejection sampling stays in range", async () => {
  const s = new Stream(seedOf(7));
  for (const n of [1, 2, 3, 77, 78]) for (let k = 0; k < 50; k++) { const v = await s.below(n); assert.ok(v >= 0 && v < n); }
});

test("picks: as many distinct fan positions as the spread holds", () => {
  assert.ok(validPicks([0], 1) && validPicks([0, 77, 12], 3));
  for (const bad of [[], [1, 2], [78], [-1], [1.5], ["1"], [3, 3, 4], null, "0"]) {
    assert.equal(validPicks(bad, 1) || validPicks(bad, 3), false, JSON.stringify(bad));
  }
});
