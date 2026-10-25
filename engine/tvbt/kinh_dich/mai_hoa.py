"""Mai Hoa Dịch Số casting and thể / dụng facts, from 梅花易數 (WEB:zh_meihua) only. One function per method of 卷一; no shortcut is
shared between methods unless the book states it once for all (卦以八除, 爻以六除, 互卦起例).

  卦以八除  凡起卦不問數多少 … 過八數即以八數遞除 … 以餘數作卦。如得八數整，即坤卦          -> remainder, 0 = Khôn (8)
  爻以六除  凡起動爻，以重卦總數除六，以餘數作動爻 … 取爻當以時加之                         -> remainder; the book gives no word for an
            exact multiple of 6: it is read as hào 6, the same way 八數整 is Khôn (labelled he_thong)
  互卦起例  以重卦去了初爻及第六爻，以中間四爻分作兩卦 … 乾坤無互，互其變卦
  體用      動者為用，靜者為體 (卷三 變卦式八則)
  先天/後天 先天卦斷吉凶，止以卦論，不甚用《易》之爻辭。後天則用爻辭，兼用卦辭 (卷二 先天後天論); both use the numbers 乾一兌二…坤八

Nothing is interpreted here: relations (sinh, khắc, tỷ hòa) and vượng / suy are facts for the rule pack."""
from __future__ import annotations

from datetime import datetime

from ..ganzhi import BRANCHES_VI
from ..lunar_vn import solar_to_lunar
from .core import flip, hexagram
from .tables import (CONTROLS, DIRECTION_CITE, DIRECTION_NOTE, DIRECTION_TRIGRAM, ELEMENT, ELEMENT_CITE, GENERATES, MEIHUA, MH1, MH2, MH3,
                     SEASON_NOTE, SEASON_OF_MONTH, SEASON_VI, SINH_KHAC_CITE, SUY, SUY_CITE, TIEN_THIEN_CITE, TIEN_THIEN_NUMBER,
                     TRIGRAM_OF_TIEN_THIEN, VUONG, VUONG_CITE, cite, lines_of)

SCHOOL = "mai_hoa"
C_BAT = cite(MEIHUA, MH1, "以餘數作卦。如得八數整，即坤卦，更不必除也。", "卦以八除")
C_LUC = cite(MEIHUA, MH1, "凡起動爻，以重卦總數除六，以餘數作動爻。", "爻以六除")
C_LUC_TIME = cite(MEIHUA, MH1, "取爻當以時加之。", "爻以六除")
C_HO = cite(MEIHUA, MH1, "互卦以重卦去了初爻及第六爻，以中間四爻分作兩卦，看得何卦。", "互卦起例")
C_HO_KC = cite(MEIHUA, MH1, "乾坤無互，互其變卦。", "互卦起例")
C_THE_DUNG = cite(MEIHUA, MH3, "動者為用，靜者為體。", "變卦式八則")
C_TIEN_HAU = cite(MEIHUA, MH2, "先天卦斷吉凶，止以卦論，不甚用《易》之爻辭。後天則用爻辭，兼用卦辭", "先天後天論")
C_HAU_NUMBERS = cite(MEIHUA, MH2, "故占卜起卦，合以此數為用。", "先天後天論")
C_HAU_TIME = cite(MEIHUA, MH2, "故後天起卦定爻必加時而後可。", "先天後天論")
C_TIME = cite(MEIHUA, MH1, "年月日為上卦。年月日加時總數為下卦。又以年月日時總數取爻。", "年月日時起例")
C_TIME_NUM = cite(MEIHUA, MH1, "如子年一數，丑年二數，直至亥年十二數。", "年月日時起例")
C_VAT = cite(MEIHUA, MH1, "凡見有可數之物，即以此數起作上卦，以時數配作下卦。即以卦數並時數總除六取動爻。", "物數占例")
C_AM = cite(MEIHUA, MH1, "凡聞聲音，數得幾數，起作上卦，加時數配作下卦。", "聲音占例")
C_CHU = cite(MEIHUA, MH1, "十一字以上至於百字，皆可起卦。但十一字以上，又不用平仄聲音調之，止用字數。", "一字占至十一字占")
C_CHU_SPLIT = cite(MEIHUA, MH1, "如字數不勻，即少一字為上卦，取天輕清之義，以多一字為下卦，取地重濁之義。", "字占")
C_CHU_HAO = cite(MEIHUA, MH1, "又合二卦總數取爻。", "一字占至十一字占")
C_TRUONG = cite(MEIHUA, MH1, "丈尺之物，以丈數為上卦，尺數為下卦。合丈尺之數取爻。寸數不用。", "丈尺占")
C_XICH = cite(MEIHUA, MH1, "以尺數為上卦，寸數為下卦。合尺寸之數加時取爻。分數不用。", "尺寸占")
C_VAT_PHUONG = cite(MEIHUA, MH1, "後天端法：以物為上卦，方位為下卦，合物卦之數與方卦之數加時數以取動爻。", "物卦起例（端法後天起卦）")

