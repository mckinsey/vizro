"""Helper Functions For Vizro AI dashboard."""

from dataclasses import dataclass, field
from typing import Any, Dict

import pandas as pd
import tqdm.std as tsd
import vizro.models as vm


@dataclass
class DfMetadata:
    """Dataclass containing metadata content for a dataframe."""

    df_schema: Dict[str, str]
    df: pd.DataFrame
    df_sample: pd.DataFrame


@dataclass
class AllDfMetadata:
    """Dataclass containing metadata for all dataframes."""

    all_df_metadata: Dict[str, DfMetadata] = field(default_factory=dict)

    def get_schemas_and_samples(self) -> Dict[str, Dict[str, str]]:
        """Retrieve only the df_schema and df_sample for all datasets."""
        return {
            name: {"df_schema": metadata.df_schema, "df_sample": metadata.df_sample}
            for name, metadata in self.all_df_metadata.items()
        }

    def get_df(self, name: str) -> pd.DataFrame:
        """Retrieve the dataframe by name."""
        try:
            return self.all_df_metadata[name].df
        except KeyError:
            raise KeyError("Dataframe not found in metadata. Please ensure that the correct dataframe is provided.")

    def get_df_schema(self, name: str) -> Dict[str, str]:
        """Retrieve the schema of the dataframe by name."""
        return self.all_df_metadata[name].df_schema


@dataclass
class DashboardOutputs:
    """Dataclass containing all possible `VizroAI.dashboard()` output."""

    code: str
    dashboard: vm.Dashboard


def _execute_step(pbar: tsd.tqdm, description: str, value: Any) -> Any:
    pbar.update(1)
    pbar.set_description_str(description)
    return value


def _register_data(all_df_metadata: AllDfMetadata) -> vm.Dashboard:
    """Register the dashboard data in data manager."""
    from vizro.managers import data_manager

    for name, metadata in all_df_metadata.all_df_metadata.items():
        data_manager[name] = metadata.df


def _dashboard_code(dashboard: vm.Dashboard) -> str:
    """Generate dashboard code from dashboard object."""
    try:
        return dashboard.to_python()
    except AttributeError:
        return "Dashboard code generation is coming soon!"
