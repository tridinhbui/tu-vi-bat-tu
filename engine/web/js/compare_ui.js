// Two-chart comparison view: structure of each chart first, then the contacts between them, grouped by tier.
// Every fact is a button that opens its rule, data and source. Facts only: no score, no verdict.
import { $, $$, esc, post } from './util.js';
import { terms, autoLink } from './glossary.js';

const PIL = { year: 'Năm', month: 'Tháng', day: 'Ngày', hour: 'Giờ' };
const STATUS = { verified: ['Đã đối chiếu sách', 'ok'], partial: ['Đối chiếu một phần', 'part'], draft: ['Bản nháp, chỉ thử nghiệm', 'draft'] };
const GROUP3 = new Set(['branch_triad', 'branch_meeting', 'branch_penalty', 'branch_semi_triad', 'branch_ban_hinh']);
const KIND_GROUP = [['Thiên can', k => k.startsWith('stem_')], ['Địa chi', k => k.startsWith('branch_') && !GROUP3.has(k)], ['Nhóm ba chi và hình', k => GROUP3.has(k)]];
const expOn = () => { try { return sessionStorage.getItem('tvbt_exp') === '1'; } catch { return false; } };
const badge = s => `<span class="cpx-b cpx-b-${(STATUS[s] || STATUS.draft)[1]}">${(STATUS[s] || STATUS.draft)[0]}</span>`;

let current = null; // last response, for the dialog

const fact = (id, html, extra = '') => `<button type="button" class="cpx-f ${extra}" data-cpx="${esc(id)}">${html}</button>`;

function who(o, names) { return esc(names[o]); }

function dataHtml(it, names) {
  const d = it.data || {};
  if (d.members) return `<ul>${d.members.map(m => `<li><b>${esc(m.name)}</b>: ${m.type === 'stem' ? 'Thiên can' : 'Địa chi'} của trụ ${esc(PIL[m.slot])} thuộc ${who(m.owner, names)}</li>`).join('')}</ul>
    ${d.table_element ? `<p>Hành theo bảng hợp: ${esc(d.table_element)} (chưa xét hóa).</p>` : ''}
    ${d.anchors?.length ? `<p>Chạm vào vị trí quan trọng: ${esc(d.anchors.join(', '))}.</p>` : ''}${d.same_slot ? '<p>Hai chữ cùng vị trí trụ trong hai lá số.</p>' : ''}${it.school_dependent ? '<p class="muted">Cách tính loại này còn tùy trường phái; hệ thống nêu ra, không kết luận mạnh nhẹ.</p>' : ''}`;
  if (d.rows) {
    const rows = d.rows;
    return `<p>Thập Thần của từng chữ, tính từ Nhật Chủ ${esc(names[d.viewer || ''] || '')}.</p><table class="cpx-t"><thead><tr><th>Trụ</th><th>Chữ</th><th>Thập Thần</th></tr></thead><tbody>${rows.map(r => `<tr><td>${esc(PIL[r.slot])}</td><td>${esc(r.char)}${r.kind === 'hidden' ? ' <small>(tàng can)</small>' : r.is_day_master ? ' <small>(Nhật Chủ)</small>' : ''}</td><td>${esc(r.ten_god)}</td></tr>`).join('')}</tbody></table>`;
  }
  if (d.palaces) return `<ul>${Object.entries(d.palaces).map(([n, p]) => `<li><b>${esc(n)}</b> ở ${esc(p.branch)}: ${p.major_stars.length ? esc(p.major_stars.map(s => s + (p.dignity?.[s] ? ` (${p.dignity[s]})` : '')).join(', ')) : 'vô chính diệu'}${p.tuan ? ' · Tuần' : ''}${p.triet ? ' · Triệt' : ''}</li>`).join('')}</ul>`;
  if (d.geometry) {
    const four = q => q.tam_phuong.map(x => `${x.role}: ${x.palace} (${x.branch}${x.major_stars.length ? ', ' + x.major_stars.join(' ') : ''})`).join('; ');
    return `<p><b>A:</b> cung ${esc(d.a.palace)} ở ${esc(d.a.branch)}. Tam phương tứ chính: ${esc(four(d.a))}.</p><p><b>B:</b> cung ${esc(d.b.palace)} ở ${esc(d.b.branch)}. Tam phương tứ chính: ${esc(four(d.b))}.</p>
      <p>Chi trùng nhau trong hai tam phương tứ chính: ${d.shared_tam_phuong_branches.length ? esc(d.shared_tam_phuong_branches.join(', ')) : 'không có'}. Chính tinh chung: ${d.shared_tam_phuong_major_stars.length ? esc(d.shared_tam_phuong_major_stars.join(', ')) : 'không có'}.</p>`;
  }
  const keys = Object.entries(d).filter(([, v]) => v !== null && typeof v !== 'object');
  return keys.length ? `<ul>${keys.map(([k, v]) => `<li>${esc(k)}: ${esc(v)}</li>`).join('')}</ul>` : '<p class="muted">Mục này không có dữ kiện bổ sung.</p>';
}

