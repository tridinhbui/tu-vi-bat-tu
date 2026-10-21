// "Tải ảnh": the Tử Vi board as a PNG, drawn by the browser itself (no library). The board is copied with its computed styles into an
// SVG <foreignObject>, painted on a canvas and saved. The page fonts are embedded when the font server allows it, else the system serif
// is used. With "Ẩn thông tin sinh" on, the birth rows are already hidden on screen (body.hide-birth) and so in the copy.
import { $ } from './util.js';

const SKIP = /^(transition|animation|will-change|cursor|pointer-events|user-select|-webkit-user-select|caret-color|scroll-|overscroll)/;
let defaults = null, fontCss = null;

/** Default computed style per tag, from a blank same-origin frame: a property is copied only when it differs, which keeps the SVG small. */
function defaultsFor(tag) {
  if (!defaults) {
    const f = document.createElement('iframe');
    f.style.cssText = 'position:fixed;width:0;height:0;border:0;visibility:hidden'; f.setAttribute('aria-hidden', 'true');
    document.body.append(f);
    defaults = { frame: f, by: new Map() };
  }
  if (!defaults.by.has(tag)) {
    const d = defaults.frame.contentDocument, el = d.createElement(tag);
    d.body.append(el);
    const cs = d.defaultView.getComputedStyle(el), o = {};
    for (const p of cs) o[p] = cs.getPropertyValue(p);
    el.remove(); defaults.by.set(tag, o);
  }
  return defaults.by.get(tag);
}

function inline(src, dst) {
  if (src.nodeType !== 1) return;
  const cs = getComputedStyle(src), def = defaultsFor(src.localName), out = [];
  for (const p of cs) { if (SKIP.test(p)) continue; const v = cs.getPropertyValue(p); if (v !== def[p]) out.push(`${p}:${v}`); }
  dst.setAttribute('style', out.join(';'));
  dst.removeAttribute('class'); dst.removeAttribute('id');
  const a = src.children, b = dst.children;
  for (let i = 0; i < a.length; i++) inline(a[i], b[i]);
}

const toDataUrl = blob => new Promise((ok, no) => { const r = new FileReader(); r.onload = () => ok(r.result); r.onerror = no; r.readAsDataURL(blob); });
/** The Google Fonts faces this page uses (latin, latin-ext, vietnamese), with the font files inlined; '' when they cannot be fetched. */
async function fonts() {
  if (fontCss !== null) return fontCss;
  fontCss = '';
  try {
    const link = [...document.querySelectorAll('link[rel=stylesheet]')].find(l => l.href.startsWith('https://fonts.googleapis.com/'));
    if (!link) return '';
    const css = await (await fetch(link.href)).text();
    const faces = css.split(/(?=\/\* )/).filter(b => /^\/\* (latin|latin-ext|vietnamese) \*\//.test(b));
    const urls = [...new Set(faces.flatMap(b => [...b.matchAll(/url\((https:[^)]+)\)/g)].map(m => m[1])))];
    const data = Object.fromEntries(await Promise.all(urls.map(async u => [u, await toDataUrl(await (await fetch(u)).blob())])));
    fontCss = faces.join('').replace(/url\((https:[^)]+)\)/g, (_, u) => `url(${data[u]})`);
  } catch { fontCss = ''; }
  return fontCss;
}

// two frames for the full-board layout to settle; a timer as well, since a background tab gets no animation frames
const frames = () => new Promise(r => { requestAnimationFrame(() => requestAnimationFrame(r)); setTimeout(r, 120); });
const bgOf = el => { for (let e = el; e; e = e.parentElement) { const c = getComputedStyle(e).backgroundColor; if (c && c !== 'transparent' && !/rgba\(.*,\s*0\)$/.test(c)) return c; } return '#fff'; };

/** Saves the Tử Vi board as la-so-tu-vi.png. Throws with a reader-facing message when the browser refuses (some Safari versions). */
export async function exportBoardPng(filename = 'la-so-tu-vi.png') {
  const view = $('#chart-view'), tab = view.dataset.tab, stage = $('#tuvi-host [data-view]'), was = stage?.dataset.view;
  view.dataset.tab = 'tuvi'; if (stage) stage.dataset.view = 'full';
  try {
    await frames(); await document.fonts?.ready;
    const board = $('#tv-board');
    if (!board) throw new Error('Chưa có lá số Tử Vi để xuất ảnh.');
    const w = board.offsetWidth, h = board.offsetHeight, bg = bgOf(board.parentElement);
    const copy = board.cloneNode(true);
    inline(board, copy);
    copy.style.transform = 'none'; copy.style.position = 'relative'; copy.style.left = '0'; copy.style.top = '0'; copy.style.margin = '0';
    const css = await fonts();
    const pad = 24, W = w + pad * 2, H = h + pad * 2;
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}"><style>${css}</style><foreignObject x="0" y="0" width="${W}" height="${H}"><div xmlns="http://www.w3.org/1999/xhtml" style="width:${W}px;height:${H}px;padding:${pad}px;box-sizing:border-box;background:${bg}">${new XMLSerializer().serializeToString(copy)}</div></foreignObject></svg>`;
    const img = new Image();
    img.decoding = 'sync';
    await new Promise((ok, no) => { img.onload = ok; img.onerror = () => no(new Error('Trình duyệt chưa dựng được ảnh lá số.')); img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg); });
    const k = Math.min(2, Math.max(1, devicePixelRatio || 1)), c = document.createElement('canvas');
    c.width = Math.round(W * k); c.height = Math.round(H * k);
    const g = c.getContext('2d'); g.scale(k, k); g.drawImage(img, 0, 0);
    const blob = await new Promise((ok, no) => { try { c.toBlob(b => b ? ok(b) : no(new Error('empty')), 'image/png'); } catch (e) { no(e); } })
      .catch(() => { throw new Error('Trình duyệt này không cho lưu ảnh từ trang. Hãy dùng “Tải PDF”, hoặc thử Chrome hay Firefox.'); });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = filename;
    document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  } finally {
    view.dataset.tab = tab; if (stage && was) stage.dataset.view = was;
  }
}
