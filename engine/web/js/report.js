// InterpretationSection chapters: calculations and traditional readings kept visibly separate.
import { $, $$, esc, STEMS, BRANCHES, EL, starKind, tenGodGroup, TEN_GOD_GROUPS, palaceOfSubject, claimLabel, elChip } from './util.js';
import { acc, notice, reasoningPanel, timeline, yearExplorer, findingCard } from './ui.js';

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

export function renderReport(host, chart, ctx) {
  const { bazi: b, tuvi: t } = chart, tv = ctx.tv, reason = ctx.reason;
  const dm = STEMS[b.pillars.day.stem];
  const tvF = reason.systems.tu_vi?.findings || [], batF = reason.systems.bat_tu?.findings || [];
  const ref = name => `<button type="button" class="ref" data-palace="${esc(name)}">${esc(name)}<svg width="11" height="11" viewBox="0 0 12 12" aria-hidden="true"><path d="M3 9l6-6M4 3h5v5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg></button>`;
  const stars = p => {
    const m = p.major_stars, mi = p.stars.filter(s => !m.includes(s)), pos = mi.filter(s => starKind(s) === 'pos'), neg = mi.filter(s => starKind(s) === 'neg');
    return `chính tinh ${m.length ? '<b>' + esc(m.join(', ')) + '</b>' : '<i>vô chính diệu</i>'}${pos.length ? `; cát tinh ${esc(pos.join(', '))}` : ''}${neg.length ? `; sát/hung tinh ${esc(neg.join(', '))}` : ''}`;
  };
  const palaceP = name => { const p = tv.byName[name]; return `<li><span class="li-h">${ref(name)}<span class="muted">${esc(p.stem)} ${esc(p.branch)}${p.tuan ? ' · Tuần' : ''}${p.triet ? ' · Triệt' : ''}</span></span><span>${stars(p)}.</span></li>`; };
  const palaceList = names => `<ul class="plist">${names.map(palaceP).join('')}</ul>`;
    const godCount = ks => Object.entries(ks.reduce((o, k) => { const g = tenGodGroup(b.pillars[k].stem_ten_god); if (g) o[g] = (o[g] || 0) + 1; return o; }, {})).map(([g, n]) => `${g} ×${n}`).join(', ') || 'không có';
  const stemGods = ['year', 'month', 'hour'];
  const allHidden = Object.values(b.pillars).flatMap(p => p.hidden.map(h => tenGodGroup(h.ten_god)));
  const hid = g => allHidden.filter(x => x === g).length;
  const tuHoa = Object.entries(t.tu_hoa).map(([k, v]) => `<li><b>${esc(k)}</b> tại ${esc(v.star)} <span class="muted">· cung ${esc(t.palaces.find(p => p.branch_index === v.branch)?.name || '')}</span></li>`).join('');

  const allF = [...tvF.map(f => ({ ...f, sys: 'tu_vi' })), ...batF.map(f => ({ ...f, sys: 'bat_tu' }))];
  const PAL_CH = { 'Mệnh': 'ban-menh', 'Phúc Đức': 'tinh-cach', 'Quan Lộc': 'cong-danh', 'Thiên Di': 'cong-danh', 'Tài Bạch': 'tai-bach', 'Điền Trạch': 'tai-bach', 'Phu Thê': 'quan-he', 'Tử Tức': 'quan-he', 'Huynh Đệ': 'quan-he', 'Phụ Mẫu': 'quan-he', 'Nô Bộc': 'quan-he' };
  const chOf = f => f.sys === 'bat_tu' ? (/^bt_(ri_gan|thieu_hanh)/.test(f.claim) ? 'tinh-cach' : 'cach-cuc')
    : /^cach_|thanh_cach/.test(f.claim) ? 'cach-cuc' : (PAL_CH[palaceOfSubject(f.subject)] || 'chuyen-sau');
  const fsFor = id => allF.filter(f => chOf(f) === id);
  const where = f => { const pn = palaceOfSubject(f.subject); return pn ? `cung ${ref(pn)}` : 'toàn lá số'; };
  const trad = (fs, extraNote) => `<div class="ch-trad"><p class="eyebrow">Diễn giải truyền thống</p>${fs.length ? fs.map(f => findingCard(f, where(f))).join('') + '<p class="muted small">Đây là cách đọc theo hệ biểu tượng truyền thống, không phải dự báo hay chẩn đoán.</p>' : notice('Chưa có quy tắc nào được kích hoạt cho phần này', extraNote || 'Bộ quy tắc hiện hành chưa phủ tới nội dung này, nên hệ thống không đưa ra nhận định thay vì suy đoán.')}</div>`;
  const calc = html => `<div class="ch-calc"><p class="eyebrow">Dữ kiện tính toán</p>${html}</div>`;

  const chapters = [
    { id: 'tong-quan', title: 'Tổng quan', lead: `Lá số lập cho người sinh năm ${esc(t.year_gz)} (âm lịch ${t.lunar.day}/${t.lunar.month}/${t.lunar.year}${t.lunar.leap ? ' nhuận' : ''}), ${esc(t.yin_yang_gender)}.`,
      calc: calc(`<div class="facts">
        <div><span class="k">Mệnh cung</span><b>${esc(tv.menh.stem)} ${esc(tv.menh.branch)}</b></div><div><span class="k">Thân cư</span><b>${esc(tv.than.name)}</b></div>
        <div><span class="k">Cục</span><b>${esc(t.cuc.name)}</b></div><div><span class="k">Bản mệnh</span><b>${esc(t.menh_nap_am)}</b></div>
        <div><span class="k">Nhật Chủ</span><b>${esc(dm.n)} ${dm.e}</b></div><div><span class="k">Nguyệt lệnh</span><b>${esc(BRANCHES[b.pillars.month.branch].n)}</b></div></div>
        <p>Hai hệ thống được tính độc lập từ cùng một thời điểm sinh đã chuẩn hóa. Phần “dữ kiện tính toán” là kết quả quy tắc lịch pháp; phần “diễn giải truyền thống” luôn được tách riêng và ghi rõ trạng thái nguồn.</p>`),
      trad: notice('Về mức độ tin cậy', 'Mọi quy tắc luận giải hiện là bản nháp, chưa đối chiếu đủ nguồn. Hãy xem đây là cách đọc theo hệ biểu tượng, không phải kết luận.', 'info') },
    { id: 'ban-menh', title: 'Bản Mệnh', lead: `Bản mệnh ${esc(t.menh_nap_am)} thuộc hành ${esc(t.menh_element)}; ${esc(t.cuc.name)} thuộc hành ${esc(t.cuc.element)}.`,
      calc: calc(`<p>Quan hệ giữa Cục và Mệnh: <b>${esc(t.menh_cuc_relation)}</b>.</p>${palaceList(['Mệnh'])}<h5>Tứ Hóa theo can năm</h5><ul class="plain">${tuHoa}</ul>`), refs: ['Mệnh'] },
    { id: 'tinh-cach', title: 'Tính cách', lead: `Nhìn từ cung Mệnh, Phúc Đức và Nhật Chủ ${esc(dm.n)} (${dm.e}).`,
      calc: calc(`${palaceList(['Mệnh', 'Phúc Đức'])}<p>Nhật Chủ <b>${esc(dm.n)}</b> thuộc hành ${elChip(dm.e)}. Thập thần trên thiên can: ${esc(godCount(stemGods))}.</p>`), refs: ['Mệnh', 'Phúc Đức'] },
    { id: 'cong-danh', title: 'Công danh', lead: 'Cung Quan Lộc và vị trí đối xứng Thiên Di trong tam phương của Mệnh.',
      calc: calc(`${palaceList(['Quan Lộc', 'Thiên Di'])}<p>Trên Bát Tự, nhóm Quan Sát xuất hiện ${godCount(stemGods).includes('Quan Sát') ? '' : 'không '}trên thiên can; trong tàng can có ${hid('Quan Sát')} chữ thuộc nhóm này, ${hid('Ấn')} chữ thuộc nhóm Ấn.</p>`), refs: ['Quan Lộc', 'Thiên Di'] },
    { id: 'tai-bach', title: 'Tài Bạch', lead: 'Cung Tài Bạch, Điền Trạch và nhóm Tài trong Bát Tự.',
      calc: calc(`${palaceList(['Tài Bạch', 'Điền Trạch'])}<p>Nhóm Tài trên thiên can: ${esc(godCount(stemGods).includes('Tài') ? godCount(stemGods).split(', ').filter(x => x.startsWith('Tài')).join(', ') : 'không có')}; trong tàng can có ${hid('Tài')} chữ thuộc nhóm Tài.</p>`), refs: ['Tài Bạch', 'Điền Trạch'] },
    { id: 'quan-he', title: 'Quan hệ', lead: 'Các cung liên quan đến người thân và các mối quan hệ.',
      calc: calc(`${palaceList(['Phu Thê', 'Tử Tức', 'Huynh Đệ', 'Phụ Mẫu', 'Nô Bộc'])}<p>Bát Tự có ${Object.values(b.relations).reduce((n, v) => n + v.length, 0)} quan hệ Can Chi giữa các trụ (hợp, xung, hại, phá, hình). Xem chi tiết trong mục <i>Quan hệ Can Chi</i> của phần Bát Tự.</p>`), refs: ['Phu Thê', 'Tử Tức', 'Huynh Đệ', 'Phụ Mẫu', 'Nô Bộc'] },
    { id: 'dai-van', title: 'Đại Vận', lead: `Đại vận ${esc(b.luck_direction)}, khởi vận khoảng ${b.luck_start.years} năm ${b.luck_start.months} tháng; đại hạn Tử Vi chạy ${esc(t.dai_han_direction)}.`,
      calc: calc(`<h5>Đại hạn Tử Vi</h5>${tv.timelineHtml}<h5>Lưu niên</h5><div id="rp-year"></div>`), trad: notice('Không có diễn giải truyền thống cho phần này', 'Hệ thống chỉ trình bày cấu trúc thời gian; việc luận từng giai đoạn cần quy tắc đã xác minh.') },
    { id: 'cach-cuc', title: 'Cách Cục', lead: 'Các hình thái đặc biệt mà bộ quy tắc hiện hành có thể nhận ra.',
      calc: calc(`<p>Bát Tự: chưa có quy tắc cách cục đã xác minh. Các nhận định về cách cục bên dưới: ${fsFor('cach-cuc').length || 'không có'}.</p>`),
      trad: (() => { const fs = fsFor('cach-cuc'); return `<div class="ch-trad"><p class="eyebrow">Diễn giải truyền thống</p>${fs.length ? `<button type="button" class="btn btn-ghost btn-sm" id="ig-toggle" aria-pressed="false">Xem đồ thị suy luận</button><div id="ig-box" hidden>${inferenceGraph(fs[0])}<p class="muted small">Ví dụ cho nhận định đầu tiên: dữ kiện và nguồn dẫn tới quy tắc, quy tắc dẫn tới nhận định.</p></div>${fs.map(f => findingCard(f, where(f))).join('')}` : notice('Không có cách cục nào được nhận ra', '')}</div>`; })() },
    { id: 'chuyen-sau', leftover: true, title: 'Luận giải chuyên sâu', lead: 'Văn bản do bộ máy sinh tự động từ các nhận định, kèm quy tắc chờ dữ kiện và vết tính toán.',
      calc: `<div class="ch-calc"><p class="eyebrow">Dành cho người muốn kiểm chứng</p>
        ${['tu_vi', 'bat_tu'].map(s => { const d = reason.systems[s]; return acc(s === 'tu_vi' ? 'Văn bản luận giải — Tử Vi' : 'Văn bản luận giải — Bát Tự', `${d.findings.length} nhận định · ${d.pending.length} quy tắc chờ dữ kiện`, `<pre class="prose-pre">${esc(d.text)}</pre>${d.pending.length ? `<h5>Quy tắc chưa đủ dữ kiện</h5><ul>${d.pending.map(p => `<li>${esc(p.rule)} <span class="muted">@${esc(p.subject)} · thiếu ${esc(p.missing_facts.join(', '))}</span></li>`).join('')}</ul>` : ''}`); }).join('')}
        ${acc('Vết tính toán (CalculationTrace)', 'từng bước chuẩn hóa và lập lá số', `<pre id="trace" class="trace">${esc(JSON.stringify({ normalization: ctx.chartRaw.normalization_trace.steps, bazi: b.trace.steps, tuvi: t.trace.steps }, null, 1))}</pre>`)}
        ${reason.pack_problems.length ? notice('Vấn đề trong bộ quy tắc', esc(reason.pack_problems.join('; ')), 'warn') : ''}</div>` },
  ];

  host.innerHTML = `<div class="rp-layout">
    <nav class="rp-toc" aria-label="Mục lục luận giải"><ol>${chapters.map((c, i) => `<li><a href="#ch-${c.id}" data-ch="${c.id}"><span>${pad(i + 1)}</span>${c.title}</a></li>`).join('')}</ol></nav>
    <div class="rp-body">${chapters.map((c, i) => {
      const fs = fsFor(c.id);
      return `<article class="chapter" id="ch-${c.id}"><header><span class="ch-no">${pad(i + 1)}</span><h3>${c.title}</h3></header><p class="lead">${c.lead}</p>${c.calc || ''}${c.leftover ? (fs.length ? trad(fs) : '') : c.trad && typeof c.trad === 'string' && c.trad.startsWith('<div class="ch-trad">') ? c.trad : c.trad ? `<div class="ch-trad"><p class="eyebrow">Diễn giải truyền thống</p>${c.trad}</div>` : trad(fs)}</article>`;
    }).join('')}</div></div>`;

  yearExplorer($('#rp-year', host), ctx.req, b);
  $$('.ref', host).forEach(r => r.onclick = () => ctx.openPalace(r.dataset.palace));
  const tg = $('#ig-toggle', host); if (tg) tg.onclick = () => { const on = tg.getAttribute('aria-pressed') !== 'true'; tg.setAttribute('aria-pressed', on); $('#ig-box', host).hidden = !on; tg.textContent = on ? 'Ẩn đồ thị suy luận' : 'Xem đồ thị suy luận'; };
  // TOC highlight
  const links = $$('.rp-toc a', host);
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) links.forEach(l => l.classList.toggle('on', l.dataset.ch === e.target.id.slice(3))); }), { rootMargin: '-30% 0px -60% 0px' });
  $$('.chapter', host).forEach(c => io.observe(c));
  links.forEach(l => l.onclick = e => { e.preventDefault(); $(l.getAttribute('href'), host).scrollIntoView({ behavior: 'smooth', block: 'start' }); });
}
