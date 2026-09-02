"""ORM model registry."""

from app.models.audit_log import AuditLog
from app.models.ai_processing_job import AIProcessingJob
from app.models.ai_provider_circuit import AIProviderCircuit
from app.models.archival_summary import ArchivalSummary
from app.models.archival_summary_source import ArchivalSummarySource
from app.models.clinical_assertion import ClinicalAssertion
from app.models.clinical_conflict import ClinicalConflict
from app.models.clinic import Clinic
from app.models.comment import Comment
from app.models.collaboration_event import CollaborationEvent
from app.models.conflict import Conflict
from app.models.highlight_feedback_event import HighlightFeedbackEvent
from app.models.glance_impression_batch import GlanceImpressionBatch
from app.models.glance_impression_item import GlanceImpressionItem
from app.models.importance_profile import ImportanceProfile
from app.models.enums import (
    ConflictStatus,
    AssertionCriticality,
    AssertionDomain,
    AssertionPolarity,
    AssertionStatus,
    AssertionVerificationStatus,
    ClinicalConflictResolution,
    ClinicalConflictStatus,
    ClinicalConflictType,
    EntryOwnerRole,
    EntryType,
    EntryVisibility,
    FeedbackEventType,
    HighlightActionState,
    HighlightItemKind,
    HighlightStatus,
    MembershipRole,
    PatientPublicationSeverity,
    PatientPublicationState,
    PublicationEvidenceStatus,
    PublicationEvidenceType,
    SourceKind,
    TaskStatus,
)
from app.models.entry import Entry
from app.models.entry_version import EntryVersion
from app.models.highlight import Highlight
from app.models.membership import ClinicMembership
from app.models.patient import Patient, PatientUserLink
from app.models.patient_publication import (
    PatientPublication,
    PatientPublicationEvidence,
    PatientPublicationVersion,
)
from app.models.patient_glance_item import PatientGlanceItem
from app.models.mention import Mention
from app.models.task import Task
from app.models.task_conflict import TaskConflict
from app.models.task_glance_item import TaskGlanceItem
from app.models.transcript_segment import TranscriptSegment
from app.models.user import User
from app.models.voice_session import VoiceSession

__all__ = [
    "AuditLog",
    "AIProcessingJob",
    "AIProviderCircuit",
    "ArchivalSummary",
    "ArchivalSummarySource",
    "Clinic",
    "ClinicMembership",
    "ClinicalAssertion",
    "ClinicalConflict",
    "AssertionCriticality",
    "AssertionDomain",
    "AssertionPolarity",
    "AssertionStatus",
    "AssertionVerificationStatus",
    "ClinicalConflictResolution",
    "ClinicalConflictStatus",
    "ClinicalConflictType",
    "Comment",
    "CollaborationEvent",
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
    "GlanceImpressionBatch",
    "GlanceImpressionItem",
    "HighlightActionState",
    "HighlightItemKind",
    "HighlightStatus",
    "ImportanceProfile",
    "MembershipRole",
    "PatientPublication",
    "PatientPublicationEvidence",
    "PatientPublicationSeverity",
    "PatientPublicationState",
    "PatientPublicationVersion",
    "PublicationEvidenceStatus",
    "PublicationEvidenceType",
    "Mention",
    "Patient",
    "PatientGlanceItem",
    "PatientUserLink",
    "SourceKind",
    "Task",
    "TaskConflict",
    "TaskGlanceItem",
    "TaskStatus",
    "TranscriptSegment",
    "User",
    "VoiceSession",
]
