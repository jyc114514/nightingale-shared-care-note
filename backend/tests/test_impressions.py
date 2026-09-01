"""Real application tests for metadata-only Glance exposure impressions."""

import httpx
import pytest
from sqlalchemy import func, inspect, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.models import (
    EntryOwnerRole,
    EntryType,
    EntryVersion,
    EntryVisibility,
    GlanceImpressionBatch,
    Highlight,
    ImportanceProfile,
    HighlightStatus,
)
from app.services.entries import create_entry_record
from app.services.highlights import create_highlight_record
from conftest import DemoData, TEST_PASSWORD


async def login(client: httpx.AsyncClient, email: str) -> None:
    response = await client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert response.status_code == 200, response.text


def make_candidate(
    db: Session,
    demo_data: DemoData,
    *,
    content: str,
    request_id: str,
    priority: float,
) -> Highlight:
    entry = create_entry_record(
        db,
        clinic_id=demo_data.clinic_a.id,
        patient_id=demo_data.patient_a.id,
        entry_type=EntryType.AI_DOCTOR_CONSULT_SUMMARY,
        owner_role=EntryOwnerRole.SYSTEM,
        visibility=EntryVisibility.INTERNAL,
        content=content,
        created_by_user_id=None,
        created_by_role="system",
        request_id=request_id,
        source_kind="doctor_consult",
        source_reference=f"{request_id}-source",
    )
    version = db.scalar(
        select(EntryVersion).where(
            EntryVersion.entry_id == entry.id,
            EntryVersion.version_number == 1,
        )
    )
    assert version is not None
    return create_highlight_record(
        db,
        source_version_id=version.id,
        start_offset=0,
        end_offset=len(content),
        quote=content,
        item_kind="information",
        status=HighlightStatus.SUGGESTED,
        display_priority=priority,
        risk_level=None,
        risk_reason="Synthetic impression fixture",
        action_label=None,
        action_state="not_applicable",
        created_by_role="system",
        created_by_user_id=None,
        request_id=f"{request_id}-highlight",
    )


