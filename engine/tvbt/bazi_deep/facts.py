"""Flat facts for the symbolic rule engine, taken from the analyzers' results. Names live in the `bazi.*` namespace
(already accepted by the pack validator). Each fact records which analyzer produced it (FACT_ORIGIN) so a finding's
provenance chain reaches back to a computation, not just to a rule."""
from __future__ import annotations

FACT_ORIGIN = {
    "bazi.dm_level": "strength.compute(sau tương tác)", "bazi.dm_level_raw": "strength.compute(nguyên cục)",
    "bazi.dm_ambiguous": "strength.compute: biên < level_margin", "bazi.dm_readings": "strength.compute",
    "bazi.dm_de_lenh": "season.season_states + strength.compute", "bazi.dm_root_grade": "position.roots + interact.resolve",
    "bazi.level_changed_by_interaction": "so sánh strength trước/sau interact.resolve",
    "bazi.cuc_formed": "interact.resolve (bước cục)", "bazi.hua_state": "interact.resolve (bước can hợp, 7 điều kiện hóa)",
    "bazi.lenh_clashed": "interact.resolve (bước xung)", "bazi.lenh_penalized": "interact.resolve (bước hình/hại/phá)",
    "bazi.interact_statuses": "interact.resolve", "bazi.geju_inner": "geju.inner_candidates", "bazi.geju_state": "geju.evaluate",
    "bazi.geju_bai": "geju.evaluate", "bazi.geju_outer": "geju.outer_candidates", "bazi.geju_outer_quality": "geju.outer_candidates",
    "bazi.yong_cach_cuc": "yongshen.cach_cuc", "bazi.yong_phu_uc_status": "yongshen.phu_uc", "bazi.method_disagreements": "yongshen.compare",
    "bazi.thong_quan_missing": "yongshen.thong_quan", "bazi.patterns": "patterns.evaluate_all", "bazi.nguyen_luu": "flow.nguyen_luu", "bazi.geju_outer_kind": "geju.outer_candidates", "bazi.dm_strong_tvh": "tvh_score.score", "bazi.dm_share_tvh": "tvh_score.score", "bazi.dm_border_tvh": "tvh_score.score", "bazi.hoa_than_du": "yongshen.thuan_the", "bazi.thuong_quan_style": "yongshen.thuong_quan_dung", "bazi.han_noan_direction": "yongshen.han_noan", "bazi.nguyen_luu_blocked": "flow.nguyen_luu", "bazi.patterns_formed": "patterns.evaluate_all",
    "bazi.patterns_weak": "patterns.evaluate_all", "bazi.patterns_unsaved": "patterns.evaluate_all",
    "bazi.t.effect": "temporal_deep.analyse_extended (so cách nguyên cục với cách trên cục mở rộng)", "bazi.t.event_kinds": "temporal_deep.overlay",
    "bazi.t.opens_kho": "temporal_deep.overlay", "bazi.t.can_chi": "temporal_deep.can_chi_relation", "bazi.t.can_chi_mitigated": "temporal_deep.can_chi_relation",
    "bazi.t.can_chi_aggravated": "temporal_deep.can_chi_relation", "bazi.t.dm_strong": "strength.compute trên cục mở rộng", "bazi.t.dm_weak": "strength.compute trên cục mở rộng", "bazi.t.completes_cuc": "temporal_deep.overlay",
    "bazi.t.role.cach_cuc": "yongshen.run trên cục mở rộng", "bazi.t.role.phu_uc": "yongshen.run trên cục mở rộng", "bazi.t.role.dieu_hau": "yongshen.run trên cục mở rộng", "bazi.climate_label": "season.climate",
}

