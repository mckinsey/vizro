"""The data manager handles access to all DataFrames used in a Vizro app."""

from __future__ import annotations

import warnings

from contextlib import suppress

import logging
import os
from typing import Callable, Dict, Optional, Union

import pandas as pd
import wrapt
from flask_caching import Cache

from vizro.managers._managers_utils import _state_modifier

# TODO: test manually and write tests:
# * new error messages that are raised
# Only need to test str/non-str static dataframe argument throughout unit tests in general.
# And test dynamic datasets by themselves


#####################
# Just for the purposes of easily seeing the right debug messages. Remove before merging to main and revert to this:
# logger = logging.getLogger(__name__)
class PrefixAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return f"[DATA MANAGER] {msg}", kwargs


logger = PrefixAdapter(logging.getLogger(__name__), {})
logger.setLevel(logging.DEBUG)
#####################

# Really ComponentID and DataSourceName should be NewType and not just aliases but then for a user's code to type check
# correctly they would need to cast all strings to these types.
# TODO: remove these type aliases once have moved component to data mapping to models
ComponentID = str
DataSourceName = str
pd_DataFrameCallable = Callable[[], pd.DataFrame]


# wrapt.decorator is the cleanest way to decorate a bound method when instance properties (here instance.timeout)
# are required as arguments. The enabled argument bypasses the entire decorator when data_manager._cache_has_app
# is False. This prevents Flask-Caching from trying to access a Flask app when one doesn't yet exist.
@wrapt.decorator(enabled=lambda: data_manager._cache_has_app)
def memoize(wrapped: Callable, instance: _DynamicData, args, kwargs):
    """Caches the result of wrapped function, taking its arguments into account in the cache key.

    This delegates to flask_caching.memoize functionality, but with an important modification. flask_caching.memoize
    is designed to apply the same timeout to every call of the function or bound method, but we want to have a
    data source-dependent timeout. This means rewriting the wrapped function's __qualname__ so that different instances
    of _DynamicData have completely independent caches. Without this, flask_caching.utils.function_namespace gives the
    same namespace for each, which means that the timeouts cannot be set independently.

    The following things *do not* work to achieve the same thing - there will still be interference between
    different caches:
    * altering wrapped.cache_timeout
    * using make_name argument (since this is only applied after function_namespace is called)
    * including self or self._name in the load_data arguments
    * whenever function_namespace recognises the memoized function as a bound method (even when __caching_id__ is
    defined so that Flask Caching does not fall back on __repr__)

    Another option would be to use flask_caching.cached rather than memoize, but that makes it harder to include
    arguments in the cache key and only works inside a Flask request context.

    Args:
        wrapped: function that will be memoized.
        instance: _DynamicData object to which wrapped is bound.
        args: positional arguments supplied to wrapped, taken into account for generating cache key.
        kwargs: keyword arguments supplied to wrapped, taken into account for generating cache key.

    Returns:
        Memoized call.

    """
    # Before altering, wrapped.__func__.__qualname__ is "_DynamicData.__call__"
    # After altering, it becomes _DynamicData.__call__._DynamicData("name", function_name)
    # Note this doesn't work by using += since the qualname will just be appended to fresh every time the function is
    wrapped.__func__.__qualname__ = ".".join([instance.__class__.__name__, wrapped.__func__.__name__, repr(instance)])
    return data_manager.cache.memoize(timeout=instance.timeout)(wrapped)(*args, **kwargs)


