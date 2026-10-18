// Time chapter (Đại hạn và tiểu hạn): the decades and the year being read, built only from data the Python engine computed and the
// time readings it attaches to them:
//   decades  palace, stem, age range, the Tứ Hóa that the decade's stem flies to natal stars (computed), and the vận readings of
//            Khảo Luận pp.233-236 / Thực Hành pp.115-117 (van_han.read, production rules)
//   stages   the life stage Khảo Luận pp.233-236 gives to the decade's palace (direction-dependent)
//   year     tiểu hạn palace (Thực Hành p.27) with its vận readings, and the lưu Tứ Hóa with the per-stem advice of Khảo Luận pp.195-197
// Natal readings about early / late success are NOT re-told here (they live in the palace chapters); nothing here predicts an event.
import { Renderer, type Paragraph, type Item } from './generator.ts';
import { joinVi } from './semantic.ts';
import type { ArgumentGraph } from './planner.ts';
import type { ChartInput, ContentModule, Decade, Knowledge } from './types.ts';

const src = (s: string) => s.replace(/pp?\.\s?/, 'tr.').replace(/-/g, '–');
const CONFLICT = 'Hai điều kiện trái chiều';
const S = (text: string, rules: string[] = []) => ({ text, rules });

export function timeline(chart: ChartInput, P: { seed: string; g: { palace(n: string): { major_stars: string[]; major_dignity: Record<string, string | null>; stars: string[] } } },
  k: Knowledge, modules: ContentModule[]): { paragraphs: Paragraph[]; graphs: ArgumentGraph[] } {
  const r = new Renderer(k, `${P.seed}|van_han`);
  const ref = k.reference;
  const stages = ref ? (chart.dai_han_direction === 'thuận' ? ref.lifeStages.thuan : ref.lifeStages.nghich) : {};
  const age = chart.year.age_tuoi_mu, now = chart.year.dai_han;
  const idxNow = chart.decades.findIndex(d => now && d.palace === now.palace && d.age_from === now.age_from);
  const majors = (name: string) => {
    const p = P.g.palace(name);
    return p.major_stars.length ? joinVi(p.major_stars.map(s => p.major_dignity[s] ? `${s} (${p.major_dignity[s]})` : s)) : 'vô chính diệu';
  };
  const decadeItem = (d: Decade): Item => {
    const readings = d.readings.filter(x => !x.text.startsWith(CONFLICT));
    const hoa = Object.entries(d.hoa).filter(([, v]) => v.palace).map(([h, v]) => `${h} vào ${v.star} (cung ${v.palace})`);
    const ky = d.hoa['Hóa Kỵ'];
    return {
      'd.range': S(`${d.age_from}–${d.age_to}`), 'd.palace': S(d.palace), 'd.stem': S(d.stem), 'd.branch': S(d.branch), 'd.majors': S(majors(d.palace)),
      'd.majors_phrase': S(P.g.palace(d.palace).major_stars.length ? `nơi có ${majors(d.palace)}` : 'một cung vô chính diệu'),
      'd.stage': S(stages[d.palace] ?? ''), 'd.domain': S(ref?.lifeStages.domain[d.palace] ?? ''),
      'd.readings': S(readings.map(x => `“${x.text.replace(/\.$/, '').replace(/\btheo sách (đây |là )?/g, '')}” (${src(x.src)})`).join('; '), readings.length ? [`VH:${d.palace}`] : []),
      'd.readings_n': S(readings.length ? String(readings.length) : ''),
      'd.conflict': S(d.readings.some(x => x.text.startsWith(CONFLICT)) ? '1' : ''),
      'd.hoa': S(joinVi(hoa)), 'd.ky_palace': S(ky?.palace ?? ''), 'd.ky_star': S(ky?.star ?? ''),
      'd.is_now': S(now && d.palace === now.palace && d.age_from === now.age_from ? '1' : ''),
      'd.title': S(`Đại hạn ${d.age_from}–${d.age_to}: cung ${d.palace}`),
    };
  };
  // the decade being lived, the next one, and the other decades that carry vận readings (others are listed only as facts)
  // decades that start beyond 85 tuổi mụ (or beyond the current age, for someone already older) are computed but not narrated, as in
  // the palace chapters: a reading for a 113-year-old says nothing useful
  const limit = Math.max(85, age);
  const cur = idxNow >= 0 ? chart.decades[idxNow] : null;
  const next0 = idxNow >= 0 ? chart.decades[idxNow + 1] ?? null : chart.decades.find(d => d.age_from > age) ?? null;
  const next = next0 && next0.age_from <= limit ? next0 : null;
  const others = chart.decades.filter(d => d !== cur && d !== next && d.age_to >= age - 10 && d.age_from <= limit && d.readings.some(x => !x.text.startsWith(CONFLICT))).slice(0, 4);
  r.setItems('decade_now', cur ? [{ ...decadeItem(cur), 't.title': S(`Chặng đang đi qua: ${cur.age_from}–${cur.age_to} tuổi, cung ${cur.palace}`) }] : []);
  r.setItems('decade_next', next ? [{ ...decadeItem(next), 't.title': S(`Chặng kế tiếp: ${next.age_from}–${next.age_to} tuổi, cung ${next.palace}`) }] : []);
  r.setItems('decade_other', others.map(d => decadeItem(d)));
  r.set('dir', chart.dai_han_direction); r.set('cuc', chart.cuc.name); r.set('start', String(chart.decades[0]?.age_from ?? ''));
  r.set('age', String(age)); r.set('year', String(chart.year.year)); r.set('year_gz', chart.year.annual_pillar ?? '');
  r.set('now.palace', now?.palace ?? ''); r.set('stage.cite', ref ? src(ref.lifeStages.cite.replace(/^KL /, 'Khảo Luận ')) : '');
  r.set('decades.path', chart.decades.filter(d => d.age_from <= Math.min(age + 25, limit) && d.age_to >= age - 25).map(d => `${d.age_from}–${d.age_to} ở ${d.palace}`).join(', '));
  // the year
  const y = chart.year, th = y.tieu_han_palace ?? '';
  const thReadings = (y.tieu_han_reading ?? []).filter(x => !x.text.startsWith(CONFLICT));
  r.set('y.th_palace', th); r.set('y.th_domain', th ? ref?.lifeStages.domain[th] ?? '' : ''); r.set('y.th_majors', th ? majors(th) : '');
  r.set('y.th_readings', thReadings.map(x => `“${x.text.replace(/\.$/, '').replace(/\btheo sách (đây |là )?/g, '')}” (${src(x.src)})`).join('; '), thReadings.length ? [`VH:${th}`] : []);
  r.set('y.th_conflict', (y.tieu_han_reading ?? []).some(x => x.text.startsWith(CONFLICT)) ? '1' : '');
  r.set('y.th_same_as_dh', th && now && th === now.palace ? '1' : '');
  r.set('y.thai_tue', y.luu_thai_tue_palace ?? '');
  const luu = (y.luu_tu_hoa_reading ?? []).filter(x => x.palace);
  r.set('y.luu', luu.map(x => `${x.hoa} vào ${x.star} ở cung ${x.palace} (sách khuyên: “${x.advice}”)`).join('; '), luu.length ? ['LUU_TU_HOA'] : []);
  r.set('y.luu_cite', luu.length ? src(luu[0].src) : '');
  const kyLuu = luu.find(x => x.hoa === 'Hóa Kỵ');
  r.set('y.luu_ky', kyLuu ? `cung ${kyLuu.palace}` : '');
  r.set('y.ky_note', kyLuu && ref ? ref.tuHoa.positionNotes['Hóa Kỵ'] ?? '' : '');
  r.set('tuhoa.cite', ref ? src(ref.tuHoa.cite.replace(/^KL /, 'Khảo Luận ')) : '');
  r.set('weight_note', ref?.tuHoa.weightNote ?? '');
  const paragraphs = r.render(modules).map(p => ({ ...p, title: p.title }));
  return { paragraphs, graphs: [] };
}
