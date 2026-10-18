// Four scripted guides: Tử Tử & Vi Vi (Tử Vi side), Bát Bát & Tự Tự (Bát Tự side).
// No AI and no free text generation: every line is assembled from the chart's own facts, the glossary and book-verified readings.
// The "typing" is only an animation of text that already exists in full (and is available to screen readers at once).
import { $, $$, esc, STEMS, BRANCHES } from './util.js';
import { classify, parsePhrase, plainElem } from './beginner.js';
import { currentPhase } from './insights.js';
import { autoLink } from './glossary.js';

export const GUIDES = {
  tu1: { name: 'Tử Tử', side: 'tv', role: 'người dẫn đường Tử Vi' },
  vi: { name: 'Vi Vi', side: 'tv', role: 'người bạn Tử Vi' },
  bat: { name: 'Bát Bát', side: 'bt', role: 'người dẫn đường Bát Tự' },
  tu2: { name: 'Tự Tự', side: 'bt', role: 'người bạn Bát Tự' },
};
const reduce = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
const first = s => (s || '').split(/(?<=\.)\s/)[0];
const cap = t => t ? t[0].toUpperCase() + t.slice(1) : t;
/** "<b>x</b>" / "**x**" markup -> [{t, b}] segments */
export function parseMarkup(s) {
  const plain = String(s).replace(/<b>/g, '**').replace(/<\/b>/g, '**').replace(/<[^>]+>/g, '').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
  return plain.split('**').map((t, i) => ({ t, b: i % 2 === 1 })).filter(x => x.t);
}
export const plainOf = s => parseMarkup(s).map(x => x.t).join('');

// ---------- avatars (inline SVG, colour from CSS variables per guide) ----------
export function avatar(id, size = 52) {
  const acc = {
    tu1: '<path class="gd-acc" d="M32 5l2.6 5.6 6 .7-4.5 4.1 1.2 6L32 18.5 26.7 21.4l1.2-6-4.5-4.1 6-.7z"/>',
    vi: '<path class="gd-acc" d="M20 13a8 8 0 1 0 10 9 6.5 6.5 0 0 1-10-9z"/><circle class="gd-acc" cx="44" cy="15" r="2.6"/>',
    bat: '<path class="gd-tuft" d="M24 14c-3-6 1-9 4-8M33 12c-1-6 4-8 7-5" fill="none" stroke-width="3" stroke-linecap="round"/><text x="32" y="60" class="gd-glyph" text-anchor="middle" lang="zh">八</text>',
    tu2: '<circle class="gd-glass" cx="25" cy="34" r="6.4"/><circle class="gd-glass" cx="39" cy="34" r="6.4"/><path class="gd-glass" d="M31.4 34h1.2"/><text x="32" y="60" class="gd-glyph" text-anchor="middle" lang="zh">字</text>',
  }[id];
  return `<svg class="gd-av gd-${id}" width="${size}" height="${size}" viewBox="0 0 64 64" role="img" aria-label="${GUIDES[id].name}"><circle class="gd-face" cx="32" cy="34" r="22"/>${acc}
    <g class="gd-eyes"><circle class="gd-eye" cx="25" cy="34" r="2.6"/><circle class="gd-eye" cx="39" cy="34" r="2.6"/></g>
    <ellipse class="gd-cheek" cx="20.5" cy="41" rx="3.4" ry="2.2"/><ellipse class="gd-cheek" cx="43.5" cy="41" rx="3.4" ry="2.2"/>
    <path class="gd-mouth" d="M27 43q5 5 10 0" fill="none" stroke-width="2" stroke-linecap="round"/></svg>`;
}

