import pytest

from vizro._vizro_utils import _set_defaults_nested


@pytest.fixture
def default_dictionary():
    return {"a": {"b": {"c": 1, "d": 2}}, "e": 3}


@pytest.mark.parametrize(
    "input, expected",
    [
        ({}, {"a": {"b": {"c": 1, "d": 2}}, "e": 3}),  # nothing supplied
        ({"e": 10}, {"a": {"b": {"c": 1, "d": 2}}, "e": 10}),  # flat main key
        ({"a": {"b": {"c": 11, "d": 12}}}, {"a": {"b": {"c": 11, "d": 12}}, "e": 3}),  # updated multiple nested keys
        ({"a": {"b": {"c": 1, "d": {"f": 42}}}}, {"a": {"b": {"c": 1, "d": {"f": 42}}}, "e": 3}),  # add new dict
        ({"a": {"b": {"c": 5}}}, {"a": {"b": {"c": 5, "d": 2}}, "e": 3}),  # arbitrary nesting
    ],
)
def test_set_defaults_nested(default_dictionary, input, expected):
    assert _set_defaults_nested(input, default_dictionary) == expected