FACT_VI = {
    "bazi.dm_level": "khí thế Nhật Chủ sau tương tác: {v}", "bazi.dm_level_raw": "khí thế Nhật Chủ trên nguyên cục: {v}",
    "bazi.dm_ambiguous": "khí thế Nhật Chủ nằm sát ranh giới hai mức", "bazi.dm_de_lenh": "Nhật Chủ so với nguyệt lệnh: {v}",
    "bazi.dm_root_grade": "căn của Nhật Chủ: {v}", "bazi.cuc_formed": "các cục hợp/hội đã thành: {v}",
    "bazi.hua_state": "trạng thái hợp can mạnh nhất trong lá số: {v}", "bazi.lenh_clashed": "nguyệt lệnh bị xung kề sát",
    "bazi.lenh_penalized": "nguyệt lệnh bị hình", "bazi.geju_inner": "nội cách theo nguyệt lệnh: {v}", "bazi.geju_state": "trạng thái cách: {v}",
    "bazi.geju_bai": "các điều kiện phá cách: {v}", "bazi.geju_outer": "ngoại cách ứng viên: {v}", "bazi.geju_outer_quality": "chất lượng ngoại cách: {v}",
    "bazi.method_disagreements": "nhóm thập thần các phương pháp dụng thần bất đồng: {v}", "bazi.thong_quan_missing": "có giao chiến thiếu thông quan",
    "bazi.level_changed_by_interaction": "tương tác làm đổi mức khí thế", "bazi.yong_cach_cuc": "dụng thần theo cách cục: {v}",
    "bazi.yong_phu_uc_status": "phù ức: {v}", "bazi.climate_label": "khí hậu thô: {v}", "bazi.interact_statuses": "tương tác đã giải: {v}",
    "bazi.nguyen_luu": "nguyên lưu: {v}", "bazi.nguyen_luu_blocked": "nguyên lưu bị ngăn bởi: {v}",
    "bazi.dm_strong_tvh": "nhật chủ vượng theo quy tắc 40% của Thiệu Vĩ Hoa: {v}", "bazi.dm_share_tvh": "phe mình theo Thiệu Vĩ Hoa chiếm: {v}", "bazi.dm_border_tvh": "phe mình sát ngưỡng 40%",
    "bazi.patterns_formed": "các cấu trúc thập thần đã thành: {v}", "bazi.patterns_weak": "cấu trúc có đủ chữ nhưng không kề: {v}", "bazi.patterns_unsaved": "cấu trúc bệnh/bị phá chưa cứu mạnh: {v}",
    "bazi.t.effect": "tác động của trụ lên cách: {v}", "bazi.t.event_kinds": "tương tác của trụ với nguyên cục: {v}",
    "derived.bazi.can_xet_cuu_ung": "cách đang bại, cần xét cứu ứng",
}


