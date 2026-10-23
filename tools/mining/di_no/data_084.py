PAGES = [{"book": "KL", "page": 83, "image_checked": True,
          "note": "Thái dương/Thái âm essay; one nature line (Khôi Việt = quí nhân, Tả Hữu = bạn bè, Xương Khúc = người tài ba). No palace headings. Text layer in order."},
         {"book": "KL", "page": 84, "image_checked": True,
          "note": "'Thái dương ở các cung': Di (1 bullet), Nô (2 bullets). Phụ line (cha mẹ mất sớm) not in scope. Text layer in order."}]

H = "Thái dương ở các cung"
ENTRIES = [
    {"id": "kl084_di_nhat_nguyet_tam_hoa", "page": 84, "palace": "Thiên Di", "heading": H + " — Di",
     "full_line": "Nhật Nguyệt, Tam hóa: phú quí, quyền uy.",
     "quote": "Nhật Nguyệt, Tam hóa: phú quí, quyền uy",
     "condition_text": "Thiên Di: Nhật Nguyệt (Thái Dương, Thái Âm) with Tam hóa (Hóa Lộc, Hóa Quyền, Hóa Khoa)",
     "condition": {"with_any": ["Thái Dương", "Thái Âm"], "own_stars": ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa"],
                   "other": "'Nhật Nguyệt, Tam hóa' — no position word; under the Thái dương section so Thái Dương (and/or Thái Âm) at Di together with the three Hóa (Lộc Quyền Khoa); book does not say đồng cung vs hội chiếu for the Hóa"},
     "reading_vi": "ra ngoài được phú quý, có quyền uy",
     "polarity": "support", "concepts": ["outside.favorable", "career.status", "fin.abundance"]},
    {"id": "kl084_no_nhat_nguyet_sang", "page": 84, "palace": "Nô Bộc", "heading": H + " — Nô",
     "full_line": "Nhật Nguyệt sáng : người dưới lạm quyền.",
     "quote": "Nhật Nguyệt sáng : người dưới lạm quyền",
     "condition_text": "Nô Bộc: Nhật Nguyệt sáng (bright: miếu/vượng/đắc)",
     "condition": {"with_any": ["Thái Dương", "Thái Âm"], "dignity": {"Thái Dương": ["miếu", "vượng", "đắc"], "Thái Âm": ["miếu", "vượng", "đắc"]},
                   "other": "book word 'sáng' (bright), not a named grade"},
     "reading_vi": "người dưới quyền dễ lạm quyền",
     "polarity": "limit", "concepts": ["NEW:ally.overstep"],
     "notes": "Compare KL p.99 (Thái âm section) 'Nhật Nguyệt sáng: tôi tớ lạm quyền, có phụ tá đắc lực' and KL p.219 'Thái dương, Thái âm đắc địa thì bạn bè được việc'."},
    {"id": "kl084_no_nhat_nguyet_ham", "page": 84, "palace": "Nô Bộc", "heading": H + " — Nô",
     "full_line": "Nhật Nguyệt hãm địa: tôi tớ ra vào luôn không ai được ở được lâu.",
     "quote": "Nhật Nguyệt hãm địa: tôi tớ ra vào luôn không ai được ở được lâu",
     "condition_text": "Nô Bộc: Nhật Nguyệt hãm địa",
     "condition": {"with_any": ["Thái Dương", "Thái Âm"], "dignity": {"Thái Dương": ["hãm"], "Thái Âm": ["hãm"]}},
     "reading_vi": "người giúp việc ra vào luôn, không ai ở được lâu",
     "polarity": "limit", "concepts": ["NEW:ally.fickle"]},
]

NATURES = [
    {"id": "khoi_viet_ta_huu.giup_do", "kind": "star_nature", "star": "Thiên Khôi", "palace": None, "page": 83,
     "quote": "Thiên Khôi, Thiên Việt là quí nhân, Tả Hữu là bạn bè",
     "full_line": "Thiên Khôi, Thiên Việt là quí nhân, Tả Hữu là bạn bè, Đào Hồng Hỉ là nhan sắc, khoan dung và vui vẻ, Xương Khúc là người tài ba, sáng suốt thì sự giúp đỡ phải hữu hiệu.",
     "text": "Khôi Việt là quý nhân, Tả Hữu là bạn bè, Xương Khúc là người tài ba sáng suốt, nên sự giúp đỡ hữu hiệu", "use": ["allies", "travel", "career"], "pol": "+",
     "explains": ["ally.", "outside.favorable", "NEW:travel.helped", "social.support"],
     "notes": "Said in the Thái dương essay (help for a hãm Thái Dương); stars covered: Thiên Khôi, Thiên Việt, Tả Phụ, Hữu Bật, Văn Xương, Văn Khúc. The Đào Hồng Hỉ clause is about appearance and left out of 'text'."},
]
