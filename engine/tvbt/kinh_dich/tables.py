"""Fixed tables of the Kinh Dịch / Mai Hoa module, each with the passage it is read from.

The 64-quẻ table itself (King Wen number, upper and lower quái) is the one tvbt.ha_lac checked against the Hà Lạc book; the tests
check it again against the 'X下Y上' headers of the zh.wikisource 周易 snapshot (WEB:zh_zhouyi), a source independent of that book.
Everything Mai Hoa uses (Tiên Thiên numbers, ngũ hành, vượng / suy) is from 梅花易數 卷一 (WEB:zh_meihua) and nowhere else: the
Lạc Thư numbers in tvbt.ha_lac belong to Hà Lạc, and 先天後天論 (卷二) rejects them for Mai Hoa."""
from __future__ import annotations

from ..ha_lac import HEXAGRAMS, NUMBER_OF, TRIGRAM_IMAGE, TRIGRAM_LINES

ZHOUYI = "WEB:zh_zhouyi"
MEIHUA = "WEB:zh_meihua"
NTT_WS = "WEB:vi_kinhdich_ntt"
METHODS = "WEB:zh_iching_methods"

MH1 = "梅花易數/卷一"
MH2 = "梅花易數/卷二"
MH3 = "梅花易數/卷三"
NTT_PREFACE = "Kinh Dịch/Những điều nên biết"
HANSHU = "周易函書 (四庫全書本)/約存卷07"
YIJIAN = "啓蒙意見 (四庫全書本)/卷4"
BUSHI = "欽定古今圖書集成/博物彙編/藝術典/第544卷"


def cite(book: str, chapter: str, quote: str, section: str | None = None) -> dict:
    """A pointer the reader's căn cứ panel can show and tests/test_kinh_dich_sources.py checks with tools/book_text.quote_on_page."""
    c = {"book": book, "chapter": chapter, "quote": quote}
    if section:
        c["section"] = section
    return c


TRIGRAMS = ("Kiền", "Đoài", "Ly", "Chấn", "Tốn", "Khảm", "Cấn", "Khôn")
TRIGRAM_HAN = {"Kiền": "乾", "Đoài": "兌", "Ly": "離", "Chấn": "震", "Tốn": "巽", "Khảm": "坎", "Cấn": "艮", "Khôn": "坤"}

# 卷一 周易卦數: 乾，一；兌，二；離，三；震，四；巽，五；坎，六；艮，七；坤，八。
TIEN_THIEN_NUMBER = {t: i + 1 for i, t in enumerate(TRIGRAMS)}
TRIGRAM_OF_TIEN_THIEN = {n: t for t, n in TIEN_THIEN_NUMBER.items()}
TIEN_THIEN_CITE = cite(MEIHUA, MH1, "乾，一；兌，二；離，三；震，四；巽，五；坎，六；艮，七；坤，八。", "周易卦數")

# 卷一 八宮所屬五行: 乾、兌，金；坤、艮，土；震、巽，木；坎，水；離，火。
ELEMENT = {"Kiền": "Kim", "Đoài": "Kim", "Khôn": "Thổ", "Cấn": "Thổ", "Chấn": "Mộc", "Tốn": "Mộc", "Khảm": "Thủy", "Ly": "Hỏa"}
ELEMENT_CITE = cite(MEIHUA, MH1, "乾、兌，金；坤、艮，土；震、巽，木；坎，水；離，火。", "八宮所屬五行")

# 卷一 五行生克
GENERATES = {"Kim": "Thủy", "Thủy": "Mộc", "Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim"}
CONTROLS = {"Kim": "Mộc", "Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim"}
SINH_KHAC_CITE = cite(MEIHUA, MH1, "金生水，水生木，木生火，火生土，土生金；", "五行生克")

# 卷一 卦氣旺 / 卦氣衰. The seasons are named, the months are not: 'season' here is read from the lunar month the cast already uses
# (1-2 xuân, 4-5 hạ, 7-8 thu, 10-11 đông, 3/6/9/12 the four Thổ months 辰未戌丑). That reading is the system's, see SEASON_NOTE.
VUONG = {"xuan": {"Chấn", "Tốn"}, "ha": {"Ly"}, "thu": {"Kiền", "Đoài"}, "dong": {"Khảm"}, "tu_quy": {"Khôn", "Cấn"}}
SUY = {"xuan": {"Khôn", "Cấn"}, "ha": {"Kiền", "Đoài"}, "thu": {"Chấn", "Tốn"}, "dong": {"Ly"}, "tu_quy": {"Khảm"}}
VUONG_CITE = cite(MEIHUA, MH1, "震、巽木旺於春，離火旺于夏，乾、兌金旺於秋，坎水旺於冬，坤、艮土旺於辰戌丑未月。", "卦氣旺")
SUY_CITE = cite(MEIHUA, MH1, "春坤、艮，夏乾、兌，秋震、巽，冬離，辰戌丑未坎。", "卦氣衰")
SEASON_OF_MONTH = {1: "xuan", 2: "xuan", 3: "tu_quy", 4: "ha", 5: "ha", 6: "tu_quy", 7: "thu", 8: "thu", 9: "tu_quy", 10: "dong",
                   11: "dong", 12: "tu_quy"}
