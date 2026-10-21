// Admin page: site statistics and the feedback inbox. The server decides who is an admin (ADMIN_EMAILS); for anyone else
// every /api/admin route answers 404 and this page shows nothing but a "not found" note.
import { loadSales } from './admin_sales.js';
const $ = (s, r = document) => r.querySelector(s);
const api = (path, opts = {}) => fetch(path, { credentials: 'same-origin', cache: 'no-store', ...opts, headers: { 'x-tvbt': '1', 'content-type': 'application/json', ...(opts.headers || {}) } });
const fmt = n => Number(n || 0).toLocaleString('vi-VN');
const when = t => new Date(t).toLocaleString('vi-VN', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit', year: 'numeric' });
const short = t => { const d = new Date(t), now = new Date(); return d.toDateString() === now.toDateString() ? d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) : d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }); };
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
const state = $('#adm-state');

// ---------- tabs ----------
function showTab(name) {
  for (const b of document.querySelectorAll('[data-tab]')) b.setAttribute('aria-selected', String(b.dataset.tab === name));
  $('#tab-stats').hidden = name !== 'stats'; $('#tab-inbox').hidden = name !== 'inbox'; $('#tab-sales').hidden = name !== 'sales';
  history.replaceState(null, '', '#' + name);
  if (name === 'inbox') loadInbox(); else if (name === 'sales') loadSales(); else loadStats();
}

// ---------- stats ----------
const LABEL = { visits: 'Lượt vào web', visitors: 'Khách (không trùng)', scans: 'Lượt quét lá số', signins: 'Lượt đăng nhập' };
let stats = null, metric = 'visits';

async function loadStats() {
  try { const r = await api('/api/admin/stats'); if (!r.ok) throw 0; stats = await r.json(); } catch { $('#kpis').textContent = 'Chưa tải được số liệu.'; return; }
  $('.adm-at').textContent = 'Cập nhật ' + when(stats.at) + (stats.live ? '' : ' · chưa nối cơ sở dữ liệu');
  const k = $('#kpis'); k.replaceChildren();
  const tile = (title, main, rows, sub) => {
    const t = el('article', 'kpi'); t.append(el('h3', '', title)); const b = el('p', 'kpi-n', fmt(main)); t.append(b);
    if (sub) t.append(el('p', 'kpi-sub', sub));
    const dl = el('dl', 'kpi-rows'); for (const [l, v] of rows) { dl.append(el('dt', '', l), el('dd', '', fmt(v))); } t.append(dl); k.append(t);
  };
  for (const key of ['visits', 'visitors', 'scans', 'signins']) {
    const r = stats[key]; tile(LABEL[key], r.today, [['7 ngày', r.d7], ['30 ngày', r.d30], ['Tất cả', r.all]], 'hôm nay');
  }
  const a = stats.accounts; tile('Tài khoản', a.total, [['Mới hôm nay', a.today], ['Mới 7 ngày', a.d7], ['Lá số đã lưu', a.savedCharts]], 'tổng số');
  const f = stats.feedback, p = stats.payments; tile('Góp ý', f.threads, [['Chưa đọc', f.unread]], 'cuộc trò chuyện');
  tile('Nạp xu', p.count, [['Xu đã bán', p.coins], ['Doanh thu (đ)', p.amount ?? 0]], 'lần thanh toán');
  badge(f.unread);
  drawChart();
}

