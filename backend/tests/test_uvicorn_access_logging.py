"""Regression tests for the Uvicorn access-log safety boundary."""

from __future__ import annotations

import http.client
import logging
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
from uvicorn.logging import AccessFormatter

from app.observability.safe_logging import SafeLogFilter, configure_safe_logging


ACCESS_TEMPLATE = '%s - "%s %s HTTP/%s" %d'
SENSITIVE_PATH = (
    "/health?person=Sarah%20Tan&id=S1234567D&phone=%2B65%209123%204567"
    "&authorization=Bearer%20token-sentinel"
)


def _access_record(path: str = SENSITIVE_PATH) -> logging.LogRecord:
    logger = logging.getLogger("uvicorn.access")
    return logger.makeRecord(
        logger.name,
        logging.INFO,
        __file__,
        1,
        ACCESS_TEMPLATE,
        ("127.0.0.1:43210", "GET", path, "1.1", 200),
        None,
    )


def _access_formatter() -> AccessFormatter:
    return AccessFormatter('%(client_addr)s - "%(request_line)s" %(status_code)s %(message)s')


def test_access_formatter_preserves_tuple_and_safe_operational_fields() -> None:
    configure_safe_logging(["Sarah Tan"])
    record = _access_record()

    assert isinstance(record.args, tuple)
    assert len(record.args) == 5
    rendered = _access_formatter().format(record)

    assert "GET /health" in rendered
    assert "HTTP/1.1" in rendered
    assert "200 OK" in rendered
    for sensitive in (
        "Sarah Tan",
        "Sarah%20Tan",
        "S1234567D",
        "9123",
        "token-sentinel",
    ):
        assert sensitive not in rendered
    assert "--- Logging error ---" not in rendered


def test_positional_logging_keeps_parameter_shape_after_sanitization() -> None:
    configure_safe_logging([])
    logger = logging.getLogger("nightingale")
    record = logger.makeRecord(
        logger.name,
        logging.INFO,
        __file__,
        1,
        "status=%s duration=%d",
        ("ok", 15),
        None,
    )

    SafeLogFilter().filter(record)

    assert isinstance(record.args, tuple)
    assert record.args == ("ok", 15)
    assert record.getMessage() == "status=ok duration=15"


def test_mapping_logging_keeps_mapping_shape_and_redacts_values() -> None:
    configure_safe_logging(["Sarah Tan"])
    logger = logging.getLogger("nightingale")
    record = logger.makeRecord(
        logger.name,
        logging.INFO,
        __file__,
        1,
        "status=%(status)s patient=%(patient)s",
        {"status": "ok", "patient": "Sarah Tan"},
        None,
    )

    SafeLogFilter().filter(record)

    assert isinstance(record.args, dict)
    assert set(record.args) == {"status", "patient"}
    assert record.args["status"] == "ok"
    assert record.args["patient"] != "Sarah Tan"
    assert "Sarah Tan" not in record.getMessage()


def test_access_sanitization_is_idempotent_and_formatter_safe() -> None:
    configure_safe_logging(["Sarah Tan"])
    record = _access_record()
    sanitizer = SafeLogFilter()

    for _ in range(3):
        assert sanitizer.filter(record) is True
        assert isinstance(record.args, tuple)
        assert len(record.args) == 5

    first = _access_formatter().format(record)
    second = _access_formatter().format(record)
    assert first == second
    assert "Sarah Tan" not in second
    assert "token-sentinel" not in second


def test_access_sanitizer_failure_keeps_formatter_safe_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.observability.safe_logging as safe_logging

    configure_safe_logging([])
    monkeypatch.setattr(
        safe_logging,
        "sanitize_log_text",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("raw sentinel")),
    )

    record = _access_record("/health?token=token-sentinel")
    rendered = _access_formatter().format(record)

    assert isinstance(record.args, tuple)
    assert len(record.args) == 5
    assert "GET /" in rendered
    assert "500 Internal Server Error" in rendered
    assert "raw sentinel" not in rendered


def test_real_uvicorn_subprocess_has_access_lines_without_logging_errors(
    tmp_path: Path,
) -> None:
    static_dir = tmp_path / "static"
    assets_dir = static_dir / "assets"
    assets_dir.mkdir(parents=True)
    (static_dir / "index.html").write_text(
        '<html><body><h1>synthetic</h1><script src="/assets/app.js"></script>'
        '<link rel="stylesheet" href="/assets/app.css"></body></html>',
        encoding="utf-8",
    )
    (assets_dir / "app.js").write_text("console.log('synthetic');", encoding="utf-8")
    (assets_dir / "app.css").write_text("body { color: black; }", encoding="utf-8")

    with socket.socket() as probe_socket:
        probe_socket.bind(("127.0.0.1", 0))
        port = probe_socket.getsockname()[1]

    child_code = """
import os
from pathlib import Path

import uvicorn

from app.main import create_app
from app.observability.safe_logging import configure_safe_logging

configure_safe_logging(["Sarah Tan"])
application = create_app(Path(os.environ["NIGHTINGALE_STATIC_DIR"]))
uvicorn.run(application, host="127.0.0.1", port=int(os.environ["NIGHTINGALE_PORT"]), log_level="info")
"""
    child_env = os.environ.copy()
    child_env.update(
        {
            "APP_ENV": "development",
            "DATABASE_URL": "sqlite:///./round9-uvicorn-smoke.db",
            "DEMO_SEED_ENABLED": "false",
            "NIGHTINGALE_PORT": str(port),
            "NIGHTINGALE_STATIC_DIR": str(static_dir),
            "PYTHONUNBUFFERED": "1",
        }
    )
    child_env.pop("COVERAGE_FILE", None)
    child_env.pop("COVERAGE_PROCESS_START", None)
    backend_dir = Path(__file__).resolve().parents[1]
    process = subprocess.Popen(
        [sys.executable, "-c", child_code],
        cwd=backend_dir,
        env=child_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    def request(path: str) -> int:
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
        try:
            connection.request("GET", path)
            response = connection.getresponse()
            response.read()
            return response.status
        finally:
            connection.close()

    try:
        deadline = time.monotonic() + 8
        while True:
            try:
                if request("/health") == 200:
                    break
            except (ConnectionError, OSError):
                if time.monotonic() >= deadline:
                    raise
            if time.monotonic() >= deadline:
                raise AssertionError("Uvicorn smoke server did not become ready")
            time.sleep(0.05)

        statuses = [
            request(SENSITIVE_PATH),
            request("/"),
            request("/auth/me?token=token-sentinel"),
            request("/patients"),
        ]
    finally:
        process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate(timeout=5)

    combined = f"{stdout}\n{stderr}"
    assert statuses == [200, 200, 401, 401]
    assert '"GET /health' in combined
    assert " 200" in combined
    for failure in ("--- Logging error ---", "Traceback", "ValueError", "Logging error"):
        assert failure not in combined
    for sensitive in ("Sarah Tan", "S1234567D", "9123", "token-sentinel"):
        assert sensitive not in combined
