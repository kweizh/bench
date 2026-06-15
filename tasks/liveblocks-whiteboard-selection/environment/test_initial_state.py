"""Initial-state checks for the liveblocks-whiteboard-selection task.

These tests verify that the scaffolded Next.js + Liveblocks project is
present at /home/user/whiteboard with dependencies installed, but that
the multi-user *selection* feature (Presence-based selection rings,
`useOthers()` consumption of `selectedShapeId`) has NOT yet been
implemented by the agent.
"""

import json
import os
import shutil
from pathlib import Path

PROJECT_DIR = "/home/user/whiteboard"


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected scaffolded project directory {PROJECT_DIR} to exist."
    )


def test_package_json_has_liveblocks_dependencies():
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(pkg_path), f"{pkg_path} does not exist."
    pkg = json.loads(_read(pkg_path))
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    for required in ("@liveblocks/client", "@liveblocks/react", "next", "react"):
        assert required in deps, (
            f"Expected dependency '{required}' to be declared in package.json."
        )


def test_node_modules_installed():
    node_modules = os.path.join(PROJECT_DIR, "node_modules")
    assert os.path.isdir(node_modules), (
        f"Expected node_modules to be pre-installed at {node_modules}."
    )
    # Spot check Liveblocks packages are present.
    for required in ("@liveblocks/client", "@liveblocks/react", "next"):
        pkg_dir = os.path.join(node_modules, required)
        assert os.path.isdir(pkg_dir), (
            f"Expected installed package directory {pkg_dir}."
        )


def test_liveblocks_config_file_exists():
    cfg_path = os.path.join(PROJECT_DIR, "liveblocks.config.ts")
    assert os.path.isfile(cfg_path), (
        f"Expected scaffolded {cfg_path} to exist for the agent to extend."
    )


def test_initial_state_has_no_presence_selection_field():
    """The Presence.selectedShapeId field MUST NOT yet exist in the scaffold.

    The agent is responsible for adding it.
    """
    cfg_path = os.path.join(PROJECT_DIR, "liveblocks.config.ts")
    content = _read(cfg_path)
    assert "selectedShapeId" not in content, (
        "Initial liveblocks.config.ts must not yet declare 'selectedShapeId'; "
        "the agent must add this Presence field."
    )


def test_initial_state_does_not_use_useOthers_for_selection():
    """The selection-aware use of useOthers MUST NOT yet exist in the scaffold."""
    tsx_files = []
    for root, _dirs, files in os.walk(PROJECT_DIR):
        # Skip node_modules and build output.
        if "node_modules" in root or "/.next" in root:
            continue
        for name in files:
            if name.endswith((".tsx", ".ts", ".jsx", ".js")):
                tsx_files.append(os.path.join(root, name))

    offenders = []
    for path in tsx_files:
        try:
            text = _read(path)
        except OSError:
            continue
        if "selectedShapeId" in text:
            offenders.append(path)
    assert not offenders, (
        "Initial scaffold must not reference 'selectedShapeId'; "
        f"found in: {offenders}"
    )


def test_initial_state_has_no_selection_ring_dom():
    """The DOM hook for other-user selection rings MUST NOT yet exist."""
    page_candidates = [
        os.path.join(PROJECT_DIR, "app", "page.tsx"),
        os.path.join(PROJECT_DIR, "pages", "index.tsx"),
        os.path.join(PROJECT_DIR, "components", "Whiteboard.tsx"),
    ]
    found_any = False
    for path in page_candidates:
        if not os.path.isfile(path):
            continue
        found_any = True
        text = _read(path)
        assert 'data-testid="selection-ring"' not in text, (
            f"Initial scaffold {path} must not yet render selection-ring "
            "elements; this is the feature the agent must implement."
        )
    assert found_any, (
        "Expected at least one of app/page.tsx, pages/index.tsx, or "
        "components/Whiteboard.tsx to exist in the scaffold."
    )


def test_shapes_seeding_mutation_present():
    """The scaffold MUST already contain shape seeding logic (the agent only
    needs to wire it through the new Storage type)."""
    grep_targets = []
    for root, _dirs, files in os.walk(PROJECT_DIR):
        if "node_modules" in root or "/.next" in root:
            continue
        for name in files:
            if name.endswith((".tsx", ".ts")):
                grep_targets.append(os.path.join(root, name))

    seeded = False
    for path in grep_targets:
        try:
            text = _read(path)
        except OSError:
            continue
        # Seeding refers to shape-a/shape-b/shape-c constants used in seed.
        if "shape-a" in text and "shape-b" in text and "shape-c" in text:
            seeded = True
            break
    assert seeded, (
        "Expected scaffold to already contain a seeding routine that creates "
        "shapes with ids shape-a, shape-b, shape-c."
    )


def test_env_local_has_liveblocks_keys():
    env_path = os.path.join(PROJECT_DIR, ".env.local")
    assert os.path.isfile(env_path), (
        f"Expected {env_path} to be pre-populated with Liveblocks credentials."
    )
    text = _read(env_path)
    assert "LIVEBLOCKS_SECRET_KEY" in text, (
        "Expected LIVEBLOCKS_SECRET_KEY to be present in .env.local."
    )
    assert "NEXT_PUBLIC_LIVEBLOCKS_PUBLIC_KEY" in text, (
        "Expected NEXT_PUBLIC_LIVEBLOCKS_PUBLIC_KEY to be present in .env.local."
    )


def test_run_id_env_propagation_wired():
    """next.config.js (or equivalent) MUST already expose ZEALT_RUN_ID as
    NEXT_PUBLIC_ZEALT_RUN_ID so the client can derive a unique room id."""
    candidates = [
        os.path.join(PROJECT_DIR, "next.config.js"),
        os.path.join(PROJECT_DIR, "next.config.mjs"),
        os.path.join(PROJECT_DIR, "next.config.ts"),
    ]
    found = [p for p in candidates if os.path.isfile(p)]
    assert found, "Expected a next.config.{js,mjs,ts} file in the scaffold."
    combined = "\n".join(_read(p) for p in found)
    assert "NEXT_PUBLIC_ZEALT_RUN_ID" in combined, (
        "Expected the Next.js config to expose NEXT_PUBLIC_ZEALT_RUN_ID."
    )
