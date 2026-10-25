# DEEP-3 — Chiều sâu luận giải Thiên Bàn (2026-10-24/25)

Kế hoạch: `~/.claude/plans/pasted-content-id-885b-prompt-radiant-donut.md`. "Trước" = main `743c094` (bản live đầu đợt); "sau" = main sau đợt
này. Giữ nguyên: không LLM khi chạy, không đổi thuật toán lập lá số, không đổi giao diện; mỗi câu là dữ kiện lá số + lời sách đã kiểm trang
(hoặc bản chụp đã lưu), hoặc lời tổng hợp có nhãn của hệ thống; không câu phổ thông; câu nhạy cảm (chết, bệnh, số con, ly hôn, tù) bỏ ngay
khi khai thác. Quyết định của chủ dự án trong đợt (2026-10-24): **văn bản cổ thuộc phạm vi công cộng trên mạng** (紫微斗數全書, 穷通宝鉴 trên
zh.wikisource) là nguồn verified khi câu trích khớp bản chụp đã lưu, dẫn theo quyển/mục thay cho trang.

Báo cáo khai thác chi tiết: [DEEP-3-mining-tuvi.md](DEEP-3-mining-tuvi.md), [DEEP-3-mining-bazi.md](DEEP-3-mining-bazi.md). Ví dụ trước / sau:
[../examples/deep-3-truoc-sau.md](../examples/deep-3-truoc-sau.md).

## 1. Audit đầu đợt (743c094, 200 lá)

| Chương | câu / lá | câu khung + hệ thống | câu lặp ở ≥5% lá | nguyên nhân chính (tệp) |
|---|---|---|---|---|
| Tử Tức | 8,5 | 54% | 7,3% | cung VCD chỉ còn câu khung; nét của con cái kể như của đương số (`luan.ts tail`) |
| Phụ Mẫu | 10,4 | 42% | 8,6% | "Phụ Mẫu quá đẹp…" bắn với một sao đắc (`depth.ts`); Nhật Nguyệt không tách theo cha / mẹ |
| Nô Bộc | 11,7 | 46% | 15,2% | câu định nghĩa của Thiên Di in trơ ở mọi lá (`domains.json depth.no_boc`) |
| Tài Bạch | 17,4 | 62% | 3,7% | dài vì sổ cái và diễn biến, ít luận điểm mới |
| Cách cục (TV) | 7,2 | 50% | 51,7% | câu mức độ đổ cho "vì đứng ở Mệnh"; cách bị phá in nhãn chung của luật (`cach_cuc.ts`) |
| Cách cục & dụng thần (BT) | 17,7 | 47% | 19,6% | "mới xác lập một phần" ở 152/200 lá; minh họa đứng trước câu đổi dụng thần (`bazi_deep.ts`) |

Khoảng trống tri thức: Tử Tức 35 luật verified (Toàn Thư 1), Phụ Mẫu 52, Nô Bộc 80; 9 cách đã kiểm trang; Bát Tự 0 luật con cái, 4 luật
dụng/hỷ/kỵ (nháp), bảng Tử Bình Chân Thuyên viết từ trí nhớ (nháp).

## 2. Đã làm

### A. Sửa bộ máy văn
- Cách cục: cách bị phá **gọi tên sao phá và chỗ nó đứng** (`structures.ts presentOf`); câu mức độ nói đúng lý do hạ bậc, cách xấu có câu
  riêng; câu cân tốt/xấu chỉ khi có cả hai phía, gọi tên từng cách; tên cách ngắn, lời giải của luật nói một lần.
- Đọc sâu: câu quan hệ cung của sách luôn đi cùng phía lá số trong một câu (≤35 chữ); câu định nghĩa không còn đứng trơ; "Phụ Mẫu quá đẹp"
  (KL tr.220) cần cung thật đẹp; Nô Bộc dùng câu của chính nó ("giàu nghèo vì bạn"); cung VCD nêu sao mượn (TT tr.18).
- Câu rào Tuần/Triệt nói nó uốn **luận điểm tốt nào**; cung VCD chỉ nêu vị trí, lý do (KL tr.146: Tuần Triệt bảo vệ cung VCD) vào Đọc sâu;
  câu "một sao" nói thiếu gì.
- Cung người khác (Tử Tức, Phụ Mẫu, Nô Bộc, Huynh Đệ): nét của họ không thành lời khuyên cho đương số, không bị ghép với nét của đương số,
  không ghép hai nét của họ thành câu khuôn.
- Bát Tự: minh họa đứng sau câu đổi dụng thần; bỏ trích dẫn lặp, lead-in lặp; trạng thái "một phần" nêu lý do của lá (sát ranh vượng/nhược);
  câu "hai thước đo" là một câu riêng của lá; lời "cát: …" / "hung: …" đọc thành "cát, vì …".

