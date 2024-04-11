"""Unit tests for vizro.managers.data_manager."""

import time
from contextlib import suppress
from functools import partial

import numpy as np
import pandas as pd
import pytest
from asserts import assert_frame_not_equal
from flask_caching import Cache
from pandas.testing import assert_frame_equal
from vizro import Vizro
from vizro.managers import data_manager


@pytest.fixture(autouse=True)
def clear_cache():
    yield
    # Vizro._reset doesn't empty the cache, so any tests which have something other than NullCache must clear it
    # after running. Suppress AttributeError: 'Cache' object has no attribute 'app' that occurs when
    # data_manager._cache_has_app is False.
    with suppress(AttributeError):
        data_manager.cache.clear()


def make_fixed_data():
    return pd.DataFrame([1, 2, 3])


class TestLoad:
    def test_static(self):
        data = make_fixed_data()
        data_manager["data"] = data
        loaded_data = data_manager["data"].load()
        assert_frame_equal(loaded_data, data)
        # Make sure loaded_data is a copy rather than the same object.
        assert loaded_data is not data

    def test_dynamic(self):
        data = make_fixed_data
        data_manager["data"] = data
        loaded_data = data_manager["data"].load()
        assert_frame_equal(loaded_data, data())
        # Make sure loaded_data is a copy rather than the same object.
        assert loaded_data is not data()

    def test_dynamic_lambda(self):
        data = lambda: make_fixed_data()  # noqa: E731
        data_manager["data"] = data
        loaded_data = data_manager["data"].load()
        assert_frame_equal(loaded_data, data())
        # Make sure loaded_data is a copy rather than the same object.
        assert loaded_data is not data()


class TestInvalid:
    def test_static_data_does_not_support_timeout(self):
        data = make_fixed_data()
        data_manager["data"] = data
        with pytest.raises(
            AttributeError, match="Static data that is a pandas.DataFrame itself does not support timeout"
        ):
            data_manager["data"].timeout = 10

    def test_setitem_invalid_callable(self):
        with pytest.raises(TypeError, match="Data source data's function does not have a name."):
            data_manager["data"] = partial(make_fixed_data)

    def test_setitem_invalid_type(self):
        with pytest.raises(
            TypeError, match="Data source data must be a pandas DataFrame or function that returns a pandas DataFrame."
        ):
            data_manager["data"] = pd.Series([1, 2, 3])

    def test_does_not_exist(self):
        with pytest.raises(KeyError, match="Data source data does not exist."):
            data_manager["data"]


def make_random_data():
    return pd.DataFrame(np.random.default_rng().random(3))


class TestCacheNotOperational:
    def test_null_cache_no_app(self):
        # No app at all, so memoize decorator is bypassed completely as data_manager._cache_has_app is False.
        data_manager["data"] = make_random_data
        loaded_data_1 = data_manager["data"].load()
        loaded_data_2 = data_manager["data"].load()
        assert_frame_not_equal(loaded_data_1, loaded_data_2)

    def test_null_cache_with_app(self):
        # App exists but cache is NullCache so does not do anything.
        data_manager["data"] = make_random_data
        Vizro()
        loaded_data_1 = data_manager["data"].load()
        loaded_data_2 = data_manager["data"].load()
        assert_frame_not_equal(loaded_data_1, loaded_data_2)

    def test_cache_no_app(self):
        # App exists and has a real cache but data_manager.cache is set too late so app is not attached to cache.
        data_manager["data"] = make_random_data
        Vizro()
        data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache"})

        with pytest.warns(UserWarning, match="Cache does not have Vizro app attached and so is not operational."):
            loaded_data_1 = data_manager["data"].load()
            loaded_data_2 = data_manager["data"].load()
        assert_frame_not_equal(loaded_data_1, loaded_data_2)


@pytest.fixture
def simple_cache():
    # We don't need the Flask request context to run tests. (flask-caching tests for memoize use
    # app.test_request_context() but look like they don't actually need to, since only flask_caching.Cache.cached
    # requires the request context.)
    # We do need a Flask app to be attached for the cache to be operational though, hence the call Vizro().
    data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
    Vizro()
    yield


class TestCache:
    def test_simple_cache_default_timeout(self, simple_cache):
        data_manager["data"] = make_random_data

        loaded_data_1 = data_manager["data"].load()
        loaded_data_2 = data_manager["data"].load()

        # Cache does not expire.
        assert_frame_equal(loaded_data_1, loaded_data_2)

    def test_change_non_default_timeout(self):
        data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 1})
        Vizro()
        data_manager["data"] = make_random_data

        loaded_data_1 = data_manager["data"].load()
        loaded_data_2 = data_manager["data"].load()
        time.sleep(1)
        loaded_data_3 = data_manager["data"].load()
        loaded_data_4 = data_manager["data"].load()

        # Cache has expired between loaded_data_2 and loaded_data_3 only.
        assert_frame_equal(loaded_data_1, loaded_data_2)
        assert_frame_equal(loaded_data_3, loaded_data_4)
        assert_frame_not_equal(loaded_data_2, loaded_data_3)

    def test_change_individual_timeout(self, simple_cache):
        data_manager["data"] = make_random_data
        data_manager["data"].timeout = 1

        loaded_data_1 = data_manager["data"].load()
        loaded_data_2 = data_manager["data"].load()
        time.sleep(1)
        loaded_data_3 = data_manager["data"].load()
        loaded_data_4 = data_manager["data"].load()

        # Cache has expired between loaded_data_2 and loaded_data_3 only.
        assert_frame_equal(loaded_data_1, loaded_data_2)
        assert_frame_equal(loaded_data_3, loaded_data_4)
        assert_frame_not_equal(loaded_data_2, loaded_data_3)

    def test_shared_dynamic_data_function(self, simple_cache):
        data_manager["data_x"] = make_random_data
        data_manager["data_y"] = make_random_data

        loaded_data_x_1 = data_manager["data_x"].load()
        loaded_data_y_1 = data_manager["data_y"].load()
        loaded_data_x_2 = data_manager["data_x"].load()
        loaded_other_y_2 = data_manager["data_y"].load()

        # Two data sources that shared the same function are independent.
        assert_frame_equal(loaded_data_x_1, loaded_data_x_2)
        assert_frame_equal(loaded_data_y_1, loaded_other_y_2)
        assert_frame_not_equal(loaded_data_x_1, loaded_data_y_1)

    def test_timeouts_do_not_interfere(self, simple_cache):
        # This test only passes thanks to the code in memoize that alters the wrapped.__func__.__qualname__,
        # as explained in the docstring there. If that bit of code is removed then this test correctly fails.
        data_manager["data_x"] = make_random_data
        data_manager["data_y"] = make_random_data
        data_manager["data_y"].timeout = 1

        loaded_data_x_1 = data_manager["data_x"].load()
        loaded_data_y_1 = data_manager["data_y"].load()
        time.sleep(1)
        loaded_data_x_2 = data_manager["data_x"].load()
        loaded_data_y_2 = data_manager["data_y"].load()

        # Cache has expired for data_y but not data_x.
        assert_frame_equal(loaded_data_x_1, loaded_data_x_2)
        assert_frame_not_equal(loaded_data_y_1, loaded_data_y_2)
