"""Allowlisted, metadata-only application logging with a defensive sanitizer."""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Callable, Iterable
from threading import RLock
from typing import Final
from urllib.parse import parse_qsl, unquote, urlsplit

from app.ai.redaction import PHONE_PATTERN, SG_ID_PATTERN


SAFE_EVENT_CODES: Final = frozenset(
    {
        "ai_job_created",
        "ai_redaction_completed",
        "ai_redaction_failed",
        "ai_provider_call_started",
        "ai_provider_call_completed",
        "ai_provider_failed",
        "ai_provenance_failed",
        "ai_provenance_completed",
        "provider_circuit_opened",
        "provider_circuit_half_open",
        "provider_circuit_closed",
        "provider_circuit_blocked",
        "provider_status_checked",
        "request_internal_error",
    }
)

SAFE_ERROR_CODES: Final = frozenset(
    {
        "empty_input",
        "secondary_detector_failed",
        "sensitive_token_remaining",
        "provider_payload_invalid",
        "provider_payload_not_redacted",
        "provider_configuration_unknown",
        "provider_configuration_missing_key",
        "provider_configuration_invalid_model",
        "provider_configuration_invalid_timeout",
        "provider_configuration_invalid_total_budget",
        "provider_configuration_invalid_max_attempts",
        "provider_configuration_invalid_max_tokens",
        "provider_configuration_invalid_base_url",
        "provider_timeout",
        "provider_unavailable",
        "provider_auth_failed",
        "provider_insufficient_balance",
        "provider_rate_limited",
        "provider_bad_request",
        "provider_output_invalid",
        "provider_output_truncated",
        "provider_empty_output",
        "provider_span_invalid",
        "provenance_creation_failed",
        "provider_circuit_open",
        "provider_circuit_probe_in_flight",
        "internal_error",
        "internal_timeout",
        "internal_validation",
    }
)

_FIELD_LIMITS: Final[dict[str, int]] = {
    "event_code": 64,
    "request_id": 128,
    "clinic_id": 128,
    "patient_id": 128,
    "entity_type": 80,
    "entity_id": 128,
    "provider_name": 80,
    "status": 64,
    "error_code": 100,
    "replacement_categories": 120,
    "input_hash": 128,
    "method": 16,
    "path": 300,
    "exception_code": 80,
    "circuit_state": 24,
}
_BEARER_PATTERN = re.compile(r"(?i)(\b(?:authorization\s*:\s*bearer|bearer)\s+)[^\s,;\\]+")
_API_KEY_PATTERN = re.compile(
    r"(?i)\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"
)
_NAMED_SECRET_PATTERN = re.compile(
    r"(?i)\b(?:api[_-]?key|deepseek[_-]?api[_-]?key|access[_-]?token|session[_-]?token)\s*[:=]\s*[^\s,;]+"
)
_DATABASE_URL_PATTERN = re.compile(r"(?i)\b(?:postgres(?:ql)?|mysql|redis)://[^\s:@/]+:[^\s@/]+@")
_COOKIE_PATTERN = re.compile(
    r"(?i)\b(?:cookie|set-cookie|session(?:id|_token)?|jwt)\s*[:=]\s*[^\s,;]+"
)
_CONTROL_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_ACCESS_LOG_TEMPLATE: Final[str] = '%s - "%s %s HTTP/%s" %d'
_ACCESS_FALLBACK_ARGS: Final[tuple[str, str, str, str, int]] = (
    "-",
    "GET",
    "/",
    "1.1",
    500,
)

_known_names_lock = RLock()
_known_names: tuple[str, ...] = ()
_factory_lock = RLock()
_factory_installed = False
_original_factory: Callable[..., logging.LogRecord] | None = None


def _name_pattern(known_names: Iterable[str]) -> re.Pattern[str] | None:
    names = sorted(
        {name.strip() for name in known_names if isinstance(name, str) and name.strip()},
        key=len,
        reverse=True,
    )
    if not names:
        return None
    return re.compile(r"(?<![\w])(?:" + "|".join(re.escape(name) for name in names) + r")(?![\w])")


def set_known_names(names: Iterable[str]) -> None:
    """Configure synthetic names for the second-layer process log sanitizer."""

    global _known_names
    sanitized = tuple(
        name.strip()[:128] for name in names if isinstance(name, str) and name.strip()
    )
    with _known_names_lock:
        _known_names = sanitized


def _configured_known_names() -> tuple[str, ...]:
    with _known_names_lock:
        return _known_names


