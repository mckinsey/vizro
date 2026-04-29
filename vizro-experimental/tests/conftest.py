"""Top-level pytest configuration.

Auto-tags integration tests by directory so the default ``pytest tests`` run only
collects unit tests; the markers are excluded in ``[tool.pytest.ini_options]``
``addopts`` in ``pyproject.toml``. Run integration suites explicitly via
``hatch run test-integration-browser`` / ``hatch run test-integration-llm``.
"""

from __future__ import annotations

import pytest


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    # ``Path.as_posix()`` normalizes separators so the substring check works on Windows too.
    for item in items:
        posix = item.path.as_posix()
        if "/integration/browser/" in posix:
            item.add_marker(pytest.mark.integration_browser)
        elif "/integration/llm/" in posix:
            item.add_marker(pytest.mark.integration_llm)
