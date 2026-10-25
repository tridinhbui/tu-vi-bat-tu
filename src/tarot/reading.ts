// A card's reading comes only from the sourced pack (engine/data/tarot/pack_tarot_pkt.json, built by tools/build_tarot_pack.py from
// hand-checked entries of A. E. Waite, The Pictorial Key to the Tarot, 1911): the book's line in English, its page, and a Vietnamese
// rendering of that line. No entry, no meaning: the card shows its name and a neutral line saying the meaning is being prepared from the
// cited book. Nothing here writes text of its own about a card.
import pack from "../../engine/data/tarot/pack_tarot_pkt.json" with { type: "json" };
import { BY_ID, type Card } from "./deck.ts";
import { cleanWording } from "./guard.ts";

export type Orientation = "upright" | "reversed";
export interface PackEntry { card: string; orientation: Orientation; page: number | string; quote_en: string; text_vi: string }
export interface PackSource { id: string; title: string; author: string; year: number; cite: string }

export const SOURCE = (pack as { source: PackSource }).source;
export const PENDING_TEXT = `Ý nghĩa của lá này đang được chuẩn bị từ sách nguồn: ${SOURCE.author}, ${SOURCE.title} (${SOURCE.year}). ` +
  "Thiên Bàn chỉ đăng ý nghĩa có ghi trang sách.";

/** Why an entry may not be used (null when it may). */
export function entryProblem(e: Partial<PackEntry>): string | null {
  if (!e || typeof e.card !== "string" || !BY_ID.has(e.card)) return "unknown card";
  if (e.orientation !== "upright" && e.orientation !== "reversed") return "orientation must be upright or reversed";
  if (!(Number.isInteger(e.page) && (e.page as number) > 0) && !(typeof e.page === "string" && /^\d+(-\d+)?$/.test(e.page))) return "page missing";
  if (typeof e.quote_en !== "string" || e.quote_en.trim().length < 3) return "quote_en missing";
  if (typeof e.text_vi !== "string" || e.text_vi.trim().length < 3) return "text_vi missing";
  if (!cleanWording(e.text_vi)) return "text_vi uses banned wording";
  return null;
}

const ENTRIES: PackEntry[] = ((pack as { entries: PackEntry[] }).entries ?? []).filter(e => entryProblem(e) === null);
const INDEX = new Map(ENTRIES.map(e => [`${e.card}:${e.orientation}`, e]));
export const packSize = () => ENTRIES.length;

export type Reading =
  | { status: "sourced"; text_vi: string; quote_en: string; page: number | string; cite: string }
  | { status: "pending"; text: string };

export function readingFor(card: Card, reversed: boolean): Reading {
  const e = INDEX.get(`${card.id}:${reversed ? "reversed" : "upright"}`);
  if (!e) return { status: "pending", text: PENDING_TEXT };
  return { status: "sourced", text_vi: e.text_vi, quote_en: e.quote_en, page: e.page, cite: `${SOURCE.cite}, tr. ${e.page}` };
}
