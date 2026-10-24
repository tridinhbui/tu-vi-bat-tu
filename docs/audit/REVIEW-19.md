# Đánh giá 19 điểm của bản live (2026-10-23): đã sửa gì, còn gì

Kế hoạch: `~/.claude/plans/pasted-content-id-de4b-p0-soft-shore.md`. "Trước" = origin/main `ef62dc5` (bản live chủ dự án đọc); "sau" = nhánh
này. Ví dụ đầy đủ ba lá (2002, 1971, 1911), mọi chương Tử Vi, trước/sau: `docs/examples/review-19-truoc-sau.md`.

Quyết định của chủ dự án trong đợt này (2026-10-23):

1. **Câu tổng hợp có nhãn** được phép: hệ thống ghép nhân quả / mâu thuẫn / bên nào nặng hơn **chỉ từ các luận điểm sách đã nói trong lá số**
   (basis `he_thong`, trang hiển thị "Lời tổng hợp của hệ thống"), không thêm ý mới, không câu phổ thông, không LLM.
2. **Phu Thê**: được nói diễn biến theo đại hạn (chặng thuận / khó), vẫn không phán sự kiện (năm cưới, ly hôn, tái hôn).
3. **Tật Ách**: một câu cân yếu tố cứu giải với yếu tố gây sức ép, không chẩn đoán, không kết luận sức khỏe.

## 1. Bảng 19 điểm

