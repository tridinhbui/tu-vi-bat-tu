"""ChartView: the eight characters of a Bát Tự chart addressed by stable ids ("month.stem", "day.branch"...)."""
from __future__ import annotations

from dataclasses import dataclass

from ..bazi import HIDDEN_STEMS, growth_stage, ten_god
from ..ganzhi import BRANCHES_VI, BRANCH_ELEMENT, STEM_ELEMENT, STEMS_VI

PILLARS = ["year", "month", "day", "hour"]
PIL_VI = {"year": "năm", "month": "tháng", "day": "ngày", "hour": "giờ"}
GOD_GROUPS = {
    "Ti": ("Tỉ Kiên", "Kiếp Tài"), "An": ("Chính Ấn", "Thiên Ấn"), "Tai": ("Chính Tài", "Thiên Tài"),
    "Quan": ("Chính Quan",), "Sat": ("Thất Sát",), "QuanSat": ("Chính Quan", "Thất Sát"),
    "Thuc": ("Thực Thần",), "Thuong": ("Thương Quan",), "ThucThuong": ("Thực Thần", "Thương Quan"),
    "Kieu": ("Thiên Ấn",), "ChinhAn": ("Chính Ấn",), "Kiep": ("Kiếp Tài",),
}
CLASS_NAMES = ["ban_khi", "trung_khi", "du_khi"]


def group_of(god: str) -> str:
    for g in ("Ti", "An", "Tai", "Quan", "Sat", "Thuc", "Thuong"):
        if god in GOD_GROUPS[g]:
            return g
    raise KeyError(god)


def parse_pillar(name: str) -> tuple[int, int]:
    s, b = name.split()
    return STEMS_VI.index(s), BRANCHES_VI.index(b)


@dataclass(frozen=True)
class ChartView:
    stems: tuple[int, int, int, int]       # year, month, day, hour
    branches: tuple[int, int, int, int]
    days_into_month: float | None = None   # days since the latest jie (needed by tư lệnh); None = unknown
    gender: str | None = None

    @classmethod
    def from_names(cls, text: str, days_into_month: float | None = None, gender: str | None = None) -> "ChartView":
        ps = [parse_pillar(p.strip()) for p in text.split("/")]
        if len(ps) != 4:
            raise ValueError("need four pillars separated by '/'")
        for s, b in ps:
            if s % 2 != b % 2:
                raise ValueError(f"invalid stem/branch parity: {STEMS_VI[s]} {BRANCHES_VI[b]}")
        return cls(tuple(p[0] for p in ps), tuple(p[1] for p in ps), days_into_month, gender)

    @classmethod
    def from_bazi(cls, bz, birth_utc=None, gender: str | None = None) -> "ChartView":
        import datetime as dt
        days = None
        if birth_utc is not None:
            prev = dt.datetime.fromisoformat(bz.jie_used["prev_jie_utc"])
            days = (birth_utc - prev).total_seconds() / 86400.0
        k = PILLARS
        return cls(tuple(bz.pillars[x].stem for x in k), tuple(bz.pillars[x].branch for x in k), days, gender)

    # ---- accessors
    def stem(self, p: str) -> int:
        return self.stems[PILLARS.index(p)]

    def branch(self, p: str) -> int:
        return self.branches[PILLARS.index(p)]

    @property
    def dm(self) -> int:
        return self.stems[2]

    @property
    def dm_element(self) -> str:
        return STEM_ELEMENT[self.dm]

    @property
    def month_branch(self) -> int:
        return self.branches[1]

    def name(self) -> str:
        return " / ".join(f"{STEMS_VI[s]} {BRANCHES_VI[b]}" for s, b in zip(self.stems, self.branches))

    def god(self, stem: int) -> str:
        return ten_god(self.dm, stem)

    def hidden(self, p: str) -> list[dict]:
        """Hidden stems of a pillar's branch: [{stem, class, ten_god, element}] main -> residual."""
        return [{"stem": h, "class": CLASS_NAMES[i], "ten_god": self.god(h), "element": STEM_ELEMENT[h], "pillar": p}
                for i, h in enumerate(HIDDEN_STEMS[self.branch(p)])]

    def visible_stems(self, include_day: bool = True) -> list[tuple[str, int]]:
        return [(p, self.stem(p)) for p in PILLARS if include_day or p != "day"]

    def stage(self, stem: int, p: str) -> str:
        return growth_stage(stem, self.branch(p))

    @staticmethod
    def dist(p: str, q: str) -> int:
        return abs(PILLARS.index(p) - PILLARS.index(q))


def char_label(view: ChartView, cid: str) -> str:
    p, kind = cid.split(".")
    return (STEMS_VI[view.stem(p)] if kind == "stem" else BRANCHES_VI[view.branch(p)]) + f" ({PIL_VI[p]})"
