// Prices, packages and allowances in one place; change them here, nowhere else. The pricing page (/bang-gia) reads this file through
// GET /api/plans, the paywall and every payment callback check against it, so the page can never show a price the server does not charge.
//
// GIÁ TẠM — chủ site đặt. Every coin cost and every VND amount below is a PLACEHOLDER picked only so the flow can be tested. The site owner
// sets the real prices (and decides VAT) before PRICES_ARE_PLACEHOLDERS is turned false; while it is true the pricing page says so.
export const PRICES_ARE_PLACEHOLDERS = true;
export const PLACEHOLDER_LABEL = "GIÁ TẠM — chủ site đặt";

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

/** Coin packs sold for money (Stripe Checkout, VNPAY). `amount` is in VND, a zero-decimal currency, so 49000 means 49.000đ. A payment
 *  callback credits coins from the order made from THIS table and checks the amount paid against it; nothing the browser sends decides
 *  what is credited. GIÁ TẠM. */
export const CURRENCY = "vnd";
export const PACKS = [
  { id: "p50", coins: 50, amount: 49000 },
  { id: "p150", coins: 150, amount: 129000 },
  { id: "p400", coins: 400, amount: 299000 },
] as const;
export type Pack = (typeof PACKS)[number];
export const packById = (id: unknown): Pack | undefined => PACKS.find(p => p.id === id);

// ---------- the report: which chapters are free, which are paid, and the packages that open them ----------
// Chapter ids are those of the reader prose served by /api/interpret mode "prose" (src/interpret/prose): the twelve palaces, the đại hạn
// and lưu niên chapter (van_han) and the Bát Tự reading (bat_tu). The chart board, the overview, the fortune charts, the book findings
// list and the year explorer are not chapters and stay free.
export const FREE_CHAPTERS = ["menh"] as const;
export const PALACE_CHAPTERS = ["cong_danh", "tai_bach", "thien_di", "phu_the", "phuc_duc", "dien_trach", "no_boc", "tu_tuc", "huynh_de", "phu_mau", "tat_ach"] as const;
export const PAID_CHAPTERS = [...PALACE_CHAPTERS, "van_han", "bat_tu"] as const;
export type PaidChapter = (typeof PAID_CHAPTERS)[number];
export const isPaidChapter = (c: unknown): c is PaidChapter => typeof c === "string" && (PAID_CHAPTERS as readonly string[]).includes(c);

/** A locked chapter still shows this many paragraphs (a chapter with fewer shows its first one, cut to PREVIEW_SENTENCES). */
export const PREVIEW_PARAGRAPHS = 2;
export const PREVIEW_SENTENCES = 2;

export const CHAPTER_TITLES: Record<string, string> = {
  menh: "Cung Mệnh", cong_danh: "Cung Quan Lộc", tai_bach: "Cung Tài Bạch", thien_di: "Cung Thiên Di", phu_the: "Cung Phu Thê",
  phuc_duc: "Cung Phúc Đức", dien_trach: "Cung Điền Trạch", no_boc: "Cung Nô Bộc", tu_tuc: "Cung Tử Tức", huynh_de: "Cung Huynh Đệ",
  phu_mau: "Cung Phụ Mẫu", tat_ach: "Cung Tật Ách", van_han: "Đại hạn, tiểu hạn và lưu niên", bat_tu: "Luận giải Bát Tự",
};

/** Packages bought with coins, for ONE chart. `chapters: "one"` opens the single chapter the reader picked. GIÁ TẠM. */
export const PLANS = [
  { id: "chuong", name: "Một chương", coins: 15, chapters: "one", blurb: "Mở trọn một chương bất kỳ cho lá số đang xem." },
  { id: "cung12", name: "Mười hai cung chi tiết", coins: 60, chapters: PALACE_CHAPTERS, blurb: "Mười một cung còn lại (cung Mệnh đã miễn phí), đọc đầy đủ kèm gợi ý hành động." },
  { id: "van_han", name: "Vận hạn", coins: 30, chapters: ["van_han"], blurb: "Từng đại hạn mười năm, tiểu hạn và lưu niên của năm đang xem, kèm lời khuyên theo từng mốc." },
  { id: "tron_bo", name: "Chuyên sâu trọn bộ", coins: 90, chapters: PAID_CHAPTERS, blurb: "Mọi chương trả phí của lá số: mười hai cung, vận hạn và Bát Tự." },
] as const;
export type Plan = (typeof PLANS)[number];
export const planById = (id: unknown): Plan | undefined => PLANS.find(p => p.id === id);
/** The chapters a plan opens; for "chuong" the one asked for (null when it is not a paid chapter). */
export function planChapters(plan: Plan, chapter?: unknown): PaidChapter[] | null {
  if (plan.chapters === "one") return isPaidChapter(chapter) ? [chapter] : null;
  return [...plan.chapters];
}
/** Plans that would open this chapter, cheapest first: what the lock card offers. */
export const plansFor = (chapter: PaidChapter) => PLANS.filter(p => p.chapters === "one" || (p.chapters as readonly string[]).includes(chapter)).sort((a, b) => a.coins - b.coins);

// ---------- discount codes ----------
export const MAX_DISCOUNT_PCT = 90;
/** The VND amount after a discount, rounded to the nearest 1.000đ and never below MIN_AMOUNT (both gateways have a floor). */
export const MIN_AMOUNT = 10000;
export const discounted = (amount: number, pct: number) => pct > 0 ? Math.min(amount, Math.max(MIN_AMOUNT, Math.round(amount * (100 - pct) / 100 / 1000) * 1000)) : amount;
