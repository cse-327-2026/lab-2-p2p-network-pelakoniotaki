SHELL := /bin/bash
PY := python3
VENV := .venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest

.PHONY: deps test itest grade clean lint

deps:
	$(PY) -m venv $(VENV)
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt

lint:
	@echo "Optional: add ruff/black/mypy here."

test:
	$(PYTEST) -q

itest:
	cd assignments/A1_grpc_kv && docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from tester

grade: test itest
	@echo "All checks passed."

clean:
	rm -rf $(VENV) .pytest_cache
	cd assignments/A1_grpc_kv && docker compose -f docker-compose.test.yml down -v --remove-orphans || true
