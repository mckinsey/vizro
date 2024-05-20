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


def make_random_data_with_args(label="x"):
    return make_random_data().assign(label=label)


# This is important to test since it's like how kedro datasets work.
class RandomData:
    # This cannot be @staticmethod since we want to test it as a bound method.
    def load(self):
        return make_random_data()


class RandomDataWithArgs:
    # This cannot be @staticmethod since we want to test it as a bound method.
    def load(self, label="x"):
        return make_random_data_with_args(label)


make_random_data_lambda = lambda: make_random_data()  # noqa: E731

make_random_data_partial = partial(make_random_data)

make_random_data_with_args_lambda = lambda label="x": make_random_data_with_args(label)  # noqa: E731

make_random_data_with_args_partial = partial(make_random_data_with_args)


# We test the function and bound method cases but not the unbound methods RandomData.load and RandomDataWithArgs.load
# which are not important.
@pytest.mark.parametrize(
    "data_callable",
    [
        make_random_data,
        make_random_data_with_args,
        RandomData().load,
        RandomDataWithArgs().load,
        make_random_data_lambda,
        make_random_data_with_args_lambda,
        make_random_data_partial,
        make_random_data_with_args_partial,
    ],
)
class TestCacheNotOperational:
    def test_null_cache_no_app(self, data_callable):
        # No app at all, so data_manager._cache_has_app is False.
        data_manager["data"] = data_callable
        loaded_data_1 = data_manager["data"].load()
        loaded_data_2 = data_manager["data"].load()
        assert_frame_not_equal(loaded_data_1, loaded_data_2)

    def test_null_cache_with_app(self, data_callable):
        # App exists but cache is NullCache so does not do anything.
        data_manager["data"] = data_callable
        Vizro()
        loaded_data_1 = data_manager["data"].load()
        loaded_data_2 = data_manager["data"].load()
        assert_frame_not_equal(loaded_data_1, loaded_data_2)

    def test_cache_no_app(self, data_callable):
        # App exists and has a real cache but data_manager.cache is set too late so app is not attached to cache.
        data_manager["data"] = data_callable
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


# We test the function and bound method cases but not the unbound method RandomData.load which is not important.
@pytest.mark.parametrize(
    "data_callable",
    [
        make_random_data,
        RandomData().load,
        make_random_data_lambda,
        make_random_data_partial,
    ],
)
class TestCache:
    def test_default_timeout(self, data_callable, simple_cache):
        data_manager["data"] = data_callable

        loaded_data_1 = data_manager["data"].load()
        loaded_data_2 = data_manager["data"].load()

        # Cache does not expire.
        assert_frame_equal(loaded_data_1, loaded_data_2)

    def test_change_non_default_timeout(self, data_callable):
        data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 1})
        Vizro()
        data_manager["data"] = data_callable

        loaded_data_1 = data_manager["data"].load()
        loaded_data_2 = data_manager["data"].load()
        time.sleep(1)
        loaded_data_3 = data_manager["data"].load()
        loaded_data_4 = data_manager["data"].load()

        # Cache has expired between loaded_data_2 and loaded_data_3 only.
        assert_frame_equal(loaded_data_1, loaded_data_2)
        assert_frame_equal(loaded_data_3, loaded_data_4)
        assert_frame_not_equal(loaded_data_2, loaded_data_3)

    def test_change_individual_timeout(self, data_callable, simple_cache):
        data_manager["data"] = data_callable
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


