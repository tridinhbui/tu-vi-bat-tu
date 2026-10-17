// InterpretationSection chapters: calculations and traditional readings kept visibly separate.
import { $, $$, esc, STEMS, BRANCHES, EL, starKind, tenGodGroup, TEN_GOD_GROUPS, palaceOfSubject, claimLabel, elChip } from './util.js';
import { acc, notice, reasoningPanel, timeline, yearExplorer, findingCard } from './ui.js';
import { scopePanelBazi } from './scope.js';
import { easyReadings, emptyReading, classify, parsePhrase } from './beginner.js';
import { autoLink, terms } from './glossary.js';
import { elementBalanceHtml, godDistributionHtml, menhTamPhuongHtml, currentPhase, currentPhaseHtml } from './insights.js';

const LAYER_HINT = { 'Tượng': 'ý nghĩa biểu tượng', 'Khí': 'điều kiện mạnh yếu', 'Thế': 'vị trí trong cấu trúc', 'Cách': 'cách cục', 'Dụng': 'vai trò theo lĩnh vực', 'Biến': 'biến đổi theo thời gian', 'Phản': 'yếu tố đối trọng', 'Tổng': 'tổng hợp' };
const BASIS = { tinh_toan: ['Tính toán', 'dữ kiện lập từ lá số'], sach: ['Theo sách', 'có trích dẫn trang'], he_thong: ['Định nghĩa của hệ thống', 'cách hệ thống chọn để mô tả; không phải lời sách'] };
function analysisHtml(blocks) {
  if (!blocks?.length) return '';
  return `<div class="ch-an pro-only"><p class="eyebrow">Phân tích cấu trúc</p>${blocks.map(b => `<p class="an-p"><span class="an-tag" title="${esc(LAYER_HINT[b.layer] || '')}">${esc(b.layer)}</span>${esc(b.text)}<span class="an-meta"><span class="an-b an-${b.basis}" title="${esc(BASIS[b.basis][1])}">${BASIS[b.basis][0]}</span>${(b.src || []).map(x => `<span class="an-src">${esc(x)}</span>`).join('')}</span></p>`).join('')}</div>`;
}
const WHAT = {
  bt: { 'tong-quan': 'Tóm gọn lá số: chữ đại diện cho bạn (Nhật Chủ), mùa bạn sinh ra (tháng) và chặng đời bạn đang đi.',
    'nhat-chu': 'Nhật Chủ là “bạn” trong lá số. Phần này nói về tính chất của chữ đó và những mô tả mà sách cổ gắn với nó.',
    'ngu-hanh': 'Đếm xem năm hành và năm nhóm Thập Thần xuất hiện nhiều hay ít: đây là bức tranh cân bằng của lá số.',
    'su-nghiep': 'Nhìn vị trí của các nhóm Thập Thần liên quan đến công việc và tiền bạc.',
    'quan-he': 'Các chữ trong lá số hợp, xung, hại nhau ra sao; và cách người ta xem bạn đời qua trụ Ngày.',
    'dai-van': 'Các chặng 10 năm và từng năm. Mỗi chặng mang một “không khí” khác nhau; đây là dữ kiện, không phải dự đoán.',
    'cach-cuc': 'Cách phân loại “mẫu hình” của lá số. Phần này người mới chưa cần vội.' },
  tv: { 'tong-quan': 'Những điều cơ bản nhất của lá số: cung Mệnh, cung Thân, Cục và bản mệnh.',
    'ban-menh': 'Cung Mệnh là “con người bạn”. Phần này xem sao nào ở đó và quan hệ giữa Cục với bản mệnh.',
    'tinh-cach': 'Tính cách được xem qua cung Mệnh và cung Phúc Đức (đời sống tinh thần).',
    'cong-danh': 'Công việc và địa vị được xem qua cung Quan Lộc và cung đối diện Thiên Di.',
    'tai-bach': 'Tiền bạc được xem qua cung Tài Bạch (thu nhập) và cung Điền Trạch (của cải tích lũy).',
    'quan-he': 'Các mối quan hệ gần gũi, mỗi cung nói về một nhóm người khác nhau.',
    'dai-han': 'Các chặng 10 năm, mỗi chặng “đi vào” một cung và làm lĩnh vực đó nổi lên. Đây là dữ kiện, không phải dự đoán.',
    'cach-cuc': 'Những “tổ hợp sao” đặc biệt mà sách cổ đặt tên riêng.',
    'muoi-hai-cung': 'Tra nhanh cả mười hai cung. Bấm vào tên sao hoặc cung để xem giải thích.' },
};
const pad = n => String(n).padStart(2, '0');