HE_THONG_SIX = "Sách không nói số chia hết cho 6: ở đây lấy hào 6, như 'được tám số chẵn thì là Khôn' của phép chia 8."


def trigram_of_number(n: int) -> str:
    if n < 1:
        raise ValueError("numbers start at 1")
    r = n % 8
    return TRIGRAM_OF_TIEN_THIEN[r or 8]


def moving_of_number(n: int) -> tuple[int, bool]:
    """(hào động, whether the exact-multiple reading was used)."""
    if n < 1:
        raise ValueError("numbers start at 1")
    r = n % 6
    return (r or 6), r == 0


def relation(the: str, other: str) -> str:
    """How another quái stands to the thể: 'ty_hoa', 'sinh_the' (it sinh thể), 'the_sinh' (thể sinh it), 'khac_the' (it khắc thể),
    'the_khac' (thể khắc it)."""
    ea, eb = ELEMENT[the], ELEMENT[other]
    if ea == eb:
        return "ty_hoa"
    if GENERATES[eb] == ea:
        return "sinh_the"
    if GENERATES[ea] == eb:
        return "the_sinh"
    if CONTROLS[eb] == ea:
        return "khac_the"
    return "the_khac"


def strength(trigram: str, month: int) -> str:
    season = SEASON_OF_MONTH[month]
    return "vuong" if trigram in VUONG[season] else ("suy" if trigram in SUY[season] else "binh")


def build(upper: str, lower: str, moving: int, *, method: str, kind: str, steps: list[dict], inputs: dict, cites: list[dict],
          month: int | None = None, notes: list[str] | None = None) -> dict:
    """The cast and its thể / dụng facts. kind: 'tien_thien' (number first) or 'hau_thien' (quái first)."""
    lines = lines_of(upper, lower)
    ban = hexagram(lines)
    bien_lines = flip(lines, [moving])
    bien = hexagram(bien_lines)
    the_pos, dung_pos = ("upper", "lower") if moving <= 3 else ("lower", "upper")
    the, dung = ban[the_pos], ban[dung_pos]
    bien_dung = bien[dung_pos]
    notes = list(notes or [])
    if ban["number"] in (1, 2):
        ho = hexagram(bien_lines[1:4] + bien_lines[2:5])
        ho_from = "bien"
        hcites = [C_HO, C_HO_KC]
    else:
        ho = hexagram(lines[1:4] + lines[2:5])
        ho_from = "ban"
        hcites = [C_HO]
    parts = {"dung": dung, "ho_upper": ho["upper"], "ho_lower": ho["lower"], "bien": bien_dung}
    rel = {k: relation(the, v) for k, v in parts.items()}
    party_the = [k for k, v in parts.items() if k != "dung" and ELEMENT[v] == ELEMENT[the]]
    party_dung = [k for k, v in parts.items() if k != "dung" and ELEMENT[v] == ELEMENT[dung]]
    out = {
        "school": SCHOOL, "method": method, "kind": kind, "inputs": inputs, "steps": steps,
        "upper": upper, "lower": lower, "moving": moving,
        "ban": ban, "bien": bien, "ho": ho, "ho_from": ho_from,
        "the": {"trigram": the, "position": the_pos, "element": ELEMENT[the]},
        "dung": {"trigram": dung, "position": dung_pos, "element": ELEMENT[dung]},
        "bien_dung": {"trigram": bien_dung, "element": ELEMENT[bien_dung]},
        "relations": rel, "party_the": party_the, "party_dung": party_dung,
        "use_hao_text": kind == "hau_thien",
        "cites": cites + hcites + [C_THE_DUNG, ELEMENT_CITE, SINH_KHAC_CITE, C_TIEN_HAU],
        "notes": notes,
    }
    if month is not None:
        out["month"] = month
        out["season"] = SEASON_OF_MONTH[month]
        out["season_vi"] = SEASON_VI[SEASON_OF_MONTH[month]]
        out["strength"] = {k: strength(v, month) for k, v in {"the": the, **parts}.items()}
        out["cites"] += [VUONG_CITE, SUY_CITE]
        out["notes"].append(SEASON_NOTE)
    return out


