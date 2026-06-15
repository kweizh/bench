import json
import os
import shutil

import pytest

PROJECT_DIR = "/home/user/myproject"


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_package_json_exists():
    pkg = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(pkg), f"package.json missing at {pkg}."


def test_package_json_declares_liveblocks_deps():
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    with open(pkg_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    deps = {}
    deps.update(data.get("dependencies", {}))
    deps.update(data.get("devDependencies", {}))
    for required in ["@liveblocks/client", "@liveblocks/react", "@liveblocks/node", "next", "react", "react-dom"]:
        assert required in deps, f"Required dependency '{required}' is missing in package.json."


def test_node_modules_preinstalled():
    nm = os.path.join(PROJECT_DIR, "node_modules")
    assert os.path.isdir(nm), "node_modules is not preinstalled (expected dependencies pre-installed)."
    for pkg in ["@liveblocks/client", "@liveblocks/react", "@liveblocks/node", "next"]:
        assert os.path.isdir(os.path.join(nm, pkg)), f"Expected node_modules/{pkg} to be installed."


def test_next_app_router_layout_exists():
    layout_tsx = os.path.join(PROJECT_DIR, "app", "layout.tsx")
    page_tsx = os.path.join(PROJECT_DIR, "app", "page.tsx")
    assert os.path.isfile(layout_tsx), f"Expected Next.js App Router layout at {layout_tsx}."
    assert os.path.isfile(page_tsx), f"Expected Next.js App Router page at {page_tsx}."


def test_liveblocks_auth_route_exists():
    route = os.path.join(PROJECT_DIR, "app", "api", "liveblocks-auth", "route.ts")
    assert os.path.isfile(route), f"Expected Liveblocks auth route at {route}."
    content = _read_text(route)
    assert "@liveblocks/node" in content, "Auth route should use @liveblocks/node."


def test_liveblocks_config_module_exists():
    # Either lib/liveblocks.ts or liveblocks.config.ts is acceptable as the typed context module.
    candidates = [
        os.path.join(PROJECT_DIR, "lib", "liveblocks.ts"),
        os.path.join(PROJECT_DIR, "liveblocks.config.ts"),
    ]
    assert any(os.path.isfile(p) for p in candidates), (
        "Expected a Liveblocks config/context module at lib/liveblocks.ts or liveblocks.config.ts."
    )


def test_scaffold_renders_canvas_and_toolbar():
    # The scaffold renders the basic placeholder shell across app/ and components/.
    # Drawing logic is NOT implemented yet.
    combined = ""
    for root_dir in [os.path.join(PROJECT_DIR, "app"), os.path.join(PROJECT_DIR, "components")]:
        if not os.path.isdir(root_dir):
            continue
        for root, _dirs, files in os.walk(root_dir):
            for fn in files:
                if fn.endswith((".ts", ".tsx", ".js", ".jsx")):
                    combined += _read_text(os.path.join(root, fn)) + "\n"
    for testid in [
        'data-testid="canvas"',
        'data-testid="color-picker"',
        'data-testid="width-picker"',
        'data-testid="tool-pen"',
        'data-testid="tool-eraser"',
        'data-testid="undo-mine"',
    ]:
        assert testid in combined, f"Scaffold should already contain {testid} placeholder in app/ or components/."


def test_drawing_logic_not_yet_implemented():
    """The scaffold should NOT yet implement stroke pushing or eraser deletion."""
    # Aggregate source from page.tsx and any component file under components/ or app/
    source_blobs = []
    for root, _dirs, files in os.walk(PROJECT_DIR):
        # Skip node_modules and .next
        rel = os.path.relpath(root, PROJECT_DIR)
        if rel.startswith("node_modules") or rel.startswith(".next") or rel.startswith(".git"):
            continue
        for fn in files:
            if fn.endswith((".ts", ".tsx", ".js", ".jsx")):
                try:
                    source_blobs.append(_read_text(os.path.join(root, fn)))
                except Exception:
                    pass
    combined = "\n".join(source_blobs)
    # No stroke push or delete logic yet (executor must add it).
    assert ".push(" not in combined or "strokes" not in combined.lower() or "LiveObject" not in combined or "points" not in combined, (
        "Initial scaffold appears to already implement stroke creation; drawing logic must NOT be pre-implemented."
    )
    # Also assert that there is no LiveList<LiveObject<... points ...>> stroke push wired together yet.
    forbidden = [
        "strokes.push(new LiveObject",
        "strokes.push(\n",
        "storage.get(\"strokes\").push",
        "strokes.delete(",
    ]
    for token in forbidden:
        assert token not in combined, (
            f"Initial scaffold must not pre-implement stroke logic; found forbidden token: {token!r}"
        )


def test_playwright_available_for_verifier():
    # Used by the final-state verifier.
    assert shutil.which("npx") is not None, "npx is required to drive Playwright."
