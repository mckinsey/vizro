"""MCP server for Vizro-AI chart creation best practices."""

import base64
import gzip
import json
from typing import Any, Literal, Optional, Union
from urllib.parse import quote, urlencode

import vizro.models as vm
from mcp.server.fastmcp import FastMCP

# from mcp.server.fastmcp.server import Context
from pydantic import BaseModel, Field, ValidationError
from vizro import Vizro

# PyCafe URL for Vizro snippets
PYCAFE_URL = "https://py.cafe"


class SimplePage(BaseModel):
    """Simplified Page modes for reduced schema. LLM should remember to insert actual components."""

    components: list[Literal["card", "button", "text", "container", "tabs"]] = Field(
        description="List of component names to be displayed."
    )
    title: str = Field(description="Title to be displayed.")
    description: str = Field(default="", description="Description for meta tags.")
    layout: Optional[Literal["grid", "flex"]] = Field(default=None, description="Layout to place components in.")
    controls: list[Literal["filter", "parameter"]] = Field(default=[], description="Controls to be displayed.")


class SimpleDashboard(BaseModel):
    """Simplified Dashboard model for reduced schema. LLM should remember to insert actual components."""

    pages: list[Literal["page"]] = Field(description="List of page names to be included in the dashboard.")
    theme: Literal["vizro_dark", "vizro_light"] = Field(
        default="vizro_dark", description="Theme to be applied across dashboard. Defaults to `vizro_dark`."
    )
    # navigation: Optional[Literal["navigation"]] = Field(
    #     default=None, description="Navigation component for the dashboard."
    # )
    title: str = Field(default="", description="Dashboard title to appear on every page on top left-side.")


# Create an MCP server with capabilities
# TODO: what do I need to do here, as things are already set up?
mcp = FastMCP(
    "Vizro Chart Creator",
    # Explicitly specify server capabilities
    capabilities={
        "prompts": {},  # Enable prompts capability
        "tools": {},  # Enable tools capability
        "resources": {},  # Enable resources capability
    },
)


@mcp.tool()
def validate_model_config(model_name: str, config: Union[str, dict[str, Any]]) -> dict[str, Any]:
    """Validate Vizro model configuration by attempting to instantiate it. Run whenever you have a complete configuration.

    Args:
        model_name: Name of the Vizro model to validate (e.g., 'Card', 'Dashboard', 'Page')
        config: Either a JSON string or a dictionary representing a Vizro model configuration

    Returns:
        Dictionary with validation status and details
    """

    try:
        # Handle input as either string or dictionary
        if isinstance(config, str):
            try:
                model_config = json.loads(config)
            except json.JSONDecodeError as e:
                return {"valid": False, "error": f"Invalid JSON: {e!s}"}
        elif hasattr(config, "items"):  # Check if it's dict-like
            model_config = config
        else:
            return {"valid": False, "error": f"Invalid input type: {type(config)}. Expected string or dictionary."}

        # Get the model class from the vizro.models namespace
        if not hasattr(vm, model_name):
            return {"valid": False, "error": f"Model '{model_name}' not found in vizro.models"}

        model_class = getattr(vm, model_name)

        # Reset Vizro state before instantiation
        Vizro._reset()

        # Attempt to instantiate a Vizro model with the configuration
        _ = model_class(**model_config)

        # Get the result before resetting
        result = {
            "valid": True,
            "message": f"Configuration is valid for {model_name}!",
        }

        return result

    except ValidationError as e:
        # Handle Pydantic validation errors
        return {"valid": False, "error": f"Validation Error: {e!s}"}
    except Exception as e:
        # Handle other exceptions
        return {"valid": False, "error": f"Error: {e!s}"}
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
        return SimplePage.model_json_schema()
    elif model_name == "Dashboard":
        return SimpleDashboard.model_json_schema()
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
    model_groups: dict[str, list[type[vm.VizroBaseModel]]] = {
        "components": [vm.Card, vm.Button, vm.Text, vm.Container, vm.Tabs],
        "layouts": [vm.Grid, vm.Flex],
        "controls": [vm.Filter, vm.Parameter],
        "selectors": [vm.Dropdown, vm.RadioItems, vm.Checklist, vm.DatePicker, vm.Slider, vm.RangeSlider],
    }

    # Convert the model_groups dict to a dict with just names and descriptions
    result = {}
    for category, models_list in model_groups.items():
        result[category] = [
            {
                "name": model_class.__name__,
                "description": (model_class.__doc__ or "No description available").split("\n")[0]
                if model_class.__doc__
                else "No description",
            }
            for model_class in models_list
        ]

    return result


