// Wording the reading layers must never use: certainty, fate and grave events told as outcomes. Shared by the chapter validator
// (validate.ts) and the Tarot guard (src/tarot/guard.ts). A quoted book line (“…”) or a parenthesis is checked by the caller as it sees fit.
export const BANNED: readonly RegExp[] = [/\bchắc chắn\b/i, /\bnhất định sẽ\b/i, /\bđịnh mệnh\b/i, /\bkhông thể tránh\b/i, /\btai họa\b/i, /\bsẽ bị\b/i,
  /\btuyệt đối\b/i, /\bluôn luôn\b/i, /\bchết\b/i, /\byểu\b/i, /\btù tội\b/i, /\bly hôn\b/i, /\bung thư\b/i, /\bphá sản\b/i];

// JavaScript's \b only knows ASCII letters: a pattern that starts or ends on an accented letter ("định mệnh", "sẽ bị", "nhất định sẽ")
// never matches through BANNED as written. BANNED_WORDS is the same list with letter-aware edges. validate.ts still uses BANNED unchanged
// (switching it would change which chapters fail; that is an owner decision, see docs/TAROT.md); new code uses BANNED_WORDS.
const edge = (r: RegExp) => new RegExp(r.source.replace(/^\\b/, "(?<![\\p{L}\\p{N}_])").replace(/\\b$/, "(?![\\p{L}\\p{N}_])"), "iu");
export const BANNED_WORDS: readonly RegExp[] = BANNED.map(edge);

/** The banned patterns a text matches (empty when the text is clean), with letter-aware word edges. */
export const bannedIn = (text: string): RegExp[] => BANNED_WORDS.filter(b => b.test(text));
