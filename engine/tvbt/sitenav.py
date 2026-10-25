"""The one site header for every page (generated articles, the app home page and the hand-written pages).

Signed out it is a top bar; signed in on a wide screen (>= 1024 px) CSS turns the same markup into a left sidebar (app.css, "Site
navigation"); on phones the nav opens as a drawer. The markup is identical on every page except aria-current, so nothing moves when
the visitor goes from page to page. js/nav.js fills the account parts after /api/auth/me answers; a tiny inline script (BOOT) applies
the last known sign-in state before the first paint so the sidebar does not pop in.

tools/build_site.py writes it into the generated pages and swaps it into the hand-written pages listed in HAND_PAGES.
"""
from __future__ import annotations

import math
import re
from html import escape as esc

SITE = "Thiên Bàn"


def _ico(d: str, cls: str = "ico") -> str:
    return (f'<svg class="{cls}" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{d}</svg>')


ICONS = {
    "home": '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/>',
    "grid": '<rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.5"/>',
    "bookmark": '<path d="M6.5 3.5h11v17l-5.5-4-5.5 4z"/>',
    "plus": '<circle cx="12" cy="12" r="8.5"/><path d="M12 8v8M8 12h8"/>',
    "eye": '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="2.8"/>',
    "compass": '<circle cx="12" cy="12" r="8.5"/><path d="m15.2 8.8-1.9 4.5-4.5 1.9 1.9-4.5z"/>',
    "star": '<path d="M12 3.5l2.3 5.3 5.7.6-4.3 3.8 1.2 5.6L12 15.9l-4.9 2.9 1.2-5.6L4 9.4l5.7-.6z"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "book": '<path d="M3 5.5h5.5A3.5 3.5 0 0 1 12 9v11.5a2.8 2.8 0 0 0-2.8-2.8H3z"/><path d="M21 5.5h-5.5A3.5 3.5 0 0 0 12 9v11.5a2.8 2.8 0 0 1 2.8-2.8H21z"/>',
    "file": '<path d="M14 3.5H6.5a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V9z"/><path d="M14 3.5V9h5.5M8.5 13h7M8.5 16.5h5"/>',
    "help": '<circle cx="12" cy="12" r="8.5"/><path d="M9.6 9.3a2.5 2.5 0 1 1 3.4 2.3c-.6.3-1 .8-1 1.5v.6M12 16.8v.1"/>',
    "info": '<circle cx="12" cy="12" r="8.5"/><path d="M12 11v5.5M12 7.8v.1"/>',
    "sliders": '<path d="M4 7h9M17 7h3M4 12h3M11 12h9M4 17h11M19 17h1"/><circle cx="15" cy="7" r="2"/><circle cx="9" cy="12" r="2"/><circle cx="17" cy="17" r="2"/>',
    "shield": '<path d="M12 3.5 19 6v5.5c0 4.5-3 7.6-7 9-4-1.4-7-4.5-7-9V6z"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/>',
    "chev": '<path d="m7 10 5 5 5-5"/>',
    "bell": '<path d="M6.5 9a5.5 5.5 0 1 1 11 0c0 6 2.5 7.5 2.5 7.5H4S6.5 15 6.5 9"/><path d="M10 19.5a2 2 0 0 0 4 0"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "panel": '<rect x="3.5" y="4.5" width="17" height="15" rx="2"/><path d="M9.5 4.5v15"/>',
    "close": '<path d="M6 6l12 12M18 6 6 18"/>',
    "hexagram": '<path d="M5 5h14M5 9h5.5M13.5 9H19M5 13h14M5 17h5.5M13.5 17H19M5 21h14" transform="translate(0 -1.5)"/>',
}


def _brand_mark(size: int = 30) -> str:
    """The same compass mark as js/compass.js brandMark(), drawn here so it is in the HTML before any script runs."""
    def pt(r, deg):
        a = (deg - 90) * math.pi / 180
        return 300 + r * math.cos(a), 300 + r * math.sin(a)
    ticks = ""
    for i in range(12):
        x1, y1 = pt(290, i * 30)
        x2, y2 = pt(236 if i % 3 == 0 else 260, i * 30)
        ticks += f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>'
    return (f'<svg class="brand-mark" width="{size}" height="{size}" viewBox="0 0 600 600" aria-hidden="true" focusable="false">'
            '<circle cx="300" cy="300" r="288" fill="none" stroke="currentColor" stroke-width="22"/>'
            f'<g stroke="currentColor" stroke-width="16" stroke-linecap="round">{ticks}</g>'
            '<ellipse cx="300" cy="300" rx="196" ry="86" transform="rotate(-32 300 300)" fill="none" stroke="currentColor" stroke-width="14" opacity=".55"/>'
            '<path d="M300 150L336 300L300 450L264 300Z" fill="var(--cinnabar)"/><circle cx="300" cy="300" r="16" fill="var(--ivory)"/></svg>')


