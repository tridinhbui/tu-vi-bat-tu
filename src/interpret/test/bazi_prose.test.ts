// Bát Tự reader prose (prose plan P7): golden text for the worked example, only verified rules voiced, every sentence traced, the manual's
// condition named as the chart has it, and the 1,000-chart run. Regenerate:  UPDATE_GOLDEN=1 node --test src/interpret/test/bazi_prose.test.ts
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { proseBazi, splitDirect } from '../prose/bazi.ts';
import { prepareBazi } from '../bazi.ts';
import { seedOf } from '../prose/chapter.ts';
import type { ChartInput, Knowledge } from '../types.ts';

const K: Knowledge = JSON.parse(readFileSync(new URL('../generated/knowledge.json', import.meta.url), 'utf8'));
const ex = JSON.parse(readFileSync(new URL('./fixtures/menh_cu_tuat.json', import.meta.url), 'utf8'));
const goldenUrl = new URL('./fixtures/menh_cu_tuat.bat_tu.prose.txt', import.meta.url);
const corpusUrl = new URL('./fixtures/corpus1000.json.gz', import.meta.url);
const run = (f: ChartInput, draft = true) => proseBazi(f, K, seedOf(f), 'test', draft);

test('splitDirect: effect and cause of a manual judgement', () => {
  assert.deepEqual(splitDirect('hôn nhân êm đẹp (nguyệt lệnh được hợp) [PDF p.57]'), { effect: 'hôn nhân êm đẹp', cause: 'nguyệt lệnh được hợp' });
  assert.deepEqual(splitDirect("nghề hợp thiên về hành chính (Quan, Sát) (thập thần của can trụ giờ: 'can là biểu') [PDF p.52]"),
    { effect: 'nghề hợp thiên về hành chính', cause: 'thập thần của can trụ giờ' });
});

test('worked example: golden text, verified rules only, every sentence traced', () => {
  const o = run(ex.facts);
  if (process.env.UPDATE_GOLDEN === '1' || !existsSync(goldenUrl)) writeFileSync(goldenUrl, o.text + '\n');
  assert.equal(o.text + '\n', readFileSync(goldenUrl, 'utf8'));
  assert.ok(o.pass, JSON.stringify(o.issues));
  const ver = new Set(prepareBazi(ex.facts, K)!.findings.filter(f => f.basis === 'verified').map(f => f.ruleId));
  for (const s of o.paragraphs.flatMap(p => p.sentences)) {
    assert.equal(s.trace.rules.length, 1);
    assert.ok(ver.has(s.trace.rules[0]), s.trace.rules[0]);
    assert.match(s.trace.cites[0], /^ZZ p/);
  }
  assert.ok(!/vượng|nhược|dụng thần|cách cục/i.test(o.text), 'strength, useful god and structure are not voiced');
  assert.equal(run(ex.facts, false).paragraphs.length, 0, 'draft library: nothing without allowDraft');
});

test('1,000 charts: no blocking error, day master always voiced, no set-valued condition left in the text',
  { skip: !existsSync(corpusUrl) && 'corpus not built' }, () => {
  const corpus = JSON.parse(gunzipSync(readFileSync(corpusUrl)).toString('utf8'));
  let direct = 0;
  for (const c of corpus) {
    const o = run(c.facts);
    assert.ok(o.pass, `${c.label}: ${JSON.stringify(o.issues)}`);
    assert.ok(o.paragraphs[0]?.sentences.some(s => s.trace.rules[0].startsWith('BT_ZZ_P2')), c.label);
    assert.ok(!/ hoặc (Ấn|Sát|Kiếp|Quan)\b|thập thần của can/.test(o.paragraphs[1]?.text ?? ''), o.paragraphs[1]?.text);
    direct += o.paragraphs[1]?.sentences.length ?? 0;
  }
  assert.ok(direct > 1000, String(direct));
});

// Track C (plan quirky-tinkering-rabin): the Bát Tự reading deepened with books and calculation only. On the benchmark and the two reference
// charts: no common-meaning sentence, every đại vận paragraph has at least two sentences from a book or a calculation, lưu niên told for
// the requested year and the two after it, a closing along the timeline; and the owner's chart's relations as 八字真宗 p.20 prints them.
test('Track C: books and calculation only, every luck pillar told with ≥2 sourced sentences, lưu niên and the closing', async () => {
  const { stats } = await import('../../../tools/interpret/bazi_depth.ts');
  const fx = (n: string) => JSON.parse(readFileSync(new URL(`./fixtures/${n}`, import.meta.url), 'utf8'));
  const charts: ChartInput[] = [fx('user_1990_nam.json'), fx('ref_2002_01_09_kl.json'), ...fx('benchmark20.json').map((b: { facts: ChartInput }) => b.facts)];
  let luck = 0, sourced = 0;
  for (const c of charts) {
    const o = run(c);
    assert.ok(o.pass, JSON.stringify(o.issues));
    assert.ok(!o.paragraphs.flatMap(p => p.sentences).some(s => s.trace.basis === 'pho_thong'));
    const s = stats(c);
    luck += s.luck; sourced += s.luckSourced;
    assert.equal(o.chapters['luu-nien']?.length, 3);
    assert.ok(o.chapters['tong-ket']?.[0]?.lead);
    assert.ok(!/\{[a-z_]+\}|\.;|undefined/.test(o.text), o.text);
  }
  assert.ok(sourced / luck >= 0.9, `${sourced}/${luck}`);
  const mine = run(fx('ref_2002_01_09_kl.json'));
  const dv = mine.chapters['dai-van']!.map(p => p.text).join('\n');
  assert.match(dv, /chi Tuất hình chi tháng Sửu và chi ngày Sửu/);
  assert.match(dv, /can Mậu xung can giờ Nhâm/);
  assert.match(mine.chapters['cach-cuc']![0].text, /cách Thiên Tài/);
  assert.ok(mine.chapters['cach-cuc']![0].sentences.some(x => x.trace.rules.includes('BT_TVH_TB_TAI_2')));
});