def sanitize_log_text(value: str, known_names: Iterable[str] = ()) -> str:
    """Remove common sensitive tokens and log-injection controls from one message."""

    if not isinstance(value, str):
        raise TypeError("log message must be text")
    text = value
    names = tuple(known_names)
    name_detector = _name_pattern(names)
    if name_detector is not None:
        text = name_detector.sub("[REDACTED_NAME]", text)
    text = SG_ID_PATTERN.sub("[REDACTED_ID]", text)
    text = PHONE_PATTERN.sub("[REDACTED_PHONE]", text)
    text = _BEARER_PATTERN.sub(r"\1[REDACTED_TOKEN]", text)
    text = _API_KEY_PATTERN.sub("[REDACTED_KEY]", text)
    text = _NAMED_SECRET_PATTERN.sub("[REDACTED_SECRET]", text)
    text = _DATABASE_URL_PATTERN.sub("[REDACTED_DATABASE_URL]", text)
    text = _COOKIE_PATTERN.sub("[REDACTED_COOKIE]", text)
    text = text.replace("\r", r"\r").replace("\n", r"\n")
    return _CONTROL_PATTERN.sub("?", text)


def _sanitize_log_value(value: object, known_names: Iterable[str]) -> object:
    if isinstance(value, str):
        return sanitize_log_text(value, known_names)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, tuple):
        return tuple(_sanitize_log_value(item, known_names) for item in value)
    if isinstance(value, list):
        return [_sanitize_log_value(item, known_names) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_log_value(item, known_names) for key, item in value.items()}
    return "[REDACTED_VALUE]"


def _sanitize_log_args(
    args: object, known_names: Iterable[str]
) -> tuple[object, ...] | dict[str, object] | None:
    if args is None:
        return None
    if isinstance(args, tuple):
        return tuple(_sanitize_log_value(item, known_names) for item in args)
    if isinstance(args, dict):
        if any(not isinstance(key, str) for key in args):
            raise TypeError("mapping log arguments must use string keys")
        return {key: _sanitize_log_value(value, known_names) for key, value in args.items()}
    return ()


def _sanitize_access_path(value: str, known_names: Iterable[str]) -> str:
    parsed = urlsplit(value)
    decoded_path = unquote(parsed.path or "/")
    safe_path = sanitize_log_text(decoded_path, known_names)
    if not parsed.query:
        return safe_path
    query_keys = parse_qsl(parsed.query, keep_blank_values=True)
    if not query_keys:
        return f"{safe_path}?[REDACTED_QUERY]"
    safe_keys = [sanitize_log_text(key, known_names) for key, _ in query_keys]
    safe_query = "&".join(f"{key}=[REDACTED_QUERY]" for key in safe_keys)
    return f"{safe_path}?{safe_query}"


def _sanitize_access_args(
    args: object, known_names: Iterable[str]
) -> tuple[object, object, object, object, object]:
    if not isinstance(args, tuple) or len(args) != 5:
        raise ValueError("uvicorn access record must have five positional arguments")
    client_addr, method, full_path, http_version, status_code = args
    if not all(isinstance(value, str) for value in (client_addr, method, full_path, http_version)):
        raise TypeError("uvicorn access fields must be strings")
    if isinstance(status_code, bool) or not isinstance(status_code, (int, float)):
        raise TypeError("uvicorn status code must be numeric")
    return (
        sanitize_log_text(client_addr, known_names),
        sanitize_log_text(method, known_names),
        _sanitize_access_path(full_path, known_names),
        sanitize_log_text(http_version, known_names),
        status_code,
    )


def _sanitize_record(record: logging.LogRecord) -> None:
    known_names = _configured_known_names()
    try:
        if record.name == "uvicorn.access":
            record.msg = _ACCESS_LOG_TEMPLATE
            record.args = _sanitize_access_args(record.args, known_names)
        else:
            if isinstance(record.msg, str):
                record.msg = sanitize_log_text(record.msg, known_names)
            else:
                record.msg = "[REDACTED_LOG_MESSAGE]"
            record.args = _sanitize_log_args(record.args, known_names)
        record.exc_info = None
        record.exc_text = None
    except Exception:
        if record.name == "uvicorn.access":
            record.msg = _ACCESS_LOG_TEMPLATE
            record.args = _ACCESS_FALLBACK_ARGS
        else:
            record.msg = "log_sanitization_failed"
            record.args = ()
        record.exc_info = None
        record.exc_text = None


class SafeLogFilter(logging.Filter):
    """Defensive filter for records that bypass the structured event helper."""

    def filter(self, record: logging.LogRecord) -> bool:
        _sanitize_record(record)
        return True


