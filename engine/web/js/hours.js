// Unknown birth hour: show what is independent of the hour and what each of the 12 hours would give.
import { esc, BRANCHES } from './util.js';
import { notice } from './ui.js';

export function renderHourSweep(host, sweep, onPick) {
  const h = sweep.hours, same = k => new Set(h.map(x => x.pillars[k])).size === 1;
  const fixed = ['year', 'month', 'day'].filter(same).map(k => ({ year: 'Trụ Năm', month: 'Trụ Tháng', day: 'Trụ Ngày' }[k] + ' ' + h[0].pillars[k]));
  const dayVaries = !same('day');
  host.innerHTML = `
    <div class="hr-split">
      <div class="card-soft"><p class="eyebrow">Không phụ thuộc giờ sinh</p><ul class="plain hr-l">${fixed.map(x => `<li>${esc(x)}</li>`).join('')}<li>Âm lịch và Can Chi của năm (Tử Vi)</li>${same('day') ? `<li>Nhật Chủ (Thiên can trụ Ngày)</li>` : ''}</ul>${dayVaries ? notice('Trụ Ngày đổi theo giờ', 'Ngày sinh nằm sát ranh giới giờ Tý (23h) nên trụ Ngày còn phụ thuộc quy ước giờ Tý ở phần cài đặt nâng cao.') : ''}</div>
      <div class="card-soft"><p class="eyebrow">Đổi theo giờ sinh</p><ul class="plain hr-l"><li>Trụ Giờ của Bát Tự và Thập thần của nó</li><li>Cung Mệnh và cung Thân của Tử Vi</li><li>Cục, vị trí Tử Vi, và vì thế toàn bộ sao trên lá số</li><li>Văn Xương, Văn Khúc, Địa Không, Địa Kiếp, Hỏa Tinh, Linh Tinh...</li></ul></div>
    </div>
    <div class="tbl-wrap"><table class="tbl hr-t"><thead><tr><th>Giờ</th><th>Trụ Giờ</th><th>Mệnh cung</th><th>Thân cư</th><th>Cục</th><th>Chính tinh ở Mệnh</th><th></th></tr></thead><tbody>
      ${h.map((x, i) => `<tr><th scope="row">${esc(x.hour_branch)} <small>${esc(x.range)}</small></th><td>${esc(x.pillars.hour)}</td><td>${esc(x.menh_stem)} ${esc(x.menh_branch)}</td><td>${esc(x.than_palace)}</td><td>${esc(x.cuc)}</td><td>${esc(x.menh_major_stars.join(', ') || 'vô chính diệu')}</td><td><button type="button" class="btn btn-ghost btn-sm" data-i="${i}">Xem lá số</button></td></tr>`).join('')}
    </tbody></table></div>
    <p class="muted small">Gợi ý: nếu chỉ nhớ “sinh buổi sáng”, “gần trưa”... hãy xem các giờ liền kề và so sánh các cung Mệnh có phù hợp với bản thân hay không. Hệ thống không đoán giờ sinh hộ bạn.</p>`;
  host.querySelectorAll('button[data-i]').forEach(b => b.onclick = () => onPick(h[+b.dataset.i]));
}
