// Renderer of the unified two-chart comparison (v2 response). Order: overview of each person -> four pillars -> Can Chi contacts ->
// Tử Vi -> support / limits -> sources and limits. Every fact says WHAT KIND of statement it is (calculation, sourced rule, experimental
// hypothesis) and opens its rule, data and source. Facts only: no score, no verdict.
import { $, $$, esc } from './util.js';
import { autoLink } from './glossary.js';
import { currentPhase } from './insights.js';

const PIL = { year: 'Năm', month: 'Tháng', day: 'Ngày', hour: 'Giờ' };
const EV = { calc: ['Tính toán', 'calc'], sourced: ['Quy tắc có nguồn', 'src'], hypothesis: ['Giả thuyết thử nghiệm', 'hyp'] };
const STATUS = { verified: 'đã đối chiếu sách', partial: 'đối chiếu một phần', draft: 'chưa xác minh' };
const GROUP3 = new Set(['branch_triad', 'branch_meeting', 'branch_penalty', 'branch_semi_triad', 'branch_ban_hinh']);
const KIND_GROUP = [['Thiên can', k => k.startsWith('stem_')], ['Địa chi', k => k.startsWith('branch_') && !GROUP3.has(k)], ['Nhóm ba chi và hình', k => GROUP3.has(k)]];
export const expOn = () => { try { return sessionStorage.getItem('tvbt_exp') === '1'; } catch { return false; } };

let current = null; // the response being shown (the detail dialog reads from it)

const tag = (ev, status) => { const [t, c] = EV[ev] || EV.hypothesis; return `<span class="cpx-ev cpx-ev-${c}">${t}${ev === 'sourced' && status === 'partial' ? ' · một phần' : ''}</span>`; };
const fact = (id, html, it) => `<button type="button" class="cpx-f ${it?.experimental ? 'x' : ''}" data-cpx="${esc(id)}">${it ? tag(it.evidence, it.status) : ''}<span>${html}</span></button>`;
const itemsOf = (r, ids) => ids.map(id => r.items.find(i => i.id === id)).filter(Boolean);

// ---------------------------------------------------------------- detail dialog
function dataHtml(it, names) {
  const d = it.data || {};
  if (d.members) return `<ul>${d.members.map(m => `<li><b>${esc(m.name)}</b>: ${m.type === 'stem' ? 'Thiên can' : 'Địa chi'} của trụ ${esc(PIL[m.slot])} thuộc ${esc(names[m.owner])}</li>`).join('')}</ul>
    ${d.table_element ? `<p>Hành theo bảng hợp: ${esc(d.table_element)} (chưa xét hóa).</p>` : ''}
    ${d.anchors?.length ? `<p>Chạm vào vị trí quan trọng: ${esc(d.anchors.join(', '))}.</p>` : ''}${d.same_slot ? '<p>Hai chữ cùng vị trí trụ trong hai lá số.</p>' : ''}${it.school_dependent ? '<p class="muted">Cách tính loại này còn tùy trường phái; hệ thống nêu ra, không kết luận mạnh nhẹ.</p>' : ''}`;
  if (d.rows) return `<p>Thập Thần của từng chữ, tính từ Nhật Chủ ${esc(names[d.viewer] || '')}.</p><table class="cpx-t"><thead><tr><th>Trụ</th><th>Chữ</th><th>Thập Thần</th></tr></thead><tbody>${d.rows.map(r => `<tr><td>${esc(PIL[r.slot])}</td><td>${esc(r.char)}${r.kind === 'hidden' ? ' <small>(tàng can)</small>' : r.is_day_master ? ' <small>(Nhật Chủ)</small>' : ''}</td><td>${esc(r.ten_god)}</td></tr>`).join('')}</tbody></table>`;
  if (d.palaces) return `<ul>${Object.entries(d.palaces).map(([n, p]) => `<li><b>${esc(n)}</b> ở ${esc(p.branch)}: ${p.major_stars.length ? esc(p.major_stars.map(s => s + (p.dignity?.[s] ? ` (${p.dignity[s]})` : '')).join(', ')) : 'vô chính diệu'}${p.tuan ? ' · Tuần' : ''}${p.triet ? ' · Triệt' : ''}</li>`).join('')}</ul>`;
  if (d.geometry) {
    const four = q => q.tam_phuong.map(x => `${x.role}: ${x.palace} (${x.branch}${x.major_stars.length ? ', ' + x.major_stars.join(' ') : ''})`).join('; ');
    return `<p><b>${esc(names.a)}:</b> cung ${esc(d.a.palace)} ở ${esc(d.a.branch)}. Tam phương tứ chính: ${esc(four(d.a))}.</p><p><b>${esc(names.b)}:</b> cung ${esc(d.b.palace)} ở ${esc(d.b.branch)}. Tam phương tứ chính: ${esc(four(d.b))}.</p>
      <p>Chi trùng nhau trong hai tam phương tứ chính: ${d.shared_tam_phuong_branches.length ? esc(d.shared_tam_phuong_branches.join(', ')) : 'không có'}. Chính tinh chung: ${d.shared_tam_phuong_major_stars.length ? esc(d.shared_tam_phuong_major_stars.join(', ')) : 'không có'}.</p>`;
  }
  if (it.kind === 'element_count') return `<table class="cpx-t"><thead><tr><th>Hành</th><th>${esc(names.a)}</th><th>${esc(names.b)}</th></tr></thead><tbody>${Object.keys(d.a).map(e => `<tr><td>${esc(e)}</td><td>${d.a[e]}</td><td>${d.b[e]}</td></tr>`).join('')}</tbody></table>`;
  const keys = Object.entries(d).filter(([, v]) => v !== null && typeof v !== 'object');
  return keys.length ? `<ul>${keys.map(([k, v]) => `<li>${esc(k)}: ${esc(v)}</li>`).join('')}</ul>` : '<p class="muted">Mục này không có dữ kiện bổ sung.</p>';
}

