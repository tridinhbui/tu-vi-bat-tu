// "Trưởng thành" tab: Personal Growth & Life Guidance on top of the computed chart.
// Every insight shows its three layers (biểu tượng / tâm lý / đời sống) and the chart facts it rests on. The journal and practice tracker live
// only in this browser (localStorage, keyed by a hash of the birth data, never the raw data); the server computes reviews statelessly.
import { $, $$, esc, post } from './util.js';
import { notice } from './ui.js';

const DOM = { self: 'Bản thân', career: 'Nghề nghiệp', money: 'Tiền bạc', love: 'Tình cảm', family: 'Gia đình', health: 'Sức khỏe' };
const LAYER = { bieu_tuong: 'Biểu tượng truyền thống', tam_ly: 'Góc nhìn tâm lý học', doi_song: 'Đời sống thực' };
const RES = { dung: 'Đúng với tôi', mot_phan: 'Đúng một phần', khong: 'Không đúng' };
const ZONES = { control: 'Kiểm soát được', influence: 'Ảnh hưởng được', outside: 'Ngoài tầm tay', unsure: 'Chưa rõ' };
const SECTIONS = [['gr-les', 'Bài học'], ['gr-bs', 'Điểm mù'], ['gr-stuck', 'Khi bế tắc'], ['gr-cmp', 'La bàn'], ['gr-prac', 'Bài tập'], ['gr-jr', 'Nhật ký'], ['gr-chat', 'Đối thoại']];
const today = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; };
const opts = (o, sel) => Object.entries(o).map(([k, v]) => `<option value="${k}"${k === sel ? ' selected' : ''}>${esc(v)}</option>`).join('');

// ---------- local store (journal + practices), per chart ----------
function keyOf(req) {
  const s = ['year', 'month', 'day', 'hour', 'minute', 'gender'].map(k => req[k]).join('|');
  let h = 2166136261; for (const c of s) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); }
  return 'tvbt-growth-v1:' + (h >>> 0).toString(36);
}
function store(req) {
  const k = keyOf(req);
  const read = () => { try { const v = JSON.parse(localStorage.getItem(k)); return v && Array.isArray(v.entries) ? v : { entries: [], practices: [] }; } catch { return { entries: [], practices: [] }; } };
  const write = v => { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch { return false; } };
  return { read, write, clear: () => { try { localStorage.removeItem(k); } catch { /* ignore */ } } };
}

// ---------- shared renderers ----------
const anchorsHtml = (ids, A) => ids.map(i => A[i]).filter(Boolean).map(a => `<li><span class="gr-sys">${a.system === 'bat_tu' ? 'Bát Tự' : 'Tử Vi'}</span>${esc(a.text)}</li>`).join('');
function layers(it) {
  const L = it.layers, b = L.bieu_tuong, t = L.tam_ly;
  return `<div class="gr-layers">
    <section class="gr-l gr-l-sym"><h5>${LAYER.bieu_tuong}</h5><p>${esc(b.text)}</p><p class="gr-src">${esc(b.source_label)}${b.cites.length ? ' · ' + esc(b.cites.join('; ')) : ''}</p></section>
    <section class="gr-l gr-l-psy"><h5>${LAYER.tam_ly}</h5><p><b>${esc(t.concept.name)}.</b> ${esc(t.text)}</p><p class="gr-src">${esc(t.concept.ref)} · ${esc(t.note)}</p></section>
    <section class="gr-l gr-l-life"><h5>${LAYER.doi_song}</h5><p>${esc(L.doi_song.text)}</p></section></div>`;
}
function exercise(it) {
  const e = it.exercise;
  return `<div class="gr-ex">
    <h5>Câu hỏi phản tư</h5><ul>${e.questions.map(q => `<li>${esc(q)}</li>`).join('')}</ul>
    <h5>Tình huống thực tế</h5><p>${esc(e.scenario.situation)} <b>Thử:</b> ${esc(e.scenario.try)}</p>
    <h5>Hành động nhỏ</h5><ul class="gr-pl">${e.practices.map((p, i) => `<li><span class="badge">${p.days} ngày</span> ${esc(p.action)} <span class="muted small">Theo dõi: ${esc(p.track)}</span> <button type="button" class="link" data-start="${esc(it.id)}#${i}">Bắt đầu</button></li>`).join('')}</ul></div>`;
}
function card(it, A, i) {
  const sh = it.shadow;
  return `<article class="gr-card${i >= 4 ? ' gr-more' : ''}" id="gi-${esc(it.id)}" ${i >= 4 ? 'hidden' : ''}>
    <p class="eyebrow">${it.kind === 'lesson' ? 'Bài học' : 'Điểm mù'} · ${it.domains.map(d => esc(DOM[d] || d)).join(', ')}</p>
    <h4>${esc(it.title)}</h4>
    ${it.skill ? `<p class="gr-skill"><b>Năng lực nên rèn:</b> ${esc(it.skill)}</p>` : ''}
    ${sh ? `<dl class="gr-sh"><div><dt>Mâu thuẫn nội tâm</dt><dd>${esc(sh.conflict)}</dd></div><div><dt>Thói quen tự cản trở</dt><dd>${esc(sh.habit)}</dd></div><div><dt>Cách nhận diện</dt><dd><ul>${sh.signals.map(s => `<li>${esc(s)}</li>`).join('')}</ul></dd></div><div><dt>Điều chỉnh</dt><dd>${esc(sh.adjust)}</dd></div></dl>` : ''}
    <details class="gr-basis"><summary>Căn cứ trên lá số</summary><ul>${anchorsHtml(it.anchors, A)}</ul></details>
    ${layers(it)}
    <details class="acc"><summary><span class="acc-t">Thực hành</span><span class="acc-s">câu hỏi, tình huống, việc nhỏ 7–30 ngày</span></summary><div class="acc-b">${exercise(it)}</div></details>
    <div class="gr-res" role="group" aria-label="Nhận định này có đúng với bạn không?"><span class="muted small">Với bạn, nhận định này:</span>${Object.entries(RES).map(([k, v]) => `<button type="button" class="chip-b" data-res="${k}" data-ins="${esc(it.id)}">${v}</button>`).join('')}</div>
  </article>`;
}
const list = (items, A, label) => items.map((it, i) => card(it, A, i)).join('') + (items.length > 4 ? `<button type="button" class="btn btn-ghost btn-sm gr-showmore">Xem thêm ${items.length - 4} ${label}</button>` : '');

