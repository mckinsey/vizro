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
    mode: Literal["ag_grid", "graph"] = "graph"  # Will need to be filled in automatically.

    # Need to check if show_in_url = True
    # and output to URL.

    # targets: list[ModelID] = Field(description="Target component IDs.")

    def function(self, trigger) -> dict[ModelID, Any]:
        if trigger is None:
            # Won't be need once this isn't triggered on page load automatically. Could move vizro_download to page
            # level or implement actions loop fix.
            raise PreventUpdate
        # TODO NOW: docstring
        # No need to take in URL as state since just update for key=value for a single control (?).
        if self.mode == "graph":
            new_control_value = glom(trigger, self.lookup)
        else:
            # f-string glom spec also works here but probably not worth doing - instead just lookup column instead.
            # Would be something like this where user can provide trigger in f-string. It starts looking complicated
            # though.
            # species = glom(trigger, "rowData.{trigger['cellClicked']['rowIndex']}.species".format(trigger)
            new_control_value = trigger["rowData"][trigger["cellClicked"]["rowIndex"]][self.lookup]
            # Could implement this using glom also if we wanted, not sure if any use though:
            # new_control_value = glom(trigger, "rowData.{trigger['cellClicked']['rowIndex']}.{self.lookup}".format(
            # trigger, self)

        target_page = model_manager._get_model_page(model_manager[self.target])
        pathname = target_page.path if target_page != model_manager._get_model_page(self) else dash.no_update
        # TODO NOW: encode the target id

        # TODO NOW: maybe don't send directly to vizro_url but instead to some proxy object and then update
        # vizro_url with cs callback that does encoding.
        # This is nice idea so then b64 logic not needed in Python (yet anyway).
        # And same page vs. different looks more similar.
        # Then do change page as another action in the chain? Would be an extra callback but work with chain. Not sure
        # if good idea.
        return pathname, f"?{self.target}={b64_encode_value(new_control_value)}"

    @property
    def outputs(self):  # type: ignore[override]
        # Would be just self.target in future for same-page control.
        return "vizro_url.pathname", "vizro_url.search"


"""
Current thoughts:

- AgGrid and Graph update_control done in same Action rather than update_control_ag_grid/update_control_graph - 
definitely this is what we want.
- Think about whether glom is best approach for graph. Definitely something like this better than needing to use
customdata (which is still possible), since can do e.g. `pointsData.x` which might be what you need without customdata.
Maybe glom not best language for it, not sure. Or maybe offer user-friendly shortcuts to glom like just "x", 
"customdata" etc. Is there every anything outside points?
- Think about what we actually want to do with AgGrid. Is it sufficient just to provide clicked value or the ID and 
restrict control selector to just use those ID values? Maybe. Note we don't want to load data_frame again on serverside.
- Problem with current approach is it sends all rowData to server. Alternative: CS callback which merges cellClicked 
and only relevant part of rowData. This would then be trigger for update_controls rather than using flexible callback signature.
- When action loop resolved, try to do same page update_controls directly to control.value rather than going 
through URL.
"""
