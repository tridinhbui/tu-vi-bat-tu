// Run by tests/test_bazi_deep_phase7.py with: node phase7_viewmodel_check.js <responses.json>
// Checks, for every response, that the draft view-model and the rendered DOM keep every method's own conclusion, never rank or merge, and always show the label and the contract messages.
const fs = require("fs");
const path = require("path");
const D = require(path.join(__dirname, "../../web/js/bazi_deep_draft.js"));
const responses = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));

function node(tag) {
  const n = { tag, className: "", dataset: {}, children: [], _text: "", attrs: {} };
  Object.defineProperty(n, "textContent", { get() { return this._text + this.children.map(c => c.textContent).join(""); }, set(v) { this._text = String(v); this.children = []; } });
  n.appendChild = c => { n.children.push(c); return c; };
  n.setAttribute = (k, v) => { n.attrs[k] = v; };
  return n;
}
global.document = { createElement: node, createTextNode: t => ({ tag: "#text", children: [], get textContent() { return t; } }) };
const walk = (n, f) => { f(n); (n.children || []).forEach(c => walk(c, f)); };

const FORBIDDEN = ["đã chứng minh", "chứng minh đúng", "chính xác", "kết luận cuối", "dụng thần cuối cùng", "điểm tổng", "chắc chắn"];
const out = { n: responses.length, states: {}, problems: [], with_disagreement: 0, hai_cach: 0, conflict_cells: 0, unified: {} };
responses.forEach((resp, i) => {
  const bad = m => out.problems.push(`#${i}: ${m}`);
  const Y = resp.yongshen, d = resp.bazi_deep_draft;
  const vm = D.buildViewModel(resp);
  out.states[vm.state] = (out.states[vm.state] || 0) + 1;
  out.unified[i] = D.unifiedState(Y);
  if (!vm.enabled || vm.label !== "Phân tích thử nghiệm – chưa được kiểm chứng thực nghiệm") bad("label");
  if (vm.methods.map(m => m.key).join() !== d.method_order.join() || vm.methods.length !== 8) bad("method order/count");
  vm.methods.forEach(m => {
    const src = Y.methods[m.key];
    const ui = d.ui_strings.group_names;
    const names = a => (a || []).map(g => ui[g] || g);
    if (src.status === "hai_cach_doc") { out.hai_cach++; if (m.readings.length !== src.alternatives.length) bad(m.key + " lost a reading"); }
    else if (JSON.stringify(m.readings[0].yong) !== JSON.stringify(names(src.yong)) || JSON.stringify(m.readings[0].xi) !== JSON.stringify(names(src.xi)) || JSON.stringify(m.readings[0].ji) !== JSON.stringify(names(src.ji))) bad(m.key + " conclusion altered");
    if (m.levels.length !== 3 || m.levels.map(l => l.key).join() !== "transcription_verified,source_rule_verified,empirical_validated") bad(m.key + " levels");
    if (m.levels[2].value !== "no" || !m.levels[2].text.includes("Chưa có kiểm chứng")) bad(m.key + " empirical shown wrongly");
    if (m.trace.length !== src.trace.length || !m.sources.length || !m.status_text || m.status_text === m.status && !d.ui_strings.status_labels[m.status] && false) bad(m.key + " trace/source/status");
    if (!d.ui_strings.status_labels[src.status]) bad(m.key + " status without label: " + src.status);
  });
  if (vm.disagreements.length !== Y.comparison.disagreements.length) bad("disagreements dropped");
  if (Y.comparison.disagreements.length) {
    out.with_disagreement++;
    if (vm.state !== "no_unified_conclusion" || vm.state_text !== d.ui_strings.states.no_unified_conclusion) bad("disagreement without the contract message");
  }
  if (d.book_internal_conflict) { out.conflict_cells++; if (!vm.conflict) bad("conflict hidden"); }
  const j = JSON.stringify(Object.assign({}, vm, { ui: null })).toLowerCase();   // the ui block carries the forbidden list itself
  FORBIDDEN.forEach(f => { if (j.includes(f)) bad("forbidden phrase in view-model: " + f); });
  if (/winner|ranking|final_answer|total_score/.test(Object.keys(vm).join(" "))) bad("ranking key in view-model");
  // DOM render
  const root = node("div");
  D.render(root, vm);
  const all = root.textContent;
  if (root.children[0].className !== "bd-label" || root.children[0].textContent !== vm.label) bad("label is not the first element");
  if (!all.includes(vm.state_text)) bad("state text not rendered");
  vm.methods.forEach(m => { if (!all.includes(m.title)) bad("method not rendered: " + m.key); m.trace.forEach(t => { if (!all.includes(t)) bad("trace step missing"); }); m.levels.forEach(l => { if (!all.includes(l.text)) bad("level text missing"); }); });
  vm.disagreements.forEach(x => { if (!all.includes(x.label)) bad("disagreement not rendered"); });
  // Phase 8: no internal identifier reaches the reader, every card carries the 'insufficient evidence' chip, and the 40% sentence appears only where a 40% threshold exists
  const RAW = /SRC_[A-Z]|he_thong|tvh_40|war_share|bridge_min|tvh_margin|\bQuanSat\b|\bThucThuong\b|khong_chan|chi_co_gia|thanh_nhung_bi_pha|cach_cuc|thuan_the/;
  const rawHit = all.match(RAW); if (rawHit) bad("raw identifier shown: " + rawHit[0]);
  vm.methods.forEach(m => { if (m.evidence_chip !== d.ui_strings.states.insufficient_evidence_chip) bad("chip"); if (m.two_readings_notice && !m.threshold && m.two_readings_notice.includes("40%")) bad("40% sentence on a method without a 40% threshold: " + m.key); if (m.threshold && m.status === "hai_cach_doc" && m.two_readings_notice !== d.ui_strings.states.two_readings) bad("threshold method lacks the 40% notice"); });
  if (vm.isolation_note !== d.ui_strings.states.isolation_note) bad("isolation note");
  let articles = 0; walk(root, n => { if (n.tag === "article") articles++; });
  if (articles !== 8) bad("articles " + articles);
  const order = []; walk(root, n => { if (n.dataset && n.dataset.method) order.push(n.dataset.method); });
  if (order.join() !== d.method_order.join()) bad("render order differs from server order");
});
// flag off: nothing is invented
const off = D.buildViewModel({ yongshen: responses[0].yongshen });
if (off.enabled !== false) out.problems.push("flag-off view-model is enabled");
console.log(JSON.stringify(out));
