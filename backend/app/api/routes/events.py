"""Cookie-authenticated DB-backed SSE invalidation stream."""

import asyncio
import json
import time
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import SessionLocal, get_db
from app.models import CollaborationEvent, User
from app.services.authorization import get_patient_context


router = APIRouter(tags=["collaboration"])


def _parse_last_event_id(value: str | None) -> int:
    try:
        return max(0, int(value or "0"))
    except ValueError:
        return 0


def _event_line(event: CollaborationEvent) -> str:
    payload = {
        "resource_type": event.resource_type,
        "resource_id": event.resource_id,
        "event_kind": event.event_kind,
    }
    return (
        f"id: {event.event_id}\n"
        "event: collaboration\n"
        f"data: {json.dumps(payload, separators=(',', ':'))}\n\n"
    )


@router.get("/patients/{patient_id}/events")
async def collaboration_events(
    request: Request,
    patient_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
) -> StreamingResponse:
    context = get_patient_context(db, user, patient_id)
    cursor = _parse_last_event_id(last_event_id)
    internal = not context.is_patient

    async def stream() -> AsyncIterator[str]:
        nonlocal cursor
        heartbeat_at = time.monotonic()
        try:
            while True:
                if await request.is_disconnected():
                    break
                with SessionLocal() as poll_db:
                    query = (
                        select(CollaborationEvent)
                        .where(
                            CollaborationEvent.patient_id == patient_id,
                            CollaborationEvent.event_id > cursor,
                        )
                        .order_by(CollaborationEvent.event_id)
                        .limit(50)
                    )
                    if not internal:
                        query = query.where(CollaborationEvent.event_kind.like("patient_%"))
                    events = list(poll_db.scalars(query))
                for event in events:
                    cursor = event.event_id
                    yield _event_line(event)
                    heartbeat_at = time.monotonic()
                if time.monotonic() - heartbeat_at >= 10:
                    yield ": heartbeat\n\n"
                    heartbeat_at = time.monotonic()
                await asyncio.sleep(0.25)
        finally:
            return

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
