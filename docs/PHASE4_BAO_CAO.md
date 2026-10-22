# Phase 4 — xác minh nguồn và cách ly trường phái (báo cáo theo module)

Phạm vi: không thêm cách cục, luật Phi Hóa hay lưu tinh mới. Chỉ audit, thêm test và sửa nhãn. Không deploy. Không sửa `api.py`, không đụng file chưa hoàn thành của phiên khác. Công việc nằm trên nhánh riêng `phase4-audit` (worktree), chưa merge.

Hai nghĩa của "verified" được tách rõ trong báo cáo này:
- **kỹ thuật**: code làm đúng điều nó nói (có test, có oracle độc lập);
- **mệnh lý**: điều kiện khớp một trang sách. **Không điều kiện mệnh lý nào trong các module dưới đây đạt mức này trong audit này**, vì không có cuốn sách nào đọc trực tiếp được ở phiên này.

Giới hạn truy xuất: ba cuốn dùng ở các phiên trước không nằm trong thư mục dự án. Tôi không mở file cá nhân trên máy để tìm. Nguồn duy nhất tôi truy xuất được thêm là 紫微斗數全書 trên zh.wikisource.org, qua công cụ tóm tắt trang (tải thô bị chặn), nên chỉ là **một bản web, chưa đối chiếu bản in**.

## 1. Cách cục (10 cách, định nghĩa v2)

Bảng đầy đủ từng điều kiện: [PHASE4_BANG_NGUON_CACH_CUC.md](PHASE4_BANG_NGUON_CACH_CUC.md) (sinh bởi `tools/build_formation_source_audit.py`, dữ liệu `engine/data/experimental/formation_source_audit.json`).

Tầng bằng chứng: T0 đọc trực tiếp trang sách · T1 luật registry đã verified · T2 luật registry còn draft · T3 câu phú gốc từ bản web · T4 giả thuyết. Registry **không được coi là bằng chứng độc lập**: nó chỉ lưu diễn giải tiếng Việt, không có nguyên văn (cột "nguyên văn" ghi rõ điều đó thay vì bịa trích dẫn). Chỉ nguồn có mức tương ứng `khop` mới tính là ủng hộ.

| | Số điều kiện |
|---|---|
| Tổng số thành phần (lõi, tăng thế, phá, cứu, phản chứng) | 93 |
| Có nguồn ủng hộ ở T1 | 10 |
| T2 | 4 |
| T3 | 2 |
| **T4, giả thuyết thiết kế** | **77** |
| T0 | 0 |

- **Verified facts (kỹ thuật)**: máy trạng thái (không hiện, hình thức, thành, thành thượng, bị phá, được cứu, phản chứng hạ bậc) có test từng cách và đối chiếu oracle độc lập ở phiên UI (vét cạn 525.960 lá số).
- **Verified facts (mệnh lý)**: không có. Mười thành phần khớp luật registry đã verified (ví dụ Thái Dương cư Ngọ ↔ TH p.72; Khôi Việt giáp Mệnh ↔ KL p.215; Cự Môn Tý/Ngọ hội đủ Tam Hóa ↔ KL p.58, TT p.34), nhưng đó là diễn giải của chính dự án.
- **Experimental rules**: cả 10 cách, `draft`, ngoài `PACKS`, chỉ qua `experimental`.
- **Xung đột nguồn phát hiện** (ghi trong audit, có test):
  1. **Mã đầu đới kiếm**: KL p.64 trong registry (draft) nói Kình Dương ở Ngọ; chú giải trong 定貴局 (T3) nói "Mã có nhận" và nói rõ **không phải cách cư Ngọ**. Điều kiện lõi chưa thể coi là đã xác định.
  2. **Thạch trung ẩn ngọc**: sách Việt (KL p.58, TT p.34) đòi Khoa + Quyền + Lộc đủ; phú gốc (T3) chỉ nêu Khoa và Lộc (科祿) chiếu. Booster `tam_hoa_hoi_du` chặt hơn câu phú.
  3. **Triệt giải sát tinh** (v1): không nguồn nào ủng hộ, và TH pp.94-95 (verified) nói Tuần/Triệt bất lợi. Đã loại ở v2.
- **Nguồn còn thiếu**: nguyên văn và trang in cho cả 93 thành phần; đặc biệt 77 giả thuyết (booster Tả Hữu/Xương Khúc, phần lớn breaker Kỵ/Không Kiếp, mọi rescuer ngoài Tam Hóa, lõi "đủ bốn sao ở tam phương" của Tử Phủ Vũ Tướng, lõi "≥3 trong 4 sao" của Sát Phá Liêm Tham).
- **Điều kiện nâng cấp một thành phần lên T0/`verified`**: đọc lại trang sách trực tiếp, chép nguyên văn vào `sources.json` kèm `locator`, đối chiếu ít nhất một nguồn thứ hai độc lập, viết golden test bằng lá số mẫu trong sách. Với cách có xung đột (Mã đầu đới kiếm, Thạch trung ẩn ngọc) phải giải quyết xung đột trước.

