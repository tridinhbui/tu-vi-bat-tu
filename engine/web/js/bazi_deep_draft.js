/* Bát Tự deep analysis, DRAFT view. Pure functions build a view-model from /api/bazi-structure (with bazi_deep_draft=true); render() draws it with textContent only.
   Contract: docs/BAZI_DEEP_API_CONTRACT.md. Rules this file must keep:
   - every method is shown with its own conclusion, in the server's fixed order; nothing is ranked, merged, scored or hidden;
   - the three verification levels are shown separately, using the server's strings; "empirical_validated" is shown as given;
   - the experimental label is always visible; a disagreement is always shown together with the "no unified conclusion" message. */
(function (root) {
  "use strict";
  // Replace internal identifiers by plain Vietnamese using the server-provided token_labels / source_labels (data, not logic; unknown tokens are left alone).
  function plain(ui, text) {
    var t = String(text);
    var src = ui.source_labels || {}, tok = ui.token_labels || {};
    t = t.replace(/SRC_[A-Z_]+/g, function (m) { return src[m] || m; });
    t = t.replace(/(['"])(Ti|An|Tai|QuanSat|ThucThuong)\1/g, function (m, q, g) { return tok[g] || g; });
    t = t.replace(/\b(Ti|An|Tai)=/g, function (m, g) { return (tok[g] || g) + "="; });
    t = t.replace(/\b(he_thong|tvh_40|war_share|bridge_min|tvh_margin|QuanSat|ThucThuong|khong_chan|chi_co_gia|thanh_nhung_bi_pha|bai_cuu_yeu|chua_ro|khong_ap_dung)\b/g, function (m) { return tok[m] || m; });
    t = t.replace(/\b(TVH|TTT)\b/g, function (m) { return tok[m] || m; });
    return t;
  }
  function gname(ui, g) { return (ui.group_names && ui.group_names[g]) || g; }
  function glist(ui, a) { return (a || []).map(function (g) { return gname(ui, g); }); }
  function stat(ui, s) { return (ui.status_labels && ui.status_labels[s]) || s; }

  // The state rule of the contract, section 3. Client-side on purpose: the server never "chooses".
  function unifiedState(Y) {
    var applied = Object.keys(Y.methods).filter(function (n) { return Y.methods[n].meta.applied; });
    if (Y.comparison.disagreements.length) return "no_unified_conclusion";
    if (applied.length >= 2 && Y.comparison.consensus.length) return "agreement_not_proof";
    return applied.length === 1 ? "single_method" : "no_unified_conclusion";
  }

  function readingsOf(ui, m) {
    var rs = [];
    var take = function (label, o) {
      rs.push({ label: label, yong: glist(ui, o.yong), xi: glist(ui, o.xi), ji: glist(ui, o.ji), need: o.need_elements || [], follows_book_rule: o.follows_book_rule });
    };
    if (m.status === "hai_cach_doc" && m.alternatives) {
      m.alternatives.forEach(function (a) { take(a.dm_vi || a.level || "cách đọc", a); });
    } else {
      take("", m);
    }
    return rs;
  }

  function buildViewModel(resp, mode) {
    var d = resp.bazi_deep_draft, Y = resp.yongshen;
    if (!d) return { enabled: false, label: null };
    var ui = d.ui_strings, order = d.method_order, titles = ui.method_titles, key = unifiedState(Y);
    var methods = order.map(function (name) {
      var m = Y.methods[name], lv = m.meta.levels;
      var levels = ["transcription_verified", "source_rule_verified", "empirical_validated"].map(function (k) {
        return { key: k, name: ui.level_names[k], value: lv[k], text: ui.level_values[k][lv[k]] };
      });
      var thr = m.threshold ? { own_share: m.threshold.own_share, near: m.threshold.near_threshold, margin_src: m.threshold.margin_src, rule_src: m.threshold.rule_src, equality: m.threshold.equality_choice } : null;
      return { key: name, title: titles[name], badge: ui.verification_badges[m.meta.verification], levels: levels, why: plain(ui, lv.why), applies_when: plain(ui, m.meta.applies_when), strength_basis: plain(ui, m.meta.strength_basis),
               status: m.status, status_text: stat(ui, m.status), applied: m.meta.applied, readings: readingsOf(ui, m), trace: m.trace.map(function (x) { return plain(ui, x); }), sources: m.meta.source.map(function (x) { return plain(ui, x); }), threshold: thr,
               two_readings_notice: m.status === "hai_cach_doc" ? (m.threshold ? ui.states.two_readings : ui.states.two_readings_system) : null,
               evidence_chip: ui.states.insufficient_evidence_chip };
    });
    var rows = {};
    Y.comparison.rows.forEach(function (r) { rows[r.group] = r.label; });
    var disagreements = Y.comparison.disagreements.map(function (x) {
      var t = function (n) { return titles[n]; };
      return { group: x.group, label: rows[x.group] || gname(ui, x.group), favourable: x.favourable_in.map(t), unfavourable: x.unfavourable_in.map(t) };
    });
    var conflict = d.book_internal_conflict ? { note_only: d.book_internal_conflict.note_only, table_only: d.book_internal_conflict.table_only, text: ui.states.book_internal_conflict } : null;
    return {
      enabled: true, label: d.draft_label, banner: d.banner, state: key, state_text: ui.states[key],
      agreement_groups: key === "agreement_not_proof" ? glist(ui, Y.comparison.consensus) : [],
      methods: methods, disagreements: disagreements, conflict: conflict, mode: mode === "expert" ? "expert" : "easy", reading: resp.bazi_deep_reading || null,
      review_line: ui.states.review_status.replace("{n}", d.review_status.cells_confirmed_by_human).replace("{total}", d.review_status.cells_total),
      isolation_note: ui.states.isolation_note, ui: ui
    };
  }

  // ------------------------------------------------------------ the seven-chapter reading (reading/1). Text comes from the server already in Vietnamese; every string is still run through plain().
  var DIR = { thuan: "Thuận lợi", bat_loi: "Bất lợi" };
  var COL = { index: "Vận", pillar: "Đại vận", start: "Bắt đầu", start_year: "Năm", god: "Thập thần của can", group: "Nhóm", verdict: "Theo bảng sách" };
  var VERDICT = { tot: "Thuận", xau: "Bất lợi", khong_neu: "Sách không nêu" };
  function textOf(ui, s) { return plain(ui, s); }

  function itemCard(ui, R, it, mode, headlines) {
    var card = el("article", "bd-item bd-basis-" + it.basis); card.dataset.item = it.id; card.dataset.basis = it.basis;
    var head = el("div", "bd-item-head");
    head.appendChild(el("span", "bd-chip bd-b-" + it.basis, it.basis_vi));
    if (DIR[it.direction]) head.appendChild(el("span", "bd-chip bd-d-" + it.direction, DIR[it.direction]));
    head.appendChild(el("b", null, textOf(ui, it.headline)));
    card.appendChild(head);
    card.appendChild(el("p", "bd-item-text", textOf(ui, mode === "expert" ? it.expert : it.easy)));
    if (it.table) {
      var tb = el("table", "bd-table"), keys = Object.keys(it.table[0] || {}).filter(function (k) { return COL[k]; });
      var tr = el("tr"); keys.forEach(function (k) { tr.appendChild(el("th", null, COL[k])); }); tb.appendChild(tr);
      it.table.forEach(function (row) { var r = el("tr"); keys.forEach(function (k) { var v = row[k]; r.appendChild(el("td", null, k === "verdict" ? VERDICT[v] || v : k === "group" ? (ui.group_names[v] || v) : v == null ? "—" : String(v))); }); tb.appendChild(r); });
      card.appendChild(tb);
    }
    var det = el("details", "bd-chain"); if (mode === "expert") det.open = true;
    det.appendChild(el("summary", null, mode === "expert" ? "Chuỗi lập luận" : "Vì sao?"));
    var ol = el("ol");
    it.chain.forEach(function (c) { var li = el("li"); li.dataset.step = c.step; li.appendChild(el("b", null, c.label + ": ")); li.appendChild(document.createTextNode(textOf(ui, c.text))); ol.appendChild(li); });
    det.appendChild(ol); card.appendChild(det);
    if (it.sources && it.sources.length) card.appendChild(line("Nguồn", it.sources.map(function (x) { return textOf(ui, x.title + (x.page ? ", " + x.page : "")); })));
    if (mode === "expert") {
      card.appendChild(el("p", "bd-note", "Mức chắc chắn: " + it.certainty_vi));
      (it.caveats || []).forEach(function (c) { card.appendChild(el("p", "bd-note", "Lưu ý: " + textOf(ui, c))); });
    }
    if (it.counter && it.counter.length) card.appendChild(line("Đi ngược chiều với", it.counter.map(function (id) { return textOf(ui, headlines[id] || id); })));
    return card;
  }

  function renderReading(container, R, mode, ui) {
    var headlines = {};
    var all = [];
    R.foundation.sections.forEach(function (s) { s.items.forEach(function (i) { headlines[i.id] = i.headline; all.push(i); }); });
    R.chapters.forEach(function (c) { c.sections.forEach(function (s) { s.items.forEach(function (i) { headlines[i.id] = i.headline; all.push(i); }); }); });
    var root = el("section", "bd-reading-root");
    root.appendChild(el("h2", null, "Luận giải theo chương"));
    root.appendChild(el("p", "bd-note", mode === "expert" ? "Chế độ Chuyên sâu: đủ thuật ngữ, chuỗi dữ kiện → quy tắc → điều kiện → kết luận, nguồn sách và mức chắc chắn." : "Chế độ Dễ hiểu: giải thích ngắn gọn; mở “Vì sao?” ở từng ý để xem lập luận."));
    root.appendChild(el("p", "bd-note", R.pillars));
    var f = el("details", "bd-chap bd-foundation"); f.open = true; f.dataset.chapter = "nen-tang";
    f.appendChild(el("summary", null, R.foundation.title)); f.appendChild(el("p", "bd-q", R.foundation.question));
    R.foundation.sections.forEach(function (s) { f.appendChild(el("h4", null, s.title)); s.items.forEach(function (i) { f.appendChild(itemCard(ui, R, i, mode, headlines)); }); });
    root.appendChild(f);
    R.chapters.forEach(function (c) {
      var d = el("details", "bd-chap"); d.open = true; d.dataset.chapter = c.id;
      d.appendChild(el("summary", null, c.title));
      d.appendChild(el("p", "bd-q", c.question));
      var sm = el("p", "bd-sum" + (c.empty ? " bd-sum-empty" : "")); sm.appendChild(el("b", null, "Kết luận chính: ")); sm.appendChild(document.createTextNode(textOf(ui, mode === "expert" ? c.summary_expert : c.summary_easy))); d.appendChild(sm);
      if (c.why.length) {
        var w = el("div", "bd-why"); w.appendChild(el("h4", null, "Vì sao lá số này được luận như vậy?"));
        var ul = el("ul");
        c.why.forEach(function (x) { var li = el("li"); li.appendChild(el("b", null, textOf(ui, x.headline))); li.appendChild(el("div", null, "Dữ kiện: " + textOf(ui, x.du_kien))); li.appendChild(el("div", null, "Quy tắc: " + textOf(ui, x.quy_tac))); li.appendChild(el("div", null, "Kết luận: " + textOf(ui, x.ket_luan))); ul.appendChild(li); });
        w.appendChild(ul); d.appendChild(w);
      }
      c.sections.forEach(function (s) { d.appendChild(el("h4", null, s.title)); s.items.forEach(function (i) { d.appendChild(itemCard(ui, R, i, mode, headlines)); }); });
      c.opposing.forEach(function (o) { d.appendChild(el("p", "bd-pair", o.note + " (" + o.thuan.length + " thuận, " + o.bat_loi.length + " bất lợi)")); });
      if (c.refs.length) d.appendChild(line("Liên quan đến nền tảng", c.refs.map(function (r) { return textOf(ui, r.headline); })));
      var g = el("div", "bd-gaps"); g.appendChild(el("h4", null, "Giới hạn và chưa đủ căn cứ"));
      c.gaps.forEach(function (x) { var p = el("p", "bd-gap"); p.appendChild(el("span", "bd-chip bd-b-chua_du_can_cu", x.basis_vi)); p.appendChild(document.createTextNode(" " + textOf(ui, mode === "expert" ? x.expert : x.easy))); g.appendChild(p); });
      d.appendChild(g); root.appendChild(d);
    });
    var lim = el("div", "bd-limits"); lim.appendChild(el("h4", null, "Giới hạn chung")); R.limits.forEach(function (x) { lim.appendChild(el("p", "bd-note", x)); }); root.appendChild(lim);
    container.appendChild(root);
  }

  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function line(label, items) { var p = el("p", "bd-line"); p.appendChild(el("b", null, label + ": ")); p.appendChild(document.createTextNode(items.length ? items.join(", ") : "—")); return p; }

  function render(container, vm) {
    container.textContent = "";
    if (!vm.enabled) { container.appendChild(el("p", "bd-off", "Chế độ phân tích chuyên sâu đang tắt.")); return; }
    var top = el("div", "bd-label", vm.label); top.setAttribute("role", "status"); container.appendChild(top);          // always visible: sticky via CSS
    container.appendChild(el("p", "bd-banner", vm.banner));
    container.appendChild(el("p", "bd-review", vm.review_line));
    var st = el("div", "bd-state bd-state-" + vm.state); st.appendChild(el("p", null, vm.state_text));
    if (vm.agreement_groups.length) st.appendChild(el("p", null, vm.ui.field_labels.consensus + ": " + vm.agreement_groups.join(", ")));
    container.appendChild(st);
    if (vm.conflict) {
      var c = el("div", "bd-conflict"); c.appendChild(el("p", null, vm.conflict.text));
      c.appendChild(line(vm.ui.field_labels.conflict_note_only, vm.conflict.note_only)); c.appendChild(line(vm.ui.field_labels.conflict_table_only, vm.conflict.table_only)); container.appendChild(c);
    }
    if (vm.reading) renderReading(container, vm.reading, vm.mode, vm.ui);
    if (vm.disagreements.length) {
      var dg = el("section", "bd-disagree"); dg.appendChild(el("h3", null, vm.ui.field_labels.disagreements));
      vm.disagreements.forEach(function (x) {
        var r = el("div", "bd-dis"); r.appendChild(el("b", null, x.label));
        r.appendChild(line(vm.ui.field_labels.favourable, x.favourable)); r.appendChild(line(vm.ui.field_labels.unfavourable, x.unfavourable)); dg.appendChild(r);
      });
      container.appendChild(dg);
    }
    vm.methods.forEach(function (m) {
      var card = el("article", "bd-method"); card.dataset.method = m.key;
      var h = el("h3", null, m.title); h.appendChild(el("span", "bd-badge", m.badge)); h.appendChild(el("span", "bd-badge bd-chip", m.evidence_chip)); card.appendChild(h);
      card.appendChild(el("p", "bd-status", m.status_text));
      m.readings.forEach(function (r) {
        var box = el("div", "bd-reading");
        if (r.label) box.appendChild(el("b", null, r.label + (r.follows_book_rule ? " (cách đọc theo quy tắc 40%)" : "")));
        box.appendChild(line(vm.ui.field_labels.yong, r.yong)); box.appendChild(line(vm.ui.field_labels.xi, r.xi)); box.appendChild(line(vm.ui.field_labels.ji, r.ji));
        if (r.need.length) box.appendChild(line(vm.ui.field_labels.need_elements, r.need));
        card.appendChild(box);
      });
      if (m.two_readings_notice) card.appendChild(el("p", "bd-note", m.two_readings_notice));
      if (m.threshold) card.appendChild(el("p", "bd-note", "Phe mình " + m.threshold.own_share + " so với ngưỡng 40% (" + plain(vm.ui, m.threshold.rule_src) + "). Biên hiển thị: " + plain(vm.ui, m.threshold.margin_src) + ". " + plain(vm.ui, m.threshold.equality)));
      var lv = el("ul", "bd-levels");
      m.levels.forEach(function (l) { var li = el("li"); li.dataset.level = l.key; li.dataset.value = l.value; li.appendChild(el("b", null, l.name + ": ")); li.appendChild(document.createTextNode(l.text)); lv.appendChild(li); });
      card.appendChild(lv);
      card.appendChild(el("p", "bd-note", m.why));
      card.appendChild(line(vm.ui.field_labels.applies_when, [m.applies_when])); card.appendChild(line(vm.ui.field_labels.strength_basis, [m.strength_basis])); card.appendChild(line(vm.ui.field_labels.source, m.sources));
      var det = el("details"); det.appendChild(el("summary", null, vm.ui.field_labels.trace)); var ol = el("ol"); m.trace.forEach(function (t) { ol.appendChild(el("li", null, t)); }); det.appendChild(ol); card.appendChild(det);
      container.appendChild(card);
    });
    container.appendChild(el("p", "bd-note", vm.isolation_note));
  }

  var api = { plain: plain, unifiedState: unifiedState, buildViewModel: buildViewModel, render: render };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.BaziDeepDraft = api;
})(typeof window !== "undefined" ? window : globalThis);
