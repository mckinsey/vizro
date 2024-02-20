"""Pre-defined action function "export_data" to be reused in `action` parameter of VizroBaseModels."""

from typing import Any, Dict, List, Optional

from dash import ctx, dcc
from typing_extensions import Literal

from vizro.actions._actions_utils import _get_filtered_data
from vizro.managers import model_manager
from vizro.managers._model_manager import ModelID
from vizro.models.types import capture


@capture("action")
def export_data(
    targets: Optional[List[ModelID]] = None, file_format: Literal["csv", "xlsx"] = "csv", **inputs: Dict[str, Any]
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
    if not targets:
        targets = [
            output["id"]["target_id"]
            for output in ctx.outputs_list
            if isinstance(output["id"], dict) and output["id"]["type"] == "download_dataframe"
        ]
    for target in targets:
        if target not in model_manager:
            raise ValueError(f"Component '{target}' does not exist.")

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
        # Invalid file_format should be caught by Action validation

        outputs[f"download_dataframe_{target_id}"] = dcc.send_data_frame(
            writer=writer, filename=f"{target_id}.{file_format}", index=False
        )

    return outputs