@pytest.mark.asyncio
async def test_get_glance_reuses_candidates_without_writing_impression_rows(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    make_candidate(
        db_session,
        demo_data,
        content="Synthetic impression candidate one.",
        request_id="impression-candidate-one",
        priority=80,
    )
    make_candidate(
        db_session,
        demo_data,
        content="Synthetic impression candidate two.",
        request_id="impression-candidate-two",
        priority=70,
    )
    await login(client, "staff@clinic-a.test")
    before = db_session.scalar(select(func.count(GlanceImpressionBatch.id)))
    glance = await client.get(f"/patients/{demo_data.patient_a.id}/glance")
    after = db_session.scalar(select(func.count(GlanceImpressionBatch.id)))
    assert glance.status_code == 200, glance.text
    assert len(glance.json()) == 2
    assert before == after == 0


@pytest.mark.asyncio
async def test_impression_snapshot_is_idempotent_and_summary_is_metadata_only(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    first = make_candidate(
        db_session,
        demo_data,
        content="Synthetic impression candidate one.",
        request_id="impression-idempotent-one",
        priority=80,
    )
    second = make_candidate(
        db_session,
        demo_data,
        content="Synthetic impression candidate two.",
        request_id="impression-idempotent-two",
        priority=70,
    )
    await login(client, "clinician@clinic-a.test")
    glance = await client.get(f"/patients/{demo_data.patient_a.id}/glance")
    assert glance.status_code == 200
    ordered = glance.json()
    assert [item["id"] for item in ordered] == [first.id, second.id]
    payload = {
        "idempotency_key": "impression-snapshot-1",
        "requested_limit": 2,
        "surfaced_items": [
            {"resource_type": "highlight", "resource_id": first.id},
        ],
    }
    created = await client.post(
        f"/patients/{demo_data.patient_a.id}/glance-impressions",
        json=payload,
    )
    assert created.status_code == 200, created.text
    body = created.json()
    assert body["algorithm_version"] == "importance-v2-safety-floor"
    assert body["eligible_count"] == 2
    assert body["stored_candidate_count"] == 2
    assert body["surfaced_count"] == 1
    assert [item["candidate_rank"] for item in body["items"]] == [1, 2]
    assert [item["surfaced"] for item in body["items"]] == [True, False]
    assert set(body["items"][0]) == {
        "id",
        "resource_type",
        "resource_id",
        "feature_signature",
        "candidate_rank",
        "surfaced",
        "display_priority",
        "safety_class",
        "safety_floor",
        "created_at",
    }

    duplicate = await client.post(
        f"/patients/{demo_data.patient_a.id}/glance-impressions",
        json=payload,
    )
    assert duplicate.status_code == 200, duplicate.text
    assert duplicate.json()["id"] == body["id"]
    assert db_session.scalar(select(func.count(GlanceImpressionBatch.id))) == 1

    mismatch = await client.post(
        f"/patients/{demo_data.patient_a.id}/glance-impressions",
        json={
            **payload,
            "surfaced_items": [
                {"resource_type": "highlight", "resource_id": second.id},
            ],
        },
    )
    assert mismatch.status_code == 409

    summary = await client.get(f"/patients/{demo_data.patient_a.id}/glance-impressions/summary")
    assert summary.status_code == 200, summary.text
    summary_body = summary.json()
    assert summary_body["batch_count"] == 1
    assert summary_body["eligible_candidate_count"] == 2
    assert summary_body["candidate_item_count"] == 2
    assert summary_body["surfaced_item_count"] == 1
    assert summary_body["truncated_batch_count"] == 0
    assert summary_body["safety_summaries"] == []
    assert db_session.scalar(select(func.count(ImportanceProfile.id))) == 0


@pytest.mark.asyncio
async def test_impression_validation_security_and_metadata_columns(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
    test_engine: Engine,
) -> None:
    candidate = make_candidate(
        db_session,
        demo_data,
        content="Synthetic impression security candidate.",
        request_id="impression-security",
        priority=80,
    )
    await login(client, "staff@clinic-a.test")
    duplicate = await client.post(
        f"/patients/{demo_data.patient_a.id}/glance-impressions",
        json={
            "idempotency_key": "impression-duplicate",
            "requested_limit": 2,
            "surfaced_items": [
                {"resource_type": "highlight", "resource_id": candidate.id},
                {"resource_type": "highlight", "resource_id": candidate.id},
            ],
        },
    )
    assert duplicate.status_code == 422
    invalid = await client.post(
        f"/patients/{demo_data.patient_a.id}/glance-impressions",
        json={
            "idempotency_key": "impression-invalid-resource",
            "requested_limit": 1,
            "surfaced_items": [
                {"resource_type": "highlight", "resource_id": "missing-highlight"},
            ],
        },
    )
    assert invalid.status_code == 422

    await login(client, "patient@clinic-a.test")
    patient_post = await client.post(
        f"/patients/{demo_data.patient_a.id}/glance-impressions",
        json={
            "idempotency_key": "patient-impression",
            "requested_limit": 1,
            "surfaced_items": [],
        },
    )
    patient_summary = await client.get(
        f"/patients/{demo_data.patient_a.id}/glance-impressions/summary"
    )
    assert patient_post.status_code == 403
    assert patient_summary.status_code == 403

    await login(client, "staff@clinic-b.test")
    foreign = await client.get(f"/patients/{demo_data.patient_a.id}/glance-impressions/summary")
    assert foreign.status_code == 404

    columns = {
        column["name"] for column in inspect(test_engine).get_columns("glance_impression_items")
    }
    assert {"quote", "content", "risk_reason", "patient_name"} - columns == {
        "quote",
        "content",
        "risk_reason",
        "patient_name",
    }


@pytest.mark.asyncio
async def test_impression_snapshot_captures_protected_metadata_without_content(
    client: httpx.AsyncClient,
    demo_data: DemoData,
    db_session: Session,
) -> None:
    source_version = db_session.scalar(
        select(EntryVersion).where(
            EntryVersion.entry_id == demo_data.staff_note.id,
            EntryVersion.version_number == 1,
        )
    )
    assert source_version is not None
    protected = create_highlight_record(
        db_session,
        source_version_id=source_version.id,
        start_offset=0,
        end_offset=len(source_version.content),
        quote=source_version.content,
        item_kind="flag",
        status=HighlightStatus.CONFLICT_REVIEW,
        display_priority=10,
        risk_level=None,
        risk_reason="Protected synthetic safety fixture",
        action_label="Review synthetic conflict",
        action_state="open",
        created_by_role="system",
        created_by_user_id=None,
        request_id="impression-protected",
        clinical_conflict_id="synthetic-conflict-id",
        safety_class="allergy_conflict",
        safety_floor=95.0,
    )
    await login(client, "staff@clinic-a.test")
    response = await client.post(
        f"/patients/{demo_data.patient_a.id}/glance-impressions",
        json={
            "idempotency_key": "impression-protected-1",
            "requested_limit": 1,
            "surfaced_items": [
                {"resource_type": "highlight", "resource_id": protected.id},
            ],
        },
    )
    assert response.status_code == 200, response.text
    item = response.json()["items"][0]
    assert item["safety_class"] == "allergy_conflict"
    assert item["safety_floor"] == 95.0
    assert "quote" not in item
    summary = await client.get(f"/patients/{demo_data.patient_a.id}/glance-impressions/summary")
    assert summary.status_code == 200
    assert summary.json()["safety_summaries"] == [
        {
            "safety_class": "allergy_conflict",
            "candidate_count": 1,
            "surfaced_count": 1,
            "exposure_rate": 1.0,
        }
    ]


def test_candidate_snapshot_truncates_storage_at_five_hundred(
    db_session: Session,
    demo_data: DemoData,
) -> None:
    from app.services.glance_read import MAX_STORED_CANDIDATES, build_glance_candidates

    source_version = db_session.scalar(
        select(EntryVersion).where(
            EntryVersion.entry_id == demo_data.staff_note.id,
            EntryVersion.version_number == 1,
        )
    )
    assert source_version is not None
    for index in range(MAX_STORED_CANDIDATES + 1):
        create_highlight_record(
            db_session,
            source_version_id=source_version.id,
            start_offset=0,
            end_offset=len(source_version.content),
            quote=source_version.content,
            item_kind="information",
            status=HighlightStatus.SUGGESTED,
            display_priority=float(index % 100),
            risk_level=None,
            risk_reason="Synthetic truncation fixture",
            action_label=None,
            action_state="not_applicable",
            created_by_role="system",
            created_by_user_id=None,
            request_id=f"impression-truncation-{index}",
            commit=False,
        )
    db_session.commit()
    snapshot = build_glance_candidates(
        db_session,
        clinic_id=demo_data.clinic_a.id,
        patient_id=demo_data.patient_a.id,
    )
    assert snapshot.eligible_count == MAX_STORED_CANDIDATES + 1
    assert len(snapshot.candidates) == MAX_STORED_CANDIDATES
    assert snapshot.candidate_truncated is True
