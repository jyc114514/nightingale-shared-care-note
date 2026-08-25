"""Real file-backed SQLite application fixtures for Gate A API tests."""

from collections.abc import AsyncIterator, Generator, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings, get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
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


TEST_PASSWORD = "test-password-only"


@dataclass(frozen=True)
class DemoData:
    clinic_a: Clinic
    clinic_b: Clinic
    patient_user: User
    staff_a: User
    clinician_a: User
    admin_a: User
    staff_b: User
    patient_a: Patient
    patient_b: Patient
    patient_summary: Entry
    patient_instruction: Entry
    staff_note: Entry
    clinician_section: Entry
    ai_summary: Entry
    ai_doctor: Entry
    ai_nurse: Entry


@pytest.fixture
def test_settings(tmp_path: Path) -> Settings:
    db_path = (tmp_path / "gate_a.sqlite").as_posix()
    return Settings(
        app_env="test",
        database_url=f"sqlite:///{db_path}",
        session_secret="test-only-session-secret-with-at-least-32-chars",
        cookie_secure=False,
        session_ttl_minutes=60,
        allowed_origins="http://testserver",
    )


@pytest.fixture
def test_engine(test_settings: Settings) -> Iterator[Engine]:
    engine = create_engine(
        test_settings.database_url,
        connect_args={"check_same_thread": False},
        future=True,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection: Any, connection_record: object) -> None:
        del connection_record
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def db_session(test_engine: Engine) -> Iterator[Session]:
    factory = sessionmaker(
        bind=test_engine, autoflush=False, expire_on_commit=False, class_=Session
    )
    db = factory()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def application(
    test_engine: Engine,
    test_settings: Settings,
) -> Iterator[FastAPI]:
    factory = sessionmaker(
        bind=test_engine, autoflush=False, expire_on_commit=False, class_=Session
    )

    def override_db() -> Generator[Session, None, None]:
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: test_settings
    try:
        yield app
    finally:
        app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(application: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=application)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client


