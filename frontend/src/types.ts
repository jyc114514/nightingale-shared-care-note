export type Role = "patient" | "staff" | "clinician" | "admin";
export type TimelineRole = Role | "system";

export type Me = {
  id: string;
  email: string;
  display_name: string;
  memberships: Array<{
    clinic_id: string;
    clinic_name: string;
    role: Exclude<Role, "patient">;
  }>;
  patient_ids: string[];
};

export type Patient = {
  id: string;
  clinic_id: string;
  synthetic_display_name: string;
  created_at: string;
};

export type TimelineEntry = {
  id: string;
  clinic_id: string | null;
  patient_id: string;
  entry_type: string;
  owner_role: TimelineRole;
  author_role: TimelineRole;
  author_id: string | null;
  created_by_user_id: string | null;
  current_version: number;
  content: string;
  occurred_at: string;
  source_kind: string;
  source_reference: string | null;
  created_at: string;
  updated_at: string;
};

export type GlanceItem = {
  id: string;
  resource_type?: "highlight" | "task";
  task_id?: string | null;
  content_summary: string;
  feature_signature: string;
  item_kind: "information" | "action" | "flag";
  status:
    "suggested" | "accepted" | "rejected" | "superseded" | "conflict_review";
  base_priority: number;
  recency_contribution: number;
  explicit_risk_contribution: number;
  unresolved_action_contribution: number;
  clinician_confirmation_contribution: number;
  adaptive_feedback_adjustment: number;
  ranking_explanation: Record<string, number>;
  display_priority: number;
  risk_level: string | null;
  risk_reason: string;
  action_label: string | null;
  action_state: "open" | "completed" | "not_applicable";
  source_entry_id: string;
  source_version_id: string;
  version_number: number;
  current_entry_version: number;
  source_label: string;
  entry_type: string;
  occurred_at: string;
  quote: string;
  assigned_to_user_id?: string | null;
  assigned_to_display_name?: string | null;
  task_status?: TaskStatus | null;
  task_version?: number | null;
};

export type MentionUser = {
  user_id: string;
  display_name: string;
  role: string;
};

export type Mention = {
  id: string;
  mentioned_user_id: string;
  display_name: string;
  role: string;
  created_at: string;
};

export type TaskStatus = "open" | "in_progress" | "done";

export type Task = {
  id: string;
  clinic_id: string;
  patient_id: string;
  source_entry_id: string | null;
  source_comment_id: string | null;
  title: string;
  created_by_user_id: string;
  assigned_to: MentionUser;
  status: TaskStatus;
  version: number;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
};

export type FeedbackEventType =
  | "accepted"
  | "rejected"
  | "pinned"
  | "unpinned"
  | "manually_highlighted"
  | "commented"
  | "resolved_after_action";

export type ImportanceFeedback = {
  event_id: string;
  event_type: FeedbackEventType;
  created: boolean;
  feature_signature: string;
  profile: {
    clinic_id: string;
    feature_key: string;
    positive_count: number;
    negative_count: number;
    bounded_weight: number;
    updated_at: string;
    version: number;
  };
  ranking_explanation: Record<string, number>;
};

export type ContextEntry = {
  id: string;
  patient_id: string;
  entry_type: string;
  owner_role: string;
  author_role: string;
  current_version: number;
  content: string | null;
  occurred_at: string;
  source_kind: string;
  source_reference: string | null;
  protection_reason: string | null;
  canonical: boolean;
};

export type WarmContextEntry = Omit<
  ContextEntry,
  "content" | "source_reference"
>;

export type ArchivalSummarySource = {
  source_entry_id: string;
  source_version_id: string;
  entry_type: string;
  version_number: number;
  occurred_at: string;
  source_order: number;
};

export type ArchivalSummary = {
  id: string;
  period_start: string;
  period_end: string;
  summary_text: string;
  source_count: number;
  source_manifest_hash: string;
  generated_by: string;
  created_at: string;
  refreshed_at: string;
  policy_version: string;
  sources: ArchivalSummarySource[];
  derived: boolean;
};

