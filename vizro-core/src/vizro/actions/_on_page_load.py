from typing import Any, Literal

from dash import ctx
from pydantic import Field

from vizro.actions._abstract_action import _AbstractAction
from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.models.types import ModelID, _Controls


# TODO-AV2 A 3: rename _on_page_load if desired and make public. Similarly for other built-in actions.
class _on_page_load(_AbstractAction):
    type: Literal["_on_page_load"] = "_on_page_load"

    targets: list[ModelID] = Field(description="Target component IDs.")

    def function(self, _controls: _Controls) -> dict[ModelID, Any]:
        """Applies controls to charts on page once the page is opened (or refreshed).

        Returns:
            Dict mapping target chart ids to modified figures e.g. {"my_scatter": Figure(...)}.

        """
        # TODO-AV2 A 1: _controls is not currently used but instead taken out of the Dash context. This
        # will change in future once the structure of _controls has been worked out and we know how to pass ids through.
        # See https://github.com/mckinsey/vizro/pull/880
        return _get_modified_page_figures(
            ctds_filter=ctx.args_grouping["external"]["_controls"]["filters"],
            ctds_parameter=ctx.args_grouping["external"]["_controls"]["parameters"],
            ctds_filter_interaction=ctx.args_grouping["external"]["_controls"]["filter_interaction"],
            targets=self.targets,
        )

    @property
    def outputs(self):  # type: ignore[override]
        return {target: target for target in self.targets}
