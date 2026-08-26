"""Focused safety tests for metadata-only SSE framing and reconnect cursors."""

from datetime import datetime, timezone

from app.api.routes.events import _event_line, _parse_last_event_id
from app.models import CollaborationEvent


def test_last_event_id_parser_is_monotonic_and_fail_safe() -> None:
    assert _parse_last_event_id(None) == 0
    assert _parse_last_event_id("") == 0
    assert _parse_last_event_id("12") == 12
    assert _parse_last_event_id("-4") == 0
    assert _parse_last_event_id("not-a-number") == 0


def test_sse_frame_contains_only_metadata() -> None:
    event = CollaborationEvent(
        event_id=42,
        clinic_id="clinic-a",
        patient_id="patient-a",
        resource_type="task",
        resource_id="task-a",
        event_kind="task_updated",
        actor_user_id="user-a",
        actor_role="staff",
        created_at=datetime.now(timezone.utc),
    )
    frame = _event_line(event)
    assert "id: 42" in frame
    assert "event: collaboration" in frame
    assert '"resource_type":"task"' in frame
    assert '"resource_id":"task-a"' in frame
    assert '"event_kind":"task_updated"' in frame
    assert "patient-a" not in frame
    assert "user-a" not in frame
    assert "title" not in frame
    assert "secret" not in frame
