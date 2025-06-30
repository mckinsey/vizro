"""MCP server for Vizro-AI chart and dashboard creation."""

import mimetypes
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Optional

import vizro.models as vm
from mcp.server.fastmcp import FastMCP
from pydantic import Field, ValidationError
from vizro import Vizro

from vizro_mcp._schemas import (
    AgGridEnhanced,
    ChartPlan,
    GraphEnhanced,
)
from vizro_mcp._utils import (
    CHART_INSTRUCTIONS,
    GAPMINDER,
    IRIS,
    STOCKS,
    TIPS,
    DFInfo,
    DFMetaData,
    NoDefsGenerateJsonSchema,
    convert_github_url_to_raw,
    create_pycafe_url,
    get_chart_prompt,
    get_dashboard_instructions,
    get_dashboard_prompt,
    get_dataframe_info,
    get_python_code_and_preview_link,
    get_starter_dashboard_prompt,
    load_dataframe_by_format,
    path_or_url_check,
)


@dataclass
class ValidateResults:
    """Results of validation tools."""

    valid: bool
    message: str
    python_code: str
    pycafe_url: Optional[str]
    browser_opened: bool


@dataclass
class DataAnalysisResults:
    """Results of the data analysis tool."""

    valid: bool
    message: str
    df_info: Optional[DFInfo]
    df_metadata: Optional[DFMetaData]


@dataclass
class ModelJsonSchemaResults:
    """Results of the get_model_json_schema tool."""

    model_name: str
    json_schema: dict[str, Any]
    additional_info: str


# TODO: check on https://github.com/modelcontextprotocol/python-sdk what new things are possible to do here
mcp = FastMCP(
    "MCP server to help create Vizro dashboards and charts.",
)


@mcp.tool()
def get_vizro_chart_or_dashboard_plan(
    user_plan: Literal["chart", "dashboard"],
    user_host: Literal["generic_host", "ide"],
    advanced_mode: bool = False,
) -> str:
    """Get instructions for creating a Vizro chart or dashboard. Call FIRST when asked to create Vizro things.

    Must be ALWAYS called FIRST with advanced_mode=False, then call again with advanced_mode=True
    if the JSON config does not suffice anymore.

    Args:
        user_plan: The type of Vizro thing the user wants to create
        user_host: The host the user is using, if "ide" you can use the IDE/editor to run python code
        advanced_mode: Only call if you need to use custom CSS, custom components or custom actions.
            No need to call this with advanced_mode=True if you need advanced charts, use `custom_charts` in
            the `validate_dashboard_config` tool instead.

    Returns:
        Instructions for creating a Vizro chart or dashboard
    """
    if user_plan == "chart":
        return CHART_INSTRUCTIONS
    elif user_plan == "dashboard":
        return f"{get_dashboard_instructions(advanced_mode, user_host)}"


@mcp.tool()
def get_model_json_schema(model_name: str) -> ModelJsonSchemaResults:
    """Get the JSON schema for the specified Vizro model.

    Args:
        model_name: Name of the Vizro model to get schema for (e.g., 'Card', 'Dashboard', 'Page')

    Returns:
        JSON schema of the requested Vizro model
    """
    modified_models = {
        "Graph": GraphEnhanced,
        "AgGrid": AgGridEnhanced,
        "Table": AgGridEnhanced,
    }

    if model_name in modified_models:
        return ModelJsonSchemaResults(
            model_name=model_name,
            json_schema=modified_models[model_name].model_json_schema(schema_generator=NoDefsGenerateJsonSchema),
            additional_info="""LLM must remember to replace `$ref` with the actual config. Request the schema of
that model if necessary. Do NOT forget to call `validate_dashboard_config` after each iteration.""",
        )

    if not hasattr(vm, model_name):
        return ModelJsonSchemaResults(
            model_name=model_name,
            json_schema={},
            additional_info=f"Model '{model_name}' not found in vizro.models",
        )

    model_class = getattr(vm, model_name)
    return ModelJsonSchemaResults(
        model_name=model_name,
        json_schema=model_class.model_json_schema(schema_generator=NoDefsGenerateJsonSchema),
        additional_info="""LLM must remember to replace `$ref` with the actual config. Request the schema of
that model if necessary. Do NOT forget to call `validate_dashboard_config` after each iteration.""",
    )


@mcp.tool()
def get_sample_data_info(data_name: Literal["iris", "tips", "stocks", "gapminder"]) -> DFMetaData:
    """If user provides no data, use this tool to get sample data information.

    Use the following data for the below purposes:
        - iris: mostly numerical with one categorical column, good for scatter, histogram, boxplot, etc.
        - tips: contains mix of numerical and categorical columns, good for bar, pie, etc.
        - stocks: stock prices, good for line, scatter, generally things that change over time
        - gapminder: demographic data, good for line, scatter, generally things with maps or many categories

    Args:
        data_name: Name of the dataset to get sample data for

    Returns:
        Data info object containing information about the dataset.
    """
    if data_name == "iris":
        return IRIS
    elif data_name == "tips":
        return TIPS
    elif data_name == "stocks":
        return STOCKS
    elif data_name == "gapminder":
        return GAPMINDER


