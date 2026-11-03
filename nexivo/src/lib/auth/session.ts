import type { AuthRole, AuthUser } from "@/features/auth/types/auth.types";

export const NEXIVO_SESSION_COOKIE = "nexivo_session";
export const NEXIVO_SESSION_MAX_AGE = 60 * 60 * 24 * 14;

export type NexivoSession = {
  accessToken: string;
  user: AuthUser;
  role: AuthRole;
  expiresAt: number;
};

function sessionSecret() {
  const configured = process.env.NEXIVO_SESSION_SECRET?.trim();
  if (configured) return configured;
  if (process.env.NODE_ENV === "production") {
    throw new Error("NEXIVO_SESSION_SECRET is required in production.");
  }
  return "nexivo-development-session-secret";
}

function encode(value: string) {
  const bytes = new TextEncoder().encode(value);
  let binary = "";
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function decode(value: string) {
  const padded = value.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(value.length / 4) * 4, "=");
  const binary = atob(padded);
  const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

async function signingKey() {
  return crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(sessionSecret()),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign", "verify"]
  );
}

export async function createSessionToken(session: NexivoSession) {
  const payload = encode(JSON.stringify(session));
  const signature = await crypto.subtle.sign("HMAC", await signingKey(), new TextEncoder().encode(payload));
  let binary = "";
  new Uint8Array(signature).forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  const encodedSignature = btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
  return `${payload}.${encodedSignature}`;
}

export async function verifySessionToken(token: string | undefined): Promise<NexivoSession | null> {
  if (!token) return null;
  const [payload, encodedSignature] = token.split(".");
  if (!payload || !encodedSignature) return null;

  try {
    const signature = encodedSignature.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(encodedSignature.length / 4) * 4, "=");
    const signatureBytes = Uint8Array.from(atob(signature), (character) => character.charCodeAt(0));
    const valid = await crypto.subtle.verify(
      "HMAC",
      await signingKey(),
      signatureBytes,
      new TextEncoder().encode(payload)
    );
    if (!valid) return null;

    const session = JSON.parse(decode(payload)) as NexivoSession;
    if (!session.accessToken || !session.user || session.expiresAt <= Date.now()) return null;
    if (session.role !== session.user.role) return null;
    return session;
  } catch {
    return null;
  }
}
