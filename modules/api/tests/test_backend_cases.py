"""Backend test cases from docs/test-cases.md (TC-001 to TC-050, excluding UI cases).

Cases whose stage is not built yet (SP-04 to SP-08) import the module that will hold the stage. They fail with
ModuleNotFoundError until it exists. They are not skipped and not marked as expected failures.
"""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import yaml

from app.config import DOTENV_PATH, Settings, load_settings, settings_from_mapping
from app.db import database_url
from app.factory import create_app
from app.llm import prompts, stages
from app.repositories.news_snapshot import NewsSnapshotRepository
from app.repositories.refresh_status import STALE_MESSAGE, RefreshStatusRepository
from app.services import relevance
from app.services.refresh import (
    COMPLETED_MESSAGE,
    FAILED_MESSAGE,
    START_FAILED_MESSAGE,
    RefreshService,
    RefreshStartError,
    redact,
    worker_main,
)
from tests.conftest import make_engine

API_ROOT = Path(__file__).resolve().parents[1]
OWNER_PROMPTS = Path(__file__).resolve().parents[3] / "artifacts/intake/supporting/llm-prompts-workflow.md"


def status_repo(engine, row_id: int = 1) -> RefreshStatusRepository:
    return RefreshStatusRepository(engine, "refresh_status", row_id)


# ---- Stages not built yet (SP-04 to SP-08): fail until the module exists -------------------------------------

@pytest.mark.parametrize("case, module", [
    ("TC-001", "app.pipeline.fetch_rss"),
    ("TC-002", "app.pipeline.fetch_rss"),
    ("TC-003", "app.pipeline.fetch_google_news"),
    ("TC-004", "app.pipeline.fetch_searchapi"),
    ("TC-005", "app.pipeline.fetch_tavily"),
    ("TC-006", "app.pipeline.fetch_all"),
    ("TC-007", "app.services.noise"),
    ("TC-009", "app.services.dedupe"),
    ("TC-012", "app.services.dedupe"),
    ("TC-013", "app.services.dedupe"),
    ("TC-014", "app.services.freshness"),
    ("TC-015", "app.services.deal_tagging"),
    ("TC-016", "app.services.classify"),
    ("TC-017", "app.services.priority"),
    ("TC-018", "app.services.sort"),
    ("TC-019", "app.services.snapshot"),
    ("TC-020", "app.pipeline.runner"),
    ("TC-021", "app.services.article"),
    ("TC-022", "app.services.dates"),
    ("TC-032", "app.services.status_fallback"),
    ("TC-045", "app.evals.parity"),
    ("TC-046", "app.services.text_clean"),
])
def test_stage_not_built(case: str, module: str) -> None:
    """Fails until the stage module exists (SP-04 to SP-08 or the owner-required parity check)."""
    importlib.import_module(module)  # ModuleNotFoundError = not built


# ---- Stage 3 and 5 relevance (built) -------------------------------------------------------------------------

def stub(replies: list, log: list):
    queue = list(replies)

    def call(system, user, temperature, max_tokens):
        log.append({"system": system, "user": user, "temperature": temperature, "max_tokens": max_tokens})
        reply = queue.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply

    return call


def test_tc008_title_recheck_restores_and_blocks_never_restore_words() -> None:
    noise = [
        {"title": "Mergers announced in cloud sector", "summary": "x"},
        {"title": "Christmas gadget sale", "summary": "x"},
        {"title": "Chip firm raises funding", "summary": "x"},
    ]
    restored = relevance.title_recheck(noise, stub([json.dumps({"keep_indices": [0, 1, 2]})], []))
    assert [a["title"] for a in restored] == ["Mergers announced in cloud sector", "Chip firm raises funding"]
    deal = relevance.title_recheck([{"title": "Deal of the year in retail", "summary": "x"}],
                                   stub([json.dumps({"keep_indices": [0]})], []))
    assert deal == []  # "deal" in the title blocks restoration (DQ-006)


def test_tc008_title_recheck_failure_restores_nothing() -> None:
    noise = [{"title": "Mergers announced", "summary": "x"}]
    assert relevance.title_recheck(noise, stub(["no json here"], [])) == []
    assert relevance.title_recheck(noise, stub([RuntimeError("boom")], [])) == []


