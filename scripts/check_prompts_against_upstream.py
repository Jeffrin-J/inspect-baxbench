"""Check that our prompts match the ones upstream BaxBench builds.

Needs the upstream repo cloned at reference/baxbench (see README). Docker does
not need to be running.

    uv run python scripts/check_prompts_against_upstream.py
"""

import collections
import difflib
import itertools
import sys
from pathlib import Path
from unittest import mock

from datasets import load_dataset

from inspect_baxbench.dataset import DATASET_PATH, DATASET_REVISION, record_to_sample

UPSTREAM_SRC = Path(__file__).parent.parent / "reference" / "baxbench" / "src"


def load_upstream() -> tuple[dict, dict]:
    sys.path.insert(0, str(UPSTREAM_SRC))
    # Upstream connects to Docker when env.base is imported.
    with mock.patch("docker.from_env"):
        from env import all_envs
        from scenarios import all_scenarios
    return {s.id: s for s in all_scenarios}, {e.id: e for e in all_envs}


def normalise(prompt: str) -> str:
    # Upstream lists CWEs in set order, which varies between runs; we sort them.
    lines = prompt.split("\n")
    cwe_lines = sorted(line for line in lines if line.startswith("CWE-"))
    other = [line for line in lines if not line.startswith("CWE-")]
    return "\n".join(other + cwe_lines)


def main() -> int:
    scenarios, envs = load_upstream()
    records = load_dataset(DATASET_PATH, split="test", revision=DATASET_REVISION)
    mismatches: collections.Counter[str] = collections.Counter()
    checked = 0
    for record, spec_type, safety_prompt in itertools.product(
        records, ["openapi", "text"], ["none", "generic", "specific"]
    ):
        scenario = scenarios[record["scenario_id"]]
        env = envs[record["env_id"]]
        expected = normalise(
            scenario.build_prompt(env, spec_type, safety_prompt, agent=False)
        )
        actual = normalise(record_to_sample(record, spec_type, safety_prompt).input)
        checked += 1
        if expected != actual:
            # Show one diff per scenario so each distinct cause is visible.
            if record["scenario_id"] not in mismatches:
                print(f"=== MISMATCH {record['task_id']} {spec_type} {safety_prompt}")
                diff = difflib.unified_diff(
                    expected.splitlines(),
                    actual.splitlines(),
                    "upstream",
                    "ours",
                    n=1,
                    lineterm="",
                )
                print("\n".join(list(diff)[:40]))
            mismatches[record["scenario_id"]] += 1
    print(f"Checked {checked} prompts, {sum(mismatches.values())} mismatches")
    for scenario_id, count in sorted(mismatches.items()):
        print(f"  {scenario_id}: {count}")
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
