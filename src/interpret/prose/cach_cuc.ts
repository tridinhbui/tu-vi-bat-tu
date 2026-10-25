// Cách cục Tử Vi (review of the live report 2026-10-23, point 13: "thiếu giải thích thành cách, phá cách và mức độ ảnh hưởng"). Every
// formation a verified rule names (kg ruleConcepts kind 'formation': Thực Hành's cách cuộc pp.72-76 and the Khảo Luận cách): its name and
// page as the book gives it (sach); then the system's tổng hợp (he_thong, content/prose/cach_cuc.json): whether a breaking element stands
// in the formation's own palace (a sát tinh not checked đắc, Hóa Kỵ, a hãm chính tinh, Tuần, Triệt: reason/evidence.ts), for a bad
// formation whether a helping element eases it; its reach (Mệnh: the whole chart, another palace: that palace's matter) and degree (three
// levels, one lower per breaking element). The ten draft formations (engine/data/experimental) are not told: none is checked on a page.
import type { ChartInput, Knowledge } from '../types.ts';
import { Micro, finish } from './micro.ts';
import type { ProseParagraph, ProseSentence, SentenceTrace } from './realize.ts';
import { validateProse, type ProseIssue, type ProseMetrics } from './validate.ts';
import { infer, type Inference } from './chapter.ts';
import { palaceEvidence, type Element } from '../reason/evidence.ts';
import { evaluateFormations } from '../reason/structures.ts';

export interface CachCucLib {
  status: string; none: string[]; intro: string[]; named: string[]; good: string[]; bad: string[]; whole: string[]; broken: string[];
  bad_eased: string[]; bad_full: string[]; degree: Record<string, string>; reach: string[]; reach_palace: string[]; rank: string[]; balance: string[];
  /** the page-checked cách (formations_verified.json): head, state by the evaluator's verdict, a refutation, the degree by state */
  f_head?: string[]; f_state?: Record<string, string[]>; f_refute?: string[]; f_degree?: Record<string, string>;
  /** the same cách at the palace holding Thân (TH p.76 "đóng Mệnh Thân") */
  f_head_than?: string[]; reach_than?: string[];
}
export interface ProseCachCuc {
  engine: string; kbVersion: string; chapter: 'cach_cuc'; palace: 'Cách cục'; title: string; draft: boolean;
  paragraphs: ProseParagraph[]; text: string; issues: ProseIssue[]; metrics: ProseMetrics; pass: boolean;
  evidence: { resolved: []; tensions: []; unused: []; rules: Record<string, { reading: string; cites: string[]; verified: boolean }>; concepts: Record<string, string>; divergences: [] };
}
const fill = (t: string, v: Record<string, string>) => t.replace(/\{([A-Za-z_]+)\}/g, (m, k) => v[k] ?? m);
const joinVi = (xs: string[]) => xs.length <= 1 ? xs.join('') : `${xs.slice(0, -1).join(', ')} và ${xs.at(-1)}`;
const cap = (s: string) => s.charAt(0).toLocaleUpperCase('vi') + s.slice(1);
const elName = (e: Element) => e.kind === 'tuan' ? 'Tuần' : e.kind === 'triet' ? 'Triệt' : e.kind === 'hoa_ky' ? 'Hóa Kỵ' : e.kind === 'ky_carrier' ? `${e.star} hóa Kỵ`
  : e.kind === 'major_ham' ? `${e.star} hãm` : e.kind === 'hoa_good' ? (e.hoa ?? '') : e.star ?? '';
/** the formation's name: its rule's reading ("cách Tử Phủ đồng cung ở Mệnh"), the stored hedge dropped */
const nameOf = (reading: string) => reading.replace(/^(khuynh hướng|hạn chế:)\s*/, '').trim();

