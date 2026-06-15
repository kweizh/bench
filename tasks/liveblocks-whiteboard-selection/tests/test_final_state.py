"""Final-state verification for the liveblocks-whiteboard-selection task.

Uses pytest-xprocess to boot the Next.js dev server and Playwright to drive
two concurrent browser contexts that simulate two distinct users joining the
same Liveblocks room. The test asserts that one user's `Presence`-driven
shape selection is propagated through the real Liveblocks cloud and rendered
as a per-user selection ring in the other user's DOM.
"""

import os
import socket
import time

import pytest
from xprocess import ProcessStarter
from playwright.sync_api import sync_playwright, expect

PROJECT_DIR = "/home/user/whiteboard"
BASE_URL = "http://localhost:3000"
USER1_COLOR = "#DC2626"  # red

SHAPE_SELECTOR = '[data-testid="shape"]'
SHAPE_IDS = ("shape-a", "shape-b", "shape-c")


def _wait_for_port(host: str, port: int, timeout: float = 180.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex((host, port)) == 0:
                return True
        time.sleep(1)
    return False


@pytest.fixture(scope="session")
def liveblocks_config_exists():
    cfg = os.path.join(PROJECT_DIR, "liveblocks.config.ts")
    assert os.path.isfile(cfg), (
        f"liveblocks.config.ts must exist at {cfg} after the agent's work."
    )
    with open(cfg, "r", encoding="utf-8") as f:
        text = f.read()
    assert "selectedShapeId" in text, (
        "liveblocks.config.ts must declare 'selectedShapeId' in Presence."
    )
    assert "LiveList" in text, (
        "liveblocks.config.ts must use LiveList in Storage.shapes."
    )
    return cfg


@pytest.fixture(scope="session")
def start_app(xprocess):
    class Starter(ProcessStarter):
        name = "whiteboard_dev"
        args = ["npm", "run", "dev"]
        env = os.environ.copy()
        popen_kwargs = {
            "cwd": PROJECT_DIR,
            "text": True,
        }
        timeout = 240
        terminate_on_interrupt = True

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("localhost", 3000)) == 0

    xprocess.ensure(Starter.name, Starter)

    # Wait until the page responds (Next.js sometimes binds port before ready).
    assert _wait_for_port("localhost", 3000, timeout=240), (
        "Next.js dev server did not become ready on port 3000."
    )
    # Give Next.js a moment to compile the first page.
    time.sleep(3)

    yield

    info = xprocess.getinfo(Starter.name)
    info.terminate()


def _wait_for_shapes(page, timeout_ms: int = 30000):
    page.wait_for_selector(SHAPE_SELECTOR, timeout=timeout_ms)
    # Wait until all three shapes appear.
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        ids = page.eval_on_selector_all(
            SHAPE_SELECTOR,
            "els => els.map(e => e.getAttribute('data-shape-id'))",
        )
        if set(ids) >= set(SHAPE_IDS):
            return
        time.sleep(0.5)
    raise AssertionError(
        f"Expected shapes {SHAPE_IDS} to render; last seen={ids}"
    )


def _ring_count_for_shape(page, shape_id: str, color: str) -> int:
    selector = (
        '[data-testid="selection-ring"]'
        f'[data-selection-shape-id="{shape_id}"]'
        f'[data-selection-color="{color}"]'
    )
    return page.locator(selector).count()


def _wait_for_ring(page, shape_id: str, color: str, timeout: float = 20.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _ring_count_for_shape(page, shape_id, color) >= 1:
            return
        time.sleep(0.5)
    raise AssertionError(
        f"Other user did not see a selection ring on {shape_id} "
        f"with color {color} within {timeout}s."
    )


def _wait_for_no_ring(page, shape_id: str, color: str, timeout: float = 20.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _ring_count_for_shape(page, shape_id, color) == 0:
            return
        time.sleep(0.5)
    raise AssertionError(
        f"Selection ring on {shape_id} ({color}) did not disappear "
        f"within {timeout}s."
    )


def _wait_for_no_any_ring(page, timeout: float = 20.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if page.locator('[data-testid="selection-ring"]').count() == 0:
            return
        time.sleep(0.5)
    raise AssertionError(
        f"All selection rings did not disappear within {timeout}s."
    )


def test_single_context_renders_three_shapes(start_app, liveblocks_config_exists):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            ctx = browser.new_context()
            page = ctx.new_page()
            page.goto(f"{BASE_URL}/?user=1", wait_until="domcontentloaded")
            _wait_for_shapes(page)
            ids = page.eval_on_selector_all(
                SHAPE_SELECTOR,
                "els => els.map(e => e.getAttribute('data-shape-id'))",
            )
            assert set(ids) == set(SHAPE_IDS), (
                f"Expected exactly shapes {SHAPE_IDS} to render, got {ids}."
            )
            ctx.close()
        finally:
            browser.close()


def test_cross_user_selection_via_presence(start_app, liveblocks_config_exists):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            ctx_a = browser.new_context()
            ctx_b = browser.new_context()
            page_a = ctx_a.new_page()
            page_b = ctx_b.new_page()

            page_a.goto(f"{BASE_URL}/?user=1", wait_until="domcontentloaded")
            page_b.goto(f"{BASE_URL}/?user=2", wait_until="domcontentloaded")

            _wait_for_shapes(page_a)
            _wait_for_shapes(page_b)

            # Give Liveblocks time to establish presence on both clients.
            time.sleep(2)

            # A clicks shape-b; B should see a red selection ring on shape-b.
            page_a.click(f'[data-shape-id="shape-b"]')
            _wait_for_ring(page_b, "shape-b", USER1_COLOR, timeout=20.0)

            # A then clicks shape-c; B should see the ring move.
            page_a.click(f'[data-shape-id="shape-c"]')
            _wait_for_no_ring(page_b, "shape-b", USER1_COLOR, timeout=20.0)
            _wait_for_ring(page_b, "shape-c", USER1_COLOR, timeout=20.0)

            # A clicks the empty SVG canvas background; B should see no rings.
            svg = page_a.locator("svg").first
            svg.click(position={"x": 5, "y": 5})
            _wait_for_no_any_ring(page_b, timeout=20.0)

            ctx_a.close()
            ctx_b.close()
        finally:
            browser.close()


def test_storage_does_not_carry_selection_attribute(
    start_app, liveblocks_config_exists
):
    """Selection must be Presence-only — shapes themselves must not be
    annotated with a storage-driven selection attribute."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            ctx = browser.new_context()
            page = ctx.new_page()
            page.goto(f"{BASE_URL}/?user=1", wait_until="domcontentloaded")
            _wait_for_shapes(page)
            page.click(f'[data-shape-id="shape-a"]')
            time.sleep(1.5)
            offenders = page.eval_on_selector_all(
                SHAPE_SELECTOR,
                "els => els.filter(e => e.hasAttribute('data-storage-selected'))"
                ".map(e => e.getAttribute('data-shape-id'))",
            )
            assert offenders == [], (
                "Shapes must not carry data-storage-selected; selection must "
                f"live in Presence only. Offending shapes: {offenders}"
            )
            ctx.close()
        finally:
            browser.close()
