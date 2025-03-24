import importlib
from collections.abc import Iterable
from typing import Any, Literal, cast

from dash import Output, ctx, dcc

from vizro.actions import AbstractAction
from vizro.actions._actions_utils import _apply_filters, _get_unfiltered_data
from vizro.managers import model_manager
from vizro.managers._model_manager import FIGURE_MODELS, ModelID
from vizro.models import VizroBaseModel
from vizro.models.types import _Controls


# TODO NOW: check how schema for this is generated.
class export_data(AbstractAction):
    type: Literal["export_data"] = "export_data"

    targets: list[
        ModelID
    ] = []  # TODO NOW: think about whether should in future rename this so it doesn't inconsistently use targets? May be ok now that targets doesn't yet have special role.
    file_format: Literal["csv", "xlsx"] = "csv"

    # TODO NOW CHECK: continue testing this and eventually remove.
    runtime_arg: str

    def function(
        self,
        runtime_arg,
        _controls: _Controls,
    ) -> dict[str, Any]:
        # TODO NOW: docstring
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
        # TODO: _controls is not currently used but instead taken out of the Dash context. This
        # will change in future once the structure of _controls has been worked out and we know how to pass ids through.
        # See https://github.com/mckinsey/vizro/pull/880
        # TODO NOW: move the setting of targets to validator. Reused in outputs and components
        targets = self.targets or [
            output["id"]["target_id"]
            for output in ctx.outputs_list
            if isinstance(output["id"], dict) and output["id"]["type"] == "download_dataframe"
        ]
        for target in targets:
            if target not in model_manager:
                raise ValueError(f"Component '{target}' does not exist.")

        ctds = ctx.args_grouping["external"]["_controls"]
        outputs = {}

        for target, unfiltered_data in _get_unfiltered_data(ctds["parameters"], targets).items():
            filtered_data = _apply_filters(unfiltered_data, ctds["filters"], ctds["filter_interaction"], target)
            # TODO NOW: refactor to dictionary lookup with validation
            if self.file_format == "csv":
                writer = filtered_data.to_csv
            elif self.file_format == "xlsx":
                writer = filtered_data.to_excel

            outputs[f"download_dataframe_{target}"] = dcc.send_data_frame(
                writer=writer, filename=f"{runtime_arg}{target}.{self.file_format}", index=False
            )

        return outputs

    # TODO NOW: think about if this is best way.
    # overrides _outputs_ not outputs
    # could convert to string ids and use outputs
    # leave like this because hopefully will have single download component in future anyway with a reserved id
    @property
    def _transformed_outputs(self) -> dict[str, Output]:
        # TODO NOW: comment
        targets = self.targets or [
            model.id
            for model in cast(
                Iterable[VizroBaseModel],
                model_manager._get_models(FIGURE_MODELS, model_manager._get_model_page(self)),
            )
        ]

        return {
            f"download_dataframe_{target}": Output(
                component_id={"type": "download_dataframe", "action_id": self.id, "target_id": target},
                component_property="data",
            )
            for target in targets
        }

    # TODO NOW: just needed due to abstractmethod
    @property
    def outputs(self):
        pass

    @property
    def _dash_components(self) -> list[dcc.Download]:
        """Creates dcc.Downloads for target components of the `export_data` action."""
        targets = self.targets or [
            model.id
            for model in cast(
                Iterable[VizroBaseModel],
                model_manager._get_models(FIGURE_MODELS, model_manager._get_model_page(self)),
            )
        ]

        return [
            dcc.Download(id={"type": "download_dataframe", "action_id": self.id, "target_id": target})
            for target in targets
        ]


# TODO NOW: add this in right place.
# TODO: Problem: generic Action model shouldn't depend on details of particular actions like export_data.
# Possible solutions: make a generic mapping of action functions to validation functions or the imports they
# require, and make the code here look up the appropriate validation using the function as key
# This could then also involve other validations currently only carried out at run-time in pre-defined actions, such
# as e.g. checking if the correct arguments have been provided to the file_format in export_data.
def validate_predefined_actions(function):
    if function._function.__name__ == "export_data":
        file_format = function._arguments.get("file_format")
        if file_format not in [None, "csv", "xlsx"]:
            raise ValueError(f'Unknown "file_format": {file_format}. Known file formats: "csv", "xlsx".')
        if file_format == "xlsx":
            if importlib.util.find_spec("openpyxl") is None and importlib.util.find_spec("xlsxwriter") is None:
                raise ModuleNotFoundError("You must install either openpyxl or xlsxwriter to export to xlsx format.")
    return function


# TODO NOW: put this in
