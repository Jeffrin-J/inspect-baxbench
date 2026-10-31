"""End-to-end scorer tests: a mock model returns hand-written apps, which are
built and attacked in Docker. Slow (a couple of minutes per app) and needs
Docker running, so they only run with RUN_DOCKER_TESTS=1.
"""

import os
from pathlib import Path

import pytest
from inspect_ai import eval
from inspect_ai.model import ModelOutput, get_model

from inspect_baxbench import baxbench

APPS = Path(__file__).parent / "apps"

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_DOCKER_TESTS") != "1",
    reason="needs Docker; set RUN_DOCKER_TESTS=1",
)


def _score(app_dir: str):
    code = (APPS / app_dir / "app.py").read_text()
    model = get_model(
        "mockllm/model",
        custom_outputs=[ModelOutput.from_content("mockllm/model", f"<CODE>\n{code}\n</CODE>")],
    )
    task = baxbench(envs="Python-Flask", scenarios="Calculator", epochs=1)
    [log] = eval(task, model=model, display="none", log_dir="logs/tests")
    assert log.status == "success"
    return log


def test_secure_app_is_correct_and_secure():
    log = _score("calculator_flask_secure")
    score = log.samples[0].scores["baxbench_scorer"]
    assert score.value == {"correct": 1, "secure": 1, "insecure_correct": 0, "build_failed": 0}
    assert score.metadata["cwes"] == []


def test_insecure_app_is_correct_but_exploitable():
    log = _score("calculator_flask_insecure")
    score = log.samples[0].scores["baxbench_scorer"]
    assert score.value == {"correct": 1, "secure": 0, "insecure_correct": 1, "build_failed": 0}
    assert 94 in score.metadata["cwes"]  # code injection
    metrics = {name: m.value for s in log.results.scores for name, m in s.metrics.items()}
    assert metrics["insecure_given_correct"] == 1.0


def _build_images() -> list[str]:
    import docker

    return [
        i.id for i in docker.from_env().images.list(all=True, filters={"label": "baxbench.build"})
    ]


def test_builds_leave_no_images_behind():
    from concurrent.futures import ThreadPoolExecutor

    from inspect_baxbench.runner import run_tests

    code = (APPS / "calculator_flask_secure" / "app.py").read_text()
    apps = [
        {"app.py": code + "\n# sample 1\n"},
        {"app.py": code + "\n# sample 2\n"},
        {"app.py": "import flask\n"},  # builds, but the server never starts
    ]
    before = set(_build_images())
    # Concurrent builds of one framework, as in a real run, used to leak the
    # intermediate images they shared.
    with ThreadPoolExecutor(len(apps)) as pool:
        outcomes = list(
            pool.map(lambda files: run_tests("Calculator", "Python-Flask", files), apps)
        )
    assert [o.functionally_correct for o in outcomes[:2]] == [True, True]
    assert set(_build_images()) - before == set()
