// What the Tarot pages may say: no banned wording, no "AI", never the trademarked deck name, the reflection line on every page, readings
// only from the sourced pack, sensitive questions noticed, and every card picture backed by a public-domain Commons page.
import { test } from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { BANNED, BANNED_WORDS, bannedIn } from "../../interpret/wording.ts";
import { cleanWording, fold, NOTICES, noticesFor, sensitiveTopics, TAROT_HEADER, cleanQuestion } from "../guard.ts";
import { entryProblem, NO_REVERSED_TEXT, packSize, PENDING_TEXT, readingFor } from "../reading.ts";
import { BY_ID, DECK, publicCard } from "../deck.ts";
import { faceHtml, resultHtml, addHistory, historyEntry, MAX_HISTORY } from "../../../engine/web/js/tarot.js";

const WEB = "engine/web";
const tarotPages = () => [`${WEB}/tarot/index.html`, `${WEB}/tarot/la-bai/index.html`,
  ...readdirSync(`${WEB}/tarot/la-bai`).filter(d => !d.endsWith(".html")).map(d => `${WEB}/tarot/la-bai/${d}/index.html`)];
const UI_FILES = () => [`${WEB}/js/tarot.js`, `${WEB}/css/tarot.css`, ...tarotPages()];
const visible = (html: string) => html.replace(/<script[\s\S]*?<\/script>/g, " ").replace(/<style[\s\S]*?<\/style>/g, " ").replace(/<[^>]+>/g, " ");

test("the banned list is one list: exported from wording.ts and used by the guard", () => {
  assert.ok(BANNED.length >= 14 && BANNED_WORDS.length === BANNED.length);
  for (const t of ["định mệnh đã an bài", "Bạn sẽ bị phạt", "nhất định sẽ thành"]) assert.equal(bannedIn(t).length, 1, t);   // accented edges
  assert.equal(bannedIn("chếtt").length + bannedIn("bệnh ung thưa").length, 0);
  assert.equal(bannedIn("điều này chắc chắn xảy ra").length, 1);
  assert.equal(cleanWording("Một lá để suy ngẫm."), true);
  assert.equal(cleanWording("Bạn sẽ bị mất việc."), false);
  assert.equal(cleanWording("Sách viết “sẽ bị” như vậy."), true);          // a quoted book line is the book's voice
  const v = readFileSync("src/interpret/validate.ts", "utf8");
  assert.match(v, /import \{ BANNED \} from '\.\/wording\.ts'/);
  assert.doesNotMatch(v, /const BANNED =/);
});

test("nothing the site writes for Tarot uses banned wording", () => {
  for (const t of [TAROT_HEADER, PENDING_TEXT, NO_REVERSED_TEXT, ...Object.values(NOTICES)]) assert.ok(cleanWording(t), t);
  for (const f of UI_FILES()) {
    const text = f.endsWith(".html") ? visible(readFileSync(f, "utf8")) : readFileSync(f, "utf8");
    assert.deepEqual(bannedIn(text).map(String), [], f);
  }
});

test('no "AI" and no trademarked deck name in any Tarot UI file; the chat button is not loaded there', () => {
  for (const f of UI_FILES()) {
    const s = readFileSync(f, "utf8");
    assert.doesNotMatch(s, /\bAI\b/, f);
    assert.doesNotMatch(s, /Rider[\s\-–]*Waite/i, f);
    if (f.endsWith(".html")) assert.ok(!s.includes("/js/ask.js"), f);
  }
});