def build(view, R, S0, S1, geju: dict, yong: dict, climate: dict, pats: list | None = None, nl: dict | None = None) -> dict[str, dict]:
    inner = geju["inner"][0] if geju["inner"] else None
    outer = geju["outer"][0] if geju["outer"] else None
    rank = ["chan_hoa", "gia_hoa", "hop_khong_hoa", "tranh_hop", "khong_ke"]
    hua = sorted((r["status"] for r in R.interactions if r["kind"] == "stem_combine" and r.get("status")), key=rank.index)
    lenh_clashed = any(r["kind"] == "branch_clash" and "month.branch" in r["members"] and r["adjacent"] and r.get("status") != "hop_giai_xung" for r in R.interactions)
    lenh_pen = any(r["kind"] in ("branch_penalty", "branch_self_penalty") and "month.branch" in r["members"] and r.get("status") == "co_hieu_luc" for r in R.interactions)
    f = {
        "chart.system": "bat_tu",
        "bazi.dm_level": S1["level"], "bazi.dm_level_raw": S0["level"], "bazi.dm_ambiguous": S1["ambiguous"], "bazi.dm_readings": S1["readings"],
        "bazi.dm_de_lenh": S1["axes"]["de_lenh"], "bazi.dm_root_grade": S1["axes"]["de_dia"],
        "bazi.level_changed_by_interaction": S0["level"] != S1["level"],
        "bazi.cuc_formed": sorted(f"{c['kind'][7:]}:{c['element']}" for c in R.cuc),
        "bazi.hua_state": hua[0] if hua else "khong_co",
        "bazi.lenh_clashed": lenh_clashed, "bazi.lenh_penalized": lenh_pen,
        "bazi.interact_statuses": sorted({f"{r['kind']}:{r['status']}" for r in R.interactions if r.get("status")}),
        "bazi.geju_inner": inner["name"] if inner else "", "bazi.geju_state": inner["state"] if inner else "khong_xac_dinh",
        "bazi.geju_bai": sorted(b["id"] for b in inner["bai"]) if inner else [],
        "bazi.geju_outer": outer["name"] if outer else "", "bazi.geju_outer_quality": outer["quality"] if outer else "",
        "bazi.yong_cach_cuc": yong["methods"]["cach_cuc"].get("yong", []), "bazi.yong_phu_uc_status": yong["methods"]["phu_uc"]["status"],
        "bazi.method_disagreements": [d["group"] for d in yong["comparison"]["disagreements"]],
        "bazi.thong_quan_missing": yong["methods"]["thong_quan"]["status"] == "co_giao_chien" and bool(yong["methods"]["thong_quan"].get("need_elements")),
        "bazi.climate_label": climate["label"],
        "bazi.dm_strong_tvh": (S1.get("tvh") or {}).get("dm_strong"),
        "bazi.dm_share_tvh": (S1.get("tvh") or {}).get("own_share"),
        "bazi.dm_border_tvh": bool(S1.get("tvh")) and S1["ambiguous"],
        "bazi.geju_outer_kind": outer["kind"] if outer else "",
        "bazi.hoa_than_du": (yong["methods"]["thuan_the"].get("hoa_than_du") if yong["methods"]["thuan_the"].get("hoa_than_du") is not None else None),
        "bazi.thuong_quan_style": (yong.get("thuong_quan") or {}).get("style") or "",
        "bazi.han_noan_direction": (yong["methods"]["dieu_hau"].get("han_noan") or {}).get("direction") or "",
        "bazi.nguyen_luu": (nl or {}).get("verdict", "khong_ket_luan"),
        "bazi.nguyen_luu_blocked": (nl or {}).get("blocked_by") or "",
        "bazi.patterns": sorted(f"{p['id']}:{p['state']}" for p in pats or []),
        "bazi.patterns_formed": sorted(p["id"] for p in pats or [] if p["state"] != "co_ten_khong_ke"),
        "bazi.patterns_weak": sorted(p["id"] for p in pats or [] if p["state"] == "co_ten_khong_ke"),
        "bazi.patterns_unsaved": sorted(p["id"] for p in pats or [] if p["state"] in ("co_benh", "co_benh_cuu_yeu", "thanh_bi_pha", "thanh_bi_pha_cuu_yeu", "hon_tap_co_benh")),
    }
    return {"chart": f}


def temporal_facts(entry: dict) -> dict[str, dict]:
    ev = entry["events"]
    roles = {m: (entry["roles"].get(m) or {}).get("stem_role") or "" for m in ("cach_cuc", "phu_uc", "dieu_hau")}
    luck = next((c for c, lab in zip(entry["can_chi"], entry["labels"]) if lab == "luck"), None)
    return {"chart": {"chart.system": "bat_tu", "bazi.t.effect": entry["effect"], "bazi.t.can_chi": luck["relation"] if luck else "", "bazi.t.can_chi_mitigated": bool(luck and luck["mitigated"]),
                      "bazi.t.can_chi_aggravated": bool(luck and luck["aggravated"]), "bazi.t.dm_strong": entry["level_index"] >= 4, "bazi.t.dm_weak": entry["level_index"] <= 2, "bazi.t.event_kinds": entry["event_kinds"],
                      "bazi.t.opens_kho": any(e.get("opens_kho") for e in ev), "bazi.t.completes_cuc": any(e["kind"] in ("branch_triad", "branch_meeting") for e in ev),
                      **{f"bazi.t.role.{m}": r for m, r in roles.items()}}}