function openItem(id) {
  const r = current; const it = r.items.find(x => x.id === id); if (!it) return;
  const rule = r.rules[it.rule], dlg = $('#cpx-dlg');
  $('#cpx-dlg-b').innerHTML = `<p class="eyebrow">${esc(it.kind_vi || 'Mục so sánh')} ${badge(it.status)}</p><h3>${esc(it.title)}</h3>
    <p>${esc(it.plain)}</p>
    <h4>Dữ kiện</h4>${dataHtml(it, r.names)}
    <h4>Quy tắc</h4><p><b>${esc(rule.title)}.</b> ${esc(rule.text)}</p>
    <h4>Nguồn</h4>${rule.source ? `<p>${esc(rule.source.title)}${rule.source.locator ? `, ${esc(rule.source.locator)}` : ''} ${rule.source.verified ? '(đã đối chiếu bản gốc)' : '(chưa đối chiếu)'}.</p>` : '<p>Chưa có nguồn trong kho. Mục này chỉ là bản nháp của hệ thống.</p>'}
    ${it.experimental ? '<p class="cpx-warn">Chế độ thử nghiệm: nội dung chưa xác minh, không thuộc kết quả chính thức.</p>' : ''}`;
  autoLink($('#cpx-dlg-b'), 'bt');
  dlg.showModal();
}

function tierBlock(r, tier, title, names) {
  const t = r.tiers[tier], items = t.ids.map(id => r.items.find(i => i.id === id));
  let body;
  if (tier === 'direct') {
    const bz = items.filter(i => i.layer === 'bazi'), parts = [];
    const tenGods = bz.filter(i => i.kind === 'ten_god_view');
    KIND_GROUP.forEach(([label, test]) => { const g = bz.filter(i => test(i.kind) && i.kind !== 'ten_god_view'); if (g.length) parts.push(`<h5>${label} <small>(${g.length})</small></h5><div class="cpx-fl">${g.map(i => fact(i.id, esc(i.plain), i.experimental ? 'x' : '')).join('')}</div>`); });
    if (tenGods.length) parts.push(`<h5>Thập Thần hai chiều</h5><div class="cpx-fl">${tenGods.map(i => fact(i.id, esc(i.plain), '')).join('')}</div>`);
    const other = bz.filter(i => !i.kind.match(/stem_|branch_|ten_god_view/));
    if (other.length) parts.push(`<h5>Bối cảnh (thử nghiệm)</h5><div class="cpx-fl">${other.map(i => fact(i.id, esc(i.plain), 'x')).join('')}</div>`);
    if (!parts.length) parts.push('<p class="muted">Không có quan hệ trực tiếp nào theo bảng giữa các chữ của hai lá số.</p>');
    body = parts.join('');
  } else if (tier === 'insufficient') body = `<div class="cpx-fl">${items.map(i => fact(i.id, `<b>${esc(i.title)}.</b> ${esc(i.plain)}`, 'ins')).join('')}</div>`;
  else body = items.length ? `<div class="cpx-fl">${items.map(i => fact(i.id, esc(i.plain), i.experimental ? 'x' : '')).join('')}</div>` : '';
  return `<section class="cpx-tier cpx-${tier}"><h4>${title}</h4><p class="muted small">${esc(t.note)}</p>${body}</section>`;
}

function structureCol(o, s, names) {
  const m = s.month, st = s.strength;
  const strengthTxt = st.borderline ? `Phe của Nhật Chủ chiếm ${(st.own_share * 100).toFixed(1)}%, sát ngưỡng ${(st.threshold * 100).toFixed(0)}%, không kết luận vượng hay nhược.`
    : `Phe của Nhật Chủ chiếm ${(st.own_share * 100).toFixed(1)}% (ngưỡng ${(st.threshold * 100).toFixed(0)}%), nên đứng ở phía ${st.side}.`;
  return `<div class="cpx-c"><span class="k">${esc(names[o])}</span><b>${esc(s.day_master)} ${esc(s.dm_element)}</b><p class="cpx-pl">${esc(s.pillars)}</p>
    <ul class="cpx-sl"><li><button type="button" class="cpx-f" data-rule="CMP_MONTH_ORDER"><b>Nguyệt lệnh ${esc(m.branch)}</b>: hành ${esc(m.ruling_element)} nắm lệnh, thuộc nhóm ${esc(m.ruling_group)} so với Nhật Chủ${m.ruling_in_own_camp ? ' (phe mình)' : ''}.</button></li>
    <li><button type="button" class="cpx-f" data-rule="CMP_STRENGTH_40">${esc(strengthTxt)}</button></li>
    <li>${s.has_root ? `Nhật Chủ có chữ cùng hành trong tàng can (${esc(s.roots.map(r => r.hidden + ' ở ' + r.branch).join(', '))}).` : 'Nhật Chủ không có chữ cùng hành nào trong tàng can.'}</li></ul></div>`;
}

