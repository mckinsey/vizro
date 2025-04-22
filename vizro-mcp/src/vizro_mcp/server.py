"""MCP server for Vizro-AI chart and dashboard creation."""

import json
from pathlib import Path
from typing import Any, Literal

import pandas as pd
import requests
import vizro.models as vm
from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError
from vizro import Vizro

from vizro_mcp.schemas import (
    AgGridEnhanced,
    ChartPlan,
    DashboardSimplified,
    GraphEnhanced,
    PageSimplified,
)
from vizro_mcp.utils import (
    convert_github_url_to_raw,
    get_dataframe_info,
    get_python_code_and_preview_link,
    path_or_url_check,
)

# TODO: what do I need to do here, as things are already set up?
mcp = FastMCP(
    "MCP server to help create Vizro dashboards and charts.",
)


@mcp.tool()
def validate_model_config(
    config: dict[str, Any], file_name: str, file_path_or_url: str, file_location_type: Literal["local", "remote"]
) -> dict[str, Any]:
    """Validate Vizro model configuration. Run whenever you have a complete dashboard configuration.

    If successful, the tool will return the python code and, if it is a remote file, the py.cafe link to the chart.

    Args:
        config: Either a JSON string or a dictionary representing a Vizro model configuration
        file_name: Name of the file to be loaded into the data_manager and used in the code, must be without extension
            (e.g., 'iris', 'gapminder', 'tips')
        file_path_or_url: String of file path or URL to be loaded into the data_manager
        file_location_type: Literal["local", "remote"]

    Returns:
        Dictionary with validation status and details
    """
    # Reset Vizro state before instantiation
    Vizro._reset()

    try:
        # Attempt to instantiate a Vizro model with the configuration
        dashboard = vm.Dashboard.model_validate(config)

    except ValidationError as e:
        # Handle Pydantic validation errors
        return {"valid": False, "error": f"Validation Error: {e!s}"}

    else:
        result = get_python_code_and_preview_link(dashboard, file_name, file_path_or_url)

        # Get the result before resetting
        result = {
            "valid": True,
            "message": "Configuration is valid for Dashboard!",
            "python_code": result["python_code"],
            "pycafe_url": result["pycafe_url"] if file_location_type == "remote" else None,
        }

        return result

    finally:
        # Always reset, regardless of success or failure
        Vizro._reset()


@mcp.tool()
def get_model_JSON_schema(model_name: str) -> dict[str, Any]:
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
    # Define the models we want to expose, grouped by category
    # TODO: do Container and Tabs need to be simplified like page, or is Page fine as original model?
    model_groups: dict[str, list[type[vm.VizroBaseModel]]] = {
        "components": [vm.Card, vm.Button, vm.Text, vm.Container, vm.Tabs, vm.Graph, vm.AgGrid],  #'Figure', 'Table'
        "layouts": [vm.Grid, vm.Flex],
        "controls": [vm.Filter, vm.Parameter],
        "selectors": [
            vm.Dropdown,
            vm.RadioItems,
            vm.Checklist,
            vm.DatePicker,
            vm.Slider,
            vm.RangeSlider,
            vm.DatePicker,
        ],
        "navigation": [vm.Navigation, vm.NavBar, vm.NavLink],
    }

    # Convert the model_groups dict to a dict with just names and descriptions
    result = {}
    for category, models_list in model_groups.items():
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
Instructions for create a Vizro chart:
    - analyze the datasets needed for the chart using the load_and_analyze_csv tool - the most important
        information here are the column names and column types
    - always return code for a plotly express chart, pay attention to the columns you have available
    - do NOT call any other tool after, especially do NOT create a dashboard
            """
    elif plan == "dashboard":
        return """
