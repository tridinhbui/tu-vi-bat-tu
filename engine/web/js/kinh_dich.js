// Kinh Dịch / Mai Hoa page. The coins are tossed here (crypto.getRandomValues); everything else — the quẻ, the moving lines, the
// reading — comes from the engine, which only receives the faces or the numbers, so a cast can be replayed from its link.
import { $, $$, esc, post } from './util.js';
import { figure, haoName, morph } from './hexagram.js';

const root = $('#kd');
const HIST = 'tvbt-kd-v1';
const TOPIC_VI = { su_nghiep: 'Sự nghiệp', tai_chinh: 'Tài chính', kinh_doanh: 'Kinh doanh', hoc_tap: 'Học tập', tinh_cam: 'Tình cảm', gia_dinh: 'Gia đình', lua_chon: 'Lựa chọn' };
const BASIS = { kinh: 'Kinh văn', chu_giai: 'Lời bàn cổ', tinh_toan: 'Tính từ quẻ', he_thong: 'Cách đọc', dien_giai: 'Diễn giải hiện đại', loi_khuyen: 'Lời khuyên' };
const LAYER = { nghia: 'dịch nghĩa', trinh_di: 'Truyện của Trình Di', chu_hy: 'Bản nghĩa của Chu Hy', tien_nho: 'lời bàn của tiên nho', han: 'nguyên văn' };
const store = {
  get: () => { try { return JSON.parse(localStorage.getItem(HIST) || '[]'); } catch { return []; } },
  set: v => { try { localStorage.setItem(HIST, JSON.stringify(v.slice(0, 30))); } catch { /* private mode */ } },
};
const reduceMotion = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const topic = () => $('input[name=kd-topic]:checked')?.value || '';
const question = () => $('#kd-q').value.trim();

