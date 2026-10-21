// The reader-facing Tử Vi reading in themes (prose-style plan S1–S2), before the twelve palace chapters: the overview block, then the
// themed sections argued from the reasoner's plans. One rule run and one Mệnh plan feed every section, so nothing is inferred twice and a
// reading told in one section is not told again in the next.
import type { ChartInput, Knowledge } from '../types.ts';
import { run } from '../engine.ts';
import { reasonMenh } from '../reason/plan.ts';
import { proseOverview, type ProseOverview } from './overview.ts';
import { seedOf } from './chapter.ts';

export type ThemeChapter = ProseOverview;

/** `luan`: the palace chapters are the luận cung ones, whose Mệnh chapter opens with the Mệnh stars and tells Thân cư: the overview then
 *  leaves those to it and keeps the chart-wide facts (bản mệnh, cục, chủ mệnh / chủ thân, độ số). */
export function proseThemes(chart: ChartInput, k: Knowledge, engine: string, opts: { allowDraft?: boolean; luan?: boolean } = {}): ThemeChapter[] {
  const allowDraft = !!opts.allowDraft;
  const findings = run(k.rules, k.sources, chart.base).findings;
  const plan = reasonMenh(chart, k, undefined, { draftFormations: allowDraft });
  const overview = proseOverview(chart, k, findings, plan, seedOf(chart), engine, allowDraft, { palaces: !opts.luan });
  return [overview];
}
