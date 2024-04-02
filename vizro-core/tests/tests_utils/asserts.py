import json

import dash.development
import plotly

STRIP_ALL = object()


def _strip_keys(object, keys):
    """Strips from a JSON `object` all entries where the key is in keys, regardless of how deeply it's nested."""
    if isinstance(object, dict):
        object = {key: _strip_keys(value, keys) for key, value in object.items() if key not in keys}
    elif isinstance(object, list):
        object = [_strip_keys(item, keys) for item in object]
    return object


def _component_to_dict(component: dash.development.base_component.Component) -> dict:
    """Prepares a Dash `component` for comparison by conversion to JSON object."""
    return json.loads(json.dumps(component, cls=plotly.utils.PlotlyJSONEncoder))


def assert_component_equal(left, right, *, keys_to_strip=None):
    """Checks that the `left` and `right` Dash components are equal, ignoring `keys_to_strip`.

    If keys_to_strip is set to STRIP_ALL then only the type and namespace of component
    will be compared, similar to doing isinstance.

    Examples
        >>> from dash import html
        >>> assert_component_equal(html.Div(), html.Div())
        >>> assert_component_equal(html.Div(id="a"), html.Div(), keys_to_strip={"id"})
        >>> assert_component_equal(html.Div([html.P(), html.P()], id="a"), html.Div(id="a"), keys_to_strip={"children"})
        >>> assert_component_equal(html.Div(html.P(), className="blah", id="a"), html.Div(), keys_to_strip=STRIP_ALL)

    """
    keys_to_strip = keys_to_strip or {}
    if keys_to_strip is STRIP_ALL:
        # Remove all properties from the component dictionary, leaving just "type" and "namespace" behind.
        keys_to_strip = {"props"}

    left = _strip_keys(_component_to_dict(left), keys_to_strip)
    right = _strip_keys(_component_to_dict(right), keys_to_strip)
    assert left == right