def _moving(total: int, notes: list[str]) -> int:
    m, exact = moving_of_number(total)
    if exact:
        notes.append(HE_THONG_SIX)
    return m


def r8(n: int) -> str:
    return f"chia 8 dư {n % 8}" if n % 8 else ("chia hết cho 8, lấy 8" if n > 8 else "chưa quá 8, giữ nguyên")


def r6(n: int) -> str:
    return f"chia 6 dư {n % 6}" if n % 6 else ("chia hết cho 6, lấy 6" if n > 6 else "chưa quá 6, giữ nguyên")


def _step(label: str, expr: str, value, result=None) -> dict:
    s = {"label": label, "expr": expr, "value": value}
    if result is not None:
        s["result"] = result
    return s


def by_time(year_branch: int, month: int, day: int, hour_branch: int, *, leap: bool = False) -> dict:
    """年月日時起例. year_branch / hour_branch: 1 = Tý … 12 = Hợi; month, day: lunar."""
    if not (1 <= year_branch <= 12 and 1 <= month <= 12 and 1 <= day <= 30 and 1 <= hour_branch <= 12):
        raise ValueError("year / hour branch 1..12, lunar month 1..12, lunar day 1..30")
    notes: list[str] = []
    s_up = year_branch + month + day
    s_all = s_up + hour_branch
    upper, lower = trigram_of_number(s_up), trigram_of_number(s_all)
    moving = _moving(s_all, notes)
    if leap:
        notes.append("Tháng nhuận: sách không nói, ở đây vẫn lấy số của tháng.")
    steps = [
        _step("Thượng quái", f"năm {year_branch} + tháng {month} + ngày {day} = {s_up}; {s_up} {r8(s_up)}", s_up, upper),
        _step("Hạ quái", f"{s_up} + giờ {hour_branch} = {s_all}; {s_all} {r8(s_all)}", s_all, lower),
        _step("Hào động", f"{s_all} {r6(s_all)}", s_all, moving),
    ]
    inputs = {"year_branch": year_branch, "month": month, "day": day, "hour_branch": hour_branch, "leap": leap}
    return build(upper, lower, moving, method="thoi_gian", kind="tien_thien", steps=steps, inputs=inputs, month=month, notes=notes,
                 cites=[C_TIME, C_TIME_NUM, TIEN_THIEN_CITE, C_BAT, C_LUC])


def hour_branch_of(hour: int) -> int:
    """Clock hour 0..23 -> 1 = Tý (23:00-00:59) … 12 = Hợi."""
    return (hour + 1) // 2 % 12 + 1


