# inspect-baxbench

An [Inspect](https://inspect.aisi.org.uk/) implementation of
[BaxBench](https://arxiv.org/abs/2502.11844) (Vero et al., ICML 2025), a benchmark
for whether LLMs can generate backend applications that are both correct and secure.
Work in progress, aimed at the Inspect Evals register.

## Setup

Requirements: Python 3.12 (uv installs it), [uv](https://docs.astral.sh/uv/), and
Docker Desktop with the WSL2 backend.

```bash
uv sync
uv run inspect eval examples/smoke_test.py --model mockllm/model
```

## Usage

So far the task generates code only. Running the apps and scoring them is not built yet.

```bash
# Two Flask tasks with the mock model (no API key needed)
uv run inspect eval src/inspect_baxbench/baxbench.py --model mockllm/model -T envs=Python-Flask -T scenarios=Calculator,Login

# Options: spec_type=openapi|text, safety_prompt=none|generic|specific
uv run inspect eval src/inspect_baxbench/baxbench.py --model openai/gpt-4o-mini -T safety_prompt=generic
```

Defaults follow upstream: OpenAPI spec, no safety prompt, temperature 0.2, high
reasoning effort (for models that support it), 5 epochs per task averaged to
estimate pass@1, and the system prompt "You are an experienced full-stack developer".
Use `--epochs 1` for quick runs.

After generation, the app's files are extracted from the response with the same
rules as upstream's `Parser` and saved in the sample store (`baxbench_files`).
Responses with no parseable code set `baxbench_parse_failed` and will be scored
incorrect.

## Development

```bash
uv run pytest
# Check prompts and code extraction match upstream (needs reference/baxbench cloned)
uv run python scripts/check_prompts_against_upstream.py
uv run python scripts/check_extraction_against_upstream.py
```

Known differences from upstream:
- With `safety_prompt=specific`, CWEs are listed sorted by number. Upstream
  iterates over a Python set, so its order changes from run to run.
- The Hugging Face dataset (Feb 2025) predates upstream v1.0.0 (Sep 2025), which
  switched the images from Alpine to Debian and reworded the FrameExtract and
  Unsubscribe specs. Scenario fields therefore come from v1.0.0, extracted into
  `src/inspect_baxbench/scenarios.py` by `scripts/generate_scenarios.py` (reads the
  upstream source with `ast`, runs none of it). Only per-framework fields come from
  Hugging Face.

## Upstream sources

| Asset | Location | Pinned at |
|---|---|---|
| Paper | https://arxiv.org/abs/2502.11844 | |
| Code, tests, exploits | https://github.com/logic-star-ai/baxbench (MIT) | `v1.0.0` / `a67abd942454a11ff2966674d498abc451a52d67` |
| Dataset | https://huggingface.co/datasets/LogicStar/BaxBench (MIT) | `f137be64a56f2e37aa218d97790f6525ca743f1f` |

A read-only clone of the upstream code lives in `reference/baxbench` (git-ignored):

```bash
git clone --depth 1 --branch v1.0.0 https://github.com/logic-star-ai/baxbench.git reference/baxbench
```

## Notes on the upstream design

- Scenarios are in `src/scenarios/` (28 files). Each defines an OpenAPI spec,
  functional tests (`FunctionalTest`) and security tests (`SecurityTest`, which return
  the CWEs found).
- Frameworks are in `src/env/`, grouped by language (Python, JavaScript, Go, PHP, Ruby, Rust).
  Each environment has a Dockerfile template, and the app must listen on port 5000.
- The tests are Python functions run **on the host** against the container's
  mapped port, using the Docker SDK directly. Porting this to Inspect sandboxes is
  the main design decision.
- Prompts (`src/prompts.py`, `scenarios/base.py`) ask for code inside `<CODE>` tags.
  There is also an agent mode where the model writes the app into `/app/code`.
