"""The data manager handles access to all DataFrames used in a Vizro app."""

from __future__ import annotations

import functools
import json
import logging
import os
import warnings
from functools import partial
from typing import Any, Callable, Optional, Union

import pandas as pd
import wrapt
from flask_caching import Cache

from vizro.managers._managers_utils import _state_modifier

logger = logging.getLogger(__name__)


# Really DataSourceName should be NewType and not just aliases but then for a user's code to type check
# correctly they would need to cast all strings to these types.
DataSourceName = str
pd_DataFrameCallable = Callable[..., pd.DataFrame]


# TODO: consider merging with model_utils _log_call. Using wrapt.decorator is probably better than functools here.
#  Might need messages that run before/after the wrapped function call.
# Follows the pattern recommended in https://wrapt.readthedocs.io/en/latest/decorators.html#decorators-with-arguments
# for making a wrapt.decorator with arguments.
def _log_call(message: str):
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        logger.debug(message)
        # Might be useful if merged with model_utils _log_call:
        # logging.debug(message.format(wrapped=wrapped, instance=instance, args=args, kwargs=kwargs))
        return wrapped(*args, **kwargs)

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

    At this point we might like to disable the behavior so that data_manager setitem and getitem handle the same
    object rather than doing an implicit conversion to _DynamicData.
    """

    def __init__(self, load_data: pd_DataFrameCallable):
        self.__load_data: pd_DataFrameCallable = load_data
        self.timeout: Optional[int] = None
        # We might also want a self.cache_arguments dictionary in future that allows user to customize more than just
        # timeout, but no rush to do this since other arguments are unlikely to be useful.

    def load(self, *args, **kwargs) -> pd.DataFrame:
        """Loads data."""
        # Data source name can be extracted from the function's name since it was added there in DataManager.__setitem__
        logger.debug(
            "Looking in cache for data source %s on process %s",
            self.__load_data.__name__.rpartition(".")[-1],
            os.getpid(),
        )
        # We don't memoize the load method itself as this is tricky to get working fully when load is called with
        # arguments, since we need the signature of the memoized function to match that of load_data. See
        # https://github.com/GrahamDumpleton/wrapt/issues/263.
        # It's also difficult to get memoize working correctly with bound methods anyway - see comment in
        # DataManager.__setitem__. It's much easier to ensure that self.__load_data is always just a function.
        if data_manager._cache_has_app:
            # This includes the case of NullCache.
            load_data = _log_call("Cache miss; reloading data")(self.__load_data)
            load_data = data_manager.cache.memoize(timeout=self.timeout)(load_data)
        else:
            logger.debug("Cache not active; reloading data")
            load_data = self.__load_data
        return load_data(*args, **kwargs)


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

    Examples:
        >>> # Static data that cannot be refreshed during runtime
        >>> data_manager["data"] = pd.read_csv("data.csv")
        >>> # Data that can be refreshed during runtime
        >>> def dynamic_data():
        >>>     return pd.read_csv("dynamic_data.csv")
        >>> data_manager["dynamic_data"] = dynamic_data
        >>> data_manager["dynamic_data"].timeout = 5  # if you want to change the cache timeout to 5 seconds

    """

    def __init__(self):
        self.__data: dict[DataSourceName, Union[_DynamicData, _StaticData]] = {}
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
            # __qualname__ is required by flask-caching (even if we specify our own make_name) but
            # not defined for partial functions and just '<lambda>' for lambda functions. Defining __qualname__
            # means it's possible to have non-interfering caches for lambda functions (similarly if we
            # end up using CapturedCallable, or that could instead set its own __qualname__).
            # We handle __name__ the same way even though it's not currently essential to functioning of flask-caching
            # in case they change the underlying implementation to use it.
            # We use partial to effectively make an independent copy of the underlying data function. This means that
            # it's possible to set __qualname__ independently for each data source. This is not essential for
            # functions other than lambda, but it is essential for bound methods, as flask-caching cannot easily
            # independently timeout different instances with different bound methods but the same underlying function
            # data.__func__. If we don't do this then the bound method case needs some uglier hacking to make work
            # correctly - see https://github.com/mckinsey/vizro/blob/abb7eebb230ba7e6cfdf6150dc56b211a78b1cd5/
            # vizro-core/src/vizro/managers/_data_manager.py.
            # Once partial has been used, all dynamic data sources are on equal footing since they're all treated as
            # functions rather than bound methods, e.g. by flask_caching.utils.function_namespace. This makes it much
            # simpler to use flask-caching reliably.
            # Note that for kedro>=0.19.9 we use lambda: catalog.load(dataset_name) rather than dataset.load so the
            # bound method case no longer arises when using kedro integration.
            # It's important the __qualname__ is the same across all workers, so use the data source name rather than
            # e.g. the repr method that includes the id of the instance so would only work in the case that gunicorn is
            # running with --preload.
            # __module__ is also required in flask_caching.utils.function_namespace and not defined for partial
            # functions in some versions of Python.
            # update_wrapper ensures that __module__, __name__, __qualname__, __annotations__ and __doc__ are
            # assigned to the new partial(data) the same as they were in data. This isn't strictly necessary but makes
            # inspecting these functions easier.
            data = functools.update_wrapper(partial(data), data)
            data.__module__ = getattr(data, "__module__", "<nomodule>")
            data.__name__ = ".".join([getattr(data, "__name__", "<unnamed>"), name])
            data.__qualname__ = ".".join([getattr(data, "__qualname__", "<unnamed>"), name])
            self.__data[name] = _DynamicData(data)
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

    def _multi_load(self, multi_name_load_kwargs: list[tuple[DataSourceName, dict[str, Any]]]) -> list[pd.DataFrame]:
        """Loads multiple data sources as efficiently as possible.

        Deduplicates a list of (data source name, load keyword argument dictionary) tuples so that each one corresponds
        to only a single load() call. In the worst case scenario where there are no repeated tuples then performance of
        this function is identical to doing a load call for each tuple.

        If a data source is static then load keyword argument dictionary must be {}.

        Args:
            multi_name_load_kwargs: List of (data source name, load keyword argument dictionary).

        Returns:
            Loaded data in the same order as `multi_name_load_kwargs` was supplied.
        """

        # Easiest way to make a key to de-duplicate each (data source name, load keyword argument dictionary) tuple.
        def encode_load_key(name, load_kwargs):
            return json.dumps([name, load_kwargs], sort_keys=True)

        def decode_load_key(key):
            return json.loads(key)

        # dict.fromkeys does the de-duplication.
        load_key_to_data = dict.fromkeys(
            encode_load_key(name, load_kwargs) for name, load_kwargs in multi_name_load_kwargs
        )

        # Load each key only once.
        for load_key in load_key_to_data.keys():
            name, load_kwargs = decode_load_key(load_key)
            load_key_to_data[load_key] = self[name].load(**load_kwargs)

        return [load_key_to_data[encode_load_key(name, load_kwargs)] for name, load_kwargs in multi_name_load_kwargs]

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
