"""Refresh start and worker logic (FR-035, FR-036, FR-039, FR-040; BR-015, BR-016; NFR-004, NFR-006).

Start order: clear a stale lock, take the atomic lock, then start the worker: the WebJob when
AZURE_WEBJOB_TRIGGER_URL is set (FR-039), otherwise refresh_worker.py as a subprocess.
If the start fails after the lock is taken, the failure is recorded and the lock is released (FR-036).
"""

from __future__ import annotations

import subprocess
import sys
import traceback
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Protocol

import requests

from app.config import Settings, load_settings
from app.db import make_engine
from app.repositories.refresh_status import RefreshStatusRepository

API_ROOT: Path = Path(__file__).resolve().parents[2]  # modules/api
WORKER_PATH: Path = API_ROOT / "refresh_worker.py"
WEBJOB_TIMEOUT_SECONDS: float = 30.0  # request timeout for the optional WebJob call

IST: timezone = timezone(timedelta(hours=5, minutes=30))  # IST, fixed offset (NFR-003)

START_FAILED_MESSAGE: str = "Refresh could not be started."
COMPLETED_MESSAGE: str = "Refresh completed."
FAILED_MESSAGE: str = "Refresh failed."


def ist_now() -> datetime:
    """Current time in IST as a naive datetime, the form stored in the status row."""
    return datetime.now(IST).replace(tzinfo=None)


class RefreshRepository(Protocol):
    """The part of the status repository the service uses. Tests can supply another object."""

    def clear_stale(self, now: datetime, cutoff: datetime) -> bool: ...

    def try_acquire(self, now: datetime) -> bool: ...

    def finish(self, now: datetime, message: str | None, trace: str | None = None) -> None: ...


class RefreshStartError(RuntimeError):
    """Raised when a refresh could not be started. The route turns it into HTTP 500 (FR-036)."""


def redact(text: str, settings: Settings) -> str:
    """Replace every configured secret value in text with *** (NFR-006)."""
    secrets = (
        settings.mysql_password,
        settings.searchapi_io_key,
        settings.tavily_api_key,
        settings.azure_openai_chat_api_key,
        settings.azure_openai_embed_api_key,
        settings.azure_webjob_pass,
    )
    for secret in secrets:
        if secret:
            text = text.replace(secret, "***")
    return text


def launch_worker(worker_path: Path = WORKER_PATH, cwd: Path = API_ROOT) -> None:
    """Start refresh_worker.py as a subprocess and return without waiting (FR-039)."""
    subprocess.Popen(
        [sys.executable, str(worker_path)],
        cwd=str(cwd),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
    )


def call_webjob(url: str, user: str, password: str) -> None:
    """Trigger the optional Azure WebJob (FR-039). Raises when the call fails."""
    response = requests.post(url, auth=(user, password), timeout=WEBJOB_TIMEOUT_SECONDS)
    response.raise_for_status()


class RefreshService:
    """Starts a refresh. Returns "started" or "running"; raises RefreshStartError on failure."""

    def __init__(
        self,
        repository: RefreshRepository,
        settings: Settings,
        *,
        now: Callable[[], datetime] = ist_now,
        start_worker: Callable[[], None] = launch_worker,
        trigger_webjob: Callable[[str, str, str], None] = call_webjob,
    ) -> None:
        self._repository = repository
        self._settings = settings
        self._now = now
        self._start_worker = start_worker
        self._trigger_webjob = trigger_webjob

    def start(self) -> str:
        """Start a refresh unless one is running (BR-015). Returns "started" or "running"."""
        current = self._now()
        cutoff = current - timedelta(minutes=self._settings.refresh_stale_minutes)
        self._repository.clear_stale(current, cutoff)  # BR-016: no-op when no stale lock

        if not self._repository.try_acquire(current):
            return "running"  # BR-015: another caller holds the lock

        try:
            if self._settings.webjob_enabled:
                self._trigger_webjob(
                    self._settings.azure_webjob_trigger_url,
                    self._settings.azure_webjob_user,
                    self._settings.azure_webjob_pass,
                )
            else:
                self._start_worker()
        except Exception as exc:
            # FR-036: record the failure and release the lock; the route returns HTTP 500.
            self._repository.finish(
                self._now(),
                START_FAILED_MESSAGE,
                redact(f"{type(exc).__name__}: {exc}", self._settings),
            )
            raise RefreshStartError("refresh could not be started") from exc
        return "started"


def run_refresh_pipeline() -> None:
    """Pipeline entry point. The stages are built in SP-04 to SP-08; until then this fails clearly."""
    raise NotImplementedError("The refresh pipeline stages are built in SP-04 to SP-08.")


def worker_main(
    settings: Settings | None = None,
    repository: RefreshRepository | None = None,
    *,
    now: Callable[[], datetime] = ist_now,
    pipeline: Callable[[], None] = run_refresh_pipeline,
) -> int:
    """Run one refresh and always clear the running flag at the end (FR-040). Returns the exit code."""
    settings = settings if settings is not None else load_settings()
    if repository is None:
        repository = RefreshStatusRepository(
            make_engine(settings),
            settings.refresh_status_table,
            settings.refresh_status_row_id,
        )
    try:
        pipeline()
    except Exception:
        repository.finish(now(), FAILED_MESSAGE, redact(traceback.format_exc(), settings))
        return 1
    repository.finish(now(), COMPLETED_MESSAGE, None)
    return 0
