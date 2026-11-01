"""Compare an eval log with the paper's published results, as Markdown.

Prints overall and per-framework pass@1 and sec_pass@1 next to the paper's
numbers (docs/paper_results.json, from scripts/extract_paper_results.py).
The interval is a 95% Wilson score interval for our run's rate, from the
number of samples behind it; a paper value inside it is consistent with ours.
(Wilson rather than mean ± 1.96 SE, which collapses to ±0 at 0% or 100%.)

    uv run python scripts/compare_with_paper.py logs/<run>.eval "DeepSeek V3"
"""

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

from inspect_ai.log import read_eval_log

PAPER = Path(__file__).parent.parent / "docs" / "paper_results.json"


def wilson95(values: list[float]) -> tuple[float, float]:
    """95% Wilson score interval, in percent, for the rate of 0/1 values."""
    n = len(values)
    p = sum(values) / n
    z = 1.96
    centre = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    half = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return max(centre - half, 0) * 100, min(centre + half, 1) * 100


def _row(name: str, ours: list[float], paper: float) -> str:
    rate = sum(ours) / len(ours) * 100
    low, high = wilson95(ours)
    inside = "yes" if low <= paper <= high else "**no**"
    return f"| {name} | {rate:.1f} ({low:.1f}-{high:.1f}) | {paper:.1f} | {rate - paper:+.1f} | {inside} |"


def main(log_path: str, paper_model: str) -> None:
    paper = json.loads(PAPER.read_text(encoding="utf-8"))
    overall = next(r for r in paper["overall"] if r["model"] == paper_model)
    frameworks = paper["per_framework"][paper_model]

    log = read_eval_log(log_path)
    assert log.samples, "log has no samples"
    # One value per sample (epochs are scored separately in the log).
    by_env: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for sample in log.samples:
        assert sample.scores and sample.metadata
        value = next(iter(sample.scores.values())).as_dict()
        for metric in ("correct", "secure"):
            by_env[sample.metadata["env_id"]][metric].append(float(value[metric] or 0))
            by_env["all"][metric].append(float(value[metric] or 0))

    epochs = log.eval.config.epochs or 1
    print(f"Model: `{log.eval.model}` vs the paper's {paper_model}.")
    temperature = log.plan.config.temperature
    print(f"Our run: {len(log.samples)} samples ({epochs} epoch(s)) at temperature {temperature}.")
    print(f"Paper: {paper['sampling']}.\n")
    for metric, label in (("correct", "Correct (pass@1)"), ("secure", "Secure (sec_pass@1)")):
        print(f"| {label} | Ours, % (95% CI) | Paper, % | Difference | Paper in CI |")
        print("|---|---|---|---|---|")
        print(_row("**All 392 tasks**", by_env["all"][metric], overall[metric]))
        for env, published in frameworks.items():
            print(_row(env, by_env[env][metric], published[metric]))
        print()


if __name__ == "__main__":
    # The table uses "±", which the Windows console encoding lacks.
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    main(sys.argv[1], sys.argv[2])
