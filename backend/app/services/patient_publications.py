"""Server-side patient publication workflow and safe portal projection."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.db.base import utcnow
from app.models import (
    Entry,
    EntryVersion,
    PatientPublication,
    PatientPublicationEvidence,
    PatientPublicationSeverity,
    PatientPublicationState,
    PatientPublicationVersion,
    User,
)
from app.models.enums import PublicationEvidenceStatus
from app.schemas.patient_publication import (
    PatientCareOut,
    PatientCareUpdateOut,
    PatientPublicationOut,
    PublicationDosageOut,
    PublicationEvidenceOut,
    PublicationSourceOut,
    PublicationVersionOut,
)
from app.services.entries import record_audit
from app.services.events import append_event
from app.services.publication_evidence import (
    DosageValidation,
    compare_dosage,
    evidence_row,
    sha256_text,
)


WITHDRAWAL_NOTICE = (
    "This care update was withdrawn by the clinic. Contact the clinic if you have questions."
)
CORRECTION_NOTICE = "This care update was corrected by the clinic."


class PublicationError(Exception):
    """A safe, user-facing publication workflow validation failure."""


class PublicationSourceChangedError(PublicationError):
    """The selected immutable source is no longer the entry's current version."""


@dataclass(frozen=True)
class PublicationConflictError(PublicationError):
    publication_id: str
    expected_workflow_version: int
    actual_workflow_version: int


def _value(value: object) -> str:
    return value.value if isinstance(value, Enum) else str(value)


def _source_for_publication(
    db: Session, publication: PatientPublication
) -> tuple[Entry, EntryVersion]:
    entry = db.get(Entry, publication.source_entry_id)
    version = db.get(EntryVersion, publication.source_version_id)
    if entry is None or version is None or version.entry_id != entry.id:
        raise PublicationError("The publication source is unavailable")
    if entry.patient_id != publication.patient_id or entry.clinic_id != publication.clinic_id:
        raise PublicationError("The publication source is outside the publication scope")
    if _value(entry.visibility) != "internal":
        raise PublicationError("Only internal source records can enter this workflow")
    return entry, version


def _source_is_current(entry: Entry, version: EntryVersion) -> bool:
    return entry.current_version == version.version_number


def _publication_version(db: Session, publication: PatientPublication) -> PatientPublicationVersion:
    version = db.scalar(
        select(PatientPublicationVersion).where(
            PatientPublicationVersion.publication_id == publication.id,
            PatientPublicationVersion.version_number == publication.content_version,
        )
    )
    if version is None:
        raise PublicationError("The publication has no current immutable content version")
    return version


def _validation(
    db: Session, publication: PatientPublication
) -> tuple[Entry, EntryVersion, PatientPublicationVersion, DosageValidation]:
    source_entry, source_version = _source_for_publication(db, publication)
    content_version = _publication_version(db, publication)
    validation = compare_dosage(source_version.content, content_version.content)
    return source_entry, source_version, content_version, validation


def _validation_allowed(validation: DosageValidation) -> bool:
    return validation.status is PublicationEvidenceStatus.MATCHED or (
        validation.severity_class is PatientPublicationSeverity.GENERAL
        and validation.status is PublicationEvidenceStatus.MISSING
    )


def _write_audit_event(
    db: Session,
    *,
    publication: PatientPublication,
    actor: User | None,
    actor_role: str,
    action: str,
    request_id: str,
    from_version: int | None = None,
    to_version: int | None = None,
) -> None:
    record_audit(
        db,
        clinic_id=publication.clinic_id,
        patient_id=publication.patient_id,
        actor_user_id=actor.id if actor else None,
        actor_role=actor_role,
        action=action,
        entity_type="patient_publication",
        entity_id=publication.id,
        request_id=request_id,
        from_version=from_version,
        to_version=to_version,
    )
    append_event(
        db,
        clinic_id=publication.clinic_id,
        patient_id=publication.patient_id,
        resource_type="patient_publication",
        resource_id=publication.id,
        event_kind=action,
        actor_user_id=actor.id if actor else None,
        actor_role=actor_role,
    )


