// "Vận hạn": three separate techniques, each in its own panel with a one-line note on its method, never merged into one score.
//   1. Transits: bars from entering to leaving the transit orb, ◆ at each exact hit (hollow when the planet is retrograde), ingress and
//      station markers on a sky lane. Window Ngày / Tháng / Năm with prev/next.
//   2. Annual profections: the current year card and the 12-year cycle.
//   3. Secondary progressions: progressed positions (the progressed Moon first) and the events around the reference date.
import { $, $$, esc } from '../util.js';
import { westPost } from './api.js';
import { bodyName, bodyGlyph, bodyLabel, aspName, aspGlyph, signLabel, signName, posFull, num, dm, fmtDate, zonedMs, zonedParts, isoDay, ASPECT, PLANETS10, SIGN, DIGNITY, SOLAR } from './vocab.js';

const TRANSITING = ['moon', 'sun', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto', 'chiron'];
const DEFAULT_FILTER = { day: TRANSITING, month: TRANSITING.filter(x => x !== 'moon'), year: ['mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto', 'chiron'] };
const SCALE_VI = { day: 'Ngày', month: 'Tháng', year: 'Năm' };

export function initForecast(root, { getCtx }) {
  const T = { scale: 'month', filter: new Set(DEFAULT_FILTER.month), cache: new Map(), refMs: Date.now(), open: new Set() };
  const ctx = () => getCtx();
  const tzOf = () => ctx()?.inp.birth.tz || 'UTC';

  root.innerHTML = `
  <div class="wt-fc-ref"><label class="fld"><span>Ngày tham chiếu</span><input type="date" id="fc-ref" min="1900-01-01" max="2100-12-31"></label>
    <button type="button" class="btn btn-ghost btn-sm" id="fc-today">Hôm nay</button>
    <p class="hint">Dùng chung cho cả ba phần dưới. Giờ hiển thị theo múi giờ nơi sinh (<span id="fc-tz"></span>).</p></div>
  <section class="wt-panel" id="fc-transit" aria-labelledby="fc-tr-h">
    <header class="wt-ph"><h3 id="fc-tr-h">Transit</h3><p class="wt-method">Vị trí các hành tinh đang chạy trên bầu trời so với vị trí gốc. Mỗi vạch là khoảng góc hợp nằm trong orb transit (quy ước của Thiên Bàn); ◆ là lúc chính xác, ◇ là lúc chính xác khi hành tinh đang nghịch hành.</p></header>
    <div class="wt-tl-ctl">
      <div class="seg" role="tablist" aria-label="Khung thời gian">${Object.entries(SCALE_VI).map(([k, v]) => `<button type="button" role="tab" data-scale="${k}" aria-selected="${k === T.scale}">${v}</button>`).join('')}</div>
      <div class="wt-tl-nav"><button type="button" class="btn btn-ghost btn-sm" id="tl-prev" aria-label="Khung trước">‹</button><b id="tl-label" aria-live="polite"></b><button type="button" class="btn btn-ghost btn-sm" id="tl-next" aria-label="Khung sau">›</button></div>
    </div>
    <fieldset class="wt-filter"><legend>Hành tinh đang chạy</legend><div class="chips" id="tl-filter"></div></fieldset>
    <div id="tl-body" class="wt-tl-body" aria-live="polite"></div>
  </section>
  <section class="wt-panel" id="fc-prof" aria-labelledby="fc-pf-h">
    <header class="wt-ph"><h3 id="fc-pf-h">Profection hằng năm</h3><p class="wt-method">Kỹ thuật Hy Lạp cổ đại: mỗi năm tuổi, điểm khởi từ cung Mọc tiến thêm một cung; chủ tinh của cung đến lượt là “chủ năm”. Năm tính từ sinh nhật này đến sinh nhật sau.</p></header>
    <div class="wt-pctl"><label class="fld"><span>Cách đếm</span><div class="sel"><select id="pf-method"><option value="whole_sign">Theo trọn cung (Whole Sign)</option><option value="degree">Theo độ cung Mọc (mỗi năm 30°)</option></select></div></label></div>
    <div id="pf-body" aria-live="polite"></div>
  </section>
  <section class="wt-panel" id="fc-prog" aria-labelledby="fc-pg-h">
    <header class="wt-ph"><h3 id="fc-pg-h">Tiến trình thứ cấp (secondary progressions)</h3><p class="wt-method" id="pg-key">Một ngày sau khi sinh ứng với một năm cuộc đời: vị trí các hành tinh ở ngày thứ N sau ngày sinh là “bản đồ tiến trình” của năm tuổi N.</p></header>
    <div class="wt-pctl"><label class="fld"><span>Cách tiến các trục</span><div class="sel"><select id="pg-angle"><option value="solar_arc">Cung Mặt Trời (solar arc)</option><option value="solar_arc_ra">Cung Mặt Trời theo xích kinh</option><option value="naibod">Naibod (0°59′08″ mỗi năm)</option></select></div></label>
      <label class="fld"><span>Khoảng sự kiện</span><div class="sel"><select id="pg-span"><option value="4">± 2 năm</option><option value="10" selected>± 5 năm</option><option value="20">± 10 năm</option></select></div></label></div>
    <div id="pg-body" aria-live="polite"></div>
  </section>`;

  const refIn = $('#fc-ref', root);
  const setRef = ms => { T.refMs = ms; refIn.value = isoDay(zonedParts(tzOf(), ms)); };
  refIn.addEventListener('change', () => {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(refIn.value); if (!m) return;
    T.refMs = zonedMs(tzOf(), +m[1], +m[2], +m[3], 12, 0); loadAll();
  });
  $('#fc-today', root).onclick = () => { setRef(Date.now()); loadAll(); };

  // ----- transits -----
  const win = () => {
    const tz = tzOf(), p = zonedParts(tz, T.refMs);
    if (T.scale === 'day') return [zonedMs(tz, p.year, p.month, p.day), zonedMs(tz, p.year, p.month, p.day + 1)];
    if (T.scale === 'month') return [zonedMs(tz, p.year, p.month, 1), zonedMs(tz, p.year, p.month + 1, 1)];
    return [zonedMs(tz, p.year, 1, 1), zonedMs(tz, p.year + 1, 1, 1)];
  };
  const winLabel = () => {
    const p = zonedParts(tzOf(), T.refMs);
    return T.scale === 'day' ? `${p.day}/${p.month}/${p.year}` : T.scale === 'month' ? `Tháng ${p.month}/${p.year}` : `Năm ${p.year}`;
  };
  const shift = k => {
    const tz = tzOf(), p = zonedParts(tz, T.refMs);
    T.refMs = T.scale === 'day' ? zonedMs(tz, p.year, p.month, p.day + k, 12) : T.scale === 'month' ? zonedMs(tz, p.year, p.month + k, Math.min(p.day, 28), 12) : zonedMs(tz, p.year + k, p.month, Math.min(p.day, 28), 12);
    setRef(T.refMs); loadAll();
  };
  $('#tl-prev', root).onclick = () => shift(-1);
  $('#tl-next', root).onclick = () => shift(1);
  $$('[data-scale]', root).forEach(b => b.onclick = () => {
    T.scale = b.dataset.scale; T.filter = new Set(DEFAULT_FILTER[T.scale]);
    $$('[data-scale]', root).forEach(x => x.setAttribute('aria-selected', String(x === b)));
    loadTransits();
  });
  const filterEl = $('#tl-filter', root);
  const drawFilter = () => {
    filterEl.innerHTML = TRANSITING.map(id => `<label class="chip-c wt-fchip"><input type="checkbox" value="${id}"${T.filter.has(id) ? ' checked' : ''}><span>${bodyLabel(id)}</span></label>`).join('');
  };
  filterEl.addEventListener('change', e => {
    const v = e.target.value; e.target.checked ? T.filter.add(v) : T.filter.delete(v);
    drawTimeline();
  });

  async function loadTransits() {
    const c = ctx(); if (!c) return;
    const body = $('#tl-body', root), [a, b] = win();
    $('#tl-label', root).textContent = winLabel();
    drawFilter();
    const key = `${JSON.stringify(c.inp)}|${a}|${b}`;
    if (!T.cache.has(key)) {
      body.innerHTML = '<p class="note">Đang tìm các transit…</p>';
      const req = { ...c.inp, start: new Date(a).toISOString(), end: new Date(b).toISOString(), transiting: TRANSITING };
      T.cache.set(key, westPost('transits', req).catch(e => { T.cache.delete(key); throw e; }));
    }
    const my = T.seq = (T.seq || 0) + 1;
    try { const d = await T.cache.get(key); if (my !== T.seq) return; T.data = d; T.win = [a, b]; drawTimeline(); }
    catch (e) { if (my === T.seq) body.innerHTML = `<p class="note">Chưa tải được transit: ${esc(e.message)}</p>`; }
  }

  function ticks(a, b) {
    const tz = tzOf(), p = zonedParts(tz, a), out = [];
    if (T.scale === 'day') for (let h = 0; h <= 21; h += 3) out.push([zonedMs(tz, p.year, p.month, p.day, h), `${h}h`]);
    else if (T.scale === 'month') { const n = new Date(Date.UTC(p.year, p.month, 0)).getUTCDate(); for (let d = 1; d <= n; d++) out.push([zonedMs(tz, p.year, p.month, d), String(d), d === 1 || d % 5 === 0]); }
    else for (let m = 1; m <= 12; m++) out.push([zonedMs(tz, p.year, m, 1), `T${m}`, true]);
    return out.map(([t, l, major = true]) => ({ x: (t - a) / (b - a) * 100, l, major }));
  }

  function drawTimeline() {
    const body = $('#tl-body', root), d = T.data; if (!d) return;
    const [a, b] = T.win, tz = tzOf(), X = iso => Math.min(100, Math.max(0, (Date.parse(iso) - a) / (b - a) * 100));
    const ev = d.events.filter(e => T.filter.has(e.transiting));
    const sky = (d.sky || []).filter(s => T.filter.has(s.body));
    const now = Date.now(), nowX = now >= a && now < b ? (now - a) / (b - a) * 100 : null;
    const grid = ticks(a, b);
    const axis = `<div class="wt-tl-axis" aria-hidden="true">${grid.map(t => `<span class="${t.major ? 'mj' : ''}" style="left:${t.x.toFixed(3)}%">${t.major ? esc(t.l) : ''}</span>`).join('')}</div>`;
    const lines = `<div class="wt-tl-grid" aria-hidden="true">${grid.filter(t => t.major).map(t => `<i style="left:${t.x.toFixed(3)}%"></i>`).join('')}${nowX != null ? `<b class="wt-tl-now" style="left:${nowX.toFixed(3)}%"><span>Bây giờ</span></b>` : ''}</div>`;
    const skyHtml = sky.length ? `<div class="wt-tl-row wt-tl-sky"><div class="wt-tl-lab">Đổi cung · đổi chiều</div><div class="wt-tl-track">${lines}${sky.map(s => {
      const lab = s.type === 'ingress' ? `${bodyName(s.body)} vào ${signName(s.sign)}${s.retrograde ? ' (nghịch hành)' : ''}` : `${bodyName(s.body)} đổi chiều: ${s.turns === 'retrograde' ? 'bắt đầu nghịch hành' : 'đi thuận trở lại'}`;
      const g = s.type === 'ingress' ? `${bodyGlyph(s.body)}→${SIGN[s.sign]?.g || ''}` : `${bodyGlyph(s.body)}${s.turns === 'retrograde' ? 'R' : 'D'}`;
      return `<span class="wt-tl-mk ${s.type}" style="left:${X(s.time).toFixed(3)}%" tabindex="0" role="img" aria-label="${esc(lab)}, ${esc(fmtDate(s.time, tz, { time: true }))}" title="${esc(lab)} · ${esc(fmtDate(s.time, tz, { time: true }))}">${g}</span>`;
    }).join('')}</div></div>` : '';
    const groups = TRANSITING.filter(id => T.filter.has(id)).map(id => [id, ev.filter(e => e.transiting === id).sort((x, y) => (x.start || '').localeCompare(y.start || '') || (x.exact[0] || '').localeCompare(y.exact[0] || ''))]).filter(([, xs]) => xs.length);
    const rowHtml = e => {
      const id = `${e.transiting}-${e.aspect}-${e.natal}-${e.exact[0] || e.start}`, open = T.open.has(id);
      const l = e.start ? X(e.start) : 0, r = e.end ? X(e.end) : 100;
      const name = `${bodyName(e.transiting)} ${aspName(e.aspect)} ${bodyName(e.natal)} gốc`;
      const exact = e.exact.map((t, i) => `<i class="wt-tl-ex${e.retro_at_exact[i] ? ' rx' : ''}" style="left:${X(t).toFixed(3)}%" title="Chính xác ${esc(fmtDate(t, tz, { time: true }))}${e.retro_at_exact[i] ? ' (nghịch hành)' : ''}"></i>`).join('');
      return `<li class="wt-tl-row tone-${ASPECT[e.aspect]?.tone || 'soft'}"><button type="button" class="wt-tl-lab" aria-expanded="${open}" data-row="${esc(id)}" aria-label="${esc(name)}, ${esc(e.start ? 'từ ' + fmtDate(e.start, tz) : 'đã trong orb từ trước')} ${esc(e.end ? 'đến ' + fmtDate(e.end, tz) : 'còn tiếp sau khung')}${e.passes > 1 ? `, ${e.passes} lần chính xác` : ''}">`
        + `<span class="wt-g" aria-hidden="true">${bodyGlyph(e.transiting)} ${aspGlyph(e.aspect)} ${bodyGlyph(e.natal)}</span><span class="wt-tl-nm">${esc(aspName(e.aspect))} ${esc(bodyName(e.natal))}</span>${e.passes > 1 ? `<small>${e.passes} lần</small>` : ''}</button>`
        + `<div class="wt-tl-track"><span class="wt-tl-bar${e.start ? '' : ' cl'}${e.end ? '' : ' cr'}" style="left:${l.toFixed(3)}%;width:${Math.max(.6, r - l).toFixed(3)}%"></span>${exact}</div>`
        + (open ? `<dl class="wt-tl-more wt-dl"><div class="wt-kv"><dt>Vào orb</dt><dd>${e.start ? esc(fmtDate(e.start, tz, { time: true })) : 'trước khung xem'}</dd></div>`
          + `<div class="wt-kv"><dt>Chính xác</dt><dd>${e.exact.map((t, i) => esc(fmtDate(t, tz, { time: true })) + (e.retro_at_exact[i] ? ' <small>(nghịch hành)</small>' : '')).join('<br>') || 'không chính xác trong khung này'}</dd></div>`
          + `<div class="wt-kv"><dt>Ra khỏi orb</dt><dd>${e.end ? esc(fmtDate(e.end, tz, { time: true })) : 'sau khung xem'}</dd></div><div class="wt-kv"><dt>Orb</dt><dd>${dm(e.orb)} · gần nhất ${dm(e.min_orb)}</dd></div></dl>` : '')
        + '</li>';
    };
    body.innerHTML = `<div class="wt-tl">${`<div class="wt-tl-row wt-tl-head"><div class="wt-tl-lab"></div><div class="wt-tl-track">${axis}</div></div>`}${skyHtml}`
      + (groups.length ? groups.map(([id, xs]) => `<section class="wt-tl-g"><h4>${bodyLabel(id)} <small>${xs.length} góc hợp</small></h4><ul>${xs.map(rowHtml).join('')}</ul></section>`).join('')
        : '<p class="note">Không có transit nào của các hành tinh đã chọn trong khung này.</p>')
      + `</div><p class="hint">Vạch mờ dần ở mép: góc hợp đã nằm trong orb trước khung xem hoặc còn kéo dài sau khung. Giờ theo múi ${esc(tz)}.</p>`;
    $$('[data-row]', body).forEach(btn => btn.onclick = () => { const id = btn.dataset.row; T.open.has(id) ? T.open.delete(id) : T.open.add(id); drawTimeline(); $(`[data-row="${CSS.escape(id)}"]`, body)?.focus(); });
    // Grid lines and the "now" marker are drawn once per row track so they line up everywhere.
    $$('.wt-tl-row:not(.wt-tl-head):not(.wt-tl-sky) .wt-tl-track', body).forEach(t => t.insertAdjacentHTML('afterbegin', lines));
  }

  // ----- profections -----
  const pfM = $('#pf-method', root);
  pfM.onchange = () => loadProf();
  async function loadProf() {
    const c = ctx(), host = $('#pf-body', root); if (!c) return;
    if (c.inp.birth.hour == null) { host.innerHTML = '<p class="note">Profection cần giờ sinh, vì điểm xuất phát là cung Mọc.</p>'; return; }
    host.innerHTML = '<p class="note">Đang tính…</p>';
    try {
      const my = T.pfSeq = (T.pfSeq || 0) + 1;
      const d = await westPost('profections', { ...c.inp, when: new Date(T.refMs).toISOString(), method: pfM.value });
      if (my !== T.pfSeq) return;
      const cur = d.current, ln = cur.lord_natal || {}, tz = tzOf();
      const byHouse = Array.from({ length: 12 }, (_, i) => d.cycle.filter(x => x.house === i + 1));
      host.innerHTML = `<div class="wt-pf-cur"><p class="eyebrow">Năm tuổi ${cur.age} · ${esc(fmtDate(cur.start_utc, tz))} – ${esc(fmtDate(cur.end_utc, tz))}</p>`
        + `<p class="wt-pf-big">${signLabel(cur.sign)} · Nhà ${cur.house}</p>`
        + `<dl class="wt-dl"><div class="wt-kv"><dt>Chủ năm</dt><dd><button type="button" class="link" data-pick="planet:${cur.lord}">${bodyLabel(cur.lord)}</button></dd></div>`
        + `<div class="wt-kv"><dt>Chủ năm ở bản đồ gốc</dt><dd>${signLabel(ln.sign)}, Nhà ${ln.house ?? '—'}${ln.retrograde ? ', nghịch hành' : ''}${ln.essential?.length ? ` · có ${esc(ln.essential.map(k => DIGNITY[k] || k).join(', '))}` : ''}${ln.debilities?.length ? ` · ${esc(ln.debilities.map(k => DIGNITY[k] || k).join(', '))}` : ''}${ln.solar ? ` · ${esc(SOLAR[ln.solar] || ln.solar)}` : ''}</dd></div>`
        + (cur.method === 'degree' ? `<div class="wt-kv"><dt>Điểm profection</dt><dd>${esc(cur.fmt)} ${signLabel(cur.sign)}</dd></div>` : '')
        + `<div class="wt-kv"><dt>Hành tinh gốc trong cung này</dt><dd>${cur.natal_planets_in_sign?.length ? cur.natal_planets_in_sign.map(bodyLabel).join(', ') : 'Không có'}</dd></div></dl></div>`
        + `<h4 class="wt-dsub">Chu kỳ 12 năm</h4><div class="tbl-wrap"><table class="tbl wt-tbl wt-pf-tbl"><thead><tr><th scope="col">Nhà</th><th scope="col">Cung</th><th scope="col">Chủ năm</th><th scope="col">Các tuổi</th></tr></thead><tbody>`
        + byHouse.map((xs, i) => {
          const f = xs[0] || {}, here = xs.some(x => x.age === cur.age);
          return `<tr${here ? ' class="wt-cur" aria-current="true"' : ''}><th scope="row">Nhà ${i + 1}</th><td>${f.sign ? signLabel(f.sign) : ''}</td><td>${f.lord ? bodyLabel(f.lord) : ''}</td><td class="wt-ages">${xs.map(x => x.age === cur.age ? `<b>${x.age}</b>` : x.age).join(' · ')}</td></tr>`;
        }).join('') + '</tbody></table></div>'
        + (pfM.value === 'degree' ? '<p class="hint">Cách đếm theo độ: cung và chủ năm trong bảng là của điểm profection đầu mỗi năm tuổi.</p>' : '');
    } catch (e) { host.innerHTML = `<p class="note">${esc(e.message)}</p>`; }
  }

  // ----- progressions -----
  const pgA = $('#pg-angle', root), pgS = $('#pg-span', root);
  pgA.onchange = pgS.onchange = () => loadProg();
  async function loadProg() {
    const c = ctx(), host = $('#pg-body', root); if (!c) return;
    host.innerHTML = '<p class="note">Đang tính…</p>';
    try {
      const my = T.pgSeq = (T.pgSeq || 0) + 1;
      const d = await westPost('progressions', { ...c.inp, when: new Date(T.refMs).toISOString(), angle_method: pgA.value, span_years: +pgS.value });
      if (my !== T.pgSeq) return;
      const p = d.progressed, tz = tzOf(), m = p.bodies.moon;
      if (d.timeline?.key) $('#pg-key', root).textContent = `${d.timeline.key.replace(/^./, x => x.toUpperCase())}: vị trí các hành tinh N ngày sau lúc sinh là bản đồ tiến trình của năm tuổi N.`;
      const rows = Object.entries(p.bodies).map(([id, b]) => `<tr${id === 'moon' ? ' class="wt-cur"' : ''}><th scope="row">${bodyLabel(id)}</th><td>${posFull(b)}</td><td>${b.natal_house ?? '—'}</td><td>${b.retrograde ? '<b class="wt-rx">R</b>' : ''}</td></tr>`).join('')
        + (p.angles ? ['asc', 'mc'].filter(k => p.angles[k]).map(k => `<tr class="wt-pt"><th scope="row">${bodyLabel(k)}</th><td>${posFull(p.angles[k])}</td><td></td><td></td></tr>`).join('') : '');
      const evs = (d.timeline?.events || []);
      const evTxt = e => e.type === 'aspect' ? `${bodyName(e.progressed)} tiến trình ${aspName(e.aspect)} ${bodyName(e.natal)} gốc`
        : e.type === 'ingress' ? `${bodyName(e.progressed)} tiến trình vào ${signName(e.sign)}` : `${bodyName(e.progressed)} tiến trình vào Nhà ${e.house} gốc`;
      const now = T.refMs;
      host.innerHTML = `<div class="wt-pg-moon"><p class="eyebrow">Mặt Trăng tiến trình · tuổi ${num(p.age_years, 2)}</p><p class="wt-pf-big">${posFull(m)}${m.natal_house ? ` · Nhà ${m.natal_house} gốc` : ''}</p>`
        + `<p class="hint">Ngày tiến trình tương ứng: ${esc(fmtDate(p.progressed_date_utc, c.inp.birth.tz, { time: true }))}${p.moon_phase != null ? ` · góc Mặt Trăng–Mặt Trời tiến trình ${num(p.moon_phase, 1)}°` : ''}. Mặt Trăng tiến trình đi khoảng một cung trong hai năm rưỡi, nên được theo dõi riêng.</p></div>`
        + `<div class="wt-two"><div><h4 class="wt-dsub">Vị trí tiến trình</h4><div class="tbl-wrap"><table class="tbl wt-tbl"><thead><tr><th scope="col">Thiên thể</th><th scope="col">Vị trí</th><th scope="col">Nhà gốc</th><th scope="col">R</th></tr></thead><tbody>${rows}</tbody></table></div>`
        + (p.angles?.method ? `<p class="hint">Trục tiến theo ${esc({ solar_arc: 'cung Mặt Trời', solar_arc_ra: 'cung Mặt Trời theo xích kinh', naibod: 'Naibod' }[p.angles.method] || p.angles.method)}.</p>` : '') + '</div>'
        + `<div><h4 class="wt-dsub">Sự kiện từ tuổi ${num(d.timeline?.from_age, 1)} đến ${num(d.timeline?.to_age, 1)}</h4>`
        + (evs.length ? `<ol class="wt-pg-ev">${evs.map((e, i) => { const past = Date.parse(e.date) < now, mark = !past && (i === 0 || Date.parse(evs[i - 1].date) < now) ? `<li class="wt-pg-now" aria-label="Ngày tham chiếu"><span>Ngày tham chiếu ${esc(fmtDate(new Date(now).toISOString(), tz))}</span></li>` : '';
          return mark + `<li class="${past ? 'past' : 'next'}${e.progressed === 'moon' ? ' moon' : ''}"><time>${esc(fmtDate(e.date, tz))}</time><span>${esc(evTxt(e))}</span><small>tuổi ${num(e.age, 1)}${e.years_in_orb != null ? ` · trong orb ~${num(e.years_in_orb, 1)} năm` : ''}</small></li>`; }).join('')}</ol>` : '<p class="note">Không có sự kiện tiến trình nào trong khoảng này.</p>')
        + '</div></div>';
    } catch (e) { host.innerHTML = `<p class="note">${esc(e.message)}</p>`; }
  }

  function loadAll() { loadTransits(); loadProf(); loadProg(); }
  return {
    /** New natal chart: reset the reference date to today and reload all three panels. */
    load() { $('#fc-tz', root).textContent = tzOf(); setRef(Date.now()); T.open.clear(); loadAll(); },
  };
}
export { PLANETS10 };
