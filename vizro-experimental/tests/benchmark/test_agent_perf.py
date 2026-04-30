"""On-demand benchmark suite measuring speed + quality by reasoning effort.

Run with:
    hatch run test:benchmark

Override effort levels to iterate faster locally:
    BENCHMARK_EFFORTS="minimal,low" hatch run test:benchmark

Output:
    - pytest PASS/FAIL per (effort, case) pair
    - per-case timing printed inline
    - markdown summary written to tests/benchmark/report.md
"""

from __future__ import annotations

import pytest
from tests.benchmark.cases import CASES, BenchmarkCase
from tests.benchmark.conftest import SELECTED_EFFORTS, record_result, stream_response


def _check_quality(case: BenchmarkCase, response: str) -> tuple[bool, str]:
    lowered = response.lower()
    if not response.strip():
        return False, "empty response"
    for needle in case.must_contain:
        if needle.lower() not in lowered:
            return False, f"missing expected substring: {needle!r}"
    for needle in case.must_not_contain:
        if needle.lower() in lowered:
            return False, f"contains forbidden substring: {needle!r}"
    return True, ""


@pytest.mark.benchmark
@pytest.mark.parametrize("effort", SELECTED_EFFORTS)
@pytest.mark.parametrize("case", CASES, ids=[c.id for c in CASES])
def test_agent_case(case: BenchmarkCase, effort: str, agents_by_effort, capsys):
    generate_response = agents_by_effort(effort)
    ttft_s, total_s, response = stream_response(generate_response, case.question)
    passed, reason = _check_quality(case, response)

    record_result(
        effort,
        case.id,
        ttft_s=ttft_s,
        total_s=total_s,
        chars=len(response),
        passed=passed,
        failure_reason=reason,
    )

    with capsys.disabled():
        # Inline per-case timing is the whole point of running this suite live with -v.
        print(  # noqa: T201
            f"\n  [{effort:<7} | {case.id:<28}] TTFT={ttft_s:5.2f}s  total={total_s:5.2f}s  "
            f"chars={len(response):>4}  {'PASS' if passed else 'FAIL: ' + reason}"
        )

    if not passed:
        snippet = response.strip().replace("\n", " ")[:300]
        pytest.fail(f"{case.id} @ {effort}: {reason}\nresponse preview: {snippet!r}")
