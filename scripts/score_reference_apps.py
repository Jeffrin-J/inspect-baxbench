"""Score the hand-written reference apps in tests/apps without calling a model.

Checks the Docker runner end to end for each framework. Needs Docker running.
The first build per language downloads its base image (1-2 GB).

    uv run python scripts/score_reference_apps.py              # all apps
    uv run python scripts/score_reference_apps.py logger_go    # selected apps
"""

import sys
import time
from pathlib import Path

from inspect_baxbench.runner import run_tests

APPS = Path(__file__).parent.parent / "tests" / "apps"

# app folder -> (scenario, framework, expected correct, expected CWEs)
CASES = {
    "calculator_flask_secure": ("Calculator", "Python-Flask", True, set()),
    "calculator_flask_insecure": ("Calculator", "Python-Flask", True, {94, 400}),
    "logger_express": ("Logger", "JavaScript-express", True, {117}),
    "logger_go": ("Logger", "Go-net/http", True, {117}),
    "logger_rust": ("Logger", "Rust-Actix", True, {117}),
    "logger_lumen": ("Logger", "PHP-Lumen", True, {117}),
    "logger_rails": ("Logger", "Ruby-Rails", True, {117}),
    "logger_fiber": ("Logger", "Go-Fiber", True, {117}),
    "logger_gin": ("Logger", "Go-Gin", True, {117}),
    "logger_fastify": ("Logger", "JavaScript-fastify", True, {117}),
    "logger_koa": ("Logger", "JavaScript-koa", True, {117}),
    "logger_nest": ("Logger", "JavaScript-nest", True, {117}),
    "logger_fastapi": ("Logger", "Python-FastAPI", True, {117}),
    "logger_aiohttp": ("Logger", "Python-aiohttp", True, {117}),
    "logger_django": ("Logger", "Python-Django", True, {117}),
}


def read_app(name: str) -> dict[str, str]:
    root = APPS / name
    return {
        path.relative_to(root).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def main(names: list[str]) -> int:
    failures = 0
    for name in names or list(CASES):
        scenario, env, expect_correct, expect_cwes = CASES[name]
        start = time.time()
        outcome = run_tests(scenario, env, read_app(name))
        ok = (
            outcome.functionally_correct == expect_correct
            and expect_cwes <= outcome.cwes
            and not outcome.build_failed
            and outcome.num_ft_exceptions == 0
        )
        failures += not ok
        print(
            f"{'OK  ' if ok else 'FAIL'} {name} ({env}): "
            f"build_failed={outcome.build_failed} "
            f"ft={outcome.num_passed_ft}/{outcome.num_total_ft} "
            f"exceptions={outcome.num_ft_exceptions}+{outcome.num_st_exceptions} "
            f"cwes={sorted(outcome.cwes)} expected={sorted(expect_cwes)} "
            f"({time.time() - start:.0f}s)",
            flush=True,
        )
        if not ok:
            print(outcome.log[-6000:], flush=True)
    return failures


# Guard needed: tests run in spawned subprocesses that re-import this module.
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
