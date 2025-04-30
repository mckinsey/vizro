"""MCP server for Vizro-AI chart and dashboard creation."""

import json
import mimetypes
from pathlib import Path
from typing import Any, Literal, Optional

import vizro.models as vm
from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError
from vizro import Vizro

from vizro_mcp._schemas import (
    MODEL_GROUPS,
    AgGridEnhanced,
    ChartPlan,
    ContainerSimplified,
    DashboardSimplified,
    FilterSimplified,
    GraphEnhanced,
    PageSimplified,
    ParameterSimplified,
    TabsSimplified,
)
from vizro_mcp._utils import (
    GAPMINDER,
    IRIS,
    STOCKS,
    TIPS,
    convert_github_url_to_raw,
    data_info,
    get_dataframe_info,
    get_python_code_and_preview_link,
    load_dataframe_by_format,
    path_or_url_check,
)

# TODO: what do I need to do here, as things are already set up?
mcp = FastMCP(
    "MCP server to help create Vizro dashboards and charts.",
)


@mcp.tool()
def get_sample_data_info(data_name: Literal["iris", "tips", "stocks", "gapminder"]) -> data_info:
    """If user provides no data, use this tool to get sample data information.

    Use the following data for the below purposes:
        - iris: mostly numerical with one categorical column, good for scatter, histogram, boxplot, etc.
        - tips: contains mix of numerical and categorical columns, good for bar, pie, etc.
        - stocks: stock prices, good for line, scatter, generally things that change over time
        - gapminder: demographic data, good for line, scatter, generally things with maps or many categories

    Args:
        data_name: Name of the dataset to get sample data for

    Returns:
        Data info object containing information about the dataset
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
def validate_model_config(config: dict[str, Any], data_infos: Optional[list[data_info]] = None) -> dict[str, Any]:
    """Validate Vizro model configuration. Run ALWAYS when you have a complete dashboard configuration.

    If successful, the tool will return the python code and, if it is a remote file, the py.cafe link to the chart.

    Args:
        config: Either a JSON string or a dictionary representing a Vizro model configuration
        data_infos: List of data_info objects containing information about the data files

    Returns:
        Dictionary with validation status and details
    """
    if data_infos is None:
        data_infos = []

    Vizro._reset()

    try:
        dashboard = vm.Dashboard.model_validate(config)
    except ValidationError as e:
        return {"valid": False, "error": f"Validation Error: {e!s}"}

    else:
        result = get_python_code_and_preview_link(dashboard, data_infos)

        result = {
            "valid": True,
            "message": "Configuration is valid for Dashboard!",
            "python_code": result["python_code"],
            "pycafe_url": result["pycafe_url"]
            if all(info.file_location_type == "remote" for info in data_infos)
            else None,
        }

        return result

    finally:
        Vizro._reset()


@mcp.tool()
def get_model_json_schema(model_name: str) -> dict[str, Any]:
    """Get the JSON schema for the specified Vizro model.

    Args:
        model_name: Name of the Vizro model to get schema for (e.g., 'Card', 'Dashboard', 'Page')

    Returns:
        JSON schema of the requested Vizro model
    """
    if model_name == "Page":
        return PageSimplified.model_json_schema()
    elif model_name == "Dashboard":
        return DashboardSimplified.model_json_schema()
    elif model_name == "Graph":
        return GraphEnhanced.model_json_schema()
    elif model_name == "AgGrid":
        return AgGridEnhanced.model_json_schema()
    elif model_name == "Tabs":
        return TabsSimplified.model_json_schema()
    elif model_name == "Container":
        return ContainerSimplified.model_json_schema()
    elif model_name == "Filter":
        return FilterSimplified.model_json_schema()
    elif model_name == "Parameter":
        return ParameterSimplified.model_json_schema()
    # Get the model class from the vizro.models namespace
    if not hasattr(vm, model_name):
        return {"error": f"Model '{model_name}' not found in vizro.models"}

    model_class = getattr(vm, model_name)

    # Get the JSON schema from the model
    schema = model_class.model_json_schema()
    return schema


@mcp.tool()
def get_overview_vizro_models() -> dict[str, list[dict[str, str]]]:
    """Get all available models in the vizro.models namespace.

    Returns:
        Dictionary with categories of models and their descriptions
    """
    # Convert the model_groups dict to a dict with just names and descriptions
    result = {}
    for category, models_list in MODEL_GROUPS.items():
        result[category] = [
            {
                "name": model_class.__name__,
                "description": (model_class.__doc__ or "No description available").split("\n")[0],
            }
            for model_class in models_list
        ]

    return result


@mcp.tool()
def get_vizro_chart_or_dashboard_plan(plan: Literal["chart", "dashboard"]) -> str:
    """Get instructions for creating a Vizro chart or dashboard. Call FIRST when asked to create Vizro things."""
    if plan == "chart":
        return """
