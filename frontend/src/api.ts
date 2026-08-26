import type {
  AIJob,
  AIProviderInfo,
  ApiErrorShape,
  Comment,
  ContextRefresh,
  PatientContext,
  Conflict,
  Diff,
  FeedbackEventType,
  GlanceItem,
  ImportanceFeedback,
  Me,
  MentionUser,
  Patient,
  ProvenanceSource,
  Task,
  TaskStatus,
  TimelineEntry,
  VoiceProviderInfo,
  VoiceSample,
  VoiceSession,
  Version,
} from "./types";

const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL;
const apiBaseUrl = (
  configuredApiBaseUrl ?? (import.meta.env.DEV ? "http://localhost:8000" : "")
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
  context: (patientId: string) =>
    request<PatientContext>(`/patients/${patientId}/context`),
  refreshContext: (patientId: string) =>
    request<ContextRefresh>(`/patients/${patientId}/context/refresh`, {
      method: "POST",
    }),
  glance: (patientId: string) =>
    request<GlanceItem[]>(`/patients/${patientId}/glance`),
  source: (highlightId: string) =>
    request<ProvenanceSource>(`/highlights/${highlightId}/source`),
  comments: (entryId: string) =>
    request<Comment[]>(`/entries/${entryId}/comments`),
  addComment: (
    entryId: string,
    body: string,
    parentCommentId?: string,
    mentionedUserIds: string[] = [],
  ) =>
    request<Comment>(`/entries/${entryId}/comments`, {
      method: "POST",
      ...json({
        body,
        parent_comment_id: parentCommentId ?? null,
        mentioned_user_ids: mentionedUserIds,
      }),
    }),
  mentionableUsers: (patientId: string) =>
    request<MentionUser[]>(`/patients/${patientId}/mentionable-users`),
  tasks: (patientId: string) => request<Task[]>(`/patients/${patientId}/tasks`),
  createTask: (
    patientId: string,
    payload: {
      title: string;
      assigned_to_user_id: string;
      source_entry_id?: string;
      source_comment_id?: string;
    },
  ) =>
    request<Task>(`/patients/${patientId}/tasks`, {
      method: "POST",
      ...json(payload),
    }),
  updateTask: (
    taskId: string,
    payload: {
      expected_version: number;
      title?: string;
      assigned_to_user_id?: string;
      status?: TaskStatus;
    },
  ) => request<Task>(`/tasks/${taskId}`, { method: "PATCH", ...json(payload) }),
  resolveComment: (commentId: string, isResolved: boolean) =>
    request<Comment>(`/comments/${commentId}/resolution`, {
      method: "PATCH",
      ...json({ is_resolved: isResolved }),
    }),
  versions: (entryId: string) =>
    request<Version[]>(`/entries/${entryId}/versions`),
  conflicts: (entryId: string) =>
    request<Conflict[]>(`/entries/${entryId}/conflicts`),
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
    request<GlanceItem>(`/highlights/${highlightId}/review`, {
      method: "PATCH",
      ...json({ status: reviewStatus }),
    }),
  feedback: (
    highlightId: string,
    eventType: FeedbackEventType,
    idempotencyKey: string,
  ) =>
    request<ImportanceFeedback>(`/highlights/${highlightId}/feedback`, {
      method: "POST",
      ...json({ event_type: eventType, idempotency_key: idempotencyKey }),
    }),
  submitAIProcessing: (
    patientId: string,
    payload: {
      interaction_type: string;
      text: string;
      source_reference: string;
      idempotency_key: string;
    },
  ) =>
    request<AIJob>(`/patients/${patientId}/ai-processing`, {
      method: "POST",
      ...json(payload),
    }),
  aiJob: (jobId: string) => request<AIJob>(`/ai-processing/${jobId}`),
  aiProvider: () => request<AIProviderInfo>("/ai-processing/provider"),
  eventsUrl: (patientId: string) =>
    `${apiBaseUrl}/patients/${patientId}/events`,
  voiceProvider: () => request<VoiceProviderInfo>("/voice/provider"),
  voiceSamples: (patientId: string) =>
    request<VoiceSample[]>(`/patients/${patientId}/voice/samples`),
  voiceAudioUrl: (patientId: string, sampleId: string) =>
    `${apiBaseUrl}/patients/${patientId}/voice/samples/${sampleId}/audio`,
  createVoiceSession: (
    patientId: string,
    payload: { sample_id: string; idempotency_key: string },
  ) =>
    request<VoiceSession>(`/patients/${patientId}/voice/sessions`, {
      method: "POST",
      ...json(payload),
    }),
  voiceSession: (patientId: string, sessionId: string) =>
    request<VoiceSession>(`/patients/${patientId}/voice/sessions/${sessionId}`),
};
