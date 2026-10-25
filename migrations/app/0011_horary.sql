-- Saved horary questions (chiêm tinh vấn sự). Only what the signed-in user chose to save: the moment and place the question was
-- received, the confirmed reading of the question (its text included) and the fingerprint of the computed chart. The chart itself
-- is never stored: reopening recomputes it from these inputs and compares fingerprints (src/horary/route.ts).
CREATE TABLE IF NOT EXISTS horary_questions (
  user_id     TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  id          TEXT NOT NULL,
  moment_json TEXT NOT NULL,
  frame_json  TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  engine      TEXT NOT NULL,
  verdict     TEXT NOT NULL,
  saved_at    INTEGER NOT NULL,
  PRIMARY KEY (user_id, id)
);
CREATE INDEX IF NOT EXISTS horary_user_saved ON horary_questions(user_id, saved_at);
