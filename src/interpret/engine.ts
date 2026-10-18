// Forward-chaining rule engine (port of engine/tvbt/reasoning/engine.py, without the experimental formations).
// Deterministic: rules ordered by (-priority, id), subjects by name; derived facts feed later rules until a fixpoint; a rule fires at most
// once per (rule, subject); an exception that holds suppresses the rule; a contradictory re-assertion is recorded, never overwritten.
import { evaluate, type World } from './dsl.ts';
import type { Facts, Finding, Rule, Source } from './types.ts';

const MAX_DEPTH = 6;

export interface EngineResult {
  findings: Finding[]; fired: Array<{ ruleId: string; subject: string; depth: number }>;
  blocked: Array<{ ruleId: string; subject: string }>; conflicts: Array<{ fact: string; subject: string; values: unknown[]; ruleId: string }>;
}

export function run(rules: Rule[], sources: Source[], base: Record<string, Facts>, system = 'tu_vi'): EngineResult {
  const src = new Map(sources.map(s => [s.id, s]));
  const derived: Record<string, Facts> = Object.fromEntries(Object.keys(base).map(s => [s, {}]));
  const ordered = rules.filter(r => r.system === system).sort((a, b) => (b.priority - a.priority) || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
  const palaces = Object.keys(base).filter(s => s !== 'chart').sort((a, b) => a < b ? -1 : a > b ? 1 : 0);
  const done = new Set<string>(), depthOf = new Map<string, number>();
  const out: EngineResult = { findings: [], fired: [], blocked: [], conflicts: [] };

  const factsOf = (subject: string): Facts => ({ ...(base.chart ?? {}), ...base[subject], ...derived[subject], ...(subject !== 'chart' ? derived.chart : {}) });
  const world: World = name => base[`palace:${name}`] ? factsOf(`palace:${name}`) : null;

  for (let depth = 1; depth <= MAX_DEPTH; depth++) {
    let progressed = false;
    for (const r of ordered) {
      for (const subj of r.subject === 'palace' ? palaces : ['chart']) {
        const key = `${r.id}\u0000${subj}`;
        if (done.has(key)) continue;
        const facts = factsOf(subj);
        const cond = evaluate(r.conditions, facts, world);
        if (cond === null) continue;                     // re-checked next round
        done.add(key);
        if (cond === false) continue;
        if (r.exceptions.some(e => evaluate(e, facts, world) === true)) { out.blocked.push({ ruleId: r.id, subject: subj }); continue; }
        const rdepth = 1 + Math.max(0, ...derivedLeaves(r, subj).map(k => depthOf.get(k) ?? 0));
        out.fired.push({ ruleId: r.id, subject: subj, depth: rdepth });
        progressed = true;
        const basis = r.reviewStatus === 'verified' && r.sourceIds.every(s => src.get(s)?.verified) ? 'verified' : 'draft';
        for (const c of r.consequences) {
          if (c.kind === 'assert' && c.fact) {
            const tgt = c.scope === 'chart' ? 'chart' : subj, val = c.value ?? true;
            if (c.fact in derived[tgt] && derived[tgt][c.fact] !== val) { out.conflicts.push({ fact: c.fact, subject: tgt, values: [derived[tgt][c.fact], val], ruleId: r.id }); continue; }
            derived[tgt][c.fact] = val;
            depthOf.set(`${tgt}\u0000${c.fact}`, rdepth);
          } else if (c.kind === 'finding' && c.claim) {
            out.findings.push({ id: `finding:${r.id}:${c.claim}@${subj}`, ruleId: r.id, subject: subj, palace: subj.startsWith('palace:') ? subj.slice(7) : null,
              claim: c.claim, effect: c.effect ?? 'support', basis, depth: rdepth });
          }
        }
      }
    }
    if (!progressed) break;
  }
  return out;

  function derivedLeaves(r: Rule, subj: string): string[] {
    const keys: string[] = [];
    const walk = (e: any) => {
      if (!e || typeof e !== 'object') return;
      if (typeof e.fact === 'string' && e.fact.startsWith('derived.')) keys.push(`${subj}\u0000${e.fact}`, `chart\u0000${e.fact}`);
      for (const k of ['all', 'any', 'count']) if (Array.isArray(e[k])) e[k].forEach(walk);
      if (e.not) walk(e.not);
    };
    walk(r.conditions);
    return keys;
  }
}
