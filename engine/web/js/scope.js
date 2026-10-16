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
    <h5>Đã đối chiếu sách</h5><ul><li>14 chính tinh, Tả Hữu, Xương Khúc, Khôi Việt, Lộc Tồn, Kình Đà, Thiên Mã, Hỏa Linh, Không Kiếp, Thiên Không, Đào Hồng Hỷ, Tuần Triệt, ba vòng sao (Thái Tuế, Lộc Tồn, Trường Sinh), Tứ Hóa và đại hạn.</li><li>Độ sáng (miếu, vượng, đắc, bình, hãm) của chính tinh theo bảng Tử Vi Thực Hành; ô nào không có nhãn nghĩa là bảng chưa ghi vị trí đó.</li></ul>
    <h5>Theo công thức phổ biến, chưa đối chiếu sách (gạch chân chấm)</h5><p>${[...unv].map(esc).join(', ') || 'không có'}. Vị trí của các sao này có thể được kiểm tra lại khi có nguồn; chưa có quy tắc luận giải nào dùng chúng.</p>
    <h5>Chưa được an hoặc chưa xử lý</h5><ul>${rest.map(x => `<li>${esc(x)}</li>`).join('')}</ul>
    <p class="muted small">Một lá số đầy đủ theo truyền thống có hơn một trăm sao. Hệ thống ưu tiên đúng và có nguồn hơn là đủ, nên các sao chưa chắc công thức bị bỏ trống thay vì an đại.</p></details>`;
}

export function scopePanelBazi(b) {
  return `<details class="sc" id="scope-bz" open><summary><span class="sc-n">8</span><span><b>chữ</b> trên bốn trụ, cùng tàng can, Thập thần, đại vận và các quan hệ Can Chi</span><span class="muted small">Phạm vi luận giải</span></summary>
    <h5>Vì sao chưa kết luận “thân vượng” hay “thân nhược”</h5>
    <p>Sách 八字真宗 (tr.26) nêu ba tiêu chí xét một hành mạnh hay yếu: đắc lệnh, đắc vị, đắc sinh, nhưng không đưa ngưỡng để cộng thành một nhãn. Nếu hệ thống tự đặt ngưỡng, kết quả sẽ phụ thuộc vào con số do chúng tôi chọn chứ không phải lời sách. Vì vậy từng tiêu chí được nêu riêng ở chương <i>Nhật Chủ & tính cách</i> và việc gộp lại để bạn hoặc thầy của bạn tự cân nhắc.</p>
    <h5>Cũng chưa kết luận</h5><ul><li><b>Cách cục</b> và <b>Dụng thần</b>: phụ thuộc trường phái và cần bộ quy tắc đã đối chiếu nguồn, hiện chưa có.</li><li><b>Thần sát</b> (Thiên Ất quý nhân, Đào hoa, Dịch mã...), <b>Không vong</b> theo trụ và <b>nạp âm</b> từng trụ: chưa được an.</li><li>Việc “hợp hóa”: quan hệ hợp chỉ được ghi là tiềm năng, chưa xét điều kiện hóa.</li></ul></details>`;
}
