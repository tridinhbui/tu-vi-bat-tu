// Tổng quan lá số Tử Vi (prose-style plan S1): the block a reader meets first. It says where the chart stands before any reading:
//   - bản mệnh (nạp âm of the year) and its element, the cục and its element, and how the two relate (computed); the Khảo Luận reading of
//     that relation only when its rule fired (Cục khắc Mệnh, KL p.238);
//   - the Mệnh palace named star by star with the brightness of the checked dignity cells ("Cự Môn (Hãm Địa) hóa Lộc tọa thủ, cùng …");
//   - where Thân sits, with the Thân-specific book readings that fired on that palace;
//   - Mệnh chủ / Thân chủ from the common table (not checked against a page: named only, labelled pho_thong);
//   - the độ số readings that fired (âm dương, giờ sinh, mùa sinh, can chi, Tứ Mộ: KL pp.238-244, TH pp.75-76), each in the rule's own sense,
//     then their lean.
// No meaning is given to the nạp âm name, the lai nhân cung or the cân lượng: no source for them is in the knowledge base.
// The structured `card` carries the same facts for a grid in the report.
import type { ChartInput, Finding, Knowledge } from '../types.ts';
import type { ReadingPlan } from '../reason/plan.ts';
import { Micro, finish, lowerFirst } from './micro.ts';
import type { ProseParagraph, ProseSentence, SentenceTrace } from './realize.ts';
import { validateProse, type ProseIssue, type ProseMetrics } from './validate.ts';
import { splitReading } from './narrative.ts';
import { configClause } from './named.ts';

export interface OverviewLib {
  status: string; identity: string[]; relation: Record<string, string[]>; menh: string[]; than_same: string[]; than: string[]; than_meaning: string[];
  than_rule: string[]; chu: string[]; relation_book?: Record<string, string[]>; degree_lead: string[]; degree: Record<string, string[]>; degree_generic: string[]; lean: Record<'up' | 'down' | 'mixed', string[]>;
}
export interface OverviewFact { key: string; label: string; value: string; basis: SentenceTrace['basis']; cites: string[] }
export interface ProseOverview {
  engine: string; kbVersion: string; chapter: 'tong_quan'; palace: 'Tổng quan'; title: string; draft: boolean;
  card: OverviewFact[]; paragraphs: ProseParagraph[]; text: string; issues: ProseIssue[]; metrics: ProseMetrics; pass: boolean;
  evidence: { resolved: []; tensions: []; unused: string[]; rules: Record<string, { reading: string; cites: string[]; verified: boolean }>; concepts: Record<string, string>; divergences: [] };
  /** rule ids this block voiced (the reasoned Mệnh section does not repeat them) */
  voiced: string[];
}

const MENH_CHU = ['Tham Lang', 'Cự Môn', 'Lộc Tồn', 'Văn Khúc', 'Liêm Trinh', 'Vũ Khúc', 'Phá Quân', 'Vũ Khúc', 'Liêm Trinh', 'Văn Khúc', 'Lộc Tồn', 'Cự Môn'];
const THAN_CHU = ['Linh Tinh', 'Thiên Tướng', 'Thiên Lương', 'Thiên Đồng', 'Văn Xương', 'Thiên Cơ', 'Hỏa Tinh', 'Thiên Tướng', 'Thiên Lương', 'Thiên Đồng', 'Văn Xương', 'Thiên Cơ'];
const BRANCHES = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'];
const STEM_EL: Record<string, string> = { 'Giáp': 'Mộc', 'Ất': 'Mộc', 'Bính': 'Hỏa', 'Đinh': 'Hỏa', 'Mậu': 'Thổ', 'Kỷ': 'Thổ', 'Canh': 'Kim', 'Tân': 'Kim', 'Nhâm': 'Thủy', 'Quý': 'Thủy' };
const BRANCH_EL: Record<string, string> = { 'Tý': 'Thủy', 'Sửu': 'Thổ', 'Dần': 'Mộc', 'Mão': 'Mộc', 'Thìn': 'Thổ', 'Tỵ': 'Hỏa', 'Ngọ': 'Hỏa', 'Mùi': 'Thổ', 'Thân': 'Kim', 'Dậu': 'Kim', 'Tuất': 'Thổ', 'Hợi': 'Thủy' };
const SEASON_EL: Record<string, string> = { 'xuân': 'Mộc', 'hạ': 'Hỏa', 'thu': 'Kim', 'đông': 'Thủy' };
const GEN: Record<string, string> = { 'Thủy': 'Mộc', 'Mộc': 'Hỏa', 'Hỏa': 'Thổ', 'Thổ': 'Kim', 'Kim': 'Thủy' };
const fill = (t: string, v: Record<string, string>) => t.replace(/\{([A-Za-z_]+)\}/g, (m, k) => v[k] ?? m);
/** a rule whose condition names the palace that holds Thân */
const isThanRule = (conditions: unknown) => JSON.stringify(conditions).includes('"palace.is_than"');

