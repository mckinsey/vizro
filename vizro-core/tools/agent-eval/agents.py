"""Docs-only agent callables for the Vizro eval harness.

An "agent callable" is a function ``(prompt, model) -> python source code`` that
the harness calls once per prompt. The agent is expected to have access to the
published Vizro docs only — no vizro-mcp, no vizro-e2e-flow skill.

Two agents are provided:

* :func:`mock_agent` — returns a hardcoded valid dashboard. Useful for smoke
  testing the harness without hitting a real API.
* :func:`anthropic_docs_only` — calls the Anthropic API with the prompt and
  optionally injects a ``llms.txt``-style docs bundle as context.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

MOCK_CODE = """\
import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro

df = px.data.iris()

dashboard = vm.Dashboard(
    pages=[
        vm.Page(
            title="Iris",
            components=[
                vm.Graph(
                    figure=px.scatter(
                        df, x="sepal_length", y="petal_width", color="species"
                    )
                )
            ],
        )
    ]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
"""


def mock_agent(prompt, model: str) -> str:
    """Return a fixed, valid Vizro dashboard regardless of prompt.

    Lets the harness be smoke-tested end-to-end without an API key.
    """
    return MOCK_CODE


SYSTEM_PROMPT = """You are a Vizro dashboard developer.

Reply with exactly one self-contained Python file that:
* imports from `vizro`, `vizro.models`, `vizro.plotly.express`, `vizro.actions`,
  `vizro.tables`, `vizro.figures`, `vizro.models.types` as needed;
* assigns the completed dashboard to a module-level variable named `dashboard`;
* ends with `if __name__ == "__main__": Vizro().build(dashboard).run()`.

Do not include any prose, explanation, or markdown outside the code. Do not
invent packages. Assume plotly.express sample datasets (iris, tips, gapminder)
are available via `vizro.plotly.express.data.<name>()`.
"""


def _extract_python(reply: str) -> str:
    """Pull the last fenced ``python`` block out of a model reply.

    Falls back to the raw reply if the model ignored the "no fences" instruction
    entirely and returned raw code.
    """
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", reply, re.DOTALL)
    if blocks:
        return blocks[-1].strip() + "\n"
    return reply.strip() + "\n"


def anthropic_docs_only(prompt, model: str) -> str:
    """Call the Anthropic API with the prompt, optionally injecting docs context.

    Requires ``ANTHROPIC_API_KEY`` in the environment. If
    ``VIZRO_EVAL_DOCS_FILE`` points at a readable file (typically
    ``vizro-core/docs/llms.txt``), its contents are prepended to the system
    prompt so the model reasons over the docs rather than its training-data
    recall alone.
    """
    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover - install-time check
        raise RuntimeError("anthropic package not installed. Install with `pip install anthropic`.") from exc

    if "ANTHROPIC_API_KEY" not in os.environ:
        raise RuntimeError("ANTHROPIC_API_KEY is not set in the environment.")

    system = SYSTEM_PROMPT
    docs_path = os.environ.get("VIZRO_EVAL_DOCS_FILE")
    if docs_path:
        docs = Path(docs_path).read_text(encoding="utf-8")
        system = (
            "The following is the current Vizro documentation. Use it as the "
            "primary reference.\n\n<vizro-docs>\n" + docs + "\n</vizro-docs>\n\n" + SYSTEM_PROMPT
        )

    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": prompt.prompt}],
    )
    reply = "".join(block.text for block in resp.content if getattr(block, "type", None) == "text")
    return _extract_python(reply)
