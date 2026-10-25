#!/usr/bin/env python3
"""Build engine/data/mai_hoa/rules_extract.json from the hand-written rule list
below. Every han_quote is checked to be an exact substring of its section's
`text` in source_zh.json before anything is written.

    python tools/mai_hoa_rules_build.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "engine" / "data" / "mai_hoa" / "source_zh.json"
OUT = ROOT / "engine" / "data" / "mai_hoa" / "rules_extract.json"

TT = {"乾": 1, "兌": 2, "離": 3, "震": 4, "巽": 5, "坎": 6, "艮": 7, "坤": 8}

SINH_THE_VI = {
    "乾": "Quái Càn sinh thể thì chủ ở chốn công môn có mừng, có ích; hoặc có mừng về công danh; hoặc nhờ quan mà có tài; hoặc hỏi kiện thì được lý; hoặc có lợi về vàng bạc châu báu; hoặc có người già đem tài đến; hoặc bậc tôn trưởng ban tặng; hoặc có mừng về quan quý.",
    "坤": "Quái Khôn sinh thể thì chủ có mừng về ruộng đất; hoặc nhờ ruộng đất mà vào tài; hoặc được người làng giúp ích; hoặc được lợi từ âm nhân (người nữ); hoặc có lợi về quả, lúa; hoặc có mừng về vải lụa.",
    "震": "Quái Chấn sinh thể thì chủ được ích về núi rừng; hoặc nhờ núi rừng mà được tài; hoặc vào tài từ phương đông; hoặc nhân trong lúc động mà có mừng; hoặc có lợi buôn bán hàng gỗ; hoặc nhờ người họ có bộ thảo, mộc mà vừa lòng.",
    "巽": "Quái Tốn sinh thể cũng chủ được ích về núi rừng; hoặc nhờ núi rừng mà được tài; hoặc được tài ở phương đông nam; hoặc nhờ người họ có bộ thảo, mộc mà vào lợi; hoặc nhờ chè, quả mà được lợi; hoặc có mừng về chè, quả, rau dưa.",
    "坎": "Quái Khảm sinh thể thì có mừng ở phương bắc; hoặc nhận tài từ phương bắc; hoặc người ở ven nước đem lợi đến; hoặc nhờ người họ có bộ thủy (chấm thủy) mà vừa lòng; hoặc có lợi buôn bán cá, muối, rượu, giấy tờ; hoặc có mừng được biếu cá, muối, rượu.",
    "離": "Quái Ly sinh thể thì chủ có tài ở phương nam; hoặc có mừng về giấy tờ; hoặc có lợi về lò rèn, lò đúc; hoặc nhờ người họ có bộ hỏa mà được tài.",
    "艮": "Quái Cấn sinh thể thì có tài ở phương đông bắc; hoặc có mừng về ruộng núi; hoặc nhờ núi rừng, ruộng đất mà được tài; hoặc được tài của người âm cung, họ có bộ thổ. Vật thì yên ổn, việc thì có đầu có cuối.",
    "兌": "Quái Đoài sinh thể thì có tài ở phương tây; hoặc có việc vui mừng; hoặc có nguồn lợi về đồ ăn, vàng ngọc, hàng hóa; hoặc người âm thương; hoặc vui gặp người họ có bộ khẩu; hoặc có niềm vui chủ khách; hoặc có việc bạn bè cùng giảng tập.",
}
KHAC_THE_VI = {
    "乾": "Như quái Càn khắc thể thì chủ có lo về việc công; hoặc lo về môn hộ; hoặc mất của cải châu báu; hoặc tổn hại về vàng, lúa; hoặc làm bậc tôn trưởng nổi giận; hoặc đắc tội với quý nhân.",
    "坤": "Quái Khôn khắc thể thì chủ có lo về ruộng đất; hoặc tổn hại về ruộng đất; hoặc bị âm nhân (người nữ) xâm hại; hoặc bị tiểu nhân làm hại; hoặc mất tài về vải lụa; hoặc mất cái lợi về lúa thóc.",
    "震": "Quái Chấn khắc thể thì chủ có hư kinh (sợ hãi hão), thường nhiều lo sợ; hoặc thân tâm không yên được; hoặc nhà cửa thấy yêu tai; hoặc người họ có bộ thảo, mộc xâm phạm; hoặc mất mát về núi rừng.",
    "巽": "Quái Tốn khắc thể cũng có người họ có bộ thảo, mộc làm hại; hoặc sinh lo về núi rừng. Mưu việc thì [kẻ hại] là người phương đông nam;\nỞ nhà thì kỵ tai ách của âm nhân, trẻ nhỏ.",
    "坎": "Quái Khảm khắc thể thì chủ có việc hiểm hãm; hoặc lo giặc cướp; hoặc thất ý với người ở ven nước; hoặc sinh tai họa sau khi uống rượu; hoặc người họ có bộ thủy làm hại; hoặc người phương bắc gây vạ.",
    "離": "Quái Ly khắc thể thì chủ lo về giấy tờ; hoặc sợ hãi vì cháy nhà; hoặc có lo ở phương nam; hoặc người họ có bộ hỏa làm hại.",
    "艮": "Quái Cấn khắc thể thì mọi việc phần nhiều trái ý, trăm mưu nửa chừng bị trở. Hoặc mất mát về núi rừng, ruộng đất; hoặc người họ có bộ thổ xâm phạm; phòng tai họa ở phương đông bắc; hoặc lo mồ mả đặt không đúng.",
    "兌": "Quái Đoài khắc thể thì bất lợi ở phương tây, chủ có tranh cãi khẩu thiệt. Hoặc người họ có bộ khẩu lấn hiếp; hoặc có nạn gãy vỡ; hoặc vì ăn uống mà sinh lo.",
}

REL_KEYS = ("the_khac_dung", "dung_khac_the", "the_sinh_dung", "dung_sinh_the", "ty_hoa")
REL_MARKERS = [("the_khac_dung", "體克用"), ("dung_khac_the", "用克體"), ("the_sinh_dung", "體生用"),
               ("dung_sinh_the", "用生體"), ("ty_hoa", "體用比和")]
# Rules whose wording does not use the standard markers.
REL_HAN_OVERRIDE = {
    "p.vat_sinh_khac": {"dung_sinh_the": "生體者，為可食之物", "dung_khac_the": "克體者，為可近人之穢物",
                        "the_sinh_dung": "體生者，為不成之器", "the_khac_dung": "體克者，為破碎損折之物",
                        "ty_hoa": "比和者，乃有用成器之物"},
}
REL_VI = {
    "t.five_relations": {"the_khac_dung": "thể khắc dụng thì mọi việc cát", "dung_khac_the": "dụng khắc thể thì mọi việc hung",
                         "the_sinh_dung": "thể sinh dụng thì có lo hao mất", "dung_sinh_the": "dụng sinh thể thì có mừng tăng ích",
                         "ty_hoa": "thể dụng tỷ hòa thì trăm việc thuận"},
    "p.nhan_su": {"the_khac_dung": "thể khắc dụng thì cát", "dung_khac_the": "dụng khắc thể thì không nên",
                  "the_sinh_dung": "thể sinh dụng thì có lo hao mất", "dung_sinh_the": "dụng sinh thể thì có mừng tăng ích",
                  "ty_hoa": "thể dụng tỷ hòa thì mưu tính cát lợi"},
    "p.gia_trach": {"the_khac_dung": "thể khắc dụng thì nhà cửa nhiều cát", "dung_khac_the": "dụng khắc thể thì nhà cửa nhiều hung",
                    "the_sinh_dung": "thể sinh dụng thì nhiều hao tán, hoặc phải phòng lo mất trộm",
                    "dung_sinh_the": "dụng sinh thể thì nhiều tăng ích, hoặc có mừng được biếu tặng",
                    "ty_hoa": "thể dụng tỷ hòa thì nhà cửa yên ổn"},
    "p.oc_xa": {"the_khac_dung": "thể khắc dụng thì ở nhà ấy cát", "dung_khac_the": "dụng khắc thể thì ở nhà ấy hung",
                "the_sinh_dung": "thể sinh dụng thì chủ của cải sút giảm", "dung_sinh_the": "dụng sinh thể thì môn hộ hưng thịnh",
                "ty_hoa": "thể dụng tỷ hòa thì tự nhiên yên ổn"},
    "p.hon_nhan": {"the_khac_dung": "thể khắc dụng thì thành được nhưng thành chậm", "dung_khac_the": "dụng khắc thể thì không thành, thành cũng có hại",
                   "the_sinh_dung": "thể sinh dụng thì hôn sự khó thành, hoặc vì hôn sự mà mất",
                   "dung_sinh_the": "dụng sinh thể thì hôn sự dễ thành, hoặc nhờ hôn sự mà được",
                   "ty_hoa": "thể dụng tỷ hòa thì hôn nhân cát lợi"},
    "p.sinh_san": {"the_khac_dung": "thể khắc dụng thì bất lợi cho con", "dung_khac_the": "dụng khắc thể thì bất lợi cho mẹ",
                   "the_sinh_dung": "thể sinh dụng thì lợi cho con", "dung_sinh_the": "dụng sinh thể thì lợi cho mẹ",
                   "ty_hoa": "thể dụng tỷ hòa thì sinh nở thuận nhanh"},
    "p.am_thuc": {"the_khac_dung": "thể khắc dụng thì ăn uống có trở ngại", "dung_khac_the": "dụng khắc thể thì tất không có ăn uống",
                  "the_sinh_dung": "thể sinh dụng thì ăn uống khó được", "dung_sinh_the": "dụng sinh thể thì ăn uống tất đầy đủ",
                  "ty_hoa": "thể dụng tỷ hòa thì ăn uống no đủ"},
    "p.cau_muu": {"the_khac_dung": "thể khắc dụng thì mưu tuy thành được nhưng thành chậm", "dung_khac_the": "dụng khắc thể thì cầu mưu không thành, mưu còn có hại",
                  "the_sinh_dung": "thể sinh dụng thì mưu nhiều mà ít được", "dung_sinh_the": "dụng sinh thể thì không mưu mà thành",
                  "ty_hoa": "thể dụng tỷ hòa thì cầu mưu vừa ý"},
    "p.cau_danh": {"the_khac_dung": "thể khắc dụng thì danh thành được nhưng thành chậm", "dung_khac_the": "dụng khắc thể thì danh không thành",
                   "the_sinh_dung": "thể sinh dụng thì danh không đạt, hoặc vì danh mà mất",
                   "dung_sinh_the": "dụng sinh thể thì danh dễ thành, hoặc nhờ danh mà được",
                   "ty_hoa": "thể dụng tỷ hòa thì công danh vừa ý"},
    "p.cau_tai": {"the_khac_dung": "thể khắc dụng thì có tài", "dung_khac_the": "dụng khắc thể thì không có tài",
                  "the_sinh_dung": "thể sinh dụng thì tài có lo hao tổn", "dung_sinh_the": "dụng sinh thể thì tài có mừng tăng ích",
                  "ty_hoa": "thể dụng tỷ hòa thì tài lợi vừa ý"},
    "p.giao_dich": {"the_khac_dung": "thể khắc dụng thì có tài", "dung_khac_the": "dụng khắc thể thì không thành",
                    "the_sinh_dung": "thể sinh dụng thì khó thành, hoặc vì giao dịch mà mất",
                    "dung_sinh_the": "dụng sinh thể thì thành ngay, thành tất có tài", "ty_hoa": "thể dụng tỷ hòa thì dễ thành"},
    "p.xuat_hanh": {"the_khac_dung": "thể khắc dụng thì đi được, đến đâu phần nhiều đắc ý", "dung_khac_the": "dụng khắc thể thì ra đi có họa",
                    "the_sinh_dung": "thể sinh dụng thì ra đi bị hao tổn", "dung_sinh_the": "dụng sinh thể thì có của bất ngờ",
                    "ty_hoa": "thể dụng tỷ hòa thì ra đi thuận nhanh"},
    "p.hanh_nhan": {"the_khac_dung": "thể khắc dụng thì người đi về chậm", "dung_khac_the": "dụng khắc thể thì người đi không về",
                    "the_sinh_dung": "thể sinh dụng thì người đi chưa về", "dung_sinh_the": "dụng sinh thể thì người đi về ngay",
                    "ty_hoa": "thể dụng tỷ hòa thì chẳng mấy ngày là về"},
    "p.yet_kien": {"the_khac_dung": "thể khắc dụng thì gặp được", "dung_khac_the": "dụng khắc thể thì không gặp",
                   "the_sinh_dung": "thể sinh dụng thì khó gặp, gặp cũng vô ích", "dung_sinh_the": "dụng sinh thể thì gặp được, gặp lại có được",
                   "ty_hoa": "thể dụng tỷ hòa thì vui vẻ gặp nhau"},
    "p.that_vat": {"the_khac_dung": "thể khắc dụng thì tìm được nhưng được chậm", "dung_khac_the": "dụng khắc thể thì không tìm được",
                   "the_sinh_dung": "thể sinh dụng thì vật khó thấy", "dung_sinh_the": "dụng sinh thể thì vật dễ tìm",
                   "ty_hoa": "thể dụng tỷ hòa thì vật không mất"},
    "p.tat_benh": {"the_khac_dung": "thể khắc dụng thì bệnh dễ yên", "the_sinh_dung": "thể sinh dụng thì bệnh khó khỏi"},
    "p.tat_benh_2": {"the_khac_dung": "thể khắc dụng thì không cần thuốc cũng có mừng", "dung_khac_the": "dụng khắc thể thì tuy có thuốc cũng vô công",
                     "the_sinh_dung": "thể sinh dụng thì kéo dài khó khỏi", "dung_sinh_the": "dụng sinh thể thì khỏi ngay",
                     "ty_hoa": "thể dụng tỷ hòa thì bệnh dễ yên"},
    "p.quan_tung": {"the_khac_dung": "thể khắc dụng thì mình thắng người", "dung_khac_the": "dụng khắc thể thì người thắng mình",
                    "the_sinh_dung": "thể sinh dụng thì chẳng những mất lý, hoặc còn vì việc quan mà mất mát",
                    "dung_sinh_the": "dụng sinh thể thì chẳng những được lý, hoặc còn nhờ kiện mà được",
                    "ty_hoa": "thể dụng tỷ hòa thì kiện tụng tốt nhất"},
    "p.phan_mo": {"the_khac_dung": "thể khắc dụng thì táng ở đó cát", "dung_khac_the": "dụng khắc thể thì táng ở đó hung",
                  "the_sinh_dung": "thể sinh dụng thì táng ở đó chủ vận lui", "dung_sinh_the": "dụng sinh thể thì táng ở đó chủ hưng thịnh, có phúc ấm cho con cháu",
                  "ty_hoa": "thể dụng tỷ hòa thì là đất tốt"},
    "p.vat_sinh_khac": {"dung_sinh_the": "quái sinh thể là vật ăn được", "dung_khac_the": "quái khắc thể là vật dơ gần người",
                        "the_sinh_dung": "quái thể sinh là đồ chưa thành", "the_khac_dung": "quái thể khắc là vật vỡ nát, gãy hỏng",
                        "ty_hoa": "tỷ hòa là đồ đã thành, dùng được"},
}


def split_relations(rid: str, han: str) -> dict:
    """Exact Hán clause for each of the five relations present in han, cut from the
    relation marker to the next marker or the clause end (；/。)."""
    if rid in REL_HAN_OVERRIDE:
        return dict(REL_HAN_OVERRIDE[rid])
    pos = {}
    for key, marker in REL_MARKERS:
        i = han.find(marker)
        if i >= 0:
            pos[key] = i
    starts = sorted(pos.values())
    out = {}
    for key, i in pos.items():
        nxt = [p for p in starts if p > i]
        seg = han[i:min(nxt) if nxt else len(han)]
        m = re.search(r"[；。]", seg[5:])  # a marker is 3–4 characters; skip a stray 。 right after it
        if m:
            seg = seg[:5 + m.start()]
        out[key] = seg.rstrip("，；。")
    return {k: out[k] for k in REL_KEYS if k in out}

# (id, section, kind, han_quote, vi, formula|None, flags|None)
R: list[tuple] = []


def rule(id, section, kind, han, vi, formula=None, flags=None):
    R.append((id, section, kind, han, vi, formula, flags))


# ---------------------------------------------------------------- casting ---
rule("c.tien_thien_so", "k1.1.1", "casting",
     "乾，一；兌，二；離，三；震，四；巽，五；坎，六；艮，七；坤，八。",
     "Số của quái: Càn 1, Đoài 2, Ly 3, Chấn 4, Tốn 5, Khảm 6, Cấn 7, Khôn 8.",
     {"number_of": TT})
rule("c.reject_lac_thu", "k2.1.4", "casting",
     "今人多以坎一、坤二、震三、巽四、中五、乾六、兌七、艮八、離九之數為用。蓋聖人作《易》畫卦，始乙太極、兩儀、四象、八卦加一倍，數自成乾一、兌二、離三、震四、巽五、坎六、艮七、坤八。故占卜起卦，合以此數為用。",
     "Người nay phần nhiều dùng số Khảm 1, Khôn 2 … Ly 9 (Lạc Thư); nhưng theo thứ tự thánh nhân vạch quái thì số tự thành Càn 1 … Khôn 8, nên lập quẻ phải dùng số ấy.",
     {"use": "tien_thien_so", "reject": {"坎": 1, "坤": 2, "震": 3, "巽": 4, "中": 5, "乾": 6, "兌": 7, "艮": 8, "離": 9}})
rule("c.trigram_lines", "k1.1.8", "casting",
     "乾三連，坤六斷，震仰盂，艮覆碗，離中虛，坎中滿，兌上缺，巽下斷。",
     "Hình quái: Càn ba vạch liền, Khôn sáu đoạn đứt, Chấn ngửa chén, Cấn úp bát, Ly giữa rỗng, Khảm giữa đầy, Đoài trên khuyết, Tốn dưới đứt.",
     {"lines_bottom_up": {"乾": "111", "坤": "000", "震": "100", "艮": "001", "離": "101", "坎": "010", "兌": "110", "巽": "011"},
      "note": "1 = dương, 0 = âm, read from the bottom line up; derived from the shape words (仰盂 = solid bottom, 覆碗 = solid top, 上缺 = broken top, 下斷 = broken bottom)."})
rule("c.gua_mod8", "k1.1.11", "casting",
     "凡起卦不問數多少，即以此數作卦數，過八數即以八數遞除。一八除不盡，再除二八，三八，直至除盡，以餘數作卦。如得八數整，即坤卦，更不必除也。",
     "Lập quái không kể số nhiều ít; quá tám thì trừ dần từng tám, lấy số dư làm quái. Được đúng tám thì là Khôn, không cần trừ.",
     {"trigram": "n mod 8 → tien_thien_so; remainder 0 → 坤 (8)"},
     ["U-trigram-multiple-of-8"])
rule("c.yao_mod6", "k1.1.12", "casting",
     "凡起動爻，以重卦總數除六，以餘數作動爻。如不滿六，止用此數為動爻，不必再除。如過六數，則除之一六，不盡再除二六、三六，直至除盡，以餘數作動爻。",
     "Tìm hào động: lấy tổng số của trùng quái chia sáu, số dư là hào động. Chưa đủ sáu thì dùng ngay số ấy; quá sáu thì trừ dần từng sáu.",
     {"moving_line": "total mod 6 (1 = bottom line); total < 6 → total"},
     ["U-line-zero"])
rule("c.yao_flip", "k1.1.12", "casting",
     "若一爻動，則看此一爻，是陽爻則變陰爻，陰爻則變陽爻。",
     "Một hào động: hào dương thì biến thành âm, hào âm biến thành dương.",
     {"bian": "flip the moving line of the original hexagram"})
rule("c.yao_add_hour", "k1.1.12", "casting",
     "取爻當以時加之。",
     "Lấy hào thì phải cộng thêm số giờ.",
     {"moving_line_total_includes": "hour_number"},
     ["U-zi-hour", "U-sheng-yin-lower"])
rule("c.hu", "k1.1.13", "casting",
     "互卦只用八卦，不必取六十四卦名。互卦以重卦去了初爻及第六爻，以中間四爻分作兩卦，看得何卦。",
     "Hỗ quái chỉ dùng tám quái, không lấy tên quẻ sáu mươi bốn: bỏ hào sơ và hào sáu, lấy bốn hào giữa chia làm hai quái.",
     {"hu_lower": "lines 2-4", "hu_upper": "lines 3-5",
      "note": "The text only says 'split the middle four lines into two trigrams'; that they overlap as 2–4 and 3–5 is fixed by every worked example (觀梅: 革 → 互 乾 巽)."})
rule("c.hu_qian_kun", "k1.1.13", "casting",
     "又云：乾坤無互，互其變卦。",
     "Lại nói: Càn Khôn không có hỗ, thì lấy hỗ của quẻ biến.",
     {"if_hexagram_in": ["乾為天", "坤為地"], "hu_from": "bian"},
     ["U-hu-qian-kun", "U-hu-source"])
rule("c.nam_thang_ngay_gio", "k1.1.14", "casting",
     "年月日為上卦。年月日加時總數為下卦。又以年月日時總數取爻。如子年一數，丑年二數，直至亥年十二數。月如正月一數，直至十二月，亦作十二數。日數如初一一數，直至三十日，為三十數。",
     "Năm + tháng + ngày làm thượng quái; năm + tháng + ngày + giờ làm hạ quái; tổng năm tháng ngày giờ lấy hào. Năm Tý là 1 … năm Hợi 12; tháng Giêng 1 … tháng mười hai 12; ngày mồng một 1 … ngày ba mươi 30.",
     {"Y": "year branch number 子1…亥12", "M": "month 1…12", "D": "day 1…30", "H": "hour branch number 子1…亥12",
      "upper": "(Y+M+D) mod 8", "lower": "(Y+M+D+H) mod 8", "moving_line": "(Y+M+D+H) mod 6"},
     ["U-leap-month", "U-year-boundary", "U-hour-boundary"])
rule("c.nam_thang_ngay_gio_hour", "k1.1.14", "casting",
     "如子時一數直至亥時十二數，就將年月日數加時之數，總計幾數，以八除之，餘數作下卦；以六除，餘數作動爻。",
     "Giờ Tý 1 … giờ Hợi 12; cộng số năm tháng ngày với số giờ, chia tám lấy dư làm hạ quái, chia sáu lấy dư làm hào động.",
     {"H": {"子": 1, "丑": 2, "寅": 3, "卯": 4, "辰": 5, "巳": 6, "午": 7, "未": 8, "申": 9, "酉": 10, "戌": 11, "亥": 12}},
     ["U-hour-boundary"])
rule("c.appendix_tien_thien", "k0.3", "casting",
     "年以子年起一數，年有十二月，則以正月起一數，月有三十日，則以初一起一數，日有十二時，則以子時起一數",
     "(Phụ lục, lời Quý Bản) năm khởi số 1 từ năm Tý, tháng khởi 1 từ tháng Giêng, ngày khởi 1 từ mồng một, giờ khởi 1 từ giờ Tý.",
     None, ["appendix"])
rule("c.appendix_can_chi", "k0.3", "casting",
     "又如十幹則以甲起一數，十二支則以子起一數",
     "(Phụ lục) mười can thì khởi 1 từ Giáp, mười hai chi khởi 1 từ Tý.",
     {"stem_number": "甲1…癸10", "branch_number": "子1…亥12"}, ["appendix"])
rule("c.vat_so", "k1.1.15", "casting",
     "凡見有可數之物，即以此數起作上卦，以時數配作下卦。即以卦數並時數總除六取動爻。",
     "Thấy vật đếm được thì lấy số ấy làm thượng quái, lấy số giờ làm hạ quái; lấy số quái cộng số giờ chia sáu lấy hào động.",
     {"upper": "count mod 8", "lower": "hour_number mod 8", "moving_line": "(卦數 + hour_number) mod 6"},
     ["U-vat-so-gua-shu"])
rule("c.thanh_am", "k1.1.16", "casting",
     "凡聞聲音，數得幾數，起作上卦，加時數配作下卦。",
     "Nghe tiếng, đếm được bao nhiêu thì làm thượng quái; cộng số giờ làm hạ quái.",
     {"upper": "count mod 8", "lower": "(count + hour_number) mod 8", "moving_line": "not stated"},
     ["U-sheng-yin-lower"])
rule("c.chu_split", "k1.1.17", "casting",
     "凡見字數如停勻，即平分一半為上卦，一半為下卦。如字數不勻，即少一字為上卦，取天輕清之義，以多一字為下卦，取地重濁之義。",
     "Số chữ chẵn thì chia đôi làm thượng, hạ quái; lẻ thì phần ít hơn một chữ làm thượng quái (trời nhẹ trong), phần nhiều hơn làm hạ quái (đất nặng đục).",
     {"upper_words": "floor(n/2)", "lower_words": "ceil(n/2)"})
rule("c.chu_1", "k1.1.18", "casting",
     "一字為太極未判。如草書，混沌不明，不可得卦。如楷書，則取其字畫，以左為陽畫，右為陰畫。居左者看幾數，取為上卦。居右者看幾數，取為下卦。又以一字之陰陽，全畫取爻。",
     "Một chữ là Thái cực chưa phân: chữ thảo thì không lập quẻ được; chữ khải thì lấy nét, nét bên trái là dương, bên phải là âm; số nét trái làm thượng quái, số nét phải làm hạ quái; tổng số nét lấy hào.",
     {"upper": "left strokes mod 8", "lower": "right strokes mod 8", "moving_line": "all strokes mod 6",
      "left_examples": ["彳", "丿"], "right_examples": ["一", "乙", "、"]},
     ["U-one-char-left-right", "U-zi-hour"])
rule("c.chu_2_3", "k1.1.18", "casting",
     "二字為兩儀平分。以一字為上卦，一字為下卦。\n三字為三才。以一字為上卦，二字為下卦。",
     "Hai chữ: một chữ làm thượng, một chữ làm hạ quái. Ba chữ: một chữ làm thượng, hai chữ làm hạ quái.",
     {"2": [1, 1], "3": [1, 2], "count_unit": "not stated; 西林寺牌額占 counts strokes"},
     ["U-zi-count", "U-zi-hour"])
rule("c.chu_4_10_tones", "k1.1.18", "casting",
     "四字為四象。平分上下為卦。又四字以上，不必數畫數，只以平仄聲音調之。平聲為一數，上聲為二數，去聲為三數，入聲為四數。",
     "Bốn chữ chia đều; từ bốn chữ trở lên không đếm nét, chỉ lấy thanh điệu: bình 1, thượng 2, khứ 3, nhập 4.",
     {"tone_value": {"平": 1, "上": 2, "去": 3, "入": 4}, "applies": "4–10 characters"},
     ["U-tones", "U-zi-hour"])
rule("c.chu_5_10_split", "k1.1.18", "casting",
     "五字為五行。以二字為上卦，三字為下卦。\n六字為六爻之集。平分上下為卦。\n七字為齊七政。以三字為上卦，四字為下卦。\n八字為八卦定位。平分上下為卦。\n九字為九疇之義。以四字為上卦，五字為下卦。\n十字為成數。平分上下為卦。",
     "Năm chữ: 2 trên 3 dưới; sáu chữ chia đều; bảy chữ: 3 trên 4 dưới; tám chữ chia đều; chín chữ: 4 trên 5 dưới; mười chữ chia đều.",
     {"4": [2, 2], "5": [2, 3], "6": [3, 3], "7": [3, 4], "8": [4, 4], "9": [4, 5], "10": [5, 5]})
rule("c.chu_11_plus", "k1.1.18", "casting",
     "十一字以上至於百字，皆可起卦。但十一字以上，又不用平仄聲音調之，止用字數。如字數均平，則以半為上卦，以半為下卦。又合二卦總數取爻。",
     "Từ mười một chữ đến trăm chữ đều lập quẻ được, không dùng thanh điệu mà chỉ đếm số chữ; số chữ chẵn thì mỗi nửa một quái; cộng số hai quái lấy hào.",
     {"upper": "number of characters in the first half mod 8", "lower": "number in the second half mod 8",
      "moving_line": "(upper count + lower count) mod 6", "odd_count": "by c.chu_split: fewer characters above"},
     ["U-zi-hour"])
rule("c.truong_xich", "k1.1.19", "casting",
     "丈尺之物，以丈數為上卦，尺數為下卦。合丈尺之數取爻。寸數不用。",
     "Vật đo bằng trượng, xích: số trượng làm thượng quái, số xích làm hạ quái; cộng hai số lấy hào; bỏ số thốn.",
     {"upper": "zhang mod 8", "lower": "chi mod 8", "moving_line": "(zhang + chi) mod 6"},
     ["U-measure-hour"])
rule("c.xich_thon", "k1.1.20", "casting",
     "以尺數為上卦，寸數為下卦。合尺寸之數加時取爻。分數不用。",
     "Số xích làm thượng quái, số thốn làm hạ quái; cộng xích, thốn và số giờ lấy hào; bỏ số phân.",
     {"upper": "chi mod 8", "lower": "cun mod 8", "moving_line": "(chi + cun + hour_number) mod 6"},
     ["U-measure-hour"])
rule("c.vi_nhan", "k1.1.21", "casting",
     "凡為人占，其例不一。或聽語聲起卦，或觀其人品，或取諸身，或取諸物，或因其服色，觸其外物，或以年月日時，或以書寫來意。",
     "Xem cho người thì nhiều cách: nghe tiếng nói, xem loại người, lấy ở thân, lấy ở vật, theo màu áo, theo vật bên ngoài chạm gặp, theo năm tháng ngày giờ, hoặc theo chữ người ấy viết ý đến hỏi.",
     {"methods": ["語聲", "人品", "身", "物", "服色", "外物", "年月日時", "書寫來意"]})
rule("c.vi_nhan_ngu_thanh", "k1.1.21", "casting",
     "又聽其語聲者，如或一句，即如其字數分之起卦，如說兩句，即用先一句為上卦，後一句為下卦。語多，則但用初聽一句，或末後所聞一句。餘句不用。",
     "Nghe tiếng nói: một câu thì chia theo số chữ; hai câu thì câu trước làm thượng quái, câu sau làm hạ quái; nói nhiều thì chỉ dùng câu nghe đầu tiên hoặc câu sau cùng.",
     {"one_sentence": "c.chu_split by characters", "two_sentences": "first → upper, second → lower",
      "many": "first heard or last heard sentence only"},
     ["U-zi-count"])
rule("c.vi_nhan_tuong", "k1.1.21", "casting",
     "觀其人品者，如老人為乾，少女為兌之類。\n取諸其身者，如頭動為乾，足動為震，目動為離之類。\n取諸其物者，如人手中偶有何物，如金玉及圓物之屬為乾，土瓦及方物之屬為坤之類。\n因其服色者，如其人青衣為震，赤衣為離之類。\n觸其外物者，起卦之時見水為坎卦，見火為離卦之類。",
     "Loại người: người già Càn, thiếu nữ Đoài…; thân: đầu động Càn, chân động Chấn, mắt động Ly…; vật cầm tay: vàng ngọc, vật tròn Càn, đất ngói, vật vuông Khôn…; màu áo: xanh Chấn, đỏ Ly…; vật gặp: thấy nước Khảm, thấy lửa Ly….",
     {"examples": {"老人": "乾", "少女": "兌", "頭動": "乾", "足動": "震", "目動": "離", "金玉圓物": "乾", "土瓦方物": "坤", "青衣": "震", "赤衣": "離", "水": "坎", "火": "離"}})
rule("c.tu_ky", "k1.1.22", "casting",
     "凡自己欲占，以年月日時或聞有聲音，或觀當時有所觸之外物，皆可起卦。",
     "Tự mình muốn xem thì dùng năm tháng ngày giờ, hoặc tiếng nghe được, hoặc vật bên ngoài chạm gặp lúc ấy, đều lập quẻ được.",
     {"methods": ["年月日時", "聲音", "外物"]})
rule("c.dong_vat", "k1.1.23", "casting",
     "凡占群物之動，不可起卦。如見一物，則就以此物為上卦，物來之方位為下卦。合物卦數及方位卦數，加時數取爻，以此數總斷其物",
     "Đàn vật động thì không lập quẻ. Thấy một con thì lấy nó làm thượng quái, phương nó đến làm hạ quái; cộng số quái của vật, số quái của phương và số giờ để lấy hào.",
     {"upper": "trigram of the creature (八卦萬物屬類)", "lower": "trigram of the direction it comes from",
      "moving_line": "(TT[upper] + TT[lower] + hour_number) mod 6", "groups": "no cast"})
rule("c.dong_vat_birth", "k1.1.23", "casting",
     "又凡牛馬犬豕之類，初生，則以初生年月日時占之。又可置買此物，亦可以初置買之時推之。",
     "Trâu ngựa chó lợn mới sinh thì xem bằng năm tháng ngày giờ mới sinh; mua về thì có thể lấy lúc mới mua mà suy.",
     {"method": "c.nam_thang_ngay_gio at birth or purchase time"})
rule("c.tinh_vat", "k1.1.24", "casting",
     "凡占靜物，有如江河山石，不可起卦。若至屋宅、樹木之類，則屋宅初創之時，樹木初置之時，皆可起卦。至於器物，則置成之時可占，如枕、椅之類是矣。餘則無故不占。",
     "Vật tĩnh như sông núi đá thì không lập quẻ; nhà cửa, cây cối thì lấy lúc mới dựng, mới trồng; đồ vật thì lấy lúc làm xong (như gối, ghế); ngoài ra không có cớ thì không xem.",
     {"no_cast": ["江河", "山石"], "cast_at": {"屋宅": "初創之時", "樹木": "初置之時", "器物": "置成之時"}})
rule("c.hau_thien_doan_phap", "k1.2.1", "casting",
     "後天端法：以物為上卦，方位為下卦，合物卦之數與方卦之數加時數以取動爻。",
     "Hậu thiên đoan pháp: vật làm thượng quái, phương vị làm hạ quái; cộng số quái của vật, số quái của phương và số giờ để lấy hào động.",
     {"upper": "object trigram", "lower": "direction trigram", "moving_line": "(TT[upper] + TT[lower] + hour_number) mod 6"})
for tri, han in [
    ("乾", "乾：天、父、老人、官貴、頭、骨、馬、金寶、珠玉、水果、圓物、冠、鏡、剛物、大赤色、水寒。"),
    ("坤", "坤：地、母、老婦、土、牛、金、布帛、文章、輿輦、方物、柄、黃色、瓦器、腹、裳、黑色、黍稷、書、米、穀。"),
    ("震", "震：雷、長男、足、髮、龍、百蟲、蹄、竹、萑葦、馬鳴、馵足、顙、稼、樂器之類、草木、青碧綠色、樹、木核、柴、蛇。"),
    ("巽", "巽：風、長女、僧尼、雞、股、百禽、百草、臼、香氣、臭、繩、眼、羽毛、帆、扇、枝葉之類、仙道工匠、直物、工巧之器。"),
    ("坎", "坎：水、雨、雪、工、豕、中男、溝瀆、弓輪、耳、血、月、盜、宮律、棟、叢棘、狐、蒺藜、桎梏、水族、魚、鹽、酒、醢、有核之物、黑色。"),
    ("離", "離：火、雉、日、目、電、霓霞、中女、甲胄、戈兵、文書、槁木、爐、獸、鱷龜蟹蚌、凡有殼之物、紅赤紫色、花、文人、乾燥物。"),
    ("艮", "艮：山、土、少男、童子、狗、手指、徑路、門闕、果、蓏、閽寺、鼠、虎、狐、黔喙之屬、木生之物、藤生之物、爪、鼻。黃色。"),
    ("兌", "兌：澤、少女、巫、舌、妾、肺、羊、毀折之物、帶口之器、屬金者、廢缺之物、奴僕、婢。"),
]:
    rule(f"c.vat_loai.{TT[tri]}", "k1.2.2", "casting", han,
         f"Vật thuộc quái {tri} (dùng làm thượng quái trong đoan pháp hậu thiên); danh sách đầy đủ ở bản dịch mục này.",
         {"trigram": tri, "role": "upper trigram (heading: 並為上卦)"})
rule("c.phuong_vi", "k2.4.2.5", "casting",
     "如離南、坎北、震東、兌西、巽東南、乾西北、艮東北、坤西南類也。",
     "Quái theo phương: Ly nam, Khảm bắc, Chấn đông, Đoài tây, Tốn đông nam, Càn tây bắc, Cấn đông bắc, Khôn tây nam.",
     {"direction_trigram": {"南": "離", "北": "坎", "東": "震", "西": "兌", "東南": "巽", "西北": "乾", "東北": "艮", "西南": "坤"},
      "note": "卷一 八卦方位圖 gives only 離南坎北震東兌西; the eight directions are stated here and in the 附錄 (後天之方位)."})
rule("c.phong_giac", "k1.2.15", "casting",
     "凡見風起而欲占之，便是風從何方而來，以之起卦。",
     "Thấy gió nổi muốn xem thì lấy phương gió thổi đến mà lập quẻ (ví dụ của sách: gió từ nam → Phong Hỏa Gia Nhân, gió từ đông → Ích, tức gió Tốn ở trên, phương ở dưới).",
     {"upper": "巽 (wind)", "lower": "direction trigram", "moving_line": "not stated"})
rule("c.dieu", "k1.2.16", "casting",
     "凡見鳥群，數其只數，看其方所，聽其聲音，辨其毛羽色，皆可起數。",
     "Thấy đàn chim: đếm số con, xem phương, nghe tiếng, phân biệt màu lông, đều có thể khởi số.",
     {"count_to_trigram": "1 乾, 2 兌, 3 離 … (tien_thien_so)"})
rule("c.thanh_am_loai", "k1.2.17", "casting",
     "如人語聲，及動物鳴叫之聲，聲自口出者屬兌。而靜物扣擊屬震，鼓拍槌敲、板木之聲是也；金聲屬乾，鍾馨鉦鐸之聲是也；火聲屬離，烈焰爆竹等聲是也；土聲屬坤，築基、杵垣、坡崩、山裂是也。",
     "Loại tiếng: tiếng từ miệng (người nói, vật kêu) thuộc Đoài; gõ vật tĩnh (trống, mõ, gỗ) thuộc Chấn; tiếng kim loại (chuông, khánh, chiêng) thuộc Càn; tiếng lửa (lửa cháy, pháo) thuộc Ly; tiếng đất (đắp nền, nện tường, lở dốc, nứt núi) thuộc Khôn.",
     {"sound_trigram": {"口": "兌", "扣擊木": "震", "金": "乾", "火": "離", "土": "坤"}})
rule("c.hinh_vat", "k1.2.18", "casting",
     "如物之圓者屬乾，剛者屬兌，方者屬坤，柔者屬巽，仰者屬震，覆者屬艮，長者屬巽，中剛外柔者屬坎，內柔外剛者屬離，乾燥枯槁者屬離，有文彩者亦屬離",
     "Hình vật: tròn Càn, cứng Đoài, vuông Khôn, mềm Tốn, ngửa Chấn, úp Cấn, dài Tốn, trong cứng ngoài mềm Khảm, trong mềm ngoài cứng Ly, khô héo Ly, có văn vẻ cũng Ly.",
     {"shape_trigram": {"圓": "乾", "剛": "兌", "方": "坤", "柔": "巽", "仰": "震", "覆": "艮", "長": "巽", "中剛外柔": "坎", "內柔外剛": "離", "乾燥枯槁": "離", "文彩": "離"}})
rule("c.mau_sac", "k1.2.19", "casting",
     "凡占色之青者屬震，紅紫赤者屬離，黃色者屬坤，白色屬兌，黑色屬坎之類是也。",
     "Màu: xanh Chấn, hồng tía đỏ Ly, vàng Khôn, trắng Đoài, đen Khảm.",
     {"color_trigram": {"青": "震", "紅紫赤": "離", "黃": "坤", "白": "兌", "黑": "坎"}})
rule("c.hau_thien_add_hour", "k2.1.4", "casting",
     "又今人起後天卦，多不加時，得此一卦，止此一爻動，更無移易變通之道。故後天起卦定爻必加時而後可。",
     "Người nay lập quẻ hậu thiên phần nhiều không cộng giờ, được quẻ nào thì chỉ một hào ấy động, không còn biến thông; nên lập quẻ hậu thiên, định hào nhất định phải cộng giờ.",
     {"hau_thien_moving_line_includes": "hour_number"})
rule("c.ho_gia_so", "k2.5.2", "casting",
     "先生以各姓而加數，遂斷之而皆驗。",
     "Tiên sinh lấy họ của từng nhà cộng thêm vào số, đoán đều nghiệm (ví dụ: năm tháng ngày + số nét họ làm thượng quái; + giờ làm hạ quái và lấy hào).",
     {"upper": "(Y+M+D+surname_strokes) mod 8", "lower": "(Y+M+D+surname_strokes+H) mod 8",
      "moving_line": "(Y+M+D+surname_strokes+H) mod 6", "golden": ["jia_shu_wang", "jia_shu_tian", "jia_shu_han"]},
     ["U-zi-count"])
rule("c.ho_gia_so_scope", "k2.5.2", "casting",
     "不特起屋之年月日時加姓也，凡冠婚及葬事皆加一姓可矣。若婚姻，則男女大事，必加二姓可也。極北之人無姓，亦必有名，不辨其字，則數聲音。又無名，則隨所寓也。",
     "Không chỉ năm tháng ngày giờ dựng nhà mới cộng họ; việc đội mũ, cưới, tang đều cộng một họ; cưới hỏi là việc lớn của nam nữ thì cộng cả hai họ. Người vùng cực bắc không có họ thì dùng tên; không biết chữ thì đếm âm; không có tên thì tùy vật gửi gắm.",
     {"add": {"冠/葬": "one surname", "婚姻": "two surnames"}})

# --------------------------------------------------------------- the_dung ---
rule("t.assign", "k3.1.4", "the_dung",
     "體用於變爻，作動靜取之。動者為用，靜者為體。",
     "Thể và dụng lấy theo hào biến mà định động tĩnh: quái động là dụng, quái tĩnh là thể.",
     {"yong": "trigram holding the moving line", "the": "the other trigram"})
rule("t.assign_appendix", "k0.3", "the_dung",
     "凡上下二卦無動爻者為體，有動爻者為用，體卦為主，用卦為事，互卦為事之中應，變卦為事之末應",
     "(Phụ lục) Trong hai quái trên dưới, quái không có hào động là thể, quái có hào động là dụng; thể là chủ, dụng là việc, hỗ là ứng giữa chừng, biến là ứng sau cùng.",
     None, ["appendix"])
rule("t.roles", "k2.1.7", "the_dung",
     "大抵體用之說，體卦為主，用卦為事，互卦為事之中間，刻應變卦為事之終。",
     "Đại để thể là chủ, dụng là việc, hỗ là khoảng giữa của việc, biến là kết cục của việc.",
     {"the": "chủ", "yong": "việc", "hu": "giữa chừng", "bian": "kết cục",
      "note": "「刻應」 sits oddly before 變卦 and is probably misplaced text."})
rule("t.others_sinh_khac", "k2.1.7", "the_dung",
     "宜受他卦之生，不宜他卦之克。他卦者，謂用互變也。",
     "Thể nên được quái khác sinh, không nên bị quái khác khắc; quái khác là dụng, hỗ, biến.",
     {"others": ["yong", "hu_upper", "hu_lower", "bian"]})
rule("t.five_relations", "k2.1.7", "the_dung",
     "體克用，諸事吉；用克體，諸事凶。體生用，有耗失之患；用生體，有進益之喜。體用比和，則百事順遂。",
     "Thể khắc dụng thì mọi việc cát; dụng khắc thể thì mọi việc hung; thể sinh dụng thì lo hao mất; dụng sinh thể thì mừng tăng ích; thể dụng tỷ hòa thì trăm việc thuận.",
     {"the_khac_dung": "吉", "dung_khac_the": "凶", "the_sinh_dung": "耗失", "dung_sinh_the": "進益", "ty_hoa": "順遂"})
rule("t.tiet_khi", "k2.1.7", "the_dung",
     "體生用，為之洩氣，如夏火逢土，亦洩氣。",
     "Thể sinh dụng gọi là tiết khí; như mùa hạ Hỏa gặp Thổ cũng là tiết khí.",
     {"the_sinh_dung": "tiết khí"})
rule("t.dang", "k2.1.7", "the_dung",
     "體党多而體勢盛，用黨多則體勢衰。如卦體是金，而互變皆金，則是體之黨多。如用卦是金，而互變皆金，則是用之黨多。",
     "Phe thể nhiều thì thế thể mạnh; phe dụng nhiều thì thế thể suy. Như thể là Kim mà hỗ, biến đều Kim thì phe thể nhiều; dụng là Kim mà hỗ, biến đều Kim thì phe dụng nhiều.",
     {"the_dang": "hu/bian with the same element as the", "dung_dang": "hu/bian with the same element as yong"},
     ["U-dang-count"])
rule("t.thinh_suy", "k2.1.7", "the_dung",
     "體盛則吉，體衰則凶。用克體固不宜，體生用亦非利。",
     "Thể thịnh thì cát, thể suy thì hung. Dụng khắc thể vốn không nên, thể sinh dụng cũng không lợi.")
rule("t.cat_hung_course", "k2.1.7", "the_dung",
     "互乃中間之應，變乃末後之期。故用吉變凶者，先吉後凶；用凶變吉者，先凶後吉。",
     "Hỗ là ứng ở giữa, biến là kỳ sau cùng; nên dụng cát mà biến hung thì trước cát sau hung; dụng hung mà biến cát thì trước hung sau cát.",
     {"course": "yong verdict first, bian verdict last"})
for tri, han in [
    ("乾", "乾卦生體，則主公門中有喜益，或功名上有喜，或因官有財，或問訟得理，或有金寶之利，或有老人進財，或尊長惠送，或有官貴之喜。"),
    ("坤", "坤卦生體，主有田土之喜，或有田土進財，或得鄉人之益，或得陰人之利，或有果穀之利，或有布帛之喜。"),
    ("震", "震卦生體，則主山林之益，或因山林得財，或進東方之財，或因動中有喜，或有木貨交易之利，或因草木姓氏人稱心。"),
    ("巽", "巽卦生體，亦主山林之益，或因山林得財，或于東南得財，或因草木姓人而進利，或以茶果得利，或有茶果菜蔬之喜。"),
    ("坎", "坎卦生體，有北方之喜，或受北方之財，或水邊人進利，或因點水人稱心，或有因魚鹽酒貨文書交易之利，或有饋送魚鹽酒之喜。"),
    ("離", "離卦生體，主有南方之財，或有文書之喜，或有爐冶場之利，或因火姓人而得財。"),
    ("艮", "艮卦生體，有東北方之財，或山田之喜，或因山林田土獲財，或得宮音帶土人之財。物當安穩，事有終始。"),
    ("兌", "兌卦生體，有西方之財，或喜悅事，或有食物金玉貨利之源，或商音之人，或帶口之人欣逢，或主賓之樂，或朋友講習之事。"),
]:
    rule(f"t.sinh_the.{TT[tri]}", "k2.1.7", "the_dung", han, SINH_THE_VI[tri],
         {"if": f"{tri} produces the 體", "trigram": tri})
for tri, han in [
    ("乾", "如乾卦克體，主有公事之憂，或門戶之憂，或有財寶之失，或于金穀有損，或有怒於尊長，或得罪於貴人。"),
    ("坤", "坤卦克體，主有田土之憂，或于田土有損，或有陰人之侵，或有小人之害，或失布帛之財，或喪穀粟之利。"),
    ("震", "震卦克體，主有虛驚，常多恐懼，或身心不能安靜，或家宅見妖災，或草木姓氏之人相侵，或于山林有所失。"),
    ("巽", "巽卦克體，亦有草木姓人相害，或于山林上生憂。謀事，乃東南方之人；\n處家，忌陰人小口之厄。"),
    ("坎", "坎卦克體，主有險陷之事，或寇盜之憂，或失意於水邊人，或生災於酒後，或點水人相害，或北方人見殃。"),
    ("離", "離卦克體，主文書之憂，或失火之驚，或有南方之憂，或火人相害。"),
    ("艮", "艮卦克體，諸事多違，百謀中阻。或有山林田土之失，或帶土人相侵，防東北方之禍害，或憂墳墓不當。"),
    ("兌", "兌卦克體，不利西方，主口舌事之紛爭。或帶口人侵欺，或有毀折之患，或因飲食而生憂。"),
]:
    rule(f"t.khac_the.{TT[tri]}", "k2.1.7", "the_dung", han, KHAC_THE_VI[tri],
         {"if": f"{tri} controls the 體", "trigram": tri})
rule("t.no_sinh_khac", "k2.1.7", "the_dung",
     "生克不逢，則止以本卦而論之。",
     "Không gặp sinh khắc thì chỉ luận theo quẻ gốc.")
rule("t.order", "k2.1.2", "the_dung",
     "大抵占卜之法，成卦之後先看《周易》爻辭，以斷吉凶。",
     "Phép xem: lập quẻ xong trước xem hào từ Chu Dịch để đoán cát hung (rồi đến thể dụng, khắc ứng, động tĩnh của mình).",
     {"order": ["爻辭", "體用生克", "克應", "己身動靜"]},
     ["U-xian-hou-yaoci"])
rule("t.order_weight", "k2.1.2", "the_dung",
     "必須以易卦為主，克應次之。俱吉則大吉；俱凶則大凶；有凶有吉。則詳審卦辭，及克用體應之類，以斷吉凶也。",
     "Phải lấy quẻ Dịch làm chính, khắc ứng là thứ; đều cát thì đại cát, đều hung thì đại hung; có cát có hung thì xét kỹ lời quẻ và sinh khắc thể dụng mà đoán.",
     {"both_good": "大吉", "both_bad": "大凶", "mixed": "weigh 卦辭 and 體用"})
rule("t.order_doubtful", "k2.1.2", "the_dung",
     "應用生及比和，則吉；體生用及克體，則不吉。",
     "(Văn bản ghi) «ứng dụng sinh và tỷ hòa thì cát; thể sinh dụng và khắc thể thì không cát».",
     {"note": "Wording is corrupt: 應 is probably 體/用 (用生體); read with t.five_relations."})
rule("t.xian_tian_gua_only", "k2.1.4", "the_dung",
     "先天卦斷吉凶，止以卦論，不甚用《易》之爻辭。後天則用爻辭，兼用卦辭",
     "Quẻ tiên thiên đoán cát hung chỉ luận theo quái, không mấy dùng hào từ; quẻ hậu thiên thì dùng hào từ, kiêm cả quái từ.",
     {"tien_thien": "quái only", "hau_thien": "hào từ + quái từ + quái"},
     ["U-xian-hou-yaoci"])
rule("t.no_calendar_spirits", "k2.1.4", "the_dung",
     "蓋曆象選時，並于《周易》不相干涉，不可用也。",
     "Phép chọn giờ theo lịch tượng (thần sát ngày) không liên can đến Chu Dịch, không được dùng.",
     {"exclude": "calendar 神煞 (魁, 破敗亡滅 …) from Mai Hoa judgement"})
rule("t.not_only_the_dung", "k2.1.5", "the_dung",
     "凡占卜決斷，固以體用為主，然有不拘體用者。",
     "Đoán quẻ vốn lấy thể dụng làm chính, nhưng có khi không câu nệ thể dụng (như chùa Tây Lâm, lấy lý mà đoán).")
rule("t.hu_order", "k3.1.6", "the_dung",
     "卦用最緊，互次之，變卦又次之。故曰用為占之即應，互為中間之應，變為事占之終應。",
     "Quái dụng quan trọng nhất, hỗ thứ hai, biến thứ ba: dụng là ứng ngay, hỗ là ứng giữa, biến là ứng cuối.",
     {"weight": ["yong", "hu", "bian"]})
rule("t.hu_of_the", "k3.1.6", "the_dung",
     "如體在上，則上互為體之互，下互為用之互，體卦在下，則下互為體之互，上互為用之互。體互最緊，用互次之。",
     "Thể ở trên thì hỗ trên là hỗ của thể, hỗ dưới là hỗ của dụng; thể ở dưới thì hỗ dưới là hỗ của thể, hỗ trên là hỗ của dụng. Hỗ của thể quan trọng hơn hỗ của dụng.",
     {"the_hu": "hu on the same side as the", "yong_hu": "the other hu", "weight": ["the_hu", "yong_hu"]})
rule("t.bian_end", "k3.1.6", "the_dung",
     "大凡占卦，變卦克體，事於末後，必有不吉。變生體及比和，則事事臨終有吉利。",
     "Biến khắc thể thì về sau việc tất không cát; biến sinh thể hoặc tỷ hòa thì cuối việc có lợi.",
     {"bian_khac_the": "end bad", "bian_sinh_the|ty_hoa": "end good"})
rule("t.many", "k2.4.4", "the_dung",
     "生體則吉，克體則凶，比和則吉，不必論矣。生體多者則愈吉，克體多者則愈凶。然此卦生體，諸卦有克此卦者，彼滅其吉。此卦克體，諸卦又有克此卦者，稍解其窮。",
     "Sinh thể cát, khắc thể hung, tỷ hòa cát; sinh thể càng nhiều càng cát, khắc thể càng nhiều càng hung. Quái sinh thể mà bị quái khác khắc thì mất cái cát; quái khắc thể mà bị quái khác khắc thì cái khốn được giải phần nào.",
     {"count": "more sinh → better, more khắc → worse", "second_order": "a helper that is itself controlled loses its help; a controller that is itself controlled is weakened"})
rule("t.one_the_many_yong", "k2.4.4", "the_dung",
     "凡占卜成卦，即畫成三重：本卦、互卦、變卦也。",
     "Lập quẻ xong thì vẽ thành ba tầng: quẻ gốc, hỗ quái, biến quái.",
     {"layers": ["本卦", "互卦", "變卦"]})
rule("t.jing_zhan", "k2.4.10", "the_dung",
     "凡占在靜室，無所聞見，則無外卦，即不論外卦。但以全卦年月日值五行衰旺之氣，以體用決之。",
     "Xem trong phòng tĩnh, không nghe thấy gì thì không có ngoại quái, không luận ngoại quái; chỉ lấy khí suy vượng ngũ hành của năm tháng ngày đối với toàn quẻ mà quyết theo thể dụng.",
     {"no_outer_omens": "judge by 體用 + 衰旺 of year/month/day only"},
     ["U-vuong-month-or-day"])
rule("t.tam_yeu_combine", "k2.3.2", "the_dung",
     "卦吉而應吉終吉，卦凶而應凶終凶。卦應一吉一凶，事體半吉半凶。",
     "Quẻ cát mà ứng cát thì rốt cuộc cát; quẻ hung mà ứng hung thì rốt cuộc hung; quẻ và ứng một cát một hung thì việc nửa cát nửa hung.",
     {"cast_good+omen_good": "吉", "cast_bad+omen_bad": "凶", "mixed": "半吉半凶",
      "note": "The rest of 三要靈應篇 is a catalogue of omens met while casting (people, gestures, objects, animals); it needs outside observation and is not extracted as computable rules."})
rule("t.thap_ung_the", "k2.4.2", "the_dung",
     "十應並以體卦為主，諸用卦為用。",
     "Thập ứng đều lấy quái thể làm chủ, các quái khác làm dụng.")
rule("t.phuong_ung", "k3.4.1", "the_dung",
     "方應者，以體為主，看來占之人在何方位上，即看其所坐立之方位。宜生體卦，又宜與體比和，則吉；如克體卦則凶，如體卦生之，亦不吉矣。",
     "Phương ứng: lấy thể làm chủ, xem người đến hỏi ngồi đứng ở phương nào; quái phương ấy sinh thể hoặc tỷ hòa thì cát, khắc thể thì hung, thể sinh nó cũng không cát.",
     {"direction_trigram_vs_the": {"sinh": "吉", "ty_hoa": "吉", "khac": "凶", "the_sinh": "不吉"}})
rule("t.ngoai_ung_tri", "k3.4.1", "the_dung",
     "如見老人、馬、金玉圓物，得乾。見老婦、牛、土瓦物，得坤之類。",
     "Ngoại ứng: thấy người già, ngựa, vàng ngọc, vật tròn là được Càn; thấy bà già, trâu, đồ đất ngói là được Khôn….",
     {"outer_trigram_vs_the": "same five relations"})
rule("t.thien_thoi_ung", "k3.4.1", "the_dung",
     "天時之應，占卜之際，晴明為離，雨雪為坎，風為巽，雷為震。如離為體，宜晴。坎為體，宜雨。巽為體，宜風。震為體，宜雷。",
     "Thiên thời ứng: trời quang là Ly, mưa tuyết Khảm, gió Tốn, sấm Chấn; thể Ly thì nên trời quang, thể Khảm nên mưa, thể Tốn nên gió, thể Chấn nên sấm.",
     {"weather_trigram": {"晴明": "離", "雨雪": "坎", "風": "巽", "雷": "震"}})
rule("t.dia_ly_ung", "k3.4.1", "the_dung",
     "在竹林間，為震、巽之地；在江河溪澗池沼之上為坎；在五金之處為乾、兌之鄉；在窯灶爐火之所為離；在土瓦之所為坤、艮",
     "Địa lý ứng: rừng tre là đất Chấn, Tốn; sông suối ao đầm là Khảm; nơi kim loại là Càn, Đoài; lò bếp là Ly; nơi đất ngói là Khôn, Cấn.",
     {"place_trigram": {"竹林": ["震", "巽"], "江河溪澗池沼": "坎", "五金": ["乾", "兌"], "窯灶爐火": "離", "土瓦": ["坤", "艮"]}})
rule("t.true_sinh_khac", "k3.1.7", "the_dung",
     "若外卦，則須明其真生真克之五行，以分輕重，則禍福立應。",
     "Với ngoại quái (điềm bên ngoài) phải phân biệt ngũ hành sinh khắc thật hay chỉ có hình sắc để định nặng nhẹ.",
     {"applies_to": "outer omens only, not the cast"})

# ------------------------------------------------------------- vuong_suy ---
rule("v.vuong", "k1.1.4", "vuong_suy",
     "震、巽木旺於春，離火旺于夏，乾、兌金旺於秋，坎水旺於冬，坤、艮土旺於辰戌丑未月。",
     "Chấn, Tốn Mộc vượng mùa xuân; Ly Hỏa vượng mùa hạ; Càn, Đoài Kim vượng mùa thu; Khảm Thủy vượng mùa đông; Khôn, Cấn Thổ vượng các tháng Thìn, Tuất, Sửu, Mùi.",
     {"vuong": {"春": ["震", "巽"], "夏": ["離"], "秋": ["乾", "兌"], "冬": ["坎"], "辰戌丑未月": ["坤", "艮"]}},
     ["U-season-months", "U-month-branch"])
rule("v.suy", "k1.1.5", "vuong_suy",
     "春坤、艮，夏乾、兌，秋震、巽，冬離，辰戌丑未坎。",
     "Suy: xuân Khôn, Cấn; hạ Càn, Đoài; thu Chấn, Tốn; đông Ly; tháng Thìn Tuất Sửu Mùi Khảm.",
     {"suy": {"春": ["坤", "艮"], "夏": ["乾", "兌"], "秋": ["震", "巽"], "冬": ["離"], "辰戌丑未月": ["坎"]}},
     ["U-season-months", "U-month-branch"])
rule("v.thoi_lenh", "k2.4.2.4", "vuong_suy",
     "旺者，如寅卯之月日則木旺，巳午之月日火旺，申酉之月日金旺，亥子之月日水旺，辰戌丑未之月日土旺。衰者，如木旺則土衰，土旺則水衰，水旺火衰，火旺則金衰，金旺則木衰。",
     "Vượng: tháng/ngày Dần Mão Mộc vượng, Tỵ Ngọ Hỏa vượng, Thân Dậu Kim vượng, Hợi Tý Thủy vượng, Thìn Tuất Sửu Mùi Thổ vượng. Suy: Mộc vượng thì Thổ suy, Thổ vượng Thủy suy, Thủy vượng Hỏa suy, Hỏa vượng Kim suy, Kim vượng Mộc suy.",
     {"vuong_by_branch": {"寅": "木", "卯": "木", "巳": "火", "午": "火", "申": "金", "酉": "金", "亥": "水", "子": "水", "辰": "土", "戌": "土", "丑": "土", "未": "土"},
      "suy": "the element controlled by the vượng element",
      "note": "This fixes the seasons of v.vuong by branch months (春 = 寅卯, 辰 is 土) and adds days (月日)."},
     ["U-vuong-month-or-day", "U-month-branch"])
rule("v.thoi_lenh_use", "k2.4.2.4", "vuong_suy",
     "是故生體卦氣，宜值時之旺氣，不宜衰氣。如克體卦氣，則宜乘衰。",
     "Quái khí sinh thể nên gặp lúc vượng, không nên suy; quái khí khắc thể thì nên gặp lúc suy.")
rule("v.suy_vuong_luan", "k2.4.6", "vuong_suy",
     "凡占卜，體卦宜盛旺。氣旺而又逢生則吉，重遇克則凶。若體衰而逢克，則其凶甚矣。體衰而有生體之卦，則衰稍解。大抵體之卦宜旺，生體之卦氣亦宜旺。克體之卦氣宜衰。",
     "Thể nên thịnh vượng: vượng lại được sinh thì cát, bị khắc nặng thì hung; thể suy mà bị khắc thì rất hung; thể suy mà có quái sinh thể thì cái suy được giải phần nào. Quái thể nên vượng, quái sinh thể nên vượng, quái khắc thể nên suy.",
     {"the_vuong+sinh": "吉", "khac_nang": "凶", "the_suy+khac": "凶甚", "the_suy+sinh": "衰稍解"})
rule("v.dac_lenh", "k3.1.8", "vuong_suy",
     "此得令之卦，乘旺之氣，雖有他卦克之，亦無大害。",
     "Quái đắc lệnh, thừa vượng khí thì dù bị quái khác khắc cũng không hại lớn.",
     {"the_vuong+khac": "無大害"})
rule("v.the_suy_khac_vuong", "k3.1.8", "vuong_suy",
     "但不要克體之卦氣旺。而體卦氣衰是不吉之占。占者有此，若問病必死，問訟必敗。若非問訟與病而常占，則防有官病之事。末臨其期，在於克體卦氣之月日也。",
     "Không nên để quái khắc thể vượng mà quái thể suy: đó là quẻ không cát; hỏi bệnh tất chết, hỏi kiện tất thua; xem việc thường thì đề phòng việc quan, bệnh; kỳ đến vào tháng ngày của quái khí khắc thể.",
     {"khac_vuong+the_suy": {"疾病": "必死", "官訟": "必敗", "other": "防官病"}, "timing": "month/day of the controlling trigram's 卦氣"})
rule("v.dang_suy", "k3.1.8", "vuong_suy",
     "內外並也生體，雖體之卦黨多，皆是衰卦，終不吉也。",
     "Trong ngoài đều sinh thể, phe thể dù nhiều mà đều là quái suy thì rốt cuộc vẫn không cát.")
rule("v.phuong", "k2.4.2.5", "vuong_suy",
     "大抵本卦之方，生為旺，受克為衰。宜以體卦參之。生體卦氣，宜受旺方；克體卦氣，宜受克方。",
     "Đại để: ở phương của chính quái hoặc phương sinh nó là vượng, ở phương khắc nó là suy; xét cùng quái thể: quái khí sinh thể nên ở phương vượng, quái khí khắc thể nên ở phương bị khắc.",
     {"applies_to": "outer omen trigrams and their direction"})
rule("v.nhat_ung", "k3.4.1", "vuong_suy",
     "日應者，以體卦為主，看所占屬何卦，及體卦與本日衰旺如何。蓋卦宜生體，宜比和；不宜克體，亦不宜體卦生之也。本日所屬卦氣如寅卯木、巳午火、申酉金、亥子水、辰戌丑未土也。",
     "Nhật ứng: lấy thể làm chủ, xem quái thể với ngày xem suy vượng thế nào; khí của ngày theo chi: Dần Mão Mộc, Tỵ Ngọ Hỏa, Thân Dậu Kim, Hợi Tý Thủy, Thìn Tuất Sửu Mùi Thổ.",
     {"day_element_by_branch": {"寅卯": "木", "巳午": "火", "申酉": "金", "亥子": "水", "辰戌丑未": "土"}})

# ------------------------------------------------------------------ topic ---
FIVE = ("the_khac_dung", "dung_khac_the", "the_sinh_dung", "dung_sinh_the", "ty_hoa")


def topic(id, section, han, vi, yong, outcomes, extra=None, flags=None):
    f = {"yong_is": yong, **dict(zip(FIVE, outcomes))}
    if extra:
        f.update(extra)
    rule(id, section, "topic", han, vi, f, flags)


rule("p.thien_thoi", "k2.2.1", "topic",
     "凡占天時，不分體用，全觀諸卦，詳推五行。離多主晴，坎多主雨，坤乃陰晦，乾主晴明，震多則春夏雷轟，巽多則四時風烈，艮多則久雨必晴，兌多則不雨亦陰。夏占離多而無坎，則亢旱炎炎。冬占坎多而無離，則雨雪飄飄。",
     "Xem thời tiết không chia thể dụng, xét hết các quái: Ly nhiều chủ nắng, Khảm nhiều chủ mưa, Khôn âm u, Càn trong sáng, Chấn nhiều thì xuân hạ sấm vang, Tốn nhiều thì bốn mùa gió mạnh, Cấn nhiều thì mưa lâu tất tạnh, Đoài nhiều thì không mưa cũng âm u; hạ mà Ly nhiều không Khảm thì hạn nắng; đông mà Khảm nhiều không Ly thì mưa tuyết.",
     {"no_the_dung": True, "count_over": "all trigrams (本, 互, 變)",
      "many": {"離": "晴", "坎": "雨", "坤": "陰晦", "乾": "晴明", "震": "雷 (春夏)", "巽": "風", "艮": "久雨必晴", "兌": "不雨亦陰"},
      "summer_li_no_kan": "亢旱", "winter_kan_no_li": "雨雪"},
     ["U-duo"])
rule("p.thien_thoi_scope", "k2.2.1", "topic",
     "全觀諸卦者，謂互變卦。",
     "«Xét hết các quái» là nói cả hỗ quái và biến quái.",
     {"count_over": ["本卦 upper", "本卦 lower", "hu_upper", "hu_lower", "bian"]}, ["U-duo"])
rule("p.thien_thoi_blocks", "k2.4.5", "topic",
     "又如乾、兌多則巽無風；坤、艮多則坎無雨；坎多，則離亦不晴。",
     "Càn, Đoài nhiều thì Tốn không có gió; Khôn, Cấn nhiều thì Khảm không có mưa; Khảm nhiều thì Ly cũng không nắng.",
     {"cancel": {"巽": "乾兌多", "坎": "坤艮多", "離": "坎多"}}, ["U-duo"])
rule("p.thien_thoi_hex_1", "k2.2.1", "topic",
     "地天泰，水天需，昏蒙之象。天地否，水地比，黑暗之形。",
     "Địa Thiên Thái, Thủy Thiên Nhu là tượng mờ mịt; Thiên Địa Bĩ, Thủy Địa Tỷ là hình tối tăm.",
     {"by_hexagram": {"地天泰": "昏蒙", "水天需": "昏蒙", "天地否": "黑暗", "水地比": "黑暗"}})
rule("p.thien_thoi_hex_2", "k2.2.1", "topic",
     "又若水火既濟、火水未濟，四時不測風雲；風澤中孚，澤風大過，三冬必然雨雪。水山蹇，山水蒙，百步必須執蓋。地風升，風地觀，四時不可行船。",
     "Thủy Hỏa Ký Tế, Hỏa Thủy Vị Tế: bốn mùa gió mây khó lường; Phong Trạch Trung Phu, Trạch Phong Đại Quá: ba tháng đông tất mưa tuyết; Thủy Sơn Kiển, Sơn Thủy Mông: đi trăm bước phải cầm ô; Địa Phong Thăng, Phong Địa Quan: bốn mùa không thể đi thuyền.",
     {"by_hexagram": {"水火既濟": "不測風雲", "火水未濟": "不測風雲", "風澤中孚": "冬雨雪", "澤風大過": "冬雨雪", "水山蹇": "雨", "山水蒙": "雨", "地風升": "不可行船", "風地觀": "不可行船"}})
rule("p.thien_thoi_li_gen", "k2.2.1", "topic",
     "離在艮上，暮雨朝晴，離互艮宮，暮晴朝雨。",
     "Ly ở trên Cấn thì chiều mưa sáng tạnh; Ly hỗ với cung Cấn thì chiều tạnh sáng mưa.")
topic("p.nhan_su", "k2.2.2",
      "人事之占，詳觀體用。體卦為主，用卦為賓。用克體不宜，體克用則吉。用生體有進益之喜，體生用有耗失之患。體用比和，謀為吉利。",
      "Xem nhân sự: thể là chủ, dụng là khách; dụng khắc thể không nên, thể khắc dụng thì cát; dụng sinh thể có mừng tăng ích, thể sinh dụng lo hao mất; thể dụng tỷ hòa thì mưu tính cát lợi.",
      "賓 (khách)", ["吉", "不宜", "耗失", "進益", "謀為吉利"])
topic("p.gia_trach", "k2.2.3",
      "凡占家宅，以體為主，用為家宅。體克用，則家宅多吉，用克體，則家宅多凶。體生用，多耗散，或防失盜之憂。用生體，多進益，或有饋送之喜。體用比和，家宅安穩。",
      "Xem nhà: thể là chủ, dụng là gia trạch; thể khắc dụng nhà nhiều cát; dụng khắc thể nhà nhiều hung; thể sinh dụng nhiều hao tán, phòng mất trộm; dụng sinh thể nhiều tăng ích, có quà biếu; tỷ hòa nhà yên ổn.",
      "家宅", ["多吉", "多凶", "耗散/防失盜", "進益/饋送", "安穩"])
topic("p.oc_xa", "k2.2.4",
      "凡占屋舍，以體為主，用為屋舍。體克用，居之吉，用克體，居之凶。體生用，主資財衰退；用生體，則門戶興隆。體用比和，自然安穩。",
      "Xem nhà ở: dụng là nhà; thể khắc dụng ở thì cát; dụng khắc thể ở thì hung; thể sinh dụng của cải sút; dụng sinh thể nhà cửa hưng thịnh; tỷ hòa tự nhiên yên ổn.",
      "屋舍", ["居之吉", "居之凶", "資財衰退", "門戶興隆", "安穩"])
topic("p.hon_nhan", "k2.2.5",
      "占婚姻以體為主，用為婚姻。用生體，婚易成，或因婚有得；體生用，婚難成，或因婚有失。體克用，可成但成之遲；用克體，不可成，成亦有害。體用比和，婚姻吉利。",
      "Xem hôn nhân: dụng là hôn sự; dụng sinh thể dễ thành, nhờ hôn nhân mà được; thể sinh dụng khó thành, vì hôn nhân mà mất; thể khắc dụng thành được nhưng chậm; dụng khắc thể không thành, thành cũng có hại; tỷ hòa cát lợi.",
      "婚姻", ["可成但遲", "不可成/成亦有害", "難成/有失", "易成/有得", "吉利"])
rule("p.hon_nhan_hai_nha", "k2.2.5", "topic",
     "占婚，體為所占之家，用為所婚之家。體卦旺，則此家門戶勝；用卦旺，則彼家資盛。",
     "Xem cưới: thể là nhà đi xem, dụng là nhà kết thông gia; thể vượng thì nhà mình môn hộ hơn, dụng vượng thì nhà kia của cải thịnh.",
     {"the": "this family", "yong": "the other family", "the_vuong": "此家門戶勝", "yong_vuong": "彼家資盛"})
rule("p.hon_nhan_mao", "k2.2.5", "topic",
     "乾：端正而長\n坎：邪淫、黑色、嫉妒、奢侈\n艮：色黃多巧\n震：美貌難犯\n巽：發少稀疏，醜陋心貪\n離：短赤色，性不常\n坤：貌醜，大腹而黃\n兌：高長，語話喜悅，白色",
     "Dáng người theo quái (trong mục hôn nhân): Càn đoan chính mà cao; Khảm tà dâm, đen, đố kỵ, xa xỉ; Cấn vàng, nhiều khéo; Chấn đẹp khó phạm; Tốn tóc thưa, xấu, lòng tham; Ly thấp, đỏ, tính không thường; Khôn mặt xấu, bụng to, da vàng; Đoài cao, nói năng vui vẻ, da trắng.",
     {"by_trigram": "appearance of the partner", "applies_to": "not stated (presumably 用卦)"}, ["U-hon-nhan-mao"])
rule("p.sinh_san", "k2.2.6", "topic",
     "占生產，以體為母，用為生。體用俱宜乘旺，不宜乘衰。宜相生，不宜相克。體克用不利於子；用克體不利於母。體克用而用卦衰，則子難完；用克體而體卦衰，則母難保。用生體，利於母；體生用，利於子。體用比和，生育順快。",
     "Xem sinh nở: thể là mẹ, dụng là con; cả hai nên thừa vượng, nên tương sinh; thể khắc dụng bất lợi cho con, dụng khắc thể bất lợi cho mẹ; thể khắc dụng mà dụng suy thì con khó toàn; dụng khắc thể mà thể suy thì mẹ khó giữ; dụng sinh thể lợi mẹ; thể sinh dụng lợi con; tỷ hòa sinh nở thuận nhanh.",
     {"the": "母", "yong": "子", "the_khac_dung": "不利子 (+用衰: 子難完)", "dung_khac_the": "不利母 (+體衰: 母難保)",
      "dung_sinh_the": "利母", "the_sinh_dung": "利子", "ty_hoa": "順快"})
rule("p.sinh_san_gioi", "k2.2.6", "topic",
     "陽卦陽爻多者則生男，陰卦陰爻多者生女。陰陽卦爻相生，則察所占左右人之奇偶以證之。",
     "Quái dương, hào dương nhiều thì sinh trai; quái âm, hào âm nhiều thì sinh gái; âm dương ngang nhau thì xét số người chung quanh chẵn lẻ mà chứng.",
     {"boy": "陽卦/陽爻 多", "girl": "陰卦/陰爻 多", "tie": "parity of people present (outside observation)"},
     ["U-yang-gua", "U-duo"])
rule("p.sinh_san_ngay", "k2.2.6", "ung_ky",
     "如欲決其日辰，則以用卦之氣數參決之。所謂卦之氣數者，即看何為用卦，於八卦時序之類次之。",
     "Muốn định ngày sinh thì lấy khí số của quái dụng mà xét, tức xem dụng là quái gì rồi theo loại «thời tự» của bát quái.",
     {"timing_from": "yong trigram → 時序 line of 八卦萬物屬類"})
topic("p.am_thuc", "k2.2.7",
      "凡占飲食，以體為主，用為飲食。用生體，飲食必豐；體生用，飲食難就。體克用，則飲食有阻；用克體，飲食必無。體用比和，飲食豐足。",
      "Xem ăn uống: dụng là món ăn; dụng sinh thể ăn uống tất đầy đủ; thể sinh dụng khó được ăn; thể khắc dụng ăn uống có trở; dụng khắc thể tất không có ăn; tỷ hòa no đủ.",
      "飲食", ["有阻", "必無", "難就", "必豐", "豐足"])
rule("p.am_thuc_kan_dui", "k2.2.7", "topic",
     "又卦中有坎則有酒，有兌則有食。無坎無兌，則皆無。兌、坎生體，酒肉醉飽。",
     "Trong quẻ có Khảm thì có rượu, có Đoài thì có đồ ăn; không Khảm không Đoài thì đều không; Đoài, Khảm sinh thể thì rượu thịt no say.",
     {"坎": "酒", "兌": "食", "neither": "無", "坎兌生體": "酒肉醉飽"})
rule("p.am_thuc_block", "k2.4.5", "topic",
     "有坎則有酒，有兌則有食。如遇坤、艮，則坎亦無酒，離值則兌亦無食。",
     "Có Khảm thì có rượu, có Đoài thì có đồ ăn; gặp Khôn, Cấn thì Khảm cũng không có rượu; gặp Ly thì Đoài cũng không có đồ ăn.",
     {"cancel": {"坎酒": ["坤", "艮"], "兌食": ["離"]}})
topic("p.cau_muu", "k2.2.8",
      "占求謀，以體為主，用為所謀之事。體克用，謀雖可成，但成遲。用克體，求謀不成，謀亦有害。用生體。不謀而成；體生用，多謀少遂。體用比和，求謀稱意。",
      "Xem mưu cầu: dụng là việc mưu; thể khắc dụng thành nhưng chậm; dụng khắc thể không thành, còn có hại; dụng sinh thể không mưu mà thành; thể sinh dụng mưu nhiều ít được; tỷ hòa vừa ý.",
      "所謀之事", ["可成但遲", "不成/有害", "多謀少遂", "不謀而成", "稱意"])
topic("p.cau_danh", "k2.2.9",
      "凡占求名，以體為主，用為名。體克用，名可成，但成遲。用克體，名不可成。體生用，名不可就，或因名有喪。用生體，名易成，或因名有得。體用比和，功名稱意。",
      "Xem cầu danh: dụng là danh; thể khắc dụng danh thành nhưng chậm; dụng khắc thể không thành; thể sinh dụng không đạt, vì danh mà mất; dụng sinh thể dễ thành, nhờ danh mà được; tỷ hòa công danh vừa ý.",
      "名", ["可成但遲", "不可成", "不可就/因名有喪", "易成/因名有得", "稱意"])
rule("p.cau_danh_ky", "k2.2.9", "ung_ky",
     "欲知名成之日，生體之卦氣詳之。欲知職任之處，變卦之方道決之。",
     "Muốn biết ngày thành danh thì xét quái khí sinh thể; muốn biết nơi nhận chức thì lấy phương của quái biến mà quyết.",
     {"success_date": "卦氣 of the trigram producing 體", "post_location": "direction of the bian trigram"})
rule("p.cau_danh_tai_nhiem", "k2.2.9", "topic",
     "若在任占卜，最忌見克體之卦，如卦有克體者，即居官見禍，輕則上司責罰，重則削官退居。其日期，看克體之卦氣者，於八卦所屬時序類中斷之。",
     "Đang tại chức mà xem thì kỵ nhất quái khắc thể: có thì làm quan gặp họa, nhẹ bị cấp trên trách phạt, nặng bị cách chức; ngày ấy xem quái khí khắc thể theo loại thời tự của bát quái.",
     {"in_office+khac_the": "居官見禍", "timing": "時序 of the controlling trigram"})
topic("p.cau_tai", "k2.2.10",
      "占求財，以體為主，以用為財。體克用，有財；用克體，無財。體生用，財有損耗之憂；用生體，財有進益之喜。體用比和，財利快意。",
      "Xem cầu tài: dụng là tài; thể khắc dụng có tài; dụng khắc thể không có tài; thể sinh dụng lo hao tài; dụng sinh thể mừng tài tăng; tỷ hòa tài lợi vừa ý.",
      "財", ["有財", "無財", "損耗", "進益", "快意"])
rule("p.cau_tai_ky", "k2.2.10", "ung_ky",
     "欲知得財之日，生體之卦氣定之。欲知破財之日，克體卦氣定之。",
     "Ngày được tài định theo quái khí sinh thể; ngày hao tài định theo quái khí khắc thể.",
     {"gain_date": "卦氣 of the producing trigram", "loss_date": "卦氣 of the controlling trigram"})
rule("p.cau_tai_ky_2", "k2.2.10", "ung_ky",
     "又若卦中有體克用之卦，及生體之卦，則有財，此卦氣即見財之日。若卦中有克體之卦，及體生用之卦，即破財，此卦氣破財之日。",
     "Trong quẻ có quái bị thể khắc và quái sinh thể thì có tài, quái khí ấy là ngày thấy tài; có quái khắc thể và quái thể sinh thì hao tài, quái khí ấy là ngày hao tài.")
topic("p.giao_dich", "k2.2.11",
      "占交易，以體為主，用為財。體克用，有財；用克體，不成。體生用，難成，或因交易有失。用生體，即成，成必有財。體用比和，易成。",
      "Xem giao dịch: dụng là tài; thể khắc dụng có tài; dụng khắc thể không thành; thể sinh dụng khó thành, có khi vì giao dịch mà mất; dụng sinh thể thành ngay, thành tất có tài; tỷ hòa dễ thành.",
      "財", ["有財", "不成", "難成/有失", "即成/有財", "易成"])
topic("p.xuat_hanh", "k2.2.12",
      "占出行，以體為主，用為所行之應。體克用，可行，所至多得意。用克體，出則有禍。體生用，出行有破耗之失；用生體，有意外之財。體用比和，出行順快。",
      "Xem xuất hành: dụng là ứng của chuyến đi; thể khắc dụng đi được, đến đâu cũng đắc ý; dụng khắc thể ra đi có họa; thể sinh dụng hao tổn; dụng sinh thể có của bất ngờ; tỷ hòa đi thuận.",
      "所行之應", ["可行/多得意", "有禍", "破耗", "意外之財", "順快"])
rule("p.xuat_hanh_tri", "k2.2.12", "topic",
     "又凡出行，體宜乘旺，諸卦宜生體。體卦乾、震多，主動。坤、艮多，不動。巽宜舟行，離宜陸行。坎妨失脫，兌主紛爭。",
     "Xuất hành: thể nên vượng, các quái nên sinh thể; Càn, Chấn nhiều thì đi, Khôn, Cấn nhiều thì không đi; Tốn nên đi thuyền, Ly nên đi bộ; Khảm phòng thất thoát, Đoài chủ tranh cãi.",
     {"乾震多": "動", "坤艮多": "不動", "巽": "舟行", "離": "陸行", "坎": "失脫", "兌": "紛爭"}, ["U-duo"])
topic("p.hanh_nhan", "k2.2.13",
      "占行人，以體為主，用為行人。體克用，行人歸遲；用克體，行人不歸。體生用，行人未歸；用生體，行人即歸。體用比和，歸期不日矣。",
      "Xem người đi xa: dụng là người đi; thể khắc dụng về chậm; dụng khắc thể không về; thể sinh dụng chưa về; dụng sinh thể về ngay; tỷ hòa chẳng mấy ngày về.",
      "行人", ["歸遲", "不歸", "未歸", "即歸", "不日歸"])
rule("p.hanh_nhan_ngoai", "k2.2.13", "topic",
     "又以用卦看行人在外之情況。逢生，在外順快；逢衰受克，在外災殃。震多不寧，艮多有阻。坎有險難，兌主紛爭。",
     "Lấy quái dụng xem tình hình người ở ngoài: được sinh thì ở ngoài thuận; suy bị khắc thì ở ngoài gặp tai; Chấn nhiều không yên, Cấn nhiều có trở, Khảm có hiểm nạn, Đoài chủ tranh cãi.",
     {"yong_sinh": "順快", "yong_suy_khac": "災殃"}, ["U-duo"])
topic("p.yet_kien", "k2.2.14",
      "占謁見，以體為主，用為所見之人。體克用，可見；用克體，不見。體生用，難見，見之而無益；用生體，可見，見之且有得。體用比和，歡然相見。",
      "Xem yết kiến: dụng là người được gặp; thể khắc dụng gặp được; dụng khắc thể không gặp; thể sinh dụng khó gặp, gặp cũng vô ích; dụng sinh thể gặp được và có được; tỷ hòa vui vẻ gặp nhau.",
      "所見之人", ["可見", "不見", "難見/無益", "可見/有得", "歡然相見"])
topic("p.that_vat", "k2.2.15",
      "占失物，以體為主，用為失物。體克用，可尋遲得；用克體，不可尋。體生用，物難見；用生體，物易尋。體用比和，物不失矣。",
      "Xem mất đồ: dụng là vật mất; thể khắc dụng tìm được nhưng chậm; dụng khắc thể không tìm được; thể sinh dụng khó thấy; dụng sinh thể dễ tìm; tỷ hòa vật không mất.",
      "失物", ["可尋遲得", "不可尋", "難見", "易尋", "不失"])
rule("p.that_vat_noi", "k2.2.15", "topic",
     "又以變卦為失物之所在。",
     "Lấy quái biến làm nơi vật mất ở: Càn tây bắc / công sở, lầu gác, cạnh kim thạch, trong đồ tròn, chỗ cao; Khôn tây nam / ruộng, kho; Chấn đông / rừng, bụi gai, cạnh chuông trống, chợ, đường lớn; Tốn đông nam / rừng, chùa quán, vườn rau, thuyền, đồ gỗ; Khảm bắc / bờ nước, giếng, rãnh, cạnh rượu giấm, chỗ cá muối; Ly nam / bếp, lò, cửa sáng, phòng trống, cạnh giấy tờ, chỗ khói lửa; Cấn đông bắc / rừng núi, ven đường, cạnh đá, hang đất; Đoài tây / bờ đầm, tường đổ, giếng hoang ao khuyết (đủ chi tiết ở bản dịch).",
     {"location_from": "bian trigram", "table_section": "k2.2.15 (變是乾 … 兌則尋於西方 …)"})
rule("p.tat_benh", "k2.2.16", "topic",
     "凡占疾病，以體為病人，用為病症。體卦宜旺不宜衰，體宜逢生，不宜見克。用宜生體，不宜克體。體克用，病易安；體生用，病難愈。",
     "Xem bệnh: thể là người bệnh, dụng là chứng bệnh; thể nên vượng không nên suy, nên được sinh không nên bị khắc; dụng nên sinh thể không nên khắc thể; thể khắc dụng bệnh dễ yên; thể sinh dụng bệnh khó khỏi.",
     {"the": "病人", "yong": "病症", "the_khac_dung": "易安", "the_sinh_dung": "難愈"})
rule("p.tat_benh_2", "k2.2.16", "topic",
     "體克用者，勿藥有喜；用克體者，雖藥無功。若體逢克而乘旺，猶為庶幾。體遇克而更衰，斷無存日。欲知凶中有救，生體之卦存焉。體生用者，遷延難好；用生體者，即愈。體用比和，疾病易安。",
     "Thể khắc dụng thì không thuốc cũng khỏi; dụng khắc thể thì có thuốc cũng vô công; thể bị khắc mà thừa vượng thì còn có thể mong; thể bị khắc lại suy thì chắc không còn ngày sống; muốn biết trong hung có cứu thì xem có quái sinh thể không; thể sinh dụng thì kéo dài khó khỏi; dụng sinh thể thì khỏi ngay; tỷ hòa bệnh dễ yên.",
     {"the_khac_dung": "勿藥有喜", "dung_khac_the": "雖藥無功", "dung_khac_the+the_vuong": "猶為庶幾", "dung_khac_the+the_suy": "斷無存日",
      "rescue": "a trigram producing 體", "the_sinh_dung": "遷延難好", "dung_sinh_the": "即愈", "ty_hoa": "易安"})
rule("p.tat_benh_ky", "k2.2.16", "ung_ky",
     "若究和平之日，主卦決之。若詳危厄之期，克體之卦定之。",
     "Ngày bình phục thì lấy quái chủ mà quyết; kỳ nguy ách thì lấy quái khắc thể mà định.",
     {"recovery": "主卦 (體)", "danger": "the controlling trigram"}, ["U-chu-gua"])
rule("p.tat_benh_thuoc", "k2.2.16", "topic",
     "若論醫藥之屬，當看生體之卦。如離卦生體，宜服熱藥；坎卦生體，宜服冷藥，如艮溫補；乾、兌涼藥是也。",
     "Bàn thuốc men thì xem quái sinh thể: Ly sinh thể nên uống thuốc nóng; Khảm sinh thể nên thuốc lạnh; Cấn thì ôn bổ; Càn, Đoài thì thuốc mát.",
     {"remedy_by_producing_trigram": {"離": "熱藥", "坎": "冷藥", "艮": "溫補", "乾": "涼藥", "兌": "涼藥"}})
rule("p.tat_benh_quy_than", "k2.2.16", "topic",
     "又有信鬼神之說，雖非《易》道，然不可謂《易》道之不該。姑以理推之。如卦有克體者，即可測其鬼神。",
     "Lại có thuyết tin quỷ thần, tuy không phải đạo Dịch nhưng không thể nói đạo Dịch không bao gồm; tạm lấy lý suy: quẻ có quái khắc thể thì có thể đoán quỷ thần (theo quái ấy, xem bản dịch).",
     {"spirit_from": "the trigram controlling 體", "none_if": "no controlling trigram"})
topic("p.quan_tung", "k2.2.17",
      "是故體克用者，已勝人；用克體者，人勝己。體生用，非為失理，或因官有所喪；用生體，不止得理，或因訟有所得。體用比和，官訟最吉。",
      "Thể khắc dụng thì mình thắng người; dụng khắc thể thì người thắng mình; thể sinh dụng chẳng những thua lý, còn vì quan mà mất; dụng sinh thể chẳng những được lý, còn vì kiện mà được; tỷ hòa kiện tụng tốt nhất.",
      "對辭之人與官訟之應", ["己勝人", "人勝己", "失理/因官有喪", "得理/因訟有得", "最吉"],
      {"note": "「非為失理」 is read as 「非惟失理」 (not only losing the case), parallel to 不止得理."})
rule("p.quan_tung_vuong", "k2.2.17", "topic",
     "占官訟，以體為主，用為對辭之人與官訟之應。體卦宜旺，用卦宜衰。",
     "Xem kiện tụng: thể là chủ, dụng là người đối tụng và ứng của vụ kiện; thể nên vượng, dụng nên suy.",
     {"the_vuong": "good", "yong_suy": "good"})
topic("p.phan_mo", "k2.2.18",
      "占墳墓以體為主，用為墳墓。體克用，葬之吉；用克體，葬之凶。體生用，葬之主運退；用生體，葬之主興隆，有蔭益後嗣。體用比和，乃為吉地。",
      "Xem mồ mả: dụng là mộ; thể khắc dụng táng thì cát; dụng khắc thể táng thì hung; thể sinh dụng táng thì vận lui; dụng sinh thể táng thì hưng thịnh, ấm đến con cháu; tỷ hòa là đất tốt.",
      "墳墓", ["葬之吉", "葬之凶", "運退", "興隆/蔭益後嗣", "吉地"])
rule("p.khi_vat", "k2.5.4", "topic",
     "大抵占器物，並不喜見兌卦，蓋兌為毀折也。若坎為體，則見兌無傷。乾卦為體亦無害。其餘卦體，逢兌不久即破。",
     "Xem đồ vật đều không thích gặp Đoài vì Đoài là gãy vỡ; thể Khảm gặp Đoài không hại, thể Càn cũng không hại; thể khác gặp Đoài chẳng bao lâu thì vỡ.",
     {"兌_present": {"坎體": "無傷", "乾體": "無害", "other": "不久即破"}})
rule("p.khi_vat_ky", "k2.5.4", "ung_ky",
     "破器之日，必申酉與占卜之年月日也。",
     "Ngày đồ vỡ tất là năm tháng ngày Thân, Dậu (kể từ lúc xem).",
     {"break_date": "申/酉 year, month or day"})
rule("p.khi_vat_thanh_hui", "k2.5.4", "ung_ky",
     "又凡見器物，欲知其成毀，亦看卦體，無克者則久長。體逢克則不久，視其器物之氣數，可久者，以全卦之年數斷之；不可久者，以月數斷之；至速者，以日數斷之也。",
     "Muốn biết đồ vật bền hay hỏng cũng xem thể: không bị khắc thì lâu bền; bị khắc thì không lâu; đồ có thể lâu thì lấy số toàn quẻ làm năm, không lâu được thì làm tháng, rất nhanh thì làm ngày.",
     {"the_not_khac": "long-lasting", "the_khac": "short", "period": "全卦之數 as years / months / days by the object's nature"})
rule("p.vat_sinh_khac", "k3.3.2", "topic",
     "其所以生體者，為可食之物；克體者，為可近人之穢物。體生者，為不成之器；體克者，為破碎損折之物；比和者，乃有用成器之物",
     "(Đoán vật) quái sinh thể là vật ăn được; khắc thể là vật dơ gần người; thể sinh là đồ chưa thành; thể khắc là vật vỡ nát gãy; tỷ hòa là đồ thành dùng được.",
     {"dung_sinh_the": "可食之物", "dung_khac_the": "穢物", "the_sinh_dung": "不成之器", "the_khac_dung": "破碎損折", "ty_hoa": "有用成器"})
rule("p.vat_so_luong", "k3.3.2", "topic",
     "此互卦決其物之數目也。如互見乾、兌，決為一二之數。互見艮、坤，為七八之數也。但互卦重乾、重艮、重坤、重坎、重離之屬，皆是兩件。",
     "Hỗ quái quyết số lượng vật: hỗ thấy Càn, Đoài là số một, hai; thấy Cấn, Khôn là bảy, tám; hỗ trùng (Càn Càn, Cấn Cấn …) đều là hai cái.",
     {"count_from": "hu trigram numbers (tien_thien_so)", "doubled_hu": 2})
rule("p.vat_bien_hao", "k3.3.3", "topic",
     "又訣，觀物變在五六爻，多是能飛動之物。",
     "Đoán vật: hào biến ở hào năm, sáu phần nhiều là vật bay động được.",
     {"moving_line_in": [5, 6], "then": "飛動之物"})

# ----------------------------------------------------------------- ung_ky ---
rule("u.tien_thien", "k2.1.4", "ung_ky",
     "又先天之卦，定事應之期，則取之卦氣，如乾、兌則應如庚、辛及申金之日，或坤為戌、亥之日時，兌為酉日時。如震、巽當應於甲、乙及支木之日，或震取卯，巽取辰之類。",
     "Quẻ tiên thiên định kỳ ứng theo quái khí: Càn, Đoài ứng ngày Canh, Tân và ngày Thân Kim, hoặc Khôn là ngày giờ Tuất, Hợi, Đoài là ngày giờ Dậu; Chấn, Tốn ứng ngày Giáp, Ất và ngày chi Mộc, hoặc Chấn lấy Mão, Tốn lấy Thìn.",
     {"乾兌": ["庚", "辛", "申"], "兌": ["酉"], "震巽": ["甲", "乙", "支木 (branches not named)"], "震": ["卯"], "巽": ["辰"], "坤 (as written)": ["戌", "亥"]},
     ["U-ung-ky-kun"])
rule("u.hau_thien", "k2.1.4", "ung_ky",
     "後天則以卦數加時數，總之而分行臥坐立之遲速，以為事應之期。",
     "Quẻ hậu thiên lấy số quái cộng số giờ, rồi tùy đi, nằm, ngồi, đứng mà chia nhanh chậm để định kỳ ứng.",
     {"base": "TT[upper] + TT[lower] + hour_number (= 成卦之數)"})
rule("u.hau_thien_far", "k2.1.4", "ung_ky",
     "卦數時類，應近而不能決諸遠者，必合先後之卦數取訣可也。",
     "Số quái và loại giờ chỉ ứng việc gần, không quyết được việc xa; việc xa phải hợp số quẻ tiên thiên và hậu thiên mà quyết.",
     None, ["U-time-unit"])
rule("u.di_ngoi_dung", "k1.2.9", "ung_ky",
     "故行則應速，以逐成卦之數，中分而取其半也。坐則事應遲，當倍其成卦之數而定之也。立則半遲半速，止以成卦之數定之可也。",
     "Đi thì ứng nhanh, lấy nửa số thành quẻ; ngồi thì ứng chậm, nhân đôi số thành quẻ; đứng thì nửa nhanh nửa chậm, lấy đúng số thành quẻ.",
     {"walking": "成卦之數 / 2", "sitting": "成卦之數 × 2", "standing": "成卦之數"},
     ["U-walk-run-lie", "U-time-unit"])
rule("u.di_ngoi_dung_flex", "k1.2.9", "ung_ky",
     "雖然如是，又在變通，如占牡丹及觀梅之類，則二日花皆朝夕之故，豈特成數之久也。",
     "Tuy vậy còn phải biến thông: như xem hoa mẫu đơn, hoa mai thì hoa chỉ sớm chiều, đâu phải chờ lâu theo số thành quẻ.")
rule("u.chay_nam", "k2.1.2", "ung_ky",
     "複驗己身之動靜。坐則事應遲，行則事應速，走則愈速，臥則愈遲之類。",
     "Lại nghiệm động tĩnh của chính mình: ngồi thì việc ứng chậm, đi thì nhanh, chạy càng nhanh, nằm càng chậm.",
     {"order": ["走", "行", "立", "坐", "臥"]}, ["U-walk-run-lie"])
rule("u.sinh_the_layer", "k3.1.5", "ung_ky",
     "如生體是用卦，則事即成。生體是互卦，則漸成。生體是變卦，則稍遲耳。",
     "Quái sinh thể là dụng thì việc thành ngay; là hỗ thì thành dần; là biến thì hơi chậm.",
     {"sinh_the_in": {"yong": "即成", "hu": "漸成", "bian": "稍遲"}})
rule("u.tro_ngay", "k3.1.5", "ung_ky",
     "若有生體之卦，又有克體之卦，則事有阻節，好中不足產。便看克體卦氣阻於幾日，若乾克體，阻一日，兌克體，阻二日之類推之。",
     "Có quái sinh thể lại có quái khắc thể thì việc có trở ngại, trong tốt có chỗ thiếu; xem quái khắc thể trở mấy ngày: Càn khắc thể trở một ngày, Đoài khắc thể trở hai ngày… cứ thế suy.",
     {"delay_days": "TT[controlling trigram]"})
rule("u.sinh_khac_ngay", "k3.1.5", "ung_ky",
     "若以日期而論，看卦中有生體之卦，則事應於生體卦氣之日；有克體之卦，則事敗於克體卦氣之日。",
     "Bàn ngày tháng: có quái sinh thể thì việc ứng vào ngày của quái khí sinh thể; có quái khắc thể thì việc hỏng vào ngày của quái khí khắc thể.")
rule("u.cat_hung_nam_thang", "k3.1.11", "ung_ky",
     "若吉凶之期，但以生體及比和之年月為吉期，克體之年月為不吉之期也。",
     "Kỳ cát hung: năm tháng của quái sinh thể và tỷ hòa là kỳ cát, năm tháng của quái khắc thể là kỳ không cát.")
rule("u.toan_que_so", "k3.1.11", "ung_ky",
     "遠者，以全卦之數為年期；近者，以全卦之數為月期。又近者，以全卦為日期也。",
     "Việc xa lấy số toàn quẻ làm năm; gần thì làm tháng; gần hơn nữa thì làm ngày.",
     {"period": "全卦之數 → years | months | days by how far the matter reaches"}, ["U-time-unit"])
rule("u.vinh_vien", "k3.1.11", "ung_ky",
     "若永遠之占，則以日為月，以月為年矣。",
     "Xem việc lâu dài thì đổi ngày thành tháng, tháng thành năm.")
rule("u.vi_du_can_the", "k3.1.11", "ung_ky",
     "如問求名則乾為體，看卦中有坤、艮，則斷其辰、戌、丑、未之土月日。",
     "Như hỏi cầu danh mà Càn là thể, trong quẻ có Khôn, Cấn thì đoán vào tháng ngày Thổ Thìn, Tuất, Sửu, Mùi.",
     {"example": {"the": "乾", "producer": ["坤", "艮"], "date": ["辰", "戌", "丑", "未"]}})
rule("u.vi_du_can_benh", "k3.1.11", "ung_ky",
     "若問病而乾卦為體，則看卦中有離，又看卦中無坤、艮，及有兇犯，則其體死於巳午火日，此克體為凶事之期也。",
     "Hỏi bệnh mà Càn là thể, trong quẻ có Ly, lại không có Khôn, Cấn, và có điềm hung, thì chết vào ngày Hỏa Tỵ, Ngọ: đó là kỳ hung của quái khắc thể.",
     {"example": {"the": "乾", "controller": "離", "no_producer": ["坤", "艮"], "date": ["巳", "午"]}})
rule("u.hanh_nhan", "k3.1.11", "ung_ky",
     "又若問行人，以生體之日為歸期，無生體比和之日，則歸必遲。",
     "Hỏi người đi xa: ngày của quái sinh thể là ngày về; không có ngày sinh thể, tỷ hòa thì về tất chậm.")
rule("u.oc_trach", "k2.5.3", "ung_ky",
     "二十九年後，此屋當毀。蓋二十九年者，全卦之成數也。",
     "Hai mươi chín năm sau nhà này sẽ hư; vì hai mươi chín là số thành của toàn quẻ.",
     {"house_years": "全卦之成數 (Y+M+D+surname+H)", "golden": "jia_shu_tian"})
rule("u.vat_ngay", "k3.2.1", "ung_ky",
     "欲知應在何日，須觀爻象值數。巽五日而坤八日，離三朝而坎六朝。",
     "Muốn biết ứng vào ngày nào phải xem số của quái: Tốn năm ngày, Khôn tám ngày, Ly ba buổi sáng, Khảm sáu buổi sáng.",
     {"days": "TT[trigram]"})
rule("u.vat_xa_gan", "k3.2.1", "ung_ky",
     "又觀遠近克應，以斷得買之相期。應遠，則全卦相同；應近，而各時同斷。假如天地否卦，上天一而下地八；設若澤火革卦，上兌二而下離三。",
     "Lại xem khắc ứng xa gần: ứng xa thì cộng cả quẻ, ứng gần thì đoán từng quái; như quẻ Thiên Địa Bĩ thì trên Càn 1 dưới Khôn 8; quẻ Trạch Hỏa Cách thì trên Đoài 2 dưới Ly 3.",
     {"far": "TT[upper] + TT[lower]", "near": "each trigram number separately"}, ["U-time-unit"])
for tri, han in [
    ("乾", "時序：秋、九十月之交、戌亥年月日時、一四九年月日時。"),
    ("坤", "時序：辰戌丑未月、未申年月日時、八五十月日。"),
    ("震", "時序：春三月、卯年月日時、四三八月日。"),
    ("巽", "時序：春夏之交、三五八之時月日、辰巳月日時。"),
    ("坎", "時序：冬十一月、子年月日時、一六月日。"),
    ("離", "時序：夏五月、午火年月日時、三二七日。"),
    ("艮", "時序：冬春之月、十二月丑寅年月日時、七五十數月日、土年月日時。"),
    ("兌", "時序：秋八月、酉年月日時、二四九月日。"),
]:
    rule(f"u.thoi_tu.{TT[tri]}", "k1.3.2", "ung_ky", han,
         f"Thời tự (thời điểm thuộc quái {tri}), dùng khi sách bảo «xét theo thời tự của bát quái» để định ngày.",
         {"trigram": tri})

# --------------------------------------------------------------- examples ---
for gid, sec, han in [
    ("guan_mei", "k1.2.4", "辰年十二月十七日申時，康節先生偶觀梅，見二雀爭枝墜地。"),
    ("mu_dan", "k1.2.5", "巳年三月十六日卯時，先生與客往司馬公家共觀牡丹。"),
    ("lin_ye_kou_men", "k1.2.6", "以一聲屬乾為上卦，以五聲屬巽為下卦"),
    ("jin_ri_dong_jing", "k1.2.7", "有客問曰：「今日動靜如何？」逐將此六字占之。"),
    ("xi_lin_si", "k1.2.8", "先生偶見西林寺之額，「林」字無兩勾，因占之"),
    ("lao_ren_you_se", "k1.2.9", "己丑日卯時，偶在途行，有老人往巽方，有憂色。"),
    ("shao_nian_xi_se", "k1.2.10", "壬申日午時，有少年從離方來，喜形於色"),
    ("niu_ai_ming", "k1.2.11", "癸卯日午時，有牛鳴于坎方，聲極悲，因占之。"),
    ("ji_bei_ming", "k1.2.12", "甲申日卯時，有雞鳴于乾方，聲極悲愴，因占之。"),
    ("ku_zhi_zhui_di", "k1.2.13", "戊子日辰時，偶行至中途，有樹蔚然，無風，枯枝自墜地于兌方。"),
    ("jia_shu_wang", "k2.5.2", "寅年十二月初一日午時，有數家起造，俱在鄰市之間。"),
    ("bing_pi_line1", "k2.2.16", "又問乾上坤下，占病如何斷"),
    ("bian_shi_1_ge", "k3.1.4", "澤火革體金，互巽木變澤山鹹"),
    ("yong_yi_tai", "k3.3.7", "有人以籠盛物者，算得地天泰之初變升"),
]:
    rule(f"e.{gid}", sec, "example", han,
         "Ví dụ của sách; đầu vào và kết quả ghi trong engine/tests/golden/mai_hoa_book_examples.json.",
         {"golden": gid})

UNDEFINED = [
    {"id": "U-leap-month", "where": "k1.1.14", "issue": "年月日時起例 counts 正月…十二月 as 1–12 and says nothing about 閏月 (leap months)."},
    {"id": "U-year-boundary", "where": "k1.1.14", "issue": "The year number is the year branch (子1…亥12); the book does not say when the year changes (正月初一 or 立春)."},
    {"id": "U-hour-boundary", "where": "k1.1.14", "issue": "Hours are counted 子1…亥12; the book does not say where 子時 starts, nor whether the day changes at 子時 (23:00) or at midnight."},
    {"id": "U-month-branch", "where": "k1.1.4, k2.4.2.4", "issue": "旺/衰 are given by season and by 寅卯/巳午/申酉/亥子/辰戌丑未 months; the book does not say whether these month branches follow the lunar month number (正月 = 寅) or the solar terms (節氣)."},
    {"id": "U-season-months", "where": "k1.1.4, k1.1.5", "issue": "卦氣旺 names seasons (春 夏 秋 冬) and separately 辰戌丑未月 for 土, so 辰 (the third spring month) is both 春 and 土 there; 時令之應 (k2.4.2.4) resolves it by branch (寅卯 木, 辰 土), which is the reading the rules use."},
    {"id": "U-vuong-month-or-day", "where": "k2.4.2.4, k2.4.10, k3.4.1", "issue": "時令之應 says 「月日」 and 靜占 says 「年月日」; the book does not say whether 旺衰 is judged by month, by day or by both, nor how to combine them. 日應 judges the day separately."},
    {"id": "U-trigram-multiple-of-8", "where": "k1.1.11", "issue": "「如得八數整，即坤卦」 is stated for exactly 8; for 16, 24 … the repeated subtraction 「直至除盡」 leaves 0 and the text does not say 0 → 坤 in so many words (it is the natural reading)."},
    {"id": "U-line-zero", "where": "k1.1.12", "issue": "爻以六除 does not say what happens when the total is a multiple of 6 (remainder 0); line 6 is the natural reading, by analogy with 八數整 → 坤, but it is not stated."},
    {"id": "U-zi-hour", "where": "k1.1.17, k1.1.18, k1.2.7, k1.2.8", "issue": "The word/stroke methods do not say whether the hour is added for the moving line; the two word examples (今日動靜如何, 西林寺) do not add it, while 爻以六除 says 「取爻當以時加之」."},
    {"id": "U-zi-count", "where": "k1.1.18, k1.2.8, k2.5.2", "issue": "For 2–3 characters the book does not say what is counted; 西林寺 counts strokes. The book's stroke counts differ from dictionary counts (西 7, 林 8 without the two hooks / 10 with them, 田 6, 韓 21), and the counting convention is not described."},
    {"id": "U-one-char-left-right", "where": "k1.1.18", "issue": "One character: strokes on the left are 陽 (upper trigram), on the right 陰 (lower trigram); only 彳 丿 (left) and 一 乙 、 (right) are given as examples, so splitting an arbitrary character is not defined."},
    {"id": "U-tones", "where": "k1.1.18, k1.2.7", "issue": "4–10 characters use the four tones 平上去入 (1–4); the book does not say which pronunciation fixes the tone (the example treats 日 as 入聲, a Middle-Chinese category absent from Mandarin)."},
    {"id": "U-vat-so-gua-shu", "where": "k1.1.15", "issue": "物數占例: 「以卦數並時數總除六」 — 卦數 may mean the raw count or the trigram number after mod 8; not stated."},
    {"id": "U-sheng-yin-lower", "where": "k1.1.16, k1.2.6", "issue": "聲音占例 says count → upper, count + hour → lower, and does not state the moving line; the 鄰夜扣門 example uses two runs of knocks for upper and lower and adds the hour only to the line."},
    {"id": "U-measure-hour", "where": "k1.1.19, k1.1.20", "issue": "丈尺占 takes the line from 丈+尺 without the hour, 尺寸占 from 尺+寸+hour; the book does not explain the difference."},
    {"id": "U-hu-qian-kun", "where": "k1.1.13", "issue": "「乾坤無互，互其變卦」: the book does not say which hexagrams count as 乾坤 here (only 乾為天 and 坤為地, whose 互 would repeat themselves, is the natural reading)."},
    {"id": "U-hu-source", "where": "k2.2.16", "issue": "In 疾病占, 乾上坤下 with the 2nd line moving, the book gives 互 巽、離 — the 互 of the changed hexagram 天水訟, not of 否 (巽、艮). Every other worked example takes 互 from the original hexagram. Not resolved."},
    {"id": "U-duo", "where": "k2.2.1, k2.2.6, k2.2.12, k2.2.13", "issue": "「多」 (many) in 天時/生產/出行/行人 is not quantified, and the book only says the count runs over 「互變卦」 (not whether 體/用 themselves and both 互 count)."},
    {"id": "U-dang-count", "where": "k2.1.7", "issue": "體黨/用黨 are defined only by the all-same-element case (互變皆金); partial cases are not defined."},
    {"id": "U-yang-gua", "where": "k2.2.6", "issue": "生產: 「陽卦陽爻多者則生男」 — this text does not define which trigrams are 陽卦 (卷三 八卦定陰陽次序 only lists the family roles)."},
    {"id": "U-hon-nhan-mao", "where": "k2.2.5", "issue": "The appearance list in 婚姻占 does not say which trigram (用? 變?) it is read from."},
    {"id": "U-chu-gua", "where": "k2.2.16", "issue": "「和平之日，主卦決之」: 主卦 is presumably 體 (體卦為主) but not stated."},
    {"id": "U-ung-ky-kun", "where": "k2.1.4", "issue": "先天 應期 lists 「坤為戌、亥之日時」 among the 金 trigrams; 戌亥 is 乾's branch pair elsewhere (八卦萬物屬類 乾: 戌亥年月日時), so 坤 here is probably an error for 乾. 震巽 → 「支木之日」 does not name the branches (寅卯 by 十二地支)."},
    {"id": "U-walk-run-lie", "where": "k2.1.2, k1.2.9", "issue": "走 (愈速) and 臥 (愈遲) have no factor; only 行 ½, 立 ×1, 坐 ×2 are quantified. The worked examples do not consistently apply the walking half (枯枝墜地占: walking, full 10)."},
    {"id": "U-time-unit", "where": "k2.1.4, k3.1.11, k3.2.1", "issue": "Whether a period number is days, months or years is left to judgement of how far the matter reaches (遠/近/永遠); no rule fixes it."},
    {"id": "U-xian-hou-yaoci", "where": "k2.1.2, k2.1.4", "issue": "占卜總決 says to read the 爻辭 first for every cast, while 先天後天論 says 先天 casts hardly use 爻辭 (「不甚用」); the two are not reconciled in the text."},
]


def main() -> None:
    src = json.loads(SRC.read_text())
    sec = {s["id"]: s for s in src["sections"]}
    ids, out, bad = set(), [], []
    und_ids = {u["id"] for u in UNDEFINED}
    for rid, section, kind, han, vi, formula, flags in R:
        if rid in ids:
            bad.append(f"duplicate id {rid}")
        ids.add(rid)
        if section not in sec:
            bad.append(f"{rid}: unknown section {section}")
            continue
        if han not in sec[section]["text"]:
            bad.append(f"{rid}: quote not in {section}: {han[:30]}")
        for f in flags or []:
            if f != "appendix" and f not in und_ids:
                bad.append(f"{rid}: unknown flag {f}")
        item = {"id": rid, "section": section, "path": sec[section]["path"], "kind": kind,
                "han_quote": han, "vi": vi}
        if formula is not None:
            item["formula"] = formula
        if rid in REL_VI:
            han_rel = split_relations(rid, han)
            if set(han_rel) != set(REL_VI[rid]):
                bad.append(f"{rid}: relation keys differ: han {sorted(han_rel)} vi {sorted(REL_VI[rid])}")
            for k, v in han_rel.items():
                if v not in han:
                    bad.append(f"{rid}: {k} clause not in quote")
            item["han_by_relation"] = han_rel
            item["vi_by_relation"] = {k: REL_VI[rid][k] for k in REL_KEYS if k in REL_VI[rid]}
        elif kind == "topic" and formula and set(REL_KEYS) & set(formula):
            bad.append(f"{rid}: topic rule with relations but no REL_VI entry")
        if flags:
            item["undefined"] = [f for f in flags if f != "appendix"]
            if "appendix" in flags:
                item["appendix"] = True
        out.append(item)
    if bad:
        raise SystemExit("\n".join(bad))
    doc = {
        "source": "WEB:zh_meihua (source_zh.json)",
        "dich_gia": "Thiên Bàn",
        "status": "draft",
        "note": ("Rules extracted from 梅花易數 (Wikisource 卷一–三). Each han_quote is an exact substring of its section's text. "
                 "`formula` restates the quote in computable form and adds nothing the quote does not say, except where a note says how "
                 "a worked example fixes a reading. Points the book leaves open are listed in `undefined` and referenced by id from the rules; "
                 "they are not filled in here. `appendix: true` marks rules from the main page's 附錄 (季本's remarks), which is not part of 卷一–三. "
                 "Built by tools/mai_hoa_rules_build.py."),
        "kinds": ["casting", "the_dung", "vuong_suy", "topic", "ung_ky", "example"],
        "undefined": UNDEFINED,
        "rules": out,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    from collections import Counter
    print(f"wrote {OUT}: {len(out)} rules", dict(Counter(r['kind'] for r in out)))


if __name__ == "__main__":
    main()
