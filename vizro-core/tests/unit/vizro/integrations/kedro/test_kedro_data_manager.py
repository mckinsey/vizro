"""Unit tests for vizro.integrations.kedro."""

import types
from pathlib import Path

import pytest
import yaml

kedro = pytest.importorskip("kedro")

import kedro.pipeline as kp  # noqa: E402
from kedro.io import DataCatalog  # noqa: E402

from vizro.integrations.kedro import datasets_from_catalog  # noqa: E402


@pytest.fixture
def catalog_path():
    return Path(__file__).parent / "fixtures/test_catalog.yaml"


def test_datasets_from_catalog(catalog_path):
    catalog = DataCatalog.from_config(yaml.safe_load(catalog_path.read_text(encoding="utf-8")))

    datasets = datasets_from_catalog(catalog)
    assert isinstance(datasets, dict)
    assert set(datasets) == {"pandas_excel", "pandas_parquet"}
    for dataset in datasets.values():
        assert isinstance(dataset, types.MethodType)


def test_datasets_from_catalog_with_pipeline(catalog_path):
    catalog = DataCatalog.from_config(yaml.safe_load(catalog_path.read_text(encoding="utf-8")))
    pipeline = kp.pipeline(
        [
            kp.node(
                func=lambda *args: None,
                inputs=["pandas_excel", "something#csv", "not_dataframe", "not_in_catalog", "pandas_parquet", "parameters", "params:z"],
                outputs=None,
            ),
        ]
    )

    datasets = datasets_from_catalog(catalog, pipeline=pipeline)
    assert set(datasets) == {"pandas_excel", "pandas_parquet", "something#csv"}