# We test the function and bound method cases but not the unbound method RandomDataWithArgs.load which is not important.
@pytest.mark.usefixtures("simple_cache")
@pytest.mark.parametrize(
    "data_callable",
    [
        make_random_data_with_args,
        RandomDataWithArgs().load,
        make_random_data_with_args_lambda,
        make_random_data_with_args_partial,
    ],
)
class TestCacheWithArguments:
    def test_default_timeout(self, data_callable):
        # Analogous to TestCache.test_default_timeout
        data_manager["data"] = data_callable

        loaded_data_x_1 = data_manager["data"].load("x")
        loaded_data_y_1 = data_manager["data"].load("y")
        loaded_data_x_2 = data_manager["data"].load("x")
        loaded_data_y_2 = data_manager["data"].load("y")

        # Memoization of arguments works correctly.
        assert_frame_equal(loaded_data_x_1, loaded_data_x_2)
        assert_frame_equal(loaded_data_y_1, loaded_data_y_2)
        assert_frame_not_equal(loaded_data_x_1, loaded_data_y_1)

    def test_change_individual_timeout(self, data_callable):
        # Analogous to TestCache.test_change_individual_timeout.
        data_manager["data"] = data_callable
        data_manager["data"].timeout = 1

        loaded_data_x_1 = data_manager["data"].load("x")
        loaded_data_x_2 = data_manager["data"].load("x")
        loaded_data_y_1 = data_manager["data"].load("y")
        loaded_data_y_2 = data_manager["data"].load("y")
        time.sleep(1)
        loaded_data_x_3 = data_manager["data"].load("x")
        loaded_data_x_4 = data_manager["data"].load("x")
        loaded_data_y_3 = data_manager["data"].load("y")
        loaded_data_y_4 = data_manager["data"].load("y")

        # For both x and y, cache has expired between loaded_data_2 and loaded_data_3 only.
        assert_frame_equal(loaded_data_x_1, loaded_data_x_2)
        assert_frame_equal(loaded_data_x_3, loaded_data_x_4)
        assert_frame_not_equal(loaded_data_x_2, loaded_data_x_3)

        assert_frame_equal(loaded_data_y_1, loaded_data_y_2)
        assert_frame_equal(loaded_data_y_3, loaded_data_y_4)
        assert_frame_not_equal(loaded_data_y_2, loaded_data_y_3)

        assert_frame_not_equal(loaded_data_x_1, loaded_data_y_1)
        assert_frame_not_equal(loaded_data_x_3, loaded_data_y_3)

    def test_timeout_expires_all(self, data_callable):
        # When the cache for one set of memoized arguments expires, the cache for the whole data source expires, even
        # for other values of memoized arguments.
        # This behavior is not particularly desirable (in fact it's maybe a bit annoying); the test is here just
        # to document the current behavior. It's not easy to change this behavior within flask-caching.
        # Loading sequence of data sources is as follows:
        # t=0: load x_1
        # t=1: load x_2     y_1  -> x cache has not expired
        # t=2: load x_3     y_2  -> x cache has expired. y cache might be expected to not expire but also has.
        # t=3: load         y_3
        data_manager["data"] = data_callable
        data_manager["data"].timeout = 2

        loaded_data_x_1 = data_manager["data"].load("x")
        time.sleep(1)
        loaded_data_x_2 = data_manager["data"].load("x")
        loaded_data_y_1 = data_manager["data"].load("y")
        time.sleep(1)
        loaded_data_x_3 = data_manager["data"].load("x")
        loaded_data_y_2 = data_manager["data"].load("y")
        time.sleep(1)
        loaded_data_y_3 = data_manager["data"].load("y")

        # These are as you would expect.
        assert_frame_equal(loaded_data_x_1, loaded_data_x_2)
        assert_frame_not_equal(loaded_data_x_2, loaded_data_x_3)

        # These you might expect to be the other way round:
        # assert_frame_equal(loaded_data_y_1, loaded_data_y_2)
        # assert_frame_not_equal(loaded_data_y_2, loaded_data_y_3)
        assert_frame_not_equal(loaded_data_y_1, loaded_data_y_2)
        assert_frame_equal(loaded_data_y_2, loaded_data_y_3)

    def test_named_and_default_args(self, data_callable):
        data_manager["data"] = data_callable

        loaded_data_x_1 = data_manager["data"].load(label="x")
        loaded_data_x_2 = data_manager["data"].load()
        loaded_data_x_3 = data_manager["data"].load("x")

        assert_frame_equal(loaded_data_x_1, loaded_data_x_2)
        assert_frame_equal(loaded_data_x_2, loaded_data_x_3)


