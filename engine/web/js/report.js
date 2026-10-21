// InterpretationSection chapters: calculations and traditional readings kept visibly separate.
import { $, $$, esc, bd, DM, STEMS, BRANCHES, EL, starKind, tenGodGroup, TEN_GOD_GROUPS, palaceOfSubject, claimLabel, elChip, CLAIMS } from './util.js';
import { acc, notice, reasoningPanel, timeline, yearExplorer, findingList } from './ui.js';
import { scopePanelBazi } from './scope.js';
import { easyReadings, emptyReading, classify, parsePhrase } from './beginner.js';
import { autoLink, terms } from './glossary.js';
import { lockHtml } from './paywall.js';
import { elementBalanceHtml, godDistributionHtml, menhTamPhuongHtml, currentPhase, currentPhaseHtml } from './insights.js';
import { HANH, MAJOR_SIGN, hk } from './stars_hanh.js';
import { orderChapters, focusIds, focusNote } from './focus.js';

const LAYER_HINT = { 'Tượng': 'ý nghĩa biểu tượng', 'Khí': 'điều kiện mạnh yếu', 'Thế': 'vị trí trong cấu trúc', 'Cách': 'cách cục', 'Dụng': 'vai trò theo lĩnh vực', 'Biến': 'biến đổi theo thời gian', 'Phản': 'yếu tố đối trọng', 'Tổng': 'tổng hợp' };
const BASIS = { tinh_toan: ['Tính toán', 'dữ kiện lập từ lá số'], sach: ['Theo sách', 'có trích dẫn trang'], he_thong: ['Định nghĩa của hệ thống', 'cách hệ thống chọn để mô tả; không phải lời sách'] };
function analysisHtml(blocks) {
  if (!blocks?.length) return '';
  return `<div class="ch-an pro-only"><p class="eyebrow">Phân tích cấu trúc</p>${blocks.map(b => `<p class="an-p"><span class="an-tag" title="${esc(LAYER_HINT[b.layer] || '')}">${esc(b.layer)}</span>${esc(b.text)}<span class="an-meta"><span class="an-b an-${b.basis}" title="${esc(BASIS[b.basis][1])}">${BASIS[b.basis][0]}</span>${(b.src || []).map(x => `<span class="an-src">${esc(x)}</span>`).join('')}</span></p>`).join('')}</div>`;
}
// ---------- 'Luận giải tổng hợp' (tvbt/synthesis): composed section at the top of a chapter, evidence list stays below ----------
const SY_BASIS = { sach: ['Theo sách', 'nội dung là nhận định của sách, có quy tắc truy vết'], dieu_kien: ['Theo điều kiện', 'giải thích quan hệ giữa điều kiện của các nhận định (chung – riêng, cùng đúng, khác sách)'],
  he_thong: ['Khung của hệ thống', 'cách hệ thống nối hoặc tóm tắt các nhận định; không phải lời sách'], tinh_toan: ['Dữ kiện', 'vị trí sao tính từ lá số, chưa diễn giải'] };
function synthHtml(ch) {
  if (!ch || !ch.paragraphs?.length) return '';
  const para = p => `<p class="sy-p sy-${p.role}">${p.sentences.map(s => `<span class="sy-s sy-b-${s.basis}${s.kind === 'reflection' ? ' sy-refl' : ''}"${s.provenance?.length ? ` data-rules="${esc(s.provenance.join(', '))}" data-basis="${s.basis}" tabindex="0" role="button"` : ''}>${esc(s.text)}</span>`).join(' ')}</p>`;
  const themes = ch.themes || [];
  const P = x => `<b>${esc(x.concept)}</b> <span class="muted">@${esc(x.palace)} · ${esc(x.rules.join(', '))}</span>`;
  const graph = themes.length ? `<ol class="sy-graph">${themes.map(t => `<li><span class="k">${esc(t.name)}</span> · ưu tiên ${t.salience} <span class="muted">(thứ tự trình bày, không phải xác suất)</span><ul>
      <li>Trọng tâm: ${P(t.main)}</li>${t.supports.map(x => `<li>Củng cố: ${P(x.prop)}${x.edge ? ` <span class="muted">— ${esc(x.edge.type)}${x.edge.frame ? ' / ' + esc(x.edge.frame) : ''}</span>` : ''}</li>`).join('')}
      ${t.counters.map(x => `<li>Đối trọng: ${P(x.prop)}${x.edge ? ` <span class="muted">— ${esc(x.edge.type)}${x.edge.resolution ? ': ' + esc(x.edge.resolution) : ''}${x.edge.frame ? ' / ' + esc(x.edge.frame) : ''} · ${esc(x.edge.basis)}</span>` : ''}</li>`).join('')}
      ${t.conditions.map(e => `<li>Điều kiện: ${esc(e.a)} → ${esc(e.b)} <span class="muted">(${esc(e.type)})</span></li>`).join('')}</ul></li>`).join('')}</ol>` : '<p class="muted small">Chương này không dựng đồ thị chủ đề (chỉ dữ kiện và lời sách theo vị trí).</p>';
  const v = ch.validation || { issues: [], metrics: {} }, m = v.metrics || {};
  const check = `<p class="small">${m.sentences || 0} câu · ${m.distinct_openers || 0} cách mở câu khác nhau · theo nguồn: ${Object.entries(m.by_basis || {}).map(([k, n]) => `${SY_BASIS[k]?.[0] || k} ${n}`).join(', ')}</p>${v.issues.length ? `<ul class="small">${v.issues.map(i => `<li>${esc(i.type)}${i.text ? ': ' + esc(i.text.slice(0, 120)) : ''}</li>`).join('')}</ul><p class="muted small">Các câu vi phạm đã bị lược bỏ khỏi văn bản thay vì viết mạnh hơn bằng chứng.</p>` : '<p class="muted small">Không có câu nào bị loại: mọi câu nội dung đều có truy vết, không có câu lặp hay từ ngữ phán quyết.</p>'}`;
  return `<section class="synth" aria-label="Luận giải tổng hợp"><p class="eyebrow">Luận giải tổng hợp</p>${ch.paragraphs.map(para).join('')}
    <div class="sy-why small" hidden></div>
    <div class="pro-only sy-legend small">${Object.entries(SY_BASIS).map(([k, [t, d]]) => `<span class="sy-chip sy-b-${k}" title="${esc(d)}">${t}</span>`).join('')}<span class="muted">Nhấn vào một câu để xem quy tắc sinh ra nó.</span></div>
    <div class="pro-only">${themes.length ? acc('Đồ thị lập luận', `${themes.length} chủ đề`, graph) : ''}${acc('Kiểm tra văn bản', v.issues.length ? `${v.issues.length} câu bị loại` : 'đạt', check)}</div>
    <p class="muted small sy-foot">Phần này được tổng hợp tự động từ các nhận định đã đối chiếu sách bên dưới, bằng quy tắc ngôn ngữ cố định (không dùng mô hình AI). Đây là cách đọc theo hệ biểu tượng truyền thống, không phải dự báo.</p></section>`;
}
// ---------- evidence engine (tvbt/reasoning/interpretation.py, server flag): six fixed sections per chapter, each item traced to rules and pages ----------
const EV_SECTIONS = [['nhan_dinh_tong_quan', 'Nhận định tổng quan'], ['co_so_luan_giai', 'Cơ sở luận giải'], ['yeu_to_ho_tro', 'Yếu tố hỗ trợ'],
  ['han_che_mau_thuan', 'Điểm hạn chế và mâu thuẫn'], ['luan_giai_tong_hop', 'Luận giải tổng hợp'], ['dieu_kien_gioi_han', 'Điều kiện và giới hạn']];