### B. Khai thác tri thức (hai phiên song song, đã gộp)
| | Trước | Sau |
|---|---|---|
| Luật Tử Vi verified | 1.468 | 1.647 (Tử Tức 35→52, Nô Bộc 80→119, Huynh Đệ 28→45, Phụ Mẫu 52→57, Mệnh 600→695) |
| Cách đã kiểm trang | 9 | 29 (28 có **ý nghĩa theo trạng thái** thành / thượng / hình thức / phá, có trang) |
| Chế hóa có trang | rải rác trong luật | 63 quan hệ (`kg/che_hoa.json`, KL tr.55–206, Nghiệm Lý tr.15) |
| Thế đứng / tổ hợp | nhóm KL tr.166-167 | + 11 thế đứng theo vị trí Tử Vi (KL tr.180–186), 7 cặp (`kg/combos.json`) |
| Khác biệt trường phái | 0 | Tử Vi 28 chủ đề (KL/TH/TT/Hán văn), Bát Tự 62 (55 ô điều hậu TVH ↔ 穷通宝鉴) |
| Luật Bát Tự (kin) verified | 237 | 361 (con cái 0→11, học hành 0→7, cát hung/thanh trọc/chân giả 0→30, dụng thần TTT 0→10) |
| Dụng/hỷ/kỵ có trang | 4 (nháp) | 132 nguyên lý (`bazi_deep/hyky.json`) |
| Thành/phá/cứu theo cách | 39 câu TVH | 12 cách (`bazi_deep/thanh_pha.json`); TBCT vẫn nháp, không nói |

Nguồn mới: Toàn Thư pp.64–76, 91–93, 112–120, 141–149; Khảo Luận pp.43–48, 55–206, 166–186; Thực Hành pp.72–74, 79–81, 130–133;
紫微斗數全書 卷一/卷二 (bản chụp zh.wikisource, revid + sha256); Nghiệm Lý (scan, chép tay pp.13–15); Trích Thiên Tủy pp.59–78, 101–112,
130–132, 143–148, 161–170, 183–201, 229–233; Thiệu Vĩ Hoa pp.158–173, 532, 546, 552–553; 八字真宗 pp.26–30, 72; 穷通宝鉴 (40 mục).
子平真詮: không có bản công cộng tải được (ctext cấm tải tự động) — giữ nháp, không bao giờ nói. Mọi câu trích qua `tools/book_text.py
quote_on_page` (nay nhận cả `WEB:<id>`, `SCAN:<id>`, TTT/TVH/ZZ theo văn bản trang đã commit).

### C–E. Lập luận nhiều tầng và Đọc sâu
Bộ suy luận vốn đã chia tầng (khung → chỗ đứng → trục → luận điểm → luận đề → bước); đợt này **bổ sung các tầng còn thiếu vào bộ máy sẵn có**
thay cho một tệp `argue.ts` mới như kế hoạch ban đầu (tránh hai đường lập luận song song):
- **Chế hóa** (Đọc sâu, mọi cung): sao chế và sao bị chế đứng đúng chỗ trang sách nói, điều kiện của trang (cung, độ sáng, đủ cặp chính tinh)
  được kiểm trên lá; tối đa 2 câu một cung; ngoài Mệnh chỉ nói phần chế hóa, không mang hệ quả viết cho Mệnh (`reason/depth.ts cheHoaUnits`).
- **Thế đứng của 14 chính tinh** theo vị trí Tử Vi (KL tr.180–186; Đọc sâu Mệnh).
- **Ý nghĩa của cách theo trạng thái** thay cho dòng mức độ của hệ thống (Cách cục).
- **Khác biệt trường phái**: cách được nói mà các bộ định nghĩa khác nhau (Đọc sâu Cách cục); ô điều hậu mà bảng kia chọn can khác (Đọc sâu
  Cách cục Bát Tự; tên sách ở căn cứ, không ở văn).
- **Phụ Mẫu theo người**: Thái Dương = cha, Thái Âm = mẹ (KL tr.85, 100), cân độ sáng + Hóa từng phía (câu tổng hợp có nhãn).
- **Bát Tự**: dụng thần theo vượng nhược thuần túy (TTT tr.63) đặt cạnh nhóm của bảng theo cách (trùng → hai chỗ dựa; khác → hai phép chưa
  trùng); đoạn cát hung / thanh trọc / chân giả thần của cả lá trong chương Cách cục; con cái và học hành trong Đọc sâu.

## 3. Đo trên 1.000 lá

`node tools/interpret/eval_deep3.ts --n 1000` (công cụ mới), corpus1000 với cùng facts cho hai phía; "sau" đo ở `be550af` — trước ba sửa
cuối (`05d40ad` và commit sau đó), các sửa này chỉ bớt câu lặp (Nô Bộc "giàu nghèo vì bạn" 535 lá, Tử Tức câu ghép hai nét ~160 lá, Cách cục
"Riêng phần lõi đã là một quý cách" ~475 lá), nên cột lặp ở bảng là cận trên. Cột: câu/lá; % lá ≤3 câu; % câu khung + hệ thống; % câu có
căn cứ sách (basis sach + trang); % câu lặp nguyên văn ở ≥5% lá; % câu lặp khung (đã che tên sao, cung, can chi, số); % lá có câu điều kiện;
câu nêu ≥2 sao / lá; % câu nêu dữ kiện riêng của lá.

