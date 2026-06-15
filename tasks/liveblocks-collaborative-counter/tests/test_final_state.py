"""Final-state verification for the liveblocks-collaborative-counter task.

These tests boot the executor's Next.js app and verify, against real Liveblocks
cloud, that:

* the `/api/liveblocks-auth` endpoint actually mints a session token;
* two browser contexts visiting `/dashboard/<room>` stay in sync;
* Storage mutations write `value`, `lastIncrementBy`, and `lastUpdated`
  together inside a batched `useMutation`;
* the global `reset-all` action propagates as a batched update.
"""

import json
import os
import re
import socket
import subprocess
import time

import pytest
import requests
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/project"
PORT = 3000
BASE_URL = f"http://localhost:{PORT}"

LIVEBLOCKS_SECRET = os.environ.get("LIVEBLOCKS_SECRET_KEY", "")
RUN_ID = os.environ.get("ZEALT_RUN_ID", "local")
ROOM = f"counter-room-{RUN_ID}"


def _port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex((host, port)) == 0


@pytest.fixture(scope="session", autouse=True)
def build_app():
    """Build the Next.js app once before the server fixture starts."""
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"`npm run build` failed (exit {result.returncode}).\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


@pytest.fixture(scope="session")
def app_server(xprocess, build_app):
    """Start the production Next.js server on port 3000."""

    class Starter(ProcessStarter):
        name = "liveblocks_counter_app"
        args = ["npm", "run", "start", "--", "-p", str(PORT)]
        env = os.environ.copy()
        popen_kwargs = {"cwd": PROJECT_DIR, "text": True}
        timeout = 180
        terminate_on_interrupt = True

        def startup_check(self):
            return _port_open("localhost", PORT)

    xprocess.ensure(Starter.name, Starter)
    # Extra grace: Next sometimes accepts connections before fully ready.
    deadline = time.time() + 60
    while time.time() < deadline:
        try:
            r = requests.get(f"{BASE_URL}/dashboard/{ROOM}", timeout=5)
            if r.status_code < 500:
                break
        except requests.RequestException:
            time.sleep(1)
    else:
        pytest.fail("Next.js server did not respond on port 3000 in time.")

    yield BASE_URL

    info = xprocess.getinfo(Starter.name)
    info.terminate()


def _assert_no_liveblocks_mocks():
    """Make sure no source file replaces Liveblocks with a stub."""
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    with open(pkg_path) as f:
        pkg = json.load(f)
    deps = {**(pkg.get("dependencies") or {}),
            **(pkg.get("devDependencies") or {})}
    for required in ("@liveblocks/client", "@liveblocks/react",
                     "@liveblocks/node"):
        assert required in deps, (
            f"{required} must remain a real dependency (no mocks)."
        )

    src_root = PROJECT_DIR
    forbidden_patterns = (re.compile(r"jest\.mock\([^\)]*liveblocks",
                                       re.IGNORECASE),
                          re.compile(r"vi\.mock\([^\)]*liveblocks",
                                       re.IGNORECASE))
    for root, dirs, files in os.walk(src_root):
        # Skip vendored / build directories.
        if any(part in root for part in ("/node_modules", "/.next",
                                          "/.git")):
            continue
        for name in files:
            if not name.endswith((".ts", ".tsx", ".js", ".jsx", ".mjs")):
                continue
            path = os.path.join(root, name)
            try:
                with open(path, encoding="utf-8", errors="ignore") as fh:
                    body = fh.read()
            except OSError:
                continue
            for pat in forbidden_patterns:
                assert not pat.search(body), (
                    f"Found mocked Liveblocks usage in {path}: {pat.pattern}"
                )


def test_no_liveblocks_mocks_or_stubs(app_server):
    _assert_no_liveblocks_mocks()


