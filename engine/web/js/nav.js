// Site navigation on every page (markup: engine/tvbt/sitenav.py). Signed in on a wide screen the header is a left sidebar
// (html.signed-in, CSS in app.css "Site navigation"); this file keeps that class true, fills the account card (name, xu, free chats,
// Mời bạn via ref.js, Quản trị, Đăng xuất), and runs the drawer, the icon-only toggle, group folding and the ⌘K quick search.
// What it remembers on this device (localStorage, each read and write guarded): whether the visitor was signed in and an admin, the
// name and email shown on the card, the collapsed sidebar and folded groups. A cached state is only a first guess for the first paint;
// /api/auth/me decides.
const root = globalThis.document?.documentElement;   // undefined under node --test (account.js imports this file)
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const store = {
  get(k) { try { return localStorage.getItem('tvbt.nav.' + k); } catch { return null; } },
  set(k, v) { try { v == null ? localStorage.removeItem('tvbt.nav.' + k) : localStorage.setItem('tvbt.nav.' + k, v); } catch { /* storage unavailable */ } },
};
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const api = (path, opts = {}) => fetch(path, { credentials: 'same-origin', ...opts, headers: { 'x-tvbt': '1', 'content-type': 'application/json', ...(opts.headers || {}) } });

/** The one /api/auth/me answer for the page ({enabled, user, admin} or null offline); account.js reads it too. */
export const authMe = root ? fetch('/api/auth/me', { credentials: 'same-origin' }).then(r => r.json()).catch(() => null) : Promise.resolve(null);

/** A gold coin stamped with a square hole, like an old Vietnamese coin; colours from app.css (.coin). */
export const COIN_SVG = '<svg class="coin" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="10.5" class="coin-rim"/><circle cx="12" cy="12" r="8.2" class="coin-face"/><circle cx="12" cy="12" r="6.6" class="coin-ring"/><rect x="9.6" y="9.6" width="4.8" height="4.8" rx=".6" class="coin-hole"/><path d="M6.4 8.2a7 7 0 0 1 3.4-3" class="coin-shine"/></svg>';

const header = root && $('#site-header');
if (header) { import('./ref.js'); init(); }       // ref.js: invite codes and the Mời bạn item in the account menu

function init() {
  const wide = matchMedia('(min-width:1024px)');

  // ----- current page: the static aria-current covers page loads; the home page also moves between its own views by hash
  const mark = () => {
    if (location.pathname !== '/') return;
    const view = document.body.dataset.view;
    const key = view === 'account' ? 'mine' : 'home';
    $$('.nv', header).forEach(a => a.dataset.k === key ? a.setAttribute('aria-current', 'page') : a.removeAttribute('aria-current'));
  };
  if (location.pathname === '/') new MutationObserver(mark).observe(document.body, { attributes: true, attributeFilter: ['data-view'] });

  // ----- drawer (under 1024 px)
  const burger = $('.nav-burger', header), panel = $('#nav-panel');
  const setOpen = open => {
    root.classList.toggle('nav-open', open);
    burger.setAttribute('aria-expanded', open);
    if (open) { panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-modal', 'true'); panel.setAttribute('aria-label', 'Menu'); ($('[aria-current=page]', panel) || $('.nv', panel))?.focus(); }
    else { panel.removeAttribute('role'); panel.removeAttribute('aria-modal'); panel.removeAttribute('aria-label'); }
  };
  const drawerOpen = () => root.classList.contains('nav-open');
  burger.addEventListener('click', () => setOpen(!drawerOpen()));
  $('.nav-close', header).addEventListener('click', () => { setOpen(false); burger.focus(); });
  document.addEventListener('click', e => { if (drawerOpen() && !e.target.closest('#nav-panel,.side-foot,.nav-burger')) setOpen(false); });
  panel.addEventListener('click', e => { if (e.target.closest('a[href]')) setOpen(false); });
  wide.addEventListener('change', () => { if (wide.matches && drawerOpen()) setOpen(false); });

  // ----- icon-only sidebar
  const mini = $('.side-mini', header);
  const paintMini = () => {
    const on = root.classList.contains('nav-mini');
    mini.setAttribute('aria-pressed', on);
    mini.setAttribute('aria-label', on ? 'Mở rộng thanh bên' : 'Thu gọn thanh bên'); mini.title = mini.getAttribute('aria-label');
    $$('.nv', header).forEach(a => { if (on) a.title = a.textContent.trim(); else a.removeAttribute('title'); });
  };
  mini.addEventListener('click', () => { root.classList.toggle('nav-mini'); store.set('mini', root.classList.contains('nav-mini') ? '1' : null); paintMini(); });
  paintMini();

  // ----- folding groups
  let folded = {}; try { folded = JSON.parse(store.get('groups') || '{}') || {}; } catch { /* bad value: all open */ }
  $$('.nv-gh', header).forEach(b => {
    const g = b.closest('.nv-g').dataset.g;
    const hasCurrent = !!$('[aria-current=page]', b.nextElementSibling);
    if (folded[g] && !hasCurrent) b.setAttribute('aria-expanded', 'false');
    b.addEventListener('click', () => {
      const open = b.getAttribute('aria-expanded') !== 'true';
      b.setAttribute('aria-expanded', open);
      if (open) delete folded[g]; else folded[g] = 1;
      store.set('groups', Object.keys(folded).length ? JSON.stringify(folded) : null);
    });
  });

  // ----- popovers in the account card (notifications, account menu)
  const pops = $$('.ubell,.ucard-btn', header);
  const closePops = except => pops.forEach(b => { if (b !== except) { b.setAttribute('aria-expanded', 'false'); $('#' + b.getAttribute('aria-controls')).hidden = true; } });
  pops.forEach(b => b.addEventListener('click', () => {
    const pop = $('#' + b.getAttribute('aria-controls')), open = pop.hidden;
    closePops(b); pop.hidden = !open; b.setAttribute('aria-expanded', open);
    if (open) $('a,button', pop)?.focus();
  }));
  document.addEventListener('click', e => { if (!e.target.closest('.ucard')) closePops(); });
  document.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    const openPop = pops.find(b => b.getAttribute('aria-expanded') === 'true');
    if (openPop) { closePops(); openPop.focus(); return; }
    if (drawerOpen()) { setOpen(false); burger.focus(); }
  });

  initSearch(wide, setOpen);
  initAccount();
}

