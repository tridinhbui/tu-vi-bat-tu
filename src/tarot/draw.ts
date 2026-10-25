// The shuffle. A draw is a 128-bit seed from crypto.getRandomValues; the deck order and the reversal bits follow from it alone, through a
// SHA-256 counter stream (block k = SHA-256(seed ‖ k as 4 bytes, big-endian)) feeding a Fisher–Yates shuffle with rejection sampling, so
// every order is equally likely and the same seed always gives the same draw. The order never leaves the server: the page shows a
// face-down fan and sends back only the positions it picked (route.ts).
import { DECK, DECK_SIZE, type Card } from "./deck.ts";

export const SPREADS = { 1: { cards: 1 }, 3: { cards: 3 } } as const;   // the three positions are a layout only: no meaning is given to them
export type SpreadSize = keyof typeof SPREADS;
export const isSpread = (n: unknown): n is SpreadSize => n === 1 || n === 3;

const hex = (b: Uint8Array) => [...b].map(x => x.toString(16).padStart(2, "0")).join("");
export const newSeed = () => hex(crypto.getRandomValues(new Uint8Array(16)));
export const SEED_RE = /^[0-9a-f]{32}$/;
const BATCH = 8;                               // 8 blocks = 64 values; a shuffle with its reversal bits needs about 160

/** Unsigned 32-bit integers from SHA-256(seed ‖ counter). */
export class Stream {
  private buf = new Uint32Array(0);
  private i = 0;
  private counter = 0;
  private readonly seed: Uint8Array;
  constructor(seedHex: string) {
    if (!SEED_RE.test(seedHex)) throw new Error("seed must be 32 hex characters");
    this.seed = new Uint8Array(seedHex.match(/../g)!.map(h => parseInt(h, 16)));
  }
  async next(): Promise<number> {
    if (this.i >= this.buf.length) {
      // BATCH consecutive blocks hashed at once: the same values in the same order as one block at a time, with fewer awaits
      const digests = await Promise.all(Array.from({ length: BATCH }, () => {
        const block = new Uint8Array(this.seed.length + 4);
        block.set(this.seed);
        new DataView(block.buffer).setUint32(this.seed.length, this.counter++, false);
        return crypto.subtle.digest("SHA-256", block);
      }));
      this.buf = new Uint32Array(8 * BATCH);
      digests.forEach((d, b) => { const v = new DataView(d); for (let k = 0; k < 8; k++) this.buf[8 * b + k] = v.getUint32(4 * k, false); });
      this.i = 0;
    }
    return this.buf[this.i++];
  }
  /** Uniform integer in [0, n): values from the top, incomplete range of 2^32 are drawn again. */
  async below(n: number): Promise<number> {
    const limit = Math.floor(0x1_0000_0000 / n) * n;
    for (;;) { const u = await this.next(); if (u < limit) return u % n; }
  }
}

export interface Shuffle { order: number[]; reversed: boolean[] }

/** The deck order (indices into DECK) and one reversal bit per position. The bits are drawn after the order, so switching reversals
 *  off changes nothing else: the same seed gives the same cards in the same places, all upright. */
export async function shuffle(seedHex: string, reversals = true): Promise<Shuffle> {
  const s = new Stream(seedHex);
  const order = Array.from({ length: DECK_SIZE }, (_, i) => i);
  for (let i = DECK_SIZE - 1; i > 0; i--) {
    const j = await s.below(i + 1);
    [order[i], order[j]] = [order[j], order[i]];
  }
  const reversed: boolean[] = [];
  for (let k = 0; k < DECK_SIZE; k++) reversed.push(((await s.next()) & 1) === 1 && reversals);
  return { order, reversed };
}

/** Positions picked from the fan: distinct whole numbers in [0, 78), as many as the spread holds. */
export function validPicks(picks: unknown, spread: SpreadSize): picks is number[] {
  return Array.isArray(picks) && picks.length === SPREADS[spread].cards && new Set(picks).size === picks.length &&
    picks.every(p => Number.isInteger(p) && p >= 0 && p < DECK_SIZE);
}

export interface Drawn { slot: number; pick: number; card: Card; reversed: boolean }

/** The cards under the picked positions, in the order they were picked (slot 1, 2, 3). */
export async function reveal(seedHex: string, reversals: boolean, picks: number[]): Promise<Drawn[]> {
  const { order, reversed } = await shuffle(seedHex, reversals);
  return picks.map((p, i) => ({ slot: i + 1, pick: p, card: DECK[order[p]], reversed: reversed[p] }));
}
