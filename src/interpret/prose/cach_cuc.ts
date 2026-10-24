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

export interface CachCucLib {
  status: string; none: string[]; intro: string[]; named: string[]; good: string[]; bad: string[]; whole: string[]; broken: string[];
  bad_eased: string[]; bad_full: string[]; degree: Record<string, string>; reach: string[]; reach_palace: string[]; rank: string[]; balance: string[];
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
    const p0: ProseSentence[] = [];
    if (!found.length) say(p0, m.pick('none', L!.none), 'cach:none', 'he_thong');
    else say(p0, fill(m.pick('intro', L!.intro), { n: String(found.length), list: joinVi(found.map(x => x.name)) }), 'cach:intro', 'sach', found.map(x => x.l.ruleId), [...new Set(found.flatMap(x => x.l.cites))].sort());
    paragraphs.push({ role: 'structure', sentences: p0, text: '' });
    const note = 'Lời tổng hợp: yếu tố phá là sát tinh không đắc, Hóa Kỵ, chính tinh hãm, Tuần hay Triệt ở ngay cung có cách; mức ảnh hưởng theo quy ước của hệ thống (cách ở Mệnh nặng hơn, mỗi yếu tố phá hạ một bậc), không phải lời sách.';
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
    if (found.length >= 2) {
      const xs: ProseSentence[] = [], g = found.filter(x => x.good).length, b = found.length - g;
      say(xs, fill(m.pick('rank', L!.rank), { first: found[0].name }), 'cach:rank', 'he_thong', [], [], note);
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
