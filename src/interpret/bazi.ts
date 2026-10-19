// Bát Tự chapter: the four pillars, the day master and what the verified Bát Tự rules say about them — nothing else.
// Rule inference runs on the fact base the Python engine reads for system 'bat_tu' (facts.bazi_facts, sent by /api/facts as bazi.base),
// with the same rule set, so the same rules fire (parity test in test/engine.test.ts). What is narrated:
//   computed   pillars, stem ten gods, hidden stems of the month branch, roots of the day master, elements visible on the chart, luck
//              pillars (tinh_toan: facts, no reading)
//   book       readings of verified rules that fired (today: day-master character, 八字真宗 PDF pp.25-26, and day-pillar nạp âm,
//              PDF pp.31-32), paraphrased, with the PDF page
//   limits     draft rules that fired are listed as left out (the manual's direct judgements, zz_direct_*, are voiced by prose/bazi.ts instead); strength (vượng suy), useful god (dụng thần), structure (cách cục) and the
//              manual's direct judgements (PDF pp.51-58) are not in this chapter, because no rule for them is both verified and wired
// Nothing here is mixed with Tử Vi: the two systems are read separately.
import { Renderer, citeVi, mergeCites, type Paragraph } from './generator.ts';
import { run } from './engine.ts';
import { joinVi } from './semantic.ts';
import type { ChartInput, ContentModule, Finding, Knowledge, Rule } from './types.ts';

const S = (text: string, rules: string[] = []) => ({ text, rules });
const ELEMENTS = ['Kim', 'Mộc', 'Thủy', 'Hỏa', 'Thổ'];
const PILLAR_VI: Record<string, string> = { year: 'năm', month: 'tháng', day: 'ngày', hour: 'giờ' };

/** "tính cách thường được mô tả là X (bảng 日干五行)" -> "X": the reading without the claim frame and the table tag */
export function baziCore(label: string): string {
  return label.replace(/^(hạn chế:\s*)?/, '').replace(/^tính cách thường được mô tả là\s+/, '').replace(/\s*\((bảng|theo nạp âm)[^)]*\)\s*$/, '').trim();
}

export interface BaziPrepared { findings: Finding[]; verified: Set<string>; drafts: Array<{ rule: Rule; claim: string }> }
const cache = new WeakMap<ChartInput, WeakMap<Knowledge, BaziPrepared>>();
export function prepareBazi(chart: ChartInput, k: Knowledge): BaziPrepared | null {
  if (!chart.bazi) return null;
  const hit = cache.get(chart)?.get(k);
  if (hit) return hit;
  const res = run(k.rules, k.sources, chart.bazi.base, 'bat_tu');
  const rmap = new Map(k.rules.map(r => [r.id, r]));
  const p: BaziPrepared = { findings: res.findings, verified: new Set(res.findings.filter(f => f.basis === 'verified').map(f => f.ruleId)),
    drafts: res.findings.filter(f => f.basis !== 'verified').map(f => ({ rule: rmap.get(f.ruleId)!, claim: f.claim })) };
  if (!cache.has(chart)) cache.set(chart, new WeakMap());
  cache.get(chart)!.set(k, p);
  return p;
}

