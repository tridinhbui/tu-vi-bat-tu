// Reader-prose validation (prose plan §4.7). Errors block publication; metrics feed the 1,000-chart evaluation (plan §6).
import type { Resolved } from '../kg/resolve.ts';
import { ABSOLUTE, META } from './lint.ts';
import type { ProseParagraph } from './realize.ts';

export interface ProseIssue { level: 'error' | 'warning'; code: string; where: string; msg: string }
export interface ProseMetrics { words: number; sentences: number; meanSentenceWords: number; sdSentenceWords: number; repeated4gramRate: number; openers: string[] }

export function validateProse(paras: ProseParagraph[], resolved: Resolved[]): { issues: ProseIssue[]; metrics: ProseMetrics } {
  const issues: ProseIssue[] = [];
  const status = new Map(resolved.map(r => [`${r.ruleId}|${r.concept}`, r.status]));
  paras.forEach((p, pi) => {
    const saidHere = new Set<string>();
    p.sentences.forEach((s, si) => {
      const where = `p${pi + 1}s${si + 1}`, low = ' ' + s.text.toLowerCase();
      for (const w of META) if (low.includes(' ' + w)) issues.push({ level: 'error', code: 'meta_language', where, msg: `"${w.trim()}" in: ${s.text}` });
      for (const w of ABSOLUTE) if (low.includes(w)) issues.push({ level: 'error', code: 'absolute', where, msg: `"${w}" in: ${s.text}` });
      if (/\{[a-zA-Z0-9_.]+\}/.test(s.text)) issues.push({ level: 'error', code: 'unfilled_slot', where, msg: s.text });
      const t = s.trace;
      if (t.basis === 'sach' && !t.rules.length) issues.push({ level: 'error', code: 'uncited_factual_sentence', where, msg: s.text });
      if (t.basis === 'he_thong' && t.concepts.some(c => !saidHere.has(c))) issues.push({ level: 'error', code: 'editorial_new_claim', where, msg: `${t.concepts.filter(c => !saidHere.has(c)).join(', ')} not said before: ${s.text}` });
      for (const c of t.concepts) for (const r of t.rules) if (status.get(`${r}|${c}`) === 'voided') issues.push({ level: 'error', code: 'voided_asserted', where, msg: `${r} ${c}` });
      t.concepts.forEach(c => saidHere.add(c));
    });
  });
  const sentences = paras.flatMap(p => p.sentences.map(s => s.text));
  const lens = sentences.map(s => s.split(/\s+/).length);
  const mean = lens.reduce((a, b) => a + b, 0) / Math.max(1, lens.length);
  const sd = Math.sqrt(lens.reduce((a, b) => a + (b - mean) ** 2, 0) / Math.max(1, lens.length));
  const words = sentences.join(' ').toLowerCase().replace(/[.,;:!?“”"()]/g, '').split(/\s+/).filter(Boolean);
  const grams = new Map<string, number>();
  for (let i = 0; i + 4 <= words.length; i++) { const g = words.slice(i, i + 4).join(' '); grams.set(g, (grams.get(g) ?? 0) + 1); }
  const total = Math.max(1, words.length - 3), rep = [...grams.values()].filter(n => n > 1).reduce((a, n) => a + n - 1, 0);
  const openers = sentences.map(s => s.split(/\s+/).slice(0, 2).join(' '));
  for (let i = 1; i < openers.length; i++) if (openers[i] === openers[i - 1]) issues.push({ level: 'warning', code: 'repeated_opener', where: `s${i + 1}`, msg: openers[i] });
  return { issues, metrics: { words: words.length, sentences: sentences.length, meanSentenceWords: +mean.toFixed(1), sdSentenceWords: +sd.toFixed(1), repeated4gramRate: +(rep / total).toFixed(3), openers } };
}
