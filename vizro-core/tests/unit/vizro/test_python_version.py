import sys

import pytest

from vizro import _warn_deprecated_python_version


def test_python_310_emits_deprecation_warning(monkeypatch):
    monkeypatch.setattr(sys, "version_info", (3, 10, 0))
    with pytest.warns(FutureWarning, match="support will be removed"):
        _warn_deprecated_python_version()
