// Small shared components: Accordion, Notice, ReasoningPanel, SourceReference, FortuneTimeline, YearExplorer.
import { esc, $, $$, post, SOURCES, elChip, STEMS, BRANCHES, claimLabel, claimPhrase } from './util.js';

export const acc = (title, sub, body, open = false, id = '') =>
  `<details class="acc"${open ? ' open' : ''}${id ? ` id="${id}"` : ''}><summary><span class="acc-t">${title}</span>${sub ? `<span class="acc-s">${sub}</span>` : ''}<svg class="acc-c" width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 6l5 5 5-5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></summary><div class="acc-b">${body}</div></details>`;

export const notice = (title, text, kind = 'info') =>
  `<div class="notice ${kind}" role="note"><svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><circle cx="9" cy="9" r="7.5" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M9 8v4.5M9 5.4v.1" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg><div><b>${title}</b>${text ? `<p>${text}</p>` : ''}</div></div>`;

export function sourceRef(id, verified = false) {
  return `<span class="src" title="${verified ? 'Đã xác minh nguồn' : 'Nguồn chưa được xác minh trang/mục cụ thể'}"><svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 1.5h6.5a1 1 0 011 1v8H3a1 1 0 01-1-1z" fill="none" stroke="currentColor" stroke-width="1"/></svg>${esc(SOURCES[id] || id)}<em>${verified ? 'đã xác minh' : 'chưa xác minh'}</em></span>`;
}

