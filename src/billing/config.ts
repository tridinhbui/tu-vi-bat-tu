// Prices and allowances in one place; change them here, nowhere else.
export const FREE_MESSAGES_PER_MONTH = 10;

/** Coins one use costs. A use listed in FREE_USES draws from the monthly free allowance first. */
export const COSTS = { chat: 1, deep: 20 } as const;
export const FREE_USES: readonly Usage[] = ["chat"];

export type Usage = keyof typeof COSTS;
export const isUsage = (u: unknown): u is Usage => typeof u === "string" && u in COSTS;

const VN_OFFSET_MS = 7 * 3600 * 1000;
/** The free allowance resets on the 1st of each month, Vietnam time. */
export const periodOf = (now: number) => new Date(now + VN_OFFSET_MS).toISOString().slice(0, 7);
export function nextResetAt(now: number): number {
  const d = new Date(now + VN_OFFSET_MS);
  return Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 1) - VN_OFFSET_MS;
}

/** Coin packs sold through Stripe Checkout. `amount` is in VND, a zero-decimal currency, so 49000 means 49.000đ. The webhook credits
 *  coins from THIS table by pack id and checks the amount paid against it; nothing the browser sends decides what is credited. */
export const CURRENCY = "vnd";
export const PACKS = [
  { id: "p50", coins: 50, amount: 49000 },
  { id: "p150", coins: 150, amount: 129000 },
  { id: "p400", coins: 400, amount: 299000 },
] as const;
export type Pack = (typeof PACKS)[number];
export const packById = (id: unknown): Pack | undefined => PACKS.find(p => p.id === id);