export function proseCachCuc(chart: ChartInput, k: Knowledge, seed: string, engine: string, allowDraft: boolean, pre?: Inference): ProseCachCuc {
  const L = k.prose?.cachCuc;
  const usable = !!L && (allowDraft || L.status === 'approved');
  const m = new Micro(`${seed}|cach_cuc`, k.prose!.connectives, k.prose!.frames);
  const rules: ProseCachCuc['evidence']['rules'] = {};
  const say = (xs: ProseSentence[], text: string, step: string, basis: SentenceTrace['basis'], ids: string[] = [], cites: string[] = [], note?: string) => {
    const t = finish(text); m.said(t);
    xs.push({ text: t, trace: { move: basis === 'sach' ? 'ANCHOR' : 'VALUE', concepts: [], rules: ids, cites, basis, step, ...(note ? { note } : {}) } as SentenceTrace });
  };
  const paragraphs: ProseParagraph[] = [];
  if (usable) {
    const inf = pre ?? infer(chart, k), rmap = new Map(k.rules.map(r => [r.id, r]));
    const short = k.prose?.structure?.domain_short ?? {};
    const seen = new Set<string>();
    const found = inf.labelled.filter(l => l.kind === 'formation' && rmap.get(l.ruleId)?.reviewStatus === 'verified')
      .filter(l => { const key = `${l.ruleId}|${l.palace ?? 'Mệnh'}`; if (seen.has(key)) return false; seen.add(key); return true; })
      .map(l => {
        const r = rmap.get(l.ruleId)!, P = l.palace ?? 'Mệnh', e = palaceEvidence(chart, k, P, { resolved: inf.resolved });
        const kyCarried = e.mixed.some(x => x.kind === 'ky_carrier');
        const limits = [...new Set([...e.limit.filter(x => !(x.kind === 'hoa_ky' && kyCarried)), ...e.mixed.filter(x => x.kind === 'ky_carrier')].map(elName).filter(Boolean))];
        const helps = [...new Set(e.support.filter(x => x.kind === 'cat' || x.kind === 'loc' || x.kind === 'hoa_good' || x.kind === 'major_bright').map(elName).filter(Boolean))];
        const good = l.pol !== '-';
        const degree = Math.max(1, 3 - (good ? Math.min(2, limits.length) : helps.length ? 1 : 0) - (P === 'Mệnh' ? 0 : 1));
        return { l, r, P, name: nameOf(r.reading ?? ''), limits, helps, good, degree };
      })
      .sort((a, b) => b.degree - a.degree || Number(b.P === 'Mệnh') - Number(a.P === 'Mệnh') || (a.l.ruleId < b.l.ruleId ? -1 : 1));
    // the page-checked cách (formations_verified.json): evaluated on the chart (reason/structures.ts); a cách whose core alone the books
    // already call a fine cách (core_alone 'thanh') is thành when nothing breaks it, not 'hình thức' (docs/audit/CACH-CUC-SOURCES.md)
    const FV = k.kg?.formationsVerified;
    // TH p.76 counts its thượng cách "đóng Mệnh Thân": a cách whose core cites that page is also read at the palace holding Thân, when Thân
    // is not in Mệnh (the other cách are defined for Mệnh only)
    const than = chart.palaces.find(p => p.is_than && p.name !== 'Mệnh');
    const at76 = (FV?.formations ?? []).filter(f => FV!.evidence[f.id]?.core.includes('TH p.76')).map(f => ({ ...f, anchor: than?.name ?? f.anchor }));
    const shown = (rs: ReturnType<typeof evaluateFormations>, thanAt?: string) => rs.filter(r => r.state !== 'khong_hien' && r.state !== 'chua_du_du_kien')
      .map(r => ({ r, thanAt, key: thanAt ? `${r.id}@than` : r.id, ev: FV!.evidence[r.id], state: r.state === 'hinh_thuc' && FV!.evidence[r.id]?.core_alone === 'thanh' ? 'thanh_core' : r.state }));
    // Thân in Mệnh's tam phương reads the same stars: a cách already told at Mệnh is not told again at Thân
    const atMenh = FV && L!.f_state ? shown(evaluateFormations(FV.formations, chart.base)) : [];
    const atThan = FV && L!.f_state && than ? shown(evaluateFormations(at76, chart.base), than.name).filter(x => !atMenh.some(y => y.r.id === x.r.id)) : [];
    const verified = [...atMenh, ...atThan];
    const p0: ProseSentence[] = [];
    const names = [...verified.map(x => `cách ${x.r.name}${x.thanAt ? ` ở cung an Thân (${x.thanAt})` : ''}`), ...found.map(x => x.name)];
    if (!names.length) say(p0, m.pick('none', L!.none), 'cach:none', 'he_thong');
    else say(p0, fill(m.pick('intro', L!.intro), { n: String(names.length), list: joinVi(names) }), 'cach:intro', 'sach', [...verified.map(x => x.r.id), ...found.map(x => x.l.ruleId)],
      [...new Set([...verified.flatMap(x => x.ev?.core ?? []), ...found.flatMap(x => x.l.cites)])].sort());
    paragraphs.push({ role: 'structure', sentences: p0, text: '' });
    const note = 'Lời tổng hợp: yếu tố phá là sát tinh không đắc, Hóa Kỵ, chính tinh hãm, Tuần hay Triệt ở ngay cung có cách; mức ảnh hưởng theo quy ước của hệ thống (cách ở Mệnh nặng hơn, mỗi yếu tố phá hạ một bậc), không phải lời sách.';
    const DEG: Record<string, number> = { thanh_thuong: 3, thanh: 2, thanh_core: 2, hinh_thuc: 1, bi_pha: 1 };
    for (const x of verified) {
      const xs: ProseSentence[] = [], id = x.key, rid = x.r.id, ev = x.ev, items = ev?.items ?? {};
      const pages = (kind: string, ms: Array<{ id: string }>) => [...new Set(ms.flatMap(e => items[`${kind}:${e.id}`] ?? []))];
      rules[id] = { reading: `cách ${x.r.name}${x.thanAt ? ' ở cung an Thân' : ''}`, cites: [...(ev?.core ?? []), ...(ev?.effect ?? [])], verified: true };
      say(xs, fill(m.pick(`fh|${id}`, x.thanAt ? L!.f_head_than! : L!.f_head!), { name: x.r.name, pal: x.thanAt ?? '' }), `cach:${id}`, 'sach', [rid], [...new Set([...(ev?.core ?? []), ...(ev?.effect ?? [])])].sort());
      const lab = (ms: Array<{ label: string }>) => joinVi([...new Set(ms.map(e => e.label))].slice(0, 3));
      const st = x.state, F = L!.f_state!;
      const text = st === 'thanh_thuong' ? fill(m.pick(`fs|${id}`, F.thanh_thuong), { boost: lab(x.r.boosters) })
        : st === 'bi_pha' ? fill(m.pick(`fs|${id}`, F.bi_pha), { broken: lab([...x.r.breakers, ...x.r.uncovered]) })
        : st === 'hinh_thuc' ? (x.r.missing.length ? fill(m.pick(`fs|${id}`, F.hinh_thuc), { missing: joinVi(x.r.missing.slice(0, 2)) }) : m.pick(`fs|${id}`, F.hinh_thuc_bare))
        : m.pick(`fs|${id}`, F[st] ?? F.thanh);
      const stCites = st === 'thanh_thuong' ? pages('boosters', x.r.boosters) : st === 'bi_pha' ? pages('breakers', [...x.r.breakers, ...x.r.uncovered]) : ev?.core ?? [];
      say(xs, text, `cach:${id}:state`, 'sach', [rid], stCites.sort());
      if (x.r.refutations.length && L!.f_refute) say(xs, fill(m.pick(`fr|${id}`, L!.f_refute), { refute: lab(x.r.refutations) }), `cach:${id}:refute`, 'sach', [rid], pages('refutations', x.r.refutations).sort());
      const deg = L!.f_degree?.[st === 'thanh_core' ? 'thanh' : st] ?? L!.degree['2'];
      say(xs, fill(m.pick(`re|${id}`, x.thanAt ? L!.reach_than! : L!.reach), { degree: deg }), `cach:${id}:reach`, 'he_thong', [], [], note);
      paragraphs.push({ role: 'support', sentences: xs, text: '', title: `Cách ${x.r.name}${x.thanAt ? ' (cung an Thân)' : ''}` } as ProseParagraph);
    }
    for (const x of found) {
      const xs: ProseSentence[] = [];
      rules[x.l.ruleId] = { reading: x.r.reading ?? '', cites: x.l.cites, verified: true };
      const head = fill(m.pick(`named|${x.l.ruleId}`, L!.named), { Name: cap(x.name), name: x.name, pal: x.P, cite: x.l.cites.join(', ') });
      say(xs, `${head}. ${m.pick(`gb|${x.l.ruleId}`, x.good ? L!.good : L!.bad)}`, `cach:${x.l.ruleId}`, 'sach', [x.l.ruleId], x.l.cites);
      const state = x.good ? (x.limits.length ? fill(m.pick(`br|${x.l.ruleId}`, L!.broken), { pal: x.P, limits: joinVi(x.limits.slice(0, 3)) }) : fill(m.pick(`wh|${x.l.ruleId}`, L!.whole), { pal: x.P }))
        : (x.helps.length ? fill(m.pick(`be|${x.l.ruleId}`, L!.bad_eased), { pal: x.P, helps: joinVi(x.helps.slice(0, 3)) }) : fill(m.pick(`bf|${x.l.ruleId}`, L!.bad_full), { pal: x.P }));
      const deg = L!.degree[String(x.degree)];
      const reach = x.P === 'Mệnh' ? fill(m.pick(`re|${x.l.ruleId}`, L!.reach), { degree: deg }) : fill(m.pick(`rp|${x.l.ruleId}`, L!.reach_palace), { degree: deg, pal: x.P, dom: short[x.P] ?? x.P });
      say(xs, cap(state), `cach:${x.l.ruleId}:state`, 'he_thong', [x.l.ruleId], [], note);
      say(xs, reach, `cach:${x.l.ruleId}:reach`, 'he_thong', [x.l.ruleId], [], note);
      paragraphs.push({ role: 'support', sentences: xs, text: '', title: cap(x.name) } as ProseParagraph);
    }
    // the ranking: page-checked cách by their state, then the named ones by degree
    const all = [...verified.map(x => ({ name: `cách ${x.r.name}${x.thanAt ? ' ở cung an Thân' : ''}`, good: x.state !== 'bi_pha', degree: DEG[x.state] ?? 1 })), ...found.map(x => ({ name: x.name, good: x.good, degree: x.degree }))]
      .sort((a, b) => b.degree - a.degree);
    if (all.length >= 2) {
      const xs: ProseSentence[] = [], g = all.filter(x => x.good).length, b = all.length - g;
      say(xs, fill(m.pick('rank', L!.rank), { first: all[0].name }), 'cach:rank', 'he_thong', [], [], note);
      say(xs, L!.balance[g > b ? 0 : g < b ? 1 : 2], 'cach:balance', 'he_thong', [], [], note);
      paragraphs.push({ role: 'balance', sentences: xs, text: '' });
    }
    for (const p of paragraphs) p.text = p.sentences.map(s => s.text).join(' ');
  }
  const { issues, metrics } = validateProse(paragraphs, []);
  return { engine, kbVersion: k.version, chapter: 'cach_cuc', palace: 'Cách cục', title: 'Cách cục', draft: usable && L!.status !== 'approved',
    paragraphs, text: paragraphs.map(p => p.text).join('\n\n'), issues, metrics, pass: !issues.some(i => i.level === 'error'),
    evidence: { resolved: [], tensions: [], unused: [], rules, concepts: {}, divergences: [] } };
}
