// Interactive glossary: any element with [data-gl="kind:name"] opens a short plain-language explanation.
// Data comes from glossary.json (built by tools/build_glossary.py from glossary_vi.json + star_profiles.json).
import { $, $$, esc, STEMS, BRANCHES, starKind } from './util.js';

let G = { terms: {}, stars: [], gods: [], aliases: {} };
let chart = null; // { tuvi, bazi } for "in your chart" notes
let ready = null;
const re = {};

export function loadGlossary() {
  ready ||= fetch('/js/glossary.json').then(r => r.json()).then(g => { G = g; buildRegex(); }).catch(() => { /* glossary degrades to nothing */ });
  return ready;
}
export const setChart = c => { chart = c; };

const alt = names => names.slice().sort((a, b) => b.length - a.length).map(n => n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
function buildRegex() {
  const L = '(?<![\\p{L}\\p{N}])', R = '(?![\\p{L}\\p{N}])';
  const concept = alt(Object.keys(G.aliases));
  re.tv = new RegExp(`${L}(${alt(G.stars)}|${concept})${R}`, 'gu');
  re.bt = new RegExp(`${L}(${alt(G.gods)}|${concept})${R}`, 'gu');
  if (G.west_aliases) re.west = new RegExp(`${L}(${alt(Object.keys(G.west_aliases))})${R}`, 'gu');
  re.key = (sys, text) => (sys === 'west' ? G.west_aliases[text] : sys === 'bt' && G.gods.includes(text) ? `god:${text}` : G.aliases[text] || `star:${text}`);
}

export const gl = (key, html, cls = '') => `<span class="gl ${cls}" role="button" tabindex="0" data-gl="${esc(key)}">${html}</span>`;

// "Tử Vi" is both a star and the name of the whole system: only treat it as the star inside a list of stars.
const starContext = (t, i, n) => /(?:[,:;–·(]|chính tinh|cát tinh|sao)\s*$/i.test(t.slice(Math.max(0, i - 12), i)) || /^\s*[,;–·()]/.test(t.slice(i + n, i + n + 3));
const SKIP = 'button,a,summary,code,pre,textarea,select,option,script,style,.gl,.pal,.ref,[data-nogl],dialog,svg,.tv-links,h1,h2,h3,h4,.eyebrow,.ln-crumb,.tags,.dr-x';
/** Wraps known terms found in text nodes under `root` (sys: 'tv' | 'bt' decides star vs ten-god for shared names like Thất Sát;
 *  'west' uses the Western astrology terms only, linking each term once per `root`). */
export function autoLink(root, sys) {
  if (!root || !re[sys]) return;
  const once = sys === 'west' ? new Set() : null;
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, { acceptNode: n => !n.nodeValue.trim() || n.parentElement.closest(SKIP) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT });
  const nodes = []; while (w.nextNode()) nodes.push(w.currentNode);
  nodes.forEach(n => {
    const t = n.nodeValue; re[sys].lastIndex = 0;
    if (!re[sys].test(t)) return;
    re[sys].lastIndex = 0;
    const frag = document.createDocumentFragment(); let last = 0, m;
    while ((m = re[sys].exec(t))) {
      const key = re.key(sys, m[1]);
      if (!G.terms[key] || (m[1] === 'Tử Vi' && !starContext(t, m.index, m[1].length)) || (once && once.has(key))) continue;
      once?.add(key);
      frag.append(t.slice(last, m.index));
      const s = document.createElement('span'); s.className = 'gl'; s.setAttribute('role', 'button'); s.tabIndex = 0; s.dataset.gl = key; s.textContent = m[1];
      frag.append(s); last = m.index + m[1].length;
    }
    frag.append(t.slice(last)); n.replaceWith(frag);
  });
}

// ---- "in your chart" notes (read from the already-computed chart; nothing is calculated here) ----
function chartNote(key) {
  if (!chart) return '';
  const [kind, name] = [key.slice(0, key.indexOf(':')), key.slice(key.indexOf(':') + 1)];
  const t = chart.tuvi, b = chart.bazi, PL = { year: 'Năm', month: 'Tháng', day: 'Ngày', hour: 'Giờ' };
  if (kind === 'star') {
    const p = t.palaces.find(x => x.stars.includes(name));
    if (!p) return '';
    const ds = p.dignity_status?.[name], dg = ds?.status === 'VERIFIED' ? ds.value : null, term = dg && ds.term, hoa = Object.entries(t.tu_hoa).find(([, v]) => v.star === name)?.[0];
    return `${esc(name)} đứng ở <b>cung ${esc(p.name)}</b> (${esc(p.stem)} ${esc(p.branch)})${dg ? `, độ sáng <b>${esc(term && term !== dg ? `${dg} (sách ghi “${term}”)` : dg)}</b>` : ds?.status === 'CONFLICT' ? ', độ sáng <b>chưa thống nhất</b> (sách ghi khác nhau)' : ''}${hoa ? `, mang nhãn <b>${esc(hoa)}</b> theo năm sinh` : ''}.`;
  }
  if (kind === 'palace') {
    const p = t.palaces.find(x => x.name === name);
    if (!p) return '';
    return `Cung ${esc(name)} của bạn ở ${esc(p.stem)} ${esc(p.branch)}; ${p.major_stars.length ? `chính tinh: <b>${esc(p.major_stars.join(', '))}</b>` : '<b>vô chính diệu</b> (không có chính tinh)'}.`;
  }
  if (kind === 'god') {
    const at = [];
    ['year', 'month', 'hour'].forEach(k => { if (b.pillars[k].stem_ten_god === name) at.push(`can trụ ${PL[k]}`); });
    ['year', 'month', 'day', 'hour'].forEach(k => b.pillars[k].hidden.forEach(h => { if (h.ten_god === name) at.push(`tàng can ${h.name} trụ ${PL[k]}`); }));
    return at.length ? `Trong lá số của bạn, ${esc(name)} xuất hiện ở: ${esc(at.join('; '))}.` : `${esc(name)} không xuất hiện trong lá số này.`;
  }
  if (kind === 'can' || kind === 'chi') {
    const at = ['year', 'month', 'day', 'hour'].filter(k => (kind === 'can' ? STEMS : BRANCHES)[b.pillars[k][kind === 'can' ? 'stem' : 'branch']].n === name).map(k => `trụ ${PL[k]}`);
    return at.length ? `Trong Bát Tự của bạn, ${esc(name)} nằm ở ${esc(at.join(', '))}.` : `${esc(name)} không nằm trên bốn trụ của lá số này.`;
  }
  if (key === 'c:nhat-chu') return `Nhật Chủ của bạn là <b>${esc(STEMS[b.pillars.day.stem].n)} ${STEMS[b.pillars.day.stem].e}</b>.`;
  if (key === 'c:cuc') return `Cục của bạn là <b>${esc(t.cuc.name)}</b>.`;
  if (key === 'c:nap-am') return `Bản mệnh của bạn là <b>${esc(t.menh_nap_am)}</b> (hành ${esc(t.menh_element)}).`;
  if (/^c:hoa-/.test(key)) { const n = G.terms[key].title, v = t.tu_hoa[n]; return v ? `Năm sinh của bạn: ${esc(n)} gắn với <b>${esc(v.star)}</b>.` : ''; }
  return '';
}

// ---- dialog ----
let dlg;
function ensureDialog() {
  if (dlg) return dlg;
  dlg = document.createElement('dialog'); dlg.id = 'gl-dlg'; dlg.className = 'dlg gl-dlg'; dlg.setAttribute('aria-labelledby', 'gl-t');
  document.body.append(dlg);
  dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });
  return dlg;
}
function fallback(key) {
  const name = key.slice(key.indexOf(':') + 1);
  if (!key.startsWith('star:')) return null;
  const k = starKind(name), kind = { pos: 'Cát tinh', neg: 'Sát / hung tinh', neu: 'Phụ tinh' }[k];
  return { kind, title: name, plain: `Một phụ tinh. Ý nghĩa của nó phụ thuộc vào các sao đi cùng trong cung và vào vị trí của cung đó, nên thường chỉ được đọc khi đặt cạnh sao khác. Thiên Bàn chưa có bài giải thích riêng cho sao này.`, lesson: 'tv-3' };
}

