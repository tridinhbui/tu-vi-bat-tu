"""Every "Cung đối là X (B)" sentence in the analysis must name the palace six branches from the palace it describes
(owner review 2026-10-22: Quan Lộc Dần was printed with "Cung đối là Thiên Di (Thìn)")."""
import random
import re

from tvbt import analysis, bazi, tuvi
from tvbt.calendar_core import BirthInput, normalize
from tvbt.ganzhi import BRANCHES_VI

PAT = re.compile(r"Cung ([A-ZÀ-Ỹ][^\s(]*(?: [A-ZÀ-Ỹ][^\s(]*)?) \(\S+ (\S+)\)[^.]*?\. Cung đối là ([^()]+?) \((\S+)\)")


def charts(n=60, seed=20261022):
    rnd = random.Random(seed)
    yield 2002, 1, 9, 4, 30, "male"
    for _ in range(n):
        yield rnd.randint(1930, 2020), rnd.randint(1, 12), rnd.randint(1, 28), rnd.randint(0, 23), rnd.choice((0, 30)), rnd.choice(("male", "female"))


def test_opposite_palace_named_correctly():
    seen = 0
    for y, m, d, h, mi, g in charts():
        nb = normalize(BirthInput(y, m, d, h, mi, "Asia/Ho_Chi_Minh", g, None, "vn", "split", False))
        tv, bz = tuvi.compute(nb, dignity_school="khao_luan"), bazi.compute(nb)
        names = {p["branch"]: p["name"] for p in tv.palaces}
        text = " ".join(b["text"] for blocks in analysis.analyse(tv, bz).values() for b in blocks)
        for pal, br, opp_name, opp_br in PAT.findall(text):
            seen += 1
            want = BRANCHES_VI[(BRANCHES_VI.index(br) + 6) % 12]
            assert opp_br == want and opp_name == names[want], (y, m, d, h, g, pal, br, opp_name, opp_br)
    assert seen >= 20
