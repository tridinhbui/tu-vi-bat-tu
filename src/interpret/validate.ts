// Quality validation of a generated chapter. Errors fail the chapter; warnings are reported. Nothing here judges whether the content is
// "expert quality": that needs a human reviewer (content modules carry their editorial status, reported with the output).
import type { ArgumentGraph } from './planner.ts';
import type { Paragraph } from './generator.ts';
import type { ChartInput, Knowledge } from './types.ts';

export interface QualityReport {
  pass: boolean; errors: Array<{ check: string; detail: string }>; warnings: Array<{ check: string; detail: string }>;
  metrics: { words: number; sentences: number; paragraphs: number; bySource: Record<string, number>; independentGrounds: number; wordsPerGround: number;
    repeated4gramRate: number; consecutiveSameOpener: number; personalization: number; citedBookSentences: number; quotes: number };
  editorial: { modules: Array<{ id: string; version: number; status: string }>; allApproved: boolean; notice: string };
}

const BANNED = [/\bchắc chắn\b/i, /\bnhất định sẽ\b/i, /\bđịnh mệnh\b/i, /\bkhông thể tránh\b/i, /\btai họa\b/i, /\bsẽ bị\b/i, /\btuyệt đối\b/i, /\bluôn luôn\b/i];
const words = (t: string) => t.split(/\s+/).filter(w => /[\p{L}\p{N}]/u.test(w));
const stripQuotes = (t: string) => t.replace(/“[^”]*”/g, ' ').replace(/\([^)]*\)/g, ' ');
const opener = (t: string) => words(t).slice(0, 2).join(' ').toLowerCase();

