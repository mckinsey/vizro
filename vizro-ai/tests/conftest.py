import pytest

# Allow our custom assert functions in tests_utils/asserts.py to do introspection nicely still.
# See https://pytest.org/en/7.4.x/how-to/assert.html#assertion-introspection-details
pytest.register_assert_rewrite("asserts")
