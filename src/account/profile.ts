// "Thông tin cá nhân": one profile per signed-in user. It prefills the chart form and, through career and relationship status,
// decides which chapters the reading shows first (engine/web/js/focus.js). Nothing here feeds a claim about the chart.

// Keys are what the page sends and stores; the Vietnamese labels live in the page (profile.js) next to the same keys.
export const CAREERS = ["hoc", "lam", "kinh_doanh", "tim_viec", "nghi"] as const;
export const RELATIONSHIPS = ["doc_than", "tim_hieu", "ket_hon", "chia_tay"] as const;

export interface Profile {
  name: string;
  gender: "male" | "female" | "";
  cal: "solar" | "lunar";
  year: number; month: number; day: number; leap: boolean;
  hour: number | null; minute: number;                 // hour null: the user does not know the birth hour
  solar: { year: number; month: number; day: number } | null;   // the date as dương lịch (equal to the typed date when cal is solar)
  place: string; tz: string;
  career: (typeof CAREERS)[number] | "";
  relationship: (typeof RELATIONSHIPS)[number] | "";
}

const int = (v: unknown, lo: number, hi: number) => Number.isInteger(v) && (v as number) >= lo && (v as number) <= hi;
const str = (v: unknown, max: number) => typeof v === "string" ? v.replace(/[\u0000-\u001F\u007F]/g, "").trim().slice(0, max) : "";

/** Whitelists a profile field by field; returns the error text for the first bad field instead when there is one. */
export function cleanProfile(x: unknown): Profile | string {
  if (!x || typeof x !== "object") return "body must be a profile object";
  const p = x as Record<string, unknown>;
  const cal = p.cal === "lunar" ? "lunar" : p.cal === "solar" || p.cal === undefined ? "solar" : null;
  if (!cal) return "cal must be solar or lunar";
  if (!int(p.year, 1900, 2049)) return "year must be 1900..2049";
  if (!int(p.month, 1, 12)) return "month must be 1..12";
  if (!int(p.day, 1, cal === "lunar" ? 30 : 31)) return "day out of range";
  if (cal === "solar") {
    const d = new Date(Date.UTC(p.year as number, (p.month as number) - 1, p.day as number));
    if (d.getUTCDate() !== p.day) return "no such date";
  }
  const hour = p.hour === null || p.hour === undefined ? null : p.hour;
  if (hour !== null && !int(hour, 0, 23)) return "hour must be 0..23 or null";
  const minute = p.minute === undefined || hour === null ? 0 : p.minute;
  if (!int(minute, 0, 59)) return "minute must be 0..59";
  const gender = p.gender === "male" || p.gender === "female" ? p.gender : p.gender === undefined || p.gender === "" ? "" : null;
  if (gender === null) return "gender must be male, female or empty";
  const career = p.career === undefined || p.career === "" ? "" : (CAREERS as readonly unknown[]).includes(p.career) ? p.career as Profile["career"] : null;
  if (career === null) return "unknown career status";
  const relationship = p.relationship === undefined || p.relationship === "" ? "" : (RELATIONSHIPS as readonly unknown[]).includes(p.relationship) ? p.relationship as Profile["relationship"] : null;
  if (relationship === null) return "unknown relationship status";
  let solar: Profile["solar"] = null;
  if (cal === "solar") solar = { year: p.year as number, month: p.month as number, day: p.day as number };
  else if (p.solar && typeof p.solar === "object") {
    const s = p.solar as Record<string, unknown>;
    if (!int(s.year, 1899, 2050) || !int(s.month, 1, 12) || !int(s.day, 1, 31)) return "solar must be {year, month, day}";
    solar = { year: s.year as number, month: s.month as number, day: s.day as number };
  }
  const tz = str(p.tz, 40);
  if (tz && !/^[A-Za-z_]+(\/[A-Za-z0-9_+-]+){0,2}$/.test(tz)) return "tz must be an IANA zone name";
  return {
    name: str(p.name, 60), gender, cal, year: p.year as number, month: p.month as number, day: p.day as number,
    leap: cal === "lunar" && p.leap === true, hour: hour as number | null, minute: minute as number, solar,
    place: str(p.place, 40), tz, career, relationship,
  };
}

export async function getProfile(db: D1Database, userId: string): Promise<Profile | null> {
  const r = await db.prepare("SELECT data_json FROM profiles WHERE user_id = ?").bind(userId).first<{ data_json: string }>();
  return r ? JSON.parse(r.data_json) as Profile : null;
}

export async function putProfile(db: D1Database, userId: string, p: Profile): Promise<void> {
  await db.prepare("INSERT INTO profiles (user_id, data_json, updated_at) VALUES (?, ?, ?) ON CONFLICT (user_id) DO UPDATE SET data_json = excluded.data_json, updated_at = excluded.updated_at")
    .bind(userId, JSON.stringify(p), Date.now()).run();
}
