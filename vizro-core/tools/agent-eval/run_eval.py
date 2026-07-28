"""Runner for the Vizro docs agent eval suite.

Loads prompts.yaml, iterates over (model, prompt), calls the configured
agent for each, executes the produced code, scores each run against
rubric.md, and writes a summary.

The agent is expected to have access to the published Vizro docs (and
``llms.txt``) only. Register an agent callable via :func:`register_agent`,
or pass ``--agent`` on the command line to use one of the built-ins.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import threading
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("This runner needs PyYAML. Install with `pip install pyyaml`.\n")
    raise

try:
    import requests
except ImportError:
    sys.stderr.write("This runner needs requests. Install with `pip install requests`.\n")
    raise

RUBRIC_VERSION = 1

RENDER_BOOT_TIMEOUT_S = 15
RENDER_POST_BOOT_LOG_WINDOW_S = 2
RENDER_HTTP_TIMEOUT_S = 5
VALIDATE_TIMEOUT_S = 30

HTTP_OK = 200
PASSING_TOTAL = 5  # ≥ this out of 6 counts as a passing run in the summary

BOOT_MARKER = "__VIZRO_EVAL_BOOT_PORT__"
GIVEUP_MARKER = "##VIZRO_EVAL_GIVEUP##"


@dataclass
class Prompt:
    """One row from ``prompts.yaml``: a stable id, group, prompt text, and intent bullets."""

    id: str
    group: str
    prompt: str
    intent: list[str] = field(default_factory=list)


@dataclass
class RunResult:
    """Scored outcome of running one prompt against one model."""

    prompt_id: str
    model: str
    code: str
    score_validates: int
    score_renders: int
    score_intent: int
    tags: list[str] = field(default_factory=list)
    notes: str = ""

    @property
    def total(self) -> int:
        """Sum of the three per-criterion scores; ranges 0-6."""
        return self.score_validates + self.score_renders + self.score_intent


AgentCallable = Callable[[Prompt, str], str]
"""Signature: ``fn(prompt, model) -> python source code as a string``."""


AGENT: AgentCallable | None = None


def register_agent(fn: AgentCallable) -> None:
    """Register the docs-only agent-invocation callable."""
    global AGENT  # noqa: PLW0603 — module-level registry is the harness's public API
    AGENT = fn


def load_prompts(path: Path) -> list[Prompt]:
    """Parse ``prompts.yaml`` into a list of :class:`Prompt`."""
    data = yaml.safe_load(path.read_text())
    return [Prompt(**p) for p in data["prompts"]]


# ----------------------------------------------------------------------------
# Scoring
# ----------------------------------------------------------------------------

# Wrapper executed in a subprocess to construct-but-not-boot the agent's app.
#
# Import order matters: we import ``dash`` and ``vizro`` first so that
# DeprecationWarnings emitted by their own dependencies (e.g. urllib3) don't
# count against the agent. Then we install a warning filter that lets us
# distinguish "clean construction" (score 2) from "constructs with a Vizro or
# pydantic deprecation" (score 1). Actual construction errors bubble up as a
# non-zero exit code (score 0).
_VALIDATE_WRAPPER = r"""
import importlib.util
import sys
import warnings

import dash
import vizro
import vizro.models as vm

vizro.Vizro.run = lambda self, *a, **kw: None
dash.Dash.run = lambda self, *a, **kw: None

warnings.simplefilter("always")

