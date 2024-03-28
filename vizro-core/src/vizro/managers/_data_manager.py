"""The data manager handles access to all DataFrames used in a Vizro app."""
from __future__ import annotations

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
# how to turn memoize off? For now just specify nullcache. Maybe in future have _dataset._cache = False as shortcut for
# this. Implementation could be using unless or nullcache or if conditional.
# If want to turn memoize off for one dataset, basically just set low timeout for now?
# timeout=0 means it never expires. 0 means memoize forever and never refresh -> never re-run function.
# Ones set with timeout=0 can still be manually refreshed with forced_update.

# TODO: test, idea 2 (see shelf)
#  whether we still need  components to dataset mapping - we don't but save this for future PR. Put mapping to
#  dataset in callable model itself. So it's still one DS to many components but no need to store mapping here.
#  Call it _cache_timeout? Only if might have cache_update etc. in future. Think about refresh_cache function - see
#  shelf

# Try out callable with parametrised args like Max example

# How to actually update/invalidate/reset memoize on demand? rather than just waiting for timeout.
# Use forced_update as in shelf "This is how to refresh memoize for one dataset"


"""
# Note limitation than you need to set preload

With flask.run and multiple processes:
- FileSystemCache: Get lots of different processes but works ok
- SimpleCache: Get lots of different processes and doesn't work ok - get interference. Put warning in
place to prevent this.

SimpleCache: Simple memory memoize for single process environments. This class exists mainly for the
development server and is not 100% thread safe.
CONCLUSION: SimpleCache only good for single process with gunicorn or flask.
As soon as move to multiple workers, need proper cache -> yes.
Note threaded=True by default with run and probably shouldn't change that (?). And SimpleCache not 100%
thread-safe.
Problem with cache not shared between workers while running is not just inefficiency but that invalidating
cache will not work properly.
But NullCache would probably be too slow as default.
Use SimpleCache by default. Set no timeout or default 5 mins?"""

import wrapt


# wrapt.decorator is the cleanest way to decorate a bound method when instance properties (here instance._timeout)
# are required as arguments.
@wrapt.decorator
def memoize(wrapped: Callable, instance: _Dataset, args, kwargs):
    """Caches the result of wrapped function, taking its arguments into account in the cache key.

    This delegates to flask_caching.memoize functionality, but with an important modification. flask_caching.memoize
    is designed to apply the same timeout to every call of the function or bound method, but we want to have a
    dataset-dependent timeout. This means rewriting the wrapped function's __qualname__ so that different instances
    of _Dataset have completely independent caches. Without this, flask_caching.utils.function_namespace gives the
    same namespace for each, which means that the timeouts cannot be set independently.

    The following things *do not* work to achieve the same thing - there will still be interference between
    different caches:
    * altering wrapped.cache_timeout
    * using make_name argument (since this is only applied after function_namespace is called)
    * including self or self._name in the load_data arguments
    * whenever function_namespace recognise the memoized function as a bound method (even when __caching_id__ is
    defined so that Flask Caching does not fall back on __repr__ which is risky)

    Another option would be to use flask_caching.cached rather than memoize, but that is generally intended only
    for use during a request, and we want to memoize during the build stage, not just at run time.

    Args:
        wrapped: function that will be memoized.
        instance: _Dataset object to which wrapped is bound.
        args: positional arguments supplied to wrapped, taken into account for generating cache key.
        kwargs: keyword arguments supplied to wrapped, taken into account for generating cache key.

    Returns:
        Memoized call.
    """
    # Before altering, wrapped.__func__.__qualname__ is "_Dataset.__call__"
    # After altering, it becomes _Dataset.__call__.<vizro.managers._data_manager._Dataset object at 0x11d5fc2d0>
    # where the repr(instance) depends on id(instance).
    # Note this doesn't work by using += since the qualname will just be appended to fresh every time the function is
    # called so will be different every time and not ever hit the cache.
    wrapped.__func__.__qualname__ = ".".join([instance.__class__.__name__, wrapped.__func__.__name__, repr(instance)])
    return data_manager._cache.memoize(timeout=instance._timeout)(wrapped)(*args, **kwargs)


class _Dataset:
    def __init__(self, load_data: pd_LazyDataFrame, /):
        self.__load_data: pd_LazyDataFrame = load_data
        # timeout will probably become public in future.
        self._timeout: Optional[int] = None
        # We might also want a _cache_arguments dictionary in future that allows user to customise more than just
        # timeout, but no rush to do this.

    @memoize
    def __call__(self) -> pd.DataFrame:
        """Loads data.

        In future this will probably take arguments that are passed through to __load_data in order to re-run the
        loading function with different arguments. We might want to use CapturedCallable for self.__load_data then.
        """
        logger.debug("Cache miss; reloading data")
        return self.__load_data()

    def __repr__(self):
        """This is just the default repr so behaviour would be the same if we removed the function definition.

        The reason for defining this is to have somewhere to put the following warning: caching currently relies on
        this returning a string that depends on id(self). This is relied on by flask_caching.utils.function_namespace
        and our own memoize decorator. If this method were changed to no longer include some representation of id(self)
        then cache keys would be mixed up.

        flask_caching make it possible to set a __cached_id__ attribute to handle this so that repr can be set
        independently of cache key, but this doesn't seem to be well documented or work well, so it's better to rely
        on __repr__.

        In future we might like to change the cache so that it works on dataset name rather than the place in memory.
        This would necessitate a new _Dataset._name attribute. This would get us closer to getting gunicorn to work
        without relying on --preload, although it would not get all the way there:
            * model_manager would need to fix a random seed or alternative solution (just like Dash does for its
            component ids)
            * not clear how to handle the case of unnamed datasets, where the name is currently generated
            automatically by the id, since without --preload this would give mismatched names. If use a random number with
            fixed seed for this then lose advantage of multiple plots that use the same dataset having just one
            underlying dataframe in memory.
            * would need to make it possible to disable cache at build time so that data would be loaded once at build
            time and then again once at runtime, which is generally not what we want
        """
        return super().__repr__()


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
            logger.debug(f"Calling dataset %s with id %s", dataset_name, id(self[dataset_name]))
            return self[dataset_name]()
        else:  # dataset_name is in self.__original_data
            # Return a copy so that the original data cannot be modified. This is not necessary if we are careful
            # to not do any inplace=True operations, but probably safest to leave it here.
            return self.__original_data[dataset_name].copy()

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
