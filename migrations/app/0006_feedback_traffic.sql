-- Feedback chat (the bubble on every page) and visit counting for the admin page.
-- The Worker also creates these tables on first use (src/feedback/store.ts), so a deploy works before this migration is applied.

-- One thread per visitor browser. The browser holds a random key; only its SHA-256 is stored, so the key alone proves ownership.
-- user_id/name/email are filled only when the visitor was signed in; ip_hash (SHA-256, never the address) rate-limits new threads.
CREATE TABLE IF NOT EXISTS feedback_threads (
  id         TEXT PRIMARY KEY,
  key_hash   TEXT NOT NULL UNIQUE,
  user_id    TEXT,
  name       TEXT NOT NULL DEFAULT '',
  email      TEXT NOT NULL DEFAULT '',
  page       TEXT NOT NULL DEFAULT '',
  ip_hash    TEXT NOT NULL DEFAULT '',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  admin_seen INTEGER NOT NULL DEFAULT 0       -- id of the last message the admin has read
);
CREATE INDEX IF NOT EXISTS feedback_threads_updated ON feedback_threads(updated_at);
CREATE INDEX IF NOT EXISTS feedback_threads_ip ON feedback_threads(ip_hash, created_at);

CREATE TABLE IF NOT EXISTS feedback_messages (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  thread_id  TEXT NOT NULL REFERENCES feedback_threads(id) ON DELETE CASCADE,
  author     TEXT NOT NULL CHECK (author IN ('visitor', 'admin')),
  body       TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS feedback_messages_thread ON feedback_messages(thread_id, id);

-- Unique visitors: one row per (Vietnam-time day, random browser id). The id is made in the browser and means nothing elsewhere.
CREATE TABLE IF NOT EXISTS visitor_days (
  day TEXT NOT NULL,
  vid TEXT NOT NULL,
  PRIMARY KEY (day, vid)
);