def test_tc010_relevance_gate_keep_drop_force_keep() -> None:
    items = [
        {"title": "Quarterly headline", "summary": "general news"},
        {"title": "Acquisition of a bank", "summary": "deal news"},
        {"title": "Garden show", "summary": "flowers"},
    ]
    kept = relevance.relevance_gate(items, stub([json.dumps({"keep_indices": [0]})], []))
    assert [a["title"] for a in kept] == ["Quarterly headline", "Acquisition of a bank"]
    dropped = relevance.relevance_gate([{"title": "Garden show", "summary": "flowers"}],
                                       stub([json.dumps({"keep_indices": []})], []))
    assert dropped == []


def test_tc011_relevance_gate_failure_keeps_batch() -> None:
    batch = [{"title": f"Plain title {i}", "summary": "plain"} for i in range(8)]
    assert len(relevance.relevance_gate(batch, stub([RuntimeError("timeout")], []))) == 8


def test_tc049_stage3_and_stage5_system_messages_are_the_owner_text() -> None:
    log: list = []
    relevance.title_recheck([{"title": "Mergers", "summary": "x"}], stub([json.dumps({"keep_indices": []})], log))
    relevance.relevance_gate([{"title": "Mergers", "summary": "x"}], stub([json.dumps({"keep_indices": []})], log))
    assert "TECHNOLOGY SERVICES COMPANY" in log[0]["system"]
    assert "IT / technology SERVICES company" in log[1]["system"]


def test_tc050_stage3_and_stage5_parameters() -> None:
    log: list = []
    relevance.title_recheck([{"title": "Mergers", "summary": "x"}], stub([json.dumps({"keep_indices": []})], log))
    relevance.relevance_gate([{"title": "Mergers", "summary": "x"}], stub([json.dumps({"keep_indices": []})], log))
    assert (log[0]["temperature"], log[0]["max_tokens"]) == (0.0, 150)
    assert (log[1]["temperature"], log[1]["max_tokens"]) == (0.0, 300)


def test_tc050_stage9_and_stage10_parameters() -> None:
    """Stage 9 and 10 modules are not built (SP-06). Fails until they exist."""
    importlib.import_module("app.services.deal_tagging")
    importlib.import_module("app.services.classify")


def test_tc048_prompts_are_verbatim_copies_of_the_owner_file() -> None:
    source = OWNER_PROMPTS.read_text(encoding="utf-8")
    names = sorted(p.name for p in prompts.PROMPTS_DIR.glob("*.txt"))
    assert len(names) == 9
    for name in names:
        assert prompts.load(name) in source, name


def test_tc048_an_edited_copy_is_detected(tmp_path: Path) -> None:
    source = OWNER_PROMPTS.read_text(encoding="utf-8")
    edited = prompts.load("b_relevance_gate_system.txt") + " "  # one changed character at the end
    assert edited not in source


def test_tc050_stage_parameters_match_section_17() -> None:
    assert (stages.STAGE_3.batch_size, stages.STAGE_3.max_tokens) == (6, 150)
    assert (stages.STAGE_5.batch_size, stages.STAGE_5.max_tokens) == (8, 300)
    assert (stages.STAGE_9.batch_size, stages.STAGE_9.max_tokens) == (8, 800)
    assert (stages.STAGE_10.batch_size, stages.STAGE_10.temperature) == (1, 0.2)


# ---- Refresh start, lock, stale lock, worker (built) --------------------------------------------------------

def test_tc025_second_start_returns_running_and_launches_no_second_worker(settings, clock_time) -> None:
    engine = make_engine()
    launches: list[int] = []
    service = RefreshService(status_repo(engine), settings, now=lambda: clock_time,
                             start_worker=lambda: launches.append(1))
    assert service.start() == "started"
    assert service.start() == "running"
    assert len(launches) == 1


def test_tc025_route_returns_started_then_running(settings, clock_time) -> None:
    engine = make_engine()
    service = RefreshService(status_repo(engine), settings, now=lambda: clock_time, start_worker=lambda: None)
    client = create_app(settings=settings, service=service, status_repository=status_repo(engine),
                        snapshot_repository=NewsSnapshotRepository(engine, "new_data")).test_client()
    first = client.post("/api/refresh")
    second = client.post("/api/refresh")
    assert first.status_code == 200 and first.get_json() == {"status": "started"}
    assert second.status_code == 200 and second.get_json() == {"status": "running"}


