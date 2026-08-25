"""Clinic-scoped patient listing and entry reads."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import ClinicMembership, Entry, EntryType, Patient, PatientUserLink, User
from app.schemas.entry import InternalEntryOut, PatientEntryOut
from app.schemas.patient import PatientOut
from app.services.authorization import enum_value, get_patient_context


router = APIRouter(tags=["patients"])


def internal_entry_out(entry: Entry, content: str) -> InternalEntryOut:
    return InternalEntryOut(
        id=entry.id,
        clinic_id=entry.clinic_id,
        patient_id=entry.patient_id,
        entry_type=EntryType(enum_value(entry.entry_type)),
        owner_role=enum_value(entry.owner_role),
        visibility=enum_value(entry.visibility),
        created_by_user_id=entry.created_by_user_id,
        current_version=entry.current_version,
        content=content,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


def patient_entry_out(entry: Entry, content: str) -> PatientEntryOut:
    return PatientEntryOut(
        id=entry.id,
        patient_id=entry.patient_id,
        entry_type=EntryType(enum_value(entry.entry_type)),
        content=content,
        current_version=entry.current_version,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


def _current_content(db: Session, entry: Entry) -> str:
    from app.models import EntryVersion

    version = db.scalar(
        select(EntryVersion).where(
            EntryVersion.entry_id == entry.id,
            EntryVersion.version_number == entry.current_version,
        )
    )
    if version is None:
        raise RuntimeError("Entry has no current immutable version")
    return version.content


@router.get("/patients", response_model=list[PatientOut])
def list_patients(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PatientOut]:
    clinic_ids = list(
        db.scalars(
            select(ClinicMembership.clinic_id)
            .where(ClinicMembership.user_id == user.id)
            .order_by(ClinicMembership.clinic_id)
        )
    )
    if clinic_ids:
        patients = list(
            db.scalars(
                select(Patient)
                .where(Patient.clinic_id.in_(clinic_ids))
                .order_by(Patient.created_at, Patient.id)
            )
        )
    else:
        patients = list(
            db.scalars(
                select(Patient)
                .join(PatientUserLink, PatientUserLink.patient_id == Patient.id)
                .where(PatientUserLink.user_id == user.id)
                .order_by(Patient.created_at, Patient.id)
            )
        )
    return [PatientOut.model_validate(patient) for patient in patients]


@router.get("/patients/{patient_id}", response_model=PatientOut)
def get_patient(
    patient_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PatientOut:
    context = get_patient_context(db, user, patient_id)
    return PatientOut.model_validate(context.patient)


@router.get(
    "/patients/{patient_id}/entries",
    response_model=list[InternalEntryOut | PatientEntryOut],
)
def list_patient_entries(
    patient_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[InternalEntryOut | PatientEntryOut]:
    context = get_patient_context(db, user, patient_id)
    entries = list(
        db.scalars(
            select(Entry)
            .where(Entry.patient_id == patient_id)
            .order_by(Entry.created_at.desc(), Entry.id.desc())
        )
    )
    result: list[InternalEntryOut | PatientEntryOut] = []
    for entry in entries:
        if context.is_patient:
            if (
                enum_value(entry.entry_type)
                not in {
                    EntryType.PATIENT_FACING_SUMMARY.value,
                    EntryType.PATIENT_INSTRUCTION.value,
                }
                or enum_value(entry.visibility) != "patient_facing"
            ):
                continue
            result.append(patient_entry_out(entry, _current_content(db, entry)))
        else:
            result.append(internal_entry_out(entry, _current_content(db, entry)))
    return result
