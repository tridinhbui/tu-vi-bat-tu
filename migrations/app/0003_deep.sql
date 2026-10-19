-- A deep reading is paid for once and then kept, so opening it again costs nothing.
CREATE TABLE IF NOT EXISTS deep_readings (
  user_id    TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  fp         TEXT NOT NULL,                 -- birth fingerprint, same as charts.fp
  chapter    TEXT NOT NULL,
  text       TEXT NOT NULL,
  model      TEXT NOT NULL DEFAULT '',
  created_at INTEGER NOT NULL,
  PRIMARY KEY (user_id, fp, chapter)
);
