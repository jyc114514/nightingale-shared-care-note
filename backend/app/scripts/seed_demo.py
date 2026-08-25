"""Create the idempotent synthetic Clinic A/Clinic B Gate A demo topology."""

import json
from datetime import datetime, timezone

from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import hash_password
from app.db.base import utcnow
from app.db.migration import CURRENT_MIGRATION_HEAD
from app.db.session import SessionLocal, engine
from app.models import (
    ArchivalSummary,
    ArchivalSummarySource,
    Clinic,
    ClinicMembership,
    Comment,
    Entry,
    EntryOwnerRole,
    EntryType,
    EntryVisibility,
    EntryVersion,
    Highlight,
    HighlightActionState,
    HighlightItemKind,
    HighlightStatus,
    Patient,
    PatientGlanceItem,
    PatientUserLink,
    User,
)
from app.services.entries import create_entry_record, record_audit
from app.services.archival import refresh_archival_summaries
from app.services.highlights import create_highlight_record
from app.services.glance import sync_highlight_projection


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
    occurred_at: datetime | None = None,
    source_kind: str | None = None,
    source_reference: str | None = None,
) -> Entry:
    entry = db.scalar(
        select(Entry).where(
            Entry.patient_id == patient.id,
            Entry.entry_type == entry_type.value,
            Entry.created_by_user_id == created_by_user_id,
        )
    )
    if entry is not None:
        current_version = db.scalar(
            select(EntryVersion).where(
                EntryVersion.entry_id == entry.id,
                EntryVersion.version_number == entry.current_version,
            )
        )
        if current_version is None:
            raise RuntimeError("Seed entry has no current version")
        if current_version.content != content:
            next_version = entry.current_version + 1
            entry.current_version = next_version
            entry.updated_at = utcnow()
            db.add(
                EntryVersion(
                    entry_id=entry.id,
                    version_number=next_version,
                    content=content,
                    created_by_user_id=created_by_user_id,
                    created_by_role=created_by_role,
                    base_version=current_version.version_number,
                )
            )
            record_audit(
                db,
                clinic_id=clinic.id,
                patient_id=patient.id,
                actor_user_id=created_by_user_id,
                actor_role=created_by_role,
                action="entry_seed_updated",
                entity_type="entry",
                entity_id=entry.id,
                request_id=request_id,
                from_version=current_version.version_number,
                to_version=next_version,
            )
        entry.occurred_at = occurred_at or entry.occurred_at
        entry.source_kind = source_kind or entry.source_kind
        entry.source_reference = source_reference
        db.commit()
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
        occurred_at=occurred_at,
        source_kind=source_kind,
        source_reference=source_reference,
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


