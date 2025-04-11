"""MCP server for Vizro-AI chart creation best practices."""

import json
from typing import Any, Literal, Optional, Union

import vizro.models as vm
from mcp.server.fastmcp import FastMCP

# from mcp.server.fastmcp.server import Context
from pydantic import BaseModel, Field, ValidationError

# Import Vizro for resetting state
from vizro import Vizro


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
mcp = FastMCP(
    "Vizro Chart Creator",
    # Explicitly specify server capabilities
    capabilities={
        "prompts": {},  # Enable prompts capability
        "tools": {},  # Enable tools capability
        "resources": {},  # Enable resources capability
    },
)


# @mcp.tool()
# async def my_tool(x: int, ctx: Context[Any, Any]) -> str:
#     # Log messages to the client
#     await ctx.info(f"Processing {x}")
#     await ctx.debug("Debug info")
#     await ctx.warning("Warning message")
#     await ctx.error("Error message")

#     # Report progress
#     # await ctx.report_progress(50, 100)

#     # Access resources
#     # data = ctx.read_resource("resource://data")

#     # # Get request info
#     # request_id = ctx.request_id
#     # client_id = ctx.client_id

#     return str(x)


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
        model_instance = model_class(**model_config)

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
def validated_config_to_python_code(model_name: str, config: dict[str, Any]) -> str:
    """Convert a Vizro model configuration to Python code.

    Args:
        model_name: Name of the Vizro model to convert to Python code
        config: Dictionary representing a Vizro model configuration

    Returns:
        Python code for the Vizro model
    """

    # Get the model class from the vizro.models namespace
    if not hasattr(vm, model_name):
        return f"Error: Model '{model_name}' not found in vizro.models"

    model_class = getattr(vm, model_name)

    Vizro._reset()
    model_instance = model_class(**config)
    python_code = model_instance._to_python()

    Vizro._reset()
    return python_code


@mcp.tool()
def get_vizro_chart_or_dashboard_plan() -> str:
    """Call this tool first to get an overview of what to do next."""
    return f"""
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
    - if you iterate over a valid produced solution, make sure to go via the validation step again to ensure the solution is valid
    """


#            - call the get_model_JSON_schema tool to get the JSON schema for the Dashboard model

# @mcp.resource("schema://card")
# def card_schema() -> str:
#     """Get the JSON schema for the Vizro Card model.

#     Returns:
#         JSON schema of the Vizro Card model as a formatted string
#     """
#     try:
#         # Get the JSON schema from the Card model
#         schema = vm.Card.model_json_schema()
#         # Return the formatted JSON string
#         return json.dumps(schema, indent=2)
#     except Exception as e:
#         return f"Error: Failed to get Card schema: {e!s}"


# @mcp.resource("models://available")
# def available_models() -> str:
#     """Get a formatted list of all available models in the vizro.models namespace.

#     Returns:
#         Formatted string with all available models and their descriptions
#     """
#     try:
#         # Get all classes defined in the vizro.models module
#         models = {
#             name: obj
#             for name, obj in inspect.getmembers(vm)
#             if inspect.isclass(obj) and obj.__module__.startswith("vizro.models")
#         }

#         # Organize models by category
#         categories = {"Components": [], "Containers": [], "Layouts": [], "Actions": [], "Other Models": []}

#         for name, model_class in sorted(models.items()):
#             # Skip private classes
#             if name.startswith("_"):
#                 continue

#             # Get docstring if available (just the first line)
#             doc = inspect.getdoc(model_class) or "No description available"
#             first_line = doc.split("\n")[0] if doc else "No description"

#             # Create model entry
#             model_entry = f"- **{name}**: {first_line}"

#             # Categorize based on module or name patterns
#             module = model_class.__module__.split(".")[-1]
#             if "component" in module.lower() or "component" in name.lower():
#                 categories["Components"].append(model_entry)
#             elif "container" in module.lower() or "container" in name.lower():
#                 categories["Containers"].append(model_entry)
#             elif "layout" in module.lower() or "layout" in name.lower():
#                 categories["Layouts"].append(model_entry)
#             elif "action" in module.lower() or "action" in name.lower():
#                 categories["Actions"].append(model_entry)
#             else:
#                 categories["Other Models"].append(model_entry)

#         # Build formatted string
#         result = "# Available Vizro Models\n\n"
#         for category, entries in categories.items():
#             if entries:  # Only include non-empty categories
#                 result += f"## {category}\n\n"
#                 result += "\n".join(entries)
#                 result += "\n\n"

#         return result
#     except Exception as e:
#         return f"Error: Failed to get available models: {e!s}"


# @mcp.prompt()
# def create_chart(data_frame: str, chart_description: str) -> str:
#     """Create a chart based on dataframe and description.

#     Args:
#         data_frame: Sample of the data_frame to use for the chart
#         chart_description: Description of the chart to create
#     """
#     return f"""
# I'll help you create a Vizro-compatible chart based on your data and requirements.

# Your dataframe code:
# ```python
# {data_frame}
# ```

# Your chart description:
# {chart_description}

# I'll generate a chart that follows these best practices:
# 1. Must use plotly.express or graph_objects, NOT matplotlib
# 2. Returns a plotly figure object
# 3. Contains appropriate titles, labels, and annotations
# 4. Does NOT use a specific color scheme unless requested in chart description
# 5. Handles data preprocessing within the function

# Let me create a chart function that:
# - Takes a single dataframe parameter
# - Does all data manipulation inside the function
# - Returns a plotly figure following your requirements

# Here's a code template:
# ```python
# import plotly.express as px

# def custom_chart(data_frame):
#     # Data preprocessing here

#     # Create figure
#     fig = px.bar(
#         data_frame,
#         x='category',
#         y='value',
#     )

#     # Optional: Additional figure customization
#     fig.update_layout(
#         legend_title='Legend',
#         xaxis_title='X-Axis',
#         yaxis_title='Y-Axis'
#     )

#     return fig
# ```
# """


if __name__ == "__main__":
    # FastMCP.run() should handle stream creation internally
    mcp.run()
