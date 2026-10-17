// Learning journey: two tracks, short lessons, written for people who know nothing yet.
// Educational vocabulary only; nothing here reads anyone's chart. Terms inside lessons become tappable via glossary autoLink.
import { $, $$, esc } from './util.js';

const PALACES = ['Mệnh', 'Phụ Mẫu', 'Phúc Đức', 'Điền Trạch', 'Quan Lộc', 'Nô Bộc', 'Thiên Di', 'Tật Ách', 'Tài Bạch', 'Tử Tức', 'Phu Thê', 'Huynh Đệ'];
const STARS14 = ['Tử Vi', 'Thiên Cơ', 'Thái Dương', 'Vũ Khúc', 'Thiên Đồng', 'Liêm Trinh', 'Thiên Phủ', 'Thái Âm', 'Tham Lang', 'Cự Môn', 'Thiên Tướng', 'Thiên Lương', 'Thất Sát', 'Phá Quân'];
const GODS = ['Tỉ Kiên', 'Kiếp Tài', 'Thực Thần', 'Thương Quan', 'Thiên Tài', 'Chính Tài', 'Thất Sát', 'Chính Quan', 'Thiên Ấn', 'Chính Ấn'];
const first = s => (s || '').split(/(?<=\.)\s/)[0];
const call = (txt, cls = '') => `<aside class="ln-call ${cls}">${txt}</aside>`;

export const TRACKS = [
  { id: 'start', title: 'Bắt đầu', sub: 'Chưa biết gì cũng đọc được', levels: [{ name: 'Làm quen', lessons: ['gioi-thieu'] }] },
  { id: 'tuvi', title: 'Tử Vi Đẩu Số', sub: 'Bản đồ mười hai lĩnh vực đời sống', levels: [
    { name: 'Cấp 1 · Tử Vi cơ bản', lessons: ['tv-1'] },
    { name: 'Cấp 2 · Mười hai cung và các sao', lessons: ['tv-2', 'tv-3', 'tv-5', 'tv-6'] },
    { name: 'Cấp 3 · Cách đọc một lá số', lessons: ['tv-7', 'tv-4'] }] },
  { id: 'bat', title: 'Bát Tự Tứ Trụ', sub: 'Tám chữ và năm kiểu năng lượng', levels: [
    { name: 'Cấp 1 · Bát Tự cơ bản', lessons: ['bt-1'] },
    { name: 'Cấp 2 · Tứ Trụ và Ngũ Hành', lessons: ['bt-2'] },
    { name: 'Cấp 3 · Thập Thần và tương tác', lessons: ['bt-3', 'bt-4'] }] },
];