def _create_draft(
    db: Session,
    *,
    clinic_id: str,
    patient_id: str,
    source_entry_id: str,
    source_version_id: str,
    content: str,
    actor: User,
    actor_role: str,
    request_id: str,
    correction_of_publication_id: str | None = None,
) -> PatientPublication:
    if not content.strip():
        raise PublicationError("Publication content cannot be empty")
    source_entry = db.get(Entry, source_entry_id)
    source_version = db.get(EntryVersion, source_version_id)
    if source_entry is None or source_version is None:
        raise PublicationError("The publication source is unavailable")
    if source_entry.clinic_id != clinic_id or source_entry.patient_id != patient_id:
        raise PublicationError("The publication source is outside the publication scope")
    if source_version.entry_id != source_entry.id or _value(source_entry.visibility) != "internal":
        raise PublicationError("Only internal source records can enter this workflow")
    validation = compare_dosage(source_version.content, content)
    publication = PatientPublication(
        clinic_id=clinic_id,
        patient_id=patient_id,
        source_entry_id=source_entry.id,
        source_version_id=source_version.id,
        state=PatientPublicationState.DRAFT,
        content_version=1,
        workflow_version=1,
        severity_class=validation.severity_class,
        correction_of_publication_id=correction_of_publication_id,
        created_by_user_id=actor.id,
        created_by_role=actor_role,
    )
    db.add(publication)
    db.flush()
    content_version = PatientPublicationVersion(
        publication_id=publication.id,
        version_number=1,
        content=content,
        content_sha256=sha256_text(content),
        created_by_user_id=actor.id,
        created_by_role=actor_role,
    )
    db.add(content_version)
    db.flush()
    db.add(
        evidence_row(
            publication_id=publication.id,
            publication_version_id=content_version.id,
            source_entry_id=source_entry.id,
            source_version_id=source_version.id,
            validation=validation,
        )
    )
    _write_audit_event(
        db,
        publication=publication,
        actor=actor,
        actor_role=actor_role,
        action="publication_draft_created",
        request_id=request_id,
        to_version=1,
    )
    db.commit()
    db.refresh(publication)
    return publication


def create_publication_draft(
    db: Session,
    *,
    clinic_id: str,
    patient_id: str,
    source_entry_id: str,
    actor: User,
    actor_role: str,
    request_id: str,
    content: str | None = None,
) -> PatientPublication:
    """Create or return the active publication for one source entry idempotently."""

    active_states = {
        PatientPublicationState.DRAFT.value,
        PatientPublicationState.CLINICIAN_APPROVED.value,
        PatientPublicationState.PUBLISHED.value,
        PatientPublicationState.RECALLED.value,
    }
    existing = db.scalar(
        select(PatientPublication)
        .where(
            PatientPublication.clinic_id == clinic_id,
            PatientPublication.patient_id == patient_id,
            PatientPublication.source_entry_id == source_entry_id,
            PatientPublication.state.in_(active_states),
        )
        .order_by(PatientPublication.created_at.desc(), PatientPublication.id.desc())
    )
    if existing is not None:
        return existing
    source_entry = db.get(Entry, source_entry_id)
    if source_entry is None:
        raise PublicationError("The publication source is unavailable")
    source_version = db.scalar(
        select(EntryVersion).where(
            EntryVersion.entry_id == source_entry.id,
            EntryVersion.version_number == source_entry.current_version,
        )
    )
    if source_version is None:
        raise PublicationError("The publication source has no current immutable version")
    return _create_draft(
        db,
        clinic_id=clinic_id,
        patient_id=patient_id,
        source_entry_id=source_entry.id,
        source_version_id=source_version.id,
        content=content or source_version.content,
        actor=actor,
        actor_role=actor_role,
        request_id=request_id,
    )


def _check_workflow_version(
    db: Session, publication: PatientPublication, expected_workflow_version: int
) -> int:
    if publication.workflow_version == expected_workflow_version:
        return expected_workflow_version + 1
    raise PublicationConflictError(
        publication.id, expected_workflow_version, publication.workflow_version
    )


def _cas_update(
    db: Session,
    *,
    publication: PatientPublication,
    expected_workflow_version: int,
    values: dict[str, object],
) -> int:
    next_version = expected_workflow_version + 1
    result = db.execute(
        update(PatientPublication)
        .where(
            PatientPublication.id == publication.id,
            PatientPublication.workflow_version == expected_workflow_version,
        )
        .values(workflow_version=next_version, updated_at=utcnow(), **values)
        .execution_options(synchronize_session=False)
    )
    if getattr(result, "rowcount", 0) != 1:
        db.refresh(publication)
        actual = publication.workflow_version
        raise PublicationConflictError(publication.id, expected_workflow_version, actual)
    return next_version