| # | Điểm | Đã làm | Ở đâu | Còn lại |
|---|---|---|---|---|
| 1 | Mệnh thiếu tâm lý, mạnh/yếu, mâu thuẫn nội tâm | Đoạn **Chân dung tổng hợp**: gom mọi nét tính cách đã nói (phần chính + Đọc sâu) thành mạnh / yếu, **mâu thuẫn nội tâm** = một nét + và một nét − cùng mặt (ưu tiên cùng facet), nói rõ mỗi nét từ sao nào; **gốc chung** khi ≥3 nét cùng một sao Mệnh | `prose/luan.ts portrait()`, `luan.json portrait` | Tâm lý sâu hơn cần thêm luật sách về tính cách (KL/TH) — tri thức, không phải khung câu |
| 2 | Quan Lộc nông | Đoạn **Diễn biến theo đại hạn**: các hạn chạm cung Quan Lộc (hạn vào cung, Hóa Lộc/Kỵ của hạn rơi vào), mức của từng hạn, chặng thuận nhất / cần giữ nhất; kết luận công danh được cân (điểm 14) | `prose/course.ts` | Năng lực / thăng tiến cụ thể vẫn chỉ đến từ luật đã có |
| 3 | Tài Bạch thiếu chiều sâu | Diễn biến tiền bạc theo đại hạn; Tổng luận xếp ba phần tiền (kiếm / giữ / tích lũy) vào thứ bậc chung | `course.ts`, `tong_luan.ts` | |
| 4 | Phu Thê thiếu tâm lý, xung đột, diễn biến | Hai mặt hôn nhân được **cân** (vd. 2002: Thái Âm vượng, chính tinh, nặng hơn Đà La) và nói lý do; **diễn biến hôn nhân theo đại hạn** (chặng, không sự kiện) | `ledger.ts weighSides`, `course.ts` | |
| 5 | Đại hạn máy móc, không liên kết | Mỗi hạn: **so với hạn trước** (lên / xuống / ngang; chênh ≥2 mức = **bước ngoặt**), **trọng tâm** của hạn (cung hạn + cung nhận Hóa Lộc, Hóa Kỵ); câu "nơi xem hôn nhân, vốn …" chỉ nói đủ một lần, lần sau gọi lại ngắn; nghĩa Quyền/Khoa nói một lần; câu KL tr.233 lặp lại được nói bằng sao của hạn đó | `prose/vanhan.ts`, `van_han.json` (`trend`, `focus`, `natal_link.again`, `kl_again`, `hoa_qk_again`) | So sao hạn với Thân (KL tr.234) vẫn chưa làm (DEEP-TUVI-2 §8) |
| 6 | Bát Tự nặng tính toán, thiếu tổ hợp Thập thần | **Phiên riêng** (đề xuất "Bát Tự: Thập thần combos + less computation") | `bazi*` | Chưa bắt đầu khi viết tài liệu này |
| 7–9 | Phúc Đức, Thiên Di, Nô Bộc sơ sài | Nhắc lại kết luận lĩnh vực tối đa 2 lần/báo cáo (bớt câu rỗng); Nô Bộc bỏ câu minh họa chung | `luan.ts echoOk`, `narrative.ts` | Cần thêm tri thức (pack_cung_bay đã có 122 luật; mục `skipped` chờ chủ quyết) |
| 10 | Điền Trạch thiếu quá trình tạo dựng | Diễn biến nhà cửa, tài sản theo đại hạn | `course.ts` | |
| 11 | Tật Ách thiếu tổng hợp đối lập | Câu **cân cứu giải / sức ép**: sao cứu giải theo KL (tr.109, 120, 122, 140, 186: `star_nature.json` explains `health.shielded`) đối với sát tinh, Hóa Kỵ, chính tinh hãm trong cung; bên nào đông hơn; câu kèm "không phải lời đoán về bệnh" | `luan.ts` (Tật Ách), `luan.json health_balance` | |
| 12 | Phụ Mẫu / Huynh Đệ / Tử Tức chung chung | Bỏ câu minh họa (`behave`) ở bốn cung người khác (Nô Bộc, Tử Tức, Huynh Đệ, Phụ Mẫu): câu kiểu "Người thân là nơi đương số tìm về khi cần" đọc như nhau ở mọi lá | `narrative.ts` | Tri thức thật còn mỏng (Huynh Đệ, Tử Tức) |
| 13 | Cách cục thiếu thành/phá, mức độ | **Chương Cách cục Tử Vi** mới, hai nguồn. (a) **9 cách đã kiểm trang** (`engine/data/formations_verified.json`, nguồn và điều kiện bỏ ở `docs/audit/CACH-CUC-SOURCES.md`): đánh giá trên lá số (`reason/structures.ts evaluateFormations`), nói **thành / thành có thế mạnh** (điều tăng thế nào) / **chỉ có hình thức** (thiếu gì) / **bị phá** (vì sao), phản chứng, mỗi câu kèm trang của điều kiện đó; cách mà sách gọi là quý cách ngay ở phần lõi (`core_alone: thanh`) không bị hạ xuống 'hình thức'; Mã đầu đới kiếm (`disputed`) không nói. (b) Các cách TH/KL do luật verified đặt tên: tốt/xấu, trọn hay bị phá bởi yếu tố trong cung. Mức ảnh hưởng (quy ước có nhãn) và cách nặng nhất. Trên 300 lá: 194 lá có ít nhất một cách đã kiểm trang | `prose/cach_cuc.ts`, `cach_cuc.json`, `build.ts formationsVerified` | Python (`formation_eval.py`) chưa dùng file này; Thân chưa xét (TH p.76 nói 'Mệnh Thân') |
| 14 | Kết luận tốt/xấu mâu thuẫn, chưa phân xử | **Thang cân có nhãn** (`domains.json weigh`): khi hai mặt đối đầu mà không câu sách nào phân xử, cân theo bậc chỗ đứng (chính tinh > phụ tinh), vai trò cung (cung chính > tam phương), độ sáng (sao sáng làm mặt thuận nặng thêm, sao hãm không có Hóa tốt làm mặt khó nặng thêm), Tuần/Triệt trên cung của mặt thuận, số chỗ đứng độc lập. Chênh ≥ 0,2 → verdict mới `nghieng_ve` (+/−), hai mặt vẫn được nêu, kèm **lý do** (≤2); chênh nhỏ giữ `chua_phan_xu` | `reason/ledger.ts`, `luan.json weighed/weigh_line/weigh_why` | |
| 15 | Lặp ý, lặp sao, lặp câu | Đo mới **trong một báo cáo** (`tools/interpret/eval_repeat.ts`); kết luận lĩnh vực nhắc lại ≤2 lần; các khung lặp nhiều nhất ở Đại hạn có biến thể / bản rút gọn | xem §2 | |
| 16 | Thiếu tổ hợp nhiều sao, nhân quả | Câu cân nói **vì sao** bên này nặng hơn (sao nào, sáng/hãm, ở đâu); chân dung nói nét nào từ sao nào, nét nào chung gốc | | Tổ hợp sao có sách (Sát Phá Tham …) chưa có luật có trang |
| 17 | Văn máy móc, ít cá nhân hóa | Các câu tổng hợp đều gọi tên sao, cung, tuổi, mức của chính lá số | | |
| 18 | Dẫn chứng nhiều, phân tích ít | Thêm các tầng phân tích: cân, chân dung, diễn biến, cách cục, tổng luận | | |
| 19 | Thiếu kết luận tổng hợp có thứ bậc | **Chương Tổng luận** mới (cuối phần Tử Vi): xếp các lĩnh vực theo verdict (mạnh nhất có gốc, giữa, yếu nhất có gốc; lĩnh vực ngang sức nói là chưa xếp; sức khỏe không xếp), chặng đại hạn cao/thấp nhất, **bước ngoặt** lớn nhất, hạn hiện tại, một lời khuyên chung có nhãn | `prose/tong_luan.ts`, `tong_luan.json`, trang: mục "Tổng luận" | |

