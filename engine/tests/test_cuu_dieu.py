"""Cửu diệu: the four worked examples printed on pp.271-272 and the printed table rows."""
from tvbt import cuu_dieu as cd


def test_book_examples():
    assert cd.star_for(26, "male")["star"] == "Thái Âm" and cd.star_for(26, "female")["star"] == "Thái Bạch"
    assert cd.star_for(54, "male")["star"] == "Mộc Đức" and cd.star_for(54, "female")["star"] == "Thủy Diệu"
    assert cd.digit_of(56) == 2                                   # 5+6=11 -> 1+1=2 (p.272)


def test_printed_table_rows_and_cycle():
    rows = {1: ("La Hầu", 6), 2: ("Thổ Tú", 5), 3: ("Thủy Diệu", 9), 4: ("Thái Bạch", 8), 5: ("Thái Dương", 7), 6: ("Vân Hán", 2), 7: ("Kế Đô", 1), 8: ("Thái Âm", 4), 9: ("Mộc Đức", 3)}
    for d, (star, nu) in rows.items():
        assert cd.NAM[d] == star and cd.NU_DIGIT[star] == nu
    assert sorted(cd.NU) == list(range(1, 10)) and len(set(cd.NU.values())) == 9
    assert [cd.digit_of(a) for a in (1, 9, 10, 18, 19, 99)] == [1, 9, 1, 9, 1, 9]
    assert all(cd.star_for(a, g)["star"] in cd.INFO for a in range(1, 100) for g in ("male", "female"))
