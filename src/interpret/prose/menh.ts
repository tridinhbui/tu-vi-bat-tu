// The Mệnh chapter of reader prose (prose plan P3); the general machinery is chapter.ts.
import type { ChartInput, Knowledge } from '../types.ts';
import { proseChapter, type ProseChapter } from './chapter.ts';

export { PROSE_VERSION, PROSE_ORDER, PROSE_SPECS, proseChapter, proseReport, seedOf, type ProseChapter, type ProseChapterId } from './chapter.ts';
export const proseMenh = (chart: ChartInput, k: Knowledge, opts: { allowDraft?: boolean } = {}): ProseChapter => proseChapter(chart, k, 'menh', opts);
