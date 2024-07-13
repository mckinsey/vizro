"""Helper Functions For Vizro AI dashboard."""

from dataclasses import dataclass, field

# import black
from typing import Any, Dict

import pandas as pd
import tqdm.std
import vizro.models as vm

IMPORT_STATEMENTS = (
    "import vizro.plotly.express as px\n"
    "from vizro.models.types import capture\n"
    "import plotly.graph_objects as go\n"
    "from vizro.tables import dash_ag_grid\n"
    "import vizro.models as vm\n"
)


@dataclass
class DataFrameMetadata:
    """Dataclass containing metadata for a dataframe."""

    df_schema: Dict[str, str]
    df: pd.DataFrame
    df_sample: str


@dataclass
class DfMetadata:
    """Dataclass containing metadata for all dataframes."""

    metadata: Dict[str, DataFrameMetadata] = field(default_factory=dict)


@dataclass
class DashboardOutputs:
    """Dataclass containing all possible `VizroAI.dashboard()` output."""

    code: str
    dashboard: vm.Dashboard


def _execute_step(pbar: tqdm.std.tqdm, description: str, value: Any) -> Any:
    pbar.set_description_str(description)
    pbar.update(1)
    return value


def _dashboard_code(dashboard: vm.Dashboard) -> str:
    """Generate dashboard code from dashboard object."""
    dashboard_code_str = IMPORT_STATEMENTS + repr(dashboard)

    # TODO: use black or ruff to format the code
    # formatted_code = black.format_str(dashboard_code_str, mode=black.Mode())
    return dashboard_code_str