@mcp.tool()
def validated_config_to_python_code(model_name: str, config: dict[str, Any]) -> dict[str, Any]:
    """Convert a Vizro model configuration to Python code and generate a PyCafe link where the dashboard is shown LIVE.
    ALWAYS offer the user the chance to see the dashboard when you have finished the code.

    Args:
        model_name: Name of the Vizro model to convert to Python code
        config: Dictionary representing a Vizro model configuration

    Returns:
        Dictionary with the Python code and PyCafe URL
    """

    # Get the model class from the vizro.models namespace
    if not hasattr(vm, model_name):
        return {"error": f"Error: Model '{model_name}' not found in vizro.models"}

    model_class = getattr(vm, model_name)

    try:
        # Reset Vizro state before instantiation
        Vizro._reset()

        # Create a model instance from the configuration
        model_instance = model_class(**config)

        # Get the Python code
        python_code = model_instance._to_python()

        # Add imports and dataset definitions at the top
        imports_and_data = """from vizro import Vizro
import vizro.plotly.express as px
from vizro.managers import data_manager

# Load predefined datasets
data_manager["iris"] = px.data.iris()
data_manager["gapminder"] = px.data.gapminder()
data_manager["tips"] = px.data.tips()

"""
        # If the code already starts with 'from vizro import Vizro', replace it
        if python_code.startswith("from vizro import Vizro"):
            python_code = imports_and_data + python_code[len("from vizro import Vizro\n") :]
        else:
            python_code = imports_and_data + python_code

        # Add final run line if not present
        if "Vizro().build(model).run()" not in python_code:
            python_code += "\n\nVizro().build(model).run()"

        # Create JSON object for py.cafe
        json_object = {
            "code": python_code,
            "requirements": "vizro",
            "files": [],
        }

        # Convert to compressed base64 URL
        json_text = json.dumps(json_object)
        compressed_json_text = gzip.compress(json_text.encode("utf8"))
        base64_text = base64.b64encode(compressed_json_text).decode("utf8")
        query = urlencode({"c": base64_text}, quote_via=quote)
        pycafe_url = f"{PYCAFE_URL}/snippet/vizro/v1?{query}"

        return {"python_code": python_code, "pycafe_url": pycafe_url}

    except Exception as e:
        return {"error": f"Error: {e!s}"}
    finally:
        # Always reset, regardless of success or failure
        Vizro._reset()


@mcp.tool()
def get_vizro_chart_or_dashboard_plan() -> str:
    """Call this tool first to get an overview of what to do next."""
    return """
    I'll help you create a Vizro-compatible chart or dashboard based on your data and requirements.

    Here's a plan for how we'll work together:
        - if you want to create a chart, do not call any other tool, but use plotly express or graph_objects to create the chart
        - if you think the query is aiming to create a dashboard, follow these steps:
            - call the get_overview_vizro_models tool to get an overview of the available models
            - make a plan of what components you would like to use, you need to decide on a layout and components per page
            then request any necessary schema using the get_model_JSON_schema tool
            - assemble your components into a page, then add the page or pages to a dashboard
            - validate the dashboard configuration using the validate_model_config tool use `Dashboard` as the model name
            - call the validated_config_to_python_code tool to convert the dashboard configuration to Python code
            - if you display any code artifact, you must use the above created code


    IMPORTANT:
    - if you iterate over a valid produced solution, make sure to go ALWAYS via the validation step again to ensure the solution is valid
    """


if __name__ == "__main__":
    mcp.run()