def test_tc026_start_failure_returns_500_and_records_failure(clock_time) -> None:
    engine = make_engine()
    secret_settings = Settings(refresh_stale_minutes=70, mysql_password="pw-secret-xyz")

    def boom() -> None:
        raise OSError("cannot start: password pw-secret-xyz rejected")

    service = RefreshService(status_repo(engine), secret_settings, now=lambda: clock_time, start_worker=boom)
    client = create_app(settings=secret_settings, service=service, status_repository=status_repo(engine),
                        snapshot_repository=NewsSnapshotRepository(engine, "new_data")).test_client()
    response = client.post("/api/refresh")
    assert response.status_code == 500
    assert response.get_data(as_text=True) == ""
    row = status_repo(engine).read()
    assert row["running"] == 0
    assert row["message"] == START_FAILED_MESSAGE
    assert "pw-secret-xyz" not in (row["trace"] or "")


def test_tc026a_stale_lock_cleared_at_72_minutes_not_at_69(settings, clock_time) -> None:
    engine = make_engine()
    repo = status_repo(engine)
    repo.try_acquire(clock_time)
    assert repo.clear_stale(clock_time + timedelta(minutes=69), clock_time + timedelta(minutes=69) - timedelta(minutes=70)) is False
    assert repo.read()["running"] == 1
    assert repo.clear_stale(clock_time + timedelta(minutes=72), clock_time + timedelta(minutes=72) - timedelta(minutes=70)) is True
    row = repo.read()
    assert row["running"] == 0
    assert row["message"] == STALE_MESSAGE


def test_tc027_status_route_shape_and_no_cache() -> None:
    engine = make_engine()
    client = create_app(settings=Settings(), status_repository=status_repo(engine),
                        snapshot_repository=NewsSnapshotRepository(engine, "new_data"),
                        service=RefreshService(status_repo(engine), Settings(), start_worker=lambda: None)).test_client()
    response = client.get("/api/refresh/status")
    body = response.get_json()
    assert response.status_code == 200
    assert set(body) == {"running", "started_at", "finished_at", "message", "last_run_type"}
    assert response.headers["Cache-Control"] == "no-cache"


def test_tc028_subprocess_by_default_webjob_only_when_url_set(settings, clock_time) -> None:
    engine = make_engine()
    launches: list[int] = []
    calls: list[tuple] = []
    RefreshService(status_repo(engine), settings, now=lambda: clock_time,
                   start_worker=lambda: launches.append(1),
                   trigger_webjob=lambda *a: calls.append(a)).start()
    assert (len(launches), len(calls)) == (1, 0)
    engine2 = make_engine()
    web = Settings(refresh_stale_minutes=70, azure_webjob_trigger_url="https://example.invalid/t",
                   azure_webjob_user="u", azure_webjob_pass="p")
    launches2: list[int] = []
    calls2: list[tuple] = []
    RefreshService(status_repo(engine2), web, now=lambda: clock_time,
                   start_worker=lambda: launches2.append(1),
                   trigger_webjob=lambda *a: calls2.append(a)).start()
    assert (len(launches2), len(calls2)) == (0, 1)
    assert calls2[0] == ("https://example.invalid/t", "u", "p")


def test_tc029_worker_success_clears_flag_with_message() -> None:
    engine = make_engine(status_running=1)
    code = worker_main(Settings(), status_repo(engine), now=lambda: datetime(2026, 10, 13, 13, 0), pipeline=lambda: None)
    row = status_repo(engine).read()
    assert code == 0
    assert row["running"] == 0 and row["finished_at"] is not None and row["message"] == COMPLETED_MESSAGE


def test_tc029_worker_failure_still_clears_flag_and_writes_trace() -> None:
    engine = make_engine(status_running=1)

    def pipeline() -> None:
        raise RuntimeError("pipeline failed with password pw-secret-xyz")

    code = worker_main(Settings(mysql_password="pw-secret-xyz"), status_repo(engine),
                       now=lambda: datetime(2026, 10, 13, 13, 0), pipeline=pipeline)
    row = status_repo(engine).read()
    assert code == 1
    assert row["running"] == 0 and row["message"] == FAILED_MESSAGE
    assert "pw-secret-xyz" not in row["trace"]


