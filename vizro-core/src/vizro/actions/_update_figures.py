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


# TODO AM QQ: Should we rename "update_figures"? It updates controls too.
#  Consider combining words update/recreate/refresh with figures/models/controls.
class update_figures(_AbstractAction):
    """Exports data of target charts, tables and figures.

    Args:
        targets (list[ModelID]): List of target component ids that will be rebuilt. If none are given then target
            all components on the page.

    Example:
        ```python
        import vizro.actions as va

        vm.Button(
            text="Recreate first graph",
            actions=va.update_figures(targets=["graph_id_1"]),
        )
        ```
    """

    type: Literal["update_figures"] = "update_figures"

    targets: list[ModelID] = Field(default=[], description="Target component IDs.")

    @_log_call
    def pre_build(self):
        # Set targets to all figures on the page if not already set.

        # TODO AM-PP OQ: This implementation enables users to manually specify filter targets outside the container.
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
        """Recreates targeted charts by applying controls.

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
        # Special handling for controls as otherwise the control's default action output would alter the selector value.
        return {
            target: f"{target}.selector" if isinstance(model_manager[target], (vm.Filter, vm.Parameter)) else target
            for target in self.targets
        }
