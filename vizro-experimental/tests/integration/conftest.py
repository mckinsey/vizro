"""Shared integration-test fixtures for both the browser and LLM suites.

Each example app is launched in its own ``python -c`` subprocess so the two
``Vizro()`` instances never share ``model_manager`` / ``dash.Dash`` state — the
same isolation vizro-core's e2e suite gets via ``dash.testing``.

Sub-conftests can override individual fixtures: ``browser/conftest.py`` shadows
``popup_app_url`` to inject a dummy ``OPENAI_API_KEY`` because it only exercises
clientside open/close wiring (``add_chat_popup`` validates the key at build time).
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from textwrap import dedent
from urllib.request import urlopen

import pytest

_EXAMPLES_DIR = Path(__file__).parents[2] / "examples"
_CHAT_EXAMPLE_DIR = str(_EXAMPLES_DIR / "chat_component")
_POPUP_EXAMPLE_DIR = str(_EXAMPLES_DIR / "popup")


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_ready(url: str, timeout: float = 30.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    return
        except OSError:  # noqa: PERF203 — readiness poll: catch is the natural loop shape
            time.sleep(0.2)
    raise TimeoutError(f"Dash app at {url} did not become ready within {timeout}s")


_MAIN_APP_SCRIPT = dedent(
    """
    import sys
    sys.path.insert(0, r"{example_dir}")
    import app as app_module
    from vizro import Vizro
    vizro = Vizro()
    vizro.build(app_module.dashboard)
    vizro.dash.server.run(host="127.0.0.1", port={port}, debug=False, use_reloader=False)
    """
).strip()

_POPUP_APP_SCRIPT = dedent(
    """
    import sys
    sys.path.insert(0, r"{example_dir}")
    import app as popup_module
    from vizro import Vizro
    from vizro_experimental.chat.popup import add_chat_popup
    vizro = Vizro()
    vizro.build(popup_module.dashboard)
    add_chat_popup(vizro, title="Chat Assistant", placeholder="Ask me anything about the data...")
    vizro.dash.server.run(host="127.0.0.1", port={port}, debug=False, use_reloader=False)
    """
).strip()


def _shutdown(proc: subprocess.Popen) -> None:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@contextmanager
def _serve(script_template: str, example_dir: str, extra_env: dict[str, str] | None = None):
    port = _find_free_port()
    code = script_template.format(example_dir=example_dir, port=port)
    env = {**os.environ, **(extra_env or {})}
    proc = subprocess.Popen([sys.executable, "-c", code], env=env)
    try:
        _wait_ready(f"http://127.0.0.1:{port}/")
        yield f"http://127.0.0.1:{port}"
    finally:
        _shutdown(proc)


@contextmanager
def serve_popup_app(extra_env: dict[str, str] | None = None):
    """Spawn the popup example app in a subprocess; yield the URL.

    Public helper for sub-conftests that need to vary the env (e.g. injecting a
    dummy ``OPENAI_API_KEY`` for clientside-only browser tests). Sub-conftests
    should call this rather than reaching into private ``_serve`` / script-template
    symbols.
    """
    with _serve(_POPUP_APP_SCRIPT, _POPUP_EXAMPLE_DIR, extra_env=extra_env) as url:
        yield url


@pytest.fixture(scope="session")
def chat_app_url():
    """URL of the multi-page chat-component example app (``examples/chat_component``)."""
    with _serve(_MAIN_APP_SCRIPT, _CHAT_EXAMPLE_DIR) as url:
        yield url


@pytest.fixture(scope="session")
def popup_app_url():
    """URL of the popup example app (``examples/popup``).

    Uses the inherited environment, so a real ``OPENAI_API_KEY`` is required for the
    popup's auto-agent to actually answer questions. The browser suite overrides
    this with a dummy key for clientside-only tests.
    """
    with serve_popup_app() as url:
        yield url
