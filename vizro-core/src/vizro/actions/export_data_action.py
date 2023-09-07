"""Pre-defined action function "export_data" to be re-used in `action` parameter of VizroBaseModels."""

from typing import Any, Dict, List, Optional

from dash import ctx, dcc
from typing_extensions import Literal

from vizro.actions._actions_utils import (
    _get_filtered_data,
)
from vizro.managers import model_manager
from vizro.models.types import capture


@capture("action")
def export_data(
    targets: Optional[List[str]] = None,
    file_format: Literal["csv", "xlsx"] = "csv",
    **inputs: Dict[str, Any],
) -> Dict[str, Any]:
    """Exports visible data of target charts/components on page after being triggered.

    Args:
        targets: List of target component ids to download data from. Defaults to None.
        file_format: Format of downloaded files. Defaults to `csv`.
        inputs: Dict mapping action function names with their inputs e.g.
            inputs = {'filters': [], 'parameters': ['gdpPercap'], 'filter_interaction': [], 'theme_selector': True}

    Raises:
        ValueError: If unknown file extension is provided.
        ValueError: If target component does not exist on page.

    Returns:
        Dict mapping target component id to modified charts/components e.g. {'my_scatter': Figure({})}
    """
    if targets is None:
        targets = [
            output["id"]["target_id"]
            for output in ctx.outputs_list
            if isinstance(output["id"], dict) and output["id"]["type"] == "download-dataframe"
        ]
    for target in targets:
        if target not in model_manager:  # type: ignore[operator]
            raise ValueError(f"Component '{target}' does not exist.")

    data_frames = _get_filtered_data(
        targets=targets,
        ctds_filters=ctx.args_grouping["filters"],
        ctds_filter_interaction=ctx.args_grouping["filter_interaction"],
    )

    callback_outputs = {}
    for _, target_id in enumerate(targets):
        if file_format == "csv":
            writer = data_frames[target_id].to_csv
        elif file_format == "xlsx":
            writer = data_frames[target_id].to_excel
        else:
            raise ValueError(f'Unknown "file_format": {file_format}.' f' Known file formats: "csv", "xlsx".')

        callback_outputs[f"download-dataframe_{target_id}"] = dcc.send_data_frame(
            writer=writer, filename=f"{target_id}.{file_format}", index=False
        )

    return callback_outputs
