"""Functions to use the Kedro Data Catalog inside Vizro.

Abstract: Usage documentation
    [How to integrate Vizro with the Kedro Data Catalog](../user-guides/kedro-data-catalog.md)
"""

from ._data_manager import catalog_from_project, datasets_from_catalog, pipelines_from_project

__all__ = ["catalog_from_project", "datasets_from_catalog", "pipelines_from_project"]