const ruleHtml = rule => `<p><b>${esc(rule.title)}.</b> ${esc(rule.text)}</p>`;
const sourceHtml = rule => rule.source ? `<p>${esc(rule.source.title)}${rule.source.locator ? `, ${esc(rule.source.locator)}` : ''} ${rule.source.verified ? '(đã đối chiếu bản gốc)' : '(chưa đối chiếu)'}.</p>`
  : rule.evidence === 'calc' ? '<p>Phép tính trên dữ kiện, không dựa vào một câu của sách.</p>' : '<p>Chưa có nguồn trong kho. Mục này chỉ là giả thuyết của hệ thống.</p>';

function showDialog(html) { const b = $('#cpx-dlg-b'); b.innerHTML = html; autoLink(b, 'bt'); $('#cpx-dlg').showModal(); }

function openItem(id) {
  const r = current; const it = r.v2.items.find(x => x.id === id); if (!it) return;
  const rule = r.v2.rules[it.rule];
  showDialog(`<p class="eyebrow">${esc(it.kind_vi || 'Mục so sánh')} ${tag(it.evidence, it.status)}</p><h3>${esc(it.title)}</h3><p>${esc(it.plain)}</p>
    <h4>Dữ kiện</h4>${dataHtml(it, r.names)}<h4>Quy tắc <small>(${esc(STATUS[rule.status])})</small></h4>${ruleHtml(rule)}<h4>Nguồn</h4>${sourceHtml(rule)}
    ${it.experimental ? '<p class="cpx-warn">Giả thuyết thử nghiệm: chưa xác minh, không thuộc kết quả chính thức.</p>' : ''}`);
}
function openRule(id) {
  const rule = current.v2.rules[id]; if (!rule) return;
  showDialog(`<p class="eyebrow">Quy tắc ${tag(rule.evidence, rule.status)}</p><h3>${esc(rule.title)}</h3><p class="muted">${esc(STATUS[rule.status])}</p>${ruleHtml(rule)}<h4>Nguồn</h4>${sourceHtml(rule)}`);
}

// ---------------------------------------------------------------- sections
const gr = arr => arr.length ? `<div class="cpx-fl">${arr.map(i => fact(i.id, esc(i.plain), i)).join('')}</div>` : '';
const sec = (id, n, title, lead, body) => `<section class="cpx-sec" id="cpx-s-${id}"><h4>${n}. ${title}</h4>${lead ? `<p class="muted small">${lead}</p>` : ''}${body}</section>`;

function strengthCell(s, r, o) {
  const st = s.strength;
  if (st.decided) return `Phe của Nhật Chủ chiếm ${(st.own_share * 100).toFixed(1)}% (ngưỡng ${(st.threshold * 100).toFixed(0)}%), đứng ở phía <b>${esc(st.side)}</b>.`;
  const key = { special: 'special', missing: 'missing', borderline: 'border' }[st.reason];
  const ins = r.items.find(i => i.id === `ins.${key}.${o}`);
  const why = { borderline: `Phe của Nhật Chủ chiếm ${((st.own_share ?? 0) * 100).toFixed(1)}%, sát ngưỡng ${(st.threshold * 100).toFixed(0)}%`, special: `Có dấu hiệu ${s.special.map(x => x.name).join(', ')}`, missing: 'Thiếu dữ kiện để tính' }[st.reason];
  return `<b>Không kết luận vượng hay nhược.</b> ${esc(why)}.${ins ? ` <button type="button" class="link" data-cpx="${esc(ins.id)}">Vì sao?</button>` : ''}`;
}

