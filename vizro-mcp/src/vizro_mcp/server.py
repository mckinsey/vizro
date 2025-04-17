"""MCP server for Vizro-AI chart creation best practices."""

import base64
import gzip
import json
import re
from pathlib import Path
from typing import Annotated, Any, Literal, Optional, Union
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

# Create an MCP server with capabilities
# TODO: what do I need to do here, as things are already set up?
mcp = FastMCP(
    "Vizro Chart Creator",
)


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
- You must use the key: "_target_: "<function_name>" to specify the function you are using. Do NOT precede by namespace (like px.line)
- you must refer to the dataframe by name, for now it is one of "gapminder", "iris", "tips".
- do not use a title if your Graph already has a title.
"""
    )


def get_python_code_and_preview_link(
    model_object: vm.VizroBaseModel, file_name: str, file_paths_or_urls: str
) -> dict[str, Any]:
    """Get the Python code and preview link for a Vizro model object."""
    # Get the Python code
    python_code = model_object._to_python()

    # Add imports and dataset definitions at the top
    imports_and_data = f"""from vizro import Vizro
import vizro.plotly.express as px
from vizro.managers import data_manager
import pandas as pd
import vizro.models as vm

# Load data into the data_manager
data_manager["{file_name}"] = pd.read_csv("{file_paths_or_urls}")

"""
    # Find the model code section and prepend imports_and_data
    model_code_marker = "########### Model code ############"
    if model_code_marker in python_code:
        parts = python_code.split(model_code_marker, 1)
        python_code = imports_and_data + model_code_marker + parts[1]
    # Fallback if marker not found
    elif python_code.startswith("from vizro import Vizro"):
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


@mcp.tool()
def validate_model_config(
    config: dict[str, Any], file_name: str, file_path_or_url: str, file_location_type: Literal["local", "remote"]
) -> dict[str, Any]:
    """Validate Vizro model configuration by attempting to instantiate it. Run whenever you have a complete DASHBOARD configuration.

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

        # Reset Vizro state before instantiation
        Vizro._reset()

        # Attempt to instantiate a Vizro model with the configuration
        dashboard = vm.Dashboard(**model_config)

        result = get_python_code_and_preview_link(dashboard, file_name, file_path_or_url)

        # Get the result before resetting
        result = {
            "valid": True,
            "message": "Configuration is valid for Dashboard!",
            "python_code": result["python_code"],
            "pycafe_url": result["pycafe_url"] if file_location_type == "remote" else None,
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
    elif model_name == "Graph":
        return GraphPX.model_json_schema()
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
        "components": [vm.Card, vm.Button, vm.Text, vm.Container, vm.Tabs, vm.Graph],
        "layouts": [vm.Grid, vm.Flex],
        "controls": [vm.Filter, vm.Parameter],
        "selectors": [vm.Dropdown, vm.RadioItems, vm.Checklist, vm.DatePicker, vm.Slider, vm.RangeSlider],
        "navigation": [vm.Navigation, vm.NavBar, vm.NavLink],
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
def get_dataframe_info(df: pd.DataFrame, file_path_or_url: Union[str, Path]) -> dict[str, Any]:
    return {
        # "info": info_str,
        "location_type": "local" if isinstance(file_path_or_url, Path) else "remote",
        "file_path_or_url": file_path_or_url,
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
    """Load a CSV file from a local path or GitHub URL into a pandas DataFrame and analyze its structure.

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

            try:
                # Directly use pandas read_csv with the URL
                df = pd.read_csv(
                    raw_url,
                    # Add error handling for common CSV issues
                    on_bad_lines="warn",
                    low_memory=False,
                )
                return {"success": True, "data": get_dataframe_info(df, raw_url)}
            except requests.exceptions.RequestException as e:
                return {"success": False, "error": f"Failed to fetch file: {e!s}"}

        # Check if input is a valid local file
        path = Path(path_or_url)
        if path.exists():
            # Consistent options for both local and remote files
            df = pd.read_csv(path, on_bad_lines="warn", low_memory=False)
            return {"success": True, "data": get_dataframe_info(df, path)}

        else:
            return {
                "success": False,
                "error": f"Invalid input: '{path_or_url}' is neither a valid local file nor a GitHub URL",
            }

    except pd.errors.ParserError as e:
        # Handle CSV parsing errors specifically
        return {"success": False, "error": f"Error parsing CSV file: {e!s}"}
    except requests.exceptions.RequestException as e:
        # Handle network-related errors
        return {"success": False, "error": f"Network error when fetching file: {e!s}"}
    except Exception as e:
        # Catch-all for other errors
        return {"success": False, "error": f"Error processing file: {e!s}"}


@mcp.prompt(
    name="create_EDA_dashboard",
    description="Prompt template for creating an EDA dashboard based on one CSV dataset",
)
def create_EDA_dashboard(
    file_path_or_url: str,
) -> str:
    return [
        {
            "role": "user",
            "content": f"""
Create an EDA dashboard based on the following dataset:{file_path_or_url}. Proceed as follows:
1. Analyze the data using the load_and_analyze_csv tool first, passing the file path or github url {file_path_or_url} to the tool.
2. Create a dashboard with 3 pages:
    - Page 1: Overview of the dataset with a summary using the Card component.
    - Page 2: Visualizing the distribution of all numeric columns using the Graph component with a histogram.
        - use a Parameter that targets the Graph component and the x argument, and you can select the column to be displayed
        - IMPORTANT:remember that you target the chart like: <graph_id>.x and NOT <graph_id>.figure.x
        - do not use any color schemes etc.
    - Page 3: Visualizing the correlation between all numeric columns using the Graph component with a scatter plot.
            """,
        }
    ]


###### Chart functionality - not sure if I should include this in the MCP server
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
            description="""
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


#################

if __name__ == "__main__":
    mcp.run()
