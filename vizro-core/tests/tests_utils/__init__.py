# This is not actually required but helps PyCharm find the right function when using "Go to declaration".
# The strange structure here is necessary so that tests_utils can be imported in an intuitive way without adding the
# whole tests folder to the pythonpath. See https://stackoverflow.com/a/75635524.
from asserts import assert_components_equal
