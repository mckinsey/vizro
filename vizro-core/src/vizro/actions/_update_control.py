from typing import Any, Callable, Literal

from dash.exceptions import PreventUpdate
from glom import glom
import pandas as pd
from dash import ctx, dash
from pydantic import Field

from vizro.actions._abstract_action import _AbstractAction
from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.actions.utils import b64_encode_value
from vizro.managers import model_manager
from vizro.models.types import ModelID, _Controls


# TODO NOW: maybe handle multiple controls to begin with. This is singular for simplicity as a PoC.
class update_control(_AbstractAction):
    type: Literal["update_control"] = "update_control"

    lookup: str  # TODO NOW: think of good name, want default value for graph? is there ever something outside
    # points?
    target: ModelID  # control_id, not selector_id
    mode: Literal["ag_grid", "graph"] = "graph"  # Will need to be filled in automatically
    trigger: str  # TODO NOW: inject automatically, won't need to specify this in future. Look at my remove actions loop
    # branch

    # Need to check if show_in_url = True
    # and output to URL.

    # targets: list[ModelID] = Field(description="Target component IDs.")

    # TODO NOW: figure out whether we can input AgGrid rowdata automatically. Or maybe ok to just specify manually
    # ag_grid_id.rowData
    # How to switch number of inputs in function depending on mode though? Do we need to merge cellClicked and
    # rowData in clientside callback?

    def function(self, trigger) -> dict[ModelID, Any]:
        if trigger is None:
            # Won't be need once this isn't triggered on page load automatically. Could move vizro_download to page
            # level or implement actions loop fix.
            raise PreventUpdate
        # TODO NOW: docstring
        # No need to take in URL as state since just update for key=value for a single control (?).
        if self.mode == "graph":
            new_control_value = glom(trigger, self.lookup)

        target_page = model_manager._get_model_page(model_manager[self.target])
        pathname = target_page.path if target_page != model_manager._get_model_page(self) else dash.no_update
        # TODO NOW: encode the target id

        return pathname, f"?{self.target}={b64_encode_value(new_control_value)}"

    @property
    def outputs(self):  # type: ignore[override]
        # Would be just self.target in future for same-page control.
        # TODO NOW: think about how this would have variable output depending on same_page condition. Should we also
        #  allow variable input? Also for AgGrid vs Graph?
        return "vizro_url.pathname", "vizro_url.search"
