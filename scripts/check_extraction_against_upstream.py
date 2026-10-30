"""Check that our code extraction matches upstream BaxBench's Parser.

Runs both parsers over a set of response shapes for a single-file and a
multi-file framework. Needs reference/baxbench cloned (see README); Docker does
not need to be running.

    uv run python scripts/check_extraction_against_upstream.py
"""

import logging
import sys
from pathlib import Path
from unittest import mock

from inspect_baxbench.extraction import parse_response

UPSTREAM_SRC = Path(__file__).parent.parent / "reference" / "baxbench" / "src"

APP = "from flask import Flask\napp = Flask(__name__)"

RESPONSES = [
    f"<CODE>\n{APP}\n</CODE>",
    f"Here you go:\n```python\n{APP}\n```\nDone.",
    f"<CODE>\nprint('code tag')\n</CODE>\n```python\n{APP}\n```",
    f"```python\n{APP}\n```\n```python\nprint('second')\n```",
    f"<CODE>\n```python\n{APP}\n```\n</CODE>",
    f"<CODE>**{APP}**</CODE>",
    "```bash\npip install flask\n```",
    f"```\n{APP}\n```",
    "I can't help with that.",
    "<FILEPATH>\nsrc/main.ts\n</FILEPATH>\n<CODE>\nmain();\n</CODE>\n"
    "<FILEPATH>package.json</FILEPATH>\n<CODE>\n{}\n</CODE>",
    "<FILEPATH>src/main.ts</FILEPATH>\n```typescript\nmain();\n```\n"
    "<FILEPATH>src/app.ts</FILEPATH>\n```typescript\napp();\n```",
    "<FILEPATH>a.ts</FILEPATH>\n<CODE>\n```typescript\na();\n```\n</CODE>\n"
    "<FILEPATH>b.ts</FILEPATH>\n<CODE>\nb();\n</CODE>",
    "### src/main.ts\n```typescript\nmain();\n```\n### src/app.ts\n```typescript\napp();\n```",
    "<FILEPATH>./src//main.ts</FILEPATH>\n<CODE>main();</CODE>",
    "<FILEPATH>a.ts</FILEPATH>\n<FILEPATH>b.ts</FILEPATH>\n<CODE>a();</CODE>",
    "### Setup\nSome prose.\n```typescript\nmain();\n```",
]


def main() -> int:
    sys.path.insert(0, str(UPSTREAM_SRC))
    # Upstream connects to Docker when env.base is imported, and prompts.py
    # imports the Anthropic and OpenAI SDKs, which Parser never uses.
    sdk_stubs = {
        name: mock.MagicMock()
        for name in ("anthropic", "anthropic.types", "openai", "openai.types", "openai.types.chat")
    }
    with mock.patch("docker.from_env"), mock.patch.dict(sys.modules, sdk_stubs):
        from env import all_envs
        from prompts import Parser

    logger = logging.getLogger("check")
    logger.disabled = True
    single_env = next(e for e in all_envs if not e.is_multi_file)
    multi_env = next(e for e in all_envs if e.is_multi_file)

    mismatches = 0
    checked = 0
    for env in (single_env, multi_env):
        parser = Parser(env, logger)
        for response in RESPONSES:
            upstream = parser.parse_response(response)
            expected = (
                None
                if list(upstream) == [Path("failed")]
                else {p.as_posix(): code for p, code in upstream.items()}
            )
            actual = parse_response(response, env.is_multi_file, env.code_filename)
            checked += 1
            if expected != actual:
                mismatches += 1
                print(f"=== MISMATCH {env.id}\n{response!r}")
                print(f"  upstream: {expected!r}\n  ours:     {actual!r}")
    print(f"Checked {checked} responses, {mismatches} mismatches")
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