// ---------- main ----------
export async function initGrowth(host, tab, req) {
  let p;
  try { p = await post('/api/growth/profile', req, { retries: 0 }); }
  catch { tab.hidden = true; host.innerHTML = ''; return null; }   // layer disabled (404) or unavailable: the tab simply does not appear
  tab.hidden = false;
  const A = Object.fromEntries(p.anchors.map(a => [a.id, a])), all = [...p.lessons, ...p.blind_spots], byId = Object.fromEntries(all.map(i => [i.id, i]));
  const st = store(req), prac = Object.fromEntries(p.practices.map(x => [x.id, x]));
  host.innerHTML = `
    ${notice('Lá số là tấm gương để tự hỏi, không phải để biết trước', esc(p.disclaimer) + ' <b>' + esc(p.barnum.name) + ':</b> ' + esc(p.barnum.gist), 'info')}
    <ul class="gr-legend">${Object.entries(p.layers_legend).map(([k, v]) => `<li class="gr-lg-${k}">${esc(v)}</li>`).join('')}</ul>
    <nav class="gr-nav" aria-label="Các phần của tầng Trưởng thành">${SECTIONS.map(([id, t]) => `<a href="#${id}" data-gr="${id}">${t}</a>`).join('')}</nav>
    ${p.stage.lines.length ? `<section class="gr-stage"><p class="eyebrow">Giai đoạn hiện tại · năm ${p.stage.year} · tuổi mụ ${p.stage.age_tuoi_mu}</p>${p.stage.lines.map(l => `<p>${esc(l)}</p>`).join('')}<p class="muted small">${esc(p.stage.how_to_use)}</p><ul>${p.stage.questions.map(q => `<li>${esc(q)}</li>`).join('')}</ul></section>` : ''}
    <section id="gr-les" class="gr-sec"><h3>Bài học cuộc đời</h3><p class="sec-sub">Từ tổ hợp sao, nhóm sao, Tứ Hóa và ngũ hành: những bài học để suy ngẫm và năng lực nên rèn luyện.</p>${list(p.lessons, A, 'bài học')}</section>
    <section id="gr-bs" class="gr-sec"><h3>Điểm mù bản thân</h3><p class="sec-sub">Mâu thuẫn nội tâm và thói quen tự cản trở, cách nhận diện và điều chỉnh. Nếu điều gì không khớp với bạn, hãy đánh dấu “Không đúng”.</p>${list(p.blind_spots, A, 'điểm mù')}</section>
    <section id="gr-stuck" class="gr-sec"><h3>Khi cuộc đời bế tắc</h3><p class="sec-sub">Tự đánh giá vấn đề, đặt câu hỏi đúng, tách điều kiểm soát được khỏi điều không kiểm soát được. Bạn tự xếp từng mục; hệ thống chỉ gợi ý.</p><div id="gr-stuck-host"></div></section>
    <section id="gr-cmp" class="gr-sec"><h3>La bàn cuộc đời</h3><p class="sec-sub">Xu hướng (theo hình tượng lá số) có thể ảnh hưởng quyết định của bạn ở từng lĩnh vực, và một công cụ đặt các lựa chọn cạnh giá trị của bạn. Hệ thống không chọn thay bạn.</p><div id="gr-cmp-host"></div></section>
    <section id="gr-prac" class="gr-sec"><h3>Bài tập thực hành</h3><p class="sec-sub">Chọn “Bắt đầu” ở bất kỳ nhận định nào. Mỗi ngày đánh dấu đã làm; tiến độ được ghi vào nhật ký của bạn.</p><div id="gr-prac-host"></div></section>
    <section id="gr-jr" class="gr-sec"><h3>Nhật ký trưởng thành</h3><p class="sec-sub">Ghi lại trải nghiệm, đối chiếu với luận giải, và nhìn lại sự thay đổi của bạn theo thời gian. Chỉ lưu trong trình duyệt này.</p><div id="gr-jr-host"></div></section>
    <section id="gr-chat" class="gr-sec"><h3>Đối thoại với lá số</h3><p class="sec-sub">Hỏi về điều bạn đang gặp. Câu trả lời được ghép từ hồ sơ lá số của bạn và điều bạn chia sẻ, bằng quy tắc cố định.</p><div id="gr-chat-host"></div></section>`;

  $$('.gr-showmore', host).forEach(b => b.onclick = () => { $$('.gr-more', b.parentElement).forEach(c => c.hidden = false); b.remove(); });
  $$('[data-gr]', host).forEach(a => a.onclick = e => { e.preventDefault(); $('#' + a.dataset.gr, host)?.scrollIntoView({ behavior: 'smooth', block: 'start' }); });

  // ----- practices tracker -----
  const pracHost = $('#gr-prac-host', host);
  function startPractice(pid) {
    const v = st.read();
    if (!v.practices.some(x => x.id === pid)) v.practices.unshift({ id: pid, start: today() });
    if (!st.write(v)) { pracHost.insertAdjacentHTML('afterbegin', notice('Trình duyệt không cho phép lưu', 'Chế độ riêng tư hoặc đã chặn lưu trữ.', 'warn')); return; }
    paintPractices(); $('#gr-prac', host).scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function paintPractices() {
    const v = st.read(), act = v.practices.filter(x => prac[x.id]);
    const done = id => new Set(v.entries.filter(e => e.practice_id === id && e.practice_done).map(e => e.date));
    pracHost.innerHTML = (act.length ? `<ul class="gr-track">${act.map(x => {
      const P = prac[x.id], d = done(x.id), t = today(), n = Math.min(d.size, P.days);
      return `<li><div class="gr-tr-h"><b>${esc(P.action)}</b><span class="badge">${n}/${P.days} ngày</span></div><div class="gr-bar" role="progressbar" aria-valuemin="0" aria-valuemax="${P.days}" aria-valuenow="${n}"><i style="width:${Math.round(100 * n / P.days)}%"></i></div>
        <p class="muted small">Từ “${esc(P.title)}” · bắt đầu ${esc(x.start)} · theo dõi: ${esc(P.track)}</p>
        <div class="gr-tr-a">${d.has(t) ? '<span class="badge ok">Hôm nay đã làm</span>' : `<button type="button" class="btn btn-sm" data-done="${esc(x.id)}">Hôm nay đã làm</button>`}<button type="button" class="link" data-stop="${esc(x.id)}">Dừng bài tập</button></div></li>`;
    }).join('')}</ul>` : '<p class="muted">Chưa có bài tập nào đang theo. Mở mục “Thực hành” ở một bài học hoặc điểm mù và bấm “Bắt đầu”.</p>')
      + `<details class="gr-cat"><summary>Tất cả bài tập trong hồ sơ của bạn (${p.practices.length})</summary><ul>${p.practices.map(x => `<li><span class="badge">${x.days} ngày</span> ${esc(x.action)} <button type="button" class="link" data-start="${esc(x.id)}">Bắt đầu</button></li>`).join('')}</ul></details>`;
    $$('[data-done]', pracHost).forEach(b => b.onclick = () => { const v2 = st.read(); v2.entries.push({ date: today(), text: 'Đã làm bài tập: ' + prac[b.dataset.done].action, domain: prac[b.dataset.done].domains[0] || 'self', practice_id: b.dataset.done, practice_done: true }); st.write(v2); paintPractices(); paintJournal(); });
    $$('[data-stop]', pracHost).forEach(b => b.onclick = () => { const v2 = st.read(); v2.practices = v2.practices.filter(x => x.id !== b.dataset.stop); st.write(v2); paintPractices(); });
  }
  host.addEventListener('click', e => {
    const s = e.target.closest('[data-start]'); if (s) { startPractice(s.dataset.start); return; }
    const r = e.target.closest('[data-res]');
    if (r) { jrForm.insight_id.value = r.dataset.ins; jrForm.resonance.value = r.dataset.res; jrForm.domain.value = byId[r.dataset.ins]?.domains[0] || 'self'; jrForm.text.focus(); $('#gr-jr', host).scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  });

  // ----- journal -----
  const jrHost = $('#gr-jr-host', host);
  jrHost.innerHTML = `<form class="gr-form" id="gr-jr-form">
      <div class="gr-row"><label class="fld"><span>Ngày</span><input type="date" name="date" value="${today()}" required></label>
      <label class="fld"><span>Lĩnh vực</span><div class="sel"><select name="domain">${opts(DOM, 'self')}</select></div></label>
      <label class="fld"><span>Tâm trạng (1–5)</span><div class="sel"><select name="mood"><option value="">—</option>${[1, 2, 3, 4, 5].map(n => `<option>${n}</option>`).join('')}</select></div></label></div>
      <div class="gr-row"><label class="fld"><span>Đối chiếu với nhận định</span><div class="sel"><select name="insight_id"><option value="">(không chọn)</option>${all.map(i => `<option value="${esc(i.id)}">${esc(i.title)}</option>`).join('')}</select></div></label>
      <label class="fld"><span>Nhận định đó với bạn</span><div class="sel"><select name="resonance"><option value="">—</option>${opts(RES)}</select></div></label></div>
      <label class="fld"><span>Trải nghiệm hôm nay</span><textarea name="text" rows="3" maxlength="4000" placeholder="Chuyện gì đã xảy ra? Bạn đã phản ứng thế nào? Lần sau muốn thử khác điều gì?"></textarea></label>
      <div class="gr-act"><button class="btn btn-sm" type="submit">Lưu ghi chép</button><button class="btn btn-ghost btn-sm" type="button" id="gr-jr-rev">Đối chiếu và nhìn lại</button><button class="btn btn-ghost btn-sm" type="button" id="gr-jr-exp">Xuất JSON</button><label class="btn btn-ghost btn-sm gr-file">Nhập JSON<input type="file" accept="application/json" id="gr-jr-imp" hidden></label><button class="link" type="button" id="gr-jr-clr">Xóa toàn bộ nhật ký</button></div>
      <p class="muted small">Nhật ký chỉ nằm trong trình duyệt này. Khi bạn bấm “Đối chiếu”, các ghi chép được gửi để tính toán rồi bỏ đi, máy chủ không lưu.</p></form>
    <div id="gr-jr-list"></div><div id="gr-jr-out" aria-live="polite"></div>`;
  const jrForm = $('#gr-jr-form', jrHost);
  function paintJournal() {
    const es = st.read().entries.slice().sort((a, b) => b.date.localeCompare(a.date));
    $('#gr-jr-list', jrHost).innerHTML = es.length ? `<h5 class="gr-h5">${es.length} ghi chép</h5><ul class="gr-entries">${es.slice(0, 30).map(e => `<li><span class="muted small">${esc(e.date)} · ${esc(DOM[e.domain] || '')}${e.mood ? ' · tâm trạng ' + e.mood : ''}${e.resonance ? ' · ' + esc(RES[e.resonance]) : ''}</span>${e.insight_id && byId[e.insight_id] ? `<span class="small"> — ${esc(byId[e.insight_id].title)}</span>` : ''}<p>${esc(e.text)}</p></li>`).join('')}</ul>` : '';
  }
  jrForm.onsubmit = e => {
    e.preventDefault();
    const f = jrForm, v = st.read();
    if (!f.text.value.trim() && !f.resonance.value) { f.text.focus(); return; }
    v.entries.push({ date: f.date.value || today(), domain: f.domain.value, text: f.text.value.trim(), mood: f.mood.value ? +f.mood.value : undefined, insight_id: f.insight_id.value || undefined, resonance: f.resonance.value || undefined });
    if (!st.write(v)) { $('#gr-jr-out', jrHost).innerHTML = notice('Trình duyệt không cho phép lưu', 'Chế độ riêng tư hoặc đã chặn lưu trữ.', 'warn'); return; }
    f.text.value = ''; f.resonance.value = ''; f.insight_id.value = ''; paintJournal();
  };
  $('#gr-jr-rev', jrHost).onclick = async () => {
    const out = $('#gr-jr-out', jrHost); out.innerHTML = '<p class="muted">Đang đối chiếu…</p>';
    try { renderReview(out, await post('/api/growth/journal-review', { birth: req, entries: st.read().entries })); }
    catch (x) { out.innerHTML = notice('Chưa đối chiếu được', esc(x.message), 'warn'); }
  };
  $('#gr-jr-exp', jrHost).onclick = () => {
    const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify(st.read(), null, 2)], { type: 'application/json' }));
    a.download = 'nhat-ky-truong-thanh.json'; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  };
  $('#gr-jr-imp', jrHost).onchange = async e => {
    const f = e.target.files[0]; if (!f) return;
    try {
      const v = JSON.parse(await f.text()), cur = st.read();
      if (!v || !Array.isArray(v.entries)) throw new Error('Tệp không đúng định dạng nhật ký.');
      const seen = new Set(cur.entries.map(x => x.date + '|' + x.text));
      cur.entries.push(...v.entries.filter(x => x && typeof x.date === 'string' && !seen.has(x.date + '|' + x.text)).slice(0, 1000));
      (v.practices || []).forEach(x => { if (x && !cur.practices.some(y => y.id === x.id)) cur.practices.push(x); });
      st.write(cur); paintJournal(); paintPractices();
    } catch (x) { $('#gr-jr-out', jrHost).innerHTML = notice('Không nhập được', esc(x.message), 'warn'); }
  };
  $('#gr-jr-clr', jrHost).onclick = () => { if (confirm('Xóa toàn bộ nhật ký và bài tập của lá số này khỏi trình duyệt? Không thể hoàn tác.')) { st.clear(); paintJournal(); paintPractices(); $('#gr-jr-out', jrHost).innerHTML = ''; } };
  function renderReview(out, r) {
    if (!r.count) { out.innerHTML = `<p class="muted">${esc(r.message)}</p>`; return; }
    out.innerHTML = `<div class="gr-review"><p><b>${r.count} ghi chép</b> từ ${esc(r.from)} đến ${esc(r.to)} (${r.weeks} tuần).</p>
      ${r.mood.trend ? `<p>${esc(r.mood.trend.text)} <span class="muted small">(trung bình ${r.mood.trend.early} → ${r.mood.trend.late})</span></p>` : ''}
      <p class="muted small">Lĩnh vực: ${r.domains.map(d => `${esc(d.label)} ${d.count}`).join(' · ')}</p>
      ${r.resonance.length ? `<h5 class="gr-h5">Bạn đối chiếu với luận giải</h5><ul>${r.resonance.map(x => `<li><b>${esc(x.title)}</b> — đúng ${x.dung}, một phần ${x.mot_phan}, không đúng ${x.khong}. ${esc(x.verdict)}</li>`).join('')}</ul>` : ''}
      ${r.practices.length ? `<h5 class="gr-h5">Bài tập</h5><ul>${r.practices.map(x => `<li>${esc(x.action || x.practice)} — ${esc(x.text)}</li>`).join('')}</ul>` : ''}
      ${r.word_shifts.length ? `<h5 class="gr-h5">Sự thay đổi trong cách bạn viết</h5><ul>${r.word_shifts.map(x => `<li><b>${esc(x.title)}</b>: ${esc(x.text)} <span class="muted small">(${x.early} → ${x.late})</span></li>`).join('')}</ul>` : ''}
      ${r.not_yet_reflected.length ? `<h5 class="gr-h5">Chưa đối chiếu</h5><ul>${r.not_yet_reflected.map(x => `<li><a class="link" href="#gi-${esc(x.insight)}">${esc(x.title)}</a></li>`).join('')}</ul>` : ''}
      <h5 class="gr-h5">Câu hỏi cho chặng tới</h5><ul>${r.next_questions.map(q => `<li>${esc(q)}</li>`).join('')}</ul>
      <p class="muted small">${esc(r.barnum.name)}: ${esc(r.barnum.gist)} ${esc(r.privacy)}</p></div>`;
  }

  // ----- stuck navigator -----
  const sh = $('#gr-stuck-host', host);
  const row = (t = '', z = 'unsure') => `<div class="gr-crow"><input type="text" maxlength="400" placeholder="Một điều đang góp phần vào bế tắc" value="${esc(t)}"><div class="sel sel-sm"><select aria-label="Thuộc cột">${opts(ZONES, z)}</select></div><button type="button" class="link" data-rm>Xóa</button></div>`;
  sh.innerHTML = `<form class="gr-form" id="gr-st-form">
      <div class="gr-row"><label class="fld"><span>Lĩnh vực</span><div class="sel"><select name="domain">${opts(DOM, 'career')}</select></div></label>
      <label class="fld"><span>Đã kéo dài</span><div class="sel"><select name="duration"><option value="">—</option><option>Dưới 1 tháng</option><option>1–6 tháng</option><option>Trên 6 tháng</option><option>Nhiều năm</option></select></div></label></div>
      <label class="fld"><span>Chuyện gì đang xảy ra?</span><textarea name="situation" rows="3" maxlength="1500" placeholder="Kể như một máy quay: sự kiện, không lời bình."></textarea></label>
      <label class="fld"><span>Bạn đã thử gì?</span><input type="text" name="tried" maxlength="1000"></label>
      <fieldset class="fld"><legend>Các yếu tố — tự xếp vào cột</legend><div id="gr-crows">${row()}${row()}${row()}</div><button type="button" class="link" id="gr-cadd">+ Thêm yếu tố</button></fieldset>
      <div class="gr-act"><button class="btn btn-sm" type="submit">Cùng nhìn lại</button></div></form><div id="gr-st-out" aria-live="polite"></div>`;
  const sf = $('#gr-st-form', sh);
  $('#gr-cadd', sh).onclick = () => $('#gr-crows', sh).insertAdjacentHTML('beforeend', row());
  sh.addEventListener('click', e => { const b = e.target.closest('[data-rm]'); if (b) b.parentElement.remove(); });
  sf.onsubmit = async e => {
    e.preventDefault();
    const out = $('#gr-st-out', sh), concerns = $$('.gr-crow', sh).map(r => ({ text: $('input', r).value.trim(), zone: $('select', r).value })).filter(c => c.text);
    out.innerHTML = '<p class="muted">Đang soạn…</p>';
    try {
      const r = await post('/api/growth/navigate', { birth: req, domain: sf.domain.value, situation: sf.situation.value, concerns, duration: sf.duration.value, tried: sf.tried.value });
      if (r.safety) { out.innerHTML = notice('An toàn của bạn quan trọng nhất', esc(r.safety.text), 'warn'); return; }
      out.innerHTML = `<div class="gr-review">
        <p><b>${esc(r.summary)}</b></p>
        <div class="gr-zones">${['control', 'influence', 'outside', 'unsure'].map(z => `<section><h5>${ZONES[z]}</h5>${r.zones[z].length ? `<ul>${r.zones[z].map(i => `<li>${esc(i.text_user)}${i.hint ? `<br><span class="muted small">Gợi ý: có thể là “${esc(i.hint.label)}”. ${esc(i.hint.note)}</span>` : ''}</li>`).join('')}</ul>` : '<p class="muted small">—</p>'}</section>`).join('')}</div>
        <div class="notice"><div><b>Kiểm tra thiên hướng (theo hình tượng cung Mệnh)</b><p>${esc(r.bias_check.text)}</p></div></div>
        ${r.steps.map((s, i) => `<h5 class="gr-h5">Bước ${i + 1}. ${esc(s.title)}</h5><ul>${s.questions.map(q => `<li>${esc(q)}</li>`).join('')}</ul><p class="muted small">${esc(s.concept.name)} — ${esc(s.concept.ref)}</p>`).join('')}
        <h5 class="gr-h5">Câu hỏi riêng cho ${esc(r.domain_label.toLowerCase())}</h5><ul>${r.domain_questions.map(q => `<li>${esc(q)}</li>`).join('')}</ul>
        ${r.chart_questions.length ? `<h5 class="gr-h5">Câu hỏi từ lá số của bạn</h5><ul>${r.chart_questions.map(q => `<li>${esc(q.question)} <span class="muted small">(${esc(q.from)})</span></li>`).join('')}</ul>` : ''}
        ${r.pattern_hits.map(h => `<p class="gr-hit">${esc(h.text)}</p>`).join('')}
        ${r.actions.length ? `<h5 class="gr-h5">Một hành động nhỏ để thử</h5><ul>${r.actions.map(a => `<li><span class="badge">${a.days} ngày</span> ${esc(a.action)} <button type="button" class="link" data-start="${esc(a.id)}">Bắt đầu</button></li>`).join('')}</ul>` : ''}
        ${r.stage.lines.length ? `<p class="muted small">Lăng kính giai đoạn: ${esc(r.stage.lines[0])} ${esc(r.stage.how_to_use)}</p>` : ''}
        ${r.notes.map(n => notice('Lưu ý', esc(n), 'warn')).join('')}
        <p class="muted small">${esc(r.reminder)}</p></div>`;
    } catch (x) { out.innerHTML = notice('Chưa soạn được', esc(x.message), 'warn'); }
  };

  // ----- compass -----
  const ch = $('#gr-cmp-host', host), C = p.compass;
  ch.innerHTML = `<div class="seg gr-seg" role="tablist" aria-label="Lĩnh vực">${Object.entries(C).map(([k, v], i) => `<button type="button" role="tab" data-cd="${k}" aria-pressed="${i === 0}">${esc(v.label)}</button>`).join('')}</div><div id="gr-cd"></div>
    <form class="gr-form" id="gr-dc-form"><h4>Đặt một quyết định lên la bàn</h4>
      <div class="gr-row"><label class="fld"><span>Lĩnh vực</span><div class="sel"><select name="domain">${Object.entries(C).map(([k, v]) => `<option value="${k}">${esc(v.label)}</option>`).join('')}</select></div></label>
      <label class="fld"><span>Quyết định</span><input type="text" name="decision" maxlength="600" placeholder="Ví dụ: ở lại công ty hay chuyển việc"></label></div>
      <div class="gr-row">${[1, 2, 3].map(i => `<label class="fld"><span>Lựa chọn ${i}</span><input type="text" name="opt${i}" maxlength="80"></label>`).join('')}</div>
      <fieldset class="fld"><legend>Giá trị quan trọng với bạn (tối đa 5)</legend><div class="gr-vals">${p.values.map(v => `<label class="chip-c"><input type="checkbox" name="val" value="${v.id}"><span>${esc(v.label)}</span></label>`).join('')}</div></fieldset>
      <div id="gr-rate"></div>
      <div class="gr-act"><button class="btn btn-sm" type="submit">Soi lựa chọn</button></div></form><div id="gr-dc-out" aria-live="polite"></div>`;
  const paintCd = k => {
    const d = C[k];
    $('#gr-cd', ch).innerHTML = `<div class="gr-review"><h5 class="gr-h5">Xu hướng cần tự kiểm tra khi quyết định về ${esc(d.label.toLowerCase())}</h5><ul>${d.tendencies.map(t => `<li><b>${esc(t.from)}:</b> ${esc(t.text)}</li>`).join('')}</ul>
      <details class="gr-basis"><summary>Căn cứ trên lá số</summary><ul>${anchorsHtml(d.anchors, A)}</ul></details>
      <h5 class="gr-h5">Câu hỏi giá trị</h5><ul>${d.questions.map(q => `<li>${esc(q)}</li>`).join('')}</ul><p class="muted small">${esc(d.reminder)}</p></div>`;
    $$('[data-cd]', ch).forEach(b => b.setAttribute('aria-pressed', b.dataset.cd === k));
  };
  $$('[data-cd]', ch).forEach(b => b.onclick = () => paintCd(b.dataset.cd)); paintCd(Object.keys(C)[0]);
  const df = $('#gr-dc-form', ch);
  const chosen = () => $$('input[name=val]:checked', df).map(i => i.value), optsOf = () => [1, 2, 3].map(i => df['opt' + i].value.trim()).filter(Boolean);
  const paintRate = () => {
    const vs = chosen(), os = optsOf(), lab = Object.fromEntries(p.values.map(v => [v.id, v.label]));
    $('#gr-rate', df).innerHTML = vs.length && os.length ? `<div class="tbl-wrap"><table class="tbl"><caption class="muted small">Tự chấm 1–5: lựa chọn này phục vụ giá trị đó đến đâu?</caption><thead><tr><th>Lựa chọn</th>${vs.map(v => `<th>${esc(lab[v])}</th>`).join('')}</tr></thead><tbody>${os.map((o, i) => `<tr><th>${esc(o)}</th>${vs.map(v => `<td><select data-o="${i}" data-v="${v}" aria-label="${esc(o)} – ${esc(lab[v])}"><option value="">–</option>${[1, 2, 3, 4, 5].map(n => `<option>${n}</option>`).join('')}</select></td>`).join('')}</tr>`).join('')}</tbody></table></div>` : '';
  };
  df.addEventListener('change', e => {
    if (e.target.name === 'val' && chosen().length > 5) e.target.checked = false;
    if (e.target.name === 'val' || /^opt/.test(e.target.name)) paintRate();
  });
  df.addEventListener('input', e => { if (/^opt/.test(e.target.name)) paintRate(); });
  df.onsubmit = async e => {
    e.preventDefault();
    const os = optsOf(), ratings = {}, out = $('#gr-dc-out', ch);
    $$('#gr-rate select', df).forEach(s => { if (s.value) (ratings[os[+s.dataset.o]] ||= {})[s.dataset.v] = +s.value; });
    out.innerHTML = '<p class="muted">Đang đặt lên la bàn…</p>';
    try {
      const r = await post('/api/growth/compass', { birth: req, domain: df.domain.value, decision: df.decision.value, options: os, values: chosen(), ratings });
      if (r.safety) { out.innerHTML = notice('An toàn của bạn quan trọng nhất', esc(r.safety.text), 'warn'); return; }
      out.innerHTML = `<div class="gr-review"><p><b>${esc(r.ownership)}</b></p>
        ${r.values_reflection.length ? `<h5 class="gr-h5">Giá trị của bạn và hình tượng lá số</h5><ul>${r.values_reflection.map(t => `<li>${esc(t)}</li>`).join('')}</ul>` : ''}
        ${r.matrix.some(m => m.rated) ? `<h5 class="gr-h5">Điểm bạn tự chấm</h5><ul>${r.matrix.map(m => `<li>${esc(m.option)}: ${m.total} điểm (${m.rated} giá trị đã chấm)</li>`).join('')}</ul><p class="muted small">${esc(r.matrix_note)}</p>` : ''}
        ${r.notes.map(n => `<p>${esc(n)}</p>`).join('')}
        <h5 class="gr-h5">Xu hướng cần kiểm tra</h5><ul>${r.tendencies_to_check.map(t => `<li><b>${esc(t.from)}:</b> ${esc(t.text)}</li>`).join('')}</ul>
        <h5 class="gr-h5">Công cụ ra quyết định</h5><ul>${r.tools.map(t => `<li><b>${esc(t.concept.name)}:</b> ${esc(t.prompt)} <span class="muted small">(${esc(t.concept.ref)})</span></li>`).join('')}</ul></div>`;
    } catch (x) { out.innerHTML = notice('Chưa xử lý được', esc(x.message), 'warn'); }
  };

  // ----- dialogue -----
  const dh = $('#gr-chat-host', host); let used = [];
  const ASK = ['Tại sao tôi luôn mắc kẹt ở đây?', 'Tôi nên thay đổi điều gì?', 'Điểm mạnh nào tôi chưa tận dụng?'];
  dh.innerHTML = `<details class="gr-ctx" open><summary>Hoàn cảnh của bạn (tùy chọn, giúp câu trả lời sát hơn)</summary>
      <div class="gr-row"><label class="fld"><span>Lĩnh vực</span><div class="sel"><select id="gr-cx-d"><option value="">Tự nhận biết</option>${opts(DOM)}</select></div></label></div>
      <label class="fld"><span>Điều bạn đang trải qua</span><textarea id="gr-cx-s" rows="2" maxlength="1500" placeholder="Ví dụ: ba năm không thăng tiến dù làm việc rất nhiều"></textarea></label>
      <p class="muted small">Giá trị bạn chọn ở La bàn cũng được dùng ở đây. Không có gì được lưu trên máy chủ.</p></details>
    <div class="gr-log" id="gr-log" aria-live="polite"></div>
    <div class="gr-sugg">${ASK.map(q => `<button type="button" class="chip-b" data-ask="${esc(q)}">${esc(q)}</button>`).join('')}</div>
    <form class="gr-ask" id="gr-ask"><label class="sr-only" for="gr-q">Câu hỏi của bạn</label><input id="gr-q" type="text" maxlength="600" placeholder="Hỏi lá số của bạn…" autocomplete="off"><button class="btn btn-sm" type="submit">Hỏi</button></form>`;
  const log = $('#gr-log', dh);
  async function ask(q) {
    if (!q.trim()) return;
    log.insertAdjacentHTML('beforeend', `<div class="gr-msg me"><p>${esc(q)}</p></div>`);
    const ctx = { situation: $('#gr-cx-s', dh).value, domain: $('#gr-cx-d', dh).value || null, values: chosen() };
    try {
      const r = await post('/api/growth/dialogue', { birth: req, question: q, context: ctx, exclude: used });
      used = [...new Set([...used, ...r.grounding])].slice(-60);
      log.insertAdjacentHTML('beforeend', `<div class="gr-msg bot">${r.reply.map(x => `<p class="gr-p gr-p-${x.layer}"><span class="gr-tag">${esc(x.label)}</span>${esc(x.text)}${x.practice ? ` <button type="button" class="link" data-start="${esc(x.practice)}">Bắt đầu</button>` : ''}</p>`).join('')}
        ${r.follow_up.length ? `<div class="gr-sugg">${r.follow_up.map(f => `<button type="button" class="chip-b" data-ask="${esc(f)}">${esc(f)}</button>`).join('')}</div>` : ''}${r.note ? `<p class="muted small">${esc(r.note)}</p>` : ''}</div>`);
    } catch (x) { log.insertAdjacentHTML('beforeend', `<div class="gr-msg bot">${notice('Chưa trả lời được', esc(x.message), 'warn')}</div>`); }
    log.lastElementChild?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
  dh.addEventListener('click', e => { const b = e.target.closest('[data-ask]'); if (b) ask(b.dataset.ask); });
  $('#gr-ask', dh).onsubmit = e => { e.preventDefault(); const i = $('#gr-q', dh); ask(i.value); i.value = ''; };

  paintPractices(); paintJournal();
  return p;
}
