// /api/west/* calls. Like util.post, but keeps the HTTP status so a missing endpoint (the reading layer before it ships) can be told
// apart from a rejected birth (422, whose Vietnamese `detail` is shown in the form as is).
const sleep = ms => new Promise(r => setTimeout(r, ms));

export class ApiError extends Error {
  constructor(msg, status) { super(msg); this.status = status; }
}

export async function westPost(path, body, { retries = 2 } = {}) {
  let last;
  for (let i = 0; i <= retries; i++) {
    try {
      const r = await fetch('/api/west/' + path, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });
      let j = {};
      try { j = await r.json(); } catch { /* non-JSON error body */ }
      if (r.ok) return j;
      if (r.status < 500) {
        const d = j.detail;
        const msg = typeof d === 'string' ? d.replace(/^./, c => c.toLocaleUpperCase('vi'))
          : Array.isArray(d) ? 'Dữ liệu chưa hợp lệ: ' + d.map(x => (x.loc || []).slice(-1)[0]).filter(Boolean).join(', ') + '.'
          : r.status === 404 || r.status === 405 ? 'Chức năng này chưa có trên máy chủ.' : 'Yêu cầu chưa hợp lệ.';
        throw new ApiError(msg, r.status);
      }
      last = new ApiError('Máy chủ chưa phản hồi. Vui lòng thử lại.', r.status);
    } catch (e) {
      if (e instanceof ApiError && e.status < 500) throw e;
      last = e instanceof ApiError ? e : new ApiError('Không kết nối được máy chủ. Vui lòng thử lại.', 0);
    }
    if (i < retries) await sleep(400 * (i + 1));
  }
  throw last;
}

/** Gazetteer search; an aborted or failed request resolves to null so the box simply keeps its previous list. */
export async function searchPlaces(q, signal) {
  try {
    const r = await fetch(`/api/west/places?q=${encodeURIComponent(q)}&limit=8`, { signal });
    if (!r.ok) return null;
    return await r.json();
  } catch { return null; }
}
