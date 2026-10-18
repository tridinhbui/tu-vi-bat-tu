// Beginner layer: plain-language summary, softened/filtered readings, and "no dead end" empty states.
// Nothing here creates conclusions: every statement is either a fact from the chart, an educational primer, or a verified finding
// (basis === 'verified') re-worded from the engine's own phrase. Draft rules stay in the 'Chuyên sâu' mode.
import { esc, STEMS, BRANCHES, EL, ELEMENTS, claimPhrase, claimKnown, palaceOfSubject } from './util.js';
import { currentPhase, elementStats } from './insights.js';
import { lessonTitle } from './learn.js';

// Phrases that describe a hard or one-sided trait: kept out of the headline summary and tucked into a clearly-labelled fold.
const CARE = /khó|nghèo|thất bại|phiêu bạt|mất mát|hao tâm|hao hụt|ganh|cao ngạo|tự cao|kiêu căng|tranh cãi|tranh giành|bất hòa|xa cách|ngậm ngùi|liều|vất vả|thiếu tình nghĩa|nóng|thờ ơ|thay đổi|phóng đãng|tật|bệnh|chết|yểu|cô độc|ly |sát tinh/i;

const cap = t => t ? t[0].toUpperCase() + t.slice(1) : t;
/** Splits an engine phrase into { core, basis, note }: "khuynh hướng X (căn cứ); ghi chú" */
export function parsePhrase(f) {
  const raw = claimPhrase(f.claim, f.effect);
  const [main, ...rest] = raw.split(/;\s+/);
  const m = main.match(/^(.*?)\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$/);
  return { core: (m ? m[1] : main).trim(), basis: m ? m[2] : '', note: rest.join('; ') };
}

export function classify(findings) {
  const out = { show: [], care: [], draft: [] };
  findings.forEach(f => {
    if (f.basis !== 'verified') out.draft.push(f);
    else if (!claimKnown(f.claim)) return; // no Vietnamese phrase loaded: never show a raw id to beginners
    else if (f.status === 'supported' && f.effect !== 'limit') (CARE.test(parsePhrase(f).core) ? out.care : out.show).push(f);
  });
  return out;
}

export const easyCard = f => {
  const p = parsePhrase(f);
  return `<div class="ez-card"><p class="ez-t">${esc(cap(p.core))}</p>${p.basis ? `<p class="ez-b">Căn cứ trên lá số: ${esc(p.basis)}</p>` : ''}${p.note ? `<p class="ez-b">${esc(cap(p.note))}</p>` : ''}<span class="ez-tag">Theo sách đã đối chiếu</span></div>`;
};

const CARE_INTRO = 'Những mô tả dưới đây nêu mặt cần để ý của một tổ hợp sao hoặc chữ. Chúng đến từ sách cổ, thường còn tùy các yếu tố đi kèm, và có thể trái chiều với các nhận định khác. Hãy xem như một góc nhìn để suy ngẫm, không phải kết luận về con người bạn.';

/** Traditional-reading block for 'Dễ hiểu' mode: verified only, hard traits folded, drafts counted but not shown. */
export function easyReadings(fs, { empty = '', where = () => '' } = {}) {
  const c = classify(fs);
  const body = [
    c.show.map(f => easyCard(f).replace('<span class="ez-tag">', `<span class="ez-tag">${where(f) ? where(f) + ' · ' : ''}`)).join(''),
    c.care.length ? `<details class="ez-care"><summary>Điểm cần cân nhắc <span class="muted">(${c.care.length})</span></summary><p class="muted small">${CARE_INTRO}</p>${c.care.map(easyCard).join('')}</details>` : '',
  ].join('');
  return c.show.length || c.care.length ? body : `${empty}${body}`;
}