class TestCacheIndependence:
    # Test both data callable with and without args in one test. The ones which don't take args are just passed an
    # empty dictionary so it's like doing data_manager["data_x"].load() with no arguments.
    @pytest.mark.parametrize(
        "data_callable, kwargs",
        [
            (make_random_data, {}),
            (RandomData().load, {}),
            (make_random_data_lambda, {}),
            (make_random_data_partial, {}),
            (make_random_data_with_args, {"label": "z"}),
            (RandomDataWithArgs().load, {"label": "z"}),
            (make_random_data_with_args_lambda, {"label": "z"}),
            (make_random_data_with_args_partial, {"label": "z"}),
        ],
    )
    def test_shared_dynamic_data_callable_no_timeout(self, data_callable, kwargs, simple_cache):
        # Two data sources that share the same function or bound method are independent when neither times out.
        # It doesn't really matter if this test passes; it's mainly here just to document the current behavior. The use
        # cases for actually wanting to do this seem limited.
        data_manager["data_x"] = data_callable
        data_manager["data_y"] = data_callable

        loaded_data_x_1 = data_manager["data_x"].load(**kwargs)
        loaded_data_y_1 = data_manager["data_y"].load(**kwargs)
        loaded_data_x_2 = data_manager["data_x"].load(**kwargs)
        loaded_data_y_2 = data_manager["data_y"].load(**kwargs)

        assert_frame_equal(loaded_data_x_1, loaded_data_x_2)
        assert_frame_equal(loaded_data_y_1, loaded_data_y_2)
        assert_frame_not_equal(loaded_data_x_1, loaded_data_y_1)

    # Test both data callable with and without args in one test. The ones which don't take args are just passed an
    # empty dictionary so it's like doing data_manager["data_x"].load() with no arguments.
    @pytest.mark.parametrize(
        "data_callable, kwargs",
        [
            (make_random_data, {}),
            (RandomData().load, {}),
            (make_random_data_lambda, {}),
            (make_random_data_partial, {}),
            (make_random_data_with_args, {"label": "z"}),
            (RandomDataWithArgs().load, {"label": "z"}),
            (make_random_data_with_args_lambda, {"label": "z"}),
            (make_random_data_with_args_partial, {"label": "z"}),
        ],
    )
    def test_shared_dynamic_data_callable_with_timeout(self, data_callable, kwargs, simple_cache):
        # Two data sources that share the same function or bound method are independent when one times out.
        # It doesn't really matter if this test passes; it's mainly here just to document the current behavior. The use
        # cases for actually wanting to do this seem limited.
        data_manager["data_x"] = data_callable
        data_manager["data_y"] = data_callable
        data_manager["data_y"].timeout = 1

        loaded_data_x_1 = data_manager["data_x"].load(**kwargs)
        loaded_data_y_1 = data_manager["data_y"].load(**kwargs)
        time.sleep(1)
        loaded_data_x_2 = data_manager["data_x"].load(**kwargs)
        loaded_data_y_2 = data_manager["data_y"].load(**kwargs)

        # Cache has expired for data_y but not data_x.
        assert_frame_equal(loaded_data_x_1, loaded_data_x_2)
        assert_frame_not_equal(loaded_data_y_1, loaded_data_y_2)

    @pytest.mark.parametrize(
        "random_data_cls, kwargs",
        [
            (RandomData, {}),
            (RandomDataWithArgs, {"label": "z"}),
        ],
    )
    def test_independent_dynamic_data_callable_no_timeout(self, simple_cache, random_data_cls, kwargs):
        # Two data sources use same method but have *different* bound instances are independent when neither times out.
        # This is the same as test_shared_dynamic_data_callable_no_timeout but it *does* matter that this test passes.
        data_manager["data_x"] = random_data_cls().load
        data_manager["data_y"] = random_data_cls().load

        loaded_data_x_1 = data_manager["data_x"].load(**kwargs)
        loaded_data_y_1 = data_manager["data_y"].load(**kwargs)
        loaded_data_x_2 = data_manager["data_x"].load(**kwargs)
        loaded_data_y_2 = data_manager["data_y"].load(**kwargs)

        assert_frame_equal(loaded_data_x_1, loaded_data_x_2)
        assert_frame_equal(loaded_data_y_1, loaded_data_y_2)
        assert_frame_not_equal(loaded_data_x_1, loaded_data_y_1)

    @pytest.mark.parametrize(
        "random_data_cls, kwargs",
        [
            (RandomData, {}),
            (RandomDataWithArgs, {"label": "z"}),
        ],
    )
    def test_independent_dynamic_data_callable_with_timeout(self, simple_cache, random_data_cls, kwargs):
        # Two data sources use same method but have *different* bound instances are independent when one times out.
        # This is the same as test_shared_dynamic_data_callable_with_timeout but it *does* matter that this test passes.
        data_manager["data_x"] = random_data_cls().load
        data_manager["data_y"] = random_data_cls().load
        data_manager["data_y"].timeout = 1

        loaded_data_x_1 = data_manager["data_x"].load(**kwargs)
        loaded_data_y_1 = data_manager["data_y"].load(**kwargs)
        time.sleep(1)
        loaded_data_x_2 = data_manager["data_x"].load(**kwargs)
        loaded_data_y_2 = data_manager["data_y"].load(**kwargs)

        # Cache has expired for data_y but not data_x.
        assert_frame_equal(loaded_data_x_1, loaded_data_x_2)
        assert_frame_not_equal(loaded_data_y_1, loaded_data_y_2)
