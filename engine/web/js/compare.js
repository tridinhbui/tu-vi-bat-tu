// The single entry to comparing two saved charts: one button, two pickers, one result view (compare_ui.js, v2 response).
// Facts only: no compatibility score, no "hợp / khắc" verdict between people. State (the two choices, the rendered result, scroll position)
// survives closing and reopening the dialog; the result is only recomputed when the pair, the charts or the experimental mode change.
import { $, esc, post } from './util.js';
import { readSaved } from './mine.js';
import { renderCompareResult, initDetailDialog, expOn } from './compare_ui.js';

const SEL_KEY = 'tvbt-cmp-sel';
const NEED = ['year', 'month', 'day', 'hour', 'minute', 'gender'];
const label = x => `${x.label} · ${x.req?.day}/${x.req?.month}/${x.req?.year}`;
const lacks = x => NEED.filter(k => x.req?.[k] === undefined || x.req[k] === null || x.req[k] === '');
const readSel = () => { try { return JSON.parse(sessionStorage.getItem(SEL_KEY)) || {}; } catch { return {}; } };
const writeSel = s => { try { sessionStorage.setItem(SEL_KEY, JSON.stringify(s)); } catch { /* the choice is simply not remembered */ } };

/** What the pre-v2 response carries (kept so an older server still shows something useful). */
function legacy(r, A, B) {
  const nm = t => esc(String(t || '').replace('người A', A.label).replace('người B', B.label));
  return `<p class="muted">Máy chủ này chưa có bản so sánh nhiều tầng; đây là phần dữ kiện cơ bản.</p><ul class="cpx-list"><li>${nm(r.element_link?.text)}</li><li>${nm(r.day_master_stems?.text)}</li>${(r.day_branches || []).map(x => `<li>${nm(x.text)}</li>`).join('')}</ul><p class="muted small">${esc(r.note || '')} (A: ${esc(A.label)}, B: ${esc(B.label)}.)</p>`;
}

export function initCompare(host) {
  host.innerHTML = '<button type="button" class="btn btn-ghost btn-sm" id="cmp-open">So sánh hai lá số</button>';
  const dlg = document.createElement('dialog');
  dlg.id = 'cmp-main'; dlg.className = 'dlg cpx-main'; dlg.setAttribute('aria-labelledby', 'cmp-t');
  dlg.innerHTML = `<div class="cpx-head"><div class="cpx-ht"><div><p class="eyebrow">So sánh</p><h3 id="cmp-t">Hai lá số cạnh nhau</h3></div><button type="button" class="cpx-x" data-close aria-label="Đóng">×</button></div>
    <div class="cpx-pick"><label>Lá số A<select id="cmp-a"></select></label><button type="button" class="btn btn-ghost btn-sm cpx-swap" id="cmp-swap" aria-label="Đổi chỗ hai lá số">⇄</button><label>Lá số B<select id="cmp-b"></select></label></div></div>
    <div class="cpx-body" id="cmp-body" aria-live="polite"></div>`;
  document.body.append(dlg);
  initDetailDialog();
  dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });
  $('[data-close]', dlg).onclick = () => dlg.close();
  const body = $('#cmp-body', dlg), selA = $('#cmp-a', dlg), selB = $('#cmp-b', dlg);
  let list = [], shown = null, seq = 0;

  const paintHost = () => { host.hidden = readSaved().length < 2; };
  paintHost();
  addEventListener('storage', paintHost);
  new MutationObserver(paintHost).observe($('#saved-list'), { childList: true });

  function fill() {
    list = readSaved();
    const ids = list.map(x => x.id), sel = readSel();
    const a = ids.includes(sel.a) ? sel.a : ids[0];
    const b = ids.includes(sel.b) && sel.b !== a ? sel.b : ids.find(i => i !== a);
    const opts = cur => list.map(x => `<option value="${esc(x.id)}"${x.id === cur ? ' selected' : ''}>${esc(label(x))}</option>`).join('');
    const html = [opts(a), opts(b)];
    if (selA.innerHTML !== html[0]) selA.innerHTML = html[0];
    if (selB.innerHTML !== html[1]) selB.innerHTML = html[1];
    selA.value = a; selB.value = b; writeSel({ a, b });
  }

  async function run() {
    const A = list.find(x => x.id === selA.value), B = list.find(x => x.id === selB.value), exp = expOn();
    if (!A || !B || A === B) { shown = null; body.innerHTML = '<p class="muted">Hãy chọn hai lá số khác nhau.</p>'; return; }
    const bad = [A, B].map(x => [x, lacks(x)]).find(([, l]) => l.length);
    if (bad) { shown = null; body.innerHTML = `<p class="muted">Lá số “${esc(bad[0].label)}” đã lưu thiếu dữ kiện (${esc(bad[1].join(', '))}). Hãy xóa lá số này ở trang chủ rồi lập và lưu lại.</p>`; return; }
    const key = JSON.stringify([A.id, B.id, A.req, B.req, exp]);
    if (key === shown) return;
    const my = ++seq;
    body.innerHTML = '<p class="muted">Đang so sánh…</p>';
    try {
      const res = await post('/api/compare-charts', { a: { ...A.req, experimental: exp }, b: { ...B.req, experimental: exp } });
      if (my !== seq) return;
      if (!res.v2) { body.innerHTML = legacy(res, A, B); shown = key; return; }
      renderCompareResult(body, { A, B, res });
      shown = key; body.scrollTop = 0;
    } catch (e) {
      if (my !== seq) return;
      shown = null;
      body.innerHTML = `<p class="muted">Chưa so sánh được: ${esc(e.message)}</p><button type="button" class="btn btn-ghost btn-sm" id="cmp-retry">Thử lại</button>`;
      $('#cmp-retry', body).onclick = run;
    }
  }

  const changed = () => { if (selA.value === selB.value) { const other = list.find(x => x.id !== selA.value); if (other) (document.activeElement === selA ? selB : selA).value = other.id; } writeSel({ a: selA.value, b: selB.value }); run(); };
  selA.onchange = changed; selB.onchange = changed;
  $('#cmp-swap', dlg).onclick = () => { const a = selA.value; selA.value = selB.value; selB.value = a; writeSel({ a: selA.value, b: selB.value }); run(); };
  $('#cmp-open', host).onclick = () => { fill(); if (!dlg.open) dlg.showModal(); run(); };
  return { refresh: paintHost };
}