class _DynamicData:
    """Wrapper for a pd_DataFrameCallable, i.e. a function that produces a pandas DataFrame. Crucially this means
    that the data can be refreshed during runtime, since the loading function can be re-run.

    This is currently private since it's not expected that a user would instantiate it directly. Instead, you would use
    through the data_manager interface as follows:
        >>> def dynamic_data():
        >>>     return pd.read_csv("dynamic_data.csv")
        >>> data_manager["dynamic_data"] = dynamic_data
        >>> data_manager["dynamic_data"].timeout = 5  # if you want to change the cache timeout to 5 seconds

    Possibly in future, this will become a public class so you could directly do:
        >>> data_manager["dynamic_data"] = DynamicData(dynamic_data, timeout=5)
    But we'd need to make sure that name is not an argument in __init__ then.

    At this point we might like to disable the behaviour so that data_manager setitem and getitem handle the same
    object rather than doing an implicit conversion to _DynamicData.
    """

    def __init__(self, name: str, load_data: pd_DataFrameCallable):
        self.__load_data: pd_DataFrameCallable = load_data
        # name is needed for the cache key and should not be modified by users.
        self._name = name
        self.timeout: Optional[int] = None
        # We might also want a self.cache_arguments dictionary in future that allows user to customise more than just
        # timeout, but no rush to do this since other arguments are unlikely to be useful.

    @memoize
    def load(self) -> pd.DataFrame:
        """Loads data.

        In future this will probably take arguments that are passed through to __load_data in order to re-run the
        loading function with different arguments. We might want to use CapturedCallable for self.__load_data then.
        """
        # Note you get the same "cache missed" message if NullCache is running or if data_manager._cache_has_app is
        # False.
        logger.debug("Cache miss; reloading data")
        return self.__load_data()

    def __repr__(self):
        """Flask-caching uses repr to form the cache key, so this is very important to set correctly.

        In particular, it must depend on something that uniquely labels the data source and is the same across all
        workers: self._name. Using id(self), as in Python's default repr, only works in the case that gunicorn is
        running with --preload: without preloading, the id of the same data source in different processes will be
        different so the cache will not match up.

        flask_caching make it possible to set a __cached_id__ attribute to handle this so that repr can be set
        independently of cache key, but this doesn't seem to be well documented or work well, so it's better to rely
        on __repr__.
        """
        # Note that using repr(self.__load_data) is not good since it depends on the id of self.__load_data and so
        # would not be consistent across processes.
        # lambda function has __qualname__. partial does not unless explicitly assigned a name but will not work with
        # flask-caching anyway since flask_caching.utils.function_namespace would not be able to find a name for it.
        return f"{self.__class__.__name__}({self._name!r}, {self.__load_data.__qualname__})"


class _StaticData:
    """Wrapper for a pd.DataFrame. This data cannot be updated during runtime.

    This is currently private since it's not expected that a user would instantiate it directly. Instead, you would use
    through the data_manager interface as follows:
         >>> data_manager["static_data"] = pd.read_csv("static_data.csv")

    This class does not have much functionality but exists for a couple of reasons:
        1. to align interface with _DynamicData by providing a load method so that fetching data from data_manager can
        transparently handle loading both _StaticData and _DynamicData without needing switching logic
        2. to raise a clear error message if a user tries to set a timeout on the data source
    """

    def __init__(self, data: pd.DataFrame):
        # No need for _name here because static data doesn't need a cache key.
        self.__data = data

    def load(self) -> pd.DataFrame:
        """Loads data.

        Returns a copy of the data. This  is not necessary if we are careful to not do any inplace=True operations,
        but probably safest to leave it here.
        """
        return self.__data.copy()

    def __setattr__(self, name, value):
        # Any attributes that are only relevant for _DynamicData should go here to raise a clear error message.
        if name in ["timeout"]:
            raise AttributeError(
                f"Static data that is a pandas.DataFrame itself does not support {name}; you should instead use a "
                "dynamic data source that is a function that returns a pandas.DataFrame."
            )
        super().__setattr__(name, value)


