"""Build a standalone binary of the app with PyInstaller.

Usage:
    python scripts/build.py [version]

The ``version`` argument is optional and only labels the artifact
(defaults to the pyproject.toml version).

PyInstaller cannot cross-compile: the produced binary always targets the
host platform, which is detected automatically. Release pipelines run this
script once per OS runner to cover Windows, macOS, and Linux.

Output per platform (written to ``dist/``):
- Windows: ``pysteg-<version>-windows.exe`` (single file)
- Linux:   ``pysteg-<version>-linux`` (single file)
- macOS:   ``pysteg-<version>-macos.zip`` (a zipped ``PySteg.app`` bundle)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import PyInstaller.__main__
from bump_version import read_current_version

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENTRY_POINT = PROJECT_ROOT / "app" / "__main__.py"
ASSETS_DIR = PROJECT_ROOT / "assets"
APP_ICON = ASSETS_DIR / "icons" / "icon.png"
DIST_DIR = PROJECT_ROOT / "dist"

APP_BUNDLE_NAME = "PySteg"
DITTO = "/usr/bin/ditto"


def detect_host() -> str:
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    return "linux"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a standalone binary.")
    parser.add_argument(
        "version",
        nargs="?",
        default=None,
        help="version label for the artifact (default: pyproject.toml version)",
    )
    return parser.parse_args()


def _common_args(name: str, data_sep: str) -> list[str]:
    return [
        str(ENTRY_POINT),
        "--name",
        name,
        "--windowed",
        "--noconfirm",
        "--clean",
        "--paths",
        str(PROJECT_ROOT),
        "--add-data",
        f"{ASSETS_DIR}{data_sep}assets",
        "--copy-metadata",
        "pysteg",
        "--icon",
        str(APP_ICON),
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(PROJECT_ROOT / "build"),
        "--specpath",
        str(PROJECT_ROOT / "build"),
    ]


def _build_macos_app(version: str) -> Path:
    """Build a ``.app`` bundle (onedir + windowed) and zip it for release."""
    PyInstaller.__main__.run([*_common_args(APP_BUNDLE_NAME, ":"), "--onedir"])

    app_path = DIST_DIR / f"{APP_BUNDLE_NAME}.app"
    zip_path = DIST_DIR / f"pysteg-{version}-macos.zip"
    zip_path.unlink(missing_ok=True)
    # ditto preserves the bundle's symlinks and metadata (unlike plain zip).
    subprocess.run(  # noqa: S603
        [DITTO, "-c", "-k", "--keepParent", str(app_path), str(zip_path)],
        check=True,
    )
    return zip_path


def _build_onefile(version: str, host: str) -> Path:
    name = f"pysteg-{version}-{host}"
    data_sep = ";" if host == "windows" else ":"
    PyInstaller.__main__.run([*_common_args(name, data_sep), "--onefile"])

    suffix = ".exe" if host == "windows" else ""
    return DIST_DIR / f"{name}{suffix}"


def build(version: str) -> Path:
    host = detect_host()
    print(f"Building pysteg {version} for {host}...")
    if host == "macos":
        return _build_macos_app(version)
    return _build_onefile(version, host)


def main() -> None:
    args = parse_args()
    version = args.version or read_current_version()

    artifact = build(version)
    print(f"Built: {artifact}")


if __name__ == "__main__":
    main()
