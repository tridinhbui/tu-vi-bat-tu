PAGES = [{"book": "KL", "page": 96, "image_checked": True,
          "note": "'Thiên phủ ở các cung': only Mệnh, Tài/Điền/Quan, Phối, Vận — no Di/Nô lines. Nothing mined."},
         {"book": "KL", "page": 99, "image_checked": True,
          "note": "'Thái âm ở các cung': Di (1 bullet), Nô (1 bullet). Text layer in order."}]

H = "Thái âm ở các cung"
ENTRIES = [
    {"id": "kl099_di_nhat_nguyet_sang_tam_hoa", "page": 99, "palace": "Thiên Di", "heading": H + " — Di",
     "full_line": "Nhật Nguyệt sáng gặp Tam hóa : được nhiều người quí trọng.",
     "quote": "Nhật Nguyệt sáng gặp Tam hóa : được nhiều người quí trọng",
     "condition_text": "Thiên Di: Nhật Nguyệt sáng gặp Tam hóa (Hóa Lộc, Hóa Quyền, Hóa Khoa)",
     "condition": {"with_any": ["Thái Âm", "Thái Dương"], "dignity": {"Thái Âm": ["miếu", "vượng", "đắc"], "Thái Dương": ["miếu", "vượng", "đắc"]},
                   "tam_phuong": ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa"],
                   "other": "'sáng' (bright) not a named grade; 'gặp' Tam hóa = may be in tam phương; under the Thái âm section"},
     "reading_vi": "ra ngoài được nhiều người quý trọng",
     "polarity": "support", "concepts": ["outside.favorable", "social.support"],
     "notes": "Parallel to KL p.84 (Thái dương section) 'Nhật Nguyệt, Tam hóa: phú quí, quyền uy', which has no brightness condition."},
    {"id": "kl099_no_nhat_nguyet_sang", "page": 99, "palace": "Nô Bộc", "heading": H + " — Nô",
     "full_line": "Nhật Nguyệt sáng : tôi tớ lạm quyền, có phụ tá đắc lực.",
     "quote": "Nhật Nguyệt sáng : tôi tớ lạm quyền, có phụ tá đắc lực",
     "condition_text": "Nô Bộc: Nhật Nguyệt sáng",
     "condition": {"with_any": ["Thái Âm", "Thái Dương"], "dignity": {"Thái Âm": ["miếu", "vượng", "đắc"], "Thái Dương": ["miếu", "vượng", "đắc"]},
                   "other": "'sáng' (bright)"},
     "reading_vi": "người dưới dễ lạm quyền nhưng có phụ tá đắc lực",
     "polarity": "neutral", "concepts": ["NEW:ally.overstep", "NEW:ally.helpful"],
     "notes": "Mixed line. Same condition as KL p.84 kl084_no_nhat_nguyet_sang (người dưới lạm quyền) but adds 'có phụ tá đắc lực'."},
]
