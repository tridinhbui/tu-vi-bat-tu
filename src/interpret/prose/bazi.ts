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

export interface BaziLibrary {
  status: 'draft' | 'approved';
  dm_first: string[]; dm_next: string[]; napam: string[]; skip: string[];
  topics: Record<string, { label: string; rules: string[] }>; topic_order: string[];
  direct: string[]; direct_same: string[];
}

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
  const paragraphs: ProseParagraph[] = [];
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
    const p2: ProseSentence[] = [];
    for (const t of L!.topic_order) {
      const spec = L!.topics[t];
      const fs = ver.filter(f => spec.rules.some(p => f.ruleId.startsWith(p))).sort((x, y) => x.ruleId.localeCompare(y.ruleId));
      fs.forEach((f, i) => {
        const { effect, cause: generic } = splitDirect(raw(f));
        if (!generic) return;
        const cause = actual(generic);
        p2.push(sentence(fill(m.pick(`${t}${i}`, i ? L!.direct_same : L!.direct), { topic: spec.label, cause: lowerFirst(cause), effect: lowerFirst(effect) }), f));
      });
    }
    if (p2.length) paragraphs.push({ role: 'support', sentences: p2, text: p2.map(s => s.text).join(' ') });
  }
  const { issues, metrics } = validateProse(paragraphs, []);
  return {
    engine, kbVersion: k.version, chapter: 'bat_tu', palace: 'Bát Tự', schema: 'BAT_TU', order: ['ANCHOR'], draft: usable && L!.status !== 'approved',
    paragraphs, text: paragraphs.map(p => p.text).join('\n\n'), issues, metrics, pass: !issues.some(i => i.level === 'error'),
    evidence: { resolved: [], tensions: [], unused: [], rules, concepts: {}, divergences: [],
      limits: ['vượng/nhược của nhật chủ, dụng thần và cách cục: chưa có quy tắc đã đối chiếu sách nên không đưa vào văn',
        ...(P?.drafts.length ? [`${P.drafts.length} nhận định Bát Tự còn ở dạng nháp, không đưa vào văn`] : [])] },
  };
}