export type PatientContext = {
  patient_id: string;
  policy_version: string;
  hot_entries: ContextEntry[];
  warm_entries: WarmContextEntry[];
  archival_summaries: ArchivalSummary[];
};

export type ContextRefresh = {
  patient_id: string;
  policy_version: string;
  archival_summary_count: number;
  archival_source_count: number;
};

export type Highlight = {
  id: string;
  clinic_id: string;
  patient_id: string;
  source_entry_id: string;
  source_version_id: string;
  start_offset: number;
  end_offset: number;
  quote: string;
  quote_sha256: string;
  offset_unit: string;
  item_kind: GlanceItem["item_kind"];
  status: GlanceItem["status"];
  display_priority: number;
  risk_level: string | null;
  risk_reason: string;
  action_label: string | null;
  action_state: GlanceItem["action_state"];
  created_by_role: Role;
  created_by_user_id: string | null;
  reviewed_by_user_id: string | null;
  reviewed_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ProvenanceSource = {
  highlight: Highlight;
  source_entry_id: string;
  source_version_id: string;
  version_number: number;
  current_entry_version: number;
  entry_type: string;
  source_kind: string;
  source_reference: string | null;
  occurred_at: string;
  version_content: string;
  quote: string;
  start_offset: number;
  end_offset: number;
};

export type Comment = {
  id: string;
  entry_id: string;
  parent_comment_id: string | null;
  author_user_id: string;
  body: string;
  is_resolved: boolean;
  resolved_at: string | null;
  resolved_by_user_id: string | null;
  created_at: string;
  updated_at: string;
  mentions?: Mention[];
};

export type Version = {
  id: string;
  entry_id: string;
  version_number: number;
  content: string;
  created_by_user_id: string | null;
  created_by_role: string;
  base_version: number;
  reverted_from_version: number | null;
  created_at: string;
};

export type VoiceSample = {
  sample_id: string;
  label: string;
  scope: "patient" | "clinical";
  interaction_type: string;
  duration_ms: number;
  audio_url: string;
  provider_disclosure: string;
};

export type VoiceProviderInfo = {
  provider_name: string;
  model: string;
  mode: "disabled" | "fixture" | "local_whisper";
  enabled: boolean;
  disclosure: string;
};

export type VoiceSessionStatus =
  | "processing"
  | "completed"
  | "failed_asr"
  | "failed_redaction"
  | "failed_provider"
  | "failed_provenance";

export type TranscriptSegment = {
  id: string;
  segment_index: number;
  start_ms: number;
  end_ms: number;
  text: string;
  confidence: number | null;
};

export type VoiceSession = {
  id: string;
  clinic_id: string;
  patient_id: string;
  actor_role: string;
  interaction_type: string;
  sample_id: string;
  audio_sha256: string;
  audio_duration_ms: number;
  asr_provider: string;
  asr_model: string;
  language: string;
  language_probability: number | null;
  status: VoiceSessionStatus;
  error_code: string | null;
  entry_id: string | null;
  highlight_id: string | null;
  source_segment_id: string | null;
  created_at: string;
  completed_at: string | null;
  segments: TranscriptSegment[];
  patient_safe: boolean;
};

export type Diff = {
  entry_id: string;
  from_version: number;
  to_version: number;
  from_content: string;
  to_content: string;
  changed: boolean;
};

export type Conflict = {
  id: string;
  entry_id: string;
  expected_version: number;
  actual_version: number;
  attempted_content: string;
  status: string;
  submitted_by_user_id: string;
  created_at: string;
};

export type AIJob = {
  id: string;
  clinic_id: string;
  patient_id: string;
  interaction_type: string;
  provider_name: string;
  status: string;
  idempotency_key: string;
  input_hash: string;
  source_reference: string;
  error_code: string | null;
  entry_id: string | null;
  highlight_id: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
};

export type AIProviderInfo = {
  provider_name: string;
  model: string;
  configured: boolean;
  mode: "fixture" | "deepseek";
};

export type ApiErrorShape = {
  detail?:
    | string
    | { message?: string; conflict_id?: string; actual_version?: number };
};