def edit_publication_draft(
    db: Session,
    *,
    publication: PatientPublication,
    content: str,
    actor: User,
    actor_role: str,
    expected_workflow_version: int,
    request_id: str,
) -> PatientPublication:
    if _value(publication.state) not in {
        PatientPublicationState.DRAFT.value,
        PatientPublicationState.CLINICIAN_APPROVED.value,
    }:
        raise PublicationError("Only a draft or approved publication can be edited")
    source_entry, source_version = _source_for_publication(db, publication)
    if not _source_is_current(source_entry, source_version):
        raise PublicationSourceChangedError("The source changed; review against the latest source")
    next_workflow_version = _check_workflow_version(db, publication, expected_workflow_version)
    next_content_version = publication.content_version + 1
    validation = compare_dosage(source_version.content, content)
    _cas_update(
        db,
        publication=publication,
        expected_workflow_version=expected_workflow_version,
        values={
            "state": PatientPublicationState.DRAFT,
            "content_version": next_content_version,
            "severity_class": validation.severity_class,
            "approved_by_user_id": None,
            "approved_at": None,
            "approved_content_version": None,
        },
    )
    content_version = PatientPublicationVersion(
        publication_id=publication.id,
        version_number=next_content_version,
        content=content,
        content_sha256=sha256_text(content),
        created_by_user_id=actor.id,
        created_by_role=actor_role,
    )
    db.add(content_version)
    db.flush()
    db.add(
        evidence_row(
            publication_id=publication.id,
            publication_version_id=content_version.id,
            source_entry_id=source_entry.id,
            source_version_id=source_version.id,
            validation=validation,
        )
    )
    _write_audit_event(
        db,
        publication=publication,
        actor=actor,
        actor_role=actor_role,
        action="publication_draft_edited",
        request_id=request_id,
        from_version=expected_workflow_version,
        to_version=next_workflow_version,
    )
    db.commit()
    db.refresh(publication)
    return publication


def approve_publication(
    db: Session,
    *,
    publication: PatientPublication,
    actor: User,
    actor_role: str,
    expected_workflow_version: int,
    request_id: str,
) -> PatientPublication:
    _check_workflow_version(db, publication, expected_workflow_version)
    if _value(publication.state) != PatientPublicationState.DRAFT.value:
        raise PublicationError("Only a draft can be approved")
    source_entry, source_version, _, validation = _validation(db, publication)
    if not _source_is_current(source_entry, source_version):
        raise PublicationSourceChangedError("The source changed; approval is blocked")
    if not _validation_allowed(validation):
        raise PublicationError("Publication approval is blocked by dosage evidence")
    next_version = _cas_update(
        db,
        publication=publication,
        expected_workflow_version=expected_workflow_version,
        values={
            "state": PatientPublicationState.CLINICIAN_APPROVED,
            "approved_by_user_id": actor.id,
            "approved_at": utcnow(),
            "approved_content_version": publication.content_version,
        },
    )
    _write_audit_event(
        db,
        publication=publication,
        actor=actor,
        actor_role=actor_role,
        action="publication_clinician_approved",
        request_id=request_id,
        from_version=expected_workflow_version,
        to_version=next_version,
    )
    db.commit()
    db.refresh(publication)
    return publication


def publish_publication(
    db: Session,
    *,
    publication: PatientPublication,
    actor: User,
    actor_role: str,
    expected_workflow_version: int,
    request_id: str,
) -> PatientPublication:
    if _value(publication.state) != PatientPublicationState.CLINICIAN_APPROVED.value:
        raise PublicationError("Only a clinician-approved publication can be published")
    source_entry, source_version, _, validation = _validation(db, publication)
    if not _source_is_current(source_entry, source_version):
        raise PublicationSourceChangedError("The source changed; publication is blocked")
    if publication.approved_content_version != publication.content_version:
        raise PublicationError("The approved content changed; review is required")
    if not _validation_allowed(validation):
        raise PublicationError("Publication is blocked by dosage evidence")
    next_version = _cas_update(
        db,
        publication=publication,
        expected_workflow_version=expected_workflow_version,
        values={
            "state": PatientPublicationState.PUBLISHED,
            "published_by_user_id": actor.id,
            "published_at": utcnow(),
        },
    )
    original = None
    if publication.correction_of_publication_id:
        original = db.get(PatientPublication, publication.correction_of_publication_id)
        if original is None or _value(original.state) not in {
            PatientPublicationState.PUBLISHED.value,
            PatientPublicationState.RECALLED.value,
        }:
            raise PublicationError("The correction source is no longer publishable")
        original_version = original.workflow_version
        _cas_update(
            db,
            publication=original,
            expected_workflow_version=original_version,
            values={
                "state": PatientPublicationState.SUPERSEDED,
                "superseded_by_publication_id": publication.id,
            },
        )
        _write_audit_event(
            db,
            publication=original,
            actor=actor,
            actor_role=actor_role,
            action="publication_superseded",
            request_id=request_id,
            from_version=original_version,
            to_version=original_version + 1,
        )
    _write_audit_event(
        db,
        publication=publication,
        actor=actor,
        actor_role=actor_role,
        action="publication_published",
        request_id=request_id,
        from_version=expected_workflow_version,
        to_version=next_version,
    )
    db.commit()
    db.refresh(publication)
    return publication


