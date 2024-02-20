"""Contains utilities for the implementation of table callables."""

from collections import defaultdict
from typing import Any, Dict, Mapping


def _set_defaults_nested(supplied: Mapping[str, Any], defaults: Mapping[str, Any]) -> Dict[str, Any]:
    supplied = defaultdict(dict, supplied)
    for default_key, default_value in defaults.items():
        if isinstance(default_value, Mapping):
            supplied[default_key] = _set_defaults_nested(supplied[default_key], default_value)
        else:
            supplied.setdefault(default_key, default_value)
    return dict(supplied)
