from collections.abc import Iterable
from typing import Any, Literal, cast

from dash import ctx
from pydantic import Field
from typing_extensions import deprecated

from vizro.actions._abstract_action import _AbstractAction
from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers._model_manager import FIGURE_MODELS, model_manager
from vizro.models._models_utils import _log_call
from vizro.models.types import FigureType, ModelID, _Controls


@deprecated(
    "`filter_interaction` is deprecated and [will not exist in Vizro 0.2.0]("
    "https://vizro.readthedocs.io/en/stable/pages/API-reference/deprecations/#filter-interaction). Use the more "
    "powerful and flexible [`set_control`][vizro.actions.set_control].",
    category=FutureWarning,
)
class filter_interaction(_AbstractAction):
    """Filters targeted graph, tables and figures when a source graph or table is clicked.

    Args:
        targets (list[ModelID]): Target component to be affected by filter. If none are given then target all
            valid components on the page.
    """

    type: Literal["filter_interaction"] = "filter_interaction"

    # Note this has a default value, unlike on_page_load, filter and parameter. It's like export_data.
    targets: list[ModelID] = Field(default=[], description="Target component IDs.")

    @_log_call
    def pre_build(self):
        # Set targets to all figures on the page if not already set. In this case we don't need to check the targets
        # are valid.
        # TODO-AV2 A 4: work out where this duplicated get_all_targets_on_page logic should live. Not important for
        #  filter_interaction given that will disappear but possibly relevant to other actions. Do we even want to
        #  keep behavior that not specifying targets downloads everything on the page? We'd still want the validation
        #  using the model_manager though.
        figure_ids_on_page = [
            model.id
            for model in cast(
                Iterable[FigureType],
                model_manager._get_models(FIGURE_MODELS, root_model=model_manager._get_model_page(self)),
            )
        ]

        if not self.targets:
            self.targets = figure_ids_on_page
        elif invalid_targets := set(self.targets) - set(figure_ids_on_page):
            raise ValueError(f"targets {invalid_targets} are not valid figures on the page.")

        # TODO: This check is temporarily disabled to avoid requiring a prior call to ag_grid or table pre_build.
        #  Otherwise, their self._inner_component_id may not be set, leading to an error when checking "modelID" in
        #  triggered_model._filter_interaction_input. We should revisit this when reworking filter interaction
        #  to find a better way to reintegrate it. Possibly now that self._inner_component_id is now set in
        #  model_post_init rather than pre_build there's an easier solution here.
        # # Check that the triggered model has the required attributes (e.g. Graph does but Button doesn't).
        # # This could potentially be done with isinstance and FigureWithFilterInteractionType but filter_interaction
        # # will be removed in future anyway.
        # triggered_model = self._get_triggered_model()
        # required_attributes = ["_filter_interaction_input", "_filter_interaction"]
        # for attribute in required_attributes:
        #     if not hasattr(triggered_model, attribute):
        #         raise ValueError(f"Model {triggered_model.id} does not have required attribute `{attribute}`.")
        #     if "modelID" not in triggered_model._filter_interaction_input:
        #         raise ValueError(
        #             f"Model {triggered_model.id} does not have required State `modelID` in "
        #             "`_filter_interaction_input`."
        #         )

    def function(self, _controls: _Controls) -> dict[ModelID, Any]:
        """Applies _controls to charts on page once the page is opened (or refreshed).

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
