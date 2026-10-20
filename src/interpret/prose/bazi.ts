// Bát Tự reader prose (prose plan P7), on the same parts as the Tử Vi chapters: rule inference (prepareBazi, the engine's 'bat_tu' run),
// Micro for variant choice, subject rotation and opener avoidance, validateProse for the blocking checks, and the evidence panel format.
// Only verified rules that fired are voiced. Paragraph 1: the day master's character (八字真宗 pp.25-26) and the day pillar's nạp âm
// (pp.31-32). Paragraph 2: the manual's direct judgements (pp.50-74), each split into its effect and the chart condition that causes it.
// Strength, useful god and structure are left out and said so in evidence.limits: no verified rule speaks of them.
import { baziCore, prepareBazi } from '../bazi.ts';
import type { ChartInput, Finding, Knowledge } from '../types.ts';
import { Micro, finish, lowerFirst } from './micro.ts';
import type { ProseParagraph, ProseSentence } from './realize.ts';
import { validateProse } from './validate.ts';
import { deepBazi, type BaziCards, type BaziDeepFrames } from './bazi_deep.ts';

export interface BaziLibrary {
  status: 'draft' | 'approved';
  dm_first: string[]; dm_next: string[]; napam: string[]; skip: string[];
  topics: Record<string, { label: string; rules: string[] }>; topic_order: string[];
  direct: string[]; direct_same: string[];
  /** which report chapter tells which topic's judgements, and the frames of the per-chapter calculated sentences */
  chapter_topics?: Record<string, string[]>; frames?: Record<string, string[]>;
  /** the structure chapters (bazi_deep.ts): strength, điều hậu, phù ức, cách, luck pillars */
  deep?: BaziDeepFrames;
}
export type BaziChapterId = 'nhat-chu' | 'ngu-hanh' | 'su-nghiep' | 'quan-he' | 'dai-van' | 'cach-cuc';
const STEM_EL: Record<string, string> = { 'Giáp': 'Mộc', 'Ất': 'Mộc', 'Bính': 'Hỏa', 'Đinh': 'Hỏa', 'Mậu': 'Thổ', 'Kỷ': 'Thổ', 'Canh': 'Kim', 'Tân': 'Kim', 'Nhâm': 'Thủy', 'Quý': 'Thủy' };
const BRANCH_EL: Record<string, string> = { 'Tý': 'Thủy', 'Sửu': 'Thổ', 'Dần': 'Mộc', 'Mão': 'Mộc', 'Thìn': 'Thổ', 'Tỵ': 'Hỏa', 'Ngọ': 'Hỏa', 'Mùi': 'Thổ', 'Thân': 'Kim', 'Dậu': 'Kim', 'Tuất': 'Thổ', 'Hợi': 'Thủy' };
const PILLAR_VI: Record<string, string> = { year: 'năm', month: 'tháng', day: 'ngày', hour: 'giờ' };
const REL_VI: Record<string, string> = { stem_combine: 'can hợp', stem_clash: 'can xung', branch_six_combine: 'lục hợp', branch_clash: 'xung', branch_harm: 'hại', branch_destroy: 'phá',
  branch_penalty: 'hình', branch_self_penalty: 'tự hình', branch_triad_complete: 'tam hợp', branch_meeting_complete: 'tam hội' };
const TEN_GROUP: Record<string, string> = { 'Tỉ Kiên': 'Tỉ Kiếp', 'Kiếp Tài': 'Tỉ Kiếp', 'Thực Thần': 'Thực Thương', 'Thương Quan': 'Thực Thương', 'Chính Tài': 'Tài', 'Thiên Tài': 'Tài',
  'Chính Quan': 'Quan Sát', 'Thất Sát': 'Quan Sát', 'Chính Ấn': 'Ấn', 'Thiên Ấn': 'Ấn' };
const joinVi = (xs: string[]) => xs.length <= 1 ? (xs[0] ?? '') : xs.slice(0, -1).join(', ') + ' và ' + xs[xs.length - 1];