function inferenceGraph(f) {
  const kinds = Object.values(f.why.kinds || {});
  const chain = f.why.chain.map((c, i) => ({ k: kinds[i], t: c.replace(/\s*@.*$/, '').replace(/\s*\((unverified|verified)\)/, '') }));
  const pick = k => chain.find(c => c.k === k);
  const box = (x, y, w, c, cls) => c ? `<g class="ig ${cls}"><rect x="${x}" y="${y}" width="${w}" height="54" rx="10"/><text x="${x + 12}" y="${y + 21}" class="ig-k">${{ fact: 'DỮ KIỆN', rule: 'QUY TẮC', source: 'NGUỒN', finding: 'NHẬN ĐỊNH' }[c.k]}</text><text x="${x + 12}" y="${y + 41}" class="ig-t">${esc(c.t.length > 30 ? c.t.slice(0, 29) + '…' : c.t)}</text></g>` : '';
  const a = (x1, y1, x2, y2) => `<path d="M${x1} ${y1}L${x2} ${y2}" class="ig-a" marker-end="url(#ig-m)"/>`;
  return `<svg class="ig-svg" viewBox="0 0 760 170" role="img" aria-label="Đồ thị suy luận: dữ kiện và nguồn dẫn tới quy tắc, quy tắc dẫn tới nhận định"><defs><marker id="ig-m" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8Z"/></marker></defs>
    ${box(8, 14, 210, pick('fact'), 'fact')}${box(8, 100, 210, pick('source'), 'source')}${box(290, 57, 190, pick('rule'), 'rule')}${box(552, 57, 200, pick('finding'), 'finding')}
    ${a(218, 41, 288, 77)}${a(218, 127, 288, 97)}${a(480, 84, 550, 84)}</svg>`;
}


const blockSys = b => /^(Bát Tự|Về Bát Tự|Nhật chi)/.test(b.text) || (b.src || []).some(x => /八字/.test(x)) ? 'bt' : /^Hai hệ thống/.test(b.text) ? 'both' : 'tv';
const PAL_CH = { 'Mệnh': 'ban-menh', 'Phúc Đức': 'tinh-cach', 'Quan Lộc': 'cong-danh', 'Thiên Di': 'cong-danh', 'Tài Bạch': 'tai-bach', 'Điền Trạch': 'tai-bach', 'Phu Thê': 'quan-he', 'Tử Tức': 'quan-he', 'Huynh Đệ': 'quan-he', 'Phụ Mẫu': 'quan-he', 'Nô Bộc': 'quan-he' };

function mount(host, chapters, prefix, ctx) {
  host.innerHTML = `<div class="rp-layout">
    <nav class="rp-toc" aria-label="Mục lục luận giải"><ol>${chapters.map((c, i) => `<li${c.pro ? ' class="pro-only"' : ''}><a href="#${prefix}-${c.id}" data-ch="${c.id}"><span>${pad(i + 1)}</span>${c.title}</a></li>`).join('')}</ol></nav>
    <div class="rp-body">${chapters.map((c, i) => `<article class="chapter${c.pro ? ' pro-only' : ''}" id="${prefix}-${c.id}"><header><span class="ch-no">${pad(i + 1)}</span><h3>${c.title}</h3></header><p class="lead">${c.lead}</p>${WHAT[prefix]?.[c.id] ? `<p class="ch-what easy-only"><b>Nói đơn giản:</b> ${WHAT[prefix][c.id]}</p>` : ''}${analysisHtml(c.blocks)}${c.calc || ''}${c.trad || ''}</article>`).join('')}
      <div class="sys-switch"><span>${prefix === 'bt' ? 'Muốn đọc cùng thời điểm sinh theo Tử Vi?' : 'Muốn đọc cùng thời điểm sinh theo Bát Tự?'}</span><button type="button" class="btn btn-ghost btn-sm" data-go="${prefix === 'bt' ? 'tu-vi' : 'bat-tu'}">${prefix === 'bt' ? 'Xem Tử Vi →' : 'Xem Bát Tự →'}</button></div></div></div>`;
  autoLink(host, prefix === 'bt' ? 'bt' : 'tv');
  $$('[data-jump]', host).forEach(r => r.onclick = () => $('#' + prefix + '-' + r.dataset.jump, host).scrollIntoView({ behavior: 'smooth', block: 'start' }));
  $$('.ref', host).forEach(r => r.onclick = () => ctx.openPalace(r.dataset.palace));
  const tg = $('.ig-toggle', host); if (tg) tg.onclick = () => { const on = tg.getAttribute('aria-pressed') !== 'true'; tg.setAttribute('aria-pressed', on); $('.ig-box', host).hidden = !on; tg.textContent = on ? 'Ẩn đồ thị suy luận' : 'Xem đồ thị suy luận'; };
  const links = $$('.rp-toc a', host);
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) links.forEach(l => { const on = l.dataset.ch === e.target.id.slice(prefix.length + 1); l.classList.toggle('on', on); const ol = l.closest('ol'); if (on && ol.scrollWidth > ol.clientWidth && matchMedia('(max-width:980px)').matches) ol.scrollTo({ left: l.offsetLeft - ol.clientWidth / 2 + l.offsetWidth / 2, behavior: 'smooth' }); }); }), { rootMargin: '-30% 0px -60% 0px' });
  $$('.chapter', host).forEach(c => io.observe(c));
  links.forEach(l => l.onclick = e => { e.preventDefault(); $(l.getAttribute('href'), host).scrollIntoView({ behavior: 'smooth', block: 'start' }); });
}

