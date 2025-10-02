"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va
from vizro.models.types import capture
from vizro import Vizro
from vizro.tables import dash_ag_grid

SELECTED_COUNTRIES = [
    "Singapore",
    "Malaysia",
    "Thailand",
    "Indonesia",
    "Philippines",
]

gapminder = px.data.gapminder().query("country.isin(@SELECTED_COUNTRIES)")


@capture("graph")
def highlighted_box(data_frame, highlight_country=None):
    fig = px.box(data_frame, x="lifeExp", y="country")
    for trace in fig.data:
        trace.opacity = 0.3

    if highlight_country is not None:
        df_highlight = data_frame[data_frame["country"] == highlight_country]
        fig_highlight = px.box(df_highlight, x="lifeExp", y="country", color="country")

        for trace in fig_highlight.data:
            trace.opacity = 1.0
            fig.add_trace(trace)

    return fig


page = vm.Page(
    title="Cross-highlight source graph",
    components=[
        vm.Graph(
            id="box_chart",
            figure=highlighted_box(data_frame=gapminder),
            header="💡 Click on a box to highlight the selected country while filtering the table below",
            actions=[
                va.set_control(control="country_filter", value="y"),
                va.set_control(control="highlight_parameter", value="y"),
            ],
        ),
        vm.AgGrid(id="gapminder_table", figure=dash_ag_grid(data_frame=gapminder)),
    ],
    controls=[
        vm.Filter(id="country_filter", column="country", targets=["gapminder_table"], visible=False),
        vm.Parameter(
            id="highlight_parameter",
            targets=["box_chart.highlight_country"],
            selector=vm.Dropdown(multi=False, options=SELECTED_COUNTRIES),
            visible=False,
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=False)
