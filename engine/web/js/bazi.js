// FourPillarsChart + Bát Tự detail accordions.
import { $, $$, esc, STEMS, BRANCHES, EL, ELEMENTS, elChip, elIcon, PILLAR_LABEL, tenGodGroup, TEN_GOD_GROUPS } from './util.js';
import { fiveElements } from './elements.js';
import { acc, notice, timeline, yearExplorer, findingCard } from './ui.js';
import { elementBalanceHtml, godDistributionHtml } from './insights.js';

const ORDER = ['year', 'month', 'day', 'hour'];

const glyph = (c, kind) => `<div class="gz-char ${kind} el-${EL[c.e].slug}" data-el="${c.e}" data-gl="${kind === 'stem' ? 'can' : 'chi'}:${esc(c.n)}" role="button" tabindex="0" aria-label="${esc(c.n)}: xem giải thích">
  <span class="gz-han" lang="zh">${c.h}</span><span class="gz-vn">${esc(c.n)}</span>
  <span class="gz-el">${elIcon(c.e, 11)}${c.e}</span></div>`;

function pillarCard(key, p, dm) {
  const stem = STEMS[p.stem], br = BRANCHES[p.branch];
  return `<article class="pillar${dm ? ' dm' : ''}" data-pillar="${key}" aria-label="Trụ ${PILLAR_LABEL[key]}: ${esc(p.name)}">
    <header><span class="pl-label">Trụ ${PILLAR_LABEL[key]}</span>${dm ? '<span class="seal" title="Thiên can của trụ Ngày là Nhật Chủ">Nhật Chủ</span>' : ''}</header>
    <div class="pl-gz">${glyph(stem, 'stem')}<span class="pl-sep" aria-hidden="true"></span>${glyph(br, 'branch')}</div>
    <div class="pl-god"><span class="muted">Thập thần</span><b>${dm ? 'Nhật Chủ' : esc(p.stem_ten_god)}</b></div>
    <div class="pl-stage"><span class="muted">Trường sinh</span><b>${esc(p.stage_vs_day_master)}</b></div>
    <div class="pl-hid"><h6>Tàng can</h6>${p.hidden.map((h, i) => `<div class="hid el-${EL[h.element].slug}" data-el="${h.element}"><span class="hid-n">${i === 0 ? 'Chính' : i === 1 ? 'Trung' : 'Dư'}</span><b>${esc(h.name)}</b>${elIcon(h.element, 10)}<span class="hid-g">${esc(h.ten_god)}</span></div>`).join('')}</div>
  </article>`;
}

const PL = { year: 'Năm', month: 'Tháng', day: 'Ngày', hour: 'Giờ' };
const plPair = s => String(s).split('-').map(x => PL[x] || x).join(' – ');
const REL_TITLE = {
  stem_combine: 'Thiên can hợp', stem_clash: 'Thiên can xung', branch_six_combine: 'Địa chi lục hợp', branch_clash: 'Địa chi lục xung',
  branch_harm: 'Địa chi lục hại', branch_destroy: 'Địa chi phá', branch_triad_complete: 'Tam hợp', branch_meeting_complete: 'Tam hội',
  branch_penalty: 'Hình', branch_self_penalty: 'Tự hình',
};
function relText(k, it) {
  const chars = (it.stems ? it.stems.map(i => STEMS[i]?.n) : it.branches ? it.branches.map(i => BRANCHES[i]?.n) : it.branch != null ? [BRANCHES[it.branch]?.n] : []).filter(Boolean).join(' · ');
  const extra = it.potential_element ? ` — tiềm năng hóa ${it.potential_element}${it.transforms ? ' (đã hóa)' : ' (chưa xét hóa)'}` : '';
  return `<li><span class="rel-p">${esc(plPair(it.pillars || ''))}</span><b>${esc(chars)}</b>${extra ? `<span class="muted">${esc(extra)}</span>` : ''}</li>`;
}

