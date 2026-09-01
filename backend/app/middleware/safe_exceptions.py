"""Generic exception boundary that never logs or returns exception text."""

from __future__ import annotations

import logging
import re
from uuid import uuid4

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.observability.safe_logging import safe_event


_SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_LOGGER = logging.getLogger("nightingale")


def _request_id(request: Request) -> str:
    candidate = request.headers.get("x-request-id", "")
    return candidate if _SAFE_REQUEST_ID.fullmatch(candidate) else str(uuid4())


def _exception_code(error: Exception) -> str:
    name = type(error).__name__
    if name in {"TimeoutError", "ReadTimeout", "ConnectTimeout"}:
        return "internal_timeout"
    if name in {"ValidationError", "RequestValidationError"}:
        return "internal_validation"
    return "internal_error"


class SafeExceptionMiddleware:
    """Catch unexpected HTTP exceptions and emit only safe route metadata."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request = Request(scope, receive)
        request_id = _request_id(request)
        response_started = False

        async def send_guarded(message: Message) -> None:
            nonlocal response_started
            if message.get("type") == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, send_guarded)
        except HTTPException:
            raise
        except Exception as error:
            safe_event(
                _LOGGER,
                "request_internal_error",
                request_id=request_id,
                method=str(scope.get("method", "")),
                path=str(scope.get("path", "")),
                status_code=500,
                exception_code=_exception_code(error),
                error_code="internal_error",
            )
            if response_started:
                raise
            response = JSONResponse(
                {"detail": "Internal server error", "request_id": request_id},
                status_code=500,
            )
            await response(scope, receive, send)
