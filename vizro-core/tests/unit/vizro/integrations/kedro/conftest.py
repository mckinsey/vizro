from pathlib import Path

import pytest


@pytest.fixture
def catalog_path():
    return Path(__file__).parent / "fixtures/test_catalog.yaml"
