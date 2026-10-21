-- Mời bạn (referral). The Worker also creates these tables on first use (src/referral/route.ts), so a deploy works before this
-- migration is applied. Rewards are paid as ordinary wallet grants (ledger refs "referral:joined" / "referral:invited:<user>").
-- Numbered 0009 so it cannot collide with migrations other branches add as 0007/0008.

-- One code per user, made the first time the user opens "Mời bạn".
CREATE TABLE IF NOT EXISTS referral_codes (
  user_id    TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  code       TEXT NOT NULL UNIQUE,
  created_at INTEGER NOT NULL
);

-- An account can join through at most one code (invitee_id is the key).
CREATE TABLE IF NOT EXISTS referrals (
  invitee_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  inviter_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  code       TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS referrals_inviter ON referrals(inviter_id);