/** `palaces` (default true): also name the Mệnh and Thân palaces star by star and the Thân readings; off when the luận cung Mệnh chapter
 *  (prose/luan.ts) tells them, so the report does not say them twice. The card keeps them either way. */
export function proseOverview(chart: ChartInput, k: Knowledge, findings: Finding[], plan: ReadingPlan, seed: string, engine: string, allowDraft: boolean,
  o: { palaces?: boolean } = {}): ProseOverview {
  const palaces = o.palaces !== false;
  const L = k.prose?.overview;
  const usable = !!L && (allowDraft || L.status === 'approved');
  const m = new Micro(`${seed}|tong_quan`, k.prose!.connectives, k.prose!.frames);
  const rmap = new Map(k.rules.map(r => [r.id, r]));
  const rules: ProseOverview['evidence']['rules'] = {};
  const voiced: string[] = [];
  const say = (xs: ProseSentence[], text: string, basis: SentenceTrace['basis'], ids: string[] = [], cites: string[] = [], concepts: string[] = []) => {
    const t = finish(text.replace(/\{S\}/g, () => lowerFirst(m.subject()))); m.said(t);
    for (const id of ids) { const r = rmap.get(id)!; rules[id] = { reading: (r.reading ?? '').replace(/^(khuynh hướng|hạn chế:)\s*/, ''), cites: r.cites, verified: r.reviewStatus === 'verified' }; voiced.push(id); }
    xs.push({ text: t, trace: { move: 'ANCHOR', concepts, rules: ids, cites: [...new Set([...cites, ...ids.flatMap(id => rmap.get(id)!.cites)])].sort(), basis, step: 'overview' } });
  };
  const menh = chart.palaces.find(p => p.name === 'Mệnh')!, than = chart.palaces.find(p => p.is_than) ?? menh;
  const cf = chart.base.chart ?? {};
  const mel = String(cf['chart.menh_element'] ?? ''), cel = chart.cuc.element;
  const [stem, ybr] = chart.year_gz.split(' ');
  const mc = MENH_CHU[menh.branch_index], tc = THAN_CHU[BRANCHES.indexOf(ybr)];
  const pol = (branchIndex: number) => branchIndex % 2 === 0 ? 'dương' : 'âm';
  const season = String(cf['chart.birth_season'] ?? '');
  const seasonEl = SEASON_EL[season];
  const v: Record<string, string> = {
    year_gz: chart.year_gz, yyg: chart.yin_yang_gender, napam: chart.menh_nap_am, mel, cuc: chart.cuc.name, cel, branch: menh.branch, mc, tc,
    mpol: pol(menh.branch_index), hpol: pol(menh.branch_index) === 'dương' ? 'âm' : 'dương', ypol: String(cf['chart.year_polarity'] ?? ''),
    season, state: seasonEl === mel ? 'Vượng' : seasonEl && GEN[seasonEl] === mel ? 'Tướng' : '', stem, ybr, sel: STEM_EL[stem] ?? '', bel: BRANCH_EL[ybr] ?? '',
  };
  const fired = new Set(findings.map(f => `${f.ruleId}|${f.subject}`));
  const verified = (id: string) => rmap.get(id)?.reviewStatus === 'verified';
  const card: OverviewFact[] = [];
  const p1: ProseSentence[] = [], p2: ProseSentence[] = [];
  const degreeIds = new Set([...plan.degree.up, ...plan.degree.down]);
  if (usable) {
    // ---- who and where: bản mệnh, cục, their relation ----
    say(p1, fill(m.pick('identity', L!.identity), v), 'tinh_toan');
    const relFired = fired.has('TV_KL_CASE_MENH_CUC_KHAC_MENH|palace:Mệnh') && verified('TV_KL_CASE_MENH_CUC_KHAC_MENH');
    const relText = L!.relation[chart.menh_cuc_relation];
    // the relation, and when Khảo Luận's reading of it fired, that reading in the same sentence (it is then not repeated with the độ số)
    if (relFired && L!.relation_book?.TV_KL_CASE_MENH_CUC_KHAC_MENH) say(p1, fill(m.pick('relation', L!.relation_book.TV_KL_CASE_MENH_CUC_KHAC_MENH), v), 'sach', ['TV_KL_CASE_MENH_CUC_KHAC_MENH']);
    else if (relText) say(p1, fill(m.pick('relation', relText), v), 'tinh_toan');
    card.push({ key: 'ban_menh', label: 'Bản mệnh', value: `${chart.menh_nap_am} (${mel})`, basis: 'tinh_toan', cites: [] },
      { key: 'cuc', label: 'Cục', value: `${chart.cuc.name} (${cel})`, basis: 'tinh_toan', cites: [] },
      { key: 'menh_cuc', label: 'Mệnh và Cục', value: chart.menh_cuc_relation, basis: relFired ? 'sach' : 'tinh_toan', cites: relFired ? rmap.get('TV_KL_CASE_MENH_CUC_KHAC_MENH')!.cites : [] },
      { key: 'am_duong', label: 'Âm dương', value: chart.yin_yang_gender, basis: 'tinh_toan', cites: [] });
    // ---- the Mệnh palace, star by star ----
    const mcfg = configClause(chart, menh);
    if (palaces) say(p1, fill(m.pick('menh', L!.menh), { ...v, config: mcfg.text }), 'tinh_toan', [], mcfg.cites);
    card.push({ key: 'menh', label: 'Mệnh', value: `${menh.stem} ${menh.branch}`, basis: 'tinh_toan', cites: [] });
    // ---- Thân ----
    // with `palaces` off the luận cung Mệnh chapter tells Thân cư (its position, the common reading, the Thân readings)
    if (palaces && than === menh) say(p1, fill(m.pick('than_same', L!.than_same), v), 'tinh_toan');
    else if (palaces) { const tcfg = configClause(chart, than); say(p1, fill(m.pick('than', L!.than), { ...v, palace: than.name, branch: than.branch, config: tcfg.text }), 'tinh_toan', [], tcfg.cites); }
    if (palaces) say(p1, m.pick('than_meaning', L!.than_meaning), 'pho_thong');
    const thanRules = !palaces ? [] : findings.filter(f => f.subject === `palace:${than.name}` && verified(f.ruleId) && isThanRule(rmap.get(f.ruleId)!.conditions))
      .map(f => f.ruleId).filter((id, i, a) => a.indexOf(id) === i).sort();
    for (const id of thanRules.slice(0, 2)) {
      const r = splitReading(rmap.get(id), k);
      if (r.claim) say(p1, fill(m.pick(`than_rule|${id}`, L!.than_rule), { palace: than.name, claim: r.claim }), 'sach', [id]);
    }
    card.push({ key: 'than', label: 'Thân cư', value: than === menh ? 'Mệnh (Thân Mệnh đồng cung)' : `${than.name} (${than.branch})`, basis: 'tinh_toan', cites: [] });
    // ---- Mệnh chủ, Thân chủ: the common table, named only ----
    say(p1, fill(m.pick('chu', L!.chu), v), 'pho_thong');
    card.push({ key: 'menh_chu', label: 'Mệnh chủ', value: mc, basis: 'pho_thong', cites: [] }, { key: 'than_chu', label: 'Thân chủ', value: tc, basis: 'pho_thong', cites: [] });

    // ---- độ số: each fired reading in its own sense, then the lean ----
    const ids = [...degreeIds].filter(id => verified(id) && !voiced.includes(id)).sort();
    const lines: Array<{ text: string; id: string }> = [];
    for (const id of ids) {
      const own = L!.degree[id];
      if (own) { lines.push({ id, text: fill(m.pick(`deg|${id}`, own), v) }); continue; }
      const r = splitReading(rmap.get(id), k);
      if (r.claim && r.cond) lines.push({ id, text: fill(m.pick(`degg|${id}`, L!.degree_generic), { cond: lowerFirst(r.cond), claim: r.claim }) });
    }
    if (lines.length) {
      lines.forEach((x, i) => say(p2, i === 0 ? `${m.pick('degree_lead', L!.degree_lead)} ${lowerFirst(x.text)}` : x.text, 'sach', [x.id], [], ['life.degree']));
      if (lines.length >= 2) say(p2, m.pick(`lean|${plan.degree.lean}`, L!.lean[plan.degree.lean]), 'he_thong', [], [], ['life.degree']);
    }
  }
  const paragraphs: ProseParagraph[] = ([['structure', p1], ['course', p2]] as Array<[ProseParagraph['role'], ProseSentence[]]>).filter(([, xs]) => xs.length)
    .map(([role, xs]) => ({ role, sentences: xs, text: xs.map(s => s.text).join(' ') }));
  const { issues, metrics } = validateProse(paragraphs, []);
  return {
    engine, kbVersion: k.version, chapter: 'tong_quan', palace: 'Tổng quan', title: 'Tổng quan lá số', draft: usable && L!.status !== 'approved',
    card, paragraphs, text: paragraphs.map(p => p.text).join('\n\n'), issues, metrics, pass: !issues.some(i => i.level === 'error'),
    evidence: { resolved: [], tensions: [], unused: [], rules, concepts: { 'life.degree': 'độ số' }, divergences: [] }, voiced,
  };
}