const fill = (t: string, v: Record<string, string>) => t.replace(/\{([A-Za-z0-9_]+)\}/g, (m, k) => v[k] ?? m);
/** "hôn nhân êm đẹp (nguyệt lệnh được hợp) [PDF p.57]" -> effect "hôn nhân êm đẹp", cause "nguyệt lệnh được hợp" (the last parenthesis) */
export function splitDirect(reading: string): { effect: string; cause: string } {
  const r = reading.replace(/\s*\[[^\]]*\]\s*$/, '').trim();
  const m = r.match(/^(.*?)\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$/);
  if (!m) return { effect: r, cause: '' };
  // a second parenthesis before the cause names the ten gods of the effect: "(Thực Thần, Thương Quan) (thập thần …)"
  const effect = m[1].replace(/\s*\([^()]*\)\s*$/, '').trim();
  const cause = m[2].replace(/:\s*'[^']*'/, '').replace(/\s*\(tính theo[^)]*\)/, '').trim();
  return { effect, cause };
}

export interface BaziProse {
  engine: string; kbVersion: string; chapter: 'bat_tu'; palace: string; schema: string; order: string[]; draft: boolean;
  paragraphs: ProseParagraph[]; text: string; issues: ReturnType<typeof validateProse>['issues']; metrics: ReturnType<typeof validateProse>['metrics']; pass: boolean;
  evidence: { resolved: []; tensions: []; unused: string[]; rules: Record<string, { reading: string; cites: string[]; verified: boolean }>; concepts: Record<string, string>;
    divergences: []; limits: string[] };
  /** the same reading split by report chapter, plus calculated sentences that tell the chapter's facts in words (basis he_thong) */
  chapters: Partial<Record<BaziChapterId, ProseParagraph[]>>;
}

