"""Helper Functions For Vizro AI dashboard."""

from dataclasses import dataclass, field

# import black
from typing import Any, Dict

import pandas as pd
import tqdm.std as tsd
import vizro.models as vm

IMPORT_STATEMENTS = (
    "import vizro.plotly.express as px\n"
    "from vizro.models.types import capture\n"
    "import plotly.graph_objects as go\n"
    "from vizro.tables import dash_ag_grid\n"
    "from vizro.models import AgGrid, Card, Dashboard, Filter, Layout, Page, Graph\n"
    "from vizro.managers import data_manager\n"
    "from vizro import Vizro\n"
    "import pandas as pd\n"
)


@dataclass
class MetadataContent:
    """Dataclass containing metadata content for a dataframe."""

    df_schema: Dict[str, str]
    df: pd.DataFrame
    df_sample: pd.DataFrame


@dataclass
class DfMetadata:
    """Dataclass containing metadata for all dataframes."""

    metadata: Dict[str, MetadataContent] = field(default_factory=dict)

    def get_schemas_and_samples(self) -> Dict[str, Dict[str, str]]:
        """Retrieve only the df_schema and df_sample for all datasets."""
        return {
            name: {"df_schema": metadata.df_schema, "df_sample": metadata.df_sample}
            for name, metadata in self.metadata.items()
        }

    def get_df(self, name: str) -> pd.DataFrame:
        """Retrieve the dataframe by name."""
        return self.metadata[name].df

    def get_df_schema(self, name: str) -> Dict[str, str]:
        """Retrieve the schema of the dataframe by name."""
        return self.metadata[name].df_schema


@dataclass
class DashboardOutputs:
    """Dataclass containing all possible `VizroAI.dashboard()` output."""

    code: str
    dashboard: vm.Dashboard
    metadata: DfMetadata


def _execute_step(pbar: tsd.tqdm, description: str, value: Any) -> Any:
    pbar.update(1)
    pbar.set_description_str(description)
    return value


def _dashboard_code(dashboard: vm.Dashboard) -> str:
    """Generate dashboard code from dashboard object."""
    dashboard_code_str = IMPORT_STATEMENTS + repr(dashboard)

    # TODO: use black or ruff to format the code
    # formatted_code = black.format_str(dashboard_code_str, mode=black.Mode())
    return dashboard_code_str


def _run_dashboard(dashboard: vm.Dashboard, df_metadata: DfMetadata) -> None:
    """Run the dashboard."""
    from vizro import Vizro
    from vizro.managers import data_manager

    for name, metadata in df_metadata.metadata.items():
        data_manager[name] = metadata.df

    Vizro().build(dashboard).run()