spec = importlib.util.spec_from_file_location("agent_script", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

dashboards = [v for v in vars(mod).values() if isinstance(v, vm.Dashboard)]
if not dashboards:
    print("NO_DASHBOARD", file=sys.stderr)
    sys.exit(2)

print("OK")
"""


# Wrapper that actually boots the app. Patches ``.run`` to capture but not
# start the server if the agent's script calls it at module level, then boots
# once itself on a caller-supplied port so we can HTTP-check ``/``.
_RENDER_WRAPPER = r"""
import importlib.util
import sys

import dash
import vizro
import vizro.models as vm

_orig_vizro_run = vizro.Vizro.run
_orig_dash_run = dash.Dash.run
vizro.Vizro.run = lambda self, *a, **kw: None
dash.Dash.run = lambda self, *a, **kw: None

spec = importlib.util.spec_from_file_location("agent_script", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

dashboards = [v for v in vars(mod).values() if isinstance(v, vm.Dashboard)]
if not dashboards:
    print("NO_DASHBOARD", file=sys.stderr)
    sys.exit(2)
dashboard = dashboards[0]

vizro.Vizro.run = _orig_vizro_run
dash.Dash.run = _orig_dash_run

port = int(sys.argv[2])
print(f"{marker}={port}", flush=True)
vizro.Vizro().build(dashboard).run(host="127.0.0.1", port=port, debug=False)
""".replace("{marker}", BOOT_MARKER)


def _write_temp_script(code: str) -> Path:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
    return Path(f.name)


def _write_temp_wrapper(source: str) -> Path:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(source)
    return Path(f.name)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _child_env() -> dict[str, str]:
    env = os.environ.copy()
    env["VIZRO_LOG_LEVEL"] = "ERROR"
    return env


_VIZRO_DEPRECATION_RE = re.compile(
    r"deprecationwarning.*(?:vizro|pydantic)|(?:vizro|pydantic).*deprecationwarning",
    re.IGNORECASE | re.DOTALL,
)


def score_validates(code: str) -> tuple[int, list[str]]:
    """Criterion A: construct a Dashboard without errors or deprecation warnings."""
    tags: list[str] = []
    script = _write_temp_script(code)
    wrapper = _write_temp_wrapper(_VALIDATE_WRAPPER)

    try:
        proc = subprocess.run(  # noqa: S603
            [sys.executable, "-u", str(wrapper), str(script)],
            capture_output=True,
            text=True,
            timeout=VALIDATE_TIMEOUT_S,
            env=_child_env(),
            check=False,
        )
    except subprocess.TimeoutExpired:
        return 0, ["timeout-on-import"]
    finally:
        script.unlink(missing_ok=True)
        wrapper.unlink(missing_ok=True)

    if proc.returncode != 0:
        err_lower = proc.stderr.lower()
        if "no_dashboard" in err_lower:
            tags.append("no-dashboard-instance")
        if "modulenotfounderror" in err_lower or "importerror" in err_lower:
            tags.append("wrong-import")
        if "validationerror" in err_lower or "pydantic" in err_lower:
            tags.append("wrong-argument")
        if not tags:
            tags.append("construction-error")
        return 0, tags

    # Any DeprecationWarning that mentions Vizro or pydantic in its traceback
    # counts against the score; warnings from unrelated transitive deps do not.
    if _VIZRO_DEPRECATION_RE.search(proc.stderr):
        return 1, ["deprecation-warning"]

    return 2, tags


_ERROR_LOG_RE = re.compile(r"\bERROR\b|Traceback \(most recent call last\)")


def _drain(stream, sink: list[str]) -> None:
    """Copy every line from ``stream`` into ``sink`` until EOF.

    Used as a background thread so the child pipe never fills and blocks the
    server, and so we always have the full log available at grading time.
    """
    sink.extend(stream)


def score_renders(code: str) -> tuple[int, list[str]]:
    """Criterion B: boot the dashboard and hit ``/`` once.

    Score 2 = HTTP 200 and no ERROR-level log records; 1 = 200 but ERROR
    records appeared; 0 = non-200, hang, or crash.

    Boot is detected by polling ``/`` until the server responds — parsing
    Werkzeug's stdout for a "Running on http://" line is unreliable because
    the click.echo path that emits it buffers differently to Dash's own log
    output when stdout+stderr are merged into a pipe.
    """
    script = _write_temp_script(code)
    wrapper = _write_temp_wrapper(_RENDER_WRAPPER)
    port = _free_port()

    proc = subprocess.Popen(  # noqa: S603
        [sys.executable, "-u", str(wrapper), str(script), str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=_child_env(),
    )

    captured: list[str] = []
    reader = threading.Thread(target=_drain, args=(proc.stdout, captured), daemon=True)
    reader.start()

    try:
        resp = None
        deadline = time.monotonic() + RENDER_BOOT_TIMEOUT_S
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                break
            try:
                resp = requests.get(f"http://127.0.0.1:{port}/", timeout=1)
                break
            except requests.RequestException:
                time.sleep(0.3)

        if resp is None:
            _kill(proc)
            reader.join(timeout=1)
            log = "".join(captured).lower()
            if "no_dashboard" in log:
                return 0, ["no-dashboard-instance"]
            if "traceback" in log:
                return 0, ["render-boot-crash"]
            return 0, ["render-boot-timeout"]

        # Let the server flush any ERROR-level records triggered by the request.
        time.sleep(RENDER_POST_BOOT_LOG_WINDOW_S)
        _kill(proc)
        reader.join(timeout=2)

        if resp.status_code != HTTP_OK:
            return 0, [f"render-http-{resp.status_code}"]

        log = "".join(captured)
        if _ERROR_LOG_RE.search(log):
            return 1, ["render-error-log"]

        return 2, []
    finally:
        script.unlink(missing_ok=True)
        wrapper.unlink(missing_ok=True)
        if proc.poll() is None:
            _kill(proc)


def _kill(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=3)


def score_intent(code: str, prompt: Prompt) -> tuple[int, list[str]]:
    """Criterion C: does the produced dashboard satisfy the prompt's intent?

    Stub. Recommended implementation:
        1. Load the produced module (via the same wrapper as ``score_validates``).
        2. Locate the ``vm.Dashboard`` instance and call ``.model_dump()``.
        3. Run a per-prompt check function that returns bool per intent bullet.
        4. Score 2 if all pass, 1 if most pass, 0 otherwise.
    """
    raise NotImplementedError("score_intent is a stub. Implement per-prompt checks (see docstring).")


def _extract_giveup_reason(code: str) -> str:
    """Return the free-text reason a giveup reply included after the marker.

    Everything after the first ``GIVEUP_MARKER`` occurrence up to the end of
    the reply is treated as the reason. Whitespace is trimmed. If the reply
    is malformed (marker at the very end), the returned reason is empty.
    """
    _, _, tail = code.partition(GIVEUP_MARKER)
    return tail.strip()


def run_one(prompt: Prompt, model: str) -> RunResult:
    """Ask the registered agent for code, then score it against all three criteria.

    Handles the giveup path specially: if the agent's reply contains the
    ``GIVEUP_MARKER``, we do not attempt to score the output as code. Instead
    we record a zero-scored ``agent-gave-up`` outcome with the reason in
    ``notes`` — this is the highest-value signal for the docs team.
    """
    if AGENT is None:
        raise RuntimeError("No agent callable registered. See register_agent or pass --agent.")

    code = AGENT(prompt, model)

    if GIVEUP_MARKER in code:
        return RunResult(
            prompt_id=prompt.id,
            model=model,
            code=code,
            score_validates=0,
            score_renders=0,
            score_intent=0,
            tags=["agent-gave-up"],
            notes=_extract_giveup_reason(code),
        )

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
        code=code,
        score_validates=validates_score,
        score_renders=renders_score,
        score_intent=intent_score,
        tags=validates_tags + renders_tags + intent_tags,
    )


def write_results(out_dir: Path, results: list[RunResult]) -> None:
    """Persist raw code, per-run JSONL scores, and a human-readable summary."""
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_dir = out_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    for r in results:
        (raw_dir / f"{r.model}-{r.prompt_id}.py").write_text(r.code)

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

    by_model: dict[str, list[RunResult]] = defaultdict(list)
    for r in results:
        by_model[r.model].append(r)

    for model, runs in sorted(by_model.items()):
        avg_val = sum(r.score_validates for r in runs) / len(runs)
        avg_ren = sum(r.score_renders for r in runs) / len(runs)
        avg_int = sum(r.score_intent for r in runs) / len(runs)
        pass_rate = sum(1 for r in runs if r.total >= PASSING_TOTAL) / len(runs)
        giveups = [r for r in runs if "agent-gave-up" in r.tags]
        summary_lines.append(
            f"## {model}\n"
            f"- Prompts run: {len(runs)}\n"
            f"- Avg validates: {avg_val:.2f}/2\n"
            f"- Avg renders: {avg_ren:.2f}/2\n"
            f"- Avg intent: {avg_int:.2f}/2\n"
            f"- Pass rate (>=5/6): {pass_rate:.0%}\n"
            f"- Giveups: {len(giveups)}/{len(runs)}\n",
        )

        # Failure-tag frequency, sorted, so the docs team can see the most
        # common failure modes at a glance.
        tag_counts: dict[str, int] = defaultdict(int)
        for r in runs:
            for t in r.tags:
                tag_counts[t] += 1
        if tag_counts:
            summary_lines.append("### Failure tags\n")
            for tag, n in sorted(tag_counts.items(), key=lambda kv: -kv[1]):
                summary_lines.append(f"- `{tag}`: {n}")
            summary_lines.append("")

        # Giveup reasons are the most actionable docs-team signal, so surface
        # each one in full rather than just a count. If the model gave up
        # honestly, its reason names the docs section that failed to unblock
        # it.
        if giveups:
            summary_lines.append("### Prompts where the agent gave up\n")
            for r in sorted(giveups, key=lambda r: r.prompt_id):
                summary_lines.append(f"**{r.prompt_id}**\n")
                summary_lines.append(f"> {r.notes or '(no reason provided)'}\n")
            summary_lines.append("")

    (out_dir / "summary.md").write_text("\n".join(summary_lines))


# ----------------------------------------------------------------------------
# Built-in agent wiring
# ----------------------------------------------------------------------------

BUILT_IN_AGENTS = {"mock", "anthropic-docs-only"}


def _install_builtin_agent(name: str) -> None:
    """Resolve a ``--agent`` choice to the matching callable in ``agents.py``."""
    from agents import anthropic_docs_only, mock_agent

    if name == "mock":
        register_agent(mock_agent)
    elif name == "anthropic-docs-only":
        register_agent(anthropic_docs_only)
    else:
        raise ValueError(f"Unknown built-in agent {name!r}. Choose from {sorted(BUILT_IN_AGENTS)}.")


def main() -> None:
    """Parse CLI args, iterate every (model, prompt), score each, and write results."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prompts", type=Path, required=True)
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument(
        "--agent",
        choices=sorted(BUILT_IN_AGENTS),
        help="Built-in agent to use. Alternatively, import run_eval and call register_agent().",
    )
    ap.add_argument(
        "--only",
        nargs="+",
        metavar="PROMPT_ID",
        help="Run only these prompt ids (e.g. P01 P07). Useful for local iteration.",
    )
    args = ap.parse_args()

    if args.agent:
        # Ensure agents.py can be imported when running the script directly.
        sys.path.insert(0, str(Path(__file__).parent))
        _install_builtin_agent(args.agent)

    prompts = load_prompts(args.prompts)
    if args.only:
        wanted = set(args.only)
        prompts = [p for p in prompts if p.id in wanted]
        if not prompts:
            raise SystemExit(f"No prompts matched --only {args.only}")

    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out_dir = args.out / stamp

    results: list[RunResult] = []
    for model in args.models:
        for prompt in prompts:
            print(f"[{model}] {prompt.id} ({prompt.group}): running...", flush=True)  # noqa: T201
            result = run_one(prompt, model)
            print(  # noqa: T201
                f"[{model}] {prompt.id}: validates={result.score_validates} "
                f"renders={result.score_renders} intent={result.score_intent} "
                f"tags={result.tags}",
                flush=True,
            )
            results.append(result)

    write_results(out_dir, results)
    print(f"Wrote {len(results)} runs to {out_dir}")  # noqa: T201


if __name__ == "__main__":
    main()
