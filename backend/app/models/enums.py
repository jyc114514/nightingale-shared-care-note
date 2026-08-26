"""Database-backed role and entry vocabulary."""

from enum import Enum


class MembershipRole(str, Enum):
    STAFF = "staff"
    CLINICIAN = "clinician"
    ADMIN = "admin"


class EntryOwnerRole(str, Enum):
    PATIENT = "patient"
    STAFF = "staff"
    CLINICIAN = "clinician"
    SYSTEM = "system"


class EntryType(str, Enum):
    PATIENT_FACING_SUMMARY = "patient_facing_summary"
    PATIENT_INSTRUCTION = "patient_instruction"
    STAFF_NOTE = "staff_note"
    CLINICIAN_SECTION = "clinician_section"
    AI_DOCTOR_CONSULT_SUMMARY = "ai_doctor_consult_summary"
    AI_NURSE_CONSULT_SUMMARY = "ai_nurse_consult_summary"
    AI_PATIENT_SESSION_SUMMARY = "ai_patient_session_summary"
    SYSTEM_EVENT = "system_event"


class EntryVisibility(str, Enum):
    PATIENT_FACING = "patient_facing"
    INTERNAL = "internal"


class ConflictStatus(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"


class SourceKind(str, Enum):
    MANUAL = "manual"
    DOCTOR_CONSULT = "doctor_consult"
    NURSE_CONSULT = "nurse_consult"
    PATIENT_AI_SESSION = "patient_ai_session"
    SYSTEM_EVENT = "system_event"
    VOICE_PATIENT = "voice_patient"
    VOICE_CLINICAL = "voice_clinical"


class HighlightItemKind(str, Enum):
    INFORMATION = "information"
    ACTION = "action"
    FLAG = "flag"


class HighlightStatus(str, Enum):
    SUGGESTED = "suggested"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    CONFLICT_REVIEW = "conflict_review"


class HighlightActionState(str, Enum):
    OPEN = "open"
    COMPLETED = "completed"
    NOT_APPLICABLE = "not_applicable"


class FeedbackEventType(str, Enum):
    """Closed vocabulary for explainable importance feedback."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PINNED = "pinned"
    UNPINNED = "unpinned"
    MANUALLY_HIGHLIGHTED = "manually_highlighted"
    COMMENTED = "commented"
    RESOLVED_AFTER_ACTION = "resolved_after_action"


class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
