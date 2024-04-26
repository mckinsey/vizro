import importlib
from typing import Any, Dict, List, Literal

from dash import Output, ctx, dcc

from vizro.managers import model_manager
from vizro.models.types import CapturedActionCallable


class ExportDataAction(CapturedActionCallable):

    # TODO-AV2: Maybe we can rename it to '_validation' or similar.
    def _post_init(self):
        """Post initialization is called in the vm.Action build phase, and it is used to validate and calculate the
        properties of the CapturedActionCallable. With this, we can validate the properties and raise errors before
        the action is built. Also, "input"/"output"/"components" properties and "pure_function" can use these validated
        and the calculated arguments.
        """
        self._page_id = model_manager._get_model_page_id(model_id=self._action_id)

        # Validate and calculate "targets"
        # TODO-AV2-TICKET-NEW-*: Make targets validation reusable for the other actions (maybe even for Filter model).
        # TODO-AV2-OQ: Rethink using self._arguments
        targets = self._arguments.get("targets")
        if targets:
            for target in targets:
                if self._page_id != model_manager._get_model_page_id(model_id=target):
                    # TODO-AV2-TICKET-NEW-*: Improve error message to explain in which action the error occurs.
                    raise ValueError(f"Component '{target}' does not exist on the page '{self._page_id}'.")
        else:
            targets = model_manager._get_page_model_ids_with_figure(page_id=self._page_id)
        self._arguments["targets"] = self.targets = targets

        # Validate and calculate "file_format"
        file_format = self._arguments.get("file_format", "csv")
        if file_format not in ["csv", "xlsx"]:
            raise ValueError(f'Unknown "file_format": {file_format}.' f' Known file formats: "csv", "xlsx".')
        if file_format == "xlsx":
            if importlib.util.find_spec("openpyxl") is None and importlib.util.find_spec("xlsxwriter") is None:
                raise ModuleNotFoundError("You must install either openpyxl or xlsxwriter to export to xlsx format.")

    @staticmethod
    def pure_function(
        targets: List[str], file_format: Literal["csv", "xlsx"] = "csv", **inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Exports visible data of target charts/components on page after being triggered.

        Args:
            targets: List of target component ids to download data from. Defaults to `None`.
            file_format: Format of downloaded files. Defaults to `csv`.
            inputs: Dict mapping action function names with their inputs e.g.
                inputs = {'filters': [], 'parameters': ['gdpPercap'], 'filter_interaction': [], 'theme_selector': True}

        Raises:
            ValueError: If unknown file extension is provided.
            ValueError: If target component does not exist on page.

        Returns:
            Dict mapping target component id to modified charts/components e.g. {'my_scatter': Figure({})}

        """
        from vizro.actions._actions_utils import _get_filtered_data

        data_frames = _get_filtered_data(
            targets=targets,
            ctds_filters=ctx.args_grouping["external"]["filters"],
            ctds_filter_interaction=ctx.args_grouping["external"]["filter_interaction"],
        )

        outputs = {}
        for target_id in targets:
            if file_format == "csv":
                writer = data_frames[target_id].to_csv
            elif file_format == "xlsx":
                writer = data_frames[target_id].to_excel

            outputs[f"download_dataframe_{target_id}"] = dcc.send_data_frame(
                writer=writer, filename=f"{target_id}.{file_format}", index=False
            )

        return outputs

    @property
    def inputs(self):
        from vizro.actions import filter_action, filter_interaction
        from vizro.actions._callback_mapping._callback_mapping_utils import (
            _get_inputs_of_figure_interactions,
            _get_inputs_of_filters,
        )

        page = model_manager[self._page_id]
        return {
            "filters": _get_inputs_of_filters(page=page, action_class=filter_action),
            "filter_interaction": _get_inputs_of_figure_interactions(page=page, action_class=filter_interaction),
        }

    @property
    def outputs(self) -> Dict[str, Output]:
        # TODO-AV2-TICKET-CREATED: Take the "actions_info" into account once it's implemented.
        return {
            f"download_dataframe_{target}": Output(
                component_id={"type": "download_dataframe", "action_id": self._action_id, "target_id": target},
                component_property="data",
            )
            for target in self.targets
        }

    @property
    def components(self):
        # TODO-AV2-TICKET-CREATED: Take the "actions_info" into account once it's implemented.
        return [
            dcc.Download(id={"type": "download_dataframe", "action_id": self._action_id, "target_id": target})
            for target in self.targets
        ]


# Alias for ExportDataAction
export_data = ExportDataAction
