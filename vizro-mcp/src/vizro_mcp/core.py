"""Core functionality for Vizro MCP - independent of MCP framework.

This module provides the core validation and utility functions that can be used
as a standalone library without requiring the MCP server framework.

Example usage:
    from vizro_mcp import validate_dashboard, validate_chart, load_data

    # Validate a dashboard configuration
    result = validate_dashboard(
        dashboard_config={...},
        data_infos=[...],
        custom_charts=[...]
    )

    # Load and analyze data
    result = load_data("/path/to/data.csv")
"""

import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import vizro
import vizro.models as vm
from pydantic import ValidationError
from vizro import Vizro

from vizro_mcp._schemas import (
    AgGridEnhanced,
    ChartPlan,
    FigureEnhanced,
    GraphEnhanced,
)
from vizro_mcp._utils import (
    GAPMINDER,
    IRIS,
    LAYOUT_INSTRUCTIONS,
    STOCKS,
    TIPS,
    DFInfo,
    DFMetaData,
    NoDefsGenerateJsonSchema,
    convert_github_url_to_raw,
    create_pycafe_url,
    get_dataframe_info,
    get_python_code_and_preview_link,
    load_dataframe_by_format,
    path_or_url_check,
)


# Result dataclasses
@dataclass
class ValidationResult:
    """Result of validation operations."""

    valid: bool
    message: str
    python_code: str
    pycafe_url: str | None


@dataclass
class DataAnalysisResult:
    """Result of data analysis operations."""

    valid: bool
    message: str
    df_info: DFInfo | None
    df_metadata: DFMetaData | None


@dataclass
class ModelSchemaResult:
    """Result of model schema operations."""

    model_name: str
    json_schema: dict[str, Any]
    additional_info: str


# Sample data mapping
SAMPLE_DATA = {
    "iris": IRIS,
    "tips": TIPS,
    "stocks": STOCKS,
    "gapminder": GAPMINDER,
}


def validate_dashboard(
    dashboard_config: dict[str, Any],
    data_infos: list[DFMetaData],
    custom_charts: list[ChartPlan] | None = None,
) -> ValidationResult:
    """Validate a Vizro dashboard configuration.

    This function validates the dashboard configuration against Vizro's schema
    and generates the Python code and PyCafe preview URL.

    Args:
        dashboard_config: Dictionary representing a Vizro dashboard model configuration.
        data_infos: List of DFMetaData objects containing information about the data files.
        custom_charts: List of ChartPlan objects for custom chart definitions.

    Returns:
        ValidationResult with validation status, generated Python code, and preview URL.

    Example:
        >>> from vizro_mcp import validate_dashboard, DFMetaData
        >>> data_info = DFMetaData(
        ...     file_name="my_data",
        ...     file_path_or_url="https://example.com/data.csv",
        ...     file_location_type="remote",
        ...     read_function_string="pd.read_csv",
        ... )
        >>> config = {
        ...     "pages": [
        ...         {
        ...             "title": "My Page",
        ...             "components": [
        ...                 {
        ...                     "type": "graph",
        ...                     "figure": {"_target_": "scatter", "data_frame": "my_data", "x": "col1", "y": "col2"},
        ...                 }
        ...             ],
        ...         }
        ...     ]
        ... }
        >>> result = validate_dashboard(config, [data_info])
        >>> print(result.valid)
        True
    """
    if custom_charts is None:
        custom_charts = []

    Vizro._reset()

    try:
        dashboard = vm.Dashboard.model_validate(
            dashboard_config,
            context={"allow_undefined_captured_callable": [custom_chart.chart_name for custom_chart in custom_charts]},
        )
    except ValidationError as e:
        return ValidationResult(
            valid=False,
            message=f"Validation Error: {e!s}. Fix the error and try again. "
            "Use get_model_schema() to check the expected schema.",
            python_code="",
            pycafe_url=None,
        )
    else:
        code_link = get_python_code_and_preview_link(dashboard, data_infos, custom_charts)
        pycafe_url = code_link.pycafe_url if all(info.file_location_type == "remote" for info in data_infos) else None

        return ValidationResult(
            valid=True,
            message="Configuration is valid for Dashboard!",
            python_code=code_link.python_code,
            pycafe_url=pycafe_url,
        )
    finally:
        Vizro._reset()


def validate_chart(
    chart_config: ChartPlan | dict[str, Any],
    data_info: DFMetaData,
) -> ValidationResult:
    """Validate chart code and generate dashboard template.

    Args:
        chart_config: A ChartPlan object or dictionary with the chart configuration.
        data_info: Metadata for the dataset to be used in the chart.

    Returns:
        ValidationResult with validation status, generated code, and preview URL.

    Example:
        >>> from vizro_mcp import validate_chart, ChartPlan, DFMetaData
        >>> chart = ChartPlan(
        ...     chart_type="scatter",
        ...     chart_name="my_scatter",
        ...     imports=["import plotly.express as px"],
        ...     chart_code='def my_scatter(data_frame):\\n    return px.scatter(data_frame, x="x", y="y")',
        ... )
        >>> data_info = DFMetaData(
        ...     file_name="my_data",
        ...     file_path_or_url="https://example.com/data.csv",
        ...     file_location_type="remote",
        ...     read_function_string="pd.read_csv",
        ... )
        >>> result = validate_chart(chart, data_info)
        >>> print(result.valid)
        True
    """
    Vizro._reset()

    try:
        if isinstance(chart_config, dict):
            chart_plan_obj = ChartPlan.model_validate(chart_config)
        else:
            chart_plan_obj = chart_config
    except ValidationError as e:
        return ValidationResult(
            valid=False,
            message=f"Validation Error: {e!s}",
            python_code="",
            pycafe_url=None,
        )
    else:
        dashboard_code = chart_plan_obj.get_dashboard_template(data_info=data_info)
        pycafe_url = create_pycafe_url(dashboard_code) if data_info.file_location_type == "remote" else None

        return ValidationResult(
            valid=True,
            message="Chart code validated successfully!",
            python_code=chart_plan_obj.get_chart_code(vizro=True),
            pycafe_url=pycafe_url,
        )
    finally:
        Vizro._reset()


