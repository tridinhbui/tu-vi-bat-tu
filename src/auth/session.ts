// Cookie sessions backed by D1. The cookie holds a random token; only its SHA-256 is stored.
export const COOKIE = "tvbt_session";
export const SESSION_DAYS = 30;

export interface User { id: string; email: string; name: string; picture: string }

const enc = new TextEncoder();
const b64url = (b: Uint8Array) => btoa(String.fromCharCode(...b)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
export const randomToken = (bytes = 32) => b64url(crypto.getRandomValues(new Uint8Array(bytes)));
export async function sha256(s: string): Promise<string> {
  return [...new Uint8Array(await crypto.subtle.digest("SHA-256", enc.encode(s)))].map(x => x.toString(16).padStart(2, "0")).join("");
}

export function readCookie(request: Request, name: string): string | null {
  for (const part of (request.headers.get("cookie") ?? "").split(";")) {
    const i = part.indexOf("=");
    if (i > 0 && part.slice(0, i).trim() === name) return part.slice(i + 1).trim();
  }
  return null;
}

export function setCookie(request: Request, name: string, value: string, maxAgeSec: number): string {
  const secure = new URL(request.url).protocol === "https:" ? "; Secure" : "";
  return `${name}=${value}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${maxAgeSec}${secure}`;
}

export async function createSession(db: D1Database, request: Request, userId: string): Promise<string> {
  const token = randomToken();
  const exp = Math.floor(Date.now() / 1000) + SESSION_DAYS * 86400;
  await db.prepare("INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)").bind(await sha256(token), userId, exp).run();
  return setCookie(request, COOKIE, token, SESSION_DAYS * 86400);
}

export async function currentUser(db: D1Database, request: Request): Promise<User | null> {
  const token = readCookie(request, COOKIE);
  if (!token) return null;
  return db.prepare(
    "SELECT u.id, u.email, u.name, u.picture FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.token_hash = ? AND s.expires_at > ?")
    .bind(await sha256(token), Math.floor(Date.now() / 1000)).first<User>();
}

export async function destroySession(db: D1Database, request: Request): Promise<void> {
  const token = readCookie(request, COOKIE);
  if (token) await db.prepare("DELETE FROM sessions WHERE token_hash = ?").bind(await sha256(token)).run();
}
