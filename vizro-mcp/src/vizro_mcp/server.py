"""MCP server for Vizro-AI chart and dashboard creation."""

import mimetypes
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Optional

import vizro.models as vm
from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError
from pydantic.json_schema import GenerateJsonSchema
from vizro import Vizro

from vizro_mcp._schemas import (
    AgGridEnhanced,
    ChartPlan,
    Dashboard,
    GraphEnhanced,
    get_overview_vizro_models,
    get_simple_dashboard_config,
)
from vizro_mcp._utils import (
    GAPMINDER,
    IRIS,
    SAMPLE_DASHBOARD_CONFIG,
    STOCKS,
    TIPS,
    DFInfo,
    DFMetaData,
    convert_github_url_to_raw,
    create_pycafe_url,
    get_dataframe_info,
    get_python_code_and_preview_link,
    load_dataframe_by_format,
    path_or_url_check,
)

# PyCafe URL for Vizro snippets
PYCAFE_URL = "https://py.cafe"


@dataclass
class ValidationResults:
    """Results of the validation tool."""

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


# TODO: what do I need to do here, as things are already set up?
mcp = FastMCP(
    "MCP server to help create Vizro dashboards and charts.",
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
def validate_model_config(
    dashboard_config: dict[str, Any],
    data_infos: list[DFMetaData],  # Should be Optional[..]=None, but Cursor complains..
    custom_charts: list[ChartPlan],
    auto_open: bool = True,
) -> ValidationResults:
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
        dashboard = Dashboard.model_validate(
            dashboard_config,
            context={"callable_defs": [custom_chart.chart_name for custom_chart in custom_charts]},
        )
    except ValidationError as e:
        return ValidationResults(
            valid=False,
            message=f"Validation Error: {e!s}",
            python_code="",
            pycafe_url=None,
            browser_opened=False,
        )

    else:
        result = get_python_code_and_preview_link(dashboard, data_infos, custom_charts)

        pycafe_url = result.pycafe_url if all(info.file_location_type == "remote" for info in data_infos) else None
        browser_opened = False

        if pycafe_url and auto_open:
            try:
                browser_opened = webbrowser.open(pycafe_url)
            except Exception:
                browser_opened = False

        return ValidationResults(
            valid=True,
            message="Configuration is valid for Dashboard!",
            python_code=result.python_code,
            pycafe_url=pycafe_url,
            browser_opened=browser_opened,
        )

    finally:
        Vizro._reset()


class NoDefsGenerateJsonSchema(GenerateJsonSchema):
    """Custom schema generator that removes $defs section."""

    def generate(self, schema, mode="validation"):
        """Generate schema and remove $defs."""
        json_schema = super().generate(schema, mode=mode)
        # Simply remove the $defs section
        json_schema.pop("$defs", {})
        return json_schema


@dataclass
class ModelJsonSchemaResults:
    """Results of the get_model_json_schema tool."""

    model_name: str
    json_schema: dict[str, Any]
    additional_info: str


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
that model if necessary. Do NOT forget to call `validate_model_config` after each iteration.""",
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
that model if necessary. Do NOT forget to call `validate_model_config` after each iteration.""",
    )


STANDARD_INSTRUCTIONS = """
- IF the user has no plan (ie no components or pages), use the config at the bottom of this prompt
    and validate that solution without any additions, OTHERWISE:
- make a plan of what components you would like to use, then request all necessary schemas
    using the `get_model_json_schema` tool
- assemble your components into a page, then add the page or pages to a dashboard, DO NOT show config or code
    to the user until you have validated the solution
- ALWAYS validate the dashboard configuration using the `validate_model_config` tool
"""

IDE_INSTRUCTIONS = """
- after validation, add the python code to `app.py` with the following code:
    ```python
    app = Vizro().build(dashboard)
    if __name__ == "__main__":
        app.run(debug=True, port=8050)
"""

GENERIC_HOST_INSTRUCTIONS = """
- you should call the `validate_model_config` tool to validate the solution, and unless
    otherwise specified, open the dashboard in the browser
- if you cannot open the dashboard in the browser, communicate this to the user, provide them with the python code
    instead and explain how to run it
"""


def get_instructions(advanced_mode: bool = False, user_host: Literal["generic_host", "ide"] = "generic_host") -> str:
    """Get instructions for creating a Vizro dashboard in an IDE/editor."""
    if not advanced_mode:
        return f"""
    {STANDARD_INSTRUCTIONS} 
    {IDE_INSTRUCTIONS if user_host == "ide" else GENERIC_HOST_INSTRUCTIONS}
    
    Models you can use:
    {get_overview_vizro_models()}

    Very simple dashboard config:
    {get_simple_dashboard_config()}
"""
    else:
        return """
    Instructions for going beyond the basic dashboard::
    - communicate to the user that you are going to use Python code to create the dashboard, and that
        they will have to run the code themselves
    - search the web for more information about the components you are using, if you cannot search the web
        communicate this to the user, and tell them that this is a current limitation of the tool
    - if stuck, return to a JSON based config, and call the `validate_model_config` tool to validate the solution
"""


