"""Round 7 forward-compatibility checks for legacy feedback writers."""

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from app.models import EntryVersion, Highlight, HighlightFeedbackEvent
from app.services.highlights import create_highlight_record
from app.services.importance import record_feedback_event
from conftest import DemoData


def make_feedback_highlight(
    db: Session,
    demo_data: DemoData,
    *,
    safety_class: str | None = None,
) -> Highlight:
    version = db.scalar(
        select(EntryVersion).where(
            EntryVersion.entry_id == demo_data.ai_doctor.id,
            EntryVersion.version_number == 1,
        )
    )
    assert version is not None
    return create_highlight_record(
        db,
        source_version_id=version.id,
        start_offset=0,
        end_offset=8,
        quote=version.content[:8],
        item_kind="action",
        status="suggested",
        display_priority=20,
        risk_level="medium",
        risk_reason="Synthetic compatibility fixture",
        action_label="Review synthetic fixture",
        action_state="open",
        created_by_role="system",
        created_by_user_id=None,
        request_id=f"round7-compat-highlight-{safety_class or 'ordinary'}",
        safety_class=safety_class,
        safety_floor=95.0 if safety_class else None,
    )


def feedback_values(demo_data: DemoData, highlight_id: str, key: str) -> dict[str, str]:
    return {
        "clinic_id": demo_data.clinic_a.id,
        "patient_id": demo_data.patient_a.id,
        "highlight_id": highlight_id,
        "actor_user_id": demo_data.clinician_a.id,
        "actor_role": "clinician",
        "event_type": "pinned",
        "feature_signature": "round7|compatibility",
        "idempotency_key": key,
    }


def test_legacy_omission_uses_true_default_and_explicit_values_survive(
    db_session: Session,
    demo_data: DemoData,
) -> None:
    highlight = make_feedback_highlight(db_session, demo_data)

    db_session.execute(
        insert(HighlightFeedbackEvent).values(
            **feedback_values(demo_data, highlight.id, "round7-omitted")
        )
    )
    db_session.execute(
        insert(HighlightFeedbackEvent).values(
            **feedback_values(demo_data, highlight.id, "round7-explicit-true"),
            applied_to_profile=True,
        )
    )
    db_session.execute(
        insert(HighlightFeedbackEvent).values(
            **feedback_values(demo_data, highlight.id, "round7-explicit-false"),
            applied_to_profile=False,
        )
    )
    db_session.commit()

    rows = db_session.scalars(
        select(HighlightFeedbackEvent).where(
            HighlightFeedbackEvent.highlight_id == highlight.id,
        )
    ).all()
    values = {row.idempotency_key: row for row in rows}
    assert values["round7-omitted"].applied_to_profile is True
    assert values["round7-explicit-true"].applied_to_profile is True
    assert values["round7-explicit-false"].applied_to_profile is False
    assert all(row.suppression_reason is None for row in rows)


def test_current_service_keeps_ordinary_true_and_protected_false(
    db_session: Session,
    demo_data: DemoData,
) -> None:
    ordinary = make_feedback_highlight(db_session, demo_data)
    protected = make_feedback_highlight(db_session, demo_data, safety_class="allergy_conflict")

    ordinary_result = record_feedback_event(
        db_session,
        highlight=ordinary,
        actor_user_id=demo_data.clinician_a.id,
        actor_role="clinician",
        event_type="pinned",
        idempotency_key="round7-service-ordinary",
        request_id="round7-service-ordinary",
    )
    protected_result = record_feedback_event(
        db_session,
        highlight=protected,
        actor_user_id=demo_data.clinician_a.id,
        actor_role="clinician",
        event_type="pinned",
        idempotency_key="round7-service-protected",
        request_id="round7-service-protected",
    )

    assert ordinary_result.event.applied_to_profile is True
    assert ordinary_result.event.suppression_reason is None
    assert protected_result.event.applied_to_profile is False
    assert protected_result.event.suppression_reason == "protected_safety_class"
