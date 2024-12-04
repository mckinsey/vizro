"""Pre-defined action function "export_data" to be reused in `action` parameter of VizroBaseModels."""

from typing import Any, Optional

from dash import ctx, dcc
from typing_extensions import Literal

from vizro.actions._actions_utils import _apply_filters, _get_unfiltered_data
from vizro.managers import model_manager
from vizro.managers._model_manager import ModelID
from vizro.models.types import capture


@capture("action")
def export_data(
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