export const LESSONS = {
  'gioi-thieu': { title: 'Tử Vi hay Bát Tự? Bắt đầu từ đâu', min: 2, sys: 'tv', body: () => `
    <p>Cả hai đều là cách cổ truyền của phương Đông để “đọc” một con người từ <b>thời điểm sinh</b>: năm, tháng, ngày, giờ. Chúng không phải khoa học dự báo; chúng là hệ biểu tượng, giống một ngôn ngữ để suy ngẫm về bản thân.</p>
    <div class="ln-cmp"><div><h4>Tử Vi Đẩu Số</h4><p>Một <b>tấm bản đồ 12 ô</b>. Mỗi ô (cung) là một lĩnh vực của đời sống: bản thân, tiền bạc, công việc, hôn nhân, sức khỏe… Các “sao” được đặt vào các ô ấy.</p><p class="muted">Hợp khi bạn hỏi: <i>“lĩnh vực nào của đời tôi có điều đáng chú ý?”</i></p></div>
    <div><h4>Bát Tự (Tứ Trụ)</h4><p><b>Tám chữ</b> chia thành bốn trụ: Năm, Tháng, Ngày, Giờ. Chữ của ngày sinh đại diện cho chính bạn; bảy chữ còn lại cho biết bạn đang “cùng” hay “ngược” với năng lượng nào.</p><p class="muted">Hợp khi bạn hỏi: <i>“tôi là kiểu người nào và cân bằng năng lượng ra sao?”</i></p></div></div>
    <h3>Nên bắt đầu từ đâu?</h3>
    <ul><li><b>Chỉ tò mò:</b> mở lá số mẫu, đọc phần “Tóm tắt” và bấm vào các từ gạch chân.</li><li><b>Muốn hiểu lá số của mình:</b> lập lá số, đọc Tóm tắt, rồi chọn tab Tử Vi hoặc Bát Tự.</li><li><b>Muốn học:</b> đi theo lộ trình bên dưới, mỗi bài 2–4 phút.</li></ul>
    ${call('<b>Lưu ý trung thực.</b> Thiên Bàn chỉ tính và trích lại những gì sách cổ nêu, kèm trang sách. Đó không phải lời dự báo, và có những phần hệ thống nói rõ là chưa có luận giải.')}` },

  'tv-1': { title: 'Tử Vi là gì? Ba thứ cần biết', min: 3, sys: 'tv', body: () => `
    <p>Một lá số Tử Vi được lập từ <b>giờ, ngày, tháng, năm sinh theo âm lịch</b>. Kết quả là một tấm bản đồ gồm ba loại thông tin:</p>
    <ol class="ln-steps"><li><b>Mười hai cung</b> — mười hai “ngăn” cho mười hai lĩnh vực của đời sống (xem bài sau).</li><li><b>Các sao</b> — mỗi sao như một “nhân vật” có tính cách riêng, đứng trong các cung.</li><li><b>Vận hạn</b> — các chặng thời gian (mỗi chặng thường 10 năm, gọi là đại hạn) cho biết chặng nào đang “chiếu” vào cung nào.</li></ol>
    <h3>Mấy cái tên bạn sẽ gặp ngay ở đầu lá số</h3>
    <ul><li><b>Cung Mệnh</b>: cung nói về chính bạn. Đây là nơi bắt đầu đọc.</li><li><b>Cục</b> (ví dụ “Hỏa lục cục”): một con số/hành tính từ năm sinh, dùng để xếp các sao và tính tuổi bắt đầu đại hạn.</li><li><b>Bản mệnh</b> (ví dụ “Lộ Bàng Thổ”): tên hình tượng theo năm sinh, thuộc một trong năm hành.</li></ul>
    ${call('<b>Một ví dụ.</b> “Hỏa lục cục” nghĩa là: đại hạn đầu tiên bắt đầu ở tuổi 6, và các chặng sau cách nhau 10 năm (6–15, 16–25…).')}
    <p>Tử Vi <b>không</b> nói “bạn sẽ thế này”. Nó mô tả những <i>xu hướng</i> được sách cổ gắn với từng tổ hợp sao, và mỗi xu hướng còn tùy vào các sao đi cùng.</p>` },

  'tv-2': { title: 'Mười hai cung: mười hai lĩnh vực đời sống', min: 3, sys: 'tv', body: T => `
    <p>Hãy hình dung mười hai cung như mười hai phòng trong một ngôi nhà. Mỗi phòng nói về một mảng cuộc sống. Dưới đây là chúng, theo thứ tự cố định của lá số:</p>
    <div class="ln-grid">${PALACES.map(p => `<div class="ln-card"><b>${p}</b><p>${esc(first(T['palace:' + p]?.plain))}</p></div>`).join('')}</div>
    <h3>Cung Thân là gì?</h3>
    <p>Ngoài Mệnh, lá số đánh dấu thêm một cung <b>Thân</b> nằm ở một trong các cung quanh Mệnh. Truyền thống xem đó là lĩnh vực mà nửa đời sau bạn thường dồn nhiều tâm sức.</p>
    <h3>Các cung nói chuyện với nhau</h3>
    <p>Mỗi cung có ba cung “họ hàng”: cung đối diện (<b>xung chiếu</b>) và hai cung cách bốn bước (<b>tam hợp</b>). Gộp bốn cung lại gọi là <b>tam phương tứ chính</b>. Khi xem Mệnh, người ta xem luôn Thiên Di, Quan Lộc và Tài Bạch.</p>
    ${call('Trên lá số của bạn, <b>bấm vào một cung</b>: các đường nối sẽ sáng lên và ngăn bên cạnh giải thích cung đó.')}` },

  'tv-3': { title: 'Các sao: chính tinh, phụ tinh, độ sáng', min: 4, sys: 'tv', body: T => `
    <p>Có hơn một trăm sao, nhưng người mới chỉ cần nhớ ba tầng:</p>
    <ul><li><b>14 chính tinh</b> — các “nhân vật chính”, quyết định màu sắc lớn của một cung.</li><li><b>Phụ tinh</b> — nhân vật phụ: <i>cát tinh</i> (thường hỗ trợ), <i>sát tinh</i> (thường gây thử thách) và nhiều sao trung tính.</li><li><b>Tứ Hóa</b> — bốn “nhãn” Lộc, Quyền, Khoa, Kỵ gắn lên bốn sao theo năm sinh (có bài riêng ở phía sau).</li></ul>
    <h3>Mười bốn chính tinh trong một dòng</h3>
    <div class="ln-grid ln-stars">${STARS14.map(s => `<div class="ln-card"><b>${s}</b><p>${esc(first(T['star:' + s]?.plain))}</p></div>`).join('')}</div>
    <h3>Độ sáng: Miếu, Vượng, Đắc, Bình, Hãm</h3>
    <p>Cùng một sao nhưng đứng ở cung khác nhau sẽ “sáng” khác nhau. Có năm mức, từ mạnh đến yếu: <b>Miếu → Vượng → Đắc → Bình → Hãm</b>. Sao sáng phát huy đặc tính tốt; sao mờ (hãm) khó phát huy hơn. Đó là mức “sáng”, không phải “số xấu”.</p>
    <h3>Vài dấu hiệu đặc biệt</h3>
    <ul><li><b>Vô chính diệu</b>: cung không có chính tinh; người ta mượn sao của cung đối diện để đọc.</li><li><b>Tuần</b> và <b>Triệt</b>: hai dấu hiệu đặt lên một cặp cung, được xem là làm sao ở đó “trống bớt” hoặc đổi sắc thái (cũng có bài riêng).</li></ul>
    ${call('<b>Mẹo.</b> Đừng học thuộc cả trăm sao. Khi gặp tên sao lạ trên lá số, bấm vào nó để đọc một dòng giải thích.')}` },

  'tv-4': { title: 'Cách đọc một lá số Tử Vi trong 5 bước', min: 4, sys: 'tv', body: () => `
    <p>Khi mở lá số, cảm giác choáng ngợp là bình thường. Hãy đọc theo thứ tự này, mỗi bước chỉ nhìn một thứ:</p>
    <ol class="ln-steps"><li><b>Cung Mệnh và cung Thân</b> — tìm hai cung này trước (Mệnh được ghi ở phần đầu lá số).</li><li><b>Chính tinh trong Mệnh và độ sáng</b> — sao nào ở đó, sáng hay mờ?</li><li><b>Tam phương tứ chính của Mệnh</b> — bấm vào cung Mệnh, xem ba cung họ hàng (Thiên Di, Quan Lộc, Tài Bạch) có sao nào nổi bật.</li><li><b>Tứ Hóa của năm sinh</b> — bốn nhãn Lộc, Quyền, Khoa, Kỵ rơi vào cung nào.</li><li><b>Đại hạn hiện tại</b> — chặng 10 năm bạn đang đi vào cung nào; chủ đề của cung đó đang được “bật sáng”.</li></ol>
    <h3>Ba nguyên tắc để không hiểu sai</h3>
    <ul><li>Một sao không nói lên điều gì khi đứng một mình: cần xem <b>độ sáng, sao đi cùng, Tuần/Triệt và vận hạn</b>.</li><li>Các nhận định đến từ nhiều sách, nhiều cung nên có thể <b>trái chiều</b>. Đó là bình thường; hãy coi chúng là các “góc nhìn”.</li><li>Đây là biểu tượng để suy ngẫm, không phải dự báo hay lời khuyên y tế, tài chính.</li></ul>
    <div class="ln-cta"><button type="button" class="btn" data-act="sample" data-tab="tuvi">Thực hành trên lá số mẫu</button></div>` },

  'tv-5': { title: 'Tứ Hóa: bốn “nhãn” Lộc, Quyền, Khoa, Kỵ', min: 3, sys: 'tv', body: T => `
    <p>Mỗi năm sinh có một Thiên can (Giáp, Ất, … Quý). Theo Can đó, bốn ngôi sao trên lá số được gắn thêm bốn “nhãn” gọi là <b>Tứ Hóa</b>. Nhãn không thay đổi bản chất của sao, chỉ <i>làm nổi bật một mặt</i> của nó.</p>
    <div class="ln-grid"><div class="ln-card"><b>Hóa Lộc</b><p>Thiên về tiền bạc, sự dễ chịu và cơ hội ở lĩnh vực của sao đó.</p></div><div class="ln-card"><b>Hóa Quyền</b><p>Thiên về quyền chủ động, địa vị và sức ảnh hưởng.</p></div><div class="ln-card"><b>Hóa Khoa</b><p>Thiên về danh tiếng, học vấn, sự được kính trọng (có tiếng chưa chắc có miếng).</p></div><div class="ln-card"><b>Hóa Kỵ</b><p>Chỗ dễ vướng mắc và lo nghĩ, cũng là điểm cần để ý hơn. Không phải bản án.</p></div></div>
    <h3>Năm sinh của bạn gắn nhãn vào sao nào?</h3>
    <p>Bảng dưới đây (theo Tử Vi Khảo Luận) cho biết bốn sao được gắn nhãn ứng với từng Can của năm sinh:</p>
    <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Can năm sinh</th><th>Lộc</th><th>Quyền</th><th>Khoa</th><th>Kỵ</th></tr></thead><tbody>${(T['x:tu-hoa-table']?.table || []).map(([n, st]) => `<tr><th scope="row">${n}</th>${st.map(x => `<td>${x}</td>`).join('')}</tr>`).join('')}</tbody></table></div>
    ${call('<b>Ví dụ.</b> Người tuổi Canh có Hóa Lộc ở Thái Dương, Hóa Quyền ở Vũ Khúc, Hóa Khoa ở Thiên Đồng và Hóa Kỵ ở Thái Âm. Muốn biết nhãn nằm ở cung nào, nhìn xem các sao đó đứng ở đâu trên lá số của bạn.')}
    <h3>Đọc Tứ Hóa thế nào cho đúng?</h3>
    <ul><li>Nhãn <b>nhấn mạnh</b> một mặt của sao, giống như tô đậm một dòng chữ. Nó không tự nói “tốt” hay “xấu”.</li><li>Cung nơi sao đứng cho biết <i>lĩnh vực</i> bị nhấn mạnh (ví dụ Hóa Lộc ở cung Tài Bạch thì chủ đề tiền bạc được “bật sáng”).</li><li>Sách có nhận xét rằng Hóa Kỵ “nặng ký” hơn các nhãn khác, nhưng Thiên Bàn không dùng điều đó để cộng điểm tốt xấu.</li></ul>
    <div class="ln-cta"><button type="button" class="btn" data-act="sample" data-tab="tuvi">Tìm Tứ Hóa trên lá số mẫu</button></div>` },

  'tv-6': { title: 'Tuần và Triệt: hai dấu hiệu đặc biệt', min: 3, sys: 'tv', body: () => `
    <p>Trên một số lá số, hai cung liền nhau được đánh dấu <b>Tuần</b> hoặc <b>Triệt</b> (có thể có cả hai, ở hai cặp cung khác nhau). Đây là hai “dấu” riêng, không phải sao.</p>
    <div class="ln-cmp"><div><h4>Tuần</h4><p>Cặp cung bị “bỏ trống” theo vòng Can Chi của năm sinh (truyền thống gọi là tuần không). Tượng trưng cho sức mạnh của sao ở đó bị <i>mờ đi hoặc đổi sắc thái</i>.</p></div><div><h4>Triệt</h4><p>Cặp cung bị “cắt ngang” tính theo Can của năm sinh. Tượng trưng cho sức mạnh của sao ở đó bị <i>cắt giảm hoặc đổi hướng</i>.</p></div></div>
    <h3>Điều cần nhớ</h3>
    <ul><li>Tuần và Triệt <b>không tự động làm cung xấu đi</b>. Truyền thống còn cho rằng chúng có thể làm dịu sao gây thử thách ở cung đó.</li><li>Các trường phái tính và luận khác nhau về Tuần, Triệt. Thiên Bàn chỉ đánh dấu cặp cung và không cố đưa ra một kết luận chung.</li><li>Khi đọc một cung, hãy hỏi thêm: cung này có Tuần hoặc Triệt không? Nếu có, hãy đọc các sao ở đó <i>thận trọng hơn</i>.</li></ul>
    ${call('Một sao “vô chính diệu” (cung không có chính tinh) khác với cung bị Tuần hoặc Triệt: cung vô chính diệu không có sao lớn, còn cung có Tuần hoặc Triệt vẫn có sao nhưng được đọc theo cách khác.')}
    <div class="ln-cta"><button type="button" class="btn" data-act="sample" data-tab="tuvi">Tìm Tuần, Triệt trên lá số mẫu</button></div>` },

  'tv-7': { title: 'Đại hạn, tiểu hạn: lá số theo thời gian', min: 4, sys: 'tv', body: () => `
    <p>Lá số gốc là bức tranh cố định. Để nói về thời gian, Tử Vi dùng các “chặng”:</p>
    <h3>Đại hạn: chặng 10 năm</h3>
    <p>Cuộc đời được chia thành các chặng 10 năm. Mỗi chặng <b>đi vào một cung</b>, nên chủ đề của cung đó được “bật sáng” trong cả chặng. Hai điều cần biết:</p>
    <ul><li><b>Bắt đầu lúc mấy tuổi?</b> Do <b>Cục</b> quyết định. Ví dụ Hỏa lục cục thì chặng đầu bắt đầu ở tuổi 6 (6–15), rồi 16–25, 26–35…</li><li><b>Đi thuận hay nghịch?</b> Tùy năm sinh và giới tính: các chặng lần lượt đi qua các cung theo chiều thuận hoặc ngược.</li></ul>
    <h3>Tiểu hạn: mỗi năm một cung</h3>
    <p>Trong từng năm, có thêm một cung được chọn làm <b>tiểu hạn</b>, cho biết chủ đề thường nổi lên trong năm đó. Cùng với năm Can Chi của năm đó (<b>lưu niên</b>) và các “nhãn” Tứ Hóa của năm, đây là cách Tử Vi nói về một năm cụ thể.</p>
    ${call('<b>Tuổi mụ</b> là cách tính tuổi ta: lấy năm xem trừ năm sinh rồi cộng 1. Các chặng đại hạn được tính theo tuổi này.')}
    <h3>Cách dùng đúng</h3>
    <ul><li>Đại hạn và tiểu hạn cho biết <i>chủ đề nào đang nổi</i>, không cho biết chuyện gì sẽ xảy ra.</li><li>Cùng một cung có thể nổi lên theo cả hướng thuận lợi lẫn thử thách, tùy sao trong cung và các sao khác.</li><li>Thiên Bàn chỉ nêu các dữ kiện này, cùng một vài điều kiện mà sách nêu rõ.</li></ul>
    <div class="ln-cta"><button type="button" class="btn" data-act="sample" data-tab="tuvi">Xem đại hạn trên lá số mẫu</button></div>` },

  'bt-1': { title: 'Bát Tự là gì? Tám chữ của bạn', min: 3, sys: 'bt', body: () => `
    <p>Bát Tự (“tám chữ”) còn gọi là Tứ Trụ. Từ <b>năm, tháng, ngày, giờ sinh</b>, ta có bốn “trụ”; mỗi trụ gồm hai chữ: một <b>Thiên can</b> (ở trên) và một <b>Địa chi</b> (ở dưới). Bốn trụ × hai chữ = tám chữ.</p>
    <div class="ln-cmp"><div><h4>Trụ Năm</h4><p>Gốc rễ, gia đình, bối cảnh.</p></div><div><h4>Trụ Tháng</h4><p>Cha mẹ, môi trường làm việc, “mùa” của lá số.</p></div><div><h4>Trụ Ngày</h4><p>Chính bạn và bạn đời. Chữ trên cùng là <b>Nhật Chủ</b>.</p></div><div><h4>Trụ Giờ</h4><p>Con cái, thành quả về sau, nội tâm.</p></div></div>
    <p>Điểm khác với Tử Vi: Bát Tự lấy tháng theo <b>tiết khí</b> (vị trí của Mặt Trời), không theo mùng một âm lịch.</p>
    ${call('<b>Nhật Chủ</b> là chữ quan trọng nhất: nó đại diện cho “bản thân bạn”. Mọi chữ khác được so với nó để biết chúng đóng vai gì với bạn.')}
    <div class="ln-cta"><button type="button" class="btn" data-act="sample" data-tab="bazi">Xem bốn trụ trên lá số mẫu</button></div>` },

  'bt-2': { title: 'Tứ Trụ, Can Chi và Ngũ Hành', min: 4, sys: 'bt', body: T => `
    <h3>Mười Thiên can: mười “hình ảnh”</h3>
    <p>Mỗi Thiên can là một hình ảnh thiên nhiên, thuộc một hành và mang tính âm hoặc dương:</p>
    <div class="ln-grid">${['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý'].map(s => `<div class="ln-card"><b>${s}</b><span class="muted small">${esc(T['can:' + s]?.facts?.map(f => f[1]).join(' · '))}</span><p>${esc(T['can:' + s]?.plain)}</p></div>`).join('')}</div>
    <h3>Mười hai Địa chi: giờ, tháng và con giáp</h3>
    <p>Địa chi là mười hai con giáp: Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi. Mỗi chi ứng với một khung giờ hai tiếng (Tý là 23h–1h) và một tháng.</p>
    <h3>Ngũ Hành: năm kiểu vận động</h3>
    <p>Mộc, Hỏa, Thổ, Kim, Thủy nối nhau bằng hai vòng:</p>
    <ul><li><b>Tương sinh</b> (nuôi dưỡng): Mộc → Hỏa → Thổ → Kim → Thủy → Mộc.</li><li><b>Tương khắc</b> (kiềm chế): Mộc → Thổ → Thủy → Hỏa → Kim → Mộc.</li></ul>
    ${call('<b>Sinh không phải lúc nào cũng tốt, khắc không phải lúc nào cũng xấu.</b> Quá nhiều một hành, hoặc thiếu một hành, đều chỉ là những dữ kiện về sự cân bằng.')}
    <p>Tám chữ trên lá số sẽ cho bạn một phép đếm: bao nhiêu chữ Mộc, Hỏa, Thổ, Kim, Thủy. Đó là bức tranh cân bằng ngũ hành của bạn.</p>` },

  'bt-3': { title: 'Nhật Chủ và Thập Thần', min: 4, sys: 'bt', body: T => `
    <p>Sau khi biết <b>Nhật Chủ</b> (bạn), ta hỏi: <i>mỗi chữ còn lại đóng vai gì đối với bạn?</i> Tên gọi của các vai ấy là <b>Thập Thần</b> (mười vai). Cách xác định chỉ dựa vào hai điều: chữ đó thuộc hành nào so với Nhật Chủ, và cùng hay khác âm dương.</p>
    <h3>Năm nhóm, mỗi nhóm hai vai</h3>
    <div class="ln-grid">${[['Tỉ Kiếp', 'Tỉ Kiên, Kiếp Tài'], ['Thực Thương', 'Thực Thần, Thương Quan'], ['Tài', 'Thiên Tài, Chính Tài'], ['Quan Sát', 'Thất Sát, Chính Quan'], ['Ấn', 'Thiên Ấn, Chính Ấn']].map(([g, m]) => `<div class="ln-card"><b>${g}</b><span class="muted small">${m}</span><p>${esc(T['gg:' + g]?.plain)}</p></div>`).join('')}</div>
    <h3>Mười vai cụ thể</h3>
    <div class="ln-grid">${GODS.map(g => `<div class="ln-card"><b>${g}</b><p>${esc(first(T['god:' + g]?.plain))}</p></div>`).join('')}</div>
    <h3>Tàng can</h3>
    <p>Dưới mỗi Địa chi còn “ẩn” từ một đến ba Thiên can (<b>tàng can</b>), giống các thành phần cấu tạo nên chi đó. Chúng cũng được gán Thập Thần, nên số vai trong lá số nhiều hơn số chữ nhìn thấy.</p>
    ${call('<b>Đừng vội kết luận.</b> Một vai xuất hiện nhiều chưa nói “tốt” hay “xấu”: còn tùy tháng sinh, sức mạnh của Nhật Chủ và các chữ đi cùng. Thiên Bàn chỉ nêu vị trí và số lượng các vai, và chỉ đưa ra nhận định khi có quy tắc đã đối chiếu sách.')}` },

  'bt-4': { title: 'Tương tác giữa các chữ và Đại vận', min: 4, sys: 'bt', body: () => `
    <h3>Hợp, xung, hại, phá, hình</h3>
    <p>Các chữ trong lá số không đứng yên mà “tác động” lên nhau. Có vài kiểu quan hệ chính:</p>
    <ul><li><b>Hợp</b>: hai chữ kéo về nhau (như hai người bắt tay).</li><li><b>Xung</b>: hai chữ đối nhau (như hai bên đối đầu).</li><li><b>Hại, phá, hình</b>: những kiểu cản trở nhẹ hơn, kéo xuống hoặc làm lệch.</li></ul>
    <p>Mỗi quan hệ chỉ cho biết “có tương tác”. Nó có thực sự “hợp hóa” hay có lực mạnh hay không còn nhiều điều kiện, và hệ thống nói rõ khi chưa xét điều đó.</p>
    <h3>Đại vận và lưu niên: lá số theo thời gian</h3>
    <ul><li><b>Đại vận</b>: các chặng 10 năm, mỗi chặng có một Can Chi riêng.</li><li><b>Lưu niên</b>: Can Chi của từng năm.</li></ul>
    <p>Mỗi Can Chi mới được đặt cạnh tám chữ gốc để xem nó “chạm” vào chữ nào, nên cùng một lá số có thể có “không khí” khác nhau ở từng giai đoạn.</p>
    ${call('Các thông tin theo thời gian trên Thiên Bàn là <b>dữ kiện cấu trúc</b>, không phải dự đoán sự kiện sẽ xảy ra.')}
    <div class="ln-cta"><button type="button" class="btn" data-act="sample" data-tab="bazi">Xem đại vận trên lá số mẫu</button></div>` },
};

