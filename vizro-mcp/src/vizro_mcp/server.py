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
    else:  # dashboard
        return """
Instructions for create a Vizro dashboard:
    - analyze the datasets needed for the dashboard using the load_and_analyze_csv tool - the most important information here
        are the column names and column types
    - call get_model_JSON_schema tool to get the schema for the components you need
    - always use validate_model_config tool to validate your dashboard configuration before returning it
    - remember that a dashboard is made up of pages, and pages are made up of components
    - most important components are: Graph, Card, Button, Text, Container, Tabs
    - controls are: Filter, Parameter
    - selectors are: Dropdown, RadioItems, Checklist, DatePicker, Slider, RangeSlider
    - navigation is: Navigation, NavBar, NavLink

Here are notes on using Graph PX component:
    - to create a plotly express figure, you need to specify the plotly express function to use in the "_target_" key
    - the figure is a dictionary with the plotly express function name and the arguments to pass to it
    - example:
```python
vm.Graph(
    id="scatter_plot",
    figure={
        "_target_": "scatter",  # This refers to px.scatter
        "data_frame": "gapminder",
        "x": "gdpPercap",
        "y": "lifeExp",
        "color": "continent",
        "size": "pop",
        "hover_name": "country",
        "log_x": True,
    },
    title="GDP vs Life Expectancy",
)
```
"""


def get_dataframe_info(df: pd.DataFrame, file_path_or_url: Union[str, Path]) -> dict[str, Any]:
    """Get basic information about a pandas DataFrame."""
    column_types = {}
    for col_name, dtype in df.dtypes.items():
        column_types[col_name] = str(dtype)

    return {
        "file_path_or_url": str(file_path_or_url),
        "num_rows": len(df),
        "num_columns": len(df.columns),
        "columns": list(df.columns),
        "column_types": column_types,
        "sample": df.head(5).to_dict(orient="records"),
    }


@mcp.tool(
    name="load_and_analyze_csv",
    description="Load a CSV file from a local path or GitHub URL into a pandas DataFrame and analyze its structure.",
)
def load_and_analyze_csv(path_or_url: str) -> dict[str, Any]:
    """Load a CSV file from a local path or GitHub URL into a pandas DataFrame and analyze its structure.

    Args:
        path_or_url: Either a local file path or a GitHub URL to a CSV file

    Returns:
        Dictionary with information about the DataFrame
    """
    try:
        # Determine if input is a URL or a local file path
        if path_or_url.startswith(("http://", "https://")):
            # Handle GitHub raw content URLs
            if "github.com" in path_or_url and not path_or_url.startswith("https://raw.githubusercontent.com"):
                # Convert GitHub URL to raw content URL
                if "/blob/" in path_or_url:
                    path_or_url = path_or_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                else:
                    return {"error": "Invalid GitHub URL format. URL should point to a specific file (blob)."}

            # Download content from URL
            response = requests.get(path_or_url, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Create a temporary file to save the content
            temp_file = Path("temp_file.csv")
            temp_file.write_bytes(response.content)

            # Read CSV file
            df = pd.read_csv(temp_file)

            # Get DataFrame info
            result = get_dataframe_info(df, path_or_url)

            # Remove the temporary file
            temp_file.unlink()

            return result
        else:
            # Handle local file path
            file_path = Path(path_or_url)
            if not file_path.exists():
                return {"error": f"File not found: {path_or_url}"}

            # Read CSV file
            df = pd.read_csv(file_path)

            # Get DataFrame info
            return get_dataframe_info(df, path_or_url)

    except Exception as e:
        return {"error": f"Error loading or analyzing CSV: {e!s}"}


@mcp.prompt(
    name="create_EDA_dashboard",
    description="Prompt template for creating an EDA dashboard based on one CSV dataset",
)
def create_EDA_dashboard(
    file_path_or_url: str,
) -> str:
    """Create a template for an EDA dashboard based on a CSV dataset.

    Args:
        file_path_or_url: Either a local file path or a GitHub URL to a CSV file

    Returns:
        A prompt template to create an EDA dashboard
    """
    return f"""You are an expert in creating data visualization dashboards with Vizro.
Your task is to create an exploratory data analysis (EDA) dashboard for the dataset at {file_path_or_url}.

Load and analyze the dataset, then plan a comprehensive EDA dashboard that will help users understand the data.
Include visualizations for distributions, correlations, and other relevant analyses based on the dataset structure.

Be creative and thoughtful about the design and layout of the dashboard.
"""


def _strip_markdown(code_string: str) -> str:
    """Strip markdown code blocks from a code string."""
    if code_string.startswith("```python"):
        code_string = code_string.split("```python", 1)[1]
    if code_string.startswith("```"):
        code_string = code_string.split("```", 1)[1]
    if code_string.endswith("```"):
        code_string = code_string.rsplit("```", 1)[0]
    return code_string.strip()


def _check_chart_code(v: str) -> str:
    """Check if the chart code is valid and return a clean version."""
    # Strip markdown code blocks
    clean_code = _strip_markdown(v)

    # Check if the code contains px or plotly express
    if "import plotly.express as px" not in clean_code and "plotly.express" not in clean_code:
        raise ValueError("Chart code must import plotly.express.")

    # Check that code contains a plot type that is a method of px
    plot_types = [
        "scatter",
        "line",
        "bar",
        "histogram",
        "box",
        "violin",
        "pie",
        "sunburst",
        "treemap",
        "scatter_3d",
        "line_3d",
        "scatter_geo",
        "scatter_polar",
        "timeline",
    ]
    px_found = False
    for plot_type in plot_types:
        if f"px.{plot_type}" in clean_code:
            px_found = True
            break
    if not px_found:
        raise ValueError("Chart code must include a plotly express plot.")

    return clean_code


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
    ] = Field(
        description="""
        A Python function that implements the full chart using plotly express. This should be a standalone chart,
        not integrated into a dashboard. The function should be well-commented and handle all necessary data preprocessing.
        It should include proper axis labels, title, and other plot customizations to make the chart informative and complete.
        """,
    )


@mcp.tool(name="get_validated_chart_code", description="Validates code created for a chart")
def get_validated_chart_code(chart_plan: dict[str, Any]) -> str:
    """Validates the chart plan and returns clean usable code."""
    valid_plan = ChartPlan(**chart_plan)
    imports = "\n".join(valid_plan.imports)
    return f"{imports}\n\n{valid_plan.chart_code}\n"


@mcp.prompt(
    name="create_vizro_chart",
    description="Prompt template for creating a Vizro chart",
)
def create_vizro_chart(
    chart_type: str,
    file_path_or_url: str,
) -> str:
    """Create a template for a Vizro chart based on a CSV dataset.

    Args:
        chart_type: The type of chart to create (e.g., scatter, line, bar)
        file_path_or_url: Either a local file path or a GitHub URL to a CSV file

    Returns:
        A prompt template to create a Vizro chart
    """
    return f"""You are an expert in creating data visualizations with Plotly Express.
Your task is to create a {chart_type} chart using the dataset at {file_path_or_url}.

First, load and analyze the dataset to understand its structure.
Then, create a {chart_type} chart that best represents the data.

Please return a detailed implementation with:
1. Proper import statements
2. Clear code with comments explaining key steps
3. Appropriate customization (colors, labels, hover information, etc.)
4. Any necessary data preprocessing

Focus on making the visualization both informative and visually appealing.
"""
