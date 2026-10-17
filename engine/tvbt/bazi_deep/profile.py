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
    strength_method: str = "he_thong"               # he_thong: tvbt.bazi_deep.strength (weights are this system's, draft) | tvh_40: Thiệu Vĩ Hoa pp.331-355 (verified method)
    tvh_margin: float = 0.03                         # |share - 0.40| below this => the day master is reported as on the border
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
    hua_ignores_tranh_hop: bool = False             # Trích Thiên Tủy p.176: tranh hợp/đố hợp 'là luận điệu hoang đường' khi đã hóa thật
    hua_du_share: float = 0.50                       # hóa thần at least this share of the total => 'có dư' (cần tiết); below => 'không đủ' (cần sinh trợ)
    presence_share: float = 0.05                     # 'có/không có' Tài, Quan Sát, Ấn in a book rule = group share at least/below this
    thuong_vuong: float = 0.30                       # Thực Thương share from which Thương Quan counts as 'vượng'
    tong_cuong_min: float = 0.20                     # Ấn and Tỉ Kiếp each at least this share => Tòng Cường
    tong_vuong_ti: float = 0.55                      # Tỉ Kiếp share from which (with Ấn thin) => Tòng Vượng
    tong_foe_max: float = 0.05                       # Tài+Quan Sát share at most this for Tòng Vượng/Cường
    tong_the_each: float = 0.15                      # each of Tài, Quan Sát, Thực Thương at least this for Tòng Thế
    chuyen_vuong_chars: int = 5                      # 'địa chi có tam hội/tam hợp hóa X hoặc X rất nhiều': at least this many of the 8 characters of element X
    chuyen_vuong_share: float = 0.60                 # hóa khí: the hóa thần takes at least this share of the scored total ('chuyên cục vượng')
    tvh_no_help: float = 0.15                        # 'không có' ngang vai/kiếp/ấn (or thực thương, quan sát) in the tòng definitions of Thiệu Vĩ Hoa
    tvh_tong_main: float = 0.35                      # the group that the day master follows takes at least this share
    flow_min: float = 0.05                           # an element below this share is treated as absent in the nguyên lưu chain
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


TTT_NTT = DEFAULT.with_(id="ttt_ntt_v1", review_status="partially_verified", kho_policy="tu_co_can", tu_lenh_table="ttt_ntt_v1", hua_ignores_tranh_hop=True)
# Trích Thiên Tủy (Nhậm Thiết Tiều): khố/dư khí count as roots without needing xung/hình to open them (PDF p.70, which also says
# hình xung tổn thương căn khí); tranh hợp does not stop a true hóa (p.176); tư lệnh table only for tháng Dần (p.67).
# Numeric weights are still the system's (draft); only the policies above are taken from the book.


TVH_40 = DEFAULT.with_(id="tvh40_v1", review_status="partially_verified", strength_method="tvh_40")
# Thiệu Vĩ Hoa: day-master strength by the degree-scoring method and the 40% rule. Group shares for cách/tòng detection are taken from the same
# scored totals. Sub-bands inside weak/strong (cực nhược…cực vượng) are this system's presentation and draft; only the 40% decision is the book's.
