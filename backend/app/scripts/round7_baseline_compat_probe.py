"""Exercise the baseline application against the expanded disposable schema."""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
from sqlalchemy import create_engine, text


def wait_for_health(client: httpx.Client) -> None:
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            response = client.get("/health")
            if response.status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.25)
    raise AssertionError("baseline application did not become healthy")


def find_free_port() -> int:
    with socket.socket() as server_socket:
        server_socket.bind(("127.0.0.1", 0))
        return int(server_socket.getsockname()[1])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline_root", type=Path)
    args = parser.parse_args()

    database_url = os.environ["DATABASE_URL"]
    seed_password = os.environ["DEMO_SEED_PASSWORD"]
    environment = os.environ.copy()
    environment["ALLOWED_ORIGINS"] = "http://127.0.0.1:5173"

    baseline_upgrade = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=args.baseline_root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    upgrade_output = f"{baseline_upgrade.stdout}\n{baseline_upgrade.stderr}"
    unknown_revision_markers = (
        "Can't locate revision",
        "No such revision",
        "ResolutionError",
    )
    assert baseline_upgrade.returncode != 0
    assert any(marker in upgrade_output for marker in unknown_revision_markers)

    port = find_free_port()
    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=args.baseline_root,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        with httpx.Client(
            base_url=f"http://127.0.0.1:{port}",
            headers={"Origin": "http://127.0.0.1:5173"},
            timeout=10,
            trust_env=False,
        ) as client:
            wait_for_health(client)
            login = client.post(
                "/auth/login",
                json={"email": "clinician.a@clinic-a.test", "password": seed_password},
            )
            assert login.status_code == 200, login.text
            patients = client.get("/patients")
            assert patients.status_code == 200, patients.text
            patient_id = patients.json()[0]["id"]
            glance = client.get(f"/patients/{patient_id}/glance")
            assert glance.status_code == 200, glance.text
            highlight_id = next(
                item["resource_id"]
                for item in glance.json()
                if item.get("resource_type") == "highlight"
            )
            feedback = client.post(
                f"/highlights/{highlight_id}/feedback",
                json={
                    "event_type": "pinned",
                    "idempotency_key": "round7-baseline-feedback",
                },
            )
            assert feedback.status_code == 200, feedback.text

        engine = create_engine(database_url, future=True)
        try:
            with engine.connect() as connection:
                applied_to_profile = connection.execute(
                    text(
                        "SELECT applied_to_profile FROM highlight_feedback_events "
                        "WHERE idempotency_key = 'round7-baseline-feedback'"
                    )
                ).scalar_one()
            assert applied_to_profile is True
        finally:
            engine.dispose()
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=10)

    print(
        json.dumps(
            {
                "baseline_startup_against_0015": "expected_unknown_revision",
                "baseline_glance_and_feedback_write": "passed",
                "omitted_applied_to_profile": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
