"""Pre-defined action function "export_data" to be reused in `action` parameter of VizroBaseModels."""

import inspect
from collections.abc import Iterable
from typing import Annotated, Any, Callable, ClassVar, Literal, TypeVar, cast

from dash import Output, ctx, dcc, State

from vizro.actions._actions_utils import _apply_filters, _get_unfiltered_data
from vizro.managers import model_manager
from vizro.managers._model_manager import FIGURE_MODELS, ModelID
from vizro.models import VizroBaseModel
from vizro.models._action._action import (
    AbstractAction,
    ControlInputs,
    _get_inputs_of_controls,
    _get_inputs_of_figure_interactions,
)
from vizro.models.types import capture, CapturedCallable

T = TypeVar("T")
S = Annotated[ClassVar[T], "s"]


class export_data(AbstractAction):
    # implementation independent, appear in schema
    # BUILD TIME PARAMS
    # SOME REINTERPRETED AT RUNTIME as in AbstractAction
    # but also have possibility of static arguments that you can't do (at least not without type hint) in Action
    targets: list[ModelID] = []  # TODO FUTURE: maybe rename this so it doesn't inconsistently
    # use targets?
    file_format: Literal["csv", "xlsx"] = "csv"

    runtime_arg: str

    def function(
        self,
        runtime_arg,
        filters,
        parameters,
        filter_interaction,
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
        # TODO NOW: move the setting of targets to validator. Reused in outputs and components
        print(f"{runtime_arg=}")
        targets = self.targets or [
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
            # TODO NOW: refactor to dictionary lookup with validation
            if self.file_format == "csv":
                writer = filtered_data.to_csv
            elif self.file_format == "xlsx":
                writer = filtered_data.to_excel
            # Invalid file_format should be caught by Action validation

            outputs[f"download_dataframe_{target}"] = dcc.send_data_frame(
                writer=writer, filename=f"{target}.{self.file_format}", index=False
            )

        return outputs

    @property
    # overrides _outputs_ not outputs
    # could convert to string ids and use outputs
    # leave like this because hopefully will have single download component in future anyway with a reserved id
    def _outputs_(self) -> dict[str, Output]:
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

    # same arguments hold as for outputs for type of argumnet
    @property
    # TODO NOW: put these thoughts somewhere
    # For multiple files could use single dcc.Download but zip file.
    # Will need some way to add new components on the fly for other actions though.
    # e.g. for key-value pairs on screen
    # This could be built into e.g. KeyValuePairs model.
    # Petar qn: what other actions would require new components on page?
    # Note name clash with "components" and current model_manager __get_model_children that looks for "components"
    # for Page.components. Hence call dash_components, which is probably better name anyway.
    def dash_components(self) -> list[dcc.Download]:
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


# TODO NOW: validation
#  -AV2: Maybe we can rename it to '_validation' or similar.

# def _post_init(self):
#     """Post initialization is called in the vm.Action build phase, and it is used to validate and calculate the
#     properties of the CapturedActionCallable. With this, we can validate the properties and raise errors before
#     the action is built. Also, "input"/"output"/"components" properties and "pure_function" can use these validated
#     and the calculated arguments.
#     """
#     self._page_id = model_manager._get_model_page_id(model_id=self._action_id)
#
#     # Validate and calculate "targets"
#     # TODO-AV2-TICKET-NEW-*: Make targets validation reusable for the other actions (maybe even for Filter model).
#     # TODO-AV2-OQ: Rethink using self._arguments
#     targets = self._arguments.get("targets")
#     if targets:
#         for target in targets:
#             if self._page_id != model_manager._get_model_page_id(model_id=target):
#                 # TODO-AV2-TICKET-NEW-*: Improve error message to explain in which action the error occurs.
#                 raise ValueError(f"Component '{target}' does not exist on the page '{self._page_id}'.")
#     else:
#         targets = model_manager._get_page_model_ids_with_figure(page_id=self._page_id)
#     self._arguments["targets"] = self.targets = targets
#
#     # Validate and calculate "file_format"
#     file_format = self._arguments.get("file_format", "csv")
#     if file_format not in ["csv", "xlsx"]:
#         raise ValueError(f'Unknown "file_format": {file_format}.' f' Known file formats: "csv", "xlsx".')
#     if file_format == "xlsx":
#         if importlib.util.find_spec("openpyxl") is None and importlib.util.find_spec("xlsxwriter") is None:
#             raise ModuleNotFoundError("You must install either openpyxl or xlsxwriter to export to xlsx format.")

# From Action
# TODO: Problem: generic Action model shouldn't depend on details of particular actions like export_data.
# Possible solutions: make a generic mapping of action functions to validation functions or the imports they
# require, and make the code here look up the appropriate validation using the function as key
# This could then also involve other validations currently only carried out at run-time in pre-defined actions, such
# as e.g. checking if the correct arguments have been provided to the file_format in export_data.
# @validator("function")
# def validate_predefined_actions(cls, function):
#     if function._function.__name__ == "export_data":
#         file_format = function._arguments.get("file_format")
#         if file_format not in [None, "csv", "xlsx"]:
#             raise ValueError(f'Unknown "file_format": {file_format}.' f' Known file formats: "csv", "xlsx".')
#         if file_format == "xlsx":
#             if importlib.util.find_spec("openpyxl") is None and importlib.util.find_spec("xlsxwriter") is None:
#                 raise ModuleNotFoundError(
#                     "You must install either openpyxl or xlsxwriter to export to xlsx format."
#                 )
#     return function

# Maybe in future build single dcc.Download component into page. Still need way of signifying
# that it should be the output component for export_data action - could do as @capture("action", download=True)
# or similar. Or special function argument def export_data(__download__=True). Treated like targets.
# Argument should not need to be provided manually by user though.
# Feels like CapturedActionCallable class gives most space for future expansion but it also more complex.
# Maybe do it this way for now, then add more actions, then come back to adding special behaviour so we can remove
# classes. At this point revisit whether each action should have separate model.
# THIS IS GOOD IDEA.
# So might as well put outputs back in opl for now.
