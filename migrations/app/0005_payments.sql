-- One row per paid Checkout session: a record for support and reconciliation. The coins themselves are credited through the ledger
-- (ref "stripe:<session id>"), which is what makes a repeated webhook harmless.
CREATE TABLE IF NOT EXISTS payments (
  session_id TEXT PRIMARY KEY,
  user_id    TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  pack       TEXT NOT NULL,
  coins      INTEGER NOT NULL,
  amount     INTEGER NOT NULL,
  currency   TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS payments_user ON payments(user_id, created_at);
