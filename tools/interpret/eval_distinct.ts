// Content distinctiveness and counterfactual sensitivity of the Mệnh chapter (plan quirky-tinkering-rabin R0/R5). Unlike eval_prose.ts, which
// measures wording, this measures WHAT is said: would the same content fit most other charts, and does it move when a key element moves?
//   node tools/interpret/eval_distinct.ts [--engine old|reasoned] [--n 1000] [--out docs/REASONER-BASELINE.md]
// Measures (all automatic, none is a judgement of a practitioner):
//   barnum        mean base rate (engine/data/kg/base_rates.json) of the concepts voiced; lower = less of what everyone gets
//   common share  share of voiced concepts asserted on ≥ 50 % of the corpus
//   grounding     per sentence, the base rate of the rarest rule it stands on; mean over sentences (lower = more specific grounds)
//   content J     median Jaccard of voiced concept sets between charts with the same Mệnh chính tinh (corpus)
//   strip sim     median word-trigram Jaccard between charts with DIFFERENT Mệnh chính tinh, star/palace/branch names removed
//   critical      a one-factor variant of a benchmark chart that should change the reading: share where the voiced concepts changed AND
//                 the change involves a rule whose conditions name the changed element; text similarity to the base chart
//   inert         a control variant: share where the voiced concepts stayed identical; text similarity
import { readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import { proseChapter } from '../../src/interpret/prose/chapter.ts';
import type { Knowledge } from '../../src/interpret/types.ts';

const ROOT = join(import.meta.dirname, '..', '..');
const FX = join(ROOT, 'src', 'interpret', 'test', 'fixtures');
const arg = (k: string, d: string) => process.argv.includes(k) ? process.argv[process.argv.indexOf(k) + 1] : d;

/** What an engine said for one chart's Mệnh chapter: the text and, per sentence, the concepts and rules it voices. */
export interface Said { text: string; sentences: Array<{ text: string; concepts: string[]; rules: string[] }> }
export type Engine = (facts: any, k: Knowledge) => Said;

export const oldEngine: Engine = (facts, k) => {
  const o = proseChapter(facts, k, 'menh', { allowDraft: true });
  return { text: o.text, sentences: o.paragraphs.flatMap(p => p.sentences.map(s => ({ text: s.text, concepts: s.trace.concepts, rules: s.trace.rules }))) };
};

const STARS = ['Tử Vi', 'Thiên Cơ', 'Thái Dương', 'Vũ Khúc', 'Thiên Đồng', 'Liêm Trinh', 'Thiên Phủ', 'Thái Âm', 'Tham Lang', 'Cự Môn', 'Thiên Tướng', 'Thiên Lương',
  'Thất Sát', 'Phá Quân', 'Kình Dương', 'Đà La', 'Hỏa Tinh', 'Linh Tinh', 'Địa Không', 'Địa Kiếp', 'Tả Phụ', 'Hữu Bật', 'Văn Xương', 'Văn Khúc', 'Thiên Khôi',
  'Thiên Việt', 'Lộc Tồn', 'Thiên Mã', 'Hóa Lộc', 'Hóa Quyền', 'Hóa Khoa', 'Hóa Kỵ', 'Tuần', 'Triệt'];
const NAMES = new RegExp([...STARS, 'Mệnh', 'Tài Bạch', 'Quan Lộc', 'Thiên Di', 'Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi',
  'miếu', 'vượng', 'đắc', 'hãm', 'bình',
  // the same brightness written as a label, "Cự Môn (Hãm Địa)" (prose/named.ts): a chart fact like "hãm", not template wording
  'Miếu Địa', 'Vượng Địa', 'Đắc Địa', 'Lợi Địa', 'Bình Hòa', 'Hãm Địa'].sort((a, b) => b.length - a.length).join('|'), 'g');
const words = (t: string) => t.toLowerCase().replace(/[.,;:!?()“”"]/g, ' ').split(/\s+/).filter(Boolean);
const grams = (t: string, n = 3) => { const w = words(t), s = new Set<string>(); for (let i = 0; i + n <= w.length; i++) s.add(w.slice(i, i + n).join(' ')); return s; };
const jac = <T>(a: Set<T>, b: Set<T>) => { if (!a.size && !b.size) return 1; let i = 0; for (const x of a) if (b.has(x)) i++; return i / (a.size + b.size - i); };
const median = (xs: number[]) => { const s = [...xs].sort((a, b) => a - b); return s.length ? s[Math.floor(s.length / 2)] : 0; };
const mean = (xs: number[]) => xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : 0;
const r3 = (x: number) => +x.toFixed(3);
const concepts = (s: Said) => new Set(s.sentences.flatMap(x => x.concepts));
const majorsOf = (facts: any) => (facts.palaces.find((p: any) => p.name === 'Mệnh').major_stars as string[]).join('+') || 'VCD';

export interface DistinctEval {
  charts: number; barnum: number; commonShare: number; grounding: number; contentJ: number; stripSim: number; emptyShare: number;
  top: Array<[string, number]>;
}
export function distinct(engine: Engine, k: Knowledge, charts: any[], rates: any): DistinctEval {
  const said = charts.map(c => ({ c, s: engine(c.facts, k) }));
  const cr = (id: string) => rates.concept[id] ?? 0, rr = (id: string) => rates.rule[id] ?? 0;
  // a cách cục state (cach:<id>:<state>) is content, but not a KG concept with a base rate: it is left out of the Barnum measures
  const per = said.map(({ s }) => [...concepts(s)].filter(x => !x.startsWith('cach:')));
  const voiced = per.flat();
  const groundings = said.flatMap(({ s }) => s.sentences.filter(x => x.rules.length).map(x => Math.min(...x.rules.map(rr))));
  const groups = new Map<string, Array<Set<string>>>();
  said.forEach(({ c, s }) => { const g = majorsOf(c.facts); (groups.get(g) ?? groups.set(g, []).get(g)!).push(concepts(s)); });
  const js: number[] = [];
  for (const g of groups.values()) for (let i = 0; i < g.length && i < 15; i++) for (let j = i + 1; j < g.length && j < 15; j++) js.push(jac(g[i], g[j]));
  const stripped = said.map(({ c, s }) => ({ g: majorsOf(c.facts), t: grams(s.text.replace(NAMES, '_')) }));
  const ss: number[] = [];
  for (let i = 0; i < stripped.length && i < 300; i++) for (let j = i + 1; j < stripped.length && j < 300; j += 7) if (stripped[i].g !== stripped[j].g) ss.push(jac(stripped[i].t, stripped[j].t));
  const freq = new Map<string, number>(); voiced.forEach(x => freq.set(x, (freq.get(x) ?? 0) + 1));
  return {
    charts: charts.length, barnum: r3(mean(per.map(cs => mean(cs.map(cr))).filter((_, i) => per[i].length))), commonShare: r3(voiced.filter(x => cr(x) >= 0.5).length / Math.max(1, voiced.length)),
    grounding: r3(mean(groundings)), contentJ: r3(median(js)), stripSim: r3(median(ss)), emptyShare: r3(said.filter(({ s }) => !s.sentences.length).length / charts.length),
    top: [...freq.entries()].sort((a, b) => b[1] - a[1]).slice(0, 10).map(([x, n]) => [x, r3(n / charts.length)]),
  };
}

export interface CounterEval {
  critical: number; criticalChanged: number; criticalLocal: number; criticalTextSim: number;
  inert: number; inertSame: number; inertTextSim: number; byKind: Record<string, { n: number; changed: number; local: number; textSim: number }>;
  rows: Array<{ base: string; kind: string; note: string; expect: string; changed: boolean; local: boolean; textSim: number; added: string[]; removed: string[] }>;
}
export function counterfactual(engine: Engine, k: Knowledge, bench: any[], variants: any[]): CounterEval {
  const rmap = new Map(k.rules.map(r => [r.id, r]));
  const baseSaid = new Map(bench.map(b => [b.label, engine(b.facts, k)]));
  const fdef = new Map((k.kg?.formations ?? []).map(f => [f.id, f]));
  const mentions = (ruleId: string, el: string) => {
    if (ruleId.startsWith('cach:')) { const f = fdef.get(ruleId.split(':')[1]); const t = JSON.stringify(f ?? ''); return el === 'Tuần' ? t.includes('tuan') : t.includes(`"${el}"`) || t.includes(el); }
    const r = rmap.get(ruleId); if (!r) return false;
    const t = JSON.stringify([r.conditions, r.exceptions ?? null]);
    return el === 'Tuần' ? t.includes('palace.tuan') : t.includes(`"${el}"`) || (el.startsWith('Hóa') && t.includes(el));
  };
  const rows: CounterEval['rows'] = [];
  for (const v of variants) {
    const a = baseSaid.get(v.base)!, b = engine(v.facts, k);
    const ca = concepts(a), cb = concepts(b);
    const changed = jac(ca, cb) < 1;
    // a cách cục state counts as its own evidence item (its definition names the stars it rests on)
    const items = (s: Said) => new Set(s.sentences.flatMap(x => [...x.rules, ...x.concepts.filter(c => c.startsWith('cach:'))]));
    const ra = items(a), rb = items(b);
    const diffRules = [...ra].filter(x => !rb.has(x)).concat([...rb].filter(x => !ra.has(x)));
    const el = v.kind === 'flip_dignity' ? v.element : v.element;
    const local = changed && diffRules.some(id => mentions(id, el));
    rows.push({ base: v.base, kind: v.kind, note: v.note, expect: v.expect, changed, local, textSim: r3(jac(grams(a.text), grams(b.text))),
      added: [...cb].filter(x => !ca.has(x)), removed: [...ca].filter(x => !cb.has(x)) });
  }
  const crit = rows.filter(r => r.expect === 'critical'), inert = rows.filter(r => r.expect === 'inert');
  const byKind: CounterEval['byKind'] = {};
  for (const r of rows) {
    const e = byKind[r.kind] ??= { n: 0, changed: 0, local: 0, textSim: 0 };
    e.n++; e.changed += +r.changed; e.local += +r.local; e.textSim += r.textSim;
  }
  for (const e of Object.values(byKind)) e.textSim = r3(e.textSim / e.n);
  return {
    critical: crit.length, criticalChanged: r3(crit.filter(r => r.changed).length / crit.length), criticalLocal: r3(crit.filter(r => r.local).length / crit.length),
    criticalTextSim: r3(mean(crit.map(r => r.textSim))), inert: inert.length, inertSame: r3(inert.filter(r => !r.changed).length / Math.max(1, inert.length)),
    inertTextSim: r3(mean(inert.map(r => r.textSim))), byKind, rows,
  };
}

export function loadSets() {
  const K: Knowledge = JSON.parse(readFileSync(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'), 'utf8'));
  const rates = JSON.parse(readFileSync(join(ROOT, 'engine', 'data', 'kg', 'base_rates.json'), 'utf8'));
  const corpus = JSON.parse(gunzipSync(readFileSync(join(FX, 'corpus1000.json.gz'))).toString('utf8'));
  const bench = JSON.parse(readFileSync(join(FX, 'benchmark20.json'), 'utf8'));
  const variants = JSON.parse(gunzipSync(readFileSync(join(FX, 'counterfactual100.json.gz'))).toString('utf8'));
  return { K, rates, corpus, bench, variants };
}

export function report(name: string, engine: Engine, n: number): string {
  const { K, rates, corpus, bench, variants } = loadSets();
  const d = distinct(engine, K, corpus.slice(0, n), rates), b = distinct(engine, K, bench, rates), c = counterfactual(engine, K, bench, variants);
  const pct = (x: number) => `${(100 * x).toFixed(1)}%`;
  const benchRows = bench.map((x: any) => {
    const s = engine(x.facts, K), cs = [...concepts(s)];
    return `| ${x.label} | ${cs.map(id => `${id} (${pct(rates.concept[id] ?? 0)})`).join(', ') || '—'} | ${pct(mean(cs.map(id => rates.concept[id] ?? 0)))} |`;
  });
  return [`# Đặc trưng nội dung chương Mệnh — engine \`${name}\``, '',
    `Sinh bởi \`tools/interpret/eval_distinct.ts --engine ${name}\` (knowledge \`${K.version}\`). Đo **nội dung** được nói ra (khái niệm, luật), không đo câu chữ. Tất cả là kiểm tra tự động; chưa có chuyên gia chấm.`, '',
    '## Đặc trưng trên corpus và bộ chuẩn', '',
    '| Chỉ số | corpus (' + d.charts + ' lá) | benchmark20 |', '|---|---|---|',
    `| Barnum: tần suất nền TB của khái niệm được nói (thấp = đặc trưng) | ${pct(d.barnum)} | ${pct(b.barnum)} |`,
    `| Tỉ lệ khái niệm được nói mà ≥ 50% lá số đều có | ${pct(d.commonShare)} | ${pct(b.commonShare)} |`,
    `| Căn cứ: tần suất bắn TB của luật hiếm nhất mỗi câu | ${pct(d.grounding)} | ${pct(b.grounding)} |`,
    `| Jaccard tập khái niệm, cùng chính tinh Mệnh (trung vị) | ${d.contentJ} | ${b.contentJ} |`,
    `| Strip test: trigram sau khi bỏ tên sao/cung, khác chính tinh (trung vị) | ${d.stripSim} | ${b.stripSim} |`,
    `| Chương rỗng | ${pct(d.emptyShare)} | ${pct(b.emptyShare)} |`, '',
    `Khái niệm được nói nhiều nhất (corpus): ${d.top.map(([x, v]) => `${x} ${pct(v)}`).join(', ')}`, '',
    '## Phản thực một yếu tố (counterfactual)', '',
    '| Nhóm | Số biến thể | Khái niệm đổi | Đổi đúng chỗ (luật nhắc yếu tố) | Độ giống văn với lá gốc (trigram) |', '|---|---|---|---|---|',
    `| critical (phải đổi) | ${c.critical} | ${pct(c.criticalChanged)} | ${pct(c.criticalLocal)} | ${c.criticalTextSim} |`,
    `| inert (không được đổi) | ${c.inert} | ${pct(1 - c.inertSame)} | — | ${c.inertTextSim} |`, '',
    '| Loại biến thể | n | đổi | đúng chỗ | giống văn |', '|---|---|---|---|---|',
    ...Object.entries(c.byKind).map(([k, e]) => `| ${k} | ${e.n} | ${e.changed} | ${e.local} | ${e.textSim} |`), '',
    '## Bộ chuẩn 20 lá: khái niệm được nói (tần suất nền)', '', '| Lá | Khái niệm | Barnum |', '|---|---|---|', ...benchRows, '',
    '## Chi tiết biến thể', '', '| Lá gốc | Biến thể | Kỳ vọng | Đổi | Đúng chỗ | Giống văn | Thêm | Bớt |', '|---|---|---|---|---|---|---|---|',
    ...c.rows.map(r => `| ${r.base} | ${r.note} | ${r.expect} | ${r.changed ? 'có' : 'không'} | ${r.local ? 'có' : '—'} | ${r.textSim} | ${r.added.join(', ')} | ${r.removed.join(', ')} |`), ''].join('\n');
}

if (import.meta.main) {
  const name = arg('--engine', 'old');
  const engines: Record<string, () => Promise<Engine>> = {
    old: async () => oldEngine,
    reasoned: async () => (await import('../../src/interpret/prose/narrative.ts')).reasonedSaid as Engine,
    // the luận cung Mệnh chapter (prose/luan.ts): the same plan as 'reasoned', in the reference reading's shape
    luan: async () => (await import('../../src/interpret/prose/luan.ts')).luanSaid as Engine,
  };
  const eng = await engines[name]();
  const md = report(name, eng, Number(arg('--n', '1000')));
  const out = arg('--out', join('docs', name === 'old' ? 'REASONER-BASELINE.md' : name === 'luan' ? 'LUAN-EVAL.md' : 'REASONER-EVAL.md'));
  writeFileSync(join(ROOT, out), md);
  console.log(md.split('\n').slice(0, 26).join('\n'));
}