test("every Tarot page carries the reflection line; 78 card pages, each named, each showing its sourced readings with their page", () => {
  const pages = tarotPages();
  assert.equal(pages.length, 80);
  for (const f of pages) assert.ok(readFileSync(f, "utf8").includes(TAROT_HEADER), f);
  for (const c of DECK) {
    const s = readFileSync(`${WEB}/tarot/la-bai/${c.slug}/index.html`, "utf8");
    assert.ok(s.includes(c.name_en) && s.includes(c.name_vi), c.slug);
    const pack = JSON.parse(readFileSync("engine/data/tarot/pack_tarot_pkt.json", "utf8"));
    for (const e of pack.entries.filter((x: any) => x.card === c.id)) {
      const esc = (t: string) => t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#x27;");
      assert.ok(s.includes(esc(e.text_vi)) && s.includes(`PKT (1916) tr. ${e.page}`), `${c.slug}: ${e.quote_en}`);
    }
  }
  const sitemap = readFileSync(`${WEB}/sitemap.xml`, "utf8");
  assert.ok(sitemap.includes("/tarot/</loc>") && DECK.every(c => sitemap.includes(`/tarot/la-bai/${c.slug}/</loc>`)));
});

test("readings come only from the pack: an empty pack gives the neutral line; a bad entry is refused", () => {
  const pack = JSON.parse(readFileSync("engine/data/tarot/pack_tarot_pkt.json", "utf8"));
  assert.equal(pack.source.id, "SRC_PKT"); assert.equal(pack.source.cite, "PKT (1916)");
  assert.ok(packSize() >= 78 * 2, String(packSize()));
  assert.equal(packSize(), pack.entries.length);                                     // no entry dropped by the reader-side checks
  for (const e of pack.entries) assert.equal(entryProblem(e), null, JSON.stringify(e));
  // every card has upright readings; every card but the Two of Cups (Waite gives none) has reversed ones; each item cites its page
  for (const c of DECK) for (const rev of [false, true]) {
    const r = readingFor(c, rev);
    if (rev && c.id === "C02") { assert.deepEqual(r, { status: "no_reversed", text: NO_REVERSED_TEXT }); continue; }
    assert.equal(r.status, "sourced", `${c.id} ${rev}`);
    if (r.status === "sourced") for (const i of r.items) assert.match(i.cite, /^PKT \(1916\) tr\. \d+$/);
  }
  const fool = readingFor(BY_ID.get("M00")!, false);
  assert.ok(fool.status === "sourced" && fool.items[0].text_vi.startsWith("Theo Waite, lá này gợi đến"));
  // the framing: a meaning the card suggests, never a forecast
  for (const e of pack.entries) assert.match(e.text_vi, /^(Theo Waite|Khi lá ngược|Waite ghi thêm|Trong phần tả lá bài)/, e.quote_en);
  const good = { card: "M00", orientation: "upright", page: 147, quote_en: "Folly, mania, extravagance, intoxication", text_vi: "Sự dại dột", category: "divinatory" } as const;
  assert.equal(entryProblem(good), null);
  assert.equal(entryProblem({ ...good, page: undefined as any }), "page missing");
  assert.equal(entryProblem({ ...good, card: "X99" }), "unknown card");
  assert.equal(entryProblem({ ...good, orientation: "sideways" as any }), "orientation must be upright or reversed");
  assert.equal(entryProblem({ ...good, text_vi: "Bạn chắc chắn thành công" }), "text_vi uses banned wording");
  assert.equal(entryProblem({ ...good, quote_en: "Folly, mania" }), "quote_en missing");
  assert.equal(entryProblem({ ...good, category: "guess" as any }), "category missing");
});