export function openTerm(key) {
  const term = G.terms[key] || fallback(key);
  if (!term) return;
  const d = ensureDialog(), note = chartNote(key);
  d.innerHTML = `<div class="gl-in">
    <p class="eyebrow">${esc(term.kind)}</p>
    <h3 id="gl-t">${esc(term.title)}${term.han ? ` <span class="gl-han" lang="zh">${esc(term.han)}</span>` : ''}</h3>
    <p class="gl-plain">${esc(term.plain)}</p>
    ${term.ex ? `<p class="gl-ex"><b>Ví dụ.</b> ${esc((x => x[0].toUpperCase() + x.slice(1))(term.ex.replace(/^Ví dụ:\s*/, '')))}</p>` : ''}
    ${term.facts?.length ? `<dl class="gl-facts">${term.facts.map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join('')}</dl>` : ''}
    ${note ? `<div class="gl-here"><span class="eyebrow">Trong lá số của bạn</span><p>${note}</p></div>` : ''}
    <div class="gl-act"><button type="button" class="btn btn-ghost btn-sm" data-close>Đóng</button></div>
    ${term.src ? `<p class="gl-src muted small">Nguồn tư liệu: ${esc(term.src)}</p>` : ''}
  </div>`;
  $('[data-close]', d).onclick = () => d.close();
  if (!d.open) d.showModal();
  $('[data-close]', d).focus({ preventScroll: true });
}

export function initGlossary() {
  loadGlossary();
  const target = e => e.target.closest?.('[data-gl]');
  // capture phase: a star inside a palace cell only explains itself once that palace is selected; otherwise the tap selects the palace
  document.addEventListener('click', e => {
    const t = target(e); if (!t) return;
    const pal = t.closest('.pal');
    if (pal && !pal.classList.contains('hl')) return;
    e.preventDefault(); e.stopPropagation(); openTerm(t.dataset.gl);
  }, true);
  document.addEventListener('keydown', e => {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    const t = target(e); if (!t || t.tagName === 'BUTTON') return;
    e.preventDefault(); e.stopPropagation(); openTerm(t.dataset.gl);
  }, true);
}
export const terms = () => G.terms;
