"""Persistent, clinic-scoped circuit state for optional external AI providers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import logging
from typing import Literal

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings
from app.db.base import utcnow
from app.models import AIProviderCircuit
from app.observability.safe_logging import SAFE_ERROR_CODES, safe_event


CircuitState = Literal["closed", "open", "half_open"]
Availability = Literal["available", "degraded", "temporarily_unavailable"]

FIXTURE_PROVIDER_NAME = "fixture-redacted-v1"
COUNTED_FAILURE_CODES = frozenset(
    {"provider_timeout", "provider_unavailable", "provider_rate_limited"}
)
UNAVAILABLE_FAILURE_CODES = frozenset(
    {
        "provider_auth_failed",
        "provider_insufficient_balance",
        "provider_configuration_unknown",
        "provider_configuration_missing_key",
        "provider_configuration_invalid_model",
        "provider_configuration_invalid_timeout",
        "provider_configuration_invalid_total_budget",
        "provider_configuration_invalid_max_attempts",
        "provider_configuration_invalid_max_tokens",
        "provider_configuration_invalid_base_url",
    }
)
_LOGGER = logging.getLogger("nightingale")


@dataclass(frozen=True)
class ProviderPermission:
    allowed: bool
    circuit_state: CircuitState
    retry_after_seconds: float | None
    probe: bool


@dataclass(frozen=True)
class ProviderAvailability:
    circuit_state: CircuitState
    retry_after_seconds: float | None
    last_failure_code: str | None
    consecutive_failures: int
    failure_threshold: int
    observed_at: datetime


@dataclass(frozen=True)
class ProviderStatus:
    provider_name: str
    model: str
    mode: Literal["fixture", "deepseek"]
    configured: bool
    availability: Availability
    circuit_state: CircuitState
    retry_after_seconds: float | None
    last_failure_code: str | None
    consecutive_failures: int
    new_suggestions_available: bool
    existing_records_available: bool
    observed_at: datetime
    limitations: tuple[str, ...]


def is_external_provider(provider_name: str) -> bool:
    return provider_name != FIXTURE_PROVIDER_NAME


def normalize_provider_error(error_code: str) -> str:
    return error_code if error_code in SAFE_ERROR_CODES else "provider_unavailable"


def _aware(value: datetime | None) -> datetime | None:
    if value is None or value.tzinfo is not None:
        return value
    return value.replace(tzinfo=timezone.utc)


def _retry_after(open_until: datetime | None, now: datetime) -> float | None:
    aware_until = _aware(open_until)
    if aware_until is None:
        return None
    return max(0.0, round((aware_until - now).total_seconds(), 3))


def _find_circuit(db: Session, clinic_id: str, provider_name: str) -> AIProviderCircuit | None:
    return db.scalar(
        select(AIProviderCircuit).where(
            AIProviderCircuit.clinic_id == clinic_id,
            AIProviderCircuit.provider_name == provider_name,
        )
    )


def _ensure_circuit(
    db: Session,
    *,
    clinic_id: str,
    provider_name: str,
    app_settings: Settings,
) -> AIProviderCircuit:
    circuit = _find_circuit(db, clinic_id, provider_name)
    if circuit is not None:
        return circuit
    circuit = AIProviderCircuit(
        clinic_id=clinic_id,
        provider_name=provider_name,
        state="closed",
        consecutive_failures=0,
        failure_threshold=app_settings.deepseek_circuit_failure_threshold,
        cooldown_seconds=app_settings.deepseek_circuit_cooldown_seconds,
        version=1,
    )
    db.add(circuit)
    try:
        db.commit()
        db.refresh(circuit)
        return circuit
    except IntegrityError:
        db.rollback()
        existing = _find_circuit(db, clinic_id, provider_name)
        if existing is None:
            raise
        return existing


def acquire_provider_permission(
    db: Session,
    *,
    clinic_id: str,
    provider_name: str,
    app_settings: Settings,
    request_id: str,
) -> ProviderPermission:
    """Allow a call or reserve the sole half-open probe using a database CAS."""

    if not is_external_provider(provider_name):
        return ProviderPermission(True, "closed", None, False)
    circuit = _ensure_circuit(
        db,
        clinic_id=clinic_id,
        provider_name=provider_name,
        app_settings=app_settings,
    )
    now = utcnow()
    for _ in range(3):
        state = circuit.state
        if state == "closed":
            return ProviderPermission(True, "closed", None, False)
        if state == "half_open":
            safe_event(
                _LOGGER,
                "provider_circuit_blocked",
                request_id=request_id,
                clinic_id=clinic_id,
                provider_name=provider_name,
                error_code="provider_circuit_probe_in_flight",
                circuit_state="half_open",
                retry_after_seconds=1,
            )
            return ProviderPermission(False, "half_open", 1.0, False)
        retry_after = _retry_after(circuit.open_until, now)
        if retry_after is not None and retry_after > 0:
            safe_event(
                _LOGGER,
                "provider_circuit_blocked",
                request_id=request_id,
                clinic_id=clinic_id,
                provider_name=provider_name,
                error_code="provider_circuit_open",
                circuit_state="open",
                retry_after_seconds=retry_after,
            )
            return ProviderPermission(False, "open", retry_after, False)
        changed = db.execute(
            update(AIProviderCircuit)
            .where(
                AIProviderCircuit.id == circuit.id,
                AIProviderCircuit.version == circuit.version,
                AIProviderCircuit.state == "open",
            )
            .values(
                state="half_open",
                version=AIProviderCircuit.version + 1,
                updated_at=now,
            )
            .execution_options(synchronize_session=False)
        )
        if getattr(changed, "rowcount", 0) == 1:
            db.commit()
            safe_event(
                _LOGGER,
                "provider_circuit_half_open",
                request_id=request_id,
                clinic_id=clinic_id,
                provider_name=provider_name,
                circuit_state="half_open",
            )
            return ProviderPermission(True, "half_open", None, True)
        db.rollback()
        latest = _find_circuit(db, clinic_id, provider_name)
        if latest is None:
            break
        circuit = latest
    return ProviderPermission(False, "half_open", 1.0, False)


def record_provider_success(
    db: Session,
    *,
    clinic_id: str,
    provider_name: str,
    app_settings: Settings,
    request_id: str,
) -> None:
    """Reset a successful external call and close any half-open probe."""

    if not is_external_provider(provider_name):
        return
    circuit = _ensure_circuit(
        db,
        clinic_id=clinic_id,
        provider_name=provider_name,
        app_settings=app_settings,
    )
    previous_state = circuit.state
    previous_failures = circuit.consecutive_failures
    for _ in range(3):
        now = utcnow()
        changed = db.execute(
            update(AIProviderCircuit)
            .where(
                AIProviderCircuit.id == circuit.id,
                AIProviderCircuit.version == circuit.version,
                AIProviderCircuit.state.in_(["closed", "half_open"]),
            )
            .values(
                state="closed",
                consecutive_failures=0,
                opened_at=None,
                open_until=None,
                last_failure_code=None,
                version=AIProviderCircuit.version + 1,
                updated_at=now,
            )
            .execution_options(synchronize_session=False)
        )
        if getattr(changed, "rowcount", 0) == 1:
            db.commit()
            db.expire(circuit)
            break
        db.rollback()
        latest = _find_circuit(db, clinic_id, provider_name)
        if latest is None:
            raise RuntimeError("Provider circuit disappeared during success update")
        if latest.state == "open":
            return
        circuit = latest
    else:
        raise RuntimeError("Provider circuit success update lost its CAS")
    if previous_state != "closed" or previous_failures:
        safe_event(
            _LOGGER,
            "provider_circuit_closed",
            request_id=request_id,
            clinic_id=clinic_id,
            provider_name=provider_name,
            circuit_state="closed",
        )


def record_provider_failure(
    db: Session,
    *,
    clinic_id: str,
    provider_name: str,
    error_code: str,
    app_settings: Settings,
    request_id: str,
) -> ProviderAvailability:
    """Persist a safe failure observation and open the circuit at its threshold."""

    if not is_external_provider(provider_name):
        return ProviderAvailability("closed", None, None, 0, 0, utcnow())
    normalized = normalize_provider_error(error_code)
    circuit = _ensure_circuit(
        db,
        clinic_id=clinic_id,
        provider_name=provider_name,
        app_settings=app_settings,
    )
    counted = normalized in COUNTED_FAILURE_CODES
    previous_state = circuit.state
    previous_failures = circuit.consecutive_failures
    now = utcnow()
    next_failures = previous_failures + 1 if counted else previous_failures
    should_open = circuit.state == "half_open" or (
        counted and next_failures >= circuit.failure_threshold
    )
    next_state: CircuitState = "open" if should_open else "closed"
    next_open_until = now + timedelta(seconds=circuit.cooldown_seconds) if should_open else None
    for _ in range(3):
        changed = db.execute(
            update(AIProviderCircuit)
            .where(
                AIProviderCircuit.id == circuit.id,
                AIProviderCircuit.version == circuit.version,
            )
            .values(
                state=next_state,
                consecutive_failures=next_failures,
                opened_at=now if should_open else None,
                open_until=next_open_until,
                last_failure_code=normalized,
                version=AIProviderCircuit.version + 1,
                updated_at=now,
            )
            .execution_options(synchronize_session=False)
        )
        if getattr(changed, "rowcount", 0) == 1:
            db.commit()
            db.expire(circuit)
            break
        db.rollback()
        latest = _find_circuit(db, clinic_id, provider_name)
        if latest is None:
            raise RuntimeError("Provider circuit disappeared during failure update")
        circuit = latest
        previous_state = circuit.state
        previous_failures = circuit.consecutive_failures
        now = utcnow()
        next_failures = previous_failures + 1 if counted else previous_failures
        should_open = circuit.state == "half_open" or (
            counted and next_failures >= circuit.failure_threshold
        )
        next_state = "open" if should_open else "closed"
        next_open_until = now + timedelta(seconds=circuit.cooldown_seconds) if should_open else None
    else:
        raise RuntimeError("Provider circuit failure update lost its CAS")
    if next_state == "open" and previous_state != "open":
        safe_event(
            _LOGGER,
            "provider_circuit_opened",
            request_id=request_id,
            clinic_id=clinic_id,
            provider_name=provider_name,
            error_code=normalized,
            circuit_state="open",
            retry_after_seconds=circuit.cooldown_seconds,
        )
    return ProviderAvailability(
        next_state,
        circuit.cooldown_seconds if next_state == "open" else None,
        normalized,
        next_failures,
        circuit.failure_threshold,
        now,
    )


def get_provider_availability(
    db: Session,
    *,
    clinic_id: str,
    provider_name: str,
    app_settings: Settings,
) -> ProviderAvailability:
    """Read circuit state without reserving a probe or writing the database."""

    now = utcnow()
    circuit = _find_circuit(db, clinic_id, provider_name)
    if circuit is None:
        return ProviderAvailability(
            "closed",
            None,
            None,
            0,
            app_settings.deepseek_circuit_failure_threshold,
            now,
        )
    retry_after = _retry_after(circuit.open_until, now)
    state: CircuitState = circuit.state  # type: ignore[assignment]
    if state == "open" and (retry_after is None or retry_after <= 0):
        state = "half_open"
    return ProviderAvailability(
        state,
        retry_after if state == "open" else None,
        circuit.last_failure_code,
        circuit.consecutive_failures,
        circuit.failure_threshold,
        circuit.updated_at,
    )


def provider_status_for_clinic(
    db: Session,
    *,
    clinic_id: str,
    app_settings: Settings,
) -> ProviderStatus:
    """Build a safe status projection without contacting the provider."""

    from app.ai.provider import ProviderError, ProviderInfo, get_provider_info
    from app.ai.deepseek import DEEPSEEK_DEFAULT_MODEL

    selected = (app_settings.llm_provider or "fixture").strip().lower() or "fixture"
    configuration_error: str | None = None
    try:
        info = get_provider_info(app_settings)
    except ProviderError as exc:
        configuration_error = normalize_provider_error(exc.error_code)
        if selected == "deepseek":
            info = ProviderInfo(
                provider_name="deepseek-v4-flash",
                model=app_settings.deepseek_model,
                configured=False,
                mode="deepseek",
            )
        else:
            info = ProviderInfo(
                provider_name="unconfigured-provider",
                model="unavailable",
                configured=False,
                mode="fixture",
            )
    if info.mode == "fixture":
        return ProviderStatus(
            provider_name=info.provider_name,
            model=info.model,
            mode="fixture",
            configured=info.configured,
            availability="available" if info.configured else "temporarily_unavailable",
            circuit_state="closed",
            retry_after_seconds=None,
            last_failure_code=configuration_error,
            consecutive_failures=0,
            new_suggestions_available=info.configured,
            existing_records_available=True,
            observed_at=utcnow(),
            limitations=(
                "Fixture mode is deterministic and does not contact an external provider.",
            ),
        )
    if info.model != DEEPSEEK_DEFAULT_MODEL:
        configuration_error = "provider_configuration_invalid_model"
        info = ProviderInfo(
            provider_name=info.provider_name,
            model=info.model,
            configured=False,
            mode=info.mode,
        )
    availability = get_provider_availability(
        db,
        clinic_id=clinic_id,
        provider_name=info.provider_name,
        app_settings=app_settings,
    )
    last_failure_code = configuration_error or availability.last_failure_code
    if not info.configured or last_failure_code in UNAVAILABLE_FAILURE_CODES:
        status_value: Availability = "temporarily_unavailable"
    elif availability.circuit_state in {"open", "half_open"}:
        status_value = "temporarily_unavailable"
    elif last_failure_code is not None:
        status_value = "degraded"
    else:
        status_value = "available"
    return ProviderStatus(
        provider_name=info.provider_name,
        model=info.model,
        mode="deepseek",
        configured=info.configured,
        availability=status_value,
        circuit_state=availability.circuit_state,
        retry_after_seconds=availability.retry_after_seconds,
        last_failure_code=last_failure_code,
        consecutive_failures=availability.consecutive_failures,
        new_suggestions_available=info.configured and status_value != "temporarily_unavailable",
        existing_records_available=True,
        observed_at=availability.observed_at,
        limitations=(
            "Provider calls are synchronous and there is no durable queue or automatic replay.",
            "Status reflects this clinic and provider circuit only.",
        ),
    )