export function renderBazi(host, b, ctx) {
  const counts = Object.fromEntries(ELEMENTS.map(e => [e, 0]));
  ORDER.forEach(k => { counts[STEMS[b.pillars[k].stem].e]++; counts[BRANCHES[b.pillars[k].branch].e]++; });
  const dmP = b.pillars.day, dmS = STEMS[dmP.stem], month = b.pillars.month;
  const gods = Object.fromEntries(TEN_GOD_GROUPS.map(g => [g, 0]));
  ORDER.filter(k => k !== 'day').forEach(k => { const g = tenGodGroup(b.pillars[k].stem_ten_god); if (g) gods[g]++; });
  const godChips = TEN_GOD_GROUPS.filter(g => gods[g]).map(g => `<span class="chip">${g}<b>×${gods[g]}</b></span>`).join('') || '<span class="muted">—</span>';
  const now = new Date().getFullYear();
  const lp = b.luck_pillars;
  const curIdx = lp.findIndex((l, i) => l.start_year_approx <= now && (!lp[i + 1] || now < lp[i + 1].start_year_approx));
  const tl = timeline(lp.map((l, i) => ({
    title: `<span class="tl-han">${esc(l.name)}</span>`, sub: `${esc(l.ten_god)}`, meta: `${Math.round(l.start_age)} tuổi · ${Math.round(l.start_year_approx)}`,
    el: EL[STEMS[l.stem].e].slug, current: i === curIdx,
  })), { label: 'Các đại vận Bát Tự' });

  const rels = Object.entries(b.relations).filter(([, v]) => v.length);
  const relBody = rels.length
    ? rels.map(([k, v]) => `<div class="rel-g"><h5>${REL_TITLE[k] || k}</h5><ul class="rel">${v.map(it => relText(k, it)).join('')}</ul></div>`).join('') + '<p class="muted small">Chỉ là dữ kiện về quan hệ giữa các chữ; việc “hóa” hay “hợp mà không hóa” chưa được xét.</p>'
    : '<p class="muted">Không phát hiện quan hệ hợp, xung, hại, phá, hình nào giữa các trụ.</p>';

  const nguyetLenh = `<p>Nguyệt lệnh là địa chi của tháng sinh (<b>${esc(BRANCHES[month.branch].n)}</b>, hành ${BRANCHES[month.branch].e}). Nhật Chủ ${esc(dmS.n)} ở trạng thái <b>${esc(month.stage_vs_day_master)}</b> tại tháng này.</p><p class="muted">Tháng Bát Tự đổi theo <i>tiết</i> trong 24 tiết khí chứ không theo mùng một âm lịch. Tiết gần nhất trước giờ sinh: <b>${new Date(b.jie_used.prev_jie_utc).toLocaleDateString('vi-VN', { timeZone: ctx.req.tz || 'Asia/Ho_Chi_Minh', day: 'numeric', month: 'numeric', year: 'numeric' })}</b>.</p>`;
  const thapThan = `<div class="tg-rows">${ORDER.map(k => { const p = b.pillars[k]; return `<div><span class="k">${PL[k]}</span><b>${k === 'day' ? 'Nhật Chủ' : esc(p.stem_ten_god)}</b><span class="muted">can ${esc(STEMS[p.stem].n)}</span></div>`; }).join('')}</div>`;
  const tangCan = `<div class="tc-rows">${ORDER.map(k => { const p = b.pillars[k]; return `<div><h5>${PL[k]} · ${esc(BRANCHES[p.branch].n)}</h5>${p.hidden.map(h => `<div class="tc">${elChip(h.element)} <b>${esc(h.name)}</b> <span class="muted">${esc(h.ten_god)}</span></div>`).join('')}</div>`; }).join('')}</div>`;
  // Thấu can / thông căn: purely positional facts (is a visible stem's own character hidden in some branch, and vice versa).
  const hiddenOf = k => b.pillars[k].hidden.map(h => h.stem);
  const rootRows = ORDER.map(k => {
    const p = b.pillars[k], st = STEMS[p.stem], sameEl = ORDER.filter(j => b.pillars[j].hidden.some(h => h.element === st.e)).map(j => PL[j]);
    const exact = ORDER.filter(j => hiddenOf(j).includes(p.stem)).map(j => PL[j]);
    return `<tr><th scope="row">${PL[k]} · ${esc(st.n)} <small>${st.e}</small></th><td>${exact.length ? esc(exact.join(', ')) : '<span class="muted">không</span>'}</td><td>${sameEl.length ? esc(sameEl.join(', ')) : '<span class="muted">không</span>'}</td></tr>`;
  }).join('');
  const thongCan = `<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Thiên can</th><th>Cùng chữ trong tàng can của trụ</th><th>Cùng hành trong tàng can của trụ</th></tr></thead><tbody>${rootRows}</tbody></table></div><p class="muted small">Đây là dữ kiện vị trí. Việc một can “có căn” mạnh hay yếu còn tùy nhiều điều kiện (mùa, hợp, xung...) mà hệ thống chưa xét.</p>`;

  host.innerHTML = `
    <div class="bz-top">
      <div>
        <div class="pillars" id="pillars">${ORDER.map(k => pillarCard(k, b.pillars[k], k === 'day')).join('')}</div>
        <div class="summary-strip">
          <div><span class="k">Nhật Chủ</span><b class="v el-${EL[dmS.e].slug}">${esc(dmS.n)} ${dmS.e}</b><span class="s">${esc(dmS.h)} · ${EL[dmS.e].h}</span></div>
          <div><span class="k">Nguyệt lệnh</span><b class="v">${esc(BRANCHES[month.branch].n)}</b><span class="s">tháng ${esc(month.name)}</span></div>
          <div><span class="k">Đại vận</span><b class="v">${esc(b.luck_direction)}</b><span class="s">khởi vận ${b.luck_start.years} năm ${b.luck_start.months} tháng</span></div>
          <div class="wide"><span class="k">Thập thần trên thiên can</span><span class="chips">${godChips}</span></div>
        </div>
      </div>
      <aside class="bz-el card-soft" aria-labelledby="bz-el-t"><h3 id="bz-el-t">Ngũ hành trong lá số</h3><p class="muted small">Đếm 8 chữ trên bốn trụ. Chọn một hành để thấy nó nằm ở đâu.</p><div id="bz-fe"></div></aside>
    </div>
    <div class="bz-tl"><h3>Đại vận</h3>${tl}</div>`;

  const pillars = $$('.pillar', host);
  const apply = el => { pillars.forEach(p => $$('.gz-char,.hid', p).forEach(c => { const hit = el && c.dataset.el === el; c.classList.toggle('hit', !!hit); c.classList.toggle('dim', !!el && !hit); })); };
  fiveElements($('#bz-fe', host), { counts, onSelect: apply });
  return { counts, parts: { luck: tl, nguyetLenh, thapThan, tangCan, thongCan, relations: relBody, relCount: rels.reduce((n, [, v]) => n + v.length, 0) } };
}
