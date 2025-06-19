"""Contains utilities for the implementation of vizro components."""

from collections import defaultdict
from collections.abc import Mapping
from dash import get_relative_path
from flask import g
from typing import Any
from vizro.managers import model_manager


def _set_defaults_nested(supplied: Mapping[str, Any], defaults: Mapping[str, Any]) -> dict[str, Any]:
    supplied = defaultdict(dict, supplied)
    for default_key, default_value in defaults.items():
        if isinstance(default_value, Mapping):
            supplied[default_key] = _set_defaults_nested(supplied[default_key], default_value)
        else:
            supplied.setdefault(default_key, default_value)
    return dict(supplied)


def _get_relative_path_with_unknown_url_params(page_path: str) -> str:
    base_path = get_relative_path(page_path)

    # Find unknown url query parameters inspecting the model_manager
    unknown_params = {
        key: value for key, value in g.url_query_params.items()
        if key not in model_manager
    }

    if not unknown_params:
        return base_path

    # Build the query string from unknown parameters
    query_string = "&".join(f"{key}={value}" for key, value in unknown_params.items())
    return f"{base_path}?{query_string}"
