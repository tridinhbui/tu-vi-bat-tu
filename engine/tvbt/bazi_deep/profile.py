"""SchoolProfile: every number, table choice and policy this system picks lives here, named and versioned.
Nothing in a profile is a claim of a classical text unless a person has verified it, so the default profile is `draft`.
Changing the profile changes the output in the named places only (see tests/test_bazi_deep_profile.py)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent.parent / "data" / "bazi_deep"
LEVELS = ["cực nhược", "nhược", "thiên nhược", "trung hòa", "thiên vượng", "vượng", "cực vượng"]


def _tu_lenh() -> dict:
    return json.loads((DATA / "tu_lenh.json").read_text("utf-8"))["tables"]


@dataclass(frozen=True)
class SchoolProfile:
    id: str = "baseline_v1"
    review_status: str = "draft"                    # no weight below is verified against a source text
    # --- khí thế
    use_tu_lenh: bool = True
    tu_lenh_table: str = "common_v1"
    tu_lenh_bonus: float = 0.5                      # extra weight of the commanding stem, as a fraction of the month-branch weight
    pos_weight_stem: dict = field(default_factory=lambda: {"year": 1.0, "month": 1.2, "day": 1.0, "hour": 1.0})
    pos_weight_branch: dict = field(default_factory=lambda: {"year": 1.0, "month": 3.0, "day": 1.8, "hour": 1.2})
    hidden_frac: dict = field(default_factory=lambda: {1: (1.0,), 2: (0.7, 0.3), 3: (0.6, 0.3, 0.1)})
    season_factor: dict = field(default_factory=lambda: {"vượng": 1.5, "tướng": 1.2, "hưu": 1.0, "tù": 0.7, "tử": 0.5})
    dist_factor: dict = field(default_factory=lambda: {0: 1.0, 1: 1.0, 2: 0.7, 3: 0.5})   # pillar distance to the day pillar
    level_cuts: tuple = (0.22, 0.36, 0.46, 0.54, 0.64, 0.78)
    level_margin: float = 0.03                      # closer than this to a cut => two readings
    stage_weight: dict = field(default_factory=lambda: {
        "Trường Sinh": 1.0, "Mộc Dục": 0.5, "Quan Đới": 0.8, "Lâm Quan": 1.0, "Đế Vượng": 1.0, "Suy": 0.6, "Bệnh": 0.4,
        "Tử": 0.3, "Mộ": 0.5, "Tuyệt": 0.1, "Thai": 0.2, "Dưỡng": 0.4})
    class_weight: dict = field(default_factory=lambda: {"ban_khi": 1.0, "trung_khi": 0.6, "du_khi": 0.3})
    kho_policy: str = "can_mo"                      # can_mo: a khố root counts half again until opened by xung/hình | tu_co_can
    # --- tương tác
    active_min: float = 0.6                         # a stem/branch below this multiplier no longer counts as 'present' for cách
    cuc_share: dict = field(default_factory=lambda: {"meeting": 0.6, "triad": 0.6, "semi": 0.35, "cung": 0.15})
    cuc_thau_bonus: float = 0.1
    luhe_mult: float = 0.85
    bound_mult: float = 0.5                         # hợp trói
    gia_hoa_mult: float = 0.6
    tranh_hop_mult: float = 0.7
    clash_adj: tuple = (0.4, 0.85, 0.6)             # weaker, stronger, tie (adjacent clash)
    clash_far: float = 0.85
    stem_clash_adj: float = 0.7
    stem_clash_far: float = 0.9
    penalty_adj: float = 0.9
    penalty_full: float = 0.8
    harm_destroy_adj: float = 0.95
    light_scope: tuple = ("month", "day")           # hình/hại/phá only change strength when they touch these pillars
    hua_requires_adjacent: bool = True
    # --- cách cục
    yin_nhan: bool = False                          # lập Dương Nhận cho âm can
    tong_dominant_share: float = 0.55
    tong_chan_tia: float = 0.08
    tong_gia_tia: float = 0.20
    tong_max_ratio: float = 0.22
    war_share: float = 0.20                         # both elements at least this share of the total => 'giao chiến'
    bridge_min: float = 0.10                        # thông quan element below this share counts as missing
    temporal_weight: dict = field(default_factory=lambda: {"luck": (1.2, 2.0), "year": (1.0, 1.2), "month": (0.6, 0.8)})   # (stem, branch) weight of a temporal pillar
    temporal_clash: float = 0.55                    # multiplier of a natal branch hit by a temporal clash
    interact_order: tuple = ("cuc", "stem_combine", "clash", "xing_hai_po")

    def tu_lenh_rows(self) -> dict:
        return _tu_lenh()[self.tu_lenh_table]

    def with_(self, **kw) -> "SchoolProfile":
        return replace(self, **kw)


DEFAULT = SchoolProfile()
