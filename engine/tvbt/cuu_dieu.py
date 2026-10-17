"""Cửu diệu (sao chiếu mạng hằng năm), Tử Vi Khảo Luận pp.271-272.
Rule of the book: add the two digits of the tuổi (virtual age); if the sum has two digits add them again; look the single digit up in the table
for the person's sex. Examples printed in the book: male 26 -> 2+6=8 -> Thái Âm; female 26 -> Thái Bạch; male 54 -> 9 -> Mộc Đức; female 54 -> Thủy Diệu;
56 -> 5+6=11 -> 1+1=2. The glosses paraphrase pp.271-272; the book itself calls the cult around these stars a matter of belief, and its warnings about
illness, death and imprisonment are left out here. This is a folk overlay, not part of the chart calculation."""
from __future__ import annotations

SRC = "Khảo Luận pp.271-272"
# the book's own table is printed star-first: Nam digit -> star, Nữ digit -> star (see test for the printed rows)
NAM = {1: "La Hầu", 2: "Thổ Tú", 3: "Thủy Diệu", 4: "Thái Bạch", 5: "Thái Dương", 6: "Vân Hán", 7: "Kế Đô", 8: "Thái Âm", 9: "Mộc Đức"}
NU_DIGIT = {"La Hầu": 6, "Thổ Tú": 5, "Thủy Diệu": 9, "Thái Bạch": 8, "Thái Dương": 7, "Vân Hán": 2, "Kế Đô": 1, "Thái Âm": 4, "Mộc Đức": 3}
NU = {d: s for s, d in NU_DIGIT.items()}
INFO = {
    "Thái Dương": ("tốt", "phúc tinh: nhiều hanh thông; nữ dễ thành hôn, nam thành công trong làm ăn", "tháng 6 và tháng 10"),
    "Thái Âm": ("tốt", "sao tốt cho cả hai phái: nữ toại nguyện thầm kín, nam có kỳ ngộ, có thể gặp người bạn đời hiền", None),
    "Mộc Đức": ("tốt", "rất tốt cho cả hai phái: phát đạt, thi cử dễ đỗ, đang thất bại thì may mắn trở lại", "tháng 10 và tháng chạp"),
    "Thủy Diệu": ("tốt", "phúc lộc tinh, hợp mạng Mộc và Kim: làm ăn dễ thành công, đi xa gặp may", "kỵ tháng 4 và tháng 8"),
    "Thái Bạch": ("tốt vừa", "Kim đức tinh: có việc vui, thêm người thêm của; không nên làm nhà mới trong năm", "kỵ tháng 5 và màu trắng"),
    "Vân Hán": ("xấu", "hung tinh: nên giữ lời ăn tiếng nói, tránh khẩu thiệt, kiện tụng", "nhất là tháng 2 và tháng 8"),
    "Thổ Tú": ("xấu", "hung tinh, hợp người mạng Thổ: hay buồn man mác, chán công việc làm ăn", "nhất là tháng 4 và tháng 8"),
    "La Hầu": ("xấu", "hung tinh: nhiều thị phi, khẩu thiệt; xấu nhất cho nam", "nhất là tháng giêng và tháng 7"),
    "Kế Đô": ("xấu", "hung tinh: thị phi, khẩu thiệt; xấu nhất cho nữ", "nhất là tháng 3 và tháng 9"),
}


def digit_of(age: int) -> int:
    n = age
    while n > 9:
        n = sum(int(c) for c in str(n))
    return max(n, 1) if n else 9       # age 0 does not occur for tuổi mụ; guard anyway


def star_for(age: int, gender: str) -> dict:
    """gender: 'male' or 'female' (BirthReq convention). age: tuổi mụ in the year examined."""
    d = digit_of(age)
    star = NAM[d] if gender == "male" else NU[d]
    tone, gloss, months = INFO[star]
    return {"age": age, "digit": d, "star": star, "tone": tone, "gloss": gloss, "months": months, "source": SRC,
            "note": "Tín ngưỡng dân gian được sách ghi lại; không phải kết quả của lá số."}
