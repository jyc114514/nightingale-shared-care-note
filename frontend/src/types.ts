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
  content_summary: string;
  item_kind: "information" | "action" | "flag";
  status:
    "suggested" | "accepted" | "rejected" | "superseded" | "conflict_review";
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

export type ApiErrorShape = {
  detail?:
    | string
    | { message?: string; conflict_id?: string; actual_version?: number };
};
