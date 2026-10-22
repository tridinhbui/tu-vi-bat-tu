"""The Phi Hóa graph of a natal chart: 12 palaces x 4 hóa = 48 directed edges  (palace --hóa--> palace holding the transformed star).

FACTS only. Every edge carries its own trace (which stem, which table, which star, where that star sits) so any later inference can cite it.
Terms (Phi Tinh school): cung phát hóa = the palace whose stem flies the hóa; cung nhận hóa = the palace that holds the transformed star;
tự hóa = the two coincide; xung phi = the target is the palace opposite the source."""
from __future__ import annotations

from dataclasses import dataclass, field

from ..ganzhi import STEMS_VI
from ..tuvi import TuViChart
from .tables import HOA, TABLES, stars_for


@dataclass
class Edge:
    src: str                 # cung phát hóa
    dst: str | None          # cung nhận hóa (None if the star is not placed in the chart)
    hoa: str
    star: str
    src_stem: str
    kinds: list[str] = field(default_factory=list)      # tu_hoa | xung_phi | tam_hop | giap | nhi_hop
    trace: str = ""


@dataclass
class PhiGraph:
    table_id: str
    table_status: str
    edges: list[Edge]
    out: dict[str, dict[str, Edge]]                     # src palace -> hoa -> edge
    inc: dict[str, dict[str, list[str]]]                # dst palace -> hoa -> [src palaces]

    def reciprocal(self, hoa_ab: str, hoa_ba: str) -> list[tuple[str, str]]:
        """Pairs (A, B), A != B, with A --hoa_ab--> B and B --hoa_ba--> A. For hoa_ab == hoa_ba each unordered pair is listed once."""
        out = []
        for a, e in ((a, self.out[a][hoa_ab]) for a in self.out):
            b = e.dst
            if b and b != a and self.out[b][hoa_ba].dst == a and (hoa_ab != hoa_ba or a < b):
                out.append((a, b))
        return sorted(out)

    def chain(self, hoa: str, start: str, max_len: int = 12) -> list[str]:
        """Follow `hoa` edges from `start` (A flies hoa to B, B flies hoa to C ...) until a repeat, a self-loop or max_len. Returns palace names."""
        path, seen = [start], {start}
        while len(path) < max_len:
            nxt = self.out[path[-1]][hoa].dst
            if not nxt or nxt in seen:
                break
            path.append(nxt)
            seen.add(nxt)
        return path


def _kinds(chart: TuViChart, src: dict, dst: dict | None) -> list[str]:
    if dst is None:
        return []
    d = (dst["branch_index"] - src["branch_index"]) % 12
    k = []
    if d == 0:
        k.append("tu_hoa")
    if d == 6:
        k.append("xung_phi")
    if d in (4, 8):
        k.append("tam_hop")
    if d in (1, 11):
        k.append("giap")
    if (src["branch_index"] + dst["branch_index"]) % 12 == 1 and d != 0:
        k.append("nhi_hop")
    return k


def build(chart: TuViChart, table_id: str = "tam_hop_vn", stem_override: dict[str, int] | None = None) -> PhiGraph:
    """stem_override: {palace name: stem index} replaces the palace stem (used for đại hạn / lưu layers that fly from another stem)."""
    by_name = {p["name"]: p for p in chart.palaces}
    holder = {}
    for p in chart.palaces:
        for s in p["stars"]:
            holder[s] = p
    edges, out, inc = [], {}, {n: {h: [] for h in HOA} for n in by_name}
    for p in chart.palaces:
        stem = (stem_override or {}).get(p["name"], STEMS_VI.index(p["stem"]))
        out[p["name"]] = {}
        for hoa, star in stars_for(stem, table_id).items():
            q = holder.get(star)
            e = Edge(p["name"], q["name"] if q else None, hoa, star, STEMS_VI[stem], _kinds(chart, p, q))
            e.trace = (f"cung {p['name']} (can {STEMS_VI[stem]}) phát {hoa} → sao {star} (bảng {table_id}: Tứ Hóa tam hợp, chưa xác minh cho Phi Tinh) "
                       + (f"đang ở cung {q['name']} → cung nhận hóa" if q else "không có trong lá số"))
            edges.append(e)
            out[p["name"]][hoa] = e
            if q:
                inc[q["name"]][hoa].append(p["name"])
    return PhiGraph(table_id, TABLES[table_id]["status"], edges, out, inc)
