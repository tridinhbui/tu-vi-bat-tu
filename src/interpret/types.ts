// Shared types of the deterministic interpretation pipeline. No field anywhere holds model-generated text.

export type Facts = Record<string, unknown>;
export type Tri = boolean | null;                       // three-valued logic: true / false / unknown

export type Expr =
  | { all: Expr[] } | { any: Expr[] } | { not: Expr }
  | { count: Expr[]; operator?: string; value: number }
  | { fact: string; operator?: string; value: unknown }
  | { ref: { palace: string; fact: string }; operator?: string; value: unknown };

export interface Source { id: string; title: string; author: string | null; locator: string | null; verified: boolean }

export interface Rule {
  id: string; system: string; school: string; category: string; subject: 'palace' | 'chart'; priority: number;
  conditions: Expr; consequences: Array<{ kind: 'finding' | 'assert'; claim?: string; effect?: 'support' | 'limit' | 'neutral'; fact?: string; value?: unknown; scope?: string }>;
  exceptions: Expr[]; sourceIds: string[]; reviewStatus: 'draft' | 'verified' | 'disputed'; cites: string[]; reading: string | null;
}

export interface Finding {
  id: string; ruleId: string; subject: string; palace: string | null; claim: string; effect: 'support' | 'limit' | 'neutral';
  basis: 'verified' | 'draft'; depth: number;
}

export interface Palace {
  name: string; branch: string; branch_index: number; stem: string; is_than: boolean; stars: string[]; major_stars: string[];
  major_dignity: Record<string, string | null>; minor_dignity: Record<string, string | null>; tuan: boolean; triet: boolean;
  // phụ tinh with a known level: the book's printed term (e.g. 'lợi'), the book it came from and the page (engine/data/dignity_aux.json)
  minor_dignity_src?: Record<string, { term: string; school: 'thuc_hanh' | 'toan_thu' | 'khao_luan'; locator: string }>;
}

export interface Decade {
  index: number; branch: string; palace: string; age_from: number; age_to: number; stem: string;
  hoa: Record<string, { star: string; palace: string | null }>; readings: Array<{ text: string; src: string }>;
}

/** What /api/facts returns: chart data computed by the validated Python engine; nothing interpreted. */
export interface ChartInput {
  engine: string; birth_year: number; lunar_year: number; gender: 'male' | 'female'; year_gz: string;
  cuc: { name: string; element: string }; menh_nap_am: string; menh_cuc_relation: string; yin_yang_gender: string; dai_han_direction: string;
  palaces: Palace[]; tu_hoa: Record<string, { star: string; branch: number }>; base: Record<string, Facts>; decades: Decade[];
  year: { year: number; age_tuoi_mu: number; dai_han: { palace: string; age_from: number; age_to: number; stem?: string; branch?: string } | null;
    tieu_han_palace?: string; tieu_han_branch?: string; tieu_han_topic?: string | null; annual_pillar?: string; luu_thai_tue_palace?: string;
    tieu_han_reading?: Array<{ text: string; src: string }>;
    luu_tu_hoa_reading?: Array<{ hoa: string; star: string; palace: string | null; advice: string; position_note: string | null; src: string }> };
  /** Bát Tự (absent in facts produced before the field existed): the 'bat_tu' fact base and the computed pillars, for the Bát Tự chapter */
  bazi?: BaziInput;
}
export interface BaziPillar { name: string; stem: string; branch: string; stem_ten_god: string | null; stage: string | null;
  hidden: Array<{ stem: string; element: string; ten_god: string }> }
export interface BaziInput {
  base: Record<string, Facts>; pillars: Record<'year' | 'month' | 'day' | 'hour', BaziPillar>; day_master: string; day_master_element: string;
  luck_direction: string; luck_start_age: number; luck: Array<{ name: string; start_age: number; start_year: number | null; start_date?: string; ten_god: string | null }>;
  kong_wang_day?: string[];
  /** pillar relations by kind (stem_combine, branch_clash …), each with its pillars "year-hour" (absent in facts produced before the field) */
  relations?: Record<string, Array<{ pillars: string }>>;
  /** structure analysis for the prose (engine/tvbt/bazi_deep pipeline.prose_summary); null when it could not read the chart */
  deep?: import('./prose/bazi_deep.ts').BaziDeep | null;
}

