"""Real application tests for bounded, clinic-scoped importance adaptation."""

import json

import httpx
import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    EntryOwnerRole,
    EntryType,
    EntryVersion,
    EntryVisibility,
    Highlight,
    HighlightFeedbackEvent,
    HighlightStatus,
    PatientGlanceItem,
)
from app.services.entries import create_entry_record
from app.services.highlights import create_highlight_record
from conftest import DemoData, TEST_PASSWORD


async def login(client: httpx.AsyncClient, email: str) -> None:
    response = await client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert response.status_code == 200, response.text


def make_synthetic_highlight(
    db: Session,
    *,
    entry_id: str,
    created_by_role: str = "system",
    created_by_user_id: str | None = None,
) -> Highlight:
    version = db.scalar(
        select(EntryVersion).where(
            EntryVersion.entry_id == entry_id,
            EntryVersion.version_number == 1,
        )
    )
    assert version is not None
    entry_content = version.content
    return create_highlight_record(
        db,
        source_version_id=version.id,
        start_offset=0,
        end_offset=len(entry_content),
        quote=entry_content,
        item_kind="action",
        status=HighlightStatus.SUGGESTED,
        display_priority=20,
        risk_level="medium",
        risk_reason="Synthetic ranking fixture",
        action_label="Review synthetic follow-up",
        action_state="open",
        created_by_role=created_by_role,
        created_by_user_id=created_by_user_id,
        request_id=f"importance-fixture-{entry_id}",
    )


@pytest.mark.asyncio
async def test_feedback_increases_similar_priority_without_mutating_source_or_cross_clinic_profile(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    similar_entry = create_entry_record(
        db_session,
        clinic_id=demo_data.clinic_a.id,
        patient_id=demo_data.patient_a.id,
        entry_type=EntryType.AI_DOCTOR_CONSULT_SUMMARY,
        owner_role=EntryOwnerRole.SYSTEM,
        visibility=EntryVisibility.INTERNAL,
        content="Synthetic second doctor action",
        created_by_user_id=None,
        created_by_role="system",
        request_id="importance-second-entry",
        source_kind="doctor_consult",
        source_reference="importance-second-source",
    )
    clinic_b_entry = create_entry_record(
        db_session,
        clinic_id=demo_data.clinic_b.id,
        patient_id=demo_data.patient_b.id,
        entry_type=EntryType.AI_DOCTOR_CONSULT_SUMMARY,
        owner_role=EntryOwnerRole.SYSTEM,
        visibility=EntryVisibility.INTERNAL,
        content="Synthetic clinic B action",
        created_by_user_id=None,
        created_by_role="system",
        request_id="importance-clinic-b-entry",
        source_kind="doctor_consult",
        source_reference="importance-clinic-b-source",
    )
    first = make_synthetic_highlight(db_session, entry_id=demo_data.ai_doctor.id)
    second = make_synthetic_highlight(db_session, entry_id=similar_entry.id)
    clinic_b = make_synthetic_highlight(db_session, entry_id=clinic_b_entry.id)
    before_second = db_session.get(PatientGlanceItem, second.id)
    before_clinic_b = db_session.get(PatientGlanceItem, clinic_b.id)
    assert before_second is not None and before_clinic_b is not None
    before_priority = before_second.display_priority
    before_risk = first.risk_level
    before_source_version = first.source_version_id
    assert before_second.feature_signature == before_clinic_b.feature_signature

    await login(client, "clinician@clinic-a.test")
    feedback = await client.post(
        f"/highlights/{first.id}/feedback",
        json={"event_type": "pinned", "idempotency_key": "importance-pin-1"},
    )
    assert feedback.status_code == 200, feedback.text
    payload = feedback.json()
    assert payload["created"] is True
    assert payload["profile"]["positive_count"] == 1
    assert payload["profile"]["negative_count"] == 0
    assert payload["profile"]["bounded_weight"] == 2.0
    assert payload["ranking_explanation"]["adaptive_feedback"] == 2.0

    duplicate = await client.post(
        f"/highlights/{first.id}/feedback",
        json={"event_type": "pinned", "idempotency_key": "importance-pin-1"},
    )
    assert duplicate.status_code == 200, duplicate.text
    assert duplicate.json()["created"] is False
    assert duplicate.json()["profile"]["positive_count"] == 1
    assert db_session.scalar(select(func.count(HighlightFeedbackEvent.id))) == 1

    db_session.expire_all()
    after_second = db_session.get(PatientGlanceItem, second.id)
    after_clinic_b = db_session.get(PatientGlanceItem, clinic_b.id)
    after_first = db_session.get(Highlight, first.id)
    assert after_second is not None and after_clinic_b is not None and after_first is not None
    assert after_second.display_priority > before_priority
    assert after_second.adaptive_feedback_adjustment == 2.0
    assert after_clinic_b.adaptive_feedback_adjustment == 0.0
    assert after_first.risk_level == before_risk
    assert after_first.source_version_id == before_source_version
    assert json.loads(after_second.ranking_explanation)["adaptive_feedback"] == 2.0

    rejected = await client.post(
        f"/highlights/{first.id}/feedback",
        json={"event_type": "rejected", "idempotency_key": "importance-reject-1"},
    )
    assert rejected.status_code == 200, rejected.text
    assert rejected.json()["profile"]["negative_count"] == 1
    db_session.expire_all()
    after_negative = db_session.get(PatientGlanceItem, second.id)
    assert after_negative is not None
    assert after_negative.adaptive_feedback_adjustment == 0.0


@pytest.mark.asyncio
async def test_feedback_authorization_and_bounded_negative_direction(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    highlight = make_synthetic_highlight(db_session, entry_id=demo_data.ai_nurse.id)
    await login(client, "staff@clinic-a.test")
    denied = await client.post(
        f"/highlights/{highlight.id}/feedback",
        json={"event_type": "accepted", "idempotency_key": "staff-accept"},
    )
    assert denied.status_code == 403

    patient_login = await client.post(
        "/auth/login", json={"email": "patient@clinic-a.test", "password": TEST_PASSWORD}
    )
    assert patient_login.status_code == 200
    patient_denied = await client.post(
        f"/highlights/{highlight.id}/feedback",
        json={"event_type": "pinned", "idempotency_key": "patient-pin"},
    )
    assert patient_denied.status_code == 403

    await login(client, "clinician@clinic-a.test")
    for index in range(10):
        response = await client.post(
            f"/highlights/{highlight.id}/feedback",
            json={
                "event_type": "rejected",
                "idempotency_key": f"bounded-reject-{index}",
            },
        )
        assert response.status_code == 200, response.text
    assert response.json()["profile"]["bounded_weight"] == -12.0
    assert response.json()["ranking_explanation"]["adaptive_feedback"] == -12.0
