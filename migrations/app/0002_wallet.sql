-- Wallet: coins ("xu") plus a monthly free allowance, and an append-only ledger of every change.
CREATE TABLE IF NOT EXISTS wallets (
  user_id     TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  coins       INTEGER NOT NULL DEFAULT 0 CHECK (coins >= 0),
  free_period TEXT NOT NULL DEFAULT '',      -- month the free counter belongs to, YYYY-MM in Vietnam time
  free_used   INTEGER NOT NULL DEFAULT 0 CHECK (free_used >= 0),
  updated_at  INTEGER NOT NULL DEFAULT 0
);

-- kind: free_spend | coin_spend | grant | refund_free | refund_coin. delta is the change in coins (0 for free uses).
-- ref makes a write idempotent: a refund is "refund:<spend id>", a grant carries the caller's own reference.
CREATE TABLE IF NOT EXISTS ledger (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id    TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  kind       TEXT NOT NULL,
  usage      TEXT NOT NULL DEFAULT '',        -- what was bought: chat, deep, ...
  delta      INTEGER NOT NULL DEFAULT 0,
  period     TEXT NOT NULL DEFAULT '',
  ref        TEXT,
  created_at INTEGER NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS ledger_ref ON ledger(user_id, ref) WHERE ref IS NOT NULL;
CREATE INDEX IF NOT EXISTS ledger_user ON ledger(user_id, id);