// ---------- typing animation ----------
function renderSegments(host, segs, n) {
  host.textContent = '';
  let left = n;
  for (const s of segs) {
    if (left <= 0) break;
    const part = s.t.slice(0, left); left -= part.length;
    if (s.b) { const el = document.createElement('b'); el.textContent = part; host.append(el); } else host.append(part);
  }
}
/** Types the segments into `host` one character at a time; resolves when finished. `ctl.skipped = true` finishes at once. */
export function typeInto(host, segs, ctl, speed = 24) {
  const total = segs.reduce((a, s) => a + s.t.length, 0), text = segs.map(s => s.t).join('');
  return new Promise(res => {
    if (reduce()) { renderSegments(host, segs, total); res(); return; }
    let i = 0;
    const step = () => {
      if (ctl.stop) { res(); return; }
      if (ctl.skipped || i >= total) { renderSegments(host, segs, total); res(); return; }
      i += 1; renderSegments(host, segs, i);
      const ch = text[i - 1];
      ctl.t = setTimeout(step, /[.!?…]/.test(ch) ? speed * 9 : /[,;:]/.test(ch) ? speed * 4 : ch === ' ' ? speed * 0.6 : speed);
    };
    step();
  });
}
const wait = (ctl, ms) => new Promise(r => { if (ctl.skipped || reduce()) r(); else ctl.t = setTimeout(r, ms); });

// ---------- the conversation panel ----------
const STATE = new WeakMap();
export function initChat(host, sys, turns) {
  if (!host) return;
  STATE.get(host)?.abort();
  const who = sys === 'tv' ? ['tu1', 'vi'] : ['bat', 'tu2'];
  host.innerHTML = `<section class="gd gd-${sys}" aria-label="Trò chuyện cùng ${GUIDES[who[0]].name} và ${GUIDES[who[1]].name}">
    <header class="gd-h"><span class="gd-pair">${avatar(who[0], 46)}${avatar(who[1], 46)}</span><div><p class="eyebrow">Trò chuyện</p><h3>${GUIDES[who[0]].name} và ${GUIDES[who[1]].name} giải thích lá số ${sys === 'tv' ? 'Tử Vi' : 'Bát Tự'}</h3></div>
      <span class="gd-act"><button type="button" class="btn btn-ghost btn-sm" data-gd="skip">Xem ngay</button><button type="button" class="btn btn-ghost btn-sm" data-gd="replay" hidden>Nghe lại</button></span></header>
    <div class="gd-log" role="log" aria-live="off"></div></section>`;
  const log = $('.gd-log', host), skip = $('[data-gd=skip]', host), replay = $('[data-gd=replay]', host);
  let ctl = null;
  const abort = () => { if (ctl) { ctl.stop = true; clearTimeout(ctl.t); } };
  const run = async () => {
    abort(); ctl = { stop: false, skipped: false }; const my = ctl;
    log.textContent = ''; skip.hidden = false; replay.hidden = true; host.classList.remove('gd-done');
    for (const turn of turns) {
      if (my.stop) return;
      const g = GUIDES[turn.who], segs = parseMarkup(turn.t);
      const row = document.createElement('div'); row.className = `gd-row gd-${turn.who}`;
      row.innerHTML = `${avatar(turn.who, 44)}<div class="gd-bub"><span class="gd-who">${g.name}</span><p class="gd-t" aria-hidden="true"></p><span class="gd-sr"></span><span class="gd-dots" aria-hidden="true"><i></i><i></i><i></i></span></div>`;
      $('.gd-sr', row).textContent = `${g.name}: ${segs.map(s => s.t).join('')}`;
      log.append(row);
      row.classList.add('gd-typing');
      await wait(my, 520); if (my.stop) return;
      row.classList.add('gd-talk');
      await typeInto($('.gd-t', row), segs, my);
      if (my.stop) return;
      row.classList.remove('gd-typing', 'gd-talk'); row.classList.add('gd-said');
      autoLink($('.gd-t', row), sys === 'tv' ? 'tv' : 'bt');
      await wait(my, 380);
    }
    skip.hidden = true; replay.hidden = false; host.classList.add('gd-done');
  };
  skip.onclick = () => { if (ctl) ctl.skipped = true; };
  replay.onclick = run;
  let started = false;
  const start = () => { if (!started) { started = true; run(); } };
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { io.disconnect(); start(); } }, { threshold: 0.35 });
    io.observe(host);
    STATE.set(host, { abort: () => { io.disconnect(); abort(); } });
  } else { start(); STATE.set(host, { abort }); }
}