// ---- educational primers (shown instead of "no rule fired") ----
const PRIMER = {
  'bt:su-nghiep': 'Trong Bát Tự, công việc và tiền bạc thường được xem qua hai nhóm Thập Thần: Quan Sát (khuôn khổ, vị trí, trách nhiệm) và Tài (tiền bạc, cơ hội). Người ta xem chúng nằm ở đâu, nhiều hay ít, và Nhật Chủ có đủ sức “gánh” chúng hay không.',
  'bt:quan-he': 'Bạn đời trong Bát Tự thường được xem qua Địa chi của trụ Ngày (gọi là cung bạn đời) và các quan hệ hợp, xung giữa trụ Ngày với các trụ khác. Hợp hay xung chỉ cho biết “có tương tác”, tự nó chưa nói tốt hay xấu.',
  'bt:cach-cuc': 'Cách cục là cách phân loại “mẫu hình” của một lá số, dựa chủ yếu vào tháng sinh và Thập Thần nổi bật. Dụng thần là hành giúp lá số cân bằng hơn. Cả hai phụ thuộc trường phái và cần nhiều bước cân nhắc, nên người mới chưa cần vội quan tâm.',
  'tv:ban-menh': 'Bản mệnh là tên hình tượng theo năm sinh (ví dụ “Lộ Bàng Thổ”). Người ta so hành của bản mệnh với hành của Cục để xem hai hành này sinh, khắc hay cùng nhau.',
  'tv:tinh-cach': 'Tính cách trong Tử Vi được xem chủ yếu qua cung Mệnh (con người bạn) và cung Phúc Đức (đời sống tinh thần). Hãy nhìn chính tinh, độ sáng của chúng và các sao đi cùng.',
  'tv:cong-danh': 'Công danh được xem qua cung Quan Lộc (công việc, địa vị) cùng cung đối diện Thiên Di (môi trường bên ngoài). Chính tinh ở đó cho biết “phong cách làm việc”.',
  'tv:tai-bach': 'Tiền bạc được xem qua cung Tài Bạch (dòng thu nhập) và cung Điền Trạch (của cải tích lũy, nhà đất). Hai cung này trả lời hai câu hỏi khác nhau: kiếm được thế nào, và giữ lại được gì.',
  'tv:quan-he': 'Các mối quan hệ được xem qua nhiều cung: Phu Thê (bạn đời), Tử Tức (con cái), Huynh Đệ (anh chị em), Phụ Mẫu (cha mẹ) và Nô Bộc (bạn bè, đồng nghiệp).',
  'tv:cach-cuc': 'Cách cục là những “tổ hợp sao” đặc biệt mà sách cổ đặt tên riêng. Hệ thống chỉ nêu khi tìm thấy đúng tổ hợp; không thấy nghĩa là lá số này không có tổ hợp nào trong danh sách đang hỗ trợ.',
};
const LEARN_FOR = { 'bt': 'bt-3', 'tv': 'tv-4' };

export function emptyReading(topic, T, { palace = null, brief = false } = {}) {
  const prim = palace ? `${esc(T['palace:' + palace]?.plain || '')} ${esc(T['palace:' + palace]?.ex || '')}` : esc(PRIMER[topic] || '');
  const less = LEARN_FOR[topic?.slice(0, 2)] || 'tv-2';
  return `<div class="ez-empty">${brief ? '' : `<p class="eyebrow">Kiến thức nền</p><p>${prim}</p>`}
    <p class="muted small">Hệ thống <b>chưa có luận giải cá nhân hóa</b> cho phần này của lá số bạn (chưa có nhận định nào đã đối chiếu sách khớp với phần này), nên chỉ cung cấp kiến thức nền và các dữ kiện đã tính. Điều đó không có nghĩa phần này “không có gì”.</p>
    <p><button type="button" class="link" data-lesson="${palace ? 'tv-2' : less}">Đọc bài: ${esc(lessonTitle(palace ? 'tv-2' : less))} →</button></p></div>`;
}

