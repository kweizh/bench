import json
import os
import shutil

PROJECT_DIR = "/home/user/myproject"


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Expected project directory {PROJECT_DIR} to exist."


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_package_json_exists():
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(pkg_path), f"Expected {pkg_path} to exist in the starter project."


def test_package_json_has_liveblocks_deps():
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    with open(pkg_path) as f:
        pkg = json.load(f)
    deps = {}
    deps.update(pkg.get("dependencies", {}))
    deps.update(pkg.get("devDependencies", {}))
    assert "@liveblocks/client" in deps, "@liveblocks/client must be preinstalled."
    assert "@liveblocks/react" in deps, "@liveblocks/react must be preinstalled."
    assert "@liveblocks/node" in deps, "@liveblocks/node must be preinstalled."
    assert "next" in deps, "next must be preinstalled."


def test_node_modules_installed():
    nm_path = os.path.join(PROJECT_DIR, "node_modules")
    assert os.path.isdir(nm_path), "node_modules must already be installed in the starter project."
    assert os.path.isdir(
        os.path.join(nm_path, "@liveblocks", "react")
    ), "@liveblocks/react must already be installed under node_modules."


def test_app_directory_exists():
    app_dir = os.path.join(PROJECT_DIR, "app")
    assert os.path.isdir(app_dir), "Next.js app/ directory must exist in the starter project."


def test_page_file_exists():
    page_path = os.path.join(PROJECT_DIR, "app", "page.tsx")
    assert os.path.isfile(page_path), "app/page.tsx must exist in the starter project."


def test_initial_form_skeleton_present():
    page_path = os.path.join(PROJECT_DIR, "app", "page.tsx")
    with open(page_path) as f:
        content = f.read()
    # The starter must already show the static three-field form skeleton.
    assert "input-name" in content, "Starter page should render an input with data-testid=input-name."
    assert "input-email" in content, "Starter page should render an input with data-testid=input-email."
    assert "input-bio" in content, "Starter page should render an input/textarea with data-testid=input-bio."


def test_typing_indicator_not_yet_implemented():
    """The presence-driven typing indicator must NOT yet be wired in the starter."""
    page_path = os.path.join(PROJECT_DIR, "app", "page.tsx")
    with open(page_path) as f:
        content = f.read()
    assert "typing-indicator-" not in content, (
        "The starter must NOT yet implement the presence-driven typing indicator "
        "(no data-testid=typing-indicator-* should appear in app/page.tsx)."
    )
    assert "lock-overlay-" not in content, (
        "The starter must NOT yet implement the per-field lock overlay "
        "(no data-testid=lock-overlay-* should appear in app/page.tsx)."
    )
    assert "useMyPresence" not in content and "useOthers" not in content, (
        "The starter must NOT yet wire Liveblocks presence hooks in app/page.tsx."
    )


def test_liveblocks_auth_endpoint_not_yet_implemented():
    auth_path = os.path.join(PROJECT_DIR, "app", "api", "liveblocks-auth", "route.ts")
    auth_path_js = os.path.join(PROJECT_DIR, "app", "api", "liveblocks-auth", "route.js")
    assert not os.path.exists(auth_path) and not os.path.exists(auth_path_js), (
        "The /api/liveblocks-auth route must NOT yet be implemented in the starter."
    )


def test_playwright_available_for_verifier():
    # Playwright is used by the final-state verifier; ensure the CLI is present.
    assert shutil.which("playwright") is not None or shutil.which("npx") is not None, (
        "playwright (or npx) must be available for the verifier."
    )
