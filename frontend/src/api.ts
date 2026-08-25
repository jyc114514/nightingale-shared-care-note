import type {
  ApiErrorShape,
  Comment,
  Diff,
  GlanceItem,
  Me,
  Patient,
  ProvenanceSource,
  TimelineEntry,
  Version,
} from "./types";

const apiBaseUrl = (
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/$/, "");

export class ApiError extends Error {
  readonly status: number;
  readonly body: ApiErrorShape;

  constructor(status: number, body: ApiErrorShape) {
    const detail = body.detail;
    const message = typeof detail === "string" ? detail : detail?.message;
    super(message ?? `Request failed with HTTP ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });
  const raw = await response.text();
  const body = raw ? (JSON.parse(raw) as T & ApiErrorShape) : (undefined as T);
  if (!response.ok) {
    throw new ApiError(response.status, (body ?? {}) as ApiErrorShape);
  }
  return body as T;
}

const json = (value: unknown): RequestInit => ({ body: JSON.stringify(value) });

export const api = {
  me: () => request<Me>("/auth/me"),
  login: (email: string, password: string) =>
    request<{ user: Me }>("/auth/login", {
      method: "POST",
      ...json({ email, password }),
    }),
  logout: () => request<void>("/auth/logout", { method: "POST" }),
  patients: () => request<Patient[]>("/patients"),
  timeline: (patientId: string) =>
    request<TimelineEntry[]>(`/patients/${patientId}/timeline`),
  glance: (patientId: string) =>
    request<GlanceItem[]>(`/patients/${patientId}/glance`),
  source: (highlightId: string) =>
    request<ProvenanceSource>(`/highlights/${highlightId}/source`),
  comments: (entryId: string) =>
    request<Comment[]>(`/entries/${entryId}/comments`),
  addComment: (entryId: string, body: string, parentCommentId?: string) =>
    request<Comment>(`/entries/${entryId}/comments`, {
      method: "POST",
      ...json({ body, parent_comment_id: parentCommentId ?? null }),
    }),
  resolveComment: (commentId: string, isResolved: boolean) =>
    request<Comment>(`/comments/${commentId}/resolution`, {
      method: "PATCH",
      ...json({ is_resolved: isResolved }),
    }),
  versions: (entryId: string) =>
    request<Version[]>(`/entries/${entryId}/versions`),
  diff: (entryId: string, fromVersion: number, toVersion: number) =>
    request<Diff>(
      `/entries/${entryId}/diff?from_version=${fromVersion}&to_version=${toVersion}`,
    ),
  updateEntry: (entryId: string, expectedVersion: number, newContent: string) =>
    request<TimelineEntry>(`/entries/${entryId}`, {
      method: "PATCH",
      ...json({ expected_version: expectedVersion, new_content: newContent }),
    }),
  revert: (
    entryId: string,
    targetVersion: number,
    expectedCurrentVersion: number,
  ) =>
    request<TimelineEntry>(`/entries/${entryId}/revert`, {
      method: "POST",
      ...json({
        target_version: targetVersion,
        expected_current_version: expectedCurrentVersion,
      }),
    }),
  reviewHighlight: (highlightId: string, reviewStatus: GlanceItem["status"]) =>
    request(`/highlights/${highlightId}/review`, {
      method: "PATCH",
      ...json({ status: reviewStatus }),
    }),
};
