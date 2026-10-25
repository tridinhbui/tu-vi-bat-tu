// The course of one life domain across the đại hạn (review of the live report 2026-10-23, points 2–4 and 10: "bước ngoặt sự nghiệp",
// "diễn biến hôn nhân", "quá trình tạo dựng tài sản"). For the chapters of Quan Lộc, Tài Bạch, Phu Thê and Điền Trạch, after the
// conclusion. It names, in age order, the hạn that touch the domain's palace — the hạn palace is that palace, or the hạn stem's Hóa Lộc /
// Hóa Kỵ lands there (Tứ Hóa by the hạn stem: a convention, he_thong; what a Hóa does in a palace: KL pp.195-197) — each with its level on
// the system indices (the period chart's levels), then the best and the hardest of them. Phu Thê tells phases only, never an event (owner
// decision 2026-10-23: no marriage, divorce or remarriage year). No book reading is added here; the đại hạn chapter tells each hạn in full.
import type { ChartInput, Knowledge } from '../types.ts';
import type { ProseSentence } from './realize.ts';
import type { Writer } from './narrative.ts';
import { computeIndices, type IndexNorms, type DecadeIndex } from '../indices.ts';
import norms from '../../../engine/data/kg/index_norms.json' with { type: 'json' };
import { shownDecades } from './vanhan.ts';

export interface CourseLib { lead: Record<string, string[]>; open: string[]; item: Record<'in' | 'loc' | 'ky', string>; best: string[]; hard: string[]; none: string[] }
const fill = (t: string, v: Record<string, string>) => t.replace(/\{([A-Za-z_]+)\}/g, (m, k) => v[k] ?? m);
const NORMS = norms as IndexNorms;
/** the palaces whose hạn tell each chapter's course: the chapter's palace (the money course also reads Điền Trạch, the property course Tài Bạch) */
export const COURSE_PALACES: Record<string, string[]> = { 'Quan Lộc': ['Quan Lộc'], 'Tài Bạch': ['Tài Bạch'], 'Phu Thê': ['Phu Thê'], 'Điền Trạch': ['Điền Trạch'] };

export function courseSentences(W: Writer, chart: ChartInput, k: Knowledge, P: string, label: string): ProseSentence[] {
  const C = k.prose?.luan?.course as CourseLib | undefined, pals = COURSE_PALACES[P];
  if (!C || !pals) return [];
  const levels = new Map<number, DecadeIndex>(computeIndices(chart, k, NORMS).decades.map(d => [d.age_from, d]));
  const hits = shownDecades(chart).map(d => {
    const how: Array<'in' | 'loc' | 'ky'> = [];
    if (pals.includes(d.palace)) how.push('in');
    if (d.hoa['Hóa Lộc']?.palace && pals.includes(d.hoa['Hóa Lộc'].palace)) how.push('loc');
    if (d.hoa['Hóa Kỵ']?.palace && pals.includes(d.hoa['Hóa Kỵ'].palace)) how.push('ky');
    return { d, how, lv: levels.get(d.age_from) };
  }).filter(x => x.how.length && x.lv);
  const tr = (step: string, basis: 'tinh_toan' | 'he_thong') => ({ move: 'TIMING' as const, step, basis, concepts: [], cites: ['KL pp.195-197'], part: 5 as const,
    note: 'Đại hạn nào chạm vào cung này: cung hạn chính là cung ấy, hoặc Hóa Lộc / Hóa Kỵ theo can hạn rơi vào đó (thông lệ); mức của hạn theo chỉ số tổng hợp của hệ thống, cùng thang với biểu đồ giai đoạn.' });
  if (!hits.length) return [W.sentence(fill(W.pick(`crs|none|${P}`, C.none), { label }), tr('course:none', 'tinh_toan'))];
  const item = (x: typeof hits[number]) => `${x.d.age_from}–${x.d.age_to} tuổi (${x.how.map(h => fill(C.item[h], { pal: h === 'loc' ? x.d.hoa['Hóa Lộc'].palace! : h === 'ky' ? x.d.hoa['Hóa Kỵ'].palace! : x.d.palace, star: h === 'loc' ? x.d.hoa['Hóa Lộc'].star : h === 'ky' ? x.d.hoa['Hóa Kỵ'].star : '' })).join(', ')}; ${x.lv!.insufficient ? 'chưa đủ căn cứ để xếp mức' : `mức ${x.lv!.level_vi.toLowerCase()}`})`;
  const out = [W.sentence(fill(W.pick(`crs|open|${P}`, C.open), { label, list: hits.map(item).join('; ') }), tr('course:list', 'tinh_toan'))];
  // best and hardest among the decades with book evidence only (a decade "chưa đủ căn cứ" has no level to compare)
  const placed = hits.filter(x => !x.lv!.insufficient);
  if (placed.length >= 2) {
    const best = [...placed].sort((a, b) => b.lv!.score - a.lv!.score)[0], hard = [...placed].sort((a, b) => a.lv!.score - b.lv!.score)[0];
    if (best.lv!.level !== hard.lv!.level) {
      out.push(W.sentence(`${fill(W.pick(`crs|best|${P}`, C.best), { label, a: String(best.d.age_from), b: String(best.d.age_to) })}; ${fill(W.pick(`crs|hard|${P}`, C.hard), { label, a: String(hard.d.age_from), b: String(hard.d.age_to) })}`, tr('course:weigh', 'he_thong')));
    }
  }
  return out;
}