// ----- quick search: the nav items plus every article on /bai-viet/ (fetched once, on first use)
function initSearch(wide, setOpen) {
  const q = $('#nav-q'), hits = $('#nav-hits');
  const fold = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'd').toLowerCase();
  let articles = null;
  const kind = href => href.includes('/sao/') ? 'Bài viết · Sao' : href.includes('/cung/') ? 'Bài viết · Cung' : href.includes('/cach-cuc/') ? 'Bài viết · Cách cục' : 'Bài viết';
  const items = () => $$('.nv', $('#site-header'))
    .filter(a => (!a.closest('.nv-member') || root.classList.contains('signed-in')) && (!a.closest('.nv-admin') || root.classList.contains('is-admin')))
    .map(a => ({ href: a.getAttribute('href'), t: a.textContent.trim(), k: 'Trang' }));
  const load = () => articles ??= fetch('/bai-viet/').then(r => r.text()).then(html => {
    const doc = new DOMParser().parseFromString(html, 'text/html'), seen = new Set();
    return $$('main a[href^="/bai-viet/"]', doc).map(a => ({ href: a.getAttribute('href'), t: ($('b', a) || a).textContent.trim().replace(/\s+/g, ' '), k: kind(a.getAttribute('href')) }))
      .filter(x => x.t && x.href !== '/bai-viet/' && !x.href.includes('#') && !seen.has(x.href) && seen.add(x.href));
  }).catch(() => []);
  const paint = async () => {
    const term = fold(q.value.trim());
    if (!term) { hits.hidden = true; hits.innerHTML = ''; return; }
    const all = [...items(), ...(await load())];
    const found = all.filter(x => fold(x.t).includes(term)).slice(0, 12);
    if (fold(q.value.trim()) !== term) return;               // a newer keystroke already repainted
    hits.innerHTML = found.length ? found.map(x => `<li><a href="${esc(x.href)}">${esc(x.t)}<small>${x.k}</small></a></li>`).join('') : '<li class="nh-none">Không thấy trang nào khớp.</li>';
    hits.hidden = false;
  };
  q.addEventListener('focus', load, { once: true });
  q.addEventListener('input', paint);
  q.addEventListener('keydown', e => {
    if (e.key === 'Enter') { const a = $('a', hits); if (a) { e.preventDefault(); location.href = a.href; } }
    else if (e.key === 'ArrowDown') { e.preventDefault(); $('a', hits)?.focus(); }
    else if (e.key === 'Escape' && q.value) { e.stopPropagation(); q.value = ''; paint(); }
  });
  hits.addEventListener('keydown', e => {
    const list = $$('a', hits), i = list.indexOf(document.activeElement);
    if (e.key === 'ArrowDown') { e.preventDefault(); list[Math.min(i + 1, list.length - 1)]?.focus(); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); (i <= 0 ? q : list[i - 1]).focus(); }
  });
  document.addEventListener('click', e => { if (!e.target.closest('.side-search')) hits.hidden = true; });
  // ⌘K / Ctrl+K: wherever the search box can be shown (the sidebar, or the drawer on narrow screens)
  document.addEventListener('keydown', e => {
    if (!(e.key === 'k' || e.key === 'K') || !(e.metaKey || e.ctrlKey) || e.altKey) return;
    const sidebar = wide.matches && root.classList.contains('signed-in');
    if (wide.matches && !sidebar) return;
    e.preventDefault();
    if (sidebar && root.classList.contains('nav-mini')) { root.classList.remove('nav-mini'); store.set('mini', null); $('.side-mini').setAttribute('aria-pressed', 'false'); }
    if (!wide.matches) setOpen(true);
    q.focus(); q.select();
  });
  if (!/Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent)) $('.side-search kbd').textContent = 'Ctrl K';
}

