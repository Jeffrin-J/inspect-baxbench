"""BaxBench: Can LLMs Generate Correct and Secure Backends?

Vero et al., ICML 2025. https://arxiv.org/abs/2502.11844

Work in progress: this task only generates code. Running the generated apps
and scoring them against BaxBench's functional tests and exploits comes next.
"""

from inspect_ai import Task, task
from inspect_ai.model import GenerateConfig
from inspect_ai.solver import generate, system_message

from inspect_baxbench.dataset import baxbench_dataset
from inspect_baxbench.prompts import SYSTEM_PROMPT, SafetyPrompt, SpecType

# Upstream default sampling temperature.
DEFAULT_TEMPERATURE = 0.2


@task
def baxbench(
    spec_type: SpecType = "openapi",
    safety_prompt: SafetyPrompt = "none",
    envs: str | list[str] | None = None,
    scenarios: str | list[str] | None = None,
) -> Task:
    """BaxBench code generation task.

    Args:
        spec_type: Describe the API with the OpenAPI schema or in plain text.
        safety_prompt: Security reminder added to the prompt: "none", "generic",
            or "specific".
        envs: Framework IDs to keep, e.g. ["Python-Flask"]. Defaults to all 14.
        scenarios: Scenario IDs to keep, e.g. ["Calculator"]. Defaults to all 28.
    """
    return Task(
        dataset=baxbench_dataset(spec_type, safety_prompt, envs, scenarios),
        solver=[system_message(SYSTEM_PROMPT), generate()],
        config=GenerateConfig(temperature=DEFAULT_TEMPERATURE),
    )
