"""UI test cases from docs/test-cases.md (TC-035 to TC-041), run in Microsoft Edge with Python Playwright.

Deviation: config.yaml names `npx playwright test`. The Node Playwright package is not installed here and the
network blocks installing it. These cases run through Python Playwright instead; the cases and checks are unchanged.
"""

from __future__ import annotations

import threading
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page, sync_playwright
from sqlalchemy import text
from werkzeug.serving import make_server

from app.config import Settings
from app.factory import create_app
from app.repositories.news_snapshot import NewsSnapshotRepository
from app.repositories.refresh_status import RefreshStatusRepository
from app.services.refresh import RefreshService
from tests.conftest import make_engine

EDGE = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")

ARTICLES = [
    {"title": "Tech Mahindra and Infinite Uptime scale physical AI", "link": "https://example.com/a",
     "source": "[Source A]", "published": "2026-09-30 16:11:00",
     "summary": "Tech Mahindra has partnered with Infinite Uptime to scale physical AI. " * 6,
     "domain": "Technology & Communication", "priority": 5, "deal_categories": ["partnerships"],
     "is_deal_news": True, "is_google_news": False, "published_at": "2026-09-30 16:11:00"},
    {"title": "Retailer completes acquisition of logistics firm", "link": "https://example.com/b",
     "source": "[Source B]", "published": "2026-10-09 08:57:00", "summary": "Short summary.",
     "domain": "Retail", "priority": 4, "deal_categories": ["mergers_acquisitions"],
     "is_deal_news": True, "is_google_news": True, "published_at": "2026-10-09 08:57:00"},
    {"title": "Bank and fintech form joint venture", "link": "https://example.com/c",
     "source": "[Source C]", "published": "2026-10-07 04:24:00", "summary": "Two firms create a new company.",
     "domain": "Banking and Financial Services", "priority": 3,
     "deal_categories": ["partnerships", "joint_ventures"], "is_deal_news": True, "is_google_news": False,
     "published_at": "2026-10-07 04:24:00"},
    {"title": "Cloud platform update", "link": "https://example.com/d", "source": "[Source D]",
     "published": "2026-10-01 10:00:00", "summary": "Plain update.", "domain": "Technology & Communication",
     "priority": 2, "deal_categories": [], "is_deal_news": False, "is_google_news": False,
     "published_at": "2026-10-01 10:00:00"},
]


class BrokenSnapshots:
    def latest(self):
        raise RuntimeError("database unavailable")


def build_app(snapshot_rows, broken: bool = False, worker_seconds: float = 0.0):
    """Create the app over the SQLite copy. worker_seconds > 0 makes the worker stub finish later."""
    import threading as _t

    engine = make_engine([snapshot_rows] if snapshot_rows is not None else None)
    status = RefreshStatusRepository(engine, "refresh_status", 1)
    snapshots = BrokenSnapshots() if broken else NewsSnapshotRepository(engine, "new_data")
    settings = Settings(refresh_stale_minutes=70)

    def fake_worker() -> None:
        if worker_seconds:
            _t.Timer(worker_seconds, lambda: status.finish(datetime(2026, 10, 13, 13, 0), "Refresh completed.", None)).start()

    service = RefreshService(status, settings, start_worker=fake_worker)
    return create_app(settings=settings, service=service, status_repository=status, snapshot_repository=snapshots)


class Server:
    def __init__(self, app, port: int) -> None:
        self.server = make_server("127.0.0.1", port, app)
        self.url = f"http://127.0.0.1:{port}/"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def stop(self) -> None:
        self.server.shutdown()


@pytest.fixture(scope="module")
def browser() -> Iterator[Browser]:
    if not EDGE.exists():
        raise RuntimeError(f"Microsoft Edge not found at {EDGE}")
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EDGE))
        yield browser
        browser.close()


def open_page(browser: Browser, url: str) -> tuple[Page, list[str]]:
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    errors: list[str] = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.goto(url)
    return page, errors


@pytest.fixture(scope="module")
def grid_server() -> Iterator[Server]:
    server = Server(build_app(ARTICLES), 5201)
    yield server
    server.stop()


def test_tc035_index_title_footer_and_no_insight(browser: Browser, grid_server: Server) -> None:
    page, errors = open_page(browser, grid_server.url)
    page.wait_for_selector(".card")
    assert page.title() == "Latest Tech News"
    assert page.inner_text("footer").strip() == "Copyright 2025 UST"
    assert page.locator(".card").count() == 4
    assert "Insight" not in page.content()
    assert "UST Relevant" not in page.content()
    assert not errors


def test_tc036_sort_control_has_two_options_and_date_order(browser: Browser, grid_server: Server) -> None:
    page, _ = open_page(browser, grid_server.url)
    page.wait_for_selector(".card")
    options = page.locator("#sort option").all_inner_texts()
    assert options == ["Priority (High to Low)", "Date (Newest to Oldest)"]
    page.select_option("#sort", "date")
    assert page.locator(".card h2").first.inner_text().startswith("Retailer")


def test_tc037_domain_filter_all_and_five_domains(browser: Browser, grid_server: Server) -> None:
    page, _ = open_page(browser, grid_server.url)
    page.wait_for_selector(".card")
    options = page.locator("#domain option").all_inner_texts()
    assert options == [
        "All", "Healthcare", "Retail", "Banking and Financial Services",
        "Technology & Communication", "Wealth & Asset Management",
    ]
    page.select_option("#domain", "Retail")
    assert page.locator(".card").count() == 1


def test_tc038_deal_chips_with_counts_and_clear_filter(browser: Browser, grid_server: Server) -> None:
    page, _ = open_page(browser, grid_server.url)
    page.wait_for_selector(".chip")
    assert page.locator(".chip").count() == 6
    assert "Partnerships (2)" in page.inner_text("#deal-chips")
    page.click("text=Partnerships (2)")
    assert page.locator(".card").count() == 2
    page.click("#clear-deal")
    assert page.locator(".card").count() == 4


def test_tc039_refresh_message_polling_and_reload(browser: Browser) -> None:
    server = Server(build_app([], worker_seconds=2.0), 5202)
    try:
        page, _ = open_page(browser, server.url)
        page.wait_for_selector("#empty:not([hidden])")
        page.click("#refresh")
        page.wait_for_selector("#notice:has-text('Refreshing news')")
        assert page.inner_text("#notice") == "Refreshing news - this may take a while..."
        page.wait_for_selector("#refresh:not([disabled])", timeout=20000)
        assert page.inner_text("#notice") == ""
    finally:
        server.stop()


def test_tc040_empty_state_no_news_found(browser: Browser) -> None:
    server = Server(build_app([]), 5203)
    try:
        page, _ = open_page(browser, server.url)
        page.wait_for_selector("#empty:not([hidden])")
        assert page.inner_text("#empty") == "No news found"
        assert page.locator(".card").count() == 0
    finally:
        server.stop()


def test_tc041_load_failure_shows_connection_message(browser: Browser) -> None:
    server = Server(build_app(None, broken=True), 5204)
    try:
        page, _ = open_page(browser, server.url)
        page.wait_for_selector("#notice:not([hidden])")
        assert page.inner_text("#notice") == "No news loaded, check your connection"
    finally:
        server.stop()
