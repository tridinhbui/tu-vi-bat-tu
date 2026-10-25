# Diễn giải hiện đại cho 64 quẻ: cách viết

Tệp `engine/data/kinh_dich/dien_giai/<số quẻ>.json` là lớp **diễn giải của hệ thống**, bản nháp, nằm tách khỏi kinh văn và lời bàn cổ.
Bộ đọc (`engine/tvbt/kinh_dich/reading.py`) ghép các câu ở đây với lời kinh (bản dịch Ngô Tất Tố) và lời bàn của Trình Di, Chu Hy. Mẫu chuẩn:
`dien_giai/7.json` (quẻ Sư).

## Nguyên tắc

1. **Mọi câu đều có chỗ dựa.** Mỗi mục có `text` (câu của hệ thống) và `from`: một đến ba trích dẫn **nguyên văn, đúng từng chữ** của một lớp
   trong sách Ngô Tất Tố. Lớp là `nghia` (dịch nghĩa), `trinh_di`, `chu_hy` hoặc `tien_nho`. Đoạn nằm trong khóa `seg` (`thoan`, `hao1`…`hao6`,
   `dung`, `thoan_truyen`, `dai_tuong`, `tieu_tuong1`…`tieu_tuong6`, `tieu_tuong_dung`, `van_ngon`). `lint()` (`engine/tvbt/kinh_dich/dien_giai.py`)
   từ chối trích dẫn không có trên đoạn đó.
2. **Không thêm ý mà lời kinh và lời bàn không có.** Diễn giải là đem ý của lời bàn sang hoàn cảnh hôm nay (công việc, tiền bạc, gia đình…),
   không phải sáng tác thêm điềm lành dữ. Nếu lời bàn không nói gì về một chủ đề, câu chủ đề phải suy từ ý cốt lõi đã trích, và nói ở mức đó.
3. **Riêng cho quẻ này.** Một câu đọc được cho mọi quẻ ("cần kiên nhẫn và bình tĩnh") là câu hỏng. Câu tốt nhắc đến hình ảnh, tình thế hay
   mối quan hệ riêng của quẻ (Sư: một người cầm quân, kỷ luật, giao trọn quyền, lui giữ sức, thưởng đúng người).
4. **Không phán chắc.** Không dùng: chắc chắn, nhất định, suốt đời, trọn đời, không bao giờ, luôn luôn, tuyệt đối, định mệnh. Viết theo lối
   "lúc này nên…", "dễ…", "thuận khi…". Không nói về sách, trang, quy tắc, hệ thống, căn cứ trong câu (những thứ đó nằm trong `from`).
5. **`traditional` là trích dẫn, không phải lời của hệ thống**: câu của Chu Hy hoặc Trình Di nói thẳng với người xem bói (thường có "răn kẻ xem",
   "lời Chiêm", "kẻ xem…"). Nếu đoạn không có câu như thế, dùng dịch nghĩa (`layer: "nghia"`). Trích đủ để câu đứng được một mình, không quá 60 chữ.
6. **Tiếng Việt tự nhiên**, câu 15–35 chữ, không lặp mở đầu câu, không dịch máy từng chữ. Dùng tên hào như sách: "hào Chín Hai", "hào Sáu Năm".

7. **Không mở câu chủ đề bằng tên lĩnh vực.** Với 64 quẻ, các mở đầu "Trong công việc,", "Về tiền bạc,", "Với việc làm ăn,", "Trong học tập,",
   "Trong tình cảm,", "Trong gia đình,", "Trước một lựa chọn," sẽ lặp khắp nơi (kiểm tra `tools/kinh_dich_eval.py` chặn một mở đầu dùng ở hơn
   6 quẻ). Mở câu bằng hình ảnh, tình thế hay người trong quẻ ("Như mây chưa thành mưa, khoản đầu tư…", "Người đứng giữa hai bên…").
8. **Trích dẫn đứng được một mình.** Không bắt đầu trích bằng "cho nên…", "vì thế…", không cắt giữa mệnh đề làm đổi nghĩa.
9. **Lời bàn mang khung cũ** (vợ chồng, vua tôi, quân tử tiểu nhân, đàn ông đàn bà): giữ nguyên trong trích dẫn, còn câu diễn giải nói ý cốt lõi
   bằng lời trung tính hôm nay; không biến khung giới hay đẳng cấp thành lời khuyên.
10. Bản dịch là **bản in** Ngô Tất Tố (chép từ ảnh quét, `engine/data/kinh_dich/ntt/`): trích đúng chữ in, kể cả khi khác bản Wikisource.
    Đoạn `intro` là lời mở quẻ của Trình Di (vì sao quẻ này đến sau quẻ trước); lời bàn tiên nho và các nhà chú khác nằm trong lớp `tien_nho`.

## Cấu trúc

```json
{
 "number": 7, "status": "draft", "author": "Thiên Bàn (bản nháp, chưa duyệt)",
 "que": {
  "core":      {"text": "…tình thế cốt lõi của quẻ, 1–2 câu…", "from": [{"seg": "thoan", "layer": "chu_hy", "quote": "…"}]},
  "image":     {"text": "…đọc hình ảnh hai quái / Đại tượng…", "from": [...]},
  "structure": {"text": "…cấu trúc hào đáng chú ý (hào chủ, một dương giữa năm âm…), chỉ khi lời bàn nói tới…", "from": [...]},
  "traditional": {"seg": "thoan", "layer": "chu_hy", "quote": "…"},
  "topics": {"su_nghiep": {...}, "tai_chinh": {...}, "kinh_doanh": {...}, "hoc_tap": {...}, "tinh_cam": {...}, "gia_dinh": {...}, "lua_chon": {...}},
  "advice":    {"text": "…lời khuyên thực tế, cụ thể…", "from": [...]},
  "conditions": [{"text": "…điều kiện làm kết quả khác đi (lời bàn: 'nếu…thì…')…", "from": [...]}]
 },
 "hao": {
  "1": {"gist": {...}, "traditional": {...}, "position": {...}, "topics": {"tinh_cam": {...}}},
  "…": "…",
  "6": {...}
 },
 "dung": {"gist": {...}, "traditional": {...}}
}
```

- `que.topics`: đủ 7 chủ đề, mỗi chủ đề 1–2 câu.
- `hao.<k>.gist`: bắt buộc cho cả 6 hào. `traditional`: bắt buộc.
- `position`: chỉ khi lời bàn của hào nói tới ngôi, giữa, chính, ứng.
- `topics` của hào: chỉ những chủ đề mà lời hào thật sự nói tới (ví dụ hào nói chuyện cưới hỏi thì có `tinh_cam`). Không bắt buộc.
- `dung`: chỉ cho quẻ Kiền (1) và Khôn (2).

## Kiểm tra

```bash
cd engine && TVBT_KD_NTT_DIR=<thư mục bản dịch> ../.venv/bin/python -c "from tvbt.kinh_dich.dien_giai import lint; print(lint(7))"
```

Kết quả phải là `[]`.