export function findingCard(f, refHtml = '') {
  const ok = f.basis === 'verified';
  return `<div class="finding-card ${ok ? 'ok' : 'draft'}"><p class="eyebrow">${ok ? 'Đã đối chiếu với sách' : 'Quy tắc nháp, chưa xác minh'}${refHtml ? ' · ' + refHtml : ''}</p><p class="f-claim">${f.effect === 'limit' ? 'Điều kiện hạn chế:' : 'Có thể nhận thấy một dấu hiệu liên quan đến'} ${esc(claimPhrase(f.claim, f.effect))}.</p>${acc('Vì sao quy tắc này khớp?', 'chuỗi suy luận, quy tắc đối lập, nguồn', reasoningPanel(f))}</div>`;
}
const KIND = { finding: 'Nhận định', rule: 'Quy tắc', source: 'Nguồn', fact: 'Dữ kiện' };
const KIND_ORDER = ['finding', 'rule', 'source', 'fact'];
/** Renders why a finding fired: the backward chain, opposing rules and the source. */
export function reasoningPanel(f, { graph = true } = {}) {
  const kinds = Object.values(f.why.kinds || {});
  const chain = (f.why.chain_vi || f.why.chain).map((c, i) => ({ text: c, kind: kinds[i] || KIND_ORDER[i] || 'fact' }));
  const srcs = [...new Set(chain.map(c => (c.text.match(/SRC_[A-Z0-9_]+/) || [])[0]).filter(Boolean))];
  const verified = id => chain.some(c => c.text.includes(id) && /\(verified\)/.test(c.text));
  const label = c => c.kind === 'finding' ? claimLabel(c.text.replace(/\s*\(.*$/, '')) : c.text.replace(/\s*@.*$/, '');
  const nodes = chain.map(c => `<li class="rn rn-${c.kind}"><span class="rn-k">${KIND[c.kind] || c.kind}</span><span class="rn-t">${esc(label(c))}</span></li>`).join('');
  return `<div class="why">
    <div class="why-h"><span class="badge ${f.basis === 'verified' ? 'ok' : 'draft'}">${f.basis === 'verified' ? 'Quy tắc đã xác minh' : 'Quy tắc nháp'}</span><span class="badge">${esc({ supported: 'Được hỗ trợ', limited: 'Bị giới hạn bởi quy tắc đối lập', unresolved: 'Chưa thể kết luận' }[f.status] || f.status)}</span><code>${esc(f.rule_id)}</code></div>
    <h5>Chuỗi suy luận ngược — vì sao nhận định này xuất hiện</h5>
    <ol class="chain">${nodes}</ol>
    <h5>Yếu tố đối lập</h5>
    ${f.why.opposed_by.length ? `<ul>${f.why.opposed_by.map(o => `<li>${esc(o)}</li>`).join('')}</ul>` : '<p class="muted">Không có quy tắc đối lập nào khớp trong bộ quy tắc hiện hành.</p>'}
    ${srcs.length ? `<h5>Nguồn tham chiếu</h5><p>${srcs.map(s => sourceRef(s, verified(s))).join(' ')}</p>` : ''}
  </div>`;
}

/** items: [{title, sub, meta, el, current, key}] */
export function timeline(items, { onPick = null, label = 'Dòng thời gian' } = {}) {
  return `<div class="tl" role="list" aria-label="${label}">${items.map((it, i) => `
    <${onPick ? 'button type="button"' : 'div'} class="tl-i${it.current ? ' now' : ''}${it.el ? ' el-' + it.el : ''}" role="listitem" data-i="${i}"${it.current ? ' aria-current="true"' : ''}>
      <span class="tl-age">${it.meta}</span><span class="tl-t">${it.title}</span><span class="tl-s">${it.sub || ''}</span>${it.current ? '<span class="tl-now">Hiện tại</span>' : ''}
    </${onPick ? 'button' : 'div'}>`).join('')}</div>`;
}

const REL = { can_hợp: 'Thiên can hợp', can_xung: 'Thiên can xung', 'chi_lục hợp': 'Địa chi lục hợp', chi_xung: 'Địa chi xung', chi_hại: 'Địa chi hại', chi_phá: 'Địa chi phá', chi_hình: 'Địa chi hình', chi_tam_hợp: 'Địa chi tam hợp', chi_tam_hội: 'Địa chi tam hội' };
const WITH = { year: 'trụ Năm', month: 'trụ Tháng', day: 'trụ Ngày', hour: 'trụ Giờ' };

/** YearExplorer — "lưu niên" structure for any chosen year. Facts only, no predictions. */
export function yearExplorer(host, req, bazi) {
  const y0 = req.year, now = new Date().getFullYear();
  const start = Math.min(Math.max(now, y0), y0 + 100);
  host.innerHTML = `<div class="yx"><div class="yx-bar"><label for="yx-r">Chọn năm</label><output class="yx-y"></output><input id="yx-r" type="range" min="${y0}" max="${y0 + 100}" value="${start}"></div><div class="yx-out" aria-live="polite"></div></div>`;
  const r = $('input', host), out = $('.yx-out', host), yv = $('.yx-y', host);
  let seq = 0;
  async function load(y) {
    yv.textContent = y; const mine = ++seq;
    out.classList.add('loading');
    try {
      const d = await post('/api/year', { ...req, to_year: y });
      if (mine !== seq) return;
      const b = d.bazi, t = d.tuvi;
      const inter = [...b.annual_vs_natal, ...b.luck_vs_natal];
      out.innerHTML = `<div class="yx-grid">
        <section><h4>Bát Tự</h4>
          <p class="yx-big"><span>Lưu niên</span><b>${esc(b.annual_pillar)}</b><em>${esc(b.annual_stem_ten_god)}</em></p>
          <p class="yx-big"><span>Đại vận</span><b>${esc(b.luck_pillar || 'chưa khởi')}</b><em>${esc(b.luck_stem_ten_god || '')}</em></p>
          <h5>Tương tác với nguyên cục</h5>
          ${inter.length ? `<ul class="yx-list">${inter.map(x => `<li><b>${esc(x.from)}</b> ${esc(REL[x.kind] || x.kind.replace(/_/g, ' '))} với ${esc(WITH[x.with] || x.with)}</li>`).join('')}</ul>` : '<p class="muted">Không có tương tác nào đáng kể.</p>'}
        </section>
        <section><h4>Tử Vi</h4>
          <p class="yx-big"><span>Tuổi mụ</span><b>${t.age_tuoi_mu}</b></p>
          <p class="yx-big"><span>Đại hạn</span><b>${t.dai_han ? esc(t.dai_han.palace) : 'chưa vào'}</b><em>${t.dai_han ? `${t.dai_han.age_from}–${t.dai_han.age_to} tuổi` : ''}</em></p>
          <p class="yx-big"><span>Lưu Thái Tuế</span><b>cung ${esc(t.luu_thai_tue_palace)}</b></p>
          <p class="yx-big"><span>Tiểu hạn</span><b>cung ${esc(t.tieu_han_palace)}</b><em>${esc(t.tieu_han_branch)}</em></p>
          <h5>Lưu Tứ Hóa</h5>
          <ul class="yx-list">${Object.entries(t.luu_tu_hoa).map(([k, v]) => `<li><b>${esc(k)}</b> · ${esc(v.star)}${v.natal_palace ? ` <span class="muted">(cung ${esc(v.natal_palace)})</span>` : ''}</li>`).join('')}</ul>
        </section></div>
        <section class="yx-months"><h4>Lưu nguyệt Bát Tự <span class="muted small">· tháng tính theo tiết, từ Lập Xuân</span></h4>
          <ol class="yx-mo">${(b.months || []).map(m => `<li><span class="mo-j">${esc(m.jie)}</span><b>${esc(m.pillar)}</b><em>${esc(m.ten_god)}</em>${m.vs_natal.length ? `<span class="mo-n" title="${esc(m.vs_natal.map(x => (REL[x.kind] || x.kind.replace(/_/g, ' ')) + ' trụ ' + (WITH[x.with] || x.with).replace('trụ ', '')).join('; '))}">${m.vs_natal.length} tương tác</span>` : '<span class="mo-n muted">—</span>'}</li>`).join('')}</ol></section>
        <p class="muted small">Đây là các dữ kiện cấu trúc theo thời gian, không phải dự đoán sự kiện. Lưu nguyệt Tử Vi chưa được hỗ trợ vì chưa có nguồn xác minh.</p>`;
    } catch (e) { out.innerHTML = notice('Không tải được dữ liệu năm này', esc(e.message), 'warn'); }
    out.classList.remove('loading');
  }
  r.oninput = () => { yv.textContent = r.value; clearTimeout(r._t); r._t = setTimeout(() => load(+r.value), 160); };
  load(start);
  return { setYear: y => { r.value = Math.min(Math.max(y, y0), y0 + 100); load(+r.value); } };
}

export const stemName = i => STEMS[i]?.n, branchName = i => BRANCHES[i]?.n;
export { claimLabel, elChip };