export function validate(paras: Paragraph[], a: ArgumentGraph, chart: ChartInput, k: Knowledge, firedVerified: Set<string>): QualityReport {
  const errors: QualityReport['errors'] = [], warnings: QualityReport['warnings'] = [];
  const sents = paras.flatMap(p => p.sentences);
  const text = sents.map(s => s.text).join(' ');

  // 1. grounding: book sentences must rest on fired, verified rules and carry a page
  for (const s of sents) {
    if (s.basis === 'sach') {
      if (!s.rules.length && !s.cites.length) errors.push({ check: 'missing_source', detail: s.text });
      const unfired = s.rules.filter(r => !firedVerified.has(r) && !r.startsWith('VH_'));
      if (unfired.length) errors.push({ check: 'unsupported_conclusion', detail: `${unfired.join(', ')} :: ${s.text}` });
      if (!/tr\.\s?\d|pp?\.\s?\d/.test(s.text) && !s.cites.length && s.kind !== 'interaction') warnings.push({ check: 'page_not_in_sentence', detail: s.text });
    }
    if (BANNED.some(b => b.test(s.text))) errors.push({ check: 'banned_wording', detail: s.text });
  }
  // 2. duplicated meanings: a book quote is narrated as a claim once; dominance/interaction sentences may refer back to it
  const seen = new Map<string, string>();
  for (const s of sents.filter(x => ['claim', 'contrast', 'timing'].includes(x.kind))) {
    for (const q of s.text.match(/“[^”]+”/g) ?? []) {
      if (seen.has(q) && seen.get(q) !== s.passage) errors.push({ check: 'duplicated_meaning', detail: `${q} narrated in ${seen.get(q)} and ${s.passage}` });
      seen.set(q, s.passage);
    }
  }
  for (let i = 0; i < sents.length; i++) for (let j = i + 1; j < sents.length; j++) {
    const A = new Set(words(stripQuotes(sents[i].text).toLowerCase())), B = new Set(words(stripQuotes(sents[j].text).toLowerCase()));
    const inter = [...A].filter(w => B.has(w)).length, uni = new Set([...A, ...B]).size;
    if (uni > 12 && inter / uni > 0.75) warnings.push({ check: 'near_duplicate_sentence', detail: `${sents[i].text} || ${sents[j].text}` });
  }
  // 3. contradictions: opposed claims both narrated must be connected by an interaction (dominance or explicit both-hold)
  const narrated = new Set(a.claims.filter(c => c.quotes.some(q => text.includes(`“${q}”`))).map(c => c.id));
  const contra = new Set(k.relations.relations.filter(r => r.type === 'contradicts').map(r => [r.a, r.b].sort().join('|')));
  const inter = sents.filter(s => s.kind === 'interaction').map(s => s.text).join(' ');
  for (const c1 of a.claims) for (const c2 of a.claims) {
    if (c1.id >= c2.id || !narrated.has(c1.id) || !narrated.has(c2.id)) continue;
    const opposed = contra.has([c1.concept, c2.concept].sort().join('|')) || (c1.palace === c2.palace && c1.palace === a.career && c1.polarity !== c2.polarity && c1.polarity !== '~' && c2.polarity !== '~' && c1.role !== c2.role);
    if (opposed && !(c1.quotes.some(q => inter.includes(q)) && c2.quotes.some(q => inter.includes(q))) && !inter.includes('giữ cả hai')) {
      const ok = a.dominance.some(d => [d.base.id, d.qualifier.id].includes(c1.id) && [d.base.id, d.qualifier.id].includes(c2.id));
      if (!ok) warnings.push({ check: 'contradiction_not_explained', detail: `${c1.quotes[0]} <> ${c2.quotes[0]}` });
    }
  }
  // 4. repetition
  const toks = words(stripQuotes(text).toLowerCase());
  const grams = new Map<string, number>();
  for (let i = 0; i + 3 < toks.length; i++) { const g = toks.slice(i, i + 4).join(' '); grams.set(g, (grams.get(g) ?? 0) + 1); }
  const rep = [...grams.values()].filter(v => v > 1).reduce((x, v) => x + v - 1, 0) / Math.max(1, grams.size);
  if (rep > 0.08) warnings.push({ check: 'excessive_repetition', detail: `repeated 4-gram rate ${rep.toFixed(3)}` });
  let same = 0;
  for (let i = 1; i < sents.length; i++) if (opener(sents[i].text) === opener(sents[i - 1].text)) same++;
  if (same > 1) warnings.push({ check: 'repeated_openers', detail: `${same} consecutive sentences start alike` });
  // 5. personalization: sentences that mention this chart's own stars, palaces, branches, ages or years
  const tokens = new Set<string>([...chart.palaces.flatMap(p => p.stars), ...chart.palaces.map(p => p.branch), String(chart.year.year)]);
  const personal = sents.filter(s => [...tokens].some(t => s.text.includes(t)) || /\d+–\d+/.test(s.text)).length / Math.max(1, sents.length);
  if (personal < 0.6) warnings.push({ check: 'weak_personalization', detail: `${(personal * 100).toFixed(0)}% of sentences name chart-specific facts` });
  // 6. length vs evidence: never inflate
  const grounds = a.claims.reduce((n, c) => n + c.grounds.filter(g => g.independent).length, 0);
  const wc = words(text).length;
  if (grounds && wc / grounds > 200) warnings.push({ check: 'possible_inflation', detail: `${wc} words for ${grounds} independent grounds` });
  if (wc > 1500) warnings.push({ check: 'over_budget', detail: `${wc} words (major chapters target 800–1,500 when evidence allows)` });
  if (wc < 250 && grounds >= 6) warnings.push({ check: 'thin_for_evidence', detail: `${wc} words for ${grounds} grounds` });

  const mods = [...new Set(sents.map(s => s.module))].map(id => k.modules.find(m => m.id === id)!).map(m => ({ id: m.id, version: m.version, status: m.status }));
  const allApproved = mods.every(m => m.status === 'approved');
  const bySource: Record<string, number> = {};
  for (const s of sents) bySource[s.basis] = (bySource[s.basis] ?? 0) + 1;
  return {
    pass: errors.length === 0, errors, warnings,
    metrics: { words: wc, sentences: sents.length, paragraphs: paras.length, bySource, independentGrounds: grounds, wordsPerGround: grounds ? Math.round(wc / grounds) : 0,
      repeated4gramRate: Number(rep.toFixed(3)), consecutiveSameOpener: same, personalization: Number(personal.toFixed(2)),
      citedBookSentences: sents.filter(s => s.basis === 'sach' && (s.cites.length || /tr\.\s?\d/.test(s.text))).length, quotes: (text.match(/“/g) ?? []).length },
    editorial: { modules: mods, allApproved,
      notice: allApproved ? 'Các module nội dung đã được chuyên gia duyệt.' : 'Nội dung biên tập của chương này đang ở trạng thái nháp, chưa qua thẩm định chuyên gia; mọi câu sách đều có truy vết nhưng cách tổ chức lập luận cần được duyệt.' },
  };
}