| Chương | câu/lá | ≤3 câu | khung+hệ thống | có căn cứ sách | lặp nguyên văn | lặp khung | có điều kiện | ≥2 sao/lá | riêng của lá |
|---|---|---|---|---|---|---|---|---|---|
| Tử Tức | 8,7 → 11,3 | 4,4 → 1,2 | 44,7 → 33,2 | 45,7 → **58,7** | 7,0 → **1,9** | 8,8 → 3,4 | 38,4 → 49,0 | 2,98 → 4,79 | 82,3 → 85,1 |
| Phụ Mẫu | 9,7 → 10,5 | 0,5 → 0,9 | 30,6 → 29,4 | 58,0 → 62,1 | 5,2 → **0** | 7,6 → 2,2 | 42,3 → 42,6 | 3,26 → 4,36 | 83,8 → 85,4 |
| Nô Bộc | 11,4 → 12,8 | 0 → 0,1 | 28,0 → 24,7 | 53,9 → **63,1** | 13,8 → 4,2* | 14,7 → 4,6 | 47,2 → 48,3 | 3,41 → 4,95 | 87,4 → 82,5 |
| Tài Bạch | 17,7 → 19,1 | 0 → 0 | 47,8 → 44,1 | 38,2 → 43,0 | 2,6 → 2,1 | 11,6 → 11,7 | 63,6 → 66,2 | 7,61 → 8,97 | 88,3 → 89,3 |
| Cách cục (TV) | 5,7 → 10,4 | 26,8 → **6,6** | 49,1 → 42,3 | 50,9 → 57,7 | 53,6 → 28,8* | 56,9 → 43,6 | 0 → 0 | 0,81 → 2,87 | 74,4 → 80,0 |
| Cách cục & dụng thần (BT) | 17,6 → 20,6 | 0 → 0 | 10,8 → 9,2 | 22,5 → **37,5** | 16,0 → 11,5 | 37,7 → 30,7 | 69,2 → 88,8 | 0,2 → 0,2 | 84,7 → 90,0 |

\* phần lớn phần còn lại là câu đã sửa ở `05d40ad` (Nô Bộc: câu "giàu nghèo vì bạn" in trơ; Cách cục: "Riêng phần lõi đã là một quý cách").

Không chương nào dài ra chỉ vì chữ: số câu có căn cứ sách tăng nhanh hơn số câu (Tử Tức +2,6 câu/lá, trong đó câu có trang +2,6; Cách cục BT
+3 câu/lá, câu có trang +3,8). Câu khung + hệ thống giảm ở mọi chương ưu tiên.

Cổng tổng hợp (`eval_synthesis.ts --n 300`), trước và sau đều **0**: giới hạn chưa đối diện 0, kết luận một sao 0, mâu thuẫn chưa giải thích 0,
verdict vênh nhau 0, lỗi 0.

| Đo khác | Trước | Sau |
|---|---|---|
| Bát Tự: câu phần chính / lá (`bazi_main_share.ts`, 1.000 lá) | 75,0 | 77,2 |
| Bát Tự: tỉ lệ `tinh_toan` ở phần chính | 34% | 33% |
| Bát Tự Cách cục: câu phần chính / lá · tỉ lệ `tinh_toan` | 6,9 · 32,2% | 9,2 · **24,3%** |
| Lặp nguyên văn trong một báo cáo (`eval_repeat.ts`, 100 lá) | 2,36 | 2,79 |
| Cụm 6 chữ lặp / 100 câu | 114,2 | 116,4 |
| Câu "chưa phân xử" / báo cáo | 4,28 | 4,14 |
| Nhắc kết luận lĩnh vực / lĩnh vực | 4,40 | 4,32 |

Lặp trong một báo cáo tăng nhẹ: các câu lặp đều ở chương Đại hạn (câu khung "Về mức chung, chặng này giữ ngang chặng trước", "Gộp các lớp
lại…" qua mười hạn, và một câu sách của `van_han_rules` cho nhiều hạn có sát tinh), có từ trước đợt này; đợt này thêm câu cho đại hạn nên số tuyệt
đối tăng. Các chương ưu tiên không có câu lặp trong báo cáo.

## 4. Kiểm thử

KẾT_QUẢ_TEST

## 5. Còn lại
- Câu minh họa Bát Tự (bệnh–thuốc, ngày giá rét) lặp ở khoảng 16% lá — đúng chính sách minh họa, có thể thêm biến thể.
- Phụ Mẫu "cha mẹ xa cách nhau" lặp vì cùng một luật sách bắn ở nhiều lá — tri thức, không phải khung câu.
- Tử Bình Chân Thuyên chưa có bản công cộng; thành/phá theo TBCT giữ nháp.
- `combos.json per_palace` trỏ về luật sẵn có; chưa có câu riêng cho tổ hợp ngoài các luật ấy.
- Chương Đại hạn: câu khung mức độ / so với hạn trước lặp qua mười hạn; câu sách `van_han_rules` cho nhiều hạn có sát tinh nên gọi lại ngắn
  sau lần đầu (như `kl_again`).
- Đo 1.000 lá ở bảng §3 là của `be550af`; nên chạy lại `eval_deep3.ts` trên bản cuối khi máy rảnh (≈20 phút).
