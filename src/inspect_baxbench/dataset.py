"""Load BaxBench tasks from Hugging Face as Inspect samples."""

from typing import Any

from inspect_ai.dataset import Dataset, Sample, hf_dataset

from inspect_baxbench.prompts import SafetyPrompt, SpecType, build_prompt
from inspect_baxbench.scenarios import SCENARIOS

DATASET_PATH = "LogicStar/BaxBench"
# Pinned so the eval is reproducible (register requirement).
DATASET_REVISION = "f137be64a56f2e37aa218d97790f6525ca743f1f"

# Fields kept in sample metadata for the sandbox and scorer.
_METADATA_FIELDS = [
    "scenario_id",
    "env_id",
    "env_language",
    "env_framework",
    "env_extension",
    "env_multifile",
    "code_filename",
    "entrypoint_cmd",
    "needs_db",
    "needs_secret",
    "needed_packages",
    "potential_cwes",
    "port",
]


def record_to_sample(
    record: dict[str, Any], spec_type: SpecType, safety_prompt: SafetyPrompt
) -> Sample:
    # The HF dataset predates upstream v1.0.0, which changed install commands
    # (Alpine -> Debian images) and reworded some specs. Take the scenario
    # fields from v1.0.0 and only the per-framework fields from HF.
    scenario = SCENARIOS[record["scenario_id"]]
    record = {
        **record,
        "short_app_description": scenario["short_app_description"],
        "api_specification": scenario["api_spec"],
        "text_specification": scenario["text_spec"],
        "scenario_instructions": scenario["scenario_instructions"],
        "needs_db": scenario["needs_db"],
        "needs_secret": scenario["needs_secret"],
        "needed_packages": scenario["needed_packages"],
    }
    return Sample(
        id=record["task_id"],
        input=build_prompt(record, spec_type, safety_prompt),
        metadata={field: record[field] for field in _METADATA_FIELDS},
    )


def baxbench_dataset(
    spec_type: SpecType = "openapi",
    safety_prompt: SafetyPrompt = "none",
    envs: str | list[str] | None = None,
    scenarios: str | list[str] | None = None,
) -> Dataset:
    """Load BaxBench, optionally filtered to some frameworks or scenarios.

    Args:
        spec_type: Describe the API with the OpenAPI schema or in plain text.
        safety_prompt: Security reminder added to the prompt: "none", "generic",
            or "specific" (lists the CWEs the scenario is tested for).
        envs: Framework IDs to keep, e.g. ["Python-Flask", "Python-FastAPI"].
        scenarios: Scenario IDs to keep, e.g. ["Calculator", "Login"].
    """
    dataset = hf_dataset(
        DATASET_PATH,
        split="test",
        revision=DATASET_REVISION,
        sample_fields=lambda record: record_to_sample(record, spec_type, safety_prompt),
    )
    # `-T envs=Python-Flask` on the command line passes a single string.
    if isinstance(envs, str):
        envs = [envs]
    if isinstance(scenarios, str):
        scenarios = [scenarios]
    if envs is not None:
        unknown = set(envs) - {(s.metadata or {})["env_id"] for s in dataset}
        if unknown:
            raise ValueError(f"Unknown envs: {sorted(unknown)}")
        dataset = dataset.filter(lambda s: (s.metadata or {})["env_id"] in envs)
    if scenarios is not None:
        unknown = set(scenarios) - {(s.metadata or {})["scenario_id"] for s in dataset}
        if unknown:
            raise ValueError(f"Unknown scenarios: {sorted(unknown)}")
        dataset = dataset.filter(lambda s: (s.metadata or {})["scenario_id"] in scenarios)
    return dataset