export function proseBazi(chart: ChartInput, k: Knowledge, seed: string, engine: string, allowDraft: boolean): BaziProse {
  const L = k.prose?.bazi as BaziLibrary | undefined, P = prepareBazi(chart, k), b = chart.bazi;
  const usable = !!L && !!P && !!b && (allowDraft || L.status === 'approved');
  const m = new Micro(`${seed}|bat_tu`, k.prose!.connectives, k.prose!.frames);
  const rmap = new Map(k.rules.map(r => [r.id, r]));
  const rules: BaziProse['evidence']['rules'] = {};
  const S = () => lowerFirst(m.subject());
  const raw = (f: Finding) => (rmap.get(f.ruleId)?.reading ?? k.claims[f.claim] ?? f.claim);
  const sentence = (text: string, f: Finding): ProseSentence => {
    const r = rmap.get(f.ruleId)!, t = finish(text); m.said(t);
    rules[f.ruleId] = { reading: raw(f).replace(/\s*\[[^\]]*\]\s*$/, ''), cites: r.cites, verified: r.reviewStatus === 'verified' };
    return { text: t, trace: { move: 'ANCHOR', concepts: [], rules: [f.ruleId], cites: [...r.cites].sort(), basis: 'sach' } };
  };
  const paragraphs: ProseParagraph[] = [], chapters: BaziProse['chapters'] = {};
  if (usable) {
    const ver = P!.findings.filter(f => f.basis === 'verified' && !L!.skip.includes(f.ruleId));
    const cat = (c: string) => ver.filter(f => rmap.get(f.ruleId)?.category === c).sort((x, y) => x.ruleId.localeCompare(y.ruleId));
    const base = { dm: b!.day_master, el: b!.day_master_element, day: b!.pillars.day.name, napam: String((b!.base.chart as Record<string, unknown>)['bazi.day_nap_am'] ?? '') };
    const p1: ProseSentence[] = [];
    cat('day_master_character').forEach((f, i) => p1.push(sentence(fill(m.pick(`dm${i}`, i ? L!.dm_next : L!.dm_first), { ...base, core: baziCore(raw(f).replace(/\s*\[[^\]]*\]/g, '')), S: S() }), f)));
    for (const f of cat('day_pillar_nap_am')) p1.push(sentence(fill(m.pick('napam', L!.napam), { ...base, core: baziCore(raw(f).replace(/\s*\[[^\]]*\]/g, '')), S: S() }), f));
    if (p1.length) paragraphs.push({ role: 'core', sentences: p1, text: p1.map(s => s.text).join(' ') });
    // the manual's condition names a set ("nguyệt kiến là Tài, Quan hoặc Ấn"); the sentence names what this chart has
    const bf = b!.base.chart as Record<string, unknown>, pil = b!.pillars;
    const actual = (c: string) => c
      .replace(/^nguyệt kiến là .*$/, `nguyệt kiến là ${bf['bazi.month_main_god']}`)
      .replace(/^nhật chi là .*$/, `nhật chi là ${bf['bazi.day_main_god']}`)
      .replace(/^can tháng là .*$/, `can tháng là ${pil.month.stem_ten_god}`)
      .replace(/^thập thần của can trụ giờ.*$/, `can trụ giờ là ${pil.hour.stem_ten_god}`);
    const p2: ProseSentence[] = [], byTopic: Record<string, ProseSentence[]> = {};
    for (const t of L!.topic_order) {
      const spec = L!.topics[t];
      const fs = ver.filter(f => spec.rules.some(p => f.ruleId.startsWith(p))).sort((x, y) => x.ruleId.localeCompare(y.ruleId));
      fs.forEach((f, i) => {
        const { effect, cause: generic } = splitDirect(raw(f));
        if (!generic) return;
        const cause = actual(generic);
        const s = sentence(fill(m.pick(`${t}${i}`, i ? L!.direct_same : L!.direct), { topic: spec.label, cause: lowerFirst(cause), effect: lowerFirst(effect) }), f);
        p2.push(s); (byTopic[t] ??= []).push(s);
      });
    }
    if (p2.length) paragraphs.push({ role: 'support', sentences: p2, text: p2.map(s => s.text).join(' ') });

    // ---- per chapter: the topic judgements where they belong, and the chapter's facts told as sentences ----
    const F = L!.frames ?? {}, calc = (text: string): ProseSentence => { const t = finish(text); m.said(t); return { text: t, trace: { move: 'ELABORATE', concepts: [], rules: [], cites: [], basis: 'he_thong' } }; };
    const para = (role: ProseParagraph['role'], xs: ProseSentence[]): ProseParagraph[] => xs.length ? [{ role, sentences: xs, text: xs.map(x => x.text).join(' ') }] : [];
    const topics = (id: string) => (L!.chapter_topics?.[id] ?? []).flatMap(t => byTopic[t] ?? []);
    const K = ['year', 'month', 'day', 'hour'] as const;
    // ngũ hành: the eight characters by element (stem and main element of each branch), and the elements none of them has
    const els = K.flatMap(k => [STEM_EL[pil[k].stem], BRANCH_EL[pil[k].branch]]).filter(Boolean);
    const count = ['Mộc', 'Hỏa', 'Thổ', 'Kim', 'Thủy'].map(e => [e, els.filter(x => x === e).length] as const);
    const missing = count.filter(([, n]) => !n).map(([e]) => e);
    const ngu: ProseSentence[] = F.chars ? [calc(fill(m.pick('chars', F.chars), { counts: joinVi(count.filter(([, n]) => n).map(([e, n]) => `${n} chữ ${e}`)),
      missing: missing.length && F.missing ? fill(m.pick('missing', F.missing), { els: joinVi(missing) }) : '' }))] : [];
    // sự nghiệp: which ten-god groups the stems show, and whether Tài shows at all
    const stems = (['year', 'month', 'hour'] as const).map(k => [k, pil[k].stem_ten_god] as const).filter(([, g]) => g);
    const sn: ProseSentence[] = [];
    if (F.layout && stems.length) sn.push(calc(fill(m.pick('layout', F.layout), { stems: joinVi(stems.map(([k, g]) => `can trụ ${PILLAR_VI[k]} là ${g}`)) })));
    const wealthShown = stems.some(([, g]) => TEN_GROUP[g!] === 'Tài');
    const wealthHidden = K.some(k => pil[k].hidden.some(h => TEN_GROUP[h.ten_god] === 'Tài'));
    if (wealthShown && F.wealth_shown) sn.push(calc(m.pick('wshown', F.wealth_shown)));
    else if (wealthHidden && F.wealth_hidden) sn.push(calc(m.pick('whidden', F.wealth_hidden)));
    // quan hệ: the day branch and what it holds; the relations between pillars
    const qh: ProseSentence[] = [];
    if (F.day_branch) qh.push(calc(fill(m.pick('dbr', F.day_branch), { day: pil.day.name, branch: pil.day.branch, hidden: joinVi(pil.day.hidden.map(h => `${h.stem} (${h.ten_god})`)) })));
    const rels = Object.entries(b!.relations ?? {}).flatMap(([kind, xs]) => xs.map(x => `${REL_VI[kind] ?? kind} giữa ${x.pillars.split('-').map(p => 'trụ ' + (PILLAR_VI[p] ?? p)).join(' và ')}`));
    if (b!.relations) { const key = rels.length ? 'relations' : 'no_relations'; if (F[key]) qh.push(calc(fill(m.pick(key, F[key]), { rels: joinVi(rels) }))); }
    // đại vận: the luck pillar of the requested year and the next one
    const yr = chart.year?.year ?? new Date().getFullYear(), luck = b!.luck.filter(l => l.start_year != null);
    const ci = luck.reduce((a, l, i) => l.start_year! <= yr ? i : a, -1);
    const dv: ProseSentence[] = [];
    if (ci >= 0 && F.luck_now) {
      const cur = luck[ci], nx = luck[ci + 1];
      dv.push(calc(fill(m.pick('lnow', F.luck_now), { year: String(yr), name: cur.name, from: String(cur.start_year), god: cur.ten_god ?? '—',
        next: nx && F.luck_next ? fill(m.pick('lnext', F.luck_next), { name: nx.name, from: String(nx.start_year) }) : '' })));
    } else if (luck[0] && F.luck_before) dv.push(calc(fill(m.pick('lbefore', F.luck_before), { name: luck[0].name, from: String(luck[0].start_year) })));
    chapters['nhat-chu'] = [...para('core', p1), ...para('support', topics('nhat-chu'))];
    chapters['ngu-hanh'] = para('core', ngu);
    chapters['su-nghiep'] = [...para('core', topics('su-nghiep')), ...para('support', sn)];
    chapters['quan-he'] = [...para('core', topics('quan-he')), ...para('support', qh)];
    chapters['dai-van'] = para('core', dv);
    chapters['cach-cuc'] = para('core', topics('cach-cuc'));
    // the structure analysis (facts.bazi.deep): appended to the chapters it belongs to, and to the whole reading in chapter order
    const deep = deepBazi(chart, k, m, L!.deep, (k.prose?.phoThong as { bazi?: BaziCards } | undefined)?.bazi, rules);
    for (const [id, ps] of Object.entries(deep) as Array<[BaziChapterId, ProseParagraph[]]>) chapters[id] = [...(chapters[id] ?? []), ...ps];
    for (const id of ['nhat-chu', 'cach-cuc', 'ngu-hanh', 'su-nghiep', 'quan-he', 'dai-van'] as const) paragraphs.push(...(deep[id] ?? []));
    for (const id of Object.keys(chapters) as BaziChapterId[]) if (!chapters[id]!.length) delete chapters[id];
  }
  const { issues, metrics } = validateProse(paragraphs, []);
  return {
    engine, kbVersion: k.version, chapter: 'bat_tu', palace: 'Bát Tự', schema: 'BAT_TU', order: ['ANCHOR'], draft: usable && L!.status !== 'approved',
    paragraphs, text: paragraphs.map(p => p.text).join('\n\n'), issues, metrics, pass: !issues.some(i => i.level === 'error'),
    evidence: { resolved: [], tensions: [], unused: [], rules, concepts: {}, divergences: [],
      limits: ['cách cục và phép phù ức: định nghĩa của hệ thống, chưa đối chiếu sách (câu ghi \'phổ thông\'); vượng/nhược theo điểm Thiệu Vĩ Hoa và điều hậu theo bảng Thiệu Vĩ Hoa đã đối chiếu',
        ...(P?.drafts.length ? [`${P.drafts.length} nhận định Bát Tự còn ở dạng nháp, không đưa vào văn`] : [])] },
    chapters,
  };
}
