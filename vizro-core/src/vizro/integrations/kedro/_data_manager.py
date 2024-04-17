from pathlib import Path
from typing import Any, Dict, Optional, Union

from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project
from kedro.io import DataCatalog

from vizro.managers._data_manager import pd_DataFrameCallable


def catalog_from_project(
    project_path: Union[str, Path], env: Optional[str] = None, extra_params: Optional[Dict[str, Any]] = None
) -> DataCatalog:
    bootstrap_project(project_path)
    with KedroSession.create(
        project_path=project_path, env=env, save_on_close=False, extra_params=extra_params
    ) as session:
        return session.load_context().catalog


def datasets_from_catalog(catalog: DataCatalog) -> Dict[str, pd_DataFrameCallable]:
    datasets = {}
    for name in catalog.list():
        dataset = catalog._get_dataset(name, suggest=False)
        if "pandas" in dataset.__module__:
            datasets[name] = dataset.load
    return datasets
