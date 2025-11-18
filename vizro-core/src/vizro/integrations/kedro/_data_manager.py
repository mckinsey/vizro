from __future__ import annotations

from importlib.metadata import version
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project
from kedro.pipeline import Pipeline
from packaging.version import parse

# find_kedro_project was made public in 1.0.0.
if parse(version("kedro")) >= parse("1.0.0"):
    from kedro.utils import find_kedro_project
else:
    from kedro.utils import _find_kedro_project as find_kedro_project

from vizro.managers._data_manager import pd_DataFrameCallable

from kedro.io import DataCatalog


def _infer_project_path(project_path) -> Union[str, Path]:
    # Follows same logic as done interally in Kedro: if project_path not explicitly specified, try to find a Kedro
    # project above this point in the directory tree, and if that fails then use current working directory. If
    # project_path is not valid then bootstrap_project will raise an error.
    return project_path or find_kedro_project(Path.cwd()) or Path.cwd()


def catalog_from_project(project_path: Optional[Union[str, Path]] = None, **kwargs: Any) -> DataCatalog:
    """Fetches the Kedro Data Catalog for a Kedro project.

    Args:
        project_path: Path to the Kedro project root directory. If not specified then attempts to find a Kedro project
            in the current directory or above.

    Other Args:
        **kwargs: Keyword arguments to pass to `KedroSession.create`, for example `env`.

    Returns:
         Kedro Data Catalog.

    Examples:
        >>> from vizro.integrations import kedro as kedro_integration
        >>> catalog = kedro_integration.catalog_from_project("/path/to/kedro/project")
    """

    # todo: API docs, check narrative docs, then done
    if kwargs.get("save_on_close"):
        raise ValueError("`catalog_from_project` cannot run with `save_on_close=True`.")
    project_path = _infer_project_path(project_path)
    bootstrap_project(project_path)
    with KedroSession.create(project_path=project_path, save_on_close=False, **kwargs) as session:
        return session.load_context().catalog


def pipelines_from_project(project_path: Optional[Union[str, Path]] = None) -> dict[str, Pipeline]:
    """Fetches Kedro pipelines for a Kedro project.

    Args:
        project_path: Path to the Kedro project root directory. If not specified then attempts to find a Kedro project
            in the current directory or above.

    Returns:
         Mapping of pipeline names to pipelines.

    Examples:
        >>> from vizro.integrations import kedro as kedro_integration
        >>> pipelines = kedro_integration.pipelines_from_project("/path/to/kedro/project")
    """
    project_path = _infer_project_path(project_path)
    bootstrap_project(project_path)
    from kedro.framework.project import pipelines

    return pipelines


def _legacy_datasets_from_catalog(catalog: DataCatalog, pipeline: Pipeline = None) -> dict[str, pd_DataFrameCallable]:
    # The old version of datasets_from_catalog from before https://github.com/mckinsey/vizro/pull/1493.
    # This is used when catalog is an old DataCatalog rather than the new KedroDataCatalog (only possible in kedro <
    # 1.0.0).
    # This doesn't include things added to the catalog at run time but that is ok for our purposes.
    config_resolver = catalog.config_resolver
    kedro_datasets = config_resolver.config.copy()

    if pipeline:
        # Go through all dataset names that weren't in catalog and try to resolve them. Those that cannot be
        # resolved give an empty dictionary and are ignored.
        for dataset_name in set(pipeline.datasets()) - set(kedro_datasets):
            if dataset_config := config_resolver.resolve_pattern(dataset_name):
                kedro_datasets[dataset_name] = dataset_config

    def _catalog_release_load(dataset_name: str):
        # release is needed to clear the Kedro load version cache so that the dashboard always fetches the most recent
        # version rather than being stuck on the same version as when the app started.
        catalog.release(dataset_name)
        return catalog.load(dataset_name)

    vizro_data_sources = {}

    for dataset_name, dataset_config in kedro_datasets.items():
        # "type" key always exists because we filtered out patterns that resolve to empty dictionary above.
        if "pandas" in dataset_config["type"]:
            # We need to bind dataset_name=dataset_name early to avoid dataset_name late-binding to the last value in
            # the for loop.
            vizro_data_sources[dataset_name] = lambda dataset_name=dataset_name: _catalog_release_load(dataset_name)

    return vizro_data_sources


# Technically on Kedro the DATA_CATALOG_CLASS is constrained to implement the more general CatalogProtocol rather than
# DataCatalog (the default value for kedro>=1), which was called KedroDataCatalog < 1. Here we rely on it being
# DataCatalog rather than any implementation of CatalogProtocol, since DataCatalog provides the very useful filter
# method.
# Note there's also CatalogCommandsMixin that is implemented automatically when DATA_CATALOG_CLASS is DataCatalog (but
# not a subclass). We don't use any methods from this.
def datasets_from_catalog(catalog: DataCatalog, *, pipeline: Pipeline = None) -> dict[str, pd_DataFrameCallable]:
    """Fetches Kedro Dataset loading functions for a Kedro Data Catalog.

    Args:
        catalog: Kedro Data Catalog.
        pipeline: Optional Kedro pipeline. If specified, the factory-based Kedro datasets it defines are returned.

    Returns:
         Mapping of dataset names to dataset loading functions that can be used in the Vizro data manager.

    # TODO: update examples
    Examples:
        >>> from vizro.integrations import kedro as kedro_integration
        >>> dataset_loaders = kedro_integration.datasets_from_catalog(catalog)
    """
    # Legacy methods are only relevant for the case that catalog is the old DataCatalog that doesn't support
    # filter.
    if parse(version("kedro")) < parse("1.0.0") and not hasattr(catalog, "filter"):
        return _legacy_datasets_from_catalog(catalog, pipeline)

    if pipeline:
        # Resolve dataset factory patterns, i.e. datasets that are used in pipeline but not explicitly defined in the
        # catalog. After this, subsequent catalog.filter calls contain the resolved dataset patterns too.
        for dataset_name in set(pipeline.datasets()) - set(catalog.filter()):
            catalog.get(dataset_name)

    def _catalog_release_load(dataset_name: str):
        # release is needed to clear the Kedro load version cache so that the dashboard always fetches the most recent
        # version rather than being stuck on the same version as when the app started.
        catalog.release(dataset_name)
        return catalog.load(dataset_name)

    # We need to bind dataset_name=dataset_name early to avoid dataset_name late-binding to the last value in
    # the for loop.
    return {
        dataset_name: lambda dataset_name=dataset_name: _catalog_release_load(dataset_name)
        for dataset_name in catalog.filter(type_regex="pandas")
    }
