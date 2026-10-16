"""Generates data/pack_bazi_napam.json from 八字真宗 PDF pp.31-32 (日柱纳音断个性: personality by the nạp âm of the DAY pillar), paraphrased.
The 30 rows are keyed by the Vietnamese nạp âm name computed by the verified nạp âm table (golden-tested against the book's own pillar list)."""
import json
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
ROWS = [  # (first day pillar of the pair, Chinese name, Vietnamese name, paraphrase)
 ("甲子", "海中金", "Hải Trung Kim", "sâu kín, khó đoán, thành phủ trầm"),
 ("丙子", "涧下水", "Giản Hạ Thủy", "ôn nhã, lịch thiệp, lòng thanh tự nhiên"),
 ("戊子", "霹雳火", "Tích Lịch Hỏa", "tính nóng nảy, dễ bùng lên"),
 ("庚子", "壁上土", "Bích Thượng Thổ", "ít hòa nhập đám đông, tính phóng khoáng, tản mạn"),
 ("壬子", "桑柘木", "Tang Đố Mộc", "uy nghiêm bất khuất, cương cường, hiếu thắng"),
 ("甲寅", "大溪水", "Đại Khê Thủy", "bôn ba vất vả nhưng tích cực cầu tiến"),
 ("丙寅", "炉中火", "Lư Trung Hỏa", "nhiệt tình phóng khoáng, tính mãnh liệt"),
 ("戊寅", "城头土", "Thành Đầu Thổ", "cố chấp, cứng nhắc, kém linh hoạt"),
 ("庚寅", "松柏木", "Tùng Bách Mộc", "tâm khí ôn hòa, lương thiện, nhân nghĩa"),
 ("壬寅", "金箔金", "Kim Bạch Kim", "dễ hào nhoáng bề ngoài mà thiếu thực chất"),
 ("甲辰", "佛灯火", "Phú Đăng Hỏa", "thích điều huyền bí, thông minh, lương thiện"),
 ("丙辰", "沙中土", "Sa Trung Thổ", "ít hợp đám đông, hay đơn độc, thiếu người giúp"),
 ("戊辰", "大林木", "Đại Lâm Mộc", "biết kết nối mọi người, nhân nghĩa, hiền thiện"),
 ("庚辰", "白腊金", "Bạch Lạp Kim", "hay tính toán chi li, lòng dạ dễ hẹp"),
 ("壬辰", "长流水", "Trường Lưu Thủy", "thích động, ghét tĩnh, ưa rong chơi"),
 ("甲午", "沙中金", "Sa Trung Kim", "cao quý, thanh nhã, cẩn trọng"),
 ("丙午", "天河水", "Thiên Hà Thủy", "tâm cao khí ngạo, chuyện hôn nhân dễ trắc trở"),
 ("戊午", "天上火", "Thiên Thượng Hỏa", "nhiệt tình hướng thượng, tính nóng vội"),
 ("庚午", "路旁土", "Lộ Bàng Thổ", "lòng dạ hẹp, dễ thiên về lợi ích bản thân"),
 ("壬午", "杨柳木", "Dương Liễu Mộc", "xuôi theo chiều gió, khéo biến thông"),
 ("甲申", "泉中水", "Tuyền Trung Thủy", "tấm lòng rộng rãi, hoài bão lớn"),
 ("丙申", "山下火", "Sơn Hạ Hỏa", "tính nóng, tích cực cầu tiến"),
 ("戊申", "大驿土", "Đại Dịch Thổ", "hoài bão rộng, lòng dạ dày rộng"),
 ("庚申", "石榴木", "Thạch Lựu Mộc", "nhiều mưu tính, mưu nhiều mà thành ít"),
 ("壬申", "剑锋金", "Kiếm Phong Kim", "cương cường, thích đấu, thẳng thừng"),
 ("甲戌", "山头火", "Sơn Đầu Hỏa", "bồng bột, phóng khoáng, nhiệt tình mãnh liệt"),
 ("丙戌", "屋上土", "Ốc Thượng Thổ", "thành thật, giữ chữ tín, thích thể hiện"),
 ("戊戌", "平地木", "Bình Địa Mộc", "cẩn trọng, ít gây thị phi"),
 ("庚戌", "钗钏金", "Thoa Xuyến Kim", "cao quý, thanh nhã, tự trọng và thích đứng riêng"),
 ("壬戌", "大海水", "Đại Hải Thủy", "lòng rộng, khoan dung, nhẫn nại"),
]
rules, claims = [], {}
for pil, zh, vi, txt in ROWS:
    claim = "bt_ngay_nap_am_" + "".join(c for c in vi.lower().replace("đ", "d").replace(" ", "_") if c.isascii() and (c.isalpha() or c == "_"))
    import unicodedata
    slug = unicodedata.normalize("NFD", vi.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_")
    claim = "bt_nap_am_ngay_" + slug.lower()
    rules.append({"id": "BT_ZZ_NAPAM_" + slug, "system": "bat_tu", "schoolId": "bazi_zhenzong_popular", "category": "day_pillar_nap_am",
        "description": f"Day pillar nạp âm {vi} ({zh}): character reading of the manual, paraphrased [八字真宗 PDF pp.31-32 日柱纳音断个性]",
        "conditions": {"fact": "bazi.day_nap_am", "value": vi},
        "consequences": [{"kind": "finding", "claim": claim, "effect": "neutral", "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 2, "sourceIds": ["SRC_BAZI_ZHENZONG"], "reviewStatus": "verified", "version": "0.1.0", "subject": "chart"})
    claims[claim] = f"tính cách thường được mô tả là {txt} (theo nạp âm của trụ Ngày: {vi})"
json.dump({"sources": [], "rules": rules, "pillars": {r[0]: r[2] for r in ROWS}}, open(D / "pack_bazi_napam.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8")); cur.update(claims)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules))
