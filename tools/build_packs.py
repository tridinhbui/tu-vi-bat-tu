"""Generates data/pack_thuc_hanh.json, data/pack_bazi_zhenzong.json and extends data/claims_vi.json.
Every rule is a paraphrase (not a quotation) of a statement the cited page makes; page cites are in each description."""
import json
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
GOOD = ["miếu", "vượng", "đắc"]

# (star, claim, effect, dignities, locator, Vietnamese phrasing)
TV = [
 ("Thiên Cơ", "co_tot_thong_minh_muu_tri", GOOD, "TH p.31", "thông minh, nhiều mưu trí, tính nhân hậu từ thiện, đời sống khá giả"),
 ("Thiên Cơ", "co_ham_kem_nhanh_van_du_an", ["hãm"], "TH p.31", "kém nhanh nhạy hơn nhưng vẫn có tài, đủ ăn đủ mặc và sống lâu"),
 ("Thái Dương", "duong_tot_thong_minh_nhan_hau", GOOD, "TH p.33", "thông minh, cương nghị, nhân hậu (nam mệnh; sinh ban ngày thì thuận hơn)"),
 ("Thái Dương", "duong_ham_ngang_gan_vat_va", ["hãm"], "TH p.33", "tính ương gàn, kém bền chí, đầu đời vất vả, về sau mới khá"),
 ("Vũ Khúc", "vu_tot_chi_lon_kinh_doanh", GOOD, "TH p.34", "thông minh, chí lớn, có óc kinh doanh, thường thành đạt muộn sau khoảng 30 tuổi"),
 ("Vũ Khúc", "vu_ham_lao_dao_tai_danh", ["hãm"], "TH p.34", "lao đao về tiền bạc và danh vọng, đời nhiều vất vả"),
 ("Thiên Đồng", "dong_tot_nhan_hau_hay_doi", GOOD, "TH p.35", "nhân hậu, hay thay đổi công việc và nơi ở, thường được hưởng sung túc và thọ"),
 ("Thiên Đồng", "dong_ham_nong_can_kham_kho", ["hãm"], "TH p.36", "suy nghĩ nông cạn, thích ăn chơi, lo toan nhiều về sinh kế"),
 ("Liêm Trinh", "liem_tot_thang_than_nghiem_nghi", GOOD, "TH p.37", "thẳng thắn, nghiêm nghị, tính nóng, đời khá giả và thọ"),
 ("Liêm Trinh", "liem_ham_khac_nghiet_lo_toan", ["hãm"], "TH p.37", "khắc nghiệt, nhiều toan tính, có óc kinh doanh và khéo kỹ nghệ nhưng cả đời lo toan vất vả"),
 ("Thái Âm", "am_tot_hien_hoa_van_chuong", GOOD, "TH p.40", "hiền hòa nhã nhặn, từ tâm, thích văn chương mỹ thuật, thường được giàu sang và sống lâu"),
 ("Thái Âm", "am_ham_uong_nganh_ngam_vinh", ["hãm"], "TH p.40", "tính ương ngạnh, thích ngâm vịnh, ít tham danh lợi, việc đời thường không vừa ý"),
 ("Tham Lang", "tham_tot_hieu_thang_hoat_dong", GOOD, "TH p.42", "tính trung hậu nhưng tự đắc, hiếu thắng, thích hoạt động, tham vọng lớn, có óc kinh doanh; thành đạt sau 30 tuổi"),
 ("Tham Lang", "tham_ham_yem_the_tu_hanh", ["hãm"], "TH p.42", "dễ yếm thế, làm gì cũng gặp trắc trở, thiên về đời sống tu hành mới yên"),
 ("Cự Môn", "cu_tot_thong_minh_ngon_ngu", GOOD, "TH p.43", "thông minh, nhiều mưu trí, xét đoán giỏi, lời lẽ sắc sảo, thường khá giả"),
 ("Cự Môn", "cu_ham_gian_xao_da_nghi", ["hãm"], "TH p.43", "kém sáng suốt, khắc nghiệt, đa nghi, hay nói khoác, ít thuận lợi giao thiệp"),
 ("Thiên Tướng", "tuong_tot_uy_nghi_don_hau", GOOD, "TH p.44", "uy nghi, đôn hậu, thông minh, thích ăn ngon mặc đẹp, thường hưởng vinh hoa phúc thọ"),
 ("Thiên Lương", "luong_tot_khoan_hoa_tho", GOOD, "TH p.46", "thanh tú, khoan hòa, hưởng thọ; có văn tinh hội thì phú quý và có uy quyền"),
 ("Thiên Lương", "luong_ham_phong_dang_phieu_luu", ["hãm"], "TH p.46", "kém thông minh, thích phóng đãng phiêu lưu, hay đổi chí hướng, bôn ba vất vả"),
 ("Thất Sát", "sat_tot_dung_manh_muu_co", GOOD, "TH p.47", "dũng mãnh, có mưu cơ, được nhiều người tin phục, giàu sang nhưng đời thường thăng trầm"),
 ("Thất Sát", "sat_ham_hung_bao_khoac_lac", ["hãm"], "TH p.47", "tính hung hãn, hay khoa trương, đời nhiều va vấp"),
 ("Phá Quân", "pha_tot_cuong_nghi_tu_dac", GOOD, "TH p.48", "thông minh, cương nghị, can đảm, thích hoạt động; đời thăng trầm, tiền bạc tụ tán bất thường"),
]
rules, claims = [], {}
for star, claim, lv, loc, vi in TV:
    cond = {"all": [{"fact": "palace.name", "value": "Mệnh"},
                    {"fact": "palace.own_major_stars", "operator": "contains", "value": star},
                    {"fact": f"palace.dignity.{star}", "operator": "in", "value": lv}]}
    rules.append({"id": "TV_TH_" + claim.upper(), "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "star_dignity",
        "description": f"Mệnh seated by {star} in {'/'.join(lv)} position (dignity from SRC_THUC_HANH pp.29-48): the book's temperament reading, paraphrased [{loc}]",
        "conditions": cond, "consequences": [{"kind": "finding", "claim": claim, "effect": "support", "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_THUC_HANH"], "reviewStatus": "verified",
        "version": "0.1.0", "subject": "palace"})
    claims[claim] = f"khuynh hướng {vi} (theo {star} ở vị trí {'/'.join(lv)} tại cung Mệnh)"
json.dump({"sources": [], "rules": rules}, open(D / "pack_thuc_hanh.json", "w"), ensure_ascii=False, indent=1)

# ---- Bát Tự: 八字真宗 PDF p.25 (日干临十神) and p.26 (日干五行直断), p.26-27 (缺)
STEMS = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
P25 = ["tiêu xài mạnh tay, kiếm được cũng tiêu được, không so đo hơn thiệt cá nhân, tự chủ và ít dựa dẫm",
       "tiêu nhiều nhưng có tính toán, để ý hơn thiệt và lợi ích, một lòng nghĩ đến tiền của",
       "tính nóng vội, thẳng thắn, dễ vướng thị phi, tâm cao khí ngạo, hành xử phóng túng",
       "cẩn trọng chu đáo, tích cực tiến thủ, chín chắn thành thật, tuân phép công, có trách nhiệm",
       "khôn vặt, lòng dạ hẹp, nhiều tính toán trong lòng, đa nghi, dễ hành động theo tình cảm",
       "nhân từ rộng lượng, lao tâm nhiều, hay lo nghĩ nhưng đối đãi người khoan dung",
       "nhiều bạn bè, ý chí kiên cường, thẳng thắn tự trọng, đoàn kết, hào sảng",
       "cứng nhắc cố chấp, hay bênh bất bình, dễ vướng thị phi, tiêu xài lớn, đời nhiều lo toan",
       "khí chất cao nhã, tư duy thoát tục, phản ứng nhanh, đa tài đa nghệ",
       "không chịu ràng buộc, kiêu ngạo, thích mơ mộng và thể hiện mình, hành xử kín đáo khó đoán, dễ gặp trắc trở"]
P26 = ["có năng lực tổ chức, cương cường tự nghiêm khắc, có tài lãnh đạo, được nhiều người tin cậy",
       "bề ngoài mềm yếu cẩn trọng nhưng trong lòng cố chấp, giữ nếp cũ, tình cảm dễ tổn thương",
       "lịch thiệp, đôn hậu, nhiệt tình và hoạt bát cởi mở nhưng thiếu kiên tâm, dễ bị hiểu lầm là thích phô trương",
       "ngoài mềm trong tiến, tư duy kín đáo, lễ độ, ngại trắc trở, thắng được mà khó bại",
       "thành thật dày dặn, giỏi giao tiếp, thích chưng diện, thiếu chủ kiến, quan hệ không bền, hiếu thắng",
       "tâm tế, có quy củ, độ lượng nhỏ, hay đa nghi và ghen ghét, hiếu thắng",
       "trọng tiền của, hơi có văn tài, giỏi kinh tế và xử lý công việc, coi trọng hưởng thụ vật chất",
       "thiếu sức hấp dẫn, ngoan cố, nhưng thông minh và gỡ được nhiều khó khăn",
       "biết đoàn kết và thuyết phục người, tính nóng, độ lượng lớn, dựa vào sức tự nhiên, cá tính hay thay đổi và đôi khi thờ ơ",
       "chính trực liêm khiết, cần mẫn, gặp nghịch cảnh vẫn mở được đường, có sức sống và chịu khổ giỏi"]
MISS = {"Mộc": "dè sẻn, hẹp hòi, kém thấu tình đạt lý", "Hỏa": "yếu mềm cả trong lẫn ngoài, diễn đạt kém rõ ràng, thiên về tiêu cực",
        "Thổ": "thiếu tình nghĩa", "Kim": "thiếu lễ nghĩa", "Thủy": "trí lực không cao, hay thất thường đổi ý"}
br = []
for i, st in enumerate(STEMS):
    for src_tbl, tag, vis, loc in [(P25, "P25", "ri_gan_lam_thap_than", "PDF p.25 日干临十神直断"), (P26, "P26", "ri_gan_ngu_hanh", "PDF p.26 日干五行直断")]:
        claim = f"bt_{vis}_{st.lower()}"
        br.append({"id": f"BT_ZZ_{tag}_{st.upper()}", "system": "bat_tu", "schoolId": "bazi_zhenzong_popular", "category": "day_master_character",
            "description": f"Day master {st}: character reading of the 八字真宗 manual, paraphrased [{loc}]",
            "conditions": {"fact": "bazi.day_master_stem", "value": st},
            "consequences": [{"kind": "finding", "claim": claim, "effect": "neutral", "scope": "natal"}],
            "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_BAZI_ZHENZONG"], "reviewStatus": "verified",
            "version": "0.1.0", "subject": "chart"})
        claims[claim] = "tính cách thường được mô tả là " + src_tbl[i] + (" (bảng 日干临十神)" if tag == "P25" else " (bảng 日干五行)")
for el, vi in MISS.items():
    claim = f"bt_thieu_hanh_{el.lower()}"
    br.append({"id": f"BT_ZZ_MISSING_{el.upper()}", "system": "bat_tu", "schoolId": "bazi_zhenzong_popular", "category": "element_balance",
        "description": f"Element {el} absent from the eight visible characters (4 stems + 4 branches; hidden stems NOT counted — our operationalisation of the manual's 缺) [PDF pp.26-27]",
        "conditions": {"fact": "bazi.missing_elements", "operator": "contains", "value": el},
        "consequences": [{"kind": "finding", "claim": claim, "effect": "neutral", "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 2, "sourceIds": ["SRC_BAZI_ZHENZONG"], "reviewStatus": "draft",
        "version": "0.1.0", "subject": "chart"})
    claims[claim] = f"xu hướng được sách nêu là {vi}, khi lá số vắng hành {el}"
json.dump({"sources": [], "rules": br}, open(D / "pack_bazi_zhenzong.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
cur.update(claims)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules), len(br), len(cur))
