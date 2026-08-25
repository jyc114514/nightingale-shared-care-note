"""Server-side clinic and role authorization for every protected API path."""

from dataclasses import dataclass
from enum import Enum

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    ClinicMembership,
    Entry,
    EntryOwnerRole,
    EntryType,
    Patient,
    PatientUserLink,
    User,
)


def enum_value(value: object) -> str:
    """Normalize SQLAlchemy String-backed enum fields for authorization checks."""

    return value.value if isinstance(value, Enum) else str(value)


@dataclass(frozen=True)
class AccessContext:
    """The authenticated actor's scope for one patient."""

    user: User
    patient: Patient
    clinic_id: str
    actor_role: str

    @property
    def is_patient(self) -> bool:
        return self.actor_role == "patient"


def forbidden(detail: str = "This action is not allowed for the current role") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def get_patient_context(db: Session, user: User, patient_id: str) -> AccessContext:
    """Resolve patient scope, returning 404 for unknown or cross-scope records."""

    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    membership = db.scalar(
        select(ClinicMembership).where(
            ClinicMembership.user_id == user.id,
            ClinicMembership.clinic_id == patient.clinic_id,
        )
    )
    if membership is not None:
        return AccessContext(
            user=user,
            patient=patient,
            clinic_id=patient.clinic_id,
            actor_role=enum_value(membership.role),
        )

    link = db.scalar(
        select(PatientUserLink).where(
            PatientUserLink.user_id == user.id,
            PatientUserLink.patient_id == patient.id,
        )
    )
    if link is not None:
        return AccessContext(
            user=user,
            patient=patient,
            clinic_id=patient.clinic_id,
            actor_role="patient",
        )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")


def get_entry_context(db: Session, user: User, entry_id: str) -> tuple[AccessContext, Entry]:
    """Resolve an entry and its patient scope without leaking cross-clinic existence."""

    entry = db.get(Entry, entry_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    context = get_patient_context(db, user, entry.patient_id)
    if entry.clinic_id != context.clinic_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    return context, entry


def require_internal(context: AccessContext) -> None:
    if context.is_patient:
        raise forbidden("Patients cannot access internal records")


def authorize_entry_create(
    context: AccessContext, entry_type: EntryType
) -> tuple[EntryOwnerRole, str]:
    """Derive owner and visibility from the authenticated role, never request fields."""

    if context.actor_role == "staff" and enum_value(entry_type) == EntryType.STAFF_NOTE.value:
        return EntryOwnerRole.STAFF, "internal"
    if (
        context.actor_role == "clinician"
        and enum_value(entry_type) == EntryType.CLINICIAN_SECTION.value
    ):
        return EntryOwnerRole.CLINICIAN, "internal"
    raise forbidden("The current role cannot create this entry type")


def authorize_entry_write(context: AccessContext, entry: Entry) -> None:
    """Permit only the role that owns the editable manual entry type."""

    if context.is_patient:
        raise forbidden("Patients cannot edit entries")
    if context.actor_role == "staff" and (
        enum_value(entry.owner_role) != EntryOwnerRole.STAFF.value
        or enum_value(entry.entry_type) != EntryType.STAFF_NOTE.value
    ):
        raise forbidden("Staff can edit staff notes only")
    if context.actor_role == "clinician" and (
        enum_value(entry.owner_role) != EntryOwnerRole.CLINICIAN.value
        or enum_value(entry.entry_type) != EntryType.CLINICIAN_SECTION.value
    ):
        raise forbidden("Clinicians can edit clinician sections only")
    if context.actor_role == "admin":
        raise forbidden("Admins have read-only Gate A access")
    if context.actor_role not in {"staff", "clinician"}:
        raise forbidden()


def authorize_patient_read(context: AccessContext, entry: Entry) -> None:
    """Limit patient reads to the two explicitly patient-facing entry types."""

    if context.is_patient and (
        enum_value(entry.visibility) != "patient_facing"
        or enum_value(entry.entry_type)
        not in {EntryType.PATIENT_FACING_SUMMARY.value, EntryType.PATIENT_INSTRUCTION.value}
    ):
        raise forbidden("Patients can view patient-facing summaries and instructions only")
