-- App database (binding DB): accounts, sessions and saved charts. Separate from migrations/interpret (the knowledge base).
CREATE TABLE IF NOT EXISTS users (
  id         TEXT PRIMARY KEY,
  google_sub TEXT NOT NULL UNIQUE,
  email      TEXT NOT NULL,
  name       TEXT NOT NULL DEFAULT '',
  picture    TEXT NOT NULL DEFAULT '',
  created_at INTEGER NOT NULL
);

-- token_hash is the SHA-256 of the cookie value; the raw token is never stored.
CREATE TABLE IF NOT EXISTS sessions (
  token_hash TEXT PRIMARY KEY,
  user_id    TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  expires_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS sessions_user ON sessions(user_id);

-- One row per distinct birth record per user; fp = year-month-day-hour-minute-gender, so the same chart saved on two devices merges.
CREATE TABLE IF NOT EXISTS charts (
  user_id    TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  fp         TEXT NOT NULL,
  id         TEXT NOT NULL,
  label      TEXT NOT NULL,
  rel        TEXT NOT NULL,
  req_json   TEXT NOT NULL,
  updated_at INTEGER NOT NULL,
  PRIMARY KEY (user_id, fp)
);
