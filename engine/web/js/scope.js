// ScopePanel: says plainly what the chart contains, what is not computed and why.
import { esc } from './util.js';

const SCOPE = [
  [/Tuần\/Triệt/, 'Các biến thể Tuần/Triệt giữa các trường phái chưa được so sánh.'],
  [/late-T/i, 'Trường hợp sinh giờ Tý muộn (23h) theo quy ước “cùng ngày” chưa xử lý ở mép ngày âm lịch.'],
];
export const scopeText = u => (SCOPE.find(([re]) => re.test(u)) || [0, u])[1];

export function scopePanelTuvi(t) {
  const names = [...new Set(t.palaces.flatMap(p => p.stars))];
  const unv = new Set(t.stars.filter(s => /chưa đối chiếu/.test(s.group)).map(s => s.name));
  const hoa = Object.keys(t.tu_hoa).length;
  const rest = t.unsupported.map(scopeText);
  return `<details class="sc" id="scope-tv"><summary><span class="sc-n">${names.length}</span><span><b>sao đã được an</b> trên lá số này: ${names.length - unv.size} theo bảng đã đối chiếu sách, ${unv.size} theo công thức phổ biến chưa đối chiếu</span><span class="muted small">Xem chi tiết</span></summary>
    <h5>Đã đối chiếu sách</h5><ul><li>14 chính tinh, Tả Hữu, Xương Khúc, Khôi Việt, Lộc Tồn, Kình Đà, Thiên Mã, Hỏa Linh, Không Kiếp, Thiên Không, Đào Hồng Hỷ, Tuần Triệt, ba vòng sao (Thái Tuế, Lộc Tồn, Trường Sinh), Tứ Hóa và đại hạn.</li><li>Độ sáng (miếu, vượng, đắc, bình, hãm) theo bảng đang chọn ở ô "Bảng độ sáng" (mặc định Khảo Luận, như các bảng lá số phổ biến); ô nào không có nhãn nghĩa là bảng đó không ghi vị trí ấy.</li><li>Ba mục các sách tính khác nhau (Tứ Hóa, tiểu hạn, Lưu Hà) ghi rõ theo sách nào trong ô "Tính theo sách nào" dưới bảng lá số.</li></ul>
    <h5>Theo công thức phổ biến, chưa đối chiếu sách (gạch chân chấm)</h5><p>${[...unv].map(esc).join(', ') || 'không có'}. Vị trí của các sao này có thể được kiểm tra lại khi có nguồn; chưa có quy tắc luận giải nào dùng chúng.</p>
    <h5>Lớp năm và tháng: đã tính gì, đã luận gì</h5><ul>${rest.map(x => `<li>${esc(x)}</li>`).join('')}</ul>
    <p class="muted small">Một lá số đầy đủ theo truyền thống có hơn một trăm sao. Hệ thống ưu tiên đúng và có nguồn hơn là đủ, nên các sao chưa chắc công thức bị bỏ trống thay vì an đại.</p></details>`;
}

// What the Bát Tự reading covers, as it stands since Track C and the 2026-10-22 audit (S2, BZ-13): this text used to say that strength,
// cách cục, dụng thần, thần sát and nạp âm were not computed, while the report showed them.
export function scopePanelBazi(b) {
  return `<details class="sc" id="scope-bz" open><summary><span class="sc-n">8</span><span><b>chữ</b> trên bốn trụ, cùng tàng can, Thập thần, đại vận và các quan hệ Can Chi</span><span class="muted small">Phạm vi luận giải</span></summary>
    <h5>Đã tính và đưa vào luận giải</h5><ul>
      <li><b>Thân vượng hay nhược</b>: theo phép chấm điểm của Thiệu Vĩ Hoa (Dự Đoán Theo Tứ Trụ, tr.331-355), phe nhật chủ từ 40% trở lên là vượng, dưới 40% là nhược. Sát ngưỡng thì gọi là “hơi vượng”, “hơi nhược” như sách gọi ở ví dụ tr.355. Ba tiêu chí đắc lệnh, đắc vị, đắc sinh của 八字真宗 (tr.26) vẫn được nêu riêng.</li>
      <li><b>Cách cục và dụng thần</b>: cách lập từ chi tháng; dụng thần và vận tốt, vận xấu theo bảng của Thiệu Vĩ Hoa (tr.378-386).</li>
      <li><b>Điều hậu</b>: các can bảng điều hậu nêu cho nhật chủ và tháng sinh (tr.389-396). Chính Thiệu Vĩ Hoa ghi bảng này do một độc giả gửi, chưa rõ xuất xứ (tr.388).</li>
      <li>Khi hai bảng trên cho kết quả khác nhau ở một đại vận hay một năm, bài luận nói rõ chỗ khác và đưa ra kết luận có điều kiện, không chọn ngầm một bên.</li>
      <li><b>Thần sát</b> (八字真宗 tr.21-22), <b>không vong</b>, <b>nạp âm</b> từng trụ, <b>trường sinh</b> (tr.24-25), cung hôn nhân và cung phối ngẫu (tr.57).</li>
      <li>Quan hệ hợp, xung, hình, hại, phá, bán hợp giữa các trụ, với đại vận và lưu niên (bảng 八字真宗 tr.19-20, mười cặp can xung, khắc).</li></ul>
    <h5>Chưa đưa vào luận giải</h5><ul>
      <li>Phép phù ức và bảng cách cục riêng của bộ máy: chưa có trang sách làm căn cứ.</li>
      <li>Ý nghĩa của hợp, xung, hình, hại, phá: sách chỉ in bảng, nên bài chỉ nêu vị trí.</li>
      <li>Việc “hợp hóa” của các can đứng xa nhau: Thiệu Vĩ Hoa chỉ xét hóa khi hai can kề nhau (tr.336-338).</li>
      <li>Lưu nguyệt, và sức vượng nhược riêng trong từng đại vận, lưu niên: chưa có phép tương ứng trong sách.</li></ul></details>`;
}