# (key, href, label, icon, classes, extra attributes). Classes: nv-side = sidebar and drawer only (the top bar has the brand and the
# "Lập lá số" button for these), nv-member = signed-in only. data-go / data-act are handled by js/app.js on the home page (same-page
# moves); elsewhere the href is followed.
HOME = ("home", "/", "Trang chủ", "home", "nv-side", 'data-go="hero"')
GROUPS = [
    ("la-so", "Lá số", "grid", "", [
        ("mine", "/#tai-khoan", "Lá số của tôi", "bookmark", "nv-side nv-member", 'data-go="tai-khoan"'),
        ("new", "/#lap-la-so", "Lập lá số", "plus", "nv-side", 'data-go="lap-la-so"'),
        ("sample", "/#la-so-mau", "Lá số mẫu", "eye", "", 'data-act="sample"'),
    ]),
    ("luan-giai", "Luận giải", "compass", "", [
        ("kinh-dich", "/kinh-dich/", "Kinh Dịch", "hexagram", "", ""),
        ("chiem-tinh", "/chiem-tinh/", "Chiêm tinh", "star", "", ""),
        ("xem-ngay", "/xem-ngay/", "Xem ngày", "calendar", "", ""),
    ]),
    ("kien-thuc", "Kiến thức", "book", "", [
        ("bai-viet", "/bai-viet/", "Bài viết", "file", "", ""),
        ("hoi-dap", "/hoi-dap/", "Hỏi đáp", "help", "", ""),
        ("gioi-thieu", "/gioi-thieu/", "Giới thiệu", "info", "", ""),
    ]),
    ("dieu-hanh", "Điều hành", "sliders", "nv-admin", [
        ("admin", "/admin", "Quản trị", "shield", "nv-side", ""),
    ]),
]
ITEMS = [HOME] + [it for g in GROUPS for it in g[4]]

# Inline, before the header: the last known sign-in state, admin flag and collapsed sidebar, so the first paint is already right.
BOOT = ("<script>/*nav-boot*/try{var d=document.documentElement.classList,s=localStorage;"
        "if(s.getItem('tvbt.nav.auth')==='1')d.add('auth-on');if(s.getItem('tvbt.nav.in')==='1')d.add('signed-in');"
        "if(s.getItem('tvbt.nav.admin')==='1')d.add('is-admin');if(s.getItem('tvbt.nav.mini')==='1')d.add('nav-mini')}catch(e){}</script>")


def current_key(path: str) -> str | None:
    if path in ("/", "/index.html"):
        return "home"
    for key, href, *_ in ITEMS:
        if href.startswith("/") and "#" not in href and href != "/" and path.startswith(href.rstrip("/")):
            return key
    return None


def _item(it, cur: str | None) -> str:
    key, href, label, icon, cls, extra = it
    attrs = f'class="nv{(" " + cls) if cls else ""}" href="{href}" data-k="{key}"' + (f" {extra}" if extra else "")
    if key == cur:
        attrs += ' aria-current="page"'
    return f'<a {attrs}>{_ico(ICONS[icon])}<span class="nv-t">{esc(label)}</span></a>'


