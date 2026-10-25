// Google sign-in and saved-chart sync. Reading charts works signed out; saving, the chat assistant, sharing and the profile are for members.
import { cloud, readSaved, writeSaved } from './mine.js';
import { authMe, COIN_SVG } from './nav.js';

export { COIN_SVG };

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

/** onSynced(): repaint anything that shows saved charts; saver: initSave handle, to refresh its wording. The header's account card,
 *  sign-in button and wallet are js/nav.js (every page); this keeps the session and the saved-chart sync. */
export async function initAccount(onSynced, saver) {
  const me = await authMe;
  if (!me) { announce(); return; }
  session.enabled = !!me.enabled; session.user = me.user || null;
  if (!me.enabled) { announce(); return; }
  if (new URLSearchParams(location.search).get('login') === 'failed') history.replaceState(null, '', location.pathname);

  if (!me.user) {
    cloud.needLogin = true; saver?.paint();
    announce();
    return;
  }
  cloud.on = true;
  cloud.push = item => { sync([item]).catch(() => { /* offline: the chart stays local and is sent on the next sign-in sync */ }); };
  cloud.remove = id => { api('/api/me/charts/' + encodeURIComponent(id), { method: 'DELETE' }).catch(() => {}); };
  saver?.paint();
  try { writeSaved(await sync(readSaved())); onSynced(); } catch { /* keep local charts; sync retries on the next visit */ }
  announce();
}