@mcp.tool()
def get_vizro_chart_or_dashboard_plan(
    user_plan: Literal["chart", "dashboard"],
    user_host: Literal["generic_host", "ide"],
    advanced_mode: bool = False,
) -> str:
    """Get instructions for creating a Vizro chart or dashboard. Call FIRST when asked to create Vizro things.

    Must be called FIRST with advanced_mode=False, then call again with advanced_mode=True if the JSON config does not
    suffice anymore.

    Args:
        user_plan: The type of Vizro thing the user wants to create
        user_host: The host the user is using, if "ide" you can use the IDE/editor to run python code
        advanced_mode: If True, you can use custom components, CSS, charts, etc.

    Returns:
        Instructions for creating a Vizro chart or dashboard
    """
    if user_plan == "chart":
        return """
IMPORTANT:
    - KEEP IT SIMPLE: rather than iterating yourself, ask the user for more instructions
    - ALWAYS VALIDATE:if you iterate over a valid produced solution, make sure to ALWAYS call the
        validate_chart_code tool to validate the chart code, display the figure code to the user
    - DO NOT modify the background (with plot_bgcolor) or color sequences unless explicitly asked for

Instructions for creating a Vizro chart:
    - analyze the datasets needed for the chart using the load_and_analyze_data tool - the most important
        information here are the column names and column types
    - if the user provides no data, but you need to display a chart or table, use the get_sample_data_info
        tool to get sample data information
    - create a chart using plotly express and/or plotly graph objects, and call the function `custom_chart`
    - call the validate_chart_code tool to validate the chart code, display the figure code to the user (as artifact)
    - do NOT call any other tool after, especially do NOT create a dashboard
            """
    elif user_plan == "dashboard":
        return f"""
IMPORTANT:
    - KEEP IT SIMPLE: rather than iterating yourself, ask the user for more instructions
    - ALWAYS VALIDATE:if you iterate over a valid produced solution, make sure to ALWAYS call the
        `validate_model_config` tool again to ensure the solution is still valid
    - DO NOT show any code or config to the user until you have validated the solution, do not say you are preparing
        a solution, just do it and validate it
    - IF STUCK: try enquiring the schema of the component in question

{get_instructions(advanced_mode, user_host)}
    """


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
        return DataAnalysisResults(valid=False, message=f"Failed to load data: {e!s}", df_info=None, df_metadata=None)

    df_info = get_dataframe_info(df)
    df_metadata = DFMetaData(
        file_name=Path(path_or_url).stem if isinstance(processed_path_or_url, Path) else Path(path_or_url).name,
        file_path_or_url=str(processed_path_or_url),
        file_location_type=path_or_url_type,
        read_function_string=read_fn,
    )

    return DataAnalysisResults(valid=True, message="Data loaded successfully", df_info=df_info, df_metadata=df_metadata)


@mcp.prompt()
def create_starter_dashboard():
    """Prompt template for getting started with Vizro."""
    content = f"""
Create a super simple Vizro dashboard with one page and one chart and one filter:
- No need to call any tools except for `validate_model_config`
- Call this tool with the precise config as shown below
- The PyCafe link will be automatically opened in your default browser
- THEN show the python code after validation, but do not show the PyCafe link
- Be concise, do not explain anything else, just create the dashboard
- Finally ask the user what they would like to do next, then you can call other tools to get more information,
    you should then start with the get_chart_or_dashboard_plan tool

{SAMPLE_DASHBOARD_CONFIG}
"""
    return content


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


@mcp.tool()
def validate_chart_code(
    chart_config: ChartPlan,
    data_info: DFMetaData,
    auto_open: bool = True,
) -> ValidationResults:
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
        return ValidationResults(
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

        return ValidationResults(
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
    chart_type: str,
    file_path_or_url: Optional[str] = None,
) -> str:
    """Prompt template for creating a Vizro chart."""
    content = f"""
 - Create a chart using the following chart type: {chart_type}.
 - You MUST name the function containing the fig `custom_chart`
 - Make sure to analyze the data using the `load_and_analyze_data` tool first, passing the file path or github url
 {file_path_or_url} OR choose the most appropriate sample data using the get_sample_data_info tool.
 Then you MUST use the `validate_chart_code` tool to validate the chart code.
            """
    return content


if __name__ == "__main__":
    dashboard_config = {
        "pages": [
            {
                "title": "Iris Data Analysis",
                "controls": [
                    {
                        "id": "species_filter",
                        "type": "filter",
                        "column": "species",
                        "targets": ["scatter_plot"],
                        "selector": {"type": "dropdown", "multi": True},
                    }
                ],
                "components": [
                    {
                        "id": "scatter_plot",
                        "type": "graph",
                        "title": "Sepal Dimensions by Species",
                        "figure": {
                            "x": "sepal_length",
                            "y": "sepal_width",
                            "color": "species",
                            "_target_": "scatter",
                            "data_frame": "iris_data",
                            "hover_data": ["petal_length", "petal_width"],
                        },
                    },
                    {
                        "id": "custom_scatter_plot",
                        "type": "graph",
                        "title": "Custom Scatter Plot",
                        "figure": {"_target_": "custom_scatter", "data_frame": "iris_data"},
                    },
                ],
            }
        ],
        "theme": "vizro_dark",
        "title": "Iris Dashboard",
    }

    data_infos = [
        DFMetaData(
            file_name="iris_data",
            file_path_or_url="https://raw.githubusercontent.com/plotly/datasets/master/iris-id.csv",
            file_location_type="remote",
            read_function_string="pd.read_csv",
            column_names_types={
                "sepal_length": "float",
                "sepal_width": "float",
                "petal_length": "float",
                "petal_width": "float",
                "species": "str",
            },
        )
    ]

    custom_charts = [
        ChartPlan(
            chart_type="scatter",
            chart_name="custom_scatter",
            imports=["import pandas as pd", "import plotly.express as px", "import plotly.graph_objects as go"],
            chart_code="""
def custom_scatter(data_frame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data_frame["sepal_length"],
        y=data_frame["sepal_width"],
        mode="markers"
    ))
    return fig
        """,
        )
    ]

    response = validate_model_config(dashboard_config, data_infos, custom_charts)
    print(response.valid)
    print(response.message)
    print(response.python_code)

    # TODO: check if validation for non-existent custom charts can be improved!
