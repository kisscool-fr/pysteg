"""Bump version, update lockfile, commit, and tag a release.

Usage:
    python scripts/release.py [patch|minor|major|X.Y.Z]

Orchestrates the full release flow in pure Python so it works
on both Unix and Windows. Defaults to "patch" when called with
no arguments.
"""

from __future__ import annotations

import subprocess
import sys

from bump_version import compute_next_version
from bump_version import read_current_version
from bump_version import write_version


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, check=False)  # noqa: S603
    if result.returncode != 0:
        print(f"error: command failed: {' '.join(cmd)}", file=sys.stderr)
        sys.exit(result.returncode)


def main() -> None:
    bump = sys.argv[1] if len(sys.argv) > 1 else "patch"

    current = read_current_version()
    new_version = compute_next_version(current, bump)
    write_version(new_version)
    print(f"Bumping to v{new_version}")

    run(["uv", "lock"])
    run(["git", "add", "pyproject.toml", "uv.lock"])
    run(["git", "commit", "-m", f"release: v{new_version}"])
    run(["git", "tag", "-a", f"v{new_version}", "-m", f"v{new_version}"])

    print(f"Release v{new_version} ready. Run 'git push && git push --tags' to publish.")


if __name__ == "__main__":
    main()
