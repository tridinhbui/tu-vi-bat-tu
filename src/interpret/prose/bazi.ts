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
import { deepBazi, type BaziDeep, type BaziDeepFrames } from './bazi_deep.ts';
import { withLead } from './luan.ts';
import { kinBazi, type KinFrames } from './bazi_kin.ts';

export interface BaziLibrary {
  status: 'draft' | 'approved';
  dm_first: string[]; dm_next: string[]; napam: string[]; skip: string[];
  topics: Record<string, { label: string; rules: string[] }>; topic_order: string[];
  direct: string[]; direct_same: string[];
  /** which report chapter tells which topic's judgements, and the frames of the per-chapter calculated sentences */
  chapter_topics?: Record<string, string[]>; frames?: Record<string, string[]>;
  /** the structure chapters (bazi_deep.ts): strength, điều hậu, phù ức, cách, luck pillars */
  deep?: BaziDeepFrames;
  /** prose-style B1/B7: the opening naming the four pillars, the paragraphs' lead-ins, the closing over the luck pillars */
  /** DEEP-BAZI-2 (prose/bazi_kin.ts): Tài, nghề, quan hệ and the years by 八字真宗 pp.50-65 */
  kin?: KinFrames;
  luan?: { frame: string[]; lead: Record<string, string[]>; summary: string[]; need: string[]; good: string[]; bad: string[]; level: Record<string, string> };
}
export type BaziChapterId = 'nhat-chu' | 'ngu-hanh' | 'su-nghiep' | 'quan-he' | 'dai-van' | 'cach-cuc' | 'luu-nien' | 'tong-ket';
const STEM_EL: Record<string, string> = { 'Giáp': 'Mộc', 'Ất': 'Mộc', 'Bính': 'Hỏa', 'Đinh': 'Hỏa', 'Mậu': 'Thổ', 'Kỷ': 'Thổ', 'Canh': 'Kim', 'Tân': 'Kim', 'Nhâm': 'Thủy', 'Quý': 'Thủy' };
const BRANCH_EL: Record<string, string> = { 'Tý': 'Thủy', 'Sửu': 'Thổ', 'Dần': 'Mộc', 'Mão': 'Mộc', 'Thìn': 'Thổ', 'Tỵ': 'Hỏa', 'Ngọ': 'Hỏa', 'Mùi': 'Thổ', 'Thân': 'Kim', 'Dậu': 'Kim', 'Tuất': 'Thổ', 'Hợi': 'Thủy' };
const PILLAR_VI: Record<string, string> = { year: 'năm', month: 'tháng', day: 'ngày', hour: 'giờ' };
const REL_VI: Record<string, string> = { stem_combine: 'can hợp', stem_clash: 'can xung', branch_six_combine: 'lục hợp', branch_clash: 'xung', branch_harm: 'hại', branch_destroy: 'phá',
  branch_penalty: 'hình', branch_self_penalty: 'tự hình', branch_triad_complete: 'tam hợp', branch_meeting_complete: 'tam hội', branch_semi_triad: 'bán hợp' };
const TEN_GROUP: Record<string, string> = { 'Tỉ Kiên': 'Tỉ Kiếp', 'Kiếp Tài': 'Tỉ Kiếp', 'Thực Thần': 'Thực Thương', 'Thương Quan': 'Thực Thương', 'Chính Tài': 'Tài', 'Thiên Tài': 'Tài',
  'Chính Quan': 'Quan Sát', 'Thất Sát': 'Quan Sát', 'Chính Ấn': 'Ấn', 'Thiên Ấn': 'Ấn' };
