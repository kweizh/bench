import json
import os
import socket
import time
import uuid

import pytest
import requests
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/myproject"
APP_URL = "http://localhost:3000"


def _wait_for_port(host: str, port: int, timeout: float = 120.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                if s.connect_ex((host, port)) == 0:
                    return True
            except OSError:
                pass
        time.sleep(1.0)
    return False


def _wait_for_http_ok(url: str, timeout: float = 120.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code < 500:
                return True
        except Exception:
            pass
        time.sleep(1.0)
    return False


@pytest.fixture(scope="session")
def run_id() -> str:
    rid = os.environ.get("ZEALT_RUN_ID")
    assert rid, "ZEALT_RUN_ID env var must be set for verification."
    return rid


@pytest.fixture(scope="session")
def room_id(run_id: str) -> str:
    return f"liveblocks-drawing-{run_id}"


@pytest.fixture(scope="session", autouse=True)
def reset_room(room_id: str):
    """Best-effort cleanup of the Liveblocks room before verification."""
    secret = os.environ.get("LIVEBLOCKS_SECRET_KEY")
    if secret:
        try:
            requests.delete(
                f"https://api.liveblocks.io/v2/rooms/{room_id}",
                headers={"Authorization": f"Bearer {secret}"},
                timeout=10,
            )
        except Exception:
            pass
    yield


@pytest.fixture(scope="session")
def start_app(xprocess):
    class Starter(ProcessStarter):
        name = "drawing_app"
        args = ["npm", "run", "dev"]
        env = os.environ.copy()
        popen_kwargs = {"cwd": PROJECT_DIR, "text": True}
        timeout = 240
        terminate_on_interrupt = True

        def startup_check(self):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    if s.connect_ex(("localhost", 3000)) != 0:
                        return False
                r = requests.get(f"{APP_URL}/?user=warmup", timeout=5)
                return r.status_code < 500
            except Exception:
                return False

    xprocess.ensure(Starter.name, Starter)
    # Give Next.js a few extra seconds to fully compile the page.
    time.sleep(3)
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()


def _open_two_contexts(playwright):
    browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
    ctx_a = browser.new_context(viewport={"width": 1280, "height": 800})
    ctx_b = browser.new_context(viewport={"width": 1280, "height": 800})
    page_a = ctx_a.new_page()
    page_b = ctx_b.new_page()
    return browser, ctx_a, ctx_b, page_a, page_b


def _wait_selector(page, selector: str, timeout: int = 30000):
    page.wait_for_selector(selector, timeout=timeout, state="attached")


def _draw_stroke(page, points):
    """Dispatch a pointerdown/move(s)/up sequence on the canvas at the given page coords."""
    canvas = page.locator('[data-testid="canvas"]')
    box = canvas.bounding_box()
    assert box is not None, "Canvas must have a bounding box."

    def _abs(p):
        return (box["x"] + p[0], box["y"] + p[1])

    x0, y0 = _abs(points[0])
    page.mouse.move(x0, y0)
    page.mouse.down()
    for p in points[1:]:
        xa, ya = _abs(p)
        page.mouse.move(xa, ya, steps=2)
        time.sleep(0.05)
    page.mouse.up()


def _select_pen(page):
    page.locator('[data-testid="tool-pen"]').click()


def _select_eraser(page):
    page.locator('[data-testid="tool-eraser"]').click()


def _set_color(page, color: str):
    picker = page.locator('[data-testid="color-picker"]')
    tag = picker.evaluate("el => el.tagName.toLowerCase()")
    if tag == "input":
        picker.fill(color)
        picker.evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); }", color)
    elif tag == "select":
        picker.select_option(color)
    else:
        # Custom element: try clicking child option with data-color matching value
        option = page.locator(f'[data-testid="color-picker"] [data-color="{color}"]')
        if option.count() > 0:
            option.first.click()


def _set_width(page, width: int):
    picker = page.locator('[data-testid="width-picker"]')
    tag = picker.evaluate("el => el.tagName.toLowerCase()")
    if tag == "input":
        picker.evaluate("(el, v) => { el.value = String(v); el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); }", str(width))
    elif tag == "select":
        picker.select_option(str(width))


def _polylines(page):
    return page.locator('[data-testid="canvas"] polyline[data-stroke-id]')