Instructions for create a Vizro dashboard:
    - analyze the datasets needed for the dashboard using the load_and_analyze_csv tool - the most
        important information here are the column names and column types
    - call the get_overview_vizro_models tool to get an overview of the available models
    - make a plan of what components you would like to use, then request all necessary schemas
    using the get_model_JSON_schema tool
    - assemble your components into a page, then add the page or pages to a dashboard
    - validate the dashboard configuration using the validate_model_config tool
    - if you display any code artifact, you must use the above created code, do not add new config to it


    IMPORTANT:
    - if you iterate over a valid produced solution, make sure to go ALWAYS via the validation step again to
        ensure the solution is valid
    - try not to output any config or code to the user until you have validated the solution
    - if you find yourself repeatedly getting something wrong, try enquiring the schema of the component in question
    """


@mcp.tool()
def load_and_analyze_csv(path_or_url: str) -> dict[str, Any]:
    """Load a CSV file from a local path or GitHub URL into a pandas DataFrame and analyze its structure.

    Args:
        path_or_url: Local file path or GitHub URL to a CSV file

    Returns:
        Dictionary containing DataFrame information and summary
    """
    path_or_url_type = path_or_url_check(path_or_url)
    if path_or_url_type == "remote":
        path_or_url = convert_github_url_to_raw(path_or_url)

    elif path_or_url_type == "local":
        path_or_url = Path(path_or_url)
    else:
        return {"success": False, "error": "Invalid path or URL"}

    try:
        df = pd.read_csv(
            path_or_url,
            # Add error handling for common CSV issues
            on_bad_lines="warn",
            low_memory=False,
        )
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Failed to fetch file: {e!s}"}
    return {
        "success": True,
        "info": get_dataframe_info(df),
        "location_type": path_or_url_type,
        "file_path_or_url": str(path_or_url),
    }


@mcp.prompt(
    name="create_EDA_dashboard",
    description="Prompt template for creating an EDA dashboard based on one CSV dataset",
)
def create_EDA_dashboard(
    file_path_or_url: str,
) -> str:
    """Prompt template for creating an EDA dashboard based on one CSV dataset."""
    content = f"""
Create an EDA dashboard based on the following dataset:{file_path_or_url}. Proceed as follows:
1. Analyze the data using the load_and_analyze_csv tool first, passing the file path or github url {file_path_or_url}
    to the tool.
2. Create a dashboard with 3 pages:
    - Page 1: Summary of the dataset using the Card component and the dataset itself using the plain AgGrid component.
    - Page 2: Visualizing the distribution of all numeric columns using the Graph component with a histogram.
        - use a Parameter that targets the Graph component and the x argument, and you can select the column to
            be displayed
        - IMPORTANT:remember that you target the chart like: <graph_id>.x and NOT <graph_id>.figure.x
        - do not use any color schemes etc.
        - add filters for all categorical columns
    - Page 3: Visualizing the correlation between all numeric columns using the Graph component with a scatter plot.
    - Page 4: Two interesting charts side by side, use the Graph component for this. Make sure they look goog
        but do not try something beyond the scope of plotly express
            """
    return content


################# Chart functionality - not sure if I should include this in the MCP server


@mcp.tool(name="get_validated_chart_code", description="Validates code created for a chart")
def get_validated_chart_code(chart_plan: dict[str, Any]) -> str:
    """Validate the chart code created by the user."""
    try:
        chart_plan_obj = ChartPlan(**chart_plan)
        return chart_plan_obj.model_dump_json()
    except ValidationError as e:
        return json.dumps({"error": f"Validation Error: {e!s}"})


@mcp.prompt(
    name="create_vizro_chart",
    description="Prompt template for creating a Vizro chart",
)
def create_vizro_chart(
    chart_type: str,
    file_path_or_url: str,
) -> str:
    """Prompt template for creating a Vizro chart."""
    content = f"""
Create a chart using the following chart type:
{chart_type}.
Make sure to analyze the data using the load_and_analyze_csv tool first, passing the file path or github url
{file_path_or_url} to the tool. Then make sure to use the get_validated_chart_code tool to validate the chart code.
            """
    return content


###########################
