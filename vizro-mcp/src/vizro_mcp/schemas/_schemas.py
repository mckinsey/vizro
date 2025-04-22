"""Schema defining pydantic models for usage in the MCP server."""

from typing import Annotated, Any, Literal, Optional

import vizro.models as vm
from pydantic import AfterValidator, BaseModel, Field

# Constants used in chart validation
CUSTOM_CHART_NAME = "custom_chart"


# These simplified page and dashboard models are used to return a flatter schema to the LLM in order to reduce the
# context size. Especially the dashboard model schema is huge as it contains all other models.
class PageSimplified(BaseModel):
    """Simplified Page modes for reduced schema. LLM should remember to insert actual components."""

    components: list[Literal["card", "button", "text", "container", "tabs"]] = Field(
        description="List of component names to be displayed."
    )
    title: str = Field(description="Title to be displayed.")
    description: str = Field(default="", description="Description for meta tags.")
    layout: Optional[Literal["grid", "flex"]] = Field(default=None, description="Layout to place components in.")
    controls: list[Literal["filter", "parameter"]] = Field(default=[], description="Controls to be displayed.")


class DashboardSimplified(BaseModel):
    """Simplified Dashboard model for reduced schema. LLM should remember to insert actual components."""

    pages: list[Literal["page"]] = Field(description="List of page names to be included in the dashboard.")
    theme: Literal["vizro_dark", "vizro_light"] = Field(
        default="vizro_dark", description="Theme to be applied across dashboard. Defaults to `vizro_dark`."
    )
    navigation: Optional[Literal["navigation"]] = Field(
        default=None, description="Navigation component for the dashboard."
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
    """A AgGrid model that uses dash-ag-grid to create the figure."""

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
