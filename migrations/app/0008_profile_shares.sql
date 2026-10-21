-- Phase 3: the signed-in user's own profile ("Thông tin cá nhân") and share links for saved charts.
-- src/account/schema.ts runs the same statements once per isolate, so a deploy works before this migration is applied.

-- data_json: name, gender, birth date as typed (solar or lunar) plus its solar equivalent, birth hour (null = unknown), place,
-- career and relationship status. Whitelisted field by field in src/account/profile.ts.
CREATE TABLE IF NOT EXISTS profiles (
  user_id    TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  data_json  TEXT NOT NULL,
  updated_at INTEGER NOT NULL
);

-- One row per share link. id is 128 random bits (base64url), the only thing a viewer needs; the link points at the saved chart
-- (user_id, chart_fp) rather than copying it, so deleting the chart ends the link too. revoked_at set = the owner turned the link off.
-- hide_birth = 1: viewers never receive the name or the birth date and hour; the Worker computes the chart for them.
CREATE TABLE IF NOT EXISTS shares (
  id         TEXT PRIMARY KEY,
  user_id    TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  chart_fp   TEXT NOT NULL,
  hide_birth INTEGER NOT NULL DEFAULT 1,
  created_at INTEGER NOT NULL,
  revoked_at INTEGER
);
CREATE INDEX IF NOT EXISTS shares_user ON shares(user_id, created_at);
