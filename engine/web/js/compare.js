// Side-by-side view of two saved charts. Facts only: no compatibility score, no "hợp / khắc" verdict between people.
import { $, esc, post, STEMS, EL, ELEMENTS } from './util.js';
import { readSaved } from './mine.js';
import { elementStats, currentPhase } from './insights.js';

const dg = (p, s) => p.major_dignity?.[s] ? ` (${p.major_dignity[s]})` : '';
const label = x => `${x.label} · ${x.req.day}/${x.req.month}/${x.req.year}`;

function column(req, chart) {
  const b = chart.bazi, t = chart.tuvi, dm = STEMS[b.pillars.day.stem], menh = t.palaces.find(p => p.name === 'Mệnh'), than = t.palaces.find(p => p.is_than);
  const { vis } = elementStats(b), ph = currentPhase(b, t, req);
  return {
    dm, rows: [
      ['Nhật Chủ (Bát Tự)', `${dm.n} ${dm.e}`],
      ['Bốn trụ', ['year', 'month', 'day', 'hour'].map(k => b.pillars[k].name).join(' · ')],
      ['Ngũ hành trên tám chữ', ELEMENTS.map(e => `${e} ${vis[e]}`).join(' · ')],
      ['Đại vận hiện tại', ph.luck ? `${ph.luck.name} (${ph.luck.ten_god})` : 'chưa khởi vận'],
      ['Cục (Tử Vi)', t.cuc.name],
      ['Bản mệnh', t.menh_nap_am],
      ['Cung Mệnh', `${menh.stem} ${menh.branch}: ${menh.major_stars.length ? menh.major_stars.map(s => s + dg(menh, s)).join(', ') : 'vô chính diệu'}`],
      ['Cung Thân', than.name],
      ['Đại hạn hiện tại', ph.dh ? `cung ${ph.dh.palace} (${ph.dh.age_from}–${ph.dh.age_to} tuổi)` : 'chưa vào đại hạn'],
    ],
  };
}

/** Relation between two elements, taken from the sinh/khắc table. */
function elementRelation(a, b) {
  if (a === b) return `Hai Nhật Chủ cùng hành ${a}.`;
  const r = EL[a];
  if (r.sinh === b) return `Hành ${a} (Nhật Chủ bên trái) sinh hành ${b} (Nhật Chủ bên phải).`;
  if (r.duocSinh === b) return `Hành ${b} (Nhật Chủ bên phải) sinh hành ${a} (Nhật Chủ bên trái).`;
  if (r.khac === b) return `Hành ${a} (Nhật Chủ bên trái) khắc hành ${b} (Nhật Chủ bên phải).`;
  return `Hành ${b} (Nhật Chủ bên phải) khắc hành ${a} (Nhật Chủ bên trái).`;
}

export function initCompare(host) {
  host.innerHTML = '<button type="button" class="btn btn-ghost btn-sm" id="cmp-open">So sánh hai lá số đã lưu</button>';
  const dlg = document.createElement('dialog'); dlg.className = 'dlg cmp-dlg'; dlg.setAttribute('aria-labelledby', 'cmp-t');
  document.body.append(dlg);
  dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });
  const paintHost = () => { host.hidden = readSaved().length < 2; };
  paintHost();
  addEventListener('storage', paintHost);
  new MutationObserver(paintHost).observe($('#saved-list'), { childList: true });

  async function show() {
    const list = readSaved(), opts = (sel) => list.map((x, i) => `<option value="${i}"${i === sel ? ' selected' : ''}>${esc(label(x))}</option>`).join('');
    dlg.innerHTML = `<div class="cmp-in"><p class="eyebrow">So sánh</p><h3 id="cmp-t">Hai lá số cạnh nhau</h3>
      <div class="cmp-pick"><label>Bên trái<select id="cmp-a">${opts(0)}</select></label><label>Bên phải<select id="cmp-b">${opts(1)}</select></label></div>
      <div id="cmp-out" aria-live="polite"></div>
      <p class="muted small">Chỉ là so sánh các dữ kiện đã tính. Thiên Bàn không chấm điểm hợp hay khắc giữa hai người, vì không có quy tắc nào đã đối chiếu sách cho việc đó.</p>
      <button type="button" class="btn btn-ghost btn-sm" data-close>Đóng</button></div>`;
    $('[data-close]', dlg).onclick = () => dlg.close();
    const run = async () => {
      const out = $('#cmp-out', dlg), A = list[+$('#cmp-a', dlg).value], B = list[+$('#cmp-b', dlg).value];
      if (A === B) { out.innerHTML = '<p class="muted">Hãy chọn hai lá số khác nhau.</p>'; return; }
      out.innerHTML = '<p class="muted">Đang tính…</p>';
      try {
        const [ca, cb] = await Promise.all([post('/api/chart', A.req), post('/api/chart', B.req)]);
        const a = column(A.req, ca), b = column(B.req, cb);
        out.innerHTML = `<div class="tbl-wrap"><table class="tbl cmp-t"><thead><tr><th></th><th scope="col">${esc(A.label)}</th><th scope="col">${esc(B.label)}</th></tr></thead><tbody>${a.rows.map((r, i) => `<tr><th scope="row">${esc(r[0])}</th><td>${esc(r[1])}</td><td>${esc(b.rows[i][1])}</td></tr>`).join('')}</tbody></table></div>
          <p class="cmp-rel"><b>Quan hệ giữa hai hành Nhật Chủ:</b> ${esc(elementRelation(a.dm.e, b.dm.e))} <span class="muted">Chỉ là quan hệ sinh khắc giữa hai hành, chưa phải đánh giá về hai người.</span></p>`;
      } catch (e) { out.innerHTML = `<p class="muted">Chưa so sánh được: ${esc(e.message)}</p>`; }
    };
    $('#cmp-a', dlg).onchange = run; $('#cmp-b', dlg).onchange = run;
    if (!dlg.open) dlg.showModal();
    run();
  }
  $('#cmp-open', host).onclick = show;
  return { refresh: paintHost };
}
