// Derived, objective summaries computed from the chart data already returned by the API (no new rules, no prose claims).
import { esc, STEMS, BRANCHES, EL, ELEMENTS, elChip, elIcon, tenGodGroup, TEN_GOD_GROUPS, starKind } from './util.js';

const KEYS = ['year', 'month', 'day', 'hour'];

export function elementStats(b) {
  const vis = Object.fromEntries(ELEMENTS.map(e => [e, 0])), hid = { ...vis };
  KEYS.forEach(k => { const p = b.pillars[k]; vis[STEMS[p.stem].e]++; vis[BRANCHES[p.branch].e]++; p.hidden.forEach(h => hid[h.element]++); });
  return { vis, hid, absentVisible: ELEMENTS.filter(e => !vis[e]), absentAll: ELEMENTS.filter(e => !vis[e] && !hid[e]) };
}

/** Five bars: visible characters (solid) and hidden stems (outlined), each labelled with text + number. */
export function elementBalanceHtml(b) {
  const { vis, hid, absentVisible, absentAll } = elementStats(b);
  const max = Math.max(1, ...ELEMENTS.map(e => vis[e] + hid[e]));
  const dm = STEMS[b.pillars.day.stem].e;
  const row = e => `<div class="eb-row el-${EL[e].slug}"><span class="eb-n">${elIcon(e, 12)}<span lang="zh">${EL[e].h}</span> ${e}${e === dm ? ' <small>Nhật Chủ</small>' : ''}</span>
    <span class="eb-bar" role="img" aria-label="${e}: ${vis[e]} trên tám chữ, ${hid[e]} trong tàng can"><i class="eb-v" style="width:${vis[e] / max * 100}%"></i><i class="eb-h" style="width:${hid[e] / max * 100}%"></i></span>
    <span class="eb-c"><b>${vis[e]}</b> + ${hid[e]}</span></div>`;
  return `<div class="eb"><div class="eb-legend"><span><i class="eb-v sw"></i>Tám chữ trên bốn trụ</span><span><i class="eb-h sw"></i>Tàng can</span></div>${ELEMENTS.map(row).join('')}
    <p class="muted small">${absentAll.length ? `Không xuất hiện ở cả tám chữ lẫn tàng can: <b>${absentAll.join(', ')}</b>.` : absentVisible.length ? `Không có trên tám chữ nhưng có trong tàng can: <b>${absentVisible.join(', ')}</b>.` : 'Cả năm hành đều xuất hiện trên tám chữ.'}</p></div>`;
}

export function godStats(b) {
  const vis = Object.fromEntries(TEN_GOD_GROUPS.map(g => [g, 0])), hid = { ...vis };
  KEYS.forEach(k => { const p = b.pillars[k]; if (k !== 'day') { const g = tenGodGroup(p.stem_ten_god); if (g) vis[g]++; } p.hidden.forEach(h => { const g = tenGodGroup(h.ten_god); if (g) hid[g]++; }); });
  return { vis, hid };
}
const GOD_NOTE = { 'Tỉ Kiếp': 'cùng hành với Nhật Chủ', 'Thực Thương': 'hành Nhật Chủ sinh ra', 'Tài': 'hành Nhật Chủ khắc', 'Quan Sát': 'hành khắc Nhật Chủ', 'Ấn': 'hành sinh ra Nhật Chủ' };
export function godDistributionHtml(b) {
  const { vis, hid } = godStats(b), max = Math.max(1, ...TEN_GOD_GROUPS.map(g => vis[g] + hid[g]));
  return `<div class="eb gd">${TEN_GOD_GROUPS.map(g => `<div class="eb-row"><span class="eb-n">${g}<small>${GOD_NOTE[g]}</small></span><span class="eb-bar" role="img" aria-label="${g}: ${vis[g]} trên thiên can, ${hid[g]} trong tàng can"><i class="eb-v gd-v" style="width:${vis[g] / max * 100}%"></i><i class="eb-h" style="width:${hid[g] / max * 100}%"></i></span><span class="eb-c"><b>${vis[g]}</b> + ${hid[g]}</span></div>`).join('')}
    <p class="muted small">Số thứ nhất: trên thiên can (ba can ngoài Nhật Chủ). Số thứ hai: trong tàng can của bốn địa chi.</p></div>`;
}

/** Summary of the palaces in the Mệnh palace's tam phương tứ chính. */
export function menhTamPhuong(t) {
  const byBranch = Object.fromEntries(t.palaces.map(p => [p.branch, p]));
  const menh = t.palaces.find(p => p.name === 'Mệnh'), s = t.structure[menh.branch];
  const set = [menh, byBranch[s.opposite], ...s.tam_hop.map(b => byBranch[b])];
  const cnt = k => set.flatMap(p => p.stars.filter(x => !p.major_stars.includes(x) && starKind(x) === k)).length;
  const majors = set.flatMap(p => p.major_stars.map(star => ({ star, palace: p.name, dg: p.major_dignity?.[star] })));
  return { set, majors, pos: cnt('pos'), neg: cnt('neg'), tuanTriet: set.filter(p => p.tuan || p.triet).map(p => `${p.name} (${[p.tuan && 'Tuần', p.triet && 'Triệt'].filter(Boolean).join(' + ')})`), menh };
}
export function menhTamPhuongHtml(t) {
  const m = menhTamPhuong(t);
  return `<div class="tp"><div class="tp-grid">${m.set.map((p, i) => `<button type="button" class="tp-p ref" data-palace="${esc(p.name)}"><span class="k">${i === 0 ? 'Bản cung' : i === 1 ? 'Xung chiếu' : 'Tam hợp'}</span><b>${esc(p.name)}</b><span class="muted">${esc(p.major_stars.join(', ') || 'vô chính diệu')}</span></button>`).join('')}</div>
    <ul class="plain tp-l"><li>Chính tinh trong tam phương tứ chính: ${m.majors.length ? m.majors.map(x => `${esc(x.star)}${x.dg ? ` (${esc(x.dg)})` : ''}`).join(', ') : 'không có'}.</li>
    <li>Phụ tinh cát: <b>${m.pos}</b> · sát/hung tinh: <b>${m.neg}</b>.</li>${m.tuanTriet.length ? `<li>Có Tuần/Triệt tại: ${esc(m.tuanTriet.join('; '))}.</li>` : ''}</ul></div>`;
}

/** Current Đại vận (Bát Tự) and Đại hạn (Tử Vi) for today's date. */
export function currentPhase(b, t, req) {
  const now = new Date().getFullYear(), age = now - req.year + 1;
  const lp = b.luck_pillars, i = lp.findIndex((l, k) => l.start_year_approx <= now && (!lp[k + 1] || now < lp[k + 1].start_year_approx));
  const dh = t.dai_han.find(d => age >= d.age_from && age <= d.age_to);
  return { now, age, luck: i >= 0 ? lp[i] : null, dh };
}
export function currentPhaseHtml(b, t, req) {
  const c = currentPhase(b, t, req);
  return `<div class="facts"><div><span class="k">Năm ${c.now}</span><b>${c.age} tuổi mụ</b></div>
    <div><span class="k">Đại vận Bát Tự</span><b>${c.luck ? `${esc(c.luck.name)} · ${esc(c.luck.ten_god)}` : 'chưa khởi vận'}</b></div>
    <div><span class="k">Đại hạn Tử Vi</span><b>${c.dh ? `${esc(c.dh.palace)} (${c.dh.age_from}–${c.dh.age_to})` : 'chưa vào'}</b></div></div>`;
}