function overview(ctx) {
  const { v2: r, names, chartA, chartB, A, B } = ctx, sa = r.structure.a, sb = r.structure.b, ta = r.tuvi_structure.a, tb = r.tuvi_structure.b;
  const phase = (c, x) => { try { return c && currentPhase(c.bazi, c.tuvi, x.req); } catch { return null; } };
  const ph = [phase(chartA, A), phase(chartB, B)];
  const luck = p => p ? (p.luck ? `${p.luck.name} (${p.luck.ten_god})` : 'chưa khởi vận') : 'không tính được';
  const han = p => p ? (p.dh ? `cung ${p.dh.palace} (${p.dh.age_from}–${p.dh.age_to} tuổi)` : 'chưa vào đại hạn') : 'không tính được';
  const month = s => s.month.ruling_element ? `${esc(s.month.branch)}: hành ${esc(s.month.ruling_element)} nắm lệnh, nhóm ${esc(s.month.ruling_group)} so với Nhật Chủ${s.month.ruling_in_own_camp ? ' (phe mình)' : ''}` : esc(s.month.branch);
  const rows = [
    ['Nhật Chủ', 'calc', 'verified', (s) => `${esc(s.day_master)} ${esc(s.dm_element)}`, null],
    ['Bốn trụ', 'calc', 'verified', (s) => esc(s.pillars), null],
    ['Ngũ Hành trên tám chữ', 'calc', 'verified', (s) => Object.entries(s.elements).map(([e, n]) => `${esc(e)} ${n}`).join(' · '), 'data-cpx="bz.elements"'],
    ['Nguyệt lệnh', 'sourced', 'verified', month, 'data-rule="CMP_MONTH_ORDER"'],
    ['Chữ cùng hành Nhật Chủ trong tàng can', 'calc', 'verified', (s) => s.has_root ? esc(s.roots.map(x => `${x.hidden} ở ${x.branch}`).join(', ')) : 'không có', null],
    ['Thế mạnh theo quy tắc 40%', 'sourced', 'partial', (s, o) => strengthCell(s, r, o), 'data-rule="CMP_STRENGTH_40"'],
    ['Đại vận hiện tại', 'calc', 'verified', (s, o, p) => esc(luck(p)), null],
    ['Đại hạn hiện tại (Tử Vi)', 'calc', 'verified', (s, o, p) => esc(han(p)), null],
    ['Cục · bản mệnh (Tử Vi)', 'calc', 'verified', (s, o, p, t) => `${esc(t.cuc)} · ${esc(t.menh_nap_am)}`, null],
  ];
  const tr = row => `<tr><th scope="row">${esc(row[0])} ${row[4] ? `<button type="button" class="cpx-q" ${row[4]} aria-label="Xem quy tắc và dữ kiện: ${esc(row[0])}">?</button>` : ''}<br>${tag(row[1], row[2])}</th><td>${row[3](sa, 'a', ph[0], ta)}</td><td>${row[3](sb, 'b', ph[1], tb)}</td></tr>`;
  return sec('overview', 1, 'Tổng quan từng người', 'Mỗi lá số được nhìn một mình trước khi so sánh.',
    `<div class="cpx-tw"><table class="cpx-t cpx-ov"><thead><tr><th>Điều được xét</th><th>${esc(names.a)}</th><th>${esc(names.b)}</th></tr></thead><tbody>${rows.map(tr).join('')}</tbody></table></div>
    <p class="muted small">Thế mạnh, nguyệt lệnh và tàng can được xét trước, vì các quan hệ bên dưới được đọc trong bối cảnh đó. Một lá số sát ngưỡng 40%, có dấu hiệu cách đặc biệt hoặc thiếu dữ kiện sẽ không bị ép thành vượng hay nhược.</p>`);
}

