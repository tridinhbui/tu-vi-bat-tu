// node reading_render_check.js <responses.json> : renders the reading in both modes with a fake DOM and checks the contract.
const fs = require("fs"), path = require("path");
const D = require(path.join(__dirname, "../../web/js/bazi_deep_draft.js"));
const responses = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
function node(tag) { const n = { tag, className: "", dataset: {}, children: [], _text: "", attrs: {}, open: false }; Object.defineProperty(n, "textContent", { get() { return this._text + this.children.map(c => c.textContent).join(""); }, set(v) { this._text = String(v); this.children = []; } }); n.appendChild = c => { n.children.push(c); return c; }; n.setAttribute = (k, v) => { n.attrs[k] = v; }; return n; }
global.document = { createElement: node, createTextNode: t => ({ tag: "#text", children: [], get textContent() { return t; } }) };
const walk = (n, f) => { f(n); (n.children || []).forEach(c => walk(c, f)); };
const RAW = /SRC_[A-Z]|he_thong|tvh_40|war_share|bridge_min|tvh_margin|\bQuanSat\b|\bThucThuong\b|khong_chan|chi_co_gia|thanh_nhung_bi_pha|cach_cuc_tvh|thuan_the|ban_khi|trung_khi|du_khi|undefined|\[object/;
const FORBID = ["đã chứng minh", "chứng minh đúng", "chính xác", "kết luận cuối", "dụng thần cuối cùng", "điểm tổng", "chắc chắn là", "nhất định"];
const out = { n: responses.length, problems: [], easyDiffersFromExpert: 0, chapters: {}, gaps: 0, withTable: 0, sources: 0 };
responses.forEach((resp, i) => {
  const bad = m => { if (out.problems.length < 30) out.problems.push(`#${i}: ${m}`); };
  const texts = {};
  ["easy", "expert"].forEach(mode => {
    const vm = D.buildViewModel(resp, mode); const root = node("div"); D.render(root, vm);
    const all = root.textContent; texts[mode] = all;
    if (root.children[0].className !== "bd-label") bad("label not first (" + mode + ")");
    const m = all.match(RAW); if (m) bad("raw identifier (" + mode + "): " + m[0]);
    FORBID.forEach(f => { if (all.toLowerCase().includes(f)) bad("forbidden phrase (" + mode + "): " + f); });
    let chaps = [], items = 0, gapEls = 0, tables = 0, srcLines = 0;
    walk(root, n => { if (n.tag === "details" && /bd-chap/.test(n.className)) chaps.push(n.dataset.chapter); if (/bd-item\b/.test(n.className) && n.tag === "article") { items++; const steps = []; walk(n, x => { if (x.dataset && x.dataset.step) steps.push(x.dataset.step); }); if (steps.join() !== "du_kien,quy_tac,dieu_kien,ket_luan") bad("chain steps " + steps.join()); } if (/bd-gap\b/.test(n.className)) gapEls++; if (n.tag === "table") tables++; });
    const want = ["nen-tang", "tinh-cach", "nang-luc", "su-nghiep", "tai-loc", "hon-nhan", "dai-van", "dung-than"];
    if (chaps.join() !== want.join()) bad("chapters " + chaps.join());
    if (gapEls < 7) bad("gaps rendered " + gapEls);
    if (tables < 1) bad("no đại vận table");
    out.gaps += gapEls; out.withTable += tables > 0; out.sources += (all.match(/Nguồn:/g) || []).length;
    const R = resp.bazi_deep_reading;
    R.chapters.forEach(c => { if (!all.includes(c.title)) bad("chapter title missing " + c.id); const sum = mode === "easy" ? c.summary_easy : c.summary_expert; if (!all.includes(D.plain(resp.bazi_deep_draft.ui_strings, sum).slice(0, 40))) bad("summary missing " + c.id); });
    R.chapters.forEach(c => { c.sections.forEach(s => s.items.forEach(it => { const t = mode === "easy" ? it.easy : it.expert; if (!all.includes(D.plain(resp.bazi_deep_draft.ui_strings, t).slice(0, 40))) bad("item text missing " + it.id); })); });
  });
  if (texts.easy !== texts.expert) out.easyDiffersFromExpert++;
  if (!texts.expert.includes("Mức chắc chắn:") || texts.easy.includes("Mức chắc chắn:")) bad("expert-only certainty line misplaced");
});
console.log(JSON.stringify(out));
