-- Phase 2 (thương mại hóa): orders for every payment provider, discount and gift codes, and chapters unlocked with coins.

-- One row per purchase attempt, created before the visitor is sent to the payment page. The provider's callback (Stripe webhook,
-- VNPAY IPN) is checked against THIS row: the amount, the coins and the user come from here, never from the callback alone.
-- The coins are credited through the ledger (ref "stripe:<session id>" or "vnpay:<order id>"), which keeps a repeated callback harmless.
CREATE TABLE IF NOT EXISTS orders (
  id            TEXT PRIMARY KEY,               -- our id; VNPAY's vnp_TxnRef
  user_id       TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  provider      TEXT NOT NULL,                  -- stripe | vnpay
  provider_ref  TEXT NOT NULL DEFAULT '',       -- Stripe Checkout session id, VNPAY vnp_TransactionNo
  pack          TEXT NOT NULL,
  coins         INTEGER NOT NULL,
  list_amount   INTEGER NOT NULL,               -- VND before the discount
  amount        INTEGER NOT NULL,               -- VND to pay
  currency      TEXT NOT NULL DEFAULT 'vnd',
  discount_code TEXT NOT NULL DEFAULT '',
  discount_pct  INTEGER NOT NULL DEFAULT 0,
  status        TEXT NOT NULL DEFAULT 'pending', -- pending | paid | failed
  detail        TEXT NOT NULL DEFAULT '',       -- provider response code or bank, for support
  created_at    INTEGER NOT NULL,
  paid_at       INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS orders_user ON orders(user_id, created_at);
CREATE INDEX IF NOT EXISTS orders_created ON orders(created_at);

-- Codes made on /admin. kind discount: percent off a coin pack bought with money, counted when the payment succeeds.
-- kind gift: a fixed number of coins, once per account. max_uses caps both; expires_at 0 means it never expires.
CREATE TABLE IF NOT EXISTS promo_codes (
  code       TEXT PRIMARY KEY,                  -- upper case, A-Z 0-9 and dash
  kind       TEXT NOT NULL CHECK (kind IN ('discount', 'gift')),
  percent    INTEGER NOT NULL DEFAULT 0,
  coins      INTEGER NOT NULL DEFAULT 0,
  max_uses   INTEGER NOT NULL DEFAULT 1,
  used       INTEGER NOT NULL DEFAULT 0,
  expires_at INTEGER NOT NULL DEFAULT 0,
  active     INTEGER NOT NULL DEFAULT 1,
  note       TEXT NOT NULL DEFAULT '',
  created_by TEXT NOT NULL DEFAULT '',
  created_at INTEGER NOT NULL
);

-- A report chapter opened for one chart (birth fingerprint, as charts.fp). Paid once, kept: the paywall reads this table.
CREATE TABLE IF NOT EXISTS unlocks (
  user_id    TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  fp         TEXT NOT NULL,
  chapter    TEXT NOT NULL,
  plan       TEXT NOT NULL,
  ledger_ref TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  PRIMARY KEY (user_id, fp, chapter)
);
