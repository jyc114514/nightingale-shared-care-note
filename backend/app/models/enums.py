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