@pytest_asyncio.fixture
async def second_client(application: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    """A second HTTP client whose requests receive independent DB sessions."""

    transport = httpx.ASGITransport(app=application)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client


@pytest.fixture
def demo_data(db_session: Session) -> DemoData:
    db = db_session
    clinic_a = Clinic(name="Test Clinic A")
    clinic_b = Clinic(name="Test Clinic B")
    db.add_all([clinic_a, clinic_b])
    db.flush()

    def user(email: str, display_name: str) -> User:
        return User(
            email=email, display_name=display_name, password_hash=hash_password(TEST_PASSWORD)
        )

    patient_user = user("patient@clinic-a.test", "Synthetic Patient")
    staff_a = user("staff@clinic-a.test", "Synthetic Staff A")
    clinician_a = user("clinician@clinic-a.test", "Synthetic Clinician A")
    admin_a = user("admin@clinic-a.test", "Synthetic Admin A")
    staff_b = user("staff@clinic-b.test", "Synthetic Staff B")
    db.add_all([patient_user, staff_a, clinician_a, admin_a, staff_b])
    db.flush()
    db.add_all(
        [
            ClinicMembership(clinic_id=clinic_a.id, user_id=staff_a.id, role="staff"),
            ClinicMembership(clinic_id=clinic_a.id, user_id=clinician_a.id, role="clinician"),
            ClinicMembership(clinic_id=clinic_a.id, user_id=admin_a.id, role="admin"),
            ClinicMembership(clinic_id=clinic_b.id, user_id=staff_b.id, role="staff"),
        ]
    )
    patient_a = Patient(clinic_id=clinic_a.id, synthetic_display_name="Sarah Tan")
    patient_b = Patient(clinic_id=clinic_b.id, synthetic_display_name="Jordan Lim")
    db.add_all([patient_a, patient_b])
    db.flush()
    db.add(PatientUserLink(user_id=patient_user.id, patient_id=patient_a.id))
    db.commit()

    patient_summary = create_entry_record(
        db,
        clinic_id=clinic_a.id,
        patient_id=patient_a.id,
        entry_type=EntryType.PATIENT_FACING_SUMMARY,
        owner_role=EntryOwnerRole.PATIENT,
        visibility=EntryVisibility.PATIENT_FACING,
        content="Patient-facing summary",
        created_by_user_id=None,
        created_by_role="system",
        request_id="fixture-summary",
    )
    patient_instruction = create_entry_record(
        db,
        clinic_id=clinic_a.id,
        patient_id=patient_a.id,
        entry_type=EntryType.PATIENT_INSTRUCTION,
        owner_role=EntryOwnerRole.PATIENT,
        visibility=EntryVisibility.PATIENT_FACING,
        content="Patient-facing instruction",
        created_by_user_id=None,
        created_by_role="system",
        request_id="fixture-instruction",
    )
    staff_note = create_entry_record(
        db,
        clinic_id=clinic_a.id,
        patient_id=patient_a.id,
        entry_type=EntryType.STAFF_NOTE,
        owner_role=EntryOwnerRole.STAFF,
        visibility=EntryVisibility.INTERNAL,
        content="Original staff note",
        created_by_user_id=staff_a.id,
        created_by_role="staff",
        request_id="fixture-staff",
    )
    clinician_section = create_entry_record(
        db,
        clinic_id=clinic_a.id,
        patient_id=patient_a.id,
        entry_type=EntryType.CLINICIAN_SECTION,
        owner_role=EntryOwnerRole.CLINICIAN,
        visibility=EntryVisibility.INTERNAL,
        content="Original clinician section",
        created_by_user_id=clinician_a.id,
        created_by_role="clinician",
        request_id="fixture-clinician",
    )
    ai_summary = create_entry_record(
        db,
        clinic_id=clinic_a.id,
        patient_id=patient_a.id,
        entry_type=EntryType.AI_PATIENT_SESSION_SUMMARY,
        owner_role=EntryOwnerRole.SYSTEM,
        visibility=EntryVisibility.INTERNAL,
        content="Raw synthetic AI session summary",
        created_by_user_id=None,
        created_by_role="system",
        request_id="fixture-ai",
        source_kind="patient_ai_session",
        source_reference="fixture-patient-session",
    )
    ai_doctor = create_entry_record(
        db,
        clinic_id=clinic_a.id,
        patient_id=patient_a.id,
        entry_type=EntryType.AI_DOCTOR_CONSULT_SUMMARY,
        owner_role=EntryOwnerRole.SYSTEM,
        visibility=EntryVisibility.INTERNAL,
        content="Synthetic doctor consult finding",
        created_by_user_id=None,
        created_by_role="system",
        request_id="fixture-ai-doctor",
        source_kind="doctor_consult",
        source_reference="fixture-doctor-consult",
    )
    ai_nurse = create_entry_record(
        db,
        clinic_id=clinic_a.id,
        patient_id=patient_a.id,
        entry_type=EntryType.AI_NURSE_CONSULT_SUMMARY,
        owner_role=EntryOwnerRole.SYSTEM,
        visibility=EntryVisibility.INTERNAL,
        content="Synthetic nurse consult finding",
        created_by_user_id=None,
        created_by_role="system",
        request_id="fixture-ai-nurse",
        source_kind="nurse_consult",
        source_reference="fixture-nurse-consult",
    )
    db.add(
        Comment(
            clinic_id=clinic_a.id,
            patient_id=patient_a.id,
            entry_id=ai_summary.id,
            author_user_id=clinician_a.id,
            body="Internal synthetic comment",
        )
    )
    db.commit()
    return DemoData(
        clinic_a=clinic_a,
        clinic_b=clinic_b,
        patient_user=patient_user,
        staff_a=staff_a,
        clinician_a=clinician_a,
        admin_a=admin_a,
        staff_b=staff_b,
        patient_a=patient_a,
        patient_b=patient_b,
        patient_summary=patient_summary,
        patient_instruction=patient_instruction,
        staff_note=staff_note,
        clinician_section=clinician_section,
        ai_summary=ai_summary,
        ai_doctor=ai_doctor,
        ai_nurse=ai_nurse,
    )
