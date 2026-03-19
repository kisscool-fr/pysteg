set quiet
set windows-shell := ["cmd.exe", "/c"]

# pysteg – just recipes for dev, test, and run
# Usage: just [recipe]
# List all recipes: just --list

python_version := trim(read(".python-version"))

# Show available recipes (default)
default:
    @just --list

# Create venv and install Python from .python-version
init:
    echo Installing Python {{ python_version }}
    uv python install {{ python_version }}
    uv venv --python {{ python_version }}

# Remove all packages from the venv (venv stays)
clean:
    echo Cleaning up...
    uv venv --clear

# Install/sync dependencies from lockfile (uv sync)
install:
    echo Installing dependencies...
    uv sync

# Upgrade dependencies and refresh lockfile
update:
    echo Updating dependencies...
    uv sync --upgrade

# List direct dependencies from pyproject.toml and their versions
info:
    echo Listing direct dependencies from pyproject.toml and their versions...
    uv tree --depth 1

# List outdated dependencies
outdated:
    echo Checking for outdated dependencies...
    uv pip list --outdated --format=columns

# Run the app (uv run -m app)
run:
    echo Running the application...
    uv run -m app

# Verify lockfile is in sync with pyproject.toml
check:
    echo Checking the lock file...
    uv lock --check

# Lint and format app/ and tests/ with ruff
format:
    echo Formatting the code...
    uv run ruff check ./app/ --fix
    uv run ruff check ./tests/ --ignore S101 --fix
    uv run ruff format ./app/ ./tests/

# Type-check with pyright
typing:
    echo Running type checking...
    uv run pyright ./app/ ./tests/ --threads 4

# Run pytest
test:
    echo Running tests...
    uv run pytest

# Security: pip-audit (deps) and gitleaks (secrets)
audit:
    echo Running security audit...
    uv run pip-audit . || true
    gitleaks dir ./ --max-decode-depth 5

# CI pipeline: check lockfile, format, typecheck, test, audit
ci: check format typing test audit
