"""Access to upstream BaxBench's environments, scenarios and tests.

The functional tests and security exploits are Python functions in the
upstream repo, so we download it at a pinned commit and import it rather than
copying thousands of lines. Upstream imports its modules by top-level name
(`env`, `scenarios`, `exploits`, `cwes`), so its `src` directory is added to
sys.path. Importing `env` connects to Docker, so Docker must be running.

BaxBench is MIT licensed, Copyright (c) 2025 SRI Lab, LogicStar.ai.
"""

import io
import sys
import tarfile
import urllib.request
from functools import cache
from pathlib import Path
from typing import Any

UPSTREAM_REPO = "logic-star-ai/baxbench"
# Tag v1.0.0.
UPSTREAM_COMMIT = "a67abd942454a11ff2966674d498abc451a52d67"

CACHE_DIR = Path.home() / ".cache" / "inspect_baxbench"


def upstream_src_dir() -> Path:
    """Download upstream at the pinned commit (once) and return its src directory."""
    root = CACHE_DIR / f"baxbench-{UPSTREAM_COMMIT}"
    src = root / "src"
    if not (src / "scenarios" / "__init__.py").exists():
        url = f"https://codeload.github.com/{UPSTREAM_REPO}/tar.gz/{UPSTREAM_COMMIT}"
        with urllib.request.urlopen(url, timeout=120) as response:
            data = response.read()
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
            # The archive's top-level directory is baxbench-<commit>.
            tar.extractall(CACHE_DIR, filter="data")
    return src


def add_upstream_to_path() -> None:
    src = str(upstream_src_dir())
    if src not in sys.path:
        sys.path.insert(0, src)


@cache
def load_upstream() -> tuple[dict[str, Any], dict[str, Any]]:
    """Return ({scenario_id: Scenario}, {env_id: Env}) from upstream."""
    add_upstream_to_path()
    from env import all_envs
    from scenarios import all_scenarios

    return {s.id: s for s in all_scenarios}, {e.id: e for e in all_envs}
