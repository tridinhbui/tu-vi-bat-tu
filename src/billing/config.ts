// Prices, packages and allowances in one place; change them here, nowhere else. The pricing page (/bang-gia) reads this file through
// GET /api/plans, the paywall and every payment callback check against it, so the page can never show a price the server does not charge.
//
// GIÁ TẠM — chủ site đặt. Every coin cost and every VND amount below is a PLACEHOLDER picked only so the flow can be tested. The site owner
// sets the real prices (and decides VAT) before PRICES_ARE_PLACEHOLDERS is turned false; while it is true the pricing page says so.
export const PRICES_ARE_PLACEHOLDERS = true;
export const PLACEHOLDER_LABEL = "GIÁ TẠM — chủ site đặt";

/** Free chat messages a member gets each day (Vietnam time). Owner decision 2026-10-23, replacing 10 a month. */
export const FREE_MESSAGES_PER_DAY = 2;
/** Every top-up (a paid coin pack, Stripe or VNPAY, or a gift code) opens a chat pass: free chat for `days` days from the later of now and
 *  the end of the current pass, at most `perDay` messages a day. Past the cap a message costs coins like any other. */
export const TOPUP_CHAT = { days: 30, perDay: 30 } as const;

/** Coins one use costs. A use listed in FREE_USES draws from the daily free allowance first. */
export const COSTS = { chat: 1, deep: 20 } as const;
export const FREE_USES: readonly Usage[] = ["chat"];

export type Usage = keyof typeof COSTS;
export const isUsage = (u: unknown): u is Usage => typeof u === "string" && u in COSTS;

const VN_OFFSET_MS = 7 * 3600 * 1000;
/** The month a ledger row is filed under, YYYY-MM in Vietnam time. */
export const periodOf = (now: number) => new Date(now + VN_OFFSET_MS).toISOString().slice(0, 7);
/** The day the free chat counter belongs to, YYYY-MM-DD in Vietnam time: the allowance resets at midnight in Vietnam. */
export const dayOf = (now: number) => new Date(now + VN_OFFSET_MS).toISOString().slice(0, 10);
export function nextResetAt(now: number): number {
  const d = new Date(now + VN_OFFSET_MS);
  return Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() + 1) - VN_OFFSET_MS;
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

// ---------- the report: three tiers (owner decision 2026-10-23) ----------
// Chapter ids are those of the reader prose served by /api/interpret mode "prose" (src/interpret/prose): the overview (tong_quan), the twelve
// palaces, the đại hạn and lưu niên chapter (van_han) and the Bát Tự reading (bat_tu, filtered per tab). Every chapter's reading has a main
// part and, for some chapters, a "Đọc sâu (theo sách)" part: Tử Vi paragraphs marked `deep` (prose/luan_deep.ts), Bát Tự paragraphs with
// depth 'sau' (prose/bazi_deep.ts).
//   guest  (not signed in, and everyone who opens a share link): the first third of each chapter's main part, never the Đọc sâu part;
//   member (signed in, free): the whole main part of every chapter; the Đọc sâu part of a chapter once it is opened with xu (`unlocks`).
// The chart board, the fortune charts, the book findings list and the year explorer are not chapters and stay open to everyone.
export type Tier = "guest" | "member";
/** How many main paragraphs a guest reads out of n: the first third, rounded up, at least one (none of none). */
export const guestShown = (n: number) => n > 0 ? Math.max(1, Math.ceil(n / 3)) : 0;

export const PALACE_CHAPTERS = ["menh", "cong_danh", "tai_bach", "thien_di", "phu_the", "phuc_duc", "dien_trach", "no_boc", "tu_tuc", "huynh_de", "phu_mau", "tat_ach"] as const;
/** The chapters whose Đọc sâu part is sold. A chapter without Đọc sâu paragraphs for a chart shows no lock for it. */
export const DEEP_CHAPTERS = [...PALACE_CHAPTERS, "van_han", "bat_tu"] as const;
export type DeepChapter = (typeof DEEP_CHAPTERS)[number];
export const isDeepChapter = (c: unknown): c is DeepChapter => typeof c === "string" && (DEEP_CHAPTERS as readonly string[]).includes(c);

