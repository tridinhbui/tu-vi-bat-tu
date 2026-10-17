"""Phase 7: why the two KL tr.221 variants of Cơ Nguyệt Đồng Lương say 'thành' on Hạng Võ and Mậu Tý although the book calls both charts failures.
The oracle reconstructs the charts and shows that the book's own cung-by-cung reasoning rests on facts that NO rule of the KL-221 variant (nor TT tr.24) names: Tuần/Triệt sitting on the
stars' palaces, Hỏa/Linh with Kỵ. KL tr.221 is a typology ('may thì làm quan, xui thì công chức ba cọc ba đồng'; 'hội với Tả Hữu Quang Quí... bác sĩ') that gives no breaker: this is a
difference of GENRE inside one book (typology p.221 vs chart commentary pp.238, 246), not a contradiction of the rule."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import control_charts_phase6 as C  # noqa: E402
import oracle_tuvi_independent as O  # noqa: E402

B = O.B


def chart(name):
    c = C.CHARTS[name]
    return O.chart(c["ly"], c["lm"], c["ld"], c["hb"], c["male"])


def test_hang_vo_chart_matches_the_book_commentary_on_pp_238():
    """KL p.238: 'Cung Tài có Đồng Lương ngộ Triệt lại gặp Địa kiếp'; 'Cung Quan có Thái âm đắc địa lại ngộ Tuần'; 'Cung Di có Cự Kỵ'; Hỏa tinh ở Mệnh."""
    o = chart("hang_vo")
    p = o["pos"]
    assert p["Thiên Đồng"] == p["Thiên Lương"] == p["Địa Kiếp"] == B["Dần"] and B["Dần"] in o["triet"]            # Tài: Đồng Lương + Triệt + Địa Kiếp
    assert p["Thái Âm"] == B["Tuất"] and B["Tuất"] in o["tuan"]                                                      # Quan: Thái Âm + Tuần
    assert p["Cự Môn"] == B["Tý"] and o["carriers"]["Hóa Kỵ"] == "Cự Môn" and B["Tý"] == O.roles(o)["opp"]            # Di (đối cung): Cự Môn hóa Kỵ
    assert p["Hỏa Tinh"] == o["menh"] == B["Ngọ"]                                                                    # Hỏa tinh ở Mệnh


def test_mau_ty_chart_matches_the_book_commentary_on_pp_245_246():
    """KL p.246: 'Thiên cơ Hóa kỵ gặp Hỏa Linh'; 'Tử Phá đóng cung Tử tức ngộ Triệt'."""
    o = chart("mau_ty_pha_san")
    p = o["pos"]
    assert p["Thiên Cơ"] == p["Hỏa Tinh"] == p["Linh Tinh"] == B["Tý"] and o["carriers"]["Hóa Kỵ"] == "Thiên Cơ"
    assert B["Tý"] in o["triet"]
    assert p["Tử Vi"] == p["Phá Quân"] == B["Sửu"] and B["Sửu"] in o["triet"] and B["Sửu"] == (o["menh"] + 9) % 12          # Tử Tức palace, on Triệt


def test_what_the_kl_221_variant_can_and_cannot_see_on_these_two_charts():
    """TT tr.24 variant: breakers are Không/Kiếp and Kỵ in the tam phương -> Hạng Võ (Địa Kiếp and Cự Kỵ in tp) and Mậu Tý (Cơ Kỵ in tp) are 'bị phá'.
    KL tr.221 variant: no breaker -> 'thành'. Neither variant has a Tuần/Triệt rule for these stars (TT tr.24 does not list it), which is the book's own main argument on Hạng Võ."""
    spec_tt = O.V()["CACH_X_CO_NGUYET_DONG_LUONG@tt_24"]
    spec_kl = O.V()["CACH_X_CO_NGUYET_DONG_LUONG@kl_221"]
    for name in ("hang_vo", "mau_ty_pha_san"):
        o = chart(name)
        assert O.state(spec_tt, o) == "bi_pha" and O.state(spec_kl, o) in ("thanh", "thanh_thuong") and spec_kl["brk"] == []
        assert "Hóa Kỵ" in O.hoa_at(o, O.tp(o))
    assert not any(f.__code__.co_names and "tuan" in f.__code__.co_names for f in spec_tt["brk"])       # no Tuần/Triệt term in the TT variant's breakers
