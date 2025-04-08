"""Unit tests for vizro.integrations.kedro."""

from importlib.metadata import version
from pathlib import Path

import kedro.pipeline as kp
import pytest
from kedro.config import OmegaConfigLoader
from packaging.version import parse

from vizro.integrations.kedro import datasets_from_catalog

LEGACY_KEDRO = parse(version("kedro")) < parse("0.19.9")

if not LEGACY_KEDRO:
    # KedroDataCatalog only exists and hence can only be tested against in kedro>=0.19.9.
    # We could also still test against DataCatalog, but that would require filtering the deprecation warnings.
    # Since there is no development expected on DataCatalog before deprecation, we might as well only test
    # KedroDataCatalog
    from kedro.io import KedroDataCatalog

    data_catalog_classes = [KedroDataCatalog]
else:
    from kedro.io import DataCatalog

    data_catalog_classes = [DataCatalog]


@pytest.fixture(params=data_catalog_classes)
def catalog(request):
    catalog_class = request.param
    conf_loader = OmegaConfigLoader(conf_source=str(Path(__file__).parent))
    return catalog_class.from_config(conf_loader["catalog"])


def test_datasets_from_catalog(catalog, mocker):
    datasets = datasets_from_catalog(catalog)
    assert datasets == {"pandas_excel": mocker.ANY, "pandas_parquet": mocker.ANY}

    if not LEGACY_KEDRO:
        # Make sure that dataset_name is bound early to the data loading function.
        # Mocking for legacy kedro (tested by lower-bounds environment) would work differently but is not subject
        # to the same potential late-binding bug since it uses catalog._get_dataset so doesn't need to be tested.
        mocker.patch.object(catalog, "load")
        for dataset_name, dataset_loader in datasets.items():
            dataset_loader()
            catalog.load.assert_called_with(dataset_name)


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
        if not LEGACY_KEDRO
        else {"pandas_excel", "pandas_parquet"}
    )

    assert datasets == dict.fromkeys(expected_dataset_names, mocker.ANY)

    if not LEGACY_KEDRO:
        # Make sure that dataset_name is bound early to the data loading function.
        # Mocking for legacy kedro (tested by lower-bounds environment) would work differently but is not subject
        # to the same potential late-binding bug since it uses catalog._get_dataset so doesn't need to be tested.
        mocker.patch.object(catalog, "load")
        for dataset_name, dataset_loader in datasets.items():
            dataset_loader()
            catalog.load.assert_called_with(dataset_name)
