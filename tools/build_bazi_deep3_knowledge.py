"""DEEP-3 (2026-10-24): the Bát Tự knowledge files that hold method, not chart judgements:
  engine/data/bazi_deep/hyky.json      dụng / hỉ / kỵ / cừu / nhàn thần: what each is, how the books choose the dụng thần, the element map of the five
                                       roles (TTT p.167, computable), cát / hung and phú / bần / quý / tiện by dụng and kỵ (TVH pp.161-173), position
                                       of hỉ and kỵ, bệnh / dược, hợp / xung, luck principles; each entry with book, page, printed quote and the
                                       rule ids (pack_*_kin.json) that carry it into a reading;
  engine/data/bazi_deep/thanh_pha.json cách thành / phá / cứu: per cách the TVH thành bại sentences (tvh_thanhbai.json) and dụng thần row
                                       (tvh_dungthan.json), Trích Thiên Tủy's thanh / trọc, chân / giả thần and phá cách; the 子平真詮 (TBCT) column
                                       stays draft (no public-domain snapshot could be saved: see sources_web/zipingzhenquan.json);
  engine/data/bazi_deep/schools.json   the points where TTT, TVH, ZZ and 窮通寶鑑 (CTBG, web snapshot) disagree, each side with its page / chapter.
Every quote is checked by engine/tests/test_bazi_deep3_mining.py against the committed page text (mined/) or the web snapshot (sources_web/).
    .venv/bin/python tools/build_bazi_deep3_knowledge.py"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "engine" / "data" / "bazi_deep"
CTBG = D / "dieu_hau_ctbg_draft.json"      # its 'snapshot' / 'disagreements': the 120 穷通宝鉴 cells read from the web snapshot (quote per cell)


def q(book, page, quote, vi, **kw):
    """one sourced statement: book ttt / tvh / zz (page 'p.N', quote on mined/<book>_pN.txt) or WEB:<id> (page = chapter)"""
    return {"book": book, "page": page, "quote": quote, "vi": vi, **kw}


# ======================================================================= hyky.json
HYKY = {
    "_status": "verified",
    "_note": ("DEEP-3 (2026-10-24). Logic of dụng / hỉ / kỵ / cừu / nhàn thần as Trích Thiên Tủy (ttt), Thiệu Vĩ Hoa (tvh) and 八字真宗 (zz) print it. "
              "Every entry: book, page, printed quote (checked against data/bazi_deep/mined/<book>_pN.txt by tests), Vietnamese gist (vi). 'rules' = the "
              "ids in pack_{ttt,tvh,zz}_kin.json that carry the entry into a reading (facts.bazi.deep.kin findings, topics yong / fortune / wealth / rank / "
              "character / children / study). Numeric measures behind 'vượng / nhược' of a group are the system's (25 % / 12 % of TVH degrees), not a page's. "
              "The engine's dụng / hỉ / kỵ come from Thiệu Vĩ Hoa's cách table (pp.378-386; tvh_dungthan.json): the TTT choice (topic 'yong') is told "
              "beside it, never in place of it."),
    "roles": {
        "dung": [q("ttt", "p.63", "Dụng là dụng thần, ngoài thể dụng ra là dụng thần vậy", "Dụng thần: chữ lá số dùng để đưa nhật chủ về thế cân."),
                 q("ttt", "p.64", "Trong mệnh chỉ có hỉ dụng hai chữ, có dụng thần, nhật chủ đáng mừng, trưóc sau dựa vào dụng thần vậy",
                   "Cả lá số xoay quanh dụng thần.")],
        "hi": [q("ttt", "p.143", "Hỉ thần, là phụ dụng thần trợ chủ", "Hỉ thần: chữ phò dụng thần, giúp nhật chủ."),
               q("ttt", "p.167", "hỉ thần là thần trợ cách phụ dụng vậy", "Hỉ thần giúp cách, phò dụng."),
               q("ttt", "p.143", "cho nên hỉ thần chính là cát thần vậy", "Hỉ thần là chữ lành.")],
        "ky": [q("ttt", "p.144", "Kỵ thần, là thần làm tổn hại dụng thần", "Kỵ thần: chữ làm hại dụng thần."),
               q("ttt", "p.167", "kỵ thần, là thần phá cách tổn dụng vậy", "Kỵ thần phá cách, làm hại dụng.")],
        "nhan": [q("ttt", "p.167", "Trong tứ trụ ngoài dụng thần, hỉ thần, kỵ thần đều là Nhàn thần", "Nhàn thần: mọi chữ còn lại."),
                 q("ttt", "p.167", "Nhàn thần không hại thể dụng, không làm trở ngại hỉ thần, cũng không nên động đến nó vậy",
                   "Nhàn thần không hại thì không nên động đến."),
                 q("ttt", "p.167", "được nhàn thần chế hóa hung thần kỵ vật của tuế vận, phụ giúp hỉ dụng cách cục",
                   "Khi vận, năm đem chữ kỵ đến, nhàn thần có thể chế hóa nó, thành 'người nhà'."),
                 q("ttt", "p.64", "trừ dụng thần, hỉ thần, kỵ thần ra thì còn lại đều là nhàn thần khách thần vậy", "Nhàn thần, khách thần: phần còn lại.")],
        "cuu": [q("ttt", "p.167", "lấy thủy làm Cừu thần", "Cừu thần: chữ sinh cho kỵ thần (trong ví dụ dụng Mộc có dư: Thủy sinh Kim kỵ thần).")],
        "many": [q("ttt", "p.167", "Hỉ thần chẳng nên nhiều vậy, một hỉ mà được 10 hỉ; Kỵ thần cũng chẳng nên nhiều vậy, một kị mà bị 10 hại vậy",
                   "Một chữ hỉ đắc lực bằng mười, một chữ kỵ đắc lực hại bằng mười.")],
    },
    # TTT p.167: the five roles from the dụng element, in two cases. Relations: 'X sinh' = the element X produces, 'sinh X' = the element producing X,
    # 'X khắc' = the element X controls, 'khắc X' = the element controlling X. Reproduced by the test for the page's own example (dụng Mộc).
    "role_map": {
        "source": q("ttt", "p.167", "Như dụng mộc, mộc có dư, lấy hỏa làm Hỉ thần, lấy kim làm Kỵ thần, lấy thủy làm Cừu thần, lấy thổ làm Nhàn thần; mộc "
                    "không đủ, lấy thủy làm hỉ thần, thổ làm kỵ thần, lấy kim làm cừu thần, lấy hỏa làm nhàn thần",
                    "Dụng có dư: hỉ là chữ nó sinh ra, kỵ là chữ khắc nó, cừu là chữ sinh ra nó, nhàn là chữ nó khắc. Dụng không đủ: hỉ là chữ sinh ra nó, "
                    "kỵ là chữ nó khắc, cừu là chữ khắc nó, nhàn là chữ nó sinh ra."),
        "du": {"hi": "dung_sinh", "ky": "khac_dung", "cuu": "sinh_dung", "nhan": "dung_khac"},
        "thieu": {"hi": "sinh_dung", "ky": "dung_khac", "cuu": "khac_dung", "nhan": "dung_sinh"},
        "example": {"dung": "Mộc", "du": {"hi": "Hỏa", "ky": "Kim", "cuu": "Thủy", "nhan": "Thổ"}, "thieu": {"hi": "Thủy", "ky": "Thổ", "cuu": "Kim", "nhan": "Hỏa"}},
        "note": "'Có dư / không đủ' của dụng thần: sách không cho thước đo; hệ thống chưa dùng bảng này để chọn hỉ / kỵ (vẫn theo bảng cách TVH).",
    },
    "order": [q("ttt", "p.59", "Trước xem có đắc lệnh tháng, sau xem thiên can có thấu lộ, kế tiếp xem sinh vượng để định chân giả, cuối cùng mới đến thủ dụng, phân thanh trọc",
                "Thứ tự xem: lệnh tháng → can thấu → sinh vượng (chân / giả) → chọn dụng → phân thanh trọc."),
              q("ttt", "p.67", "Khí tượng, cách cục, dụng thần đều lệ thuộc vào đề cương tháng", "Khí tượng, cách cục, dụng thần đều dựa vào chi tháng."),
              q("tvh", "p.161", "Quy luật chung là: căn cứ can ngày mạnh hay yếu, dụng thần có lực hay không để thấy được giàu nghèo, sang hèn",
                "Giàu nghèo sang hèn xem ở nhật chủ mạnh yếu và dụng thần có lực hay không.")],
    "chanh_bien": [q("ttt", "p.59", "Chánh cách tức gồm đủ ngũ hành sinh khắc thường tình như quan sanh ấn, sát sanh ấn, tài sanh sát, thực chế sát, thực sanh tài, thương quan bội ấn, thương quan sanh tài",
                     "Chính cách: sinh khắc thường tình (Quan sinh Ấn, Sát sinh Ấn, Tài sinh Sát, Thực chế Sát, Thực sinh Tài, Thương bội Ấn, Thương sinh Tài)."),
                   q("ttt", "p.59", "biến cách nhất định phải tòng khí thế của ngũ hành", "Biến cách: thuận theo khí thế (các cách tòng).")],
    "dung_rules": {
        "TTT60": q("ttt", "p.60", "Nhật chủ vượng cần nên chế, suy cần nên tương trợ, ấn vượng tiết quan cần có tài, ấn suy phùng tài nên có kiếp, dụng pháp này không thay đổi",
                   "Vượng thì chế, suy thì trợ; Ấn vượng làm tiết Quan thì cần Tài; Ấn suy gặp Tài thì cần Kiếp."),
        "TTT63_core": q("ttt", "p.63", "Vượng tất nên ức, nhược tất nên phù", "Vượng thì ức, nhược thì phù."),
        "TTT63_reverse": [q("ttt", "p.63", "Vượng nên ức nhưng không thể ức, phản lại nên phù; nhược nên phù nhưng không thể phù, phản lại nên ức",
                            "Cực vượng không ức được thì thuận mà phù; cực nhược không phù được thì thuận mà ức."),
                          q("ttt", "p.63", "Cực cường vượng bị ức mà có hại, tất nên tòng cường mà phù cường; cực nhược được phù, phù mà uổng công vô dụng, tất nên tòng nhược mà ức nhược",
                            "Cực cường thì tòng cường; cực nhược thì tòng nhược."),
                          q("ttt", "p.76", "“vượng cực không thể tổn, suy cực không thể sinh”", "Vượng cực không thể tổn, suy cực không thể sinh.")],
        "TTT111": [q("ttt", "p.111", "Chỉ có thể thuận theo khí thế mà dẫn thông, cho nên khí lưu hành gặp phú hĩ, nếu miễn cưỡng khắc chế, chọc giận cường thần, chắc chắn gặp phải điều dữ",
                     "Thế mạnh tập trung thì thuận mà dẫn thông, cưỡng chế sẽ chọc giận nó."),
                   q("ttt", "p.111", "cho nên chế sát không bằng hóa sát", "Với Sát: hóa (bằng Ấn) hơn chế.")],
        "TVH167": q("tvh", "p.167", "Thân vượng mới có thể lấy quan tinh làm dụng thần", "Chỉ khi thân vượng mới lấy Quan làm dụng thần (khác tr.173: schools.json)."),
    },
    # TTT Thể Dụng p.63 (+ Cương Nhu p.109, Phản cục p.188): the dụng-thần table; 'rule' carries it (topic 'yong', meta 'yong' = the group)
    "dung_table": [
        dict(q("ttt", "p.63", "Nếu như nhật chủ vượng, đề cương hoặc quan hoặc tài hoặc thực thương, đều có thể làm dụng thần; nhật chủ suy, đặc biệt tìm tứ trụ can chi có trợ nhật chủ làm dụng thần",
               "Nhật chủ vượng: Quan, Tài hoặc Thực Thương ở chi tháng đều làm dụng được; nhật chủ suy: tìm chữ trợ nhật chủ."), id="T01", rule=None),
        dict(q("ttt", "p.63", "Nhật chủ làm thể, nhật chủ vượng, ấn thụ nhiều, cần phải lấy tài tinh làm dụng thần", "Vượng, Ấn nhiều → Tài."), id="T02", rule="BT_TTTK_DT01", dung="Tai"),
        dict(q("ttt", "p.63", "nhật chủ vượng, quan sát khinh, cũng lấy tài tinh làm dụng thần", "Vượng, Quan Sát nhẹ → Tài."), id="T03", rule="BT_TTTK_DT02", dung="Tai"),
        dict(q("ttt", "p.63", "Nhật chủ vượng, tỉ kiếp nhiều, gánh được tài tinh, lấy thực thương làm dụng thần", "Vượng, Tỉ Kiếp nhiều, gánh được Tài → Thực Thương."), id="T04", rule="BT_TTTK_DT03", dung="ThucThuong"),
        dict(q("ttt", "p.63", "nhật chủ vượng, tỉ kiếp nhiều, mà tài tinh khinh, cũng lấy thực thương làm dụng thần", "Vượng, Tỉ Kiếp nhiều, Tài nhẹ → Thực Thương."), id="T05", rule="BT_TTTK_DT04", dung="ThucThuong"),
        dict(q("ttt", "p.63", "Nhật chủ vượng, quan tinh khinh, ấn thụ trọng điệp, lấy tài tinh làm dụng thần", "Vượng, Quan nhẹ, Ấn trùng điệp → Tài."), id="T06", rule="BT_TTTK_DT05", dung="Tai"),
        dict(q("ttt", "p.63", "Nhật chủ nhược, thực thương nhiều, lấy ấn thụ làm dụng thần", "Nhược, Thực Thương nhiều → Ấn."), id="T07", rule="BT_TTTK_DT06", dung="An"),
        dict(q("ttt", "p.63", "nhật chủ nhược, tài tinh vượng, tất lấy tỉ kiếp làm dụng thần", "Nhược, Tài vượng → Tỉ Kiếp."), id="T08", rule="BT_TTTK_DT07", dung="Ti"),
        dict(q("ttt", "p.63", "Nhật chủ cùng quan sát cân bằng, tất lấy thực thương làm dụng thần", "Nhật chủ ngang Quan Sát → Thực Thương."), id="T09", rule=None, dung="ThucThuong",
             why_no_rule="'Cân bằng' không có thước đo trong sách."),
        dict(q("ttt", "p.63", "nhật chủ cùng tài tinh cân bằng, tất lấy ấn thụ làm dụng thần", "Nhật chủ ngang Tài → Ấn."), id="T10", rule=None, dung="An",
             why_no_rule="'Cân bằng' không có thước đo trong sách."),
        dict(q("ttt", "p.63", "Nếu như tứ trụ can chi tài sát thái vượng, nhật chủ vượng biến thành nhược, cần tìm trợ nhật chủ chế hóa tài sát làm dụng thần",
               "Tài Sát quá vượng: lấy chữ trợ nhật chủ, chế hóa Tài Sát."), id="T11", rule=None),
        dict(q("ttt", "p.63", "hóa thần thật, tức lấy hóa thần làm thể. Hóa thần có lực, tất lấy hóa thần làm dụng; hóa thần không đủ lực, tất lấy sanh trợ hóa thần làm dụng thần",
               "Hóa cách: hóa thần có lực thì dùng nó, thiếu lực thì dùng chữ sinh nó."), id="T12", rule=None),
        dict(q("ttt", "p.63", "lấy sanh trợ khí tượng làm dụng thần, hoặc lấy thực thương làm dụng thần, hoặc lấy tài tinh làm dụng thần, chỉ không nên dụng quan sát",
               "Năm cách khúc trực (một hành): dùng chữ sinh trợ khí tượng, Thực Thương hoặc Tài, không dùng Quan Sát."), id="T13", rule=None),
        dict(q("ttt", "p.109", "Nói chung đắc thời đương lệnh, tứ trụ không có khắc chế, dụng thực thần thuận theo khí thế, tiết kỳ tinh anh",
               "Đắc lệnh, không có chữ khắc chế → Thực Thần, thuận khí thế."), id="T14", rule="BT_TTTK_DT08", dung="ThucThuong"),
        dict(q("ttt", "p.188", "trong cục Ấn thụ tuy vượng, trong trụ Tài tinh có khí, có thể dụng Tài phá Ấn vậy", "Ấn vượng, Tài có khí → Tài phá Ấn."), id="T15", rule="BT_TTTK_DT09", dung="Tai"),
        dict(q("ttt", "p.188", "Mẫu từ diệt Tử, dẫu có Tài tinh mà vô khí, không thể lấy Tài tinh phá Ấn vậy", "Ấn vượng, Tài vô khí → thuận Ấn, đi đất Tỉ Kiếp."), id="T16", rule="BT_TTTK_DT10", dung="Ti"),
    ],
    "hi_by_dung": [q("ttt", "p.143", "Dụng Quan, nếu thân vượng có thể lấy Tài làm hỉ thần; thân nhược dụng Ấn, rồi sau đó lấy Quan làm hỉ thần",
                     "Dùng Quan khi thân vượng thì Tài là hỉ; thân nhược dùng Ấn thì Quan là hỉ.")],
    "no_dung": [q("ttt", "p.61", "Không theo cách cục vẫn có thể thủ dụng, không có dụng thần vẫn có thể tìm ở vận trình", "Không có dụng thần trong trụ thì tìm ở vận."),
                q("ttt", "p.64", "Tóm lại, có dụng thần hay không có dụng thần, nhất định vẫn có một chỗ dụng, chắc chắn không đổi vậy", "Lá số nào cũng có một chỗ để dùng.")],
    "dung_disabled": [q("ttt", "p.63", "hoặc bị nhàn thần hợp mất, hoặc bị xung làm tổn thương, hoặc bị kỵ thần cướp giật chiếm giữ, hoặc khách thần ngăn trở",
                        "Dụng thần mất tác dụng khi bị hợp mất, bị xung, bị kỵ thần chiếm, bị khách thần ngăn."),
                      q("ttt", "p.64", "Nếu đắc tuế vận phá đi hợp thần, hợp mất xung thần, chế kỵ thần, thông cách thần, thì tuế vận đó sẽ yên ổn",
                        "Vận, năm gỡ được các thế ấy thì yên.")],
    "dung_position": [q("ttt", "p.64", "cho nên thiên can dễ xem, địa chi khó suy ra", "Dụng thần ở can dễ xem; ở chi khó suy.")],
    "position": {
        "quotes": [q("ttt", "p.101", "hỉ thần nên đắc địa phùng sanh, cùng nhật chủ kề cận là cát lợi; kỵ thần nên thất thế lâm tuyệt địa, cùng nhật chủ xa cách thì đẹp vậy",
                     "Hỉ gần nhật chủ là tốt, kỵ xa nhật chủ là tốt."),
                   q("ttt", "p.165", "Về phần thần đáng ghét, may mắn là ở xa; còn thần yêu thích, gần thì càng thân thiết", "Chữ ghét ở xa, chữ thương ở gần.")],
        "rules": ["BT_TTTK_HK06", "BT_TTTK_HK07"], "near_dm": ["day.branch", "month.stem", "hour.stem"],
    },
    "verdicts": {
        "ttt": [dict(q("ttt", "p.143", "không có hỉ thần mà dụng thần đắc lệnh hùng tráng, đại thế kiên cố, tứ trụ an hòa, dụng thần đứng cạnh, không tranh không đố, tức gặp kỵ thần cũng không hung hiểm",
                       "Dụng thần nắm lệnh và mạnh: gặp kỵ cũng không hung."), rule="BT_TTTK_HK01"),
                dict(q("ttt", "p.143", "Như nguyên cục không có hỷ thần, có kỵ thần (hoặc ám phục hoặc xuất hiện), hoặc đứng sát bên dụng thần",
                       "Không có hỉ mà kỵ đứng sát dụng: dễ hung khi vận dẫn kỵ."), rule="BT_TTTK_HK02"),
                dict(q("ttt", "p.144", "Tài Quan vô khí, dụng thần vô lực, chẳng qua không thể phát đạt được mà thôi, cũng không có hình hung vậy",
                       "Tài Quan và dụng thần yếu: chỉ không phát đạt, không có hung."), rule="BT_TTTK_HK03"),
                dict(q("ttt", "p.67", "hỉ thần đắc lệnh thì cát lợi", "Hỉ thần nắm lệnh tháng: cát."), rule="BT_TTTK_HK05"),
                dict(q("ttt", "p.105", "Nói nhật chủ có dụng thần, nắm lệnh tại đề cương, lại thấu xuất thiên can gọi là tụ đắc chân thần, cuộc đời phú quý hĩ",
                       "Dụng thần nắm lệnh lại thấu can: chân thần, phú quý."), rule="BT_TTTK_CT01")],
        "tvh_cat_hung": {"cat": [dict(q("tvh", "p.170", "Dụng thần có sinh hoặc có bảo vệ, tránh bị khắc tổn thương", "Cát: dụng thần được sinh, được giữ, không bị khắc."), rule=None),
                                 dict(q("tvh", "p.170", "Dụng thần ở thiên can không bị khắc hợp; dụng thần ở địa chi không bị khắc, hợp, hình, xung",
                                        "Cát: dụng ở can không bị khắc hợp; ở chi không bị khắc, hợp, hình, xung."), rule=None)]
                                + [dict(x, rule=r) for x, r in (
                                    (q("tvh", "p.170", "Thân vượng dụng thần là tài, có thực thương sinh tài; hoặc có quan sát bảo vệ tài", "Vượng, dụng Tài có nguồn / có giữ."), "BT_TVHK_CH01"),
                                    (q("tvh", "p.170", "Thân vượng dụng thần là quan, hoặc có ấn bảo vệ quan", "Vượng, dụng Quan có Ấn giữ."), None),
                                    (q("tvh", "p.170", "Thân vượng, dụng thần là sát, sát nặng có thực thương chế ngự; hoặc sát nhẹ có tài sinh", "Vượng, dụng Sát có chế / có sinh."), "BT_TVHK_CH02"),
                                    (q("tvh", "p.170", "Thân vượng, dụng thần là thực thương, có tài lưu thông và bảo vệ thực thương, đều là cát", "Vượng, dụng Thực Thương có Tài."), "BT_TVHK_CH03"),
                                    (q("tvh", "p.170", "Thân nhược, dụng thần là tỉ kiếp, quan tinh nặng, có ấn sinh thân xì hơi quan", "Nhược, dụng Tỉ Kiếp, Quan nặng có Ấn."), "BT_TVHK_CH04"),
                                    (q("tvh", "p.170", "Thân nhược, dụng thần là tỉ kiếp, tài tinh nặng, có quan xì hơi tài sinh ấn", "Nhược, dụng Tỉ Kiếp, Tài nặng có Quan."), None),
                                    (q("tvh", "p.170", "Thân nhược, dụng thần là tỉ kiếp, thực thương nặng, có ấn chế ngự thực thương mà sinh thân", "Nhược, dụng Tỉ Kiếp, Thực Thương nặng có Ấn."), "BT_TVHK_CH05"),
                                    (q("tvh", "p.170", "Thân nhược, dụng thần là ấn, có quan tinh sinh ấn; hoặc tỉ kiếp bảo vệ ấn", "Nhược, dụng Ấn có Quan sinh / Tỉ giữ."), "BT_TVHK_CH06"))],
                         "hung": [dict(q("tvh", "p.171", "Không có dụng thần hoặc bị hóa mất dụng thần hoặc dụng thần không được sinh hoặc dụng thần bị khắc", "Hung: mất dụng thần hoặc dụng bị khắc."), rule=None),
                                  dict(q("tvh", "p.171", "Kị thần nhiều quá, hoặc kị thần không bị chế ngự, hoặc kị thần được sinh", "Hung: kỵ nhiều, không bị chế, được sinh."), rule=None)]
                                 + [dict(q("tvh", "p.171", t, v), rule=r) for t, v, r in (
                                     ("Tài nặng: tài vượng, thân nhược, kiếp và ấn nhẹ", "Tài nặng.", "BT_TVHK_CH10"),
                                     ("Tài nhẹ: dụng thần là tài, tài nhẹ còn kiếp nặng, ấn nặng", "Tài nhẹ.", "BT_TVHK_CH11"),
                                     ("Quan nặng: quan nhiều, thân nhược lại không có ấn", "Quan nặng.", "BT_TVHK_CH12"),
                                     ("Quan nhẹ: dụng thần là quan, ấn nặng", "Quan nhẹ.", "BT_TVHK_CH13"),
                                     ("Sát nặng: thân nhẹ lại không có thực thương, ấn thụ", "Sát nặng.", "BT_TVHK_CH14"),
                                     ("Sát nhẹ: dụng thần là sát, sát nhẹ không chế ngự được nặng lại còn không có tài", "Sát nhẹ.", "BT_TVHK_CH15"),
                                     ("Ấn nặng: ấn kiếp đều nặng mà quan thì nhẹ", "Ấn nặng.", "BT_TVHK_CH16"),
                                     ("Ấn nhẹ: dụng thần là ấn mà gặp tài nhiều", "Ấn nhẹ.", "BT_TVHK_CH17"),
                                     ("Thực thương nặng: Thực thương nhiều lại không có ấn", "Thực Thương nặng.", "BT_TVHK_CH18"),
                                     ("Thực thương nhẹ: dụng thần là thực thương lại gặp nhiều kiêu thần", "Thực Thương nhẹ.", "BT_TVHK_CH19"),
                                     ("Tỉ kiếp nặng: Tứ trụ tỉ kiếp nhiều mà không có quan sát", "Tỉ Kiếp nặng.", "BT_TVHK_CH20"),
                                     ("Tỉ kiếp nhẹ: Dụng thần là tỉ kiếp mà quan sát nhiều", "Tỉ Kiếp nhẹ.", "BT_TVHK_CH21"))]},
        # TVH p.173: the six verdicts by strength and dụng / kỵ group ('càng vượng càng ...')
        "tvh_p173": [dict(q("tvh", "p.173", t, v), dm=dm, role=role, groups=g, verdict=vd, rule=r) for t, v, dm, role, g, vd, r in (
            ("Giàu: nhật chủ mạnh, tài tinh là dụng thần, tài tinh càng vượng càng giàu", "Mạnh, dụng Tài: giàu.", "vuong", "dung", ["Tai"], "giau", "BT_TVHK_W03"),
            ("Nhật chủ yếu, tỉ kiếp là dụng thần. Tỉ kiếp càng vượng càng giàu", "Yếu, dụng Tỉ Kiếp: giàu.", "nhuoc", "dung", ["Ti"], "giau", "BT_TVHK_F44"),
            ("Sang: nhật chủ nhược, quan sát là dụng thần. Quan sát càng vượng càng sang", "Nhược, dụng Quan Sát: sang (mâu thuẫn tr.167).", "nhuoc", "dung", ["QuanSat"], "sang", None),
            ("Nhật chủ nhược, ấn tinh là dụng thần. Ấn tinh càng vượng càng sang", "Nhược, dụng Ấn: sang.", "nhuoc", "dung", ["An"], "sang", "BT_TVHK_F45"),
            ("Cát: nhật chủ mạnh, cái áp chế, làm hao tổn, xì hơi nhật chủ là dụng thần. Dụng thần được sinh vượng thì càng tốt", "Mạnh, dụng Quan / Tài / Thực Thương: cát.",
             "vuong", "dung", ["QuanSat", "Tai", "ThucThuong"], "cat", None),
            ("Nhật chủ nhược, cái sinh phù nhật chủ là dụng thần. Dụng thần được sinh vượng thì càng cát", "Nhược, dụng Ấn / Tỉ: cát.", "nhuoc", "dung", ["An", "Ti"], "cat", None),
            ("Nghèo: Nhật chủ mạnh, tỉ kiếp là kị thần. Kị thần càng vượng càng nghèo", "Mạnh, kỵ Tỉ Kiếp: nghèo.", "vuong", "ky", ["Ti"], "ngheo", "BT_TVHK_F40"),
            ("Nhật chủ nhược, tài tinh là kị thần. Tài tinh càng vượng càng nghèo", "Nhược, kỵ Tài: nghèo.", "nhuoc", "ky", ["Tai"], "ngheo", "BT_TVHK_F41"),
            ("Hèn: nhật chủ mạnh, ấn tinh là kị thần. Ấn tinh càng vượng càng hèn", "Mạnh, kỵ Ấn: hèn.", "vuong", "ky", ["An"], "hen", "BT_TVHK_F42"),
            ("Nhật chủ nhược, quan sát là kị thần. Quan sát càng vượng càng hèn", "Nhược, kỵ Quan Sát: hèn.", "nhuoc", "ky", ["QuanSat"], "hen", "BT_TVHK_F43"),
            ("Hung: nhật chủ mạnh, cái sinh phù là kị thần. Kị thần càng vượng càng hung", "Mạnh, kỵ Ấn / Tỉ: hung.", "vuong", "ky", ["An", "Ti"], "hung", None),
            ("Nhật chủ nhược, cái khắc, xì hơi, hao tổn nhật chủ là kị thần. Kị thần càng vượng càng hung", "Nhược, kỵ Quan / Thực Thương / Tài: hung.", "nhuoc", "ky",
             ["QuanSat", "ThucThuong", "Tai"], "hung", None))],
        "timing": [q("tvh", "p.162", "Lúc mà họ cất đầu lên được cũng là lúc dụng thần phát huy tác dụng, còn lúc rủi ro, khốn khó là lúc dụng thần đang bị khắc",
                     "Lúc lên là lúc dụng thần được trợ; lúc khó là lúc dụng thần bị khắc."),
                   q("tvh", "p.173", "đại vận tốt mà lưu niên không tốt, đại vận không tốt mà lưu niên tốt là còn có cứu. Ngược lại, đại vận đã xấu, lưu niên cũng xấu là không có cứu",
                     "Vận và năm một tốt một xấu: còn cứu; cả hai xấu: không cứu.")],
    },
    "benh_duoc": [q("ttt", "p.144", "Lấy kỵ thần là bệnh, hỉ thần là dược, bệnh có dược chữa là cát, có bệnh mà không có dược là hung", "Kỵ là bệnh, hỉ là thuốc."),
                  q("ttt", "p.77", "có bệnh rõ ràng mà dễ dàng chọn, không có bệnh mà khó đoán", "Có bệnh rõ thì dễ chọn dụng; không bệnh thì khó đoán.")],
    "ton_ich": [q("ttt", "p.65", "Có thừa cần nên bớt đi, không đủ cần nên bồi thêm", "Thừa thì bớt, thiếu thì bù."),
                q("ttt", "p.65", "đại khái có thừa quá mức, nếu tổn phản lại kích động phẫn nộ, tất nên thuận theo mà tiết đi", "Thừa quá thì tiết, đừng khắc.")],
    "strength_notes": [q("ttt", "p.70", "nhật chủ không luận hưu tù nguyệt lệnh, chỉ cần tứ trụ hữu căn, liền có thể đảm nhận tài quan thực thương thất sát",
                         "Nhật chủ có gốc thì gánh được Tài Quan, dù thất lệnh."),
                       q("ttt", "p.70", "nhiều can không bằng thông căn nơi địa chi", "Nhiều can trợ không bằng một gốc ở chi.")],
    "trung_hoa": [q("ttt", "p.77", "Tức đắc trung hòa chánh khí, danh lợi làm sao mà không toại được", "Được trung hòa thì danh lợi dễ toại.")],
    "mon_dia": [q("ttt", "p.67", "thiên can không thấu xuất hỏa thổ mà thấu thủy mộc, thì môn (can) suy địa vượng", "Tháng Dần: can thấu và chi nắm lệnh khác nhau thì cát hung nửa nọ nửa kia.")],
    "phan_uc": [q("ttt", "p.163", "chỗ dụng đều đắc khí, hỉ thần đều đắc lực, kỵ thần đều thất thế", "Phấn phát khi dụng đắc khí, hỉ có lực, kỵ thất thế.")],
    "an_oan": [q("ttt", "p.165", "Ân oán, là Hỉ Kỵ vậy", "Ân oán là hỉ kỵ: chữ hỉ xa được hợp kéo gần là ân; bị kỵ ngăn là oán.")],
    "hop_xung": [q("ttt", "p.168", "Hợp mà không hóa, thì giống như bị lưu luyến ràng buộc", "Tham hợp không hóa: bị ràng buộc."),
                 q("ttt", "p.169", "Đoạn này chính là đắc dụng phùng xung vậy", "Dụng thần được xung gỡ ra thì nhật chủ tự do."),
                 q("ttt", "p.194", "Hợp có nên và không nên, không nên hợp nhiều", "Hợp có nên có không; không nên hợp nhiều."),
                 q("ttt", "p.192", "Thiên chiến còn có thể, Địa chiến gấp như hỏa", "Can chiến còn chịu được, chi chiến thì gấp."),
                 q("ttt", "p.192", "Cho nên thiên can luận là khắc, địa chi nói xung, xung tức là khắc vậy", "Can luận khắc, chi luận xung.")],
    "phan_cuc": [q("ttt", "p.186", "Quân dựa vào Thần sinh, ý nói Ấn thụ quá vượng vậy", "Ấn quá vượng thì dùng Tài (phản cục)."),
                 q("ttt", "p.186", "Phá Ấn mà tựu Tài, là ý phạm thượng, cho nên gọi là Phản cục vậy", "Phá Ấn để dùng Tài gọi là phản cục."),
                 q("ttt", "p.190", "kim khắc mộc, gọi là chồng khỏe mà sợ vợ vậy", "Phu kiện phạ thê: nhật chủ mạnh mà Tài sinh Quan khắc lại.")],
    "tong_luck": [q("ttt", "p.183", "là lấy Tòng Nhi cách tối kỵ Ấn vận, kế đến là Quan vận", "Tòng Nhi kỵ nhất vận Ấn, sau là vận Quan."),
                  q("ttt", "p.185", "Phàm Tòng Nhi cách, hành vận không nghịch, gặp Tài không thể không có phú quý vậy", "Tòng Nhi gặp Tài, vận thuận: phú quý.")],
    "cuong_nhu": [q("ttt", "p.109", "Khắc, tiết, dẫn, tòng bốn chữ nên nghiên cứu kỹ càng", "Bốn cách xử: khắc, tiết, dẫn, tòng.")],
    "luck_principles": [q("ttt", "p.229", "Phú quý tuy định ở cách cục, cũng phải gắn liền với vận đồ thuận lợi nữa, chỗ gọi là Mệnh tốt không bằng vận tốt vậy", "Mệnh tốt không bằng vận tốt."),
                        q("ttt", "p.229", "Cho nên lấy địa chi làm trọng", "Đại vận: lấy chi làm trọng."),
                        q("ttt", "p.229", "thiên can sinh địa chi mà phúc dày, địa chi sinh thiên can mà khí tiết", "Can vận sinh chi vận thì phúc dày; chi sinh can thì khí tiết."),
                        q("ttt", "p.61", "nếu chánh cách dụng chân mà gặp vận hành bội phản, trọn đời có chí mà vất vả", "Cách chính, dụng thật mà vận ngược: có chí mà vất vả."),
                        q("ttt", "p.163", "Nhưng cục dù âm hối, mà vận đồ phối hợp dương minh, cũng có thể thông suốt", "Cục u uất mà vận sáng cũng thông được.")],
    "luck_year": [q("ttt", "p.231", "Chiến là khắc vậy. Như vận Bính năm Canh, là vận khắc Tuế", "Chiến: can vận khắc can năm (hoặc ngược lại); cát hung theo nhật chủ hỉ chữ nào."),
                  q("ttt", "p.232", "Xung là phá vậy. Như vận Tý năm Ngọ, gọi là vận xung tuế", "Xung: chi vận xung chi năm."),
                  q("ttt", "p.232", "Hòa là Hợp vậy", "Hòa: vận và năm hợp; hợp hóa ra chữ hỉ thì cát."),
                  q("ttt", "p.233", "Tốt, là loại tương đồng vậy", "Hảo: vận và năm cùng loại (lộc, cùng hành).")],
    "zz_element_state": [q("zz", "p.27", "以得令、得位、得生为旺，以失令、失位、无生为弱", "Một hành vượng khi đắc lệnh, đắc vị, được sinh; yếu khi thất lệnh, thất vị, không được sinh.")],
}

# ======================================================================= thanh_pha.json (sources)
TTT_BY_CACH = {
    "Chính Quan": [dict(q("ttt", "p.101", "Như chánh quan cách, thân nhược có ấn, kỵ tài, tài tinh không hiện, có thể thấy ngay là thanh hĩ",
                          "Chính Quan cách, thân nhược có Ấn, Tài không lộ: thanh."), side="thanh"),
                   dict(q("ttt", "p.101", "tất tài sanh quan, quan sanh ấn, ấn sanh nhật chủ", "Có Tài mà Tài → Quan → Ấn → nhật chủ liền mạch thì vẫn thanh."), side="cuu"),
                   dict(q("ttt", "p.101", "Như chánh quan cách, thân vượng mừng có tài, mà kỵ ấn thụ, tiếp theo kỵ thương quan",
                          "Chính Quan cách, thân vượng: mừng Tài, kỵ Ấn rồi đến Thương Quan."), side="thanh"),
                   dict(q("ttt", "p.101", "Như thương quan cùng tài tinh cách xa, ngược lại thương quan kế cận quan tinh, tài không đủ lực sanh quan",
                          "Thương Quan sát Quan mà Tài ở xa: phá."), side="pha")],
}
THANH_PHA = {
    "_status": "verified (TVH, TTT) / draft (TBCT)",
    "_note": ("DEEP-3 (2026-10-24). Cách thành / phá / cứu per cách. 'tvh': the Thiệu Vĩ Hoa thành bại sentences (tvh_thanhbai.json, pp.367-369: ids, "
              "verdict, the system's encoding) and the cách's row of the dụng thần table (tvh_dungthan.json, pp.378-386); 'ttt': Trích Thiên Tủy's own "
              "words where a page speaks of that cách; 'tbct': the 子平真詮 conditions of geju_defs.json, still written from memory: NO public-domain "
              "snapshot of 子平真詮 could be saved (zh.wikisource has none; ctext blocks automated access, its terms forbid scraping), so this column "
              "stays draft and is not voiced. 'general': the TTT principles that apply to every cách (thanh / trọc, chân / giả thần, phá cách and cứu)."),
    "cach": {},
    "general": {
        "pha_cach": [q("ttt", "p.61", "phá cách tổn hại dụng thần, thì có bệnh vậy, ưu sầu nhiều vui mừng ít", "Cách bị phá, dụng thần bị hại: bệnh, buồn nhiều vui ít."),
                     q("ttt", "p.61", "Nhưng nếu hành vận thích hợp, khử mất kỵ thần, sanh trợ dụng thần giống như người bệnh lâu ngày được thầy thuốc giỏi cứu chữa, không phú cũng quý",
                       "Cứu: vận khử kỵ thần, trợ dụng thần thì không phú cũng quý."),
                     q("ttt", "p.61", "Đại phàm cách cục thuần nhất, trăm mệnh không có được một vậy", "Cách thuần nhất trăm người không được một.")],
        "no_clash_kho": [q("ttt", "p.61", "Lại cho rằng tạp khí tài quan cần nên xung thật là hàm hồ", "Không phải tạp khí Tài Quan cần xung mới dùng."),
                         q("ttt", "p.62", "Cho nên luận mộ khố gặp xung tất phát thật sai lầm vậy", "Mộ khố gặp xung chưa chắc phát."),
                         q("ttt", "p.70", "mà không biết hình xung tất thương tổn căn khí", "Hình xung làm tổn gốc.")],
        "thanh": [q("ttt", "p.101", "Thanh mà hữu khí, tất tinh thần thông suốt mà đầy đủ; thanh mà vô khí, tất tinh thần khô héo tiều tụy", "Thanh phải có khí mới tốt.")],
        "troc": {"quotes": [q("ttt", "p.103", "Nhâm thị viết: Trọc gọi là tứ trụ hỗn tạp vậy", "Trọc: tứ trụ hỗn tạp."),
                            q("ttt", "p.103", "tuy thành bại không đều, có nhiều hiểm trở, nhưng ngộ đắc hành vận, khử đi trọc khí, cũng có cơ hội khởi phát",
                              "Trọc: thành bại không đều; gặp vận khử trọc thì khởi phát."),
                            q("ttt", "p.103", "thà rằng dụng trong thanh có trọc, không thể dụng trong thanh có khô", "Thà thanh lẫn trọc, không thể thanh mà khô.")],
                 "rules": ["BT_TTTK_TR01", "BT_TTTK_TR02", "BT_TTTK_TR03", "BT_TTTK_TR04"]},
        "chan_gia": {"quotes": [q("ttt", "p.105", "Nói nhật chủ có dụng thần, nắm lệnh tại đề cương, lại thấu xuất thiên can gọi là tụ đắc chân thần, cuộc đời phú quý hĩ",
                                  "Chân thần: dụng thần nắm lệnh và thấu can."),
                                q("ttt", "p.105", "Nhưng nếu kề sát chân thần, hoặc tương khắc tương xung chân thần, hoặc hợp chân thần, ám hóa kỵ thần, chung thân lục đục",
                                  "Giả thần kề sát, khắc, xung, hợp chân thần: cả đời lục đục."),
                                q("ttt", "p.107", "Hết thảy đều do an hưởng phúc đức, phần nhiều do chân thần đắc dụng; sang nghiệp hưng gia, khó nhọc mà thiếu an nhàn, phần nhiều do giả thần đắc cục",
                                  "Chân thần đắc dụng: hưởng phúc; giả thần đắc cục: lập nghiệp vất vả.")],
                     "rules": ["BT_TTTK_CT01", "BT_TTTK_CT02"]},
    },
}
# ======================================================================= schools.json (sources)
SCHOOLS = {
    "_status": "verified",
    "_note": ("DEEP-3 (2026-10-24). Points where the Bát Tự sources disagree, each side with book and page (or web chapter). Books: ttt = Trích Thiên Tủy "
              "(bản dịch Việt), tvh = Thiệu Vĩ Hoa, Dự Đoán Theo Tứ Trụ, zz = 八字真宗, WEB:CTBG = 穷通宝鉴 (zh.wikisource snapshot, sources_web/). "
              "'engine' says which side the engine follows today."),
    "points": [
        {"id": "children_star", "topic": "sao con cái",
         "sides": [dict(q("ttt", "p.130", "Như hỉ thần là Quan tinh, con cái hiền tài", "Nguyên chú: xem con cái theo Quan."), who="TTT nguyên chú"),
                   dict(q("ttt", "p.130", "Nay sửa đổi lấy Thực Thương làm con", "Nhâm thị: lấy Thực Thương làm con."), who="TTT Nhâm thị"),
                   dict(q("ttt", "p.131", "Nói chung, thân vượng lấy Tài là con, thân suy lấy Ấn là con", "Nhâm thị (thêm): thân vượng lấy Tài, thân suy lấy Ấn làm con."), who="TTT Nhâm thị"),
                   dict(q("ttt", "p.132", "phàm dụng thần bát tự là Tử tức tinh", "Nhâm thị (kết): dụng thần là sao con."), who="TTT Nhâm thị")],
         "engine": "Bát Tự Chân Tông tr.60 (sao con theo giới tính) cho chỗ đứng; luật con cái DEEP-3 theo chi giờ (TVH tr.158) và TTT tr.130 (hai câu không nói số, giới)."},
        {"id": "an_vuong_than_vuong", "topic": "thân vượng, Ấn vượng",
         "sides": [q("tvh", "p.527", "Thân vượng, ấn vượng là tiền hao tán không tụ", "Về tiền: hao tán."),
                   q("tvh", "p.553", "Thân vượng ấn vượng là hiển đạt cao quý", "Về danh: hiển đạt."),
                   q("tvh", "p.173", "Hèn: nhật chủ mạnh, ấn tinh là kị thần. Ấn tinh càng vượng càng hèn", "Theo dụng thần: Ấn là kỵ thì càng vượng càng hèn.")],
         "engine": "BT_TVHK_W12 (tiền) và BT_TVHK_F42 (Ấn kỵ) đứng; BT_TVHK_D09 (hiển đạt) chỉ khi Ấn không phải chữ kỵ."},
        {"id": "quan_dung_strength", "topic": "lấy Quan Sát làm dụng thần khi nào",
         "sides": [q("tvh", "p.167", "Thân vượng mới có thể lấy quan tinh làm dụng thần", "Chỉ khi thân vượng."),
                   q("tvh", "p.173", "Sang: nhật chủ nhược, quan sát là dụng thần. Quan sát càng vượng càng sang", "Bảng tr.173 in 'nhược' (có lẽ in nhầm)."),
                   q("ttt", "p.143", "Dụng Quan, nếu thân vượng có thể lấy Tài làm hỉ thần", "TTT: dùng Quan khi thân vượng.")],
         "engine": "Dòng 'Sang' của tr.173 không đóng gói (mâu thuẫn tr.167 và TTT tr.143)."},
        {"id": "ren_table", "topic": "bảng dương nhận (刃) của can âm",
         "sides": [q("zz", "p.28", "看月支又是日干的禄星或刃星，才属此项直断", "Bảng tr.28: 乙刃辰, 丁刃未, 己刃未, 辛刃戌, 癸刃丑 (thuận sau lộc)."),
                   q("zz", "p.72", "羊刃煞（临七柱）直断", "Bảng tr.72 (đang dùng cho mọi luật khác): 乙刃寅, 丁己刃巳, 辛刃申, 癸刃亥 (nghịch trước lộc).")],
         "engine": "Luật 日月合化 (BT_ZZK_HH*) theo bảng tr.28 của chính mục ấy; các luật khác theo tr.72."},
        {"id": "tai_many_dm_weak", "topic": "Tài nhiều, thân nhược",
         "sides": [q("ttt", "p.191", "Nếu như nhật chủ không kiện, gọi là Tài đa thân nhược, cuối cùng là thân khốn khổ vậy", "TTT: khốn khổ."),
                   q("tvh", "p.522", "Tài nhiều gặp tỉ kiếp trợ giúp là nhà giàu thịnh vượng", "TVH: có Tỉ Kiếp đỡ thì lại giàu.")],
         "engine": "BT_TVHK_G03 / W11 khi không có Tỉ Kiếp, BT_TVHK_W08 khi có."},
        {"id": "kieu_doat_thuc", "topic": "Thiên Ấn gặp Thực Thần",
         "sides": [q("tvh", "p.527", "Thực thần gặp kiêu là tài vật hao tán", "TVH: hao tán."),
                   q("ttt", "p.63", "Nhật chủ nhược, thực thương nhiều, lấy ấn thụ làm dụng thần", "TTT cùng câu: thân nhược Thực Thương nhiều thì Ấn là dụng, không cứ luận 'kiêu đoạt thực'.")],
         "engine": "BT_TVHK_W13 theo tổ hợp; BT_TTTK_DT06 nói dụng thần TTT bên cạnh."},
        {"id": "dung_choice", "topic": "chọn dụng thần: bảng cách TVH và Thể Dụng TTT",
         "sides": [q("tvh", "p.161", "Quy luật chung là: căn cứ can ngày mạnh hay yếu, dụng thần có lực hay không để thấy được giàu nghèo, sang hèn", "TVH: bảng dụng thần theo cách (tr.378-386)."),
                   q("ttt", "p.63", "Vượng tất nên ức, nhược tất nên phù", "TTT: phù ức theo Thể Dụng, có đảo ngược khi cực vượng / cực nhược.")],
         "engine": "Bảng cách TVH quyết định hỉ / kỵ; TTT (topic 'yong') nói bên cạnh; tỉ lệ trùng đo trong docs/audit/DEEP-3-mining-bazi.md."},
        {"id": "dieu_hau_ctbg_vs_tvh", "topic": "điều hậu: bảng TVH (tr.389-390) và 穷通宝鉴", "cells": None,
         "engine": "Tập can theo bảng TVH, thứ tự theo chú thích TVH tr.391-396; ô 穷通宝鉴 chỉ để so (dieu_hau_ctbg_draft.json 'snapshot')."},
    ],
}


# ======================================================================= published shapes (asked by the main session for prose/bazi_deep.ts, 2026-10-24)
# hyky.json      {"version", "principles": [{id, topic, when: {dm, group, role, relation}, text, book, page | chapter, quote, reviewStatus, ...}], "role_map"}
# thanh_pha.json {"version", "cach": [{cach, thanh: [...], pha: [...], cuu: [...], reviewStatus}], "general": [...], "tbct_draft": {...}}
# schools.json   {"version", "topics": [{id, topic, kind, sides: [{school, statement, cite, quote, book, page | chapter}], engine}]}
# Extra keys beside the asked ones: result (what the statement concludes), rules (kin rule ids that voice it), section, conditions (rule DSL),
# engine_id (tvh_thanhbai.json id), engine_when (its machine condition).
VERSION = "1.0.0"
BOOK = {"ttt": "TTT", "tvh": "TVH", "zz": "ZZ"}
GVI = {"Tai": "Tài", "QuanSat": "Quan Sát", "An": "Ấn", "Ti": "Tỉ Kiếp", "ThucThuong": "Thực Thương"}


def pub(o: dict) -> dict:
    b = o["book"]
    out = {"book": BOOK.get(b, b)}
    if b.startswith("WEB:"):
        out["chapter"] = o["page"]
    else:
        out["page"] = int(str(o["page"]).removeprefix("p."))
    out["quote"] = o["quote"]
    return out


def cite(o: dict) -> str:
    return f"{o['book']} {o['chapter']}" if "chapter" in o else f"{o['book']} tr.{o['page']}"


def W(dm=None, group=None, role=None, relation=None) -> dict:
    return {"dm": dm, "group": group, "role": role, "relation": relation}


PRINC: list[dict] = []
_n: dict = {}


def P(section: str, topic: str, o: dict, when: dict | None = None, **extra) -> None:
    src = pub(o)
    key = f"{src['book']}_{section.upper()}"
    _n[key] = _n.get(key, 0) + 1
    PRINC.append({"id": f"{key}_{_n[key]:02d}", "topic": topic, "when": when or W(), "text": o["vi"], **src, "reviewStatus": "verified",
                  "section": section, **{k: v for k, v in extra.items() if v is not None}})


H = HYKY
for o in H["roles"]["dung"]:
    P("roles", "dung", o)
for o in H["roles"]["hi"] + H["roles"]["many"]:
    P("roles", "hy", o)
for o in H["roles"]["ky"]:
    P("roles", "ky", o)
for o in H["roles"]["nhan"]:
    P("roles", "nhan", o)
for o in H["roles"]["cuu"]:
    P("roles", "cuu", o)
P("role_map", "cuu", H["role_map"]["source"], result={"role_map": "see top-level role_map"})
for sec in ("order", "chanh_bien", "no_dung", "dung_disabled", "dung_position", "strength_notes", "trung_hoa", "mon_dia", "ton_ich", "cuong_nhu",
            "phan_cuc", "tong_luck", "luck_principles", "luck_year", "zz_element_state", "hop_xung"):
    for o in H[sec]:
        P(sec, "dung", o)
for k, v in H["dung_rules"].items():
    for o in (v if isinstance(v, list) else [v]):
        P("dung_rules", "dung", o, W(dm="vuong") if k == "TVH167" else None, result={"dung": "Quan Sát"} if k == "TVH167" else None)
for o in H["benh_duoc"]:
    P("benh_duoc", "ky", o)
for o in H["phan_uc"] + H["an_oan"]:
    P("phan_uc_an_oan", "hy", o)
hb = H["hi_by_dung"][0]
P("hi_by_dung", "hy", hb, W("vuong", "Quan Sát", "yong"), result={"hy": "Tài"})
P("hi_by_dung", "hy", hb, W("nhuoc", "Ấn", "yong"), result={"hy": "Quan Sát"})
# the TTT dụng table: 'when.group' is the group whose weight sets the row (with 'state'); result.dung is the group this book takes
DT_WHEN = {"T01": (None, None, None), "T02": ("vuong", "Ấn", "nhieu"), "T03": ("vuong", "Quan Sát", "nhe"), "T04": ("vuong", "Tỉ Kiếp", "nhieu"),
           "T05": ("vuong", "Tỉ Kiếp", "nhieu"), "T06": ("vuong", "Ấn", "nhieu"), "T07": ("nhuoc", "Thực Thương", "nhieu"), "T08": ("nhuoc", "Tài", "vuong"),
           "T09": (None, "Quan Sát", "can_bang"), "T10": (None, "Tài", "can_bang"), "T11": (None, None, None), "T12": (None, None, None),
           "T13": (None, None, None), "T14": ("vuong", None, None), "T15": (None, "Ấn", "vuong"), "T16": (None, "Ấn", "vuong")}
_, _, KMETA = None, None, {}
for b in ("ttt", "tvh", "zz"):
    KMETA |= json.loads((D / f"quotes_{b}_kin.json").read_text("utf-8"))
KPACK = {}
for b in ("ttt", "tvh", "zz"):
    KPACK |= {r["id"]: r for r in json.loads((D / f"pack_{b}_kin.json").read_text("utf-8"))["rules"]}
for row in H["dung_table"]:
    dm, g, st = DT_WHEN[row["id"]]
    P("dung_table", "dung", row, W(dm, g), state=st, result={"dung": GVI[row["dung"]]} if row.get("dung") else None,
      rules=[row["rule"]] if row.get("rule") else None, conditions=KPACK[row["rule"]]["conditions"] if row.get("rule") else None,
      why_no_rule=row.get("why_no_rule"))
TOPIC_OF = {"BT_TTTK_HK01": ("dung", W(role="yong")), "BT_TTTK_HK02": ("ky", W(role="ky", relation="khac")), "BT_TTTK_HK03": ("dung", W(role="yong")),
            "BT_TTTK_HK05": ("hy", W(role="hy")), "BT_TTTK_CT01": ("dung", W(role="yong"))}
for v in H["verdicts"]["ttt"]:
    t, w = TOPIC_OF[v["rule"]]
    P("verdicts", t, v, w, rules=[v["rule"]], conditions=KPACK[v["rule"]]["conditions"])
CAT_WHEN = {"BT_TVHK_CH01": ("vuong", "Tài"), "BT_TVHK_CH02": ("vuong", "Quan Sát"), "BT_TVHK_CH03": ("vuong", "Thực Thương"),
            "BT_TVHK_CH04": ("nhuoc", "Tỉ Kiếp"), "BT_TVHK_CH05": ("nhuoc", "Tỉ Kiếp"), "BT_TVHK_CH06": ("nhuoc", "Ấn")}
CAT_TEXT_WHEN = {"Thân vượng dụng thần là quan": ("vuong", "Quan Sát"), "Thân nhược, dụng thần là tỉ kiếp, tài tinh nặng": ("nhuoc", "Tỉ Kiếp")}
for v in H["verdicts"]["tvh_cat_hung"]["cat"]:
    dm, g = CAT_WHEN.get(v.get("rule"), next((x for k, x in CAT_TEXT_WHEN.items() if v["quote"].startswith(k)), (None, None)))
    P("cat_hung", "dung", v, W(dm, g, "yong"), result={"verdict": "cat"}, rules=[v["rule"]] if v.get("rule") else None,
      conditions=KPACK[v["rule"]]["conditions"] if v.get("rule") else None)
HUNG_WHEN = {"CH10": ("nhuoc", "Tài", None), "CH11": (None, "Tài", "yong"), "CH12": ("nhuoc", "Quan Sát", None), "CH13": (None, "Quan Sát", "yong"),
             "CH14": ("nhuoc", "Quan Sát", None), "CH15": (None, "Quan Sát", "yong"), "CH16": (None, "Ấn", None), "CH17": (None, "Ấn", "yong"),
             "CH18": (None, "Thực Thương", None), "CH19": (None, "Thực Thương", "yong"), "CH20": (None, "Tỉ Kiếp", None), "CH21": (None, "Tỉ Kiếp", "yong")}
for v in H["verdicts"]["tvh_cat_hung"]["hung"]:
    dm, g, role = HUNG_WHEN.get((v.get("rule") or "").removeprefix("BT_TVHK_"), (None, None, "ky"))
    P("cat_hung", "ky", v, W(dm, g, role), result={"verdict": "hung"}, rules=[v["rule"]] if v.get("rule") else None,
      conditions=KPACK[v["rule"]]["conditions"] if v.get("rule") else None)
for v in H["verdicts"]["tvh_p173"]:
    for g in v["groups"]:
        P("phu_quy_p173", "dung" if v["role"] == "dung" else "ky", v, W(v["dm"], GVI[g], "yong" if v["role"] == "dung" else "ky"),
          result={"verdict": v["verdict"]}, rules=[v["rule"]] if v.get("rule") else None)
for o in H["verdicts"]["timing"]:
    P("timing", "dung", o)
for o in H["position"]["quotes"]:
    P("position", "hy", o, W(relation="ke_nhat_chu"), rules=H["position"]["rules"], near_dm=H["position"]["near_dm"])
assert len({p["id"] for p in PRINC}) == len(PRINC)
HYKY_OUT = {"version": VERSION, "_note": HYKY["_note"] + (" Shape agreed with the main session (2026-10-24): principles[] with when "
            "{dm: vuong|nhuoc|null, group: Vietnamese group|null, role: yong|hy|ky|null, relation}; extra keys result / rules / conditions / state / "
            "section. 'role_map' = TTT p.167 element map, computable."),
            "principles": PRINC, "role_map": {k: v for k, v in HYKY["role_map"].items() if k != "source"}}

# ---------------------------------------------------------------- thanh_pha.json: TVH pp.367-369 sentence by sentence (mined/tvh_p367-369.txt)
import re as _re
tb = json.loads((D / "tvh_thanhbai.json").read_text("utf-8"))
CACH_KEY = json.loads((D / "tvh_dungthan.json").read_text("utf-8"))["cach_key"]
SEC = {"1": "quan", "2": "sat", "3": "an", "4": "tai", "5": "thuc", "6": "thuong_quan", "7": "kien_loc"}
IDP = {"quan": "quan", "sat": "sat", "an": "an", "tai": "tai", "thuc": "thuc", "thuong_quan": "thuong", "kien_loc": "loc", "kinh_duong": "loc"}
items: dict[str, list] = {}
cur, on = None, False
for pg in (367, 368, 369):
    for line in (D / "mined" / f"tvh_p{pg}.txt").read_text("utf-8").splitlines():
        if line.startswith("2. Đánh giá"):
            on = True
            continue
        if line.startswith("3. Cách cục đặc biệt"):
            on = False
        if not on:
            continue
        m = _re.match(r"^(\d)\. Cách ", line)
        if m:
            cur = SEC[m.group(1)]
            continue
        m = _re.match(r"^(\d)\) (.*)$", line)
        if m and cur:
            items.setdefault(cur, []).append((int(m.group(1)), m.group(2), pg))
TBR = {r["id"]: r for v in tb["rules"].values() for r in v}


def tvh_item(key, k, text, pg):
    bad = "xấu" in text or "phá hại" in text
    dm = "vuong" if _re.match(r"^(Khi )?[Nn]hật chủ (vượng|mạnh)", text) else "nhuoc" if _re.match(r"^(Khi )?[Nn]hật chủ nhược", text) else None
    eid = f"{IDP[key]}.{k}"
    it = {"id": f"TVH_{key.upper()}_{k}", "when": W(dm), "text": text, "book": "TVH", "page": pg, "quote": text}
    if eid in TBR:
        it |= {"engine_id": eid, "engine_when": TBR[eid]["all"]}
    else:
        it["engine_id"] = None
    return ("pha" if bad else "thanh"), it


TTT_CACH_OUT = {"Chính Quan": {"thanh": [TTT_BY_CACH["Chính Quan"][0], TTT_BY_CACH["Chính Quan"][2]], "cuu": [TTT_BY_CACH["Chính Quan"][1]],
                               "pha": [TTT_BY_CACH["Chính Quan"][3]]}}
WHEN_TTT = {0: W("nhuoc", "Ấn", "yong"), 1: W("nhuoc", "Tài", None, "sinh"), 2: W("vuong", "Tài", "hy"), 3: W(None, "Thực Thương", None, "khac")}
cach_out = []
for name, key in CACH_KEY.items():
    e = {"cach": name, "thanh": [], "pha": [], "cuu": [], "reviewStatus": "verified"}
    for k, text, pg in items.get("kien_loc" if key == "kinh_duong" else key, []):
        side, it = tvh_item("kien_loc" if key == "kinh_duong" else key, k, text, pg)
        e[side].append(it)
    for side, lst in TTT_CACH_OUT.get(name, {}).items():
        for o in lst:
            i = TTT_BY_CACH[name].index(o)
            e[side].append({"id": f"TTT_{key.upper()}_{i + 1}", "when": WHEN_TTT[i], "text": o["vi"], **pub(o)})
    cach_out.append(e)
general = []
for sec, lst in (("pha_cach", THANH_PHA["general"]["pha_cach"]), ("no_clash_kho", THANH_PHA["general"]["no_clash_kho"]),
                 ("thanh", THANH_PHA["general"]["thanh"]), ("troc", THANH_PHA["general"]["troc"]["quotes"]),
                 ("chan_gia", THANH_PHA["general"]["chan_gia"]["quotes"])):
    for i, o in enumerate(lst, 1):
        side = "cuu" if "cứu" in o["vi"].lower() or "khử" in o["vi"] else "pha" if sec in ("pha_cach", "troc") or "lục đục" in o["vi"] else "thanh"
        general.append({"id": f"TTT_{sec.upper()}_{i}", "side": side, "when": W(), "text": o["vi"], **pub(o),
                        **({"rules": THANH_PHA["general"][sec]["rules"]} if isinstance(THANH_PHA["general"][sec], dict) else {})})
THANH_PHA_OUT = {"version": VERSION, "_note": THANH_PHA["_note"] + (" Shape agreed with the main session: cach[] (names as D.cach_tvh.cach, the "
                 "twelve of tvh_dungthan.json cach_key) with thanh / pha / cuu items {id, when, text, book, page | chapter, quote}; TVH items carry "
                 "engine_id (tvh_thanhbai.json) and engine_when (its machine condition) when the engine encodes the sentence, null otherwise "
                 "(the sentences it left out as vague). 'general' = TTT principles for every cách (item.side = thanh / pha / cuu). 'tbct_draft' = "
                 "the 子平真詮 conditions of geju_defs.json, memory-written, never to be voiced."),
                 "cach": cach_out, "general": general, "tbct_draft": {"status": "draft", "why": "no public-domain snapshot of 子平真詮 (DEEP-3)",
                                                                      "defs": json.loads((D / "geju_defs.json").read_text("utf-8"))["defs"]}}

# ---------------------------------------------------------------- schools.json
KIND = {"children_star": "luc_than", "an_vuong_than_vuong": "dung_than", "quan_dung_strength": "dung_than", "ren_table": "bang",
        "tai_many_dm_weak": "dung_than", "kieu_doat_thuc": "cach", "dung_choice": "dung_than"}
topics = []
for pt in SCHOOLS["points"]:
    if pt["id"] == "dieu_hau_ctbg_vs_tvh":
        continue
    sides = []
    for s_ in pt["sides"]:
        src = pub(s_)
        sides.append({"school": src["book"], "statement": s_["vi"], "cite": cite(src), **src, **({"who": s_["who"]} if s_.get("who") else {})})
    topics.append({"id": pt["id"], "topic": pt["topic"], "kind": KIND[pt["id"]], "sides": sides, "engine": pt["engine"]})
_ct = json.loads(CTBG.read_text("utf-8"))
for r in _ct.get("disagreements", []):
    if not r.get("ctbg_quote") or not ({"tap_can_khac_bang_TVH", "can_chu_khac_chu_thich_TVH"} & set(r["kinds"])):
        continue
    src = {"book": "WEB:CTBG", "chapter": r["chapter"], "quote": r["ctbg_quote"]}
    topics.append({"id": f"dieu_hau_{r['stem']}{r['branch']}", "topic": f"điều hậu {r['stem']} sinh tháng {r['branch']}", "kind": "dieu_hau",
                   "kinds": r["kinds"], "sides": [
                       {"school": "TVH", "statement": f"bảng: {r['tvh_table']}; chú thích (thứ tự): {r['tvh_notes']}", "cite": "TVH tr.389-390, 391-396",
                        "quote": None, "book": "TVH", "page": 389, "note": "ô bảng, không có câu để trích; tvh_dieuhau.json"},
                       {"school": "CTBG", "statement": f"用 {r['ctbg']}" + (f" (độ tin {r['confidence']})" if r['confidence'] != "high" else ""),
                        "cite": cite(src), **src}],
                   "engine": "Tập can theo bảng TVH, thứ tự theo chú thích TVH; ô 穷通宝鉴 chỉ để so."})
SCHOOLS_OUT = {"version": VERSION, "_note": SCHOOLS["_note"] + (" Shape agreed with the main session: topics[] {id, topic, kind, sides[{school, "
               "statement, cite, quote, book, page | chapter}], engine}. kind: dieu_hau | dung_than | cach | luc_than | bang. A TVH điều hậu side has "
               "quote null (a table cell, no sentence to quote)."), "summary": {"ctbg_checked_cells": len(_ct.get("checked_cells", [])),
               "ctbg_set_differs_from_tvh": sum("tap_can_khac_bang_TVH" in r["kinds"] for r in _ct.get("disagreements", [])),
               "ctbg_first_differs_from_tvh_notes": sum("can_chu_khac_chu_thich_TVH" in r["kinds"] for r in _ct.get("disagreements", []))},
               "topics": topics}

for name, obj in (("hyky.json", HYKY_OUT), ("thanh_pha.json", THANH_PHA_OUT), ("schools.json", SCHOOLS_OUT)):
    (D / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(name)
