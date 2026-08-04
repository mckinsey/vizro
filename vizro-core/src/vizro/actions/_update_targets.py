from collections.abc import Iterable
from typing import Any, Literal, cast

from dash import ctx
from pydantic import Field

import vizro.models as vm
from vizro.actions._abstract_action import _AbstractAction
from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers import model_manager
from vizro.managers._model_manager import FIGURE_MODELS
from vizro.models._models_utils import _log_call
from vizro.models.types import FigureType, ModelID, _Controls


class update_targets(_AbstractAction):
    """Refreshes target figures on the page by re-applying the page's controls.

    Re-runs the targeted charts, tables and figures against the current values of the page's filters and parameters.
    This is the shared mechanism behind `Filter`, `Parameter` and on-page-load, and can also be used directly (for
    example on a `Button`) to refresh figures on demand.

    Args:
        targets (list[ModelID]): Component ids to refresh. If none are given then all figures on the page are targeted.
            Defaults to `[]`.

    Example:
        ```python
        import vizro.actions as va
        import vizro.models as vm

        vm.Button(text="Apply controls", actions=va.update_targets(targets=["my_graph"]))
        ```
    """

    type: Literal["update_targets"] = "update_targets"

    targets: list[ModelID] = Field(default=[], description="Component ids to refresh. Defaults to all figures on page.")

    @_log_call
    def pre_build(self):
        # Default to every figure on the page. Dynamic filters are not figures but are still valid explicit targets,
        # since their selector options are recalculated when their underlying data changes.
        # TODO-AV2 A 4: work out where this duplicated get_all_targets_on_page logic should live.
        root_model = model_manager._get_model_page(self)

        figure_ids_on_page = [
            model.id for model in cast(Iterable[FigureType], model_manager._get_models(FIGURE_MODELS, root_model))
        ]
        dynamic_filter_ids_on_page = [
            filter.id
            for filter in cast(Iterable[vm.Filter], model_manager._get_models(vm.Filter, root_model=root_model))
            if filter._dynamic
        ]

        if not self.targets:
            self.targets = figure_ids_on_page
        elif invalid_targets := set(self.targets) - set(figure_ids_on_page + dynamic_filter_ids_on_page):
            raise ValueError(f"targets {invalid_targets} are not valid figures on the page.")

    def function(self, _controls: _Controls) -> dict[ModelID, Any]:
        """Recreates the targeted figures by applying the page's controls.

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
        # Special handling for vm.Filter (dynamic filters can be targets) as otherwise the filter's default action
        # output would alter the selector value.
        return {
            target: f"{target}.selector" if isinstance(model_manager[target], vm.Filter) else target
            for target in self.targets
        }