const shell = ctx => {
  const { reason, analysis } = ctx;
  const blocks = (sys, ...ids) => ids.flatMap(id => (analysis?.[id] || []).filter(b => [sys, 'both'].includes(blockSys(b)) && !(blockSys(b) === 'both' && sys === 'bt' && id !== 'tong-quan')));
  const calc = html => `<div class="ch-calc"><p class="eyebrow">Dữ kiện tính toán</p>${html}</div>`;
  const ref = name => `<button type="button" class="ref" data-palace="${esc(name)}">${esc(name)}<svg width="11" height="11" viewBox="0 0 12 12" aria-hidden="true"><path d="M3 9l6-6M4 3h5v5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg></button>`;
  const where = f => { const pn = palaceOfSubject(f.subject); return pn ? `cung ${ref(pn)}` : 'toàn lá số'; };
  const trad = (fs, note, topic, palace) => `<div class="ch-trad"><p class="eyebrow">Diễn giải truyền thống</p>
    <div class="pro-only">${fs.length ? fs.map(f => findingCard(f, where(f))).join('') + '<p class="muted small">Đây là cách đọc theo hệ biểu tượng truyền thống, không phải dự báo hay chẩn đoán.</p>' : notice('Chưa có quy tắc nào được kích hoạt cho phần này', note || 'Bộ quy tắc hiện hành chưa phủ tới nội dung này, nên hệ thống không đưa ra nhận định thay vì suy đoán.')}</div>
    <div class="easy-only">${easyReadings(fs, { where, empty: emptyReading(topic, terms(), { palace }) })}<p class="muted small">Đây là cách đọc theo hệ biểu tượng truyền thống, không phải dự báo hay chẩn đoán.</p></div></div>`;
  const deep = (sysKey, label, traceObj) => { const d = reason.systems[sysKey]; return `<div class="ch-calc"><p class="eyebrow">Dành cho người muốn kiểm chứng</p>
    ${acc(`Văn bản luận giải — ${label}`, `${d.findings.length} nhận định · ${d.pending.length} quy tắc chờ dữ kiện`, `<pre class="prose-pre">${esc(d.text)}</pre>${d.pending.length ? `<h5>Quy tắc chưa đủ dữ kiện</h5><ul>${d.pending.map(p => `<li>${esc(p.rule)} <span class="muted">@${esc(p.subject)} · thiếu ${esc(p.missing_facts.join(', '))}</span></li>`).join('')}</ul>` : ''}`)}
    ${d.findings.length ? acc('Tất cả nhận định và chuỗi suy luận', `${d.findings.length} nhận định`, d.findings.map(f => findingCard(f, where(f))).join('')) : ''}
    ${acc(`Vết tính toán — ${label}`, 'từng bước chuẩn hóa và lập lá số', `<pre class="trace">${esc(JSON.stringify(traceObj, null, 1))}</pre>`)}
    ${reason.pack_problems.length ? notice('Vấn đề trong bộ quy tắc', esc(reason.pack_problems.join('; ')), 'warn') : ''}</div>`; };
  return { blocks, calc, ref, where, trad, deep };
};

