"""Which texts a cast is read by: Chu Hy's 考變占 (易學啟蒙). One school only; the others are listed in data, not computed.

易學啟蒙 itself is not in the saved sources (not on Wikisource; ctext needs a key). Its clauses are read where two later books quote them:
胡煦 周易函書 約存卷七 (each 啟蒙 clause, then his objection 煦按) and 韓邦奇 啓蒙意見 卷四 (七占), which marks the clauses he keeps 仍舊.
Both are in WEB:zh_iching_methods. Ngô Tất Tố's quẻ Kiền (Bản nghĩa of Chu Hy and the note after it) agrees on 0, 3 and 6 lines.

  0 moving  占本卦彖辭，以內卦為貞，外卦為悔                       (啓蒙意見: 凡卦六爻皆不變…, 此二條仍舊)
  1         占本卦變爻辭                                              (函書; 啓蒙意見 仍舊)
  2         占本卦二變爻辭，以上爻為主                                (函書: 二爻變則占本卦二變爻以上爻為主)
  3         占本卦及之卦彖辭，本卦為貞，之卦為悔；有初爻變者主本卦  (函書: 三爻變則占本卦及之卦彖辭 … 凡三爻變而有初爻變者則占本彖辭)
  4         占之卦二不變爻，以下爻為主                                (函書: 四變爻則占之卦二不變爻以下爻為主)
  5         占之卦不變爻                                              (函書: 五爻變則以之卦不變爻占)
  6         乾坤占二用，餘卦占之卦彖辭                                (函書; 啓蒙意見 此亦仍舊)

For 3 lines the 函書 passage gives 前十卦主貞，後十卦主悔 and explains it (黃葵峯): of the 20 ways three lines can move, the 10 in which hào 1
moves are the 前十卦, read mainly by the quẻ chủ's thoán; the other 10 by the quẻ biến's. 胡煦 restates it as 凡三爻變而有初爻變者則占本彖辭,
三爻變而初爻不變者則占之卦彖辭. That is what is implemented."""
from __future__ import annotations

from .tables import HANSHU, METHODS, NTT_WS, YIJIAN, cite

SCHOOL = "chu_hy_khai_mong"
SCHOOL_VI = "Chu Hy, Dịch học khải mông (phép khảo biến chiêm)"

CITES = {
    0: [cite(METHODS, YIJIAN, "凡卦六爻皆不變則占本卦彖辭而以内卦為貞外卦為悔"),
        cite(NTT_WS, "Kinh Dịch/Chu Dịch thượng kinh/Quẻ Kiền", "hễ được quẻ ấy mà cả sáu hào không biến")],
    1: [cite(METHODS, HANSHU, "一爻變則占本卦變爻辭"), cite(METHODS, YIJIAN, "一爻變則以本卦變爻辭占")],
    2: [cite(METHODS, HANSHU, "二爻變則占本卦二變爻以上爻為主")],
    3: [cite(METHODS, HANSHU, "三爻變則占本卦及之卦彖辭而以本卦為貞之卦為悔"),
        cite(METHODS, HANSHU, "總之凡三爻變而有初爻變者則占本彖辭"),
        cite(METHODS, HANSHU, "三爻變而初爻不變者則占之卦彖辭"),
        cite(NTT_WS, "Kinh Dịch/Chu Dịch thượng kinh/Quẻ Kiền", "quẻ Kiền biến đi ba hào, hay là ba hào quẻ khác biến sang quẻ Kiền, cũng lấy câu đó mà đoán")],
    4: [cite(METHODS, HANSHU, "四變爻則占之卦二不變爻以下爻為主")],
    5: [cite(METHODS, HANSHU, "五爻變則以之卦不變爻占")],
    6: [cite(METHODS, HANSHU, "六爻變則乾坤占二用"), cite(METHODS, YIJIAN, "六爻變乾坤占二用餘占之卦之彖辭")],
}


def text_ref(hexagram: int, kind: str, hao: int | None = None) -> dict:
    """kind: thoan (lời quẻ), hao (lời hào), dung (dụng cửu / dụng lục)."""
    r = {"hexagram": hexagram, "kind": kind}
    if hao is not None:
        r["hao"] = hao
    return r


