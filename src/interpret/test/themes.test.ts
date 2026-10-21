// The themed reading (prose-style plan S1–S2): the overview block and the sections argued from the reasoner's plans. Gates: no blocking
// error on any corpus chart; every book sentence traces to a fired, verified rule; the overview names only chart facts and the độ số
// readings that fired, never a meaning for the nạp âm name. Golden: UPDATE_GOLDEN=1 regenerates menh_cu_tuat.themes.txt.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import type { Knowledge } from '../types.ts';
import { run } from '../engine.ts';
import { proseThemes } from '../prose/themes.ts';

const FX = join(import.meta.dirname, 'fixtures');
const K: Knowledge = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'generated', 'knowledge.json'), 'utf8'));
const load = (f: string) => { const x = JSON.parse(readFileSync(join(FX, f), 'utf8')); return x.facts ?? x; };
const corpus = JSON.parse(gunzipSync(readFileSync(join(FX, 'corpus1000.json.gz'))).toString('utf8'));
const rmap = new Map(K.rules.map(r => [r.id, r]));

test('worked example: overview names Mệnh and Thân star by star with checked brightness, and the độ số that fired', () => {
  const ch = proseThemes(load('menh_cu_tuat.json'), K, 'test', { allowDraft: true });
  const ov = ch.find(c => c.chapter === 'tong_quan')!;
  assert.ok(ov.pass, JSON.stringify(ov.issues));
  assert.match(ov.text, /Cự Môn \(Hãm Địa\) hóa Lộc tọa thủ/);
  assert.match(ov.text, /Kình Dương \(Đắc Địa\)/);
  assert.match(ov.text, /Tài Bạch/, 'Thân cư Tài Bạch');
  assert.match(ov.text, /Cục khắc Mệnh/);
  assert.equal(ov.card.find(f => f.key === 'menh_chu')?.basis, 'pho_thong');
  const golden = join(FX, 'menh_cu_tuat.themes.txt'), text = ch.map(c => `== ${c.chapter}\n${c.text}`).join('\n\n') + '\n';
  if (process.env.UPDATE_GOLDEN || !existsSync(golden)) writeFileSync(golden, text);
  assert.equal(text, readFileSync(golden, 'utf8'));
});

test('corpus: every themed section passes, book sentences trace to fired verified rules, no nạp âm meaning', () => {
  for (const c of corpus.slice(0, 400)) {
    const facts = c.facts;
    const fired = new Set(run(K.rules, K.sources, facts.base).findings.map(f => f.ruleId));
    for (const ch of proseThemes(facts, K, 'test', { allowDraft: true })) {
      assert.ok(ch.pass, `${c.id ?? ''} ${ch.chapter}: ${JSON.stringify(ch.issues.filter(i => i.level === 'error'))}`);
      for (const p of ch.paragraphs) for (const s of p.sentences) {
        assert.ok(s.trace.step, `no step: ${s.text}`);
        if (s.trace.basis === 'sach') for (const id of s.trace.rules) {
          assert.ok(fired.has(id), `${id} did not fire: ${s.text}`);
          assert.equal(rmap.get(id)?.reviewStatus, 'verified', `${id} is not verified: ${s.text}`);
        }
      }
      if (ch.chapter === 'tong_quan') assert.ok(!new RegExp(`${facts.menh_nap_am}[^.]*(nghĩa là|tượng trưng|chủ về)`).test(ch.text), ch.text);
    }
  }
});
