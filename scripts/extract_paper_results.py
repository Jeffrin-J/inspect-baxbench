"""Extract the paper's published results into docs/paper_results.json.

The BaxBench paper (arXiv:2502.11844v3) reports its results only as bar
charts. Its LaTeX source includes each chart as a matplotlib PDF, so this reads
the bar heights from those PDFs, for the default setting (OpenAPI spec, no
security reminder):

- overall pass@1 and sec_pass@1 for the 11 models (Figure 3), and
- per-framework pass@1 and sec_pass@1 for each model (Appendix D.4).

Overall values agree with the percentage labels printed on Figure 3.

    uv run python scripts/extract_paper_results.py
"""

import io
import json
import tarfile
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

import pdfplumber

SOURCE_URL = "https://arxiv.org/e-print/2502.11844v3"
OUTPUT = Path(__file__).parent.parent / "docs" / "paper_results.json"

# Fill colours of the stacked bars. Dark red is "Correct and Secure" in the no
# security reminder setting; the hatched "H*" fills are the setting outlines.
_SECURE_NO_REMINDER = (0.6980392157, 0.1333333333, 0.1333333333)

# Figure file names -> model names as the paper's text uses them.
MODELS = {
    "o3-mini": "OpenAI o3-mini",
    "deepseek-ai-DeepSeek-R1": "DeepSeek R1",
    "claude-3-5-sonnet-latest": "Claude 3.5 Sonnet",
    "o1": "OpenAI o1",
    "gpt-4o": "GPT-4o",
    "deepseek-ai-DeepSeek-V3": "DeepSeek V3",
    "mistralai-codestral-2501": "Codestral",
    "Qwen-Qwen2.5-Coder-32B-Instruct": "Qwen2.5 Coder",
    "meta-llama-Llama-3.3-70B-Instruct-Turbo": "Llama 3.3 70B",
    "Qwen-Qwen2.5-72B-Instruct-Turbo": "Qwen2.5 72B",
    "Qwen-Qwen2.5-7B-Instruct-Turbo": "Qwen2.5 7B",
}


def _is_secure_bar(rect: dict[str, Any]) -> bool:
    color = rect.get("non_stroking_color")
    return isinstance(color, tuple) and all(
        abs(a - b) < 1e-6 for a, b in zip(color, _SECURE_NO_REMINDER, strict=True)
    )


def _filled(page: Any) -> list[dict[str, Any]]:
    return [r for r in page.rects if r["fill"]]


def _percent(top: float, zero: float, full: float) -> float:
    return round((zero - top) / (zero - full) * 100, 1)


def overall(pdf_path: Path) -> list[dict[str, Any]]:
    """Read Figure 3: one stacked bar per model, ordered as in MODELS."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        rects = _filled(page)
        # Each model's bar is a full-height "Incorrect" outline (H1), then the
        # pass@1 bar (H2), then the sec_pass@1 bar (dark red), same x range.
        outlines = sorted(
            (r for r in rects if r["non_stroking_color"] == "H1"), key=lambda r: r["x0"]
        )
        results = []
        for model, outline in zip(MODELS.values(), outlines, strict=True):
            same = [r for r in rects if abs(r["x0"] - outline["x0"]) < 1]
            zero, full = outline["bottom"], outline["top"]
            correct = next(r for r in same if r["non_stroking_color"] == "H2")
            secure = [r for r in same if _is_secure_bar(r)]
            results.append(
                {
                    "model": model,
                    "correct": _percent(correct["top"], zero, full),
                    "secure": _percent(secure[0]["top"], zero, full) if secure else 0.0,
                }
            )
        return results


def per_framework(pdf_path: Path) -> dict[str, dict[str, float]]:
    """Read one model's Appendix D.4 figure: three bars per framework (no,
    generic, oracle security reminder); we keep the first."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        rects = _filled(page)
        groups = sorted(
            (r for r in rects if r["non_stroking_color"] == "H1"), key=lambda r: r["x0"]
        )
        zero = groups[0]["bottom"]
        # Labels are rotated 45 degrees, so x + y is nearly constant along one
        # label and jumps between neighbouring labels.
        chars = sorted(
            (c for c in page.chars if c["top"] > zero), key=lambda c: c["x0"] + c["bottom"]
        )
        labels: list[list[dict[str, Any]]] = [[chars[0]]]
        for prev, char in zip(chars, chars[1:], strict=False):
            if char["x0"] + char["bottom"] - (prev["x0"] + prev["bottom"]) > 12:
                labels.append([])
            labels[-1].append(char)
        if len(labels) != len(groups):
            raise RuntimeError(f"{pdf_path.name}: {len(labels)} labels for {len(groups)} bars")

        results = {}
        for label, group in zip(labels, groups, strict=True):
            name = "".join(c["text"] for c in sorted(label, key=lambda c: c["x0"]))
            # The paper stars multi-file frameworks.
            name = name.replace("*", "")
            # The first narrow bar in the group is the no-reminder setting.
            first = [
                r
                for r in rects
                if abs(r["x0"] - group["x0"]) < 1 and r["width"] < group["width"] / 2
            ]
            # A bar at 0% isn't drawn.
            correct = [r["top"] for r in first if r["non_stroking_color"] == "H2"]
            secure = [r["top"] for r in first if _is_secure_bar(r)]
            results[name] = {
                "correct": _percent(min(correct), zero, group["top"]) if correct else 0.0,
                "secure": _percent(secure[0], zero, group["top"]) if secure else 0.0,
            }
        return results


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        with urllib.request.urlopen(SOURCE_URL, timeout=120) as response:
            data = response.read()
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
            tar.extractall(tmp, filter="data")
        figures = Path(tmp) / "figures"
        results = {
            "source": SOURCE_URL,
            "setting": "OpenAPI spec, no security reminder",
            "sampling": "10 samples per task at temperature 0.4; 1 sample for o1, o3-mini and R1",
            "overall": overall(figures / "main" / "main_fig_im.pdf"),
            "per_framework": {
                name: per_framework(
                    figures
                    / "env_per_model"
                    / f"env_per_model_{key}"
                    / f"env_per_model_{key}_im.pdf"
                )
                for key, name in MODELS.items()
            },
        }
    OUTPUT.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
