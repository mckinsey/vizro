"""Unit tests for vizro.integrations.kedro."""

import types
from importlib.metadata import version
from pathlib import Path

import kedro.pipeline as kp
import pytest
import yaml
from kedro.io import DataCatalog
from packaging.version import parse

from vizro.integrations.kedro import datasets_from_catalog

if parse(version("kedro")) >= parse("0.19.9"):
    # KedroDataCatalog only exists and hence can only be tested against in kedro>=0.19.9.
    from kedro.io import KedroDataCatalog

    data_catalog_classes = [DataCatalog, KedroDataCatalog]
else:
    data_catalog_classes = [DataCatalog]


@pytest.fixture(params=data_catalog_classes)
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
                    "something_else#csv",
                    "not_dataframe",
                    "not_in_catalog",
                    "parameters",
                    "params:z",
                ],
                outputs=None,
            ),
        ]
    )

    datasets = datasets_from_catalog(catalog, pipeline=pipeline)
    # Dataset factories only work for kedro>=0.19.9.
    expected_datasets = (
        {"pandas_excel", "pandas_parquet", "something#csv", "something_else#csv"}
        if parse(version("kedro")) >= parse("0.19.9")
        else {"pandas_excel", "pandas_parquet"}
    )

    assert set(datasets) == expected_datasets
