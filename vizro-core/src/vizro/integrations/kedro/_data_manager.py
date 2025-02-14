from __future__ import annotations

from importlib.metadata import version
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project
from kedro.pipeline import Pipeline
from packaging.version import parse

from vizro.managers._data_manager import pd_DataFrameCallable

if TYPE_CHECKING:
    from kedro.io import CatalogProtocol


def catalog_from_project(
    project_path: Union[str, Path], env: Optional[str] = None, extra_params: Optional[dict[str, Any]] = None
) -> CatalogProtocol:
    bootstrap_project(project_path)
    with KedroSession.create(
        project_path=project_path, env=env, save_on_close=False, extra_params=extra_params
    ) as session:
        return session.load_context().catalog


def pipelines_from_project(project_path: Union[str, Path]) -> Pipeline:
    bootstrap_project(project_path)
    from kedro.framework.project import pipelines

    return pipelines


def _legacy_datasets_from_catalog(catalog: CatalogProtocol) -> dict[str, pd_DataFrameCallable]:
    # The old version of datasets_from_catalog from before https://github.com/mckinsey/vizro/pull/1001.
    # This does not support dataset factories.
    # We keep this version to maintain backwards compatibility with 0.19.0 <= kedro < 0.19.9.
    # Note the pipeline argument does not exist.
    datasets = {}
    for name in catalog.list():
        dataset = catalog._get_dataset(name, suggest=False)
        if "pandas" in dataset.__module__:
            datasets[name] = dataset.load
    return datasets


def datasets_from_catalog(catalog: CatalogProtocol, *, pipeline: Pipeline = None) -> dict[str, pd_DataFrameCallable]:
    if parse(version("kedro")) < parse("0.19.9"):
        return _legacy_datasets_from_catalog(catalog)

    # This doesn't include things added to the catalog at run time but that is ok for our purposes.
    config_resolver = catalog.config_resolver
    kedro_datasets = config_resolver.config.copy()

    if pipeline:
        # Go through all dataset names that weren't in catalog and try to resolve them. Those that cannot be
        # resolved give an empty dictionary and are ignored.
        for dataset_name in set(pipeline.datasets()) - set(kedro_datasets):
            if dataset_config := config_resolver.resolve_pattern(dataset_name):
                kedro_datasets[dataset_name] = dataset_config

    vizro_data_sources = {}

    for dataset_name, dataset_config in kedro_datasets.items():
        # "type" key always exists because we filtered out patterns that resolve to empty dictionary above.
        if "pandas" in dataset_config["type"]:
            # TODO: in future update to use lambda: catalog.load(dataset_name) instead of _get_dataset
            #  but need to check if works with caching.
            dataset = catalog._get_dataset(dataset_name, suggest=False)
            vizro_data_sources[dataset_name] = dataset.load

    return vizro_data_sources
