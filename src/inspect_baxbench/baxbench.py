"""BaxBench: Can LLMs Generate Correct and Secure Backends?

Vero et al., ICML 2025. https://arxiv.org/abs/2502.11844

The model writes a backend app from an API spec. The app is built in Docker
and checked with BaxBench's functional tests and security exploits. Docker
must be running.
"""

from inspect_ai import Epochs, Task, task
from inspect_ai.model import GenerateConfig
from inspect_ai.solver import generate, system_message

from inspect_baxbench.dataset import baxbench_dataset
from inspect_baxbench.extraction import extract_code
from inspect_baxbench.prompts import SYSTEM_PROMPT, SafetyPrompt, SpecType
from inspect_baxbench.runner import DEFAULT_TEST_TIMEOUT
from inspect_baxbench.scorer import DEFAULT_MAX_CONCURRENT_TESTS, baxbench_scorer

# Upstream defaults (src/main.py): 5 samples per task to estimate pass@1,
# temperature 0.2, and high reasoning effort for models that support it.
DEFAULT_EPOCHS = 5
DEFAULT_TEMPERATURE = 0.2
DEFAULT_REASONING_EFFORT = "high"


@task
def baxbench(
    spec_type: SpecType = "openapi",
    safety_prompt: SafetyPrompt = "none",
    envs: str | list[str] | None = None,
    scenarios: str | list[str] | None = None,
    epochs: int = DEFAULT_EPOCHS,
    test_timeout: int = DEFAULT_TEST_TIMEOUT,
    max_concurrent_tests: int = DEFAULT_MAX_CONCURRENT_TESTS,
) -> Task:
    """BaxBench code generation task.

    Args:
        spec_type: Describe the API with the OpenAPI schema or in plain text.
        safety_prompt: Security reminder added to the prompt: "none", "generic",
            or "specific".
        envs: Framework IDs to keep, e.g. ["Python-Flask"]. Defaults to all 14.
        scenarios: Scenario IDs to keep, e.g. ["Calculator"]. Defaults to all 28.
        epochs: Samples per task. Scores are averaged, so with the upstream
            default of 5 the mean is an estimate of pass@1.
        test_timeout: Seconds allowed for each individual test (upstream: 300).
        max_concurrent_tests: Samples tested in parallel. Each builds a Docker
            image and starts a container per test.
    """
    return Task(
        dataset=baxbench_dataset(spec_type, safety_prompt, envs, scenarios),
        solver=[system_message(SYSTEM_PROMPT), generate(), extract_code()],
        scorer=baxbench_scorer(test_timeout, max_concurrent_tests),
        epochs=Epochs(epochs, "mean"),
        config=GenerateConfig(
            temperature=DEFAULT_TEMPERATURE,
            reasoning_effort=DEFAULT_REASONING_EFFORT,
        ),
    )
