"""LLM-judge integration suite fixtures.

The shared ``chat_app_url`` and ``popup_app_url`` session fixtures live in
``tests/integration/conftest.py`` — they boot the example apps in subprocesses so
the suite is self-hosting; no manual ``hatch run example`` is required first. The
suite skips entirely when ``OPENAI_API_KEY`` is unset, since both the popup's
auto-agent and the LLM judge need a real key.
"""

from __future__ import annotations

import os

import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session", autouse=True)
def _require_api_key():
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set — LLM integration suite needs a real key")


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture()
def page(browser):
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()
    yield page
    context.close()
