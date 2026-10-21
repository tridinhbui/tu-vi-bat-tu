// The page side of phase 3, without a browser: chapter order from the profile, which chart counts as the user's own, the share-link
// rerouting of engine calls (no birth field may leave the page), the birth-data wrapper, and that every element the scripts look up exists.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { focusOf, orderChapters, focusIds, focusNote } from "../../../engine/web/js/focus.js";
import { bd, post, shareMode } from "../../../engine/web/js/util.js";
import { profileState, isOwnChart, focusFor } from "../../../engine/web/js/profile.js";
import { maskReq, SHARE_ENDPOINTS } from "../shares.ts";

const TV = ["tong-quan", "ban-menh", "tinh-cach", "cong-danh", "tai-bach", "quan-he", "dai-han", "cach-cuc", "muoi-hai-cung", "chuyen-sau"].map(id => ({ id, title: id }));
const BT = ["tong-quan", "nhat-chu", "ngu-hanh", "su-nghiep", "quan-he", "dai-van", "cach-cuc", "chuyen-sau"].map(id => ({ id, title: id }));
const ids = (cs: { id: string }[]) => cs.map(c => c.id);

test("a status in motion comes first; a settled one follows; 'nghỉ hưu' and 'không muốn nói' reorder nothing", () => {
  assert.deepEqual(focusOf({ career: "lam", relationship: "tim_hieu" }).map((f: any) => f.topic), ["rel", "career"]);
  assert.deepEqual(focusOf({ career: "tim_viec", relationship: "ket_hon" }).map((f: any) => f.topic), ["career", "rel"]);
  assert.deepEqual(focusOf({ career: "lam", relationship: "doc_than" }).map((f: any) => f.topic), ["career", "rel"]);   // tie: career first
  assert.deepEqual(focusOf({ career: "nghi", relationship: "" }), []);
  assert.deepEqual(focusOf(null), []);
});

test("the focus chapters move right after the overview; nothing is added or dropped", () => {
  const f = focusOf({ career: "lam", relationship: "chia_tay" });
  const tv = orderChapters(TV, "tv", f), bt = orderChapters(BT, "bt", f);
  assert.deepEqual(ids(tv), ["tong-quan", "quan-he", "cong-danh", "tai-bach", "ban-menh", "tinh-cach", "dai-han", "cach-cuc", "muoi-hai-cung", "chuyen-sau"]);
  assert.deepEqual(ids(bt), ["tong-quan", "quan-he", "su-nghiep", "nhat-chu", "ngu-hanh", "dai-van", "cach-cuc", "chuyen-sau"]);
  assert.deepEqual([...ids(tv)].sort(), [...ids(TV)].sort());
  assert.equal(orderChapters(TV, "tv", []), TV);
  assert.deepEqual(focusIds("tv", f), ["quan-he", "cong-danh", "tai-bach"]);
  const note = focusNote(f, ["Quan hệ", "Công danh"]);
  assert.match(note, /Ly thân hoặc ly hôn/); assert.match(note, /Chỉ thứ tự thay đổi/);
  assert.equal(focusNote([], []), "");
});

test("only the user's own chart is reordered: same dương lịch date, gender and (when known) hour", () => {
  profileState.profile = { cal: "lunar", year: 1990, month: 4, day: 23, solar: { year: 1990, month: 5, day: 17 }, hour: 10, minute: 30, gender: "female", career: "tim_viec", relationship: "" } as any;
  const own = { year: 1990, month: 5, day: 17, hour: 10, minute: 30, gender: "female" };
  assert.equal(isOwnChart(own), true);
  assert.equal(isOwnChart({ ...own, hour: 11 }), false);
  assert.equal(isOwnChart({ ...own, gender: "male" }), false);
  assert.equal(isOwnChart({ ...own, day: 23, month: 4 }), false);          // the typed âm lịch date is not the request date
  assert.deepEqual(focusFor({ ...own, year: 1965 }), []);
  assert.equal(focusFor(own).length, 1);
  profileState.profile = { ...profileState.profile, hour: null } as any;   // hour unknown: the date and gender decide
  assert.equal(isOwnChart({ ...own, hour: 3 }), true);
  profileState.profile = null;
  assert.equal(isOwnChart(own), false);
});

