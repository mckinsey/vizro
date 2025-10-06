"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va
from vizro.models.types import capture
from vizro import Vizro
from vizro.tables import dash_ag_grid

SELECTED_COUNTRIES = ["Singapore", "Malaysia", "Thailand", "Indonesia", "Philippines", "NONE"]

gapminder = px.data.gapminder().query("country.isin(@SELECTED_COUNTRIES)")


@capture("graph")
def highlighted_box(data_frame, highlight_country=None):  # (1)!
    fig = px.box(data_frame, x="lifeExp", y="country", color="country")
    fig.update_traces(marker=dict(opacity=0.1, color="#00b4ff"))  # (2)!
    fig.update_layout(showlegend=False)

    if highlight_country:
        for trace in fig.data:
            if trace.name == highlight_country:
                trace.marker.opacity = 1.0
                trace.marker.color = "#ff9222"

    return fig


page = vm.Page(
    title="Cross-highlight source graph",
    components=[
        vm.Graph(
            id="box_chart",  # (4)!
            figure=highlighted_box(data_frame=gapminder),
            header="💡 Click on a box to highlight the selected country while filtering the table below",
            actions=[
                va.set_control(control="country_filter", value="y"),
                va.set_control(control="highlight_parameter", value="y"),  # (5)!
            ],
        ),
        vm.AgGrid(id="gapminder_table", figure=dash_ag_grid(data_frame=gapminder)),
    ],
    controls=[
        vm.Filter(id="country_filter", column="country", targets=["gapminder_table"], visible=False),
        vm.Parameter(
            id="highlight_parameter",  # (6)!
            targets=["box_chart.highlight_country"],  # (7)!
            selector=vm.Dropdown(multi=False, options=SELECTED_COUNTRIES, value="NONE"),
            visible=False,  # (8)!
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