function drawChart() {
  if (!stats) return;
  const vals = stats.series[metric], days = stats.days, max = Math.max(1, ...vals);
  $('#chart-h').textContent = LABEL[metric] + ', 30 ngày';
  const W = 720, H = 220, L = 34, B = 26, T = 10, n = vals.length, bw = (W - L) / n, top = niceMax(max);
  const y = v => T + (H - T - B) * (1 - v / top);
  let svg = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${LABEL[metric]} theo ngày, 30 ngày gần nhất">`;
  for (const g of [0, top / 2, top]) svg += `<line class="ch-grid" x1="${L}" x2="${W}" y1="${y(g)}" y2="${y(g)}"/><text class="ch-ax" x="${L - 6}" y="${y(g) + 4}" text-anchor="end">${fmt(g)}</text>`;
  vals.forEach((v, i) => {
    const x = L + i * bw + 1, w = Math.max(2, bw - 2), h = Math.max(v ? 2 : 0, H - B - y(v));
    const r = Math.min(4, w / 2, h);
    // bar with 4px rounded top, square at the baseline
    const yt = H - B - h;
    svg += `<g class="ch-bar" data-i="${i}"><rect class="ch-hit" x="${L + i * bw}" y="${T}" width="${bw}" height="${H - T - B}"/>`;
    if (h > 0) svg += `<path class="ch-fill${i === n - 1 ? ' ch-today' : ''}" d="M${x} ${H - B}V${yt + r}Q${x} ${yt} ${x + r} ${yt}H${x + w - r}Q${x + w} ${yt} ${x + w} ${yt + r}V${H - B}Z"/>`;
    svg += '</g>';
    if (i % 7 === (n - 1) % 7) svg += `<text class="ch-ax" x="${L + i * bw + bw / 2}" y="${H - 8}" text-anchor="middle">${days[i].slice(8)}/${days[i].slice(5, 7)}</text>`;
  });
  svg += `<line class="ch-base" x1="${L}" x2="${W}" y1="${H - B}" y2="${H - B}"/></svg><div class="ch-tip" hidden></div>`;
  const host = $('#chart'); host.innerHTML = svg;
  const tip = $('.ch-tip', host);
  host.querySelectorAll('.ch-bar').forEach(g => {
    const i = +g.dataset.i;
    const show = () => {
      host.querySelectorAll('.ch-bar.on').forEach(x => x.classList.remove('on')); g.classList.add('on');
      tip.innerHTML = `<b>${fmt(vals[i])}</b><span>${days[i].split('-').reverse().join('/')}</span>`; tip.hidden = false;
      const box = host.getBoundingClientRect(), r = g.getBoundingClientRect();
      tip.style.left = Math.min(box.width - 90, Math.max(0, r.left - box.left + r.width / 2 - 45)) + 'px';
    };
    g.addEventListener('pointerenter', show); g.addEventListener('click', show);
  });
  host.onpointerleave = () => { tip.hidden = true; host.querySelectorAll('.ch-bar.on').forEach(x => x.classList.remove('on')); };
  const tb = el('table', 'adm-table'); tb.innerHTML = '<thead><tr><th>Ngày</th><th>Lượt vào</th><th>Khách</th><th>Lượt quét</th><th>Đăng nhập</th></tr></thead>';
  const body = el('tbody'); for (let i = n - 1; i >= 0; i--) { const tr = el('tr'); tr.append(el('td', '', days[i].split('-').reverse().join('/'))); for (const k of ['visits', 'visitors', 'scans', 'signins']) tr.append(el('td', '', fmt(stats.series[k][i]))); body.append(tr); }
  tb.append(body); $('#chart-table').replaceChildren(tb);
}
function niceMax(m) { const p = Math.pow(10, Math.floor(Math.log10(m))); for (const s of [1, 2, 2.5, 5, 10]) if (s * p >= m) return Math.max(2, s * p); return m; }
$('#chart-pick').addEventListener('click', e => {
  const b = e.target.closest('button[data-k]'); if (!b) return;
  metric = b.dataset.k; for (const x of document.querySelectorAll('#chart-pick button')) x.setAttribute('aria-pressed', String(x === b)); drawChart();
});

// ---------- inbox ----------
let current = null, inboxTimer = 0;
const badge = n => { const b = $('.adm-badge'); b.hidden = !n; b.textContent = n; };
const who = t => t.name || t.email ? `${t.name || ''}${t.email ? ` · ${t.email}` : ''}`.replace(/^ · /, '') : 'Khách chưa đăng nhập';

