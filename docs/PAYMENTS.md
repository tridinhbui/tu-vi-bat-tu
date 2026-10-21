# Thanh toán, gói và paywall (giai đoạn 2)

Tài liệu cho chủ site và người vận hành. Mọi giá hiện tại là **GIÁ TẠM**: chỉ để thử hệ thống.

## Một nguồn giá duy nhất

`src/billing/config.ts` giữ mọi con số: gói xu bán bằng tiền (`PACKS`, đơn vị đồng), các gói mở khóa bằng xu (`PLANS`), chương nào miễn phí (`FREE_CHAPTERS`), chương nào trả phí (`PAID_CHAPTERS`), số đoạn xem trước (`PREVIEW_PARAGRAPHS`), giá chat và bài luận viết dài (`COSTS`). Trang `/bang-gia` đọc chúng qua `GET /api/plans`; paywall và mọi callback thanh toán kiểm tra theo chính file này. Khi đã đặt giá thật, đổi `PRICES_ARE_PLACEHOLDERS` thành `false` để trang bỏ dòng "GIÁ TẠM".

## Miễn phí và trả phí

| Miễn phí | Trả phí (mở bằng xu, cho từng lá số) |
|---|---|
| bảng lá số Tử Vi và Bát Tự, tổng quan, biểu đồ, danh sách nhận định có trang sách, năm đang xem, chương cung Mệnh đọc liền mạch | 11 cung còn lại, chương vận hạn (đại hạn, tiểu hạn, lưu niên, lời khuyên theo mốc), luận giải Bát Tự theo chương |

Chương khóa vẫn gửi 2 đoạn đầu (chương ngắn: 1 đoạn hoặc vài câu đầu) và thẻ khóa liệt kê các gói mở được chương đó.

## Paywall (bật bằng `TVBT_PAYWALL=1`)

Worker tính (hoặc lấy từ cache) toàn bộ luận giải `/api/interpret`, rồi `src/billing/paywall.ts` cắt mọi chương trả phí mà tài khoản đang đăng nhập chưa mở **trước khi** trả về trình duyệt. Chỉ các trường trong danh sách cho phép được giữ, nên trường mới thêm vào chương sau này không lọt qua khóa. Ai chưa đăng nhập, hoặc gửi thân yêu cầu không phải ngày giờ sinh, thì không mở được gì. Mở khóa (`POST /api/me/unlock`) trừ xu trong một giao dịch D1: không đủ xu thì không trừ, bấm hai lần chỉ trừ một lần, gói đã mở hết thì không trừ.

Mặc định **tắt**: khi chưa đặt biến, mọi chương vẫn hiện đủ như trước. Bật khi đã đặt giá thật:

```
wrangler.jsonc → "vars": { ..., "TVBT_PAYWALL": "1" }
```

Ghi chú: mua gói lớn sau khi đã mở lẻ vài chương vẫn tính đủ giá gói (chủ site quyết có hoàn chênh lệch không, xem chính sách hoàn tiền).

## Mã giảm giá và mã quà tặng

Tạo, xem, tắt trên `/admin` → tab "Bán hàng" (chỉ tài khoản trong `ADMIN_EMAILS`).

- **Quà tặng**: cộng số xu cố định, mỗi tài khoản một lần, có giới hạn tổng lượt và ngày hết hạn (hết ngày theo giờ Việt Nam).
- **Giảm giá**: giảm % (1–90) số tiền khi nạp xu bằng Stripe hoặc VNPAY; mỗi tài khoản một lần; lượt chỉ được đếm khi thanh toán thành công. Số tiền sau giảm làm tròn tới 1.000đ và không dưới 10.000đ.

## Đơn hàng, biên nhận, lịch sử ví

