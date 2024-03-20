"""The data manager handles access to all DataFrames used in a Vizro app."""
import logging
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
# If want to turn cache off for one dataset, basically just set low timeout for now?
# timeout=0 means it never expires. 0 means cache forever and never refresh -> never re-run function.
# Ones set with timeout=0 can still be manually refreshed with forced_update.

# TODO: test, idea 2 (see shelf)
#  whether we still need  components to dataset mapping - we don't but save this for future PR. Put mapping to
#  dataset in callable model itself. So it's still one DS to many components but no need to store mapping here.
#  Call it _cache_timeout? Only if might have cache_update etc. in future. Think about refresh_cache function

# Try out callable with parametrised args

# How to actually update/invalidate/reset cache on demand? rather than just waiting for timeout.
# Use forced_update as in shelf "This is how to refresh cache for one dataset"

# Note limitation than you need to set preload

# Remove _name - just there for debugging purposes


class _Dataset:
    def __init__(self, load_data: pd_LazyDataFrame, /):
        self.__load_data: pd_LazyDataFrame = load_data
        # timeout will probably become public in future.
        self._timeout: Optional[int] = None
        # self._cache is the same for all datasets and is just the data_manager._cache. Only one global cache for now.
        # TODO: just call data_manager._cache directly?
        self._cache: Optional[Cache] = None
        # name should never become public since it's taken from the key in data_manager.
        # This scheme seems ugly - is there a better way? Yes - just use id(self). self._name is only here for
        # debugging.
        self._name: str = ""
        # We might also want a _cache_arguments dictionary in future that allows user to customise more than just
        # timeout, but no rush to do this.

    def __call__(self) -> pd.DataFrame:
        # In future this will probably take arguments that are passed through to _load_data in order to re-run the
        # loading function with different arguments. We might want to use CapturedCallable for self.__load_data then.
        logger.debug("** Calling dataset %s", self._name)

        # memoize is designed to apply the same timeout setting to every call of the function, but we want to
        # have a dataset-dependent timeout in the same cache. The only way to do this is to write a closure and alter
        # the function qualname used in flask_caching.utils.function_namespace so that each _Dataset instance has a
        # different cache for load_data.
        # The following things *do not* work to achieve the same thing - there will still be interference between
        # different load_data caches:
        # * altering load_data.cache_timeout
        # * using make_name argument (since this is only applied after function_namespace is called)
        # * including self or self._name in the load_data arguments
        # * whenever function_namespace recognise the memoized function as a bound method (even when __caching_id__ is
        # defined so that Flask Caching does not fall back on __repr__ which is risky)
        # Another option would be to use cached rather than memoize, but that is generally intended only for use
        # during a request, and we want to call _load_data during the build stage, not just at run time.

        # HERE: maybe doing as bound method and/or using data_manager._cache rather than self._cache was actually ok and
        # it just didn't work properly because had multiple processes with SimpleCache?
        #
        # With flask.run and multiple processes:
        #  - FileSystemCache: Get lots of different processes but works ok
        #  - SimpleCache: Get lots of different processes and doesn't work ok - get interference. Put warning in
        #  place to prevent this.
        # When use gunicorn with two processes:
        #   - FileSystemCache: get initial process for loading data and then boots two processes and just uses those from then on.
        #   Cache works correctly.
        #  - SimpleCache: same number of processes. Cache works sort of correctly - don't have interference,
        #    but cache not being shared between processes, as expected.

        # SimpleCache: Simple memory cache for single process environments. This class exists mainly for the
        # development server and is not 100% thread safe.
        # As soon as move to gunicorn, need to setup proper cache -> yes. SimpleCache still works ok but not memory
        # efficient.
        # Note threaded=True by default with run and probably shouldn't change that (?). And SimpleCache not 100%
        # thread-safe.
        # Problem with cache not shard between workers while running is not just inefficiency but that invalidating
        # cache will not work properly.
        # But NullCache would probably be too slow as default.
        # Use SimpleCache with no timeout as default?

        # What should default cache be?
        # Check preload and non-preload behaviour
        # Clear up debugging messaging and go through above again.
        import os

        logger.debug(f"{self._name=}\t{id(self)}\t{os.getpid()=}")

        @self._cache.memoize(timeout=self._timeout)
        def _load_data():
            logger.debug("** Cache for dataset %s not found; reloading data", self._name)
            return self.__load_data()

        _load_data.uncached.__qualname__ += f"__{id(self)}"
        return _load_data()


#
# class _Dataset:
#     """A dataset with flask-caching config attached.
#
#     Examples:
#         >>> import plotly.express as px
#         >>> data_manager["iris"] = pd.DataFrame()
#         >>> data_manager["iris"]._cache_arguments = {"timeout": 600}
#     """
# Old notes:
# # Options for configuring per-dataset arguments:
# # 1.
# data_manager["iris"] = lambda: pd.DataFrame()
# data_manager["iris"].set_cache(timeout=50)
#
#
# # 2.
# class VizroDataSet:
#     pass
#
#
# data_manager["iris"] = VizroDataSet(lambda: pd.DataFrame(), timeout=50)


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
        # Note possibility of accepting just config dict in future

    # AM: consider if this should also call the lazy data to populate the cache? Probably doesn't matter.
    # Probably not because then it would load up all data even in not used.
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
        # Need to inject it here rather than in setitem so that you can set cache *after* adding things to DM
        for dataset in self.__lazy_data.values():
            dataset._cache = self._cache
        self._cache.init_app(app)

    # TODO: consider implementing __iter__ to make looping through datasets easier. Might not be worth doing though.

    # TODO: we should be able to remove this soon. Try to avoid using it.
    def _has_registered_data(self, component_id: ComponentID) -> bool:
        try:
            self._get_component_data(component_id)
            return True
        except KeyError:
            return False

    def _clear(self):
        # CLEAR CACHE?
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
