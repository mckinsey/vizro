"""Shared fixtures for secret-free browser-level integration tests.

Each example app is launched in its own ``python -c`` subprocess so the two
``Vizro()`` instances never share ``model_manager`` / ``dash.Dash`` state —
the same isolation vizro-core's e2e suite gets via ``dash.testing``.
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
from playwright.sync_api import Browser, Page, sync_playwright

_EXAMPLES_DIR = Path(__file__).parents[3] / "examples"
_CHAT_EXAMPLE_DIR = str(_EXAMPLES_DIR / "chat_component")
_POPUP_EXAMPLE_DIR = str(_EXAMPLES_DIR / "popup")

# Distinctive substrings of the two rendered Material Symbols Light send paths.
SEND_ICON_OUTLINED = "v-13"
SEND_ICON_FILLED = "v-5.154"

_SEND_ICON_PATH_POLL_JS = (
    "(sig) => { const p = document.querySelector('[id$=\"-send-icon\"] path');"
    " return !!p && p.getAttribute('d').includes(sig); }"
)


def wait_for_send_icon(page: Page, signature: str) -> None:
    """Wait until the rendered send-icon SVG path matches ``signature``."""
    page.wait_for_function(_SEND_ICON_PATH_POLL_JS, arg=signature)


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


@pytest.fixture(scope="session")
def app_url():
    with _serve(_MAIN_APP_SCRIPT, _CHAT_EXAMPLE_DIR) as url:
        yield url


@pytest.fixture(scope="session")
def popup_app_url():
    # ``add_chat_popup`` constructs ``ChatOpenAI`` at build time, which validates
    # ``api_key`` before any network call. The popup tests only exercise the
    # clientside open/close wiring, so a dummy key is enough.
    with _serve(_POPUP_APP_SCRIPT, _POPUP_EXAMPLE_DIR, extra_env={"OPENAI_API_KEY": "sk-test-dummy"}) as url:
        yield url


@pytest.fixture(scope="session")
def browser() -> Browser:
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture()
def page(browser: Browser) -> Page:
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    yield pg
    ctx.close()
