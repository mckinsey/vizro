import importlib
import sys

import pytest


class TestDeprecationWarning:
    def test_import_emits_deprecation_warning(self):
        sys.modules.pop("vizro_ai", None)

        with pytest.warns(DeprecationWarning, match="vizro-ai is deprecated"):
            importlib.import_module("vizro_ai")