const EV_CH = { 'ban-menh': ['menh'], 'tinh-cach': ['tinh_cach'], 'cong-danh': ['cong_danh'], 'tai-bach': ['tai_loc'], 'quan-he': ['quan_he', 'tat_ach'], 'dai-han': ['van_han'] };
function evHtml(chs) {
  chs = (chs || []).filter(Boolean);
  if (!chs.length) return '';
  const li = x => typeof x === 'string' ? `<li>${esc(x)}</li>` : `<li>${esc(x.text)}${x.sources?.length ? ` <span class="src-chip">${esc(x.sources.join('; '))}</span>` : ''}</li>`;
  const list = xs => xs?.length ? `<ul class="yx-list">${xs.map(li).join('')}</ul>` : '<p class="muted small">Không có.</p>';
  const sec = (k, v) => typeof v === 'string' ? `<p>${esc(v)}</p>` : Array.isArray(v) ? list(v)
    : list([...(v.items || []), ...(v.relations || []), ...(v.conditions || []), ...(v.open_questions || []).map(q => 'Câu hỏi mở: ' + q), ...(v.guards || []),
      ...(v.structural_labels || []).map(x => 'Nhận diện cấu trúc: ' + x.text)]);
  return chs.map(ch => `<section class="synth ev-report" aria-label="${esc(ch.title)}"><p class="eyebrow">Luận giải có căn cứ · ${esc(ch.title)} <span class="muted">(thử nghiệm)</span></p>
    ${EV_SECTIONS.map(([k, t]) => ch.sections[k] == null ? '' : (k === 'nhan_dinh_tong_quan' ? `<h5>${t}</h5>${sec(k, ch.sections[k])}` : acc(t, '', sec(k, ch.sections[k])))).join('')}</section>`).join('');
}
// ---------- reader prose for Mệnh (src/interpret/prose via /api/interpret mode "prose"): clean text, evidence per sentence on click ----------
const PR_MOVE = { STRUCT: 'Cấu trúc cung', PHO_THONG: 'Nghĩa phổ thông', BALANCE: 'Cân bằng và hướng đi', ANCHOR: 'Nét lõi', BORROW: 'Nét lõi, mượn cung đối diện', ELABORATE: 'Biểu hiện', TURN: 'Mặt trái', RESCUE: 'Cứu giải', TENSION: 'Yếu tố làm sắc',
  TIMING: 'Nhịp thời gian', SATELLITE: 'Nét bổ trợ', VALUE: 'Giá trị', TRANSFORM: 'Hướng chuyển hóa', DEGREE: 'Nền độ số', EXTRA: 'Đường đời' };
const PR_BOOK = { TH: 'Thực Hành', KL: 'Khảo Luận', TT: 'Toàn Thư', TL: 'Nghiệm Lý (Thiên Lương, bản gõ)', NL: 'Nghiệm Lý 1974 (Thiên Lương, bản scan HELEN)', ZZ: 'Bát Tự Chân Tông' };
const prCite = c => String(c).replace(/^(TH|KL|TT|TL|NL|ZZ)\s*(?:PDF\s*)?pp?\.\s*/, (_, b) => `${PR_BOOK[b] || b} tr.`);
// star names in reader prose take the board's ngũ hành colour (stars_hanh.js, a display convention) and the chính tinh are bold, as on the
// board; "Phúc Đức" is left alone (it is also the palace's name)
const PR_STARS = Object.keys(HANH).filter(n => n !== 'Phúc Đức').sort((a, b) => b.length - a.length);
const PR_STAR_RE = new RegExp(`(?<![\\p{L}])(${PR_STARS.join('|')})(?![\\p{L}])`, 'gu');
const starsHtml = t => esc(t).replace(PR_STAR_RE, n => `<span class="pr-star h-${hk(HANH[n])}${MAJOR_SIGN[n] ? ' pr-maj' : ''}">${n}</span>`);
/** a sentence: its bold lead-in when the paragraph has one (luận cung, prose/luan.ts), the rest with coloured star names */
const prSentence = (s, lead) => lead && s.text.startsWith(lead) ? `<strong class="pr-lead">${starsHtml(lead)}</strong>${starsHtml(s.text.slice(lead.length))}` : starsHtml(s.text);
/** the dignity table the chart was computed with (renderTuviReport sets it): the prose footer names it */
let prSchool = 'khao_luan';
const DG_NAME = { khao_luan: 'Khảo Luận', thuc_hanh: 'Thực Hành', toan_thu: 'Toàn Thư' };
const PR_FB_ICON = {
  up: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M7 10v10H4V10h3zM7 10l4-7c1.4 0 2.3 1 2 2.4L12.4 9H19a2 2 0 0 1 2 2.3l-1.2 7A2 2 0 0 1 17.8 20H7"/></svg>',
  down: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M17 14V4h3v10h-3zM17 14l-4 7c-1.4 0-2.3-1-2-2.4l.6-3.6H5a2 2 0 0 1-2-2.3l1.2-7A2 2 0 0 1 6.2 4H17"/></svg>',
  say: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5.5h16a1.5 1.5 0 0 1 1.5 1.5v9a1.5 1.5 0 0 1-1.5 1.5H10l-4.5 3.5V17.5H4A1.5 1.5 0 0 1 2.5 16V7A1.5 1.5 0 0 1 4 5.5z"/></svg>',
};
/** 👍 👎 💬 under a paragraph: sent to /api/feedback with the chapter, the paragraph's index and the prose version (bindProseFeedback) */
const prFeedback = i => `<div class="pr-fb" data-p="${i}" role="group" aria-label="Đánh giá đoạn này">
  <button type="button" class="pr-fb-b" data-v="up" aria-label="Đoạn này hữu ích" aria-pressed="false">${PR_FB_ICON.up}</button>
  <button type="button" class="pr-fb-b" data-v="down" aria-label="Đoạn này chưa ổn" aria-pressed="false">${PR_FB_ICON.down}</button>
  <button type="button" class="pr-fb-b" data-v="say" aria-label="Góp ý cho đoạn này" aria-expanded="false">${PR_FB_ICON.say}</button></div>`;