async function loadInbox() {
  clearTimeout(inboxTimer);
  let threads;
  try { const r = await api('/api/admin/feedback'); if (!r.ok) throw 0; threads = (await r.json()).threads; } catch { $('#ib-list').replaceChildren(el('li', 'muted ib-none', 'Chưa tải được hộp thư.')); return; }
  const list = $('#ib-list'); list.replaceChildren();
  if (!threads.length) list.append(el('li', 'muted ib-none', 'Chưa có góp ý nào.'));
  badge(threads.filter(t => t.unread > 0).length);
  for (const t of threads) {
    const li = el('li'); const b = el('button', 'ib-item' + (t.unread ? ' unread' : '') + (current === t.id ? ' on' : ''));
    b.type = 'button';
    const top = el('span', 'ib-top'); top.append(el('b', '', who(t)), el('time', '', short(t.updatedAt))); b.append(top);
    b.append(el('span', 'ib-last', (t.lastAuthor === 'admin' ? 'Bạn: ' : '') + t.last));
    const meta = el('span', 'ib-meta', `${t.total} tin${t.page ? ' · ' + t.page : ''}`); if (t.unread) meta.append(el('i', 'ib-n', String(t.unread))); b.append(meta);
    b.onclick = () => openThread(t.id);
    li.append(b); list.append(li);
  }
  if (current) refreshThread();
  inboxTimer = setTimeout(() => { if (!$('#tab-inbox').hidden && !document.hidden) loadInbox(); }, 20000);
}

async function openThread(id) {
  current = id; document.body.classList.add('ib-open');
  document.querySelectorAll('.ib-item').forEach(b => b.classList.remove('on'));
  await refreshThread(true);
  loadInbox();
}

async function refreshThread(focus = false) {
  const host = $('#ib-thread');
  let j; try { const r = await api('/api/admin/feedback/' + current); if (!r.ok) throw 0; j = await r.json(); } catch { host.replaceChildren(el('p', 'muted', 'Chưa tải được cuộc trò chuyện.')); return; }
  const keep = $('textarea', host)?.value || '';
  host.replaceChildren();
  const h = el('header', 'ib-th'); const back = el('button', 'link ib-back', '← Danh sách'); back.type = 'button';
  back.onclick = () => { document.body.classList.remove('ib-open'); current = null; loadInbox(); };
  const info = el('div'); info.append(el('b', '', who(j.thread)), el('small', 'muted', `Bắt đầu ${when(j.thread.createdAt)}${j.thread.page ? ' · trang ' + j.thread.page : ''}`));
  h.append(back, info); host.append(h);
  const log = el('div', 'ib-log');
  for (const m of j.messages) { const p = el('p', 'fb-m ' + (m.author === 'admin' ? 'fb-me' : 'fb-them'), m.body); p.append(el('time', '', (m.author === 'admin' ? 'Bạn · ' : '') + when(m.at))); log.append(p); }
  host.append(log);
  const form = el('form', 'fb-form'); const ta = el('textarea'); ta.rows = 2; ta.maxLength = 2000; ta.placeholder = 'Trả lời (khách thấy ngay trong bong bóng góp ý)'; ta.value = keep; ta.setAttribute('aria-label', 'Trả lời');
  const send = el('button', 'btn btn-sm', 'Gửi'); send.type = 'submit'; form.append(ta, send); host.append(form);
  ta.addEventListener('keydown', e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) { e.preventDefault(); form.requestSubmit(); } });
  form.onsubmit = async e => {
    e.preventDefault(); const body = ta.value.trim(); if (!body) return; send.disabled = true;
    try { const r = await api('/api/admin/feedback/' + current, { method: 'POST', body: JSON.stringify({ body }) }); if (!r.ok) throw 0; ta.value = ''; await refreshThread(true); loadInbox(); }
    catch { send.disabled = false; alert('Chưa gửi được trả lời.'); }
  };
  log.scrollTop = log.scrollHeight;
  if (focus) ta.focus();
}
$('#ib-refresh').onclick = loadInbox;

// ---------- boot ----------
(async () => {
  let me = null;
  try { const r = await api('/api/admin/me'); if (r.ok) me = await r.json(); } catch { /* offline */ }
  if (!me?.admin) { state.innerHTML = 'Không tìm thấy trang. <a href="/">Về trang chủ</a>'; return; }
  state.hidden = true; $('.adm-tabs').hidden = false; $('.adm-who').textContent = me.email;
  for (const b of document.querySelectorAll('[data-tab]')) b.onclick = () => showTab(b.dataset.tab);
  showTab(location.hash === '#inbox' ? 'inbox' : location.hash === '#sales' ? 'sales' : 'stats');
})();
