from typing import Any

from dash import ctx
from pydantic import Field

from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers._model_manager import ModelID, model_manager
from vizro.models._action._action import AbstractAction, Controls

from typing import Literal


class _parameter(AbstractAction):
    type: Literal["_parameter"] = "_parameter"

    targets: list[ModelID] = Field(description="Targets in the form `<target_component>.<target_argument>`.")

    @property
    def _target_ids(self) -> list[ModelID]:
        # This cannot be implemented as PrivateAttr(default_factory=lambda data: ...) because, unlike Field,
        # PrivateAttr does not yet support an argument to the default_factory function. See:
        # https://github.com/pydantic/pydantic/issues/10992
        return [target.partition(".")[0] for target in self.targets]

    def function(self, controls: Controls) -> dict[ModelID, Any]:
        """Applies controls to charts on page once the page is opened (or refreshed).

        Returns:
            Dict mapping target chart ids to modified figures e.g. {"my_scatter": Figure(...)}.

        """
        # This is identical to _on_page_load but with self._target_ids rather than self.targets.
        # TODO: controls is not currently used but instead taken out of the Dash context. This
        # will change in future once the structure of controls has been worked out and we know how to pass ids through.
        # See https://github.com/mckinsey/vizro/pull/880
        return _get_modified_page_figures(
            ctds_filter=ctx.args_grouping["external"]["controls"]["filters"],
            ctds_parameter=ctx.args_grouping["external"]["controls"]["parameters"],
            ctds_filter_interaction=ctx.args_grouping["external"]["controls"]["filter_interaction"],
            targets=self._target_ids,
        )

    @property
    def outputs(self):
        # This is identical to _on_page_load but with self._target_ids rather than self.targets.
        outputs = {}

        for target in self._target_ids:
            component_id = target
            component_property = model_manager[target]._output_component_property
            outputs[target] = f"{component_id}.{component_property}"

        return outputs
