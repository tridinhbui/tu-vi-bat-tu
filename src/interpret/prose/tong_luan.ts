// Tổng luận Tử Vi (review of the live report, 2026-10-23, point 19: "thiếu kết luận tổng hợp có thứ bậc ưu tiên"). The report's last
// chapter. It adds no reading: every sentence is the system's tổng hợp (he_thong) over what the chapters concluded —
//   - the life domains ranked by their one report-wide verdict (reason/ledger.ts): the strongest named with the reading it rests on, the
//     weakest with its ground, the rest in order; a domain whose two sides are even is said to be unranked; health is never ranked;
//   - the đại hạn on the system indices (indices.ts, a labelled convention, the same levels as the period chart): the highest and lowest
//     decade, the largest change between two decades, the current one;
//   - one lời khuyên chung (loi_khuyen) naming the strongest and the weakest domain.
import type { ChartInput, Knowledge } from '../types.ts';
import { Micro, finish } from './micro.ts';
import type { ProseParagraph, ProseSentence, SentenceTrace } from './realize.ts';
import { validateProse, type ProseIssue, type ProseMetrics } from './validate.ts';
import { buildLedger, verdictKey, type DomainVerdict, type Ledger, type LedgerItem } from '../reason/ledger.ts';
import { computeIndices, type IndexNorms } from '../indices.ts';
import { infer } from './chapter.ts';
import { bookLean } from './vanhan.ts';
import norms from '../../../engine/data/kg/index_norms.json' with { type: 'json' };

export interface TongLuanLib {
  status: string; lead: string[]; best: string[]; worst: string[]; middle: string[]; same: string[]; open: string[]; health: string[];
  best_multi?: string[]; worst_multi?: string[]; pair?: string[]; best_off?: string[];
  dec_best: string[]; dec_worst: string[]; turn_up: string[]; turn_down: string[]; current: string[]; advice: string[];
  /** the lowest decade whose book side leans good; a ranked domain whose core palace the twelve-palace chart reads the other way */
  dec_worst_rel?: string[]; radar_best?: string[]; radar_worst?: string[];
}
export interface ProseTongLuan {
  engine: string; kbVersion: string; chapter: 'tong_luan'; palace: 'Tổng luận'; title: string; draft: boolean;
  paragraphs: ProseParagraph[]; text: string; issues: ProseIssue[]; metrics: ProseMetrics; pass: boolean;
  evidence: { resolved: []; tensions: []; unused: []; rules: Record<string, never>; concepts: Record<string, string>; divergences: [] };
}

/** a verdict's place on the ranking (higher = stronger); null: not ranked (two even sides, nothing to conclude, health) */
const RANK: Record<string, number> = { thuan: 4, 'co_dieu_kien+': 3, 'nghieng_ve+': 2.5, hai_mat: 2, 'giam_nhe-': 1, 'nghieng_ve-': 0.5, 'co_dieu_kien-': 0.5, 'tro_ngai-': 0, tro_ngai: 0 };
const rankOf = (v: DomainVerdict) => RANK[verdictKey(v)] ?? RANK[v.verdict] ?? null;
const fill = (t: string, v: Record<string, string>) => t.replace(/\{([A-Za-z_]+)\}/g, (m, k) => v[k] ?? m);
const joinVi = (xs: string[]) => xs.length <= 1 ? xs.join('') : `${xs.slice(0, -1).join(', ')} và ${xs.at(-1)}`;
const NORMS = norms as IndexNorms;
/** the life-wide ranking of đại hạn reads the decades that start before this age (owner decision Q4 2026-11-07) */
export const RANK_AGE_LIMIT = 80;

/** what a domain's conclusion stands on: the heavier side's reading (weighed), else the side's most fundamental reading, by its stars; with the
 *  cause it names (INV-2: every "do / nền ở X" traces to the rule and the stars where they stand) */