@mcp.tool()
def load_and_analyze_data(path_or_url: str) -> DataAnalysisResults:
    """Use to understand local or remote data files. Must be called with absolute paths or URLs.

    Supported formats:
    - CSV (.csv)
    - JSON (.json)
    - HTML (.html, .htm)
    - Excel (.xls, .xlsx)
    - OpenDocument Spreadsheet (.ods)
    - Parquet (.parquet)

    Args:
        path_or_url: Absolute (important!) local file path or URL to a data file

    Returns:
        DataAnalysisResults object containing DataFrame information and metadata
    """
    # Handle files and URLs
    path_or_url_type = path_or_url_check(path_or_url)
    mime_type, _ = mimetypes.guess_type(str(path_or_url))
    processed_path_or_url = path_or_url

    if path_or_url_type == "remote":
        processed_path_or_url = convert_github_url_to_raw(path_or_url)
    elif path_or_url_type == "local":
        processed_path_or_url = Path(path_or_url)
    else:
        return DataAnalysisResults(valid=False, message="Invalid path or URL", df_info=None, df_metadata=None)

    try:
        df, read_fn = load_dataframe_by_format(processed_path_or_url, mime_type)

    except Exception as e:
        return DataAnalysisResults(
            valid=False,
            message=f"""Failed to load data: {e!s}. Remember to use the ABSOLUTE path or URL!
Alternatively, you can use any data analysis means available to you. Most important information are the column names and
column types for passing along to the `validate_dashboard_config` or `validate_chart_code` tools.""",
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

    return DataAnalysisResults(valid=True, message="Data loaded successfully", df_info=df_info, df_metadata=df_metadata)


# TODO: Additional things we could validate:
# - data_infos: check we are referring to the correct dataframe, or at least A DF
@mcp.tool()
def validate_dashboard_config(
    dashboard_config: dict[str, Any],
    data_infos: list[DFMetaData],
    custom_charts: list[ChartPlan],
    auto_open: bool = True,
) -> ValidateResults:
    """Validate Vizro model configuration. Run ALWAYS when you have a complete dashboard configuration.

    If successful, the tool will return the python code and, if it is a remote file, the py.cafe link to the chart.
    The PyCafe link will be automatically opened in your default browser if auto_open is True.

    Args:
        dashboard_config: Either a JSON string or a dictionary representing a Vizro dashboard model configuration
        data_infos: List of DFMetaData objects containing information about the data files
        custom_charts: List of ChartPlan objects containing information about the custom charts in the dashboard
        auto_open: Whether to automatically open the PyCafe link in a browser

    Returns:
        ValidationResults object with status and dashboard details
    """
    Vizro._reset()

    try:
        dashboard = vm.Dashboard.model_validate(
            dashboard_config,
            context={"allow_undefined_captured_callable": [custom_chart.chart_name for custom_chart in custom_charts]},
        )
    except ValidationError as e:
        return ValidateResults(
            valid=False,
            message=f"""Validation Error: {e!s}. Fix the error and call this tool again.
Calling `get_model_json_schema` may help.""",
            python_code="",
            pycafe_url=None,
            browser_opened=False,
        )

    else:
        code_link = get_python_code_and_preview_link(dashboard, data_infos, custom_charts)

        pycafe_url = code_link.pycafe_url if all(info.file_location_type == "remote" for info in data_infos) else None
        browser_opened = False

        if pycafe_url and auto_open:
            try:
                browser_opened = webbrowser.open(pycafe_url)
            except Exception:
                browser_opened = False

        return ValidateResults(
            valid=True,
            message="""Configuration is valid for Dashboard! Do not forget to call this tool again after each iteration.
If you are creating an `app.py` file, you MUST use the code from the validation tool, do not modify it, watch out for
differences to previous `app.py`""",
            python_code=code_link.python_code,
            pycafe_url=pycafe_url,
            browser_opened=browser_opened,
        )

    finally:
        Vizro._reset()


@mcp.prompt()
def create_starter_dashboard():
    """Prompt template for getting started with Vizro."""
    return get_starter_dashboard_prompt()


@mcp.prompt()
def create_dashboard(
    file_path_or_url: str = Field(description="The absolute path or URL to the data file you want to use."),
    context: Optional[str] = Field(default=None, description="(Optional) Describe the dashboard you want to create."),
) -> str:
    """Prompt template for creating an EDA dashboard based on one dataset."""
    return get_dashboard_prompt(file_path_or_url, context)


@mcp.tool()
def validate_chart_code(
    chart_config: ChartPlan,
    data_info: DFMetaData,
    auto_open: bool = True,
) -> ValidateResults:
    """Validate the chart code created by the user and optionally open the PyCafe link in a browser.

    Args:
        chart_config: A ChartPlan object with the chart configuration
        data_info: Metadata for the dataset to be used in the chart
        auto_open: Whether to automatically open the PyCafe link in a browser

    Returns:
        ValidationResults object with status and dashboard details
    """
    Vizro._reset()

    try:
        chart_plan_obj = ChartPlan.model_validate(chart_config)
    except ValidationError as e:
        return ValidateResults(
            valid=False,
            message=f"Validation Error: {e!s}",
            python_code="",
            pycafe_url=None,
            browser_opened=False,
        )
    else:
        dashboard_code = chart_plan_obj.get_dashboard_template(data_info=data_info)

        # Generate PyCafe URL if all data is remote
        pycafe_url = create_pycafe_url(dashboard_code) if data_info.file_location_type == "remote" else None
        browser_opened = False

        if auto_open and pycafe_url:
            try:
                browser_opened = webbrowser.open(pycafe_url)
            except Exception:
                browser_opened = False

        return ValidateResults(
            valid=True,
            message="Chart only dashboard created successfully!",
            python_code=chart_plan_obj.get_chart_code(vizro=True),
            pycafe_url=pycafe_url,
            browser_opened=browser_opened,
        )

    finally:
        Vizro._reset()


@mcp.prompt()
def create_vizro_chart(
    file_path_or_url: str = Field(description="The absolute path or URL to the data file you want to use."),
    context: Optional[str] = Field(default=None, description="(Optional) Describe the chart you want to create."),
) -> str:
    """Prompt template for creating a Vizro chart."""
    return get_chart_prompt(file_path_or_url, context)
