# AGENTS.md

## Project overview

pysteg is a desktop GUI application for LSB steganography on PNG images with optional AES-256-GCM encryption.  
Built with Python 3.13, PyQt6, the `stegano` library, and the `cryptography` library.  
Licensed under MIT.

## Project structure

```
app/                    # Main application package
├── __main__.py         # Entry point (uv run -m app)
├── aes256.py           # AES-GCM + PBKDF2 crypto helper
├── constants.py        # App name, version, paths, icons
└── gui/                # PyQt6 UI layer
    ├── main_window.py
    ├── controllers/    # Action logic (encrypt/decrypt, hide/reveal)
    ├── models/         # Data models (window state, mode enum)
    ├── validators/     # Input validation
    └── ui/             # UI layout and components
tests/                  # pytest test suite
```

## Development workflow

The project uses **uv** for dependency management and **just** as task runner.

| Command          | Purpose                                      |
|------------------|----------------------------------------------|
| `just init`      | Create venv and install Python from `.python-version` |
| `just install`   | Install/sync dependencies from lockfile      |
| `just run`       | Run the app (`uv run -m app`)                |
| `just format`    | Lint and format with ruff                    |
| `just typing`    | Type-check with pyright (strict mode)        |
| `just test`      | Run pytest                                   |
| `just audit`     | Security audit (pip-audit + gitleaks)        |
| `just ci`        | Full CI pipeline: check, format, typing, test, audit |

## Code style

Enforced by **ruff** (`ruff.toml`) and **pyright** (strict mode in `pyproject.toml`):

- Python 3.13+ — use modern syntax (`StrEnum`, `type` aliases, `match`, etc.)
- Line length: 88
- Indent: 4 spaces
- Quotes: double
- Imports: one per line (`force-single-line = true` in isort)
- Naming: `snake_case` for functions/variables/modules, `PascalCase` for classes
- Type annotations required on all public functions and methods (pyright strict)
- Ruff rule sets: bugbear, bandit, pylint, pyupgrade, simplify, comprehensions, perflint

When editing `tests/`, ruff rule `S101` (use of `assert`) is ignored.

## Testing

- Framework: **pytest**
- Run: `just test` or `uv run pytest`
- Tests live in `tests/` with `test_*.py` naming convention
- New features should include corresponding tests when feasible

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on push/PR to `main`:  
setup → check (ruff + pyright) → security-audit (pip-audit + gitleaks) → test (pytest)

## Key patterns

- GUI follows a lightweight MVC pattern: `models/` for state, `controllers/` for logic, `ui/` for layout
- Crypto operations return `tuple[bool, str]` (success flag + message/data)
- The `stegano` library lacks type stubs — use `# type: ignore` on its imports
- i18n uses `gettext` (`_ = gettext.gettext`)
- Broad exceptions in controller code are annotated with `# noqa: BLE001`
