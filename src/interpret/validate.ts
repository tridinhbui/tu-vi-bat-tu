// Quality validation of a generated chapter. Errors fail the chapter; warnings are reported. Nothing here judges whether the content is
// "expert quality": that needs a human reviewer (content modules carry their editorial status, reported with the output).
//   grounding      'sach' sentences rest on fired, verified rules (or production time readings) and carry pages
//   unsupported    a system / condition sentence may not introduce an evaluation (a polar concept of the lexicon) that no narrated reading
//                  carries: the system frames and connects, it does not add verdicts
//   contradictions opposed readings that are both narrated must sit in one paragraph that states how they relate
//   filler         system sentences that name nothing of this chart (no star, palace, branch, age, year, quote) are counted
//   repetition     a book sentence is narrated once; near-duplicate sentences, repeated 4-grams and openers are reported
//   sensitivity    chapters on health, money and relationships must carry their notice
import { opposedPair, relIndexOf, type ArgumentGraph, type Claim } from './planner.ts';
import type { Paragraph } from './generator.ts';
import type { ChartInput, Knowledge } from './types.ts';

export interface QualityReport {
  pass: boolean; errors: Array<{ check: string; detail: string }>; warnings: Array<{ check: string; detail: string }>;
  metrics: { words: number; sentences: number; paragraphs: number; bySource: Record<string, number>; independentGrounds: number; wordsPerGround: number;
    repeated4gramRate: number; consecutiveSameOpener: number; personalization: number; citedBookSentences: number; quotes: number; genericSentences: number };
  editorial: { modules: Array<{ id: string; version: number; status: string }>; allApproved: boolean; notice: string };
}

const BANNED = [/\bchắc chắn\b/i, /\bnhất định sẽ\b/i, /\bđịnh mệnh\b/i, /\bkhông thể tránh\b/i, /\btai họa\b/i, /\bsẽ bị\b/i, /\btuyệt đối\b/i, /\bluôn luôn\b/i,
  /\bchết\b/i, /\byểu\b/i, /\btù tội\b/i, /\bly hôn\b/i, /\bung thư\b/i, /\bphá sản\b/i];
const words = (t: string) => t.split(/\s+/).filter(w => /[\p{L}\p{N}]/u.test(w));
const stripQuotes = (t: string) => t.replace(/“[^”]*”/g, ' ').replace(/\([^)]*\)/g, ' ');
const opener = (t: string) => words(t).slice(0, 2).join(' ').toLowerCase();
const PALACES = ['Mệnh', 'Phụ Mẫu', 'Phúc Đức', 'Điền Trạch', 'Quan Lộc', 'Nô Bộc', 'Thiên Di', 'Tật Ách', 'Tài Bạch', 'Tử Tức', 'Phu Thê', 'Huynh Đệ', 'Thân'];
const NOTICE: Record<string, RegExp> = {
  health: /không (thay thế|dùng để thay) .*(chẩn đoán|y khoa|bác sĩ)|chẩn đoán/i,
  finance: /(quyết định tài chính|tư vấn tài chính|không phải lời khuyên)/i,
  relationships: /(không (quyết định|thay cho)|quyết định .*(của|thuộc về) (hai người|mỗi người|chính mình))/i,
};

