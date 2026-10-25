// /cung-hoang-dao/: look up the cung hoàng đạo of a birth moment with /api/hoang-dao (the engine computes; this file only draws).
import { $, esc } from './util.js';
import { hoangdaoCard } from './hoangdao.js';

const getJSON = async u => {
  for (let i = 0; i < 4; i++) {
    try {
      const r = await fetch(u);
      if (r.ok) return r.json();
      if (r.status < 500) { const b = await r.json().catch(() => ({})); throw Object.assign(new Error(typeof b.detail === 'string' ? b.detail : 'Ngày giờ chưa hợp lệ.'), { final: true }); }
    } catch (e) { if (e.final || i === 3) throw e; }
    await new Promise(r => setTimeout(r, 600 * (i + 1)));
  }
};

const f = $('#hd-form'), out = $('#hd-out');
f.d.innerHTML = Array.from({ length: 31 }, (_, i) => `<option value="${i + 1}">${i + 1}</option>`).join('');
f.m.innerHTML = Array.from({ length: 12 }, (_, i) => `<option value="${i + 1}">Tháng ${i + 1}</option>`).join('');
// the birth is never put in the page address (nothing to share or log by accident); the form starts empty each time

async function look(ev) {
  ev?.preventDefault();
  const y = +f.y.value, m = +f.m.value, d = +f.d.value, [h, mi] = (f.t.value || '12:00').split(':').map(Number);
  if (!(y >= 1900 && y <= 2049)) { out.innerHTML = '<p class="hd-err">Năm sinh cần trong khoảng 1900 đến 2049.</p>'; return; }
  if (new Date(y, m - 1, d).getMonth() !== m - 1) { out.innerHTML = '<p class="hd-err">Ngày này không có trong tháng đã chọn.</p>'; return; }
  out.innerHTML = '<p class="note">Đang tính…</p>';
  try {
    const w = await getJSON(`/api/hoang-dao?y=${y}&m=${m}&d=${d}&h=${h}&mi=${mi}&tz=${encodeURIComponent(f.tz.value)}`);
    out.innerHTML = hoangdaoCard(w, { heading: 'h2' }) + (f.t.value ? '' : '<p class="note">Bạn chưa nhập giờ sinh nên hệ thống lấy 12:00 trưa. Nếu ghi chú "sinh sát ranh giới" hiện ra, hãy nhập giờ sinh để biết chắc.</p>');
  } catch (e) { out.innerHTML = `<p class="hd-err">${esc(e.message || 'Chưa tính được, thử lại sau.')}</p>`; }
}
f.onsubmit = look;
