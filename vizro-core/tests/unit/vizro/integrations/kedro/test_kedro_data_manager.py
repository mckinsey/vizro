"""Unit tests for vizro.integrations.kedro."""
import types

import pytest
import yaml

kedro = pytest.importorskip("kedro")
from kedro.io import DataCatalog  # noqa: E402

from vizro.integrations.kedro import datasets_from_catalog  # noqa: E402


def test_datasets_from_catalog(catalog_path):
    catalog = DataCatalog.from_config(yaml.safe_load(catalog_path.read_text(encoding="utf-8")))
    assert "companies" in datasets_from_catalog(catalog)
    assert isinstance(datasets_from_catalog(catalog), dict)
    assert isinstance(datasets_from_catalog(catalog)["companies"], types.MethodType)
