"""ORM model registry."""

from app.models.audit_log import AuditLog
from app.models.ai_processing_job import AIProcessingJob
from app.models.archival_summary import ArchivalSummary
from app.models.archival_summary_source import ArchivalSummarySource
from app.models.clinic import Clinic
from app.models.comment import Comment
from app.models.conflict import Conflict
from app.models.highlight_feedback_event import HighlightFeedbackEvent
from app.models.importance_profile import ImportanceProfile
from app.models.enums import (
    ConflictStatus,
    EntryOwnerRole,
    EntryType,
    EntryVisibility,
    FeedbackEventType,
    HighlightActionState,
    HighlightItemKind,
    HighlightStatus,
    MembershipRole,
    SourceKind,
    TaskStatus,
)
from app.models.entry import Entry
from app.models.entry_version import EntryVersion
from app.models.highlight import Highlight
from app.models.membership import ClinicMembership
from app.models.patient import Patient, PatientUserLink
from app.models.patient_glance_item import PatientGlanceItem
from app.models.mention import Mention
from app.models.task import Task
from app.models.task_conflict import TaskConflict
from app.models.task_glance_item import TaskGlanceItem
from app.models.user import User

__all__ = [
    "AuditLog",
    "AIProcessingJob",
    "ArchivalSummary",
    "ArchivalSummarySource",
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
    "FeedbackEventType",
    "Highlight",
    "HighlightFeedbackEvent",
    "HighlightActionState",
    "HighlightItemKind",
    "HighlightStatus",
    "ImportanceProfile",
    "MembershipRole",
    "Mention",
    "Patient",
    "PatientGlanceItem",
    "PatientUserLink",
    "SourceKind",
    "Task",
    "TaskConflict",
    "TaskGlanceItem",
    "TaskStatus",
    "User",
]
