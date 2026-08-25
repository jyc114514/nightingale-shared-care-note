"""Capture safe Python-environment evidence without recording local file URLs.

The command records interpreter metadata, pip health, and package name/version
pairs. It deliberately excludes environment variables, credentials, and package
installation paths.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import subprocess
import sys
from pathlib import Path


def package_lines() -> list[str]:
    packages = {
        distribution.metadata["Name"]: distribution.version
        for distribution in importlib.metadata.distributions()
        if distribution.metadata.get("Name")
    }
    return [
        f"{name}=={version}"
        for name, version in sorted(packages.items(), key=lambda item: item[0].lower())
    ]


def command_output(command: list[str]) -> tuple[int, str]:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    output = (completed.stdout + completed.stderr).strip()
    return completed.returncode, output


def write_snapshot(output_path: Path) -> None:
    pip_code, pip_check = command_output([sys.executable, "-m", "pip", "check"])
    _, pip_version = command_output([sys.executable, "-m", "pip", "--version"])
    environment_root = Path(sys.prefix)
    if (environment_root / "conda-meta").is_dir():
        environment_type = "conda"
    elif (environment_root / "pyvenv.cfg").is_file():
        environment_type = "venv/virtualenv"
    else:
        environment_type = "other Python environment"

    lines = [
        "# Safe ai_env snapshot: package names and versions only",
        f"environment_type={environment_type}",
        f"python_executable={sys.executable}",
        f"python_version={sys.version.replace(chr(10), ' ')}",
        f"sys_prefix={sys.prefix}",
        f"pip_version={pip_version}",
        f"pip_check_exit_code={pip_code}",
        f"pip_check={pip_check or '<no output>'}",
        "",
        "[packages]",
        *package_lines(),
        "",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def package_map(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    in_packages = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line == "[packages]":
            in_packages = True
            continue
        if in_packages and "==" in line:
            name, version = line.split("==", 1)
            result[name.lower()] = version
    return result


def write_delta(before: Path, after: Path, output: Path) -> None:
    before_map = package_map(before)
    after_map = package_map(after)
    names = sorted(set(before_map) | set(after_map))
    changes = []
    for name in names:
        old = before_map.get(name)
        new = after_map.get(name)
        if old != new:
            changes.append(f"{name}: {old or '<missing>'} -> {new or '<missing>'}")
    output.write_text(
        "# Package delta (after compared with before)\n"
        + ("\n".join(changes) if changes else "No package changes detected.")
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_constraints(output_path: Path) -> None:
    """Write current package versions as resolver constraints for this environment."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "# Generated from the confirmed ai_env; package names and versions only.\n"
        + "\n".join(package_lines())
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--delta-from", type=Path)
    parser.add_argument("--delta-output", type=Path)
    parser.add_argument("--constraints-output", type=Path)
    args = parser.parse_args()

    write_snapshot(args.output)
    if args.delta_from and args.delta_output:
        write_delta(args.delta_from, args.output, args.delta_output)
    if args.constraints_output:
        write_constraints(args.constraints_output)


if __name__ == "__main__":
    main()
