// A card's reading comes only from the sourced pack (engine/data/tarot/pack_tarot_pkt.json, built by tools/build_tarot_pack.py from
// hand-made entries checked against the printed pages of Waite's Pictorial Key text, 1916 de Laurence issue, source SRC_PKT): Waite's words
// in English, the page, and a Vietnamese paraphrase of those words only. No entry, no meaning: the card then shows its name and a neutral
// line. Nothing here writes text of its own about a card.
import pack from "../../engine/data/tarot/pack_tarot_pkt.json" with { type: "json" };
import { BY_ID, type Card } from "./deck.ts";
import { cleanWording } from "./guard.ts";

export type Orientation = "upright" | "reversed";
export type Category = "divinatory" | "another_reading" | "description";
export interface PackEntry { card: string; orientation: Orientation; page: number | string; quote_en: string; text_vi: string; category: Category }
export interface PackSource { id: string; title: string; author: string; year: number; edition: string; cite: string }

export const SOURCE = (pack as { source: PackSource }).source;
export const PENDING_TEXT = `Ý nghĩa của lá này đang được chuẩn bị từ sách nguồn: ${SOURCE.author}, ${SOURCE.title}. Thiên Bàn chỉ đăng ý nghĩa có ghi trang sách.`;
const CATEGORIES: readonly Category[] = ["divinatory", "another_reading", "description"];
// counted as tools/build_tarot_pack.py counts them: "…" and dashes separate words, a hyphen joins
const words = (q: string) => q.replace(/[…—–]/g, " ").replace(/-\s*/g, "").split(/[^A-Za-z0-9]+/).filter(Boolean).length;

/** Why an entry may not be used (null when it may). */
export function entryProblem(e: Partial<PackEntry>): string | null {
  if (!e || typeof e.card !== "string" || !BY_ID.has(e.card)) return "unknown card";
  if (e.orientation !== "upright" && e.orientation !== "reversed") return "orientation must be upright or reversed";
  if (!(Number.isInteger(e.page) && (e.page as number) > 0) && !(typeof e.page === "string" && /^\d+(-\d+)?$/.test(e.page))) return "page missing";
  if (typeof e.quote_en !== "string" || words(e.quote_en) < 4) return "quote_en missing";
  if (typeof e.text_vi !== "string" || e.text_vi.trim().length < 3) return "text_vi missing";
  if (!CATEGORIES.includes(e.category as Category)) return "category missing";
  if (!cleanWording(e.text_vi)) return "text_vi uses banned wording";
  return null;
}

const ENTRIES: PackEntry[] = ((pack as { entries: PackEntry[] }).entries ?? []).filter(e => entryProblem(e) === null);
const INDEX = new Map<string, PackEntry[]>();
for (const e of ENTRIES) {
  const k = `${e.card}:${e.orientation}`;
  INDEX.set(k, [...(INDEX.get(k) ?? []), e]);
}
export const packSize = () => ENTRIES.length;
export const citeOf = (page: number | string) => `${SOURCE.cite} tr. ${page}`;

export interface ReadingItem { text_vi: string; quote_en: string; page: number | string; cite: string; category: Category }
export type Reading = { status: "sourced"; items: ReadingItem[] } | { status: "pending" | "no_reversed"; text: string };
export const NO_REVERSED_TEXT = "Waite không ghi nghĩa riêng cho lá này khi ngược; Thiên Bàn không tự thêm. Bạn có thể đọc nghĩa của lá xuôi ở trang lá bài.";

/** Every entry of the card in its orientation, in the pack's order (divinatory meanings first, then other readings and the description). */
export function readingFor(card: Card, reversed: boolean): Reading {
  const list = INDEX.get(`${card.id}:${reversed ? "reversed" : "upright"}`);
  if (!list?.length) return reversed && INDEX.has(`${card.id}:upright`) ? { status: "no_reversed", text: NO_REVERSED_TEXT } : { status: "pending", text: PENDING_TEXT };
  const rank = (c: Category) => CATEGORIES.indexOf(c);
  return {
    status: "sourced",
    items: [...list].sort((a, b) => rank(a.category) - rank(b.category))
      .map(e => ({ text_vi: e.text_vi, quote_en: e.quote_en, page: e.page, cite: citeOf(e.page), category: e.category })),
  };
}

/** Waite gives no reversed meaning for this card (the page has none, so the reversed card shows the neutral line). */
export const noReversed = (card: Card) => !INDEX.has(`${card.id}:reversed`) && INDEX.has(`${card.id}:upright`);
