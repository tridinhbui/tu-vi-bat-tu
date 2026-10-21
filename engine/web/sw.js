// Thiên Bàn service worker: an offline shell, nothing more. Pages and static files are served from the network when it is there
// (so a deploy shows at once) and from the cache when it is not; the API and sign-in are never cached (charts, accounts and coins
// are always live). Bump VERSION to drop every old cache.
const VERSION = 'tvbt-v1';
const SHELL = ['/', '/css/app.css', '/css/atlas.css', '/css/dash.css', '/css/content.css', '/css/feedback.css', '/js/app.js', '/js/util.js',
  '/js/pwa.js', '/js/ref.js', '/js/feedback.js', '/manifest.webmanifest', '/icons/icon-192.png', '/bai-viet/', '/xem-ngay/', '/hoi-dap/', '/gioi-thieu/'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => Promise.all(SHELL.map(u => c.add(u).catch(() => { /* one missing file must not block install */ })))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

const NEVER = p => p.startsWith('/api/') || p.startsWith('/admin') || p === '/sw.js';
const FONTS = h => h === 'fonts.googleapis.com' || h === 'fonts.gstatic.com';

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const same = url.origin === self.location.origin;
  if ((same && NEVER(url.pathname)) || (!same && !FONTS(url.hostname))) return;
  // network first, cache as fallback; a navigation with nothing cached falls back to the home shell
  e.respondWith((async () => {
    const cache = await caches.open(VERSION);
    try {
      const res = await fetch(req);
      if (res.ok || res.type === 'opaque') cache.put(req, res.clone()).catch(() => {});
      return res;
    } catch (err) {
      const hit = await cache.match(req, { ignoreSearch: req.mode === 'navigate' });
      if (hit) return hit;
      if (req.mode === 'navigate') { const home = await cache.match('/'); if (home) return home; }
      throw err;
    }
  })());
});