const highlightsHtml = (fs, chTitle, chOf, extra) => {
  const ver = fs.filter(f => f.basis === 'verified'), top = ver.filter(f => chOf(f) !== 'chuyen-sau').slice(0, 4);
  return `<h5>Điểm nổi bật</h5><p class="hl-sum"><b>${fs.length}</b> nhận định được kích hoạt: <b>${ver.length}</b> từ quy tắc đã đối chiếu sách, <b>${fs.length - ver.length}</b> từ quy tắc nháp.</p>${top.length ? `<ul class="hl-list">${top.map(f => `<li><button type="button" data-jump="${chOf(f)}"><span class="k">${chTitle[chOf(f)] || ''}</span><span>${esc(claimLabel(f.claim))}</span></button></li>`).join('')}</ul>` : ''}${extra || ''}`;
};

export function renderBaziReport(host, chart, ctx, parts) {
  const b = chart.bazi, t = chart.tuvi, { blocks, calc, trad, deep } = shell(ctx);
  const dm = STEMS[b.pillars.day.stem], month = b.pillars.month, mb = BRANCHES[month.branch];
  const fs = (ctx.reason.systems.bat_tu?.findings || []).map(f => ({ ...f, sys: 'bat_tu' }));
  const chOf = f => /^bt_(ri_gan|thieu_hanh|nap_am)/.test(f.claim) ? 'nhat-chu' : 'cach-cuc';
  const of = id => fs.filter(f => chOf(f) === id);
  const TITLE = { 'nhat-chu': 'Nhật Chủ & tính cách', 'cach-cuc': 'Cách cục & Dụng thần' };
  const ph = currentPhase(b, t, ctx.req);
  const godCount = ks => Object.entries(ks.reduce((o, k) => { const g = tenGodGroup(b.pillars[k].stem_ten_god); if (g) o[g] = (o[g] || 0) + 1; return o; }, {})).map(([g, n]) => `${g} ×${n}`).join(', ') || 'không có';
  const chapters = [
    { id: 'tong-quan', title: 'Tổng quan Bát Tự', lead: `Nhật Chủ <b>${esc(dm.n)}</b> (${dm.e}) sinh vào tháng ${esc(mb.n)}; đại vận ${esc(b.luck_direction)}, khởi vận sau khoảng ${b.luck_start.years} năm ${b.luck_start.months} tháng.`, blocks: blocks('bt', 'tong-quan'),
      calc: calc(`<div class="facts"><div><span class="k">Nhật Chủ</span><b>${esc(dm.n)} ${dm.e}</b></div><div><span class="k">Nguyệt lệnh</span><b>${esc(mb.n)} (${mb.e})</b></div><div><span class="k">Trường sinh so với nguyệt lệnh</span><b>${esc(month.stage_vs_day_master)}</b></div><div><span class="k">Đại vận</span><b>${esc(b.luck_direction)}</b></div><div><span class="k">Khởi vận</span><b>${b.luck_start.years} năm ${b.luck_start.months} tháng</b></div><div><span class="k">Đại vận hiện tại</span><b>${ph.luck ? `${esc(ph.luck.name)}` : 'chưa khởi'}</b></div></div><div class="pro-only">${highlightsHtml(fs, TITLE, chOf)}</div>${acc('Nguyệt Lệnh', 'Tháng sinh và mùa của lá số', parts.nguyetLenh)}`),
      trad: notice('Về mức độ tin cậy', 'Quy tắc đã đối chiếu sách và quy tắc nháp luôn được ghi nhãn riêng ở từng nhận định.', 'info') && `<div class="ch-trad">${notice('Về mức độ tin cậy', 'Quy tắc đã đối chiếu sách và quy tắc nháp luôn được ghi nhãn riêng ở từng nhận định. Đây là cách đọc theo hệ biểu tượng, không phải kết luận.', 'info')}</div>` },
    { id: 'nhat-chu', title: 'Nhật Chủ & tính cách', lead: `Nhật Chủ ${esc(dm.n)} thuộc hành ${elChip(dm.e)}; Thập thần trên thiên can: ${esc(godCount(['year', 'month', 'hour']))}.`, blocks: blocks('bt', 'tinh-cach'),
      calc: calc(`<h5>Thấu can và thông căn (dữ kiện vị trí)</h5>${parts.thongCan}`), trad: trad(of('nhat-chu'), null, 'bt:nhat-chu') },
    { id: 'ngu-hanh', title: 'Ngũ Hành & Thập Thần', lead: 'Sự phân bố của năm hành và năm nhóm Thập thần trên toàn lá số.',
      calc: calc(`<h5>Cân bằng Ngũ Hành</h5>${elementBalanceHtml(b)}<h5>Phân bố Thập Thần</h5>${godDistributionHtml(b)}${acc('Thập Thần theo từng trụ', 'Quan hệ của mỗi can với Nhật Chủ', parts.thapThan)}${acc('Tàng Can', 'Can ẩn trong từng địa chi', parts.tangCan)}`), trad: '' },
    { id: 'su-nghiep', title: 'Sự nghiệp & Tài lộc', lead: 'Vị trí của nhóm Quan Sát, Ấn và Tài trong lá số.', blocks: blocks('bt', 'cong-danh', 'tai-bach'),
      calc: calc(`<p>Trên thiên can: ${esc(godCount(['year', 'month', 'hour']))}. Chi tiết số lượng trong tàng can xem ở chương <i>Ngũ Hành & Thập Thần</i>.</p>`), trad: trad([], 'Chưa có quy tắc Bát Tự nào về sự nghiệp hay tài lộc được kích hoạt hoặc đã xác minh.', 'bt:su-nghiep') },
    { id: 'quan-he', title: 'Quan hệ Can Chi & hôn nhân', lead: `${parts.relCount ? `Có ${parts.relCount} quan hệ hợp, xung, hại, phá, hình giữa các trụ.` : 'Không có hợp, xung, hại, phá, hình nào giữa các trụ gốc.'}`, blocks: blocks('bt', 'quan-he'),
      calc: calc(parts.relations), trad: trad([], 'Chưa có quy tắc Bát Tự về quan hệ hôn nhân được kích hoạt hoặc đã xác minh.', 'bt:quan-he') },
    { id: 'dai-van', title: 'Đại vận & lưu niên', lead: `Đại vận ${esc(b.luck_direction)}; hiện ở ${ph.luck ? `đại vận ${esc(ph.luck.name)} (${esc(ph.luck.ten_god)})` : 'giai đoạn chưa khởi vận'}.`, blocks: blocks('bt', 'dai-van'),
      calc: calc(`<h5>Các đại vận</h5>${parts.luck}<h5>Lưu niên và lưu nguyệt</h5><div id="bt-year"></div>`), trad: '' },
    { id: 'cach-cuc', title: 'Cách cục & Dụng thần', lead: 'Phân loại cấu trúc và hành cần cân bằng của lá số.',
      calc: calc(`<div class="pro-only">${notice('Cách cục và Dụng thần chưa được xác định', 'Hai nội dung này cần bộ quy tắc đã đối chiếu nguồn và phụ thuộc trường phái. Hệ thống không đoán để tránh đưa ra kết luận thiếu căn cứ; hiện chỉ nêu từng tiêu chí ở chương Nhật Chủ.')}</div>`), trad: trad(of('cach-cuc'), 'Không có cách cục nào được nhận ra.', 'bt:cach-cuc') },
    { id: 'chuyen-sau', pro: true, title: 'Luận giải chuyên sâu', lead: 'Văn bản do bộ máy sinh từ các nhận định, kèm vết tính toán.', calc: deep('bat_tu', 'Bát Tự', { normalization: ctx.chartRaw.normalization_trace.steps, bazi: b.trace.steps }), trad: '' },
  ];
  mount(host, chapters, 'bt', ctx);
  host.insertAdjacentHTML('afterbegin', scopePanelBazi(b));
  yearExplorer($('#bt-year', host), ctx.req, b, 'bazi');
}

