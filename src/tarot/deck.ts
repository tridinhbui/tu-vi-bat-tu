// The 78 cards of the Waite–Smith deck (1909): ids, names, numbers and suits only (engine/data/tarot/deck.json, shared with the static
// pages). A card's meaning lives in the sourced pack (reading.ts), never here.
import deckJson from "../../engine/data/tarot/deck.json" with { type: "json" };
import imagesJson from "../../engine/data/tarot/images.json" with { type: "json" };

export type Suit = "wands" | "cups" | "swords" | "pentacles";
export interface Card { id: string; slug: string; arcana: "major" | "minor"; number: number; suit: Suit | null; name_en: string; name_vi: string }
export interface CardImage { card: string; files: Record<string, { path: string; width: number; height: number }> }

export const DECK: readonly Card[] = (deckJson as { cards: Card[] }).cards;
export const SUITS = (deckJson as { suits: Record<Suit, { en: string; vi: string }> }).suits;
export const BY_ID: ReadonlyMap<string, Card> = new Map(DECK.map(c => [c.id, c]));
export const DECK_SIZE = DECK.length;

// only images whose Commons page states public domain are listed in images.json "images" (tools/fetch_tarot_images.py)
const IMAGES: ReadonlyMap<string, CardImage> = new Map(((imagesJson as { images?: CardImage[] }).images ?? []).map(i => [i.card, i]));

const ROMAN = ["0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI"];
/** What the card face prints as its number: a Roman numeral for the Major Arcana, the rank for a court card, the pip value otherwise. */
export const numeral = (c: Card) => c.arcana === "major" ? ROMAN[c.number] : c.number === 1 ? "Át" : c.number <= 10 ? String(c.number) : "";

/** A card as the API sends it: names, number, suit and, when an approved image exists, its two WebP sizes. */
export function publicCard(c: Card) {
  const img = IMAGES.get(c.id);
  return {
    id: c.id, slug: c.slug, arcana: c.arcana, number: c.number, numeral: numeral(c), suit: c.suit,
    suit_vi: c.suit ? SUITS[c.suit].vi : null, suit_en: c.suit ? SUITS[c.suit].en : null, name_en: c.name_en, name_vi: c.name_vi,
    image: img ? { small: img.files["300"]?.path, large: img.files["600"]?.path, width: img.files["600"]?.width, height: img.files["600"]?.height } : null,
  };
}
