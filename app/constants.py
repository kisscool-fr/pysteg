import sys
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version
from pathlib import Path

APP_NAME = "PySteg"


def _resolve_version() -> str:
    try:
        return version("pysteg")
    except PackageNotFoundError:
        # Frozen binaries (PyInstaller) may ship without package metadata.
        return "0.0.0"


APP_VERSION = _resolve_version()

SHARED_SECRET_MIN_LENGTH = 8


def _resource_root() -> Path:
    """Root directory for bundled resources.

    PyInstaller unpacks bundled data files to a temporary directory exposed
    via ``sys._MEIPASS``; fall back to the project root for normal runs.
    """
    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir is not None:
        return Path(bundle_dir)
    return Path(__file__).parent.parent


ASSETS_DIRECTORY: Path = _resource_root() / "assets"
APP_ICON: Path = ASSETS_DIRECTORY / "icons" / "icon.png"

ICON_LOCK = "🔐"
ICON_UNLOCK = "🔓"
