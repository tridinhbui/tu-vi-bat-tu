// The account page (#tai-khoan): Thông tin cá nhân, Lá số của tôi, Quyền riêng tư. Signed out it only offers the Google sign-in.
import { $, $$ } from './util.js';
import { api, session } from './account.js';
import { initProfile } from './profile.js';
import { initMyCharts } from './mycharts.js';
import { writeSaved } from './mine.js';

const CONFIRM = 'XOA';      // src/account/route.ts checks the same word
/** Everything this site keeps in this browser (saved charts, journal, remembered choices) starts with "tvbt". */
function clearDevice() {
  for (const s of [localStorage, sessionStorage]) {
    try { Object.keys(s).filter(k => k.startsWith('tvbt')).forEach(k => s.removeItem(k)); } catch { /* storage unavailable */ }
  }
}

/** deps: { placeOptions, onPrefill(profile), onRun(profile), onOpen(req), compare, onChange() } */
export function initAccountPage(root, deps) {
  root.innerHTML = `<section class="acc-mast"><div class="wrap"><p class="eyebrow">Tài khoản</p><h1>Tài khoản của bạn</h1><p class="acc-who muted"></p>
      <nav class="acc-nav" aria-label="Các phần của trang tài khoản"><a href="#acc-profile">Thông tin cá nhân</a><a href="#acc-charts">Lá số của tôi</a><a href="#acc-privacy">Quyền riêng tư</a></nav></div></section>
    <div class="acc-out wrap" hidden><p>Đăng nhập để lưu thông tin cá nhân, đồng bộ lá số và tạo liên kết chia sẻ.</p><a class="btn" href="/api/auth/google">Đăng nhập với Google</a></div>
    <div class="acc-in" hidden>
      <section class="wrap acc-sec" id="acc-profile" aria-labelledby="acc-profile-h"><h2 id="acc-profile-h">Thông tin cá nhân</h2><p class="sec-sub">Dùng để điền sẵn ô lập lá số và sắp xếp các chương bạn quan tâm lên trước khi xem lá số của chính bạn.</p><div data-profile></div></section>
      <section class="wrap acc-sec" id="acc-charts" aria-labelledby="acc-charts-h"><h2 id="acc-charts-h">Lá số của tôi</h2><p class="sec-sub">Lá số của bạn, người thân và bạn bè. Mở lại, đổi tên, chia sẻ, xóa, hoặc chọn hai lá số để so sánh.</p><div data-charts></div></section>
      <section class="wrap acc-sec" id="acc-privacy" aria-labelledby="acc-privacy-h"><h2 id="acc-privacy-h">Quyền riêng tư</h2>
        <p class="sec-sub">Đọc <a class="link" href="/privacy">Chính sách dữ liệu</a> để biết hệ thống giữ gì và vì sao.</p>
        <div class="acc-danger">
          <div><h3>Xóa toàn bộ dữ liệu</h3><p>Xóa thông tin cá nhân, mọi lá số đã lưu, liên kết chia sẻ, các bản luận giải sâu đã mua và góp ý bạn đã gửi khi đăng nhập. Tài khoản, số xu và lịch sử giao dịch được giữ lại. Lá số trên máy này cũng bị xóa.</p>
            <form data-wipe="data"><label>Gõ <b>${CONFIRM}</b> để xác nhận<input name="confirm" autocomplete="off" spellcheck="false"></label><button class="btn btn-sm mc-del" disabled>Xóa dữ liệu</button><span class="muted small" role="status"></span></form></div>
          <div><h3>Xóa tài khoản</h3><p>Xóa mọi thứ ở mục bên cạnh, cùng với tài khoản, số xu còn lại và lịch sử giao dịch, rồi đăng xuất. Không hoàn tác được; số xu chưa dùng sẽ mất. Đăng nhập lại bằng Google sau đó sẽ tạo một tài khoản mới, trống.</p>
            <form data-wipe="account"><label>Gõ <b>${CONFIRM}</b> để xác nhận<input name="confirm" autocomplete="off" spellcheck="false"></label><button class="btn btn-sm mc-del" disabled>Xóa tài khoản</button><span class="muted small" role="status"></span></form></div>
        </div></section>
    </div>`;
  const profile = initProfile($('[data-profile]', root), deps);
  const charts = initMyCharts($('[data-charts]', root), deps);
  $$('.acc-nav a', root).forEach(a => a.onclick = e => { e.preventDefault(); $(a.getAttribute('href'), root)?.scrollIntoView({ behavior: 'smooth', block: 'start' }); });
  $$('[data-wipe]', root).forEach(f => {
    const btn = $('button', f), st = $('[role=status]', f);
    f.confirm.oninput = () => { btn.disabled = f.confirm.value.trim().toUpperCase() !== CONFIRM; };
    f.onsubmit = async e => {
      e.preventDefault(); btn.disabled = true; st.textContent = 'Đang xóa…';
      const r = await api(f.dataset.wipe === 'account' ? '/api/me/account' : '/api/me/data', { method: 'POST', body: JSON.stringify({ confirm: CONFIRM }) }).catch(() => null);
      if (!r?.ok) { st.textContent = 'Chưa xóa được, vui lòng thử lại.'; btn.disabled = false; return; }
      clearDevice();
      if (f.dataset.wipe === 'account') { location.replace('/'); return; }
      writeSaved([]); profile.reset(); deps.onChange(); charts.paint(); f.reset(); st.textContent = 'Đã xóa.';
    };
  });
  const paint = () => {
    const signed = !!session.user;
    $('.acc-out', root).hidden = signed || !session.ready; $('.acc-in', root).hidden = !signed;
    $('.acc-nav', root).hidden = !signed;
    $('.acc-who', root).textContent = signed ? `Đăng nhập bằng ${session.user.email}` : session.ready && !session.enabled ? 'Tài khoản chưa được bật trên máy chủ này.' : '';
    if (session.ready && !session.enabled) $('.acc-out', root).hidden = true;
  };
  paint(); addEventListener('tvbt:account', paint);
  return { paint: () => { paint(); charts.paint(); } };
}