export const ORDER = TRACKS.flatMap(t => t.levels.flatMap(l => l.lessons));
export const lessonTitle = id => LESSONS[id]?.title;
export const lessonSys = id => LESSONS[id]?.sys || 'tv';

/** Renders the learning hub (id = null) or one lesson into host. */
export function renderLearn(host, id, T) {
  if (!id || !LESSONS[id]) {
    host.innerHTML = `<header class="ln-hero"><p class="eyebrow">Học từ đầu</p><h1>Hiểu Tử Vi và Bát Tự<br>không cần biết trước gì</h1><p class="sec-sub">Hai lộ trình ngắn, mỗi bài 2–4 phút, đi từ khái niệm cơ bản tới cách tự đọc một lá số. Từ nào lạ, bạn đều có thể bấm để xem giải thích ngay tại chỗ.</p>
      <p><a class="btn" href="#hoc/gioi-thieu" data-go="hoc/gioi-thieu">Bắt đầu: Tử Vi hay Bát Tự?</a></p></header>
      <div class="ln-tracks">${TRACKS.filter(t => t.id !== 'start').map(t => `<section class="ln-track" aria-labelledby="ln-${t.id}"><h2 id="ln-${t.id}">${t.title}</h2><p class="muted">${t.sub}</p>
        ${t.levels.map(l => `<div class="ln-level"><h3>${l.name}</h3><ol>${l.lessons.map(x => `<li><a href="#hoc/${x}" data-go="hoc/${x}"><b>${LESSONS[x].title}</b><span>${LESSONS[x].min} phút đọc</span></a></li>`).join('')}</ol></div>`).join('')}</section>`).join('')}</div>`;
    return;
  }
  const L = LESSONS[id], i = ORDER.indexOf(id), prev = ORDER[i - 1], next = ORDER[i + 1];
  const track = TRACKS.find(t => t.levels.some(l => l.lessons.includes(id))), level = track.levels.find(l => l.lessons.includes(id));
  host.innerHTML = `<div class="ln-page">
    <nav class="ln-crumb" aria-label="Vị trí bài học"><a href="#hoc" data-go="hoc">Học</a> › <span>${track.title}</span> › <span>${level.name}</span></nav>
    <article class="ln-art"><p class="eyebrow">Bài ${i + 1} / ${ORDER.length} · ${L.min} phút đọc</p><h1>${L.title}</h1><div class="ln-body">${L.body(T)}</div></article>
    <nav class="ln-pn" aria-label="Chuyển bài">${prev ? `<a href="#hoc/${prev}" data-go="hoc/${prev}"><small>← Bài trước</small>${LESSONS[prev].title}</a>` : '<span></span>'}${next ? `<a class="nx" href="#hoc/${next}" data-go="hoc/${next}"><small>Bài tiếp theo →</small>${LESSONS[next].title}</a>` : `<a class="nx" href="#lap-la-so" data-go="lap-la-so"><small>Bạn đã học xong</small>Lập lá số của bạn →</a>`}</nav>
  </div>`;
}
