import json
import os
import re
import socket
import subprocess
import time

import pytest
import requests
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/myproject"
APP_URL = "http://localhost:3000"
RUN_ID = os.environ.get("ZEALT_RUN_ID", "local")
ROOM_ID = f"harbor-typing-form-{RUN_ID}"


def _port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex((host, port)) == 0


@pytest.fixture(scope="session")
def start_app(xprocess):
    """Build (if needed) and start the Next.js app on port 3000."""

    # Build the production bundle first; xprocess only runs the start command.
    build = subprocess.run(
        ["npm", "run", "build"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        timeout=600,
    )
    assert build.returncode == 0, f"`npm run build` failed:\nSTDOUT:\n{build.stdout}\nSTDERR:\n{build.stderr}"

    class Starter(ProcessStarter):
        name = "next_app"
        args = ["npm", "run", "start", "--", "-p", "3000"]
        env = os.environ.copy()
        popen_kwargs = {"cwd": PROJECT_DIR, "text": True}
        timeout = 180
        terminate_on_interrupt = True

        def startup_check(self):
            return _port_open("localhost", 3000)

    xprocess.ensure(Starter.name, Starter)
    # Extra grace period for Liveblocks websocket connections to settle.
    time.sleep(2)

    yield

    info = xprocess.getinfo(Starter.name)
    info.terminate()


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox"])
        yield b
        b.close()


def _wait_for(predicate, timeout: float = 10.0, interval: float = 0.25):
    deadline = time.time() + timeout
    last_exc = None
    while time.time() < deadline:
        try:
            if predicate():
                return True
        except Exception as e:  # noqa: BLE001
            last_exc = e
        time.sleep(interval)
    if last_exc is not None:
        raise last_exc
    return False


def test_form_skeleton_renders(start_app, browser):
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto(f"{APP_URL}/?name=Alice", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="input-name"]', timeout=15000)
    page.wait_for_selector('[data-testid="input-email"]', timeout=15000)
    page.wait_for_selector('[data-testid="input-bio"]', timeout=15000)
    body_text = page.locator("body").inner_text()
    assert "Name" in body_text, "Page should render a visible 'Name' label."
    assert "Email" in body_text, "Page should render a visible 'Email' label."
    assert "Bio" in body_text, "Page should render a visible 'Bio' label."
    ctx.close()


def test_liveblocks_auth_endpoint_returns_token(start_app):
    """The /api/liveblocks-auth route must be implemented and call the real Liveblocks cloud."""
    resp = requests.post(
        f"{APP_URL}/api/liveblocks-auth",
        json={"room": ROOM_ID},
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    assert resp.status_code == 200, (
        f"Expected 200 from /api/liveblocks-auth, got {resp.status_code}: {resp.text[:500]}"
    )
    try:
        body = resp.json()
    except ValueError:
        pytest.fail(f"Auth endpoint did not return JSON. Body: {resp.text[:500]}")
    assert "token" in body, f"Auth response missing 'token' field. Body keys: {list(body.keys())}"
    assert isinstance(body["token"], str) and len(body["token"]) > 20, (
        "Auth token should be a non-trivial string (Liveblocks-issued JWT)."
    )


@pytest.fixture
def two_contexts(start_app, browser):
    ctx_a = browser.new_context()
    ctx_b = browser.new_context()
    page_a = ctx_a.new_page()
    page_b = ctx_b.new_page()
    page_a.goto(f"{APP_URL}/?name=Alice", wait_until="domcontentloaded")
    page_b.goto(f"{APP_URL}/?name=Bob", wait_until="domcontentloaded")
    # Wait for both pages to render the form skeleton.
    page_a.wait_for_selector('[data-testid="input-bio"]', timeout=20000)
    page_b.wait_for_selector('[data-testid="input-bio"]', timeout=20000)
    # Give Liveblocks websockets time to connect.
    time.sleep(3)
    yield page_a, page_b
    ctx_a.close()
    ctx_b.close()


def test_storage_sync_between_contexts(two_contexts):
    page_a, page_b = two_contexts

    # Name field
    page_a.locator('[data-testid="input-name"]').click()
    page_a.locator('[data-testid="input-name"]').fill("")
    page_a.locator('[data-testid="input-name"]').type("Hello", delay=40)
    page_a.locator('[data-testid="input-name"]').blur()
    _wait_for(
        lambda: page_b.locator('[data-testid="input-name"]').input_value() == "Hello",
        timeout=15.0,
    )
    assert page_b.locator('[data-testid="input-name"]').input_value() == "Hello", (
        "Name field did not sync from context A to context B via Liveblocks Storage."
    )

    # Email field
    page_a.locator('[data-testid="input-email"]').click()
    page_a.locator('[data-testid="input-email"]').fill("")
    page_a.locator('[data-testid="input-email"]').type("a@b.co", delay=40)
    page_a.locator('[data-testid="input-email"]').blur()
    _wait_for(
        lambda: page_b.locator('[data-testid="input-email"]').input_value() == "a@b.co",
        timeout=15.0,
    )
    assert page_b.locator('[data-testid="input-email"]').input_value() == "a@b.co", (
        "Email field did not sync from context A to context B via Liveblocks Storage."
    )

    # Bio field
    page_a.locator('[data-testid="input-bio"]').click()
    page_a.locator('[data-testid="input-bio"]').fill("")
    page_a.locator('[data-testid="input-bio"]').type("hi from A", delay=40)
    page_a.locator('[data-testid="input-bio"]').blur()
    _wait_for(
        lambda: page_b.locator('[data-testid="input-bio"]').input_value() == "hi from A",
        timeout=15.0,
    )
    assert page_b.locator('[data-testid="input-bio"]').input_value() == "hi from A", (
        "Bio field did not sync from context A to context B via Liveblocks Storage."
    )


@pytest.mark.parametrize(
    "field,label",
    [("name", "Name"), ("email", "Email"), ("bio", "Bio")],
)
def test_typing_indicator_appears_and_clears(two_contexts, field, label):
    page_a, page_b = two_contexts
    selector_a = f'[data-testid="input-{field}"]'
    indicator_b = f'[data-testid="typing-indicator-{field}"]'

    # A starts typing in the field.
    page_a.locator(selector_a).click()
    page_a.locator(selector_a).type("x", delay=40)

    # B should see the typing indicator with Alice's name and the field label.
    _wait_for(
        lambda: page_b.locator(indicator_b).count() > 0
        and page_b.locator(indicator_b).first.is_visible(),
        timeout=12.0,
    )
    indicator_text = page_b.locator(indicator_b).first.inner_text()
    assert "Alice" in indicator_text, (
        f"Typing indicator for {field} should contain the typing user's name 'Alice'. "
        f"Got: {indicator_text!r}"
    )
    assert label in indicator_text, (
        f"Typing indicator for {field} should contain the field label '{label}'. "
        f"Got: {indicator_text!r}"
    )

    # A blurs the field.
    page_a.locator(selector_a).blur()

    # B's indicator should disappear.
    _wait_for(
        lambda: page_b.locator(indicator_b).count() == 0
        or not page_b.locator(indicator_b).first.is_visible(),
        timeout=12.0,
    )
    visible_after = (
        page_b.locator(indicator_b).count() > 0
        and page_b.locator(indicator_b).first.is_visible()
    )
    assert not visible_after, (
        f"Typing indicator for {field} should disappear when user blurs the field."
    )


def test_lock_overlay_appears_and_clears(two_contexts):
    page_a, page_b = two_contexts
    overlay_b = '[data-testid="lock-overlay-bio"]'

    page_a.locator('[data-testid="input-bio"]').click()
    page_a.locator('[data-testid="input-bio"]').type("z", delay=40)

    _wait_for(
        lambda: page_b.locator(overlay_b).count() > 0
        and page_b.locator(overlay_b).first.is_visible(),
        timeout=12.0,
    )
    assert page_b.locator(overlay_b).count() > 0, (
        "Lock overlay for Bio should be present in context B when A is typing in Bio."
    )

    page_a.locator('[data-testid="input-bio"]').blur()

    _wait_for(
        lambda: page_b.locator(overlay_b).count() == 0
        or not page_b.locator(overlay_b).first.is_visible(),
        timeout=12.0,
    )
    gone = (
        page_b.locator(overlay_b).count() == 0
        or not page_b.locator(overlay_b).first.is_visible()
    )
    assert gone, "Lock overlay for Bio should disappear when A blurs the field."


def test_soft_lock_allows_takeover(two_contexts):
    """B must still be able to type in Bio even while A's overlay is shown there."""
    page_a, page_b = two_contexts

    page_a.locator('[data-testid="input-bio"]').click()
    page_a.locator('[data-testid="input-bio"]').type("A-typing", delay=40)

    # Make sure overlay is up in B.
    _wait_for(
        lambda: page_b.locator('[data-testid="lock-overlay-bio"]').count() > 0,
        timeout=12.0,
    )

    # B clicks Bio and types — this MUST go through (soft lock).
    page_b.locator('[data-testid="input-bio"]').click()
    page_b.locator('[data-testid="input-bio"]').type("B-takeover", delay=40)

    _wait_for(
        lambda: "B-takeover" in page_a.locator('[data-testid="input-bio"]').input_value(),
        timeout=15.0,
    )
    assert "B-takeover" in page_a.locator('[data-testid="input-bio"]').input_value(), (
        "Soft lock must allow user B to take over and type in the field; "
        "the new content was not propagated to user A."
    )


def test_codebase_uses_real_liveblocks_packages():
    """Reject mocked Liveblocks; require real SDK imports."""
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    with open(pkg_path) as f:
        pkg = json.load(f)
    deps = {}
    deps.update(pkg.get("dependencies", {}))
    deps.update(pkg.get("devDependencies", {}))
    assert "@liveblocks/client" in deps, "@liveblocks/client must remain a real dependency."
    assert "@liveblocks/react" in deps, "@liveblocks/react must remain a real dependency."

    # grep -R for @liveblocks/react imports under app/ and components/
    result = subprocess.run(
        ["grep", "-R", "-l", "@liveblocks/react", PROJECT_DIR + "/app"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0 and result.stdout.strip(), (
        "Expected at least one file under app/ to import from @liveblocks/react."
    )

    # Ensure no obvious mocks.
    forbidden = re.compile(r"MockLiveblocks|FakeLiveblocks|stubLiveblocks", re.IGNORECASE)
    grep = subprocess.run(
        ["grep", "-R", "-E", "MockLiveblocks|FakeLiveblocks|stubLiveblocks", PROJECT_DIR + "/app"],
        capture_output=True,
        text=True,
    )
    # grep returns 1 when no match -> good.
    assert grep.returncode != 0 or not forbidden.search(grep.stdout), (
        f"Liveblocks SDK must not be mocked. Found: {grep.stdout[:500]}"
    )
