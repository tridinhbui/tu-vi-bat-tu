// Prose library (prose plan P2): every concept a Mệnh rule can assert has a card; cards, frames, modifiers, schemas and connectives
// pass the structural lint (no meta-language, no absolutes, known slots, enough variants, no repeats).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { lintLibrary } from '../prose/lint.ts';
import type { Knowledge } from '../types.ts';

const K: Knowledge = JSON.parse(readFileSync(new URL('../generated/knowledge.json', import.meta.url), 'utf8'));
export const SLOTS = {
  fragment: [], behave: ['S'], frame: ['stars', 'star', 'branch', 'opp_stars', 'dignity', 'palace', 'own'],
  modifier: ['star', 'stars', 'branch', 'hoa', 'tt', 'dignity', 'S', 'palace', 'concept.np', 'concept.pron', 'concept.say', 'target.np', 'target.pron', 'value', 'value2', 'mature'],
};
const required = [...new Set(Object.values(K.kg!.ruleConcepts!).flatMap(e => e.asserts.map(a => a.concept)))].sort();

test('prose library: every concept that Mệnh rules assert has a card, and the whole library passes lint', () => {
  const issues = lintLibrary(K.prose!, K.concepts.concepts, required, SLOTS);
  const errors = issues.filter(i => i.level === 'error').map(i => `${i.where}: ${i.msg}`);
  assert.deepEqual(errors, []);
  assert.ok(issues.filter(i => i.level === 'warning').length <= 10, issues.map(i => i.msg).join('\n'));
});

test('prose library: sizes the Mệnh plan asks for (§3 table)', () => {
  const P = K.prose!;
  assert.ok(P.concepts.length >= required.length, `${P.concepts.length} cards for ${required.length} concepts`);
  assert.ok(P.schemas.length >= 12);
  assert.ok(P.connectives.length >= 120);
  assert.ok(P.modifiers.length >= 15);
  for (const rel of ['contrast', 'concession', 'rescue', 'addition', 'consequence', 'synthesis', 'elaboration', 'timing'])
    assert.ok(P.connectives.filter(c => c.rel === rel && c.pos === 'initial').length >= 8, rel);
  assert.ok(P.schemas.some(s => s.needs.length === 0), 'a fallback schema that always applies');
});

test('prose library: every card is a draft until reviewed; nothing claims to be approved yet', () => {
  const st = new Set([...K.prose!.concepts.map(c => c.status), ...K.prose!.modifiers.map(m => m.status)]);
  assert.deepEqual([...st], ['draft']);
});
