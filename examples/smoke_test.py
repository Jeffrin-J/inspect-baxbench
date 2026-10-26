"""Minimal task to check that Inspect is installed and working.

Run with no API key:
    uv run inspect eval examples/smoke_test.py --model mockllm/model
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes
from inspect_ai.solver import generate


@task
def smoke_test() -> Task:
    return Task(
        dataset=[
            Sample(input="What is 2 + 2? Answer with a number.", target="4"),
            Sample(input="What is the capital of Scotland?", target="Edinburgh"),
        ],
        solver=generate(),
        scorer=includes(),
    )