const XSTATE = { thanh_thuong: ['Thành cách, thế mạnh', 0], thanh: ['Thành cách', 1], pha_duoc_cuu: ['Bị phá nhưng được cứu', 2], bi_pha: ['Bị phá cách', 3], hinh_thuc: ['Mới có hình thức', 4], chua_du_du_kien: ['Chưa đủ dữ kiện để kết luận', 5], khong_hien: ['Không hiện', 6] };
const idText = s => String(s).replace(/_/g, ' ');
function experimentalHtml(x) {
  if (!x) return '';
  const fs = (x.formations || []).slice().sort((a, b) => (XSTATE[a.state]?.[1] ?? 9) - (XSTATE[b.state]?.[1] ?? 9));
  const shown = fs.filter(f => f.state !== 'khong_hien'), hidden = fs.filter(f => f.state === 'khong_hien');
  const card = f => `<div class="exp-card st-${esc(f.state)}"><h5>${esc(f.name_vi)} <span class="exp-pill">${esc(XSTATE[f.state]?.[0] || f.state)}</span></h5><p>${esc(f.text)}</p>
    ${f.breakers?.length ? `<p class="small"><b>Phá cách:</b> ${esc(f.breakers.map(idText).join('; '))}</p>` : ''}${f.rescuers?.length ? `<p class="small"><b>Cứu giải:</b> ${esc(f.rescuers.map(idText).join('; '))}</p>` : ''}
    ${f.uncovered_breakers?.length ? `<p class="small"><b>Phá cách chưa được cứu:</b> ${esc(f.uncovered_breakers.map(idText).join('; '))}</p>` : ''}${f.refutations?.length ? `<p class="small"><b>Phản chứng:</b> ${esc(f.refutations.map(idText).join('; '))}</p>` : ''}
    ${f.missing_for_next_level?.length ? `<p class="small muted"><b>Còn thiếu để lên bậc:</b> ${esc(f.missing_for_next_level.map(idText).join('; '))}</p>` : ''}</div>`;
  return `<div class="exp"><p class="exp-tag">Thử nghiệm · chưa đối chiếu sách</p><p class="small">${esc(x.warning || 'Các điều kiện thành, phá, cứu do người xây dựng hệ thống đặt ra từ kiến thức chung, chưa đối chiếu trang sách nào. Chỉ mô tả cấu trúc, không dự báo.')}</p>
    ${shown.length ? shown.map(card).join('') : '<p class="muted">Không có cách nào trong danh sách thử nghiệm hiện hình trên lá số này.</p>'}
    ${hidden.length ? acc('Các cách đã kiểm tra nhưng không hiện', `${hidden.length} cách`, `<ul class="plain">${hidden.map(f => `<li>${esc(f.name_vi)}</li>`).join('')}</ul>`) : ''}</div>`;
}