Mỗi lần bấm nạp xu tạo một dòng `orders` (bảng mới, `migrations/app/0007_commerce.sql`). Callback của cổng thanh toán được đối chiếu với **đơn này** (số tiền, số xu, tài khoản). Xu được cộng qua sổ cái với khóa `stripe:<session>` hoặc `vnpay:<mã đơn>`, nên callback lặp lại không cộng hai lần. Sau thanh toán người dùng về `/bien-nhan?order=…` (trang tự cập nhật khi cổng xác nhận). `/bang-gia#lich-su` liệt kê mọi lần nạp, đổi mã, mở khóa và hoàn xu.

`receiptEmail()` trong `src/billing/orders.ts` soạn sẵn email biên nhận (văn bản và HTML), nhưng **chưa gửi**: cần một dịch vụ gửi mail cho tên miền của site (ví dụ Cloudflare Email Service sau khi xác minh tên miền). Khi có, gọi hàm này trong `completeOrder`.

## VNPAY

Tích hợp theo API 2.1.0: tạo URL thanh toán ký HMAC-SHA512, Return URL (chỉ hiển thị kết quả, không cộng xu) và IPN (kiểm chữ ký, mã merchant, mã đơn, số tiền; cộng xu đúng một lần; trả `RspCode` 00/01/02/04/97/99 như VNPAY yêu cầu). Mặc định **tắt**; bật khi có đủ ba điều kiện:

```
npx wrangler secret put VNPAY_TMN_CODE
npx wrangler secret put VNPAY_HASH_SECRET
wrangler.jsonc → "vars": { ..., "VNPAY_ENABLED": "1" }      # và VNPAY_URL khi chuyển sang cổng thật
```

`VNPAY_URL` mặc định là sandbox `https://sandbox.vnpayment.vn/paymentv2/vpcpay.html`. Trong cổng quản trị merchant của VNPAY, khai báo IPN URL là `https://<tên miền>/api/vnpay/ipn`.

Cách ký đã được kiểm bằng test với HMAC độc lập của Node; chưa chạy một giao dịch thật trên sandbox vì cần mã TMN sandbox. Việc đầu tiên sau khi có khóa sandbox: thanh toán thử một gói bằng thẻ test NCB của VNPAY, xem đơn chuyển sang "Đã thanh toán" trên `/admin` → "Bán hàng".

## Stripe

Vẫn hoạt động như trước (`STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`); nay mỗi phiên Checkout gắn với một đơn (`metadata[order]`), nên giá sau mã giảm giá được kiểm ở webhook. Phiên tạo trước bản này (không có `metadata[order]`) vẫn được cộng theo cách cũ.

## Trước khi bật, cần áp dụng migration

```
npx wrangler d1 migrations apply tvbt-app --remote
```

## Việc chỉ chủ site làm được

1. **Giá**: giá từng gói xu (VND) và từng gói mở khóa (xu), giá chat và bài luận; VAT đã gồm hay chưa. Sửa trong `src/billing/config.ts`, rồi `PRICES_ARE_PLACEHOLDERS = false`.
2. **Chương nào miễn phí**: hiện là cung Mệnh; đổi trong `FREE_CHAPTERS` / `PAID_CHAPTERS`.
3. **VNPAY**: đăng ký merchant (cần pháp nhân), nhận `TMN_CODE` và `HASH_SECRET` sandbox rồi thật, khai báo IPN URL, chạy giao dịch thử.
4. **Pháp lý**: duyệt và hoàn thiện `/chinh-sach-hoan-tien` (đang là BẢN NHÁP, có chỗ trong ngoặc vuông), điền thông tin đơn vị bán trên biên nhận, thông báo website TMĐT với Bộ Công Thương.
5. **Email biên nhận**: chọn dịch vụ gửi mail và tên miền gửi.
6. Bật `TVBT_PAYWALL=1` khi các mục trên xong, và thêm liên kết "Bảng giá" (`/bang-gia`) vào thanh điều hướng và chân trang của `engine/web/index.html`, cùng "Chính sách hoàn tiền" (`/chinh-sach-hoan-tien`) khi bản chính thức đã duyệt. Hiện hai trang này chỉ mở được bằng đường dẫn trực tiếp, để trang đang chạy không hiện giá tạm và bản nháp pháp lý.
