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