export function renderTuviReport(host, chart, ctx) {
  const b = chart.bazi, t = chart.tuvi, tv = ctx.tv, { blocks, calc, ref, trad, deep } = shell(ctx);
  const fs = (ctx.reason.systems.tu_vi?.findings || []).map(f => ({ ...f, sys: 'tu_vi' }));
  const chOf = f => /^cach_|thanh_cach/.test(f.claim) ? 'cach-cuc' : (PAL_CH[palaceOfSubject(f.subject)] || 'chuyen-sau');
  const of = id => fs.filter(f => chOf(f) === id);
  const TITLE = { 'ban-menh': 'Bản Mệnh', 'tinh-cach': 'Tính cách', 'cong-danh': 'Công danh', 'tai-bach': 'Tài Bạch', 'quan-he': 'Quan hệ', 'cach-cuc': 'Cách Cục' };
  const stars = p => {
    const m = p.major_stars, mi = p.stars.filter(s => !m.includes(s)), pos = mi.filter(s => starKind(s) === 'pos'), neg = mi.filter(s => starKind(s) === 'neg');
    return `chính tinh ${m.length ? '<b>' + esc(m.map(s => s + (p.major_dignity?.[s] ? ` (${p.major_dignity[s]})` : '')).join(', ')) + '</b>' : '<i>vô chính diệu</i>'}${pos.length ? `; cát tinh ${esc(pos.join(', '))}` : ''}${neg.length ? `; sát/hung tinh ${esc(neg.join(', '))}` : ''}`;
  };
  const palaceP = name => { const p = tv.byName[name]; return `<li><span class="li-h">${ref(name)}<span class="muted">${esc(p.stem)} ${esc(p.branch)}${p.tuan ? ' · Tuần' : ''}${p.triet ? ' · Triệt' : ''}</span></span><span>${stars(p)}.</span></li>`; };
  const palaceList = names => `<ul class="plist">${names.map(palaceP).join('')}</ul>`;
  const tuHoa = Object.entries(t.tu_hoa).map(([k, v]) => `<li><b>${esc(k)}</b> tại ${esc(v.star)} <span class="muted">· cung ${esc(t.palaces.find(p => p.branch_index === v.branch)?.name || '')}</span></li>`).join('');
  const ph = currentPhase(b, t, ctx.req);
  // Mười hai cung: one accordion per palace, facts only
  const p12 = t.palaces.slice().sort((a, c) => (a.branch_index - tv.menh.branch_index + 12) % 12 - (c.branch_index - tv.menh.branch_index + 12) % 12).map(p => {
    const s = t.structure[p.branch], mi = p.stars.filter(x => !p.major_stars.includes(x)), g = k => mi.filter(x => starKind(x) === k);
    const hoa = Object.entries(t.tu_hoa).filter(([, v]) => v.branch === p.branch_index).map(([k, v]) => `${k} (${v.star})`);
    const pf = fs.filter(f => palaceOfSubject(f.subject) === p.name), d = t.dai_han.find(x => x.branch === p.branch);
    const row = (k, v) => v ? `<div><span class="k">${k}</span>${v}</div>` : '';
    return acc(`${esc(p.name)} <span class="muted">· ${esc(p.stem)} ${esc(p.branch)}</span>`, esc(p.major_stars.join(' · ') || 'vô chính diệu'), `<div class="p12-s">
      ${row('Chính tinh', p.major_stars.length ? esc(p.major_stars.map(x => x + (p.major_dignity?.[x] ? ` (${p.major_dignity[x]})` : '')).join(', ')) : '<i>vô chính diệu</i>')}
      ${row('Cát tinh', esc(g('pos').join(', ')))}${row('Sát / hung tinh', esc(g('neg').join(', ')))}${row('Phụ tinh khác', esc(g('neu').join(', ')))}
      ${row('Tứ Hóa', esc(hoa.join('; ')))}${row('Tuần / Triệt', esc([p.tuan && 'Tuần', p.triet && 'Triệt'].filter(Boolean).join(' + ')))}${row('Đại hạn', d ? `${d.age_from}–${d.age_to} tuổi` : '')}
      ${row('Xung chiếu', `${ref(t.palaces.find(x => x.branch === s.opposite).name)}`)}${row('Tam hợp', s.tam_hop.map(x => ref(t.palaces.find(y => y.branch === x).name)).join(' · '))}
      ${row('Nhận định', (pf.length ? `<span class="pro-only">${esc(pf.map(f => claimLabel(f.claim)).join('; '))}</span>` : '<span class="pro-only muted">chưa có quy tắc được kích hoạt</span>') + `<span class="easy-only">${(() => { const sh = classify(pf).show; return sh.length ? esc(sh.map(f => parsePhrase(f).core).join('; ')) : `<span class="muted">${esc(terms()['palace:' + p.name]?.plain || '')} Chưa có luận giải cá nhân hóa cho cung này.</span>`; })()}</span>`)}</div>`);
  }).join('');
  const chapters = [
    { id: 'tong-quan', title: 'Tổng quan Tử Vi', lead: `Lá số lập cho người sinh năm ${esc(t.year_gz)} (âm lịch ${t.lunar.day}/${t.lunar.month}/${t.lunar.year}${t.lunar.leap ? ' nhuận' : ''}), ${esc(t.yin_yang_gender)}.`, blocks: blocks('tv', 'tong-quan'),
      calc: calc(`<div class="facts"><div><span class="k">Mệnh cung</span><b>${esc(tv.menh.stem)} ${esc(tv.menh.branch)}</b></div><div><span class="k">Thân cư</span><b>${esc(tv.than.name)}</b></div><div><span class="k">Cục</span><b>${esc(t.cuc.name)}</b></div><div><span class="k">Bản mệnh</span><b>${esc(t.menh_nap_am)}</b></div><div><span class="k">Cục và Mệnh</span><b>${esc(t.menh_cuc_relation)}</b></div><div><span class="k">Đại hạn hiện tại</span><b>${ph.dh ? `${esc(ph.dh.palace)} (${ph.dh.age_from}–${ph.dh.age_to})` : 'chưa vào'}</b></div></div><div class="pro-only">${highlightsHtml(fs, TITLE, chOf)}</div>`),
      trad: `<div class="ch-trad">${notice('Về mức độ tin cậy', 'Quy tắc đã đối chiếu sách và quy tắc nháp luôn được ghi nhãn riêng ở từng nhận định. Đây là cách đọc theo hệ biểu tượng, không phải kết luận.', 'info')}</div>` },
    { id: 'ban-menh', title: 'Bản Mệnh', lead: `Bản mệnh ${esc(t.menh_nap_am)} thuộc hành ${esc(t.menh_element)}; ${esc(t.cuc.name)} thuộc hành ${esc(t.cuc.element)}.`, blocks: blocks('tv', 'ban-menh'),
      calc: calc(`${t.extras?.menh_chu ? `<div class="facts"><div><span class="k">Mệnh chủ (theo chi cung Mệnh)</span><b>${esc(t.extras.menh_chu.star)}</b></div><div><span class="k">Thân chủ (theo chi năm)</span><b>${esc(t.extras.than_chu.star)}</b></div><div><span class="k">Độ tin cậy</span><b>công thức phổ biến, chưa đối chiếu sách</b></div></div>` : ''}${palaceList(['Mệnh'])}<h5>Tam phương tứ chính của cung Mệnh</h5>${menhTamPhuongHtml(t)}<h5>Tứ Hóa theo can năm</h5><ul class="plain">${tuHoa}</ul>`), trad: trad(of('ban-menh'), null, 'tv:ban-menh') },
    { id: 'tinh-cach', title: 'Tính cách', lead: 'Nhìn từ cung Mệnh và cung Phúc Đức.', blocks: blocks('tv', 'tinh-cach'), calc: calc(palaceList(['Mệnh', 'Phúc Đức'])), trad: trad(of('tinh-cach'), null, 'tv:tinh-cach') },
    { id: 'cong-danh', title: 'Công danh', lead: 'Cung Quan Lộc và cung đối Thiên Di.', blocks: blocks('tv', 'cong-danh'), calc: calc(palaceList(['Quan Lộc', 'Thiên Di'])), trad: trad(of('cong-danh'), null, 'tv:cong-danh') },
    { id: 'tai-bach', title: 'Tài Bạch', lead: 'Cung Tài Bạch và Điền Trạch.', blocks: blocks('tv', 'tai-bach'), calc: calc(palaceList(['Tài Bạch', 'Điền Trạch'])), trad: trad(of('tai-bach'), null, 'tv:tai-bach') },
    { id: 'quan-he', title: 'Quan hệ', lead: 'Các cung liên quan đến người thân và các mối quan hệ.', blocks: blocks('tv', 'quan-he'), calc: calc(palaceList(['Phu Thê', 'Tử Tức', 'Huynh Đệ', 'Phụ Mẫu', 'Nô Bộc'])), trad: trad(of('quan-he'), null, 'tv:quan-he') },
    { id: 'dai-han', title: 'Đại hạn & lưu niên', lead: `Đại hạn chạy ${esc(t.dai_han_direction)}; ${ph.dh ? `hiện ở cung ${esc(ph.dh.palace)} (${ph.dh.age_from}–${ph.dh.age_to} tuổi)` : 'chưa vào đại hạn đầu'}.`, blocks: blocks('tv', 'dai-van'),
      calc: calc(`<h5>Các đại hạn</h5>${tv.timelineHtml}<h5>Lưu niên</h5><div id="tv-year"></div>`), trad: '' },
    { id: 'cach-cuc', title: 'Cách cục', lead: 'Các hình thái đặc biệt mà bộ quy tắc hiện hành có thể nhận ra.', blocks: blocks('tv', 'cach-cuc'),
      calc: calc(`${experimentalHtml(ctx.reason.experimental)}<h5>Nhận diện theo tên (vị trí sao)</h5>${(t.extras?.cach_cuc || []).length ? `<ul class="cc-list">${t.extras.cach_cuc.map(x => `<li><b>${esc(x.name)}</b><span class="muted">${esc(x.evidence)}</span></li>`).join('')}</ul><p class="muted small">Đây chỉ là nhận diện tên cách theo vị trí các sao. Ý nghĩa cát hay hung của từng cách chưa được đối chiếu sách nên hệ thống không nêu. Tên cách và nhóm sao theo thông lệ phổ biến, chưa đối chiếu trang sách.</p>` : '<p class="muted">Không nhận ra cách nào trong danh sách các cách được kiểm tra.</p>'}<h5>Nhận định từ bộ quy tắc</h5><p>Số nhận định về cách cục: ${of('cach-cuc').length || 'không có'}.</p>`),
      trad: (() => { const c = of('cach-cuc'); return `<div class="ch-trad"><p class="eyebrow">Diễn giải truyền thống</p><div class="pro-only">${c.length ? `<button type="button" class="btn btn-ghost btn-sm ig-toggle" aria-pressed="false">Xem đồ thị suy luận</button><div class="ig-box" hidden>${inferenceGraph(c[0])}<p class="muted small">Ví dụ cho nhận định đầu tiên.</p></div>${c.map(f => findingCard(f, shell(ctx).where(f))).join('')}` : notice('Không có cách cục nào được nhận ra', '')}</div><div class="easy-only">${easyReadings(c, { where: shell(ctx).where, empty: emptyReading('tv:cach-cuc', terms()) })}</div></div>`; })() },
    { id: 'muoi-hai-cung', title: 'Toàn bộ mười hai cung', lead: 'Tra nhanh từng cung: sao, Tứ Hóa, Tuần Triệt, đại hạn và nhận định.', calc: calc(`<div class="p12">${p12}</div>`), trad: '' },
    { id: 'chuyen-sau', pro: true, title: 'Luận giải chuyên sâu', lead: 'Văn bản do bộ máy sinh từ các nhận định, kèm vết tính toán.', calc: deep('tu_vi', 'Tử Vi', { normalization: ctx.chartRaw.normalization_trace.steps, tuvi: t.trace.steps }), trad: '' },
  ];
  mount(host, chapters, 'tv', ctx);
  yearExplorer($('#tv-year', host), ctx.req, b, 'tuvi');
}
