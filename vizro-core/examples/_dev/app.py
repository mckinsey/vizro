"""Dev app to try things out."""

from typing import Literal, Optional

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from dash import html
from vizro import Vizro
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
            number={"font": {"size": 32}},
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
    layout=vm.Layout(grid=[[0, 1]] + [[-1, -1]] * 3),
    components=[
        vm.Graph(
            id="kpi-total",
            figure=plt_kpi_card(
                data_frame=iris_df,
                column="sepal_width",
                title="Sepal Width AVG",
            ),
        ),
        CustomKPI(
            title="Total Complaints",
            value="75.513",
            icon="arrow_circle_up",
            sign="up",
            ref_value="5.5% vs. Last Year"
        ),
    ],
    controls=[vm.Filter(column="species")],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
