# -*- mode: Makefile -*-

.phony: run

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

style:
	uv run pyright ./app/ --threads 4

test:
	uv run pytest

audit:
	uv run pip-audit
	gitleaks dir ./ --max-decode-depth 5