def time_inputs(moment: datetime, *, tz_hours: float = 7.0) -> dict:
    """A civil moment in Việt Nam -> the four numbers of by_time.
    Book silent (labelled in the reading): the year is the lunar year (it changes at Tết), and from 23:00 the Tý hour belongs to the next day."""
    from datetime import timedelta
    d = moment.date() + (timedelta(days=1) if moment.hour == 23 else timedelta(0))
    lday, lmonth, lyear, leap = solar_to_lunar(d, tz_hours)
    return {"year_branch": (lyear - 4) % 12 + 1, "month": lmonth, "day": lday, "hour_branch": hour_branch_of(moment.hour), "leap": leap,
            "lunar_year": lyear, "year_branch_vi": BRANCHES_VI[(lyear - 4) % 12], "hour_branch_vi": BRANCHES_VI[hour_branch_of(moment.hour) - 1]}


TIME_NOTE = ("Sách không nói năm đổi lúc nào và giờ Tý thuộc ngày nào: ở đây năm theo âm lịch (đổi vào Tết), "
             "từ 23 giờ là giờ Tý của ngày hôm sau.")


def by_count(count: int, hour_branch: int, *, month: int | None = None) -> dict:
    """物數占例: a number of things seen -> upper; the hour -> lower; both together -> hào động."""
    notes: list[str] = []
    upper, lower = trigram_of_number(count), trigram_of_number(hour_branch)
    total = count + hour_branch
    moving = _moving(total, notes)
    steps = [_step("Thượng quái", f"số vật {count}; {r8(count)}", count, upper),
             _step("Hạ quái", f"giờ {hour_branch}; {r8(hour_branch)}", hour_branch, lower),
             _step("Hào động", f"{count} + {hour_branch} = {total}; {r6(total)}", total, moving)]
    return build(upper, lower, moving, method="vat_so", kind="tien_thien", steps=steps, month=month, notes=notes,
                 inputs={"count": count, "hour_branch": hour_branch}, cites=[C_VAT, TIEN_THIEN_CITE, C_BAT, C_LUC])


def by_sound(count: int, hour_branch: int, *, month: int | None = None) -> dict:
    """聲音占例: the number of sounds -> upper; sounds + hour -> lower; hào động by 爻以六除 (重卦總數, 以時加之): sounds + hour."""
    notes: list[str] = []
    total = count + hour_branch
    upper, lower = trigram_of_number(count), trigram_of_number(total)
    moving = _moving(total, notes)
    steps = [_step("Thượng quái", f"số tiếng {count}; {r8(count)}", count, upper),
             _step("Hạ quái", f"{count} + giờ {hour_branch} = {total}; {r8(total)}", total, lower),
             _step("Hào động", f"{total} {r6(total)}", total, moving)]
    return build(upper, lower, moving, method="thanh_am", kind="tien_thien", steps=steps, month=month, notes=notes,
                 inputs={"count": count, "hour_branch": hour_branch}, cites=[C_AM, TIEN_THIEN_CITE, C_BAT, C_LUC, C_LUC_TIME])


def by_words(n_words: int, *, month: int | None = None) -> dict:
    """字占, 11 chữ trở lên: only the count. Fewer words split by 平仄 tones of Chinese or by strokes, which a Vietnamese text has no
    agreed reading for, so they are not offered. A Vietnamese syllable is taken as one chữ (labelled)."""
    if n_words < 11:
        raise ValueError("phép đếm chữ chỉ dùng từ 11 chữ trở lên")
    notes = ["Một âm tiết tiếng Việt được tính là một chữ."]
    top = n_words // 2
    bottom = n_words - top
    upper, lower = trigram_of_number(top), trigram_of_number(bottom)
    moving = _moving(n_words, notes)
    steps = [_step("Thượng quái", f"nửa trên {top} chữ; {r8(top)}", top, upper),
             _step("Hạ quái", f"nửa dưới {bottom} chữ; {r8(bottom)}", bottom, lower),
             _step("Hào động", f"{top} + {bottom} = {n_words}; {r6(n_words)}", n_words, moving)]
    return build(upper, lower, moving, method="chu", kind="tien_thien", steps=steps, month=month, notes=notes,
                 inputs={"words": n_words}, cites=[C_CHU, C_CHU_SPLIT, C_CHU_HAO, TIEN_THIEN_CITE, C_BAT, C_LUC])


