// Google sign-in and saved-chart sync. Everything works signed out (charts stay on this device); signing in only adds sync.
import { $ } from './util.js';
import { cloud, readSaved, writeSaved } from './mine.js';

const api = (path, opts = {}) => fetch(path, { credentials: 'same-origin', ...opts, headers: { 'x-tvbt': '1', 'content-type': 'application/json', ...(opts.headers || {}) } });

async function sync(list) {
  const r = await api('/api/me/charts/sync', { method: 'POST', body: JSON.stringify({ charts: list }) });
  if (!r.ok) throw new Error(String(r.status));
  return (await r.json()).charts;
}

/** host: header slot; onSynced(): repaint anything that shows saved charts; saver: initSave handle, to refresh its wording. */
export async function initAccount(host, onSynced, saver) {
  let me;
  try { me = await (await fetch('/api/auth/me', { credentials: 'same-origin' })).json(); } catch { return; }
  if (!me.enabled) return;
  if (new URLSearchParams(location.search).get('login') === 'failed') history.replaceState(null, '', location.pathname);

  if (!me.user) {
    host.innerHTML = '<a class="btn btn-sm btn-ghost acct-in" href="/api/auth/google">Đăng nhập với Google</a>';
    return;
  }
  cloud.on = true;
  cloud.push = item => { sync([item]).catch(() => { /* offline: the chart stays local and is sent on the next sign-in sync */ }); };
  cloud.remove = id => { api('/api/me/charts/' + encodeURIComponent(id), { method: 'DELETE' }).catch(() => {}); };
  const first = (me.user.name || me.user.email).split(' ').slice(-1)[0];
  host.innerHTML = `<span class="acct-name" title="${me.user.email.replace(/"/g, '&quot;')}"></span><button type="button" class="btn btn-sm btn-ghost acct-out">Đăng xuất</button>`;
  $('.acct-name', host).textContent = first;
  $('.acct-out', host).onclick = async () => { await api('/api/auth/logout', { method: 'POST' }).catch(() => {}); location.reload(); };
  saver?.paint();
  try { writeSaved(await sync(readSaved())); onSynced(); } catch { /* keep local charts; sync retries on the next visit */ }
}
