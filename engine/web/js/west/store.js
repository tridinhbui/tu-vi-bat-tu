// Saved profiles and recently opened charts, kept only in this browser (localStorage, every access guarded: private windows and
// blocked storage simply show an empty list). Share links carry the birth data in the #fragment, which browsers never send to a server.
const K_PROF = 'tb_west_profiles', K_RECENT = 'tb_west_recent', MAX_RECENT = 8;

const load = k => { try { const v = JSON.parse(localStorage.getItem(k) || '[]'); return Array.isArray(v) ? v : []; } catch { return []; } };
const save = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch { return false; } };
/** Same person, same moment, same place: the identity used to de-duplicate lists. */
const keyOf = b => [b.year, b.month, b.day, b.hour ?? 'x', b.minute ?? 'x', (+b.lat).toFixed(3), (+b.lon).toFixed(3), b.tz, b.fold || 0, b.utc_offset_hours ?? ''].join('|');

export const profiles = () => load(K_PROF);
export const recent = () => load(K_RECENT);

export function saveProfile(inp, label) {
  const list = profiles().filter(p => keyOf(p.birth) !== keyOf(inp.birth));
  list.unshift({ id: Date.now().toString(36), label: label || inp.birth.name || '', birth: inp.birth, options: inp.options, gender: inp.gender || null, at: new Date().toISOString() });
  return save(K_PROF, list.slice(0, 50));
}
export function deleteProfile(id) { return save(K_PROF, profiles().filter(p => p.id !== id)); }
export function remember(inp) {
  const list = recent().filter(p => keyOf(p.birth) !== keyOf(inp.birth));
  list.unshift({ birth: inp.birth, options: inp.options, gender: inp.gender || null, at: new Date().toISOString() });
  save(K_RECENT, list.slice(0, MAX_RECENT));
}
export function clearRecent() { return save(K_RECENT, []); }
export const isSaved = inp => profiles().some(p => keyOf(p.birth) === keyOf(inp.birth));

// ----- share fragment: #ban-do=<base64url(JSON)> -----
const b64u = s => btoa(String.fromCharCode(...new TextEncoder().encode(s))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const unb64u = s => new TextDecoder().decode(Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0)));
const SHORT = { year: 'y', month: 'm', day: 'd', hour: 'h', minute: 'i', lat: 'la', lon: 'lo', tz: 'z', place: 'p', name: 'n', fold: 'f', utc_offset_hours: 'u' };
export function shareUrl(inp) {
  const b = {};
  for (const [k, s] of Object.entries(SHORT)) if (inp.birth[k] != null && inp.birth[k] !== '') b[s] = inp.birth[k];
  return `${location.origin}${location.pathname}#ban-do=${b64u(JSON.stringify({ v: 1, b, o: inp.options, ...(inp.gender ? { g: inp.gender } : {}) }))}`;
}
export function readShare(hash = location.hash) {
  const m = /^#ban-do=([A-Za-z0-9_-]+)$/.exec(hash || '');
  if (!m) return null;
  try {
    const j = JSON.parse(unb64u(m[1])), birth = {};
    for (const [k, s] of Object.entries(SHORT)) if (j.b?.[s] !== undefined) birth[k] = j.b[s];
    if (birth.hour === undefined) { birth.hour = null; birth.minute = null; }
    if (![birth.year, birth.month, birth.day, birth.lat, birth.lon].every(Number.isFinite) || !birth.tz) return null;
    return { birth, options: j.o || {}, gender: j.g === 'male' || j.g === 'female' ? j.g : null };
  } catch { return null; }
}
