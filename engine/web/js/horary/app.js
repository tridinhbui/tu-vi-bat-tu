// Chiêm tinh vấn sự page: ask -> confirm the reading of the question -> chart, judgment and reading. No LLM; every number and
// sentence comes from /api/horary (engine/horary). History lives in this browser (and in the account when signed in); a share
// link carries the moment, the place and the confirmed reading in the URL fragment, which never reaches the server.
import { renderWheel, PLANET_VI, SIGN_VI, ASPECT_VI, fmtPos, fmtDeg } from './wheel.js';

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const HIST_KEY = 'tvbt.horary.history.v1';
const PLACES = {   // city: [lat, lon, IANA zone]; northern cities use tzdb's Asia/Hanoi history (as the birth form does)
  'Hà Nội': [21.0285, 105.8542, 'Asia/Hanoi'], 'TP. Hồ Chí Minh': [10.7769, 106.7009, 'Asia/Ho_Chi_Minh'],
  'Đà Nẵng': [16.0544, 108.2022, 'Asia/Ho_Chi_Minh'], 'Huế': [16.4637, 107.5909, 'Asia/Ho_Chi_Minh'],
  'Hải Phòng': [20.8449, 106.6881, 'Asia/Hanoi'], 'Cần Thơ': [10.0452, 105.7469, 'Asia/Ho_Chi_Minh'],
  'Nha Trang': [12.2388, 109.1967, 'Asia/Ho_Chi_Minh'], 'Đà Lạt': [11.9404, 108.4583, 'Asia/Ho_Chi_Minh'],
  'Vinh': [18.6796, 105.6813, 'Asia/Hanoi'],
};
const TIER_VI = { decisive: 'Quyết định', strong: 'Mạnh', moderate: 'Vừa', minor: 'Nhỏ' };
const VERDICT_CLASS = { favourable: 'pos', conditional: 'cond', unfavourable: 'neg', unclear: 'unc' };
const CONF_VI = { high: 'không có cảnh báo về tính hợp lệ', medium: 'có lưu ý về tính hợp lệ', low: 'có cảnh báo mạnh về tính hợp lệ' };
let catalog = null, rules = null, last = null, cls = null;

async function api(path, body) {
  const r = await fetch(path, body ? { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) } : {});
  let j = {};
  try { j = await r.json(); } catch { /* empty */ }
  if (!r.ok) throw Object.assign(new Error(typeof j.detail === 'string' ? j.detail : 'Máy chủ không trả lời được, hãy thử lại.'), { detail: j.detail, status: r.status });
  return j;
}
const busy = (btn, on) => { btn.classList.toggle('busy', on); btn.disabled = on; };

// ---------------------------------------------------------------- step 1: question, moment, place
const form = $('#hz-form');
form.place.innerHTML = Object.keys(PLACES).map(p => `<option>${p}</option>`).join('') + '<option value="__other">Nơi khác / ngoài Việt Nam</option>';
const syncPlace = () => { $('#hz-other').hidden = form.place.value !== '__other'; };
form.place.onchange = syncPlace;
$$('input[name=when]', form).forEach(r => { r.onchange = () => { $('#hz-manual').hidden = form.when.value !== 'manual'; }; });
$('#hz-geo').onclick = () => navigator.geolocation?.getCurrentPosition(p => {
  form.lat.value = p.coords.latitude.toFixed(4); form.lon.value = p.coords.longitude.toFixed(4);
  form.tz.value = Intl.DateTimeFormat().resolvedOptions().timeZone || form.tz.value;
}, () => { $('#hz-q-tip').textContent = 'Không lấy được vị trí; hãy nhập vĩ độ, kinh độ.'; });

