"""MCP server for Vizro-AI chart creation best practices."""

import base64
import gzip
import io
import json
import re
from pathlib import Path
from typing import Annotated, Any, Literal, Optional
from urllib.parse import quote, urlencode

import pandas as pd
import requests
import vizro.models as vm
from mcp.server.fastmcp import FastMCP

# from mcp.server.fastmcp.server import Context
from pydantic import AfterValidator, BaseModel, Field, ValidationError
from vizro import Vizro

# PyCafe URL for Vizro snippets
PYCAFE_URL = "https://py.cafe"
CUSTOM_CHART_NAME = "custom_chart"


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


class GraphPX(vm.Graph):
    """A Graph model that uses Plotly Express to create the figure."""

    figure: dict[str, Any] = Field(
        description="""
This is the plotly express figure to be displayed. Only use valid plotly express functions to create the figure.
Only use the arguments that are supported by the function you are using.

- Configure a dictionary as if this would be added as **kwargs to the function you are using.
- You must use the key: "_target_: "<function_name>" to specify the function you are using.
- you must refer to the dataframe by name, for now it is one of "gapminder", "iris", "tips".
- do not use a title if your Graph already has a title.
"""
    )


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
def validate_model_config(model_name: str, config: dict[str, Any]) -> dict[str, Any]:
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


@mcp.tool(
    name="get_model_JSON_schema",
    description="Get the JSON schema for the specified Vizro model. Only use if you are asked to create a DASHBOARD.",
)
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
    elif model_name == "Graph":
        return GraphPX.model_json_schema()
    # Get the model class from the vizro.models namespace
    if not hasattr(vm, model_name):
        return {"error": f"Model '{model_name}' not found in vizro.models"}

    model_class = getattr(vm, model_name)

    # Get the JSON schema from the model
    schema = model_class.model_json_schema()
    return schema