test("on a share link, engine calls go to /api/share/<id>/… carrying only viewer options; other calls are untouched", async () => {
  const seen: { url: string; body: any }[] = [];
  const realFetch = globalThis.fetch;
  globalThis.fetch = (async (url: string, init: RequestInit) => { seen.push({ url, body: JSON.parse(String(init.body)) }); return new Response("{}", { status: 200 }); }) as typeof fetch;
  try {
    shareMode.id = "A".repeat(22);
    const masked = { year: 1990, gender: "female", tz: "Asia/Ho_Chi_Minh" };
    await post("/api/chart", masked);
    await post("/api/year", { ...masked, day: 17, hour: 10, to_year: 2030, dignity_school: "khao_luan" });
    await post("/api/interpret", { ...masked, chapter: "all", mode: "prose" });
    await post("/api/lunar-to-solar", { day: 1, month: 1, year: 2000 });
    assert.deepEqual(seen.map(s => s.url), [`/api/share/${"A".repeat(22)}/chart`, `/api/share/${"A".repeat(22)}/year`, `/api/share/${"A".repeat(22)}/interpret`, "/api/lunar-to-solar"]);
    assert.deepEqual(seen.map(s => s.body).slice(0, 3), [{}, { to_year: 2030, dignity_school: "khao_luan" }, { chapter: "all", mode: "prose" }]);
    // every endpoint the page reroutes is one the Worker accepts
    for (const ep of ["chart", "reasoning", "analysis", "synthesis", "interpretation", "interpret", "year", "formations"]) assert.ok(SHARE_ENDPOINTS.has(ep), ep);
  } finally { shareMode.id = null; globalThis.fetch = realFetch; }
});

test("birth data is wrapped for hiding, and a value the page never got prints only the stand-in", () => {
  assert.equal(bd("17/05/"), '<span class="bd">17/05/</span><span class="bd-x">ẩn</span>');
  assert.equal(bd(undefined), '<span class="bd-x bd-on">ẩn</span>');
  assert.equal(bd("x", false, "··/··/"), '<span class="bd-x bd-on">··/··/</span>');
  assert.deepEqual(Object.keys(maskReq({ year: 1990, month: 5, day: 17, hour: 10, minute: 30, gender: "male", longitude: 106, use_true_solar_time: true, tz: "Asia/Ho_Chi_Minh" })).sort(), ["gender", "tz", "year"]);
});

test("every #id the account, share and export code looks up exists in the page or in a template the scripts render", () => {
  const page = readFileSync("engine/web/index.html", "utf8");
  const files = ["app", "acctpage", "profile", "mycharts", "share", "png"].map(f => readFileSync(`engine/web/js/${f}.js`, "utf8"));
  const all = page + readdirSync("engine/web/js").filter(f => f.endsWith(".js")).map(f => readFileSync(`engine/web/js/${f}`, "utf8")).join("\n");
  // a prefix with a value appended ($('#tv-' + id)) names a family of rendered ids, not one fixed id
  const wanted = new Set(files.join("\n").match(/\$\('#[a-z0-9-]+'(?!\s*\+)/gi)!.map(s => s.slice(4, -1)));
  for (const id of wanted) assert.ok(new RegExp(`id="${id}"|id = '${id}'|\\.id = '${id}'`).test(all), `#${id} is looked up but never defined`);
  for (const id of ["share-btn", "png-btn", "hide-birth", "share-banner", "account-view", "res-msg"]) assert.ok(wanted.has(id), id);
  assert.match(page, /href="\/css\/account\.css"/);
  assert.match(page, /href="\/privacy"/);
});