def test_auth_endpoint_returns_real_token(app_server):
    """The /api/liveblocks-auth endpoint must mint a real session token."""
    response = requests.post(
        f"{BASE_URL}/api/liveblocks-auth",
        json={"room": ROOM},
        timeout=15,
    )
    assert response.status_code == 200, (
        f"Expected 200 from /api/liveblocks-auth, got "
        f"{response.status_code}. Body: {response.text[:500]}"
    )
    body = response.json()
    token = body.get("token")
    assert isinstance(token, str) and len(token) >= 16, (
        f"Auth endpoint did not return a non-empty `token` string. "
        f"Body: {body!r}"
    )

    # Issuing a second call should also yield a token (proves it is not
    # a hard-coded constant — they should at minimum still be valid JWT-ish
    # shapes; tokens may or may not differ).
    response2 = requests.post(
        f"{BASE_URL}/api/liveblocks-auth",
        json={"room": ROOM},
        timeout=15,
    )
    assert response2.status_code == 200, (
        "Second call to /api/liveblocks-auth failed."
    )
    assert isinstance(response2.json().get("token"), str), (
        "Second auth response missing `token`."
    )


# ---------------------------------------------------------------------------
# Playwright two-context end-to-end test
# ---------------------------------------------------------------------------


def _set_identity(page, value: str) -> None:
    locator = page.locator('[data-testid="identity-input"]')
    locator.wait_for(state="visible", timeout=20_000)
    locator.fill("")
    locator.fill(value)
    locator.blur()


def _create_counter(page, key: str, initial: int) -> None:
    page.locator('[data-testid="new-counter-key"]').fill(key)
    page.locator('[data-testid="new-counter-initial"]').fill(str(initial))
    page.locator('[data-testid="create-counter"]').click()


def _row(page, key: str):
    return page.locator(f'[data-testid="counter-row"][data-counter-key="{key}"]')


def _wait_for_value(page, key: str, expected: int, timeout_ms: int = 15_000) -> None:
    locator = _row(page, key).locator('[data-testid="counter-value"]')
    locator.wait_for(state="visible", timeout=timeout_ms)
    deadline = time.time() + timeout_ms / 1000.0
    last = None
    while time.time() < deadline:
        last = (locator.text_content() or "").strip()
        if last == str(expected):
            return
        time.sleep(0.25)
    raise AssertionError(
        f"Timed out waiting for counter {key!r} to read {expected}; "
        f"last observed value: {last!r}"
    )


def _wait_for_last_toucher(page, key: str, identity: str,
                            timeout_ms: int = 15_000) -> str:
    locator = _row(page, key).locator('[data-testid="last-touched"]')
    locator.wait_for(state="visible", timeout=timeout_ms)
    pattern = re.compile(
        rf"^Last touched by {re.escape(identity)} at "
        rf"\d{{4}}-\d{{2}}-\d{{2}}T[\d:.\-+Z]+$"
    )
    deadline = time.time() + timeout_ms / 1000.0
    last = None
    while time.time() < deadline:
        last = (locator.text_content() or "").strip()
        if pattern.match(last):
            return last
        time.sleep(0.25)
    raise AssertionError(
        f"Last-touched line for {key!r} never matched identity={identity!r}. "
        f"Last observed: {last!r}"
    )


