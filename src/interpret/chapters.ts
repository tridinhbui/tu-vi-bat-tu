// Chapter specifications: which palace a chapter (or each section of a combined chapter) is read from, which concept facets count as
// the chapter's subject when a reading sits in ANOTHER palace, and which sensitivity notice applies. Pure data: adding a chapter here does
// not create content; its prose comes from the shared editorial modules plus the chapter's own module file in content/.
export type ChapterId =
  | 'menh' | 'cong_danh' | 'tai_bach' | 'dien_trach' | 'phu_the' | 'phuc_duc' | 'gia_dao' | 'di_no_tat' | 'van_han' | 'bat_tu';

export interface SectionSpec {
  /** palace whose readings are the core of the section (the name as on the chart; 'Thân' = the palace where Thân sits) */
  palace: string;
  /** facets that make a reading from Mệnh / Thân / the chart (or the tam phương) belong here */
  facets: string[];
  /** facets read from the environment palace (default: the palace opposite the focus) as the "environment" of the section */
  envFacets?: string[];
  /** environment palace when it is not the opposite one (Công danh reads the outside world from Thiên Di, opposite Mệnh) */
  envPalace?: string;
  /** further palaces whose readings count when their facet is the section's (Điền Trạch for money, Phúc Đức for marriage...) */
  linked?: string[];
  /** short Vietnamese name of the section's subject, used by templates ("công danh", "tiền bạc"...) */
  topic: string;
}

export interface ChapterSpec {
  id: ChapterId; title: string; sections: SectionSpec[];
  /** notice shown once in the chapter (health, marriage...): the reading is symbolic, not a prediction or a diagnosis */
  sensitive?: 'health' | 'relationships' | 'finance';
  /** chapter-level lead: a sentence-sized description of what the chapter covers (system wording) */
  scope: string;
}

const CAREER = ['career.authority', 'career.trajectory', 'career.expertise', 'career.path', 'career.support', 'career.timing'];
const FINANCE = ['finance.flow', 'finance.retention', 'finance.style', 'finance.source'];
const IDENTITY = ['identity.cognition', 'identity.communication', 'identity.temperament', 'identity.values', 'identity.adaptability', 'identity.discipline',
  'identity.ambition', 'identity.presence', 'identity.emotion', 'identity.lifestyle', 'life.spirituality', 'inner.contentment'];
const LIFE = ['life.course', 'life.timing', 'life.mobility'];
const LOVE = ['relationships.marriage', 'relationships.partner', 'relationships.timing', 'relationships.romance'];

export const SPECS: Record<ChapterId, ChapterSpec> = {
  menh: { id: 'menh', title: 'Mệnh, Thân và tính cách', scope: 'con người nền tảng: tính khí, cách nghĩ, giá trị và nhịp đời',
    sections: [{ palace: 'Mệnh', facets: [...IDENTITY, ...LIFE], linked: ['Phúc Đức'], topic: 'con người' }] },
  cong_danh: { id: 'cong_danh', title: 'Công danh', scope: 'đường công danh, năng lực chuyên môn và vị trí trong tập thể',
    sections: [{ palace: 'Quan Lộc', facets: CAREER, envFacets: ['career.support', 'career.trajectory', 'life.mobility', 'life.course', 'career.timing'], envPalace: 'Thiên Di', topic: 'công danh' }] },
  tai_bach: { id: 'tai_bach', title: 'Tài Bạch', scope: 'cách tiền bạc đến, ở lại và được sử dụng', sensitive: 'finance',
    sections: [{ palace: 'Tài Bạch', facets: FINANCE, envFacets: ['finance.flow', 'finance.source', 'finance.retention'], linked: ['Điền Trạch'], topic: 'tiền bạc' }] },
  dien_trach: { id: 'dien_trach', title: 'Điền Trạch', scope: 'nhà cửa, đất đai và cơ nghiệp vật chất', sensitive: 'finance',
    sections: [{ palace: 'Điền Trạch', facets: ['finance.property'], envFacets: ['finance.property'], topic: 'nhà cửa, cơ nghiệp' }] },
  phu_the: { id: 'phu_the', title: 'Phu Thê', scope: 'hôn nhân, người bạn đời và nhịp kết duyên', sensitive: 'relationships',
    sections: [{ palace: 'Phu Thê', facets: LOVE, envFacets: LOVE, linked: ['Phúc Đức'], topic: 'hôn nhân' }] },
  phuc_duc: { id: 'phuc_duc', title: 'Phúc Đức', scope: 'đời sống tinh thần, sự an ổn trong lòng và nền nếp họ hàng',
    sections: [{ palace: 'Phúc Đức', facets: ['inner.contentment', 'life.spirituality', 'relationships.family', 'wellbeing.longevity'], topic: 'phúc phần' }] },
  gia_dao: { id: 'gia_dao', title: 'Phụ Mẫu, Huynh Đệ và Tử Tức', scope: 'cha mẹ, anh chị em và con cái', sensitive: 'relationships',
    sections: [
      { palace: 'Phụ Mẫu', facets: [], topic: 'cha mẹ' },
      { palace: 'Huynh Đệ', facets: [], topic: 'anh chị em' },
      { palace: 'Tử Tức', facets: [], topic: 'con cái' },
    ] },
  di_no_tat: { id: 'di_no_tat', title: 'Thiên Di, Nô Bộc và Tật Ách', scope: 'môi trường bên ngoài, bạn bè cộng sự và thể trạng', sensitive: 'health',
    sections: [
      { palace: 'Thiên Di', facets: ['life.mobility'], topic: 'môi trường bên ngoài' },
      { palace: 'Nô Bộc', facets: ['relationships.social'], topic: 'bạn bè, cộng sự' },
      { palace: 'Tật Ách', facets: ['wellbeing.health', 'wellbeing.longevity'], topic: 'thể trạng' },
    ] },
  van_han: { id: 'van_han', title: 'Đại hạn và tiểu hạn', scope: 'các chặng mười năm và năm đang xem', sections: [] },
  // Bát Tự is a separate system: its chapter has no palace section (bazi.ts builds it from the pillars and the 'bat_tu' rules)
  bat_tu: { id: 'bat_tu', title: 'Bát Tự: tứ trụ và nhật chủ', scope: 'tứ trụ, nhật chủ và những câu sách Bát Tự đã đối chiếu', sections: [] },
};

export const CHAPTER_IDS = Object.keys(SPECS) as ChapterId[];
