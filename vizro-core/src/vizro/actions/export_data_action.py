"""Pre-defined action function "export_data" to be reused in `action` parameter of VizroBaseModels."""

from typing import Any, Optional

from dash import ctx, dcc, Output
from typing_extensions import Literal

from vizro.actions._actions_utils import _apply_filters, _get_unfiltered_data
from vizro.managers import model_manager
from vizro.managers._model_manager import ModelID
from vizro.models.types import capture, CapturedActionCallable


class export_data(CapturedActionCallable):
    @staticmethod
    def pure_function(
        targets: Optional[list[ModelID]] = None, file_format: Literal["csv", "xlsx"] = "csv", **inputs: dict[str, Any]
    ) -> dict[str, Any]:
        """Exports visible data of target charts/components on page after being triggered.

        Args:
            targets: List of target component ids to download data from. Defaults to `None`.
            file_format: Format of downloaded files. Defaults to `csv`.
            inputs: Dict mapping action function names with their inputs e.g.
                inputs = {'filters': [], 'parameters': ['gdpPercap'], 'filter_interaction': []}

        Raises:
            ValueError: If unknown file extension is provided.
            ValueError: If target component does not exist on page.

        Returns:
            Dict mapping target component id to modified charts/components e.g. {'my_scatter': Figure({})}

        """
        if not targets:
            targets = [
                output["id"]["target_id"]
                for output in ctx.outputs_list
                if isinstance(output["id"], dict) and output["id"]["type"] == "download_dataframe"
            ]
        for target in targets:
            if target not in model_manager:
                raise ValueError(f"Component '{target}' does not exist.")

        ctds = ctx.args_grouping["external"]
        outputs = {}

        for target, unfiltered_data in _get_unfiltered_data(ctds["parameters"], targets).items():
            filtered_data = _apply_filters(unfiltered_data, ctds["filters"], ctds["filter_interaction"], target)
            if file_format == "csv":
                writer = filtered_data.to_csv
            elif file_format == "xlsx":
                writer = filtered_data.to_excel
            # Invalid file_format should be caught by Action validation

            outputs[f"download_dataframe_{target}"] = dcc.send_data_frame(
                writer=writer, filename=f"{target}.{file_format}", index=False
            )

        return outputs

    @property
    def inputs(self):
        # SAME AS OPL
        from vizro.actions import filter_interaction
        from vizro.actions._callback_mapping._callback_mapping_utils import (
            _get_inputs_of_controls,
            _get_inputs_of_figure_interactions,
        )
        from vizro.models import Filter, Parameter

        page_id = model_manager._get_model_page_id(model_id=self._action_id)
        page = model_manager[page_id]
        # use List[State]
        action_input_mapping = {
            "filters": _get_inputs_of_controls(page=page, control_type=Filter),
            "parameters": _get_inputs_of_controls(page=page, control_type=Parameter),
            # TODO: Probably need to adjust other inputs to follow the same structure list[dict[str, State]]
            "filter_interaction": _get_inputs_of_figure_interactions(
                page=page, action_function=filter_interaction.__wrapped__
            ),
        }
        return action_input_mapping

    @property
    def outputs(self) -> dict[ModelID, Output]:
        # DIFFERENT FROM OPL
        """Gets mapping of relevant output target name and `Outputs` for `export_data` action."""
        try:
            targets = self["targets"]
        except KeyError:
            targets = None

        if not targets:
            targets = model_manager._get_page_model_ids_with_figure(
                page_id=model_manager._get_model_page_id(model_id=self._action_id)
            )

        return {
            f"download_dataframe_{target}": Output(
                component_id={"type": "download_dataframe", "action_id": self._action_id, "target_id": target},
                component_property="data",
            )
            for target in targets
        }

    @property
    # For multiple files could use single dcc.Download but zip file.
    # Will need some way to add new components on the fly for other actions though.
    # e.g. for key-value pairs on screen
    # This could be built into e.g. KeyValuePairs model.
    # Petar qn: what other actions would require new components on page?
    def components(self) -> list[dcc.Download]:
        """Creates dcc.Downloads for target components of the `export_data` action."""
        try:
            targets = self["targets"]
        except KeyError:
            targets = None

        if not targets:
            targets = model_manager._get_page_model_ids_with_figure(
                page_id=model_manager._get_model_page_id(model_id=self._action_id)
            )

        return [
            dcc.Download(id={"type": "download_dataframe", "action_id": self._action_id, "target_id": target})
            for target in targets
        ]
