# -*- mode: Makefile -*-

.phony: run

init:
	uv python install 3.13
	uv venv --python 3.13

clean:
	uv venv --clear

install:
	uv sync

update:
	uv sync --upgrade

outdated:
	uv pip list --outdated

run:
	uv run -m app

check:
	uv lock --check

format:
	uv run ruff check ./app/ --fix
	uv run ruff check ./tests/ --ignore S101 --fix
	uv run ruff format ./app/ ./tests/ 

typing:
	uv run pyright ./app/ ./tests/ --threads 4

test:
	uv run pytest

audit:
	uv run pip-audit .
	gitleaks dir ./ --max-decode-depth 5

ci: check format typing test audit