def header(path: str) -> str:
    """The header block for the page at `path` (BOOT script, header, nav.js). Identical on every page apart from aria-current."""
    cur = current_key(path)
    groups = "".join(
        f'<div class="nv-g{(" " + gcls) if gcls else ""}" data-g="{gid}">'
        f'<button type="button" class="nv-gh" aria-expanded="true" aria-controls="nvg-{gid}">{_ico(ICONS[icon])}<span class="nv-t">{esc(label)}</span>{_ico(ICONS["chev"], "chev")}</button>'
        f'<div class="nv-gb" id="nvg-{gid}">{"".join(_item(it, cur) for it in items)}</div></div>'
        for gid, label, icon, gcls, items in GROUPS)
    return f"""{BOOT}
<header class="site-header" id="site-header"><div class="wrap hdr">
<a class="brand" href="/" data-go="hero" aria-label="{SITE}, trang chủ">{_brand_mark()}<span class="brand-t"><b>{SITE}</b><small>Tử Vi · Bát Tự</small></span></a>
<button type="button" class="side-mini" aria-pressed="false" aria-label="Thu gọn thanh bên" title="Thu gọn thanh bên">{_ico(ICONS["panel"])}</button>
<div class="nav-panel" id="nav-panel">
<div class="side-head"><b>{SITE}</b><button type="button" class="nav-close" aria-label="Đóng menu">{_ico(ICONS["close"])}</button></div>
<div class="side-search" role="search"><label class="sr-only" for="nav-q">Tìm nhanh trang và bài viết</label>{_ico(ICONS["search"])}<input id="nav-q" type="search" placeholder="Tìm nhanh" autocomplete="off" aria-controls="nav-hits"><kbd aria-hidden="true">⌘K</kbd><ul class="nav-hits" id="nav-hits" hidden aria-label="Kết quả tìm"></ul></div>
<nav class="nav" id="nav" aria-label="Điều hướng chính">{_item(HOME, cur)}{groups}</nav>
</div>
<div class="hdr-end">
<button type="button" class="btn btn-sm btn-ghost hdr-pdf" data-act="print" title="Mở hộp thoại in; chọn “Lưu thành PDF” để tải về">Tải PDF</button>
<button type="button" class="exp-badge" id="exp-badge" hidden title="Chế độ thử nghiệm đang bật. Nhấn để tắt.">Thử nghiệm</button>
<a class="btn btn-sm btn-ghost hdr-in" href="/api/auth/google" title="Đăng nhập với Google">Đăng nhập</a>
<a class="btn btn-sm hdr-cta" href="/#lap-la-so" data-go="lap-la-so">Lập lá số</a>
<button type="button" class="nav-burger" aria-controls="nav-panel" aria-expanded="false" aria-label="Mở menu">{_ico(ICONS["menu"])}</button>
</div>
<div class="side-foot" id="side-foot">
<a class="btn btn-sm btn-ghost side-in" href="/api/auth/google">Đăng nhập với Google</a>
<div class="ucard">
<button type="button" class="ubell" aria-label="Thông báo" aria-expanded="false" aria-controls="nv-bell">{_ico(ICONS["bell"])}</button>
<div class="upop ubell-pop" id="nv-bell" hidden><p class="upop-h">Thông báo</p><div data-u="notes"><p class="muted small">Chưa có thông báo mới.</p></div></div>
<button type="button" class="ucard-btn" aria-expanded="false" aria-controls="acct" aria-label="Tài khoản"><span class="uav" data-u="av" aria-hidden="true"></span><span class="ucard-t"><b data-u="name"></b><small data-u="email"></small></span>{_ico(ICONS["chev"], "chev")}</button>
<div class="upop umenu" id="acct" hidden></div>
</div>
</div>
</div></header>
<script type="module" src="/js/nav.js"></script>"""


# Hand-written pages that carry the site header: file under engine/web -> its URL path (for aria-current).
HAND_PAGES = {
    "index.html": "/",
    "chiem-tinh/index.html": "/chiem-tinh/",
    "bang-gia.html": "/bang-gia",
    "bien-nhan.html": "/bien-nhan",
    "chinh-sach-hoan-tien.html": "/chinh-sach-hoan-tien",
    "privacy.html": "/privacy",
    "library.html": "/library",
    "admin.html": "/admin",
}
_BLOCK = re.compile(r'(?:<script>/\*nav-boot\*/.*?</script>\s*)?<header class="site-header[^"]*"[^>]*>.*?</header>(?:\s*<script type="module" src="/js/nav\.js"></script>)?', re.S)


def sync(doc: str, path: str) -> str:
    """Replaces the page's header block with the canonical one."""
    new, n = _BLOCK.subn(lambda _m: header(path), doc, count=1)
    if n != 1:
        raise ValueError(f"no site header in {path}")
    return new


def nav_list(doc: str) -> list[tuple[str, str]]:
    """(href, label) of every item in a page's main nav, in order (for tests)."""
    m = re.search(r'<nav class="nav" id="nav"[^>]*>(.*?)</nav>', doc, re.S)
    if not m:
        return []
    return [(h, re.sub(r"<[^>]+>", "", t).strip()) for h, t in re.findall(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', m.group(1), re.S)]
