// Installable app: registers the service worker (offline shell, see /sw.js) and, when the browser offers installation, adds an
// "Cài ứng dụng" button to the footer. Nothing here is needed for the site to work.
if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')) {
  addEventListener('load', () => navigator.serviceWorker?.register('/sw.js').catch(() => { /* private mode or blocked: the site works without it */ }));
}
let deferred = null;
addEventListener('beforeinstallprompt', e => {
  e.preventDefault(); deferred = e;
  const foot = document.querySelector('.site-footer .foot-note');
  if (!foot || document.getElementById('pwa-install')) return;
  const b = document.createElement('button'); b.type = 'button'; b.id = 'pwa-install'; b.className = 'link'; b.textContent = 'Cài Thiên Bàn lên máy';
  b.onclick = async () => { if (!deferred) return; deferred.prompt(); await deferred.userChoice.catch(() => {}); deferred = null; b.remove(); };
  foot.append(' · ', b);
});
addEventListener('appinstalled', () => document.getElementById('pwa-install')?.remove());
