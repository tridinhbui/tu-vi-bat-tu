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
