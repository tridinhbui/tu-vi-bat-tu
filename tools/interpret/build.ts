// Builds the interpretation knowledge base from the repository's source corpus.
//   node tools/interpret/build.ts            -> src/interpret/generated/knowledge.json + migrations/interpret/0002_seed.sql
// Inputs (never edited here): engine/data rule packs (the list in engine/tvbt/knowledge/loader.py), sources.json, claims_vi.json,
// star_profiles.json, data/semantic/*.json, and the editorial content modules in src/interpret/content/*.json.
// The same knowledge feeds the bundled store (Worker without D1) and the D1 seed, so both stores answer identically.
import { readFileSync, writeFileSync, mkdirSync, readdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const DATA = join(ROOT, 'engine', 'data');
const read = (p: string) => JSON.parse(readFileSync(p, 'utf8'));

const loader = readFileSync(join(ROOT, 'engine', 'tvbt', 'knowledge', 'loader.py'), 'utf8');
const packs: string[] = JSON.parse(loader.match(/^PACKS = (\[.*\])$/m)![1].replace(/'/g, '"'));
const CITE = /\[((?:TH|KL|TT)[^\]]*?)\]/g;
const PARA = /paraphrased\)?[^:]{0,80}?:\s*(.+)$/;
// 八字真宗 (Bát Tự Chân Tông) rules give their place as "[PDF p.25 …]" or "[八字真宗 PDF pp.31-32 …]": PDF page numbers of the circulated scan
const ZZ_CITE = /\[(?:八字真宗 )?PDF (pp?\.\s?[\d]+(?:[-–][\d]+)?)/g;

type Raw = { id: string; system: string; schoolId: string; category: string; description: string; conditions: unknown; consequences: any[];
  exceptions?: unknown[]; priority?: number; sourceIds?: string[]; reviewStatus: string; subject?: string };

const sources = new Map<string, any>();
for (const s of read(join(DATA, 'sources.json')).sources) sources.set(s.id, s);
const rules: any[] = [];
for (const name of packs) {
  const d = read(join(DATA, name));
  for (const s of d.sources ?? []) if (!sources.has(s.id)) sources.set(s.id, s);
  for (const r of d.rules as Raw[]) {
    const cites = [...r.description.matchAll(CITE)].map(m => m[1]);
    if (r.system === 'bat_tu' && (r.sourceIds ?? []).includes('SRC_BAZI_ZHENZONG')) cites.push(...[...r.description.matchAll(ZZ_CITE)].map(m => `ZZ ${m[1]}`));
    const para = r.description.match(PARA);
    rules.push({
      id: r.id, system: r.system, school: r.schoolId, category: r.category, subject: r.subject ?? 'chart', priority: r.priority ?? 0,
      conditions: r.conditions, consequences: r.consequences, exceptions: r.exceptions ?? [], sourceIds: r.sourceIds ?? [],
      reviewStatus: r.reviewStatus, cites, reading: para ? para[1].replace(CITE, '').trim() : null,
    });
  }
}
const claims: Record<string, string> = read(join(DATA, 'claims_vi.json'));
const sem = (n: string) => read(join(DATA, 'semantic', n));
const contentDir = join(ROOT, 'src', 'interpret', 'content');
const modules = readdirSync(contentDir).filter(f => f.endsWith('.json')).sort().flatMap(f => read(join(contentDir, f)).modules);
// Sourced reference material used by every chapter (never interpreted beyond what the source says):
//   palace roles  — Khảo Luận pp.214-220, transcribed in engine/tvbt/analysis.py (PALACE_ROLE)
//   star groups   — Khảo Luận pp.166-167 group notes (GROUP_NOTE in analysis.py)
//   life stages   — Khảo Luận pp.233-236 (STAGE_THUAN / STAGE_NGHICH / DOMAIN in van_han.py)
//   Tứ Hóa notes  — Khảo Luận pp.195-197 (engine/data/tu_hoa_vi.json)
//   dignity pages — Thực Hành per-star brightness headers (engine/data/dignity_vn.json locators)
const pyDict = (file: string, name: string): Record<string, string> => {
  const src = readFileSync(join(ROOT, 'engine', 'tvbt', file), 'utf8');
  const m = src.match(new RegExp(`^${name} = \\{([\\s\\S]*?)\\}\\s*(?:#.*)?$`, 'm'));
  if (!m) throw new Error(`${name} not found in ${file}`);
  return Object.fromEntries([...m[1].matchAll(/"([^"]+)":\s*"([^"]*)"/g)].map(x => [x[1], x[2]]));
};
const dignity = read(join(DATA, 'dignity_vn.json'));
const tuHoa = read(join(DATA, 'tu_hoa_vi.json'));
const reference = {
  palaceRoles: { cite: 'KL pp.214-220', roles: pyDict('analysis.py', 'PALACE_ROLE') },
  groupNotes: { cite: 'KL pp.166-167', notes: pyDict('analysis.py', 'GROUP_NOTE'), members: (() => {
    const src = readFileSync(join(ROOT, 'engine', 'tvbt', 'analysis.py'), 'utf8');
    const body = src.match(/^GROUPS = \{([\s\S]*?)\}\s*$/m)![1];
    return Object.fromEntries([...body.matchAll(/"([^"]+)":\s*\[([^\]]*)\]/g)].map(m => [m[1], [...m[2].matchAll(/"([^"]+)"/g)].map(x => x[1])]));
  })() },
  lifeStages: { cite: 'KL pp.233-236', thuan: pyDict('van_han.py', 'STAGE_THUAN'), nghich: pyDict('van_han.py', 'STAGE_NGHICH'), domain: pyDict('van_han.py', 'DOMAIN') },
  tuHoa: { cite: 'KL pp.195-197', meaning: tuHoa.meaning, positionNotes: tuHoa.position_notes, byPalace: tuHoa.position_notes_by_palace ?? {}, weightNote: tuHoa.weight_note,
    byStem: tuHoa.by_stem },
  dignity: { source: dignity.source, levels: dignity.levels, locators: Object.fromEntries(Object.entries(dignity.stars).map(([s, v]: [string, any]) => [s, v.locator])) },
};
const knowledge = {
  reference,
  sources: [...sources.values()].map(s => ({ id: s.id, title: s.title, author: s.author ?? null, locator: s.locator ?? null, verified: !!s.verified })),
  rules, claims,
  concepts: sem('concepts.json'), relations: sem('relations.json'), ontology: sem('ontology.json'),
  starProfiles: read(join(DATA, 'star_profiles.json')),
  modules,
  // knowledge graph (prose plan §2): page-checked qualifiers now; rule→concept links and rule relations join here in P1
  kg: { qualifiers: read(join(DATA, 'kg', 'qualifiers.json')).qualifiers },
};
const version = createHash('sha256').update(JSON.stringify(knowledge)).digest('hex').slice(0, 16);
const out = { version, builtFrom: packs, ...knowledge };
mkdirSync(join(ROOT, 'src', 'interpret', 'generated'), { recursive: true });
writeFileSync(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'), JSON.stringify(out));

// ---- D1 seed (same content, relational) ----
const q = (v: unknown) => v === null || v === undefined ? 'NULL' : typeof v === 'number' ? String(v) : `'${String(typeof v === 'string' ? v : JSON.stringify(v)).replace(/'/g, "''")}'`;
const lines: string[] = ['-- generated by tools/interpret/build.ts; do not edit', `INSERT OR REPLACE INTO kb_meta (key, value) VALUES ('version', ${q(version)});`, 'DELETE FROM module_reviews;'];
for (const s of out.sources) lines.push(`INSERT OR REPLACE INTO sources (id, title, author, locator, verified) VALUES (${q(s.id)}, ${q(s.title)}, ${q(s.author)}, ${q(s.locator)}, ${s.verified ? 1 : 0});`);
for (const r of rules) lines.push(`INSERT OR REPLACE INTO rules (id, system, school, category, subject, priority, conditions_json, consequences_json, exceptions_json, source_ids_json, review_status, cites_json, reading) VALUES (${[r.id, r.system, r.school, r.category, r.subject, r.priority, r.conditions, r.consequences, r.exceptions, r.sourceIds, r.reviewStatus, r.cites, r.reading].map(q).join(', ')});`);
for (const [k, v] of Object.entries(claims)) lines.push(`INSERT OR REPLACE INTO claims (id, label) VALUES (${q(k)}, ${q(v)});`);
for (const c of out.concepts.concepts) lines.push(`INSERT OR REPLACE INTO concepts (id, facet, pol, kind, opp, cues_json, np, short) VALUES (${[c.id, c.facet, c.pol, c.kind, c.opp ?? null, c.cues, c.np, c.short ?? null].map(q).join(', ')});`);
for (const r of out.relations.relations) lines.push(`INSERT OR REPLACE INTO concept_relations (a, b, type, frame, synth) VALUES (${[r.a, r.b, r.type, r.frame ?? null, r.synth ?? null].map(q).join(', ')});`);
for (const m of modules) {
  const layout = { order: m.order, each: m.each, merge: m.merge, exceptChapters: m.exceptChapters };
  lines.push(`INSERT OR REPLACE INTO content_modules (id, chapter, role, version, status, title, when_json, evidence_json, slots_json, author, layout_json) VALUES (${[m.id, m.chapter, m.role, m.version, m.status, m.title, m.when ?? null, m.evidence ?? null, m.slots ?? null, m.author ?? null, layout].map(q).join(', ')});`);
  for (const r of m.reviews ?? []) lines.push(`INSERT INTO module_reviews (module_id, version, reviewer, decision, notes, created_at) VALUES (${[m.id, r.version, r.by, r.decision, r.notes ?? null, r.at].map(q).join(', ')});`);
  (m.passages ?? []).forEach((p: any, i: number) => lines.push(`INSERT OR REPLACE INTO module_passages (module_id, passage_id, ord, when_json, basis, kind, variants_json, cites_json, layout_json) VALUES (${[m.id, p.id, i, p.when ?? null, p.basis, p.kind ?? 'claim', p.variants, p.cites ?? [], p.each || p.followups ? { each: p.each, followups: p.followups } : null].map(q).join(', ')});`));
}
for (const [star, prof] of Object.entries(out.starProfiles.stars)) lines.push(`INSERT OR REPLACE INTO kg_nodes (id, kind, label, data_json) VALUES (${q('star:' + star)}, 'star', ${q(star)}, ${q(prof)});`);
mkdirSync(join(ROOT, 'migrations', 'interpret'), { recursive: true });
writeFileSync(join(ROOT, 'migrations', 'interpret', '0002_seed.sql'), lines.join('\n') + '\n');
console.log(`knowledge ${version}: ${rules.length} rules, ${out.sources.length} sources, ${modules.length} modules, ${lines.length} seed statements`);