def by_zhang_chi(zhang: int, chi: int, *, month: int | None = None) -> dict:
    """丈尺占: trượng -> upper, thước -> lower, trượng + thước -> hào động (the section names no hour; tấc are not used)."""
    notes: list[str] = []
    total = zhang + chi
    upper, lower = trigram_of_number(zhang), trigram_of_number(chi)
    moving = _moving(total, notes)
    steps = [_step("Thượng quái", f"{zhang} trượng; {r8(zhang)}", zhang, upper),
             _step("Hạ quái", f"{chi} thước; {r8(chi)}", chi, lower),
             _step("Hào động", f"{zhang} + {chi} = {total}; {r6(total)}", total, moving)]
    return build(upper, lower, moving, method="truong_xich", kind="tien_thien", steps=steps, month=month, notes=notes,
                 inputs={"zhang": zhang, "chi": chi}, cites=[C_TRUONG, TIEN_THIEN_CITE, C_BAT, C_LUC])


def by_chi_cun(chi: int, cun: int, hour_branch: int, *, month: int | None = None) -> dict:
    """尺寸占: thước -> upper, tấc -> lower, thước + tấc + giờ -> hào động (phân are not used)."""
    notes: list[str] = []
    total = chi + cun + hour_branch
    upper, lower = trigram_of_number(chi), trigram_of_number(cun)
    moving = _moving(total, notes)
    steps = [_step("Thượng quái", f"{chi} thước; {r8(chi)}", chi, upper),
             _step("Hạ quái", f"{cun} tấc; {r8(cun)}", cun, lower),
             _step("Hào động", f"{chi} + {cun} + giờ {hour_branch} = {total}; {r6(total)}", total, moving)]
    return build(upper, lower, moving, method="xich_thon", kind="tien_thien", steps=steps, month=month, notes=notes,
                 inputs={"chi": chi, "cun": cun, "hour_branch": hour_branch}, cites=[C_XICH, TIEN_THIEN_CITE, C_BAT, C_LUC])


def by_object_direction(object_trigram: str, direction: str, hour_branch: int, *, month: int | None = None) -> dict:
    """物卦起例 (後天端法): the quái of the thing -> upper, the quái of the direction it comes from -> lower, their Tiên Thiên numbers +
    the hour -> hào động. Which quái a thing belongs to is the user's choice from 八卦萬物屬類 (the UI lists the book's classes)."""
    if object_trigram not in TIEN_THIEN_NUMBER or direction not in DIRECTION_TRIGRAM:
        raise ValueError("unknown quái or direction")
    notes = [] if direction in ("nam", "bac", "dong", "tay") else [DIRECTION_NOTE]
    lower = DIRECTION_TRIGRAM[direction]
    a, b = TIEN_THIEN_NUMBER[object_trigram], TIEN_THIEN_NUMBER[lower]
    total = a + b + hour_branch
    moving = _moving(total, notes)
    steps = [_step("Thượng quái", f"vật thuộc {object_trigram} (số {a})", a, object_trigram),
             _step("Hạ quái", f"phương {direction.replace('_', ' ')} thuộc {lower} (số {b})", b, lower),
             _step("Hào động", f"{a} + {b} + giờ {hour_branch} = {total}; {r6(total)}", total, moving)]
    return build(object_trigram, lower, moving, method="vat_phuong", kind="hau_thien", steps=steps, month=month, notes=notes,
                 inputs={"object_trigram": object_trigram, "direction": direction, "hour_branch": hour_branch},
                 cites=[C_VAT_PHUONG, DIRECTION_CITE, C_HAU_NUMBERS, C_HAU_TIME, TIEN_THIEN_CITE, C_LUC])