function groundOf(chart: ChartInput, v: DomainVerdict): { text: string; cause?: { domain: string; ruleId: string; stars: Array<{ name: string; palace: string }> } } {
  const core = v.limits[0]?.palace ?? v.supports[0]?.palace;
  const side = v.weigh ? v.weigh.heavy : (v.base === '-' ? v.neg : v.pos).concat(v.base === '-' ? [] : v.mixed)
    .sort((a, b) => Number(!!a.grave) - Number(!!b.grave) || Number(b.palace === core) - Number(a.palace === core) || a.seat.tier - b.seat.tier || b.rarity - a.rarity || (a.ruleId < b.ruleId ? -1 : 1))[0] as LedgerItem | undefined;
  if (side?.at?.length) {
    // a star is named where it stands: a borrowed chính tinh of a vô chính diệu palace, or a Hóa, is said with its own palace (INV-1)
    const where = (a: { name: string; palace: string }) => {
      const t = chart.tu_hoa[a.name], own = t ? chart.palaces.find(p => p.branch_index === t.branch)?.name : chart.palaces.find(p => p.stars.includes(a.name) || p.major_stars.includes(a.name))?.name;
      return own ?? a.palace;
    };
    const by = new Map<string, { names: string[]; to?: string }>();
    for (const a of side.at) { const q = where(a), e = by.get(q) ?? by.set(q, { names: [], ...(q !== a.palace ? { to: a.palace } : {}) }).get(q)!; if (!e.names.includes(a.name)) e.names.push(a.name); }
    const shown = [...by].slice(0, 2);
    return { text: joinVi(shown.map(([p, e]) => `${joinVi(e.names)} ở cung ${p}${e.to ? ` chiếu sang cung ${e.to}` : ''}`)),
      cause: { domain: v.id, ruleId: side.ruleId, stars: shown.flatMap(([p, e]) => e.names.map(name => ({ name, palace: p }))) } };
  }
  const el = (v.base === '-' ? v.limits : v.supports)[0];
  const name = el ? el.star ?? el.hoa ?? (el.kind === 'tuan' ? 'Tuần' : el.kind === 'triet' ? 'Triệt' : el.kind === 'hoa_ky' ? 'Hóa Kỵ' : '') : '';
  // a borrowed chính tinh (vô chính diệu) is named where it stands, reaching the palace it is read for
  const own = el?.star ? chart.palaces.find(p => p.stars.includes(el.star!) || p.major_stars.includes(el.star!))?.name : undefined;
  const pal = own ?? el?.palace ?? '';
  return el ? { text: `${name} ở cung ${pal}${own && own !== el.palace ? ` chiếu sang cung ${el.palace}` : ''}`.trim(), cause: { domain: v.id, ruleId: '', stars: [{ name, palace: pal }] } } : { text: '' };
}