def resolve(cast: dict) -> dict:
    """cast: core.cast(...). Returns the main text, the other texts to read with it, and the rule applied."""
    moving = cast["moving"]
    n = len(moving)
    ban = cast["ban"]["number"]
    bien = cast["bien"]["number"] if cast["bien"] else None
    still = [p for p in range(1, 7) if p not in moving]
    if n == 0:
        main, also = text_ref(ban, "thoan"), []
        note = "nội quái là trinh, ngoại quái là hối"
    elif n == 1:
        main, also = text_ref(ban, "hao", moving[0]), []
        note = ""
    elif n == 2:
        main, also = text_ref(ban, "hao", moving[1]), [text_ref(ban, "hao", moving[0])]
        note = "hào trên làm chủ"
    elif n == 3:
        if 1 in moving:
            main, also = text_ref(ban, "thoan"), [text_ref(bien, "thoan")]
            note = "có hào Đầu động: lời quẻ chủ làm chủ, quẻ chủ là trinh, quẻ biến là hối"
        else:
            main, also = text_ref(bien, "thoan"), [text_ref(ban, "thoan")]
            note = "hào Đầu không động: lời quẻ biến làm chủ, quẻ chủ là trinh, quẻ biến là hối"
    elif n == 4:
        main, also = text_ref(bien, "hao", still[0]), [text_ref(bien, "hao", still[1])]
        note = "hai hào không động của quẻ biến, hào dưới làm chủ"
    elif n == 5:
        main, also = text_ref(bien, "hao", still[0]), []
        note = "hào không động của quẻ biến"
    else:
        if ban in (1, 2):
            main, also = text_ref(ban, "dung"), []
            note = "Kiền dùng Chín, Khôn dùng Sáu"
        else:
            main, also = text_ref(bien, "thoan"), []
            note = "lời quẻ biến"
    return {"school": SCHOOL, "school_vi": SCHOOL_VI, "moving_count": n, "main": main, "also": also, "note": note, "cites": CITES[n]}


# Other schools for the same number of moving lines, shown in Đọc sâu only (never used to choose the text): 程迥 (Trình Hồi, 沙隨) 考古占例
# as 周易函書 quotes it, and 韓邦奇's rules marked 新定 in 啓蒙意見 (he keeps Chu Hy's clauses for 0, 1 and 6 lines). The Vietnamese is the
# system's gloss of the quoted clause.
OTHER_SCHOOLS = {
    "trinh_hoi": {"name": "Trình Hồi (程迥), Khảo cổ chiêm lệ", "chapter": HANSHU, "rules": {
        0: ("六爻不變以卦彖占内卦為貞外卦為悔", "không hào nào động: xem lời quẻ, nội quái là trinh, ngoại quái là hối"),
        1: ("一爻變以變爻占", "một hào động: xem lời hào động"),
        2: ("二爻三爻四爻變以本卦為貞之卦為悔", "hai đến bốn hào động: quẻ chủ là trinh, quẻ biến là hối, không chọn riêng một lời"),
        3: ("二爻三爻四爻變以本卦為貞之卦為悔", "hai đến bốn hào động: quẻ chủ là trinh, quẻ biến là hối, không chọn riêng một lời"),
        4: ("二爻三爻四爻變以本卦為貞之卦為悔", "hai đến bốn hào động: quẻ chủ là trinh, quẻ biến là hối, không chọn riêng một lời"),
        5: ("五爻變以不變爻占", "năm hào động: xem hào không động"),
        6: ("六爻變以乾坤二用為例", "sáu hào động: theo lệ dùng Chín, dùng Sáu của Kiền, Khôn"),
    }},
    "han_bang_ky": {"name": "Hàn Bang Kỳ (韓邦奇), Khải mông ý kiến", "chapter": YIJIAN, "rules": {
        2: ("二爻變則以本卦二變爻辭占仍以下爻為主", "hai hào động: xem hai lời hào của quẻ chủ, hào dưới làm chủ (Chu Hy lấy hào trên)"),
        3: ("三爻變前十卦占本卦變爻辭後十卦占之卦變爻辭", "ba hào động: xem lời các hào động, ở quẻ chủ hay quẻ biến tùy vị trí (Chu Hy xem lời quẻ)"),
        4: ("四爻變占之卦變爻辭主上二爻", "bốn hào động: xem lời các hào đã biến của quẻ biến, hai hào trên làm chủ (Chu Hy xem hai hào không động)"),
        5: ("五爻變則以之卦變爻辭占", "năm hào động: xem lời các hào đã biến của quẻ biến (Chu Hy xem hào không động)"),
    }},
}


def other_schools(moving_count: int) -> list[dict]:
    out = []
    for key, sc in OTHER_SCHOOLS.items():
        r = sc["rules"].get(moving_count)
        if r:
            out.append({"school": key, "name": sc["name"], "han": r[0], "vi": r[1], "cite": cite(METHODS, sc["chapter"], r[0])})
    return out
