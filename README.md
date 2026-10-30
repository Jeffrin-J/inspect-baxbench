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

Docker must be running: every generated app is built and attacked in containers.

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
Responses with no parseable code set `baxbench_parse_failed` and are scored
incorrect without running anything.

## Scoring

The scorer downloads upstream BaxBench at the pinned commit (cached in
`~/.cache/inspect_baxbench`) and runs its own functional tests and exploits, the
same way upstream's `src/tasks.py` does: one image per sample, a fresh container
per test, a 300 s timeout per test, a 1 GB memory limit, and CWE-703 when a test
crashes the server.

| Metric | Meaning |
|---|---|
| `correct` | Every functional test passed (pass@1) |
| `secure` | Correct and no CWE found (sec_pass@1) |
| `insecure_correct` | Correct but exploitable |
| `insecure_given_correct` | Per task, the share of correct samples that were exploitable, averaged over tasks with a correct sample (upstream's "insec") |
| `build_failed` | Images that failed to build. A diagnostic: a high value usually means a Docker or network problem |

Each score's metadata has the CWEs found, test counts and the test log.
Task options: `test_timeout` (default 300) and `max_concurrent_tests` (default 4).

## Development

```bash
uv run pytest
# Also run the Docker end-to-end scorer tests (a few minutes)
RUN_DOCKER_TESTS=1 uv run pytest tests/test_scorer.py
# Score the hand-written apps in tests/apps directly
uv run python scripts/score_reference_apps.py
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
- Every upstream image is Debian 11 (bullseye), which reached end of life in August
  2026. Its packages are leaving deb.debian.org (some already return 404), so builds
  fail at upstream's `apt-get install sqlite3`. A line inserted right after each
  Dockerfile's `FROM` points apt at https://archive.debian.org, which serves the
  same package versions (`use_debian_archive`, on by default).
- Upstream leaves some build dependencies unpinned, and they have since moved
  past the toolchains in its images, so those builds fail today.
  `src/inspect_baxbench/env_patches.py` pins the newest versions that still work
  with each image's toolchain: goimports v0.36.0 (Go 1.23), a `Cargo.lock`
  resolved for Rust 1.83 (`scripts/generate_cargo_lock.sh`), Rails `~> 8.0.1`,
  and `json < 3` for Rails. The prompts are unchanged.
- Docker picks each container's host port (upstream uses a port pool), and images
  are deleted after testing.

Hand-written reference apps in `tests/apps` cover all 14 frameworks
(`scripts/score_reference_apps.py`). Each builds, passes its functional tests, and
has the expected CWEs found: a secure and an `eval()`-based Calculator on Flask,
and a Logger with log injection (CWE-117) on every framework.

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
  mapped port, using the Docker SDK directly (they read files, run SQL and check
  memory inside the container). Generated code is also processed at image build
  time (e.g. `go build`, `cargo build`, Rails migrations). So the scorer builds
  and runs containers itself, as upstream does, rather than using an Inspect
  sandbox, which would start before the code exists.
- Prompts (`src/prompts.py`, `scenarios/base.py`) ask for code inside `<CODE>` tags.
  There is also an agent mode where the model writes the app into `/app/code`.
