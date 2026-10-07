"""Generate platform-specific app icons from a single master image.

Usage:
    python scripts/generate_icons.py

Reads ``assets/icons/icon-master.png`` (expected to be a 1024x1024 PNG with
the artwork inset by roughly 8-10% on each side, per Apple's Human Interface
Guidelines for Dock icons) and produces, alongside it:

- ``icon.icns``: macOS icon bundle (requires ``iconutil``, macOS only).
- ``icon.ico``: Windows multi-resolution icon.
- ``icon.png``: resized master, used at runtime for QIcon (title bar,
  Windows/Linux taskbar) and as the Linux build icon.

If ``icon-master.png`` is missing, falls back to upscaling the existing
``icon.png`` so the pipeline still runs end to end, but this is a stopgap:
replace ``icon-master.png`` with real 1024x1024 artwork and re-run this
script to get a crisp, properly-padded icon on every platform.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ICONS_DIR = PROJECT_ROOT / "assets" / "icons"
MASTER_ICON = ICONS_DIR / "icon-master.png"
LEGACY_ICON = ICONS_DIR / "icon.png"

ICNS_OUTPUT = ICONS_DIR / "icon.icns"
ICO_OUTPUT = ICONS_DIR / "icon.ico"
PNG_OUTPUT = ICONS_DIR / "icon.png"

MASTER_SIZE = 1024
RUNTIME_PNG_SIZE = 512
ICO_SIZES = [16, 32, 48, 64, 128, 256]
ICNS_SIZES = {
    "icon_16x16.png": 16,
    "icon_16x16@2x.png": 32,
    "icon_32x32.png": 32,
    "icon_32x32@2x.png": 64,
    "icon_128x128.png": 128,
    "icon_128x128@2x.png": 256,
    "icon_256x256.png": 256,
    "icon_256x256@2x.png": 512,
    "icon_512x512.png": 512,
    "icon_512x512@2x.png": 1024,
}


def load_master() -> Image.Image:
    if MASTER_ICON.exists():
        img = Image.open(MASTER_ICON).convert("RGBA")
        if img.size != (MASTER_SIZE, MASTER_SIZE):
            print(
                f"warning: {MASTER_ICON.name} is {img.size[0]}x{img.size[1]}, "
                f"expected {MASTER_SIZE}x{MASTER_SIZE}",
                file=sys.stderr,
            )
        return img

    print(
        f"warning: {MASTER_ICON} not found; falling back to upscaling "
        f"{LEGACY_ICON.name}. This keeps the build working but does NOT fix "
        "the icon padding/quality issue. Provide a real "
        f"{MASTER_SIZE}x{MASTER_SIZE} master with safe-zone padding and "
        "re-run this script.",
        file=sys.stderr,
    )
    img = Image.open(LEGACY_ICON).convert("RGBA")
    return img.resize((MASTER_SIZE, MASTER_SIZE), Image.Resampling.LANCZOS)


def resized(master: Image.Image, size: int) -> Image.Image:
    return master.resize((size, size), Image.Resampling.LANCZOS)


def write_runtime_png(master: Image.Image) -> None:
    resized(master, RUNTIME_PNG_SIZE).save(PNG_OUTPUT)
    print(f"wrote {PNG_OUTPUT}")


def write_ico(master: Image.Image) -> None:
    sizes = [(s, s) for s in ICO_SIZES]
    master.save(ICO_OUTPUT, format="ICO", sizes=sizes)
    print(f"wrote {ICO_OUTPUT}")


def write_icns(master: Image.Image) -> None:
    if sys.platform != "darwin":
        print(
            "skipping .icns generation: iconutil is only available on macOS",
            file=sys.stderr,
        )
        return

    if shutil.which("iconutil") is None:
        print("skipping .icns generation: iconutil not found on PATH", file=sys.stderr)
        return

    build_dir = PROJECT_ROOT / "build"
    build_dir.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=build_dir) as tmp:
        iconset_dir = Path(tmp) / "icon.iconset"
        iconset_dir.mkdir()
        for filename, size in ICNS_SIZES.items():
            resized(master, size).save(iconset_dir / filename)

        subprocess.run(  # noqa: S603
            ["/usr/bin/iconutil", "-c", "icns", str(iconset_dir), "-o", str(ICNS_OUTPUT)],
            check=True,
        )
    print(f"wrote {ICNS_OUTPUT}")


def main() -> None:
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    master = load_master()

    write_runtime_png(master)
    write_ico(master)
    write_icns(master)


if __name__ == "__main__":
    main()
