// Google sign-in and saved-chart sync. Reading charts works signed out; saving, the chat assistant, sharing and the profile are for members.
import { $ } from './util.js';
import { cloud, readSaved, writeSaved } from './mine.js';

export const api = (path, opts = {}) => fetch(path, { credentials: 'same-origin', ...opts, headers: { 'x-tvbt': '1', 'content-type': 'application/json', ...(opts.headers || {}) } });

/** Who is signed in, once /api/auth/me has answered; the 'tvbt:account' event fires then (profile.js, mycharts.js listen). */
export const session = { ready: false, enabled: false, user: null };
const announce = () => { session.ready = true; dispatchEvent(new CustomEvent('tvbt:account', { detail: session })); };

/** Sends one saved chart now and waits for the server's copy (a share link needs the chart to exist on the server). */
export const syncItem = item => sync([item]).then(list => { writeSaved(list); return list.find(x => x.id === item.id) || list.find(x => ['year', 'month', 'day', 'hour', 'minute', 'gender'].every(k => x.req[k] === item.req[k])); });

async function sync(list) {
  const r = await api('/api/me/charts/sync', { method: 'POST', body: JSON.stringify({ charts: list }) });
  if (!r.ok) throw new Error(String(r.status));
  return (await r.json()).charts;
}

/** host: header slot; onSynced(): repaint anything that shows saved charts; saver: initSave handle, to refresh its wording. */
export async function initAccount(host, onSynced, saver) {
  let me;
  try { me = await (await fetch('/api/auth/me', { credentials: 'same-origin' })).json(); } catch { announce(); return; }
  session.enabled = !!me.enabled; session.user = me.user || null;
  if (!me.enabled) { announce(); return; }
  if (new URLSearchParams(location.search).get('login') === 'failed') history.replaceState(null, '', location.pathname);

  if (!me.user) {
    host.innerHTML = '<a class="btn btn-sm btn-ghost acct-in" href="/api/auth/google">Đăng nhập với Google</a>';
    cloud.needLogin = true; saver?.paint();
    announce();
    return;
  }
  cloud.on = true;
  cloud.push = item => { sync([item]).catch(() => { /* offline: the chart stays local and is sent on the next sign-in sync */ }); };
  cloud.remove = id => { api('/api/me/charts/' + encodeURIComponent(id), { method: 'DELETE' }).catch(() => {}); };
  const first = (me.user.name || me.user.email).split(' ').slice(-1)[0];
  host.innerHTML = `${me.admin ? '<a class="acct-admin" href="/admin" title="Trang quản trị">Quản trị</a>' : ''}<span class="acct-wallet" hidden></span><a class="acct-name" href="#tai-khoan" data-go="tai-khoan" title="Tài khoản: ${me.user.email.replace(/"/g, '&quot;')}"></a><button type="button" class="btn btn-sm btn-ghost acct-out">Đăng xuất</button>`;
  $('.acct-name', host).textContent = first;
  $('.acct-out', host).onclick = async () => { await api('/api/auth/logout', { method: 'POST' }).catch(() => {}); location.reload(); };
  saver?.paint();
  paintWallet($('.acct-wallet', host));
  try { writeSaved(await sync(readSaved())); onSynced(); } catch { /* keep local charts; sync retries on the next visit */ }
  announce();
}

/** A gold coin stamped with a square hole, like an old Vietnamese coin; colours follow the theme tokens in app.css (.coin). */
export const COIN_SVG = '<svg class="coin" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="10.5" class="coin-rim"/><circle cx="12" cy="12" r="8.2" class="coin-face"/><circle cx="12" cy="12" r="6.6" class="coin-ring"/><rect x="9.6" y="9.6" width="4.8" height="4.8" rx=".6" class="coin-hole"/><path d="M6.4 8.2a7 7 0 0 1 3.4-3" class="coin-shine"/></svg>';

/** "7 lượt chat miễn phí · 🪙 3 xu" next to the name (on phones only the coin and amount); the title says when the free allowance
 *  resets. Repainted when the chat panel reports a new wallet. */
async function paintWallet(el) {
  const render = w => {
    el.innerHTML = `<span class="aw-free">${Number(w.free.remaining)} lượt chat miễn phí ·</span> <span class="aw-coins">${COIN_SVG}<b>${Number(w.coins).toLocaleString('vi-VN')}</b><span class="aw-x">xu</span></span>`;
    el.setAttribute('aria-label', `${w.free.remaining} lượt chat miễn phí, ${w.coins} xu`);
    el.title = `Lượt miễn phí tháng này: ${w.free.used}/${w.free.limit}, làm mới ngày ${new Date(w.free.resetsAt).toLocaleDateString('vi-VN')}. Hết lượt miễn phí, mỗi tin nhắn tốn ${w.costs.chat} xu; luận giải bằng AI tốn ${w.costs.deep} xu một chương.`;
    el.hidden = false;
  };
  addEventListener('tvbt:wallet', e => render(e.detail));
  try {
    const r = await api('/api/me/wallet'); if (!r.ok) return;
    render(await r.json());
  } catch { /* the chip is optional */ }
}