// ---------------------------------------------------------------- modes
function setMode(m) {
  $$('.kd-mode button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.mode === m)));
  $('#kd-gieo').hidden = m !== 'gieo';
  $('#kd-maihoa').hidden = m !== 'mai-hoa';
}
$$('.kd-mode button').forEach(b => b.addEventListener('click', () => setMode(b.dataset.mode)));

// ---------------------------------------------------------------- gieo quẻ
let tosses = [];
const face = () => (crypto.getRandomValues(new Uint8Array(1))[0] & 1) ? 'lung' : 'chu';
const valueOf = t => ({ 1: 7, 2: 8, 3: 9, 0: 6 })[t.filter(f => f === 'lung').length];

function drawBuild() {
  const vals = tosses.map(valueOf);
  $('#kd-build').innerHTML = figure(vals.map(v => (v === 7 || v === 9) ? 1 : 0), { values: vals, moving: vals.map((v, i) => (v === 6 || v === 9) ? i + 1 : 0).filter(Boolean), label: `Đã gieo ${vals.length} hào` });
  $('#kd-toss').textContent = tosses.length < 6 ? `Gieo lần ${tosses.length + 1} / 6` : 'Đang xem quẻ…';
  $('#kd-reset').hidden = !tosses.length;
}

async function toss() {
  if (tosses.length >= 6) return;
  const btn = $('#kd-toss');
  btn.disabled = true;
  const t = [face(), face(), face()];
  const coins = $$('#kd-coins .coin');
  coins.forEach(c => { c.className = 'coin'; void c.offsetWidth; if (!reduceMotion()) c.classList.add('spin'); });
  if (!reduceMotion()) await sleep(700);
  coins.forEach((c, i) => c.classList.add(t[i]));
  tosses.push(t);
  drawBuild();
  btn.disabled = tosses.length >= 6;
  if (tosses.length === 6) await readKinhDich({ tosses }, { q: tosses.map(valueOf).join('') });
}
$('#kd-toss').addEventListener('click', toss);
$('#kd-reset').addEventListener('click', () => { tosses = []; drawBuild(); $('#kd-result').hidden = true; $('#kd-toss').disabled = false; });

// manual entry
$('#kd-manual-lines').innerHTML = [6, 5, 4, 3, 2, 1].map(p => `<label>Hào ${['Đầu', 'Hai', 'Ba', 'Tư', 'Năm', 'Trên'][p - 1]}<span class="sel"><select data-p="${p}">
  <option value="7">7 · dương tĩnh</option><option value="8">8 · âm tĩnh</option><option value="9">9 · dương động</option><option value="6">6 · âm động</option></select></span></label>`).join('');
$('#kd-manual-go').addEventListener('click', () => {
  const vals = [1, 2, 3, 4, 5, 6].map(p => +$(`#kd-manual-lines select[data-p="${p}"]`).value);
  readKinhDich({ values: vals }, { q: vals.join('') });
});

// ---------------------------------------------------------------- reading
let current = null;

async function readKinhDich(input, share) {
  const res = $('#kd-result');
  res.hidden = false;
  res.innerHTML = '<p class="note">Đang đọc quẻ…</p>';
  let data;
  try { data = await post('/api/kinh-dich/reading', { ...input, topic: topic() || null }); }
  catch (e) { res.innerHTML = `<p class="notice warn">Không đọc được quẻ lúc này (${esc(e.message || e)}). Thử lại sau giây lát.</p>`; return; }
  current = { kind: 'kd', data, share: { ...share, t: topic() } };
  renderKinhDich(data);
  remember();
}

function sentenceBasis(s) {
  const from = (s.from || []).flatMap(f => f.cites ? f.cites : [f]).filter(f => f.quote).map(f => {
    const where = f.layer ? `${LAYER[f.layer] || f.layer}${f.hexagram ? `, quẻ ${f.hexagram}` : ''}` : f.path ? `Mai Hoa Dịch Số, ${f.path}` : (f.chapter || f.book || '');
    return `<q>${esc(f.quote)}</q> <span class="src">(${esc(where)})</span>`;
  });
  return `<li><span class="b-tag b-${s.basis}">${esc(BASIS[s.basis] || s.basis)}</span>${esc(s.text)}${from.length ? `<br>${from.join('<br>')}` : ''}${s.note ? `<br><span class="src">${esc(s.note)}</span>` : ''}</li>`;
}

function sectionHtml(sec) {
  const depth = sec.paragraphs.some(p => p.depth === 'sau') ? 'sau' : 'nhanh';
  const paras = sec.paragraphs.map(p => {
    const text = p.sentences.map(s => `<span class="${s.basis === 'kinh' ? 'k-kinh' : ''}">${esc(s.text)}</span>`).join(' ');
    return `<p>${text}</p><details class="kd-basis"><summary>Mỗi câu dựa vào đâu</summary><ol>${p.sentences.map(sentenceBasis).join('')}</ol></details>`;
  }).join('');
  return `<section class="kd-sec${sec.id === 'loi_khuyen' ? ' advice' : ''}" data-depth="${depth}"><h3>${esc(sec.title)}</h3>${paras}</section>`;
}

// what the paywall held back (src/billing/paywall.ts gateCast): Đọc sâu goes to a member holding a paid package for any chart
function lockNote(r) {
  const l = r?.locked;
  if (!l) return '';
  const what = `${l.deep} đoạn Đọc sâu (cấu trúc quẻ, vị trí từng hào động, quẻ hỗ, nguyên văn và lời bàn)`;
  return l.need === 'sign_in'
    ? `<p class="notice"><span><b>Còn ${esc(what)}.</b> Đăng nhập và có một gói luận giải cho bất kỳ lá số nào để đọc phần này. <a class="link" href="/#tai-khoan">Đăng nhập</a></span></p>`
    : `<p class="notice"><span><b>Còn ${esc(what)}.</b> Phần Đọc sâu mở cho thành viên đã có một gói luận giải của bất kỳ lá số nào. <a class="link" href="/bang-gia.html">Xem các gói</a></span></p>`;
}

function figureBlock(h, title, opts) {
  return `<figure class="kd-fig">${figure(h.lines, opts)}<figcaption>${esc(title)}<b>${esc(h.full_name)} <span lang="zh">${esc(h.han)}</span></b></figcaption></figure>`;
}

function renderKinhDich(data) {
  const { cast, reading } = data;
  const q = question();
  const t = reading.topic;
  const res = $('#kd-result');
  const figs = [figureBlock(cast.ban, 'Quẻ chủ', { moving: cast.moving, values: cast.values, interactive: true, label: 'Quẻ chủ, chạm từng hào để xem lời hào', cls: 'main' })];
  // the quẻ biến is drawn as the quẻ chủ, then its moving lines turn over (morph below)
  if (cast.bien) figs.push(`<span class="kd-arrow" aria-hidden="true">→</span>`, figureBlock({ ...cast.bien, lines: cast.ban.lines }, 'Quẻ biến', { label: 'Quẻ biến', cls: 'bien' }));
  figs.push(figureBlock(cast.ho, 'Quẻ hỗ', { label: 'Quẻ hỗ', cls: 'sm' }));
  const missing = reading.missing?.length ? `<p class="notice"><span><b>Phần còn thiếu.</b> Chưa có ${esc(reading.missing.join('; '))}: phần đó chỉ hiện kinh văn và lời bàn, chưa có diễn giải.</span></p>` : '';
  res.innerHTML = `<div class="kd" data-depth="nhanh">
    <header class="kd-head"><p class="eyebrow">Quẻ của bạn${t ? ` · ${esc(TOPIC_VI[t])}` : ''}</p>
      <h2>${esc(cast.ban.full_name)}<span class="han" lang="zh">${esc(cast.ban.han)}</span>${cast.bien ? ` → ${esc(cast.bien.name)}` : ''}</h2>
      ${q ? `<p class="kd-q">“${esc(q)}”</p>` : ''}</header>
    <div class="kd-figs">${figs.join('')}</div>
    <div class="kd-tools"><div class="seg kd-depth" role="group" aria-label="Mức đọc"><button type="button" data-depth="nhanh" aria-pressed="true">Đọc nhanh</button><button type="button" data-depth="sau" aria-pressed="false">Đọc sâu</button></div>
      <button type="button" class="btn btn-ghost btn-sm" data-act="share">Chép liên kết</button><button type="button" class="btn btn-ghost btn-sm" data-act="print">In / lưu PDF</button></div>
    ${missing}
    ${reading.sections.map(sectionHtml).join('')}
    ${lockNote(reading)}
    <p class="note small">Bản nháp: phần diễn giải hiện đại và lời khuyên chưa qua người duyệt.</p></div>`;
  wireResult(res);
  if (cast.bien) morph(res.querySelector('.hx.bien'), cast.moving);
  res.querySelectorAll('.kd-fig .hx.main button.hx-line').forEach(b => b.addEventListener('click', () => openHao(cast, +b.dataset.hao, b)));
  res.scrollIntoView({ behavior: reduceMotion() ? 'auto' : 'smooth', block: 'start' });
}

function wireResult(res) {
  res.querySelectorAll('.kd-depth button').forEach(b => b.addEventListener('click', () => {
    res.querySelector('.kd').dataset.depth = b.dataset.depth;
    res.querySelectorAll('.kd-depth button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
  }));
  res.querySelector('[data-act=share]')?.addEventListener('click', async e => {
    const url = `${location.origin}/kinh-dich/#${new URLSearchParams(current.share)}`;
    try { await navigator.clipboard.writeText(url); e.target.textContent = 'Đã chép'; } catch { prompt('Liên kết của quẻ này', url); }
  });
  res.querySelector('[data-act=print]')?.addEventListener('click', () => { res.querySelectorAll('details').forEach(d => { d.open = true; }); print(); });
}

// ---------------------------------------------------------------- hào sheet
const textCache = new Map();
async function quẻText(n) {
  if (!textCache.has(n)) textCache.set(n, fetch(`/api/kinh-dich/text/${n}`).then(r => r.ok ? r.json() : Promise.reject(new Error(r.status))));
  return textCache.get(n);
}

async function openHao(cast, p, opener) {
  const sheet = $('#kd-sheet'), box = sheet.firstElementChild;
  const h = cast.hao[p - 1];
  box.innerHTML = `<button type="button" class="btn btn-ghost btn-sm x" data-close>Đóng</button><h2 id="kd-sheet-h">Hào ${esc(haoName(p, h.yang))} <span lang="zh">${esc(h.han)}</span></h2><p class="note">Đang tải lời hào…</p>`;
  sheet.hidden = false;
  box.focus();
  const close = () => { sheet.hidden = true; opener?.focus(); document.removeEventListener('keydown', onKey); };
  const onKey = e => { if (e.key === 'Escape') close(); };
  document.addEventListener('keydown', onKey);
  sheet.onclick = e => { if (e.target === sheet || e.target.closest('[data-close]')) close(); };
  let t;
  try { t = await quẻText(cast.ban.number); } catch { box.querySelector('.note').textContent = 'Không tải được lời hào.'; return; }
  const seg = t.segments[`hao${p}`] || {}, tt = t.segments[`tieu_tuong${p}`] || {};
  const L = seg.layers || {}, dg = t.dien_giai?.hao?.[String(p)];
  const facts = [h.chinh ? 'đúng ngôi' : 'không đúng ngôi', h.trung ? 'ở giữa quái' : null, h.ung ? `có ứng với hào ${['Đầu', 'Hai', 'Ba', 'Tư', 'Năm', 'Trên'][h.ung_with - 1]}` : 'không có ứng'].filter(Boolean).join(', ');
  const para = (title, v) => v ? `<h3>${title}</h3>${String(v).split('\n').map(x => `<p>${esc(x)}</p>`).join('')}` : '';
  box.innerHTML = `<button type="button" class="btn btn-ghost btn-sm x" data-close>Đóng</button>
    <h2 id="kd-sheet-h">Hào ${esc(haoName(p, h.yang))}${h.moving ? ' · động' : ''}</h2>
    <p class="han" lang="zh">${esc(seg.han || '')}</p>${L.am ? `<p class="am">${esc(L.am)}</p>` : ''}
    ${para('Dịch nghĩa', L.nghia)}${para('Lời Tượng', tt.layers?.nghia)}
    ${dg?.gist ? para('Diễn giải hiện đại (bản nháp)', dg.gist.text) : ''}
    <h3>Vị trí</h3><p>Hào ${h.yang ? 'dương' : 'âm'}, ${esc(facts)}. Ngôi của hào theo lệ chung là ngôi ${esc(h.rank)}.</p>
    ${para('Bản nghĩa của Chu Hy', L.chu_hy)}${para('Truyện của Trình Di', L.trinh_di)}
    ${t.has_translation ? '' : '<p class="notice">Quẻ này chưa có bản dịch Ngô Tất Tố trong kho: chỉ có nguyên văn chữ Hán.</p>'}
    <p class="note small">Bản dịch và lời bàn: Ngô Tất Tố, Kinh Dịch (dịch và chú giải). Ngôi, giữa, ứng theo phần “Những điều nên biết” của sách.</p>`;
}

// ---------------------------------------------------------------- Mai Hoa
const MH_FIELDS = {
  thoi_gian: () => `<p class="note small">Dùng năm, tháng, ngày âm lịch và giờ của thời điểm lập quẻ ở trên.</p>`,
  vat_so: () => num('mh-count', 'Số vật đếm được', 1),
  thanh_am: () => `<div class="kd-mh-row">${num('mh-count', 'Số tiếng (lần đầu)', 1)}<label class="fld"><span>Lần sau (nếu có)</span><input id="mh-second" type="number" inputmode="numeric" min="1" placeholder="bỏ trống nếu chỉ một lần"></label></div>`,
  chu: () => num('mh-words', 'Số chữ (âm tiết), từ 11', 11),
  truong_xich: () => `<div class="kd-mh-row">${num('mh-zhang', 'Trượng', 1)}${num('mh-chi', 'Thước', 1)}</div>`,
  xich_thon: () => `<div class="kd-mh-row">${num('mh-chi', 'Thước', 1)}${num('mh-cun', 'Tấc', 1)}</div>`,
  vat_phuong: () => `<div class="kd-mh-row"><label class="fld"><span>Vật thuộc quái</span><span class="sel"><select id="mh-obj">${['Kiền', 'Đoài', 'Ly', 'Chấn', 'Tốn', 'Khảm', 'Cấn', 'Khôn'].map(x => `<option>${x}</option>`).join('')}</select></span></label>
    <label class="fld"><span>Hướng vật tới</span><span class="sel"><select id="mh-dir">${[['bac', 'Bắc'], ['nam', 'Nam'], ['dong', 'Đông'], ['tay', 'Tây'], ['dong_bac', 'Đông bắc'], ['dong_nam', 'Đông nam'], ['tay_bac', 'Tây bắc'], ['tay_nam', 'Tây nam']].map(([v, l]) => `<option value="${v}">${l}</option>`).join('')}</select></span></label></div>`,
};
const num = (id, label, min) => `<label class="fld"><span>${label}</span><input id="${id}" type="number" inputmode="numeric" min="${min}" value="${min}"></label>`;
const pad = n => String(n).padStart(2, '0');
const nowLocal = () => { const d = new Date(); return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`; };
$('#mh-moment').value = nowLocal();
const drawFields = () => { $('#mh-fields').innerHTML = MH_FIELDS[$('#mh-method').value](); };
$('#mh-method').addEventListener('change', drawFields);
drawFields();

function mhInput() {
  const m = $('#mh-method').value, v = id => $(id) ? +$(id).value : undefined;
  const body = { method: m, moment: $('#mh-moment').value };
  if (m === 'vat_so' || m === 'thanh_am') body.count = v('#mh-count');
  if (m === 'thanh_am' && $('#mh-second').value) body.second = v('#mh-second');
  if (m === 'chu') body.words = v('#mh-words');
  if (m === 'truong_xich') { body.zhang = v('#mh-zhang'); body.chi = v('#mh-chi'); }
  if (m === 'xich_thon') { body.chi = v('#mh-chi'); body.cun = v('#mh-cun'); }
  if (m === 'vat_phuong') { body.object_trigram = $('#mh-obj').value; body.direction = $('#mh-dir').value; }
  return body;
}

const REL_VI = { ty_hoa: 'tỷ hòa (cùng hành)', sinh_the: 'sinh thể', the_sinh: 'thể sinh nó (thể hao)', khac_the: 'khắc thể', the_khac: 'thể khắc nó' };
const STR_VI = { vuong: 'vượng', suy: 'suy', binh: 'bình' };

async function readMaiHoa(body) {
  const res = $('#kd-result');
  res.hidden = false;
  res.innerHTML = '<p class="note">Đang lập quẻ…</p>';
  let c, reading;
  try { ({ cast: c, reading } = await post('/api/mai-hoa/reading', { ...body, topic: topic() || null })); }
  catch (e) { res.innerHTML = `<p class="notice warn">Không lập được quẻ (${esc(e.message || e)}).</p>`; return; }
  current = { kind: 'mh', data: c, share: { mh: JSON.stringify(body), t: topic() } };
  const roles = { [c.the.position]: 'thể', [c.dung.position]: 'dụng' };
  const strength = k => c.strength ? ` · ${STR_VI[c.strength[k]]}` : '';
  res.innerHTML = `<div class="kd" data-depth="nhanh">
    <header class="kd-head"><p class="eyebrow">Quẻ Mai Hoa</p><h2>${esc(c.ban.full_name)}<span class="han" lang="zh">${esc(c.ban.han)}</span> → ${esc(c.bien.name)}</h2></header>
    <div class="kd-steps">${c.steps.map(s => `<div><b>${esc(s.label)}:</b> ${esc(s.expr)} → ${esc(String(s.result))}</div>`).join('')}</div>
    <div class="kd-figs">${figureBlock(c.ban, 'Quẻ chủ', { moving: [c.moving], roles: { upper: roles.upper, lower: roles.lower }, label: 'Quẻ chủ' })}
      <span class="kd-arrow" aria-hidden="true">→</span>${figureBlock(c.bien, 'Quẻ biến', { label: 'Quẻ biến' })}${figureBlock(c.ho, 'Quẻ hỗ', { label: 'Quẻ hỗ', cls: 'sm' })}</div>
    <section class="kd-sec"><h3>Thể và dụng</h3>
      <dl class="kd-rel"><dt>Thể</dt><dd>${esc(c.the.trigram)} (${esc(c.the.element)})${strength('the')}</dd>
      <dt>Dụng</dt><dd>${esc(c.dung.trigram)} (${esc(c.dung.element)}): ${esc(REL_VI[c.relations.dung])}${strength('dung')}</dd>
      <dt>Hỗ</dt><dd>${esc(c.ho.upper)}: ${esc(REL_VI[c.relations.ho_upper])}; ${esc(c.ho.lower)}: ${esc(REL_VI[c.relations.ho_lower])}${c.ho_from === 'bien' ? ' (Kiền, Khôn không có hỗ: lấy hỗ của quẻ biến)' : ''}</dd>
      <dt>Biến</dt><dd>${esc(c.bien_dung.trigram)} (${esc(c.bien_dung.element)}): ${esc(REL_VI[c.relations.bien])}${strength('bien')}</dd></dl>
      ${c.season_vi ? `<p class="note small">Vượng, suy tính theo ${esc(c.season_vi)} (tháng ${c.month} âm lịch).</p>` : ''}</section>
    ${reading ? `<div class="kd-tools"><div class="seg kd-depth" role="group" aria-label="Mức đọc"><button type="button" data-depth="nhanh" aria-pressed="true">Đọc nhanh</button><button type="button" data-depth="sau" aria-pressed="false">Đọc sâu</button></div></div>
      ${reading.sections.filter(s => s.id !== 'lap_que').map(sectionHtml).join('')}${lockNote(reading)}<p class="note small">${esc(reading.translation)}; nguyên văn chữ Hán trong phần “Mỗi câu dựa vào đâu”.</p>`
      : '<p class="notice"><span><b>Chưa có phần luận.</b> Quẻ, thể, dụng, hỗ, biến và vượng suy ở trên đã tính theo Mai Hoa Dịch Số.</span></p>'}
    ${c.notes.length ? `<details class="kd-basis"><summary>Chỗ sách không nói và cách Thiên Bàn chọn</summary><ol>${c.notes.map(n => `<li>${esc(n)}</li>`).join('')}</ol></details>` : ''}
    <div class="kd-tools"><button type="button" class="btn btn-ghost btn-sm" data-act="share">Chép liên kết</button></div></div>`;
  wireResult(res);
  remember();
}
$('#mh-go').addEventListener('click', () => readMaiHoa(mhInput()));

// ---------------------------------------------------------------- history and links
function remember() {
  if (!current) return;
  const title = current.kind === 'kd' ? `${current.data.cast.ban.full_name}${current.data.cast.bien ? ` → ${current.data.cast.bien.name}` : ''}` : `Mai Hoa: ${current.data.ban.full_name}`;
  const item = { at: new Date().toISOString(), title, q: question(), hash: String(new URLSearchParams(current.share)) };
  store.set([item, ...store.get().filter(x => x.hash !== item.hash)]);
  drawHistory();
}
function drawHistory() {
  const items = store.get();
  let box = $('#kd-history');
  if (!items.length) { box?.remove(); return; }
  if (!box) { box = document.createElement('section'); box.id = 'kd-history'; box.className = 'kd-history'; root.querySelector('.cnote').before(box); }
  box.innerHTML = `<h2>Quẻ đã xem trên máy này</h2><ul>${items.slice(0, 8).map(x => `<li><a href="#${esc(x.hash)}"><span>${esc(x.title)}${x.q ? ` · ${esc(x.q.slice(0, 40))}` : ''}</span><small>${new Date(x.at).toLocaleDateString('vi-VN')}</small></a></li>`).join('')}</ul>`;
}
function fromHash() {
  const h = new URLSearchParams(location.hash.slice(1));
  const t = h.get('t');
  if (t !== null) { const r = $(`input[name=kd-topic][value="${t}"]`); if (r) r.checked = true; }
  if (/^[6-9]{6}$/.test(h.get('q') || '')) { setMode('gieo'); const vals = [...h.get('q')].map(Number); readKinhDich({ values: vals }, { q: h.get('q') }); return; }
  if (h.get('mh')) { try { setMode('mai-hoa'); readMaiHoa(JSON.parse(h.get('mh'))); } catch { /* a broken link */ } }
}
addEventListener('hashchange', fromHash);
drawBuild();
drawHistory();
fromHash();