def _record_factory(*args: object, **kwargs: object) -> logging.LogRecord:
    if _original_factory is None:
        raise RuntimeError("safe logging factory is not configured")
    record = _original_factory(*args, **kwargs)
    _sanitize_record(record)
    return record


def configure_safe_logging(known_names: Iterable[str] = ()) -> None:
    """Install the process-wide defensive filter once and update synthetic names."""

    set_known_names(known_names)
    global _factory_installed, _original_factory
    with _factory_lock:
        if not _factory_installed:
            _original_factory = logging.getLogRecordFactory()
            logging.setLogRecordFactory(_record_factory)
            _factory_installed = True
    filter_instance = SafeLogFilter()
    logger_names = ("nightingale", "uvicorn", "uvicorn.access", "uvicorn.error")
    for logger_name in logger_names:
        logger = logging.getLogger(logger_name)
        logger.disabled = False
        if logger_name == "nightingale" and logger.level == logging.NOTSET:
            logger.setLevel(logging.INFO)
        if not any(isinstance(item, SafeLogFilter) for item in logger.filters):
            logger.addFilter(filter_instance)
        for handler in logger.handlers:
            if not any(isinstance(item, SafeLogFilter) for item in handler.filters):
                handler.addFilter(filter_instance)
    root = logging.getLogger()
    for handler in root.handlers:
        if not any(isinstance(item, SafeLogFilter) for item in handler.filters):
            handler.addFilter(filter_instance)


def _bounded_string(field: str, value: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"safe log field {field} must be a string")
    sanitized = sanitize_log_text(value, ())
    limit = _FIELD_LIMITS[field]
    if not sanitized or len(sanitized) > limit:
        raise ValueError(f"safe log field {field} exceeds its bound")
    return sanitized


def _bounded_number(field: str, value: int | float) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"safe log field {field} must be numeric")
    if value < 0:
        raise ValueError(f"safe log field {field} cannot be negative")
    bounds = {
        "duration_ms": 300_000,
        "retry_count": 10,
        "replacement_count": 1000,
        "status_code": 599,
        "retry_after_seconds": 3600,
    }
    if field in bounds and value > bounds[field]:
        raise ValueError(f"safe log field {field} exceeds its bound")
    return value


def safe_event(
    logger: logging.Logger,
    event_code: str,
    *,
    request_id: str,
    clinic_id: str | None = None,
    patient_id: str | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    provider_name: str | None = None,
    status: str | None = None,
    error_code: str | None = None,
    duration_ms: int | float | None = None,
    retry_count: int | None = None,
    replacement_categories: str | None = None,
    replacement_count: int | None = None,
    input_hash: str | None = None,
    method: str | None = None,
    path: str | None = None,
    status_code: int | None = None,
    exception_code: str | None = None,
    retry_after_seconds: int | float | None = None,
    circuit_state: str | None = None,
) -> None:
    """Emit one closed-vocabulary metadata event; no arbitrary payload is accepted."""

    if event_code not in SAFE_EVENT_CODES:
        raise ValueError("unknown safe event code")
    payload: dict[str, str | int | float] = {
        "event_code": _bounded_string("event_code", event_code),
        "request_id": _bounded_string("request_id", request_id),
    }
    string_values = {
        "clinic_id": clinic_id,
        "patient_id": patient_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "provider_name": provider_name,
        "status": status,
        "error_code": error_code,
        "replacement_categories": replacement_categories,
        "input_hash": input_hash,
        "method": method,
        "path": path,
        "exception_code": exception_code,
        "circuit_state": circuit_state,
    }
    for field_name, value in string_values.items():
        if value is not None:
            payload[field_name] = _bounded_string(field_name, value)
    if error_code is not None and error_code not in SAFE_ERROR_CODES:
        raise ValueError("unknown safe error code")
    if replacement_categories is not None:
        categories = {item for item in replacement_categories.split(",") if item}
        if not categories <= {"name", "id", "phone"}:
            raise ValueError("unknown replacement category")
    numeric_values: dict[str, int | float | None] = {
        "duration_ms": duration_ms,
        "retry_count": retry_count,
        "replacement_count": replacement_count,
        "status_code": status_code,
        "retry_after_seconds": retry_after_seconds,
    }
    for numeric_field, numeric_value in numeric_values.items():
        if numeric_value is not None:
            payload[numeric_field] = _bounded_number(numeric_field, numeric_value)
    logger.info(json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
