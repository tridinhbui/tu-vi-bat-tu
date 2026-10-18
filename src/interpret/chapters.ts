// Chapter specifications. One planner, one generator and one set of generic content modules serve every chapter; a chapter only says
// which palace it reads, which semantic facets belong to it, where its "environment" is read, and which readings are about timing.
// Rules and templates are never duplicated per chapter.

export type ChapterId = 'cong_danh' | 'tai_bach' | 'menh';

export interface ChapterSpec {
  id: ChapterId;
  title: string;
  focus: string;                 // the palace the chapter is about
  topic: string;                 // how the prose names the subject ("công danh")
  /** facets in scope for readings OUTSIDE the focus palace (Mệnh, Thân, link palaces). Prefix match on the facet id. */
  facets: string[];
  /** facets accepted from the environment palace */
  env: { palace: string; label: string; facets: string[] } | null;
  /** palaces whose in-scope readings are linked into the chapter (besides the focus frame) */
  links: Array<'Mệnh' | 'Thân' | string>;
  timing: { facets: string[]; early: string[]; late: string[] };
  /** facets narrated as "how the person goes about it" (only where the chapter has such a lens) */
  workStyle: string[];
  /** rules the books give for the same chính tinh in Mệnh are listed as not transferable (not meaningful for the Mệnh chapter) */
  scopeNotes: boolean;
  /** facets kept from the focus palace itself (undefined = everything the palace says belongs to the chapter); the rest is left to the
   *  chapter that owns it and only counted, so a reader of several chapters does not meet the same sentence three times */
  focusFacets?: string[];
  /** in-scope readings of the other tam phương palaces are linked in (meaningful for career and wealth, not for the person) */
  frameLinks: boolean;
}

export const SPECS: Record<ChapterId, ChapterSpec> = {
  cong_danh: {
    id: 'cong_danh', title: 'Công danh', focus: 'Quan Lộc', topic: 'công danh',
    facets: ['career.authority', 'career.trajectory', 'career.expertise', 'career.path', 'career.timing', 'life.mobility'],
    env: { palace: 'Thiên Di', label: 'hoàn cảnh khi ra ngoài xã hội', facets: ['career.support', 'career.trajectory', 'life.mobility', 'life.course', 'career.timing'] },
    links: ['Mệnh', 'Thân'],
    timing: { facets: ['career.timing'], early: ['career.early'], late: ['career.late'] },
    workStyle: ['identity.ambition', 'identity.discipline'],
    scopeNotes: true, frameLinks: true,
  },
  tai_bach: {
    id: 'tai_bach', title: 'Tài bạch', focus: 'Tài Bạch', topic: 'tiền bạc',
    facets: ['finance.flow', 'finance.retention', 'finance.style', 'finance.source', 'finance.property'],
    env: { palace: 'Điền Trạch', label: 'của cải tích lũy và nhà đất', facets: ['finance.property', 'finance.retention', 'finance.flow'] },
    links: ['Mệnh', 'Thân'],
    timing: { facets: ['life.timing'], early: [], late: ['life.late_bloom'] },
    workStyle: [],
    scopeNotes: true, frameLinks: true,
  },
  menh: {
    id: 'menh', title: 'Mệnh', focus: 'Mệnh', topic: 'con người',
    facets: ['identity.', 'life.course', 'life.timing', 'inner.', 'life.spirituality'],
    env: { palace: 'Phúc Đức', label: 'phúc phần và nền tảng tinh thần', facets: ['life.course', 'inner.', 'life.timing', 'wellbeing.longevity'] },
    links: ['Thân'],
    timing: { facets: ['life.timing'], early: [], late: ['life.late_bloom'] },
    workStyle: [],
    scopeNotes: false, frameLinks: false,
    focusFacets: ['identity.', 'life.', 'inner.', 'wellbeing.', 'relationships.romance'],
  },
};

export const inFacets = (facet: string, list: string[]) => list.some(f => f.endsWith('.') ? facet.startsWith(f) : facet === f);
