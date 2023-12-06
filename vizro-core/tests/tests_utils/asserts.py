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


def assert_component_equal(left, right, extra_strip_keys=None, keep_keys=None):
    extra_strip_keys = extra_strip_keys or set()
    keep_keys = keep_keys or set()
    total_strip_keys = {"id", "class_name", "className"} | extra_strip_keys - keep_keys

    left = strip_keys(component_to_dict(left), total_strip_keys)
    right = strip_keys(component_to_dict(right), total_strip_keys)
    assert left == right