function pillars(ctx) {
  const { v2: r, names } = ctx;
  return sec('pillars', 2, 'Bốn trụ cạnh nhau', '', `<div class="cpx-tw"><table class="cpx-t"><thead><tr><th>Trụ</th><th>${esc(names.a)}</th><th>${esc(names.b)}</th></tr></thead><tbody>
    ${r.pillars.map(p => `<tr><td>${esc(PIL[p.slot])}</td><td>${esc(p.a)}${p.a_ten_god ? ` <small>${esc(p.a_ten_god)}</small>` : ' <small>Nhật Chủ</small>'}</td><td>${esc(p.b)}${p.b_ten_god ? ` <small>${esc(p.b_ten_god)}</small>` : ' <small>Nhật Chủ</small>'}</td></tr>`).join('')}</tbody></table></div>
    <p class="muted small">Chữ nhỏ bên cạnh là Thập Thần của chữ đó so với Nhật Chủ của chính lá số ấy. ${tag('calc', 'verified')} ${tag('sourced', 'verified')}</p>`);
}

function contacts(ctx) {
  const { v2: r, v1, names } = ctx;
  const direct = itemsOf(r, r.tiers.direct.ids).filter(i => i.layer === 'bazi' && i.kind !== 'element_count');
  const solid = direct.filter(i => !i.experimental), hyp = direct.filter(i => i.experimental);
  const parts = [];
  KIND_GROUP.forEach(([label, test]) => { const g = solid.filter(i => test(i.kind)); if (g.length) parts.push(`<h5>${label} <small>(${g.length})</small></h5>${gr(g)}`); });
  const tg = solid.filter(i => i.kind === 'ten_god_view');
  if (tg.length) parts.push(`<h5>Thập Thần hai chiều</h5>${gr(tg)}`);
  if (!parts.length) parts.push('<p class="muted">Không có quan hệ trực tiếp nào theo bảng giữa các chữ của hai lá số.</p>');
  const el = v1?.element_link ? `<p class="cpx-line">${tag('sourced', 'verified')} <b>Hai hành Nhật Chủ.</b> ${esc(v1.element_link.text.replace('người A', names.a).replace('người B', names.b))} <span class="muted">Chỉ là quan hệ sinh khắc giữa hai hành, chưa phải đánh giá về hai người.</span></p>` : '';
  return sec('contacts', 3, 'Tương tác Can Chi', 'Quan hệ giữa các chữ cụ thể của hai người, lấy từ bảng đã đối chiếu sách. Hợp, xung, hình, hại, phá chỉ cho biết hai chữ chạm nhau; sinh hay khắc không mặc định là tốt hay xấu.',
    el + parts.join('') + (hyp.length ? `<h5>Giả thuyết thử nghiệm <small>(chưa xác minh)</small></h5>${gr(hyp)}` : ''));
}

function tuvi(ctx) {
  const { v2: r, names } = ctx;
  const col = (o, s) => `<div class="cpx-c"><span class="k">${esc(names[o])} · ${esc(s.year)}</span><b>${esc(s.cuc)}</b><p class="cpx-pl">Bản mệnh ${esc(s.menh_nap_am)}</p><ul class="cpx-sl">${['Mệnh', 'Thân', 'Phu Thê', 'Phúc Đức'].map(n => `<li><b>${n}</b> ở ${esc(s[n].branch)}: ${s[n].major_stars.length ? esc(s[n].major_stars.map(x => x + (s[n].dignity?.[x] ? ` (${s[n].dignity[x]})` : '')).join(', ')) : 'vô chính diệu'}${s[n].tuan ? ' · Tuần' : ''}${s[n].triet ? ' · Triệt' : ''}</li>`).join('')}</ul></div>`;
  const pairs = r.items.filter(i => i.layer === 'tuvi' && i.tier === 'direct' && !['placement', 'napam'].includes(i.kind));
  const nap = r.items.filter(i => i.kind === 'napam');
  return sec('tuvi', 4, 'Tử Vi', 'Tử Vi được tính độc lập với Bát Tự. Chỉ nêu vị trí cung, sao và quan hệ hình học (cùng vị trí, xung chiếu, tam hợp, liền kề). Ý nghĩa khi cung của hai người gặp nhau không được diễn giải, vì không có nguồn nào nêu.',
    `<div class="cpx-cols">${col('a', r.tuvi_structure.a)}${col('b', r.tuvi_structure.b)}</div>${gr(pairs)}${nap.length ? `<h5>Giả thuyết thử nghiệm <small>(chưa xác minh)</small></h5>${gr(nap)}` : ''}`);
}

