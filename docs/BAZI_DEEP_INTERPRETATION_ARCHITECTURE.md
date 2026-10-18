# Kiến trúc Interpretation Engine của Bát Tự sâu (reading/1)

Mục tiêu: biến kết quả tính toán đã có (khí thế, tương tác, cách cục, dụng thần, đại vận) thành bản luận bảy chương **có chuỗi lập luận, nguồn và mức chắc chắn**, mà không viết lời riêng cho từng lá số và không dùng LLM. Mã nguồn: `engine/tvbt/bazi_deep/reading.py`; dữ liệu: `engine/data/bazi_deep/reading_spec.json`.

## 1. Dòng dữ liệu
```
ngày giờ sinh ──▶ bazi.compute (tứ trụ, tiết khí, đại vận chính xác tới ngày)
                  │
                  ├─▶ pipeline.analyse (TVH_40) ─▶ khí thế, tương tác, cách cục (thành/bại), dụng thần ×8 phương pháp, điều hậu
                  ├─▶ pipeline.timeline ──────────▶ tác động từng đại vận lên nguyên cục (draft)
                  └─▶ rule engine (reasoning.engine) trên 104 luật 八字真宗 với dữ kiện zz  ─▶ findings + chuỗi `why`
                          │
        Providers (mỗi lớp bằng chứng một hàm, mã tổng quát) ─▶ Item {basis, direction, chain, sources, certainty, caveats}
                          │
        reading_spec.json định tuyến Item vào: Nền tảng + 7 chương (Tính cách, Năng lực, Sự nghiệp, Tài lộc, Hôn nhân, Đại vận, Dụng thần)
                          │
        Composer: sắp theo mục và mức nguồn → tóm tắt (chỉ từ tiêu đề các ý được chọn) → ghép cặp ý ngược chiều → thêm giới hạn
                          │
        JSON `bazi_deep_reading` (cờ mặc định TẮT) ─▶ trang nháp /bazi-deep-draft (chế độ Dễ hiểu / Chuyên sâu)
```
Không có bước nào gọi mạng, đọc ngẫu nhiên hay sinh văn bản tự do. Chạy hai lần cho kết quả giống từng byte (test).

## 2. Hạt nhân: `Item`
Mỗi câu trong bản luận là một `Item` có:
| Trường | Ý nghĩa |
|---|---|
| `basis` | **tinh_toan** dữ kiện tính toán · **co_nguon** diễn giải có nguồn (luật đã đối chiếu trang) · **truong_phai** giả thuyết của một trường phái hoặc bản nháp · **chua_du_can_cu** chưa đủ căn cứ |
| `kind` | `sach` (một luật có trích dẫn), `phuong_phap` (một phương pháp dụng thần), `cau_truc` (vai trò cấu trúc), `tinh_toan`, `gioi_han` |
| `chain` | luôn đủ bốn bước **Dữ kiện → Quy tắc → Điều kiện → Kết luận**, bước nào cũng có chữ |
| `sources` | sách và trang; bắt buộc nếu `basis = co_nguon` (test) |
| `direction` | thuận / bất lợi / trung tính / cấu trúc (phân loại do hệ thống đọc từ lời sách, không phải lời sách) |
| `easy`, `expert` | hai văn bản cho hai chế độ đọc, cùng một chuỗi lập luận |
| `caveats`, `counter` | điều cần lưu ý; các ý đi ngược chiều trong cùng mục |
| `pillar_refs`, `table` | trụ/chữ liên quan để làm nổi bật; bảng (đại vận) |

`Item.out()` chạy bộ làm sạch `vi()` trên mọi chữ: mã nội bộ (`he_thong`, `SRC_…`, tên trạng thái) đổi sang tiếng Việt; test quét hàng trăm lá số để chắc không mã nào lọt ra.

## 3. Providers (lớp bằng chứng → nguồn → mức)
| Provider | Lấy từ | Mức nguồn | Vào đâu |
|---|---|---|---|
| nguyệt lệnh, khí mùa | tra bảng vượng–tướng–hưu–tù–tử; tư lệnh | dữ kiện tính toán (nguyên tắc: Trích Thiên Tủy) | Nền tảng |
| khí thế | quy tắc 40% của Thiệu Vĩ Hoa tr.355 và cách tính riêng của hệ thống, **đặt cạnh nhau** | có nguồn / giả thuyết trường phái | Nền tảng |
| hàn–nóng, điều hậu | bảng TVH tr.389–396; hàn–noãn TTT tr.113–114 | có nguồn / giả thuyết | Nền tảng |
| cách cục | cách thành/bại (bảng nháp), đánh giá tốt xấu của TVH tr.367–369, ngoại cách chân/giả | giả thuyết / có nguồn | Nền tảng |
| tương tác | hợp, xung, hình, hại, phá, hợp hóa và trạng thái đã giải | dữ kiện tính toán (hệ số: hệ thống) | Nền tảng |
| thập thần có tên | `patterns` | giả thuyết (draft) | Nền tảng |
| luật 八字真宗 | `engine.run` trên pack `pack_bazi_zhenzong`, `…napam`, `…zz_direct`, định tuyến theo `zz_routing` | có nguồn (đã đối chiếu) hoặc giả thuyết (draft) | Tính cách, Năng lực, Sự nghiệp, Tài lộc, Hôn nhân |
| vai trò nhóm trong các phương pháp | bảng vai trò của từng phương pháp dụng thần | có nguồn một phần (cấu trúc) | Năng lực, Sự nghiệp, Tài lộc |
| đại vận | lịch khởi vận; vận hỷ/kỵ TVH tr.382–386; tác động lên nguyên cục | tính toán / có nguồn / giả thuyết | Đại vận |
| dụng thần | tám phương pháp tách biệt + bất đồng + đồng thuận | theo `meta.levels` của từng phương pháp | Dụng thần |

