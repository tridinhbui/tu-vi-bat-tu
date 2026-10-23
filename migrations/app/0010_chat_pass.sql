-- Chat pass: every top-up (a paid coin pack or a gift code) gives 30 days of free chat, at most 30 messages a day (src/billing/config.ts
-- TOPUP_CHAT). `until` is when the pass ends, in ms; a new top-up extends it from the later of now and the current end.
-- Its own table, created with IF NOT EXISTS, so the Worker can also create it on first use (src/billing/wallet.ts) and this migration still
-- applies cleanly afterwards. The daily free counter reuses wallets.free_period / free_used, now holding a day (YYYY-MM-DD) instead of a month.
CREATE TABLE IF NOT EXISTS chat_passes (
  user_id    TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  until      INTEGER NOT NULL DEFAULT 0,
  updated_at INTEGER NOT NULL DEFAULT 0
);
