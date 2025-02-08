from pathlib import Path
from typing import Any, Optional, Union

from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project
from kedro.io import CatalogProtocol, KedroDataCatalog
from kedro.pipeline import Pipeline

from vizro.managers._data_manager import pd_DataFrameCallable


def catalog_from_project(
    project_path: Union[str, Path], env: Optional[str] = None, extra_params: Optional[dict[str, Any]] = None
) -> Union[CatalogProtocol, KedroDataCatalog]:
    bootstrap_project(project_path)
    with KedroSession.create(
        project_path=project_path, env=env, save_on_close=False, extra_params=extra_params
    ) as session:
        return session.load_context().catalog


def pipelines_from_project(project_path: Union[str, Path]) -> Pipeline:
    bootstrap_project(project_path)
    from kedro.framework.project import pipelines

    return pipelines


def datasets_from_catalog(
    catalog: Union[CatalogProtocol, KedroDataCatalog], *, pipeline: Pipeline = None
) -> dict[str, pd_DataFrameCallable]:
    # This doesn't include things added to the catalog at run time but that is ok for our purposes.
    config_resolver = catalog.config_resolver
    kedro_datasets = config_resolver.config.copy()

    if pipeline is not None:
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
