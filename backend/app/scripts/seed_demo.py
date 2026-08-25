"""Create the idempotent synthetic Clinic A/Clinic B Gate A demo topology."""

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import (
    Clinic,
    ClinicMembership,
    Comment,
    Entry,
    EntryOwnerRole,
    EntryType,
    EntryVisibility,
    Patient,
    PatientUserLink,
    User,
)
from app.services.entries import create_entry_record


def get_or_create_clinic(db: Session, name: str) -> Clinic:
    clinic = db.scalar(select(Clinic).where(Clinic.name == name))
    if clinic is not None:
        return clinic
    clinic = Clinic(name=name)
    db.add(clinic)
    db.commit()
    db.refresh(clinic)
    return clinic


def get_or_create_user(db: Session, email: str, display_name: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user is not None:
        return user
    user = User(email=email, display_name=display_name, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def ensure_membership(db: Session, clinic: Clinic, user: User, role: str) -> None:
    membership = db.scalar(
        select(ClinicMembership).where(
            ClinicMembership.clinic_id == clinic.id,
            ClinicMembership.user_id == user.id,
        )
    )
    if membership is None:
        db.add(ClinicMembership(clinic_id=clinic.id, user_id=user.id, role=role))
        db.commit()


def get_or_create_patient(db: Session, clinic: Clinic, display_name: str) -> Patient:
    patient = db.scalar(
        select(Patient).where(
            Patient.clinic_id == clinic.id,
            Patient.synthetic_display_name == display_name,
        )
    )
    if patient is not None:
        return patient
    patient = Patient(clinic_id=clinic.id, synthetic_display_name=display_name)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def ensure_patient_link(db: Session, user: User, patient: Patient) -> None:
    link = db.scalar(
        select(PatientUserLink).where(
            PatientUserLink.user_id == user.id,
            PatientUserLink.patient_id == patient.id,
        )
    )
    if link is None:
        db.add(PatientUserLink(user_id=user.id, patient_id=patient.id))
        db.commit()


def ensure_entry(
    db: Session,
    *,
    clinic: Clinic,
    patient: Patient,
    entry_type: EntryType,
    owner_role: EntryOwnerRole,
    visibility: EntryVisibility,
    content: str,
    created_by_user_id: str | None,
    created_by_role: str,
    request_id: str,
) -> Entry:
    entry = db.scalar(
        select(Entry).where(
            Entry.patient_id == patient.id,
            Entry.entry_type == entry_type.value,
            Entry.created_by_user_id == created_by_user_id,
        )
    )
    if entry is not None:
        return entry
    return create_entry_record(
        db,
        clinic_id=clinic.id,
        patient_id=patient.id,
        entry_type=entry_type,
        owner_role=owner_role,
        visibility=visibility,
        content=content,
        created_by_user_id=created_by_user_id,
        created_by_role=created_by_role,
        request_id=request_id,
    )


def ensure_comment(
    db: Session, clinic: Clinic, patient: Patient, entry: Entry, author: User
) -> Comment:
    comment = db.scalar(
        select(Comment).where(
            Comment.entry_id == entry.id,
            Comment.author_user_id == author.id,
        )
    )
    if comment is not None:
        return comment
    comment = Comment(
        clinic_id=clinic.id,
        patient_id=patient.id,
        entry_id=entry.id,
        author_user_id=author.id,
        body="Internal follow-up: confirm the next appointment window.",
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def seed_demo() -> dict[str, object]:
    password = settings.demo_seed_password
    if not password:
        raise SystemExit("DEMO_SEED_PASSWORD must be set; no seed data was written")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        clinic_a = get_or_create_clinic(db, "Nightingale Demo Clinic A")
        clinic_b = get_or_create_clinic(db, "Nightingale Demo Clinic B")

        patient_user = get_or_create_user(
            db, "sarah.patient@clinic-a.test", "Sarah Patient", password
        )
        staff_a = get_or_create_user(db, "staff.a@clinic-a.test", "Staff A", password)
        clinician_a = get_or_create_user(db, "clinician.a@clinic-a.test", "Clinician A", password)
        admin_a = get_or_create_user(db, "admin.a@clinic-a.test", "Admin A", password)
        staff_b = get_or_create_user(db, "staff.b@clinic-b.test", "Staff B", password)

        ensure_membership(db, clinic_a, staff_a, "staff")
        ensure_membership(db, clinic_a, clinician_a, "clinician")
        ensure_membership(db, clinic_a, admin_a, "admin")
        ensure_membership(db, clinic_b, staff_b, "staff")

        patient_a = get_or_create_patient(db, clinic_a, "Sarah Tan")
        patient_b = get_or_create_patient(db, clinic_b, "Jordan Lim")
        ensure_patient_link(db, patient_user, patient_a)

        summary = ensure_entry(
            db,
            clinic=clinic_a,
            patient=patient_a,
            entry_type=EntryType.PATIENT_FACING_SUMMARY,
            owner_role=EntryOwnerRole.PATIENT,
            visibility=EntryVisibility.PATIENT_FACING,
            content="Your care team recorded a follow-up plan for the next visit.",
            created_by_user_id=None,
            created_by_role="system",
            request_id="seed-summary",
        )
        ensure_entry(
            db,
            clinic=clinic_a,
            patient=patient_a,
            entry_type=EntryType.PATIENT_INSTRUCTION,
            owner_role=EntryOwnerRole.PATIENT,
            visibility=EntryVisibility.PATIENT_FACING,
            content="Bring your medication list to the next appointment.",
            created_by_user_id=None,
            created_by_role="system",
            request_id="seed-instruction",
        )
        ensure_entry(
            db,
            clinic=clinic_a,
            patient=patient_a,
            entry_type=EntryType.STAFF_NOTE,
            owner_role=EntryOwnerRole.STAFF,
            visibility=EntryVisibility.INTERNAL,
            content="Staff note: appointment coordination is pending.",
            created_by_user_id=staff_a.id,
            created_by_role="staff",
            request_id="seed-staff-note",
        )
        ensure_entry(
            db,
            clinic=clinic_a,
            patient=patient_a,
            entry_type=EntryType.CLINICIAN_SECTION,
            owner_role=EntryOwnerRole.CLINICIAN,
            visibility=EntryVisibility.INTERNAL,
            content="Clinician section: review reported symptoms at follow-up.",
            created_by_user_id=clinician_a.id,
            created_by_role="clinician",
            request_id="seed-clinician-section",
        )
        ensure_entry(
            db,
            clinic=clinic_a,
            patient=patient_a,
            entry_type=EntryType.AI_DOCTOR_CONSULT_SUMMARY,
            owner_role=EntryOwnerRole.SYSTEM,
            visibility=EntryVisibility.INTERNAL,
            content="Synthetic AI doctor consult summary; clinician review required.",
            created_by_user_id=None,
            created_by_role="system",
            request_id="seed-ai-doctor",
        )
        ensure_entry(
            db,
            clinic=clinic_a,
            patient=patient_a,
            entry_type=EntryType.AI_NURSE_CONSULT_SUMMARY,
            owner_role=EntryOwnerRole.SYSTEM,
            visibility=EntryVisibility.INTERNAL,
            content="Synthetic AI nurse consult summary; clinician review required.",
            created_by_user_id=None,
            created_by_role="system",
            request_id="seed-ai-nurse",
        )
        ai_session = ensure_entry(
            db,
            clinic=clinic_a,
            patient=patient_a,
            entry_type=EntryType.AI_PATIENT_SESSION_SUMMARY,
            owner_role=EntryOwnerRole.SYSTEM,
            visibility=EntryVisibility.INTERNAL,
            content="Synthetic raw AI patient-session summary; not patient-facing.",
            created_by_user_id=None,
            created_by_role="system",
            request_id="seed-ai-session",
        )
        ensure_comment(db, clinic_a, patient_a, ai_session, clinician_a)

        counts = {
            "clinics": db.query(Clinic).count(),
            "users": db.query(User).count(),
            "patients": db.query(Patient).count(),
            "entries": db.query(Entry).count(),
            "comments": db.query(Comment).count(),
        }
        return {
            "clinic_ids": [clinic_a.id, clinic_b.id],
            "user_ids": [patient_user.id, staff_a.id, clinician_a.id, admin_a.id, staff_b.id],
            "patient_ids": [patient_a.id, patient_b.id],
            "entry_ids": [summary.id, ai_session.id],
            "counts": counts,
        }
    finally:
        db.close()


if __name__ == "__main__":
    print(json.dumps(seed_demo(), sort_keys=True))
