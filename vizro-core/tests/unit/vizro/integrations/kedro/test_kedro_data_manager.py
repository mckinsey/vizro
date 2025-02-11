"""Unit tests for vizro.integrations.kedro."""

import types
from pathlib import Path

import kedro.pipeline as kp
import pytest
import yaml
from kedro.io import DataCatalog, KedroDataCatalog

from vizro.integrations.kedro import datasets_from_catalog


@pytest.fixture(params=[DataCatalog, KedroDataCatalog])
def catalog(request):
    catalog_class = request.param
    catalog_path = Path(__file__).parent / "fixtures/test_catalog.yaml"
    return catalog_class.from_config(yaml.safe_load(catalog_path.read_text(encoding="utf-8")))


def test_datasets_from_catalog(catalog):
    datasets = datasets_from_catalog(catalog)
    assert isinstance(datasets, dict)
    assert set(datasets) == {"pandas_excel", "pandas_parquet"}
    for dataset in datasets.values():
        assert isinstance(dataset, types.MethodType)


def test_datasets_from_catalog_with_pipeline(catalog):
    pipeline = kp.pipeline(
        [
            kp.node(
                func=lambda *args: None,
                inputs=[
                    "pandas_excel",
                    "something#csv",
                    "not_dataframe",
                    "not_in_catalog",
                    "pandas_parquet",
                    "parameters",
                    "params:z",
                ],
                outputs=None,
            ),
        ]
    )

    datasets = datasets_from_catalog(catalog, pipeline=pipeline)
    assert set(datasets) == {"pandas_excel", "pandas_parquet", "something#csv"}
