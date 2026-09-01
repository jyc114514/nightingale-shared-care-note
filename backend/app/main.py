"""FastAPI application and same-origin production static asset serving."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.auth import router as auth_router
from app.api.routes.ai_processing import router as ai_processing_router
from app.api.routes.comments import router as comments_router
from app.api.routes.clinical_conflicts import router as clinical_conflicts_router
from app.api.routes.context import router as context_router
from app.api.routes.conflicts import router as conflicts_router
from app.api.routes.entries import router as entries_router
from app.api.routes.events import router as events_router
from app.api.routes.gate_b import router as gate_b_router
from app.api.routes.impressions import router as impressions_router
from app.api.routes.patients import router as patients_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.voice import router as voice_router
from app.config import settings


def _mount_frontend(application: FastAPI, static_directory: Path) -> None:
    """Serve the built SPA only after all API routes have been registered."""

    static_directory = static_directory.resolve()
    index_path = static_directory / "index.html"
    assets_directory = static_directory / "assets"
    if not index_path.is_file():
        return
    if assets_directory.is_dir():
        application.mount(
            "/assets",
            StaticFiles(directory=str(assets_directory)),
            name="frontend-assets",
        )

    @application.get("/", include_in_schema=False)
    def serve_index() -> FileResponse:
        return FileResponse(index_path)

    @application.get("/{path:path}", include_in_schema=False)
    def serve_spa(path: str) -> FileResponse:
        candidate = (static_directory / path).resolve()
        if candidate.is_file() and candidate.is_relative_to(static_directory):
            return FileResponse(candidate)
        return FileResponse(index_path)


def create_app(static_directory: Path | None = None) -> FastAPI:
    """Build the application, optionally attaching a production SPA directory."""

    settings.validate_runtime_security()
    application = FastAPI(title="Nightingale", version="0.4.0")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    application.include_router(auth_router)
    application.include_router(ai_processing_router)
    application.include_router(patients_router)
    application.include_router(entries_router)
    application.include_router(events_router)
    application.include_router(gate_b_router)
    application.include_router(impressions_router)
    application.include_router(comments_router)
    application.include_router(clinical_conflicts_router)
    application.include_router(conflicts_router)
    application.include_router(context_router)
    application.include_router(tasks_router)
    application.include_router(voice_router)

    @application.get("/health")
    def health() -> dict[str, str]:
        """Return a fixed, non-sensitive process health response."""

        return {"status": "ok", "phase": "4-bonus-local"}

    if static_directory is None:
        static_directory = Path(__file__).resolve().parent / "static"
    _mount_frontend(application, static_directory)
    return application


app = create_app()