## 2. Phi Hóa

- **Bảng Tứ Hóa**: là bảng của hệ **Tam Hợp**, dùng lại bảng nguyên cục (verified cho Tứ Hóa lá số sinh theo Thực Hành p.21 và Khảo Luận pp.196-197). Nhãn trong code, API và trace từng cạnh nay ghi: `school: tam_hop`, `status: reused_unverified_for_phi_tinh`, `verified_for: [tam_hop_natal_tu_hoa]`, "chưa xác minh cho Phi Tinh". Không chỗ nào trình bày nó như bảng Phi Tinh.
- **Tách tính toán khỏi diễn giải**: `/api/phi-hoa` trả hai khối riêng. `computation` (level `computed`: bảng + 48 cạnh + trace, không có finding nào) và `interpretation` (level `experimental`, `reviewStatus: draft`: 10 luật, finding, ngoại lệ, xung đột). Có test khẳng định hai khối không lẫn khóa.
- **Oracle độc lập cho 48 cạnh** (`tests/test_phase4_phi_oracle.py`): 180 lá số thật × 48 cạnh. Oracle tự tính can cung bằng ngũ hổ độn từ can năm, lấy sao Tứ Hóa từ file khác (`data/tu_hoa_vi.json`, Khảo Luận pp.195-197) thay vì `tuvi.TU_HOA`, tự tìm cung giữ sao, tự tính nhãn hình học. Khớp 100% về cung phát hóa, can cung, sao nhận hóa, cung nhận hóa, nhãn, nghịch đảo `phi.in.*`, và trace chứa đủ cung, can, hóa, sao, cung nhận, bảng, nhãn chưa xác minh.
- **Hai cung trùng can**: 12 cung, 10 can nên Tý trùng can với Dần và Sửu trùng can với Mão (kiểm trong mọi lá số). Test chứng minh hai cung bay cùng một sao tới cùng một cung, và cung nhận liệt kê **cả hai** cung phát.
- **Experimental rules**: 10 luật `phi_tinh_draft` (giả thuyết cấu trúc).
- **Nguồn còn thiếu**: một tài liệu Phi Tinh cụ thể (bảng Tứ Hóa theo can, định nghĩa tự hóa/xung phi/chuỗi), và tên sách + trang cho từng khái niệm.
- **Xung đột trường phái**: tài liệu Phi Tinh có thể dùng bảng khác ở vài can; chưa có bảng nào được kiểm nên `stars_for` từ chối id lạ. Cách ly (`validate_isolation`) ngăn luật tam hợp đọc `phi.*` và ngược lại.
- **Điều kiện nâng cấp**: thêm một bảng đã xác minh theo từng tài liệu vào `TABLES` (tách theo `school`), đối chiếu 48 cạnh với một lá số mẫu trong chính tài liệu đó, rồi mới cân nhắc đổi nhãn.

## 3. Lưu tinh (và tầng đại hạn / lưu niên)

Hồ sơ audit: `engine/data/experimental/luu_tinh_audit.json`.

- **Verified facts**: các bảng **nguyên cục** (Lộc Tồn, Kình, Đà theo can; Khôi, Việt theo can; Thiên Mã theo chi) đã verified ở Thực Hành pp.19-24 cho lá số sinh.
- **Phép an lưu theo năm**: **không có nguồn**. Tìm trong toàn bộ `pack_*.json` không có luật nào về lưu Lộc/Kình/Đà/Khôi/Việt/Mã (0 kết quả); `aux_stars.py` của dự án cũng ghi các sao này chưa được kiểm. Đây chỉ là suy rộng từ nguyên cục, nên giữ nhãn `experimental`. Test kiểm tính nhất quán duy nhất mà quy ước tuyên bố: vị trí lưu tinh của năm Y trùng vị trí sao nguyên cục của người sinh năm Y (5 năm).
- **Không tạo ra**: lưu Xương/Khúc, lưu Hỏa/Linh/Không/Kiếp, nguyệt hạn (không có công thức đã kiểm).
- **Experimental rules**: 13 luật tầng thời gian, trong đó 5 luật lưu tinh; tất cả `draft`.
- **Điều kiện nâng cấp**: một nguồn có trang nói rõ các sao này an theo can/chi năm xem bằng đúng các bảng nguyên cục, cùng một lá số mẫu trong sách làm golden test.

