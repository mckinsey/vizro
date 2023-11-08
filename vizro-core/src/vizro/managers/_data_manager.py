"""The data manager handles access to all DataFrames used in a Vizro app."""
import logging
import time
from typing import Callable, Dict, Optional, Union

import pandas as pd
from flask_caching import Cache

from vizro.managers._managers_utils import _state_modifier

logger = logging.getLogger(__name__)
# Really ComponentID and DatasetName should be NewType and not just aliases but then for a user's code to type check
# correctly they would need to cast all strings to these types.
ComponentID = str
DatasetName = str
pd_LazyDataFrame = Callable[[], pd.DataFrame]


class VizroDataSet:
    """A dataset with flask-caching config attached.

    Examples:
        >>> import plotly.express as px
        >>> data_manager["iris"] = VizroDataSet(lambda: pd.DataFrame(), timeout=300)
        >>> data_manager.__lazy_data["iris"]._cache_arguments == {"timeout": 300}
    """
    def __init__(self, data: pd_LazyDataFrame, timeout: Optional[int] = None, unless: Optional[Callable] = None):
        self.data = data
        self._cache_arguments: Dict[str, int] = {}
        self.set_cache_config(timeout, unless)

    def set_cache_config(self, timeout: int = None, unless: Callable = None):
        """Sets the cache configuration for the dataset."""
        self._cache_arguments["timeout"] = timeout
        self._cache_arguments["unless"] = unless
        logger.debug(f"set_cache_config: {self._cache_arguments}")


class DataManager:
    """Object to handle all data for the `vizro` application.

    Examples:
        >>> import plotly.express as px
        >>> data_manager["iris"] = px.data.iris()

    """

    _cache = Cache(config={"CACHE_TYPE": "SimpleCache"})

    def __init__(self):
        self.__lazy_data: Dict[DatasetName, VizroDataSet] = {}
        self.__original_data: Dict[DatasetName, pd.DataFrame] = {}
        self.__component_to_original: Dict[ComponentID, DatasetName] = {}
        self._frozen_state = False

    # happens before dashboard build
    @_state_modifier
    def __setitem__(self, dataset_name: DatasetName, data: Union[pd.DataFrame, pd_LazyDataFrame, VizroDataSet]):
        """Adds `data` to the `DataManager` with key `dataset_name`.

        This is the only user-facing function when configuring a simple dashboard. Others are only used internally
        in Vizro or advanced users who write their own actions.
        """
        if dataset_name in self.__original_data or dataset_name in self.__lazy_data:
            raise ValueError(f"Dataset {dataset_name} already exists.")

        if callable(data):
            data = VizroDataSet(data)
        elif isinstance(data, pd.DataFrame):
            self.__original_data[dataset_name] = data
        elif isinstance(data, VizroDataSet):
            pass
        else:
            raise TypeError(
                f"Dataset {dataset_name} must be a pandas DataFrame or callable that returns pandas DataFrame."
                f"Additionally, it can be a VizroDataSet object."
            )

        if isinstance(data, VizroDataSet):
            self.__lazy_data[dataset_name] = data

    def __getitem__(self, dataset_name: DatasetName) -> VizroDataSet:
        """Returns the `VizroDataSet` object associated with `dataset_name`."""
        if dataset_name not in self.__original_data and dataset_name not in self.__lazy_data:
            raise KeyError(f"Dataset {dataset_name} does not exist.")
        if dataset_name in self.__original_data:
            # no cache available
            raise ValueError(f"Dataset {dataset_name} is not lazy.")
        if dataset_name in self.__lazy_data:
            return self.__lazy_data[dataset_name]

    # happens before dashboard build
    @_state_modifier
    def _add_component(self, component_id: ComponentID, dataset_name: DatasetName):
        """Adds a mapping from `component_id` to `dataset_name`."""
        if dataset_name not in self.__original_data and dataset_name not in self.__lazy_data:
            raise KeyError(f"Dataset {dataset_name} does not exist.")
        if component_id in self.__component_to_original:
            raise ValueError(
                f"Component with id={component_id} already exists and is mapped to dataset "
                f"{self.__component_to_original[component_id]}. Components must uniquely map to a dataset across the "
                f"whole dashboard. If you are working from a Jupyter Notebook, please either restart the kernel, or "
                f"use 'from vizro import Vizro; Vizro._reset()`."
            )
        self.__component_to_original[component_id] = dataset_name

    def _load_lazy_data(self, dataset_name: DatasetName) -> pd.DataFrame:
        logger.debug("reloading lazy data: %s", dataset_name)

        @self._cache.memoize(**self.__lazy_data[dataset_name]._cache_arguments)
        # timeout (including 0 -> never expires), unless -> always executes function (like
        # timeout=0.000001) and doesn't update cache.
        # timeout and unless need to depend on dataset_name
        def inner(dataset):
            time.sleep(2.0)
            return self.__lazy_data[dataset].data()
        return inner(dataset_name)

    def _get_component_data(self, component_id: ComponentID) -> pd.DataFrame:
        """Returns the original data for `component_id`."""
        logger.debug("get_component_data: %s", component_id)
        if component_id not in self.__component_to_original:
            raise KeyError(f"Component {component_id} does not exist. You need to call add_component first.")
        dataset_name = self.__component_to_original[component_id]

        if dataset_name in self.__lazy_data:
            return self._load_lazy_data(dataset_name)
        else:  # dataset_name is in self.__original_data
            # Return a copy so that the original data cannot be modified. This is not necessary if we are careful
            # to not do any inplace=True operations, but probably safest to leave it here.
            return self.__original_data[dataset_name].copy()

    def _has_registered_data(self, component_id: ComponentID) -> bool:
        try:
            self._get_component_data(component_id)
            return True
        except KeyError:
            return False

    def _clear(self):
        self.__init__()  # type: ignore[misc]


data_manager = DataManager()


if __name__ == "__main__":
    from functools import partial

    import vizro.plotly.express as px

    dm = data_manager
    dm["iris"] = px.data.iris()

    dm._add_component("component_id_a", "iris")
    print(len(dm._get_component_data("component_id_a")))  # 150   # noqa: T201

    dm._add_component("component_id_b", "iris")
    df_a = dm._get_component_data("component_id_a")
    df_a.drop(columns="species", inplace=True)
    print(df_a.shape)  # (150, 5)   # noqa: T201
    df_b = dm._get_component_data("component_id_b")
    print(df_b.shape)  # (150, 6)   # noqa: T201

    # Lazy loading example 1
    def retrieve_iris():
        df = px.data.iris()
        subset = df.query("species == 'setosa'")
        return subset

    dm["iris_subset"] = retrieve_iris
    dm._add_component("component_id_c", "iris_subset")
    print(len(dm._get_component_data("component_id_c")))  # 50   # noqa: T201

    # Lazy loading example 2
    def retrieve_one_species(species):
        df = px.data.iris()
        subset = df[df["species"] == species].copy()
        return subset

    dm["data_from_external_1"] = lambda: retrieve_one_species("setosa")
    dm._add_component("component_id_d", "data_from_external_1")
    print(len(dm._get_component_data("component_id_d")))  # 50   # noqa: T201

    # Lazy loading example 3
    dm["data_from_external_2"] = partial(retrieve_one_species, "setosa")
    dm._add_component("component_id_e", "data_from_external_2")
    print(len(dm._get_component_data("component_id_e")))  # 50   # noqa: T201
