"""Helper Functions For Vizro AI dashboard."""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Union

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
    """Dataclass containing all possible `VizroAI._dashboard()` output."""

    dashboard: vm.Dashboard
    code: str


@dataclass
class ComponentResult:
    """Dataclass containing the result of a component creation."""

    component: Union[vm.Card, vm.AgGrid, vm.Figure]
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


def _extract_custom_functions_and_imports(custom_charts_code: List[List[Dict[str, str]]]) -> Tuple[Set[str], Set[str]]:
    """Extract custom functions and imports from the custom charts code.

    Args:
        custom_charts_code: A list of lists of dictionaries, where each dictionary
                                    contains the custom chart code for a component.
                                    The outer list represents pages, the inner list represents
                                    components on a page, and the dictionary maps component IDs to their code.

    Returns:
        A tuple containing:
        - A set of custom function code snippets
        - A set of import statements

    """
    custom_functions: Set[str] = set()
    imports: Set[str] = set()

    for page_components in custom_charts_code:
        for component_code in page_components:
            for code in component_code.values():
                # Extract imports
                import_match = re.match(r"((?:from|import).*?)\n\n", code, re.DOTALL)
                if import_match:
                    imports.add(import_match.group(1))

                # Remove leading imports and the last line (any chart creation)
                code_without_imports = code[import_match.end() :]
                code_without_chart_creation, _, _ = code_without_imports.rpartition("\n\n")

                custom_functions.add(code_without_chart_creation)

    return custom_functions, imports
