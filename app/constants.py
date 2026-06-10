from importlib.metadata import version
from pathlib import Path

APP_NAME = "PySteg"
APP_VERSION = version("pysteg")

SHARED_SECRET_MIN_LENGTH = 8

ASSETS_DIRECTORY: Path = Path(__file__).parent.parent / "assets"

ICON_LOCK = "🔐"
ICON_UNLOCK = "🔓"
