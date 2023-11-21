"""The data manager handles access to all DataFrames used in a Vizro app."""
import logging
import time
from typing import Callable, Dict, Optional, Union

import flask
import pandas as pd
from flask_caching import Cache

from vizro.managers._managers_utils import _state_modifier

logger = logging.getLogger(__name__)
# Really ComponentID and DatasetName should be NewType and not just aliases but then for a user's code to type check
# correctly they would need to cast all strings to these types.
ComponentID = str
DatasetName = str
pd_LazyDataFrame = Callable[[], pd.DataFrame]

# _caches = {"simple": Cache(config={"CACHE_TYPE": "SimpleCache"}), "null": Cache(config={"CACHE_TYPE": "NullCache"})}
# don't want this for now but might have in future.
# how to turn cache off? For now just specify nullcache. Maybe in future have _dataset._cache = False as shortcut for
# this. Implementation could be using unless or nullcache or if conditional.


class _Dataset:
    def __init__(self, load_data: pd_LazyDataFrame, /):
        self.__load_data: pd_LazyDataFrame = load_data
        # timeout and cache will probably become public in future.
        self._timeout: Optional[int] = None
        self._cache: Optional[Cache] = None
        # name should never become public since it's taken from the key in data_manager.
        self._name: str = ""

        # We might also want a _cache_arguments dictionary in future that allows user to customise more than just
        # timeout, but no rush to do this.

    def __call__(self) -> pd.DataFrame:
        # In future this will probably take arguments that are passed through to _load_data in order to re-run the
        # loading function with different arguments. We might want to use CapturedCallable for self.__load_data then.
        logger.debug("Calling dataset %s", self._name)

        # memoize is designed to apply the same timeout setting to every call of the function, but we want to
        # have a dataset-dependent timeout in the same cache. The only way to do this is to alter the function qualname
        # used in flask_caching.utils.function_namespace so that each _Dataset instance has a different cache for
        # load_data.
        # The following things *do not* work to achieve the same thing - there will still be interference between
        # different load_data caches:
        # * altering load_data.cache_timeout
        # * using make_name argument (since this is only applied after function_namespace is called)
        # * including self or self._name in the load_data arguments
        # Since the function is labelled by the unique self._name, there's no need to include self in the arguments.
        # Doing so would be ok but means also defining a __caching_id__ = self._name property for _Dataset so that
        # Flask Caching does not fall back on __repr__ to identify the _Dataset instance, which is risky.
        @self._cache.memoize(timeout=self._timeout)
        def _load_data():
            logger.debug("Cache for dataset %s not found; reloading data", self._name)
            return self.__load_data()

        _load_data.uncached.__qualname__ += f"__{self._name}"
        return _load_data()

    def _init_cache(self, app: flask.Flask):
        # Initialising the same cache repeatedly doesn't cause any harm but is not necessary. Once initialised,
        # flask caching puts the cache in the flask.extensions["cache"] dictionary.
        if self._cache not in flask.extensions.get("cache", {}):
            self._cache.init_app(app)


#
# class _Dataset:
#     """A dataset with flask-caching config attached.
#
#     Examples:
#         >>> import plotly.express as px
#         >>> data_manager["iris"] = pd.DataFrame()
#         >>> data_manager["iris"]._cache_arguments = {"timeout": 600}
#     """


class DataManager:
    """Object to handle all data for the `vizro` application.

    Examples:
        >>> import plotly.express as px
        >>> data_manager["iris"] = px.data.iris()

    """

    def __init__(self):
        """Initializes the `DataManager` object."""
        self.__lazy_data: Dict[DatasetName, _Dataset] = {}
        self.__original_data: Dict[DatasetName, pd.DataFrame] = {}
        self.__component_to_original: Dict[ComponentID, DatasetName] = {}
        self._frozen_state = False
        self._cache = Cache(config={"CACHE_TYPE": "SimpleCache"})

    # AM: consider if this should also call the lazy data to populate the cache? Probably doesn't matter.
    @_state_modifier
    def __setitem__(self, dataset_name: DatasetName, data: Union[pd.DataFrame, pd_LazyDataFrame]):
        """Adds `data` to the `DataManager` with key `dataset_name`.

        This is the only user-facing function when configuring a simple dashboard. Others are only used internally
        in Vizro or advanced users who write their own actions.
        """
        if dataset_name in self.__original_data or dataset_name in self.__lazy_data:
            raise ValueError(f"Dataset {dataset_name} already exists.")

        if callable(data):
            self.__lazy_data[dataset_name] = _Dataset(data)
            self.__lazy_data[dataset_name]._name = dataset_name
        elif isinstance(data, pd.DataFrame):
            self.__original_data[dataset_name] = data  # AM: should also put into Dataset?
        else:
            raise TypeError(
                f"Dataset {dataset_name} must be a pandas DataFrame or callable that returns pandas DataFrame."
            )

    def __getitem__(self, dataset_name: DatasetName) -> _Dataset:
        """Returns the `_Dataset` object associated with `dataset_name`."""
        if dataset_name not in self.__original_data and dataset_name not in self.__lazy_data:
            raise KeyError(f"Dataset {dataset_name} does not exist.")
        if dataset_name in self.__original_data:
            # no cache available
            # AM: should always wrap into Dataset to make this consistent?
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

    def _get_component_data(self, component_id: ComponentID) -> pd.DataFrame:
        """Returns the original data for `component_id`."""
        if component_id not in self.__component_to_original:
            raise KeyError(f"Component {component_id} does not exist. You need to call add_component first.")
        dataset_name = self.__component_to_original[component_id]

        if dataset_name in self.__lazy_data:
            return self[dataset_name]()

        else:  # dataset_name is in self.__original_data
            # Return a copy so that the original data cannot be modified. This is not necessary if we are careful
            # to not do any inplace=True operations, but probably safest to leave it here.
            return self.__original_data[dataset_name].copy()

    def _init_cache(self, app: flask.Flask):
        """Sets the default cache for all datasets to be the same as the data_manager cache and initializes cache."""
        for dataset in self.__lazy_data.values():
            dataset._cache = dataset._cache or self._cache
            dataset._init_cache(app)

    # TODO: consider implementing __iter__ to make looping through datasets easier. Might not be worth doing though.

    # TODO: we should be able to remove this soon. Try to avoid using it.
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
