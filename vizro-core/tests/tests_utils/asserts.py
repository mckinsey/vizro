import json

import dash.development
import plotly


def strip_keys(object, keys):
    """Strips all entries with key "id" from a dictionary, regardless of how deeply it's nested.

    This makes it easy to compare dictionaries generated from Dash components we've created that contain random IDs.
    """
    if isinstance(object, dict):
        object = {key: strip_keys(value, keys) for key, value in object.items() if key not in keys}
    elif isinstance(object, list):
        object = [strip_keys(item, keys) for item in object]
    return object


def component_to_dict(component: dash.development.base_component.Component) -> dict:
    return json.loads(json.dumps(component, cls=plotly.utils.PlotlyJSONEncoder))


# TODO: implement some sort of depth limit to comparison so can use in high level tests, roll out more widely across
# tests
def assert_component_equal(left, right, keys_to_strip=None):
    # Note we check for None explicitly because {} is a valid value for keys_to_strip.
    keys_to_strip = keys_to_strip if keys_to_strip is not None else {"id", "class_name", "className"}
    left = strip_keys(component_to_dict(left), keys_to_strip)
    right = strip_keys(component_to_dict(right), keys_to_strip)
    assert left == right
