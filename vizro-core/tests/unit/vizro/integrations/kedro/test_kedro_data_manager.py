"""Unit tests for vizro.integrations.kedro."""

from importlib.metadata import version
from pathlib import Path

import kedro.pipeline as kp
import pytest
from kedro.config import OmegaConfigLoader
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
    conf_loader = OmegaConfigLoader(conf_source=str(Path(__file__).parent))
    return catalog_class.from_config(conf_loader["catalog"])


def test_datasets_from_catalog(catalog, mocker):
    datasets = datasets_from_catalog(catalog)
    assert datasets == {"pandas_excel": mocker.ANY, "pandas_parquet": mocker.ANY}


def test_datasets_from_catalog_with_pipeline(catalog, mocker):
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
    expected_dataset_names = (
        {"pandas_excel", "pandas_parquet", "something#csv", "something_else#csv"}
        if parse(version("kedro")) >= parse("0.19.9")
        else {"pandas_excel", "pandas_parquet"}
    )

    assert datasets == {dataset_name: mocker.ANY for dataset_name in expected_dataset_names}