def load_data(
    path_or_url: str,
) -> DataAnalysisResult:
    """Load and analyze data from a file path or URL.

    Supports CSV, JSON, HTML, Excel (.xls, .xlsx), OpenDocument Spreadsheet (.ods),
    and Parquet formats.

    Args:
        path_or_url: Absolute local file path or URL to a data file.

    Returns:
        DataAnalysisResult with DataFrame information and metadata.

    Example:
        >>> from vizro_mcp import load_data
        >>> result = load_data("https://raw.githubusercontent.com/plotly/datasets/master/iris-id.csv")
        >>> print(result.valid)
        True
        >>> print(result.df_metadata.file_name)
        iris-id
    """
    path_or_url_type = path_or_url_check(path_or_url)
    mime_type, _ = mimetypes.guess_type(str(path_or_url))
    processed_path_or_url = path_or_url

    if path_or_url_type == "remote":
        processed_path_or_url = convert_github_url_to_raw(path_or_url)
    elif path_or_url_type == "local":
        processed_path_or_url = Path(path_or_url)
    else:
        return DataAnalysisResult(valid=False, message="Invalid path or URL", df_info=None, df_metadata=None)

    try:
        df, read_fn = load_dataframe_by_format(processed_path_or_url, mime_type)
    except Exception as e:
        return DataAnalysisResult(
            valid=False,
            message=f"Failed to load data: {e!s}. Ensure you're using an absolute path or valid URL.",
            df_info=None,
            df_metadata=None,
        )

    df_info = get_dataframe_info(df)
    df_metadata = DFMetaData(
        file_name=Path(path_or_url).stem if isinstance(processed_path_or_url, Path) else Path(path_or_url).name,
        file_path_or_url=str(processed_path_or_url),
        file_location_type=path_or_url_type,
        read_function_string=read_fn,
    )

    return DataAnalysisResult(valid=True, message="Data loaded successfully", df_info=df_info, df_metadata=df_metadata)


def get_model_schema(
    model_name: str,
) -> ModelSchemaResult:
    """Get the JSON schema for a Vizro model.

    Args:
        model_name: Name of the Vizro model (e.g., 'Card', 'Dashboard', 'Page', 'Graph').

    Returns:
        ModelSchemaResult with the JSON schema and additional information.

    Example:
        >>> from vizro_mcp import get_model_schema
        >>> result = get_model_schema("Graph")
        >>> print(result.model_name)
        Graph
    """
    if not hasattr(vm, model_name):
        return ModelSchemaResult(
            model_name=model_name,
            json_schema={},
            additional_info=f"Model '{model_name}' not found in vizro.models",
        )

    modified_models = {
        "Graph": GraphEnhanced,
        "AgGrid": AgGridEnhanced,
        "Table": AgGridEnhanced,
        "Figure": FigureEnhanced,
    }

    if model_name in modified_models:
        return ModelSchemaResult(
            model_name=model_name,
            json_schema=modified_models[model_name].model_json_schema(schema_generator=NoDefsGenerateJsonSchema),
            additional_info="Remember to replace `$ref` with the actual config. "
            "Request the schema of that model if necessary.",
        )

    deprecated_models = {"filter_interaction": "set_control", "Layout": "Grid"}
    if model_name in deprecated_models:
        return ModelSchemaResult(
            model_name=model_name,
            json_schema={},
            additional_info=f"Model '{model_name}' is deprecated. Use {deprecated_models[model_name]} instead.",
        )

    model_class = getattr(vm, model_name)
    if model_name in {"Grid", "Flex"}:
        return ModelSchemaResult(
            model_name=model_name,
            json_schema=model_class.model_json_schema(schema_generator=NoDefsGenerateJsonSchema),
            additional_info=LAYOUT_INSTRUCTIONS,
        )

    return ModelSchemaResult(
        model_name=model_name,
        json_schema=model_class.model_json_schema(schema_generator=NoDefsGenerateJsonSchema),
        additional_info="Remember to replace `$ref` with the actual config. "
        "Request the schema of that model if necessary.",
    )


def get_sample_data(
    data_name: Literal["iris", "tips", "stocks", "gapminder"],
) -> DFMetaData:
    """Get metadata for a sample dataset.

    Available datasets:
        - iris: Numerical data with one categorical column, good for scatter, histogram, boxplot.
        - tips: Mix of numerical and categorical columns, good for bar, pie charts.
        - stocks: Stock prices over time, good for line, time series charts.
        - gapminder: Demographic data, good for maps and multi-category visualizations.

    Args:
        data_name: Name of the sample dataset.

    Returns:
        DFMetaData with information about the dataset.

    Example:
        >>> from vizro_mcp import get_sample_data
        >>> iris_data = get_sample_data("iris")
        >>> print(iris_data.file_name)
        iris_data
    """
    return SAMPLE_DATA[data_name]


def get_vizro_version() -> str:
    """Get the version of Vizro being used.

    Returns:
        The Vizro version string.
    """
    return vizro.__version__
