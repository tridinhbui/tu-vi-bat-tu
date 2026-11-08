// Style measures of the reader's report (plan THIEN-BAN-33 G10.4 / G10.7): habitual additive openers, the same causal joint repeated in a
// paragraph, sentences over 35 words, paragraphs chosen for the model pass (refine/refine.ts polishScore), before and after the
// deterministic style pass (prose/checked.ts connectorParagraphs).
//   node tools/interpret/eval_style.ts [--n 40]
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import type { ChartInput, Knowledge } from '../../src/interpret/types.ts';
import type { ProseParagraph } from '../../src/interpret/prose/realize.ts';
import { proseAllChapters } from '../../src/interpret/route.ts';
import { checkedOnly } from '../../src/interpret/prose/checked.ts';
import { polishScore } from '../../src/interpret/refine/refine.ts';
const arg = (k: string, d: string) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const K: Knowledge = JSON.parse(readFileSync('src/interpret/generated/knowledge.json', 'utf8'));
const corpus = (JSON.parse(gunzipSync(readFileSync('src/interpret/test/fixtures/corpus1000.json.gz')).toString()) as Array<{ facts: ChartInput }>).slice(0, Number(arg('--n', '40')));
const HABIT = /^(Bên cạnh đó|Ngoài ra|Thêm vào đó|Thêm nữa|Hơn nữa|Song song với điều ấy|Cùng với đó),/u;
type Ch = { chapter: string; paragraphs: ProseParagraph[] };
const measure = (chs: Ch[]) => {
  const ps = chs.flatMap(c => c.paragraphs), ss = ps.flatMap(p => p.sentences);
  return { sentences: ss.length, habit: ss.filter(s => HABIT.test(s.text)).length,
    repeatHabit: ps.filter(p => p.sentences.filter(s => HABIT.test(s.text)).length >= 2).length,
    repeatCausal: ps.filter(p => p.sentences.filter(s => s.text.includes('; vì vậy ')).length >= 2).length,
    long: ss.filter(s => s.text.split(/\s+/).length > 35).length, polish: ps.filter(p => polishScore(p) >= 2).length };
};
const sum = (a: ReturnType<typeof measure>, b: ReturnType<typeof measure>) => Object.fromEntries(Object.keys(a).map(k => [k, (a as never)[k] + (b as never)[k]])) as ReturnType<typeof measure>;
let before = measure([]), after = measure([]);
for (const c of corpus) {
  const raw = proseAllChapters(c.facts, K, { allowDraft: true, deep: true, luan: true }) as unknown as Ch[];
  before = sum(before, measure(raw));
  after = sum(after, measure(raw.map(x => checkedOnly(x as never, c.facts, K)) as unknown as Ch[]));
}
const per100 = (m: ReturnType<typeof measure>, k: keyof ReturnType<typeof measure>) => (100 * m[k] / Math.max(1, m.sentences)).toFixed(2);
console.log(`${corpus.length} charts`);
for (const [label, m] of [['before', before], ['after', after]] as const)
  console.log(`${label.padEnd(7)} sentences ${m.sentences}, habitual openers ${m.habit} (${per100(m, 'habit')}/100), paragraphs repeating one ${m.repeatHabit}, repeating "; vì vậy" ${m.repeatCausal}, over 35 words ${per100(m, 'long')}%, polish candidates ${m.polish}`);