@mcp.tool(
    name="get_overview_vizro_models",
    description="Get an overview of the available models in the vizro.models namespace. Only use if you are asked to create a DASHBOARD.",
)
def get_overview_vizro_models() -> dict[str, list[dict[str, str]]]:
    """Get all available models in the vizro.models namespace.

    Returns:
        Dictionary with categories of models and their descriptions
    """
    # Define the models we want to expose, grouped by category
    model_groups: dict[str, list[type[vm.VizroBaseModel]]] = {
        "components": [vm.Card, vm.Button, vm.Text, vm.Container, vm.Tabs, vm.Graph],
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
    ALWAYS offer the user the chance to see the dashboard when you have finished the code, but make it a hyperlink as the URL is long.

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


@mcp.tool(
    name="get_vizro_chart_or_dashboard_plan",
    description="Call this tool first to get an overview of what to do next when asked to create a Vizro chart or dashboard.",
)
def get_vizro_chart_or_dashboard_plan(plan: Literal["chart", "dashboard"]) -> str:
    if plan == "chart":
        return """
Instructions for create a Vizro chart:
    - analyze the datasets needed for the chart using the load_and_analyze_csv tool - the most important information here
        are the column names and column types
    - always return code for a plotly express chart, pay attention to the columns you have available
    - do NOT call any other tool after, especially do NOT create a dashboard
            """
    elif plan == "dashboard":
        return """
Instructions for create a Vizro dashboard:
    - analyze the datasets needed for the dashboard using the load_and_analyze_csv tool - the most important information here
        are the column names and column types
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


# Function to capture DataFrame info
def get_dataframe_info(df: pd.DataFrame) -> dict[str, Any]:
    return {
        # "info": info_str,
        "shape": df.shape,
        "columns": list(df.columns),
        "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
        # "missing_values": df.isna().sum().to_dict(),
        # "numeric_stats": df.describe().to_dict() if not df.empty else {},
        "sample": df.sample(5).to_dict() if not df.empty else {},
    }


@mcp.tool(
    name="load_and_analyze_csv",
    description="Load a CSV file from a local path or GitHub URL into a pandas DataFrame and analyze its structure.",
)
def load_and_analyze_csv(path_or_url: str) -> dict[str, Any]:
    """
    Load a CSV file from a local path or GitHub URL into a pandas DataFrame and analyze its structure.

    Args:
        path_or_url: Local file path or GitHub URL to a CSV file

    Returns:
        Dictionary containing DataFrame information and summary
    """

    try:
        # Check if input is a GitHub URL
        github_pattern = r"https?://(?:www\.)?github\.com/([^/]+)/([^/]+)/(?:blob|raw)/([^/]+)/(.+\.csv)"
        github_match = re.match(github_pattern, path_or_url)

        if github_match:
            # Convert GitHub URL to raw URL
            user, repo, branch, file_path = github_match.groups()
            raw_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file_path}"

            # Use standard requests library with timeout and streaming
            response = requests.get(raw_url, timeout=30, stream=True)
            if response.status_code == 200:
                # Use BytesIO for better performance with binary content
                df = pd.read_csv(
                    io.BytesIO(response.content),
                    # Add error handling for common CSV issues
                    on_bad_lines="warn",
                    low_memory=False,
                )
                return {"success": True, "data": get_dataframe_info(df)}
            else:
                return {"success": False, "error": f"Failed to fetch file: {response.status_code}"}

        # Check if input is a valid local file
        path = Path(path_or_url)
        if path.exists():
            # Consistent options for both local and remote files
            df = pd.read_csv(path, on_bad_lines="warn", low_memory=False)
            return {"success": True, "data": get_dataframe_info(df)}

        else:
            return {
                "success": False,
                "error": f"Invalid input: '{path_or_url}' is neither a valid local file nor a GitHub URL",
            }

    except pd.errors.ParserError as e:
        # Handle CSV parsing errors specifically
        return {"success": False, "error": f"Error parsing CSV file: {str(e)}"}
    except requests.exceptions.RequestException as e:
        # Handle network-related errors
        return {"success": False, "error": f"Network error when fetching file: {str(e)}"}
    except Exception as e:
        # Catch-all for other errors
        return {"success": False, "error": f"Error processing file: {str(e)}"}


def _strip_markdown(code_string: str) -> str:
    """Remove any code block wrappers (markdown or triple quotes)."""
    wrappers = [("```python\n", "```"), ("```py\n", "```"), ("```\n", "```"), ('"""', '"""'), ("'''", "'''")]

    for start, end in wrappers:
        if code_string.startswith(start) and code_string.endswith(end):
            code_string = code_string[len(start) : -len(end)]
            break

    return code_string.strip()


def _check_chart_code(v: str) -> str:
    v = _strip_markdown(v)

    # TODO: add more checks: ends with return, has return, no second function def, only one indented line
    func_def = f"def {CUSTOM_CHART_NAME}("
    if func_def not in v:
        raise ValueError(f"The chart code must be wrapped in a function named `{CUSTOM_CHART_NAME}`")

    # Keep only the function definition and everything after it
    # Sometimes models like Gemini return extra imports in chart_code field
    v = v[v.index(func_def) :].strip()

    first_line = v.split("\n")[0].strip()
    if "data_frame" not in first_line:
        raise ValueError(
            """The chart code must accept a single argument `data_frame`,
and it should be the first argument of the chart."""
        )
    return v


class ChartPlan(BaseModel):
    """Base chart plan used to generate chart code based on user visualization requirements."""

    chart_type: str = Field(
        description="""
        Describes the chart type that best reflects the user request.
        """,
    )
    imports: list[str] = Field(
        description="""
        List of import statements required to render the chart defined by the `chart_code` field. Ensure that every
        import statement is a separate list/array entry: An example of valid list of import statements would be:

        [`import pandas as pd`,
        `import plotly.express as px`]
        """,
    )
    chart_code: Annotated[
        str,
        AfterValidator(_check_chart_code),
        Field(
            description=f"""
        Python code that generates a generates a plotly go.Figure object. It must fulfill the following criteria:
        1. Must be wrapped in a function name
        2. Must accept a single argument `data_frame` which is a pandas DataFrame
        3. Must return a plotly go.Figure object
        4. All data used in the chart must be derived from the data_frame argument, all data manipulations
        must be done within the function.
        """,
        ),
    ]


@mcp.tool(name="get_validated_chart_code", description="Validates code created for a chart")
def get_validated_chart_code(chart_plan: dict[str, Any]) -> str:
    """Validate the chart code created by the user."""
    try:
        chart_plan = ChartPlan(**chart_plan)
        return chart_plan.model_dump_json()
    except ValidationError as e:
        return {"error": f"Validation Error: {e!s}"}


@mcp.prompt(
    name="create_vizro_chart",
    description="Prompt template for creating a Vizro chart",
)
def create_vizro_chart(
    chart_type: str,
    file_path_or_url: str,
) -> str:
    return [
        {
            "role": "Assistant",
            "content": f"""
Create a chart using the following chart type:\n{chart_type}.
Make sure to analyze the data using the load_and_analyze_csv tool first, passing the file path or github url {file_path_or_url} to the tool.
Then make sure to use the get_validated_chart_code tool to validate the chart code.
            """,
        }
    ]


if __name__ == "__main__":
    mcp.run()