export interface Concept { id: string; facet: string; pol: '+' | '-' | '~'; kind: string; opp?: string; cues: string[]; np: string; short?: string }
export interface Relation { a: string; b: string; type: string; frame?: string; synth?: string }

export type Basis = 'sach' | 'dieu_kien' | 'he_thong' | 'tinh_toan';

export interface Passage {
  id: string; when?: ModuleCond; basis: Basis; kind?: 'claim' | 'ground' | 'contrast' | 'interaction' | 'condition' | 'timing' | 'reflection' | 'limit' | 'limits' | 'intro' | 'synthesis' | 'frame' | 'notice' | 'method';
  variants: string[]; cites?: string[]; each?: string; followups?: string[];
}
/** Conditions a content module or passage may test: chart facts (DSL), fired rules, and computed slots. */
export type ModuleCond =
  | { all: ModuleCond[] } | { any: ModuleCond[] } | { not: ModuleCond }
  | { fired: string } | { firedAny: string[] } | { slot: string; truthy?: boolean; eq?: unknown; gte?: number; contains?: string }
  | { list: string; min?: number }
  | { fact: string; palace?: string; operator?: string; value: unknown };

export interface ContentModule {
  id: string; chapter: string; role: 'central' | 'factor' | 'counter' | 'cross' | 'dominance' | 'timing' | 'limits' | 'synthesis';
  /** module-level iteration: render every passage once per item of this list and emit one paragraph per item (title from the item) */
  each?: string;
  /** with `each`: render all items into ONE paragraph (item after item) instead of one paragraph per item */
  merge?: boolean;
  /** '*' modules are shared by every chapter except those listed here */
  exceptChapters?: string[];
  version: number; status: 'draft' | 'in_review' | 'approved' | 'retired'; title: string; order: number;
  when?: ModuleCond; evidence?: { anyRules?: string[]; allRules?: string[]; minFired?: number };
  passages: Passage[]; author?: string; reviewers?: string[]; notes?: string;
}

export interface Knowledge {
  version: string; sources: Source[]; rules: Rule[]; claims: Record<string, string>;
  concepts: { negators: string[]; concepts: Concept[]; valence_cues?: unknown }; relations: { relations: Relation[]; frames: Record<string, string> };
  ontology: any; starProfiles: { stars: Record<string, { element?: string; dau?: string; domain?: string; locator?: string }> };
  modules: ContentModule[];
  reference?: Reference;
  kg?: { qualifiers: import('./kg/qualifiers.ts').Qualifier[]; ruleConcepts?: Record<string, import('./kg/lift.ts').RuleConcept>;
    relations?: import('./kg/resolve.ts').KgRelation[];
    /** corpus rates (0 … 1) of each concept asserted at Mệnh and each rule firing on Mệnh (engine/data/kg/base_rates.json) */
    baseRates?: { concept: Record<string, number>; rule: Record<string, number>;
      /** the same rates for each other palace (tools/interpret/base_rates.ts), for the palace reasoner */
      palaces?: Record<string, { concept: Record<string, number>; rule: Record<string, number> }> };
    positionGuards?: import('./reason/positions.ts').PositionGuard[];
    formations?: import('./reason/structures.ts').Formation[] };
  prose?: import('./prose/types.ts').ProseLibrary;
}

/** Sourced reference material compiled by tools/interpret/build.ts (see the comment there for the page of each table). */
export interface Reference {
  palaceRoles: { cite: string; roles: Record<string, string> };
  groupNotes: { cite: string; notes: Record<string, string>; members: Record<string, string[]> };
  lifeStages: { cite: string; thuan: Record<string, string>; nghich: Record<string, string>; domain: Record<string, string> };
  tuHoa: { cite: string; meaning: Record<string, string>; positionNotes: Record<string, string>; byPalace: Record<string, Record<string, string>>; weightNote: string;
    byStem: Record<string, Array<{ star: string; advice: string }>> };
  dignity: { source: string; levels: string[]; locators: Record<string, string> };
}
