"""Extract the generated app's source files from a model response.

Ported from BaxBench's `Parser` (src/prompts.py, v1.0.0), MIT License,
Copyright (c) 2025 SRI Lab, LogicStar.ai. The fallback order and regexes are
kept as upstream has them, including their quirks, so that the same responses
parse to the same files. Notably, Markdown blocks only match when the fence has
a language tag (```python), and a "```bash" block is never treated as code.
"""

import re
from pathlib import PurePosixPath

from inspect_ai.solver import Generate, Solver, TaskState, solver

# Store keys written by `extract_code` and read by the scorer.
FILES_KEY = "baxbench_files"
PARSE_FAILED_KEY = "baxbench_parse_failed"

_FILEPATH_PATTERN = re.compile(r"<FILEPATH>(.+?)</FILEPATH>", re.DOTALL)
_HEADING_FILEPATH_PATTERN = re.compile(r"^###\s*(.+?)$", re.DOTALL | re.MULTILINE)
_MARKDOWN_PATTERN = re.compile(r"```(?!bash)\w+\n(.*?)\n```", re.DOTALL)
_CODE_PATTERN = re.compile(r"<CODE>(.+?)</CODE>", re.DOTALL)


def _clean(s: str) -> str:
    s = s.strip()
    if s.startswith("**"):
        s = s[2:]
    if s.endswith("**"):
        s = s[:-2]
    return s.strip()


def _markdown_blocks(response: str) -> list[str]:
    return [_clean(s) for s in _MARKDOWN_PATTERN.findall(response)]


def _code_blocks(response: str) -> list[str]:
    return [_clean(s) for s in _CODE_PATTERN.findall(response)]


def _parse_single_file(response: str, code_filename: str) -> dict[str, str] | None:
    markdown = _markdown_blocks(response)
    if markdown:
        return {code_filename: markdown[0]}
    code = _code_blocks(response)
    if code:
        return {code_filename: code[0]}
    return None


def _parse_multi_file(response: str) -> dict[str, str] | None:
    markdown = _markdown_blocks(response)
    code = _code_blocks(response)
    # Try <FILEPATH> tags first, then "### path" headings.
    for pattern in (_FILEPATH_PATTERN, _HEADING_FILEPATH_PATTERN):
        # Upstream wraps paths in pathlib.Path, which drops "./" and repeated "/".
        paths = [str(PurePosixPath(_clean(s))) for s in pattern.findall(response)]
        if not paths:
            continue
        if len(paths) == len(markdown):
            return dict(zip(paths, markdown))
        if len(paths) == len(code):
            # A <CODE> block may itself wrap a Markdown block.
            unwrapped = [(_markdown_blocks(c) or [c])[0] for c in code]
            return dict(zip(paths, unwrapped))
    return None


def parse_response(
    response: str, multi_file: bool, code_filename: str | None
) -> dict[str, str] | None:
    """Return {relative file path: content}, or None if no code was found."""
    if multi_file:
        return _parse_multi_file(response)
    if code_filename is None:
        raise ValueError("Single-file environments need a code_filename")
    return _parse_single_file(response, code_filename)


@solver
def extract_code() -> Solver:
    """Parse the model's final response into files and save them in the store.

    Upstream writes a placeholder file when parsing fails, so the app cannot
    start and the sample counts as incorrect. We record the failure instead and
    let the scorer mark the sample incorrect without running anything.
    """

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        files = parse_response(
            state.output.completion,
            multi_file=state.metadata["env_multifile"],
            code_filename=state.metadata["code_filename"],
        )
        state.store.set(FILES_KEY, files or {})
        state.store.set(PARSE_FAILED_KEY, files is None)
        return state

    return solve