def ensure_reply(
    db: Session,
    *,
    clinic: Clinic,
    patient: Patient,
    entry: Entry,
    author: User,
    parent_comment_id: str,
    body: str,
) -> Comment:
    comment = db.scalar(
        select(Comment).where(
            Comment.entry_id == entry.id,
            Comment.author_user_id == author.id,
            Comment.body == body,
        )
    )
    if comment is not None:
        return comment
    comment = Comment(
        clinic_id=clinic.id,
        patient_id=patient.id,
        entry_id=entry.id,
        parent_comment_id=parent_comment_id,
        author_user_id=author.id,
        body=body,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def ensure_highlight(
    db: Session,
    *,
    entry: Entry,
    quote: str,
    item_kind: HighlightItemKind,
    status: HighlightStatus,
    display_priority: float,
    risk_reason: str,
    action_label: str | None,
    action_state: HighlightActionState,
    created_by_role: str,
    created_by_user_id: str | None,
    request_id: str,
) -> None:
    version = db.scalar(
        select(EntryVersion).where(
            EntryVersion.entry_id == entry.id,
            EntryVersion.version_number == entry.current_version,
        )
    )
    if version is None:
        raise RuntimeError("Seed entry has no current version")
    existing = db.scalar(
        select(Highlight).where(
            Highlight.source_version_id == version.id,
            Highlight.quote == quote,
        )
    )
    if existing is not None:
        existing.status = status
        existing.display_priority = display_priority
        existing.risk_reason = risk_reason
        existing.action_label = action_label
        existing.action_state = action_state
        sync_highlight_projection(db, existing)
        db.commit()
        return
    start_offset = version.content.index(quote)
    create_highlight_record(
        db,
        source_version_id=version.id,
        start_offset=start_offset,
        end_offset=start_offset + len(quote),
        quote=quote,
        item_kind=item_kind,
        status=status,
        display_priority=display_priority,
        risk_level=None,
        risk_reason=risk_reason,
        action_label=action_label,
        action_state=action_state,
        created_by_role=created_by_role,
        created_by_user_id=created_by_user_id,
        reviewed_by_user_id=created_by_user_id if status is not HighlightStatus.SUGGESTED else None,
        reviewed_at=datetime.now(timezone.utc) if status is not HighlightStatus.SUGGESTED else None,
        request_id=request_id,
    )


def require_current_migration() -> None:
    """Refuse to seed a database that was not upgraded through the current Alembic head."""

    if not inspect(engine).has_table("alembic_version"):
        raise SystemExit(
            "Database is not migrated: run `python -m alembic upgrade head` before seeding"
        )
    with engine.connect() as connection:
        revision = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one_or_none()
    if revision != CURRENT_MIGRATION_HEAD:
        raise SystemExit(
            f"Database revision {revision!r} is not current ({CURRENT_MIGRATION_HEAD}); "
            "run `python -m alembic upgrade head` before seeding"
        )


def demo_time(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


def seed_demo() -> dict[str, object]:
    password = settings.demo_seed_password
    if not password:
        raise SystemExit("DEMO_SEED_PASSWORD must be set; no seed data was written")

    require_current_migration()
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
            occurred_at=demo_time("2025-04-15T09:00:00"),
            source_kind="system_event",
            source_reference="synthetic-history-2025-04-15",
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
            occurred_at=demo_time("2025-04-15T09:05:00"),
            source_kind="system_event",
            source_reference="synthetic-instruction-2025-04-15",
        )
        staff_note = ensure_entry(
            db,
            clinic=clinic_a,
            patient=patient_a,
            entry_type=EntryType.STAFF_NOTE,
            owner_role=EntryOwnerRole.STAFF,
            visibility=EntryVisibility.INTERNAL,
            content="Pending renal panel requires coordination.",
            created_by_user_id=staff_a.id,
            created_by_role="staff",
            request_id="seed-staff-note",
            occurred_at=demo_time("2026-08-25T08:00:00"),
            source_kind="manual",
            source_reference="self-manual",
        )
        clinician_section = ensure_entry(
            db,
            clinic=clinic_a,
            patient=patient_a,
            entry_type=EntryType.CLINICIAN_SECTION,
            owner_role=EntryOwnerRole.CLINICIAN,
            visibility=EntryVisibility.INTERNAL,
            content="Clinician-confirmed follow-up plan is recorded.",
            created_by_user_id=clinician_a.id,
            created_by_role="clinician",
            request_id="seed-clinician-section",
            occurred_at=demo_time("2026-08-25T09:00:00"),
            source_kind="manual",
            source_reference="self-manual",
        )
        ai_doctor = ensure_entry(
            db,
            clinic=clinic_a,
            patient=patient_a,
            entry_type=EntryType.AI_DOCTOR_CONSULT_SUMMARY,
            owner_role=EntryOwnerRole.SYSTEM,
            visibility=EntryVisibility.INTERNAL,
            content="Documented symptom after dose change awaits clinician review.",
            created_by_user_id=None,
            created_by_role="system",
            request_id="seed-ai-doctor",
            occurred_at=demo_time("2026-02-06T10:00:00"),
            source_kind="doctor_consult",
            source_reference="synthetic-doctor-consult-2026-02-06",
        )
        ai_nurse = ensure_entry(
            db,
            clinic=clinic_a,
            patient=patient_a,
            entry_type=EntryType.AI_NURSE_CONSULT_SUMMARY,
            owner_role=EntryOwnerRole.SYSTEM,
            visibility=EntryVisibility.INTERNAL,
            content="Unresolved cardiology referral noted in the nurse consult.",
            created_by_user_id=None,
            created_by_role="system",
            request_id="seed-ai-nurse",
            occurred_at=demo_time("2026-08-24T10:00:00"),
            source_kind="nurse_consult",
            source_reference="synthetic-nurse-consult-2026-08-24",
        )
        ai_session = ensure_entry(
            db,
            clinic=clinic_a,
            patient=patient_a,
            entry_type=EntryType.AI_PATIENT_SESSION_SUMMARY,
            owner_role=EntryOwnerRole.SYSTEM,
            visibility=EntryVisibility.INTERNAL,
            content="Open follow-up task remains pending in the patient session.",
            created_by_user_id=None,
            created_by_role="system",
            request_id="seed-ai-session",
            occurred_at=demo_time("2026-08-20T10:00:00"),
            source_kind="patient_ai_session",
            source_reference="synthetic-patient-session-2026-08-20",
        )
        root_comment = ensure_comment(db, clinic_a, patient_a, ai_session, clinician_a)
        ensure_reply(
            db,
            clinic=clinic_a,
            patient=patient_a,
            entry=ai_session,
            author=staff_a,
            parent_comment_id=root_comment.id,
            body="Staff reply: synthetic follow-up is queued for review.",
        )
        ensure_highlight(
            db,
            entry=staff_note,
            quote="Pending renal panel",
            item_kind=HighlightItemKind.ACTION,
            status=HighlightStatus.ACCEPTED,
            display_priority=95,
            risk_reason="Open task in the most recent follow-up",
            action_label="Review task",
            action_state=HighlightActionState.OPEN,
            created_by_role="staff",
            created_by_user_id=staff_a.id,
            request_id="seed-highlight-renal",
        )
        ensure_highlight(
            db,
            entry=ai_nurse,
            quote="Unresolved cardiology referral",
            item_kind=HighlightItemKind.ACTION,
            status=HighlightStatus.SUGGESTED,
            display_priority=90,
            risk_reason="Unresolved referral noted in the nurse consult",
            action_label="Review referral",
            action_state=HighlightActionState.OPEN,
            created_by_role="system",
            created_by_user_id=None,
            request_id="seed-highlight-referral",
        )
        ensure_highlight(
            db,
            entry=ai_doctor,
            quote="Documented symptom after dose change",
            item_kind=HighlightItemKind.INFORMATION,
            status=HighlightStatus.SUGGESTED,
            display_priority=85,
            risk_reason="Explicit symptom mention awaiting clinician review",
            action_label="Review suggestion",
            action_state=HighlightActionState.OPEN,
            created_by_role="system",
            created_by_user_id=None,
            request_id="seed-highlight-symptom",
        )
        ensure_highlight(
            db,
            entry=clinician_section,
            quote="Clinician-confirmed follow-up plan",
            item_kind=HighlightItemKind.INFORMATION,
            status=HighlightStatus.ACCEPTED,
            display_priority=80,
            risk_reason="Clinician-confirmed follow-up plan",
            action_label=None,
            action_state=HighlightActionState.NOT_APPLICABLE,
            created_by_role="clinician",
            created_by_user_id=clinician_a.id,
            request_id="seed-highlight-plan",
        )
        ensure_highlight(
            db,
            entry=ai_session,
            quote="Open follow-up task remains pending",
            item_kind=HighlightItemKind.FLAG,
            status=HighlightStatus.CONFLICT_REVIEW,
            display_priority=75,
            risk_reason="Patient session context needs clinician review",
            action_label="Open review",
            action_state=HighlightActionState.OPEN,
            created_by_role="system",
            created_by_user_id=None,
            request_id="seed-highlight-conflict",
        )
        refresh_archival_summaries(
            db,
            clinic_id=clinic_a.id,
            patient_id=patient_a.id,
            now=demo_time("2026-08-26T12:00:00"),
        )

        counts = {
            "clinics": db.query(Clinic).count(),
            "users": db.query(User).count(),
            "patients": db.query(Patient).count(),
            "entries": db.query(Entry).count(),
            "comments": db.query(Comment).count(),
            "highlights": db.query(Highlight).count(),
            "glance_items": db.query(PatientGlanceItem).count(),
            "archival_summaries": db.query(ArchivalSummary).count(),
            "archival_sources": db.query(ArchivalSummarySource).count(),
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
