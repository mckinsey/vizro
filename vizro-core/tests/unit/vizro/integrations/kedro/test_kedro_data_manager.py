"""Unit tests for vizro.integrations.kedro."""
import types
from pathlib import Path

import pytest
import yaml
from kedro.io import DataCatalog

from vizro.integrations.kedro import datasets_from_catalog


@pytest.fixture
def catalog_path():
    return Path(__file__).parent / "fixtures/test_catalog.yaml"


def test_datasets_from_catalog(catalog_path):
    catalog = DataCatalog.from_config(yaml.safe_load(catalog_path.read_text(encoding="utf-8")))
    assert "companies" in datasets_from_catalog(catalog)
    assert isinstance(datasets_from_catalog(catalog), dict)
    assert isinstance(datasets_from_catalog(catalog)["companies"], types.MethodType)