test("sensitive questions: health, pregnancy, life and death, law, money — with or without accents, without false alarms", () => {
  const cases: Array<[string, string[]]> = [
    ["Tôi có bị bệnh nặng không?", ["health"]], ["toi co nen di kham benh khong", ["health"]], ["Có nên uống thuốc này?", ["health"]],
    ["Tôi có mang thai không?", ["pregnancy"]], ["khi nao toi co bau", ["pregnancy"]],
    ["Bao giờ tôi chết?", ["life"]], ["tôi muốn tự tử", ["life"]],
    ["Tôi có thắng kiện không, có nên thuê luật sư?", ["legal"]], ["vợ chồng tôi có ly hôn không", ["legal"]], ["anh ấy có phải đi tù không", ["legal"]],
    ["Có nên đầu tư chứng khoán?", ["investment"]], ["mua bitcoin luc nay duoc khong", ["investment"]],
    ["Tôi nên nhìn công việc hiện tại thế nào?", []], ["Làm từ từ có được không?", []], ["Điều này thuộc về ai?", []],
    ["Tôi muốn đi tu", []], ["Tôi nên bênh vực bạn mình không?", []], ["", []],
  ];
  for (const [q, want] of cases) assert.deepEqual(sensitiveTopics(q), want, q);
  assert.equal(noticesFor("có nên vay tiền mua đất")[0].text, NOTICES.investment);
  assert.match(NOTICES.life, /115/);
  assert.equal(fold("Đường"), "duong");
  assert.equal(cleanQuestion("  a\u0000b  "), "a b");
  assert.equal(cleanQuestion("x".repeat(400))!.length, 300);
  assert.equal(cleanQuestion("   "), null); assert.equal(cleanQuestion(5), null);
});

test("card pictures: every listed image has a public-domain Commons page, sha256, size and its WebP files; the rest fall back to type", () => {
  const m = JSON.parse(readFileSync("engine/data/tarot/images.json", "utf8"));
  assert.equal(m.images.length + m.skipped.length, 78);
  const ids = new Set(m.images.map((i: any) => i.card));
  for (const i of m.images) {
    assert.ok(BY_ID.has(i.card), i.card);
    assert.match(i.commons_url, /^https:\/\/commons\.wikimedia\.org\/wiki\/File:/);
    assert.match(i.licence, /\{\{\s*PD-/);
    assert.equal(i.licence_short_name, "Public domain");
    assert.match(i.sha256, /^[0-9a-f]{64}$/);
    assert.ok(i.width > 500 && i.height > 800 && i.author === "Pamela Colman Smith", i.card);
    for (const w of ["300", "600"]) {
      const f = i.files[w], path = `${WEB}${f.path}`;
      assert.ok(existsSync(path), path);
      assert.equal(createHash("sha256").update(readFileSync(path)).digest("hex"), f.sha256, path);
      assert.equal(f.width, Number(w));
    }
  }
  for (const c of DECK) {
    const pc = publicCard(c);
    assert.equal(!!pc.image, ids.has(c.id), c.id);
    assert.match(faceHtml(pc, false), ids.has(c.id) ? /<img class="tcard timg"/ : /class="tcard tface/);
  }
  // the service worker does not preload the pictures
  assert.doesNotMatch(readFileSync(`${WEB}/sw.js`, "utf8"), /tarot\/img/);
});

test("the page script: a reversed card is marked, readings show the neutral line, history keeps the newest 20", () => {
  const c = publicCard(BY_ID.get("M13")!);
  const draw = { id: "A".repeat(22), spread: 1, header: TAROT_HEADER, layout_note: null, notices: [{ topic: "health", text: NOTICES.health }],
    cards: [{ slot: 1, pick: 3, reversed: true, card: { ...c, image: null }, reading: { status: "pending", text: PENDING_TEXT } }] };
  const html = resultHtml(draw);
  assert.ok(html.includes("is-rev") && html.includes("Ngược") && html.includes(PENDING_TEXT) && html.includes(NOTICES.health) && html.includes(TAROT_HEADER));
  const sourced = resultHtml({ ...draw, cards: [{ ...draw.cards[0], reading: readingFor(BY_ID.get("M13")!, true) }] });
  assert.ok(sourced.includes("PKT (1916) tr. 147") && sourced.includes("<blockquote lang=\"en\">"));
  assert.ok(html.includes("Tử Thần") && html.includes("Death"));
  let list: any[] = [];
  for (let i = 0; i < 25; i++) list = addHistory(list, historyEntry({ ...draw, id: String(i).padStart(22, "x") }, null));
  assert.equal(list.length, MAX_HISTORY); assert.equal(list[0].id, "24".padStart(22, "x"));
});
