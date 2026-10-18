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
  year: { year: number; age_tuoi_mu: number; dai_han: { palace: string; age_from: number; age_to: number } | null };
}

export interface Concept { id: string; facet: string; pol: '+' | '-' | '~'; kind: string; opp?: string; cues: string[]; np: string; short?: string }
export interface Relation { a: string; b: string; type: string; frame?: string; synth?: string }

export type Basis = 'sach' | 'dieu_kien' | 'he_thong' | 'tinh_toan';

export interface Passage {
  id: string; when?: ModuleCond; basis: Basis; kind?: 'claim' | 'ground' | 'contrast' | 'interaction' | 'condition' | 'timing' | 'reflection' | 'limit' | 'intro' | 'synthesis';
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
  version: number; status: 'draft' | 'in_review' | 'approved' | 'retired'; title: string; order: number;
  when?: ModuleCond; evidence?: { anyRules?: string[]; allRules?: string[]; minFired?: number };
  passages: Passage[]; author?: string; reviewers?: string[]; notes?: string;
}

export interface Knowledge {
  version: string; sources: Source[]; rules: Rule[]; claims: Record<string, string>;
  concepts: { negators: string[]; concepts: Concept[]; valence_cues?: unknown }; relations: { relations: Relation[]; frames: Record<string, string> };
  ontology: any; starProfiles: { stars: Record<string, { element?: string; dau?: string; domain?: string; locator?: string }> };
  modules: ContentModule[];
}
