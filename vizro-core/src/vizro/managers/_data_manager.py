"""The data manager handles access to all DataFrames used in a Vizro app."""

from __future__ import annotations

import logging
import warnings
from typing import Callable, Dict, Optional, Union

import pandas as pd
import wrapt
from flask_caching import Cache

from vizro.managers._managers_utils import _state_modifier

logger = logging.getLogger(__name__)

# Really DataSourceName should be NewType and not just aliases but then for a user's code to type check
# correctly they would need to cast all strings to these types.
DataSourceName = str
pd_DataFrameCallable = Callable[..., pd.DataFrame]


def memoize(*, timeout: Optional[int], make_name: Optional[Callable]) -> Callable:
    """Creates memoize decorator for use with data_manager.cache.

    Follows the pattern recommended in https://wrapt.readthedocs.io/en/latest/decorators.html#decorators-with-arguments
    or making a wrapt.decorator with arguments. This is just a wrapper for flask_caching.Cache.memoize with the timeout
    and make_name arguments exposed as keyword-only arguments.

    Args:
       timeout: passed through to flask_caching.Cache.memoize. If set to None, will just use
        the CACHE_DEFAULT_TIMEOUT; if set to an integer, will cache for that number of seconds.
       make_name: passed through to flask_caching.Cache.memoize. If set, this is a function that accepts
        a single argument, the function name, and returns a new string to be used as the function name. This can be
        used to set the cache key as we please.

    Returns:
         memoize decorator.

    """

    @wrapt.decorator(enabled=lambda: data_manager._cache_has_app)
    def wrapper(wrapped, instance, args, kwargs):
        return data_manager.cache.memoize(timeout=timeout, make_name=make_name)(wrapped)(*args, **kwargs)

    return wrapper


class _DynamicData:
    """Wrapper for a pd_DataFrameCallable, i.e. a function that produces a pandas DataFrame.

    Crucially this means that the data can be refreshed during runtime, since the loading function can be re-run.

    This is currently private since it's not expected that a user would instantiate it directly. Instead, you would use
    through the data_manager interface as follows:
        >>> def dynamic_data():
        >>>     return pd.read_csv("dynamic_data.csv")
        >>> data_manager["dynamic_data"] = dynamic_data
        >>> data_manager["dynamic_data"].timeout = 5  # if you want to change the cache timeout to 5 seconds

    Possibly in future, this will become a public class so you could directly do:
        >>> data_manager["dynamic_data"] = DynamicData(dynamic_data, timeout=5)
    But we'd need to make sure that name is not an argument in __init__ then.

    At this point we might like to disable the behavior so that data_manager setitem and getitem handle the same
    object rather than doing an implicit conversion to _DynamicData.
    """

    def __init__(self, name: str, load_data: pd_DataFrameCallable):
        # When load_data is a bound method (e.g. as it will be for a kedro dataset),
        # flask_caching.utils.function_namespace generates a cache key based on __caching_id__ (if defined) or  __repr__
        # of the instance to which it's bound. We need this to be something that uniquely labels the data source and
        # is the same across all workers so use the data source name. Most repr methods include the id of the
        # instance so would only work in the case that gunicorn is running with --preload: without preloading, the id
        # of the same (e.g. kedro dataset) instance is not the same across different processes so the cache will not
        # match up.
        if hasattr(load_data, "__self__"):
            load_data.__self__.__caching_id__ = lambda _: name

        self.__load_data: pd_DataFrameCallable = load_data
        # name is needed for the cache key and should not be modified by users.
        self._name = name
        self.timeout: Optional[int] = None
        # We might also want a self.cache_arguments dictionary in future that allows user to customize more than just
        # timeout, but no rush to do this since other arguments are unlikely to be useful.

    def load(self, *args, **kwargs) -> pd.DataFrame:
        """Loads data."""
        # Note you get the same "cache missed" message if NullCache is running or if data_manager._cache_has_app is
        # False.

        #  TODO: Think about whether to use wrapt at all (probably yes) and how to handle enabled=False.
        # TODO: logger.debug("Cache miss; reloading data"). Could inject this with a decorator into load_data if wanted
        # to.
        # Including make_name here ensures that the cache key for two data sources with the same underlying function
        # are different - see test_shared_dynamic_data_function and test_timeouts_do_not_interfere. This
        # functionality is not particularly important to enable, but including make_name feels like a robust thing to
        # do anyway: it's not  strictly needed to make work the case that load_data is a bound method but
        # probably good to keep for that in case the way that flask-caching handles bound methods changes.
        # We don't memoize the load method itself since this is tricky to get working fully when load is called with
        # arguments, since we need the signature of the memoized function to match that of load_data. See
        # https://github.com/GrahamDumpleton/wrapt/issues/263.
        return memoize(timeout=self.timeout, make_name=lambda _: self._name)(self.__load_data)(*args, **kwargs)


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

        Returns a copy of the data. This is not necessary if we are careful to not do any inplace=True operations,
        but safest to leave it here, e.g. in case a user-defined action mutates the data. To be even safer we could
        additionally (but not instead) copy data when setting it in __init__ but this consumes more memory and is not
        necessary so long as data is only ever accessed through the intended API of data_manager["static_data"].load().
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
            if not hasattr(data, "__qualname__"):
                # __qualname__ is required by flask-caching (even though we specify our own make_name) but
                # not defined for partial functions and  just '<lambda>' for lambda functions. Defining __qualname__
                # means it's possible to have non-interfering caches for partial and lambda functions (similarly if we
                # end up using CapturedCallable, or that could instead set its own __qualname__).
                data.__qualname__ = name
                # TODO: write test for both partial and lambda

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


data_manager: DataManager = DataManager()
