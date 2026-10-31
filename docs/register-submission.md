# Inspect Evals Register submission (draft)

Open a **Register Eval Submission** issue on UKGovernmentBEIS/inspect_evals and
fill in the form as below. Replace `<SHA>` with the full 40-character commit SHA
of the pushed commit that contains the rescored results (`git rev-parse HEAD`).

## Form fields

**arXiv URL**

```
https://arxiv.org/abs/2502.11844v3
```

**Source URL**

```
https://github.com/Jeffrin-J/inspect-baxbench/blob/<SHA>/src/inspect_baxbench/baxbench.py
```

**Maintainers**

```
Jeffrin-J
```

## Additional notes (paste into the issue body if the form has a free-text field, or as a first comment)

BaxBench (Vero et al., ICML 2025): 392 tasks asking for a complete backend app
(28 scenarios x 14 frameworks in 6 languages). The scorer builds each generated
app in Docker and runs upstream BaxBench's own functional tests and security
exploits against it.

For the security review:

- Model-generated code runs only inside Docker containers (one image per
  sample, a fresh container per test, 1 GB memory limit), as upstream does. It
  does not use an Inspect sandbox because the code is compiled at image build
  time and the tests are host-side Python functions that use the Docker SDK to
  inspect the container (read files, run SQL, check memory). Nothing generated
  by the model runs on the host.
- The scorer imports upstream's test code from GitHub at a pinned commit
  (v1.0.0, `a67abd942454a11ff2966674d498abc451a52d67`, MIT). The dataset is
  pinned to a Hugging Face revision.

Validation against the paper (all 392 tasks, default setting, 1 epoch):

| Model | Correct (ours / paper) | Secure (ours / paper) |
|---|---|---|
| DeepSeek V3 | <fill in after rescoring> / 40.3% | <...> / 19.4% |
| Llama 3.3 70B | <...> / 22.0% | <...> / 9.2% |

Per-framework comparisons and known differences from upstream are in the README.

## After the bot opens the PR

Upload the two de-identified logs from `logs/public/` to the log store as the
PR describes, then comment:

```
Uploaded logs for two full runs of all 392 samples:
- openrouter/deepseek/deepseek-chat (DeepSeek V3)
- openrouter/meta-llama/llama-3.3-70b-instruct (Llama 3.3 70B)
Local paths were removed from the test logs (scripts/deidentify_logs.py).
```