// ---- "năm nay của bạn": a plain-language view of the already-computed year data (lưu niên / tiểu hạn / lưu Tứ Hóa) ----
const REL_PLAIN = { 'can_hợp': 'hợp (kéo về nhau)', 'can_xung': 'xung (đối nhau)', 'chi_lục hợp': 'lục hợp (kéo về nhau)', 'chi_xung': 'xung (đối nhau)', 'chi_hại': 'hại', 'chi_phá': 'phá', 'chi_hình': 'hình', 'chi_tam_hợp': 'tam hợp', 'chi_tam_hội': 'tam hội' };
const PILLAR = { year: 'trụ Năm', month: 'trụ Tháng', day: 'trụ Ngày', hour: 'trụ Giờ' };
const firstSentence = s => (s || '').split(/(?<=\.)\s/)[0];
export function yearCard(d, T, sys, { atStart = false, atEnd = false } = {}) {
  const b = d.bazi, t = d.tuvi;
  const bar = `<div class="by-bar"><button type="button" class="btn btn-ghost btn-sm" data-yd="-1" aria-label="Năm trước"${atStart ? ' disabled' : ''}>‹</button><span><b>Năm ${d.bazi.year}</b> <span class="muted">· tuổi mụ ${t.age_tuoi_mu}</span></span><button type="button" class="btn btn-ghost btn-sm" data-yd="1" aria-label="Năm sau"${atEnd ? ' disabled' : ''}>›</button></div>`;
  let body;
  if (sys === 'bt') {
    const inter = [...b.annual_vs_natal].map(x => `${esc(PILLAR[x.with] || x.with)} ${esc(REL_PLAIN[x.kind] || x.kind.replace(/_/g, ' '))}`);
    const god = T['god:' + b.annual_stem_ten_god]?.plain;
    body = `<p>Năm này là năm <b>${esc(b.annual_pillar)}</b>. Đặt cạnh Nhật Chủ của bạn, Thiên can của năm đóng vai <b>${esc(b.annual_stem_ten_god)}</b>${god ? `: ${esc(firstSentence(god))}` : '.'}</p>
      <p>${inter.length ? `Năm nay “chạm” vào lá số gốc ở: ${inter.join('; ')}. Đây chỉ cho biết có tương tác giữa các chữ.` : 'Năm nay không có tương tác đáng kể với bốn trụ gốc.'}</p>
      <p class="muted small">Đại vận hiện tại: ${esc(b.luck_pillar || 'chưa khởi')}${b.luck_stem_ten_god ? ` (${esc(b.luck_stem_ten_god)})` : ''}.</p>`;
  } else {
    const hoa = Object.entries(t.luu_tu_hoa).map(([k, v]) => `<li><b>${esc(k)}</b> ở ${esc(v.star)} (cung ${esc(v.natal_palace)}): ${esc(firstSentence(T[{ 'Hóa Lộc': 'c:hoa-loc', 'Hóa Quyền': 'c:hoa-quyen', 'Hóa Khoa': 'c:hoa-khoa', 'Hóa Kỵ': 'c:hoa-ky' }[k]]?.plain).replace(/^Nhãn '[^']*' gắn vào một sao: /, ''))}</li>`).join('');
    body = `<p>Tiểu hạn năm nay ở <b>cung ${esc(t.tieu_han_palace)}</b>, nên chủ đề <b>${esc(t.tieu_han_topic || '')}</b> thường được “bật sáng”. ${esc(firstSentence(T['palace:' + t.tieu_han_palace]?.plain))}</p>
      <p>Chặng 10 năm hiện tại: ${t.dai_han ? `đại hạn cung <b>${esc(t.dai_han.palace)}</b> (${t.dai_han.age_from}–${t.dai_han.age_to} tuổi).` : 'chưa vào đại hạn đầu.'}</p>
      <p class="by-h">Bốn nhãn Tứ Hóa của năm</p><ul class="by-hoa">${hoa}</ul>`;
  }
  return `<h3>Năm nay của bạn</h3>${bar}<div class="by-body">${body}</div><p class="muted small">Đây là những chủ đề được “bật sáng” theo biểu tượng truyền thống, không phải dự đoán sự kiện sẽ xảy ra.</p>`;
}

// ---- summary card ----
const li = t => `<li>${t}</li>`;
const plainElem = (b) => {
  const { vis, hid } = elementStats(b), by = ELEMENTS.map(e => [e, vis[e]]).sort((a, c) => c[1] - a[1]);
  const top = by.filter(x => x[1] === by[0][1]).map(x => x[0]), none = ELEMENTS.filter(e => !vis[e]), noneAll = none.filter(e => !hid[e]);
  return `Trên tám chữ, hành nhiều nhất là <b>${top.join(', ')}</b> (${by[0][1]}/8 chữ)${none.length ? `; hành <b>${none.join(', ')}</b> không xuất hiện${noneAll.length ? '' : ' (nhưng có ẩn trong tàng can)'}` : ''}.`;
};
const sortKeys = (fs) => { // spread across palaces/themes so one topic does not dominate
  const seen = new Set(), out = [];
  fs.forEach(f => { const k = palaceOfSubject(f.subject) || 'chart'; if (!seen.has(k)) { seen.add(k); out.push(f); } });
  fs.forEach(f => { if (!out.includes(f)) out.push(f); });
  return out;
};
const next = (items) => `<h3>Nên khám phá tiếp</h3><div class="bs-next">${items.map(([id, txt]) => `<button type="button" class="btn btn-ghost btn-sm" data-lesson="${id}">${esc(txt)}</button>`).join('')}</div>`;
const limits = items => `<h3>Giới hạn của bản luận giải này</h3><ul class="bs-lim">${items.map(li).join('')}</ul>`;
const findingsBlock = (fs, T) => {
  const c = classify(fs), top = sortKeys(c.show).slice(0, 4);
  return { c, html: `<h3>Điều hệ thống có căn cứ để nói</h3>${top.length ? `<div class="ez-list">${top.map(easyCard).join('')}</div>` : `<div class="ez-empty"><p>Hệ thống chưa có nhận định nào đã đối chiếu sách cho lá số này, nên bản tóm tắt chỉ dựa vào các dữ kiện đã tính ở trên. Bạn vẫn có thể bấm vào từng sao, cung, chữ để hiểu ý nghĩa của chúng.</p></div>`}
    <p class="muted small">Chỉ hiển thị nhận định từ quy tắc đã đối chiếu sách. ${c.care.length ? `Còn ${c.care.length} mô tả thiên về mặt cần để ý được xếp vào mục “Điểm cần cân nhắc” ở các chương bên dưới. ` : ''}Các nhận định đến từ nhiều sách, nhiều cung nên có thể trái chiều; đó là bình thường.</p>` };
};

