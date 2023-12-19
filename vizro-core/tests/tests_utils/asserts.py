import json

import dash.development
import plotly


def _strip_keys(object, keys):
    """Strips from a JSON object all entries where the key is in keys, regardless of how deeply it's nested."""
    if isinstance(object, dict):
        object = {key: _strip_keys(value, keys) for key, value in object.items() if key not in keys}
    elif isinstance(object, list):
        object = [_strip_keys(item, keys) for item in object]
    return object


def _component_to_dict(component: dash.development.base_component.Component) -> dict:
    """Prepares a Dash component for comparison by conversion to JSON object."""
    return json.loads(json.dumps(component, cls=plotly.utils.PlotlyJSONEncoder))


def assert_component_equal(left, right, keys_to_strip=None):
    """Checks that the left and right Dash components are equal, ignoring keys_to_strip.

    Examples:
        >>> from dash import html
        >>> assert_component_equal(html.Div(), html.Div())
        >>> assert_component_equal(html.Div(id="a"), html.Div(), keys_to_strip={"id"})
        >>> assert_component_equal(html.Div(html.Div()), html.Div(), keys_to_strip={"children"})
    """
    keys_to_strip = keys_to_strip or {}

    left = _strip_keys(_component_to_dict(left), keys_to_strip)
    right = _strip_keys(_component_to_dict(right), keys_to_strip)
    assert left == right
