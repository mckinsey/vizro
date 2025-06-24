"""Schema defining pydantic models for usage in the MCP server."""

from typing import Annotated, Any, Optional

import vizro.models as vm
from pydantic import AfterValidator, BaseModel, Field, PrivateAttr, ValidationInfo

from vizro_mcp._utils import DFMetaData

BASE_IMPORTS = [
    "import vizro.plotly.express as px",
    "import plotly.graph_objects as go",
    "import pandas as pd",
    "import numpy as np",
    "from vizro.models.types import capture",
]


# These enhanced models are used to return a more complete schema to the LLM. Although we do not have actual schemas for
# the figure fields, we can prompt the model via the description to produce something likely correct.
class GraphEnhanced(vm.Graph):
    """A Graph model that uses Plotly Express to create the figure."""

    figure: dict[str, Any] = Field(
        description="""
For simpler charts and without need for data manipulation, use this field:
This is the plotly express figure to be displayed. Only use valid plotly express functions to create the figure.
Only use the arguments that are supported by the function you are using and where no extra modules such as statsmodels
are needed (e.g. trendline):
- Configure a dictionary as if this would be added as **kwargs to the function you are using.
- You must use the key: "_target_: "<function_name>" to specify the function you are using. Do NOT precede by
    namespace (like px.line)
- you must refer to the dataframe by name, check file_name in the data_infos field ("data_frame": "<file_name>")
- do not use a title if your Graph model already has a title.

For more complex charts and those that require data manipulation, use the `custom_charts` field:
- create the suitable number of custom charts and add them to the `custom_charts` field
- refer here to the function signature you created
- you must use the key: "_target_: "<custom_chart_name>"
- you must refer to the dataframe by name, check file_name in the data_infos field ("data_frame": "<file_name>")
- in general, DO NOT modify the background (with plot_bgcolor) or color sequences unless explicitly asked for
- when creating hover templates, EXPLICITLY style them to work on light and dark mode
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


###### Chart functionality ######
def _strip_markdown(code_string: str) -> str:
    """Remove any code block wrappers (markdown or triple quotes)."""
    wrappers = [("```python\n", "```"), ("```py\n", "```"), ("```\n", "```"), ('"""', '"""'), ("'''", "'''")]

    for start, end in wrappers:
        if code_string.startswith(start) and code_string.endswith(end):
            code_string = code_string[len(start) : -len(end)]
            break

    return code_string.strip()


def _check_chart_code(v: str, info: ValidationInfo) -> str:
    v = _strip_markdown(v)

    # TODO: add more checks: ends with return, has return, no second function def, only one indented line
    func_def = f"def {info.data['chart_name']}("
    if func_def not in v:
        raise ValueError(f"The chart code must be wrapped in a function named `{info.data['chart_name']}`")

    v = v[v.index(func_def) :].strip()

    first_line = v.split("\n")[0].strip()
    if "(data_frame" not in first_line:
        raise ValueError("""The chart code must accept as first argument `data_frame` which is a pandas DataFrame.""")
    return v


class ChartPlan(BaseModel):
    """Base chart plan used to generate chart code based on user visualization requirements."""

    chart_type: str = Field(
        description="""
        Describes the chart type that best reflects the user request.
        """,
    )
    chart_name: str = Field(
        description="""
        The name of the chart function. Should be unique, concise and in snake_case.
        """,
        pattern=r"^[a-z][a-z0-9_]*$",
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
        1. Must be wrapped in a function that is named `chart_name`
        2. Must accept as first argument argument `data_frame` which is a pandas DataFrame
        3. Must return a plotly go.Figure object
        4. All data used in the chart must be derived from the data_frame argument, all data manipulations
        must be done within the function.
        5. DO NOT modify the background (with plot_bgcolor) or color sequences unless explicitly asked for
        6. When creating hover templates, explicitly ensure that it works on light and dark mode
        """,
        ),
    ]

    _base_chart_imports: list[str] = PrivateAttr(BASE_IMPORTS)

    def get_imports(self, vizro: bool = False):
        imports = list(dict.fromkeys(self.imports + self._base_chart_imports))  # remove duplicates
        if vizro:
            imports = [imp for imp in imports if "import plotly.express as px" not in imp]
        else:
            imports = [imp for imp in imports if "vizro" not in imp]
        return "\n".join(imports) + "\n"

    def get_chart_code(self, chart_name: Optional[str] = None, vizro: bool = False):
        chart_code = self.chart_code
        if vizro:
            chart_code = chart_code.replace(f"def {self.chart_name}", f"@capture('graph')\ndef {self.chart_name}")
        if chart_name is not None:
            chart_code = chart_code.replace(f"def {self.chart_name}", f"def {chart_name}")
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
        additional_dashboard_imports = [
            "import vizro.models as vm",
            "from vizro import Vizro",
            "from vizro.managers import data_manager",
        ]

        # Combine imports without duplicates
        all_imports = list(dict.fromkeys(additional_dashboard_imports + imports.split("\n")))

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
                    figure={self.chart_name}("{data_info.file_name}"),
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


if __name__ == "__main__":
    plan = ChartPlan(
        chart_type="scatter",
        chart_name="scatter",
        imports=["import pandas as pd", "import plotly.express as px"],
        chart_code="""
def scatter(data_frame):
    return px.scatter(data_frame, x="sepal_length", y="sepal_width")
        """,
    )

    # print(plan.get_chart_code(chart_name="poo", vizro=True))
