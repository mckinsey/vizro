"""Schema defining pydantic models for usage in the MCP server."""

from typing import Annotated, Any, Literal, Optional

import vizro.models as vm
from pydantic import AfterValidator, BaseModel, Field, PrivateAttr, conlist

from vizro_mcp._utils import SAMPLE_DASHBOARD_CONFIG, DFMetaData

# Constants used in chart validation
CUSTOM_CHART_NAME = "custom_chart"
ADDITIONAL_IMPORTS = [
    "import vizro.plotly.express as px",
    "import plotly.graph_objects as go",
    "import pandas as pd",
    "import numpy as np",
    "from vizro.models.types import capture",
]

# These types are used to simplify the schema for the LLM.
SimplifiedComponentType = Literal["Card", "Button", "Text", "Container", "Tabs", "Graph", "AgGrid"]
SimplifiedSelectorType = Literal[
    "Dropdown", "RadioItems", "Checklist", "DatePicker", "Slider", "RangeSlider", "DatePicker"
]
SimplifiedControlType = Literal["Filter", "Parameter"]
SimplifiedLayoutType = Literal["Grid", "Flex"]

# This dict is used to give the model and overview of what is available in the vizro.models namespace.
# It helps it to narrow down the choices when asking for a model.
MODEL_GROUPS: dict[str, list[type[vm.VizroBaseModel]]] = {
    "main": [vm.Dashboard, vm.Page],
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


# These simplified page, container, tabs and dashboard models are used to return a flatter schema to the LLM in order to
# reduce the context size. Especially the dashboard model schema is huge as it contains all other models.


class FilterSimplified(vm.Filter):
    """Simplified Filter model for reduced schema. LLM should remember to insert actual components."""

    selector: Optional[SimplifiedSelectorType] = Field(
        default=None, description="Selector to be displayed. Only provide if asked for!"
    )


class ParameterSimplified(vm.Parameter):
    """Simplified Parameter model for reduced schema. LLM should remember to insert actual components."""

    selector: SimplifiedSelectorType = Field(description="Selector to be displayed.")


class ContainerSimplified(vm.Container):
    """Simplified Container model for reduced schema. LLM should remember to insert actual components."""

    components: list[SimplifiedComponentType] = Field(description="List of component names to be displayed.")
    layout: Optional[SimplifiedLayoutType] = Field(
        default=None, description="Layout to place components in. Only provide if asked for!"
    )


class TabsSimplified(vm.Tabs):
    """Simplified Tabs model for reduced schema. LLM should remember to insert actual components."""

    tabs: conlist(ContainerSimplified, min_length=1)


class PageSimplified(BaseModel):
    """Simplified Page modes for reduced schema. LLM should remember to insert actual components."""

    components: list[SimplifiedComponentType] = Field(description="List of component names to be displayed.")
    title: str = Field(description="Title to be displayed.")
    description: str = Field(default="", description="Description for meta tags.")
    layout: Optional[SimplifiedLayoutType] = Field(
        default=None, description="Layout to place components in. Only provide if asked for!"
    )
    controls: list[SimplifiedControlType] = Field(default=[], description="Controls to be displayed.")


class DashboardSimplified(BaseModel):
    """Simplified Dashboard model for reduced schema. LLM should remember to insert actual components."""

    pages: list[Literal["Page"]] = Field(description="List of page names to be included in the dashboard.")
    theme: Literal["vizro_dark", "vizro_light"] = Field(
        default="vizro_dark", description="Theme to be applied across dashboard. Defaults to `vizro_dark`."
    )
    navigation: Optional[Literal["Navigation"]] = Field(
        default=None, description="Navigation component for the dashboard. Only provide if asked for!"
    )
    title: str = Field(default="", description="Dashboard title to appear on every page on top left-side.")


# These enhanced models are used to return a more complete schema to the LLM. Although we do not have actual schemas for
# the figure fields, we can prompt the model via the description to produce something likely correct.
class GraphEnhanced(vm.Graph):
    """A Graph model that uses Plotly Express to create the figure."""

    figure: dict[str, Any] = Field(
        description="""
This is the plotly express figure to be displayed. Only use valid plotly express functions to create the figure.
Only use the arguments that are supported by the function you are using and where no extra modules such as statsmodels
are needed (e.g. trendline).

- Configure a dictionary as if this would be added as **kwargs to the function you are using.
- You must use the key: "_target_: "<function_name>" to specify the function you are using. Do NOT precede by
    namespace (like px.line)
- you must refer to the dataframe by name, for now it is one of "gapminder", "iris", "tips".
- do not use a title if your Graph model already has a title.
"""
    )


class AgGridEnhanced(vm.AgGrid):
    """AgGrid model that uses dash-ag-grid to create the figure."""

    figure: dict[str, Any] = Field(
        description="""
This is the ag-grid figure to be displayed. Only use arguments from the [`dash-ag-grid` function](https://dash.plotly.com/dash-ag-grid/reference).

The only difference to the dash version is that:
    - you must use the key: "_target_: "dash_ag_grid"
    - you must refer to data via "data_frame": <data_frame_name> and NOT via columnDefs and rowData (do NOT set)
        """
    )


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

        ["import pandas as pd",
        "import plotly.express as px"]
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

    _additional_vizro_imports: list[str] = PrivateAttr(ADDITIONAL_IMPORTS)

    def get_imports(self, vizro: bool = False):
        imports = list(dict.fromkeys(self.imports + self._additional_vizro_imports))  # remove duplicates
        if vizro:  # TODO: improve code of below
            imports = [imp for imp in imports if "import plotly.express as px" not in imp]
        else:
            imports = [imp for imp in imports if "vizro" not in imp]
        return "\n".join(imports) + "\n"

    def get_chart_code(self, chart_name: Optional[str] = None, vizro: bool = False):
        chart_code = self.chart_code
        if vizro:
            chart_code = chart_code.replace(f"def {CUSTOM_CHART_NAME}", f"@capture('graph')\ndef {CUSTOM_CHART_NAME}")
        if chart_name is not None:
            chart_code = chart_code.replace(f"def {CUSTOM_CHART_NAME}", f"def {chart_name}")
        return chart_code

    def get_dashboard_template(self, data_info: DFMetaData) -> str:
        """Create a simple dashboard template for displaying the chart.

        Args:
            data_info: The metadata of the dataset to use.

        Returns:
            Complete Python code for a Vizro dashboard displaying the chart.
        """
        chart_code = self.get_chart_code(vizro=True)
        imports = self.get_imports(vizro=True)

        # Add the Vizro-specific imports if not present
        additional_imports = [
            "import vizro.models as vm",
            "from vizro import Vizro",
            "from vizro.managers import data_manager",
        ]

        # Combine imports without duplicates
        all_imports = list(dict.fromkeys(additional_imports + imports.split("\n")))

        dashboard_template = f"""
{chr(10).join(imp for imp in all_imports if imp)}

# Load the data
data_manager["{data_info.file_name}"] = {data_info.read_function_string}("{data_info.file_path_or_url}")


# Custom chart code
{chart_code}

# Create a dashboard to display the chart
dashboard = vm.Dashboard(
    pages=[
        vm.Page(
            title="{self.chart_type.capitalize()} Chart",
            components=[
                vm.Graph(
                    id="{self.chart_type}_graph",
                    figure={CUSTOM_CHART_NAME}("{data_info.file_name}"),
                )
            ],
        )
    ],
    title="{self.chart_type.capitalize()} Dashboard",
)

# Run the dashboard
Vizro().build(dashboard).run()
"""

        return dashboard_template


def get_overview_vizro_models() -> dict[str, list[dict[str, str]]]:
    """Get all available models in the vizro.models namespace.

    Returns:
        Dictionary with categories of models and their descriptions
    """
    result: dict[str, list[dict[str, str]]] = {}
    for category, models_list in MODEL_GROUPS.items():
        result[category] = [
            {
                "name": model_class.__name__,
                "description": (model_class.__doc__ or "No description available").split("\n")[0],
            }
            for model_class in models_list
        ]
    return result


def get_simple_dashboard_config() -> str:
    """Very simple Vizro dashboard configuration. Use this config as a starter when no other config is provided."""
    return SAMPLE_DASHBOARD_CONFIG