// ---------- one-bubble commentary at the head of each chapter ----------
export function initChapterBubbles(root, sys) {
  if (!root) return;
  const who = sys === 'tv' ? ['tu1', 'vi'] : ['bat', 'tu2'];
  const todo = [];
  $$('.ch-what', root).forEach((p, i) => {
    const text = p.textContent.replace(/^\s*Nói đơn giản:\s*/, '').trim(), g = who[i % 2];
    p.classList.add('gd-chap', `gd-${g}`);
    p.innerHTML = `${avatar(g, 40)}<span class="gd-bub"><span class="gd-who">${GUIDES[g].name}</span><span class="gd-t" aria-hidden="true"></span><span class="gd-sr"></span></span>`;
    $('.gd-sr', p).textContent = `${GUIDES[g].name}: ${text}`;
    const t = $('.gd-t', p); t.textContent = reduce() ? text : '';
    todo.push({ p, t, text });
  });
  if (reduce() || !('IntersectionObserver' in window)) { todo.forEach(x => { x.t.textContent = x.text; }); return; }
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    io.unobserve(e.target);
    const x = todo.find(y => y.p === e.target); if (!x) return;
    const ctl = { stop: false, skipped: false };
    x.p.classList.add('gd-talk');
    typeInto(x.t, [{ t: x.text, b: false }], ctl, 18).then(() => x.p.classList.remove('gd-talk'));
    x.p.addEventListener('click', () => { ctl.skipped = true; }, { once: true });
  }), { threshold: 0.6 });
  todo.forEach(x => io.observe(x.p));
}

// ---------- a guide's bubble in the palace detail panel (12 cung) ----------
/** Static one-bubble reading of a palace: what the palace is about, its main stars, and the first book-verified reading that fired there
 *  (or a plain statement that none did). Facts only, like the conversation scripts; alternates the two Tử Vi guides by palace. */
export function palaceBubble(p, findings, T) {
  const g = p.branch_index % 2 ? 'vi' : 'tu1';
  const what = first(T['palace:' + p.name]?.plain) || '';
  const stars = p.major_stars.length ? `Chính tinh ở đây là **${p.major_stars.map(s => s + (p.major_dignity?.[s] ? ` (${p.major_dignity[s]})` : '')).join(', ')}**.` : 'Cung này **vô chính diệu** (không có chính tinh), nên đọc thêm sao của cung đối diện.';
  const c = classify(findings), top = c.show[0] || c.care[0];
  const say = top ? `Sách đã đối chiếu ghi: ${parsePhrase(top).core.replace(/^(khuynh hướng|hạn chế:)\s*/i, "")}.` : 'Chưa có câu sách đã đối chiếu nào khớp với cung này, nên mình chỉ nói điều đã tính được.';
  const text = `${what} ${stars} ${say}`.trim();
  return `<div class="gd-chap gd-${g} gd-pal">${avatar(g, 40)}<span class="gd-bub"><span class="gd-who">${GUIDES[g].name}</span><span class="gd-t">${parseMarkup(text).map(x => x.b ? `<b>${esc(x.t)}</b>` : esc(x.t)).join('')}</span></span></div>`;
}

// ---------- scripts (facts only) ----------
const tail = '**Không phải dự báo**, chỉ là biểu tượng để suy ngẫm. Bấm vào từ gạch chân bất kỳ để hiểu thêm nhé!';
const finding = (who, top) => top
  ? { who, t: `Một điều sách đã đối chiếu có nêu: ${cap(parsePhrase(top).core)}.${parsePhrase(top).basis ? ` (Căn cứ: ${parsePhrase(top).basis}.)` : ''}` }
  : { who, t: 'Hệ thống chưa có nhận định nào đã đối chiếu sách cho lá số này, nên mình chỉ nói những điều đã tính được.' };

