// Ngũ hành of each star, for COLOUR ONLY on the traditional board (Kim xám, Mộc xanh lá, Thủy đen, Hỏa đỏ, Thổ cam). The chính tinh follow
// engine/data/star_profiles.json (TH pp.29-47); the phụ tinh follow the common Vietnamese board convention and have NOT been checked against
// a page of the project's books: this table is a display convention, never read by any rule or reading.
export const HANH = {
  'Tử Vi': 'Thổ', 'Thiên Cơ': 'Mộc', 'Thái Dương': 'Hỏa', 'Vũ Khúc': 'Kim', 'Thiên Đồng': 'Thủy', 'Liêm Trinh': 'Hỏa', 'Thiên Phủ': 'Thổ',
  'Thái Âm': 'Thủy', 'Tham Lang': 'Thủy', 'Cự Môn': 'Thủy', 'Thiên Tướng': 'Thủy', 'Thiên Lương': 'Mộc', 'Thất Sát': 'Kim', 'Phá Quân': 'Thủy',
  'Văn Xương': 'Kim', 'Văn Khúc': 'Thủy', 'Tả Phụ': 'Thổ', 'Hữu Bật': 'Thủy', 'Thiên Khôi': 'Hỏa', 'Thiên Việt': 'Hỏa', 'Lộc Tồn': 'Thổ', 'Thiên Mã': 'Hỏa',
  'Kình Dương': 'Kim', 'Đà La': 'Kim', 'Hỏa Tinh': 'Hỏa', 'Linh Tinh': 'Hỏa', 'Địa Không': 'Hỏa', 'Địa Kiếp': 'Hỏa',
  'Hóa Lộc': 'Mộc', 'Hóa Quyền': 'Mộc', 'Hóa Khoa': 'Thủy', 'Hóa Kỵ': 'Thủy',
  // vòng Lộc Tồn
  'Bác Sĩ': 'Thủy', 'Lực Sĩ': 'Hỏa', 'Thanh Long': 'Thủy', 'Tiểu Hao': 'Hỏa', 'Tướng Quân': 'Mộc', 'Tấu Thư': 'Kim', 'Phi Liêm': 'Hỏa', 'Hỷ Thần': 'Hỏa',
  'Bệnh Phù': 'Thổ', 'Đại Hao': 'Hỏa', 'Phục Binh': 'Hỏa', 'Quan Phủ': 'Hỏa',
  // vòng Thái Tuế
  'Thái Tuế': 'Hỏa', 'Thiếu Dương': 'Hỏa', 'Tang Môn': 'Mộc', 'Thiếu Âm': 'Thủy', 'Quan Phù': 'Hỏa', 'Tử Phù': 'Kim', 'Tuế Phá': 'Hỏa', 'Long Đức': 'Thủy',
  'Bạch Hổ': 'Kim', 'Phúc Đức': 'Thổ', 'Điếu Khách': 'Hỏa', 'Trực Phù': 'Kim',
  // các sao khác
  'Thiên Khốc': 'Thủy', 'Thiên Hư': 'Thủy', 'Long Trì': 'Thủy', 'Phượng Các': 'Thổ', 'Tam Thai': 'Thủy', 'Bát Tọa': 'Mộc', 'Ân Quang': 'Mộc', 'Thiên Quý': 'Thổ',
  'Hồng Loan': 'Thủy', 'Thiên Hỷ': 'Thủy', 'Đào Hoa': 'Mộc', 'Thiên Riêu': 'Thủy', 'Thiên Y': 'Thủy', 'Thiên Hình': 'Hỏa', 'Cô Thần': 'Thổ', 'Quả Tú': 'Thổ',
  'Thiên Quan': 'Hỏa', 'Thiên Phúc': 'Thổ', 'Thiên Giải': 'Hỏa', 'Địa Giải': 'Thổ', 'Thiên Đức': 'Thổ', 'Nguyệt Đức': 'Hỏa', 'Hoa Cái': 'Kim', 'Kiếp Sát': 'Hỏa',
  'Phá Toái': 'Hỏa', 'Đẩu Quân': 'Hỏa', 'Lưu Hà': 'Thủy', 'Thiên Thọ': 'Thổ', 'Thiên Tài': 'Thổ', 'Thiên Thương': 'Thổ', 'Thiên Sứ': 'Thủy', 'Thiên La': 'Kim',
  'Địa Võng': 'Kim', 'Thiên Không': 'Hỏa',
  'Quốc Ấn': 'Thổ', 'Đường Phù': 'Mộc', 'Văn Tinh': 'Hỏa', 'Thiên Trù': 'Thổ', 'Phong Cáo': 'Thổ', 'Thai Phụ': 'Kim', 'Giải Thần': 'Mộc',
};
/** Âm (−) / dương (+) of the chính tinh, as the board prints it before the name. */
export const MAJOR_SIGN = { 'Tử Vi': '+', 'Thái Dương': '+', 'Thiên Đồng': '+', 'Thiên Lương': '+', 'Thiên Tướng': '+', 'Thất Sát': '+',
  'Thiên Cơ': '−', 'Vũ Khúc': '−', 'Liêm Trinh': '−', 'Thiên Phủ': '−', 'Thái Âm': '−', 'Tham Lang': '−', 'Cự Môn': '−', 'Phá Quân': '−' };
/** Printed bold on the board: lục cát, lục sát, Lộc Tồn, Thiên Mã and the paired stars. */
export const BOLD = new Set(['Văn Xương', 'Văn Khúc', 'Tả Phụ', 'Hữu Bật', 'Thiên Khôi', 'Thiên Việt', 'Lộc Tồn', 'Thiên Mã', 'Kình Dương', 'Đà La', 'Hỏa Tinh',
  'Linh Tinh', 'Địa Không', 'Địa Kiếp', 'Long Trì', 'Phượng Các', 'Tam Thai', 'Bát Tọa']);
/** The twelve Tràng Sinh stages: printed at the foot of the palace, not in the star list. */
export const TRANG_SINH = ['Trường Sinh', 'Mộc Dục', 'Quan Đới', 'Lâm Quan', 'Đế Vượng', 'Suy', 'Bệnh', 'Tử', 'Mộ', 'Tuyệt', 'Thai', 'Dưỡng'];
export const BRANCH_HANH = { 'Tý': 'Thủy', 'Sửu': 'Thổ', 'Dần': 'Mộc', 'Mão': 'Mộc', 'Thìn': 'Thổ', 'Tỵ': 'Hỏa', 'Ngọ': 'Hỏa', 'Mùi': 'Thổ', 'Thân': 'Kim', 'Dậu': 'Kim', 'Tuất': 'Thổ', 'Hợi': 'Thủy' };
export const STEM_HANH = { 'Giáp': 'Mộc', 'Ất': 'Mộc', 'Bính': 'Hỏa', 'Đinh': 'Hỏa', 'Mậu': 'Thổ', 'Kỷ': 'Thổ', 'Canh': 'Kim', 'Tân': 'Kim', 'Nhâm': 'Thủy', 'Quý': 'Thủy' };
export const YANG_BRANCH = new Set(['Tý', 'Dần', 'Thìn', 'Ngọ', 'Thân', 'Tuất']);
export const hk = h => ({ 'Kim': 'kim', 'Mộc': 'moc', 'Thủy': 'thuy', 'Hỏa': 'hoa', 'Thổ': 'tho' })[h] || 'none';
