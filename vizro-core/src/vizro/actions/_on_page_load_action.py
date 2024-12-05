"""Pre-defined action function "_on_page_load" to be reused in `action` parameter of VizroBaseModels."""

from pydantic import field_validator
from typing import Any, Optional, Callable

from dash import ctx, Output

from vizro.actions._actions_utils import _get_modified_page_figures


from vizro.managers._model_manager import ModelID, model_manager
from vizro.models._action._action import NewAction

from vizro.models.types import capture

from vizro.models import Action


# TODO NOW: rename apply_controls or similar. Docstring. Tidy comments in arguments.
class _on_page_load(NewAction):
    targets: list[ModelID]

    def __call__(self, **inputs: dict[str, Any]) -> dict[ModelID, Any]:
        """Applies controls to charts on page once the page is opened (or refreshed).

        Args:
            targets: List of target component ids to filter by chart interaction. If missing, will target all valid
                components on page. Defaults to `None`.
            inputs: Dict mapping action function names with their inputs e.g.
                inputs = {'filters': [], 'parameters': ['gdpPercap'], 'filter_interaction': [], 'theme_selector': True}

        Returns:
            Dict mapping target component ids to modified charts/components e.g. {'my_scatter': Figure({})}
        """

        # TODO NOW: comment about how filters, paramters, filter_interaction currently ignored but will be used in
        #  future when do pattern matching callback.

        return _get_modified_page_figures(
            ctds_filter=ctx.args_grouping["external"]["filters"],
            ctds_filter_interaction=ctx.args_grouping["external"]["filter_interaction"],
            ctds_parameter=ctx.args_grouping["external"]["parameters"],
            targets=self.targets,
        )

    # update_figures
    # def _post_init(self):
    #     """Post initialization is called in the vm.Action build phase, and it is used to validate and calculate the
    #     properties of the CapturedActionCallable. With this, we can validate the properties and raise errors before
    #     the action is built. Also, "input"/"output"/"components" properties and "pure_function" can use these validated
    #     and the calculated arguments.
    #     """
    #     self._page_id = model_manager._get_model_page_id(model_id=self._action_id)
    #
    #     # Validate and calculate "targets"
    #     targets = self._arguments.get("targets")
    #     if targets:
    #         for target in targets:
    #             if self._page_id != model_manager._get_model_page_id(model_id=target):
    #                 raise ValueError(f"Component '{target}' does not exist on the page '{self._page_id}'.")
    #     else:
    #         targets = model_manager._get_page_model_ids_with_figure(page_id=self._page_id)
    #     self._arguments["targets"] = self.targets = targets