export function dialogueBazi(chart, ctx, T) {
  const b = chart.bazi, t = chart.tuvi, dm = STEMS[b.pillars.day.stem], mb = BRANCHES[b.pillars.month.branch], ph = currentPhase(b, t, ctx.req);
  const top = classify(ctx.reason.systems.bat_tu?.findings || []).show[0];
  return [
    { who: 'bat', t: 'Chào bạn, mình là **Bát Bát**! Cùng đọc **tám chữ** của bạn thật dễ hiểu nhé.' },
    { who: 'tu2', t: `Mình là **Tự Tự**. Chữ đại diện cho bạn, gọi là **Nhật Chủ**, là **${dm.n} ${dm.e}**. ${T['can:' + dm.n]?.plain || ''}` },
    { who: 'bat', t: `Về cân bằng năng lượng: ${plainOf(plainElem(b))}` },
    { who: 'tu2', t: `Bạn sinh vào tháng **${mb.n}** (hành ${mb.e}). Tháng sinh giống như “mùa” của lá số.` },
    { who: 'bat', t: ph.luck ? `Chặng 10 năm bạn đang đi là **đại vận ${ph.luck.name}**, vai **${ph.luck.ten_god}** đối với Nhật Chủ.` : 'Đại vận đầu tiên của bạn chưa bắt đầu.' },
    finding('tu2', top),
    { who: 'bat', t: tail },
  ];
}
export function dialogueTuvi(chart, ctx, T) {
  const t = chart.tuvi, b = chart.bazi, menh = t.palaces.find(p => p.name === 'Mệnh'), than = t.palaces.find(p => p.is_than), ph = currentPhase(b, t, ctx.req);
  const top = classify(ctx.reason.systems.tu_vi?.findings || []).show[0], star = menh.major_stars[0];
  const stars = menh.major_stars.map(s => s + (menh.major_dignity?.[s] ? ` (${menh.major_dignity[s]})` : '')).join(', ');
  const hoa = Object.entries(t.tu_hoa).map(([k, v]) => `${k} ở ${v.star}`).join(', ');
  return [
    { who: 'tu1', t: 'Chào bạn, mình là **Tử Tử**! Lá số Tử Vi là một tấm bản đồ **mười hai cung**, mỗi cung một lĩnh vực đời sống.' },
    { who: 'vi', t: `Mình là **Vi Vi**. Ta bắt đầu từ cung **Mệnh**, chính là bạn. ${menh.major_stars.length ? `Ở đó có **${stars}**. ${first(T['star:' + star]?.plain)}` : 'Cung Mệnh của bạn **vô chính diệu** (không có chính tinh), nên người ta mượn sao của cung đối diện để đọc.'}` },
    { who: 'tu1', t: `Cung **Thân** của bạn nằm ở **${than.name}**. ${first(T['palace:' + than.name]?.plain)}` },
    { who: 'vi', t: `Cục của bạn là **${t.cuc.name}** và bản mệnh là **${t.menh_nap_am}**. Cục dùng để xếp sao và tính tuổi bắt đầu đại hạn.` },
    { who: 'tu1', t: ph.dh ? `Chặng 10 năm hiện tại là **đại hạn cung ${ph.dh.palace}** (${ph.dh.age_from}–${ph.dh.age_to} tuổi): chủ đề này đang được “bật sáng”.` : 'Đại hạn đầu tiên của bạn chưa bắt đầu.' },
    { who: 'vi', t: `Năm sinh của bạn gắn bốn nhãn **Tứ Hóa**: ${hoa}. Nhãn chỉ làm nổi một mặt của sao, không tự nó tốt hay xấu.` },
    finding('tu1', top),
    { who: 'vi', t: tail },
  ];
}
