// The Western astrology reading (POST /api/west/reading, engine/western/reading) cut to the reader's tier. Owner decision 2026-10-25:
// only part of it is paid. A chapter's paragraphs are "main" (level overview) or "Đọc sâu" (level deep).
//   guest  (not signed in): the first half of each chapter's main part, never Đọc sâu;
//   member (signed in, free): every natal chapter's main part whole, and Đọc sâu of the four chapters that describe the chart itself
//          (WEST_DEEP_FREE); Tổng hợp and Thời vận: the first half of the main part;
//   opened (the "Chiêm tinh" package bought for this birth): everything.
// The chart, its tables and wheel, the transit / progression / profection / solar-return data and synastry are not cut.
// A Western birth has a place, so its fingerprint is not the Tử Vi one (westFp); unlocks rows for it are "west:<chapter>".
import { WEST_DEEP_FREE, WEST_MAIN_FREE, WEST_PAID, WEST_TITLES, guestShown, plansFor } from "./config.ts";
import type { Access } from "./paywall.ts";

type Json = Record<string, any>;

/** The fingerprint of a Western birth ({year, month, day, hour?, minute?, lat, lon, tz}), or null when it is not one. */
export function westFp(b: unknown): string | null {
  if (!b || typeof b !== "object") return null;
  const r = b as Record<string, unknown>;
  const ints = ["year", "month", "day"].map(k => r[k]);
  if (!ints.every(Number.isInteger) || typeof r.lat !== "number" || typeof r.lon !== "number" || typeof r.tz !== "string" || !r.tz) return null;
  const hm = ["hour", "minute"].map(k => Number.isInteger(r[k]) ? String(r[k]) : "x");
  return ["w", ...ints, ...hm, (r.lat as number).toFixed(3), (r.lon as number).toFixed(3), r.tz.slice(0, 64)].join(":");
}

/** The birth of a /api/west/* request body ({birth: {...}, ...}). */
export const westBody = (body: unknown) => (body && typeof body === "object" ? (body as Json).birth : null);

const key = (id: string) => `west:${id}`;
const opened = (a: Access, id: string) => a.tier === "member" && a.open.has(key(id));

/** One chapter for this reader: paragraphs cut, and a `locked` card (counts only) when something was held back. */
function gateWestChapter(ch: Json, a: Access): Json {
  const id = String(ch?.id ?? ""), ps: Json[] = Array.isArray(ch?.paragraphs) ? ch.paragraphs : [];
  if (!WEST_PAID.includes(id) && !WEST_MAIN_FREE.includes(id) && !WEST_DEEP_FREE.includes(id)) return ch;   // a chapter added later: open
  if (opened(a, id)) return { ...ch, unlocked: true };
  const main = ps.filter(p => p?.level !== "deep"), deep = ps.filter(p => p?.level === "deep");
  const member = a.tier === "member";
  const mainWhole = member && WEST_MAIN_FREE.includes(id), deepOpen = member && WEST_DEEP_FREE.includes(id);
  const keepMain = new Set(mainWhole ? main : main.slice(0, guestShown(main.length)));
  const kept = ps.filter(p => keepMain.has(p) || (deepOpen && p?.level === "deep"));
  if (kept.length === ps.length) return ch;
  const locked: Json = { chapter: key(id), title: WEST_TITLES[id] ?? String(ch.title ?? id), tier: a.tier, shown: keepMain.size, total: main.length,
                         deep: deepOpen ? 0 : deep.length, next: "/chiem-tinh/", perks: "Đăng nhập bằng Google, miễn phí: đọc trọn phần luận chính của lá số gốc và Đọc sâu của bốn chương đầu." };
  if (member) locked.plans = plansFor(key(id)).map(p => ({ id: p.id, name: p.name, coins: p.coins, price: Math.max(0, p.coins - (a.credit ?? 0)) }));
  return { id: ch.id, title: ch.title, ...(ch.lead ? { lead: ch.lead } : {}), paragraphs: kept, locked };
}

/** A whole /api/west/reading answer. The audit counts and the operational definitions are about the method, not the text: kept. */
export function gateWest(out: Json, a: Access): Json {
  if (!out || typeof out !== "object" || !Array.isArray(out.chapters)) return out;
  return { ...out, chapters: out.chapters.map((c: Json) => gateWestChapter(c, a)) };
}