export function summaryBazi(chart, ctx, T, counts) {
  const b = chart.bazi, t = chart.tuvi, dm = STEMS[b.pillars.day.stem], mb = BRANCHES[b.pillars.month.branch], ph = currentPhase(b, t, ctx.req);
  const fs = (ctx.reason.systems.bat_tu?.findings || []);
  const { c, html } = findingsBlock(fs, T);
  const gaps = ['Chưa kết luận Thân vượng hay nhược, Cách cục và Dụng thần, vì sách không đưa ngưỡng tính cụ thể.'];
  gaps.push('Sự nghiệp, tài lộc và hôn nhân: hiện chỉ có kiến thức nền và dữ kiện, chưa có luận giải cá nhân hóa.');
  gaps.push('Mọi thông tin theo năm, theo đại vận là dữ kiện cấu trúc, không phải dự đoán sự kiện.');
  return `<section class="bs" aria-labelledby="bs-bt-h"><p class="eyebrow">Tóm tắt cho người mới · Bát Tự</p><h2 id="bs-bt-h">Lá số Bát Tự của bạn trong một phút</h2>
    <p class="sec-sub">Bát Tự đọc tám chữ (bốn trụ) từ năm, tháng, ngày, giờ sinh. Dưới đây là những điều cơ bản nhất, giải thích bằng lời thường. Từ gạch chân nào cũng bấm được.</p>
    <div class="bs-grid">
      <div class="bs-c"><span class="k">Bạn được đại diện bởi</span><b>${esc(dm.n)} ${dm.e}</b><p>${esc(T['can:' + dm.n]?.plain || '')} Chữ này gọi là Nhật Chủ.</p></div>
      <div class="bs-c"><span class="k">Cân bằng năng lượng</span><b>Ngũ Hành</b><p>${plainElem(b)}</p></div>
      <div class="bs-c"><span class="k">Mùa bạn sinh ra</span><b>Tháng ${esc(mb.n)} (${mb.e})</b><p>Tháng sinh được lấy theo tiết khí và cho biết “mùa” của lá số. Mùa này thuộc hành ${mb.e}, nên hành đó có thế mạnh hơn trong lá số.</p></div>
      <div class="bs-c"><span class="k">Chặng 10 năm đang đi</span><b>${ph.luck ? `Đại vận ${esc(ph.luck.name)}` : 'Chưa khởi vận'}</b><p>${ph.luck ? `Năm ${ph.now} bạn khoảng ${ph.age} tuổi mụ. Chặng này mang vai <b>${esc(ph.luck.ten_god)}</b> đối với Nhật Chủ.` : 'Đại vận đầu tiên chưa bắt đầu.'}</p></div>
    </div><div class="bs-year" data-sys="bt"></div>${html}${limits(gaps)}
    ${next([['bt-1', 'Bát Tự là gì?'], ['bt-3', 'Thập Thần là gì?'], ['bt-2', 'Can Chi và Ngũ Hành']])}</section>`;
}