class DataManager:
    """Object to handle all data for the `vizro` application.

    Examples
        >>> # Static data that cannot be refreshed during runtime
        >>> data_manager["data"] = pd.read_csv("data.csv")
        >>> # Data that can be refreshed during runtime
        >>> def dynamic_data():
        >>>     return pd.read_csv("dynamic_data.csv")
        >>> data_manager["dynamic_data"] = dynamic_data
        >>> data_manager["dynamic_data"].timeout = 5  # if you want to change the cache timeout to 5 seconds

    """

    def __init__(self):
        self.__data: Dict[DataSourceName, Union[_DynamicData, _StaticData]] = {}
        self.__component_to_data: Dict[ComponentID, DataSourceName] = {}
        self._frozen_state = False
        self.cache = Cache(config={"CACHE_TYPE": "NullCache"})
        # In future, possibly we will accept just a config dict. Would need to work out whether to handle merging with
        # default values though. We would do this with something like this:
        # def __set_cache(self, cache_config):
        #     if not isinstance(cache, Cache):
        #         self._cache = Cache(**cache)
        #     self._cache = value
        # _cache = property(fset=__set_cache)

    @_state_modifier
    def __setitem__(self, name: DataSourceName, data: Union[pd.DataFrame, pd_DataFrameCallable]):
        """Adds `data` to the `DataManager` with key `name`."""
        if callable(data):
            self.__data[name] = _DynamicData(name, data)
        elif isinstance(data, pd.DataFrame):
            self.__data[name] = _StaticData(data)
        else:
            raise TypeError(
                f"Data source {name} must be a pandas DataFrame or function that returns a pandas DataFrame."
            )

    def __getitem__(self, name: DataSourceName) -> Union[_DynamicData, _StaticData]:
        """Returns the `_DynamicData` or `_StaticData` object associated with `name`."""
        try:
            return self.__data[name]
        except KeyError as exc:
            raise KeyError(f"Data source {name} does not exist.") from exc

    @_state_modifier
    def _add_component(self, component_id: ComponentID, name: DataSourceName):
        """Adds a mapping from `component_id` to `name`."""
        # TODO: once have removed self.__component_to_data, we shouldn't need this function any more.
        #  Maybe always updated capturedcallable data_frame to  data source name string then.
        if name not in self.__data:
            raise KeyError(f"Data source {name} does not exist.")
        if component_id in self.__component_to_data:
            raise ValueError(
                f"Component with id={component_id} already exists and is mapped to data "
                f"{self.__component_to_data[component_id]}. Components must uniquely map to a data source across the "
                f"whole dashboard. If you are working from a Jupyter Notebook, please either restart the kernel, or "
                f"use 'from vizro import Vizro; Vizro._reset()`."
            )
        self.__component_to_data[component_id] = name

    def _get_component_data(self, component_id: ComponentID) -> pd.DataFrame:
        # TODO: once have removed self.__component_to_data, we shouldn't need this function any more. Calling
        #  functions would just do data_manager[name].load().
        """Returns the original data for `component_id`."""
        if component_id not in self.__component_to_data:
            raise KeyError(f"Component {component_id} does not exist. You need to call add_component first.")
        name = self.__component_to_data[component_id]

        logger.debug("Loading data %s on process %s", name, os.getpid())
        return self[name].load()

    def _clear(self):
        # We do not actually call self.cache.clear() because (a) it would only work when self._cache_has_app is True,
        # which is not the case when e.g. Vizro._reset is called, and (b) because we do not want to accidentally
        # clear the cache if we eventually put a call to Vizro._reset inside Vizro(), since cache should be persisted
        # across server restarts.
        self.__init__()  # type: ignore[misc]

    @property
    def _cache_has_app(self) -> bool:
        """Detects whether self.cache.init_app has been called (as it is in Vizro) to attach a Flask app to the cache.

        Note that even NullCache needs to have an app attached before it can be "used". The only time the cache would
        not have an app attached is if the user tries to interact with the cache before Vizro() has been called.
        """
        cache_has_app = hasattr(self.cache, "app")
        if not cache_has_app and self.cache.config["CACHE_TYPE"] != "NullCache":
            # Try to prevent anyone from setting data_manager.cache after they've instantiated Vizro().
            # No need to emit a warning if the cache is left as NullCache; we only care about this if someone has
            # explicitly set a cache.
            # Eventually Vizro should probably have init_app method explicitly to clear this up so the order of
            # operations is more reliable. Alternatively we could just initialize cache at run time rather than build
            # time, which is what Flask-Caching is really designed for. This would require an extra step for users
            # though, since it could not go in Vizro.run() since that is not used in the case of gunicorn.
            warnings.warn(
                "Cache does not have Vizro app attached and so is not operational. Make sure you call "
                "Vizro() after you set data_manager.cache."
            )
        return cache_has_app


data_manager = DataManager()
