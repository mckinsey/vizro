"""Dev app to try things out."""

from typing import Literal, Optional

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from dash import html
from vizro import Vizro
from vizro.cards import kpi_card_agg, kpi_card_ref
from vizro.models.types import capture

iris_df = px.data.iris()

# Open questions -------
# Shall we allow for automatic data aggregations? Or shall this be the user's responsibility? (data transformation to live inside / outside component)
# Shall we actually just extend vm.Card and allow a figure attribute there? or shall the KPI Card be its own component?


# Method 1: Using go.Indicator inside vm.Graph
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
            number={"font": {"size": 28}},
            title={"text": f"<br><span style='font-size:1rem;'>{title}</span><br>", "align": align},
            align=align,
        )
    )
    return fig


# Method 2: Using custom component
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
                html.H4(self.title, className="card-title"),
                html.P(self.value, className="card-value"),
                html.Span(
                    [
                        html.Span(self.icon, className=f"material-symbols-outlined {self.sign}"),
                        html.Span(self.ref_value, className=self.sign),
                    ],
                    className="card-ref-value",
                ),
            ],
            className=f"card-border-{self.sign}",
        )


vm.Page.add_type("components", CustomKPI)

page = vm.Page(
    title="Table Page",
       layout=vm.Layout(grid=[[0, 1, 2], [3, 4, 5], [-1, -1, -1]]),
    components=[
        # Method 1: Plotly Indicator inside vm.Graph
        vm.Graph(
            id="kpi-total",
            figure=plt_kpi_card(
                data_frame=iris_df,
                column="sepal_width",
                title="Sepal Width AVG",
            ),
        ),
        # Method 2: Custom component without a figure attribute
        CustomKPI(
            title="Total Complaints", value="75.513", icon="arrow_circle_up", sign="up", ref_value="5.5% vs. Last Year"
        ),
        # Method 3: Using vm.Card with a figure attribute
        vm.Card(
            figure=kpi_card_agg(
                data_frame=iris_df, value="sepal_width", title="Sepal Width AVG", agg_fct=lambda x: x.mean()
            )
        ),
        # Method 3: Using vm.Card with a figure attribute
        vm.Card(
            figure=kpi_card_ref(
                data_frame=iris_df, value="sepal_width", ref_value="petal_width", title="Sepal Width AVG", agg_fct=lambda x: x.mean()
            )
        ),
        # TODO: This should still work without a figure argument
        vm.Card(text="""Hello, this is a text card"""),
        vm.Card(text="""Hello, this is a nav card""", href="https://www.google.com"),
    ],
    controls=[vm.Filter(column="species")],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