/** the ten gods' names keep their capitals inside a sentence ("Xét đến tiền bạc, Thiên Tài thấu can …") */
const TEN_GODS = new Set(Object.keys(TEN_GROUP));
const lowerName = (t: string) => [...TEN_GODS].some(g => t.startsWith(g) || t.toLowerCase().startsWith(g.toLowerCase())) ? t.charAt(0).toLocaleUpperCase('vi') + t.slice(1) : lowerFirst(t);
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
        const s = sentence(fill(m.pick(`${t}${i}`, i ? L!.direct_same : L!.direct), { topic: spec.label, cause: lowerName(cause), effect: lowerName(effect) }), f);
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
    const hasKin = !!(b as typeof b & { deep?: { kin?: unknown } }).deep?.kin && !!L!.kin;
    if (F.layout && stems.length && !hasKin) sn.push(calc(fill(m.pick('layout', F.layout), { stems: joinVi(stems.map(([k, g]) => `can trụ ${PILLAR_VI[k]} là ${g}`)) })));
    const wealthShown = stems.some(([, g]) => TEN_GROUP[g!] === 'Tài');
    const wealthHidden = K.some(k => pil[k].hidden.some(h => TEN_GROUP[h.ten_god] === 'Tài'));
    if (hasKin) { /* the kin layout says where Tài stands */ }
    else if (wealthShown && F.wealth_shown) sn.push(calc(m.pick('wshown', F.wealth_shown)));
    else if (wealthHidden && F.wealth_hidden) sn.push(calc(m.pick('whidden', F.wealth_hidden)));
    // quan hệ: the day branch and what it holds; the relations between pillars
    const qh: ProseSentence[] = [];
    // 八字真宗 p.57: the month branch is the marriage palace, the day branch the spouse palace
    if (F.day_branch) qh.push({ ...calc(fill(m.pick('dbr', F.day_branch), { day: pil.day.name, branch: pil.day.branch, mb: pil.month.branch, hidden: joinVi(pil.day.hidden.map(h => `${h.stem} (${h.ten_god})`)) })),
      trace: { move: 'ELABORATE', concepts: [], rules: [], cites: ['ZZ p.57', 'ZZ pp.19-20'], basis: 'tinh_toan' } });
    const rels = Object.entries(b!.relations ?? {}).flatMap(([kind, xs]) => xs.map(x => `${REL_VI[kind] ?? kind} giữa ${x.pillars.split('-').map(p => 'trụ ' + (PILLAR_VI[p] ?? p)).join(' và ')}`));
    // the relations between the natal pillars: a table lookup (八字真宗 pp.19-20), told as positions
    if (b!.relations) { const key = rels.length ? 'relations' : 'no_relations'; if (F[key]) { const t = calc(fill(m.pick(key, F[key]), { rels: joinVi(rels) })); qh.push({ ...t, trace: { ...t.trace, basis: 'tinh_toan', cites: ['ZZ pp.19-20'] } }); } }
    // đại vận: the luck pillar of the requested year and the next one
    const yr = chart.year?.year ?? new Date().getFullYear(), luck = b!.luck.filter(l => l.start_year != null);
    const ci = luck.reduce((a, l, i) => l.start_year! <= yr ? i : a, -1);
    const dv: ProseSentence[] = [];
    if (ci >= 0 && F.luck_now) {
      const cur = luck[ci], nx = luck[ci + 1];
      const t = calc(fill(m.pick('lnow', F.luck_now), { year: String(yr), name: cur.name, from: String(cur.start_year), god: cur.ten_god ?? '—',
        next: nx && F.luck_next ? fill(m.pick('lnext', F.luck_next), { name: nx.name, from: String(nx.start_year) }) : '' }));
      dv.push({ ...t, trace: { ...t.trace, basis: 'tinh_toan', cites: ['ZZ p.20'] } });
    } else if (luck[0] && F.luck_before) dv.push(calc(fill(m.pick('lbefore', F.luck_before), { name: luck[0].name, from: String(luck[0].start_year) })));
    chapters['nhat-chu'] = [...para('core', p1), ...para('support', topics('nhat-chu'))];
    chapters['ngu-hanh'] = para('core', ngu);
    chapters['su-nghiep'] = [...para('core', topics('su-nghiep')), ...para('support', sn)];
    chapters['quan-he'] = [...para('core', topics('quan-he')), ...para('support', qh)];
    chapters['dai-van'] = para('core', dv);
    chapters['cach-cuc'] = para('core', topics('cach-cuc'));
    // the structure analysis (facts.bazi.deep): appended to the chapters it belongs to, and to the whole reading in chapter order
    // 八字真宗 pp.50-65 by position and flow (prose/bazi_kin.ts), told before the structure analysis so the Tài layers know what was said
    const Dk = (b as typeof b & { deep?: { strength?: { dm_strong: boolean | null }; cach_tvh?: { status: string | null; van_xau: string[]; van_tot: string[]; yong: string[]; dominant: string | null; cach: string | null; verification?: string } } }).deep;
    const CTk = Dk?.cach_tvh?.status === 'ap_dung' ? Dk.cach_tvh : null;
    const kin = kinBazi(chart, m, L!.kin, rules, { gender: String(bf['chart.gender'] ?? '') || null, dm: b!.day_master, strong: Dk?.strength?.dm_strong ?? null,
      taiDm: Dk?.strength?.dm_strong === false && !!CTk && (CTk.van_xau.includes('Tài') || CTk.dominant === 'Tài'),
      cach: CTk ? CTk.cach : null, cachPartial: !!CTk && CTk.verification !== 'verified',
      taiRole: !CTk ? null : CTk.yong?.includes('Tài') ? 'yong' : CTk.van_tot?.includes('Tài') ? 'tot' : CTk.van_xau.includes('Tài') ? 'xau' : null });
    const deep0 = { ...kin };
    const deep = deepBazi(chart, k, m, L!.deep ? { ...L!.deep, kin: L!.kin } as NonNullable<BaziLibrary['deep']> : undefined, rules, { weigh: kin.weigh, work: kin.work });
    for (const [id, ps] of Object.entries(deep) as Array<[BaziChapterId, ProseParagraph[]]>) chapters[id] = [...(chapters[id] ?? []), ...ps];
    for (const id of ['nhat-chu', 'cach-cuc', 'ngu-hanh', 'su-nghiep', 'quan-he', 'dai-van', 'luu-nien', 'tong-ket'] as const) paragraphs.push(...(id === 'su-nghiep' || id === 'quan-he' ? deep0[id] : []), ...(deep[id] ?? []));
    for (const id of ['su-nghiep', 'quan-he'] as const) chapters[id] = [...(chapters[id] ?? []), ...deep0[id]];
    if (L!.luan) luanBazi(chart, k, m, L!.luan, chapters, { p1, deep, topicsOf: topics, dv, ngu, sn, qh, kin });
    for (const id of Object.keys(chapters) as BaziChapterId[]) if (!chapters[id]!.length) delete chapters[id];
  }
  const { issues, metrics } = validateProse(paragraphs, []);
  return {
    engine, kbVersion: k.version, chapter: 'bat_tu', palace: 'Bát Tự', schema: 'BAT_TU', order: ['ANCHOR'], draft: usable && L!.status !== 'approved',
    paragraphs, text: paragraphs.map(p => p.text).join('\n\n'), issues, metrics, pass: !issues.some(i => i.level === 'error'),
    evidence: { resolved: [], tensions: [], unused: [], rules, concepts: {}, divergences: [],
      // what the reading leaves out, as data (the report renders it): Track B shows it in the footer
      limits: ['thành bại của cách theo bảng riêng của bộ máy và phép phù ức: chưa có trang sách, không đưa vào văn',
        'ý nghĩa của hợp, xung, hình, hại, phá giữa vận, năm và tứ trụ: Bát Tự Chân Tông tr.19-20 chỉ in bảng, nên văn chỉ nêu vị trí',
        'hệ quả của các thần sát nhóm hung: chỉ nêu tên và vị trí',
        'chỗ bảng dụng thần theo cách và bảng điều hậu của Thiệu Vĩ Hoa cho kết quả khác nhau: kết luận có điều kiện, không xếp bảng nào trên bảng nào',
        'một năm được tính vào đại vận đang hiệu lực ở giữa năm Bát Tự (quy ước hiển thị); ngày đổi vận chính xác có ở dải đại vận',
        'lưu nguyệt',
        ...(P?.drafts.length ? [`${P.drafts.length} nhận định Bát Tự còn ở dạng nháp, không đưa vào văn`] : [])] },
    chapters,
  };
}

