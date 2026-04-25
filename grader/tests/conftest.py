"""
Test-directory-level conftest that works around two bugs in legacy/duplicate
test files left in the repo, plus one ordering hazard:

1. test_02_mulitple_jobs.py (note the typo) and test_04_leader_failure.py use
   `from conftest import ...`, but there is no `conftest` module directly in
   `grader/tests/`. The real helpers live in `grader/conftest.py`. We re-export
   them here so the import works (pytest adds this directory to sys.path).

2. test_04_leader_failure.py calls `time.sleep(1)` without doing
   `import time`. We inject the `time` module into every collected test
   module's namespace (harmless no-op if the module already imports it).

3. test_04_leader_failure.py kills queue1 but never restarts it, which would
   break every subsequent test that expects queue1 to be alive (e.g.
   test_05_leader_failure does `kill_service("queue1")` with check=True; that
   raises if queue1 is already stopped). We add an autouse fixture that runs
   `docker compose up -d queue1 queue2 worker1` before AND after every test.
   This is a no-op when the services are already running, and brings them
   back when a previous test left one dead.

We do NOT modify any test file. This file only adds helper infrastructure.
"""

import subprocess
import time as _time

import pytest

from grader.conftest import (  # noqa: F401 (re-exported for `from conftest import ...`)
    BASE_URL,
    wait_for_system,
    submit_job_with_retries,
    submit_job,
    get_job,
    wait_for_completion,
    kill_service,
    restart_service,
    reset_system,
)


def pytest_collection_modifyitems(config, items):
    """Inject `time` into test modules that reference it without importing it."""
    for item in items:
        mod = getattr(item, "module", None)
        if mod is not None and not hasattr(mod, "time"):
            mod.time = _time


_REQUIRED_SERVICES = ("queue1", "queue2", "worker1")


def _ensure_up(svc):
    """Bring a docker-compose service up. No-op if already running."""
    try:
        subprocess.run(
            ["docker", "compose", "up", "-d", svc],
            check=False,
            capture_output=True,
            timeout=60,
        )
    except Exception:
        # Last-resort safety net so the test session never crashes here.
        pass


@pytest.fixture(autouse=True)
def _services_running():
    """Make sure required containers are running before each test.

    Some legacy tests (notably test_04_leader_failure.py) kill queue1 without
    restarting it. Without this fixture, every test that runs after that one
    would either hit a dead leader or have its `kill_service` call raise
    because the container is already stopped. This fixture is a cheap
    idempotent guard.
    """
    for svc in _REQUIRED_SERVICES:
        _ensure_up(svc)
    # Tiny pause so a freshly-restarted Flask process has time to bind to
    # its port before the test starts hitting the gateway.
    _time.sleep(0.5)
    yield
    # Bring everything back so the next test starts from a healthy cluster.
    for svc in _REQUIRED_SERVICES:
        _ensure_up(svc)
