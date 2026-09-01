"""Independent Alembic and synthetic-seed smoke tests.

These checks deliberately create no tables through SQLAlchemy metadata.  The database
under test is produced by the same Alembic commands used by the local runtime.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect, text


BACKEND_ROOT = Path(__file__).resolve().parents[1]


def run_alembic(database_url: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["DATABASE_URL"] = database_url
    return subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=BACKEND_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def run_seed(database_url: str, password: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["DATABASE_URL"] = database_url
    environment["DEMO_SEED_PASSWORD"] = password
    return subprocess.run(
        [sys.executable, "-m", "app.scripts.seed_demo"],
        cwd=BACKEND_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture
def migrated_database(tmp_path: Path) -> str:
    database_url = f"sqlite:///{(tmp_path / 'migration.sqlite').as_posix()}"
    upgraded = run_alembic(database_url, "upgrade", "head")
    assert upgraded.returncode == 0, upgraded.stderr
    return database_url


def test_alembic_head_matches_orm_shape_without_create_all(migrated_database: str) -> None:
    checked = run_alembic(migrated_database, "check")
    assert checked.returncode == 0, checked.stderr
    assert "No new upgrade operations detected" in checked.stdout

    engine = create_engine(migrated_database, future=True)
    try:
        database_inspector = inspect(engine)
        assert set(database_inspector.get_table_names()) >= {
            "alembic_version",
            "entries",
            "entry_versions",
            "comments",
            "highlights",
            "ai_processing_jobs",
            "patient_glance_items",
            "highlight_feedback_events",
            "importance_profiles",
            "archival_summaries",
            "archival_summary_sources",
            "mentions",
            "tasks",
            "task_conflicts",
            "task_glance_items",
            "collaboration_events",
            "voice_sessions",
            "transcript_segments",
            "clinical_assertions",
            "clinical_conflicts",
            "glance_impression_batches",
            "glance_impression_items",
            "ai_provider_circuits",
            "patient_publications",
            "patient_publication_versions",
            "patient_publication_evidence",
        }
        entry_columns = {column["name"] for column in database_inspector.get_columns("entries")}
        assert {"occurred_at", "source_kind", "source_reference"} <= entry_columns
        comment_columns = {column["name"] for column in database_inspector.get_columns("comments")}
        assert {"parent_comment_id", "resolved_at", "resolved_by_user_id", "updated_at"} <= (
            comment_columns
        )
        highlight_columns = {
            column["name"] for column in database_inspector.get_columns("highlights")
        }
        assert {
            "source_entry_id",
            "source_version_id",
            "start_offset",
            "end_offset",
            "quote_sha256",
            "display_priority",
            "risk_level",
        } <= highlight_columns
        glance_columns = {
            column["name"] for column in database_inspector.get_columns("patient_glance_items")
        }
        assert {
            "feature_signature",
            "base_priority",
            "adaptive_feedback_adjustment",
            "ranking_explanation",
            "clinical_conflict_id",
            "safety_class",
            "safety_floor",
        } <= glance_columns
        feedback_columns = {
            column["name"] for column in database_inspector.get_columns("highlight_feedback_events")
        }
        assert {"applied_to_profile", "suppression_reason"} <= feedback_columns
        assertion_columns = {
            column["name"] for column in database_inspector.get_columns("clinical_assertions")
        }
        assert {
            "source_entry_id",
            "source_version_id",
            "start_offset",
            "end_offset",
            "quote_sha256",
            "verification_status",
            "status",
        } <= assertion_columns
        conflict_columns = {
            column["name"] for column in database_inspector.get_columns("clinical_conflicts")
        }
        assert {
            "positive_assertion_id",
            "negative_assertion_id",
            "version",
            "resolution",
            "status",
        } <= conflict_columns
        impression_batch_columns = {
            column["name"] for column in database_inspector.get_columns("glance_impression_batches")
        }
        assert {
            "actor_user_id",
            "algorithm_version",
            "requested_limit",
            "eligible_count",
            "stored_candidate_count",
            "surfaced_count",
            "candidate_truncated",
        } <= impression_batch_columns
        impression_item_columns = {
            column["name"] for column in database_inspector.get_columns("glance_impression_items")
        }
        assert {
            "resource_type",
            "resource_id",
            "feature_signature",
            "candidate_rank",
            "surfaced",
            "display_priority",
            "safety_class",
            "safety_floor",
        } <= impression_item_columns
        job_columns = {
            column["name"] for column in database_inspector.get_columns("ai_processing_jobs")
        }
        assert "retry_after_seconds" in job_columns
        circuit_columns = {
            column["name"] for column in database_inspector.get_columns("ai_provider_circuits")
        }
        assert {
            "clinic_id",
            "provider_name",
            "state",
            "consecutive_failures",
            "failure_threshold",
            "cooldown_seconds",
            "open_until",
            "last_failure_code",
            "version",
        } <= circuit_columns
        publication_columns = {
            column["name"] for column in database_inspector.get_columns("patient_publications")
        }
        assert {
            "source_entry_id",
            "source_version_id",
            "state",
            "content_version",
            "workflow_version",
            "severity_class",
            "correction_of_publication_id",
            "superseded_by_publication_id",
            "approved_content_version",
        } <= publication_columns
        publication_version_columns = {
            column["name"]
            for column in database_inspector.get_columns("patient_publication_versions")
        }
        assert {"publication_id", "version_number", "content_sha256"} <= (
            publication_version_columns
        )
        publication_evidence_columns = {
            column["name"]
            for column in database_inspector.get_columns("patient_publication_evidence")
        }
        assert {
            "publication_version_id",
            "source_version_id",
            "start_offset",
            "end_offset",
            "quote_sha256",
            "validation_status",
        } <= publication_evidence_columns
        email_indexes = {
            index["name"]: index["unique"] for index in database_inspector.get_indexes("users")
        }
        assert email_indexes.get("ix_users_email") == 1
        patient_link_indexes = {
            index["name"]: index["column_names"]
            for index in database_inspector.get_indexes("patient_user_links")
        }
        assert "ix_patient_user_links_patient_id" not in patient_link_indexes
        with engine.connect() as connection:
            assert (
                connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
                == "0014_patient_publications"
            )
    finally:
        engine.dispose()


def test_migration_downgrade_and_reupgrade_are_reversible(migrated_database: str) -> None:
    downgraded = run_alembic(migrated_database, "downgrade", "0001_gate_a")
    assert downgraded.returncode == 0, downgraded.stderr
    upgraded = run_alembic(migrated_database, "upgrade", "head")
    assert upgraded.returncode == 0, upgraded.stderr
    checked = run_alembic(migrated_database, "check")
    assert checked.returncode == 0, checked.stderr


def test_legacy_gate_a_indexes_are_repaired_without_data_loss(tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'legacy.sqlite').as_posix()}"
    upgraded_to_legacy = run_alembic(database_url, "upgrade", "0001_gate_a")
    assert upgraded_to_legacy.returncode == 0, upgraded_to_legacy.stderr

    engine = create_engine(database_url, future=True)
    try:
        with engine.begin() as connection:
            connection.execute(text("DROP INDEX IF EXISTS ix_users_email"))
            connection.execute(text("CREATE INDEX ix_users_email ON users (email)"))
            connection.execute(
                text(
                    "CREATE INDEX ix_patient_user_links_patient_id "
                    "ON patient_user_links (patient_id)"
                )
            )
    finally:
        engine.dispose()

    stamped = run_alembic(database_url, "stamp", "0001_gate_a")
    assert stamped.returncode == 0, stamped.stderr
    repaired = run_alembic(database_url, "upgrade", "head")
    assert repaired.returncode == 0, repaired.stderr
    checked = run_alembic(database_url, "check")
    assert checked.returncode == 0, checked.stderr

    engine = create_engine(database_url, future=True)
    try:
        database_inspector = inspect(engine)
        email_indexes = {
            index["name"]: index["unique"] for index in database_inspector.get_indexes("users")
        }
        patient_link_indexes = {
            index["name"] for index in database_inspector.get_indexes("patient_user_links")
        }
        assert email_indexes["ix_users_email"] == 1
        assert "ix_patient_user_links_patient_id" not in patient_link_indexes
        with engine.connect() as connection:
            assert (
                connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
                == "0014_patient_publications"
            )
    finally:
        engine.dispose()


def test_seed_requires_migrations_and_is_idempotent(tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'seed.sqlite').as_posix()}"
    before_migration = run_seed(database_url, "test-seed-password")
    assert before_migration.returncode != 0
    assert "not migrated" in before_migration.stderr

    upgraded = run_alembic(database_url, "upgrade", "head")
    assert upgraded.returncode == 0, upgraded.stderr
    first = run_seed(database_url, "test-seed-password")
    second = run_seed(database_url, "test-seed-password")
    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    first_result = json.loads(first.stdout)
    second_result = json.loads(second.stdout)
    assert first_result["counts"] == second_result["counts"]
    assert first_result["counts"]["highlights"] >= 5
    assert first_result["counts"]["glance_items"] == first_result["counts"]["highlights"]

    engine = create_engine(database_url, future=True)
    try:
        with engine.connect() as connection:
            ai_rows = connection.execute(
                text(
                    "SELECT entry_type, occurred_at, source_reference FROM entries "
                    "WHERE entry_type LIKE 'ai_%'"
                )
            ).mappings()
            ai_by_reference = {row["source_reference"]: row for row in ai_rows}
            allergy_rows = list(
                connection.execute(
                    text(
                        "SELECT entry_type, source_reference FROM entries "
                        "WHERE source_reference IN "
                        "('synthetic-allergy-nurse-note', "
                        "'synthetic-allergy-patient-session')"
                    )
                ).mappings()
            )
            assertion_count = connection.execute(
                text("SELECT COUNT(*) FROM clinical_assertions")
            ).scalar_one()
            clinical_conflict_count = connection.execute(
                text("SELECT COUNT(*) FROM clinical_conflicts")
            ).scalar_one()
            publication_rows = list(
                connection.execute(
                    text(
                        "SELECT state, severity_class FROM patient_publications "
                        "WHERE source_entry_id IN (SELECT id FROM entries "
                        "WHERE source_reference = 'synthetic-medication-plan')"
                    )
                ).mappings()
            )
            publication_evidence_status = connection.execute(
                text(
                    "SELECT validation_status FROM patient_publication_evidence "
                    "WHERE publication_id IN (SELECT id FROM patient_publications "
                    "WHERE source_entry_id IN (SELECT id FROM entries "
                    "WHERE source_reference = 'synthetic-medication-plan'))"
                )
            ).scalar_one()
        assert ai_by_reference["synthetic-doctor-consult-2026-02-06"]["occurred_at"].startswith(
            "2026-02-06"
        )
        assert ai_by_reference["synthetic-nurse-consult-2026-08-24"]["occurred_at"].startswith(
            "2026-08-24"
        )
        assert ai_by_reference["synthetic-patient-session-2026-08-20"]["occurred_at"].startswith(
            "2026-08-20"
        )
        assert all(row["source_reference"] for row in ai_rows)
        assert len(allergy_rows) == 2
        assert assertion_count == 2
        assert clinical_conflict_count == 1
        assert publication_rows == [{"state": "draft", "severity_class": "medication_dosage"}]
        assert publication_evidence_status == "mismatch"
    finally:
        engine.dispose()

    seed_source = (BACKEND_ROOT / "app" / "scripts" / "seed_demo.py").read_text(encoding="utf-8")
    assert "Base.metadata.create_all" not in seed_source
