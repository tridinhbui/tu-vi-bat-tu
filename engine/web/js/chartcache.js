// A chart already built on this device opens again without rebuilding: the engine results for one request (and one account, since the
// member tier changes what the server sends) are kept in IndexedDB for a few hours. "Mở" in Lá số của tôi and a page reload then draw the
// chart at once. Stale copies expire, and anything that changes what the server would send (a bought Đọc sâu) asks for a fresh build.
// The chart on screen is also remembered for this tab (sessionStorage), so a reload of #la-so/... comes back to it instead of the form.
const DB = 'tvbt-charts', STORE = 'results', TTL = 12 * 3600e3, CURRENT = 'tvbt.current';

let dbp = null;
const open = () => dbp ??= new Promise((res, rej) => {
  const r = indexedDB.open(DB, 1);
  r.onupgradeneeded = () => r.result.createObjectStore(STORE);
  r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error);
}).catch(() => null);
const tx = async (mode, fn) => {
  const db = await open(); if (!db) return null;
  return new Promise(res => { const s = db.transaction(STORE, mode).objectStore(STORE), r = fn(s); r.onsuccess = () => res(r.result); r.onerror = () => res(null); });
};

/** one key per request and account: field order does not matter */
export const cacheKey = (req, user) => JSON.stringify([user || '', Object.keys(req).sort().map(k => [k, req[k]])]);

export async function cachedChart(key) {
  try { const v = await tx('readonly', s => s.get(key)); return v && Date.now() - v.at < TTL ? v.state : null; } catch { return null; }
}
export async function cacheChart(key, state) {
  try {
    await tx('readwrite', s => s.put({ at: Date.now(), state }, key));
    // drop expired entries now and then so the store stays small
    if (Math.random() < .2) {
      const db = await open(), r = db?.transaction(STORE, 'readwrite').objectStore(STORE).openCursor();
      if (r) r.onsuccess = () => { const c = r.result; if (!c) return; if (Date.now() - c.value.at >= TTL) c.delete(); c.continue(); };
    }
  } catch { /* storage unavailable: the chart is simply built again next time */ }
}

export function rememberCurrent(req, lunarIn) { try { sessionStorage.setItem(CURRENT, JSON.stringify({ req, lunarIn })); } catch { /* storage unavailable */ } }
export function forgetCurrent() { try { sessionStorage.removeItem(CURRENT); } catch { /* storage unavailable */ } }
export function currentChart() { try { return JSON.parse(sessionStorage.getItem(CURRENT) || 'null'); } catch { return null; } }
