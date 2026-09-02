"""Create and inspect a small synthetic database at an older migration revision."""

from __future__ import annotations

import argparse
import json
from hashlib import sha256

from sqlalchemy import inspect, select, text

from app.db.base import new_id, utcnow
from app.db.session import SessionLocal
from app.models import (
    Clinic,
    ClinicMembership,
    Comment,
    Entry,
    EntryVersion,
    Patient,
    PatientUserLink,
    Task,
    User,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True, help="opaque disposable probe label")
    parser.add_argument("command", choices=("prepare", "snapshot"))
    return parser


def prepare(label: str) -> dict[str, object]:
    db = SessionLocal()
    try:
        clinic = Clinic(name=f"Round5 Legacy {label}")
        db.add(clinic)
        db.flush()
        staff = User(
            email=f"round5-{label}@synthetic.test",
            password_hash="synthetic-legacy-hash",
            display_name="Round5 Synthetic Staff",
            is_active=True,
        )
        db.add(staff)
        db.flush()
        db.add(ClinicMembership(clinic_id=clinic.id, user_id=staff.id, role="staff"))
        patient = Patient(
            clinic_id=clinic.id,
            synthetic_display_name=f"Round5 Synthetic Patient {label}",
        )
        db.add(patient)
        db.flush()
        db.add(PatientUserLink(user_id=staff.id, patient_id=patient.id))
        entry = Entry(
            clinic_id=clinic.id,
            patient_id=patient.id,
            entry_type="staff_note",
            owner_role="staff",
            visibility="internal",
            current_version=1,
            created_by_user_id=staff.id,
            occurred_at=utcnow(),
            source_kind="manual",
            source_reference=f"round5-legacy-{label}",
            created_at=utcnow(),
            updated_at=utcnow(),
        )
        db.add(entry)
        db.flush()
        version = EntryVersion(
            entry_id=entry.id,
            version_number=1,
            content="Legacy synthetic source record.",
            created_by_user_id=staff.id,
            created_by_role="staff",
            base_version=0,
            created_at=utcnow(),
        )
        db.add(version)
        db.flush()
        comment = Comment(
            clinic_id=clinic.id,
            patient_id=patient.id,
            entry_id=entry.id,
            author_user_id=staff.id,
            body="Legacy synthetic comment.",
            updated_at=utcnow(),
        )
        db.add(comment)
        db.add(
            Task(
                clinic_id=clinic.id,
                patient_id=patient.id,
                source_entry_id=entry.id,
                source_comment_id=None,
                title="Legacy synthetic task",
                created_by_user_id=staff.id,
                assigned_to_user_id=staff.id,
                status="open",
                version=1,
                created_at=utcnow(),
                updated_at=utcnow(),
            )
        )
        quote = "Legacy synthetic"
        db.flush()
        db.execute(
            text(
                "INSERT INTO highlights ("
                "id, clinic_id, patient_id, source_entry_id, source_version_id, "
                "start_offset, end_offset, quote, quote_sha256, offset_unit, item_kind, "
                "status, display_priority, risk_level, risk_reason, action_label, "
                "action_state, created_by_user_id, created_by_role, reviewed_by_user_id, "
                "reviewed_at, created_at, updated_at) VALUES ("
                ":id, :clinic_id, :patient_id, :source_entry_id, :source_version_id, "
                ":start_offset, :end_offset, :quote, :quote_sha256, :offset_unit, "
                ":item_kind, :status, :display_priority, :risk_level, :risk_reason, "
                ":action_label, :action_state, :created_by_user_id, :created_by_role, "
                ":reviewed_by_user_id, :reviewed_at, :created_at, :updated_at)"
            ),
            {
                "id": new_id(),
                "clinic_id": clinic.id,
                "patient_id": patient.id,
                "source_entry_id": entry.id,
                "source_version_id": version.id,
                "start_offset": 0,
                "end_offset": len(quote),
                "quote": quote,
                "quote_sha256": sha256(quote.encode("utf-8")).hexdigest(),
                "offset_unit": "unicode_codepoint",
                "item_kind": "information",
                "status": "accepted",
                "display_priority": 80.0,
                "risk_level": None,
                "risk_reason": "Legacy synthetic probe item.",
                "action_label": None,
                "action_state": "not_applicable",
                "created_by_user_id": staff.id,
                "created_by_role": "staff",
                "reviewed_by_user_id": staff.id,
                "reviewed_at": utcnow(),
                "created_at": utcnow(),
                "updated_at": utcnow(),
            },
        )
        db.commit()
        return {"label": label, "clinic_id": clinic.id, "patient_id": patient.id}
    finally:
        db.close()


def snapshot(label: str) -> dict[str, object]:
    db = SessionLocal()
    try:
        inspector = inspect(db.get_bind())
        clinic = db.scalar(select(Clinic).where(Clinic.name == f"Round5 Legacy {label}"))
        if clinic is None:
            raise SystemExit(f"Legacy probe data not found for label {label!r}")
        patient = db.scalar(
            select(Patient).where(
                Patient.clinic_id == clinic.id,
                Patient.synthetic_display_name == f"Round5 Synthetic Patient {label}",
            )
        )
        if patient is None:
            raise SystemExit(f"Legacy probe patient not found for label {label!r}")
        result: dict[str, object] = {
            "label": label,
            "tables": sorted(inspector.get_table_names()),
            "legacy_counts": {},
        }
        counts = result["legacy_counts"]
        assert isinstance(counts, dict)
        for table in (
            "entries",
            "entry_versions",
            "comments",
            "highlights",
            "tasks",
            "patient_publications",
            "patient_publication_versions",
            "patient_publication_evidence",
        ):
            if inspector.has_table(table):
                if table == "patient_publication_versions":
                    query = (
                        "SELECT COUNT(*) FROM patient_publication_versions v "
                        "JOIN patient_publications p ON p.id = v.publication_id "
                        "WHERE p.patient_id = :patient_id"
                    )
                elif table == "patient_publication_evidence":
                    query = (
                        "SELECT COUNT(*) FROM patient_publication_evidence e "
                        "JOIN patient_publications p ON p.id = e.publication_id "
                        "WHERE p.patient_id = :patient_id"
                    )
                elif table == "entry_versions":
                    query = (
                        "SELECT COUNT(*) FROM entry_versions v "
                        "JOIN entries e ON e.id = v.entry_id "
                        "WHERE e.patient_id = :patient_id"
                    )
                else:
                    query = f"SELECT COUNT(*) FROM {table} WHERE patient_id = :patient_id"
                counts[table] = db.execute(
                    text(query),
                    {"patient_id": patient.id},
                ).scalar_one()
        return result
    finally:
        db.close()


def main() -> None:
    args = _parser().parse_args()
    result = prepare(args.label) if args.command == "prepare" else snapshot(args.label)
    print(json.dumps(result, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