/** prose-style B1/B7 on the Bát Tự chapters, as on the luận cung ones: the opening that names the four pillars with their nạp âm and the
 *  day master's season, strength and điều hậu need, a bold lead-in on each paragraph, the manual's limiting judgements after the plain ones
 *  with a turn between them, the luck pillars and the years (lưu niên), and a closing along the timeline (bazi_deep.ts). */
function luanBazi(chart: ChartInput, k: Knowledge, m: Micro, LU: NonNullable<BaziLibrary['luan']>, chapters: BaziProse['chapters'],
  parts: { p1: ProseSentence[]; deep: Partial<Record<BaziChapterId, ProseParagraph[]>>; topicsOf: (id: string) => ProseSentence[]; dv: ProseSentence[]; ngu: ProseSentence[];
    sn: ProseSentence[]; qh: ProseSentence[]; kin: ReturnType<typeof kinBazi> }) {
  const b = chart.bazi!, pil = b.pillars, D = (b as typeof b & { deep?: BaziDeep | null }).deep;
  const rmap = new Map(k.rules.map(r => [r.id, r]));
  const say = (text: string, basis: 'tinh_toan' | 'he_thong', move: 'ANCHOR' | 'VALUE', step: string): ProseSentence => { const t = finish(text); m.said(t); return { text: t, trace: { move, concepts: [], rules: [], cites: [], basis, step } }; };
  // a judgement that opens by naming its topic ("Chuyện nghề nghiệp cũng có dấu hiệu riêng: …", "Về dương nhẫn, …") drops that opening
  // under a lead-in that already names it
  const labels = Object.values((k.prose?.bazi as BaziLibrary).topics).map(t => t.label);
  // (2026-10-23) a paragraph's first sentence never opens on a "more of the same" connective ("Thêm nữa, …") once the order put it first
  const unTopic = (t: string) => { t = t.replace(/^(Thêm nữa|Ngoài ra|Cũng vậy|Bên cạnh đó|Hơn nữa),\s*/u, '');
    const m2 = t.match(/^([^,:]{0,48})[,:]\s+/); return m2 && labels.some(x => m2[1].toLowerCase().includes(x)) ? t.slice(m2[0].length) : t; };
  const lead = (key: string, p: ProseParagraph): ProseParagraph => {
    const l = LU.lead[key]?.length ? m.pick(`btlead|${key}`, LU.lead[key]) : '';
    if (!l || !p.sentences.length) return p;
    const xs = [{ ...p.sentences[0], text: withLead(l, unTopic(p.sentences[0].text), TEN_GODS) }, ...p.sentences.slice(1)];
    return { ...p, lead: l, topic: key, sentences: xs, text: xs.map(x => x.text).join(' ') };
  };
  // the manual's limiting judgements after its plain ones, the first of them turned with a contrast
  const turned = (xs: ProseSentence[], key: string) => {
    const eff = (s: ProseSentence) => rmap.get(s.trace.rules[0])?.consequences[0]?.effect;
    const plain = xs.filter(s => eff(s) !== 'limit'), lim = xs.filter(s => eff(s) === 'limit');
    if (!plain.length || !lim.length) return xs;
    const c = m.conn('contrast', `bt|turn|${key}`);
    const body = lim[0].text.replace(/^(Thêm nữa|Ngoài ra|Cũng vậy|Bên cạnh đó|Hơn nữa|Đồng thời),\s*/u, '');
    const low = [...TEN_GODS].some(g => body.startsWith(g)) ? body : body.charAt(0).toLocaleLowerCase('vi') + body.slice(1);
    return [...plain, ...(c ? [{ ...lim[0], text: `${c} ${low}` }] : [lim[0]]), ...lim.slice(1)];
  };
  const P = (role: ProseParagraph['role'], xs: ProseSentence[]): ProseParagraph[] => xs.length ? [{ role, sentences: xs, text: xs.map(x => x.text).join(' ') }] : [];
  const deepOf = (id: BaziChapterId, key: string | null) => (parts.deep[id] ?? []).map((p, i) => i === 0 && key ? lead(key, p) : p);
  // ---- B1: the four pillars with their nạp âm (八字真宗 pp.20-21; the year and day pillars' from the older facts when the analysis is absent),
  // then the frame's second sentence: season, TVH vượng / nhược, điều hậu ----
  const nap: Record<string, string> = D?.pillars ? Object.fromEntries((['year', 'month', 'day', 'hour'] as const).map(x => [x, D.pillars![x].nap_am]))
    : { year: chart.menh_nap_am ?? '', day: String((b.base.chart as Record<string, unknown>)['bazi.day_nap_am'] ?? '') };
  const pillars = (['year', 'month', 'day', 'hour'] as const).map(x => `${PILLAR_VI[x]} ${pil[x].name}${nap[x] ? ` (${nap[x]})` : ''}`);
  const frame = say(fill(m.pick('btframe', LU.frame), { dm: b.day_master, el: b.day_master_element, mb: pil.month.branch, pillars: joinVi(pillars) }), 'tinh_toan', 'ANCHOR', 'frame:bat_tu');
  frame.trace.cites = ['ZZ pp.20-21'];                   // the nạp âm table, whether the names come from the analysis or the older facts
  const nc = parts.deep['nhat-chu'] ?? [], frame2 = nc.filter(p => p.role === 'structure').flatMap(p => p.sentences), ncRest = nc.filter(p => p.role !== 'structure');
  const cc = parts.deep['cach-cuc'] ?? [], ss = cc.filter(p => p.topic === 'than_sat'), ssNums = cc.filter(p => p.topic === 'than_sat_sau'), ccRest = cc.filter(p => p.topic !== 'than_sat' && p.topic !== 'than_sat_sau');
  const leadAll = (key: string, ps: ProseParagraph[]) => ps.map((p, i) => i === 0 ? lead(key, p) : p);
  // REVIEW-19 W6: with the structure analysis, the four pillars and their nạp âm go to the Số liệu fold; the chapter opens on the season and điều hậu
  const nums = (title: string, xs: ProseSentence[]): ProseParagraph[] => xs.length ? [{ role: 'support', sentences: xs, text: xs.map(x => x.text).join(' '), depth: 'sau', depthTitle: `Số liệu · ${title}` }] : [];
  const pillarsNums = frame2.length ? nums('tứ trụ', [frame]) : [];
  chapters['nhat-chu'] = [...P('structure', frame2.length ? frame2 : [frame]), ...P('core', parts.p1).map(p => lead('nhat_chu', p)), ...P('support', turned(parts.topicsOf('nhat-chu'), 'nc')).map(p => lead('study', p)),
    ...leadAll('strength', ncRest), ...pillarsNums];
  const nh = parts.deep['ngu-hanh'] ?? [], kn = parts.kin['ngu-hanh'];
  // REVIEW-19 W6: the strong and weak groups in words and what the books say of the person by them; the counts and degrees in Số liệu
  if (kn.length) {
    const nNums = nh.find(p => p.depthTitle?.startsWith('Số liệu'));
    const numsP = nums('ngũ hành theo độ', [...parts.ngu, ...(nNums?.sentences ?? [])]);
    chapters['ngu-hanh'] = [...kn.map((p, i) => i === 0 ? lead('ngu_hanh', p) : p), ...numsP, ...nh.filter(p => p.depth === 'sau' && p !== nNums)];
  } else chapters['ngu-hanh'] = [...P('core', [...parts.ngu, ...nh.filter(p => p.depth !== 'sau').flatMap(p => p.sentences)]).map(p => lead('ngu_hanh', p)), ...nh.filter(p => p.depth === 'sau')];
  // sự nghiệp & quan hệ (DEEP-BAZI-2): the short reading (bazi_kin main paragraphs, the manual's other judgements, the computed positions),
  // the Tài layers, then the Đọc sâu paragraphs
  const kMain = (id: 'su-nghiep' | 'quan-he') => parts.kin[id].filter(p => p.depth !== 'sau'), kDeep = (id: 'su-nghiep' | 'quan-he') => parts.kin[id].filter(p => p.depth === 'sau');
  const snTop = P('core', turned(parts.topicsOf('su-nghiep'), 'sn'));
  chapters['su-nghiep'] = [...kMain('su-nghiep'), ...(kMain('su-nghiep').length ? snTop : snTop.map(p => lead('work', p))), ...P('support', parts.sn), ...deepOf('su-nghiep', 'tai_layers'), ...kDeep('su-nghiep')];
  // the manual's older marriage judgements and the new ones in one paragraph under one lead-in
  const unlead = (p: ProseParagraph): ProseSentence[] => p.lead && p.sentences[0].text.startsWith(`${p.lead}, `)
    ? [{ ...p.sentences[0], text: p.sentences[0].text.slice(p.lead.length + 2).replace(/^./u, c => c.toLocaleUpperCase('vi')) }, ...p.sentences.slice(1)] : p.sentences;
  const kq = kMain('quan-he'), km = kq.find(p => p.topic === 'kin_marriage');
  // siblings have their own paragraph (bazi_kin) when the chart has a sibling star: the lead-in then names marriage only
  let qhTop = P('core', turned(parts.topicsOf('quan-he'), 'qh')).map(p => lead(kq.some(x => x.topic === 'kin_family') && LU.lead.marriage ? 'marriage' : 'kin', p));
  if (qhTop.length && km) { const xs = [...qhTop[0].sentences, ...unlead(km)]; qhTop = [{ ...qhTop[0], sentences: xs, text: xs.map(x => x.text).join(' ') }, ...qhTop.slice(1)]; }
  // REVIEW-19 W6: the spouse palace's hidden stems and the relations between the pillars are positions: in Số liệu when the kin reading tells the chapter
  chapters['quan-he'] = [...qhTop, ...kq.filter(p => !(qhTop.length && p === km)), ...(kq.length ? nums('cung phối ngẫu và quan hệ giữa các trụ', parts.qh) : P('support', parts.qh)),
    ...deepOf('quan-he', 'pillar_kin'), ...kDeep('quan-he')];
  // the cách chapter in the frame of plan step 4: the first paragraph under the chapter's lead-in, each later part under its own
  // (điểm tựa và giới hạn, điều hậu, chỗ hai cách xét khác nhau, kết luận); the sources are each sentence's trace
  const leadParts = (ps: ProseParagraph[]) => ps.map((p, i) => { const pt = (p as ProseParagraph & { part?: string }).part;
    return i === 0 ? lead('cach', p) : pt && LU.lead[`part_${pt}`] ? lead(`part_${pt}`, p) : p; });
  chapters['cach-cuc'] = [...leadParts(ccRest), ...P('support', [...turned(parts.topicsOf('cach-cuc'), 'cc'), ...ss.flatMap(p => p.sentences)]).map(p => lead('blade', p)), ...ssNums];
  // REVIEW-19 W6: with the structure analysis, the chapter opens on what each group stands for (its first paragraph) instead of the current pillar,
  // which the pillar's own paragraph names
  const dvOpen = (parts.deep['dai-van'] ?? [])[0]?.role === 'structure';
  chapters['dai-van'] = dvOpen ? deepOf('dai-van', 'dai_van') : [...P('core', parts.dv).map(p => lead('dai_van', p)), ...deepOf('dai-van', null)];
  chapters['luu-nien'] = leadAll('luu_nien', parts.deep['luu-nien'] ?? []);
  chapters['tong-ket'] = leadAll('tong_ket', parts.deep['tong-ket'] ?? []);
}
