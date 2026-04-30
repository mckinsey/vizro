"""Pytest configuration for the agent benchmark suite.

The suite is excluded from default `pytest` runs via the `-m "not benchmark"`
option in pyproject.toml; the hatch `test:benchmark` script passes its own
`-m benchmark` to override. An ``OPENAI_API_KEY`` env check skips the session
if the key is missing (prevents silent zero-cost "passes" in CI). A
session-scoped writer saves a markdown summary to ``tests/benchmark/report.md``
so results across runs are comparable.
"""

from __future__ import annotations

import os
import time
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

import pytest
from dotenv import load_dotenv
from tests.benchmark.cases import CASES

load_dotenv(Path(__file__).resolve().parents[2] / "examples" / ".env")


# Names consumed by tests/benchmark/test_agent_perf.py and its parametrize
# decorators — re-exported so static analyzers treat them as used module exports.
__all__ = ["REASONING_LEVELS", "SELECTED_EFFORTS", "record_result", "stream_response"]


REASONING_LEVELS: tuple[str, ...] = ("low", "medium", "high")

# Default: run all three effort levels. Override with BENCHMARK_EFFORTS="low"
# to iterate faster locally.
_efforts_env = os.environ.get("BENCHMARK_EFFORTS")
SELECTED_EFFORTS: tuple[str, ...] = (
    tuple(e.strip() for e in _efforts_env.split(",") if e.strip()) if _efforts_env else REASONING_LEVELS
)

_CASE_INDEX: dict[str, int] = {c.id: i for i, c in enumerate(CASES)}


@pytest.fixture(scope="session", autouse=True)
def _require_api_key():
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set — benchmark suite requires a live API key")


@pytest.fixture(scope="session")
def dashboard_built():
    """Build the example dashboard once for the whole session.

    The agent reads `data_manager` / `model_manager` state that only exists
    after `app.build(...)`, so we construct it here and reuse across tests.
    """
    import vizro.models as vm
    import vizro.plotly.express as px
    from vizro import Vizro
    from vizro.managers import data_manager

    # Register datasets by name so the system prompt exposes them as
    # `iris` / `gapminder`, not auto-generated UUIDs. This matches the real
    # dashboard-building pattern and makes benchmark assertions stable.
    data_manager["iris"] = px.data.iris()
    data_manager["gapminder"] = px.data.gapminder().query("year == 2007")

    page1 = vm.Page(
        title="Iris Scatter Plot",
        components=[vm.Graph(figure=px.scatter("iris", x="sepal_width", y="sepal_length", color="species"))],
    )
    page2 = vm.Page(
        title="Gapminder",
        components=[
            vm.Graph(
                figure=px.scatter(
                    "gapminder",
                    x="gdpPercap",
                    y="lifeExp",
                    color="continent",
                )
            )
        ],
    )
    app = Vizro()
    app.build(vm.Dashboard(pages=[page1, page2], theme="vizro_light"))
    return app


@pytest.fixture(scope="session")
def agents_by_effort(dashboard_built):
    """Lazy-init one agent per reasoning effort, cached for the session.

    Each test parametrized on (effort, case) reuses the same agent so we're
    not measuring repeated setup cost.

    Set ``BENCHMARK_MODEL`` to swap the default model while keeping the rest
    of the setup (tool, prompt, reasoning_effort) identical — useful for
    comparing a new model against the current default on the same cases.
    """
    from vizro_experimental.chat.popup.dashboard_agent import (
        create_dashboard_agent,
        make_generate_response,
    )

    cache: dict[str, Any] = {}
    model_override = os.environ.get("BENCHMARK_MODEL")

    def _get(effort: str):
        if effort not in cache:
            if model_override:
                from langchain_openai import ChatOpenAI

                # use_responses_api=True is required for gpt-5.4+ models when
                # combining reasoning_effort with function tools — the chat
                # completions endpoint returns 400 in that combination.
                model = ChatOpenAI(
                    model=model_override,
                    max_tokens=4096,
                    reasoning_effort=effort,
                    use_responses_api=True,
                )
                agent, _ = create_dashboard_agent(model=model)
            else:
                agent, _ = create_dashboard_agent(reasoning_effort=effort)  # type: ignore[arg-type]
            cache[effort] = make_generate_response(agent)
        return cache[effort]

    return _get


# Collected during the session, rendered by pytest_sessionfinish.
_RESULTS: dict[tuple[str, str], dict[str, Any]] = {}


def record_result(effort: str, case_id: str, **payload: Any) -> None:
    _RESULTS[(effort, case_id)] = payload


def pytest_sessionfinish(session, exitstatus):
    if not _RESULTS:
        return
    model_override = os.environ.get("BENCHMARK_MODEL") or "gpt-5.4-mini-2026-03-17 (default)"
    lines: list[str] = []
    lines.append("# Dashboard agent benchmark report\n")
    lines.append(f"Model: `{model_override}`\n")
    lines.append(f"Exit status: {exitstatus}\n")
    lines.append("")

    by_effort: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    for (effort, case_id), payload in _RESULTS.items():
        by_effort[effort].append((case_id, payload))

    # Summary table: median TTFT / total per effort level.
    lines.append("## Summary (median across cases)\n")
    lines.append("| Effort | Cases | TTFT p50 | Total p50 | Passed |")
    lines.append("|---|---|---|---|---|")
    for effort in REASONING_LEVELS:
        rows = by_effort.get(effort, [])
        if not rows:
            continue
        ttfts = [r[1]["ttft_s"] for r in rows]
        totals = [r[1]["total_s"] for r in rows]
        passed = sum(1 for _, r in rows if r["passed"])
        lines.append(
            f"| {effort} | {len(rows)} | {median(ttfts):.2f}s | {median(totals):.2f}s | {passed}/{len(rows)} |"
        )
    lines.append("")

    # Per-case breakdown.
    for effort in REASONING_LEVELS:
        rows = by_effort.get(effort, [])
        if not rows:
            continue
        lines.append(f"## reasoning_effort = `{effort}`\n")
        lines.append("| Case | TTFT | Total | Chars | Passed | Note |")
        lines.append("|---|---|---|---|---|---|")
        rows_sorted = sorted(rows, key=lambda r: _CASE_INDEX[r[0]])
        for case_id, payload in rows_sorted:
            mark = "PASS" if payload["passed"] else "FAIL"
            note = payload.get("failure_reason", "")
            lines.append(
                f"| `{case_id}` | {payload['ttft_s']:.2f}s | {payload['total_s']:.2f}s | "
                f"{payload['chars']} | {mark} | {note} |"
            )
        lines.append("")

    if os.environ.get("BENCHMARK_MODEL"):
        safe_name = os.environ["BENCHMARK_MODEL"].replace("/", "_").replace(":", "_")
        report_path = Path(__file__).parent / f"report_{safe_name}.md"
    else:
        report_path = Path(__file__).parent / "report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    # Benchmark is on-demand and runs with -v; stdout path is the expected surface.
    print(f"\nBenchmark report: {report_path}")  # noqa: T201


def stream_response(generate_response, question: str) -> tuple[float, float, str]:
    """Stream a single response and return (ttft_s, total_s, response_text)."""
    messages = [{"role": "user", "content": question}]
    t_start = time.perf_counter()
    t_first: float | None = None
    parts: list[str] = []
    for chunk in generate_response(messages):
        if t_first is None:
            t_first = time.perf_counter() - t_start
        parts.append(chunk)
    t_total = time.perf_counter() - t_start
    return (t_first or t_total), t_total, "".join(parts)