def recall_publication(
    db: Session,
    *,
    publication: PatientPublication,
    actor: User,
    actor_role: str,
    expected_workflow_version: int,
    reason_code: str,
    request_id: str,
) -> PatientPublication:
    current_state = _value(publication.state)
    if reason_code == "entered_in_error":
        allowed_states = {
            PatientPublicationState.DRAFT.value,
            PatientPublicationState.CLINICIAN_APPROVED.value,
            PatientPublicationState.PUBLISHED.value,
        }
        next_state = PatientPublicationState.ENTERED_IN_ERROR
    else:
        allowed_states = {PatientPublicationState.PUBLISHED.value}
        next_state = PatientPublicationState.RECALLED
    if current_state not in allowed_states:
        raise PublicationError("This publication cannot be withdrawn in its current state")
    next_version = _cas_update(
        db,
        publication=publication,
        expected_workflow_version=expected_workflow_version,
        values={
            "state": next_state,
            "recalled_by_user_id": actor.id,
            "recalled_at": utcnow(),
            "recall_reason_code": reason_code,
        },
    )
    _write_audit_event(
        db,
        publication=publication,
        actor=actor,
        actor_role=actor_role,
        action="publication_entered_in_error"
        if next_state is PatientPublicationState.ENTERED_IN_ERROR
        else "publication_recalled",
        request_id=request_id,
        from_version=expected_workflow_version,
        to_version=next_version,
    )
    db.commit()
    db.refresh(publication)
    return publication


def create_correction_draft(
    db: Session,
    *,
    publication: PatientPublication,
    actor: User,
    actor_role: str,
    request_id: str,
) -> PatientPublication:
    if _value(publication.state) not in {
        PatientPublicationState.PUBLISHED.value,
        PatientPublicationState.RECALLED.value,
    }:
        raise PublicationError("Only a published or recalled update can be corrected")
    source_entry, source_version = _source_for_publication(db, publication)
    if not _source_is_current(source_entry, source_version):
        raise PublicationSourceChangedError("The source changed; correction is blocked")
    active_states = {
        PatientPublicationState.DRAFT.value,
        PatientPublicationState.CLINICIAN_APPROVED.value,
        PatientPublicationState.PUBLISHED.value,
    }
    existing = db.scalar(
        select(PatientPublication)
        .where(
            PatientPublication.correction_of_publication_id == publication.id,
            PatientPublication.state.in_(active_states),
        )
        .order_by(PatientPublication.created_at.desc(), PatientPublication.id.desc())
    )
    if existing is not None:
        return existing
    original_content = _publication_version(db, publication).content
    return _create_draft(
        db,
        clinic_id=publication.clinic_id,
        patient_id=publication.patient_id,
        source_entry_id=source_entry.id,
        source_version_id=source_version.id,
        content=original_content,
        actor=actor,
        actor_role=actor_role,
        request_id=request_id,
        correction_of_publication_id=publication.id,
    )


def list_publications(db: Session, *, clinic_id: str, patient_id: str) -> list[PatientPublication]:
    return list(
        db.scalars(
            select(PatientPublication)
            .where(
                PatientPublication.clinic_id == clinic_id,
                PatientPublication.patient_id == patient_id,
            )
            .order_by(PatientPublication.created_at.desc(), PatientPublication.id.desc())
        )
    )


