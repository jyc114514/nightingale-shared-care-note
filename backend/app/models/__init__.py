"""ORM model registry."""

from app.models.audit_log import AuditLog
from app.models.ai_processing_job import AIProcessingJob
from app.models.clinic import Clinic
from app.models.comment import Comment
from app.models.conflict import Conflict
from app.models.enums import (
    ConflictStatus,
    EntryOwnerRole,
    EntryType,
    EntryVisibility,
    HighlightActionState,
    HighlightItemKind,
    HighlightStatus,
    MembershipRole,
    SourceKind,
)
from app.models.entry import Entry
from app.models.entry_version import EntryVersion
from app.models.highlight import Highlight
from app.models.membership import ClinicMembership
from app.models.patient import Patient, PatientUserLink
from app.models.patient_glance_item import PatientGlanceItem
from app.models.user import User

__all__ = [
    "AuditLog",
    "AIProcessingJob",
    "Clinic",
    "ClinicMembership",
    "Comment",
    "Conflict",
    "ConflictStatus",
    "Entry",
    "EntryOwnerRole",
    "EntryType",
    "EntryVersion",
    "EntryVisibility",
    "Highlight",
    "HighlightActionState",
    "HighlightItemKind",
    "HighlightStatus",
    "MembershipRole",
    "Patient",
    "PatientGlanceItem",
    "PatientUserLink",
    "SourceKind",
    "User",
]
