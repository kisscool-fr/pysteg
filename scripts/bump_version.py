"""Bump the project version in pyproject.toml.

Usage:
    python scripts/bump_version.py [patch|minor|major|X.Y.Z]

Reads the current version from pyproject.toml, computes the new version,
writes it back, and prints the new version to stdout.
Defaults to "patch" when called with no arguments.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"
VERSION_RE = re.compile(r'^(version\s*=\s*")([^"]+)(")', re.MULTILINE)
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
VERSION_PARTS = 3


def read_current_version() -> str:
    with PYPROJECT.open("rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


def compute_next_version(current: str, bump: str) -> str:
    if SEMVER_RE.match(bump):
        return bump

    parts = current.split(".")
    if len(parts) != VERSION_PARTS or not all(p.isdigit() for p in parts):
        print(f"error: current version '{current}' is not valid semver", file=sys.stderr)
        sys.exit(1)

    major, minor, patch = (int(p) for p in parts)

    if bump == "patch":
        patch += 1
    elif bump == "minor":
        minor += 1
        patch = 0
    elif bump == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        print(f"error: invalid bump '{bump}' (use patch, minor, major, or X.Y.Z)", file=sys.stderr)
        sys.exit(1)

    return f"{major}.{minor}.{patch}"


def write_version(new_version: str) -> None:
    text = PYPROJECT.read_text()
    new_text, count = VERSION_RE.subn(rf"\g<1>{new_version}\g<3>", text, count=1)
    if count == 0:
        print("error: could not find version field in pyproject.toml", file=sys.stderr)
        sys.exit(1)
    PYPROJECT.write_text(new_text)


def main() -> None:
    bump = sys.argv[1] if len(sys.argv) > 1 else "patch"
    current = read_current_version()
    new_version = compute_next_version(current, bump)
    write_version(new_version)
    print(new_version)


if __name__ == "__main__":
    main()