Instructions for creating a Vizro chart:
    - analyze the datasets needed for the chart using the load_and_analyze_data tool - the most important
        information here are the column names and column types
    - if the user provides no data, but you need to display a chart or table, use the get_sample_data_info
        tool to get sample data information
    - do NOT call any other tool after, especially do NOT create a dashboard
            """
    elif plan == "dashboard":
        return """
IMPORTANT:
    - if you iterate over a valid produced solution, make sure to go ALWAYS via the validation step again to
        ensure the solution is valid
    - DO NOT show any code or config to the user until you have validated the solution, do not say you are preparing
        a solution, just do it and validate it
    - if you find yourself repeatedly getting something wrong, try enquiring the schema of the component in question

Instructions for creating a Vizro dashboard:
    - analyze the datasets needed for the dashboard using the load_and_analyze_data tool - the most
        important information here are the column names and column types
    - if the user provides no data, but you need to display a chart or table, use the get_sample_data_info
        tool to get sample data information
    - call the get_overview_vizro_models tool to get an overview of the available models
    - make a plan of what components you would like to use, then request all necessary schemas
        using the get_model_json_schema tool
    - assemble your components into a page, then add the page or pages to a dashboard, DO NOT show config or code
        to the user until you have validated the solution
    - ALWAYS validate the dashboard configuration using the validate_model_config tool
    - if you display any code artifact, you must use the above created code, do not add new config to it


    """


@mcp.tool()
def load_and_analyze_data(path_or_url: str) -> dict[str, Any]:
    """Load data from various file formats into a pandas DataFrame and analyze its structure.

    Supported formats:
    - CSV (.csv)
    - JSON (.json)
    - HTML (.html, .htm)
    - Excel (.xls, .xlsx)
    - OpenDocument Spreadsheet (.ods)
    - Parquet (.parquet)

    Args:
        path_or_url: Local file path or URL to a data file

    Returns:
        Dictionary containing DataFrame information and summary
    """
    # Handle files and URLs
    path_or_url_type = path_or_url_check(path_or_url)
    mime_type, _ = mimetypes.guess_type(str(path_or_url))
    if path_or_url_type == "remote":
        path_or_url = convert_github_url_to_raw(path_or_url)
    elif path_or_url_type == "local":
        path_or_url = Path(path_or_url)
    else:
        return {"success": False, "error": "Invalid path or URL"}

    try:
        df, read_fn = load_dataframe_by_format(path_or_url, mime_type)

    except Exception as e:
        return {"success": False, "error": f"Failed to load data: {e!s}"}

    return {
        "success": True,
        "info": get_dataframe_info(df),
        "location_type": path_or_url_type,
        "file_path_or_url": str(path_or_url),
        "detected_format": mime_type,
        "read_function_string": read_fn,
    }


@mcp.prompt()
def create_eda_dashboard(
    file_path_or_url: str,
) -> str:
    """Prompt template for creating an EDA dashboard based on one dataset."""
    content = f"""
Create an EDA dashboard based on the following dataset:{file_path_or_url}. Proceed as follows:
1. Analyze the data using the load_and_analyze_data tool first, passing the file path or github url {file_path_or_url}
    to the tool.
2. Create a dashboard with 4 pages:
    - Page 1: Summary of the dataset using the Card component and the dataset itself using the plain AgGrid component.
    - Page 2: Visualizing the distribution of all numeric columns using the Graph component with a histogram.
        - use a Parameter that targets the Graph component and the x argument, and you can select the column to
            be displayed
        - IMPORTANT:remember that you target the chart like: <graph_id>.x and NOT <graph_id>.figure.x
        - do not use any color schemes etc.
        - add filters for all categorical columns
    - Page 3: Visualizing the correlation between all numeric columns using the Graph component with a scatter plot.
    - Page 4: Two interesting charts side by side, use the Graph component for this. Make sure they look good
        but do not try something beyond the scope of plotly express
"""
    return content


################# Chart functionality - not sure if I should include this in the MCP server


@mcp.tool()
def get_validated_chart_code(chart_plan: dict[str, Any]) -> str:
    """Validate the chart code created by the user."""
    try:
        chart_plan_obj = ChartPlan.model_validate(chart_plan)
        return chart_plan_obj.model_dump_json()
    except ValidationError as e:
        return json.dumps({"error": f"Validation Error: {e.errors()}"})


@mcp.prompt()
def create_vizro_chart(
    chart_type: str,
    file_path_or_url: str,
) -> str:
    """Prompt template for creating a Vizro chart."""
    content = f"""
Create a chart using the following chart type:
{chart_type}.
Make sure to analyze the data using the load_and_analyze_data tool first, passing the file path or github url
{file_path_or_url} to the tool. Then make sure to use the get_validated_chart_code tool to validate the chart code.
            """
    return content


########################### Trial Resources


@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data."""
    return "App configuration here"


@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """Echo a message as a resource."""
    return f"Resource echo: {message}"
