# Contributing to PySteg

Thank you for your interest in contributing to PySteg!

## Before you start

- Check the [open issues](https://github.com/kisscool-fr/pysteg/issues) and [Roadmap](README.md#roadmap) to avoid duplicating effort.
- For a significant change, open an issue first so we can discuss the approach before you write code.

## Development setup

You need Python 3.13, [uv](https://docs.astral.sh/uv/), and optionally [just](https://github.com/casey/just).

```bash
just init     # create venv with the right Python version
just install  # install all dependencies
```

Or with uv directly:

```bash
uv sync
```

## Running the full local CI pipeline

```bash
just ci
```

This runs (in order): lock-file check, lint/format with ruff, type-check with pyright, pytest, and pip-audit + gitleaks.

You can also run individual steps:

| Command | What it does |
|---------|-------------|
| `just test` | Run pytest |
| `just format` | Lint and auto-fix with ruff |
| `just typing` | Type-check with pyright (strict) |
| `just audit` | pip-audit + gitleaks secret scan |

## Code style

- Formatting and linting: **ruff** (configured in `ruff.toml`). Run `just format` before committing.
- Type annotations: all public interfaces must be fully annotated; the project uses **pyright strict** mode.
- No commented-out code or debugging print statements in PRs.

## Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>
```

Common types: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`, `style`, `build`.  
Examples: `feat(crypto): add keyfile support`, `fix(ui): reset text field on mode switch`.

## Submitting a pull request

1. Fork the repository and create a branch from `main`.
2. Make your changes; keep commits focused and atomic.
3. Ensure `just ci` passes locally.
4. Open a PR against `main` and fill in the pull request template.
5. A maintainer will review and may request changes.

## Security issues

**Do not open a public issue for security vulnerabilities.** Please follow the [Security Policy](SECURITY.md) instead.

## License

By contributing, you agree that your contributions will be licensed under the project's [GPL-3.0-or-later](LICENSE) license.