## 2. Số đo (trước → sau)

Phân xử hai mặt (300 lá đầu của corpus, `reason/ledger.ts`): số lĩnh vực **"chưa phân xử"** trước = chua_phan_xu cũ, sau = phần còn lại
khi thang cân thấy hai bên ngang nhau (phần kia thành `nghieng_ve`).

| Lĩnh vực | Chưa phân xử trước | Sau | Thành nghiêng về (+ / −) |
|---|---|---|---|
| đường công danh | 128 | 45 | 76 / 7 |
| khả năng kiếm tiền | 215 | 51 | 144 / 20 |
| tích lũy, nhà cửa | 114 | 44 | 53 / 17 |
| hôn nhân | 139 | 73 | 29 / 37 |

Lý do đứng đầu của các verdict cân: bậc chỗ đứng (chính tinh / phụ tinh) 227, độ sáng 68, số chỗ đứng 57, cung chính 20, Tuần/Triệt 15.

Lặp trong một báo cáo (`tools/interpret/eval_repeat.ts --n 100`; Tử Vi + đại hạn + hai chương mới, sau `checkedOnly`):

| Đo | Trước (ef62dc5) | Sau |
|---|---|---|
| câu trùng nguyên văn / báo cáo | 5,84 | **2,24** |
| cụm 6 chữ lặp / 100 câu | 148,7 | **115,1** |
| câu "chưa phân xử / chưa xếp được" / báo cáo | 10,16 | **4,28** |
| câu nêu kết luận lĩnh vực / lĩnh vực / báo cáo | 3,80 | 4,40 |

Câu nêu kết luận tăng vì có thêm Tổng luận (mỗi lĩnh vực một lần) và câu "cân hai bên"; số lần **nhắc lại** sau lần nói đủ bị chặn ≤2
(test `review19.test.ts`). Số câu mỗi báo cáo: 280 → 317.

Cổng tổng hợp cũ (`eval_synthesis.ts --n 300`), trước và sau đều: giới hạn chưa đối diện 0, kết luận một sao 0, mâu thuẫn chưa giải thích 0,
verdict vênh nhau 0.

## 3. Kiểm thử

- `node --test src/interpret/test/*.test.ts`: **240/240 qua** (gồm 7 test mới `review19.test.ts`: cân hai mặt có lý do, Tổng luận không xếp
  sức khỏe và không thêm ý, Cách cục chỉ dùng luật verified, diễn biến chỉ dùng tuổi có trong lá và Phu Thê không phán sự kiện, chân dung chỉ
  nhắc nét đã nói, Tật Ách không kết luận sức khỏe, cung người thân không có câu minh họa, nhắc lại ≤2, đại hạn có câu so với hạn trước).
- Golden cập nhật (đã đọc diff): `menh_cu_tuat.luan.txt`, `menh_cu_tuat.van_han.prose.txt`.
- Phần Python không đổi (engine không sửa).
- Xem trên trang (dev server `tvbt-prose`, lá mẫu 17/05/1990): mục 08 Cách cục và 09 Tổng luận hiện đúng chỗ trong tab Tử Vi.

## 4. Khoảng trống

- Bát Tự (điểm 6): phiên riêng, đã lên main (4d777fc, `docs/audit/REVIEW-19-BAZI.md`). Kiểm trang 10 cách cục: phiên riêng, đã gộp và dùng trong chương Cách cục.
- Tâm lý / năng lực / quan hệ xã hội sâu hơn cần thêm luật có trang; khung câu không thay được tri thức.
- So sao hạn với Thân (KL tr.234), lưu Tuần/Triệt, đuôi `van_han_rules.json` bị cắt: như DEEP-TUVI-2 §8.
- Thang cân là quy ước của hệ thống (có nhãn); chủ dự án có thể chỉnh trọng số / margin trong `engine/data/kg/domains.json → weigh`.