def test_tc030_creating_the_app_fetches_nothing() -> None:
    engine = make_engine([[{"title": "Stored", "summary": "s"}]])
    create_app(settings=Settings(), status_repository=status_repo(engine),
               snapshot_repository=NewsSnapshotRepository(engine, "new_data"),
               service=RefreshService(status_repo(engine), Settings(), start_worker=lambda: None))
    assert "app.services.refresh" in __import__("sys").modules  # module graph has no fetch adapters at start
    assert all(not name.startswith("app.pipeline") for name in __import__("sys").modules)


def test_tc031_settings_come_from_dotenv_and_no_secret_is_in_source(tmp_path: Path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("MYSQL_HOST=db.local\nMYSQL_PASSWORD=test-only-value-123\n", encoding="utf-8")
    monkeypatch.delenv("MYSQL_HOST", raising=False)
    monkeypatch.delenv("MYSQL_PASSWORD", raising=False)
    settings = load_settings(env_file)
    assert settings.mysql_host == "db.local"
    assert settings.mysql_password == "test-only-value-123"
    for path in API_ROOT.rglob("*.py"):
        if path.name == "test_backend_cases.py":
            continue
        assert "test-only-value-123" not in path.read_text(encoding="utf-8"), path


def test_tc033_migration_seeds_ready_row() -> None:
    result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
                            cwd=API_ROOT, capture_output=True, text=True, check=True)
    assert "INSERT INTO refresh_status" in result.stdout and "'Ready'" in result.stdout


def test_tc034_database_is_news_app_by_default() -> None:
    assert Settings().mysql_database == "news_app"
    assert "news_app" in str(database_url(Settings(mysql_host="h", mysql_user="u", mysql_password="p")))


def test_tc043_secret_is_masked_in_trace() -> None:
    masked = redact("failed with key test-only-key-999", Settings(tavily_api_key="test-only-key-999"))
    assert "test-only-key-999" not in masked and "***" in masked


def test_tc044_coverage_floor_is_70_percent() -> None:
    config = yaml.safe_load((API_ROOT.parents[1] / ".claude/config.yaml").read_text(encoding="utf-8"))
    assert config["quality_gates"]["api_unit_line_coverage_min"] == 0.70


def test_tc047_routes_answer_without_authentication() -> None:
    engine = make_engine()
    client = create_app(settings=Settings(), status_repository=status_repo(engine),
                        snapshot_repository=NewsSnapshotRepository(engine, "new_data"),
                        service=RefreshService(status_repo(engine), Settings(), start_worker=lambda: None)).test_client()
    assert client.get("/api/news").status_code == 200
    assert client.get("/api/refresh/status").status_code == 200
    assert client.post("/api/refresh").status_code == 200


def test_tc023_news_route_empty_and_stored_snapshot() -> None:
    empty = make_engine()
    client = create_app(settings=Settings(), status_repository=status_repo(empty),
                        snapshot_repository=NewsSnapshotRepository(empty, "new_data"),
                        service=RefreshService(status_repo(empty), Settings(), start_worker=lambda: None)).test_client()
    body = client.get("/api/news").get_json()
    assert body == {"count": 0, "results": [], "fetched_at": None}
    stored = make_engine([[{"title": "A"}, {"title": "B"}]])
    client2 = create_app(settings=Settings(), status_repository=status_repo(stored),
                         snapshot_repository=NewsSnapshotRepository(stored, "new_data"),
                         service=RefreshService(status_repo(stored), Settings(), start_worker=lambda: None)).test_client()
    response = client2.get("/api/news")
    body2 = response.get_json()
    assert body2["count"] == 2 and len(body2["results"]) == 2
    assert response.headers["Cache-Control"] == "no-cache"


def test_tc024_health_returns_ok() -> None:
    client = create_app(settings=Settings(), status_repository=status_repo(make_engine()),
                        snapshot_repository=NewsSnapshotRepository(make_engine(), "new_data"),
                        service=RefreshService(status_repo(make_engine()), Settings(), start_worker=lambda: None)).test_client()
    response = client.get("/health")
    assert response.status_code == 200 and response.mimetype == "text/plain"
    assert response.get_data(as_text=True) == "OK"


@pytest.mark.skip(reason="blocked: owner must record evals/product/baseline.md (TC-045b, DQ-019)")
def test_tc045b_parity_baseline_recorded() -> None:
    raise AssertionError("blocked")
