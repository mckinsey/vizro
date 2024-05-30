"""Dev app to try things out."""

from typing import Literal, Optional

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from dash import html
from vizro import Vizro
from vizro.cards import kpi_card_icon, kpi_card_ref
from vizro.models.types import capture

iris_df = px.data.iris()


# Create the pandas DataFrame
df = pd.DataFrame([[67434, 65553, "A"], [6434, 6553, "B"], [34, 53, "C"]], columns=["Actual", "Reference", "Category"])


# Method 1: Using go.Indicator inside vm.Graph
# (+) Can already be used with vm.Graph, dynamic, possibility to add other traces
# (-) Resizing doesn't seem to work well, difficulties customising style, not visib
@capture("graph")
def plt_kpi_card(
    column: str,
    data_frame: pd.DataFrame = None,
    title: Optional[str] = None,
    align: str = "left",
):
    """Custom KPI card."""
    # Do any data aggregation here
    value = data_frame[column].mean()

    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=value,
            number={"prefix": "$", "font": {"size": 32}},
            title={"text": f"<br><span style='font-size:1rem;'>{title}</span><br>", "align": align},
            align=align,
        )
    )
    return fig


# Method 2: Using custom component
# (+) Fully customisable in style and layout, possibility to add other traces via adding dcc.Graph
# (-) Static
class CustomKPI(vm.VizroBaseModel):
    """New custom component `KPI`."""

    type: Literal["kpi"] = "kpi"
    title: str
    value: str
    icon: str
    sign: Literal["up", "down"]
    ref_value: str

    def build(self):
        return dbc.Card(
            [
                html.H2(self.title),
                html.H1(self.value, className="kpi-value"),
                html.Span(
                    [
                        html.Span(self.icon, className="material-symbols-outlined"),
                        html.Span(self.ref_value),
                    ],
                    className=f"kpi-ref-value {self.sign}",
                ),
            ],
            className=f"kpi-{self.sign}",
        )


vm.Page.add_type("components", CustomKPI)

# Method 3: Extend vm.Card with figure attribute
# (+) Fully customisable in style and layout, possibility to add other traces via adding dcc.Graph, dynamic
# (-) Requires CapturedCallable for static cards now as well

# Most common arguments for CapturedCallable
# kpi_card_ref(
#     data_frame=iris_df,              | YES
#     value="sepal_width",             | YES
#     ref_value="petal_width",         | YES
#     title="Dynamic Card Ref.",       | MAYBE - Eventually better to use Mkd text for this, so they can flexibly use a title / subtitle etc.
#     agg_fct=lambda x: x.mean(),      | MAYBE - Useful if our CapturedCallables should work out of the box without custom code
#     icon="Home"                      | MAYBE
# )


# Method 4: Create new custom component with figure attribute
# Aligned with A. not to do this for now as it would require a higher-level model that does not fit into our
# scheme of components for now. We could consider this in the future if we see a need for it.

page = vm.Page(
    title="KPI Indicators",
    layout=vm.Layout(grid=[[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, -1]]),
    components=[
        # Method 3: Using vm.Card with a figure attribute - value only
        # Style 1: Value Only
        vm.Card(figure=kpi_card_icon(data_frame=df, value="Actual", title="Value I", agg_fct=lambda x: x.sum())),
        vm.Card(figure=kpi_card_icon(data_frame=df, value="Actual", title="Value II", agg_fct=lambda x: x.mean())),
        vm.Card(figure=kpi_card_icon(data_frame=df, value="Actual", title="Value III", agg_fct=lambda x: x.median())),
        # Style 2: Value and reference value
        vm.Card(
            figure=kpi_card_ref(
                data_frame=df,
                value="Reference",
                ref_value="Actual",
                title="Ref. Value II",
                agg_fct=lambda x: x.sum(),
            )
        ),
        vm.Card(
            figure=kpi_card_ref(
                data_frame=df,
                value="Actual",
                ref_value="Reference",
                title="Ref. Value I",
                agg_fct=lambda x: x.sum(),
            )
        ),
        vm.Card(
            figure=kpi_card_ref(
                data_frame=df,
                value="Actual",
                ref_value="Reference",
                title="Ref. Value III",
                agg_fct=lambda x: x.median(),
            )
        ),
        # Style 3: Value and icon
        vm.Card(
            figure=kpi_card_icon(
                data_frame=df,
                value="Actual",
                icon="shopping_cart",
                title="Icon I",
                agg_fct=lambda x: x.sum(),
            )
        ),
        vm.Card(
            figure=kpi_card_icon(
                data_frame=df,
                value="Actual",
                icon="payment",
                title="Icon II",
                agg_fct=lambda x: x.mean(),
            )
        ),
        vm.Card(
            figure=kpi_card_icon(
                data_frame=df,
                value="Actual",
                icon="monitoring",
                title="Icon III",
                agg_fct=lambda x: x.median(),
            )
        ),
        # This should still work without a figure argument
        vm.Card(
            text="""
                # Text Card
                Hello, this is a text card.
            """
        ),
        vm.Card(
            text="""
                # Nav Card
                Hello, this is a nav card.
            """,
            href="https://www.google.com",
        ),
    ],
    controls=[vm.Filter(column="Category")],
)

another_page = vm.Page(
    title="Temporary solutions",
    layout=vm.Layout(grid=[[0, 1, -1]] + [[-1, -1, -1]] * 3),
    components=[
        # Method 1: Plotly indicator inside vm.Graph
        vm.Graph(
            id="kpi-total",
            figure=plt_kpi_card(
                data_frame=iris_df,
                column="sepal_width",
                title="Plotly Indicator",
            ),
        ),
        # Method 2: Custom component without a figure attribute
        CustomKPI(
            title="Custom component", value="75.513", icon="arrow_circle_up", sign="up", ref_value="5.5% vs. Last Year"
        ),
    ],
)


dashboard = vm.Dashboard(pages=[page, another_page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
