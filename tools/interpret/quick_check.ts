// A check in seconds before the long suites (lessons of 2026-10-23/25: most red runs were a meta word in a new frame, a long new sentence,
// or a blocking validator error, each found only after 20+ minutes of the whole suite):
//   node tools/interpret/quick_check.ts [--n 20]
//   1. every frame of the reader-prose libraries (content/prose/*.json, not the concept cards) is free of META words and absolutes;
//   2. the whole report of the three reference charts and the first N corpus charts: no blocking validator issue in any chapter, no META
//      word in a sentence; the share of sentences over 35 words is printed as a pointer (the gate itself is readable.test.ts).
// Exit code 1 on any failure. Then run only the test files of the modules you touched; the whole suite before a push to main.
import { readFileSync, readdirSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import type { ChartInput, Knowledge } from '../../src/interpret/types.ts';
import { proseAllChapters } from '../../src/interpret/route.ts';
import { checkedOnly } from '../../src/interpret/prose/checked.ts';
import { META, ABSOLUTE } from '../../src/interpret/prose/lint.ts';

const ROOT = join(import.meta.dirname, '..', '..');
const arg = (k: string, d: string) => process.argv.includes(k) ? process.argv[process.argv.indexOf(k) + 1] : d;
const K: Knowledge = JSON.parse(readFileSync(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'), 'utf8'));
const FX = join(ROOT, 'src', 'interpret', 'test', 'fixtures');
const bad: string[] = [];

// 1. frames
const P = join(ROOT, 'src', 'interpret', 'content', 'prose');
for (const f of readdirSync(P).filter(x => x.endsWith('.json') && !x.startsWith('concepts_'))) {
  const walk = (x: unknown, at: string): void => {
    if (typeof x === 'string') {
      // a regex field is not text; "chưa đủ căn cứ" is the owner's own wording for a period with no book evidence (decision 2026-10-24)
      if (at.endsWith('.note') || at === 'note' || at.endsWith('.match') || at.startsWith('level_thin')) return;
      const low = ' ' + x.toLowerCase();
      for (const w of META) if (low.includes(' ' + w)) bad.push(`frame ${f}:${at}: meta "${w.trim()}"`);
      for (const w of ABSOLUTE) if (low.includes(w)) bad.push(`frame ${f}:${at}: absolute "${w}"`);
    } else if (Array.isArray(x)) x.forEach((y, i) => walk(y, `${at}[${i}]`));
    else if (x && typeof x === 'object') for (const [k, v] of Object.entries(x)) if (k !== 'note' && k !== 'weigh_note') walk(v, at ? `${at}.${k}` : k);
  };
  walk(JSON.parse(readFileSync(join(P, f), 'utf8')), '');
}

// 2. reports
const refs = Object.entries(JSON.parse(readFileSync(join(FX, 'deep_reference_charts.json'), 'utf8')) as Record<string, ChartInput>);
const corpus = (JSON.parse(gunzipSync(readFileSync(join(FX, 'corpus1000.json.gz'))).toString()) as Array<{ facts: ChartInput }>).slice(0, Number(arg('--n', '20')));
const charts: Array<[string, ChartInput]> = [...refs, ...corpus.map((c, i) => [`corpus#${i}`, c.facts] as [string, ChartInput])];
let n = 0, long = 0;
const t0 = Date.now();
for (const [label, f] of charts) {
  for (const ch of proseAllChapters(f, K, { allowDraft: true, deep: true, luan: true })) {
    const c = checkedOnly(ch as never) as unknown as { chapter: string; issues?: Array<{ level: string; code: string; msg: string }>; paragraphs: Array<{ sentences: Array<{ text: string }> }> };
    for (const i of (ch as { issues?: Array<{ level: string; code: string; msg: string }> }).issues ?? []) if (i.level === 'error') bad.push(`${label}/${c.chapter}: ${i.code}: ${i.msg.slice(0, 140)}`);
    for (const s of c.paragraphs.flatMap(p => p.sentences)) {
      n++;
      if (s.text.split(/\s+/).length > 35) long++;
      const low = ' ' + s.text.toLowerCase();
      for (const w of META) if (low.includes(' ' + w)) bad.push(`${label}/${c.chapter}: meta "${w.trim()}": ${s.text.slice(0, 140)}`);
    }
  }
}
// the readability gate (readable.test.ts) measures its own chart set; here the share is a pointer, not a failure
const share = long / Math.max(1, n);
console.log(`${charts.length} charts, ${n} sentences, ${(100 * share).toFixed(1)} % over 35 words, ${((Date.now() - t0) / 1000).toFixed(0)} s`);
for (const b of [...new Set(bad)].slice(0, 40)) console.log('✖', b);
console.log(bad.length ? `${bad.length} problem(s)` : 'ok');
process.exit(bad.length ? 1 : 0);