function proseHtml(p) {
  if (!p?.paragraphs?.length) return '';
  const draft = p.draft !== false;
  const title = p.title ? esc(p.title) : p.chapter === 'van_han' ? 'Luận giải các đại hạn' : String(p.chapter).startsWith('bat_tu') ? 'Luận giải Bát Tự' : `Luận giải cung ${esc(p.palace || 'Mệnh')}`;
  return `<section class="synth prose${p.luan ? ' pr-luan' : ''}${p.locked ? ' pw-cut' : ''}" data-chapter="${esc(p.chapter)}" data-engine="${esc(p.engine || '')}" aria-label="${title}"><p class="eyebrow">${title}</p>
    ${p.paragraphs.map((para, i) => `<div class="pr-block"><p class="sy-p pr-p${para.role === 'colour' ? ' pr-p-pt' : ''}${para.lead ? ' pr-p-lead' : ''}">${para.sentences.map((s, j) => `<span class="sy-s pr-s${s.trace.basis === 'pho_thong' ? ' pr-pt' : ''}" data-pr="${i}.${j}" tabindex="0" role="button" aria-expanded="false">${prSentence(s, j === 0 ? para.lead : null)}</span>`).join(' ')}</p>${prFeedback(i)}</div>`).join('')}
    <div class="pr-why small" hidden></div>${lockHtml(p)}${adviceHtml(p.advice)}${prDiverge(p)}
    <p class="muted small sy-foot">Văn bản do bộ máy ghép, không dùng mô hình AI: chỉ gồm nhận định đã đối chiếu sách, dữ kiện tính từ lá số và lời nối của hệ thống; độ sáng các sao theo bảng ${DG_NAME[prSchool] || prSchool}${prSchool !== 'thuc_hanh' ? ' (nhận định của sách Thực Hành, Toàn Thư được xét trên bảng này)' : ''}${draft ? '; thư viện câu chữ đang là bản nháp, chưa qua chuyên gia duyệt' : ''}. Nhấn vào một câu để xem căn cứ. Đây là cách đọc theo hệ biểu tượng truyền thống, không phải dự báo.</p></section>`;
}
// what the voiced traits suggest doing (chapter.ts adviceOf): strengths to lean on, habits to watch; the system's wording, said as such
function adviceHtml(a) {
  if (!a || (!a.strengths?.length && !a.actions?.length)) return '';
  const cap = t => t.charAt(0).toLocaleUpperCase('vi') + t.slice(1);
  return `<div class="pr-adv"><p class="eyebrow">Gợi ý hướng hành động</p>${a.strengths?.length ? `<p class="pr-adv-s"><b>Thế mạnh nên dựa vào:</b> ${esc(a.strengths.join(', '))}.</p>` : ''}`
    + `${a.actions?.length ? `<ul class="pr-adv-a">${a.actions.map(x => `<li>${esc(cap('nên ' + x))}.</li>`).join('')}</ul>` : ''}`
    + `<p class="muted small">Gợi ý của hệ thống, rút từ chính các nét đã nêu ở trên; không phải lời sách.</p></div>`;
}
// two schools disagree on this chart: the text says neither; both readings are listed here with their pages
function prDiverge(p) {
  const ds = p.evidence?.divergences || [], lim = p.evidence?.limits || [];
  const limits = lim.length ? `<p class="muted small">Chưa nói đến: ${lim.map(esc).join('; ')}.</p>` : '';
  if (!ds.length) return limits;
  return `<details class="pr-div small"><summary>Các trường phái nhận định khác nhau (${ds.length})</summary>${ds.map(d => `<p>${esc(d.note || '')}</p><ul class="pr-rules">${d.rules.map(r => `<li><b>${esc(r.cites.map(prCite).join('; ') || '—')}</b> ${esc(r.reading)} <code class="muted">${esc(r.id)}</code></li>`).join('')}</ul>`).join('')}<p class="muted">Văn bản phía trên không theo bên nào trong các điểm này.</p></details>${limits}`;
}
function proseWhy(p, key) {
  const [i, j] = key.split('.').map(Number), s = p.paragraphs[i]?.sentences[j];
  if (!s) return '';
  const t = s.trace, R = p.evidence?.rules || {}, C = p.evidence?.concepts || {};
  const moves = [t.move, ...(t.woven || [])].map(m => PR_MOVE[m] || m).join(' + ');
  const basis = t.basis === 'he_thong' ? '<span class="an-b an-he_thong">Lời tổng hợp của hệ thống</span> <span class="muted">không phải lời sách; chỉ nhắc lại những ý đã có căn cứ ở câu trước</span>'
    : t.basis === 'tinh_toan' ? '<span class="an-b an-tinh_toan">Tính từ lá số</span> <span class="muted">dữ kiện tính được, hoặc tra từ bảng có ghi trang sách</span>'
    : t.basis === 'pho_thong' ? '<span class="an-b an-pho_thong">Thông lệ phổ biến</span> <span class="muted">nghĩa thường dùng, do hệ thống soạn, chưa đối chiếu sách</span>'
    : '<span class="an-b an-sach">Theo sách</span>';
  const src = !t.rules.length && t.cites?.length ? `<p class="muted">Nguồn: ${esc(t.cites.map(prCite).join('; '))}</p>` : '';
  const res = t.resolution ? `<p><b>Phân xử:</b> câu sách ở ${esc(prCite(t.resolution.cite || ''))} làm mềm nhận định bất lợi đi kèm (quan hệ <code>${esc(t.resolution.relation)}</code>).</p>` : '';
  // under a rescue, the readings it softened are listed for the record but marked: the text does not voice them as they stand
  const softened = id => t.resolution && id !== t.resolution.byRule ? ' <span class="muted">· đã được câu sách trên làm mềm, văn bản không nêu nguyên ý này</span>' : '';
  const rules = t.rules.map(id => R[id] ? `<li><b>${esc(R[id].cites.map(prCite).join('; ') || '—')}</b> ${esc(R[id].reading)}${softened(id)} <code class="muted">${esc(id)}</code></li>` : `<li><code>${esc(id)}</code></li>`).join('');
  return `<p><b>${esc(moves)}</b> · ${basis}</p>${src}${t.concepts.length ? `<p class="muted">Ý được nói: ${esc(t.concepts.map(c => C[c] || c).join(', '))}</p>` : ''}${res}${rules ? `<ul class="pr-rules">${rules}</ul>` : ''}`;
}
function bindProse(host, byChapter) {
  $$('.prose', host).forEach(sec => {
    const p = byChapter[sec.dataset.chapter], box = $('.pr-why', sec);
    if (p && box) bindOne(sec, p, box);
    if (p) bindProseFeedback(sec, p);
  });
}
// Paragraph feedback goes into the visitor's feedback thread (src/feedback/route.ts, the same thread the Góp ý bubble uses: its key is
// shared through localStorage), one message per reaction, tagged so the admin page can tell which paragraph of which chapter and which
// prose version it is about. A reaction already sent from this browser is shown pressed and is not sent again.
const FB_KEY = 'tvbt.fb.key', FB_DONE = 'tvbt.prfb';
const fbStore = { get: k => { try { return localStorage.getItem(k); } catch { return null; } }, set: (k, v) => { try { localStorage.setItem(k, v); } catch { /* private mode */ } } };
async function sendProseFeedback(body) {
  const key = fbStore.get(FB_KEY);
  const r = await fetch('/api/feedback', { method: 'POST', credentials: 'same-origin', cache: 'no-store',
    headers: { 'x-tvbt': '1', 'content-type': 'application/json', ...(key ? { 'x-feedback-key': key } : {}) },
    body: JSON.stringify({ body, page: location.pathname + location.search }) });
  const j = await r.json().catch(() => ({}));
  if (j.key) fbStore.set(FB_KEY, j.key);
  if (!r.ok) throw new Error(j.detail || r.status);
}
function bindProseFeedback(sec, p) {
  const done = (() => { try { return JSON.parse(fbStore.get(FB_DONE) || '{}'); } catch { return {}; } })();
  const tag = i => `${p.chapter}#${i}@${p.engine || ''}`;
  const head = (i, v) => {
    const para = p.paragraphs[i], first = para?.sentences?.[0]?.text || '';
    return `[đoạn văn] ${v} · chương ${p.chapter} · đoạn ${i + 1}${para?.lead ? ` «${para.lead}»` : ''} · ${p.engine || ''}${p.kbVersion ? ' / ' + p.kbVersion : ''}\n${first.slice(0, 160)}`;
  };
  $$('.pr-fb', sec).forEach(row => {
    const i = Number(row.dataset.p);
    const mark = v => $$('.pr-fb-b', row).forEach(b => { if (b.dataset.v !== 'say') b.setAttribute('aria-pressed', String(b.dataset.v === v)); });
    if (done[tag(i)]) mark(done[tag(i)]);
    $$('.pr-fb-b', row).forEach(b => b.onclick = async () => {
      const v = b.dataset.v;
      if (v === 'say') {
        const open = $('.pr-fb-form', row.parentElement);
        if (open) { open.remove(); b.setAttribute('aria-expanded', 'false'); return; }
        b.setAttribute('aria-expanded', 'true');
        row.insertAdjacentHTML('afterend', `<form class="pr-fb-form"><label class="fb-sr" for="prfb-${esc(p.chapter)}-${i}">Góp ý cho đoạn này</label><textarea id="prfb-${esc(p.chapter)}-${i}" rows="2" maxlength="1500" placeholder="Đoạn này chỗ nào chưa đúng hay khó hiểu?" required></textarea><button class="btn btn-sm" type="submit">Gửi</button><span class="pr-fb-msg small muted" aria-live="polite"></span></form>`);
        const f = $('.pr-fb-form', row.parentElement), ta = $('textarea', f), msg = $('.pr-fb-msg', f);
        ta.focus();
        f.onsubmit = async e => {
          e.preventDefault();
          const t = ta.value.trim(); if (!t) return;
          msg.textContent = 'Đang gửi…';
          try { await sendProseFeedback(`${head(i, '💬')}\n— ${t}`); msg.textContent = 'Đã gửi, cảm ơn bạn.'; ta.value = ''; } catch { msg.textContent = 'Chưa gửi được, bạn thử lại sau.'; }
        };
        return;
      }
      if (done[tag(i)] === v) return;
      mark(v);
      try { await sendProseFeedback(head(i, v === 'up' ? '👍' : '👎')); done[tag(i)] = v; fbStore.set(FB_DONE, JSON.stringify(done)); }
      catch { mark(done[tag(i)] || ''); }
    });
  });
}
function bindOne(host, p, box) {
  $$('.pr-s', host).forEach(s => {
    const open = () => {
      const on = !s.classList.contains('on');
      $$('.pr-s.on', host).forEach(o => { o.classList.remove('on'); o.setAttribute('aria-expanded', 'false'); });
      if (on) { s.classList.add('on'); s.setAttribute('aria-expanded', 'true'); s.closest('.pr-p').after(box); box.innerHTML = proseWhy(p, s.dataset.pr); }
      box.hidden = !on;
    };
    s.onclick = e => { if (!e.target.closest('a, .gl')) open(); };
    s.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } };
  });
}
const SY_CH = { 'tong-quan': 'tong_quan', 'ban-menh': 'ban_menh', 'tinh-cach': 'tinh_cach', 'cong-danh': 'cong_danh', 'tai-bach': 'tai_bach', 'quan-he': 'quan_he', 'dai-han': 'dai_han', 'cach-cuc': 'cach_cuc' };

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