function support(ctx) {
  const { v2: r } = ctx;
  const mk = (tier, title) => { const it = itemsOf(r, r.tiers[tier].ids); return `<h5>${title}</h5>${it.length ? `<p class="muted small">Giả thuyết thử nghiệm: suy từ thế mạnh của từng lá số, chưa xác minh.</p>${gr(it)}` : `<p class="muted">Chưa có quy tắc đã xác minh để xếp mục nào vào đây. ${esc(r.tiers[tier].note)}</p>`}`; };
  return sec('support', 5, 'Hỗ trợ và hạn chế', 'Yếu tố có thể nâng đỡ hoặc làm hạn chế một quan hệ. Mục này chỉ nhận quy tắc đã xác minh; phần suy từ ngưỡng 40%, bù hành hay vai trò trụ nằm trong chế độ thử nghiệm.',
    mk('support', 'Yếu tố hỗ trợ') + mk('limit', 'Yếu tố hạn chế') + (!r.experimental && r.hidden_experimental ? `<p class="muted small">Có ${r.hidden_experimental} mục giả thuyết đang được ẩn.</p>` : ''));
}

function sources(ctx) {
  const { v2: r } = ctx;
  const ins = itemsOf(r, r.tiers.insufficient.ids), rules = Object.values(r.rules);
  return sec('sources', 6, 'Nguồn và giới hạn', '', `<h5>Chưa đủ căn cứ để kết luận</h5><p class="muted small">${esc(r.tiers.insufficient.note)}</p><div class="cpx-fl">${ins.map(i => `<button type="button" class="cpx-f ins" data-cpx="${esc(i.id)}"><span><b>${esc(i.title)}.</b> ${esc(i.plain)}</span></button>`).join('')}</div>
    <h5>Quy tắc đã dùng</h5><div class="cpx-fl">${rules.map(x => `<button type="button" class="cpx-f ${x.evidence === 'hypothesis' ? 'x' : ''}" data-rule="${esc(x.id)}">${tag(x.evidence, x.status)}<span><b>${esc(x.title)}</b> · ${esc(STATUS[x.status])}</span></button>`).join('')}</div>
    <h5>Nguồn</h5><ul class="cpx-src">${r.sources.map(s => `<li>${esc(s.title)} <small>${s.verified ? '(đã đối chiếu bản gốc)' : '(chưa đối chiếu)'}</small></li>`).join('') || '<li>Không có nguồn nào được dùng.</li>'}</ul>
    <h5>Ba loại câu trong trang này</h5><ul class="cpx-leg"><li>${tag('calc', 'verified')} đếm hoặc đặt cạnh dữ kiện đã tính, không diễn giải.</li><li>${tag('sourced', 'verified')} áp bảng hoặc phương pháp của một cuốn sách đã đối chiếu (nhãn “một phần” nghĩa là sách nêu phương pháp nhưng có chỗ hệ thống tự đặt, đã ghi trong quy tắc).</li><li>${tag('hypothesis', 'draft')} suy luận của hệ thống, chưa có nguồn; chỉ hiện ở chế độ thử nghiệm.</li></ul>
    <p class="muted small">${esc(r.principle)}</p>`);
}

const NAV = [['overview', 'Tổng quan'], ['pillars', 'Bốn trụ'], ['contacts', 'Can Chi'], ['tuvi', 'Tử Vi'], ['support', 'Hỗ trợ/hạn chế'], ['sources', 'Nguồn và giới hạn']];

/** ctx = { A, B (saved items), res (full response: v1 fields + v2), chartA, chartB (optional /api/chart results) } */
export function renderCompareResult(host, ctx) {
  const v2 = ctx.res.v2, names = { a: ctx.A.label, b: ctx.B.label };
  const c = { ...ctx, v2, v1: ctx.res, names };
  current = c;
  host.innerHTML = `<p class="muted cpx-pr">${esc(v2.principle)}${v2.experimental ? ' <b>Chế độ thử nghiệm đang bật.</b>' : ''}</p>
    <nav class="cpx-nav" aria-label="Các phần của bản so sánh">${NAV.map(([id, t]) => `<button type="button" data-go-sec="${id}">${t}</button>`).join('')}</nav>
    ${overview(c)}${pillars(c)}${contacts(c)}${tuvi(c)}${support(c)}${sources(c)}`;
  $$('[data-cpx]', host).forEach(b => b.onclick = () => openItem(b.dataset.cpx));
  $$('[data-rule]', host).forEach(b => b.onclick = () => openRule(b.dataset.rule));
  $$('[data-go-sec]', host).forEach(b => b.onclick = () => $(`#cpx-s-${b.dataset.goSec}`, host)?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  autoLink(host, 'bt');
}

export function initDetailDialog() {
  const d = $('#cpx-dlg'); d.addEventListener('click', e => { if (e.target === d) d.close(); });
}
