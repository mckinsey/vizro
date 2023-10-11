# Redundant aliases here to prevent ruff from removing unused imports.
from typing import Any, Callable, Dict

from vizro.actions._filter_action import _filter
from vizro.actions._on_page_load_action import _on_page_load
from vizro.actions._parameter_action import _parameter
from vizro.actions.export_data_action import export_data
from vizro.actions.filter_interaction_action import filter_interaction

# Please keep alphabetically ordered
__all__ = ["export_data", "filter_interaction"]

# Actions lookup dictionary to facilitate function comparison
action_functions: Dict[Callable[[Any], Dict[str, Any]], str] = {
    export_data.__wrapped__: "export_data",
    filter_interaction.__wrapped__: "filter_interaction",
    _filter.__wrapped__: "filter",
    _parameter.__wrapped__: "parameter",
    _on_page_load.__wrapped__: "on_page_load",
}
