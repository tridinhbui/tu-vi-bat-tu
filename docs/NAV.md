# Thanh điều hướng (navbar / sidebar)

## Vì sao navbar bị nhảy khi chuyển trang

1. **Mỗi trang một header khác nhau.** Trang chủ (`engine/web/index.html`) có 5 mục riêng (Bạn nhận được gì, Bài viết, Xem ngày, Chiêm tinh, Lá số mẫu); các trang bài viết do `sitegen.py` sinh ra có 5 mục khác (Bài viết, Xem ngày, Chiêm tinh, Hỏi đáp, Giới thiệu); Bảng giá, Biên nhận, Chính sách, Privacy, Library chỉ có logo và nút "← Trang chủ"; trang Quản trị có tab riêng trên header.
2. **Mục nav canh phải (`margin-left:auto`)**, nên vị trí phụ thuộc mọi thứ đứng bên phải: chip tài khoản, ví xu, nút Đăng nhập. Đo ở 1440 px: mục "Bài viết" ở x=633 trên trang chủ, x=768 trên trang bài viết, x=443 trên trang chủ khi đã đăng nhập.
3. **Chip tài khoản hiện ra sau khi tải** (`/api/auth/me` trả lời) và đẩy các mục sang trái (CLS của header khoảng 0,007–0,008 trên trang chủ).
4. **Logo trang chủ được vẽ bằng JS** (`brandMark()`), các trang khác không có logo, nên chiều rộng thương hiệu khác nhau và đổi sau khi script chạy.
5. Các khác biệt nhỏ: `content.css` đổi `gap` của header, `.stuck` bật/tắt viền khi cuộn, trang kết quả ẩn hẳn nav, thanh cuộn dọc có/không giữa trang ngắn và trang dài, font web đổi sau khi tải (`display=swap`).

## Đã sửa gì

- **Một header duy nhất** cho mọi trang: `engine/tvbt/sitenav.py`. `tools/build_site.py` ghi nó vào trang sinh ra và thay header trong các trang viết tay (`index.html`, `chiem-tinh/`, `bang-gia`, `bien-nhan`, `chinh-sach-hoan-tien`, `privacy`, `library`, `admin`). Chỉ `aria-current` khác nhau giữa các trang. Test `test_every_page_has_the_same_header` kiểm tra danh sách mục giống hệt nhau trên mọi trang.
- **Danh sách mục** (cùng thứ tự ở mọi nơi): Trang chủ · Lá số (Lá số của tôi, Lập lá số, Lá số mẫu) · Luận giải (Chiêm tinh, Xem ngày) · Kiến thức (Bài viết, Hỏi đáp, Giới thiệu) · Điều hành (Quản trị, chỉ admin). Thanh ngang chỉ hiện: Lá số mẫu, Chiêm tinh, Xem ngày, Bài viết, Hỏi đáp, Giới thiệu, rồi Đăng nhập và nút chính "Lập lá số".
- **Không còn xê dịch:** mục nav nằm ngay sau logo có chiều rộng cố định (không canh phải); cụm nút bên phải canh phải và nút Đăng nhập giữ chỗ (ẩn bằng `visibility`) cho tới khi biết trạng thái đăng nhập; logo là SVG tĩnh; mục đang mở không đổi độ đậm; `html{scrollbar-gutter:stable}`; font dự phòng "Inter Fallback" có số đo gần Inter.
- **Đã đăng nhập, màn hình ≥ 1024 px: sidebar bên trái** (244 px, nền giấy, viền phải mảnh): logo, ô Tìm nhanh (⌘K / Ctrl K, tìm cả mục điều hướng và bài viết sao, cung, cách cục), Trang chủ, các nhóm có nhãn chữ hoa nhỏ và mũi tên thu gọn, cuối cùng là chuông thông báo (câu chat miễn phí, số dư xu) và thẻ người dùng (chữ cái đầu, tên, email, menu: số xu và câu chat miễn phí, Tài khoản, Nạp xu, Quản trị, Mời bạn, Đăng xuất). Nút ở góc trên thu sidebar về chỉ còn biểu tượng (72 px). Trạng thái thu gọn và nhóm đã gập được nhớ trong `localStorage` (có try/catch). Nội dung dịch sang phải; không còn thanh ngang trên cùng.
- Một đoạn script nhỏ đặt ngay trước header áp trạng thái đăng nhập lần trước (`tvbt.nav.*` trong localStorage) trước khi trang vẽ, nên sidebar không bật ra sau khi tải. `/api/auth/me` vẫn là bên quyết định.
- **Dưới 1024 px:** thanh trên gọn (logo, "Lập lá số", nút menu); menu mở ra dạng ngăn kéo trượt từ trái với cùng nội dung như sidebar. Esc hoặc bấm ra ngoài để đóng.
- Truy cập: `<nav aria-label="Điều hướng chính">`, `aria-current="page"`, nút nhóm có `aria-expanded`, khi thu gọn tên mục vẫn còn cho trình đọc màn hình và hiện dạng tooltip, viền focus đỏ son như cả site.
- Phần tài khoản trên header chuyển từ `account.js` (chỉ trang chủ) sang `js/nav.js` (mọi trang); `account.js` vẫn lo đồng bộ lá số. Bảng giá không còn ô email/đăng nhập riêng trên header.

## Ảnh chụp (mô tả)

- *Chưa đăng nhập, 1440 px, trang Bài viết:* thanh ngang nền giấy, logo la bàn + "Thiên Bàn / Tử Vi · Bát Tự", sáu mục, mục "Bài viết" có nền be bo tròn; bên phải "Đăng nhập" (viền) và "Lập lá số" (đỏ son). Đổi sang Xem ngày, Hỏi đáp, Bảng giá, trang chủ: các mục đứng yên đúng chỗ.
- *Đã đăng nhập, 1440 px:* sidebar trắng ngà bên trái, ô Tìm nhanh có ⌘K, "Trang chủ"/mục đang mở là viên thuốc nền be với biểu tượng đỏ son, các nhóm LÁ SỐ, LUẬN GIẢI, KIẾN THỨC, ĐIỀU HÀNH; dưới cùng chuông và thẻ "Bùi Đình Trí / email". Nút Góp ý dời sang phải sidebar.
- *Điện thoại 375 px:* thanh trên gồm logo, "Lập lá số", nút ba gạch; bấm vào mở ngăn kéo cùng nội dung sidebar, phía sau mờ đi.

## Số đo (Chrome headless, 12 trang)

| | Trước | Sau |
|---|---|---|
| x của "Bài viết", 1440 px, chưa đăng nhập | 633 (trang chủ) / 768 (trang khác) | 611 trên cả 12 trang |
| x của "Bài viết", 1440 px, đã đăng nhập | 443 (trang chủ) / 768 | sidebar: x=12, y=498 trên cả 12 trang |
| CLS của header | 0,0065–0,0082 trên trang chủ | 0 (chỉ lần đầu, khi font web chưa có trong cache, còn ~0,003 do đổi font) |