## 4. Quy tắc của Composer
1. **Không gộp trường phái.** Hai cách đọc vượng/nhược (TVH 40% và hệ thống) là hai `Item` riêng, đặt cạnh nhau; sát ngưỡng 40% thì nói hai cách đọc.
2. **Tóm tắt chỉ từ ý đã chọn.** `Kết luận chính` ghép tiêu đề của tối đa ba ý `sach/phuong_phap` có nguồn (ưu tiên có nguồn đã đối chiếu), kèm số đếm theo mức nguồn. Chương không có ý nào như vậy **nói rõ là không có quy tắc nào khớp** (cờ `empty`), không lấp bằng lời chung.
3. **Ý ngược chiều không cộng trừ.** Trong cùng một mục, ý thuận và ý bất lợi có nguồn được ghép cặp: mỗi bên ghi `counter` trỏ tới bên kia, chương ghi `opposing` với câu "không cộng trừ cho nhau".
4. **Giới hạn luôn hiện.** Mỗi chương mang danh sách `gaps` (mức `chua_du_can_cu`): điều các sách đã nhập chưa có quy tắc, dưới dạng chữ cho cả hai chế độ.
5. **Đại vận hỷ/kỵ có điều kiện.** Có bảng thì dùng; sát ngưỡng thì hai bảng; cách chưa xác định thì ghi `chua_du_can_cu`, không bịa.
6. **Chương Dụng thần không chọn đáp án cuối.** Mỗi phương pháp một ý; bất đồng và đồng thuận được liệt kê; câu về việc sách không nói cách chọn luôn nằm trong `gaps`.

## 5. Chuỗi "Vì sao lá số này được luận như vậy?"
Mỗi chương có `why`: tối đa ba ý nổi bật, mỗi ý ba dòng Dữ kiện → Quy tắc → Kết luận, trích đúng từ chuỗi của chính ý đó; trong chế độ Dễ hiểu mỗi ý còn có mục "Vì sao?" mở ra bốn bước; trong chế độ Chuyên sâu bốn bước mở sẵn, kèm nguồn, mức chắc chắn và lưu ý.

## 6. Cách cờ và cách ly
- API: `bazi_deep_reading` trên `POST /api/bazi-structure`, **mặc định tắt**; bật thì thêm đúng một khóa, không đổi byte nào của phản hồi cũ (test so từng phản hồi). `bazi_deep_draft` là cờ riêng cho phong bì trình bày; hai cờ độc lập.
- Reading không sửa kết quả của phương pháp nào (test so JSON `yongshen` trước/sau).
- Cách ly hai trường phái của Phase 5–6 được giữ nguyên: phía hệ thống và phía Thiệu Vĩ Hoa vẫn tách; reading chỉ đọc kết quả.

## 7. Thêm một quy tắc có nguồn
1. Đọc trang sách, ghi vào pack luật (điều kiện + hệ quả + `sourceIds` + trang + `reviewStatus`) và thêm câu tiếng Việt vào `claims_vi.json`.
2. Nếu cần dữ kiện mới, thêm vào `facts.bazi_facts` và nhãn vào `reading_spec.json → fact_vi`.
3. Định tuyến luật vào chương/mục trong `zz_routing` (và `zz_direction` nếu muốn phân loại thuận/bất lợi). Test `test_every_zz_rule_is_routed…` sẽ bắt luật chưa định tuyến.
4. Chạy `tools/bazi_deep_reading_coverage.py` để cập nhật ma trận bao phủ và chỉ số phân biệt.
5. Luật mới là `draft` cho đến khi có người đối chiếu trang; mức `co_nguon` chỉ dành cho luật đã `verified`.

## 8. Những gì cố ý KHÔNG làm
Không tự đặt ngưỡng vượng/nhược hay chọn dụng thần khi thiếu căn cứ; không gán tính cách/sự nghiệp từ khí thế hay cách cục khi sách không nói; không viết "sao vợ/chồng" khi chưa có điều sách được đối chiếu; không dùng sách 'Đổi Vận' làm nguồn quy tắc; không dự đoán sự kiện.