export function summaryTuvi(chart, ctx, T) {
  const t = chart.tuvi, b = chart.bazi, menh = t.palaces.find(p => p.name === 'Mệnh'), than = t.palaces.find(p => p.is_than), ph = currentPhase(b, t, ctx.req);
  const fs = (ctx.reason.systems.tu_vi?.findings || []);
  const { c, html } = findingsBlock(fs, T);
  const covered = new Set(c.show.concat(c.care).map(f => palaceOfSubject(f.subject)).filter(Boolean));
  const uncovered = t.palaces.filter(p => !covered.has(p.name)).length;
  const star = menh.major_stars[0], dg = star && menh.major_dignity?.[star];
  const hoa = Object.entries(t.tu_hoa).map(([k, v]) => `${k} (${v.star}) ở cung ${t.palaces.find(p => p.branch_index === v.branch)?.name}`);
  const gaps = [
    `Có ${uncovered}/12 cung chưa có luận giải cá nhân hóa; với các cung này chỉ có kiến thức nền và dữ kiện sao.`,
    'Một sao “hãm” chỉ là sao ở vị trí yếu, chưa nói được điều gì xấu; cần xem thêm sao đi cùng, Tuần/Triệt và vận hạn.',
    'Lưu nguyệt Tử Vi chưa được hỗ trợ vì chưa có nguồn xác minh; thông tin theo năm là dữ kiện cấu trúc, không phải dự đoán.',
  ];
  return `<section class="bs" aria-labelledby="bs-tv-h"><p class="eyebrow">Tóm tắt cho người mới · Tử Vi</p><h2 id="bs-tv-h">Lá số Tử Vi của bạn trong một phút</h2>
    <p class="sec-sub">Tử Vi là bản đồ mười hai cung, mỗi cung một lĩnh vực đời sống, trên đó đặt các sao. Hãy bắt đầu từ cung Mệnh (chính bạn). Từ gạch chân nào cũng bấm được.</p>
    <div class="bs-grid">
      <div class="bs-c"><span class="k">Cung Mệnh: con người bạn</span><b>${esc(menh.stem)} ${esc(menh.branch)}</b><p>${menh.major_stars.length ? `Chính tinh: <b>${esc(menh.major_stars.map(s => s + (menh.major_dignity?.[s] ? ` (${menh.major_dignity[s]})` : '')).join(', '))}</b>. ${esc(T['star:' + star]?.plain || '')}${dg ? ` Độ sáng “${esc(dg)}” cho biết sao này ở vị trí ${esc({ miếu: 'rất thuận', vượng: 'khá thuận', đắc: 'tạm thuận', bình: 'bình thường', hãm: 'yếu' }[dg] || dg)}.` : ''}` : 'Cung Mệnh vô chính diệu (không có chính tinh): người ta mượn sao của cung đối diện để đọc.'}</p></div>
      <div class="bs-c"><span class="k">Cung Thân</span><b>${esc(than.name)}</b><p>${esc(T['palace:' + than.name]?.plain || '')} Cung Thân thường được xem là lĩnh vực bạn dồn nhiều tâm sức về nửa đời sau.</p></div>
      <div class="bs-c"><span class="k">Cục và bản mệnh</span><b>${esc(t.cuc.name)} · ${esc(t.menh_nap_am)}</b><p>Cục dùng để xếp các sao và tính tuổi bắt đầu đại hạn (ở đây tuổi ${t.dai_han[0].age_from}); bản mệnh là tên hình tượng theo năm sinh, thuộc hành ${esc(t.menh_element)}. Quan hệ giữa hai hành: ${esc(t.menh_cuc_relation)}.</p></div>
      <div class="bs-c"><span class="k">Chặng 10 năm đang đi</span><b>${ph.dh ? `Đại hạn cung ${esc(ph.dh.palace)}` : 'Chưa vào đại hạn'}</b><p>${ph.dh ? `${ph.dh.age_from}–${ph.dh.age_to} tuổi. ${esc(T['palace:' + ph.dh.palace]?.plain || '')} Chủ đề này thường được “bật sáng” trong chặng hiện tại.` : ''}</p></div>
    </div>
    <p class="bs-hoa"><b>Tứ Hóa theo năm sinh:</b> ${esc(hoa.join(' · '))}. <span class="muted">Mỗi nhãn làm nổi bật một mặt của sao đó, không phải điều tốt hay xấu tự thân.</span></p>
    <div class="bs-year" data-sys="tv"></div>${html}${limits(gaps)}
    ${next([['tv-1', 'Tử Vi là gì?'], ['tv-4', 'Cách đọc lá số trong 5 bước'], ['tv-3', 'Các sao và độ sáng']])}</section>`;
}
