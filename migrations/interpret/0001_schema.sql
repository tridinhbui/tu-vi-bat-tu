-- Thiên Bàn interpretation knowledge base (Cloudflare D1 / SQLite). Deterministic: no table holds model output.
-- Apply:  wrangler d1 migrations apply thien-ban-interpret   (migrations_dir = migrations/interpret)

CREATE TABLE IF NOT EXISTS kb_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);

-- Book references. `verified` = the locator was checked against the source.
CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY, title TEXT NOT NULL, author TEXT, locator TEXT, verified INTEGER NOT NULL DEFAULT 0
);

-- Rules: conditions are the closed DSL of engine/tvbt/knowledge/dsl.py (all / any / not / count / fact / ref).
CREATE TABLE IF NOT EXISTS rules (
  id TEXT PRIMARY KEY, system TEXT NOT NULL, school TEXT, category TEXT, subject TEXT NOT NULL, priority INTEGER NOT NULL DEFAULT 0,
  conditions_json TEXT NOT NULL, consequences_json TEXT NOT NULL, exceptions_json TEXT NOT NULL DEFAULT '[]',
  source_ids_json TEXT NOT NULL DEFAULT '[]', review_status TEXT NOT NULL CHECK (review_status IN ('draft','verified','disputed')),
  cites_json TEXT NOT NULL DEFAULT '[]', reading TEXT
);
CREATE INDEX IF NOT EXISTS rules_system ON rules (system, subject);

-- Vietnamese claim phrasing ('limit:<claim>' rows hold the wording of a limiting rule).
CREATE TABLE IF NOT EXISTS claims (id TEXT PRIMARY KEY, label TEXT NOT NULL);

-- Semantic lexicon and the explicit relations between concepts (supports / qualifies / contradicts / ...).
CREATE TABLE IF NOT EXISTS concepts (
  id TEXT PRIMARY KEY, facet TEXT NOT NULL, pol TEXT NOT NULL CHECK (pol IN ('+','-','~')), kind TEXT NOT NULL, opp TEXT,
  cues_json TEXT NOT NULL, np TEXT NOT NULL, short TEXT
);
CREATE TABLE IF NOT EXISTS concept_relations (
  a TEXT NOT NULL, b TEXT NOT NULL, type TEXT NOT NULL, frame TEXT, synth TEXT, PRIMARY KEY (a, b, type)
);

-- Static knowledge graph (stars, palaces, profiles, rule anchors). Per-chart graphs are built in memory and cached with the output.
CREATE TABLE IF NOT EXISTS kg_nodes (id TEXT PRIMARY KEY, kind TEXT NOT NULL, label TEXT NOT NULL, data_json TEXT);
CREATE TABLE IF NOT EXISTS kg_edges (src TEXT NOT NULL, dst TEXT NOT NULL, kind TEXT NOT NULL, data_json TEXT, PRIMARY KEY (src, dst, kind));

-- Editorial content modules: curated, source-grounded interpretation units. A module renders only when its evidence gate is met by
-- rules that actually fired on the chart; every passage declares its basis and citations.
CREATE TABLE IF NOT EXISTS content_modules (
  id TEXT PRIMARY KEY, chapter TEXT NOT NULL, role TEXT NOT NULL, version INTEGER NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('draft','in_review','approved','retired')),
  title TEXT NOT NULL, when_json TEXT, evidence_json TEXT, slots_json TEXT, author TEXT, updated_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS module_passages (
  module_id TEXT NOT NULL REFERENCES content_modules(id), passage_id TEXT NOT NULL, ord INTEGER NOT NULL, when_json TEXT,
  basis TEXT NOT NULL CHECK (basis IN ('sach','dieu_kien','he_thong','tinh_toan')), kind TEXT NOT NULL DEFAULT 'claim',
  variants_json TEXT NOT NULL, cites_json TEXT NOT NULL DEFAULT '[]', PRIMARY KEY (module_id, passage_id)
);
-- Editorial workflow: every status change of a module version is a review row (who, decision, notes).
CREATE TABLE IF NOT EXISTS module_reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT, module_id TEXT NOT NULL REFERENCES content_modules(id), version INTEGER NOT NULL,
  reviewer TEXT NOT NULL, decision TEXT NOT NULL CHECK (decision IN ('submit','approve','request_changes','retire')),
  notes TEXT, created_at TEXT DEFAULT (datetime('now'))
);

-- Output cache: one row per (chart facts, chapter, engine version, knowledge version). Large bodies may live in R2 (r2_key).
CREATE TABLE IF NOT EXISTS interpretations (
  cache_key TEXT PRIMARY KEY, chapter TEXT NOT NULL, engine_version TEXT NOT NULL, kb_version TEXT NOT NULL,
  output_json TEXT, r2_key TEXT, quality_pass INTEGER NOT NULL, created_at TEXT DEFAULT (datetime('now'))
);
-- Argument graphs kept for audit (what the planner decided and why), keyed like the output.
CREATE TABLE IF NOT EXISTS argument_graphs (cache_key TEXT PRIMARY KEY, chapter TEXT NOT NULL, graph_json TEXT NOT NULL);