def _dosage_out(validation: DosageValidation) -> PublicationDosageOut:
    source = validation.source
    draft = validation.draft
    return PublicationDosageOut(
        status=validation.status,
        severity_class=validation.severity_class,
        source_concept_key=source.concept_key,
        source_value=source.normalized_value,
        source_unit=source.unit,
        source_frequency=source.frequency,
        draft_concept_key=draft.concept_key,
        draft_value=draft.normalized_value,
        draft_unit=draft.unit,
        draft_frequency=draft.frequency,
        source_quote=source.quote,
        source_start_offset=source.start_offset,
        source_end_offset=source.end_offset,
    )


def publication_detail(db: Session, publication: PatientPublication) -> PatientPublicationOut:
    source_entry, source_version, content_version, validation = _validation(db, publication)
    evidence_rows = list(
        db.scalars(
            select(PatientPublicationEvidence)
            .where(PatientPublicationEvidence.publication_id == publication.id)
            .order_by(PatientPublicationEvidence.created_at, PatientPublicationEvidence.id)
        )
    )
    publication_versions = list(
        db.scalars(
            select(PatientPublicationVersion)
            .where(PatientPublicationVersion.publication_id == publication.id)
            .order_by(PatientPublicationVersion.version_number)
        )
    )
    source_observation = validation.source
    return PatientPublicationOut(
        id=publication.id,
        clinic_id=publication.clinic_id,
        patient_id=publication.patient_id,
        source_entry_id=publication.source_entry_id,
        source_version_id=publication.source_version_id,
        state=PatientPublicationState(_value(publication.state)),
        content_version=publication.content_version,
        workflow_version=publication.workflow_version,
        severity_class=PatientPublicationSeverity(_value(publication.severity_class)),
        published_entry_id=publication.published_entry_id,
        correction_of_publication_id=publication.correction_of_publication_id,
        superseded_by_publication_id=publication.superseded_by_publication_id,
        created_by_user_id=publication.created_by_user_id,
        created_by_role=publication.created_by_role,
        approved_by_user_id=publication.approved_by_user_id,
        approved_at=publication.approved_at,
        approved_content_version=publication.approved_content_version,
        published_by_user_id=publication.published_by_user_id,
        published_at=publication.published_at,
        recalled_by_user_id=publication.recalled_by_user_id,
        recalled_at=publication.recalled_at,
        recall_reason_code=publication.recall_reason_code,
        created_at=publication.created_at,
        updated_at=publication.updated_at,
        current_content=content_version.content,
        source=PublicationSourceOut(
            source_entry_id=source_entry.id,
            source_version_id=source_version.id,
            version_number=source_version.version_number,
            current_entry_version=source_entry.current_version,
            entry_type=_value(source_entry.entry_type),
            source_kind=_value(source_entry.source_kind),
            source_reference=source_entry.source_reference,
            occurred_at=source_entry.occurred_at,
            version_content=source_version.content,
            quote=source_observation.quote,
            start_offset=source_observation.start_offset,
            end_offset=source_observation.end_offset,
            quote_sha256=sha256_text(source_observation.quote),
            offset_unit="unicode_codepoint",
            source_is_current_version=_source_is_current(source_entry, source_version),
        ),
        dosage=_dosage_out(validation),
        versions=[PublicationVersionOut.model_validate(row) for row in publication_versions],
        evidence=[PublicationEvidenceOut.model_validate(row) for row in evidence_rows],
    )


def patient_care_projection(db: Session, *, patient_id: str) -> PatientCareOut:
    publications = list(
        db.scalars(
            select(PatientPublication)
            .where(PatientPublication.patient_id == patient_id)
            .order_by(PatientPublication.published_at, PatientPublication.created_at)
        )
    )
    updates: list[PatientCareUpdateOut] = []
    for publication in publications:
        state = _value(publication.state)
        if state == PatientPublicationState.PUBLISHED.value:
            content = _publication_version(db, publication).content
            updates.append(
                PatientCareUpdateOut(
                    kind=("corrected" if publication.correction_of_publication_id else "published"),
                    published_at=publication.published_at,
                    content=content,
                    notice=CORRECTION_NOTICE if publication.correction_of_publication_id else None,
                )
            )
        elif (
            state
            in {
                PatientPublicationState.RECALLED.value,
                PatientPublicationState.ENTERED_IN_ERROR.value,
            }
            and publication.published_at is not None
        ):
            updates.append(
                PatientCareUpdateOut(
                    kind="withdrawn",
                    published_at=publication.recalled_at or publication.published_at,
                    content=None,
                    notice=WITHDRAWAL_NOTICE,
                )
            )
    return PatientCareOut(updates=updates)
