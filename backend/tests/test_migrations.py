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
            assert connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one() == ("0002_gate_b")
    finally:
        engine.dispose()


def test_migration_downgrade_and_reupgrade_are_reversible(migrated_database: str) -> None:
    downgraded = run_alembic(migrated_database, "downgrade", "0001_gate_a")
    assert downgraded.returncode == 0, downgraded.stderr
    upgraded = run_alembic(migrated_database, "upgrade", "head")
    assert upgraded.returncode == 0, upgraded.stderr
    checked = run_alembic(migrated_database, "check")
    assert checked.returncode == 0, checked.stderr


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

    seed_source = (BACKEND_ROOT / "app" / "scripts" / "seed_demo.py").read_text(encoding="utf-8")
    assert "Base.metadata.create_all" not in seed_source