export function validate(paras: Paragraph[], graphs: ArgumentGraph[], chart: ChartInput, k: Knowledge, firedVerified: Set<string>, sensitive?: string): QualityReport {
  const errors: QualityReport['errors'] = [], warnings: QualityReport['warnings'] = [];
  const sents = paras.flatMap(p => p.sentences);
  const text = sents.map(s => s.text).join(' ');
  const claims: Claim[] = graphs.flatMap(a => a.claims);

  // 1. grounding: book sentences must rest on fired, verified rules (or the time readings the engine attaches to a palace) and carry a page
  for (const s of sents) {
    if (s.basis === 'sach') {
      if (!s.rules.length && !s.cites.length) errors.push({ check: 'missing_source', detail: s.text });
      const unfired = s.rules.filter(r => !firedVerified.has(r) && !r.startsWith('VH_') && !r.startsWith('VH:') && r !== 'LUU_TU_HOA');
      if (unfired.length) errors.push({ check: 'unsupported_conclusion', detail: `${unfired.join(', ')} :: ${s.text}` });
      if (!/tr\.\s?\d|pp?\.\s?\d|quyển \d/.test(s.text) && !s.cites.length && s.kind !== 'interaction') warnings.push({ check: 'page_not_in_sentence', detail: s.text });
    }
    if (BANNED.some(b => b.test(stripQuotes(s.text)))) errors.push({ check: 'banned_wording', detail: s.text });
    // the system's own voice must not appear inside a quoted book reading
    for (const qt of s.text.match(/“[^”]+”/g) ?? []) if (/theo sách|hệ thống|bản luận|đọc là|ngưỡng '/.test(qt)) errors.push({ check: 'editorial_leak', detail: qt });
    // 'chỉ đứng được / chỉ thỏa vì …' claims necessity: only where a cross dependency was tested counterfactually
    if (/(chỉ|đứng được là) (đứng được|thỏa|nhờ)/.test(s.text) && s.basis === 'sach' && !graphs.some(a => a.cross.some(x => x.deps.length && s.text.includes(x.claim.quotes[0]))))
      errors.push({ check: 'unsupported_conclusion', detail: `necessity not established :: ${s.text}` });
  }
  // 2. the system never adds a verdict: polar lexicon concepts in he_thong / dieu_kien sentences must belong to a narrated facet
  const lexCues = k.concepts.concepts.filter(c => c.pol !== '~').flatMap(c => c.cues.map(q => ({ q, c })));
  const narratedFacets = new Set(claims.filter(c => c.quotes.some(q => text.includes(`“${q}”`))).map(c => c.facet));
  const narratedConcepts = claims.filter(c => c.quotes.some(q => text.includes(`“${q}”`))).map(c => k.concepts.concepts.find(x => x.id === c.concept)).filter(Boolean);
  const own = [...narratedConcepts.flatMap(c => [c!.np, c!.short ?? '']), ...PALACES].filter(Boolean).map(x => x.toLowerCase()).sort((a, b) => b.length - a.length);
  for (const s of sents.filter(x => (x.basis === 'he_thong' || x.basis === 'dieu_kien') && !['limits', 'notice', 'reflection', 'method'].includes(x.kind))) {
    let low = ' ' + stripQuotes(s.text).toLowerCase() + ' ';
    for (const o of own) low = low.split(o).join(' ');
    for (const { q, c } of lexCues) {
      if (q.length < 4 || !low.includes(' ' + q + ' ')) continue;
      if (!narratedFacets.has(c.facet)) { errors.push({ check: 'unsupported_evaluation', detail: `“${q}” (${c.id}) in a ${s.basis} sentence with no narrated reading on ${c.facet}: ${s.text}` }); break; }
    }
  }
  // 3. duplicated meanings: a book quote is narrated as a claim once; interaction / synthesis sentences may refer back to it
  const seen = new Map<string, string>();
  for (const s of sents.filter(x => ['claim', 'contrast', 'timing', 'ground'].includes(x.kind))) {
    for (const q of s.text.match(/“[^”]+”/g) ?? []) {
      const key = `${q}`, where = `${s.module}/${s.passage}`;
      if (seen.has(key) && seen.get(key) !== where && !s.module.startsWith('VH.')) errors.push({ check: 'duplicated_meaning', detail: `${q} narrated in ${seen.get(key)} and ${where}` });
      seen.set(key, where);
    }
  }
  for (let i = 0; i < sents.length; i++) for (let j = i + 1; j < sents.length; j++) {
    const A = new Set(words(stripQuotes(sents[i].text).toLowerCase())), B = new Set(words(stripQuotes(sents[j].text).toLowerCase()));
    const inter = [...A].filter(w => B.has(w)).length, uni = new Set([...A, ...B]).size;
    if (uni > 12 && inter / uni > 0.75) warnings.push({ check: 'near_duplicate_sentence', detail: `${sents[i].text} || ${sents[j].text}` });
  }
  // 4. contradictions: opposed readings both narrated must share a paragraph that says how they relate (an interaction sentence)
  const paraOf = (q: string) => paras.find(p => p.text.includes(`“${q}”`));
  const rel = relIndexOf(k);
  const person = (p: string) => p === 'Mệnh' || p === 'chart' || !!chart.palaces.find(x => x.name === p)?.is_than;
  for (const c1 of claims) for (const c2 of claims) {
    if (c1.id >= c2.id || c1.role === 'timing' || c2.role === 'timing') continue;
    const p1 = c1.quotes.map(paraOf).find(Boolean), p2 = c2.quotes.map(paraOf).find(Boolean);
    if (!p1 || !p2) continue;
    if (!opposedPair(c1, c2, rel, person)) continue;
    // explained when the two sides meet in one paragraph that says how they relate: the limiting reading sits next to a reading of the
    // same facet and opposite direction (the same claim, or another one of its side) and the paragraph carries an interaction sentence
    // the limiting side is the lower one (- < ~ < +): a mixed reading set against a favourable one limits it
    const rank = (c: Claim) => c.polarity === '-' ? 0 : c.polarity === '~' ? 1 : 2;
    const [pos, neg] = rank(c1) < rank(c2) ? [c2, c1] : [c1, c2];
    const side = claims.filter(c => c.facet === pos.facet && c.polarity !== '-' && c.palace === pos.palace);
    const explained = paras.some(p => p.sentences.some(s => s.kind === 'interaction') && neg.quotes.some(q => p.text.includes(`“${q}”`)) &&
      side.some(c => c.quotes.some(q => p.text.includes(`“${q}”`)))) ||
      paras.some(p => p.sentences.some(s => s.kind === 'interaction' && c1.quotes.some(q => s.text.includes(q)) && c2.quotes.some(q => s.text.includes(q))));
    // a counter-reading is argued against its theme's lead in an interaction sentence; the theme's supports stand with that lead
    const viaTheme = graphs.some(a => [...a.themes, ...a.envThemes].some(t => t.counters.some(x => x.claim === neg) && [t.lead, ...t.support].includes(pos))) &&
      paras.some(p => p.sentences.some(s => s.kind === 'interaction' && neg.quotes.some(q => s.text.includes(q))));
    // ... or the limiting reading's own sentence points back to the lead of the theme the favourable reading belongs to
    const viaBackRef = graphs.some(a => [...a.themes, ...a.envThemes].some(t => [t.lead, ...t.support].includes(pos) &&
      paras.some(p => p.sentences.some(s => s.kind === 'interaction' && neg.quotes.some(q => s.text.includes(q)) && t.lead.quotes.some(q => s.text.includes(q))))));
    if (!explained && !viaTheme && !viaBackRef) warnings.push({ check: 'contradiction_not_explained', detail: `${c1.quotes[0]} <> ${c2.quotes[0]}` });
  }
  // 5. repetition
  // page citations are required on every book sentence; they are not counted as repeated wording
  const toks = words(stripQuotes(text).replace(/\([^()]*tr\.[^()]*\)/g, ' ').toLowerCase());
  const grams = new Map<string, number>();
  for (let i = 0; i + 3 < toks.length; i++) { const g = toks.slice(i, i + 4).join(' '); grams.set(g, (grams.get(g) ?? 0) + 1); }
  const rep = [...grams.values()].filter(v => v > 1).reduce((x, v) => x + v - 1, 0) / Math.max(1, grams.size);
  if (rep > 0.08) warnings.push({ check: 'excessive_repetition', detail: `repeated 4-gram rate ${rep.toFixed(3)}` });
  let same = 0;
  for (let i = 1; i < sents.length; i++) if (opener(sents[i].text) === opener(sents[i - 1].text)) same++;
  if (same > 1) warnings.push({ check: 'repeated_openers', detail: `${same} consecutive sentences start alike` });
  // 6. personalization and generic filler
  const bz = chart.bazi ? Object.values(chart.bazi.pillars).flatMap(p => [p.name, p.stem, p.branch]) : [];
  const tokens = new Set<string>([...chart.palaces.flatMap(p => p.stars), ...chart.palaces.map(p => p.branch), String(chart.year.year), ...PALACES, ...bz]);
  const specific = (t: string) => [...tokens].some(x => t.includes(x)) || /\d+–\d+|“/.test(t);
  const personal = sents.filter(s => specific(s.text)).length / Math.max(1, sents.length);
  const framingOnly = claims.every(c => !c.grounds.some(g => g.independent));
  if (sents.length >= 4 && personal < 0.6 && !framingOnly) warnings.push({ check: 'weak_personalization', detail: `${(personal * 100).toFixed(0)}% of sentences name chart-specific facts` });
  const generic = sents.filter(s => (s.basis === 'he_thong' || s.basis === 'dieu_kien') && !['limits', 'notice', 'reflection', 'method'].includes(s.kind) && !specific(s.text));
  if (generic.length / Math.max(1, sents.length) > 0.2) warnings.push({ check: 'generic_filler', detail: `${generic.length} system sentences name nothing of this chart: ${generic.slice(0, 2).map(s => s.text).join(' | ')}` });
  // 7. length vs evidence: never inflate
  // evidence units: independent grounds of the readings + sourced reference sentences (palace roles, star profiles, time readings)
  const grounds = claims.reduce((n, c) => n + c.grounds.filter(g => g.independent).length, 0);
  const units = grounds + sents.filter(s => s.basis === 'sach' && !s.rules.some(r => firedVerified.has(r))).length;
  const wc = words(text).length;
  if (units && grounds && wc / units > 160) warnings.push({ check: 'possible_inflation', detail: `${wc} words for ${units} evidence units (${grounds} independent grounds)` });
  if (wc > 1500) warnings.push({ check: 'over_budget', detail: `${wc} words (major chapters target 800–1,500 when evidence allows)` });
  if (wc < 250 && grounds >= 8) warnings.push({ check: 'thin_for_evidence', detail: `${wc} words for ${grounds} grounds` });

  const mods = [...new Set(sents.map(s => s.module))].map(id => k.modules.find(m => m.id === id)!).filter(Boolean).map(m => ({ id: m.id, version: m.version, status: m.status }));
  const allApproved = mods.length > 0 && mods.every(m => m.status === 'approved');
  const bySource: Record<string, number> = {};
  for (const s of sents) bySource[s.basis] = (bySource[s.basis] ?? 0) + 1;
  const notice = checkNotice(paras, sensitive);
  if (notice) errors.push(notice);
  return {
    pass: errors.length === 0, errors, warnings,
    metrics: { words: wc, sentences: sents.length, paragraphs: paras.length, bySource, independentGrounds: grounds, wordsPerGround: grounds ? Math.round(wc / grounds) : 0,
      repeated4gramRate: Number(rep.toFixed(3)), consecutiveSameOpener: same, personalization: Number(personal.toFixed(2)),
      citedBookSentences: sents.filter(s => s.basis === 'sach' && (s.cites.length || /tr\.\s?\d/.test(s.text))).length, quotes: (text.match(/“/g) ?? []).length,
      genericSentences: generic.length },
    editorial: { modules: mods, allApproved,
      notice: allApproved ? 'Các module nội dung đã được chuyên gia duyệt.' : 'Nội dung biên tập của chương này đang ở trạng thái nháp, chưa qua thẩm định chuyên gia; mọi câu sách đều có truy vết nhưng cách tổ chức lập luận cần được duyệt.' },
  };
}

/** The sensitivity notice a chapter must carry (checked by the pipeline with the chapter spec). */
export function checkNotice(paras: Paragraph[], sensitive: string | undefined): { check: string; detail: string } | null {
  if (!sensitive) return null;
  const has = paras.some(p => p.sentences.some(s => s.kind === 'notice' && NOTICE[sensitive]?.test(s.text)));
  return has ? null : { check: 'missing_notice', detail: `chapter is '${sensitive}'-sensitive but carries no notice` };
}
