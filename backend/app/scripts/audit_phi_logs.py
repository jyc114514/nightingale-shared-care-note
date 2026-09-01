"""Audit explicitly supplied local log files without echoing matched values."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

from app.ai.redaction import PHONE_PATTERN, SG_ID_PATTERN
from app.observability.safe_logging import (
    _BEARER_PATTERN,
    _COOKIE_PATTERN,
    _DATABASE_URL_PATTERN,
    _name_pattern,
)


def _patterns(known_names: Iterable[str]) -> dict[str, re.Pattern[str] | None]:
    return {
        "sg_id": SG_ID_PATTERN,
        "phone": PHONE_PATTERN,
        "known_name": _name_pattern(known_names),
        "authorization": _BEARER_PATTERN,
        "api_key": re.compile(
            r"(?:\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9_]{20,}|"
            r"github_pat_[A-Za-z0-9_]{20,})\b|\b(?:api[_-]?key|deepseek[_-]?api[_-]?key|"
            r"access[_-]?token|session[_-]?token)\s*[:=]\s*[^\s,;]+)",
            re.IGNORECASE,
        ),
        "database_url": _DATABASE_URL_PATTERN,
        "cookie_or_session": _COOKIE_PATTERN,
    }


def _safe_path(path: Path) -> str:
    return str(path).replace("\r", r"\r").replace("\n", r"\n")


def audit_paths(paths: Iterable[Path], known_names: Iterable[str] = ()) -> int:
    failed = False
    compiled = _patterns(known_names)
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            failed = True
            print(
                json.dumps(
                    {
                        "file": _safe_path(path),
                        "category": "unreadable",
                        "hit_count": 1,
                        "line_count": 0,
                    },
                    ensure_ascii=True,
                    sort_keys=True,
                )
            )
            continue
        line_count = len(text.splitlines())
        if text and not text.splitlines():
            line_count = 1
        for category, pattern in compiled.items():
            hit_count = len(pattern.findall(text)) if pattern is not None else 0
            if hit_count:
                failed = True
            print(
                json.dumps(
                    {
                        "file": _safe_path(path),
                        "category": category,
                        "hit_count": hit_count,
                        "line_count": line_count,
                    },
                    ensure_ascii=True,
                    sort_keys=True,
                )
            )
    print(json.dumps({"status": "failed" if failed else "clean"}, sort_keys=True))
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit explicit local logs for PHI/credential leaks"
    )
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--known-name", action="append", default=[])
    args = parser.parse_args(argv)
    return audit_paths(args.paths, args.known_name)


if __name__ == "__main__":
    sys.exit(main())
