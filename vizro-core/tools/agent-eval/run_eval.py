"""Skeleton runner for the Vizro docs agent eval suite.

Loads prompts.yaml, iterates over (model, mode, prompt), calls the configured
agent for each combination, executes the produced code, scores each run
against rubric.md, and writes a summary.

Agent-invocation is deliberately abstract: register a callable per mode via
:func:`register_mode`. Without at least one registered mode, the runner
raises before making any calls.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable

try:
    import yaml
except ImportError:
    sys.stderr.write("This runner needs PyYAML. Install with `pip install pyyaml`.\n")
    raise

RUBRIC_VERSION = 1


@dataclass
class Prompt:
    id: str
    group: str
    prompt: str
    intent: list[str] = field(default_factory=list)


@dataclass
class RunResult:
    prompt_id: str
    model: str
    mode: str
    code: str
    score_validates: int
    score_renders: int
    score_intent: int
    tags: list[str] = field(default_factory=list)
    notes: str = ""

    @property
    def total(self) -> int:
        return self.score_validates + self.score_renders + self.score_intent


AgentCallable = Callable[[Prompt, str], str]
"""Signature: ``fn(prompt, model) -> python source code as a string``."""


MODES: dict[str, AgentCallable] = {}


def register_mode(name: str, fn: AgentCallable) -> None:
    """Register an agent-invocation callable for a mode."""

    MODES[name] = fn


def load_prompts(path: Path) -> list[Prompt]:
    data = yaml.safe_load(path.read_text())
    return [Prompt(**p) for p in data["prompts"]]


def score_validates(code: str) -> tuple[int, list[str]]:
    """Run the code in a subprocess and check that it constructs a Dashboard.

    Returns ``(score, tags)``. The subprocess should import the module and call
    ``dashboard = vm.Dashboard(...)`` cleanly.
    """

    tags: list[str] = []
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        f.write("\n\nimport warnings\n")
        f.write("warnings.filterwarnings('error', category=DeprecationWarning)\n")
        script = Path(f.name)

    try:
        proc = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=20,
            env={"VIZRO_LOG_LEVEL": "ERROR", "PATH": ""},
        )
    except subprocess.TimeoutExpired:
        return 0, ["timeout-on-import"]
    finally:
        script.unlink(missing_ok=True)

    if proc.returncode != 0:
        err = proc.stderr.lower()
        if "modulenotfounderror" in err or "importerror" in err:
            tags.append("wrong-import")
        if "validationerror" in err or "pydantic" in err:
            tags.append("wrong-argument")
        return 0, tags

    if "warning" in proc.stderr.lower() or "deprecationwarning" in proc.stderr.lower():
        return 1, ["deprecation-warning"]

    return 2, tags


def score_renders(code: str) -> tuple[int, list[str]]:
    """Boot the dashboard in a subprocess and hit ``/`` once.

    This is intentionally a stub. It requires a live Vizro install and a way
    to run a Dash app. Fill in with the eval harness's own boot loop, or
    replace with PyCafe's execution sandbox.
    """

    raise NotImplementedError(
        "score_renders is a stub. Wire this to your dashboard-boot harness (see docstring)."
    )


def score_intent(code: str, prompt: Prompt) -> tuple[int, list[str]]:
    """Compare the agent's dashboard against the prompt's intent bullets.

    Stub. Recommended implementation:
        1. Import the produced module.
        2. Call ``dashboard.model_dump()``.
        3. For each intent bullet, run a check function that returns bool.
        4. Score 2 if all pass, 1 if most pass, 0 otherwise.

    The checks depend on the prompt. Consider a lightweight registry in the
    eval harness (e.g. ``INTENT_CHECKS[prompt.id]``) rather than a monolithic
    matcher here.
    """

    raise NotImplementedError(
        "score_intent is a stub. Implement per-prompt checks (see docstring)."
    )


def run_one(prompt: Prompt, model: str, mode: str) -> RunResult:
    if mode not in MODES:
        raise RuntimeError(f"No agent callable registered for mode {mode!r}. See register_mode.")

    agent_fn = MODES[mode]
    code = agent_fn(prompt, model)

    validates_score, validates_tags = score_validates(code)
    try:
        renders_score, renders_tags = score_renders(code)
    except NotImplementedError:
        renders_score, renders_tags = 0, ["renders-not-implemented"]
    try:
        intent_score, intent_tags = score_intent(code, prompt)
    except NotImplementedError:
        intent_score, intent_tags = 0, ["intent-not-implemented"]

    return RunResult(
        prompt_id=prompt.id,
        model=model,
        mode=mode,
        code=code,
        score_validates=validates_score,
        score_renders=renders_score,
        score_intent=intent_score,
        tags=validates_tags + renders_tags + intent_tags,
    )


def write_results(out_dir: Path, results: list[RunResult]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_dir = out_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    for r in results:
        (raw_dir / f"{r.model}-{r.mode}-{r.prompt_id}.py").write_text(r.code)

    with (out_dir / "scores.jsonl").open("w") as f:
        for r in results:
            data = asdict(r)
            data.pop("code")
            data["total"] = r.total
            data["rubric_version"] = RUBRIC_VERSION
            f.write(json.dumps(data) + "\n")

    summary_lines: list[str] = [
        "# Vizro docs agent eval - summary",
        "",
        f"Rubric version: {RUBRIC_VERSION}",
        "",
    ]
    from collections import defaultdict

    by_pair: dict[tuple[str, str], list[RunResult]] = defaultdict(list)
    for r in results:
        by_pair[(r.model, r.mode)].append(r)

    for (model, mode), runs in sorted(by_pair.items()):
        avg_val = sum(r.score_validates for r in runs) / len(runs)
        avg_ren = sum(r.score_renders for r in runs) / len(runs)
        avg_int = sum(r.score_intent for r in runs) / len(runs)
        pass_rate = sum(1 for r in runs if r.total >= 5) / len(runs)
        summary_lines.append(
            f"## {model} - {mode}\n"
            f"- Prompts run: {len(runs)}\n"
            f"- Avg validates: {avg_val:.2f}/2\n"
            f"- Avg renders: {avg_ren:.2f}/2\n"
            f"- Avg intent: {avg_int:.2f}/2\n"
            f"- Pass rate (>=5/6): {pass_rate:.0%}\n",
        )

    (out_dir / "summary.md").write_text("\n".join(summary_lines))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prompts", type=Path, required=True)
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--modes", nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    prompts = load_prompts(args.prompts)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out_dir = args.out / stamp

    results: list[RunResult] = []
    for model in args.models:
        for mode in args.modes:
            for prompt in prompts:
                results.append(run_one(prompt, model, mode))

    write_results(out_dir, results)
    print(f"Wrote {len(results)} runs to {out_dir}")


if __name__ == "__main__":
    main()
