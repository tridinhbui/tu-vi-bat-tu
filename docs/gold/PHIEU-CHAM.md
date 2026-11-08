# Phiếu chấm tình huống miền (G4.4)

Mỗi tình huống: lá số (ngày giờ sinh trong corpus), miền đang xét, các chứng cứ bộ máy đã kích hoạt, và kết luận nháp hiện tại. Xin ghi vào `src/interpret/test/fixtures/gold/cases.json` (hoặc trả lời theo số thứ tự): `expected.lean` (thuận / khó / ngang), `expected.strength` (nhẹ / vừa / rõ), `expected.dominant` (yếu tố chi phối), `expected.reducers` (yếu tố làm giảm), `forbidden` (những kết luận không được phép), `why` (lý do).

Tập kiểm định độc lập (`holdout.json`, 15 tình huống từ các lá khác) xin chấm **trước** khi mình chỉnh trọng số; mình sẽ không mở nó trong lúc chỉnh. Bộ này đo tính nhất quán và chất lượng lập luận theo hệ quy tắc, không chứng minh khả năng dự đoán.

## 1. A · lá #0 (17/10/2016 11h, nữ) · đường công danh

Kết luận nháp: **co_dieu_kien (+)**, độ chắc vua, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_HOA_QUYEN_QUAN_LOC_HQ_QUAN_HOP_VI | uy thế và khả năng điều khiển người khác (Hóa Quyền, cung Quan Lộc)
  - rule:TV_HS_HOA_QUYEN_QUAN_LOC_QUAN_HOP_VI | uy thế và khả năng điều khiển người khác (Hóa Quyền, cung Quan Lộc)
  - rule:TV_HS_THIEN_CO_QUAN_LOC_QUAN_CO_LOI | sự thuận lợi trên đường công danh (Thiên Cơ, cung Quan Lộc)
  - rule:TV_HS_THIEN_CO_QUAN_LOC_QUAN_NGUYET_Y | năng lực nổi trội (Thiên Cơ, Thái Âm, cung Quan Lộc)
  - rule:TV_KL_STAR_QUAN_LOC_CO_NGUYET | năng khiếu chuyên môn, kỹ thuật (Thiên Cơ, Thái Âm, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_TA_HUU | khả năng kiêm cả văn lẫn võ (Tả Phụ, Hữu Bật, cung Quan Lộc)
  - rule:TV_TT_PAL_QUAN_LOC_THAI_AM_MIEU_P | triển vọng về địa vị, công danh (Thái Âm, cung Quan Lộc)
  - rule:TV_TT_PAL_QUAN_LOC_THAI_AM_WITH_THIEN_CO_P | sự thuận lợi trên đường công danh (Thái Âm, Thiên Cơ, cung Quan Lộc)
- Khó:
  - member:star:Tiểu Hao@Phu Thê | Tiểu Hao (Phu Thê): Tiểu Hao từ cung Phu Thê làm giảm sức
  - member:star:Linh Tinh@Mệnh | Linh Tinh (Mệnh): Linh Tinh từ cung Mệnh làm giảm sức
  - member:star:Đại Hao@Quan Lộc | Đại Hao (Quan Lộc): Đại Hao trong cung làm giảm sức
  - member:star:Hỏa Tinh@Quan Lộc | Hỏa Tinh (Quan Lộc): Hỏa Tinh trong cung làm giảm sức
- Tương tác:
  - Hóa Lộc đóng trên Thiên Đồng (KL pp.195-197)
  - Hóa Quyền đóng trên Thiên Cơ (KL pp.195-197)
  - Hóa Khoa đóng trên Văn Xương (KL pp.195-197)
  - Thiên Cơ rất sợ Hỏa, Linh (KL p.81)
- Cứu giải:
  - Hóa Khoa là sao cứu giải mạnh nhất (KL p.120)
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 2. A · lá #1 (26/10/2024 16h, nam) · đường công danh

Kết luận nháp: **nghieng_ve (+)**, độ chắc vua, tầm menh_tai_quan

- Thuận:
  - rule:TV_TH_P2_QUAN_LOC_TA_HUU | khả năng kiêm cả văn lẫn võ (Tả Phụ, Hữu Bật, cung Quan Lộc)
  - rule:TV_KL_PHU2_MA_TRUONG_SINH | sự thuận lợi trên đường công danh (Thiên Mã, Trường Sinh, cung Mệnh)
  - rule:TV_KL_PHU2_THIEN_MA | năng lực nổi trội (Thiên Mã, cung Mệnh)
  - rule:TV_TH_COMBO_CỰ_MON_VAN_TAI | năng lực học thuật, văn chương (Cự Môn, Văn Xương, cung Mệnh)
  - rule:TV_KL_AUX_TA_HUU | năng lực nổi trội (Hữu Bật, cung Mệnh)
  - rule:TV_KL_STAR_MENH_TA_HUU_XUONG | triển vọng về địa vị, công danh (Hữu Bật, Văn Xương, cung Mệnh)
  - rule:TV_TH_AUX_MENH_CHIEN_MA | uy thế và khả năng điều khiển người khác (Thiên Mã, Linh Tinh, cung Mệnh)
  - rule:TV_TH_AUX_MENH_MA_TAI_NANG | năng lực nổi trội (Thiên Mã, cung Mệnh)
- Khó:
  - rule:TV_KL_AUX_LOC_TON | thế đơn độc, ít người đỡ (Lộc Tồn, cung Mệnh)
  - rule:TV_TH_AUX_MENH_HKY_VAN_TINH | khoảng cách giữa học vấn và thành tựu (Hóa Kỵ, Văn Xương, cung Mệnh)
  - member:hoa:Thái Dương Hóa Kỵ@Mệnh | Thái Dương hóa Kỵ (Mệnh): Hóa Kỵ từ cung Mệnh làm vướng phần nó chạm tới
- Tương tác:
  - Quan Lộc mượn Thiên Đồng của Phu Thê (KL pp.218, 222)
  - Quan Lộc mượn Thái Âm của Phu Thê (KL pp.218, 222)
  - Hóa Kỵ đóng trên Thái Dương (KL pp.195-197)

## 3. A · lá #2 (13/11/1976 12h, nam) · đường công danh

Kết luận nháp: **nghieng_ve (+)**, độ chắc vua, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_THIEN_TUONG_QUAN_LOC_QUAN_QUYENTINH | sự thuận lợi trên đường công danh (Thiên Tướng, cung Quan Lộc)
  - rule:TV_HS_THIEN_TUONG_QUAN_LOC_QUAN_TOT | triển vọng về địa vị, công danh (Thiên Tướng, Vũ Khúc, cung Quan Lộc)
  - rule:TV_HS_THIEN_TUONG_QUAN_LOC_QUAN_TOT | khả năng kiêm cả văn lẫn võ (Thiên Tướng, Vũ Khúc, cung Quan Lộc)
  - rule:TV_HS_VU_KHUC_QUAN_LOC_QUAN_DAC | triển vọng về địa vị, công danh (Vũ Khúc, cung Quan Lộc)
  - rule:TV_HS_VU_KHUC_QUAN_LOC_QUAN_TUONG | sự thuận lợi trên đường công danh (Vũ Khúc, Thiên Tướng, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_TA_HUU | khả năng kiêm cả văn lẫn võ (Tả Phụ, Hữu Bật, cung Quan Lộc)
  - rule:TV_TT_PAL_QUAN_LOC_THIEN_TUONG_MIEU_P | khả năng kiêm cả văn lẫn võ (Thiên Tướng, cung Quan Lộc)
  - rule:TV_D3_TT74_DA_TU_MO_TU_PHU | chủ đề danh tiếng (Đà La, Tử Vi, Thiên Phủ, cung Mệnh)
- Khó:
  - rule:TV_TH_AUX2_MENH_TUE_KY_DA | những trở ngại trên đường công danh (Thái Tuế, Hóa Kỵ, Đà La, cung Mệnh)
  - rule:TV_TH_AUX_MENH_HKY_VAN_TINH | khoảng cách giữa học vấn và thành tựu (Hóa Kỵ, Văn Xương, Văn Khúc, cung Mệnh)
  - member:hoa:Liêm Trinh Hóa Kỵ@Mệnh | Liêm Trinh hóa Kỵ (Mệnh): Hóa Kỵ từ cung Mệnh làm vướng phần nó chạm tới
  - member:star:Đại Hao@Phu Thê | Đại Hao (Phu Thê): Đại Hao từ cung Phu Thê làm giảm sức
  - member:star:Linh Tinh@Mệnh | Linh Tinh (Mệnh): Linh Tinh từ cung Mệnh làm giảm sức
  - member:star:Tiểu Hao@Quan Lộc | Tiểu Hao (Quan Lộc): Tiểu Hao trong cung làm giảm sức
  - member:star:Hỏa Tinh@Quan Lộc | Hỏa Tinh (Quan Lộc): Hỏa Tinh trong cung làm giảm sức
  - member:star:Phá Quân@Phu Thê | Phá Quân (Phu Thê): Phá Quân hãm ở cung Phu Thê hội về
- Tương tác:
  - Hóa Khoa đóng trên Văn Xương (KL pp.195-197)
  - Hóa Kỵ đóng trên Liêm Trinh (KL pp.195-197)
  - Tử Vi không sợ Hỏa, Linh (KL p.75)
  - Thiên Tướng không sợ sát tinh mà còn chế ngự được chúng (KL p.108)
- Cứu giải:
  - Thiên Phủ giảm bớt tính hung hăng của sát tinh (KL p.97)
  - Hóa Khoa là sao cứu giải mạnh nhất (KL p.120)
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)

## 4. A · lá #3 (1/11/1971 15h, nữ) · đường công danh

Kết luận nháp: **nghieng_ve (+)**, độ chắc vua, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_THIEN_KHOI_QUAN_LOC_QUAN_LUNG_LAY | chủ đề danh tiếng (Thiên Khôi, cung Quan Lộc)
  - rule:TV_HS_THIEN_KHOI_QUAN_LOC_QUAN_LUNG_LAY | sự thuận lợi trên đường công danh (Thiên Khôi, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_KHOI_VIET | sự thuận lợi trên đường công danh (Thiên Khôi, Thiên Việt, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_TA_HUU | khả năng kiêm cả văn lẫn võ (Tả Phụ, Hữu Bật, cung Quan Lộc)
  - rule:TV_KL_PHU_CU_NHAT_DAN_THAN | triển vọng về địa vị, công danh (Cự Môn, Thái Dương, cung Mệnh)
  - rule:TV_KL_AUX_TA_HUU | năng lực nổi trội (Hữu Bật, cung Mệnh)
  - rule:TV_KL_CT_DUONG_THU_MENH | triển vọng về địa vị, công danh (Thái Dương, cung Mệnh)
  - rule:TV_KL_STAR_MENH_NHAT_DAN_THIN | triển vọng về địa vị, công danh (Thái Dương, cung Mệnh)
- Khó:
  - rule:TV_TH_AUX_MENH_HKY_VAN_TINH | khoảng cách giữa học vấn và thành tựu (Hóa Kỵ, Văn Xương, Thiên Khôi, Thiên Việt, cung Mệnh)
  - rule:TV_TH_AUX_MENH_HQ_TT | những trở ngại trên đường công danh (Hóa Quyền, cung Mệnh)
  - member:hoa:Văn Xương Hóa Kỵ@Mệnh | Văn Xương hóa Kỵ (Mệnh): Hóa Kỵ từ cung Mệnh làm vướng phần nó chạm tới
  - member:star:Tiểu Hao@Phu Thê | Tiểu Hao (Phu Thê): Tiểu Hao từ cung Phu Thê làm giảm sức
  - member:star:Đại Hao@Quan Lộc | Đại Hao (Quan Lộc): Đại Hao trong cung làm giảm sức
  - member:star:Kình Dương@Tài Bạch | Kình Dương (Tài Bạch): Kình Dương ở cung Tài Bạch chế Thiên Khôi: Khôi Việt sợ Tuần Triệt, Hình Kỵ, Kình Đà, Không Kiếp, Hỏa Linh: công danh trắc trở
- Tương tác:
  - Quan Lộc mượn Thiên Đồng của Phu Thê (KL pp.218, 222)
  - Quan Lộc mượn Thái Âm của Phu Thê (KL pp.218, 222)
  - Hóa Lộc đóng trên Cự Môn (KL pp.195-197)
  - Hóa Quyền đóng trên Thái Dương (KL pp.195-197)
- Cứu giải:
  - Hóa Khoa là sao cứu giải mạnh nhất (KL p.120)

## 5. B · lá #4 (24/10/1931 15h, nữ) · đường công danh

Kết luận nháp: **hai_mat**, độ chắc tam, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_THIEN_KHOI_QUAN_LOC_QUAN_LUNG_LAY | chủ đề danh tiếng (Thiên Khôi, cung Quan Lộc)
  - rule:TV_HS_THIEN_KHOI_QUAN_LOC_QUAN_LUNG_LAY | sự thuận lợi trên đường công danh (Thiên Khôi, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_KHOI_VIET | sự thuận lợi trên đường công danh (Thiên Khôi, Thiên Việt, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_TA_HUU | khả năng kiêm cả văn lẫn võ (Tả Phụ, Hữu Bật, cung Quan Lộc)
  - rule:TV_KL_PHU_CU_NHAT_DAN_THAN | triển vọng về địa vị, công danh (Cự Môn, Thái Dương, cung Mệnh)
  - rule:TV_KL_AUX_TA_HUU | năng lực nổi trội (Hữu Bật, cung Mệnh)
  - rule:TV_KL_CT_DUONG_THU_MENH | triển vọng về địa vị, công danh (Thái Dương, cung Mệnh)
  - rule:TV_KL_STAR_MENH_NHAT_DAN_THIN | triển vọng về địa vị, công danh (Thái Dương, cung Mệnh)
- Khó:
  - rule:TV_TH_AUX_MENH_HKY_VAN_TINH | khoảng cách giữa học vấn và thành tựu (Hóa Kỵ, Văn Xương, Thiên Khôi, Thiên Việt, cung Mệnh)
  - rule:TV_KL7_THIEN_DI_CO_QUA | thế đơn độc, ít người đỡ (Cô Thần, cung Thiên Di)
  - member:hoa:Văn Xương Hóa Kỵ@Mệnh | Văn Xương hóa Kỵ (Mệnh): Hóa Kỵ từ cung Mệnh làm vướng phần nó chạm tới
  - member:star:Tiểu Hao@Phu Thê | Tiểu Hao (Phu Thê): Tiểu Hao từ cung Phu Thê làm giảm sức
  - member:star:Đại Hao@Quan Lộc | Đại Hao (Quan Lộc): Đại Hao trong cung làm giảm sức
  - member:star:Kình Dương@Tài Bạch | Kình Dương (Tài Bạch): Kình Dương ở cung Tài Bạch chế Thiên Khôi: Khôi Việt sợ Tuần Triệt, Hình Kỵ, Kình Đà, Không Kiếp, Hỏa Linh: công danh trắc trở
- Tương tác:
  - Quan Lộc mượn Thiên Đồng của Phu Thê (KL pp.218, 222)
  - Quan Lộc mượn Thái Âm của Phu Thê (KL pp.218, 222)
  - Hóa Lộc đóng trên Cự Môn (KL pp.195-197)
  - Hóa Quyền đóng trên Thái Dương (KL pp.195-197)
- Cứu giải:
  - Hóa Khoa là sao cứu giải mạnh nhất (KL p.120)

## 6. B · lá #5 (17/10/1955 12h, nam) · đường công danh

Kết luận nháp: **hai_mat**, độ chắc tam, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_LIEM_TRINH_QUAN_LOC_QUAN_GOOD | uy thế và khả năng điều khiển người khác (Liêm Trinh, cung Quan Lộc)
  - rule:TV_HS_THIEN_PHUC_QUAN_LOC_QUAN_GIUP_DO | sự hỗ trợ từ người khác (Thiên Phúc, cung Quan Lộc)
  - rule:TV_HS_THIEN_VIET_QUAN_LOC_QUAN_LUNG_LAY | chủ đề danh tiếng (Thiên Việt, cung Quan Lộc)
  - rule:TV_HS_THIEN_VIET_QUAN_LOC_QUAN_LUNG_LAY | sự thuận lợi trên đường công danh (Thiên Việt, cung Quan Lộc)
  - rule:TV_KL_SAO_CUNG_QUAN_LOC_LIEM_QUYEN | uy thế và khả năng điều khiển người khác (Liêm Trinh, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_KHOI_VIET | sự thuận lợi trên đường công danh (Thiên Khôi, Thiên Việt, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_TA_HUU | khả năng kiêm cả văn lẫn võ (Tả Phụ, Hữu Bật, cung Quan Lộc)
  - rule:TV_TT_PAL_QUAN_LOC_LIEM_TRINH_MIEU_P | triển vọng về địa vị, công danh (Liêm Trinh, cung Quan Lộc)
- Khó:
  - rule:TV_HS_THIEN_KHONG_QUAN_LOC_QUAN_CHAM | những trở ngại trên đường công danh (Thiên Không, cung Quan Lộc)
  - rule:TV_TH_COMBO_THIEN_TUONG_TUAN_TRIET | những trở ngại trên đường công danh (Thiên Tướng, cung Mệnh)
  - rule:TV_D3_TT65_TU_VI_THIN_TUAT_PHA | triển vọng về địa vị, công danh (Tử Vi, cung Mệnh)
  - rule:TV_KL_CT_TUONG_TUAN | những trở ngại trên đường công danh (Thiên Tướng, cung Mệnh)
  - rule:TV_KL_STAR_MENH_HOA_LINH_KINH | những trở ngại trên đường công danh (Linh Tinh, Kình Dương, cung Mệnh)
  - rule:TV_KL_STAR_MENH_TV_DE_NGO_HUNG_DO | uy thế và khả năng điều khiển người khác (Tử Vi, Kình Dương, Linh Tinh, cung Mệnh)
  - member:star:Tiểu Hao@Tài Bạch | Tiểu Hao (Tài Bạch): Tiểu Hao từ cung Tài Bạch làm giảm sức
  - member:star:Đà La@Phu Thê | Đà La (Phu Thê): Đà La từ cung Phu Thê làm giảm sức
- Tương tác:
  - Hóa Khoa đóng trên Tử Vi (KL pp.195-197)
  - Thiên Tướng chế ngự Liêm Trinh, canh chừng Phá Quân (KL p.189)
  - Khôi Việt sợ Tuần Triệt, Hình Kỵ, Kình Đà, Không Kiếp, Hỏa Linh: công danh trắc trở (KL p.145)
- Cứu giải:
  - Hóa Khoa là sao cứu giải mạnh nhất (KL p.120)
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 7. B · lá #6 (28/5/1934 15h, nam) · đường công danh

Kết luận nháp: **hai_mat**, độ chắc tam, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_HOA_KHOA_QUAN_LOC_QUAN_TOT | năng lực học thuật, văn chương (Hóa Khoa, cung Quan Lộc)
  - rule:TV_HS_HOA_KHOA_QUAN_LOC_QUAN_TOT | chủ đề danh tiếng (Hóa Khoa, cung Quan Lộc)
  - rule:TV_HS_THIEN_KHOI_QUAN_LOC_QUAN_LUNG_LAY | chủ đề danh tiếng (Thiên Khôi, cung Quan Lộc)
  - rule:TV_HS_THIEN_KHOI_QUAN_LOC_QUAN_LUNG_LAY | sự thuận lợi trên đường công danh (Thiên Khôi, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_KHOI_VIET | sự thuận lợi trên đường công danh (Thiên Khôi, Thiên Việt, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_TA_HUU | khả năng kiêm cả văn lẫn võ (Tả Phụ, Hữu Bật, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_TU_PHU_TAM_HOA | sự thuận lợi trên đường công danh (Tử Vi, Hóa Khoa, Hóa Quyền, Hóa Lộc, cung Quan Lộc)
  - rule:TV_KL_STAR_MENH_QUYEN_LOC | triển vọng về địa vị, công danh (Hóa Quyền, Hóa Lộc, cung Mệnh)
- Khó:
  - rule:TV_KL_AUX_TRUC_TU_PHU | những trở ngại trên đường công danh (Trực Phù, cung Mệnh)
  - rule:TV_TH_AUX_MENH_HQ_TT | những trở ngại trên đường công danh (Hóa Quyền, cung Mệnh)
  - rule:TV_TH_STAR_PHA_QUAN_NAM_HAM | thế đơn độc, ít người đỡ (Phá Quân, cung Mệnh)
  - rule:TV_TT_PHU_MENH_LIEM_MAO_DAU | triển vọng về địa vị, công danh (Liêm Trinh, cung Mệnh)
  - rule:TV_TT_PAL_THIEN_DI_KINH_DUONG_HAM_M | triển vọng về địa vị, công danh (Kình Dương, cung Thiên Di)
  - member:star:Tiểu Hao@Tài Bạch | Tiểu Hao (Tài Bạch): Tiểu Hao từ cung Tài Bạch làm giảm sức
  - member:star:Linh Tinh@Phu Thê | Linh Tinh (Phu Thê): Linh Tinh từ cung Phu Thê làm giảm sức
  - member:star:Địa Kiếp@Phu Thê | Địa Kiếp (Phu Thê): Địa Kiếp từ cung Phu Thê làm giảm sức
- Tương tác:
  - Hóa Lộc đóng trên Liêm Trinh (KL pp.195-197)
  - Hóa Quyền đóng trên Phá Quân (KL pp.195-197)
  - Hóa Khoa đóng trên Vũ Khúc (KL pp.195-197)
  - Thất Sát không sợ Tuần Triệt, không ngán Kình Đà, còn sai khiến được chúng (KL p.114)
- Cứu giải:
  - Hóa Khoa là sao cứu giải mạnh nhất (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 8. A · lá #7 (24/7/1942 20h, nữ) · đường công danh

Kết luận nháp: **nghieng_ve (+)**, độ chắc vua, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_HOA_QUYEN_QUAN_LOC_HQ_QUAN_HOP_VI | uy thế và khả năng điều khiển người khác (Hóa Quyền, cung Quan Lộc)
  - rule:TV_HS_HOA_QUYEN_QUAN_LOC_QUAN_HOP_VI | uy thế và khả năng điều khiển người khác (Hóa Quyền, cung Quan Lộc)
  - rule:TV_HS_PHA_QUAN_QUAN_LOC_QUAN_TY_NGO_TU_VI | sự thuận lợi trên đường công danh (Phá Quân, Tử Vi, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_TA_HUU | khả năng kiêm cả văn lẫn võ (Tả Phụ, Hữu Bật, cung Quan Lộc)
  - rule:TV_TT_PAL_QUAN_LOC_PHA_QUAN_WITH_TU_VI_P | chủ đề danh tiếng (Phá Quân, Tử Vi, cung Quan Lộc)
  - rule:TV_TT_PAL_QUAN_LOC_TU_VI_WITH_PHA_QUAN_P | triển vọng về địa vị, công danh (Tử Vi, Phá Quân, cung Quan Lộc)
  - rule:TV_KL_AUX_TA_HUU | năng lực nổi trội (Tả Phụ, cung Mệnh)
  - rule:TV_KL_CT_SAT_THU_MENH | sự thuận lợi trên đường công danh (Thất Sát, cung Mệnh)
- Khó:
  - rule:TV_HS_DIA_KHONG_QUAN_LOC_QUAN_DEM_PHA | những trở ngại trên đường công danh (Địa Không, cung Quan Lộc)
  - rule:TV_HS_DIA_KHONG_QUAN_LOC_QUAN_THAP_KEM | những trở ngại trên đường công danh (Địa Không, cung Quan Lộc)
  - rule:TV_HS_TU_VI_QUAN_LOC_QUAN_PHA_THAM | những trở ngại trên đường công danh (Tử Vi, Phá Quân, cung Quan Lộc)
  - rule:TV_KL_SAO_CUNG_QUAN_LOC_KHONG_KIEP | những trở ngại trên đường công danh (Địa Không, cung Quan Lộc)
  - rule:TV_TH_AUX2_QUAN_LOC_KK_HAM | những trở ngại trên đường công danh (Địa Không, cung Quan Lộc)
  - rule:TV_TT_PAL_QUAN_LOC_TU_VI_SAT_M | những trở ngại trên đường công danh (Tử Vi, Linh Tinh, Địa Không, Địa Kiếp, cung Quan Lộc)
  - rule:TV_KL_CT_HONG_DON_THU | những trở ngại trên đường công danh (Hồng Loan, cung Mệnh)
  - rule:TV_TH_AUX_MENH_HKY_VAN_TINH | khoảng cách giữa học vấn và thành tựu (Hóa Kỵ, Thiên Khôi, Thiên Việt, cung Mệnh)
- Tương tác:
  - Hóa Quyền đóng trên Tử Vi (KL pp.195-197)
  - Hóa Khoa đóng trên Tả Phụ (KL pp.195-197)
  - Hóa Kỵ đóng trên Vũ Khúc (KL pp.195-197)
  - Tử Vi không sợ Hỏa, Linh (KL p.75)
- Cứu giải:
  - Kình, Đà, Không, Kiếp, Tuần, Triệt biến Tử Vi thành kẻ côi cút, mất sức cứu giải (KL p.75)
  - Hóa Khoa là sao cứu giải mạnh nhất (KL p.120)
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)

## 9. B · lá #8 (27/6/1949 3h, nữ) · đường công danh

Kết luận nháp: **nghieng_ve (-)**, độ chắc vua, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_TA_PHU_QUAN_LOC_QUAN_PHO_TA | sự hỗ trợ từ người khác (Tả Phụ, cung Quan Lộc)
  - rule:TV_HS_TA_PHU_QUAN_LOC_QUAN_PHO_TA | sự thuận lợi trên đường công danh (Tả Phụ, cung Quan Lộc)
  - rule:TV_HS_THAT_SAT_QUAN_LOC_QUAN_VU_HIEN | sự thuận lợi trên đường công danh (Thất Sát, Vũ Khúc, cung Quan Lộc)
  - rule:TV_HS_THIEN_QUAN_QUAN_LOC_QUAN_GIUP_DO | sự hỗ trợ từ người khác (Thiên Quan, cung Quan Lộc)
  - rule:TV_HS_VU_KHUC_QUAN_LOC_QUAN_SAT_VO | triển vọng về địa vị, công danh (Vũ Khúc, Thất Sát, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_TA_HUU | khả năng kiêm cả văn lẫn võ (Tả Phụ, Hữu Bật, cung Quan Lộc)
  - rule:TV_TT_PAL_QUAN_LOC_THAT_SAT_WITH_VU_KHUC_P | triển vọng về địa vị, công danh (Thất Sát, Vũ Khúc, cung Quan Lộc)
  - rule:TV_TT_PAL_QUAN_LOC_VU_KHUC_WITH_THAT_SAT_P | sự thuận lợi trên đường công danh (Vũ Khúc, Thất Sát, cung Quan Lộc)
- Khó:
  - rule:TV_HS_DIA_KHONG_QUAN_LOC_QUAN_DEM_PHA | những trở ngại trên đường công danh (Địa Không, cung Quan Lộc)
  - rule:TV_HS_DIA_KHONG_QUAN_LOC_QUAN_THAP_KEM | những trở ngại trên đường công danh (Địa Không, cung Quan Lộc)
  - rule:TV_HS_THAT_SAT_QUAN_LOC_QUAN_VU_THANG_TRAM | đường công danh lúc lên lúc xuống (Thất Sát, Vũ Khúc, cung Quan Lộc)
  - rule:TV_HS_TRIET_QUAN_LOC_QUAN_LAN_DAN | những trở ngại trên đường công danh (Quan Lộc, cung Quan Lộc)
  - rule:TV_HS_VU_KHUC_QUAN_LOC_QUAN_SAT_THANGGIANG | những trở ngại trên đường công danh (Vũ Khúc, Thất Sát, cung Quan Lộc)
  - rule:TV_KL_SAO_CUNG_QUAN_LOC_KHONG_KIEP | những trở ngại trên đường công danh (Địa Không, cung Quan Lộc)
  - rule:TV_TH_AUX2_QUAN_LOC_KK_HAM | những trở ngại trên đường công danh (Địa Không, cung Quan Lộc)
  - member:star:Địa Kiếp@Tài Bạch | Địa Kiếp (Tài Bạch): Địa Kiếp từ cung Tài Bạch làm giảm sức
- Tương tác:
  - Hóa Lộc đóng trên Vũ Khúc (KL pp.195-197)
  - Hóa Quyền đóng trên Tham Lang (KL pp.195-197)
  - Tuần, Triệt là sao cản phá: giảm cả cái tốt lẫn cái xấu của các sao (KL p.203)
  - Thiên Phủ không sợ Triệt (KL p.96)
- Cứu giải:
  - Thiên Phủ giảm bớt tính hung hăng của sát tinh (KL p.97)
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 10. B · lá #9 (9/7/1937 8h, nam) · đường công danh

Kết luận nháp: **hai_mat**, độ chắc tam, tầm menh_tai_quan

- Thuận:
  - rule:TV_KL_PHU2_CO_DAC_DIA | năng lực nổi trội (Thiên Cơ, cung Mệnh)
  - rule:TV_TH_COMBO_THIEN_CO_CAT | uy thế và khả năng điều khiển người khác (Thiên Cơ, Thiên Khôi, Thiên Việt, Tả Phụ, Hóa Khoa, Hóa Quyền, cung Mệnh)
  - rule:TV_KL_CT_CNDL | năng lực học thuật, văn chương (Mệnh, cung Mệnh)
  - rule:TV_KL_STAR_MENH_CO_CAT_TINH | chủ đề danh tiếng (Thiên Cơ, Tả Phụ, Thiên Khôi, Thiên Việt, cung Mệnh)
  - rule:TV_KL_STAR_MENH_CO_MAO_DAU | năng lực nổi trội (Thiên Cơ, cung Mệnh)
  - rule:TV_TH_MV_MENH_CO_MIEU_VUONG | triển vọng về địa vị, công danh (Thiên Cơ, cung Mệnh)
  - rule:TV_TH_STAR_THIEN_CO_NAM_HAO | khả năng kiêm cả văn lẫn võ (Thiên Cơ, Đại Hao, Tiểu Hao, cung Mệnh)
  - rule:TV_TT_MENH_KHOA_MENH_QUYEN_CHIEU | năng lực học thuật, văn chương (Hóa Khoa, Hóa Quyền, cung Mệnh)
- Khó:
  - rule:TV_HS_DIA_KHONG_QUAN_LOC_QUAN_DEM_PHA | những trở ngại trên đường công danh (Địa Không, cung Quan Lộc)
  - rule:TV_HS_DIA_KHONG_QUAN_LOC_QUAN_THAP_KEM | những trở ngại trên đường công danh (Địa Không, cung Quan Lộc)
  - rule:TV_KL_SAO_CUNG_QUAN_LOC_KHONG_KIEP | những trở ngại trên đường công danh (Địa Không, cung Quan Lộc)
  - rule:TV_TH_AUX2_QUAN_LOC_KK_HAM | những trở ngại trên đường công danh (Địa Không, cung Quan Lộc)
  - rule:TV_KL_CT_CAP_DOI_BAC_TRUNG | triển vọng về địa vị, công danh (Cự Môn, Thiên Cơ, cung Mệnh)
  - rule:TV_TH_AUX_MENH_HKY_VAN_TINH | khoảng cách giữa học vấn và thành tựu (Hóa Kỵ, Thiên Khôi, Thiên Việt, cung Mệnh)
  - member:hoa:Cự Môn Hóa Kỵ@Mệnh | Cự Môn hóa Kỵ (Mệnh): Hóa Kỵ từ cung Mệnh làm vướng phần nó chạm tới
  - member:star:Tiểu Hao@Mệnh | Tiểu Hao (Mệnh): Tiểu Hao từ cung Mệnh làm giảm sức
- Tương tác:
  - Quan Lộc mượn Thái Dương của Phu Thê (KL pp.218, 222)
  - Quan Lộc mượn Thái Âm của Phu Thê (KL pp.218, 222)
  - Hóa Lộc đóng trên Thái Âm (KL pp.195-197)
  - Hóa Quyền đóng trên Thiên Đồng (KL pp.195-197)
- Cứu giải:
  - Hóa Khoa là sao cứu giải mạnh nhất (KL p.120)
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 11. A · lá #10 (15/12/1948 23h, nam) · đường công danh

Kết luận nháp: **nghieng_ve (+)**, độ chắc vua, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_THIEN_LUONG_QUAN_LOC_QUAN_VAN | năng lực học thuật, văn chương (Thiên Lương, cung Quan Lộc)
  - rule:TV_TT_PAL_QUAN_LOC_VAN_KHUC_MIEU_P | khả năng kiêm cả văn lẫn võ (Văn Khúc, cung Quan Lộc)
  - rule:TV_D3_TT67_DONG_MIEU_VUONG | chủ đề danh tiếng (Thiên Đồng, cung Mệnh)
  - rule:TV_D3_TT68_AM_MIEU_QUYEN | triển vọng về địa vị, công danh (Thái Âm, Hóa Quyền, cung Mệnh)
  - rule:TV_KL_AUX_TA_HUU | năng lực nổi trội (Hữu Bật, cung Mệnh)
  - rule:TV_KL_CT_CNDL | năng lực học thuật, văn chương (Mệnh, cung Mệnh)
  - rule:TV_TH_AUX2_MENH_TUE_VAN_TINH | năng lực học thuật, văn chương (Thái Tuế, Văn Khúc, cung Mệnh)
  - rule:TV_TH_AUX2_MENH_TUE_VAN_TINH | sự thuận lợi trên đường công danh (Thái Tuế, Văn Khúc, cung Mệnh)
- Khó:
  - rule:TV_HS_HOA_KY_QUAN_LOC_QUAN_CHAM_THANG | những trở ngại trên đường công danh (Hóa Kỵ, cung Quan Lộc)
  - rule:TV_HS_HOA_KY_QUAN_LOC_QUAN_DEM_PHA | những trở ngại trên đường công danh (Hóa Kỵ, cung Quan Lộc)
  - rule:TV_KL_CT_CAP_DOI_BAC_TRUNG | triển vọng về địa vị, công danh (Thiên Đồng, Thái Âm, cung Mệnh)
  - rule:TV_TH_AUX2_MENH_TUE_KY_DA | những trở ngại trên đường công danh (Thái Tuế, Hóa Kỵ, Đà La, cung Mệnh)
  - rule:TV_TH_AUX_MENH_HQ_TT | những trở ngại trên đường công danh (Hóa Quyền, cung Mệnh)
  - rule:TV_TT_PAL_THIEN_DI_KINH_DUONG_HAM_M | triển vọng về địa vị, công danh (Kình Dương, cung Thiên Di)
  - member:hoa:Thiên Cơ Hóa Kỵ@Quan Lộc | Thiên Cơ hóa Kỵ (Quan Lộc): Hóa Kỵ ngay trong cung làm vướng phần nó chạm tới
  - member:star:Tiểu Hao@Tài Bạch | Tiểu Hao (Tài Bạch): Tiểu Hao từ cung Tài Bạch làm giảm sức
- Tương tác:
  - Hóa Quyền đóng trên Thái Âm (KL pp.195-197)
  - Hóa Khoa đóng trên Hữu Bật (KL pp.195-197)
  - Hóa Kỵ đóng trên Thiên Cơ (KL pp.195-197)
  - Thiên Lương sợ Tuần, Triệt, Hỏa, Linh (KL p.111)
- Cứu giải:
  - Hóa Khoa là sao cứu giải mạnh nhất (KL p.120)

## 12. A · lá #11 (10/11/2021 11h, nữ) · đường công danh

Kết luận nháp: **thuan (+)**, độ chắc ro, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_THIEN_QUAN_QUAN_LOC_QUAN_GIUP_DO | sự hỗ trợ từ người khác (Thiên Quan, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_TA_HUU | khả năng kiêm cả văn lẫn võ (Tả Phụ, Hữu Bật, cung Quan Lộc)
  - rule:TV_TT_PAL_QUAN_LOC_LOC_TON_BASE_P | khả năng kiêm cả văn lẫn võ (Lộc Tồn, cung Quan Lộc)
  - rule:TV_KL_PHU2_KHONG_KIEP_TY_HOI | sự thuận lợi trên đường công danh (Địa Không, Địa Kiếp, cung Mệnh)
  - rule:TV_KL_CT_CNDL | năng lực học thuật, văn chương (Mệnh, cung Mệnh)
  - rule:TV_KL_CT_NHAT_NGUYET_CHIEU | năng lực nổi trội (Thái Dương, Thái Âm, cung Mệnh)
  - rule:TV_KL_CT_NHAT_NGUYET_CHIEU | sự thuận lợi trên đường công danh (Thái Dương, Thái Âm, cung Mệnh)
  - rule:TV_TH_MV_MENH_KK_TY_HOI | triển vọng về địa vị, công danh (Địa Không, Địa Kiếp, cung Mệnh)
- Khó:
  - member:star:Thiên Lương@Mệnh | Thiên Lương (Mệnh): Thiên Lương hãm ở cung Mệnh hội về
- Tương tác:
  - Quan Lộc mượn Thiên Cơ của Phu Thê (KL pp.218, 222)
  - Quan Lộc mượn Cự Môn của Phu Thê (KL pp.218, 222)
  - Hóa Lộc đóng trên Cự Môn (KL pp.195-197)
  - Hóa Quyền đóng trên Thái Dương (KL pp.195-197)
- Cứu giải:
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 13. B · lá #12 (9/3/1989 15h, nam) · đường công danh

Kết luận nháp: **hai_mat**, độ chắc tam, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_THAT_SAT_QUAN_LOC_QUAN_DEP | uy thế và khả năng điều khiển người khác (Thất Sát, Tử Vi, cung Quan Lộc)
  - rule:TV_HS_THAT_SAT_QUAN_LOC_QUAN_DEP | khả năng kiêm cả văn lẫn võ (Thất Sát, Tử Vi, cung Quan Lộc)
  - rule:TV_KL_SAO_CUNG_QUAN_LOC_SAT_TRIEU | uy thế và khả năng điều khiển người khác (Thất Sát, Tử Vi, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_SAT_MIEU | uy thế và khả năng điều khiển người khác (Thất Sát, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_SAT_MIEU | triển vọng về địa vị, công danh (Thất Sát, cung Quan Lộc)
  - rule:TV_KL_PHU_THAM_HOA_LINH_TU_MO | uy thế và khả năng điều khiển người khác (Tham Lang, Hỏa Tinh, cung Mệnh)
  - rule:TV_KL_PHU_VU_DAC_DIA | uy thế và khả năng điều khiển người khác (Vũ Khúc, cung Mệnh)
  - rule:TV_KL_PHU_VU_DAC_DIA | chủ đề danh tiếng (Vũ Khúc, cung Mệnh)
- Khó:
  - rule:TV_HS_TUAN_QUAN_LOC_QUAN_LAN_DAN | những trở ngại trên đường công danh (Quan Lộc, cung Quan Lộc)
  - rule:TV_TT_PAL_QUAN_LOC_TU_VI_SAT_M | những trở ngại trên đường công danh (Tử Vi, Kình Dương, Đà La, Hỏa Tinh, Địa Không, Địa Kiếp, cung Quan Lộc)
  - rule:TV_KL_CT_CAP_DOI_BAC_TRUNG | triển vọng về địa vị, công danh (Tham Lang, Vũ Khúc, cung Mệnh)
  - rule:TV_KL_STAR_MENH_HOA_LINH_KINH | những trở ngại trên đường công danh (Hỏa Tinh, Kình Dương, cung Mệnh)
  - rule:TV_TH_AUX2_MENH_KK_QUYEN | những trở ngại trên đường công danh (Địa Kiếp, Hóa Quyền, cung Mệnh)
  - member:star:Tiểu Hao@Tài Bạch | Tiểu Hao (Tài Bạch): Tiểu Hao từ cung Tài Bạch làm giảm sức
  - member:star:Địa Không@Tài Bạch | Địa Không (Tài Bạch): Địa Không từ cung Tài Bạch làm giảm sức
  - member:star:Đà La@Phu Thê | Đà La (Phu Thê): Đà La từ cung Phu Thê làm giảm sức
- Tương tác:
  - Hóa Lộc đóng trên Vũ Khúc (KL pp.195-197)
  - Hóa Quyền đóng trên Tham Lang (KL pp.195-197)
  - Tuần, Triệt là sao cản phá: giảm cả cái tốt lẫn cái xấu của các sao (KL p.203)
  - chính tinh đắc địa gặp Tuần, Triệt thì như hãm địa, bị phá hư (KL p.203)

## 14. B · lá #13 (19/3/1957 15h, nam) · đường công danh

Kết luận nháp: **chua_phan_xu**, độ chắc tam, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_THIEN_KHOI_QUAN_LOC_QUAN_LUNG_LAY | chủ đề danh tiếng (Thiên Khôi, cung Quan Lộc)
  - rule:TV_HS_THIEN_KHOI_QUAN_LOC_QUAN_LUNG_LAY | sự thuận lợi trên đường công danh (Thiên Khôi, cung Quan Lộc)
  - rule:TV_HS_THIEN_LUONG_QUAN_LOC_QUAN_VAN | năng lực học thuật, văn chương (Thiên Lương, cung Quan Lộc)
  - rule:TV_HS_THIEN_PHUC_QUAN_LOC_QUAN_GIUP_DO | sự hỗ trợ từ người khác (Thiên Phúc, cung Quan Lộc)
  - rule:TV_KL_CT_CNDL | năng lực học thuật, văn chương (Mệnh, cung Mệnh)
  - rule:TV_KL_CT_DUONG_THU_MENH | triển vọng về địa vị, công danh (Thái Dương, cung Mệnh)
  - rule:TV_KL_STAR_MENH_MINH_AM_LOC | triển vọng về địa vị, công danh (Hóa Lộc, Lộc Tồn, cung Mệnh)
  - rule:TV_TH_AUX2_MENH_KINH_HOA_TU_MO | uy thế và khả năng điều khiển người khác (Kình Dương, Hỏa Tinh, cung Mệnh)
- Khó:
  - rule:TV_HS_THIEN_LUONG_QUAN_LOC_QUAN_TYHOI | những trở ngại trên đường công danh (Thiên Lương, cung Quan Lộc)
  - rule:TV_KL_CT_CAP_DOI_BAC_TRUNG | triển vọng về địa vị, công danh (Thái Dương, Thái Âm, cung Mệnh)
  - rule:TV_KL_CT_NHAT_NGUYET_DONG_CUNG | triển vọng về địa vị, công danh (Thái Dương, Thái Âm, cung Mệnh)
  - rule:TV_KL_STAR_MENH_HOA_LINH_KINH | những trở ngại trên đường công danh (Hỏa Tinh, Kình Dương, cung Mệnh)
  - rule:TV_TH_MV_MENH_NN_SUU_MUI_SAT | những trở ngại trên đường công danh (Thái Dương, Thái Âm, Địa Không, Địa Kiếp, cung Mệnh)
  - member:star:Tiểu Hao@Tài Bạch | Tiểu Hao (Tài Bạch): Tiểu Hao từ cung Tài Bạch làm giảm sức
  - member:star:Địa Không@Tài Bạch | Địa Không (Tài Bạch): Địa Không từ cung Tài Bạch làm giảm sức
  - member:star:Đà La@Phu Thê | Đà La (Phu Thê): Đà La từ cung Phu Thê làm giảm sức
- Tương tác:
  - Hóa Lộc đóng trên Thái Âm (KL pp.195-197)
  - Hóa Quyền đóng trên Thiên Đồng (KL pp.195-197)
  - Khôi Việt sợ Tuần Triệt, Hình Kỵ, Kình Đà, Không Kiếp, Hỏa Linh: công danh trắc trở (KL p.145)
- Cứu giải:
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 15. B · lá #14 (2/12/1961 12h, nam) · đường công danh

Kết luận nháp: **nghieng_ve (-)**, độ chắc vua, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_THAT_SAT_QUAN_LOC_QUAN_VU_HIEN | sự thuận lợi trên đường công danh (Thất Sát, Vũ Khúc, cung Quan Lộc)
  - rule:TV_HS_THIEN_QUAN_QUAN_LOC_QUAN_GIUP_DO | sự hỗ trợ từ người khác (Thiên Quan, cung Quan Lộc)
  - rule:TV_HS_VU_KHUC_QUAN_LOC_QUAN_SAT_VO | triển vọng về địa vị, công danh (Vũ Khúc, Thất Sát, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_TA_HUU | khả năng kiêm cả văn lẫn võ (Tả Phụ, Hữu Bật, cung Quan Lộc)
  - rule:TV_TT_PAL_QUAN_LOC_LOC_TON_BASE_P | khả năng kiêm cả văn lẫn võ (Lộc Tồn, cung Quan Lộc)
  - rule:TV_TT_PAL_QUAN_LOC_THAT_SAT_WITH_VU_KHUC_P | triển vọng về địa vị, công danh (Thất Sát, Vũ Khúc, cung Quan Lộc)
  - rule:TV_TT_PAL_QUAN_LOC_VU_KHUC_WITH_THAT_SAT_P | sự thuận lợi trên đường công danh (Vũ Khúc, Thất Sát, cung Quan Lộc)
  - rule:TV_KL_PHU2_KHONG_KIEP_TY_HOI | sự thuận lợi trên đường công danh (Địa Không, Địa Kiếp, cung Mệnh)
- Khó:
  - rule:TV_HS_THAT_SAT_QUAN_LOC_QUAN_VU_THANG_TRAM | đường công danh lúc lên lúc xuống (Thất Sát, Vũ Khúc, cung Quan Lộc)
  - rule:TV_HS_VU_KHUC_QUAN_LOC_QUAN_SAT_THANGGIANG | những trở ngại trên đường công danh (Vũ Khúc, Thất Sát, cung Quan Lộc)
  - rule:TV_TH_AUX2_MENH_TUONG_TT | những trở ngại trên đường công danh (Tướng Quân, cung Mệnh)
  - member:star:Liêm Trinh@Mệnh | Liêm Trinh (Mệnh): Liêm Trinh hãm ở cung Mệnh hội về
  - member:star:Tham Lang@Mệnh | Tham Lang (Mệnh): Tham Lang hãm ở cung Mệnh hội về
- Tương tác:
  - Tử Vi không sợ Hỏa, Linh (KL p.75)
  - Tham Lang giải trừ ác tính của Hỏa Linh (KL p.190)
  - Hỏa Linh không đánh được Tử Vi, Thiên Phủ, Thái Dương (KL p.200)
  - gặp sao giải mạnh thì hung sát tinh bị hóa giải, thành ra ngộ chế (KL p.200)
- Cứu giải:
  - Thiên Phủ giảm bớt tính hung hăng của sát tinh (KL p.97)
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 16. B · lá #15 (24/11/1966 10h, nam) · đường công danh

Kết luận nháp: **hai_mat**, độ chắc tam, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_AN_QUANG_QUAN_LOC_QUAN_MAY_MAN | sự thuận lợi trên đường công danh (Thiên Quý, cung Quan Lộc)
  - rule:TV_HS_AN_QUANG_QUAN_LOC_QUAN_NANG_DO | sự hỗ trợ từ người khác (Thiên Quý, cung Quan Lộc)
  - rule:TV_HS_VU_KHUC_QUAN_LOC_QUAN_DAC | triển vọng về địa vị, công danh (Vũ Khúc, cung Quan Lộc)
  - rule:TV_D3_TT69_TUONG_VU_PHA_SAT | năng khiếu chuyên môn, kỹ thuật (Thiên Tướng, Vũ Khúc, Phá Quân, Kình Dương, Hỏa Tinh, Linh Tinh, cung Mệnh)
  - rule:TV_TH_AUX2_MENH_KINH_LUC_SI | năng lực nổi trội (Kình Dương, Lực Sĩ, cung Mệnh)
  - rule:TV_TH_STAR_THIEN_TUONG_NAM_MV | uy thế và khả năng điều khiển người khác (Thiên Tướng, cung Mệnh)
  - rule:TV_TH_STAR_THIEN_TUONG_NAM_MV | chủ đề danh tiếng (Thiên Tướng, cung Mệnh)
  - member:star:Vũ Khúc@Quan Lộc | Vũ Khúc (Quan Lộc): Vũ Khúc là sao chủ của cung
- Khó:
  - rule:TV_HS_SUY_QUAN_LOC_QUAN_THAP | triển vọng về địa vị, công danh (Suy, cung Quan Lộc)
  - rule:TV_KL_STAR_MENH_HOA_LINH_KINH | những trở ngại trên đường công danh (Hỏa Tinh, Kình Dương, cung Mệnh)
  - rule:TV_KL_STAR_MENH_KINH_LUC_SI | chủ đề danh tiếng (Kình Dương, Lực Sĩ, cung Mệnh)
  - rule:TV_TH_AUX2_MENH_TUE_KY_DA | những trở ngại trên đường công danh (Thái Tuế, Hóa Kỵ, cung Mệnh)
  - member:hoa:Liêm Trinh Hóa Kỵ@Mệnh | Liêm Trinh hóa Kỵ (Mệnh): Hóa Kỵ từ cung Mệnh làm vướng phần nó chạm tới
  - member:star:Đại Hao@Tài Bạch | Đại Hao (Tài Bạch): Đại Hao từ cung Tài Bạch làm giảm sức
  - member:star:Địa Kiếp@Phu Thê | Địa Kiếp (Phu Thê): Địa Kiếp từ cung Phu Thê làm giảm sức
  - member:star:Kình Dương@Mệnh | Kình Dương (Mệnh): Kình Dương từ cung Mệnh làm giảm sức
- Tương tác:
  - Hóa Kỵ đóng trên Liêm Trinh (KL pp.195-197)
  - Tử Vi không sợ Hỏa, Linh (KL p.75)
  - Thiên Tướng không sợ sát tinh mà còn chế ngự được chúng (KL p.108)
  - Vũ Khúc đắc địa là khắc của các sát tinh (KL p.187)
- Cứu giải:
  - Thiên Phủ giảm bớt tính hung hăng của sát tinh (KL p.97)
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)

## 17. B · lá #16 (28/11/1955 14h, nữ) · đường công danh

Kết luận nháp: **hai_mat**, độ chắc tam, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_LIEM_TRINH_QUAN_LOC_QUAN_GOOD | uy thế và khả năng điều khiển người khác (Liêm Trinh, cung Quan Lộc)
  - rule:TV_HS_THIEN_PHUC_QUAN_LOC_QUAN_GIUP_DO | sự hỗ trợ từ người khác (Thiên Phúc, cung Quan Lộc)
  - rule:TV_HS_THIEN_VIET_QUAN_LOC_QUAN_LUNG_LAY | chủ đề danh tiếng (Thiên Việt, cung Quan Lộc)
  - rule:TV_HS_THIEN_VIET_QUAN_LOC_QUAN_LUNG_LAY | sự thuận lợi trên đường công danh (Thiên Việt, cung Quan Lộc)
  - rule:TV_KL_SAO_CUNG_QUAN_LOC_LIEM_QUYEN | uy thế và khả năng điều khiển người khác (Liêm Trinh, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_KHOI_VIET | sự thuận lợi trên đường công danh (Thiên Khôi, Thiên Việt, cung Quan Lộc)
  - rule:TV_TT_PAL_QUAN_LOC_LIEM_TRINH_MIEU_P | triển vọng về địa vị, công danh (Liêm Trinh, cung Quan Lộc)
  - rule:TV_KL_PHU_TU_TUONG_THIN_TUAT | triển vọng về địa vị, công danh (Tử Vi, Thiên Tướng, cung Mệnh)
- Khó:
  - rule:TV_HS_THIEN_KHONG_QUAN_LOC_QUAN_CHAM | những trở ngại trên đường công danh (Thiên Không, cung Quan Lộc)
  - rule:TV_KL_PHU_TU_VI_KHONG_TA_HUU | thế đơn độc, ít người đỡ (Tử Vi, cung Mệnh)
  - rule:TV_TH_COMBO_THIEN_TUONG_TUAN_TRIET | những trở ngại trên đường công danh (Thiên Tướng, cung Mệnh)
  - rule:TV_TH_COMBO_TU_VI_KIEP_KHONG | những trở ngại trên đường công danh (Tử Vi, Địa Không, cung Mệnh)
  - rule:TV_KL_CT_TUONG_TUAN | những trở ngại trên đường công danh (Thiên Tướng, cung Mệnh)
  - rule:TV_KL_STAR_MENH_HOA_LINH_KINH | những trở ngại trên đường công danh (Hỏa Tinh, Kình Dương, cung Mệnh)
  - rule:TV_KL_STAR_MENH_KINH_LUC_SI | chủ đề danh tiếng (Kình Dương, Lực Sĩ, cung Mệnh)
  - rule:TV_KL_STAR_MENH_TV_DE_NGO_HUNG_DO | uy thế và khả năng điều khiển người khác (Tử Vi, Kình Dương, Địa Không, Hỏa Tinh, cung Mệnh)
- Tương tác:
  - Hóa Khoa đóng trên Tử Vi (KL pp.195-197)
  - Thiên Tướng chế ngự Liêm Trinh, canh chừng Phá Quân (KL p.189)
  - Khôi Việt sợ Tuần Triệt, Hình Kỵ, Kình Đà, Không Kiếp, Hỏa Linh: công danh trắc trở (KL p.145)
- Cứu giải:
  - Hóa Khoa là sao cứu giải mạnh nhất (KL p.120)
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 18. A · lá #17 (5/11/2021 15h, nam) · đường công danh

Kết luận nháp: **nghieng_ve (+)**, độ chắc vua, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_DE_VUONG_QUAN_LOC_QUAN_QUYEN | uy thế và khả năng điều khiển người khác (Đế Vượng, Hóa Quyền, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_TA_HUU | khả năng kiêm cả văn lẫn võ (Tả Phụ, Hữu Bật, cung Quan Lộc)
  - rule:TV_KL_PHU2_CO_DAC_DIA | năng lực nổi trội (Thiên Cơ, cung Mệnh)
  - rule:TV_KL_PHU_CU_CO_MAO_DAU | triển vọng về địa vị, công danh (Cự Môn, Thiên Cơ, cung Mệnh)
  - rule:TV_TH_COMBO_THIEN_CO_CAT | uy thế và khả năng điều khiển người khác (Thiên Cơ, Hóa Lộc, cung Mệnh)
  - rule:TV_KL_CT_CNDL | năng lực học thuật, văn chương (Mệnh, cung Mệnh)
  - rule:TV_KL_STAR_MENH_CO_CU_MAO | năng lực nổi trội (Thiên Cơ, Cự Môn, cung Mệnh)
  - rule:TV_KL_STAR_MENH_CO_CU_MAO | sự thuận lợi trên đường công danh (Thiên Cơ, Cự Môn, cung Mệnh)
- Khó:
  - rule:TV_HS_DIA_KHONG_QUAN_LOC_QUAN_DEM_PHA | những trở ngại trên đường công danh (Địa Kiếp, cung Quan Lộc)
  - rule:TV_HS_DIA_KHONG_QUAN_LOC_QUAN_THAP_KEM | những trở ngại trên đường công danh (Địa Kiếp, cung Quan Lộc)
  - rule:TV_KL_SAO_CUNG_QUAN_LOC_KHONG_KIEP | những trở ngại trên đường công danh (Địa Kiếp, cung Quan Lộc)
  - rule:TV_TH_AUX2_QUAN_LOC_KK_HAM | những trở ngại trên đường công danh (Địa Kiếp, cung Quan Lộc)
  - rule:TV_KL_CT_CAP_DOI_BAC_TRUNG | triển vọng về địa vị, công danh (Cự Môn, Thiên Cơ, cung Mệnh)
  - member:star:Địa Không@Mệnh | Địa Không (Mệnh): Địa Không từ cung Mệnh làm giảm sức
  - member:star:Hỏa Tinh@Quan Lộc | Hỏa Tinh (Quan Lộc): Hỏa Tinh trong cung làm giảm sức
  - member:star:Địa Kiếp@Quan Lộc | Địa Kiếp (Quan Lộc): Địa Kiếp trong cung làm giảm sức
- Tương tác:
  - Quan Lộc mượn Thái Dương của Phu Thê (KL pp.218, 222)
  - Quan Lộc mượn Thái Âm của Phu Thê (KL pp.218, 222)
  - Hóa Lộc đóng trên Cự Môn (KL pp.195-197)
  - Hóa Quyền đóng trên Thái Dương (KL pp.195-197)

## 19. C · lá #18 (23/11/2020 3h, nữ) · hôn nhân

Kết luận nháp: **tro_ngai (-)**, độ chắc ro, tầm tam_phuong, có câu nặng

- Thuận:
  - member:star:Vũ Khúc@Quan Lộc | Vũ Khúc (Quan Lộc): cung Phu Thê vô chính diệu nên mượn Vũ Khúc từ cung Quan Lộc làm sao chủ
  - member:star:Tham Lang@Quan Lộc | Tham Lang (Quan Lộc): cung Phu Thê vô chính diệu nên mượn Tham Lang từ cung Quan Lộc làm sao chủ
  - member:hoa:Vũ Khúc Hóa Quyền@Quan Lộc | Vũ Khúc hóa Quyền (Quan Lộc): Quyền là địa vị, quyền
  - member:star:Tả Phụ@Quan Lộc | Tả Phụ (Quan Lộc): Tả Phụ từ cung Quan Lộc thêm trợ lực
  - member:star:Hữu Bật@Quan Lộc | Hữu Bật (Quan Lộc): Hữu Bật từ cung Quan Lộc thêm trợ lực
  - member:star:Thiên Phủ@Phúc Đức | Thiên Phủ (Phúc Đức): Thiên Phủ sáng ở cung Phúc Đức hội về
- Khó:
  - rule:TV_HS_TRIET_PHU_THE_PHU_TRAC_TRO | những trắc trở trong chuyện gắn bó (Phu Thê, cung Phu Thê)
  - rule:TV_KL_CUNG_PHU_THE_KINH_DA_KHONG_KIEP | những trắc trở trong chuyện gắn bó (Đà La, cung Phu Thê)
  - rule:TV_PB_TT_PHU_THE_TT_PHU_THE_DA_LA_NU | những trắc trở trong chuyện gắn bó (Đà La, cung Phu Thê)
  - rule:TV_TH_AUX2_MENH_KK_DAO_HONG | những trắc trở trong chuyện gắn bó (Địa Không, Đào Hoa, Hồng Loan, cung Mệnh)
  - member:star:Địa Kiếp@Quan Lộc | Địa Kiếp (Quan Lộc): Địa Kiếp từ cung Quan Lộc làm giảm sức
  - member:star:Đại Hao@Phúc Đức | Đại Hao (Phúc Đức): Đại Hao từ cung Phúc Đức làm giảm sức
  - member:star:Thiên Tướng@Thiên Di | Thiên Tướng (Thiên Di): Thiên Tướng hãm ở cung Thiên Di hội về
  - member:tt:Triệt@Phu Thê | Triệt (Phu Thê): Triệt án ngữ: giảm cả cái tốt lẫn cái xấu
- Tương tác:
  - Phu Thê mượn Vũ Khúc của Quan Lộc (KL pp.218, 222)
  - Phu Thê mượn Tham Lang của Quan Lộc (KL pp.218, 222)
  - Hóa Quyền đóng trên Vũ Khúc (KL pp.195-197)
  - Tuần, Triệt là sao cản phá: giảm cả cái tốt lẫn cái xấu của các sao (KL p.203)
- Cứu giải:
  - Thiên Phủ giảm bớt tính hung hăng của sát tinh (KL p.97)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 20. A · lá #19 (7/9/2021 8h, nữ) · khả năng kiếm tiền

Kết luận nháp: **nghieng_ve (+)**, độ chắc vua, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_PHA_QUAN_TAI_BACH_TAI_TU_VU | khuynh hướng tài lộc thuận lợi (Phá Quân, Tử Vi, cung Tài Bạch)
  - rule:TV_TT_PAL_TAI_BACH_TU_VI_BASE_P | khuynh hướng tài lộc thuận lợi (Tử Vi, cung Tài Bạch)
  - rule:TV_TT_PAL_QUAN_LOC_LOC_TON_BASE_P | khuynh hướng tài lộc thuận lợi (Lộc Tồn, cung Quan Lộc)
  - member:star:Tử Vi@Tài Bạch | Tử Vi (Tài Bạch): Tử Vi là sao chủ của cung
  - member:star:Phá Quân@Tài Bạch | Phá Quân (Tài Bạch): Phá Quân là sao chủ của cung
  - member:star:Lộc Tồn@Quan Lộc | Lộc Tồn (Quan Lộc): Lộc Tồn từ cung Quan Lộc thêm trợ lực
  - member:star:Thiên Tướng@Phúc Đức | Thiên Tướng (Phúc Đức): Thiên Tướng sáng ở cung Phúc Đức hội về
- Khó:
  - rule:TV_KL_CASE_TAI_BACH_THAN | những giới hạn về tài chính (Tài Bạch, cung Tài Bạch)
  - rule:TV_TT_PAL_TAI_BACH_TU_VI_SAT_M | khuynh hướng tài lộc thuận lợi (Tử Vi, Hỏa Tinh, Địa Không, cung Tài Bạch)
  - rule:TV_KL_PHU2_BA_KHONG | những giới hạn về tài chính (Mệnh, cung Mệnh)
  - rule:TV_KL_STAR_PHUC_DUC_KHONG_KIEP | những giới hạn về tài chính (Địa Không, cung Phúc Đức)
  - member:star:Hỏa Tinh@Phúc Đức | Hỏa Tinh (Phúc Đức): Hỏa Tinh từ cung Phúc Đức làm giảm sức
  - member:star:Địa Không@Phúc Đức | Địa Không (Phúc Đức): Địa Không từ cung Phúc Đức làm giảm sức
  - member:star:Liêm Trinh@Mệnh | Liêm Trinh (Mệnh): Liêm Trinh hãm ở cung Mệnh hội về
  - member:star:Tham Lang@Mệnh | Tham Lang (Mệnh): Tham Lang hãm ở cung Mệnh hội về
- Tương tác:
  - một trong hai sao Không, Kiếp cũng đủ hóa giải hết hiệu lực của Tử Vi (KL p.125)
  - Phá Toái làm hao tán các sao hiền (KL p.202)
  - Phá Toái làm bộ Sát Phá Tham mạnh thêm (KL p.202)
- Cứu giải:
  - Kình, Đà, Không, Kiếp, Tuần, Triệt biến Tử Vi thành kẻ côi cút, mất sức cứu giải (KL p.75)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 21. A · lá #20 (3/2/2011 18h, nam) · khả năng kiếm tiền

Kết luận nháp: **nghieng_ve (+)**, độ chắc vua, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_PHA_QUAN_TAI_BACH_TAI_TU_VU | khuynh hướng tài lộc thuận lợi (Phá Quân, Tử Vi, cung Tài Bạch)
  - rule:TV_HS_TU_VI_TAI_BACH_TAI_DAC | khuynh hướng tài lộc thuận lợi (Tử Vi, cung Tài Bạch)
  - rule:TV_TT_PAL_TAI_BACH_TU_VI_BASE_P | khuynh hướng tài lộc thuận lợi (Tử Vi, cung Tài Bạch)
  - rule:TV_TT_PAL_QUAN_LOC_LOC_TON_BASE_P | khuynh hướng tài lộc thuận lợi (Lộc Tồn, cung Quan Lộc)
  - member:star:Tử Vi@Tài Bạch | Tử Vi (Tài Bạch): Tử Vi là sao chủ của cung
  - member:star:Phá Quân@Tài Bạch | Phá Quân (Tài Bạch): Phá Quân là sao chủ của cung
  - member:hoa:Văn Khúc Hóa Khoa@Tài Bạch | Văn Khúc hóa Khoa (Tài Bạch): Khoa là danh vọng, tiếng tăm
  - member:star:Lộc Tồn@Quan Lộc | Lộc Tồn (Quan Lộc): Lộc Tồn từ cung Quan Lộc thêm trợ lực
- Khó:
  - rule:TV_TH_P2_TAI_BACH_KY | những giới hạn về tài chính (Hóa Kỵ, cung Tài Bạch)
  - rule:TV_TT_PAL_TAI_BACH_TU_VI_SAT_M | khuynh hướng tài lộc thuận lợi (Tử Vi, Linh Tinh, cung Tài Bạch)
  - member:hoa:Văn Xương Hóa Kỵ@Tài Bạch | Văn Xương hóa Kỵ (Tài Bạch): Hóa Kỵ ngay trong cung làm vướng phần nó chạm tới
  - member:star:Linh Tinh@Phúc Đức | Linh Tinh (Phúc Đức): Linh Tinh từ cung Phúc Đức làm giảm sức
  - member:star:Liêm Trinh@Mệnh | Liêm Trinh (Mệnh): Liêm Trinh hãm ở cung Mệnh hội về
  - member:star:Tham Lang@Mệnh | Tham Lang (Mệnh): Tham Lang hãm ở cung Mệnh hội về
  - member:star:Thất Sát@Quan Lộc | Thất Sát (Quan Lộc): Thất Sát hãm ở cung Quan Lộc hội về
- Tương tác:
  - Hóa Khoa đóng trên Văn Khúc (KL pp.195-197)
  - Hóa Kỵ đóng trên Văn Xương (KL pp.195-197)
  - Xương Khúc chỉ sợ Hóa Kỵ (KL p.128)
  - Phá Toái làm hao tán các sao hiền (KL p.202)
- Cứu giải:
  - Kình, Đà, Không, Kiếp, Tuần, Triệt biến Tử Vi thành kẻ côi cút, mất sức cứu giải (KL p.75)
  - Hóa Khoa là sao cứu giải mạnh nhất (KL p.120)
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)

## 22. C · lá #21 (11/8/1959 11h, nam) · sức khỏe

Kết luận nháp: **khong_ket_luan**, độ chắc tam, tầm tam_phuong, có câu nặng

- Thuận:
  - rule:TV_D3_TT91_TAT_TUAN_TRIET | sao cứu giải ở cung Tật Ách (Tật Ách, cung Tật Ách)
  - rule:TV_HS_PHA_TOAI_TAT_ACH_TAT_IT_BENH | bệnh tật nhẹ, dễ chữa (Phá Toái, cung Tật Ách)
  - rule:TV_HS_THIEN_PHU_TAT_ACH_TAT_GIAI | sao cứu giải ở cung Tật Ách (Thiên Phủ, cung Tật Ách)
  - rule:TV_HS_TRIET_TAT_ACH_TAT_GIAI | sao cứu giải ở cung Tật Ách (Tật Ách, cung Tật Ách)
  - rule:TV_KL7_TAT_ACH_PHA_SAT | sao cứu giải ở cung Tật Ách (Phá Toái, cung Tật Ách)
  - rule:TV_KL7_TAT_ACH_SONG_HAO | sao cứu giải ở cung Tật Ách (Đại Hao, cung Tật Ách)
  - rule:TV_PB_KL_TAT_ACH_KL_TAT_ACH_CUU_GIAI_MANH | sao cứu giải ở cung Tật Ách (Thiên Phủ, cung Tật Ách)
  - rule:TV_PB_KL_TAT_ACH_KL_TAT_ACH_CUU_GIAI_NHO | sao cứu giải ở cung Tật Ách (Thiên Quan, cung Tật Ách)
- Khó:
  - member:star:Tiểu Hao@Phụ Mẫu | Tiểu Hao (Phụ Mẫu): Tiểu Hao từ cung Phụ Mẫu làm giảm sức
  - member:star:Hỏa Tinh@Phụ Mẫu | Hỏa Tinh (Phụ Mẫu): Hỏa Tinh từ cung Phụ Mẫu làm giảm sức
  - member:star:Đà La@Điền Trạch | Đà La (Điền Trạch): Đà La từ cung Điền Trạch làm giảm sức
  - member:star:Đại Hao@Tật Ách | Đại Hao (Tật Ách): Đại Hao trong cung làm giảm sức
  - member:star:Thất Sát@Phụ Mẫu | Thất Sát (Phụ Mẫu): Thất Sát hãm ở cung Phụ Mẫu hội về
  - member:star:Địa Không@Điền Trạch | Địa Không (Điền Trạch): Địa Không ở cung Điền Trạch chế Thiên Phủ: Thiên Phủ sợ Hóa Kỵ và Không Kiếp: Mệnh dễ nghèo
  - member:star:Địa Kiếp@Điền Trạch | Địa Kiếp (Điền Trạch): Địa Kiếp ở cung Điền Trạch chế Thiên Phủ: Thiên Phủ sợ Hóa Kỵ và Không Kiếp: Mệnh dễ nghèo
  - member:tt:Triệt@Tật Ách | Triệt (Tật Ách): Triệt án ngữ: giảm cả cái tốt lẫn cái xấu
- Tương tác:
  - Hóa Lộc đóng trên Vũ Khúc (KL pp.195-197)
  - Tuần, Triệt là sao cản phá: giảm cả cái tốt lẫn cái xấu của các sao (KL p.203)
  - chính tinh đắc địa gặp Tuần, Triệt thì như hãm địa, bị phá hư (KL p.203)
  - Thiên Phủ không sợ Triệt (KL p.96)
- Cứu giải:
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 23. C · lá #23 (12/8/2022 9h, nữ) · sức khỏe

Kết luận nháp: **khong_ket_luan**, độ chắc tam, tầm tam_phuong, có câu nặng

- Thuận:
  - rule:TV_HS_HOA_KHOA_TAT_ACH_TAT_BENH_NHE | sao cứu giải ở cung Tật Ách (Hóa Khoa, cung Tật Ách)
  - rule:TV_HS_HOA_KHOA_TAT_ACH_TAT_BENH_NHE | bệnh tật nhẹ, dễ chữa (Hóa Khoa, cung Tật Ách)
  - rule:TV_HS_TA_PHU_TAT_ACH_TAT_MAU_MANH | bệnh tật nhẹ, dễ chữa (Tả Phụ, cung Tật Ách)
  - rule:TV_KL7_TAT_ACH_PHA_SAT | sao cứu giải ở cung Tật Ách (Phá Quân, cung Tật Ách)
  - rule:TV_PB_KL_TAT_ACH_KL_TAT_ACH_CUU_GIAI_MANH | sao cứu giải ở cung Tật Ách (Hóa Khoa, cung Tật Ách)
  - rule:TV_PB_KL_TAT_ACH_KL_TAT_ACH_CUU_GIAI_NHO | sao cứu giải ở cung Tật Ách (Thiên Quan, cung Tật Ách)
  - rule:TV_PB_TH_TAT_ACH_TH_TAT_ACH_QUAN_PHUC | sao cứu giải ở cung Tật Ách (Thiên Quan, Thiên Phúc, cung Tật Ách)
  - rule:TV_PB_TH_TAT_ACH_TH_TAT_ACH_TU_PHU_LUONG_CHIEU | sao cứu giải ở cung Tật Ách (Tử Vi, cung Tật Ách)
- Khó:
  - member:star:Đại Hao@Huynh Đệ | Đại Hao (Huynh Đệ): Đại Hao từ cung Huynh Đệ làm giảm sức
  - member:star:Địa Kiếp@Phụ Mẫu | Địa Kiếp (Phụ Mẫu): Địa Kiếp từ cung Phụ Mẫu làm giảm sức
  - member:star:Địa Không@Điền Trạch | Địa Không (Điền Trạch): Địa Không từ cung Điền Trạch làm giảm sức
- Tương tác:
  - Hóa Quyền đóng trên Tử Vi (KL pp.195-197)
  - Hóa Khoa đóng trên Tả Phụ (KL pp.195-197)
  - Thiên Tướng không sợ sát tinh mà còn chế ngự được chúng (KL p.108)
  - Thất Sát không sợ Tuần Triệt, không ngán Kình Đà, còn sai khiến được chúng (KL p.114)
- Cứu giải:
  - Hóa Khoa là sao cứu giải mạnh nhất (KL p.120)
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 24. C · lá #24 (27/4/2007 15h, nam) · hôn nhân

Kết luận nháp: **tro_ngai (-)**, độ chắc ro, tầm tam_phuong, có câu nặng

- Thuận:
  - member:star:Phá Quân@Phu Thê | Phá Quân (Phu Thê): Phá Quân là sao chủ của cung
  - member:star:Văn Khúc@Quan Lộc | Văn Khúc (Quan Lộc): Văn Khúc từ cung Quan Lộc thêm trợ lực
  - member:star:Văn Xương@Thiên Di | Văn Xương (Thiên Di): Văn Xương từ cung Thiên Di thêm trợ lực
  - member:star:Tả Phụ@Phu Thê | Tả Phụ (Phu Thê): Tả Phụ trong cung thêm trợ lực
  - member:star:Lộc Tồn@Phu Thê | Lộc Tồn (Phu Thê): Lộc Tồn trong cung thêm trợ lực
  - member:star:Liêm Trinh@Quan Lộc | Liêm Trinh (Quan Lộc): Liêm Trinh sáng ở cung Quan Lộc hội về
  - member:star:Thiên Tướng@Quan Lộc | Thiên Tướng (Quan Lộc): Thiên Tướng sáng ở cung Quan Lộc hội về
  - member:star:Thất Sát@Thiên Di | Thất Sát (Thiên Di): Thất Sát sáng ở cung Thiên Di hội về
- Khó:
  - rule:TV_HS_HOA_TINH_PHU_THE_PHU_XUNG_KHAC | những trắc trở trong chuyện gắn bó (Linh Tinh, cung Phu Thê)
  - rule:TV_HS_PHA_QUAN_PHU_THE_PHU_THE_GENERAL | những trắc trở trong chuyện gắn bó (Phá Quân, cung Phu Thê)
  - rule:TV_HS_PHA_QUAN_PHU_THE_PHU_THE_GENERAL | tính hay ghen trong tình cảm (Phá Quân, cung Phu Thê)
  - rule:TV_HS_TUAN_PHU_THE_PHU_TRAC_TRO | những trắc trở trong chuyện gắn bó (Phu Thê, cung Phu Thê)
  - rule:TV_KL_CUNG_PHU_THE_SAT_PHA_LIEM_THAM | những trắc trở trong chuyện gắn bó (Phu Thê, cung Phu Thê)
  - rule:TV_KL_SAO_CUNG_PHU_THE_PHA | những trắc trở trong chuyện gắn bó (Phá Quân, cung Phu Thê)
  - rule:TV_PB_TT_PHU_THE_TT_PHU_THE_LOC_TON_TUAN_TRIET | những trắc trở trong chuyện gắn bó (Lộc Tồn, cung Phu Thê)
  - rule:TV_TH_P2_PHU_THE_PHA_TT | những trắc trở trong chuyện gắn bó (Phá Quân, cung Phu Thê)
- Tương tác:
  - Tuần, Triệt là sao cản phá: giảm cả cái tốt lẫn cái xấu của các sao (KL p.203)
  - chính tinh đắc địa gặp Tuần, Triệt thì như hãm địa, bị phá hư (KL p.203)
  - Thiên Tướng không sợ sát tinh mà còn chế ngự được chúng (KL p.108)
  - Thất Sát không sợ Tuần Triệt, không ngán Kình Đà, còn sai khiến được chúng (KL p.114)
- Cứu giải:
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 25. C · lá #25 (3/1/2016 20h, nam) · cách giữ và quản lý tiền

Kết luận nháp: **chua_du**, độ chắc tam, tầm mot_sao

- Thuận:
  - member:star:Thiên Cơ@Phúc Đức | Thiên Cơ (Phúc Đức): cung Tài Bạch vô chính diệu nên mượn Thiên Cơ từ cung Phúc Đức làm sao chủ
  - member:star:Thiên Lương@Phúc Đức | Thiên Lương (Phúc Đức): cung Tài Bạch vô chính diệu nên mượn Thiên Lương từ cung Phúc Đức làm sao chủ
  - member:hoa:Thiên Cơ Hóa Lộc@Phúc Đức | Thiên Cơ hóa Lộc (Phúc Đức): Lộc là tiền bạc, sự dễ chịu về vật chất
  - member:hoa:Thiên Lương Hóa Quyền@Phúc Đức | Thiên Lương hóa Quyền (Phúc Đức): Quyền là địa vị, quyền
  - member:star:Tả Phụ@Mệnh | Tả Phụ (Mệnh): Tả Phụ từ cung Mệnh thêm trợ lực
  - member:star:Văn Khúc@Mệnh | Văn Khúc (Mệnh): Văn Khúc từ cung Mệnh thêm trợ lực
  - member:star:Thái Dương@Mệnh | Thái Dương (Mệnh): Thái Dương sáng ở cung Mệnh hội về
  - member:star:Cự Môn@Mệnh | Cự Môn (Mệnh): Cự Môn sáng ở cung Mệnh hội về
- Khó:
  - member:star:Đà La@Mệnh | Đà La (Mệnh): Đà La từ cung Mệnh làm giảm sức
  - member:star:Đại Hao@Quan Lộc | Đại Hao (Quan Lộc): Đại Hao từ cung Quan Lộc làm giảm sức
- Tương tác:
  - Tài Bạch mượn Thiên Cơ của Phúc Đức (KL pp.218, 222)
  - Tài Bạch mượn Thiên Lương của Phúc Đức (KL pp.218, 222)
  - Hóa Lộc đóng trên Thiên Cơ (KL pp.195-197)
  - Hóa Quyền đóng trên Thiên Lương (KL pp.195-197)
- Cứu giải:
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 26. C · lá #26 (20/7/1991 21h, nữ) · sức khỏe

Kết luận nháp: **khong_ket_luan**, độ chắc tam, tầm tam_phuong, có câu nặng

- Thuận:
  - rule:TV_HS_HOA_KHOA_TAT_ACH_TAT_BENH_NHE | sao cứu giải ở cung Tật Ách (Hóa Khoa, cung Tật Ách)
  - rule:TV_HS_HOA_KHOA_TAT_ACH_TAT_BENH_NHE | bệnh tật nhẹ, dễ chữa (Hóa Khoa, cung Tật Ách)
  - rule:TV_HS_THIEN_GIAI_TAT_ACH_TAT_TOT | sao cứu giải ở cung Tật Ách (Giải Thần, cung Tật Ách)
  - rule:TV_PB_KL_TAT_ACH_KL_TAT_ACH_CUU_GIAI_MANH | sao cứu giải ở cung Tật Ách (Hóa Khoa, cung Tật Ách)
  - rule:TV_PB_KL_TAT_ACH_KL_TAT_ACH_CUU_GIAI_NHO | sao cứu giải ở cung Tật Ách (Giải Thần, cung Tật Ách)
  - rule:TV_PB_KL_TAT_ACH_KL_TAT_ACH_THIEN_TAI | sao cứu giải ở cung Tật Ách (Thiên Tài, cung Tật Ách)
  - rule:TV_PB_TH_TAT_ACH_TH_TAT_ACH_TU_PHU_LUONG_CHIEU | sao cứu giải ở cung Tật Ách (Thiên Lương, cung Tật Ách)
  - rule:TV_PB_TT_TAT_ACH_TT_TAT_ACH_KHUC_CAT | sao cứu giải ở cung Tật Ách (Văn Khúc, Hóa Khoa, cung Tật Ách)
- Khó:
  - member:hoa:Văn Xương Hóa Kỵ@Điền Trạch | Văn Xương hóa Kỵ (Điền Trạch): Hóa Kỵ từ cung Điền Trạch làm vướng phần nó chạm tới
  - member:star:Linh Tinh@Điền Trạch | Linh Tinh (Điền Trạch): Linh Tinh từ cung Điền Trạch làm giảm sức
  - member:star:Thiên Đồng@Huynh Đệ | Thiên Đồng (Huynh Đệ): Thiên Đồng hãm ở cung Huynh Đệ hội về
- Tương tác:
  - Tật Ách mượn Thái Dương của Phụ Mẫu (KL pp.218, 222)
  - Tật Ách mượn Thiên Lương của Phụ Mẫu (KL pp.218, 222)
  - Hóa Lộc đóng trên Cự Môn (KL pp.195-197)
  - Hóa Quyền đóng trên Thái Dương (KL pp.195-197)
- Cứu giải:
  - Hóa Khoa là sao cứu giải mạnh nhất (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 27. C · lá #27 (7/4/1934 3h, nam) · hôn nhân

Kết luận nháp: **tro_ngai (-)**, độ chắc ro, tầm tam_phuong, có câu nặng

- Thuận:
  - member:star:Liêm Trinh@Quan Lộc | Liêm Trinh (Quan Lộc): cung Phu Thê vô chính diệu nên mượn Liêm Trinh từ cung Quan Lộc làm sao chủ
  - member:star:Tham Lang@Quan Lộc | Tham Lang (Quan Lộc): cung Phu Thê vô chính diệu nên mượn Tham Lang từ cung Quan Lộc làm sao chủ
  - member:hoa:Liêm Trinh Hóa Lộc@Quan Lộc | Liêm Trinh hóa Lộc (Quan Lộc): Lộc là tiền bạc, sự dễ chịu về vật chất
  - member:star:Tả Phụ@Quan Lộc | Tả Phụ (Quan Lộc): Tả Phụ từ cung Quan Lộc thêm trợ lực
  - member:star:Thiên Việt@Thiên Di | Thiên Việt (Thiên Di): Thiên Việt từ cung Thiên Di thêm trợ lực
  - member:star:Thiên Phủ@Phúc Đức | Thiên Phủ (Phúc Đức): Thiên Phủ sáng ở cung Phúc Đức hội về
  - member:star:Thiên Tướng@Thiên Di | Thiên Tướng (Thiên Di): Thiên Tướng sáng ở cung Thiên Di hội về
- Khó:
  - rule:TV_PB_KL_PHU_THE_KL_PHU_THE_CO_QUA | những trắc trở trong chuyện gắn bó (Cô Thần, cung Phu Thê)
  - rule:TV_TH_AUX2_MENH_KK_DAO_HONG | những trắc trở trong chuyện gắn bó (Địa Kiếp, Hồng Loan, cung Mệnh)
  - member:star:Kình Dương@Phúc Đức | Kình Dương (Phúc Đức): Kình Dương từ cung Phúc Đức làm giảm sức
  - member:star:Hỏa Tinh@Phúc Đức | Hỏa Tinh (Phúc Đức): Hỏa Tinh từ cung Phúc Đức làm giảm sức
  - member:star:Tiểu Hao@Quan Lộc | Tiểu Hao (Quan Lộc): Tiểu Hao từ cung Quan Lộc làm giảm sức
  - member:star:Đại Hao@Phu Thê | Đại Hao (Phu Thê): Đại Hao trong cung làm giảm sức
- Tương tác:
  - Phu Thê mượn Liêm Trinh của Quan Lộc (KL pp.218, 222)
  - Phu Thê mượn Tham Lang của Quan Lộc (KL pp.218, 222)
  - Hóa Lộc đóng trên Liêm Trinh (KL pp.195-197)
- Cứu giải:
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 28. C · lá #29 (27/9/1992 13h, nam) · phần tích lũy, nhà cửa

Kết luận nháp: **tro_ngai (-)**, độ chắc ro, tầm tam_phuong, có câu nặng

- Thuận:
  - member:star:Thất Sát@Điền Trạch | Thất Sát (Điền Trạch): Thất Sát là sao chủ của cung
  - member:hoa:Tả Phụ Hóa Khoa@Tử Tức | Tả Phụ hóa Khoa (Tử Tức): Khoa là danh vọng, tiếng tăm
  - member:star:Hữu Bật@Huynh Đệ | Hữu Bật (Huynh Đệ): Hữu Bật từ cung Huynh Đệ thêm trợ lực
  - member:star:Thiên Phủ@Tử Tức | Thiên Phủ (Tử Tức): Thiên Phủ sáng ở cung Tử Tức hội về
  - member:star:Tham Lang@Huynh Đệ | Tham Lang (Huynh Đệ): Tham Lang sáng ở cung Huynh Đệ hội về
  - member:star:Phá Quân@Tật Ách | Phá Quân (Tật Ách): Phá Quân sáng ở cung Tật Ách hội về
- Khó:
  - rule:TV_HS_DIA_KHONG_DIEN_TRACH_DIEN_HAM | những giới hạn về nhà cửa, cơ nghiệp (Địa Kiếp, cung Điền Trạch)
  - rule:TV_HS_THAT_SAT_DIEN_TRACH_DIEN_BAT_LOI | những giới hạn về nhà cửa, cơ nghiệp (Thất Sát, cung Điền Trạch)
  - rule:TV_HS_THAT_SAT_DIEN_TRACH_DIEN_TY_NGO | những giới hạn về nhà cửa, cơ nghiệp (Thất Sát, cung Điền Trạch)
  - rule:TV_KL_SAO_CUNG_DIEN_TRACH_SAT | những giới hạn về nhà cửa, cơ nghiệp (Thất Sát, cung Điền Trạch)
  - rule:TV_PB_KL_DIEN_TRACH_KL_DIEN_TRACH_KK_HAM | những giới hạn về nhà cửa, cơ nghiệp (Địa Kiếp, cung Điền Trạch)
  - rule:TV_PB_KL_DIEN_TRACH_KL_DIEN_TRACH_NGHEO | những giới hạn về nhà cửa, cơ nghiệp (Thất Sát, Địa Kiếp, cung Điền Trạch)
  - member:hoa:Vũ Khúc Hóa Kỵ@Tử Tức | Vũ Khúc hóa Kỵ (Tử Tức): Hóa Kỵ từ cung Tử Tức làm vướng phần nó chạm tới
  - member:star:Kình Dương@Tử Tức | Kình Dương (Tử Tức): Kình Dương từ cung Tử Tức làm giảm sức
- Tương tác:
  - Hóa Khoa đóng trên Tả Phụ (KL pp.195-197)
  - Hóa Kỵ đóng trên Vũ Khúc (KL pp.195-197)
  - gặp sao giải mạnh thì hung sát tinh bị hóa giải, thành ra ngộ chế (KL p.200)
  - Sát Phá Tham, nhất là hãm địa, gặp Hóa Khoa thì hung tinh ngộ chế (TVNL p.15)
- Cứu giải:
  - Thiên Phủ giảm bớt tính hung hăng của sát tinh (KL p.97)
  - Hóa Khoa là sao cứu giải mạnh nhất (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 29. C · lá #30 (13/12/2007 5h, nữ) · sức khỏe

Kết luận nháp: **khong_ket_luan**, độ chắc tam, tầm tam_phuong, có câu nặng

- Thuận:
  - rule:TV_HS_HOA_LOC_TAT_ACH_TAT_MAU_KHOI | bệnh tật nhẹ, dễ chữa (Hóa Lộc, cung Tật Ách)
  - rule:TV_PB_KL_TAT_ACH_KL_TAT_ACH_CUU_GIAI_NHO | sao cứu giải ở cung Tật Ách (Nguyệt Đức, Hóa Lộc, cung Tật Ách)
  - rule:TV_PB_TH_TAT_ACH_TH_TAT_ACH_TU_PHU_LUONG_CHIEU | sao cứu giải ở cung Tật Ách (Thiên Lương, cung Tật Ách)
  - member:star:Thái Âm@Tật Ách | Thái Âm (Tật Ách): Thái Âm là sao chủ của cung
  - member:hoa:Thái Âm Hóa Lộc@Tật Ách | Thái Âm hóa Lộc (Tật Ách): Lộc là tiền bạc, sự dễ chịu về vật chất
  - member:hoa:Thiên Đồng Hóa Quyền@Huynh Đệ | Thiên Đồng hóa Quyền (Huynh Đệ): Quyền là địa vị, quyền
  - member:hoa:Thiên Cơ Hóa Khoa@Điền Trạch | Thiên Cơ hóa Khoa (Điền Trạch): Khoa là danh vọng, tiếng tăm
  - member:star:Hữu Bật@Điền Trạch | Hữu Bật (Điền Trạch): Hữu Bật từ cung Điền Trạch thêm trợ lực
- Khó:
  - member:star:Hỏa Tinh@Điền Trạch | Hỏa Tinh (Điền Trạch): Hỏa Tinh từ cung Điền Trạch làm giảm sức
  - member:star:Thái Dương@Phụ Mẫu | Thái Dương (Phụ Mẫu): Thái Dương hãm ở cung Phụ Mẫu hội về
- Tương tác:
  - Hóa Lộc đóng trên Thái Âm (KL pp.195-197)
  - Hóa Quyền đóng trên Thiên Đồng (KL pp.195-197)
  - Hóa Khoa đóng trên Thiên Cơ (KL pp.195-197)
- Cứu giải:
  - Hóa Khoa là sao cứu giải mạnh nhất (KL p.120)

## 30. C · lá #31 (19/1/1955 5h, nữ) · sức khỏe

Kết luận nháp: **khong_ket_luan**, độ chắc tam, tầm tam_phuong, có câu nặng

- Thuận:
  - rule:TV_D3_TT91_TAT_TUAN_TRIET | sao cứu giải ở cung Tật Ách (Tật Ách, cung Tật Ách)
  - rule:TV_HS_PHA_TOAI_TAT_ACH_TAT_IT_BENH | bệnh tật nhẹ, dễ chữa (Phá Toái, cung Tật Ách)
  - rule:TV_HS_TUAN_TAT_ACH_TAT_GIAI | sao cứu giải ở cung Tật Ách (Tật Ách, cung Tật Ách)
  - rule:TV_KL7_TAT_ACH_PHA_SAT | sao cứu giải ở cung Tật Ách (Phá Toái, cung Tật Ách)
  - rule:TV_KL7_TAT_ACH_SONG_HAO | sao cứu giải ở cung Tật Ách (Đại Hao, cung Tật Ách)
  - rule:TV_PB_KL_TAT_ACH_KL_TAT_ACH_CUU_GIAI_MANH | sao cứu giải ở cung Tật Ách (Thiên Đồng, cung Tật Ách)
  - rule:TV_PB_TH_TAT_ACH_TH_TAT_ACH_TU_PHU_LUONG_CHIEU | sao cứu giải ở cung Tật Ách (Thiên Lương, cung Tật Ách)
  - rule:TV_TL_TAT_ACH_GIAM | bệnh tật nhẹ, dễ chữa (Tật Ách, cung Tật Ách)
- Khó:
  - member:star:Đại Hao@Tật Ách | Đại Hao (Tật Ách): Đại Hao trong cung làm giảm sức
  - member:star:Tiểu Hao@Phụ Mẫu | Tiểu Hao (Phụ Mẫu): Tiểu Hao từ cung Phụ Mẫu làm giảm sức
  - member:star:Thiên Lương@Phụ Mẫu | Thiên Lương (Phụ Mẫu): Thiên Lương hãm ở cung Phụ Mẫu hội về
  - member:tt:Tuần@Tật Ách | Tuần (Tật Ách): Tuần án ngữ: giảm cả cái tốt lẫn cái xấu
- Tương tác:
  - Tuần, Triệt là sao cản phá: giảm cả cái tốt lẫn cái xấu của các sao (KL p.203)
  - chính tinh đắc địa gặp Tuần, Triệt thì như hãm địa, bị phá hư (KL p.203)
  - Thiên Đồng không sợ Tuần, Triệt (có ý kiến cho là cần, để bớt thay đổi) (KL p.91)
- Cứu giải:
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 31. holdout · lá #997 (20/11/1959 21h, nam) · cách giữ và quản lý tiền

Kết luận nháp: **chua_phan_xu**, độ chắc tam, tầm tam_phuong

- Thuận:
  - rule:TV_TT_PAL_TAI_BACH_CU_MON_WITH_THAI_DUONG_P | sự bền vững của tài sản (Cự Môn, Thái Dương, cung Tài Bạch)
  - member:star:Thái Dương@Tài Bạch | Thái Dương (Tài Bạch): Thái Dương là sao chủ của cung
  - member:star:Cự Môn@Tài Bạch | Cự Môn (Tài Bạch): Cự Môn là sao chủ của cung
  - member:star:Thiên Khôi@Mệnh | Thiên Khôi (Mệnh): Thiên Khôi từ cung Mệnh thêm trợ lực
  - member:star:Thiên Việt@Tài Bạch | Thiên Việt (Tài Bạch): Thiên Việt trong cung thêm trợ lực
- Khó:
  - rule:TV_TT_PAL_TAI_BACH_THAI_DUONG_WITH_CU_MON_M | dòng tiền khó giữ, dễ hao tán (Thái Dương, Cự Môn, cung Tài Bạch)
  - member:star:Địa Không@Mệnh | Địa Không (Mệnh): Địa Không từ cung Mệnh làm giảm sức
  - member:tt:Triệt@Tài Bạch | Triệt (Tài Bạch): Triệt án ngữ: giảm cả cái tốt lẫn cái xấu
- Tương tác:
  - Tuần, Triệt là sao cản phá: giảm cả cái tốt lẫn cái xấu của các sao (KL p.203)
  - chính tinh đắc địa gặp Tuần, Triệt thì như hãm địa, bị phá hư (KL p.203)
  - Khôi Việt sợ Tuần Triệt, Hình Kỵ, Kình Đà, Không Kiếp, Hỏa Linh: công danh trắc trở (KL p.145)
  - cát tinh sợ Triệt vì không có dịp phát triển (KL p.146)
- Cứu giải:
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 32. holdout · lá #966 (16/11/1961 4h, nam) · khả năng kiếm tiền

Kết luận nháp: **chua_phan_xu**, độ chắc tam, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_BAT_TOA_TAI_BACH_TAI_CO_TIEN | khuynh hướng tài lộc thuận lợi (Bát Tọa, cung Tài Bạch)
  - rule:TV_KL_CT_LUONG_DUONG | khuynh hướng tài lộc thuận lợi (Thiên Lương, Thái Dương, cung Mệnh)
  - rule:TV_TT_MENH_TA_HUU_TAI_QUAN | khuynh hướng tài lộc thuận lợi (Tả Phụ, Hữu Bật, cung Mệnh)
  - member:star:Thái Âm@Tài Bạch | Thái Âm (Tài Bạch): Thái Âm là sao chủ của cung
  - member:hoa:Thái Dương Hóa Quyền@Mệnh | Thái Dương hóa Quyền (Mệnh): Quyền là địa vị, quyền
  - member:star:Tả Phụ@Quan Lộc | Tả Phụ (Quan Lộc): Tả Phụ từ cung Quan Lộc thêm trợ lực
  - member:star:Hữu Bật@Quan Lộc | Hữu Bật (Quan Lộc): Hữu Bật từ cung Quan Lộc thêm trợ lực
  - member:star:Lộc Tồn@Mệnh | Lộc Tồn (Mệnh): Lộc Tồn từ cung Mệnh thêm trợ lực
- Khó:
  - rule:TV_HS_THIEN_KHOC_TAI_BACH_TAI_KHO | những giới hạn về tài chính (Thiên Khốc, cung Tài Bạch)
  - rule:TV_TH_P2_TAI_BACH_TT | những giới hạn về tài chính (Tài Bạch, cung Tài Bạch)
  - rule:TV_KL_PHU2_BA_KHONG | những giới hạn về tài chính (Địa Không, cung Mệnh)
  - member:star:Địa Kiếp@Quan Lộc | Địa Kiếp (Quan Lộc): Địa Kiếp từ cung Quan Lộc làm giảm sức
  - member:star:Địa Không@Mệnh | Địa Không (Mệnh): Địa Không từ cung Mệnh làm giảm sức
  - member:star:Thiên Lương@Mệnh | Thiên Lương (Mệnh): Thiên Lương hãm ở cung Mệnh hội về
  - member:tt:Tuần và Triệt@Tài Bạch | Tuần và Triệt (Tài Bạch): Tuần và Triệt án ngữ: giảm cả cái tốt lẫn cái xấu
- Tương tác:
  - Hóa Quyền đóng trên Thái Dương (KL pp.195-197)
  - Tuần, Triệt là sao cản phá: giảm cả cái tốt lẫn cái xấu của các sao (KL p.203)
  - Tuần và Triệt cùng một cung thì sức cản, sức giúp đều mạnh hơn (KL p.204)
- Cứu giải:
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 33. holdout · lá #935 (21/11/1943 5h, nữ) · đường công danh

Kết luận nháp: **hai_mat**, độ chắc tam, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_THIEN_LUONG_QUAN_LOC_QUAN_TOT | triển vọng về địa vị, công danh (Thiên Lương, cung Quan Lộc)
  - rule:TV_HS_THIEN_LUONG_QUAN_LOC_QUAN_TOT | năng lực nổi trội (Thiên Lương, cung Quan Lộc)
  - rule:TV_HS_THIEN_LUONG_QUAN_LOC_QUAN_VAN | năng lực học thuật, văn chương (Thiên Lương, cung Quan Lộc)
  - rule:TV_KL_SAO_CUNG_QUAN_LOC_LUONG_QUY | triển vọng về địa vị, công danh (Thiên Lương, cung Quan Lộc)
  - rule:TV_KL_SAO_CUNG_QUAN_LOC_LUONG_QUY | năng lực nổi trội (Thiên Lương, cung Quan Lộc)
  - rule:TV_TT_PAL_QUAN_LOC_LOC_TON_BASE_P | khả năng kiêm cả văn lẫn võ (Lộc Tồn, cung Quan Lộc)
  - rule:TV_KL_PHU2_CO_DAC_DIA | năng lực nổi trội (Thiên Cơ, cung Mệnh)
  - rule:TV_TH_COMBO_THIEN_CO_CAT | uy thế và khả năng điều khiển người khác (Thiên Cơ, Hóa Khoa, cung Mệnh)
- Khó:
  - rule:TV_HS_TRIET_QUAN_LOC_QUAN_LAN_DAN | những trở ngại trên đường công danh (Quan Lộc, cung Quan Lộc)
  - member:star:Hỏa Tinh@Quan Lộc | Hỏa Tinh (Quan Lộc): Hỏa Tinh trong cung làm giảm sức
  - member:tt:Triệt@Quan Lộc | Triệt (Quan Lộc): Triệt án ngữ: giảm cả cái tốt lẫn cái xấu
- Tương tác:
  - Hóa Khoa đóng trên Thái Âm (KL pp.195-197)
  - Tuần, Triệt là sao cản phá: giảm cả cái tốt lẫn cái xấu của các sao (KL p.203)
  - chính tinh đắc địa gặp Tuần, Triệt thì như hãm địa, bị phá hư (KL p.203)
  - Thiên Đồng không sợ Tuần, Triệt (có ý kiến cho là cần, để bớt thay đổi) (KL p.91)
- Cứu giải:
  - Hóa Khoa là sao cứu giải mạnh nhất (KL p.120)
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 34. holdout · lá #904 (9/5/1931 0h, nam) · hôn nhân

Kết luận nháp: **nghieng_ve (-)**, độ chắc vua, tầm tam_phuong, có câu nặng

- Thuận:
  - rule:TV_TT_PAL_PHU_THE_THIEN_VIET_BASE_P | sự hòa hợp và gắn bó trong hôn nhân (Thiên Việt, cung Phu Thê)
  - member:star:Phá Quân@Phu Thê | Phá Quân (Phu Thê): Phá Quân là sao chủ của cung
  - member:star:Thiên Việt@Phu Thê | Thiên Việt (Phu Thê): Thiên Việt trong cung thêm trợ lực
  - member:star:Tả Phụ@Phúc Đức | Tả Phụ (Phúc Đức): Tả Phụ từ cung Phúc Đức thêm trợ lực
  - member:star:Thiên Khôi@Phúc Đức | Thiên Khôi (Phúc Đức): Thiên Khôi từ cung Phúc Đức thêm trợ lực
  - member:star:Hữu Bật@Quan Lộc | Hữu Bật (Quan Lộc): Hữu Bật từ cung Quan Lộc thêm trợ lực
  - member:star:Thiên Tướng@Quan Lộc | Thiên Tướng (Quan Lộc): Thiên Tướng sáng ở cung Quan Lộc hội về
- Khó:
  - rule:TV_HS_PHA_QUAN_PHU_THE_PHU_THE_GENERAL | những trắc trở trong chuyện gắn bó (Phá Quân, cung Phu Thê)
  - rule:TV_HS_PHA_QUAN_PHU_THE_PHU_THE_GENERAL | tính hay ghen trong tình cảm (Phá Quân, cung Phu Thê)
  - rule:TV_KL_CUNG_PHU_THE_SAT_PHA_LIEM_THAM | những trắc trở trong chuyện gắn bó (Phu Thê, cung Phu Thê)
  - rule:TV_KL_SAO_CUNG_PHU_THE_PHA | những trắc trở trong chuyện gắn bó (Phá Quân, cung Phu Thê)
  - rule:TV_TL_PHU_THE_SPT_CHANG_LANH | những trắc trở trong chuyện gắn bó (Phá Quân, cung Phu Thê)
  - rule:TV_TT_PAL_PHU_THE_PHA_QUAN_BASE_M | những trắc trở trong chuyện gắn bó (Phá Quân, cung Phu Thê)
  - member:hoa:Văn Xương Hóa Kỵ@Thiên Di | Văn Xương hóa Kỵ (Thiên Di): Hóa Kỵ từ cung Thiên Di làm vướng phần nó chạm tới
  - member:star:Tiểu Hao@Phúc Đức | Tiểu Hao (Phúc Đức): Tiểu Hao từ cung Phúc Đức làm giảm sức
- Tương tác:
  - Hóa Kỵ đóng trên Văn Xương (KL pp.195-197)
  - Khôi Việt sợ Tuần Triệt, Hình Kỵ, Kình Đà, Không Kiếp, Hỏa Linh: công danh trắc trở (KL p.145)
- Cứu giải:
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)

## 35. holdout · lá #873 (20/6/2018 4h, nữ) · phần tích lũy, nhà cửa

Kết luận nháp: **nghieng_ve (-)**, độ chắc vua, tầm tam_phuong

- Thuận:
  - rule:TV_KL_SAO_CUNG_DIEN_TRACH_CU | chủ đề nhà cửa, cơ nghiệp (Cự Môn, cung Điền Trạch)
  - rule:TV_HS_MO_TAI_BACH_TAI_LONG_PHUONG | cơ nghiệp thừa hưởng từ ông cha (Mộ, Phượng Các, cung Tài Bạch)
  - member:star:Thiên Đồng@Điền Trạch | Thiên Đồng (Điền Trạch): Thiên Đồng là sao chủ của cung
  - member:star:Cự Môn@Điền Trạch | Cự Môn (Điền Trạch): Cự Môn là sao chủ của cung
  - member:star:Thiên Khôi@Tử Tức | Thiên Khôi (Tử Tức): Thiên Khôi từ cung Tử Tức thêm trợ lực
  - member:star:Thiên Việt@Điền Trạch | Thiên Việt (Điền Trạch): Thiên Việt trong cung thêm trợ lực
- Khó:
  - rule:TV_PB_TT_DIEN_TRACH_TT_DIEN_TRACH_CU_PHA_TO | cơ nghiệp thừa hưởng từ ông cha (Cự Môn, cung Điền Trạch)
  - rule:TV_TT_PAL_DIEN_TRACH_CU_MON_HAM_M | chủ đề nhà cửa, cơ nghiệp (Cự Môn, cung Điền Trạch)
  - rule:TV_TT_PAL_DIEN_TRACH_THIEN_DONG_WITH_CU_MON_M | chủ đề nhà cửa, cơ nghiệp (Thiên Đồng, Cự Môn, cung Điền Trạch)
  - member:hoa:Thiên Cơ Hóa Kỵ@Tật Ách | Thiên Cơ hóa Kỵ (Tật Ách): Hóa Kỵ từ cung Tật Ách làm vướng phần nó chạm tới
  - member:star:Địa Kiếp@Tử Tức | Địa Kiếp (Tử Tức): Địa Kiếp từ cung Tử Tức làm giảm sức
  - member:star:Hỏa Tinh@Tật Ách | Hỏa Tinh (Tật Ách): Hỏa Tinh từ cung Tật Ách làm giảm sức
- Tương tác:
  - Hóa Kỵ đóng trên Thiên Cơ (KL pp.195-197)
  - Khôi Việt sợ Tuần Triệt, Hình Kỵ, Kình Đà, Không Kiếp, Hỏa Linh: công danh trắc trở (KL p.145)
- Cứu giải:
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 36. holdout · lá #842 (22/6/2000 20h, nữ) · cách giữ và quản lý tiền

Kết luận nháp: **tro_ngai (-)**, độ chắc ro, tầm tam_phuong

- Thuận:
  - member:star:Thiên Cơ@Phúc Đức | Thiên Cơ (Phúc Đức): cung Tài Bạch vô chính diệu nên mượn Thiên Cơ từ cung Phúc Đức làm sao chủ
  - member:star:Thiên Lương@Phúc Đức | Thiên Lương (Phúc Đức): cung Tài Bạch vô chính diệu nên mượn Thiên Lương từ cung Phúc Đức làm sao chủ
  - member:hoa:Thái Dương Hóa Lộc@Mệnh | Thái Dương hóa Lộc (Mệnh): Lộc là tiền bạc, sự dễ chịu về vật chất
  - member:star:Văn Xương@Quan Lộc | Văn Xương (Quan Lộc): Văn Xương từ cung Quan Lộc thêm trợ lực
  - member:star:Tả Phụ@Mệnh | Tả Phụ (Mệnh): Tả Phụ từ cung Mệnh thêm trợ lực
  - member:star:Lộc Tồn@Mệnh | Lộc Tồn (Mệnh): Lộc Tồn từ cung Mệnh thêm trợ lực
  - member:star:Cự Môn@Mệnh | Cự Môn (Mệnh): Cự Môn sáng ở cung Mệnh hội về
- Khó:
  - rule:TV_TH_AUX2_TAI_BACH_HOA_TAI | dòng tiền khó giữ, dễ hao tán (Hỏa Tinh, cung Tài Bạch)
  - member:star:Hỏa Tinh@Tài Bạch | Hỏa Tinh (Tài Bạch): Hỏa Tinh trong cung làm giảm sức
  - member:star:Linh Tinh@Mệnh | Linh Tinh (Mệnh): Linh Tinh từ cung Mệnh làm giảm sức
- Tương tác:
  - Tài Bạch mượn Thiên Cơ của Phúc Đức (KL pp.218, 222)
  - Tài Bạch mượn Thiên Lương của Phúc Đức (KL pp.218, 222)
  - Hóa Lộc đóng trên Thái Dương (KL pp.195-197)
  - Xương Khúc không sợ sát tinh (KL p.128)
- Cứu giải:
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)

## 37. holdout · lá #811 (11/3/2007 13h, nữ) · khả năng kiếm tiền

Kết luận nháp: **nghieng_ve (-)**, độ chắc vua, tầm menh_tai_quan

- Thuận:
  - rule:TV_TH_P2_TAI_BACH_LINH | khuynh hướng tài lộc thuận lợi (Linh Tinh, cung Tài Bạch)
  - rule:TV_KL_CT_DONG_THU_MENH | khả năng tự tạo dựng từ hai bàn tay (Thiên Đồng, cung Mệnh)
  - rule:TV_TT_MENH_KINH_MIEU | khuynh hướng tài lộc thuận lợi (Kình Dương, cung Mệnh)
  - rule:TV_TT_NU_DONG_XK | khuynh hướng tài lộc thuận lợi (Thiên Đồng, Văn Xương, Văn Khúc, cung Mệnh)
  - member:star:Thái Dương@Phúc Đức | Thái Dương (Phúc Đức): cung Tài Bạch vô chính diệu nên mượn Thái Dương từ cung Phúc Đức làm sao chủ
  - member:star:Thiên Lương@Phúc Đức | Thiên Lương (Phúc Đức): cung Tài Bạch vô chính diệu nên mượn Thiên Lương từ cung Phúc Đức làm sao chủ
  - member:hoa:Thiên Đồng Hóa Quyền@Mệnh | Thiên Đồng hóa Quyền (Mệnh): Quyền là địa vị, quyền
  - member:hoa:Thiên Cơ Hóa Khoa@Quan Lộc | Thiên Cơ hóa Khoa (Quan Lộc): Khoa là danh vọng, tiếng tăm
- Khó:
  - rule:TV_TH_P2_TAI_BACH_TT | những giới hạn về tài chính (Tài Bạch, cung Tài Bạch)
  - rule:TV_KL_PHU2_BA_KHONG | những giới hạn về tài chính (Mệnh, cung Mệnh)
  - rule:TV_TH_DONG_HAM_NONG_CAN_KHAM_KHO | những giới hạn về tài chính (Thiên Đồng, cung Mệnh)
  - member:hoa:Cự Môn Hóa Kỵ@Mệnh | Cự Môn hóa Kỵ (Mệnh): Hóa Kỵ từ cung Mệnh làm vướng phần nó chạm tới
  - member:star:Đại Hao@Tài Bạch | Đại Hao (Tài Bạch): Đại Hao trong cung làm giảm sức
  - member:star:Linh Tinh@Tài Bạch | Linh Tinh (Tài Bạch): Linh Tinh trong cung làm giảm sức
  - member:star:Tiểu Hao@Phúc Đức | Tiểu Hao (Phúc Đức): Tiểu Hao từ cung Phúc Đức làm giảm sức
  - member:star:Cự Môn@Mệnh | Cự Môn (Mệnh): Cự Môn hãm ở cung Mệnh hội về
- Tương tác:
  - Tài Bạch mượn Thái Dương của Phúc Đức (KL pp.218, 222)
  - Tài Bạch mượn Thiên Lương của Phúc Đức (KL pp.218, 222)
  - Hóa Quyền đóng trên Thiên Đồng (KL pp.195-197)
  - Hóa Khoa đóng trên Thiên Cơ (KL pp.195-197)
- Cứu giải:
  - Hóa Khoa là sao cứu giải mạnh nhất (KL p.120)
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 38. holdout · lá #780 (19/6/1980 15h, nam) · đường công danh

Kết luận nháp: **hai_mat**, độ chắc tam, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_THIEN_MA_QUAN_LOC_QUAN_DAC | sự thuận lợi trên đường công danh (Thiên Mã, cung Quan Lộc)
  - rule:TV_HS_THIEN_VIET_QUAN_LOC_QUAN_LUNG_LAY | chủ đề danh tiếng (Thiên Việt, cung Quan Lộc)
  - rule:TV_HS_THIEN_VIET_QUAN_LOC_QUAN_LUNG_LAY | sự thuận lợi trên đường công danh (Thiên Việt, cung Quan Lộc)
  - rule:TV_KL_SAO_CUNG_QUAN_LOC_PHA_DAN_THAN | năng khiếu chuyên môn, kỹ thuật (Phá Quân, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_HOA_LINH_MA | năng khiếu chuyên môn, kỹ thuật (Linh Tinh, Thiên Mã, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_KHOI_VIET | sự thuận lợi trên đường công danh (Thiên Khôi, Thiên Việt, cung Quan Lộc)
  - rule:TV_TH_P2_QUAN_LOC_TA_HUU | khả năng kiêm cả văn lẫn võ (Tả Phụ, Hữu Bật, cung Quan Lộc)
  - rule:TV_KL_CT_SAT_THU_MENH | sự thuận lợi trên đường công danh (Thất Sát, cung Mệnh)
- Khó:
  - rule:TV_HS_PHA_QUAN_QUAN_LOC_QUAN_DAN_THAN_VU_LIEM | những trở ngại trên đường công danh (Phá Quân, cung Quan Lộc)
  - member:star:Thất Sát@Mệnh | Thất Sát (Mệnh): Thất Sát hãm ở cung Mệnh hội về
  - member:star:Linh Tinh@Quan Lộc | Linh Tinh (Quan Lộc): Linh Tinh ở cung Quan Lộc chế Thiên Việt: Khôi Việt sợ Tuần Triệt, Hình Kỵ, Kình Đà, Không Kiếp, Hỏa Linh: công danh trắc trở
- Tương tác:
  - Hóa Quyền đóng trên Vũ Khúc (KL pp.195-197)
  - Thiên Tướng không sợ sát tinh mà còn chế ngự được chúng (KL p.108)
  - Xương Khúc không sợ sát tinh (KL p.128)
  - Khôi Việt sợ Tuần Triệt, Hình Kỵ, Kình Đà, Không Kiếp, Hỏa Linh: công danh trắc trở (KL p.145)
- Cứu giải:
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 39. holdout · lá #749 (9/12/2000 18h, nam) · hôn nhân

Kết luận nháp: **chua_phan_xu**, độ chắc tam, tầm tam_phuong

- Thuận:
  - rule:TV_HS_AN_QUANG_PHU_THE_PHU_THE_HOA_THUAN | sự hòa hợp và gắn bó trong hôn nhân (Ân Quang, Thiên Quý, cung Phu Thê)
  - rule:TV_HS_THIEN_DUC_PHU_THE_THE_DAO | sự hòa hợp và gắn bó trong hôn nhân (Thiên Đức, Đào Hoa, cung Phu Thê)
  - rule:TV_KL_CUNG_PHU_THE_DEP_DOI | sự hòa hợp và gắn bó trong hôn nhân (Thiên Phủ, cung Phu Thê)
  - rule:TV_PB_KL_PHU_THE_KL_PHU_THE_QUANG_QUY | sự hòa hợp và gắn bó trong hôn nhân (Ân Quang, Thiên Quý, cung Phu Thê)
  - rule:TV_TT_PAL_PHU_THE_THIEN_PHU_BASE_P | sự hòa hợp và gắn bó trong hôn nhân (Thiên Phủ, cung Phu Thê)
  - member:star:Thiên Phủ@Phu Thê | Thiên Phủ (Phu Thê): Thiên Phủ là sao chủ của cung
  - member:star:Văn Xương@Phu Thê | Văn Xương (Phu Thê): Văn Xương trong cung thêm trợ lực
  - member:star:Văn Khúc@Phu Thê | Văn Khúc (Phu Thê): Văn Khúc trong cung thêm trợ lực
- Khó:
  - rule:TV_HS_HOA_TINH_PHU_THE_PHU_XUNG_KHAC | những trắc trở trong chuyện gắn bó (Linh Tinh, cung Phu Thê)
  - rule:TV_HS_THIEN_PHU_PHU_THE_PT_SMMD | những trắc trở trong chuyện gắn bó (Thiên Phủ, cung Phu Thê)
  - rule:TV_KL_SAO_CUNG_PHU_THE_PHU_BAT_HOA | những trắc trở trong chuyện gắn bó (Thiên Phủ, cung Phu Thê)
  - rule:TV_PB_KL_PHU_THE_KL_PHU_THE_CO_QUA | những trắc trở trong chuyện gắn bó (Quả Tú, cung Phu Thê)
  - member:star:Linh Tinh@Phu Thê | Linh Tinh (Phu Thê): Linh Tinh trong cung làm giảm sức
  - member:star:Đại Hao@Phúc Đức | Đại Hao (Phúc Đức): Đại Hao từ cung Phúc Đức làm giảm sức
  - member:star:Kình Dương@Thiên Di | Kình Dương (Thiên Di): Kình Dương từ cung Thiên Di làm giảm sức
- Tương tác:
  - Thiên Phủ sợ Tuần không, Thiên không: kho trở nên rỗng (KL p.188)
  - Thiên Tướng không sợ sát tinh mà còn chế ngự được chúng (KL p.108)
  - Xương Khúc không sợ sát tinh (KL p.128)
  - Hỏa Linh không đánh được Tử Vi, Thiên Phủ, Thái Dương (KL p.200)
- Cứu giải:
  - Thiên Phủ giảm bớt tính hung hăng của sát tinh (KL p.97)
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)

## 40. holdout · lá #718 (21/5/1948 11h, nam) · phần tích lũy, nhà cửa

Kết luận nháp: **nghieng_ve (+)**, độ chắc vua, tầm tam_phuong

- Thuận:
  - rule:TV_PB_KL_DIEN_TRACH_KL_DIEN_TRACH_LUONG_TOT | chủ đề nhà cửa, cơ nghiệp (Thiên Lương, Thiên Đồng, cung Điền Trạch)
  - rule:TV_PB_TT_DIEN_TRACH_TT_DIEN_TRACH_LUONG_TOT | chủ đề nhà cửa, cơ nghiệp (Thiên Lương, cung Điền Trạch)
  - rule:TV_PB_TT_DIEN_TRACH_TT_DIEN_TRACH_THIEN_MA | chủ đề nhà cửa, cơ nghiệp (Thiên Mã, cung Điền Trạch)
  - rule:TV_TH_P2_DIEN_TRACH_LUONG_CO | chủ đề nhà cửa, cơ nghiệp (Thiên Lương, cung Điền Trạch)
  - rule:TV_TT_PAL_DIEN_TRACH_THIEN_LUONG_MIEU_P | chủ đề nhà cửa, cơ nghiệp (Thiên Lương, cung Điền Trạch)
  - member:star:Thiên Đồng@Điền Trạch | Thiên Đồng (Điền Trạch): Thiên Đồng là sao chủ của cung
  - member:star:Thiên Lương@Điền Trạch | Thiên Lương (Điền Trạch): Thiên Lương là sao chủ của cung
  - member:hoa:Thái Âm Hóa Quyền@Huynh Đệ | Thái Âm hóa Quyền (Huynh Đệ): Quyền là địa vị, quyền
- Khó:
  - rule:TV_KL_SAO_CUNG_DIEN_TRACH_SONG_HAO | những giới hạn về nhà cửa, cơ nghiệp (Đại Hao, cung Điền Trạch)
  - rule:TV_PB_KL_DIEN_TRACH_KL_DIEN_TRACH_HO_TANG | những giới hạn về nhà cửa, cơ nghiệp (Tang Môn, cung Điền Trạch)
  - rule:TV_TH_P2_DIEN_TRACH_TANG_HO | những giới hạn về nhà cửa, cơ nghiệp (Tang Môn, Bạch Hổ, cung Điền Trạch)
  - member:hoa:Thiên Cơ Hóa Kỵ@Tật Ách | Thiên Cơ hóa Kỵ (Tật Ách): Hóa Kỵ từ cung Tật Ách làm vướng phần nó chạm tới
  - member:star:Đại Hao@Điền Trạch | Đại Hao (Điền Trạch): Đại Hao trong cung làm giảm sức
  - member:star:Kình Dương@Tật Ách | Kình Dương (Tật Ách): Kình Dương từ cung Tật Ách làm giảm sức
  - member:star:Tiểu Hao@Tử Tức | Tiểu Hao (Tử Tức): Tiểu Hao từ cung Tử Tức làm giảm sức
  - member:star:Hỏa Tinh@Tử Tức | Hỏa Tinh (Tử Tức): Hỏa Tinh từ cung Tử Tức làm giảm sức
- Tương tác:
  - Hóa Quyền đóng trên Thái Âm (KL pp.195-197)
  - Hóa Kỵ đóng trên Thiên Cơ (KL pp.195-197)
  - Thiên Lương sợ Tuần, Triệt, Hỏa, Linh (KL p.111)
- Cứu giải:
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)

## 41. holdout · lá #687 (24/4/1966 12h, nữ) · cách giữ và quản lý tiền

Kết luận nháp: **tro_ngai (-)**, độ chắc ro, tầm tam_phuong

- Thuận:
  - member:star:Thiên Đồng@Phúc Đức | Thiên Đồng (Phúc Đức): cung Tài Bạch vô chính diệu nên mượn Thiên Đồng từ cung Phúc Đức làm sao chủ
  - member:star:Thái Âm@Phúc Đức | Thái Âm (Phúc Đức): cung Tài Bạch vô chính diệu nên mượn Thái Âm từ cung Phúc Đức làm sao chủ
  - member:hoa:Thiên Đồng Hóa Lộc@Phúc Đức | Thiên Đồng hóa Lộc (Phúc Đức): Lộc là tiền bạc, sự dễ chịu về vật chất
  - member:star:Tả Phụ@Tài Bạch | Tả Phụ (Tài Bạch): Tả Phụ trong cung thêm trợ lực
  - member:star:Văn Khúc@Mệnh | Văn Khúc (Mệnh): Văn Khúc từ cung Mệnh thêm trợ lực
  - member:star:Thái Dương@Quan Lộc | Thái Dương (Quan Lộc): Thái Dương sáng ở cung Quan Lộc hội về
  - member:star:Cự Môn@Quan Lộc | Cự Môn (Quan Lộc): Cự Môn sáng ở cung Quan Lộc hội về
- Khó:
  - rule:TV_HS_KINH_DUONG_TAI_BACH_TAI_HAM | dòng tiền khó giữ, dễ hao tán (Kình Dương, cung Tài Bạch)
  - member:star:Tiểu Hao@Quan Lộc | Tiểu Hao (Quan Lộc): Tiểu Hao từ cung Quan Lộc làm giảm sức
  - member:star:Kình Dương@Tài Bạch | Kình Dương (Tài Bạch): Kình Dương trong cung làm giảm sức
- Tương tác:
  - Tài Bạch mượn Thiên Đồng của Phúc Đức (KL pp.218, 222)
  - Tài Bạch mượn Thái Âm của Phúc Đức (KL pp.218, 222)
  - Hóa Lộc đóng trên Thiên Đồng (KL pp.195-197)
  - Xương Khúc không sợ sát tinh (KL p.128)
- Cứu giải:
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 42. holdout · lá #656 (18/7/2007 15h, nữ) · khả năng kiếm tiền

Kết luận nháp: **nghieng_ve (-)**, độ chắc vua, tầm menh_tai_quan

- Thuận:
  - rule:TV_TH_VERSE_TAI_CU_MON | khả năng tự tạo dựng từ hai bàn tay (Cự Môn, cung Tài Bạch)
  - rule:TV_TT_PAL_TAI_BACH_CU_MON_BASE_P | khả năng tự tạo dựng từ hai bàn tay (Cự Môn, cung Tài Bạch)
  - rule:TV_TT_PAL_TAI_BACH_CU_MON_BASE_P | khuynh hướng tài lộc thuận lợi (Cự Môn, cung Tài Bạch)
  - rule:TV_TT_PAL_TAI_BACH_THIEN_DONG_BASE_P | khả năng tự tạo dựng từ hai bàn tay (Thiên Đồng, cung Tài Bạch)
  - rule:TV_KL_STAR_MENH_CO_CAT_TINH | khuynh hướng tài lộc thuận lợi (Thiên Cơ, Hữu Bật, Thiên Khôi, cung Mệnh)
  - rule:TV_TT_MENH_KQL_HOP | khuynh hướng tài lộc thuận lợi (Hóa Khoa, Hóa Quyền, Hóa Lộc, cung Mệnh)
  - rule:TV_TT_MENH_QUYEN_LOC | khuynh hướng tài lộc thuận lợi (Hóa Quyền, Hóa Lộc, cung Mệnh)
  - member:star:Thiên Đồng@Tài Bạch | Thiên Đồng (Tài Bạch): Thiên Đồng là sao chủ của cung
- Khó:
  - rule:TV_HS_DIA_KHONG_TAI_BACH_TAI_HAM | những giới hạn về tài chính (Địa Kiếp, cung Tài Bạch)
  - rule:TV_HS_THIEN_KHOC_TAI_BACH_TAI_KHO | những giới hạn về tài chính (Thiên Khốc, cung Tài Bạch)
  - rule:TV_KL_SAO_CUNG_TAI_BACH_DONG_CU | những giới hạn về tài chính (Thiên Đồng, Cự Môn, cung Tài Bạch)
  - rule:TV_KL_STAR_TAI_BACH_KHONG_KIEP | những giới hạn về tài chính (Địa Kiếp, cung Tài Bạch)
  - rule:TV_TH_P2_TAI_BACH_KHONG_KIEP | những giới hạn về tài chính (Địa Kiếp, cung Tài Bạch)
  - rule:TV_TH_P2_TAI_BACH_KY | những giới hạn về tài chính (Hóa Kỵ, cung Tài Bạch)
  - rule:TV_TH_P2_TAI_BACH_TT | những giới hạn về tài chính (Tài Bạch, cung Tài Bạch)
  - member:hoa:Cự Môn Hóa Kỵ@Tài Bạch | Cự Môn hóa Kỵ (Tài Bạch): Hóa Kỵ ngay trong cung làm vướng phần nó chạm tới
- Tương tác:
  - Hóa Quyền đóng trên Thiên Đồng (KL pp.195-197)
  - Hóa Khoa đóng trên Thiên Cơ (KL pp.195-197)
  - Hóa Kỵ đóng trên Cự Môn (KL pp.195-197)
  - Tuần, Triệt là sao cản phá: giảm cả cái tốt lẫn cái xấu của các sao (KL p.203)
- Cứu giải:
  - Cự Môn hãm cần Hóa Khoa cứu giải (KL p.106)
  - Hóa Khoa là sao cứu giải mạnh nhất (KL p.120)
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)

## 43. holdout · lá #625 (7/1/2022 9h, nam) · đường công danh

Kết luận nháp: **nghieng_ve (+)**, độ chắc vua, tầm menh_tai_quan

- Thuận:
  - rule:TV_HS_THIEN_CO_QUAN_LOC_QUAN_CO_LOI | sự thuận lợi trên đường công danh (Thiên Cơ, cung Quan Lộc)
  - rule:TV_KL_PHU_DONG_LUONG_DAN_THAN | triển vọng về địa vị, công danh (Thiên Đồng, Thiên Lương, cung Mệnh)
  - rule:TV_TH_COMBO_THIEN_LUONG_CAT | uy thế và khả năng điều khiển người khác (Thiên Lương, Thiên Việt, cung Mệnh)
  - rule:TV_D3_TT67_DONG_MIEU_VUONG | chủ đề danh tiếng (Thiên Đồng, cung Mệnh)
  - rule:TV_KL_CT_CNDL | năng lực học thuật, văn chương (Mệnh, cung Mệnh)
  - rule:TV_TT_MENH_CNDL_DAN_THAN | sự thuận lợi trên đường công danh (Thiên Cơ, Thái Âm, Thiên Đồng, Thiên Lương, cung Mệnh)
  - rule:TV_TH_P2_THIEN_DI_VIET | sự hỗ trợ từ người khác (Thiên Việt, cung Thiên Di)
  - member:star:Thiên Cơ@Quan Lộc | Thiên Cơ (Quan Lộc): Thiên Cơ là sao chủ của cung
- Khó:
  - rule:TV_KL_CT_CAP_DOI_BAC_TRUNG | triển vọng về địa vị, công danh (Thiên Đồng, Thiên Lương, cung Mệnh)
  - rule:TV_KL7_THIEN_DI_CO_QUA | thế đơn độc, ít người đỡ (Cô Thần, cung Thiên Di)
  - member:star:Đại Hao@Quan Lộc | Đại Hao (Quan Lộc): Đại Hao trong cung làm giảm sức
  - member:star:Địa Kiếp@Tài Bạch | Địa Kiếp (Tài Bạch): Địa Kiếp từ cung Tài Bạch làm giảm sức
  - member:star:Tiểu Hao@Phu Thê | Tiểu Hao (Phu Thê): Tiểu Hao từ cung Phu Thê làm giảm sức
  - member:star:Địa Không@Phu Thê | Địa Không (Phu Thê): Địa Không từ cung Phu Thê làm giảm sức
  - member:star:Đà La@Mệnh | Đà La (Mệnh): Đà La từ cung Mệnh làm giảm sức
  - member:star:Thái Âm@Tài Bạch | Thái Âm (Tài Bạch): Thái Âm hãm ở cung Tài Bạch hội về
- Tương tác:
  - Hóa Lộc đóng trên Cự Môn (KL pp.195-197)
  - Thiên Cơ rất thích Song Hao; Cự Cơ Mão Dậu gặp Song Hao thì phú quý (KL p.81)
- Cứu giải:
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)

## 44. holdout · lá #594 (13/8/1936 18h, nam) · hôn nhân

Kết luận nháp: **tro_ngai (-)**, độ chắc ro, tầm tam_phuong, có câu nặng

- Thuận:
  - member:star:Tham Lang@Phu Thê | Tham Lang (Phu Thê): Tham Lang là sao chủ của cung
  - member:star:Thất Sát@Phúc Đức | Thất Sát (Phúc Đức): Thất Sát sáng ở cung Phúc Đức hội về
  - member:star:Phá Quân@Thiên Di | Phá Quân (Thiên Di): Phá Quân sáng ở cung Thiên Di hội về
- Khó:
  - rule:TV_HS_THAM_LANG_PHU_THE_PHU_THE_DAN_THAN | tính hay ghen trong tình cảm (Tham Lang, cung Phu Thê)
  - rule:TV_HS_THAM_LANG_PHU_THE_PHU_THE_DAN_THAN | những trắc trở trong chuyện gắn bó (Tham Lang, cung Phu Thê)
  - rule:TV_HS_THAM_LANG_PHU_THE_PHU_THE_JEALOUS_WIFE | tính hay ghen trong tình cảm (Tham Lang, cung Phu Thê)
  - rule:TV_HS_TUAN_PHU_THE_PHU_TRAC_TRO | những trắc trở trong chuyện gắn bó (Phu Thê, cung Phu Thê)
  - rule:TV_KL_CUNG_PHU_THE_KINH_DA_KHONG_KIEP | những trắc trở trong chuyện gắn bó (Địa Kiếp, cung Phu Thê)
  - rule:TV_KL_CUNG_PHU_THE_SAT_PHA_LIEM_THAM | những trắc trở trong chuyện gắn bó (Phu Thê, cung Phu Thê)
  - rule:TV_PB_TH_PHU_THE_TH_PHU_THE_TANG_HO_HAO | những trắc trở trong chuyện gắn bó (Bạch Hổ, Tiểu Hao, cung Phu Thê)
  - rule:TV_TH_P2_PHU_THE_KHONG_KIEP | những trắc trở trong chuyện gắn bó (Địa Kiếp, cung Phu Thê)
- Tương tác:
  - Hóa Kỵ đóng trên Liêm Trinh (KL pp.195-197)
  - Tuần, Triệt là sao cản phá: giảm cả cái tốt lẫn cái xấu của các sao (KL p.203)
  - chính tinh đắc địa gặp Tuần, Triệt thì như hãm địa, bị phá hư (KL p.203)
  - Thất Sát không sợ Tuần Triệt, không ngán Kình Đà, còn sai khiến được chúng (KL p.114)
- Cứu giải:
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
  - Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt (KL p.194)

## 45. holdout · lá #563 (5/6/1971 3h, nam) · phần tích lũy, nhà cửa

Kết luận nháp: **nghieng_ve (-)**, độ chắc vua, tầm tam_phuong, có câu nặng

- Thuận:
  - rule:TV_HS_AN_QUANG_DIEN_TRACH_DIEN_DI_SAN | cơ nghiệp thừa hưởng từ ông cha (Ân Quang, Thiên Quý, cung Điền Trạch)
  - rule:TV_HS_AN_QUANG_DIEN_TRACH_DIEN_DUOC_HIEN | chủ đề nhà cửa, cơ nghiệp (Ân Quang, Thiên Quý, cung Điền Trạch)
  - rule:TV_TT_PAL_DIEN_TRACH_PHA_QUAN_BASE_P | cơ nghiệp thừa hưởng từ ông cha (Phá Quân, cung Điền Trạch)
  - rule:TV_TT_PAL_DIEN_TRACH_TU_VI_BASE_P | chủ đề nhà cửa, cơ nghiệp (Tử Vi, cung Điền Trạch)
  - member:star:Tử Vi@Điền Trạch | Tử Vi (Điền Trạch): Tử Vi là sao chủ của cung
  - member:star:Phá Quân@Điền Trạch | Phá Quân (Điền Trạch): Phá Quân là sao chủ của cung
  - member:star:Thiên Tướng@Tử Tức | Thiên Tướng (Tử Tức): Thiên Tướng sáng ở cung Tử Tức hội về
- Khó:
  - rule:TV_HS_TU_VI_DIEN_TRACH_DIEN_SAT_PHA_THAM | những giới hạn về nhà cửa, cơ nghiệp (Tử Vi, Phá Quân, cung Điền Trạch)
  - rule:TV_KL_STAR_DIEN_TRACH_TV_SPT | chủ đề nhà cửa, cơ nghiệp (Tử Vi, Phá Quân, cung Điền Trạch)
  - rule:TV_PB_KL_DIEN_TRACH_KL_DIEN_TRACH_HO_TANG | những giới hạn về nhà cửa, cơ nghiệp (Bạch Hổ, cung Điền Trạch)
  - rule:TV_TH_P2_DIEN_TRACH_PHA | những giới hạn về nhà cửa, cơ nghiệp (Phá Quân, cung Điền Trạch)
  - rule:TV_TH_P2_DIEN_TRACH_TANG_HO | những giới hạn về nhà cửa, cơ nghiệp (Tang Môn, Bạch Hổ, cung Điền Trạch)
  - rule:TV_TT_PAL_DIEN_TRACH_TU_VI_SAT_M | chủ đề nhà cửa, cơ nghiệp (Tử Vi, Hỏa Tinh, Địa Kiếp, cung Điền Trạch)
  - rule:TV_TT_PAL_DIEN_TRACH_TU_VI_WITH_PHA_QUAN_M | những giới hạn về nhà cửa, cơ nghiệp (Tử Vi, Phá Quân, cung Điền Trạch)
  - member:star:Địa Kiếp@Tử Tức | Địa Kiếp (Tử Tức): Địa Kiếp từ cung Tử Tức làm giảm sức
- Tương tác:
  - Tử Vi không sợ Hỏa, Linh (KL p.75)
  - Thiên Tướng không sợ sát tinh mà còn chế ngự được chúng (KL p.108)
  - một trong hai sao Không, Kiếp cũng đủ hóa giải hết hiệu lực của Tử Vi (KL p.125)
  - Tham Lang giải trừ ác tính của Hỏa Linh (KL p.190)
- Cứu giải:
  - Kình, Đà, Không, Kiếp, Tuần, Triệt biến Tử Vi thành kẻ côi cút, mất sức cứu giải (KL p.75)
  - Thiên Giải, Địa Giải là sao cứu giải nhỏ (KL p.120)
