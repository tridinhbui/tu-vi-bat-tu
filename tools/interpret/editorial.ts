// Editorial workflow for interpretation content modules (src/interpret/content/*.json).
//   node tools/interpret/editorial.ts lint                          schema + safety checks, render coverage (every chapter, regression charts)
//   node tools/interpret/editorial.ts preview [chart-index] [chapter]   render a chapter (default cong_danh) with sentence provenance
//   node tools/interpret/editorial.ts submit  <module> --by <name> [--notes ...]            draft -> in_review
//   node tools/interpret/editorial.ts approve <module> --by <name> [--notes ...]            in_review -> approved (reviewer != author)
//   node tools/interpret/editorial.ts request-changes <module> --by <name> --notes ...      in_review -> draft
//   node tools/interpret/editorial.ts retire  <module> --by <name> --notes ...              any -> retired
// Every transition appends a review record to the module and bumps nothing else; editing a passage of an approved module must bump
// `version` and send it back to draft (lint enforces this through a content hash). Run `npm run build:knowledge` afterwards.
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { interpret, CHAPTERS, type Chapter } from '../../src/interpret/pipeline.ts';
import type { ContentModule, Knowledge } from '../../src/interpret/types.ts';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const CONTENT = join(ROOT, 'src', 'interpret', 'content');
const BASES = new Set(['sach', 'dieu_kien', 'he_thong', 'tinh_toan']);
const ROLES = new Set(['central', 'factor', 'counter', 'cross', 'dominance', 'timing', 'limits', 'synthesis', 'notice', 'frame']);
const BANNED = [/chắc chắn/i, /định mệnh/i, /nhất định sẽ/i, /tai họa/i, /sẽ bị/i, /tuyệt đối/i, /không thể tránh/i, /\bchết\b/i, /\bly hôn\b/i, /\bphá sản\b/i, /\bung thư\b/i];
// slots that carry fired book readings or sourced reference sentences (a 'sach' passage must use one, or declare its own cites)
const SACH_SLOT = /\{\??(list:|x\.quote|profiles|dh\.(quan|focus)_readings|d\.|s\.|t\.|y\.|r\.quote|rest|f\.(role|group|hoa_notes|dignity)|group\.|menh\.|stage|tuhoa|timing\.list|lim\.scope)/;
const files = readdirSync(CONTENT).filter(f => f.endsWith('.json')).sort();
const load = () => files.map(f => ({ f, d: JSON.parse(readFileSync(join(CONTENT, f), 'utf8')) as { modules: Array<ContentModule & { reviews?: any[]; contentHash?: string }> } }));
const hashOf = (m: ContentModule) => createHash('sha256').update(JSON.stringify(m.passages)).digest('hex').slice(0, 12);
const knowledge = (): Knowledge => JSON.parse(readFileSync(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'), 'utf8'));
const charts = () => JSON.parse(readFileSync(join(ROOT, 'src', 'interpret', 'test', 'fixtures', 'charts.json'), 'utf8'));

function lint(): number {
  const problems: string[] = [], seen = new Set<string>();
  for (const { f, d } of load()) for (const m of d.modules) {
    const where = `${f}:${m.id}`;
    if (seen.has(m.id)) problems.push(`${where}: duplicate module id`); seen.add(m.id);
    if (!ROLES.has(m.role)) problems.push(`${where}: unknown role ${m.role}`);
    if (!['draft', 'in_review', 'approved', 'retired'].includes(m.status)) problems.push(`${where}: unknown status ${m.status}`);
    if (m.status === 'approved' && m.contentHash && m.contentHash !== hashOf(m)) problems.push(`${where}: passages changed after approval — bump version and send back to draft`);
    for (const p of m.passages) {
      if (!BASES.has(p.basis)) problems.push(`${where}/${p.id}: unknown basis ${p.basis}`);
      if (!p.variants?.length) problems.push(`${where}/${p.id}: no variants`);
      for (const v of [...p.variants, ...(p.followups ?? [])]) {
        if (BANNED.some(b => b.test(v))) problems.push(`${where}/${p.id}: banned wording in template: ${v.slice(0, 60)}`);
        if (p.basis === 'sach' && !SACH_SLOT.test(v) && !(p.cites ?? []).length)
          problems.push(`${where}/${p.id}: a 'sach' passage must quote fired rules through a slot or declare cites`);
        const stray = v.replace(/\{[^{}]*\}/g, '').match(/[“”]/g);
        if (stray && stray.length % 2) problems.push(`${where}/${p.id}: unbalanced quotes in template`);
      }
    }
  }
  // render coverage: passages that never render on any regression chart are flagged (dead text or a gate that cannot hold)
  const k = knowledge(), rendered = new Set<string>();
  for (const c of charts()) for (const ch of CHAPTERS) for (const p of interpret(c.facts, ch, k).paragraphs) for (const s of p.sentences) rendered.add(`${s.module}/${s.passage}`);
  const never = load().flatMap(({ d }) => d.modules.flatMap(m => m.passages.map(p => `${m.id}/${p.id}`))).filter(x => !rendered.has(x));
  for (const p of problems) console.log('ERROR', p);
  console.log(`modules: ${seen.size}; passages never rendered on the ${charts().length} regression charts: ${never.length ? never.join(', ') : 'none'}`);
  return problems.length ? 1 : 0;
}

function preview(idx: number, chapter: Chapter) {
  const c = charts()[idx], o = interpret(c.facts, chapter, knowledge());
  console.log(`# ${o.title} · ${c.label} — ${c.birth.year}-${c.birth.month}-${c.birth.day} ${c.birth.hour}:${c.birth.minute} ${c.birth.gender}\n`);
  for (const p of o.paragraphs) {
    console.log(`## ${p.title}  [${p.module}]`);
    for (const s of p.sentences) console.log(`  (${s.basis}${s.rules.length ? ' · ' + s.rules.join(', ') : ''}) ${s.text}`);
    console.log('');
  }
  console.log('quality:', JSON.stringify({ pass: o.quality.pass, errors: o.quality.errors, warnings: o.quality.warnings.map(w => w.check), ...o.quality.metrics }));
  console.log('editorial:', o.quality.editorial.notice);
}

function transition(action: string, id: string, by: string, notes: string) {
  const all = load();
  const hit = all.find(({ d }) => d.modules.some(m => m.id === id));
  if (!hit) throw new Error(`no module ${id}`);
  const m = hit.d.modules.find(x => x.id === id)!;
  const allowed: Record<string, [string[], string]> = { submit: [['draft'], 'in_review'], approve: [['in_review'], 'approved'], 'request-changes': [['in_review'], 'draft'], retire: [['draft', 'in_review', 'approved'], 'retired'] };
  const [from, to] = allowed[action] ?? [[], ''];
  if (!from.includes(m.status)) throw new Error(`${id} is ${m.status}; '${action}' needs ${from.join(' or ')}`);
  if (action === 'approve' && (m.author ?? '').includes(by)) throw new Error('the author cannot approve their own module');
  if ((action === 'request-changes' || action === 'retire') && !notes) throw new Error('notes are required');
  m.status = to as ContentModule['status'];
  (m.reviews ??= []).push({ version: m.version, by, decision: action === 'request-changes' ? 'request_changes' : action, notes: notes || null, at: new Date().toISOString().slice(0, 10) });
  if (to === 'approved') m.contentHash = hashOf(m);
  writeFileSync(join(CONTENT, hit.f), JSON.stringify(hit.d, null, 1) + '\n');
  console.log(`${id}: ${from.join('/')} -> ${to} by ${by}. Run npm run build:knowledge.`);
}

const [cmd, a1, ...rest] = process.argv.slice(2);
const flag = (n: string) => { const i = rest.indexOf(n); return i >= 0 ? rest[i + 1] ?? '' : ''; };
if (cmd === 'lint') process.exit(lint());
else if (cmd === 'preview') preview(Number(a1 ?? 0), (rest[0] ?? 'cong_danh') as Chapter);
else if (['submit', 'approve', 'request-changes', 'retire'].includes(cmd)) transition(cmd, a1, flag('--by') || (() => { throw new Error('--by is required'); })(), flag('--notes'));
else { console.log(readFileSync(fileURLToPath(import.meta.url), 'utf8').split('\n').slice(0, 10).join('\n')); process.exit(2); }
