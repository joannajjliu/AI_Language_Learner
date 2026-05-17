import type { AuthUser, GoogleAuthResponse } from "../types/auth";
import { formatErrorDetail, getBaseUrl } from "./api";

export async function verifyGoogleCredential(
  credential: string,
): Promise<AuthUser> {
  const url = `${getBaseUrl().replace(/\/$/, "")}/auth/google`;
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ credential }),
  });

  const text = await response.text();
  let data: unknown;
  try {
    data = text ? (JSON.parse(text) as unknown) : {};
  } catch {
    throw new Error(text || `Invalid JSON (${response.status})`);
  }

  if (!response.ok) {
    throw new Error(
      formatErrorDetail(data, text || `Sign-in failed (${response.status})`),
    );
  }

  const body = data as GoogleAuthResponse;
  return {
    user_id: body.user_id,
    email: body.email,
    name: body.name,
    picture: body.picture ?? null,
  };
}
