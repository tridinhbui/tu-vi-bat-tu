// Prose library types (prose plan §3). The library holds only HOW to say things; WHAT is said comes from the knowledge graph:
// a concept card voices a concept that a fired, linked rule asserted; frames and modifier cards only name chart facts (star, palace,
// branch, Hóa, Tuần/Triệt) and relations the resolver applied. No card may introduce a claim of its own.
//
// Slot syntax is the generator's ({key} required, {?key|body} optional). Fragments ("pred", "turn", "soft", "mature") are lower-case
// clauses without a final period; "behave" items are whole sentences whose subject is {S} (the current way to refer to the person).

export type CardStatus = 'draft' | 'in_review' | 'approved' | 'retired';
export type Move = 'ANCHOR' | 'ELABORATE' | 'TURN' | 'RESCUE' | 'TENSION' | 'TIMING' | 'SATELLITE' | 'VALUE' | 'TRANSFORM' | 'BORROW';

/** How one concept is voiced. Which fields are required depends on the concept's polarity (see lint.ts). */
export interface ConceptCard {
  id: string;                      // concept id (knowledge.concepts)
  status: CardStatus;
  np: string;                      // noun phrase, for aggregation and VALUE: "óc suy xét sắc bén"
  pron: string;                    // anaphor after first mention: "sự sắc sảo ấy"
  pred?: string[];                 // predicate after "thường …" (affirmed, + and ~ concepts)
  behave?: string[];               // whole sentences, subject {S}
  turn?: string[];                 // predicate after "dễ …" for the limiting side (- concepts)
  soft?: string[];                 // predicate when the assertion is softened/weakened or the stance is 'weakens'
  value?: string[];                // NP for "điều đáng quý là …" (+ concepts)
  mature?: string[];               // clause for "khi biết …" (- concepts, and + concepts with a shadow)
  shadow?: string;                 // concept id of this trait's limiting side, when one exists
  notes?: string;
}

/** Sentence frames that name the chart (no claims): anchors for the Mệnh configuration, dignity phrases, references to the person. */
export interface Frames {
  anchor: Record<'single' | 'pair' | 'vcd' | 'vcd_own' | 'vcd_plain', string[]>;     // opener up to the predicate: "Người có {stars} tọa Mệnh tại {branch}"
  anchor_palace: Record<'single' | 'pair' | 'vcd' | 'vcd_own' | 'vcd_plain', string[]>; // the same for any other palace, named by {palace}
  via: string[];                                             // a reading carried by another palace: "Nhìn từ cung {from}, {S}"
  dignity: Record<string, string[]>;                         // "hãm" -> ["đứng thế hãm", "ở vào thế hãm"]
  subject: { first: string[]; next: string[]; palace_first: string[] }; // {S}: "Người có lá số này" / "Họ"; palace frames: "đương số"
  other: Record<string, { first: string[]; next: string[] }>; // Phu Thê, Nô Bộc: the people a non-bond reading is about
}

/** Voicing of a chart fact or resolver decision that changes how a concept lands (Tứ Hóa, sát đắc/hãm, Tuần/Triệt, rescues …). */
export interface ModifierCard {
  id: string; status: CardStatus; move: Move;
  when: { relation?: string; hoa?: string; star_group?: 'sat' | 'cat'; dignity_ok?: boolean; tuan_triet?: boolean; status?: string; degree?: 'up' | 'down' | 'mixed' };
  variants: string[];
}

/** A paragraph shape: moves in order; '?' marks an optional move. `needs`/`forbid` test the argument tree. */
export interface ParagraphSchema { id: string; needs: Move[]; forbid?: Move[]; order: string[]; note?: string }

export type ConnRel = 'contrast' | 'concession' | 'rescue' | 'addition' | 'consequence' | 'synthesis' | 'elaboration' | 'timing';
export interface Connective { id: string; rel: ConnRel; text: string; pos: 'initial' | 'medial'; register?: 'neutral' | 'literary' }

export interface ProseLibrary {
  version: string; concepts: ConceptCard[]; frames: Frames; modifiers: ModifierCard[]; schemas: ParagraphSchema[]; connectives: Connective[];
  vanhan?: import('./vanhan.ts').VanHanLibrary; bazi?: import('./bazi.ts').BaziLibrary;
}