export const CHAPTER_TITLES: Record<string, string> = {
  tong_quan: "Tổng quan Tử Vi", menh: "Cung Mệnh", cong_danh: "Cung Quan Lộc", tai_bach: "Cung Tài Bạch", thien_di: "Cung Thiên Di", phu_the: "Cung Phu Thê",
  phuc_duc: "Cung Phúc Đức", dien_trach: "Cung Điền Trạch", no_boc: "Cung Nô Bộc", tu_tuc: "Cung Tử Tức", huynh_de: "Cung Huynh Đệ",
  phu_mau: "Cung Phụ Mẫu", tat_ach: "Cung Tật Ách", van_han: "Đại hạn, tiểu hạn và lưu niên", bat_tu: "Luận giải Bát Tự",
};
/** The Bát Tự tabs (prose/bazi.ts `chapters`), for the lock card of each. */
export const BAZI_TAB_TITLES: Record<string, string> = {
  "nhat-chu": "Nhật Chủ & tính cách", "ngu-hanh": "Ngũ Hành & Thập Thần", "su-nghiep": "Sự nghiệp & Tài lộc", "quan-he": "Quan hệ Can Chi & hôn nhân",
  "dai-van": "Đại vận", "cach-cuc": "Cách cục & Dụng thần", "luu-nien": "Lưu niên", "tong-ket": "Tổng kết theo trục thời gian",
};

/** Packages bought with coins, for ONE chart; each opens the Đọc sâu part of its chapters. `chapters: "one"` opens the chapter the reader
 *  picked. GIÁ TẠM. */
export const PLANS = [
  { id: "chuong", name: "Đọc sâu một chương", coins: 15, chapters: "one", blurb: "Mở phần Đọc sâu (theo sách) của một chương bất kỳ cho lá số đang xem." },
  { id: "cung12", name: "Đọc sâu mười hai cung", coins: 60, chapters: PALACE_CHAPTERS, blurb: "Phần Đọc sâu (theo sách) của cả mười hai cung Tử Vi, những cung có phần này với lá số của bạn." },
  { id: "tron_bo", name: "Đọc sâu trọn bộ", coins: 90, chapters: DEEP_CHAPTERS, blurb: "Phần Đọc sâu (theo sách) của mọi chương: mười hai cung, đại hạn và Bát Tự." },
] as const;
export type Plan = (typeof PLANS)[number];
/** Plans sold before 2026-10-23: no longer offered, named in the wallet history. */
export const RETIRED_PLAN_NAMES: Record<string, string> = { van_han: "Vận hạn (gói cũ)" };
export const planById = (id: unknown): Plan | undefined => PLANS.find(p => p.id === id);
/** The chapters a plan opens; for "chuong" the one asked for (null when it has no Đọc sâu part to sell). */
export function planChapters(plan: Plan, chapter?: unknown): DeepChapter[] | null {
  if (plan.chapters === "one") return isDeepChapter(chapter) ? [chapter] : null;
  return [...plan.chapters];
}
/** Plans that would open this chapter, cheapest first: what the lock card offers. */
export const plansFor = (chapter: DeepChapter) => PLANS.filter(p => p.chapters === "one" || (p.chapters as readonly string[]).includes(chapter)).sort((a, b) => a.coins - b.coins);

// ---------- discount codes ----------
export const MAX_DISCOUNT_PCT = 90;
/** The VND amount after a discount, rounded to the nearest 1.000đ and never below MIN_AMOUNT (both gateways have a floor). */
export const MIN_AMOUNT = 10000;
export const discounted = (amount: number, pct: number) => pct > 0 ? Math.min(amount, Math.max(MIN_AMOUNT, Math.round(amount * (100 - pct) / 100 / 1000) * 1000)) : amount;
