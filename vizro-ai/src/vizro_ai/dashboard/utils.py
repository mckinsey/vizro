"""Helper Functions For Vizro AI dashboard."""

from dataclasses import dataclass, field

# import black
from typing import Any, Dict

import pandas as pd
import tqdm.std
import vizro.models as vm
from vizro_ai.dashboard.constants import IMPORT_STATEMENTS


@dataclass
class MetadataContent:
    """Dataclass containing metadata content for a dataframe."""

    df_schema: Dict[str, str]
    df: pd.DataFrame
    df_sample: str


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


def _execute_step(pbar: tqdm.std.tqdm, description: str, value: Any) -> Any:
    pbar.update(1)
    pbar.set_description_str(description)
    return value


def _dashboard_code(dashboard: vm.Dashboard) -> str:
    """Generate dashboard code from dashboard object."""
    dashboard_code_str = IMPORT_STATEMENTS + repr(dashboard)

    # TODO: use black or ruff to format the code
    # formatted_code = black.format_str(dashboard_code_str, mode=black.Mode())
    return dashboard_code_str