// ----- account: sign-in state, the card, the menu, the wallet
function initAccount() {
  const card = $('.ucard'), menu = $('#acct');
  const paintCard = u => {
    const name = u?.name || u?.email || '';
    $('[data-u=name]', card).textContent = name;
    $('[data-u=email]', card).textContent = u?.email || '';
    $('[data-u=av]', card).textContent = (name.split(' ').slice(-1)[0] || '?').charAt(0).toUpperCase();
    $('.ucard-btn', card).setAttribute('aria-label', name ? `Tài khoản: ${name}` : 'Tài khoản');
  };
  let cached = null; try { cached = JSON.parse(store.get('me') || 'null'); } catch { /* none */ }
  if (cached && root.classList.contains('signed-in')) paintCard(cached);

  authMe.then(me => {
    if (!me) return;                                    // offline: keep the last known state
    const on = !!me.enabled, user = on ? me.user : null;
    root.classList.toggle('auth-on', on); store.set('auth', on ? '1' : null);
    root.classList.toggle('signed-in', !!user); store.set('in', user ? '1' : null);
    root.classList.toggle('is-admin', !!(user && me.admin)); store.set('admin', user && me.admin ? '1' : null);
    if (!user) {
      store.set('me', null);
      // ref.js watches #acct: a sign-in link there tells it the visitor is signed out
      menu.innerHTML = on ? '<a class="acct-in" href="/api/auth/google">Đăng nhập với Google</a>' : '';
      return;
    }
    store.set('me', JSON.stringify({ name: user.name || '', email: user.email || '' }));
    paintCard(user);
    menu.innerHTML = `<div class="uwallet" hidden></div><hr>
      <a href="/#tai-khoan" data-go="tai-khoan">Tài khoản và lá số đã lưu</a>
      <a href="/bang-gia">Nạp xu và bảng giá</a>
      ${me.admin ? '<a href="/admin">Quản trị</a>' : ''}
      <button type="button" class="acct-out">Đăng xuất</button>`;
    $('.acct-out', menu).addEventListener('click', async () => {
      await api('/api/auth/logout', { method: 'POST' }).catch(() => {});
      ['in', 'admin', 'me'].forEach(k => store.set(k, null));
      location.reload();
    });
    wallet($('.uwallet', menu));
  });
}

/** Free chats left today and the xu balance, in the account menu and the notifications; repainted when the chat panel reports a new
 *  wallet (the 'tvbt:wallet' event). */
async function wallet(el) {
  const notes = $('[data-u=notes]'), bell = $('.ubell');
  let w = {};
  const render = part => {
    w = { ...w, ...part };                                   // some senders report only part of the wallet
    if (!w.free || w.coins == null) return;
    const free = Number(w.free.remaining), coins = Number(w.coins);
    el.innerHTML = `<span class="acct-wallet"><span class="aw-coins">${COIN_SVG}<b>${coins.toLocaleString('vi-VN')}</b> xu</span></span><span>${free} câu chat miễn phí hôm nay</span>`;
    el.hidden = false;
    const pass = w.pass?.active ? `<p>Gói chat từ lần nạp còn tới ${new Date(w.pass.until).toLocaleDateString('vi-VN')}, tới ${w.pass.perDay} câu mỗi ngày.</p>` : '';
    notes.innerHTML = `<p>Hôm nay còn <b>${free}/${Number(w.free.limit)}</b> câu chat miễn phí với Bát Bát; làm mới lúc 0 giờ.</p>${pass}<p>Số dư: <b>${coins.toLocaleString('vi-VN')} xu</b>.</p>`;
    bell.toggleAttribute('data-dot', w.pass?.active && new Date(w.pass.until) - Date.now() < 3 * 864e5);
  };
  addEventListener('tvbt:wallet', e => render(e.detail));
  try { const r = await api('/api/me/wallet'); if (r.ok) render(await r.json()); } catch { /* the wallet line is optional */ }
}