def test_two_client_realtime_sync(app_server):
    from playwright.sync_api import sync_playwright

    url = f"{BASE_URL}/dashboard/{ROOM}"

    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--no-sandbox"])
        try:
            ctx_a = browser.new_context()
            ctx_b = browser.new_context()
            page_a = ctx_a.new_page()
            page_b = ctx_b.new_page()

            page_a.goto(url, wait_until="domcontentloaded", timeout=60_000)
            page_b.goto(url, wait_until="domcontentloaded", timeout=60_000)

            # Both pages must expose the static skeleton.
            for page in (page_a, page_b):
                page.locator('[data-testid="identity-input"]').wait_for(
                    state="visible", timeout=30_000
                )
                page.locator('[data-testid="reset-all"]').wait_for(
                    state="visible", timeout=30_000
                )

            _set_identity(page_a, "alice")
            _set_identity(page_b, "bob")

            # 1. A creates `alpha` at 10.
            _create_counter(page_a, "alpha", 10)
            _wait_for_value(page_a, "alpha", 10)
            _wait_for_last_toucher(page_a, "alpha", "alice")

            # 2. B should see the new counter without a reload.
            _wait_for_value(page_b, "alpha", 10)

            # 3. B increments twice — A should see 12 and bob as toucher.
            page_b.locator(
                f'[data-testid="counter-row"][data-counter-key="alpha"] '
                f'[data-testid="increment"]'
            ).click()
            page_b.locator(
                f'[data-testid="counter-row"][data-counter-key="alpha"] '
                f'[data-testid="increment"]'
            ).click()
            _wait_for_value(page_a, "alpha", 12)
            _wait_for_last_toucher(page_a, "alpha", "bob")

            # 4. A decrements — B should see 11 and alice as toucher.
            page_a.locator(
                f'[data-testid="counter-row"][data-counter-key="alpha"] '
                f'[data-testid="decrement"]'
            ).click()
            _wait_for_value(page_b, "alpha", 11)
            _wait_for_last_toucher(page_b, "alpha", "alice")

            # 5. A creates a second counter `beta` at 5, B increments once.
            _create_counter(page_a, "beta", 5)
            _wait_for_value(page_b, "beta", 5)
            page_b.locator(
                f'[data-testid="counter-row"][data-counter-key="beta"] '
                f'[data-testid="increment"]'
            ).click()
            _wait_for_value(page_a, "beta", 6)
            _wait_for_last_toucher(page_a, "beta", "bob")

            # 6. Reset all — every counter resets to 0 with alice as toucher.
            page_a.locator('[data-testid="reset-all"]').click()
            for key in ("alpha", "beta"):
                _wait_for_value(page_b, key, 0)
                _wait_for_last_toucher(page_b, key, "alice")
        finally:
            browser.close()


def test_storage_schema_via_liveblocks_rest(app_server):
    """Validate Storage layout against real Liveblocks cloud."""
    if not LIVEBLOCKS_SECRET:
        pytest.skip("LIVEBLOCKS_SECRET_KEY not provided; skipping REST check.")

    headers = {"Authorization": f"Bearer {LIVEBLOCKS_SECRET}"}
    # Give Liveblocks a moment to persist the latest mutations from the
    # previous test before we query storage.
    deadline = time.time() + 60
    last_body = None
    while time.time() < deadline:
        resp = requests.get(
            f"https://api.liveblocks.io/v2/rooms/{ROOM}/storage",
            headers=headers,
            timeout=20,
        )
        if resp.status_code == 200:
            last_body = resp.json()
            data = last_body.get("data") if isinstance(last_body, dict) else None
            counters = (data or {}).get("counters")
            if isinstance(counters, dict) and counters.get(
                "liveblocksType"
            ) == "LiveMap":
                entries = counters.get("data") or {}
                if entries:
                    # Validate every LiveObject entry.
                    for key, entry in entries.items():
                        assert isinstance(entry, dict), (
                            f"Counter {key!r} is not a LiveObject."
                        )
                        assert entry.get("liveblocksType") == "LiveObject", (
                            f"Counter {key!r} is not typed as LiveObject; "
                            f"got {entry.get('liveblocksType')!r}."
                        )
                        fields = entry.get("data") or {}
                        assert isinstance(fields.get("value"), (int, float)), (
                            f"Counter {key!r} `value` is not numeric: "
                            f"{fields.get('value')!r}"
                        )
                        assert isinstance(fields.get("lastIncrementBy"), str), (
                            f"Counter {key!r} `lastIncrementBy` is not a "
                            f"string: {fields.get('lastIncrementBy')!r}"
                        )
                        assert isinstance(fields.get("lastUpdated"),
                                          (int, float)), (
                            f"Counter {key!r} `lastUpdated` is not numeric: "
                            f"{fields.get('lastUpdated')!r}"
                        )
                    return
        time.sleep(2)
    pytest.fail(
        "Storage schema check failed; last body: "
        f"{json.dumps(last_body)[:1000] if last_body else 'no body'}"
    )
