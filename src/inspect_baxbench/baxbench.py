"""BaxBench: Can LLMs Generate Correct and Secure Backends?

Vero et al., ICML 2025. https://arxiv.org/abs/2502.11844

Work in progress: this task generates code and extracts the app's files.
Running the generated apps and scoring them against BaxBench's functional
tests and exploits comes next.
"""

from inspect_ai import Epochs, Task, task
from inspect_ai.model import GenerateConfig
from inspect_ai.solver import generate, system_message

from inspect_baxbench.dataset import baxbench_dataset
from inspect_baxbench.extraction import extract_code
from inspect_baxbench.prompts import SYSTEM_PROMPT, SafetyPrompt, SpecType

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
    """
    return Task(
        dataset=baxbench_dataset(spec_type, safety_prompt, envs, scenarios),
        solver=[system_message(SYSTEM_PROMPT), generate(), extract_code()],
        epochs=Epochs(epochs, "mean"),
        config=GenerateConfig(
            temperature=DEFAULT_TEMPERATURE,
            reasoning_effort=DEFAULT_REASONING_EFFORT,
        ),
    )