function placeOf() {
  if (form.place.value !== '__other') { const [lat, lon, tz] = PLACES[form.place.value]; return { lat, lon, tz, place: form.place.value }; }
  const lat = parseFloat(form.lat.value), lon = parseFloat(form.lon.value);
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) throw new Error('Hãy nhập vĩ độ và kinh độ của nơi tiếp nhận câu hỏi.');
  return { lat, lon, tz: form.tz.value.trim() || 'UTC', place: `${lat.toFixed(4)}, ${lon.toFixed(4)}` };
}
// tzdb's Asia/Hanoi (backzone) is unknown to browsers; since 1975 it equals Asia/Ho_Chi_Minh, which is all the page needs locally
const browserTz = tz => tz === 'Asia/Hanoi' ? 'Asia/Ho_Chi_Minh' : tz;
function wallClock(date, tz) {      // the instant `date` as wall-clock fields in `tz`
  const f = new Intl.DateTimeFormat('en-GB', { timeZone: browserTz(tz), year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23' });
  const p = Object.fromEntries(f.formatToParts(date).map(x => [x.type, x.value]));
  return { year: +p.year, month: +p.month, day: +p.day, hour: +p.hour, minute: +p.minute, second: +p.second };
}
function moment() {
  const pl = placeOf();
  let t;
  if (form.when.value === 'now') t = wallClock(new Date(), pl.tz);
  else {
    if (!form.date.value || !form.time.value) throw new Error('Hãy chọn ngày và giờ câu hỏi được tiếp nhận.');
    const [y, m, d] = form.date.value.split('-').map(Number), [hh, mm] = form.time.value.split(':').map(Number);
    t = { year: y, month: m, day: d, hour: hh, minute: mm, second: 0 };
  }
  return { ...t, ...pl, house_system: form.house_system.value, school: 'lilly' };
}
const tickNow = () => {
  try { const m = moment(); if (form.when.value === 'now') $('#hz-now').textContent = `Giờ tại ${m.place}: ${String(m.hour).padStart(2, '0')}:${String(m.minute).padStart(2, '0')}, ${m.day}/${m.month}/${m.year}. Thời điểm được chốt khi bạn bấm “Lập bản đồ sao”.`; } catch { /* other place not filled */ }
};
setInterval(tickNow, 20000); tickNow(); form.onchange = tickNow;

form.onsubmit = async e => {
  e.preventDefault();
  const text = form.text.value.trim();
  if (text.length < 8) { $('#hz-q-tip').textContent = 'Hãy viết câu hỏi rõ hơn: việc gì, của ai.'; form.text.focus(); return; }
  const btn = $('#hz-go'); busy(btn, true);
  try {
    catalog ||= await api('/api/horary/catalog');
    cls = await api('/api/horary/classify', { text });
    showConfirm(text, cls);
  } catch (err) { $('#hz-q-tip').textContent = err.message; } finally { busy(btn, false); }
};

// ---------------------------------------------------------------- step 2: confirm the reading of the question
const fr = $('#hz-frame');
function fillTopic(sel) {
  fr.topic.innerHTML = Object.entries(catalog.topics).map(([k, v]) => `<option value="${k}"${k === sel ? ' selected' : ''}>${esc(v.vi)}</option>`).join('');
}
function fillSub(topic, sel) {
  fr.subtype.innerHTML = Object.entries(catalog.topics[topic].subtypes).map(([k, v]) => `<option value="${k}"${k === sel ? ' selected' : ''}>${esc(v.vi)}</option>`).join('');
}
function fillParty(sel) {
  fr.party.innerHTML = Object.entries(catalog.parties).map(([k, v]) => `<option value="${k}"${k === sel ? ' selected' : ''}>${esc(v.vi)}</option>`).join('');
}
function houseLine() {
  const t = catalog.topics[fr.topic.value], st = t.subtypes[fr.subtype.value], ph = catalog.parties[fr.party.value].house;
  const qh = fr.party.value === 'self' ? st.house : ((ph - 1 + st.house - 1) % 12) + 1;
  $('#hz-house').innerHTML = `Bạn ở <b>nhà 1</b>; việc được hỏi ở <b>nhà ${qh}</b>` + (fr.party.value === 'self' ? '' :
    ` (nhà ${st.house} tính từ nhà ${ph} của ${esc(catalog.parties[fr.party.value].vi)}, theo cách “xoay lá số” của Lilly)`) + '.' +
    (t.caution ? `<br><span class="hz-warn">${esc(t.caution)}</span>` : '') +
    (fr.topic.value === 'study' ? '<br><span class="hz-warn">Lilly không có chương riêng về thi cử, nhập học hay học bổng; Thiên Bàn dùng nhà gần nhất theo nghĩa của Lilly và ghi rõ đây là cách vận dụng, không phải quy tắc có sẵn trong sách.</span>' : '');
}
function showConfirm(text, c) {
  $('#hz-confirm').hidden = false;
  const box = $('#hz-cls');
  if (c.restricted.length) {
    box.innerHTML = `<div class="hz-stop"><b>Thiên Bàn không luận câu hỏi này.</b>${c.restricted.map(r => `<p>${esc(r.why)}</p>`).join('')}<p class="note">Bạn có thể hỏi một việc khác.</p></div>`;
    fr.hidden = true; return;
  }
  fr.hidden = false;
  const r0 = c.readings[0];
  fillTopic(r0?.topic || 'career'); fillSub(fr.topic.value, r0?.subtype); fillParty(r0?.party || 'self');
  const reads = c.readings.length ? `<p>Thiên Bàn hiểu câu hỏi như sau${c.readings.length > 1 ? ' (có nhiều cách hiểu, hãy chọn một)' : ''}:</p><ul class="hz-reads">${c.readings.map((r, i) =>
    `<li><label><input type="radio" name="reading" value="${i}"${i === 0 ? ' checked' : ''}> <b>${esc(catalog.topics[r.topic].vi)}</b>: ${esc(catalog.topics[r.topic].subtypes[r.subtype].vi)}`
    + `${r.party !== 'self' ? ` — việc của ${esc(catalog.parties[r.party].vi)}` : ''} <span class="note">(từ khóa: ${esc(r.matched.join(', '))})</span></label></li>`).join('')}</ul>` : '';
  box.innerHTML = reads + (c.reasons.length ? `<ul class="hz-reasons">${c.reasons.map(x => `<li>${esc(x)}</li>`).join('')}</ul>` : '');
  $$('input[name=reading]', box).forEach(inp => { inp.onchange = () => { const r = c.readings[+inp.value]; fillTopic(r.topic); fillSub(r.topic, r.subtype); fillParty(r.party); houseLine(); }; });
  fr.ok.checked = false; $('#hz-judge').disabled = true;
  houseLine();
  $('#hz-confirm').scrollIntoView({ behavior: 'smooth', block: 'start' });
}
fr.topic.onchange = () => { fillSub(fr.topic.value); houseLine(); };
fr.subtype.onchange = houseLine; fr.party.onchange = houseLine;
fr.ok.onchange = () => { $('#hz-judge').disabled = !fr.ok.checked; };
fr.onsubmit = async e => {
  e.preventDefault();
  const btn = $('#hz-judge'); busy(btn, true);
  try {
    const m = moment();
    const frame = { text: form.text.value.trim(), topic: fr.topic.value, subtype: fr.subtype.value, party: fr.party.value, confirmed: true };
    await run(m, frame);
  } catch (err) { $('#hz-house').insertAdjacentHTML('beforeend', `<br><span class="hz-warn">${esc(restrictedMsg(err))}</span>`); } finally { busy(btn, false); }
};
const restrictedMsg = err => err.detail?.restricted ? err.detail.restricted.map(r => r.why).join(' ') : err.message;

// ---------------------------------------------------------------- step 3: result
async function run(m, frame, opts = {}) {
  rules ||= (await api('/api/horary/rules')).rules.reduce((o, r) => (o[r.id] = r, o), {});
  const res = await api('/api/horary/judge', { moment: m, frame, fingerprint: opts.fingerprint || null });
  last = { moment: m, frame, res };
  render(res, opts);
  return res;
}

function render(res, opts = {}) {
  const { chart, judgment: j, reading } = res;
  const v = j.verdict;
  $('#hz-result').hidden = false;
  const vb = $('#hz-verdict-box');
  vb.className = `hz-verdict hz-v-${VERDICT_CLASS[v.label]}`;
  $('#hz-verdict').textContent = v.vi;
  $('#hz-verdict-sub').innerHTML = `Lá số ${esc(CONF_VI[v.confidence])}. ` + (opts.shared ? '<b>Đây là lá số được chia sẻ.</b> ' : '') +
    (res.unchanged === false ? '<b class="hz-warn">Phép tính đã thay đổi so với lúc lưu (phiên bản engine khác); nội dung dưới đây là bản tính mới.</b>' : res.unchanged ? 'Lá số trùng khớp với bản đã lưu.' : '');
  $('#hz-quick').innerHTML = reading.quick.paragraphs.map(p => para(p)).join('');
  $('#hz-deep').innerHTML = reading.deep.sections.map(s => `<section class="hz-sec"><h3>${esc(s.title)}</h3>${s.paragraphs.map(p => para(p)).join('')}</section>`).join('');
  renderWheel($('#hz-wheel'), chart, j, sel => detail(sel, chart, j));
  $('#hz-wheel-cap').textContent = `Hệ nhà ${chart.input.house_system}; vòng ngoài là 12 cung, số trong là 12 nhà. Vòng màu: đỏ son = người hỏi, xanh ngọc = việc được hỏi, xanh lam = Mặt Trăng. Đường liền = đang tiến tới, đứt = đang tách ra. Lịch thiên văn: ${chart.ephemeris.label}.`;
  $('#hz-tables').innerHTML = tables(chart, j);
  $('#hz-flow').innerHTML = flow(j);
  bindRefs($('#hz-result'));
  $('#hz-result').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function para(p) {
  const refs = (p.refs || []).filter(Boolean);
  return `<p>${esc(p.text)}${refs.length ? ` <button type="button" class="hz-ref" data-refs="${esc(refs.join(' '))}" aria-expanded="false">căn cứ</button>` : ''}</p>`;
}
function refHtml(ids) {
  const T = Object.fromEntries((last?.res.judgment.testimonies || []).map(t => [t.id, t]));
  return ids.map(id => {
    const t = T[id];
    const r = rules[id] || (t && rules[t.rule]);
    if (t && !rules[id]) return `<li><b>${esc(TIER_VI[t.tier])}</b> · ${esc(t.vi)}${r ? ruleLine(r) : ''}</li>`;
    if (r) return `<li>${ruleLine(r, true)}</li>`;
    return `<li class="note">${esc(id)}: quy tắc vận hành của Thiên Bàn</li>`;
  }).join('');
}
function ruleLine(r, full) {
  const src = (r.sources || []).map(s => `${s.work === 'LILLY' ? 'Lilly, Christian Astrology' : s.work.startsWith('BONATUS') ? 'Bonatti/Coley' : s.work === 'PTOLEMY' ? 'Ptolemy/Ashmand' : esc(s.work)} tr.${esc(s.page)}`).join('; ');
  return `${full ? `<b>${esc(r.title_vi || r.id)}</b>: ` : '<br><span class="note">'}${esc(r.statement_vi || '')}${full ? '' : '</span>'} <span class="hz-src">${esc(src)}${r.status !== 'classical' ? ` · ${r.status === 'disputed' ? 'có tranh luận' : 'cách vận hành của Thiên Bàn'}` : ''}</span>`;
}
function bindRefs(root) {
  $$('.hz-ref', root).forEach(b => {
    b.onclick = () => {
      const open = b.getAttribute('aria-expanded') === 'true';
      b.setAttribute('aria-expanded', String(!open));
      const nx = b.nextElementSibling;
      if (open && nx?.classList.contains('hz-refbox')) { nx.remove(); return; }
      b.insertAdjacentHTML('afterend', `<ul class="hz-refbox">${refHtml(b.dataset.refs.split(' '))}</ul>`);
    };
  });
}

function detail(sel, chart, j) {
  const box = $('#hz-detail');
  if (sel.kind === 'planet') {
    const b = chart.bodies[sel.id], s = j.strength[sel.id];
    if (!s) { box.innerHTML = `<h3>${PLANET_VI[sel.id]}</h3><p>${fmtPos(b.lon)}, nhà ${b.house}. Hành tinh ngoài hệ bảy sao cổ điển: chỉ vẽ để tham khảo, không dùng để luận (Lilly chỉ dùng bảy hành tinh).</p>`; return; }
    const es = s.essential, L = es.lords;
    const recs = j.receptions.filter(r => r.planet === sel.id || r.by === sel.id);
    box.innerHTML = `<h3>${PLANET_VI[sel.id]}</h3>
      <p><b>${fmtPos(b.lon)}</b>, nhà ${b.house}${b.house_by_cusp_rule ? ' (trong 5° trước đỉnh nhà nên tính vào nhà này, theo Lilly)' : ''}; vĩ độ hoàng đạo ${b.lat.toFixed(2)}°; tốc độ ${b.speed.toFixed(4)}°/ngày${b.retrograde ? ' (nghịch hành)' : ''}.</p>
      <p class="note">Kinh độ biểu kiến, hệ hoàng đạo và xuân phân thực của ngày, lấy từ ${esc(chart.ephemeris.label)}.</p>
      <h4>Phẩm chất thiết yếu (Lilly tr.104)</h4>
      <table class="hz-mini"><tr><th>Nhà</th><th>Vượng</th><th>Tam hợp</th><th>Giới hạn</th><th>Diện</th></tr>
      <tr>${['house', 'exaltation', 'triplicity', 'term', 'face'].map(k => `<td${L[k] === sel.id ? ' class="hz-hit"' : ''}>${L[k] ? PLANET_VI[L[k]] : '—'}</td>`).join('')}</tr></table>
      <p>Điểm thiết yếu <b>${s.essential_score >= 0 ? '+' : ''}${s.essential_score}</b>${es.peregrine ? ' (peregrine: không có phẩm chất nào, −5)' : ''}${es.debilities.length ? `; ${es.debilities.map(d => d === 'detriment' ? 'hãm −5' : 'suy −4').join(', ')}` : ''}.</p>
      <h4>Phẩm chất ngẫu nhiên (Lilly tr.115)</h4>
      <ul class="hz-acc">${s.accidental.items.map(i => `<li><span title="${esc(i.label_en)}">${esc(i.label_vi || i.label_en)}${i.detail ? ` <span class="note">(${esc(i.detail)})</span>` : ''}</span><b>${i.points > 0 ? '+' : ''}${i.points}</b></li>`).join('')}</ul>
      <p>Tổng: <b>${s.total >= 0 ? '+' : ''}${s.total}</b>. <span class="note">${esc(s.note)}</span></p>
      ${recs.length ? `<h4>Tiếp nhận</h4><ul>${recs.map(r => `<li>${PLANET_VI[r.planet]} đứng trong ${({ house: 'nhà', exaltation: 'cung vượng', triplicity: 'tam hợp', term: 'giới hạn', face: 'diện' })[r.dignity]} của ${PLANET_VI[r.by]}${r.mutual_with.length ? ' (lẫn nhau)' : ''}</li>`).join('')}</ul>` : ''}`;
  } else {
    const p = sel.pair, [a, b] = sel.key.split('-');
    const orbs = j.orbs;
    box.innerHTML = `<h3>${PLANET_VI[a]} ${ASPECT_VI[p.angle]} ${PLANET_VI[b]}</h3>
      <p>Lệch khỏi góc chính xác <b>${p.orb.toFixed(2)}°</b>. Orb cho phép theo Lilly là nửa tổng orb hai sao (tr.107, tr.110): (${orbs[a]} + ${orbs[b]}) / 2 = <b>${p.moiety_sum.toFixed(2)}°</b>, nên ${p.within_orb ? 'đang trong orb' : 'ngoài orb'}${p.by_sign ? '; hai cung cũng ở đúng góc này' : '; nhưng hai cung không ở đúng góc này (góc lệch cung)'}.</p>
      <p>${p.motion === 'applying' ? `Đang <b>tiến tới</b> (${PLANET_VI[p.applier]} là sao tiến tới).` : 'Đang <b>tách ra</b>.'} ${p.next_perfection_jd ? `Góc chính xác kế tiếp: ${jdLocal(p.next_perfection_jd, chart)}${p.perfection_before_sign_change === false ? ' (sau khi một trong hai đổi cung)' : ''}.` : ''} ${p.last_perfection_jd ? `Lần chính xác gần nhất: ${jdLocal(p.last_perfection_jd, chart)}.` : ''}</p>
      ${p.refranation ? `<p class="hz-warn">Trước khi chính xác, ${PLANET_VI[p.refranation.station.planet]} đổi chiều (${jdLocal(p.refranation.station.jd, chart)}): quay lui (refranation).</p>` : ''}
      <p class="note">Thời điểm tính trực tiếp từ lịch thiên văn (không ngoại suy từ tốc độ), sai số dưới một giây.</p>`;
  }
}
function jdLocal(jd, chart) {
  const d = new Date((jd - 2440587.5) * 86400000);
  try { return d.toLocaleString('vi-VN', { timeZone: chart.input.julian_calendar ? 'UTC' : browserTz(chart.input.tz), hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit', year: 'numeric' }); }
  catch { return d.toISOString(); }
}

function tables(chart, j) {
  const trad = chart.traditional;
  const sig = j.significators;
  const role = p => p === sig.querent.planet ? 'người hỏi' : p === sig.quesited.planet ? 'việc được hỏi' : p === 'moon' ? 'đồng chủ tinh' : '';
  const rows = Object.values(chart.bodies).map(b => {
    const s = j.strength[b.id];
    return `<tr${role(b.id) ? ' class="hz-row-sig"' : ''}><th scope="row">${PLANET_VI[b.id]}${role(b.id) ? `<br><span class="note">${role(b.id)}</span>` : ''}</th><td>${fmtPos(b.lon)}</td><td>${b.house}</td>
      <td>${b.speed.toFixed(3)}${b.retrograde ? ' ℞' : ''}</td><td>${s ? (s.essential_score >= 0 ? '+' : '') + s.essential_score : '—'}</td><td>${s ? (s.accidental_score >= 0 ? '+' : '') + s.accidental_score : '—'}</td></tr>`;
  }).join('');
  const ess = trad.map(p => {
    const L = j.strength[p].essential.lords;
    return `<tr><th scope="row">${PLANET_VI[p]}</th>${['house', 'exaltation', 'triplicity', 'term', 'face', 'detriment', 'fall'].map(k => `<td${L[k] === p ? ' class="hz-hit"' : ''}>${L[k] ? PLANET_VI[L[k]] : '—'}</td>`).join('')}</tr>`;
  }).join('');
  const recs = j.receptions.filter(r => r.mutual_with.length).map(r => `<li>${PLANET_VI[r.planet]} ↔ ${PLANET_VI[r.by]}: ${({ house: 'nhà', exaltation: 'vượng', triplicity: 'tam hợp', term: 'giới hạn', face: 'diện' })[r.dignity]}</li>`);
  const tl = j.timeline.map(e => {
    const t = jdLocal(e.jd, chart), past = e.jd < chart.jd_ut ? ' class="hz-past"' : '';
    if (e.kind === 'perfection') return `<li${past}><time>${t}</time> ${PLANET_VI[e.a]} ${({ conjunction: 'hội hợp', sextile: 'lục hợp', square: 'vuông góc', trine: 'tam hợp', opposition: 'xung chiếu' })[e.aspect]} ${PLANET_VI[e.b]}</li>`;
    if (e.kind === 'station') return `<li${past}><time>${t}</time> ${PLANET_VI[e.planet]} đứng, chuyển ${e.turns === 'retrograde' ? 'nghịch' : 'thuận'} hành</li>`;
    return `<li${past}><time>${t}</time> ${PLANET_VI[e.planet]} vào ${SIGN_VI[e.sign_to]}${e.retrograde ? ' (lùi)' : ''}</li>`;
  }).join('');
  const cusps = chart.cusps.map((c, i) => `<tr><th scope="row">${i + 1}</th><td>${fmtPos(c)}</td></tr>`).join('');
  return `<div class="hz-tgrid">
    <section><h3>Hành tinh</h3><div class="hz-scroll"><table class="hz-t"><thead><tr><th>Sao</th><th>Vị trí</th><th>Nhà</th><th>°/ngày</th><th>Thiết yếu</th><th>Ngẫu nhiên</th></tr></thead><tbody>${rows}</tbody></table></div>
      <p class="note">Ba hành tinh ngoài (Thiên Vương, Hải Vương, Diêm Vương) chỉ để tham khảo; Lilly luận bằng bảy hành tinh.</p></section>
    <section><h3>Phẩm chất thiết yếu của độ mỗi sao đứng</h3><div class="hz-scroll"><table class="hz-t"><thead><tr><th>Sao</th><th>Nhà</th><th>Vượng</th><th>Tam hợp</th><th>Giới hạn</th><th>Diện</th><th>Hãm</th><th>Suy</th></tr></thead><tbody>${ess}</tbody></table></div>
      <p class="note">Ô tô đậm: sao đang giữ phẩm chất đó tại chỗ của mình. Bảng theo Lilly tr.104; tam hợp lấy chủ ${chart.is_day ? 'ngày' : 'đêm'}.</p></section>
    <section><h3>Tiếp nhận lẫn nhau</h3>${recs.length ? `<ul>${[...new Set(recs)].join('')}</ul>` : '<p class="note">Không có.</p>'}</section>
    <section><h3>Dòng thời gian góc hợp</h3><ol class="hz-tl">${tl}</ol><p class="note">Các sự kiện của chủ tinh hai bên và Mặt Trăng, từ 3 ngày trước đến 60 ngày sau câu hỏi.</p></section>
    <section><h3>Đỉnh các nhà</h3><table class="hz-t hz-t-sm"><tbody>${cusps}</tbody></table>
      <p class="note">Điểm Mọc ${fmtPos(chart.asc)}, Thiên Đỉnh ${fmtPos(chart.mc)}, Điểm May Mắn ${fmtPos(chart.fortune)}, La Hầu ${fmtPos(chart.nodes.north)}.${chart.planetary_hour.available ? ` Giờ hành tinh: ${PLANET_VI[chart.planetary_hour.hour_ruler]} (giờ thứ ${chart.planetary_hour.hour_number}, ngày của ${PLANET_VI[chart.planetary_hour.day_ruler]}).` : ''}</p></section>
  </div>`;
}

function flow(j) {
  const pol = p => p > 0 ? '<span class="hz-pol hz-pol-pos">thuận</span>' : p < 0 ? '<span class="hz-pol hz-pol-neg">nghịch</span>' : '<span class="hz-pol">trung tính</span>';
  const ref = id => `<button type="button" class="hz-ref" data-refs="${esc(id)}" aria-expanded="false">căn cứ</button>`;
  const tli = x => `<li>${pol(x.polarity)} <span class="hz-tier">${TIER_VI[x.tier]}</span> ${esc(x.vi)} ${ref(x.id)}</li>`;
  const sig = j.significators, L1 = sig.querent.planet, LQ = sig.quesited.planet;
  const cons = j.considerations.filter(c => c.applies);
  const ps = j.pairs[`${L1}-${LQ}`] || j.pairs[`${LQ}-${L1}`];
  const rel = j.testimonies.filter(t => ['reception', 'separation', 'no_connection'].includes(t.id) || t.id.startsWith('perfection'));
  const course = j.testimonies.filter(t => ['translation', 'collection', 'prohibition', 'frustration', 'abscission', 'refranation', 'moon_voc', 'moon_applies_quesited'].includes(t.id));
  const st = p => j.strength[p];
  const tm = j.timing;
  return `<ol class="hz-flow">
    <li><h3>Tầng 1 · Tính hợp lệ theo truyền thống</h3>${cons.length ? `<ul>${cons.map(c => `<li><span class="hz-tier">${c.severity === 'strong_caution' ? 'cảnh báo mạnh' : c.severity === 'testimony_against' ? 'chứng cứ nghịch' : 'lưu ý'}</span> ${esc(c.vi)} ${ref(c.id)}</li>`).join('')}</ul><p class="note">Không lời cảnh báo nào tự làm lá số vô hiệu; chúng hạ độ tin cậy của kết luận.</p>` : '<p class="note">Không có lời cảnh báo nào.</p>'}</li>
    <li><h3>Tầng 2 · Chủ tinh</h3><p>Người hỏi: <b>${PLANET_VI[L1]}</b> (chủ nhà 1), sức mạnh ${st(L1).total >= 0 ? '+' : ''}${st(L1).total} · Việc được hỏi: <b>${PLANET_VI[LQ]}</b> (chủ nhà ${sig.quesited.house}), sức mạnh ${st(LQ).total >= 0 ? '+' : ''}${st(LQ).total} · Mặt Trăng: đồng chủ tinh của người hỏi. ${ref('lilly.significator.lord_of_house')}</p></li>
    <li><h3>Tầng 3 · Mối quan hệ</h3>${ps ? `<p>Giữa hai chủ tinh: góc ${ASPECT_VI[ps.angle]}, lệch ${ps.orb.toFixed(2)}° (orb ${ps.moiety_sum.toFixed(2)}°), ${ps.motion === 'applying' ? 'đang tiến tới' : 'đang tách ra'}.</p>` : ''}${rel.length ? `<ul>${rel.map(tli).join('')}</ul>` : ''}</li>
    <li><h3>Tầng 4 · Diễn biến (theo thứ tự thời gian thiên văn)</h3>${course.length ? `<ul>${course.sort((a, b) => (a.jd || 1e12) - (b.jd || 1e12)).map(tli).join('')}</ul>` : '<p class="note">Không có hành tinh thứ ba nào chuyển, thu, ngăn hay phá sự gặp gỡ.</p>'}</li>
    <li><h3>Tầng 5 · Thời gian</h3>${tm ? `<p>${esc(tm.house_rule.vi)} ${ref(tm.house_rule.rule)}</p><p>${esc(tm.sign_rule.vi)} ${ref(tm.sign_rule.rule)}</p><p class="note">${esc(tm.caveat)}</p>` : '<p class="note">Không có cấu hình thành sự nên không ước lượng thời gian.</p>'}</li>
    <li class="hz-flow-end"><h3>Tầng 6 · Tổng hợp</h3><p><b>${esc(j.verdict.vi)}</b>. ${j.verdict.reasons.map(esc).join(' ')}</p>
      <details><summary>Toàn bộ chứng cứ theo tầng (${j.testimonies.length})</summary><ul>${j.testimonies.map(tli).join('')}</ul></details>
      <p class="note">${esc(j.verdict.method)}</p></li>
  </ol>`;
}

// tabs
$$('.hz-tabs [role=tab]').forEach(tab => {
  tab.onclick = () => {
    $$('.hz-tabs [role=tab]').forEach(t => { t.setAttribute('aria-selected', String(t === tab)); $('#' + t.getAttribute('aria-controls')).hidden = t !== tab; });
  };
  tab.onkeydown = e => {
    const tabs = $$('.hz-tabs [role=tab]'), i = tabs.indexOf(tab);
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { const n = tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length]; n.focus(); n.click(); }
  };
});

// ---------------------------------------------------------------- history, share, PDF
const loadHist = () => { try { return JSON.parse(localStorage.getItem(HIST_KEY) || '[]'); } catch { return []; } };
const saveHist = h => { try { localStorage.setItem(HIST_KEY, JSON.stringify(h.slice(0, 100))); return true; } catch { return false; } };
function showHist() {
  const h = loadHist();
  $('#hz-history').hidden = !h.length;
  $('#hz-history-list').innerHTML = h.map((x, i) => `<li><button type="button" class="link" data-i="${i}">${esc(x.frame.text)}</button>
    <span class="note">${x.moment.day}/${x.moment.month}/${x.moment.year} ${String(x.moment.hour).padStart(2, '0')}:${String(x.moment.minute).padStart(2, '0')} · ${esc(x.moment.place)} · ${esc(x.verdict)}</span>
    <button type="button" class="hz-del" data-del="${i}" aria-label="Xóa câu hỏi này">Xóa</button></li>`).join('');
  $$('#hz-history-list [data-i]').forEach(b => { b.onclick = () => { const x = loadHist()[+b.dataset.i]; run(x.moment, x.frame, { fingerprint: x.fingerprint }).catch(err => msg(err.message)); }; });
  $$('#hz-history-list [data-del]').forEach(b => {
    b.onclick = () => {
      const h2 = loadHist(), [gone] = h2.splice(+b.dataset.del, 1); saveHist(h2); showHist();
      if (gone) fetch('/api/me/horary/' + encodeURIComponent(gone.id), { method: 'DELETE', credentials: 'same-origin', headers: { 'x-tvbt': '1' } }).catch(() => {});
    };
  });
}
// signed in: merge the account's saved questions into this device's list (the account copy wins for the same id)
async function syncCloud() {
  try {
    const r = await fetch('/api/me/horary', { credentials: 'same-origin' });
    if (!r.ok) return;
    const { items } = await r.json();
    const byId = new Map(loadHist().map(x => [x.id, x]));
    for (const it of items) byId.set(it.id, it);
    saveHist([...byId.values()].sort((a, b) => (b.saved_at || 0) - (a.saved_at || 0)));
    showHist();
  } catch { /* offline or no accounts */ }
}
const msg = t => { $('#hz-action-msg').textContent = t; };
$('#hz-save').onclick = async () => {
  if (!last) return;
  const item = { id: last.res.fingerprint + '-' + Date.now().toString(36), saved_at: Date.now(), moment: last.moment, frame: last.frame,
    fingerprint: last.res.fingerprint, engine: last.res.engine, verdict: last.res.judgment.verdict.vi };
  const ok = saveHist([item, ...loadHist().filter(x => !(x.fingerprint === item.fingerprint && x.frame.text === item.frame.text))]);
  let cloud = '';
  try {
    const r = await fetch('/api/me/horary', { method: 'POST', credentials: 'same-origin', headers: { 'content-type': 'application/json', 'x-tvbt': '1' }, body: JSON.stringify(item) });
    if (r.ok) cloud = ' và vào tài khoản';
  } catch { /* not signed in or offline */ }
  msg(ok ? `Đã lưu trên thiết bị này${cloud}.` : 'Trình duyệt không cho lưu (chế độ riêng tư?).');
  showHist();
};
const b64u = s => btoa(unescape(encodeURIComponent(s))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const unb64u = s => decodeURIComponent(escape(atob(s.replace(/-/g, '+').replace(/_/g, '/'))));
$('#hz-share').onclick = async () => {
  if (!last) return;
  const withText = confirm('Kèm nội dung câu hỏi trong liên kết chia sẻ?\n\nBấm “Hủy” để chỉ chia sẻ lá số và chủ đề, không kèm câu chữ bạn đã viết.');
  const f = { ...last.frame, text: withText ? last.frame.text : '(câu hỏi không được chia sẻ)' };
  const url = `${location.origin}/chiem-tinh-van-su/#q=${b64u(JSON.stringify({ m: last.moment, f, fp: last.res.fingerprint }))}`;
  try { await navigator.clipboard.writeText(url); msg('Đã chép liên kết. Dữ liệu nằm sau dấu # nên không gửi lên máy chủ khi mở.'); }
  catch { prompt('Chép liên kết này:', url); }
};
$('#hz-pdf').onclick = () => { document.body.classList.add('hz-printing'); requestAnimationFrame(() => requestAnimationFrame(() => window.print())); };
addEventListener('afterprint', () => document.body.classList.remove('hz-printing'));
addEventListener('beforeprint', () => document.body.classList.add('hz-printing'));
$('#hz-new').onclick = () => { $('#hz-result').hidden = true; $('#hz-confirm').hidden = true; form.text.value = ''; form.text.focus(); history.replaceState(null, '', location.pathname); };

showHist(); syncCloud();
const shared = location.hash.match(/^#q=([A-Za-z0-9_-]+)$/);
if (shared) {
  try {
    const s = JSON.parse(unb64u(shared[1]));
    form.text.value = s.f.text;
    run(s.m, { ...s.f, confirmed: true }, { fingerprint: s.fp, shared: true }).catch(err => msg(restrictedMsg(err)));
  } catch { msg('Liên kết chia sẻ không đọc được.'); }
}
