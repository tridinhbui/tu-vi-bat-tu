-- Tarot (src/tarot/route.ts), behind TVBT_TAROT. Written, not applied: apply with `npx wrangler d1 migrations apply tvbt-app --remote`
-- before turning TVBT_TAROT on (the route also creates these tables on first use, as account/route.ts does).
-- tarot_draws: one row per shuffle. The seed alone fixes the deck order and the reversal bits (src/tarot/draw.ts); picks_json holds the
-- fan positions the reader chose. user_id is set when a signed-in reader draws or saves; question is stored only when the reader saves
-- it, and show_question (default off) lets a shared link print it. Unsaved rows are removed after two days.
CREATE TABLE IF NOT EXISTS tarot_draws (
  id TEXT PRIMARY KEY,
  seed TEXT NOT NULL,
  spread INTEGER NOT NULL,
  reversals INTEGER NOT NULL DEFAULT 1,
  picks_json TEXT,
  user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
  saved INTEGER NOT NULL DEFAULT 0,
  question TEXT,
  show_question INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL,
  revealed_at INTEGER,
  saved_at INTEGER
);
CREATE INDEX IF NOT EXISTS tarot_draws_user ON tarot_draws(user_id, saved, saved_at);
CREATE INDEX IF NOT EXISTS tarot_draws_unsaved ON tarot_draws(saved, created_at);
-- tarot_daily: free draws per reader per day (Vietnam date). key = 'u:<user id>' or 'ip:<salted hash of the address>'.
CREATE TABLE IF NOT EXISTS tarot_daily (
  key TEXT NOT NULL,
  day TEXT NOT NULL,
  n INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (key, day)
);
