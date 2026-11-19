<p align="center">
  <img src="assets/icons/icon.png" alt="PySteg app icon" width="128" height="128">
</p>

<h1 align="center">PySteg</h1>

<p align="center">
  <a href="https://github.com/kisscool-fr/pysteg/actions/workflows/ci.yml"><img src="https://github.com/kisscool-fr/pysteg/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI"></a>
  <a href="https://github.com/kisscool-fr/pysteg/actions/workflows/security.yml"><img src="https://github.com/kisscool-fr/pysteg/actions/workflows/security.yml/badge.svg?branch=main" alt="Security"></a>
  <a href="https://github.com/kisscool-fr/pysteg/releases/latest"><img src="https://img.shields.io/github/v/release/kisscool-fr/pysteg" alt="Latest release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/kisscool-fr/pysteg" alt="License"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fkisscool-fr%2Fpysteg%2Fmain%2Fpyproject.toml" alt="Python version">
  <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://microsoft.github.io/pyright/"><img src="https://microsoft.github.io/pyright/img/pyright_badge.svg" alt="Checked with pyright"></a>
  <a href="https://github.com/PyCQA/bandit"><img src="https://img.shields.io/badge/security-bandit-yellow.svg" alt="Security: bandit"></a>
  <a href="https://github.com/gitleaks/gitleaks"><img src="https://img.shields.io/badge/protected%20by-gitleaks-blue" alt="Protected by gitleaks"></a>
</p>

<p align="center">
  A simple GUI for steganography: hide and reveal secret messages in images,<br>
  with optional AES-256-GCM encryption and Argon2id key derivation.
</p>

Built as a replacement for [Steganozorus](https://thomasnerrant.com/steganozorus.htm) © 2002 – [Thomas Nerrant](https://thomasnerrant.com/).

> **Warning:** PySteg is still under active development. Backward compatibility for hidden text is not guaranteed before version 1.0 (messages encoded with an earlier release may not be readable after an upgrade).

## Sponsor

If you find this project useful, consider [buying me a coffee](https://www.buymeacoffee.com/kisscool).

## Features

- **Hide and reveal messages** in image files using LSB or EXIF steganography
- **AES-256-GCM encryption** with Argon2id key derivation from a shared secret
- **Plain text mode** to hide a message without encryption (useful for testing or low-risk payloads)
- Desktop GUI built with PyQt6

### Supported media formats

PySteg uses [Stegano](https://github.com/cedricbonhomme/Stegano) for steganography.

| Format | Technique | Support |
|--------|-----------|---------|
| PNG, BMP | LSB (least significant bit) | ✅ |
| JPEG, TIFF | EXIF header | ✅ |
| WAV | LSB | 🔜 |
| PNG (grayscale) | RDH (reversible histogram shifting) | 🔜 |
| RGB images (PNG, BMP, JPEG, …) | RED (red channel) | 🔜 |

✅ supported today

🔜 available in Stegano, planned for PySteg integration

## Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- [just](https://github.com/casey/just) (optional, for recipe commands)

## Installation

First-time setup (creates a virtual environment with the Python version from `.python-version`):

```bash
just init
just install
```

Or with uv directly:

```bash
uv sync
```

## Usage

```bash
just run
```

Or:

```bash
uv run -m app
```

1. Choose **Hide** or **Reveal** mode.
2. Drop a cover image on the window, or click **Browse…**. PySteg shows its format, the technique it will use (LSB or EXIF) and how much text it can hold.
3. In hide mode, type the message; the capacity meter shows how much of the image it uses.
4. Enter a shared secret (at least 8 characters, typed twice when hiding), or turn **Encrypt with a shared secret** off to store plain text.
5. In hide mode, check the output path (pre-filled next to the cover image) or click **Change…**.
6. Click the action button or press Ctrl+Enter (⌘+Return on macOS). The button stays disabled, with the reason underneath, until everything is valid.
7. After hiding, open the output folder or click **Test with Reveal** to check the new image. After revealing, **Copy** the message or save it as a `.txt` file.

See [docs/design/DESIGN.md](docs/design/DESIGN.md) for the reasoning behind the interface.

## Development

Common tasks via [just](https://github.com/casey/just):

```bash
just test      # run pytest
just format    # lint and format with ruff
just typing    # type-check with pyright
just ci        # full local CI pipeline
```

List all recipes with `just --list`.

## Building a binary

Build a standalone executable with [PyInstaller](https://pyinstaller.org/):

```bash
just build         # build for the host OS, version from pyproject.toml
just build 0.4.0   # override the version label
```

The output is written to `dist/`:

- **Windows** — `pysteg-<version>-windows.exe` (single file)
- **Linux** — `pysteg-<version>-linux` (single file)
- **macOS** — `pysteg-<version>-macos.zip` (a zipped `PySteg.app` bundle)

> [!NOTE]
> PyInstaller cannot cross-compile: a build always targets the OS it runs on.
> That is why each release binary is built on its own runner. Releases attach
> binaries for all three platforms automatically (see
> `.github/workflows/release.yml`).

## Screenshots

PySteg looks the same on Windows, macOS and Linux.

| Hide | Message hidden |
| :---: | :---: |
| <img src="docs/screenshots/hide.png" alt="Hide mode with a cover image, a message and a shared secret, ready to hide" width="340"> | <img src="docs/screenshots/hide-done.png" alt="Result page after hiding a message, with the new image and its actions" width="340"> |
| **Reveal** | **Wrong secret** |
| <img src="docs/screenshots/reveal.png" alt="Reveal mode showing the decrypted message with Copy and Save buttons" width="340"> | <img src="docs/screenshots/reveal-error.png" alt="Reveal mode with a wrong shared secret and troubleshooting tips" width="340"> |

## Roadmap

- [x] Choose output file name
- [ ] Add pane to choose encryption / diffusion algorithm
- [ ] Add support for more encryption algorithms
- [ ] Add support for keyfiles
- [ ] Audio and video support, drag & drop
- [ ] Deniability support
- [ ] Self-destructing messages (one-time reveal that restores the original cover)
- [ ] More languages
- [x] Binary release
- [ ] Code signing
- [x] Design improvements

> [!NOTE]
> Release binaries are currently **unsigned**. Planned signing per platform:
>
> - **Linux** — no code signing needed; publishing `SHA256` checksums for verification is enough.
> - **Windows** — free Authenticode signing via the [SignPath Foundation](https://signpath.org/) OSS tier (HSM-backed, integrates with GitHub Actions).
> - **macOS** — requires an Apple Developer Program membership ($99/yr) to sign with a *Developer ID Application* certificate and notarize the `.app`. Until then, bypass Gatekeeper with right-click → **Open** (or `xattr -d com.apple.quarantine <file>`).

## License

[GPL-3.0-or-later](LICENSE)

## Community

- [Contributing](CONTRIBUTING.md) — development setup, code style, and pull request process
- [Security policy](SECURITY.md) — how to report vulnerabilities privately
- [Code of conduct](CODE_OF_CONDUCT.md)

## Credits

[Sébastien B](https://github.com/kisscool-fr/)
