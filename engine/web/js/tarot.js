// /tarot/: shuffle on the server, pick from a face-down fan, reveal. The page never sees the deck order, only the cards under the
// positions it picked (src/tarot/route.ts). Guests keep their draws in this browser (localStorage); a signed-in reader may save a draw to
// the account, with or without the question, and share it. Card meanings come only from the sourced pack; without one the card shows its
// name and a neutral line.
import { esc } from './util.js';

export const HISTORY_KEY = 'tvbt.tarot.history';
export const MAX_HISTORY = 20;

const store = {
  get() { try { const v = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); return Array.isArray(v) ? v : []; } catch { return []; } },
  set(v) { try { localStorage.setItem(HISTORY_KEY, JSON.stringify(v)); } catch { /* private mode: history is simply not kept */ } },
};

/** The history entry kept on this device for one revealed draw (names and orientation only, plus the question if one was typed). */
export function historyEntry(draw, question) {
  return {
    id: draw.id, at: Date.now(), spread: draw.spread, question: question || null,
    cards: draw.cards.map(c => ({ id: c.card.id, slug: c.card.slug, name_vi: c.card.name_vi, name_en: c.card.name_en, reversed: c.reversed })),
  };
}
export function addHistory(list, entry) {
  return [entry, ...list.filter(e => e && e.id !== entry.id)].slice(0, MAX_HISTORY);
}

/** A card face: the approved picture, or the typographic face (number, Vietnamese name, English name, group). */
export function faceHtml(card, reversed = false) {
  const inner = card.image
    ? `<img class="tcard timg" src="${esc(card.image.small)}" srcset="${esc(card.image.small)} 300w, ${esc(card.image.large)} 600w" sizes="(max-width: 640px) 120px, 260px" width="${card.image.width || 600}" height="${card.image.height || 1006}" alt="Lá ${esc(card.name_en)} (${esc(card.name_vi)})${reversed ? ', lá ngược' : ''}">`
    : `<div class="tcard tface t-${esc(card.suit || 'major')}" role="img" aria-label="${esc(card.name_vi)} (${esc(card.name_en)})${reversed ? ', lá ngược' : ''}"><span class="tc-num">${esc(card.numeral)}</span><span class="tc-name">${esc(card.name_vi)}</span><span class="tc-en">${esc(card.name_en)}</span><span class="tc-suit">${esc(card.suit_vi || 'Ẩn Chính')}</span></div>`;
  return `<div class="tc-wrap${reversed ? ' is-rev' : ''}">${inner}</div>`;
}

/** The card's sourced readings: each paraphrase with Waite's words and the page they are on; otherwise the neutral line. */
export function readingHtml(r) {
  if (!r || r.status !== 'sourced' || !r.items?.length) return `<p class="treading pending">${esc(r?.text || '')}</p>`;
  return `<ul class="treading">${r.items.map(i => `<li><p>${esc(i.text_vi)}</p><blockquote lang="en">“${esc(i.quote_en)}”</blockquote><cite>${esc(i.cite)}</cite></li>`).join('')}</ul>`;
}

/** The drawn cards, the header line, any notice and the layout note. */
export function resultHtml(draw, { title = 'Lá bài của bạn', question = null } = {}) {
  const notices = (draw.notices || []).map(n => `<p>${esc(n.text)}</p>`).join('');
  const slots = draw.cards.map(c => `<div class="t-slot">${faceHtml(c.card, c.reversed)}<div>
    <h3>${esc(c.card.name_vi)}${c.reversed ? '<span class="t-flag">Ngược</span>' : ''}</h3>
    <p class="t-meta">${draw.cards.length > 1 ? `Lá ${c.slot} · ` : ''}${esc(c.card.name_en)} · <a class="link" href="/tarot/la-bai/${esc(c.card.slug)}/">Trang lá bài</a></p>
    ${readingHtml(c.reading)}</div></div>`).join('');
  return `<h2>${esc(title)}</h2>
    <p class="tarot-head" role="note">${esc(draw.header)}</p>
    ${question ? `<p class="note">Điều bạn suy ngẫm: “${esc(question)}”</p>` : ''}
    ${notices ? `<div class="t-notice" role="note">${notices}</div>` : ''}
    <div class="t-spreadrow n${draw.cards.length}">${slots}</div>
    ${draw.layout_note ? `<p class="t-layout">${esc(draw.layout_note)}</p>` : ''}`;
}

