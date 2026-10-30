import pytest
from inspect_ai import eval
from inspect_ai.model import ModelOutput, get_model

from inspect_baxbench import baxbench
from inspect_baxbench.extraction import FILES_KEY, PARSE_FAILED_KEY, parse_response

APP = "from flask import Flask\napp = Flask(__name__)"


def single(response: str) -> dict[str, str] | None:
    return parse_response(response, multi_file=False, code_filename="app.py")


def multi(response: str) -> dict[str, str] | None:
    return parse_response(response, multi_file=True, code_filename=None)


# Single-file responses


def test_code_tags():
    assert single(f"<CODE>\n{APP}\n</CODE>") == {"app.py": APP}


def test_markdown_block():
    assert single(f"Here you go:\n```python\n{APP}\n```\nDone.") == {"app.py": APP}


def test_markdown_wins_over_code_tags():
    response = f"<CODE>\nprint('code tag')\n</CODE>\n```python\n{APP}\n```"
    assert single(response) == {"app.py": APP}


def test_first_block_is_used():
    response = f"```python\n{APP}\n```\n```python\nprint('second')\n```"
    assert single(response) == {"app.py": APP}


def test_markdown_inside_code_tags_keeps_inner_code():
    # The Markdown regex matches first, so the fences are not left in the file.
    assert single(f"<CODE>\n```python\n{APP}\n```\n</CODE>") == {"app.py": APP}


def test_bold_markers_are_stripped():
    assert single(f"<CODE>**{APP}**</CODE>") == {"app.py": APP}


def test_bash_blocks_are_ignored():
    assert single("```bash\npip install flask\n```") is None


def test_untagged_markdown_fence_is_not_matched():
    # Upstream quirk: the fence needs a language tag.
    assert single(f"```\n{APP}\n```") is None


def test_no_code_fails():
    assert single("I can't help with that.") is None


def test_single_file_needs_filename():
    with pytest.raises(ValueError):
        parse_response("<CODE>x</CODE>", multi_file=False, code_filename=None)


# Multi-file responses


def test_filepath_and_code_tags():
    response = (
        "<FILEPATH>\nsrc/main.ts\n</FILEPATH>\n<CODE>\nmain();\n</CODE>\n"
        "<FILEPATH>package.json</FILEPATH>\n<CODE>\n{}\n</CODE>"
    )
    assert multi(response) == {"src/main.ts": "main();", "package.json": "{}"}


def test_filepath_and_markdown_blocks():
    response = (
        "<FILEPATH>src/main.ts</FILEPATH>\n```typescript\nmain();\n```\n"
        "<FILEPATH>src/app.ts</FILEPATH>\n```typescript\napp();\n```"
    )
    assert multi(response) == {"src/main.ts": "main();", "src/app.ts": "app();"}


def test_code_tags_wrapping_markdown_are_unwrapped():
    # Counts differ for Markdown (1) and paths (2), so the <CODE> branch is used
    # and the Markdown fence inside the first block is removed.
    response = (
        "<FILEPATH>a.ts</FILEPATH>\n<CODE>\n```typescript\na();\n```\n</CODE>\n"
        "<FILEPATH>b.ts</FILEPATH>\n<CODE>\nb();\n</CODE>"
    )
    assert multi(response) == {"a.ts": "a();", "b.ts": "b();"}


def test_heading_filepaths():
    response = "### src/main.ts\n```typescript\nmain();\n```\n### src/app.ts\n```typescript\napp();\n```"
    assert multi(response) == {"src/main.ts": "main();", "src/app.ts": "app();"}


def test_paths_are_normalised_like_pathlib():
    response = "<FILEPATH>./src//main.ts</FILEPATH>\n<CODE>main();</CODE>"
    assert multi(response) == {"src/main.ts": "main();"}


def test_mismatched_counts_fail():
    response = "<FILEPATH>a.ts</FILEPATH>\n<FILEPATH>b.ts</FILEPATH>\n<CODE>a();</CODE>"
    assert multi(response) is None


def test_multi_file_without_paths_fails():
    assert multi(f"<CODE>{APP}</CODE>") is None


# The solver inside a full (mock) eval


def _run(response: str):
    model = get_model("mockllm/model", custom_outputs=[ModelOutput.from_content("mockllm/model", response)])
    task = baxbench(envs="Python-Flask", scenarios="Calculator", epochs=1)
    # score=False: these tests check extraction only, without building apps.
    [log] = eval(task, model=model, display="none", log_dir="logs/tests", score=False)
    return log.samples[0].store


def test_solver_stores_extracted_files():
    store = _run(f"<CODE>\n{APP}\n</CODE>")
    assert store[FILES_KEY] == {"app.py": APP}
    assert store[PARSE_FAILED_KEY] is False


def test_solver_records_parse_failure():
    store = _run("Sorry, no code today.")
    assert store[FILES_KEY] == {}
    assert store[PARSE_FAILED_KEY] is True