// Semantic routing: a reading fired at Mệnh or Phúc Đức goes to the chapter that answers its question (tính cách, nghề, tiền, gia đình),
// using the facet of its leading idea served by /api/claims ('facet:<claim>'). Readings of the other palaces describe that palace's topic
// (a 'khá giả' at Tử Tức is about the children), so they keep the palace route.
const DOMAIN_CH = { identity: 'tinh-cach', inner: 'tinh-cach', career: 'cong-danh', finance: 'tai-bach', relationships: 'quan-he' };
function topicChapter(f) {
  const pal = palaceOfSubject(f.subject), facet = CLAIMS['facet:' + f.claim];
  if (!facet || !['Mệnh', 'Phúc Đức'].includes(pal)) return null;
  const dom = facet === 'life.spirituality' ? 'inner' : facet.split('.')[0];
  if (pal === 'Phúc Đức') return dom === 'relationships' ? 'quan-he' : (dom === 'identity' || dom === 'inner') ? 'tinh-cach' : 'ban-menh';
  return DOMAIN_CH[dom] || 'ban-menh';
}

// The reading leads; what it stands on (structural analysis, calculation facts, book-verified findings) folds into one "Căn cứ" box, open only
// when the chapter has no reading of its own. A chapter whose facts are an instrument (the đại hạn / đại vận timeline) keeps them outside.
const KEEP_CALC = new Set(['dai-han', 'dai-van', 'muoi-hai-cung', 'tong-quan']);
function chapterBasis(c) {
  const inner = analysisHtml(c.blocks) + (KEEP_CALC.has(c.id) ? '' : c.calc || '') + (c.trad || '');
  const keep = KEEP_CALC.has(c.id) ? c.calc || '' : '';
  if (!inner.trim()) return keep;
  return keep + `<details class="ch-basis"${c.synth ? '' : ' open'}><summary><span class="cb-t">Căn cứ của chương này</span><span class="cb-s">dữ kiện lá số, phân tích cấu trúc và các nhận định theo sách</span></summary>${inner}</details>`;
}
function mount(host, chapters, prefix, ctx) {
  // the user's own chart, with career / relationship status in the profile: those chapters come right after the overview (focus.js)
  if (ctx.focus?.length) {
    chapters = orderChapters(chapters, prefix, ctx.focus);
    const tq = chapters.find(c => c.id === 'tong-quan'), titles = focusIds(prefix, ctx.focus).map(id => chapters.find(c => c.id === id)?.title).filter(Boolean);
    if (tq && titles.length) tq.synth = focusNote(ctx.focus, titles) + (tq.synth || '');
  }
  host.innerHTML = `<div class="rp-layout">
    <nav class="rp-toc" aria-label="Mục lục luận giải"><ol>${chapters.map((c, i) => `<li${c.pro ? ' class="pro-only"' : ''}><a href="#${prefix}-${c.id}" data-ch="${c.id}"><span>${pad(i + 1)}</span>${c.title}</a></li>`).join('')}</ol></nav>
    <div class="rp-body">${chapters.map((c, i) => `<article class="chapter${c.pro ? ' pro-only' : ''}" id="${prefix}-${c.id}"><header><span class="ch-no">${pad(i + 1)}</span><h3>${c.title}</h3></header><p class="lead">${c.lead}</p>${WHAT[prefix]?.[c.id] ? `<p class="ch-what easy-only"><b>Nói đơn giản:</b> ${WHAT[prefix][c.id]}</p>` : ''}${c.synth || ''}${chapterBasis(c)}</article>`).join('')}
      <div class="sys-switch"><div><b>${prefix === 'bt' ? 'Đã đọc hết phần Bát Tự' : 'Đã đọc hết phần Tử Vi'}</b><span>${prefix === 'bt' ? 'Xem cùng thời điểm sinh theo Tử Vi, hoặc lưu bản luận giải đầy đủ.' : 'Xem cùng thời điểm sinh theo Bát Tự, hoặc lưu bản luận giải đầy đủ.'}</span></div>
        <div class="sys-act"><button type="button" class="btn btn-sm" data-go="${prefix === 'bt' ? 'tu-vi' : 'bat-tu'}">${prefix === 'bt' ? 'Xem Tử Vi →' : 'Xem Bát Tự →'}</button><button type="button" class="btn btn-ghost btn-sm" data-act="print">Tải PDF</button><button type="button" class="btn btn-ghost btn-sm" data-act="again">Lập lá số khác</button></div></div></div></div>`;
  autoLink(host, prefix === 'bt' ? 'bt' : 'tv');
  $$('[data-jump]', host).forEach(r => r.onclick = () => $('#' + prefix + '-' + r.dataset.jump, host).scrollIntoView({ behavior: 'smooth', block: 'start' }));
  $$('.ref', host).forEach(r => r.onclick = () => ctx.openPalace(r.dataset.palace));
  $$('.cx-cond', host).forEach(b => b.onclick = () => ctx.highlight?.(JSON.parse(b.dataset.items), b.dataset.label));
  $$('.sy-s[data-rules]', host).forEach(s => s.onclick = () => { const on = s.classList.toggle('on'); const box = s.closest('.synth').querySelector('.sy-why'); if (box) { s.closest('.sy-p').after(box); box.hidden = !on; box.innerHTML = on ? `<b>Truy vết câu này:</b> ${esc(s.dataset.rules)}<br><span class="muted">${esc(SY_BASIS[s.dataset.basis]?.[1] || '')}</span>` : ''; } $$('.sy-s.on', s.closest('.synth')).forEach(o => o !== s && o.classList.remove('on')); });
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
    <div class="pro-only">${fs.length ? findingList(fs, { label: true }) + '<p class="muted small">Đây là cách đọc theo hệ biểu tượng truyền thống, không phải dự báo hay chẩn đoán.</p>' : notice('Chưa có quy tắc nào được kích hoạt cho phần này', note || 'Bộ quy tắc hiện hành chưa phủ tới nội dung này, nên hệ thống không đưa ra nhận định thay vì suy đoán.')}</div>
    <div class="easy-only">${easyReadings(fs, { where, empty: emptyReading(topic, terms(), { palace }) })}<p class="muted small">Đây là cách đọc theo hệ biểu tượng truyền thống, không phải dự báo hay chẩn đoán.</p></div></div>`;
  const deep = (sysKey, label, traceObj) => { const d = reason.systems[sysKey]; return `<div class="ch-calc"><p class="eyebrow">Dành cho người muốn kiểm chứng</p>
    ${d.findings.length ? acc('Tất cả nhận định và chuỗi suy luận', `${d.findings.length} nhận định`, findingList(d.findings, { where, byPlace: true, label: true })) : ''}
    ${acc(`Vết tính toán — ${label}`, 'từng bước chuẩn hóa và lập lá số', `<pre class="trace">${esc(JSON.stringify(traceObj, null, 1))}</pre>`)}
    ${reason.pack_problems.length ? notice('Vấn đề trong bộ quy tắc', esc(reason.pack_problems.join('; ')), 'warn') : ''}</div>`; };
  return { blocks, calc, ref, where, trad, deep };
};

const highlightsHtml = (fs, chTitle, chOf, extra) => {
  const ver = fs.filter(f => f.basis === 'verified'), top = ver.filter(f => chOf(f) !== 'chuyen-sau').slice(0, 4);
  return `<h5>Điểm nổi bật</h5><p class="hl-sum"><b>${ver.length}</b> nhận định được kích hoạt từ quy tắc đã đối chiếu sách.</p>${top.length ? `<ul class="hl-list">${top.map(f => `<li><button type="button" data-jump="${chOf(f)}"><span class="k">${chTitle[chOf(f)] || ''}</span><span>${esc(claimLabel(f.claim))}</span></button></li>`).join('')}</ul>` : ''}${extra || ''}`;
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
      trad: notice('Về mức độ tin cậy', 'Chỉ các nhận định đã đối chiếu sách mới được hiển thị.', 'info') && `<div class="ch-trad">${notice('Về mức độ tin cậy', 'Chỉ các nhận định đã đối chiếu sách mới được hiển thị. Đây là cách đọc theo hệ biểu tượng, không phải kết luận.', 'info')}</div>` },
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
  const evBt = ctx.interp?.report?.chapters?.find(c => c.id === 'bat_tu');
  if (evBt) { const cc = chapters.find(c => c.id === 'cach-cuc'); if (cc) cc.synth = evHtml([evBt]) + (cc.synth || ''); }
  // reader prose for Bát Tự (src/interpret/prose/bazi.ts) heads the Nhật Chủ chapter, evidence per sentence on click
  const bp = ctx.prose?.bat_tu, nc = chapters.find(x => x.id === 'nhat-chu');
  // the Bát Tự reading, split by chapter (prose/bazi.ts `chapters`); an older response without the split still goes to Nhật Chủ whole
  const btBy = {};
  if (bp?.chapters && Object.keys(bp.chapters).length) {
    for (const [id, paras] of Object.entries(bp.chapters)) {
      const c = chapters.find(x => x.id === id); if (!c || !paras?.length) continue;
      const key = 'bat_tu:' + id; btBy[key] = { ...bp, chapter: key, paragraphs: paras, evidence: { ...bp.evidence, limits: id === 'nhat-chu' ? bp.evidence.limits : [] } };
      c.synth = proseHtml(btBy[key]) + (c.synth || '');
    }
  } else if (bp?.paragraphs?.length && nc) { btBy.bat_tu = bp; nc.synth = proseHtml(bp) + (nc.synth || ''); }
  mount(host, chapters, 'bt', ctx);
  if (Object.keys(btBy).length) bindProse(host, btBy);
  host.insertAdjacentHTML('afterbegin', scopePanelBazi(b));
  yearExplorer($('#bt-year', host), ctx.req, b, 'bazi');
}

const XSTATE = { thanh_thuong: ['Thành cách, thế mạnh', 0], thanh: ['Thành cách', 1], pha_duoc_cuu: ['Bị phá nhưng được cứu', 2], bi_pha: ['Bị phá cách', 3], hinh_thuc: ['Mới có hình thức', 4], chua_du_du_kien: ['Chưa đủ dữ kiện để kết luận', 5], khong_hien: ['Không hiện', 6] };
const srcChip = src => src ? `<span class="cx-src cx-src-${esc(src.status)}" title="${esc(src.note || '')}"><b>${esc(src.status_vi)}</b>${src.sources?.length ? ' · ' + esc(src.sources.map(x => x.text).join('; ')) : ''}</span>${src.note ? `<span class="cx-note">${esc(src.note)}</span>` : ''}${src.reach_note ? `<span class="cx-note cx-dead">${esc(src.reach_note)}</span>` : ''}` : '';
const cond = (label, items, extra = '') => items?.length
  ? `<li><button type="button" class="cx-cond" data-label="${esc(label)}" data-items="${esc(JSON.stringify(items))}" title="Nhấn để tô sáng trên lá số"><span class="cx-l">${esc(label)}</span>${extra}</button></li>` : '';
function experimentalHtml(x) {
  if (!x) return '';
  const fs = (x.formations || []).slice().sort((a, b) => (XSTATE[a.state]?.[1] ?? 9) - (XSTATE[b.state]?.[1] ?? 9));
  const shown = fs.filter(f => f.state !== 'khong_hien'), hidden = fs.filter(f => f.state === 'khong_hien');
  const group = (f, kind, title) => {
    const rows = f.evidence.filter(e => e.kind === kind);
    if (!rows.length) return '';
    return `<div class="cx-g"><h6>${title}</h6><ul>${rows.map(e => e.active
      ? cond(e.label, e.items, `<span class="cx-b">${esc(e.because)}${e.rescues?.length ? ` · cứu: ${esc(e.rescues.join('; '))}` : ''}</span>${srcChip(e.source)}`)
      : `<li class="cx-off"><span class="cx-l">${esc(e.label)}</span><span class="cx-b">không có</span>${srcChip(e.source)}</li>`).join('')}</ul></div>`;
  };
  const card = f => `<div class="exp-card st-${esc(f.state)}"><h5>${esc(f.name_vi)} <span class="exp-pill">${esc(XSTATE[f.state]?.[0] || f.state)}</span></h5>
    ${f.source_summary?.text ? `<p class="small cx-sum">${esc(f.source_summary.text)}</p>` : ''}${(f.impossible_states || []).map(x => `<p class="small muted"><b>Trạng thái không thể đạt:</b> ${esc(x.reason)}.</p>`).join('')}
    <ol class="cx-chain">${f.chain.map(c => `<li><b>${esc(c.step)}</b><span>${esc(c.text)}</span></li>`).join('')}</ol>
    <div class="cx-conds"><div class="cx-g"><h6>Cấu trúc lõi</h6><ul>${cond('Các sao tạo nên cách ' + f.name_vi, f.core.items, `<span class="cx-b">${esc(f.core.because)}</span>${srcChip(f.core.source)}`)}</ul></div>
      ${group(f, 'boosters', 'Yếu tố tăng thế')}${group(f, 'breakers', 'Yếu tố phá cách')}${group(f, 'rescuers', 'Yếu tố cứu giải')}${group(f, 'refutations', 'Phản chứng')}</div>
    ${f.missing?.length ? `<p class="small muted"><b>Còn thiếu để lên bậc:</b> ${esc(f.missing.join('; '))}</p>` : ''}${f.caveats?.length ? `<p class="small muted"><b>Lưu ý:</b> ${esc(f.caveats.join('; '))}</p>` : ''}</div>`;
  return `<div class="exp"><p class="exp-tag">Thử nghiệm · chưa đối chiếu sách</p><p class="small">${esc(x.warning)}</p><p class="small muted">Nhấn vào từng điều kiện để tô sáng các sao và cung liên quan trên lá số.</p>
    ${shown.length ? shown.map(card).join('') : '<p class="muted">Không có cách nào trong danh sách thử nghiệm hiện hình trên lá số này.</p>'}
    ${hidden.length ? acc('Các cách đã kiểm tra nhưng không hiện', `${hidden.length} cách`, `<ul class="plain">${hidden.map(f => `<li>${esc(f.name_vi)}</li>`).join('')}</ul>`) : ''}</div>`;
}

export function renderTuviReport(host, chart, ctx) {
  const b = chart.bazi, t = chart.tuvi, tv = ctx.tv, { blocks, calc, ref, trad, deep } = shell(ctx);
  prSchool = t?.school?.dignity_school || 'khao_luan';
  const fs = (ctx.reason.systems.tu_vi?.findings || []).map(f => ({ ...f, sys: 'tu_vi' }));
  const chOf = f => /^cach_|thanh_cach/.test(f.claim) ? 'cach-cuc' : (topicChapter(f) || PAL_CH[palaceOfSubject(f.subject)] || 'chuyen-sau');
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
  // Mười hai cung: one accordion per palace, its facts and, when the reader prose has the palace, its whole reading
  const P12_CH = { 'Mệnh': 'menh', 'Quan Lộc': 'cong_danh', 'Tài Bạch': 'tai_bach', 'Thiên Di': 'thien_di', 'Phu Thê': 'phu_the', 'Phúc Đức': 'phuc_duc', 'Điền Trạch': 'dien_trach',
    'Nô Bộc': 'no_boc', 'Tử Tức': 'tu_tuc', 'Huynh Đệ': 'huynh_de', 'Phụ Mẫu': 'phu_mau', 'Tật Ách': 'tat_ach' };
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
      ${P12_CH[p.name] && ctx.prose?.[P12_CH[p.name]]?.paragraphs?.length ? `</div>${proseHtml(ctx.prose[P12_CH[p.name]])}<div class="p12-s">` : row('Nhận định', (pf.length ? `<span class="pro-only">${esc(pf.map(f => claimLabel(f.claim)).join('; '))}</span>` : '<span class="pro-only muted">chưa có quy tắc được kích hoạt</span>') + `<span class="easy-only">${(() => { const sh = classify(pf).show; return sh.length ? esc(sh.map(f => parsePhrase(f).core).join('; ')) : `<span class="muted">${esc(terms()['palace:' + p.name]?.plain || '')} Chưa có luận giải cá nhân hóa cho cung này.</span>`; })()}</span>`)}</div>`);
  }).join('');
  const chapters = [
    { id: 'tong-quan', title: 'Tổng quan Tử Vi', lead: `Lá số lập cho người sinh năm ${esc(t.year_gz)} (âm lịch ${bd(`${t.lunar.day}/${t.lunar.month}/`, t.lunar.day != null, DM)}${t.lunar.year}${t.lunar.leap ? ' nhuận' : ''}), ${esc(t.yin_yang_gender)}.`, blocks: blocks('tv', 'tong-quan'),
      calc: calc(`<div class="facts"><div><span class="k">Mệnh cung</span><b>${esc(tv.menh.stem)} ${esc(tv.menh.branch)}</b></div><div><span class="k">Thân cư</span><b>${esc(tv.than.name)}</b></div><div><span class="k">Cục</span><b>${esc(t.cuc.name)}</b></div><div><span class="k">Bản mệnh</span><b>${esc(t.menh_nap_am)}</b></div><div><span class="k">Cục và Mệnh</span><b>${esc(t.menh_cuc_relation)}</b></div><div><span class="k">Đại hạn hiện tại</span><b>${ph.dh ? `${esc(ph.dh.palace)} (${ph.dh.age_from}–${ph.dh.age_to})` : 'chưa vào'}</b></div></div><div class="pro-only">${highlightsHtml(fs, TITLE, chOf)}</div>`),
      trad: `<div class="ch-trad">${notice('Về mức độ tin cậy', 'Chỉ các nhận định đã đối chiếu sách mới được hiển thị. Đây là cách đọc theo hệ biểu tượng, không phải kết luận.', 'info')}</div>` },
    { id: 'ban-menh', title: 'Bản Mệnh', lead: `Bản mệnh ${esc(t.menh_nap_am)} thuộc hành ${esc(t.menh_element)}; ${esc(t.cuc.name)} thuộc hành ${esc(t.cuc.element)}.`, blocks: blocks('tv', 'ban-menh'),
      calc: calc(`${t.extras?.menh_chu ? `<div class="facts"><div><span class="k">Mệnh chủ (theo chi cung Mệnh)</span><b>${esc(t.extras.menh_chu.star)}</b></div><div><span class="k">Thân chủ (theo chi năm)</span><b>${esc(t.extras.than_chu.star)}</b></div><div><span class="k">Độ tin cậy</span><b>công thức phổ biến, chưa đối chiếu sách</b></div></div>` : ''}${palaceList(['Mệnh'])}<h5>Tam phương tứ chính của cung Mệnh</h5>${menhTamPhuongHtml(t)}<h5>Tứ Hóa theo can năm</h5><ul class="plain">${tuHoa}</ul>`), trad: trad(of('ban-menh'), null, 'tv:ban-menh') },
    { id: 'tinh-cach', title: 'Tính cách', lead: 'Nhìn từ cung Mệnh và cung Phúc Đức.', blocks: blocks('tv', 'tinh-cach'), calc: calc(palaceList(['Mệnh', 'Phúc Đức'])), trad: trad(of('tinh-cach'), null, 'tv:tinh-cach') },
    { id: 'cong-danh', title: 'Công danh', lead: 'Cung Quan Lộc và cung đối Thiên Di.', blocks: blocks('tv', 'cong-danh'), calc: calc(palaceList(['Quan Lộc', 'Thiên Di'])), trad: trad(of('cong-danh'), null, 'tv:cong-danh') },
    { id: 'tai-bach', title: 'Tài Bạch', lead: 'Cung Tài Bạch và Điền Trạch.', blocks: blocks('tv', 'tai-bach'), calc: calc(palaceList(['Tài Bạch', 'Điền Trạch'])), trad: trad(of('tai-bach'), null, 'tv:tai-bach') },
    { id: 'quan-he', title: 'Quan hệ', lead: 'Các cung liên quan đến người thân và các mối quan hệ.', blocks: blocks('tv', 'quan-he'), calc: calc(palaceList(['Phu Thê', 'Tử Tức', 'Huynh Đệ', 'Phụ Mẫu', 'Nô Bộc'])), trad: trad(of('quan-he'), null, 'tv:quan-he') },
    { id: 'dai-han', title: 'Đại hạn & lưu niên', lead: `Đại hạn chạy ${esc(t.dai_han_direction)}; ${ph.dh ? `hiện ở cung ${esc(ph.dh.palace)} (${ph.dh.age_from}–${ph.dh.age_to} tuổi)` : 'chưa vào đại hạn đầu'}.`, blocks: blocks('tv', 'dai-van'),
      calc: calc(`<h5>Các đại hạn</h5>${tv.timelineHtml}<h5>Lưu niên</h5><div id="tv-year"></div>`), trad: '' },
    { id: 'cach-cuc', title: 'Cách cục', lead: 'Các hình thái đặc biệt mà bộ quy tắc hiện hành có thể nhận ra.', blocks: blocks('tv', 'cach-cuc'),
      calc: calc(`${experimentalHtml(ctx.formations)}<h5>Nhận diện theo tên (vị trí sao)</h5>${(t.extras?.cach_cuc || []).length ? `<ul class="cc-list">${t.extras.cach_cuc.map(x => `<li><b>${esc(x.name)}</b><span class="muted">${esc(x.evidence)}</span></li>`).join('')}</ul><p class="muted small">Đây chỉ là nhận diện tên cách theo vị trí các sao. Ý nghĩa cát hay hung của từng cách chưa được đối chiếu sách nên hệ thống không nêu. Tên cách và nhóm sao theo thông lệ phổ biến, chưa đối chiếu trang sách.</p>` : '<p class="muted">Không nhận ra cách nào trong danh sách các cách được kiểm tra.</p>'}<h5>Nhận định từ bộ quy tắc</h5><p>Số nhận định về cách cục: ${of('cach-cuc').length || 'không có'}.</p>`),
      trad: (() => { const c = of('cach-cuc'); return `<div class="ch-trad"><p class="eyebrow">Diễn giải truyền thống</p><div class="pro-only">${c.length ? `<button type="button" class="btn btn-ghost btn-sm ig-toggle" aria-pressed="false">Xem đồ thị suy luận</button><div class="ig-box" hidden>${inferenceGraph(c[0])}<p class="muted small">Ví dụ cho nhận định đầu tiên.</p></div>${findingList(c, { label: true })}` : notice('Không có cách cục nào được nhận ra', '')}</div><div class="easy-only">${easyReadings(c, { where: shell(ctx).where, empty: emptyReading('tv:cach-cuc', terms()) })}</div></div>`; })() },
    { id: 'muoi-hai-cung', title: 'Toàn bộ mười hai cung', lead: 'Tra nhanh từng cung: sao, Tứ Hóa, Tuần Triệt, đại hạn và nhận định.', calc: calc(`<div class="p12">${p12}</div>`), trad: '' },
    { id: 'chuyen-sau', pro: true, title: 'Luận giải chuyên sâu', lead: 'Văn bản do bộ máy sinh từ các nhận định, kèm vết tính toán.', calc: deep('tu_vi', 'Tử Vi', { normalization: ctx.chartRaw.normalization_trace.steps, tuvi: t.trace.steps }), trad: '' },
  ];
  if (ctx.synth?.chapters) {
    const by = Object.fromEntries(ctx.synth.chapters.map(c => [c.id, c]));
    chapters.forEach(c => { c.synth = synthHtml(by[SY_CH[c.id]]); });
  }
  if (ctx.interp?.report?.chapters) {
    const ev = Object.fromEntries(ctx.interp.report.chapters.map(c => [c.id, c]));
    chapters.forEach(c => { if (EV_CH[c.id]) c.synth = evHtml(EV_CH[c.id].map(k => ev[k])) + (c.synth || ''); });
  }
  // reader prose per chapter (/api/interpret mode "prose"): Mệnh -> Bản Mệnh, Công danh -> Công danh, Tài Bạch -> Tài Bạch
  const PR_CH = { tong_quan: 'tong-quan', menh: 'ban-menh', cong_danh: 'cong-danh', tai_bach: 'tai-bach', thien_di: 'cong-danh', phu_the: 'quan-he', phuc_duc: 'tinh-cach', dien_trach: 'tai-bach', no_boc: 'quan-he',
    tu_tuc: 'quan-he', huynh_de: 'quan-he', phu_mau: 'quan-he', tat_ach: 'tinh-cach', van_han: 'dai-han' };
  const prByCh = {};
  for (const [k, id] of Object.entries(PR_CH)) { const p = ctx.prose?.[k]; if (p?.paragraphs?.length) prByCh[id] = (prByCh[id] || '') + proseHtml(p); }
  for (const [id, html] of Object.entries(prByCh)) { const c = chapters.find(x => x.id === id); if (c) c.synth = html + (c.synth || ''); }
  mount(host, chapters, 'tv', ctx);
  if (ctx.prose) bindProse(host, ctx.prose);
  yearExplorer($('#tv-year', host), ctx.req, b, 'tuvi');
}
