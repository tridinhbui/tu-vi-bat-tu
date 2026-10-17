/* Bát Tự deep analysis, DRAFT view. Pure functions build a view-model from /api/bazi-structure (with bazi_deep_draft=true); render() draws it with textContent only.
   Contract: docs/BAZI_DEEP_API_CONTRACT.md. Rules this file must keep:
   - every method is shown with its own conclusion, in the server's fixed order; nothing is ranked, merged, scored or hidden;
   - the three verification levels are shown separately, using the server's strings; "empirical_validated" is shown as given;
   - the experimental label is always visible; a disagreement is always shown together with the "no unified conclusion" message. */
(function (root) {
  "use strict";
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

  function buildViewModel(resp) {
    var d = resp.bazi_deep_draft, Y = resp.yongshen;
    if (!d) return { enabled: false, label: null };
    var ui = d.ui_strings, order = d.method_order, titles = ui.method_titles, key = unifiedState(Y);
    var methods = order.map(function (name) {
      var m = Y.methods[name], lv = m.meta.levels;
      var levels = ["transcription_verified", "source_rule_verified", "empirical_validated"].map(function (k) {
        return { key: k, name: ui.level_names[k], value: lv[k], text: ui.level_values[k][lv[k]] };
      });
      var thr = m.threshold ? { own_share: m.threshold.own_share, near: m.threshold.near_threshold, margin_src: m.threshold.margin_src, rule_src: m.threshold.rule_src, equality: m.threshold.equality_choice } : null;
      return { key: name, title: titles[name], badge: ui.verification_badges[m.meta.verification], levels: levels, why: lv.why, applies_when: m.meta.applies_when, strength_basis: m.meta.strength_basis,
               status: m.status, status_text: stat(ui, m.status), applied: m.meta.applied, readings: readingsOf(ui, m), trace: m.trace.slice(), sources: m.meta.source.slice(), threshold: thr,
               two_readings_notice: m.status === "hai_cach_doc" ? ui.states.two_readings : null };
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
      methods: methods, disagreements: disagreements, conflict: conflict,
      review_line: ui.states.review_status.replace("{n}", d.review_status.cells_confirmed_by_human).replace("{total}", d.review_status.cells_total),
      isolation_note: Y.isolation.note, ui: ui
    };
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
      var h = el("h3", null, m.title); h.appendChild(el("span", "bd-badge", m.badge)); card.appendChild(h);
      card.appendChild(el("p", "bd-status", m.status_text));
      m.readings.forEach(function (r) {
        var box = el("div", "bd-reading");
        if (r.label) box.appendChild(el("b", null, r.label + (r.follows_book_rule ? " (cách đọc theo quy tắc 40%)" : "")));
        box.appendChild(line(vm.ui.field_labels.yong, r.yong)); box.appendChild(line(vm.ui.field_labels.xi, r.xi)); box.appendChild(line(vm.ui.field_labels.ji, r.ji));
        if (r.need.length) box.appendChild(line(vm.ui.field_labels.need_elements, r.need));
        card.appendChild(box);
      });
      if (m.two_readings_notice) card.appendChild(el("p", "bd-note", m.two_readings_notice));
      if (m.threshold) card.appendChild(el("p", "bd-note", "Phe mình " + m.threshold.own_share + " so với ngưỡng 40% (" + m.threshold.rule_src + "). Biên hiển thị: " + m.threshold.margin_src + ". " + m.threshold.equality));
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

  var api = { unifiedState: unifiedState, buildViewModel: buildViewModel, render: render };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.BaziDeepDraft = api;
})(typeof window !== "undefined" ? window : globalThis);