function tvCol(o, s, names) {
  return `<div class="cpx-c"><span class="k">${esc(names[o])} · ${esc(s.year)}</span><b>${esc(s.cuc)}</b><p class="cpx-pl">Bản mệnh ${esc(s.menh_nap_am)}</p>
    <ul class="cpx-sl">${['Mệnh', 'Thân', 'Phu Thê', 'Phúc Đức'].map(n => `<li><b>${n}</b> ở ${esc(s[n].branch)}: ${s[n].major_stars.length ? esc(s[n].major_stars.join(', ')) : 'vô chính diệu'}</li>`).join('')}</ul></div>`;
}

export async function renderCompare(host, A, B) {
  host.innerHTML = '<p class="muted">Đang so sánh…</p>';
  const exp = expOn();
  let r;
  try { r = (await post('/api/compare-charts', { a: { ...A.req, experimental: exp }, b: { ...B.req, experimental: exp } })).v2; }
  catch (e) { host.innerHTML = `<p class="muted">Chưa so sánh được: ${esc(e.message)}</p>`; return; }
  const names = { a: A.label, b: B.label }; r.names = names; current = r;
  const sub = r.items.filter(i => i.layer === 'tuvi' && i.kind !== 'placement' && i.tier === 'direct');
  host.innerHTML = `<div class="cpx"><p class="eyebrow">So sánh nhiều tầng${exp ? ' · chế độ thử nghiệm' : ''}</p><h3>${esc(A.label)} (A) và ${esc(B.label)} (B)</h3>
    <p class="muted">${esc(r.principle)} Bấm vào từng dòng để xem quy tắc, dữ kiện và nguồn.</p>
    <section class="cpx-tier"><h4>1. Mỗi lá số một mình, trước khi so</h4><p class="muted small">Sách xét nguyệt lệnh và thế mạnh yếu của Nhật Chủ trước, rồi mới xét các quan hệ.</p>
      <div class="cpx-cols">${structureCol('a', r.structure.a, names)}${structureCol('b', r.structure.b, names)}</div></section>
    <section class="cpx-tier"><h4>2. Bốn trụ cạnh nhau</h4><table class="cpx-t cpx-pt"><thead><tr><th>Trụ</th><th>${esc(A.label)}</th><th>${esc(B.label)}</th></tr></thead><tbody>
      ${r.pillars.map(p => `<tr><td>${esc(PIL[p.slot])}</td><td>${esc(p.a)}${p.a_ten_god ? ` <small>${esc(p.a_ten_god)}</small>` : ' <small>Nhật Chủ</small>'}</td><td>${esc(p.b)}${p.b_ten_god ? ` <small>${esc(p.b_ten_god)}</small>` : ' <small>Nhật Chủ</small>'}</td></tr>`).join('')}</tbody></table>
      <p class="muted small">Thập Thần nhỏ bên cạnh là của chữ đó so với Nhật Chủ của chính lá số ấy.</p></section>
    ${tierBlock(r, 'direct', '3. Tương tác trực tiếp giữa hai lá số', names)}
    ${tierBlock(r, 'support', '4. Yếu tố hỗ trợ', names)}
    ${tierBlock(r, 'limit', '5. Yếu tố hạn chế', names)}
    <section class="cpx-tier"><h4>6. Tử Vi <small>(tính độc lập với Bát Tự)</small></h4><p class="muted small">Chỉ nêu vị trí cung và sao chung; ý nghĩa khi cung của hai người gặp nhau không được diễn giải.</p>
      <div class="cpx-cols">${tvCol('a', r.tuvi_structure.a, names)}${tvCol('b', r.tuvi_structure.b, names)}</div>
      <div class="cpx-fl">${sub.map(i => fact(i.id, esc(i.plain), i.experimental ? 'x' : '')).join('')}</div></section>
    ${tierBlock(r, 'insufficient', '7. Chưa đủ căn cứ để kết luận', names)}
    ${!exp && r.hidden_experimental ? `<p class="muted small">Có ${r.hidden_experimental} mục bản nháp chưa xác minh đang được ẩn.</p>` : ''}
    </div>`;
  $$('[data-cpx]', host).forEach(b => b.onclick = () => openItem(b.dataset.cpx));
  $$('[data-rule]', host).forEach(b => b.onclick = () => openRule(b.dataset.rule));
  autoLink(host, 'bt');
}

function openRule(id) {
  const rule = current.rules[id]; if (!rule) return;
  $('#cpx-dlg-b').innerHTML = `<p class="eyebrow">Quy tắc ${badge(rule.status)}</p><h3>${esc(rule.title)}</h3><p>${esc(rule.text)}</p><h4>Nguồn</h4>${rule.source ? `<p>${esc(rule.source.title)}${rule.source.locator ? `, ${esc(rule.source.locator)}` : ''}.</p>` : '<p>Chưa có nguồn trong kho.</p>'}`;
  $('#cpx-dlg').showModal();
}

export function initCompareDialog() {
  const d = $('#cpx-dlg'); d.addEventListener('click', e => { if (e.target === d) d.close(); });
}
