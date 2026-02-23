set quiet
set windows-shell := ["cmd.exe", "/c"]

# Default recipe: show available commands
default:
    @just --list

python_version := trim(read(".python-version"))

init:
    echo Installing Python {{ python_version }}
    uv python install {{ python_version }}
    uv venv --python {{ python_version }}

clean:
    echo Cleaning up...
    uv venv --clear

install:
    echo Installing dependencies...
    uv sync

update:
    echo Updating dependencies...
    uv sync --upgrade

outdated:
    echo Checking for outdated dependencies...
    uv pip list --outdated

run:
    echo Running the application...
    uv run -m app

check:
    echo Checking the lock file...
    uv lock --check

format:
    echo Formatting the code...
    uv run ruff check ./app/ --fix
    uv run ruff check ./tests/ --ignore S101 --fix
    uv run ruff format ./app/ ./tests/

typing:
    echo Running type checking...
    uv run pyright ./app/ ./tests/ --threads 4

test:
    echo Running tests...
    uv run pytest

audit:
    echo Running security audit...
    uv run pip-audit . || true
    gitleaks dir ./ --max-decode-depth 5

ci: check format typing test audit