SEASON_VI = {"xuan": "mùa xuân", "ha": "mùa hạ", "thu": "mùa thu", "dong": "mùa đông", "tu_quy": "tháng Thìn, Tuất, Sửu, Mùi"}
SEASON_NOTE = ("Sách nói vượng suy theo mùa và theo bốn tháng Thìn, Tuất, Sửu, Mùi, không nói tháng tính theo âm lịch hay theo tiết khí: "
               "ở đây dùng tháng âm lịch đã dùng để lập quẻ, tháng 3, 6, 9, 12 là bốn tháng Thổ.")

# 卷一 象數易理篇之二 八卦方位圖 (後天): 離南坎北，震東兌西 — the four corners are the usual 後天 square (乾 tây bắc, 坤 tây nam, 艮 đông bắc,
# 巽 đông nam); the book's figure is not in the Wikisource text, so only the four sides are quoted.
DIRECTION_TRIGRAM = {"nam": "Ly", "bac": "Khảm", "dong": "Chấn", "tay": "Đoài", "tay_bac": "Kiền", "tay_nam": "Khôn", "dong_bac": "Cấn",
                     "dong_nam": "Tốn"}
DIRECTION_CITE = cite(MEIHUA, MH1, "離南坎北，震東兌西", "八卦方位圖")
DIRECTION_NOTE = ("Bản Wikisource chỉ có câu 'Ly nam, Khảm bắc, Chấn đông, Đoài tây'; bốn góc (Kiền tây bắc, Khôn tây nam, Cấn đông bắc, "
                  "Tốn đông nam) theo hình Hậu thiên thông dụng, hình vẽ của sách không có trong bản chép.")

# 64 quẻ: King Wen number -> Hán name (order of the 周易 page in WEB:zh_zhouyi)
HAN_NAMES = ("乾 坤 屯 蒙 需 訟 師 比 小畜 履 泰 否 同人 大有 謙 豫 隨 蠱 臨 觀 噬嗑 賁 剝 復 无妄 大畜 頤 大過 坎 離 "
             "咸 恒 遯 大壯 晉 明夷 家人 睽 蹇 解 損 益 夬 姤 萃 升 困 井 革 鼎 震 艮 漸 歸妹 豐 旅 巽 兌 渙 節 中孚 小過 既濟 未濟").split()
HEX_HAN = {i + 1: n for i, n in enumerate(HAN_NAMES)}

# Positions (NTT preface 'Những điều nên biết'): Đầu, Hai, Ba, Tư, Năm, Trên; the Hán names 初 二 三 四 五 上 with 九 / 六
POSITION_VI = ("Đầu", "Hai", "Ba", "Tư", "Năm", "Trên")
POSITION_HAN = ("初", "二", "三", "四", "五", "上")
NUMBER_HV = {"九": "Cửu", "六": "Lục"}
POSITION_HV = ("Sơ", "Nhị", "Tam", "Tứ", "Ngũ", "Thượng")
# NTT preface: 'hào Đầu là ngôi thứ dân, hào Hai là ngôi tư mục, hào Ba là ngôi quan Khanh, quan Đại phu, hào Tư là ngôi đại thần, hào Năm là
# ngôi vua, hào Trên là ngôi các vị lão thành. Đấy cũng là nói đại khái mà thôi'
RANK = ("thứ dân", "tư mục", "quan Khanh, quan Đại phu", "đại thần", "vua", "các vị lão thành")
RANK_CITE = cite(NTT_WS, NTT_PREFACE, "hào Đầu là ngôi thứ dân, hào Hai là ngôi tư mục")
CHINH_CITE = cite(NTT_WS, NTT_PREFACE, "Hào Dương mà ở ngôi lẻ, tức là ngôi Đầu, ngôi Ba, ngôi Năm; hào Âm mà ở ngôi chẵn")
TRUNG_CITE = cite(NTT_WS, NTT_PREFACE, "Trong mỗi quẻ, chỉ có hào Hai hào Năm là giữa")
UNG_CITE = cite(NTT_WS, NTT_PREFACE, "hào Đầu ứng với hào Tư, hào Hai ứng với hào Năm, hào Ba ứng với hào Trên")
UNG_POLARITY_CITE = cite(NTT_WS, NTT_PREFACE, "Nhưng phải một hào là Dương, một hào là Âm, mới là có ứng")
# Line values (筮儀, NTT 'Phép bói bằng cỏ thi'; the preface of quẻ Kiền: 'số Chín là Dương già, số Bảy là Dương trẻ, số Sáu là Âm già, số
# Tám là Âm trẻ, già biến đổi mà trẻ thì không biến đổi')
VALUE_NAME = {6: "lão âm", 7: "thiếu dương", 8: "thiếu âm", 9: "lão dương"}
VALUE_CITE = cite(NTT_WS, "Kinh Dịch/Chu Dịch thượng kinh/Quẻ Kiền", "già biến đổi mà trẻ thì không biến đổi")


def lines_of(upper: str, lower: str) -> tuple[int, ...]:
    return TRIGRAM_LINES[lower] + TRIGRAM_LINES[upper]


def hexagram_of(upper: str, lower: str) -> dict:
    n = NUMBER_OF[(upper, lower)]
    name = HEXAGRAMS[n][0]
    full = f"Thuần {name}" if upper == lower else f"{TRIGRAM_IMAGE[upper]} {TRIGRAM_IMAGE[lower]} {name}"
    return {"number": n, "name": name, "han": HEX_HAN[n], "full_name": full, "upper": upper, "lower": lower,
            "lines": list(lines_of(upper, lower))}