def test_dependencies_declared_and_no_mock():
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    with open(pkg_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    deps = {}
    deps.update(data.get("dependencies", {}))
    deps.update(data.get("devDependencies", {}))
    for required in ["@liveblocks/client", "@liveblocks/react", "@liveblocks/node"]:
        assert required in deps, f"package.json must declare {required} (no mocking allowed)."

    # No mock or fake of @liveblocks/client anywhere in user source files.
    forbidden_tokens = [
        'jest.mock("@liveblocks/client"',
        "jest.mock('@liveblocks/client'",
        'vi.mock("@liveblocks/client"',
        "vi.mock('@liveblocks/client'",
    ]
    for root, _dirs, files in os.walk(PROJECT_DIR):
        rel = os.path.relpath(root, PROJECT_DIR)
        if rel.startswith("node_modules") or rel.startswith(".next") or rel.startswith(".git"):
            continue
        for fn in files:
            if not fn.endswith((".ts", ".tsx", ".js", ".jsx")):
                continue
            path = os.path.join(root, fn)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    txt = fh.read()
            except Exception:
                continue
            for tok in forbidden_tokens:
                assert tok not in txt, f"Mocking the Liveblocks client is forbidden ({tok} in {path})."


def test_static_page_contract(start_app):
    assert _wait_for_http_ok(f"{APP_URL}/?user=alice", timeout=180), "Next.js app did not become ready."
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(f"{APP_URL}/?user=alice")
        for testid in ["canvas", "color-picker", "width-picker", "tool-pen", "tool-eraser", "undo-mine"]:
            _wait_selector(page, f'[data-testid="{testid}"]')
        canvas_box = page.locator('[data-testid="canvas"]').bounding_box()
        assert canvas_box is not None, "Canvas must be rendered with bounding box."
        assert canvas_box["width"] >= 800 and canvas_box["height"] >= 600, (
            f"Canvas must be at least 800x600, got {canvas_box}"
        )
        tag = page.locator('[data-testid="canvas"]').evaluate("el => el.tagName.toLowerCase()")
        assert tag == "svg", f"Canvas must be an <svg> element, got <{tag}>."
        browser.close()


def test_collaborative_stroke_propagation_and_eraser_and_undo(start_app, room_id):
    assert _wait_for_http_ok(f"{APP_URL}/?user=alice", timeout=180), "Next.js app did not become ready."
    from playwright.sync_api import sync_playwright

    unique_a = f"alice-{uuid.uuid4().hex[:6]}"
    unique_b = f"bob-{uuid.uuid4().hex[:6]}"

    with sync_playwright() as p:
        browser, ctx_a, ctx_b, page_a, page_b = _open_two_contexts(p)
        try:
            page_a.goto(f"{APP_URL}/?user={unique_a}")
            page_b.goto(f"{APP_URL}/?user={unique_b}")
            _wait_selector(page_a, '[data-testid="canvas"]')
            _wait_selector(page_b, '[data-testid="canvas"]')
            # Allow connection to room.
            time.sleep(3)

            # --- Scenario 1: A draws a stroke, B sees it. ---
            _select_pen(page_a)
            _set_color(page_a, "#ff0000")
            _set_width(page_a, 6)
            _draw_stroke(page_a, [(120, 120), (160, 160), (200, 200), (240, 240), (280, 280)])
            # Wait for propagation.
            deadline = time.time() + 10
            propagated = False
            while time.time() < deadline:
                if page_b.locator(f'[data-testid="canvas"] polyline[data-user-id="{unique_a}"]').count() >= 1:
                    propagated = True
                    break
                time.sleep(0.5)
            assert propagated, "Bob's canvas did not receive Alice's stroke within 10 seconds."

            poly_b = page_b.locator(f'[data-testid="canvas"] polyline[data-user-id="{unique_a}"]').first
            stroke_id = poly_b.get_attribute("data-stroke-id")
            assert stroke_id, "Replicated polyline must have a data-stroke-id attribute."

            points_attr = poly_b.get_attribute("points") or ""
            # Count coordinate pairs.
            pairs = [pp for pp in points_attr.replace(",", " ").split() if pp.strip()]
            num_pairs = len(pairs) // 2
            assert num_pairs >= 2, f"Polyline must contain at least 2 points, got {num_pairs} (points={points_attr!r})."
            # Throttling: with ~5 pointer events ~50ms apart and 30ms throttle, expect at most ~8 points
            # (allow some slack for rapid movements). Below 30 is the loose upper bound.
            assert num_pairs <= 30, (
                f"Polyline contains too many points ({num_pairs}); throttling appears to be missing."
            )

            # --- Scenario 2: B uses eraser on A's stroke. ---
            _select_eraser(page_b)
            page_b.locator(f'[data-testid="canvas"] polyline[data-stroke-id="{stroke_id}"]').first.click(force=True)
            deadline = time.time() + 10
            erased_in_a = False
            erased_in_b = False
            while time.time() < deadline:
                erased_in_b = page_b.locator(f'[data-testid="canvas"] polyline[data-stroke-id="{stroke_id}"]').count() == 0
                erased_in_a = page_a.locator(f'[data-testid="canvas"] polyline[data-stroke-id="{stroke_id}"]').count() == 0
                if erased_in_a and erased_in_b:
                    break
                time.sleep(0.5)
            assert erased_in_b, "Bob's eraser click did not remove the stroke locally."
            assert erased_in_a, "Bob's eraser did not propagate to Alice's canvas."

            # --- Scenario 3: Undo my last stroke (only affects current user's latest stroke). ---
            _select_pen(page_a)
            _set_color(page_a, "#0000ff")
            _set_width(page_a, 4)
            _draw_stroke(page_a, [(50, 50), (100, 100), (150, 150)])
            time.sleep(1.0)

            _select_pen(page_b)
            _set_color(page_b, "#00aa00")
            _set_width(page_b, 4)
            _draw_stroke(page_b, [(300, 300), (320, 320), (350, 350)])
            time.sleep(1.0)

            _set_color(page_a, "#aa00aa")
            _draw_stroke(page_a, [(400, 100), (450, 100), (500, 100)])

            # Wait for all three strokes to be visible in B.
            deadline = time.time() + 10
            while time.time() < deadline:
                if (
                    page_b.locator(f'[data-testid="canvas"] polyline[data-user-id="{unique_a}"]').count() >= 2
                    and page_b.locator(f'[data-testid="canvas"] polyline[data-user-id="{unique_b}"]').count() >= 1
                ):
                    break
                time.sleep(0.5)

            alice_polys = page_a.locator(f'[data-testid="canvas"] polyline[data-user-id="{unique_a}"]')
            assert alice_polys.count() >= 2, (
                f"Expected at least 2 of Alice's strokes after drawing; got {alice_polys.count()}."
            )
            # Record current alice stroke ids (in DOM order = creation order for the LiveList).
            alice_ids_before = [alice_polys.nth(i).get_attribute("data-stroke-id") for i in range(alice_polys.count())]
            # Assume DOM order matches LiveList push order (newest last).
            newest_alice = alice_ids_before[-1]
            older_alice = alice_ids_before[-2]

            bob_polys = page_b.locator(f'[data-testid="canvas"] polyline[data-user-id="{unique_b}"]')
            assert bob_polys.count() >= 1, "Bob's stroke must be visible."
            bob_id = bob_polys.first.get_attribute("data-stroke-id")

            # Click undo in Alice.
            page_a.locator('[data-testid="undo-mine"]').click()
            deadline = time.time() + 10
            success = False
            while time.time() < deadline:
                in_a_newest = page_a.locator(f'[data-testid="canvas"] polyline[data-stroke-id="{newest_alice}"]').count()
                in_b_newest = page_b.locator(f'[data-testid="canvas"] polyline[data-stroke-id="{newest_alice}"]').count()
                in_a_older = page_a.locator(f'[data-testid="canvas"] polyline[data-stroke-id="{older_alice}"]').count()
                in_b_older = page_b.locator(f'[data-testid="canvas"] polyline[data-stroke-id="{older_alice}"]').count()
                in_a_bob = page_a.locator(f'[data-testid="canvas"] polyline[data-stroke-id="{bob_id}"]').count()
                in_b_bob = page_b.locator(f'[data-testid="canvas"] polyline[data-stroke-id="{bob_id}"]').count()
                if (
                    in_a_newest == 0
                    and in_b_newest == 0
                    and in_a_older == 1
                    and in_b_older == 1
                    and in_a_bob == 1
                    and in_b_bob == 1
                ):
                    success = True
                    break
                time.sleep(0.5)
            assert success, (
                "Undo must remove only Alice's most recent stroke while leaving Alice's earlier stroke "
                "and Bob's stroke intact."
            )

            # Click undo again - should remove the older alice stroke too.
            page_a.locator('[data-testid="undo-mine"]').click()
            deadline = time.time() + 10
            success2 = False
            while time.time() < deadline:
                in_b_older = page_b.locator(f'[data-testid="canvas"] polyline[data-stroke-id="{older_alice}"]').count()
                in_b_bob = page_b.locator(f'[data-testid="canvas"] polyline[data-stroke-id="{bob_id}"]').count()
                if in_b_older == 0 and in_b_bob == 1:
                    success2 = True
                    break
                time.sleep(0.5)
            assert success2, (
                "Second undo must remove Alice's remaining stroke, leaving Bob's stroke untouched."
            )
        finally:
            ctx_a.close()
            ctx_b.close()
            browser.close()
