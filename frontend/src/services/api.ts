import type { LearnRequestPayload, LearningState } from "../types/learning";

const DEFAULT_BASE = "http://localhost:8000";

export function getBaseUrl(): string {
  return process.env.REACT_APP_API_URL || DEFAULT_BASE;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

export function formatErrorDetail(data: unknown, fallback: string): string {
  if (!isRecord(data)) {
    return fallback;
  }
  const detail = data.detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (isRecord(item) && typeof item.msg === "string") {
          return item.msg;
        }
        return JSON.stringify(item);
      })
      .join("; ");
  }
  return fallback;
}

/**
 * POST /learn — returns `LearningState` (unwraps `{ state }` from API).
 */
export async function callLearnAPI(
  payload: LearnRequestPayload,
  authToken: string,
): Promise<LearningState> {
  const url = `${getBaseUrl().replace(/\/$/, "")}/learn`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${authToken}`,
  };
  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify({
        user_id: payload.user_id,
        level: payload.level,
        target_language: payload.target_language,
        native_language: payload.native_language,
        user_answers: payload.user_answers ?? [],
        action: payload.action ?? "full",
        lesson: payload.lesson ?? {},
        exercises: payload.exercises ?? [],
      }),
    });
  } catch (err) {
    const message =
      err instanceof TypeError
        ? "Network error — is the API running on port 8000?"
        : err instanceof Error
          ? err.message
          : String(err);
    throw new Error(message);
  }

  const text = await response.text();
  let data: unknown;
  try {
    data = text ? (JSON.parse(text) as unknown) : {};
  } catch {
    throw new Error(text || `Invalid JSON (${response.status})`);
  }

  if (!response.ok) {
    const detail = formatErrorDetail(
      data,
      text || `Request failed (${response.status})`,
    );
    throw new Error(detail);
  }

  if (isRecord(data) && isRecord(data.state)) {
    return data.state as unknown as LearningState;
  }
  return data as unknown as LearningState;
}
