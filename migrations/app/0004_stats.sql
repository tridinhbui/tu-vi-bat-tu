-- Public counters shown on the landing page. They start from the figures the site already had (37 charts made, 15 people who joined)
-- and every real event after that adds one. Only totals are stored here, never anything about a person or a birth record.
CREATE TABLE IF NOT EXISTS stats (
  key        TEXT PRIMARY KEY,
  value      INTEGER NOT NULL DEFAULT 0 CHECK (value >= 0),
  updated_at INTEGER NOT NULL DEFAULT 0
);
INSERT OR IGNORE INTO stats (key, value) VALUES ('charts', 37), ('users', 15);
