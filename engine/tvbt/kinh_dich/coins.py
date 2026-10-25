"""Three coins instead of the yarrow stalks (以錢代蓍畫法, 卜筮全書 as printed in 古今圖書集成 博物彙編 藝術典 卷544):

  擲錢一背為單畫 ⚊，二背為拆畫 ⚋，三背為重畫 ○，純字為交畫 ×。自下而上 … 重變為拆，交變為單。

One back (背) = 單, a resting dương line; two backs = 拆, a resting âm line; three backs = 重, a dương line that changes; no back (all 字) =
交, an âm line that changes. With the yarrow values of 筮儀 these are 7, 8, 9 and 6. The toss itself is random and happens in the
browser; the server only receives the faces, so a cast can always be recomputed from what was stored."""
from __future__ import annotations

from .tables import BUSHI, METHODS, cite

COIN_CITE = cite(METHODS, BUSHI, "重變為拆，交變為單", "以錢代蓍畫法")
FACES_CITE = cite(METHODS, BUSHI, "擲錢一背為單畫", "以錢代蓍畫法")
BACKS_TO_VALUE = {1: 7, 2: 8, 3: 9, 0: 6}
VALUE_NAME_BUSHI = {7: "單", 8: "拆", 9: "重", 6: "交"}


def toss_value(faces) -> int:
    """faces: three coins, each 'lung' (背, the back) or 'chu' (字, the side with characters)."""
    faces = list(faces)
    if len(faces) != 3 or set(faces) - {"lung", "chu"}:
        raise ValueError("three faces 'lung' / 'chu' expected")
    return BACKS_TO_VALUE[faces.count("lung")]


def values_from_tosses(tosses) -> list[int]:
    """Six tosses, the first is hào 1 (自下而上)."""
    tosses = list(tosses)
    if len(tosses) != 6:
        raise ValueError("six tosses expected, hào 1 first")
    return [toss_value(t) for t in tosses]
