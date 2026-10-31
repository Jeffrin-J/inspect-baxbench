"""Copy eval logs with local paths removed, for publishing.

Test logs in the scores include tracebacks with paths such as
C:\\Users\\<name>\\... . This replaces the home directory with "~" and the
repo checkout with "<repo>" in every string of the log, writes the copy to
logs/public/, and fails if the home directory or user name is still present.

    uv run python scripts/deidentify_logs.py logs/<run>.eval [...]
"""

import getpass
import json
import sys
from pathlib import Path
from typing import Any

from inspect_ai.log import EvalLog, read_eval_log, write_eval_log

REPO = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO / "logs" / "public"


def _variants(path: Path) -> list[str]:
    """The ways a path can appear in a string: native, with forward slashes, and
    with doubled backslashes (as in repr() of a path inside a traceback)."""
    native = str(path)
    forms = {native, path.as_posix(), native.replace("\\", "\\\\")}
    # Longest first, so the doubled form is replaced before its substrings.
    return sorted(forms, key=len, reverse=True)


REPLACEMENTS = [(v, "<repo>") for v in _variants(REPO)] + [(v, "~") for v in _variants(Path.home())]


def _clean(value: Any) -> Any:
    if isinstance(value, str):
        for old, new in REPLACEMENTS:
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [_clean(v) for v in value]
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items()}
    return value


def deidentify(path: Path) -> Path:
    log = read_eval_log(str(path))
    cleaned = EvalLog.model_validate(_clean(log.model_dump()))
    text = json.dumps(cleaned.model_dump(), default=str)
    user = getpass.getuser()
    for leftover in [*_variants(Path.home()), f"\\{user}\\", f"/{user}/"]:
        if leftover in text:
            raise RuntimeError(f"{path.name}: {leftover!r} is still in the log")
    out = OUTPUT_DIR / path.name
    out.parent.mkdir(parents=True, exist_ok=True)
    write_eval_log(cleaned, str(out))
    return out


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print(f"Wrote {deidentify(Path(arg))}")
