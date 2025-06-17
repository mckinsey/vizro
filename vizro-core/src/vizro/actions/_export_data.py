import importlib.util
from collections.abc import Iterable
from typing import Any, Literal, cast

from dash import Output, ctx, dcc
from pydantic import Field

from vizro.actions._abstract_action import _AbstractAction
from vizro.actions._actions_utils import _apply_filters, _get_unfiltered_data
from vizro.managers import model_manager
from vizro.managers._model_manager import FIGURE_MODELS
from vizro.models._models_utils import _log_call
from vizro.models.types import FigureType, ModelID, _Controls


class export_data(_AbstractAction):
    """Exports visible data of target charts/components.

    Args:
        targets (list[ModelID]): List of target component ids to download data from. If none are given then download
             from all components on the page.
        file_format (Literal["csv", "xlsx"]): Format of downloaded files. Defaults to `csv`.
    """

    type: Literal["export_data"] = "export_data"
    targets: list[ModelID] = Field(
        default=[],
        description="List of target component ids to download data from. If none are given then download"
        "from all components on the page.",
    )
    file_format: Literal["csv", "xlsx"] = Field(
        default="csv", description="Format of downloaded files. Defaults to `csv`."
    )

    @_log_call
    def pre_build(self):
        # Set targets to all figures on the page if not already set. In this case we don't need to check the targets
        # are valid.
        # TODO-AV2 A 4: work out where this duplicated get_all_targets_on_page logic should live. Do we even want to
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

        if (
            self.file_format == "xlsx"
            and importlib.util.find_spec("openpyxl") is None
            and importlib.util.find_spec("xlsxwriter") is None
        ):
            raise ModuleNotFoundError("You must install either openpyxl or xlsxwriter to export to xlsx format.")

    def function(self, _controls: _Controls) -> dict[str, Any]:
        """Exports data after applying _controls."""
        # TODO-AV2 A 1: _controls is not currently used but instead taken out of the Dash context. This
        # will change in future once the structure of _controls has been worked out and we know how to pass ids through.
        # See https://github.com/mckinsey/vizro/pull/880
        ctds = ctx.args_grouping["external"]["_controls"]
        writers = {"csv": "to_csv", "xlsx": "to_excel"}
        outputs = {}

        for target, unfiltered_data in _get_unfiltered_data(ctds["parameters"], self.targets).items():
            filtered_data = _apply_filters(unfiltered_data, ctds["filters"], ctds["filter_interaction"], target)
            writer = getattr(filtered_data, writers[self.file_format])
            outputs[f"download_dataframe_{target}"] = dcc.send_data_frame(
                writer=writer, filename=f"{target}.{self.file_format}", index=False
            )

        return outputs

    # TODO-AV2 D 4: We need to override transformed_outputs to supply a dictionary ID but in future will probably change
    #  to use a single built-in vizro_download component. See
    #  https://github.com/mckinsey/vizro/pull/1054#discussion_r1989405177.
    @property
    def _transformed_outputs(self) -> dict[str, Output]:
        return {
            f"download_dataframe_{target}": Output(
                component_id={"type": "download_dataframe", "action_id": self.id, "target_id": target},
                component_property="data",
            )
            for target in self.targets
        }

    # This must be defined even though it's not used anywhere (since we define transformed_outputs) since it's an
    # abstractmethod.
    @property
    def outputs(self):  # type: ignore[override]
        pass

    @property
    def _dash_components(self) -> list[dcc.Download]:
        return [
            dcc.Download(id={"type": "download_dataframe", "action_id": self.id, "target_id": target})
            for target in self.targets
        ]