export function proseTongLuan(chart: ChartInput, k: Knowledge, seed: string, engine: string, allowDraft: boolean, ledger?: Ledger): ProseTongLuan {
  const L = k.prose?.tongLuan;
  const V = k.prose?.luan?.ledger?.verdict ?? {};
  const usable = !!L && (allowDraft || L.status === 'approved');
  const m = new Micro(`${seed}|tong_luan`, k.prose!.connectives, k.prose!.frames);
  const say = (xs: ProseSentence[], text: string, step: string, extra: Partial<SentenceTrace> = {}, basis: SentenceTrace['basis'] = 'he_thong') => {
    const t = finish(text); m.said(t);
    xs.push({ text: t, trace: { move: 'VALUE', concepts: [], rules: [], cites: [], basis, step, ...extra } as SentenceTrace });
  };
  const p1: ProseSentence[] = [], p2: ProseSentence[] = [], p3: ProseSentence[] = [];
  if (usable) {
    const led = ledger ?? buildLedger(chart, k, infer(chart, k).resolved);
    const words = (v: DomainVerdict) => { const xs = V[verdictKey(v)]; return xs?.length ? m.pick(`tlv|${v.id}`, xs) : ''; };
    const tr = (v: DomainVerdict): Partial<SentenceTrace> => { const it = [...v.pos, ...v.neg, ...v.timing, ...v.mixed];
      return { rules: [...new Set(it.map(x => x.ruleId))].sort(), cites: [...new Set(it.flatMap(x => x.cites))].sort(), ledger: { domain: v.id, verdict: v.verdict, base: v.base } }; };
    const ranked = led.domains.map(v => ({ v, r: rankOf(v) })).filter((x): x is { v: DomainVerdict; r: number } => x.r !== null && !!words(x.v))
      .sort((a, b) => b.r - a.r || (a.v.id < b.v.id ? -1 : 1));
    const open = led.domains.filter(v => v.verdict === 'chua_phan_xu');
    if (ranked.length >= 2 && ranked[0].r > ranked.at(-1)!.r) {
      // ties share a place: every domain at the top rank is a strength, every one at the bottom a weakness; the first of each is the one named
      // a strength is a domain at least leaning to the good side, a weakness one at most eased: two-faceted or balanced domains are neither
      const top = ranked.filter(x => x.r === ranked[0].r && x.r >= 2.5), bottom = ranked.filter(x => x.r === ranked.at(-1)!.r && x.r <= 1);
      const best = top[0], worst = bottom[0];
      const named = (xs: typeof ranked) => joinVi(xs.map(x => x.v.label));
      say(p1, m.pick('lead', L!.lead), 'tong_luan:lead');
      // the twelve-palace chart reads the domain's own palace alone; a ranked domain whose palace it reads the other way is explained, not left
      // to look like a contradiction (review of the live charts 2026-10-25)
      const radar = new Map(computeIndices(chart, k, NORMS).palaces.map(p => [p.palace, p]));
      const DEF = (k.kg?.domains as { domains?: Record<string, { palaces?: Record<string, string>; parts?: Record<string, { palaces: Record<string, string> }> }> } | undefined)?.domains ?? {};
      const palsOf = (v: DomainVerdict) => { const [id, part] = v.id.split('.'); const d0 = DEF[id]; return (part ? d0?.parts?.[part]?.palaces : d0?.palaces) ?? {}; };
      const radarOff = (v: DomainVerdict, kind: 'best' | 'worst') => {
        const ps = palsOf(v), core = Object.keys(ps).find(p => ps[p] === 'core'), r = core ? radar.get(core) : undefined;
        return !!core && !!r && Object.keys(ps).some(p => p !== core) && (kind === 'best' ? r.support < 1 && r.limit > 1 : r.support > 1 && r.limit < 1);
      };
      const radarLine = (v: DomainVerdict, kind: 'best' | 'worst') => {
        const ps = palsOf(v), core = Object.keys(ps).find(p => ps[p] === 'core'), r = core ? radar.get(core) : undefined;
        const others = Object.keys(ps).filter(p => p !== core);
        if (!core || !r || !others.length) return;
        const off = kind === 'best' ? r.support < 1 && r.limit > 1 : r.support > 1 && r.limit < 1;
        const F = kind === 'best' ? L!.radar_best : L!.radar_worst;
        if (off && F?.length) say(p1, fill(m.pick(`radar|${kind}`, F), { pal: core, domain: v.label, others: joinVi(others.map(p => `cung ${p}`)) }), `tong_luan:radar:${v.id}`,
          { note: 'Biểu đồ mười hai cung đo riêng từng cung với tam phương; kết luận lĩnh vực gộp mọi cung của lĩnh vực ấy (quy ước domains.json).' });
      };
      // each domain of a shared place is named with its own ground (review 2026-11-07: two domains under one cause read as a wrong attribution)
      const place = (xs: typeof ranked, kind: 'best' | 'worst', step: string) => {
        const head = xs[0], g0 = groundOf(chart, head.v);
        const trc = (gs: Array<ReturnType<typeof groundOf>>) => ({ ...tr(head.v), rules: [...new Set(xs.flatMap(x => tr(x.v).rules!))].sort(), cause: gs.flatMap(g => g.cause ? [g.cause] : []) });
        const LL = L as unknown as Record<string, string[] | undefined>;
        if (xs.length > 1 && LL[`${kind}_multi`]?.length && L!.pair?.length) {
          const gs = xs.map(x => groundOf(chart, x.v));
          const pairs = joinVi(xs.map((x, i) => fill(m.pick(`pair|${x.v.id}`, L!.pair!), { domain: x.v.label, verdict: words(x.v).replace(/^là /, ''), ground: gs[i].text || 'các chương trước' })));
          say(p1, fill(m.pick(`${kind}_multi`, LL[`${kind}_multi`]!), { pairs }), step, trc(gs));
          return;
        }
        // a strength whose own palace reads below the usual on the twelve-palace chart is not called the chart's support (review 2026-11-07)
        const F = kind === 'best' && radarOff(head.v, 'best') && L!.best_off?.length ? L!.best_off : L![kind];
        say(p1, fill(m.pick(kind, F), { domain: named(xs), verdict: words(head.v).replace(/^là /, ''), ground: g0.text || 'các chương trước' }), step, trc([g0]));
      };
      if (best) place(top, 'best', `tong_luan:best:${best.v.id}`);
      const mid = ranked.filter(x => !top.includes(x) && !bottom.includes(x));
      if (mid.length) say(p1, fill(m.pick('middle', L!.middle), { list: joinVi(mid.map(x => `${x.v.label} ${words(x.v)}`)) }), 'tong_luan:middle', { rules: mid.flatMap(x => tr(x.v).rules!) });
      if (best) radarLine(best.v, 'best');
      if (worst) place(bottom, 'worst', `tong_luan:worst:${worst.v.id}`);
      if (worst) radarLine(worst.v, 'worst');
      for (const v of open.slice(0, 2)) say(p1, fill(m.pick(`open|${v.id}`, L!.open), { domain: v.label }), `tong_luan:open:${v.id}`, tr(v));
      if (led.domains.some(v => v.verdict === 'khong_ket_luan')) say(p1, m.pick('health', L!.health), 'tong_luan:health');
      if (best && worst) say(p3, fill(m.pick('advice', L!.advice), { best: best.v.label, worst: worst.v.label }), 'tong_luan:advice',
        { note: 'Gợi ý của hệ thống rút từ thứ bậc vừa nêu, không phải lời phán đoán của lá số.' }, 'loi_khuyen');
    } else if (ranked.length) {
      say(p1, fill(m.pick('same', L!.same), { list: joinVi(ranked.map(x => `${x.v.label} ${words(x.v)}`)) }), 'tong_luan:same');
      for (const v of open.slice(0, 2)) say(p1, fill(m.pick(`open|${v.id}`, L!.open), { domain: v.label }), `tong_luan:open:${v.id}`, tr(v));
    }
    // the đại hạn on the system indices (the period chart's levels): highest, lowest, the largest change, the current one
    // a decade with no book evidence ("chưa đủ căn cứ", indices-3.0.0) is never named best, worst or a turning point
    // only decades starting before 80 are ranked (owner decision Q4 2026-11-07); the later ones keep their own reading in the đại hạn chapter
    const ds = computeIndices(chart, k, NORMS).decades.filter(d => !d.insufficient && d.age_from < RANK_AGE_LIMIT);
    if (ds.length >= 3) {
      const ix = { note: 'Mức của đại hạn theo chỉ số tổng hợp của hệ thống (cùng thang với biểu đồ giai đoạn), không phải lời sách.' };
      const hi = [...ds].sort((a, b) => b.score - a.score)[0], lo = [...ds].sort((a, b) => a.score - b.score)[0];
      const dv = (d: typeof ds[number]) => ({ a: String(d.age_from), b: String(d.age_to), pal: d.palace, level: d.level_vi });
      // the lowest decade is lowest against the corpus; when its own book side leans good, the sentence says so (review of the live charts 2026-10-25)
      const rel = bookLean(lo.items) > 0 && L!.dec_worst_rel?.length ? m.pick('dec_worst_rel', L!.dec_worst_rel) : '';
      if (hi.level !== lo.level) say(p2, `${fill(m.pick('dec_best', L!.dec_best), dv(hi))}; ${fill(m.pick('dec_worst', L!.dec_worst), dv(lo))}${rel}`, 'tong_luan:decades', ix, 'he_thong');
      const jumps = ds.slice(1).map((d, i) => ({ d, prev: ds[i], j: d.level - ds[i].level })).filter(x => x.j !== 0).sort((a, b) => Math.abs(b.j) - Math.abs(a.j) || a.d.age_from - b.d.age_from);
      const t = jumps[0];
      if (t && Math.abs(t.j) >= 2) say(p2, fill(m.pick(t.j > 0 ? 'turn_up' : 'turn_down', t.j > 0 ? L!.turn_up : L!.turn_down), { a: String(t.d.age_from), pal: t.d.palace, from: t.prev.level_vi, to: t.d.level_vi }), 'tong_luan:turn', ix, 'he_thong');
      const cur = ds.find(d => d.current);  // (an insufficient current decade is left out above: nothing to say of its level)
      if (cur && cur !== hi && cur !== lo) say(p2, fill(m.pick('current', L!.current), dv(cur)), 'tong_luan:current', ix, 'he_thong');
    }
  }
  const paragraphs: ProseParagraph[] = ([['structure', p1], ['course', p2], ['balance', p3]] as Array<[ProseParagraph['role'], ProseSentence[]]>).filter(([, xs]) => xs.length)
    .map(([role, xs]) => ({ role, sentences: xs, text: xs.map(s => s.text).join(' ') }));
  const { issues, metrics } = validateProse(paragraphs, []);
  return { engine, kbVersion: k.version, chapter: 'tong_luan', palace: 'Tổng luận', title: 'Tổng luận', draft: usable && L!.status !== 'approved',
    paragraphs, text: paragraphs.map(p => p.text).join('\n\n'), issues, metrics, pass: !issues.some(i => i.level === 'error'),
    evidence: { resolved: [], tensions: [], unused: [], rules: {}, concepts: {}, divergences: [] } };
}
