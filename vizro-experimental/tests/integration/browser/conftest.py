"""Browser-suite fixtures.

Shared subprocess + URL helpers live in ``tests/integration/conftest.py``. This
file overrides ``popup_app_url`` with a dummy ``OPENAI_API_KEY`` (no LLM calls
happen in the browser suite, but ``add_chat_popup`` validates the key at build
time) and adds Playwright + send-icon helpers used only here.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Browser, Page, sync_playwright
from tests.integration.conftest import serve_popup_app

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


@pytest.fixture(scope="session")
def popup_app_url():
    """Override: browser tests don't hit the LLM.

    A dummy ``OPENAI_API_KEY`` bypasses ``add_chat_popup``'s api-key validation at
    build time without sending real requests if a callback misfires.
    """
    with serve_popup_app(extra_env={"OPENAI_API_KEY": "sk-test-dummy"}) as url:
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