export function baziChapter(chart: ChartInput, k: Knowledge, modules: ContentModule[], seed: string): { paragraphs: Paragraph[]; verified: Set<string> } {
  const P = prepareBazi(chart, k), b = chart.bazi;
  const r = new Renderer(k, `${seed}|bat_tu`);
  if (!P || !b) {
    r.set('bz.none', '1');
    return { paragraphs: r.render(modules), verified: new Set() };
  }
  const rmap = new Map(k.rules.map(x => [x.id, x]));
  const reading = (f: Finding) => { const rule = rmap.get(f.ruleId); return baziCore(rule?.reading?.replace(/\s*\[[^\]]*\]/g, '') ?? k.claims[f.claim] ?? f.claim); };
  const cite = (f: Finding) => mergeCites((rmap.get(f.ruleId)?.cites ?? []).map(citeVi));
  // the manual's direct judgements (category zz_direct_*, pp.50-74) belong to the reader prose (prose/bazi.ts), not to this chapter
  const direct = (f: { ruleId: string }) => (rmap.get(f.ruleId)?.category ?? '').startsWith('zz_direct');
  const ver = P.findings.filter(f => f.basis === 'verified' && !direct(f));
  const byCat = (cat: string) => ver.filter(f => rmap.get(f.ruleId)?.category === cat).sort((x, y) => x.ruleId.localeCompare(y.ruleId));
  const pil = b.pillars, f = b.base.chart as Record<string, unknown>;

  // ---------- computed frame
  r.set('bz.pillars', (['year', 'month', 'day', 'hour'] as const).map(x => `${PILLAR_VI[x]} ${pil[x].name}`).join(', '));
  r.set('bz.dm', b.day_master); r.set('bz.dm_el', b.day_master_element);
  r.set('bz.day', pil.day.name); r.set('bz.month_branch', pil.month.branch); r.set('bz.dm_stage', pil.month.stage ?? '');
  r.set('bz.stem_gods', (['year', 'month', 'hour'] as const).filter(x => pil[x].stem_ten_god).map(x => `can ${PILLAR_VI[x]} ${pil[x].stem} là ${pil[x].stem_ten_god}`).join(', '));
  r.set('bz.month_hidden', joinVi(pil.month.hidden.map(h => `${h.stem} (${h.element}, ${h.ten_god})`)));
  const roots = (f['bazi.dm_root_pillars'] as string[] | undefined) ?? [];
  r.set('bz.roots', roots.length ? joinVi(roots.map(x => `trụ ${PILLAR_VI[x] ?? x}`)) : '');
  r.set('bz.no_root', f['bazi.dm_has_root'] === false ? '1' : '');
  const missing = (f['bazi.missing_elements'] as string[] | undefined) ?? [];
  r.set('bz.missing', joinVi(missing));
  r.set('bz.all_elements', missing.length ? '' : '1');
  const hiddenEls = new Set(Object.values(pil).flatMap(p => p.hidden.map(h => h.element)));
  const hiddenOnly = missing.filter(e => hiddenEls.has(e));
  r.set('bz.hidden_only', joinVi(hiddenOnly));
  r.set('bz.absent', joinVi(missing.filter(e => !hiddenEls.has(e) && ELEMENTS.includes(e))));
  // luck pillars
  const yr = chart.year.year;
  const cur = [...b.luck].reverse().find(l => l.start_year !== null && l.start_year <= yr), next = cur ? b.luck[b.luck.indexOf(cur) + 1] : b.luck[0];
  r.set('bz.luck_dir', b.luck_direction);
  const a = b.luck_start_age, months = Math.round((a - Math.floor(a)) * 12);
  r.set('bz.luck_start', `${Math.floor(a)} tuổi${months ? ` ${months} tháng` : ''}`);
  r.set('bz.luck_now', cur ? `${cur.name}${cur.ten_god ? ` (thập thần ${cur.ten_god})` : ''}, bắt đầu khoảng năm ${cur.start_year}` : '');
  r.set('bz.luck_now_starts_this_year', cur && cur.start_year === yr ? '1' : '');
  r.set('bz.luck_next', next ? `${next.name}${next.ten_god ? ` (${next.ten_god})` : ''} từ khoảng năm ${next.start_year}` : '');
  r.set('bz.year', String(yr));
  r.set('bz.kong', joinVi(b.kong_wang_day ?? []));

  // ---------- verified readings
  const dm = byCat('day_master_character'), na = byCat('day_pillar_nap_am');
  r.setItems('bz_dm', dm.map(x => ({ 'r.quote': S(reading(x), [x.ruleId]), 'r.cite': S(cite(x)) })));
  r.set('bz.napam', String(f['bazi.day_nap_am'] ?? ''));
  r.setItems('bz_napam', na.map(x => ({ 'r.quote': S(reading(x), [x.ruleId]), 'r.cite': S(cite(x)) })));
  const other = ver.filter(x => !['day_master_character', 'day_pillar_nap_am'].includes(rmap.get(x.ruleId)?.category ?? ''));
  r.setItems('bz_other', other.map(x => ({ 'r.quote': S(reading(x), [x.ruleId]), 'r.cite': S(cite(x)) })));
  r.set('bz.verified_n', String(ver.length));
  r.set('bz.has_readings', ver.length ? '1' : '');
  // ---------- limits
  const dr = P.drafts.filter(d => !d.rule.category.startsWith('zz_direct')).map(d => baziCore((d.rule.reading ?? k.claims[d.claim] ?? d.claim).replace(/\s*\[[^\]]*\]/g, '')));
  r.set('bz.drafts', dr.length ? `${joinVi(dr.slice(0, 3).map(x => `“${x}”`))}${dr.length > 3 ? ` cùng ${dr.length - 3} câu khác` : ''}` : '', P.drafts.filter(d => !d.rule.category.startsWith('zz_direct')).map(d => d.rule.id));
  r.set('bz.drafts_n', dr.length ? String(dr.length) : '');
  return { paragraphs: r.render(modules), verified: P.verified };
}
