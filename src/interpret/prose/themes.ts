// The reader-facing Tử Vi reading in themes (prose-style plan S1–S2), before the twelve palace chapters: the overview block, then the
// themed sections argued from the reasoner's plans. One rule run and one Mệnh plan feed every section, so nothing is inferred twice and a
// reading told in one section is not told again in the next.
import type { ChartInput, Knowledge } from '../types.ts';
import { run } from '../engine.ts';
import { reasonMenh } from '../reason/plan.ts';
import { proseOverview, type ProseOverview } from './overview.ts';
import { seedOf } from './chapter.ts';

export type ThemeChapter = ProseOverview;

export function proseThemes(chart: ChartInput, k: Knowledge, engine: string, opts: { allowDraft?: boolean } = {}): ThemeChapter[] {
  const allowDraft = !!opts.allowDraft;
  const findings = run(k.rules, k.sources, chart.base).findings;
  const plan = reasonMenh(chart, k, undefined, { draftFormations: allowDraft });
  const overview = proseOverview(chart, k, findings, plan, seedOf(chart), engine, allowDraft);
  return [overview];
}
