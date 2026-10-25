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
  /** reach when breaking (or, for a bad cách, easing) elements lowered the degree: the reason named, not the palace */
  reach_lowered?: string[]; reach_palace_lowered?: string[]; reach_bad?: string[];
  /** the page-checked breaker the chart itself holds ({present}) beside the book's condition ({broken}) */
  f_broken_present?: string[];
  /** a told cách the books define differently (DEEP-3) */
  school_head?: string[]; school_side?: string[];
  /** the page-checked cách (formations_verified.json): head, state by the evaluator's verdict, a refutation, the degree by state */
  f_head?: string[]; f_state?: Record<string, string[]>; f_refute?: string[]; f_degree?: Record<string, string>;
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
const nameOf = (reading: string) => reading.replace(/^(khuynh hướng|hạn chế:)\s*/, '').replace(/\s*\(.*\)\s*$/, '').trim();
/** the rule's gloss of the cách in brackets ("Thiên Không, Đào Hoa ở Mệnh …: có danh thì nghèo"), told once, in the cách's head */
const glossOf = (reading: string) => reading.match(/\(([^()]*)\)\s*$/)?.[1]?.trim() ?? '';

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
        const lowered = good ? limits.slice(0, 2) : helps.slice(0, 1);
        return { l, r, P, name: nameOf(r.reading ?? ''), gloss: glossOf(r.reading ?? ''), limits, helps, good, degree, lowered };
      })
      .sort((a, b) => b.degree - a.degree || Number(b.P === 'Mệnh') - Number(a.P === 'Mệnh') || (a.l.ruleId < b.l.ruleId ? -1 : 1));
    // the page-checked cách (formations_verified.json): evaluated on the chart (reason/structures.ts); a cách whose core alone the books
    // already call a fine cách (core_alone 'thanh') is thành when nothing breaks it, not 'hình thức' (docs/audit/CACH-CUC-SOURCES.md)
    const FV = k.kg?.formationsVerified;
    const verified = (FV && L!.f_state ? evaluateFormations(FV.formations, chart.base) : []).filter(r => r.state !== 'khong_hien' && r.state !== 'chua_du_du_kien')
      .map(r => ({ r, ev: FV!.evidence[r.id], state: r.state === 'hinh_thuc' && FV!.evidence[r.id]?.core_alone === 'thanh' ? 'thanh_core' : r.state }));
    const p0: ProseSentence[] = [];
    const names = [...verified.map(x => `cách ${x.r.name}`), ...found.map(x => x.name)];
    if (!names.length) say(p0, m.pick('none', L!.none), 'cach:none', 'he_thong');
    else say(p0, fill(m.pick('intro', L!.intro), { n: String(names.length), list: joinVi(names) }), 'cach:intro', 'sach', [...verified.map(x => x.r.id), ...found.map(x => x.l.ruleId)],
      [...new Set([...verified.flatMap(x => x.ev?.core ?? []), ...found.flatMap(x => x.l.cites)])].sort());
    paragraphs.push({ role: 'structure', sentences: p0, text: '' });
    const note = 'Lời tổng hợp: yếu tố phá là sát tinh không đắc, Hóa Kỵ, chính tinh hãm, Tuần hay Triệt ở ngay cung có cách; mức ảnh hưởng theo quy ước của hệ thống (cách ở Mệnh nặng hơn, mỗi yếu tố phá hạ một bậc), không phải lời sách.';
    const DEG: Record<string, number> = { thanh_thuong: 3, thanh: 2, thanh_core: 2, hinh_thuc: 1, bi_pha: 1 };
    for (const x of verified) {
      const xs: ProseSentence[] = [], id = x.r.id, ev = x.ev, items = ev?.items ?? {};
      const pages = (kind: string, ms: Array<{ id: string }>) => [...new Set(ms.flatMap(e => items[`${kind}:${e.id}`] ?? []))];
      rules[id] = { reading: `cách ${x.r.name}`, cites: [...(ev?.core ?? []), ...(ev?.effect ?? [])], verified: true };
      say(xs, fill(m.pick(`fh|${id}`, L!.f_head!), { name: x.r.name }), `cach:${id}`, 'sach', [id], [...new Set([...(ev?.core ?? []), ...(ev?.effect ?? [])])].sort());
      const lab = (ms: Array<{ label: string }>) => joinVi([...new Set(ms.map(e => e.label))].slice(0, 3));
      const st = x.state, F = L!.f_state!;
      const text = st === 'thanh_thuong' ? fill(m.pick(`fs|${id}`, F.thanh_thuong), { boost: lab(x.r.boosters) })
        : st === 'bi_pha' ? (() => {
          const ms = [...x.r.breakers, ...x.r.uncovered], present = [...new Set(ms.flatMap(e => e.present ?? []))].slice(0, 3);
          const withLabel = present.length && L!.f_broken_present ? fill(m.pick(`fs|${id}`, L!.f_broken_present), { present: joinVi(present), broken: lab(ms) }) : '';
          if (withLabel && withLabel.split(/\s+/).length > 35) return fill(m.pick(`fs|${id}`, F.bi_pha), { broken: joinVi(present) });
          return withLabel ? withLabel
            : fill(m.pick(`fs|${id}`, F.bi_pha), { broken: lab(ms) });
        })()
        : st === 'hinh_thuc' ? (x.r.missing.length ? fill(m.pick(`fs|${id}`, F.hinh_thuc), { missing: joinVi(x.r.missing.slice(0, 2)) }) : m.pick(`fs|${id}`, F.hinh_thuc_bare))
        : m.pick(`fs|${id}`, F[st] ?? F.thanh);
      const stCites = st === 'thanh_thuong' ? pages('boosters', x.r.boosters) : st === 'bi_pha' ? pages('breakers', [...x.r.breakers, ...x.r.uncovered]) : ev?.core ?? [];
      // a plain thành (or a core the books already call fine) with the page's meaning for that state: the meaning says it (DEEP-3: the bare
      // "Cách thành" / "Riêng phần lõi đã là một quý cách" line read the same on half the charts)
      const plain = (st === 'thanh' || st === 'thanh_core') && !!ev?.meaning?.thanh;
      if (!plain) say(xs, text, `cach:${id}:state`, 'sach', [id], stCites.sort());
      if (x.r.refutations.length && L!.f_refute) say(xs, fill(m.pick(`fr|${id}`, L!.f_refute), { refute: lab(x.r.refutations) }), `cach:${id}:refute`, 'sach', [id], pages('refutations', x.r.refutations).sort());
      // what the cách brings in this state, as the page says (formations_verified meaning, DEEP-3); with it the system's degree line is not
      // needed, without it the degree line stands
      const mean = ev?.meaning?.[st === 'thanh_core' ? 'thanh' : st];
      if (mean) say(xs, cap(mean.text), `cach:${id}:meaning`, 'sach', [id], [mean.cite]);
      else {
        const deg = L!.f_degree?.[st === 'thanh_core' ? 'thanh' : st] ?? L!.degree['2'];
        say(xs, fill(m.pick(`re|${id}`, L!.reach), { degree: deg }), `cach:${id}:reach`, 'he_thong', [], [], note);
      }
      paragraphs.push({ role: 'support', sentences: xs, text: '', title: `Cách ${x.r.name}` } as ProseParagraph);
    }
    for (const x of found) {
      const xs: ProseSentence[] = [];
      rules[x.l.ruleId] = { reading: x.r.reading ?? '', cites: x.l.cites, verified: true };
      const head = fill(m.pick(`named|${x.l.ruleId}`, L!.named), { Name: cap(x.name), name: x.name, pal: x.P, cite: x.l.cites.join(', ') }) + (x.gloss ? `: ${x.gloss}` : '');
      say(xs, `${head}. ${m.pick(`gb|${x.l.ruleId}`, x.good ? L!.good : L!.bad)}`, `cach:${x.l.ruleId}`, 'sach', [x.l.ruleId], x.l.cites);
      const state = x.good ? (x.limits.length ? fill(m.pick(`br|${x.l.ruleId}`, L!.broken), { pal: x.P, limits: joinVi(x.limits.slice(0, 3)) }) : fill(m.pick(`wh|${x.l.ruleId}`, L!.whole), { pal: x.P }))
        : (x.helps.length ? fill(m.pick(`be|${x.l.ruleId}`, L!.bad_eased), { pal: x.P, helps: joinVi(x.helps.slice(0, 3)) }) : fill(m.pick(`bf|${x.l.ruleId}`, L!.bad_full), { pal: x.P }));
      const deg = L!.degree[String(x.degree)];
      const low = x.lowered.length && L!.reach_lowered && L!.reach_palace_lowered, why = joinVi(x.lowered);
      // a bad cách: its reach is the reach of its harm (DEEP-3: "không bị yếu tố nào hạ bậc" read as praise)
      const reach = !x.good && !low && L!.reach_bad?.length ? fill(m.pick(`rb|${x.l.ruleId}`, L!.reach_bad), { degree: deg, pal: x.P, dom: x.P === 'Mệnh' ? 'cả đời người' : short[x.P] ?? x.P })
        : x.P === 'Mệnh' ? fill(m.pick(`re|${x.l.ruleId}`, low ? L!.reach_lowered! : L!.reach), { degree: deg, why })
        : fill(m.pick(`rp|${x.l.ruleId}`, low ? L!.reach_palace_lowered! : L!.reach_palace), { degree: deg, pal: x.P, dom: short[x.P] ?? x.P, why });
      say(xs, cap(state), `cach:${x.l.ruleId}:state`, 'he_thong', [x.l.ruleId], [], note);
      say(xs, reach, `cach:${x.l.ruleId}:reach`, 'he_thong', [x.l.ruleId], [], note);
      paragraphs.push({ role: 'support', sentences: xs, text: '', title: cap(x.name) } as ProseParagraph);
    }
    // where the books define a told cách differently (kg/schools.json kind 'cach', DEEP-3): each book's definition, in the Đọc sâu fold
    const norm = (x: string) => x.toLocaleLowerCase('vi').replace(/^cách\s+/, '').replace(/\s+(ở|tại)\s+.*$/, '').trim();
    const told = [...verified.map(x => ({ id: x.r.id, name: x.r.name })), ...found.map(x => ({ id: x.l.ruleId, name: x.name }))];
    const SCH: Record<string, string> = { KL: 'Khảo Luận', TH: 'Thực Hành', TT: 'Toàn Thư', ZWDS_HAN: 'bản Hán văn', TVNL: 'Nghiệm Lý' };
    for (const t of (k.kg?.schools?.topics ?? []).filter(t => t.kind === 'cach')) {
      const head = norm(t.topic.split(':')[0]), hit = told.find(x => norm(x.name) === head || norm(x.name).startsWith(head));
      const SH = L!.school_head, SS = L!.school_side;
      if (!hit || !SH || !SS) continue;
      const xs: ProseSentence[] = [];
      say(xs, fill(m.pick(`sch|${t.id}`, SH), { name: t.topic.split(':')[0].trim(), n: String(t.sides.length) }), `cach:school:${t.id}`, 'sach', [hit.id], t.sides.map(s => s.cite));
      t.sides.forEach((s, i) => say(xs, fill(m.pick(`schs|${t.id}|${i}`, SS), { book: SCH[s.school] ?? s.school, statement: s.statement }), `cach:school:${t.id}:${i}`, 'sach', [hit.id], [s.cite]));
      paragraphs.push({ role: 'support', sentences: xs, text: '', deep: true, title: 'Các bộ sách định nghĩa khác nhau' } as ProseParagraph);
    }
    // the ranking: page-checked cách by their state, then the named ones by degree
    const all = [...verified.map(x => ({ name: `cách ${x.r.name}`, good: x.state !== 'bi_pha', degree: DEG[x.state] ?? 1 })), ...found.map(x => ({ name: x.name, good: x.good, degree: x.degree }))]
      .sort((a, b) => b.degree - a.degree);
    if (all.length >= 2) {
      // the balance is told only when both sides are present, with the cách of each side named and the sides weighed by degree
      const xs: ProseSentence[] = [], goods = all.filter(x => x.good), bads = all.filter(x => !x.good);
      say(xs, fill(m.pick('rank', L!.rank), { first: all[0].name }), 'cach:rank', 'he_thong', [], [], note);
      if (goods.length && bads.length) {
        const wg = goods.reduce((a, x) => a + x.degree, 0), wb = bads.reduce((a, x) => a + x.degree, 0);
        say(xs, fill(L!.balance[wg > wb ? 0 : wg < wb ? 1 : 2], { goods: joinVi(goods.map(x => x.name)), bads: joinVi(bads.map(x => x.name)) }), 'cach:balance', 'he_thong', [], [], note);
      }
      paragraphs.push({ role: 'balance', sentences: xs, text: '' });
    }
    for (const p of paragraphs) p.text = p.sentences.map(s => s.text).join(' ');
  }
  const { issues, metrics } = validateProse(paragraphs, []);
  return { engine, kbVersion: k.version, chapter: 'cach_cuc', palace: 'Cách cục', title: 'Cách cục', draft: usable && L!.status !== 'approved',
    paragraphs, text: paragraphs.map(p => p.text).join('\n\n'), issues, metrics, pass: !issues.some(i => i.level === 'error'),
    evidence: { resolved: [], tensions: [], unused: [], rules, concepts: {}, divergences: [] } };
}