const when = ms => { try { return new Date(ms).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' }); } catch { return ''; } };
const historyItem = e => `<li><span>${e.cards.map(c => `<a class="link" href="/tarot/la-bai/${esc(c.slug)}/">${esc(c.name_vi)}</a>${c.reversed ? ' (ngược)' : ''}`).join(' · ')}</span>
  <span class="when">${esc(when(e.at))}</span>${e.question ? `<span class="q">“${esc(e.question)}”</span>` : ''}</li>`;

async function api(path, init = {}) {
  const r = await fetch(path, { credentials: 'same-origin', ...init, headers: { 'content-type': 'application/json', 'x-tvbt': '1', ...(init.headers || {}) } });
  let data = null;
  try { data = await r.json(); } catch { /* not JSON */ }
  return { ok: r.ok, status: r.status, data };
}

function init() {
  const $ = id => document.getElementById(id);
  const form = $('t-form'), status = $('t-status'), fanWrap = $('t-fan-wrap'), fan = $('t-fan'), revealBtn = $('t-reveal'), result = $('t-result');
  const saveBox = $('t-save'), shuffleBtn = $('t-shuffle'), remainingEl = $('t-remaining');
  let current = null, picks = [], user = null, lastQuestion = null;

  const say = (text, warn = false) => { status.textContent = text; status.classList.toggle('warn', warn); };
  const OFF = 'Phần rút bài chưa mở trên máy chủ. Bạn vẫn xem được 78 lá bài ở cuối trang.';

  function showHistory() {
    const list = store.get();
    $('t-history').hidden = !list.length;
    $('t-history-list').innerHTML = list.map(historyItem).join('');
  }
  $('t-history-clear').addEventListener('click', () => { store.set([]); showHistory(); });

  async function showMine() {
    if (!user) return;
    const r = await api('/api/me/tarot', { method: 'GET' });
    if (!r.ok || !r.data) return;
    const draws = r.data.draws || [];
    $('t-mine').hidden = !draws.length;
    $('t-mine-list').innerHTML = draws.map(d => `<li><span>${d.cards.map(c => `${esc(c.card.name_vi)}${c.reversed ? ' (ngược)' : ''}`).join(' · ')}</span>
      <span class="when">${esc(when(d.saved_at))}</span><a class="link" href="/tarot/?x=${esc(d.id)}">Liên kết</a>
      <button type="button" class="link" data-del="${esc(d.id)}">Xóa</button>${d.question ? `<span class="q">“${esc(d.question)}”${d.show_question ? '' : ' (ẩn trên liên kết)'}</span>` : ''}</li>`).join('');
  }
  $('t-mine-list').addEventListener('click', async ev => {
    const id = ev.target.closest('[data-del]')?.dataset.del;
    if (!id) return;
    const r = await api('/api/me/tarot?id=' + encodeURIComponent(id), { method: 'DELETE' });
    if (r.ok) showMine();
  });

  function drawFan(n) {
    fan.innerHTML = Array.from({ length: n }, (_, i) => `<button type="button" class="t-back" data-pos="${i}" aria-pressed="false" aria-label="Lá úp thứ ${i + 1}"></button>`).join('');
  }
  function syncFan() {
    for (const b of fan.querySelectorAll('.t-back')) {
      const k = picks.indexOf(Number(b.dataset.pos));
      b.setAttribute('aria-pressed', String(k >= 0));
      b.innerHTML = k >= 0 && current.pick > 1 ? `<span class="t-order">${k + 1}</span>` : '';
    }
    fan.classList.toggle('done', picks.length === current.pick);
    revealBtn.disabled = picks.length !== current.pick;
  }
  fan.addEventListener('click', ev => {
    const b = ev.target.closest('.t-back');
    if (!b || !current) return;
    const pos = Number(b.dataset.pos), k = picks.indexOf(pos);
    if (k >= 0) picks.splice(k, 1); else if (picks.length < current.pick) picks.push(pos);
    syncFan();
  });

  shuffleBtn.addEventListener('click', async () => {
    const spread = Number(form.querySelector('input[name="t-spread"]:checked')?.value || 1);
    shuffleBtn.disabled = true; say('Đang xáo bài…');
    const r = await api('/api/tarot/draw', { method: 'POST', body: JSON.stringify({ spread, reversals: $('t-rev').checked }) }).catch(() => null);
    shuffleBtn.disabled = false;
    if (!r) return say('Không kết nối được máy chủ. Mời bạn thử lại.', true);
    if (r.status === 404) return say(OFF, true);
    if (!r.ok) return say(r.data?.detail || 'Không xáo được bài. Mời bạn thử lại.', true);
    current = r.data; picks = [];
    remainingEl.textContent = `Còn ${current.remaining}/${current.limit} lượt miễn phí hôm nay.`;
    $('t-need').textContent = String(current.pick);
    drawFan(current.fan); syncFan();
    result.hidden = true; saveBox.hidden = true; fanWrap.hidden = false;
    say('Đã xáo bài. Mời bạn chọn lá.');
    fanWrap.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  revealBtn.addEventListener('click', async () => {
    if (!current || picks.length !== current.pick) return;
    revealBtn.disabled = true; say('Đang lật bài…');
    lastQuestion = $('t-q').value.trim() || null;
    const r = await api('/api/tarot/draw', { method: 'POST', body: JSON.stringify({ id: current.id, picks, question: lastQuestion }) }).catch(() => null);
    if (!r || !r.ok) { revealBtn.disabled = false; return say(r?.data?.detail || 'Không lật được bài. Mời bạn thử lại.', true); }
    const draw = r.data;
    fanWrap.hidden = true; current = null;
    result.innerHTML = resultHtml(draw, { question: lastQuestion }); result.hidden = false;
    store.set(addHistory(store.get(), historyEntry(draw, lastQuestion))); showHistory();
    showSave(draw);
    say('');
    result.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  function showSave(draw) {
    if (!user) {
      saveBox.innerHTML = '<p class="note" style="margin:0">Lượt rút này được giữ trong trình duyệt này. Đăng nhập để lưu vào tài khoản và chia sẻ bằng liên kết.</p>';
      saveBox.hidden = false; return;
    }
    saveBox.innerHTML = `<b>Lưu lượt rút vào tài khoản</b>
      ${lastQuestion ? `<label><input type="checkbox" id="t-save-q"> Lưu cả câu hỏi</label>
      <label><input type="checkbox" id="t-show-q" disabled> Hiện câu hỏi trên liên kết chia sẻ</label>` : ''}
      <p class="t-actions"><button type="button" class="btn btn-sm" id="t-save-btn">Lưu</button></p><div id="t-share-out"></div>`;
    saveBox.hidden = false;
    const saveQ = document.getElementById('t-save-q'), showQ = document.getElementById('t-show-q');
    saveQ?.addEventListener('change', () => { showQ.disabled = !saveQ.checked; if (!saveQ.checked) showQ.checked = false; });
    document.getElementById('t-save-btn').addEventListener('click', async ev => {
      ev.target.disabled = true;
      const body = { id: draw.id, question: saveQ?.checked ? lastQuestion : null, show_question: !!showQ?.checked };
      const r = await api('/api/me/tarot', { method: 'POST', body: JSON.stringify(body) }).catch(() => null);
      const out = document.getElementById('t-share-out');
      if (!r || !r.ok) { ev.target.disabled = false; out.innerHTML = `<p class="note">${esc(r?.data?.detail || 'Không lưu được. Mời bạn thử lại.')}</p>`; return; }
      const link = location.origin + r.data.share_path;
      out.innerHTML = `<p class="note" style="margin:0">Đã lưu. Liên kết chia sẻ${r.data.show_question ? ' (có câu hỏi)' : ' (không kèm câu hỏi)'}:</p>
        <input type="text" readonly value="${esc(link)}" aria-label="Liên kết chia sẻ"><p class="t-actions"><button type="button" class="btn btn-sm btn-ghost" id="t-copy">Chép liên kết</button></p>`;
      document.getElementById('t-copy').addEventListener('click', () => navigator.clipboard?.writeText(link).catch(() => {}));
      showMine();
    });
  }

  async function showShared(id) {
    const box = $('t-shared');
    const r = await api('/api/tarot/x/' + encodeURIComponent(id), { method: 'GET' }).catch(() => null);
    box.hidden = false;
    if (!r || !r.ok) { box.innerHTML = `<p class="t-status warn">${esc(r?.status === 404 && !r?.data?.detail?.startsWith('Liên kết') ? OFF : (r?.data?.detail || 'Không mở được liên kết.'))}</p>`; return; }
    box.innerHTML = resultHtml(r.data, { title: 'Lượt rút được chia sẻ', question: r.data.question })
      + (r.data.question_hidden ? '<p class="note">Người chia sẻ không hiện câu hỏi của họ.</p>' : '')
      + '<p class="note">Muốn tự rút? Dùng phần bên dưới.</p>';
  }

  showHistory();
  const x = new URLSearchParams(location.search).get('x');
  if (x && /^[A-Za-z0-9_-]{22}$/.test(x)) showShared(x);
  fetch('/api/auth/me', { credentials: 'same-origin' }).then(r => r.json()).then(me => { user = me?.user || null; showMine(); }).catch(() => {});
}

if (typeof document !== 'undefined' && document.getElementById('t-form')) init();
