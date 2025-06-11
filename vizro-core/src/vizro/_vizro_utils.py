"""Contains utilities for the implementation of vizro components."""

from collections import defaultdict
from collections.abc import Mapping
from typing import Any


def _set_defaults_nested(supplied: Mapping[str, Any], defaults: Mapping[str, Any]) -> dict[str, Any]:
    supplied = defaultdict(dict, supplied)
    for default_key, default_value in defaults.items():
        if isinstance(default_value, Mapping):
            supplied[default_key] = _set_defaults_nested(supplied[default_key], default_value)
        else:
            supplied.setdefault(default_key, default_value)
    return dict(supplied)
