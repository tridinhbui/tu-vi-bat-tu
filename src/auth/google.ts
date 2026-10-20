// Google OAuth 2.0 authorization-code flow. The id_token is read straight from Google's token endpoint over TLS, which is the
// case where Google documents that the signature check can be skipped; aud, iss, exp and email_verified are still checked.
import { randomToken } from "./session.ts";

export interface GoogleProfile { sub: string; email: string; name: string; picture: string }
export interface GoogleConfig { clientId: string; clientSecret: string }

export const redirectUri = (request: Request) => new URL("/api/auth/google/callback", request.url).toString();

export function authUrl(cfg: GoogleConfig, request: Request, state: string): string {
  const q = new URLSearchParams({
    client_id: cfg.clientId, redirect_uri: redirectUri(request), response_type: "code",
    scope: "openid email profile", state, prompt: "select_account",
  });
  return `https://accounts.google.com/o/oauth2/v2/auth?${q}`;
}

export const newState = () => randomToken(24);

export async function exchangeCode(cfg: GoogleConfig, request: Request, code: string): Promise<GoogleProfile> {
  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST", headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ code, client_id: cfg.clientId, client_secret: cfg.clientSecret, redirect_uri: redirectUri(request), grant_type: "authorization_code" }),
  });
  if (!res.ok) throw new Error(`token exchange failed (${res.status})`);
  const { id_token } = await res.json() as { id_token?: string };
  const part = id_token?.split(".")[1];
  if (!part) throw new Error("no id_token");
  const bin = atob(part.replace(/-/g, "+").replace(/_/g, "/"));
  const c = JSON.parse(new TextDecoder().decode(Uint8Array.from(bin, ch => ch.charCodeAt(0)))) as Record<string, unknown>;
  if (c.aud !== cfg.clientId) throw new Error("id_token audience mismatch");
  if (c.iss !== "https://accounts.google.com" && c.iss !== "accounts.google.com") throw new Error("id_token issuer mismatch");
  if (typeof c.exp !== "number" || c.exp < Date.now() / 1000) throw new Error("id_token expired");
  if (c.email_verified !== true || typeof c.sub !== "string" || typeof c.email !== "string") throw new Error("unverified Google account");
  return { sub: c.sub, email: c.email, name: typeof c.name === "string" ? c.name : "", picture: typeof c.picture === "string" ? c.picture : "" };
}