## 4. Cách ly trường phái và chế độ thử nghiệm (engine → API → UI)

`tests/test_phase4_isolation.py` (có test chứng minh bộ dò rò rỉ phát hiện được rò rỉ thật).

- **Engine**: registry production không chứa id, schoolId hay nguồn nào của vật liệu thử nghiệm; mọi luật thử nghiệm `draft`.
- **API**: 16 lời gọi mặc định trên 13 endpoint (chart, analysis, reasoning cả hai trường phái độ sáng, year, bazi-structure, bazi-timeline, twelve-gods, hour-sweep, compare-charts, compare-hours, rules, claims, dignity) không chứa bất kỳ chuỗi `phi.*`, `ph_*`, `ly_*`, `CACH_X_*`, `SRC_EXPERIMENTAL`, lưu tinh thử nghiệm. Bật `experimental` chỉ thêm đúng một khóa `experimental`; phần còn lại giống từng byte. Mỗi khối thử nghiệm chỉ chứa trường phái của mình (cách cục ↔ `reasoning`; lớp thời gian và lưu tinh ↔ `year`; Phi Hóa ↔ `phi-hoa`). Tổng luận (`reasoning.systems`, `analysis`) không có chữ "thử nghiệm".
- **UI (mã nguồn)**: UI không gọi `/api/phi-hoa` ở bất kỳ đâu; `/api/formations` chỉ được gọi khi `expOn()`; `/api/year` luôn gửi yêu cầu không có cờ thử nghiệm; không có chuỗi "Phi Hóa/Phi Tinh/Lưu Lộc Tồn" trong JS/HTML.
- **UI (chạy thật, trình duyệt)**, desktop và mobile (375 px), từ máy chủ dựng bằng nhánh này:
  - mặc định và `?thu-nghiem=off` (mạng kiểm ở bản desktop): huy hiệu "Thử nghiệm" ẩn; 0 lần xuất hiện "thử nghiệm"; 0 rò rỉ; mạng chỉ gọi chart/reasoning/analysis/year; không lỗi console; không tràn ngang trên mobile;
  - `?thu-nghiem`: huy hiệu hiện; có thêm `/api/formations`; tab Tử Vi có 3 chỗ gắn nhãn "thử nghiệm"; 0 rò rỉ tên luật/id nội bộ; không gọi `/api/phi-hoa`; không lỗi console; không tràn ngang.

## 5. Ngôn ngữ

`tests/test_phase4_audit.py` quét mọi câu thử nghiệm (mô tả 10 luật Phi Hóa, 13 luật tầng thời gian gồm 5 luật lưu tinh, 3 luật demo, tên và nhãn mọi thành phần cách cục, mọi nhãn trạng thái, mọi câu `render_vi`, cảnh báo của ba endpoint thử nghiệm) tìm lối nói chắc chắn ("chắc chắn", "nhất định", "sẽ", "tất yếu", "đảm bảo", "định mệnh", "tuyệt đối"...). Không có. Mọi luật thử nghiệm bắt đầu bằng nhãn "[thử nghiệm", và mọi câu cách cục đang có trạng thái đều kèm "bản thử nghiệm… không dự báo". Tên `claim` chỉ là định danh máy.

## 6. Hồi quy

- **HEAD sạch** (`d0c3ab8`, export bằng `git archive`): `pytest` **879 passed, 1 skipped, 2 xfailed**.
- **Nhánh `phase4-audit`** (HEAD + Phase 4, rebase trên `d0c3ab8`): **1081 passed, 1 skipped, 2 xfailed**, 0 hỏng. (202 test mới.)
- Không có thay đổi nào ở code production (`api.py`, `tuvi.py`, `analysis.py`…). File sửa: `phi_hoa/{tables,graph}.py`, `phi_hoa_api.py` (response tách hai khối; endpoint này là thử nghiệm và chưa có UI), cộng dữ liệu/test/công cụ audit.

## 7. Việc cần quyết định

1. Merge `phase4-audit` vào `main` (commit `67657ba` + báo cáo này); tôi không tự merge hay deploy.
2. Đưa sách hoặc trang để lên T0: ưu tiên KL p.64 (Mã đầu đới kiếm), KL p.58/TT p.34 (Thạch trung ẩn ngọc), TT p.24 (Cơ Nguyệt Đồng Lương), TH pp.74, 76, 77.
3. Với Phi Hóa: chọn một tài liệu Phi Tinh cụ thể làm chuẩn trước khi thêm bảng riêng.
