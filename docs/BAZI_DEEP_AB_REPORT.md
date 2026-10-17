# So sánh trước/sau trên EX1–EX15

Sinh bởi `tools/bazi_deep_compare.py`. **Trước** = pipeline cũ đã đóng băng (`engine/tests/golden/bazi_deep_baseline.json`): đắc lệnh là boolean, căn là danh sách trụ, chỉ quan hệ từng cặp, không có cách cục/dụng thần.
**Sau** = `tvbt.bazi_deep` với `SchoolProfile baseline_v1` (mọi trọng số, ngưỡng, bảng cách: **draft**, chưa đối chiếu sách). Lá số EX không có giờ sinh thực nên tư lệnh TẮT.

| Mã | Tứ Trụ | Trước | Khí thế: nguyên cục → sau tương tác | Trục lệnh/địa (sau) | Tương tác (số, trạng thái) | Cách cục | Hợp can mạnh nhất | Số finding |
|---|---|---|---|---|---|---|---|---|
| EX1 | Giáp Tý / Bính Dần / Giáp Tuất / Canh Ngọ | có / căn: 1 trụ / 4 quan hệ cặp | thiên nhược → **nhược** ⚠ sát ranh giới | đắc lệnh; căn yếu | 4 (formed, xung_ke, xung_xa, xung_xa_cuc) | Kiến Lộc (thanh); ngoại: — | khong_co | 4 |
| EX2 | Quý Dậu / Ất Mão / Mậu Tý / Đinh Tỵ | không / căn: 1 trụ / 5 quan hệ cặp | cực nhược → **cực nhược** ⚠ sát ranh giới | thất lệnh; căn yếu | 6 (co_hieu_luc, khong_ke, xa, xung_nho, xung_xa) | Chính Quan (bai); ngoại: — | khong_ke | 4 |
| EX3 | Tân Mão / Đinh Dậu / Giáp Thìn / Giáp Tý | không / căn: 2 trụ / 5 quan hệ cặp | nhược → **nhược** | thất lệnh; căn yếu | 6 (bi_tranh, formed, xa, xung_nho) | Chính Quan (bai); ngoại: — | khong_co | 5 |
| EX4 | Canh Thân / Ất Dậu / Ất Dậu / Tân Tỵ | không / căn: 0 trụ / 7 quan hệ cặp | cực nhược → **cực nhược** | thất lệnh; căn không | 9 (co_hieu_luc, formed, khong_ke, tranh_hop, xa, xung_ke, xung_xa) | Thất Sát (thanh_nhung_bi_pha); ngoại: Tòng Sát (giả) | tranh_hop | 5 |
| EX5 | Mậu Tuất / Kỷ Mùi / Giáp Tuất / Mậu Thìn | không / căn: 2 trụ / 5 quan hệ cặp | cực nhược → **cực nhược** | thất lệnh; căn yếu | 6 (co_hieu_luc, gia_hoa, xung_nho, xung_xa) | Chính Tài (bai); ngoại: Hóa Thổ (giả), Tòng Tài (giả) | gia_hoa | 5 |
| EX6 | Nhâm Tý / Mậu Thân / Canh Thìn / Nhâm Ngọ | có / căn: 1 trụ / 2 quan hệ cặp | trung hòa → **nhược** | đắc lệnh; căn yếu | 2 (formed, xung_xa_cuc) | Kiến Lộc (thanh); ngoại: — | khong_co | 5 |
| EX7 | Canh Tý / Nhâm Ngọ / Đinh Dậu / Quý Mão | có / căn: 1 trụ / 7 quan hệ cặp | trung hòa → **thiên vượng** | đắc lệnh; căn mạnh | 7 (hop_khong_hoa, xa, xung_ke, xung_nho) | Kiến Lộc (thanh_nhung_bi_pha); ngoại: — | hop_khong_hoa | 5 |
| EX8 | Giáp Thân / Bính Tý / Bính Dần / Giáp Ngọ | không / căn: 2 trụ / 2 quan hệ cặp | thiên nhược → **trung hòa** ⚠ sát ranh giới | thất lệnh; căn yếu | 5 (formed, xa, xung_xa) | Chính Quan (thanh); ngoại: — | khong_co | 4 |
| EX9 | Nhâm Dần / Bính Ngọ / Bính Tuất / Mậu Tý | có / căn: 3 trụ / 4 quan hệ cặp | trung hòa → **vượng** | đắc lệnh; căn yếu | 4 (formed, xung_ke, xung_xa, xung_xa_cuc) | Dương Nhận (thanh); ngoại: — | khong_co | 4 |
| EX10 | Canh Thân / Mậu Dần / Giáp Thân / Canh Ngọ | có / căn: 1 trụ / 4 quan hệ cặp | thiên nhược → **thiên nhược** ⚠ sát ranh giới | đắc lệnh; căn mạnh | 6 (co_hieu_luc, formed, xung_ke, xung_vao_cuc, xung_xa) | Kiến Lộc (thanh_nhung_bi_pha); ngoại: — | khong_co | 5 |
| EX11 | Tân Sửu / Nhâm Thìn / Ất Mão / Đinh Hợi | không / căn: 3 trụ / 4 quan hệ cặp | thiên nhược → **thiên nhược** | thất lệnh; căn vừa | 5 (co_hieu_luc, formed, khong_ke, xung_xa) | Chính Tài (thanh); ngoại: — | khong_ke | 4 |
| EX12 | Quý Hợi / Kỷ Mùi / Canh Tý / Kỷ Mão | có / căn: 0 trụ / 3 quan hệ cặp | thiên vượng → **trung hòa** ⚠ sát ranh giới | được lệnh sinh; căn không | 3 (co_hieu_luc, formed) | Chính Ấn (thanh); ngoại: — | khong_co | 5 |
| EX13 | Giáp Thìn / Đinh Mão / Bính Dần / Quý Tỵ | có / căn: 2 trụ / 4 quan hệ cặp | cực vượng → **cực vượng** | được lệnh sinh; căn mạnh | 5 (co_hieu_luc, formed, xung_xa) | Chính Ấn (thanh); ngoại: — | khong_co | 3 |
| EX14 | Giáp Tý / Bính Dần / Kỷ Sửu / Canh Ngọ | không / căn: 3 trụ / 5 quan hệ cặp | thiên nhược → **thiên vượng** ⚠ sát ranh giới | thất lệnh; căn yếu | 6 (co_hieu_luc, formed, khong_ke, xung_xa, xung_xa_cuc) | Chính Quan (thanh), Chính Ấn (thanh); ngoại: — | khong_ke | 4 |
| EX15 | Nhâm Dần / Quý Mão / Ất Mão / Bính Tý | có / căn: 3 trụ / 3 quan hệ cặp | cực vượng → **cực vượng** | đắc lệnh; căn mạnh | 3 (co_hieu_luc, xa, xung_xa) | Kiến Lộc (thanh); ngoại: — | khong_co | 2 |

## Tổng hợp

- Quan hệ: cũ tìm 64 quan hệ cặp trên 15 lá số; mới ghi 77 tương tác (có thêm bán hợp, củng hợp, bán hình, vị trí kề/cách vị, trạng thái đã giải).
- Tương tác làm đổi mức khí thế Nhật Chủ ở 7/15 lá số.
- Cách cục: cũ 0/15 lá số có nhãn; mới định được ứng viên ở 15/15; 3 lá số có cách đang bại.
- Khí thế sát ranh giới (hệ thống không chọn một mức): 6/15.
- Các phương pháp dụng thần bất đồng ít nhất một nhóm thập thần: 4/15.

Mọi số liệu trên là kết quả của quy tắc hệ thống đang ở trạng thái draft; chúng cho thấy hệ thống đã làm gì khác trước, không chứng minh kết luận mệnh lý đúng.
