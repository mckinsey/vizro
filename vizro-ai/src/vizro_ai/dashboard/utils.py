"""Helper Functions For Vizro AI dashboard."""

from dataclasses import dataclass
from typing import Any, Optional, Union

import pandas as pd
import tqdm.std as tsd
import vizro.models as vm
from pydantic import BaseModel, ConfigDict


class DfMetadata(BaseModel):
    """Pydantic model containing metadata content for a dataframe."""

    df_schema: dict[str, str]
    df: pd.DataFrame
    df_sample: pd.DataFrame

    model_config = ConfigDict(arbitrary_types_allowed=True)


class AllDfMetadata(BaseModel):
    """Pydantic model containing metadata for all dataframes."""

    all_df_metadata: dict[str, DfMetadata] = {}

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def get_schemas_and_samples(self) -> dict[str, dict[str, str]]:
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

    def get_df_schema(self, name: str) -> dict[str, str]:
        """Retrieve the schema of the dataframe by name."""
        return self.all_df_metadata[name].df_schema


@dataclass
class DashboardOutputs:
    """Dataclass containing all possible `VizroAI.dashboard()` output."""

    dashboard: vm.Dashboard
    code: str


@dataclass
class ComponentResult:
    """Dataclass containing the result of a component creation."""

    component: Union[vm.Card, vm.AgGrid, vm.Figure]
    imports: Optional[str] = None
    code: Optional[str] = None


def _execute_step(pbar: tsd.tqdm, description: str, value: Any) -> Any:
    pbar.update(1)
    pbar.set_description_str(description)
    return value


def _register_data(all_df_metadata: AllDfMetadata) -> vm.Dashboard:
    """Register the dashboard data in data manager."""
    from vizro.managers import data_manager

    for name, metadata in all_df_metadata.all_df_metadata.items():
        data_manager[name] = metadata.df


def _extract_overall_imports_and_code(
    custom_charts_code: list[list[dict[str, str]]], custom_charts_imports: list[list[dict[str, str]]]
) -> tuple[set[str], set[str]]:
    """Extract custom functions and imports from the custom charts code.

    Args:
        custom_charts_code: A list of lists of dictionaries, where each dictionary
            contains the custom chart code for a component.
            The outer list represents pages, the inner list represents
            components on a page, and the dictionary maps component IDs to their code.
        custom_charts_imports: A list of lists of dictionaries, where each dictionary
            contains the custom chart imports for a component.
            The outer list represents pages, the inner list represents
            components on a page, and the dictionary maps component IDs to their imports.

    Returns:
        A tuple containing:
        - A set of custom function code snippets
        - A set of import statements

    """
    custom_functions = {
        code
        for page_components in custom_charts_code
        for component_code in page_components
        for code in component_code.values()
    }
    imports = {
        component_imports
        for page_components in custom_charts_imports
        for component_code in page_components
        for component_imports in component_code.values()
    }

    return custom_functions, imports
