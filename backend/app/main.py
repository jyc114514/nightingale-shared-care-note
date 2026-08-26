"""FastAPI application for the Nightingale Phase 3 local Gate C prototype."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.ai_processing import router as ai_processing_router
from app.api.routes.comments import router as comments_router
from app.api.routes.context import router as context_router
from app.api.routes.conflicts import router as conflicts_router
from app.api.routes.entries import router as entries_router
from app.api.routes.events import router as events_router
from app.api.routes.gate_b import router as gate_b_router
from app.api.routes.patients import router as patients_router
from app.api.routes.tasks import router as tasks_router
from app.config import settings

settings.validate_runtime_security()

app = FastAPI(title="Nightingale", version="0.4.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(ai_processing_router)
app.include_router(patients_router)
app.include_router(entries_router)
app.include_router(events_router)
app.include_router(gate_b_router)
app.include_router(comments_router)
app.include_router(conflicts_router)
app.include_router(context_router)
app.include_router(tasks_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Return a fixed, non-sensitive process health response."""

    return {"status": "ok", "phase": "4-bonus-local"}
